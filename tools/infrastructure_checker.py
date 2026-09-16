#!/usr/bin/env python3
"""Build the MW/$ data-center infrastructure bottleneck and pricing-power state."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "infrastructure-checker.json"
ENTITY_PATH = ROOT / "memory" / "infrastructure-entities.jsonl"
SOURCE_PATH = ROOT / "memory" / "infrastructure-sources.jsonl"
OBS_PATH = ROOT / "memory" / "infrastructure-observations.jsonl"
PROJECT_PATH = ROOT / "memory" / "infrastructure-projects.jsonl"
STATE_PATH = ROOT / "state" / "infrastructure-backlog.json"
STATE_MD_PATH = ROOT / "state" / "infrastructure-backlog.md"
WEEKLY_DIR = ROOT / "state" / "infrastructure-weekly"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    rows = []
    if not path.exists():
        return rows
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path.relative_to(ROOT)}:{n}: invalid JSON: {exc}")
        if not isinstance(row, dict):
            raise SystemExit(f"{path.relative_to(ROOT)}:{n}: expected object")
        rows.append(row)
    return rows


def unique_index(rows, label):
    out = {}
    for row in rows:
        row_id = row.get("id")
        if not row_id:
            raise SystemExit(f"{label}: record missing id")
        if row_id in out:
            raise SystemExit(f"{label}: duplicate id {row_id}")
        out[row_id] = row
    return out


def interpolate(value, points):
    points = sorted((float(x), float(y)) for x, y in points)
    x = float(value)
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return y1
            f = (x - x0) / (x1 - x0)
            return y0 + f * (y1 - y0)
    raise AssertionError("unreachable")


def input_hash(paths):
    h = hashlib.sha256()
    for path in paths:
        h.update(path.relative_to(ROOT).as_posix().encode())
        h.update(b"\0")
        h.update(path.read_bytes() if path.exists() else b"")
        h.update(b"\0")
    return h.hexdigest()


def validate(config, entities, sources, observations, projects):
    layer_ids = {row["id"] for row in config["layers"]}
    entity_ids = set(entities)
    source_ids = set(sources)
    valid_scopes = set(config["scope_multipliers"])
    valid_evidence = set(config["evidence_multipliers"])
    scored_metrics = set(config["pressure_metrics"]) | set(config["pricing_metrics"])

    for row in observations:
        required = ["id", "as_of", "observed_at", "entity_id", "layer", "metric", "value", "unit", "scope", "scope_class", "evidence", "source_ids", "tags"]
        missing = [x for x in required if x not in row]
        if missing:
            raise SystemExit(f"{row.get('id', '<unknown>')}: missing {', '.join(missing)}")
        if row["entity_id"] not in entity_ids:
            raise SystemExit(f"{row['id']}: unknown entity {row['entity_id']}")
        if row["layer"] not in layer_ids:
            raise SystemExit(f"{row['id']}: unknown layer {row['layer']}")
        if row["scope_class"] not in valid_scopes:
            raise SystemExit(f"{row['id']}: unknown scope_class {row['scope_class']}")
        if row["evidence"] not in valid_evidence:
            raise SystemExit(f"{row['id']}: unknown evidence {row['evidence']}")
        if not isinstance(row["value"], (int, float)) or isinstance(row["value"], bool) or not math.isfinite(row["value"]):
            raise SystemExit(f"{row['id']}: value must be finite numeric")
        unknown_sources = [x for x in row["source_ids"] if x not in source_ids]
        if unknown_sources:
            raise SystemExit(f"{row['id']}: unknown source ids {unknown_sources}")
        if row["metric"] not in scored_metrics and not row.get("tags"):
            raise SystemExit(f"{row['id']}: unscored metric requires tags")

    allowed_status = {"announced", "verified", "underway", "complete", "delayed", "cancelled"}
    allowed_stages = {x for values in config["project_stage_gates"].values() for x in values}
    for project in projects:
        for field in ["id", "name", "region", "announced_it_mw", "stages", "source_ids"]:
            if field not in project:
                raise SystemExit(f"project {project.get('id', '<unknown>')}: missing {field}")
        unknown_sources = [x for x in project.get("source_ids", []) if x not in source_ids]
        if unknown_sources:
            raise SystemExit(f"project {project['id']}: unknown source ids {unknown_sources}")
        for stage in project["stages"]:
            if stage.get("stage") not in allowed_stages:
                raise SystemExit(f"project {project['id']}: unsupported stage {stage.get('stage')}")
            if stage.get("status") not in allowed_status:
                raise SystemExit(f"project {project['id']}: unsupported status {stage.get('status')}")
            unknown = [x for x in stage.get("source_ids", []) if x not in source_ids]
            if unknown:
                raise SystemExit(f"project {project['id']} stage {stage.get('stage')}: unknown sources {unknown}")


def latest_observations(observations):
    """Use only the latest record per entity/layer/metric so history is not double-counted."""
    latest = {}
    for row in observations:
        key = (row["entity_id"], row["layer"], row["metric"])
        stamp = (row["as_of"], row["observed_at"], row["id"])
        if key not in latest or stamp > latest[key][0]:
            latest[key] = (stamp, row)
    return [pair[1] for pair in latest.values()]


def score_category(rows, metric_config, config):
    score_num = 0.0
    score_den = 0.0
    metric_weight_seen = {}
    entities = set()
    details = []
    for row in rows:
        metric = metric_config.get(row["metric"])
        if not metric:
            continue
        raw_score = interpolate(row["value"], metric["points"])
        scope_mult = config["scope_multipliers"][row["scope_class"]]
        evidence_mult = config["evidence_multipliers"][row["evidence"]]
        adjusted_weight = metric["weight"] * scope_mult * evidence_mult
        score_num += raw_score * adjusted_weight
        score_den += adjusted_weight
        metric_weight_seen[row["metric"]] = max(metric_weight_seen.get(row["metric"], 0.0), metric["weight"])
        entities.add(row["entity_id"])
        details.append({
            "observation_id": row["id"], "entity_id": row["entity_id"], "metric": row["metric"],
            "value": row["value"], "raw_metric_score": round(raw_score, 1),
            "adjusted_weight": round(adjusted_weight, 4), "scope_class": row["scope_class"], "evidence": row["evidence"]
        })
    if not score_den:
        return None, 0.0, "empty", details
    score = score_num / score_den
    total_metric_weight = sum(v["weight"] for v in metric_config.values())
    metric_coverage = sum(metric_weight_seen.values()) / total_metric_weight if total_metric_weight else 0.0
    entity_coverage = min(1.0, len(entities) / config["coverage"]["target_entities_per_layer"])
    coverage = 0.7 * metric_coverage + 0.3 * entity_coverage
    if coverage >= config["coverage"]["high"]:
        label = "high"
    elif coverage >= config["coverage"]["medium"]:
        label = "medium"
    elif coverage >= config["coverage"]["low"]:
        label = "low"
    else:
        label = "sparse"
    return round(score, 1), round(coverage, 3), label, details


def project_mw_by_layer(projects, config):
    active_status = {"verified", "underway", "complete"}
    out = {layer["id"]: 0.0 for layer in config["layers"]}
    project_count = {layer["id"]: 0 for layer in config["layers"]}
    for layer, allowed_stages in config["project_stage_gates"].items():
        for project in projects:
            candidates = []
            for stage in project.get("stages", []):
                if stage.get("stage") in allowed_stages and stage.get("status") in active_status:
                    mw = stage.get("it_mw")
                    if isinstance(mw, (int, float)):
                        candidates.append(float(mw))
            if candidates:
                out[layer] += max(candidates)
                project_count[layer] += 1
    return out, project_count


def previous_layer_scores():
    if not WEEKLY_DIR.exists():
        return {}
    files = sorted(WEEKLY_DIR.glob("*.json"))
    if not files:
        return {}
    try:
        previous = load_json(files[-1])
    except Exception:
        return {}
    return {row["layer"]: row for row in previous.get("layers", [])}


def build_state(config, entities, sources, observations, projects):
    latest = latest_observations(observations)
    verified_mw, project_counts = project_mw_by_layer(projects, config)
    previous = previous_layer_scores()
    alert_tags = set(config["alerts"]["high_information_tags"])
    layers = []
    alerts = []

    for layer_cfg in sorted(config["layers"], key=lambda x: x["order"]):
        layer = layer_cfg["id"]
        rows = [row for row in latest if row["layer"] == layer]
        pressure, p_cov, p_conf, p_details = score_category(rows, config["pressure_metrics"], config)
        pricing, m_cov, m_conf, m_details = score_category(rows, config["pricing_metrics"], config)
        monetization = round(pressure * pricing / 100.0, 1) if pressure is not None and pricing is not None else None
        prior = previous.get(layer, {})
        pressure_delta = round(pressure - prior["pressure_score"], 1) if pressure is not None and prior.get("pressure_score") is not None else None
        pricing_delta = round(pricing - prior["pricing_score"], 1) if pricing is not None and prior.get("pricing_score") is not None else None
        source_ids = sorted({sid for row in rows for sid in row["source_ids"]})
        entity_ids = sorted({row["entity_id"] for row in rows})
        layers.append({
            "layer": layer, "name": layer_cfg["name"], "order": layer_cfg["order"],
            "pressure_score": pressure, "pressure_coverage": p_cov, "pressure_confidence": p_conf,
            "pricing_score": pricing, "pricing_coverage": m_cov, "pricing_confidence": m_conf,
            "scarcity_monetization_score": monetization,
            "pressure_delta_vs_previous_weekly": pressure_delta, "pricing_delta_vs_previous_weekly": pricing_delta,
            "verified_project_it_mw": round(verified_mw[layer], 3), "verified_project_count": project_counts[layer],
            "entity_ids": entity_ids, "source_ids": source_ids,
            "pressure_components": p_details, "pricing_components": m_details
        })
        for row in rows:
            matched_tags = sorted(set(row.get("tags", [])) & alert_tags)
            if matched_tags:
                alerts.append({"type": "high_information_event", "layer": layer, "entity_id": row["entity_id"], "observation_id": row["id"], "tags": matched_tags, "as_of": row["as_of"]})
        if pressure is not None and pressure >= config["alerts"]["pressure_score"]:
            alerts.append({"type": "high_pressure", "layer": layer, "score": pressure})
        if pricing is not None and pricing >= config["alerts"]["pricing_score"]:
            alerts.append({"type": "high_pricing_power", "layer": layer, "score": pricing})
        if pressure_delta is not None and abs(pressure_delta) >= config["alerts"]["weekly_score_change"]:
            alerts.append({"type": "pressure_migration", "layer": layer, "delta": pressure_delta})

    ranked_pressure = [x for x in layers if x["pressure_score"] is not None]
    ranked_pressure.sort(key=lambda x: (x["pressure_score"], x["pressure_coverage"]), reverse=True)
    ranked_monetization = [x for x in layers if x["scarcity_monetization_score"] is not None]
    ranked_monetization.sort(key=lambda x: (x["scarcity_monetization_score"], x["pricing_coverage"]), reverse=True)

    observed_at = max((row["observed_at"] for row in observations), default=None)
    source_data_through = max((row["as_of"] for row in observations), default=None)
    return {
        "schema_version": config["schema_version"],
        "as_of": observed_at,
        "source_data_through": source_data_through,
        "region": config["target_region"],
        "method": "INFRA-BOTTLENECK-V1",
        "evidence_status": "seeded_primary_sparse; scores are not comparable to high-coverage layers without coverage context",
        "input_sha256": input_hash([CONFIG_PATH, ENTITY_PATH, SOURCE_PATH, OBS_PATH, PROJECT_PATH]),
        "layers": layers,
        "top_pressure_layers": [x["layer"] for x in ranked_pressure[:3]],
        "top_monetization_layers": [x["layer"] for x in ranked_monetization[:3]],
        "alerts": alerts,
        "cadence": config["cadence"],
        "strongest_disconfirming_rule": "Backlog or bookings alone do not establish pricing power; capacity additions, weak price-cost, or margin compression can reverse the signal.",
        "missing_denominator_rule": "Do not create demand/capacity ratios unless demand and executable supply share geography, delivery window, power scope and product perimeter."
    }


def fmt(value):
    return "—" if value is None else f"{value:.1f}"


def render_markdown(state):
    lines = [
        "# Data-center infrastructure backlog checker",
        "",
        f"**As of:** {state['as_of'] or 'no observations'}  ",
        f"**Source data through:** {state['source_data_through'] or 'none'}  ",
        f"**Region:** {state['region']}  ",
        f"**Method:** `{state['method']}`  ",
        "",
        "> Scores are evidence-weighted and must be read with coverage. Blank beats invented precision.",
        "",
        "| Layer | Pressure | Cov. | Pricing | Cov. | Scarcity monetization | Verified project IT MW |",
        "|---|---:|---:|---:|---:|---:|---:|"
    ]
    for row in state["layers"]:
        lines.append(
            f"| {row['name']} | {fmt(row['pressure_score'])} | {row['pressure_coverage']:.0%} | "
            f"{fmt(row['pricing_score'])} | {row['pricing_coverage']:.0%} | {fmt(row['scarcity_monetization_score'])} | "
            f"{row['verified_project_it_mw']:.1f} |"
        )
    lines += [
        "",
        "## Current read",
        "",
        f"- Highest seeded pressure: {', '.join(state['top_pressure_layers']) or 'none'}.",
        f"- Highest seeded scarcity monetization: {', '.join(state['top_monetization_layers']) or 'none'}.",
        f"- Evidence state: {state['evidence_status']}.",
        "",
        "## Alert tape",
        ""
    ]
    if state["alerts"]:
        for alert in state["alerts"]:
            lines.append(f"- `{alert['type']}` — {json.dumps(alert, sort_keys=True)}")
    else:
        lines.append("- No configured alerts.")
    lines += [
        "",
        "## Guardrails",
        "",
        f"- {state['strongest_disconfirming_rule']}",
        f"- {state['missing_denominator_rule']}",
        ""
    ]
    return "\n".join(lines)


def write_if_changed(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--weekly", action="store_true")
    parser.add_argument("--snapshot-date", default=None)
    args = parser.parse_args()

    config = load_json(CONFIG_PATH)
    entities = unique_index(load_jsonl(ENTITY_PATH), "infrastructure entities")
    sources = unique_index(load_jsonl(SOURCE_PATH), "infrastructure sources")
    observations = load_jsonl(OBS_PATH)
    unique_index(observations, "infrastructure observations")
    projects = load_jsonl(PROJECT_PATH)
    unique_index(projects, "infrastructure projects")
    validate(config, entities, sources, observations, projects)
    state = build_state(config, entities, sources, observations, projects)

    if args.validate_only and not (args.write_state or args.weekly):
        print(f"VALID: {len(entities)} entities, {len(sources)} sources, {len(observations)} observations, {len(projects)} projects")
        return

    state_json = json.dumps(state, indent=2, sort_keys=False) + "\n"
    state_md = render_markdown(state)
    if args.write_state or not args.weekly:
        changed_json = write_if_changed(STATE_PATH, state_json)
        changed_md = write_if_changed(STATE_MD_PATH, state_md)
        print(f"state: {'updated' if changed_json or changed_md else 'unchanged'}")
    if args.weekly:
        snapshot_date = args.snapshot_date or date.today().isoformat()
        weekly_json = WEEKLY_DIR / f"{snapshot_date}.json"
        weekly_md = WEEKLY_DIR / f"{snapshot_date}.md"
        write_if_changed(weekly_json, state_json)
        write_if_changed(weekly_md, state_md)
        print(f"weekly snapshot: {snapshot_date}")


if __name__ == "__main__":
    main()

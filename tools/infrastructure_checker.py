#!/usr/bin/env python3
"""Build the MW/$ data-center infrastructure bottleneck, pricing-power and investment-cycle state."""
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
    cycle = config.get("investment_cycle", {})
    if cycle:
        required_stages = {
            "NO_SIGNAL", "PRE_SCARCITY", "SCARCITY_FORMING", "SCARCITY_CONFIRMED",
            "MONETIZATION", "PEAK_MONETIZATION", "CAPACITY_CATCH_UP", "REVERSAL"
        }
        if set(cycle.get("stage_index", {})) != required_stages:
            raise SystemExit("investment_cycle.stage_index must define the complete cycle")

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


def previous_snapshot():
    if not WEEKLY_DIR.exists():
        return {}
    files = sorted(WEEKLY_DIR.glob("*.json"))
    if not files:
        return {}
    try:
        return load_json(files[-1])
    except Exception:
        return {}


def coverage_label(value, config):
    if value >= config["coverage"]["high"]:
        return "high"
    if value >= config["coverage"]["medium"]:
        return "medium"
    if value >= config["coverage"]["low"]:
        return "low"
    return "sparse"


def cycle_coverage(pressure, pricing, pressure_cov, pricing_cov):
    if pressure is not None and pricing is not None:
        return round((pressure_cov + pricing_cov) / 2.0, 3)
    if pressure is not None:
        return round(pressure_cov * 0.75, 3)
    if pricing is not None:
        return round(pricing_cov * 0.50, 3)
    return 0.0


def classify_cycle(pressure, pricing, pressure_delta, pricing_delta, coverage, tags, config):
    cycle = config["investment_cycle"]
    t = cycle["thresholds"]
    tags = set(tags)
    capacity_response = bool(tags & set(cycle["capacity_response_tags"]))
    demand_break = bool(tags & set(cycle["demand_break_tags"]))
    p = pressure if pressure is not None else -1.0
    m = pricing if pricing is not None else -1.0

    if pressure is None and pricing is None:
        stage = "NO_SIGNAL"
        action = "WATCH"
        reason = "No scored pressure or pricing evidence."
    elif demand_break and ((pressure_delta is None) or pressure_delta <= 0):
        if p < t["reversal_pressure_max"] and (pricing is None or m < t["reversal_pricing_max"]):
            stage, action = "REVERSAL", "SELL_AVOID"
            reason = "Demand/project break with weak or falling scarcity economics."
        else:
            stage, action = "CAPACITY_CATCH_UP", "RISK_OFF_REDUCE"
            reason = "Project slippage/demand-break evidence is appearing before full economic reversal."
    elif capacity_response and pressure_delta is not None and pressure_delta <= t["capacity_catch_up_pressure_delta_max"]:
        stage, action = "CAPACITY_CATCH_UP", "RISK_OFF_REDUCE"
        reason = "New capacity is arriving while pressure is no longer accelerating."
    elif pressure_delta is not None and pressure_delta <= t["reversal_weekly_delta"]:
        if p < t["reversal_pressure_max"] and (pricing is None or m < t["reversal_pricing_max"]):
            stage, action = "REVERSAL", "SELL_AVOID"
            reason = "Pressure has rolled over into a weak-scarcity regime."
        else:
            stage, action = "CAPACITY_CATCH_UP", "RISK_OFF_REDUCE"
            reason = "Pressure is falling materially from a still-elevated base."
    elif pricing is not None and m >= t["peak_pricing_min"] and (pressure is None or p < t["monetization_pressure_min"]):
        stage, action = "CAPACITY_CATCH_UP", "RISK_OFF_REDUCE"
        reason = "Pricing remains elevated without matching physical pressure; late-cycle pricing lag risk."
    elif pressure is not None and pricing is not None and p >= t["peak_pressure_min"] and m >= t["peak_pricing_min"]:
        stage, action = "PEAK_MONETIZATION", "HOLD"
        reason = "Scarcity and pricing power are both already extreme; upside now depends on duration, not discovery."
    elif pressure is not None and pricing is not None and p >= t["monetization_pressure_min"] and m >= t["monetization_pricing_min"]:
        stage, action = "MONETIZATION", "ADD_HOLD"
        reason = "Physical scarcity is translating into supplier economics without a confirmed rollover."
    elif pressure is not None and p >= t["confirmed_pressure_min"] and (pricing is None or m < t["monetization_pricing_min"]):
        stage, action = "SCARCITY_CONFIRMED", "ACCUMULATE"
        reason = "Physical scarcity is strong but monetization is not yet fully reflected in the available pricing evidence."
    elif pressure is not None and p >= t["forming_pressure_min"] and (pricing is None or m < t["monetization_pricing_min"]):
        stage = "SCARCITY_FORMING"
        if pressure_delta is not None and pressure_delta >= t["forming_accumulate_delta"]:
            action = "ACCUMULATE"
            reason = "Pressure is emerging and accelerating before mature monetization."
        else:
            action = "WATCH"
            reason = "Pressure is emerging, but acceleration or monetization confirmation is still missing."
    else:
        stage, action = "PRE_SCARCITY", "WATCH"
        reason = "No durable scarcity/monetization regime is established yet."

    return {
        "cycle_stage": stage,
        "cycle_stage_index": cycle["stage_index"][stage],
        "investment_action": action,
        "cycle_coverage": coverage,
        "cycle_confidence": coverage_label(coverage, config),
        "capacity_response_active": capacity_response,
        "demand_break_active": demand_break,
        "reason": reason,
        "action_priority": cycle["action_priority"][action]
    }


def entity_state(entity, rows, previous, config):
    pressure, p_cov, p_conf, p_details = score_category(rows, config["pressure_metrics"], config)
    pricing, m_cov, m_conf, m_details = score_category(rows, config["pricing_metrics"], config)
    monetization = round(pressure * pricing / 100.0, 1) if pressure is not None and pricing is not None else None
    prior = previous.get(entity["id"], {})
    pressure_delta = round(pressure - prior["pressure_score"], 1) if pressure is not None and prior.get("pressure_score") is not None else None
    pricing_delta = round(pricing - prior["pricing_score"], 1) if pricing is not None and prior.get("pricing_score") is not None else None
    tags = sorted({tag for row in rows for tag in row.get("tags", [])})
    cov = cycle_coverage(pressure, pricing, p_cov, m_cov)
    cycle = classify_cycle(pressure, pricing, pressure_delta, pricing_delta, cov, tags, config)
    source_ids = sorted({sid for row in rows for sid in row["source_ids"]})
    layers = sorted({row["layer"] for row in rows})
    return {
        "entity_id": entity["id"], "name": entity["name"], "ticker": entity.get("ticker"), "type": entity.get("type"),
        "layers": layers, "pressure_score": pressure, "pressure_coverage": p_cov, "pressure_confidence": p_conf,
        "pricing_score": pricing, "pricing_coverage": m_cov, "pricing_confidence": m_conf,
        "scarcity_monetization_score": monetization,
        "pressure_delta_vs_previous_weekly": pressure_delta, "pricing_delta_vs_previous_weekly": pricing_delta,
        **cycle, "source_ids": source_ids, "pressure_components": p_details, "pricing_components": m_details
    }


def build_state(config, entities, sources, observations, projects):
    latest = latest_observations(observations)
    verified_mw, project_counts = project_mw_by_layer(projects, config)
    previous = previous_snapshot()
    previous_layers = {row["layer"]: row for row in previous.get("layers", [])}
    previous_entities = {row["entity_id"]: row for row in previous.get("entities", [])}
    alert_tags = set(config["alerts"]["high_information_tags"])
    layers = []
    alerts = []

    for layer_cfg in sorted(config["layers"], key=lambda x: x["order"]):
        layer = layer_cfg["id"]
        rows = [row for row in latest if row["layer"] == layer]
        pressure, p_cov, p_conf, p_details = score_category(rows, config["pressure_metrics"], config)
        pricing, m_cov, m_conf, m_details = score_category(rows, config["pricing_metrics"], config)
        monetization = round(pressure * pricing / 100.0, 1) if pressure is not None and pricing is not None else None
        prior = previous_layers.get(layer, {})
        pressure_delta = round(pressure - prior["pressure_score"], 1) if pressure is not None and prior.get("pressure_score") is not None else None
        pricing_delta = round(pricing - prior["pricing_score"], 1) if pricing is not None and prior.get("pricing_score") is not None else None
        source_ids = sorted({sid for row in rows for sid in row["source_ids"]})
        entity_ids = sorted({row["entity_id"] for row in rows})
        tags = sorted({tag for row in rows for tag in row.get("tags", [])})
        cov = cycle_coverage(pressure, pricing, p_cov, m_cov)
        cycle = classify_cycle(pressure, pricing, pressure_delta, pricing_delta, cov, tags, config)
        layers.append({
            "layer": layer, "name": layer_cfg["name"], "order": layer_cfg["order"],
            "pressure_score": pressure, "pressure_coverage": p_cov, "pressure_confidence": p_conf,
            "pricing_score": pricing, "pricing_coverage": m_cov, "pricing_confidence": m_conf,
            "scarcity_monetization_score": monetization,
            "pressure_delta_vs_previous_weekly": pressure_delta, "pricing_delta_vs_previous_weekly": pricing_delta,
            "verified_project_it_mw": round(verified_mw[layer], 3), "verified_project_count": project_counts[layer],
            "entity_ids": entity_ids, "source_ids": source_ids, **cycle,
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
        prior_action = prior.get("investment_action")
        if prior_action and prior_action != cycle["investment_action"]:
            alerts.append({"type": "investment_cycle_change", "layer": layer, "from": prior_action, "to": cycle["investment_action"]})

    entity_rows = []
    for entity in entities.values():
        rows = [row for row in latest if row["entity_id"] == entity["id"]]
        if rows:
            entity_rows.append(entity_state(entity, rows, previous_entities, config))

    ranked_pressure = sorted((x for x in layers if x["pressure_score"] is not None), key=lambda x: (x["pressure_score"], x["pressure_coverage"]), reverse=True)
    ranked_monetization = sorted((x for x in layers if x["scarcity_monetization_score"] is not None), key=lambda x: (x["scarcity_monetization_score"], x["pricing_coverage"]), reverse=True)
    ranked_cycle_layers = sorted(layers, key=lambda x: (x["action_priority"], x["cycle_coverage"], x["scarcity_monetization_score"] or -1), reverse=True)
    ranked_cycle_entities = sorted(entity_rows, key=lambda x: (x["action_priority"], x["cycle_coverage"], x["scarcity_monetization_score"] or -1), reverse=True)

    action_board_layers = {}
    action_board_entities = {}
    for action in config["investment_cycle"]["action_order"]:
        action_board_layers[action] = [x["layer"] for x in ranked_cycle_layers if x["investment_action"] == action]
        action_board_entities[action] = [x["entity_id"] for x in ranked_cycle_entities if x["investment_action"] == action]

    observed_at = max((row["observed_at"] for row in observations), default=None)
    source_data_through = max((row["as_of"] for row in observations), default=None)
    return {
        "schema_version": config["schema_version"],
        "as_of": observed_at,
        "source_data_through": source_data_through,
        "region": config["target_region"],
        "method": "INFRA-BOTTLENECK-CYCLE-V2",
        "evidence_status": "seeded_primary_sparse; cycle labels are model states, not stand-alone trade instructions, and must be read with coverage",
        "input_sha256": input_hash([CONFIG_PATH, ENTITY_PATH, SOURCE_PATH, OBS_PATH, PROJECT_PATH]),
        "layers": layers,
        "entities": entity_rows,
        "top_pressure_layers": [x["layer"] for x in ranked_pressure[:3]],
        "top_monetization_layers": [x["layer"] for x in ranked_monetization[:3]],
        "investment_cycle_layer_ranking": [x["layer"] for x in ranked_cycle_layers],
        "investment_cycle_entity_ranking": [x["entity_id"] for x in ranked_cycle_entities],
        "investment_action_board": {"layers": action_board_layers, "entities": action_board_entities},
        "alerts": alerts,
        "cadence": config["cadence"],
        "strongest_disconfirming_rule": "Backlog or bookings alone do not establish pricing power; capacity additions, weak price-cost, or margin compression can move a layer from HOLD to RISK_OFF even while backlog stays high.",
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
        "> Pressure, pricing power, investment-cycle stage and evidence coverage are separate. A hot bottleneck can already be late-cycle.",
        "",
        "| Layer | Pressure | Pricing | Cycle stage | Action | Cycle cov. | Scarcity monetization | Verified IT MW |",
        "|---|---:|---:|---|---|---:|---:|---:|"
    ]
    for row in state["layers"]:
        lines.append(
            f"| {row['name']} | {fmt(row['pressure_score'])} | {fmt(row['pricing_score'])} | "
            f"{row['cycle_stage']} | **{row['investment_action']}** | {row['cycle_coverage']:.0%} | "
            f"{fmt(row['scarcity_monetization_score'])} | {row['verified_project_it_mw']:.1f} |"
        )
    lines += ["", "## Supplier / contractor investment cycle", "", "| Entity | Ticker | Pressure | Pricing | Cycle stage | Action | Cycle cov. |", "|---|---|---:|---:|---|---|---:|"]
    for row in state["entities"]:
        lines.append(
            f"| {row['name']} | {row.get('ticker') or '—'} | {fmt(row['pressure_score'])} | {fmt(row['pricing_score'])} | "
            f"{row['cycle_stage']} | **{row['investment_action']}** | {row['cycle_coverage']:.0%} |"
        )
    lines += ["", "## Investment action board", ""]
    for action, entity_ids in state["investment_action_board"]["entities"].items():
        lines.append(f"- **{action}:** {', '.join(entity_ids) if entity_ids else 'none'}")
    lines += [
        "",
        "## Current read",
        "",
        f"- Highest pressure: {', '.join(state['top_pressure_layers']) or 'none'}.",
        f"- Highest scarcity monetization: {', '.join(state['top_monetization_layers']) or 'none'}.",
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
        "- Cycle labels describe model position; they do not override valuation, balance-sheet, company-specific execution, or portfolio constraints.",
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

#!/usr/bin/env python3
"""Build the MW/$ project time, latency and economic-depreciation state."""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_PATH = ROOT / "memory" / "infrastructure-projects.jsonl"
CONFIG_PATH = ROOT / "config" / "project-time-depreciation.json"
STATE_JSON = ROOT / "state" / "project-time-depreciation.json"
STATE_MD = ROOT / "state" / "project-time-depreciation.md"

DURATION_PAIRS = [
    ("permit_latency", "permit_filed", "permit_approved"),
    ("approval_to_site_work", "permit_approved", "site_work_start"),
    ("permit_approved_to_groundbreak", "permit_approved", "groundbreak"),
    ("groundbreak_to_first_energized", "groundbreak", "first_energized_mw"),
    ("groundbreak_to_first_operational", "groundbreak", "first_operational_mw"),
    ("groundbreak_to_first_billable", "groundbreak", "first_billable_mw"),
    ("first_energized_to_operational", "first_energized_mw", "first_operational_mw"),
    ("first_operational_to_billable", "first_operational_mw", "first_billable_mw"),
    ("first_energized_to_billable", "first_energized_mw", "first_billable_mw"),
    ("first_billable_to_full_phase", "first_billable_mw", "full_phase_operational"),
    ("contract_to_first_operational", "contract_committed", "first_operational_mw"),
    ("contract_to_first_billable", "contract_committed", "first_billable_mw"),
    ("permit_approved_to_first_energized", "permit_approved", "first_energized_mw"),
    ("permit_approved_to_first_operational", "permit_approved", "first_operational_mw"),
    ("permit_approved_to_full_phase", "permit_approved", "full_phase_operational"),
    ("groundbreak_to_full_phase", "groundbreak", "full_phase_operational"),
    ("groundbreak_to_full_campus", "groundbreak", "full_campus_operational"),
]

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()

def months(days):
    return days / 30.4375

def midpoint(a, b):
    return a + (b - a) / 2

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def load_jsonl(path):
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

def milestone_map(project):
    out = {}
    for m in project.get("milestones", []):
        if m.get("status", "actual") != "actual":
            continue
        if not m.get("event") or not m.get("date_start") or not m.get("date_end"):
            continue
        start, end = parse_date(m["date_start"]), parse_date(m["date_end"])
        if end < start:
            raise SystemExit(f"{project['id']} {m['event']}: date_end before date_start")
        row = {
            "start": start,
            "end": end,
            "mid": midpoint(start, end),
            "precision": m.get("precision"),
            "source_ids": m.get("source_ids", []),
        }
        current = out.get(m["event"])
        if current is None or start < current["start"]:
            out[m["event"]] = row
    return out

def duration_between(a, b):
    low = max(0, (b["start"] - a["end"]).days)
    high = max(0, (b["end"] - a["start"]).days)
    mid = max(0, (b["mid"] - a["mid"]).days)
    return {
        "months_low": round(months(low), 2),
        "months_mid": round(months(mid), 2),
        "months_high": round(months(high), 2),
    }

def km_curve(observations):
    if not observations:
        return []
    times = sorted(set(round(x[0], 6) for x in observations))
    at_risk = len(observations)
    survival = 1.0
    rows = []
    for t in times:
        events = sum(1 for value, event in observations if round(value, 6) == t and event)
        censored = sum(1 for value, event in observations if round(value, 6) == t and not event)
        if events and at_risk:
            survival *= 1 - events / at_risk
        rows.append({
            "months": round(t, 2),
            "at_risk": at_risk,
            "events": events,
            "censored": censored,
            "prob_not_operational": round(survival, 4),
            "prob_operational": round(1 - survival, 4),
        })
        at_risk -= events + censored
    return rows

def build_state(projects, as_of, config):
    capex_ref = float(config["reference_capex_usd_per_it_mw"])
    waccs = [float(x) for x in config["wacc_scenarios"]]
    results = []
    survival = []
    pair_names = {(a, b): name for name, a, b in DURATION_PAIRS}

    for project in projects:
        milestones = milestone_map(project)
        durations = {}

        for name, start_event, end_event in DURATION_PAIRS:
            if start_event in milestones and end_event in milestones:
                durations[name] = duration_between(milestones[start_event], milestones[end_event])

        for direct in project.get("duration_observations", []):
            if direct.get("status", "actual") != "actual":
                continue
            key = pair_names.get((direct.get("from_event"), direct.get("to_event")))
            if not key or key in durations:
                continue
            low_days = float(direct.get("days_low", direct.get("days", 0)))
            high_days = float(direct.get("days_high", direct.get("days", low_days)))
            mid_days = (low_days + high_days) / 2
            durations[key] = {
                "months_low": round(months(low_days), 2),
                "months_mid": round(months(mid_days), 2),
                "months_high": round(months(high_days), 2),
                "direct_reported": True,
                "source_ids": direct.get("source_ids", []),
            }

        censored = None
        if "groundbreak_to_first_operational" in durations:
            survival.append((durations["groundbreak_to_first_operational"]["months_mid"], True))
        elif "groundbreak_to_first_billable" in durations:
            survival.append((durations["groundbreak_to_first_billable"]["months_mid"], True))
        elif "groundbreak_to_first_energized" in durations:
            survival.append((durations["groundbreak_to_first_energized"]["months_mid"], True))
        elif "groundbreak" in milestones:
            censored = max(0, months((as_of - milestones["groundbreak"]["mid"]).days))
            survival.append((censored, False))
            censored = round(censored, 2)

        economics = {
            "reference_capex_usd_per_it_mw": capex_ref,
            "wacc_scenarios": [],
        }
        basis = (
            durations.get("groundbreak_to_first_operational")
            or durations.get("groundbreak_to_first_billable")
            or durations.get("groundbreak_to_first_energized")
        )
        if basis:
            years = basis["months_mid"] / 12
            for wacc in waccs:
                economics["wacc_scenarios"].append({
                    "wacc": wacc,
                    "full_capital_carry_usd_per_mw": round(capex_ref * wacc * years),
                    "linear_spend_carry_usd_per_mw": round(capex_ref * 0.5 * wacc * years),
                    "carry_usd_per_mw_per_month_at_full_capital": round(capex_ref * wacc / 12),
                })
            if years > 0:
                economics["reference_time_adjusted_mw_per_billion_year"] = round(
                    (1_000_000_000 / capex_ref) / years, 3
                )

        results.append({
            "id": project["id"],
            "name": project["name"],
            "region": project["region"],
            "announced_it_mw": project.get("announced_it_mw"),
            "durations": durations,
            "groundbreak_right_censored_months": censored,
            "economics": economics,
            "source_ids": sorted({
                sid
                for row in project.get("milestones", []) + project.get("duration_observations", [])
                for sid in row.get("source_ids", [])
            }),
        })

    completed = sum(1 for _, event in survival if event)
    survival_state = {
        "n": len(survival),
        "completed_events": completed,
        "right_censored": len(survival) - completed,
        "status": "computed" if len(survival) >= 3 else "insufficient_n",
        "curve": km_curve(survival) if len(survival) >= 3 else [],
    }

    return {
        "schema_version": config["schema_version"],
        "as_of": as_of.isoformat(),
        "method": config["method"],
        "reference_scenario": {
            "capex_usd_per_it_mw": capex_ref,
            "wacc_scenarios": waccs,
            "note": "Reference scenario only. Full-capital carry is an upper-bound style exposure; linear-spend carry assumes capital deploys evenly from zero to full over the build.",
        },
        "projects": results,
        "groundbreak_to_first_operational_survival": survival_state,
    }

def render_markdown(state):
    lines = [
        "# Project time / depreciation dashboard",
        "",
        f"**As of:** {state['as_of']}  ",
        f"**Method:** `{state['method']}`  ",
        f"**Reference capex:** ${state['reference_scenario']['capex_usd_per_it_mw']/1e6:.1f}M per IT MW  ",
        f"**WACC scenarios:** {', '.join(f'{x:.0%}' for x in state['reference_scenario']['wacc_scenarios'])}  ",
        "",
        "> Actual and target milestones are kept separate. Imprecise dates remain intervals; the model does not invent exact days.",
        "",
        "| Project | Permit->operational | Groundbreak->energized | Groundbreak->operational | Groundbreak->full phase | Right-censored |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    def shown(project, key):
        row = project["durations"].get(key)
        if not row:
            return "—"
        if row["months_low"] == row["months_high"]:
            return f"{row['months_mid']:.1f} mo"
        return f"{row['months_mid']:.1f} mo ({row['months_low']:.1f}-{row['months_high']:.1f})"

    for project in state["projects"]:
        censored = project["groundbreak_right_censored_months"]
        lines.append(
            f"| {project['name']} | {shown(project, 'permit_approved_to_first_operational')} | "
            f"{shown(project, 'groundbreak_to_first_energized')} | {shown(project, 'groundbreak_to_first_operational')} | "
            f"{shown(project, 'groundbreak_to_full_phase')} | {'—' if censored is None else f'{censored:.1f} mo'} |"
        )

    survival = state["groundbreak_to_first_operational_survival"]
    lines += [
        "",
        "## Survival curve status",
        "",
        f"- Observations: {survival['n']} ({survival['completed_events']} completed, {survival['right_censored']} right-censored).",
        f"- Status: `{survival['status']}`.",
    ]
    if survival["curve"]:
        lines += ["", "| Month | At risk | Operational probability |", "|---:|---:|---:|"]
        for row in survival["curve"]:
            lines.append(f"| {row['months']:.1f} | {row['at_risk']} | {row['prob_operational']:.1%} |")

    lines += [
        "",
        "## Economic-time interpretation",
        "",
        "- `full_capital_carry_usd_per_mw` assumes the entire reference capex is economically exposed from groundbreak; treat it as an upper-bound style scenario, not accounting depreciation.",
        "- `linear_spend_carry_usd_per_mw` assumes capital deploys evenly during construction, so average exposed capital is 50% of final capex.",
        "- Revenue delay and hardware obsolescence are separate layers and should be added only when project/company evidence supports them.",
        "",
    ]
    return "\n".join(lines)

def write_if_changed(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--write-state", action="store_true")
    args = parser.parse_args()

    projects = load_jsonl(PROJECT_PATH)
    config = load_json(CONFIG_PATH)
    as_of = parse_date(args.as_of) if args.as_of else date.today()
    state = build_state(projects, as_of, config)

    if args.validate_only:
        s = state["groundbreak_to_first_operational_survival"]
        print(f"VALID: {len(projects)} projects; time-observations={s['n']}; completed={s['completed_events']}; censored={s['right_censored']}")
        return

    state_json = json.dumps(state, indent=2, sort_keys=False) + "\n"
    state_md = render_markdown(state)
    if args.write_state:
        changed_json = write_if_changed(STATE_JSON, state_json)
        changed_md = write_if_changed(STATE_MD, state_md)
        print(f"state: {'updated' if changed_json or changed_md else 'unchanged'}")
    else:
        print(state_json)

if __name__ == "__main__":
    main()

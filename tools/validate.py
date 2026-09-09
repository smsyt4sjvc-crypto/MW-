#!/usr/bin/env python3
"""Validate MW/$ memory references, invariants, projections, and workbook integrity."""

from __future__ import annotations

import csv
import json
import math
import sys
import zipfile
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "memory"
ERRORS = []


def fail(message):
    ERRORS.append(message)


def load_jsonl(name):
    rows = []
    path = MEMORY / name
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"{name}:{number}: invalid JSON: {exc}")
            continue
        if not isinstance(value, dict):
            fail(f"{name}:{number}: record is not an object")
        rows.append(value)
    return rows


def index(rows, name):
    result = {}
    for row in rows:
        row_id = row.get("id")
        if not row_id:
            fail(f"{name}: missing id")
        elif row_id in result:
            fail(f"{name}: duplicate id {row_id}")
        else:
            result[row_id] = row
    return result


def require_ref(owner, field, values, target):
    for value in values:
        if value not in target:
            fail(f"{owner}: {field} references missing id {value}")


def read_csv(name):
    with (ROOT / "data" / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_schema(value, schema, location):
    """Validate the JSON Schema keywords used by the checked-in review schema."""
    kinds = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v),
        "null": lambda v: v is None,
    }
    allowed = schema.get("type")
    if allowed:
        allowed = allowed if isinstance(allowed, list) else [allowed]
        if not any(kinds[kind](value) for kind in allowed):
            fail(f"{location}: expected {allowed}")
            return
    if "const" in schema and value != schema["const"]:
        fail(f"{location}: incorrect constant")
    if "enum" in schema and value not in schema["enum"]:
        fail(f"{location}: unsupported enum value")
    if isinstance(value, dict):
        for field in schema.get("required", []):
            if field not in value:
                fail(f"{location}: missing {field}")
        for field, sub in schema.get("properties", {}).items():
            if field in value:
                validate_schema(value[field], sub, f"{location}.{field}")
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            fail(f"{location}: too few items")
        for i, item in enumerate(value):
            validate_schema(item, schema.get("items", {}), f"{location}[{i}]")
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value) or value < schema.get("minimum", -math.inf):
            fail(f"{location}: numeric bound violation")
    elif isinstance(value, str):
        try:
            if schema.get("format") == "date":
                date.fromisoformat(value)
            elif schema.get("format") == "date-time":
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            elif schema.get("format") == "uri" and not value.startswith(("https://", "http://")):
                fail(f"{location}: expected source URL")
        except ValueError:
            fail(f"{location}: invalid {schema.get('format')}")


manifest = json.loads((MEMORY / "manifest.json").read_text(encoding="utf-8"))
for path in [*manifest["canonical"].values(), *manifest["projections"].values()]:
    if not (ROOT / path).exists():
        fail(f"manifest path missing: {path}")
for path in manifest.get("operations", {}).values():
    if not (ROOT / path).exists():
        fail(f"operations path missing: {path}")

entities = index(load_jsonl("entities.jsonl"), "entities")
methods = index(load_jsonl("methods.jsonl"), "methods")
sources = index(load_jsonl("sources.jsonl"), "sources")
facts = index(load_jsonl("facts.jsonl"), "facts")
claims = index(load_jsonl("claims.jsonl"), "claims")
questions = index(load_jsonl("questions.jsonl"), "questions")
index(load_jsonl("changelog.jsonl"), "changelog")

require_ref(
    "manifest",
    "record_defaults.method_source_ids",
    manifest.get("record_defaults", {}).get("method_source_ids", []),
    sources,
)

for entity in entities.values():
    method_id = entity.get("method_id")
    if method_id and method_id not in methods:
        fail(f"{entity['id']}: missing method {method_id}")
for method in methods.values():
    require_ref(method["id"], "entity_id", [method.get("entity_id")], entities)
for fact in facts.values():
    for field in ("as_of", "metric", "unit", "scope", "evidence", "status", "source_ids", "tags"):
        if field not in fact:
            fail(f"{fact['id']}: missing field {field}")
    if fact.get("evidence") not in manifest["evidence_states"]:
        fail(f"{fact['id']}: unsupported evidence state {fact.get('evidence')}")
    if fact.get("status") not in manifest["status_values"]:
        fail(f"{fact['id']}: unsupported status {fact.get('status')}")
    require_ref(fact["id"], "entity_ids", fact.get("entity_ids", []), entities)
    require_ref(fact["id"], "source_ids", fact.get("source_ids", []), sources)
    require_ref(fact["id"], "depends_on", fact.get("depends_on", []), facts)
for claim in claims.values():
    require_ref(claim["id"], "supporting_fact_ids", claim.get("supporting_fact_ids", []), facts)
    require_ref(claim["id"], "disconfirming_fact_ids", claim.get("disconfirming_fact_ids", []), facts)
for question in questions.values():
    require_ref(question["id"], "entity_ids", question.get("entity_ids", []), entities)

queue = json.loads((MEMORY / "research-queue.json").read_text(encoding="utf-8"))
require_ref("research queue", "rotation_order", queue["rotation_order"], entities)
if not queue["rotation_order"] or len(queue["rotation_order"]) != len(set(queue["rotation_order"])):
    fail("research queue: empty or duplicate rotation")
for entity_id in queue["rotation_order"]:
    if entity_id in entities and not entities[entity_id].get("method_id"):
        fail(f"research queue: {entity_id} lacks a method")
require_ref("research queue", "last_reviewed", queue["last_reviewed"].keys(), entities)
for run in load_jsonl("research-runs.jsonl"):
    require_ref(run.get("id"), "entity_id", [run.get("entity_id")], entities)
    require_ref(run.get("id"), "source_ids", run.get("source_ids", []), sources)
    if run.get("review_path") and not (ROOT / run["review_path"]).exists():
        fail(f"{run.get('id')}: missing review file")
review_schema = json.loads((ROOT / "schemas/company-review.schema.json").read_text(encoding="utf-8"))
for review_path in (ROOT / "research/companies").glob("*/*.json"):
    review = json.loads(review_path.read_text(encoding="utf-8"))
    validate_schema(review, review_schema, str(review_path.relative_to(ROOT)))
    require_ref(review.get("id"), "entity_id", [review.get("entity_id")], entities)
    require_ref(review.get("id"), "method_id", [review.get("method_id")], methods)
    require_ref(review.get("id"), "source_ids", review.get("source_ids", []), sources)
    pue = review.get("pue", {})
    require_ref(review.get("id"), "pue.source_ids", pue.get("source_ids", []), sources)
    values = [pue.get(key) for key in ("low", "base", "high")]
    if all(isinstance(value, (int, float)) for value in values) and values != sorted(values):
        fail(f"{review.get('id')}: PUE range is not ordered low <= base <= high")
    if pue.get("status") in ("reported", "inferred", "proxy") and not pue.get("source_ids"):
        fail(f"{review.get('id')}: numeric PUE needs sources")

nscale = facts.get("F-NSCALE-REV-MW", {}).get("value")
if nscale is not None and not math.isclose(nscale, 45e9 / 6 / 460 / 1e6, rel_tol=1e-10):
    fail("F-NSCALE-REV-MW does not match its canonical formula")
jevons = facts.get("F-VERCEL-JUL-BREAKEVEN", {}).get("value")
if jevons is not None and not math.isclose(jevons, 0.136 / (1 - 0.136), rel_tol=1e-9):
    fail("F-VERCEL-JUL-BREAKEVEN does not match d/(1-d)")

csv_rows = {}
for csv_name in (
    "company-methods.csv",
    "company-models.csv",
    "power-compute-benchmarks.csv",
    "token-economics.csv",
    "source-register.csv",
):
    csv_rows[csv_name] = read_csv(csv_name)
    for row_number, row in enumerate(csv_rows[csv_name], start=2):
        source_id = row.get("source_id")
        if source_id and source_id not in sources:
            fail(f"data/{csv_name}:{row_number}: unknown source_id {source_id}")

for csv_name in ("company-methods.csv", "company-models.csv"):
    projected = {row["method_id"] for row in csv_rows[csv_name]}
    if projected != set(methods):
        fail(f"data/{csv_name}: method IDs differ from memory/methods.jsonl")
projected_sources = {row["source_id"] for row in csv_rows["source-register.csv"]}
if projected_sources != set(sources):
    fail("data/source-register.csv: source IDs differ from memory/sources.jsonl")

workbook = ROOT / manifest["projections"]["workbook"]
if workbook.exists() and not zipfile.is_zipfile(workbook):
    fail(f"{workbook.relative_to(ROOT)} is not a valid XLSX zip container")

if ERRORS:
    print("INVALID")
    for error in ERRORS:
        print(f"- {error}")
    sys.exit(1)
print(
    f"VALID: {len(entities)} entities, {len(methods)} methods, {len(facts)} facts, "
    f"{len(claims)} claims, {len(questions)} open questions, {len(sources)} sources"
)

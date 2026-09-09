#!/usr/bin/env python3
"""Emit minimal, provenance-complete MW/$ context for another agent."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "memory"


def load_json(name: str):
    return json.loads((MEMORY / name).read_text(encoding="utf-8"))


def load_jsonl(name: str):
    records = []
    for line in (MEMORY / name).read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def referenced_sources(records):
    ids = set()
    for record in records:
        ids.update(record.get("source_ids", []))
    sources = {row["id"]: row for row in load_jsonl("sources.jsonl")}
    return [sources[source_id] for source_id in sorted(ids) if source_id in sources]


def related_claims(facts, claims):
    fact_ids = {row["id"] for row in facts}
    return [
        row
        for row in claims
        if fact_ids.intersection(row.get("supporting_fact_ids", []))
        or fact_ids.intersection(row.get("disconfirming_fact_ids", []))
    ]


def payload_for_entity(query: str):
    entities = load_jsonl("entities.jsonl")
    needle = norm(query)
    matches = []
    for entity in entities:
        keys = [entity["id"], entity["name"], *entity.get("aliases", [])]
        if any(needle == norm(key) for key in keys):
            matches.append(entity)
    if not matches:
        for entity in entities:
            keys = [entity["id"], entity["name"], *entity.get("aliases", [])]
            if any(needle in norm(key) for key in keys):
                matches.append(entity)
    if len(matches) != 1:
        choices = [row["id"] for row in matches] or [row["id"] for row in entities]
        raise SystemExit(f"Entity query must resolve uniquely. Candidates: {', '.join(choices)}")

    entity = matches[0]
    entity_id = entity["id"]
    facts = [row for row in load_jsonl("facts.jsonl") if entity_id in row.get("entity_ids", [])]
    claims = related_claims(facts, load_jsonl("claims.jsonl"))
    questions = [row for row in load_jsonl("questions.jsonl") if entity_id in row.get("entity_ids", [])]
    methods = [row for row in load_jsonl("methods.jsonl") if row["entity_id"] == entity_id]
    method_sources = load_json("manifest.json").get("record_defaults", {}).get("method_source_ids", [])
    return {
        "query": {"type": "entity", "value": query},
        "entity": entity,
        "methods": methods,
        "facts": facts,
        "claims": claims,
        "open_questions": questions,
        "sources": referenced_sources([*facts, {"source_ids": method_sources}]),
    }


def payload_for_topic(tag: str):
    valid_tags = load_json("manifest.json")["topic_tags"]
    if tag not in valid_tags:
        raise SystemExit(f"Unknown topic tag. Valid tags: {', '.join(valid_tags)}")
    facts = [row for row in load_jsonl("facts.jsonl") if tag in row.get("tags", [])]
    claims = [row for row in load_jsonl("claims.jsonl") if tag in row.get("tags", [])]
    questions = [row for row in load_jsonl("questions.jsonl") if tag in row.get("tags", [])]
    entity_ids = {entity_id for row in facts for entity_id in row.get("entity_ids", [])}
    entities = [row for row in load_jsonl("entities.jsonl") if row["id"] in entity_ids]
    method_ids = {row.get("method_id") for row in entities if row.get("method_id")}
    methods = [row for row in load_jsonl("methods.jsonl") if row["id"] in method_ids]
    method_sources = load_json("manifest.json").get("record_defaults", {}).get("method_source_ids", [])
    return {
        "query": {"type": "topic", "value": tag},
        "entities": entities,
        "methods": methods,
        "facts": facts,
        "claims": claims,
        "open_questions": questions,
        "sources": referenced_sources([*facts, {"source_ids": method_sources}]),
    }


def payload_bootstrap():
    claims = load_jsonl("claims.jsonl")
    claim_fact_ids = {
        fact_id
        for row in claims
        for fact_id in row.get("supporting_fact_ids", []) + row.get("disconfirming_fact_ids", [])
    }
    facts = [row for row in load_jsonl("facts.jsonl") if row["id"] in claim_fact_ids]
    questions = sorted(load_jsonl("questions.jsonl"), key=lambda row: (row["priority"], row["id"]))
    manifest = load_json("manifest.json")
    return {
        "query": {"type": "bootstrap"},
        "as_of": manifest["as_of"],
        "purpose": manifest["purpose"],
        "unit_conventions": manifest["unit_conventions"],
        "claims": claims,
        "claim_facts": facts,
        "open_questions": questions,
        "sources": referenced_sources(facts),
        "next": manifest["retrieval"],
    }


def payload_next():
    queue = load_json("research-queue.json")
    local_date = datetime.now(ZoneInfo(queue["timezone"])).date().isoformat()
    if queue.get("last_attempt_local_date") == local_date:
        if queue.get("last_attempt_outcome") in ("complete", "partial"):
            return {"local_date": local_date, "action": "already_reviewed", "entity_id": queue["last_attempt_entity_id"]}
        if queue.get("last_attempt_entity_id"):
            selected = queue["last_attempt_entity_id"]
        else:
            selected = None
    else:
        selected = None
    if selected is None:
        order = queue["rotation_order"]
        selected = min(order, key=lambda entity_id: (queue["last_reviewed"].get(entity_id) or "", order.index(entity_id)))
    return {"local_date": local_date, "action": "review", "entity_id": selected,
            "protocol": "ops/daily-company-research.md", "context": payload_for_entity(selected)}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("bootstrap")
    entity = sub.add_parser("entity")
    entity.add_argument("query")
    topic = sub.add_parser("topic")
    topic.add_argument("tag")
    sub.add_parser("open")
    sub.add_parser("next")
    args = parser.parse_args()

    if args.command == "bootstrap":
        payload = payload_bootstrap()
    elif args.command == "entity":
        payload = payload_for_entity(args.query)
    elif args.command == "topic":
        payload = payload_for_topic(args.tag)
    elif args.command == "next":
        payload = payload_next()
    else:
        payload = {
            "query": {"type": "open"},
            "open_questions": sorted(
                load_jsonl("questions.jsonl"), key=lambda row: (row["priority"], row["id"])
            ),
        }
    json.dump(payload, sys.stdout, indent=2, sort_keys=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

# MW/$ agent contract

This repository is persistent memory for AI-compute economics. Optimize for correct agent retrieval, provenance, and update safety. Human readability is secondary.

## Mandatory bootstrap

1. Read `AGENTS.md`.
2. Read `memory/manifest.json`.
3. Run `python3 tools/context.py bootstrap`.
4. Before entity/topic work, run `python3 tools/context.py entity <id>` or `python3 tools/context.py topic <tag>`.
5. Run `python3 tools/validate.py` before committing.

For the authorized recurring research cycle, read `ops/daily-company-research.md` and run `python3 tools/context.py next`. Standing authorization and repository boundaries are recorded in `ops/authorization.json`.

Do not recursively ingest the repository unless auditing. Search before declaring information absent.

## Authority order

1. Current user instruction
2. `AGENTS.md` — behavior and invariants
3. `memory/manifest.json` — routing and canonical-file map
4. `memory/*.jsonl` — atomic source of truth
5. `data/*.csv` — model inputs/projections
6. `data/ai-compute-economics.xlsx` — generated compatibility artifact
7. `wiki/` and `state/` — secondary narrative views
8. `logs/` — history, not current truth by itself

If records conflict, prefer stronger evidence and later `as_of`; preserve the conflict explicitly. Never silently reconcile incompatible scopes.

## Invariants

- Every fact has a stable ID, `as_of`, evidence state, unit/scope, and source IDs.
- DATA (`memory/facts.jsonl`) and THESIS (`memory/claims.jsonl`) stay separate.
- Label power as `generation`, `facility`, `it_load`, or `effective_utilized_it`.
- Label dollar perimeter explicitly: segment revenue, AI-attributed revenue, contract revenue, compute capex, facility capex, silicon content, etc.
- Convert power scopes explicitly. Keep PUE, availability, reserve, and utilization separate; do not double-count reliability.
- Divide period revenue by period-average active capacity, never exit-rate capacity.
- AI revenue attribution is editable and sourced, never assumed.
- Standardize the final unit, not each company's route. Apply its method record.
- Exact Jevons break-even for price decline `d` is `d / (1 - d)`.
- Demand, tightness, and monetization are separate gauges.
- List price is not realized price.
- Supersede errors visibly; never erase correction history.
- Blank output beats invented precision.

Canonical operator output: `USD_millions_per_effective_utilized_IT_MW_year`.

`effective_utilized_it_mw = reported_mw * scope_conversion * availability * reserve_factor * utilization`

Use availability and reserve together only when the source defines distinct effects. A contract-rate output may use utilization 1 only when labeled contracted economics, not physical utilization.

## Mutation protocol

1. Register the source in `memory/sources.jsonl`.
2. Add or supersede atomic facts in `memory/facts.jsonl`.
3. Update affected method, claim, and open-question records.
4. Update affected CSV model inputs/projections.
5. Rebuild the workbook with `tools/build_workbook.mjs` if CSVs changed.
6. Append one `memory/changelog.jsonl` record.
7. Update secondary Markdown only if its conclusion changed.
8. Run `python3 tools/validate.py`.

User authorization dated 2026-09-09 permits research updates and pushes to the public `smsyt4sjvc-crypto/MW-` repository and the daily one-company research task. This permission persists across sessions; routine updates in this scope do not require renewed confirmation. Never access or modify `Wiki-Brain` during this recurring task: it is a separate research vault. Existing reference links remain historical provenance only. Additional paid services, trading, or unrelated automations are outside this authorization.

## Response behavior

Lead with the result. State scope, date, unit, method ID, and evidence status. Name the strongest disconfirming fact. If incomplete, name the exact missing numerator, denominator, or attribution bridge.

# One-company research protocol

Target: `smsyt4sjvc-crypto/MW-`, branch `main`. Authoritative permission: `ops/authorization.json`. The user does not browse this vault; optimize retrieval and persistent updates for agents. Never access or mutate `Wiki-Brain` during this process.

## Select and resume

Fetch current main before work. Read AGENTS, manifest, queue, and the selected entity's context. `python3 tools/context.py next` returns the least recently reviewed eligible company; ties follow rotation order. First review: Oracle OCI. Review one company per America/Los_Angeles calendar day. A persisted attempt with today's local date makes retries idempotent; recover an interrupted attempt for the same company rather than moving to another. Refresh the whole rotation continuously. Add a newly implicated counterparty with its own method and a primary-source relationship; don't turn a single company's review into an unbounded market scan.

## Retrieve evidence

Open the latest available annual filing (10-K/20-F or equivalent), quarterly filing (10-Q/6-K), earnings release, company presentation and prepared remarks/transcript, and relevant material 8-K/6-K exhibits. Verify publication dates and fiscal periods. Retrieve the selected company's structured deals: signed compute offtake, take-or-pay, prepayments, GPU or facility leases, customer-supplied hardware, PPAs, project financing, debt/SPV/VIE arrangements, guarantees, residual-value commitments, related-party transactions, and capacity delivery schedules. Prefer regulator, issuer, counterparty, utility and permitting originals. Extract sustainability/energy disclosures and site design details when needed for power conversion. For private companies use public issuer/counterparty documents; explicitly record disclosure gaps.

Register exact document URLs, filing accession when available, page/table/section locators, period, publication date, and retrieval timestamp. Source a narrow observation rather than a generic investor-relations home page. Keep financial observations from new primaries distinct from inherited chat/reference estimates. Do not promote a historical compiled claim to verified status without reading the original.

## Produce a company-specific model

Use the existing method's numerator and exclusions. Identify recognized revenue, annualized run rate, contracted value and RPO separately. Reconstruct time-weighted active capacity over the revenue period; show activation dates and ramp assumptions. Do not divide a quarter's revenue by exit or announced MW. Isolate AI compute, internal workloads, pass-through hardware, storage/services and mining as applicable. Keep owned, leased, customer-owned and project-level assets distinct.

PUE means total data-center energy / IT-equipment energy over the same boundary and period. It measures facility overhead, not GPU utilization or revenue productivity. Method reference: https://datacenters.google/efficiency/ .

PUE evidence order:

1. Same-site and same-period measured PUE, with boundary and methodology.
2. A disclosed fleet annual PUE, with coverage and period mismatch flagged.
3. A clearly labeled inferred range using disclosed energy/IT energy, or a reproducible bottom-up cooling/electrical-overhead model.
4. A matched site/technology/geography proxy range with sourced assumptions and explicit transfer limits.
5. `not_disclosed` if evidence cannot support even a useful range; do not invent a universal PUE. Record the exact missing input and sensitivity, when defensible.

Calculate aggregate PUE as sum(total energy) / sum(IT energy), equivalently IT-energy-weighted site PUE; do not use a simple site average. A design target is not a measured operational PUE. If only generation capacity or fuel input is known, model generation availability/reserve/conversion separately. Do not label a generation-to-IT ratio as PUE.

Keep three fields distinct: reported PUE; modeled low/base/high PUE; PUE selected for the model with rationale. Extrapolate transparently. Use `not_applicable` for a supplier's own PUE when it does not describe the compute sold; carry customer-site assumptions only in a separately labeled deployment model.

Outputs when supported: IT MW, effective utilized IT MW, annualized attributable revenue, revenue per IT MW-year, revenue per effective utilized IT MW-year, capex per IT MW and per GW, token/task economics, utilization and power-cost sensitivities. Keep contracted revenue per contracted MW separate from physical utilization economics. For vendors report silicon/system content per IT GW with architecture mix. Never force a vendor onto an operator revenue metric.

Low/high scenarios must jointly vary documented uncertain inputs; never present arbitrary narrow confidence intervals. Keep gross revenue payback separate from cash payback and include power, operating costs, financing, useful life and replacement risk when inputs support them. Connect price/volume/token/task changes to Jevons and open/proprietary mix only with scoped evidence; a missing metric is a finding.

## Persist and verify

Write `research/companies/<entity_id>/<local-date>.json` matching `schemas/company-review.schema.json`. Add/supersede facts, methods, source pointers, claims and questions using stable IDs. Preserve prior record versions and correction reasons; use a new dated fact ID for each new observation rather than overwriting a time series. Update affected CSV projections and workbook when economics inputs change. If the spreadsheet runtime is unavailable, retain the structured research, mark the workbook stale explicitly, and record the rebuild gap rather than pretending it was refreshed.

Append `{id, date, entity_id, outcome, review_path, source_ids, summary}` to `memory/research-runs.jsonl`. Update queue last-reviewed and last-attempt fields in the same commit. An honest partial model advances the queue; an access failure leaves the company due for the next run. Validate JSON/schema, IDs, source links, period/perimeter consistency, formula results, and projections using `python3 tools/validate.py` plus targeted arithmetic. Fetch main again before publication; reconcile concurrent edits and fast-forward only. Commit/push only MW- and verify the remote commit and review file. Record failures truthfully; never claim a push completed without readback.

Return a short result: company, strongest new finding, reported or estimated PUE, revenue-per-MW range or exact gap, material financing/deal implication, and verified commit link. No requirement for the user to open the repo. If blocked, name the blocker and what remains saved.

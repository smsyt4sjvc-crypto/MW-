# MW/$ project time and depreciation model

## Objective

Measure the time between project commitment, permits, shovels, energized capacity and billable/operational MW, then convert delay into economic capital drag without confusing that drag with GAAP depreciation.

The core chain is:

`contract -> permit filed -> permit approved -> site work -> groundbreak -> power available -> first energized MW -> first operational MW -> first billable MW -> full phase -> full campus`

This is the time axis of MW/$.

## Core rules

1. Keep **actual** and **target** dates separate. A target COD is not an operating milestone.
2. Never invent an exact day from a month, quarter, half-year or year disclosure. Store a date interval and its precision.
3. Use source-reported durations directly when the source gives a duration but not exact endpoints.
4. Treat unfinished projects as **right-censored** observations rather than dropping them from the sample.
5. Do not mix IT-load MW, facility MW and generation MW.
6. The reference `$50M / IT MW` is a scenario benchmark. Use project-specific capex when a compatible denominator exists.
7. Separate economic time drag from accounting depreciation. Construction-in-progress may have no book depreciation while capital is economically tied up.
8. Separate facility/site life from compute-hardware obsolescence. Never apply an AI capability-price decline to the whole building.
9. Revenue delay is not profit loss. Track delayed revenue separately from capital carry and only when a sourced company-specific revenue/MW bridge exists.
10. Blank output beats false precision.

## Canonical milestones

- `contract_committed`
- `permit_filed`
- `permit_approved`
- `site_work_start`
- `groundbreak`
- `shell_ready`
- `power_available`
- `first_energized_mw`
- `first_operational_mw`
- `first_billable_mw`
- `full_phase_operational`
- `full_campus_operational`

Each milestone stores `date_start`, `date_end`, `precision`, `status`, and source IDs. Exact dates use the same start/end date.

When a source directly reports a duration, store it in `duration_observations` with `from_event`, `to_event`, and exact/range days. This is preferred to reverse-engineering a fake endpoint.

## Primary latency metrics

- Permit latency = permit approved - permit filed
- Approval-to-shovels = site work start - permit approved
- Permit-approved-to-groundbreak = groundbreak - permit approved
- Groundbreak-to-first-energized = first energized MW - groundbreak
- Groundbreak-to-first-operational = first operational MW - groundbreak
- Groundbreak-to-first-billable = first billable MW - groundbreak
- Energized-to-operational = first operational MW - first energized MW
- Operational-to-billable = first billable MW - first operational MW
- Energized-to-billable = first billable MW - first energized MW
- Billable-to-full-phase = full phase operational - first billable MW
- Contract-to-first-operational = first operational MW - contract committed
- Contract-to-first-billable = first billable MW - contract committed
- Permit-approved-to-first-energized = first energized MW - permit approved
- Permit-approved-to-first-operational = first operational MW - permit approved
- Permit-approved-to-full-phase = full phase operational - permit approved
- Groundbreak-to-full-phase = full phase operational - groundbreak
- Groundbreak-to-full-campus = full campus operational - groundbreak

## Economic-time metrics

Reference capital carry at full exposure:

`carry_per_MW = capex_per_MW * WACC * years_to_operation`

A more realistic simple build-spend scenario assumes capex deploys linearly from zero to full:

`linear_spend_carry_per_MW = 0.5 * capex_per_MW * WACC * years_to_operation`

At the reference $50M/MW:

- 8% WACC = $333,333/MW/month at full-capital exposure
- 10% WACC = $416,667/MW/month at full-capital exposure
- linear-spend approximation is half those values during construction

Time-adjusted capital velocity:

`MW_per_$B_year = (MW / capex_$B) / years_to_operation`

At $50M/MW the static capital density is 20 MW/$B. A 12-month build is therefore 20 MW/$B-year; 24 months is 10; 36 months is 6.67.

## Delay / depreciation layers

Track three separate curves.

### 1. Capital time drag
Opportunity cost of capital tied up before useful/billable MW. Use project-specific spend timing when available; otherwise show full-capital and linear-spend scenarios separately.

### 2. Revenue delay
Company-specific billable capacity delayed by schedule slippage. Use only with a sourced revenue/MW bridge. Do not treat revenue as profit.

### 3. Hardware obsolescence / generation gap
Only apply when accelerator procurement timing is known.

`generation_gap = deployed_compute_per_MW_at_COD / frontier_compute_per_MW_at_COD`

If chips are already purchased and wait for power, measure the stranded-silicon holding period separately. If the site can simply install a newer accelerator generation at COD, do not depreciate the whole facility as though the old chips were stranded.

## Forward rental prices and billing cohorts

Use the optional `PROJECT-TIME-FORWARD-RENTAL-V1` extension only after a liquid matching-generation curve is available. CME's planned H100 and B200 contracts reference cash-settled neocloud rental indices; they do not deliver GPUs or guarantee occupancy.

1. Match each accelerator cohort's first-billable month, contract renewal and refinancing date to available maturities. Keep dates beyond the quoted horizon open.
2. Store quote timestamp, maturity, GPU generation, index boundary, volume, open interest and spread. An indicative quote is not evidence of executable hedge capacity.
3. Map benchmark price to realized service price with sourced adjustments for cluster, geography, networking, duration and service mix. Model differences explicitly; do not silently treat the index as hyperscaler or dedicated-cluster pricing.
4. Forecast merchant rental revenue as the sum over cohorts/months of GPU count times calendar hours times billed occupancy times realized USD per GPU-hour. Apply actual contract revenue-recognition terms to fixed-price offtake instead. Billable occupancy and physical utilization are distinct.
5. Derive GPUs per IT MW from the full IT-system power perimeter, including associated IT networking/CPU/memory. GPU nameplate watts alone do not supply this bridge. Convert facility power through matched PUE only when necessary.
6. Canonical revenue/MW requires annualized attributable recognized revenue and period-average effective utilized AI IT MW on the same perimeter. Do not apply an occupancy or utilization factor twice.
7. Evaluate cash flows over their actual dates, subtracting scoped power/opex, capex and replacements. Keep unlevered DCF separate from debt/equity cash flows; do not double-count WACC carry or financing.
8. Stress rental-rate renewal exposure against debt service and replacement timing. Treat guarantee risk separately using its legal asset perimeter, valuation date, threshold and trigger conditions. A rental-index decline alone is not an RVG trigger or hardware resale mark.

Forward prices contain risk/liquidity premia and are not unbiased forecasts. Hedging does not remove basis, volume, availability, customer-credit, margin-liquidity or construction risk. Do not extrapolate H100/B200 prices into Rubin, TPU or an undated generic compute unit.

Evidence as of October 4, 2026: `SRC-CME-COMPUTE-SPECS-20261004`; launch unresolved under `SRC-CME-COMPUTE-REVISED-20261004`. No live curve is populated.

## Statistical treatment

The main empirical curve is survival analysis.

For each project with a known groundbreak:
- completed: event occurs at first energized/billable/operational milestone;
- unfinished: right-censored at the latest observation date;
- imprecise dates: interval bounds are preserved and midpoint is used only for the displayed base estimate.

Build Kaplan-Meier-style curves for:
- groundbreak -> first operational MW;
- permit approval -> first operational MW;
- first operational MW -> full phase.

Publish unweighted project counts first. Add MW-weighted curves only where MW boundaries are comparable.

Split the sample when coverage permits:
- greenfield vs retrofit;
- grid vs behind-the-meter / dedicated generation;
- project size;
- geography;
- developer/operator;
- accelerator generation;
- year of groundbreak.

## Research cadence

During every infrastructure scan, collect dates whenever a primary source materially identifies:
- permit filing/approval;
- site preparation or groundbreak;
- power reservation or first available power;
- commissioning;
- first racks/workloads;
- first customer/billable MW;
- phase/campus completion;
- target COD changes or slippage.

The weekly infrastructure run should update the time ledger before rebuilding state. The monthly audit should publish the latency distribution, censored observations, and the strongest source of delay by stage.

## Outputs

- `state/project-time-depreciation.json`
- `state/project-time-depreciation.md`

Tool:

`python3 tools/project_time_model.py --write-state`

Validation:

`python3 tools/project_time_model.py --validate-only`

The model becomes decision-useful as the project sample grows; until then, display sample size and censoring explicitly rather than implying population precision.

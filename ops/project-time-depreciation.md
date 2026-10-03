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

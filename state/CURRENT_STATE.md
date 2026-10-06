# Current state

**As of:** 2026-10-06
**Evidence:** published company reviews through xAI/SpaceX; historical token samples; seeded project-time model; CME product specifications.
**Methods:** company-specific operator/vendor methods plus `PROJECT-TIME-DEPRECIATION-V1`. Includes the October 6 xAI/SpaceX review, the October 5 Nscale review and the separately authorized compute-futures topic update.

## Current read

AI demand growth can coexist with weak returns on newly financed capacity. The unresolved question is how much attributable cash a particular cohort earns after it becomes billable, relative to its construction spending, fixed obligations and replacement needs. Demand, token expenditure, GPU rental revenue, hardware sales and project cash returns remain separate measurements.

Time makes the test stricter: a MW delivered in 2028 must be evaluated against its 2028 hardware, achievable rental rates and costs. Today's shortage or spot price cannot establish that project's return. A late build can accumulate capital cost before billing and, where chips were purchased early, lose competitive life while waiting for power. Deferring hardware procurement can reduce that second risk; the whole facility should not inherit a GPU obsolescence rate.

The financing reviews show large leases, prepayments, purchase commitments and project guarantees alongside demand commitments. Offtake and customer funding can protect timing or price, but their enforceability, customer credit, delivery conditions, hardware replacements and maturities determine protection. Meta's June 30 Hyperion maximum exposure was $46.03B; its $278.99B of uncommenced leases is a different perimeter and must not be added to that exposure without reconciliation.

Nscale makes the time risk concrete: the filed Anthropic order starts fees only after acceptance, allows delay-related discounts and termination, and includes a financing longstop. Its September 25 corporate convertible raise supports funding but does not itself confirm the Monarch project is fully financed. The October 1 deployment update is positive execution evidence, while matched PUE and recognized revenue per effective IT MW remain unknown. See `research/companies/nscale_anthropic/2026-10-05.json`.

xAI/SpaceX now supplies a cleaner reality check. Q2 recognized $1.6B of incremental cloud revenue while total installed nameplate IT draw moved from a 1.0GW Q1 exit to 1.4GW at Q2 exit. A 1.0-1.4GW average bound implies $4.57-$6.40M of annualized recognized cloud revenue per total nameplate MW-year, $5.33M at a linear-ramp base. That is not the canonical effective-MW rate: the denominator includes internal capacity, physical utilization is missing, and the filing explicitly says nameplate draw is not actual consumption. PUE is also undisclosed because the metric excludes facility overhead. See `research/companies/xai_spacex/2026-10-06.json`.

## The measurements we can and cannot compare

| Stored measure | Value | Evidence and limit |
|---|---:|---|
| IREN Microsoft contract value per stated IT MW-year | $9.67M | Derived contract rate, not recognized revenue or physical utilization |
| Nscale/Anthropic current contract | Up to $44.6B; normalized rate unresolved | Primary S-1 and order: capacity, term and price redacted; old $16.30M anchor retained only as historical reference |
| CoreWeave Q2 all-cloud annualized reference | $8.24M per modeled average active-power MW-year | Includes unisolated services; power boundary and linear ramp are not measured average AI IT MW |
| xAI recognized Q2 new-cloud / total nameplate diagnostic | $4.57M-$6.40M per modeled average nameplate IT MW-year | Primary revenue and exit metrics; noncanonical because external allocation and utilization are missing |
| xAI management monetization guidance | $30M-$50M per stated MW-year | Primary call best guess; forward/Rubin and time/power boundary unresolved; not a realized Q2 rate |
| Hyperscaler AI revenue per effective utilized IT MW-year | Unresolved | Matching AI numerator, period-average capacity and utilization remain incomplete |

These are not an apples-to-apples ranking. Prior $10M-$12M merchant and $25M healthy-case anchors remain historical model references, not verified current universal rates. Supplier silicon content per IT GW is capex content, not an operator revenue multiple. Meta's reported 1.08 FY2024 fleet PUE is historical context, not a matched Q2 2026 AI conversion.

## Time is now an explicit part of MW/$

The existing time ledger follows permits, construction, energization, operations and billing separately. Its October 2 seed has only three completed groundbreak-to-operational observations: Colossus about 4.0 months, Abilene about 12.3 months and Fairwater about 31.2 months. Sites, phases and definitions differ. Jupiter lacks the required endpoints. There are no usable censored observations in this seed, so the survival curve is not a credible industry forecast.

Illustrative economics at **$50M per IT MW** and **8%-10% cost of capital**, with spending ramping evenly during construction:

| Build duration | Capital carry per IT MW | Capacity delivered per $1B per build-year |
|---|---:|---:|
| 12 months | $2.0M-$2.5M | 20.0 MW |
| 24 months | $4.0M-$5.0M | 10.0 MW |
| 36 months | $6.0M-$7.5M | 6.7 MW |

These are scenarios, not observed project costs or accounting depreciation. An extra year after the entire $50M/MW has been spent carries $4M-$5M/MW, not the half-exposure construction figure. Use actual draw schedules where known. Do not add WACC carry on top of a DCF that already accounts for the same timing and capital cost.

Delayed revenue is separate from delayed profit. Hardware economic obsolescence, book depreciation, facility life and guarantee valuation are separate again.

## New compute-futures evidence

The October 3 FT commentary raises the possibility that compute derivatives improve price discovery. CME's own specifications describe financially settled H100/GPU1 and B200/GPU2 contracts: 730 GPU-hours each, monthly maturities out 36 months, based on non-hyperscaler on-demand rental indices. These are rental-price hedges, not physical GPU delivery or loan securitizations.

The original October 5 launch target remains unconfirmed on the October 5 recheck: the revised CME notice title says effective date to be announced. No live, liquid forward curve has been established here.

If trading becomes liquid, compare each project's first-billing, renewal and refinancing dates with the matching GPU-generation rental curve. Adjust for configuration, networking, geography, tenancy, contract length and service mix. Do not treat a forward quote as an unbiased forecast, hardware resale value, guaranteed occupancy or contracted operator revenue. A short futures hedge can offset benchmark price declines, but basis, volume, margin liquidity, construction and customer risks remain.

A lower curve could challenge future merchant earnings and refinancing assumptions. It does not automatically trigger a residual-value guarantee; asset perimeter, valuation date, threshold and contract conditions control that outcome.

## Token demand and the disconfirming evidence

Vercel's July sample showed volume +59%, price -13.6% and spending +37%, well beyond the exact 15.7% volume break-even. That is evidence against treating all efficiency gains as lost spending. It is historical and sample-specific. Ramp's September $0.68/million-token observation uses a different business sample; it cannot be spliced into Vercel or converted directly into MW revenue.

The thesis would weaken if projects arrive on schedule, realized cohort cash margins remain strong through renewal, enforceable offtake covers debt and replacements, and utilization absorbs efficiency gains. It would strengthen if delivery slips, same-generation realized rents fall, cash payback extends beyond economic hardware life, or refinancing relies increasingly on guarantees.

## Exact gaps and next evidence

- Live futures listing, dated quotes, volume, open interest and bid-ask spreads.
- Project spend schedules, first billable dates and accelerator procurement/installation cohorts.
- GPU density per IT MW, realized rental basis, billable occupancy and separately measured physical utilization.
- Same-period attributable revenue, operating cash costs, financing terms and replacement cash needs.
- Contract renewal, debt maturity and guarantee test dates.
- More comparable completed and unfinished projects for the latency distribution.

Canonical metric remains USD millions per effective utilized IT MW-year, with matching-period capacity. The added time dimension evaluates when that earning capacity arrives and how long its cash returns last.

## Evidence map

New sources: `SRC-FT-COMPUTE-FUTURES-20261003`, `SRC-CME-COMPUTE-SPECS-20261004`, `SRC-CME-COMPUTE-REVISED-20261004`, `SRC-CME-COMPUTE-ANNOUNCE-20260811`, `SRC-MW-TIME-METHOD-20261002`. See `research/topics/compute-futures/2026-10-04.json`.

Company facts: `F-IREN-MSFT-RATE`, `F-NSCALE-REV-MW`, `F-CRWV-ALLCLOUD-PER-FACILITYMW-Q2FY26`, `F-XAI-CLOUD-PER-NAMEPLATE-MW-Q2FY26`, `F-XAI-MONETIZATION-GUIDANCE-Q2FY26`, `F-META-HYPERION-MAX-EXPOSURE`, `F-META-UNCOMMENCED-LEASE-JUN26`, `F-META-PUE-FY24`. Time ledger and its underlying source IDs: `state/project-time-depreciation.json`. Existing token facts retain their original dates and sample boundaries.

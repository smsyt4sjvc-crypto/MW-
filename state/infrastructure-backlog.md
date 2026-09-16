# Data-center infrastructure backlog checker

**As of:** 2026-09-15  
**Source data through:** 2026-06-30  
**Region:** North America unless observation scope says otherwise  
**Method:** `INFRA-BOTTLENECK-CYCLE-V2`  

> Pressure, pricing power, investment-cycle stage and evidence coverage are separate. A hot bottleneck can already be late-cycle.

| Layer | Pressure | Pricing | Cycle stage | Action | Cycle cov. | Scarcity monetization | Verified IT MW |
|---|---:|---:|---|---|---:|---:|---:|
| Land & permitting | — | — | NO_SIGNAL | **WATCH** | 0% | — | 0.0 |
| Civil & excavation | 82.6 | — | SCARCITY_CONFIRMED | **ACCUMULATE** | 21% | — | 0.0 |
| Structure & shell | — | — | NO_SIGNAL | **WATCH** | 0% | — | 0.0 |
| HV / interconnect | 90.0 | 100.0 | PEAK_MONETIZATION | **HOLD** | 23% | 90.0 | 0.0 |
| Generation / backup power | 99.0 | — | SCARCITY_CONFIRMED | **ACCUMULATE** | 15% | — | 0.0 |
| Electrical distribution | 68.4 | 78.5 | MONETIZATION | **ADD_HOLD** | 34% | 53.7 | 0.0 |
| Cooling | 84.8 | 100.0 | PEAK_MONETIZATION | **HOLD** | 39% | 84.8 | 0.0 |
| MEP / modular integration | 91.0 | — | SCARCITY_CONFIRMED | **ACCUMULATE** | 15% | — | 0.0 |
| Commissioning | — | — | NO_SIGNAL | **WATCH** | 0% | — | 0.0 |
| PUE / operations | — | — | NO_SIGNAL | **WATCH** | 0% | — | 0.0 |

## Supplier / contractor investment cycle

| Entity | Ticker | Pressure | Pricing | Cycle stage | Action | Cycle cov. |
|---|---|---:|---:|---|---|---:|
| Eaton | ETN | 68.4 | 78.5 | MONETIZATION | **ADD_HOLD** | 34% |
| GE Vernova | GEV | 93.8 | 100.0 | PEAK_MONETIZATION | **HOLD** | 28% |
| Trane Technologies | TT | 80.8 | — | SCARCITY_CONFIRMED | **ACCUMULATE** | 27% |
| Modine | MOD | 100.0 | 100.0 | PEAK_MONETIZATION | **HOLD** | 21% |
| Comfort Systems USA | FIX | 91.0 | — | SCARCITY_CONFIRMED | **ACCUMULATE** | 15% |
| Sterling Infrastructure | STRL | 82.6 | — | SCARCITY_CONFIRMED | **ACCUMULATE** | 21% |

## Investment action board

- **ACCUMULATE:** `TT`, `STRL`, `FIX`
- **ADD_HOLD:** `ETN`
- **HOLD:** `GEV`, `MOD`
- **WATCH:** none among seeded suppliers
- **RISK_OFF_REDUCE:** none yet
- **SELL_AVOID:** none yet

These labels describe position in the infrastructure scarcity/monetization cycle. They are not a valuation score. A name can be in an attractive industrial-cycle phase and still be expensive at the equity level.

## Cycle logic

`PRE_SCARCITY -> SCARCITY_FORMING -> SCARCITY_CONFIRMED -> MONETIZATION -> PEAK_MONETIZATION -> CAPACITY_CATCH_UP -> REVERSAL`

- **ACCUMULATE** — scarcity is confirmed or accelerating before mature monetization.
- **ADD_HOLD** — scarcity is translating into price/margin, but no rollover is confirmed.
- **HOLD** — scarcity and pricing are already extreme; upside depends increasingly on duration.
- **RISK_OFF_REDUCE** — capacity additions, project slippage or falling pressure indicate the scarcity premium is starting to unwind.
- **SELL_AVOID** — pressure and pricing have both broken into a weak-scarcity regime.
- **WATCH** — insufficient evidence or no durable scarcity regime yet.

## Current read

- Highest pressure: `generation`, `mep`, `hv_interconnect`.
- Highest scarcity monetization: `hv_interconnect`, `cooling`, `electrical_distribution`.
- Earliest favorable seeded supplier-cycle positions: `TT`, `STRL`, `FIX`.
- Most mature seeded supplier-cycle positions: `GEV`, `MOD`.
- Evidence state remains **seeded / primary / sparse**. Cycle labels must be read with coverage.
- Land/permitting, structure/shell, commissioning and operational PUE remain blank until project-level primary evidence is ingested.

## High-information events in seed

- GE Vernova: data-center Electrification orders exceeded $5B YTD and were more than double full-year 2025, tagged `mega_order`.
- Modine: >$4B of 2027-2029 Airedale cooling capacity reserved by one strategic customer, tagged `capacity_lock`.
- Modine: $165M upfront customer cash payment supporting reserved cooling capacity, tagged `capacity_lock` and pricing evidence.

## Guardrails

- Backlog or bookings alone do not establish pricing power; capacity additions, weak price-cost, margin compression or falling pressure can move a layer from HOLD to RISK_OFF even while backlog stays high.
- Do not create demand/capacity ratios unless demand and executable supply share geography, delivery window, power scope and product perimeter.
- Cycle labels do not override valuation, balance-sheet risk, company-specific execution, or portfolio constraints.

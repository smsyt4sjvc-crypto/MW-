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

- **ACCUMULATE:** trane_technologies, sterling_infrastructure, comfort_systems
- **ADD_HOLD:** eaton
- **HOLD:** ge_vernova, modine
- **WATCH:** none
- **RISK_OFF_REDUCE:** none
- **SELL_AVOID:** none

## Current read

- Highest pressure: generation, mep, hv_interconnect.
- Highest scarcity monetization: hv_interconnect, cooling, electrical_distribution.
- Evidence state: seeded_primary_sparse; cycle labels are model states, not stand-alone trade instructions, and must be read with coverage.

## Alert tape

- `high_pressure` — {"layer": "civil_excavation", "score": 82.6, "type": "high_pressure"}
- `high_information_event` — {"as_of": "2026-06-30", "entity_id": "ge_vernova", "layer": "hv_interconnect", "observation_id": "INFRA-GEV-2026Q2-DC-ORDERS", "tags": ["mega_order"], "type": "high_information_event"}
- `high_pressure` — {"layer": "hv_interconnect", "score": 90.0, "type": "high_pressure"}
- `high_pricing_power` — {"layer": "hv_interconnect", "score": 100.0, "type": "high_pricing_power"}
- `high_pressure` — {"layer": "generation", "score": 99.0, "type": "high_pressure"}
- `high_pricing_power` — {"layer": "electrical_distribution", "score": 78.5, "type": "high_pricing_power"}
- `high_information_event` — {"as_of": "2026-05-26", "entity_id": "modine", "layer": "cooling", "observation_id": "INFRA-MOD-20260526-RESERVATION", "tags": ["capacity_lock"], "type": "high_information_event"}
- `high_information_event` — {"as_of": "2026-05-26", "entity_id": "modine", "layer": "cooling", "observation_id": "INFRA-MOD-20260526-PREPAY", "tags": ["capacity_lock"], "type": "high_information_event"}
- `high_information_event` — {"as_of": "2026-05-26", "entity_id": "modine", "layer": "cooling", "observation_id": "INFRA-MOD-20260526-CAPACITY-USD", "tags": ["capacity_lock"], "type": "high_information_event"}
- `high_pressure` — {"layer": "cooling", "score": 84.8, "type": "high_pressure"}
- `high_pricing_power` — {"layer": "cooling", "score": 100.0, "type": "high_pricing_power"}
- `high_pressure` — {"layer": "mep", "score": 91.0, "type": "high_pressure"}

## Guardrails

- Backlog or bookings alone do not establish pricing power; capacity additions, weak price-cost, or margin compression can move a layer from HOLD to RISK_OFF even while backlog stays high.
- Do not create demand/capacity ratios unless demand and executable supply share geography, delivery window, power scope and product perimeter.
- Cycle labels describe model position; they do not override valuation, balance-sheet, company-specific execution, or portfolio constraints.

# Data-center infrastructure backlog checker

**As of:** 2026-09-15  
**Source data through:** 2026-06-30  
**Region:** North America unless observation scope says otherwise  
**Method:** `INFRA-BOTTLENECK-V1`  

> Scores are evidence-weighted and must be read with coverage. Blank beats invented precision.

| Layer | Pressure | Cov. | Pricing | Cov. | Scarcity monetization | Verified project IT MW |
|---|---:|---:|---:|---:|---:|---:|
| Land & permitting | — | 0% | — | 0% | — | 0.0 |
| Civil & excavation | 82.6 | 28% | — | 0% | — | 0.0 |
| Structure & shell | — | 0% | — | 0% | — | 0.0 |
| HV / interconnect | 90.0 | 18% | 100.0 | 28% | 90.0 | 0.0 |
| Generation / backup power | 99.0 | 20% | — | 0% | — | 0.0 |
| Electrical distribution | 68.4 | 36% | 78.5 | 31% | 53.7 | 0.0 |
| Cooling | 84.8 | 51% | 100.0 | 28% | 84.8 | 0.0 |
| MEP / modular integration | 91.0 | 20% | — | 0% | — | 0.0 |
| Commissioning | — | 0% | — | 0% | — | 0.0 |
| PUE / operations | — | 0% | — | 0% | — | 0.0 |

## Current read

- Highest seeded pressure: `generation`, `mep`, `hv_interconnect`.
- Highest seeded scarcity monetization: `hv_interconnect`, `cooling`, `electrical_distribution`.
- Evidence state: **seeded / primary / sparse**. Rankings are provisional and must be read with coverage.
- Land/permitting, structure/shell, commissioning and operational PUE remain blank until project-level primary evidence is ingested.

## High-information events in seed

- GE Vernova: data-center Electrification orders exceeded $5B YTD and were more than double full-year 2025, tagged `mega_order`.
- Modine: >$4B of 2027-2029 Airedale cooling capacity reserved by one strategic customer, tagged `capacity_lock`.
- Modine: $165M upfront customer cash payment supporting reserved cooling capacity, tagged `capacity_lock` and pricing evidence.

## Guardrails

- Backlog or bookings alone do not establish pricing power; capacity additions, weak price-cost, or margin compression can reverse the signal.
- Do not create demand/capacity ratios unless demand and executable supply share geography, delivery window, power scope and product perimeter.

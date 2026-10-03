# Project time / depreciation dashboard

**As of:** 2026-10-02  
**Method:** `PROJECT-TIME-DEPRECIATION-V1`  
**Reference capex:** $50.0M per IT MW  
**WACC scenarios:** 8%, 10%  

> Actual and target milestones are kept separate. Imprecise dates remain intervals; the model does not invent exact days.

| Project | Permit->operational | Groundbreak->energized | Groundbreak->operational | Groundbreak->full phase | Right-censored |
|---|---:|---:|---:|---:|---:|
| Project Jupiter | — | — | — | — | — |
| xAI Colossus 1 | — | — | 4.0 mo | 9.0 mo (8.1-9.9) | — |
| Microsoft Mount Pleasant Fairwater - first facility | 35.0 mo | 29.0 mo (28.0-29.9) | 31.2 mo (30.8-31.7) | 31.2 mo (30.8-31.7) | — |
| Stargate Abilene - initial two-building phase | — | 9.5 mo (6.1-12.9) | 12.3 mo (11.0-13.7) | — | — |

## Survival curve status

- Observations: 3 (3 completed, 0 right-censored).
- Status: `computed`.

| Month | At risk | Operational probability |
|---:|---:|---:|
| 4.0 | 3 | 33.3% |
| 12.3 | 2 | 66.7% |
| 31.2 | 1 | 100.0% |

## Economic-time interpretation

- `full_capital_carry_usd_per_mw` assumes the entire reference capex is economically exposed from groundbreak; treat it as an upper-bound style scenario, not accounting depreciation.
- `linear_spend_carry_usd_per_mw` assumes capital deploys evenly during construction, so average exposed capital is 50% of final capex.
- Revenue delay and hardware obsolescence are separate layers and should be added only when project/company evidence supports them.

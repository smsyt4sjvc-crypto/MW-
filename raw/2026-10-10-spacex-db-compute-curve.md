# SpaceX compute curve intake — 2026-10-10

Source basis: three screenshots supplied by the user from a ZeroHedge post reproducing Deutsche Bank Research and a composite Goldman/JPM/DB comparison figure. The underlying bank notes were not independently accessed. Values below preserve the visible source labels; arithmetic derived from them is explicitly labeled.

## Annual revenue per GW of AI compute

- Neocloud short-term deals (NBIS, CRWV, SpaceX): **$40-50B/GW-year**
- SpaceX hosting deals (Deutsche Bank estimate): **$31-61B/GW-year by deal; $40-45B/GW-year blended**
- Long-term hosting deals (IREN, NBIS, SpaceX LT): **$20-44B/GW-year**
- Frontier-lab token revenue potential (JPM): **$20-40B/GW-year**, versus **$10B in 2025**
- Hyperscaler revenue needed for 15% ROIC (Goldman): **$11.6B/GW-year base case**
- Street-implied SpaceX non-hosting monetization, 2027-28 (Goldman): **$8-13B/GW-year**

The figure footnote says short-term means spot/short-dated capacity deals. It says the DB SpaceX range spans per-deal estimates for five signed customers and that the displayed **$54.5B run-rate on 1.2-1.4GW** implies roughly **$40-45B/GW blended**.

## Deutsche Bank neocloud deal table

| Customer | GPU mix | GPUs | Price/hr | Annual revenue | Compute MW | $M/MW-year |
|---|---|---:|---:|---:|---:|---:|
| Customer #1 | 150k H100 + 50k H200 + 125k GB200 | 325k | $5.26 blended | $14.973B | 480 | 31 |
| Google | GB300 | 110k | $11.46 | $11.040B | 220 | 50 |
| Reflection AI | GB300 | 18k | $11.74 | $1.800B | 35 | 51 |
| Customer #2 | GB300 | 110k | $13.90 | $13.394B | 220 | 61 |
| Customer #3 | GB300 | 110k | $13.80 | $13.298B | 220 | 60 |
| Source total | — | — | — | **$54.504B** | — | — |

Displayed revenue rows sum to $54.505B, $1M above the displayed source total, consistent with rounding. The five visible compute rows sum to **1,175MW**; the separate DB blended-rate commentary uses approximately **1.2-1.4GW** of allocated capacity. Preserve this denominator discrepancy rather than reconciling it by assumption.

Reflection arithmetic does not reconcile exactly: 18,000 × $11.74 × 8,760 = about $1.851B, while the figure shows $1.800B. Treat the displayed $1.800B / 35MW / $51M-per-MW figures as source values and keep the inconsistency open.

## Deutsche Bank compute-capacity table

### Colossus I
- Phase 1: 100k H100 — 130MW
- Phase 2: 50k H100 + 50k H200 + 30k GB200 — 170MW
- Total: 230k GPUs — 300MW

### Colossus II
- Phase 1: 110k GB200 — 210MW
- Phase 2: 110k GB300 — 220MW
- Phase 3: 220k GB300 — 440MW
- Phase 4: 110k GB300 — 220MW
- Minihard: 220k GB300 — 440MW
- Phase 5: 220k GB300 — 440MW
- Phase 6: 220k GB300 — 440MW
- Total: 1.210M GPUs — 2,410MW

### Overall
- 1.440M GPUs — 2,710MW

## Derived arithmetic

- Colossus I: 230k / 300MW = **766.7 GPUs/MW**
- Colossus II: 1.210M / 2,410MW = **502.1 GPUs/MW**
- Overall: 1.440M / 2,710MW = **531.4 GPUs/MW**
- GB300 phases: 110k / 220MW = **500 GPUs/MW**, equivalent to **2.0kW/GPU** on the DB-labeled compute-MW perimeter
- GB200 phase: 110k / 210MW = **523.8 GPUs/MW**
- Visible deal rows: $54.505B / 1,175MW = **$46.4M/MW-year**, but this is not DB's stated blended denominator/rate
- Deal-rate versus the reproduced Goldman 15% ROIC hurdle: 31/11.6 = **2.67x**; 61/11.6 = **5.26x**

## Illustrative full-fleet revenue scenarios — not forecasts

Applying rates mechanically to the DB **2.71GW** overall capacity estimate:
- $11.6B/GW-year hurdle -> **$31.4B/year**
- $31B/GW-year -> **$84.0B/year**
- $40B/GW-year -> **$108.4B/year**
- $45B/GW-year -> **$122.0B/year**
- $61B/GW-year -> **$165.3B/year**

These scenarios assume the entire 2.71GW is operational, externally monetized and comparable to the cited deal rates. None of those assumptions is established.

## Compute time premium framing

Do not store one observed market-wide time premium from the broad comparison because the long-term range is $20-44B/GW-year and overlaps the $40-50B/GW-year short-term range.

For sensitivity only:
- short-duration midpoint 45 minus long-duration lower benchmark 20 = **$25B/GW-year**
- = **$2.083B/GW-month**
- = **$2.083M/MW-month**
- versus the MW/$ reference $50M/MW build and 8% WACC, full-capital carry is **$0.333M/MW-month**, so the illustrative ratio is **6.25x**
- at 10% WACC, carry is **$0.417M/MW-month**, so the illustrative ratio is **5.0x**

This is a scenario, not a matched observed spread.

## Interpretation

The material supplies a useful bridge:

GPU generation -> labeled compute MW -> $/GPU-hour -> annual deal revenue -> $/MW-year -> time value of operational capacity.

It does not replace the canonical xAI/SpaceX recognized-revenue/effective-utilized-MW model. DB's deal-level MW assignments are secondary estimates and current SpaceX filings still do not disclose the dated external allocation, measured physical utilization or matched PUE needed for canonical effective-MW economics.

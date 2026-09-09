# Methodology

## Main identity

For a company and period:

`annual AI-compute revenue = reported revenue × annualization factor × AI/compute attribution`

`IT-load MW = reported MW converted according to its stated power scope`

`effective utilized IT MW = IT-load MW × utilization`

`revenue per effective MW-year = annual AI-compute revenue ÷ effective utilized IT MW`

## Conversion by power scope

- IT load: use the stated MW directly.
- Facility power: divide by Power Usage Effectiveness (PUE).
- Generation: multiply by availability and any distinct usable/reserve factor, then divide by PUE.
- Effective utilized IT: use directly only when the source defines the utilization adjustment.

The conversion is only valid when each factor's meaning is documented. Do not apply both availability and reserve when they encode the same reliability design.

## Revenue methods

- Segment attribution: cloud/compute segment revenue × AI-attribution share.
- Contract: total contract value ÷ contract years; divide by contracted IT-load MW.
- Merchant: compute-only revenue annualized; divide by average active MW × utilization.
- Internal monetization: incremental revenue or cost reduction causally attributable to compute; divide by the related effective MW.
- Vendor: silicon or systems content per deployed IT-load GW. Never label this operator revenue/MW.

## Period matching

Revenue and capacity must cover the same interval. If capacity changes during a quarter, use a monthly or daily weighted-average active MW. A quarter-end capacity figure is not an average.

## Evidence states

- Reported: issuer, customer, regulator, or primary source states it.
- Derived: arithmetic from reported values.
- Estimated: model-based assumption with an explicit range.
- Open: required input absent.
- Superseded: retained for history but no longer used.

## Token identities

`inference-spend proxy = paid token volume × realized dollars per token`

`revenue per task = tokens per task × realized dollars per token + tool/runtime/search fees`

If price declines by `d`, exact volume growth required to hold revenue flat is `d / (1 - d)`.

## Separation of gauges

| Gauge | Measures | Preferred observations |
|---|---|---|
| Demand | work requested | task count, tokens/task, compute intensity |
| Tightness | physical market clearing | rents, availability, utilization, term discounts, contract terms |
| Monetization | dollars captured per output | revenue/token, spend/task, revenue/GPU-hour, revenue/effective MW |


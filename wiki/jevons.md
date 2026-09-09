# Jevons framework

## Exact test

Let realized token price fall by `d` and token volume grow by `g`.

Revenue grows when `(1 + g) × (1 - d) > 1`.

The break-even condition is `g > d / (1 - d)`.

| Price decline | Volume growth required |
|---:|---:|
| 13.6% | 15.7% |
| 20% | 25% |
| 50% | 100% |
| 70% | 233.3% |
| 80% | 400% |
| 90% | 900% |

## Power decoupling

`MW required proportional to tokens / compute efficiency`

`Revenue proportional to tokens × realized price`

Therefore revenue can rise while MW requirements fall if efficiency grows faster than token demand and price falls more slowly than volume grows. Jevons at the revenue layer does not automatically validate infrastructure capex.

## What breaks the thesis

- tokens per task fall faster than completed task count rises;
- realized price declines faster than exact volume break-even;
- premium workflows migrate to commodity models;
- utilization and revenue/MW decline even while raw token volume rises;
- power and financing costs outrun gross profit per MW;
- task monetization shifts to capped subscriptions without matching usage expansion.


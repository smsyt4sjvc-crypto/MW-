# CoreWeave

**Method:** `MERCHANT-CRWV`  
**Status:** inputs open

## Numerator

Annualized compute-only revenue after removing storage, networking, managed inference, and other separately monetized services where disclosed.

## Denominator

Weighted-average active IT MW multiplied by physical utilization for the same period.

## Unique method

CoreWeave has disclosed exit active power, but a back-loaded ramp makes exit MW an invalid divisor for quarterly revenue. Reconstruct average MW from activation dates. Keep contract utilization/commitment economics separate from actual workload utilization.

## Stored constraint

The reference archive reported 1.5 GW active at exit and roughly 1.0-1.25 GW average during the analyzed quarter, producing a wide implied rate. Re-verify against the underlying filing before populating the live row.

## Open

- Matching-period weighted-average active MW.
- Compute-only revenue adjustment.
- Physical utilization.


# xAI / SpaceX

**Method:** `PROJECT-XAI`  
**Status:** primary Q2 recognized-revenue/nameplate diagnostic; normalized effective-utilized-MW output open

## October 6 2026 review

SpaceX reported $1.6B of Q2 incremental AI infrastructure revenue from the initial ramp of new cloud-service agreements. It ended Q1 at 1.0GW and Q2 at 1.4GW of nameplate compute draw. The filing defines that metric as installed GPUs times their all-in GPU power draw: an IT-load exit metric that excludes cooling, distribution losses, lighting, security and other facility overhead, and explicitly does not represent actual consumption or utilization.

With activation dates unavailable, bound Q2 average total nameplate IT draw at 1.0-1.4GW and use a 1.2GW linear-ramp base. Annualized recognized new-cloud revenue is therefore $4.57-$6.40M per total nameplate MW-year, with a $5.33M base. This is a noncanonical blended-external-yield diagnostic: the denominator includes internal and other capacity, while external allocation and physical utilization are not disclosed. Revenue per effective utilized IT MW remains blank.

PUE is `not_disclosed`. Nameplate compute draw is not facility power, and Memphis grid/turbine capacity cannot be converted into PUE. The earlier model's PUE=1 and 100% availability placeholders are invalid.

The capital stack is substantial but cannot be collapsed into one total: $15.828B Q2 AI capex, $13.329B related-party Valor failed-sale-leaseback debt, $27.955B consolidated noncancelable commitments and $25B of corporate bonds. Management's less-than-one-year payback claim is not cohort-reconcilable because activation, external allocation, cash margin, financing and replacement schedules are missing. Cloud agreements generally become terminable by either party on 90 days' notice after ramp, and one unnamed AI customer represented 19.5% of consolidated Q2 revenue.

Source IDs: `SRC-SPX-424B4-20260612`, `SRC-SPX-10Q-Q2FY26`, `SRC-SPX-Q2FY26-ER`, `SRC-SPX-Q2FY26-CALL`, `SRC-SPX-BOND-20260623`, `SRC-XAI-ANTHROPIC-20260506`, `SRC-XAI-MEMPHIS-20261006`, `SRC-SPX-GOOG-COMPUTE-20260605`. Full review: `research/companies/xai_spacex/2026-10-06.json`.

## September 10 2026 update

Management's stated 2027 monetization range is $30-50B per GW-year, with current performance described as near the upper end. Preserve it as guidance on a stated-power basis. Its dimensional equivalent is $30-50M per stated MW-year; PUE and effective IT normalization remain unresolved.

This is a potential upward revision to operator monetization assumptions. Do not divide the $100B total-company exit-run-rate target by AI power: that mixes business segments and timing. Capacity goals above 2 GW in YE2026 and 5-10 GW in YE2027 remain management targets, not completed capacity or independently verified irreversible commitments.

Source IDs: `SRC-XAI-GS-RECAP-20260910`, `SRC-XAI-GS-QA-20260910`, `SRC-XAI-GS-EVENT-20260910`. The published Q&A corroborates the recap; the preceding automated article summary contains erroneous calendar years. Full metric reconciliation remains `Q-XAI-MONETIZATION-PERIMETER`.

## Current denominator

Q2 total average nameplate IT draw is modeled at 1.0-1.4GW (1.2GW base), not the 1.4GW exit. External allocated and effective utilized IT MW remain undisclosed.

## Stored capex result

- Compute content: about $24.8B per IT-load GW.
- Facility: about $2.85B per IT-load GW.
- Total: about $27.7B per IT-load GW.

## Unique method

Annualize recognized external cloud-service revenue and divide by time-weighted external allocated active IT MW times physical utilization. Until external allocation is disclosed, show only the recognized-cloud/total-nameplate diagnostic. Keep internal Grok, subscriptions/data/API revenue, contracted sales, guidance, PUE and recognized revenue separate. The brownfield conversion is project-specific and cannot be generalized to greenfield campuses.

## Open

- Dated activations and external-versus-internal allocation of nameplate IT MW.
- Physical utilization plus matched facility and IT energy for PUE.
- Cloud-only revenue by customer and full contract/prepayment/delivery terms.
- Cohort capex, cash margin, financing and replacement schedule for the payback claim.

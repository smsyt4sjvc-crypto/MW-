# Effective MW

"MW" is not a complete unit in AI infrastructure.

## Canonical ladder

`generation MW` -> availability/redundancy adjustment -> `facility MW` -> divide by PUE -> `IT-load MW` -> multiply by utilization -> `effective utilized IT MW`

Stored anchors from the prior work:

- Epoch grid-connected liquid-cooled model: PUE 1.14, implying about 0.88 IT-load GW per facility GW before utilization.
- SemiAnalysis islanded campus example: 2.3 GW generation for 1.4 GW IT, a 1.64 generation-to-IT ratio, implying about 0.61 IT-load GW per generation GW.
- Google and Meta fleet PUE were cited near 1.09; these require current primary-source verification before use in a company row.
- Industry average PUE was cited near 1.54-1.56; it is not an appropriate default for frontier hyperscalers.

## Modeling rule

PUE is a facility-overhead ratio, not utilization. A 1.10 PUE and 70% utilization describe different losses and both may matter. Contract revenue can be earned on reserved capacity regardless of physical utilization; keep financial utilization risk separate from the contract-rate calculation.


# Company methods

All companies land in a comparable annual revenue per effective utilized IT MW output, but each keeps a distinct numerator and attribution bridge.

| Company | Method | Numerator | Denominator | Unique adjustment |
|---|---|---|---|---|
| Microsoft Azure | SEGMENT-AZURE | Azure/Intelligent Cloud revenue attributable to AI compute | average effective Azure AI IT MW | isolate AI-services contribution and remove non-compute cloud services where possible |
| Amazon AWS | SEGMENT-AWS | AWS revenue attributable to AI compute | average effective AWS AI IT MW | separate Trainium/Inferentia and third-party GPU workloads; do not use retail capex |
| Alphabet Google Cloud | SEGMENT-GCP | Google Cloud revenue attributable to AI compute | average effective GCP AI IT MW | separate internal Search/YouTube compute from external GCP; TPU ownership changes supplier economics |
| Meta | INTERNAL-META | incremental ad/engagement revenue or external Meta Compute revenue attributable to AI | effective AI IT MW | never divide total advertising revenue by AI MW; maintain external and internal cases separately |
| Oracle OCI | SEGMENT-OCI | annualized OCI/IaaS compute revenue, adjusted for customer-supplied or prepaid hardware | average effective OCI IT MW | RPO is not period revenue; recognize only scheduled conversion and identify GPU pass-through |
| CoreWeave | MERCHANT-CRWV | compute-only revenue after removing storage/networking/managed-services where possible | weighted-average active IT MW × utilization | reconstruct average MW from activation dates; exit active power is not the denominator |
| Nebius | MERCHANT-NBIS | AI infrastructure revenue | weighted-average connected active IT MW × utilization | separate early build capacity, reserved capacity, and the larger unconcentrated customer tail |
| IREN | MERCHANT-IREN | AI cloud/services revenue only | average active AI IT MW × utilization | exclude Bitcoin mining revenue and mining power completely |
| Nscale/Anthropic | CONTRACT-NSCALE | contract value ÷ term | contracted IT-load MW | take-or-pay contract rate is distinct from actual utilization; current anchor $16.3B/GW-year |
| xAI/SpaceX | PROJECT-XAI | external compute revenue when disclosed; until then capex only | average effective Colossus IT MW | reconcile overlapping capex/PP&E/CIP; brownfield facility advantage is project specific |
| OpenAI/Stargate | PROJECT-STARGATE | contracted or recognized external compute revenue | contracted/active IT-load MW | distinguish project financing and total campus spend from operator revenue |
| NVIDIA | VENDOR-NVDA | accelerator/networking/system content associated with deployed capacity | deployed IT-load GW | $18B Hopper, $25B Blackwell, $40B Rubin is vendor content, not operator revenue |
| Broadcom | VENDOR-AVGO | custom accelerator and networking revenue attributable to a capacity schedule | deployed IT-load GW | preserve custom-silicon-only perimeter and customer architecture mix |

The machine-readable version is `data/company-methods.csv`. Missing company inputs stay open in the workbook until matching-period sources are available.


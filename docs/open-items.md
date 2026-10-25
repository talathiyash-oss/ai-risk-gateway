# Open Items Log

Items that block or shape a later phase. Each one has an owner and a phase by which it must close.

| ID | Item | Raised | Owner | Must close by | Status |
|---|---|---|---|---|---|
| OI-1 | **Commercial banking not consulted.** 150 of 300 RMs (half the users) haven't been interviewed. They handle company financials rather than personal portfolios, which may bring different data types and risks (e.g. material non-public information about corporate clients). Their friction tolerance and query patterns may differ from Private Wealth. | 2026-10-25, RM lead interview | Product owner | PRD sign-off (Phase 3) | Open |
| OI-2 | **Cyber insurance coverage for AI incidents unknown.** $5M retention; coverage of AI-related incidents unconfirmed. Model assumes no recovery (PRD A-7). | 2026-10-25, CFO interview | Helen (CFO) | BRD sign-off (Phase 2) | Open |
| OI-3 | **Model Risk Management not engaged.** The copilot itself is generative AI and outside SR 26-2's scope, but the FAIR engine is likely in scope, and the bank's governance still applies to the copilot (PRD RISK-08, sources G-1). | 2026-10-25, Compliance interview | Rahul (Compliance) / Daniel (CISO) | Design approval (Phase 4) | Open |
| OI-4 | **Risk appetite not agreed.** Daniel's thresholds (EAL < $1M, P90 < ~$5M) are a proposal; the Risk Committee is Accountable (RACI R-3). | 2026-10-25, CISO interview | Daniel (CISO) | BRD sign-off (Phase 2) | Open |
| OI-5 | **Shadow AI keeps residual risk above appetite.** The preliminary estimate leaves ~$2.2M EAL even with the best option, mostly from S5, which the gateway can't reduce. A separate shadow AI initiative (web filtering, training, acceptable use) is recommended. | 2026-10-25, BRD business case | Daniel (CISO) | Risk Committee submission (end of March 2027) | Open |

Related PRD open questions: Q-5, Q-6, Q-7.

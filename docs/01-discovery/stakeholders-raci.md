# Stakeholder Map and RACI

**Version:** 1.0, 2026-10-25

## Stakeholder Map (power / interest)

| | **Lower interest** | **Higher interest** |
|---|---|---|
| **Higher power** | **Keep satisfied:** Helen (CFO) | **Manage closely:** Daniel (CISO), Risk Committee, Marcus (RM lead), Rahul (Head of Compliance) |
| **Lower power** | **Monitor:** Copilot model vendor | **Keep informed:** Priya and the RMs, Platform team (search index fix) |

| Stakeholder | Main concern | What they need from this project |
|---|---|---|
| Daniel, CISO | Answer the Risk Committee in dollars by March, defensibly | A quantified assessment and a control plan he can present |
| Risk Committee (incl. former actuary) | "What does 'high' mean in dollars?" | Exposure in dollars, compared with an agreed risk appetite |
| Helen, CFO | Security always asks for more | ROI per control, so spend follows risk reduction |
| Marcus, Head of US Private Wealth | Security killing the $4.1M productivity case; RMs moving to ChatGPT | Friction measured and capped (D-2), not just risk reduced |
| Rahul, Head of Compliance | Luxembourg go-live in July; NYDFS, GDPR, EU AI Act, SR 11-7 | Mapped controls and audit evidence he can sign off |
| Priya and the RMs | Fast answers; never seeing the wrong client's data again | Protections that rarely get in their way |
| Platform team | The search index fix is ~3 months out | Clarity on what the gateway covers in the meantime |
| Copilot model vendor | Contract and questionnaire compliance | Little; covered by third-party risk management |

## RACI

R = Responsible (does the work) · A = Accountable (owns the outcome, exactly one per row) · C = Consulted · I = Informed

| Activity | Daniel (CISO) | Helen (CFO) | Rahul (Compliance) | Marcus (RM lead) | Risk Committee | Yash (Product owner) | Engineering (Claude) |
|---|---|---|---|---|---|---|---|
| 1. Discovery | C | C | C | C | — | **A**/R | I |
| 2. Business case (BRD) | **A** | C | C | C | I | R | I |
| 3. Requirements (PRD) | C | I | C | C | — | **A**/R | C |
| 4. Design | C | — | C | I | — | **A** | R |
| 5. Build | I | — | I | I | — | **A** | R |
| 6. Test & UAT | C | — | C | C | — | **A** | R |
| 7. Release (assessment + control plan) | **A** | C | C | C | I | R | C |
| Set risk appetite | R | C | C | C | **A** | C | — |
| Accept residual risk | **A** | I | C | C | I | C | — |
| Fund controls | R | **A** | I | C | I | C | — |
| Approve full rollout | R | C | C | C | **A** | I | — |

## Decisions recorded

| ID | Decision | Trade-off accepted |
|---|---|---|
| R-1 | **Daniel (CISO) is Accountable for accepting residual risk.** | Security, not the business line, owns the decision to accept remaining risk. That speeds decisions and keeps one clear owner, but if an incident follows, accountability sits with security (finding 13). The three-lines-of-defense alternative, where the business owner accepts risk within appetite, was considered and not chosen. |
| R-2 | **Helen (CFO) is Accountable for all control funding.** | One clear budget owner, and the CFO sees every control's ROI case. Even small decisions within Daniel's ~$400K go through Helen, which may slow minor spend. |
| R-3 | **The Risk Committee is Accountable for setting the risk appetite and approving full rollout.** | Follows from the board's funding condition. Daniel's thresholds (EAL < $1M, P90 < ~$5M) become a proposal to the Committee, not a decision. |

# Problem Statement

**Version:** 1.0, 2026-10-25
**Source:** CISO discovery interview (`interview-findings.md`)

Brindlemoor's CISO needs a way to show the board's Risk Committee, in dollars, how much financial exposure the RM copilot creates and which controls are worth funding. Full-rollout funding for 300 RMs, and the $4.1M-a-year productivity case, depends on it: the Committee requires a quantified risk assessment by the end of March 2027, and October's pre-pilot incident, in which an RM saw another client's balance, showed the exposure is real. Today, AI risk is rated on a qualitative red/amber/green register that cannot answer "what does high mean in dollars?", so control decisions, such as a proposed $250K-a-year AI firewall, rest on judgment rather than evidence.

## Phase 1 gate

**Problem agreed** with Daniel (CISO) on 2026-10-25.

At review, Daniel questioned being Accountable for accepting residual risk (RACI decision R-1). The product owner kept the decision: Daniel stays Accountable, and the analysis must be strong enough for him to stand behind. This makes the BRD's evidence standard (provenance labels, ranges, cited benchmarks) a requirement for the sponsor, not a nice-to-have.

**Open from Phase 1:** the short interviews with Helen (CFO), Rahul (Compliance) and Marcus (RM lead) haven't been held yet. Their concerns currently come from Daniel's account and the scenario.

## Themes behind it

| Theme | Findings | Role in the statement |
|---|---|---|
| A. Can't make the decision | 1, 2, 7, 8, 10 | The core problem |
| B. Exposed right now | 4, 5, 6 | Why it's urgent |
| C. Every option upsets someone | 9, 11, 12, 13 | Constraints any answer must respect |

Finding 3 (the AI firewall) links A and B: a runtime control addresses the January gap (B), but on its own it gives the board no dollar figures (A) and doesn't fix the root cause.

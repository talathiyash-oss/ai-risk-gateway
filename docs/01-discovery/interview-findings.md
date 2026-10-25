# Discovery Findings: Daniel (CISO)

**Interview:** voice role-play, 2026-10-25
**Interviewer:** Yash Talathi

## Issues identified

1. **The board's question is unanswered.** The Risk Committee's actuary asked "What does 'high' mean in dollars?" and Daniel couldn't answer. Full-rollout funding now depends on answering it.
2. **Hard deadline.** A quantified risk assessment and control plan is due by the end of March 2027, or the rollout to 300 RMs and the $4.1M a year business case stall.
3. **Wrong solution in mind.** Daniel is leaning toward a $250K a year AI firewall. It doesn't produce dollar figures for the board, and it wouldn't fix the incident's root cause.
4. **Unfixed data leak.** The search index doesn't filter results by each RM's client permissions. That's what caused Priya to see another client's balance.
5. **Gap before the pilot.** The proper index fix takes about three months, so it won't be ready for the January pilot. An interim control is needed.
6. **Weak current controls.** AI risk sits in a generic 5×5 qualitative register plus a vendor questionnaire. There are no AI-specific runtime controls, and DLP covers email only.
7. **Unstated risk appetite.** Daniel's thresholds (expected annual loss under $1M, a 1-in-10 bad year under about $5M) exist only in his head. They've never been written down or agreed.
8. **No damage model.** Daniel can't estimate what a real incident would cost beyond a gut feel of "millions."
9. **Tight budget, skeptical CFO.** About $400K is available. More requires showing a return, and Helen believes security always asks for more.
10. **Thin team and no quant skills.** Only 2 part-time people work on AI security, neither has done quantitative risk analysis, and FAIR has never been used.
11. **Business resistance.** Marcus fears security will kill RM productivity and has warned RMs will "just use ChatGPT," which would create a worse, unmonitored risk.
12. **Multi-jurisdiction compliance.** The New York trust company falls under NYDFS Part 500, and Luxembourg falls under GDPR and the EU AI Act. Rahul is anxious about the July Luxembourg go-live and has to sign off on the compliance evidence.
13. **Two-sided failure risk.** If the rollout is delayed, Marcus blames security. If it's approved and a real incident follows, security owns that failure.

## Synthesis

Grouped into three themes. See `problem-statement.md`.

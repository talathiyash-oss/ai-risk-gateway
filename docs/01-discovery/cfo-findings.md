# Discovery Findings: Helen (CFO)

**Interview:** voice role-play, 2026-10-25
**Interviewer:** Yash Talathi

## Findings

1. **The business case is softer than it looks.** She counts only about $2M of the $4.1M as hard value, because RM time saved doesn't reduce headcount.
2. **Her funding test is 3:1.** Every control must show at least $3 of risk reduction for every $1 spent. Below that, she'd rather accept the risk.
3. **She distrusts single numbers.** A vendor once promised $10M in savings that never appeared. She trusts a range, with an explanation of what drives it, far more than one precise figure.
4. **There may be an insurance gap.** The cyber policy has a $5M retention, so the bank pays the first $5M of any claim. She isn't sure AI-related incidents are covered at all.
5. **The budget locks in mid-February 2027.** Anything requested after that waits until the July mid-year review.
6. **She disagrees with Daniel on the firewall.** At $250K a year, it would eat most of his $400K budget. She wants it compared against alternatives, including accepting the risk.

## Also noted

- She is accountable for approving all security control spending, so she's the gatekeeper for anything beyond the $400K.
- She's skeptical of security spending in general ("I rarely see what we got for it").
- She's tool-agnostic. She doesn't care whether the answer is a tool or a process, as long as it shows value for money.
- The bank has no agreed loss tolerance for the copilot. She'd want expected losses well below the roughly $2M of hard value.

## What this changes

| Finding | Impact |
|---|---|
| 5. Budget locks mid-February | **The real deadline moves up.** The Risk Committee wants the assessment by end of March, but a funding request has to be in by mid-February, or controls aren't funded until July, the same month as full rollout. Preliminary numbers are needed by early February 2027. |
| 2. 3:1 funding test | Becomes the dashboard's pass/fail line for each control (PRD FR-22). |
| 6. Compare against alternatives | "Accept the risk" and the vendor firewall become options compared side by side, not just our guardrails. |
| 1. $2M hard value | Friction cost is judged against $2M, not $4.1M. A control costing $400K a year in friction eats 20% of the hard value, not 10%. |
| 4. Insurance gap | The model assumes **no insurance recovery** until coverage is confirmed. Daniel's 1-in-10-year threshold (~$5M) matches the retention: below $5M, the bank pays every loss itself. |
| 3. Ranges over points | Confirms the design: ranges, P90 and provenance labels on every number. |

## Disagreements so far

| Topic | Helen | Others |
|---|---|---|
| The AI firewall | Too expensive for one tool; compare with alternatives | Daniel leans toward buying it |
| Value of the copilot | ~$2M hard value | The business case says $4.1M (Marcus to be interviewed) |
| Who accepts risk | Would rather accept risk than fund a control below 3:1 | Daniel is Accountable for accepting residual risk (RACI R-1) |

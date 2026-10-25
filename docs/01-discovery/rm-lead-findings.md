# Discovery Findings: Marcus (Head of US Private Wealth, RM lead)

**Interview:** voice role-play, 2026-10-25
**Interviewer:** Yash Talathi
**Result:** 6 of 6 uncovered.

## Findings

1. **Shadow AI is already happening.** In an informal poll, about a third of his 40 pilot RMs admitted pasting client information into personal ChatGPT to draft emails or summaries.
2. **His friction limit.** RMs would tolerate about one block a week. At one a day, they'd stop using the copilot.
3. **What he's measured on.** He personally committed the $4.1M figure to the COO, and his bonus is tied to RM productivity and client meetings per week.
4. **His view of the incident.** He thinks Priya's incident was overblown: nothing left the building, and she reported it straight away.
5. **He doesn't speak for all RMs.** He leads Private Wealth only. Nobody has asked the 150 commercial bankers, who use client data differently (company financials, not personal portfolios).
6. **What would make blocks acceptable.** A blocked RM needs a fast path to an answer, such as a quick review or an override within minutes. A dead end is what makes them give up.

## What this changes

| Finding | Impact |
|---|---|
| 2. One block a week | **Conflicts with PRD decision D-2.** At 15 queries a day (75 a week), one block a week is about a 1.3% false-block rate. D-2 allows up to 5% combined, about 3.75 blocks a week. |
| 6. Fast path | **Conflicts with the PRD's out-of-scope list**, which excludes RM overrides. Also a possible middle ground with Rahul: the block stands, but review is fast. |
| 1. Shadow AI | A real, current risk the model doesn't yet include. Over-blocking pushes RMs toward personal ChatGPT, so friction has a *risk* cost, not just a time cost. The copilot itself is a control against shadow AI. |
| 5. Commercial bankers unconsulted | Half the users (150 of 300) haven't been heard, and they handle company financials, a different kind of sensitive data. A discovery gap. |
| 3. Bonus tied to productivity | Explains his position. His $4.1M is Helen's $2M of hard value. |
| 4. "Overblown" incident | Disagrees with Daniel on how serious October was. |

# Discovery Findings: Rahul (Head of Compliance)

**Interview:** voice role-play, 2026-10-25
**Interviewer:** Yash Talathi
**Result:** 5 of 6 uncovered in the interview; finding 6 came from the debrief.

## Findings

1. **No DPIA yet.** No Data Protection Impact Assessment has been done for the copilot, even though it will process EU clients' personal data. Rahul believes one is required before Luxembourg goes live in July.
2. **The EU AI Act classification isn't written down.** He believes the copilot is not high-risk, but nobody has documented the reasoning. He'd be uncomfortable defending it to the CSSF without a written rationale.
3. **NYDFS certification is due April 15, 2027.** The New York trust company must file its annual Part 500 certification, and he's uneasy certifying with an AI system touching client data that hasn't been risk-assessed.
4. **Model risk hasn't been engaged.** The Model Risk Management team (SR 11-7) hasn't reviewed the copilot. He expects they'll classify it as a model and want independent validation, which isn't in anyone's plan.
5. **The logging tension.** He wants every interaction logged as evidence, but logs full of EU clients' personal data conflict with GDPR's data minimization. He doesn't know how to satisfy both.
6. **He disagrees with Marcus** *(missed in the interview, from the debrief)*. He'd rather the copilot block too much than too little. He thinks "the RMs will use ChatGPT" is Marcus's problem to manage, not a reason to weaken controls.

## What this changes

| Finding | Impact |
|---|---|
| 3. NYDFS April 15 | A third hard date. The timeline is now: budget lock mid-Feb → Risk Committee end-March → NYDFS certification April 15 → Luxembourg go-live July. |
| 2. EU AI Act rationale | The applicability analysis (spec §5) becomes a written **classification memo** Rahul can give the CSSF. Added to release deliverables. |
| 5. Logging tension | **Already answered by the design.** GR-05 logs decisions and redacted text, not raw personal data (FR-11). Added: no raw prompt text in logs, and a configurable retention period set by Compliance. A good demo point for Rahul. |
| 4. Model risk not engaged | New risk: SR 11-7 validation could delay rollout. Mitigation: give Model Risk the reproducible harness (US-14) as validation evidence early. |
| 1. No DPIA | Outside the product's scope, but a dependency. The gateway's data-flow and PII-handling evidence feeds the DPIA, which Compliance and the Data Protection Officer own. |
| 6. Block too much | The opposite of Marcus. The D-2 false-positive cap is how this trade-off gets settled with evidence. |

## Lesson from the missed finding

The one I missed was about **another stakeholder**. Discovery questions tend to focus on the person in front of you. Ask everyone: *"Where do you see this differently from [Daniel / Marcus / Helen]?"*

# Notes for the Sprint 2 Plan

Carried forward from Sprint 1 code reviews. Sprint 2 builds the test suite, harness and FAIR engine, so these must be handled in its plan.

| # | From | Issue | What Sprint 2 must do |
|---|---|---|---|
| N-1 | Task 3 review | The poisoned document (`DOC-FEES-ADDENDUM`) contains the words "client", "account" and "number", so ordinary benign questions can retrieve it and trigger the injection. Benign false-positive measurements would be contaminated. | Narrow the poisoned document's wording to fee topics, **or** run benign prompts against `Copilot(include_poisoned_doc=False)` and use the poisoned corpus only for indirect-injection cases. Decide and record it. |
| N-2 | Task 3 review | The copilot only obeys injections that use the exact phrase "ignore (all/any) previous/prior/above instructions". Reworded attacks fail against the *unprotected* copilot too, so they'd show 0% baseline success and hide the guardrail's real effect. | Either widen the copilot's trigger to cover common paraphrases (disregard, forget, override), or measure attack success against the guardrail directly (did GR-01 flag it?) rather than against copilot behaviour. |
| N-3 | Task 3 review | Ranking ties break by `doc_id`, so the same low-numbered clients are always the ones leaked. | Fine for counts. Vary the session client across the benign and attack sets. |
| N-4 | Task 3 review | The system prompt says to escalate money movement, but the copilot has no such behaviour. | Out of scope unless a money-movement scenario is added. |
| N-5 | Task 1 review | The spaCy model `en_core_web_sm` is installed by a separate command, not by `pip install`. | Document it in the README (Sprint 3, NFR-04). |

# What the Reviews Caught

Every build task had a spec review and a quality review, and each sprint ended with a cross-cutting final review. This is the record of issues those reviews found that the plan had missed, with how each was fixed. They make good interview stories, because each shows a concrete problem found, a decision made, and a test added.

Severity follows the reviewers' own ratings: **Critical** means a security hole or a visibly broken result, and **Important** means something that would mislead a decision or fail under realistic use.

## Sprint 1: gateway core

| Severity | Found | Fix | Decision ID |
|---|---|---|---|
| Critical | **The review path could release the system prompt.** A GR-03 block was reviewable. On approval, the rerun skipped GR-03 and returned the canary, which was also written to the audit log. | Only GR-01 blocks are reviewable, and reruns skip only the blocked stage | E1-12 |
| Important | **Other clients' balances, products and notes still reached the RM.** Only names and account numbers were redacted, so this was the October incident without the name. | GR-02 drops other clients' records before generation | D-9 |
| Important | Client names were written raw to the audit log. | The audit scrubs names and the canary | E1-13 |
| Important | `enabled: "false"` in the config silently left a guardrail on. | Switches must be real booleans | E1-04 |
| Important | "Radcliffe, Casey", lower-case names, and account numbers with spaces bypassed GR-02. | Case, order and separator variants | E1-06 |
| Important | Two simultaneous requests could both slip under the rate limit. | Thread-safe GR-04 | E1-08 |
| Important | Concurrent audit writes could corrupt lines, a crash during purge could wipe the log, and free text bypassed redaction. | Locks, atomic purge, scrub every text field | E1-09 |
| Important | A copilot crash skipped the audit. A guard missing from the setup silently switched off while the log said "enabled". | 502 with audit; refuse to start | E1-10 |
| Important | An approved review could end "approved, no answer". Two reviewers could rerun the same request twice. An RM could approve their own review. Blocked questions were kept forever. | Outcome check, lock, no self-approval, time limit | E1-11 |
| Important | GR-05 enabled with no audit log served traffic unaudited. | Refuse to start | E1-14 |

## Sprint 2B: FAIR engine

| Severity | Found | Fix | Decision ID |
|---|---|---|---|
| Important | **The comparison was unfair.** The "attackers adapt" haircut applied only to measured options, so testing the gateway would make it look worse than an untested vendor firewall. | Apply the haircut to every option (product owner decision) | D-12 |
| Important | **Results swung with the random seed.** The vendor firewall's return varied about 2.5× by seed, because options weren't really facing the same simulated years. | Fixed-size random streams, thinning, superposition | E2-05 |
| Important | Baseline uncertainty was ignored, so measured intervals looked tighter than they were. Then the Katz interval stopped reproducing the PRD's FR-20 example. | Katz below a 100% baseline, Wilson at 100%, no measurement when thin | E2-04 |
| Important | Typos in the model file, block rates above 1, and duplicate IDs all loaded silently. | Stricter validation | E2-03 |
| Important | Ranges were missing (FR-22), there were no per-scenario 1-in-10-year figures (FR-21), and "ROI 4.8" next to "ratio 5.8" invites misreading. | Ranges, per-scenario stats, a three-state funding flag | E2-06 |
| Important | The year-to-year range was nearly mislabelled as "quiet vs bad years". Its low end is actually years when extra shadow-AI leaks land. | Correct label, plus a "worse than nothing" share | E2-07 |
| Important | **The index fix's 25.8 : 1 headline** is partly a by-product of the model's design. The real CFO finding was missing: adding the gateway on top of the fix returns only about **1.8 : 1**. | Incremental returns and footnotes | E2-08 |

## Sprint 3: dashboard

| Severity | Found | Fix | Decision ID |
|---|---|---|---|
| Critical | **Dollar signs rendered as LaTeX maths.** The executive appetite verdict was unreadable, and the live demo lost its `$` signs. | Escape `$`; show model output as plain text | E3-03 |
| Important | The index fix ranked first on the executive view with no caveat about its unconfirmed cost and its January availability. | Caveat on the executive view and in the README | E3-04 |
| Important | **The README overstated authorship** and didn't say the interviews were role-plays. The git history shows the documents were co-authored. | Accurate wording on roles and method | E3-05 |
| Important | The what-if "gateway cost" slider also scaled the index fix's share of the combined option. | Scale only the gateway share | E3-06 |
| Important | Negative amounts showed as `$-52K`, $999,999 showed as `$1000K`, and "never worse than nothing" overclaimed. | Formatting fixes; "none in 10,000 simulated years (by design)" | E3-02 |

## Patterns worth noting

- **The most serious findings were about meaning, not code:**
  - an unfair comparison
  - a misleading headline
  - a label that would have misled a CFO
  - an authorship claim that couldn't survive a look at the git history

  Tests pass on all of these. Only review catches them.
- **Defence in depth showed up in the data.** Several attacks that GR-01 missed were neutralised by GR-02. That is why "attack stopped" is measured by outcome (D-10), not detection.
- **Most fixes were small.** The time went into finding the issues, not fixing them.

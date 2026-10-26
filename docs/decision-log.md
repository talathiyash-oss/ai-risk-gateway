# Decision Log

Every decision taken on the AI Risk Gateway project, in the order it was made. Each one lists the options considered, the choice, the reason, who decided, and where it is recorded in more detail.

**Who decided:**
- **PO** is Yash Talathi, product owner. These are product, scope and business decisions.
- **Eng** is the engineering team (Claude), which made technical choices within the product decisions.
- **Review** means a code or design review raised the issue and the fix was adopted.

Product decisions in the PRD keep their PRD IDs (D-1 to D-12). Everything else uses a phase prefix:

| Prefix | Phase |
|---|---|
| F | Framing |
| S | Scenario |
| P | Discovery |
| B | Business case |
| R | Research |
| G | Gate |
| E1 | Sprint 1 engineering |
| E2 | Sprint 2B engineering |
| E3 | Sprint 3 engineering |

---

## 1. Framing (2026-10-23)

| ID | Decision | Options considered | Chosen | Why | By |
|---|---|---|---|---|---|
| F-01 | Shape of the project | Two separate projects (a security proxy, a risk model); one connected system | **One system:** the gateway is the sensor and the FAIR model turns what it sees into dollars | Two disconnected tools read as tutorials. Connecting them answers the question CISOs actually face: which controls are worth funding. | PO |
| F-02 | Product owner's role | Write the code; pair-build; product owner directs while AI builds | **Product owner and consultant**, with an AI-assisted build | The PO doesn't code and is targeting consulting and security PM roles. Resume wording must not claim the PO wrote the code. | PO |
| F-03 | Client industry | Healthcare; financial services; B2B SaaS; insurance; retail | **Financial services** | FAIR started in banking, and banks are the biggest client base for Big 4 risk work. Regulation is rich, and public fine data exists to calibrate losses. | PO |
| F-04 | AI use case | Internal RM copilot; customer-facing chatbot; credit memo drafting | **Internal relationship-manager copilot (RAG over client data)** | The threats are realistic (cross-client leakage, injection hidden in documents), the regulation is moderate, and it mirrors the PO's prior knowledge-assistant work. | PO |
| F-05 | How much to build | Proxy plus simulated LLM plus attack suite; the same with a real LLM; documents and a model only | **Working proxy, simulated copilot, attack suite, FAIR engine, dashboard** | A real LLM can be added later. Simulation is free, gives the same results every run, and makes the dollar figures rest on measurement rather than guesses. | PO |
| F-06 | OWASP LLM Top 10 scope | All ten; only those a runtime gateway can stop and measure | **LLM01, LLM02, LLM07, LLM10 at the gateway.** The other six are documented with their owning control | Claiming all ten would overstate what a gateway can do. LLM05 was added later (D-6). | PO |
| F-07 | EU exposure | No EU presence; a small EU subsidiary | **A small EU subsidiary** | It makes the EU AI Act applicability analysis real: the Act partly applies, rather than "doesn't apply". | PO |
| F-08 | Model risk guidance | Leave it out; add Fed/OCC model risk guidance | **Add it** (originally SR 11-7; see R-01) | It signals banking-consulting knowledge for very little extra work. | PO |
| F-09 | Delivery method | Waterfall; agile; hybrid | **Hybrid:** phase gates for documents, sprints for the build | This is how banks actually run projects. | PO |
| F-10 | Where documents live | Claude Docs; repository Markdown | **Repository Markdown under `docs/`** | Everything ships together on GitHub. | Eng |

## 2. Scenario (2026-10-25)

| ID | Decision | Options considered | Chosen | Why | By |
|---|---|---|---|---|---|
| S-01 | Bank size | About $15B; about $35B; about $80B | **About $35B in assets, about 3,500 staff, 300 RMs** | Big enough to attract regulatory scrutiny and support an EU arm, small enough that the CISO fights for budget. | PO |
| S-02 | Bank name | Four invented names | **Brindlemoor Trust** (no match in FDIC BankFind) | An invented name avoids impersonating a real institution. | PO |
| S-03 | Headquarters | Chicago with a New York trust company; Rochester, NY; Charlotte | **Chicago, plus a New York-licensed trust company** | NYDFS Part 500 then applies to one entity only, which is a realistic nuance to analyse. | PO |
| S-04 | EU subsidiary location | Luxembourg; Ireland | **Luxembourg (Brindlemoor Wealth S.A.)** | Europe's hub for private banking. | PO |
| S-05 | Luxembourg's involvement | Pilot users; Phase 2 users; data only | **Phase 2 users (about 20 RMs, July 2027)** | EU duties start on a known date, which gives a deadline. | PO |
| S-06 | Rollout numbers | Proposed set; adjust | **Pilot of 40 RMs, January to March 2027. Full rollout of 300 by July 2027. 15 queries per RM per day. About $4.1M a year in time saved** | The numbers are internally consistent and match the PRD's examples. | PO |
| S-07 | Trigger | Board condition plus near miss; board only; regulator finding; near miss only | **The board makes funding conditional on a dollar assessment, and an RM saw another client's balance in testing** | The board condition forces dollars, and the near miss provides evidence. | PO |

## 3. Discovery (2026-10-25)

| ID | Decision | Options considered | Chosen | Why | By |
|---|---|---|---|---|---|
| P-01 | Interview method | Text in chat; voice in a separate chat | **Voice role-plays.** Fictional stakeholders were played by AI from written prompts, with hidden facts to uncover and a scored debrief | Practises a real skill; the debriefs gave measurable feedback (23 of 24 hidden facts found). | PO |
| P-02 | Problem statement | The PO's draft; a revised version | **The revised 107-word version** | Every claim is backed by something an interviewee said. | PO |
| P-03 (R-1) | Who accepts residual risk | The business, within appetite (three lines of defence); the CISO; always the Risk Committee | **The CISO** | One clear owner and faster decisions. Accepted trade-off: security owns the failure if an incident follows. Re-confirmed when the CISO pushed back at sign-off. | PO |
| P-04 (R-2) | Who approves control funding | The CISO up to $400K, the CFO above; always the CFO | **Always the CFO** | One budget owner sees every ROI case. | PO |
| P-05 (R-3) | Who sets the risk appetite and approves rollout | — | **The Risk Committee** | Follows from the board's funding condition. The CISO's thresholds become a proposal. | Eng, accepted by PO |
| P-06 | More interviews | Skip; interview the CFO, Compliance and the RM lead | **Interview all three** | Disagreements between stakeholders shape the requirements. Each interview changed the PRD. | PO |

## 4. Product requirements (PRD §6, 2026-10-23 to 2026-10-27)

| ID | Decision | Options considered | Chosen | Why | By |
|---|---|---|---|---|---|
| PD-01 | Order of documents | BRD first; PRD first | **PRD drafted before the BRD,** with business objectives marked as assumed | At the PO's request. The business objectives were later replaced by the BRD's. | PO |
| D-1 | Guardrail failure mode | All fail closed; GR-03 open; GR-05 open with an alert | **Fail closed** for GR-01, 02, 03 and 05. **Fail open** for GR-04 | A data leak costs far more than a short outage. "If we can't record it, we don't serve it." | PO |
| D-2 | False-block cap | 1%/3%; 2%/5%; 5%/10% | **1% per guardrail, 2% combined** (tightened from 2%/5% after the RM lead interview) | RMs tolerate about one block a week. | PO |
| D-3 | Test suite size | 40 per category + 200 with no hold-out; 100 + 1,000; 200 + 2,000 | **100 attacks per category + 1,000 benign questions, split 60/40** | Precise enough to enforce D-2. Beyond that, extra prompts mostly add variations. | PO |
| D-4 | Friction cost inputs | Single values; ranges | **Ranges:** $70/$95/$130 an hour and 1/3/10 minutes per false block. Volumes come from the scenario | Consistent with the rest of the model. | PO |
| D-5 | Effectiveness haircut | Fixed multipliers; statistics only; statistics plus an attacker factor | **Statistical interval (measured) × an adaptive-attacker factor of 0/15/40% (assumed)** | Separates measurement noise from what can only be judged. | PO |
| D-6 | Stretch items | Decide later; promote FR-31 | **FR-31 (upstream index fix) promoted to Should.** FR-30 (link stripping, GR-06) moved into Sprint 2 on 2026-10-26 | FR-31 enables the "fix upstream or catch at the gateway" comparison. | PO |
| D-7 | Fast path for blocked RMs | Review without override; self-override with a reason; none | **Review without override,** with a 15-minute target | Removes the dead end that drives RMs to ChatGPT, while the block still stands. | PO |
| D-8 | Shadow AI | Scenario linked to friction; fixed-rate scenario; a note only | **Scenario S5, whose frequency rises with false blocks** | Puts a dollar figure on the risk cost of over-blocking. | PO |
| D-9 | Other clients' records retrieved by the copilot | Redact identifiers only; drop whole records | **GR-02 drops other clients' records before the copilot answers** | Redacting names still leaked balances: the October incident without the name. | PO, after review |
| D-10 | What counts as "attack stopped" | Outcome; detection | **Outcome:** the attacker gained nothing | Matches FAIR's Vulnerability and credits defence in depth. | PO |
| D-11 | Shape of incident losses | PERT ranges; lognormal | **Lognormal, entered as a 90% range** | Breach losses are heavily skewed: a median claim of $110K against an average breach of $6.29M. | PO |
| D-12 | Does the haircut apply to untested options? | Measured rates only; all rates | **All rates, measured or assumed** | Otherwise testing a control would make it look worse than an untested rival. | PO, after review |
| — | FR-19 acceptance wording | Exactly equal; within a tolerance | **Within 1% at 200,000 iterations** | Incident counts are random by design. | Eng |

## 5. Business case (BRD, 2026-10-25)

| ID | Decision | Options considered | Chosen | Why | By |
|---|---|---|---|---|---|
| B-01 | Measure for "reduce risk" (BO-2) | Within appetite; cut by 60%; both | **Within appetite:** expected loss under $1M and a 1-in-10-year loss under $5M | The Risk Committee decides against thresholds. | PO |
| B-02 | Measure for "protect productivity" (BO-3) | Blocks per week; % of hard value; both | **Friction under 10% of the $2M hard value (about $200K a year)** | Comparable with what the CFO counts. | PO |
| B-03 | Assessment scope | All 300 RMs with commercial banking flagged; wealth only; pilot only | **All 300, with commercial banking figures provisional** | The board is funding the full rollout. | PO |
| B-04 | Numbers before the model exists | Rough ranges; options without numbers; a full estimate | **A full preliminary estimate,** labelled and later replaced | At the PO's request. A self-assessment bias was noted and addressed in D-12 and E2-06. | PO |
| B-05 | Shadow AI keeps the bank above appetite | Add it to scope; a separate initiative; report the gap only | **A separate shadow-AI initiative owned by the CISO** | The gateway can't reduce it. | PO |

## 6. Research corrections (2026-10-25)

| ID | Decision | Chosen | Why | By |
|---|---|---|---|---|
| R-01 | Model risk guidance | **SR 11-7 replaced by SR 26-2** everywhere | Verified on the Federal Reserve's site: SR 26-2 (17 April 2026) supersedes SR 11-7 and excludes generative AI. The copilot falls outside it; the FAIR engine likely falls inside it. | Eng |
| R-02 | EU AI Act timeline | **High-risk duties dated 2 December 2027;** Art. 4 AI literacy treated as "take measures" | The Digital Omnibus (Regulation (EU) 2026/1744) changed both. | Eng |

## 7. Gates

| ID | Date | Decision | Consequence | By |
|---|---|---|---|---|
| G-01 (GD-1) | 2026-10-25 | Start the build before BRD and PRD sign-off | Open items carried forward; least-volatile parts built first | PO |
| G-02 | 2026-10-25 | Merge Sprint 1 after the final review and fix pass | — | PO |
| G-03 (GD-2) | 2026-10-26 | Start Sprint 2 before the CFO and CISO review the BRD | Dollar figures are provisional and labelled Assumed | PO |
| G-04 | 2026-10-26 | Split Sprint 2 into 2A (attack suite and harness) and 2B (FAIR engine); build 2B first | 2B runs on Assumed effectiveness until 2A exists. 2A planning stopped partway | PO and Eng |
| G-05 | 2026-10-26 | Merge Sprint 2B | — | PO |
| G-06 | 2026-10-27 | Sprint 3 (dashboard) before documentation; publish to GitHub only with explicit approval | — | PO |

## 8. Sprint 1 engineering (gateway core)

| ID | Decision | Why | By |
|---|---|---|---|
| E1-01 | Build test-first, with a fresh subagent per task and two reviews per task | The PO chose subagent-driven development; each task gets a spec review and a quality review. | PO |
| E1-02 | Deterministic simulated copilot with deliberate weaknesses | Gives a measurable, free and repeatable baseline. | Eng |
| E1-03 | Presidio with the small spaCy model, plus a custom recognizer for the bank's account format | Lightweight, at a few milliseconds per question. | Eng |
| E1-04 | Config switches must be real booleans | `enabled: "false"` used to silently leave a guardrail on. | Review |
| E1-05 | GR-01 matches whitespace variants | Double spaces and newlines bypassed it. | Review |
| E1-06 | GR-02 matches case, "Last, First" and separator variants | Name and account variants bypassed it. | Review |
| E1-07 | GR-03 canary check ignores case | An upper-cased canary bypassed it. | Review |
| E1-08 | GR-04 is thread-safe | Concurrent requests could exceed the limit. | Review |
| E1-09 | Audit log is thread-safe, purges atomically, and scrubs every text field | Concurrent writes could corrupt it, and free text bypassed redaction. | Review |
| E1-10 | The gateway audits copilot errors (502), refuses to start with a missing guard, and turns fail-closed errors into 503 | Errors used to skip the audit; a missing guard silently failed open. | Review |
| E1-11 | The review queue checks the rerun outcome, prevents races and self-approval, and limits retention | Silent "approved, no answer"; double reruns; D-7's ban on self-override. | Review |
| E1-12 | Only GR-01 blocks are reviewable, and reruns skip only the blocked stage | A GR-03 review could release the system prompt. | Review |
| E1-13 | The audit log never stores client names or the canary | Names were written raw. | Review |
| E1-14 | Gateway refuses GR-05 enabled without an audit log | Otherwise it would serve traffic unaudited, silently. | Review |

## 9. Sprint 2B engineering (FAIR engine)

| ID | Decision | Why | By |
|---|---|---|---|
| E2-01 | The engine reads harness results when they exist, otherwise labelled assumptions | It runs today and upgrades automatically once Sprint 2A exists. | Eng |
| E2-02 | Common random numbers across options | Differences between options shouldn't be sampling noise. | Eng |
| E2-03 | Stricter input validation: block-rate keys, 0–1 bounds, unique IDs, positive values | Typos used to load silently. | Review |
| E2-04 | Katz log-ratio interval when the baseline is below 100%, Wilson when it is 100%, and no measurement when the baseline is thin | Accounts for baseline uncertainty and reproduces the PRD's FR-20 example. | Review |
| E2-05 | Fixed-size random draws per component, thinning for controls, and superposition for the shadow-AI uplift (no SciPy) | Pairing between options mostly failed before: return ratios swung up to 2.5× by seed. | Review |
| E2-06 | Report ranges, per-scenario statistics, a three-state funding flag, and accurate false-positive provenance | Needed for FR-21 and FR-22, and to avoid misreading by a CFO. | Review |
| E2-07 | Label the year-to-year range as variation, not uncertainty, and add a "worse than nothing" share | The low end is years when shadow-AI leaks land, not quiet years. | Review |
| E2-08 | Show incremental returns and footnote the index fix | Adding the gateway on top of the index fix returns only about 1.8 : 1. The index fix "can't backfire" by the model's construction. | Review |

## 10. Sprint 3 engineering (dashboard)

| ID | Decision | Why | By |
|---|---|---|---|
| E3-01 | Streamlit, with all logic in pure, tested modules | Every displayed number is testable (NFR-05). | Eng |
| E3-02 | Number formatting handles negatives, unit boundaries, NaN, and the "none in N simulated years" wording | Values a CFO sees must not overclaim. | Review |
| E3-03 | Escape `$` in markdown and show copilot output as plain text | `$...$` rendered as maths and garbled the appetite verdict. Plain text also stops image links in model output from loading. | Review |
| E3-04 | Caveat the index fix on the executive view and in the README | It was ranked first without the A-6 timing and cost caveat. | Review |
| E3-05 | README states that the interviews were role-plays and gives the actual division of work | The previous wording overstated authorship; the git history shows co-authored documents. | Review |
| E3-06 | The what-if gateway cost scales only the gateway's share of the combined option | Scaling the whole combined cost understated its return. | Review |
| E3-07 | Deferred: FR-25 per-guardrail view, FR-26 value and range columns, FR-28 loss-magnitude and on/off controls, NFR-05 per-value sources | Need Sprint 2A data or schema changes; recorded rather than silently unmet. | PO |

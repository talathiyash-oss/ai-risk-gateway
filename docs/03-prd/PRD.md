# Product Requirements Document: AI Risk Gateway

## 0. Document Control

| Field | Value |
|---|---|
| Version | 0.2 (draft) |
| Status | Draft for product owner review |
| Product owner | Yash Talathi |
| Approvers | CISO, Head of Compliance, RM lead, Engineering lead |
| Source spec | `docs/superpowers/specs/2026-10-23-ai-risk-gateway-design.md` |

**Drafted before the BRD.** The business objectives (BO-x) in §1.3 are working assumptions. The BRD will confirm or replace them, and this PRD is updated to match before sign-off. Every item marked **[Assumed]** needs product owner confirmation.

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-23 | First draft |
| 0.2 | 2026-10-23 | Product owner confirmed D-1 to D-6. Test suite resized and split 60/40 (D-3). Friction inputs became ranges linked to the scenario doc (D-4). Effectiveness haircut split into measured and assumed parts (D-5). FR-31 promoted to Should (D-6). |

---

## 1. Overview

### 1.1 Problem

The Bank is rolling out an internal AI copilot that lets relationship managers (RMs) ask questions over client account data, policies and product documents. The CISO can't tell the board or CFO how much financial exposure the copilot creates, or which security controls are worth paying for. Current AI risk assessments give qualitative ratings ("high," "medium") that can't be compared with a control's cost.

### 1.2 Product Vision

A security gateway that protects the copilot at runtime, measures how well each protection works, and turns those measurements into Expected Annual Loss, so that funding decisions on AI controls are made in dollars and backed by evidence.

### 1.3 Business Objectives [Assumed, pending BRD]

| ID | Objective |
|---|---|
| BO-1 | Quantify the copilot's security-related loss exposure in dollars, as a range, before full rollout |
| BO-2 | Reduce modeled Expected Annual Loss from copilot incidents by at least 60% vs. the unprotected baseline |
| BO-3 | Protect the copilot's productivity case: controls must not noticeably slow down or block legitimate RM work |
| BO-4 | Produce audit-ready evidence against NIST AI RMF, ISO/IEC 42001, the EU AI Act (EU subsidiary) and SR 11-7 |
| BO-5 | Rank AI security controls by return on investment so the CISO can prioritize funding |

---

## 2. Personas

| Persona | Role | Goals | Frustrations | "Good" looks like |
|---|---|---|---|---|
| **Priya, Relationship Manager** | End user. Uses the copilot 10–20 times a day to prepare for client meetings | Fast, accurate answers about her clients | Security tools that block her for no clear reason; hearing "use a different tool" | She rarely notices the gateway exists |
| **Daniel, CISO** | Buyer. Accountable for AI security risk | Defend AI security spend to the CFO and board in dollars | Vendors and teams that say "high risk" without numbers; numbers he can't defend | He answers "what's our exposure and what should we fund?" in one slide |
| **Maria, Compliance Analyst** | Auditor. Prepares evidence for regulators and internal audit | Show which controls exist, which rules they satisfy, and that they ran | Evidence spread across emails and screenshots | One export answers the auditor's questions |
| **Sam, Model Risk Validator** | Second line of defense under SR 11-7 | Independently check that the model and its controls work as claimed | Results she can't reproduce | Reruns the tests and gets the same numbers |

---

## 3. User Stories

| ID | Story | Priority | BO |
|---|---|---|---|
| US-01 | As an RM, I want to ask questions about my clients and get answers without noticeable delay, so that the copilot saves me time | Must | BO-3 |
| US-02 | As an RM, when a request is blocked, I want a clear message and a reference ID, so that I can get help without guessing | Must | BO-3 |
| US-03 | As an RM, I want to never see another client's data by mistake, so that I don't cause a privacy breach | Must | BO-2 |
| US-04 | As the CISO, I want to see the copilot's Expected Annual Loss in dollars, with a range, so that I can report exposure to the board | Must | BO-1 |
| US-05 | As the CISO, I want to see the loss reduction, cost and ROI of each guardrail, so that I can decide what to fund | Must | BO-5 |
| US-06 | As the CISO, I want to know which inputs are measured, benchmarked or assumed, so that I can defend the numbers when challenged | Must | BO-1 |
| US-07 | As the CISO, I want to turn individual guardrails on and off and see the effect, so that each control's value is measured separately | Must | BO-5 |
| US-08 | As the CISO, I want to see a 1-in-10-year loss figure, so that I can discuss reserves with the CFO | Should | BO-1 |
| US-09 | As the CISO, I want to change key assumptions and see the loss recalculate, so that I can test how sensitive the answer is | Should | BO-5 |
| US-10 | As a compliance analyst, I want every gateway decision logged with its control ID, so that I can prove controls operated | Must | BO-4 |
| US-11 | As a compliance analyst, I want to see which regulations apply and which control addresses each, so that I can prepare for an exam | Must | BO-4 |
| US-12 | As a compliance analyst, I want to export the audit log, so that I can hand it to auditors | Should | BO-4 |
| US-13 | As the CISO, I want to see coverage of all 10 OWASP LLM risks, including those owned outside the gateway, so that there are no unexplained gaps | Should | BO-4 |
| US-14 | As a model risk validator, I want to rerun the test suite and get identical results, so that I can independently validate the controls | Must | BO-4 |
| US-15 | As the CISO, I want to see a live attack blocked by the gateway, so that the board understands what the controls do | Should | BO-1 |

---

## 4. Functional Requirements

Each requirement has acceptance criteria in Given/When/Then form. Test case IDs mirror requirement IDs (FR-05 → TC-05a, TC-05b, …) and are written in Phase 6.

### 4.1 Gateway Core

**FR-01 Request proxying** (US-01) Must
The gateway accepts RM chat requests, forwards them to the copilot, and returns the copilot's response.
- *Given* all guardrails are off, *when* an RM sends a question, *then* the response is identical to the copilot's direct response.

**FR-02 Guardrail switches** (US-07) Must
Each guardrail (GR-01 to GR-05) can be turned on or off in a configuration file, with no code change.
- *Given* GR-02 is set to off in configuration, *when* the gateway restarts, *then* no GR-02 checks run and the startup log lists GR-02 as disabled.

**FR-03 Policy decisions** (US-02) Must
For each request, the gateway decides allow, redact or block. A block returns a standard message with a reference ID and **no detail about which rule fired** (to avoid helping attackers adjust).
- *Given* a request is blocked, *when* the RM sees the response, *then* it shows the standard block message and a reference ID that matches the audit log entry.
- *Given* a request is blocked, *when* the response is inspected, *then* it contains no guardrail ID, pattern or score.

**FR-04 Fail modes** (D-1) Must
Each guardrail has a configurable failure mode: fail closed (block the request if the guardrail errors) or fail open (allow the request and log the failure).
- *Given* GR-02 is fail closed and its PII engine raises an error, *when* a request arrives, *then* the request is blocked and the log records `GR-02 / error / fail_closed`.
- *Given* GR-04 is fail open and the rate limiter errors, *when* a request arrives, *then* the request is allowed and the log records `GR-04 / error / fail_open`.

### 4.2 GR-01 Prompt Injection (OWASP LLM01)

**FR-05 Direct injection detection** (US-03) Must
Detect instructions in the RM's prompt that try to override the copilot's rules.
- *Given* GR-01 is on, *when* a prompt from the injection test set is submitted, *then* it is blocked and a GR-01 event is logged.

**FR-06 Indirect injection detection** (US-03) Must
Scan retrieved document chunks for embedded instructions before they reach the copilot.
- *Given* GR-01 is on and a retrieved chunk contains an embedded instruction, *when* the copilot builds its answer, *then* that chunk is excluded and a GR-01 event is logged with the document ID.

### 4.3 GR-02 Sensitive Information (OWASP LLM02)

**FR-07 PII redaction in prompts** (US-03) Must
Detect and redact PII in prompts using Presidio, including custom recognizers for Bank account numbers and client IDs.
- *Given* GR-02 is on, *when* a prompt contains an SSN, *then* the SSN is replaced with `<US_SSN>` before reaching the copilot, and a GR-02 redact event is logged.
- *Given* GR-02 is on, *when* a prompt contains a Bank account number in the Bank's format, *then* it is replaced with `<ACCOUNT_NUMBER>`.

**FR-08 Cross-client leak check** (US-03) Must
Each request carries the client ID the RM is working on. The response may reference only that client.
- *Given* GR-02 is on and the session client is C-1001, *when* the copilot response contains an account number belonging to C-2002, *then* that account number is redacted and a GR-02 event is logged with both client IDs.

### 4.4 GR-03 System Prompt Leakage (OWASP LLM07)

**FR-09 System prompt leak blocking** (US-03) Must
The copilot's system prompt contains a secret canary string. Responses containing the canary, or closely matching system prompt text, are blocked.
- *Given* GR-03 is on, *when* a response contains the canary string, *then* the response is blocked and a GR-03 event is logged.
- *Given* GR-03 is on, *when* a response reproduces at least 80% of any system prompt sentence, *then* the response is blocked.

### 4.5 GR-04 Unbounded Consumption (OWASP LLM10)

**FR-10 Rate limiting and budgets** (US-01) Must
Per-user limits on requests per minute and tokens per day. [Assumed defaults: 20 requests/minute, 50,000 tokens/day]
- *Given* GR-04 is on, *when* a user sends a 21st request within one minute, *then* the gateway returns HTTP 429 with the standard message and logs a GR-04 event.

### 4.6 GR-05 Audit Logging

**FR-11 Decision logging** (US-10) Must
Every request produces one log entry: timestamp, request ID, user ID, session client ID, guardrails evaluated, decision per guardrail, reason code, latency. No raw PII is written to the log.
- *Given* any request, *when* it completes, *then* exactly one log entry exists with all listed fields.
- *Given* a prompt contains an SSN, *when* the log entry is written, *then* the log contains `<US_SSN>`, not the SSN.
- *Given* any request, *when* the log entry is written, *then* it contains only redacted prompt and response text, never the raw text (GDPR data minimization, Compliance interview 2026-10-25).
- *Given* a retention period set in configuration, *when* a log entry is older than that period, *then* it is deleted. The period is set by Compliance.

**FR-12 Log export** (US-12) Should
Export the audit log for a date range as JSON Lines.
- *Given* log entries exist for a date range, *when* an export is requested, *then* a `.jsonl` file is produced with one entry per line, matching the log exactly.

### 4.7 Simulated Copilot

**FR-13 Synthetic dataset** (US-14) Must
At least 50 synthetic clients across at least 10 RMs, generated from a fixed seed. Includes names, account numbers, balances, products and notes. No real data.
- *Given* the same seed, *when* the dataset is generated twice, *then* the files are byte-identical.

**FR-14 Deliberate baseline vulnerabilities** (US-07) Must
With all guardrails off, the copilot obeys injected instructions, can return other clients' data, and can reveal its system prompt. This gives a measurable unprotected baseline.
- *Given* all guardrails are off, *when* each attack category's example prompt is sent, *then* the attack succeeds.

### 4.8 Test Suite and Evaluation Harness

**FR-15 Labelled test suite** (US-14) Must
Labelled attack prompts for each in-scope category, plus benign RM questions, in the sizes set by D-3. **Split into a tuning set (60%) and a hold-out set (40%).** Guardrails may be tuned only on the tuning set; reported rates use the hold-out set only (see RISK-01).
- *Given* the suite, *when* inspected, *then* every prompt has a category label, an expected outcome (attack/benign), and a split label (tune/holdout).

**FR-16 Harness runs** (US-07, US-14) Must
The harness replays the hold-out set under these configurations: all off, each guardrail on alone, all on. For each, it reports attack block rate and benign false-positive rate, with counts and a 95% Wilson confidence interval.
- *Given* a fixed seed, *when* the harness runs twice, *then* the results files are identical.
- *Given* 37 of 40 hold-out attacks blocked, *when* results are reported, *then* the block rate is 92.5% with a 95% interval of 80.1%–97.4%.
- *Given* a guardrail's measured false-positive rate is above the D-2 cap (2% per guardrail; 5% for all guardrails combined), *when* results are reported, *then* that guardrail is flagged as failing the cap.
- *Given* the all-off configuration, *when* the harness runs, *then* the attack block rate is 0%.

**FR-17 Results handoff** (US-04) Must
The harness writes a results file that the FAIR engine reads as the source for Vulnerability inputs.
- *Given* a harness results file, *when* the FAIR engine runs, *then* each scenario's Vulnerability is labelled "Measured" and cites the results file and run ID.

### 4.9 FAIR Risk Engine

**FR-18 Scenario configuration** (US-06) Must
Scenarios S1–S4 are defined in a configuration file. Every input is a PERT range (min, most likely, max) with a provenance label (Measured / Benchmarked / Assumed) and a source or rationale.
- *Given* an input without a provenance label, *when* the engine starts, *then* it refuses to run and names the missing field.

**FR-19 Monte Carlo simulation** (US-04, US-14) Must
Simulate 10,000 years per scenario (configurable), without and with controls, with an optional fixed seed.
- *Given* a fixed seed, *when* the engine runs twice, *then* all outputs are identical.
- *Given* inputs where min = most likely = max (no uncertainty), *when* the engine runs, *then* EAL equals frequency × magnitude exactly.

**FR-20 Effectiveness haircut** (US-06) Must
Vulnerability is derived from two separately labelled parts (D-5):
1. **Measurement uncertainty [Measured]:** the block rate's 95% confidence interval from FR-16.
2. **Adaptive-attacker degradation [Assumed]:** how much worse real attackers are than our test suite, as a PERT range of 0% / 15% / 40%.

Vulnerability = 1 − (block rate × (1 − degradation)): min uses the interval's upper bound with 0% degradation, most likely uses the measured rate with 15%, max uses the interval's lower bound with 40%.
- *Given* 37/40 blocked (92.5%, interval 80.1%–97.4%), *when* Vulnerability is derived, *then* the PERT range is min 2.6%, most likely 21.4%, max 51.9%.
- *Given* a derived Vulnerability, *when* the provenance view shows it, *then* the measured part and the assumed part are displayed separately.

**FR-21 Risk outputs** (US-04, US-08) Must
Per scenario and in total, without and with controls: EAL, P10, P50, P90, and a loss exceedance curve.
- *Given* a completed run, *when* outputs are read, *then* all listed values exist for every scenario and for the total, in both conditions.

**FR-22 ROI per control** (US-05) Must
ROI = (EAL reduction − control cost) ÷ control cost. Control cost = annual run cost + friction cost. Friction cost = false-positive rate × annual benign queries × minutes lost per false block ÷ 60 × RM loaded hourly rate. Annual benign queries = RMs × queries per RM per day × working days, taken from `docs/00-scenario.md`. Minutes lost and hourly rate are PERT ranges (D-4), so friction cost and ROI are simulated and reported as ranges.
- *Given* most-likely values of EAL reduction $500,000, run cost $40,000, FP rate 1%, 1,125,000 annual benign queries, 3 minutes per block, $95/hour, *when* ROI is calculated, *then* friction cost = $53,437.50, control cost = $93,437.50, ROI ≈ 4.35 (435%).
- *Given* the scenario doc changes the number of RMs, *when* the engine reruns, *then* annual benign queries and friction cost update with no other edits.
- *Given* a control's EAL reduction is less than 3 times its control cost (the CFO's funding test), *when* results are shown, *then* the control is flagged "Below 3:1, consider accepting the risk."

**FR-33 Compare alternatives, including doing nothing** (US-05) Must
The control view compares our guardrails against two alternatives: **accept the risk** (no new controls, cost $0) and a **vendor AI firewall** modelled as a single control at $250K a year, with assumed effectiveness labelled as Assumed.
- *Given* a completed run, *when* the CISO opens the control view, *then* "accept the risk," the vendor firewall and the recommended guardrail set appear side by side with EAL, P90, cost and ROI.

### 4.10 Dashboard

**FR-23 Executive view** (US-04, US-08) Must
Total EAL without and with controls, P90, percentage reduction, and the top three controls by ROI.
- *Given* a completed FAIR run, *when* the CISO opens the dashboard, *then* the executive view shows all listed values on one screen without scrolling at 1440×900.

**FR-24 Loss exceedance curve** (US-08) Must
A chart of the probability of losing more than $X, without vs. with controls.

**FR-25 Control view** (US-05) Must
Per guardrail: block rate, false-positive rate, EAL reduction, run cost, friction cost, ROI.

**FR-26 Provenance view** (US-06) Must
Every model input shows its value, range, provenance label and source. Can be filtered to show only Assumed inputs.
- *Given* the provenance view, *when* "Assumed only" is selected, *then* only Assumed inputs appear, each with its rationale.

**FR-27 Compliance view** (US-11, US-13) Must
Shows the applicability table, the control register (GR-x → OWASP, NIST AI RMF, ISO 42001, EU AI Act, SR 11-7), and the coverage table for all 10 OWASP risks, naming the owning control for those outside the gateway.

**FR-28 What-if analysis** (US-09) Should
Change selected inputs (threat frequency, loss magnitude, adaptive-attacker degradation, guardrail on/off) and see EAL recalculate.
- *Given* the CISO doubles S2's threat event frequency, *when* the model reruns, *then* the new EAL appears within 10 seconds next to the original.

**FR-29 Live demo panel** (US-15) Should
Send a prompt through the running gateway and see the decision and the audit log entry.

### 4.11 Stretch Items

**FR-30 Markdown link stripping, OWASP LLM05** Could (D-6)
Remove markdown images and links pointing to domains not on an allowlist, blocking data exfiltration through rendered images.

**FR-31 Permission-aware retrieval, OWASP LLM08** Should (D-6)
A switchable option in the simulated copilot: when on, it only retrieves records for the session client. The FAIR engine compares S1 loss under four strategies: neither, upstream fix only, GR-02 only, and both.
- *Given* the harness and FAIR engine have run all four strategies, *when* the CISO opens the control view, *then* S1 EAL, control cost and ROI are shown side by side for each strategy.

**FR-32 Real LLM backend** Won't (this release)
Replace the simulated copilot with a real LLM API. Planned as a later toggle.

---

## 5. Non-Functional Requirements

| ID | Requirement | Acceptance |
|---|---|---|
| NFR-01 | Gateway adds no more than 150 ms at p95 per request, excluding copilot time, on a standard laptop | Harness reports p95 added latency ≤ 150 ms over the full suite |
| NFR-02 | Synthetic data only. No real personal or bank data anywhere in the repository | Scan of the repo finds no real data; the data generator is the only source |
| NFR-03 | Reproducible: the same seed gives identical harness and FAIR outputs | FR-16 and FR-19 reproducibility tests pass |
| NFR-04 | Runs locally with one setup command and one run command. No paid services. Python 3.11+ | A fresh clone runs following only the README |
| NFR-05 | Every number on the dashboard can be traced to a configuration file or results file | Each dashboard value shows its source file on hover or in a tooltip |
| NFR-06 | Block messages reveal nothing about detection logic | FR-03 second criterion passes |
| NFR-07 | The README explains every component in plain language for a non-engineer | Product owner review: can explain each component after reading |

---

## 6. Decision Log

All decisions confirmed by the product owner on 2026-10-23.

| ID | Decision | Options considered | Decision | Why |
|---|---|---|---|---|
| D-1 | Failure mode per guardrail | All closed; GR-03 open; GR-05 open with alert | GR-01, GR-02, GR-03, GR-05: **fail closed**. GR-04: **fail open** | Data exposure costs far more than a short outage, and a rate-limiter fault exposes no data. GR-05 fails closed because "if we can't record it, we don't serve it" supports SR 11-7 and EU AI Act Art. 12 evidence. Accepted trade-off: a logging fault takes the copilot down. |
| D-2 | Highest acceptable false-positive rate | 1%/3%, 2%/5%, 5%/10% (per guardrail / combined) | **2% per guardrail, 5% combined** | At worst about one false block per RM per day. Higher rates push RMs toward unapproved tools, which is a worse risk. A guardrail over the cap fails UAT and is retuned. |
| D-3 | Test suite size and split | 40/category + 200 with no hold-out; 100 + 1,000; 200 + 2,000 | **100 attacks per category (400) + 1,000 benign, split 60% tuning / 40% hold-out** | Gives 40 scored attacks per category (37/40 → interval 80–97%) and 400 scored benign questions (2% → interval 1.0–3.9%), precise enough to enforce D-2. Beyond this, extra prompts mostly add variations rather than new techniques. |
| D-4 | Friction cost inputs | Point values; ranges | **RM loaded hourly cost $70 / $95 / $130; minutes lost per false block 1 / 3 / 10 (PERT, Assumed). RM count, queries per RM per day and working days come from `docs/00-scenario.md`.** | Consistent with the rest of the model, which uses ranges. The 10-minute tail covers an RM giving up and finding the answer another way. Hourly cost to be benchmarked during BRD research. |
| D-5 | Effectiveness haircut | Fixed multipliers; confidence interval only; interval + attacker factor | **Confidence interval [Measured] × adaptive-attacker degradation 0% / 15% / 40% [Assumed], shown separately** | Separates measurement noise, which statistics can handle, from attacker adaptation, which only judgment can. Avoids arbitrary multipliers and lets the CISO test the assumption in the what-if view (FR-28). |
| D-6 | Stretch items | Both later; FR-31 Should and FR-30 later; both Should | **FR-31 promoted to Should. FR-30 stays Could and is decided at the end of Sprint 2.** | FR-31 costs little in a simulated copilot, and it lets the FAIR engine compare fixing the root cause upstream with catching the symptom at the gateway. |

---

## 7. Success Metrics

### Product metrics (does it work?)

| Metric | Target |
|---|---|
| Attack block rate on the hold-out set, all guardrails on | ≥ 90% per in-scope category |
| Benign false-positive rate, hold-out set | Within D-2 limits |
| Gateway added latency | Within NFR-01 |
| Reproducibility | 100% identical on rerun |
| Must requirements with a passing test | 100% |

The block-rate target is a hygiene check on our own suite, not proof of real-world security. That's why D-5 exists.

### Outcome metrics (does it deliver the business objectives?)

| Metric | Target | BO |
|---|---|---|
| Modeled EAL reduction, all controls on vs. baseline | ≥ 60% | BO-2 |
| CISO can answer "what's our exposure and what should we fund?" from the executive view | In a 3-minute demo, unaided | BO-1, BO-5 |
| Controls ranked by ROI, with friction included | All 5 guardrails | BO-5 |
| In-scope controls mapped with verified citations | 100% | BO-4 |
| Traceability: every BO links to at least one Must FR with a test | 100% | All |

---

## 8. OWASP LLM Top 10 (2025) Coverage

| Risk | Coverage | Owner |
|---|---|---|
| LLM01 Prompt Injection | Gateway: GR-01 | This product |
| LLM02 Sensitive Information Disclosure | Gateway: GR-02 | This product |
| LLM03 Supply Chain | Out of scope | Third-party risk management: vendor due diligence (ISO 42001 A.10) |
| LLM04 Data & Model Poisoning | Partly: poisoned documents via FR-06 | Model vendor (weights, training data); content owners (document review) |
| LLM05 Improper Output Handling | Stretch: FR-30 | This product (if built); otherwise front-end team |
| LLM06 Excessive Agency | Not applicable by design: the copilot is read-only | Architecture decision, recorded here |
| LLM07 System Prompt Leakage | Gateway: GR-03 | This product |
| LLM08 Vector & Embedding Weaknesses | Symptom caught by GR-02. Root-cause fix modelled in FR-31 (Should) | Retrieval/platform team |
| LLM09 Misinformation | Out of scope | Business line: grounding checks and human review of client-facing advice |
| LLM10 Unbounded Consumption | Gateway: GR-04 | This product |

---

## 9. Out of Scope

- A real LLM backend (FR-32, later release)
- Authentication and single sign-on (user ID is passed in the request)
- Production deployment, high availability, scaling
- A real vector database (the simulated copilot uses in-memory retrieval)
- RM override of blocks ("break glass")
- OWASP risks not listed as covered in §8

---

## 10. Assumptions, Dependencies, Risks

### Assumptions

| ID | Assumption |
|---|---|
| A-1 | BO-1 to BO-5 reflect the Bank's priorities (to be confirmed in the BRD) |
| A-2 | D-4 hourly cost and minutes-lost ranges are reasonable for a US regional bank (hourly cost to be benchmarked in the BRD) |
| A-5 | Year-one budget for AI security controls is about $400K (CISO interview, 2026-10-25); total recommended control cost should fit within it, or the ROI case must justify more |
| A-6 | The permission-aware search index fix (FR-31) is about three months away and won't be ready for the January 2027 pilot, so the gateway serves as the interim control (CISO interview) |
| A-7 | No insurance recovery is assumed. The cyber policy has a $5M retention and may not cover AI incidents (CFO interview, 2026-10-25) |
| A-8 | The CFO counts about $2M a year of the $4.1M business case as hard value; friction cost is compared against $2M |
| A-4 | Adaptive-attacker degradation of 0% / 15% / 40% is a reasonable starting assumption (D-5); shown as Assumed and adjustable in FR-28 |
| A-3 | Public breach-cost benchmarks for the financial sector are a fair basis for loss magnitude |

### Dependencies

| ID | Dependency |
|---|---|
| DEP-1 | Scenario doc (`docs/00-scenario.md`) completed |
| DEP-2 | BRD v1.0 signed off |
| DEP-3 | Open-source libraries: FastAPI, Microsoft Presidio (with spaCy model), Streamlit, NumPy |
| DEP-4 | Phase 4 verification of framework citations |
| DEP-5 | GDPR Data Protection Impact Assessment for the copilot, owned by Compliance and the Data Protection Officer, required before Luxembourg go-live. The gateway's data-flow and PII-handling evidence is an input. |

### Risks

| ID | Risk | Mitigation |
|---|---|---|
| RISK-01 | Guardrails overfit to the test suite, so measured rates look better than reality | Tuning/hold-out split (FR-15) and the effectiveness haircut (D-5) |
| RISK-02 | Benchmark loss figures are outdated or not comparable | Cite year and sector for each; show as Benchmarked with ranges |
| RISK-03 | Presidio misses Bank-specific identifiers | Custom recognizers (FR-07); a test set of Bank-format IDs |
| RISK-04 | Scope creep from stretch items | D-6 decision gate at the end of Sprint 2 |
| RISK-05 | Framework clause IDs cited incorrectly | Phase 4 verification against primary sources |
| RISK-06 | Dollar outputs taken as precise predictions | Always show ranges, P90 and provenance; label it a model, not a forecast |
| RISK-08 | Model Risk Management (SR 11-7) hasn't reviewed the copilot and may require independent validation that isn't in anyone's plan, delaying rollout | Engage Model Risk early; give them the reproducible harness and test suite (FR-15, FR-16, US-14) as validation evidence |
| RISK-09 | Three external dates cluster: budget lock mid-February, NYDFS Part 500 certification April 15, 2027, Luxembourg go-live July 2027 | Release plan works back from mid-February; compliance view (FR-27) produces evidence usable for the April certification |
| RISK-07 | The 2027 budget locks in mid-February, six weeks before the Risk Committee deadline. A late funding request means controls aren't funded until July, the month of full rollout | Preliminary EAL and ROI results ready by early February 2027, with the full assessment by end of March |

---

## 11. Release Plan

| Sprint | Scope | Demo at sprint review |
|---|---|---|
| 1 | FR-01–FR-14, NFR-06 | An attack succeeds with guardrails off and is blocked with them on; audit log entries |
| 2 | FR-15–FR-22, FR-31, NFR-01, NFR-03 | Harness results with confidence intervals; FAIR outputs from the command line, including the four S1 strategies; FR-30 decision |
| 3 | FR-23–FR-29, FR-33, NFR-04, NFR-05, NFR-07; FR-30 if approved | Full CISO dashboard walkthrough |

**Release deliverables beyond the software:** CISO one-page brief; **EU AI Act classification memo** for Compliance to use with the CSSF (from the applicability analysis); README.

---

## 12. Open Questions

| ID | Question | Resolved by |
|---|---|---|
| Q-1 | ~~Bank name, size, number of RMs, query volume~~ | Resolved 2026-10-23: Brindlemoor Trust, see `docs/00-scenario.md` |
| Q-2 | Are BO-1 to BO-5 and the 60% target right? | BRD |
| Q-3 | ~~What is the Bank's risk appetite for this copilot?~~ | Partly resolved 2026-10-25 in the CISO interview: EAL under $1M and P90 under about $5M. These are Daniel's personal thresholds, not yet agreed by the Risk Committee; the BRD formalizes them. |
| Q-6 | Does the cyber insurance policy cover AI-related incidents? | CFO / insurance broker; BRD |
| Q-5 | Should BO-2 ("reduce EAL by at least 60%") be replaced by "bring EAL within risk appetite"? | BRD |
| Q-4 | ~~Confirm decisions D-1 to D-6~~ | Resolved 2026-10-23, see §6 |

---

## 13. Approvals

| Role | Name | Decision | Date |
|---|---|---|---|
| Product owner | Yash Talathi | | |
| CISO | | | |
| Head of Compliance | | | |
| RM lead | | | |
| Engineering lead | | | |

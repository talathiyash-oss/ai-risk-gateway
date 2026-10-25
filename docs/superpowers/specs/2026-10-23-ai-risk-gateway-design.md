# AI Risk Gateway: Design Spec

**Date:** 2026-10-23
**Product owner:** Yash Talathi
**Status:** Design approved, pending spec review

## 1. Purpose

A portfolio project for consulting and security PM roles. It shows the full SDLC, from business problem through release. The product owner writes the business and product documents and makes the scope and trade-off decisions. The code is built with AI assistance and accepted by the product owner against written acceptance criteria.

**The one-sentence story:** A runtime security gateway measures how well each LLM guardrail works, and a FAIR Monte Carlo engine turns those measurements into Expected Annual Loss, so a CISO can see which guardrails are worth funding.

## 2. Scenario

- **Client:** a fictional US regional bank, called "the Bank" in this spec. It has a small EU wealth-management subsidiary. The product owner names the Bank in Phase 1 and checks that the name isn't a real institution.
- **System under protection:** an internal RAG copilot for relationship managers (RMs). RMs ask questions over client account data, internal policies, and product documents.
- **Executive question:** "What is our dollar exposure from this copilot, and which guardrails are worth funding?"
- **All data is synthetic.** No real client, bank, or person data.

## 3. Architecture

```
RM prompt → AI Security Gateway (FastAPI)
              input guards → policy engine (allow/redact/block) → output guards
              audit log (every decision tagged with a control ID)
           → Simulated bank copilot (synthetic client records)

Test suite (attacks + benign RM questions) → Evaluation harness → block rate, false-positive rate
Control register + harness results → FAIR Monte Carlo engine → EAL, P90, loss curve, ROI
                                                              → Streamlit dashboard
```

### Components

| # | Component | One job |
|---|---|---|
| 1 | Simulated copilot | Answers RM questions over synthetic records. Deliberately unsafe when unprotected (leaks other clients' data, obeys injected instructions, reveals its system prompt). Deterministic, with no LLM API calls. |
| 2 | Gateway | FastAPI service between the user and the copilot. Runs input and output guards and applies the policy decision. |
| 3 | Guardrails | Five controls, each with an ID and an on/off switch (see §5). |
| 4 | Test suite | Labelled attack prompts for each OWASP category, plus benign RM questions used to measure false positives. |
| 5 | Evaluation harness | Replays the suite through the gateway with each guardrail on and off. Outputs block rate and false-positive rate per guardrail. |
| 6 | FAIR engine | Runs four loss scenarios (§4) through a Monte Carlo simulation, without and with controls. |
| 7 | Dashboard | Streamlit. Shows EAL before and after, P90, loss exceedance curve, ROI per control, the control register, and a measured/benchmarked/assumed label on every input. |

**Out of scope (YAGNI):** a real LLM (a later toggle), authentication/SSO, production deployment, OWASP categories beyond LLM01/02/07/10, a real vector database.

### Failure behavior

A per-guardrail fail-closed or fail-open policy. The PRD decides the setting for each guardrail, and the design implements it as configuration. Suggested starting point: fail closed for GR-01/02/03, fail open for GR-04.

## 4. FAIR Model

**Formula:** Risk = Loss Event Frequency × Loss Magnitude, where LEF = Threat Event Frequency × Vulnerability, and Loss Magnitude = primary loss + (secondary loss × probability of secondary loss).

### Scenarios

| # | Scenario | Threat actor | Controls that lower it |
|---|---|---|---|
| S1 | Copilot shows one client's data to an RM working another client's account | Insider (error or curiosity) | GR-02 |
| S2 | Hidden instructions in a document make the copilot leak client data | External attacker | GR-01, GR-02 |
| S3 | System prompt and internal policy logic disclosed | Curious user or red-teamer | GR-03 |
| S4 | Scripted abuse runs up costs or degrades the service | Compromised account or bot | GR-04 |
| S5 | RM pastes client data into an unapproved external AI tool (shadow AI). *Added 2026-10-25 from the RM lead interview; see PRD D-8.* | Insider, to work around friction | None directly; rises with the false-block rate |

### Inputs

- Every input is a PERT range (min, most likely, max).
- Every input carries a provenance label:
  - **Measured:** Vulnerability, from the harness.
  - **Benchmarked:** loss amounts from public sources (IBM *Cost of a Data Breach* financial sector, NYDFS enforcement actions, Verizon DBIR), each cited in the BRD.
  - **Assumed:** threat frequency, with the reasoning written down.
- **Effectiveness haircut:** a block rate measured on our own suite is treated as the best case. The Vulnerability range is widened toward lower effectiveness, because real attackers adapt.

### Simulation and outputs

- 10,000 simulated years per scenario, without and with controls.
- Outputs: EAL (mean), P90, a loss exceedance curve, and ROI per control.
- ROI per control = (EAL reduction − control cost) ÷ control cost.
- Control cost = run cost + **friction cost**. Friction cost = false-positive rate × benign query volume × minutes lost per block × RM loaded hourly rate.

## 5. Control Mapping

### Applicability (first page of the deliverable)

| Framework | Applicability | Treatment |
|---|---|---|
| NIST AI RMF 1.0 (+ AI 600-1 GenAI Profile) | Voluntary; the US reference point | Main structure |
| ISO/IEC 42001:2023 | Voluntary, certifiable | Shows what an audit would ask for |
| EU AI Act | Applies via the EU subsidiary. The RM copilot is likely not high-risk under Annex III. | Art. 4 AI literacy applies; high-risk articles used as voluntary benchmarks |
| Fed/OCC SR 11-7 (Model Risk Management) | Applies: regulators treat an LLM as a model | Validation and ongoing monitoring expectations |
| OWASP Top 10 for LLM Applications (2025) | Industry threat taxonomy | Threat categories for guardrails and tests |

### Control register (draft; all clause IDs verified against primary sources in Phase 4)

| ID | Guardrail | OWASP | NIST AI RMF | ISO 42001 | EU AI Act |
|---|---|---|---|---|---|
| GR-01 | Prompt-injection detection | LLM01 | MEASURE 2.7 | A.6 verification & validation | Art. 15* |
| GR-02 | PII scrubbing (Presidio) + cross-client leak check | LLM02 | MEASURE 2.10 | A.7 data for AI systems | Art. 10* |
| GR-03 | System-prompt leak blocking | LLM07 | MEASURE 2.7 | A.6 life cycle | Art. 15* |
| GR-04 | Rate limiting / usage caps | LLM10 | MANAGE 4.1 | A.6 operation & monitoring | Art. 15* |
| GR-05 | Audit log of all gateway decisions | supports all | MANAGE 4.1 | A.6 event logging | Art. 12* |

\* Voluntary benchmark unless the system is high-risk. SR 11-7 maps to the harness (validation) and GR-05 (ongoing monitoring).

### Process-level mapping

- FAIR analysis → NIST MAP 5.1, ISO 42001 Clause 6.1.2.
- ROI-based funding recommendation → NIST MANAGE 1.3, ISO 42001 Clause 6.1.3.
- Harness results → NIST MEASURE evidence and SR 11-7 validation.

## 6. SDLC Plan

Hybrid delivery: phase gates for documents, sprints for the build.

| Phase | Deliverable | Author | Gate |
|---|---|---|---|
| 1. Discovery | Problem statement, stakeholder map, RACI | Product owner (Claude plays the CISO) | Problem agreed |
| 2. Business case | BRD | Product owner, coached | BRD sign-off |
| 3. Requirements | PRD + traceability matrix (BRD objective → PRD requirement → test case) | Product owner, coached | PRD sign-off |
| 4. Design | Technical design, FAIR model spec, verified control register | Claude | Product owner approval |
| 5. Build | Sprint 1: copilot + gateway + guardrails. Sprint 2: test suite, harness, FAIR engine. Sprint 3: dashboard. | Claude, with sprint demos | Sprint reviews |
| 6. Test & UAT | Test plan, test results, UAT sign-off | Claude (tests), product owner (UAT) | Accepted against PRD criteria |
| 7. Release | README, CISO one-page brief, 3-minute demo, resume bullets | Both | Done |

## 7. Testing

1. **FAIR math:** fixed-input cases with known answers (e.g. constant inputs give an exact EAL), plus a check that a fixed random seed reproduces the same results.
2. **Guardrails:** harness block rate and false-positive rate per guardrail, plus unit tests for each guard.
3. **UAT:** the product owner tests as the CISO and RM personas against the PRD's acceptance criteria.

## 8. Repository Layout

```
ai-risk-gateway/
  docs/       BRD, PRD, RACI, traceability matrix, design, test plan, CISO brief
  src/        copilot, gateway, guardrails, harness, fair engine, dashboard
  data/       synthetic client records, test suite
  tests/
```

Pushing to a public GitHub repo at release is optional.

## 9. Resume Framing

Bullets describe what the product owner actually did: defining requirements, leading an AI-assisted build through the SDLC, mapping controls, and quantifying risk. They don't claim the product owner wrote the code. The product owner must be able to explain every component in an interview; each one gets explained as it's built.

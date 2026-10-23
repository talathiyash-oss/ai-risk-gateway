# Traceability Matrix

Version 0.2 (draft), linked to PRD v0.2. Test case IDs are reserved now and written in Phase 6.

**How to read it:** each row traces a business objective down to the requirement that delivers it, the test that proves it, and the control it relates to. A BO with no Must row means a requirement is missing. A requirement with no BO is scope creep.

## By Business Objective

| BO | User story | Requirement | Priority | Test cases | Control |
|---|---|---|---|---|---|
| BO-1 Quantify exposure | US-04 | FR-17 Results handoff | Must | TC-17a | — |
| BO-1 | US-04 | FR-19 Monte Carlo | Must | TC-19a, TC-19b | — |
| BO-1 | US-04, US-08 | FR-21 Risk outputs | Must | TC-21a | — |
| BO-1 | US-04, US-08 | FR-23 Executive view | Must | TC-23a | — |
| BO-1 | US-08 | FR-24 Loss exceedance curve | Must | TC-24a | — |
| BO-1 | US-06 | FR-18 Scenario config + provenance | Must | TC-18a | — |
| BO-1 | US-06 | FR-20 Effectiveness haircut | Must | TC-20a, TC-20b | — |
| BO-1 | US-06 | FR-26 Provenance view | Must | TC-26a | — |
| BO-1 | US-15 | FR-29 Live demo panel | Should | TC-29a | — |
| BO-2 Reduce EAL ≥60% | US-03 | FR-05 Direct injection | Must | TC-05a | GR-01 |
| BO-2 | US-03 | FR-06 Indirect injection | Must | TC-06a | GR-01 |
| BO-2 | US-03 | FR-07 PII redaction | Must | TC-07a, TC-07b | GR-02 |
| BO-2 | US-03 | FR-08 Cross-client leak check | Must | TC-08a | GR-02 |
| BO-2 | US-03 | FR-09 System prompt leak | Must | TC-09a, TC-09b | GR-03 |
| BO-2 | — | FR-30 Markdown link stripping | Could | TC-30a | (LLM05) |
| BO-2 | — | FR-31 Permission-aware retrieval | Should | TC-31a | (LLM08) |
| BO-3 Protect productivity | US-01 | FR-01 Request proxying | Must | TC-01a | — |
| BO-3 | US-01 | FR-10 Rate limiting | Must | TC-10a | GR-04 |
| BO-3 | US-01 | NFR-01 Latency ≤150 ms p95 | Must | TC-N01a | — |
| BO-3 | US-02 | FR-03 Policy decisions | Must | TC-03a, TC-03b | — |
| BO-3 | US-02 | NFR-06 No detection detail in block messages | Must | TC-03b | — |
| BO-3 | — | D-2 False-positive limit (via FR-16) | Must | TC-16c | All |
| BO-4 Audit evidence | US-10 | FR-11 Decision logging | Must | TC-11a, TC-11b | GR-05 |
| BO-4 | US-12 | FR-12 Log export | Should | TC-12a | GR-05 |
| BO-4 | US-11, US-13 | FR-27 Compliance view | Must | TC-27a | All |
| BO-4 | US-14 | FR-13 Synthetic dataset | Must | TC-13a | — |
| BO-4 | US-14 | FR-15 Labelled test suite | Must | TC-15a | All |
| BO-4 | US-14 | FR-16 Harness runs | Must | TC-16a, TC-16b, TC-16d | All |
| BO-4 | US-14 | NFR-03 Reproducibility | Must | TC-16a, TC-19a | — |
| BO-4 | — | FR-04 Fail modes (D-1) | Must | TC-04a, TC-04b | All |
| BO-5 Rank controls by ROI | US-05 | FR-22 ROI per control | Must | TC-22a, TC-22b | All |
| BO-5 | US-05 | FR-25 Control view | Must | TC-25a | All |
| BO-5 | US-07 | FR-02 Guardrail switches | Must | TC-02a | All |
| BO-5 | US-07 | FR-14 Baseline vulnerabilities | Must | TC-14a | — |
| BO-5 | US-09 | FR-28 What-if analysis | Should | TC-28a | — |

## Coverage Check

| BO | Must requirements | Gaps |
|---|---|---|
| BO-1 | 8 | None |
| BO-2 | 5 | None |
| BO-3 | 6 | None |
| BO-4 | 7 | None |
| BO-5 | 4 | None |

Every Must user story (US-01–07, US-10, US-11, US-14) maps to at least one Must requirement.

Requirements with no user story: FR-04 (from decision D-1), FR-30/FR-31 (stretch items from the OWASP coverage review). These trace to BOs through decisions rather than stories, which is acceptable. NFR-02, NFR-04, NFR-05, NFR-07 are delivery constraints and are verified in Phase 6 rather than traced to a single BO.

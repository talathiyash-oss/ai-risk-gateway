# Business Requirements Document: AI Risk Gateway

| Field | Value |
|---|---|
| Client | Brindlemoor Trust (fictional) |
| Sponsor | Daniel, CISO (Accountable, RACI) |
| Author | Yash Talathi, Product owner |
| Version | 0.1 (draft) |
| Status | In progress |
| Related | Problem statement (`docs/01-discovery/problem-statement.md`), sources (`sources.md`), PRD (`docs/03-prd/PRD.md`) |

---

## 1. Executive Summary

*Written last.*

---

## 2. Background and Problem

### 2.1 Background

Brindlemoor Trust (~$35B in assets, Chicago) is rolling out **Brindlemoor Assist**, an internal AI copilot that lets its 300 relationship managers (RMs) ask questions over client account data, policies and product documents. The pilot covers 40 US Private Wealth RMs from January to March 2027. Full rollout, including the New York trust company and the Luxembourg subsidiary, is planned for July 2027. The business case is about $4.1M a year in RM time saved, of which the CFO counts about $2M as hard value.

In September 2026, the board's Risk Committee approved the pilot but made **full-rollout funding conditional on a quantified risk assessment and control plan by the end of March 2027**. In October 2026, during pre-pilot testing, an RM was shown another client's account balance. The cause was a search index that doesn't filter results by each RM's client entitlements; the fix is about three months away and won't be ready for the January pilot.

### 2.2 Problem Statement

Brindlemoor's CISO needs a way to show the board's Risk Committee, in dollars, how much financial exposure the RM copilot creates and which controls are worth funding. Full-rollout funding for 300 RMs, and the $4.1M-a-year productivity case, depends on it: the Committee requires a quantified risk assessment by the end of March 2027, and October's pre-pilot incident, in which an RM saw another client's balance, showed the exposure is real. Today, AI risk is rated on a qualitative red/amber/green register that cannot answer "what does high mean in dollars?", so control decisions, such as a proposed $250K-a-year AI firewall, rest on judgment rather than evidence.

### 2.3 Why Now

Five dates drive the timeline:

| Date | Event | Source |
|---|---|---|
| January 2027 | Pilot starts; the search index fix isn't ready | CISO interview |
| Mid-February 2027 | 2027 budget locks; later requests wait until July | CFO interview |
| End of March 2027 | Risk Committee deadline for the quantified assessment | Board condition |
| 15 April 2027 | NYDFS Part 500 annual certification for the NY trust company | Compliance interview |
| July 2027 | Full rollout, including Luxembourg (GDPR, EU AI Act) | Rollout plan |

### 2.4 What the Evidence Says

- A breach at a financial firm costs **$6.29M** on average (IBM 2026, ⚠️), more than six times the CISO's $1M yearly comfort level.
- Most incidents are small (median insurance claim **$110K**), but a few exceed **$5M** (Verizon 2026, ⚠️). A single average figure misleads; ranges are needed.
- Shadow AI is already present at Brindlemoor: about a third of pilot RMs have pasted client information into personal ChatGPT (RM lead interview). Industry-wide, shadow-AI breaches average about **$5.39M** (IBM 2026, ⚠️).

⚠️ = from secondary coverage; to be checked against the primary report. See `sources.md`.

---

## 3. Business Objectives

| ID | Objective | Measure | Owner |
|---|---|---|---|
| BO-1 | **Quantify the copilot's exposure in dollars** | Expected annual loss (EAL) and a 1-in-10-year loss (P90), as ranges: preliminary by **early February 2027**, final by **end of March 2027** | Daniel (CISO) |
| BO-2 | **Bring the copilot's risk within appetite** | EAL **under $1M** and P90 **under about $5M**, once the Risk Committee agrees these thresholds (OI-4) | Daniel (CISO) |
| BO-3 | **Protect the copilot's productivity case** | Friction cost from controls **under 10% of the ~$2M hard value**, about **$200K a year** | Marcus (RM lead) |
| BO-4 | **Have compliance evidence in time** | Evidence ready for the NYDFS certification (**15 April 2027**) and before the Luxembourg go-live (**July 2027**) | Rahul (Compliance) |
| BO-5 | **Fund only controls that pay off** | Every recommended control returns at least **$3 of risk reduction per $1 spent**; total fits the **~$400K** budget unless the return justifies more | Helen (CFO) |

**Why these measures:**
- BO-2 uses the risk appetite rather than a percentage cut, because the Risk Committee decides against thresholds. A 60% cut could still leave the bank above appetite.
- BO-3 is in dollars so it can be compared with the hard value Helen counts. As a check: at the most-likely inputs (2% false-block rate, 3 minutes lost, $95 an hour), friction is about **$107K a year**, within the limit. At the worst-case inputs (10 minutes, $130 an hour) it's about **$488K**, well over. The fast review path (PRD D-7) is what keeps the worst case down.

---

## 4. Stakeholders

| Stakeholder | Role in this initiative | What they need | Main tension |
|---|---|---|---|
| Daniel, CISO | Sponsor. Accountable for the BRD, the release, and accepting residual risk | A dollar-based assessment and control plan he can defend to the Risk Committee | Personally accountable if an incident follows |
| Risk Committee (incl. former actuary) | Accountable for setting risk appetite and approving full rollout | Exposure in dollars against an agreed appetite | Wants numbers, not ratings |
| Helen, CFO | Accountable for all control funding | Every control to clear a 3:1 return; ranges, not single numbers | Skeptical of security spend; budget locks mid-February |
| Rahul, Head of Compliance | Consulted; signs off compliance evidence | Evidence for NYDFS (April 15), GDPR and the EU AI Act (July) | Would rather block too much |
| Marcus, Head of US Private Wealth | Consulted; owns the productivity case | No more than about one block per RM per week; a fast path when blocked | Bonus tied to RM productivity |
| RMs (incl. Priya) | End users | Fast answers; never the wrong client's data | Already using personal ChatGPT |
| Commercial banking (150 RMs) | End users | **Not yet consulted (OI-1)** | Unknown |
| Platform team | Owns the search index fix | Clarity on what the interim control covers | Fix ~3 months out |

Full RACI: `docs/01-discovery/stakeholders-raci.md`. Disagreements: `docs/01-discovery/stakeholder-disagreements.md`.

---

## 5. Scope

*Pending.*

---

## 6. Business Case

*Pending.*

---

## 7. Regulatory Drivers

*Pending.*

---

## 8. Assumptions, Constraints and Risks

*Pending.*

---

## 9. Success Measures

*Pending.*

---

## 10. Approvals

*Pending.*

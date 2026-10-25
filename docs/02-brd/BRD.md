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

### In scope

- A **quantified risk assessment** of Brindlemoor Assist across **all 300 RMs** and all four business lines: Commercial banking, US Private Wealth, the New York trust company and Brindlemoor Wealth S.A. (Luxembourg). This matches the full rollout the Risk Committee is being asked to fund.
- **Interim runtime controls** to cover the gap before the search index fix, starting with the January 2027 pilot.
- A **comparison of control options**, including accepting the risk and the proposed vendor AI firewall, judged by dollars of risk reduced against cost.
- **Measurement of friction**: how often controls wrongly block legitimate RM work, and what that costs.
- The **shadow AI risk** created when RMs work around the copilot.
- **Compliance evidence**: control mapping, audit logs, and an EU AI Act classification memo.

**Commercial banking figures are provisional.** Its 150 RMs haven't been consulted (OI-1). Until they are, the assessment applies Private Wealth assumptions to them and labels those results provisional.

### Out of scope

| Item | Owner |
|---|---|
| Building the permission-aware search index fix (it's modelled, not built) | Platform team |
| The GDPR Data Protection Impact Assessment (this initiative supplies inputs) | Compliance and the Data Protection Officer |
| Due diligence on the copilot's model vendor | Third-party risk management |
| Other AI systems at the bank, and any client-facing AI | Future initiatives |
| Production deployment, single sign-on, high availability | IT, after the Risk Committee decision |
| Changes to the cyber insurance policy | CFO (OI-2) |

---

## 6. Business Case

> **Preliminary hand estimate** (calculation: `brd_estimate.py`). Every input below is a range from public benchmarks (`sources.md`) or an assumption, and the arithmetic is simple (average frequency × average cost per event). The FAIR model replaces these figures with simulated, measured results by **early February 2027**. Don't quote them as final.

### 6.1 Cost of inaction (accept the risk)

Full rollout, 300 RMs, no new controls. Per year.

| Scenario | Events per year (low / likely / high) | Cost per event (low / likely / high) | Expected annual loss | Basis |
|---|---|---|---|---|
| S1 Cross-client exposure | 2 / 6 / 15 | $50K / $150K / $750K | **$1.59M** | October incident; Verizon median claim $110K |
| S2 Injection-driven data theft | 0.05 / 0.2 / 0.5 | $1M / $4M / $15M | **$1.20M** | IBM financial-sector average $6.29M |
| S3 System prompt leak | 1 / 3 / 8 | $10K / $40K / $150K | **$0.19M** | Assumed |
| S4 Abuse and cost overrun | 2 / 4 / 10 | $5K / $20K / $75K | **$0.12M** | Assumed |
| S5 Shadow AI leak | 0.1 / 0.4 / 1.0 | $0.5M / $2M / $6M | **$1.09M** | RM lead poll; IBM shadow-AI average $5.39M |
| **Total** | | | **≈ $4.2M** | Range: $0.2M (everything goes well) to $26.7M (everything goes badly) |

**Against the appetite:** about **4×** the CISO's $1M threshold.

### 6.2 Options

| Option | Expected annual loss | Risk reduced | Annual cost (run + friction) | Return | Meets 3:1? | Friction vs. $2M hard value |
|---|---|---|---|---|---|---|
| A. Accept the risk | $4.2M | — | $0 | — | — | 0% |
| B. Vendor AI firewall | $3.7M | $0.5M | $410K ($250K + $160K) | 1.2 : 1 | ❌ | 8% |
| C. Gateway guardrails (GR-01 to GR-05) | $2.5M | $1.7M | $227K ($120K + $107K) | 7.6 : 1 | ✅ | 5% |
| D. Guardrails + search index fix | $2.2M | $2.0M | $277K ($170K + $107K) | 7.4 : 1 | ✅ | 5% |

Friction uses 1,125,000 queries a year, 3 minutes per false block and $95 an hour. Option D's cost includes about $50K a year for the index fix, assumed. In options B to D, S5 rises by 1.5× because false blocks push RMs toward personal AI tools (PRD FR-35, elasticity 0.5).

### 6.3 What the estimate says

1. **Doing nothing is about $4.2M a year**: over four times the appetite, and more than the copilot's $2M of hard value.
2. **Options C and D clear the CFO's 3:1 test and fit the $400K budget.**
3. **No option brings the bank within appetite.** The best leaves about $2.2M. The biggest remaining item is **shadow AI (S5)**, which the gateway can't reduce, and which rises slightly when controls add friction.

### 6.4 Limits of this estimate

- **The option comparison rests on assumed effectiveness.** The vendor firewall's effectiveness (60% on S2, 30% on S1, 3% false blocks) and our guardrails' (70–80%) are guesses, made by the team proposing the guardrails. **That's a bias risk.** The test harness measures both on the same test suite before any funding decision. On cost alone, the firewall is about twice as expensive per year.
- Run costs ($120K for the guardrails, $50K for the index fix) are assumed and need IT estimates.
- No insurance recovery is assumed (OI-2).
- Commercial banking figures are provisional (OI-1).

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

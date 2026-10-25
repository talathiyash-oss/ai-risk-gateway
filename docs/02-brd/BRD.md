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
| Shadow AI controls outside the copilot: web filtering, RM training, acceptable-use policy (a separate initiative; see §6.3) | Daniel (CISO), OI-5 |

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

**Recommendation:** fund Option C for the January pilot, adding the index fix (Option D) when it's ready, and launch a **separate shadow AI initiative owned by the CISO**: block personal AI sites on bank devices, train RMs (which also meets the EU AI Act's AI literacy duty in Luxembourg), and make the copilot the easiest approved option. BO-2 (within appetite) depends on both. The gateway alone can't get there.

### 6.4 Limits of this estimate

- **The option comparison rests on assumed effectiveness.** The vendor firewall's effectiveness (60% on S2, 30% on S1, 3% false blocks) and our guardrails' (70–80%) are guesses, made by the team proposing the guardrails. **That's a bias risk.** The test harness measures both on the same test suite before any funding decision. On cost alone, the firewall is about twice as expensive per year.
- Run costs ($120K for the guardrails, $50K for the index fix) are assumed and need IT estimates.
- No insurance recovery is assumed (OI-2).
- Commercial banking figures are provisional (OI-1).

---

## 7. Regulatory Drivers

| Rule | Applies to | What it means for the copilot, in plain terms | Key date | How this initiative helps |
|---|---|---|---|---|
| **NYDFS Part 500** (cybersecurity) | NY trust company | The trust company must assess and control cyber risk, and certify compliance each year. Penalties seen: $250K–$4.5M | **15 April 2027** certification | Gives Compliance a documented risk assessment, controls and audit logs to certify against |
| **GDPR** | Brindlemoor Wealth S.A. | A privacy impact assessment is needed before EU client data flows through the copilot. Keep only the personal data that's needed: Luxembourg's regulator mostly fines for this | **July 2027** go-live | Redacted audit logs (no raw client data); data-flow evidence for the privacy assessment |
| **EU AI Act** | Brindlemoor Wealth S.A. (as a user of AI) | The copilot is likely **not** high-risk; that reasoning needs to be written down. Staff using AI need AI literacy measures (enforced from August 2026). High-risk rules, if they applied, would start December 2027 | **July 2027** go-live | A written classification memo for Compliance; AI literacy covered by the shadow AI initiative's training |
| **Federal Reserve SR 26-2** (model risk) | Main bank (over $30B in assets) | Generative AI like the copilot is **outside** this guidance, but the bank must still govern it. The **risk model** built here is a quantitative model and likely **inside** it | Before the risk model's numbers are relied on | Reproducible test harness and documented model assumptions for Model Risk to validate |
| **Bank information security rules** (GLBA and interagency guidelines) | All US entities | Customer information must be protected with appropriate safeguards | Ongoing | Runtime controls on client data in prompts and answers |
| **NIST AI RMF, ISO/IEC 42001** | Whole bank (voluntary) | Recognized frameworks for managing AI risk; useful structure for auditors and the board | — | Each control mapped to them (PRD FR-27) |

Sources and dates: `sources.md` (G-1 to G-3, R-1 to R-4). Items marked ⚠️ there are still to be checked against primary sources.

---

## 8. Assumptions, Constraints and Risks

### Assumptions

| ID | Assumption | If wrong |
|---|---|---|
| BA-1 | The preliminary estimate's inputs (§6) are reasonable orders of magnitude | Business case numbers shift; the risk model replaces them in February |
| BA-2 | Daniel's thresholds (EAL < $1M, P90 < ~$5M) will be accepted by the Risk Committee as the appetite (OI-4) | BO-2's target changes |
| BA-3 | About $2M of the $4.1M business case is hard value (CFO) | BO-3's $200K friction limit changes |
| BA-4 | No insurance recovery for AI incidents (OI-2) | Net losses would be lower if covered |
| BA-5 | The search index fix arrives about three months after work starts | Option D's benefit starts later |
| BA-6 | Commercial banking RMs behave like Private Wealth RMs (OI-1) | Commercial figures change |

### Constraints

| ID | Constraint |
|---|---|
| BC-1 | Budget of about **$400K** for AI security controls in 2027; more needs a return the CFO accepts |
| BC-2 | Funding requests must reach the CFO before the **mid-February 2027** budget lock |
| BC-3 | The interim control must be ready for the **January 2027** pilot |
| BC-4 | Only 2 part-time AI security staff, with no quantitative risk experience |
| BC-5 | Prototype only: synthetic data, no production deployment before the Risk Committee decision |

### Project risks

| ID | Risk | Mitigation |
|---|---|---|
| PR-1 | Preliminary numbers miss the mid-February budget lock, so controls aren't funded until July | Deliver preliminary EAL and ROI by early February; share the §6 estimate with the CFO now |
| PR-2 | Benchmarks aren't verified against primary sources, and the actuary on the Risk Committee challenges them | Verify every ⚠️ figure before the March submission; show ranges and sources |
| PR-3 | The option comparison is biased toward the team's own guardrails (§6.4) | Measure all options, including the vendor firewall, on the same test suite |
| PR-4 | Model Risk asks to validate the risk model late, delaying the March submission | Engage Model Risk in the design phase (OI-3) |
| PR-5 | Commercial banking needs change the numbers or the controls | Interview a commercial banking lead before PRD sign-off (OI-1) |
| PR-6 | RMs reject the controls and move to personal AI tools | Friction cap, fast review path, shadow AI initiative |
| PR-7 | The Risk Committee doesn't agree a risk appetite in time | Propose Daniel's thresholds in the submission; show results against them either way |

---

## 9. Success Measures

| BO | The business will judge success by | When |
|---|---|---|
| BO-1 | The CFO receives preliminary EAL and ROI ranges before the budget lock, and the Risk Committee accepts the final assessment, including the actuary's "what does high mean in dollars?" question | Early February; end of March 2027 |
| BO-2 | Modeled EAL and P90, with the recommended controls and the shadow AI initiative, fall within the agreed appetite, or the CISO formally accepts the remaining risk | End of March 2027 |
| BO-3 | Measured friction cost stays under about $200K a year, in the test harness and in the pilot | End of pilot, March 2027 |
| BO-4 | Compliance files the NYDFS certification without an exception for the copilot, and the evidence pack is complete before Luxembourg goes live | 15 April 2027; July 2027 |
| BO-5 | The CFO approves funding before the budget lock, and every funded control shows at least 3:1 | Mid-February 2027 |

---

## 10. Approvals

*Pending.*

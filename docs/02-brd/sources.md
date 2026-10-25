# BRD Sources and Benchmarks

**Gathered:** 2026-10-25
**Verification key:** ✅ checked against the primary source · ⚠️ from secondary coverage (trade press, law firms, vendors); check the primary source before external use

The last column is for the product owner: one line on why each source matters to Brindlemoor (roadmap Task 2.1, Step 2).

## 1. Breach costs

| # | Source | Figure | Verified | Use in model | Why it matters to Brindlemoor |
|---|---|---|---|---|---|
| B-1 | IBM *Cost of a Data Breach 2026* (released 29 July 2026; 602 organizations, breaches March 2025–February 2026). Coverage: [Help Net Security](https://www.helpnetsecurity.com/2026/07/30/ibm-cost-of-a-data-breach-2026/), [eSecurity Planet](https://www.esecurityplanet.com/cybersecurity/ibm-2026-cost-of-a-data-breach-report-key-findings/), [Northdoor](https://www.northdoor.co.uk/about-us/resources/cost-of-a-data-breach-financial-services-2026/) | Financial services average **$6.29M** per breach (up from $5.56M in 2025); global average **$4.99M** | ⚠️ | Anchor for S1/S2 loss magnitude, as the upper part of the range | One average breach is more than 6× Daniel's $1M yearly comfort level, so a single incident would blow the risk appetite |
| B-2 | IBM 2026, shadow AI findings. Coverage: [Sentra](https://sentra.io/blog/ibm-cost-of-a-data-breach-2026-shadow-ai), [SureCloud](https://www.surecloud.com/blog-hub/shadow-ai-data-breach-cost-2026), [Kiteworks](https://www.kiteworks.com/cybersecurity-risk-management/ibm-2026-breach-report-ai-governance/) | Shadow-AI breaches averaged about **$5.39M** (up from $4.63M); shadow AI involved in a reported **43%** of incidents (up from 20%); **68%** of breached organizations had no AI governance | ⚠️ | S5 loss magnitude and frequency context | Shadow AI isn't hypothetical: a third of Marcus's pilot RMs already do it, so over-blocking pushes the bank toward a $5M+ risk |
| B-3 | Verizon *2026 Breach Impact Study* (with the 2026 DBIR; ~70,000 US cyber insurance claims, 2019–Oct 2025). Coverage: [SecurityInfoWatch](https://www.securityinfowatch.com/cybersecurity/news/55388513/verizon-business-study-finds-median-breach-costs-have-nearly-doubled-since-2019); report hub: [verizon.com/dbir](https://www.verizon.com/business/resources/reports/dbir/) | **Median** claim loss **$110K** (2024); top 2.5% of payouts **above $5M** | ⚠️ | Shape of the loss distribution: most incidents are small, a few are huge | A single figure like "$6.29M" misleads: most incidents are small and a few are huge, which is why Helen trusts ranges |

**Note for Phase 4 design.** B-1 (an *average* of $6.29M) and B-3 (a *median* of $110K) aren't contradictory. Breach losses are heavily skewed: a few very large events pull the average far above the typical case. A PERT range can understate that tail. The FAIR engine should consider a heavier-tailed distribution (e.g. lognormal) for loss magnitude. To be decided in Phase 4.

## 2. Regulatory penalties

| # | Source | Figure | Verified | Use in model | Why it matters to Brindlemoor |
|---|---|---|---|---|---|
| R-1 | NYDFS Part 500 penalty framework. [LexBlog](https://www.lexblog.com/?p=2360155), [Secure Controls Framework](https://securecontrolsframework.com/faqs/ny-dfs-part-500-penalties-non-compliance) | Up to $250,000 per day of violation or 1% of banking assets; set case by case | ⚠️ | Upper bound only; not a realistic estimate | See R-2 |
| R-2 | NYDFS Part 500 consent orders. [DFS enforcement actions](https://www.dfs.ny.gov/industry_guidance/enforcement_actions_lfs), [DFS press release (Order Express)](https://www.dfs.ny.gov/reports_and_publications/press_releases/pr20260805), [Goodwin (EyeMed)](https://www.goodwinlaw.com/en/insights/blogs/2022/11/nydfs-escalates-and-expands-cybersecurity-enforcement) | Examples: **$250K** (Order Express, 2026), **$1.2M** (bitFlyer USA, 2023), **$1.5M** (Residential Mortgage, 2021), **$4.5M** (EyeMed, 2022) | ⚠️ | Secondary loss range for the NY trust company: about $0.25M–$4.5M | Rahul must certify the NY trust company by April 15; a weak certification could add a $250K–$4.5M fine on top of the breach itself |
| R-3 | OCC penalty against Capital One (6 August 2020), after the 2019 breach. [Security Affairs](https://securityaffairs.com/posts/capital-one-fined), [Mondaq](https://mondaq.co.uk/unitedstates/financial-services/977444/occ-imposes-$80-million-penalty-in-connection-with-bank-data-breach) | **$80M** civil money penalty for failing to assess risk before a cloud migration (~100M people affected) | ⚠️ | Extreme tail for a US bank regulator penalty; far larger bank and breach than Brindlemoor's scenarios | Shows how large a regulator penalty can get, but Capital One was far bigger, so it's an extreme upper bound, not a forecast |
| R-4 | Luxembourg CNPD (GDPR). [Enforcement Tracker](https://www.enforcementtracker.com/ETid-2615), [CMS GDPR report](https://cms.law/en/int/publication/GDPR-Enforcement-Tracker-Report/luxembourg) | **€175,000** fine on a credit institution (6 January 2025) for late responses to data subject requests; CNPD's 2025 fines ranged €1,277–€175,000, mostly for data minimization and retention failures | ⚠️ | Secondary loss range for Brindlemoor Wealth S.A. GDPR fines can legally reach 4% of global turnover, but Luxembourg's actual fines on banks are modest | Luxembourg's fines were mostly for data minimization, exactly Rahul's logging worry, so GR-05's redacted logs address what this regulator actually punishes |

## 3. Regulatory changes since the design

| # | Source | Finding | Verified | Impact |
|---|---|---|---|---|
| G-1 | Federal Reserve **SR 26-2** (17 April 2026): [letter](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm), [guidance PDF](https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf) | **Supersedes and replaces SR 11-7.** Most relevant to banks over $30B in assets (Brindlemoor: ~$35B). Footnote 3: generative AI and agentic AI models "are not within the scope of this guidance," but the bank's risk management and governance practices should still determine appropriate controls for them. | ✅ | **All SR 11-7 references in the spec and PRD were outdated.** The copilot (generative AI) is *outside* SR 26-2's scope. The **FAIR engine itself** is a "complex quantitative method" producing estimates, so it's likely *inside* scope. The tool built to assess the AI is the part model risk guidance covers. |
| G-2 | EU **Digital Omnibus on AI**, Regulation (EU) 2026/1744 (published 24 July 2026, in force 27 July 2026). [Gibson Dunn](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/), [Orrick](https://www.orrick.com/en/Insights/2026/07/EU-AI-Act-Update-Digital-Omnibus-Finalizes-8-Compliance-Changes), [Morgan Lewis](https://www.morganlewis.com/pubs/2026/06/eu-approves-delays-and-other-amendments-to-certain-eu-ai-act-obligations-what-businesses-should-know) | Annex III high-risk obligations delayed from 2 August 2026 to **2 December 2027**. Article 50 transparency still applies from 2 August 2026. | ⚠️ | The copilot is still likely not high-risk. If it were, obligations would start December 2027, after Luxembourg's July 2027 go-live. |
| G-3 | Omnibus change to **Article 4 (AI literacy)**. [KI-Campus](https://ki-campus.org/en/blog/eu-ai-act-ai-omnibus-recalibrates-article-4-ai-literacy-remains-mandatory), [AI Act Monitor](https://www.aiactblog.nl/en/ai-act-monitor/article-4-measures-duty-updated-guidance) | Deployers must now "take measures" to support AI literacy, rather than ensure a sufficient level; still mandatory; national enforcement from 2 August 2026 | ⚠️ | Brindlemoor Wealth S.A. must train its 20 RMs before go-live and keep evidence. Lighter than before, still real. |

## 4. Friction inputs

| # | Source | Figure | Verified | Use in model | Why it matters to Brindlemoor |
|---|---|---|---|---|---|
| F-1 | PayScale, Private Banking Relationship Manager (US, 2026). [PayScale](https://www.payscale.com/research/US/Job=Private_Banking_Relationship_Manager/Salary/e8212d33/Banking) | Average base **~$84K**; total pay roughly **$57K–$188K**; experienced average base ~$99K | ⚠️ | Checks D-4's loaded hourly cost of $70 / $95 / $130. At ~1.3× for benefits over ~2,000 hours, $108K–$200K total pay gives about $70–$130 an hour. Most likely $95 implies ~$146K total pay, plausible for experienced Private Wealth RMs, high for commercial bankers. | The data is for private banking RMs; the 150 commercial bankers may earn differently, which is another reason to close the commercial banking gap (OI-1) |

## Not found

- **Per-record breach cost for financial services** (IBM 2026). The full IBM report is gated; secondary coverage doesn't report it.
- **2026 DBIR sector findings for finance and insurance.** Requires the full PDF.
- **A 2025–2026 NYDFS Part 500 consent order against a bank.** The most recent found involve non-bank licensees.

## Caveats

- Most figures come from secondary coverage because the primary reports are gated. Before the BRD goes to the "Risk Committee," the ⚠️ figures should be checked against the primary reports.
- Penalty examples come from different regulators, years and violation types. They give a *range*, not a prediction for Brindlemoor.

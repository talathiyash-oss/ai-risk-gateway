# Client Scenario: Brindlemoor Trust

Everything in this document is fictional. All figures are illustrative.

## The Bank

| Item | Value |
|---|---|
| **Name** | Brindlemoor Trust (holding company: Brindlemoor Financial Corp.) |
| **Name check** | FDIC BankFind API searched 2026-10-23 for "Brindlemoor" and "Brindle": 0 institutions found |
| **Headquarters** | Chicago, Illinois. Illinois-chartered bank |
| **Total assets** | ~$35 billion |
| **Employees** | ~3,500 |
| **Business lines** | Commercial banking (Midwest), US Private Wealth, Brindlemoor Trust Company of New York, Luxembourg wealth subsidiary |
| **Relationship managers** | 300 |
| **Client relationships served by RMs** | ~20,000 |

### Legal entities and regulators

| Entity | Role | Key regulators and rules |
|---|---|---|
| Brindlemoor Trust (Chicago) | Main bank | Federal Reserve, Illinois IDFPR, FDIC; GLBA; SR 11-7 |
| Brindlemoor Trust Company of New York | Trust and fiduciary services for US wealth clients | NYDFS (Part 500 applies to this entity) |
| Brindlemoor Wealth S.A. (Luxembourg) | Private banking for European clients | CSSF; GDPR; EU AI Act (as a deployer) |

### RMs by business line

| Business line | RMs | Clients per RM (approx.) | Clients |
|---|---|---|---|
| Commercial banking (Chicago/Midwest) | 150 | 60 | ~9,000 |
| US Private Wealth (Chicago) | 90 | 80 | ~7,200 |
| Brindlemoor Trust Company of New York | 40 | 80 | ~3,200 |
| Brindlemoor Wealth S.A. (Luxembourg) | 20 | 50 | ~1,000 |
| **Total** | **300** | | **~20,400** |

## The EU Subsidiary

- **Country:** Luxembourg
- **What it does:** private banking and wealth management for European clients, many of them family businesses with US ties
- **Size:** ~120 staff, 20 RMs, ~1,000 client relationships
- **Why it matters:** Luxembourg RMs join the copilot in Phase 2 (full rollout). From that date the subsidiary is a deployer under the EU AI Act, and EU client data flows through the copilot under GDPR.

## The Copilot Rollout

- **What it is:** an internal RAG assistant ("Brindlemoor Assist") that RMs use to ask questions over client account data, internal policies and product documents
- **Pilot:** 40 US Private Wealth RMs, January–March 2027
- **Full rollout:** all 300 RMs, including the NY trust company and Luxembourg, by July 2027
- **Expected queries:** 15 per RM per day, 250 working days → **1,125,000 queries a year** at full rollout
- **Business case:** saves about 3 hours of meeting preparation per RM per week → about **$4.1M a year** in productivity (300 RMs × 3 hours × 48 weeks × $95/hour)

## The Trigger

In September 2026, the board's Risk Committee approved the pilot but made **full-rollout funding conditional on a quantified risk assessment and control plan, due by the end of March 2027.** The Committee asked for exposure in dollars, not ratings.

In October 2026, during pre-pilot testing, a US Private Wealth RM preparing for a meeting asked the copilot about her client's portfolio and was shown **another client's account balance.** No data left the bank, and the issue was traced to the search index not filtering by RM entitlements. But it showed the Committee's concern was real.

The CISO now has to answer two questions by March 2027: *What is our dollar exposure from this copilot, and which controls are worth funding before full rollout?*

## Key Stakeholders

| Person | Role | Main concern |
|---|---|---|
| Daniel | CISO | Answer the Risk Committee in dollars, defensibly |
| Helen | CFO | Spend only where the risk reduction justifies it |
| Rahul | Head of Compliance | NYDFS, GDPR, EU AI Act and SR 11-7 evidence before Luxembourg goes live |
| Marcus | Head of US Private Wealth (RM lead) | Don't let security kill the $4.1M productivity case |
| Priya | Relationship Manager, US Private Wealth (pilot user) | Fast answers; never see the wrong client's data again |

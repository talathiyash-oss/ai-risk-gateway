# AI Risk Gateway

**A security gateway for an AI copilot, and a model that turns its protection into dollars.**

Brindlemoor Trust is a fictional US regional bank. It is rolling out an AI assistant that its 300 relationship managers (RMs) use to ask questions about their clients. The board won't fund the full rollout until the CISO can answer two questions:

1. **How much could this copilot cost us in a bad year?**
2. **Which protections are worth paying for?**

This project answers both. It is a working prototype with synthetic data. It was built as a portfolio project to show the full software development lifecycle, from stakeholder discovery to a working product.

## What's in it

| Part | What it does |
|---|---|
| **Security gateway** | Sits between the RMs and the copilot and checks every question and answer. Five guardrails: block prompt injection, remove personal data and other clients' records, stop the copilot revealing its instructions, cap usage, and log every decision. |
| **Review path** | When a legitimate question is wrongly blocked, the RM can ask for a quick review instead of hitting a dead end. |
| **Risk model (FAIR)** | FAIR (Factor Analysis of Information Risk) is an open standard for putting dollar figures on cyber risk. The model simulates 10,000 possible years and works out expected annual loss, the 1-in-10-year loss, and the return on each protection, including the cost of wrongly blocked questions. |
| **CISO dashboard** | Executive summary, loss curve, option comparison, what-if sliders, every input with its label and source, a compliance view, and a live demo. |

## Results so far

| Option | Expected loss a year | Annual cost | Return | Clears the CFO's 3:1 test? |
|---|---|---|---|---|
| Do nothing | $4.48M | n/a | n/a | n/a |
| Vendor AI firewall | $4.26M | $471K | 0.5 : 1 | No |
| Gateway guardrails | $2.96M | $263K | 5.8 : 1 | Yes |
| Search index fix only* | $3.14M | $52K | 25.8 : 1 | Yes |
| Gateway + index fix | $2.67M | $314K | 5.8 : 1 | Yes |

- **No option alone brings the bank within its proposed risk appetite.** With the gateway options, the biggest remaining loss is shadow AI: RMs pasting client data into personal AI tools.
- **The index fix is the best value once it exists, but it won't be ready for the January pilot, so the gateway is the interim control.** Adding the gateway on top of the fix returns only about 1.8 : 1.

\* The index fix's cost is an estimate the platform team hasn't confirmed, and the fix won't be ready for the January 2027 pilot (PRD A-6).

> **Read these numbers as provisional.**
> - Control effectiveness is still **Assumed**, because the attack test suite hasn't been built yet.
> - 32 of the model's 37 inputs are assumptions. Each one is labelled and sourced in the dashboard.
> - The figures are model outputs, not forecasts.

## Run it

Prerequisites: Python 3.11 or newer, about 1 GB of free disk space, and network access for the first setup.

```bash
./scripts/setup.sh                                  # one-time setup
.venv/bin/streamlit run src/airg/dashboard/app.py   # the dashboard
```

Other entry points:

```bash
.venv/bin/python scripts/demo_sprint1.py   # attacks with the gateway off vs on
.venv/bin/python scripts/run_fair.py       # the risk model as a table
.venv/bin/pytest -q                        # the test suite
```

## How it was built

The project followed a consulting-style SDLC: discovery interviews with four stakeholders (CISO, CFO, Head of Compliance, RM lead), a problem statement and RACI, a business requirements document, a product requirements document with a traceability matrix, then build sprints. Each sprint task was built test-first and reviewed twice, once against the spec and once for quality.

The discovery interviews were **role-played**. The four stakeholders are fictional: the interviews were held by voice, with AI playing each stakeholder. The prompts are in `docs/01-discovery/`.

**Roles.**
- **Yash Talathi, product owner:** ran the role-played discovery interviews, made every product and scope decision, and directed and reviewed all documents.
- **Claude (Anthropic) via Claude Code:** drafted the documents with Yash, implemented the code, and ran the test-first build with spec and quality reviews.

**Sprints.** Sprint 1 is the gateway, Sprint 2B the FAIR model, and Sprint 3 the dashboard. Sprint 2A, the attack test suite, isn't built yet.

Every decision, with the options considered and the reasons, is in `docs/decision-log.md`. The product decisions are also in the PRD's decision log (`docs/03-prd/PRD.md` §6).

## Repository map

| Path | Contents |
|---|---|
| `docs/00-scenario.md` | The fictional bank, its people and numbers |
| `docs/01-discovery/` | Interview findings, problem statement, RACI, stakeholder disagreements |
| `docs/02-brd/` | Business requirements document and research sources |
| `docs/03-prd/` | Product requirements document and traceability matrix |
| `docs/open-items.md` | Open items and gate decisions |
| `src/airg/` | Gateway, guardrails, audit log, review queue, API |
| `src/airg/fair/` | The FAIR risk model |
| `src/airg/dashboard/` | The dashboard |
| `config/` | Gateway settings and risk model inputs |
| `results/fair.json` | Latest risk model output |

## Known limits

- Synthetic data and a simulated copilot, not a real LLM.
- No authentication: user IDs are passed in requests.
- Control effectiveness is Assumed until the attack test suite (Sprint 2A) runs.
- The business requirements still await CFO and CISO review.
- Framework clause references are drafts that still need checking against primary sources.

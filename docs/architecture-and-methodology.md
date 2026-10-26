# Architecture and Methodology

How the AI Risk Gateway works, and how its numbers are produced. For *why* each choice was made, see `decision-log.md`.

---

## 1. System at a glance

```
RM question
   │
   ▼
┌──────────────────────────── AI Security Gateway ────────────────────────────┐
│ input stage     GR-04 rate limit → GR-01 injection → GR-03 → GR-02 PII redact │
│ retrieve        copilot searches client records and bank documents           │
│ chunks stage    GR-01 drops poisoned documents · GR-02 drops other clients'   │
│                 records (D-9)                                                │
│ generate        simulated copilot writes an answer                           │
│ output stage    GR-03 blocks system-prompt leaks · GR-02 redacts cross-client │
│                 identifiers (defence in depth)                               │
│ GR-05 audit     one redacted log entry per request; fail closed               │
└──────────────────────────────────────────────────────────────────────────────┘
   │ allowed, redacted, or blocked (403 / 429 / 502 / 503)
   ▼
RM   ──(GR-01 false positive?)──► review queue: a reviewer reruns the request,
                                  skipping only the blocking guard and stage

FAIR risk model ◄── scenario inputs (config/fair_model.yaml)
                ◄── control effectiveness (harness results when they exist, otherwise Assumed)
        │
        ▼
results/fair.json ──► CISO dashboard (Streamlit) and scripts/run_fair.py
```

## 2. Components

| Component | Module | What it does |
|---|---|---|
| Synthetic data | `airg.data` | 60 fictional clients across 12 RMs, generated from a fixed seed (FR-13) |
| Simulated copilot | `airg.copilot` | Keyword retrieval with no entitlement filter. It obeys injected instructions and reveals its system prompt when asked. **Deliberately unsafe**, so there is a measurable baseline (FR-14) |
| Configuration | `airg.config` | Guardrail on/off switches, fail modes (D-1), and options, with strict validation |
| PII redactor | `airg.redaction` | Microsoft Presidio with the small spaCy model, plus a recognizer for Brindlemoor account numbers |
| GR-01 Prompt injection | `airg.guardrails.injection` | Pattern detection on prompts. Removes retrieved documents that contain instructions (FR-05, FR-06) |
| GR-02 Sensitive information | `airg.guardrails.pii` | Redacts PII in prompts, drops other clients' records before generation (D-9), and redacts cross-client identifiers in answers (FR-07, FR-08) |
| GR-03 System prompt leakage | `airg.guardrails.prompt_leak` | Blocks answers containing the canary or close copies of system-prompt sentences (FR-09) |
| GR-04 Rate limits | `airg.guardrails.rate_limit` | Per-user requests per minute and tokens per day; thread-safe (FR-10) |
| GR-05 Audit log | `airg.audit` | JSON Lines file. Every text field is scrubbed, including client names and the canary. Atomic retention purge and range export (FR-11, FR-12) |
| Policy engine | `airg.pipeline` | Runs the guards stage by stage, applies fail modes, and audits every outcome, including copilot errors (FR-01 to FR-04) |
| Review queue | `airg.reviews` | Only GR-01 blocks are reviewable. No self-approval. Race-safe. Held questions expire (FR-34, D-7) |
| API | `airg.api` | FastAPI endpoints for chat and reviews. Block messages reveal no detection detail (NFR-06) |
| FAIR engine | `airg.fair` | Monte Carlo risk model (section 4) |
| Dashboard | `airg.dashboard` | Pure data, compliance and what-if modules, with a thin Streamlit layer (FR-23 to FR-29) |

## 3. Security design choices

- **Fail modes (D-1).** GR-01, 02, 03 and 05 fail closed. GR-04 fails open. A crashed guard returns 503, so it can't be mistaken for a reviewable policy block.
- **Defence in depth.** GR-02 removes other clients' records before the copilot sees them. Its output check then catches anything that still gets through.
- **No detection detail to the user.** Blocked responses carry only a reference ID. Guard IDs and reasons stay in the audit log.
- **The review path can't release protected assets.** GR-03 (system prompt) blocks are final. An approved review skips only the one guard *and stage* that blocked, and the skip is recorded as an override in the audit log.
- **The audit log minimises data (GDPR).** Personal data, client names and the canary are replaced before anything is written. A log write failure blocks the request.

## 4. Risk model (FAIR) methodology

**FAIR** (Factor Analysis of Information Risk) expresses risk as *how often a loss happens × how much it costs*.

### 4.1 Scenarios

| ID | Scenario | Gateway controls that act on it |
|---|---|---|
| S1 | Cross-client exposure (the October incident) | GR-02, and the index fix (FR-31) |
| S2 | Injection-driven data theft | GR-01, GR-02 |
| S3 | System prompt leak | GR-03 |
| S4 | Abuse and cost overrun | GR-04 |
| S5 | Shadow AI: RMs pasting client data into personal AI tools | None directly. **It gets worse as false blocks increase** (D-8, FR-35) |

### 4.2 Inputs

- **Frequency** (events per year) and **control effectiveness** are PERT ranges (minimum, most likely, maximum).
- **Loss per incident** is a lognormal fitted to a 90% range (D-11), because breach costs are heavily skewed.
- **Every input carries a label:** Measured, Benchmarked or Assumed. The engine refuses to run if any input is unlabelled (FR-18). Today 32 of the 37 inputs are Assumed.

### 4.3 Control effectiveness

**Vulnerability** is the share of attack attempts that still succeed with a control in place.

- **Measured:** the block rate relative to the unprotected baseline, with a 95% interval. The interval is Wilson when the baseline always succeeds and Katz when it doesn't. A baseline with fewer than 10 successes is too thin to use.
- **Otherwise:** the strategy's assumed block rate.
- **Either way:** the rate is widened by an "attackers adapt" factor of 0%, 15% or 40% (D-5). This applies to *every* option, measured or not (D-12).

### 4.4 Simulation

The model runs 10,000 simulated years. In each year it:

1. Draws potential loss events for each scenario at the *unprotected* rate.
2. Gives each event a loss and a random number.
3. Decides whether an option stops the event: it does if the event's random number is above the option's Vulnerability (**thinning**).
4. For S5, adds extra shadow-AI events in proportion to false blocks (**superposition**).

Every random component uses its own fixed-size stream, so **every option faces the same simulated years and the same incidents.** Differences between options come from the controls, not from chance (common random numbers). One honest caveat: effectiveness is redrawn each year, which narrows the tails. A two-level simulation would be the rigorous version.

### 4.5 Outputs (FR-21, FR-22, FR-33)

| Output | Meaning |
|---|---|
| **Expected annual loss** | The average across simulated years |
| **1-in-10-year loss (P90)** | The loss exceeded in about 1 year in 10 |
| **Loss exceedance curve** | The chance that a year's losses exceed $X |
| **Cost** | Run cost plus **friction**: false-block rate × queries × minutes lost × RM hourly cost |
| **Return (average year)** | Risk reduced per $1 of cost. The CFO's test is 3 : 1. Risk reduced is net of any extra shadow-AI loss the option causes |
| **Year-to-year range** | The spread of return across years. It shows how lumpy the payoff is, not uncertainty in the average |
| **"Worse than nothing"** | The share of years in which an option loses more than doing nothing |
| **Incremental returns** | What each add-on buys, e.g. the gateway on top of the index fix ≈ 1.8 : 1 |

### 4.6 Reproducibility (NFR-03)

The same seed gives a byte-identical `results/fair.json`. The NumPy version is not yet pinned (sprint notes F-3).

## 5. Measurement plan (Sprint 2A, not yet built)

- A deterministic suite of 100 attacks per category and 1,000 benign questions, split 60/40 between tuning and hold-out (D-3).
- Outcome-based scoring: an attack succeeds only if the attacker got what they were after (D-10).
- A results file in the contract described in the Sprint 2B plan. The FAIR engine picks it up automatically.

Until this exists, control effectiveness is Assumed, and the dashboard says so.

## 6. Testing approach

- **Test-first:** every task in every sprint started with a failing test.
- **Two reviews per task:** spec compliance first, then quality. Fixes were re-reviewed.
- **A cross-cutting final review per sprint**, which probed the running system with real attacks and seed sweeps.
- **270 automated tests**, covering unit logic, the end-to-end pipeline, the API, statistical properties of the model, and dashboard smoke tests (Streamlit AppTest).

## 7. Known limits

- **Prototype scope:** a simulated copilot, synthetic data, and no authentication.
- **Assumed numbers:** control effectiveness, and most model inputs, are Assumed. The business requirements still await CFO and CISO review (GD-2).
- **Unbuilt pieces:** GR-06 (link stripping) is planned but not built. The per-guardrail dashboard view, input values, and some what-if controls are deferred (OI-6 to OI-9).
- **Unverified references:** framework clause references are drafts that still need checking against primary sources.

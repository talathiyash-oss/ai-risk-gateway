# AI Risk Gateway: Delivery Roadmap and Phase 1–3 Plan

> **For agentic workers:** Phases 1–3 are run interactively with the product owner, not by subagents. The code-level plan for Phases 4–7 is written with superpowers:writing-plans at the Phase 4 gate, from the signed PRD. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Take the AI Risk Gateway from business problem to signed PRD, so that the build (Phases 4–7) starts from requirements the product owner wrote and approved.

**Approach:** Claude plays the stakeholders (CISO, CFO, Head of Compliance, RM lead) and coaches. The product owner writes every document in Phases 1–3. Each phase ends at a gate, and the next phase doesn't start until the product owner signs off.

**Spec:** `docs/superpowers/specs/2026-10-23-ai-risk-gateway-design.md`

**Why the code plan is deferred:** The build depends on PRD decisions: fail-open or fail-closed per guardrail, acceptance criteria, test suite size, dashboard requirements. Planning code before those decisions exist would let engineering set product requirements.

---

## Roadmap

| Phase | Output | Gate | Planned in |
|---|---|---|---|
| 1. Discovery | Problem statement, stakeholder map, RACI | Problem agreed | This file |
| 2. Business case | BRD | BRD sign-off | This file |
| 3. Requirements | PRD, traceability matrix | PRD sign-off | This file |
| 4. Design | Technical design, FAIR model spec, verified control register | Design approval | Code plan, written at this gate |
| 5. Build | 3 sprints with demos | Sprint reviews | Code plan |
| 6. Test & UAT | Test plan, results, UAT sign-off | Acceptance | Code plan |
| 7. Release | README, CISO brief, demo, resume bullets | Done | Code plan |

---

## Phase 1: Discovery

**You'll learn:** how to run a stakeholder interview, and how to separate the problem from someone's preferred solution.
**Interview question to master:** "How do you start an engagement when the client already has a solution in mind?"

### Task 1.1: Name the client

**Files:**
- Create: `docs/00-scenario.md`

- [x] **Step 1:** Choose a fictional bank name. Search it plus "bank" and check the FDIC BankFind database to confirm no real institution uses it.
- [x] **Step 2:** Write `docs/00-scenario.md` with: bank name, size (assets, number of RMs, number of clients), US footprint, the EU subsidiary (country, what it does), and the copilot rollout plan (pilot group, timeline). Claude reviews it to make sure the numbers are consistent.
- [x] **Step 3:** Commit: `git add docs/00-scenario.md && git commit -m "docs: define client scenario"`

### Task 1.2: Prepare the interview

**Files:**
- Create: `docs/01-discovery/interview-guide.md`

- [x] **Step 1:** Write 8–12 open questions for the CISO, grouped into: current state, pain, what triggered this, constraints (budget, timeline, regulators), and what success looks like.
- [x] **Step 2:** Claude reviews them and flags leading questions (ones that suggest an answer) and closed yes/no questions.
- [x] **Step 3:** Revise and commit: `git commit -am "docs: discovery interview guide"` (use `git add` first for the new file).
  *Done as `interview-cheat-sheet.md` plus the role-play prompt `ciso-roleplay-prompt.md`; the interview ran by voice on 2026-10-25.*

### Task 1.3: Run the interviews

**Files:**
- Create: `docs/01-discovery/interview-notes.md`

- [x] **Step 1:** Interview Claude-as-CISO (about 20 minutes, in chat). Take notes in your own words.
- [ ] **Step 2:** Short interviews (5 questions each) with Claude-as-CFO, Claude-as-Head of Compliance, and Claude-as-RM lead. Expect them to disagree. The RM lead will push back on friction.
- [ ] **Step 3:** At the end of the notes, list where the stakeholders disagree. Commit.

### Task 1.4: Problem statement, stakeholder map, RACI

**Files:**
- Create: `docs/01-discovery/problem-statement.md`
- Create: `docs/01-discovery/stakeholders-raci.md`

- [x] **Step 1:** Write the problem statement in this format: *"[Who] needs a way to [do what] because [why it matters, with evidence]. Today, [current workaround and its cost]."* Keep it under 120 words, and don't name a solution.
- [x] **Step 2:** Stakeholder map: a power/interest grid listing each stakeholder's main concern.
- [x] **Step 3:** RACI table. Rows: the 7 SDLC phases plus "accept residual risk" and "fund controls." Columns: CISO, CFO, Head of Compliance, RM lead, Product owner, Engineering. Each row has exactly one **A** (Accountable).
- [x] **Step 4:** Claude-as-CISO reviews it. **Gate: problem agreed.** Commit: `git commit -m "docs: phase 1 discovery complete"`

---

## Phase 2: Business Case (BRD)

**You'll learn:** how to tie a technology project to business objectives and frame a business case without having the final numbers yet.
**Interview question to master:** "What's the difference between a BRD and a PRD?" (Answer: a BRD covers *why* and *what the business gets*; a PRD covers *what the product must do*.)

### Task 2.1: Research benchmarks

**Files:**
- Create: `docs/02-brd/sources.md`

- [ ] **Step 1:** Claude gathers current figures with links: IBM *Cost of a Data Breach* (financial sector average cost and per-record cost), sample NYDFS Part 500 penalties, Verizon DBIR figures for the financial sector, and the current EU AI Act timeline. Claude flags anything it couldn't verify.
- [ ] **Step 2:** You read each source summary and note in one line why it matters to the Bank. Commit.

### Task 2.2: Write the BRD

**Files:**
- Create: `docs/02-brd/BRD.md`

- [ ] **Step 1:** Write these sections, using the coaching notes:

  | Section | What goes in it | Coaching note |
  |---|---|---|
  | 1. Executive summary | 5 sentences | Write it last |
  | 2. Background & problem | From Task 1.4 | Cite the sources from Task 2.1 |
  | 3. Business objectives | 3–5 objectives (e.g. BO-1, BO-2) | Each one specific and measurable, with no technology in it |
  | 4. Stakeholders | From the RACI | Include what each stakeholder needs from this |
  | 5. Scope | In / out, at business level | Out of scope matters as much as in scope |
  | 6. Business case | Cost of inaction vs. investment, as ranges | The FAIR engine later replaces these estimates with measured ranges |
  | 7. Regulatory drivers | Applicability table from the spec §5 | Business language, not clause IDs |
  | 8. Assumptions, constraints, risks | Each with an ID | Risks to the *project*, not to the bank |
  | 9. Success measures | How the business will judge it | Must trace back to section 3 |
  | 10. Approvals | Sign-off table | |

- [ ] **Step 2:** Claude-as-CFO reviews it, pushing on whether the business case is believable.
- [ ] **Step 3:** Claude-as-CISO reviews it, pushing on whether the scope is right.
- [ ] **Step 4:** Revise. **Gate: BRD signed off.** Commit: `git commit -m "docs: BRD v1.0 signed off"`

---

## Phase 3: Requirements (PRD + Traceability)

**You'll learn:** how to write requirements an engineer can build and a tester can verify, and how to make trade-offs explicitly.
**Interview question to master:** "How do you write a good acceptance criterion?" (Answer: it's testable, has a pass/fail result, and uses Given/When/Then.)

### Task 3.1: Personas and user stories

**Files:**
- Create: `docs/03-prd/PRD.md` (sections 1–3)

- [ ] **Step 1:** Write 3 personas: an RM (end user), the CISO (buyer), and a compliance analyst (auditor). For each: goals, frustrations, and what "good" looks like to them.
- [ ] **Step 2:** Write 10–15 user stories in the form *"As a [persona], I want [capability], so that [outcome]."* Each gets an ID (US-01, US-02, …) and a BO-x link back to the BRD.
- [ ] **Step 3:** Prioritize them with MoSCoW (Must / Should / Could / Won't). Claude-as-RM-lead challenges every Must.

### Task 3.2: Requirements and decisions

**Files:**
- Modify: `docs/03-prd/PRD.md` (sections 4–7)

- [ ] **Step 1:** Functional requirements (FR-01, FR-02, …). Each has at least one Given/When/Then acceptance criterion. Example:
  *FR-03: Given GR-02 is enabled, when the copilot response contains another client's account number, then the gateway redacts it and logs a GR-02 event.*
- [ ] **Step 2:** Non-functional requirements (NFR-01, …): latency added by the gateway, availability, auditability, synthetic-data-only.
- [ ] **Step 3:** Decision log. Each entry records options, your decision, and why:
  - D-1: fail-open or fail-closed, per guardrail
  - D-2: the highest acceptable false-positive rate before a guardrail is considered too disruptive
  - D-3: test suite size per OWASP category
  - D-4: RM loaded hourly rate and minutes lost per block (feeds the friction cost)
- [ ] **Step 4:** Success metrics. Product metrics (e.g. EAL reduction, block rate, false-positive rate) separate from business metrics (traced back to BRD section 9).
- [ ] **Step 5:** Out of scope, taken from spec §3.

### Task 3.3: Traceability matrix

**Files:**
- Create: `docs/03-prd/traceability-matrix.md`

- [ ] **Step 1:** Build a table with columns: BO-x → US-x → FR/NFR-x → Test case ID (TC-x, placeholder IDs; the test cases themselves come in Phase 6) → Control ID (GR-x).
- [ ] **Step 2:** Check that every BO has at least one FR and every Must story has at least one FR. Any row with a gap is either a missing requirement or scope creep. Decide which and fix it.

### Task 3.4: PRD sign-off

- [ ] **Step 1:** Claude-as-engineering lead reviews: is each requirement buildable and unambiguous? Flags vague words ("fast," "secure," "user-friendly").
- [ ] **Step 2:** Revise. **Gate: PRD signed off.** Commit: `git commit -m "docs: PRD v1.0 and traceability matrix signed off"`
- [ ] **Step 3:** Claude writes the Phase 4–7 code plan with superpowers:writing-plans, using the signed PRD as the source of requirements and acceptance criteria.

---

## Spec Coverage Check

| Spec section | Covered by |
|---|---|
| §1 Purpose, §9 Resume framing | Roadmap; Phase 7 in the code plan |
| §2 Scenario | Task 1.1 |
| §3 Architecture, failure behavior | D-1 in Task 3.2; Phase 4 design |
| §4 FAIR model | Task 2.1 benchmarks, D-4 friction inputs; Phase 4–5 build |
| §5 Control mapping | BRD section 7; traceability Control ID column; Phase 4 verification |
| §6 SDLC plan | This roadmap |
| §7 Testing | Acceptance criteria (Task 3.2), TC IDs (Task 3.3); Phase 6 |
| §8 Repo layout | `docs/` structure used here; `src/` set up in the code plan |

# Sprint 2B: FAIR Risk Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Monte Carlo FAIR engine that turns scenario inputs and control effectiveness into Expected Annual Loss, a 1-in-10-year loss, a loss exceedance curve, and ROI per strategy (including friction), with every input labelled Measured, Benchmarked or Assumed.

PRD scope: FR-18, FR-19, FR-20, FR-21, FR-22, FR-33, FR-35, NFR-03. Decisions: D-4, D-5, D-8, D-11.

**Architecture:** The engine is a small package, `airg.fair`, with one module per job:
- `distributions`: PERT and lognormal sampling.
- `inputs`: loads the model and validates its labels.
- `effectiveness`: turns block rates into Vulnerability ranges.
- `simulate`: simulated years.
- `report`: EAL, percentiles, ROI, flags.

Inputs live in `config/fair_model.yaml`, taken from the BRD §6 estimate. Control effectiveness comes from the harness results file when it exists (Sprint 2A). Otherwise each strategy's assumed block rates are used, labelled Assumed. So the engine runs today and upgrades automatically once the harness exists.

**Tech Stack:** Python 3.12, NumPy (already installed as a Presidio dependency; declared explicitly here), PyYAML, pytest.

**Harness results contract (what Sprint 2A must write to `results/harness.json`):**
```
{
  "run_id": str,
  "rate_limit": {"abusive": {"n", "count", "rate", "ci95": [lo, hi]}},
  "strategies": {
    <name>: {"splits": {"holdout": {
      "attacks": {<category>: {"success": {"n", "count", "rate", "ci95"}}},
      "benign": {"false_positive": {"n", "count", "rate", "ci95"}}
    }}}
  }
}
```
- Strategy names: `all_off`, `all_on`, `permission_aware_only`, `all_on_permission_aware`.
- Categories: `LLM01-direct`, `LLM01-indirect`, `LLM02-cross-client`, `LLM07-system-prompt`, `LLM05-exfiltration`.

**Model choices made here:**

| Choice | Detail |
|---|---|
| Loss events | Poisson per simulated year, with rate = unprotected events per year × Vulnerability |
| Loss per event | Lognormal fitted so its 5th and 95th percentiles equal the 90% range (D-11) |
| Common random numbers | Every strategy uses the same seeds per scenario, so differences between strategies aren't sampling noise |
| Measured block rate | Relative to the unprotected baseline: `1 − success_rate(strategy) / success_rate(all_off)`, pooled over the scenario's categories. It is then widened by D-5's degradation. Assumed block rates aren't widened again, because they're already judgment. |
| Insurance | None is assumed (PRD A-7) |

FR-19's acceptance criterion says constant inputs give EAL equal to frequency × magnitude "exactly". Event counts are Poisson by design, so the test checks it within 1% at 200,000 iterations, and the PRD wording is updated to match.

---

## File Structure

```
pyproject.toml                    MODIFY: add numpy
src/airg/stats.py                 CREATE: wilson_interval (shared with Sprint 2A)
src/airg/fair/__init__.py         CREATE
src/airg/fair/distributions.py    CREATE: PERT, lognormal 90% range
src/airg/fair/inputs.py           CREATE: model dataclasses, loader, label validation (FR-18)
src/airg/fair/effectiveness.py    CREATE: Vulnerability ranges, false-positive rates (FR-20)
src/airg/fair/simulate.py         CREATE: Monte Carlo, shadow-AI multiplier (FR-19, FR-35)
src/airg/fair/report.py           CREATE: summaries, friction, ROI, flags, provenance (FR-21, FR-22, FR-33)
config/fair_model.yaml            CREATE: inputs from BRD §6
scripts/run_fair.py               CREATE: run and print; writes results/fair.json
tests/conftest.py                 MODIFY: synthetic_harness fixture
tests/test_fair_distributions.py, test_fair_inputs.py, test_fair_effectiveness.py,
tests/test_fair_simulate.py, test_fair_report.py
```

Run all commands from `/Users/yash/Projects/ai-risk-gateway`, on branch `sprint-2b`, which is already created.

---

### Task 1: Distributions and the Wilson interval

**Files:**
- Modify: `pyproject.toml`
- Create: `src/airg/stats.py`, `src/airg/fair/__init__.py`, `src/airg/fair/distributions.py`
- Test: `tests/test_fair_distributions.py`

- [ ] **Step 1: Add NumPy to `pyproject.toml` dependencies.** Insert `"numpy>=1.26",` after `"presidio-anonymizer>=2.2",`. Then run `.venv/bin/pip install -q -e ".[dev]"`.

- [ ] **Step 2: Write the failing tests `tests/test_fair_distributions.py`**

```python
import math

import numpy as np
import pytest

from airg.fair.distributions import Z90, lognormal, lognormal_params, pert, pert_mean
from airg.stats import wilson_interval


def rng():
    return np.random.default_rng(1)


def test_pert_degenerate_is_constant():
    assert np.all(pert(rng(), 5, 5, 5, 100) == 5)


def test_pert_stays_in_bounds_and_matches_mean():
    x = pert(rng(), 1, 3, 10, 200_000)
    assert x.min() >= 1 and x.max() <= 10
    assert x.mean() == pytest.approx(pert_mean(1, 3, 10), rel=0.01)


def test_pert_rejects_bad_order():
    with pytest.raises(ValueError):
        pert(rng(), 3, 1, 10, 10)


def test_lognormal_params_from_90_range():
    mu, sigma = lognormal_params(100, 10_000)
    assert mu == pytest.approx(math.log(1_000))
    assert sigma == pytest.approx(math.log(100) / (2 * Z90))


def test_lognormal_hits_its_90_range():
    x = lognormal(rng(), 50_000, 750_000, 200_000)
    assert np.percentile(x, 5) == pytest.approx(50_000, rel=0.03)
    assert np.percentile(x, 95) == pytest.approx(750_000, rel=0.03)


def test_lognormal_degenerate_is_constant():
    assert lognormal(rng(), 1_000, 1_000, 10) == pytest.approx(np.full(10, 1_000.0))


def test_wilson_interval_matches_prd_example():
    lo, hi = wilson_interval(37, 40)
    assert (round(lo, 3), round(hi, 3)) == (0.801, 0.974)


def test_wilson_interval_empty():
    assert wilson_interval(0, 0) == (0.0, 1.0)
```

- [ ] **Step 3: Run to verify failure.** `.venv/bin/pytest tests/test_fair_distributions.py -q` fails with `ModuleNotFoundError: No module named 'airg.fair'`.

- [ ] **Step 4: Write `src/airg/stats.py`**

```python
"""Small statistics helpers shared by the harness and the FAIR engine."""
from __future__ import annotations

import math


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a proportion (PRD FR-16)."""
    if n == 0:
        return 0.0, 1.0
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)
```

- [ ] **Step 5: Write `src/airg/fair/__init__.py`**

```python
"""FAIR (Factor Analysis of Information Risk) engine: Monte Carlo annual loss per strategy."""
```

- [ ] **Step 6: Write `src/airg/fair/distributions.py`**

```python
"""Sampling helpers: PERT ranges for frequencies and effectiveness, lognormal 90% ranges for
loss per incident (D-11)."""
from __future__ import annotations

import math

import numpy as np

Z90 = 1.6448536269514722  # standard normal z at the 95th percentile


def pert(rng: np.random.Generator, low: float, mode: float, high: float, size: int) -> np.ndarray:
    if not low <= mode <= high:
        raise ValueError(f"PERT needs low <= mode <= high, got {low}, {mode}, {high}")
    if high == low:
        return np.full(size, float(low))
    alpha = 1 + 4 * (mode - low) / (high - low)
    beta = 1 + 4 * (high - mode) / (high - low)
    return low + rng.beta(alpha, beta, size) * (high - low)


def pert_mean(low: float, mode: float, high: float) -> float:
    return (low + 4 * mode + high) / 6


def lognormal_params(p05: float, p95: float) -> tuple[float, float]:
    """Lognormal mu and sigma whose 5th and 95th percentiles are p05 and p95."""
    if not 0 < p05 <= p95:
        raise ValueError(f"lognormal 90% range needs 0 < p05 <= p95, got {p05}, {p95}")
    mu = (math.log(p05) + math.log(p95)) / 2
    sigma = (math.log(p95) - math.log(p05)) / (2 * Z90)
    return mu, sigma


def lognormal(rng: np.random.Generator, p05: float, p95: float, size: int) -> np.ndarray:
    mu, sigma = lognormal_params(p05, p95)
    if sigma == 0:
        return np.full(size, math.exp(mu))
    return rng.lognormal(mu, sigma, size)
```

- [ ] **Step 7: Run to verify pass.** `.venv/bin/pytest tests/test_fair_distributions.py -q` gives `8 passed`. Then run `.venv/bin/pytest -q`; all tests must pass.

- [ ] **Step 8: Commit.**
```bash
git add pyproject.toml src/airg/stats.py src/airg/fair/__init__.py src/airg/fair/distributions.py tests/test_fair_distributions.py
git commit -m "feat: FAIR distributions and Wilson interval"
```

---

### Task 2: Model inputs and label validation (FR-18)

**Files:**
- Create: `src/airg/fair/inputs.py`, `config/fair_model.yaml`
- Test: `tests/test_fair_inputs.py`

- [ ] **Step 1: Write the failing tests `tests/test_fair_inputs.py`**

```python
import pytest
import yaml

from airg.fair.inputs import load_model

MODEL = "config/fair_model.yaml"


def test_repo_model_loads():
    m = load_model(MODEL)
    assert (m.iterations, m.seed) == (10_000, 2027)
    assert [s.scenario_id for s in m.scenarios] == ["S1", "S2", "S3", "S4", "S5"]
    assert [s.strategy_id for s in m.strategies] == [
        "accept_risk", "vendor_firewall", "gateway", "index_fix", "gateway_plus_index_fix"]
    assert m.shadow_ai.scenario_id == "S5"
    assert (m.appetite_eal, m.appetite_p90, m.funding_ratio) == (1_000_000, 5_000_000, 3)


def broken(tmp_path, mutate):
    raw = yaml.safe_load(open(MODEL))
    mutate(raw)
    path = tmp_path / "model.yaml"
    path.write_text(yaml.safe_dump(raw))
    return path


def test_missing_provenance_is_refused(tmp_path):
    path = broken(tmp_path, lambda r: r["scenarios"][0]["events_per_year"].pop("provenance"))
    with pytest.raises(ValueError, match="S1.events_per_year"):
        load_model(path)


def test_missing_source_is_refused(tmp_path):
    path = broken(tmp_path, lambda r: r["scenarios"][1]["loss_per_event"].pop("source"))
    with pytest.raises(ValueError, match="S2.loss_per_event: source"):
        load_model(path)


def test_unknown_provenance_is_refused(tmp_path):
    path = broken(tmp_path, lambda r: r["degradation"].update(provenance="Guessed"))
    with pytest.raises(ValueError, match="degradation: provenance"):
        load_model(path)


def test_out_of_order_range_is_refused(tmp_path):
    path = broken(tmp_path, lambda r: r["scenarios"][0]["events_per_year"].update(low=100))
    with pytest.raises(ValueError, match="low <= mode <= high"):
        load_model(path)


def test_accept_risk_strategy_is_required(tmp_path):
    path = broken(tmp_path, lambda r: r["strategies"].pop(0))
    with pytest.raises(ValueError, match="accept_risk"):
        load_model(path)
```

- [ ] **Step 2: Run to verify failure.** `.venv/bin/pytest tests/test_fair_inputs.py -q` fails with a ModuleNotFoundError.

- [ ] **Step 3: Write `src/airg/fair/inputs.py`**

```python
"""FAIR model inputs (FR-18). Every input carries a provenance label (Measured, Benchmarked or
Assumed) and a source or rationale; the loader refuses to run without them."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

PROVENANCE = ("Measured", "Benchmarked", "Assumed")


@dataclass(frozen=True)
class Pert:
    low: float
    mode: float
    high: float
    provenance: str
    source: str


@dataclass(frozen=True)
class Range90:
    p05: float
    p95: float
    provenance: str
    source: str


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    name: str
    events_per_year: Pert
    loss_per_event: Range90
    harness_categories: tuple[str, ...]


@dataclass(frozen=True)
class Strategy:
    strategy_id: str
    name: str
    harness_strategy: str | None
    annual_run_cost: Pert
    assumed_block_rates: dict[str, Pert] = field(default_factory=dict)
    assumed_false_positive_rate: Pert | None = None


@dataclass(frozen=True)
class Friction:
    annual_queries: int
    queries_source: str
    minutes_lost: Pert
    hourly_cost: Pert


@dataclass(frozen=True)
class ShadowAI:
    scenario_id: str
    elasticity: Pert
    reference_fp_rate: float


@dataclass(frozen=True)
class Model:
    iterations: int
    seed: int
    scenarios: tuple[Scenario, ...]
    strategies: tuple[Strategy, ...]
    friction: Friction
    shadow_ai: ShadowAI
    degradation: Pert
    appetite_eal: float
    appetite_p90: float
    funding_ratio: float
    friction_limit: float


def _label(raw: dict, where: str) -> tuple[str, str]:
    provenance = raw.get("provenance")
    if provenance not in PROVENANCE:
        raise ValueError(f"{where}: provenance must be one of {PROVENANCE}, got {provenance!r}")
    source = raw.get("source")
    if not source:
        raise ValueError(f"{where}: source is required")
    return provenance, str(source)


def _pert(raw, where: str) -> Pert:
    if not isinstance(raw, dict):
        raise ValueError(f"{where}: expected low, mode, high, provenance and source")
    try:
        low, mode, high = float(raw["low"]), float(raw["mode"]), float(raw["high"])
    except KeyError as missing:
        raise ValueError(f"{where}: missing {missing.args[0]}") from None
    if not low <= mode <= high:
        raise ValueError(f"{where}: needs low <= mode <= high")
    return Pert(low, mode, high, *_label(raw, where))


def _range90(raw, where: str) -> Range90:
    if not isinstance(raw, dict):
        raise ValueError(f"{where}: expected p05, p95, provenance and source")
    try:
        p05, p95 = float(raw["p05"]), float(raw["p95"])
    except KeyError as missing:
        raise ValueError(f"{where}: missing {missing.args[0]}") from None
    if not 0 < p05 <= p95:
        raise ValueError(f"{where}: needs 0 < p05 <= p95")
    return Range90(p05, p95, *_label(raw, where))


def _parse(raw: dict) -> Model:
    scenarios = tuple(
        Scenario(
            scenario_id=s["id"],
            name=s["name"],
            events_per_year=_pert(s.get("events_per_year"), f"{s['id']}.events_per_year"),
            loss_per_event=_range90(s.get("loss_per_event"), f"{s['id']}.loss_per_event"),
            harness_categories=tuple(s.get("harness_categories") or ()),
        )
        for s in raw["scenarios"])
    strategies = tuple(
        Strategy(
            strategy_id=st["id"],
            name=st["name"],
            harness_strategy=st.get("harness_strategy"),
            annual_run_cost=_pert(st.get("annual_run_cost"), f"{st['id']}.annual_run_cost"),
            assumed_block_rates={
                sid: _pert(p, f"{st['id']}.assumed_block_rates.{sid}")
                for sid, p in (st.get("assumed_block_rates") or {}).items()},
            assumed_false_positive_rate=(
                _pert(st["assumed_false_positive_rate"], f"{st['id']}.assumed_false_positive_rate")
                if st.get("assumed_false_positive_rate") else None),
        )
        for st in raw["strategies"])
    if "accept_risk" not in [st.strategy_id for st in strategies]:
        raise ValueError("strategies: an 'accept_risk' baseline strategy is required")
    friction = raw["friction"]
    shadow = raw["shadow_ai"]
    if shadow["scenario"] not in [s.scenario_id for s in scenarios]:
        raise ValueError(f"shadow_ai: unknown scenario {shadow['scenario']}")
    appetite = raw["appetite"]
    return Model(
        iterations=int(raw["iterations"]),
        seed=int(raw["seed"]),
        scenarios=scenarios,
        strategies=strategies,
        friction=Friction(int(friction["annual_queries"]), str(friction["queries_source"]),
                          _pert(friction["minutes_lost"], "friction.minutes_lost"),
                          _pert(friction["hourly_cost"], "friction.hourly_cost")),
        shadow_ai=ShadowAI(shadow["scenario"], _pert(shadow["elasticity"], "shadow_ai.elasticity"),
                           float(shadow["reference_fp_rate"])),
        degradation=_pert(raw.get("degradation"), "degradation"),
        appetite_eal=float(appetite["eal"]),
        appetite_p90=float(appetite["p90"]),
        funding_ratio=float(raw["funding_ratio"]),
        friction_limit=float(raw["friction_limit"]),
    )


def load_model(path: str | Path) -> Model:
    return _parse(yaml.safe_load(Path(path).read_text()))
```

- [ ] **Step 4: Write `config/fair_model.yaml`**

```yaml
# FAIR model inputs for Brindlemoor Assist (PRD FR-18). Every value carries a provenance label.
# Values come from the BRD §6 preliminary estimate and docs/02-brd/sources.md, and are
# provisional until the deferred BRD reviews (gate decision GD-2).
iterations: 10000
seed: 2027

appetite:            # CISO's proposed thresholds, not yet agreed by the Risk Committee (OI-4)
  eal: 1000000
  p90: 5000000
funding_ratio: 3     # CFO's test: at least $3 of risk reduction per $1 spent
friction_limit: 200000   # BRD BO-3: friction under 10% of ~$2M hard value

degradation: {low: 0.0, mode: 0.15, high: 0.40, provenance: Assumed,
              source: "PRD D-5: real attackers adapt beyond the test suite"}

friction:
  annual_queries: 1125000
  queries_source: "Scenario doc: 300 RMs x 15 queries/day x 250 days"
  minutes_lost: {low: 1, mode: 3, high: 10, provenance: Assumed,
                 source: "PRD D-4: 1 min to rephrase, up to 10 min to find the answer another way"}
  hourly_cost: {low: 70, mode: 95, high: 130, provenance: Benchmarked,
                source: "PayScale 2026 RM total pay x 1.3 / 2,000 hours (sources.md F-1)"}

shadow_ai:
  scenario: S5
  elasticity: {low: 0.0, mode: 0.5, high: 1.5, provenance: Assumed,
               source: "PRD FR-35: how strongly false blocks push RMs to personal AI tools"}
  reference_fp_rate: 0.02

scenarios:
  - id: S1
    name: Cross-client exposure
    harness_categories: [LLM02-cross-client]
    events_per_year: {low: 2, mode: 6, high: 15, provenance: Assumed,
                      source: "October pre-pilot incident; 300 RMs without entitlement filtering"}
    loss_per_event: {p05: 50000, p95: 750000, provenance: Benchmarked,
                     source: "Verizon 2026 median claim $110K (sources.md B-3); NYDFS fines R-2"}
  - id: S2
    name: Injection-driven data theft
    harness_categories: [LLM01-direct, LLM01-indirect, LLM05-exfiltration]
    events_per_year: {low: 0.05, mode: 0.2, high: 0.5, provenance: Assumed,
                      source: "External attacker needs a working injection path; rare"}
    loss_per_event: {p05: 1000000, p95: 15000000, provenance: Benchmarked,
                     source: "IBM 2026 financial-sector average $6.29M (sources.md B-1)"}
  - id: S3
    name: System prompt leak
    harness_categories: [LLM07-system-prompt]
    events_per_year: {low: 1, mode: 3, high: 8, provenance: Assumed,
                      source: "Curious users and red-teamers"}
    loss_per_event: {p05: 10000, p95: 150000, provenance: Assumed,
                     source: "Investigation and prompt rework; no client data"}
  - id: S4
    name: Abuse and cost overrun
    harness_categories: [rate_limit]
    events_per_year: {low: 2, mode: 4, high: 10, provenance: Assumed,
                      source: "Scripted use from compromised accounts"}
    loss_per_event: {p05: 5000, p95: 75000, provenance: Assumed,
                     source: "LLM spend and service disruption"}
  - id: S5
    name: Shadow AI leak
    harness_categories: []
    events_per_year: {low: 0.1, mode: 0.4, high: 1.0, provenance: Assumed,
                      source: "RM lead poll: a third of pilot RMs use personal ChatGPT"}
    loss_per_event: {p05: 500000, p95: 6000000, provenance: Benchmarked,
                     source: "IBM 2026 shadow-AI breach average ~$5.39M (sources.md B-2)"}

strategies:
  - id: accept_risk
    name: Accept the risk
    harness_strategy: null
    annual_run_cost: {low: 0, mode: 0, high: 0, provenance: Assumed, source: "No new controls"}

  - id: vendor_firewall
    name: Vendor AI firewall
    harness_strategy: null
    annual_run_cost: {low: 250000, mode: 250000, high: 250000, provenance: Benchmarked,
                      source: "Vendor quote reported in the CISO interview"}
    assumed_block_rates:
      S1: {low: 0.15, mode: 0.30, high: 0.45, provenance: Assumed, source: "Generic PII filter; not entitlement-aware (BRD §6.4)"}
      S2: {low: 0.40, mode: 0.60, high: 0.75, provenance: Assumed, source: "Vendor injection filter (BRD §6.4)"}
      S3: {low: 0.30, mode: 0.50, high: 0.70, provenance: Assumed, source: "BRD §6.4"}
    assumed_false_positive_rate: {low: 0.02, mode: 0.03, high: 0.05, provenance: Assumed, source: "BRD §6.2"}

  - id: gateway
    name: Gateway guardrails
    harness_strategy: all_on
    annual_run_cost: {low: 80000, mode: 120000, high: 180000, provenance: Assumed,
                      source: "Hosting plus part-time tuning; needs an IT estimate (BRD §6.4)"}
    assumed_block_rates:
      S1: {low: 0.60, mode: 0.70, high: 0.85, provenance: Assumed, source: "BRD §6.2, used until harness results exist"}
      S2: {low: 0.60, mode: 0.75, high: 0.90, provenance: Assumed, source: "BRD §6.2, used until harness results exist"}
      S3: {low: 0.70, mode: 0.80, high: 0.95, provenance: Assumed, source: "BRD §6.2, used until harness results exist"}
      S4: {low: 0.70, mode: 0.80, high: 0.95, provenance: Assumed, source: "BRD §6.2, used until harness results exist"}
    assumed_false_positive_rate: {low: 0.01, mode: 0.02, high: 0.03, provenance: Assumed, source: "PRD D-2 cap"}

  - id: index_fix
    name: Search index fix only
    harness_strategy: permission_aware_only
    annual_run_cost: {low: 30000, mode: 50000, high: 80000, provenance: Assumed,
                      source: "Platform team estimate needed (BRD §6.2)"}
    assumed_block_rates:
      S1: {low: 0.70, mode: 0.85, high: 0.95, provenance: Assumed, source: "Root-cause fix for the October incident"}

  - id: gateway_plus_index_fix
    name: Gateway + index fix
    harness_strategy: all_on_permission_aware
    annual_run_cost: {low: 110000, mode: 170000, high: 260000, provenance: Assumed,
                      source: "Gateway plus index fix run costs"}
    assumed_block_rates:
      S1: {low: 0.80, mode: 0.90, high: 0.97, provenance: Assumed, source: "Both layers"}
      S2: {low: 0.60, mode: 0.75, high: 0.90, provenance: Assumed, source: "As gateway"}
      S3: {low: 0.70, mode: 0.80, high: 0.95, provenance: Assumed, source: "As gateway"}
      S4: {low: 0.70, mode: 0.80, high: 0.95, provenance: Assumed, source: "As gateway"}
    assumed_false_positive_rate: {low: 0.01, mode: 0.02, high: 0.03, provenance: Assumed, source: "As gateway"}
```

- [ ] **Step 5: Run to verify pass.** `.venv/bin/pytest tests/test_fair_inputs.py -q` gives `6 passed`. The full suite must pass.

- [ ] **Step 6: Commit.**
```bash
git add src/airg/fair/inputs.py config/fair_model.yaml tests/test_fair_inputs.py
git commit -m "feat: FAIR model inputs with provenance validation (FR-18)"
```

---

### Task 3: Control effectiveness (FR-20)

**Files:**
- Create: `src/airg/fair/effectiveness.py`
- Modify: `tests/conftest.py` (append the fixture)
- Test: `tests/test_fair_effectiveness.py`

- [ ] **Step 1: Append to `tests/conftest.py`**

```python


@pytest.fixture
def synthetic_harness():
    """A minimal results file in the Sprint 2A contract, for FAIR tests."""
    def rate(n, count, lo, hi):
        return {"n": n, "count": count, "rate": round(count / n, 4), "ci95": [lo, hi]}
    return {
        "run_id": "abc123",
        "rate_limit": {"abusive": rate(600, 580, 0.95, 0.98)},
        "strategies": {
            "all_off": {"splits": {"holdout": {
                "attacks": {"LLM02-cross-client": {"success": rate(40, 40, 0.912, 1.0)}},
                "benign": {"false_positive": rate(400, 0, 0.0, 0.0095)}}}},
            "all_on": {"splits": {"holdout": {
                "attacks": {"LLM02-cross-client": {"success": rate(40, 4, 0.04, 0.231)}},
                "benign": {"false_positive": rate(400, 8, 0.0102, 0.039)}}}},
        },
    }
```

- [ ] **Step 2: Write the failing tests `tests/test_fair_effectiveness.py`**

```python
import pytest

from airg.fair.effectiveness import (NO_CONTROL, false_positive_rate, measured_block_rate,
                                     vulnerabilities, vulnerability_from_block_rate)
from airg.fair.inputs import Pert, load_model
from airg.stats import wilson_interval

DEGRADATION = Pert(0.0, 0.15, 0.40, "Assumed", "D-5")


@pytest.fixture
def model():
    return load_model("config/fair_model.yaml")


def strategy(model, sid):
    return next(s for s in model.strategies if s.strategy_id == sid)


def test_prd_fr20_example():
    v = vulnerability_from_block_rate(0.925, (0.801, 0.974), DEGRADATION, "test")
    assert (round(v.low, 3), round(v.mode, 3), round(v.high, 3)) == (0.026, 0.214, 0.519)
    assert v.provenance == "Measured"


def test_measured_block_rate_is_relative_to_baseline(synthetic_harness):
    block, (lo, hi) = measured_block_rate(synthetic_harness, "all_on", ("LLM02-cross-client",))
    wlo, whi = wilson_interval(4, 40)
    assert block == pytest.approx(0.9)
    assert (lo, hi) == (pytest.approx(1 - whi), pytest.approx(1 - wlo))


def test_rate_limit_block_rate_only_for_gateway_strategies(synthetic_harness):
    assert measured_block_rate(synthetic_harness, "all_on", ("rate_limit",)) == (0.9667, (0.95, 0.98))
    assert measured_block_rate(synthetic_harness, "permission_aware_only", ("rate_limit",)) is None


def test_missing_categories_give_no_measurement(synthetic_harness):
    assert measured_block_rate(synthetic_harness, "all_on", ("LLM01-direct",)) is None


def test_vulnerabilities_use_measured_values_when_available(model, synthetic_harness):
    v = vulnerabilities(model, strategy(model, "gateway"), synthetic_harness)
    assert v["S1"].provenance == "Measured"
    assert v["S4"].provenance == "Measured"
    assert v["S2"].provenance == "Assumed"
    assert v["S5"] == NO_CONTROL


def test_vulnerabilities_fall_back_to_assumed(model):
    v = vulnerabilities(model, strategy(model, "gateway"), None)
    assert (v["S1"].low, v["S1"].mode, v["S1"].high) == pytest.approx((0.15, 0.30, 0.40))
    assert all(v[s].provenance == "Assumed" for s in ("S1", "S2", "S3", "S4"))


def test_accept_risk_has_no_protection(model):
    assert set(vulnerabilities(model, strategy(model, "accept_risk"), None).values()) == {NO_CONTROL}


def test_false_positive_rates(model, synthetic_harness):
    measured = false_positive_rate(strategy(model, "gateway"), synthetic_harness)
    assert (measured.low, measured.mode, measured.high, measured.provenance) == (0.0102, 0.02, 0.039, "Measured")
    assert false_positive_rate(strategy(model, "gateway"), None).provenance == "Assumed"
    accept = false_positive_rate(strategy(model, "accept_risk"), None)
    assert (accept.low, accept.mode, accept.high) == (0.0, 0.0, 0.0)
```

- [ ] **Step 3: Run to verify failure.** `.venv/bin/pytest tests/test_fair_effectiveness.py -q` fails with a ModuleNotFoundError.

- [ ] **Step 4: Write `src/airg/fair/effectiveness.py`**

```python
"""Control effectiveness as Vulnerability ranges (FR-20, D-5).

Vulnerability is the share of attack attempts that still succeed with a strategy in place
(1.0 means no protection). Measured values come from the harness hold-out results (FR-17),
relative to the unprotected baseline, and are widened by the adaptive-attacker degradation (D-5).
Without harness results, a strategy's assumed block rates are used and labelled Assumed. They're
already judgment, so they aren't widened again. A scenario a strategy doesn't address gets 1.0.
"""
from __future__ import annotations

from airg.fair.inputs import Model, Pert, Strategy
from airg.stats import wilson_interval

NO_CONTROL = Pert(1.0, 1.0, 1.0, "Assumed", "No control in this strategy addresses this scenario")
NO_BLOCKING = Pert(0.0, 0.0, 0.0, "Assumed", "Strategy adds no blocking")
RATE_LIMIT = "rate_limit"
GATEWAY_STRATEGIES = frozenset({"all_on", "all_on_permission_aware"})


def _clip(x: float) -> float:
    return min(1.0, max(0.0, x))


def vulnerability_from_block_rate(block: float, block_ci95: tuple[float, float],
                                  degradation: Pert, source: str) -> Pert:
    lo, hi = block_ci95
    return Pert(_clip(1 - hi * (1 - degradation.low)),
                _clip(1 - block * (1 - degradation.mode)),
                _clip(1 - lo * (1 - degradation.high)),
                "Measured", source)


def _pooled_success(harness: dict, strategy_name: str, categories) -> tuple[int, int] | None:
    run = harness.get("strategies", {}).get(strategy_name)
    if run is None:
        return None
    attacks = run["splits"]["holdout"]["attacks"]
    rows = [attacks[c]["success"] for c in categories if c in attacks]
    if not rows:
        return None
    return sum(r["n"] for r in rows), sum(r["count"] for r in rows)


def measured_block_rate(harness: dict, strategy_name: str, categories) -> tuple[float, tuple[float, float]] | None:
    """Pooled hold-out block rate relative to the unprotected baseline, with an approximate
    95% interval, or None if the harness didn't measure it."""
    if RATE_LIMIT in categories:
        abusive = harness.get("rate_limit", {}).get("abusive")
        if abusive is None or strategy_name not in GATEWAY_STRATEGIES:
            return None
        return abusive["rate"], (abusive["ci95"][0], abusive["ci95"][1])
    baseline = _pooled_success(harness, "all_off", categories)
    current = _pooled_success(harness, strategy_name, categories)
    if baseline is None or current is None or baseline[1] == 0:
        return None
    p_off = baseline[1] / baseline[0]
    n, k = current
    lo, hi = wilson_interval(k, n)
    return _clip(1 - (k / n) / p_off), (_clip(1 - hi / p_off), _clip(1 - lo / p_off))


def vulnerabilities(model: Model, strategy: Strategy, harness: dict | None = None) -> dict[str, Pert]:
    out: dict[str, Pert] = {}
    for scenario in model.scenarios:
        sid = scenario.scenario_id
        if sid == model.shadow_ai.scenario_id:
            out[sid] = NO_CONTROL
            continue
        measured = None
        if harness is not None and strategy.harness_strategy and scenario.harness_categories:
            measured = measured_block_rate(harness, strategy.harness_strategy, scenario.harness_categories)
        if measured is not None:
            block, ci = measured
            source = f"Harness run {harness['run_id']}, strategy {strategy.harness_strategy}, hold-out set"
            out[sid] = vulnerability_from_block_rate(block, ci, model.degradation, source)
        elif sid in strategy.assumed_block_rates:
            b = strategy.assumed_block_rates[sid]
            out[sid] = Pert(1 - b.high, 1 - b.mode, 1 - b.low, b.provenance, b.source)
        else:
            out[sid] = NO_CONTROL
    return out


def false_positive_rate(strategy: Strategy, harness: dict | None = None) -> Pert:
    if harness is not None and strategy.harness_strategy in harness.get("strategies", {}):
        fp = harness["strategies"][strategy.harness_strategy]["splits"]["holdout"]["benign"]["false_positive"]
        return Pert(fp["ci95"][0], fp["rate"], fp["ci95"][1], "Measured",
                    f"Harness run {harness['run_id']}, hold-out benign set")
    if strategy.assumed_false_positive_rate is not None:
        return strategy.assumed_false_positive_rate
    return NO_BLOCKING
```

- [ ] **Step 5: Run to verify pass.** `.venv/bin/pytest tests/test_fair_effectiveness.py -q` gives `8 passed`. The full suite must pass.

- [ ] **Step 6: Commit.**
```bash
git add src/airg/fair/effectiveness.py tests/conftest.py tests/test_fair_effectiveness.py
git commit -m "feat: FAIR control effectiveness from harness or assumptions (FR-20)"
```

---

### Task 4: Monte Carlo simulation (FR-19, FR-35)

**Files:**
- Create: `src/airg/fair/simulate.py`
- Test: `tests/test_fair_simulate.py`

- [ ] **Step 1: Write the failing tests `tests/test_fair_simulate.py`**

```python
import dataclasses

import numpy as np
import pytest

from airg.fair.inputs import Pert, Range90, load_model
from airg.fair.simulate import shadow_ai_multiplier, simulate_losses


def one(v):
    return Pert(v, v, v, "Assumed", "test")


def constant_model(iterations=200_000):
    m = load_model("config/fair_model.yaml")
    s1 = dataclasses.replace(m.scenarios[0], events_per_year=one(4.0),
                             loss_per_event=Range90(10_000, 10_000, "Assumed", "test"))
    s5 = dataclasses.replace(m.scenarios[4], events_per_year=one(1.0),
                             loss_per_event=Range90(1_000, 1_000, "Assumed", "test"))
    return dataclasses.replace(m, iterations=iterations, scenarios=(s1, s5),
                               shadow_ai=dataclasses.replace(m.shadow_ai, elasticity=one(1.0)))


FULL = {"S1": one(1.0), "S5": one(1.0)}


def test_constant_inputs_give_frequency_times_magnitude():
    losses, _ = simulate_losses(constant_model(), FULL, one(0.0))
    assert losses["S1"].mean() == pytest.approx(4 * 10_000, rel=0.01)


def test_vulnerability_scales_frequency():
    losses, _ = simulate_losses(constant_model(), {**FULL, "S1": one(0.5)}, one(0.0))
    assert losses["S1"].mean() == pytest.approx(2 * 10_000, rel=0.01)


def test_shadow_ai_rises_with_false_blocks():
    m = constant_model()
    base, _ = simulate_losses(m, FULL, one(0.0))
    more, fp = simulate_losses(m, FULL, one(0.02))
    assert more["S5"].mean() == pytest.approx(2 * base["S5"].mean(), rel=0.02)
    assert np.all(fp == 0.02)


def test_multiplier_formula():
    assert shadow_ai_multiplier(np.array([0.0, 0.02]), np.array([1.0, 1.0]), 0.02).tolist() == [1.0, 2.0]


def test_same_seed_is_reproducible():
    m = constant_model(1_000)
    a, _ = simulate_losses(m, FULL, one(0.0))
    b, _ = simulate_losses(m, FULL, one(0.0))
    assert all(np.array_equal(a[k], b[k]) for k in a)


def test_different_seed_differs():
    m = constant_model(1_000)
    a, _ = simulate_losses(m, FULL, one(0.0), seed=1)
    b, _ = simulate_losses(m, FULL, one(0.0), seed=2)
    assert not np.array_equal(a["S1"], b["S1"])


def test_scenarios_use_independent_streams():
    m = constant_model(1_000)
    a, _ = simulate_losses(m, FULL, one(0.0))
    b, _ = simulate_losses(m, {**FULL, "S5": one(0.5)}, one(0.0))
    assert np.array_equal(a["S1"], b["S1"])
```

- [ ] **Step 2: Run to verify failure.** `.venv/bin/pytest tests/test_fair_simulate.py -q` fails with a ModuleNotFoundError.

- [ ] **Step 3: Write `src/airg/fair/simulate.py`**

```python
"""Monte Carlo annual loss (FR-19, FR-35, D-11).

Each iteration is one simulated year. A scenario's loss-event count is Poisson with rate
= events per year x Vulnerability; each event's loss is lognormal, fitted to its 90% range.
Shadow AI (S5) frequency rises with the strategy's false-block rate (FR-35).

Every scenario draws from its own random stream, seeded the same way for every strategy
(common random numbers), so differences between strategies aren't sampling noise.
"""
from __future__ import annotations

import numpy as np

from airg.fair.distributions import lognormal, pert
from airg.fair.inputs import Model, Pert


def _draw(rng: np.random.Generator, p: Pert, n: int) -> np.ndarray:
    return pert(rng, p.low, p.mode, p.high, n)


def shadow_ai_multiplier(fp_rate: np.ndarray, elasticity: np.ndarray, reference_fp_rate: float) -> np.ndarray:
    return 1 + elasticity * fp_rate / reference_fp_rate


def simulate_losses(model: Model, vulnerabilities: dict[str, Pert], fp_rate: Pert,
                    seed: int | None = None) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Annual loss per scenario (one value per simulated year) and the false-block rate draws."""
    n = model.iterations
    streams = np.random.SeedSequence(model.seed if seed is None else seed).spawn(len(model.scenarios) + 1)
    shared = np.random.default_rng(streams[0])
    fp = _draw(shared, fp_rate, n)
    elasticity = _draw(shared, model.shadow_ai.elasticity, n)
    losses: dict[str, np.ndarray] = {}
    for scenario, stream in zip(model.scenarios, streams[1:]):
        rng = np.random.default_rng(stream)
        rate = _draw(rng, scenario.events_per_year, n) * _draw(rng, vulnerabilities[scenario.scenario_id], n)
        if scenario.scenario_id == model.shadow_ai.scenario_id:
            rate = rate * shadow_ai_multiplier(fp, elasticity, model.shadow_ai.reference_fp_rate)
        counts = rng.poisson(rate)
        draws = lognormal(rng, scenario.loss_per_event.p05, scenario.loss_per_event.p95, int(counts.sum()))
        total = np.zeros(n)
        np.add.at(total, np.repeat(np.arange(n), counts), draws)
        losses[scenario.scenario_id] = total
    return losses, fp
```

- [ ] **Step 4: Run to verify pass.** `.venv/bin/pytest tests/test_fair_simulate.py -q` gives `7 passed`. The full suite must pass.

- [ ] **Step 5: Commit.**
```bash
git add src/airg/fair/simulate.py tests/test_fair_simulate.py
git commit -m "feat: FAIR Monte Carlo with lognormal losses and shadow-AI link (FR-19, FR-35)"
```

---

### Task 5: Results, ROI and strategy comparison (FR-21, FR-22, FR-33)

**Files:**
- Create: `src/airg/fair/report.py`
- Test: `tests/test_fair_report.py`

- [ ] **Step 1: Write the failing tests `tests/test_fair_report.py`**

```python
import dataclasses

import pytest

from airg.fair.inputs import PROVENANCE, load_model
from airg.fair.report import friction_cost, run_model


@pytest.fixture(scope="module")
def model():
    return dataclasses.replace(load_model("config/fair_model.yaml"), iterations=5_000)


@pytest.fixture(scope="module")
def results(model):
    return run_model(model)


def test_friction_cost_prd_example():
    assert friction_cost(0.01, 1_125_000, 3, 95) == pytest.approx(53_437.50)


def test_baseline_has_no_reduction(results):
    accept = results["strategies"]["accept_risk"]
    assert accept["risk_reduction"] == 0
    assert accept["reduction_to_cost"] is None
    assert accept["meets_funding_test"] is False


def test_every_strategy_has_the_outputs(results):
    for s in results["strategies"].values():
        assert s["p10"] <= s["p50"] <= s["p90"]
        assert set(s["eal_by_scenario"]) == {"S1", "S2", "S3", "S4", "S5"}
        probabilities = [point["probability"] for point in s["loss_exceedance"]]
        assert probabilities == sorted(probabilities, reverse=True)


def test_gateway_reduces_expected_loss(results):
    assert results["strategies"]["gateway"]["eal"] < results["strategies"]["accept_risk"]["eal"]


def test_flags_follow_thresholds(results, model):
    for s in results["strategies"].values():
        if s["reduction_to_cost"] is not None:
            assert s["meets_funding_test"] == (s["reduction_to_cost"] >= model.funding_ratio)
        assert s["within_appetite"] == (s["eal"] < model.appetite_eal and s["p90"] < model.appetite_p90)
        assert s["friction_within_limit"] == (s["friction_cost"] <= model.friction_limit)


def test_run_is_deterministic(model, results):
    assert run_model(model) == results


def test_every_input_is_labelled(results):
    assert len(results["inputs"]) >= 10
    assert all(row["provenance"] in PROVENANCE and row["source"] for row in results["inputs"])


def test_harness_results_switch_labels_to_measured(model, synthetic_harness):
    r = run_model(model, synthetic_harness)
    assert r["harness_run_id"] == "abc123"
    assert r["strategies"]["gateway"]["vulnerabilities"]["S1"]["provenance"] == "Measured"
    assert r["strategies"]["gateway"]["false_positive_rate"]["provenance"] == "Measured"
```

- [ ] **Step 2: Run to verify failure.** `.venv/bin/pytest tests/test_fair_report.py -q` fails with a ModuleNotFoundError.

- [ ] **Step 3: Write `src/airg/fair/report.py`**

```python
"""Risk outputs (FR-21), ROI with friction (FR-22) and the strategy comparison (FR-33).

Risk reduction is measured against the 'accept_risk' baseline. Because shadow AI (S5) is part
of every strategy's losses, each strategy's reduction is already net of any shadow-AI increase
its false blocks cause (FR-35).
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from airg.fair.distributions import pert
from airg.fair.effectiveness import false_positive_rate, vulnerabilities
from airg.fair.inputs import Model, Pert, Range90
from airg.fair.simulate import simulate_losses

LEC_THRESHOLDS = (250_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000, 20_000_000)


def friction_cost(fp_rate, annual_queries, minutes_lost, hourly_cost):
    """Cost of legitimate questions wrongly blocked (PRD FR-22)."""
    return fp_rate * annual_queries * minutes_lost / 60 * hourly_cost


def summarize(total: np.ndarray) -> dict:
    return {
        "eal": int(round(total.mean())),
        "p10": int(round(np.percentile(total, 10))),
        "p50": int(round(np.percentile(total, 50))),
        "p90": int(round(np.percentile(total, 90))),
        "loss_exceedance": [{"threshold": t, "probability": round(float((total > t).mean()), 4)}
                            for t in LEC_THRESHOLDS],
    }


def _row(name: str, value: Pert | Range90) -> dict:
    return {"input": name, "provenance": value.provenance, "source": value.source}


def inputs_provenance(model: Model) -> list[dict]:
    rows = [_row("degradation", model.degradation),
            _row("friction.minutes_lost", model.friction.minutes_lost),
            _row("friction.hourly_cost", model.friction.hourly_cost),
            _row("shadow_ai.elasticity", model.shadow_ai.elasticity),
            {"input": "friction.annual_queries", "provenance": "Assumed", "source": model.friction.queries_source}]
    for s in model.scenarios:
        rows += [_row(f"{s.scenario_id}.events_per_year", s.events_per_year),
                 _row(f"{s.scenario_id}.loss_per_event", s.loss_per_event)]
    for st in model.strategies:
        rows.append(_row(f"{st.strategy_id}.annual_run_cost", st.annual_run_cost))
        rows += [_row(f"{st.strategy_id}.assumed_block_rates.{sid}", p) for sid, p in st.assumed_block_rates.items()]
        if st.assumed_false_positive_rate is not None:
            rows.append(_row(f"{st.strategy_id}.assumed_false_positive_rate", st.assumed_false_positive_rate))
    return rows


def run_model(model: Model, harness: dict | None = None) -> dict:
    n = model.iterations
    raw = {}
    for strategy in model.strategies:
        vulns = vulnerabilities(model, strategy, harness)
        fp = false_positive_rate(strategy, harness)
        losses, fp_draws = simulate_losses(model, vulns, fp)
        cost_rng = np.random.default_rng(model.seed + 1)
        run_cost = pert(cost_rng, strategy.annual_run_cost.low, strategy.annual_run_cost.mode,
                        strategy.annual_run_cost.high, n)
        f = model.friction
        minutes = pert(cost_rng, f.minutes_lost.low, f.minutes_lost.mode, f.minutes_lost.high, n)
        hourly = pert(cost_rng, f.hourly_cost.low, f.hourly_cost.mode, f.hourly_cost.high, n)
        raw[strategy.strategy_id] = {
            "strategy": strategy, "losses": losses, "total": sum(losses.values()),
            "run_cost": float(run_cost.mean()),
            "friction": float(friction_cost(fp_draws, f.annual_queries, minutes, hourly).mean()),
            "vulnerabilities": {sid: asdict(p) for sid, p in vulns.items()},
            "false_positive_rate": asdict(fp),
        }
    baseline_eal = float(raw["accept_risk"]["total"].mean())
    strategies = {}
    for sid, r in raw.items():
        summary = summarize(r["total"])
        cost = r["run_cost"] + r["friction"]
        reduction = baseline_eal - float(r["total"].mean())
        ratio = None if cost == 0 else reduction / cost
        strategies[sid] = {
            "name": r["strategy"].name,
            **summary,
            "eal_by_scenario": {k: int(round(v.mean())) for k, v in r["losses"].items()},
            "annual_run_cost": int(round(r["run_cost"])),
            "friction_cost": int(round(r["friction"])),
            "total_cost": int(round(cost)),
            "risk_reduction": int(round(reduction)),
            "reduction_to_cost": None if ratio is None else round(ratio, 2),
            "roi": None if cost == 0 else round((reduction - cost) / cost, 2),
            "meets_funding_test": ratio is not None and round(ratio, 2) >= model.funding_ratio,
            "within_appetite": summary["eal"] < model.appetite_eal and summary["p90"] < model.appetite_p90,
            "friction_within_limit": int(round(r["friction"])) <= model.friction_limit,
            "vulnerabilities": r["vulnerabilities"],
            "false_positive_rate": r["false_positive_rate"],
        }
    return {
        "iterations": n,
        "seed": model.seed,
        "harness_run_id": harness.get("run_id") if harness else None,
        "appetite": {"eal": model.appetite_eal, "p90": model.appetite_p90},
        "funding_ratio": model.funding_ratio,
        "strategies": strategies,
        "inputs": inputs_provenance(model),
    }


def write_results(results: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
```

- [ ] **Step 4: Run to verify pass.** `.venv/bin/pytest tests/test_fair_report.py -q` gives `8 passed`. The full suite must pass.

- [ ] **Step 5: Commit.**
```bash
git add src/airg/fair/report.py tests/test_fair_report.py
git commit -m "feat: FAIR results, ROI with friction and strategy comparison (FR-21, FR-22, FR-33)"
```

---

### Task 6: Run script and first results

**Files:**
- Create: `scripts/run_fair.py`
- Generated: `results/fair.json`

- [ ] **Step 1: Write `scripts/run_fair.py`**

```python
"""Run the FAIR risk model and write results/fair.json (Sprint 2B)."""
import json
from collections import Counter
from pathlib import Path

from airg.fair.inputs import load_model
from airg.fair.report import run_model, write_results

MODEL_PATH = Path("config/fair_model.yaml")
HARNESS_PATH = Path("results/harness.json")
RESULTS_PATH = Path("results/fair.json")


def money(x: float) -> str:
    return f"${x / 1e6:.2f}M" if abs(x) >= 1e6 else f"${x / 1e3:.0f}K"


def main() -> None:
    model = load_model(MODEL_PATH)
    harness = json.loads(HARNESS_PATH.read_text()) if HARNESS_PATH.exists() else None
    results = run_model(model, harness)
    write_results(results, RESULTS_PATH)

    source = (f"control effectiveness from harness run {results['harness_run_id']}" if harness
              else "no harness results yet, so control effectiveness is Assumed")
    print(f"\nFAIR model: {model.iterations:,} simulated years, seed {model.seed}; {source}\n")
    print(f"{'Strategy':26}{'Expected loss':>15}{'1-in-10 year':>14}{'Annual cost':>13}"
          f"{'Reduction:cost':>16}{'3:1?':>6}{'Appetite?':>11}")
    print("-" * 101)
    for s in results["strategies"].values():
        ratio = "n/a" if s["reduction_to_cost"] is None else f"{s['reduction_to_cost']:.1f} : 1"
        print(f"{s['name']:26}{money(s['eal']):>15}{money(s['p90']):>14}{money(s['total_cost']):>13}"
              f"{ratio:>16}{('yes' if s['meets_funding_test'] else 'no'):>6}"
              f"{('yes' if s['within_appetite'] else 'no'):>11}")
    a = results["appetite"]
    print(f"\nRisk appetite (CISO proposal, not yet agreed): expected loss under {money(a['eal'])}, "
          f"1-in-10-year under {money(a['p90'])}.")
    baseline = results["strategies"]["accept_risk"]["eal_by_scenario"]
    print("Expected loss by scenario if nothing is done: "
          + ", ".join(f"{k} {money(v)}" for k, v in baseline.items()))
    counts = Counter(row["provenance"] for row in results["inputs"])
    print("Inputs by label: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print(f"\nWrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it.** `.venv/bin/python scripts/run_fair.py`
Expected:
- The header says "no harness results yet, so control effectiveness is Assumed".
- There are five strategy rows.
- "Accept the risk" has the highest expected loss and shows "n/a" for the ratio.
- "Gateway guardrails" has a lower expected loss than accepting the risk.
- The line "Inputs by label" lists Assumed and Benchmarked counts.
- `results/fair.json` exists.

Paste the actual output in the report. Exact figures depend on the inputs.

- [ ] **Step 3: Check runtime and reproducibility.** Run the script twice and confirm `results/fair.json` is byte-identical: `md5 results/fair.json` before and after. The run should take under 30 seconds.

- [ ] **Step 4: Commit.**
```bash
git add scripts/run_fair.py results/fair.json
git commit -m "feat: FAIR run script and first results"
```

---

## Requirement Coverage

| Requirement | Task | Tests |
|---|---|---|
| FR-18 Scenario config with provenance | 2 | test_fair_inputs.py |
| FR-19 Monte Carlo, fixed seed | 4 | test_constant_inputs_give_frequency_times_magnitude, test_same_seed_is_reproducible |
| FR-20 Effectiveness haircut | 3 | test_prd_fr20_example, test_vulnerabilities_* |
| FR-21 EAL, P10/P50/P90, exceedance curve | 5 | test_every_strategy_has_the_outputs |
| FR-22 ROI with friction; 3:1 flag | 5 | test_friction_cost_prd_example, test_flags_follow_thresholds |
| FR-33 Compare with accepting the risk and the vendor firewall | 2, 5 | test_baseline_has_no_reduction; yaml strategies |
| FR-35 Shadow AI linked to friction | 4 | test_shadow_ai_rises_with_false_blocks, test_multiplier_formula |
| NFR-03 Reproducible | 4, 5, 6 | test_run_is_deterministic; Task 6 step 3 |
| D-11 Lognormal losses | 1 | test_lognormal_hits_its_90_range |

**Deliberate limits:**
- FR-31's four-strategy S1 comparison uses the `index_fix` and `gateway_plus_index_fix` strategies. Until the harness exists, their effectiveness is Assumed.
- Measured block rates arrive when Sprint 2A writes `results/harness.json` in the contract above. No engine change is needed then.

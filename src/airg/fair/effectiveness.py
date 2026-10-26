"""Control effectiveness as Vulnerability ranges (FR-20, D-5).

Vulnerability is the share of attack attempts that still succeed with a strategy in place
(1.0 means no protection). Measured values come from the harness hold-out results (FR-17),
relative to the unprotected baseline, and are widened by the adaptive-attacker degradation (D-5).
Without harness results, a strategy's assumed block rates are used and labelled Assumed. Every
block rate, measured or assumed, is widened by the same degradation so strategies are comparable.
A scenario a strategy doesn't address gets 1.0.
"""
from __future__ import annotations

import math

from airg.fair.inputs import Model, Pert, Strategy
from airg.stats import wilson_interval

NO_CONTROL = Pert(1.0, 1.0, 1.0, "Assumed", "No control in this strategy addresses this scenario")
NO_BLOCKING = Pert(0.0, 0.0, 0.0, "Assumed", "Strategy adds no blocking")
RATE_LIMIT = "rate_limit"
MIN_BASELINE_SUCCESSES = 10
GATEWAY_STRATEGIES = frozenset({"all_on", "all_on_permission_aware"})


def _clip(x: float) -> float:
    return min(1.0, max(0.0, x))


def _widen(block_low: float, block_mode: float, block_high: float, degradation: Pert,
           provenance: str, source: str) -> Pert:
    block_mode = min(max(block_mode, block_low), block_high)
    return Pert(_clip(1 - block_high * (1 - degradation.low)),
                _clip(1 - block_mode * (1 - degradation.mode)),
                _clip(1 - block_low * (1 - degradation.high)),
                provenance, source)


def vulnerability_from_block_rate(block: float, block_ci95: tuple[float, float],
                                  degradation: Pert, source: str) -> Pert:
    lo, hi = block_ci95
    return _widen(lo, block, hi, degradation, "Measured", source)


def _common_categories(harness: dict, strategy_name: str, categories) -> list[str]:
    strategies = harness.get("strategies", {})
    if strategy_name not in strategies or "all_off" not in strategies:
        return []
    off = strategies["all_off"]["splits"]["holdout"]["attacks"]
    cur = strategies[strategy_name]["splits"]["holdout"]["attacks"]
    return [c for c in categories if c in off and c in cur]


def _pooled(harness: dict, strategy_name: str, categories) -> tuple[int, int]:
    attacks = harness["strategies"][strategy_name]["splits"]["holdout"]["attacks"]
    rows = [attacks[c]["success"] for c in categories]
    return sum(r["n"] for r in rows), sum(r["count"] for r in rows)


def measured_block_rate(harness: dict, strategy_name: str, categories) -> tuple[float, tuple[float, float]] | None:
    """Pooled hold-out block rate relative to the unprotected baseline, with a Katz log-ratio
    95% interval on the success ratio, or None if the harness didn't measure it well enough."""
    if RATE_LIMIT in categories:
        abusive = harness.get("rate_limit", {}).get("abusive")
        if abusive is None or strategy_name not in GATEWAY_STRATEGIES:
            return None
        return abusive["rate"], (abusive["ci95"][0], abusive["ci95"][1])
    common = _common_categories(harness, strategy_name, categories)
    if not common:
        return None
    n0, k0 = _pooled(harness, "all_off", common)
    n1, k1 = _pooled(harness, strategy_name, common)
    if n0 == 0 or n1 == 0 or k0 < MIN_BASELINE_SUCCESSES:
        return None
    p0 = k0 / n0
    block = _clip(1 - (k1 / n1) / p0)
    if k1 == 0:
        k1, n1 = 0.5, n1 + 0.5
    p1 = k1 / n1
    r = p1 / p0
    se = math.sqrt((1 - p1) / k1 + (1 - p0) / k0)
    r_lo, r_hi = r * math.exp(-1.96 * se), r * math.exp(1.96 * se)
    return block, (_clip(1 - r_hi), _clip(1 - r_lo))


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
            if RATE_LIMIT not in scenario.harness_categories:
                covered = _common_categories(harness, strategy.harness_strategy, scenario.harness_categories)
                if len(covered) < len(scenario.harness_categories):
                    source += f"; categories measured: {', '.join(covered)}"
            out[sid] = vulnerability_from_block_rate(block, ci, model.degradation, source)
        elif sid in strategy.assumed_block_rates:
            b = strategy.assumed_block_rates[sid]
            out[sid] = _widen(b.low, b.mode, b.high, model.degradation, b.provenance,
                              f"{b.source}; widened for adaptive attackers (D-5)")
        else:
            out[sid] = NO_CONTROL
    return out


def false_positive_rate(strategy: Strategy, harness: dict | None = None) -> Pert:
    if harness is not None and strategy.harness_strategy in harness.get("strategies", {}):
        fp = harness["strategies"][strategy.harness_strategy]["splits"]["holdout"]["benign"]["false_positive"]
        lo, hi = fp["ci95"]
        return Pert(lo, min(max(fp["rate"], lo), hi), hi, "Measured",
                    f"Harness run {harness['run_id']}, hold-out benign set")
    if strategy.assumed_false_positive_rate is not None:
        return strategy.assumed_false_positive_rate
    return NO_BLOCKING

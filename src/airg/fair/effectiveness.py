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

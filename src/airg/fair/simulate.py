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

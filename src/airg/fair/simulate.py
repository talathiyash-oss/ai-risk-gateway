"""Monte Carlo annual loss (FR-19, FR-35, D-11).

Each iteration is one simulated year. A scenario's loss events are Poisson with rate
= events per year x Vulnerability; each event's loss is lognormal, fitted to its 90% range.
Shadow AI (S5) frequency rises with the strategy's false-block rate (FR-35).

Common random numbers: every random component (shared false-block rate and elasticity;
per scenario frequency, vulnerability, base event counts, event losses, keep decisions,
shadow-AI uplift) has its own child stream of the seed, and draws a fixed number of
uniforms (one per year, or one per potential event), mapped through inverse CDFs. A
strategy's parameters therefore never change how much randomness is consumed. Controls
act by thinning: base events are drawn at the uncontrolled rate and each is kept when its
keep-uniform is below Vulnerability, so every strategy sees the same potential events and
losses, and lower Vulnerability can never raise any year's loss. The shadow-AI uplift
(multiplier >= 1) adds extra events by superposition on top of the thinned base events.

Caveat: effectiveness and the false-positive rate are redrawn every simulated year and
independently per scenario, which narrows the tails; a two-level simulation (draw
parameters once per world, then simulate years) would be the rigorous version.
"""
from __future__ import annotations

import numpy as np

from airg.fair.distributions import lognormal, pert_ppf
from airg.fair.inputs import Model, Pert


def _draw(rng: np.random.Generator, p: Pert, n: int) -> np.ndarray:
    return pert_ppf(rng.random(n), p.low, p.mode, p.high)


def shadow_ai_multiplier(fp_rate: np.ndarray, elasticity: np.ndarray, reference_fp_rate: float) -> np.ndarray:
    return 1 + elasticity * fp_rate / reference_fp_rate


def simulate_losses(model: Model, vulnerabilities: dict[str, Pert], fp_rate: Pert,
                    seed: int | None = None) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Annual loss per scenario (one value per simulated year) and the false-block rate draws."""
    n = model.iterations
    root = np.random.SeedSequence(model.seed if seed is None else seed)
    shared_seeds, *scenario_seeds = root.spawn(len(model.scenarios) + 1)
    fp_stream, elasticity_stream = (np.random.default_rng(s) for s in shared_seeds.spawn(2))
    fp = _draw(fp_stream, fp_rate, n)
    elasticity = _draw(elasticity_stream, model.shadow_ai.elasticity, n)
    losses: dict[str, np.ndarray] = {}
    for scenario, seeds in zip(model.scenarios, scenario_seeds):
        freq_r, vuln_r, count_r, loss_r, keep_r, uplift_r = (np.random.default_rng(s) for s in seeds.spawn(6))
        p05, p95 = scenario.loss_per_event.p05, scenario.loss_per_event.p95
        freq = _draw(freq_r, scenario.events_per_year, n)
        v = _draw(vuln_r, vulnerabilities[scenario.scenario_id], n)
        counts0 = count_r.poisson(freq)
        total_events = int(counts0.sum())
        event_loss = lognormal(loss_r, p05, p95, total_events)
        keep_u = keep_r.random(total_events)
        year = np.repeat(np.arange(n), counts0)
        keep = keep_u < np.repeat(v, counts0)
        total = np.bincount(year[keep], weights=event_loss[keep], minlength=n)
        if scenario.scenario_id == model.shadow_ai.scenario_id:
            m = shadow_ai_multiplier(fp, elasticity, model.shadow_ai.reference_fp_rate)
            extra = uplift_r.poisson(freq * v * (m - 1))
            extra_loss = lognormal(uplift_r, p05, p95, int(extra.sum()))
            total = total + np.bincount(np.repeat(np.arange(n), extra), weights=extra_loss, minlength=n)
        losses[scenario.scenario_id] = total
    return losses, fp

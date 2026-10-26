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


def test_lower_vulnerability_never_increases_any_year():
    m = constant_model(5_000)
    high, _ = simulate_losses(m, {**FULL, "S1": one(0.5)}, one(0.0))
    low, _ = simulate_losses(m, {**FULL, "S1": one(0.3)}, one(0.0))
    assert np.all(low["S1"] <= high["S1"])


def test_ordered_vulnerability_ranges_are_coupled_per_year():
    from airg.fair.inputs import Pert as P
    m = constant_model(5_000)
    s1 = dataclasses.replace(m.scenarios[0], loss_per_event=Range90(50_000, 750_000, "Assumed", "test"))
    m = dataclasses.replace(m, scenarios=(s1, m.scenarios[1]))
    lo, _ = simulate_losses(m, {**FULL, "S1": P(0.1, 0.2, 0.3, "Assumed", "t")}, one(0.0))
    hi, _ = simulate_losses(m, {**FULL, "S1": P(0.4, 0.5, 0.6, "Assumed", "t")}, one(0.0))
    assert np.all(lo["S1"] <= hi["S1"])


def test_lognormal_losses_have_the_right_mean():
    import math
    from airg.fair.distributions import lognormal_params
    m = constant_model(200_000)
    s1 = dataclasses.replace(m.scenarios[0], loss_per_event=Range90(50_000, 750_000, "Assumed", "test"))
    m = dataclasses.replace(m, scenarios=(s1, m.scenarios[1]))
    mu, sigma = lognormal_params(50_000, 750_000)
    losses, _ = simulate_losses(m, FULL, one(0.0))
    assert losses["S1"].mean() == pytest.approx(4 * math.exp(mu + sigma ** 2 / 2), rel=0.03)


def test_elasticity_does_not_depend_on_strategy_fp():
    m = constant_model(2_000)
    a, _ = simulate_losses(m, FULL, Pert(0, 0, 0, "Assumed", "t"))
    b, _ = simulate_losses(m, FULL, Pert(0.01, 0.02, 0.03, "Assumed", "t"))
    assert np.array_equal(a["S1"], b["S1"])

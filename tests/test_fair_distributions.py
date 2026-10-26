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

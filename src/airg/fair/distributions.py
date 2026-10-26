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

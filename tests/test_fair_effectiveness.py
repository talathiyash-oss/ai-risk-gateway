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

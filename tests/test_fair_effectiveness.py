import math

import pytest

from airg.fair.effectiveness import (NO_CONTROL, false_positive_rate, measured_block_rate,
                                     vulnerabilities, vulnerability_from_block_rate)
from airg.fair.inputs import Pert, load_model

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
    r = 0.1
    se = math.sqrt(0.9 / 4)
    assert block == pytest.approx(0.9)
    assert (lo, hi) == (pytest.approx(1 - r * math.exp(1.96 * se)), pytest.approx(1 - r * math.exp(-1.96 * se)))


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
    assert (v["S1"].low, v["S1"].mode, v["S1"].high) == pytest.approx((0.15, 0.405, 0.64))
    assert "D-5" in v["S1"].source
    assert all(v[s].provenance == "Assumed" for s in ("S1", "S2", "S3", "S4"))


def test_accept_risk_has_no_protection(model):
    assert set(vulnerabilities(model, strategy(model, "accept_risk"), None).values()) == {NO_CONTROL}


def test_false_positive_rates(model, synthetic_harness):
    measured = false_positive_rate(strategy(model, "gateway"), synthetic_harness)
    assert (measured.low, measured.mode, measured.high, measured.provenance) == (0.0102, 0.02, 0.039, "Measured")
    assert false_positive_rate(strategy(model, "gateway"), None).provenance == "Assumed"
    accept = false_positive_rate(strategy(model, "accept_risk"), None)
    assert (accept.low, accept.mode, accept.high) == (0.0, 0.0, 0.0)


def harness_with(off, on, category="LLM01-direct", n=120):
    def run(k):
        return {"splits": {"holdout": {"attacks": {category: {"success": {"n": n, "count": k}}}}}}
    return {"run_id": "x", "strategies": {"all_off": run(off), "all_on": run(on)}}


def test_baseline_below_one_widens_interval():
    block, (lo, hi) = measured_block_rate(harness_with(60, 6), "all_on", ("LLM01-direct",))
    assert block == pytest.approx(0.9)
    p1, p0 = 6 / 120, 0.5
    se = math.sqrt((1 - p1) / 6 + (1 - p0) / 60)
    assert lo == pytest.approx(1 - 0.1 * math.exp(1.96 * se))
    assert hi == pytest.approx(1 - 0.1 * math.exp(-1.96 * se))
    se_only_strategy = math.sqrt((1 - p1) / 6)
    assert hi - lo > (0.1 * math.exp(1.96 * se_only_strategy) - 0.1 * math.exp(-1.96 * se_only_strategy))


def test_thin_baseline_gives_no_measurement():
    assert measured_block_rate(harness_with(5, 0), "all_on", ("LLM01-direct",)) is None


def test_zero_successes_keep_point_estimate():
    block, (lo, hi) = measured_block_rate(harness_with(60, 0), "all_on", ("LLM01-direct",))
    assert block == 1.0
    assert 0 < lo < hi <= 1.0


def test_empty_strategy_sample_gives_no_measurement():
    h = harness_with(60, 0)
    h["strategies"]["all_on"]["splits"]["holdout"]["attacks"]["LLM01-direct"]["success"]["n"] = 0
    assert measured_block_rate(h, "all_on", ("LLM01-direct",)) is None


def test_pools_only_common_categories(model):
    h = harness_with(60, 6, "LLM01-direct")
    h["strategies"]["all_on"]["splits"]["holdout"]["attacks"]["LLM01-indirect"] = {
        "success": {"n": 50, "count": 0}}
    scenario = next(s for s in model.scenarios if "LLM01-direct" in s.harness_categories)
    expected = measured_block_rate(h, "all_on", scenario.harness_categories)
    assert expected is not None
    assert expected[0] == pytest.approx(0.9)
    v = vulnerabilities(model, strategy(model, "gateway"), h)[scenario.scenario_id]
    if len(scenario.harness_categories) > 1:
        assert "categories measured: LLM01-direct" in v.source


@pytest.mark.parametrize("k0", [10, 40])
@pytest.mark.parametrize("k1", [0, 5, 40])
@pytest.mark.parametrize("d", [Pert(0.0, 0.15, 0.40, "Assumed", "d"), Pert(0.1, 0.1, 0.3, "Assumed", "d"),
                               Pert(0.0, 0.0, 0.0, "Assumed", "d")])
def test_vulnerability_is_ordered_and_bounded(k0, k1, d):
    block, ci = measured_block_rate(harness_with(k0, k1, n=40), "all_on", ("LLM01-direct",))
    v = vulnerability_from_block_rate(block, ci, d, "t")
    assert 0 <= v.low <= v.mode <= v.high <= 1


def test_strategy_worse_than_baseline_has_no_protection():
    block, ci = measured_block_rate(harness_with(20, 40, n=40), "all_on", ("LLM01-direct",))
    v = vulnerability_from_block_rate(block, ci, DEGRADATION, "t")
    assert (v.low, v.mode, v.high) == (1.0, 1.0, 1.0)


def test_strategy_without_harness_mapping_uses_assumed(model, synthetic_harness):
    vendor = strategy(model, "vendor_firewall")
    assert vendor.harness_strategy is None
    v = vulnerabilities(model, vendor, synthetic_harness)
    assert all(p.provenance != "Measured" for p in v.values())

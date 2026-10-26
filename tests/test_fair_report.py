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
    assert accept["meets_funding_test"] is None


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


def test_roi_prd_example():
    from airg.fair.report import roi
    assert roi(500_000, 40_000, 53_437.50) == pytest.approx(4.351, abs=0.001)
    assert roi(100, 0, 0) is None


def test_roi_matches_ratio(results):
    for s in results["strategies"].values():
        if s["reduction_to_cost"] is not None:
            assert s["roi"] == pytest.approx(s["reduction_to_cost"] - 1, abs=0.01)


def test_vendor_firewall_friction_exceeds_limit(results):
    assert results["strategies"]["vendor_firewall"]["friction_within_limit"] is False
    assert results["strategies"]["gateway"]["friction_within_limit"] is True


def test_shadow_ai_rises_with_false_blocks_in_report(results):
    assert (results["strategies"]["gateway"]["eal_by_scenario"]["S5"]
            > results["strategies"]["accept_risk"]["eal_by_scenario"]["S5"])


def test_ranges_are_ordered(results):
    for s in results["strategies"].values():
        if s["total_cost"] == 0:
            continue
        for key in ("friction_range", "run_cost_range", "risk_reduction_range"):
            assert s[key]["p10"] <= s[key]["p90"]
        assert s["return_range"]["low"] <= s["return_range"]["high"]


def test_per_scenario_summaries(results):
    for s in results["strategies"].values():
        assert set(s["scenarios"]) == {"S1", "S2", "S3", "S4", "S5"}
        for summary in s["scenarios"].values():
            assert summary["p10"] <= summary["p50"] <= summary["p90"]
            assert summary["loss_exceedance"]


def test_write_results_is_valid_json(tmp_path, results):
    import json
    from airg.fair.report import write_results
    write_results(results, tmp_path / "out" / "r.json")
    assert json.loads((tmp_path / "out" / "r.json").read_text())["iterations"] == results["iterations"]


def test_zero_friction_assumption_is_listed(results):
    assert any(r["input"].endswith(".false_positive_rate") and r["provenance"] == "Assumed"
               and r["source"] == "Strategy adds no blocking" for r in results["inputs"])


def test_p_worse_than_nothing(results):
    s = results["strategies"]
    assert s["accept_risk"]["p_worse_than_nothing"] is None
    assert 0 <= s["gateway"]["p_worse_than_nothing"] <= 1
    assert s["index_fix"]["p_worse_than_nothing"] <= s["gateway"]["p_worse_than_nothing"]


def test_measured_fp_provenance_with_harness(model, synthetic_harness):
    r = run_model(model, synthetic_harness)
    rows = [x for x in r["inputs"] if x["input"] == "gateway.false_positive_rate"]
    assert len(rows) == 1 and rows[0]["provenance"] == "Measured"


def test_each_strategy_has_one_fp_row(results):
    names = [x["input"] for x in results["inputs"] if x["input"].endswith("false_positive_rate")]
    assert len(names) == len(set(names)) == len(results["strategies"])

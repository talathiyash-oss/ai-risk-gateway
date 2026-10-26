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
    assert accept["meets_funding_test"] is False


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

import copy

import pytest
import yaml

from airg.fair.inputs import load_model

MODEL = "config/fair_model.yaml"


def test_repo_model_loads():
    m = load_model(MODEL)
    assert (m.iterations, m.seed) == (10_000, 2027)
    assert [s.scenario_id for s in m.scenarios] == ["S1", "S2", "S3", "S4", "S5"]
    assert [s.strategy_id for s in m.strategies] == [
        "accept_risk", "vendor_firewall", "gateway", "index_fix", "gateway_plus_index_fix"]
    assert m.shadow_ai.scenario_id == "S5"
    assert (m.appetite_eal, m.appetite_p90, m.funding_ratio) == (1_000_000, 5_000_000, 3)


def test_repo_model_block_rate_keys_are_valid():
    m = load_model(MODEL)
    scenario_ids = {s.scenario_id for s in m.scenarios}
    for st in m.strategies:
        assert set(st.assumed_block_rates) <= scenario_ids, st.strategy_id


def broken(tmp_path, mutate):
    with open(MODEL) as f:
        raw = yaml.safe_load(f)
    mutate(raw)
    path = tmp_path / "model.yaml"
    path.write_text(yaml.safe_dump(raw))
    return path


def test_missing_provenance_is_refused(tmp_path):
    path = broken(tmp_path, lambda r: r["scenarios"][0]["events_per_year"].pop("provenance"))
    with pytest.raises(ValueError, match="S1.events_per_year"):
        load_model(path)


def test_missing_source_is_refused(tmp_path):
    path = broken(tmp_path, lambda r: r["scenarios"][1]["loss_per_event"].pop("source"))
    with pytest.raises(ValueError, match="S2.loss_per_event: source"):
        load_model(path)


def test_unknown_provenance_is_refused(tmp_path):
    path = broken(tmp_path, lambda r: r["degradation"].update(provenance="Guessed"))
    with pytest.raises(ValueError, match="degradation: provenance"):
        load_model(path)


def test_out_of_order_range_is_refused(tmp_path):
    path = broken(tmp_path, lambda r: r["scenarios"][0]["events_per_year"].update(low=100))
    with pytest.raises(ValueError, match="low <= mode <= high"):
        load_model(path)


def test_accept_risk_strategy_is_required(tmp_path):
    path = broken(tmp_path, lambda r: r["strategies"].pop(0))
    with pytest.raises(ValueError, match="accept_risk"):
        load_model(path)


def _set_vendor_key(raw):
    rates = raw["strategies"][1]["assumed_block_rates"]
    rates["S11"] = rates.pop("S1")


def _vendor_s1_high(raw):
    raw["strategies"][1]["assumed_block_rates"]["S1"]["high"] = 1.3


def _degradation_high(raw):
    raw["degradation"]["high"] = 1.2


def _ref_fp_zero(raw):
    raw["shadow_ai"]["reference_fp_rate"] = 0


def _duplicate_strategy(raw):
    raw["strategies"].append(copy.deepcopy(raw["strategies"][0]))


def _duplicate_scenario(raw):
    raw["scenarios"].append(copy.deepcopy(raw["scenarios"][0]))


def _iterations_zero(raw):
    raw["iterations"] = 0


def _p90_below_eal(raw):
    raw["appetite"]["p90"] = 500_000


@pytest.mark.parametrize("mutate, match", [
    (_set_vendor_key, "vendor_firewall.assumed_block_rates: unknown scenario S11"),
    (_vendor_s1_high, "must be between 0 and 1"),
    (_degradation_high, "degradation: must be between 0 and 1"),
    (_ref_fp_zero, "shadow_ai.reference_fp_rate: must be between 0 and 1"),
    (_duplicate_strategy, "duplicate strategy id accept_risk"),
    (_duplicate_scenario, "duplicate scenario id S1"),
    (_iterations_zero, "iterations"),
    (_p90_below_eal, "appetite.p90"),
])
def test_invalid_model_is_refused(tmp_path, mutate, match):
    path = broken(tmp_path, mutate)
    with pytest.raises(ValueError, match=match):
        load_model(path)

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


def broken(tmp_path, mutate):
    raw = yaml.safe_load(open(MODEL))
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

import pytest

from airg.config import GUARD_IDS, default_config, load_config


def test_defaults_follow_decision_d1():
    cfg = default_config()
    assert all(cfg.guardrails[g].enabled for g in GUARD_IDS)
    assert {g: cfg.guardrails[g].fail_mode for g in GUARD_IDS} == {
        "GR-01": "closed", "GR-02": "closed", "GR-03": "closed", "GR-04": "open", "GR-05": "closed"}
    assert cfg.review_target_minutes == 15


def test_guardrail_can_be_switched_off_in_yaml(tmp_path):
    path = tmp_path / "gw.yaml"
    path.write_text("guardrails:\n  GR-02:\n    enabled: false\n")
    cfg = load_config(path)
    assert cfg.guardrails["GR-02"].enabled is False
    assert cfg.guardrails["GR-01"].enabled is True


def test_options_are_passed_through(tmp_path):
    path = tmp_path / "gw.yaml"
    path.write_text("guardrails:\n  GR-04:\n    requests_per_minute: 5\n")
    assert load_config(path).guardrails["GR-04"].options == {"requests_per_minute": 5}


def test_rejects_unknown_guardrail(tmp_path):
    path = tmp_path / "gw.yaml"
    path.write_text("guardrails:\n  GR-99:\n    enabled: true\n")
    with pytest.raises(ValueError, match="GR-99"):
        load_config(path)


def test_rejects_bad_fail_mode(tmp_path):
    path = tmp_path / "gw.yaml"
    path.write_text("guardrails:\n  GR-01:\n    fail_mode: sideways\n")
    with pytest.raises(ValueError, match="fail_mode"):
        load_config(path)


def test_repo_config_loads():
    cfg = load_config("config/gateway.yaml")
    assert cfg.guardrails["GR-04"].fail_mode == "open"
    assert cfg.guardrails["GR-04"].options["requests_per_minute"] == 20


def test_rejects_non_boolean_enabled(tmp_path):
    path = tmp_path / "gw.yaml"
    path.write_text('guardrails:\n  GR-02:\n    enabled: "false"\n')
    with pytest.raises(ValueError, match="enabled"):
        load_config(path)


def test_rejects_non_mapping_entry(tmp_path):
    path = tmp_path / "gw.yaml"
    path.write_text("guardrails:\n  GR-01: true\n")
    with pytest.raises(ValueError, match="GR-01"):
        load_config(path)

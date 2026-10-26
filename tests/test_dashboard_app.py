from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "src" / "airg" / "dashboard" / "app.py")


@pytest.fixture(scope="module")
def app():
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    return at


def test_app_runs_without_errors(app):
    assert not app.exception
    assert app.title[0].value.startswith("AI Risk Gateway")


def test_has_seven_tabs(app):
    assert [t.label for t in app.tabs] == ["Executive", "Loss curve", "Options", "What-if", "Inputs", "Compliance", "Live demo"]


def test_assumed_warning_without_harness(app):
    assert any("Assumed" in w.value for w in app.warning)


def test_appetite_verdict_is_stated(app):
    assert any("risk appetite" in e.value for e in app.error) or any("risk appetite" in s.value for s in app.success)


def test_what_if_slider_reruns(app):
    app.slider(key="wi_attack").set_value(2.0).run()
    assert not app.exception


def test_assumed_only_toggle(app):
    app.toggle(key="inputs_assumed_only").set_value(True).run()
    assert not app.exception


def test_live_demo_blocks_injection():
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    at.selectbox(key="demo_preset").set_value("Attack: direct prompt injection").run()
    at.button(key="demo_send").click().run()
    assert not at.exception
    assert any(e.value.startswith("Blocked") for e in at.error)


def test_appetite_banner_escapes_dollar_signs(app):
    banners = [e.value for e in app.error] + [s.value for s in app.success]
    appetite = next(b for b in banners if "risk appetite" in b)
    assert "\\$1.00M" in appetite and "$" not in appetite.replace("\\$", "")

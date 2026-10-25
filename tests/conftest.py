import pytest

from airg.data import generate_clients


@pytest.fixture(scope="session")
def records():
    return generate_clients(seed=42)


@pytest.fixture
def ctx():
    from airg.guardrails.base import RequestContext
    return RequestContext(request_id="req-1", user_id="RM-01", client_id="C-1001")


@pytest.fixture
def make_config():
    from airg.config import GatewayConfig, GuardConfig, default_config

    def _make(enabled, fail_modes=None):
        base = default_config()
        return GatewayConfig(
            guardrails={
                g: GuardConfig(g in enabled, (fail_modes or {}).get(g, c.fail_mode), dict(c.options))
                for g, c in base.guardrails.items()},
            review_target_minutes=base.review_target_minutes)
    return _make


@pytest.fixture(scope="session")
def redactor():
    from airg.redaction import get_redactor
    return get_redactor()


class FakeClock:
    def __init__(self, t: float = 1_000_000.0):
        self.t = t

    def __call__(self) -> float:
        return self.t


@pytest.fixture
def clock():
    return FakeClock()

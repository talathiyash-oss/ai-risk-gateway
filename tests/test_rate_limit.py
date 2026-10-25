from airg.guardrails.base import Action, RequestContext
from airg.guardrails.rate_limit import RateLimitGuard


def test_blocks_21st_request_in_a_minute(ctx, clock):
    guard = RateLimitGuard(requests_per_minute=20, tokens_per_day=50_000, clock=clock)
    for _ in range(20):
        assert guard.check_input(ctx, "hello").action is Action.ALLOW
    result = guard.check_input(ctx, "hello")
    assert (result.guard_id, result.action, result.reason) == ("GR-04", Action.BLOCK, "rate_limit:requests_per_minute")


def test_window_resets_after_a_minute(ctx, clock):
    guard = RateLimitGuard(requests_per_minute=20, clock=clock)
    for _ in range(20):
        guard.check_input(ctx, "hello")
    clock.t += 60
    assert guard.check_input(ctx, "hello").action is Action.ALLOW


def test_limits_are_per_user(ctx, clock):
    guard = RateLimitGuard(requests_per_minute=1, clock=clock)
    guard.check_input(ctx, "hello")
    other = RequestContext("req-2", "RM-02", "C-1002")
    assert guard.check_input(other, "hello").action is Action.ALLOW


def test_daily_token_budget(ctx, clock):
    guard = RateLimitGuard(requests_per_minute=20, tokens_per_day=10, clock=clock)
    assert guard.check_input(ctx, "one two three four five six").action is Action.ALLOW
    result = guard.check_input(ctx, "one two three four five six")
    assert (result.action, result.reason) == (Action.BLOCK, "rate_limit:tokens_per_day")

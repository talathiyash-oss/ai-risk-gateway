"""GR-04: per-user request and token limits (OWASP LLM10, FR-10).

The requests-per-minute window is a sliding window. The daily token budget resets per UTC day.
All state is guarded by a lock, so check_input is safe to call from multiple threads.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Callable

from airg.guardrails.base import Action, Guardrail, GuardResult, RequestContext


class RateLimitGuard(Guardrail):
    guard_id = "GR-04"

    def __init__(self, requests_per_minute: int = 20, tokens_per_day: int = 50_000,
                 clock: Callable[[], float] = time.time):
        self._rpm = requests_per_minute
        self._tpd = tokens_per_day
        self._clock = clock
        self._lock = threading.Lock()
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._tokens: dict[tuple[str, int], int] = defaultdict(int)

    def check_input(self, ctx: RequestContext, text: str) -> GuardResult:
        with self._lock:
            now = self._clock()
            window = self._requests[ctx.user_id]
            while window and now - window[0] >= 60:
                window.popleft()
            if len(window) >= self._rpm:
                return GuardResult(self.guard_id, "input", Action.BLOCK, "rate_limit:requests_per_minute")
            day_key = (ctx.user_id, int(now // 86_400))
            tokens = len(text.split())
            if self._tokens[day_key] + tokens > self._tpd:
                return GuardResult(self.guard_id, "input", Action.BLOCK, "rate_limit:tokens_per_day")
            window.append(now)
            self._tokens[day_key] += tokens
            return GuardResult(self.guard_id, "input", Action.ALLOW, "ok")

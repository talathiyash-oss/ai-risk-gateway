"""Gateway policy engine (FR-01 to FR-04): runs enabled guardrails around the copilot.

Stages, in order: input (prompt) -> retrieve -> chunks (documents) -> generate -> output (answer).
A BLOCK at any stage stops the request. A REDACT replaces the text and continues.
"""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Callable

from airg.config import GUARD_IDS, GatewayConfig
from airg.copilot import Copilot
from airg.guardrails.base import Action, Guardrail, GuardResult, RequestContext

logger = logging.getLogger(__name__)

GUARD_ORDER = ("GR-04", "GR-01", "GR-03", "GR-02")
BLOCK_MESSAGE = "This request can't be completed. Reference: {request_id}. You can request a review."
RATE_LIMIT_MESSAGE = "Too many requests. Reference: {request_id}. Please wait a minute and try again."


@dataclass(frozen=True)
class GatewayResult:
    request_id: str
    status: str
    answer: str | None
    http_status: int
    blocked_by: str | None = None  # internal only; never sent to the RM (NFR-06)


class Gateway:
    def __init__(self, config: GatewayConfig, copilot: Copilot, guards: dict[str, Guardrail],
                 audit=None, id_factory: Callable[[], str] | None = None):
        self._config = config
        self._copilot = copilot
        self._audit = audit if config.guardrails["GR-05"].enabled else None
        self._new_id = id_factory or (lambda: uuid.uuid4().hex[:12])
        self._guards = [guards[g] for g in GUARD_ORDER if g in guards and config.guardrails[g].enabled]
        for guard_id in GUARD_IDS:
            logger.info("%s %s", guard_id, "enabled" if config.guardrails[guard_id].enabled else "disabled")

    def _failure(self, guard_id: str, stage: str) -> GuardResult:
        mode = self._config.guardrails[guard_id].fail_mode
        logger.exception("%s failed at %s stage (fail %s)", guard_id, stage, mode)
        action = Action.BLOCK if mode == "closed" else Action.ALLOW
        return GuardResult(guard_id, stage, action, f"error/fail_{mode}")

    def handle(self, user_id: str, client_id: str, message: str,
               skip_guards: frozenset[str] = frozenset()) -> GatewayResult:
        ctx = RequestContext(self._new_id(), user_id, client_id)
        start = time.perf_counter()
        guards = [g for g in self._guards if g.guard_id not in skip_guards]
        decisions: list[GuardResult] = []

        text = message
        for guard in guards:
            try:
                result = guard.check_input(ctx, text)
            except Exception:
                result = self._failure(guard.guard_id, "input")
            decisions.append(result)
            if result.action is Action.BLOCK:
                return self._finish(ctx, decisions, start, text, None, blocked_by=result.guard_id)
            if result.action is Action.REDACT and result.text is not None:
                text = result.text

        chunks = self._copilot.retrieve(text, client_id)
        for guard in guards:
            try:
                chunks, results = guard.check_chunks(ctx, chunks)
            except Exception:
                results = [self._failure(guard.guard_id, "chunks")]
            decisions.extend(results)
            blocking = next((r for r in results if r.action is Action.BLOCK), None)
            if blocking is not None:
                return self._finish(ctx, decisions, start, text, None, blocked_by=blocking.guard_id)

        answer = self._copilot.generate(text, client_id, chunks)
        for guard in guards:
            try:
                result = guard.check_output(ctx, answer)
            except Exception:
                result = self._failure(guard.guard_id, "output")
            decisions.append(result)
            if result.action is Action.BLOCK:
                return self._finish(ctx, decisions, start, text, None, blocked_by=result.guard_id)
            if result.action is Action.REDACT and result.text is not None:
                answer = result.text

        return self._finish(ctx, decisions, start, text, answer)

    def _finish(self, ctx: RequestContext, decisions: list[GuardResult], start: float, prompt: str,
                answer: str | None, blocked_by: str | None = None) -> GatewayResult:
        latency_ms = (time.perf_counter() - start) * 1000
        if blocked_by:
            final = "block"
        elif any(d.action is Action.REDACT for d in decisions):
            final = "redact"
        else:
            final = "allow"
        if self._audit is not None:
            try:
                self._audit.record_request(ctx=ctx, decisions=decisions, final_action=final,
                                           latency_ms=latency_ms, prompt=prompt, response=answer)
            except Exception:
                logger.exception("Audit log write failed")
                if self._config.guardrails["GR-05"].fail_mode == "closed":
                    return GatewayResult(ctx.request_id, "blocked", None, 503, blocked_by="GR-05")
        if blocked_by:
            http_status = 429 if blocked_by == "GR-04" else 403
            return GatewayResult(ctx.request_id, "blocked", None, http_status, blocked_by=blocked_by)
        return GatewayResult(ctx.request_id, "ok", answer, 200)

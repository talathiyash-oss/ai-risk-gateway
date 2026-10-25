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
STAGES = ("input", "chunks", "output")
BLOCK_MESSAGE = "This request can't be completed. Reference: {request_id}. You can request a review."
RATE_LIMIT_MESSAGE = "Too many requests. Reference: {request_id}. Please wait a minute and try again."
NOT_REVIEWABLE_MESSAGE = "This request can't be completed. Reference: {request_id}."


@dataclass(frozen=True)
class GatewayResult:
    request_id: str
    status: str
    answer: str | None
    http_status: int
    blocked_by: str | None = None  # internal only; never sent to the RM (NFR-06)
    blocked_stage: str | None = None  # internal only


class Gateway:
    def __init__(self, config: GatewayConfig, copilot: Copilot, guards: dict[str, Guardrail],
                 audit=None, id_factory: Callable[[], str] | None = None):
        self._config = config
        self._copilot = copilot
        self._audit = audit if config.guardrails["GR-05"].enabled else None
        self._new_id = id_factory or (lambda: uuid.uuid4().hex[:12])
        for guard_id in GUARD_ORDER:
            if config.guardrails[guard_id].enabled:
                if guard_id not in guards:
                    raise ValueError(f"{guard_id} is enabled but no guard was provided")
                if guards[guard_id].guard_id != guard_id:
                    raise ValueError(f"guard registered as {guard_id} reports id {guards[guard_id].guard_id}")
        self._guards = [guards[g] for g in GUARD_ORDER if g in guards and config.guardrails[g].enabled]
        for guard_id in GUARD_IDS:
            logger.info("%s %s", guard_id, "enabled" if config.guardrails[guard_id].enabled else "disabled")

    def _failure(self, guard_id: str, stage: str) -> GuardResult:
        mode = self._config.guardrails[guard_id].fail_mode
        logger.exception("%s failed at %s stage (fail %s)", guard_id, stage, mode)
        action = Action.BLOCK if mode == "closed" else Action.ALLOW
        return GuardResult(guard_id, stage, action, f"error/fail_{mode}")

    def handle(self, user_id: str, client_id: str, message: str,
               skip_stages: frozenset[tuple[str, str]] = frozenset(),
               override_of: str | None = None) -> GatewayResult:
        """Run one request through the enabled guardrails and the copilot.

        An output-stage block logs response=None on purpose, so a leaked system prompt is not
        persisted. skip_stages is a set of (guard_id, stage) pairs: each pair skips that guard at
        that stage only, and is recorded in the audit log as an override (stage "override",
        referencing override_of).
        """
        if skip_stages:
            if override_of is None:
                raise ValueError("skip_stages requires override_of")
            for guard_id, stage in skip_stages:
                if guard_id not in GUARD_ORDER:
                    raise ValueError(f"unknown guard in skip_stages: {guard_id}")
                if stage not in STAGES:
                    raise ValueError(f"unknown stage in skip_stages: {stage}")
        ctx = RequestContext(self._new_id(), user_id, client_id)
        start = time.perf_counter()

        def active(stage: str) -> list[Guardrail]:
            return [g for g in self._guards if (g.guard_id, stage) not in skip_stages]

        decisions: list[GuardResult] = [
            GuardResult(g, "override", Action.ALLOW, f"skipped_for_review:{stage}:{override_of}")
            for g, stage in sorted(skip_stages)]

        text = message
        for guard in active("input"):
            try:
                result = guard.check_input(ctx, text)
            except Exception:
                result = self._failure(guard.guard_id, "input")
            decisions.append(result)
            if result.action is Action.BLOCK:
                return self._finish(ctx, decisions, start, text, None, blocking=result)
            if result.action is Action.REDACT and result.text is not None:
                text = result.text

        try:
            chunks = self._copilot.retrieve(text, client_id)
        except Exception:
            return self._copilot_failure(ctx, decisions, start, text, "retrieve")
        for guard in active("chunks"):
            try:
                chunks, results = guard.check_chunks(ctx, chunks)
            except Exception:
                results = [self._failure(guard.guard_id, "chunks")]
            decisions.extend(results)
            blocking = next((r for r in results if r.action is Action.BLOCK), None)
            if blocking is not None:
                return self._finish(ctx, decisions, start, text, None, blocking=blocking)

        try:
            answer = self._copilot.generate(text, client_id, chunks)
        except Exception:
            return self._copilot_failure(ctx, decisions, start, text, "generate")
        for guard in active("output"):
            try:
                result = guard.check_output(ctx, answer)
            except Exception:
                result = self._failure(guard.guard_id, "output")
            decisions.append(result)
            if result.action is Action.BLOCK:
                return self._finish(ctx, decisions, start, text, None, blocking=result)
            if result.action is Action.REDACT and result.text is not None:
                answer = result.text

        return self._finish(ctx, decisions, start, text, answer)

    def _copilot_failure(self, ctx, decisions, start, prompt, stage):
        logger.exception("Copilot failed at %s stage", stage)
        result = GuardResult("COPILOT", stage, Action.BLOCK, "error/copilot")
        decisions.append(result)
        return self._finish(ctx, decisions, start, prompt, None, blocking=result)

    def _finish(self, ctx: RequestContext, decisions: list[GuardResult], start: float, prompt: str,
                answer: str | None, blocking: GuardResult | None = None) -> GatewayResult:
        blocked_by = blocking.guard_id if blocking else None
        blocked_stage = blocking.stage if blocking else None
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
            if blocking.reason.startswith("error/"):
                http_status = 502 if blocked_by == "COPILOT" else 503
            else:
                http_status = 429 if blocked_by == "GR-04" else 403
            return GatewayResult(ctx.request_id, "blocked", None, http_status, blocked_by=blocked_by,
                                 blocked_stage=blocked_stage)
        return GatewayResult(ctx.request_id, "ok", answer, 200)

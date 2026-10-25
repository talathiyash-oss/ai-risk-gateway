"""Shared types for guardrails. A guardrail can act at three stages: input, chunks, output."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from airg.copilot import Chunk


class Action(str, Enum):
    ALLOW = "allow"
    REDACT = "redact"
    BLOCK = "block"


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    user_id: str
    client_id: str


@dataclass(frozen=True)
class GuardResult:
    guard_id: str
    stage: str
    action: Action
    reason: str
    text: str | None = None


class Guardrail:
    """Base class: allows everything. Subclasses override the stages they care about."""

    guard_id = "GR-00"

    def check_input(self, ctx: RequestContext, text: str) -> GuardResult:
        return GuardResult(self.guard_id, "input", Action.ALLOW, "ok")

    def check_chunks(self, ctx: RequestContext, chunks: list[Chunk]) -> tuple[list[Chunk], list[GuardResult]]:
        return chunks, []

    def check_output(self, ctx: RequestContext, text: str) -> GuardResult:
        return GuardResult(self.guard_id, "output", Action.ALLOW, "ok")

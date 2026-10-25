"""GR-01: prompt injection detection (OWASP LLM01, FR-05 direct, FR-06 indirect)."""
from __future__ import annotations

import re

from airg.copilot import Chunk
from airg.guardrails.base import Action, Guardrail, GuardResult, RequestContext

INJECTION_PATTERNS = [
    re.compile(r"\bignore (all |any )?(the )?(previous|prior|above|earlier) (instructions|rules|directions)\b", re.I),
    re.compile(r"\bdisregard (all |any )?(the )?(previous|prior|above|earlier) (instructions|rules)\b", re.I),
    re.compile(r"\byou are now\b", re.I),
    re.compile(r"\b(reveal|print|show|repeat) (me )?(your|the) (system prompt|instructions)\b", re.I),
    re.compile(r"\bnote to (the )?assistant\b", re.I),
]


def looks_like_injection(text: str) -> bool:
    return any(p.search(text) for p in INJECTION_PATTERNS)


class InjectionGuard(Guardrail):
    guard_id = "GR-01"

    def check_input(self, ctx: RequestContext, text: str) -> GuardResult:
        if looks_like_injection(text):
            return GuardResult(self.guard_id, "input", Action.BLOCK, "prompt_injection")
        return GuardResult(self.guard_id, "input", Action.ALLOW, "ok")

    def check_chunks(self, ctx: RequestContext, chunks: list[Chunk]) -> tuple[list[Chunk], list[GuardResult]]:
        kept, results = [], []
        for chunk in chunks:
            if looks_like_injection(chunk.text):
                results.append(GuardResult(self.guard_id, "chunks", Action.REDACT,
                                           f"indirect_injection:{chunk.doc_id}"))
            else:
                kept.append(chunk)
        return kept, results

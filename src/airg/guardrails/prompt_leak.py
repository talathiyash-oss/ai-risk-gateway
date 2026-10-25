"""GR-03: block answers that reveal the system prompt (OWASP LLM07, FR-09)."""
from __future__ import annotations

import re

from airg.copilot import CANARY, SYSTEM_PROMPT
from airg.guardrails.base import Action, Guardrail, GuardResult, RequestContext


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class PromptLeakGuard(Guardrail):
    guard_id = "GR-03"

    def __init__(self, system_prompt: str = SYSTEM_PROMPT, canary: str = CANARY,
                 threshold: float = 0.8, min_words: int = 5):
        self._canary = canary
        self._threshold = threshold
        sentences = re.split(r"(?<=\.)\s+", system_prompt)
        self._sentences = [_words(s) for s in sentences if len(_words(s)) >= min_words]

    def check_output(self, ctx: RequestContext, text: str) -> GuardResult:
        if self._canary in text:
            return GuardResult(self.guard_id, "output", Action.BLOCK, "canary")
        words = _words(text)
        for sentence in self._sentences:
            if len(sentence & words) / len(sentence) >= self._threshold:
                return GuardResult(self.guard_id, "output", Action.BLOCK, "system_prompt_similarity")
        return GuardResult(self.guard_id, "output", Action.ALLOW, "ok")

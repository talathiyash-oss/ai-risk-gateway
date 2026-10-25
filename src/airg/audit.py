"""GR-05: JSON Lines audit log (FR-11), with retention and export (FR-12).

Text is always passed through the PII redactor before it is written, whether or not GR-02
is enabled (GDPR data minimization, Compliance interview 2026-10-25). Known sensitive terms
(client names, the system prompt canary) are replaced as well, since the redactor has no PERSON entity.
"""
from __future__ import annotations

import json
import logging
import os
import re
import threading
import time
from pathlib import Path
from typing import Callable

from airg.guardrails.base import GuardResult, RequestContext
from airg.redaction import PiiRedactor, get_redactor

log = logging.getLogger(__name__)


class AuditLog:
    def __init__(self, path: str | Path, redactor: PiiRedactor | None = None,
                 clock: Callable[[], float] = time.time, sensitive_terms: dict[str, str] | None = None):
        self.path = Path(path)
        self._redactor = redactor or get_redactor()
        self._terms = [(self._term_pattern(term), placeholder)
                       for term, placeholder in (sensitive_terms or {}).items() if term]
        self._clock = clock
        self._lock = threading.RLock()

    @staticmethod
    def _line(entry: dict) -> str:
        return json.dumps(entry, sort_keys=True) + "\n"

    def _write(self, entry: dict) -> None:
        line = self._line(entry)
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a") as f:
                f.write(line)

    @staticmethod
    def _term_pattern(term: str) -> re.Pattern:
        escaped = re.escape(term)
        start = r"\b" if re.match(r"\w", term[0]) else ""
        end = r"\b" if re.match(r"\w", term[-1]) else ""
        return re.compile(start + escaped + end, re.IGNORECASE)

    def _scrub(self, text: str | None) -> str | None:
        if text is None:
            return None
        text = self._redactor.redact(text)[0]
        for pattern, placeholder in self._terms:
            text = pattern.sub(placeholder, text)
        return text

    def record_event(self, event: str, **fields) -> dict:
        scrubbed = {k: self._scrub(v) if isinstance(v, str) else v for k, v in fields.items()}
        entry = {**scrubbed, "event": event, "timestamp": self._clock()}
        self._write(entry)
        return entry

    def record_request(self, *, ctx: RequestContext, decisions: list[GuardResult], final_action: str,
                       latency_ms: float, prompt: str, response: str | None) -> dict:
        return self.record_event(
            "request",
            request_id=ctx.request_id,
            user_id=ctx.user_id,
            client_id=ctx.client_id,
            guardrails_evaluated=sorted({d.guard_id for d in decisions}),
            decisions=[{"guard_id": d.guard_id, "stage": d.stage, "action": d.action.value,
                        "reason": self._scrub(d.reason)}
                       for d in decisions],
            final_action=final_action,
            latency_ms=round(latency_ms, 2),
            prompt_redacted=self._scrub(prompt),
            response_redacted=self._scrub(response),
        )

    def entries(self) -> list[dict]:
        with self._lock:
            if not self.path.exists():
                return []
            result = []
            for lineno, line in enumerate(self.path.read_text().splitlines(), start=1):
                if not line:
                    continue
                try:
                    result.append(json.loads(line))
                except json.JSONDecodeError:
                    log.warning("skipping corrupt audit line %d in %s", lineno, self.path)
            return result

    def _rewrite(self, entries: list[dict]) -> None:
        tmp = self.path.with_suffix(".jsonl.tmp")
        tmp.write_text("".join(self._line(e) for e in entries))
        os.replace(tmp, self.path)

    def purge(self, retention_days: float) -> int:
        with self._lock:
            cutoff = self._clock() - retention_days * 86_400
            entries = self.entries()
            kept = [e for e in entries if e["timestamp"] >= cutoff]
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._rewrite(kept)
            return len(entries) - len(kept)

    def export(self, start: float, end: float, out_path: str | Path) -> int:
        with self._lock:
            selected = [e for e in self.entries() if start <= e["timestamp"] < end]
            Path(out_path).write_text("".join(self._line(e) for e in selected))
            return len(selected)

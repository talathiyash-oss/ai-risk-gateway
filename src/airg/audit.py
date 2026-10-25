"""GR-05: JSON Lines audit log (FR-11), with retention and export (FR-12).

Text is always passed through the PII redactor before it is written, whether or not GR-02
is enabled (GDPR data minimization, Compliance interview 2026-10-25).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from airg.guardrails.base import GuardResult, RequestContext
from airg.redaction import PiiRedactor, get_redactor


class AuditLog:
    def __init__(self, path: str | Path, redactor: PiiRedactor | None = None,
                 clock: Callable[[], float] = time.time):
        self.path = Path(path)
        self._redactor = redactor or get_redactor()
        self._clock = clock

    def _write(self, entry: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

    def _scrub(self, text: str | None) -> str | None:
        return None if text is None else self._redactor.redact(text)[0]

    def record_event(self, event: str, **fields) -> dict:
        entry = {"event": event, "timestamp": self._clock(), **fields}
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
            decisions=[{"guard_id": d.guard_id, "stage": d.stage, "action": d.action.value, "reason": d.reason}
                       for d in decisions],
            final_action=final_action,
            latency_ms=round(latency_ms, 2),
            prompt_redacted=self._scrub(prompt),
            response_redacted=self._scrub(response),
        )

    def entries(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line]

    def purge(self, retention_days: float) -> int:
        cutoff = self._clock() - retention_days * 86_400
        entries = self.entries()
        kept = [e for e in entries if e["timestamp"] >= cutoff]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in kept))
        return len(entries) - len(kept)

    def export(self, start: float, end: float, out_path: str | Path) -> int:
        selected = [e for e in self.entries() if start <= e["timestamp"] < end]
        Path(out_path).write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in selected))
        return len(selected)

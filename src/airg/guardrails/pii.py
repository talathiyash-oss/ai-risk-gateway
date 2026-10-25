"""GR-02: PII redaction in prompts (FR-07) and cross-client leak check in answers (FR-08)."""
from __future__ import annotations

import re

from airg.data import ClientRecord
from airg.guardrails.base import Action, Guardrail, GuardResult, RequestContext
from airg.redaction import PiiRedactor, get_redactor

ACCOUNT_RE = re.compile(r"\bBMT[-–\s]?(\d{8})\b", re.IGNORECASE)
CLIENT_ID_RE = re.compile(r"\bC-\d{4}\b", re.IGNORECASE)


class PiiGuard(Guardrail):
    guard_id = "GR-02"

    def __init__(self, records: list[ClientRecord], redactor: PiiRedactor | None = None):
        self._redactor = redactor or get_redactor()
        # Account lookup is keyed on the 8 digits so separator and case variants resolve to the same owner.
        self._account_owner = {r.account_number.split("-", 1)[1]: r.client_id for r in records}
        self._client_ids = {r.client_id for r in records}
        self._name_patterns = []
        for r in records:
            first, last = r.name.split(" ", 1)
            f, l = re.escape(first), re.escape(last)
            pattern = re.compile(rf"\b(?:{f}\s+{l}|{l},\s*{f})\b", re.IGNORECASE)
            self._name_patterns.append((pattern, r.client_id))

    def check_input(self, ctx: RequestContext, text: str) -> GuardResult:
        redacted, entities = self._redactor.redact(text)
        if entities:
            return GuardResult(self.guard_id, "input", Action.REDACT, "pii:" + ",".join(entities), redacted)
        return GuardResult(self.guard_id, "input", Action.ALLOW, "ok")

    def check_output(self, ctx: RequestContext, text: str) -> GuardResult:
        leaked: set[str] = set()

        def replace_account(match: re.Match) -> str:
            owner = self._account_owner.get(match.group(1))
            if owner is not None and owner != ctx.client_id:
                leaked.add(owner)
                return "<ACCOUNT_NUMBER>"
            return match.group(0)

        def replace_client_id(match: re.Match) -> str:
            client_id = match.group(0).upper()
            if client_id in self._client_ids and client_id != ctx.client_id:
                leaked.add(client_id)
                return "<CLIENT_ID>"
            return match.group(0)

        out = ACCOUNT_RE.sub(replace_account, text)
        out = CLIENT_ID_RE.sub(replace_client_id, out)
        for pattern, owner in self._name_patterns:
            if owner != ctx.client_id and pattern.search(out):
                out = pattern.sub("<PERSON>", out)
                leaked.add(owner)
        if leaked:
            reason = f"cross_client:{ctx.client_id}->{','.join(sorted(leaked))}"
            return GuardResult(self.guard_id, "output", Action.REDACT, reason, out)
        return GuardResult(self.guard_id, "output", Action.ALLOW, "ok")

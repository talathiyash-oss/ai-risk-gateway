"""Builds the gateway, review queue and audit log from configuration."""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from airg.audit import AuditLog
from airg.config import GatewayConfig
from airg.copilot import CANARY, Copilot
from airg.data import ClientRecord
from airg.guardrails.injection import InjectionGuard
from airg.guardrails.pii import PiiGuard
from airg.guardrails.prompt_leak import PromptLeakGuard
from airg.guardrails.rate_limit import RateLimitGuard
from airg.pipeline import Gateway
from airg.redaction import PiiRedactor
from airg.reviews import ReviewQueue


@dataclass(frozen=True)
class Services:
    gateway: Gateway
    reviews: ReviewQueue
    copilot: Copilot
    audit: AuditLog | None


def build_services(config: GatewayConfig, records: list[ClientRecord], *,
                   audit_path: str | Path = "logs/audit.jsonl", clock: Callable[[], float] = time.time,
                   redactor: PiiRedactor | None = None) -> Services:
    g = config.guardrails
    copilot = Copilot(records)
    guards = {}
    if g["GR-01"].enabled:
        guards["GR-01"] = InjectionGuard()
    if g["GR-02"].enabled:
        guards["GR-02"] = PiiGuard(records, redactor)
    if g["GR-03"].enabled:
        guards["GR-03"] = PromptLeakGuard()
    if g["GR-04"].enabled:
        guards["GR-04"] = RateLimitGuard(
            requests_per_minute=g["GR-04"].options.get("requests_per_minute", 20),
            tokens_per_day=g["GR-04"].options.get("tokens_per_day", 50_000),
            clock=clock)
    audit = None
    if g["GR-05"].enabled:
        sensitive = {r.name: "<PERSON>" for r in records}
        sensitive[CANARY] = "<CANARY>"
        audit = AuditLog(g["GR-05"].options.get("log_path", audit_path), redactor, clock=clock,
                         sensitive_terms=sensitive)
        audit.purge(g["GR-05"].options.get("retention_days", 395))
    gateway = Gateway(config, copilot, guards, audit)
    reviews = ReviewQueue(gateway, audit, target_minutes=config.review_target_minutes, clock=clock)
    return Services(gateway, reviews, copilot, audit)

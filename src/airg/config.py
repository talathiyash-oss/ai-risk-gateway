"""Gateway configuration (FR-02 switches, FR-04 fail modes, PRD decision D-1 defaults)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

GUARD_IDS = ("GR-01", "GR-02", "GR-03", "GR-04", "GR-05")
DEFAULT_FAIL_MODES = {"GR-01": "closed", "GR-02": "closed", "GR-03": "closed", "GR-04": "open", "GR-05": "closed"}
FAIL_MODES = ("closed", "open")


@dataclass(frozen=True)
class GuardConfig:
    enabled: bool
    fail_mode: str
    options: dict = field(default_factory=dict)


@dataclass(frozen=True)
class GatewayConfig:
    guardrails: dict[str, GuardConfig]
    review_target_minutes: int = 15


def _parse(raw: dict) -> GatewayConfig:
    section = raw.get("guardrails") or {}
    unknown = sorted(set(section) - set(GUARD_IDS))
    if unknown:
        raise ValueError(f"Unknown guardrail(s) in config: {', '.join(unknown)}")
    guardrails = {}
    for guard_id in GUARD_IDS:
        entry = section.get(guard_id)
        if entry is None:
            entry = {}
        if not isinstance(entry, dict):
            raise ValueError(f"{guard_id}: settings must be a mapping")
        enabled = entry.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError(f"{guard_id}: enabled must be true or false, got {enabled!r}")
        fail_mode = entry.get("fail_mode", DEFAULT_FAIL_MODES[guard_id])
        if fail_mode not in FAIL_MODES:
            raise ValueError(f"{guard_id}: fail_mode must be one of {FAIL_MODES}, got {fail_mode!r}")
        options = {k: v for k, v in entry.items() if k not in ("enabled", "fail_mode")}
        guardrails[guard_id] = GuardConfig(enabled, fail_mode, options)
    reviews = raw.get("reviews") or {}
    return GatewayConfig(guardrails, int(reviews.get("target_minutes", 15)))


def load_config(path: str | Path) -> GatewayConfig:
    return _parse(yaml.safe_load(Path(path).read_text()) or {})


def default_config() -> GatewayConfig:
    return _parse({})

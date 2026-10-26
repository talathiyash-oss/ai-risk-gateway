"""FAIR model inputs (FR-18). Every input carries a provenance label (Measured, Benchmarked or
Assumed) and a source or rationale; the loader refuses to run without them."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

PROVENANCE = ("Measured", "Benchmarked", "Assumed")


@dataclass(frozen=True)
class Pert:
    low: float
    mode: float
    high: float
    provenance: str
    source: str


@dataclass(frozen=True)
class Range90:
    p05: float
    p95: float
    provenance: str
    source: str


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    name: str
    events_per_year: Pert
    loss_per_event: Range90
    harness_categories: tuple[str, ...]


@dataclass(frozen=True)
class Strategy:
    strategy_id: str
    name: str
    harness_strategy: str | None
    annual_run_cost: Pert
    assumed_block_rates: dict[str, Pert] = field(default_factory=dict)
    assumed_false_positive_rate: Pert | None = None


@dataclass(frozen=True)
class Friction:
    annual_queries: int
    queries_source: str
    minutes_lost: Pert
    hourly_cost: Pert


@dataclass(frozen=True)
class ShadowAI:
    scenario_id: str
    elasticity: Pert
    reference_fp_rate: float


@dataclass(frozen=True)
class Model:
    iterations: int
    seed: int
    scenarios: tuple[Scenario, ...]
    strategies: tuple[Strategy, ...]
    friction: Friction
    shadow_ai: ShadowAI
    degradation: Pert
    appetite_eal: float
    appetite_p90: float
    funding_ratio: float
    friction_limit: float


def _label(raw: dict, where: str) -> tuple[str, str]:
    provenance = raw.get("provenance")
    if provenance not in PROVENANCE:
        raise ValueError(f"{where}: provenance must be one of {PROVENANCE}, got {provenance!r}")
    source = raw.get("source")
    if not source:
        raise ValueError(f"{where}: source is required")
    return provenance, str(source)


def _pert(raw, where: str, unit: bool = False) -> Pert:
    if not isinstance(raw, dict):
        raise ValueError(f"{where}: expected low, mode, high, provenance and source")
    try:
        low, mode, high = float(raw["low"]), float(raw["mode"]), float(raw["high"])
    except KeyError as missing:
        raise ValueError(f"{where}: missing {missing.args[0]}") from None
    if not low <= mode <= high:
        raise ValueError(f"{where}: needs low <= mode <= high")
    if unit and not (0 <= low and high <= 1):
        raise ValueError(f"{where}: must be between 0 and 1")
    return Pert(low, mode, high, *_label(raw, where))


def _range90(raw, where: str) -> Range90:
    if not isinstance(raw, dict):
        raise ValueError(f"{where}: expected p05, p95, provenance and source")
    try:
        p05, p95 = float(raw["p05"]), float(raw["p95"])
    except KeyError as missing:
        raise ValueError(f"{where}: missing {missing.args[0]}") from None
    if not 0 < p05 <= p95:
        raise ValueError(f"{where}: needs 0 < p05 <= p95")
    return Range90(p05, p95, *_label(raw, where))


def _unique(ids: list[str], kind: str) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise ValueError(f"duplicate {kind} id {item_id}")
        seen.add(item_id)


def _parse(raw: dict) -> Model:
    scenarios = tuple(
        Scenario(
            scenario_id=s["id"],
            name=s["name"],
            events_per_year=_pert(s.get("events_per_year"), f"{s['id']}.events_per_year"),
            loss_per_event=_range90(s.get("loss_per_event"), f"{s['id']}.loss_per_event"),
            harness_categories=tuple(s.get("harness_categories") or ()),
        )
        for s in raw["scenarios"])
    _unique([s.scenario_id for s in scenarios], "scenario")
    scenario_ids = {s.scenario_id for s in scenarios}
    strategies = tuple(
        Strategy(
            strategy_id=st["id"],
            name=st["name"],
            harness_strategy=st.get("harness_strategy"),
            annual_run_cost=_pert(st.get("annual_run_cost"), f"{st['id']}.annual_run_cost"),
            assumed_block_rates=_block_rates(st),
            assumed_false_positive_rate=(
                _pert(st["assumed_false_positive_rate"], f"{st['id']}.assumed_false_positive_rate",
                      unit=True)
                if st.get("assumed_false_positive_rate") is not None else None),
        )
        for st in raw["strategies"])
    _unique([st.strategy_id for st in strategies], "strategy")
    if "accept_risk" not in [st.strategy_id for st in strategies]:
        raise ValueError("strategies: an 'accept_risk' baseline strategy is required")
    for st in strategies:
        for sid in st.assumed_block_rates:
            if sid not in scenario_ids:
                raise ValueError(f"{st.strategy_id}.assumed_block_rates: unknown scenario {sid}")
    friction = raw["friction"]
    shadow = raw["shadow_ai"]
    if shadow["scenario"] not in scenario_ids:
        raise ValueError(f"shadow_ai: unknown scenario {shadow['scenario']}")
    reference_fp_rate = float(shadow["reference_fp_rate"])
    if not 0 < reference_fp_rate <= 1:
        raise ValueError("shadow_ai.reference_fp_rate: must be between 0 and 1")
    appetite = raw["appetite"]
    appetite_eal, appetite_p90 = float(appetite["eal"]), float(appetite["p90"])
    if appetite_eal <= 0:
        raise ValueError("appetite.eal: must be > 0")
    if appetite_p90 < appetite_eal:
        raise ValueError("appetite.p90: must be >= appetite.eal")
    iterations = int(raw["iterations"])
    if iterations < 1:
        raise ValueError("iterations: must be >= 1")
    funding_ratio = float(raw["funding_ratio"])
    if funding_ratio <= 0:
        raise ValueError("funding_ratio: must be > 0")
    friction_limit = float(raw["friction_limit"])
    if friction_limit < 0:
        raise ValueError("friction_limit: must be >= 0")
    annual_queries = int(friction["annual_queries"])
    if annual_queries < 0:
        raise ValueError("friction.annual_queries: must be >= 0")
    return Model(
        iterations=iterations,
        seed=int(raw["seed"]),
        scenarios=scenarios,
        strategies=strategies,
        friction=Friction(annual_queries, str(friction["queries_source"]),
                          _pert(friction["minutes_lost"], "friction.minutes_lost"),
                          _pert(friction["hourly_cost"], "friction.hourly_cost")),
        shadow_ai=ShadowAI(shadow["scenario"], _pert(shadow["elasticity"], "shadow_ai.elasticity"),
                           reference_fp_rate),
        degradation=_pert(raw.get("degradation"), "degradation", unit=True),
        appetite_eal=appetite_eal,
        appetite_p90=appetite_p90,
        funding_ratio=funding_ratio,
        friction_limit=friction_limit,
    )


def _block_rates(st: dict) -> dict[str, Pert]:
    return {
        sid: _pert(p, f"{st['id']}.assumed_block_rates.{sid}", unit=True)
        for sid, p in (st.get("assumed_block_rates") or {}).items()}


def load_model(path: str | Path) -> Model:
    return _parse(yaml.safe_load(Path(path).read_text()))

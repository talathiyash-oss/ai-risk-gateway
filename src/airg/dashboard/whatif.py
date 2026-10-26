"""What-if analysis (FR-28): rerun the FAIR model with selected assumptions changed.

The model reruns with the same seed, so differences come from the change rather than from chance.
Changed inputs are labelled Assumed, with a source starting "What-if".
"""
from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass

from airg.dashboard.data import HARNESS_PATH, MODEL_PATH
from airg.fair.inputs import Model, Pert, load_model
from airg.fair.report import run_model


@dataclass(frozen=True)
class WhatIf:
    attack_frequency: float = 1.0    # multiplier on S2 (injection-driven data theft) events per year
    exposure_frequency: float = 1.0  # multiplier on S1 (cross-client exposure) events per year
    elasticity: float = 0.5          # most likely shadow-AI elasticity (config default 0.5)
    degradation: float = 0.15        # most likely adaptive-attacker degradation (config default 0.15)
    gateway_cost: float = 1.0        # multiplier on the run cost of options that include the gateway


def _scaled(p: Pert, k: float, what: str) -> Pert:
    if k == 1.0:
        return p
    return Pert(p.low * k, p.mode * k, p.high * k, "Assumed", f"What-if: {what} x{k:g} (was: {p.source})")


def _add_gateway_share(combo: Pert, gateway: Pert, k: float) -> Pert:
    """Scale only the gateway's share of a combined run cost: add (k - 1) x the gateway's own cost."""
    if k == 1.0:
        return combo
    return Pert(combo.low + (k - 1) * gateway.low, combo.mode + (k - 1) * gateway.mode,
                combo.high + (k - 1) * gateway.high, "Assumed",
                f"What-if: gateway share of run cost x{k:g} (was: {combo.source})")


def _with_mode(p: Pert, mode: float, what: str) -> Pert:
    mode = min(max(mode, p.low), p.high)
    if mode == p.mode:
        return p
    return Pert(p.low, mode, p.high, "Assumed", f"What-if: {what} most likely {mode:g} (was: {p.source})")


def apply_what_if(model: Model, w: WhatIf) -> Model:
    scenarios = []
    for s in model.scenarios:
        if s.scenario_id == "S2":
            s = dataclasses.replace(s, events_per_year=_scaled(s.events_per_year, w.attack_frequency, "attack frequency"))
        elif s.scenario_id == "S1":
            s = dataclasses.replace(s, events_per_year=_scaled(s.events_per_year, w.exposure_frequency, "exposure frequency"))
        scenarios.append(s)
    by_id = {st.strategy_id: st for st in model.strategies}
    gateway_cost = by_id["gateway"].annual_run_cost
    strategies = []
    for st in model.strategies:
        if st.strategy_id == "gateway":
            st = dataclasses.replace(st, annual_run_cost=_scaled(st.annual_run_cost, w.gateway_cost, "gateway run cost"))
        elif st.strategy_id == "gateway_plus_index_fix":
            st = dataclasses.replace(st, annual_run_cost=_add_gateway_share(st.annual_run_cost, gateway_cost, w.gateway_cost))
        strategies.append(st)
    strategies = tuple(strategies)
    return dataclasses.replace(
        model,
        scenarios=tuple(scenarios),
        strategies=strategies,
        shadow_ai=dataclasses.replace(model.shadow_ai,
                                      elasticity=_with_mode(model.shadow_ai.elasticity, w.elasticity, "shadow-AI elasticity")),
        degradation=_with_mode(model.degradation, w.degradation, "attacker degradation"),
    )


def run_what_if(w: WhatIf, model: Model | None = None) -> dict:
    harness = json.loads(HARNESS_PATH.read_text()) if HARNESS_PATH.exists() else None
    return run_model(apply_what_if(model or load_model(MODEL_PATH), w), harness)

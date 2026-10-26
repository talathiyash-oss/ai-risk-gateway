"""Risk outputs (FR-21), ROI with friction (FR-22) and the strategy comparison (FR-33).

Risk reduction is measured against the 'accept_risk' baseline. Because shadow AI (S5) is part
of every strategy's losses, each strategy's reduction is already net of any shadow-AI increase
its false blocks cause (FR-35).
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from airg.fair.distributions import pert_ppf
from airg.fair.effectiveness import false_positive_rate, vulnerabilities
from airg.fair.inputs import Model, Pert, Range90
from airg.fair.simulate import simulate_losses

LEC_THRESHOLDS = (250_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000, 20_000_000)


def friction_cost(fp_rate, annual_queries, minutes_lost, hourly_cost):
    """Cost of legitimate questions wrongly blocked (PRD FR-22)."""
    return fp_rate * annual_queries * minutes_lost / 60 * hourly_cost


def summarize(total: np.ndarray) -> dict:
    return {
        "eal": int(round(total.mean())),
        "p10": int(round(np.percentile(total, 10))),
        "p50": int(round(np.percentile(total, 50))),
        "p90": int(round(np.percentile(total, 90))),
        "loss_exceedance": [{"threshold": t, "probability": round(float((total > t).mean()), 4)}
                            for t in LEC_THRESHOLDS],
    }


def _row(name: str, value: Pert | Range90) -> dict:
    return {"input": name, "provenance": value.provenance, "source": value.source}


def inputs_provenance(model: Model) -> list[dict]:
    rows = [_row("degradation", model.degradation),
            _row("friction.minutes_lost", model.friction.minutes_lost),
            _row("friction.hourly_cost", model.friction.hourly_cost),
            _row("shadow_ai.elasticity", model.shadow_ai.elasticity),
            {"input": "friction.annual_queries", "provenance": "Assumed", "source": model.friction.queries_source}]
    for s in model.scenarios:
        rows += [_row(f"{s.scenario_id}.events_per_year", s.events_per_year),
                 _row(f"{s.scenario_id}.loss_per_event", s.loss_per_event)]
    for st in model.strategies:
        rows.append(_row(f"{st.strategy_id}.annual_run_cost", st.annual_run_cost))
        rows += [_row(f"{st.strategy_id}.assumed_block_rates.{sid}", p) for sid, p in st.assumed_block_rates.items()]
        if st.assumed_false_positive_rate is not None:
            rows.append(_row(f"{st.strategy_id}.assumed_false_positive_rate", st.assumed_false_positive_rate))
    return rows


def run_model(model: Model, harness: dict | None = None) -> dict:
    n = model.iterations
    raw = {}
    for strategy in model.strategies:
        vulns = vulnerabilities(model, strategy, harness)
        fp = false_positive_rate(strategy, harness)
        losses, fp_draws = simulate_losses(model, vulns, fp)
        cost_rng = np.random.default_rng(model.seed + 1)
        f = model.friction
        rc = strategy.annual_run_cost
        # Fixed draw order and one uniform per year keep cost draws common across strategies.
        run_cost = pert_ppf(cost_rng.random(n), rc.low, rc.mode, rc.high)
        minutes = pert_ppf(cost_rng.random(n), f.minutes_lost.low, f.minutes_lost.mode, f.minutes_lost.high)
        hourly = pert_ppf(cost_rng.random(n), f.hourly_cost.low, f.hourly_cost.mode, f.hourly_cost.high)
        raw[strategy.strategy_id] = {
            "strategy": strategy, "losses": losses, "total": sum(losses.values()),
            "run_cost": float(run_cost.mean()),
            "friction": float(friction_cost(fp_draws, f.annual_queries, minutes, hourly).mean()),
            "vulnerabilities": {sid: asdict(p) for sid, p in vulns.items()},
            "false_positive_rate": asdict(fp),
        }
    baseline_eal = float(raw["accept_risk"]["total"].mean())
    strategies = {}
    for sid, r in raw.items():
        summary = summarize(r["total"])
        cost = r["run_cost"] + r["friction"]
        reduction = baseline_eal - float(r["total"].mean())
        ratio = None if cost == 0 else reduction / cost
        strategies[sid] = {
            "name": r["strategy"].name,
            **summary,
            "eal_by_scenario": {k: int(round(v.mean())) for k, v in r["losses"].items()},
            "annual_run_cost": int(round(r["run_cost"])),
            "friction_cost": int(round(r["friction"])),
            "total_cost": int(round(cost)),
            "risk_reduction": int(round(reduction)),
            "reduction_to_cost": None if ratio is None else round(ratio, 2),
            "roi": None if cost == 0 else round((reduction - cost) / cost, 2),
            "meets_funding_test": ratio is not None and round(ratio, 2) >= model.funding_ratio,
            "within_appetite": summary["eal"] < model.appetite_eal and summary["p90"] < model.appetite_p90,
            "friction_within_limit": int(round(r["friction"])) <= model.friction_limit,
            "vulnerabilities": r["vulnerabilities"],
            "false_positive_rate": r["false_positive_rate"],
        }
    return {
        "iterations": n,
        "seed": model.seed,
        "harness_run_id": harness.get("run_id") if harness else None,
        "appetite": {"eal": model.appetite_eal, "p90": model.appetite_p90},
        "funding_ratio": model.funding_ratio,
        "strategies": strategies,
        "inputs": inputs_provenance(model),
    }


def write_results(results: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

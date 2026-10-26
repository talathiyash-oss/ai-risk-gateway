"""Display data for the CISO dashboard (FR-23 to FR-26).

Pure functions with no Streamlit, so every number shown can be tested and traced back to
results/fair.json (NFR-05).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from airg.fair.inputs import load_model

ROOT = Path(__file__).resolve().parents[3]
RESULTS_PATH = ROOT / "results" / "fair.json"
HARNESS_PATH = ROOT / "results" / "harness.json"
MODEL_PATH = ROOT / "config" / "fair_model.yaml"
BASELINE = "accept_risk"

OPTIONS_NOTES = (
    "**Return (avg yr)** is the average annual risk reduced per $1 of annual cost: run cost plus the cost "
    "of wrongly blocked questions. Risk reduced is net of the extra shadow-AI losses that false blocks cause "
    "(PRD FR-35). The CFO's 3:1 test uses this figure.\n\n"
    "**Year-to-year range** is the 10th to 90th percentile of the return across simulated years. It shows "
    "how lumpy the payoff is from one year to the next, not how uncertain the average is.\n\n"
    "**Search index fix** shows \"none ... (by design, see note)\" in the \"Worse than nothing\" column because the model "
    "gives it no way to backfire: it's assumed to add no false blocks, and it acts only on S1. Its run cost is an unconfirmed estimate, "
    "and it won't be ready for the January 2027 pilot (PRD A-6)."
)


def md_escape(text: str) -> str:
    """Escape dollar signs so Streamlit markdown does not treat $...$ as maths."""
    return text.replace("$", "\\$")


def load_results(path: str | Path = RESULTS_PATH) -> dict:
    return json.loads(Path(path).read_text())


def scenario_names(model_path: str | Path = MODEL_PATH) -> dict[str, str]:
    return {s.scenario_id: s.name for s in load_model(model_path).scenarios}


def _missing(x) -> bool:
    return x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x)))


def money(x) -> str:
    if _missing(x):
        return "n/a"
    sign = "-" if x < 0 else ""
    v = abs(x)
    if v >= 1e6 or round(v / 1e3) >= 1000:
        return f"{sign}${v / 1e6:.2f}M"
    if v >= 1e3:
        return f"{sign}${v / 1e3:.0f}K"
    return f"{sign}${v:,.0f}"


def ratio(x) -> str:
    return "n/a" if _missing(x) else f"{x:.1f} : 1"


def flag(x) -> str:
    return "n/a" if x is None else ("yes" if x else "no")


def worse_text(p, iterations: int | None = None) -> str:
    if _missing(p):
        return "n/a"
    if p == 0:
        return f"none in {iterations:,} simulated years (by design, see note)" if iterations else "none in the simulated years"
    if p >= 0.5:
        return f"{p:.0%} of years"
    return f"1 year in {max(2, round(1 / p))}"


def options(results: dict) -> dict[str, str]:
    """Strategy id to display name, excluding the do-nothing baseline."""
    return {sid: s["name"] for sid, s in results["strategies"].items() if sid != BASELINE}


def lowest_eal_strategy(results: dict) -> str:
    return min(options(results), key=lambda sid: results["strategies"][sid]["eal"])


def executive_summary(results: dict, strategy_id: str) -> dict:
    strategies = results["strategies"]
    base, chosen = strategies[BASELINE], strategies[strategy_id]
    ranked = sorted((s for sid, s in strategies.items() if sid != BASELINE and s["reduction_to_cost"] is not None),
                    key=lambda s: s["reduction_to_cost"], reverse=True)
    largest = max(chosen["eal_by_scenario"], key=chosen["eal_by_scenario"].get)
    return {
        "name": chosen["name"],
        "baseline_eal": base["eal"],
        "baseline_p90": base["p90"],
        "eal": chosen["eal"],
        "p90": chosen["p90"],
        "reduction_pct": round(100 * (base["eal"] - chosen["eal"]) / base["eal"], 1) if base["eal"] else 0.0,
        "return": chosen["reduction_to_cost"],
        "meets_funding_test": chosen["meets_funding_test"],
        "top_by_return": [(s["name"], s["reduction_to_cost"]) for s in ranked[:3]],
        "within_appetite": [s["name"] for sid, s in strategies.items() if sid != BASELINE and s["within_appetite"]],
        "appetite": results["appetite"],
        "largest_remaining_scenario": largest,
        "largest_remaining_eal": chosen["eal_by_scenario"][largest],
    }


def funding_verdict(meets) -> str:
    if meets is None:
        return "n/a"
    return "Meets 3:1" if meets else "Below 3:1, consider accepting the risk"


def options_table(results: dict) -> list[dict]:
    rows = []
    for s in results["strategies"].values():
        rr = s.get("return_range")
        rows.append({
            "Option": s["name"],
            "Expected loss": money(s["eal"]),
            "1-in-10 yr": money(s["p90"]),
            "False-block rate (likely)": f"{s['false_positive_rate']['mode']:.1%}",
            "Run cost": money(s["annual_run_cost"]),
            "Friction": money(s["friction_cost"]),
            "Total cost": money(s["total_cost"]),
            "Risk reduced": money(s["risk_reduction"]),
            "Return (avg yr)": ratio(s["reduction_to_cost"]),
            "3:1?": flag(s["meets_funding_test"]),
            "Funding verdict": funding_verdict(s["meets_funding_test"]),
            "Year-to-year range": "n/a" if not rr else f"{rr['low']:.1f} to {rr['high']:.1f} : 1",
            "Worse than nothing": worse_text(s.get("p_worse_than_nothing"), results.get("iterations")),
            "Within appetite": flag(s["within_appetite"]),
            "Friction within limit": flag(s["friction_within_limit"]),
        })
    return rows


def increments_table(results: dict) -> list[dict]:
    names = {sid: s["name"] for sid, s in results["strategies"].items()}
    return [{
        "Change": f"{names[i['to']]} instead of {names[i['from']]}",
        "Added cost a year": money(i["added_cost"]),
        "Less expected loss": money(i["added_reduction"]),
        "Return": ratio(i["ratio"]),
        "3:1?": flag(i["meets_funding_test"]),
    } for i in results.get("increments", [])]


def loss_exceedance_rows(results: dict, strategy_ids: list[str]) -> list[dict]:
    strategies = results["strategies"]
    points = strategies[strategy_ids[0]]["loss_exceedance"]
    rows = []
    for i, point in enumerate(points):
        row = {"Loss above": point["threshold"]}
        for sid in strategy_ids:
            row[strategies[sid]["name"]] = strategies[sid]["loss_exceedance"][i]["probability"]
        rows.append(row)
    return rows


def scenario_rows(results: dict, strategy_id: str, names: dict[str, str]) -> list[dict]:
    base = results["strategies"][BASELINE]["scenarios"]
    chosen = results["strategies"][strategy_id]["scenarios"]
    return [{
        "Scenario": f"{sid} {names.get(sid, '')}".strip(),
        "Expected loss, doing nothing": money(base[sid]["eal"]),
        "Expected loss, with option": money(chosen[sid]["eal"]),
        "1-in-10 yr, doing nothing": money(base[sid]["p90"]),
        "1-in-10 yr, with option": money(chosen[sid]["p90"]),
    } for sid in base]


def effectiveness_rows(results: dict, names: dict[str, str]) -> list[dict]:
    rows = []
    for strategy_id, s in results["strategies"].items():
        if strategy_id == BASELINE:
            continue
        for sid, v in s["vulnerabilities"].items():
            if sid == "S5":
                continue
            rows.append({
                "Option": s["name"],
                "Scenario": f"{sid} {names.get(sid, '')}".strip(),
                "Attempts that still succeed (low / likely / high)": f"{v['low']:.0%} / {v['mode']:.0%} / {v['high']:.0%}",
                "Label": v["provenance"],
                "Measured block rate": "see source" if v["provenance"] == "Measured" else "not measured yet",
                "Source": v["source"],
            })
    return rows


def provenance_rows(results: dict, assumed_only: bool = False) -> list[dict]:
    rows = [{"Input": r["input"], "Label": r["provenance"], "Source": r["source"]} for r in results["inputs"]]
    return [r for r in rows if r["Label"] == "Assumed"] if assumed_only else rows


def provenance_counts(results: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in results["inputs"]:
        counts[r["provenance"]] = counts.get(r["provenance"], 0) + 1
    return dict(sorted(counts.items()))


def compare_rows(original: dict, what_if: dict) -> list[dict]:
    rows = []
    for sid, s in original["strategies"].items():
        w = what_if["strategies"][sid]
        rows.append({
            "Option": s["name"],
            "Expected loss": money(s["eal"]),
            "Expected loss (what-if)": money(w["eal"]),
            "Return": ratio(s["reduction_to_cost"]),
            "Return (what-if)": ratio(w["reduction_to_cost"]),
            "3:1? (what-if)": flag(w["meets_funding_test"]),
        })
    return rows

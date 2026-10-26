"""Run the FAIR risk model and write results/fair.json (Sprint 2B)."""
import json
from collections import Counter
from pathlib import Path

from airg.fair.inputs import load_model
from airg.fair.report import run_model, write_results

MODEL_PATH = Path("config/fair_model.yaml")
HARNESS_PATH = Path("results/harness.json")
RESULTS_PATH = Path("results/fair.json")


def money(x: float) -> str:
    return f"${x / 1e6:.2f}M" if abs(x) >= 1e6 else f"${x / 1e3:.0f}K"


def ratio(x) -> str:
    return "n/a" if x is None else f"{x:.1f} : 1"


def flag(x) -> str:
    return "n/a" if x is None else ("yes" if x else "no")


def main() -> None:
    model = load_model(MODEL_PATH)
    harness = json.loads(HARNESS_PATH.read_text()) if HARNESS_PATH.exists() else None
    results = run_model(model, harness)
    write_results(results, RESULTS_PATH)

    source = (f"control effectiveness measured in harness run {results['harness_run_id']}" if harness
              else "no harness results yet, so control effectiveness is Assumed")
    print(f"\nFAIR model: {model.iterations:,} simulated years, seed {model.seed}; {source}\n")

    print(f"{'Option':26}{'Expected loss':>14}{'1-in-10 yr':>12}{'Annual cost':>13}"
          f"{'Return (avg yr)':>17}{'3:1?':>6}{'Year-to-year range':>21}{'Worse than nothing':>20}")
    print("-" * 129)
    for s in results["strategies"].values():
        rr = s.get("return_range")
        rng = "n/a" if not rr else f"{rr['low']:.1f} to {rr['high']:.1f} : 1"
        worse = s.get("p_worse_than_nothing")
        worse_txt = "n/a" if worse is None else (f"1 year in {round(1 / worse)}" if worse > 0 else "never*")
        print(f"{s['name']:26}{money(s['eal']):>14}{money(s['p90']):>12}{money(s['total_cost']):>13}"
              f"{ratio(s['reduction_to_cost']):>17}{flag(s['meets_funding_test']):>6}{rng:>21}{worse_txt:>20}")

    names = {k: v["name"] for k, v in results["strategies"].items()}
    print("\nAdding one option on top of another")
    for i in results["increments"]:
        print(f"  {names[i['to']]} instead of {names[i['from']]}: +{money(i['added_cost'])} a year buys "
              f"{money(i['added_reduction'])} less expected loss ({ratio(i['ratio'])}, 3:1? {flag(i['meets_funding_test'])})")

    print("\nReturn (avg yr) = average annual risk reduced per $1 of annual cost (run cost plus the cost")
    print("  of wrongly blocked questions). Risk reduced is net of extra shadow-AI losses caused by")
    print("  false blocks (PRD FR-35). The 3:1 test uses this figure.")
    print("Year-to-year range = 10th to 90th percentile of the return across simulated years. It shows")
    print("  how lumpy the payoff is from year to year, not how uncertain the average is. A negative")
    print("  value is a year when losses were higher than doing nothing, mainly from extra shadow-AI")
    print("  incidents caused by false blocks.")
    print("* The model gives the index fix no way to backfire: it is assumed to add no false blocks and acts only on S1.")
    print("  Its run cost is an unconfirmed estimate, and it will not be ready for the January 2027 pilot (PRD A-6).")

    a = results["appetite"]
    within = [s["name"] for s in results["strategies"].values() if s["within_appetite"]]
    print(f"\nRisk appetite (CISO proposal, not yet agreed): expected loss under {money(a['eal'])} "
          f"and 1-in-10-year loss under {money(a['p90'])}.")
    print("Options within appetite: " + (", ".join(within) if within else
          "none. No option alone brings the bank within appetite."))

    over = [s["name"] for s in results["strategies"].values() if not s["friction_within_limit"]]
    if over:
        print(f"Friction above the {money(model.friction_limit)} limit (BRD BO-3): " + ", ".join(over))

    baseline = results["strategies"]["accept_risk"]["eal_by_scenario"]
    print("\nExpected loss by scenario if nothing is done: "
          + ", ".join(f"{k} {money(v)}" for k, v in baseline.items()))
    counts = Counter(row["provenance"] for row in results["inputs"])
    print("Inputs by label: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print(f"\nWrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()

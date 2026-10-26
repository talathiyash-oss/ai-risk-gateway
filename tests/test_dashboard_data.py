import pytest

from airg.dashboard import data


@pytest.fixture(scope="module")
def results():
    return data.load_results()


def test_money_formats():
    assert [data.money(x) for x in (None, 0, 950, 52_000, 4_480_000)] == ["n/a", "$0", "$950", "$52K", "$4.48M"]


def test_ratio_flag_and_worse_text():
    assert (data.ratio(None), data.ratio(5.78)) == ("n/a", "5.8 : 1")
    assert (data.flag(None), data.flag(True), data.flag(False)) == ("n/a", "yes", "no")
    assert (data.worse_text(None), data.worse_text(0), data.worse_text(0.141)) == ("n/a", "never", "1 year in 7")


def test_options_exclude_baseline(results):
    assert "accept_risk" not in data.options(results)
    assert len(data.options(results)) == len(results["strategies"]) - 1


def test_executive_summary(results):
    sid = data.lowest_eal_strategy(results)
    s = data.executive_summary(results, sid)
    base, chosen = results["strategies"]["accept_risk"], results["strategies"][sid]
    assert s["eal"] == chosen["eal"] and s["baseline_eal"] == base["eal"]
    assert s["reduction_pct"] == round(100 * (base["eal"] - chosen["eal"]) / base["eal"], 1)
    returns = [r for _, r in s["top_by_return"]]
    assert returns == sorted(returns, reverse=True) and len(returns) <= 3
    assert all(name != base["name"] for name, _ in s["top_by_return"])
    assert s["largest_remaining_scenario"] in chosen["eal_by_scenario"]
    assert s["within_appetite"] == [v["name"] for k, v in results["strategies"].items()
                                    if k != "accept_risk" and v["within_appetite"]]


def test_options_table(results):
    rows = data.options_table(results)
    assert len(rows) == len(results["strategies"])
    baseline = next(r for r in rows if r["Option"] == results["strategies"]["accept_risk"]["name"])
    assert (baseline["Return (avg yr)"], baseline["3:1?"], baseline["Worse than nothing"]) == ("n/a", "n/a", "n/a")


def test_increments_table(results):
    rows = data.increments_table(results)
    assert len(rows) == len(results["increments"])
    assert all(" instead of " in r["Change"] for r in rows)


def test_loss_exceedance_rows(results):
    ids = ["accept_risk", data.lowest_eal_strategy(results)]
    rows = data.loss_exceedance_rows(results, ids)
    thresholds = [r["Loss above"] for r in rows]
    assert thresholds == sorted(thresholds)
    for sid in ids:
        column = [r[results["strategies"][sid]["name"]] for r in rows]
        assert column == sorted(column, reverse=True)


def test_scenario_rows(results):
    rows = data.scenario_rows(results, "gateway", data.scenario_names())
    assert len(rows) == len(results["strategies"]["accept_risk"]["scenarios"])
    assert rows[0]["Scenario"].startswith("S1 ")


def test_effectiveness_rows(results):
    rows = data.effectiveness_rows(results, data.scenario_names())
    assert len(rows) == sum(len(s["vulnerabilities"]) for s in results["strategies"].values())
    assert all(r["Measured block rate"] in ("see source", "not measured yet") for r in rows)


def test_provenance_rows_and_filter(results):
    everything = data.provenance_rows(results)
    assumed = data.provenance_rows(results, assumed_only=True)
    assert len(everything) == len(results["inputs"])
    assert assumed and all(r["Label"] == "Assumed" for r in assumed)
    assert sum(data.provenance_counts(results).values()) == len(everything)


def test_compare_rows_identical_inputs(results):
    rows = data.compare_rows(results, results)
    assert all(r["Expected loss"] == r["Expected loss (what-if)"] for r in rows)

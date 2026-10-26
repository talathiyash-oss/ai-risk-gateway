import time

import pytest

from airg.dashboard.data import load_results
from airg.dashboard.whatif import WhatIf, run_what_if


@pytest.fixture(scope="module")
def base():
    return run_what_if(WhatIf())


def test_defaults_reproduce_committed_results(base):
    assert base["strategies"] == load_results()["strategies"]


def test_more_attacks_raise_expected_loss(base):
    changed = run_what_if(WhatIf(attack_frequency=2.0))
    assert changed["strategies"]["accept_risk"]["eal_by_scenario"]["S2"] > 1.5 * base["strategies"]["accept_risk"]["eal_by_scenario"]["S2"]


def test_more_exposure_raises_s1(base):
    changed = run_what_if(WhatIf(exposure_frequency=2.0))
    assert changed["strategies"]["accept_risk"]["eal_by_scenario"]["S1"] > 1.5 * base["strategies"]["accept_risk"]["eal_by_scenario"]["S1"]


def test_stronger_elasticity_raises_gateway_shadow_ai(base):
    changed = run_what_if(WhatIf(elasticity=1.5))
    assert changed["strategies"]["gateway"]["eal_by_scenario"]["S5"] > base["strategies"]["gateway"]["eal_by_scenario"]["S5"]


def test_more_capable_attackers_raise_gateway_loss(base):
    changed = run_what_if(WhatIf(degradation=0.40))
    assert changed["strategies"]["gateway"]["eal"] > base["strategies"]["gateway"]["eal"]


def test_gateway_cost_multiplier(base):
    changed = run_what_if(WhatIf(gateway_cost=2.0))
    assert changed["strategies"]["gateway"]["annual_run_cost"] == pytest.approx(
        2 * base["strategies"]["gateway"]["annual_run_cost"], rel=0.01)
    assert changed["strategies"]["vendor_firewall"]["annual_run_cost"] == base["strategies"]["vendor_firewall"]["annual_run_cost"]


def test_changed_inputs_are_labelled_as_what_if():
    changed = run_what_if(WhatIf(attack_frequency=2.0))
    row = next(r for r in changed["inputs"] if r["input"] == "S2.events_per_year")
    assert row["provenance"] == "Assumed" and row["source"].startswith("What-if")


def test_reruns_within_ten_seconds():
    start = time.perf_counter()
    run_what_if(WhatIf(attack_frequency=2.0))
    assert time.perf_counter() - start < 10

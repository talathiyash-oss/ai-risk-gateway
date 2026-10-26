from airg.dashboard import compliance


def test_owasp_coverage_lists_all_ten_in_order():
    assert [r["Risk"].split()[0] for r in compliance.OWASP_COVERAGE] == [f"LLM{i:02d}" for i in range(1, 11)]
    assert all(r["Owner"] for r in compliance.OWASP_COVERAGE)


def test_control_register_ids_and_status():
    ids = [r["ID"] for r in compliance.CONTROL_REGISTER]
    assert ids == ["GR-01", "GR-02", "GR-03", "GR-04", "GR-05", "GR-06", "FAIR engine"]
    gr06 = compliance.CONTROL_REGISTER[5]
    assert gr06["Status"].startswith("Planned")
    assert all(r["Status"].startswith("Built") for r in compliance.CONTROL_REGISTER[:5])
    assert compliance.CONTROL_REGISTER[-1]["Status"] == "Built (Sprint 2B)"


def test_control_register_has_sr_26_2_column():
    rows = compliance.CONTROL_REGISTER
    assert all("SR 26-2" in r for r in rows)
    assert [r["SR 26-2"] for r in rows if r["ID"] in ("GR-01", "GR-02", "GR-03", "GR-04", "GR-06")] == \
        ["Out of scope (generative AI)"] * 5
    assert next(r for r in rows if r["ID"] == "GR-05")["SR 26-2"] == "Supports ongoing monitoring evidence"


def test_llm04_coverage_mentions_injected_instructions():
    llm04 = next(r for r in compliance.OWASP_COVERAGE if r["Risk"].startswith("LLM04"))
    assert llm04["Coverage"] == "Partly: documents containing injected instructions are removed by GR-01"


def test_applicability_mentions_the_corrected_model_risk_guidance():
    frameworks = " ".join(r["Framework"] for r in compliance.APPLICABILITY)
    assert "SR 26-2" in frameworks and "SR 11-7" in frameworks
    assert all(set(r) == {"Framework", "Applies to Brindlemoor?", "How it's used"} for r in compliance.APPLICABILITY)


def test_citation_note_present():
    assert "primary sources" in compliance.CITATION_NOTE

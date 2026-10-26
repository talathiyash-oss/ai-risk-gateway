from airg.dashboard import compliance


def test_owasp_coverage_lists_all_ten_in_order():
    assert [r["Risk"].split()[0] for r in compliance.OWASP_COVERAGE] == [f"LLM{i:02d}" for i in range(1, 11)]
    assert all(r["Owner"] for r in compliance.OWASP_COVERAGE)


def test_control_register_ids_and_status():
    assert [r["ID"] for r in compliance.CONTROL_REGISTER] == ["GR-01", "GR-02", "GR-03", "GR-04", "GR-05", "GR-06"]
    gr06 = compliance.CONTROL_REGISTER[-1]
    assert gr06["Status"].startswith("Planned")
    assert all(r["Status"].startswith("Built") for r in compliance.CONTROL_REGISTER[:5])


def test_applicability_mentions_the_corrected_model_risk_guidance():
    frameworks = " ".join(r["Framework"] for r in compliance.APPLICABILITY)
    assert "SR 26-2" in frameworks and "SR 11-7" in frameworks
    assert all(set(r) == {"Framework", "Applies to Brindlemoor?", "How it's used"} for r in compliance.APPLICABILITY)


def test_citation_note_present():
    assert "primary sources" in compliance.CITATION_NOTE

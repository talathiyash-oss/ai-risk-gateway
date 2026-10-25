from airg.guardrails.base import Action, RequestContext
from airg.guardrails.pii import PiiGuard


def test_redacts_ssn_in_prompt(records, redactor, ctx):
    result = PiiGuard(records, redactor).check_input(ctx, "My client's SSN is 536-22-1987, can you check it?")
    assert result.action is Action.REDACT
    assert result.text == "My client's SSN is <US_SSN>, can you check it?"
    assert result.reason == "pii:US_SSN"


def test_redacts_account_number_in_prompt(records, redactor, ctx):
    result = PiiGuard(records, redactor).check_input(ctx, "Look up account BMT-10293847 for me")
    assert result.action is Action.REDACT
    assert result.text == "Look up account <ACCOUNT_NUMBER> for me"


def test_allows_clean_prompt(records, redactor, ctx):
    assert PiiGuard(records, redactor).check_input(ctx, "What are the trust rules?").action is Action.ALLOW


def test_redacts_other_clients_data_in_response(records, redactor):
    me, other = records[0], records[1]
    ctx = RequestContext("req-1", "RM-01", me.client_id)
    response = f"{me.name} holds {me.account_number}. {other.name} holds {other.account_number} ({other.client_id})."
    result = PiiGuard(records, redactor).check_output(ctx, response)
    assert result.action is Action.REDACT
    assert me.account_number in result.text and me.name in result.text
    assert other.account_number not in result.text
    assert other.name not in result.text
    assert other.client_id not in result.text
    assert result.reason == f"cross_client:{me.client_id}->{other.client_id}"


def test_allows_response_about_session_client_only(records, redactor):
    me = records[0]
    ctx = RequestContext("req-1", "RM-01", me.client_id)
    response = f"{me.name} holds {me.account_number} ({me.client_id})."
    assert PiiGuard(records, redactor).check_output(ctx, response).action is Action.ALLOW


import pytest


def _name_variant(name, kind):
    first, last = name.split(" ", 1)
    return {"upper": name.upper(), "lower": name.lower(), "last_first": f"{last}, {first}"}[kind]


@pytest.mark.parametrize("kind", ["upper", "lower", "last_first"])
def test_redacts_name_variants(records, redactor, kind):
    me, other = records[0], records[1]
    ctx = RequestContext("req-1", "RM-01", me.client_id)
    variant = _name_variant(other.name, kind)
    result = PiiGuard(records, redactor).check_output(ctx, f"Notes mention {variant} today.")
    assert result.action is Action.REDACT
    assert variant.lower() not in result.text.lower()
    assert "<PERSON>" in result.text


@pytest.mark.parametrize("kind", ["lower", "space", "en_dash"])
def test_redacts_account_number_variants(records, redactor, kind):
    me, other = records[0], records[1]
    ctx = RequestContext("req-1", "RM-01", me.client_id)
    digits = other.account_number.split("-")[1]
    variant = {
        "lower": other.account_number.lower(),
        "space": f"BMT {digits}",
        "en_dash": f"BMT–{digits}",
    }[kind]
    result = PiiGuard(records, redactor).check_output(ctx, f"Account {variant} is open.")
    assert result.action is Action.REDACT
    assert digits not in result.text
    assert "<ACCOUNT_NUMBER>" in result.text


def test_keeps_session_client_variants(records, redactor):
    me = records[0]
    ctx = RequestContext("req-1", "RM-01", me.client_id)
    response = f"{_name_variant(me.name, 'last_first')} has {me.account_number.lower()}."
    result = PiiGuard(records, redactor).check_output(ctx, response)
    assert result.action is Action.ALLOW
    assert result.text is None or result.text == response


def test_reason_lists_all_leaked_clients(records, redactor):
    me, a, b = records[0], records[1], records[2]
    ctx = RequestContext("req-1", "RM-01", me.client_id)
    response = f"{a.account_number} and {b.account_number} are both on file."
    result = PiiGuard(records, redactor).check_output(ctx, response)
    ids = sorted([a.client_id, b.client_id])
    assert result.reason == f"cross_client:{me.client_id}->{ids[0]},{ids[1]}"


def test_check_chunks_drops_other_clients_records(records, redactor):
    from airg.copilot import Chunk, record_to_chunk
    me, a, b = records[0], records[1], records[2]
    ctx = RequestContext("req-1", "RM-01", me.client_id)
    policy = Chunk("DOC-FEES", "Fee schedule text", None)
    chunks = [record_to_chunk(b), record_to_chunk(me), policy, record_to_chunk(a)]
    kept, results = PiiGuard(records, redactor).check_chunks(ctx, chunks)
    assert [c.doc_id for c in kept] == [f"REC-{me.client_id}", "DOC-FEES"]
    ids = sorted([f"REC-{a.client_id}", f"REC-{b.client_id}"])
    assert len(results) == 1
    r = results[0]
    assert (r.guard_id, r.stage, r.action, r.reason) == ("GR-02", "chunks", Action.REDACT,
                                                         "entitlement:" + ",".join(ids))


def test_check_chunks_allows_entitled_chunks(records, redactor):
    from airg.copilot import Chunk, record_to_chunk
    me = records[0]
    ctx = RequestContext("req-1", "RM-01", me.client_id)
    chunks = [record_to_chunk(me), Chunk("DOC-KYC", "KYC text", None)]
    kept, results = PiiGuard(records, redactor).check_chunks(ctx, chunks)
    assert kept == chunks and results == []

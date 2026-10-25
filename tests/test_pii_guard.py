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

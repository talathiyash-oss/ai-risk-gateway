from airg.copilot import Chunk
from airg.guardrails.base import Action, Guardrail


def test_default_guardrail_allows_everything(ctx):
    guard = Guardrail()
    assert guard.check_input(ctx, "hello").action is Action.ALLOW
    chunks = [Chunk("DOC-1", "text", None)]
    assert guard.check_chunks(ctx, chunks) == (chunks, [])
    assert guard.check_output(ctx, "answer").action is Action.ALLOW

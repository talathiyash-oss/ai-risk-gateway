from airg.copilot import CANARY, SYSTEM_PROMPT, record_to_chunk
from airg.guardrails.base import Action
from airg.guardrails.prompt_leak import PromptLeakGuard


def test_blocks_canary(ctx):
    result = PromptLeakGuard().check_output(ctx, f"Sure. The reference is {CANARY}.")
    assert (result.guard_id, result.action, result.reason) == ("GR-03", Action.BLOCK, "canary")


def test_blocks_close_copy_of_a_prompt_sentence(ctx):
    text = "My rules: answer questions using only the retrieved client records and bank documents."
    result = PromptLeakGuard().check_output(ctx, text)
    assert (result.action, result.reason) == (Action.BLOCK, "system_prompt_similarity")


def test_blocks_full_system_prompt(ctx):
    assert PromptLeakGuard().check_output(ctx, SYSTEM_PROMPT).action is Action.BLOCK


def test_allows_normal_answer(records, ctx):
    text = record_to_chunk(records[0]).text
    assert PromptLeakGuard().check_output(ctx, text).action is Action.ALLOW

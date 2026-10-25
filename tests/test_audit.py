import json

from airg.audit import AuditLog
from airg.guardrails.base import Action, GuardResult, RequestContext

CTX = RequestContext("req-1", "RM-01", "C-1001")


def test_one_entry_per_request_with_all_fields(tmp_path, redactor, clock):
    log = AuditLog(tmp_path / "audit.jsonl", redactor, clock=clock)
    decisions = [
        GuardResult("GR-01", "input", Action.ALLOW, "ok"),
        GuardResult("GR-02", "input", Action.REDACT, "pii:US_SSN", "redacted text"),
    ]
    log.record_request(ctx=CTX, decisions=decisions, final_action="redact",
                       latency_ms=12.345, prompt="hello", response="answer")
    [entry] = log.entries()
    assert set(entry) == {"event", "timestamp", "request_id", "user_id", "client_id",
                          "guardrails_evaluated", "decisions", "final_action", "latency_ms",
                          "prompt_redacted", "response_redacted"}
    assert entry["event"] == "request"
    assert entry["guardrails_evaluated"] == ["GR-01", "GR-02"]
    assert entry["decisions"][1] == {"guard_id": "GR-02", "stage": "input", "action": "redact", "reason": "pii:US_SSN"}
    assert entry["latency_ms"] == 12.35


def test_never_writes_raw_pii(tmp_path, redactor, clock):
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path, redactor, clock=clock)
    log.record_request(ctx=CTX, decisions=[], final_action="allow", latency_ms=1.0,
                       prompt="SSN is 536-22-1987", response="Account BMT-10293847 balance")
    raw = path.read_text()
    assert "536-22-1987" not in raw and "BMT-10293847" not in raw
    assert "<US_SSN>" in raw and "<ACCOUNT_NUMBER>" in raw


def test_purge_removes_entries_older_than_retention(tmp_path, redactor, clock):
    log = AuditLog(tmp_path / "audit.jsonl", redactor, clock=clock)
    clock.t = 0.0
    log.record_event("request", request_id="old")
    clock.t = 100 * 86_400
    log.record_event("request", request_id="new")
    assert log.purge(retention_days=30) == 1
    assert [e["request_id"] for e in log.entries()] == ["new"]


def test_export_date_range(tmp_path, redactor, clock):
    log = AuditLog(tmp_path / "audit.jsonl", redactor, clock=clock)
    for t, rid in [(10.0, "a"), (20.0, "b"), (30.0, "c")]:
        clock.t = t
        log.record_event("request", request_id=rid)
    out = tmp_path / "export.jsonl"
    assert log.export(start=15.0, end=35.0, out_path=out) == 2
    exported = [json.loads(line) for line in out.read_text().splitlines()]
    assert exported == log.entries()[1:]


def test_record_event(tmp_path, redactor, clock):
    log = AuditLog(tmp_path / "audit.jsonl", redactor, clock=clock)
    log.record_event("review_requested", review_id="rv-1")
    assert log.entries() == [{"event": "review_requested", "timestamp": clock.t, "review_id": "rv-1"}]


def test_record_event_scrubs_free_text(tmp_path, redactor, clock):
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path, redactor, clock=clock)
    log.record_event("note", text="SSN 536-22-1987")
    raw = path.read_text()
    assert "536-22-1987" not in raw
    assert "<US_SSN>" in raw


def test_concurrent_writes_keep_every_line_valid(tmp_path, redactor, clock):
    import threading

    path = tmp_path / "audit.jsonl"
    log = AuditLog(path, redactor, clock=clock)
    big = "x" * 10_000

    def worker(n):
        for i in range(25):
            log.record_event("note", worker=n, i=i, text=big)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(log.entries()) == 200
    lines = path.read_text().splitlines()
    assert len(lines) == 200
    for line in lines:
        json.loads(line)


def test_entries_skip_corrupt_lines(tmp_path, redactor, clock):
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path, redactor, clock=clock)
    log.record_event("request", request_id="first")
    with path.open("a") as f:
        f.write("{not json\n")
    log.record_event("request", request_id="second")
    assert [e["request_id"] for e in log.entries()] == ["first", "second"]


def test_purge_leaves_no_temp_file(tmp_path, redactor, clock):
    log = AuditLog(tmp_path / "audit.jsonl", redactor, clock=clock)
    clock.t = 0.0
    log.record_event("request", request_id="old")
    clock.t = 100 * 86_400
    log.record_event("request", request_id="new")
    assert log.purge(retention_days=30) == 1
    assert list(tmp_path.glob("*.tmp")) == []

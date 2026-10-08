import json
import threading

import pytest

from qp import budget


@pytest.fixture(autouse=True)
def ledger(tmp_path, monkeypatch):
    path = tmp_path / "ledger.jsonl"
    monkeypatch.setenv("QP_LEDGER", str(path))
    monkeypatch.setenv("QP_BUDGET_USD", "10")
    return path


def test_price_per_token_type():
    m = 1_000_000
    assert budget.price({"input_tokens": m}) == pytest.approx(4.0)
    assert budget.price({"output_tokens": m}) == pytest.approx(20.0)
    assert budget.price({"cache_creation_input_tokens": m}) == pytest.approx(5.0)   # 1.25x, 5-min TTL
    assert budget.price({"cache_read_input_tokens": m}) == pytest.approx(0.20)
    one_hour = {"cache_creation_input_tokens": m, "cache_creation": {"ephemeral_1h_input_tokens": m}}
    assert budget.price(one_hour) == pytest.approx(8.0)
    mixed = {"input_tokens": 10_000, "output_tokens": 5_000, "cache_read_input_tokens": 2_000}
    assert budget.price(mixed) == pytest.approx(0.04 + 0.10 + 0.0004)
    assert budget.price(mixed, batch=True) == pytest.approx((0.04 + 0.10 + 0.0004) / 2)


def test_price_accepts_sdk_usage_and_none_fields():
    from anthropic.types import Usage
    u = Usage(input_tokens=1000, output_tokens=2000, cache_creation_input_tokens=None, cache_read_input_tokens=None)
    assert budget.price(u) == pytest.approx(0.004 + 0.04)


def test_unknown_model_is_priced_conservatively():
    with pytest.warns(UserWarning):
        assert budget.price({"output_tokens": 1_000_000}, model="claude-new") >= 20.0


def test_record_spent_and_ledger_format(ledger):
    e = budget.record("run1", "claude-opus-5-5", "sync", "req_1", {"input_tokens": 1000, "output_tokens": 1000},
                      video_id="v1")
    budget.record("run1", "claude-opus-5-5", "batch", "b1/v2", {"input_tokens": 1000, "output_tokens": 1000})
    assert e["usd"] == pytest.approx(0.024)
    assert budget.spent() == pytest.approx(0.024 + 0.012)
    lines = [json.loads(x) for x in ledger.read_text().splitlines()]
    assert {"ts", "run", "model", "mode", "id", "input_tokens", "output_tokens", "cache_creation_input_tokens",
            "cache_read_input_tokens", "usd"} <= set(lines[0])
    assert lines[0]["video_id"] == "v1" and lines[1]["mode"] == "batch"
    with pytest.raises(ValueError):
        budget.record("run1", "claude-opus-5-5", "stream", "x", {})


def test_check_enforces_cap():
    assert budget.check(9.0) == pytest.approx(1.0)
    budget.record("r", "claude-opus-5-5", "sync", "a", {}, usd=6.0)
    budget.check(4.0)
    with pytest.raises(budget.BudgetExceeded):
        budget.check(4.01)


def test_holds_count_until_released():
    budget.hold("r", "batch_1", 7.0)
    assert budget.committed() == pytest.approx(7.0)
    with pytest.raises(budget.BudgetExceeded):
        budget.check(5.0)
    budget.record("r", "claude-opus-5-5", "batch", "batch_1/v", {}, usd=3.0)
    budget.release("batch_1")
    assert budget.committed() == pytest.approx(3.0)
    budget.check(5.0)


def test_reserve_blocks_concurrent_overspend():
    with budget.reserve(6.0):
        assert budget.committed() == pytest.approx(6.0)
        with pytest.raises(budget.BudgetExceeded):
            with budget.reserve(6.0):
                pass
    assert budget.committed() == pytest.approx(0.0)


def test_thread_safe_appends(ledger):
    def work(k):
        for i in range(50):
            budget.record("r", "claude-opus-5-5", "sync", f"{k}-{i}", {"input_tokens": 1000})

    threads = [threading.Thread(target=work, args=(k,)) for k in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    lines = ledger.read_text().splitlines()
    assert len(lines) == 800 and all(json.loads(x)["usd"] == 0.004 for x in lines)
    assert budget.spent() == pytest.approx(800 * 0.004)


def test_hold_stores_recovery_fields(ledger):
    budget.hold("r", "batch_9", 2.5, split="val", custom_ids={"v1": "vid 1"}, config={"effort": "high"})
    (e,) = budget.entries()
    assert e["type"] == "hold" and e["usd"] == 2.5 and e["split"] == "val"
    assert e["custom_ids"] == {"v1": "vid 1"} and e["config"] == {"effort": "high"}
    assert budget.open_holds() == {"batch_9": 2.5}

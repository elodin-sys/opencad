"""Prism-hosted turns: usage rebuilt from a SubAgent block the way worker/prism_host.py reads Prism's thread store."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from opencad.worker import prism_host


def _block(agent_id: str, written: Path) -> dict:
    tools = [
        ["exec_command", "c1", "Elapsed: 0.01 s\nProcess exited with code 0\nOutput size: ~1000 tokens\nOutput:\n" + "x" * 4000],
        ["write_file", "c2", f"write_file: updated {written}"],
        ["view_image", "c3", "[image]"],
        ["notify_parent", "c4", "The main agent has been notified."],
    ]
    turns = [{"kind": "tool", "text": "c1"}, {"kind": "tool", "text": "c2"}, {"kind": "tool", "text": "c3"},
             {"kind": "report", "text": "r" * 400}, {"kind": "tool", "text": "c4"}]
    return {"agent_id": agent_id, "model": "gpt-6-astra", "tools": tools, "turns": turns, "text": "done",
            "usage": {"context_tokens": 20_050, "input_tokens": 20_000, "output_tokens": 50}}


def test_estimate_pins_the_final_request_and_sums_every_request(tmp_path: Path):
    written = tmp_path / "main.py"
    written.write_text("a" * 4000)  # 1000 tokens of write_file arguments
    u = prism_host.estimate_usage(_block("a1", written))
    # deltas: exec 80 + 1040, write 1000 + 83//4, image 30 + 1600, report 100, notify 0 + 34//4
    deltas = [80 + 1040, 1000 + len(f"write_file: updated {written}") // 4, 30 + 1600, 100, 0 + len("The main agent has been notified.") // 4]
    base = 20_000 - sum(deltas)
    inputs = [base, base + deltas[0], base + sum(deltas[:2]), base + sum(deltas[:4]), 20_000]
    assert u["requests"] == 5 and u["final_input"] == 20_000 and u["base_context"] == base and not u["scaled"]
    assert u["input"] == sum(inputs) and u["cached"] == sum(inputs[:-1])
    assert u["output"] == 80 + 1000 + 30 + 100 + 0 + 50 and u["reasoning"] == 0


def test_estimate_scales_a_transcript_larger_than_the_measured_context(tmp_path: Path):
    b = _block("a2", tmp_path / "missing.py")
    b["usage"] = {"context_tokens": 2_600, "input_tokens": 2_500, "output_tokens": 100}
    u = prism_host.estimate_usage(b)
    assert u["scaled"] and prism_host.MIN_BASE_CONTEXT <= u["base_context"] < prism_host.MIN_BASE_CONTEXT + 10 and u["final_input"] == 2_500


def test_usage_for_agents_reads_the_thread_store_and_sums_a_redispatched_order(tmp_path: Path, monkeypatch):
    db = tmp_path / "chat.sqlite"
    con = sqlite3.connect(db)
    con.execute("create table thread_records (id text primary key, local text, source text)")
    source = json.dumps([{"blocks": [{"SubAgent": _block("a1", tmp_path / "x.py")}, {"Text": "hi"}]},
                         {"blocks": [{"SubAgent": _block("a2", tmp_path / "x.py")}]}])
    con.execute("insert into thread_records values ('t', '{}', ?)", (source,))
    con.commit()
    con.close()
    monkeypatch.setenv("OPENCAD_PRISM_THREADS", str(db))
    one = prism_host.usage_for_agents(["a1"])
    both = prism_host.usage_for_agents(["a1", "a2", "a1"])
    assert one["mode"] == "prism-estimate" and both["input"] == 2 * one["input"] and len(both["agents"]) == 2
    assert prism_host.usage_for_agents(["nobody"]) is None
    order = tmp_path / "order"
    order.mkdir()
    (order / "dispatch.json").write_text(json.dumps({"agent_id": "a2", "dispatches": [{"agent_id": "a1"}, {"agent_id": "a2"}]}))
    assert prism_host.dispatched_agents(order) == ["a1", "a2"]
    assert prism_host.usage_for_order(order)["requests"] == 10

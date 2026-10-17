"""Telemetry rows, aggregation, comparison, alerts, bench reports and baseline promotion."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from opencad import telemetry
from opencad.worker.result import WorkerResult


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(telemetry, "results_of", lambda name: tmp_path / "results" / name)
    monkeypatch.setattr(telemetry, "CAMPAIGN_FILE", tmp_path / "results" / "_campaign" / "telemetry.jsonl")
    monkeypatch.setattr(telemetry, "BASELINE_POINTER", tmp_path / "no-baseline.json")
    monkeypatch.setenv("OPENCAD_TRANSCRIPTS", str(tmp_path / "transcripts"))
    telemetry._SEGMENT_CACHE.clear()
    yield


def test_turn_rows_alerts_and_summary(tmp_path: Path, capsys):
    results = tmp_path / "results" / "demo"
    cursor = WorkerResult(
        "agent-1",
        0,
        1200.0,
        40,
        {},
        tmp_path,
        "## Result\nok",
        backend="cursor",
        role="model",
        model="fable",
        order_id="002-model",
        metrics={
            "engine_ledger_calls": 9,
            "engine_ledger_seconds": 30.5,
            "self_corrections": 1,
            "files_changed": ["main.kcl"],
            "incomplete": False,
        },
    )
    row = telemetry.record("turn", "demo", telemetry.turn_data(cursor, budget_s=900), results_dir=results)
    assert row["over_budget"] and row["engine_calls"] == 9 and row["backend"] == "cursor" and "tokens_input" not in row
    assert "ALERT model turn 002-model took 1200 s" in capsys.readouterr().out
    codex = WorkerResult(
        "thr",
        0,
        600.0,
        20,
        {"input": 8_000_000, "cached": 7_900_000, "output": 40_000, "reasoning": 30_000},
        tmp_path,
        "## Result\nok",
        backend="codex",
        role="plan",
        model="gpt-6-astra",
    )
    row = telemetry.record("turn", "demo", telemetry.turn_data(codex, budget_s=900), results_dir=results)
    assert row["reasoning_share"] == 0.75 and not row["over_budget"]
    assert row["usd"] == 21.8 and row["price_card"] == "gpt-6-astra-fast-short-2026-10-14"
    assert "codex context" in capsys.readouterr().out
    telemetry.record(
        "stage",
        "demo",
        telemetry.stage_data(
            "inspect", 1224.0, False, [{"seconds": 95.0, "class": "ok"}, {"seconds": 2.0, "class": "transient"}]
        ),
        results_dir=results,
    )
    out = capsys.readouterr().out
    assert "stage inspect took 1224.0 s" in out and "an engine call took 95.0 s" in out
    telemetry.record(
        "gates",
        "demo",
        telemetry.gates_data(
            {"ok": False, "summary": {"pass": 9, "fail": 2}, "failed": ["features"], "retryable_failed": ["features"]}
        ),
        results_dir=results,
    )
    rows = telemetry.rows_for("demo")
    assert [r["kind"] for r in rows] == ["turn", "turn", "stage", "gates"] and len(
        telemetry.read(telemetry.CAMPAIGN_FILE)
    ) == 4
    s = telemetry.summarize(rows)
    assert (
        s["worker_s"] == 1800
        and s["evaluator_s"] == 1224
        and s["by_role"]["model"]["over_budget"] == 1
        and s["by_role"]["plan"]["reasoning_share"] == 0.75
        and s["usd"] == 21.8
        and s["by_role"]["plan"]["tokens_input"] == 8_000_000
    )
    assert s["by_stage"]["inspect"]["engine_calls"] == 2 and s["gates"] == {"evaluations": 1, "pass": 0, "retries": 0}
    text = telemetry.format_summary(s, "demo")
    assert "model" in text and "inspect" in text and "gates: 0/1 PASS" in text
    d = telemetry.design_summary("demo")
    assert (
        d["worker_s_by_role"] == {"model": 1200, "plan": 600}
        and d["backends"] == ["codex", "cursor"]
        and d["over_budget_turns"] == 1
    )


def test_attempt_row_and_compare(tmp_path: Path):
    results = tmp_path / "results" / "demo"
    for role, secs in (("plan", 300.0), ("model", 2000.0), ("retry", 2500.0)):
        r = WorkerResult("t", 0, secs, 5, {}, tmp_path, "## Result\nok", backend="cursor", role=role, model="m")
        telemetry.record("turn", "demo", telemetry.turn_data(r, budget_s=9999), results_dir=results)
    telemetry.record("stage", "demo", telemetry.stage_data("verify", 100.0, True, []), results_dir=results)
    entry = {
        "started": "2000-01-01T00:00:00Z",
        "seconds": 5000,
        "stage_reached": "scored",
        "scorecard": {"verdict": "FAIL"},
        "pipeline": {"gates": {"pass": 9}},
    }
    a = telemetry.attempt_data("case", "arm", entry, "demo")
    assert (
        a["worker_s"] == 4800
        and a["evaluator_s"] == 100
        and a["verdict"] == "FAIL"
        and "largest role retry" in a["over_budget_reason"]
    )
    telemetry.record("attempt", "demo", a, results_dir=results)
    base = telemetry.summarize(telemetry.rows_for("demo"))
    cur_rows = [
        {"kind": "turn", "part": "demo", "role": "model", "seconds": 500, "backend": "cursor", "ok": True},
        {
            "kind": "stage",
            "part": "demo",
            "stage": "verify",
            "seconds": 20,
            "ok": True,
            "engine_calls": 1,
            "engine_seconds": 3,
        },
        {"kind": "attempt", "part": "demo", "seconds": 700, "verdict": "PASS"},
    ]
    text = telemetry.compare(base, telemetry.summarize(cur_rows))
    assert "model" in text and "x0.25" in text and "attempts PASS: 0/1 -> 1/1" in text


def _at(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def _attempt_rows(t: float) -> list[dict]:
    """A model turn (latency 30 + 30), an evaluator stage, a correction turn interrupted once (100 s) and a second stage."""
    return [
        {
            "kind": "turn",
            "part": "demo",
            "role": "model",
            "key": "model",
            "order_id": "001-model",
            "ts": _at(t + 330),
            "seconds": 300,
            "issued_at": _at(t),
            "dispatched_at": _at(t + 30),
            "done_at": _at(t + 300),
            "consumed_at": _at(t + 330),
            "engine_seconds": 27,
            "engine_share": 0.1,
        },
        {
            "kind": "stage",
            "part": "demo",
            "stage": "verify",
            "ts": _at(t + 360),
            "seconds": 30,
            "engine_calls": 1,
            "engine_seconds": 9,
        },
        {
            "kind": "turn",
            "part": "demo",
            "role": "correction",
            "key": "correction-1",
            "order_id": "002-correction",
            "ts": _at(t + 760),
            "seconds": 340,
            "issued_at": _at(t + 360),
            "dispatched_at": _at(t + 400),
            "redispatched_at": _at(t + 500),
            "done_at": _at(t + 700),
            "consumed_at": _at(t + 760),
            "engine_seconds": 20,
            "engine_share": 0.1,
        },
        {"kind": "stage", "part": "demo", "stage": "gates", "ts": _at(t + 800), "seconds": 40},
    ]


def test_timeline_buckets_waterfall_and_attempt_critical_path(tmp_path: Path):
    t = 1_900_000_000.0
    rows = _attempt_rows(t)
    cp = telemetry.timeline(rows, t, t + 900)
    assert cp == {
        "worker_union_s": 470,
        "evaluator_s": 70,
        "interruption_s": 100,
        "latency_s": 160,
        "other_s": 100,
        "wall_s": 900,
    }
    part = tmp_path / "results" / "demo"
    part.mkdir(parents=True)
    (part / telemetry.PART_FILE).write_text("".join(json.dumps(r) + "\n" for r in rows))
    a = telemetry.attempt_data(
        "case",
        "arm",
        {
            "started": _at(t),
            "seconds": 900,
            "pipeline": {"gates": {"pass": 11, "fail": 0}},
            "scorecard": {"verdict": "PASS"},
        },
        "demo",
    )
    assert a["critical_path"] == cp and a["rounds"] == 1 and a["engine_share"] == round(47 / 640, 3)
    text = telemetry.waterfall(
        [*rows, {"kind": "attempt", "part": "demo", "started": _at(t), "ts": _at(t + 900)}], "demo"
    )
    assert (
        "wall 15:00" in text
        and "round 1" in text
        and "interruption" in text
        and "correction 002-correction" in text
        and "+  5:30" in text
    )


def test_bench_report_cells_and_completion(tmp_path: Path):
    t = 1_900_000_000.0
    stage = {"kind": "stage", "stage": "inspect", "seconds": 12, "tag": "b"}
    rows = [{**r, "tag": "b", "cad_backend": "cadquery"} for r in _attempt_rows(t)] + [
        {
            "kind": "attempt",
            "case": "bearing-housing",
            "cad_backend": "cadquery",
            "tag": "b",
            "seconds": 840,
            "verdict": "PASS",
            "rounds": 1,
            "turns": 3,
            "gates": {"pass": 11, "fail": 0},
            "critical_path": {
                "worker_union_s": 600,
                "evaluator_s": 120,
                "latency_s": 90,
                "interruption_s": 0,
                "other_s": 30,
            },
            "engine_share": 0.05,
        },
        {
            "kind": "attempt",
            "case": "bearing-housing",
            "cad_backend": "freecad",
            "tag": "b",
            "seconds": 1500,
            "verdict": "FAIL",
            "rounds": 3,
            "turns": 6,
            "critical_path": {
                "worker_union_s": 900,
                "evaluator_s": 400,
                "latency_s": 150,
                "interruption_s": 0,
                "other_s": 50,
            },
        },
        {**stage, "cad_backend": "cadquery"},
        {**stage, "cad_backend": "freecad", "seconds": 30},
    ]
    f = tmp_path / "c.jsonl"
    f.write_text("".join(json.dumps(r) + "\n" for r in rows + [{"kind": "attempt", "tag": "other", "seconds": 1}]))
    got = telemetry.bench_rows("b", [f])
    assert len(got) == len(rows)
    md = telemetry.bench("b", got)
    assert (
        "| bearing-housing | cadquery | 14:00 | PASS | 11/11 | 1 | 3 | 10:00 | 2:00 | 1:30 | 0:00 | 0:30 | 0.05 |" in md
    )
    assert "| bearing-housing / freecad | 1 | 0 | 0% | 25:00 |" in md and "All cells: 1/2 PASS (50%)" in md
    assert "| inspect | 12 (n=1) | 30 (n=1) |" in md and "| correction |" in md


def _event(role: str, content: list[dict]) -> str:
    return json.dumps({"role": role, "message": {"content": content}})


def test_transcript_usage_splits_a_resumed_turn(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENCAD_TRANSCRIPTS", str(tmp_path))
    agent = tmp_path / "proj" / "agent-transcripts" / "conv" / "subagents" / "agent-1.jsonl"
    agent.parent.mkdir(parents=True)
    tool = {"type": "tool_use", "input": {"x": 1}}
    lines = [
        _event("user", [{"type": "text", "text": "read /repo/results/cadquery/housing/worker/001-model/brief.md"}]),
        _event("assistant", [{"type": "text", "text": "abcd"}, tool]),
        _event(
            "user", [{"type": "text", "text": "continue /repo/results/cadquery/housing/worker/002-correction/brief.md"}]
        ),
        _event("assistant", [{"type": "text", "text": "zzzzzzzz"}]),
    ]
    agent.write_text("\n".join(lines) + "\n", encoding="utf-8")
    telemetry._SEGMENT_CACHE.clear()
    first = telemetry.transcript_usage("agent-1", "001-model")
    second = telemetry.transcript_usage("agent-1", "002-correction")
    assert first is not None and second is not None
    assert first["tool_calls"] == 1 and first["model_steps"] == 1
    assert first["chars"] == 4 + len(json.dumps({"x": 1})) and first["est_output_tokens"] == round(first["chars"] / 4)
    assert (
        second["tool_calls"] == 0
        and second["model_steps"] == 1
        and second["chars"] == 8
        and second["est_output_tokens"] == 2
    )
    whole = telemetry.transcript_usage("agent-1")
    assert whole is not None and whole["chars"] == first["chars"] + second["chars"] and whole["model_steps"] == 2
    turns = [{"thread_id": "agent-1", "order_id": "001-model"}, {"thread_id": "agent-1", "order_id": "002-correction"}]
    summed = telemetry._usage_for_turns(turns)
    assert (
        summed is not None
        and summed["est_output_tokens"] == first["est_output_tokens"] + second["est_output_tokens"]
        and summed["tool_calls"] == 1
        and summed["off_brief_reads"] == 0
    )


def test_off_brief_reads_count_library_and_other_parts(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENCAD_TRANSCRIPTS", str(tmp_path))
    agent = tmp_path / "proj" / "agent-transcripts" / "conv" / "subagents" / "agent-off.jsonl"
    agent.parent.mkdir(parents=True)

    def read(path: str) -> dict:
        return {"type": "tool_use", "name": "Read", "input": {"path": path}}

    lines = [
        _event("user", [{"type": "text", "text": "order /repo/results/build123d/housing/worker/001-model/brief.md"}]),
        _event(
            "assistant",
            [
                {"type": "text", "text": "looking"},
                read("/repo/src/opencad/schemas.py"),
                read("/repo/designs/.staging-housing/contract.yaml"),
                read("/repo/parts/build123d/housing/main.py"),
                read("/repo/parts/cadquery/housing/main.py"),
                read("/repo/designs/enclosure-base/contract.yaml"),
                read("/repo/tests/test_worker.py"),
                read("/repo/results/build123d/housing/worker/002-correction/brief.md"),
                {"type": "tool_use", "name": "Grep", "input": {"pattern": "Literal", "path": "/repo/truth/cases"}},
            ],
        ),
    ]
    agent.write_text("\n".join(lines) + "\n", encoding="utf-8")
    telemetry._SEGMENT_CACHE.clear()
    usage = telemetry.transcript_usage("agent-off", "001-model")
    assert usage is not None and usage["off_brief_reads"] == 6 and usage["tool_calls"] == 8
    rows = [
        {
            "kind": "turn",
            "part": "housing",
            "cad_backend": "build123d",
            "ts": "2026-09-24T00:00:10Z",
            "thread_id": "agent-off",
            "order_id": "001-model",
            "role": "model",
        },
        {
            "kind": "attempt",
            "tag": "off",
            "case": "housing",
            "design": "housing",
            "cad_backend": "build123d",
            "seconds": 60,
            "verdict": "PASS",
            "gates": {"pass": 11, "fail": 0},
            "started": "2026-09-24T00:00:00Z",
            "rounds": 1,
            "turns": 1,
            "engine_share": 0,
            "critical_path": {
                "worker_union_s": 50,
                "evaluator_s": 5,
                "latency_s": 5,
                "interruption_s": 0,
                "other_s": 0,
            },
        },
    ]
    md = telemetry.bench("off", rows)
    assert "| off-brief reads |" in md
    row = next(line for line in md.splitlines() if line.startswith("| housing |"))
    assert row.endswith("| 6 |")


def test_bench_baseline_section_and_compare_baseline(tmp_path: Path, monkeypatch):
    root = tmp_path / "results"
    specs = (
        ("cadquery", "base", 120, 100),
        ("freecad", "base", 80, 70),
        ("cadquery", "new", 60, 40),
        ("freecad", "new", 90, 50),
    )
    by_backend: dict[str, list[str]] = {}
    for be, tag, seconds, role_s in specs:
        attempt = {
            "kind": "attempt",
            "tag": tag,
            "case": "bearing-housing",
            "cad_backend": be,
            "seconds": seconds,
            "verdict": "PASS",
            "gates": {"pass": 11, "fail": 0},
            "accuracy_score": 99.0,
            "est_output_tokens": 1000,
            "model": "cheap",
            "started": "2026-09-23T00:00:00Z",
            "critical_path": {
                "worker_union_s": seconds - 10,
                "evaluator_s": 5,
                "latency_s": 5,
                "interruption_s": 0,
                "other_s": 0,
            },
        }
        turn = {
            "kind": "turn",
            "tag": tag,
            "part": "bearing-housing",
            "cad_backend": be,
            "role": "model",
            "seconds": role_s,
            "backend": "cursor",
            "ok": True,
        }
        by_backend.setdefault(be, []).extend((json.dumps(attempt), json.dumps(turn)))
    for be, lines in by_backend.items():
        campaign = root / be / "_campaign"
        campaign.mkdir(parents=True)
        (campaign / "telemetry.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    pointer = tmp_path / "baseline.json"
    pointer.write_text(json.dumps({"tag": "base", "model": "opus"}), encoding="utf-8")
    monkeypatch.setattr(telemetry, "BASELINE_POINTER", pointer)
    monkeypatch.setattr(telemetry, "RESULTS_BASE", root)
    md = telemetry.bench("new", telemetry.bench_rows("new"))
    assert "## Against the baseline `base`" in md
    assert "| bearing-housing / cadquery | 1:00 | -1:00 | 1/1 | 11/11 | 99.0 | 1000 | 2:00 | 99.0 | 1000 |" in md
    assert "Median wall 1:15 (baseline 1:40, delta -0:25)." in md
    assert {r["cad_backend"] for r in telemetry.rows_for_spec("baseline")} == {"cadquery", "freecad"}
    base = telemetry.summarize(telemetry.rows_for_spec("baseline"))
    cur = telemetry.summarize(telemetry.rows_for_spec("tag:new"))
    assert base["worker_s"] == 170 and cur["worker_s"] == 90
    text = telemetry.compare(base, cur)
    assert "model" in text and "x0.53" in text
    pointer.write_text(json.dumps({"tag": "promoted", "model": "other"}), encoding="utf-8")
    chosen = telemetry.bench("new", telemetry.bench_rows("new"), against="base")
    assert (
        "## Against the baseline `base`" in chosen
        and "promoted" not in chosen.split("Against the baseline", 1)[1][:400]
    )


def test_bench_regression_session_drafts_and_baseline(tmp_path: Path, monkeypatch):
    root = tmp_path / "results"
    rows: dict[str, list[dict]] = {}

    def add(be: str, **row) -> None:
        rows.setdefault(be, []).append(row)

    def attempt(tag: str, case: str, be: str, started: str, seconds: int, **kw) -> None:
        add(be, kind="attempt", tag=tag, case=case, design=case, cad_backend=be, started=started, seconds=seconds, **kw)

    for case in ("bearing-housing", "enclosure-base"):
        for be in ("cadquery", "freecad"):
            attempt("base", case, be, "2026-09-22T00:00:00Z", 1800, verdict="PASS", gates={"pass": 11, "fail": 0})
    attempt("reg", "bearing-housing", "cadquery", "2026-09-24T00:00:00Z", 600, stage_reached="published")
    attempt("reg", "enclosure-base", "cadquery", "2026-09-24T00:00:00Z", 540, stage_reached="published")
    for role, model, ts in (("draft", "opus", "2026-09-24T00:09:00Z"), ("model", "grok", "2026-09-24T00:12:00Z")):
        add("cadquery", kind="turn", tag="reg", part="bearing-housing", cad_backend="cadquery", role=role, model=model, seconds=60, ts=ts)
    for case, be, secs, passed in (
        ("bearing-housing", "cadquery", 1200, 11),
        ("bearing-housing", "freecad", 1500, 11),
        ("enclosure-base", "cadquery", 900, 11),
        ("enclosure-base", "freecad", 1320, 10),
    ):
        gates = {"pass": passed, "fail": 11 - passed}
        attempt("reg", case, be, "2026-09-24T00:10:00Z", secs, resume_from="blockout", stage_reached="scored", verdict="PASS", gates=gates)
    for be, rs in rows.items():
        (root / be / "_campaign").mkdir(parents=True)
        (root / be / "_campaign" / "telemetry.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rs), encoding="utf-8")
    monkeypatch.setattr(telemetry, "RESULTS_BASE", root)
    monkeypatch.setattr(telemetry, "BASELINE_POINTER", tmp_path / "none.json")
    md = telemetry.bench("reg", telemetry.bench_rows("reg"), against="base")
    assert "Regression (scorecard PASS and no failed gate): cadquery PASS (2/2); freecad FAIL (1/2: enclosure-base PASS gates 10/11)." in md
    assert "Session wall 35:00, first start to last finish across 6 attempts." in md
    assert "| bearing-housing | cadquery | 10:00 | published | - | opus |" in md, "a draft owns only its draft turns"
    assert "| bearing-housing / cadquery | 1 | 1 | 100% | 20:00 |" in md, "drafts stay out of the cells"
    assert "| bearing-housing / cadquery | 30:00 | +0:00 | 1/1 |" in md and "| enclosure-base / freecad | 31:00 | +1:00 | 1/1 | 10/11 |" in md
    assert "Session wall 35:00 against 120:00 for one sequential pass at the baseline medians (sum of its 4 cell medians): 29% of that time, delta -85:00." in md


def _regression(add, tag: str, day: str, draft: int, lane: int) -> None:
    for case in ("bearing-housing", "enclosure-base"):
        add("cadquery", kind="attempt", tag=tag, case=case, design=case, cad_backend="cadquery", started=f"{day}T00:00:00Z", seconds=draft, stage_reached="published")
        for be in ("cadquery", "freecad"):
            add(be, kind="attempt", tag=tag, case=case, design=case, cad_backend=be, started=f"{day}T00:10:00Z", seconds=lane,
                resume_from="blockout", stage_reached="scored", verdict="PASS", gates={"pass": 11, "fail": 0})
    add("cadquery", kind="turn", tag=tag, part="bearing-housing", cad_backend="cadquery", role="draft", model="opus", seconds=60, ts=f"{day}T00:05:00Z")
    add("freecad", kind="turn", tag=tag, part="bearing-housing", cad_backend="freecad", role="model", model="grok", seconds=60, ts=f"{day}T00:20:00Z")


def test_promote_snapshots_a_baseline_that_bench_compares_symmetrically(tmp_path: Path, monkeypatch):
    root = tmp_path / "results"
    rows: dict[str, list[dict]] = {}

    def add(be: str, **row) -> None:
        rows.setdefault(be, []).append(row)

    _regression(add, "reg", "2026-09-24", 600, 1200)
    _regression(add, "new", "2026-09-25", 500, 1000)
    add("cadquery", kind="attempt", tag="base", case="bearing-housing", cad_backend="cadquery", started="2026-09-22T00:00:00Z", seconds=1800, verdict="PASS")

    def write(keep) -> None:
        for be, rs in rows.items():
            (root / be / "_campaign").mkdir(parents=True, exist_ok=True)
            (root / be / "_campaign" / "telemetry.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rs if keep(r)), encoding="utf-8")

    write(lambda r: True)
    monkeypatch.setattr(telemetry, "RESULTS_BASE", root)
    pointer = tmp_path / "bakeoff" / "baseline.json"
    pointer.parent.mkdir()
    pointer.write_text(json.dumps({"tag": "base", "model": "opus"}))
    monkeypatch.setattr(telemetry, "BASELINE_POINTER", pointer)
    report = tmp_path / "reg.md"
    report.write_text("# reg\n")
    info = telemetry.promote("reg", report=report)
    assert info["tag"] == "reg" and info["previous"] == "base" and info["models"] == {"draft": "opus", "model": "grok"}
    assert info["session_wall_s"] == 1800 and json.loads(pointer.read_text())["tag"] == "reg"
    snaps = pointer.parent / "baselines"
    assert (snaps / "reg.md").read_text() == "# reg\n" and (snaps / "base.jsonl").exists()
    write(lambda r: r["tag"] == "new")
    assert len(telemetry.bench_rows("reg")) == sum(r["tag"] == "reg" for rs in rows.values() for r in rs), "the snapshot serves a lost tag"
    md = telemetry.bench("new", telemetry.bench_rows("new"))
    assert "## Against the baseline `reg`" in md
    assert "| bearing-housing / cadquery | 25:00 | -5:00 | 1/1 |" in md, "both sides add their own draft wall"
    assert "Drafts: bearing-housing 8:20 (baseline 10:00, -1:40); enclosure-base 8:20 (baseline 10:00, -1:40)." in md
    assert "Session wall 26:40 against the baseline session 30:00: delta -3:20." in md


def test_timed_stage_row_survives_a_pending_turn_and_ledger_startup(tmp_path: Path):
    import sys

    from opencad.backends.local import reset_ledger, run_script

    results = tmp_path / "results" / "demo"
    with pytest.raises(RuntimeError), telemetry.timed("briefs", "demo", results, key="correction-1") as t:
        t["ok"] = True
        raise RuntimeError("stands in for WorkerPending")
    row = telemetry.rows_for("demo")[-1]
    assert row["stage"] == "briefs" and row["key"] == "correction-1" and row["ok"] is True and row["engine_calls"] == 0
    payload = tmp_path / "out.json"
    script = tmp_path / "runner.py"
    script.write_text(
        f"import json; json.dump({{'ok': True, 'timings': {{'build_s': 0.001, 'main_s': 0.002}}}}, open({str(payload)!r}, 'w'))\n"
    )
    r = run_script([sys.executable, str(script)], backend_id="cadquery", cwd=tmp_path, lock=False, payload=payload)
    assert r["ok"] and r["timings"]["build_s"] == 0.001 and r["startup_s"] >= 0 and r["started"] <= time.time()
    assert reset_ledger("cadquery")[-1]["startup_s"] == r["startup_s"]
    s = telemetry.stage_data("export", 3.0, True, [{"seconds": 2.0, "startup_s": 1.5}, {"seconds": 1.0}])
    assert s["engine_startup_s"] == 1.5 and s["engine_seconds"] == 3.0


def test_concurrent_appends_keep_long_rows_whole(tmp_path: Path):
    import threading

    path = tmp_path / "telemetry.jsonl"

    def write(n: int) -> None:
        for i in range(20):
            telemetry._append(path, {"writer": n, "i": i, "pad": "x" * 100_000})

    threads = [threading.Thread(target=write, args=(n,)) for n in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(rows) == 120 and all(len(r["pad"]) == 100_000 for r in rows)

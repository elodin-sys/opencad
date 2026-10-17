"""Work orders, re-entrant dispatch, Codex opt-in with budget fallback, role profiles, resumable pipeline state, vault attach/keep."""

from __future__ import annotations

import json
import os
import time
import shutil
from pathlib import Path

import pytest

from opencad import worker
from opencad.worker import backends, codex_backend, orders, profiles, state
from opencad.worker.result import WorkerResult


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("OPENCAD_WORKER", raising=False)
    monkeypatch.setattr(state, "CAMPAIGN_STATE", tmp_path / "_campaign" / "worker-state.json")
    from opencad import telemetry

    monkeypatch.setattr(telemetry, "CAMPAIGN_FILE", tmp_path / "_campaign" / "telemetry.jsonl")
    backends.set_continue_cmd("")
    yield


def _finish_order(
    order: orders.WorkOrder,
    result: str = "## Result\nbuilt\n## Files changed\n- main.kcl\n## Verification\nok\n## Open questions\nnone\n",
    metrics: dict | None = None,
    agent_id: str = "agent-1",
) -> None:
    order.result_path.write_text(result)
    order.metrics_path.write_text(
        json.dumps(
            metrics
            or {
                "commands": 7,
                "self_corrections": 1,
                "engine_calls": 3,
                "files_changed": ["main.kcl"],
                "incomplete": False,
            }
        )
    )
    order.dispatch_path.write_text(json.dumps({"agent_id": agent_id, "model": order.model}))
    order.ledger_path.write_text(
        "\n".join(json.dumps({"cmd": "zoo kcl analyze x.kcl", "seconds": 2.5, "ok": True}) for _ in range(3)) + "\n"
    )
    order.done_path.touch()


def test_issue_pending_next_line_and_complete(tmp_path: Path):
    results = tmp_path / "results" / "demo"
    deliverable = tmp_path / "parts" / "demo" / "main.kcl"
    o = orders.issue(
        results,
        key="model",
        role="model",
        part="demo",
        brief="Build the thing.",
        cwd=tmp_path / "work",
        images=[tmp_path / "a.png"],
        deliverables=[deliverable],
        model="m",
        budget_s=100,
        continue_cmd="python -m opencad drive demo",
    )
    assert o.id == "001-model" and o.status == "pending" and orders.pending(results) == [o]
    prompt = o.brief_path.read_text()
    assert (
        "Build the thing." in prompt
        and str(o.done_path) in prompt
        and "opencad engine" in prompt
        and "--ledger" in prompt
        and "a.png" in prompt
    )
    line = orders.next_line(o)
    assert line.startswith("NEXT ")
    d = json.loads(line[5:])
    assert (
        d["action"] == "worker"
        and d["model"] == "m"
        and d["continue"] == "python -m opencad drive demo"
        and d["prompt"] == str(o.brief_path)
    )
    # deliverable missing -> failed result
    _finish_order(o)
    r = orders.complete(orders.load(o.dir))
    assert not r.ok and "deliverables missing" in r.failure and r.backend == "cursor" and r.thread_id == "agent-1"
    deliverable.parent.mkdir(parents=True)
    deliverable.write_text("x = 1\n")
    r = orders.complete(orders.load(o.dir))
    assert (
        r.ok
        and r.commands == 7
        and r.sections["Result"] == "built"
        and r.metrics["engine_ledger_calls"] == 3
        and r.metrics["engine_ledger_seconds"] == 7.5
    )
    assert orders.load(o.dir).status == "done" and orders.pending(results) == []
    s = r.summary()
    assert s["backend"] == "cursor" and s["order_id"] == "001-model" and s["timeline"] == {}
    assert r.metrics.get("visual_check") is None


def test_turn_row_carries_lifecycle_and_ledger_fields(tmp_path: Path, capsys):
    """issued -> dispatched -> re-dispatched (interrupted worker) -> done -> consumed, and the per-call engine numbers, on the one turn row."""
    from opencad import telemetry

    results = tmp_path / "results" / "demo"
    o = orders.issue(
        results,
        key="correction-2",
        role="correction",
        part="demo",
        brief="Fix.",
        cwd=tmp_path / "work",
        model="m",
        budget_s=900,
    )
    t0 = time.time() - 600
    o.created_ts = t0
    orders.save(o)
    orders.record_dispatch(o, "agent-1")
    orders.record_dispatch(o, "agent-2")  # the first Task died with the session; the order was handed to a new one
    rec = json.loads(o.dispatch_path.read_text())
    rec["dispatches"][0]["ts"], rec["dispatches"][1]["ts"] = t0 + 30, t0 + 300
    o.dispatch_path.write_text(json.dumps(rec))
    o.result_path.write_text(
        "## Result\nok\n## Files changed\n-\n## Verification\nVisual: fine\n## Open questions\nnone\n"
    )
    o.metrics_path.write_text(json.dumps({"commands": 3}))
    o.ledger_path.write_text(
        "".join(
            json.dumps({"seconds": s, "started": t0 + st, "startup_s": 0.5}) + "\n"
            for s, st in ((2, 320), (4, 400), (10, 450))
        )
    )
    o.done_path.touch()
    os.utime(o.done_path, (t0 + 500, t0 + 500))
    orders.complete(orders.load(o.dir))
    row = telemetry.read(results / telemetry.PART_FILE)[-1]
    assert (
        row["key"] == "correction-2"
        and row["dispatches"] == 2
        and row["dispatch_latency_s"] == 30
        and row["interruption_s"] == 270
    )
    assert (
        row["worker_s"] == 200
        and 95 <= row["pickup_latency_s"] <= 130
        and row["issued_at"]
        and row["redispatched_at"]
        and row["consumed_at"]
    )
    assert (
        row["engine_call_p50_s"] == 4
        and row["engine_call_max_s"] == 10
        and row["first_engine_call_s"] == 290
        and row["engine_share"] == 0.08
    )
    assert row["engine_startup_s"] == 1.5 and "re-dispatched: 270.0 s lost" in capsys.readouterr().out


def test_wait_returns_when_every_order_is_done_and_flags_a_stale_worker_once(tmp_path: Path, capsys):
    """`--wait`: the command polls the pending orders' done files and continues itself; a dispatched worker idle past 1.25x its
    budget gets one STALE line naming the agent to resume."""
    import threading

    results = tmp_path / "results" / "demo"
    quiet = orders.issue(
        results, key="module-a", role="module", part="demo", brief="A.", cwd=tmp_path / "a", model="m", budget_s=1
    )
    busy = orders.issue(
        results, key="module-b", role="module", part="demo", brief="B.", cwd=tmp_path / "b", model="m", budget_s=900
    )
    orders.record_dispatch(quiet, "agent-quiet")
    orders.record_dispatch(busy, "agent-busy")
    old = time.time() - 60
    quiet.created_ts = old
    orders.save(quiet)
    for f in quiet.dir.rglob("*"):
        os.utime(f, (old, old))

    def finish() -> None:
        time.sleep(0.4)
        busy.done_path.touch()
        quiet.done_path.touch()

    threading.Thread(target=finish).start()
    t0 = time.time()
    orders.wait(results, poll_s=0.05)
    out = capsys.readouterr().out
    stale = [json.loads(line[6:]) for line in out.splitlines() if line.startswith("STALE ")]
    assert (
        0.3 < time.time() - t0 < 5
        and len(stale) == 1
        and stale[0]["id"] == quiet.id
        and stale[0]["resume"] == "agent-quiet"
    )
    assert stale[0]["idle_s"] >= 50 and not orders.pending(results)


def test_watch_prints_undispatched_and_stale_orders_or_the_pipeline_exit(tmp_path: Path, capsys):
    """`next --watch`: the orchestrator waits on the order files instead of a pipeline's output, which dies with its terminal."""
    import subprocess

    results = tmp_path / "results" / "demo"
    fresh = orders.issue(results, key="model", role="model", part="demo", brief="A.", cwd=tmp_path / "a", model="m", budget_s=900)
    assert orders.watch(lambda: orders.pending(results), poll_s=0.01, timeout=1) == 0
    assert json.loads(capsys.readouterr().out.split(" ", 1)[1])["id"] == fresh.id
    orders.record_dispatch(fresh, "agent-a")
    assert orders.watch(lambda: orders.pending(results), poll_s=0.01, timeout=0.05) == 4 and "TIMEOUT" in capsys.readouterr().out
    old = time.time() - 60
    fresh.created_ts = old
    orders.save(fresh)
    for f in fresh.dir.rglob("*"):
        os.utime(f, (old, old))
    assert orders.watch(lambda: orders.pending(results), stale_s=30, poll_s=0.01, timeout=1) == 0
    assert capsys.readouterr().out.startswith("STALE ")
    fresh.done_path.touch()
    gone = subprocess.Popen(["true"])
    gone.wait()
    assert orders.watch(lambda: orders.pending(results), pid=gone.pid, poll_s=0.01, timeout=1) == 3 and "EXITED" in capsys.readouterr().out


def test_enforced_budget_takes_the_executing_checkpoint(tmp_path: Path, capsys):
    """--enforce-budgets: a turn past 1.5x its budget is taken at the worker's executing checkpoint when the deliverable itself does
    not execute; the turn row records `expired`."""
    from opencad import telemetry

    results = tmp_path / "results" / "demo"
    work = tmp_path / "model-work"
    work.mkdir()
    deliverable = tmp_path / "parts" / "demo" / "main.py"
    deliverable.parent.mkdir(parents=True)
    deliverable.write_text("broken(\n")
    (work / "checkpoint.py").write_text("good = 1\n")
    o = orders.issue(
        results,
        key="correction-1",
        role="correction",
        part="demo",
        brief="Fix.",
        cwd=work,
        deliverables=[deliverable],
        model="m",
        budget_s=10,
    )
    orders.record_dispatch(o, "agent-late")
    rec = json.loads(o.dispatch_path.read_text())
    rec["dispatches"][0]["ts"] = time.time() - 100
    o.dispatch_path.write_text(json.dumps(rec))
    orders.wait(results, poll_s=0.01, enforce=lambda p: "good" in p.read_text())
    out = capsys.readouterr().out
    expired = [json.loads(line[8:]) for line in out.splitlines() if line.startswith("EXPIRED ")]
    assert (
        deliverable.read_text() == "good = 1\n"
        and len(expired) == 1
        and expired[0]["resume"] == "agent-late"
        and "checkpoint" in expired[0]["took"]
    )
    assert json.loads(o.metrics_path.read_text())["expired"] is True and o.done_path.exists()
    orders.complete(orders.load(o.dir))
    row = telemetry.read(results / telemetry.PART_FILE)[-1]
    assert "checkpoint" in row["expired"] and row["incomplete"] is True


def test_small_contracts_scale_early_budgets_skip_the_blockout_and_brief_the_envelope(monkeypatch, tmp_path: Path):
    """B5: draft/blockout/model budgets scale with the work; a contract of <= 30 acceptance items needs no blockout checkpoint and its
    model brief makes the envelope the first checkpoint."""
    from types import SimpleNamespace

    from opencad.stages import decompose, model

    assert (
        profiles.scaled_budget("model", 22) == 1040
        and profiles.scaled_budget("draft", 4) == 660
        and profiles.scaled_budget("model", 500) == 2700
    )
    assert (
        profiles.scaled_budget("model", 22, SimpleNamespace(turn_factor=1.5)) == 1560
        and profiles.scaled_budget("blockout", 50) == 600
    )
    ctx, pipeline, _ = _loop_ctx(monkeypatch, tmp_path, [])
    n = decompose.acceptance_count(ctx.contract)
    assert n <= profiles.SMALL_CONTRACT_ITEMS and not (ctx.results_dir / "blockout.json").exists()
    assert pipeline.run(ctx, from_stage="plan") in (0, 1), "below the size threshold no blockout checkpoint is required"
    seen: dict = {}
    monkeypatch.setattr(
        worker,
        "dispatch",
        lambda brief, **kw: (
            seen.update(kw, brief=brief)
            or WorkerResult("a", 0, 1.0, 1, {}, tmp_path, "## Result\nok", backend="cursor", role="model")
        ),
    )
    monkeypatch.setattr(ctx.backend.language, "format_write", lambda p: None)
    ctx.write_stage("plan", {"ok": True, "folded": True})
    model.run(ctx)
    assert (
        seen["budget"] == profiles.scaled_budget("model", n, ctx.backend.engine)
        and "No blockout checkpoint ran for this part" in seen["brief"]
    )
    assert str(list(ctx.contract.envelope.min)) in seen["brief"]


def test_complete_records_visual_check(tmp_path: Path):
    results = tmp_path / "results" / "demo"
    deliverable = tmp_path / "parts" / "demo" / "main.kcl"
    deliverable.parent.mkdir(parents=True)
    deliverable.write_text("x = 1\n")
    o = orders.issue(
        results,
        key="model",
        role="model",
        part="demo",
        brief="Build.",
        cwd=tmp_path / "work",
        deliverables=[deliverable],
        model="m",
        budget_s=100,
    )
    assert "Visual:" in o.brief_path.read_text()
    _finish_order(
        o,
        result="## Result\nbuilt\n## Files changed\n- main.kcl\n## Verification\nVisual: port stern fold, underside clean\n## Open questions\nnone\n",
    )
    r = orders.complete(orders.load(o.dir))
    assert r.ok and r.metrics["visual_check"] == "Visual: port stern fold, underside clean"


def test_dispatch_record_and_idle_seconds(tmp_path: Path):
    """`opencad dispatch` writes the record the orchestrator used to hand-edit; idle_s follows the newest file a worker touched."""
    import time

    results = tmp_path / "results" / "demo"
    deliverable = tmp_path / "parts" / "demo" / "main.kcl"
    deliverable.parent.mkdir(parents=True)
    o = orders.issue(
        results,
        key="model",
        role="model",
        part="demo",
        brief="Build.",
        cwd=tmp_path / "work",
        writable_dirs=[deliverable.parent],
        deliverables=[deliverable],
        model="inherit",
        budget_s=100,
    )
    p = orders.record_dispatch(o, "agent-42")
    rec = json.loads(p.read_text())
    assert (
        rec["agent_id"] == "agent-42" and rec["model"] == "inherit" and rec["finished"] is None and rec["dispatched_at"]
    )
    assert [d["agent_id"] for d in rec["dispatches"]] == ["agent-42"]
    orders.record_dispatch(o, "agent-42", finished=True)
    assert json.loads(p.read_text())["finished"] is not None and orders.known_agent(results, "agent-42")
    line = json.loads(orders.next_line(o, idle=True).removeprefix("NEXT "))
    assert line["dispatched"] is True and line["idle_s"] >= 0 and "opencad dispatch" in line["dispatch"]
    old = time.time() - 3600
    o.created_ts = old  # issued an hour ago
    for f in o.dir.rglob("*"):
        if f.is_file():
            os.utime(f, (old, old))
    assert orders.idle_seconds(o) > 3000
    deliverable.write_text("a = 1\n")  # the worker wrote the deliverable just now
    assert orders.idle_seconds(o) < 60
    from opencad.cli import main as cli_main

    assert cli_main(["dispatch", str(o.dir), "--agent-id", "agent-43", "--finished"]) == 0
    assert json.loads(p.read_text())["agent_id"] == "agent-43"


def test_complete_records_visual_check_as_bullet(tmp_path: Path):
    results = tmp_path / "results" / "demo"
    deliverable = tmp_path / "parts" / "demo" / "main.kcl"
    deliverable.parent.mkdir(parents=True)
    deliverable.write_text("x = 1\n")
    o = orders.issue(
        results,
        key="model",
        role="model",
        part="demo",
        brief="Build.",
        cwd=tmp_path / "work",
        deliverables=[deliverable],
        model="m",
        budget_s=100,
    )
    _finish_order(
        o,
        result="## Result\nbuilt\n## Files changed\n- main.kcl\n## Verification\n- Visual: pin through hole, no gap\n## Open questions\nnone\n",
    )
    r = orders.complete(orders.load(o.dir))
    assert r.ok and r.metrics["visual_check"] == "Visual: pin through hole, no gap"


def test_dispatch_is_reentrant_and_supersede_starts_fresh(tmp_path: Path):
    results = tmp_path / "results" / "demo"
    kw = dict(
        role="plan",
        key="plan",
        results_dir=results,
        part="demo",
        cd=tmp_path / "work",
        run_dir=tmp_path / "work" / "codex",
        read_only=True,
    )
    with pytest.raises(worker.WorkerPending) as ei:
        worker.dispatch("plan it", **kw)
    o = ei.value.order
    assert (
        o.role == "plan"
        and o.model == profiles.profile("plan").model
        and o.budget_s == profiles.profile("plan").budget_s
    )
    with pytest.raises(worker.WorkerPending) as ei2:  # still open: the same order, no duplicate
        worker.dispatch("plan it", **kw)
    assert ei2.value.order.id == o.id and len(orders.list_orders(results)) == 1
    _finish_order(o, result="## Result\nstep 1\n## Files changed\nnone\n## Verification\n-\n## Open questions\n-\n")
    r = worker.dispatch("plan it", **kw)
    assert r.ok and r.sections["Result"] == "step 1" and r.role == "plan"
    assert worker.dispatch("plan it", **kw).ok  # idempotent on a continued run
    assert not worker.fresh(results, "plan")
    assert orders.supersede(results, "plan") == 1 and worker.fresh(results, "plan")
    with pytest.raises(worker.WorkerPending) as ei3:
        worker.dispatch("plan it again", **kw)
    assert ei3.value.order.id == "002-plan" and "plan it again" in ei3.value.order.brief_path.read_text()
    assert orders.previous_results(results, before=ei3.value.order) == [o.result_path]


def test_timeout_caps_the_role_budget_and_env_overrides(monkeypatch):
    for key in list(os.environ):
        if key == "OPENCAD_MODEL" or key.startswith("OPENCAD_MODEL_"):
            monkeypatch.delenv(key, raising=False)
    assert profiles.profile("draft").model == profiles.profile("asm-draft").model == "claude-opus-5-5-max"
    assert all(profiles.profile(role).model == profiles.WORK_MODEL == "grok-4.7-xhigh-fast" for role in profiles.ROLES if role not in ("draft", "asm-draft"))
    monkeypatch.setenv("OPENCAD_MODEL", profiles.INHERIT)
    assert profiles.profile("draft").model == profiles.INHERIT
    monkeypatch.delenv("OPENCAD_MODEL")
    assert profiles.budget_for("model", None) == profiles.profile("model").budget_s
    assert profiles.budget_for("model", 600) == 600
    assert profiles.budget_for("model", 99999) == profiles.profile("model").budget_s
    monkeypatch.setenv("OPENCAD_MODEL_BLOCKOUT", "some-model")
    monkeypatch.setenv("OPENCAD_BUDGET_BLOCKOUT", "42")
    monkeypatch.setenv("OPENCAD_CODEX_EFFORT_BLOCKOUT", "xhigh")
    p = profiles.profile("blockout")
    assert p.model == "some-model" and p.budget_s == 42 and p.codex_effort == "xhigh" and p.codex_idle_s == 300.0
    monkeypatch.setenv("OPENCAD_CODEX_EFFORT", "max")
    assert profiles.profile("model").codex_effort == "max" and profiles.profile("model").codex_idle_s == 900.0
    assert profiles.profile("blockout").codex_effort == "xhigh", "a per-role effort wins over OPENCAD_CODEX_EFFORT"
    assert profiles.profile("unknown-role").role == "unknown-role"


def test_scaled_budget_applies_the_engine_turn_factor(monkeypatch):
    """FreeCAD turns (every critic run is a freecadcmd export) get 1.5x the budget, cap included; other engines are unchanged."""
    monkeypatch.delenv("OPENCAD_BUDGET_CORRECTION", raising=False)
    monkeypatch.delenv("OPENCAD_BUDGET_MODULE", raising=False)

    class Slow:
        turn_factor = 1.5

    class Plain:
        pass

    assert profiles.scaled_budget("module", 10) == 1500 == profiles.scaled_budget("module", 10, Plain())
    assert profiles.scaled_budget("module", 10, Slow()) == 2250
    assert profiles.scaled_budget("correction", 40) == 1800 and profiles.scaled_budget("correction", 40, Slow()) == 2700
    monkeypatch.setenv("OPENCAD_BUDGET_MODULE", "99")
    assert profiles.scaled_budget("module", 10, Slow()) == 99, "an explicit env budget is not scaled"


def test_backend_selection(monkeypatch):
    assert worker.selected_backend() == "cursor"
    monkeypatch.setenv("OPENCAD_WORKER", "codex")
    assert worker.selected_backend() == "codex"
    monkeypatch.setenv("OPENCAD_WORKER", "nope")
    with pytest.raises(ValueError):
        worker.selected_backend()
    worker.set_backend("cursor")
    assert worker.selected_backend() == "cursor"


def _sessions(tmp_path: Path, rate_limits: dict) -> Path:
    root = tmp_path / "sessions" / "2026" / "09" / "18"
    root.mkdir(parents=True)
    f = root / "rollout-2026-09-18T10-00-00-abc.jsonl"
    rows = [
        {"type": "session_meta", "payload": {"id": "abc"}},
        {
            "type": "event_msg",
            "payload": {"type": "token_count", "info": {"total_token_usage": {}}, "rate_limits": rate_limits},
            "timestamp": "2026-09-18T10:00:00Z",
        },
    ]
    f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return tmp_path / "sessions"


def test_codex_budget_from_sessions(tmp_path: Path):
    rl_ok = {
        "primary": {"used_percent": 10},
        "secondary": {"used_percent": 100, "resets_at": 1789930971},
        "credits": {"has_credits": True},
        "plan_type": "team",
    }
    b = codex_backend.budget(_sessions(tmp_path / "a", rl_ok))
    assert b["known"] and not b["exhausted"] and b["secondary_used"] == 100 and b["plan_type"] == "team"
    rl_gone = {**rl_ok, "credits": {"has_credits": False}}
    b = codex_backend.budget(_sessions(tmp_path / "b", rl_gone))
    assert b["exhausted"] and "no credits" in b["reason"] and b["resets_at"] == 1789930971
    rl_hard = {**rl_ok, "rate_limit_reached_type": "weekly"}
    assert codex_backend.budget(_sessions(tmp_path / "c", rl_hard))["exhausted"]
    assert not codex_backend.budget(tmp_path / "missing")["known"]


def test_result_exhausted_classification(tmp_path: Path):
    r = WorkerResult("t", 1, 3.0, 0, {}, tmp_path, "", failure="You've hit your usage limit. Try again later")
    assert codex_backend.result_exhausted(r)
    r_ok = WorkerResult("t", 0, 3.0, 0, {}, tmp_path, "## Result\nfine")
    assert not codex_backend.result_exhausted(r_ok)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "events.jsonl").write_text(
        json.dumps({"type": "error", "message": "insufficient_quota: billing hard limit reached"}) + "\n"
    )
    assert codex_backend.result_exhausted(WorkerResult("t", 1, 3.0, 0, {}, run_dir, "", failure="exit 1"))
    assert not codex_backend.result_exhausted(
        WorkerResult("t", 1, 3.0, 0, {}, tmp_path, "", failure="kernel failed the boolean")
    )


def test_codex_opt_in_falls_back_to_cursor_when_exhausted(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENCAD_WORKER", "codex")
    results = tmp_path / "results" / "demo"
    calls: list[dict] = []

    def fake_codex(brief, *, cd, run_dir, timeout, effort, idle_timeout, **kw):
        calls.append({"effort": effort, "timeout": timeout, "idle": idle_timeout})
        Path(run_dir).mkdir(parents=True, exist_ok=True)
        return WorkerResult(
            "thr",
            1,
            12.0,
            2,
            {},
            Path(run_dir),
            "",
            failure="stream error: usage limit reached for this week",
            backend="codex",
        )

    monkeypatch.setattr(codex_backend, "dispatch", fake_codex)
    resets_at = (
        int(time.time()) + 3600
    )  # a mark whose reset is still ahead; a fixed epoch expires and turns the test into a time bomb
    monkeypatch.setattr(
        codex_backend, "budget", lambda *a, **k: {"known": True, "exhausted": False, "resets_at": resets_at}
    )
    kw = dict(
        role="model",
        key="model",
        results_dir=results,
        part="demo",
        cd=tmp_path / "w",
        run_dir=tmp_path / "w" / "codex",
        timeout=7200,
    )
    with pytest.raises(worker.WorkerPending) as ei:
        worker.dispatch("build", **kw)
    o = ei.value.order
    assert calls == [{"effort": "high", "timeout": profiles.profile("model").budget_s, "idle": 300.0}]
    assert o.context["fallback_from"] == "codex" and o.context["codex_partial"] == str(tmp_path / "w" / "codex")
    assert "Codex worker started this turn" in o.brief_path.read_text()
    exhausted, info = state.codex_exhausted()
    assert exhausted and info["codex_exhausted_until"] == resets_at
    # the next turn skips Codex entirely while the mark holds
    with pytest.raises(worker.WorkerPending) as ei2:
        worker.dispatch(
            "plan",
            role="plan",
            key="plan",
            results_dir=results,
            part="demo",
            cd=tmp_path / "w",
            run_dir=tmp_path / "w" / "codex2",
        )
    assert len(calls) == 1 and ei2.value.order.context["fallback_from"] == "codex"
    state.clear_codex_exhausted()
    assert not state.codex_exhausted()[0]


def test_codex_no_fallback_stops_instead_of_issuing_a_cursor_order(monkeypatch, tmp_path: Path):
    from opencad.orchestrator import PipelineError

    monkeypatch.setenv("OPENCAD_WORKER", "codex")
    monkeypatch.setenv("OPENCAD_CODEX_NO_FALLBACK", "1")
    monkeypatch.setattr(
        codex_backend,
        "dispatch",
        lambda brief, **kw: WorkerResult("thr", 1, 1.0, 0, {}, Path(kw["run_dir"]), "", failure="usage limit reached", backend="codex"),
    )
    monkeypatch.setattr(codex_backend, "budget", lambda *a, **k: {"known": False, "exhausted": False})
    try:
        with pytest.raises(PipelineError, match="OPENCAD_CODEX_NO_FALLBACK"):
            worker.dispatch("build", role="model", key="model", results_dir=tmp_path / "r", part="demo", cd=tmp_path, run_dir=tmp_path / "codex")
        assert orders.list_orders(tmp_path / "r") == []
    finally:
        state.clear_codex_exhausted()


def test_codex_does_not_resume_a_cursor_agent_id(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENCAD_WORKER", "codex")
    monkeypatch.setattr(codex_backend, "budget", lambda *a, **k: {"known": False, "exhausted": False})
    seen: list[str | None] = []

    def fake_codex(brief, *, resume=None, **kw):
        seen.append(resume)
        return WorkerResult("thr", 0, 1.0, 0, {}, Path(kw["run_dir"]), "## Result\nok", backend="codex")

    monkeypatch.setattr(codex_backend, "dispatch", fake_codex)
    monkeypatch.setattr(orders, "known_agent", lambda results_dir, agent_id: agent_id == "cursor-agent")
    kw = {"role": "correction", "key": "correction-1", "results_dir": tmp_path / "r", "part": "demo", "cd": tmp_path, "run_dir": tmp_path / "codex"}
    worker.dispatch("fix", resume="cursor-agent", **kw)
    worker.dispatch("fix", resume="codex-thread", **{**kw, "key": "correction-2", "run_dir": tmp_path / "codex2"})
    assert seen == [None, "codex-thread"]


def test_codex_opt_in_returns_inline_result(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENCAD_WORKER", "codex")
    monkeypatch.setattr(codex_backend, "budget", lambda *a, **k: {"known": False, "exhausted": False})
    monkeypatch.setattr(
        codex_backend,
        "dispatch",
        lambda brief, **kw: WorkerResult(
            "thr", 0, 5.0, 1, {"input": 10}, Path(kw["run_dir"]), "## Result\nok", backend="codex"
        ),
    )
    r = worker.dispatch(
        "plan",
        role="plan",
        key="plan",
        results_dir=tmp_path / "r",
        part="demo",
        cd=tmp_path / "w",
        run_dir=tmp_path / "w" / "codex",
    )
    assert r.ok and r.backend == "codex" and r.role == "plan" and orders.list_orders(tmp_path / "r") == []


def test_pipeline_run_hands_back_and_continues(monkeypatch, tmp_path: Path):
    from opencad import zoo
    from opencad.contract import template_contract
    from opencad.orchestrator import Ctx
    from opencad.stages import pipeline

    monkeypatch.setattr(zoo, "require_credits", lambda *a, **k: {"known": False})
    monkeypatch.setattr(zoo, "credit_banner", lambda *a, **k: "credits: test")
    design = tmp_path / "designs" / "demo"
    design.mkdir(parents=True)
    ctx = Ctx(
        "demo",
        design,
        design / "contract.yaml",
        template_contract(),
        tmp_path / "results" / "demo",
        tmp_path / "parts" / "demo",
        3600,
        "zoo",
    )
    monkeypatch.setattr(
        ctx.backend.engine, "preflight", lambda: {"ok": True, "version": "test", "billing": {"known": False}}
    )
    # default: the plan is folded into the model turn, so the first order is the model turn
    assert pipeline.run(ctx, skip_blockout=True) == 75
    first = orders.pending(ctx.results_dir)
    assert [o.role for o in first] == ["model"] and json.loads((ctx.results_dir / "plan.json").read_text())["folded"]
    assert "Plan first, inside this turn" in first[0].brief_path.read_text()
    # --plan-separately restores the read-only planning turn
    code = pipeline.run(ctx, skip_blockout=True, plan_separately=True)
    assert code == 75
    st = state.load(ctx.results_dir)
    assert st["phase"] == "stages" and st["stage"] == "plan"
    pend = orders.pending(ctx.results_dir)
    assert len(pend) == 1 and pend[0].role == "plan" and pend[0].read_only
    _finish_order(
        pend[0], result="## Result\n1. base plate\n## Files changed\nnone\n## Verification\n-\n## Open questions\n-\n"
    )
    code = pipeline.run(ctx, cont=True)
    assert code == 75
    assert (ctx.results_dir / "plan.md").read_text().startswith("1. base plate")
    plan = json.loads((ctx.results_dir / "plan.json").read_text())
    assert plan["ok"] and plan["worker"]["backend"] == "cursor" and plan["thread_id"] == "agent-1"
    st = state.load(ctx.results_dir)
    assert st["stage"] == "model"
    pend = orders.pending(ctx.results_dir)
    assert [o.role for o in pend] == ["model"] and pend[0].deliverables == [ctx.kcl_target]
    assert ctx.part_dir in pend[0].writable_dirs
    with pytest.raises(Exception):
        pipeline.run(ctx, cont=False, from_stage="nope")  # a bad stage name still fails fast


def test_correction_loop_is_bounded_and_stops_on_repeat(monkeypatch, tmp_path: Path):
    """After failed gates the pipeline runs short correction turns (not one full retry), each followed by the evaluator; identical failures stop it."""
    from opencad import zoo
    from opencad.contract import template_contract
    from opencad.orchestrator import Ctx
    from opencad.stages import pipeline

    monkeypatch.setattr(zoo, "require_credits", lambda *a, **k: {"known": False})
    monkeypatch.setattr(zoo, "credit_banner", lambda *a, **k: "credits: test")
    design = tmp_path / "designs" / "demo"
    design.mkdir(parents=True)
    ctx = Ctx(
        "demo",
        design,
        design / "contract.yaml",
        template_contract(),
        tmp_path / "results" / "demo",
        tmp_path / "parts" / "demo",
        3600,
        "zoo",
    )
    monkeypatch.setattr(
        ctx.backend.engine, "preflight", lambda: {"ok": True, "version": "test", "billing": {"known": False}}
    )
    ctx.results_dir.mkdir(parents=True)
    ctx.part_dir.mkdir(parents=True)
    ctx.kcl_target.write_text("a = 1\n")
    ctx.write_stage("model", {"ok": True, "thread_id": "agent-9", "codex_report": {"Result": "built"}})
    for st in (
        "verify",
        "export",
        "inspect",
        "edit",
    ):  # the evaluator is faked below; these JSONs stand in for its output
        ctx.write_stage(
            st, {"ok": True, "files": {"step": {"path": str(tmp_path / "x.step")}}, "engine": {"class": "ok"}}
        )
    calls: list[str] = []
    gate_runs = {"n": 0}

    def fake_gates(ctx_, extra=None):
        gate_runs["n"] += 1
        failed = ["features"] if gate_runs["n"] <= 3 else []
        fb = {
            "ok": not failed,
            "summary": {},
            "failed": failed,
            "retryable_failed": failed,
            "gates": [{"id": "features", "ok": not failed}],
        }
        if extra:
            fb.update(extra)
        (ctx_.results_dir / "gate_feedback.json").write_text(json.dumps(fb))
        return fb

    monkeypatch.setattr(pipeline, "run_gates", fake_gates)
    monkeypatch.setattr(pipeline, "_run_evaluator", lambda ctx_: calls.append("evaluator"))

    def fake_finish(ctx_, fb):
        (ctx_.results_dir / "gate_feedback.json").write_text(json.dumps(fb))
        return fb

    monkeypatch.setattr(pipeline, "finish", fake_finish)
    monkeypatch.setattr(pipeline.gates_mod, "correction_message", lambda ctx_, fb: "move hole H3 by 0.7 mm")
    # the worker "edits" the KCL each turn so the loop sees progress until the signature repeats
    orig_dispatch = worker.dispatch

    def fake_dispatch(brief, *, role, key, **kw):
        calls.append(key)
        ctx.kcl_target.write_text(ctx.kcl_target.read_text() + f"# {key}\n")
        return WorkerResult("agent-9", 0, 30.0, 3, {}, tmp_path / key, "## Result\nfixed", backend="cursor", role=role)

    monkeypatch.setattr(worker, "dispatch", fake_dispatch)

    def fake_stage(ctx_, name):
        data = {"ok": True, "files": {"step": {"path": str(tmp_path / "x.step")}}, "engine": {"class": "ok"}}
        ctx_.write_stage(name, data)
        return data

    monkeypatch.setattr(pipeline, "run_stage", fake_stage)
    code = pipeline.run(ctx, skip_blockout=True, from_stage="verify")
    fb = json.loads((ctx.results_dir / "gate_feedback.json").read_text())
    r = fb["retry"]
    # correction-1 changes the KCL but the failure repeats identically -> stop after the second identical signature
    assert calls[:3] == ["correction-1", "evaluator", "correction-2"] and r["attempted"] and r["corrections"] == 2
    assert r["stopped"].startswith("same failure") and r["history"][0]["role"] == "correction" and code == 1
    assert (ctx.load_stage("model") or {})["corrections"][0]["key"] == "correction-1" and len(
        (ctx.load_stage("model") or {})["corrections"]
    ) == 2
    monkeypatch.setattr(worker, "dispatch", orig_dispatch)


def _loop_ctx(monkeypatch, tmp_path: Path, failing: list[str]):
    """A pipeline context at the retry decision with `failing` cylinder items in inspect.json and a faked evaluator."""
    from opencad import zoo
    from opencad.contract import template_contract
    from opencad.orchestrator import Ctx
    from opencad.stages import pipeline

    monkeypatch.setattr(zoo, "require_credits", lambda *a, **k: {"known": False})
    monkeypatch.setattr(zoo, "credit_banner", lambda *a, **k: "credits: test")
    design = tmp_path / "designs" / "demo"
    design.mkdir(parents=True)
    ctx = Ctx(
        "demo",
        design,
        design / "contract.yaml",
        template_contract(),
        tmp_path / "results" / "demo",
        tmp_path / "parts" / "demo",
        3600,
        "zoo",
    )
    monkeypatch.setattr(
        ctx.backend.engine, "preflight", lambda: {"ok": True, "version": "test", "billing": {"known": False}}
    )
    ctx.results_dir.mkdir(parents=True)
    ctx.part_dir.mkdir(parents=True)
    ctx.kcl_target.write_text("a = 1\n")
    ctx.write_stage("model", {"ok": True, "thread_id": "agent-9", "codex_report": {"Result": "built"}})
    ok_stage = {"ok": True, "files": {"step": {"path": str(tmp_path / "x.step")}}, "engine": {"class": "ok"}}
    for st in ("verify", "export", "edit"):
        ctx.write_stage(st, ok_stage)
    ctx.write_stage("inspect", {**ok_stage, "cylinders": {n: {"ok": False} for n in failing}})

    def fake_stage(ctx_, name):
        data = {**ok_stage, "cylinders": {n: {"ok": False} for n in failing}} if name == "inspect" else ok_stage
        ctx_.write_stage(name, data)
        return data

    def fake_finish(ctx_, fb):
        (ctx_.results_dir / "gate_feedback.json").write_text(json.dumps(fb))
        return fb

    monkeypatch.setattr(pipeline, "run_stage", fake_stage)
    monkeypatch.setattr(pipeline, "finish", fake_finish)
    monkeypatch.setattr(pipeline.gates_mod, "correction_message", lambda ctx_, fb: "fix the clamp")
    return ctx, pipeline, ok_stage


def _fake_gates(pipeline, fails_until: int):
    runs = {"n": 0}

    def fake(ctx_, extra=None):
        runs["n"] += 1
        failed = ["features"] if runs["n"] <= fails_until else []
        fb = {
            "ok": not failed,
            "summary": {},
            "failed": failed,
            "retryable_failed": failed,
            "gates": [{"id": "features", "ok": not failed}],
        }
        if extra:
            fb.update(extra)
        (ctx_.results_dir / "gate_feedback.json").write_text(json.dumps(fb))
        return fb

    return fake


def test_correction_loop_earns_turns_past_the_floor_while_the_failing_count_falls(monkeypatch, tmp_path: Path):
    """Five failing items fixed one per turn: the loop runs five corrections (floor is three) because every turn made progress."""
    ctx, pipeline, ok_stage = _loop_ctx(monkeypatch, tmp_path, ["c1", "c2", "c3", "c4", "c5"])
    monkeypatch.setattr(pipeline, "run_gates", _fake_gates(pipeline, fails_until=5))
    turn = {"n": 0}

    def fake_evaluator(ctx_):
        left = [f"c{i}" for i in range(turn["n"] + 1, 6)]  # c1 fixed after turn 1, c2 after turn 2, ...
        for st in ("verify", "export", "edit"):
            ctx_.write_stage(st, ok_stage)
        ctx_.write_stage("inspect", {**ok_stage, "cylinders": {n: {"ok": False} for n in left}})

    monkeypatch.setattr(pipeline, "_run_evaluator", fake_evaluator)

    def fake_dispatch(brief, *, role, key, budget=None, **kw):
        turn["n"] += 1
        ctx.kcl_target.write_text(ctx.kcl_target.read_text() + f"# {key}\n")
        return WorkerResult(
            "agent-9",
            0,
            30.0,
            3,
            {},
            tmp_path / key,
            "## Result\nfixed",
            backend="cursor",
            role=role,
            metrics={"budget": budget},
        )

    monkeypatch.setattr(worker, "dispatch", fake_dispatch)
    code = pipeline.run(ctx, skip_blockout=True, from_stage="verify")
    r = json.loads((ctx.results_dir / "gate_feedback.json").read_text())["retry"]
    assert code == 0 and r["stopped"] == "gates pass" and r["corrections"] == 5 > pipeline.CORRECTION_FLOOR
    assert [h["failing_count"] for h in r["history"]] == [4, 3, 2, 1, 0] and r["history"][3]["role"] == "correction"
    assert r["history"][0]["budget_s"] == 900 + 60 * 5  # scaled by the failing-item count before the turn


def test_stuck_class_is_none_when_the_gates_pass(monkeypatch, tmp_path: Path):
    """A worker that checkpointed incomplete mid-round is not a stuck attempt once a later round passes the gates."""
    ctx, pipeline, _ = _loop_ctx(monkeypatch, tmp_path, ["a"])
    rec = {"history": [{"key": "correction-1", "incomplete": True}, {"key": "correction-2"}], "stopped": "gates pass"}
    assert pipeline.stuck_class(ctx, rec) is None
    assert (
        pipeline.stuck_class(ctx, {**rec, "stopped": "same failure after correction-2: x"}) == "incomplete-checkpoint"
    )


def test_correction_loop_stops_when_the_failing_count_stagnates(monkeypatch, tmp_path: Path):
    """Different items fail each turn but the count never falls: two such turns are no progress."""
    ctx, pipeline, ok_stage = _loop_ctx(monkeypatch, tmp_path, ["a", "b", "c", "d", "e"])
    monkeypatch.setattr(pipeline, "run_gates", _fake_gates(pipeline, fails_until=99))
    turn = {"n": 0}

    def fake_evaluator(ctx_):
        for st in ("verify", "export", "edit"):
            ctx_.write_stage(st, ok_stage)
        ctx_.write_stage(
            "inspect", {**ok_stage, "cylinders": {n: {"ok": False} for n in ["a", "b", "c", "d", f"new{turn['n']}"]}}
        )

    monkeypatch.setattr(pipeline, "_run_evaluator", fake_evaluator)

    def fake_dispatch(brief, *, role, key, **kw):
        turn["n"] += 1
        ctx.kcl_target.write_text(ctx.kcl_target.read_text() + f"# {key}\n")
        return WorkerResult("agent-9", 0, 30.0, 3, {}, tmp_path / key, "## Result\nfixed", backend="cursor", role=role)

    monkeypatch.setattr(worker, "dispatch", fake_dispatch)
    code = pipeline.run(ctx, skip_blockout=True, from_stage="verify")
    r = json.loads((ctx.results_dir / "gate_feedback.json").read_text())["retry"]
    assert (
        code == 1
        and r["corrections"] == 2
        and r["stopped"].startswith("no progress after correction-2")
        and r["stuck_class"] == "no-progress"
    )


def test_continued_round_re_measures_when_the_contract_changed(monkeypatch, tmp_path: Path):
    """The orchestrator edits the contract while a round's worker turn is pending: on continue the loop re-runs the evaluator and gates
    against the new contract and rebuilds the correction text instead of briefing the next turn from the stale one."""
    from opencad.paths import CONTRACT_FILE, TEMPLATE

    ctx, pipeline, _ = _loop_ctx(monkeypatch, tmp_path, ["c1"])
    template = (TEMPLATE / CONTRACT_FILE).read_text()
    ctx.contract_path.write_text(template)
    monkeypatch.setattr(pipeline, "run_gates", _fake_gates(pipeline, fails_until=2))
    calls: list[str] = []
    monkeypatch.setattr(pipeline, "_run_evaluator", lambda ctx_: calls.append("evaluator"))
    monkeypatch.setattr(
        pipeline.gates_mod,
        "correction_message",
        lambda ctx_, fb: calls.append("message") or f"fix v{calls.count('message')}",
    )
    assert pipeline.run(ctx, skip_blockout=True, from_stage="verify") == 75
    rec = state.load(ctx.results_dir)["retry"]
    assert rec["in_progress"] and rec["contract_sha"] and rec["correction"] == "fix v1" and calls == ["message"]
    pend = orders.pending(ctx.results_dir)
    assert len(pend) == 1 and pend[0].key == "correction-1"
    ctx.contract_path.write_text(template.replace("tolerance_rel: 0.002", "tolerance_rel: 0.001", 1))  # tightened while the turn was out
    _finish_order(
        pend[0], result="## Result\nfixed\n## Files changed\nmain.kcl\n## Verification\n-\n## Open questions\n-\n"
    )
    code = pipeline.run(ctx, cont=True)
    r = json.loads((ctx.results_dir / "gate_feedback.json").read_text())["retry"]
    # re-measured before the (already finished) turn was consumed, then the normal evaluator pass after it
    assert calls == ["message", "evaluator", "message", "evaluator"] and code == 0 and r["stopped"] == "gates pass"
    assert ctx.contract.acceptance.volume.tolerance_rel == 0.001, "the re-measure reads the edited contract, not the one loaded at start"
    rec = state.load(ctx.results_dir) or {}
    assert not rec  # the run finished and cleared its state


def test_decomposed_round_measures_the_modules_before_an_integrate_turn(monkeypatch, tmp_path: Path):
    """After a round's module corrections the pipeline measures main.py (it imports the modules) first: gates that pass need no integrate
    turn; gates that still fail get an integrate turn briefed from the fresh measurements."""
    from opencad.stages import decompose, verify

    monkeypatch.setattr(verify, "render_snapshots", lambda ctx_: {})
    for passes_after_modules, expect_integrate in ((True, False), (False, True)):
        root = tmp_path / str(passes_after_modules)
        ctx, pipeline, _ = _loop_ctx(monkeypatch, root, ["c1"])
        ctx.write_stage(
            "model", {"ok": True, "decomposed": True, "thread_id": "agent-9", "codex_report": {"Result": "built"}}
        )
        calls: list[str] = []
        monkeypatch.setattr(pipeline, "run_gates", _fake_gates(pipeline, fails_until=1 if passes_after_modules else 2))
        monkeypatch.setattr(pipeline, "_run_evaluator", lambda ctx_: calls.append("evaluator"))
        monkeypatch.setattr(
            pipeline.gates_mod,
            "correction_message",
            lambda ctx_, fb: calls.append("message") or f"fix v{calls.count('message')}",
        )

        def fake_modules(ctx_, correction, key):
            calls.append(f"modules {key}")
            (ctx_.part_dir / "clamp.kcl").write_text(f"# {key}\n")
            return {"modules": {"clamp": {"ok": True}}, "items": {"clamp": ["cylinders/c1"]}}

        monkeypatch.setattr(decompose, "module_corrections", fake_modules)
        briefs: list[str] = []

        def fake_dispatch(brief, *, role, key, **kw):
            calls.append(key)
            briefs.append(brief)
            ctx.kcl_target.write_text(ctx.kcl_target.read_text() + f"# {key}\n")
            return WorkerResult("agent-9", 0, 30.0, 3, {}, root / key, "## Result\nfixed", backend="cursor", role=role)

        monkeypatch.setattr(worker, "dispatch", fake_dispatch)
        code = pipeline.run(ctx, skip_blockout=True, from_stage="verify")
        r = json.loads((ctx.results_dir / "gate_feedback.json").read_text())["retry"]
        assert code == 0 and r["stopped"] == "gates pass" and ("correction-1" in calls) is expect_integrate
        if expect_integrate:
            assert calls == ["message", "modules correction-1", "evaluator", "message", "correction-1", "evaluator"]
            assert briefs[0].startswith("fix v2") and "Module-level corrections were applied" in briefs[0]
        else:
            assert calls == ["message", "modules correction-1", "evaluator"] and r["history"][0]["integrate_skipped"]


def test_stagnation_restarts_after_a_mid_round_contract_change():
    """Counts measured against different contracts are not compared: 6 -> 3 -> (contract changed) 9 -> 4 is progress, not stagnation."""
    from opencad.stages import pipeline

    hist = [{"failing_count": 3}, {"failing_count": 9, "contract_changed": True}, {"failing_count": 4}]
    stagnated, seq = pipeline._stagnated(6, hist)
    assert not stagnated and seq == [9, 4]
    assert pipeline._stagnated(6, [{"failing_count": 6}, {"failing_count": 6}]) == (True, [6, 6, 6])
    stagnated, _ = pipeline._stagnated(
        6,
        [
            {"failing_count": 3},
            {"failing_count": 9, "contract_changed": True},
            {"failing_count": 9},
            {"failing_count": 9},
        ],
    )
    assert stagnated, "two flat rounds after the change still stop the loop"
    # one rising round (compensating geometry retired, items exposed) is allowed; the next round decides
    assert not pipeline._stagnated(12, [{"failing_count": 11}, {"failing_count": 10}, {"failing_count": 13}])[0]
    assert pipeline._stagnated(
        12, [{"failing_count": 11}, {"failing_count": 10}, {"failing_count": 13}, {"failing_count": 13}]
    )[0]


def test_correction_that_does_not_execute_is_reverted_to_the_checkpoint(monkeypatch, tmp_path: Path):
    """A correction leaves a non-executing source: the pipeline restores the worker's checkpoint, re-measures, and the turn does not end the loop."""
    ctx, pipeline, ok_stage = _loop_ctx(monkeypatch, tmp_path, ["c1", "c2"])
    monkeypatch.setattr(pipeline, "run_gates", _fake_gates(pipeline, fails_until=2))
    checkpoint = ctx.results_dir / "model-work" / "checkpoint.kcl"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text("a = 1\n# checkpoint\n")
    evals = {"n": 0}

    def fake_evaluator(ctx_):
        evals["n"] += 1
        broken = ctx_.kcl_target.read_text().endswith("# correction-1\n")
        exp = (
            {"ok": False, "engine": {"class": "program"}, "errors": {"step": "execution failed: syntax"}}
            if broken
            else ok_stage
        )
        ctx_.write_stage("verify", ok_stage)
        ctx_.write_stage("export", exp)
        ctx_.write_stage("edit", ok_stage)
        ctx_.write_stage("inspect", {**ok_stage, "cylinders": {"c1": {"ok": False}, "c2": {"ok": False}}})

    monkeypatch.setattr(pipeline, "_run_evaluator", fake_evaluator)

    def fake_dispatch(brief, *, role, key, **kw):
        ctx.kcl_target.write_text(ctx.kcl_target.read_text() + f"# {key}\n")
        return WorkerResult("agent-9", 0, 30.0, 3, {}, tmp_path / key, "## Result\nfixed", backend="cursor", role=role)

    monkeypatch.setattr(worker, "dispatch", fake_dispatch)
    code = pipeline.run(ctx, skip_blockout=True, from_stage="verify")
    r = json.loads((ctx.results_dir / "gate_feedback.json").read_text())["retry"]
    assert (
        r["history"][0]["reverted_to_checkpoint"] is True and evals["n"] == 3
    )  # broken turn measured, reverted, measured again; then turn 2
    assert (
        code == 0
        and r["stopped"] == "gates pass"
        and r["corrections"] == 2
        and r["history"][1]["reverted_to_checkpoint"] is False
    )
    assert "# checkpoint" in ctx.kcl_target.read_text() and "# correction-1" not in ctx.kcl_target.read_text()


def test_sequester_keep_and_attach(tmp_path: Path, monkeypatch):
    from opencad.truth import runner

    case = tmp_path / "cases" / "c1"
    (case / "truth").mkdir(parents=True)
    (case / "truth" / "ref.step").write_text("x")
    (case / "manifest.yaml").write_text("id: c1\n")
    monkeypatch.setattr(runner, "case_dir", lambda cid: case)
    monkeypatch.setattr(runner, "VAULT", tmp_path / "vault")
    with runner.Sequester("c1") as s:
        s.keep()
        vault = s.dst
    assert (
        not (case / "truth").exists() and (vault / "truth" / "ref.step").exists() and (vault / "manifest.yaml").exists()
    ), "kept vaulted for the worker"
    with runner.Sequester.attach("c1", vault):
        assert not (case / "truth").exists()
    assert (case / "truth" / "ref.step").read_text() == "x" and (case / "manifest.yaml").exists() and not vault.exists()
    # a gone vault with truth back in the tree (a crash restored it) sequesters again instead of failing the continue
    again = runner.Sequester.attach("c1", tmp_path / "gone")
    with again:
        assert not (case / "truth").exists()
    assert (case / "truth" / "ref.step").exists()
    shutil.rmtree(case / "truth")
    (case / "manifest.yaml").unlink()
    with pytest.raises(Exception):
        runner.Sequester.attach("c1", tmp_path / "gone")


def test_sequester_concurrent_holders(tmp_path: Path, monkeypatch):
    from opencad.truth import runner

    case = tmp_path / "cases" / "c2"
    (case / "truth").mkdir(parents=True)
    (case / "truth" / "ref.step").write_text("x")
    (case / "manifest.yaml").write_text("id: c2\n")
    monkeypatch.setattr(runner, "case_dir", lambda cid: case)
    monkeypatch.setattr(runner, "VAULT", tmp_path / "vault")
    a = runner.Sequester("c2")
    b = runner.Sequester("c2")
    a.__enter__()
    b.__enter__()
    assert not (case / "truth").exists()
    a.__exit__(None, None, None)
    assert not (case / "truth").exists(), "first holder exit does not restore"
    b.__exit__(None, None, None)
    assert (case / "truth" / "ref.step").read_text() == "x"


def test_lean_prompt_inlines_skill_prior_results_and_critic_method(tmp_path: Path, monkeypatch):
    from opencad.paths import DESIGNS

    monkeypatch.setenv("OPENCAD_LEAN_TURNS", "1")
    results = tmp_path / "results" / "demo"
    prior = results / "worker" / "001-draft" / "result.md"
    prior.parent.mkdir(parents=True)
    prior.write_text("## Result\ndrafted the contract\n\n## Open questions\nnone yet\n", encoding="utf-8")
    order = orders.issue(
        results,
        key="model",
        role="model",
        part="demo",
        brief="Build the part.",
        cwd=tmp_path / "work",
        model="m",
        budget_s=60,
    )
    order.backend = "build123d"
    order.context["contract"] = str(DESIGNS / "bracket" / "contract.yaml")
    text = orders.prompt(order, "Build the part.", previous=[prior])
    assert "### SKILL.md" in text and "taper=draftAngle" in text and "mirror it across each plane" in text
    assert "description: Worker pack" not in text
    assert "do not re-read them" in text
    assert "drafted the contract" in text and "none yet" in text
    assert "How the critic measures" in text and "- sections:" in text
    assert "quick" in text and "--all" in text
    header, _, _ = text.partition("# Task")
    assert "Read only this brief" in header and "inspect.signature" in header
    draft = orders.issue(
        results,
        key="draft",
        role="draft",
        part="demo",
        brief="Draft the contract.",
        cwd=tmp_path / "work",
        model="m",
        budget_s=60,
    )
    draft.backend = "build123d"
    draft_text = orders.prompt(draft, "Draft the contract.")
    draft_header, _, _ = draft_text.partition("# Task")
    assert "Read only this brief" in draft_header and "inspect.signature" not in draft_header


@pytest.mark.parametrize(("backend", "marker"), [("cadquery", "import cadquery as cq"), ("freecad", "PartDesign::Mirrored")])
def test_lean_prompt_inlines_the_skill_on_the_other_python_backends(tmp_path: Path, monkeypatch, backend: str, marker: str):
    from opencad.paths import DESIGNS

    monkeypatch.setenv("OPENCAD_LEAN_TURNS", "1")
    order = orders.issue(
        tmp_path / "results" / "demo", key="model", role="model", part="demo", brief="Build the part.", cwd=tmp_path / "work", model="m", budget_s=60
    )
    order.backend = backend
    order.context["contract"] = str(DESIGNS / "bracket" / "contract.yaml")
    text = orders.prompt(order, "Build the part.")
    header, _, _ = text.partition("# Task")
    assert "Read only this brief" in header and "inlined at the end" in header
    assert "### SKILL.md" in text and marker in text and "it across each plane" in text
    assert "description: Worker pack" not in text
    assert "How the critic measures" in text

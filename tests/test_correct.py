"""opencad correct: a deliberate geometry turn on the model thread, then re-verify."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from opencad import worker
from opencad.contract import template_contract
from opencad.orchestrator import Ctx
from opencad.stages import correct
from opencad.worker import orders
from tests.test_worker import _finish_order


def _ctx(tmp_path: Path, monkeypatch) -> Ctx:
    design = tmp_path / "designs" / "demo"
    design.mkdir(parents=True)
    ctx = Ctx("demo", design, design / "contract.yaml", template_contract(), tmp_path / "results" / "demo", tmp_path / "parts" / "demo", 3600, "zoo")
    monkeypatch.setattr(ctx.backend.engine, "preflight", lambda: {"ok": True, "version": "test", "billing": {"known": False}})
    ctx.results_dir.mkdir(parents=True)
    ctx.part_dir.mkdir(parents=True)
    ctx.entry.write_text("a = 1\n")
    ctx.write_stage("model", {"ok": True, "thread_id": "agent-9", "codex_report": {"Result": "built"}})
    ctx.write_stage("gate_feedback", {"ok": True, "summary": {"pass": 11, "fail": 0, "not_applicable": 1}})
    prior = orders.issue(
        ctx.results_dir, key="model", role="model", part="demo", brief="model", cwd=ctx.results_dir / "model-work",
        deliverables=[ctx.entry], model="inherit", budget_s=100,
    )
    prior.dispatch_path.write_text(json.dumps({"agent_id": "agent-9", "model": "inherit"}))
    prior.done_path.touch()
    prior.status = "done"
    orders.save(prior)
    return ctx


def test_correct_issues_improve_order_then_verifies(tmp_path: Path, monkeypatch):
    ctx = _ctx(tmp_path, monkeypatch)
    with pytest.raises(worker.WorkerPending) as ei:
        correct.run(ctx, note="smooth the hull")
    o = ei.value.order
    assert o.key == "improve-1" and o.role == "correction" and o.resume_of == "agent-9"
    text = o.brief_path.read_text()
    assert "smooth the hull" in text and "gate_feedback.json" in text
    state = json.loads((ctx.results_dir / "correct.json").read_text())
    assert state["key"] == "improve-1" and state["phase"] == "worker"

    _finish_order(o, agent_id="agent-9")
    calls: list[tuple] = []

    def fake_pipeline(ctx_, *, cont=False, skip_blockout=False, from_stage="plan", allow_retry=True, **kw):
        calls.append((cont, skip_blockout, from_stage, allow_retry))
        return 0

    monkeypatch.setattr("opencad.stages.pipeline.run", fake_pipeline)
    data = correct.run(ctx, note="", cont=True)
    assert data["pipeline_code"] == 0 and data["phase"] == "done"
    assert calls == [(False, True, "verify", True)]
    assert (ctx.load_stage("model") or {}).get("corrections")[-1]["key"] == "improve-1"


def test_delta_vs_previous_reports_changed_side(tmp_path: Path):
    import trimesh

    a = trimesh.creation.box(extents=(10, 10, 4))
    b = a.copy()
    v = b.vertices.copy()
    v[v[:, 1] > 4.9, 1] += 2.0
    b = trimesh.Trimesh(v, b.faces, process=True)
    prev, new = tmp_path / "prev.stl", tmp_path / "new.stl"
    a.export(prev)
    b.export(new)
    d = correct._delta_vs_previous(prev, new, "y", 0.0)
    assert d["max"] == pytest.approx(2.0, abs=0.2)
    assert d["changed_area_positive"] > d["changed_area_negative"]
    assert d["changed_region_bbox"] is not None

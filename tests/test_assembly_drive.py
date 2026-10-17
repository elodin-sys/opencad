"""`assembly drive` hand-back protocol: the assemble turn is issued as a work order with one EVENT#k line, a simulated worker
finishes it, and the driver continues through the evaluator stages to a report without being re-run. The /initialize-cad
checkpoint (`--stop-after`), the blockout-only part lane and the pre-build revision are tested with stubbed turns."""

import copy
import io
import json
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from test_assembly_pipeline import CONTRACT, SOURCE, _parts


def _fake_worker(root: Path, stop: threading.Event) -> None:
    orders = root / "results" / "build123d" / "t-mixer" / "worker"
    while not stop.is_set():
        for od in sorted(orders.glob("*/order.json")) if orders.exists() else []:
            d = od.parent
            if (d / "done").exists():
                continue
            entry = root / "parts" / "build123d" / "t-mixer" / "main.py"
            entry.write_text(SOURCE, encoding="utf-8")
            (d / "result.md").write_text("## Result\nplaced\n## Files changed\n- main.py\n## Verification\nVisual: ok\n## Open questions\n- none\n", encoding="utf-8")
            (d / "metrics.json").write_text(json.dumps({"commands": 1, "self_corrections": 0, "engine_calls": 1, "files_changed": [str(entry)], "incomplete": False}))
            (d / "done").touch()
        time.sleep(0.2)


def test_drive_hands_back_the_assemble_turn_and_finishes(tmp_path, monkeypatch):
    import opencad.assembly as asm
    import opencad.assembly.pipeline as pipe
    from opencad import paths
    from opencad.backends.registry import set_backend
    from opencad.worker import orders

    set_backend("build123d")
    for mod, attr, val in ((paths, "DESIGNS", tmp_path / "designs"), (paths, "RESULTS_BASE", tmp_path / "results"), (paths, "PARTS_BASE", tmp_path / "parts"),
                           (asm, "DESIGNS", tmp_path / "designs"), (pipe, "DESIGNS", tmp_path / "designs"), (pipe, "RESULTS_BASE", tmp_path / "results")):
        monkeypatch.setattr(mod, attr, val)
    monkeypatch.setattr(orders, "wait", lambda d, **kw: _poll(orders, d))
    design = tmp_path / "designs" / "t-mixer"
    design.mkdir(parents=True)
    (design / "assembly.yaml").write_text(yaml.safe_dump(CONTRACT), encoding="utf-8")
    (design / "brief.md").write_text("# t-mixer\n", encoding="utf-8")
    for leaf in ("housing", "rotor"):
        rd = tmp_path / "results" / "build123d" / "t-mixer" / "parts" / leaf
        (rd / "handoff").mkdir(parents=True)
        (rd / "gate_feedback.json").write_text(json.dumps({"ok": True, "summary": "12 pass"}))
    staging = tmp_path / "inputs"
    staging.mkdir()
    _parts(staging)
    for leaf in ("housing", "rotor"):
        d = f"t-mixer-{leaf}"
        (tmp_path / "results" / "build123d" / "t-mixer" / "parts" / leaf / "handoff" / f"{d}.step").write_bytes((staging / f"{d}.step").read_bytes())
    stop = threading.Event()
    th = threading.Thread(target=_fake_worker, args=(tmp_path, stop), daemon=True)
    th.start()
    out = io.StringIO()
    try:
        code = pipe.drive("t-mixer", backend="build123d", out=out)
    finally:
        stop.set()
        th.join()
    log = out.getvalue()
    events = [line for line in log.splitlines() if line.startswith("EVENT#")]
    assert len(events) == 1 and '"role": "assemble"' in events[0], log
    rd = tmp_path / "results" / "build123d" / "t-mixer"
    fb = json.loads((rd / "gate_feedback.json").read_text())
    assert code == 0 and fb["ok"], [g for g in fb["gates"] if g["ok"] is False]
    assert not (rd / "pipeline-state.json").exists()
    assert (rd / "handoff" / "assembly.glb").exists() and (rd / "report.md").read_text().startswith("# t-mixer (build123d): PASS")
    assert (rd / "package" / "geometry" / "t-mixer.step").exists() and (rd / "package" / "provenance" / "provenance.json").exists()
    stls = sorted(p.name for p in (rd / "boundaries").glob("*.stl"))
    assert stls and stls == sorted(p.name for p in (rd / "package" / "boundaries").glob("*.stl"))
    assert (tmp_path / "parts" / "build123d" / "t-mixer" / "inputs" / "t-mixer-rotor.step").exists()


def _poll(orders, results_dir):
    while orders.pending(results_dir):
        time.sleep(0.2)


def _redirect(monkeypatch, root: Path) -> None:
    import opencad.assembly as asm
    import opencad.assembly.pipeline as pipe
    from opencad import contract, paths
    from opencad.assembly import draft, parts
    from opencad.backends.registry import set_backend

    set_backend("build123d")
    for mod in (paths, asm, pipe, draft, parts, contract):
        for attr, sub in (("DESIGNS", "designs"), ("RESULTS_BASE", "results"), ("PARTS_BASE", "parts")):
            if hasattr(mod, attr):
                monkeypatch.setattr(mod, attr, root / sub)


def _part_bundle(name: str, lo: list[float], hi: list[float]) -> None:
    from opencad.paths import TEMPLATE, design_dir

    c = yaml.safe_load((TEMPLATE / "contract.yaml").read_text())
    c.update(name=name, intent=f"{name} of the synthetic mixer", frame={"origin": "own origin", "axes": {"x": "length", "y": "width", "z": "up"}, "datums": []})
    c["envelope"].update(min=lo, max=hi)
    for p in c["parameters"]:
        p["source"] = "intent"
    d = design_dir(name)
    d.mkdir(parents=True)
    (d / "contract.yaml").write_text(yaml.safe_dump(c), encoding="utf-8")
    (d / "brief.md").write_text(f"# {name}\n\nfilled\n", encoding="utf-8")


def test_stop_after_hands_back_at_the_checkpoint_and_the_build_starts_at_parts(tmp_path, monkeypatch):
    import opencad.assembly.pipeline as pipe
    from opencad.assembly import AssemblyError, draft, parts

    _redirect(monkeypatch, tmp_path)

    def fake_draft(turn, name):
        design = tmp_path / "designs" / name
        design.mkdir(parents=True)
        (design / "assembly.yaml").write_text(yaml.safe_dump(CONTRACT), encoding="utf-8")
        (design / "brief.md").write_text("# t-mixer\n", encoding="utf-8")
        return {"ok": True, "published": [name]}

    monkeypatch.setattr(draft, "run", fake_draft)
    out = io.StringIO()
    assert pipe.drive("t-mixer", backend="build123d", out=out, stop_after="draft") == 0
    rd = tmp_path / "results" / "build123d" / "t-mixer"
    assert not (rd / "pipeline-state.json").exists() and not (rd / "parts.json").exists()
    assert pipe._start(rd, None, None, "t-mixer") == "parts" and "/create-cad designs/t-mixer" in out.getvalue()
    with pytest.raises(AssemblyError, match="from-stage"):
        pipe.drive("t-mixer", backend="build123d", stop_after="blockout", from_stage="assemble")

    def fake_blockouts(actx, session, *, jobs, blockout_only):
        assert blockout_only
        for d in actx.contract.designs():
            p = tmp_path / "results" / "build123d" / "t-mixer" / "parts" / d.removeprefix("t-mixer-") / "blockout.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"ok": True, "snapshots": {"four-ways": f"{d}-four-ways.png"}}))
        return {}

    monkeypatch.setattr(parts, "run", fake_blockouts)
    out = io.StringIO()
    assert pipe.drive("t-mixer", backend="build123d", out=out, stop_after="blockout") == 0
    assert "part t-mixer-rotor" in out.getvalue() and "blockout ok t-mixer-rotor-four-ways.png" in out.getvalue(), out.getvalue()
    assert not (rd / "pipeline-state.json").exists() and not (rd / "parts.json").exists()


def test_blockout_only_lane_stops_before_the_part_pipeline(tmp_path, monkeypatch):
    import opencad.stages.pipeline as part_pipeline
    from opencad.assembly import parts
    from opencad.stages import blockout

    _redirect(monkeypatch, tmp_path)
    _part_bundle("t-mixer-rotor", [-10.0, -2.0, -5.0], [10.0, 2.0, 5.0])
    calls: list[str] = []
    monkeypatch.setattr(blockout, "run", lambda ctx, cont=False: calls.append("blockout") or {"ok": True})
    monkeypatch.setattr(part_pipeline, "run", lambda ctx, **kw: calls.append("pipeline") or 0)
    assert parts.drive_part("t-mixer-rotor", blockout_only=True) == 0 and calls == ["blockout"]
    assert parts.drive_part("t-mixer-rotor") == 0 and calls == ["blockout", "pipeline"]  # a build lane skips a small contract's blockout
    assert parts.lane_argv("t-mixer-rotor", "build123d", blockout_only=True)[-1] == "--blockout-only"


def test_a_fresh_blockout_drops_the_stale_record_and_an_unmeasured_iteration_gets_a_brief(tmp_path, monkeypatch):
    from opencad.orchestrator import Ctx
    from opencad.stages import blockout
    from opencad.worker import WorkerPending, orders

    _redirect(monkeypatch, tmp_path)
    _part_bundle("t-mixer-rotor", [-10.0, -2.0, -5.0], [10.0, 2.0, 5.0])
    ctx = Ctx.load("t-mixer-rotor")
    stale = ctx.stage_file("blockout")
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text(json.dumps({"ok": False, "pending": True, "thread_id": "old", "iterations": [{"iteration": 1, "measured": {"ok": False, "error": "x"}}]}))

    def pending(msg, **kw):
        raise WorkerPending(orders.issue(ctx.results_dir, key=kw["key"], role="blockout", part=ctx.name, brief=msg, cwd=kw["cd"], model="m", budget_s=60))

    monkeypatch.setattr(blockout.worker, "dispatch", pending)
    with pytest.raises(WorkerPending):
        blockout.run(ctx)
    assert not stale.exists()
    assert "could not be measured: the worker produced no main.py" in blockout.correction({"ok": False, "error": "the worker produced no main.py"})


def test_revise_republishes_only_the_changed_part_and_clears_its_blockout(tmp_path, monkeypatch):
    from opencad.assembly import draft
    from opencad.worker import orders

    _redirect(monkeypatch, tmp_path)
    designs, results = tmp_path / "designs", tmp_path / "results" / "build123d"
    nested_designs, nested_results = designs / "t-mixer" / "parts", results / "t-mixer" / "parts"
    a = copy.deepcopy(CONTRACT)
    for p in a["parts"]:
        if p["kind"] == "modelled":
            p["intent"] += ", in its own frame at the joint origin, every dimension as its contract states"
    (designs / "t-mixer").mkdir(parents=True)
    (designs / "t-mixer" / "assembly.yaml").write_text(yaml.safe_dump(a), encoding="utf-8")
    (designs / "t-mixer" / "brief.md").write_text("# t-mixer\n\nfilled\n", encoding="utf-8")
    for d, lo, hi in (("t-mixer-housing", [-30.0, -20.0, 0.0], [30.0, 20.0, 30.0]), ("t-mixer-rotor", [-10.0, -2.0, -5.0], [10.0, 2.0, 5.0])):
        _part_bundle(d, lo, hi)
        rd = nested_results / d.removeprefix("t-mixer-")
        (rd / "blockout").mkdir(parents=True)
        (rd / "blockout.json").write_text(json.dumps({"ok": True}))
        orders.issue(rd, key="blockout-1", role="blockout", part=d, brief="B.", cwd=rd / "blockout", model="m", budget_s=60)
    assert (nested_designs / "rotor" / "contract.yaml").exists()

    def fake_dispatch(brief, **kw):
        assert kw["key"] == "asm-revise-1" and "the rotor 22 mm long" in brief
        assert not (designs / ".staging-t-mixer" / "parts").exists(), "the staged assembly holds only its own files"
        c = designs / ".staging-t-mixer-rotor" / "contract.yaml"
        c.write_text(c.read_text().replace("of the synthetic mixer", "of the synthetic mixer, revised to 22 mm"), encoding="utf-8")
        return SimpleNamespace(thread_id="agent-1", summary=lambda: {"role": kw["role"]})

    monkeypatch.setattr(draft.worker, "dispatch", fake_dispatch)
    res = draft.revise(lambda fn: fn(), "t-mixer", "Make the rotor 22 mm long.")
    assert res["ok"] and res["changed"] == ["t-mixer-rotor"], res
    assert "revised to 22 mm" in (nested_designs / "rotor" / "contract.yaml").read_text()
    assert "revised" not in (designs / "t-mixer" / ".amended" / "rotor-1" / "contract.yaml").read_text()
    assert not (nested_results / "rotor" / "blockout.json").exists() and not (nested_results / "rotor" / "blockout").exists()
    assert orders.find(nested_results / "rotor", "blockout-1") is None and orders.find(nested_results / "housing", "blockout-1")
    assert (nested_results / "housing" / "blockout.json").exists() and not (designs / "t-mixer" / ".amended" / "housing-1").exists()
    assert not list(designs.glob(".staging-*")) and not (designs / "t-mixer" / ".amended" / "assembly-1").exists()
    assert not (results / "t-mixer" / "revise-pending.json").exists()

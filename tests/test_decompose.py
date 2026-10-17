"""Decomposition: partition validation, sub-contracts, parallel module orders, integrate turn, and the size trigger."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from opencad import worker
from opencad.contract import load_contract, template_contract
from opencad.orchestrator import Ctx
from opencad.stages import decompose
from opencad.worker import orders, state
from opencad.worker.result import WorkerResult


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("OPENCAD_WORKER", raising=False)
    monkeypatch.setattr(state, "CAMPAIGN_STATE", tmp_path / "_campaign" / "worker-state.json")
    from opencad import telemetry

    monkeypatch.setattr(telemetry, "CAMPAIGN_FILE", tmp_path / "_campaign" / "telemetry.jsonl")
    yield


def _ctx(tmp_path: Path, backend: str = "zoo") -> Ctx:
    design = tmp_path / "designs" / "demo"
    design.mkdir(parents=True)
    c = template_contract()
    (design / "contract.yaml").write_text(yaml.safe_dump(json.loads(c.model_dump_json()), sort_keys=False))
    ctx = Ctx("demo", design, design / "contract.yaml", c, tmp_path / "results" / "demo", tmp_path / "parts" / "demo", None, backend)
    ctx.results_dir.mkdir(parents=True)
    ctx.write_stage("plan", {"ok": True, "folded": True})
    return ctx


# minimal executing-looking module sources per language, for the orchestration tests (no engine runs)
STUBS = {
    "zoo": {"params": "export width = 60mm\n", "datum": "export datum = 1\n", "module": "export fn g(@body) { return body }\n",
            "main": "@settings(defaultLengthUnit = mm, kclVersion = 2.0)\nimport datum from \"datum.kcl\"\ndatum\n"},
    "cadquery": {"params": "width = 60.0\n", "datum": "datum = 1\n", "module": "def apply(body):\n    return body\n", "main": "from datum import datum\n\nresult = datum\n"},
}


def _full_partition(ctx: Ctx, n_groups: int = 2) -> dict:
    names = decompose.acceptance_names(ctx.contract)
    feats = [f.id for f in ctx.contract.features]
    groups = [{"id": f"group{i}", "title": f"group {i}", "features": [], "parameters": [], "acceptance": {}, "depends_on": ([] if i == 0 else [f"group{i - 1}"]),
               "region": {"min": [-1000, -1000, -1000], "max": [1000, 1000, 1000]}} for i in range(n_groups)]
    for j, f in enumerate(feats):
        groups[j % n_groups]["features"].append(f)
    for k, lst in names.items():
        for j, n in enumerate(lst):
            groups[j % n_groups]["acceptance"].setdefault(k, []).append(n)
    return {"groups": groups}


def _done(order: orders.WorkOrder, files: dict[Path, str] | None = None) -> None:
    for p, text in (files or {}).items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    order.result_path.write_text("## Result\ndone\n## Files changed\n-\n## Verification\n-\n## Open questions\n-\n")
    order.metrics_path.write_text(json.dumps({"commands": 3, "engine_calls": 1, "incomplete": False}))
    order.dispatch_path.write_text(json.dumps({"agent_id": f"agent-{order.id}", "model": order.model}))
    order.done_path.touch()


def test_validate_partition_reports_coverage_and_files(tmp_path: Path):
    ctx = _ctx(tmp_path)
    data = _full_partition(ctx)
    probs = decompose.validate_partition(ctx, data)
    assert probs == [f"{ctx.part_dir / 'params.kcl'} missing", f"{ctx.part_dir / 'datum.kcl'} missing"]
    ctx.part_dir.mkdir(parents=True)
    (ctx.part_dir / "params.kcl").write_text("export width = 60mm\n")
    (ctx.part_dir / "datum.kcl").write_text("export datum = 1\n")
    assert decompose.validate_partition(ctx, data) == []
    data["groups"][0]["features"].append("nope")
    data["groups"][1]["depends_on"] = ["ghost"]
    probs = decompose.validate_partition(ctx, data)
    assert any("unknown feature nope" in p for p in probs) and any("unknown group ghost" in p for p in probs)
    dup = _full_partition(ctx)
    dup["groups"][1]["features"] = list(dup["groups"][0]["features"]) + dup["groups"][1]["features"]
    assert any("owned by both" in p for p in decompose.validate_partition(ctx, dup))
    noreg = _full_partition(ctx)
    del noreg["groups"][0]["region"]
    assert any("`region` must be" in p for p in decompose.validate_partition(ctx, noreg))


def test_subcontract_keeps_only_owned_items(tmp_path: Path):
    ctx = _ctx(tmp_path)
    data = _full_partition(ctx, 2)
    g = data["groups"][0]
    dest = decompose.write_subcontract(ctx, g, tmp_path / "sub" / "contract.yaml")
    sub = load_contract(dest)
    assert sub.name == "demo-group0" and {f.id for f in sub.features} == set(g["features"])
    assert sub.acceptance.volume is None and sub.acceptance.center_of_mass is None
    assert [s.id for s in sub.acceptance.sections] == list((g["acceptance"].get("sections") or []))
    assert len(sub.parameters) == len(ctx.contract.parameters)


def test_subcontract_leaves_sections_that_cross_other_regions_to_the_composed_critic(tmp_path: Path):
    """A section plane that also cuts another group's region has no standalone meaning: its band is dropped from the module's
    sub-contract and the intent names it as composed-only; a plane inside the group's own region alone keeps its band."""
    from opencad.schemas import Section, SectionExpect

    ctx = _ctx(tmp_path)
    ctx.contract.acceptance.sections = [Section(id="own_z2", plane="z", at=2.0, expect=SectionExpect(area=100.0)),
                                        Section(id="shared_z6", plane="z", at=6.0, expect=SectionExpect(area=200.0))]
    ctx.contract_path.write_text(yaml.safe_dump(json.loads(ctx.contract.model_dump_json()), sort_keys=False))
    data = _full_partition(ctx, 2)
    g, other = data["groups"]
    g["acceptance"]["sections"] = ["own_z2", "shared_z6"]
    other["acceptance"].pop("sections", None)
    g["region"] = {"min": [0, 0, 0], "max": [20, 20, 4]}
    other["region"] = {"min": [0, 0, 4], "max": [20, 20, 10]}  # z = 6 cuts it; z = 2 does not
    raw = yaml.safe_load(ctx.contract_path.read_text())
    assert decompose.composed_only_sections(raw, g, data) == ["shared_z6"]
    assert decompose.composed_only_sections(raw, g, None) == []
    sub = load_contract(decompose.write_subcontract(ctx, g, tmp_path / "sub" / "contract.yaml", partition=data))
    assert [s.id for s in sub.acceptance.sections] == ["own_z2"]
    assert "shared_z6" in sub.intent and "judged on the composed part only" in sub.intent


def test_apply_order_respects_dependencies():
    groups = [{"id": "c", "depends_on": ["b"]}, {"id": "a"}, {"id": "b", "depends_on": ["a", "datum"]}]
    assert decompose._apply_order(groups) == ["a", "b", "c"]


@pytest.mark.parametrize("backend,sfx", [("zoo", ".kcl"), ("cadquery", ".py")])
def test_decompose_run_issues_parallel_module_orders_then_integrates(monkeypatch, tmp_path: Path, backend: str, sfx: str):
    from opencad import zoo

    monkeypatch.setattr(zoo, "format_write", lambda p: None)
    monkeypatch.setattr(decompose, "measure_datum", lambda ctx, data: {"ok": True, "problems": [], "reassigned": [], "unplaceable": [], "exterior_required": False})
    monkeypatch.setattr(decompose, "compose_probe", lambda ctx, data: {"order": ["group0", "group1", "group2"], "overlaps": [{"a": "group0.removed", "b": "group1.added", "volume": 12.5}],
                                                                        "steps": [{"step": 0, "module": "datum", "ok": True, "valid": True, "solids": 1, "volume": 9600.0, "counts": {}, "failing": []},
                                                                                  {"step": 1, "module": "group0", "ok": True, "valid": True, "solids": 1, "volume": 9500.0, "counts": {"sections": "0/1"}, "failing": ["sections/mid_z"], "newly_failing": ["sections/mid_z"], "newly_passing": [], "added_volume": 0.0, "removed_volume": 100.0}]})
    monkeypatch.setenv("OPENCAD_BACKEND", backend)  # as `--backend` does: work orders record the selected backend
    stub = STUBS[backend]
    ctx = _ctx(tmp_path, backend)
    with pytest.raises(worker.WorkerPending) as ei:
        decompose.run(ctx)
    part = ei.value.order
    assert part.role == "partition" and "partition.yaml" in part.brief_path.read_text() and (ctx.part_dir / f"params{sfx}") in part.deliverables
    data = _full_partition(ctx, 3)
    _done(part, {decompose.work_dir(ctx) / decompose.PARTITION_FILE: yaml.safe_dump(data), ctx.part_dir / f"params{sfx}": stub["params"], ctx.part_dir / f"datum{sfx}": stub["datum"]})
    with pytest.raises(worker.WorkerPending) as ei2:
        decompose.run(ctx)
    mods = ei2.value.orders
    assert [o.role for o in mods] == ["module"] * 3 and sorted(o.key for o in mods) == ["module-group0", "module-group1", "module-group2"]
    assert all((decompose.work_dir(ctx) / o.key.split("-", 1)[1] / "contract.yaml").exists() for o in mods)
    assert "group0" in mods[1].brief_path.read_text() and "depends_on" in mods[1].brief_path.read_text()
    assert [o.deliverables for o in mods] == [[ctx.part_dir / f"group{i}{sfx}"] for i in range(3)]
    # the module critic target is pre-written: datum + transitive dependencies + the module, in application order
    scratch2 = (decompose.work_dir(ctx) / "group2" / ctx.backend.language.entry).read_text()
    assert ("|> group0()\n  |> group1()\n  |> group2()" in scratch2) if backend == "zoo" else ("result = apply_group2(apply_group1(apply_group0(datum)))" in scratch2)
    for o in mods:
        _done(o, {ctx.part_dir / f"{o.key.split('-', 1)[1]}{sfx}": stub["module"]})
    with pytest.raises(worker.WorkerPending) as ei3:
        decompose.run(ctx)
    integ = ei3.value.order
    brief = integ.brief_path.read_text()
    assert integ.role == "integrate" and integ.model == worker.profile("integrate").model and "group0 -> group1 -> group2" in brief
    assert "Composition probe" in brief and "breaks ['sections/mid_z']" in brief and "group0.removed x group1.added: 12.5 mm3" in brief
    assert ("kcl-bisect" in brief) if backend == "zoo" else ("engine --backend cadquery -- analyze" in brief and "kcl" not in brief.lower())
    assert integ.deliverables == [ctx.part_dir / f"main{sfx}"]
    _done(integ, {ctx.entry: stub["main"]})
    result = decompose.run(ctx)
    assert result["ok"] and result["decomposed"] and result["groups"] == ["group0", "group1", "group2"] and result["thread_id"] == f"agent-{integ.id}"
    mdl = ctx.load_stage("model")
    assert mdl["ok"] and set(mdl["modules_ok"]) == {"group0", "group1", "group2"} and f"params{sfx}" in mdl["files"] and mdl["kcl"] == str(ctx.part_dir / f"main{sfx}")


def test_zoo_engine_runs_a_parent_import_from_a_flat_staged_project(monkeypatch, tmp_path: Path):
    """KCL refuses `import x from "../..."`: a decompose scratch main runs from a temporary copy of the part's sources."""
    import subprocess

    from opencad.backends.zoo import engine as zoo_engine

    ctx = _ctx_with_hole(tmp_path)
    (ctx.part_dir / "params.kcl").write_text("export width = 60mm\n")
    (ctx.part_dir / "holes.kcl").write_text('import width from "params.kcl"\nexport fn holes(@body) { return body }\n')
    scratch = decompose.work_dir(ctx) / "holes"
    scratch.mkdir(parents=True)
    entry = scratch / "main.kcl"
    entry.write_text(decompose.scratch_main(ctx, ["holes"], scratch))
    seen: dict[str, object] = {}

    def fake_run(argv, **kw):
        target = Path(argv[-2])
        seen.update(target=target, text=target.read_text(), files=sorted(p.name for p in target.parent.iterdir()))
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setenv("OPENCAD_ZOO_LOCK", str(tmp_path / "zoo.lock"))
    monkeypatch.setattr(zoo_engine, "zoo_bin", lambda: "zoo")
    monkeypatch.setattr(zoo_engine.subprocess, "run", fake_run)
    assert zoo_engine.run(["kcl", "export", "--output-format", "step", str(entry), str(tmp_path / "out")], engine=True).ok
    assert seen["target"].parent != scratch and not seen["target"].exists(), "the staged project is temporary"
    assert 'import datum from "datum.kcl"' in seen["text"] and 'import holes from "holes.kcl"' in seen["text"] and ".." not in seen["text"]
    assert {"datum.kcl", "holes.kcl", "params.kcl", "main.kcl"} <= set(seen["files"])
    assert "../" in entry.read_text(), "the scratch main on disk is unchanged"
    plain = tmp_path / "plain.kcl"
    plain.write_text('import width from "params.kcl"\n')
    with zoo_engine.staged_entry(plain) as same:
        assert same == plain


def test_a_timed_out_integrate_turn_is_measured_and_restores_its_checkpoint(monkeypatch, tmp_path: Path):
    """The integrate turn killed at its budget leaves the entry mid-edit: the last executing checkpoint goes back and the stage is ok."""
    from opencad.stages import model

    monkeypatch.setenv("OPENCAD_BACKEND", "zoo")
    ctx = _ctx(tmp_path, "zoo")
    ctx.part_dir.mkdir(parents=True)
    for name, text in (("params", "export width = 60mm\n"), ("datum", "export datum = 1\n"), ("group0", "export fn group0(@body) { return body }\n")):
        (ctx.part_dir / f"{name}.kcl").write_text(text)
    wd = decompose.work_dir(ctx)

    def fake_dispatch(brief, *, role, run_dir, **kw):
        if role == "partition":
            (wd / decompose.PARTITION_FILE).write_text(yaml.safe_dump(_full_partition(ctx, 1)))
        if role == "integrate":
            cp = decompose.integrate_checkpoint(ctx)
            cp.mkdir(parents=True)
            (cp / "main.kcl").write_text("// executing\n")
            (cp / "group0.kcl").write_text("export fn group0(@body) { return body }\n")
            ctx.entry.write_text("// mid-edit\n")
            (ctx.part_dir / "group0.kcl").write_text("// mid-edit\n")
            return WorkerResult("t-int", 124, 2700, 9, {}, Path(run_dir), "", failure="exit 124")
        return WorkerResult(f"t-{role}", 0, 1, 1, {}, Path(run_dir), "")

    monkeypatch.setattr(decompose.worker, "dispatch", fake_dispatch)
    monkeypatch.setattr(decompose.worker, "dispatch_many", lambda specs: [fake_dispatch(**s) for s in specs])
    monkeypatch.setattr(decompose, "validate_partition", lambda ctx, data: [])
    monkeypatch.setattr(decompose, "measure_datum", lambda ctx, data: {"ok": True, "problems": []})
    monkeypatch.setattr(decompose, "compose_probe", lambda ctx, data: {"steps": [], "overlaps": []})
    monkeypatch.setattr(model, "_builds", lambda ctx, entry: "mid-edit" not in Path(entry).read_text())
    monkeypatch.setattr(ctx.backend.language, "format_write", lambda p: None)
    result = decompose.run(ctx)
    assert result["ok"] and result["timed_out"] and result["restored_checkpoint"]
    assert ctx.entry.read_text() == "// executing\n" and "mid-edit" not in (ctx.part_dir / "group0.kcl").read_text()
    assert (wd / "integrate" / "timed-out" / "main.kcl").read_text() == "// mid-edit\n"
    killed = WorkerResult("t", 124, 1, 1, {}, tmp_path, "", failure="exit 124")
    assert model.turn_ok(killed, True) and not model.turn_ok(killed, False)
    assert not model.turn_ok(WorkerResult("t", 1, 1, 1, {}, tmp_path, "", failure="crash"), True)


def test_size_trigger_and_flags(tmp_path: Path):
    ctx = _ctx(tmp_path)
    assert not decompose.should_decompose(ctx, None)
    assert decompose.should_decompose(ctx, True) and not decompose.should_decompose(ctx, False)
    local = _ctx(tmp_path / "local", "cadquery")
    # local backends decompose on request and on the same size knobs as Zoo; `--no-decompose` wins everywhere
    assert decompose.should_decompose(local, True) and not decompose.should_decompose(local, False) and not decompose.should_decompose(local, None)
    import pytest as _pytest

    mp = _pytest.MonkeyPatch()
    mp.setattr(decompose, "SIZE_TRIGGER_PARAMS", len(ctx.contract.parameters))
    try:
        assert decompose.should_decompose(ctx, None) and decompose.should_decompose(local, None)
        assert not decompose.should_decompose(local, False)
    finally:
        mp.undo()
    assert not decompose.should_decompose(local, None)


def test_local_briefs_describe_python_modules(tmp_path: Path):
    ctx = _ctx(tmp_path, "cadquery")
    data = _full_partition(ctx, 2)
    kcl_words = ("params.kcl", "datum.kcl", ".kcl", "kcl-bisect", "zoo kcl", "@settings", "export fn")
    part = decompose.partition_brief(ctx, "")
    assert str(ctx.part_dir / "params.py") in part and str(ctx.part_dir / "datum.py") in part and str(ctx.results_dir / "blockout" / "main.py") in part
    assert "top-level float" in part and "from params import" in part and "cq.Workplane" in part
    scratch = decompose.work_dir(ctx) / "group1"
    sub = decompose.write_subcontract(ctx, data["groups"][1], scratch / "contract.yaml")
    mod = decompose.module_brief(ctx, data["groups"][1], sub, scratch, data)
    assert str(ctx.part_dir / "group1.py") in mod and "def apply(body)" in mod and "from params import" in mod and str(ctx.part_dir / "group0.py") in mod
    assert f"quick {scratch / 'main.py'} --contract {sub} --backend cadquery" in mod and "engine --backend cadquery -- analyze" in mod
    assert "0.01-0.05 mm" in mod and "coincident" in mod
    integ = decompose.integrate_brief(ctx, data, {"steps": [], "aborted": "no engine", "overlaps": []})
    assert str(ctx.part_dir / "main.py") in integ and "from datum import datum" in integ and "apply_<last>(... apply_<first>(datum))" in integ
    assert "`params.py`" in integ and "`group0.py`, `group1.py`" in integ and "ruff format" in integ and "--stl" in integ
    corr = decompose.module_correction_brief(ctx, data["groups"][1], ["sections/mid_z"], "- section mid_z: area 2300 vs 2400", sub, scratch, "", data)
    assert str(ctx.part_dir / "group1.py") in corr and "def apply(body)" in corr and f"quick {scratch / 'main.py'}" in corr
    for text in (part, mod, integ, corr):
        assert not any(w in text for w in kcl_words), [w for w in kcl_words if w in text]
    for b in ("build123d", "freecad"):
        other = decompose.module_brief(_ctx(tmp_path / b, b), data["groups"][0], sub, scratch, data)
        assert "def apply(body)" in other and f"--backend {b}" in other and ".kcl" not in other
    assert "PartDesign" in decompose.recipe(_ctx(tmp_path / "fc2", "freecad"))["datum"] and "Part`/`Solid" in decompose.recipe(_ctx(tmp_path / "b2", "build123d"))["datum"]
    # the foundation files are checked under the language suffix, and a module name that would shadow the foundation is refused
    assert decompose.validate_partition(ctx, data) == [f"{ctx.part_dir / 'params.py'} missing", f"{ctx.part_dir / 'datum.py'} missing"]
    bad = _full_partition(ctx, 2)
    bad["groups"][0]["id"] = "params"
    assert any("reserved" in p for p in decompose.validate_partition(ctx, bad))


def test_scratch_mains_compose_python_for_local_backends(monkeypatch, tmp_path: Path):
    ctx = _ctx_with_hole(tmp_path, "cadquery")
    written: dict[str, str] = {}

    def fake_export(ctx_, entry: Path, out_dir: Path):
        written[Path(entry).name] = Path(entry).read_text()
        i = int(Path(entry).stem.replace("step", "")) if Path(entry).stem.startswith("step") else 0
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        return _write_step(_plate(with_hole=i >= 1, with_boss=i >= 2), Path(out_dir) / f"s{i}.step")

    monkeypatch.setattr(decompose, "export_scratch", fake_export)
    data = {"groups": [{"id": "datum", "acceptance": {"cylinders": ["centreHole"]}}, {"id": "holes", "region": {"min": [20, 10, 0], "max": [40, 30, 4]}},
                       {"id": "boss", "depends_on": ["holes"], "region": {"min": [0, 0, 4], "max": [20, 20, 10]}}]}
    dm = decompose.measure_datum(ctx, data)
    assert dm["ok"] and dm["reassigned"] == [{"item": "cylinders/centreHole", "to": "holes"}]
    assert written["main.py"] == f'import sys\n\nsys.path.insert(0, {str(ctx.part_dir)!r})\nfrom datum import datum  # noqa: E402\n\nresult = datum\n'
    probe = decompose.compose_probe(ctx, data)
    assert probe["order"] == ["holes", "boss"] and [s["module"] for s in probe["steps"]] == ["datum", "holes", "boss"] and "probes/bossVoid" in probe["steps"][2]["newly_failing"]
    assert written["step2.py"].endswith("from datum import datum  # noqa: E402\nfrom holes import apply as apply_holes  # noqa: E402\nfrom boss import apply as apply_boss  # noqa: E402\n\nresult = apply_boss(apply_holes(datum))\n")
    assert "@settings" not in written["step2.py"] and ".kcl" not in written["step2.py"]
    kcl = decompose.scratch_main(_ctx_with_hole(tmp_path / "z"), ["holes", "boss"], tmp_path / "z" / "results" / "demo" / "decompose" / "probe")
    assert 'import datum from "../../../../parts/demo/datum.kcl"' in kcl and "body = datum\n  |> holes()\n  |> boss()" in kcl and "sys.path" not in kcl


def _write_step(shape, path: Path) -> Path:
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    w.Write(str(path))
    return path


def _plate(with_hole: bool, with_boss: bool = False):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    s = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 60, 40, 4).Shape()
    if with_hole:
        s = BRepAlgoAPI_Cut(s, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(30, 20, -1), gp_Dir(0, 0, 1)), 3.0, 6).Shape()).Shape()
    if with_boss:
        s = BRepAlgoAPI_Fuse(s, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(10, 10, 4), gp_Dir(0, 0, 1)), 4.0, 6).Shape()).Shape()
    return s


def _ctx_with_hole(tmp_path: Path, backend: str = "zoo") -> Ctx:
    design = tmp_path / "designs" / "demo"
    design.mkdir(parents=True)
    raw = json.loads(template_contract().model_dump_json())
    raw["acceptance"]["cylinders"] = [{"name": "centreHole", "point": [30, 20, 2], "direction": [0, 0, 1], "kind": "hole", "radius": 3.0}]
    raw["acceptance"]["probes"] = [{"name": "bossVoid", "state": "void", "points": [[10, 10, 7]]}]
    (design / "contract.yaml").write_text(yaml.safe_dump(raw, sort_keys=False))
    c = load_contract(design / "contract.yaml")
    ctx = Ctx("demo", design, design / "contract.yaml", c, tmp_path / "results" / "demo", tmp_path / "parts" / "demo", None, backend)
    ctx.results_dir.mkdir(parents=True)
    ctx.part_dir.mkdir(parents=True)
    (ctx.part_dir / f"datum{ctx.backend.language.suffixes[0]}").write_text(STUBS.get(backend, STUBS["cadquery"])["datum"])
    return ctx


def test_measure_datum_reassigns_failing_items_by_region(monkeypatch, tmp_path: Path):
    ctx = _ctx_with_hole(tmp_path)
    monkeypatch.setattr(decompose, "export_scratch", lambda ctx, kcl, out_dir: _write_step(_plate(with_hole=False), Path(out_dir).joinpath("d.step") if Path(out_dir).mkdir(parents=True, exist_ok=True) is None else None))
    data = {"groups": [{"id": "datum", "acceptance": {"cylinders": ["centreHole"], "sections": ["mid_z"], "probes": ["bossVoid"]}},
                       {"id": "holes", "features": ["blank"], "acceptance": {}, "region": {"min": [20, 10, 0], "max": [40, 30, 4]}},
                       {"id": "far", "features": [], "acceptance": {}, "region": {"min": [50, 30, 0], "max": [60, 40, 4]}}]}
    r = decompose.measure_datum(ctx, data)
    assert r["ok"] and r["reassigned"] == [{"item": "cylinders/centreHole", "to": "holes"}]
    assert "centreHole" not in data["groups"][0]["acceptance"]["cylinders"] and data["groups"][1]["acceptance"]["cylinders"] == ["centreHole"]
    assert not r["exterior_required"] and r["problems"] == [] and "mid_z" in data["groups"][0]["acceptance"]["sections"]
    # a failing item outside every region is a partition problem, and a credits failure is a tooling outcome, not a partition verdict
    from opencad import zoo

    def boom(ctx, kcl, out_dir):
        raise zoo.ZooCreditsError("no credits")

    monkeypatch.setattr(decompose, "export_scratch", boom)
    r2 = decompose.measure_datum(ctx, data)
    assert not r2["ok"] and r2["tooling"] and "credits" in r2["error"]


def test_compose_probe_reports_breaks_and_overlaps(monkeypatch, tmp_path: Path):
    ctx = _ctx_with_hole(tmp_path)
    for g in ("holes", "boss"):
        (ctx.part_dir / f"{g}.kcl").write_text("export fn g(@body) { return body }\n")

    def fake_export(ctx_, kcl: Path, out_dir: Path):
        i = int(Path(kcl).stem.replace("step", ""))
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        return _write_step(_plate(with_hole=i >= 1, with_boss=i >= 2), Path(out_dir) / f"s{i}.step")

    monkeypatch.setattr(decompose, "export_scratch", fake_export)
    data = {"groups": [{"id": "datum", "acceptance": {}}, {"id": "holes", "region": {"min": [20, 10, 0], "max": [40, 30, 4]}}, {"id": "boss", "depends_on": ["holes"], "region": {"min": [0, 0, 4], "max": [20, 20, 10]}}]}
    probe = decompose.compose_probe(ctx, data)
    assert probe["order"] == ["holes", "boss"] and [s["module"] for s in probe["steps"]] == ["datum", "holes", "boss"]
    s1, s2 = probe["steps"][1], probe["steps"][2]
    assert "cylinders/centreHole" in s1["newly_passing"] and abs(s1["removed_volume"] - 3.1416 * 9 * 4) < 1.0 and s1["added_volume"] < 1e-6
    assert "probes/bossVoid" in s2["newly_failing"] and s2["added_volume"] > 200 and s2["removed_volume"] < 1e-6
    assert probe["overlaps"] == [] and (decompose.work_dir(ctx) / "probe.json").exists()
    text = decompose.probe_findings_text(probe)
    assert "step 2 (+boss)" in text and "breaks ['probes/bossVoid']" in text and "fixes ['cylinders/centreHole']" in text
    assert "unavailable" in decompose.probe_findings_text({"steps": [], "aborted": "credits: no credits", "overlaps": []})


def test_compose_probe_bisects_a_nondeterministic_export_to_its_module(monkeypatch, tmp_path: Path):
    """After the edit stage's restore re-export mismatched, each step is exported twice; the first step whose STEP body differs names the breaker."""
    ctx = _ctx_with_hole(tmp_path)
    for g in ("holes", "boss"):
        (ctx.part_dir / f"{g}.kcl").write_text("export fn g(@body) { return body }\n")
    calls: list[str] = []

    def fake_export(ctx_, kcl: Path, out_dir: Path):
        i = int(Path(kcl).stem.replace("step", ""))
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        calls.append(Path(out_dir).name)
        p = _write_step(_plate(with_hole=i >= 1, with_boss=i >= 2), Path(out_dir) / f"s{i}.step")
        if i >= 2 and Path(out_dir).name.endswith("-again"):  # the boss step's second export comes back with another sub-shape order
            p.write_text(p.read_text().replace("ENDSEC;", "ENDSEC;", 1) + "/* reordered */\n")
        return p

    monkeypatch.setattr(decompose, "export_scratch", fake_export)
    data = {"groups": [{"id": "datum", "acceptance": {}}, {"id": "holes", "region": {"min": [20, 10, 0], "max": [40, 30, 4]}}, {"id": "boss", "depends_on": ["holes"], "region": {"min": [0, 0, 4], "max": [20, 20, 10]}}]}
    probe = decompose.compose_probe(ctx, data)
    assert "step0-again" not in calls, "no second export while the edit stage's restore matched"
    ctx.write_stage("edit", {"ok": False, "restore": {"ok": False, "baseline_sha256": "a", "re_export_sha256": "b"}})
    calls.clear()
    probe = decompose.compose_probe(ctx, data)
    assert calls == ["step0", "step0-again", "step1", "step1-again", "step2", "step2-again"]
    assert [s.get("deterministic") for s in probe["steps"]] == [True, True, False] and probe["breakers"]["export/determinism"] == "boss"
    assert "NOT DETERMINISTIC" in decompose.probe_findings_text(probe)


def test_compose_probe_names_the_module_that_shrinks_a_passage(monkeypatch, tmp_path: Path):
    """Passages are probed per step from the STL; a module that part-fills another module's sealed air volume is its breaker."""
    from opencad.schemas import PassageSpec
    from opencad.stages import inspect_stage

    ctx = _ctx_with_hole(tmp_path)
    ctx.contract.acceptance.passages = [PassageSpec(name="duct", point_a=[1, 1, 1], point_b=[2, 2, 2], plugs=[([0, 0, 0], [1, 1, 1])])]
    for g in ("holes", "boss"):
        (ctx.part_dir / f"{g}.kcl").write_text("export fn g(@body) { return body }\n")
    stl_calls: list[int] = []

    def fake_export(ctx_, kcl: Path, out_dir: Path):
        i = int(Path(kcl).stem.replace("step", ""))
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        return _write_step(_plate(with_hole=i >= 1, with_boss=i >= 2), Path(out_dir) / f"s{i}.step")

    def fake_stl(ctx_, kcl: Path, out_dir: Path):
        stl_calls.append(int(Path(kcl).stem.replace("step", "")))
        return Path(out_dir) / "fake.stl"

    volumes = {0: 5000.0, 1: 5000.0, 2: 4000.0}  # the boss module fills 20 % of the duct
    # before the `holes` module encloses it, `open` is the whole exterior air (unsealed, failing): enclosing it is not filling it
    open_air = {0: (30000.0, False), 1: (4500.0, True), 2: (4500.0, True)}
    real_measure = inspect_stage.measure

    def fake_measure(step, stl, contract, design_dir):
        m = real_measure(step, None, contract, design_dir)
        i = int(Path(step).stem.replace("s", ""))
        m["passages"] = {"duct": {"ok": True, "passage_volume": volumes[i]}, "open": {"ok": open_air[i][1], "passage_volume": open_air[i][0]}}
        return m

    monkeypatch.setattr(decompose, "export_scratch", fake_export)
    monkeypatch.setattr(decompose, "export_scratch_stl", fake_stl)
    monkeypatch.setattr(inspect_stage, "measure", fake_measure)
    data = {"groups": [{"id": "datum", "acceptance": {}}, {"id": "holes", "acceptance": {"passages": ["duct"]}, "region": {"min": [20, 10, 0], "max": [40, 30, 4]}},
                       {"id": "boss", "depends_on": ["holes"], "region": {"min": [0, 0, 4], "max": [20, 20, 10]}}]}
    probe = decompose.compose_probe(ctx, data)
    assert stl_calls == [0, 1, 2], "an STL per step when the contract declares passages"
    s2 = probe["steps"][2]
    assert s2["passage_shrink"] == [{"passage": "duct", "before": 5000.0, "after": 4000.0, "module": "boss"}]
    assert "passage_shrink" not in probe["steps"][1] and "passages/open" not in probe["breakers"]
    assert probe["breakers"]["passages/duct"] == "boss" and probe["breakers"]["probes/bossVoid"] == "boss"
    text = decompose.probe_findings_text(probe)
    assert "fills 1000 mm3 of passage `duct`" in text and "passages/duct: `boss`" in text
    # the breaker, not the owner, gets the correction for that item (boss is applied after holes, the owner)
    assert decompose.owners(data, {"passages": ["duct"]}) == {"holes": ["passages/duct"]}
    assert decompose.owners(data, {"passages": ["duct"]}, probe["breakers"]) == {"boss": ["passages/duct"]}
    # a "breaker" applied BEFORE the owner cannot have broken an item that did not exist yet: the owner keeps it
    early = {"groups": [{"id": "datum", "acceptance": {}}, {"id": "shell", "acceptance": {}}, {"id": "ducts", "depends_on": ["shell"], "acceptance": {"passages": ["duct"]}}]}
    assert decompose.owners(early, {"passages": ["duct"]}, {"passages/duct": "shell"}) == {"ducts": ["passages/duct"]}
    # a passage renamed after the partition is unowned: the module owning every other passage takes it, not the smallest region
    assert decompose.owners(early, {"passages": ["ductRenamed"]}, None) == {"ducts": ["passages/ductRenamed"]}
    # an unowned section with no breaker is never region-guessed: its plane crosses every region
    assert decompose.owners(data, {"sections": ["mid_z"]}, None, ctx.contract) == {}
    # an item added to the contract after the partition is owned by the module whose region holds it
    from opencad.schemas import ProbeSpec

    ctx.contract.acceptance.probes = [ProbeSpec(name="lateAir", state="void", points=[[30, 20, 2]])]
    assert decompose.owners(data, {"probes": ["lateAir"]}) == {}
    assert decompose.owners(data, {"probes": ["lateAir"]}, None, ctx.contract) == {"holes": ["probes/lateAir"]}


def test_module_brief_lists_void_keepouts_of_other_groups(tmp_path: Path):
    from opencad.schemas import PassageSpec, ProbeSpec

    ctx = _ctx_with_hole(tmp_path)
    ctx.contract.acceptance.passages = [PassageSpec(name="duct", point_a=[1, 1, 1], point_b=[2, 2, 2], seal_radius=3.2, plugs=[([0, 0, 0], [1, 1, 1])])]
    ctx.contract.acceptance.probes = [ProbeSpec(name="airA", state="void", points=[[5, 5, 5]]), ProbeSpec(name="ownAir", state="void", points=[[9, 9, 9]])]
    partition = {"groups": [{"id": "ducts", "acceptance": {"passages": ["duct"], "probes": ["airA"]}, "region": {"min": [0, 0, 0], "max": [1, 1, 1]}},
                            {"id": "boss", "acceptance": {"probes": ["ownAir"]}, "region": {"min": [0, 0, 4], "max": [20, 20, 10]}}]}
    text = decompose._region_text(partition["groups"][1], partition, ctx.contract)
    assert "Keep-outs" in text and "passage `duct` (owner `ducts`)" in text and "3.2 mm closing" in text and "void probe `airA`" in text
    assert "ownAir" not in text, "a group's own air is not a keep-out for itself"
    ducts_text = decompose._region_text(partition["groups"][0], partition, ctx.contract)
    assert "void probe `ownAir` (owner `boss`)" in ducts_text and "`duct`" not in ducts_text.split("Keep-outs")[1]


def test_module_corrections_leave_integrate_level_items_alone(tmp_path: Path):
    """An item that passes with every module composed (last probe step) and fails only on the integrated entry is main.py's:
    no module order is issued for it. The probe must have been measured against the current contract and current modules."""
    from opencad.io import sha256_file

    ctx = _ctx_with_hole(tmp_path)
    for g in ("holes", "boss"):
        (ctx.part_dir / f"{g}.kcl").write_text("export fn g(@body) { return body }\n")
    wd = decompose.work_dir(ctx)
    wd.mkdir(parents=True, exist_ok=True)
    data = {"groups": [{"id": "datum", "acceptance": {}},
                       {"id": "holes", "acceptance": {"cylinders": ["centreHole"]}, "region": {"min": [20, 10, 0], "max": [40, 30, 4]}},
                       {"id": "boss", "acceptance": {}, "region": {"min": [0, 0, 4], "max": [20, 20, 10]}}]}
    (wd / "partition.json").write_text(json.dumps(data))
    ctx.write_stage("model", {"ok": True, "decomposed": True, "modules": {}})
    ctx.write_stage("inspect", {"ok": False, "cylinders": {"centreHole": {"ok": False}}})
    step = {"ok": True, "valid": True, "solids": 1, "volume": 100.0, "counts": {}, "failing": [], "newly_failing": [], "newly_passing": []}
    probe = {"steps": [{**step, "step": 0, "module": "datum"}, {**step, "step": 1, "module": "holes", "added_volume": 1.0, "removed_volume": 0.0}],
             "overlaps": [], "breakers": {}, "contract_sha": sha256_file(ctx.contract_path)}
    (wd / "probe.json").write_text(json.dumps(probe))
    assert decompose.module_corrections(ctx, "x", "correction-1") is None, "passes with all modules composed: integrate-level"
    # measured against another contract: the probe cannot vouch for the item, so ownership applies again
    probe["contract_sha"] = "0" * 64
    (wd / "probe.json").write_text(json.dumps(probe))
    with pytest.raises(worker.WorkerPending) as ei:
        decompose.module_corrections(ctx, "x", "correction-2")
    assert ei.value.order.key == "correction-2-holes"


def test_module_corrections_target_the_owning_modules(monkeypatch, tmp_path: Path):
    ctx = _ctx_with_hole(tmp_path)
    for g in ("holes", "boss"):
        (ctx.part_dir / f"{g}.kcl").write_text("export fn g(@body) { return body }\n")
    (ctx.part_dir / "params.kcl").write_text("export width = 60mm\n")
    wd = decompose.work_dir(ctx)
    wd.mkdir(parents=True, exist_ok=True)
    data = {"groups": [{"id": "datum", "acceptance": {"sections": ["mid_z"]}},
                       {"id": "holes", "features": ["blank"], "acceptance": {"cylinders": ["centreHole"]}, "region": {"min": [20, 10, 0], "max": [40, 30, 4]}},
                       {"id": "boss", "acceptance": {"probes": ["bossVoid"]}, "region": {"min": [0, 0, 4], "max": [20, 20, 10]}}]}
    (wd / "partition.json").write_text(json.dumps(data))
    ctx.write_stage("model", {"ok": True, "decomposed": True, "modules": {"holes": {"thread_id": "agent-holes"}, "boss": {}}})
    ctx.write_stage("inspect", {"ok": False, "cylinders": {"centreHole": {"ok": False}}, "probes": {"bossVoid": {"ok": True}}, "sections": {"mid_z": {"ok": False}}})
    assert decompose.owners(data, decompose.failing_items(ctx)) == {"holes": ["cylinders/centreHole"]}
    with pytest.raises(worker.WorkerPending) as ei:
        decompose.module_corrections(ctx, "- cylinder centreHole: axis offset 0.8 mm (max 0.1)\n- section mid_z: area 2300 vs 2400", "correction-1")
    o = ei.value.order
    assert o.role == "correction" and o.key == "correction-1-holes" and o.resume_of is None  # agent-holes is not a recorded agent here
    brief = o.brief_path.read_text()
    assert "holes.kcl" in brief and "axis offset 0.8" in brief and "mid_z" not in brief.split("Rules:")[0].split("Measured vs expected")[1]
    # a composed entry (datum + every module, apply order) checked against the full contract, beside the standalone scratch
    composed = wd / "holes" / "composed.kcl"
    assert composed.exists() and 'import holes from' in composed.read_text() and 'import boss from' in composed.read_text()
    assert f"quick {composed} --contract {ctx.contract_path}" in brief and "The gates measure the COMPOSED part" in brief
    # once the integrate turn wrote the entry, the composed critic is the entry itself (modules + integrate-level operations)
    ctx.kcl_target.write_text(STUBS["zoo"]["main"])
    brief2 = decompose.module_correction_brief(ctx, data["groups"][1], ["cylinders/centreHole"], "x", wd / "holes" / "contract.yaml", wd / "holes", "", data,
                                               composed=ctx.kcl_target)
    assert f"quick {ctx.kcl_target} --contract {ctx.contract_path}" in brief2 and "integrated entry the gates inspect" in brief2
    ctx.kcl_target.unlink()
    _done(o)
    # the worker declines the item: it is recorded and never re-issued to this module
    o.result_path.write_text("## Result\nnot mine\n## Files changed\n-\n## Verification\n-\n## Open questions\n-\n"
                             "## Not this module\n- cylinders/centreHole: main.kcl `_restock` cuts it after this module\n")
    mc = decompose.module_corrections(ctx, "x", "correction-1")
    assert mc and set(mc["modules"]) == {"holes"} and mc["items"] == {"holes": ["cylinders/centreHole"]}
    assert decompose.load_declined(ctx) == {"holes": {"cylinders/centreHole": "main.kcl `_restock` cuts it after this module"}}
    assert decompose.module_corrections(ctx, "x", "correction-2") is None, "the only failing item was declined by its only owner"
    ctx.write_stage("model", {"ok": True, "decomposed": False})
    assert decompose.module_corrections(ctx, "x", "correction-3") is None


def test_unowned_face_goes_to_the_module_owning_its_plane():
    """A summed whole-plane face added after the partition has no owner and no point: the module holding the other faces on x=26.5 takes it."""
    from opencad.schemas import FaceSpec

    class C:
        class acceptance:
            faces = [FaceSpec(name="frontPanel", plane="x", at=26.5, normal="+", area=64.9), FaceSpec(name="backPanel", plane="x", at=26.5, normal="+", area=41.9),
                     FaceSpec(name="sideTotal", plane="x", at=26.5, normal="+", area=106.8, mode="sum"), FaceSpec(name="lid", plane="z", at=10.0, normal="+", area=5.0),
                     FaceSpec(name="lidTotal", plane="z", at=10.0, normal="+", area=9.0, mode="sum")]

    data = {"groups": [{"id": "datum", "acceptance": {}}, {"id": "clamp", "acceptance": {"faces": ["frontPanel", "backPanel"]}},
                       {"id": "exterior", "acceptance": {"faces": ["lid"]}}, {"id": "keyhole", "acceptance": {"faces": ["lidTotal"]}}]}
    assert decompose.owners(data, {"faces": ["sideTotal"]}, None, C) == {"clamp": ["faces/sideTotal"]}
    # two modules own faces on z=10: no single plane owner, and with no region the item stays integrate-level
    data["groups"][3]["acceptance"]["faces"] = ["other"]
    C.acceptance.faces.append(FaceSpec(name="other", plane="z", at=10.0, normal="+", area=1.0))
    assert decompose.owners(data, {"faces": ["lidTotal"]}, None, C) == {}


def test_thickness_item_goes_to_every_module_holding_a_thin_cluster():
    """Thin skins sit on module boundaries: the wall item is issued to each module whose region holds a thin-skin cluster centre."""
    data = {"groups": [{"id": "datum", "acceptance": {}}, {"id": "fasteners", "acceptance": {"thickness": ["wall"]}, "region": {"min": [-20, -10, 50], "max": [20, 0, 62]}},
                       {"id": "leftDuct", "acceptance": {}, "region": {"min": [-36, -28, 2], "max": [-13, 0, 62]}}, {"id": "exterior", "acceptance": {}}]}
    spots = {"thickness/wall": [[6.0, -2.4, 54.0], [-27.8, -14.0, 36.0], [80.0, 80.0, 80.0]]}  # the last one is in no region
    assert decompose.owners(data, {"thickness": ["wall"]}, None, None, spots) == {"fasteners": ["thickness/wall"], "leftDuct": ["thickness/wall"]}
    # the probe's breaker joins the holders (a boundary skin has two sides), and without cluster evidence the partition owner keeps it
    only_left = {"thickness/wall": [[-27.8, -14.0, 36.0]]}
    assert decompose.owners(data, {"thickness": ["wall"]}, {"thickness/wall": "exterior"}, None, only_left) == {"exterior": ["thickness/wall"], "leftDuct": ["thickness/wall"]}
    assert decompose.owners(data, {"thickness": ["wall"]}, None, None, {}) == {"fasteners": ["thickness/wall"]}


def test_declines_naming_an_owner_hand_the_item_to_that_module():
    """`- sections/midPlate: owned by `sideClamp` ...` from the fasteners worker routes midPlate to sideClamp next round."""
    declined = {"fasteners": {"sections/midPlate": "owned by `sideClamp`: the 12th loop is the clamp's crescent", "sections/other": "not ours, unclear who"},
                "exterior": {"planes/rightUpperBevel": "owner sideClamp - the relief bite sets it"}}
    assert decompose.handoffs(declined, {"sideClamp", "exterior", "fasteners"}) == {"sections/midPlate": "sideClamp", "planes/rightUpperBevel": "sideClamp"}
    assert decompose.handoffs({"a": {"x/y": "owner nobody"}}, {"a", "b"}) == {}
    # the phrasings the FreeCAD Prusa workers used: "<module> owns ...", and a reason opening with the module name
    natural = {"fasteners": {"sections/midPlate": "clamp owns the second loop at [25.17, 7, -6]..[26.50, 7, 0]; keyhole owns the filament hole",
                             "sections/pivotDepthSection": "clamp/exterior own the -63 mm2 (x > 21)"},
               "exterior": {"faces/rightSideFrontPanel": "clamp — the 67.94 mm2 front +x patch is y=11.93..14",
                            "faces/topRightLedge": "keyhole / fasteners — standalone z=28 right shelf is 92.23",
                            "faces/other": "the 4.7 mm2 leftover sits in x>21 (module unclear)"}}
    assert decompose.handoffs(natural, {"clamp", "keyhole", "fasteners", "exterior"}) == {
        "sections/midPlate": "clamp", "sections/pivotDepthSection": "clamp", "faces/rightSideFrontPanel": "clamp", "faces/topRightLedge": "keyhole"}

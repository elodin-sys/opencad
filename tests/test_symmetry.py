"""Mirror-plane deviation, features-gate evidence, and contract wiring."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import trimesh
import yaml

from opencad import gates
from opencad.contract import lint_contract
from opencad.geomcheck.mesh import mirror_deviation
from opencad.paths import DESIGNS, TEMPLATE
from opencad.schemas import PartContract
from tests.test_gates import make_ctx


def _box_stl(path: Path, extents=(20.0, 20.0, 10.0), bump_y: float = 0.0) -> Path:
    m = trimesh.creation.box(extents=extents)
    if bump_y:
        v = np.asarray(m.vertices, float)
        v[v[:, 1] > extents[1] / 2 - 1e-6, 1] += bump_y
        m = trimesh.Trimesh(v, m.faces, process=True)
    m.export(path)
    return path


def test_mirror_deviation_symmetric_box_is_near_zero(tmp_path):
    stl = _box_stl(tmp_path / "box.stl")
    r = mirror_deviation(stl, "y", 0.0, samples=4000)
    assert r["max"] < 0.05 and r["p95"] < 0.02
    assert r["worst_point"] is not None


def test_mirror_deviation_one_sided_bump_reports_height(tmp_path):
    stl = _box_stl(tmp_path / "bump.stl", bump_y=3.0)
    r = mirror_deviation(stl, "y", 0.0, samples=8000)
    assert r["max"] == pytest.approx(3.0, abs=0.15)
    assert r["worst_point"][1] > 0
    assert r["n_exceed"] > 0


def test_features_fails_on_symmetry_line(tmp_path):
    ctx = make_ctx(tmp_path)
    ins = json.loads(ctx.stage_file("inspect").read_text())
    ins["symmetry"] = {
        "mirrorY": {
            "ok": False,
            "max": 3.427,
            "p95": 0.140,
            "worst_point": [17.6, 7.2, 3.6],
            "max_deviation": 0.1,
            "p95_deviation": 0.05,
        }
    }
    ctx.stage_file("inspect").write_text(json.dumps(ins))
    fb = gates.evaluate(ctx)
    by_id = {g["id"]: g for g in fb["gates"]}
    assert by_id["features"]["ok"] is False
    assert by_id["features"]["details"]["symmetry_failed"] == ["mirrorY"]
    assert any(
        "symmetry mirrorY: max 3.427 mm at (17.6, 7.2, 3.6), p95 0.140 (tol 0.1 / 0.05)" in e
        for e in by_id["features"]["evidence"]
    )
    msg = gates.correction_message(ctx, fb)
    assert "symmetry mirrorY" in msg and "3.427" in msg


def test_features_ignores_missing_symmetry_key(tmp_path):
    ctx = make_ctx(tmp_path)
    ins = json.loads(ctx.stage_file("inspect").read_text())
    assert "symmetry" not in ins
    fb = gates.evaluate(ctx)
    by_id = {g["id"]: g for g in fb["gates"]}
    assert by_id["features"]["ok"] is True
    assert by_id["features"]["details"]["symmetry_failed"] == []


def test_symmetry_names_are_valid_interface_checks():
    d = yaml.safe_load((TEMPLATE / "contract.yaml").read_text())
    d["acceptance"]["symmetry"] = [
        {"name": "mirrorY", "plane": "y", "at": 0, "max_deviation": 0.1, "p95_deviation": 0.05}
    ]
    d.setdefault("interfaces", [])
    d["interfaces"].append({"name": "sym", "description": "mirror plane", "checks": ["mirrorY"]})
    c = PartContract.model_validate(d)
    assert "mirrorY" in c.interface_checks()


def test_duplicate_symmetry_names_rejected():
    d = yaml.safe_load((TEMPLATE / "contract.yaml").read_text())
    d["acceptance"]["symmetry"] = [{"name": "m", "plane": "y"}, {"name": "m", "plane": "x"}]
    with pytest.raises(Exception, match="duplicate"):
        PartContract.model_validate(d)


def test_unknown_symmetry_interface_check_rejected():
    d = yaml.safe_load((TEMPLATE / "contract.yaml").read_text())
    d.setdefault("interfaces", [])
    d["interfaces"].append({"name": "sym", "description": "mirror", "checks": ["mirrorY"]})
    with pytest.raises(Exception, match="unknown acceptance item"):
        PartContract.model_validate(d)


def test_inspection_items_can_list_passing_checks():
    raw = yaml.safe_load((TEMPLATE / "contract.yaml").read_text())
    contract = PartContract.model_validate(raw)
    ins = {
        "sections": {"mid": {"ok": True, "plane": "z", "at": 1.0}},
        "faces": {
            "top": {"ok": False, "plane": "z", "at": 4, "normal": "+", "found": 0, "area": 0, "area_expected": 10}
        },
    }
    failed = gates.inspection_items(ins, contract)
    assert any("named face top" in line for _, line in failed) and not any("section mid" in line for _, line in failed)
    everything = gates.inspection_items(ins, contract, only_failed=False)
    assert any("section mid" in line and "OK" in line for _, line in everything)


def test_symmetry_uses_a_fine_step_tessellation_not_the_stl(tmp_path: Path):
    from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    from opencad.stages.inspect_stage import measure

    shape = BRepPrimAPI_MakeCone(8.0, 4.0, 20.0).Shape()
    fillet = BRepFilletAPI_MakeFillet(shape)
    found = TopExp_Explorer(shape, TopAbs_EDGE)
    fillet.Add(0.4, TopoDS.Edge_s(found.Current()))
    fillet.Build()
    if fillet.IsDone():
        shape = fillet.Shape()
    step = tmp_path / "cone.step"
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    assert writer.Write(str(step)) == IFSelect_RetDone
    trimesh.creation.box(extents=(40, 8, 8)).apply_translation((30, 0, 0)).export(tmp_path / "bad.stl")
    raw = yaml.safe_load((TEMPLATE / "contract.yaml").read_text())
    raw["acceptance"]["symmetry"] = [
        {"name": "mirrorX", "plane": "x", "at": 0, "max_deviation": 0.1, "p95_deviation": 0.05}
    ]
    row = measure(step, tmp_path / "bad.stl", PartContract.model_validate(raw), tmp_path)["symmetry"]["mirrorX"]
    assert row["source"] == "fine STEP tessellation" and row["p95"] <= 0.01


def test_quick_samples_less_than_the_gate_and_renders_views_only_on_request(tmp_path: Path, monkeypatch):
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    from opencad import quick, render
    from opencad.geomcheck import mesh
    from opencad.stages.inspect_stage import measure

    step = tmp_path / "box.step"
    writer = STEPControl_Writer()
    writer.Transfer(BRepPrimAPI_MakeBox(60.0, 40.0, 4.0).Shape(), STEPControl_AsIs)
    assert writer.Write(str(step)) == IFSelect_RetDone
    raw = yaml.safe_load((TEMPLATE / "contract.yaml").read_text())
    raw["acceptance"]["symmetry"] = [{"name": "mirrorX", "plane": "x", "at": 30}]
    contract = tmp_path / "contract.yaml"
    contract.write_text(yaml.safe_dump(raw))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    samples: list[int] = []
    real = mesh.mirror_deviation

    def spy(*args, **kwargs):
        samples.append(kwargs["samples"])
        return real(*args, **kwargs)

    monkeypatch.setattr(mesh, "mirror_deviation", spy)
    angles: list[tuple[str, ...]] = []
    monkeypatch.setattr(render, "render_snapshots", lambda src, dest, views, **kw: angles.append(tuple(views)) or {})
    quick.run(step, contract, ledger=tmp_path / "ledger.jsonl")
    assert samples == [quick.SYMMETRY_SAMPLES] and angles == []
    quick.run(step, contract, with_stl=True, ledger=tmp_path / "ledger.jsonl")
    assert angles == [render.DEFAULT_VIEWS]
    measure(step, None, PartContract.model_validate(raw), tmp_path)
    assert samples[-1] == 60000


def test_step_tessellation_reuses_the_cached_stl(tmp_path: Path, monkeypatch):
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    from opencad.backends import local
    from opencad.geomcheck import mesh

    step = tmp_path / "box.step"
    writer = STEPControl_Writer()
    writer.Transfer(BRepPrimAPI_MakeBox(10.0, 8.0, 6.0).Shape(), STEPControl_AsIs)
    assert writer.Write(str(step)) == IFSelect_RetDone
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    calls = {"n": 0}
    real = local.write_stl

    def wrapped(*args, **kwargs):
        calls["n"] += 1
        return real(*args, **kwargs)

    monkeypatch.setattr(local, "write_stl", wrapped)
    first = mesh.step_tessellation(step)
    second = mesh.step_tessellation(step)
    assert calls["n"] == 1
    assert len(first.vertices) > 0 and len(second.vertices) > 0
    assert list((tmp_path / ".cache" / "opencad" / "tess").glob("*.stl"))


def test_mirror_prose_without_symmetry_spec_warns():
    raw = yaml.safe_load((DESIGNS / "_template" / "contract.yaml").read_text())
    raw["frame"]["datums"] = [{"name": "centre", "description": "mirror plane y=0"}]
    _, warnings = lint_contract(PartContract.model_validate(raw))
    assert any("acceptance.symmetry" in w for w in warnings)
    raw["acceptance"]["symmetry"] = [{"name": "mirrorY", "plane": "y"}]
    _, warnings2 = lint_contract(PartContract.model_validate(raw))
    assert not any("acceptance.symmetry" in w for w in warnings2)

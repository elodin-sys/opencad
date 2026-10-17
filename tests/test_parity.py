"""`truth parity`: the truth manifest's observables against the worker-visible contract, plus scorecard-PASS/gates-FAIL cells."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from opencad.contract import template_contract
from opencad.schemas import CylinderSpec, PassageSpec, Section, SectionExpect, ThicknessSpec
from opencad.truth import parity
from opencad.truth.manifest import CaseManifest


def _manifest() -> CaseManifest:
    raw = {
        "id": "duct",
        "title": "duct",
        "truth_class": "B",
        "role": "validation",
        "source": {"citation": "test", "urls": [], "accessed": "2026-09-20", "revision": "1", "license": "test"},
        "intent": "demo",
        "inputs": [{"path": "inputs/a.md", "kind": "text", "sha256": "0" * 64}],
        "truth": [{"path": "truth/ref.stl", "kind": "mesh", "sha256": "0" * 64}],
        "arms": [{"id": "a", "design": "duct", "inputs": ["inputs/a.md"]}],
        "observables": [
            {
                "id": "passage_left",
                "kind": "passage",
                "point": [-21, -14, 50],
                "point_b": [-26, -10, 10],
                "pitch": 0.4,
                "seal_radius": 3.2,
                "volume_min": 3400,
                "volume_max": 5200,
            },
            {
                "id": "passage_cavity",
                "kind": "passage",
                "point": [0, -18, 26],
                "point_b": [10, -18, 30],
                "pitch": 0.4,
                "seal_radius": 3.2,
            },
            {
                "id": "section_z45",
                "kind": "section",
                "plane": "z",
                "at": 45.0,
                "expected": {"area": 566.0},
                "area_tolerance_rel": 0.08,
            },
            {"id": "wall_min", "kind": "thickness", "stat": "p05", "min": 0.75, "max_thickness": 8.0},
            {
                "id": "hole_a",
                "kind": "cylinder",
                "point": [-7, -4, 59],
                "direction": [0, 0, 1],
                "radius": 2.5,
                "cyl_kind": "hole",
                "radius_tolerance": 0.1,
            },
            {"id": "dev", "kind": "deviation", "required": False, "reference": "truth/ref.stl", "p95_max": 1.0},
        ],
    }
    return CaseManifest.model_validate(raw)


def _contract():
    c = template_contract()
    plugs = [([-28, -25, 61], [-8, -13, 62])]
    c.acceptance.passages = [
        PassageSpec(name="leftBranch", point_a=[-15, -19, 60], point_b=[-22, -8, 7.5], pitch=0.25, plugs=plugs)
    ]
    c.acceptance.sections = [
        Section(id="sec_z45", plane="z", at=45.0, expect=SectionExpect(area=566.0, area_tolerance_rel=0.3))
    ]
    c.acceptance.thickness = [ThicknessSpec(name="wall", min=0.75, stat="p05", samples=12000)]
    c.acceptance.cylinders = [
        CylinderSpec(
            name="topBore", point=[-7, -4, 0], direction=[0, 0, 1], radius=2.5, kind="hole", radius_tolerance=0.15
        )
    ]
    return c


def test_audit_reports_missing_looser_and_parameter_differences():
    findings = {f["observable"]: f for f in parity.audit(_manifest(), _contract())}
    left = findings["passage_left"]
    # plugs the scorer never paints and a missing volume band make the contract LOOSER than the truth, not merely different
    assert left["status"] == "looser" and left["counterpart"] == "leftBranch"
    assert "plugs 1 ports the truth leaves to the closing radius" in left["detail"] and "unbanded" in left["detail"] and "drift" in left["detail"]
    assert findings["passage_cavity"]["status"] == "missing"
    assert (
        findings["section_z45"]["status"] == "looser"
        and "30% looser than truth 8%" in findings["section_z45"]["detail"]
    )
    assert findings["wall_min"]["status"] == "params" and "max_thickness" in findings["wall_min"]["detail"]
    assert findings["hole_a"]["status"] == "looser" and "radius tolerance 0.15" in findings["hole_a"]["detail"]
    assert findings["dev"]["status"] == "info" and "scorer-only" in findings["dev"]["detail"]


def test_summed_face_with_a_narrower_plane_window_is_looser():
    """A summed face's plane window is part of its band: the gate must sum every sliver the scorer sums (Prusa back_mating_face, 2231.74 vs 2229.50)."""
    from opencad.schemas import FaceSpec

    m = _manifest()
    m.observables.append(m.observables[0].model_copy(update={"id": "back_face", "kind": "face", "plane": "y", "at": 0.0, "normal": "-", "mode": "sum",
                                                             "expected": 2166.0, "area_tolerance_rel": 0.03, "tolerance": 0.05}))
    c = _contract()
    c.acceptance.faces = [FaceSpec(name="backDatum", plane="y", at=0.0, normal="-", area=2166.0, area_tolerance_rel=0.03, tolerance=0.03, mode="sum")]
    f = {x["observable"]: x for x in parity.audit(m, c)}["back_face"]
    assert f["status"] == "looser" and "plane window 0.03 mm narrower than truth 0.05" in f["detail"]
    c.acceptance.faces[0].tolerance = 0.05
    assert {x["observable"]: x for x in parity.audit(m, c)}["back_face"]["status"] == "ok"


def test_reference_integrity_classifies_endpoints_and_probes_on_the_brep(tmp_path: Path):
    """A truth passage whose endpoint is inside the reference material is a truth defect; the audit names it and the
    contract items that copied it, and reports the reference mesh's voxel fill health."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    from opencad.schemas import ProbeSpec
    from opencad.truth.mutants import write_step, write_stl

    box = BRepPrimAPI_MakeBox(40, 40, 40).Shape()
    bore = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(20, 20, -1), gp_Dir(0, 0, 1)), 4, 42).Shape()
    shape = BRepAlgoAPI_Cut(box, bore).Shape()
    root = tmp_path / "case"
    (root / "truth").mkdir(parents=True)
    write_step(shape, root / "truth" / "ref.step")
    write_stl(shape, root / "truth" / "ref.stl")
    raw = _manifest().model_dump(by_alias=True, exclude_none=True)
    raw["truth"] = [
        {"path": "truth/ref.step", "kind": "cad", "sha256": "0" * 64},
        {"path": "truth/ref.stl", "kind": "mesh", "sha256": "0" * 64},
    ]
    raw["observables"] = [
        {
            "id": "bore_air",
            "kind": "passage",
            "point": [20, 20, 5],
            "point_b": [20, 20, 35],
            "pitch": 1.0,
            "plugs": [[[15, 15, -1], [25, 25, 1]], [[15, 15, 39], [25, 25, 41]]],
        },
        {
            "id": "fake_cavity",
            "kind": "passage",
            "point": [5, 5, 5],
            "point_b": [20, 20, 35],
            "pitch": 1.0,
            "seal_radius": 2.0,
        },
        {"id": "wall_void", "kind": "probe", "state": "void", "points": [[5, 5, 5], [20, 20, 20]]},
    ]
    m = CaseManifest.model_validate(raw)
    c = _contract()
    c.acceptance.passages = [
        PassageSpec(name="fakeChamber", point_a=[5, 5, 5], point_b=[35, 35, 35], pitch=1.0, seal_radius=2.0)
    ]
    c.acceptance.probes = [
        ProbeSpec(name="chamberAir", state="void", points=[[5, 5, 5], [20, 20, 20]]),
        ProbeSpec(name="body", state="solid", points=[[5, 5, 5]]),
    ]
    integ = parity.reference_integrity(m, root, c)
    assert integ["mesh"]["fill_ratio"] > 0.9 and not integ["mesh"]["leak"]
    invalid = {r["observable"]: r["detail"] for r in integ["invalid"]}
    assert (
        set(invalid) == {"fake_cavity", "wall_void"}
        and "['in', 'out']" in invalid["fake_cavity"]
        and "1/2 void probe points" in invalid["wall_void"]
    )
    items = {r["item"]: r["detail"] for r in integ["contract_disagreements"]}
    assert {"passages/fakeChamber", "probes/chamberAir"} <= set(items)
    # the worker's critic run on the reference: items the reference itself fails are contract defects (here the template's
    # section and bore, which the box does not have) - the fake chamber passage shows up there too
    assert "passages/fakeChamber" in integ["reference_fails"] and "sections/sec_z45" in integ["reference_fails"]
    assert all(items[i].startswith("the reference itself fails") for i in integ["reference_fails"])
    report = parity.write_report("duct", {"duct": []}, [], out=tmp_path / "parity.md", integrity={"duct": integ})
    text = report.read_text()
    assert "## Reference integrity (duct)" in text and "**fake_cavity**" in text and "**probes/chamberAir**" in text


def test_gate_scorecard_mismatches_and_report(tmp_path: Path, monkeypatch):
    cases = tmp_path / "truth" / "cases"
    (cases / "duct" / "scorecards").mkdir(parents=True)
    card = {"verdict": "PASS", "pipeline_gates": {"ok": False, "failed": ["features", "edit_robustness"]}}
    (cases / "duct" / "scorecards" / "arm@zoo-latest.json").write_text(json.dumps(card))
    (cases / "duct" / "scorecards" / "arm@cadquery-latest.json").write_text(
        json.dumps({"verdict": "PASS", "pipeline_gates": {"ok": True, "failed": []}})
    )
    (cases / "duct" / "manifest.yaml").write_text(
        yaml.safe_dump(_manifest().model_dump(by_alias=True, exclude_none=True))
    )
    monkeypatch.setattr(parity, "TRUTH", tmp_path / "truth")
    monkeypatch.setattr(parity, "case_dir", lambda cid: cases / cid)
    rows = parity.gate_scorecard_mismatches("duct")
    assert rows == [
        {
            "case": "duct",
            "arm": "arm",
            "backend": "zoo",
            "failed_gates": ["features", "edit_robustness"],
            "scorecard": str(cases / "duct" / "scorecards" / "arm@zoo-latest.json"),
        }
    ]
    out = parity.write_report(
        "duct", {"duct": parity.audit(_manifest(), _contract())}, rows, out=tmp_path / "parity.md"
    )
    text = out.read_text()
    assert (
        "| passage_cavity | passage | yes | **missing** |" in text
        and "| duct | arm | zoo | features, edit_robustness |" in text
    )
    assert "Never hand this file to a worker" in text

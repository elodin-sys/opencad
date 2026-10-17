"""Contract-side cylinder / plane / dimension checks and the discriminating provenance gate."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeWedge
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

from opencad.geomcheck import brep, features
from opencad.orchestrator import Ctx
from opencad.paths import DESIGNS
from opencad.schemas import FaceSpec, PartContract
from opencad import gates

BASE = yaml.safe_load((DESIGNS / "_template" / "contract.yaml").read_text())


def _contract(**acceptance_extra) -> PartContract:
    data = yaml.safe_load(yaml.safe_dump(BASE))
    data["name"] = "geo-test"
    data["envelope"] = {"min": [0, 0, 0], "max": [40, 30, 15], "tolerance": 0.05}
    data["parameters"] = [{"name": "plateWidth", "value": 40, "unit": "mm", "provenance": "stated", "tolerance": 0.01, "source": "sources/spec.md"}]
    data["features"] = [{"id": "hole", "kind": "hole", "description": "through hole", "verify": [{"method": "cylinder", "cylinder": "h1"}]}]
    data["interfaces"] = [{"name": "mount", "description": "hole and top face", "checks": ["h1", "top"]}]
    data["acceptance"] = {"solid_count": 1, "faces": [{"name": "top", "plane": "z", "at": 10, "normal": "+"}, {"name": "bottom", "plane": "z", "at": 0, "normal": "-"}],
                          "cylinders": [{"name": "h1", "point": [10, 10, 0], "direction": [0, 0, 1], "kind": "hole", "diameter": 6.0, "length": 10}], **acceptance_extra}
    for k in ("volume", "center_of_mass", "blockout"):
        data["acceptance"].pop(k, None)
    return PartContract.model_validate(data)


def _shape():
    box = BRepPrimAPI_MakeBox(40, 30, 10).Shape()
    hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(10, 10, -1), gp_Dir(0, 0, 1)), 3.0, 12).Shape()
    shape = BRepAlgoAPI_Cut(box, hole).Shape()
    pin = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(30, 15, 10), gp_Dir(0, 0, 1)), 4.0, 5).Shape()
    return BRepAlgoAPI_Fuse(shape, pin).Shape()


def test_cylinder_specs_pass_and_fail():
    c = _contract(cylinders=[
        {"name": "h1", "point": [10, 10, 0], "direction": [0, 0, 1], "kind": "hole", "diameter": 6.0, "length": 10},
        {"name": "p1", "point": [30, 15, 0], "direction": [0, 0, 1], "kind": "pin", "radius": 4.0},
        {"name": "h_off", "point": [10.7, 10, 0], "direction": [0, 0, 1], "kind": "hole", "radius": 3.0},
        {"name": "h_missing", "point": [20, 20, 0], "direction": [0, 0, 1], "kind": "hole", "radius": 1.0},
    ])
    r = features.check_cylinders(_shape(), c)
    assert r["h1"]["ok"] and r["h1"]["checks"]["length"]["ok"] and r["p1"]["ok"]
    assert r["h_off"]["found"] and not r["h_off"]["ok"] and abs(r["h_off"]["axis_offset"] - 0.7) < 1e-6
    assert not r["h_missing"]["found"] and not r["h_missing"]["ok"]
    feats = features.check_features(_shape(), c, {}, {}, True, cylinders=r)
    assert feats["hole"]["ok"] and feats["hole"]["checks"][0]["method"] == "cylinder"


def test_plane_and_dimension_specs():
    c = _contract(planes=[{"name": "side", "point": [40, 0, 0], "normal": [1, 0, 0], "area": 300}, {"name": "tilted", "point": [0, 0, 0], "normal": [0.7071, 0, 0.7071]}],
                  dimensions=[{"name": "thick", "axis": "z", "expected": 10, "tolerance": 0.05, "between": ["top", "bottom"]},
                              {"name": "span", "axis": "x", "expected": 40, "tolerance": 0.05},
                              {"name": "wrong", "axis": "y", "expected": 31, "tolerance": 0.05}])
    shape = _shape()
    pl = features.check_planes(shape, c)
    assert pl["side"]["ok"] and pl["side"]["found"] == 1 and not pl["tilted"]["ok"]
    faces = features.check_faces(shape, c)
    dims = features.check_dimensions(c, [40, 30, 15], faces)
    assert dims["thick"]["ok"] and abs(dims["thick"]["measured"] - 10) < 1e-9
    assert dims["span"]["ok"] and not dims["wrong"]["ok"]
    assert c.interface_checks() == ["h1", "top"]


def test_sum_face_totals_the_plane_beside_one_faces():
    """A `sum` face spec counts every hit on its plane even when `one` specs share the plane (the scorer's mode)."""
    c = _contract()
    c.acceptance.faces = [FaceSpec(name="top", plane="z", at=10, normal="+"), FaceSpec(name="pinTop", plane="z", at=15, normal="+", mode="one"),
                          FaceSpec(name="zTopTotal", plane="z", at=15, normal="+", mode="sum", area=50.27, area_tolerance_rel=0.02),
                          FaceSpec(name="z10Total", plane="z", at=10, normal="+", mode="sum", area=1200 - 28.27 - 50.27, area_tolerance_rel=0.02)]
    r = features.check_faces(_shape(), c)
    assert r["pinTop"]["found"] == 1 and r["zTopTotal"]["found"] == 1 and r["zTopTotal"]["ok"], r["zTopTotal"]
    assert r["top"]["ok"] and r["z10Total"]["ok"] and abs(r["z10Total"]["area"] - (1200 - 28.27 - 50.27)) < 1.0  # top minus the hole and the pin footprint


def test_inclined_plane_found_on_wedge():
    wedge = BRepPrimAPI_MakeWedge(10, 10, 10, 0).Shape()  # slanted face from (0,0,10)-(10,..) down to x=10 at z=0? use planar_faces to discover
    faces = brep.planar_faces(wedge)
    slanted = [f for f in faces if all(abs(abs(x) - 1) > 1e-6 for x in f["normal"] if abs(x) > 1e-9)]
    assert slanted, "wedge should have an inclined face"
    f = slanted[0]
    hits = brep.find_face_normal(faces, f["normal"], f["point"], 0.01)
    assert len(hits) == 1


def test_contract_rejects_unknown_interface_check_and_duplicate_cylinder():
    with pytest.raises(ValueError):
        _contract(cylinders=[{"name": "h1", "point": [0, 0, 0], "direction": [0, 0, 1], "radius": 1}, {"name": "h1", "point": [1, 0, 0], "direction": [0, 0, 1], "radius": 1}])
    data = yaml.safe_load(yaml.safe_dump(BASE))
    data["interfaces"] = [{"name": "x", "description": "d", "checks": ["nope"]}]
    with pytest.raises(ValueError):
        PartContract.model_validate(data)
    with pytest.raises(ValueError):
        _contract(cylinders=[{"name": "h1", "point": [0, 0, 0], "direction": [0, 0, 1], "radius": 1, "diameter": 2}])


def test_provenance_checks_resolve_sources(tmp_path: Path):
    c = _contract()
    design = tmp_path / "geo-test"
    (design / "sources").mkdir(parents=True)
    ctx = Ctx("geo-test", design, design / "contract.yaml", c, tmp_path / "results", tmp_path / "parts")
    pv = gates.provenance_checks(ctx)
    assert pv["unresolved_sources"] == {"plateWidth": ["sources/spec.md"]} and pv["unenforced_interfaces"] == []
    (design / "sources" / "spec.md").write_text("spec")
    pv = gates.provenance_checks(ctx)
    assert pv["unresolved_sources"] == {} and pv["interface_checks"] == ["h1", "top"]
    c.open_questions.append("blocking: which face is the datum?")
    assert gates.provenance_checks(ctx)["blocking_questions"]

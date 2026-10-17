"""Multi-body contract checks (solids, hardware, clearances, passages, thickness, counts, probes) and their truth kinds."""

from __future__ import annotations

from pathlib import Path

import yaml
from OCP.BRep import BRep_Builder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.TopoDS import TopoDS_Compound

from opencad.geomcheck import brep, multibody
from opencad.paths import DESIGNS
from opencad.schemas import PartContract
from opencad.truth.mutants import write_stl

BASE = yaml.safe_load((DESIGNS / "_template" / "contract.yaml").read_text())


def _enclosure():
    base = BRepAlgoAPI_Cut(BRepPrimAPI_MakeBox(gp_Pnt(-3, -3, -8), gp_Pnt(93, 63, 10)).Shape(), BRepPrimAPI_MakeBox(gp_Pnt(-1, -1, -6), gp_Pnt(91, 61, 11)).Shape()).Shape()
    # a plug opening in the y = -3..-1 wall
    base = BRepAlgoAPI_Cut(base, BRepPrimAPI_MakeBox(gp_Pnt(5, -4, 2), gp_Pnt(18, 0, 9)).Shape()).Shape()
    # a standoff with a pilot hole
    boss = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(3.5, 3.5, -6), gp_Dir(0, 0, 1)), 3.0, 6).Shape()
    base = BRepAlgoAPI_Cut(BRepAlgoAPI_Cut(base, boss).Shape(), boss).Shape() if False else base
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse

    base = BRepAlgoAPI_Fuse(base, boss).Shape()
    base = BRepAlgoAPI_Cut(base, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(3.5, 3.5, -5), gp_Dir(0, 0, 1)), 1.25, 6).Shape()).Shape()
    lid = BRepAlgoAPI_Cut(BRepPrimAPI_MakeBox(gp_Pnt(-3, -3, 10), gp_Pnt(93, 63, 26)).Shape(), BRepPrimAPI_MakeBox(gp_Pnt(-1, -1, 9), gp_Pnt(91, 61, 24)).Shape()).Shape()
    comp = TopoDS_Compound()
    bb = BRep_Builder()
    bb.MakeCompound(comp)
    bb.Add(comp, base)
    bb.Add(comp, lid)
    return comp


SOLIDS = [{"name": "base", "contains_point": [45, 30, -7]}, {"name": "lid", "contains_point": [45, 30, 25]}]
HW = [{"name": "board", "kind": "box", "min": [0, 0, 0], "max": [85, 56, 1.6]},
      {"name": "usb_plug", "kind": "box", "min": [6, -20, 2.5], "max": [17, 0, 8.5]},
      {"name": "blocked_plug", "kind": "box", "min": [40, -20, 2.5], "max": [50, 0, 8.5]},
      {"name": "keepout", "kind": "box", "min": [0, 0, -3], "max": [85, 56, 0], "exclude_cylinders": [{"point": [3.5, 3.5, -4], "direction": [0, 0, 1], "radius": 3.1, "length": 5}]}]


def test_multibody_checks_on_synthetic_enclosure(tmp_path: Path):
    comp = _enclosure()
    hw = multibody.build_hardware(HW)
    sol = multibody.check_solids(comp, SOLIDS)
    assert sol["base"]["found"] and sol["lid"]["found"] and sol["base"]["volume"] > sol["lid"]["volume"]
    cl = multibody.check_clearances(comp, [
        {"name": "board_fit", "a": "all", "b": "board", "min_gap": 0.0},  # standoffs touch the board bottom: contact allowed, interference not
        {"name": "usb", "a": "all", "b": "usb_plug"},
        {"name": "blocked", "a": "all", "b": "blocked_plug"},
        {"name": "keepout_ok", "a": "all", "b": "keepout"},
        {"name": "lid_on_base", "a": "lid", "b": "base", "max_gap": 0.1},
    ], SOLIDS, hw)
    assert cl["board_fit"]["ok"] and cl["usb"]["ok"] and not cl["blocked"]["ok"] and cl["lid_on_base"]["ok"]
    assert cl["keepout_ok"]["ok"], cl["keepout_ok"]  # the standoff sits inside the excluded ring
    stl = write_stl(comp, tmp_path / "enc.stl", 0.05)
    th = multibody.check_thickness(stl, [{"name": "wall", "min": 1.5, "samples": 3000, "max_thickness": 10}])
    assert th["wall"]["ok"] and abs(th["wall"]["measured"] - 2.0) < 0.1
    pr = multibody.check_probes(comp, [{"name": "head", "state": "void", "points": [[40, 30, 20]]}, {"name": "floor", "state": "solid", "points": [[40, 30, -7]]}])
    assert pr["head"]["ok"] and pr["floor"]["ok"]
    cnt = multibody.check_cylinder_counts(brep.cylinders(comp), [{"name": "pilots", "radius": 1.25, "kind": "hole", "expected_min": 1}, {"name": "missing", "radius": 1.6, "expected_min": 4}])
    assert cnt["pilots"]["ok"] and not cnt["missing"]["ok"]


def test_contract_accepts_multibody_acceptance():
    raw = yaml.safe_load(yaml.safe_dump(BASE))
    raw["acceptance"].update({
        "solid_count": 2,
        "solids": SOLIDS,
        "hardware": HW[:2],
        "clearances": [{"name": "board_fit", "a": "all", "b": "board", "min_gap": 0.5}, {"name": "lid_on_base", "a": "lid", "b": "base", "max_gap": 0.1}],
        "passages": [{"name": "duct", "point_a": [0, 0, 0], "point_b": [1, 1, 1], "seal_radius": 3.0}],
        "thickness": [{"name": "wall", "min": 2.0}],
        "probes": [{"name": "head", "state": "void", "points": [[40, 30, 20]]}],
        "cylinder_counts": [{"name": "pilots", "radius": 1.25, "kind": "hole", "expected_min": 8}],
    })
    c = PartContract.model_validate(raw)
    assert [s.name for s in c.acceptance.solids] == ["base", "lid"] and c.acceptance.clearances[1].max_gap == 0.1
    import pytest

    raw["acceptance"]["clearances"].append({"name": "bad", "a": "nowhere", "b": "board"})
    with pytest.raises(ValueError):
        PartContract.model_validate(raw)

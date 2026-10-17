"""Cylinder detection and the mutant harness: deliberately wrong parts must fail the scorer."""

from __future__ import annotations

from pathlib import Path

import pytest
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

from opencad.geomcheck import brep
from opencad.paths import RESULTS, TRUTH
from opencad.truth import mutants
from opencad.truth.manifest import load_manifest


def _plate_with_hole_and_pin():
    box = BRepPrimAPI_MakeBox(40, 30, 10).Shape()
    hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(10, 10, -1), gp_Dir(0, 0, 1)), 3.0, 12).Shape()
    shape = BRepAlgoAPI_Cut(box, hole).Shape()
    pin = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(30, 15, 10), gp_Dir(0, 0, 1)), 4.0, 5).Shape()
    shape = BRepAlgoAPI_Fuse(shape, pin).Shape()
    side = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(-1, 20, 5), gp_Dir(1, 0, 0)), 1.5, 8).Shape()
    return BRepAlgoAPI_Cut(shape, side).Shape()


def test_cylinders_hole_vs_pin_and_extent():
    cyls = brep.cylinders(_plate_with_hole_and_pin())
    kinds = sorted((c["kind"], round(c["radius"], 3)) for c in cyls)
    assert kinds == [("hole", 1.5), ("hole", 3.0), ("pin", 4.0)]
    through = next(c for c in cyls if c["radius"] == 3.0)
    assert through["full"] and abs(through["length"] - 10) < 1e-6 and [round(x, 6) for x in through["center"]] == [10, 10, 5]
    blind = next(c for c in cyls if c["radius"] == 1.5)
    assert abs(blind["length"] - 7) < 1e-6 and blind["direction"] == [1.0, 0.0, 0.0]


def test_match_cylinder_reports_axis_offset():
    cyls = brep.cylinders(_plate_with_hole_and_pin())
    m = brep.match_cylinder(cyls, [10.7, 10, 0], [0, 0, 1], 3.0, kind="hole", axis_tol=0.05, radius_tol=0.01)
    assert m["found"] and not m["ok"] and abs(m["axis_offset"] - 0.7) < 1e-6
    m = brep.match_cylinder(cyls, [30, 15, 0], [0, 0, 1], 4.0, kind="pin", axis_tol=0.05, radius_tol=0.01)
    assert m["ok"] and m["axis_offset"] < 1e-9
    assert not brep.match_cylinder(cyls, [30, 15, 0], [0, 0, 1], 4.0, kind="hole", axis_tol=0.05, radius_tol=0.01)["found"]


def test_shift_hole_moves_only_that_hole():
    shape = _plate_with_hole_and_pin()
    moved = mutants.shift_hole(shape, near=[10, 10, 5], offset=[0.7, 0, 0], radius=3.0)
    cyls = brep.cylinders(moved)
    hole = next(c for c in cyls if c["kind"] == "hole" and abs(c["radius"] - 3.0) < 1e-6)
    assert abs(hole["center"][0] - 10.7) < 1e-6 and abs(hole["center"][1] - 10) < 1e-6
    # the plug is 1 um oversize so the fuse is robust; the leftover sliver is < 0.01 mm3
    assert abs(brep.volume_props(moved)["volume"] - brep.volume_props(shape)["volume"]) < 0.05


def test_scale_and_fuse_and_remove():
    shape = _plate_with_hole_and_pin()
    lo, hi = brep.bbox(mutants.scale(shape, 1.02))
    assert abs((hi[0] - lo[0]) - 40.8) < 1e-6
    two = BRepAlgoAPI_Fuse(BRepPrimAPI_MakeBox(10, 10, 10).Shape(), BRepPrimAPI_MakeBox(gp_Pnt(20, 0, 0), gp_Pnt(30, 10, 10)).Shape()).Shape()
    assert len(brep.solids(two)) == 2
    assert len(brep.solids(mutants.remove_solid(two, contains=[25, 5, 5]))) == 1
    # a bridge fuses the two bodies into one (the "fused moving component" failure)
    assert len(brep.solids(mutants.fill_box(two, [9, 4, 4], [21, 6, 6]))) == 1
    overlapping = mutants.remove_solid(two, contains=[25, 5, 5])
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound
    comp = TopoDS_Compound()
    b = BRep_Builder()
    b.MakeCompound(comp)
    b.Add(comp, overlapping)
    b.Add(comp, BRepPrimAPI_MakeBox(gp_Pnt(8, 0, 0), gp_Pnt(18, 10, 10)).Shape())
    assert len(brep.solids(comp)) == 2 and len(brep.solids(mutants.fuse_solids(comp))) == 1


@pytest.mark.skipif(not (RESULTS / "chiral-keyplate" / "handoff" / "chiral-keyplate.step").exists() or not (TRUTH / "cases" / "chiral-keyplate" / "truth").exists(),
                    reason="needs the chiral candidate and unsequestered truth")
def test_chiral_mutants_are_caught(tmp_path: Path):
    m = load_manifest("chiral-keyplate")
    specs = {s["id"]: s for s in mutants.load_mutants("chiral-keyplate")}
    r = mutants.run_mutant("chiral-keyplate", m, "text-only", specs["mirrored"], out_dir=tmp_path / "mirrored")
    assert r["baseline"]["verdict"] == "PASS" and r["verdict"] == "FAIL"
    assert "not_matching_mirror" in r["caught_by"] and r["ok"]
    r = mutants.run_mutant("chiral-keyplate", m, "text-only", specs["scaled_2pct"], out_dir=tmp_path / "scaled", baseline=False)
    assert "bbox_size" in r["caught_by"] and r["ok"]

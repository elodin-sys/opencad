"""Coarse-to-fine meshing sweep: resolution bookkeeping, interference detection, and the per-shell watertight rule."""

from __future__ import annotations

from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt

from opencad.gates import mesh_watertight
from opencad.geomcheck import gears


def _box(x0: float, y0: float, z0: float, dx: float, dy: float, dz: float):
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), dx, dy, dz).Shape()


def test_mesh_motion_coarse_to_fine_counts_and_verdict():
    # two 10 mm cubes on axes 40 mm apart, 20 mm gap: never touch, so every pose passes the interference check but the gap exceeds the band
    a = _box(-5, -5, 0, 10, 10, 10)
    b = _box(35, -5, 0, 10, 10, 10)
    r = gears.mesh_motion(a, b, ([0, 0, 0], [0, 0, 1]), ([40, 0, 0], [0, 0, 1]), ratio=0.5, pitch_deg=18, steps=72, backlash_max=0.15, coarse=6, workers=1)
    assert r["coarse_steps"] == 6 and r["requested_steps"] == 72
    assert 7 <= len(r["poses"]) <= 7 + 2 * 12 and r["refined_poses"] > 0
    assert r["max_interference"] == 0.0 and r["gap_min"] > 10 and not r["ok"]  # gap outside the backlash band
    thetas = [p["theta_deg"] for p in r["poses"]]
    assert thetas == sorted(thetas) and len(set(thetas)) == len(thetas)


def test_mesh_motion_detects_interference_and_parallel_path():
    a = _box(-5, -5, 0, 10, 10, 10)
    b = _box(2, -5, 0, 10, 10, 10)  # overlaps by 3 mm at theta = 0
    r = gears.mesh_motion(a, b, ([0, 0, 0], [0, 0, 1]), ([7, 0, 0], [0, 0, 1]), ratio=1.0, pitch_deg=20, steps=8, backlash_max=0.3, coarse=4, workers=2)
    assert r["max_interference"] > 100 and not r["ok"] and r["workers"] == 2
    assert any(p["theta_deg"] == 0 and not p["ok"] for p in r["poses"])


def test_mesh_watertight_per_shell_rule():
    assert mesh_watertight({"watertight": True}, 1)
    assert not mesh_watertight({"watertight": False, "solids_watertight": True}, 1)
    assert mesh_watertight({"watertight": False, "solids_watertight": True, "components_watertight": [True, True, True]}, 3)
    assert not mesh_watertight({"watertight": False, "solids_watertight": False}, 3)

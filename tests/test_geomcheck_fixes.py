"""Evaluator fixes from the 2026-09-19 recon runs: gapped coaxial bores, teeth with an inner loop, concentric face pairing, revolve halves, passage sealing."""

from __future__ import annotations

import math
from pathlib import Path

from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.StlAPI import StlAPI_Writer

from opencad.geomcheck import assembly, brep, features, gears
from opencad.schemas import FaceSpec


def _cyl(x: float, y: float, z: float, dx: float, dy: float, dz: float, r: float, h: float):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z), gp_Dir(dx, dy, dz)), r, h).Shape()


def _cut(a, b):
    op = BRepAlgoAPI_Cut(a, b)
    op.Build()
    return op.Shape()


def _fuse(a, b):
    op = BRepAlgoAPI_Fuse(a, b)
    op.Build()
    return op.Shape()


def test_gapped_coaxial_bores_stay_separate():
    """Two Ø2 x 5 blind bores drilled from opposite edges of a 100 mm plate are two features, not one Ø2 x 100 cylinder."""
    plate = BRepPrimAPI_MakeBox(gp_Pnt(-50, -50, 0), 100, 100, 3).Shape()
    plate = _cut(plate, _cyl(-50.5, 42, 1.5, 1, 0, 0, 1.0, 5.5))
    plate = _cut(plate, _cyl(50.5, 42, 1.5, -1, 0, 0, 1.0, 5.5))
    holes = [c for c in brep.cylinders(plate) if c["kind"] == "hole" and abs(c["radius"] - 1.0) < 1e-6]
    assert len(holes) == 2, holes
    assert all(abs(h["length"] - 5.0) < 1e-6 for h in holes)
    assert sorted(round(h["center"][0], 3) for h in holes) == [-47.5, 47.5]
    # a bore split into two faces by a seam (touching extents) is still one feature
    through = _cut(BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 20, 20, 10).Shape(), _cyl(10, 10, -1, 0, 0, 1, 3.0, 12))
    one = [c for c in brep.cylinders(through) if c["kind"] == "hole"]
    assert len(one) == 1 and abs(one[0]["length"] - 10) < 1e-6


def _gear(teeth: int = 12, r_root: float = 8.0, r_tip: float = 10.0, thick: float = 4.0, socket: float | None = None):
    body = _cyl(0, 0, 0, 0, 1, 0, r_root, thick)
    for k in range(teeth):
        ang = 2 * math.pi * k / teeth
        tooth = BRepPrimAPI_MakeBox(gp_Pnt(r_root - 0.5, 0, -0.8), r_tip - r_root + 0.5, thick, 1.6).Shape()
        t = gp_Trsf()
        t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)), ang)
        body = _fuse(body, BRepBuilderAPI_Transform(tooth, t, True).Shape())
    if socket:
        body = _cut(body, _cyl(0, -1, 0, 0, 1, 0, socket, thick + 2))
    return body


def test_tooth_count_ignores_an_inner_loop():
    module = 2 * 10.0 / 12  # tip diameter / teeth, close enough for the threshold
    plain = gears.tooth_count(_gear(), [0, 0, 0], [0, 1, 0], 2.0, module, expected_teeth=12)
    assert plain["teeth"] == 12 and plain["ok"]
    with_socket = gears.tooth_count(_gear(socket=3.5), [0, 0, 0], [0, 1, 0], 2.0, module, expected_teeth=12)
    assert with_socket["teeth"] == 12 and with_socket["ok"], with_socket
    assert with_socket["root_radius"] > 3.5, "the root radius is the toothed loop's minimum, not the socket"


def test_concentric_coplanar_faces_pair_by_area():
    """A flange annulus and a hub disc share a plane and a centre; the area tie-break assigns each spec its own face."""
    disc = _cyl(0, 0, 0, 0, 0, 1, 40.0, 5.0)
    part = _cut(disc, _cut(_cyl(0, 0, -1, 0, 0, 1, 20.0, 7), _cyl(0, 0, -1, 0, 0, 1, 15.0, 7)))  # full-depth ring groove r 15..20
    faces = brep.planar_faces(part)
    hits = brep.find_face(faces, "z", 0.0, "-", 0.05)
    assert len(hits) == 2
    hub = FaceSpec(name="hub", plane="z", at=0.0, normal="-", area=math.pi * 15 ** 2, center=(0.0, 0.0), mode="one")
    flange = FaceSpec(name="flange", plane="z", at=0.0, normal="-", area=math.pi * (40 ** 2 - 20 ** 2), center=(0.0, 0.0), mode="one")
    res = features.assign_coplanar([flange, hub], hits, "z")
    assert res["flange"]["ok"] and abs(res["flange"]["area"] - math.pi * 1200) < 1.0
    assert res["hub"]["ok"] and abs(res["hub"]["area"] - math.pi * 225) < 1.0


def test_revolve_half_faces_merge_into_the_named_face():
    """Two half-annulus hits (a seam-split 360-degree revolve, centroids at y = +/-22.79) satisfy one `mode: one` face spec together."""
    full = math.pi * (40 ** 2 - 20 ** 2)
    half = full / 2
    hits = [{"normal": [0, 0, -1], "point": [0, 22.79, 0], "centroid": [0, 22.79, 0], "area": half, "bbox_min": [-40, 0, 0], "bbox_max": [40, 40, 0]},
            {"normal": [0, 0, -1], "point": [0, -22.79, 0], "centroid": [0, -22.79, 0], "area": half, "bbox_min": [-40, -40, 0], "bbox_max": [40, 0, 0]},
            {"normal": [0, 0, -1], "point": [60, 0, 0], "centroid": [60, 0, 0], "area": 12.0, "bbox_min": [58, -2, 0], "bbox_max": [62, 2, 0]}]
    spec = FaceSpec(name="bottom", plane="z", at=0.0, normal="-", area=full, center=(0.0, 0.0), mode="one")
    res = features.assign_coplanar([spec], hits, "z")
    assert res["bottom"]["ok"] and res["bottom"].get("merged_faces") == 2 and abs(res["bottom"]["area"] - full) < 1e-6
    assert res["bottom"]["center_error"] < 1e-9 and res["bottom"]["found"] == 2
    # a single face that already matches is untouched
    one = features.assign_coplanar([spec], [{"normal": [0, 0, -1], "point": [0, 0, 0], "centroid": [0, 0, 0], "area": full, "bbox_min": [-40, -40, 0], "bbox_max": [40, 40, 0]}], "z")
    assert one["bottom"]["ok"] and "merged_faces" not in one["bottom"]


def _stl(shape, path: Path) -> Path:
    BRepMesh_IncrementalMesh(shape, 0.1, False, 0.3, True)
    w = StlAPI_Writer()
    w.ASCIIMode = False
    w.Write(shape, str(path))
    return path


def test_passage_seal_radius_floors_and_reports_a_fill(tmp_path: Path):
    """A 2.4 mm seal at 0.5 mm pitch is 4 voxels (2.0 mm), not 5 (2.5 mm): it must not fill a Ø5 through bore; plugs are the right seal."""
    block = _cut(BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 20, 20, 30).Shape(), _cyl(10, 10, -1, 0, 0, 1, 2.5, 32))
    stl = _stl(block, tmp_path / "bore.stl")
    a, b = [10, 10, 5], [10, 10, 25]
    r = assembly.passage(stl, a, b, pitch=0.5, seal_radius=2.4)
    assert r["seal_effective_mm"] == 2.0 and "error" not in r
    assert r["a"]["state"] != "solid" and r["reaches_exterior"], "an unsealed through bore reads exterior, not solid"
    r2 = assembly.passage(stl, a, b, pitch=0.5, seal_radius=3.0)
    assert r2["a"]["state"] == "solid" and "fills the passage" in r2["error"]
    plugged = assembly.passage(stl, a, b, pitch=0.5, plugs=[([6, 6, -1.5], [14, 14, 0.5]), ([6, 6, 29.5], [14, 14, 31.5])])
    assert plugged["ok"] and plugged["connected"] and not plugged["reaches_exterior"]

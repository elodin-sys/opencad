#!/usr/bin/env python3
"""Build the chiral-keyplate truth STEP/STL and its mirrored mesh (OpenCascade, no Zoo).

Square plate 80 x 80 x 8 mm, origin at the XY centre, z = 0 at the bottom. Four 16 x 6 mm
pockets, 4 mm deep from the top, in a C4 pinwheel whose first slot is centred at (20, 8).
The mirror in the YZ plane (x -> -x) has the same volume, bbox and COM but a different
pattern.

usage: derive_chiral_truth.py <out-dir>
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.StlAPI import StlAPI_Writer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from opencad.geomcheck import brep, mesh as meshcheck  # noqa: E402

PLATE = 80.0
THICK = 8.0
SLOT_L = 16.0
SLOT_W = 6.0
SLOT_D = 4.0
SLOT_A = (20.0, 8.0)  # centre of slot A in XY


def _box(xmin: float, ymin: float, zmin: float, xmax: float, ymax: float, zmax: float):
    return BRepPrimAPI_MakeBox(gp_Pnt(xmin, ymin, zmin), gp_Pnt(xmax, ymax, zmax)).Shape()


def slot_centres() -> list[tuple[float, float, float, float]]:
    """(cx, cy, dx, dy) for each slot; dx/dy are plan extents (long along the pinwheel)."""
    cx, cy = SLOT_A
    return [
        (cx, cy, SLOT_L, SLOT_W),
        (-cy, cx, SLOT_W, SLOT_L),
        (-cx, -cy, SLOT_L, SLOT_W),
        (cy, -cx, SLOT_W, SLOT_L),
    ]


def build_plate():
    half = PLATE / 2
    body = _box(-half, -half, 0.0, half, half, THICK)
    for cx, cy, dx, dy in slot_centres():
        cutter = _box(cx - dx / 2, cy - dy / 2, THICK - SLOT_D, cx + dx / 2, cy + dy / 2, THICK + 1.0)
        cut = BRepAlgoAPI_Cut(body, cutter)
        cut.Build()
        body = cut.Shape()
    return body


def write_step(shape, path: Path) -> None:
    Interface_Static.SetCVal_s("write.step.schema", "AP214")
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    w.Write(str(path))


def write_stl(shape, path: Path, deflection: float = 0.02) -> None:
    BRepMesh_IncrementalMesh(shape, deflection, False, 0.2, True)
    sw = StlAPI_Writer()
    sw.ASCIIMode = False
    sw.Write(shape, str(path))


def mirror_yz(shape):
    tr = gp_Trsf()
    tr.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)))
    return BRepBuilderAPI_Transform(shape, tr, True).Shape()


def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    plate = build_plate()
    step = out_dir / "chiral-keyplate.step"
    stl = out_dir / "chiral-keyplate.stl"
    mirrored = out_dir / "chiral-keyplate-mirrored.stl"
    write_step(plate, step)
    write_stl(plate, stl)
    write_stl(mirror_yz(plate), mirrored)
    a = brep.analyze_step(step)
    print("truth", {k: a[k] for k in ("solids", "valid", "faces", "bbox_min", "bbox_max", "volume", "center_of_mass")})
    shape = brep.read_step(step)
    for z in (2.0, 6.0):
        s = brep.section(shape, "z", z)
        print(f"section z={z}", {k: s[k] for k in ("area", "loops", "holes")},
              [(r["centroid"], [b - a for a, b in zip(r["bbox_min"], r["bbox_max"])]) for r in s["regions"]])
    z_floor = THICK - SLOT_D
    faces = [f for f in brep.planar_faces(shape) if abs(f["centroid"][2] - z_floor) < 0.05 and f["area"] < 200]
    print("pocket floors", [(f["area"], f["centroid"], f["normal"]) for f in faces])
    d = meshcheck.deviation(stl, mirrored, samples=20000, seed=0)
    print("truth vs mirrored", {k: d[k] for k in ("p95", "hausdorff_estimate", "silhouette_iou_min", "volume_ratio")})
    print("analytic volume", PLATE * PLATE * THICK - 4 * SLOT_L * SLOT_W * SLOT_D)
    print("slot centres", slot_centres())


if __name__ == "__main__":
    main(Path(sys.argv[1]))

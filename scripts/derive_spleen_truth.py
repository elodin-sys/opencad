#!/usr/bin/env python3
"""Derive a single-blade SPLEEN C1 truth from a published cascade CAD.

SPLEENC1_Geometry_Airfoil_2D_CAD_v{1,2}.stp is a five-blade cascade (blades extruded
165 mm along its y axis, pitchwise along z). This script cuts out the central blade
with a box, maps it into the coordinate-table frame (x axial, y pitchwise as in
SPLEENC1_Geometry_Airfoil_2D_v1.xlsx, z spanwise 0..165) and writes
truth/spleen-c1-blade3-from-<source>.step plus an STL tessellation.

v1 (Zenodo 7264762, 2022-10-30) has the documented wrong stagger; v2 is the
corrected CAD. The v1 plate sits at y = -0.1..0; the v2 plate at y = 165..165.1.
Re-run v2 only if you intend to replace the pinned hashes.

usage: derive_spleen_truth.py [--source v1|v2] <cad.stp> <out-dir>
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.StlAPI import StlAPI_Writer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from opencad.geomcheck import brep  # noqa: E402

# central blade of the five; y range excludes the end plate on that revision
BOXES = {
    "v2": ((-5.0, -1.0, -10.8), (52.0, 165.0, 23.0)),  # CAD z -9.51 .. 21.70
    "v1": ((-5.0, 0.05, -10.8), (52.0, 165.0, 23.0)),  # CAD z -9.69 .. 20.71; plate at y < 0
}


def derive(src: Path, out_dir: Path, source: str) -> None:
    lo, hi = BOXES[source]
    shape = brep.read_step(src)
    box = BRepPrimAPI_MakeBox(gp_Pnt(*lo), gp_Pnt(*hi)).Shape()
    common = BRepAlgoAPI_Common(shape, box)
    common.Build()
    blade = common.Shape()
    # rotation +90 deg about x maps (x, y, z) -> (x, -z, y): table frame
    tr = gp_Trsf()
    tr.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi / 2)
    moved = BRepBuilderAPI_Transform(blade, tr, True).Shape()
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"spleen-c1-blade3-from-{source}"
    step_out = out_dir / f"{stem}.step"
    Interface_Static.SetCVal_s("write.step.schema", "AP214")
    w = STEPControl_Writer()
    w.Transfer(moved, STEPControl_AsIs)
    w.Write(str(step_out))
    BRepMesh_IncrementalMesh(moved, 0.01, False, 0.1, True)
    sw = StlAPI_Writer()
    sw.ASCIIMode = False
    sw.Write(moved, str(out_dir / f"{stem}.stl"))
    a = brep.analyze_step(step_out)
    print(source, {k: a[k] for k in ("solids", "valid", "faces", "bbox_min", "bbox_max", "volume", "surface_area", "center_of_mass")})
    sec = brep.section(brep.read_step(step_out), "z", 82.5)
    print("midspan section", {k: sec[k] for k in ("area", "loops", "holes")}, [(r["bbox_min"], r["bbox_max"]) for r in sec["regions"]])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--source", choices=sorted(BOXES), default="v2")
    a = ap.parse_args()
    derive(a.src, a.out_dir, a.source)


if __name__ == "__main__":
    main()

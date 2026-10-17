#!/usr/bin/env python3
"""Revolve the NASA TMR axisymmetric transonic bump meridian (OpenCascade, no Zoo).

Bachalo & Johnson 1986 / NASA TMR ATB. Inch-native: c = 8 in, t = 0.75 in, d = 6 in.
R1 = 0.5 (t^2 + 0.25 c^2) / t = 280.46 mm. Leading-edge fillet R2 is 18.30 cm or 20.32 cm;
this script builds both. Truth STEP/STL is R2 = 183.0 mm. Axial extent is the x-range of
bumpgrd.surfpts_orig.dat (nondimensional by the 8 in chord).

usage: derive_bump_truth.py <surfpts.dat> <out-dir>
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
from OCP.GC import GC_MakeArcOfCircle, GC_MakeSegment
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.StlAPI import StlAPI_Writer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from opencad.geomcheck import brep  # noqa: E402

IN = 25.4
C = 8.0 * IN
T = 0.75 * IN
R_CYL = 3.0 * IN
R1 = 0.5 * (T * T + 0.25 * C * C) / T
R2_TRUTH = 183.0
R2_ALT = 203.2
CHORD_MM = 203.2


def load_x_range(path: Path) -> tuple[float, float]:
    xs = []
    for line in Path(path).read_text().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            xs.append(float(parts[0]) * CHORD_MM)
        except ValueError:
            continue
    if len(xs) < 8:
        raise SystemExit(f"{path}: not enough points")
    return xs[0], xs[-1]


def tangent_points(r2: float) -> dict[str, tuple[float, float]]:
    c1 = (C / 2.0, R_CYL + T - R1)
    c2y = R_CYL + r2
    dy = c1[1] - c2y
    dist = R1 + r2
    c2 = (c1[0] - math.sqrt(dist * dist - dy * dy), c2y)
    tan_cyl = (c2[0], R_CYL)
    nrm = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
    n = ((c1[0] - c2[0]) / nrm, (c1[1] - c2[1]) / nrm)
    tan_bump = (c2[0] + r2 * n[0], c2[1] + r2 * n[1])
    a0 = math.atan2(tan_cyl[1] - c2[1], tan_cyl[0] - c2[0])
    a1 = math.atan2(tan_bump[1] - c2[1], tan_bump[0] - c2[0])
    da = a1 - a0
    while da <= 0:
        da += 2 * math.pi
    am = a0 + da / 2
    mid_fillet = (c2[0] + r2 * math.cos(am), c2[1] + r2 * math.sin(am))
    peak = (C / 2.0, R_CYL + T)
    te = (C, R_CYL)
    return {"tan_cyl": tan_cyl, "mid_fillet": mid_fillet, "tan_bump": tan_bump, "peak": peak, "te": te}


def _seg(a: tuple[float, float], b: tuple[float, float]):
    return BRepBuilderAPI_MakeEdge(GC_MakeSegment(gp_Pnt(*a, 0), gp_Pnt(*b, 0)).Value()).Edge()


def _arc(p1: tuple[float, float], p2: tuple[float, float], p3: tuple[float, float]):
    return BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(gp_Pnt(*p1, 0), gp_Pnt(*p2, 0), gp_Pnt(*p3, 0)).Value()).Edge()


def revolve(r2: float, x_min: float, x_max: float):
    t = tangent_points(r2)
    w = BRepBuilderAPI_MakeWire()
    w.Add(_seg((x_min, 0.0), (x_min, R_CYL)))
    w.Add(_seg((x_min, R_CYL), t["tan_cyl"]))
    w.Add(_arc(t["tan_cyl"], t["mid_fillet"], t["tan_bump"]))
    w.Add(_arc(t["tan_bump"], t["peak"], t["te"]))
    w.Add(_seg(t["te"], (x_max, R_CYL)))
    w.Add(_seg((x_max, R_CYL), (x_max, 0.0)))
    w.Add(_seg((x_max, 0.0), (x_min, 0.0)))
    face = BRepBuilderAPI_MakeFace(w.Wire(), True).Face()
    return BRepPrimAPI_MakeRevol(face, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 2 * math.pi).Shape()


def write_step(shape, path: Path) -> None:
    Interface_Static.SetCVal_s("write.step.schema", "AP214")
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    w.Write(str(path))


def write_stl(shape, path: Path, deflection: float = 0.05) -> None:
    BRepMesh_IncrementalMesh(shape, deflection, False, 0.2, True)
    sw = StlAPI_Writer()
    sw.ASCIIMode = False
    sw.Write(shape, str(path))


def main(surfpts: Path, out_dir: Path) -> None:
    x_min, x_max = load_x_range(surfpts)
    out_dir.mkdir(parents=True, exist_ok=True)
    vols = {}
    for r2, label in ((R2_TRUTH, "truth"), (R2_ALT, "alt")):
        shape = revolve(r2, x_min, x_max)
        if label == "truth":
            step = out_dir / "bump.step"
            write_step(shape, step)
            write_stl(shape, out_dir / "bump.stl")
            a = brep.analyze_step(step)
            print("R2", r2, {k: a[k] for k in ("solids", "valid", "faces", "bbox_min", "bbox_max", "volume", "center_of_mass")})
            for x in (x_min + 20.0, 0.0, C / 2.0, C + 20.0):
                s = brep.section(brep.read_step(step), "x", x)
                print(f"  section x={x:.4f}", {k: s.get(k) for k in ("area", "loops", "holes")})
            vols[r2] = a["volume"]
        else:
            tmp = out_dir / "_alt.step"
            write_step(shape, tmp)
            a = brep.analyze_step(tmp)
            print("R2", r2, "volume", a["volume"])
            vols[r2] = a["volume"]
            tmp.unlink()
    print("R1", R1, "r_cyl", R_CYL, "c", C, "t", T, "x", x_min, x_max)
    print("volume band", min(vols.values()), max(vols.values()), vols)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))

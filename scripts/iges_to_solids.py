"""Reference IGES surfaces to qualified STEP solids for analysis-mode machine cases (evaluator side): read the untrimmed
surfaces, sew them at a tolerance sweep, make one solid per closed shell, repair and qualify each (geomcheck.qualify), and write
the shells whose bounding boxes match the requested bodies.

    .venv/bin/python scripts/iges_to_solids.py <file.igs> --list [--tolerance 0.05]
    .venv/bin/python scripts/iges_to_solids.py <file.igs> --body name=xmin,ymin,zmin,xmax,ymax,zmax ... --out <dir>

`--list` prints every closed shell (index, bbox, faces, volume, qualification) at each tolerance; `--body` picks, for each name,
the valid solid whose bbox is closest to the given one (within 1 mm per coordinate) over the tolerance sweep.

`--revolve name=ox,oy,oz,dx,dy,dz,angle` rebuilds that body as the revolution of its meridional section: the half-plane through
the axis at `angle` degrees from the radial direction nearest +x, the section curves polygonized into the planar cells they bound,
the union simplified to REVOLVE_TOLERANCE and revolved about the axis (analytic faces). It fits bodies made of touching
axisymmetric parts whose contact faces were sewn into one shell, and B-spline bodies whose STEP the reader's healing turns
inside-out; features off the section plane (bolt holes) are not reproduced, so choose an angle clear of them. Every written
file is read back and qualified.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import numpy as np

TOLERANCES = (0.01, 0.02, 0.05, 0.1, 0.2)
REVOLVE_TOLERANCE = 0.005  # mm, Douglas-Peucker on the section; also the sampling step / 4


def revolve_section(shape: Any, origin: list[float], axis: list[float], angle: float, snap: float = 0.1) -> tuple[Any, dict[str, Any]]:
    """The solid of revolution of `shape`'s meridional section (see the module docstring) and a record of the construction."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Section
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
    from OCP.GCPnts import GCPnts_UniformAbscissa
    from OCP.gp import gp_Ax1, gp_Dir, gp_Pln, gp_Pnt
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopoDS import TopoDS
    from shapely.geometry import LineString, box
    from shapely.ops import polygonize, unary_union

    from opencad.geomcheck import brep

    o, a = np.asarray(origin, float), np.asarray(axis, float) / np.linalg.norm(axis)
    ref = np.array([1.0, 0.0, 0.0]) if abs(a[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    u0 = ref - (ref @ a) * a
    u0 /= np.linalg.norm(u0)
    v0 = np.cross(a, u0)
    u = math.cos(math.radians(angle)) * u0 + math.sin(math.radians(angle)) * v0
    sec = BRepAlgoAPI_Section(shape, gp_Pln(gp_Pnt(*o), gp_Dir(*np.cross(u, a))))
    sec.Build()
    lines = []
    for e in brep._explore(sec.Shape(), TopAbs_EDGE):
        c = BRepAdaptor_Curve(TopoDS.Edge_s(e))
        ua = GCPnts_UniformAbscissa(c, REVOLVE_TOLERANCE * 4)
        if not ua.IsDone() or ua.NbPoints() < 2:
            continue
        pts = []
        for k in range(1, ua.NbPoints() + 1):
            q = c.Value(ua.Parameter(k))
            w = np.array([q.X(), q.Y(), q.Z()]) - o
            pts.append((float(w @ a), float(w @ u)))  # (axial, signed radial): the whole section, both sides of the axis
        lines.append(pts)
    # section edges meet within the sewing tolerance, not exactly: snap every endpoint to its cluster so the rings close
    ends = np.array([p for pts in lines for p in (pts[0], pts[-1])])
    rep = np.arange(len(ends))
    for i in range(len(ends)):
        near = np.flatnonzero(np.linalg.norm(ends - ends[i], axis=1) < snap)
        rep[near] = rep[near].min()
    for k, pts in enumerate(lines):
        pts[0], pts[-1] = tuple(ends[rep[2 * k]]), tuple(ends[rep[2 * k + 1]])
    cells = list(polygonize(unary_union([LineString(pts) for pts in lines])))
    full = unary_union(cells)
    x0, x1 = min(p[0] for pts in lines for p in pts) - 1.0, max(p[0] for pts in lines for p in pts) + 1.0
    region = full.intersection(box(x0, 0.0, x1, max(p[1] for pts in lines for p in pts) + 1.0))  # the half-section, closed on the axis
    polys = [p for p in getattr(region, "geoms", [region]) if p.geom_type == "Polygon" and p.area > 0]
    solids, faces = [], 0
    for poly in polys:
        ring = poly.simplify(REVOLVE_TOLERANCE, preserve_topology=True).exterior.coords
        mp = BRepBuilderAPI_MakePolygon()
        for x, r in list(ring)[:-1]:
            p = o + x * a + r * u
            mp.Add(gp_Pnt(*p))
        mp.Close()
        face = BRepBuilderAPI_MakeFace(mp.Wire(), True).Face()
        solids.append(BRepPrimAPI_MakeRevol(face, gp_Ax1(gp_Pnt(*o), gp_Dir(*a)), 2 * math.pi).Shape())
        faces += len(ring) - 1
    out = solids[0]
    for s in solids[1:]:
        fuse = BRepAlgoAPI_Fuse(out, s)
        fuse.Build()
        out = fuse.Shape()
    unify = ShapeUpgrade_UnifySameDomain(out, True, True, True)
    unify.Build()
    area = sum(p.area for p in polys)
    centroid_r = sum(p.area * p.centroid.y for p in polys) / area
    return unify.Shape(), {"method": f"revolution of the meridional section at {angle:g} deg about {list(o)} along {list(a)}", "cells": len(cells),
                           "regions": len(polys), "holes": sum(len(p.interiors) for p in polys), "section_segments": faces,
                           "pappus_volume": 2 * math.pi * centroid_r * area, "simplify_mm": REVOLVE_TOLERANCE}


def read_faces(path: Path) -> list[Any]:
    from OCP.IGESControl import IGESControl_Reader
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.TopAbs import TopAbs_FACE

    from opencad.geomcheck import brep

    r = IGESControl_Reader()
    if r.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"cannot read {path}")
    r.TransferRoots()
    return brep._explore(r.OneShape(), TopAbs_FACE)


def shells_at(faces: list[Any], tol: float) -> list[dict[str, Any]]:
    """Every shell the sewing closes at `tol`, as a repaired solid with its qualification."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing
    from OCP.ShapeFix import ShapeFix_Solid
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopoDS import TopoDS

    from opencad.geomcheck import brep
    from opencad.geomcheck.qualify import qualify, repair

    sew = BRepBuilderAPI_Sewing(tol)
    for f in faces:
        sew.Add(f)
    sew.Perform()
    out = []
    for k, sh in enumerate(brep._explore(sew.SewedShape(), TopAbs_SHELL)):
        fix = ShapeFix_Solid(BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(sh)).Solid())
        fix.Perform()
        solid, rec = repair(fix.Solid())
        q = qualify(solid)
        lo, hi = brep.bbox(solid)
        out.append({"index": k, "tolerance": tol, "solid": solid, "bbox": [*lo, *hi], "faces": q["faces"], "volumes": q["volumes"], "ok": q["ok"],
                    "problems": q["problems"], "steps": rec["steps"]})
    return out


def main(argv: list[str] | None = None) -> int:
    from opencad.backends.local import write_step
    from opencad.geomcheck import brep
    from opencad.io import sha256_file

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("iges", type=Path)
    p.add_argument("--list", action="store_true")
    p.add_argument("--tolerance", type=float, action="append", help="sewing tolerance(s), mm (default: the sweep)")
    p.add_argument("--body", action="append", default=[], help="name=xmin,ymin,zmin,xmax,ymax,zmax")
    p.add_argument("--revolve", action="append", default=[], help="name=ox,oy,oz,dx,dy,dz,angle: rebuild that body from its meridional section")
    p.add_argument("--out", type=Path)
    a = p.parse_args(argv)
    from opencad.geomcheck.qualify import qualify

    faces = read_faces(a.iges)
    print(f"{a.iges.name}: {len(faces)} faces", flush=True)
    wanted = {b.split("=", 1)[0]: [float(x) for x in b.split("=", 1)[1].split(",")] for b in a.body}
    revolve = {b.split("=", 1)[0]: [float(x) for x in b.split("=", 1)[1].split(",")] for b in a.revolve}
    best: dict[str, tuple[float, dict[str, Any]]] = {}
    for tol in a.tolerance or TOLERANCES:
        shells = shells_at(faces, tol)
        print(f"-- sewn at {tol:g} mm: {len(shells)} closed shells", flush=True)
        for s in shells:
            if a.list:
                print(f"  [{s['index']:3d}] bbox {[round(x, 1) for x in s['bbox']]} faces {s['faces']} volumes {[round(v, 1) for v in s['volumes']]} "
                      f"{'ok' if s['ok'] else 'FAIL ' + '; '.join(s['problems'])}" + (f" (repaired: {', '.join(s['steps'])})" if s["steps"] else ""))
            for name, box in wanted.items():
                err = max(abs(x - y) for x, y in zip(s["bbox"], box))
                if (s["ok"] or name in revolve) and err <= 1.0 and (name not in best or err < best[name][0] or (s["ok"] and not best[name][1]["ok"])):
                    best[name] = (err, s)
        if wanted and all(n in best and best[n][1]["ok"] for n in wanted):
            break
    done = True
    for name in wanted:
        if name not in best:
            print(f"{name}: no solid within 1 mm of the requested bbox")
            done = False
            continue
        err, s = best[name]
        solid, how = s["solid"], f"shell {s['index']} sewn at {s['tolerance']:g} mm (bbox within {err:.3f} mm)" + (f", repaired: {', '.join(s['steps'])}" if s["steps"] else "")
        if name in revolve:
            r = revolve[name]
            solid, rec = revolve_section(s["solid"], r[:3], r[3:6], r[6], snap=2 * s["tolerance"])
            how += (f"; {'valid' if s['ok'] else 'not valid (' + '; '.join(s['problems']) + ')'}, rebuilt as the {rec['method']} ({rec['regions']} regions, "
                    f"{rec['holes']} holes, {rec['section_segments']} segments, Pappus volume {rec['pappus_volume']:.1f} mm3)")
        q = qualify(solid)
        if not q["ok"]:
            print(f"{name}: {how}; still not valid: {'; '.join(q['problems'])}")
            done = False
            continue
        dest = a.out / f"{name}.step"
        dest.parent.mkdir(parents=True, exist_ok=True)
        write_step(solid, dest, name)
        back = qualify(brep.read_step(dest))  # what a reader of the file gets
        if not back["ok"]:
            print(f"{name}: {how}; the written STEP does not qualify: {'; '.join(back['problems'])}")
            done = False
            continue
        print(f"{name}: {how}; {back['faces']} faces, volume {back['volumes'][0]:.3f} mm3 -> {dest} sha256 {sha256_file(dest)}")
    return 0 if done else 1


if __name__ == "__main__":
    raise SystemExit(main())

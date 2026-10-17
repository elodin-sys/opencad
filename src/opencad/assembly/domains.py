"""Domains: fluid regions derived by boolean (capped box minus walls and inner bodies, the piece holding the seed), sealed and
compared with the source's fluid body; every face of a bounded body mapped to one named boundary, with per-patch STLs."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from opencad.assembly import AsmCtx
from opencad.geomcheck import brep

PAD_MM = 2.0
TOUCH_SAMPLES = 16
ANGLE_TOL_DEG = 1.0


def _compound(shapes: list[Any]):
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound

    comp = TopoDS_Compound()
    b = BRep_Builder()
    b.MakeCompound(comp)
    for s in shapes:
        b.Add(comp, s)
    return comp


def _half_space(point: list[float], normal: list[float]):
    """The solid half-space on the side opposite to `normal` (the fluid side of an outward cap normal)."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeHalfSpace
    from OCP.gp import gp_Dir, gp_Pln, gp_Pnt

    n = np.asarray(normal, float) / np.linalg.norm(normal)
    face = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(*point), gp_Dir(*n))).Face()
    ref = np.asarray(point, float) - n
    return BRepPrimAPI_MakeHalfSpace(face, gp_Pnt(*ref)).Solid()


def opening_radius(fluid: Any, point: list[float], normal: list[float], tol: float = 0.05) -> float | None:
    """How far the fluid body's planar face in the cap plane reaches from the cap point (None when no such face exists)."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Plane
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopoDS import TopoDS

    c, n = np.asarray(point, float), np.asarray(normal, float) / np.linalg.norm(normal)
    best = None
    for f in brep._explore(fluid, TopAbs_FACE):
        s = BRepAdaptor_Surface(TopoDS.Face_s(f))
        if s.GetType() != GeomAbs_Plane:
            continue
        pl = s.Plane()
        d, o = pl.Axis().Direction(), pl.Location()
        if abs(abs(d.X() * n[0] + d.Y() * n[1] + d.Z() * n[2]) - 1.0) > 1e-3 or abs((np.array([o.X(), o.Y(), o.Z()]) - c) @ n) > tol:
            continue
        lo, hi = brep.bbox(f)
        corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        r = float(np.max(np.linalg.norm(corners - c, axis=1)))
        best = r if best is None else min(best, r)
    return best


def _plug(point: list[float], normal: list[float], radius: float, height: float):
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    n = np.asarray(normal, float) / np.linalg.norm(normal)
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*point), gp_Dir(*n)), radius, height).Shape()


def derive_fluid(walls: list[Any], minus: list[Any], caps: list[Any], seed: list[float], fluid_body: Any = None) -> dict[str, Any]:
    """Padded box over the walls and the cap points minus walls and inner bodies, each port closed at its cap, and the piece holding the
    seed. A cap whose plane the fluid body crosses elsewhere gets a local plug just outside the plane (sized from the fluid body's face
    there); every other cap clips the half-space beyond its plane."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut

    from opencad.geomcheck.assembly import make_box

    lo, hi = brep.bbox(_compound(walls))
    # caps can bound the fluid beyond the walls (an open box around a duct)
    pts = [list(cap.point) for cap in caps]
    lo = [min([lo[i], *(p[i] for p in pts)]) - PAD_MM for i in range(3)]
    hi = [max([hi[i], *(p[i] for p in pts)]) + PAD_MM for i in range(3)]
    cut = BRepAlgoAPI_Cut(make_box(lo, hi), _compound([*walls, *minus]))
    cut.Build()
    if not cut.IsDone():
        return {"ok": False, "error": "walls/minus subtraction failed"}
    region = cut.Shape()
    for cap in caps:
        r = None
        if fluid_body is not None:
            flo, fhi = brep.bbox(fluid_body)
            corners = np.array([[x, y, z] for x in (flo[0], fhi[0]) for y in (flo[1], fhi[1]) for z in (flo[2], fhi[2])])
            n = np.asarray(cap.normal, float) / np.linalg.norm(cap.normal)
            if float(np.max((corners - np.asarray(cap.point, float)) @ n)) > PAD_MM:  # the fluid crosses this cap's plane elsewhere
                r = opening_radius(fluid_body, list(cap.point), list(cap.normal))
        # a plug touching the wall face must be cut on its own: a compound tool leaves the coplanar contact open
        op = (BRepAlgoAPI_Cut(region, _plug(list(cap.point), list(cap.normal), r + 1.0, PAD_MM)) if r is not None
              else BRepAlgoAPI_Common(region, _half_space(list(cap.point), list(cap.normal))))
        op.Build()
        if not op.IsDone():
            return {"ok": False, "error": f"cap {cap.name}: closing the port failed"}
        region = op.Shape()
    pieces = brep.solids(region)
    piece = next((s for s in pieces if brep.classify_points(s, [tuple(seed)])[0] == "in"), None)
    if piece is None:
        return {"ok": False, "error": f"no fluid piece contains the seed {list(seed)} ({len(pieces)} pieces)", "pieces": len(pieces)}
    plo, phi = brep.bbox(piece)
    leaks = [f"{'xyz'[i]}{'-' if k == 0 else '+'}" for i in range(3) for k, (a, b) in enumerate(((plo[i], lo[i]), (phi[i], hi[i]))) if abs(a - b) < 1e-3]
    vp = brep.volume_props(piece)
    return {"ok": not leaks, "sealed": not leaks, "leaks_to": leaks, "volume": vp["volume"], "surface_area": vp["surface_area"],
            "bbox_min": plo, "bbox_max": phi, "pieces": len(pieces), "shape": piece}


def _deviation(a: Any, b: Any) -> dict[str, Any]:
    import shutil
    import tempfile
    from pathlib import Path

    from opencad.backends.local import write_stl
    from opencad.geomcheck import mesh

    td = Path(tempfile.mkdtemp(prefix="opencad-fluid-"))
    try:
        write_stl(a, td / "a.stl")
        write_stl(b, td / "b.stl")
        dev = mesh.deviation(td / "a.stl", td / "b.stl", samples=20000)
        return {"p99": max(dev["candidate_to_reference"]["p99"], dev["reference_to_candidate"]["p99"]), "hausdorff_estimate": dev["hausdorff_estimate"]}
    finally:
        shutil.rmtree(td, ignore_errors=True)


def fluids(actx: AsmCtx, shapes: dict[str, Any]) -> dict[str, Any]:
    from opencad.backends.local import write_step

    out = {}
    for fv in actx.contract.fluid_volumes:
        missing = [b for b in [*fv.walls, *fv.minus] if b not in shapes]
        if missing:
            out[fv.name] = {"ok": False, "error": f"bodies missing from the export: {missing}"}
            continue
        d = derive_fluid([shapes[b] for b in fv.walls], [shapes[b] for b in fv.minus], fv.caps, list(fv.seed), shapes.get(fv.body) if fv.body else None)
        region = d.pop("shape", None)
        row: dict[str, Any] = dict(d)
        if region is not None:
            path = actx.results_dir / "export" / "bodies" / f"{fv.name}-derived.step"
            write_step(region, path, f"{fv.name}-derived")
            row["derived_step"] = str(path)
            if fv.volume is not None:
                ok, band = fv.volume.within(d["volume"])
                row["volume_check"] = {"measured": d["volume"], "expected": fv.volume.expected, "band": band, "ok": ok}
            if fv.body is not None:
                body = shapes.get(fv.body)
                if body is None:
                    row["agreement"] = {"ok": False, "error": f"fluid body {fv.body} missing from the export"}
                else:
                    bv = brep.volume_props(body)["volume"]
                    dev = _deviation(body, region)
                    # p99 each way: a boolean-derived region keeps zero-volume fins where faces touch coplanar (a shaft end on a wall)
                    row["agreement"] = {"body": fv.body, "volume_body": bv, "volume_derived": d["volume"], "volume_rel": abs(bv - d["volume"]) / d["volume"],
                                        "deviation_p99_mm": dev["p99"], "hausdorff_mm": dev["hausdorff_estimate"], "hausdorff_max_mm": fv.hausdorff_max,
                                        "ok": dev["p99"] <= fv.hausdorff_max}
        row["ok"] = bool(row.get("ok")) and (row.get("volume_check") or {}).get("ok", True) and (row.get("agreement") or {}).get("ok", True)
        out[fv.name] = row
    return out


def face_table(shape: Any) -> list[dict[str, Any]]:
    """Every face with its type, area, centroid, outward normal (planes) or axis and radius (cylinders)."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepGProp import BRepGProp
    from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane
    from OCP.GProp import GProp_GProps
    from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    rows = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    i = 0
    while exp.More():
        f = TopoDS.Face_s(exp.Current())
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(f, props)
        c = props.CentreOfMass()
        row: dict[str, Any] = {"id": i, "area": float(props.Mass()), "centroid": [c.X(), c.Y(), c.Z()], "type": "other", "face": f}
        s = BRepAdaptor_Surface(f)
        if s.GetType() == GeomAbs_Plane:
            d = s.Plane().Axis().Direction()
            n = np.array([d.X(), d.Y(), d.Z()])
            row.update(type="plane", normal=(-n if f.Orientation() == TopAbs_REVERSED else n).tolist())
        elif s.GetType() == GeomAbs_Cylinder:
            cyl = s.Cylinder()
            ax = cyl.Axis()
            row.update(type="cylinder", axis_point=[ax.Location().X(), ax.Location().Y(), ax.Location().Z()],
                       axis_dir=[ax.Direction().X(), ax.Direction().Y(), ax.Direction().Z()], radius=float(cyl.Radius()))
        rows.append(row)
        i += 1
        exp.Next()
    return rows


def _face_points(face: Any, limit: int = TOUCH_SAMPLES) -> list[np.ndarray]:
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopLoc import TopLoc_Location

    BRepMesh_IncrementalMesh(face, 0.2, False, 0.5, True)
    loc = TopLoc_Location()
    tri = BRep_Tool.Triangulation_s(face, loc)
    if tri is None:
        return []
    trsf = loc.Transformation()
    pts = []
    n = tri.NbTriangles()
    for k in np.linspace(1, n, min(limit, n)).astype(int):
        a, b, c = tri.Triangle(int(k)).Get()
        p = [tri.Node(x).Transformed(trsf) for x in (a, b, c)]
        pts.append(np.mean([[q.X(), q.Y(), q.Z()] for q in p], axis=0))
    return pts


def _touches(face: Any, other: Any, tol: float) -> bool:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.gp import gp_Pnt

    pts = _face_points(face)
    if not pts:
        return False
    for p in pts:
        d = BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex(), other)
        d.Perform()
        if not d.IsDone() or d.Value() > tol:
            return False
    return True


def _selects(b: Any, row: dict[str, Any], shapes: dict[str, Any]) -> bool:
    cos_tol = math.cos(math.radians(ANGLE_TOL_DEG))
    if b.select == "plane":
        if row["type"] != "plane":
            return False
        n = np.asarray(b.normal, float) / np.linalg.norm(b.normal)
        return float(np.dot(row["normal"], n)) >= cos_tol and abs(float(np.dot(np.subtract(row["centroid"], b.point), n))) <= b.tolerance
    if b.select == "cylinder":
        if row["type"] != "cylinder":
            return False
        d = np.asarray(b.direction, float) / np.linalg.norm(b.direction)
        if abs(float(np.dot(row["axis_dir"], d))) < cos_tol or abs(row["radius"] - float(b.radius)) > b.tolerance:
            return False
        w = np.subtract(b.point, row["axis_point"])
        return float(np.linalg.norm(w - np.dot(w, d) * d)) <= b.tolerance
    if b.select == "region":
        lo, hi = b.region
        return all(l - 1e-9 <= x <= h + 1e-9 for x, l, h in zip(row["centroid"], lo, hi))
    if b.select == "touching":
        other = shapes.get(b.touching)
        return other is not None and _touches(row["face"], other, b.tolerance)
    return False


def boundaries(actx: AsmCtx, shapes: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    by_body: dict[str, list[Any]] = {}
    for b in actx.contract.boundaries:
        by_body.setdefault(b.body, []).append(b)
    for body, specs in by_body.items():
        shape = shapes.get(body)
        if shape is None:
            out[body] = {"ok": False, "error": f"{body} missing from the export"}
            continue
        rows = face_table(shape)
        claims: dict[int, list[str]] = {}
        for b in [s for s in specs if s.select != "rest"]:
            for row in rows:
                if _selects(b, row, shapes):
                    claims.setdefault(row["id"], []).append(b.name)
        rest = [s for s in specs if s.select == "rest"]
        for row in rows:
            if row["id"] not in claims and rest:
                claims[row["id"]] = [rest[0].name]
        labels = {}
        for b in specs:
            ids = [i for i, names in claims.items() if b.name in names]
            area = sum(rows[i]["area"] for i in ids)
            lab: dict[str, Any] = {"role": b.role, "faces": sorted(ids), "area": area, "ok": bool(ids)}
            if b.area is not None:
                ok, band = b.area.within(area)
                lab["area_check"] = {"measured": area, "expected": b.area.expected, "band": band, "ok": ok}
                lab["ok"] = lab["ok"] and ok
            labels[b.name] = lab
        unassigned = [r["id"] for r in rows if r["id"] not in claims]
        conflicts = {i: names for i, names in claims.items() if len(names) > 1}
        out[body] = {"faces": [{k: v for k, v in r.items() if k != "face"} | {"label": (claims.get(r["id"]) or [None])[0]} for r in rows],
                     "labels": labels, "unassigned": unassigned, "conflicts": conflicts,
                     "ok": not unassigned and not conflicts and all(v["ok"] for v in labels.values())}
        write_patches(actx.results_dir / "boundaries" / f"{body}.stl", rows, claims)
    return out


def write_patches(path: Path, rows: list[dict[str, Any]], claims: dict[int, list[str]]) -> Path:
    """One ASCII STL with a `solid <label>` block per boundary (snappyHexMesh regions); triangles follow each face's orientation."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_REVERSED
    from OCP.TopLoc import TopLoc_Location

    groups: dict[str, list[str]] = {}
    for row in rows:
        label = (claims.get(row["id"]) or ["unassigned"])[0]
        f = row["face"]
        BRepMesh_IncrementalMesh(f, 0.05, False, 0.3, True)
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f, loc)
        if tri is None:
            continue
        trsf = loc.Transformation()
        rev = f.Orientation() == TopAbs_REVERSED
        lines = groups.setdefault(label, [])
        for k in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(k).Get()
            if rev:
                b, c = c, b
            p = [np.array([q.X(), q.Y(), q.Z()]) for q in (tri.Node(x).Transformed(trsf) for x in (a, b, c))]
            n = np.cross(p[1] - p[0], p[2] - p[0])
            n = n / (np.linalg.norm(n) or 1.0)
            lines.append(f"  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n    outer loop\n" + "".join(f"      vertex {v[0]:.6e} {v[1]:.6e} {v[2]:.6e}\n" for v in p)
                         + "    endloop\n  endfacet\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"solid {label}\n{''.join(tris)}endsolid {label}\n" for label, tris in groups.items()), encoding="utf-8")
    return path


def run(actx: AsmCtx) -> dict[str, Any]:
    shapes = {}
    for p in actx.contract.parts:
        f = actx.placed_step(p.name)
        if f.exists():
            shapes[p.name] = brep.read_step(f)
    fl = fluids(actx, shapes)
    for fv in actx.contract.fluid_volumes:
        if fv.body is None and fl.get(fv.name, {}).get("derived_step"):
            shapes[fv.name] = brep.read_step(Path(fl[fv.name]["derived_step"]))
    bd = boundaries(actx, shapes)
    applicable = bool(actx.contract.fluid_volumes or actx.contract.boundaries)
    return {"ok": all(v.get("ok") for v in fl.values()) and all(v.get("ok") for v in bd.values()), "applicable": applicable, "fluids": fl, "boundaries": bd}

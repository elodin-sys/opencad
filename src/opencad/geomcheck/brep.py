"""STEP B-rep inspection with OpenCascade via OCP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from OCP.Bnd import Bnd_Box
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Section
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepGProp import BRepGProp
from OCP.BRepTools import BRepTools
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane
from OCP.gp import gp_Dir, gp_Pln, gp_Pnt
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_IN, TopAbs_ON, TopAbs_REVERSED, TopAbs_SOLID, TopAbs_WIRE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS, TopoDS_Shape


class BrepError(RuntimeError):
    pass


def read_step(path: Path) -> TopoDS_Shape:
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone:
        raise BrepError(f"STEP read failed for {path} (status {status})")
    reader.TransferRoots()
    shape = reader.OneShape()
    if shape.IsNull():
        raise BrepError(f"STEP {path} contains no shape")
    return shape


def _explore(shape: TopoDS_Shape, kind) -> list:
    out = []
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        out.append(exp.Current())
        exp.Next()
    return out


def solids(shape: TopoDS_Shape) -> list:
    return [TopoDS.Solid(s) for s in _explore(shape, TopAbs_SOLID)]


def match_solids(shape: TopoDS_Shape, targets: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Greedy assignment of solids to named targets by centre-of-mass, preferring volume within 5 %."""
    sols = solids(shape)
    props = [volume_props(s) for s in sols]
    used: set[int] = set()
    out: dict[str, dict[str, Any]] = {}
    for name, target in targets.items():
        want_v = target.get("volume")
        want_com = target.get("com") or target.get("center_of_mass")
        best_i, best_d = None, 1e18
        for i, p in enumerate(props):
            if i in used:
                continue
            if want_v and abs(p["volume"] - float(want_v)) / max(float(want_v), 1e-9) > 0.05:
                continue
            if want_com is None:
                d = 0.0
            else:
                d = sum((a - b) ** 2 for a, b in zip(p["center_of_mass"], want_com)) ** 0.5
            if d < best_d:
                best_i, best_d = i, d
        if best_i is None:
            out[name] = {"ok": False, "error": "no matching solid"}
            continue
        used.add(best_i)
        out[name] = {"ok": True, "solid": sols[best_i], "com_error_mm": best_d, **props[best_i]}
    return out


def volume_props(shape: TopoDS_Shape) -> dict[str, Any]:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props, 1e-7)
    com = props.CentreOfMass()
    sprops = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, sprops, 1e-7)
    inertia = props.MatrixOfInertia()
    return {
        "volume": float(props.Mass()),
        "surface_area": float(sprops.Mass()),
        "center_of_mass": [com.X(), com.Y(), com.Z()],
        "inertia_about_com": [[inertia.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)],
    }


def bbox(shape: TopoDS_Shape) -> tuple[list[float], list[float]]:
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box, False, False)
    lo, hi = box.CornerMin(), box.CornerMax()
    return [lo.X(), lo.Y(), lo.Z()], [hi.X(), hi.Y(), hi.Z()]


def planar_faces(shape: TopoDS_Shape) -> list[dict[str, Any]]:
    """Every planar face: outward normal (orientation-corrected), a point on the plane, area, bounds."""
    out = []
    for f in _explore(shape, TopAbs_FACE):
        face = TopoDS.Face(f)
        ad = BRepAdaptor_Surface(face)
        if ad.GetType() != GeomAbs_Plane:
            continue
        pln = ad.Plane()
        n = pln.Axis().Direction()
        nx, ny, nz = n.X(), n.Y(), n.Z()
        if face.Orientation() == TopAbs_REVERSED:
            nx, ny, nz = -nx, -ny, -nz
        p = pln.Location()
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(face, props)
        lo, hi = bbox(face)
        c = props.CentreOfMass()
        out.append({
            "normal": [nx, ny, nz], "point": [p.X(), p.Y(), p.Z()], "area": float(props.Mass()),
            "bbox_min": lo, "bbox_max": hi, "centroid": [c.X(), c.Y(), c.Z()],
        })
    return out


def find_face(faces: list[dict[str, Any]], axis: str, at: float, sign: str, tol: float) -> list[dict[str, Any]]:
    i = "xyz".index(axis)
    want = 1.0 if sign == "+" else -1.0
    hits = []
    for f in faces:
        n = f["normal"]
        pos = (f.get("centroid") or f["point"])[i]
        if abs(n[i] - want) < 1e-6 and all(abs(n[j]) < 1e-6 for j in range(3) if j != i) and abs(pos - at) <= tol:
            hits.append(f)
    return hits


def find_face_normal(faces: list[dict[str, Any]], normal: list[float], point: list[float], tol: float, angle_tol_deg: float = 0.5) -> list[dict[str, Any]]:
    """Planar faces whose outward normal matches `normal` and whose plane passes within `tol` of `point` (inclined planes)."""
    import math

    n0 = _unit(normal)
    cos_tol = math.cos(math.radians(angle_tol_deg))
    hits = []
    for f in faces:
        n = f["normal"]
        if sum(a * b for a, b in zip(n, n0)) < cos_tol:
            continue
        # signed distance from `point` to the face plane
        d = sum((a - b) * c for a, b, c in zip(point, f["point"], n))
        if abs(d) <= tol:
            hits.append(f)
    return hits


def _unit(v: list[float]) -> list[float]:
    n = sum(x * x for x in v) ** 0.5
    return [x / n for x in v] if n else list(v)


def _canonical_axis(loc, direction) -> tuple[list[float], list[float]]:
    """Axis as (point closest to the origin, unit direction with the first non-zero component positive)."""
    d = _unit([direction.X(), direction.Y(), direction.Z()])
    for x in d:
        if abs(x) > 1e-9:
            if x < 0:
                d = [-y for y in d]
            break
    p = [loc.X(), loc.Y(), loc.Z()]
    t = sum(a * b for a, b in zip(p, d))
    p0 = [a - t * b for a, b in zip(p, d)]
    return p0, d


def cylinders(shape: TopoDS_Shape, merge_tol: float = 1e-4, gap_tol: float = 1e-3) -> list[dict[str, Any]]:
    """Cylindrical faces merged into axes: point, direction, radius, extent along the axis, hole (concave) or pin (convex).

    A face whose outward normal points away from the axis is convex (pin, boss, shaft); one whose
    outward normal points toward the axis is concave (hole, bore). Split faces (two halves of one
    hole) are merged when coaxial with the same radius and touching along the axis; coaxial faces
    separated by more than `gap_tol` along the axis (two blind bores from opposite edges, a waisted
    hub) stay separate features.
    """
    import math

    groups: dict[tuple, list[dict[str, Any]]] = {}
    # merge within one solid only: a bore in one body over a coaxial hole in another body are two features
    bodies = solids(shape) or [shape]
    for si, body in enumerate(bodies):
        for f in _explore(body, TopAbs_FACE):
            face = TopoDS.Face(f)
            ad = BRepAdaptor_Surface(face)
            if ad.GetType() != GeomAbs_Cylinder:
                continue
            cyl = ad.Cylinder()
            p0, d = _canonical_axis(cyl.Axis().Location(), cyl.Axis().Direction())
            r = float(cyl.Radius())
            umin, umax, vmin, vmax = BRepTools.UVBounds_s(face)
            # the natural cylinder normal is radial-outward; a REVERSED face has material outside -> hole
            concave = face.Orientation() == TopAbs_REVERSED
            # v runs along the cylinder's own axis direction (which may be the flipped canonical d)
            axis_dir = cyl.Axis().Direction()
            sign = 1.0 if sum(a * b for a, b in zip([axis_dir.X(), axis_dir.Y(), axis_dir.Z()], d)) > 0 else -1.0
            loc = cyl.Axis().Location()
            t_loc = sum((a - b) * c for a, b, c in zip([loc.X(), loc.Y(), loc.Z()], p0, d))
            t0, t1 = sorted((t_loc + sign * vmin, t_loc + sign * vmax))
            key = (si, tuple(round(x / merge_tol) for x in p0), tuple(round(x / merge_tol) for x in d), round(r / merge_tol), concave)
            # split faces of one feature touch or overlap along the axis; two coaxial bores separated by material are two features
            segs = groups.setdefault(key, [])
            for g in segs:
                if t0 <= g["t_max"] + gap_tol and t1 >= g["t_min"] - gap_tol:
                    g["t_min"], g["t_max"] = min(g["t_min"], t0), max(g["t_max"], t1)
                    g["angular_span"] += float(umax - umin)
                    g["faces"] += 1
                    break
            else:
                segs.append({"point": p0, "direction": d, "radius": r, "kind": "hole" if concave else "pin", "t_min": t0, "t_max": t1,
                             "angular_span": float(umax - umin), "faces": 1, "solid_index": si})
    merged_all: list[dict[str, Any]] = []
    for segs in groups.values():
        segs.sort(key=lambda g: g["t_min"])
        merged: list[dict[str, Any]] = []
        for g in segs:  # a face added before its neighbour may bridge two earlier segments
            if merged and g["t_min"] <= merged[-1]["t_max"] + gap_tol:
                m = merged[-1]
                m["t_max"] = max(m["t_max"], g["t_max"])
                m["angular_span"] += g["angular_span"]
                m["faces"] += g["faces"]
            else:
                merged.append(g)
        merged_all.extend(merged)
    out = []
    for g in merged_all:
        g["length"] = g["t_max"] - g["t_min"]
        g["full"] = g["angular_span"] >= 2 * math.pi - 1e-3
        tc = 0.5 * (g["t_min"] + g["t_max"])
        g["center"] = [a + tc * b for a, b in zip(g["point"], g["direction"])]
        g["diameter"] = 2 * g["radius"]
        out.append(g)
    out.sort(key=lambda g: (g["kind"], -g["radius"], tuple(round(c, 3) for c in g["center"])))
    return out


def axis_distance(point_a: list[float], dir_a: list[float], point_b: list[float], dir_b: list[float]) -> tuple[float, float]:
    """(perpendicular offset between two nearly parallel axes, angle between them in degrees)."""
    import math

    da, db = _unit(dir_a), _unit(dir_b)
    cosang = min(1.0, abs(sum(a * b for a, b in zip(da, db))))
    ang = math.degrees(math.acos(cosang))
    w = [a - b for a, b in zip(point_b, point_a)]
    t = sum(a * b for a, b in zip(w, da))
    perp = [a - t * b for a, b in zip(w, da)]
    return float(sum(x * x for x in perp) ** 0.5), float(ang)


def _union_segments(segs: list[dict[str, Any]]) -> dict[str, Any]:
    """One measured cylinder spanning coaxial segments (a bore interrupted by a slot, a shaft interrupted by a groove)."""
    base = segs[0]
    t_min = min(s["t_min"] for s in segs)
    t_max = max(s["t_max"] for s in segs)
    tc = 0.5 * (t_min + t_max)
    return {**base, "t_min": t_min, "t_max": t_max, "length": t_max - t_min, "faces": sum(s["faces"] for s in segs),
            "angular_span": max(s["angular_span"] for s in segs), "full": all(s["full"] for s in segs),
            "center": [a + tc * b for a, b in zip(base["point"], base["direction"])], "segments": len(segs),
            "gaps": [round(b["t_min"] - a["t_max"], 4) for a, b in zip(segs, segs[1:])]}


def match_cylinder(cyls: list[dict[str, Any]], point: list[float], direction: list[float], radius: float, *, kind: str = "any",
                   axis_tol: float, radius_tol: float, angle_tol_deg: float = 0.5, t_range: tuple[float, float] | None = None,
                   length: float | None = None) -> dict[str, Any]:
    """Best measured cylinder for a spec: right kind, radius within band, then smallest axis offset; among coaxial
    candidates (stacked bores, a bore over a hole in another body) prefer the one whose extent contains the spec point.

    `cyls` are gap-aware segments. A spec whose `length` (or `t_range`) spans several coaxial segments matches their
    union (a through bore crossing a slot, a hub OD interrupted by a groove); a spec matching one segment gets that
    segment (two blind bores from opposite edges stay two features).
    """
    d0 = _unit(direction)
    matched: list[tuple[dict[str, Any], float, float]] = []
    for c in cyls:
        if kind != "any" and c["kind"] != kind:
            continue
        if abs(c["radius"] - radius) > radius_tol:
            continue
        off, ang = axis_distance(point, d0, c["point"], c["direction"])
        if ang > angle_tol_deg or off > max(axis_tol * 4, 1.0):
            continue
        matched.append((c, off, ang))
    if not matched:
        return {"found": False, "ok": False, "axis_offset": None, "radius_error": None}
    # coaxial groups (same measured axis) -> singles plus every run of consecutive segments
    groups: dict[tuple, list[tuple[dict[str, Any], float, float]]] = {}
    for c, off, ang in matched:
        key = (tuple(round(x, 3) for x in c["point"]), tuple(round(x, 3) for x in c["direction"]), c["kind"], c.get("solid_index"))
        groups.setdefault(key, []).append((c, off, ang))
    candidates: list[tuple[dict[str, Any], float, float]] = []
    for grp in groups.values():
        grp.sort(key=lambda x: x[0]["t_min"])
        candidates.extend(grp)
        n = len(grp)
        for i in range(n):
            for j in range(i + 2, n + 1):
                run = [g[0] for g in grp[i:j]]
                candidates.append((_union_segments(run), grp[i][1], grp[i][2]))
    best: dict[str, Any] | None = None
    best_key: tuple | None = None
    for c, off, ang in candidates:
        if t_range is not None:
            t_spec = [sum((a + t * b - q) * e for a, b, q, e in zip(point, d0, c["point"], c["direction"])) for t in t_range]
            lo, hi = min(t_spec), max(t_spec)
            if hi < c["t_min"] - axis_tol or lo > c["t_max"] + axis_tol:
                continue
        t_point = sum((a - q) * e for a, q, e in zip(point, c["point"], c["direction"]))
        contains = c["t_min"] - axis_tol <= t_point <= c["t_max"] + axis_tol
        length_err = abs(c["length"] - length) if length is not None else 0.0
        cand = {"measured": c, "axis_offset": off, "angle_deg": ang, "radius_error": c["radius"] - radius}
        # a union is only preferred when the spec's length says the feature spans the gap
        key = (0 if off <= axis_tol else 1, 0 if contains else 1, round(length_err, 6), c.get("segments", 1), off)
        if best is None or key < best_key:
            best, best_key = cand, key
    if best is None:
        return {"found": False, "ok": False, "axis_offset": None, "radius_error": None}
    best.update({"found": True, "ok": best["axis_offset"] <= axis_tol})
    return best


def classify_points(shape: TopoDS_Shape, points: list[tuple[float, float, float]], tol: float = 1e-6) -> list[str]:
    """'in' | 'out' | 'on' for each point, against the union of all solids."""
    sols = solids(shape) or [shape]
    out = []
    for x, y, z in points:
        state = "out"
        for s in sols:
            clf = BRepClass3d_SolidClassifier(s, gp_Pnt(x, y, z), tol)
            st = clf.State()
            if st == TopAbs_IN:
                state = "in"
                break
            if st == TopAbs_ON:
                state = "on"
        out.append(state)
    return out


def _regions_from_faces(faces: list) -> tuple[list[dict[str, Any]], float, int]:
    regions = []
    total = 0.0
    holes = 0
    for f in faces:
        face = TopoDS.Face(f)
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(face, props)
        area = float(props.Mass())
        wires = _explore(face, TopAbs_WIRE)
        nh = max(0, len(wires) - 1)
        holes += nh
        lo, hi = bbox(face)
        c = props.CentreOfMass()
        total += area
        regions.append({"area": area, "holes": nh, "bbox_min": lo, "bbox_max": hi, "centroid": [c.X(), c.Y(), c.Z()]})
    regions.sort(key=lambda r: (round(r["centroid"][0], 3), round(r["centroid"][1], 3), round(r["centroid"][2], 3)))
    return regions, total, holes


def _section_from_wires(shape: TopoDS_Shape, pln: gp_Pln) -> list:
    """Build planar faces from Section edges when Common is not done."""
    from OCP.ShapeAnalysis import ShapeAnalysis_FreeBounds

    sec = BRepAlgoAPI_Section(shape, pln)
    sec.Build()
    if not sec.IsDone():
        return []
    faces = []
    edges = _explore(sec.Shape(), TopAbs_EDGE)
    if edges:
        mw = BRepBuilderAPI_MakeWire()
        for e in edges:
            mw.Add(TopoDS.Edge(e))
        if mw.IsDone():
            maker = BRepBuilderAPI_MakeFace(pln, mw.Wire())
            if maker.IsDone():
                faces.append(maker.Face())
    if not faces:
        fb = ShapeAnalysis_FreeBounds(sec.Shape(), 1e-4, False)
        for w in _explore(fb.GetClosedWires(), TopAbs_WIRE):
            maker = BRepBuilderAPI_MakeFace(pln, TopoDS.Wire(w))
            if maker.IsDone():
                faces.append(maker.Face())
    return faces


def section(shape: TopoDS_Shape, axis: str, at: float, extent: float = 1e4) -> dict[str, Any]:
    """Exact planar cross-section: solid area, face (loop) count, hole count, per-region bounds."""
    i = "xyz".index(axis)
    origin = [0.0, 0.0, 0.0]
    origin[i] = at
    normal = [0.0, 0.0, 0.0]
    normal[i] = 1.0
    pln = gp_Pln(gp_Pnt(*origin), gp_Dir(*normal))
    plane_face = BRepBuilderAPI_MakeFace(pln, -extent, extent, -extent, extent).Face()
    common = BRepAlgoAPI_Common(shape, plane_face)
    common.Build()
    method = "common"
    if not common.IsDone():
        faces = _section_from_wires(shape, pln)
        method = "section-wires"
        if not faces:
            return {"plane": axis, "at": at, "ok": False, "error": "section boolean failed", "method": method}
    else:
        faces = _explore(common.Shape(), TopAbs_FACE)
    regions, total, holes = _regions_from_faces(faces)
    return {"plane": axis, "at": at, "ok": True, "area": total, "loops": len(regions), "holes": holes, "regions": regions, "method": method}


def analyze_step(path: Path) -> dict[str, Any]:
    shape = read_step(path)
    sols = solids(shape)
    valid = BRepCheck_Analyzer(shape).IsValid()
    props = volume_props(shape)
    lo, hi = bbox(shape)
    faces = _explore(shape, TopAbs_FACE)
    pf = planar_faces(shape)
    return {
        "solids": len(sols),
        "valid": bool(valid),
        "faces": len(faces),
        "planar_faces": len(pf),
        "bbox_min": lo,
        "bbox_max": hi,
        "bbox_size": [h - l for l, h in zip(lo, hi)],
        **props,
    }

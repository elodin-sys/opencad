"""Evaluate contract features, sections, and named faces against the exported STEP (exact) and STL."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from opencad.geomcheck import brep
from opencad.schemas import FaceSpec, PartContract, Section

_INPLANE = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}


def check_sections(shape, contract: PartContract) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for s in contract.acceptance.sections:
        r = brep.section(shape, s.plane, s.at)
        out[s.id] = evaluate_section(s, r)
    return out


def evaluate_section(s: Section, r: dict[str, Any]) -> dict[str, Any]:
    e = s.expect
    res: dict[str, Any] = {"plane": s.plane, "at": s.at, "measured": {k: r.get(k) for k in ("area", "loops", "holes")}, "regions": r.get("regions", []), "checks": {}}
    if not r.get("ok", False):
        res["ok"] = False
        res["error"] = r.get("error", "section failed")
        return res
    if e.area is not None:
        err = abs(r["area"] - e.area)
        res["checks"]["area"] = {"expected": e.area, "measured": r["area"], "ok": err <= e.area * e.area_tolerance_rel, "tolerance_rel": e.area_tolerance_rel}
    if e.loops is not None:
        res["checks"]["loops"] = {"expected": e.loops, "measured": r["loops"], "ok": r["loops"] == e.loops}
    if e.holes is not None:
        res["checks"]["holes"] = {"expected": e.holes, "measured": r["holes"], "ok": r["holes"] == e.holes}
    if e.islands_min is not None:
        res["checks"]["islands_min"] = {"expected": e.islands_min, "measured": r["loops"], "ok": r["loops"] >= e.islands_min}
    res["ok"] = all(c["ok"] for c in res["checks"].values())
    return res


def _face_uv(hit: dict[str, Any], plane: str) -> list[float]:
    u, v = _INPLANE[plane]
    c = hit.get("centroid")
    if c is None:
        lo, hi = hit["bbox_min"], hit["bbox_max"]
        c = [(a + b) / 2 for a, b in zip(lo, hi)]
    return [c[u], c[v]]


def _merge_halves(spec: FaceSpec, hits: list[dict[str, Any]], unused: set[int], plane: str, ctol: float) -> tuple[dict[str, Any], set[int]] | None:
    """Two or three coplanar hits whose areas sum to the spec's area (and whose area-weighted centroid matches its centre) form one face."""
    from itertools import combinations

    cand = sorted(unused)
    for k in (2, 3):
        for combo in combinations(cand, k):
            area = sum(hits[i]["area"] for i in combo)
            if abs(area - spec.area) > spec.area * spec.area_tolerance_rel:
                continue
            cx = sum(_face_uv(hits[i], plane)[0] * hits[i]["area"] for i in combo) / area
            cy = sum(_face_uv(hits[i], plane)[1] * hits[i]["area"] for i in combo) / area
            center = getattr(spec, "center", None)
            if center is not None and math.dist([cx, cy], list(center)) > ctol:
                continue
            xyz = [0.0, 0.0, 0.0]
            u, v = _INPLANE[plane]
            xyz[u], xyz[v] = cx, cy
            xyz["xyz".index(plane)] = sum((hits[i].get("centroid") or hits[i]["point"])["xyz".index(plane)] * hits[i]["area"] for i in combo) / area
            merged = {"area": area, "centroid": xyz, "point": xyz, "position": xyz["xyz".index(plane)], "normal": hits[combo[0]].get("normal")}
            return merged, set(combo)
    return None


def assign_coplanar(specs: list[FaceSpec], hits: list[dict[str, Any]], plane: str) -> dict[str, dict[str, Any]]:
    """One measured face per spec. Prefer an explicit in-plane center; otherwise match by area.

    Summing every hit on the plane is `mode: sum` and must be explicit — never the default on a busy plane.
    """
    unused = set(range(len(hits)))
    out: dict[str, dict[str, Any]] = {}
    for spec in specs:
        best_i, best = None, math.inf
        center = getattr(spec, "center", None)
        ctol = spec.tolerance or 0.2
        for i in unused:
            h = hits[i]
            if center is not None:
                # centre first; the relative area error breaks ties between concentric faces (a hub disc inside a flange annulus)
                score = math.dist(_face_uv(h, plane), list(center)) + (ctol * abs(h["area"] - spec.area) / spec.area if spec.area else 0.0)
            elif spec.area is not None:
                score = abs(h["area"] - spec.area)
            else:
                score = 0.0
            if score < best:
                best_i, best = i, score
        res: dict[str, Any] = {"plane": spec.plane, "at": spec.at, "normal": spec.normal, "found": 0, "area": 0.0, "ok": False}
        if best_i is None:
            out[spec.name] = res
            continue
        h = hits[best_i]
        if spec.area is not None and abs(h["area"] - spec.area) > spec.area * spec.area_tolerance_rel:
            # a 360-degree revolve exports one annulus as two half faces: their union is the face the contract names
            pair = _merge_halves(spec, hits, unused, plane, ctol)
            if pair is not None:
                h, used = pair
                unused -= used
                uv = _face_uv(h, plane)
                res.update({"position": h["position"], "merged_faces": len(used)})
                res["area_expected"] = spec.area
                res["area_ok"] = abs(h["area"] - spec.area) <= spec.area * spec.area_tolerance_rel
                ok = bool(res["area_ok"])
                if center is not None:
                    res["center_expected"] = list(center)
                    res["center_error"] = math.dist(uv, list(center))
                    ok = ok and res["center_error"] <= ctol
                res.update({"found": len(used), "area": h["area"], "centroid_uv": uv, "ok": ok})
                out[spec.name] = res
                continue
        unused.remove(best_i)
        uv = _face_uv(h, plane)
        res["position"] = (h.get("centroid") or h["point"])["xyz".index(plane)]
        ok = True
        if spec.area is not None:
            res["area_expected"] = spec.area
            res["area_ok"] = abs(h["area"] - spec.area) <= spec.area * spec.area_tolerance_rel
            ok = bool(res["area_ok"])
        if center is not None:
            res["center_expected"] = list(center)
            res["center_error"] = math.dist(uv, list(center))
            ok = ok and res["center_error"] <= (spec.tolerance or 0.2)
        res.update({"found": 1, "area": h["area"], "centroid_uv": uv, "ok": ok})
        out[spec.name] = res
    return out


def check_faces(shape, contract: PartContract) -> dict[str, dict[str, Any]]:
    faces = brep.planar_faces(shape)
    groups: dict[tuple[str, float, str], list[FaceSpec]] = defaultdict(list)
    for f in contract.acceptance.faces:
        groups[(f.plane, f.at, f.normal)].append(f)
    out: dict[str, dict[str, Any]] = {}
    for (plane, at, normal), specs in groups.items():
        tol = next((s.tolerance for s in specs if s.tolerance is not None), None) or contract.envelope.tolerance
        hits = brep.find_face(faces, plane, at, normal, tol)
        # a `sum` spec totals every hit on its plane whatever else is declared there (the scorer's mode); `one` specs share the hits
        for f in [s for s in specs if s.mode == "sum"]:
            area = sum(h["area"] for h in hits)
            res: dict[str, Any] = {"plane": f.plane, "at": f.at, "normal": f.normal, "found": len(hits), "area": area, "mode": "sum", "ok": len(hits) > 0}
            if hits:
                res["position"] = sum((h.get("centroid") or h["point"])["xyz".index(plane)] * h["area"] for h in hits) / area if area else hits[0]["point"]["xyz".index(plane)]
            if f.area is not None and hits:
                res["area_expected"] = f.area
                res["area_ok"] = abs(area - f.area) <= f.area * f.area_tolerance_rel
                res["ok"] = res["ok"] and res["area_ok"]
            out[f.name] = res
        ones = [s for s in specs if s.mode != "sum"]
        if ones:
            out.update(assign_coplanar(ones, hits, plane))
    return out


def check_cylinders(shape, contract: PartContract) -> dict[str, dict[str, Any]]:
    """Each CylinderSpec against the merged cylindrical faces of the STEP: axis offset, radius error, extent."""
    if not contract.acceptance.cylinders:
        return {}
    cyls = brep.cylinders(shape)
    out: dict[str, dict[str, Any]] = {}
    for spec in contract.acceptance.cylinders:
        axis_tol = spec.axis_tolerance or contract.envelope.tolerance
        r = brep.match_cylinder(cyls, list(spec.point), list(spec.direction), spec.r, kind=spec.kind, axis_tol=axis_tol,
                                radius_tol=spec.radius_tolerance, t_range=spec.t_range, length=spec.length)
        res: dict[str, Any] = {
            "kind": spec.kind, "point": list(spec.point), "direction": list(spec.direction), "radius_expected": spec.r,
            "found": bool(r.get("found")), "axis_offset": r.get("axis_offset"), "axis_tolerance": axis_tol,
            "radius_error": r.get("radius_error"), "checks": {},
        }
        if r.get("found"):
            m = r["measured"]
            res["measured"] = {k: m[k] for k in ("center", "direction", "radius", "length", "kind", "t_min", "t_max", "full")}
            if m.get("segments", 1) > 1:
                res["measured"]["segments"], res["measured"]["gaps"] = m["segments"], m["gaps"]
            res["checks"]["axis"] = {"max": axis_tol, "measured": r["axis_offset"], "ok": bool(r["ok"])}
            if spec.length is not None:
                res["checks"]["length"] = {"expected": spec.length, "measured": m["length"], "ok": abs(m["length"] - spec.length) <= spec.length_tolerance}
        else:
            res["checks"]["axis"] = {"max": axis_tol, "measured": None, "ok": False, "error": f"no {spec.kind} cylinder of radius {spec.r} within radius band {spec.radius_tolerance} near the axis"}
        res["ok"] = all(c["ok"] for c in res["checks"].values())
        out[spec.name] = res
    return out


def check_planes(shape, contract: PartContract) -> dict[str, dict[str, Any]]:
    if not contract.acceptance.planes:
        return {}
    faces = brep.planar_faces(shape)
    out: dict[str, dict[str, Any]] = {}
    for spec in contract.acceptance.planes:
        tol = spec.tolerance or contract.envelope.tolerance
        hits = brep.find_face_normal(faces, list(spec.normal), list(spec.point), tol, spec.angle_tolerance_deg)
        area = sum(h["area"] for h in hits)
        res: dict[str, Any] = {"point": list(spec.point), "normal": list(spec.normal), "found": len(hits), "area": area, "tolerance": tol, "ok": len(hits) > 0}
        if spec.area is not None and hits:
            res["area_expected"] = spec.area
            res["area_ok"] = abs(area - spec.area) <= spec.area * spec.area_tolerance_rel
            res["ok"] = res["ok"] and res["area_ok"]
        out[spec.name] = res
    return out


def check_dimensions(contract: PartContract, bbox_size: list[float], faces: dict[str, dict[str, Any]], planar: list[dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    """bbox extent along an axis, or the separation of two named faces (by their assigned centroids) along it."""
    out: dict[str, dict[str, Any]] = {}
    for d in contract.acceptance.dimensions:
        i = "xyz".index(d.axis)
        res: dict[str, Any] = {"axis": d.axis, "expected": d.expected, "between": list(d.between) if d.between else None}
        if d.between is None:
            meas = bbox_size[i]
        else:
            a, b = (faces.get(n) or {} for n in d.between)
            pa, pb = a.get("position"), b.get("position")
            if pa is None or pb is None:
                res.update({"measured": None, "ok": False, "error": "a named face was not found"})
                out[d.name] = res
                continue
            meas = abs(pa - pb)
        ok, band = d.within(meas)
        res.update({"measured": meas, "band": band, "ok": ok})
        out[d.name] = res
    return out


def check_features(shape, contract: PartContract, sections: dict[str, dict[str, Any]], faces: dict[str, dict[str, Any]], bbox_ok: bool,
                   cylinders: dict[str, dict[str, Any]] | None = None, planes: dict[str, dict[str, Any]] | None = None,
                   dimensions: dict[str, dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    cylinders, planes, dimensions = cylinders or {}, planes or {}, dimensions or {}
    out: dict[str, dict[str, Any]] = {}
    for feat in contract.features:
        checks = []
        for v in feat.verify:
            if v.method == "bbox":
                checks.append({"method": "bbox", "ok": bbox_ok})
            elif v.method in ("cylinder", "plane", "dimension"):
                table = {"cylinder": cylinders, "plane": planes, "dimension": dimensions}[v.method]
                name = getattr(v, v.method) or ""
                r = table.get(name, {"ok": False, "error": f"{v.method} not evaluated"})
                checks.append({"method": v.method, v.method: name, "ok": bool(r.get("ok")), "measured": r.get("measured"), "axis_offset": r.get("axis_offset"), "found": r.get("found")})
            elif v.method in ("void", "solid"):
                states = brep.classify_points(shape, [tuple(p) for p in v.points or []])
                want = "out" if v.method == "void" else "in"
                checks.append({"method": v.method, "points": v.points, "states": states, "ok": all(s == want for s in states), "note": v.note})
            elif v.method == "section":
                s = sections.get(v.section or "", {"ok": False, "error": "section not evaluated"})
                checks.append({"method": "section", "section": v.section, "ok": s.get("ok", False), "measured": s.get("measured")})
            elif v.method == "count":
                s = sections.get(v.section or "", {})
                loops = (s.get("measured") or {}).get("loops")
                checks.append({"method": "count", "section": v.section, "expected": v.count, "measured": loops, "ok": loops == v.count})
            elif v.method == "face":
                f = faces.get(v.face or "", {"ok": False})
                checks.append({"method": "face", "face": v.face, "ok": f.get("ok", False), "found": f.get("found")})
        ok = all(c["ok"] for c in checks) if checks else None
        out[feat.id] = {"kind": feat.kind, "optional": feat.optional, "checks": checks, "ok": ok, "verified": bool(checks)}
    return out

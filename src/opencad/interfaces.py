"""Measured state of the acceptance items pinned by must_not_change interfaces, and baseline comparison.

Used by the edit stage (a parameter edit must not move interfaces it does not drive) and by the
change-request stage (everything the request did not change must return to its baseline).
"""

from __future__ import annotations

from typing import Any

from pathlib import Path

from opencad.geomcheck import brep, features, mesh
from opencad.schemas import PartContract


def measure(shape, contract: PartContract, bbox_size: list[float], *, mesh_path: Path | None = None, step_path: Path | None = None) -> dict[str, dict[str, Any]]:
    sections = features.check_sections(shape, contract)
    faces = features.check_faces(shape, contract)
    cyls = features.check_cylinders(shape, contract)
    planes = features.check_planes(shape, contract)
    dims = features.check_dimensions(contract, bbox_size, faces)
    out: dict[str, dict[str, Any]] = {}
    for name in contract.interface_checks():
        for kind, table in (("section", sections), ("face", faces), ("cylinder", cyls), ("plane", planes), ("dimension", dims)):
            if name in table:
                r = table[name]
                out[name] = {"kind": kind, "ok": bool(r.get("ok")), **signature(kind, r)}
                break
    need = [s for s in contract.acceptance.symmetry if s.name in contract.interface_checks()]
    src: Path | object | None = None
    if need:
        if mesh_path and Path(mesh_path).exists():
            src = Path(mesh_path)
        elif step_path and Path(step_path).exists():
            from opencad import render

            src = render.load_mesh(Path(step_path))
    for spec in need:
        if src is None:
            out[spec.name] = {"kind": "symmetry", "ok": False, "error": "no mesh to measure"}
            continue
        r = mesh.mirror_deviation(src, spec.plane, spec.at)
        ok = r["max"] <= spec.max_deviation and r["p95"] <= spec.p95_deviation
        out[spec.name] = {"kind": "symmetry", "ok": ok, **signature("symmetry", r)}
    return out


def signature(kind: str, r: dict[str, Any]) -> dict[str, Any]:
    if kind == "cylinder":
        m = r.get("measured") or {}
        return {"center": m.get("center"), "radius": m.get("radius"), "length": m.get("length"), "direction": m.get("direction")}
    if kind == "face":
        return {"position": r.get("position"), "area": r.get("area"), "centroid_uv": r.get("centroid_uv")}
    if kind == "plane":
        return {"area": r.get("area"), "found": r.get("found")}
    if kind == "dimension":
        return {"measured": r.get("measured")}
    if kind == "section":
        m = r.get("measured") or {}
        return {"area": m.get("area"), "loops": m.get("loops"), "holes": m.get("holes")}
    if kind == "symmetry":
        return {"max": r.get("max"), "p95": r.get("p95"), "worst_point": r.get("worst_point")}
    return {}


def driven_items(contract: PartContract, parameter: str) -> set[str]:
    """Acceptance items verified by features that declare `parameter` among their drivers."""
    out: set[str] = set()
    for f in contract.features:
        if parameter in f.parameters:
            for v in f.verify:
                for k in ("face", "cylinder", "plane", "dimension", "section"):
                    if getattr(v, k, None):
                        out.add(getattr(v, k))
    return out


def present(kind: str, a: dict[str, Any] | None) -> bool:
    """Does the item still exist after a rebuild (whatever its values)? The edit test exempts driven items from their original values, not from existing."""
    if not a:
        return False
    if kind == "cylinder":
        return a.get("center") is not None
    if kind == "face":
        return bool(a.get("area")) and a.get("position") is not None
    if kind == "plane":
        return bool(a.get("found"))
    if kind == "dimension":
        return a.get("measured") is not None
    if kind == "section":
        return a.get("area") is not None
    if kind == "symmetry":
        return a.get("max") is not None
    return True


def declared(contract: PartContract) -> set[str]:
    """Names of the measurable acceptance items (sections, faces, cylinders, planes, dimensions, symmetry) the contract still declares."""
    a = contract.acceptance
    return {s.id for s in a.sections} | {x.name for table in (a.faces, a.cylinders, a.planes, a.dimensions, a.symmetry) for x in table}


def compare(baseline: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]], contract: PartContract, changed: set[str], *, mode: str = "ecr") -> dict[str, Any]:
    """Preserved items must match the baseline within the contract tolerances.

    `changed` items are judged by the (revised) contract in `ecr` mode: a revised item by its new spec, an item the
    request removed (no longer declared) is deleted as asked and has nothing to preserve. In `edit` mode the contract
    is not revised, so a driven item (a hole whose diameter is the edited parameter) is expected to leave its original
    values: it must still exist, its new signature is recorded, and only the undriven pinned items decide the verdict.
    """
    tol = contract.envelope.tolerance
    edit = mode == "edit"
    still_declared = declared(contract)
    pinned = set(contract.interface_checks())
    rows: dict[str, dict[str, Any]] = {}
    for name, b in baseline.items():
        a = after.get(name)
        row: dict[str, Any] = {"kind": b["kind"], "changed_by_request": name in changed}
        if name in changed and edit:
            # the edit is supposed to move this item; the test's own checks (volume, bbox, direction, solids) judge the effect
            row.update({"ok": True, "note": "driven by the edited parameter; exempt from preservation, judged by the edit test's expectations",
                        "after": {k: v for k, v in (a or {}).items() if k not in ("kind", "ok")}, "present_after": present(b["kind"], a)})
        elif name in changed and name not in still_declared:
            row.update({"ok": True, "note": "removed by the request; no longer in the revised contract, nothing to preserve"})
        elif name in changed:
            row.update({"ok": bool(a and a.get("ok")), "note": "revised by the request; judged by the revised contract"})
        elif not edit and a is None and name not in pinned:
            row.update({"ok": True, "note": "no longer pinned by a must_not_change interface in the revised contract; judged by the features gate"})
        elif edit and not b.get("ok"):
            row.update({"ok": True, "note": "not present at the baseline; nothing to preserve", "baseline_ok": False})
        elif a is None or (not edit and not a.get("ok")) or (edit and not present(b["kind"], a)):
            row.update({"ok": False, "note": "not found or failing after the change"})
        elif b["kind"] == "cylinder":
            spec = next(c for c in contract.acceptance.cylinders if c.name == name)
            off = brep.axis_distance(b["center"], b["direction"], a["center"], a["direction"])[0] if b.get("center") and a.get("center") else None
            dr = abs((a.get("radius") or 0) - (b.get("radius") or 0))
            dl = abs((a.get("length") or 0) - (b.get("length") or 0))
            # an edit elsewhere may lengthen or shorten a bore through the moved material; its axis and radius are the interface
            ok = off is not None and off <= (spec.axis_tolerance or tol) and dr <= spec.radius_tolerance and (edit or dl <= spec.length_tolerance)
            row.update({"axis_shift": off, "radius_change": dr, "length_change": dl, "ok": ok})
        elif b["kind"] == "face":
            spec = next(f for f in contract.acceptance.faces if f.name == name)
            dp = abs((a.get("position") or 0) - (b.get("position") or 0))
            da = abs((a.get("area") or 0) - (b.get("area") or 0)) / max(abs(b.get("area") or 1e-9), 1e-9)
            # a driven hole through a pinned face changes its area, not its position: the mating plane is the interface
            row.update({"position_shift": dp, "area_change_rel": da, "ok": dp <= (spec.tolerance or tol) and (edit or da <= spec.area_tolerance_rel)})
        elif b["kind"] == "section":
            spec = next(s for s in contract.acceptance.sections if s.id == name)
            da = abs((a.get("area") or 0) - (b.get("area") or 0)) / max(abs(b.get("area") or 1e-9), 1e-9)
            row.update({"area_change_rel": da, "ok": (edit or da <= spec.expect.area_tolerance_rel) and a.get("loops") == b.get("loops") and a.get("holes") == b.get("holes")})
        elif b["kind"] == "dimension":
            spec = next(d for d in contract.acceptance.dimensions if d.name == name)
            dm = abs((a.get("measured") or 0) - (b.get("measured") or 0))
            row.update({"change": dm, "ok": dm <= (spec.tolerance if spec.tolerance is not None else abs(spec.expected) * (spec.tolerance_rel or 0))})
        elif b["kind"] == "symmetry":
            spec = next(s for s in contract.acceptance.symmetry if s.name == name)
            mx, p95 = a.get("max"), a.get("p95")
            ok = mx is not None and mx <= spec.max_deviation and (p95 or 0) <= spec.p95_deviation
            row.update({"max": mx, "p95": p95, "ok": ok})
        else:
            row.update({"ok": True})
        rows[name] = row
    return {"ok": all(r["ok"] for r in rows.values()), "items": rows,
            "preserved": [n for n, r in rows.items() if not r["changed_by_request"]], "changed": sorted(changed)}

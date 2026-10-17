"""Contract-level multi-body and interior checks on an exported STEP/STL: named solids, hardware envelopes,
clearances, passages, wall thickness, cylinder counts, void/solid probes. Shared by the inspect stage and the truth scorer.

Specs are plain dicts (pydantic models are passed through `model_dump()`), so the same code judges a
PartContract acceptance block and a truth manifest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from opencad.geomcheck import assembly, brep


select_solid = assembly.select_solid


select_solid = assembly.select_solid


def _d(spec: Any) -> dict[str, Any]:
    return spec if isinstance(spec, dict) else spec.model_dump(mode="json")


def check_solids(shape, solids: list[Any]) -> dict[str, dict[str, Any]]:
    """Each SolidSelector: the solid containing `contains_point`, with its properties and optional volume band."""
    out: dict[str, dict[str, Any]] = {}
    for s in solids:
        s = _d(s)
        sol = assembly.select_solid(shape, list(s["contains_point"]))
        res: dict[str, Any] = {"contains_point": list(s["contains_point"]), "found": sol is not None, "ok": sol is not None}
        if sol is not None:
            res.update(assembly.solid_props(sol))
            vol = s.get("volume")
            if vol:
                exp = float(vol["expected"])
                band = vol.get("tolerance") if vol.get("tolerance") is not None else abs(exp) * float(vol.get("tolerance_rel") or 0)
                res["volume_check"] = {"expected": exp, "measured": res["volume"], "band": band, "ok": abs(res["volume"] - exp) <= band}
                res["ok"] = res["volume_check"]["ok"]
        out[s["name"]] = res
    return out


def build_hardware(hardware: list[Any], base_dir: Path | None = None) -> dict[str, Any]:
    """Evaluator-side envelopes: boxes, cylinders, or placed STEP files, with optional excluded cylinders (standoff rings)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut

    out: dict[str, Any] = {}
    for h in hardware:
        h = _d(h)
        kind = h["kind"]
        if kind == "box":
            shape = assembly.make_box(list(h["min"]), list(h["max"]))
        elif kind == "cylinder":
            shape = assembly.make_cylinder(list(h["point"]), list(h["direction"]), float(h["radius"]), float(h["length"]))
        elif kind == "step":
            p = Path(h["path"])
            if not p.is_absolute() and base_dir is not None:
                p = base_dir / p
            shape = assembly.load_placed(p, translate=h.get("translate"), scale=h.get("scale"))
        else:
            raise ValueError(f"hardware {h.get('name')}: unknown kind {kind}")
        for ex in h.get("exclude_cylinders") or []:
            tool = assembly.make_cylinder(list(ex["point"]), list(ex["direction"]), float(ex["radius"]), float(ex["length"]))
            shape = BRepAlgoAPI_Cut(shape, tool).Shape()
        out[h["name"]] = shape
    return out


def resolve_body(name: str, shape, solids_found: dict[str, Any], solids_specs: list[Any], hardware: dict[str, Any]):
    """`all` = the whole exported shape; a solid selector name; or a hardware envelope name."""
    if name == "all":
        return shape
    for s in solids_specs:
        s = _d(s)
        if s["name"] == name:
            return assembly.select_solid(shape, list(s["contains_point"]))
    if name in hardware:
        return hardware[name]
    raise KeyError(name)


def check_clearances(shape, clearances: list[Any], solids_specs: list[Any], hardware: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    solids_found = {}
    for c in clearances:
        c = _d(c)
        res: dict[str, Any] = {"a": c["a"], "b": c["b"], "min_gap": c.get("min_gap", 0.0), "max_gap": c.get("max_gap")}
        try:
            a = resolve_body(c["a"], shape, solids_found, solids_specs, hardware)
            b = resolve_body(c["b"], shape, solids_found, solids_specs, hardware)
        except KeyError as e:
            res.update({"ok": False, "error": f"unknown body {e}"})
            out[c["name"]] = res
            continue
        if a is None or b is None:
            res.update({"ok": False, "error": "a named solid was not found"})
            out[c["name"]] = res
            continue
        res.update(assembly.clearance(a, b, min_gap=float(c.get("min_gap", 0.0) or 0.0), max_gap=c.get("max_gap"), interference_tol=float(c.get("interference_tolerance", 1e-3))))
        out[c["name"]] = res
    return out


def check_passages(stl: Path | None, passages: list[Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in passages:
        p = _d(p)
        if stl is None or not Path(stl).exists():
            out[p["name"]] = {"ok": False, "error": "no STL to voxelize"}
            continue
        plugs = [(list(lo), list(hi)) for lo, hi in (p.get("plugs") or [])]
        r = assembly.passage(Path(stl), list(p["point_a"]), list(p["point_b"]), pitch=float(p.get("pitch", 0.5)), plugs=plugs or None,
                             seal_radius=p.get("seal_radius"), expect_connected=bool(p.get("expect_connected", True)))
        vol, vol_max = r.get("passage_volume"), r.get("passage_volume_max")
        if vol is not None and (p.get("volume_min") is not None or p.get("volume_max") is not None):
            lo, hi = p.get("volume_min"), p.get("volume_max")
            # the voxel count brackets the volume (void voxels .. plus the partly-void layer on the walls); a band must meet the bracket
            r["volume_check"] = {"measured": vol, "measured_max": vol_max, "min": lo, "max": hi,
                                 "ok": (lo is None or (vol_max if vol_max is not None else vol) >= lo) and (hi is None or vol <= hi)}
            r["ok"] = bool(r["ok"] and r["volume_check"]["ok"])
        out[p["name"]] = {k: v for k, v in r.items() if k != "grid"}
    return out


def check_thickness(stl: Path | None, specs: list[Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for t in specs:
        t = _d(t)
        if stl is None or not Path(stl).exists():
            out[t["name"]] = {"ok": False, "error": "no STL to sample"}
            continue
        region = tuple(t["region"]) if t.get("region") else None
        r = assembly.thickness(Path(stl), samples=int(t.get("samples", 6000)), region=region, max_thickness=t.get("max_thickness"), thin_below=float(t["min"]))
        stat = t.get("stat", "p05")
        if "error" in r:
            r["ok"] = False
        else:
            val = r[stat]
            # a wall built exactly at the minimum measures 3.0 - 6e-15 through the ray cast; 1 µm of slack is far below any tolerance in play
            r.update({"stat": stat, "measured": val, "min_required": t["min"], "ok": val >= float(t["min"]) - 1e-6})
        out[t["name"]] = r
    return out


def check_cylinder_counts(cyls: list[dict[str, Any]], specs: list[Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for s in specs:
        s = _d(s)
        rtol = float(s.get("radius_tolerance", 0.05))
        kind = s.get("kind", "any")
        hits = [c for c in cyls if abs(c["radius"] - float(s["radius"])) <= rtol and (kind == "any" or c["kind"] == kind)
                and (s.get("direction") is None or brep.axis_distance([0, 0, 0], list(s["direction"]), [0, 0, 0], c["direction"])[1] <= 0.5)
                and in_region(c["center"], s.get("region"))]
        n = len(hits)
        exp, lo = s.get("expected"), s.get("expected_min")
        ok = (exp is None or n == int(exp)) and (lo is None or n >= int(lo))
        out[s["name"]] = {"radius": s["radius"], "kind": kind, "expected": exp, "expected_min": lo, "measured": n, "centers": [h["center"] for h in hits], "ok": ok,
                          **({"region": [list(s["region"][0]), list(s["region"][1])]} if s.get("region") else {})}
    return out


def in_region(point: list[float], region: Any) -> bool:
    """True when `region` is None or the point lies inside the (min, max) box."""
    if not region:
        return True
    lo, hi = region
    return all(float(lo[i]) <= float(point[i]) <= float(hi[i]) for i in range(3))


def check_probes(shape, probes: list[Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in probes:
        p = _d(p)
        pts = [tuple(x) for x in p["points"]]
        states = brep.classify_points(shape, pts)
        want = "out" if p["state"] == "void" else "in"
        out[p["name"]] = {"state": p["state"], "points": [list(x) for x in pts], "states": states, "ok": all(s == want for s in states)}
    return out

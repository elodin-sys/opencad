"""inspect: independent OCP/trimesh checks on the exported STEP/STL, features, faces, deviation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from opencad import cache
from opencad.backends.local import lap_timer
from opencad.gates import mesh_watertight
from opencad.geomcheck import brep, features, gears, mesh, multibody
from opencad.orchestrator import Ctx, PipelineError
from opencad.schemas import PartContract
from opencad.stages.common import bbox_check, point_check, quantity_check


def run(ctx: Ctx) -> dict[str, Any]:
    exp = ctx.require_stage("export")
    ver = ctx.load_stage("verify") or {}
    c = ctx.contract
    step = Path(exp["files"].get("step", {}).get("path", ""))
    stl = Path(exp["files"].get("stl", {}).get("path", ""))
    if not step.exists():
        raise PipelineError("no STEP export to inspect")
    # the measurements depend only on the exported files, the contract and the engine volume verify recorded
    engine_vol_key = str((ver.get("analyze") or {}).get("volume_mm3")) + str((ver.get("engine") or {}).get("class"))
    ref_dir = ctx.design_dir / "reference"
    ref_files = sorted(ref_dir.glob("reference.*")) if ref_dir.exists() else []
    ck = cache.key("inspect", step, stl, ctx.contract_path, *ref_files, extra=engine_vol_key)
    hit = cache.get("inspect", ck)
    if hit is not None:
        hit["cached"] = True
        dev, own = hit.get("deviation") or {}, ctx.results_dir / "deviation-map.png"
        if dev.get("map"):  # the results dir, where the map lives, is cleaned on every restart
            dev["map"] = str(own) if own.exists() else mesh.deviation(stl, Path(dev["reference"]), map_path=own)["map"]
        ctx.write_stage("inspect", hit)
        print(f"inspect {'ok' if hit.get('ok') else 'FAILED'} (cached: unchanged STEP/STL/contract)")
        return hit
    out = measure(step, stl, c, ctx.design_dir, engine_vol=(ver.get("analyze") or {}).get("volume_mm3"), engine=ver.get("engine") or {},
                 engine_independent=ctx.backend.independent_of_evaluator, deviation_map=ctx.results_dir / "deviation-map.png")
    cache.put("inspect", ck, out)
    ctx.write_stage("inspect", out)
    _print(out)
    return out


def measure(step: Path, stl: Path | None, c: PartContract, design_dir: Path, *, engine_vol: float | None = None, kcl_vol: float | None = None, engine: dict[str, Any] | None = None, engine_independent: bool = True, symmetry_samples: int = 60000,
            deviation_map: Path | None = None) -> dict[str, Any]:
    """Every contract check on an exported STEP (+ STL): the same measurements the pipeline gates on, usable by the worker's local critic.
    `deviation_map` is where the reference deviation's signed map is drawn, when the bundle carries a reference."""
    engine = engine or {}
    if engine_vol is None:
        engine_vol = kcl_vol
    stl = Path(stl) if stl and str(stl) not in ("", ".") else Path("/nonexistent/no.stl")  # Path("") is the cwd and "exists"
    out: dict[str, Any] = {"step": str(step), "stl": str(stl) if stl.exists() else None}
    lap = lap_timer()

    shape = brep.read_step(step)
    out["brep"] = brep.analyze_step(step)
    out["bbox"] = bbox_check(c, out["brep"]["bbox_min"], out["brep"]["bbox_max"])
    out["volume"] = quantity_check(c.acceptance.volume, out["brep"]["volume"])
    out["surface_area"] = quantity_check(c.acceptance.surface_area, out["brep"]["surface_area"])
    out["center_of_mass"] = point_check(c.acceptance.center_of_mass, out["brep"]["center_of_mass"])
    out["solid_count"] = {"expected": c.acceptance.solid_count, "measured": out["brep"]["solids"], "ok": out["brep"]["solids"] == c.acceptance.solid_count}
    out["valid"] = out["brep"]["valid"]
    lap("brep")

    out["sections"] = features.check_sections(shape, c)
    lap("sections")
    out["faces"] = features.check_faces(shape, c)
    lap("faces")
    out["cylinders"] = features.check_cylinders(shape, c)
    lap("cylinders")
    out["planes"] = features.check_planes(shape, c)
    lap("planes")
    out["dimensions"] = features.check_dimensions(c, out["brep"]["bbox_size"], out["faces"])
    out["features"] = features.check_features(shape, c, out["sections"], out["faces"], out["bbox"]["ok"], out["cylinders"], out["planes"], out["dimensions"])
    lap("features")
    # multi-body and interior checks (Phase 3-5): named solids, hardware envelopes, clearances, passages, wall thickness, probes, counts, gears
    a = c.acceptance
    stl_path = stl if stl.exists() else None
    out["solids"] = multibody.check_solids(shape, a.solids)
    hw = multibody.build_hardware(a.hardware, base_dir=design_dir) if a.hardware else {}
    out["clearances"] = multibody.check_clearances(shape, a.clearances, a.solids, hw)
    lap("solids")
    out["passages"] = multibody.check_passages(stl_path, a.passages)
    lap("passages")
    out["thickness"] = multibody.check_thickness(stl_path, a.thickness)
    lap("thickness")
    out["probes"] = multibody.check_probes(shape, a.probes)
    lap("probes")
    all_cyls = brep.cylinders(shape) if a.cylinder_counts else []
    out["cylinder_counts"] = multibody.check_cylinder_counts(all_cyls, count_specs(a.cylinder_counts))
    out["gears"] = {}
    for g in a.gears:
        body = multibody.select_solid(shape, list(next(s for s in a.solids if s.name == g.solid).contains_point)) if g.solid else shape
        out["gears"][g.name] = gears.tooth_count(body, list(g.point), list(g.direction), g.at, g.module, g.teeth) if body is not None else {"ok": False, "error": "solid not found"}
    out["meshes"] = {}
    for ms in a.meshes:
        ba = multibody.select_solid(shape, list(next(s for s in a.solids if s.name == ms.a).contains_point))
        bb = multibody.select_solid(shape, list(next(s for s in a.solids if s.name == ms.b).contains_point))
        if ba is None or bb is None:
            out["meshes"][ms.name] = {"ok": False, "error": "a gear solid was not found"}
            continue
        r = gears.mesh_motion(ba, bb, (list(ms.axis_a[0]), list(ms.axis_a[1])), (list(ms.axis_b[0]), list(ms.axis_b[1])), ratio=ms.ratio, pitch_deg=ms.pitch_deg, steps=ms.steps, backlash_max=ms.backlash_max)
        out["meshes"][ms.name] = r
    lap("counts_gears")
    if stl.exists():
        out["mesh"] = mesh.analyze_mesh(stl)
    else:
        out["mesh"] = None
    lap("mesh")

    out["symmetry"] = {}
    if c.acceptance.symmetry:
        sym_src = mesh.step_tessellation(step)
        for spec in c.acceptance.symmetry:
            r = mesh.mirror_deviation(sym_src, spec.plane, spec.at, samples=symmetry_samples)
            ok = r["max"] <= spec.max_deviation and r["p95"] <= spec.p95_deviation
            out["symmetry"][spec.name] = {**r, "source": "fine STEP tessellation", "max_deviation": spec.max_deviation, "p95_deviation": spec.p95_deviation, "ok": ok}
        lap("symmetry")

    # the must_not_change interfaces, as the set of acceptance items they pin (preserved across edits and change requests)
    pinned = c.interface_checks()
    tables = (("section", out["sections"]), ("face", out["faces"]), ("cylinder", out["cylinders"]), ("plane", out["planes"]), ("dimension", out["dimensions"]),
              ("solid", out["solids"]), ("clearance", out["clearances"]), ("passage", out["passages"]), ("thickness", out["thickness"]), ("probe", out["probes"]),
              ("cylinder_count", out["cylinder_counts"]), ("gear", out["gears"]), ("mesh", out["meshes"]), ("symmetry", out["symmetry"]))
    lookup = {k: v for _, tbl in tables for k, v in tbl.items()}
    out["interfaces"] = {n: {"ok": bool((lookup.get(n) or {}).get("ok")), "kind": next((k for k, tbl in tables if n in tbl), None)} for n in pinned}

    from opencad.backends.base import is_program

    engine_class = engine.get("class")
    engine_missing = engine_vol is None or engine.get("status") == "missing"
    tol = c.acceptance.export_volume_tolerance_rel
    manifold = (out["mesh"] or {}).get("manifold_volume")
    agreement: dict[str, Any] = {
        "engine": engine_vol, "kcl": engine_vol, "step": out["brep"]["volume"], "stl": (out["mesh"] or {}).get("volume"),
        "tolerance_rel": tol, "engine_missing": engine_missing, "engine_class": engine_class,
        "engine_independent": engine_independent,
        # the Manifold kernel shares no code with OCCT or the modelling backend: the witness the shared-kernel arms lacked (disclosed, not gated)
        "manifold": manifold,
        "manifold_vs_step_rel": (abs(manifold - out["brep"]["volume"]) / out["brep"]["volume"]) if manifold and out["brep"]["volume"] else None,
    }
    ref = out["brep"]["volume"]
    rel = None if engine_missing else (abs(engine_vol - ref) / ref if engine_vol and ref else None)
    agreement["engine_vs_step_rel"] = rel
    agreement["kcl_vs_step_rel"] = rel
    agreement["stl_vs_step_rel"] = abs(agreement["stl"] - ref) / ref if agreement["stl"] and ref else None
    stl_ok = bool(agreement["stl_vs_step_rel"] is None or agreement["stl_vs_step_rel"] <= max(tol, 0.005))
    if is_program(engine_class):
        agreement["ok"] = False
    elif engine_missing:
        agreement["ok"] = bool(ref and stl_ok)
    else:
        agreement["ok"] = bool(ref and (rel is None or rel <= tol) and stl_ok)
    out["agreement"] = agreement

    # deviation against a reference mesh, when the bundle carries one
    ref_mesh = next((p for p in (design_dir / "reference").glob("reference.*") if p.suffix in (".ply", ".stl")), None) if (design_dir / "reference").exists() else None
    if ref_mesh and stl.exists():
        dev = mesh.deviation(stl, ref_mesh, map_path=deviation_map)
        d = c.acceptance.deviation
        checks = {}
        if d:
            for band in dev["bands"]:  # a band over the p95 limit is a failing item, so the correction loop sees the deviation move
                band["ok"] = band["n"] == 0 or band["p95"] <= d.p95_max
            checks["p95"] = {"max": d.p95_max, "measured": dev["p95"], "ok": dev["p95"] <= d.p95_max}
            if d.hausdorff_max is not None:
                checks["hausdorff"] = {"max": d.hausdorff_max, "measured": dev["hausdorff_estimate"], "ok": dev["hausdorff_estimate"] <= d.hausdorff_max}
            if d.silhouette_iou_min is not None:
                checks["silhouette_iou"] = {"min": d.silhouette_iou_min, "measured": dev["silhouette_iou_min"], "ok": dev["silhouette_iou_min"] >= d.silhouette_iou_min}
        out["deviation"] = {"reference": str(ref_mesh), **dev, "checks": checks, "declared": d is not None, "ok": all(x["ok"] for x in checks.values()) if checks else None}
    else:
        out["deviation"] = {"reference": None, "declared": c.acceptance.deviation is not None, "ok": None}

    lap("deviation")
    out["timings"] = lap.timings
    required_features_ok = all(f["ok"] is not False for f in out["features"].values() if not f["optional"])
    out["ok"] = bool(
        out["valid"] and out["solid_count"]["ok"] and out["bbox"]["ok"] and out["volume"]["ok"] and out["surface_area"]["ok"]
        and         out["center_of_mass"]["ok"] and all(s["ok"] for s in out["sections"].values()) and all(f["ok"] for f in out["faces"].values())
        and all(x["ok"] for x in out["cylinders"].values()) and all(x["ok"] for x in out["planes"].values()) and all(x["ok"] for x in out["dimensions"].values())
        and all(x["ok"] for k in ("solids", "clearances", "passages", "thickness", "probes", "cylinder_counts", "gears", "meshes", "symmetry") for x in out[k].values())
        and required_features_ok and out["agreement"]["ok"] and (out["deviation"]["ok"] is not False)
        # sealed cavities are extra STL shells (NIST L10: 1 solid, 6 components, 5 void shells); touching bodies are judged per shell
        and (out["mesh"] is None or (mesh_watertight(out["mesh"], c.acceptance.solid_count) and (out["mesh"]["components"] - out["mesh"].get("void_shells", 0)) == c.acceptance.solid_count))
    )
    return out


def count_specs(specs: list[Any]) -> list[dict[str, Any]]:
    """CylinderCountSpec rows for multibody.check_cylinder_counts, the region box included (it filters which axis centres count)."""
    return [{"name": s.name, "radius": s.r, "radius_tolerance": s.radius_tolerance, "kind": s.kind, "direction": list(s.direction) if s.direction else None,
             "region": [list(s.region[0]), list(s.region[1])] if s.region else None, "expected": s.expected, "expected_min": s.expected_min} for s in specs]


def _print(out: dict[str, Any]) -> None:
    b = out["brep"]
    agreement = out["agreement"]
    print(f"inspect {'ok' if out['ok'] else 'FAILED'}: STEP valid={b['valid']} solids={b['solids']} volume={b['volume']:.3f} "
          f"sections={sum(1 for s in out['sections'].values() if s['ok'])}/{len(out['sections'])} faces={sum(1 for f in out['faces'].values() if f['ok'])}/{len(out['faces'])} "
          f"cylinders={sum(1 for x in out['cylinders'].values() if x['ok'])}/{len(out['cylinders'])} planes={sum(1 for x in out['planes'].values() if x['ok'])}/{len(out['planes'])} "
          f"dimensions={sum(1 for x in out['dimensions'].values() if x['ok'])}/{len(out['dimensions'])} "
          + "".join(f"{k}={sum(1 for x in out[k].values() if x['ok'])}/{len(out[k])} " for k in ("solids", "clearances", "passages", "thickness", "probes", "cylinder_counts", "gears", "meshes", "symmetry") if out[k])
          + f"features={sum(1 for f in out['features'].values() if f['ok'])}/{len(out['features'])} agreement={agreement['ok']}"
          + (f" deviation p95={out['deviation']['p95']:.3f}" if out['deviation'].get('p95') is not None else ""))

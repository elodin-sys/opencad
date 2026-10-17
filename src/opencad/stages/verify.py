"""verify: source hygiene, format/lint, engine analyze against the contract.

Snapshots render locally from the exported STL after the gates (see `render_snapshots`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from opencad.backends.base import BillingError, EngineError
from opencad.backends.local import lap_timer
from opencad.orchestrator import Ctx, PipelineError
from opencad.stages.common import bbox_check, point_check, quantity_check

from opencad.render import DEFAULT_VIEWS

SNAPSHOT_ANGLES = DEFAULT_VIEWS


def run(ctx: Ctx) -> dict[str, Any]:
    if not ctx.entry.exists():
        raise PipelineError(f"{ctx.entry} missing; run the model stage first")
    c = ctx.contract
    lap = lap_timer()
    checked = ctx.backend.language.check(ctx.part_dir, c)
    lap("check")
    out: dict[str, Any] = {"source": str(ctx.entry), "kcl": str(ctx.entry), **checked}
    out["engine_note"] = "engine analyze: tessellated volume/area; bounding box may include internal cut-tool extents; authoritative values come from inspect.json (STEP)"
    missing = {"ok": None}
    from opencad.stages.export import shared_build

    try:
        b = shared_build(ctx)
        if b is not None and not b["ok"]:
            raise b["error"]
        a = b["analyze"] if b is not None else ctx.backend.engine.analyze(ctx.entry, density_kg_m3=c.density_kg_m3)
        out["engine"] = {"status": "ok", "class": "ok"}
        out["analyze"] = {k: a.get(k) for k in ("bbox_min", "bbox_max", "bbox_size", "com", "volume_mm3", "surface_area_mm2", "mass_g", "density_kg_m3", "seconds")}
        out["bbox"] = bbox_check(c, a["bbox_min"], a["bbox_max"])
        out["volume"] = quantity_check(c.acceptance.volume, a["volume_mm3"])
        out["surface_area"] = quantity_check(c.acceptance.surface_area, a["surface_area_mm2"])
        out["center_of_mass"] = point_check(c.acceptance.center_of_mass, a["com"])
        out["analyze_ok"] = True
    except BillingError:
        raise
    except EngineError as e:
        kind = e.kind or ctx.backend.engine.classify(e)
        out["engine"] = {"status": "missing", "class": kind, "error": str(e)[:3000], "guard": bool(getattr(e, "guard", False))}
        out["analyze_ok"] = False
        out["analyze_error"] = str(e)[:3000]
        out["bbox"] = dict(missing)
        out["volume"] = dict(missing)
        out["surface_area"] = dict(missing)
        out["center_of_mass"] = dict(missing)
    lap("analyze")
    out["timings"] = lap.timings
    out["snapshots"] = {"deferred": True}
    out["engine_checks_ok"] = bool(out["analyze_ok"] and out["bbox"].get("ok") and out["volume"].get("ok") and out["surface_area"].get("ok") and out["center_of_mass"].get("ok"))
    out["ok"] = bool(out["format"]["ok"] and out["lint"]["ok"] and out["hygiene"]["ok"])
    ctx.write_stage("verify", out)
    a = out.get("analyze", {})
    eng = out.get("engine") or {}
    print(f"verify {'ok' if out['ok'] else 'FAILED'}: source ok={out['ok']}; engine {eng.get('status')} class={eng.get('class')}; "
          f"bbox err {out['bbox'].get('max_error', out['bbox'].get('ok'))}, volume {a.get('volume_mm3', '?')} "
          f"(exp {c.acceptance.volume.expected if c.acceptance.volume else '-'}), com {a.get('com', '?')} [engine evidence; STEP is authoritative]; hygiene {out['hygiene']['ok']}, lint {out['lint']['ok']}, format {out['format']['ok']}")
    return out


def render_snapshots(ctx: Ctx, angles: tuple[str, ...] = SNAPSHOT_ANGLES, workers: int = 2) -> dict[str, str]:
    """Render the report views from the exported STL. Failures are recorded, never fatal."""
    from opencad import render

    ver = ctx.load_stage("verify") or {}
    exp = ctx.load_stage("export") or {}
    files = exp.get("files") or {}
    candidates = [Path(p) for p in ((files.get("stl") or {}).get("path"), (files.get("step") or {}).get("path")) if p]
    stl = next((p for p in candidates if p.is_file()), None)
    if stl is None:
        return ver.get("snapshots") or {}
    snap_dir = ctx.results_dir / "snapshots"
    try:
        snaps = render.render_snapshots(stl, snap_dir, angles, contract=ctx.contract)
        refs = render.reference_renders(ctx.design_dir / "sources")
        if refs:  # the arm's input renders beside the part's views, plus a framing-independent silhouette agreement per view
            cmp = render.compare_sheet(snap_dir, refs, snap_dir / "view-compare.png")
            if cmp:
                snaps["compare"] = str(cmp)
            snaps["reference_silhouette"] = render.reference_silhouettes(snap_dir, refs)
    except Exception as e:
        snaps = {"error": str(e)[:500], "class": ctx.backend.engine.classify(e)}
    ver["snapshots"] = snaps
    ctx.write_stage("verify", {k: v for k, v in ver.items() if k not in ("provenance", "stage")}, ledger_prefix=ver.get("engine_calls") or [])
    n = len([k for k in snaps if k in angles])
    print(f"snapshots: {n}/{len(angles)} rendered from {stl.name}" + (f"; error {snaps.get('error')}" if snaps.get("error") else ""))
    return snaps

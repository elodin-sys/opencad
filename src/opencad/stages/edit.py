"""edit: rebuild with each declared parameter edit in a temp copy; confirm the effect; baseline STEP hash unchanged.

Edited copies are exported to STEP and measured with OpenCascade (exact), not with the
tessellated engine analysis, so small deltas are not lost in tessellation noise.

Three kinds of evidence per parameter:
- the primary delta (expected volume/bbox effect) plus interface preservation: pinned interface
  items that this parameter does not drive must not move;
- an optional sweep (regeneration over a declared range, no agent): every value must rebuild a
  valid part with the right solid count, keep the undriven interfaces, and scale its bbox/volume
  consistently with the declared expectation;
- optional infeasible deltas: the KCL must refuse them with an assert (a kcl-class export error);
  a silent successful build is the failure the campaign calls "silent distortion".

The hosted exports (one per variant, plus the restore re-export) run concurrently; the OpenCascade
measurements run afterwards, sequentially, because the STEP reader is not thread-safe.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from opencad import cache, interfaces
from opencad.backends.base import BillingError, EngineError, is_program, is_tooling
from opencad.backends.local import lap_timer
from opencad.geomcheck import brep
from opencad.io import sha256_file
from opencad.orchestrator import Ctx, PipelineError


def _export_variant(ctx: Ctx, name: str, value: float, td: Path) -> tuple[Path | None, str | None, str | None]:
    """Rewrite the constant in a temp copy and export STEP. Returns (step_path, error, error_class)."""
    work = td / "part"
    shutil.copytree(ctx.part_dir, work)
    try:
        ctx.backend.language.rewrite_parameter(work, name, value)
    except KeyError:
        return None, f"parameter {name} not found as a top-level constant", "missing"
    try:
        written = ctx.backend.engine.export(work / ctx.backend.language.entry, td / "step", "step", deterministic=True, lock=False)
        return written[0], None, None
    except BillingError:
        raise
    except EngineError as e:
        return None, f"rebuild failed: {_kcl_failure_summary(str(e))}", e.kind


def _kcl_failure_summary(text: str, limit: int = 800) -> str:
    """The lines that name the failing assert/operation, so a correction brief quotes the guard rather than the CLI banner."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    key = [l for l in lines if any(t in l.lower() for t in ("assert", "failed", "error", "cannot", "expected"))]
    picked = key[:6] if key else lines[-6:]
    return " | ".join(picked)[:limit] or text[:limit]


def _measure(step: Path | None, err: str | None, err_class: str | None) -> tuple[dict[str, Any] | None, Any, str | None, str | None]:
    if step is None:
        return None, None, err, err_class
    try:
        return brep.analyze_step(step), brep.read_step(step), None, None
    except brep.BrepError as e:
        return None, None, f"rebuild failed: {str(e)[:800]}", "brep"


def run(ctx: Ctx) -> dict[str, Any]:
    if not ctx.entry.exists():
        raise PipelineError(f"{ctx.entry} missing")
    exp = ctx.require_stage("export")
    ins = ctx.require_stage("inspect")
    # every export still takes a machine-wide engine slot; the cap keeps one part from holding all of them
    workers = min(ctx.backend.engine.max_concurrency(), max(1, int(os.environ.get("OPENCAD_EDIT_WORKERS") or 4)))
    src_files = ctx.backend.language.source_files(ctx.part_dir)
    ck = cache.key("edit", *src_files, ctx.contract_path, Path(exp["files"].get("step", {}).get("path", "")))
    hit = cache.get("edit", ck)
    if hit is not None:
        hit["cached"] = True
        ctx.write_stage("edit", hit)
        print(f"edit {'ok' if hit.get('ok') else 'FAILED'} (cached: unchanged KCL/contract/STEP)")
        return hit
    lap = lap_timer()
    base = ins.get("brep") or {}
    base_vol, base_size = base.get("volume"), base.get("bbox_size")
    c = ctx.contract
    step_path = Path(exp["files"].get("step", {}).get("path", ""))
    baseline_if: dict[str, dict[str, Any]] = {}
    if c.interface_checks() and step_path.exists():
        baseline_if = interfaces.measure(brep.read_step(step_path), c, base_size or [0, 0, 0], step_path=step_path)
    lap("baseline_interfaces")

    # every variant this stage needs, exported concurrently up front
    variants: list[tuple[str, str, float]] = []  # (parameter, kind, value)
    for p in c.parameters:
        if not p.edit_test:
            continue
        et = p.edit_test
        variants.append((p.name, "primary", p.value + et.delta))
        if et.sweep:
            variants += [(p.name, "sweep", v) for v in et.sweep.sequence() if abs(v - p.value) >= 1e-12]
        if et.infeasible_deltas:
            variants += [(p.name, "infeasible", p.value + d) for d in et.infeasible_deltas]
    root = Path(tempfile.mkdtemp(prefix="opencad-edit-"))
    exported: dict[tuple[str, str, float], tuple[Path | None, str | None, str | None]] = {}
    restore: dict[str, Any] = {"baseline_sha256": exp["files"].get("step", {}).get("sha256")}
    try:
        def job(v: tuple[str, str, float]) -> tuple[tuple[str, str, float], tuple[Path | None, str | None, str | None]]:
            td = root / f"{v[0]}-{v[1]}-{v[2]:g}".replace("/", "_")
            td.mkdir(parents=True, exist_ok=True)
            return v, _export_variant(ctx, v[0], v[2], td)

        def restore_job() -> None:
            try:
                w = ctx.backend.engine.export(ctx.entry, root / "restore", "step", deterministic=True, lock=False)
                restore["re_export_sha256"] = sha256_file(w[0])
                restore["ok"] = restore["re_export_sha256"] == restore["baseline_sha256"]
            except EngineError as e:
                restore.update({"ok": False, "error": str(e)[:800]})

        with ThreadPoolExecutor(max_workers=workers) as pool:
            fut_restore = pool.submit(restore_job)
            for v, res in pool.map(job, variants):
                exported[v] = res
            fut_restore.result()
        lap("exports")

        tests: list[dict[str, Any]] = []
        for p in c.parameters:
            if not p.edit_test:
                continue
            et = p.edit_test
            driven = interfaces.driven_items(c, p.name)
            t: dict[str, Any] = {"parameter": p.name, "delta": et.delta, "new_value": p.value + et.delta}
            primary_step = exported[(p.name, "primary", t["new_value"])][0]
            a, shape, err, err_class = _measure(*exported[(p.name, "primary", t["new_value"])])
            if a is None:
                t.update({"ok": False, "error": err, "error_class": err_class})
                tests.append(t)
                continue
            e = et.expect
            t["volume"] = a["volume"]
            t["solids"] = a["solids"]
            t["volume_delta"] = a["volume"] - base_vol if base_vol is not None else None
            t["bbox_size_delta"] = [n - b for n, b in zip(a["bbox_size"], base_size)] if base_size else None
            checks: dict[str, Any] = {}
            if e.volume_delta is not None and t["volume_delta"] is not None:
                err_v = abs(t["volume_delta"] - e.volume_delta)
                checks["volume_delta"] = {"expected": e.volume_delta, "measured": t["volume_delta"], "ok": err_v <= abs(e.volume_delta) * e.tolerance_rel + 1e-6}
            if e.direction and t["volume_delta"] is not None:
                d = t["volume_delta"]
                got = "increase" if d > 1e-6 else "decrease" if d < -1e-6 else "none"
                checks["direction"] = {"expected": e.direction, "measured": got, "ok": got == e.direction}
            if e.bbox_delta is not None and t["bbox_size_delta"] is not None:
                errs = [abs(m - x) for m, x in zip(t["bbox_size_delta"], e.bbox_delta)]
                checks["bbox_delta"] = {"expected": list(e.bbox_delta), "measured": t["bbox_size_delta"], "ok": max(errs) <= c.bbox_tolerance}
            checks["solid_count"] = {"expected": c.acceptance.solid_count, "measured": a["solids"], "ok": a["solids"] == c.acceptance.solid_count}
            checks["valid"] = {"ok": bool(a["valid"])}
            if baseline_if:
                after = interfaces.measure(shape, c, a["bbox_size"], step_path=primary_step)
                pres = interfaces.compare(baseline_if, after, c, driven, mode="edit")
                t["preservation"] = pres
                checks["interfaces_preserved"] = {"preserved": len(pres["preserved"]), "driven": sorted(driven), "ok": pres["ok"],
                                                  "moved": [n for n, r in pres["items"].items() if not r["ok"]]}
            t["checks"] = checks
            # regeneration sweep: no agent, every value must rebuild
            if et.sweep:
                rows = []
                for v in et.sweep.sequence():
                    row: dict[str, Any] = {"value": v}
                    if abs(v - p.value) < 1e-12:
                        row.update({"ok": True, "note": "baseline value"})
                        rows.append(row)
                        continue
                    a2, shape2, err, err_class = _measure(*exported[(p.name, "sweep", v)])
                    if a2 is None:
                        row.update({"ok": False, "error": err, "error_class": err_class})
                        rows.append(row)
                        continue
                    sub: dict[str, Any] = {
                        "valid": {"ok": bool(a2["valid"])},
                        "solid_count": {"expected": c.acceptance.solid_count, "measured": a2["solids"], "ok": a2["solids"] == c.acceptance.solid_count},
                    }
                    scale = (v - p.value) / et.delta if et.delta else None
                    if e.bbox_delta is not None and base_size and scale is not None:
                        exp_bb = [x * scale for x in e.bbox_delta]
                        got_bb = [n - b for n, b in zip(a2["bbox_size"], base_size)]
                        sub["bbox_linear"] = {"expected": exp_bb, "measured": got_bb, "ok": max(abs(m - x) for m, x in zip(got_bb, exp_bb)) <= c.bbox_tolerance}
                    if e.direction in ("increase", "decrease") and base_vol is not None and scale is not None and abs(scale) > 1e-9:
                        dv = a2["volume"] - base_vol
                        want = (1 if e.direction == "increase" else -1) * (1 if scale > 0 else -1)
                        sub["volume_monotonic"] = {"volume_delta": dv, "ok": (dv > 0) == (want > 0) or abs(dv) < 1e-6}
                    if baseline_if:
                        sweep_step = exported[(p.name, "sweep", v)][0]
                        pres2 = interfaces.compare(baseline_if, interfaces.measure(shape2, c, a2["bbox_size"], step_path=sweep_step), c, driven, mode="edit")
                        sub["interfaces_preserved"] = {"ok": pres2["ok"], "moved": [n for n, r in pres2["items"].items() if not r["ok"]]}
                    row.update({"volume": a2["volume"], "bbox_size": a2["bbox_size"], "checks": sub, "ok": all(x["ok"] for x in sub.values())})
                    rows.append(row)
                t["sweep"] = {"values": rows, "declared": len(rows), "passed": sum(1 for r in rows if r["ok"]), "ok": all(r["ok"] for r in rows)}
            # infeasible deltas: the model must refuse them explicitly
            if et.infeasible_deltas:
                rows = []
                for d in et.infeasible_deltas:
                    row = {"delta": d, "value": p.value + d}
                    a3, _, err, err_class = _measure(*exported[(p.name, "infeasible", p.value + d)])
                    if a3 is not None:
                        row.update({"outcome": "built", "ok": False, "volume": a3["volume"], "solids": a3["solids"],
                                    "note": "silent distortion: an impossible value produced a part instead of failing an assert"})
                    elif is_program(err_class):
                        row.update({"outcome": "refused", "ok": True, "error": (err or "")[:300]})
                    else:
                        row.update({"outcome": "error", "ok": False, "error_class": err_class, "error": (err or "")[:300], "note": "not a program-class refusal; tooling failure or missing constant"})
                    rows.append(row)
                t["infeasible"] = {"deltas": rows, "declared": len(rows), "refused": sum(1 for r in rows if r["ok"]), "ok": all(r["ok"] for r in rows)}
            t["ok"] = all(ch["ok"] for ch in t["checks"].values()) and t.get("sweep", {}).get("ok", True) and t.get("infeasible", {}).get("ok", True)
            tests.append(t)
        lap("measure")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    data = {
        "ok": all(t["ok"] for t in tests) and restore.get("ok", False), "tests": tests, "restore": restore, "declared": len(tests),
        "sweep_values": sum(t.get("sweep", {}).get("declared", 0) for t in tests), "sweep_passed": sum(t.get("sweep", {}).get("passed", 0) for t in tests),
        "infeasible_declared": sum(t.get("infeasible", {}).get("declared", 0) for t in tests), "infeasible_refused": sum(t.get("infeasible", {}).get("refused", 0) for t in tests),
        "interfaces_pinned": len(baseline_if), "exports_parallel": workers, "timings": lap.timings,
    }
    tooling_errors = [t.get("error_class") for t in tests if is_tooling(t.get("error_class"))]
    tooling_errors += [r.get("error_class") for t in tests for r in ((t.get("sweep") or {}).get("values", []) + (t.get("infeasible") or {}).get("deltas", []))
                       if is_tooling(r.get("error_class"))]
    if not tooling_errors and restore.get("ok") is not None:  # never cache a verdict the engine, not the part, produced
        cache.put("edit", ck, data)
    data["tooling_errors"] = len(tooling_errors)
    ctx.write_stage("edit", data)
    print(f"edit {'ok' if data['ok'] else 'FAILED'}: {sum(1 for t in tests if t['ok'])}/{len(tests)} edit tests, sweep {data['sweep_passed']}/{data['sweep_values']}, "
          f"infeasible refused {data['infeasible_refused']}/{data['infeasible_declared']}, interfaces pinned {data['interfaces_pinned']}, restore hash match={restore.get('ok')}")
    return data

"""/initialize-cad checkpoint: envelope-only KCL from the worker, measured against the contract envelope."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from opencad import codex, telemetry, worker
from opencad.backends.base import BillingError, EngineError, is_billing
from opencad.io import utc_now
from opencad.orchestrator import Ctx, PipelineError
from opencad.stages.common import bbox_check, volume_band_check
from opencad.stages.decompose import acceptance_count
from opencad.worker import orders


def _entry(ctx: Ctx, work: Path) -> Path:
    return work / ctx.backend.language.entry


def brief(ctx: Ctx, work: Path) -> str:
    lo, hi = ctx.contract.blockout_band()
    entry = _entry(ctx, work)
    note = ctx.backend.language.critics().get("note") or ""
    return f"""Write an ENVELOPE-ONLY blockout of the part below as `{entry}` (create the file; nothing else is a deliverable).

{note}

{codex.contract_digest(ctx.contract, ctx.design_dir)}

Blockout rules:
- Only the primary solids that define the outer envelope: extrudes/revolves/sweeps of the main bodies, positioned in the contract frame. No fillets, chamfers, holes, pockets, patterns, shells, cosmetic features, text, or colours.
- The measured bounding box must equal the contract envelope within ±{ctx.contract.bbox_tolerance} mm on every axis, and the volume must lie in [{lo:.3f}, {hi:.3f}] mm3.
- Declare every contract parameter as a top-level constant with the exact contract name and value even if the blockout does not use it yet.
- Run from `{work}` only; write scratch snapshots there.

{ctx.backend.language.rules()}
Report measured bbox min/max and volume from engine analyze under `## Verification`.
"""


def correction(measured: dict[str, Any]) -> str:
    if "bbox" not in measured:
        return (f"The blockout could not be measured: {measured.get('error') or measured.get('step_error') or 'no exported STEP'}. Fix the entry file "
                "in place (same file, same frame) so it executes and exports the solid, re-verify, and report the measured values. Do not change the contract.")
    bb, vb = measured["bbox"], measured["volume_band"]
    engine = measured.get("engine") or {}
    ebb, evb = engine.get("bbox") or {}, engine.get("volume_band") or {}
    engine_note = ""
    if ebb and not ebb.get("ok", True) and bb.get("ok"):
        engine_note = (
            f"\n(engine analyze bbox max error {ebb.get('max_error')} is disclosed only; "
            "the engine box can include sketch or cut-tool extents. Do not grow or shrink the solid to match it.)"
        )
    source_lines = ""
    for key, label in (("lint", "lint"), ("format", "format")):
        r = measured.get(key) or {}
        if r and not r.get("ok", True):
            detail = r.get("output") or r.get("error") or "; ".join(str(f.get("error", f)) for f in (r.get("findings") or []))
            source_lines += f"\n- {label} FAILS (a blockout must be lint-clean and formatted): {str(detail)[:400]}"
    geometry_ok = bool(bb.get("ok")) and bool(vb.get("ok"))
    verdict = "The geometry meets the envelope and band; only the source checks below fail." if geometry_ok and source_lines else "The blockout does not meet the contract yet."
    return f"""{verdict} Measured independently on the exported STEP (OpenCascade):
- bbox min {bb['measured_min']} max {bb['measured_max']}; expected min {bb['expected_min']} max {bb['expected_max']} (tolerance ±{bb['tolerance']}); max error {bb['max_error']} -> {'ok' if bb.get('ok') else 'FAIL'}
- volume {vb['measured']} mm3; required band {vb['band']} -> {'ok' if vb.get('ok') else 'FAIL'}
- engine analyze (evidence only): bbox max error {ebb.get('max_error', '?')}, volume {evb.get('measured', '?')}{engine_note}{source_lines}
Fix the entry file in place (same file, same frame), re-verify, and report the new measured values. Do not change the contract."""


def measure(ctx: Ctx, work: Path) -> dict[str, Any]:
    """Envelope and volume are judged on the exported STEP (OpenCascade). Engine analyze is evidence only."""
    from opencad.geomcheck import brep

    checked = ctx.backend.language.check(work, ctx.contract)
    fmt, lint = checked["format"], checked["lint"]
    out: dict[str, Any] = {"format": fmt, "lint": lint}
    lo, hi = ctx.contract.blockout_band()
    entry = _entry(ctx, work)
    try:
        a = ctx.backend.engine.analyze(entry)
        out["engine"] = {
            "status": "ok",
            "class": "ok",
            "bbox": bbox_check(ctx.contract, a["bbox_min"], a["bbox_max"]),
            "volume_band": volume_band_check(a["volume_mm3"], lo, hi),
            "volume_mm3": a["volume_mm3"],
            "com": a["com"],
        }
    except BillingError:
        raise
    except EngineError as e:
        out["engine"] = {"status": "missing", "class": e.kind, "error": str(e)[:2000]}
        out["analyze_error"] = str(e)[:2000]
    try:
        step_dir = work / "_measure"
        if step_dir.exists():
            shutil.rmtree(step_dir)
        written = ctx.backend.engine.export(entry, step_dir, "step", deterministic=True)
        s = brep.analyze_step(written[0])
    except BillingError:
        raise
    except (EngineError, brep.BrepError) as e:
        out.update({"step_error": str(e)[:2000], "ok": False})
        return out
    out["bbox"] = bbox_check(ctx.contract, s["bbox_min"], s["bbox_max"])
    out["volume_band"] = volume_band_check(s["volume"], lo, hi)
    out["volume_mm3"] = s["volume"]
    out["com"] = s["center_of_mass"]
    out["step"] = {"path": str(written[0]), "solids": s["solids"], "valid": s["valid"]}
    out["ok"] = bool(out["bbox"]["ok"] and out["volume_band"]["ok"] and lint["ok"])
    return out


def _render_blockout(ctx: Ctx, work: Path, measured: dict[str, Any]) -> dict[str, str]:
    from opencad import render

    snaps: dict[str, str] = {}
    step = Path((measured.get("step") or {}).get("path") or "")
    if not step.exists():
        return snaps
    try:
        views = render.render_snapshots(step, work, ("iso", "four-ways"))
        if "four-ways" in views:
            dest = work / "blockout-four-ways.png"
            shutil.copy2(views["four-ways"], dest)
            snaps["four-ways"] = str(dest)
        if "iso" in views:
            dest = work / "blockout-iso.png"
            shutil.copy2(views["iso"], dest)
            snaps["iso"] = str(dest)
    except Exception as e:
        snaps["error"] = str(e)[:500]
    return snaps


def _append_blockout_log(ctx: Ctx, row: str) -> None:
    log = ctx.results_dir / "blockout-log.md"
    if not log.exists():
        log.write_text("# Blockout checkpoint log\n\n| n | bbox | volume | verdict | note |\n|---|---|---|---|---|\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(row.rstrip() + "\n")


def run(ctx: Ctx, *, max_iterations: int = 2, cont: bool = False) -> dict[str, Any]:
    """`cont=True` continues a run interrupted by a worker handback: finished iterations and the scratch dir are kept."""
    try:
        return _run_blockout(ctx, max_iterations=max_iterations, cont=cont)
    finally:
        from opencad.stages.pipeline import _write_cost

        _write_cost(ctx)


def _run_blockout(ctx: Ctx, *, max_iterations: int = 2, cont: bool = False) -> dict[str, Any]:
    pf = ctx.backend.engine.preflight()
    if pf.get("billing"):
        from opencad.backends.zoo.engine import credit_banner
        from opencad.costing import begin_credits

        print(credit_banner(pf["billing"]))
        begin_credits(ctx.results_dir, pf["billing"], reset=not cont)
    elif not pf.get("ok"):
        cls = pf.get("class") or "unknown"
        msg = pf.get("error") or "backend preflight failed"
        if is_billing(cls):
            raise BillingError(msg)
        raise PipelineError(f"preflight failed ({cls}): {msg}")
    from opencad.costing import mark_cell_start

    mark_cell_start(ctx.results_dir, reset=not cont)
    work = ctx.results_dir / "blockout"
    target = _entry(ctx, work)
    if not cont:
        orders.supersede(ctx.results_dir, "blockout-")
    prev = None if worker.fresh(ctx.results_dir, "blockout-1") else ctx.load_stage("blockout")
    iterations: list[dict[str, Any]] = []
    thread: str | None = None
    final: dict[str, Any] = {"ok": False}
    prior_calls: list[dict[str, Any]] = []
    if worker.fresh(ctx.results_dir, "blockout-1"):
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        ctx.stage_file("blockout").unlink(missing_ok=True)
    elif prev and prev.get("pending"):
        iterations = list(prev.get("iterations") or [])
        thread = prev.get("thread_id")
        final = iterations[-1]["measured"] if iterations else {"ok": False}
        prior_calls = list(prev.get("engine_calls") or [])
    else:
        work.mkdir(parents=True, exist_ok=True)
    ctx.backend.engine.reset_ledger()
    for i in range(len(iterations) + 1, max_iterations + 1):
        run_dir = work / f"codex-{i}"
        msg = brief(ctx, work) if thread is None and i == 1 else correction(final)
        r = worker.dispatch(msg, role="blockout", key=f"blockout-{i}", results_dir=ctx.results_dir, part=ctx.name, cd=work, run_dir=run_dir,
                            resume=thread, timeout=ctx.timeout, deliverables=[target],
                            budget=worker.scaled_budget("blockout", acceptance_count(ctx.contract), ctx.backend.engine))
        thread = r.thread_id or thread
        summary = r.summary()
        rec: dict[str, Any] = {"iteration": i, "worker": summary, "codex": summary, "codex_report": r.sections}
        if not target.exists():
            rec["measured"] = {"ok": False, "error": f"the worker produced no {ctx.backend.language.entry}"}
            iterations.append(rec)
            final = rec["measured"]
        else:
            with telemetry.timed("blockout-measure", ctx.name, ctx.results_dir, key=f"blockout-{i}") as t:
                ctx.backend.language.format_write(target)
                final = measure(ctx, work)
                t["ok"] = bool(final.get("ok"))
                t["engine_calls"] = list(ctx.backend.engine.reset_ledger())
                prior_calls += t["engine_calls"]
            rec["measured"] = final
            iterations.append(rec)
        prior_calls += ctx.backend.engine.reset_ledger()
        ctx.write_stage("blockout", {"ok": False, "pending": not final.get("ok"), "iterations": iterations, "iterations_used": len(iterations),
                                     "max_iterations": max_iterations, "thread_id": thread, "kcl": str(target), "source": str(target)}, ledger_prefix=prior_calls)
        if final["ok"]:
            break
    with telemetry.timed("blockout-views", ctx.name, ctx.results_dir):
        snaps = _render_blockout(ctx, work, final) if target.exists() else {}
    data = {
        "ok": bool(final.get("ok")),
        "iterations": iterations,
        "iterations_used": len(iterations),
        "max_iterations": max_iterations,
        "thread_id": thread,
        "kcl": str(target),
        "source": str(target),
        "snapshots": snaps,
        "measured": {k: final.get(k) for k in ("bbox", "volume_band", "volume_mm3", "com", "lint", "format", "engine", "step", "analyze_error", "step_error") if k in final},
    }
    engine_calls = len(prior_calls) + ctx.backend.engine.engine_calls()
    ctx.write_stage("blockout", data, ledger_prefix=prior_calls)
    bb = final.get("bbox", {})
    row = (
        f"| {len(iterations)} | {bb.get('measured_min', '?')} → {bb.get('measured_max', '?')} | {final.get('volume_mm3', '?')} | "
        f"{'pass' if data['ok'] else 'FAIL'} | {utc_now()}: {'within envelope and band' if data['ok'] else 'see results/' + ctx.backend_id + '/' + ctx.name + '/blockout.json'} |"
    )
    _append_blockout_log(ctx, row)
    verdict = "PASS" if data["ok"] else "FAIL"
    print(f"blockout {verdict}: bbox err {bb.get('max_error', '?')} (tol {bb.get('tolerance', '?')}), volume {final.get('volume_mm3', '?')} band {final.get('volume_band', {}).get('band', '?')}; "
          f"{len(iterations)} iteration(s), engine calls {engine_calls}")
    return data

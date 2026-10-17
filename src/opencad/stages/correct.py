"""correct: a deliberate geometry turn on the model thread, then re-verify from the verify stage."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from opencad.io import dump_json, load_json
from opencad.orchestrator import Ctx, PipelineError
from opencad.stages import model as model_mod
from opencad.worker import orders, state as worker_state

STATE_FILE = "correct.json"


def _read_note(note: str) -> str:
    try:
        p = Path(note)
        if p.is_file():
            return p.read_text(encoding="utf-8")
    except OSError:  # inline text longer than a file name
        pass
    return note


def _next_key(results_dir: Path) -> str:
    n = 1
    for o in orders.list_orders(results_dir):
        if o.key.startswith("improve-"):
            try:
                n = max(n, int(o.key.split("-", 1)[1]) + 1)
            except ValueError:
                pass
    return f"improve-{n}"


def brief(ctx: Ctx, note: str) -> str:
    fb = ctx.load_stage("gate_feedback") or {}
    summary = fb.get("summary") if fb.get("summary") is not None else {"ok": fb.get("ok")}
    return (
        f"The part currently passes its gates (`gate_feedback.json` summary: {summary}). "
        "Every contract acceptance item, section, edit test and the volume band must keep passing. "
        "Change only what the note names.\n\n"
        f"{note.strip()}\n\n"
        "Run the local critic (`python -m opencad quick` with `--stl`) before finishing. "
        "Open `quick-views.png` and write one `Visual:` line. Report measured versus expected values."
    )


def _current_stl(ctx: Ctx) -> Path | None:
    exp = ctx.load_stage("export") or {}
    raw = (exp.get("files") or {}).get("stl", {}).get("path") or ""
    stl = Path(raw)
    if raw and stl.is_file():
        return stl
    export_dir = ctx.results_dir / "export"
    cands = sorted(export_dir.glob("*.stl")) if export_dir.exists() else []
    return cands[0] if cands else None


def _delta_vs_previous(prev: Path, new: Path, plane: str = "y", at: float = 0.0) -> dict[str, Any]:
    import numpy as np
    import trimesh

    from opencad.geomcheck.mesh import closest_point, deviation
    from opencad.reference.mesh import load_mesh

    d = deviation(new, prev, samples=20000)
    a, b = load_mesh(new), load_mesh(prev)
    pts, _ = trimesh.sample.sample_surface(a, 20000, seed=0)
    _, dist, _ = closest_point(b, pts)
    changed = np.asarray(dist, float) > 0.05
    axis = "xyz".index(plane)
    if changed.any():
        cpts = pts[changed]
        bbox = {"min": [round(float(v), 4) for v in cpts.min(axis=0)], "max": [round(float(v), 4) for v in cpts.max(axis=0)]}
        area_each = float(a.area) / max(len(pts), 1)
        pos = cpts[:, axis] >= at
        area_pos, area_neg = float(pos.sum()) * area_each, float((~pos).sum()) * area_each
    else:
        bbox, area_pos, area_neg = None, 0.0, 0.0
    return {
        "p95": d["p95"],
        "max": d["hausdorff_estimate"],
        "changed_region_bbox": bbox,
        "changed_area_positive": area_pos,
        "changed_area_negative": area_neg,
        "changed_fraction": float(changed.mean()) if len(dist) else 0.0,
    }


def run(ctx: Ctx, *, note: str = "", allow_retry: bool = True, cont: bool = False) -> dict[str, Any]:
    if not ctx.entry.exists():
        raise PipelineError(f"{ctx.entry} missing")
    pf = ctx.backend.engine.preflight()
    if not pf.get("ok") and pf.get("class") == "billing":
        from opencad.backends.base import BillingError

        raise BillingError(pf.get("error") or "backend preflight failed")

    state_path = ctx.results_dir / STATE_FILE
    mdl = ctx.load_stage("model") or {}
    thread = mdl.get("thread_id") or None
    if not thread:
        print(f"correct: {ctx.name} has no recorded worker thread; the worker starts fresh from earlier turn reports", flush=True)

    if cont and state_path.exists():
        data: dict[str, Any] = load_json(state_path) or {}
        key = str(data["key"])
        note_text = str(data.get("note") or "")
        allow_retry = bool(data.get("allow_retry", allow_retry))
    else:
        if cont and not state_path.exists():
            raise PipelineError(f"nothing to continue for {ctx.name}: no {STATE_FILE}")
        if not (note or "").strip():
            raise PipelineError("correct requires --note (a markdown file or inline text)")
        note_text = _read_note(note)
        key = _next_key(ctx.results_dir)
        prev_stl = _current_stl(ctx)
        snap = ctx.results_dir / "correct-previous.stl"
        if prev_stl is not None:
            shutil.copy2(prev_stl, snap)
        data = {"key": key, "note": note_text, "allow_retry": allow_retry, "phase": "worker",
                "previous_stl": str(snap) if prev_stl is not None else None}
        dump_json(state_path, data)

    recorded = [c.get("key") for c in (ctx.load_stage("model") or {}).get("corrections") or []]
    if key not in recorded:
        model_mod.retry(ctx, thread or "", brief(ctx, note_text), key=key, role="correction")
        data["phase"] = "stages"
        dump_json(state_path, data)

    from opencad.stages import pipeline

    if worker_state.load(ctx.results_dir) is not None:
        code = pipeline.run(ctx, cont=True)
    else:
        code = pipeline.run(ctx, skip_blockout=True, from_stage="verify", allow_retry=allow_retry)
    data["pipeline_code"] = code
    data["phase"] = "done"
    new_stl = _current_stl(ctx)
    prev = Path(data.get("previous_stl") or "")
    if prev.exists() and new_stl is not None and new_stl.exists():
        specs = ctx.contract.acceptance.symmetry
        plane, at = (specs[0].plane, specs[0].at) if specs else ("y", 0.0)
        data["delta_vs_previous"] = _delta_vs_previous(prev, new_stl, plane, at)
    dump_json(state_path, data)
    return data

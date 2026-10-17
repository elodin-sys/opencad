"""export: deterministic STEP + STL on the critical path; the determinism re-export and the GLB viewer file after the gates.

`run` exports STEP and STL concurrently (the two files every later stage needs). `finalize` runs once the
retry decision is made: a second deterministic STEP whose hash must match, and the GLB. Gates read
`step.deterministic`: None means "not yet checked", False fails.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from opencad.backends.base import BillingError, EngineError
from opencad.io import sha256_file
from opencad.orchestrator import Ctx, PipelineError


_BUILDS: dict[tuple[str, str], dict[str, Any]] = {}


def shared_build(ctx: Ctx) -> dict[str, Any] | None:
    """verify and export of one source from a single engine run (analyze + STEP + STL + FCStd), memoised per source tree.
    None when the engine has no `build` (Zoo): the stages then run their own calls."""
    build = getattr(ctx.backend.engine, "build", None)
    if build is None:
        return None
    from opencad.io import sha256_tree

    tree = json.dumps(sorted(sha256_tree(ctx.part_dir, ctx.backend.language.suffixes).items()))
    key = (str(ctx.entry), hashlib.sha256(tree.encode()).hexdigest())
    hit = _BUILDS.get(key)
    if hit is not None and (not hit["ok"] or all(p is None or p.exists() for p in (hit.get("step"), hit.get("stl")))):
        return hit
    out = ctx.results_dir / "build" / key[1][:12]
    shutil.rmtree(out, ignore_errors=True)
    try:
        hit = {"ok": True, **build(ctx.entry, step=out / f"{ctx.entry.stem}.step", stl=out / f"{ctx.entry.stem}.stl",
                                   fcstd=out / f"{ctx.entry.parent.name}.FCStd", density_kg_m3=ctx.contract.density_kg_m3)}
    except BillingError:
        raise
    except EngineError as e:
        hit = {"ok": False, "error": e}
    _BUILDS[key] = hit
    return hit


def _export(ctx: Ctx, out_dir: Path, sub: str, fmt: str) -> tuple[str, Path | None, str | None]:
    try:
        w = ctx.backend.engine.export(ctx.entry, out_dir / sub, fmt, deterministic=True, lock=False)
        return fmt, w[0], None
    except BillingError:
        raise
    except EngineError as e:
        return fmt, None, str(e)[:2000]


def run(ctx: Ctx) -> dict[str, Any]:
    if not ctx.entry.exists():
        raise PipelineError(f"{ctx.entry} missing; run the model stage first")
    out_dir = ctx.results_dir / "export"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    files: dict[str, Any] = {}
    errors: dict[str, str] = {}
    b = shared_build(ctx)
    if b is not None:
        out_dir.mkdir(parents=True)
        err = None if b["ok"] else str(b["error"])[:2000]
        results = [("step", b.get("step"), err), ("stl", b.get("stl"), err)]
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda job: _export(ctx, out_dir, *job), (("step-a", "step"), ("stl-out", "stl"))))
    for fmt, written, err in results:
        if written is None:
            errors[fmt] = err or "export failed"
            continue
        final = out_dir / f"{ctx.name}.{fmt}"
        shutil.copy2(written, final)
        files[fmt] = {"path": str(final), "sha256": sha256_file(final), "bytes": final.stat().st_size}
        for extra in written.parent.glob("*.FCStd"):
            dest = out_dir / extra.name
            shutil.copy2(extra, dest)
            files["fcstd"] = {"path": str(dest), "sha256": sha256_file(dest), "bytes": dest.stat().st_size}
        if fmt == "step":
            files[fmt].update({"deterministic": None, "second_sha256": None})
    # STEP + STL are the authoritative deliverables. GLB and the determinism re-export follow in finalize().
    data = {"ok": "step" in files and "stl" in files, "files": files, "errors": errors, "finalized": False}
    ctx.write_stage("export", data)
    print(f"export {'ok' if data['ok'] else 'FAILED'}: {', '.join(f'{k} {v['bytes']}B' for k, v in files.items())}"
          + ("; determinism and GLB deferred to finalize" if 'step' in files else "") + (f"; errors {list(errors)}" if errors else ""))
    return data


def finalize(ctx: Ctx) -> dict[str, Any]:
    """Second deterministic STEP (hash must match) and the GLB viewer file, concurrently; updates export.json in place. The edit stage's
    restore re-export of this same STEP is that second export already, and a local engine's GLB converts the exported STL: no engine run."""
    data = ctx.load_stage("export") or {}
    files = data.get("files") or {}
    if "step" not in files or not ctx.entry.exists():
        return data
    if data.get("finalized"):
        return data
    out_dir = ctx.results_dir / "export"
    errors: dict[str, str] = dict(data.get("errors") or {})
    timings: dict[str, float] = {}
    restore = (ctx.load_stage("edit") or {}).get("restore") or {}
    stl = Path((files.get("stl") or {}).get("path") or "")
    local = getattr(ctx.backend.engine, "build", None) is not None

    def job(sub: str, fmt: str) -> tuple[str, Path | None, str | None]:
        t0 = time.time()
        try:
            if fmt == "step" and restore.get("re_export_sha256") and restore.get("baseline_sha256") == files["step"]["sha256"]:
                files["step"]["determinism_source"] = "edit restore re-export"
                return fmt, None, None
            if fmt == "glb" and local and stl.is_file():
                from opencad.backends.local import stl_to_glb

                return fmt, stl_to_glb(stl, out_dir / sub / f"{ctx.name}.glb"), None
            return _export(ctx, out_dir, sub, fmt)
        finally:
            timings["determinism_s" if fmt == "step" else f"{fmt}_s"] = round(time.time() - t0, 2)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda j: job(*j), (("step-b", "step"), ("glb-out", "glb"))))
    for fmt, written, err in results:
        if fmt == "step" and files["step"].get("determinism_source"):
            files["step"]["second_sha256"] = restore["re_export_sha256"]
            files["step"]["deterministic"] = restore["re_export_sha256"] == files["step"]["sha256"]
            continue
        if fmt == "step":
            if written is None:
                errors["step-b"] = err or "second export failed"
                files["step"]["deterministic"] = False
            else:
                hb = sha256_file(written)
                files["step"]["second_sha256"] = hb
                files["step"]["deterministic"] = hb == files["step"]["sha256"]
        elif written is None:
            errors[fmt] = err or "export failed"
        else:
            final = out_dir / f"{ctx.name}.{fmt}"
            shutil.copy2(written, final)
            files[fmt] = {"path": str(final), "sha256": sha256_file(final), "bytes": final.stat().st_size}
    data.update({"files": files, "errors": errors, "finalized": True, "ok": bool(data.get("ok")) and files["step"]["deterministic"] is not False})
    ctx.write_stage("export", {k: v for k, v in data.items() if k not in ("provenance", "stage")}, ledger_prefix=data.get("engine_calls") or [])
    print(f"export finalize: STEP deterministic={files['step']['deterministic']}" + (f", glb {files['glb']['bytes']}B" if 'glb' in files else "") + (f"; errors {list(errors)}" if errors else ""))
    return {**data, "finalize_timings": timings}

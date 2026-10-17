"""`python -m opencad run` / `drive`: stage order, stale cleanup, single bounded retry, gates, report.

The run is resumable across worker handbacks: a stage that needs a worker turn raises WorkerPending, the
state (phase, stage, retry record) is persisted in results/<part>/pipeline-state.json, and the process
exits 75 after printing one `NEXT {...}` line. `run(..., cont=True)` re-enters at the recorded point.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import time
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from opencad import gates as gates_mod
from opencad import report as report_mod
from opencad import telemetry
from opencad.backends.base import BillingError, EngineError, is_billing, is_program
from opencad.contract import load_contract
from opencad.io import dump_json, load_json, sha256_file
from opencad.orchestrator import Ctx, PipelineError
from opencad.worker import EXIT_WORKER_PENDING, WorkerPending, orders, state

ORDER = ["plan", "model", "verify", "export", "inspect", "edit", "gates", "report"]  # edit needs inspect (STEP baseline)
ARTIFACTS = {
    "plan": ["plan.json", "plan.md", "plan-work"],
    "model": ["model.json", "model-work"],
    "verify": ["verify.json", "snapshots", "build"],
    "export": ["export.json", "export"],
    "inspect": ["inspect.json", "deviation-map.png"],
    "edit": ["edit.json"],
    "gates": ["gate_feedback.json"],
    "report": ["report.html", "report.md", "contact-sheet.png", "handoff"],
}
# work-order keys a stage owns; superseded when the stage restarts fresh
ORDER_KEYS = {"plan": ("plan",), "model": ("model", "retry", "correction-", "improve-", "partition", "module-", "integrate")}
MAX_CORRECTIONS = int(os.environ.get("OPENCAD_MAX_CORRECTIONS", "6"))
CORRECTION_FLOOR = int(os.environ.get("OPENCAD_CORRECTION_FLOOR", "3"))  # turns always granted; beyond, a turn is earned by a falling failing-item count
MAX_CHECKPOINT_REVERTS = 2  # consecutive corrections that left a non-executing source before the loop stops
EXIT_TOOLING = 3  # a pipeline exception in a worker stage; state is kept for `drive` to continue
KERNEL_RE = re.compile(r"cannot handle this 3D|kernel (error|failure|failed|crash)|boolean (failed|failure|error)|engine (error|panic)|failed to (fuse|subtract|union|intersect)", re.I)  # zoo default; overridden per backend via engine.kernel_patterns()


DECOMPOSE: bool | None = None  # set per run: True forces the partition/module/integrate path, False forbids it, None = size heuristic


def _stage_fn(name: str) -> Callable[[Ctx], dict[str, Any]]:
    if name == "plan":
        from opencad.stages import plan
        return plan.run
    if name == "model":
        from opencad.stages import decompose, model

        def model_stage(ctx: Ctx) -> dict[str, Any]:
            if decompose.should_decompose(ctx, DECOMPOSE):
                print(f"model stage: decomposing ({len(ctx.contract.parameters)} parameters, {sum(len(v) for v in decompose.acceptance_names(ctx.contract).values())} acceptance items"
                      f"{'; requested' if DECOMPOSE else '; size trigger'})", flush=True)
                return decompose.run(ctx)
            return model.run(ctx)

        return model_stage
    if name == "verify":
        from opencad.stages import verify
        return verify.run
    if name == "export":
        from opencad.stages import export
        return export.run
    if name == "inspect":
        from opencad.stages import inspect_stage
        return inspect_stage.run
    if name == "edit":
        from opencad.stages import edit
        return edit.run
    raise PipelineError(f"no stage {name}")


def run_stage(ctx: Ctx, name: str) -> dict[str, Any]:
    print(f"== {name} ({ctx.name}) ==", flush=True)
    t0 = time.time()
    try:
        data = _stage_fn(name)(ctx)
    except WorkerPending:
        raise
    except BillingError as e:
        data = {"ok": False, "error": str(e)[:4000], "class": "billing"}
        ctx.write_stage(name, data)
        print(f"{name} FAILED (billing): {str(e)[:300]}")
    except (PipelineError, EngineError) as e:
        data = {"ok": False, "error": str(e)[:4000], "class": getattr(e, "kind", None)}
        ctx.write_stage(name, data)
        print(f"{name} FAILED: {str(e)[:300]}")
    except Exception as e:  # tooling failure: recorded, never masked as a design failure
        data = {"ok": False, "error": f"tooling exception: {e!r}", "traceback": traceback.format_exc()[-3000:]}
        ctx.write_stage(name, data)
        print(f"{name} FAILED (tooling): {e!r}")
    if name not in ("plan", "model"):  # worker stages are measured as turns; the evaluator stages as stage rows
        row = telemetry.stage_data(name, time.time() - t0, data.get("ok"), (ctx.load_stage(name) or {}).get("engine_calls"), cached=bool(data.get("cached")))
        telemetry.record("stage", ctx.name, {**row, **({"timings": data["timings"]} if data.get("timings") else {})}, results_dir=ctx.results_dir)
    return data


def run_gates(ctx: Ctx, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    with telemetry.timed("gates", ctx.name, ctx.results_dir) as t:
        fb = gates_mod.evaluate(ctx)
        t["ok"] = fb.get("ok")
    if extra:
        fb.update(extra)
    dump_json(ctx.results_dir / "gate_feedback.json", fb)
    print("== gates ==")
    for g in fb["gates"]:
        mark = "PASS" if g["ok"] else ("n/a " if g["ok"] is None else "FAIL")
        print(f"  [{g['tier']}] {mark} {g['id']}: {g['evidence'][0][:140]}")
    print(f"gates: {fb['summary']}")
    telemetry.record("gates", ctx.name, telemetry.gates_data(fb, retry=bool((extra or {}).get("retry"))), results_dir=ctx.results_dir)
    return fb


def run_report(ctx: Ctx, fb: dict[str, Any]) -> dict[str, Any]:
    print("== report ==")
    data = report_mod.build(ctx, fb)
    ctx.write_stage("report", data)
    print(f"report: {data['report_html']} verdict {data['verdict']}")
    return data


def _write_cost(ctx: Ctx) -> None:
    try:
        from opencad.costing import write_cell_cost

        write_cell_cost(ctx.results_dir, backend_id=ctx.backend_id)
    except Exception as e:
        print(f"cost snapshot failed: {e}")


def finish(ctx: Ctx, fb: dict[str, Any]) -> dict[str, Any]:
    """After the retry decision: determinism re-export + GLB, report snapshots, final gates, report. Decoration never delays a correction turn."""
    from opencad.stages import export as export_mod
    from opencad.stages import verify as verify_mod

    retry_info = fb.get("retry") or {"attempted": False}
    if (ctx.load_stage("export") or {}).get("ok"):
        print("== finalize (determinism re-export, GLB, snapshots) ==", flush=True)
        before = {s: len((ctx.load_stage(s) or {}).get("engine_calls") or []) for s in ("export", "verify")}
        with telemetry.timed("finalize", ctx.name, ctx.results_dir, ok=True) as t:
            try:
                t.update((export_mod.finalize(ctx) or {}).get("finalize_timings") or {})
                t1 = time.time()
                verify_mod.render_snapshots(ctx)
                t["snapshots_s"] = round(time.time() - t1, 2)
            except BillingError as e:
                print(f"finalize skipped: {str(e)[:200]}")
            t["engine_calls"] = [c for s, n in before.items() for c in ((ctx.load_stage(s) or {}).get("engine_calls") or [])[n:]]
        fb = run_gates(ctx, {"retry": retry_info} if retry_info.get("attempted") else None)
    fb["retry"] = retry_info
    dump_json(ctx.results_dir / "gate_feedback.json", fb)
    run_report(ctx, fb)
    return fb


def _classify_text(text: str) -> str:
    from opencad.backends.registry import get

    return get().engine.classify(text)


def _failure_class(stage: dict[str, Any] | None) -> str | None:
    """Best-effort engine failure class from a stage JSON (engine block, errors, or error string)."""
    if not stage:
        return None
    eng = stage.get("engine") or {}
    if isinstance(eng, dict) and eng.get("class"):
        return eng["class"]
    for key in ("error", "analyze_error"):
        if stage.get(key):
            return _classify_text(str(stage[key]))
    for err in (stage.get("errors") or {}).values():
        kind = _classify_text(str(err))
        if kind != "unknown":
            return kind
    snaps = stage.get("snapshots") or {}
    if isinstance(snaps, dict) and snaps.get("error"):
        return snaps.get("class") or _classify_text(str(snaps["error"]))
    return None


def program_failed(ctx: Ctx) -> bool:
    """The source itself did not execute (program-class analyze or export failure), or its build outgrew the engine memory
    budget and was killed: model-attributable, never tooling."""
    exp = ctx.load_stage("export") or {}
    ver = ctx.load_stage("verify") or {}
    kinds = (_failure_class(exp), (ver.get("engine") or {}).get("class"))
    return not exp.get("ok") and any(is_program(k) or k == "memory" for k in kinds)


def tooling_failed(ctx: Ctx) -> bool:
    """True when a dead connection / timeout / billing refusal should skip the worker retry.

    A program that does not execute is the model's fault even though inspect/edit then cannot run.
    """
    if program_failed(ctx):
        return False
    ins = ctx.load_stage("inspect") or {}
    if ins.get("error") or ins.get("traceback"):
        return True
    for name in ("verify", "export", "inspect"):
        kind = _failure_class(ctx.load_stage(name))
        if kind in ("transient", "timeout") or is_billing(kind):
            return True
    return False


def _clean(ctx: Ctx, names: list[str]) -> None:
    for name in names:
        for art in ARTIFACTS[name]:
            p = ctx.results_dir / art
            if p.is_dir():
                shutil.rmtree(p)
            elif p.exists():
                p.unlink()


def _run_evaluator(ctx: Ctx) -> None:
    """verify -> export -> inspect -> edit, skipping the measurements when export produced no STEP."""
    for name in ("verify", "export", "inspect", "edit"):
        if name in ("inspect", "edit") and not (ctx.load_stage("export") or {}).get("ok"):
            # no STEP to measure: record the cause instead of a traceback so the retry policy can attribute it
            exp = ctx.load_stage("export") or {}
            kind = _failure_class(exp) or "unknown"
            ctx.write_stage(name, {"ok": False, "skipped": True, "class": kind, "error": f"export produced no STEP ({kind}): {list((exp.get('errors') or {}).values())[:1]}"})
            print(f"{name} skipped: export produced no STEP ({kind})")
            continue
        run_stage(ctx, name)


def source_hash(ctx: Ctx) -> str:
    from opencad.io import sha256_tree

    suffixes = ctx.backend.language.suffixes
    return ";".join(f"{k}={v[:12]}" for k, v in sorted(sha256_tree(ctx.part_dir, suffixes).items())) if ctx.part_dir.exists() else ""


kclsrc_hash = source_hash  # historical name


def failing_items(ctx: Ctx) -> list[str]:
    """`kind/name` of every inspect item the last evaluator pass failed: the progress signal of the correction loop."""
    return gates_mod.failing_item_names(ctx.load_stage("inspect") or {})


def _contract_sha(ctx: Ctx) -> str | None:
    return sha256_file(ctx.contract_path) if ctx.contract_path.exists() else None


def _failure_signature(ctx: Ctx, fb: dict[str, Any]) -> str:
    """What failed: the failed gate ids, the engine failure class and a digest of the failing items, so two identical outcomes
    in a row stop the loop while 44/52 -> 48/52 on the same gate counts as progress."""
    exp = ctx.load_stage("export") or {}
    ver = ctx.load_stage("verify") or {}
    cls = _failure_class(exp) or (ver.get("engine") or {}).get("class") or "-"
    items = failing_items(ctx)
    digest = hashlib.sha256(",".join(items).encode()).hexdigest()[:12] if items else "-"
    return f"{','.join(sorted(fb.get('failed') or []))}|{cls}|{digest}"


def checkpoint_path(ctx: Ctx) -> Path | None:
    """The worker's last executing copy of the entry (model brief: `<model-work>/checkpoint<suffix>`; a copy beside the entry also counts)."""
    suffix = ctx.backend.language.suffixes[0]
    for cand in (ctx.results_dir / "model-work" / f"checkpoint{suffix}", ctx.part_dir / f"checkpoint{suffix}"):
        if cand.exists():
            return cand
    return None


def revert_to_checkpoint(ctx: Ctx) -> bool:
    """A correction that left a non-executing source is replaced by the worker's own checkpoint: a revert, not modelling."""
    cp = checkpoint_path(ctx)
    if cp is None or not ctx.kcl_target.exists() or cp.read_bytes() == ctx.kcl_target.read_bytes():
        return False
    shutil.copy2(cp, ctx.kcl_target)
    return True


def _stagnated(baseline: int | None, history: list[dict[str, Any]]) -> tuple[bool, list[int]]:
    """Two consecutive correction turns without a fall in the failing-item count. A round whose contract changed under it
    (new items measured) restarts the sequence: its count is not comparable with the rounds before it."""
    start = max((i for i, h in enumerate(history) if h.get("contract_changed")), default=None)
    hist = history if start is None else history[start:]
    seq = ([baseline] if baseline is not None and start is None else []) + [h.get("failing_count") for h in hist if h.get("failing_count") is not None]
    no_fall = [seq[i] >= seq[i - 1] for i in range(1, len(seq))]
    return (len(no_fall) >= 2 and no_fall[-1] and no_fall[-2]), seq


def stuck_class(ctx: Ctx, rec: dict[str, Any]) -> str | None:
    """Why a part is stuck after its corrections: kernel-boolean loop, incomplete checkpoint, or None (progress, or a plain failure)."""
    if rec.get("stopped") == "gates pass":
        return None
    mdl = ctx.load_stage("model") or {}
    hist = rec.get("history") or []
    texts = [str((c.get("codex_report") or {}).get("Open questions", "")) + str((c.get("codex_report") or {}).get("Result", "")) for c in (mdl.get("corrections") or [])]
    texts.append(str((mdl.get("codex_report") or {}).get("Open questions", "")) + str((mdl.get("codex_report") or {}).get("Result", "")))
    patterns = ctx.backend.engine.kernel_patterns() or [KERNEL_RE]
    kernel = any(p.search(t) for p in patterns for t in texts) or program_failed(ctx)
    incomplete = bool(mdl.get("self_reported_incomplete")) or any(h.get("incomplete") for h in hist)
    if incomplete and kernel:
        return "kernel-incomplete"
    if incomplete:
        return "incomplete-checkpoint"
    if kernel:
        return "kernel"
    stopped = str(rec.get("stopped", ""))
    if hist and stopped.startswith(("same failure", "no progress")):
        return "no-progress"
    return None


def _pending_exit(wp: WorkerPending) -> int:
    for o in wp.orders:
        print(f"== worker turn pending: {o.id} ({o.role}, model {o.model}, budget {o.budget_s:.0f} s) ==", flush=True)
        print(orders.next_line(o), flush=True)
    if len(wp.orders) > 1:
        print(f"== {len(wp.orders)} independent turns: launch them all at once ==", flush=True)
    return EXIT_WORKER_PENDING


@contextmanager
def _drive_lock(ctx: Ctx) -> Iterator[None]:
    """One driver per part: a worker that runs the pipeline itself, or a second drive loop, must not race the orchestrator."""
    import fcntl

    ctx.results_dir.mkdir(parents=True, exist_ok=True)
    with open(ctx.results_dir / ".drive.lock", "a+") as fh:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise PipelineError(f"another pipeline process is driving {ctx.name} (results/{ctx.name}/.drive.lock is held); wait for it or stop it first")
        try:
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def run(ctx: Ctx, *, skip_blockout: bool = False, from_stage: str = "plan", allow_retry: bool = True, cont: bool = False, plan_separately: bool = False,
        decompose: bool | None = None) -> int:
    with _drive_lock(ctx):
        try:
            return _run(ctx, skip_blockout=skip_blockout, from_stage=from_stage, allow_retry=allow_retry, cont=cont, plan_separately=plan_separately, decompose=decompose)
        finally:
            _write_cost(ctx)


def _run(ctx: Ctx, *, skip_blockout: bool, from_stage: str, allow_retry: bool, cont: bool, plan_separately: bool, decompose: bool | None) -> int:
    global DECOMPOSE
    st = state.load(ctx.results_dir) if cont else None
    if cont and (st is None or st.get("command") != "run"):
        raise PipelineError(f"nothing to continue for {ctx.name}: no pipeline-state.json from an interrupted run")
    if st is not None:
        from_stage, allow_retry, skip_blockout = st["from_stage"], st["allow_retry"], st["skip_blockout"]
        plan_separately = bool(st.get("plan_separately", False))
        decompose = st.get("decompose")
        phase, stage = st["phase"], st["stage"]
        print(f"== continuing {ctx.name} at {phase}/{stage} ==", flush=True)
    else:
        if from_stage not in ORDER:
            raise PipelineError(f"--from-stage must be one of {ORDER}")
        if not skip_blockout and from_stage == "plan":
            from opencad.stages.decompose import acceptance_count
            from opencad.worker.profiles import SMALL_CONTRACT_ITEMS

            blk = ctx.load_stage("blockout")
            if (not blk or not blk.get("ok")) and acceptance_count(ctx.contract) > SMALL_CONTRACT_ITEMS:
                raise PipelineError("blockout checkpoint missing or failed; run `python -m opencad blockout <part>` or pass --skip-blockout")
        start = ORDER.index(from_stage)
        pf = ctx.backend.engine.preflight()
        if not pf.get("ok") and pf.get("class") == "billing":
            raise BillingError(pf.get("error") or "backend preflight failed")
        if pf.get("billing"):
            from opencad.backends.zoo.engine import credit_banner, forecast_calls

            print(credit_banner(pf["billing"], forecast_calls(ctx.contract, from_stage)))
        elif pf.get("error"):
            print(f"preflight: {pf['error']}")
        else:
            print(f"preflight ok: backend={ctx.backend_id} engine={pf.get('version')}")
        from opencad.costing import begin_credits, mark_cell_start

        mark_cell_start(ctx.results_dir, reset=False)
        if pf.get("billing"):
            begin_credits(ctx.results_dir, pf["billing"], reset=False)
        ctx.results_dir.mkdir(parents=True, exist_ok=True)
        _clean(ctx, ORDER[start:])
        for name in ORDER[start:]:
            for key in ORDER_KEYS.get(name, ()):
                orders.supersede(ctx.results_dir, key)
        if from_stage == "plan" and ctx.part_dir.exists():
            suffixes = ctx.backend.language.suffixes
            for p in ctx.part_dir.iterdir():
                if p.is_file() and p.suffix in suffixes:
                    p.unlink()
        phase, stage = "stages", from_stage
    DECOMPOSE = decompose
    base = {"command": "run", "part": ctx.name, "backend": ctx.backend_id, "from_stage": from_stage, "allow_retry": allow_retry, "skip_blockout": skip_blockout, "plan_separately": plan_separately,
            "decompose": decompose}

    try:
        if phase == "stages":
            for name in ORDER[ORDER.index(stage):]:
                if name in ("gates", "report"):
                    break
                state.save(ctx.results_dir, {**base, "phase": "stages", "stage": name})
                if name in ("inspect", "edit") and not (ctx.load_stage("export") or {}).get("ok"):
                    exp = ctx.load_stage("export") or {}
                    kind = _failure_class(exp) or "unknown"
                    ctx.write_stage(name, {"ok": False, "skipped": True, "class": kind, "error": f"export produced no STEP ({kind}): {list((exp.get('errors') or {}).values())[:1]}"})
                    print(f"{name} skipped: export produced no STEP ({kind})")
                    continue
                if name == "plan" and not plan_separately:
                    from opencad.stages import plan as plan_mod

                    data = plan_mod.fold(ctx)
                else:
                    data = run_stage(ctx, name)
                if data.get("class") in ("credits", "billing"):
                    break
                if str(data.get("error") or "").startswith("tooling exception") and name in ("plan", "model"):
                    # a pipeline bug, not a design failure: keep the state (and the finished worker turn) so `drive` re-enters here after the fix
                    print(f"== {name} hit a tooling exception; state kept at stages/{name}; fix the pipeline and run `python -m opencad drive {ctx.name}` ==", flush=True)
                    return EXIT_TOOLING
                if not data.get("ok") and name in ("plan", "model"):
                    break  # nothing downstream can run without a model
            phase = "gates"

        if phase == "gates":
            state.save(ctx.results_dir, {**base, "phase": "gates", "stage": "gates"})
            fb = run_gates(ctx)
            mdl = ctx.load_stage("model") or {}
            skip_retry = tooling_failed(ctx)
            if skip_retry:
                print("skipping the worker correction: verify/export/inspect recorded a transient, timeout, credits, or tooling exception")
            retryable = fb.get("retryable_failed") or []
            if allow_retry and not skip_retry and retryable and mdl and ctx.kcl_target.exists():
                items0 = failing_items(ctx)
                rec = {"n": 0, "history": [], "gates_before": {g["id"]: g["ok"] for g in fb["gates"]}, "reason": retryable,
                       "thread_id": mdl.get("thread_id") or "", "last_signature": _failure_signature(ctx, fb),
                       "baseline_count": len(items0), "baseline_items": items0}
                state.save(ctx.results_dir, {**base, "phase": "retry", "stage": "retry", "retry": rec})
                phase = "retry"
            else:
                fb["retry"] = {"attempted": False}
                fb = finish(ctx, fb)
                state.clear(ctx.results_dir)
                return 0 if fb["ok"] else 1

        # phase == "retry": short targeted turns with measured deltas, each followed by the evaluator and the gates. CORRECTION_FLOOR turns
        # are granted; further turns up to MAX_CORRECTIONS are earned by a falling failing-item count.
        from opencad.stages import model as model_mod
        from opencad.stages import verify as verify_mod
        from opencad.worker import profiles

        st = state.load(ctx.results_dir) or {}
        rec = st.get("retry") or {}
        fb = load_json(ctx.results_dir / "gate_feedback.json")
        while True:
            n = int(rec.get("n") or 0) + (0 if rec.get("in_progress") else 1)  # a continued run re-enters the pending correction
            if n > MAX_CORRECTIONS:
                rec["stopped"] = f"correction budget exhausted ({MAX_CORRECTIONS} turns)"
                break
            key = f"correction-{n}"
            hist = list(rec.get("history") or [])
            if n > CORRECTION_FLOOR and not rec.get("in_progress") and hist and not hist[-1].get("contract_changed"):
                # past the floor a turn is earned by a falling failing-item count; one flat or rising round is allowed (a module that
                # retires compensating geometry exposes items before they can be fixed), two in a row are not
                stagnated, seq = _stagnated(rec.get("baseline_count"), hist)
                if stagnated:
                    rec["stopped"] = f"no progress before {key}: failing items {' -> '.join(str(x) for x in seq[-3:])}"
                    break
            role = "retry" if n == MAX_CORRECTIONS else "correction"  # the last shot goes to the stronger profile
            with telemetry.timed("briefs", ctx.name, ctx.results_dir, key=f"correction-{n}"):
                correction = rec.get("correction") or gates_mod.correction_message(ctx, fb)
                kcl_before = kclsrc_hash(ctx)
                n_fail = len(failing_items(ctx))
            first_pass = not rec.get("in_progress")
            if first_pass:
                if n == 1:
                    orders.supersede(ctx.results_dir, "correction-")
                    if (ctx.load_stage("model") or {}).get("decomposed"):
                        from opencad.stages import decompose

                        decompose.clear_module_targets(ctx)
                rec.pop("subround", None)
                rec.update({"n": n, "correction": correction, "kcl_before": kcl_before, "in_progress": True, "n_fail": n_fail, "contract_sha": _contract_sha(ctx)})
            else:
                correction, kcl_before = rec.get("correction") or correction, rec.get("kcl_before") or kcl_before
                n_fail = int(rec.get("n_fail") or n_fail)
                if rec.get("contract_sha") and rec["contract_sha"] != _contract_sha(ctx):
                    # the orchestrator changed the contract while this round's turns were pending: the saved correction text and the
                    # module attribution describe items that no longer exist; re-measure against the current contract first
                    print(f"== {key}: the contract changed during the round; re-measuring before the next turn ==", flush=True)
                    ctx.contract = load_contract(ctx.contract_path)
                    _clean(ctx, ["verify", "export", "inspect", "edit"])
                    _run_evaluator(ctx)
                    fb = run_gates(ctx, {"retry": {"attempted": True, "corrections": n - 1}})
                    correction = gates_mod.correction_message(ctx, fb)
                    n_fail = len(failing_items(ctx))
                    rec.update({"correction": correction, "n_fail": n_fail, "contract_sha": _contract_sha(ctx), "subround": int(rec.get("subround") or 0) + 1})
                    if fb["ok"] or not fb.get("retryable_failed"):
                        rec.update({"in_progress": False, "stopped": "gates pass" if fb["ok"] else "no retryable failure left"})
                        rec.pop("correction", None)
                        break
            state.save(ctx.results_dir, {**base, "phase": "retry", "stage": key, "retry": rec})
            print(f"== {key} ({role}: {fb.get('failed')}; {n_fail} failing items) ==")
            snap = ctx.results_dir / "snapshots"
            if first_pass or not (snap / "view-all.png").exists():
                try:  # the worker sees the part it is correcting: report views (and the reference compare sheet when input renders exist)
                    with telemetry.timed("snapshots", ctx.name, ctx.results_dir, key=key):
                        verify_mod.render_snapshots(ctx)
                except (OSError, ValueError, RuntimeError) as e:  # never block a correction on a render
                    print(f"snapshots before {key} skipped: {e!r}")
            if (ctx.load_stage("model") or {}).get("decomposed"):
                # decomposed part: the modules that own failing items are corrected first, in parallel; the integrate turn then recomposes
                from opencad.stages import decompose

                # after a mid-round contract change the modules get fresh orders (`correction-4.1-<module>`) for the re-attributed items
                mkey = f"{key}.{rec['subround']}" if rec.get("subround") else key
                mc = decompose.module_corrections(ctx, correction, mkey)  # may raise WorkerPending
                if mc:
                    rec["module_corrections"] = {**(rec.get("module_corrections") or {}), key: {gid: s.get("ok") for gid, s in mc["modules"].items()}}
                    if rec.get("modules_measured") != mkey:
                        # main.py imports the corrected modules: measure them before paying for an integrate turn, and brief it from fresh numbers
                        _clean(ctx, ["verify", "export", "inspect", "edit"])
                        _run_evaluator(ctx)
                        fb = run_gates(ctx, {"retry": {"attempted": True, "corrections": n}})
                        rec["modules_measured"] = mkey
                        if fb["ok"] or not fb.get("retryable_failed"):
                            items_after = failing_items(ctx)
                            rec["history"] = hist + [{"key": key, "role": "modules", "failed_after": fb.get("failed"), "retryable_after": fb.get("retryable_failed"),
                                                      "signature": _failure_signature(ctx, fb), "kcl_changed": kclsrc_hash(ctx) != kcl_before, "incomplete": False,
                                                      "failing_count": len(items_after), "failing_items": items_after, "reverted_to_checkpoint": False,
                                                      "budget_s": None, "contract_changed": bool(rec.get("subround")), "integrate_skipped": True}]
                            rec.update({"in_progress": False, "stopped": "gates pass" if fb["ok"] else "no retryable failure left"})
                            rec.pop("correction", None)
                            break
                        n_fail = len(failing_items(ctx))
                        rec.update({"correction": gates_mod.correction_message(ctx, fb), "n_fail": n_fail})
                        correction = rec["correction"]
                        state.save(ctx.results_dir, {**base, "phase": "retry", "stage": key, "retry": rec})
                        try:
                            with telemetry.timed("snapshots", ctx.name, ctx.results_dir, key=key):
                                verify_mod.render_snapshots(ctx)
                        except (OSError, ValueError, RuntimeError) as e:
                            print(f"snapshots before the {key} integrate turn skipped: {e!r}")
                    correction = (correction + "\n\nModule-level corrections were applied this round to: " + ", ".join(f"`{decompose.src_path(ctx, gid).name}` ({items})" for gid, items in mc["items"].items())
                                  + f". Recompose `{ctx.backend.language.entry}` from the corrected modules (do not redo their work), re-measure the full contract and fix what remains at the integration level.")
            budget = profiles.scaled_budget("correction", n_fail, ctx.backend.engine) if role == "correction" else None
            with telemetry.timed("briefs", ctx.name, ctx.results_dir, key=key):
                model_mod.retry(ctx, rec.get("thread_id") or "", correction, key=key, role=role, budget=budget,
                                images=[snap / "view-compare.png", snap / "view-all.png", ctx.results_dir / "deviation-map.png"])  # may raise WorkerPending
            mdl = ctx.load_stage("model") or {}
            rec["thread_id"] = mdl.get("thread_id") or rec.get("thread_id") or ""
            _clean(ctx, ["verify", "export", "inspect", "edit"])
            _run_evaluator(ctx)
            reverted = False
            if program_failed(ctx) and revert_to_checkpoint(ctx):
                reverted = True
                print(f"== {key}: the corrected source does not execute; reverted to the worker's checkpoint and re-measured ==", flush=True)
                _clean(ctx, ["verify", "export", "inspect", "edit"])
                _run_evaluator(ctx)
            fb = run_gates(ctx, {"retry": {"attempted": True, "corrections": n}})
            sig = _failure_signature(ctx, fb)
            items_after = failing_items(ctx)
            entry = {"key": key, "role": role, "failed_after": fb.get("failed"), "retryable_after": fb.get("retryable_failed"), "signature": sig,
                     "kcl_changed": kclsrc_hash(ctx) != kcl_before, "incomplete": bool((mdl.get("retry") or {}).get("incomplete")),
                     "failing_count": len(items_after), "failing_items": items_after, "reverted_to_checkpoint": reverted, "budget_s": budget,
                     "contract_changed": bool(rec.get("subround"))}
            rec["history"] = hist + [entry]
            rec.pop("correction", None)
            rec["in_progress"] = False
            if fb["ok"] or not fb.get("retryable_failed"):
                rec["stopped"] = "gates pass" if fb["ok"] else "no retryable failure left"
                break
            if tooling_failed(ctx):
                rec["stopped"] = "tooling failure after the correction"
                break
            if reverted:
                # the turn produced nothing measurable; it does not count toward the same-signature stop, but two in a row end the loop
                rec["reverts"] = int(rec.get("reverts") or 0) + 1
                if rec["reverts"] >= MAX_CHECKPOINT_REVERTS:
                    rec["stopped"] = f"{rec['reverts']} corrections in a row left a non-executing source (reverted to the checkpoint each time)"
                    break
                state.save(ctx.results_dir, {**base, "phase": "retry", "stage": key, "retry": rec})
                continue
            rec["reverts"] = 0
            if not entry["kcl_changed"]:
                rec["stopped"] = "the worker changed nothing"
                break
            if sig == rec.get("last_signature"):
                rec["stopped"] = f"same failure after {key}: {sig} ({len(items_after)} failing items)"
                break
            stagnated, seq = _stagnated(rec.get("baseline_count"), rec["history"])
            if stagnated:
                rec["stopped"] = f"no progress after {key}: failing items {' -> '.join(str(x) for x in seq[-3:])}"
                break
            rec["last_signature"] = sig
            state.save(ctx.results_dir, {**base, "phase": "retry", "stage": key, "retry": rec})
        retry_info = {"attempted": True, "corrections": len(rec.get("history") or []), "reason": rec.get("reason"), "gates_before": rec.get("gates_before"),
                      "gates_after": {g["id"]: g["ok"] for g in fb["gates"]}, "history": rec.get("history"), "stopped": rec.get("stopped"),
                      "stuck_class": stuck_class(ctx, rec)}
        fb["retry"] = retry_info
        fb = finish(ctx, fb)
        state.clear(ctx.results_dir)
        return 0 if fb["ok"] else 1
    except WorkerPending as wp:
        return _pending_exit(wp)


def run_single(ctx: Ctx, name: str, *, cont: bool = False) -> int:
    if name == "gates":
        return 0 if run_gates(ctx)["ok"] else 1
    if name == "report":
        fb = ctx.load_stage("gate_feedback") or run_gates(ctx)
        run_report(ctx, fb)
        return 0
    if not cont:
        for key in ORDER_KEYS.get(name, ()):
            orders.supersede(ctx.results_dir, key)
    try:
        data = run_stage(ctx, name)
    except WorkerPending as wp:
        return _pending_exit(wp)
    return 0 if data.get("ok") else 1

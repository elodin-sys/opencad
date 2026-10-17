"""Parts stage: every modelled part design through the ordinary part pipeline, one lane subprocess per design in parallel.

A lane is `python -m opencad assembly part <design>`: blockout when the contract needs one, then `drive` until the pipeline
finishes, waiting on each work order's `done` file. The assembly driver pumps every lane's output and turns each `NEXT` line
into an `EVENT#k` line for the orchestrator (the regression session's lane runner)."""

from __future__ import annotations

import sys
import time
from typing import Any

from opencad.assembly import AsmCtx
from opencad.io import load_json, sha256_file
from opencad.paths import design_dir


def part_done(actx: AsmCtx, design: str) -> dict[str, Any]:
    rd = actx.part_results(design)
    fb = load_json(rd / "gate_feedback.json") if (rd / "gate_feedback.json").exists() else {}
    step = actx.handoff_step(design)
    return {"gates_ok": bool(fb.get("ok")), "summary": fb.get("summary"), "failed": fb.get("failed"), "handoff": str(step) if step.exists() else None,
            "step_sha256": sha256_file(step) if step.exists() else None, "pending": (rd / "pipeline-state.json").exists()}


def blockout_state(actx: AsmCtx, design: str) -> dict[str, Any]:
    p = actx.part_results(design) / "blockout.json"
    blk = load_json(p) if p.exists() else {}
    status = "ok" if blk.get("ok") else "pending" if blk.get("pending") else "failed" if blk else "missing"
    return {"ok": status == "ok", "status": status, "four_ways": (blk.get("snapshots") or {}).get("four-ways"), "iterations": blk.get("iterations_used")}


def blockouts(actx: AsmCtx) -> dict[str, Any]:
    """Every design's blockout checkpoint, read from its own results."""
    out = {d: blockout_state(actx, d) for d in actx.contract.designs()}
    return {"ok": all(v["ok"] for v in out.values()), "designs": out, "failed": [d for d, v in out.items() if not v["ok"]]}


def lane_argv(design: str, backend: str, *, blockout_only: bool = False) -> list[str]:
    return [sys.executable, "-m", "opencad", "assembly", "part", design, "--backend", backend, *(["--blockout-only"] if blockout_only else [])]


def run(actx: AsmCtx, session: Any, *, jobs: int = 4, force: bool = False, blockout_only: bool = False) -> dict[str, Any]:
    """`blockout_only`: every design without a passing blockout runs just its blockout checkpoint (the /initialize-cad stop).
    Lanes are capped by memory as well as `jobs`, and a lane starts only while its reserve fits (always when none is running)."""
    from opencad import resources
    from opencad.truth.regress import Lane

    designs = actx.contract.designs()
    if blockout_only:
        todo = [d for d in designs if force or not blockout_state(actx, d)["ok"]]
    else:
        todo = [d for d in designs if force or not (part_done(actx, d)["handoff"] and not part_done(actx, d)["pending"])]
    lanes = [Lane(case=d, design=d, backend=actx.backend_id) for d in todo]
    cap = min(jobs, resources.memory_slots())
    if cap < jobs:
        session.say(f"== parts: {cap} lanes at once, not {jobs}: {resources.memory_slots()} engine processes fit in {resources.gb(resources.total())} "
                    f"at {resources.gb(resources.runner_budget())} each beside {resources.gb(resources.headroom())} headroom ==")
    queue, running = list(lanes), []
    t0 = noted = time.time()
    try:
        while queue or running:
            for lane in [x for x in running if x.proc is not None and x.proc.poll() is not None]:
                lane.pump.join()
                lane.ended, lane.code = time.time(), lane.proc.returncode
                running.remove(lane)
                session.event(lane, "exit", code=lane.code, wall_s=round(lane.wall_s or 0), **lane.exit_reason())
            while queue and len(running) < cap:
                if running and not resources.fits(resources.lane_reserve()):
                    if time.time() - noted >= resources.WAIT_NOTE_S:
                        session.say(f"== parts: {queue[0].design} waits for memory: available {resources.gb(resources.available())} ==")
                        noted = time.time()
                    break
                lane = queue.pop(0)
                session.start(lane, lane_argv(lane.design, actx.backend_id, blockout_only=blockout_only))
                running.append(lane)
            time.sleep(0.5)
    finally:
        for lane in running:
            if lane.proc is not None and lane.proc.poll() is None:
                lane.proc.terminate()
    if blockout_only:
        return {**blockouts(actx), "wall_s": round(time.time() - t0, 1)}
    return {**summary(actx, {x.design: x.code for x in lanes}), "wall_s": round(time.time() - t0, 1)}


def summary(actx: AsmCtx, codes: dict[str, int | None] | None = None) -> dict[str, Any]:
    """Every design's current gate verdict and handoff, read from its own results (no lanes run)."""
    designs = actx.contract.designs()
    out = {d: {**part_done(actx, d), "lane_code": (codes or {}).get(d), "reused": codes is not None and d not in codes} for d in designs}
    return {"ok": all(v["gates_ok"] and v["handoff"] for v in out.values()), "designs": out, "missing": [d for d, v in out.items() if not v["handoff"]]}


def drive_part(design: str, *, timeout: float | None = None, blockout_only: bool = False) -> int:
    """The lane body: blockout if the contract needs it, then the part pipeline, each worker turn awaited on its done file.
    `blockout_only` runs the blockout whatever the contract's size and stops there."""
    from opencad import worker
    from opencad.orchestrator import Ctx
    from opencad.stages import blockout, pipeline
    from opencad.stages.decompose import acceptance_count
    from opencad.worker import WorkerPending, orders, state
    from opencad.worker.profiles import SMALL_CONTRACT_ITEMS

    if not (design_dir(design) / "contract.yaml").exists():
        print(f"error: {design_dir(design)} is not published", flush=True)
        return 2
    ctx = Ctx.load(design, timeout=timeout or 3600)
    worker.set_continue_cmd(f"python -m opencad assembly part {design} --backend {ctx.backend_id}" + (" --blockout-only" if blockout_only else ""))
    blk = ctx.load_stage("blockout")
    if (not blk or not blk.get("ok")) and (blockout_only or (acceptance_count(ctx.contract) > SMALL_CONTRACT_ITEMS and state.load(ctx.results_dir) is None)):
        cont = bool(orders.find(ctx.results_dir, "blockout-1"))
        while True:
            try:
                blk = blockout.run(ctx, cont=cont)
                break
            except WorkerPending as wp:
                for o in wp.orders:
                    print(orders.next_line(o), flush=True)
                orders.wait(ctx.results_dir)
                cont = True
        print(f"blockout {'ok' if blk.get('ok') else 'FAILED'} for {design}" + ("" if blockout_only else "; continuing to the pipeline"), flush=True)
    if blockout_only:
        return 0 if blk and blk.get("ok") else 1
    st = state.load(ctx.results_dir)
    code = pipeline.run(ctx, cont=bool(st and st.get("command") == "run"), skip_blockout=True)
    while code == 75:
        orders.wait(ctx.results_dir)
        code = pipeline.run(ctx, cont=True)
    return code

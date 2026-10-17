"""`python -m opencad assembly drive <asm>`: draft -> parts -> assemble -> verify -> kinematics -> domains -> simulate -> gates -> report.

One foreground process for the whole machine. Worker turns are awaited on their `done` files; every hand-back prints a numbered
`EVENT#k {...}` line (in-process turns and every part lane alike) so the orchestrator launches the worker and waits for the next
number. The stage reached is kept in results/<backend>/<asm>/pipeline-state.json; re-running `drive` continues there."""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import IO, Any

from opencad import telemetry
from opencad.assembly import AsmCtx, AssemblyError
from opencad.backends.registry import current_id
from opencad.io import dump_json, dump_stage, load_json, utc_now
from opencad.paths import ASSEMBLY_FILE, DESIGNS, RESULTS_BASE, design_dir, parts_root, results_root
from opencad.worker import WorkerPending, orders, state

ORDER = ["draft", "parts", "assemble", "verify", "kinematics", "domains", "simulate", "gates", "report"]
EVALUATOR = ("verify", "kinematics", "domains", "simulate")
MAX_CORRECTIONS = int(os.environ.get("OPENCAD_ASM_CORRECTIONS", "2"))
ARTIFACTS = {"parts": ["parts.json"], "assemble": ["assemble.json"], "verify": ["verify.json", "export"], "kinematics": ["kinematics.json"],
             "domains": ["domains.json", "boundaries"], "simulate": ["simulate.json", "sim"], "gates": ["gate_feedback.json"],
             "report": ["report.md", "report.html", "handoff", "package"]}


class Driver:
    """Runs a dispatch until its orders are done: announces each new order once (NEXT + EVENT#k), then waits on the done files."""

    def __init__(self, session: Any, lane: Any):
        self.session, self.lane = session, lane
        self.announced: set[str] = set()

    def turn(self, fn: Callable[[], Any]) -> Any:
        while True:
            try:
                return fn()
            except WorkerPending as wp:
                fresh = [o for o in wp.orders if str(o.dir) not in self.announced]
                for o in fresh:
                    self.announced.add(str(o.dir))
                    line = orders.next_line(o)
                    print(line, flush=True)
                    self.session.event(self.lane, "next", order=json.loads(line.split(" ", 1)[1]))
                if len(fresh) > 1:
                    self.session.say(f"== {len(fresh)} independent turns: launch them all at once ==")
                for d in sorted({o.dir.parent.parent for o in wp.orders}):
                    orders.wait(d)


@contextmanager
def _lock(results_dir: Any) -> Iterator[None]:
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / ".drive.lock", "a+") as fh:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise AssemblyError(f"another process is driving {results_dir.name} ({results_dir / '.drive.lock'} is held)")
        try:
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _clean(results_dir: Any, stages: list[str]) -> None:
    for s in stages:
        for art in ARTIFACTS.get(s, []):
            p = results_dir / art
            if art == "sim" and p.is_dir():  # simulate adopts the finished runs whose inputs are unchanged, then drops the rest
                shutil.rmtree(results_dir / "sim.prev", ignore_errors=True)
                p.rename(results_dir / "sim.prev")
            elif p.is_dir():
                shutil.rmtree(p)
            elif p.exists():
                p.unlink()


def clear_sources(part_dir: Any) -> None:
    """A fresh assemble turn re-authors the source: drop the previous entry, checkpoint and placements sidecar, in any language."""
    for pattern in ("main.*", "checkpoint.*", "placements.json"):
        for p in part_dir.glob(pattern):
            if p.is_file():
                p.unlink()


def run_evaluator(actx: AsmCtx, stage: str) -> dict[str, Any]:
    from opencad.assembly import domains, kinematics, simulate, verify

    fn = {"verify": verify.run, "kinematics": kinematics.run, "domains": domains.run, "simulate": simulate.run}[stage]
    print(f"== {stage} ({actx.name}) ==", flush=True)
    t0 = time.time()
    try:
        data = fn(actx)
    except Exception as e:  # tooling failure: recorded, never masked as a design verdict
        import traceback

        data = {"ok": False, "error": f"tooling exception: {e!r}", "traceback": traceback.format_exc()[-3000:]}
    actx.write_stage(stage, data)
    telemetry.record("stage", actx.name, telemetry.stage_data(stage, time.time() - t0, data.get("ok"), None), results_dir=actx.results_dir)
    print(f"{stage}: {'ok' if data.get('ok') else 'FAILED'} in {time.time() - t0:.1f} s" + (f" ({data['error'][:300]})" if data.get("error") else ""), flush=True)
    return data


def run_gates(actx: AsmCtx, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    from opencad.assembly import gates

    with telemetry.timed("gates", actx.name, actx.results_dir) as t:
        fb = gates.evaluate(actx)
        t["ok"] = fb["ok"]
    fb.update(extra or {})
    dump_json(actx.results_dir / "gate_feedback.json", fb)
    print("== assembly gates ==", flush=True)
    for g in fb["gates"]:
        mark = "PASS" if g["ok"] else ("n/a " if g["ok"] is None else "FAIL")
        print(f"  [{g['tier']}] {mark} {g['id']}: {g['evidence'][0][:150]}", flush=True)
    print(f"gates: {fb['summary']}", flush=True)
    return fb


def _start(results_dir: Any, st: dict[str, Any] | None, from_stage: str | None, name: str) -> str:
    if st is not None:
        return st["stage"]
    if from_stage:
        if from_stage not in ORDER:
            raise AssemblyError(f"--from-stage must be one of {ORDER}")
        return from_stage
    return "draft" if not (DESIGNS / name / ASSEMBLY_FILE).exists() else "parts"


def drive(name: str, *, backend: str | None = None, from_stage: str | None = None, fresh: bool = False, allow_retry: bool = True, jobs: int = 4,
          out: IO[str] | None = None, amend: str | None = None, stop_after: str | None = None) -> int:
    """`amend`: evaluator evidence for an engineering change on the published contract (one asm-draft turn), then re-place from assemble.
    `stop_after` is the /initialize-cad checkpoint: "draft" stops once the assembly and part contracts are published, "blockout" once every
    part's blockout has run; the state is cleared, so a plain `drive` later starts at parts. With it, `amend` is a pre-build revision."""
    from opencad.truth.regress import Lane, Session

    if stop_after not in (None, "draft", "blockout"):
        raise AssemblyError(f"--stop-after must be draft or blockout, not {stop_after!r}")
    if stop_after and from_stage not in (None, "draft"):
        raise AssemblyError(f"--stop-after (the initialize checkpoint) does not combine with --from-stage {from_stage}")
    be = backend or current_id()
    results_dir = results_root(be) / name
    with _lock(results_dir):
        st = None if fresh or amend else state.load(results_dir)
        if st is not None and st.get("command") != "assembly":
            st = None
        stage = "assemble" if amend and not stop_after else _start(results_dir, st, from_stage, name)
        if stop_after and ORDER.index(stage) > ORDER.index("parts"):
            raise AssemblyError(f"{name} is past the initialize checkpoint (at {stage}); continue it without --stop-after, or restart with --fresh")
        rec: dict[str, Any] = dict((st or {}).get("retry") or {})
        if st is None and not stop_after:  # the build that follows the checkpoint cleans what a revision made stale
            _clean(results_dir, ORDER[ORDER.index(stage):])
            if stage in ("draft", "parts", "assemble"):
                for key in ("assemble", "correction-"):
                    orders.supersede(results_dir, key)
                if not amend:
                    clear_sources(parts_root(be) / name)
        tag = os.environ.get("OPENCAD_TAG") or f"asm-{name}"
        session = Session(RESULTS_BASE / "_logs" / tag, out)
        (RESULTS_BASE / "_logs" / tag).mkdir(parents=True, exist_ok=True)
        driver = Driver(session, Lane(case=name, design=name, backend=be))
        session.say(f"== assembly {name} ({be}): from {stage}{' (continuing)' if st else ''}; logs {RESULTS_BASE / '_logs' / tag} ==")
        base = {"command": "assembly", "assembly": name, "backend": be}
        fb: dict[str, Any] = load_json(results_dir / "gate_feedback.json") if (results_dir / "gate_feedback.json").exists() else {}
        t0, started = time.time(), utc_now()
        if amend:
            from opencad.assembly import draft

            res = (draft.revise if stop_after else draft.amend)(driver.turn, name, amend)
            dump_stage(results_dir, "revise" if stop_after else "amend", res)
            if not res.get("ok"):
                session.say(f"== {'revision' if stop_after else 'amendment'} not publishable: {res.get('problems')} ==")
                return 1
        stages = ORDER[ORDER.index(stage):]
        if stop_after:
            stages = [s for s in stages if s == "draft" or (s == "parts" and stop_after == "blockout")]
        for s in stages:
            state.save(results_dir, {**base, "stage": s, "retry": rec})
            if s == "draft":
                from opencad.assembly import draft

                res = draft.run(driver.turn, name)
                dump_stage(results_dir, "draft", res)
                if not res.get("ok"):
                    session.say(f"== draft FAILED at {res.get('stage')}: {res.get('problems')} ==")
                    state.clear(results_dir)
                    return 1
                continue
            actx = AsmCtx.load(name, backend=be)
            if s == "parts":
                from opencad.assembly import parts

                if stop_after:
                    parts.run(actx, session, jobs=jobs, blockout_only=True)
                    continue
                res = parts.run(actx, session, jobs=jobs)
                actx.write_stage("parts", res)
                if res["missing"]:
                    session.say(f"== parts: no handoff STEP for {res['missing']}; the assembly cannot be placed ==")
                    state.clear(results_dir)
                    return 1
            elif s == "assemble":
                from opencad.assembly import assemble

                res = assemble.run(driver.turn, actx)
                actx.write_stage("assemble", res)
                rec.update(thread_id=res.get("thread_id"), n=0)
            elif s in EVALUATOR:
                run_evaluator(actx, s)
            elif s == "gates":
                fb = run_gates(actx)
                fb = _corrections(driver, actx, fb, rec, base, allow_retry)
            elif s == "report":
                from opencad.assembly import report

                print("== report ==", flush=True)
                data = report.build(actx, fb)
                actx.write_stage("report", data)
                session.say(f"report: {data['report_html']} verdict {data['verdict']}")
        state.clear(results_dir)
        if stop_after:
            return _checkpoint(session, AsmCtx.load(name, backend=be), stop_after)
        telemetry.record("attempt", name, {"arm": "assembly", "case": name, "started": started, "seconds": round(time.time() - t0, 1),
                                           "verdict": "PASS" if fb.get("ok") else "FAIL",
                                           "gates": {"pass": len(fb.get("passed") or []), "fail": len(fb.get("failed") or [])}}, results_dir=results_dir)
        session.say(f"== assembly {name} ({be}): {'PASS' if fb.get('ok') else 'FAIL'} ({fb.get('summary')}) ==")
        return 0 if fb.get("ok") else 1


def _checkpoint(session: Any, actx: AsmCtx, stop_after: str) -> int:
    """What /initialize-cad reviews: the published bundles and, after the blockouts, each part's verdict and four-view render."""
    from opencad.assembly.parts import blockouts

    blk = blockouts(actx) if stop_after == "blockout" else None
    session.say(f"== initialize checkpoint {actx.name} ({actx.backend_id}): assembly {actx.design_dir} ==")
    for d in actx.contract.designs():
        b = (blk or {"designs": {}})["designs"].get(d)
        session.say(f"  part {d}: {design_dir(d)}" + (f"; blockout {b['status']}" + (f" {b['four_ways']}" if b["four_ways"] else "") if b else ""))
    session.say(f"== build: /create-cad designs/{actx.name} (python -m opencad assembly drive {actx.name} --backend {actx.backend_id}) ==")
    return 0 if blk is None or blk["ok"] else 1


def _corrections(driver: Driver, actx: AsmCtx, fb: dict[str, Any], rec: dict[str, Any], base: dict[str, Any], allow_retry: bool) -> dict[str, Any]:
    """Up to MAX_CORRECTIONS turns on the assemble thread for failures the assembly source can fix; stops on no progress."""
    from opencad.assembly import assemble, gates

    history = list(rec.get("history") or [])
    while allow_retry and fb.get("retryable_failed") and int(rec.get("n") or 0) < MAX_CORRECTIONS:
        n = int(rec.get("n") or 0) + 1
        msg = rec.get("message") if rec.get("in_progress") else gates.correction_message(actx, fb)
        rec.update(n=n - 1, in_progress=True, message=msg)
        state.save(actx.results_dir, {**base, "stage": "gates", "retry": rec})
        print(f"== assembly correction-{n}: {fb.get('retryable_failed')} ==", flush=True)
        res = assemble.run(driver.turn, actx, key=f"correction-{n}", message=msg, resume=rec.get("thread_id"), role="correction")
        rec["thread_id"] = res.get("thread_id") or rec.get("thread_id")
        for s in EVALUATOR:
            run_evaluator(actx, s)
        before = set(fb.get("failed") or [])
        fb = run_gates(actx)
        history.append({"n": n, "failed_before": sorted(before), "failed_after": fb.get("failed")})
        rec.update(n=n, in_progress=False, history=history)
        rec.pop("message", None)
        state.save(actx.results_dir, {**base, "stage": "gates", "retry": rec})
        if set(fb.get("failed") or []) >= before:
            break
    if history:
        fb["retry"] = {"attempted": True, "corrections": len(history), "history": history,
                       "stopped": "gates pass" if fb.get("ok") else ("budget" if len(history) >= MAX_CORRECTIONS else "no progress or nothing retryable")}
        dump_json(actx.results_dir / "gate_feedback.json", fb)
    return fb


def run_stage(name: str, stage: str, *, backend: str | None = None) -> int:
    """Re-run one evaluator stage (or gates/report) on an assembled machine: development and after a control-plane fix."""
    actx = AsmCtx.load(name, backend=backend)
    if stage == "parts":
        from opencad.assembly.parts import summary

        data = summary(actx)
        actx.write_stage("parts", data)
        print(f"parts: {'ok' if data['ok'] else 'FAILED'} " + ", ".join(f"{d}={v['summary']}" for d, v in data["designs"].items()))
        return 0 if data["ok"] else 1
    if stage in EVALUATOR:
        return 0 if run_evaluator(actx, stage).get("ok") else 1
    if stage == "gates":
        return 0 if run_gates(actx)["ok"] else 1
    if stage == "report":
        from opencad.assembly import report

        fb = load_json(actx.results_dir / "gate_feedback.json") if (actx.results_dir / "gate_feedback.json").exists() else run_gates(actx)
        data = report.build(actx, fb)
        actx.write_stage("report", data)
        print(f"report: {data['report_html']} verdict {data['verdict']}")
        return 0
    raise AssemblyError(f"stage {stage!r} is not re-runnable on its own (use `drive --from-stage {stage}`)")

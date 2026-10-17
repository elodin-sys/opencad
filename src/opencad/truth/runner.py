"""Headless case run: sequester truth, initialize (worker draft + blockout), pipeline, restore, score.

Worker turns are handed back to the orchestrating Cursor agent: when a stage issues a work order the
run stops with exit 75, truth stays vaulted, and the attempt state is persisted next to the design's
results. `--continue` re-enters at the recorded point; truth is restored only when the attempt ends
(scored, failed) or by `truth restore`.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml

from opencad import initialize
from opencad.contract import ContractError, check_bundle, load_contract, publish_bundle, stage_bundle
from opencad.io import dump_json, load_json, utc_now
from opencad.orchestrator import Ctx, PipelineError
from opencad.backends.registry import current_id, get
from opencad.paths import DESIGNS, design_dir, part_dir
from opencad.paths import results_dir as results_of
from opencad.reference.mesh import ingest
from opencad.reference.profile import ingest_profile
from opencad.truth.manifest import CaseManifest, case_dir
from opencad.truth import scorer
from opencad.worker import EXIT_WORKER_PENDING, WorkerPending, orders

VAULT = Path(os.environ.get("OPENCAD_VAULT", Path.home() / ".cache" / "opencad-vault"))


# scorecards and attempts.yaml carry expected values and verdicts: a worker must not read them while any holder is active
SEQUESTERED = ("truth", "manifest.yaml", "mutants.yaml", "scorecards", "attempts.yaml")
ATTEMPT_STATE = "attempt-state.json"
ECR_STATE = "ecr-attempt-state.json"


def vault_path(case_id: str) -> Path:
    return VAULT / case_id


def _lock_file(dst: Path) -> Path:
    """Beside the vault dir, not in it: it outlives the restore that removes the dir."""
    return dst.with_name(dst.name + ".lock")


@contextmanager
def case_lock(case_id: str) -> Iterator[None]:
    """Serialises sequester, restore and every case-file write across processes."""
    lock = _lock_file(vault_path(case_id))
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a+") as lf:
        fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        yield


def case_file(case_id: str, name: str, *, tree: Path | None = None) -> Path:
    """Where a sequestered case file lives now: the vault while any holder is active, else the tree."""
    held = vault_path(case_id)
    return held / name if (held / "holders.json").exists() else (tree or case_dir(case_id)) / name


def _merge_back(src: Path, target: Path) -> None:
    if src.is_dir():
        target.mkdir(parents=True, exist_ok=True)
        for child in src.iterdir():
            dest = target / child.name
            if dest.is_dir():
                shutil.rmtree(dest)
            elif dest.exists():
                dest.unlink()
            shutil.move(str(child), str(dest))
        src.rmdir()
        return
    if target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()
    shutil.move(str(src), str(target))


def live_holders(case_id: str) -> list[str]:
    """Active holders of the case vault whose process is still running (holder ids start with the pid)."""
    p = vault_path(case_id) / "holders.json"
    try:
        active = json.loads(p.read_text(encoding="utf-8")).get("active") or []
    except (OSError, json.JSONDecodeError):
        return []
    live = []
    for h in active:
        try:
            os.kill(int(str(h).split("-")[0]), 0)
        except ProcessLookupError:
            continue
        except (PermissionError, ValueError):
            pass
        live.append(h)
    return live


def vault_dirs(case_id: str) -> list[Path]:
    """The case's vault dir, when a run left one."""
    held = vault_path(case_id)
    return [held] if held.is_dir() else []


class Sequester:
    """Move truth/, manifest.yaml and mutants.yaml out of the repository while a worker can read the tree.

    Concurrent holders share `VAULT/<case>`. `keep()` leaves a pending token so files stay vaulted
    for `--continue`; `attach()` consumes that token. The last holder without a pending token restores.
    """

    def __init__(self, case_id: str, dst: Path | None = None, *, consume_pending: bool = False):
        self.case = case_dir(case_id)
        self.src = self.case / "truth"
        self.dst = Path(dst) if dst is not None else vault_path(case_id)
        self._consume_pending = consume_pending
        self._keep = False
        self._holder_id = f"{os.getpid()}-{time.time_ns()}"

    @classmethod
    def attach(cls, case_id: str, dst: Path) -> "Sequester":
        if Path(dst).exists():
            return cls(case_id, Path(dst), consume_pending=True)
        if (case_dir(case_id) / "manifest.yaml").exists():
            print(f"== {case_id}: vault {dst} is gone but truth is back in the tree; sequestering again ==", flush=True)
            return cls(case_id)
        raise PipelineError(
            f"vault {dst} for {case_id} is gone and truth is not in the tree; run `python -m opencad.truth restore {case_id}`"
        )

    def keep(self) -> None:
        self._keep = True

    def _lock_path(self) -> Path:
        return _lock_file(self.dst)

    def _state_path(self) -> Path:
        return self.dst / "holders.json"

    def _load_state(self) -> dict[str, Any]:
        p = self._state_path()
        if not p.exists():
            return {"active": [], "pending": 0}
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"active": [], "pending": 0}
        data.setdefault("active", [])
        data.setdefault("pending", 0)
        return data

    def _save_state(self, data: dict[str, Any]) -> None:
        self._state_path().write_text(json.dumps(data), encoding="utf-8")

    def _with_state(self, fn):
        """Run fn(state) under the case lock; fn returns the state to save, or None when it restored the case."""
        VAULT.mkdir(parents=True, exist_ok=True)
        self.dst.mkdir(parents=True, exist_ok=True)
        with self._lock_path().open("a+") as lf:
            fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
            state = fn(self._load_state())
            if state is not None:
                self._save_state(state)
            return state

    def _move_into_vault(self) -> None:
        self.dst.mkdir(parents=True, exist_ok=True)
        for name in SEQUESTERED:
            src = self.case / name
            dest = self.dst / name
            if src.exists() and not dest.exists():
                shutil.move(str(src), str(dest))

    def _restore(self) -> None:
        if not self.dst.exists():
            return
        for name in SEQUESTERED:
            v = self.dst / name
            if v.exists():
                _merge_back(v, self.case / name)
        for leftover in (self._state_path(), self.dst / "holders.lock"):
            leftover.unlink(missing_ok=True)
        if self.dst.exists() and not any(self.dst.iterdir()):
            self.dst.rmdir()

    def __enter__(self) -> "Sequester":
        def _enter(state: dict[str, Any]) -> dict[str, Any]:
            self._move_into_vault()
            if self._consume_pending and state.get("pending", 0) > 0:
                state["pending"] = state["pending"] - 1
            active = list(state.get("active") or [])
            active.append(self._holder_id)
            state["active"] = active
            return state

        self._with_state(_enter)
        return self

    def __exit__(self, *exc: Any) -> None:
        if not self.dst.exists():
            return

        def _exit(state: dict[str, Any]) -> dict[str, Any] | None:
            state["active"] = [h for h in (state.get("active") or []) if h != self._holder_id]
            if self._keep:
                state["pending"] = int(state.get("pending") or 0) + 1
            if state["active"] or int(state.get("pending") or 0) > 0:
                return state
            self._restore()
            return None

        self._with_state(_exit)


def attempts_path(case_id: str) -> Path:
    return case_file(case_id, "attempts.yaml")


def log_attempt(case_id: str, entry: dict[str, Any]) -> None:
    with case_lock(case_id):
        p = attempts_path(case_id)
        data = yaml.safe_load(p.read_text()) if p.exists() else {"attempts": []}
        data["attempts"] = data.get("attempts") or []
        data["attempts"].append(entry)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def log_score(case_id: str, arm_id: str, card: dict[str, Any], *, seconds: float) -> None:
    """Append a score-only attempt (no hosted run)."""
    log_attempt(
        case_id,
        {
            "started": card.get("scored_at") or utc_now(),
            "finished": utc_now(),
            "arm": arm_id,
            "design": card.get("design"),
            "resume_from": "score",
            "stage_reached": "scored",
            "scorecard": {
                "verdict": card.get("verdict"),
                "summary": card.get("summary"),
                "failed": [c["id"] for c in card.get("checks", []) if not c.get("ok")],
            },
            "step_sha256": (card.get("hash_binding") or {}).get("step_sha256"),
            "seconds": round(seconds),
            "backend": current_id(),
        },
    )


def reset_design(design: str) -> None:
    for d in (
        design_dir(design),
        part_dir(design),
        results_of(design),
        DESIGNS / f".staging-{design}",
        DESIGNS / f".codex-draft-{design}",
    ):
        if d.exists():
            shutil.rmtree(d)


def reset_run(design: str) -> None:
    """This backend's part and results only: the published design is shared by every backend's run."""
    for d in (part_dir(design), results_of(design)):
        if d.exists():
            shutil.rmtree(d)


def attempt_state_path(design: str, name: str = ATTEMPT_STATE) -> Path:
    return results_of(design) / name


def pending_attempts(m: CaseManifest) -> list[dict[str, Any]]:
    """Interrupted attempts (a worker turn pending) for any arm of the case."""
    out = []
    for arm in m.arms:
        for name in (ATTEMPT_STATE, ECR_STATE):
            p = attempt_state_path(arm.design, name)
            if p.exists():
                st = load_json(p)
                out.append(
                    {
                        "arm": arm.id,
                        "design": arm.design,
                        "point": st.get("point"),
                        "order": st.get("order"),
                        "kind": "ecr" if name == ECR_STATE else "run",
                    }
                )
    return out


def _pending(entry: dict[str, Any], wp: WorkerPending | None, arm_id: str) -> dict[str, Any]:
    if wp is not None:
        for o in wp.orders:
            print(
                f"== worker turn pending: {o.id} ({o.role}, model {o.model}, budget {o.budget_s:.0f} s) ==", flush=True
            )
            print(orders.next_line(o), flush=True)
    return {
        "pending": True,
        "arm": arm_id,
        "design": entry.get("design"),
        "stage_reached": entry.get("stage_reached"),
        "order": wp.order.id if wp else None,
    }


def prior_stuck_class(case_id: str, arm_id: str) -> str | None:
    with case_lock(case_id):
        p = attempts_path(case_id)
        attempts = (yaml.safe_load(p.read_text()) or {}).get("attempts") or [] if p.exists() else []
    bid = current_id()
    for a in reversed(attempts):
        if a.get("arm") != arm_id or a.get("resume_from") == "score":
            continue
        if (a.get("backend") or "zoo") != bid:
            continue
        return a.get("stuck_class")
    return None


def run_case(
    case_id: str,
    m: CaseManifest,
    arm_id: str,
    *,
    force: bool = False,
    timeout: float | None = None,
    stop_after: str | None = None,
    resume_from: str | None = None,
    allow_retry: bool = True,
    cont: bool = False,
    decompose: bool | None = None,
) -> dict[str, Any]:
    """resume_from: 'publish' takes designs/.staging-<design>; 'blockout' keeps a published design; 'pipeline' also keeps the blockout;
    'retry' keeps the modelled part and its thread (re-verify, gates, bounded retry). `cont` continues an attempt a worker handback interrupted."""
    arm = next((a for a in m.arms if a.id == arm_id), None)
    if arm is None:
        raise PipelineError(f"arm {arm_id} not in manifest {case_id}")
    design = arm.design
    case = case_dir(case_id)
    state_path = attempt_state_path(design)
    from opencad.backends.base import EngineError

    if cont:
        if not state_path.exists():
            raise PipelineError(f"nothing to continue for {case_id}/{arm_id}: {state_path} missing")
        st = load_json(state_path)
        entry: dict[str, Any] = st["entry"]
        t0 = float(st["t0"])
        point = st["point"]
        cont_point = point
        stop_after, resume_from, allow_retry = st.get("stop_after"), st.get("resume_from"), st.get("allow_retry", True)
        timeout, decompose = st.get("timeout"), st.get("decompose")
        seq = Sequester.attach(case_id, Path(st["vault"]))
        print(f"== continuing {case_id}/{arm_id} at {point} ==", flush=True)
    else:
        entry = {
            "started": utc_now(),
            "arm": arm_id,
            "backend": current_id(),
            "design": design,
            "stage_reached": "init",
            "force": force,
            "resume_from": resume_from,
        }
        staging = DESIGNS / f".staging-{design}"
        if resume_from == "publish":
            if not staging.exists():
                raise PipelineError(f"--resume-from publish needs {staging}")
        elif resume_from:
            if not (design_dir(design) / "contract.yaml").exists():
                raise PipelineError(f"--resume-from needs a published designs/{design}")
            if force and resume_from == "blockout":
                reset_run(design)
        elif design_dir(design).exists() or results_of(design).exists():
            entry_path = part_dir(design) / get().language.entry
            model_json = results_of(design) / "model.json"
            if (
                not force
                and entry_path.exists()
                and model_json.exists()
                and (design_dir(design) / "contract.yaml").exists()
            ):
                # keep the modelled part and its worker thread: a fresh plan+model repeats the failure it did not learn from
                resume_from = "retry"
                entry["resume_from"] = "retry"
                entry["resume_reason"] = (
                    "modelled part exists; --force redoes plan+model, --resume-from pipeline keeps the blockout only"
                )
                print(
                    f"== {case_id}/{arm_id}: {entry_path} exists; continuing from the modelled part (--resume-from retry). Pass --force to redo everything. ==",
                    flush=True,
                )
            elif not force:
                raise PipelineError(
                    f"{design_dir(design)} or {results_of(design)} exists; pass --force to redo the attempt or --resume-from publish|blockout|pipeline|retry"
                )
            else:
                reset_design(design)
        pf = get().engine.preflight()
        if not pf.get("ok") and pf.get("class") == "billing":
            from opencad.backends.base import BillingError

            raise BillingError(pf.get("error") or "backend preflight failed")
        t0 = time.time()
        if decompose is None:
            stuck = prior_stuck_class(case_id, arm_id)
            if stuck and (stuck.startswith("kernel") or stuck == "incomplete-checkpoint"):
                decompose = True
                entry["decompose_reason"] = f"previous attempt stuck: {stuck}"
                print(
                    f"== {case_id}/{arm_id}: previous attempt was stuck ({stuck}); modelling through decomposition ==",
                    flush=True,
                )
        entry["decompose"] = decompose
        point = (
            "draft"
            if not resume_from
            else ("publish" if resume_from == "publish" else "blockout" if resume_from == "blockout" else "pipeline")
        )
        cont_point = None
        seq = Sequester(case_id)

    def save_state(pt: str, order_id: str | None = None) -> None:
        dump_json(
            state_path,
            {
                "case": case_id,
                "arm": arm_id,
                "design": design,
                "entry": entry,
                "t0": t0,
                "vault": str(seq.dst),
                "point": pt,
                "stop_after": stop_after,
                "resume_from": resume_from,
                "allow_retry": allow_retry,
                "timeout": timeout,
                "order": order_id,
                "decompose": decompose,
            },
        )

    with seq:
        entry["truth_sequestered_to"] = str(seq.dst)
        try:
            staging = DESIGNS / f".staging-{design}"
            if point == "draft":
                save_state("draft")
                if cont_point != "draft":
                    staging = stage_bundle(design)
                    if arm.reference:
                        r = arm.reference
                        planes = [(s.split("=")[0], float(s.split("=")[1])) for s in r.sections] or None
                        ingest(
                            case / r.mesh,
                            staging / "reference",
                            units=r.units,
                            axes=r.axes,
                            datum=r.datum,
                            expect_size_mm=r.expect_size_mm,
                            section_planes=planes,
                        )
                    if arm.profile:
                        pr = arm.profile
                        ingest_profile(
                            case / pr.table,
                            staging / "reference",
                            units=pr.units,
                            sheet=pr.sheet,
                            columns=tuple(pr.columns),
                            skip=pr.skip,
                            sides=[tuple(s) for s in pr.sides] if pr.sides else None,
                            scale_to_mm=pr.scale_to_mm,
                        )
                sources = [case / p for p in arm.inputs]
                images = [case / p for p in arm.images]
                entry["stage_reached"] = "draft"
                d = initialize.draft(
                    staging,
                    design,
                    m.intent,
                    sources=sources,
                    images=images,
                    notes=arm.notes,
                    timeout=timeout,
                    cont=cont_point == "draft",
                    checks=[(o.kind, o.id) for o in m.observables if o.kind not in (*PARITY_UNGATED_KINDS, "deviation")],
                )
                entry["draft"] = {
                    "ok": d["ok"],
                    "rounds": len(d["rounds"]),
                    "thread_id": d["thread_id"],
                    "problems": d["problems"],
                }
                if not d["ok"]:
                    entry["stage_reached"] = "draft-failed"
                    state_path.unlink(missing_ok=True)
                    return _finish(case_id, entry, t0)
                gap = parity_gap(m, staging, design)
                if gap or entry.get(
                    "parity"
                ):  # a continued attempt re-audits the fixed contract: the finished round must still be consumed
                    entry.setdefault(
                        "parity", {"before": [f"{f['status']} {f['kind']} {f['observable']}" for f in gap]}
                    )
                    problems = initialize.parity_round(
                        staging, design, gap, thread=d["thread_id"], timeout=timeout
                    )  # may raise WorkerPending
                    gap = parity_gap(m, staging, design)
                    entry["parity"]["after"] = [f"{f['status']} {f['kind']} {f['observable']}" for f in gap]
                    if gap or problems:
                        entry["stage_reached"] = "contract-parity"
                        entry["error"] = (
                            f"contract-parity: {len(gap)} checks still missing or looser, {len(problems)} bundle problems after the parity round"
                        )
                        state_path.unlink(missing_ok=True)
                        return _finish(case_id, entry, t0)
                publish_bundle(staging, design)
                entry["stage_reached"] = "published"
                if stop_after == "draft":
                    state_path.unlink(missing_ok=True)
                    return _finish(case_id, entry, t0)
                point = "blockout"
            elif point == "publish":
                problems = check_bundle(staging, design)
                if problems:
                    raise PipelineError("staging bundle problems:\n  - " + "\n  - ".join(problems))
                publish_bundle(staging, design)
                entry["stage_reached"] = "published"
                point = "blockout"

            ctx = Ctx.load(design, timeout=timeout or 3600)
            from opencad.stages import blockout as blockout_mod
            from opencad.stages import pipeline

            if point == "blockout":
                save_state("blockout")
                from opencad.stages.decompose import acceptance_count
                from opencad.worker.profiles import SMALL_CONTRACT_ITEMS

                n_items = acceptance_count(ctx.contract)
                if resume_from in ("pipeline", "retry") and (ctx.load_stage("blockout") or {}).get("ok"):
                    b = ctx.load_stage("blockout")
                elif n_items <= SMALL_CONTRACT_ITEMS and stop_after != "blockout":
                    b = {
                        "ok": False,
                        "skipped": f"{n_items} acceptance items (<= {SMALL_CONTRACT_ITEMS}): the model turn starts with the envelope",
                    }
                    print(f"== {case_id}/{arm_id}: no blockout turn, {b['skipped']} ==", flush=True)
                else:
                    b = blockout_mod.run(ctx, max_iterations=2, cont=cont_point == "blockout")
                entry["blockout"] = {
                    "ok": b["ok"],
                    "iterations": b.get("iterations_used"),
                    "thread_id": b.get("thread_id"),
                    "skipped": b.get("skipped"),
                }
                entry["stage_reached"] = "blockout"
                if stop_after == "blockout":
                    state_path.unlink(missing_ok=True)
                    return _finish(case_id, entry, t0)
                point = "pipeline"

            b = ctx.load_stage("blockout") or {"ok": False}
            from_stage = "plan"
            if resume_from == "retry":
                if not (ctx.kcl_target.exists() and (ctx.load_stage("model") or {}).get("thread_id") is not None):
                    raise PipelineError(f"--resume-from retry needs {ctx.entry} and a model.json thread")
                from_stage = "verify"
            save_state("pipeline")
            code = pipeline.run(
                ctx,
                skip_blockout=not b.get("ok"),
                from_stage=from_stage,
                allow_retry=allow_retry,
                cont=cont_point == "pipeline",
                decompose=decompose,
            )
            if code == EXIT_WORKER_PENDING:
                seq.keep()
                pend = orders.pending(ctx.results_dir)
                save_state("pipeline", pend[-1].id if pend else None)
                return _pending(entry, None, arm_id)
            if code == pipeline.EXIT_TOOLING:
                # a pipeline exception in a worker stage: keep truth vaulted and the state intact; fix, then `--continue`
                seq.keep()
                save_state("pipeline")
                print(
                    f"== {case_id}/{arm_id}: tooling exception in the pipeline; truth stays vaulted; fix and re-run with --continue ==",
                    flush=True,
                )
                return {
                    "pending": True,
                    "tooling_error": True,
                    "arm": arm_id,
                    "design": design,
                    "stage_reached": entry.get("stage_reached"),
                }
            fb = load_json(results_of(design) / "gate_feedback.json")
            rt = fb.get("retry") or {}
            entry["pipeline"] = {
                "exit": code,
                "gates": fb.get("summary"),
                "failed": fb.get("failed"),
                "retry": rt.get("attempted"),
                "corrections": rt.get("corrections"),
                "stopped": rt.get("stopped"),
            }
            entry["stage_reached"] = "pipeline"
            mdl = ctx.load_stage("model") or {}
            stuck = rt.get("stuck_class") or (
                "incomplete-checkpoint" if mdl.get("self_reported_incomplete") and code != 0 else None
            )
            if stuck:
                # the stuck rule fires after ONE attempt of this class: another plan+model against the same kernel limit has no new information
                entry["stuck_class"] = stuck
                entry["recommendation"] = (
                    "decompose: partition the contract into feature-group modules (python -m opencad run <part> --decompose) "
                    "instead of re-running plan+model"
                    if stuck.startswith("kernel") or stuck == "incomplete-checkpoint"
                    else "inspect the correction history in gate_feedback.json before another attempt"
                )
                print(f"== stuck rule: {stuck}; {entry['recommendation']} ==", flush=True)
        except WorkerPending as wp:
            seq.keep()
            save_state(point, wp.order.id)
            return _pending(entry, wp, arm_id)
        except (ContractError, PipelineError, EngineError) as e:
            entry["error"] = str(e)[:2000]
            state_path.unlink(missing_ok=True)
            return _finish(case_id, entry, t0)
        # score while this process still holds the case: another backend may hold it too, so the truth files are read from
        # wherever they are (the vault until the last holder leaves), never assumed back in the tree
        state_path.unlink(missing_ok=True)
        _score_into(entry, case_id, m, arm_id, seq)
    return _finish(case_id, entry, t0)


PARITY_GATED = ("missing", "looser")
PARITY_UNGATED_KINDS = (
    "probe",
)  # probe points are the evaluator's own samples; a worker cannot place its probes on them from the sources


def parity_gap(m: CaseManifest, staging: Path, design: str) -> list[dict[str, Any]]:
    """Truth observables the drafted contract lacks or states more loosely (evaluator-side; the findings' details stay here)."""
    from opencad import telemetry
    from opencad.truth import parity

    with telemetry.timed("parity", design, results_of(design)) as t:
        c = load_contract(Path(staging) / "contract.yaml")
        gap = [f for f in parity.audit(m, c) if f["status"] in PARITY_GATED and f["kind"] not in PARITY_UNGATED_KINDS]
        t.update({"ok": not gap, "gap": len(gap)})
    return gap


def truth_root(case_id: str, seq: Sequester) -> Path:
    """The case files for scoring: the live tree when it holds the manifest, else this run's vault."""
    live = case_dir(case_id)
    return live if (live / "manifest.yaml").exists() else Path(seq.dst)


def _score_into(entry: dict[str, Any], case_id: str, m: CaseManifest, arm_id: str, seq: Sequester) -> None:
    from opencad import telemetry

    design = entry.get("design") or case_id
    with telemetry.timed("score", design, results_of(design)) as t:
        try:
            card = scorer.score_case(case_id, m, arm_id, case_root=truth_root(case_id, seq))
            entry["scorecard"] = {
                "verdict": card["verdict"],
                "summary": card["summary"],
                "accuracy_score": card.get("accuracy_score"),
                "failed": [c["id"] for c in card["checks"] if not c.get("ok")],
            }
            entry["stage_reached"] = "scored"
            t["ok"] = card["verdict"] == "PASS"
        except Exception as e:
            entry["score_error"] = f"{type(e).__name__}: {e}"


def run_ecr(
    case_id: str,
    m: CaseManifest,
    arm_id: str,
    *,
    timeout: float | None = None,
    expect_infeasible: bool = False,
    keep_kcl: bool = False,
    cont: bool = False,
) -> dict[str, Any]:
    """A change-request case: sequester it, run `opencad ecr` on the arm's design with the arm's request and
    `inputs/contract-delta.yaml`, restore, score results/<design>/ecr/<label>/handoff, log the attempt.

    The base part is restored afterwards unless `keep_kcl`, so every request is judged against the same passing design.
    A worker handback leaves the case vaulted and the base KCL copy in results/<design>/ until `--continue` finishes the attempt.
    """
    from opencad.backends.base import EngineError
    from opencad.stages import ecr as ecr_mod

    arm = next((a for a in m.arms if a.id == arm_id), None)
    if arm is None:
        raise PipelineError(f"arm {arm_id} not in manifest {case_id}")
    if not arm.ecr:
        raise PipelineError(f"arm {arm_id} of {case_id} has no `ecr` label; `truth ecr` is for change-request cases")
    case = case_dir(case_id)
    requests = [case / p for p in arm.inputs if p.endswith(".md")]
    if len(requests) != 1:
        raise PipelineError(
            f"arm {arm_id} must list exactly one markdown request among its inputs, found {len(requests)}"
        )
    delta = case / "inputs" / "contract-delta.yaml"
    lang = get().language
    kcl = part_dir(arm.design) / lang.entry
    if not kcl.exists():
        raise PipelineError(f"{kcl} missing: the base design must pass first")
    state_path = attempt_state_path(arm.design, ECR_STATE)
    base_copy = results_of(arm.design) / f"ecr-base-{arm.ecr}{lang.suffixes[0]}"
    if cont:
        if not state_path.exists():
            raise PipelineError(f"nothing to continue for {case_id}/{arm_id}: {state_path} missing")
        st = load_json(state_path)
        entry: dict[str, Any] = st["entry"]
        t0 = float(st["t0"])
        expect_infeasible, keep_kcl, timeout = (
            st.get("expect_infeasible", expect_infeasible),
            st.get("keep_kcl", keep_kcl),
            st.get("timeout"),
        )
        seq = Sequester.attach(case_id, Path(st["vault"]))
        print(f"== continuing {case_id}/{arm_id} (ecr {arm.ecr}) ==", flush=True)
    else:
        base_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(kcl, base_copy)
        entry = {
            "started": utc_now(),
            "arm": arm_id,
            "design": arm.design,
            "ecr": arm.ecr,
            "stage_reached": "init",
            "request": str(requests[0]),
            "delta": str(delta) if delta.exists() else None,
            "expect_infeasible": expect_infeasible,
        }
        t0 = time.time()
        seq = Sequester(case_id)
    pending = False
    try:
        with seq:
            entry["truth_sequestered_to"] = str(seq.dst)
            try:
                data = ecr_mod.run(
                    arm.design,
                    requests[0],
                    delta_path=delta if delta.exists() else None,
                    label=arm.ecr,
                    expect_infeasible=expect_infeasible,
                    timeout=timeout,
                    cont=cont,
                )
            except WorkerPending as wp:
                seq.keep()
                pending = True
                dump_json(
                    state_path,
                    {
                        "case": case_id,
                        "arm": arm_id,
                        "design": arm.design,
                        "entry": entry,
                        "t0": t0,
                        "vault": str(seq.dst),
                        "point": "ecr",
                        "expect_infeasible": expect_infeasible,
                        "keep_kcl": keep_kcl,
                        "timeout": timeout,
                        "order": wp.order.id,
                    },
                )
                return _pending(entry, wp, arm_id)
            entry["ecr"] = {k: data.get(k) for k in ("ok", "outcome", "refused", "kcl_modified", "verdict_note")}
            entry["ecr"]["gates"] = (data.get("gates") or {}).get("summary")
            entry["ecr"]["preservation"] = (data.get("preservation") or {}).get("ok")
            entry["ecr"]["worker"] = data.get("worker") or data.get("codex")
            entry["stage_reached"] = "ecr"
            if expect_infeasible:
                entry["stage_reached"] = "judged"
            else:  # still holding the case: the truth files are wherever this run's Sequester left them
                _score_into(entry, case_id, m, arm_id, seq)
    except (ContractError, PipelineError, EngineError) as e:
        entry["error"] = str(e)[:2000]
        return _finish(case_id, entry, t0)
    finally:
        if not pending:
            state_path.unlink(missing_ok=True)
            if not keep_kcl and kcl.exists() and base_copy.exists():
                kcl.write_bytes(base_copy.read_bytes())
                entry["base_kcl_restored"] = True
            base_copy.unlink(missing_ok=True)
    return _finish(case_id, entry, t0)


def _finish(case_id: str, entry: dict[str, Any], t0: float) -> dict[str, Any]:
    from opencad import telemetry

    entry["seconds"] = round(time.time() - t0)
    entry["finished"] = utc_now()
    log_attempt(case_id, entry)
    design = entry.get("design") or case_id
    try:
        telemetry.record(
            "attempt",
            design,
            telemetry.attempt_data(case_id, str(entry.get("arm")), entry, design),
            results_dir=results_of(design),
        )
    except Exception as e:  # telemetry never fails an attempt
        print(f"[telemetry] attempt row not written: {e!r}", flush=True)
    return entry

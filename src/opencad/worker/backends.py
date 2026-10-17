"""Worker dispatch policy: the Cursor cad-worker by default (handback via work orders), Codex only when opted in.

`dispatch()` is re-entrant: a stage calls it with a stable `key`; the first call issues an order and raises
WorkerPending (the driver exits 75); when the pipeline is re-run after the worker finished, the same call
returns the completed result. On the Codex path the turn runs inline, and an exhausted Codex budget hands
the same turn to the Cursor path with the partial Codex run attached (`OPENCAD_CODEX_NO_FALLBACK=1` stops instead).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from opencad import telemetry
from opencad.worker import orders, profiles
from opencad.worker.result import WorkerResult

BACKENDS = ("cursor", "codex")
EXIT_WORKER_PENDING = 75
_ENV = "OPENCAD_WORKER"
_continue_cmd = ""


class WorkerPending(Exception):
    """A work order was issued (or is still open); the pipeline must stop and let the orchestrator run the worker.

    `orders` lists every open order of a parallel batch (module turns); the orchestrator launches them all at once.
    """

    def __init__(self, order: orders.WorkOrder, all_orders: list[orders.WorkOrder] | None = None):
        super().__init__(f"worker turn pending: {order.id} ({order.role}) -> {order.brief_path}")
        self.order = order
        self.orders = list(all_orders or [order])


def dispatch_many(specs: list[dict[str, Any]]) -> list[WorkerResult]:
    """Issue every missing order of a batch before stopping, so independent turns run in parallel; returns results in spec order once all are done."""
    results: dict[str, WorkerResult] = {}
    pending: list[orders.WorkOrder] = []
    for spec in specs:
        try:
            results[spec["key"]] = dispatch(**spec)
        except WorkerPending as wp:
            pending.extend(wp.orders)
    if pending:
        raise WorkerPending(pending[0], pending)
    return [results[s["key"]] for s in specs]


def selected_backend() -> str:
    name = (os.environ.get(_ENV) or "cursor").strip().lower()
    if name not in BACKENDS:
        raise ValueError(f"{_ENV}={name!r}; expected one of {BACKENDS}")
    return name


def set_backend(name: str) -> None:
    if name not in BACKENDS:
        raise ValueError(f"worker backend {name!r}; expected one of {BACKENDS}")
    os.environ[_ENV] = name


def set_continue_cmd(cmd: str) -> None:
    """What the orchestrator runs after the worker finishes (printed in the NEXT line of every order this process issues)."""
    global _continue_cmd
    _continue_cmd = cmd


def continue_cmd() -> str:
    return _continue_cmd


def fresh(results_dir: Path, key: str) -> bool:
    """True when no live order with this key exists: the stage may (re)initialise its scratch directory."""
    return orders.find(results_dir, key) is None


def dispatch(brief: str, *, role: str, key: str, results_dir: Path, part: str, cd: Path, run_dir: Path, images: list[Path] | None = None,
             read_only: bool = False, resume: str | None = None, add_dirs: list[Path] | None = None, timeout: float | None = None,
             deliverables: list[Path] | None = None, context: dict[str, Any] | None = None, echo: bool = True, budget: float | None = None) -> WorkerResult:
    prof = profiles.profile(role)
    budget = profiles.budget_for(role, timeout, budget)
    fallback_from: str | None = None
    ctx: dict[str, Any] = dict(context or {})
    if selected_backend() == "codex":
        from opencad.worker import codex_backend

        if resume and orders.known_agent(results_dir, resume):  # a Cursor agent id is not a Codex thread; the brief carries the earlier reports
            if echo:
                print(f"[worker] not resuming Cursor agent {resume}; this turn starts a new Codex thread", flush=True)
            resume = None
        no_fallback = os.environ.get("OPENCAD_CODEX_NO_FALLBACK", "").lower() in {"1", "true", "yes"}
        exhausted, info = codex_backend.exhausted_state()
        if exhausted:
            reason = info.get("reason") or info.get("codex_exhausted_reason") or "marked"
            if no_fallback:
                from opencad.orchestrator import PipelineError

                raise PipelineError(f"codex budget exhausted ({reason}); OPENCAD_CODEX_NO_FALLBACK is set, so this {role} turn is not handed to the Cursor cad-worker")
            fallback_from = "codex"
            if echo:
                print(f"[worker] codex budget exhausted ({reason}); {role} turn goes to the Cursor cad-worker", flush=True)
        else:
            r = codex_backend.dispatch(brief, cd=cd, run_dir=run_dir, images=images, read_only=read_only, resume=resume, add_dirs=add_dirs,
                                       timeout=budget, echo=echo, effort=prof.codex_effort, idle_timeout=prof.codex_idle_s)
            r.role = role
            telemetry.record("turn", part, telemetry.turn_data(r, budget_s=budget), results_dir=results_dir)
            if not codex_backend.result_exhausted(r):
                return r
            b = codex_backend.budget()
            codex_backend.mark_exhausted(r.failure or "usage limit", resets_at=b.get("resets_at") if b.get("known") else None)
            if no_fallback:
                from opencad.orchestrator import PipelineError

                raise PipelineError(f"codex turn failed on budget ({(r.failure or '')[:200]}); OPENCAD_CODEX_NO_FALLBACK is set, so this {role} turn is not handed to the Cursor cad-worker")
            fallback_from = "codex"
            ctx.update({"codex_partial": str(run_dir), "codex_failure": (r.failure or "")[:300]})
            if echo:
                print(f"[worker] codex turn failed on budget ({(r.failure or '')[:100]}); handing the {role} turn to the Cursor cad-worker", flush=True)
    order = orders.find(results_dir, key)
    if order is not None:
        if orders.is_done(order):  # idempotent: a continued run may pass this dispatch again; complete() records the turn once
            r = orders.complete(order)
            r.fallback_from = fallback_from or r.fallback_from
            return r
        raise WorkerPending(order)
    resume_of = resume if orders.known_agent(results_dir, resume) else None  # a Codex thread id or an unrecorded agent cannot be resumed; the brief carries the earlier reports instead
    order = orders.issue(
        results_dir, key=key, role=role, part=part, brief=brief, cwd=Path(cd), writable_dirs=[Path(d) for d in (add_dirs or [])],
        images=images, read_only=read_only, deliverables=deliverables, resume_of=resume_of, model=prof.model, budget_s=budget,
        context={**ctx, **({"fallback_from": fallback_from} if fallback_from else {})}, continue_cmd=_continue_cmd or f"python -m opencad drive {part}",
    )
    raise WorkerPending(order)

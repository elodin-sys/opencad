"""Pipeline context and command routing for `python -m opencad`."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from opencad import zoo
from opencad.backends.base import BillingError, EngineError
from opencad.backends.registry import current_id, get
from opencad.contract import ContractError, check_bundle, load_contract
from opencad.io import dump_stage, load_json
from opencad.paths import PartNameError, part_dir, resolve_part
from opencad.schemas import PartContract


class PipelineError(RuntimeError):
    pass


STAGES = ("plan", "model", "verify", "export", "inspect", "edit", "gates", "report")
EXIT_WORKER_PENDING = 75  # a work order is waiting for the cad-worker; re-run the printed `continue` command afterwards


@dataclass
class Ctx:
    name: str
    design_dir: Path
    contract_path: Path
    contract: PartContract
    results_dir: Path
    part_dir: Path
    timeout: float = 3600
    backend_id: str = field(default_factory=current_id)

    @classmethod
    def load(cls, part_arg: str, *, timeout: float = 3600, backend: str | None = None) -> "Ctx":
        bid = backend or current_id()
        get(bid)
        try:
            name, contract_path, results_dir = resolve_part(part_arg, backend=bid)
        except PartNameError as e:
            raise PipelineError(str(e)) from e
        design_dir = contract_path.parent
        if not contract_path.exists():
            raise PipelineError(f"{contract_path} does not exist; run /initialize-cad first")
        problems = check_bundle(
            design_dir, lint=False
        )  # drafting rules gate publishing, not the evaluation of a published design
        if problems:
            raise PipelineError("design bundle problems:\n  - " + "\n  - ".join(problems))
        try:
            contract = load_contract(contract_path)
        except ContractError as e:
            raise PipelineError(str(e)) from e
        return cls(name, design_dir, contract_path, contract, results_dir, part_dir(name, backend=bid), timeout, bid)

    @property
    def backend(self):
        return get(self.backend_id)

    @property
    def entry(self) -> Path:
        return self.part_dir / self.backend.language.entry

    def stage_file(self, stage: str) -> Path:
        return self.results_dir / f"{stage}.json"

    def load_stage(self, stage: str) -> dict[str, Any] | None:
        p = self.stage_file(stage)
        return load_json(p) if p.exists() else None

    def require_stage(self, stage: str) -> dict[str, Any]:
        data = self.load_stage(stage)
        if data is None:
            raise PipelineError(
                f"stage {stage!r} has not run for {self.name}; run `python -m opencad {stage} {self.name}` first"
            )
        return data

    def write_stage(
        self, stage: str, data: dict[str, Any], *, ledger_prefix: list[dict[str, Any]] | None = None
    ) -> Path:
        data = dict(data)
        data["engine_calls"] = list(ledger_prefix or []) + self.backend.engine.reset_ledger()
        return dump_stage(self.results_dir, stage, data, contract_path=self.contract_path)

    def clean_stage_outputs(self, *names: str) -> None:
        for n in names:
            p = self.results_dir / n
            if p.is_dir():
                shutil.rmtree(p)
            elif p.exists():
                p.unlink()

    @property
    def kcl_target(self) -> Path:
        return self.entry


def _prepare_worker(args: argparse.Namespace) -> None:
    """Apply --worker / --parallel / --tag and record the command the orchestrator should re-run after a handback."""
    from opencad import worker

    if getattr(args, "worker", None):
        worker.set_backend(args.worker)
    if getattr(args, "tag", None):
        os.environ["OPENCAD_TAG"] = args.tag
    part = getattr(args, "part", None)
    be = getattr(args, "backend", None) or current_id()
    flag = f" --backend {be}"
    if part and getattr(args, "parallel", False):
        # concurrent drive loops: one engine lock per part instead of the global one
        os.environ.setdefault(
            "OPENCAD_ZOO_LOCK",
            str(Path.home() / ".cache" / "opencad" / f"zoo-{resolve_part(part, backend=be)[0]}.lock"),
        )
    if part:
        name = resolve_part(part, backend=be)[0]
        drive = f"python -m opencad drive {name}{flag}" + (" --wait" if getattr(args, "wait", False) else "")
        cont = {
            "run": drive,
            "drive": drive,
            "blockout": f"python -m opencad blockout {name} --continue{flag}",
            "correct": f"python -m opencad correct {name} --continue{flag}",
            "ecr": f"python -m opencad ecr {name} {getattr(args, 'request', '')} --label {getattr(args, 'label', 'ecr1')} --continue{flag}",
        }
        worker.set_continue_cmd(cont.get(args.cmd, f"python -m opencad {args.cmd} {name} --continue{flag}"))
    elif args.cmd == "draft":
        worker.set_continue_cmd(
            f"python -m opencad draft {args.dir} --name {args.name} --intent '<same intent>' --continue{flag}"
        )


def engine_wrapper(argv: list[str], ledger: Path | None) -> int:
    """`python -m opencad engine [--ledger PATH] -- <cmd>`: run through the selected backend and record the call."""
    return get().engine.ledger_wrapper(argv, ledger)


def _telemetry(args: argparse.Namespace) -> int:
    from opencad import telemetry

    def rows(spec: str | None, file: str | None = None, tag: str | None = None) -> list[dict[str, Any]]:
        if spec == "baseline" or (spec and spec.startswith("tag:")):
            try:
                return telemetry.rows_for_spec(spec)
            except ValueError as e:
                raise PipelineError(str(e)) from e
        if file:
            return telemetry.rows_for(path=Path(file), tag=tag)
        if spec and (spec.endswith(".jsonl") or "/" in spec):
            return telemetry.rows_for(path=Path(spec), tag=tag)
        return telemetry.rows_for(spec, tag=tag)

    if args.tcmd == "summary":
        s = telemetry.summarize(rows(args.part, args.file, getattr(args, "tag", None)))
        print(
            json.dumps(s, indent=2) if args.json else telemetry.format_summary(s, args.part or args.file or "campaign")
        )
        return 0
    if args.tcmd == "compare":
        print(telemetry.compare(telemetry.summarize(rows(args.baseline)), telemetry.summarize(rows(args.current))))
        return 0
    if args.tcmd == "timeline":
        print(telemetry.waterfall(telemetry.rows_for(args.part), f"timeline {args.part} ({current_id()})"))
        return 0
    if args.tcmd == "bench":
        from opencad.paths import REGRESS

        out = Path(args.out) if args.out else REGRESS / f"bench-{args.tag}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(telemetry.bench(args.tag, telemetry.bench_rows(args.tag), against=getattr(args, "against", None), suite=getattr(args, "suite", "parts")),
                       encoding="utf-8")
        print(out.read_text(encoding="utf-8"))
        print(f"wrote {out}")
        return 0
    if args.tcmd == "promote":
        try:
            info = telemetry.promote(args.tag, report=Path(args.report) if args.report else None, suite=getattr(args, "suite", "parts"))
        except ValueError as e:
            raise PipelineError(str(e)) from e
        print(json.dumps(info, indent=2))
        print(f"snapshot {telemetry.snapshot_path(args.tag)}")
        return 0
    raise PipelineError(f"unknown telemetry command {args.tcmd}")


def dispatch(args: argparse.Namespace) -> int:
    if getattr(args, "backend", None):
        from opencad.backends.registry import set_backend

        set_backend(args.backend)
    if args.cmd in ("zoo", "engine"):
        argv = list(getattr(args, "engine_args", None) or getattr(args, "zoo_args", None) or [])
        return engine_wrapper(argv, Path(args.ledger) if args.ledger else None)
    if args.cmd == "telemetry":
        return _telemetry(args)
    if args.cmd == "kcl-bisect":
        from opencad import bisect

        return bisect.main(
            Path(args.target),
            mode=args.mode,
            ledger=Path(args.ledger) if args.ledger else None,
            no_cache=args.no_cache,
            as_json=args.json,
        )
    if args.cmd == "quick":
        from opencad import quick

        return quick.run(
            Path(args.target),
            Path(args.contract) if args.contract else None,
            with_stl=args.stl,
            ledger=Path(args.ledger) if args.ledger else None,
            as_json=args.json,
            show_all=args.all,
        )
    if args.cmd == "next":
        from opencad.worker import orders

        def pending() -> list[Any]:
            if getattr(args, "part", None):
                return orders.pending(resolve_part(args.part)[2])
            if getattr(args, "backend", None):
                return orders.all_pending()
            from opencad.paths import RESULTS_BASE  # no backend named: every backend's results tree, not just the default one

            if not RESULTS_BASE.exists():
                return []
            return [o for d in sorted(RESULTS_BASE.iterdir()) if d.is_dir() and not d.name.startswith("_") for o in orders.all_pending(d)]

        if getattr(args, "watch", False):
            return orders.watch(pending, stale_s=args.stale, pid=args.pid, timeout=args.timeout)
        pend = pending()
        stale = getattr(args, "stale", None)
        if stale is not None:
            pend = [o for o in pend if orders.idle_seconds(o) >= stale]
        for o in pend:
            print(orders.next_line(o, idle=True))
        if not pend:
            print("no pending worker turns" if stale is None else f"no pending worker turns idle for {stale:g} s")
        return 0
    if args.cmd == "dispatch":
        from opencad.worker import orders

        p = Path(args.order)
        order_dir = p.parent if p.name == orders.DISPATCH_FILE else p
        try:
            order = orders.load(order_dir)
        except FileNotFoundError:
            print(f"error: {order_dir} is not a work order (no {orders.ORDER_FILE})", file=sys.stderr)
            return 2
        out = orders.record_dispatch(order, args.agent_id, model=args.model or "inherit", finished=args.finished)
        print(out)
        return 0
    _prepare_worker(args)
    if args.cmd == "validate":
        ctx = Ctx.load(args.part)
        c = ctx.contract
        print(
            f"ok: {ctx.contract_path} ({len(c.parameters)} parameters, {len(c.features)} features, provenance {c.provenance_summary()})"
        )
        return 0
    if args.cmd == "stage-bundle":
        from opencad.contract import stage_bundle

        try:
            print(stage_bundle(args.name))
        except (ContractError, PartNameError) as e:
            raise PipelineError(str(e)) from e
        return 0
    if args.cmd == "check-bundle":
        problems = check_bundle(Path(args.dir), args.name)
        if problems:
            print("bundle problems:\n  - " + "\n  - ".join(problems))
            return 1
        c = load_contract(Path(args.dir))
        print(
            f"ok: {args.dir} ({len(c.parameters)} parameters, {len(c.features)} features, provenance {c.provenance_summary()})"
        )
        from opencad.contract import lint_contract

        for w in lint_contract(c)[1]:
            print(f"warning: {w}")
        return 0
    if args.cmd == "draft":
        from opencad import initialize
        from opencad.worker import WorkerPending, orders

        try:
            res = initialize.draft(
                Path(args.dir),
                args.name,
                args.intent,
                sources=[Path(s) for s in args.source] + [Path(i) for i in args.image],
                images=[Path(i) for i in args.image],
                notes=args.notes,
                timeout=args.timeout,
                cont=args.cont,
            )
        except WorkerPending as wp:
            for o in wp.orders:
                print(orders.next_line(o), flush=True)
            return EXIT_WORKER_PENDING
        print(f"draft {'ok' if res['ok'] else 'FAILED'} after {len(res['rounds'])} round(s); thread {res['thread_id']}")
        for pr in res["problems"]:
            print(f"  - {pr}")
        return 0 if res["ok"] else 1
    if args.cmd == "publish":
        from opencad.contract import publish_bundle

        try:
            target = publish_bundle(Path(args.dir), args.name)
        except (ContractError, PartNameError) as e:
            raise PipelineError(str(e)) from e
        print(f"published {target}")
        return 0
    if args.cmd in ("credits", "preflight"):
        pf = get().engine.preflight()
        print(json.dumps(pf, indent=2, default=str))
        if pf.get("billing"):
            print(zoo.credit_banner(pf["billing"]))
        return 0 if pf.get("ok") else 1
    from opencad.worker import WorkerPending, orders, state

    try:
        if args.cmd == "blockout":
            from opencad.stages import blockout

            try:
                data = blockout.run(
                    Ctx.load(args.part, timeout=args.timeout), max_iterations=args.max_iterations, cont=args.cont
                )
            except WorkerPending as wp:
                for o in wp.orders:
                    print(orders.next_line(o), flush=True)
                return EXIT_WORKER_PENDING
            return 0 if data["ok"] else 1
        if args.cmd in ("run", "drive"):
            from opencad.stages import pipeline
            from opencad.worker import orders

            ctx = Ctx.load(args.part, timeout=args.timeout)
            cont = bool(getattr(args, "cont", False))
            if args.cmd == "drive" and not args.fresh and state.load(ctx.results_dir) is not None:
                cont = True  # drive continues an interrupted run by default
            if cont:
                code = pipeline.run(ctx, cont=True)
            else:
                code = pipeline.run(
                    ctx,
                    skip_blockout=args.skip_blockout,
                    from_stage=args.from_stage,
                    allow_retry=not args.no_retry,
                    plan_separately=bool(getattr(args, "plan_separately", False)),
                    decompose=getattr(args, "decompose", None),
                )
            while code == EXIT_WORKER_PENDING and getattr(args, "wait", False):
                orders.wait(
                    ctx.results_dir, enforce=orders.executes if getattr(args, "enforce_budgets", False) else None
                )
                code = pipeline.run(ctx, cont=True)
            return code
        if args.cmd == "correct":
            from opencad.stages import correct

            ctx = Ctx.load(args.part, timeout=args.timeout)
            try:
                data = correct.run(ctx, note=args.note, allow_retry=not args.no_retry, cont=args.cont)
            except WorkerPending as wp:
                for o in wp.orders:
                    print(orders.next_line(o), flush=True)
                return EXIT_WORKER_PENDING
            return int(data.get("pipeline_code") or 0)
        if args.cmd == "ecr":
            from opencad.stages import ecr

            name, _, _ = resolve_part(args.part)
            try:
                data = ecr.run(
                    name,
                    Path(args.request),
                    delta_path=Path(args.contract_delta) if args.contract_delta else None,
                    label=args.label,
                    expect_infeasible=args.expect_infeasible,
                    timeout=args.timeout,
                    allow_retry=not args.no_retry,
                    cont=args.cont,
                )
            except WorkerPending as wp:
                for o in wp.orders:
                    print(orders.next_line(o), flush=True)
                return EXIT_WORKER_PENDING
            return 0 if data.get("ok") else 1
        if args.cmd in STAGES:
            from opencad.stages import pipeline

            return pipeline.run_single(
                Ctx.load(args.part, timeout=args.timeout), args.cmd, cont=bool(getattr(args, "cont", False))
            )
    except (zoo.ZooError, EngineError, BillingError) as e:
        raise PipelineError(str(e)) from e
    raise PipelineError(f"unknown command {args.cmd}")

"""`python -m opencad <command>`: orchestrator and individual stages.

Stage modules are imported lazily so that `--help` and light commands do not load OCP.

Worker turns (draft, blockout, plan, model, corrections, ECR, correct) are handed back to the orchestrating
Cursor agent: the command exits 75 after printing a `NEXT {...}` line naming the work order; run the
cad-worker on its brief, then re-run the printed `continue` command. `--worker codex` runs the turns
inline through the local Codex CLI instead (falls back to the handback when its budget is exhausted).
"""

from __future__ import annotations

import argparse
import sys


def _add_part(p: argparse.ArgumentParser) -> None:
    p.add_argument("part", help="<name>, designs/<name>, or designs/<name>/contract.yaml")


def _add_worker(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--worker",
        choices=["cursor", "codex"],
        help="worker backend for this command (default OPENCAD_WORKER or cursor)",
    )


def _add_backend(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--backend",
        default=None,
        help="modelling backend: zoo, cadquery, build123d, freecad (default OPENCAD_BACKEND or build123d)",
    )


def _add_continue(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--continue",
        dest="cont",
        action="store_true",
        help="continue after a worker handback (the work order's `done` file exists)",
    )


def _add_campaign(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--parallel",
        action="store_true",
        help="this loop runs beside other parts: use a per-part engine lock instead of the global one",
    )
    p.add_argument(
        "--tag", help="label every telemetry row of this run (A/B comparisons: `telemetry compare tag:A tag:B`)"
    )


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="opencad", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("assembly", help="machines: `python -m opencad assembly stage|check|drive|part|check-source|stage-run ...` (see `assembly --help`)")
    sub.add_parser("sim", help="`python -m opencad sim study <asm> <sim> --case <id> [--levels ...] [--dry-run]`: one simulation's mesh ladder (see `sim --help`)")

    p = sub.add_parser("validate", help="validate designs/<part>/contract.yaml against PartContract")
    _add_part(p)
    _add_backend(p)

    p = sub.add_parser("credits", help="show the current backend preflight (Zoo: API credit balance)")
    _add_backend(p)
    p = sub.add_parser("preflight", help="probe the selected backend (billing, version, readiness)")
    _add_backend(p)

    p = sub.add_parser("stage-bundle", help="create designs/.staging-<part>/ from the template (for /initialize-cad)")
    p.add_argument("name")
    _add_backend(p)

    p = sub.add_parser("check-bundle", help="validate a staged or published bundle directory")
    p.add_argument("dir")
    p.add_argument("--name", help="intended designs/<name> (defaults to the directory name)")
    _add_backend(p)

    p = sub.add_parser("publish", help="atomically move a complete staged bundle to designs/<name>")
    p.add_argument("dir")
    p.add_argument("--name", required=True)
    _add_backend(p)

    p = sub.add_parser(
        "draft",
        help="the worker drafts contract.yaml + brief.md into a staging bundle (headless /initialize-cad step 3-4)",
    )
    p.add_argument("dir")
    p.add_argument("--name", required=True)
    p.add_argument("--intent", required=True)
    p.add_argument("--source", action="append", default=[], help="text/table source file (copied into sources/)")
    p.add_argument(
        "--image", action="append", default=[], help="drawing/figure attached to the worker (also copied into sources/)"
    )
    p.add_argument("--notes", default="")
    p.add_argument(
        "--timeout", type=float, default=None, help="cap on the draft turn budget (default: the role profile)"
    )
    _add_worker(p)
    _add_backend(p)
    _add_continue(p)

    p = sub.add_parser(
        "blockout", help="/initialize-cad checkpoint: envelope-only model from the worker, analyze + four-view"
    )
    _add_part(p)
    p.add_argument("--max-iterations", type=int, default=2)
    p.add_argument(
        "--timeout", type=float, default=None, help="cap on each blockout turn budget (default: the role profile)"
    )
    _add_worker(p)
    _add_backend(p)
    _add_campaign(p)
    _add_continue(p)

    for name, help_ in (
        (
            "run",
            "/create-cad: plan, model, verify, export, inspect, edit, gates, report (exit 75 = worker turn pending)",
        ),
        (
            "drive",
            "same as run, but continues an interrupted run automatically when results/<part>/pipeline-state.json exists",
        ),
    ):
        p = sub.add_parser(name, help=help_)
        _add_part(p)
        p.add_argument("--skip-blockout", action="store_true", help="do not require a passed blockout checkpoint")
        p.add_argument(
            "--from-stage",
            default="plan",
            help="resume from this stage (keeps earlier stage JSONs). plan deletes the part source files",
        )
        p.add_argument("--no-retry", action="store_true", help="disable the single bounded gate retry")
        p.add_argument(
            "--plan-separately",
            action="store_true",
            help="run the read-only planning turn as its own worker turn (default: the model turn writes plan.md first)",
        )
        p.add_argument(
            "--decompose",
            dest="decompose",
            action="store_const",
            const=True,
            default=None,
            help="model through partition -> parallel module turns -> integrate (default: automatic for large contracts)",
        )
        p.add_argument(
            "--no-decompose",
            dest="decompose",
            action="store_const",
            const=False,
            help="force the single model turn even for a large contract",
        )
        p.add_argument(
            "--timeout", type=float, default=None, help="cap on each worker turn budget (default: the role profile)"
        )
        p.add_argument(
            "--wait",
            action="store_true",
            help="after a NEXT line keep running: poll the orders' done files every 5 s and continue by itself "
            "(STALE {...} when a dispatched worker is idle past 1.25x its budget)",
        )
        p.add_argument(
            "--enforce-budgets",
            action="store_true",
            help="with --wait: a turn past 1.5x its budget is taken at its executing deliverable or "
            "checkpoint (EXPIRED {...}; stop that worker)",
        )
        _add_worker(p)
        _add_backend(p)
        _add_campaign(p)
        if name == "run":
            _add_continue(p)
        else:
            p.add_argument("--fresh", action="store_true", help="discard an interrupted run's state and start over")

    p = sub.add_parser(
        "next",
        help="list pending worker turns (work orders waiting for the cad-worker) with idle_s since the worker last touched anything",
    )
    p.add_argument("part", nargs="?", help="only this part (default: every part under results/<backend>/)")
    p.add_argument(
        "--stale",
        type=float,
        default=None,
        metavar="SECONDS",
        help="only orders idle for at least this long (a dispatched worker that stopped mid-turn)",
    )
    p.add_argument(
        "--watch",
        action="store_true",
        help="block until an undispatched order (NEXT), a dispatched one idle past --stale or 1.25x its budget (STALE), "
        "or the --pid process exits (EXITED); exit 0, 3 on EXITED, 4 on --timeout",
    )
    p.add_argument("--pid", type=int, default=None, help="with --watch: the pipeline process to watch")
    p.add_argument("--timeout", type=float, default=3600.0, help="with --watch: give up after this many seconds")
    _add_backend(p)

    p = sub.add_parser(
        "dispatch",
        help="record which agent runs a work order: writes <order>/dispatch.json (resume identity, model on the telemetry row)",
    )
    p.add_argument("order", help="the order directory (NEXT.order) or its dispatch.json")
    p.add_argument("--agent-id", required=True)
    p.add_argument("--model", default=None, help="explicit model override; default inherit")
    p.add_argument("--finished", action="store_true", help="stamp the finish time (after the Task returned)")

    p = sub.add_parser(
        "engine", help="run the selected backend and append one ledger row: opencad engine [--ledger PATH] -- <cmd>"
    )
    p.add_argument(
        "--ledger", help="JSONL ledger path (default $OPENCAD_ENGINE_LEDGER or ~/.cache/opencad/engine-ledger.jsonl)"
    )
    _add_backend(p)
    p.add_argument("engine_args", nargs=argparse.REMAINDER, help="arguments for the backend (prefix with --)")

    p = sub.add_parser("zoo", help="alias for `opencad engine` on the zoo backend")
    p.add_argument(
        "--ledger", help="JSONL ledger path (default $OPENCAD_ENGINE_LEDGER or ~/.cache/opencad/engine-ledger.jsonl)"
    )
    _add_backend(p)
    p.add_argument("zoo_args", nargs=argparse.REMAINDER, help="arguments for zoo (prefix with --)")

    p = sub.add_parser(
        "quick",
        help="local critic for workers: export once (cached by source hash), measure the STEP with OpenCascade against the contract, print the failing checks",
    )
    p.add_argument("target", help="parts/<backend>/<part>/main.* or an exported .step")
    p.add_argument("--contract", help="designs/<part>/contract.yaml (inferred from the part path when omitted)")
    p.add_argument("--stl", action="store_true", help="also export the STL and check it is watertight")
    p.add_argument("--ledger", help="append the exports to this engine ledger (the work order's engine-ledger.jsonl)")
    p.add_argument("--json", action="store_true", help="print the full inspect dictionary instead of the lines")
    p.add_argument("--all", action="store_true", help="print passing checks as well as failing ones")
    _add_backend(p)

    p = sub.add_parser(
        "kcl-bisect",
        help="which `|>` step makes a KCL file fail on the engine: one analyze per step with that step disabled (cached by content hash)",
    )
    p.add_argument("target", help="the .kcl file (variants are written next to it so imports resolve)")
    p.add_argument(
        "--mode",
        choices=("single", "prefix"),
        default="single",
        help="single: disable one step at a time; prefix: truncate the last chain step by step",
    )
    p.add_argument(
        "--ledger", help="append the hosted analyzes to this engine ledger (the work order's engine-ledger.jsonl)"
    )
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--json", action="store_true")
    _add_backend(p)

    p = sub.add_parser(
        "telemetry",
        help="turn/stage/gates/attempt rows: summary [part], compare <baseline.jsonl> <current.jsonl|part>, backfill [--out PATH]",
    )
    tsub = p.add_subparsers(dest="tcmd", required=True)
    q = tsub.add_parser(
        "summary",
        help="aggregate results/<part>/telemetry.jsonl (or the campaign file with no part; `tag:<label>` selects an A/B arm)",
    )
    q.add_argument("part", nargs="?")
    q.add_argument("--file", help="read this JSONL instead")
    q.add_argument("--tag", help="only rows recorded with this --tag")
    q.add_argument("--json", action="store_true", help="print the aggregate as JSON")
    _add_backend(q)
    q = tsub.add_parser(
        "compare", help="baseline vs current: per-role and per-stage mean wall, engine calls, pass rates"
    )
    q.add_argument(
        "baseline",
        help="`baseline` (results/_regress/baseline.json), `tag:<label>` (every backend), a JSONL file, or a part name",
    )
    q.add_argument("current", help="`tag:<label>`, a JSONL file, or a part name")
    _add_backend(q)
    q = tsub.add_parser(
        "timeline",
        help="per-round waterfall of a part's latest attempt (or the one in progress) with its critical-path buckets",
    )
    q.add_argument("part")
    _add_backend(q)
    q = tsub.add_parser(
        "bench",
        help="case x backend table of every attempt tagged --tag (all backends) -> results/_regress/bench-<tag>.md",
    )
    q.add_argument("--tag", required=True)
    q.add_argument("--against", help="compare each cell to this tag (default: the promoted baseline in results/_regress/baseline.json)")
    q.add_argument("--suite", default="parts", choices=["parts", "assembly"], help="which suite's baseline to compare with (assembly: baseline-assembly.json)")
    q.add_argument("--out", help="report path (default results/_regress/bench-<tag>.md)")
    q = tsub.add_parser(
        "promote",
        help="make --tag the baseline: results/_regress/baseline.json plus a tracked snapshot of its rows and report in results/_regress/baselines/",
    )
    q.add_argument("--tag", required=True)
    q.add_argument("--report", help="the tag's report (default results/_regress/<tag>.md or bench-<tag>.md)")
    q.add_argument("--suite", default="parts", choices=["parts", "assembly"], help="assembly: promote into results/_regress/baseline-assembly.json")
    _add_backend(p)

    p = sub.add_parser(
        "correct", help="deliberate geometry turn on the existing model thread, then re-verify from the verify stage"
    )
    _add_part(p)
    p.add_argument("--note", default="", help="markdown file or inline note (required unless --continue)")
    p.add_argument("--no-retry", action="store_true", help="disable the bounded gate retry after the turn")
    p.add_argument(
        "--timeout", type=float, default=None, help="cap on the worker turn budget (default: the role profile)"
    )
    _add_worker(p)
    _add_backend(p)
    _add_continue(p)

    p = sub.add_parser(
        "ecr",
        help="engineering change request: the worker edits the existing part on its model thread; re-verify against a revised contract with interface preservation",
    )
    _add_part(p)
    p.add_argument("request", help="markdown file with the change request")
    p.add_argument(
        "--contract-delta",
        help="YAML with contract entries to add/replace by name/id (parameters, features, interfaces, acceptance.*, envelope, open_questions)",
    )
    p.add_argument("--label", default="ecr1", help="results/<part>/ecr/<label>/ and designs/<part>/ecr/<label>/")
    p.add_argument(
        "--expect-infeasible",
        action="store_true",
        help="the request is deliberately impossible: an explicit refusal passes, any model change fails",
    )
    p.add_argument("--no-retry", action="store_true")
    p.add_argument(
        "--timeout", type=float, default=None, help="cap on each worker turn budget (default: the role profile)"
    )
    _add_worker(p)
    _add_backend(p)
    _add_continue(p)

    for name, help_ in [
        ("plan", "the worker proposes a construction sequence and invariants"),
        ("model", "the worker authors parts/<backend>/<part>/main.* (bounded)"),
        ("verify", "format/lint/analyze against the contract"),
        ("export", "deterministic STEP (twice), STL, GLB"),
        ("inspect", "independent OCP/trimesh checks, sections, features, deviation"),
        ("edit", "edit-robustness rebuild/restore test"),
        ("gates", "evaluate the 12 tiered gates"),
        ("report", "report.html, report.md, handoff/"),
    ]:
        p = sub.add_parser(name, help=help_)
        _add_part(p)
        p.add_argument("--timeout", type=float, default=None)
        _add_worker(p)
        _add_backend(p)
        _add_continue(p)

    return ap


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["assembly"]:
        from opencad.assembly.cli import main as assembly_main

        return assembly_main(argv[1:])
    if argv[:1] == ["sim"]:
        from opencad.sim.cli import main as sim_main

        return sim_main(argv[1:])
    args = build_parser().parse_args(argv)
    if args.cmd == "zoo" and getattr(args, "zoo_args", None) and args.zoo_args[0] == "--":
        args.zoo_args = args.zoo_args[1:]
    if args.cmd == "engine" and getattr(args, "engine_args", None) and args.engine_args[0] == "--":
        args.engine_args = args.engine_args[1:]
    if getattr(args, "backend", None):
        from opencad.backends.registry import set_backend

        set_backend(args.backend)
    from opencad import orchestrator

    try:
        return orchestrator.dispatch(args)
    except orchestrator.PipelineError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

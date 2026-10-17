"""`python -m opencad assembly <verb>`: stage, check, drive, part, check-source, stage-run, viz."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="opencad assembly", description=__doc__)
    sub = ap.add_subparsers(dest="verb", required=True)

    def backend(p: argparse.ArgumentParser) -> None:
        p.add_argument("--backend", default=None, help="build123d (default), cadquery, freecad or zoo (a KCL assembly source)")

    p = sub.add_parser("stage", help="designs/.staging-<asm>/ with the sources copied in and the draft request recorded")
    p.add_argument("name")
    p.add_argument("--intent", required=True)
    p.add_argument("--source", action="append", default=[])
    p.add_argument("--image", action="append", default=[])
    p.add_argument("--notes", default="")
    p = sub.add_parser("check", help="validate and lint an assembly bundle (the asm-draft critic)")
    p.add_argument("dir")
    p.add_argument("--name")
    p = sub.add_parser("drive", help="draft -> parts -> assemble -> verify -> kinematics -> domains -> simulate -> gates -> report; EVENT#k per worker hand-back")
    p.add_argument("name")
    p.add_argument("--from-stage", default=None)
    p.add_argument("--fresh", action="store_true", help="discard an interrupted run's state")
    p.add_argument("--no-retry", action="store_true")
    p.add_argument("--jobs", type=int, default=4, help="part lanes at once")
    p.add_argument("--tag", default=None)
    p.add_argument("--amend", default=None, help="markdown file (or text) of evaluator evidence for an engineering change on the published contract")
    p.add_argument("--stop-after", choices=["draft", "blockout"], default=None,
                   help="the /initialize-cad checkpoint: stop once the drafts are published, or once every part's blockout ran; with --amend, the "
                        "reviewer's notes revise the drafts before anything is built")
    backend(p)
    p = sub.add_parser("part", help="lane body: one part design through blockout (when needed) and the part pipeline, waiting on each order")
    p.add_argument("design")
    p.add_argument("--timeout", type=float, default=None)
    p.add_argument("--blockout-only", action="store_true", help="run the part's blockout checkpoint and stop")
    backend(p)
    p = sub.add_parser("check-source", help="the assemble worker's critic: build the assembly source and print every assembly check")
    p.add_argument("name")
    p.add_argument("--ledger", default=None)
    p.add_argument("--json", action="store_true")
    backend(p)
    p = sub.add_parser("stage-run", help="re-run one evaluator stage (verify, kinematics, domains, simulate, gates, report)")
    p.add_argument("name")
    p.add_argument("stage")
    backend(p)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "backend", None):
        from opencad.backends.registry import set_backend

        set_backend(args.backend)
    from opencad.assembly import AssemblyError
    from opencad.contract import ContractError

    try:
        if args.verb == "stage":
            from opencad.assembly.draft import stage_request

            print(stage_request(args.name, args.intent, [Path(s) for s in args.source], [Path(i) for i in args.image], args.notes))
            return 0
        if args.verb == "check":
            from opencad.contract import check_assembly_bundle, lint_assembly, load_assembly

            problems = check_assembly_bundle(Path(args.dir), args.name)
            if problems:
                print("assembly bundle problems:\n  - " + "\n  - ".join(problems))
                return 1
            a = load_assembly(Path(args.dir))
            print(f"ok: {args.dir} ({len(a.parts)} bodies, {len(a.joints)} joints, {len(a.transmissions)} transmissions, {len(a.simulations)} simulations)")
            for w in lint_assembly(a)[1]:
                print(f"warning: {w}")
            return 0
        if args.verb == "drive":
            import os

            from opencad.assembly.pipeline import drive

            if args.tag:
                os.environ["OPENCAD_TAG"] = args.tag
            note = args.amend
            if note and Path(note).is_file():
                note = Path(note).read_text(encoding="utf-8")
            from opencad.backends.registry import current_id, get
            from opencad.costing import begin_credits, mark_cell_start, write_cell_cost
            from opencad.paths import results_root

            be = args.backend or current_id()
            results_dir = results_root(be) / Path(args.name).name
            mark_cell_start(results_dir, reset=args.fresh)
            if be == "zoo":
                begin_credits(results_dir, get(be).engine.preflight().get("billing"), reset=args.fresh)
            try:
                return drive(args.name, backend=args.backend, from_stage=args.from_stage, fresh=args.fresh, allow_retry=not args.no_retry, jobs=args.jobs,
                             amend=note, stop_after=args.stop_after)
            finally:
                write_cell_cost(results_dir, backend_id=be)
        if args.verb == "part":
            from opencad.assembly.parts import drive_part

            return drive_part(args.design, timeout=args.timeout, blockout_only=args.blockout_only)
        if args.verb == "check-source":
            from opencad.assembly.verify import critic

            return critic(args.name, ledger=Path(args.ledger) if args.ledger else None, as_json=args.json)
        if args.verb == "stage-run":
            from opencad.assembly.pipeline import run_stage

            return run_stage(args.name, args.stage)
    except (AssemblyError, ContractError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 2

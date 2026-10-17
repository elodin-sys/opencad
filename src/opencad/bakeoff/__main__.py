"""python -m opencad.bakeoff status|next|run|report"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from opencad.bakeoff import CANDIDATES, REFERENCE, next_cell, next_rung, run_argv, status, write_report
from opencad.paths import REPO_ROOT


def rebuild_site(repo: Path | None = None, out: Path | None = None) -> int:
    """Refresh the static site so a new published.yaml entry appears on the bake-off page."""
    from opencad.site.build import SiteBuildError, build_site

    repo = repo or REPO_ROOT
    out = out or (repo / "_site")
    try:
        designs = build_site(repo, out)
    except SiteBuildError as e:
        print(f"site: {e}", file=sys.stderr)
        return 1
    print(f"built {out} with {len(designs)} designs")
    return 0


def child_env() -> dict[str, str]:
    env = os.environ.copy()
    env["OPENCAD_CODEX_NO_FALLBACK"] = "1"
    env["OPENCAD_CODEX_EFFORT"] = "max"
    env["CODEX_SERVICE_TIER"] = "fast"
    return env


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="opencad.bakeoff", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("status", help="print part x backend gate status")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("next", help="print the next unfinished rung (all three backend commands)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--cell", action="store_true", help="print only the first unfinished cell")
    p = sub.add_parser("run", help="blockout or drive the next cell (or --backend/--part)")
    p.add_argument("--backend", choices=[*CANDIDATES, *REFERENCE])
    p.add_argument("--part")
    p.add_argument("--print-only", action="store_true", help="print the command and exit 0")
    p = sub.add_parser("report", help="write results/_bakeoff/report.md and rebuild _site")
    p.add_argument("-o", "--out", type=Path, help="write the markdown here and skip the site rebuild")
    p = sub.add_parser("compare-assembly", help="machine handoff parity across backends: results/_bakeoff/<asm>-compare.md")
    p.add_argument("asm")
    p.add_argument("--reference", default="build123d")
    p.add_argument("--backends", default="cadquery,build123d,freecad,zoo")
    p.add_argument("-o", "--out", type=Path)
    args = ap.parse_args(argv)

    if args.cmd == "status":
        rows = status()
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            for r in rows:
                print(f"{r['backend']:10s} {r['part']:28s} {r['status']}")
        return 0
    if args.cmd == "next":
        if args.cell:
            nxt = next_cell()
            if nxt is None:
                print("done")
                return 0
            if args.json:
                print(json.dumps(nxt, indent=2))
            else:
                print(f"{nxt['backend']} {nxt['part']} {nxt['status']}")
                print(" ".join(run_argv(nxt["backend"], nxt["part"])))
            return 0
        rung = next_rung()
        if rung is None:
            print("done")
            return 0
        if args.json:
            print(json.dumps(rung, indent=2))
        else:
            print(f"rung {rung['part']}")
            for c in rung["cells"]:
                print(f"{c['backend']} {c['status']}")
            for cmd in rung["commands"]:
                print(" ".join(cmd))
        return 0
    if args.cmd == "run":
        nxt = {"backend": args.backend, "part": args.part} if args.backend and args.part else next_cell()
        if nxt is None or not nxt.get("backend") or not nxt.get("part"):
            print("bakeoff: nothing to run", file=sys.stderr)
            return 0
        argv = run_argv(nxt["backend"], nxt["part"])
        print(" ".join(argv), flush=True)
        if args.print_only:
            return 0
        return subprocess.call(argv, cwd=str(REPO_ROOT), env=child_env())
    if args.cmd == "report":
        out = write_report(args.out)
        print(out)
        return 0 if args.out is not None else rebuild_site()
    if args.cmd == "compare-assembly":
        from opencad.bakeoff.compare import compare_assembly

        ok, path = compare_assembly(args.asm, reference=args.reference, backends=tuple(args.backends.split(",")), out=args.out)
        print(path.read_text(encoding="utf-8"))
        return 0 if ok else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

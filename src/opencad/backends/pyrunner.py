"""Load a CadQuery or build123d main.py, take `result`, analyze and export; run by each backend's `runner` module."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

from opencad.backends.local import lap_timer, result_shape


def load_namespace(entry: Path, ns_name: str) -> dict:
    entry = Path(entry).resolve()
    # `python -I` drops the script dir; sibling modules (params, datum, groups) must import
    sys.path.insert(0, str(entry.parent))
    ns: dict = {"__name__": ns_name, "__file__": str(entry)}
    src = Path(entry).read_text(encoding="utf-8")
    exec(compile(src, str(entry), "exec"), ns, ns)
    return ns


def main(argv: list[str] | None = None, *, ns_name: str) -> int:
    lap = lap_timer()
    ap = argparse.ArgumentParser()
    ap.add_argument("--entry", required=True)
    ap.add_argument("--out", help="JSON sidecar")
    ap.add_argument("--analyze")
    ap.add_argument("--export-step")
    ap.add_argument("--export-stl")
    ap.add_argument("--result-name", default="result")
    args = ap.parse_args(argv)
    payload: dict = {"ok": True}
    try:
        from opencad.backends.local import analyze_shape, write_step, write_stl
        from opencad.backends.placements import as_joints, as_placements

        ns = load_namespace(Path(args.entry), ns_name)
        if args.result_name not in ns:
            raise RuntimeError(f"{args.result_name!r} is not defined in {args.entry}")
        shape = result_shape(ns[args.result_name])
        lap("build_s")
        placements = as_placements(ns.get("placements"))
        if placements:
            payload["placements"] = placements
        joints = as_joints(ns.get("joints"))
        if joints:
            payload["joints"] = joints
        if args.analyze:
            data = analyze_shape(shape)
            Path(args.analyze).parent.mkdir(parents=True, exist_ok=True)
            Path(args.analyze).write_text(json.dumps(data, indent=2), encoding="utf-8")
            payload["analyze"] = data
            lap("analyze_s")
        if args.export_step:
            write_step(shape, Path(args.export_step), Path(args.entry).stem)
            payload["step"] = str(args.export_step)
            lap("step_s")
        if args.export_stl:
            write_stl(shape, Path(args.export_stl))
            payload["stl"] = str(args.export_stl)
            lap("stl_s")
    except Exception as e:
        lap("failed_s")
        payload = {
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc()[-2000:],
            "class": "program"
            if type(e).__name__ in {"AssertionError", "SyntaxError", "NameError", "ValueError"}
            else "unknown",
        }
        if (
            "StdFail" in type(e).__name__
            or "ConstructionError" in type(e).__name__
            or "Standard_Failure" in type(e).__name__
        ):
            payload["class"] = "kernel"
    payload["timings"] = lap.timings
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in payload if k != "traceback"}))
    return 0 if payload.get("ok") else 1

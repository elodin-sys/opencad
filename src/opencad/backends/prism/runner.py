"""Prism runner: stdlib + OCP + build123d only, run by Prism's managed interpreter (`python -I <this file> --entry main.py ...`).

Prism's python-env has no pyyaml, psutil or trimesh, so `opencad` is not importable there; this file mirrors
`opencad.backends.pyrunner` (same flags, same JSON payload) without importing it. Millimetres: the pipeline's contract
units, not the metres of Prism's standalone code-cad skill, so the STEP unit is pinned to MM even when a `navier_cad`
helper has switched the OCCT statics to metres.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import traceback
from pathlib import Path

FILE_NAME_RE = re.compile(r"FILE_NAME\s*\((.*?)\)\s*;", re.S)
STL_DEFLECTION = 0.02
STL_ANGULAR = 0.5


def normalize_step_header(path: Path, name: str = "opencad") -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    repl = f"FILE_NAME('{name}.step','1970-01-01T00:00:00',('opencad'),('opencad'),'opencad','opencad','');"
    new, n = FILE_NAME_RE.subn(repl, text, count=1)
    if n:
        path.write_text(new, encoding="utf-8")


def load_namespace(entry: Path, ns_name: str = "__prism_main__") -> dict:
    entry = Path(entry).resolve()
    sys.path.insert(0, str(entry.parent))  # `python -I` drops the script dir; sibling modules (params, datum, groups) must import
    ns: dict = {"__name__": ns_name, "__file__": str(entry)}
    src = entry.read_text(encoding="utf-8")
    exec(compile(src, str(entry), "exec"), ns, ns)
    return ns


def collect_shapes(obj) -> list:
    """Every OCC shape behind `result`: a Shape (`.wrapped`), a builder (`.part`), or a list/tuple of those."""
    if isinstance(obj, (list, tuple)):
        return [s for o in obj for s in collect_shapes(o)]
    if callable(getattr(obj, "vals", None)):
        return [s for o in obj.vals() for s in collect_shapes(o)]
    if hasattr(obj, "wrapped"):
        return [obj.wrapped]
    part = getattr(obj, "part", None)
    if hasattr(part, "wrapped"):
        return [part.wrapped]
    return [obj]


def result_shape(obj):
    """One TopoDS shape: a lone shape as is, several as one TopoDS_Compound (every body of a multi-solid deliverable)."""
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound, TopoDS_Shape

    shapes = [s for s in collect_shapes(obj) if isinstance(s, TopoDS_Shape) and not s.IsNull()]
    if not shapes:
        raise ValueError(f"result holds no OCC shape (got {type(obj).__name__}); assign a solid, a Compound or a list")
    if len(shapes) == 1:
        return shapes[0]
    comp = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(comp)
    for s in shapes:
        builder.Add(comp, s)
    return comp


def analyze_shape(shape) -> dict:
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props, 1e-7)
    sprops = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, sprops, 1e-7)
    com = props.CentreOfMass()
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box, False, False)
    lo, hi = box.CornerMin(), box.CornerMax()
    lo = [lo.X(), lo.Y(), lo.Z()]
    hi = [hi.X(), hi.Y(), hi.Z()]
    return {
        "bbox_min": lo,
        "bbox_max": hi,
        "bbox_size": [h - l for l, h in zip(lo, hi)],
        "com": [com.X(), com.Y(), com.Z()],
        "volume_mm3": float(props.Mass()),
        "surface_area_mm2": float(sprops.Mass()),
        "mass_g": None,
        "density_kg_m3": None,
    }


def write_step(shape, path: Path, name: str) -> None:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.Interface import Interface_Static
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Controller, STEPControl_Writer

    STEPControl_Controller.Init_s()
    Interface_Static.SetCVal_s("write.step.unit", "MM")  # navier_cad.shapes.load_step switches the writer to metres
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    status = writer.Write(str(path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f"StdFail_NotDone: STEP write failed for {path} (status {status})")
    normalize_step_header(path, name)


def write_stl(shape, path: Path) -> None:
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    path.parent.mkdir(parents=True, exist_ok=True)
    BRepMesh_IncrementalMesh(shape, STL_DEFLECTION, False, STL_ANGULAR, True)
    w = StlAPI_Writer()
    w.ASCIIMode = False
    if not w.Write(shape, str(path)):
        raise RuntimeError(f"StdFail_NotDone: STL write failed for {path}")


def as_placements(raw):
    """Body name -> 4x4 row-major floats (a nested list or a flat 16-vector)."""
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("placements must be a dict of body name -> 4x4 row-major matrix")
    out = {}
    for key, val in raw.items():
        if hasattr(val, "tolist"):
            val = val.tolist()
        rows = [list(r) for r in val]
        if len(rows) == 16 and not isinstance(rows[0], (list, tuple)):
            rows = [rows[i : i + 4] for i in range(0, 16, 4)]
        if len(rows) != 4 or any(len(r) != 4 for r in rows):
            raise ValueError(f"placement {key!r} must be 4x4")
        out[str(key)] = [[float(x) for x in row] for row in rows]
    return out


def as_joints(raw):
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("joints must be a dict of joint name -> {origin, axis}")
    out = {}
    for k, v in raw.items():
        if not isinstance(v, dict) or "origin" not in v or "axis" not in v:
            raise ValueError(f"joint {k!r} needs origin and axis")
        out[str(k)] = {"origin": [float(x) for x in list(v["origin"])[:3]], "axis": [float(x) for x in list(v["axis"])[:3]]}
    return out


def main(argv: list[str] | None = None) -> int:
    t0 = last = time.perf_counter()
    timings: dict[str, float] = {}

    def lap(name: str) -> None:
        nonlocal last
        now = time.perf_counter()
        timings[name] = round(timings.get(name, 0.0) + now - last, 3)
        timings["main_s"] = round(now - t0, 3)
        last = now

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
        ns = load_namespace(Path(args.entry))
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
        name = type(e).__name__
        payload = {
            "ok": False,
            "error": f"{name}: {e}",
            "traceback": traceback.format_exc()[-2000:],
            "class": "program" if name in {"AssertionError", "SyntaxError", "NameError", "ValueError"} else "unknown",
        }
        if "StdFail" in name or "ConstructionError" in name or "Standard_Failure" in name or "StdFail_NotDone" in str(e):
            payload["class"] = "kernel"
    payload["timings"] = timings
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in payload if k != "traceback"}))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

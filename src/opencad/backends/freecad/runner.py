"""FreeCAD runner: stdlib + FreeCAD modules only. Invoked under freecadcmd."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path

FILE_NAME_RE = re.compile(r"FILE_NAME\s*\((.*?)\)\s*;", re.S)


def normalize_step_header(path: Path, name: str = "opencad") -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    repl = f"FILE_NAME('{name}.step','1970-01-01T00:00:00',('opencad'),('opencad'),'opencad','opencad','');"
    new, n = FILE_NAME_RE.subn(repl, text, count=1)
    if n:
        path.write_text(new, encoding="utf-8")


def feature_tree(doc) -> list[dict]:
    rows = []
    for obj in doc.Objects:
        typ = getattr(obj, "TypeId", type(obj).__name__)
        valid = True
        try:
            if str(typ).startswith("PartDesign::") and hasattr(obj, "isValid"):
                valid = bool(obj.isValid())
        except Exception:
            valid = False
        rows.append({"name": obj.Name, "label": getattr(obj, "Label", obj.Name), "type": typ, "valid": valid})
    return rows


def _is_result_body(obj) -> bool:
    tid = str(getattr(obj, "TypeId", "") or "")
    return tid.startswith("PartDesign::Body") or tid.startswith("Part::Feature")


def result_bodies(result) -> list:
    """`result` is one PartDesign::Body or Part::Feature, or a list/tuple of those (one per solid)."""
    bodies = list(result) if isinstance(result, (list, tuple)) else [result]
    bad = [
        str(getattr(b, "TypeId", None) or type(b).__name__)
        for b in bodies
        if not _is_result_body(b)
    ]
    if not bodies or bad:
        raise RuntimeError(
            "result must be a PartDesign::Body, Part::Feature, or a tuple of those, got %s" % (bad or "an empty list")
        )
    return bodies


def body_solids(bodies) -> list:
    """Every solid of every body; a Body whose Shape is a Compound (AllowCompound) contributes each of its Solids."""
    out = []
    for b in bodies:
        shape = b.Shape
        out.extend(list(getattr(shape, "Solids", []) or []) or [shape])
    return out


def analyze_bodies(bodies) -> dict:
    """Combined bbox, summed volume and area, volume-weighted centroid (Part.Compound has no CenterOfMass)."""
    solids = body_solids(bodies)
    volume = sum(float(s.Volume) for s in solids)
    if volume <= 0:
        raise RuntimeError("result has no solid volume")
    com = [sum(float(s.Volume) * getattr(s.CenterOfMass, k) for s in solids) / volume for k in "xyz"]
    boxes = [s.BoundBox for s in solids]
    lo = [min(getattr(b, k + "Min") for b in boxes) for k in "XYZ"]
    hi = [max(getattr(b, k + "Max") for b in boxes) for k in "XYZ"]
    return {
        "bbox_min": lo,
        "bbox_max": hi,
        "bbox_size": [h - l for l, h in zip(lo, hi)],
        "com": com,
        "volume_mm3": volume,
        "surface_area_mm2": sum(float(s.Area) for s in solids),
        "mass_g": None,
        "density_kg_m3": None,
    }


def _placements_from_ns(ns):
    """stdlib-only: freecadcmd cannot import opencad. Body name -> 4x4 row-major floats."""
    raw = ns.get("placements")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise RuntimeError("placements must be a dict of body name -> 4x4 matrix")
    out = {}
    for key, val in raw.items():
        if hasattr(val, "tolist"):
            val = val.tolist()
        rows = [list(r) for r in val]
        if len(rows) == 16 and not isinstance(rows[0], (list, tuple)):
            rows = [rows[i : i + 4] for i in range(0, 16, 4)]
        if len(rows) != 4 or any(len(r) != 4 for r in rows):
            raise RuntimeError("placement %r must be 4x4" % key)
        out[str(key)] = [[float(x) for x in row] for row in rows]
    return out


def load_result(entry: Path, name: str = "result"):
    import FreeCAD  # noqa: F401

    entry = Path(entry).resolve()
    sys.path.insert(0, str(entry.parent))  # sibling modules (params, datum, groups) must import under freecadcmd
    ns = {"__name__": "__fc_main__", "__file__": str(entry)}
    src = Path(entry).read_text(encoding="utf-8")
    exec(compile(src, str(entry), "exec"), ns, ns)
    if name not in ns:
        raise RuntimeError("%r is not defined in %s" % (name, entry))
    return ns[name], ns


def _from_env() -> list[str]:
    mapping = {
        "OPENCAD_FC_ENTRY": "--entry",
        "OPENCAD_FC_OUT": "--out",
        "OPENCAD_FC_ANALYZE": "--analyze",
        "OPENCAD_FC_STEP": "--export-step",
        "OPENCAD_FC_STL": "--export-stl",
        "OPENCAD_FC_FCSTD": "--export-fcstd",
        "OPENCAD_FC_RESULT": "--result-name",
    }
    out = []
    for env, flag in mapping.items():
        val = os.environ.get(env)
        if val:
            out += [flag, val]
    return out


def main(argv=None) -> int:
    t0 = last = time.perf_counter()
    timings = {}

    def lap(name):
        nonlocal last
        now = time.perf_counter()
        timings[name] = round(timings.get(name, 0.0) + now - last, 3)
        timings["main_s"] = round(now - t0, 3)
        last = now

    raw = list(sys.argv[1:] if argv is None else argv)
    if raw and raw[0] == "--":
        raw = raw[1:]
    env_args = _from_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--entry", required=True)
    ap.add_argument("--out")
    ap.add_argument("--analyze")
    ap.add_argument("--export-step")
    ap.add_argument("--export-stl")
    ap.add_argument("--export-fcstd")
    ap.add_argument("--result-name", default="result")
    args = ap.parse_args(env_args if env_args else raw)
    payload = {"ok": True}
    try:
        import FreeCAD
        import Mesh
        import MeshPart
        import Part

        lap("imports_s")
        result, ns = load_result(Path(args.entry), args.result_name)
        placements = _placements_from_ns(ns)
        if placements:
            payload["placements"] = placements
        doc = FreeCAD.ActiveDocument
        if doc is None:
            for d in getattr(FreeCAD, "listDocuments", lambda: {})():
                doc = FreeCAD.getDocument(d)
                break
        if doc is None:
            raise RuntimeError("main.py did not create a FreeCAD document")
        doc.recompute()
        bodies = result_bodies(result)
        tree = feature_tree(doc)
        payload["feature_tree"] = tree
        if any(not r["valid"] for r in tree):
            raise RuntimeError("invalid features: %s" % [r["name"] for r in tree if not r["valid"]])
        lap("build_s")
        if args.analyze:
            data = analyze_bodies(bodies)
            Path(args.analyze).parent.mkdir(parents=True, exist_ok=True)
            Path(args.analyze).write_text(json.dumps(data, indent=2), encoding="utf-8")
            payload["analyze"] = data
            lap("analyze_s")
        if args.export_step:
            dest = Path(args.export_step)
            dest.parent.mkdir(parents=True, exist_ok=True)
            Part.export(bodies, str(dest))
            normalize_step_header(dest, Path(args.entry).stem)
            payload["step"] = str(dest)
            lap("step_s")
        if args.export_stl:
            dest = Path(args.export_stl)
            dest.parent.mkdir(parents=True, exist_ok=True)
            # One mesh per Body: meshing a compound welds coincident seating faces and tears every shell open.
            tess = {"LinearDeflection": 0.02, "AngularDeflection": 0.1, "Relative": False}
            shells = [Mesh.Mesh(MeshPart.meshFromShape(Shape=b.Shape, **tess).Topology) for b in bodies]
            mesh = shells[0]
            for shell in shells[1:]:
                mesh.addMesh(shell)
            mesh.write(str(dest))
            payload["stl"] = str(dest)
            lap("stl_s")
        if args.export_fcstd:
            dest = Path(args.export_fcstd)
            dest.parent.mkdir(parents=True, exist_ok=True)
            doc.saveAs(str(dest))
            payload["fcstd"] = str(dest)
            lap("fcstd_s")
    except Exception as e:
        lap("failed_s")
        payload = {
            "ok": False,
            "error": "%s: %s" % (type(e).__name__, e),
            "traceback": traceback.format_exc()[-2000:],
            "class": "program"
            if type(e).__name__ in {"AssertionError", "SyntaxError", "NameError", "RuntimeError"}
            else "unknown",
        }
        err = str(e).lower()
        if "recompute failed" in err or "not done" in err:
            payload["class"] = "kernel"
    payload["timings"] = timings
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in payload if k != "traceback"}))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())

"""Gear checks on exported B-reps: tooth count from a mid-thickness section, and meshing motion (interference and flank gap
through a rotation sweep of two bodies about their own axes). OpenCascade only."""

from __future__ import annotations

import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.GCPnts import GCPnts_UniformAbscissa
from OCP.gp import gp_Ax1, gp_Dir, gp_Pln, gp_Pnt, gp_Trsf
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

from opencad.geomcheck import assembly, brep, pool_context


def section_polar(shape, point: list[float], direction: list[float], at: float, step: float = 0.1) -> np.ndarray:
    """Sample the section of `shape` by the plane through point + at*direction (normal = direction); return (angle, radius) about the axis."""
    d = np.asarray(brep._unit(list(direction)), float)
    p0 = np.asarray(point, float) + at * d
    sec = BRepAlgoAPI_Section(shape, gp_Pln(gp_Pnt(*p0), gp_Dir(*d)))
    sec.Build()
    # in-plane basis
    u = np.cross(d, [0, 0, 1.0]) if abs(d[2]) < 0.9 else np.cross(d, [1.0, 0, 0])
    u /= np.linalg.norm(u)
    v = np.cross(d, u)
    pts = []
    exp = TopExp_Explorer(sec.Shape(), TopAbs_EDGE)
    while exp.More():
        curve = BRepAdaptor_Curve(TopoDS.Edge(exp.Current()))
        ua = GCPnts_UniformAbscissa(curve, step)
        if ua.IsDone():
            for k in range(1, ua.NbPoints() + 1):
                q = curve.Value(ua.Parameter(k))
                w = np.array([q.X(), q.Y(), q.Z()]) - p0
                pts.append((math.atan2(float(w @ v), float(w @ u)), float(math.hypot(w @ u, w @ v))))
        exp.Next()
    arr = np.asarray(pts)
    return arr[np.argsort(arr[:, 0])] if len(arr) else arr


def section_points(shape, point: list[float], normal: list[float], step: float = 0.02) -> np.ndarray:
    """Points every `step` along the section of `shape` by the plane through `point` with normal `normal` (assembly frame)."""
    d = np.asarray(brep._unit(list(normal)), float)
    sec = BRepAlgoAPI_Section(shape, gp_Pln(gp_Pnt(*[float(x) for x in point]), gp_Dir(*d)))
    sec.Build()
    pts = []
    exp = TopExp_Explorer(sec.Shape(), TopAbs_EDGE)
    while exp.More():
        curve = BRepAdaptor_Curve(TopoDS.Edge(exp.Current()))
        ua = GCPnts_UniformAbscissa(curve, step)
        if ua.IsDone():
            for k in range(1, ua.NbPoints() + 1):
                q = curve.Value(ua.Parameter(k))
                pts.append((q.X(), q.Y(), q.Z()))
        exp.Next()
    return np.asarray(pts, float).reshape(-1, 3)


def rack_pitch(shape, point: list[float], normal: list[float], along: list[float], toward: list[float], step: float = 0.02) -> dict[str, Any]:
    """Tooth pitch of a rack from its section in the pinion's mesh plane (through `point`, normal the pinion axis): the profile
    nearest the pinion along the slider axis `along` (`toward` points from the pinion axis to the rack), its teeth where it comes
    closer than midway between tip and root line, and the pitch as the slope of the interior tooth centres (edges interpolated)."""
    pts = section_points(shape, point, normal, step)
    if len(pts) < 20:
        return {"teeth": 0, "error": "no section in the pinion's mesh plane"}
    p0, u_dir, t_dir = np.asarray(point, float), np.asarray(brep._unit(list(along)), float), np.asarray(brep._unit(list(toward)), float)
    u, t = (pts - p0) @ u_dir, (pts - p0) @ t_dir
    width = 3 * step
    bins = int((u.max() - u.min()) / width) + 1
    idx = np.clip(((u - u.min()) / width).astype(int), 0, bins - 1)
    prof = np.full(bins, np.nan)
    for i, ti in zip(idx, t):
        if np.isnan(prof[i]) or ti < prof[i]:
            prof[i] = ti
    ok = ~np.isnan(prof)
    filled = np.interp(np.arange(bins), np.flatnonzero(ok), prof[ok])
    tip, root = float(filled.min()), float(filled.max())
    if root - tip < 0.2:
        return {"teeth": 0, "tip": tip, "root": root, "note": "no relief toward the pinion: not a toothed rack"}
    mid = (tip + root) / 2
    tooth = filled < mid
    edges = np.flatnonzero(np.diff(tooth.astype(int)))
    cross = [u.min() + (k + 0.5 + (mid - filled[k]) / (filled[k + 1] - filled[k])) * width for k in edges]
    rises = [c for k, c in zip(edges, cross) if tooth[k + 1]]
    falls = [c for k, c in zip(edges, cross) if not tooth[k + 1]]
    centres = [(r + next(f for f in falls if f > r)) / 2 for r in rises if any(f > r for f in falls)]  # whole teeth only
    teeth = len(rises) + (1 if tooth[0] else 0)
    if len(centres) < 2:
        return {"teeth": teeth, "tip": tip, "root": root, "error": "fewer than two whole teeth in the section"}
    pitch = float(np.polyfit(np.arange(len(centres)), np.asarray(centres), 1)[0])
    return {"teeth": teeth, "whole_teeth": len(centres), "pitch": abs(pitch), "tip": tip, "root": root, "samples": int(len(pts))}


def _angular_profile(samples: np.ndarray, bins: int, outermost: bool) -> np.ndarray:
    """r(theta) of the boundary read: the largest (outermost) or smallest radius per angular bin, empty bins interpolated."""
    idx = ((samples[:, 0] + math.pi) / (2 * math.pi) * bins).astype(int) % bins
    prof = np.full(bins, np.nan)
    for i, r in zip(idx, samples[:, 1]):
        if np.isnan(prof[i]) or (r > prof[i] if outermost else r < prof[i]):
            prof[i] = r
    return np.where(np.isnan(prof), np.interp(np.arange(bins), np.flatnonzero(~np.isnan(prof)), prof[~np.isnan(prof)], period=bins), prof)


def tooth_count(shape, point: list[float], direction: list[float], at: float, module: float, expected_teeth: int | None = None) -> dict[str, Any]:
    """Count teeth as the number of angular runs where the outer boundary radius exceeds (tip radius - 0.6 module).

    The tip radius is taken from the section itself (max radius), so the check does not presuppose the pitch radius. A plain
    outer boundary (a ring gear's rim) means the teeth are on the inner boundary: they are then counted where it comes inside
    (its tip radius + 0.6 module), and the result says `internal`.
    """
    ar = section_polar(shape, point, direction, at)
    if len(ar) < 10:
        return {"ok": False, "error": "no section", "teeth": 0}
    r_tip = float(ar[:, 1].max())
    # outer loop only: a bore or socket inside the toothed loop lies more than a whole tooth depth (~2.25 module)
    # below the tip; its samples must not fall into angular bins the outer loop left empty and read as dips
    outer = ar[ar[:, 1] > r_tip - 3.0 * module]
    if len(outer) < 10:
        outer = ar
    bins = 3600
    filled = _angular_profile(outer, bins, True)
    kind: dict[str, Any] = {}
    if float(filled.max() - filled.min()) < 0.25 * module:
        r_in = float(ar[:, 1].min())
        inner = ar[ar[:, 1] < r_in + 3.0 * module]
        filled = _angular_profile(inner, bins, False)
        r_tip, r_root = float(filled.min()), float(filled.max())
        thresh = r_tip + 0.6 * module
        tooth = filled < thresh
        kind = {"internal": True, "inner_samples": int(len(inner))}
    else:
        r_root = float(outer[:, 1].min())
        thresh = r_tip - 0.6 * module
        tooth = filled > thresh
    runs = int(np.sum((tooth.astype(int) - np.roll(tooth.astype(int), 1)) == 1))
    res = {"teeth": runs, "tip_radius": r_tip, "root_radius": r_root, "threshold": thresh, "samples": int(len(ar)), "outer_samples": int(len(outer)), **kind, "ok": True}
    if expected_teeth is not None:
        res.update({"expected": expected_teeth, "ok": runs == expected_teeth})
    return res


def _rotate(shape, point: list[float], direction: list[float], angle_rad: float):
    t = gp_Trsf()
    t.SetRotation(gp_Ax1(gp_Pnt(*point), gp_Dir(*brep._unit(list(direction)))), angle_rad)
    return BRepBuilderAPI_Transform(shape, t, True).Shape()


COARSE_STEPS = int(os.environ.get("OPENCAD_MESH_COARSE", "12"))


def mesh_workers() -> int:
    """Meshing-pose processes: OPENCAD_MESH_WORKERS, else cores - 1 up to 8, capped by memory."""
    from opencad import resources

    n = os.environ.get("OPENCAD_MESH_WORKERS")
    return max(1, int(n)) if n else resources.pool_workers(min(8, (os.cpu_count() or 2) - 1))


def _pose(gear_a, gear_b, axis_a, axis_b, ratio: float, deg: float, interference_tol: float, backlash_max: float) -> dict[str, Any]:
    th = math.radians(deg)
    a = _rotate(gear_a, axis_a[0], axis_a[1], th)
    b = _rotate(gear_b, axis_b[0], axis_b[1], -th * ratio)
    inter = assembly.common_volume(a, b)
    gap = assembly.min_distance(a, b) if inter <= interference_tol else 0.0
    return {"theta_deg": round(deg, 6), "interference_volume": inter, "gap": gap, "ok": inter <= interference_tol and gap <= backlash_max + 1e-6}


def _poses_from_files(job: tuple[str, str, tuple, tuple, float, list[float], float, float]) -> list[dict[str, Any]]:
    """Worker-process entry: read both gears from BREP files and evaluate a chunk of poses (TopoDS shapes do not pickle)."""
    path_a, path_b, axis_a, axis_b, ratio, degs, interference_tol, backlash_max = job
    ga, gb = _read_brep(path_a), _read_brep(path_b)
    return [_pose(ga, gb, axis_a, axis_b, ratio, d, interference_tol, backlash_max) for d in degs]


def _write_brep(shape, path: Path) -> None:
    from OCP.BRepTools import BRepTools

    BRepTools.Write_s(shape, str(path))


def _read_brep(path: str):
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape

    s = TopoDS_Shape()
    BRepTools.Read_s(s, str(path), BRep_Builder())
    return s


def _evaluate(gear_a, gear_b, axis_a, axis_b, ratio, degs: list[float], interference_tol: float, backlash_max: float, workers: int) -> list[dict[str, Any]]:
    if workers <= 1 or len(degs) < 4:
        return [_pose(gear_a, gear_b, axis_a, axis_b, ratio, d, interference_tol, backlash_max) for d in degs]
    from concurrent.futures import ProcessPoolExecutor

    with tempfile.TemporaryDirectory(prefix="opencad-mesh-") as td:
        pa, pb = Path(td) / "a.brep", Path(td) / "b.brep"
        _write_brep(gear_a, pa)
        _write_brep(gear_b, pb)
        n = min(workers, len(degs))
        chunks = [degs[i::n] for i in range(n)]
        jobs = [(str(pa), str(pb), axis_a, axis_b, ratio, ch, interference_tol, backlash_max) for ch in chunks if ch]
        try:
            with ProcessPoolExecutor(max_workers=n, mp_context=pool_context()) as pool:
                rows = [r for part in pool.map(_poses_from_files, jobs) for r in part]
        except Exception as e:  # a pool failure falls back to the sequential path, never to a missing verdict
            print(f"[gears] parallel pose evaluation failed ({e!r}); evaluating sequentially", flush=True)
            rows = [_pose(gear_a, gear_b, axis_a, axis_b, ratio, d, interference_tol, backlash_max) for d in degs]
    return rows


def mesh_motion(gear_a, gear_b, axis_a: tuple[list[float], list[float]], axis_b: tuple[list[float], list[float]], *, ratio: float, pitch_deg: float,
                steps: int = 10, backlash_max: float = 0.3, interference_tol: float = 1e-3, refine: bool = True, coarse: int | None = None,
                workers: int | None = None) -> dict[str, Any]:
    """Rotate gear A by theta and gear B by -theta*ratio over one pitch of A; every pose must be interference-free with a flank gap inside [0, backlash_max].

    ratio = teeth_a / teeth_b (B turns slower, opposite sense). `steps` is the fine resolution the contract asks for; the sweep is
    coarse-to-fine: `coarse` poses over the pitch (parallel worker processes), then the fine resolution across the coarse interval
    on each side of the worst pose (largest interference, then largest gap). The 3-D booleans dominate the cost, so 72 requested
    steps cost about 12 + 12 poses instead of 73.
    """
    coarse = COARSE_STEPS if coarse is None else coarse
    workers = mesh_workers() if workers is None else workers
    fine = pitch_deg / max(1, steps)
    n_coarse = max(2, min(steps, coarse))
    degs = [round(pitch_deg * i / n_coarse, 6) for i in range(n_coarse + 1)]
    rows = _evaluate(gear_a, gear_b, axis_a, axis_b, ratio, degs, interference_tol, backlash_max, workers)
    refined: list[float] = []
    if refine and rows and steps > n_coarse:
        worst = max(rows, key=lambda r: (r["interference_volume"], r["gap"]))
        h = pitch_deg / n_coarse
        lo, hi = worst["theta_deg"] - h, worst["theta_deg"] + h
        k = int(round((hi - lo) / fine))
        seen = {r["theta_deg"] for r in rows}
        refined = [round(lo + i * fine, 6) for i in range(k + 1)]
        refined = [d for d in refined if 0 <= d <= pitch_deg and d not in seen]
        rows += _evaluate(gear_a, gear_b, axis_a, axis_b, ratio, refined, interference_tol, backlash_max, workers)
    elif refine and rows:
        worst = max(rows, key=lambda r: (r["interference_volume"], r["gap"]))
        h = pitch_deg / n_coarse / 2
        extra = [d for d in (worst["theta_deg"] - h, worst["theta_deg"] + h) if 0 <= d <= pitch_deg]
        rows += _evaluate(gear_a, gear_b, axis_a, axis_b, ratio, extra, interference_tol, backlash_max, workers)
        refined = extra
    rows.sort(key=lambda r: r["theta_deg"])
    return {
        "poses": rows, "ratio": ratio, "pitch_deg": pitch_deg, "backlash_max": backlash_max, "requested_steps": steps, "coarse_steps": n_coarse,
        "refined_poses": len(refined), "workers": workers,
        "max_interference": max(r["interference_volume"] for r in rows), "gap_min": min(r["gap"] for r in rows), "gap_max": max(r["gap"] for r in rows),
        "ok": all(r["ok"] for r in rows),
    }

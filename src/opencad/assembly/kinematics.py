"""Kinematics: drive each declared motion through its range with transmissions propagated and closed loops solved, check every
moving body pair for interference at every pose, sweep gear meshes through one pitch, measure gear ratios from tooth counts
(external, internal and rack), and check joint limits. OpenCascade only; poses run in parallel worker processes that read the
placed bodies from BREP files."""

from __future__ import annotations

import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from opencad import resources
from opencad.assembly import AsmCtx
from opencad.assembly import joints as jm
from opencad.geomcheck import brep, pool_context


def kin_workers() -> int:
    """Pose-evaluation processes: OPENCAD_KIN_WORKERS, else cores - 1 up to 8, capped by memory."""
    n = os.environ.get("OPENCAD_KIN_WORKERS")
    return max(1, int(n)) if n else resources.pool_workers(min(8, (os.cpu_count() or 2) - 1))


def load_rest(actx: AsmCtx) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    from opencad.backends.placements import read_placements

    raw = read_placements(actx.results_dir / "export" / "placements.json") or {}
    placements = {k: np.asarray(v, float) for k, v in raw.items()}
    shapes = {}
    for p in actx.contract.parts:
        placements.setdefault(p.name, np.eye(4))
        f = actx.placed_step(p.name)
        if f.exists():
            shapes[p.name] = brep.read_step(f)
    return placements, shapes


def deltas(actx: AsmCtx, placements: dict[str, np.ndarray], values: dict[str, float]) -> dict[str, np.ndarray]:
    """Motion of each placed body from rest: M_b(q) M_b^-1."""
    ps = jm.poses(actx.contract, placements, values)
    return {n: ps[n] @ np.linalg.inv(placements[n]) for n in ps}


def _trsf(m: np.ndarray):
    from OCP.gp import gp_Trsf

    t = gp_Trsf()
    t.SetValues(*[float(m[i, j]) for i in range(3) for j in range(4)])
    return t


def moved(shape: Any, m: np.ndarray) -> Any:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

    if np.allclose(m, np.eye(4), atol=1e-12):
        return shape
    return BRepBuilderAPI_Transform(shape, _trsf(m), True).Shape()


def _aabb(lo: list[float], hi: list[float], m: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    corners = np.array([[x, y, z, 1.0] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    pts = (m @ corners.T).T[:, :3]
    return pts.min(axis=0), pts.max(axis=0)


def _overlap(a: tuple[np.ndarray, np.ndarray], b: tuple[np.ndarray, np.ndarray], margin: float = 0.01) -> bool:
    return bool(np.all(a[0] <= b[1] + margin) and np.all(b[0] <= a[1] + margin))


def _eval_tasks(job: tuple[dict[str, str], list[tuple[int, str, str, list[float], list[float]]]]) -> list[tuple[int, str, str, float]]:
    """Worker-process entry: read the bodies from BREP files (TopoDS shapes do not pickle) and compute common volumes."""
    from opencad.geomcheck import assembly as geo
    from opencad.geomcheck.gears import _read_brep

    paths, tasks = job
    shapes = {n: _read_brep(p) for n, p in paths.items()}
    out = []
    for k, a, b, ma, mb in tasks:
        va = moved(shapes[a], np.asarray(ma, float).reshape(4, 4))
        vb = moved(shapes[b], np.asarray(mb, float).reshape(4, 4))
        out.append((k, a, b, float(geo.common_volume(va, vb))))
    return out


def interference(shapes: dict[str, Any], tasks: list[tuple[int, str, str, np.ndarray, np.ndarray]], workers: int | None = None) -> dict[tuple[int, str, str], float]:
    from opencad.geomcheck import assembly as geo
    from opencad.geomcheck.gears import _write_brep

    if not tasks:
        return {}
    workers = kin_workers() if workers is None else workers
    if workers <= 1 or len(tasks) < 4:
        return {(k, a, b): float(geo.common_volume(moved(shapes[a], ma), moved(shapes[b], mb))) for k, a, b, ma, mb in tasks}
    from concurrent.futures import ProcessPoolExecutor

    with tempfile.TemporaryDirectory(prefix="opencad-kin-") as td:
        names = sorted({n for _, a, b, _, _ in tasks for n in (a, b)})
        paths = {}
        for n in names:
            paths[n] = str(Path(td) / f"{n}.brep")
            _write_brep(shapes[n], Path(paths[n]))
        flat = [(k, a, b, ma.ravel().tolist(), mb.ravel().tolist()) for k, a, b, ma, mb in tasks]
        n = min(workers, len(flat))
        jobs = [(paths, flat[i::n]) for i in range(n)]
        try:
            with ProcessPoolExecutor(max_workers=n, mp_context=pool_context()) as pool:
                rows = [r for part in pool.map(_eval_tasks, jobs) for r in part]
        except Exception as e:  # a pool failure falls back to the sequential path, never to a missing verdict
            print(f"[kinematics] parallel evaluation failed ({e!r}); evaluating sequentially", flush=True)
            rows = [(k, a, b, float(geo.common_volume(moved(shapes[a], ma), moved(shapes[b], mb)))) for k, a, b, ma, mb in tasks]
    return {(k, a, b): v for k, a, b, v in rows}


def sweep(actx: AsmCtx, m: Any, placements: dict[str, np.ndarray], shapes: dict[str, Any]) -> dict[str, Any]:
    a = actx.contract
    qs = [m.range[0] + (m.range[1] - m.range[0]) * i / m.steps for i in range(m.steps + 1)]
    path = jm.solve_path(a, placements, [{m.drive: q} for q in qs])
    values = [v for v, _ in path]
    loops = not jm.is_tree(a)
    pairs = [tuple(p) for p in m.pairs] or jm.moving_pairs(a, placements, values)
    pairs = [(x, y) for x, y in pairs if x in shapes and y in shapes]
    boxes = {n: brep.bbox(s) for n, s in shapes.items()}
    tasks, skipped = [], 0
    pose_deltas = []
    for k, v in enumerate(values):
        d = deltas(actx, placements, v)
        pose_deltas.append(d)
        for x, y in pairs:
            if _overlap(_aabb(*boxes[x], d[x]), _aabb(*boxes[y], d[y])):
                tasks.append((k, x, y, d[x], d[y]))
            else:
                skipped += 1
    vols = interference(shapes, tasks)
    rows = []
    for k, (q, v) in enumerate(zip(qs, values)):
        inter = {f"{x}|{y}": vols.get((k, x, y), 0.0) for x, y in pairs}
        worst = max(inter.values(), default=0.0)
        info = path[k][1]
        rows.append({"q": q, "joints": {n: round(val, 9) for n, val in v.items() if val}, "interference": inter, "max_interference": worst,
                     "ok": all(val <= m.interference_tolerance for val in inter.values()) and info["ok"],
                     **({"closure_mm": info["closure_mm"], "closure_deg": info["closure_deg"]} if loops else {})})
    violations = []
    for j in a.joints:
        if j.limits is None:
            continue
        for v in values:
            if not (j.limits[0] - 1e-9 <= v.get(j.name, 0.0) <= j.limits[1] + 1e-9):
                violations.append({"joint": j.name, "value": v[j.name], "limits": list(j.limits)})
                break
    out = {"drive": m.drive, "range": list(m.range), "steps": m.steps, "pairs": [list(p) for p in pairs], "poses": rows, "boolean_ops": len(tasks),
           "prefiltered": skipped, "max_interference": max((r["max_interference"] for r in rows), default=0.0), "limit_violations": violations,
           "ok": all(r["ok"] for r in rows) and not violations}
    if loops:
        infos = [i for _, i in path]
        out["loop"] = {"closure_mm_max": max(i["closure_mm"] for i in infos), "closure_deg_max": max(i["closure_deg"] for i in infos),
                       "transmission_residual_max": max(i["residual"] for i in infos), "open_at": [q for q, i in zip(qs, infos) if not i["ok"]],
                       "free": sorted({n for i in infos for n in i["free"]})}
    return out


def axial_span(shape: Any, point: np.ndarray, direction: np.ndarray) -> tuple[float, float]:
    lo, hi = brep.bbox(shape)
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    t = (corners - point) @ direction
    return float(t.min()), float(t.max())


RACK_RATIO_REL = 1e-3  # a rack's pitch is measured from sampled flanks, not counted: relative band on its mm/deg ratio


def count_teeth(shape: Any, point: np.ndarray, direction: np.ndarray, at: float | None = None, internal: bool = False) -> dict[str, Any]:
    """Tooth count from the section at `at` along the axis (default mid-extent), thresholded midway between root and tip (no module
    needed). A compound gear must be cut where it meshes: pass the axial overlap with its mate. `internal` reads a ring gear's
    inner outline (its tips point inward, so `tip_radius` is the smallest radius)."""
    from opencad.geomcheck.gears import section_polar

    if at is None:
        t0, t1 = axial_span(shape, point, direction)
        at = (t0 + t1) / 2
    lo, hi = brep.bbox(shape)
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) - point
    r_est = float(np.max(np.linalg.norm(corners - np.outer(corners @ direction, direction), axis=1)))
    step = max(r_est / 600, 1e-5)  # a tooth tip spans several samples at any gear size (mm or cm models)
    ar = section_polar(shape, point.tolist(), direction.tolist(), at, step=step)
    if len(ar) < 20:
        return {"teeth": 0, "error": "no section at mid-extent", "at": at}
    # a bin must hold several samples of the outline read, or edges beyond it (a hub circle under the teeth, a ring's rim) win empty bins
    bins = max(360, int(2 * math.pi * float(ar[:, 1].min() if internal else ar[:, 1].max()) / (3 * step)))
    idx = ((ar[:, 0] + math.pi) / (2 * math.pi) * bins).astype(int) % bins
    prof = np.full(bins, np.nan)
    for i, r in zip(idx, ar[:, 1]):
        if np.isnan(prof[i]) or (r < prof[i] if internal else r > prof[i]):
            prof[i] = r
    ok = ~np.isnan(prof)
    filled = np.interp(np.arange(bins), np.flatnonzero(ok), prof[ok], period=bins)
    r_tip, r_root = (float(filled.min()), float(filled.max())) if internal else (float(filled.max()), float(filled.min()))
    kind = {"internal": True} if internal else {}
    if abs(r_tip - r_root) < 0.2:
        return {"teeth": 0, "tip_radius": r_tip, "root_radius": r_root, "at": at, **kind, "note": "no radial relief: not a toothed profile"}
    tooth = filled < (r_tip + r_root) / 2 if internal else filled > (r_tip + r_root) / 2
    runs = int(np.sum((tooth.astype(int) - np.roll(tooth.astype(int), 1)) == 1))
    return {"teeth": runs, "tip_radius": r_tip, "root_radius": r_root, "at": at, **kind}


def _pair_teeth(ga: Any, gb: Any, od: np.ndarray, ad: np.ndarray, on: np.ndarray, an: np.ndarray, h: float, centre: float) -> tuple[dict[str, Any], dict[str, Any], bool]:
    """Both counts at height h along the driver axis; a gear that encloses its mate is a ring and is read internally."""
    hb = float((od - on) @ an + h * (ad @ an))
    ta, tb = count_teeth(ga, od, ad, h), count_teeth(gb, on, an, hb)
    if centre + tb.get("tip_radius", 0.0) < ta.get("tip_radius", 0.0):
        ta = count_teeth(ga, od, ad, h, internal=True)
    elif centre + ta.get("tip_radius", 0.0) < tb.get("tip_radius", 0.0):
        tb = count_teeth(gb, on, an, hb, internal=True)
    if not (ta.get("teeth") and tb.get("teeth")):
        return ta, tb, False
    if ta.get("internal"):
        return ta, tb, centre + tb["tip_radius"] > ta["tip_radius"]
    if tb.get("internal"):
        return ta, tb, centre + ta["tip_radius"] > tb["tip_radius"]
    return ta, tb, ta["tip_radius"] + tb["tip_radius"] > centre


def meshing_teeth(ga: Any, gb: Any, od: np.ndarray, ad: np.ndarray, on: np.ndarray, an: np.ndarray, heights: int = 7) -> tuple[dict[str, Any], dict[str, Any]]:
    """Tooth counts of two gears where they mesh: heights in their axial overlap at which the tips reach across the centre
    distance (a compound gear's other stage does not), the most frequent count pair among them. A ring gear is read internally."""
    from collections import Counter

    a0, a1 = axial_span(ga, od, ad)
    b0, b1 = axial_span(gb, od, ad)
    lo, hi = max(a0, b0), min(a1, b1)
    if hi <= lo:
        return count_teeth(ga, od, ad), count_teeth(gb, on, an)
    w = on - od
    centre = float(np.linalg.norm(w - (w @ ad) * ad))
    rows = []
    for h in np.linspace(lo, hi, heights + 2)[1:-1]:
        ta, tb, reach = _pair_teeth(ga, gb, od, ad, on, an, float(h), centre)
        if reach:
            rows.append((ta["teeth"], tb["teeth"], ta, tb))
    if not rows:
        ta, tb, _ = _pair_teeth(ga, gb, od, ad, on, an, (lo + hi) / 2, centre)
        return ta, tb
    (na, nb), _ = Counter((r[0], r[1]) for r in rows).most_common(1)[0]
    ta, tb = next((r[2], r[3]) for r in rows if (r[0], r[1]) == (na, nb))
    return {**ta, "heights_meshing": len(rows)}, {**tb, "heights_meshing": len(rows)}


def rack_ratio(pinion: Any, rack: Any, op: np.ndarray, ap: np.ndarray, slide: np.ndarray) -> dict[str, Any]:
    """mm of rack travel per degree of pinion rotation from the pinion's tooth count and the rack's measured pitch, signed by the
    direction the pinion's pitch point moves along the slider axis."""
    from opencad.geomcheck import gears

    p0, p1 = axial_span(pinion, op, ap)
    r0, r1 = axial_span(rack, op, ap)
    if min(p1, r1) <= max(p0, r0):
        return {"error": "pinion and rack do not overlap along the pinion axis"}
    h = (max(p0, r0) + min(p1, r1)) / 2
    tp = count_teeth(pinion, op, ap, h)
    lo, hi = brep.bbox(rack)
    w = (np.asarray(lo) + np.asarray(hi)) / 2 - op
    w = w - (w @ ap) * ap
    w = w - (w @ slide) * slide
    if float(np.linalg.norm(w)) < 1e-9:
        return {"pinion": tp, "error": "the rack lies on the pinion axis"}
    toward = w / np.linalg.norm(w)
    rp = gears.rack_pitch(rack, (op + h * ap).tolist(), ap.tolist(), slide.tolist(), toward.tolist())
    out: dict[str, Any] = {"pinion": tp, "rack": rp}
    if tp.get("teeth") and rp.get("pitch"):
        sense = 1.0 if float(np.cross(ap, toward) @ slide) > 0 else -1.0
        out["mm_per_deg"] = sense * tp["teeth"] * rp["pitch"] / 360.0
    return out


def transmission(actx: AsmCtx, t: Any, placements: dict[str, np.ndarray], shapes: dict[str, Any]) -> dict[str, Any]:
    from opencad.geomcheck import gears

    a = actx.contract
    jd, jn = a.joint(t.driver), a.joint(t.driven)
    axes = jm.world_axes(a, placements)
    (od, ad), (on, an) = axes[t.driver], axes[t.driven]
    out: dict[str, Any] = {"kind": t.kind, "driver": t.driver, "driven": t.driven, "ratio": t.ratio, "ok": True, **({"carrier": t.carrier} if t.carrier else {})}
    ga, gb = shapes.get(jd.child), shapes.get(jn.child)
    fixed_member = t.carrier is not None and jd.kind == "rigid"  # a fixed ring or sun meshing with a planet
    if t.kind == "gear" and ga is not None and gb is not None and (jd.rotates or fixed_member) and jn.rotates:
        ta, tb = meshing_teeth(ga, gb, od, ad, on, an)
        out["teeth"] = {jd.child: ta, jn.child: tb}
        if ta.get("teeth") and tb.get("teeth"):
            sense = 1.0 if float(np.dot(ad, an)) > 0 else -1.0
            internal = bool(ta.get("internal") or tb.get("internal"))  # an internal mesh turns both gears the same way
            measured = (sense if internal else -sense) * ta["teeth"] / tb["teeth"]
            out["ratio_measured"] = measured
            out["ratio_ok"] = abs(measured - t.ratio) <= 1e-6 * max(1.0, abs(t.ratio))
            out["ok"] = out["ok"] and out["ratio_ok"]
    elif t.kind == "gear" and ga is not None and gb is not None and {jd.kind, jn.kind} == {"revolute", "slider"}:
        pinion, rack, (op, ap), slide = (ga, gb, (od, ad), an) if jd.rotates else (gb, ga, (on, an), ad)
        rr = rack_ratio(pinion, rack, op, ap, slide)
        out["rack"] = rr
        if rr.get("mm_per_deg"):
            measured = rr["mm_per_deg"] if jd.rotates else 1.0 / rr["mm_per_deg"]
            out["ratio_measured"] = measured
            out["ratio_ok"] = abs(measured - t.ratio) <= RACK_RATIO_REL * abs(t.ratio)
            out["ok"] = out["ok"] and out["ratio_ok"]
    if t.mesh is not None and ga is not None and gb is not None:
        mm = gears.mesh_motion(ga, gb, (od.tolist(), ad.tolist()), (on.tolist(), an.tolist()), ratio=-t.ratio, pitch_deg=t.mesh.pitch_deg,
                               steps=t.mesh.steps, backlash_max=t.mesh.backlash_max, interference_tol=t.mesh.interference_tolerance)
        out["mesh"] = mm
        out["ok"] = out["ok"] and bool(mm["ok"])
    elif t.mesh is not None:
        out.update(ok=False, error=f"bodies {jd.child} / {jn.child} missing from the export")
    return out


def run(actx: AsmCtx) -> dict[str, Any]:
    placements, shapes = load_rest(actx)
    missing = [p.name for p in actx.contract.parts if p.placed and p.name not in shapes]
    motions = {m.name: sweep(actx, m, placements, shapes) for m in actx.contract.acceptance.motions}
    trans = {t.name: transmission(actx, t, placements, shapes) for t in actx.contract.transmissions}
    ok = not missing and all(v["ok"] for v in motions.values()) and all(v["ok"] for v in trans.values())
    return {"ok": ok, "missing_bodies": missing, "motions": motions, "transmissions": trans, "closures": [j.name for j in actx.contract.joints if j.closure],
            "workers": kin_workers()}

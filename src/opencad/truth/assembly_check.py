"""`python -m opencad.truth assembly-check <work>`: the assembly worker's local critic.

Computes the evaluator's numbers (axis angle, axis line distance, key-point axial offset, interference, gap, flip)
from the worker's `assembly.yaml` and the task's `joint-task.json` alone: no truth, no hosted engine. The joint key
points and axis directions in `joint-task.json` are the joint definition; the dataset's poses are not needed.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from opencad.geomcheck import assembly, brep
from opencad.truth import assembly_task as at


def check(work: Path, manifest: Path | None = None) -> dict[str, Any]:
    work = Path(work)
    jt = json.loads((work / "joint-task.json").read_text(encoding="utf-8"))
    man = yaml.safe_load((manifest or work / "assembly.yaml").read_text(encoding="utf-8")) or {}
    bodies = man.get("bodies") or man
    b1, b2 = jt["body_one"], jt["body_two"]
    if b1 not in bodies or b2 not in bodies:
        return {"ok": False, "error": f"assembly.yaml must place both bodies {b1} and {b2}", "found": sorted(bodies)}
    a1, a2 = at.manifest_matrix(bodies[b1]), at.manifest_matrix(bodies[b2])
    k1, d1 = at.transform_line(np.asarray(jt["one"]["key_point_local_mm"], float), np.asarray(jt["one"]["axis_direction_local"], float), a1)
    k2, d2 = at.transform_line(np.asarray(jt["two"]["key_point_local_mm"], float), np.asarray(jt["two"]["axis_direction_local"], float), a2)
    dot = float(np.dot(d1, d2))
    ang = math.degrees(math.acos(min(1.0, abs(dot))))
    w = k1 - k2
    line_dist = float(np.linalg.norm(w - np.dot(w, d2) * d2))
    axial = float(np.dot(w, d2))
    ev = jt.get("evaluator") or {}
    off = float(jt["offset_mm"])
    flipped_now = dot < 0
    checks: dict[str, Any] = {
        "axis_angle_deg": {"measured": ang, "max": ev.get("axis_angle_max_deg", 2.0), "ok": ang <= ev.get("axis_angle_max_deg", 2.0)},
        "axis_line_distance": {"measured": line_dist, "max": ev.get("axis_line_distance_max_mm", 0.5), "ok": line_dist <= ev.get("axis_line_distance_max_mm", 0.5)},
        "axial_offset": {"measured": axial, "expected": off, "max_error": ev.get("axial_offset_tolerance_mm", 0.5), "ok": abs(axial - off) <= ev.get("axial_offset_tolerance_mm", 0.5)},
        "flip": {"measured": "anti-parallel" if flipped_now else "parallel", "expected": "anti-parallel" if jt.get("is_flipped") else "parallel", "ok": flipped_now == bool(jt.get("is_flipped"))},
    }
    s1 = at.apply(brep.read_step(work / f"{b1}.step"), a1)
    s2 = at.apply(brep.read_step(work / f"{b2}.step"), a2)
    inter = assembly.common_volume(s1, s2)
    gap = assembly.min_distance(s1, s2) if inter <= 1.0 else 0.0
    checks["interference_mm3"] = {"measured": inter, "note": "the evaluator allows max(1, dataset's own interference + 1); a small overlap at the key-point placement is not a reason to move the bodies", "ok": inter <= 1.0}
    checks["gap_mm"] = {"measured": gap, "max": ev.get("gap_max_mm", 1.0), "ok": gap <= ev.get("gap_max_mm", 1.0)}
    ok = all(c["ok"] for k, c in checks.items() if k != "interference_mm3")
    return {"ok": ok, "checks": checks, "key_points_placed": {"one": k1.round(4).tolist(), "two": k2.round(4).tolist()},
            "axes_placed": {"one": d1.round(6).tolist(), "two": d2.round(6).tolist()}, "joint_type": jt.get("joint_type"),
            "note": "PASS here means the four geometric checks match the task; the evaluator additionally judges interference against the dataset's own pose"}


def format_report(r: dict[str, Any]) -> str:
    if r.get("error"):
        return f"assembly-check: {r['error']}"
    lines = [f"assembly-check {'PASS' if r['ok'] else 'FAIL'} ({r.get('joint_type')})"]
    for k, c in r["checks"].items():
        exp = f" expected {c['expected']}" if "expected" in c else (f" max {c['max']}" if "max" in c else "")
        if "max_error" in c:
            exp += f" (+/- {c['max_error']})"
        m = c["measured"]
        lines.append(f"  {'ok  ' if c['ok'] else 'FAIL'} {k}: {m if isinstance(m, str) else round(float(m), 4)}{exp}")
    lines.append(f"  key points placed: one {r['key_points_placed']['one']} two {r['key_points_placed']['two']}")
    if not r["checks"]["interference_mm3"]["ok"]:
        lines.append(f"  note: {r['checks']['interference_mm3']['note']}")
    for name, body in ((r.get("export_agreement") or {}).get("bodies") or {}).items():
        if "error" in body:
            lines.append(f"  FAIL agreement {name}: {body['error']}")
            continue
        vol = body.get("volume_rel")
        haus = body.get("hausdorff_mm")
        lines.append(
            f"  {'ok  ' if body.get('ok') else 'FAIL'} agreement {name}: volume_rel={vol if vol is None else round(float(vol), 6)} "
            f"hausdorff={haus if haus is None else round(float(haus), 4)} mm"
        )
    if r.get("solid_count") is not None:
        lines.append(f"  {'ok  ' if r.get('solid_count') == 2 else 'FAIL'} solid_count: {r.get('solid_count')} expected 2")
    return "\n".join(lines)


def _render_views(src: Path, dest: Path) -> Path | None:
    from opencad import render

    dest.parent.mkdir(parents=True, exist_ok=True)
    snaps = render.render_snapshots(src, dest.parent, ("iso", "front", "top"), px=480)
    keys = [(k, k) for k in ("iso", "front", "top") if snaps.get(k)]
    if not keys:
        return None
    render.sheet({k: Path(snaps[k]) for k, _ in keys}, dest, keys, cols=3, cell_w=480)
    return dest


def check_modelled(
    work: Path,
    entry: Path,
    *,
    backend: str | None = None,
    ledger: Path | None = None,
    manifest: Path | None = None,
) -> dict[str, Any]:
    """Export through the engine, derive yaml from placements, then the joint + agreement critic."""
    import time

    from opencad.backends.placements import read_placements
    from opencad.backends.registry import current_id, get, set_backend
    from opencad.io import utc_now
    from opencad.truth import assembly_agree

    work, entry = Path(work), Path(entry)
    prev = current_id()
    if backend:
        set_backend(backend)
    t0 = time.time()
    tmp = work / "_check-export"
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        eng = get().engine
        step = eng.export(entry, tmp, "step")[0]
        try:
            stl = eng.export(entry, tmp, "stl")[0]
        except Exception:
            stl = None
        if ledger is not None:
            Path(ledger).parent.mkdir(parents=True, exist_ok=True)
            with Path(ledger).open("a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "ts": utc_now(),
                            "cmd": f"engine export step+stl {entry}",
                            "seconds": round(time.time() - t0, 2),
                            "ok": True,
                            "via": "assembly-check",
                        }
                    )
                    + "\n"
                )
        placements = read_placements(tmp / "placements.json")
        if not placements:
            return {"ok": False, "error": f"export wrote no placements.json beside {step}"}
        yaml_path = manifest or work / "assembly.yaml"
        assembly_agree.write_yaml(yaml_path, placements)
        r = check(work, yaml_path)
        agree = assembly_agree.agree(
            step,
            {b: work / f"{b}.step" for b in placements},
            placements,
            bodies_dir=tmp / "bodies",
        )
        from opencad.geomcheck import brep

        solids = brep.analyze_step(step)["solids"]
        r["export_agreement"] = agree
        r["solid_count"] = solids
        r["ok"] = bool(r.get("ok") and agree.get("ok") and solids == 2)
        mesh_src = stl if stl and Path(stl).exists() else step
        views_dir = Path(ledger).parent if ledger else work
        views = _render_views(mesh_src, views_dir / "assembly-views.png")
        if views:
            r["views"] = str(views)
            print(f"assembly-views: {views}", flush=True)
        return r
    finally:
        if backend and prev:
            set_backend(prev)


def main(
    work: Path,
    manifest: Path | None = None,
    as_json: bool = False,
    entry: Path | None = None,
    backend: str | None = None,
    ledger: Path | None = None,
) -> int:
    r = (
        check_modelled(work, entry, backend=backend, ledger=ledger, manifest=manifest)
        if entry
        else check(work, manifest)
    )
    print(json.dumps(r, indent=2, default=str) if as_json else format_report(r))
    return 0 if r.get("ok") else 1

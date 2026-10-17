"""Machine handoff parity across backends: files, gates, per-body volume and centre of mass, envelope, observables, GLB bodies."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from opencad.paths import DESIGNS, RESULTS_BASE, results_dir

BACKENDS = ("cadquery", "build123d", "freecad", "zoo")
VOLUME_REL_MAX = 1e-3
COM_MAX_MM = 0.1  # a gear's centre of mass sits on its axis, so an equivalent mesh phase still compares equal
BBOX_MAX_MM = 0.1
FLOW_REL_MAX = 0.005


def handoff_files(asm: str) -> list[str]:
    return ["assembly.glb", "assembly-clips.glb", "assembly.html", f"{asm}.step", f"{asm}.stl"]


def placed_bodies(asm: str) -> list[str]:
    from opencad.contract import load_assembly

    return [p.name for p in load_assembly(DESIGNS / asm / "assembly.yaml").parts if p.placed]


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def snapshot(asm: str, backend: str, bodies: list[str]) -> dict[str, Any]:
    """What one backend's machine handoff contains, measured from its own export."""
    from opencad.geomcheck import brep

    root = results_dir(asm, backend=backend)
    props = {}
    for b in bodies:
        p = root / "export" / "bodies" / f"{b}.step"
        if p.exists():
            v = brep.volume_props(brep.read_step(p))
            props[b] = {"volume": v["volume"], "com": v["center_of_mass"]}
    env = _json(root / "verify.json").get("envelope") or {}
    obs = _json(root / "simulate.json").get("observables") or {}
    glb = root / "handoff" / "assembly.glb"
    nodes = None
    if glb.exists():
        import trimesh

        nodes = sorted(trimesh.load(str(glb), force="scene").geometry)
    return {
        "files": {f: (root / "handoff" / f).exists() for f in handoff_files(asm)},
        "placements": (root / "export" / "placements.json").exists(),
        "bodies": props,
        "gates": _json(root / "gate_feedback.json").get("summary"),
        "bbox": [env.get("bbox_min"), env.get("bbox_max")] if env.get("bbox_min") else None,
        "observables": {k: (v or {}).get("value") for k, v in obs.items()},
        "glb_nodes": nodes,
    }


def checks(asm: str, cur: dict[str, Any], ref: dict[str, Any], bodies: list[str]) -> list[tuple[bool, str]]:
    out: list[tuple[bool, str]] = []
    missing = [f for f, ok in cur["files"].items() if not ok]
    out.append((not missing, f"handoff files present (missing {missing or 'none'})"))
    out.append((cur["placements"], "export/placements.json present"))
    absent = [b for b in bodies if b not in cur["bodies"]]
    out.append((not absent, f"export/bodies for every placed body (missing {absent or 'none'})"))
    out.append((cur["gates"] == ref["gates"], f"gates {cur['gates']} vs reference {ref['gates']}"))
    for b in bodies:
        c, r = cur["bodies"].get(b), ref["bodies"].get(b)
        if not c or not r:
            continue
        vrel = abs(c["volume"] - r["volume"]) / r["volume"] if r["volume"] else float("inf")
        dcom = float(np.linalg.norm(np.subtract(c["com"], r["com"])))
        out.append((vrel <= VOLUME_REL_MAX and dcom <= COM_MAX_MM, f"body {b}: volume rel {vrel:.2e} (max {VOLUME_REL_MAX:g}), COM {dcom:.4f} mm (max {COM_MAX_MM})"))
    if cur["bbox"] and ref["bbox"]:
        d = float(np.max(np.abs(np.subtract(cur["bbox"], ref["bbox"]))))
        out.append((d <= BBOX_MAX_MM, f"assembly bbox max difference {d:.4f} mm (max {BBOX_MAX_MM})"))
    else:
        out.append((False, "assembly bbox missing from verify.json"))
    dc, dr = cur["observables"].get("driveRatio"), ref["observables"].get("driveRatio")
    if dr is not None:
        out.append((dc is not None and abs(dc - dr) < 1e-9, f"driveRatio {dc} vs reference {dr}"))
    fc, fr = cur["observables"].get("flowRate"), ref["observables"].get("flowRate")
    if fr is not None:
        ok = fc is not None and abs(fc - fr) / abs(fr) <= FLOW_REL_MAX
        out.append((ok, f"flowRate {fc} vs reference {fr} (max {FLOW_REL_MAX:.1%})"))
    out.append((cur["glb_nodes"] is not None and cur["glb_nodes"] == ref["glb_nodes"], f"GLB bodies {len(cur['glb_nodes'] or [])} vs reference {len(ref['glb_nodes'] or [])}"))
    return out


def compare_assembly(asm: str, *, reference: str = "build123d", backends: tuple[str, ...] = BACKENDS, out: Path | None = None) -> tuple[bool, Path]:
    bodies = placed_bodies(asm)
    ref = snapshot(asm, reference, bodies)
    lines = [f"# {asm}: handoff parity against {reference}", ""]
    all_ok = True
    for be in backends:
        if be == reference:
            continue
        rows = checks(asm, snapshot(asm, be, bodies), ref, bodies)
        ok = all(r for r, _ in rows)
        all_ok = all_ok and ok
        lines += [f"## {be}: {'PASS' if ok else 'FAIL'}", ""] + [f"- {'ok' if r else 'FAIL'} {text}" for r, text in rows] + [""]
    path = out or RESULTS_BASE / "_bakeoff" / f"{asm}-compare.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return all_ok, path

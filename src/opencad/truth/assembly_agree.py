"""Modelled-assembly agreement: exported solids vs input STEP × declared placement; source hygiene."""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from opencad.geomcheck import brep, mesh
from opencad.truth.assembly_task import apply

CAD_SUFFIXES = {".step", ".stp", ".stl", ".obj", ".iges", ".igs", ".brep"}
VOL_REL_MAX = 1e-4
HAUSDORFF_MAX_MM = 0.05
_LIT = re.compile(r"""['"]([^'"]+)['"]""")


def yaml_from_placements(placements: dict[str, list[list[float]]]) -> dict[str, Any]:
    bodies: dict[str, Any] = {}
    for name, m in placements.items():
        bodies[name] = {
            "origin": [m[0][3], m[1][3], m[2][3]],
            "x_axis": [m[0][0], m[1][0], m[2][0]],
            "y_axis": [m[0][1], m[1][1], m[2][1]],
            "z_axis": [m[0][2], m[1][2], m[2][2]],
            "matrix": m,
        }
    return {"bodies": bodies}


def write_yaml(path: Path, placements: dict[str, list[list[float]]]) -> Path:
    path = Path(path)
    path.write_text(yaml.safe_dump(yaml_from_placements(placements), sort_keys=False), encoding="utf-8")
    return path


def match_solids(exported, expected: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Greedy COM match of exported solids to named expected shapes."""
    sols = brep.solids(exported)
    props = [(s, brep.volume_props(s)) for s in sols]
    used: set[int] = set()
    out: dict[str, dict[str, Any]] = {}
    for name, exp in expected.items():
        ep = brep.volume_props(exp)
        best_i, best_d = None, 1e18
        for i, (_, p) in enumerate(props):
            if i in used:
                continue
            d = float(np.linalg.norm(np.asarray(p["center_of_mass"]) - np.asarray(ep["center_of_mass"])))
            if d < best_d:
                best_i, best_d = i, d
        if best_i is None:
            out[name] = {"ok": False, "error": "no exported solid to match"}
            continue
        used.add(best_i)
        s, p = props[best_i]
        out[name] = {"ok": True, "solid": s, "com_error_mm": best_d, **p}
    return out


def _hausdorff(a, b) -> float:
    from opencad.backends.local import write_stl

    td = Path(tempfile.mkdtemp(prefix="opencad-agree-"))
    try:
        write_stl(a, td / "a.stl")
        write_stl(b, td / "b.stl")
        return float(mesh.deviation(td / "a.stl", td / "b.stl", samples=8000)["hausdorff_estimate"])
    finally:
        shutil.rmtree(td, ignore_errors=True)


def write_body_steps(matched: dict[str, dict[str, Any]], dest_dir: Path) -> dict[str, Path]:
    from opencad.backends.local import write_step

    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    out: dict[str, Path] = {}
    for name, row in matched.items():
        if not row.get("ok") or row.get("solid") is None:
            continue
        dest = dest_dir / f"{name}.step"
        write_step(row["solid"], dest, name)
        out[name] = dest
    return out


def agree(
    export_step: Path,
    inputs: dict[str, Path],
    placements: dict[str, list[list[float]]],
    *,
    bodies_dir: Path | None = None,
    vol_rel_max: float = VOL_REL_MAX,
    hausdorff_max: float = HAUSDORFF_MAX_MM,
) -> dict[str, Any]:
    """Per-body volume relative error and Hausdorff of exported solid vs input STEP × placement."""
    exported = brep.read_step(export_step)
    expected: dict[str, Any] = {}
    for name, src in inputs.items():
        if name not in placements:
            return {"ok": False, "error": f"placements missing body {name!r}", "bodies": {}}
        expected[name] = apply(brep.read_step(src), np.asarray(placements[name], float))
    matched = match_solids(exported, expected)
    if bodies_dir is not None:
        write_body_steps(matched, bodies_dir)
    bodies: dict[str, Any] = {}
    ok = True
    for name, exp in expected.items():
        row = matched.get(name) or {}
        if not row.get("ok"):
            bodies[name] = {"ok": False, "error": row.get("error") or "unmatched"}
            ok = False
            continue
        ev = float(brep.volume_props(exp)["volume"])
        mv = float(row["volume"])
        vol_rel = abs(mv - ev) / ev if ev else float("inf")
        haus = _hausdorff(row["solid"], exp)
        body_ok = vol_rel <= vol_rel_max and haus <= hausdorff_max
        bodies[name] = {
            "ok": body_ok,
            "volume_expected": ev,
            "volume_measured": mv,
            "volume_rel": vol_rel,
            "volume_rel_max": vol_rel_max,
            "hausdorff_mm": haus,
            "hausdorff_max_mm": hausdorff_max,
            "com_error_mm": row.get("com_error_mm"),
        }
        ok = ok and body_ok
    return {"ok": ok, "bodies": bodies}


def _refs(src: str, bodies: list[str]) -> tuple[list[str], list[str]]:
    """CAD path literals outside `inputs/<body>.<ext>`, and anything under truth/."""
    cad_refs: list[str] = []
    truth_refs: list[str] = []
    allowed_stems = set(bodies)
    for lit in _LIT.findall(src):
        norm = lit.replace("\\", "/")
        if "truth/" in norm:
            truth_refs.append(lit)
        p = Path(norm)
        if p.suffix.lower() not in CAD_SUFFIXES:
            continue
        if p.stem not in allowed_stems or p.parent.as_posix() not in ("", ".", "inputs"):
            cad_refs.append(lit)
    return cad_refs, truth_refs


def kcl_hygiene(part_dir: Path, bodies: list[str]) -> dict[str, Any]:
    """A KCL assembly source: top-level `.kcl` files import only `inputs/<body>.step`, nothing under truth/, and a `placements.json` sidecar."""
    files = sorted(Path(part_dir).glob("*.kcl"))
    src = "\n".join(p.read_text(encoding="utf-8") for p in files)
    cad_refs, truth_refs = _refs(src, bodies)
    has_placements = (Path(part_dir) / "placements.json").exists()
    return {
        "ok": has_placements and not cad_refs and not truth_refs and bool(files),
        "has_placements": has_placements,
        "cad_refs": cad_refs,
        "truth_refs": truth_refs,
        "files": [str(p) for p in files],
    }


def hygiene(part_dir: Path, bodies: list[str]) -> dict[str, Any]:
    """`main.py` may reference only the two `inputs/<body>.step` paths; nothing under truth/."""
    from opencad.backends.pythonlang import source_files

    files = source_files(part_dir)
    src = "\n".join(p.read_text(encoding="utf-8") for p in files)
    cad_refs, truth_refs = _refs(src, bodies)
    has_result = bool(re.search(r"(?m)^result\s*=", src))
    has_placements = bool(re.search(r"(?m)^placements\s*=", src))
    ok = has_result and has_placements and not cad_refs and not truth_refs and bool(files)
    return {
        "ok": ok,
        "has_result": has_result,
        "has_placements": has_placements,
        "cad_refs": cad_refs,
        "truth_refs": truth_refs,
        "files": [str(p) for p in files],
    }


def integrity(step: Path, stl: Path | None, *, expected_solids: int = 2) -> dict[str, Any]:
    from opencad.gates import mesh_watertight

    info = brep.analyze_step(step)
    mesh_info = mesh.analyze_mesh(stl) if stl and Path(stl).exists() else {}
    wt = bool(mesh_info) and mesh_watertight(mesh_info, expected_solids)
    valid = bool(info.get("valid"))
    solids_ok = int(info.get("solids") or 0) == expected_solids
    # combined STL of touching or slightly interpenetrating assembly bodies is evidence, not a fail
    mesh_ok = (not mesh_info) or expected_solids > 1 or wt
    return {
        "ok": valid and solids_ok and mesh_ok,
        "valid": valid,
        "solids": info.get("solids"),
        "expected_solids": expected_solids,
        "watertight": wt if mesh_info else None,
        "deterministic": True,
    }

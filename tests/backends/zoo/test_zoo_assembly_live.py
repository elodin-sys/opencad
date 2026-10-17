"""Live check that a KCL assembly source can place staged STEP inputs (`OPENCAD_ZOO_LIVE=1`; hosted calls, billed).

Two staged pump inputs are imported, placed with global elementary rotations and a global translate, exported through
`ZooEngine.build_assembly`, and each exported solid is held to the assembly agreement tolerances against input x placement.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import numpy as np
import pytest

from opencad.paths import REPO_ROOT

INPUTS = REPO_ROOT / "parts" / "zoo" / "peristaltic-pump" / "inputs"
VOLUME_REL_MAX = 1e-4
HAUSDORFF_MAX_MM = 0.05

pytestmark = pytest.mark.skipif(os.environ.get("OPENCAD_ZOO_LIVE") != "1", reason="hosted Zoo calls: set OPENCAD_ZOO_LIVE=1")


def rot(axis: str, deg: float) -> np.ndarray:
    c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
    m = {"x": [[1, 0, 0], [0, c, -s], [0, s, c]], "y": [[c, 0, s], [0, 1, 0], [-s, 0, c]], "z": [[c, -s, 0], [s, c, 0], [0, 0, 1]]}[axis]
    return np.array(m, float)


def placement(rotations: list[tuple[str, float]], t: list[float]) -> np.ndarray:
    r = np.eye(3)
    for axis, deg in rotations:  # applied in order, each about the world axes
        r = rot(axis, deg) @ r
    m = np.eye(4)
    m[:3, :3], m[:3, 3] = r, t
    return m


BODIES = {
    "motorGear": ([("x", -90.0), ("y", 30.0)], [-20.5, 12.0, -20.5]),
    "motor": ([("y", 180.0)], [10.0, 0.0, 5.0]),
}
AXES = {"x": "[1, 0, 0]", "y": "[0, 1, 0]", "z": "[0, 0, 1]"}


def kcl_source() -> str:
    lines = ["@settings(defaultLengthUnit = mm, kclVersion = 2.0)", ""]
    lines += [f'import "inputs/{name}.step" as {name}' for name in BODIES]
    for name, (rotations, t) in BODIES.items():
        lines += ["", name]
        lines += [f"  |> rotate(axis = {AXES[a]}, angle = {deg}deg, global = true)" for a, deg in rotations]
        lines.append(f"  |> translate(xyz = [{t[0]}, {t[1]}, {t[2]}], global = true)")
    return "\n".join(lines) + "\n"


def test_kcl_assembly_places_staged_steps_within_agreement(tmp_path: Path):
    from opencad.assembly.verify import match
    from opencad.backends.zoo.engine import ZooEngine
    from opencad.geomcheck import brep
    from opencad.truth.assembly_agree import _hausdorff
    from opencad.truth.assembly_task import apply

    if not all((INPUTS / f"{n}.step").exists() for n in BODIES):
        pytest.skip(f"staged pump inputs missing under {INPUTS}")
    src = tmp_path / "asm"
    (src / "inputs").mkdir(parents=True)
    for name in BODIES:
        shutil.copy2(INPUTS / f"{name}.step", src / "inputs" / f"{name}.step")
    (src / "main.kcl").write_text(kcl_source(), encoding="utf-8")
    places = {n: placement(*v) for n, v in BODIES.items()}
    (src / "placements.json").write_text(json.dumps({n: m.tolist() for n, m in places.items()}), encoding="utf-8")

    out = tmp_path / "export"
    built = ZooEngine().build_assembly(src / "main.kcl", analyze=False, step=out / "asm.step", stl=out / "asm.stl")
    assert built["step"] and built["stl"] and (out / "placements.json").exists()

    solids = brep.solids(brep.read_step(built["step"]))
    expected = {n: apply(brep.read_step(src / "inputs" / f"{n}.step"), places[n]) for n in BODIES}
    report = {"solids": len(solids)}
    matched = match(solids, expected)
    for name, exp in expected.items():
        got = solids[matched[name]] if name in matched else None
        if got is None:
            report[name] = "no exported solid matched"
            continue
        ev, mv = brep.volume_props(exp)["volume"], brep.volume_props(got)["volume"]
        report[name] = {"volume_rel": abs(mv - ev) / ev, "hausdorff_mm": _hausdorff(got, exp)}
    print(json.dumps(report, indent=2))
    assert len(solids) == len(BODIES), report
    for name in BODIES:
        r = report[name]
        assert isinstance(r, dict), report
        assert r["volume_rel"] <= VOLUME_REL_MAX and r["hausdorff_mm"] <= HAUSDORFF_MAX_MM, report

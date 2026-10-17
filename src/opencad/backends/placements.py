"""Optional `placements` dict from a runner entry: body name → 4×4 row-major millimetre matrix."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def as_matrix(value: Any) -> list[list[float]]:
    """Accept a 4×4 nested list or a flat 16-vector; return a 4×4 of floats."""
    if hasattr(value, "tolist"):
        value = value.tolist()
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"placement matrix must be a 4x4 list, got {type(value).__name__}")
    rows = [list(r) for r in value]
    if len(rows) == 16 and not isinstance(rows[0], (list, tuple)):
        rows = [rows[i : i + 4] for i in range(0, 16, 4)]
    if len(rows) != 4 or any(len(r) != 4 for r in rows):
        raise ValueError(f"placement matrix must be 4x4, got {[len(r) for r in rows]}")
    return [[float(x) for x in row] for row in rows]


def as_placements(obj: Any) -> dict[str, list[list[float]]] | None:
    if obj is None:
        return None
    if not isinstance(obj, dict):
        raise ValueError("placements must be a dict of body name -> 4x4 row-major matrix")
    return {str(k): as_matrix(v) for k, v in obj.items()}


def write_placements(path: Path, placements: dict[str, list[list[float]]]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(placements, indent=2) + "\n", encoding="utf-8")
    return path


def read_placements(path: Path) -> dict[str, list[list[float]]] | None:
    path = Path(path)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return as_placements(data)


def as_joints(obj: Any) -> dict[str, dict[str, list[float]]] | None:
    """Optional `joints` dict: joint name -> {"origin": [x, y, z], "axis": [x, y, z]} in the assembly frame (mm)."""
    if obj is None:
        return None
    if not isinstance(obj, dict):
        raise ValueError("joints must be a dict of joint name -> {origin, axis}")
    out = {}
    for k, v in obj.items():
        if not isinstance(v, dict) or "origin" not in v or "axis" not in v:
            raise ValueError(f"joint {k!r} needs origin and axis")
        out[str(k)] = {"origin": [float(x) for x in list(v["origin"])[:3]], "axis": [float(x) for x in list(v["axis"])[:3]]}
    return out


def read_joints(path: Path) -> dict[str, dict[str, list[float]]] | None:
    path = Path(path)
    return as_joints(json.loads(path.read_text(encoding="utf-8"))) if path.exists() else None


def sidecar(out_dir: Path, payload: dict[str, Any]) -> Path | None:
    """Write `placements.json` (and `joints.json` when declared) beside an export when the runner payload carried them."""
    payload = payload or {}
    if payload.get("joints"):
        path = Path(out_dir) / "joints.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(as_joints(payload["joints"]), indent=2) + "\n", encoding="utf-8")
    raw = payload.get("placements")
    if not raw:
        return None
    return write_placements(Path(out_dir) / "placements.json", as_placements(raw))

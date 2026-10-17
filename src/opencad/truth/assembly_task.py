"""Held-out assembly task (Fusion 360 Gallery joint sets): score a transform manifest against the dataset joint.

Ground truth: each body's `transform` in the joint-set JSON places it in the assembled state (dataset
units cm; the STEP bodies are millimetres). The agent receives both bodies in their local frames and a
joint description, and returns `assembly.yaml` with a 4x4 (or origin + axes) transform per body. We
score the *relative* pose: body one's joint axis must be colinear with body two's (JoinABLe's own
criterion: angle and line distance), the axial offset along the joint axis must match, the bodies must
not interpenetrate, and symmetry-equivalent poses (any rotation about a revolute axis) are accepted.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf

from opencad.geomcheck import assembly, brep

CM = 10.0


def _vec(d: dict[str, Any]) -> np.ndarray:
    return np.array([d["x"], d["y"], d["z"]], float)


def transform_matrix(t: dict[str, Any] | None, scale: float = CM) -> np.ndarray:
    """4x4 from the dataset transform {origin, x_axis, y_axis, z_axis} (cm origin -> mm)."""
    m = np.eye(4)
    if not t:
        return m
    m[:3, 0] = _vec(t["x_axis"])
    m[:3, 1] = _vec(t["y_axis"])
    m[:3, 2] = _vec(t["z_axis"])
    m[:3, 3] = _vec(t["origin"]) * scale
    return m


def manifest_matrix(entry: dict[str, Any]) -> np.ndarray:
    """Agent transform: {matrix: 4x4} or {origin: [..], x_axis: [..], y_axis: [..], z_axis: [..]} in mm."""
    if "matrix" in entry:
        m = np.asarray(entry["matrix"], float)
        assert m.shape == (4, 4)
        return m
    m = np.eye(4)
    for i, k in enumerate(("x_axis", "y_axis", "z_axis")):
        v = np.asarray(entry.get(k, np.eye(3)[i]), float)
        m[:3, i] = v / np.linalg.norm(v)
    m[:3, 3] = np.asarray(entry.get("origin", [0, 0, 0]), float)
    return m


def apply(shape, m: np.ndarray):
    t = gp_Trsf()
    t.SetValues(*[float(m[i, j]) for i in range(3) for j in range(4)])
    return BRepBuilderAPI_Transform(shape, t, True).Shape()


def axis_assembled(js_side: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """The joint axis line as stored: assembled coordinates (cm -> mm)."""
    al = js_side["axis_line"]
    d = _vec(al["direction"])
    return _vec(al["origin"]) * CM, d / np.linalg.norm(d)


def transform_line(o: np.ndarray, d: np.ndarray, m: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ow = m[:3, :3] @ o + m[:3, 3]
    dw = m[:3, :3] @ d
    return ow, dw / np.linalg.norm(dw)


def truth_poses(joint_set: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Local -> assembled transform of each body (the STEP bodies are in their local frames)."""
    j = joint_set["joints"][0]
    return transform_matrix(j["geometry_or_origin_one"].get("transform")), transform_matrix(j["geometry_or_origin_two"].get("transform"))


def relative(m1: np.ndarray, m2: np.ndarray) -> np.ndarray:
    """Pose of body one in body two's frame."""
    return np.linalg.inv(m2) @ m1


def score(joint_set_path: Path, body_steps: dict[str, Path], manifest_path: Path, *, angle_tol_deg: float = 2.0, axis_tol: float = 0.5,
          offset_tol: float = 0.5, interference_tol: float = 1.0) -> dict[str, Any]:
    js = json.loads(Path(joint_set_path).read_text())
    j = js["joints"][0]
    b1, b2 = js["body_one"], js["body_two"]
    man = yaml.safe_load(Path(manifest_path).read_text()) or {}
    bodies = man.get("bodies") or man
    if b1 not in bodies or b2 not in bodies:
        return {"ok": False, "error": f"assembly manifest must place both bodies {b1} and {b2}", "found": sorted(bodies)}
    a1, a2 = manifest_matrix(bodies[b1]), manifest_matrix(bodies[b2])
    t1, t2 = truth_poses(js)
    # The agent's relative motion of body one expressed in assembled coordinates: identity when the agent reproduces the truth.
    # Comparing relative to body two makes a rigid motion of the whole assembly irrelevant.
    motion = t2 @ np.linalg.inv(a2) @ a1 @ np.linalg.inv(t1)
    o1, d1 = axis_assembled(j["geometry_or_origin_one"])
    o2, d2 = axis_assembled(j["geometry_or_origin_two"])
    o1a, d1a = transform_line(o1, d1, motion)
    ang = math.degrees(math.acos(min(1.0, abs(float(np.dot(d1a, d2))))))
    w = o1a - o2
    line_dist = float(np.linalg.norm(w - np.dot(w, d2) * d2))
    axial_agent = float(np.dot(o1a - o2, d2))
    axial_truth = float(np.dot(o1 - o2, d2))
    checks = {
        "axis_angle_deg": {"measured": ang, "max": angle_tol_deg, "ok": ang <= angle_tol_deg},
        "axis_line_distance": {"measured": line_dist, "max": axis_tol, "ok": line_dist <= axis_tol},
        "axial_offset": {"measured": axial_agent, "expected": axial_truth, "max_error": offset_tol, "ok": abs(axial_agent - axial_truth) <= offset_tol},
    }
    checks["residual_rotation_deg"] = {"measured": math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(motion[:3, :3]) - 1) / 2)))),
                                       "note": "rotation about a revolute axis is free; any value passes if the axis checks pass"}
    # interference in the agent's assembled state (both bodies placed by the agent's transforms), judged against the
    # dataset's own assembled state: reference assemblies are not guaranteed interference-free
    raw1, raw2 = brep.read_step(body_steps[b1]), brep.read_step(body_steps[b2])
    truth_inter = assembly.common_volume(apply(raw1, t1), apply(raw2, t2))
    s1, s2 = apply(raw1, a1), apply(raw2, a2)
    inter = assembly.common_volume(s1, s2)
    allowed = max(interference_tol, truth_inter + interference_tol)
    gap = assembly.min_distance(s1, s2) if inter <= allowed else 0.0
    checks["no_interference"] = {"interference_volume": inter, "truth_interference": truth_inter, "max": allowed, "ok": inter <= allowed}
    checks["contact_or_near"] = {"gap": gap, "max": 1.0, "ok": gap <= 1.0, "note": "the mated bodies touch or nearly touch"}
    out = {"joint_type": j["joint_motion"]["joint_type"], "flipped_truth": j.get("is_flipped"), "offset_truth_mm": (j.get("offset") or {}).get("value", 0.0) * CM,
           "checks": checks, "ok": all(c.get("ok", True) for c in checks.values())}
    return out


def truth_manifest(joint_set: dict[str, Any]) -> dict[str, Any]:
    """The dataset's own assembled placement as an assembly manifest (evaluator-side; proves the scorer accepts the truth)."""
    t1, t2 = truth_poses(joint_set)
    return {"bodies": {joint_set["body_one"]: {"matrix": t1.tolist()}, joint_set["body_two"]: {"matrix": t2.tolist()}}}

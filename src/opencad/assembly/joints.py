"""Joint graph math: joint frames in the assembly frame, joint fidelity of a placement, forward kinematics, transmissions and
closed loops.

A body's pose at joint values q is M_b(q) = D_1(q_1) ... D_k(q_k) M_b, where D_i is joint i's motion about (or along) its
rest axis in the assembly frame, applied from the datum outward along the body's joint chain (tree joints only). Closure
joints and epicyclic transmissions make the joint values the solution of a constraint system (`solve`); a pure tree with
plain transmissions keeps the exact propagation driven = ratio x driver.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from opencad.schemas import AssemblyContract, Joint, JointFrame

MAX_STEP = 2.0  # deg or mm per continuation step: a loop solved from its last pose stays on the branch it was assembled in


def unit(v: Any) -> np.ndarray:
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n else v


def frame_world(frame: JointFrame, m: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    o = m[:3, :3] @ np.asarray(frame.origin, float) + m[:3, 3]
    a = unit(m[:3, :3] @ np.asarray(frame.axis, float))
    r = unit(m[:3, :3] @ np.asarray(frame.ref, float)) if frame.ref is not None else None
    return o, a, r


def signed_angle(u: np.ndarray, v: np.ndarray, axis: np.ndarray) -> float:
    """Angle from u to v about axis, deg in (-180, 180]; both projected onto the plane normal to axis."""
    u = unit(u - np.dot(u, axis) * axis)
    v = unit(v - np.dot(v, axis) * axis)
    return math.degrees(math.atan2(float(np.dot(np.cross(u, v), axis)), float(np.dot(u, v))))


def _wrap(deg: float) -> float:
    return (deg + 180.0) % 360.0 - 180.0


MESH_RADIAL_FRACTION = 0.2  # of a mesh's backlash_max: how far off its axis a meshed gear may sit


def mesh_bounds(a: AssemblyContract) -> dict[str, float]:
    """Radial bound of every rotating joint a checked gear mesh couples: a gear placed off its axis spins eccentrically, trading its
    backlash for clearance, so it sits within a fifth of the mesh's backlash_max (or its own position_tolerance, if tighter)."""
    out: dict[str, float] = {}
    for t in a.transmissions:
        for name in (t.driver, t.driven) if t.mesh is not None else ():
            j = a.joint(name)
            if j.kind in ("revolute", "cylindrical"):
                out[name] = min(out.get(name, j.position_tolerance), MESH_RADIAL_FRACTION * t.mesh.backlash_max)
    return out


def fidelity(j: Joint, mp: np.ndarray, mc: np.ndarray, radial_max: float | None = None) -> dict[str, Any]:
    """How far a placement puts the child's joint frame from the parent's, per the joint kind's constraints; `radial_max` tightens the
    radial bound (a meshed gear, `mesh_bounds`)."""
    op, ap, rp = frame_world(j.parent_frame, mp)
    oc, ac, rc = frame_world(j.child_frame, mc)
    target = -ac if j.flip else ac
    axis_angle = math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(ap, target))))))
    w = oc - op
    axial = float(np.dot(w, ap))
    radial = float(np.linalg.norm(w - axial * ap))
    checks: dict[str, dict[str, Any]] = {}
    if j.kind != "ball":
        checks["axis_angle_deg"] = {"measured": axis_angle, "max": j.angle_tolerance_deg, "ok": axis_angle <= j.angle_tolerance_deg}
    if j.kind in ("rigid", "revolute", "ball", "slider", "cylindrical"):
        r_max = min(j.position_tolerance, radial_max) if radial_max is not None else j.position_tolerance
        checks["radial_mm"] = {"measured": radial, "max": r_max, "ok": radial <= r_max,
                               **({"note": f"gear mesh: {MESH_RADIAL_FRACTION:g} x backlash_max"} if r_max < j.position_tolerance else {})}
    if j.kind in ("rigid", "revolute", "ball", "planar", "slider", "cylindrical"):
        checks["axial_mm"] = {"measured": axial, "expected": j.offset, "max_error": j.position_tolerance, "ok": abs(axial - j.offset) <= j.position_tolerance}
    if rp is not None and rc is not None and j.kind in ("rigid", "revolute", "cylindrical"):
        rest = signed_angle(rp, rc, ap)
        err = abs(_wrap(rest - j.angle))
        checks["rest_angle_deg"] = {"measured": rest, "expected": j.angle, "max_error": j.angle_tolerance_deg, "ok": err <= j.angle_tolerance_deg}
    return {
        "kind": j.kind, "parent": j.parent, "child": j.child, "ok": all(c["ok"] for c in checks.values()), "checks": checks,
        "parent_origin": op.round(6).tolist(), "parent_axis": ap.round(9).tolist(), "child_origin": oc.round(6).tolist(),
        "child_axis": ac.round(9).tolist(),
    }


def world_axes(a: AssemblyContract, placements: dict[str, np.ndarray]) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Each joint's rest axis in the assembly frame, on the parent side (the motion axis)."""
    out = {}
    for j in a.joints:
        o, ax, _ = frame_world(j.parent_frame, placements[j.parent])
        out[j.name] = (o, ax)
    return out


def motion(j: Joint, axis: tuple[np.ndarray, np.ndarray], q: float) -> np.ndarray:
    """4x4 rigid motion of joint j's child subtree for joint value q (deg for rotations, mm for translations)."""
    o, ax = axis
    m = np.eye(4)
    if j.kind in ("revolute", "cylindrical", "ball"):
        r = _rotation(ax, math.radians(q))
        m[:3, :3] = r
        m[:3, 3] = o - r @ o
    elif j.kind == "slider":
        m[:3, 3] = ax * q
    elif j.kind == "planar":
        perp = unit(np.cross(ax, [1.0, 0.0, 0.0]) if abs(ax[0]) < 0.9 else np.cross(ax, [0.0, 1.0, 0.0]))
        m[:3, 3] = perp * q
    return m


def _rotation(axis: np.ndarray, theta: float) -> np.ndarray:
    x, y, z = unit(axis)
    c, s, t = math.cos(theta), math.sin(theta), 1 - math.cos(theta)
    return np.array([[t * x * x + c, t * x * y - s * z, t * x * z + s * y],
                     [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
                     [t * x * z - s * y, t * y * z + s * x, t * z * z + c]])


def chain(a: AssemblyContract, body: str) -> list[Joint]:
    """Tree joints from the datum part out to `body`."""
    by_child = {j.child: j for j in a.joints if not j.closure}
    out: list[Joint] = []
    cur = body
    while cur in by_child:
        j = by_child[cur]
        out.append(j)
        cur = j.parent
    return out[::-1]


def tree_joint(a: AssemblyContract, body: str) -> Joint | None:
    return next((j for j in a.joints if j.child == body and not j.closure), None)


def loop_joints(a: AssemblyContract, closure: Joint) -> list[str]:
    """The moving tree joints of the loop a closure joint closes: those on one body's chain but not the other's."""
    pa, pc = {j.name for j in chain(a, closure.parent)}, {j.name for j in chain(a, closure.child)}
    return [j.name for j in a.joints if j.name in pa ^ pc and j.kind != "rigid"]


def propagate(a: AssemblyContract, drive: str, q: float) -> dict[str, float]:
    """Joint values when `drive` is at q: transmissions carry the motion (driven = ratio x driver), everything else rests."""
    values = {j.name: 0.0 for j in a.joints}
    values[drive] = q
    frontier = [drive]
    while frontier:
        cur = frontier.pop()
        for t in a.transmissions:
            if t.driver == cur:
                values[t.driven] = t.ratio * values[cur]
                frontier.append(t.driven)
    return values


def is_tree(a: AssemblyContract) -> bool:
    """No closure joint and no epicyclic mesh: joint values follow by propagation alone."""
    return not any(j.closure for j in a.joints) and not any(t.carrier for t in a.transmissions)


def unknowns(a: AssemblyContract, fixed: dict[str, float]) -> list[str]:
    """Joints a solve determines: loop joints, transmission-driven joints, carriers and the members of epicyclic meshes, less
    the held ones. A joint nothing constrains rests, as in propagation."""
    kinds = {j.name: j.kind for j in a.joints}
    names = {n for j in a.joints if j.closure for n in loop_joints(a, j)}
    for t in a.transmissions:
        names |= {t.driven, *([t.carrier, t.driver] if t.carrier else [])}
    return [j.name for j in a.joints if j.name in names and j.name not in fixed and kinds[j.name] != "rigid" and not j.closure]


def closure_residual(j: Joint, mp: np.ndarray, mc: np.ndarray) -> tuple[np.ndarray, float, float]:
    """Constraint residual of a closure joint between its bodies' poses: (vector, position error mm, axis error deg)."""
    op, ap, rp = frame_world(j.parent_frame, mp)
    oc, ac, rc = frame_world(j.child_frame, mc)
    target = -ac if j.flip else ac
    w = oc - op
    if j.kind in ("slider", "cylindrical"):
        pos = w - float(w @ ap) * ap
    elif j.kind == "planar":
        pos = np.array([float(w @ ap) - j.offset])
    else:
        pos = w - j.offset * ap
    axis = np.cross(ap, target) if j.kind != "ball" else np.zeros(3)
    parts = [pos, axis]
    if j.kind == "slider" and rp is not None and rc is not None:  # a slider also locks the rotation about its axis
        parts.append(np.array([math.radians(_wrap(signed_angle(rp, rc, ap) - j.angle))]))
    axis_deg = math.degrees(math.asin(min(1.0, float(np.linalg.norm(axis)))))
    return np.concatenate(parts), float(np.linalg.norm(pos)), axis_deg


def _signs(a: AssemblyContract, placements: dict[str, np.ndarray]) -> dict[tuple[str, str], float]:
    """Sense of each carrier transmission member's axis against its carrier's axis (+1 parallel, -1 anti-parallel)."""
    axes = world_axes(a, placements)
    return {(t.name, n): (1.0 if float(np.dot(axes[n][1], axes[t.carrier][1])) >= 0 else -1.0)
            for t in a.transmissions if t.carrier for n in (t.driver, t.driven)}


def _relative(t: Any, name: str, values: dict[str, float], chains: dict[str, set[str]], signs: dict[tuple[str, str], float]) -> float:
    """A transmission member's displacement relative to its carrier (a joint mounted on the carrier already moves with it)."""
    v = values.get(name, 0.0)
    if t.carrier is None or t.carrier in chains[name]:
        return v
    return v - signs[(t.name, name)] * values.get(t.carrier, 0.0)


def solve(a: AssemblyContract, placements: dict[str, np.ndarray], fixed: dict[str, float], guess: dict[str, float] | None = None) -> tuple[dict[str, float], dict[str, Any]]:
    """Joint values with the `fixed` joints held: transmissions carry the motion and closure joints stay closed. Returns the
    values and {closure_mm, closure_deg, residual, free, ok}: `free` lists joints the held ones leave undetermined."""
    rigid = {j.name for j in a.joints if j.kind == "rigid"}
    if is_tree(a):
        values = {j.name: 0.0 for j in a.joints}
        for d, q in fixed.items():
            for n, v in propagate(a, d, q).items():
                values[n] += v
        return values, {"closure_mm": 0.0, "closure_deg": 0.0, "residual": 0.0, "free": [], "ok": True}
    from scipy.optimize import least_squares

    names = unknowns(a, fixed)
    base = {j.name: 0.0 for j in a.joints} | {n: v for n, v in (guess or {}).items() if n not in rigid} | fixed
    closures = [j for j in a.joints if j.closure]
    chains = {j.name: {c.name for c in chain(a, j.child)} for j in a.joints}
    signs = _signs(a, placements)

    def values_of(x: np.ndarray) -> dict[str, float]:
        return base | dict(zip(names, (float(v) for v in x)))

    def residual(x: np.ndarray) -> np.ndarray:
        v = values_of(x)
        out = [np.array([_relative(t, t.driven, v, chains, signs) - t.ratio * _relative(t, t.driver, v, chains, signs) for t in a.transmissions])]
        if closures:
            ps = poses(a, placements, v)
            out += [closure_residual(j, ps[j.parent], ps[j.child])[0] for j in closures]
        return np.concatenate(out)

    x0 = np.array([base[n] for n in names], float)
    if names:
        m = len(residual(x0))
        sol = least_squares(residual, x0, method="lm" if m >= len(names) else "trf", xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=200 * (len(names) + 1))
        x, jac = sol.x, np.atleast_2d(sol.jac)
        sv = np.linalg.svd(jac, compute_uv=False) if jac.size else np.zeros(0)
        rank = int(np.sum(sv > 1e-9 * max(1.0, float(sv.max(initial=0.0)))))
        free = []
        if rank < len(names):
            null = np.linalg.svd(jac)[2][rank:]
            free = [n for k, n in enumerate(names) if float(np.max(np.abs(null[:, k]))) > 1e-6]
    else:
        x, free = x0, []
    values = values_of(x)
    ps = poses(a, placements, values) if closures else {}
    worst_mm = worst_deg = 0.0
    ok = not free
    for j in closures:
        _, e_mm, e_deg = closure_residual(j, ps[j.parent], ps[j.child])
        worst_mm, worst_deg = max(worst_mm, e_mm), max(worst_deg, e_deg)
        ok = ok and e_mm <= j.position_tolerance and e_deg <= j.angle_tolerance_deg
    trans = float(np.max(np.abs(residual(x)[:len(a.transmissions)]), initial=0.0)) if names else 0.0
    ok = ok and trans <= 1e-6
    return values, {"closure_mm": worst_mm, "closure_deg": worst_deg, "residual": trans, "free": free, "ok": ok}


def solve_path(a: AssemblyContract, placements: dict[str, np.ndarray], targets: list[dict[str, float]], max_step: float = MAX_STEP) -> list[tuple[dict[str, float], dict[str, Any]]]:
    """Solve at each target in turn, from rest, in steps of at most `max_step` so a loop keeps its assembled branch."""
    out: list[tuple[dict[str, float], dict[str, Any]]] = []
    prev: dict[str, float] = {}
    cur: dict[str, float] | None = None
    tree = is_tree(a)
    for target in targets:
        keys = set(prev) | set(target)
        span = max((abs(target.get(k, 0.0) - prev.get(k, 0.0)) for k in keys), default=0.0)
        n = 1 if tree else max(1, math.ceil(span / max_step))
        for s in range(1, n + 1):
            f = s / n
            cur, info = solve(a, placements, {k: prev.get(k, 0.0) + (target.get(k, 0.0) - prev.get(k, 0.0)) * f for k in keys}, cur)
        out.append((cur, info))
        prev = target
    return out


def displacement(a: AssemblyContract, placements: dict[str, np.ndarray], values: dict[str, float], joint: str) -> float:
    """A joint's displacement from rest: its value for a tree joint; for a closure joint, the child's motion relative to the
    parent measured from the two bodies' poses (deg about, or mm along, the parent axis)."""
    j = a.joint(joint)
    if not j.closure:
        return float(values.get(joint, 0.0))
    ps = poses(a, placements, values)
    op, ap, _ = frame_world(j.parent_frame, ps[j.parent])
    oc, _, _ = frame_world(j.child_frame, ps[j.child])
    if j.kind in ("slider", "planar"):
        rest_op, rest_ap, _ = frame_world(j.parent_frame, placements[j.parent])
        rest_oc, _, _ = frame_world(j.child_frame, placements[j.child])
        return float((oc - op) @ ap) - float((rest_oc - rest_op) @ rest_ap)
    _, rest_ap, _ = frame_world(j.parent_frame, placements[j.parent])
    u = np.cross(rest_ap, [1.0, 0.0, 0.0])
    u = unit(u if np.linalg.norm(u) > 1e-6 else np.cross(rest_ap, [0.0, 1.0, 0.0]))
    dp = ps[j.parent][:3, :3] @ placements[j.parent][:3, :3].T
    dc = ps[j.child][:3, :3] @ placements[j.child][:3, :3].T
    return signed_angle(dp @ u, dc @ u, ap)


def poses(a: AssemblyContract, placements: dict[str, np.ndarray], values: dict[str, float]) -> dict[str, np.ndarray]:
    axes = world_axes(a, placements)
    joints = {j.name: j for j in a.joints}
    out = {}
    for p in a.parts:
        if not p.placed:
            continue
        m = np.eye(4)
        for j in chain(a, p.name):
            m = m @ motion(joints[j.name], axes[j.name], values.get(j.name, 0.0))
        out[p.name] = m @ placements[p.name]
    return out


def moving_pairs(a: AssemblyContract, placements: dict[str, np.ndarray], samples: list[dict[str, float]]) -> list[tuple[str, str]]:
    """Body pairs whose relative pose changes across the sampled joint values (fluid bodies excluded: they are rest-pose regions)."""
    names = [p.name for p in a.parts if p.placed and p.role != "fluid"]
    rel: dict[tuple[str, str], list[np.ndarray]] = {}
    for v in samples:
        ps = poses(a, placements, v)
        for i, x in enumerate(names):
            for y in names[i + 1:]:
                rel.setdefault((x, y), []).append(np.linalg.inv(ps[x]) @ ps[y])
    return [k for k, ms in rel.items() if any(not np.allclose(ms[0], m, atol=1e-9) for m in ms[1:])]

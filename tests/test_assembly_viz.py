"""The animated GLB: a viewer's interpolation between keyframes follows the forward kinematics, and the default file has one clip."""

from types import SimpleNamespace

import numpy as np
import trimesh
from pygltflib import GLTF2

from opencad.assembly import joints as jm
from opencad.assembly import viz
from opencad.schemas import AssemblyContract

BOXES = {"base": ([0, -5, 0], [120, 5, 2]), "arm": ([50, -3, 2], [110, 3, 4]), "tip": ([95, -2, 4], [125, 2, 6])}
RIG = {
    "name": "t-rig",
    "intent": "an arm turning on a base about an axis 60 mm off the origin, and a tip turning on the arm",
    "frame": {"origin": "base corner", "axes": {"x": "length", "y": "width", "z": "up"}},
    "envelope": {"min": [-10.0, -80.0, 0.0], "max": [170.0, 80.0, 6.0], "tolerance": 0.05},
    "datum_part": "base",
    "parts": [{"name": n, "kind": "purchased", "catalog": {"name": n, "kind": "box", "min": lo, "max": hi}} for n, (lo, hi) in BOXES.items()],
    "joints": [
        {"name": "armSpin", "kind": "revolute", "parent": "base", "child": "arm", "parent_frame": {"origin": [60.0, 0.0, 2.0]},
         "child_frame": {"origin": [60.0, 0.0, 2.0]}, "drive": {"kind": "motor", "speed": 10.0}},
        {"name": "tipSpin", "kind": "revolute", "parent": "arm", "child": "tip", "parent_frame": {"origin": [100.0, 0.0, 4.0]},
         "child_frame": {"origin": [100.0, 0.0, 4.0]}, "drive": {"kind": "motor", "speed": 30.0}},
    ],
    "acceptance": {"motions": [{"name": "swing", "drive": "armSpin", "range": [0.0, 90.0], "steps": 4}]},
}


def _read(g, blob, acc):
    a = g.accessors[acc]
    bv = g.bufferViews[a.bufferView]
    n = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[a.type]
    return np.frombuffer(blob, np.float32, a.count * n, (bv.byteOffset or 0) + (a.byteOffset or 0)).reshape(a.count, n).astype(float)


def _slerp(q0, q1, u):
    d = float(np.dot(q0, q1))
    if d > 0.9995:
        q = q0 + u * (q1 - q0)
        return q / np.linalg.norm(q)
    th = np.arccos(np.clip(d, -1.0, 1.0))
    return (np.sin((1 - u) * th) * q0 + np.sin(u * th) * q1) / np.sin(th)


def _world(g, blob, anim, name, t):
    """World matrix of node `name` at time t, sampling the animation as a viewer does (lerp translations, slerp rotations)."""
    parent = {c: i for i, n in enumerate(g.nodes) for c in (n.children or [])}
    sampled = {}
    for ch in anim.channels:
        s = anim.samplers[ch.sampler]
        ts, vs = _read(g, blob, s.input)[:, 0], _read(g, blob, s.output)
        k = int(min(np.searchsorted(ts, t, side="right") - 1, len(ts) - 2))
        u = (t - ts[k]) / (ts[k + 1] - ts[k])
        sampled[(ch.target.node, ch.target.path)] = _slerp(vs[k], vs[k + 1], u) if ch.target.path == "rotation" else vs[k] + u * (vs[k + 1] - vs[k])

    def local(i):
        n = g.nodes[i]
        if n.matrix is not None:
            return np.asarray(n.matrix, float).reshape(4, 4).T
        tr = sampled.get((i, "translation"), n.translation or [0.0, 0.0, 0.0])
        x, y, z, w = sampled.get((i, "rotation"), n.rotation or [0.0, 0.0, 0.0, 1.0])
        m = trimesh.transformations.quaternion_matrix([w, x, y, z])
        m[:3, 3] = tr
        return m

    i = next(k for k, n in enumerate(g.nodes) if n.name == name)
    m = np.eye(4)
    while i is not None:
        m = local(i) @ m
        i = parent.get(i)
    return m


def test_interpolated_frames_follow_the_kinematics_and_the_default_file_has_one_clip(tmp_path):
    contract = AssemblyContract.model_validate(RIG)
    placements = {n: np.eye(4) for n in BOXES}
    scene = trimesh.Scene()
    scene.graph.update(frame_to="root", frame_from=scene.graph.base_frame, matrix=viz.ZUP_MM_TO_YUP_M)
    for n, (lo, hi) in BOXES.items():
        scene.add_geometry(trimesh.creation.box(bounds=[lo, hi]), node_name=f"body:{n}", geom_name=f"body:{n}", parent_node_name="root")
    actx = SimpleNamespace(contract=contract)
    values = viz.clip_values(actx, placements)
    values["explode"] = [{} for _ in range(viz.KEYFRAMES)]
    one, full = tmp_path / "assembly.glb", tmp_path / "assembly-clips.glb"
    data = scene.export(file_type="glb")
    for path, clips in ((one, {"operate": values["operate"]}), (full, values)):
        path.write_bytes(data)
        viz.rig(path, contract, placements, clips, viz.explode_offsets(actx, {}))
    assert [a.name for a in GLTF2().load(str(one)).animations] == ["operate"]
    g = GLTF2().load(str(full))
    assert {a.name for a in g.animations} == {"drive:swing", "operate", "explode"}
    blob = g.binary_blob()
    times = np.linspace(0.0, viz.CLIP_S, viz.KEYFRAMES)
    corners = {n: np.array([[x, y, z, 1.0] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) for n, (lo, hi) in BOXES.items()}
    for clip in ("operate", "drive:swing"):
        anim = next(a for a in g.animations if a.name == clip)
        for k in (3, 17, 42):
            t = 0.5 * (times[k] + times[k + 1])  # between keyframes, where a translated-rotation track drifts off the axis
            q = {j: 0.5 * (values[clip][k].get(j, 0.0) + values[clip][k + 1].get(j, 0.0)) for j in ("armSpin", "tipSpin")}
            poses = jm.poses(contract, placements, q)
            for n in BOXES:
                got = (_world(g, blob, anim, f"body:{n}", t) @ corners[n].T).T
                want = (viz.ZUP_MM_TO_YUP_M @ poses[n] @ corners[n].T).T
                assert np.abs(got - want).max() < 1e-6, (clip, k, n, np.abs(got - want).max())

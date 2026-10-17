"""Assembly visuals: `assembly.glb` with the single `operate` clip (every motor drive at its relative speed), `assembly-clips.glb`
with every clip (one per motion sweep, `operate`, `explode`) for the model-viewer page's clip selector. Poses come from forward
kinematics over the measured placements; visuals never change a verdict.

Each body hangs under one pivot node per moving joint of its chain (the kinematic tree), so a clip animates joint rotations about
their own axes and a viewer's interpolation between keyframes stays on the joint's arc. Clips on the same nodes blend in viewers
that play every animation at once, which is why the default file carries one clip."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

from opencad.assembly import AsmCtx
from opencad.assembly import joints as jm

PALETTE = ((205, 70, 60), (60, 120, 220), (240, 170, 40), (80, 170, 90), (150, 90, 200), (40, 170, 180), (200, 110, 150), (120, 120, 120))
FLUID_RGBA = (90, 160, 240, 60)
CLIP_S = 6.0
KEYFRAMES = 61
EXPLODE = 1.2
ZUP_MM_TO_YUP_M = np.array([[1e-3, 0, 0, 0], [0, 0, 1e-3, 0], [0, -1e-3, 0, 0], [0, 0, 0, 1]])
MODEL_VIEWER_CDN = "https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js"


def _speed(j: Any, case: Any) -> float:
    """deg/s (rotation) or mm/s (translation) at the reference case; 1 when the drive states none."""
    d = j.drive
    s = d.speed if d.speed is not None else (case.values.get(d.case_value) if case is not None and d.case_value else None)
    if s is None and d.history:
        s = max(abs(v) for _, v in d.history)
    s = 1.0 if s is None else float(s)
    return s * 6.0 if j.rotates else s


def _history_shape(j: Any, t: np.ndarray) -> np.ndarray:
    """Normalised displacement (0..1 over the clip) for a speed history; linear for a constant speed."""
    h = j.drive.history
    if not h:
        return t / t[-1]
    ht = np.array([p[0] for p in h], float)
    hv = np.array([p[1] for p in h], float)
    tau = ht[0] + (ht[-1] - ht[0]) * t / t[-1]
    v = np.interp(tau, ht, hv)
    disp = np.concatenate([[0.0], np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(tau))])
    return disp / (disp[-1] or 1.0)


def clip_values(actx: AsmCtx, placements: dict[str, np.ndarray]) -> dict[str, list[dict[str, float]]]:
    """Joint values per keyframe for every clip (the explode clip is handled separately); closed loops are solved per keyframe."""
    a = actx.contract
    t = np.linspace(0.0, CLIP_S, KEYFRAMES)
    clips: dict[str, list[dict[str, float]]] = {}
    for m in a.acceptance.motions:
        j = a.joint(m.drive)
        span = m.range[1] - m.range[0]
        full = j.rotates and abs(span) >= 359.999
        phase = t / CLIP_S if full else 0.5 - 0.5 * np.cos(2 * math.pi * t / CLIP_S)
        clips[f"drive:{m.name}"] = [v for v, _ in jm.solve_path(a, placements, [{m.drive: m.range[0] + span * float(p)} for p in phase])]
    motors = [j for j in a.joints if j.drive is not None and j.drive.kind == "motor"]
    if motors:
        case = next((c for c in a.operating_cases if c.split == "development"), a.operating_cases[0] if a.operating_cases else None)
        speeds = {j.name: _speed(j, case) for j in motors}
        fastest = max(abs(v) for v in speeds.values()) or 1.0
        shapes = {j.name: (720.0 if j.rotates else 50.0) * speeds[j.name] / fastest * _history_shape(j, t) for j in motors}
        clips["operate"] = [v for v, _ in jm.solve_path(a, placements, [{n: float(s[k]) for n, s in shapes.items()} for k in range(len(t))])]
    return clips


def _quat(r: np.ndarray) -> list[float]:
    m = np.eye(4)
    m[:3, :3] = r
    w, x, y, z = trimesh.transformations.quaternion_from_matrix(m)
    return [x, y, z, w]


def explode_offsets(actx: AsmCtx, coms: dict[str, np.ndarray]) -> dict[str, list[np.ndarray]]:
    """body -> translation per keyframe (mm) away from the assembly's centre of mass; the datum stays."""
    centre = np.mean([c for c in coms.values()], axis=0) if coms else np.zeros(3)
    t = np.linspace(0.0, CLIP_S, KEYFRAMES)
    phase = 0.5 - 0.5 * np.cos(2 * math.pi * t / CLIP_S)
    out = {}
    for p in actx.contract.parts:
        if p.placed:
            d = np.zeros(3) if p.name == actx.contract.datum_part else (coms.get(p.name, centre) - centre) * EXPLODE
            out[p.name] = [d * f for f in phase]
    return out


def build_scene(actx: AsmCtx) -> tuple[trimesh.Scene, dict[str, np.ndarray], dict[str, np.ndarray]]:
    from opencad.backends.placements import read_placements
    from opencad.geomcheck import brep
    from opencad.truth.assembly_viz import _paint, tessellate

    raw = read_placements(actx.results_dir / "export" / "placements.json") or {}
    placements = {k: np.asarray(v, float) for k, v in raw.items()}
    scene = trimesh.Scene()
    scene.graph.update(frame_to="root", frame_from=scene.graph.base_frame, matrix=ZUP_MM_TO_YUP_M)
    coms = {}
    for i, p in enumerate(actx.contract.parts):
        placements.setdefault(p.name, np.eye(4))
        f = actx.placed_step(p.name)
        if not f.exists():
            continue
        m = tessellate(f, deflection=0.05)
        rgba = FLUID_RGBA if p.role == "fluid" else (*PALETTE[i % len(PALETTE)], 255)
        _paint(m, rgba, f"body:{p.name}")
        scene.add_geometry(m, node_name=f"body:{p.name}", geom_name=f"body:{p.name}", parent_node_name="root")
        coms[p.name] = np.asarray(brep.volume_props(brep.read_step(f))["center_of_mass"])
    return scene, placements, coms


def rig(glb: Path, contract: Any, placements: dict[str, np.ndarray], clips: dict[str, list[dict[str, float]]],
        explode: dict[str, list[np.ndarray]] | None = None) -> None:
    """Re-parent each body mesh under its moving joints and write one animation per clip (joint values per keyframe).

    root > joint:<path> (pivot on the joint's rest origin; animated rotation about, or translation along, its rest axis)
    > offset:<path> (minus that origin) > ... > explode:<body> > body:<body> (the mesh at rest, assembly frame, mm). Pivot then
    offset is the joint's motion D_j, and nesting them along the chain composes D_1 ... D_k as the forward kinematics do. Every
    clip keys every pivot and explode node, so switching clips never leaves a node where the last clip put it."""
    from pygltflib import (
        ANIM_LINEAR,
        FLOAT,
        GLTF2,
        SCALAR,
        VEC3,
        VEC4,
        Accessor,
        Animation,
        AnimationChannel,
        AnimationChannelTarget,
        AnimationSampler,
        BufferView,
        Node,
    )

    axes = jm.world_axes(contract, placements)
    g = GLTF2().load(str(glb))
    root = next(i for i, n in enumerate(g.nodes) if n.name == "root")
    bodies = {n.name[len("body:"):]: i for i, n in enumerate(g.nodes) if n.name and n.name.startswith("body:")}
    for i in bodies.values():
        n = g.nodes[i]
        n.matrix, n.translation, n.rotation, n.scale = None, None, None, None
        for prim in g.meshes[n.mesh].primitives if n.mesh is not None else []:
            if prim.material is not None:
                g.materials[prim.material].name = n.name

    def add(name: str, translation: Any, children: list[int] | None = None) -> int:
        g.nodes.append(Node(name=name, translation=[float(x) for x in translation], children=children or []))
        return len(g.nodes) - 1

    g.nodes[root].children = []
    pivots: dict[int, Any] = {}
    under: dict[tuple[str, ...], int] = {}
    shifts: dict[int, str] = {}
    for body, bi in bodies.items():
        parent, path = root, ()
        for j in jm.chain(contract, body):
            if j.kind == "rigid":
                continue
            path = (*path, j.name)
            if path not in under:
                o = axes[j.name][0]
                piv = add("joint:" + ">".join(path), o)
                off = add("offset:" + ">".join(path), -o)
                g.nodes[piv].children.append(off)
                g.nodes[parent].children.append(piv)
                under[path], pivots[piv] = off, j
            parent = under[path]
        ex = add(f"explode:{body}", [0.0, 0.0, 0.0], [bi])
        g.nodes[parent].children.append(ex)
        shifts[ex] = body

    blob = bytearray(g.binary_blob() or b"")

    def push(data: np.ndarray, typ: str, **extra: Any) -> int:
        raw = np.ascontiguousarray(data, np.float32).tobytes()
        blob.extend(b"\x00" * ((-len(blob)) % 4))
        g.bufferViews.append(BufferView(buffer=0, byteOffset=len(blob), byteLength=len(raw)))
        blob.extend(raw)
        g.accessors.append(Accessor(bufferView=len(g.bufferViews) - 1, componentType=FLOAT, count=len(data), type=typ, **extra))
        return len(g.accessors) - 1

    t_acc = push(np.linspace(0.0, CLIP_S, KEYFRAMES), SCALAR, min=[0.0], max=[float(CLIP_S)])
    rest = [np.zeros(3)] * KEYFRAMES

    def key(anim: Any, node: int, path: str, data: np.ndarray, typ: str) -> None:
        anim.samplers.append(AnimationSampler(input=t_acc, output=push(data, typ), interpolation=ANIM_LINEAR))
        anim.channels.append(AnimationChannel(sampler=len(anim.samplers) - 1, target=AnimationChannelTarget(node=node, path=path)))

    for clip, frames in clips.items():
        anim = Animation(name=clip, samplers=[], channels=[])
        for piv, j in pivots.items():
            o = axes[j.name][0]
            ms = [jm.motion(j, axes[j.name], float(v.get(j.name, 0.0))) for v in frames]
            rot = np.asarray([_quat(m[:3, :3]) for m in ms])
            for k in range(1, len(rot)):  # neighbouring quaternions in one hemisphere, so the viewer's slerp takes the short way
                if float(np.dot(rot[k], rot[k - 1])) < 0:
                    rot[k] = -rot[k]
            key(anim, piv, "rotation", rot, VEC4)
            key(anim, piv, "translation", np.asarray([m[:3, :3] @ o + m[:3, 3] for m in ms]), VEC3)
        for ex, body in shifts.items():
            key(anim, ex, "translation", np.asarray((explode or {}).get(body, rest) if clip == "explode" else rest), VEC3)
        g.animations.append(anim)
    g.set_binary_blob(bytes(blob))
    g.buffers[0].byteLength = len(blob)
    g.save(str(glb))


def write_html(path: Path, actx: AsmCtx, glb_name: str, clips: list[str], fb: dict[str, Any] | None, sim: dict[str, Any] | None) -> Path:
    gates = "".join(f"<tr><td>[{g['tier']}] {g['id']}</td><td class='{'pass' if g['ok'] else ('fail' if g['ok'] is False else '')}'>{'PASS' if g['ok'] else ('FAIL' if g['ok'] is False else 'n/a')}</td></tr>"
                    for g in (fb or {}).get("gates") or [])
    obs = "".join(f"<tr><td>{k}</td><td>{v.get('status')}</td><td>{_fmt(v.get('value'))}" + (f" &plusmn; {_fmt(v['u_numerical'])}" if v.get("u_numerical") else "")
                  + f" {v.get('unit') or ''}</td><td>{ {True: 'yes', False: 'no'}.get(v.get('resolved'), '-') }</td><td>{v.get('case') or ''}</td></tr>"
                  for k, v in ((sim or {}).get("observables") or {}).items())
    bodies = "".join(f"<label><input type='checkbox' checked data-body='{p.name}'> {p.name} <small>({p.kind}{', ' + p.role if p.role != 'solid' else ''})</small></label>" for p in actx.contract.parts if p.placed)
    options = "".join(f"<option value='{c}'{' selected' if c == 'operate' else ''}>{c}</option>" for c in clips)
    verdict = "PASS" if (fb or {}).get("ok") else ("FAIL" if fb else "unscored")
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{actx.name} assembly: {verdict}</title>
<script type="module" src="{MODEL_VIEWER_CDN}"></script>
<style>body{{font:14px system-ui,sans-serif;margin:0;display:grid;grid-template-columns:1fr 380px;height:100vh}}model-viewer{{width:100%;height:100%;background:#f4f4f4}}
aside{{padding:14px;overflow:auto;border-left:1px solid #ddd}}table{{border-collapse:collapse;width:100%;margin:6px 0 12px}}td{{border-bottom:1px solid #eee;padding:3px 4px;font-variant-numeric:tabular-nums}}
h1{{font-size:16px;margin:0 0 8px}}.pass{{color:#177a2a}}.fail{{color:#b3261e}}label{{display:block;margin:4px 0}}</style></head><body>
<model-viewer id="mv" src="{glb_name}" camera-controls autoplay animation-name="{'operate' if 'operate' in clips else (clips[0] if clips else '')}" shadow-intensity="0.6" exposure="1.0" interaction-prompt="none"></model-viewer>
<aside><h1>{actx.name} <span class="{'pass' if verdict == 'PASS' else 'fail'}">{verdict}</span></h1>
<p>{actx.contract.intent[:400]}</p>
<label>clip <select id="clip">{options}</select></label><label><input type="checkbox" id="play" checked> play</label>
{bodies}
<h2>gates</h2><table>{gates}</table><h2>observables</h2><table><tr><td>id</td><td>status</td><td>value &plusmn; u_numerical</td><td>mesh-resolved</td><td>case</td></tr>{obs}</table>
<p><small>A value its mesh ladder does not resolve is not evidence of performance; report.md gives each prediction's validation basis.</small></p></aside>
<script>
const mv = document.getElementById('mv');
document.getElementById('clip').onchange = e => {{ mv.animationName = e.target.value; mv.play(); }};
document.getElementById('play').onchange = e => {{ if (e.target.checked) mv.play(); else mv.pause(); }};
for (const cb of document.querySelectorAll('input[data-body]')) cb.onchange = () => {{
  for (const m of mv.model.materials) if (m.name === 'body:' + cb.dataset.body) {{ const c = m.pbrMetallicRoughness.baseColorFactor;
    m.pbrMetallicRoughness.setBaseColorFactor([c[0], c[1], c[2], cb.checked ? 1.0 : 0.0]); m.setAlphaMode(cb.checked ? 'OPAQUE' : 'BLEND'); }} }};
</script></body></html>"""
    path.write_text(html, encoding="utf-8")
    return path


def _fmt(v: Any) -> str:
    return f"{v:.5g}" if isinstance(v, (int, float)) else ("" if v is None else str(v))


def generate(actx: AsmCtx, out_dir: Path, *, fb: dict[str, Any] | None = None, sim: dict[str, Any] | None = None) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    scene, placements, coms = build_scene(actx)
    values = clip_values(actx, placements)
    values["explode"] = [{} for _ in range(KEYFRAMES)]
    default = "operate" if "operate" in values else next(iter(values))
    explode = explode_offsets(actx, coms)
    glb, full = out_dir / "assembly.glb", out_dir / "assembly-clips.glb"
    data = scene.export(file_type="glb")
    for path, clips in ((glb, {default: values[default]}), (full, values)):
        path.write_bytes(data)
        rig(path, actx.contract, placements, clips, explode)
    return {"glb": str(glb), "glb_clips": str(full), "clips": list(values), "default_clip": default,
            "html": str(write_html(out_dir / "assembly.html", actx, full.name, list(values), fb, sim))}

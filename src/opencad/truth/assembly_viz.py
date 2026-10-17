"""Visual verification of an assembly placement: GLB with the joint animated, plus an HTML viewer with a joint slider.

Everything is local: OpenCascade tessellates the STEP bodies, trimesh writes the scene, pygltflib adds a glTF
animation along the joint's degree of freedom. No hosted engine calls. Inputs are the worker's `assembly.yaml`,
the STEP bodies and `joint-task.json`. After scoring, a translucent `ghost:<body>` node is the dataset pose of
body one (toggle it in the HTML viewer; a raw GLB preview always shows it).
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

from opencad.truth import assembly_task as at

BODY_COLORS = ((205, 70, 60, 255), (60, 120, 220, 255))
GHOST_COLOR = (140, 140, 140, 70)
AXIS_COLOR = (40, 190, 60, 255)
PIVOT = "joint_pivot"
CYCLE_S = 4.0
MODEL_VIEWER_CDN = "https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js"


def tessellate(step: Path, deflection: float = 0.1) -> trimesh.Trimesh:
    from opencad.truth.scorer import step_to_mesh

    with tempfile.TemporaryDirectory(prefix="opencad-viz-") as td:
        stl = step_to_mesh(Path(step), Path(td) / "body.stl", deflection)
        m = trimesh.load(stl, force="mesh")
    return m


def _paint(mesh: trimesh.Trimesh, rgba: tuple[int, int, int, int], name: str) -> trimesh.Trimesh:
    """A named PBR material (not vertex colours) so the viewer can toggle bodies and ghosts by material name."""
    from trimesh.visual.material import PBRMaterial

    mat = PBRMaterial(name=name, baseColorFactor=[c / 255.0 for c in rgba], metallicFactor=0.1, roughnessFactor=0.7,
                      alphaMode="BLEND" if rgba[3] < 255 else "OPAQUE", doubleSided=rgba[3] < 255)
    mesh.visual = trimesh.visual.TextureVisuals(material=mat)
    return mesh


def _unit(v) -> np.ndarray:
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) or 1.0)


def joint_frame(jt: dict[str, Any], a2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Body two's placed key point and axis direction: the joint axis every motion is defined on."""
    return at.transform_line(np.asarray(jt["two"]["key_point_local_mm"], float), np.asarray(jt["two"]["axis_direction_local"], float), a2)


def motion_range(jt: dict[str, Any]) -> dict[str, Any]:
    """What the joint may do, from its type and enabled limits (radians / mm)."""
    jtype = str(jt.get("joint_type", ""))
    lim = jt.get("limits") or {}
    rot = lim.get("rotation_limits") or {}
    sli = lim.get("slide_limits") or {}
    rot_range = (rot.get("minimum_value", 0.0) if rot.get("is_minimum_value_enabled") else 0.0,
                 rot.get("maximum_value", 2 * math.pi) if rot.get("is_maximum_value_enabled") else 2 * math.pi)
    slide_range = (sli.get("minimum_value", -10.0) * 10 if sli.get("is_minimum_value_enabled") else -10.0,
                   sli.get("maximum_value", 10.0) * 10 if sli.get("is_maximum_value_enabled") else 10.0)
    if "Revolute" in jtype:
        return {"kind": "revolute", "rotation": rot_range, "slide": (0.0, 0.0), "label": "joint angle (deg)"}
    if "Slider" in jtype:
        return {"kind": "slider", "rotation": (0.0, 0.0), "slide": slide_range, "label": "travel (mm)"}
    if "Cylindrical" in jtype or "PinSlot" in jtype:
        return {"kind": "cylindrical", "rotation": rot_range, "slide": slide_range, "label": "angle (deg) + travel (mm)"}
    if "Ball" in jtype:
        return {"kind": "ball", "rotation": (0.0, math.radians(15.0)), "slide": (0.0, 0.0), "label": "wobble (deg)"}
    if "Planar" in jtype:
        return {"kind": "planar", "rotation": (0.0, 0.0), "slide": (-10.0, 10.0), "label": "in-plane travel (mm)"}
    return {"kind": "rigid", "rotation": (0.0, 0.0), "slide": (0.0, 10.0), "label": "explode (mm)"}


def pose_at(t: float, mr: dict[str, Any], k: np.ndarray, d: np.ndarray) -> np.ndarray:
    """Rigid motion of body one about the joint axis (through k along d) at phase t in [0, 1]."""
    phase = 0.5 - 0.5 * math.cos(2 * math.pi * t)  # 0 -> 1 -> 0, smooth
    ang = mr["rotation"][0] + (mr["rotation"][1] - mr["rotation"][0]) * (t if mr["kind"] == "revolute" and mr["rotation"][1] - mr["rotation"][0] >= 2 * math.pi - 1e-9 else phase)
    travel = mr["slide"][0] + (mr["slide"][1] - mr["slide"][0]) * phase
    m = np.eye(4)
    if mr["kind"] in ("revolute", "cylindrical"):
        m = trimesh.transformations.rotation_matrix(ang, d, point=k)
    elif mr["kind"] == "ball":
        perp = _unit(np.cross(d, [1, 0, 0]) if abs(d[0]) < 0.9 else np.cross(d, [0, 1, 0]))
        m = trimesh.transformations.rotation_matrix(ang, perp, point=k) @ trimesh.transformations.rotation_matrix(2 * math.pi * t, d, point=k)
    if mr["kind"] in ("slider", "cylindrical", "rigid"):
        m = trimesh.transformations.translation_matrix(d * travel) @ m
    elif mr["kind"] == "planar":
        perp = _unit(np.cross(d, [1, 0, 0]) if abs(d[0]) < 0.9 else np.cross(d, [0, 1, 0]))
        m = trimesh.transformations.translation_matrix(perp * travel) @ m
    return m


def build_scene(
    work: Path,
    jt: dict[str, Any],
    manifest: dict[str, Any],
    truth: tuple[np.ndarray, np.ndarray] | None = None,
    placed_steps: dict[str, Path] | None = None,
) -> tuple[trimesh.Scene, dict[str, Any]]:
    b1, b2 = jt["body_one"], jt["body_two"]
    bodies = manifest.get("bodies") or manifest
    a1, a2 = at.manifest_matrix(bodies[b1]), at.manifest_matrix(bodies[b2])
    local1 = tessellate(work / f"{b1}.step")
    if placed_steps and b1 in placed_steps and b2 in placed_steps:
        m1, m2 = tessellate(placed_steps[b1]), tessellate(placed_steps[b2])
        t1, t2 = np.eye(4), np.eye(4)
    else:
        m1, m2 = local1, tessellate(work / f"{b2}.step")
        t1, t2 = a1, a2
    _paint(m1, BODY_COLORS[0], f"body:{b1}")
    _paint(m2, BODY_COLORS[1], f"body:{b2}")
    k2, d2 = joint_frame(jt, a2)
    scene = trimesh.Scene()
    scene.add_geometry(m2, node_name=f"body:{b2}", geom_name=f"body:{b2}", transform=t2)
    # body one hangs under a pivot at the joint key point so an animation of the pivot is a motion about the joint axis
    t_pivot = trimesh.transformations.translation_matrix(k2)
    scene.graph.update(frame_to=PIVOT, frame_from=scene.graph.base_frame, matrix=t_pivot)
    scene.add_geometry(m1, node_name=f"body:{b1}", geom_name=f"body:{b1}", parent_node_name=PIVOT, transform=np.linalg.inv(t_pivot) @ t1)
    extent = float(np.linalg.norm(scene.bounds[1] - scene.bounds[0]))
    axis = _paint(trimesh.creation.cylinder(radius=max(0.15, extent / 600), height=extent * 1.2, sections=24), AXIS_COLOR, "joint_axis")
    scene.add_geometry(axis, node_name="joint_axis", geom_name="joint_axis", transform=_axis_transform(k2, d2))
    if truth is not None:
        truth1, truth2 = truth
        rel = a2 @ np.linalg.inv(truth2)  # dataset pose expressed in the worker's shared frame (body two coincides)
        g1 = _paint(local1.copy(), GHOST_COLOR, f"ghost:{b1}")
        scene.add_geometry(g1, node_name=f"ghost:{b1}", geom_name=f"ghost:{b1}", transform=rel @ truth1)
    info = {"a1": a1.tolist(), "a2": a2.tolist(), "pivot": k2.tolist(), "axis": d2.tolist(), "extent": extent}
    return scene, info


def _axis_transform(k: np.ndarray, d: np.ndarray) -> np.ndarray:
    m = trimesh.geometry.align_vectors([0, 0, 1], _unit(d))
    m = np.asarray(m, float)
    m[:3, 3] = k
    return m


def export_glb(scene: trimesh.Scene, path: Path, jt: dict[str, Any], info: dict[str, Any]) -> Path:
    path = Path(path)
    path.write_bytes(scene.export(file_type="glb"))
    add_joint_animation(path, jt, info)
    return path


def add_joint_animation(glb: Path, jt: dict[str, Any], info: dict[str, Any], keyframes: int = 25) -> None:
    """One glTF animation on the pivot node: the joint's degree of freedom over one CYCLE_S loop. Materials are named after their nodes."""
    from pygltflib import (ANIM_LINEAR, FLOAT, SCALAR, VEC3, VEC4, Accessor, Animation, AnimationChannel, AnimationChannelTarget, AnimationSampler,
                           BufferView, GLTF2)

    g = GLTF2().load(str(glb))
    nodes = {n.name: i for i, n in enumerate(g.nodes) if n.name}
    for i, n in enumerate(g.nodes):  # name the materials so the viewer can toggle bodies and ghosts
        if n.mesh is not None and n.name and n.name.split(":", 1)[0] in ("body", "ghost", "joint_axis"):
            for prim in g.meshes[n.mesh].primitives:
                if prim.material is not None:
                    g.materials[prim.material].name = n.name
                    if n.name.startswith("ghost"):
                        g.materials[prim.material].alphaMode = "BLEND"
                        g.materials[prim.material].doubleSided = True
    if PIVOT not in nodes:
        g.save(str(glb))
        return
    mr = motion_range(jt)
    k = np.asarray(info["pivot"], float)
    d = _unit(info["axis"])
    times = np.linspace(0.0, CYCLE_S, keyframes, dtype=np.float32)
    rots, trans = [], []
    for t in times:
        m = pose_at(float(t) / CYCLE_S, mr, np.zeros(3), d)  # about the pivot's own origin (the pivot sits at k)
        q = trimesh.transformations.quaternion_from_matrix(m)  # (w, x, y, z)
        rots.append([q[1], q[2], q[3], q[0]])
        trans.append(k + m[:3, 3])
    rot_blob = np.asarray(rots, np.float32).tobytes()
    tr_blob = np.asarray(trans, np.float32).tobytes()
    time_blob = times.tobytes()
    blob = g.binary_blob() or b""
    pad = (-len(blob)) % 4
    blob = blob + b"\x00" * pad
    offsets = {}
    for name, data in (("time", time_blob), ("rot", rot_blob), ("tr", tr_blob)):
        offsets[name] = len(blob)
        blob += data + b"\x00" * ((-len(data)) % 4)
    g.set_binary_blob(blob)
    buf_index = 0
    g.buffers[buf_index].byteLength = len(blob)
    bv0 = len(g.bufferViews)
    g.bufferViews += [BufferView(buffer=buf_index, byteOffset=offsets["time"], byteLength=len(time_blob)),
                      BufferView(buffer=buf_index, byteOffset=offsets["rot"], byteLength=len(rot_blob)),
                      BufferView(buffer=buf_index, byteOffset=offsets["tr"], byteLength=len(tr_blob))]
    acc0 = len(g.accessors)
    g.accessors += [Accessor(bufferView=bv0, componentType=FLOAT, count=keyframes, type=SCALAR, min=[0.0], max=[float(CYCLE_S)]),
                    Accessor(bufferView=bv0 + 1, componentType=FLOAT, count=keyframes, type=VEC4),
                    Accessor(bufferView=bv0 + 2, componentType=FLOAT, count=keyframes, type=VEC3)]
    anim = Animation(name=f"joint:{mr['kind']}", samplers=[AnimationSampler(input=acc0, output=acc0 + 1, interpolation=ANIM_LINEAR),
                                                          AnimationSampler(input=acc0, output=acc0 + 2, interpolation=ANIM_LINEAR)],
                     channels=[AnimationChannel(sampler=0, target=AnimationChannelTarget(node=nodes[PIVOT], path="rotation")),
                               AnimationChannel(sampler=1, target=AnimationChannelTarget(node=nodes[PIVOT], path="translation"))])
    # the pivot node must use TRS (not a matrix) for animation targets
    pivot = g.nodes[nodes[PIVOT]]
    pivot.matrix = None
    pivot.translation = [float(x) for x in k]
    pivot.rotation = [0.0, 0.0, 0.0, 1.0]
    pivot.scale = [1.0, 1.0, 1.0]
    g.animations.append(anim)
    g.save(str(glb))


def write_html(path: Path, glb_name: str, jt: dict[str, Any], card: dict[str, Any] | None, mr: dict[str, Any], verdict: str) -> Path:
    checks = (card or {}).get("checks") or {}
    rows = "".join(f"<tr><td>{k}</td><td>{'ok' if v.get('ok') else ('FAIL' if 'ok' in v else '')}</td><td>{_fmt(v.get('measured'))}</td><td>{_fmt(v.get('expected', v.get('max')))}</td></tr>" for k, v in checks.items())
    unit = "deg" if mr["kind"] in ("revolute", "ball") else "mm"
    lo, hi = (math.degrees(mr["rotation"][0]), math.degrees(mr["rotation"][1])) if unit == "deg" else mr["slide"]
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{jt.get('set', '')} assembly: {verdict}</title>
<script type="module" src="{MODEL_VIEWER_CDN}"></script>
<style>body{{font:14px system-ui,sans-serif;margin:0;display:grid;grid-template-columns:1fr 360px;height:100vh}}model-viewer{{width:100%;height:100%;background:#f4f4f4}}
aside{{padding:14px;overflow:auto;border-left:1px solid #ddd}}table{{border-collapse:collapse;width:100%}}td{{border-bottom:1px solid #eee;padding:3px 4px;font-variant-numeric:tabular-nums}}
h1{{font-size:16px;margin:0 0 8px}}.pass{{color:#177a2a}}.fail{{color:#b3261e}}label{{display:block;margin:6px 0}}input[type=range]{{width:100%}}</style></head><body>
<model-viewer id="mv" src="{glb_name}" camera-controls autoplay animation-name="joint:{mr['kind']}" shadow-intensity="0.6" exposure="1.0" interaction-prompt="none"></model-viewer>
<aside><h1>{jt.get('set', '')} <span class="{'pass' if verdict == 'PASS' else 'fail'}">{verdict}</span></h1>
<p>{jt.get('joint_type', '')} "{jt.get('joint_name', '')}", offset {jt.get('offset_mm', 0):.2f} mm, {'flipped' if jt.get('is_flipped') else 'aligned'}. Red = body one ({jt.get('body_one')}), blue = body two ({jt.get('body_two')}), green = joint axis through body two's key point. Grey is a second mesh of body one in the dataset pose (not a rendering artifact); uncheck it to hide.</p>
<label><input type="checkbox" id="play" checked> animate the joint ({mr['label']})</label>
<label>{mr['label']}: <span id="val">-</span><input type="range" id="scrub" min="0" max="1000" value="0"></label>
<label><input type="checkbox" id="ghost"> show dataset pose (ghost)</label>
<label><input type="checkbox" id="b1" checked> show body one</label>
<label><input type="checkbox" id="b2" checked> show body two</label>
<table><tr><td>check</td><td></td><td>measured</td><td>expected / max</td></tr>{rows}</table>
<p style="color:#666">Scrub the slider to drive the joint by hand; the range is the joint's enabled limits ({lo:.1f} .. {hi:.1f} {unit}). Orbit with the mouse, zoom with the wheel.</p></aside>
<script>
const mv = document.getElementById('mv'), scrub = document.getElementById('scrub'), val = document.getElementById('val'), play = document.getElementById('play');
const cycle = {CYCLE_S}, lo = {lo}, hi = {hi};
function setAlpha(prefix, on) {{ if (!mv.model) return; for (const m of mv.model.materials) {{ if (m.name && m.name.startsWith(prefix)) {{ const c = m.pbrMetallicRoughness.baseColorFactor; m.pbrMetallicRoughness.setBaseColorFactor([c[0], c[1], c[2], on ? (prefix === 'ghost' ? 0.28 : 1.0) : 0.0]); m.setAlphaMode(on && prefix !== 'ghost' ? 'OPAQUE' : 'BLEND'); }} }} }}
document.getElementById('ghost').onchange = e => setAlpha('ghost', e.target.checked);
document.getElementById('b1').onchange = e => setAlpha('body:{jt.get('body_one')}', e.target.checked);
document.getElementById('b2').onchange = e => setAlpha('body:{jt.get('body_two')}', e.target.checked);
play.onchange = () => {{ if (play.checked) mv.play(); else mv.pause(); }};
scrub.oninput = () => {{ play.checked = false; mv.pause(); mv.currentTime = cycle * scrub.value / 1000; }};
mv.addEventListener('load', () => {{ setAlpha('ghost', false); }});
setInterval(() => {{ if (!mv.paused) scrub.value = Math.round(1000 * (mv.currentTime % cycle) / cycle); const t = scrub.value / 1000; const phase = 0.5 - 0.5 * Math.cos(2 * Math.PI * t); const v = '{mr['kind']}' === 'revolute' && (hi - lo) >= 359.9 ? lo + (hi - lo) * t : lo + (hi - lo) * phase; val.textContent = v.toFixed(1) + ' {unit}'; }}, 100);
</script></body></html>"""
    Path(path).write_text(html, encoding="utf-8")
    return Path(path)


def _fmt(v: Any) -> str:
    if isinstance(v, (int, float)):
        return f"{v:.4g}"
    return "" if v is None else str(v)


def generate(
    work: Path,
    out_dir: Path,
    *,
    card: dict[str, Any] | None = None,
    truth_joint_set: Path | None = None,
    placed_steps: dict[str, Path] | None = None,
    native_glb: Path | None = None,
) -> dict[str, Any]:
    """assembly.glb (+animation) and assembly.html for one attempt; returns the paths. Never raises into the scorer."""
    import shutil

    work, out_dir = Path(work), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    jt = json.loads((work / "joint-task.json").read_text(encoding="utf-8"))
    import yaml

    manifest = yaml.safe_load((work / "assembly.yaml").read_text(encoding="utf-8")) or {}
    truth = None
    if truth_joint_set is not None and Path(truth_joint_set).exists():
        truth = at.truth_poses(json.loads(Path(truth_joint_set).read_text(encoding="utf-8")))
    scene, info = build_scene(work, jt, manifest, truth, placed_steps=placed_steps)
    verdict = str((card or {}).get("verdict") or "unscored")
    out = {
        "glb": str(export_glb(scene, out_dir / "assembly.glb", jt, info)),
        "html": str(write_html(out_dir / "assembly.html", "assembly.glb", jt, card, motion_range(jt), verdict)),
        "motion": motion_range(jt)["kind"],
    }
    if native_glb and Path(native_glb).exists():
        dest = out_dir / "assembly-native.glb"
        shutil.copy2(native_glb, dest)
        out["native_glb"] = str(dest)
    return out

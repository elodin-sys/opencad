#!/usr/bin/env python
"""Build the held-out Fusion 360 Gallery cases (Phase 6) from the frozen selection.

For each selected joint set two tasks are staged:
- reconstruction: `fusion-<set>-recon` truth case: body one's STEP is truth; the agent gets renders,
  section drawings and a dimension sheet; observables are bbox, volume, COM, every axis-aligned
  cylinder, planar faces by level, and deviation.
- assembly: `truth/cases/fusion-<set>-assembly/` holds both bodies (agent inputs, in their local
  frames), a joint description written from the dataset joint (which faces mate, joint type, offset
  and flip in words), and the joint-set JSON as truth; scored by opencad.truth.assembly_task.

Autodesk Fusion 360 Gallery Assembly-Joint dataset (j1.0.0), non-commercial research license; used here
for research evaluation only.

  python scripts/derive_fusion_heldout.py && for c in $(ls truth/cases | rg '^fusion-'); do python -m opencad.truth pin $c; done
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from opencad.geomcheck import brep  # noqa: E402
from opencad.truth.scorer import step_to_mesh  # noqa: E402

SEL = Path.home() / ".cache" / "opencad" / "downloads" / "fusion360" / "selected"
SELECTION = REPO / "truth" / "cases" / "_fusion360-selection.yaml"
SOURCE = {
    "citation": "Autodesk AI Lab, Fusion 360 Gallery Dataset, Assembly-Joint subset j1.0.0 (Willis et al., JoinABLe, CVPR 2022)",
    "urls": ["https://github.com/AutodeskAILab/Fusion360GalleryDataset/blob/master/docs/assembly_joint.md",
             "https://fusion-360-gallery-dataset.s3.us-west-2.amazonaws.com/assembly/j1.0.0/j1.0.0.7z"],
    "accessed": "2026-09-17", "revision": "j1.0.0",
    "license": "Fusion 360 Gallery Dataset License (non-commercial research); STEP bodies in mm, joint JSON in cm",
}


def _slug(v: float) -> str:
    return f"{v:.3g}".replace("-", "m").replace(".", "p")


def recon_observables(step: Path, step_rel: str, stl_rel: str) -> list[dict]:
    shape = brep.read_step(step)
    a = brep.analyze_step(step)
    obs: list[dict] = [
        {"id": "bbox_size", "kind": "bbox_size", "expected": [round(x, 4) for x in a["bbox_size"]], "tolerance": 0.1},
        {"id": "solid_count", "kind": "solid_count", "expected": 1},
        {"id": "volume", "kind": "volume", "from": {"file": step_rel, "measure": "volume"}, "tolerance_rel": 0.01},
        {"id": "center_of_mass", "kind": "center_of_mass", "from": {"file": step_rel, "measure": "center_of_mass"}, "tolerance": 0.2},
    ]
    for c in brep.cylinders(shape):
        if c["radius"] < 0.5 or sum(1 for x in c["direction"] if abs(abs(x) - 1) < 1e-6) != 1:
            continue
        cid = f"{c['kind']}_d{_slug(c['diameter'])}_{_slug(c['center'][0])}_{_slug(c['center'][1])}_{_slug(c['center'][2])}"
        obs.append({"id": cid, "kind": "cylinder", "cyl_kind": c["kind"], "point": [round(x, 4) for x in c["center"]], "direction": [round(x, 4) for x in c["direction"]],
                    "radius": round(c["radius"], 4), "radius_tolerance": 0.05, "tolerance": 0.1, "length": round(c["length"], 4), "length_tolerance": 0.2})
    faces = brep.planar_faces(shape)
    TOL = 0.05  # the scorer sums every face within this band of `at`; group the same way, and skip levels that would overlap a neighbour's band
    levels: dict[tuple[str, str], list[float]] = {}
    for f in faces:
        n = f["normal"]
        ax = [i for i in range(3) if abs(abs(n[i]) - 1) < 1e-6 and all(abs(n[j]) < 1e-6 for j in range(3) if j != i)]
        if not ax or f["area"] < 4.0:
            continue
        i = ax[0]
        levels.setdefault(("xyz"[i], "+" if n[i] > 0 else "-"), []).append(f["point"][i])
    for (axis, sign), positions in levels.items():
        i = "xyz".index(axis)
        want = 1.0 if sign == "+" else -1.0
        distinct = sorted({round(p, 3) for p in positions})
        for at in distinct:
            if any(abs(at - other) <= 2 * TOL and other != at for other in distinct):
                continue  # two levels closer than the band cannot be told apart by a sum
            hits = [g for g in faces if abs(g["normal"][i] - want) < 1e-6 and all(abs(g["normal"][j]) < 1e-6 for j in range(3) if j != i) and abs(g["point"][i] - at) <= TOL]
            area = round(sum(g["area"] for g in hits), 3)
            if area <= 0:
                continue
            obs.append({"id": f"face_{axis}{'p' if sign == '+' else 'n'}_{_slug(at)}", "kind": "face", "plane": axis, "at": at, "normal": sign, "mode": "sum",
                        "expected": area, "area_tolerance_rel": 0.02, "tolerance": TOL})
    obs.append({"id": "deviation", "kind": "deviation", "reference": stl_rel, "p95_max": 0.2, "hausdorff_max": 1.0, "silhouette_iou_min": 0.98})
    return obs


def _local_joint_side(g: dict, step: Path) -> dict:
    """The joint geometry of one side in the body's own frame: face bbox, key point, axis direction, radius (from the STEP)."""
    import numpy as np

    from opencad.truth import assembly_task as at

    t = at.transform_matrix(g.get("transform"))
    inv = np.linalg.inv(t)
    o_asm, d_asm = at.axis_assembled(g)
    kp = inv[:3, :3] @ o_asm + inv[:3, 3]
    d = inv[:3, :3] @ d_asm
    e = g["entity_one"]
    bb = e["bounding_box"]
    lo = [round(bb["min_point"][k] * 10, 3) for k in "xyz"]
    hi = [round(bb["max_point"][k] * 10, 3) for k in "xyz"]
    radius = None
    if e.get("surface_type") == "CylinderSurfaceType":
        best = None
        for cy in brep.cylinders(brep.read_step(step)):
            dd = np.asarray(cy["direction"], float)
            if abs(abs(float(np.dot(dd, d))) - 1) > 1e-3:
                continue
            w = kp - np.asarray(cy["point"], float)
            dist = float(np.linalg.norm(w - np.dot(w, dd) * dd))
            if dist < 0.05 and (best is None or dist < best[0]):
                best = (dist, cy["radius"])
        radius = round(best[1], 4) if best else None
    return {"surface_type": e.get("surface_type"), "radius_mm": radius, "bbox_local_mm": [lo, hi], "key_point_type": g.get("key_point_type"),
            "key_point_local_mm": [round(float(x), 4) for x in kp], "axis_direction_local": [round(float(x), 6) for x in d]}


def joint_task(js: dict, b1: str, b2: str, case_dir: Path) -> dict:
    """Machine-readable joint definition for the worker and the local critic: everything the evaluator's four metrics depend on, no poses."""
    j = js["joints"][0]
    one = _local_joint_side(j["geometry_or_origin_one"], case_dir / "inputs" / f"{b1}.step")
    two = _local_joint_side(j["geometry_or_origin_two"], case_dir / "inputs" / f"{b2}.step")
    jm = j["joint_motion"]
    limits = {}
    for key in ("rotation_limits", "slide_limits"):
        lim = jm.get(key) or {}
        if lim.get("is_minimum_value_enabled") or lim.get("is_maximum_value_enabled"):
            limits[key] = {k: lim.get(k) for k in ("minimum_value", "maximum_value", "rest_value", "is_minimum_value_enabled", "is_maximum_value_enabled")}
    return {
        "set": js.get("set", ""), "joint_name": j.get("name", ""), "joint_type": jm["joint_type"], "rotation_axis": jm.get("rotation_axis"), "limits": limits,
        "body_one": b1, "body_two": b2, "one": one, "two": two,
        "offset_mm": (j.get("offset") or {}).get("value", 0.0) * 10, "angle_rad": (j.get("angle") or {}).get("value", 0.0), "is_flipped": bool(j.get("is_flipped")),
        "evaluator": {
            "axis_angle_max_deg": 2.0, "axis_line_distance_max_mm": 0.5, "axial_offset_tolerance_mm": 0.5, "interference_max_mm3": "max(1, dataset's own interference + 1)", "gap_max_mm": 1.0,
            "axial_offset_definition": "(K1' - K2') . d2' where K1', K2' are the two key points and d2' body two's axis direction, all after placement; must equal offset_mm",
            "flip_definition": "is_flipped true: body one's placed axis_direction_local is anti-parallel to body two's placed axis_direction_local; false: parallel",
        },
    }


def joint_description(js: dict, b1: str, b2: str, a1: dict, a2: dict, jt: dict | None = None) -> str:
    j = js["joints"][0]
    off = (j.get("offset") or {}).get("value", 0.0) * 10
    ang = (j.get("angle") or {}).get("value", 0.0)
    flipped = bool(j.get("is_flipped"))
    jtype = j["joint_motion"]["joint_type"].replace("JointType", " joint")

    def side(s: dict) -> str:
        lo, hi = s["bbox_local_mm"]
        r = f", radius {s['radius_mm']} mm" if s.get("radius_mm") else ""
        return (f"{s['surface_type']} face{r}, body-local bbox {lo} .. {hi} mm; joint key point ({s['key_point_type']}) at body-local "
                f"{s['key_point_local_mm']} mm on the face's axis, axis direction (body-local) {s['axis_direction_local']}")

    sides = ""
    if jt is not None:
        sides = f"- Body one's joint face: {side(jt['one'])}.\n- Body two's joint face: {side(jt['two'])}.\n"
    limits = ""
    if jt and jt.get("limits"):
        limits = f"- Motion limits in the dataset: {jt['limits']} (radians / mm).\n"
    return f"""# Assembly task: joint set {js.get('set', '')}

Two parts are supplied as STEP files in their own local frames (millimetres): `{b1}.step`
(body one, bbox size {a1['bbox_size']}) and `{b2}.step` (body two, bbox size {a2['bbox_size']}).
They are joined by a {jtype} named "{j.get('name', '')}". The machine-readable joint definition is `joint-task.json`
(same numbers as below).

{sides}- Joint definition (Fusion 360 joint parameters, as designed): the two faces' axes are colinear in the assembled state;
  `is_flipped` = {flipped}: after placement body one's axis direction is {'ANTI-parallel' if flipped else 'parallel'} to body two's;
  `offset` = {off:.2f} mm: the axial offset between the two key points, (K1' - K2') . d2' measured along body two's
  placed axis direction, equals {off:.2f} mm; the joint angle is {ang:.4f} rad in the dataset, but any rotation about a revolute
  axis is accepted.
{limits}- The evaluator (`opencad.truth.assembly_task.score`) applies your transforms in OpenCascade and checks: axis angle <= 2 deg,
  axis line distance <= 0.5 mm, |axial offset - {off:.2f}| <= 0.5 mm, interference <= max(1 mm3, the dataset's own assembled
  interference + 1 mm3) (the dataset's pose may itself interpenetrate slightly; do not reject the key-point placement for that),
  and the bodies touch or nearly touch (gap <= 1 mm). `python -m opencad.truth assembly-check <work dir>` computes exactly
  these numbers from your `assembly.yaml` without the truth.

Deliverable: `assembly.yaml` with a placement for each body in one shared frame, e.g.

```yaml
bodies:
  {b1}: {{origin: [x, y, z], x_axis: [1, 0, 0], y_axis: [0, 1, 0], z_axis: [0, 0, 1]}}
  {b2}: {{origin: [0, 0, 0], x_axis: [1, 0, 0], y_axis: [0, 1, 0], z_axis: [0, 0, 1]}}
```

(or `matrix: 4x4` per body). Body two may stay at the identity. Do not modify the STEP files.
"""


def stage_assembly_case(js: dict, sid: str, d: Path, b1: str, b2: str, size1: list[float], *, refresh_only: bool = False) -> Path:
    """Write (or rewrite) the assembly case: inputs (both STEP bodies, task text, joint-task.json, renders), truth joint JSON, task.yaml."""
    acase = REPO / "truth" / "cases" / f"fusion-{sid.replace('joint_set_', '')}-assembly"
    (acase / "inputs").mkdir(parents=True, exist_ok=True)
    (acase / "truth").mkdir(exist_ok=True)
    if not refresh_only:
        for b in (b1, b2):
            shutil.copy2(d / f"{b}.step", acase / "inputs" / f"{b}.step")
        shutil.copy2(d / "joint_set.json", acase / "truth" / "joint_set.json")
        for b in (b1, b2):
            subprocess.run([sys.executable, str(REPO / "scripts" / "render_reference.py"), str(acase / "inputs" / f"{b}.step"), str(acase / "inputs" / "renders"), "--views", "iso,top,front", "--px", "1200", "--prefix", f"{b}-"], check=True)
    a2 = brep.analyze_step(acase / "inputs" / f"{b2}.step")
    jt = joint_task(js, b1, b2, acase)
    (acase / "inputs" / "joint-task.json").write_text(json.dumps(jt, indent=2), encoding="utf-8")
    (acase / "inputs" / "assembly-task.md").write_text(joint_description(js, b1, b2, {"bbox_size": [round(x, 3) for x in size1]}, {"bbox_size": [round(x, 3) for x in a2["bbox_size"]]}, jt), encoding="utf-8")
    (acase / "task.yaml").write_text(yaml.safe_dump({"id": acase.name, "kind": "assembly", "set": sid, "bodies": [b1, b2], "source": SOURCE,
                                                        "inputs": ["inputs/assembly-task.md", "inputs/joint-task.json", f"inputs/{b1}.step", f"inputs/{b2}.step"], "truth": ["truth/joint_set.json"],
                                                        "deliverable": "assembly.yaml", "scorer": "opencad.truth.assembly_task.score",
                                                        "task_text_version": 2}, sort_keys=False), encoding="utf-8")
    return acase


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--assembly-only", action="store_true", help="rewrite only the assembly cases' task text, joint-task.json and task.yaml (recon cases and STEP/render inputs untouched)")
    args = ap.parse_args()
    sel = yaml.safe_load(SELECTION.read_text())
    for info in sel["selected"]:
        sid = info["set"]
        d = SEL / sid
        js = json.load(open(d / "joint_set.json"))
        js["set"] = sid
        b1, b2 = js["body_one"], js["body_two"]
        if args.assembly_only:
            acase = REPO / "truth" / "cases" / f"fusion-{sid.replace('joint_set_', '')}-assembly"
            size1 = brep.analyze_step(acase / "inputs" / f"{b1}.step")["bbox_size"]
            stage_assembly_case(js, sid, d, b1, b2, size1, refresh_only=True)
            print(f"refreshed {acase.name} task text (v2: key points, evaluator definition)")
            continue
        # reconstruction case for body one
        case = REPO / "truth" / "cases" / f"fusion-{sid.replace('joint_set_', '')}-recon"
        (case / "inputs" / "renders").mkdir(parents=True, exist_ok=True)
        (case / "truth").mkdir(exist_ok=True)
        step = case / "truth" / f"{b1}.step"
        shutil.copy2(d / f"{b1}.step", step)
        stl = step_to_mesh(step, case / "truth" / f"{b1}.stl", 0.02)
        a = brep.analyze_step(step)
        size = a["bbox_size"]
        secs = ",".join(f"{ax}={(a['bbox_min'][i] + a['bbox_max'][i]) / 2:.3f}" for i, ax in enumerate("xyz"))
        subprocess.run([sys.executable, str(REPO / "scripts" / "render_reference.py"), str(step), str(case / "inputs" / "renders"), "--views", "top,front,right,iso,iso2,iso-below",
                        "--sections", secs, "--px", "1600"], check=True)
        subprocess.run([sys.executable, str(REPO / "scripts" / "dimension_sheet.py"), str(step), str(case / "inputs" / "dimension-sheet.md"), "--sections", secs, "--min-face-area", "1.0"], check=True)
        (case / "inputs" / "part-brief.md").write_text(
            f"# Held-out reconstruction: Fusion 360 Gallery body `{b1}` (joint set {sid})\n\nReconstruct this single mechanical part as editable KCL from the renders, "
            f"section drawings and dimension sheet. Frame: the part's own frame as shown (bbox min {[round(x, 3) for x in a['bbox_min']]}, size {[round(x, 3) for x in size]} mm). "
            "Every cylindrical feature (holes, bosses, shafts) and planar face level in the sheet is scored on the exported STEP, with volume, centre of mass and "
            "surface deviation. One solid; export STEP and STL. The reference CAD is evaluator-only.\n", encoding="utf-8")
        inputs = [{"path": "inputs/part-brief.md", "kind": "text", "sha256": "PIN"}, {"path": "inputs/dimension-sheet.md", "kind": "text", "sha256": "PIN"}]
        images = []
        for p in sorted((case / "inputs" / "renders").glob("*.png")):
            inputs.append({"path": f"inputs/renders/{p.name}", "kind": "image", "sha256": "PIN", "units": "mm"})
            images.append(f"inputs/renders/{p.name}")
        inputs.append({"path": "inputs/renders/render-notes.md", "kind": "text", "sha256": "PIN"})
        m = {
            "id": case.name, "title": f"Held-out Fusion 360 Gallery body {b1} (joint set {sid}): reconstruction", "truth_class": "B", "role": "validation",
            "source": SOURCE,
            "intent": (f"Reconstruct the mechanical part shown in the attached renders, sections and dimension sheet as editable, parameterized KCL in the part's own frame "
                       f"(bbox min {[round(x, 3) for x in a['bbox_min']]}, size {[round(x, 3) for x in size]} mm). Declare every hole, boss and shaft as an acceptance cylinder and every "
                       "planar face level as a named face; one solid; export STEP and STL. Held-out: the pipeline is frozen, the reference CAD is evaluator-only."),
            "inputs": inputs,
            "truth": [{"path": f"truth/{b1}.step", "kind": "cad", "sha256": "PIN", "units": "mm"}, {"path": f"truth/{b1}.stl", "kind": "mesh", "sha256": "PIN", "units": "mm"}],
            "arms": [{"id": "renders-and-sheet", "design": case.name, "inputs": [i["path"] for i in inputs], "images": images, "notes": "held-out; no tuning after the run"}],
            "observables": recon_observables(step, f"truth/{b1}.step", f"truth/{b1}.stl"),
            "notes": ["Held-out generalization case: selected by seed before the pipeline freeze (truth/cases/_fusion360-selection.yaml)."],
        }
        (case / "manifest.yaml").write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
        acase = stage_assembly_case(js, sid, d, b1, b2, a["bbox_size"])
        print(f"staged {case.name} ({len(m['observables'])} observables) and {acase.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

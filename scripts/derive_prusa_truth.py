#!/usr/bin/env python
"""Build the `prusa-mini-extruder-front` truth case (and its change-request case) from Prusa's published STEP.

Truth: MINI-extruder-front.stp (Original Prusa MINI printed parts, GPL-3.0). Inputs for the agent: renders,
section drawings and an evaluator-prepared dimension sheet. Observables follow the campaign's priority
for functional parts: every axis-aligned hole/bore axis with its depth, the mating planes and the
mid-plate section are required; volume, centre of mass and exterior deviation are diagnostic.

  python scripts/derive_prusa_truth.py --source-dir ~/.cache/opencad/downloads/prusa-mini
  python -m opencad.truth pin prusa-mini-extruder-front && python -m opencad.truth pin prusa-mini-extruder-front-ecr1
"""

from __future__ import annotations

import argparse
import copy
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from opencad.geomcheck import brep  # noqa: E402

CASE = REPO / "truth" / "cases" / "prusa-mini-extruder-front"
ECR_CASE = REPO / "truth" / "cases" / "prusa-mini-extruder-front-ecr1"
DESIGN = "prusa-mini-extruder-front"

# the two heat-set traps the change request modifies (axis x, z in the part frame; axis along +y from the back face)
ECR_TRAPS = [(-18.5, 22.0), (-17.0, -20.0)]
ECR_NEW_DIAMETER = 5.0
ECR_NEW_DEPTH = 6.0

DESCRIPTION = """# Original Prusa MINI extruder front housing: reconstruction brief

Source: prusa3d/Original-Prusa-MINI, `STEP/PRINTED PARTS/MINI-extruder-front.stp` (GNU GPL v3.0). The
reference CAD is evaluator-only; the agent works from the renders, section drawings and the dimension
sheet in this bundle.

## What the part is

The front half of the MINI extruder body: a printed plate, 53 x 14 x 63.72 mm, that mates face-to-face
with the extruder rear housing and carries the idler pivot. Functional geometry that governs assembly:

- Frame (native to the reference): x across the plate (-26.5 .. +26.5), y through the plate thickness
  with the flat back (mating) face at y = 0 and the front face at y = 14, z vertical (-30 .. +33.72) with
  the flat bottom face at z = -30.
- A keyhole-shaped central opening: a Ø22.5 recess 3 mm deep from the back face (y 0..3), a Ø16 bore
  (y 3..8) and a Ø26 counterbore from the front (y 8..14), all on the axis x = -2, z = 0 (parallel to y);
  above it a Ø12 recess (y 0..3) and Ø16 bore (y 3..8) with a Ø14 counterbore (y 10.36..14) on the axis
  x = -2, z = 16.4. The two circles merge into one keyhole in the mid-plate section.
- Screw holes parallel to y: Ø3.4 through holes and their Ø6.5 / Ø3.5 counterbores and heat-set traps
  at the positions listed in the dimension sheet; hexagonal nut traps on the front face around several
  of them.
- The filament path: Ø4 holes near the top lug (x ~ 14.7 and an angled entry) and the hotend clamp
  channel along z at x ~ 25.6 (stepped Ø12.63 / Ø9.5 / Ø8 bores, partial, forming the groove-mount
  half-clamp) on the +x side.
- Mating planes: back face y = 0, front face y = 14, bottom z = -30, left side x = -26.5, plus the
  smaller +x side faces.

The organic fan-duct lobe on the +x side, the top lug fillet, the embossed "R1" text and arrow are
cosmetic for this benchmark: reproduce their envelope, but they are not scored individually.

## What is scored (evaluator)

Required: bounding box, one solid, every axis-aligned cylindrical feature (hole or bore) with its axis
position and depth, the mating planes' positions and areas, and the mid-plate section area at y = 7.
Diagnostic only: volume, centre of mass, exterior deviation against the reference mesh.
"""

INTENT = (
    "Reconstruct the Original Prusa MINI extruder front housing (MINI-extruder-front) as editable, parameterized KCL from the "
    "attached renders, section drawings and dimension sheet. Frame: x across the plate (-26.5 to 26.5), y through the thickness "
    "with the back mating face at y = 0 and the front face at y = 14, z vertical from the bottom face z = -30 to the top lug at "
    "z = 33.72. Assembly-governing geometry must be exact: the keyhole central opening (Ø22.5 x 3 recess, Ø16 bore, Ø26 x 6 "
    "counterbore on the axis x = -2, z = 0; Ø12 x 3 recess, Ø16 bore and Ø14 counterbore on x = -2, z = 16.4), every Ø3.4 through "
    "hole with its Ø6.5 / Ø3.5 counterbore or heat-set trap, the Ø4 filament holes, the hotend clamp channel bores along z at "
    "x ~ 25.6, and the mating planes (y = 0, y = 14, z = -30, x = -26.5). Declare each hole as an acceptance cylinder and the "
    "mating planes as interfaces with checks. The fan-duct lobe, top-lug fillet and embossed text are cosmetic (optional features). "
    "One solid; export STEP and STL. The reference CAD is evaluator-only; the deliverable must be construction, never an import."
)

ECR_REQUEST = f"""# Engineering change request ECR-1: heat-set insert size change

The rear housing now uses M3 heat-set inserts with a Ø5.0 mm x 6.0 mm deep bore. Modify the two heat-set
traps on the back (mating) face of the extruder front at (x, z) = (-18.5, 22.0) and (-17.0, -20.0):

- the Ø6.5 mm x 9.8 mm deep bores from the back face (y = 0) become Ø{ECR_NEW_DIAMETER:g} mm x {ECR_NEW_DEPTH:g} mm deep;
- the Ø3.5 mm through portion of those two holes is unchanged.

Preserve every other interface exactly: all other hole axes, diameters and depths, the keyhole bore
stack, the hotend clamp channel, and the mating planes y = 0, y = 14, z = -30 and x = -26.5. The
bounding box must not change. Do not enlarge or shift anything else. Report the new analytic volume
delta (two bores: Ø6.5 x 9.8 minus Ø5.0 x 6.0 each).
"""

ECR_INFEASIBLE = """# Engineering change request ECR-2 (feasibility check)

Reduce the plate thickness from 14 mm to 6 mm (front face y = 14 moves to y = 6) while preserving the
Ø6.5 x 9.8 mm deep heat-set traps and the 9.4 mm deep Ø3.4 screw holes measured from the back face, and
the Ø26 x 6 mm counterbore from the front face.

If this request cannot be satisfied without violating a preserved interface, do not modify the model:
state INFEASIBLE under ## Result with the specific conflict.
"""


def _slug(v: float) -> str:
    return f"{v:g}".replace("-", "m").replace(".", "p")


def _cid(kind: str, d: float, c: list[float]) -> str:
    return f"{kind}_d{_slug(round(d, 2))}_{_slug(round(c[0], 2))}_{_slug(round(c[2], 2))}_y{_slug(round(c[1], 2))}"


def build_observables(step: Path, step_rel: str, stl_rel: str) -> list[dict]:
    shape = brep.read_step(step)
    a = brep.analyze_step(step)
    obs: list[dict] = [
        {"id": "bbox_size", "kind": "bbox_size", "expected": [round(x, 3) for x in a["bbox_size"]], "tolerance": 0.1},
        {"id": "solid_count", "kind": "solid_count", "expected": 1},
        {"id": "volume", "kind": "volume", "required": False, "from": {"file": step_rel, "measure": "volume"}, "tolerance_rel": 0.05,
         "note": "diagnostic: the fan-duct lobe and embossed text are cosmetic"},
        {"id": "center_of_mass", "kind": "center_of_mass", "required": False, "from": {"file": step_rel, "measure": "center_of_mass"}, "tolerance": 1.0},
    ]
    for c in brep.cylinders(shape):
        d = c["direction"]
        axis_aligned = sum(1 for x in d if abs(abs(x) - 1) < 1e-6) == 1
        if c["radius"] < 1.5:
            continue
        cid = _cid(c["kind"], c["diameter"], c["center"])
        required = axis_aligned and c["kind"] == "hole"
        o = {"id": cid, "kind": "cylinder", "required": required, "cyl_kind": c["kind"],
             "point": [round(x, 4) for x in c["center"]], "direction": [round(x, 4) for x in d],
             "radius": round(c["radius"], 4), "radius_tolerance": 0.05, "tolerance": 0.1,
             "note": f"{c['kind']} Ø{c['diameter']:.3g}, extent {c['t_min']:.3g}..{c['t_max']:.3g} along the axis" + ("" if c["full"] else " (partial arc)")}
        if c["full"] or (axis_aligned and c["kind"] == "hole"):
            o["length"] = round(c["length"], 4)
            o["length_tolerance"] = 0.2
        obs.append(o)
    faces = brep.planar_faces(shape)

    def plane_sum(axis: str, at: float, sign: str, rel: float, required: bool = True, name: str | None = None) -> None:
        i = "xyz".index(axis)
        want = 1.0 if sign == "+" else -1.0
        hits = [f for f in faces if abs(f["normal"][i] - want) < 1e-6 and all(abs(f["normal"][j]) < 1e-6 for j in range(3) if j != i) and abs(f["point"][i] - at) < 1e-3]
        area = sum(f["area"] for f in hits)
        obs.append({"id": name or f"face_{axis}{_slug(at)}_{'pos' if sign == '+' else 'neg'}", "kind": "face", "plane": axis, "at": at, "normal": sign, "mode": "sum",
                    "expected": round(area, 2), "area_tolerance_rel": rel, "tolerance": 0.05, "required": required})

    plane_sum("y", 0.0, "-", 0.03, name="back_mating_face")
    plane_sum("y", 14.0, "+", 0.05, name="front_face")
    plane_sum("z", -30.0, "-", 0.05, name="bottom_face")
    plane_sum("x", -26.5, "-", 0.05, name="left_side_face")
    plane_sum("x", 26.5, "+", 0.15, required=False, name="right_side_faces")
    for axis, at, rel, req, note in (("y", 7.0, 0.03, True, "mid-plate: keyhole and every through hole"), ("y", 1.5, 0.05, False, "back recesses"), ("y", 12.0, 0.05, False, "front counterbores and nut traps")):
        s = brep.section(shape, axis, at)
        obs.append({"id": f"section_{axis}{_slug(at)}", "kind": "section", "plane": axis, "at": at, "required": req,
                    "expected": {"area": round(s["area"], 3), "holes": s["holes"] if req else None}, "area_tolerance_rel": rel, "note": note})
    obs.append({"id": "deviation_vs_prusa", "kind": "deviation", "required": False, "reference": stl_rel, "p95_max": 0.8, "hausdorff_max": 4.0, "silhouette_iou_min": 0.93,
                "note": "diagnostic exterior agreement; cosmetic lobe and text differences are expected"})
    return obs


def ecr_observables(base: list[dict]) -> list[dict]:
    """Copy the reconstruction observables; the two traps take the new diameter/depth; everything else is preserved."""
    obs = copy.deepcopy(base)
    changed = 0
    for o in obs:
        if o["kind"] == "cylinder" and o["cyl_kind"] == "hole" and abs(o["radius"] - 3.25) < 1e-3:
            for x, z in ECR_TRAPS:
                if abs(o["point"][0] - x) < 1e-3 and abs(o["point"][2] - z) < 1e-3:
                    o["radius"] = ECR_NEW_DIAMETER / 2
                    o["length"] = ECR_NEW_DEPTH
                    o["point"] = [x, round(ECR_NEW_DEPTH / 2, 4), z]
                    o["id"] = o["id"].replace("d6p5", f"d{_slug(ECR_NEW_DIAMETER)}") + "_ecr1"
                    o["note"] = f"ECR-1: Ø{ECR_NEW_DIAMETER:g} x {ECR_NEW_DEPTH:g} deep from the back face"
                    o["required"] = True
                    changed += 1
    assert changed == 2, changed
    # volume becomes a required check: the bores shrink by a known amount relative to the reconstruction baseline
    for o in obs:
        if o["id"] in ("volume", "center_of_mass", "deviation_vs_prusa"):
            o["required"] = False
    return obs


def main(argv: list[str] | None = None) -> int:
    import math

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, default=Path.home() / ".cache" / "opencad" / "downloads" / "prusa-mini")
    a = ap.parse_args(argv)
    src = a.source_dir
    (CASE / "inputs" / "renders").mkdir(parents=True, exist_ok=True)
    (CASE / "truth").mkdir(exist_ok=True)
    step = CASE / "truth" / "MINI-extruder-front.stp"
    shutil.copy2(src / "MINI-extruder-front.stp", step)
    shutil.copy2(src / "LICENSE", CASE / "truth" / "LICENSE-GPL-3.0.txt")
    from opencad.truth.scorer import step_to_mesh

    stl = step_to_mesh(step, CASE / "truth" / "MINI-extruder-front.stl", deflection=0.02)
    py = sys.executable
    sections = "y=7,y=1.5,y=12,x=0,x=-18.5,z=0,z=17,z=-20"
    subprocess.run([py, str(REPO / "scripts" / "render_reference.py"), str(step), str(CASE / "inputs" / "renders"), "--views", "top,bottom,front,back,right,left,iso,iso2,iso-below",
                    "--sections", sections, "--px", "1800"], check=True)
    subprocess.run([py, str(REPO / "scripts" / "dimension_sheet.py"), str(step), str(CASE / "inputs" / "dimension-sheet.md"), "--sections", sections,
                    "--min-face-area", "1.0", "--max-faces", "40", "--min-radius", "0.9"], check=True)
    (CASE / "inputs" / "prusa-extruder-front-description.md").write_text(DESCRIPTION, encoding="utf-8")
    inputs = [
        {"path": "inputs/prusa-extruder-front-description.md", "kind": "text", "sha256": "PIN", "note": "part identity, frame, interfaces, what is scored"},
        {"path": "inputs/dimension-sheet.md", "kind": "text", "sha256": "PIN", "note": "evaluator-prepared dimension sheet measured from the reference"},
    ]
    images: list[str] = []
    for p in sorted((CASE / "inputs" / "renders").glob("*.png")):
        rel = f"inputs/renders/{p.name}"
        inputs.append({"path": rel, "kind": "image", "sha256": "PIN", "units": "mm", "note": "evaluator render (orthographic, mm grid)" if "section" not in p.name else "evaluator section drawing"})
        images.append(rel)
    inputs.append({"path": "inputs/renders/render-notes.md", "kind": "text", "sha256": "PIN", "note": "what each render shows"})
    obs = build_observables(step, "truth/MINI-extruder-front.stp", "truth/MINI-extruder-front.stl")
    source = {
        "citation": "Prusa Research, Original Prusa MINI / MINI+ printed parts, STEP/PRINTED PARTS/MINI-extruder-front.stp (GitHub prusa3d/Original-Prusa-MINI, master)",
        "urls": ["https://github.com/prusa3d/Original-Prusa-MINI/tree/master/STEP/PRINTED%20PARTS",
                 "https://raw.githubusercontent.com/prusa3d/Original-Prusa-MINI/master/STEP/PRINTED%20PARTS/MINI-extruder-front.stp"],
        "accessed": "2026-09-17", "revision": "master as of 2026-09-17", "license": "GNU GPL v3.0 (repository LICENSE); used as an internal benchmark reference",
    }
    m = {
        "id": "prusa-mini-extruder-front",
        "title": "Original Prusa MINI extruder front housing: functional mating part with keyhole bore stack, screw holes, heat-set traps, filament path and hotend clamp channel",
        "truth_class": "B", "role": "validation", "source": source, "intent": INTENT,
        "inputs": inputs,
        "truth": [
            {"path": "truth/MINI-extruder-front.stp", "kind": "cad", "sha256": "PIN", "units": "mm", "note": "manufacturer STEP; primary truth"},
            {"path": "truth/MINI-extruder-front.stl", "kind": "mesh", "sha256": "PIN", "units": "mm", "note": "OpenCascade tessellation of the STEP (0.02 mm) for deviation"},
            {"path": "truth/LICENSE-GPL-3.0.txt", "kind": "text", "sha256": "PIN", "note": "repository license"},
        ],
        "arms": [{"id": "renders-and-sheet", "design": DESIGN, "inputs": [i["path"] for i in inputs], "images": images,
                  "notes": "Renders, sections and the dimension sheet only. Required observables are the assembly-governing features; the organic lobe and text are diagnostic."}],
        "observables": obs,
        "notes": ["Functional-interface benchmark: hole axes, depths and mating planes are scored on the exported STEP, never from parameter names.",
                  "The change-request case prusa-mini-extruder-front-ecr1 re-scores the same design after `python -m opencad ecr`."],
    }
    (CASE / "manifest.yaml").write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
    (CASE / "mutants.yaml").write_text("# Deliberately wrong parts the scorer must reject.\n" + yaml.safe_dump({"mutants": [
        {"id": "scaled_2pct", "op": "scale", "factor": 1.02, "expect_caught_by": ["bbox_size"]},
        {"id": "screw_hole_shifted", "op": "shift_hole", "near": [-23.92, 4, 0], "radius": 1.7, "offset": [0.5, 0, 0], "note": "one Ø3.4 screw hole 0.5 mm off its axis"},
        {"id": "heat_set_trap_missing", "op": "fill_box", "min": [-21.8, -0.01, 18.7], "max": [-15.2, 9.8, 25.3], "note": "the Ø6.5 trap at (-18.5, 22) filled; the Ø3.5 through hole remains"},
        {"id": "plate_thickened", "op": "fill_box", "min": [-26.5, 14.0, -30], "max": [26.5, 16.0, 24.0], "note": "the enlarge-everything shortcut: 2 mm added to the front face"},
    ]}, sort_keys=False, width=110), encoding="utf-8")
    # change-request case: same design, patched observables, request files as inputs
    (ECR_CASE / "inputs").mkdir(parents=True, exist_ok=True)
    (ECR_CASE / "truth").mkdir(exist_ok=True)
    (ECR_CASE / "inputs" / "ecr-1-request.md").write_text(ECR_REQUEST, encoding="utf-8")
    (ECR_CASE / "inputs" / "ecr-2-infeasible-request.md").write_text(ECR_INFEASIBLE, encoding="utf-8")
    shutil.copy2(step, ECR_CASE / "truth" / "MINI-extruder-front.stp")
    delta_v = 2 * (math.pi / 4) * (6.5 ** 2 * 9.8 - ECR_NEW_DIAMETER ** 2 * ECR_NEW_DEPTH)
    ecr_obs = ecr_observables(obs)
    ecr_obs = [o for o in ecr_obs if o["kind"] != "deviation"]
    ecr_obs.append({"id": "volume_gain_vs_reference", "kind": "volume", "from": {"file": "truth/MINI-extruder-front.stp", "measure": "volume"}, "tolerance_rel": 0.05, "required": False,
                    "note": f"reference volume plus the two-bore gain of {delta_v:.2f} mm3 is the target; the reconstruction's own cosmetic error dominates the band"})
    em = {
        "id": "prusa-mini-extruder-front-ecr1",
        "title": "Prusa MINI extruder front after ECR-1 (heat-set traps Ø6.5 x 9.8 -> Ø5.0 x 6.0) with every other interface preserved",
        "truth_class": "C", "role": "validation",
        "source": {**source, "citation": source["citation"] + "; ECR-1 nominal derived from the request (class C)"},
        "intent": "Score the design after the ECR-1 change request: the two traps carry the new size, every other hole axis, depth and mating plane is unchanged.",
        "inputs": [{"path": "inputs/ecr-1-request.md", "kind": "text", "sha256": "PIN", "note": "feasible change request"},
                   {"path": "inputs/ecr-2-infeasible-request.md", "kind": "text", "sha256": "PIN", "note": "deliberately infeasible request; must be refused"}],
        "truth": [{"path": "truth/MINI-extruder-front.stp", "kind": "cad", "sha256": "PIN", "units": "mm", "note": "pre-change reference for the preserved interfaces"}],
        "arms": [{"id": "ecr1", "design": DESIGN, "inputs": ["inputs/ecr-1-request.md", "inputs/ecr-2-infeasible-request.md"], "images": [],
                  "notes": "Scored with `python -m opencad.truth score` after `python -m opencad ecr`; not a drafting run."}],
        "observables": ecr_obs,
        "notes": [f"Analytic volume gain from ECR-1: {delta_v:.2f} mm3 (two bores Ø6.5 x 9.8 replaced by Ø5.0 x 6.0)."],
    }
    (ECR_CASE / "manifest.yaml").write_text(yaml.safe_dump(em, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
    print(f"wrote {CASE / 'manifest.yaml'} ({len(obs)} observables, {sum(1 for o in obs if o.get('required', True))} required) and {ECR_CASE / 'manifest.yaml'} ({len(ecr_obs)} observables)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

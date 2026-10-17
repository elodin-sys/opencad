#!/usr/bin/env python
"""Build the `nist-am-test-artifact` truth case from NIST's published package (OpenCascade, no Zoo).

Truth: NIST Test Artifact_ver3b.step (and the 2013 online STL translated into the STEP frame).
Inputs for the agent: the engineering drawing pages, the paper's feature text, evaluator renders with
a mm grid, section drawings, and a dimension sheet derived from the reference. Observables are
feature-by-feature: every cylinder axis, every staircase step, the ramp plane, the diamond sides,
sections with region matching, and deviation. Run `python -m opencad.truth pin nist-am-test-artifact` after.

  python scripts/derive_nist_am_truth.py --source-dir ~/.cache/opencad/downloads/nist-am
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import trimesh
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from opencad.geomcheck import brep  # noqa: E402

CASE = REPO / "truth" / "cases" / "nist-am-test-artifact"
STL_OFFSET = (-70.71070098876953, -70.71070098876953, -10.0)

DESCRIPTION = """# NIST Additive Manufacturing Test Artifact: published description (excerpts)

Source: S. P. Moylan, J. A. Slotwinski, A. L. Cooke, K. K. Jurrens, M. A. Donmez, "An Additive
Manufacturing Test Artifact", J. Res. NIST 119 (2014), doi:10.6028/jres.119.017, section 7 and Fig. 8;
NIST's artifact page (public domain, US Government work). The engineering drawing (Fig. 8, two pages)
is attached as `drawing-01.png` and `drawing-02.png`; its GD&T tolerance boxes read "xx" on purpose.

## Overview (paper, section 7)

"The artifact is comprised of several features with simple geometry, atop or within a diamond-shaped
base." "The part should be built in the center of the building platform with the 4 mm pins and holes
aligned along the machine x- and y-axes. It is 17 mm tall and has a volume of approximately 101 000
mm3."

Feature list (Fig. 7 labels): Top Surface; Center Hole; Central Cylinders; 4 mm Holes (x4); 4 mm Pins
(x16); Staircases (two) with Vertical Surfaces; Ramp; Lateral Features; Fine Features: Negative (x5
holes) and Positive (x5 pins), plus neighbouring rectangular bosses/holes; Outer Edges.

## Datum frame used for this reconstruction

- 7.1 "The top surface of the part is the primary datum feature defining the z-direction and the
  z-origin of the measurement coordinate system." So z = 0 on the top surface, +z toward the pin tips;
  the diamond base extends to z = -10 (10 mm thick) and the tallest features reach z = +7 (17 mm total).
- 7.2 "The center hole in the part is the secondary datum feature defining the x- and y-origin." So
  the Ø10 through hole is on the z axis at x = y = 0.
- 7.3 "The right-most hole in the top view of the part is the tertiary datum feature defining the
  x-direction." So +x points from the centre toward the 4 mm hole at x = +60, and the 4 mm pin and
  hole rows lie along +-x and +-y.
- The diamond base is a 100 mm square rotated 45 deg about z: its corners lie on the x and y axes.

## Feature notes (paper, sections 7.2-7.9)

- Center hole and central cylinders: a round through hole on the z axis inside two concentric round
  bosses that rise from the top surface (7.6: "round or arced bosses ... concentric features").
- Pins and holes (7.3): sixteen Ø4 pins standing on the top surface along the +-x and +-y axes at
  20, 30, 40 and 50 mm from centre; four Ø4 holes through the base at 60 mm from centre on the same
  axes.
- Staircases (7.4): two L-shaped staircases with 1 mm steps ("the distance between steps (1 mm)");
  one rises above the top surface in the (-x, +y) quadrant, the other descends into the base in the
  (-x, -y) quadrant. Section F-F / G-G on drawing page 2 give the step heights 3, 4, 5, 6, 7 mm from
  datum A. Step treads are 10 mm squares.
- Ramp (7.7): "designed to slope constantly with a 1 mm rise over a 25 mm run", with "2.5 mm flat
  landings at its top and bottom", in the (+x, -y) quadrant along the diagonal, rising from 1 mm to
  2 mm above the top surface (drawing section C-C).
- Lateral features (7.8): on one outer edge (the (-x, +y) diamond side) a set of shallow lateral
  cavities and bosses of different cross-sections (round Ø3 x 3 deep and Ø6 x 5 deep holes, square,
  diamond, hexagon and lens shapes) cut into the vertical side face at mid-height of the base
  (drawing section A-A). Reproduce the round ones exactly; the others as drawn.
- Fine features (7.9): "the widths of the fine features descend from 2 mm to 0.25 mm from the center
  of the set outward ... All features are 2 mm tall or deep." Round pins (Ø2, 1.5, 1, 0.5, 0.25) on
  the top surface along the diagonal in the (+x, +y) quadrant and matching round holes on the other
  side of that diagonal (section D-D); neighbouring rectangular bosses and slots of widths 2 to 0.25
  along the diagonal further out (section E-E).
- Outer edges (7.5): three plain 45 deg diamond sides; the fourth carries the lateral features.

The renders (`renders/*.png`, orthographic with a mm grid) and section drawings show exactly where
each feature sits. `dimension-sheet.md` lists every planar face level, cylindrical feature axis,
diameter and depth, and section summary measured from the reference geometry by the evaluator. The
reference CAD itself is not available to the design agent.
"""

INTENT = (
    "Reconstruct the NIST Additive Manufacturing Test Artifact (Moylan et al. 2014, Fig. 8) as editable, "
    "parameterized KCL from the attached drawing, paper excerpts, renders, section drawings and dimension sheet. "
    "Frame: origin at the centre of the top surface, z = 0 on the top surface with +z toward the pin tips (the base "
    "extends to z = -10, features to z = +7), the Ø10 centre hole on the z axis, +x toward the Ø4 hole at x = +60; "
    "the four rows of Ø4 pins (20, 30, 40, 50) and the four Ø4 holes (60) lie on the +-x and +-y axes; the diamond "
    "base is a 100 mm square rotated 45 deg (corners on the axes at 70.71). Model every feature at its stated size and "
    "position: centre hole and two concentric central cylinders, 16 pins and 4 holes, both L-shaped staircases with "
    "1 mm steps and 10 mm treads, the 1-in-25 ramp with 2.5 mm landings, the lateral cavities and bosses on one side, "
    "the five fine pins and five fine holes (Ø2 to Ø0.25, 2 mm tall/deep) and the fine rectangular bosses and slots. "
    "Small features are scored individually: a correct base cannot compensate for a missing pin. One solid; export "
    "STEP and STL. The reference CAD is evaluator-only; the deliverable must be construction, never an import."
)


def _slug(v: float) -> str:
    s = f"{v:g}".replace("-", "m").replace(".", "p")
    return s


def _id(kind: str, d: float, c: list[float]) -> str:
    return f"{kind}_d{_slug(d)}_{_slug(round(c[0], 2))}_{_slug(round(c[1], 2))}"


def build_manifest(step: Path, stl_rel: str, step_rel: str, inputs: list[dict], images: list[str]) -> dict:
    shape = brep.read_step(step)
    a = brep.analyze_step(step)
    obs: list[dict] = [
        {"id": "bbox_size", "kind": "bbox_size", "expected": [round(x, 4) for x in a["bbox_size"]], "tolerance": 0.05},
        {"id": "volume", "kind": "volume", "from": {"file": step_rel, "measure": "volume"}, "tolerance_rel": 0.003,
         "note": "paper: approximately 101 000 mm3; reference STEP 100987.06"},
        {"id": "solid_count", "kind": "solid_count", "expected": 1},
        {"id": "center_of_mass", "kind": "center_of_mass", "from": {"file": step_rel, "measure": "center_of_mass"}, "tolerance": 0.15},
    ]
    # every cylindrical feature, individually
    cyls = brep.cylinders(shape)
    for c in cyls:
        cid = _id(c["kind"], c["diameter"], c["center"])
        obs.append({
            "id": cid, "kind": "cylinder", "cyl_kind": c["kind"],
            "point": [round(x, 4) for x in c["center"]], "direction": [round(x, 4) for x in c["direction"]],
            "radius": round(c["radius"], 4), "radius_tolerance": 0.02, "tolerance": 0.05,
            "length": round(c["length"], 4), "length_tolerance": 0.05,
            "t_range": [round(c["t_min"] - sum((p - q) * d for p, q, d in zip(c["center"], c["point"], c["direction"])), 4),
                        round(c["t_max"] - sum((p - q) * d for p, q, d in zip(c["center"], c["point"], c["direction"])), 4)],
            "note": f"{c['kind']} Ø{c['diameter']:g}, {c['length']:g} long along {[round(x, 3) for x in c['direction']]}",
        })
    obs.append({"id": "count_pins_d4", "kind": "cylinder_count", "radius": 2.0, "cyl_kind": "pin", "expected": 16, "radius_tolerance": 0.02, "direction": [0, 0, 1]})
    obs.append({"id": "count_holes_d4", "kind": "cylinder_count", "radius": 2.0, "cyl_kind": "hole", "expected": 4, "radius_tolerance": 0.02, "direction": [0, 0, 1]})
    obs.append({"id": "count_fine_pins", "kind": "cylinder_count", "radius": 0.125, "cyl_kind": "pin", "expected": 1, "radius_tolerance": 0.01, "note": "the smallest pin, Ø0.25"})
    obs.append({"id": "count_fine_holes", "kind": "cylinder_count", "radius": 0.125, "cyl_kind": "hole", "expected": 1, "radius_tolerance": 0.01, "note": "the smallest hole, Ø0.25"})
    # planes: ramp and the four diamond sides
    faces = brep.planar_faces(shape)
    ramp = max((f for f in faces if 0.9 < f["normal"][2] < 0.9999), key=lambda f: f["area"])
    obs.append({"id": "ramp_plane", "kind": "plane", "point": [round(x, 4) for x in ramp["centroid"]], "direction": [round(x, 5) for x in ramp["normal"]],
                "expected": round(ramp["area"], 2), "area_tolerance_rel": 0.03, "tolerance": 0.05, "note": "1 mm rise over 25 mm run; the 2.5 mm landings are separate faces"})
    sides = [f for f in faces if abs(f["normal"][2]) < 1e-6 and abs(abs(f["normal"][0]) - 0.7071) < 1e-3 and f["area"] > 500]
    for f in sorted(sides, key=lambda f: (round(f["normal"][0], 2), round(f["normal"][1], 2))):
        nx, ny = f["normal"][0], f["normal"][1]
        name = f"side_{'px' if nx > 0 else 'mx'}{'py' if ny > 0 else 'my'}"
        obs.append({"id": name, "kind": "plane", "point": [round(x, 4) for x in f["centroid"]], "direction": [round(x, 5) for x in f["normal"]],
                    "expected": round(f["area"], 2), "area_tolerance_rel": 0.02, "tolerance": 0.05,
                    "note": "diamond side; the (-x,+y) side carries the lateral features so its plain area is smaller"})
    # faces: top, bottom, staircase steps, ramp landings
    obs.append({"id": "top_surface", "kind": "face", "plane": "z", "at": 0.0, "normal": "+", "mode": "sum", "expected": None, "tolerance": 0.05,
                "note": "primary datum; area is not scored (a split top face is fine), only its presence"})
    bottom = [f for f in faces if abs(f["point"][2] + 10) < 1e-6 and f["normal"][2] < -0.99]
    obs.append({"id": "bottom_face", "kind": "face", "plane": "z", "at": -10.0, "normal": "-", "mode": "sum", "expected": round(sum(f["area"] for f in bottom), 2),
                "area_tolerance_rel": 0.005, "tolerance": 0.05})
    for f in faces:
        if f["normal"][2] > 0.99 and abs(f["area"] - 100) < 0.5 and abs(f["point"][2]) > 2.5:
            z = round(f["point"][2], 3)
            obs.append({"id": f"step_{'up' if z > 0 else 'down'}_z{_slug(z)}", "kind": "face", "plane": "z", "at": z, "normal": "+",
                        "center": [round(f["centroid"][0], 3), round(f["centroid"][1], 3)], "expected": 100.0, "area_tolerance_rel": 0.01, "tolerance": 0.2,
                        "note": "staircase tread, 10 x 10"})
    for f in faces:
        if f["normal"][2] > 0.99 and abs(f["area"] - 12.5) < 0.05:
            z = round(f["point"][2], 3)
            obs.append({"id": f"ramp_landing_z{_slug(z)}", "kind": "face", "plane": "z", "at": z, "normal": "+",
                        "center": [round(f["centroid"][0], 3), round(f["centroid"][1], 3)], "expected": 12.5, "area_tolerance_rel": 0.02, "tolerance": 0.2})
    # sections with region matching
    for axis, at, note in (("z", 1.0, "fine pins, Ø4 pins, up-staircase, central cylinder, ramp"), ("z", -1.0, "fine holes, centre hole, down-staircase, lateral features"),
                           ("z", 5.0, "up-staircase upper treads, Ø4 pins, Ø15 boss"), ("z", -5.0, "down-staircase, Ø4 holes, lateral cavities"), ("x", 0.0, "centre hole and y-row pins"), ("y", 0.0, "centre hole and x-row pins")):
        s = brep.section(shape, axis, at)
        u, v = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[axis]
        regions = [{"center": [round(r["centroid"][u], 3), round(r["centroid"][v], 3)], "size": [round(r["bbox_max"][u] - r["bbox_min"][u], 3), round(r["bbox_max"][v] - r["bbox_min"][v], 3)]} for r in s["regions"]]
        obs.append({"id": f"section_{axis}{_slug(at)}", "kind": "section", "plane": axis, "at": at,
                    "expected": {"area": round(s["area"], 3), "loops": s["loops"], "holes": s["holes"], "regions": regions},
                    "area_tolerance_rel": 0.01, "tolerance": 0.25, "note": note})
    obs.append({"id": "deviation_vs_nist", "kind": "deviation", "reference": stl_rel, "p95_max": 0.1, "hausdorff_max": 0.6, "silhouette_iou_min": 0.985,
                "note": "NIST online STL translated into the STEP frame (matches the STEP to p95 0.005)"})
    m = {
        "id": "nist-am-test-artifact",
        "title": "NIST Additive Manufacturing Test Artifact (Moylan et al. 2014): diamond base with centre hole, concentric bosses, 16 pins, 4 holes, two staircases, ramp, lateral and fine features",
        "truth_class": "B",
        "role": "validation",
        "source": {
            "citation": "S. P. Moylan, J. A. Slotwinski, A. L. Cooke, K. K. Jurrens, M. A. Donmez, An Additive Manufacturing Test Artifact, J. Res. NIST 119 (2014) 429-459, doi:10.6028/jres.119.017; NIST artifact download page",
            "urls": ["https://www.nist.gov/el/intelligent-systems-division-73500/production-systems-group/nist-additive-manufacturing-test",
                     "https://doi.org/10.6028/jres.119.017",
                     "https://www.nist.gov/system/files/documents/2017/10/19/nist_test_artifact_ver3b.zip"],
            "accessed": "2026-09-17",
            "revision": "NIST Test Artifact_ver3b.step (2017-10-05) and NIST Test Artifact online.STL (2013-04-10); STL translated by (-70.7107, -70.7107, -10) into the STEP frame",
            "license": "US Government work, public domain (17 USC 105); NIST asks for acknowledgement",
        },
        "intent": INTENT,
        "inputs": inputs,
        "truth": [
            {"path": step_rel, "kind": "cad", "sha256": "PIN", "units": "mm", "note": "NIST design file, B-rep; primary truth"},
            {"path": stl_rel, "kind": "mesh", "sha256": "PIN", "units": "mm", "note": "NIST online STL translated into the STEP frame; deviation reference"},
            {"path": "truth/test-artifact-inspection-sheet.xlsx", "kind": "table", "sha256": "PIN", "note": "NIST inspection worksheet (nominal measurements); evaluator-only"},
        ],
        "arms": [{
            "id": "drawing-renders-sheet",
            "design": "nist-am-test-artifact",
            "inputs": [i["path"] for i in inputs],
            "images": images,
            "notes": ("The drawing carries GD&T placeholders and leaves several sizes undimensioned; the renders (mm grid), section drawings and the "
                      "evaluator-prepared dimension sheet supply positions and sizes. The agent never sees the CAD. Every one of the 34 cylindrical "
                      "features, 10 staircase treads, the ramp and the diamond sides is a required observable."),
        }],
        "observables": obs,
        "notes": [
            "Feature-by-feature benchmark: small features have their own acceptance so a correct base cannot compensate for a missing pin.",
            "Frame is the STEP's own frame, which matches the paper's datum scheme (top surface z = 0, centre hole on z, +x toward the right-most Ø4 hole).",
            "The published STL is the same design as the STEP (p95 0.005 mm after translation).",
        ],
    }
    return m


MUTANTS = {"mutants": [
    {"id": "scaled_2pct", "op": "scale", "factor": 1.02, "expect_caught_by": ["bbox_size"], "note": "whole-part scale error"},
    {"id": "hole_shifted_0p7", "op": "shift_hole", "near": [60, 0, -5], "radius": 2.0, "offset": [0.7, 0, 0],
     "expect_caught_by": ["hole_d4_60_0"], "note": "the +x datum hole 0.7 mm off its axis: the campaign's canonical evaluator message"},
    {"id": "fine_pin_missing", "op": "cut_box", "min": [42.2, 6.85, 0.0], "max": [42.66, 7.3, 2.5],
     "expect_caught_by": ["pin_d0p25_42p43_7p07", "count_fine_pins"], "note": "the Ø0.25 pin removed: a visually convincing part missing its smallest feature"},
    {"id": "step_missing", "op": "fill_box", "min": [-42, 12, 3], "max": [-32, 22, 7], "note": "the z = 3 tread raised to z = 7 (staircase flattened)"},
    {"id": "ramp_flat", "op": "fill_box", "min": [9, -46, 1], "max": [46, -9, 2], "note": "ramp filled to its top landing level (no slope)"},
]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, default=Path.home() / ".cache" / "opencad" / "downloads" / "nist-am")
    a = ap.parse_args(argv)
    src = a.source_dir
    (CASE / "inputs" / "renders").mkdir(parents=True, exist_ok=True)
    (CASE / "truth").mkdir(exist_ok=True)
    step = CASE / "truth" / "nist-am-test-artifact.step"
    shutil.copy2(src / "NIST Test Artifact_ver3b.step", step)
    shutil.copy2(src / "test-artifact-inspection-sheet.xlsx", CASE / "truth" / "test-artifact-inspection-sheet.xlsx")
    stl = trimesh.load(src / "NIST Test Artifact online.STL", force="mesh")
    stl.apply_translation(STL_OFFSET)
    stl_path = CASE / "truth" / "nist-am-test-artifact-centred.stl"
    stl.export(stl_path)
    # agent inputs
    py = sys.executable
    subprocess.run([py, str(REPO / "scripts" / "pdf_pages.py"), str(src / "engineering-drawing.pdf"), str(CASE / "inputs"), "--dpi", "220", "--prefix", "drawing-"], check=True)
    subprocess.run([py, str(REPO / "scripts" / "render_reference.py"), str(step), str(CASE / "inputs" / "renders"), "--views", "top,bottom,front,right,iso,iso2,iso-below",
                    "--sections", "z=1,z=-1,z=5,z=-5,x=0,y=0", "--px", "1800"], check=True)
    subprocess.run([py, str(REPO / "scripts" / "dimension_sheet.py"), str(step), str(CASE / "inputs" / "dimension-sheet.md"), "--sections", "z=1,z=-1,z=5,z=-5,x=0,y=0",
                    "--min-face-area", "0.04", "--max-faces", "40"], check=True)
    (CASE / "inputs" / "nist-am-artifact-description.md").write_text(DESCRIPTION, encoding="utf-8")
    inputs = [
        {"path": "inputs/nist-am-artifact-description.md", "kind": "text", "sha256": "PIN", "note": "paper section 7 excerpts, datum frame, feature notes"},
        {"path": "inputs/drawing-01.png", "kind": "drawing", "sha256": "PIN", "units": "mm", "note": "Fig. 8 part 1: plan view with datums, sections A-A, B-B, C-C, D-D"},
        {"path": "inputs/drawing-02.png", "kind": "drawing", "sha256": "PIN", "units": "mm", "note": "Fig. 8 part 2: sections E-E (fine rectangular features), F-F and G-G (staircases)"},
        {"path": "inputs/dimension-sheet.md", "kind": "text", "sha256": "PIN", "note": "evaluator-prepared dimension sheet measured from the reference (face levels, cylinder axes, sections)"},
    ]
    images = ["inputs/drawing-01.png", "inputs/drawing-02.png"]
    for p in sorted((CASE / "inputs" / "renders").glob("*.png")):
        rel = f"inputs/renders/{p.name}"
        inputs.append({"path": rel, "kind": "image", "sha256": "PIN", "units": "mm", "note": "evaluator render of the reference (orthographic, mm grid)" if "section" not in p.name else "evaluator section drawing of the reference"})
        images.append(rel)
    inputs.append({"path": "inputs/renders/render-notes.md", "kind": "text", "sha256": "PIN", "note": "what each render shows"})
    m = build_manifest(step, "truth/nist-am-test-artifact-centred.stl", "truth/nist-am-test-artifact.step", inputs, images)
    (CASE / "manifest.yaml").write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
    (CASE / "mutants.yaml").write_text("# Deliberately wrong parts the scorer must reject (python -m opencad.truth mutate nist-am-test-artifact).\n"
                                       + yaml.safe_dump(MUTANTS, sort_keys=False, width=110), encoding="utf-8")
    print(f"wrote {CASE / 'manifest.yaml'} with {len(m['observables'])} observables; now run: python -m opencad.truth pin nist-am-test-artifact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

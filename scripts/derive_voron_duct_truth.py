#!/usr/bin/env python
"""Build the `voron-sb-duct` truth case: the Voron Stealthburner printhead front (Rapido V2 variant), a ducted housing.

Truth: solid 0 of CAD/Printheads/Stealthburner_Printhead_Rapido_V2.step (GPL-3.0), extracted with OpenCascade.
Interior observables carry the case: passage connectivity of each part-cooling duct (sealed by
morphological closing), separation of the two ducts, the hotend cavity, passage volumes, interior
section stations, and minimum wall thickness. Exterior agreement is diagnostic.

  python scripts/derive_voron_duct_truth.py --source-dir ~/.cache/opencad/downloads/voron
  python -m opencad.truth pin voron-sb-duct
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from opencad.geomcheck import assembly, brep  # noqa: E402
from opencad.truth.mutants import write_step, write_stl  # noqa: E402

CASE = REPO / "truth" / "cases" / "voron-sb-duct"
DESIGN = "voron-sb-duct"
PITCH, SEAL = 0.4, 3.2
PROBES = {
    "left_duct": ([-21.2, -14.4, 50.8], [-26.0, -10.0, 10.0]),
    "right_duct": ([22.0, -11.2, 43.6], [26.0, -10.0, 10.0]),
    "hotend_cavity": ([-13.6, -18.8, 26.4], [10.0, -18.0, 30.0]),
}

DESCRIPTION = """# Voron Stealthburner printhead front (Rapido V2 variant): ducted housing reconstruction brief

Source: VoronDesign/Voron-Stealthburner, `CAD/Printheads/Stealthburner_Printhead_Rapido_V2.step`, the
front (part-cooling duct) body (GPL-3.0). The reference CAD is evaluator-only; work from the renders,
the section drawings and the dimension sheet.

## What the part is

The front shell of the Stealthburner toolhead: a printed housing 71.07 x 27.40 x 59.13 mm that carries
two part-cooling air ducts, the hotend cavity and the hotend-fan opening. Frame (native to the
reference): x across the toolhead (-35.53 .. +35.53, symmetric), y from the flat back mating face at
y = 0 toward the front (negative y, to -27.40), z up from the nozzle end (z = 2.37) to the top (z = 61.5).

## Interior geometry that is scored (the section drawings show it; this text names it)

- Two part-cooling ducts, mirror images about x = 0. Each is a closed curved channel that starts at a
  rectangular fan inlet on the top face (about x -24..-17 / 17..24, y -23..-12, z ~ 56) and runs down the
  outside of the housing to the nozzle end, where it forks into two outlets that open downward and inward
  around z ~ 8..10 (see sections z = 10 and z = 20). At z = 45 each duct is a single channel about 8 x 19 mm
  (sections z = 45, z = 30); the duct wall is about 1 mm thick. The two ducts do not connect to each other.
- The hotend cavity: a rounded-rectangle pocket about 26 mm wide (x) and 35 mm tall (z 9..44), open to the
  back face (y = 0) and to the nozzle end, with the round hotend-fan opening on the front (see y = -12 and
  y = -20 sections and the front render).
- The screw holes and their bosses at the positions in the dimension sheet.

The evaluator checks connectivity inside the ducts (a probe near each fan inlet must reach a probe near
its outlets through air, with the ports sealed; a path around the outside does not count), that the two
ducts are separate, the hotend cavity, the air volume of each passage, the material area at the section
stations, and the minimum wall thickness (5th percentile of inward ray casts >= 0.75 mm). Exterior
volume and deviation are diagnostic only: styling surfaces, the embossed text and the fan grille are
cosmetic.
"""

INTENT = (
    "Reconstruct the Voron Stealthburner printhead front housing (Rapido V2 variant) as editable, parameterized KCL from the attached "
    "renders, section drawings and dimension sheet, in the reference frame (x symmetric about 0, back mating face y = 0 with the part "
    "extending to y = -27.4, z from 2.37 at the nozzle end to 61.5 at the top). The interior matters most: two mirrored closed part-cooling "
    "ducts from the top fan inlets down to the forked nozzle outlets (about 8 x 19 mm channels with ~1 mm walls, never connected to each "
    "other), the hotend cavity (about 26 x 35 mm, open to the back and the nozzle end) with the round hotend-fan opening on the front, and "
    "the screw holes. Declare the duct probe points as void probes, the sections as acceptance sections, the ducts as passages and the wall "
    "minimum as a thickness check. Cosmetic styling, text and grille are optional. One solid; export STEP and STL. Reference CAD is evaluator-only."
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, default=Path.home() / ".cache" / "opencad" / "downloads" / "voron")
    a = ap.parse_args(argv)
    (CASE / "inputs" / "renders").mkdir(parents=True, exist_ok=True)
    (CASE / "truth").mkdir(exist_ok=True)
    src_step = a.source_dir / "Stealthburner_Printhead_Rapido_V2.step"
    sols = brep.solids(brep.read_step(src_step))
    front = max(sols, key=lambda s: brep.volume_props(s)["volume"])
    step = write_step(front, CASE / "truth" / "sb-printhead-front.step")
    stl = write_stl(front, CASE / "truth" / "sb-printhead-front.stl", 0.02)
    shutil.copy2(a.source_dir / "LICENSE", CASE / "truth" / "LICENSE-GPL-3.0.txt")
    shape = brep.read_step(step)
    an = brep.analyze_step(step)
    py = sys.executable
    sections = "y=-5,y=-12,y=-20,z=10,z=20,z=30,z=45,z=55,x=0,x=-22,x=22"
    subprocess.run([py, str(REPO / "scripts" / "render_reference.py"), str(step), str(CASE / "inputs" / "renders"), "--views", "front,back,top,bottom,left,right,iso,iso2,iso-below",
                    "--sections", sections, "--px", "1800"], check=True)
    subprocess.run([py, str(REPO / "scripts" / "dimension_sheet.py"), str(step), str(CASE / "inputs" / "dimension-sheet.md"), "--sections", sections,
                    "--min-face-area", "2.0", "--max-faces", "30", "--min-radius", "1.2"], check=True)
    (CASE / "inputs" / "voron-duct-description.md").write_text(DESCRIPTION, encoding="utf-8")
    inputs = [{"path": "inputs/voron-duct-description.md", "kind": "text", "sha256": "PIN", "note": "part identity, frame, interior description, what is scored"},
              {"path": "inputs/dimension-sheet.md", "kind": "text", "sha256": "PIN", "note": "evaluator-prepared dimension sheet"}]
    images: list[str] = []
    for p in sorted((CASE / "inputs" / "renders").glob("*.png")):
        rel = f"inputs/renders/{p.name}"
        inputs.append({"path": rel, "kind": "image", "sha256": "PIN", "units": "mm", "note": "evaluator render" if "section" not in p.name else "evaluator section drawing (reveals the passages)"})
        images.append(rel)
    inputs.append({"path": "inputs/renders/render-notes.md", "kind": "text", "sha256": "PIN", "note": "what each render shows"})

    obs: list[dict] = [
        {"id": "bbox_size", "kind": "bbox_size", "expected": [round(x, 3) for x in an["bbox_size"]], "tolerance": 0.3},
        {"id": "solid_count", "kind": "solid_count", "expected": 1},
        {"id": "volume", "kind": "volume", "required": False, "from": {"file": "truth/sb-printhead-front.step", "measure": "volume"}, "tolerance_rel": 0.06, "note": "diagnostic: styling surfaces are cosmetic"},
    ]
    for name, (pa, pb) in PROBES.items():
        r = assembly.passage(stl, pa, pb, pitch=PITCH, seal_radius=SEAL)
        assert r["ok"], (name, r)
        obs.append({"id": f"passage_{name}", "kind": "passage", "point": pa, "point_b": pb, "pitch": PITCH, "seal_radius": SEAL,
                    "volume_min": round(r["passage_volume"] * 0.8, 1), "volume_max": round(r["passage_volume"] * 1.2, 1),
                    "note": f"air path {name}; reference passage volume {r['passage_volume']:.0f} mm3"})
    obs.append({"id": "ducts_separate", "kind": "passage", "point": PROBES["left_duct"][0], "point_b": PROBES["right_duct"][0], "pitch": PITCH, "seal_radius": SEAL,
                "expect_connected": False, "note": "the two part-cooling ducts must not share air"})
    for axis, at, rel, holes_req in (("y", -12.0, 0.06, True), ("y", -20.0, 0.08, False), ("z", 10.0, 0.08, False), ("z", 30.0, 0.08, False), ("z", 45.0, 0.08, False)):
        s = brep.section(shape, axis, at)
        exp = {"area": round(s["area"], 2)}
        if holes_req:
            exp["holes"] = s["holes"]
        obs.append({"id": f"section_{axis}{str(at).replace('-', 'm').replace('.0', '')}", "kind": "section", "plane": axis, "at": at, "expected": exp, "area_tolerance_rel": rel,
                    "note": f"material at the station: {s['loops']} loops, {s['holes']} holes in the reference"})
    th = assembly.thickness(stl, samples=8000, max_thickness=8.0)
    obs.append({"id": "wall_min", "kind": "thickness", "stat": "p05", "min": 0.75, "samples": 8000, "max_thickness": 8.0,
                "note": f"reference p05 {th['p05']:.2f} mm, p50 {th['p50']:.2f} mm"})
    for c in brep.cylinders(shape):
        if not c["full"] or c["radius"] < 1.2 or sum(1 for x in c["direction"] if abs(abs(x) - 1) < 1e-6) != 1:
            continue
        cid = f"{c['kind']}_d{c['diameter']:.3g}_{c['center'][0]:.1f}_{c['center'][1]:.1f}_{c['center'][2]:.1f}".replace("-", "m").replace(".", "p")
        obs.append({"id": cid, "kind": "cylinder", "cyl_kind": c["kind"], "point": [round(x, 3) for x in c["center"]], "direction": [round(x, 4) for x in c["direction"]],
                    "radius": round(c["radius"], 3), "radius_tolerance": 0.1, "tolerance": 0.2, "note": f"{c['kind']} Ø{c['diameter']:.3g}, {c['length']:.3g} long"})
    obs.append({"id": "deviation_vs_voron", "kind": "deviation", "required": False, "reference": "truth/sb-printhead-front.stl", "p95_max": 1.0, "hausdorff_max": 5.0, "silhouette_iou_min": 0.9})
    m = {
        "id": "voron-sb-duct",
        "title": "Voron Stealthburner printhead front (Rapido V2): two part-cooling ducts, hotend cavity, fan opening; interior connectivity, passage volumes, sections and wall minimum",
        "truth_class": "B", "role": "validation",
        "source": {"citation": "VoronDesign, Voron-Stealthburner, CAD/Printheads/Stealthburner_Printhead_Rapido_V2.step (front body, solid 0)",
                   "urls": ["https://github.com/VoronDesign/Voron-Stealthburner/tree/main/CAD", "https://raw.githubusercontent.com/VoronDesign/Voron-Stealthburner/main/CAD/Printheads/Stealthburner_Printhead_Rapido_V2.step"],
                   "accessed": "2026-09-17", "revision": "main as of 2026-09-17 (release 1.0, 2024-07-04)", "license": "GNU GPL v3.0"},
        "intent": INTENT,
        "inputs": inputs,
        "truth": [{"path": "truth/sb-printhead-front.step", "kind": "cad", "sha256": "PIN", "units": "mm", "note": "front duct body extracted from the printhead STEP"},
                  {"path": "truth/sb-printhead-front.stl", "kind": "mesh", "sha256": "PIN", "units": "mm", "note": "OpenCascade tessellation (0.02 mm) for passages, thickness and deviation"},
                  {"path": "truth/LICENSE-GPL-3.0.txt", "kind": "text", "sha256": "PIN", "note": "repository license"}],
        "arms": [{"id": "renders-sections-sheet", "design": DESIGN, "inputs": [i["path"] for i in inputs], "images": images,
                  "notes": "Exterior renders plus section drawings that reveal the passages; hidden geometry the inputs do not show is not penalised."}],
        "observables": obs,
        "notes": ["Interior-first benchmark: passages are checked by voxel flood fill on the exported STL with ports sealed by morphological closing (radius 3.2 mm).",
                  "Exterior styling is diagnostic (optional volume and deviation)."],
    }
    (CASE / "manifest.yaml").write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
    (CASE / "mutants.yaml").write_text("# Deliberately wrong ducts the scorer must reject.\n" + yaml.safe_dump({"mutants": [
        {"id": "scaled_2pct", "op": "scale", "factor": 1.02, "expect_caught_by": ["bbox_size"]},
        {"id": "left_duct_blocked", "op": "fill_box", "min": [-30, -27, 28], "max": [-14, -4, 32], "expect_caught_by": ["passage_left_duct"], "note": "a plug across the left duct at z 28..32"},
        {"id": "right_duct_missing", "op": "fill_box", "min": [14, -27, 6], "max": [33, -4, 57], "expect_caught_by": ["passage_right_duct"], "note": "the right duct filled solid"},
        {"id": "left_wall_opened", "op": "cut_box", "min": [-34, -27.5, 25], "max": [-27.5, -5, 35], "expect_caught_by": ["passage_left_duct"], "note": "outer duct wall removed; the passage leaks to the exterior"},
    ]}, sort_keys=False, width=110), encoding="utf-8")
    print(f"wrote {CASE / 'manifest.yaml'} with {len(obs)} observables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Independent reference for the spur-gear pair case (numpy involute + OpenCascade; no Zoo, no KCL).

Design (explicit so the reference and the KCL represent the same gears):
  module 2 mm, pressure angle 20 deg, zero profile shift, 20T pinion at (0,0) and 40T wheel at (60,0),
  centre distance 60 = (20+40)*2/2, face width 8 mm (z 0..8), bores Ø6 (pinion) and Ø8 (wheel),
  addendum 1.0 m, dedendum 1.25 m (tip clearance 0.25 m = 0.5 mm), circular backlash 0.10 mm total
  (each tooth thinned by 0.05 mm at its pitch circle), involute flanks discretised with 16 points
  per flank, root and tip arcs discretised at 0.25 mm; carrier plate 110 x 50 x 5 mm under the gears
  (z -5..0) with Ø6 and Ø8 shaft holes on the gear axes; the three bodies are separate solids.

Writes truth/cases/gear-pair/truth/{pinion,wheel,carrier,pair}.step, pair.stl and the 2D tooth
profiles as CSV loops. Run `python -m opencad.truth pin gear-pair` afterwards.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from OCP.BRep import BRep_Builder  # noqa: E402
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut  # noqa: E402
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon  # noqa: E402
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism  # noqa: E402
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Vec  # noqa: E402
from OCP.TopoDS import TopoDS_Compound  # noqa: E402

from opencad.truth.mutants import write_step, write_stl  # noqa: E402

CASE = REPO / "truth" / "cases" / "gear-pair"
SPEC = {
    "module": 2.0, "pressure_angle_deg": 20.0, "profile_shift": 0.0,
    "pinion_teeth": 20, "wheel_teeth": 40, "center_distance": 60.0,
    "face_width": 8.0, "pinion_bore": 6.0, "wheel_bore": 8.0,
    "addendum_coeff": 1.0, "dedendum_coeff": 1.25, "backlash_total": 0.10,
    "flank_points": 16, "arc_step": 0.25,
    "carrier": {"size": [110.0, 50.0, 5.0], "min": [-25.0, -25.0, -5.0]},
    "pinion_center": [0.0, 0.0], "wheel_center": [60.0, 0.0],
    "phase": "pinion tooth centred on +x; wheel rotated by half a pitch (pi/40) so a tooth space faces it",
}


def involute_gear_polygon(n: int, m: float, alpha_deg: float, backlash: float, flank_points: int, arc_step: float,
                          addendum: float = 1.0, dedendum: float = 1.25) -> np.ndarray:
    """Closed CCW polygon (x, y) of an external involute spur gear centred at the origin."""
    alpha = math.radians(alpha_deg)
    r = m * n / 2
    rb = r * math.cos(alpha)
    ra = r + addendum * m
    rf = r - dedendum * m

    def inv(a: float) -> float:
        return math.tan(a) - a

    # half tooth thickness angle at the pitch circle, thinned by half the backlash
    psi = math.pi / (2 * n) - (backlash / 2) / r
    inv_pitch = inv(alpha)
    pts: list[tuple[float, float]] = []
    r_start = max(rb, rf)
    radii = np.linspace(r_start, ra, flank_points)
    for k in range(n):
        phi = 2 * math.pi * k / n
        # left flank going outward (angles increase CCW)
        left = []
        for rho in radii:
            a = math.acos(rb / rho)
            th = psi + inv_pitch - inv(a)
            left.append((rho, phi + th))
        right = [(rho, phi - th + 2 * (psi + inv_pitch - inv_pitch)) for rho, th in [(rho, psi + inv_pitch - inv(math.acos(rb / rho))) for rho in radii]]
        right = [(rho, phi - (th - phi)) for rho, th in left]  # mirror of the left flank about the tooth centre line
        # tooth: root -> right flank up -> tip arc -> left flank down -> root, walking CCW means right flank first (angle below phi)
        seq: list[tuple[float, float]] = []
        if rf < rb:
            seq.append((rf, right[0][1]))
        seq += right
        # tip arc from right tip angle to left tip angle
        a0, a1 = right[-1][1], left[-1][1]
        n_arc = max(2, int(abs(a1 - a0) * ra / arc_step))
        seq += [(ra, a0 + (a1 - a0) * i / n_arc) for i in range(1, n_arc)]
        seq += left[::-1]
        if rf < rb:
            seq.append((rf, left[0][1]))
        # root arc to the next tooth's right flank start
        next_phi = 2 * math.pi * (k + 1) / n
        b0, b1 = left[0][1], next_phi - (left[0][1] - phi)
        n_arc = max(2, int(abs(b1 - b0) * rf / arc_step))
        seq += [(rf, b0 + (b1 - b0) * i / n_arc) for i in range(1, n_arc)]
        pts += [(rho * math.cos(t), rho * math.sin(t)) for rho, t in seq]
    arr = np.asarray(pts)
    # drop consecutive duplicates
    keep = np.ones(len(arr), bool)
    keep[1:] = np.linalg.norm(np.diff(arr, axis=0), axis=1) > 1e-9
    return arr[keep]


def prism(poly: np.ndarray, height: float, center: tuple[float, float]):
    mp = BRepBuilderAPI_MakePolygon()
    for x, y in poly:
        mp.Add(gp_Pnt(float(x + center[0]), float(y + center[1]), 0.0))
    mp.Close()
    face = BRepBuilderAPI_MakeFace(mp.Wire(), True).Face()
    return BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, height)).Shape()


def gear_solid(n: int, center: tuple[float, float], bore: float, spec: dict, phase: float = 0.0) -> tuple[object, np.ndarray]:
    """`phase` rotates the tooth pattern (radians); the wheel is phased by half a pitch so a tooth space faces the pinion tooth on the centre line."""
    poly = involute_gear_polygon(n, spec["module"], spec["pressure_angle_deg"], spec["backlash_total"], spec["flank_points"], spec["arc_step"],
                                 spec["addendum_coeff"], spec["dedendum_coeff"])
    if phase:
        c, s = math.cos(phase), math.sin(phase)
        poly = poly @ np.array([[c, s], [-s, c]])
    body = prism(poly, spec["face_width"], center)
    hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(center[0], center[1], -1), gp_Dir(0, 0, 1)), bore / 2, spec["face_width"] + 2).Shape()
    return BRepAlgoAPI_Cut(body, hole).Shape(), poly


def carrier_solid(spec: dict):
    lo = spec["carrier"]["min"]
    sz = spec["carrier"]["size"]
    plate = BRepPrimAPI_MakeBox(gp_Pnt(*lo), gp_Pnt(lo[0] + sz[0], lo[1] + sz[1], lo[2] + sz[2])).Shape()
    for c, d in ((spec["pinion_center"], spec["pinion_bore"]), (spec["wheel_center"], spec["wheel_bore"])):
        hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(c[0], c[1], lo[2] - 1), gp_Dir(0, 0, 1)), d / 2, sz[2] + 2).Shape()
        plate = BRepAlgoAPI_Cut(plate, hole).Shape()
    return plate


SPEC_TEXT = """# Spur-gear pair on a carrier plate: design specification

Design the assembly below as editable KCL: three separate solids in one file (no fused bodies).

| Parameter | Value |
| --- | ---: |
| Module | 2 mm |
| Pressure angle | 20 deg |
| Profile shift | 0 (both gears) |
| Pinion | 20 teeth, bore Ø6, axis at (0, 0) parallel to z |
| Wheel | 40 teeth, bore Ø8, axis at (60, 0) parallel to z |
| Centre distance | 60 mm (= (20 + 40) x 2 / 2) |
| Face width | 8 mm, both gears from z = 0 to z = 8 |
| Addendum / dedendum | 1.0 m / 1.25 m (tip radii 22 and 42; root radii 17.5 and 37.5; tip clearance 0.5) |
| Circular backlash | 0.10 mm total: thin each tooth by 0.05 mm at its pitch circle |
| Tooth phase | pinion has a tooth centred on +x; the wheel has a tooth SPACE centred toward the pinion (rotate its pattern half a pitch, pi/40) |
| Carrier plate | 110 x 50 x 5 mm, corner at (-25, -25, -5) to (85, 25, 0), with Ø6 and Ø8 clearance holes on the two gear axes |
| Motion | the wheel turns at half the pinion's speed in the opposite sense; the pair must rotate through a full pitch with zero interference and a flank gap of at most 0.15 mm |

Frame: z up (gear axes), the pinion axis is the origin, +x from the pinion axis toward the wheel axis. The gears sit on
the carrier (gear bottoms at z = 0, carrier top at z = 0), touching but separate. The involute flanks may be built from
the involute equations (recommended, sample the flank at 12-16 points from the base circle to the tip) or with the
standard library's gear functions if they honour the module, tooth counts, pressure angle and backlash above.

Scored on the exported STEP: three solids, tooth counts (20 and 40) from a mid-thickness section, bore axes and
diameters, the centre distance, the tooth profile against an independently generated involute (p95 <= 0.1 mm), and a
rotation sweep of the meshed pair (interference and backlash band). The reference geometry is evaluator-only.
"""


def write_case(spec: dict, truth_dir: Path, pinion_poly: np.ndarray, wheel_poly: np.ndarray) -> None:
    import yaml as _yaml

    case = truth_dir.parent
    (case / "inputs").mkdir(exist_ok=True)
    (case / "inputs" / "gear-pair-spec.md").write_text(SPEC_TEXT, encoding="utf-8")
    inputs = [{"path": "inputs/gear-pair-spec.md", "kind": "text", "sha256": "PIN", "note": "the complete design specification"}]
    m_ = spec["module"]
    from opencad.geomcheck import brep as _brep

    pair_bbox = [round(x, 3) for x in _brep.analyze_step(truth_dir / "pair.step")["bbox_size"]]
    obs: list[dict] = [
        {"id": "bbox_size", "kind": "bbox_size", "expected": pair_bbox, "tolerance": 0.15, "note": "carrier -25..85 in x but the wheel tips reach ~102; wheel tips ~+-42 in y (phased half a pitch); z -5..8"},
        {"id": "solid_count", "kind": "solid_count", "expected": 3},
        {"id": "pinion", "kind": "solid", "point": [12.0, 0.0, 4.0], "from": {"file": "truth/pinion.step", "measure": "volume"}, "tolerance_rel": 0.01, "note": "the pinion body, volume vs the independent involute"},
        {"id": "wheel", "kind": "solid", "point": [90.0, 0.0, 4.0], "from": {"file": "truth/wheel.step", "measure": "volume"}, "tolerance_rel": 0.01},
        {"id": "carrier", "kind": "solid", "point": [30.0, 15.0, -2.5], "from": {"file": "truth/carrier.step", "measure": "volume"}, "tolerance_rel": 0.005},
        {"id": "pinion_bore", "kind": "cylinder", "cyl_kind": "hole", "point": [0, 0, 4], "direction": [0, 0, 1], "radius": spec["pinion_bore"] / 2, "radius_tolerance": 0.02, "tolerance": 0.05, "length": spec["face_width"], "length_tolerance": 0.1},
        {"id": "wheel_bore", "kind": "cylinder", "cyl_kind": "hole", "point": [spec["center_distance"], 0, 4], "direction": [0, 0, 1], "radius": spec["wheel_bore"] / 2, "radius_tolerance": 0.02, "tolerance": 0.05, "length": spec["face_width"], "length_tolerance": 0.1},
        {"id": "carrier_pinion_hole", "kind": "cylinder", "cyl_kind": "hole", "point": [0, 0, -2.5], "direction": [0, 0, 1], "radius": spec["pinion_bore"] / 2, "radius_tolerance": 0.02, "tolerance": 0.05, "length": 5.0, "length_tolerance": 0.1},
        {"id": "carrier_wheel_hole", "kind": "cylinder", "cyl_kind": "hole", "point": [spec["center_distance"], 0, -2.5], "direction": [0, 0, 1], "radius": spec["wheel_bore"] / 2, "radius_tolerance": 0.02, "tolerance": 0.05, "length": 5.0, "length_tolerance": 0.1},
        {"id": "pinion_teeth", "kind": "teeth", "solid": "pinion", "point": [0, 0, 0], "direction": [0, 0, 1], "at": 4.0, "module": m_, "expected": spec["pinion_teeth"]},
        {"id": "wheel_teeth", "kind": "teeth", "solid": "wheel", "point": [spec["center_distance"], 0, 0], "direction": [0, 0, 1], "at": 4.0, "module": m_, "expected": spec["wheel_teeth"]},
        {"id": "pinion_profile", "kind": "profile2d", "solid": "pinion", "plane": "z", "at": 4.0, "reference": "truth/pinion-profile.csv", "reference_units": "mm", "reference_skip": 1,
         "p95_max": 0.1, "tolerance_rel": 0.01, "chord_tolerance": 0.2, "stagger_tolerance_deg": 360.0, "outer_only": True, "note": "tooth profile vs the independent involute; the chord/stagger of a gear outline are not meaningful, only p95 and area"},
        {"id": "gear_mesh", "kind": "gear_mesh", "a": "pinion", "b": "wheel", "axis_a": [[0, 0, 0], [0, 0, 1]], "axis_b": [[spec["center_distance"], 0, 0], [0, 0, 1]],
         "ratio": spec["pinion_teeth"] / spec["wheel_teeth"], "pitch_deg": 360.0 / spec["pinion_teeth"], "steps": 6, "backlash_max": 0.15,
         "note": "rotate the pinion through one pitch, the wheel at half speed opposite; no interference, flank gap within the backlash band"},
        {"id": "gears_separate", "kind": "clearance", "a": "pinion", "b": "wheel", "min_gap": 0.0, "max_gap": 0.15, "note": "separate solids in contact range, never fused"},
        {"id": "pinion_on_carrier", "kind": "clearance", "a": "pinion", "b": "carrier", "min_gap": 0.0, "max_gap": 0.05},
        {"id": "gear_tops", "kind": "face", "plane": "z", "at": spec["face_width"], "normal": "+", "mode": "sum", "from": None, "expected": None, "tolerance": 0.05, "note": "both gear top faces at z = 8"},
    ]
    manifest = {
        "id": "gear-pair", "title": "Spur-gear pair (20T/40T, m = 2, 20 deg) on a carrier plate: separate solids, tooth counts, involute profile, meshing motion",
        "truth_class": "C", "role": "validation",
        "source": {"citation": "Design specification authored for this benchmark; reference geometry generated independently by scripts/derive_gear_truth.py (numpy involute + OpenCascade)",
                   "urls": [], "accessed": "2026-09-17", "revision": "spec v1", "license": "this repository"},
        "intent": ("Design the spur-gear pair and carrier plate exactly as specified in the attached specification: module 2, pressure angle 20 deg, zero profile shift, 20-tooth pinion "
                   "(bore Ø6) at the origin and 40-tooth wheel (bore Ø8) at (60, 0), face width 8 (z 0..8), 0.10 mm total circular backlash, pinion tooth centred on +x and the wheel "
                   "phased half a pitch so the pair meshes; carrier 110 x 50 x 5 under the gears with clearance holes on the axes. Three separate solids in one KCL file; the pair must turn "
                   "through a full pitch without interference. Declare the three solids by contained points, the bores as cylinders, and the gears' tooth counts and mesh as acceptance items."),
        "inputs": inputs,
        "truth": [{"path": "truth/pair.step", "kind": "cad", "sha256": "PIN", "units": "mm"}, {"path": "truth/pinion.step", "kind": "cad", "sha256": "PIN", "units": "mm"},
                  {"path": "truth/wheel.step", "kind": "cad", "sha256": "PIN", "units": "mm"}, {"path": "truth/carrier.step", "kind": "cad", "sha256": "PIN", "units": "mm"},
                  {"path": "truth/pair.stl", "kind": "mesh", "sha256": "PIN", "units": "mm"}, {"path": "truth/pinion-profile.csv", "kind": "table", "sha256": "PIN", "units": "mm"},
                  {"path": "truth/wheel-profile.csv", "kind": "table", "sha256": "PIN", "units": "mm"}, {"path": "truth/gear-spec.yaml", "kind": "yaml", "sha256": "PIN"},
                  {"path": "truth/pair-19t.step", "kind": "cad", "sha256": "PIN", "units": "mm", "note": "wrong-pinion (19 teeth) variant for the mutant harness"}],
        "arms": [{"id": "spec-only", "design": "gear-pair", "inputs": ["inputs/gear-pair-spec.md"], "images": [], "notes": "Text specification only; the reference involutes are evaluator-only."}],
        "observables": obs,
        "notes": ["Motion is checked by rotating the exported solids in OpenCascade; a fused gear-shaped mesh fails solid_count and the clearances."],
    }
    (case / "manifest.yaml").write_text(_yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
    (case / "mutants.yaml").write_text("# Deliberately wrong gear sets the scorer must reject.\n" + _yaml.safe_dump({"mutants": [
        {"id": "gears_fused", "op": "fill_box", "min": [17.0, -1.5, 0.5], "max": [43.0, 1.5, 7.5], "expect_caught_by": ["solid_count"], "note": "a bar joining pinion and wheel: one fused body"},
        {"id": "wheel_shifted_1mm", "op": "translate_solid", "contains": [90, 0, 4], "offset": [1.0, 0, 0], "expect_caught_by": ["wheel_bore", "gear_mesh"], "note": "centre distance 61: backlash band violated"},
        {"id": "wheel_too_close", "op": "translate_solid", "contains": [90, 0, 4], "offset": [-0.5, 0, 0], "expect_caught_by": ["gear_mesh"], "note": "centre distance 59.5: the gears interfere"},
        {"id": "pinion_19_teeth", "op": "scale", "factor": 1.0, "source": "truth/pair-19t.step", "expect_caught_by": ["pinion_teeth"], "note": "a 19-tooth pinion of the same tip radius"},
    ]}, sort_keys=False, width=110), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=CASE / "truth")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    spec = SPEC
    pinion, poly_p = gear_solid(spec["pinion_teeth"], tuple(spec["pinion_center"]), spec["pinion_bore"], spec)
    wheel, poly_w = gear_solid(spec["wheel_teeth"], tuple(spec["wheel_center"]), spec["wheel_bore"], spec, phase=math.pi / spec["wheel_teeth"])
    carrier = carrier_solid(spec)
    comp = TopoDS_Compound()
    b = BRep_Builder()
    b.MakeCompound(comp)
    for s in (pinion, wheel, carrier):
        b.Add(comp, s)
    write_step(pinion, a.out / "pinion.step")
    write_step(wheel, a.out / "wheel.step")
    write_step(carrier, a.out / "carrier.step")
    write_step(comp, a.out / "pair.step")
    write_stl(comp, a.out / "pair.stl", 0.01)
    for name, poly, c in (("pinion", poly_p, spec["pinion_center"]), ("wheel", poly_w, spec["wheel_center"])):
        pts = poly + np.asarray(c)
        pts = np.vstack([pts, pts[:1]])
        np.savetxt(a.out / f"{name}-profile.csv", pts, delimiter=",", header="x_mm,y_mm", comments="", fmt="%.6f")
    (a.out / "gear-spec.yaml").write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    # wrong-pinion variant (19 teeth, same module) for the mutant harness
    spec19 = dict(spec, pinion_teeth=19)
    p19, _ = gear_solid(19, tuple(spec["pinion_center"]), spec["pinion_bore"], spec19)
    comp19 = TopoDS_Compound()
    b19 = BRep_Builder()
    b19.MakeCompound(comp19)
    for s in (p19, wheel, carrier):
        b19.Add(comp19, s)
    write_step(comp19, a.out / "pair-19t.step")
    if a.out == CASE / "truth":
        write_case(spec, a.out, poly_p, poly_w)
    from opencad.geomcheck import brep

    an = brep.analyze_step(a.out / "pair.step")
    print(f"pair: solids {an['solids']} valid {an['valid']} volume {an['volume']:.2f} bbox {[round(x, 3) for x in an['bbox_min']]} .. {[round(x, 3) for x in an['bbox_max']]}")
    for name in ("pinion", "wheel"):
        an = brep.analyze_step(a.out / f"{name}.step")
        print(f"{name}: volume {an['volume']:.3f} faces {an['faces']} bbox size {[round(x, 3) for x in an['bbox_size']]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

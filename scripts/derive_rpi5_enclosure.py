#!/usr/bin/env python
"""Build the `rpi5-enclosure` requirements case (class C: requirements, not a golden mesh) and its change-request cases.

The truth is a set of functional requirements derived from the Raspberry Pi 5 mechanical drawing
(RP-008347-DS-1): the board must fit, standoffs must meet the board at its mounting datums, every
connector plug must pass through its opening to the socket, the lid must close on the base without
interference, walls must be thick enough, and the two parts must be separate solids. Many shapes
satisfy them; the scorer checks the contract, not a reference shape.

  python scripts/derive_rpi5_enclosure.py --source-dir ~/.cache/opencad/downloads/rpi5
  python -m opencad.truth pin rpi5-enclosure
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

CASE = REPO / "truth" / "cases" / "rpi5-enclosure"
DESIGN = "rpi5-enclosure"

# Board frame (drawing RP-008347-DS-1): x along the 85 mm edge, y along the 56 mm edge, origin at the
# board corner nearest the USB-C connector, z up with the PCB bottom surface at z = 0 (PCB 1.6 thick).
PCB = (85.0, 56.0, 1.6)
HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]  # Ø2.7, M2.5
HOLE_KEEPOUT_R = 3.1  # component-free ring around each hole where a standoff may touch the board
BOTTOM_KEEPOUT_Z = -3.0  # bottom-side components reach 3 mm below the PCB (drawing side view "3")
HEADROOM = 20.0  # internal clear height above the PCB top over the component field (Active Cooler)
WALL_MIN = 2.0
# connector openings as plug envelopes in the board frame: a box that must be air, from the board edge
# outward through the wall to 25 mm outside (cable plug bodies included). Edge y = 0 carries USB-C and
# the two micro-HDMI; edge x = 85 carries the two USB-A stacks and the RJ45 (positions from the drawing).
PLUGS = {
    "usb_c_plug": ([11.2 - 6.5, -25.0, PCB[2]], [11.2 + 6.5, 0.0, PCB[2] + 7.0]),
    "hdmi0_plug": ([25.8 - 6.0, -25.0, PCB[2]], [25.8 + 6.0, 0.0, PCB[2] + 6.5]),
    "hdmi1_plug": ([39.2 - 6.0, -25.0, PCB[2]], [39.2 + 6.0, 0.0, PCB[2] + 6.5]),
    "usb_a_upper_plug": ([85.0, 47.0 - 7.5, PCB[2]], [110.0, 47.0 + 7.5, PCB[2] + 17.0]),
    "usb_a_lower_plug": ([85.0, 29.1 - 7.5, PCB[2]], [110.0, 29.1 + 7.5, PCB[2] + 17.0]),
    "rj45_plug": ([85.0, 10.2 - 8.5, PCB[2]], [110.0, 10.2 + 8.5, PCB[2] + 15.0]),
    "sd_card_slot": ([-25.0, 22.0, -3.0], [0.0, 34.0, 0.0]),
}

REQUIREMENTS = f"""# Raspberry Pi 5 two-piece enclosure: requirements (the contract to design to)

This is a design task, not a reconstruction: there is no reference enclosure. Every requirement below
is checked on the exported geometry. Interface authority: Raspberry Pi 5 mechanical drawing
RP-008347-DS-1 (attached as `rpi5-drawing-01.png`; all dimensions mm, approximate per the drawing note).

## Board frame (use this frame for the enclosure too)

- x along the 85 mm board edge, y along the 56 mm edge, origin at the board corner nearest the USB-C
  connector (bottom-left in the drawing's plan view); z up with the PCB bottom surface at z = 0 and the
  PCB top at z = {PCB[2]}.
- Mounting holes Ø2.7 (M2.5) at (x, y) = {HOLES}; 58 x 49 centres.
- Bottom-side components reach z = {BOTTOM_KEEPOUT_Z} everywhere except within {HOLE_KEEPOUT_R} mm of each
  hole centre (component-free rings where standoffs may touch the board).
- Top-side envelope: the component field needs {HEADROOM} mm of clear height above the PCB top over the
  whole board footprint (this fits the official Active Cooler).
- Connectors on the y = 0 edge (plan view bottom): USB-C centred x = 11.2, micro-HDMI centred x = 25.8 and
  x = 39.2. Connectors on the x = 85 edge: two stacked USB-A pairs centred y = 47.0 and y = 29.1, RJ45
  centred y = 10.2. The micro-SD slot is under the board at the x = 0 edge, y 22..34. Each connector needs
  a wall opening that a cable plug body passes through: the plug envelopes are listed below as boxes in
  the board frame that must contain no enclosure material.

## Enclosure requirements

1. Two separate printed parts (two solids in one STEP, not touching each other's material): `base`
   below/around the board and `lid` above. The base contains the point (42.5, 28, -6); the lid contains
   (42.5, 28, {PCB[2] + HEADROOM + 3}).
2. Standoffs: four bosses on the base whose top faces lie exactly at z = 0 (the PCB bottom) centred on the
   four hole positions, each with a Ø2.5 x >= 5 mm deep pilot hole on the hole axis for M2.5 self-tapping
   screws from above the board (the boss outer diameter is your choice, <= {2 * HOLE_KEEPOUT_R} mm).
3. Board fit: no enclosure material inside the PCB slab [0,85] x [0,56] x [0,{PCB[2]}], inside the
   bottom-component keep-out (the slab footprint from z = {BOTTOM_KEEPOUT_Z} to 0, minus the four standoff
   rings), or inside the top envelope [0,85] x [0,56] x [{PCB[2]}, {PCB[2] + HEADROOM}]. Leave >= 0.5 mm
   between the board edges and the inner walls.
4. Connector access: none of these plug envelopes may intersect enclosure material:
{chr(10).join(f'   - {k}: min {v[0]} max {v[1]}' for k, v in PLUGS.items())}
5. Lid closes on the base: the lid rests on the base rim (max gap 0.1 mm at the closest approach) with
   zero interference; the lid is removable, so no fused geometry.
6. Lid fastening: at least four Ø3.0..3.4 clearance holes through the lid along z that continue as
   Ø2.5 pilot holes >= 5 mm deep into base corner posts, positioned outside the board footprint.
7. Walls: minimum wall and floor thickness {WALL_MIN} mm for the enclosure shells, measured by the evaluator as the
   5th percentile of inward ray casts on the exported STL (walls, floor, lid, the material around every
   opening). The four standoff bosses are the one accepted exception: a boss capped at Ø{2 * HOLE_KEEPOUT_R} around
   a Ø2.5 pilot leaves a {(2 * HOLE_KEEPOUT_R - 2.5) / 2:.2f} mm annulus, which is intended; declare the wall check
   with the percentile statistic (or exclude the boss annuli by region), not as a global minimum.
8. Declared manufacturing process: FFF printing, no supports; overhangs <= 45 deg; the base prints on its
   floor and the lid on its ceiling.
9. Parametric: enclosure wall thickness, internal headroom, and standoff height are top-level parameters;
   the headroom parameter carries a regeneration sweep over 10 values from 15 to 35 mm and one infeasible
   value (negative headroom) that an assert must reject. Sweep values only have to regenerate a valid
   two-solid enclosure with the standoff datums and openings preserved; the fit requirements above are
   checked at the nominal {HEADROOM} mm only, so no assert may reject a headroom in 15..35.

## Not required

Ventilation slots, text, fillets and cable strain reliefs are welcome but not scored. Do not model the
board itself in the deliverable; it is an evaluator-side keep-out envelope.
"""

INTENT = (
    "Design a two-piece FFF-printed enclosure (base and removable lid, two separate solids in one STEP) for a Raspberry Pi 5 "
    "to the attached requirements document, in the board frame it defines (x along 85, y along 56, PCB bottom at z = 0). The "
    "board must fit with 0.5 mm edge clearance and 20 mm headroom above the PCB; four standoffs meet the PCB bottom at the "
    "Ø2.7 mounting holes (3.5,3.5) (61.5,3.5) (3.5,52.5) (61.5,52.5) with Ø2.5 x 5 pilot holes; every listed cable-plug envelope "
    "(USB-C, 2x micro-HDMI on y = 0; 2x USB-A stacks and RJ45 on x = 85; micro-SD under x = 0) passes through its wall opening; "
    "the lid closes on the base rim with zero interference and is held by four Ø3 through holes into Ø2.5 corner-post pilots; "
    "walls and floor >= 2 mm (5th percentile of inward ray casts; the Ø6.2 standoff bosses' 1.85 mm annuli are the accepted "
    "exception). Declare the base and lid as acceptance solids by a contained point, the keep-outs and "
    "plug envelopes as acceptance hardware with no-interference clearances, the standoff faces and pilot holes as faces and "
    "cylinders pinned by interfaces, and the wall minimum as a p05 thickness check. Headroom, wall thickness and standoff height are "
    "top-level parameters; the headroom parameter gets a 10-value regeneration sweep (15..35, every value must build) and one "
    "infeasible negative value guarded by an assert."
)


def hardware(headroom: float = HEADROOM) -> list[dict]:
    hw = [
        {"name": "pcb_slab", "kind": "box", "min": [0, 0, 0], "max": [PCB[0], PCB[1], PCB[2]]},
        {"name": "pcb_edge_band", "kind": "box", "min": [-0.5, -0.5, 0.2], "max": [PCB[0] + 0.5, PCB[1] + 0.5, PCB[2]],
         "description": "0.5 mm clearance band around the board edges at board height (standoffs touch the board bottom below z = 0.2, which this band excludes)"},
        {"name": "top_envelope", "kind": "box", "min": [0, 0, PCB[2]], "max": [PCB[0], PCB[1], PCB[2] + headroom]},
        {"name": "bottom_keepout", "kind": "box", "min": [0, 0, BOTTOM_KEEPOUT_Z], "max": [PCB[0], PCB[1], 0.0],
         "exclude_cylinders": [{"point": [x, y, BOTTOM_KEEPOUT_Z - 1], "direction": [0, 0, 1], "radius": HOLE_KEEPOUT_R, "length": 2 - BOTTOM_KEEPOUT_Z} for x, y in HOLES]},
    ]
    for k, (lo, hi) in PLUGS.items():
        hw.append({"name": k, "kind": "box", "min": lo, "max": hi})
    return hw


# ECR-3 moves the lid screws to the long sides: two per side at these x, in the walls beyond the board's 0.5 mm band
SIDE_SCREW_X = (50.0, 75.0)


def observables(headroom: float = HEADROOM, wall_min: float = WALL_MIN, side_fasteners: bool = False) -> list[dict]:
    obs: list[dict] = [
        {"id": "two_solids", "kind": "solid_count", "expected": 2},
        {"id": "base_solid", "kind": "solid", "point": [42.5, 28.0, -6.0], "note": "the base contains this point"},
        {"id": "lid_solid", "kind": "solid", "point": [42.5, 28.0, PCB[2] + headroom + 3.0], "note": "the lid contains this point"},
    ]
    for hw in ("pcb_slab", "pcb_edge_band", "top_envelope", "bottom_keepout", *PLUGS.keys()):
        obs.append({"id": f"clear_{hw}", "kind": "clearance", "a": "all", "b": hw, "min_gap": 0.0,
                    "note": "no enclosure material inside this envelope (contact allowed, e.g. standoffs on the PCB bottom)"})
    obs.append({"id": "lid_on_base", "kind": "clearance", "a": "lid_solid", "b": "base_solid", "min_gap": 0.0, "max_gap": 0.1, "note": "lid rests on the base rim without interference"})
    for i, (x, y) in enumerate(HOLES, 1):
        obs.append({"id": f"standoff_{i}_top", "kind": "face", "plane": "z", "at": 0.0, "normal": "+", "center": [x, y], "tolerance": 0.3, "note": "standoff top meets the PCB bottom at the hole datum"})
        obs.append({"id": f"standoff_{i}_pilot", "kind": "cylinder", "cyl_kind": "hole", "point": [x, y, -2.5], "direction": [0, 0, 1], "radius": 1.25, "radius_tolerance": 0.1,
                    "tolerance": 0.2, "length": 6.0, "length_tolerance": 3.0, "note": "Ø2.5 pilot >= 5 deep (checked as 3..9)"})
    if side_fasteners:
        # exactly four lid clearance holes and eight pilots in total (the corner posts are gone), one of each in every side-wall station
        obs.append({"id": "lid_screw_clearance_holes", "kind": "cylinder_count", "cyl_kind": "hole", "radius": 1.6, "radius_tolerance": 0.15, "expected": 4, "direction": [0, 0, 1], "note": "Ø3.2 through the lid flange, long sides only"})
        obs.append({"id": "pilot_holes_total", "kind": "cylinder_count", "cyl_kind": "hole", "radius": 1.25, "radius_tolerance": 0.1, "expected": 8, "direction": [0, 0, 1], "note": "4 standoff + 4 side-boss pilots"})
        for x in SIDE_SCREW_X:
            for side, (y0, y1) in (("ym", (-20.0, -0.5)), ("yp", (PCB[1] + 0.5, PCB[1] + 20.0))):
                region = [[x - 0.5, y0, -20.0], [x + 0.5, y1, 60.0]]
                obs.append({"id": f"side_screw_{side}_x{int(x)}", "kind": "cylinder_count", "cyl_kind": "hole", "radius": 1.6, "radius_tolerance": 0.15, "expected_min": 1, "direction": [0, 0, 1], "region": region,
                            "note": f"lid clearance hole at x = {x} in the {'y < 0' if side == 'ym' else 'y > 56'} wall"})
                obs.append({"id": f"side_pilot_{side}_x{int(x)}", "kind": "cylinder_count", "cyl_kind": "hole", "radius": 1.25, "radius_tolerance": 0.1, "expected_min": 1, "direction": [0, 0, 1], "region": region,
                            "note": f"Ø2.5 boss pilot under the x = {x} screw"})
    else:
        obs.append({"id": "lid_screw_clearance_holes", "kind": "cylinder_count", "cyl_kind": "hole", "radius": 1.6, "radius_tolerance": 0.15, "expected_min": 4, "direction": [0, 0, 1], "note": "Ø3.0..3.4 through the lid"})
        obs.append({"id": "pilot_holes_total", "kind": "cylinder_count", "cyl_kind": "hole", "radius": 1.25, "radius_tolerance": 0.1, "expected_min": 8, "direction": [0, 0, 1], "note": "4 standoff + 4 corner-post pilots"})
    obs.append({"id": "wall_min", "kind": "thickness", "min": wall_min, "samples": 6000, "max_thickness": 12.0, "note": "minimum wall/floor thickness by inward ray casting"})
    obs.append({"id": "headroom_probe", "kind": "probe", "state": "void", "points": [[20, 20, PCB[2] + headroom - 0.5], [65, 40, PCB[2] + headroom - 0.5], [42.5, 28, PCB[2] + 5]], "note": "air above the board"})
    # requirement 1's stated base point; the floor level itself is the designer's choice (it need not touch the keep-out)
    obs.append({"id": "floor_probe", "kind": "probe", "state": "solid", "points": [[42.5, 28, -6.0]], "note": "there is a floor under the component keep-out (requirement 1: the base contains (42.5, 28, -6))"})
    return obs


ECRS = {
    # label: (request file, title, headroom, wall_min, side_fasteners)
    "ecr1": ("ecr-1-headroom.md", "+10 mm internal headroom, datums and openings fixed", HEADROOM + 10.0, WALL_MIN, False),
    "ecr2": ("ecr-2-walls.md", "3 mm walls growing outward, interior preserved", HEADROOM, 3.0, False),
    "ecr3": ("ecr-3-fasteners.md", f"lid screws moved to the long sides at x = {SIDE_SCREW_X}", HEADROOM, WALL_MIN, True),
}


def write_ecr_cases(source: dict) -> None:
    """One class-C case per feasible change request, scored on results/<design>/ecr/<label>/ after `python -m opencad ecr`."""
    for label, (req, title, headroom, wall_min, side) in ECRS.items():
        case = CASE.parent / f"rpi5-enclosure-{label}"
        (case / "inputs").mkdir(parents=True, exist_ok=True)
        (case / "truth").mkdir(exist_ok=True)
        shutil.copy2(CASE / "inputs" / "ecr" / req, case / "inputs" / req)
        (case / "truth" / "requirements.yaml").write_text(yaml.safe_dump({"headroom": headroom, "wall_min": wall_min, "side_screw_x": list(SIDE_SCREW_X) if side else None,
                                                                          "base": "rpi5-enclosure"}, sort_keys=False), encoding="utf-8")
        m = {
            "id": f"rpi5-enclosure-{label}", "title": f"Raspberry Pi 5 enclosure after {label.upper()}: {title}",
            "truth_class": "C", "role": "validation", "source": source,
            "intent": f"Score the enclosure after change request {label.upper()} ({title}): the revised requirement values apply and every other requirement is unchanged.",
            "inputs": [{"path": f"inputs/{req}", "kind": "text", "sha256": "PIN", "note": "the change request"}],
            "truth": [{"path": "truth/requirements.yaml", "kind": "yaml", "sha256": "PIN", "note": "revised requirement values (evaluator-side)"}],
            "hardware": hardware(headroom),
            "arms": [{"id": label, "design": DESIGN, "ecr": label, "inputs": [f"inputs/{req}"], "images": [],
                      "notes": f"Scored with `python -m opencad.truth score` after `python -m opencad ecr {DESIGN} <request> --contract-delta <yaml> --label {label}`; not a drafting run."}],
            "observables": observables(headroom, wall_min, side),
            "notes": ["Class C change-request case: the base case's functional checks with the request's revisions applied."],
        }
        (case / "manifest.yaml").write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
        print(f"wrote {case / 'manifest.yaml'} with {len(m['observables'])} observables")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, default=Path.home() / ".cache" / "opencad" / "downloads" / "rpi5")
    ap.add_argument("--ecr-cases", action="store_true", help="also write the rpi5-enclosure-ecr1..3 change-request cases")
    a = ap.parse_args(argv)
    (CASE / "inputs").mkdir(parents=True, exist_ok=True)
    (CASE / "truth").mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(REPO / "scripts" / "pdf_pages.py"), str(a.source_dir / "rpi5-mechanical-drawing.pdf"), str(CASE / "inputs"), "--dpi", "220", "--prefix", "rpi5-drawing-"], check=True)
    (CASE / "inputs" / "rpi5-enclosure-requirements.md").write_text(REQUIREMENTS, encoding="utf-8")
    shutil.copy2(a.source_dir / "LICENSE.txt", CASE / "truth" / "rpi5-step-LICENSE.txt")
    (CASE / "truth" / "requirements.yaml").write_text(yaml.safe_dump({"pcb": list(PCB), "holes": HOLES, "hole_keepout_r": HOLE_KEEPOUT_R, "bottom_keepout_z": BOTTOM_KEEPOUT_Z,
                                                                       "headroom": HEADROOM, "wall_min": WALL_MIN, "plugs": {k: [list(v[0]), list(v[1])] for k, v in PLUGS.items()}}, sort_keys=False), encoding="utf-8")
    source = {"citation": "Raspberry Pi Ltd, Raspberry Pi 5 mechanical drawing RP-008347-DS-1 (pip.raspberrypi.com); requirements authored for this benchmark",
              "urls": ["https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008347-DS-1-raspberry-pi-5-mechanical-drawing.pdf",
                       "https://pip.raspberrypi.com/categories/892-raspberry-pi-5"],
              "accessed": "2026-09-17", "revision": "drawing updated 6 Oct 2025 per the product information portal", "license": "Raspberry Pi drawing: reference use; requirements: this repository"}
    m = {
        "id": "rpi5-enclosure",
        "title": "Raspberry Pi 5 two-piece enclosure designed to functional requirements (board fit, standoff datums, plug access, lid closure, wall minimum)",
        "truth_class": "C", "role": "validation",
        "source": source,
        "intent": INTENT,
        "inputs": [{"path": "inputs/rpi5-enclosure-requirements.md", "kind": "text", "sha256": "PIN", "note": "the requirements contract"},
                   {"path": "inputs/rpi5-drawing-01.png", "kind": "drawing", "sha256": "PIN", "units": "mm", "note": "official mechanical drawing"}],
        "truth": [{"path": "truth/requirements.yaml", "kind": "yaml", "sha256": "PIN", "note": "machine-readable requirement values (evaluator-side)"},
                  {"path": "truth/rpi5-step-LICENSE.txt", "kind": "text", "sha256": "PIN", "note": "license of the Raspberry Pi STEP package (board model available to the evaluator)"}],
        "hardware": hardware(),
        "arms": [{"id": "requirements", "design": DESIGN, "inputs": ["inputs/rpi5-enclosure-requirements.md", "inputs/rpi5-drawing-01.png"], "images": ["inputs/rpi5-drawing-01.png"],
                  "notes": "Design to requirements. Many shapes pass; the scorer checks fit, datums, plug access, closure, walls and separability."}],
        "observables": observables(),
        "notes": ["Class C requirements case: truth is a set of functional checks, not a mesh.",
                  "Change requests (results/<design>/ecr/*) are scored against the same observables with the request's revisions applied."],
    }
    (CASE / "manifest.yaml").write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
    (CASE / "mutants.yaml").write_text("# Deliberately wrong enclosures the scorer must reject (run after a passing design exists).\n" + yaml.safe_dump({"mutants": [
        {"id": "lid_fused_to_base", "op": "fill_box", "min": [-8.5, -8.5, 21.4], "max": [93.5, -0.5, 21.8], "expect_caught_by": ["two_solids"], "note": "a bridge of material across the rim gap along the front wall: one printed blob, the lid cannot come off (a plain fuse of two non-touching solids changes nothing)"},
        {"id": "usb_c_blocked", "op": "fill_box", "min": [4.0, -3.0, 1.6], "max": [18.5, 0.5, 9.0], "expect_caught_by": ["clear_usb_c_plug"], "note": "the USB-C opening walled over"},
        {"id": "standoff_shifted", "op": "shift_hole", "near": [3.5, 3.5, -2.5], "radius": 1.25, "offset": [0.6, 0, 0], "expect_caught_by": ["standoff_1_pilot"], "note": "one pilot 0.6 mm off its datum"},
        {"id": "floor_thinned", "op": "cut_box", "min": [30, 20, -6.5], "max": [55, 36, -4.2], "note": "floor cut to below the wall minimum from below (depends on the floor level of the design)"},
    ]}, sort_keys=False, width=110), encoding="utf-8")
    print(f"wrote {CASE / 'manifest.yaml'} with {len(m['observables'])} observables and {len(m['hardware'])} hardware envelopes")
    if a.ecr_cases:
        write_ecr_cases(source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

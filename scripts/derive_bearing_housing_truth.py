#!/usr/bin/env python
"""Frozen reference for the bearing-housing fast regression case (build123d; evaluator-only geometry).

Source: build123d `examples/cast_bearing_unit.py` at dev commit cdaf1caa4c72436ebfe0907e1fb05e246d568cbc (2025-05-25),
Copyright 2025 Gumyr, Apache-2.0. `build()` below is the upstream modelling block verbatim; only the viewer call
(`ocp_vscode.show`) and the colour assignment are dropped. The bearing and the screws the upstream docstring mentions are
not in that file and are not part of this case: the housing alone is one connected solid.

Run in the repo .venv (build123d 0.12.0), then pin:

  .venv/bin/python scripts/derive_bearing_housing_truth.py && .venv/bin/python -m opencad.truth pin bearing-housing

Writes truth/cases/bearing-housing/truth/{housing.step, housing.stl}, the wrong variant housing-no-draft.step for the
mutant harness, the worker-visible views inputs/bearing-housing-{iso,top,section}.png, and prints the measurements the
spec and the manifest quote.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from opencad import render  # noqa: E402
from opencad.geomcheck import brep  # noqa: E402
from opencad.truth.mutants import write_step, write_stl  # noqa: E402

CASE = REPO / "truth" / "cases" / "bearing-housing"
UPSTREAM = "https://github.com/gumyr/build123d/blob/cdaf1caa4c72436ebfe0907e1fb05e246d568cbc/examples/cast_bearing_unit.py"


def build(draft_deg: float = 4):
    """The upstream block; `draft_deg=0` skips the draft (the wrong variant the mutant harness scores)."""
    from build123d import (Axis, BuildPart, BuildSketch, Circle, CounterBoreHole, GridLocations, Hole, Locations, Plane,
                           draft, extrude, fillet, make_hull)

    A, A1, Db2, H, J = 26, 11, 57, 98.5, 76.5
    with BuildPart() as oval_flanged_bearing_unit:
        with BuildSketch() as plan:  # noqa: F841 - upstream name
            housing = Circle(Db2 / 2)
            with GridLocations(J, 0, 2, 1) as bolt_centers:
                Circle((H - J) / 2)
            make_hull()
        extrude(amount=A1)
        extrude(housing, amount=A)
        drafted_faces = oval_flanged_bearing_unit.faces().filter_by(Axis.Z, reverse=True)
        if draft_deg:
            draft(drafted_faces, Plane.XY, draft_deg)
        fillet(oval_flanged_bearing_unit.edges(), 1)
        with Locations(oval_flanged_bearing_unit.faces().sort_by(Axis.Z)[-1]):
            CounterBoreHole(14 / 2, 47 / 2, 14)
        with Locations(*bolt_centers):
            Hole(5)
    return oval_flanged_bearing_unit.part


def main() -> int:
    part = build()
    if not part.is_valid or len(part.solids()) != 1:
        raise SystemExit(f"reference is not one valid solid (valid={part.is_valid}, solids={len(part.solids())})")
    (CASE / "truth").mkdir(parents=True, exist_ok=True)
    (CASE / "inputs").mkdir(parents=True, exist_ok=True)
    step = write_step(part.wrapped, CASE / "truth" / "housing.step")
    stl = write_stl(part.wrapped, CASE / "truth" / "housing.stl", deflection=0.02)
    write_step(build(draft_deg=0).wrapped, CASE / "truth" / "housing-no-draft.step")
    mesh = render.load_mesh(stl)
    render.render_view(mesh, "iso", CASE / "inputs" / "bearing-housing-iso.png", px=1200, title="bearing housing: isometric (reference)")
    render.render_view(mesh, "top", CASE / "inputs" / "bearing-housing-top.png", px=1200, title="bearing housing: top view, +x right, +y up")
    render.render_section(mesh, "y", 0.0, CASE / "inputs" / "bearing-housing-section.png", title="bearing housing: section y = 0 (x-z plane), mm")
    shape = brep.read_step(step)
    a = brep.analyze_step(step)
    print(f"source {UPSTREAM}")
    print(f"volume {a['volume']:.3f}  surface {a['surface_area']:.3f}  CoM {[round(v, 3) for v in a['center_of_mass']]}  bbox size {[round(v, 3) for v in a['bbox_size']]}")
    for plane, at in (("z", 5.5), ("z", 15.0), ("z", 24.0), ("y", 0.0), ("x", 0.0), ("x", 38.25)):
        s = brep.section(shape, plane, at)
        print(f"section {plane}={at}: area {s['area']:.3f} loops {s['loops']} holes {s['holes']}")
    for f in sorted(brep.planar_faces(shape), key=lambda f: -f["area"]):
        print(f"face area {f['area']:.3f} normal {[round(v, 4) for v in f['normal']]} centroid {[round(v, 3) for v in f['centroid']]}")
    for c in brep.cylinders(shape):
        if c["radius"] > 1.5:
            print(f"cylinder r {c['radius']:.3f} {c['kind']} centre {[round(v, 3) for v in c['center']]} length {c['length']:.3f} t {c['t_min']:.3f}..{c['t_max']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

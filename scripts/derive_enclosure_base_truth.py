#!/usr/bin/env python
"""Frozen reference for the enclosure-base fast regression case (CadQuery; evaluator-only geometry).

Source: CadQuery documentation, "A Parametric Enclosure" (`doc/examples.rst` at master commit
17846d631e26e8deee0fee43bd6daa1c5c5dbee2, 2023-10-22), CadQuery Apache-2.0. `build()` below is the upstream code through
the lid/base split, verbatim with the published default parameters; the lid branch (counterbores, flip, union) is dropped
and the lower body is selected by position (lowest centre of mass), never by enumeration order. The base is 47 mm tall
after the split (not the 50 mm `p_outerHeight`); the post bores stop at the 3 mm floor.

Run in the repo .venv (CadQuery 2.8.0), then pin:

  .venv/bin/python scripts/derive_enclosure_base_truth.py && .venv/bin/python -m opencad.truth pin enclosure-base

Writes truth/cases/enclosure-base/truth/{base.step, base.stl}, the wrong variant base-50-tall.step (the unsplit height
trap) for the mutant harness, the worker-visible views inputs/enclosure-base-{iso,top,section}.png, and prints the
measurements the spec and the manifest quote.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from opencad import render  # noqa: E402
from opencad.geomcheck import brep  # noqa: E402
from opencad.truth.mutants import write_step, write_stl  # noqa: E402

CASE = REPO / "truth" / "cases" / "enclosure-base"
UPSTREAM = "https://github.com/CadQuery/cadquery/blob/17846d631e26e8deee0fee43bd6daa1c5c5dbee2/doc/examples.rst#a-parametric-enclosure"


def build(p_outerHeight: float = 50.0):
    """The upstream code through the split; `p_outerHeight=53` gives the 50-tall base the mutant harness scores."""
    import cadquery as cq

    # parameter definitions (published defaults)
    p_outerWidth = 100.0  # Outer width of box enclosure
    p_outerLength = 150.0  # Outer length of box enclosure
    p_thickness = 3.0  # Thickness of the box walls
    p_sideRadius = 10.0  # Radius for the curves around the sides of the box
    p_topAndBottomRadius = 2.0  # Radius for the curves on the top and bottom edges of the box
    p_screwpostInset = 12.0  # How far in from the edges the screw posts should be place.
    p_screwpostID = 4.0  # Inner Diameter of the screw post holes, should be roughly screw diameter not including threads
    p_screwpostOD = 10.0  # Outer Diameter of the screw posts.
    p_lipHeight = 1.0  # Height of lip on the underside of the lid.

    # outer shell
    oshell = cq.Workplane("XY").rect(p_outerWidth, p_outerLength).extrude(p_outerHeight + p_lipHeight)
    # weird geometry happens if we make the fillets in the wrong order
    if p_sideRadius > p_topAndBottomRadius:
        oshell = oshell.edges("|Z").fillet(p_sideRadius)
        oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
    else:
        oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
        oshell = oshell.edges("|Z").fillet(p_sideRadius)
    # inner shell
    ishell = (oshell.faces("<Z").workplane(p_thickness, True)
              .rect((p_outerWidth - 2.0 * p_thickness), (p_outerLength - 2.0 * p_thickness))
              .extrude((p_outerHeight - 2.0 * p_thickness), False))
    ishell = ishell.edges("|Z").fillet(p_sideRadius - p_thickness)
    # make the box outer box
    box = oshell.cut(ishell)
    # make the screw posts
    POSTWIDTH = p_outerWidth - 2.0 * p_screwpostInset
    POSTLENGTH = p_outerLength - 2.0 * p_screwpostInset
    box = (box.faces(">Z").workplane(-p_thickness).rect(POSTWIDTH, POSTLENGTH, forConstruction=True)
           .vertices().circle(p_screwpostOD / 2.0).circle(p_screwpostID / 2.0)
           .extrude(-1.0 * (p_outerHeight + p_lipHeight - p_thickness), True))
    # split lid into top and bottom parts
    parts = box.faces(">Z").workplane(-p_thickness - p_lipHeight).split(keepTop=True, keepBottom=True).all()
    solids = [s for w in parts for s in w.solids().vals()]
    return min(solids, key=lambda s: s.Center().z)


def main() -> int:
    base = build()
    if not base.isValid() or len(base.Solids()) != 1:
        raise SystemExit(f"reference is not one valid solid (valid={base.isValid()}, solids={len(base.Solids())})")
    (CASE / "truth").mkdir(parents=True, exist_ok=True)
    (CASE / "inputs").mkdir(parents=True, exist_ok=True)
    step = write_step(base.wrapped, CASE / "truth" / "base.step")
    stl = write_stl(base.wrapped, CASE / "truth" / "base.stl", deflection=0.02)
    write_step(build(p_outerHeight=53.0).wrapped, CASE / "truth" / "base-50-tall.step")
    mesh = render.load_mesh(stl)
    render.render_view(mesh, "iso", CASE / "inputs" / "enclosure-base-iso.png", px=1200, title="enclosure base: isometric (reference)")
    render.render_view(mesh, "top", CASE / "inputs" / "enclosure-base-top.png", px=1200, title="enclosure base: top view, +x right, +y up")
    render.render_section(mesh, "x", 38.0, CASE / "inputs" / "enclosure-base-section.png", title="enclosure base: section x = 38 (y-z plane) through two posts, mm")
    shape = brep.read_step(step)
    a = brep.analyze_step(step)
    print(f"source {UPSTREAM}")
    print(f"volume {a['volume']:.3f}  surface {a['surface_area']:.3f}  CoM {[round(v, 3) for v in a['center_of_mass']]}  bbox size {[round(v, 3) for v in a['bbox_size']]}")
    for plane, at in (("z", 1.5), ("z", 25.0), ("z", 45.0), ("x", 38.0), ("y", 0.0), ("y", 63.0)):
        s = brep.section(shape, plane, at)
        print(f"section {plane}={at}: area {s['area']:.3f} loops {s['loops']} holes {s['holes']}")
    for f in sorted(brep.planar_faces(shape), key=lambda f: -f["area"]):
        print(f"face area {f['area']:.3f} normal {[round(v, 4) for v in f['normal']]} centroid {[round(v, 3) for v in f['centroid']]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

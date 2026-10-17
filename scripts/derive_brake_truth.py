"""Reference geometry of the COMSOL 6.3 brake_disc model (evaluator side), from its published construction steps, in mm.

Disc: cylinder r 140 x 13 (z 0..13) plus hub cylinder r 80 x 10 (z 13..23). Pad: a closed outline of four cubic Bezier
curves in the work plane z = 13 (curve 1 weight 2.5 on its third control point, curve 4 on its second), extruded 6.5 mm.
Writes truth/cases/disc-brake/truth/{disc,pad,brake}.step and brake-spec.yaml (volumes, areas, centroids, radial extent).

    .venv/bin/python scripts/derive_brake_truth.py
"""

from __future__ import annotations

import math
from pathlib import Path

import yaml
from build123d import Align, Bezier, Compound, Cylinder, Plane, Pos, Wire, export_step, extrude, make_face

OUT = Path(__file__).resolve().parents[1] / "truth" / "cases" / "disc-brake" / "truth"
CURVES = (
    ([(0, 135), (20, 135), (50, 130), (40, 105)], [1, 1, 2.5, 1]),
    ([(40, 105), (30, 80), (35, 90), (0, 90)], None),
    ([(0, 90), (-35, 90), (-30, 80), (-40, 105)], None),
    ([(-40, 105), (-50, 130), (-20, 135), (0, 135)], [1, 2.5, 1, 1]),
)


def build():
    zmin = (Align.CENTER, Align.CENTER, Align.MIN)
    disc = Cylinder(140, 13, align=zmin) + Pos(0, 0, 13) * Cylinder(80, 10, align=zmin)
    edges = [Bezier(*[(x, y, 13.0) for x, y in pts], weights=w) if w else Bezier(*[(x, y, 13.0) for x, y in pts]) for pts, w in CURVES]
    outline = make_face(Wire(edges))
    pad = extrude(outline, amount=6.5, dir=(0, 0, 1))
    return disc, pad, outline


def main() -> None:
    disc, pad, outline = build()
    OUT.mkdir(parents=True, exist_ok=True)
    export_step(disc, str(OUT / "disc.step"))
    export_step(pad, str(OUT / "pad.step"))
    export_step(Compound([disc, pad]), str(OUT / "brake.step"))
    c = outline.center()
    radii = [math.hypot(v.X, v.Y) for v in pad.vertices()] + [math.hypot(*p) for pts, _ in CURVES for p in pts]
    spec = {
        "disc_volume_mm3": disc.volume, "pad_volume_mm3": pad.volume, "pad_contact_area_mm2": outline.area,
        "pad_contact_centroid_mm": [c.X, c.Y, c.Z], "disc_top_annulus_area_mm2": math.pi * (140 ** 2 - 80 ** 2),
        "pad_bbox_mm": [list(pad.bounding_box().min), list(pad.bounding_box().max)], "pad_vertex_radius_range_mm": [min(radii), max(radii)],
        "note": "COMSOL 6.3 brake_disc construction steps; the Bezier weights follow the documented Weights fields",
    }
    (OUT / "brake-spec.yaml").write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    print(yaml.safe_dump(spec, sort_keys=False))
    _ = Plane


if __name__ == "__main__":
    main()

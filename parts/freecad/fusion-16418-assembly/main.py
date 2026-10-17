from pathlib import Path

import FreeCAD
import Part

here = Path(__file__).resolve().parent
doc = FreeCAD.newDocument("asm")

# Body two stays at identity. Both local axes are +Y; is_flipped requires
# d1' anti-parallel, so Rx(180), then translate so (K1'-K2')·d2' = -5.
tx = 11.5
ty = 3.5
tz = -38.0
rot = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 180)


def load(name, step_name, origin, rotation=None):
    shp = Part.Shape()
    shp.read(str(here / "inputs" / step_name))
    feat = doc.addObject("Part::Feature", name)
    feat.Shape = shp
    feat.Placement = FreeCAD.Placement(
        FreeCAD.Vector(*origin),
        rotation if rotation is not None else FreeCAD.Rotation(),
    )
    return feat


one = load("body_one", "23309_76dcf100_0002_1.step", (tx, ty, tz), rot)
two = load("body_two", "23309_76dcf100_0003_2.step", (0.0, 0.0, 0.0))
doc.recompute()
result = (one, two)
placements = {
    "23309_76dcf100_0002_1": [
        [1, 0, 0, tx],
        [0, -1, 0, ty],
        [0, 0, -1, tz],
        [0, 0, 0, 1],
    ],
    "23309_76dcf100_0003_2": [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ],
}

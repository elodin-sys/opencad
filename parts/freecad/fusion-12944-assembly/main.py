from pathlib import Path

import FreeCAD
import Part

here = Path(__file__).resolve().parent
doc = FreeCAD.newDocument("asm")

# Body two (bolt) stays at identity. Both local axes are (0,-1,0); is_flipped
# requires d1' anti-parallel, so rotate body one (plate) 180° about X, then
# translate so K1=[0,15,0] lands on K2=[0,-29.5,0] (offset 0).
tx = 0.0
ty = -14.5
tz = 0.0
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


one = load("body_one", "22303_e9723631_0014_1.step", (tx, ty, tz), rot)
two = load("body_two", "22303_e9723631_0013_1.step", (0.0, 0.0, 0.0))
doc.recompute()
result = (one, two)
placements = {
    "22303_e9723631_0014_1": [
        [1, 0, 0, tx],
        [0, -1, 0, ty],
        [0, 0, -1, tz],
        [0, 0, 0, 1],
    ],
    "22303_e9723631_0013_1": [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ],
}

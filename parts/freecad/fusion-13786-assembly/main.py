from pathlib import Path

import FreeCAD
import Part

here = Path(__file__).resolve().parent
doc = FreeCAD.newDocument("asm")

# Body two (pin) stays at identity. Body one (plate) is translated so
# K1=[50, 42, 1.5] lands at K2+offset*d2=[11, 40.3792, 49.5496].
# d1=(-1,0,0) is already anti-parallel to d2=(1,0,0); is_flipped=true.
tx = -39.0
ty = -1.6208
tz = 48.0496


def load(name, step_name, origin):
    shp = Part.Shape()
    shp.read(str(here / "inputs" / step_name))
    feat = doc.addObject("Part::Feature", name)
    feat.Shape = shp
    feat.Placement = FreeCAD.Placement(FreeCAD.Vector(*origin), FreeCAD.Rotation())
    return feat


one = load("body_one", "84608_204c01e6_0008_1.step", (tx, ty, tz))
two = load("body_two", "84608_204c01e6_0008_2.step", (0.0, 0.0, 0.0))
doc.recompute()
result = (one, two)
placements = {
    "84608_204c01e6_0008_1": [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1],
    ],
    "84608_204c01e6_0008_2": [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ],
}

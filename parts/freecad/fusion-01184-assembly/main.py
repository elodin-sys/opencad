from pathlib import Path

import FreeCAD
import Part

here = Path(__file__).resolve().parent
doc = FreeCAD.newDocument("asm")

# Body two (plate) stays at identity. Body one (T-pin) is translated so K1 lands
# at K2 + offset*d2 = (20, -1, 60); both joint axes are already +Y (not flipped).
tx = -85.0
ty = -10.706
tz = -35.0


def load(name, step_name, origin):
    shp = Part.Shape()
    shp.read(str(here / "inputs" / step_name))
    feat = doc.addObject("Part::Feature", name)
    feat.Shape = shp
    feat.Placement = FreeCAD.Placement(FreeCAD.Vector(*origin), FreeCAD.Rotation())
    return feat


one = load("body_one", "36938_ae684b66_0002_2.step", (tx, ty, tz))
two = load("body_two", "36938_ae684b66_0001_2.step", (0.0, 0.0, 0.0))
doc.recompute()
result = (one, two)
placements = {
    "36938_ae684b66_0002_2": [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1],
    ],
    "36938_ae684b66_0001_2": [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ],
}

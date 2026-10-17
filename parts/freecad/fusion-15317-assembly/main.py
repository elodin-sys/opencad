from pathlib import Path

import FreeCAD
import Part

here = Path(__file__).resolve().parent
doc = FreeCAD.newDocument("asm")

# Body two stays at identity. d1=(0,1,0) is already anti-parallel to
# d2=(0,-1,0); is_flipped=true. Translate so K1 lands on K2 (offset 0).
tx = 0.0
ty = -14.7258
tz = 0.0


def load(name, step_name, origin):
    shp = Part.Shape()
    shp.read(str(here / "inputs" / step_name))
    feat = doc.addObject("Part::Feature", name)
    feat.Shape = shp
    feat.Placement = FreeCAD.Placement(FreeCAD.Vector(*origin), FreeCAD.Rotation())
    return feat


one = load("body_one", "22337_e2f65ed2_0003_1.step", (tx, ty, tz))
two = load("body_two", "22337_e2f65ed2_0003_2.step", (0.0, 0.0, 0.0))
doc.recompute()
result = (one, two)
placements = {
    "22337_e2f65ed2_0003_1": [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1],
    ],
    "22337_e2f65ed2_0003_2": [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ],
}

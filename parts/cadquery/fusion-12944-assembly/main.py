from pathlib import Path

import cadquery as cq

here = Path(__file__).resolve().parent
body_one = cq.importers.importStep(str(here / "inputs" / "22303_e9723631_0014_1.step"))
body_two = cq.importers.importStep(str(here / "inputs" / "22303_e9723631_0013_1.step"))

# K1=[0, 15, 0] d1=-Y; K2=[0, -29.5, 0] d2=-Y; is_flipped; offset=0
# R_x(180) → d1'=+Y anti-parallel to d2'; t = K2 - R*K1 = [0, -14.5, 0]
tx, ty, tz = 0.0, -14.5, 0.0
placed_one = body_one.val().located(cq.Location(cq.Vector(tx, ty, tz), cq.Vector(1.0, 0.0, 0.0), 180.0))
result = [placed_one, body_two]
placements = {
    "22303_e9723631_0014_1": [
        [1.0, 0.0, 0.0, tx],
        [0.0, -1.0, 0.0, ty],
        [0.0, 0.0, -1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ],
    "22303_e9723631_0013_1": [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
}

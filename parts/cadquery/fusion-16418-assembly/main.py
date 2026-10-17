from pathlib import Path

import cadquery as cq

here = Path(__file__).resolve().parent
body_one = cq.importers.importStep(str(here / "inputs" / "23309_76dcf100_0002_1.step"))
body_two = cq.importers.importStep(str(here / "inputs" / "23309_76dcf100_0003_2.step"))

# K1=[0, 1, 0] d1=+Y; K2=[11.5, 7.5, -38] d2=+Y; is_flipped; offset=-5
# Rx(180) → d1'=-Y anti-parallel to d2'; t = K2 + offset*d2 - R*K1
tx, ty, tz = 11.5, 3.5, -38.0
placed_one = body_one.val().located(cq.Location(cq.Vector(tx, ty, tz), cq.Vector(1.0, 0.0, 0.0), 180.0))
result = [placed_one, body_two]
placements = {
    "23309_76dcf100_0002_1": [
        [1.0, 0.0, 0.0, tx],
        [0.0, -1.0, 0.0, ty],
        [0.0, 0.0, -1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ],
    "23309_76dcf100_0003_2": [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
}

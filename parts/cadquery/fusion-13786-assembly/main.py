from pathlib import Path

import cadquery as cq

here = Path(__file__).resolve().parent
body_one = cq.importers.importStep(str(here / "inputs" / "84608_204c01e6_0008_1.step"))
body_two = cq.importers.importStep(str(here / "inputs" / "84608_204c01e6_0008_2.step"))

# K1=[50, 42, 1.5] d1=-X; K2=[15, 40.3792, 49.5496] d2=+X; is_flipped; offset=-4 → T=K2+offset*d2-K1
tx = -39.0
ty = -1.6208
tz = 48.0496
placed_one = body_one.val().located(cq.Location(cq.Vector(tx, ty, tz)))
result = [placed_one, body_two]
placements = {
    "84608_204c01e6_0008_1": [
        [1.0, 0.0, 0.0, tx],
        [0.0, 1.0, 0.0, ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ],
    "84608_204c01e6_0008_2": [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
}

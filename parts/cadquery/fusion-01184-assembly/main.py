from pathlib import Path

import cadquery as cq

here = Path(__file__).resolve().parent
body_one = cq.importers.importStep(str(here / "inputs" / "36938_ae684b66_0002_2.step"))
body_two = cq.importers.importStep(str(here / "inputs" / "36938_ae684b66_0001_2.step"))

# K1=[105, 9.706, 95], K2=[20, 0, 60], both +Y; is_flipped=false; offset=-1 → T=K2+offset*d2-K1
tx = -85.0
ty = -10.706
tz = -35.0
placed_one = body_one.val().located(cq.Location(cq.Vector(tx, ty, tz)))
result = [placed_one, body_two]
placements = {
    "36938_ae684b66_0002_2": [
        [1.0, 0.0, 0.0, tx],
        [0.0, 1.0, 0.0, ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ],
    "36938_ae684b66_0001_2": [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
}

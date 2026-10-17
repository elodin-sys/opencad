from pathlib import Path

import cadquery as cq

here = Path(__file__).resolve().parent
body_one = cq.importers.importStep(str(here / "inputs" / "22337_e2f65ed2_0003_1.step"))
body_two = cq.importers.importStep(str(here / "inputs" / "22337_e2f65ed2_0003_2.step"))

# K1=[0, 106.2985, 0] d1=+Y; K2=[0, 91.5727, 0] d2=-Y; is_flipped; offset=0
# d1 already anti-parallel to d2; T=K2+offset*d2-K1
tx = 0.0
ty = -14.7258
tz = 0.0
placed_one = body_one.val().located(cq.Location(cq.Vector(tx, ty, tz)))
result = [placed_one, body_two]
placements = {
    "22337_e2f65ed2_0003_1": [
        [1.0, 0.0, 0.0, tx],
        [0.0, 1.0, 0.0, ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ],
    "22337_e2f65ed2_0003_2": [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
}

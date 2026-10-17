from pathlib import Path

from build123d import Location, import_step

here = Path(__file__).resolve().parent
one = import_step(here / "inputs" / "22337_e2f65ed2_0003_1.step")
two = import_step(here / "inputs" / "22337_e2f65ed2_0003_2.step")

# Body two stays at identity. d1=(0,1,0) is already anti-parallel to d2=(0,-1,0).
# Offset 0: K1 [0, 106.2985, 0] -> K2 [0, 91.5727, 0].
tx, ty, tz = 0.0, -14.7258, 0.0
placed = one.move(Location((tx, ty, tz)))
result = [placed, two]
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

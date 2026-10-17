from pathlib import Path

from build123d import Location, import_step

here = Path(__file__).resolve().parent
one = import_step(here / "inputs" / "22303_e9723631_0014_1.step")
two = import_step(here / "inputs" / "22303_e9723631_0013_1.step")

# Body two stays at identity. d1=(0,-1,0) must become anti-parallel to d2'=(0,-1,0),
# so R = Rx(180) = diag(1,-1,-1). Offset 0: K1' = K2' = [0,-29.5,0];
# t = K2 - R@K1 = [0,-29.5,0] - [0,-15,0] = [0,-14.5,0].
tx, ty, tz = 0.0, -14.5, 0.0
placed = one.move(Location((tx, ty, tz), (180, 0, 0)))
result = [placed, two]
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

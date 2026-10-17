from pathlib import Path

from build123d import Location, import_step

here = Path(__file__).resolve().parent
one = import_step(here / "inputs" / "23309_76dcf100_0002_1.step")
two = import_step(here / "inputs" / "23309_76dcf100_0003_2.step")

# Body two stays at identity. d1=(0,1,0) must become anti-parallel to d2'=(0,1,0),
# so R = Rx(180) = diag(1,-1,-1). Offset -5: K1' = [11.5, 2.5, -38];
# t = K2 + offset*d2 - R@K1 = [11.5, 7.5, -38] + [0, -5, 0] - [0, -1, 0].
tx, ty, tz = 11.5, 3.5, -38.0
placed = one.move(Location((tx, ty, tz), (180, 0, 0)))
result = [placed, two]
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

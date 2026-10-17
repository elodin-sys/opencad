from pathlib import Path

from build123d import Location, import_step

here = Path(__file__).resolve().parent
one = import_step(here / "inputs" / "84608_204c01e6_0008_1.step")
two = import_step(here / "inputs" / "84608_204c01e6_0008_2.step")

# Body two stays at identity. d1 [-1,0,0] is already anti-parallel to d2 [1,0,0].
# K1 [50, 42, 1.5] -> [11, 40.3792, 49.5496] so (K1'-K2')·d2' = -4 mm.
tx, ty, tz = -39.0, -1.6208, 48.0496
placed = one.move(Location((tx, ty, tz)))
result = [placed, two]
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

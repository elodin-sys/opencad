from pathlib import Path

from build123d import Location, import_step

here = Path(__file__).resolve().parent
one = import_step(here / "inputs" / "36938_ae684b66_0002_2.step")
two = import_step(here / "inputs" / "36938_ae684b66_0001_2.step")

# Body two stays at identity. Body one: identity rotation (d1 already || d2),
# K1 [105, 9.706, 95] -> [20, -1, 60] so (K1'-K2')·d2' = -1 mm.
tx, ty, tz = -85.0, -10.706, -35.0
placed = one.move(Location((tx, ty, tz)))
result = [placed, two]
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

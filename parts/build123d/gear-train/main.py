import math
from pathlib import Path

from build123d import Pos, Rot, import_step

here = Path(__file__).resolve().parent

carrier = import_step(here / "inputs" / "gear-train-carrier.step")
pinion = import_step(here / "inputs" / "gear-train-pinion.step")
wheel = import_step(here / "inputs" / "gear-train-wheel.step")

# Half a wheel pitch: a tooth space faces the pinion along -x.
wheel_angle = 4.5
placed_wheel = wheel.move(Pos(60.0, 0.0, 0.0) * Rot(0.0, 0.0, wheel_angle))

identity = [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0],
]
cosine = math.cos(math.radians(wheel_angle))
sine = math.sin(math.radians(wheel_angle))

result = [carrier, pinion, placed_wheel]
placements = {
    "carrier": identity,
    "pinion": [row[:] for row in identity],
    "wheel": [
        [cosine, -sine, 0.0, 60.0],
        [sine, cosine, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
}
joints = {
    "pinionSpin": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    "wheelSpin": {"origin": [60.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
}

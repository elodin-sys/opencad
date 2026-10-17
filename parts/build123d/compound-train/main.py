from math import cos, radians, sin
from pathlib import Path

from build123d import Location, import_step

here = Path(__file__).resolve().parent


def matrix(tx: float, ty: float, tz: float, angle_deg: float):
    # Right-handed about +z: the child +x ref lands `angle_deg` from the parent +x ref.
    a = radians(angle_deg)
    c, s = cos(a), sin(a)
    return [
        [c, -s, 0.0, tx],
        [s, c, 0.0, ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def place(shape, tx: float, ty: float, tz: float, angle_deg: float):
    return shape.moved(Location((tx, ty, tz), (0.0, 0.0, angle_deg)))


base = import_step(here / "inputs" / "compound-train-base.step")
pinion = place(import_step(here / "inputs" / "compound-train-pinion.step"), 0.0, 0.0, 0.0, 0.0)
idler = place(import_step(here / "inputs" / "compound-train-idler.step"), 60.0, 0.0, 0.0, 4.5)
output = place(import_step(here / "inputs" / "compound-train-output.step"), 120.0, 0.0, 8.5, 6.5)

result = [base, pinion, idler, output]
placements = {
    "base": matrix(0.0, 0.0, 0.0, 0.0),
    "pinion": matrix(0.0, 0.0, 0.0, 0.0),
    "idler": matrix(60.0, 0.0, 0.0, 4.5),
    "output": matrix(120.0, 0.0, 8.5, 6.5),
}
joints = {
    "pinionSpin": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    "idlerSpin": {"origin": [60.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    "outputSpin": {"origin": [120.0, 0.0, 8.5], "axis": [0.0, 0.0, 1.0]},
}

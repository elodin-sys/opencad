import math
from pathlib import Path

from build123d import Pos, Rot, import_step

here = Path(__file__).resolve().parent


def load(name: str):
    return import_step(here / "inputs" / name)


def pose(tx: float, ty: float, tz: float, angle_deg: float):
    radians = math.radians(angle_deg)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    return [
        [cosine, -sine, 0.0, tx],
        [sine, cosine, 0.0, ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def place(shape, tx: float, ty: float, tz: float, angle_deg: float):
    return shape.moved(Pos(tx, ty, tz) * Rot(0, 0, angle_deg))


base = load("planetary-set-base.step")
ring = load("planetary-set-ring.step")
sun = load("planetary-set-sun.step")
carrier = place(load("planetary-set-carrier.step"), 0.0, 0.0, 10.0, 0.0)
planet1 = place(load("planetary-set-planet.step"), 36.0, 0.0, 0.0, 15.0)
planet2 = place(load("planetary-set-planet.step"), -18.0, 31.176915, 0.0, 15.0)
planet3 = place(load("planetary-set-planet.step"), -18.0, -31.176915, 0.0, 15.0)

result = [base, ring, sun, carrier, planet1, planet2, planet3]

placements = {
    "base": pose(0.0, 0.0, 0.0, 0.0),
    "ring": pose(0.0, 0.0, 0.0, 0.0),
    "sun": pose(0.0, 0.0, 0.0, 0.0),
    "carrier": pose(0.0, 0.0, 10.0, 0.0),
    "planet1": pose(36.0, 0.0, 0.0, 15.0),
    "planet2": pose(-18.0, 31.176915, 0.0, 15.0),
    "planet3": pose(-18.0, -31.176915, 0.0, 15.0),
}

joints = {
    "ringFixed": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    "sunSpin": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    "carrierSpin": {"origin": [0.0, 0.0, 10.0], "axis": [0.0, 0.0, 1.0]},
    "planet1Spin": {"origin": [36.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    "planet2Spin": {"origin": [-18.0, 31.176915, 0.0], "axis": [0.0, 0.0, 1.0]},
    "planet3Spin": {"origin": [-18.0, -31.176915, 0.0], "axis": [0.0, 0.0, 1.0]},
}

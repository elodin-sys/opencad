from pathlib import Path

from build123d import Pos, Rot, import_step

here = Path(__file__).resolve().parent

crankLength = 30.0
layerThickness = 5.0
guideOffset = 10.0
rodRestAngle = 5.739170477
restSliderX = 129.498743711

_IDENTITY = [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0],
]


def _load(name):
    return import_step(here / "inputs" / name)


def _matrix(loc):
    x = loc.x_axis.direction
    y = loc.y_axis.direction
    z = loc.z_axis.direction
    p = loc.position
    return [
        [x.X, y.X, z.X, p.X],
        [x.Y, y.Y, z.Y, p.Y],
        [x.Z, y.Z, z.Z, p.Z],
        [0.0, 0.0, 0.0, 1.0],
    ]


ground = _load("crank-slider-ground.step")
crank = _load("crank-slider-crank.step")
rod_at = Pos(crankLength, 0.0, layerThickness) * Rot(0, 0, rodRestAngle)
rod = _load("crank-slider-rod.step").move(rod_at)
slider_at = Pos(restSliderX, guideOffset, 0.0)
slider = _load("crank-slider-slider.step").move(slider_at)

result = [ground, crank, rod, slider]
placements = {
    "ground": _IDENTITY,
    "crank": _IDENTITY,
    "rod": _matrix(rod_at),
    "slider": _matrix(slider_at),
}
joints = {
    "crankPivot": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    "crankPin": {"origin": [crankLength, 0.0, layerThickness], "axis": [0.0, 0.0, 1.0]},
    "guide": {"origin": [restSliderX, guideOffset, 0.0], "axis": [1.0, 0.0, 0.0]},
    "wristPin": {
        "origin": [restSliderX, guideOffset, layerThickness],
        "axis": [0.0, 0.0, 1.0],
    },
}

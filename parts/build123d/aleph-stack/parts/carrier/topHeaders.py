from build123d import Align, Box, Compound, Pos
from params import (
    ffcTopZ,
    ffcX0,
    ffcX1,
    ffcY0,
    ffcY1,
    molexTopZ,
    molexX0,
    molexX1,
    molexY0,
    molexY1,
    pcbThickness,
)

assert molexTopZ > pcbThickness, "infeasible: molexTopZ must stay above the board"
assert ffcTopZ > pcbThickness, "infeasible: ffcTopZ must stay above the board"
assert molexX1 > molexX0 and molexY1 > molexY0, "infeasible: molex envelope is inverted"
assert ffcX1 > ffcX0 and ffcY1 > ffcY0, "infeasible: ffc envelope is inverted"


def _box(x0, y0, z0, x1, y1, z1):
    return Pos(x0, y0, z0) * Box(
        x1 - x0,
        y1 - y0,
        z1 - z0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def apply(body):
    # Overlap the board top so the fuse face is not coincident with the stock.
    seam = 0.02
    tool = Compound(
        children=[
            _box(molexX0, molexY0, pcbThickness - seam, molexX1, molexY1, molexTopZ),
            _box(ffcX0, ffcY0, pcbThickness - seam, ffcX1, ffcY1, ffcTopZ),
        ]
    )
    return body + tool

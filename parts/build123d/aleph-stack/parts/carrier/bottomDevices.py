from build123d import Align, Box, Compound, Pos
from params import (
    gctBottomZ,
    gctX0,
    gctX1,
    gctY0,
    gctY1,
    inductor1X0,
    inductor1X1,
    inductor1Y0,
    inductor1Y1,
    inductor2X0,
    inductor2X1,
    inductor2Y0,
    inductor2Y1,
    inductorBottomZ,
)

assert gctX1 > gctX0 and gctY1 > gctY0, "infeasible: GCT envelope extents are inverted"
assert inductor1X1 > inductor1X0 and inductor1Y1 > inductor1Y0, "infeasible: inductor 1 envelope extents are inverted"
assert inductor2X1 > inductor2X0 and inductor2Y1 > inductor2Y0, "infeasible: inductor 2 envelope extents are inverted"
assert gctBottomZ < 0, "infeasible: GCT box must stay below the board"
assert inductorBottomZ < 0, "infeasible: inductor boxes must stay below the board"

# Past z = 0 into board material that already exists, so the fuse is not coplanar.
fuseOverrun = 0.02


def _envelope(x0, y0, z0, x1, y1):
    return Pos(x0, y0, z0) * Box(
        x1 - x0,
        y1 - y0,
        -z0 + fuseOverrun,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def apply(body):
    tool = Compound(
        children=[
            _envelope(gctX0, gctY0, gctBottomZ, gctX1, gctY1),
            _envelope(inductor1X0, inductor1Y0, inductorBottomZ, inductor1X1, inductor1Y1),
            _envelope(inductor2X0, inductor2Y0, inductorBottomZ, inductor2X1, inductor2Y1),
        ]
    )
    return body + tool

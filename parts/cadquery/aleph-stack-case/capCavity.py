# Single open-bottom pocket; dimensions are in millimetres.
import cadquery as cq
from params import (
    floorTop,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    roofBottom,
    seamGap,
)


def apply(body):
    upper, lower = body
    bottomOverrun = 0.02
    pocketBottom = floorTop + seamGap - bottomOverrun
    cavityLength = innerXMax - innerXMin
    cavityWidth = innerYMax - innerYMin

    assert seamGap > bottomOverrun, "infeasible: pocket bottom overrun must stay inside the seam air"
    assert cavityLength > 0.0, "infeasible: cavity x span must be positive"
    assert cavityWidth > 0.0, "infeasible: cavity y span must be positive"
    assert roofBottom > floorTop + seamGap, "infeasible: cavity ceiling must be above the upper-cap rim"

    # The bottom overruns the cap rim into seam air. The blind ceiling stops
    # exactly at roofBottom; extending it would thin the roof owned elsewhere.
    cavityTool = cq.Workplane("XY", origin=(innerXMin, innerYMin, pocketBottom)).box(
        cavityLength,
        cavityWidth,
        roofBottom - pocketBottom,
        centered=(False, False, False),
    )
    newUpper = upper.cut(cavityTool, clean=True)
    return [newUpper, lower]

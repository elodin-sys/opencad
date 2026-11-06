"""Uncut upper-cap and bottom-cover envelopes, in the Aleph mm frame.

This is the passed blockout with shared, literal-only parameters. Derive
stock boundaries locally so changing wallThickness grows both outer skins
without moving the cavity frame, roof bearing plane, or cover deck.
No cavity, openings, bores, support pads, or hardware are built here.
"""

from build123d import Align, Box, Pos
from params import (
    floorThickness,
    floorTop,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    roofBottom,
    roofThickness,
    seamGap,
    wallThickness,
)

assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
assert roofThickness > 0.0, "infeasible: roofThickness must be positive"
assert floorThickness > 0.0, "infeasible: floorThickness must be positive"
assert seamGap > 0.0, "infeasible: seamGap must be positive"
assert innerXMax > innerXMin, "infeasible: cavity frame needs positive x span"
assert innerYMax > innerYMin, "infeasible: cavity frame needs positive y span"

# Literal outer* and z parameters in params.py record the nominal contract.
# Use the dependency expressions below, not those frozen nominal extents.
stock_x_min = innerXMin - wallThickness
stock_x_max = innerXMax + wallThickness
stock_y_min = innerYMin - wallThickness
stock_y_max = innerYMax + wallThickness
cover_bottom = floorTop - floorThickness
cap_bottom = floorTop + seamGap
cap_top = roofBottom + roofThickness
assert roofBottom > cap_bottom, "infeasible: cap needs a positive cavity height"

upper_cap = Pos(stock_x_min, stock_y_min, cap_bottom) * Box(
    stock_x_max - stock_x_min,
    stock_y_max - stock_y_min,
    cap_top - cap_bottom,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
bottom_cover = Pos(stock_x_min, stock_y_min, cover_bottom) * Box(
    stock_x_max - stock_x_min,
    stock_y_max - stock_y_min,
    floorThickness,
    align=(Align.MIN, Align.MIN, Align.MIN),
)

# Stable primary-body order for every apply(body): upper cap, bottom cover.
# Never fuse across the seam; every later module returns both bodies.
datum = [upper_cap, bottom_cover]

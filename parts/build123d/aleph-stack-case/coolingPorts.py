"""Open the heatsink roof aperture and the two lower side exhaust windows."""

from build123d import Align, Box, Compound, Pos
from params import (
    heatsinkBottom,
    heatsinkCenterX,
    heatsinkCenterY,
    heatsinkLength,
    heatsinkMargin,
    heatsinkWidth,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    roofBottom,
    roofThickness,
    wallThickness,
)


def apply(body):
    """Cut the upper cap once and preserve the original bottom cover."""
    assert isinstance(body, (list, tuple)) and len(body) == 2, (
        "infeasible: coolingPorts requires the ordered cap and cover bodies"
    )
    upper_cap, bottom_cover = body
    assert heatsinkLength > 0.0 and heatsinkWidth > 0.0, "infeasible: heatsink footprint dimensions must be positive"
    assert heatsinkMargin > 0.0, "infeasible: heatsinkMargin must be positive"
    assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
    assert roofThickness > 0.0, "infeasible: roofThickness must be positive"
    assert roofBottom > heatsinkBottom, "infeasible: exhaust windows require a positive height below the roof"

    # The nominal heatOpening* literals are documentation, not edit drivers.
    opening_length = heatsinkLength + 2.0 * heatsinkMargin
    opening_width = heatsinkWidth + 2.0 * heatsinkMargin
    opening_x_min = heatsinkCenterX - opening_length / 2.0
    opening_y_min = heatsinkCenterY - opening_width / 2.0
    assert innerXMin < opening_x_min < opening_x_min + opening_length < innerXMax, (
        "infeasible: the roof aperture must remain inside the cavity x span"
    )
    assert innerYMin < opening_y_min < opening_y_min + opening_width < innerYMax, (
        "infeasible: the roof aperture must remain inside the cavity y span"
    )

    exhaust_width = heatsinkWidth + 2.0 * 1.5
    exhaust_y_min = heatsinkCenterY - exhaust_width / 2.0
    exhaust_height = roofBottom - heatsinkBottom
    assert innerYMin < exhaust_y_min < exhaust_y_min + exhaust_width < innerYMax, (
        "infeasible: exhaust windows must stay between the front and rear walls"
    )

    overrun = 0.03
    roof_tool = Pos(opening_x_min, opening_y_min, roofBottom - overrun) * Box(
        opening_length,
        opening_width,
        roofThickness + 2.0 * overrun,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    # Only the through-wall x ends overrun into air. Exact z limits preserve
    # the sill and bearing roof; wallThickness edits move the outer x ends.
    left_tool = Pos(innerXMin - wallThickness - overrun, exhaust_y_min, heatsinkBottom) * Box(
        wallThickness + 2.0 * overrun,
        exhaust_width,
        exhaust_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    right_tool = Pos(innerXMax - overrun, exhaust_y_min, heatsinkBottom) * Box(
        wallThickness + 2.0 * overrun,
        exhaust_width,
        exhaust_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    tool = Compound([roof_tool, left_tool, right_tool])
    return [upper_cap - tool, bottom_cover]

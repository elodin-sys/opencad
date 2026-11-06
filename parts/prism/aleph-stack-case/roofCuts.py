"""Roof-only aperture and four attachment bores, in millimetres.

The dependency has already opened the cap cavity. Keep the original two-body
ordering, cut only the upper cap, and leave the separate bottom cover untouched.
"""

from build123d import Align, Box, Compound, Cylinder, Pos
from params import (
    heatsinkCenterX,
    heatsinkCenterY,
    heatsinkLength,
    heatsinkMargin,
    heatsinkWidth,
    mountHoleDiameter,
    mountXHigh,
    mountXLow,
    mountYHigh,
    mountYLow,
    roofBottom,
    roofSpacerDiameter,
    roofThickness,
)


def apply(body):
    """Subtract one batched through-roof tool from [upper_cap, bottom_cover]."""
    assert len(body) == 2, "roofCuts requires [upper_cap, bottom_cover]"
    assert heatsinkMargin > 0.0, "infeasible: heatsinkMargin must be positive for heatsink clearance"
    assert heatsinkLength > 0.0 and heatsinkWidth > 0.0, "infeasible: heatsink footprint dimensions must be positive"
    assert roofThickness > 0.0, "infeasible: roofThickness must be positive"
    assert 0.0 < mountHoleDiameter < roofSpacerDiameter, (
        "infeasible: roof bore must leave a positive metal-spacer bearing land"
    )
    assert mountXHigh > mountXLow and mountYHigh > mountYLow, (
        "infeasible: roof attachment axes must have positive spacing"
    )

    upper_cap, bottom_cover = body
    opening_length = heatsinkLength + 2.0 * heatsinkMargin
    opening_width = heatsinkWidth + 2.0 * heatsinkMargin
    opening_x_min = heatsinkCenterX - 0.5 * opening_length
    opening_x_max = heatsinkCenterX + 0.5 * opening_length
    opening_y_min = heatsinkCenterY - 0.5 * opening_width
    opening_y_max = heatsinkCenterY + 0.5 * opening_width

    # Preserve the bearing lands even when the heat margin is edited. The
    # permitted margin sweep changes only aperture edges, not the bore axes.
    bearing_radius = 0.5 * roofSpacerDiameter
    assert opening_x_min > mountXLow + bearing_radius, (
        "infeasible: heat aperture reaches the left roof-spacer bearing lands"
    )
    assert opening_x_max < mountXHigh - bearing_radius, (
        "infeasible: heat aperture reaches the right roof-spacer bearing lands"
    )

    # At these footprints the lower overrun enters the existing cavity, while
    # the upper overrun enters ambient air. No wall or exhaust material is cut.
    overrun = 0.03
    tool_z_min = roofBottom - overrun
    tool_height = roofThickness + 2.0 * overrun
    tools = [
        Pos(opening_x_min, opening_y_min, tool_z_min)
        * Box(
            opening_x_max - opening_x_min,
            opening_y_max - opening_y_min,
            tool_height,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )
    ]
    axes = (
        (mountXLow, mountYLow),
        (mountXHigh, mountYLow),
        (mountXHigh, mountYHigh),
        (mountXLow, mountYHigh),
    )
    tools.extend(
        Pos(x, y, tool_z_min)
        * Cylinder(
            0.5 * mountHoleDiameter,
            tool_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        for x, y in axes
    )

    # One compound cutting tool and one boolean; the disconnected bore tools
    # are deliberately not fused to any stock or exported as hardware.
    roof_tool = Compound(tools)
    return [upper_cap - roof_tool, bottom_cover]

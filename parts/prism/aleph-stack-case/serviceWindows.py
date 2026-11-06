"""Through-wall connector and UART service openings, in assembly millimetres.

The supplied connector body bounds, not PCB layout anchors, define these
projections. Only wall-normal tool depths depend on wallThickness. The
front rectangles overlap; the power/J10 rectangle intentionally bridges
their intervening gap. No other wall, roof, or lower-cover material changes.
"""

from build123d import Align, Box, Pos
from params import (
    baseBoardThickness,
    carrierBottom,
    carrierTop,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    portMargin,
    wallThickness,
)


def _box(x_min, x_max, y_min, y_max, z_min, z_max):
    """A minimum-corner-aligned cutter, with no top-level geometry."""
    assert x_max > x_min, "infeasible: service cutter needs positive x span"
    assert y_max > y_min, "infeasible: service cutter needs positive y span"
    assert z_max > z_min, "infeasible: service cutter needs positive z span"
    return Pos(x_min, y_min, z_min) * Box(
        x_max - x_min,
        y_max - y_min,
        z_max - z_min,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def apply(body):
    """Cut the upper cap once; preserve the separate bottom cover unchanged."""
    upper_cap, bottom_cover = body
    assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
    assert portMargin > 0.0, "infeasible: portMargin must be positive"

    overrun = 0.03
    front_y_min = innerYMin - wallThickness - overrun
    front_y_max = innerYMin + overrun
    rear_y_min = innerYMax - overrun
    rear_y_max = innerYMax + wallThickness + overrun
    side_x_min = innerXMax - overrun
    side_x_max = innerXMax + wallThickness + overrun

    # Base GH housings rise 4.42 above the PCB; base USB-C rises 3.38.
    base_floor = baseBoardThickness - portMargin
    gh_ceiling = baseBoardThickness + 4.42 + portMargin
    base_usb_ceiling = baseBoardThickness + 3.38 + portMargin

    rear_left = 8.08 - portMargin
    rear_right = 73.33 + portMargin
    front_left = min(31.73, 66.24) - portMargin
    front_right = max(64.15, 75.18) + portMargin
    j9_left = 42.16 - portMargin
    j9_right = 50.90 + portMargin
    j9_floor = carrierBottom - 3.11 - portMargin
    j8_left = 62.31 - portMargin
    j8_right = 71.25 + portMargin
    j8_floor = carrierBottom - 3.37 - portMargin
    carrier_lower_ceiling = carrierBottom + portMargin

    # One rectangular envelope for base J12 plus carrier-top J10: no web.
    power_low_y = min(6.65, 7.97) - portMargin
    power_high_y = max(15.39, 16.71) + portMargin
    power_floor = min(baseBoardThickness, carrierTop) - portMargin
    power_ceiling = max(baseBoardThickness + 7.07, carrierTop + 3.11) + portMargin
    side_usb_low_y = 36.43 - portMargin
    side_usb_high_y = 45.37 + portMargin

    assert innerXMin < rear_left < rear_right < innerXMax, "infeasible: rear service projection reaches a corner wall"
    assert innerXMin < front_left < front_right < innerXMax, (
        "infeasible: front service projection reaches a corner wall"
    )
    assert front_left < j9_left < j9_right < j8_left < j8_right < front_right, (
        "infeasible: raised front USB openings must retain their separating web"
    )
    assert base_floor < max(j9_floor, j8_floor) < gh_ceiling, (
        "infeasible: raised front rectangles must overlap the lower window"
    )
    assert gh_ceiling < carrier_lower_ceiling, "infeasible: carrier USB windows must extend above the GH window"
    assert innerYMin < power_low_y < power_high_y < side_usb_low_y, (
        "infeasible: right service windows must remain separate from the corners"
    )
    assert side_usb_low_y < side_usb_high_y < innerYMax, "infeasible: side USB projection reaches the rear corner wall"

    tools = [
        _box(rear_left, rear_right, rear_y_min, rear_y_max, base_floor, gh_ceiling),
        _box(front_left, front_right, front_y_min, front_y_max, base_floor, gh_ceiling),
        _box(
            j9_left,
            j9_right,
            front_y_min,
            front_y_max,
            j9_floor,
            carrier_lower_ceiling,
        ),
        _box(
            j8_left,
            j8_right,
            front_y_min,
            front_y_max,
            j8_floor,
            carrier_lower_ceiling,
        ),
        _box(
            side_x_min,
            side_x_max,
            power_low_y,
            power_high_y,
            power_floor,
            power_ceiling,
        ),
        _box(
            side_x_min,
            side_x_max,
            side_usb_low_y,
            side_usb_high_y,
            base_floor,
            base_usb_ceiling,
        ),
    ]
    # A single boolean union resolves the overlaps of the three front boxes.
    # Disconnected rear/side cutters remain in this one tool compound.
    service_tool = tools[0].fuse(*tools[1:])
    return [upper_cap - service_tool, bottom_cover]

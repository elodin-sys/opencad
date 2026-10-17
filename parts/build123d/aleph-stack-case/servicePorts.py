"""Connector access through the upper cap's rear, front, and right walls."""

from build123d import Align, Box, Compound, Pos
from params import (
    baseBoardThickness,
    carrierBottom,
    carrierTop,
    innerXMax,
    innerYMax,
    innerYMin,
    portMargin,
    wallThickness,
)


def _box(x_min, x_max, y_min, y_max, z_min, z_max):
    """Make one rectangular cutter from its assembly-frame bounds."""
    assert x_max > x_min and y_max > y_min and z_max > z_min, "infeasible: service-port cutter spans must be positive"
    return Pos(x_min, y_min, z_min) * Box(
        x_max - x_min,
        y_max - y_min,
        z_max - z_min,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def apply(body):
    """Cut all service windows once, retaining the original bottom cover."""
    assert isinstance(body, (list, tuple)) and len(body) == 2, (
        "infeasible: service ports require the ordered cap and cover bodies"
    )
    assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
    assert portMargin > 0.0, "infeasible: portMargin must be positive"
    assert carrierTop > carrierBottom > baseBoardThickness > 0.0, (
        "infeasible: the base and carrier board planes must remain ordered"
    )
    upper_cap, bottom_cover = body
    overrun = 0.03
    p = portMargin

    # Match datum.py's working exterior planes, including wallThickness edits.
    rear_y_min = innerYMax - overrun
    rear_y_max = innerYMax + wallThickness + overrun
    front_y_min = innerYMin - wallThickness - overrun
    front_y_max = innerYMin + overrun
    right_x_min = innerXMax - overrun
    right_x_max = innerXMax + wallThickness + overrun

    lower_z = baseBoardThickness - p
    header_top = 5.98 + p
    carrier_top = carrierBottom + p
    j9_bottom = carrierBottom - 3.11 - p
    j8_bottom = carrierBottom - 3.37 - p
    assert lower_z < j8_bottom < header_top < carrier_top, (
        "infeasible: the lower front and raised J8 windows must overlap"
    )
    assert lower_z < j9_bottom < header_top, "infeasible: the lower front and raised J9 windows must overlap"
    assert (62.31 - p) - (50.90 + p) >= 2.10, "infeasible: the web between the raised USB windows needs 2.10 mm"

    # Tangential and z bounds are connector-body projections plus portMargin;
    # only the wall-normal direction overruns the stock into air.
    rear_tool = _box(8.08 - p, 73.33 + p, rear_y_min, rear_y_max, lower_z, header_top)
    front_lower_tool = _box(31.73 - p, 75.18 + p, front_y_min, front_y_max, lower_z, header_top)
    j9_tool = _box(42.16 - p, 50.90 + p, front_y_min, front_y_max, j9_bottom, carrier_top)
    j8_tool = _box(62.31 - p, 71.25 + p, front_y_min, front_y_max, j8_bottom, carrier_top)
    power_j10_tool = _box(right_x_min, right_x_max, 6.65 - p, 16.71 + p, lower_z, carrierTop + 3.11 + p)
    side_usb_tool = _box(right_x_min, right_x_max, 36.43 - p, 45.37 + p, lower_z, 4.94 + p)

    # Fuse overlapping front boxes before batching the four disjoint mouths.
    # Power and J10 share one rectangle, so no thin intermediate web survives.
    front_tool = front_lower_tool + j9_tool + j8_tool
    tool = Compound([rear_tool, front_tool, power_j10_tool, side_usb_tool])
    cut_cap = upper_cap - tool
    return [cut_cap, bottom_cover]

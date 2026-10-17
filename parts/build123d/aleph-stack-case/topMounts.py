"""Drill the four roof attachment bores while preserving the lower cover."""

from build123d import Align, Compound, Cylinder, Pos
from params import (
    mountHoleDiameter,
    mountXHigh,
    mountXLow,
    mountYHigh,
    mountYLow,
    roofBottom,
    roofThickness,
)


def apply(body):
    """Cut only the upper cap at the four board/standoff mounting axes."""
    assert isinstance(body, (list, tuple)) and len(body) == 2, (
        "infeasible: topMounts requires the ordered cap and cover bodies"
    )
    upper_cap, bottom_cover = body
    assert mountHoleDiameter > 0.0, "infeasible: roof bores require a positive diameter"
    assert roofThickness > 0.0, "infeasible: the roof must have positive thickness"
    assert mountXHigh - mountXLow > mountHoleDiameter, "infeasible: roof bores must remain separate in x"
    assert mountYHigh - mountYLow > mountHoleDiameter, "infeasible: roof bores must remain separate in y"

    mount_axes = (
        (mountXLow, mountYLow),
        (mountXHigh, mountYLow),
        (mountXHigh, mountYHigh),
        (mountXLow, mountYHigh),
    )
    # Both tool ends extend into air; the roof bearing planes stay unchanged.
    overrun = 0.03
    tool = Compound(
        [
            Pos(x, y, roofBottom - overrun)
            * Cylinder(
                mountHoleDiameter / 2.0,
                roofThickness + 2.0 * overrun,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            for x, y in mount_axes
        ]
    )
    return [upper_cap - tool, bottom_cover]

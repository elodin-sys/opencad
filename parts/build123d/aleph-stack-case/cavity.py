"""Open the underside of the upper cap while preserving the separate cover."""

from build123d import Align, Box, Compound, Pos
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
    """Return the pocketed cap and the original, untouched bottom cover."""
    assert isinstance(body, (list, tuple)) and len(body) == 2, (
        "infeasible: cavity requires the ordered cap and cover bodies"
    )
    upper_cap, bottom_cover = body
    cap_base_z = floorTop + seamGap
    assert innerXMax > innerXMin, "infeasible: cavity x span must be positive"
    assert innerYMax > innerYMin, "infeasible: cavity y span must be positive"
    assert roofBottom > cap_base_z, "infeasible: cavity depth must be positive"

    # Overrun only the open underside; shared inner planes stay exact so later
    # ports and roof bores connect to this air without a residual membrane.
    overrun = 0.03
    cavity_tool = Pos(innerXMin, innerYMin, cap_base_z - overrun) * Box(
        innerXMax - innerXMin,
        innerYMax - innerYMin,
        roofBottom - cap_base_z + overrun,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    tool = Compound([cavity_tool])
    cut_cap = upper_cap - tool
    return [cut_cap, bottom_cover]

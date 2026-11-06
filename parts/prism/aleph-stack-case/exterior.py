"""Bottom-open upper cap only, in millimetres; keep the cover unchanged."""

from build123d import Align, Box, Pos
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
    """Hollow the first datum body, returning [upper_cap, bottom_cover]."""
    assert len(body) == 2, "exterior requires the ordered cap and cover pair"
    upper_cap, bottom_cover = body
    overrun = 0.03
    cap_bottom = floorTop + seamGap
    assert seamGap > overrun, "infeasible: cavity overrun must stay in seam air"
    assert innerXMax > innerXMin, "infeasible: cavity x span must be positive"
    assert innerYMax > innerYMin, "infeasible: cavity y span must be positive"
    assert roofBottom > cap_bottom, "infeasible: cavity height must be positive"

    # Only the lower opening crosses a pre-existing stock face. The cutter
    # overruns that rim into seam air; its other faces create the cavity walls
    # and roof bearing plane, so they terminate exactly on the shared datums.
    cavity_tool = Pos(innerXMin, innerYMin, cap_bottom - overrun) * Box(
        innerXMax - innerXMin,
        innerYMax - innerYMin,
        roofBottom - cap_bottom + overrun,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    upper_shell = upper_cap - cavity_tool
    return [upper_shell, bottom_cover]

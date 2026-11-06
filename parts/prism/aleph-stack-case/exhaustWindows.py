"""Paired high end-wall exhaust cuts; millimetres in the Aleph frame."""

from build123d import Align, Box, Compound, Pos
from params import (
    heatsinkBottom,
    heatsinkCenterY,
    heatsinkWidth,
    innerXMax,
    innerXMin,
    roofBottom,
    wallThickness,
)


def apply(body):
    """Cut the upper cap's two exhaust slots, preserving the separate cover."""
    assert len(body) == 2, "exhaustWindows requires the ordered cap and cover pair"
    assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
    assert heatsinkWidth > 0.0, "infeasible: heatsinkWidth must be positive"
    assert innerXMax > innerXMin, "infeasible: cavity x span must be positive"
    assert roofBottom > heatsinkBottom, "infeasible: exhaust height must be positive"
    upper_cap, bottom_cover = body

    # Fixed photo-size/centering allowance, deliberately NOT heatsinkMargin.
    # Wall edits change cutter depth only; the yz projections remain invariant.
    uncertainty_allowance = 1.5
    overrun = 0.03
    slot_width = heatsinkWidth + 2.0 * uncertainty_allowance
    slot_height = roofBottom - heatsinkBottom
    slot_y_min = heatsinkCenterY - slot_width / 2.0
    tools = [
        Pos(x_min, slot_y_min, heatsinkBottom)
        * Box(
            wallThickness + 2.0 * overrun,
            slot_width,
            slot_height,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )
        for x_min in (
            innerXMin - wallThickness - overrun,
            innerXMax - overrun,
        )
    ]

    # Batch the disjoint cutters into one tool and subtract once. Only x faces
    # overrun into ambient/cavity air. The top MUST stop at roofBottom: this is
    # the shared underside boundary, not permission to cut roof material.
    exhaust_tool = Compound(tools)
    return [upper_cap - exhaust_tool, bottom_cover]

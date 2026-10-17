import cadquery as cq  # isort: skip
import math

from params import (
    keyAxisX,
    keyBackDepth,
    keyLowerExitDiameter,
    keyLowerExitStart,
    keyLowerRecessDiameter,
    keyMiddleEnd,
    keyUpperBoreDiameter,
    keyUpperCounterboreDiameter,
    keyUpperRecessDiameter,
    keyUpperZ,
    lowerTransitionLength,
    plateThickness,
)

_OVERRUN = 0.03


def _revolved_tool(profile, axis_z):
    return (
        cq.Workplane("XY", origin=(keyAxisX, 0.0, axis_z))
        .polyline(profile)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )


def apply(body):
    assert 0.0 < keyBackDepth < keyMiddleEnd < keyLowerExitStart < plateThickness, (
        "infeasible: keyhole depth stations must be ordered inside the plate"
    )
    assert 0.0 < keyUpperRecessDiameter < keyUpperBoreDiameter < keyUpperCounterboreDiameter, (
        "infeasible: upper keyhole diameters must increase toward the front"
    )
    assert 0.0 < keyLowerExitDiameter < keyLowerRecessDiameter, (
        "infeasible: lower keyhole taper must narrow toward the front"
    )
    assert 0.0 < lowerTransitionLength < plateThickness - keyBackDepth, (
        "infeasible: lower transition length must fit inside the plate"
    )
    assert keyUpperZ > 0.0, "infeasible: upper opening must lie above the lower axis"

    back, front = -_OVERRUN, plateThickness + _OVERRUN
    upper_back_r = keyUpperRecessDiameter / 2.0
    upper_middle_r = keyUpperBoreDiameter / 2.0
    upper_front_r = keyUpperCounterboreDiameter / 2.0
    lower_back_r = keyLowerRecessDiameter / 2.0
    lower_front_r = keyLowerExitDiameter / 2.0
    widest_r = max(upper_front_r, lower_back_r)
    assert -15.0 <= keyAxisX - widest_r and keyAxisX + widest_r <= 11.0, (
        "infeasible: keyhole diameters cross this module's x region"
    )
    assert lower_back_r <= 11.25 and keyUpperZ + upper_front_r <= 29.4, (
        "infeasible: keyhole diameters cross this module's z region"
    )

    # Q1: use the dimension table and sections. Revolving complete profiles
    # preserves exact internal shoulders; only the two datum ends overrun.
    upper_tool = _revolved_tool(
        [
            (0.0, back),
            (upper_back_r, back),
            (upper_back_r, keyBackDepth),
            (upper_middle_r, keyBackDepth),
            (upper_middle_r, keyMiddleEnd),
            (upper_front_r, keyMiddleEnd),
            (upper_front_r, front),
            (0.0, front),
        ],
        keyUpperZ,
    )
    # The two axial stations define the derived lowerTransitionLength. There
    # is one conical wall between them, with no intermediate D16 cylinder.
    lower_tool = _revolved_tool(
        [
            (0.0, back),
            (lower_back_r, back),
            (lower_back_r, keyBackDepth),
            (lower_front_r, keyLowerExitStart),
            (lower_front_r, front),
            (0.0, front),
        ],
        0.0,
    )

    # Dimension-sheet inclined rows 8/9. Normalize the rounded normals and
    # translate their documented anchors with the common keyhole axis.
    normal_length = math.hypot(0.9659, 0.2588)
    nx, nz = 0.9659 / normal_length, -0.2588 / normal_length
    left_anchor_x, left_anchor_z = keyAxisX - 6.566, keyUpperZ - 11.22
    right_anchor_x, right_anchor_z = keyAxisX + 4.594, keyUpperZ - 3.86
    left_c = nx * left_anchor_x + nz * left_anchor_z
    right_c = -nx * right_anchor_x + nz * right_anchor_z
    left_low, right_low = left_c / nx, -right_c / nx
    left_high = (left_c - nz * keyUpperZ) / nx
    right_high = (nz * keyUpperZ - right_c) / nx

    lower_radius_at_middle = lower_back_r - (lower_back_r - lower_front_r) * (
        (keyMiddleEnd - keyBackDepth) / (keyLowerExitStart - keyBackDepth)
    )
    assert keyAxisX - lower_radius_at_middle < left_low < right_low < keyAxisX + lower_radius_at_middle, (
        "infeasible: neck must terminate inside the lower taper"
    )
    assert keyAxisX - upper_back_r < left_high < right_high < keyAxisX + upper_back_r, (
        "infeasible: neck must terminate inside the upper recess"
    )
    neck_tool = (
        cq.Workplane("XZ", origin=(0.0, back, 0.0))
        .polyline([(left_low, 0.0), (right_low, 0.0), (right_high, keyUpperZ), (left_high, keyUpperZ)])
        .close()
        .extrude(back - keyMiddleEnd)
    )

    # Each neck end is buried in a round tool. The front D26 tool trims the
    # upper ends of both planar walls at y=8; all booleans meet in one cutter.
    cutter = upper_tool.union(lower_tool, clean=True).union(neck_tool, clean=True)
    return body.cut(cutter, clean=True)

"""Connected keyhole cuts, using the provisional table-and-section layout."""

from math import hypot

from build123d import Align, Cone, Cylinder, Plane, Polygon, Pos, Rot, extrude
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

overrun = 0.03


def _cylinder(diameter, start, end, height):
    """Place a cutter on the common +y axis."""
    return (
        Pos(keyAxisX, start, height)
        * Rot(-90.0, 0.0, 0.0)
        * Cylinder(
            diameter / 2.0,
            end - start,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )


def _neck_side(x, z, nx, nz, height):
    """Intersect a documented, normalized side plane with a z station."""
    magnitude = hypot(nx, nz)
    assert magnitude > 0.0, "infeasible: the neck plane normal must be nonzero"
    nx, nz = nx / magnitude, nz / magnitude
    assert abs(nx) > 0.01, "infeasible: the neck plane must define an x coordinate"
    offset = nx * x + nz * z
    return (offset - nz * height) / nx


def _neck():
    # The y-independent planes are pinned to the documented points.  The
    # horizontal closing edges are buried in the two circular openings.
    low, high = 0.0, keyUpperZ
    left_low = _neck_side(-8.566, 5.18, 0.9659, -0.2588, low)
    left_high = _neck_side(-8.566, 5.18, 0.9659, -0.2588, high)
    right_low = _neck_side(2.594, 12.54, -0.9659, -0.2588, low)
    right_high = _neck_side(2.594, 12.54, -0.9659, -0.2588, high)
    assert left_low < right_low and left_high < right_high, "infeasible: neck sides must not cross"
    profile = Plane.XZ * Polygon(
        (left_low, low),
        (right_low, low),
        (right_high, high),
        (left_high, high),
        align=None,
    )
    return Pos(0.0, -overrun, 0.0) * extrude(profile, amount=keyMiddleEnd + overrun, dir=(0.0, 1.0, 0.0))


def apply(body):
    """Union the connected cavity tools, then subtract once from the stock."""
    assert 0.0 < keyBackDepth < keyMiddleEnd < plateThickness, "infeasible: upper depth stations must be ordered"
    assert keyBackDepth < keyLowerExitStart < plateThickness, "infeasible: lower depth stations must be ordered"
    assert 0.0 < keyUpperRecessDiameter < keyUpperBoreDiameter < keyUpperCounterboreDiameter, (
        "infeasible: upper recess, bore and counterbore diameters must increase"
    )
    assert 0.0 < keyLowerExitDiameter < keyLowerRecessDiameter, "infeasible: lower taper must narrow"
    assert lowerTransitionLength > 0.0, "infeasible: lowerTransitionLength must be positive"
    assert keyUpperZ > 0.0, "infeasible: the upper axis must be above the lower axis"

    # Smaller upper cutters overrun into the next, larger opening; their
    # overlap leaves both shoulder planes at their exact nominal stations.
    tools = [
        _cylinder(keyUpperRecessDiameter, -overrun, keyBackDepth + overrun, keyUpperZ),
        _cylinder(keyUpperBoreDiameter, keyBackDepth, keyMiddleEnd + overrun, keyUpperZ),
        _cylinder(keyUpperCounterboreDiameter, keyMiddleEnd, plateThickness + overrun, keyUpperZ),
        _cylinder(keyLowerRecessDiameter, -overrun, keyBackDepth, 0.0),
    ]

    # Retain the complete lower cone, without an invented diameter-16
    # cylindrical segment.  Its far end overruns inside the diameter-14
    # exit, so the exposed cone still ends at keyLowerExitStart.
    taper_slope = (keyLowerRecessDiameter - keyLowerExitDiameter) / (2.0 * lowerTransitionLength)
    cone_top_radius = keyLowerRecessDiameter / 2.0 - taper_slope * (keyLowerExitStart - keyBackDepth + overrun)
    assert cone_top_radius > 0.0, "infeasible: the extended lower cone must retain a positive radius"
    tools.append(
        Pos(keyAxisX, keyBackDepth, 0.0)
        * Rot(-90.0, 0.0, 0.0)
        * Cone(
            keyLowerRecessDiameter / 2.0,
            cone_top_radius,
            keyLowerExitStart - keyBackDepth + overrun,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
    tools.append(_cylinder(keyLowerExitDiameter, keyLowerExitStart - overrun, plateThickness + overrun, 0.0))
    tools.append(_neck())
    cutter = tools[0].fuse(*tools[1:])
    assert len(cutter.solids()) == 1 and cutter.is_valid, "infeasible: keyhole cutters must form one valid solid"
    shaped = body - cutter
    assert len(shaped.solids()) == 1 and shaped.is_valid, "infeasible: keyhole cut must leave one valid solid"
    return shaped

"""Rounded through-windows and paired underside pockets on fixed VTX axes."""

from math import atan2, degrees, hypot, sqrt

from build123d import Align, Cylinder, Polygon, Pos, SlotCenterToCenter, extrude, fillet
from params import (
    armWidth,
    innerPatternPitch,
    m2HoleDiameter,
    outerPatternPitch,
    patternCenterY,
    plateThickness,
    plateTopZ,
    slotDepth,
    slotWidth,
    windowBaseX,
    windowBaseY,
    windowCornerRadius,
)


def apply(body):
    assert 0 < slotDepth < plateThickness, "slotDepth must leave positive plate skin"
    assert slotWidth > 0, "slotWidth must be positive"
    assert 0 < m2HoleDiameter < slotWidth, "holes must fit inside the pockets"
    assert 0 < innerPatternPitch < outerPatternPitch, "pattern pitches must be ordered"
    assert armWidth > 0, "armWidth must be positive"
    assert windowCornerRadius > 0, "windowCornerRadius must be positive"
    overrun = 0.03
    bottom = plateTopZ - plateThickness
    ceiling = bottom + slotDepth
    offset = armWidth / sqrt(2)
    assert min(windowBaseX, windowBaseY) > offset + 3 * windowCornerRadius, "window corners must fit between arms"
    tools = []
    # Parallel diagonal edges are armWidth apart, normal to each diagonal.
    for sign in (-1, 1):
        for side in (False, True):
            base = windowBaseX if side else windowBaseY
            points = [(offset, 0), (base, base - offset), (base, -base + offset)]
            points = [(sign * x, y + patternCenterY) if side else (y, sign * x + patternCenterY) for x, y in points]
            triangle = Polygon(*points, align=None)
            rounded = fillet(triangle.vertices(), windowCornerRadius)
            tools.append(
                Pos(0, 0, bottom - overrun) * extrude(rounded, amount=plateThickness + 2 * overrun, dir=(0, 0, 1))
            )
    for sx in (-1, 1):
        for sy in (-1, 1):
            inner = (sx * innerPatternPitch / 2, patternCenterY + sy * innerPatternPitch / 2)
            outer = (sx * outerPatternPitch / 2, patternCenterY + sy * outerPatternPitch / 2)
            dx, dy = outer[0] - inner[0], outer[1] - inner[1]
            capsule = Pos((inner[0] + outer[0]) / 2, (inner[1] + outer[1]) / 2) * SlotCenterToCenter(
                hypot(dx, dy), slotWidth, rotation=degrees(atan2(dy, dx))
            )
            tools.append(Pos(0, 0, bottom - overrun) * extrude(capsule, amount=slotDepth + overrun))
            for x, y in (inner, outer):
                tools.append(
                    Pos(x, y, ceiling - overrun)
                    * Cylinder(
                        m2HoleDiameter / 2,
                        plateTopZ - ceiling + 2 * overrun,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                )
    # Fuse overlapping pocket/hole tools before the single stock subtraction.
    tool = tools[0].fuse(*tools[1:])
    return body - tool

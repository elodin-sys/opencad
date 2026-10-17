from build123d import Align, Box, Compound, Cylinder, Pos, RectangleRounded, extrude
from params import (
    cornerRadius,
    erfBottomZ,
    erfX0,
    erfX1,
    erfY0,
    erfY1,
    latchX0,
    latchX1,
    latchY0,
    mountHoleDiameter,
    mountHoleX0,
    mountHoleX1,
    mountHoleY0,
    mountHoleY1,
    pcbLength,
    pcbThickness,
    pcbWidth,
    seatHoleDiameter,
    seatZ,
    sodimmTopZ,
    sodimmX0,
    sodimmX1,
    sodimmY0,
    sodimmY1,
    spacerDiameter,
    spacerX0,
    spacerX1,
    spacerY,
    usbBotX0,
    usbBotX1,
    usbBotY0,
    usbBotY1,
    usbBotZ,
    usbTopX0,
    usbTopX1,
    usbTopY0,
    usbTopY1,
    usbTopZ,
)

assert pcbLength > 0 and pcbWidth > 0 and pcbThickness > 0, "infeasible: board size"
assert cornerRadius > 0, "infeasible: corner radius"
assert mountHoleDiameter > 0, "infeasible: mount hole diameter"
assert seatHoleDiameter > 0, "infeasible: seat hole diameter"
assert mountHoleX1 > mountHoleX0, "infeasible: mount hole x span"
assert mountHoleY1 > mountHoleY0, "infeasible: mount hole y span"
assert spacerDiameter > seatHoleDiameter, "infeasible: spacer must bear on the board"
assert seatZ > pcbThickness, "infeasible: seat must stay above the board"
assert sodimmTopZ > seatZ, "infeasible: sodimmTopZ must stay above seatZ"


def envelope(x0, y0, z0, x1, y1, z1):
    assert x1 > x0 and y1 > y0 and z1 > z0, "infeasible: envelope extents are inverted"
    return Pos(x0, y0, z0) * Box(
        x1 - x0,
        y1 - y0,
        z1 - z0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def spacer(x):
    return Pos(x, spacerY, pcbThickness) * Cylinder(
        spacerDiameter / 2,
        seatZ - pcbThickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def board_hole(x, y, diameter):
    # Cut 0.02 mm past both board faces into air so the tool is not coplanar.
    overrun = 0.02
    return Pos(x, y, -overrun) * Cylinder(
        diameter / 2,
        pcbThickness + 2 * overrun,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


board = extrude(
    Pos(pcbLength / 2, pcbWidth / 2) * RectangleRounded(pcbLength, pcbWidth, cornerRadius),
    pcbThickness,
) - Compound(
    children=[
        board_hole(mountHoleX0, mountHoleY0, mountHoleDiameter),
        board_hole(mountHoleX1, mountHoleY0, mountHoleDiameter),
        board_hole(mountHoleX1, mountHoleY1, mountHoleDiameter),
        board_hole(mountHoleX0, mountHoleY1, mountHoleDiameter),
        board_hole(spacerX0, spacerY, seatHoleDiameter),
        board_hole(spacerX1, spacerY, seatHoleDiameter),
    ]
)

datum = (
    board
    + envelope(sodimmX0, sodimmY0, pcbThickness, sodimmX1, sodimmY1, sodimmTopZ)
    + envelope(sodimmX0, latchY0, pcbThickness, latchX0, sodimmY0, sodimmTopZ)
    + envelope(latchX1, latchY0, pcbThickness, sodimmX1, sodimmY0, sodimmTopZ)
    + envelope(usbTopX0, usbTopY0, pcbThickness, usbTopX1, usbTopY1, usbTopZ)
    + envelope(usbBotX0, usbBotY0, usbBotZ, usbBotX1, usbBotY1, 0.0)
    + envelope(erfX0, erfY0, erfBottomZ, erfX1, erfY1, 0.0)
    + spacer(spacerX0)
    + spacer(spacerX1)
)

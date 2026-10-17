from build123d import Align, Box, Compound, Cylinder, Polygon, Pos, extrude

boardLength = 85.0
boardWidth = 56.0
pcbThickness = 1.6
mountX = 3.5
mountY = 3.5
mountPitchX = 58.0
mountPitchY = 49.0
boardMountDiameter = 2.7
underBoardDepth = 3.0
componentFreeRadius = 3.1
edgeClearance = 0.5
headroom = 20.0
wallThickness = 2.4
standoffHeight = 5.0
standoffDiameter = 6.2
pilotDiameter = 2.5
pilotDepth = 5.0
lidHoleDiameter = 3.0
lidThickness = 4.0
cornerPostWidth = 8.0
closureGap = 0.05
usbCx = 11.2
hdmi0X = 25.8
hdmi1X = 39.2
usbAUpperY = 47.0
usbALowerY = 29.1
rj45Y = 10.2
sdYMin = 22.0
sdYMax = 34.0

assert headroom > 0, "infeasible: headroom must be positive"
assert boardLength > 0, "infeasible: boardLength must be positive"
assert boardWidth > 0, "infeasible: boardWidth must be positive"
assert pcbThickness > 0, "infeasible: pcbThickness must be positive"
assert mountX > 0, "infeasible: mountX must be positive"
assert mountY > 0, "infeasible: mountY must be positive"
assert mountPitchX > 0, "infeasible: mountPitchX must be positive"
assert mountPitchY > 0, "infeasible: mountPitchY must be positive"
assert boardMountDiameter > 0, "infeasible: boardMountDiameter must be positive"
assert underBoardDepth > 0, "infeasible: underBoardDepth must be positive"
assert componentFreeRadius > 0, "infeasible: componentFreeRadius must be positive"
assert edgeClearance > 0, "infeasible: edgeClearance must be positive"
assert wallThickness > 0, "infeasible: wallThickness must be positive"
assert standoffHeight > 0, "infeasible: standoffHeight must be positive"
assert standoffDiameter > 0, "infeasible: standoffDiameter must be positive"
assert pilotDiameter > 0, "infeasible: pilotDiameter must be positive"
assert pilotDepth > 0, "infeasible: pilotDepth must be positive"
assert lidHoleDiameter > 0, "infeasible: lidHoleDiameter must be positive"
assert lidThickness > 0, "infeasible: lidThickness must be positive"
assert cornerPostWidth > 0, "infeasible: cornerPostWidth must be positive"
assert closureGap >= 0, "infeasible: closureGap must be non-negative"
assert usbCx > 0, "infeasible: usbCx must be positive"
assert hdmi0X > 0, "infeasible: hdmi0X must be positive"
assert hdmi1X > 0, "infeasible: hdmi1X must be positive"
assert usbAUpperY > 0, "infeasible: usbAUpperY must be positive"
assert usbALowerY > 0, "infeasible: usbALowerY must be positive"
assert rj45Y > 0, "infeasible: rj45Y must be positive"
assert sdYMax > sdYMin, "infeasible: sd card slot must have positive width"

inner_left = -edgeClearance
inner_right = boardLength + edgeClearance
inner_front = -edgeClearance
inner_back = boardWidth + edgeClearance
wall_left = inner_left - wallThickness
wall_right = inner_right + wallThickness
wall_front = inner_front - wallThickness
wall_back = inner_back + wallThickness
post_left = inner_left - cornerPostWidth
post_right = inner_right + cornerPostWidth
post_front = inner_front - cornerPostWidth
post_back = inner_back + cornerPostWidth
floor_top = -standoffHeight
floor_bottom = floor_top - wallThickness
lid_bottom = pcbThickness + headroom
rim_z = lid_bottom - closureGap
lid_top = lid_bottom + lidThickness
overshoot = 0.05

assert rim_z > floor_top, "infeasible: base rim must sit above the floor"
assert lid_bottom > rim_z, "infeasible: lid must sit above the base rim"
assert standoffHeight + wallThickness > pilotDepth, "infeasible: standoff pilots would break the floor"
assert rim_z - floor_bottom > pilotDepth, "infeasible: corner pilots would break the floor"

outline = Polygon(
    (post_left, post_front),
    (inner_left, post_front),
    (inner_left, wall_front),
    (inner_right, wall_front),
    (inner_right, post_front),
    (post_right, post_front),
    (post_right, inner_front),
    (wall_right, inner_front),
    (wall_right, inner_back),
    (post_right, inner_back),
    (post_right, post_back),
    (inner_right, post_back),
    (inner_right, wall_back),
    (inner_left, wall_back),
    (inner_left, post_back),
    (post_left, post_back),
    (post_left, inner_back),
    (wall_left, inner_back),
    (wall_left, inner_front),
    (post_left, inner_front),
)

base_blank = Pos(0, 0, floor_bottom) * extrude(outline, amount=rim_z - floor_bottom)
cavity = Pos(inner_left, inner_front, floor_top) * Box(
    inner_right - inner_left,
    inner_back - inner_front,
    rim_z - floor_top + overshoot,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
shell = base_blank - cavity

mounts = (
    (mountX, mountY),
    (mountX + mountPitchX, mountY),
    (mountX, mountY + mountPitchY),
    (mountX + mountPitchX, mountY + mountPitchY),
)
bosses = Compound(
    [
        Pos(x, y, floor_top - overshoot)
        * Cylinder(
            standoffDiameter / 2,
            standoffHeight + overshoot,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        for x, y in mounts
    ]
)
board_pilots = Compound(
    [
        Pos(x, y, -pilotDepth)
        * Cylinder(
            pilotDiameter / 2,
            pilotDepth + overshoot,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        for x, y in mounts
    ]
)

plug_boxes = (
    (usbCx - 6.5, -25.0, pcbThickness, usbCx + 6.5, 0.0, pcbThickness + 7.0),
    (hdmi0X - 6.0, -25.0, pcbThickness, hdmi0X + 6.0, 0.0, pcbThickness + 6.5),
    (hdmi1X - 6.0, -25.0, pcbThickness, hdmi1X + 6.0, 0.0, pcbThickness + 6.5),
    (boardLength, usbAUpperY - 7.5, pcbThickness, boardLength + 25.0, usbAUpperY + 7.5, pcbThickness + 17.0),
    (boardLength, usbALowerY - 7.5, pcbThickness, boardLength + 25.0, usbALowerY + 7.5, pcbThickness + 17.0),
    (boardLength, rj45Y - 8.5, pcbThickness, boardLength + 25.0, rj45Y + 8.5, pcbThickness + 15.0),
    (-25.0, sdYMin, -underBoardDepth, 0.0, sdYMax, 0.0),
)


def _clipped_box(x0, y0, z0, x1, y1, z1):
    x0 = max(x0, post_left)
    y0 = max(y0, post_front)
    x1 = min(x1, post_right)
    y1 = min(y1, post_back)
    assert x1 > x0 and y1 > y0 and z1 > z0, "infeasible: clipped cutter has no volume"
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN))


notches = Compound([_clipped_box(x0, y0, z0, x1, y1, rim_z + overshoot) for x0, y0, z0, x1, y1, z1 in plug_boxes])

corners = (
    (inner_left - cornerPostWidth / 2, inner_front - cornerPostWidth / 2),
    (inner_right + cornerPostWidth / 2, inner_front - cornerPostWidth / 2),
    (inner_left - cornerPostWidth / 2, inner_back + cornerPostWidth / 2),
    (inner_right + cornerPostWidth / 2, inner_back + cornerPostWidth / 2),
)
corner_pilots = Compound(
    [
        Pos(x, y, rim_z - pilotDepth)
        * Cylinder(
            pilotDiameter / 2,
            pilotDepth + overshoot,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        for x, y in corners
    ]
)
base = (shell + bosses) - Compound([board_pilots, notches, corner_pilots])

lid_blank = Pos(0, 0, lid_bottom) * extrude(outline, amount=lidThickness)
lid_holes = Compound(
    [
        Pos(x, y, lid_bottom - 0.02)
        * Cylinder(
            lidHoleDiameter / 2,
            lidThickness + 0.04,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        for x, y in corners
    ]
)
lid = lid_blank - lid_holes
lid_reliefs = [
    _clipped_box(x0, y0, z0, x1, y1, z1) for x0, y0, z0, x1, y1, z1 in plug_boxes if z1 > lid_bottom and z0 < lid_top
]
if lid_reliefs:
    lid = lid - Compound(lid_reliefs)

result = [base, lid]

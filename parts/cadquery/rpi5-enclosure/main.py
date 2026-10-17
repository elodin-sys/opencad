import cadquery as cq

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
assert wallThickness >= 2, "infeasible: wallThickness below 2 mm"
assert standoffHeight > 0, "infeasible: standoffHeight must be positive"
assert standoffHeight > underBoardDepth, "infeasible: standoffHeight does not clear bottom components"
assert standoffHeight >= pilotDepth, "infeasible: standoffHeight shorter than pilotDepth"
assert standoffDiameter > 0, "infeasible: standoffDiameter must be positive"
assert standoffDiameter / 2 <= componentFreeRadius, "infeasible: standoff boss leaves the component-free ring"
assert pilotDiameter > 0, "infeasible: pilotDiameter must be positive"
assert pilotDiameter < boardMountDiameter, "infeasible: pilot larger than the board hole"
assert pilotDepth > 0, "infeasible: pilotDepth must be positive"
assert lidHoleDiameter > 0, "infeasible: lidHoleDiameter must be positive"
assert lidThickness >= 2, "infeasible: lidThickness below 2 mm"
assert cornerPostWidth > 0, "infeasible: cornerPostWidth must be positive"
assert cornerPostWidth > lidHoleDiameter, "infeasible: lid hole larger than the corner post"
assert cornerPostWidth > pilotDiameter, "infeasible: corner pilot larger than the corner post"
assert 0 <= closureGap <= 0.1, "infeasible: closureGap outside 0..0.1 mm"
assert usbCx > 0, "infeasible: usbCx must be positive"
assert hdmi0X > 0, "infeasible: hdmi0X must be positive"
assert hdmi1X > 0, "infeasible: hdmi1X must be positive"
assert usbAUpperY > 0, "infeasible: usbAUpperY must be positive"
assert usbALowerY > 0, "infeasible: usbALowerY must be positive"
assert rj45Y > 0, "infeasible: rj45Y must be positive"
assert sdYMin > 0, "infeasible: sdYMin must be positive"
assert sdYMax > sdYMin, "infeasible: sdYMax must exceed sdYMin"

cutPast = 0.05
floorInterior = -standoffHeight
floorExterior = -standoffHeight - wallThickness
lidUnderside = pcbThickness + headroom
baseRim = lidUnderside - closureGap
baseHeight = baseRim - floorExterior

cavityX0 = -edgeClearance
cavityY0 = -edgeClearance
cavityX1 = boardLength + edgeClearance
cavityY1 = boardWidth + edgeClearance
ringX0 = cavityX0 - wallThickness
ringY0 = cavityY0 - wallThickness
ringX1 = cavityX1 + wallThickness
ringY1 = cavityY1 + wallThickness

footprintO = [
    (-edgeClearance - cornerPostWidth, -edgeClearance - cornerPostWidth),
    (cavityX0, -edgeClearance - cornerPostWidth),
    (cavityX0, ringY0),
    (cavityX1, ringY0),
    (cavityX1, -edgeClearance - cornerPostWidth),
    (cavityX1 + cornerPostWidth, -edgeClearance - cornerPostWidth),
    (cavityX1 + cornerPostWidth, cavityY0),
    (ringX1, cavityY0),
    (ringX1, cavityY1),
    (cavityX1 + cornerPostWidth, cavityY1),
    (cavityX1 + cornerPostWidth, cavityY1 + cornerPostWidth),
    (cavityX1, cavityY1 + cornerPostWidth),
    (cavityX1, ringY1),
    (cavityX0, ringY1),
    (cavityX0, cavityY1 + cornerPostWidth),
    (-edgeClearance - cornerPostWidth, cavityY1 + cornerPostWidth),
    (-edgeClearance - cornerPostWidth, cavityY1),
    (ringX0, cavityY1),
    (ringX0, cavityY0),
    (-edgeClearance - cornerPostWidth, cavityY0),
]


def prism_o(z0, height):
    sketch = cq.Workplane("XY").workplane(offset=z0).moveTo(footprintO[0][0], footprintO[0][1])
    for x, y in footprintO[1:]:
        sketch = sketch.lineTo(x, y)
    return sketch.close().extrude(height)


def box_tool(xmin, ymin, zmin, xmax, ymax, zmax):
    return (
        cq.Workplane("XY")
        .workplane(offset=zmin)
        .center(xmin, ymin)
        .rect(xmax - xmin, ymax - ymin, centered=False)
        .extrude(zmax - zmin)
    )


def cylinder_tools(points, radius, zmin, zmax):
    return cq.Workplane("XY").workplane(offset=zmin).pushPoints(points).circle(radius).extrude(zmax - zmin)


mounts = [
    (mountX, mountY),
    (mountX + mountPitchX, mountY),
    (mountX, mountY + mountPitchY),
    (mountX + mountPitchX, mountY + mountPitchY),
]
corners = [
    (-edgeClearance - cornerPostWidth / 2, -edgeClearance - cornerPostWidth / 2),
    (boardLength + edgeClearance + cornerPostWidth / 2, -edgeClearance - cornerPostWidth / 2),
    (-edgeClearance - cornerPostWidth / 2, boardWidth + edgeClearance + cornerPostWidth / 2),
    (boardLength + edgeClearance + cornerPostWidth / 2, boardWidth + edgeClearance + cornerPostWidth / 2),
]

usbCWidth = 13.0
hdmiWidth = 12.0
usbAWidth = 15.0
rj45Width = 17.0
plugReach = 25.0
frontPlugY0 = -plugReach
frontPlugY1 = 0.0
rightPlugX0 = boardLength
rightPlugX1 = boardLength + plugReach
leftPlugX0 = -plugReach
leftPlugX1 = 0.0
portSill = pcbThickness
usbCPlugZ1 = 8.6
hdmiPlugZ1 = 8.1
usbAPlugZ1 = 18.6
rj45PlugZ1 = 16.6

base = prism_o(floorExterior, baseHeight)
cavity = box_tool(cavityX0, cavityY0, floorInterior, cavityX1, cavityY1, baseRim + cutPast)
base = base.cut(cavity, clean=True)

bosses = cylinder_tools(mounts, standoffDiameter / 2, floorInterior - cutPast, 0.0)
base = base.union(bosses, clean=True)

standoffPilots = cylinder_tools(mounts, pilotDiameter / 2, -pilotDepth, cutPast)
cornerPilots = cylinder_tools(corners, pilotDiameter / 2, baseRim - pilotDepth, baseRim + cutPast)
usbCNotch = box_tool(
    usbCx - usbCWidth / 2,
    frontPlugY0,
    portSill,
    usbCx + usbCWidth / 2,
    frontPlugY1,
    baseRim + cutPast,
)
hdmi0Notch = box_tool(
    hdmi0X - hdmiWidth / 2,
    frontPlugY0,
    portSill,
    hdmi0X + hdmiWidth / 2,
    frontPlugY1,
    baseRim + cutPast,
)
hdmi1Notch = box_tool(
    hdmi1X - hdmiWidth / 2,
    frontPlugY0,
    portSill,
    hdmi1X + hdmiWidth / 2,
    frontPlugY1,
    baseRim + cutPast,
)
usbAUpperNotch = box_tool(
    rightPlugX0,
    usbAUpperY - usbAWidth / 2,
    portSill,
    rightPlugX1,
    usbAUpperY + usbAWidth / 2,
    baseRim + cutPast,
)
usbALowerNotch = box_tool(
    rightPlugX0,
    usbALowerY - usbAWidth / 2,
    portSill,
    rightPlugX1,
    usbALowerY + usbAWidth / 2,
    baseRim + cutPast,
)
rj45Notch = box_tool(
    rightPlugX0,
    rj45Y - rj45Width / 2,
    portSill,
    rightPlugX1,
    rj45Y + rj45Width / 2,
    baseRim + cutPast,
)
sdNotch = box_tool(
    leftPlugX0,
    sdYMin,
    -underBoardDepth,
    leftPlugX1,
    sdYMax,
    baseRim + cutPast,
)
baseCutters = (
    standoffPilots.union(cornerPilots)
    .union(usbCNotch)
    .union(hdmi0Notch)
    .union(hdmi1Notch)
    .union(usbAUpperNotch)
    .union(usbALowerNotch)
    .union(rj45Notch)
    .union(sdNotch)
)
base = base.cut(baseCutters, clean=True)

lid = prism_o(lidUnderside, lidThickness)
lidHoles = cylinder_tools(
    corners,
    lidHoleDiameter / 2,
    lidUnderside - cutPast,
    lidUnderside + lidThickness + cutPast,
)
usbCPlug = box_tool(
    usbCx - usbCWidth / 2,
    frontPlugY0,
    portSill,
    usbCx + usbCWidth / 2,
    frontPlugY1,
    usbCPlugZ1,
)
hdmi0Plug = box_tool(
    hdmi0X - hdmiWidth / 2,
    frontPlugY0,
    portSill,
    hdmi0X + hdmiWidth / 2,
    frontPlugY1,
    hdmiPlugZ1,
)
hdmi1Plug = box_tool(
    hdmi1X - hdmiWidth / 2,
    frontPlugY0,
    portSill,
    hdmi1X + hdmiWidth / 2,
    frontPlugY1,
    hdmiPlugZ1,
)
usbAUpperPlug = box_tool(
    rightPlugX0,
    usbAUpperY - usbAWidth / 2,
    portSill,
    rightPlugX1,
    usbAUpperY + usbAWidth / 2,
    usbAPlugZ1,
)
usbALowerPlug = box_tool(
    rightPlugX0,
    usbALowerY - usbAWidth / 2,
    portSill,
    rightPlugX1,
    usbALowerY + usbAWidth / 2,
    usbAPlugZ1,
)
rj45Plug = box_tool(
    rightPlugX0,
    rj45Y - rj45Width / 2,
    portSill,
    rightPlugX1,
    rj45Y + rj45Width / 2,
    rj45PlugZ1,
)
sdPlug = box_tool(leftPlugX0, sdYMin, -underBoardDepth, leftPlugX1, sdYMax, 0.0)
lidCutters = (
    lidHoles.union(usbCPlug)
    .union(hdmi0Plug)
    .union(hdmi1Plug)
    .union(usbAUpperPlug)
    .union(rj45Plug)
    .union(usbALowerPlug)
    .union(sdPlug)
)
lid = lid.cut(lidCutters, clean=True)

result = [base, lid]

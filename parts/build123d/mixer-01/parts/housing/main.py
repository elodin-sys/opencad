from build123d import Align, Compound, Cylinder, Pos

chamberRadius = 25.0
chamberHeight = 25.0
wallThickness = 3.0
floorThickness = 3.0
lidThickness = 3.0
outerRadius = chamberRadius + wallThickness
inletBoreDiameter = 12.0
inletOuterDiameter = 16.0
inletTopZ = 48.0
outletBoreDiameter = 10.0
outletOuterDiameter = 14.0
outletAxisZ = 12.5
outletEndX = 58.0
pinDiameter = 6.0
pinHeight = 12.0

assert wallThickness > 0, "infeasible: wallThickness must be positive"
assert lidThickness > 0, "infeasible: lidThickness must be positive"
assert floorThickness > 0, "infeasible: floorThickness must be positive"
assert chamberRadius > 0, "infeasible: chamberRadius must be positive"
assert chamberHeight > 0, "infeasible: chamberHeight must be positive"
assert chamberHeight + lidThickness < inletTopZ, "infeasible: lid top must stay below inletTopZ"
assert inletOuterDiameter > inletBoreDiameter, "infeasible: inlet tube wall must be positive"
assert outletOuterDiameter > outletBoreDiameter, "infeasible: outlet tube wall must be positive"
assert pinDiameter > 0, "infeasible: pinDiameter must be positive"
assert pinDiameter < 2 * chamberRadius, "infeasible: pin must fit inside the chamber"
assert pinHeight > 0, "infeasible: pinHeight must be positive"
assert pinHeight < chamberHeight, "infeasible: pin must stay below the lid"
assert outletEndX > outerRadius, "infeasible: outlet end must clear the side wall"

embed = 0.02
lidTop = chamberHeight + lidThickness
shellHeight = floorThickness + lidTop
shell = Pos(0, 0, -floorThickness + shellHeight / 2) * Cylinder(outerRadius, shellHeight)

inletHeight = inletTopZ - (lidTop - embed)
inlet = Pos(0, 0, lidTop - embed + inletHeight / 2) * Cylinder(inletOuterDiameter / 2, inletHeight)

outletStart = chamberRadius - outletOuterDiameter / 2
outlet = Pos(outletStart, 0, outletAxisZ) * Cylinder(
    outletOuterDiameter / 2,
    outletEndX - outletStart,
    rotation=(0, 90, 0),
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)

chamber = Pos(0, 0, chamberHeight / 2) * Cylinder(chamberRadius, chamberHeight)
inletBoreLength = inletTopZ - chamberHeight + 2 * embed
inletBore = Pos(0, 0, chamberHeight - embed + inletBoreLength / 2) * Cylinder(inletBoreDiameter / 2, inletBoreLength)
outletBoreStart = pinDiameter / 2 + outletBoreDiameter / 2 + 1.0
outletBore = Pos(outletBoreStart, 0, outletAxisZ) * Cylinder(
    outletBoreDiameter / 2,
    outletEndX + embed - outletBoreStart,
    rotation=(0, 90, 0),
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)

pin = Pos(0, 0, -embed + (pinHeight + embed) / 2) * Cylinder(pinDiameter / 2, pinHeight + embed)

result = shell + inlet + outlet - Compound(children=[chamber, inletBore, outletBore]) + pin

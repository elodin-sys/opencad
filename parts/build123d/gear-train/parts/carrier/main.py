from build123d import Align, Box, Compound, Cylinder, Pos

plateLength = 110.0
plateWidth = 50.0
plateThickness = 5.0
plateXMin = -25.0
pinionBoreDiameter = 6.0
wheelBoreDiameter = 8.0
centerDistance = 60.0

assert plateLength > 0, "infeasible: plateLength must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert plateWidth > pinionBoreDiameter, "infeasible: plateWidth does not contain the pinion bore"
assert plateWidth > wheelBoreDiameter, "infeasible: plateWidth does not contain the wheel bore"
assert pinionBoreDiameter > 0, "infeasible: pinionBoreDiameter must be positive"
assert wheelBoreDiameter > 0, "infeasible: wheelBoreDiameter must be positive"
assert plateXMin < -pinionBoreDiameter / 2, "infeasible: pinion bore breaks the -x face"
assert pinionBoreDiameter / 2 < plateXMin + plateLength, "infeasible: pinion bore breaks the +x face"
assert plateXMin < centerDistance - wheelBoreDiameter / 2, "infeasible: wheel bore breaks the -x face"
assert centerDistance + wheelBoreDiameter / 2 < plateXMin + plateLength, "infeasible: wheel bore breaks the +x face"
assert pinionBoreDiameter / 2 + wheelBoreDiameter / 2 < centerDistance, "infeasible: bores overlap"

plate = Pos(plateXMin, -plateWidth / 2, -plateThickness) * Box(
    plateLength,
    plateWidth,
    plateThickness,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
# 0.05 mm past each face so the cutter is not coincident with the seat or the underside.
cutter_overrun = 0.05
pinion_hole = Pos(0, 0, -plateThickness / 2) * Cylinder(
    pinionBoreDiameter / 2,
    plateThickness + 2 * cutter_overrun,
)
wheel_hole = Pos(centerDistance, 0, -plateThickness / 2) * Cylinder(
    wheelBoreDiameter / 2,
    plateThickness + 2 * cutter_overrun,
)
result = plate - Compound(children=[pinion_hole, wheel_hole])

from build123d import Align, Box, Cylinder, Pos

plateLength = 200.0
plateWidth = 70.0
plateThickness = 5.0
plateXMin = -40.0
plateYMin = -30.0
pivotHoleDiameter = 6.0

assert plateLength > 0, "infeasible: plateLength must be positive"
assert plateWidth > 0, "infeasible: plateWidth must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert pivotHoleDiameter > 0, "infeasible: pivotHoleDiameter must be positive"

plate = Pos(plateXMin, plateYMin, -plateThickness) * Box(
    plateLength,
    plateWidth,
    plateThickness,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
# 0.02 mm past each face so the cutter is not coincident with the plate
hole = Pos(0, 0, -plateThickness / 2) * Cylinder(
    pivotHoleDiameter / 2,
    plateThickness + 0.04,
)
result = plate - hole

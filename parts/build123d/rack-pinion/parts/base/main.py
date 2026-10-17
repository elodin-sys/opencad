from build123d import Align, Box, Cylinder, Pos

plateLength = 240.0
plateWidth = 80.0
plateThickness = 5.0
plateYMin = -50.0
plateYMax = plateYMin + plateWidth
holeDiameter = 6.0

assert plateLength > holeDiameter, "infeasible: plateLength must exceed holeDiameter"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert plateWidth > 0, "infeasible: plateWidth must be positive"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"

plate = Pos(-plateLength / 2, plateYMin, -plateThickness) * Box(
    plateLength,
    plateYMax - plateYMin,
    plateThickness,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
hole = Pos(0, 0, -plateThickness - 0.05) * Cylinder(
    holeDiameter / 2,
    plateThickness + 0.1,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
result = plate - hole

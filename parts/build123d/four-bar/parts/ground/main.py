from build123d import Align, Box, Compound, Cylinder, Pos

plateLength = 160.0
plateWidth = 60.0
plateThickness = 5.0
plateXMin = -30.0
groundLength = 100.0
holeDiameter = 6.0

assert plateLength > 0, "infeasible: plateLength must be positive"
assert plateWidth > holeDiameter, "infeasible: plateWidth must exceed holeDiameter"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"
assert groundLength > 0, "infeasible: groundLength must be positive"
assert plateXMin + holeDiameter / 2 < 0, "infeasible: O2 bore must lie inside the plate"
assert plateXMin + plateLength > groundLength + holeDiameter / 2, "infeasible: O4 bore must lie inside the plate"

plate = Pos(plateXMin, -plateWidth / 2, -plateThickness) * Box(
    plateLength,
    plateWidth,
    plateThickness,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
cutter_height = plateThickness + 0.1
cutters = Compound(
    children=[
        Pos(0, 0, -plateThickness / 2) * Cylinder(holeDiameter / 2, cutter_height),
        Pos(groundLength, 0, -plateThickness / 2) * Cylinder(holeDiameter / 2, cutter_height),
    ]
)
result = plate - cutters

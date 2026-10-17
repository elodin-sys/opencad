from build123d import Align, Axis, Box, Compound, Cylinder, Location, fillet

plateWidth = 80.0
plateHeight = 50.0
plateThickness = 6.0
holeDiameter = 4.5
holeInset = 10.0
cornerRadius = 5.0
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert holeInset * 2 < plateWidth, "infeasible: holeInset leaves no plate"
assert holeInset * 2 < plateHeight, "infeasible: holeInset leaves no plate"
assert cornerRadius < holeInset, "infeasible: fillet larger than inset"

plate = Box(plateWidth, plateHeight, plateThickness, align=(Align.MIN, Align.MIN, Align.MIN))
plate = fillet(plate.edges().filter_by(Axis.Z), cornerRadius)
tools = []
for x in (holeInset, plateWidth - holeInset):
    for y in (holeInset, plateHeight - holeInset):
        cyl = Cylinder(holeDiameter / 2, plateThickness + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        tools.append(cyl.move(Location((x, y, -0.05))))
result = plate - Compound(tools)

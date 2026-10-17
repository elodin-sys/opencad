import cadquery as cq

plateWidth = 80.0
plateHeight = 50.0
plateThickness = 6.0
holeDiameter = 4.5
holeInset = 10.0
cornerRadius = 5.0

assert min(plateWidth, plateHeight, plateThickness) > 0, "Plate dimensions must be positive"
assert 0 < cornerRadius < min(plateWidth, plateHeight) / 2, "Corner radius must fit the plate"
assert holeDiameter > 0, "Hole diameter must be positive"
assert holeInset > holeDiameter / 2, "Holes must clear the straight plate edges"
assert 2 * holeInset + holeDiameter < min(plateWidth, plateHeight), "Holes must not overlap"
assert holeInset >= cornerRadius, "Hole centres must lie beyond the corner tangent lines"

plate = cq.Workplane("XY").box(plateWidth, plateHeight, plateThickness, centered=(False, False, False))
rounded_plate = plate.edges("|Z").fillet(cornerRadius)
hole_centres = [
    (holeInset, holeInset),
    (plateWidth - holeInset, holeInset),
    (plateWidth - holeInset, plateHeight - holeInset),
    (holeInset, plateHeight - holeInset),
]
cut_overrun = 0.02
hole_tools = (
    cq.Workplane("XY", origin=(0, 0, -cut_overrun))
    .pushPoints(hole_centres)
    .circle(holeDiameter / 2)
    .extrude(plateThickness + 2 * cut_overrun, combine=False)
)
result = rounded_plate.cut(hole_tools, clean=True)

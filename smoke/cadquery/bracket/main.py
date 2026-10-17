import cadquery as cq

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

result = (
    cq.Workplane("XY")
    .box(plateWidth, plateHeight, plateThickness, centered=(False, False, False))
    .edges("|Z")
    .fillet(cornerRadius)
    .faces(">Z")
    .workplane()
    .rect(plateWidth - 2 * holeInset, plateHeight - 2 * holeInset, forConstruction=True)
    .vertices()
    .hole(holeDiameter)
)

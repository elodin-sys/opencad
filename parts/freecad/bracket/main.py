"""Parametric mounting plate, millimetres; datum origin at the blank minimum."""

import FreeCAD
import Part
import Sketcher

plateWidth = 80.0
plateHeight = 50.0
plateThickness = 6.0
holeDiameter = 4.5
holeInset = 10.0
cornerRadius = 5.0

assert min(plateWidth, plateHeight, plateThickness) > 0, "Plate dimensions must be positive"
assert 0 < cornerRadius < min(plateWidth, plateHeight) / 2, "Corner radius must fit"
assert holeDiameter > 0, "Hole diameter must be positive"
assert holeInset > cornerRadius + holeDiameter / 2, "Holes must clear the corner blends"
assert 2 * holeInset + holeDiameter < min(plateWidth, plateHeight), "Holes must be separate"

doc = FreeCAD.newDocument("Bracket")
body = doc.addObject("PartDesign::Body", "BracketBody")
xy_plane = next(item for item in body.Origin.OriginFeatures if item.Name.startswith("XY_Plane"))
outline = body.newObject("Sketcher::SketchObject", "PlateOutline")
outline.AttachmentSupport = [(xy_plane, "")]
outline.MapMode = "FlatFace"
corners = [(0, 0), (plateWidth, 0), (plateWidth, plateHeight), (0, plateHeight)]
for i, (x, y) in enumerate(corners):
    x_next, y_next = corners[(i + 1) % 4]
    outline.addGeometry(Part.LineSegment(FreeCAD.Vector(x, y, 0), FreeCAD.Vector(x_next, y_next, 0)), False)
    outline.addConstraint(Sketcher.Constraint("Horizontal" if i % 2 == 0 else "Vertical", i))
for i in range(4):
    outline.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
outline.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1))
outline.addConstraint(Sketcher.Constraint("Distance", 0, plateWidth))
outline.addConstraint(Sketcher.Constraint("Distance", 1, plateHeight))
doc.recompute()
assert outline.FullyConstrained, "Plate outline must be fully constrained"
plate = body.newObject("PartDesign::Pad", "Plate")
plate.Profile = outline
plate.Length = plateThickness
plate.Refine = True
outline.Visibility = False
doc.recompute()
assert plate.Shape.isValid(), "Plate pad must be valid"
assert len(plate.Shape.Solids) == 1, "Plate must be a single solid"

# Select edges by geometry so parameter edits do not depend on edge numbering.
vertical_edges = []
for index, edge in enumerate(plate.Shape.Edges, start=1):
    bounds = edge.BoundBox
    if bounds.XLength < 1e-7 and bounds.YLength < 1e-7 and abs(bounds.ZLength - plateThickness) < 1e-7:
        vertical_edges.append(f"Edge{index}")
assert len(vertical_edges) == 4, "The blank must have four vertical corner edges"
corner_fillets = body.newObject("PartDesign::Fillet", "CornerFillets")
corner_fillets.Base = (plate, vertical_edges)
corner_fillets.Radius = cornerRadius
corner_fillets.Refine = True
plate.Visibility = False
doc.recompute()
assert corner_fillets.Shape.isValid(), "Corner fillets must be valid"
assert len(corner_fillets.Shape.Solids) == 1, "Fillets must preserve one solid"

# A datum-based top sketch avoids fragile face attachments and follows thickness edits.
hole_sketch = body.newObject("Sketcher::SketchObject", "MountingHoleSketch")
hole_sketch.AttachmentSupport = [(xy_plane, "")]
hole_sketch.MapMode = "FlatFace"
hole_sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, plateThickness), FreeCAD.Rotation())
hole_centres = [
    (holeInset, holeInset),
    (plateWidth - holeInset, holeInset),
    (plateWidth - holeInset, plateHeight - holeInset),
    (holeInset, plateHeight - holeInset),
]
for x, y in hole_centres:
    circle = hole_sketch.addGeometry(
        Part.Circle(FreeCAD.Vector(x, y, 0), FreeCAD.Vector(0, 0, 1), holeDiameter / 2), False
    )
    hole_sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, circle, 3, x))
    hole_sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, circle, 3, y))
    hole_sketch.addConstraint(Sketcher.Constraint("Diameter", circle, holeDiameter))
doc.recompute()
assert hole_sketch.FullyConstrained, "Mounting-hole sketch must be fully constrained"
mounting_holes = body.newObject("PartDesign::Pocket", "MountingHoles")
mounting_holes.Profile = hole_sketch
mounting_holes.Type = "ThroughAll"
mounting_holes.Refine = True
corner_fillets.Visibility = False
hole_sketch.Visibility = False
doc.recompute()
for feature in (outline, plate, corner_fillets, hole_sketch, mounting_holes, body):
    assert feature.isValid(), f"Feature {feature.Name} must be valid"
    assert feature.Shape.isValid(), f"Shape of {feature.Name} must be valid"
assert len(body.Shape.Solids) == 1, "Finished bracket must contain exactly one solid"
result = body

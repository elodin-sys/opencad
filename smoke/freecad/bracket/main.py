import FreeCAD
import Part
import Sketcher

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


doc = FreeCAD.newDocument("bracket")
body = doc.addObject("PartDesign::Body", "Body")
sketch = body.newObject("Sketcher::SketchObject", "Sketch")
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(plateWidth, 0, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(plateWidth, 0, 0), FreeCAD.Vector(plateWidth, plateHeight, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(plateWidth, plateHeight, 0), FreeCAD.Vector(0, plateHeight, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(0, plateHeight, 0), FreeCAD.Vector(0, 0, 0)), False)
sketch.addConstraint(Sketcher.Constraint("Coincident", 0, 2, 1, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 1, 2, 2, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 2, 2, 3, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 3, 2, 0, 1))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 2))
sketch.addConstraint(Sketcher.Constraint("Vertical", 1))
sketch.addConstraint(Sketcher.Constraint("Vertical", 3))
sketch.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, plateWidth))
sketch.addConstraint(Sketcher.Constraint("DistanceY", 3, 1, 3, 2, plateHeight))
sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 1, 0.0))
sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 0, 1, 0.0))
pad = body.newObject("PartDesign::Pad", "Pad")
pad.Profile = sketch
pad.Length = plateThickness
holes = body.newObject("Sketcher::SketchObject", "Holes")
r = holeDiameter / 2
for x, y in (
    (holeInset, holeInset),
    (plateWidth - holeInset, holeInset),
    (holeInset, plateHeight - holeInset),
    (plateWidth - holeInset, plateHeight - holeInset),
):
    holes.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0), FreeCAD.Vector(0, 0, 1), r), False)
pocket = body.newObject("PartDesign::Pocket", "Pocket")
pocket.Profile = holes
pocket.Length = plateThickness + 0.05
if hasattr(pocket, "Type"):
    try:
        pocket.Type = "ThroughAll"
    except Exception:
        pocket.Type = 1
doc.recompute()
doc.recompute()
result = body

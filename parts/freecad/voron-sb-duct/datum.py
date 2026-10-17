import FreeCAD
import Part
import PartDesign  # noqa: F401
import Sketcher
from params import backY, frontY, halfWidth, nozzleEndZ, overallDepth, overallHeight, overallWidth, topZ

assert overallWidth > 0, "infeasible: overallWidth must be positive"
assert overallDepth > 0, "infeasible: overallDepth must be positive"
assert overallHeight > 0, "infeasible: overallHeight must be positive"
assert halfWidth > 0, "infeasible: halfWidth must be positive"
assert topZ > nozzleEndZ, "infeasible: topZ must be above nozzleEndZ"
assert frontY < backY, "infeasible: frontY must sit forward of backY"

doc = FreeCAD.newDocument("voron_sb_duct")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xy = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)

sketch = body.newObject("Sketcher::SketchObject", "EnvelopeSketch")
sketch.AttachmentSupport = [(xy, "")]
sketch.MapMode = "FlatFace"
sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, nozzleEndZ), FreeCAD.Rotation())
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(-halfWidth, frontY, 0), FreeCAD.Vector(halfWidth, frontY, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(halfWidth, frontY, 0), FreeCAD.Vector(halfWidth, backY, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(halfWidth, backY, 0), FreeCAD.Vector(-halfWidth, backY, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(-halfWidth, backY, 0), FreeCAD.Vector(-halfWidth, frontY, 0)), False)
sketch.addConstraint(Sketcher.Constraint("Coincident", 0, 2, 1, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 1, 2, 2, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 2, 2, 3, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 3, 2, 0, 1))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 2))
sketch.addConstraint(Sketcher.Constraint("Vertical", 1))
sketch.addConstraint(Sketcher.Constraint("Vertical", 3))
sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 1, -halfWidth))
sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 2, halfWidth))
sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 0, 1, frontY))
sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 2, 1, backY))

pad = body.newObject("PartDesign::Pad", "Envelope")
pad.Profile = sketch
pad.Length = overallHeight
pad.Refine = True
doc.recompute()

assert pad.isValid(), "kernel: envelope pad is invalid after recompute"
assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
datum = body

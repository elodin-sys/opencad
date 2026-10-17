import FreeCAD
import Part
import Sketcher

width = 60.0
height = 40.0
thickness = 4.0
assert width > 0, "infeasible: width must be positive"
assert height > 0, "infeasible: height must be positive"
assert thickness > 0, "infeasible: thickness must be positive"

doc = FreeCAD.newDocument("coupon")
body = doc.addObject("PartDesign::Body", "Body")
# Single-solid rule: with the 1.1 default (True) every feature after the Pad returns a Compound wrapper.
body.AllowCompound = False
doc.recompute()
xy = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)

sketch = body.newObject("Sketcher::SketchObject", "BlankSketch")
sketch.AttachmentSupport = [(xy, "")]
sketch.MapMode = "FlatFace"
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(width, 0, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(width, 0, 0), FreeCAD.Vector(width, height, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(width, height, 0), FreeCAD.Vector(0, height, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(0, height, 0), FreeCAD.Vector(0, 0, 0)), False)
sketch.addConstraint(Sketcher.Constraint("Coincident", 0, 2, 1, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 1, 2, 2, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 2, 2, 3, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 3, 2, 0, 1))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 2))
sketch.addConstraint(Sketcher.Constraint("Vertical", 1))
sketch.addConstraint(Sketcher.Constraint("Vertical", 3))
sketch.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, width))
sketch.addConstraint(Sketcher.Constraint("DistanceY", 0, 1, 3, 1, height))
sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 1, 0.0))
sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 0, 1, 0.0))

pad = body.newObject("PartDesign::Pad", "Blank")
pad.Profile = sketch
pad.Length = thickness
pad.Refine = True
doc.recompute()

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
result = body

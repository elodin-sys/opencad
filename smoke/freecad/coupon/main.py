import FreeCAD
import Part
import Sketcher

width = 60.0
height = 40.0
thickness = 4.0
assert thickness > 0, "infeasible: thickness must be positive"
assert width > 0, "infeasible: width must be positive"
assert height > 0, "infeasible: height must be positive"

doc = FreeCAD.newDocument("coupon")
body = doc.addObject("PartDesign::Body", "Body")
sketch = body.newObject("Sketcher::SketchObject", "Sketch")
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
sketch.addConstraint(Sketcher.Constraint("DistanceY", 3, 1, 3, 2, height))
sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 1, 0.0))
sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 0, 1, 0.0))
pad = body.newObject("PartDesign::Pad", "Pad")
pad.Profile = sketch
pad.Length = thickness
pad.Refine = True
doc.recompute()
result = body

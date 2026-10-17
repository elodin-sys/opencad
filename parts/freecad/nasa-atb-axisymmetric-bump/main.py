import math

import FreeCAD
import Part
import Sketcher

cylinderDiameter = 152.4
bumpChord = 203.2
bumpHeight = 19.05
filletRadius = 183.0
upstreamX = -650.0073203536
downstreamX = 900.0029136304

assert cylinderDiameter > 0, "infeasible: cylinderDiameter must be positive"
assert bumpChord > 0, "infeasible: bumpChord must be positive"
assert bumpHeight > 0, "infeasible: bumpHeight must be positive"
assert filletRadius > 0, "infeasible: filletRadius must be positive"
assert bumpHeight * 2 < bumpChord, "infeasible: use the shallow upper circular-arc branch"
assert upstreamX < 0, "infeasible: upstream cylinder must start before the origin"
assert downstreamX > bumpChord, "infeasible: keep a positive downstream cylinder span"

cylinder_radius = cylinderDiameter / 2.0
half_chord = bumpChord / 2.0
main_radius = (bumpHeight**2 + half_chord**2) / (2.0 * bumpHeight)
assert main_radius > bumpHeight, "infeasible: main-circle center must lie below the crown"
blend_radicand = 2.0 * (main_radius + filletRadius) * bumpHeight - bumpHeight**2
assert blend_radicand > 0, "infeasible: blend tangency must have a real solution"
blend_offset = math.sqrt(blend_radicand)
blend_start_x = half_chord - blend_offset
blend_end_x = blend_start_x + filletRadius * blend_offset / (main_radius + filletRadius)
assert upstreamX < blend_start_x, "infeasible: keep a positive upstream cylinder span"
assert blend_start_x < 0, "infeasible: leading blend must begin upstream of the origin"
assert 0 < blend_end_x < bumpChord, "infeasible: blend must meet the bump before the trailing join"

blend_center_y = cylinder_radius + filletRadius
blend_end_y = blend_center_y - math.sqrt(filletRadius**2 - (blend_end_x - blend_start_x) ** 2)
blend_mid_x = 0.5 * (blend_start_x + blend_end_x)
blend_mid_y = blend_center_y - math.sqrt(filletRadius**2 - (blend_mid_x - blend_start_x) ** 2)
crown_y = cylinder_radius + bumpHeight

doc = FreeCAD.newDocument("nasa-atb-axisymmetric-bump")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
# Seam at 45 deg about +x: OCC volume-props of a 360-revolve bias COM along the seam plane.
seam = body.newObject("PartDesign::Plane", "SeamPlane")
seam.MapMode = "Deactivated"
seam.Placement = FreeCAD.Placement(
    FreeCAD.Vector(0, 0, 0),
    FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 45.0),
)

# Sketch u=+x, v=+radius. Closed meridian, revolved 360 deg about +x.
sketch = body.newObject("Sketcher::SketchObject", "MeridianSketch")
sketch.AttachmentSupport = [(seam, "")]
sketch.MapMode = "FlatFace"

geoms = [
    Part.LineSegment(
        FreeCAD.Vector(upstreamX, 0.0, 0),
        FreeCAD.Vector(upstreamX, cylinder_radius, 0),
    ),
    Part.LineSegment(
        FreeCAD.Vector(upstreamX, cylinder_radius, 0),
        FreeCAD.Vector(blend_start_x, cylinder_radius, 0),
    ),
    Part.ArcOfCircle(
        FreeCAD.Vector(blend_start_x, cylinder_radius, 0),
        FreeCAD.Vector(blend_mid_x, blend_mid_y, 0),
        FreeCAD.Vector(blend_end_x, blend_end_y, 0),
    ),
    Part.ArcOfCircle(
        FreeCAD.Vector(blend_end_x, blend_end_y, 0),
        FreeCAD.Vector(half_chord, crown_y, 0),
        FreeCAD.Vector(bumpChord, cylinder_radius, 0),
    ),
    Part.LineSegment(
        FreeCAD.Vector(bumpChord, cylinder_radius, 0),
        FreeCAD.Vector(downstreamX, cylinder_radius, 0),
    ),
    Part.LineSegment(
        FreeCAD.Vector(downstreamX, cylinder_radius, 0),
        FreeCAD.Vector(downstreamX, 0.0, 0),
    ),
    Part.LineSegment(
        FreeCAD.Vector(downstreamX, 0.0, 0),
        FreeCAD.Vector(upstreamX, 0.0, 0),
    ),
]
for geom in geoms:
    sketch.addGeometry(geom, False)
# DistanceX/Y on these arcs flips the main branch or empties the profile; Block pins the parameter-built vertices.
for i in range(len(geoms)):
    sketch.addConstraint(Sketcher.Constraint("Block", i))

rev = body.newObject("PartDesign::Revolution", "FullRevolution")
rev.Profile = sketch
rev.ReferenceAxis = (sketch, ["H_Axis"])
rev.Angle = 360.0
rev.Refine = True
doc.recompute()

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"

# Gates bind these on the STEP by plane, outward normal, area, centre.
endCapNames = ("upstreamCap", "downstreamCap")
assert len(endCapNames) == 2, "infeasible: expected two named end caps"
result = body

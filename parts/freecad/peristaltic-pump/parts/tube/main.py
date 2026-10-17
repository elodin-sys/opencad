"""Uncompressed silicone U-tube in the pump's own millimetre frame."""

import math

import FreeCAD
import Part
import Sketcher

tubeOuterDiameter = 3.0
tubeInnerDiameter = 1.0
trackRadius = 12.17
centrelineRadius = trackRadius - tubeOuterDiameter / 2.0
bendAngle = 180.0
legLength = 30.0

assert tubeOuterDiameter > 0.0, "infeasible: tubeOuterDiameter must be positive"
assert 0.0 < tubeInnerDiameter < tubeOuterDiameter, "infeasible: require 0 < ID < OD"
assert legLength > 0.0, "infeasible: legLength must be positive"
assert centrelineRadius > tubeOuterDiameter / 2.0, "infeasible: bend self-intersects"
assert math.isclose(bendAngle, 180.0, abs_tol=1e-9), "infeasible: the parallel -x legs require a 180-degree bend"

doc = FreeCAD.newDocument("PeristalticPumpTube")
body = doc.addObject("PartDesign::Body", "Tube")
body.Label = "Uncompressed silicone tube, 50 A"
doc.recompute()


def profile(name):
    """Upper semi-annulus at y=-R; its inner arc produces the continuous bore."""
    sketch = body.newObject("Sketcher::SketchObject", name)
    sketch.AttachmentSupport = (doc.getObject("YZ_Plane"), [""])
    sketch.MapMode = "FlatFace"
    # YZ's local u=y, v=z becomes u=-y, v=z and the normal becomes -x.
    sketch.AttachmentOffset = FreeCAD.Placement(
        FreeCAD.Vector(0.0, 0.0, 0.0),
        FreeCAD.Rotation(FreeCAD.Vector(0.0, 1.0, 0.0), 180.0),
    )
    arcs = []
    for diameter in (tubeOuterDiameter, tubeInnerDiameter):
        radius = diameter / 2.0
        arc = sketch.addGeometry(
            Part.ArcOfCircle(
                Part.Circle(
                    FreeCAD.Vector(centrelineRadius, 0.0, 0.0),
                    FreeCAD.Vector(0.0, 0.0, 1.0),
                    radius,
                ),
                0.0,
                math.pi,
            ),
            False,
        )
        sketch.addConstraint(Sketcher.Constraint("Radius", arc, radius))
        sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, arc, 3, centrelineRadius))
        for point in (1, 2, 3):
            sketch.addConstraint(Sketcher.Constraint("PointOnObject", arc, point, -1))
        arcs.append(arc)
    for endpoint, sign in ((1, 1.0), (2, -1.0)):
        bridge = sketch.addGeometry(
            Part.LineSegment(
                FreeCAD.Vector(centrelineRadius + sign * tubeOuterDiameter / 2.0, 0.0, 0.0),
                FreeCAD.Vector(centrelineRadius + sign * tubeInnerDiameter / 2.0, 0.0, 0.0),
            ),
            False,
        )
        sketch.addConstraint(Sketcher.Constraint("Coincident", bridge, 1, arcs[0], endpoint))
        sketch.addConstraint(Sketcher.Constraint("Coincident", bridge, 2, arcs[1], endpoint))
    doc.recompute()
    assert sketch.FullyConstrained, f"infeasible: {name} is underconstrained"
    assert sketch.isValid(), f"infeasible: {name} is invalid"
    centre = sketch.Placement.multVec(FreeCAD.Vector(centrelineRadius, 0.0, 0.0))
    assert (centre - FreeCAD.Vector(0.0, -centrelineRadius, 0.0)).Length < 1e-7, "infeasible: profile datum frame moved"
    return sketch


bend_profile = profile("BendProfile")
bend = body.newObject("PartDesign::Revolution", "Bend")
bend.Label = "bend: lower-y quarter, upper-z section"
bend.Profile = bend_profile
bend.ReferenceAxis = (bend_profile, ["V_Axis"])
bend.Angle = bendAngle / 2.0
bend.Refine = True
doc.recompute()

leg_profile = profile("LegProfile")
outlet_leg = body.newObject("PartDesign::Pad", "OutletLeg")
outlet_leg.Label = "outletLeg: upper-z section along -x"
outlet_leg.Profile = leg_profile
outlet_leg.Length = legLength
outlet_leg.Refine = True
doc.recompute()

symmetry = body.newObject("PartDesign::MultiTransform", "TubeSymmetry")
symmetry.Label = "tubeSeat: datum C and datum A mirrors"
symmetry.Originals = [bend, outlet_leg]

mirror_y = doc.addObject("PartDesign::Mirrored", "InletLegAndBend")
mirror_y.Label = "inletLeg and bend: mirror across datum C, y=0"
mirror_y.MirrorPlane = (doc.getObject("XZ_Plane"), [""])
mirror_y.Refine = True
body.addObject(mirror_y)

mirror_z = doc.addObject("PartDesign::Mirrored", "MirrorMidPlane")
mirror_z.Label = "Complete section: mirror across datum A, z=0"
mirror_z.MirrorPlane = (doc.getObject("XY_Plane"), [""])
mirror_z.Refine = True
body.addObject(mirror_z)
symmetry.Transformations = [mirror_y, mirror_z]
symmetry.Refine = True
body.Tip = symmetry
doc.recompute()

for feature in body.Group:
    assert feature.isValid(), f"infeasible: invalid feature {feature.Name}"
assert body.Shape.isValid(), "infeasible: tube shape is invalid"
assert len(body.Shape.Solids) == 1, "infeasible: tube must be one connected solid"

# Cache triangulation for FreeCAD's fast bounding box; the analytic B-rep stays
# unchanged and is independently checked after STEP export by the local critic.
body.Shape.tessellate(0.005)
doc.recompute()
result = body

import math

import FreeCAD
import Part
import Sketcher

overallHeight = 26.0
flangeThickness = 11.0
bossDiameter = 57.0
flangeLength = 98.5
holeSpacing = 76.5
lobeDiameter = flangeLength - holeSpacing
draftAngle = 4.0
edgeRadius = 1.0
counterboreDiameter = 47.0
counterboreDepth = 14.0
boreDiameter = 14.0
mountingHoleDiameter = 10.0

assert overallHeight > flangeThickness, "infeasible: overallHeight must exceed flange thickness"
assert counterboreDepth > 0.0, "infeasible: counterboreDepth must be positive"
assert counterboreDepth < overallHeight, "infeasible: counterbore deeper than the housing"
assert boreDiameter > 0.0, "infeasible: boreDiameter must be positive"
assert boreDiameter < counterboreDiameter, "infeasible: bore must be smaller than the counterbore"
assert mountingHoleDiameter > 0.0, "infeasible: mounting hole diameter must be positive"
assert mountingHoleDiameter < lobeDiameter, "infeasible: mounting hole larger than the lobe"
assert edgeRadius > 0.0, "infeasible: edgeRadius must be positive"
assert draftAngle > 0.0, "infeasible: draftAngle must be positive"
assert flangeThickness > edgeRadius, "infeasible: flange thinner than the edge round"
assert holeSpacing > bossDiameter, "infeasible: mounting holes fall inside the boss"

_TAN = math.tan(math.radians(draftAngle))
_GAMMA = math.acos((bossDiameter - lobeDiameter) / holeSpacing)
assert lobeDiameter / 2.0 > flangeThickness * _TAN, "infeasible: draft consumes the lobe"
assert bossDiameter / 2.0 > overallHeight * _TAN, "infeasible: draft consumes the boss"


def _point(cx, cy, radius, angle, z):
    return FreeCAD.Vector(cx + radius * math.cos(angle), cy + radius * math.sin(angle), z)


def _hull_wire(z, shrink):
    boss_r = bossDiameter / 2.0 - shrink
    lobe_r = lobeDiameter / 2.0 - shrink
    half = holeSpacing / 2.0
    gamma = _GAMMA

    def arc(cx, cy, radius, a0, a1):
        circle = Part.Circle(FreeCAD.Vector(cx, cy, z), FreeCAD.Vector(0, 0, 1), radius)
        return Part.ArcOfCircle(circle, a0, a1).toShape()

    edges = [
        arc(0.0, 0.0, boss_r, gamma, math.pi - gamma),
        Part.makeLine(_point(0.0, 0.0, boss_r, math.pi - gamma, z), _point(-half, 0.0, lobe_r, math.pi - gamma, z)),
        arc(-half, 0.0, lobe_r, math.pi - gamma, math.pi + gamma),
        Part.makeLine(_point(-half, 0.0, lobe_r, math.pi + gamma, z), _point(0.0, 0.0, boss_r, math.pi + gamma, z)),
        arc(0.0, 0.0, boss_r, math.pi + gamma, 2.0 * math.pi - gamma),
        Part.makeLine(_point(0.0, 0.0, boss_r, -gamma, z), _point(half, 0.0, lobe_r, -gamma, z)),
        arc(half, 0.0, lobe_r, -gamma, gamma),
        Part.makeLine(_point(half, 0.0, lobe_r, gamma, z), _point(0.0, 0.0, boss_r, gamma, z)),
    ]
    return Part.Wire(edges)


def _circle_wire(z, radius):
    circle = Part.Circle(FreeCAD.Vector(0.0, 0.0, z), FreeCAD.Vector(0.0, 0.0, 1), radius)
    return Part.Wire(circle.toShape())


def _cast_solid():
    shrink_flange = flangeThickness * _TAN
    shrink_top = overallHeight * _TAN
    flange = Part.makeLoft(
        [_hull_wire(0.0, 0.0), _hull_wire(flangeThickness, shrink_flange)],
        True,
        True,
    )
    boss = Part.makeLoft(
        [
            _circle_wire(flangeThickness, bossDiameter / 2.0 - shrink_flange),
            _circle_wire(overallHeight, bossDiameter / 2.0 - shrink_top),
        ],
        True,
        True,
    )
    fused = flange.fuse(boss)
    horizontal = [edge for edge in fused.Edges if edge.BoundBox.ZLength < 1e-4 and edge.Length > 1e-6]
    rounded = fused.makeFillet(edgeRadius, horizontal)
    assert len(rounded.Solids) == 1 and rounded.isValid(), "infeasible: drafted housing did not fillet"
    return rounded


def _origin_plane(body, name):
    for feature in body.Origin.OriginFeatures:
        if feature.Name == name:
            return feature
    raise RuntimeError(f"missing origin plane {name}")


def _circle_sketch(body, name, support, z_offset, circles):
    sketch = body.newObject("Sketcher::SketchObject", name)
    sketch.AttachmentSupport = [(support, "")]
    sketch.MapMode = "FlatFace"
    if z_offset:
        sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, z_offset), FreeCAD.Rotation())
    for cx, cy, radius in circles:
        geo = sketch.addGeometry(Part.Circle(FreeCAD.Vector(cx, cy, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), radius), False)
        sketch.addConstraint(Sketcher.Constraint("Radius", geo, radius))
        if cx == 0.0 and cy == 0.0:
            sketch.addConstraint(Sketcher.Constraint("Coincident", geo, 3, -1, 1))
        else:
            sketch.addConstraint(Sketcher.Constraint("DistanceX", geo, 3, cx))
            sketch.addConstraint(Sketcher.Constraint("DistanceY", geo, 3, cy))
    return sketch


doc = FreeCAD.newDocument("bearing_housing")
stock = doc.addObject("Part::Feature", "CastStock")
stock.Shape = _cast_solid()
body = doc.addObject("PartDesign::Body", "Housing")
body.BaseFeature = stock
xy = _origin_plane(body, "XY_Plane")

counterbore = _circle_sketch(
    body,
    "CounterboreSketch",
    xy,
    overallHeight,
    [(0.0, 0.0, counterboreDiameter / 2.0)],
)
counterbore_cut = body.newObject("PartDesign::Pocket", "Counterbore")
counterbore_cut.Profile = counterbore
counterbore_cut.Type = "Length"
counterbore_cut.Length = counterboreDepth
counterbore_cut.Reversed = False

bore = _circle_sketch(body, "BoreSketch", xy, 0.0, [(0.0, 0.0, boreDiameter / 2.0)])
bore_cut = body.newObject("PartDesign::Pocket", "ThroughBore")
bore_cut.Profile = bore
bore_cut.Type = "ThroughAll"
bore_cut.Reversed = True

half = holeSpacing / 2.0
mounts = _circle_sketch(
    body,
    "MountingSketch",
    xy,
    0.0,
    [(-half, 0.0, mountingHoleDiameter / 2.0), (half, 0.0, mountingHoleDiameter / 2.0)],
)
mount_cut = body.newObject("PartDesign::Pocket", "MountingHoles")
mount_cut.Profile = mounts
mount_cut.Type = "ThroughAll"
mount_cut.Reversed = True
mount_cut.Refine = True

doc.recompute()
for feature in (counterbore, bore, mounts, counterbore_cut, bore_cut, mount_cut):
    assert feature.isValid(), f"infeasible: {feature.Name} failed"
for sketch in (counterbore, bore, mounts):
    assert sketch.FullyConstrained, f"infeasible: {sketch.Name} is not fully constrained"
assert len(body.Shape.Solids) == 1, "infeasible: housing must be one solid"
result = body

import math

import FreeCAD
import Part
import PartDesign
import Sketcher

flangeDia = 88.9
hubDia = 50.8
hubYMin = 92.804
flangeYMin = 106.298
flangeYMax = 125.348
slotY = 112.648
slotHalf = 19.844
grooveY = 103.917
grooveFaceArea = 414.95
holeMajorDia = 11.113
holeMinorDia = 7.938
holeY = 118.204
holeZ = 19.05
holeMajorPosY = 118.139
holeMajorPosZ = 18.923
rimHoleDia = 2.261
rimHoleY = 109.594
rimHoleX = -5.077
rimHoleZ = 39.746
rimHoleLen = 8.763
xFace = 36.512
hubNeckRadius = 21.1
hubNeckY = 102.2
hubWaistY = 94.5
flangeRadius = 44.45
hubRadius = 25.4
flangeThick = 19.05
hubLen = 13.494
slotDepth = 12.7
slotWidth = 39.688
overallY = 32.544
grooveInnerRadius = 22.651

assert flangeDia > 0, "infeasible: flangeDia must be positive"
assert hubDia > 0, "infeasible: hubDia must be positive"
assert hubYMin < flangeYMin, "infeasible: hubYMin must sit below flangeYMin"
assert flangeYMin < flangeYMax, "infeasible: flangeYMin must sit below flangeYMax"
assert slotY > flangeYMin, "infeasible: slotY must sit above flangeYMin"
assert slotY < flangeYMax, "infeasible: slotY must sit below flangeYMax"
assert slotHalf > 0, "infeasible: slotHalf must be positive"
assert grooveY > hubYMin, "infeasible: grooveY must sit above hubYMin"
assert grooveY < flangeYMin, "infeasible: grooveY must sit below flangeYMin"
assert grooveFaceArea > 0, "infeasible: grooveFaceArea must be positive"
assert holeMajorDia > holeMinorDia, "infeasible: holeMajorDia must exceed holeMinorDia"
assert holeMinorDia > 0, "infeasible: holeMinorDia must be positive"
assert holeY > flangeYMin, "infeasible: holeY must sit above flangeYMin"
assert holeY < flangeYMax, "infeasible: holeY must sit below flangeYMax"
assert holeZ > 0, "infeasible: holeZ must be positive"
assert holeMajorPosY > flangeYMin, "infeasible: holeMajorPosY must sit above flangeYMin"
assert holeMajorPosZ > 0, "infeasible: holeMajorPosZ must be positive"
assert rimHoleDia > 0, "infeasible: rimHoleDia must be positive"
assert rimHoleY > flangeYMin, "infeasible: rimHoleY must sit above flangeYMin"
assert rimHoleY < flangeYMax, "infeasible: rimHoleY must sit below flangeYMax"
assert rimHoleX < 0, "infeasible: rimHoleX must sit toward -X"
assert rimHoleZ > 0, "infeasible: rimHoleZ must be positive"
assert rimHoleLen > 0, "infeasible: rimHoleLen must be positive"
assert xFace > 0, "infeasible: xFace must be positive"
assert hubNeckRadius > 0, "infeasible: hubNeckRadius must be positive"
assert hubNeckRadius < hubRadius, "infeasible: hubNeckRadius must sit inside the hub OD"
assert hubWaistY > hubYMin, "infeasible: hubWaistY must sit above hubYMin"
assert hubNeckY > hubWaistY, "infeasible: hubNeckY must sit above hubWaistY"
assert hubNeckY < flangeYMin, "infeasible: hubNeckY must sit below flangeYMin"
assert flangeRadius > hubRadius, "infeasible: flangeRadius must exceed hubRadius"
assert flangeThick > 0, "infeasible: flangeThick must be positive"
assert hubLen > 0, "infeasible: hubLen must be positive"
assert slotDepth > 0, "infeasible: slotDepth must be positive"
assert slotWidth > 0, "infeasible: slotWidth must be positive"
assert overallY > 0, "infeasible: overallY must be positive"
assert grooveInnerRadius > hubNeckRadius, "infeasible: grooveInnerRadius must exceed hubNeckRadius"
assert grooveInnerRadius < hubRadius, "infeasible: grooveInnerRadius must sit inside the hub OD"

_ = PartDesign
z_axis = FreeCAD.Vector(0, 0, 1)

doc = FreeCAD.newDocument("fusion_15317_recon")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xz = next(f for f in body.Origin.OriginFeatures if "XZ" in f.Name and "Plane" in f.Name)
xy = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)


def attach_xz(sketch, y):
    if hasattr(sketch, "AttachmentSupport"):
        sketch.AttachmentSupport = [(xz, "")]
    else:
        sketch.Support = [(xz, "")]
    sketch.MapMode = "FlatFace"
    # XZ local +z is −Y; negative offset places the sketch at world y.
    sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, -y), FreeCAD.Rotation())


def attach(sketch, plane):
    if hasattr(sketch, "AttachmentSupport"):
        sketch.AttachmentSupport = [(plane, "")]
    else:
        sketch.Support = [(plane, "")]
    sketch.MapMode = "FlatFace"


def add_circle(sketch, diameter, cx=0.0, cy=0.0):
    gid = sketch.addGeometry(
        Part.Circle(FreeCAD.Vector(cx, cy, 0), z_axis, diameter / 2.0),
        False,
    )
    sketch.addConstraint(Sketcher.Constraint("Diameter", gid, diameter))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gid, 3, cx))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gid, 3, cy))
    return gid


def add_blocked(sketch, geoms):
    for geom in geoms:
        gid = sketch.addGeometry(geom, False)
        sketch.addConstraint(Sketcher.Constraint("Block", gid))


def make_yz_plane(name, x):
    plane = body.newObject("PartDesign::Plane", name)
    plane.MapMode = "Deactivated"
    plane.Placement = FreeCAD.Placement(
        FreeCAD.Vector(x, 0.0, 0.0),
        FreeCAD.Rotation(
            FreeCAD.Vector(0, 1, 0),
            FreeCAD.Vector(0, 0, 1),
            FreeCAD.Vector(1, 0, 0),
            "ZXY",
        ),
    )
    return plane


def make_xy_plane(name, origin):
    plane = body.newObject("PartDesign::Plane", name)
    plane.MapMode = "Deactivated"
    plane.Placement = FreeCAD.Placement(FreeCAD.Vector(*origin), FreeCAD.Rotation())
    return plane


hub_sketch = body.newObject("Sketcher::SketchObject", "HubSketch")
attach_xz(hub_sketch, hubYMin)
add_circle(hub_sketch, hubDia)

hub = body.newObject("PartDesign::Pad", "Hub")
hub.Profile = hub_sketch
hub.Length = flangeYMin - hubYMin + 0.05
hub.Reversed = True
doc.recompute()

flange_sketch = body.newObject("Sketcher::SketchObject", "FlangeSketch")
attach_xz(flange_sketch, flangeYMin)
add_circle(flange_sketch, flangeDia)

flange = body.newObject("PartDesign::Pad", "Flange")
flange.Profile = flange_sketch
flange.Length = flangeYMax - flangeYMin
flange.Reversed = True
doc.recompute()


def two_point_arc(p0, p1, radius, larger_x_center):
    x0, y0 = p0
    x1, y1 = p1
    chord = math.hypot(x1 - x0, y1 - y0)
    rise = math.sqrt(max(radius * radius - (chord / 2.0) ** 2, 0.0))
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    ux, uy = (x1 - x0) / chord, (y1 - y0) / chord
    c0 = (mx - rise * uy, my + rise * ux)
    c1 = (mx + rise * uy, my - rise * ux)
    center = c0 if (c0[0] > c1[0]) == larger_x_center else c1
    a0 = math.atan2(y0 - center[1], x0 - center[0])
    a1 = math.atan2(y1 - center[1], x1 - center[0])
    delta = (a1 - a0 + math.pi) % (2.0 * math.pi) - math.pi
    amid = a0 + 0.5 * delta
    mid = (center[0] + radius * math.cos(amid), center[1] + radius * math.sin(amid))
    return Part.ArcOfCircle(
        FreeCAD.Vector(x0, y0, 0),
        FreeCAD.Vector(mid[0], mid[1], 0),
        FreeCAD.Vector(x1, y1, 0),
    )


# Section-z0 bowl: shallow concave arc (not the R≈8 algebraic fit).
waist_arc_r = 45.17
lip_r = grooveInnerRadius - hubNeckRadius
lip_end_r = grooveInnerRadius + lip_r * math.cos(math.radians(60.0))
lip_end_y = hubNeckY + lip_r * math.sin(math.radians(60.0))
lip_mid_r = grooveInnerRadius + lip_r * math.cos(math.radians(120.0))
lip_mid_y = hubNeckY + lip_r * math.sin(math.radians(120.0))
od_over = 0.3
ring_bottom_y = hubNeckY + lip_r - 0.6

waist_sk = body.newObject("Sketcher::SketchObject", "WaistSketch")
attach(waist_sk, xy)
add_blocked(
    waist_sk,
    (
        Part.LineSegment(
            FreeCAD.Vector(hubRadius + od_over, hubWaistY, 0),
            FreeCAD.Vector(hubRadius, hubWaistY, 0),
        ),
        two_point_arc((hubRadius, hubWaistY), (hubNeckRadius, hubNeckY), waist_arc_r, True),
        Part.ArcOfCircle(
            FreeCAD.Vector(hubNeckRadius, hubNeckY, 0),
            FreeCAD.Vector(lip_mid_r, lip_mid_y, 0),
            FreeCAD.Vector(lip_end_r, lip_end_y, 0),
        ),
        Part.LineSegment(
            FreeCAD.Vector(lip_end_r, lip_end_y, 0),
            FreeCAD.Vector(hubRadius + od_over, lip_end_y, 0),
        ),
        Part.LineSegment(
            FreeCAD.Vector(hubRadius + od_over, lip_end_y, 0),
            FreeCAD.Vector(hubRadius + od_over, hubWaistY, 0),
        ),
    ),
)
waist = body.newObject("PartDesign::Groove", "HubWaist")
waist.Profile = waist_sk
waist.ReferenceAxis = (waist_sk, ["V_Axis"])
waist.Angle = 360.0
waist.Midplane = False
waist.Reversed = False
doc.recompute()

ring_sk = body.newObject("Sketcher::SketchObject", "ShoulderSketch")
attach_xz(ring_sk, grooveY)
add_circle(ring_sk, 2.0 * (hubRadius + od_over))
add_circle(ring_sk, 2.0 * grooveInnerRadius)
ring = body.newObject("PartDesign::Pocket", "GrooveShoulder")
ring.Profile = ring_sk
ring.Type = "Length"
ring.Length = grooveY - ring_bottom_y
ring.Reversed = True
doc.recompute()

z_cut = flangeRadius + 0.2
slot_sk = body.newObject("Sketcher::SketchObject", "SlotSketch")
attach_xz(slot_sk, flangeYMax)
add_blocked(
    slot_sk,
    (
        Part.LineSegment(FreeCAD.Vector(-slotHalf, -z_cut, 0), FreeCAD.Vector(slotHalf, -z_cut, 0)),
        Part.LineSegment(FreeCAD.Vector(slotHalf, -z_cut, 0), FreeCAD.Vector(slotHalf, z_cut, 0)),
        Part.LineSegment(FreeCAD.Vector(slotHalf, z_cut, 0), FreeCAD.Vector(-slotHalf, z_cut, 0)),
        Part.LineSegment(FreeCAD.Vector(-slotHalf, z_cut, 0), FreeCAD.Vector(-slotHalf, -z_cut, 0)),
    ),
)
slot = body.newObject("PartDesign::Pocket", "USlot")
slot.Profile = slot_sk
slot.Type = "Length"
slot.Length = flangeYMax - slotY
slot.Reversed = True
doc.recompute()

mid_dia = (holeMinorDia + holeMajorDia) / 2.0
r_min = holeMinorDia / 2.0
r_mid = mid_dia / 2.0
chamfer = r_mid - r_min
outer_cone_x = xFace - chamfer
inner_cone_x = slotHalf + chamfer
end_x = xFace + 0.05


def coaxial_profile():
    return (
        Part.LineSegment(FreeCAD.Vector(-end_x, 0, 0), FreeCAD.Vector(end_x, 0, 0)),
        Part.LineSegment(FreeCAD.Vector(end_x, 0, 0), FreeCAD.Vector(end_x, r_mid, 0)),
        Part.LineSegment(FreeCAD.Vector(end_x, r_mid, 0), FreeCAD.Vector(xFace, r_mid, 0)),
        Part.LineSegment(FreeCAD.Vector(xFace, r_mid, 0), FreeCAD.Vector(outer_cone_x, r_min, 0)),
        Part.LineSegment(FreeCAD.Vector(outer_cone_x, r_min, 0), FreeCAD.Vector(inner_cone_x, r_min, 0)),
        Part.LineSegment(FreeCAD.Vector(inner_cone_x, r_min, 0), FreeCAD.Vector(slotHalf, r_mid, 0)),
        Part.LineSegment(FreeCAD.Vector(slotHalf, r_mid, 0), FreeCAD.Vector(-slotHalf, r_mid, 0)),
        Part.LineSegment(FreeCAD.Vector(-slotHalf, r_mid, 0), FreeCAD.Vector(-inner_cone_x, r_min, 0)),
        Part.LineSegment(FreeCAD.Vector(-inner_cone_x, r_min, 0), FreeCAD.Vector(-outer_cone_x, r_min, 0)),
        Part.LineSegment(FreeCAD.Vector(-outer_cone_x, r_min, 0), FreeCAD.Vector(-xFace, r_mid, 0)),
        Part.LineSegment(FreeCAD.Vector(-xFace, r_mid, 0), FreeCAD.Vector(-end_x, r_mid, 0)),
        Part.LineSegment(FreeCAD.Vector(-end_x, r_mid, 0), FreeCAD.Vector(-end_x, 0, 0)),
    )


def bore_groove(name, z_station):
    plane = make_xy_plane(name + "Plane", (0.0, holeY, z_station))
    sk = body.newObject("Sketcher::SketchObject", name + "Sketch")
    attach(sk, plane)
    add_blocked(sk, coaxial_profile())
    groove = body.newObject("PartDesign::Groove", name)
    groove.Profile = sk
    groove.ReferenceAxis = (sk, ["H_Axis"])
    groove.Angle = 360.0
    groove.Midplane = False
    groove.Reversed = False
    doc.recompute()
    return groove


bore_groove("BorePosZ", holeZ)
bore_groove("BoreNegZ", -holeZ)

major_len = flangeRadius - xFace + 3.0
yz_pos = make_yz_plane("MajorPosXPlane", xFace)
major_pos_sk = body.newObject("Sketcher::SketchObject", "MajorPosXSketch")
attach(major_pos_sk, yz_pos)
add_circle(major_pos_sk, holeMajorDia, holeMajorPosY, holeMajorPosZ)
add_circle(major_pos_sk, holeMajorDia, holeY, -holeZ)
major_pos = body.newObject("PartDesign::Pocket", "MajorPosX")
major_pos.Profile = major_pos_sk
major_pos.Type = "Length"
major_pos.Length = major_len
major_pos.Reversed = True
doc.recompute()

yz_neg = make_yz_plane("MajorNegXPlane", -xFace)
major_neg_sk = body.newObject("Sketcher::SketchObject", "MajorNegXSketch")
attach(major_neg_sk, yz_neg)
add_circle(major_neg_sk, holeMajorDia, holeMajorPosY, holeMajorPosZ)
add_circle(major_neg_sk, holeMajorDia, holeY, -holeZ)
major_neg = body.newObject("PartDesign::Pocket", "MajorNegX")
major_neg.Profile = major_neg_sk
major_neg.Type = "Length"
major_neg.Length = major_len
major_neg.Reversed = False
doc.recompute()


def make_aimed_plane(name, origin, z_dir):
    z = FreeCAD.Vector(z_dir)
    z.normalize()
    x = FreeCAD.Vector(0, 1, 0)
    if abs(z.dot(x)) > 0.9:
        x = FreeCAD.Vector(1, 0, 0)
    y = z.cross(x)
    y.normalize()
    x = y.cross(z)
    x.normalize()
    plane = body.newObject("PartDesign::Plane", name)
    plane.MapMode = "Deactivated"
    plane.Placement = FreeCAD.Placement(origin, FreeCAD.Rotation(x, y, z, "ZXY"))
    return plane


skin_over = 0.6
start_r = flangeRadius + skin_over
cut_len = rimHoleLen + skin_over


def rim_hole(name, z_sign):
    outward = FreeCAD.Vector(rimHoleX, 0.0, z_sign * rimHoleZ)
    outward.normalize()
    origin = FreeCAD.Vector(outward.x * start_r, rimHoleY, outward.z * start_r)
    inward = FreeCAD.Vector(-outward.x, 0.0, -outward.z)
    plane = make_aimed_plane(name + "Plane", origin, inward)
    sk = body.newObject("Sketcher::SketchObject", name + "Sketch")
    attach(sk, plane)
    add_circle(sk, rimHoleDia)
    pocket = body.newObject("PartDesign::Pocket", name)
    pocket.Profile = sk
    pocket.Type = "Length"
    pocket.Length = cut_len
    pocket.Reversed = True
    return pocket


rim_pos = rim_hole("RimHolePosZ", 1.0)
rim_neg = rim_hole("RimHoleNegZ", -1.0)
rim_neg.Refine = True
doc.recompute()

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
result = body

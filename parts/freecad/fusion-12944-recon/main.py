import math

import FreeCAD
import Part
import PartDesign
import Sketcher

xMin = -63.351
yMin = 0.0
zMin = -54.0
spanX = 126.701
plateThickness = 15.0
spanZ = 108.0
centerHoleDiameter = 18.0
mountHoleDiameter = 10.0
mountHoleLength = 11.0
mountHoleY0 = 4.0
bossDiameter = 24.0
sideCutDiameter = 174.0
sideCutCentreX = 141.0
mountCentreX = 51.351
mountCentreZ = 42.0
pocketDepth = 3.0
xMax = 63.351
yMax = 15.0
zMax = 54.0
pocketFloorY = 3.0
pocketCeilY = 12.0
hubDiameter = 36.0
pocketDiameter = 81.174
filletRadius = 3.0

assert spanX > 0.0, "infeasible: spanX must be positive"
assert spanZ > 0.0, "infeasible: spanZ must be positive"
assert plateThickness > 0.0, "infeasible: plateThickness must be positive"
assert xMax > xMin, "infeasible: xMax must be greater than xMin"
assert yMax > yMin, "infeasible: yMax must be greater than yMin"
assert zMax > zMin, "infeasible: zMax must be greater than zMin"
assert bossDiameter > 0.0, "infeasible: bossDiameter must be positive"
assert sideCutDiameter > 0.0, "infeasible: sideCutDiameter must be positive"
assert sideCutCentreX > 0.0, "infeasible: sideCutCentreX must be positive"
assert mountCentreX > 0.0, "infeasible: mountCentreX must be positive"
assert mountCentreZ > 0.0, "infeasible: mountCentreZ must be positive"
assert centerHoleDiameter > 0.0, "infeasible: centerHoleDiameter must be positive"
assert centerHoleDiameter < hubDiameter, "infeasible: centerHoleDiameter must stay inside the hub"
assert mountHoleDiameter > 0.0, "infeasible: mountHoleDiameter must be positive"
assert mountHoleDiameter < bossDiameter, "infeasible: mountHoleDiameter must stay inside the boss"
assert mountHoleLength > 0.0, "infeasible: mountHoleLength must be positive"
assert mountHoleY0 >= yMin, "infeasible: mountHoleY0 is below the plate"
assert mountHoleY0 + mountHoleLength <= yMax + 0.05, "infeasible: mount hole extends past yMax"
assert pocketDepth > 0.0, "infeasible: pocketDepth must be positive"
assert 2.0 * pocketDepth < plateThickness, "infeasible: pockets would consume the plate"
assert pocketFloorY > yMin, "infeasible: pocketFloorY must sit above yMin"
assert pocketCeilY < yMax, "infeasible: pocketCeilY must sit below yMax"
assert hubDiameter > 0.0, "infeasible: hubDiameter must be positive"
assert pocketDiameter > hubDiameter, "infeasible: pocketDiameter must exceed the hub"
assert filletRadius >= 0.0, "infeasible: filletRadius must be non-negative"
assert sideCutCentreX - sideCutDiameter / 2.0 < xMax, "infeasible: +x side cut misses the plate"
assert -sideCutCentreX + sideCutDiameter / 2.0 > xMin, "infeasible: -x side cut misses the plate"

_ = PartDesign
boss_r = bossDiameter / 2.0
z_axis = FreeCAD.Vector(0, 0, 1)
cut_over = 0.05
# Face mouths are Ø18→Ø10 cones; literals so bore/hole edits do not move them.
csk_face_r = 9.0
csk_inner_r = 5.0
hub_r = hubDiameter / 2.0
pocket_r = pocketDiameter / 2.0
corner_r = min(pocketDepth, filletRadius)
if corner_r > 0.0:
    pocket_cut_r = corner_r + math.sqrt(pocket_r * pocket_r - hub_r * hub_r + (hub_r + corner_r) * (hub_r + corner_r))
else:
    pocket_cut_r = pocket_r
extra_depth = pocketDepth - corner_r
open_extra = 0.10
mount_pts = (
    (mountCentreX, mountCentreZ),
    (mountCentreX, -mountCentreZ),
    (-mountCentreX, mountCentreZ),
    (-mountCentreX, -mountCentreZ),
)

doc = FreeCAD.newDocument("fusion-12944-recon")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xy_plane = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)


def make_xz_plane(name, y):
    plane = body.newObject("PartDesign::Plane", name)
    plane.MapMode = "Deactivated"
    plane.Placement = FreeCAD.Placement(
        FreeCAD.Vector(0.0, y, 0.0),
        FreeCAD.Rotation(
            FreeCAD.Vector(1, 0, 0),
            FreeCAD.Vector(0, 0, 1),
            FreeCAD.Vector(0, 1, 0),
            "ZXY",
        ),
    )
    return plane


def attach(sk, plane):
    sk.AttachmentSupport = [(plane, "")]
    sk.MapMode = "FlatFace"


def add_blocked(sk, geoms):
    for geom in geoms:
        gid = sk.addGeometry(geom, False)
        sk.addConstraint(Sketcher.Constraint("Block", gid))


def add_circle(sk, cx, cy, diameter):
    gid = sk.addGeometry(Part.Circle(FreeCAD.Vector(cx, cy, 0), z_axis, diameter / 2.0), False)
    sk.addConstraint(Sketcher.Constraint("Diameter", gid, diameter))
    sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gid, 3, cx))
    sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gid, 3, cy))
    return gid


datum_a = make_xz_plane("DatumA", yMin)
datum_top = make_xz_plane("DatumTop", yMax)
datum_csk = make_xz_plane("DatumCsk", mountHoleY0)

sketch = body.newObject("Sketcher::SketchObject", "BlankSketch")
attach(sketch, datum_a)
add_blocked(
    sketch,
    (
        Part.LineSegment(FreeCAD.Vector(xMax, -mountCentreZ, 0), FreeCAD.Vector(xMax, mountCentreZ, 0)),
        Part.ArcOfCircle(
            Part.Circle(FreeCAD.Vector(mountCentreX, mountCentreZ, 0), z_axis, boss_r),
            0.0,
            math.pi / 2.0,
        ),
        Part.LineSegment(FreeCAD.Vector(mountCentreX, zMax, 0), FreeCAD.Vector(-mountCentreX, zMax, 0)),
        Part.ArcOfCircle(
            Part.Circle(FreeCAD.Vector(-mountCentreX, mountCentreZ, 0), z_axis, boss_r),
            math.pi / 2.0,
            math.pi,
        ),
        Part.LineSegment(FreeCAD.Vector(xMin, mountCentreZ, 0), FreeCAD.Vector(xMin, -mountCentreZ, 0)),
        Part.ArcOfCircle(
            Part.Circle(FreeCAD.Vector(-mountCentreX, -mountCentreZ, 0), z_axis, boss_r),
            math.pi,
            3.0 * math.pi / 2.0,
        ),
        Part.LineSegment(FreeCAD.Vector(-mountCentreX, zMin, 0), FreeCAD.Vector(mountCentreX, zMin, 0)),
        Part.ArcOfCircle(
            Part.Circle(FreeCAD.Vector(mountCentreX, -mountCentreZ, 0), z_axis, boss_r),
            3.0 * math.pi / 2.0,
            2.0 * math.pi,
        ),
    ),
)

pad = body.newObject("PartDesign::Pad", "PlateBlank")
pad.Profile = sketch
pad.Length = plateThickness
pad.Midplane = False
pad.Reversed = False
doc.recompute()

cut_sketch = body.newObject("Sketcher::SketchObject", "SideCutSketch")
attach(cut_sketch, datum_a)
for cx in (sideCutCentreX, -sideCutCentreX):
    add_circle(cut_sketch, cx, 0.0, sideCutDiameter)

side_cuts = body.newObject("PartDesign::Pocket", "SideCuts")
side_cuts.Profile = cut_sketch
side_cuts.Type = "ThroughAll"
side_cuts.Reversed = True
doc.recompute()


def arc_mid(p0, p1, radius, toward):
    mx = (p0[0] + p1[0]) / 2.0
    my = (p0[1] + p1[1]) / 2.0
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    dist = math.hypot(dx, dy)
    height = math.sqrt(max(radius * radius - (dist / 2.0) ** 2, 0.0))
    ux, uy = -dy / dist, dx / dist

    def mid(ctr):
        s0 = (p0[0] - ctr[0]) / radius + (p1[0] - ctr[0]) / radius
        s1 = (p0[1] - ctr[1]) / radius + (p1[1] - ctr[1]) / radius
        norm = math.hypot(s0, s1)
        return (ctr[0] + radius * s0 / norm, ctr[1] + radius * s1 / norm)

    m0 = mid((mx + height * ux, my + height * uy))
    m1 = mid((mx - height * ux, my - height * uy))
    if math.hypot(m0[0] - toward[0], m0[1] - toward[1]) < math.hypot(m1[0] - toward[0], m1[1] - toward[1]):
        return m0
    return m1


def pocket_profile(y_face, sign):
    y_out = y_face - sign * cut_over
    y_blend = y_face + sign * corner_r
    r_open = pocket_cut_r + open_extra
    r_wall = pocket_cut_r - corner_r
    half = math.sqrt(2.0) / 2.0
    if corner_r > 0.0:
        p_hub = (hub_r, y_face)
        p_inner = (hub_r + corner_r, y_blend)
        p_wall = (r_wall, y_blend)
        p_outer = (r_open, y_face)
        mid_in = (hub_r + corner_r - corner_r * half, y_face + sign * corner_r * half)
        mid_out = arc_mid(p_wall, p_outer, corner_r, (r_open, y_blend))
        return (
            Part.LineSegment(FreeCAD.Vector(hub_r, y_out, 0), FreeCAD.Vector(r_open, y_out, 0)),
            Part.LineSegment(FreeCAD.Vector(r_open, y_out, 0), FreeCAD.Vector(p_outer[0], p_outer[1], 0)),
            Part.ArcOfCircle(
                FreeCAD.Vector(p_outer[0], p_outer[1], 0),
                FreeCAD.Vector(mid_out[0], mid_out[1], 0),
                FreeCAD.Vector(p_wall[0], p_wall[1], 0),
            ),
            Part.LineSegment(
                FreeCAD.Vector(p_wall[0], p_wall[1], 0),
                FreeCAD.Vector(p_inner[0], p_inner[1], 0),
            ),
            Part.ArcOfCircle(
                FreeCAD.Vector(p_inner[0], p_inner[1], 0),
                FreeCAD.Vector(mid_in[0], mid_in[1], 0),
                FreeCAD.Vector(p_hub[0], p_hub[1], 0),
            ),
            Part.LineSegment(FreeCAD.Vector(p_hub[0], p_hub[1], 0), FreeCAD.Vector(hub_r, y_out, 0)),
        )
    return (
        Part.LineSegment(FreeCAD.Vector(hub_r, y_out, 0), FreeCAD.Vector(pocket_cut_r, y_out, 0)),
        Part.LineSegment(FreeCAD.Vector(pocket_cut_r, y_out, 0), FreeCAD.Vector(pocket_cut_r, y_blend, 0)),
        Part.LineSegment(FreeCAD.Vector(pocket_cut_r, y_blend, 0), FreeCAD.Vector(hub_r, y_blend, 0)),
        Part.LineSegment(FreeCAD.Vector(hub_r, y_blend, 0), FreeCAD.Vector(hub_r, y_out, 0)),
    )


def groove_pocket(name, y_face, sign):
    sk = body.newObject("Sketcher::SketchObject", name + "Sketch")
    attach(sk, xy_plane)
    add_blocked(sk, pocket_profile(y_face, sign))
    groove = body.newObject("PartDesign::Groove", name)
    groove.Profile = sk
    groove.ReferenceAxis = (sk, ["V_Axis"])
    groove.Angle = 360.0
    groove.Midplane = False
    groove.Reversed = False
    doc.recompute()
    return groove


groove_pocket("PocketMinusY", yMin, 1.0)
groove_pocket("PocketPlusY", yMax, -1.0)


def extra_ring(name, y_station, reversed_cut):
    plane = make_xz_plane(name + "Plane", y_station)
    sk = body.newObject("Sketcher::SketchObject", name + "Sketch")
    attach(sk, plane)
    add_circle(sk, 0.0, 0.0, 2.0 * (pocket_cut_r - corner_r))
    add_circle(sk, 0.0, 0.0, 2.0 * (hub_r + corner_r))
    pocket = body.newObject("PartDesign::Pocket", name)
    pocket.Profile = sk
    pocket.Type = "Length"
    pocket.Length = extra_depth + cut_over
    pocket.Reversed = reversed_cut
    doc.recompute()
    return pocket


if extra_depth > 1e-6:
    extra_ring("PocketExtraMinusY", yMin + corner_r, True)
    extra_ring("PocketExtraPlusY", yMax - corner_r, False)

bore_sketch = body.newObject("Sketcher::SketchObject", "CentreBoreSketch")
attach(bore_sketch, datum_a)
add_circle(bore_sketch, 0.0, 0.0, centerHoleDiameter)
centre_bore = body.newObject("PartDesign::Pocket", "CentreBore")
centre_bore.Profile = bore_sketch
centre_bore.Type = "ThroughAll"
centre_bore.Reversed = True
doc.recompute()

mount_sketch = body.newObject("Sketcher::SketchObject", "MountHoleSketch")
attach(mount_sketch, datum_top)
for mx, mz in mount_pts:
    add_circle(mount_sketch, mx, mz, mountHoleDiameter)
mount_holes = body.newObject("PartDesign::Pocket", "MountHoles")
mount_holes.Profile = mount_sketch
mount_holes.Type = "Length"
mount_holes.Length = mountHoleLength + cut_over
mount_holes.Reversed = False
doc.recompute()

csk_face = body.newObject("Sketcher::SketchObject", "CskFaceSketch")
attach(csk_face, datum_a)
csk_inner = body.newObject("Sketcher::SketchObject", "CskInnerSketch")
attach(csk_inner, datum_csk)
for mx, mz in mount_pts:
    add_circle(csk_face, mx, mz, 2.0 * csk_face_r)
    add_circle(csk_inner, mx, mz, 2.0 * csk_inner_r)
csk = body.newObject("PartDesign::SubtractiveLoft", "MountCones")
csk.Profile = csk_face
csk.Sections = [csk_inner]
csk.Ruled = True
csk.Refine = True
doc.recompute()

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
assert body.Shape.Solids, "kernel: finished plate produced no solid"
result = body

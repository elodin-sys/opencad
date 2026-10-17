import math

import FreeCAD
import Part
import PartDesign
import Sketcher

envelopeMinX = -10.242
envelopeMinY = 0.0
envelopeMinZ = -10.242
envelopeSizeX = 20.483
envelopeSizeY = 4.0
envelopeSizeZ = 20.483
discThickness = 3.0
hexFloorY = 1.0
hexPocketFlat = 3.463
hexBossFlat = 4.332
hexPocketVertex = 4.0
hexBossVertex = 5.0
boreDiameter = 3.1
boreLength = 1.0
rootDiameter = 19.0
tipFilletDiameter = 0.2
tipCircleRadius = 10.142
toothCount = 36
toothPhase = 0.0
hubHeight = 1.0
hexPocketDepth = 3.0
hexPocketAcross = 6.926
hexBossAcross = 8.664
boreRadius = 1.55
rootRadius = 9.5
tipFilletRadius = 0.1
tipOuterRadius = 10.242
toothPitchDeg = 10.0
gearModule = 0.569

assert envelopeSizeY > discThickness, "infeasible: envelopeSizeY must exceed discThickness"
assert envelopeSizeY > envelopeMinY, "infeasible: envelopeSizeY must sit above envelopeMinY"
assert discThickness > 0, "infeasible: discThickness must be positive"
assert tipOuterRadius > 0, "infeasible: tipOuterRadius must be positive"
assert hexBossVertex > 0, "infeasible: hexBossVertex must be positive"
assert hexBossFlat > 0, "infeasible: hexBossFlat must be positive"
assert hexPocketVertex > 0, "infeasible: hexPocketVertex must be positive"
assert hexPocketFlat > 0, "infeasible: hexPocketFlat must be positive"
assert hexFloorY > envelopeMinY, "infeasible: hexFloorY must sit above the seating face"
assert hexFloorY < envelopeSizeY, "infeasible: hexFloorY must sit below the boss cap"
assert hexPocketVertex < hexBossVertex, "infeasible: hex pocket must sit inside the boss"
assert rootRadius > 0, "infeasible: rootRadius must be positive"
assert tipCircleRadius > rootRadius, "infeasible: tipCircleRadius must exceed rootRadius"
assert tipFilletRadius > 0, "infeasible: tipFilletRadius must be positive"
assert boreDiameter > 0, "infeasible: boreDiameter must be positive"
assert boreRadius > 0, "infeasible: boreRadius must be positive"
assert toothCount > 1, "infeasible: toothCount must be at least 2"
assert rootRadius > hexBossVertex, "infeasible: rootRadius must clear the hex boss"

_ = PartDesign
_ = envelopeMinX
_ = envelopeMinZ
_ = envelopeSizeX
_ = envelopeSizeZ
_ = hexPocketDepth
_ = hexPocketAcross
_ = hexBossAcross
_ = hubHeight
_ = boreLength
_ = rootDiameter
_ = tipFilletDiameter
_ = gearModule

doc = FreeCAD.newDocument("fusion_16418_recon")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xz = next(f for f in body.Origin.OriginFeatures if "XZ" in f.Name and "Plane" in f.Name)


def attach_xz(sketch, y):
    if hasattr(sketch, "AttachmentSupport"):
        sketch.AttachmentSupport = [(xz, "")]
    else:
        sketch.Support = [(xz, "")]
    sketch.MapMode = "FlatFace"
    # XZ local +z is −Y; negative offset places the sketch at world y.
    sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, -y), FreeCAD.Rotation())


def add_circle(sketch, radius):
    gid = sketch.addGeometry(
        Part.Circle(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), radius),
        False,
    )
    sketch.addConstraint(Sketcher.Constraint("Radius", gid, radius))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gid, 3, 0.0))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gid, 3, 0.0))
    return gid


def pin_xy(sketch, gid, vertex, x, y):
    sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gid, vertex, x))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gid, vertex, y))


def tooth0_points(phase_deg):
    # 30° + 10° pitch stacks opposite flanks on one plane; sheet toothFlankA is 30.403°.
    half = math.atan2(0.5061, 0.8625)
    phase = math.radians(phase_deg)
    n_cw = (math.sin(half), -math.cos(half))
    n_ccw = (math.sin(half), math.cos(half))
    c0 = (tipCircleRadius, 0.0)
    t_cw = (c0[0] + tipFilletRadius * n_cw[0], c0[1] + tipFilletRadius * n_cw[1])
    t_ccw = (c0[0] + tipFilletRadius * n_ccw[0], c0[1] + tipFilletRadius * n_ccw[1])
    outer = (c0[0] + tipFilletRadius, 0.0)
    d_cw = (-math.cos(half), -math.sin(half))
    d_ccw = (-math.cos(half), math.sin(half))

    def hit_root(point, direction):
        b = 2 * (point[0] * direction[0] + point[1] * direction[1])
        c_term = point[0] ** 2 + point[1] ** 2 - rootRadius**2
        disc = b * b - 4 * c_term
        assert disc > 0, "infeasible: tooth flank must meet the root circle"
        root_d = math.sqrt(disc)
        ts = [(-b - root_d) / 2, (-b + root_d) / 2]
        t = min(val for val in ts if val > 1e-12)
        return (point[0] + t * direction[0], point[1] + t * direction[1])

    r_cw = hit_root(t_cw, d_cw)
    r_ccw = hit_root(t_ccw, d_ccw)
    inner = (0.5 * (hexBossVertex + rootRadius), 0.0)
    cos_a, sin_a = math.cos(phase), math.sin(phase)

    def rot(p):
        return (p[0] * cos_a - p[1] * sin_a, p[0] * sin_a + p[1] * cos_a)

    return rot(t_cw), rot(outer), rot(t_ccw), rot(r_ccw), rot(inner), rot(r_cw), rot(c0)


def add_tooth(sketch, phase_deg):
    t_cw, _outer, t_ccw, r_ccw, inner, r_cw, center = tooth0_points(phase_deg)
    a0 = math.atan2(t_cw[1] - center[1], t_cw[0] - center[0])
    a1 = math.atan2(t_ccw[1] - center[1], t_ccw[0] - center[0])
    g0 = sketch.addGeometry(
        Part.LineSegment(FreeCAD.Vector(r_cw[0], r_cw[1], 0), FreeCAD.Vector(t_cw[0], t_cw[1], 0)),
        False,
    )
    g1 = sketch.addGeometry(
        Part.ArcOfCircle(
            Part.Circle(FreeCAD.Vector(center[0], center[1], 0), FreeCAD.Vector(0, 0, 1), tipFilletRadius),
            a0,
            a1,
        ),
        False,
    )
    g2 = sketch.addGeometry(
        Part.LineSegment(FreeCAD.Vector(t_ccw[0], t_ccw[1], 0), FreeCAD.Vector(r_ccw[0], r_ccw[1], 0)),
        False,
    )
    g3 = sketch.addGeometry(
        Part.LineSegment(FreeCAD.Vector(r_ccw[0], r_ccw[1], 0), FreeCAD.Vector(inner[0], inner[1], 0)),
        False,
    )
    g4 = sketch.addGeometry(
        Part.LineSegment(FreeCAD.Vector(inner[0], inner[1], 0), FreeCAD.Vector(r_cw[0], r_cw[1], 0)),
        False,
    )
    pin_xy(sketch, g0, 1, r_cw[0], r_cw[1])
    pin_xy(sketch, g0, 2, t_cw[0], t_cw[1])
    pin_xy(sketch, g1, 3, center[0], center[1])
    pin_xy(sketch, g2, 1, t_ccw[0], t_ccw[1])
    pin_xy(sketch, g2, 2, r_ccw[0], r_ccw[1])
    pin_xy(sketch, g3, 2, inner[0], inner[1])
    pin_xy(sketch, g4, 1, inner[0], inner[1])
    pin_xy(sketch, g4, 2, r_cw[0], r_cw[1])


def add_pointy_hex(sketch, vertex):
    pts = []
    for k in range(6):
        ang = math.radians(90.0 + k * 60.0)
        pts.append((vertex * math.cos(ang), vertex * math.sin(ang)))
    for i in range(6):
        a, b = pts[i], pts[(i + 1) % 6]
        sketch.addGeometry(
            Part.LineSegment(FreeCAD.Vector(a[0], a[1], 0), FreeCAD.Vector(b[0], b[1], 0)),
            False,
        )
    for i in range(6):
        sketch.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 6, 1))
    for i in range(6):
        sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, i, 1, pts[i][0]))
        sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, i, 1, pts[i][1]))


disc_sketch = body.newObject("Sketcher::SketchObject", "DiscSketch")
attach_xz(disc_sketch, envelopeMinY)
add_circle(disc_sketch, rootRadius)

disc = body.newObject("PartDesign::Pad", "Disc")
disc.Profile = disc_sketch
disc.Length = discThickness
disc.Reversed = True
doc.recompute()

tooth_sketch = body.newObject("Sketcher::SketchObject", "ToothSketch")
attach_xz(tooth_sketch, envelopeMinY)
for k in range(toothCount):
    add_tooth(tooth_sketch, toothPhase + k * toothPitchDeg)

tooth = body.newObject("PartDesign::Pad", "Teeth")
tooth.Profile = tooth_sketch
tooth.Length = discThickness
tooth.Reversed = True
doc.recompute()

hex_sketch = body.newObject("Sketcher::SketchObject", "HexBossSketch")
attach_xz(hex_sketch, envelopeMinY + discThickness)
add_pointy_hex(hex_sketch, hexBossVertex)

hex_boss = body.newObject("PartDesign::Pad", "HexBoss")
hex_boss.Profile = hex_sketch
hex_boss.Length = envelopeSizeY - discThickness
hex_boss.Reversed = True
doc.recompute()

pocket_sketch = body.newObject("Sketcher::SketchObject", "HexPocketSketch")
attach_xz(pocket_sketch, envelopeSizeY)
add_pointy_hex(pocket_sketch, hexPocketVertex)

hex_pocket = body.newObject("PartDesign::Pocket", "HexPocket")
hex_pocket.Profile = pocket_sketch
hex_pocket.Length = envelopeSizeY - hexFloorY
hex_pocket.Reversed = True
doc.recompute()

bore_sketch = body.newObject("Sketcher::SketchObject", "BoreSketch")
attach_xz(bore_sketch, envelopeMinY)
add_circle(bore_sketch, boreRadius)

bore = body.newObject("PartDesign::Pocket", "CenterBore")
bore.Profile = bore_sketch
bore.Length = hexFloorY - envelopeMinY
bore.Refine = True
doc.recompute()

result = body

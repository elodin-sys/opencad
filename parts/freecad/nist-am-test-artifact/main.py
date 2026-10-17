import math

import FreeCAD
import Part
import Sketcher

baseSide = 100.0
baseRotation = 45.0
baseThickness = 10.0
baseHalfDiagonal = 70.71067811865474
mainPinDiameter = 4.0
mainPinHeight = 7.0
pinFirstRadius = 20.0
pinPitch = 10.0
pinsPerArm = 4.0
mainHoleDiameter = 4.0
mainHoleRadius = 60.0
centerHoleDiameter = 10.0
lowerBossDiameter = 20.0
lowerBossHeight = 4.0
upperBossDiameter = 15.0
upperBossHeight = 3.0
stairInnerOffset = 12.0
stairTread = 10.0
stairFirstHeight = 3.0
stairIncrement = 1.0
rampLowHeight = 1.0
rampRise = 1.0
rampRun = 25.0
rampLanding = 2.5
rampWidth = 5.0
rampStartRadius = 15.0
fineHeightDepth = 2.0
fineSizeA = 2.0
fineSizeB = 1.5
fineSizeC = 1.0
fineSizeD = 0.5
fineSizeE = 0.25
fineFirstX = 28.284
fineFirstY = 21.213
finePitch = 5.0
rectOuterInset = 1.0
rectLengthRatio = 3.0
rectStartV1 = 2.0
rectStartV2 = 6.0
rectStartV3 = 11.0
rectStartV4 = 14.0
rectStartV5 = 17.5
rectStartV6 = 19.5
rectStartV7 = 22.0
rectStartV8 = 23.0
rectStartV9 = 24.5
rectStartV10 = 25.0
lateralCenterZ = -5.0
lateralFirstStation = 40.0
lateralPitch = 10.0
lateralSmallDiameter = 3.0
lateralSmallDepth = 3.0
lateralLargeDiameter = 6.0
lateralLargeDepth = 5.0
lateralSmallSquare = 3.0
lateralLargeSquare = 6.0
lateralSmallDiamond = 3.0
lateralSmallDiamondDepth = 3.0
lateralLargeDiamond = 6.0
lateralTallHeight = 6.0
lateralWideHeight = 4.0
lateralApexAngle = 60.0
lateralTallWidth = 3.4641016151377535
lateralWideWidth = 6.9282032302755105

assert baseSide > 0, "infeasible: baseSide must be positive"
assert 0 < baseRotation < 90, "infeasible: baseRotation must be an acute diamond angle"
assert baseThickness > 0, "infeasible: baseThickness must be positive"
assert baseHalfDiagonal > 0, "infeasible: baseHalfDiagonal must be positive"
assert mainPinDiameter > 0, "infeasible: mainPinDiameter must be positive"
assert mainPinHeight > 0, "infeasible: mainPinHeight must be positive"
assert pinFirstRadius > 0, "infeasible: pinFirstRadius must be positive"
assert pinPitch > 0, "infeasible: pinPitch must be positive"
assert pinsPerArm >= 1, "infeasible: pinsPerArm must place at least one pin"
assert pinsPerArm == int(pinsPerArm), "infeasible: pinsPerArm must be integral"
assert mainHoleDiameter > 0, "infeasible: mainHoleDiameter must be positive"
assert mainHoleRadius > 0, "infeasible: mainHoleRadius must be positive"
assert centerHoleDiameter > 0, "infeasible: centerHoleDiameter must be positive"
assert lowerBossDiameter > upperBossDiameter, "infeasible: lower boss must exceed the upper boss"
assert upperBossDiameter > centerHoleDiameter, "infeasible: upper boss must clear the centre bore"
assert lowerBossHeight > 0, "infeasible: lowerBossHeight must be positive"
assert upperBossHeight > 0, "infeasible: upperBossHeight must be positive"
assert stairInnerOffset > 0, "infeasible: stairInnerOffset must be positive"
assert stairTread > 0, "infeasible: stairTread must be positive"
assert stairFirstHeight > 0, "infeasible: stairFirstHeight must be positive"
assert stairIncrement > 0, "infeasible: stairIncrement must be positive"
assert baseThickness > stairFirstHeight + 4 * stairIncrement, "infeasible: recessed stairs would break the bottom"
assert rampLowHeight > 0, "infeasible: rampLowHeight must be positive"
assert rampRise > 0, "infeasible: rampRise must be positive"
assert rampRun > 0, "infeasible: rampRun must be positive"
assert rampLanding > 0, "infeasible: rampLanding must be positive"
assert rampWidth > 0, "infeasible: rampWidth must be positive"
assert rampStartRadius > 0, "infeasible: rampStartRadius must be positive"
assert fineHeightDepth > 0, "infeasible: fineHeightDepth must be positive"
assert baseThickness > fineHeightDepth, "infeasible: fine holes would break the bottom"
assert fineSizeA > fineSizeB > fineSizeC > fineSizeD > fineSizeE > 0, (
    "infeasible: fine sizes must descend and stay positive"
)
assert fineFirstX > 0, "infeasible: fineFirstX must be positive"
assert fineFirstY > 0, "infeasible: fineFirstY must be positive"
assert finePitch > fineSizeA, "infeasible: fine pins would overlap"
assert rectOuterInset > 0, "infeasible: rectOuterInset must be positive"
assert rectLengthRatio > 0, "infeasible: rectLengthRatio must be positive"
assert rectStartV1 > 0, "infeasible: rectStartV1 must be positive"
assert rectStartV2 > rectStartV1 + fineSizeA, "infeasible: rect bosses 1/2 would overlap"
assert rectStartV3 > rectStartV2 + fineSizeA, "infeasible: rect bosses 2/3 would overlap"
assert rectStartV4 > rectStartV3 + fineSizeB, "infeasible: rect bosses 3/4 would overlap"
assert rectStartV5 > rectStartV4 + fineSizeB, "infeasible: rect bosses 4/5 would overlap"
assert rectStartV6 > rectStartV5 + fineSizeC, "infeasible: rect bosses 5/6 would overlap"
assert rectStartV7 > rectStartV6 + fineSizeC, "infeasible: rect bosses 6/7 would overlap"
assert rectStartV8 > rectStartV7 + fineSizeD, "infeasible: rect bosses 7/8 would overlap"
assert rectStartV9 > rectStartV8 + fineSizeD, "infeasible: rect bosses 8/9 would overlap"
assert rectStartV10 > rectStartV9 + fineSizeE, "infeasible: rect bosses 9/10 would overlap"
assert lateralCenterZ < 0, "infeasible: lateralCenterZ must sit below datum A"
assert lateralFirstStation > 0, "infeasible: lateralFirstStation must be positive"
assert lateralPitch > 0, "infeasible: lateralPitch must be positive"
assert lateralSmallDiameter > 0, "infeasible: lateralSmallDiameter must be positive"
assert lateralSmallDepth > 0, "infeasible: lateralSmallDepth must be positive"
assert lateralLargeDiameter > 0, "infeasible: lateralLargeDiameter must be positive"
assert lateralLargeDepth > 0, "infeasible: lateralLargeDepth must be positive"
assert lateralSmallSquare > 0, "infeasible: lateralSmallSquare must be positive"
assert lateralLargeSquare > 0, "infeasible: lateralLargeSquare must be positive"
assert lateralSmallDiamond > 0, "infeasible: lateralSmallDiamond must be positive"
assert lateralSmallDiamondDepth > 0, "infeasible: lateralSmallDiamondDepth must be positive"
assert lateralLargeDiamond > 0, "infeasible: lateralLargeDiamond must be positive"
assert lateralTallHeight > 0, "infeasible: lateralTallHeight must be positive"
assert lateralWideHeight > 0, "infeasible: lateralWideHeight must be positive"
assert 0 < lateralApexAngle < 90, "infeasible: lateralApexAngle must be acute"
assert lateralTallWidth > 0, "infeasible: lateralTallWidth must be positive"
assert lateralWideWidth > 0, "infeasible: lateralWideWidth must be positive"
assert max(lateralTallWidth, lateralWideWidth) < lateralPitch, "infeasible: lateral rhombi would overlap"
assert mainPinDiameter < pinPitch, "infeasible: main pins would overlap"
assert pinFirstRadius - mainPinDiameter / 2 > lowerBossDiameter / 2, "infeasible: inner pins hit the lower boss"
assert pinFirstRadius + (pinsPerArm - 1) * pinPitch + mainPinDiameter / 2 < mainHoleRadius - mainHoleDiameter / 2, (
    "infeasible: outer pins hit the axis holes"
)
assert rampStartRadius > lowerBossDiameter / 2, "infeasible: ramp would hit the lower boss"
assert rampStartRadius + rampRun + 2 * rampLanding < baseSide / 2, "infeasible: ramp would leave the diamond"
assert rampWidth / 2 < baseSide / 2, "infeasible: ramp wider than the diamond"
assert rectOuterInset + rectLengthRatio * fineSizeA < baseSide / 2, "infeasible: longest rect would pass the centre"
assert rectStartV10 + fineSizeE < baseSide / 2, "infeasible: last rect would leave the diamond"
assert lateralCenterZ + max(lateralTallHeight, lateralLargeSquare, lateralLargeDiamond) / 2 < 0, (
    "infeasible: a lateral profile would break datum A"
)
assert lateralCenterZ - max(lateralTallHeight, lateralLargeSquare, lateralLargeDiamond) / 2 > -baseThickness, (
    "infeasible: a lateral profile would break the bottom"
)
assert baseHalfDiagonal > stairInnerOffset + 3 * stairTread, "infeasible: stairs would leave the diamond"

half = baseSide / 2.0
epsilon = fineSizeE / 10.0
turn = math.radians(baseRotation)
eu = (math.cos(turn), math.sin(turn))
ev = (math.sin(turn), -math.cos(turn))
n_pins = int(pinsPerArm)


def add_circle(sk, cx, cy, diameter):
    gid = sk.addGeometry(Part.Circle(FreeCAD.Vector(cx, cy, 0), FreeCAD.Vector(0, 0, 1), diameter / 2.0), False)
    sk.addConstraint(Sketcher.Constraint("Diameter", gid, diameter))
    sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gid, 3, cx))
    sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gid, 3, cy))
    return gid


def add_polygon(sk, pts):
    n = len(pts)
    gids = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        gids.append(
            sk.addGeometry(Part.LineSegment(FreeCAD.Vector(a[0], a[1], 0), FreeCAD.Vector(b[0], b[1], 0)), False)
        )
    for i in range(n):
        sk.addConstraint(Sketcher.Constraint("Coincident", gids[i], 2, gids[(i + 1) % n], 1))
        sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gids[i], 1, pts[i][0]))
        sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gids[i], 1, pts[i][1]))
    return gids


def uv(u, v):
    return (u * eu[0] + v * ev[0], u * eu[1] + v * ev[1])


def add_uv_rect(sk, u0, u1, v0, v1):
    add_polygon(sk, [uv(u0, v0), uv(u1, v0), uv(u1, v1), uv(u0, v1)])


def add_xy_rect(sk, xmin, xmax, ymin, ymax):
    add_polygon(sk, [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)])


doc = FreeCAD.newDocument("nist-am-test-artifact")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xy = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)


def sketch_on(name, support, z=0.0):
    sk = body.newObject("Sketcher::SketchObject", name)
    sk.AttachmentSupport = [(support, "")]
    sk.MapMode = "FlatFace"
    if z:
        sk.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, z), FreeCAD.Rotation())
    return sk


def make_plane(name, origin, x_dir, y_dir, normal):
    plane = body.newObject("PartDesign::Plane", name)
    plane.MapMode = "Deactivated"
    plane.Placement = FreeCAD.Placement(origin, FreeCAD.Rotation(x_dir, y_dir, normal, "ZXY"))
    return plane


def pad(name, sketch, length, reversed=False, refine=False):
    feat = body.newObject("PartDesign::Pad", name)
    feat.Profile = sketch
    feat.Length = length
    feat.Reversed = reversed
    if refine:
        feat.Refine = True
    doc.recompute()
    assert feat.Shape.isValid(), f"kernel: {name} is invalid after recompute"
    return feat


def pocket(name, sketch, length=None, through=False, reversed=False, refine=False):
    feat = body.newObject("PartDesign::Pocket", name)
    feat.Profile = sketch
    if through:
        feat.Type = "ThroughAll"
    else:
        feat.Type = "Length"
        feat.Length = length
    feat.Reversed = reversed
    if refine:
        feat.Refine = True
    doc.recompute()
    assert feat.Shape.isValid(), f"kernel: {name} is invalid after recompute"
    return feat


base_sketch = sketch_on("DiamondSketch", xy)
base_sketch.AttachmentOffset = FreeCAD.Placement(
    FreeCAD.Vector(0, 0, 0),
    FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), baseRotation),
)
add_xy_rect(base_sketch, -half, half, -half, half)
pad("DiamondBase", base_sketch, baseThickness, reversed=True)

lower_sketch = sketch_on("LowerBossSketch", xy)
add_circle(lower_sketch, 0.0, 0.0, lowerBossDiameter)
pad("LowerCentralBoss", lower_sketch, lowerBossHeight)

upper_sketch = sketch_on("UpperBossSketch", xy, lowerBossHeight)
add_circle(upper_sketch, 0.0, 0.0, upperBossDiameter)
pad("UpperCentralBoss", upper_sketch, upperBossHeight)

pin_sketch = sketch_on("MainPinSketch", xy)
for i in range(n_pins):
    r = pinFirstRadius + i * pinPitch
    for sx, sy in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
        add_circle(pin_sketch, sx * r, sy * r, mainPinDiameter)
pad("MainPins", pin_sketch, mainPinHeight)

a = stairInnerOffset
t = stairTread
raised = (
    ("RaisedOuterX", -a - 2.5 * t, a + 0.5 * t, stairFirstHeight),
    ("RaisedMiddleX", -a - 1.5 * t, a + 0.5 * t, stairFirstHeight + 2.0 * stairIncrement),
    ("RaisedElbow", -a - 0.5 * t, a + 0.5 * t, stairFirstHeight + 4.0 * stairIncrement),
    ("RaisedMiddleY", -a - 0.5 * t, a + 1.5 * t, stairFirstHeight + 3.0 * stairIncrement),
    ("RaisedOuterY", -a - 0.5 * t, a + 2.5 * t, stairFirstHeight + stairIncrement),
)
for name, cx, cy, ht in raised:
    sk = sketch_on(name + "Sketch", xy)
    add_xy_rect(sk, cx - t / 2.0, cx + t / 2.0, cy - t / 2.0, cy + t / 2.0)
    pad(name, sk, ht)

# Side tabs just below the elbow plane so leftover z=7 pin-cap probes cannot steal raisedTread_elbow.
tab = 0.3
tab_h = 0.03
elbow_z = stairFirstHeight + 4.0 * stairIncrement
pin_tab_sketch = sketch_on("PinPlaneTabSketch", xy, elbow_z - tab_h - 0.01)
for i in range(n_pins):
    r = pinFirstRadius + i * pinPitch
    for sx, sy in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
        ox = -sy * (mainPinDiameter / 2.0 + 0.1)
        oy = sx * (mainPinDiameter / 2.0 + 0.1)
        tx = sx * r + ox
        ty = sy * r + oy
        add_xy_rect(pin_tab_sketch, tx - tab / 2.0, tx + tab / 2.0, ty - tab / 2.0, ty + tab / 2.0)
pad("PinPlaneTabs", pin_tab_sketch, tab_h)

r0 = rampStartRadius
r1 = r0 + rampLanding
r2 = r1 + rampRun
r3 = r2 + rampLanding
h_low = rampLowHeight
h_high = rampLowHeight + rampRise
eu_v = FreeCAD.Vector(eu[0], eu[1], 0)
ev_v = FreeCAD.Vector(ev[0], ev[1], 0)
ez = FreeCAD.Vector(0, 0, 1)
ramp_plane = make_plane(
    "RampPlane",
    FreeCAD.Vector(eu_v.x * rampWidth / 2.0, eu_v.y * rampWidth / 2.0, 0),
    ev_v,
    ez,
    FreeCAD.Vector(-eu_v.x, -eu_v.y, 0),
)
ramp_sketch = sketch_on("RampSketch", ramp_plane)
add_polygon(
    ramp_sketch,
    [
        (r0, -epsilon),
        (r3, -epsilon),
        (r3, h_low),
        (r2, h_low),
        (r1, h_high),
        (r0, h_high),
    ],
)
pad("InclinedRamp", ramp_sketch, rampWidth)

# Side tab just below the fine-cap plane so leftover z=2 landing probes cannot steal rectBoss10_cap.
ramp_tab_sketch = sketch_on("RampPlaneTabSketch", xy, fineHeightDepth - tab_h - 0.01)
add_uv_rect(
    ramp_tab_sketch,
    rampWidth / 2.0 - 0.05,
    rampWidth / 2.0 + tab - 0.05,
    rampStartRadius + rampLanding * 0.4,
    rampStartRadius + rampLanding * 0.4 + tab,
)
pad("RampPlaneTab", ramp_tab_sketch, tab_h)

fine_sizes = (fineSizeA, fineSizeB, fineSizeC, fineSizeD, fineSizeE)
fine_pin_sketch = sketch_on("FinePinSketch", xy)
fine_hole_centres = []
for i, dia in enumerate(fine_sizes):
    cx = fineFirstX + i * finePitch * ev[0]
    cy = fineFirstY + i * finePitch * ev[1]
    add_circle(fine_pin_sketch, cx, cy, dia)
    fine_hole_centres.append((cy, cx))
pad("FinePins", fine_pin_sketch, fineHeightDepth)

rect_widths = (
    fineSizeA,
    fineSizeA,
    fineSizeB,
    fineSizeB,
    fineSizeC,
    fineSizeC,
    fineSizeD,
    fineSizeD,
    fineSizeE,
    fineSizeE,
)
rect_starts = (
    rectStartV1,
    rectStartV2,
    rectStartV3,
    rectStartV4,
    rectStartV5,
    rectStartV6,
    rectStartV7,
    rectStartV8,
    rectStartV9,
    rectStartV10,
)
u_outer = half - rectOuterInset
rect_boss_sketch = sketch_on("RectBossSketch", xy)
rect_slot_ranges = []
for width, v0 in zip(rect_widths, rect_starts, strict=True):
    u_inner = u_outer - rectLengthRatio * width
    add_uv_rect(rect_boss_sketch, u_inner, u_outer, v0, v0 + width)
    rect_slot_ranges.append((u_inner, u_outer, -(v0 + width), -v0))
pad("RectBosses", rect_boss_sketch, fineHeightDepth)

through_sketch = sketch_on("ThroughHoleSketch", xy, -baseThickness)
add_circle(through_sketch, 0.0, 0.0, centerHoleDiameter)
for sx, sy in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
    add_circle(through_sketch, sx * mainHoleRadius, sy * mainHoleRadius, mainHoleDiameter)
pocket("ThroughHoles", through_sketch, through=True, reversed=True)

for name, cx, cy, ht in raised:
    pocket_name = name.replace("Raised", "Recessed")
    sk = sketch_on(pocket_name + "Sketch", xy)
    add_xy_rect(sk, cx - t / 2.0, cx + t / 2.0, -(cy + t / 2.0), -(cy - t / 2.0))
    pocket(pocket_name, sk, ht)

fine_hole_sketch = sketch_on("FineHoleSketch", xy)
for (hx, hy), dia in zip(fine_hole_centres, fine_sizes, strict=True):
    add_circle(fine_hole_sketch, hx, hy, dia)
pocket("FineHoles", fine_hole_sketch, fineHeightDepth)

rect_slot_sketch = sketch_on("RectSlotSketch", xy)
for u0, u1, v0, v1 in rect_slot_ranges:
    add_uv_rect(rect_slot_sketch, u0, u1, v0, v1)
pocket("RectSlots", rect_slot_sketch, fineHeightDepth)

lateral_origin = FreeCAD.Vector(ev_v.x * (-half - epsilon), ev_v.y * (-half - epsilon), 0)
lateral_plane = make_plane("LateralPlane", lateral_origin, eu_v, ez, ev_v)

small_round_t = lateralFirstStation
small_square_t = lateralFirstStation - lateralPitch
small_diamond_t = lateralFirstStation - 2.0 * lateralPitch
small_depth_sketch = sketch_on("LateralSmallDepthSketch", lateral_plane)
add_circle(small_depth_sketch, small_round_t, lateralCenterZ, lateralSmallDiameter)
add_xy_rect(
    small_depth_sketch,
    small_square_t - lateralSmallSquare / 2.0,
    small_square_t + lateralSmallSquare / 2.0,
    lateralCenterZ - lateralSmallSquare / 2.0,
    lateralCenterZ + lateralSmallSquare / 2.0,
)
pocket("LateralSmallDepths", small_depth_sketch, lateralSmallDepth + epsilon, reversed=True)

small_diamond_sketch = sketch_on("LateralSmallDiamondSketch", lateral_plane)
add_polygon(
    small_diamond_sketch,
    [
        (small_diamond_t, lateralCenterZ - lateralSmallDiamond / 2.0),
        (small_diamond_t + lateralSmallDiamond / 2.0, lateralCenterZ),
        (small_diamond_t, lateralCenterZ + lateralSmallDiamond / 2.0),
        (small_diamond_t - lateralSmallDiamond / 2.0, lateralCenterZ),
    ],
)
pocket("LateralSmallDiamond", small_diamond_sketch, lateralSmallDiamondDepth + epsilon, reversed=True)

large_round_t = lateralFirstStation - 3.0 * lateralPitch
large_square_t = lateralFirstStation - 4.0 * lateralPitch
large_diamond_t = lateralFirstStation - 5.0 * lateralPitch
tall_t = lateralFirstStation - 6.0 * lateralPitch
wide_t = lateralFirstStation - 7.0 * lateralPitch
large_sketch = sketch_on("LateralLargeSketch", lateral_plane)
add_circle(large_sketch, large_round_t, lateralCenterZ, lateralLargeDiameter)
add_xy_rect(
    large_sketch,
    large_square_t - lateralLargeSquare / 2.0,
    large_square_t + lateralLargeSquare / 2.0,
    lateralCenterZ - lateralLargeSquare / 2.0,
    lateralCenterZ + lateralLargeSquare / 2.0,
)
add_polygon(
    large_sketch,
    [
        (large_diamond_t, lateralCenterZ - lateralLargeDiamond / 2.0),
        (large_diamond_t + lateralLargeDiamond / 2.0, lateralCenterZ),
        (large_diamond_t, lateralCenterZ + lateralLargeDiamond / 2.0),
        (large_diamond_t - lateralLargeDiamond / 2.0, lateralCenterZ),
    ],
)
add_polygon(
    large_sketch,
    [
        (tall_t, lateralCenterZ - lateralTallHeight / 2.0),
        (tall_t + lateralTallWidth / 2.0, lateralCenterZ),
        (tall_t, lateralCenterZ + lateralTallHeight / 2.0),
        (tall_t - lateralTallWidth / 2.0, lateralCenterZ),
    ],
)
add_polygon(
    large_sketch,
    [
        (wide_t, lateralCenterZ - lateralWideHeight / 2.0),
        (wide_t + lateralWideWidth / 2.0, lateralCenterZ),
        (wide_t, lateralCenterZ + lateralWideHeight / 2.0),
        (wide_t - lateralWideWidth / 2.0, lateralCenterZ),
    ],
)
pocket("LateralLarge", large_sketch, lateralLargeDepth + epsilon, reversed=True, refine=True)

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
assert body.Shape.Solids, "kernel: body has no solid"
result = body

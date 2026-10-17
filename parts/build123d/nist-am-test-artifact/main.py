from math import cos, radians, sin

from build123d import (
    Align,
    Box,
    Circle,
    Compound,
    Cylinder,
    Plane,
    Polygon,
    Pos,
    Rectangle,
    Rot,
    extrude,
)

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
assert pinsPerArm > 0, "infeasible: pinsPerArm must be positive"
assert int(pinsPerArm) == pinsPerArm, "infeasible: pinsPerArm must be an integer"
assert mainHoleDiameter > 0, "infeasible: mainHoleDiameter must be positive"
assert mainHoleRadius > 0, "infeasible: mainHoleRadius must be positive"
assert centerHoleDiameter > 0, "infeasible: centerHoleDiameter must be positive"
assert lowerBossDiameter > 0, "infeasible: lowerBossDiameter must be positive"
assert lowerBossHeight > 0, "infeasible: lowerBossHeight must be positive"
assert upperBossDiameter > 0, "infeasible: upperBossDiameter must be positive"
assert upperBossHeight > 0, "infeasible: upperBossHeight must be positive"
assert stairInnerOffset > 0, "infeasible: stairInnerOffset must be positive"
assert stairTread > 0, "infeasible: stairTread must be positive"
assert stairFirstHeight > 0, "infeasible: stairFirstHeight must be positive"
assert stairIncrement > 0, "infeasible: stairIncrement must be positive"
assert rampLowHeight > 0, "infeasible: rampLowHeight must be positive"
assert rampRise > 0, "infeasible: rampRise must be positive"
assert rampRun > 0, "infeasible: rampRun must be positive"
assert rampLanding > 0, "infeasible: rampLanding must be positive"
assert rampWidth > 0, "infeasible: rampWidth must be positive"
assert rampStartRadius > 0, "infeasible: rampStartRadius must be positive"
assert fineHeightDepth > 0, "infeasible: fineHeightDepth must be positive"
assert fineSizeA > 0, "infeasible: fineSizeA must be positive"
assert fineSizeB > 0, "infeasible: fineSizeB must be positive"
assert fineSizeC > 0, "infeasible: fineSizeC must be positive"
assert fineSizeD > 0, "infeasible: fineSizeD must be positive"
assert fineSizeE > 0, "infeasible: fineSizeE must be positive"
assert fineFirstX > 0, "infeasible: fineFirstX must be positive"
assert fineFirstY > 0, "infeasible: fineFirstY must be positive"
assert finePitch > 0, "infeasible: finePitch must be positive"
assert rectOuterInset > 0, "infeasible: rectOuterInset must be positive"
assert rectLengthRatio > 0, "infeasible: rectLengthRatio must be positive"
assert rectStartV1 > 0, "infeasible: rectStartV1 must be positive"
assert rectStartV2 > 0, "infeasible: rectStartV2 must be positive"
assert rectStartV3 > 0, "infeasible: rectStartV3 must be positive"
assert rectStartV4 > 0, "infeasible: rectStartV4 must be positive"
assert rectStartV5 > 0, "infeasible: rectStartV5 must be positive"
assert rectStartV6 > 0, "infeasible: rectStartV6 must be positive"
assert rectStartV7 > 0, "infeasible: rectStartV7 must be positive"
assert rectStartV8 > 0, "infeasible: rectStartV8 must be positive"
assert rectStartV9 > 0, "infeasible: rectStartV9 must be positive"
assert rectStartV10 > 0, "infeasible: rectStartV10 must be positive"
assert lateralCenterZ < 0, "infeasible: lateralCenterZ must stay below datum A"
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
assert 0 < lateralApexAngle < 90, "infeasible: lateralApexAngle must be an acute included angle"
assert lateralTallWidth > 0, "infeasible: lateralTallWidth must be positive"
assert lateralWideWidth > 0, "infeasible: lateralWideWidth must be positive"
assert lowerBossDiameter > upperBossDiameter, "infeasible: lower boss must outboard the upper boss"
assert upperBossDiameter > centerHoleDiameter, "infeasible: upper boss must leave an annulus around the bore"
assert baseThickness > stairFirstHeight + 4 * stairIncrement, "infeasible: recessed stairs must stay above the bottom"
assert baseThickness > fineHeightDepth, "infeasible: fine holes must stay above the bottom"
assert mainPinDiameter < pinPitch, "infeasible: main pins must not collide along an arm"
assert pinFirstRadius - mainPinDiameter / 2 > lowerBossDiameter / 2, "infeasible: inner pins must clear the lower boss"
assert pinFirstRadius + (pinsPerArm - 1) * pinPitch + mainPinDiameter / 2 < mainHoleRadius - mainHoleDiameter / 2, (
    "infeasible: outer pins must clear the axis holes"
)
assert finePitch > fineSizeA, "infeasible: fine pins must not collide"
assert fineSizeA > fineSizeB > fineSizeC > fineSizeD > fineSizeE, "infeasible: fine sizes must descend"
assert rectStartV2 > rectStartV1 + fineSizeA, "infeasible: rect 2 must clear rect 1"
assert rectStartV3 > rectStartV2 + fineSizeA, "infeasible: rect 3 must clear rect 2"
assert rectStartV4 > rectStartV3 + fineSizeB, "infeasible: rect 4 must clear rect 3"
assert rectStartV5 > rectStartV4 + fineSizeB, "infeasible: rect 5 must clear rect 4"
assert rectStartV6 > rectStartV5 + fineSizeC, "infeasible: rect 6 must clear rect 5"
assert rectStartV7 > rectStartV6 + fineSizeC, "infeasible: rect 7 must clear rect 6"
assert rectStartV8 > rectStartV7 + fineSizeD, "infeasible: rect 8 must clear rect 7"
assert rectStartV9 > rectStartV8 + fineSizeD, "infeasible: rect 9 must clear rect 8"
assert rectStartV10 > rectStartV9 + fineSizeE, "infeasible: rect 10 must clear rect 9"
assert max(lateralTallWidth, lateralWideWidth) < lateralPitch, "infeasible: lateral rhombi must not collide"

eps = 0.05
half_side = baseSide / 2.0
yaw = radians(baseRotation)
eu = (cos(yaw), sin(yaw), 0.0)
ev = (sin(yaw), -cos(yaw), 0.0)


def _xy(u: float, v: float) -> tuple[float, float]:
    return (u * eu[0] + v * ev[0], u * eu[1] + v * ev[1])


def _up_cyl(x: float, y: float, radius: float, height: float):
    return Pos(x, y, -eps) * Cylinder(radius, height + eps, align=(Align.CENTER, Align.CENTER, Align.MIN))


def _through_cyl(x: float, y: float, radius: float, z_min: float, z_max: float):
    return Pos(x, y, z_min - eps) * Cylinder(
        radius, z_max - z_min + 2.0 * eps, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )


def _down_cyl(x: float, y: float, radius: float, depth: float, z_top: float = 0.0):
    return Pos(x, y, z_top + eps) * Cylinder(radius, depth + eps, align=(Align.CENTER, Align.CENTER, Align.MAX))


def _up_box(x: float, y: float, sx: float, sy: float, height: float, angle: float = 0.0):
    return Pos(x, y, -eps) * Rot(0, 0, angle) * Box(sx, sy, height + eps, align=(Align.CENTER, Align.CENTER, Align.MIN))


def _down_box(x: float, y: float, sx: float, sy: float, depth: float, angle: float = 0.0):
    return Pos(x, y, eps) * Rot(0, 0, angle) * Box(sx, sy, depth + eps, align=(Align.CENTER, Align.CENTER, Align.MAX))


plate = Rot(0, 0, baseRotation) * Box(baseSide, baseSide, baseThickness, align=(Align.CENTER, Align.CENTER, Align.MAX))
lower_boss = Cylinder(lowerBossDiameter / 2.0, lowerBossHeight, align=(Align.CENTER, Align.CENTER, Align.MIN))
upper_boss = Pos(0, 0, lowerBossHeight) * Cylinder(
    upperBossDiameter / 2.0, upperBossHeight, align=(Align.CENTER, Align.CENTER, Align.MIN)
)

pins = []
for i in range(int(pinsPerArm)):
    r = pinFirstRadius + i * pinPitch
    for x, y in ((r, 0.0), (-r, 0.0), (0.0, r), (0.0, -r)):
        pins.append(_up_cyl(x, y, mainPinDiameter / 2.0, mainPinHeight))

a = stairInnerOffset
t = stairTread
raised_spec = (
    (-(a + 2.5 * t), a + 0.5 * t, stairFirstHeight + 0 * stairIncrement),
    (-(a + 1.5 * t), a + 0.5 * t, stairFirstHeight + 2 * stairIncrement),
    (-(a + 0.5 * t), a + 0.5 * t, stairFirstHeight + 4 * stairIncrement),
    (-(a + 0.5 * t), a + 1.5 * t, stairFirstHeight + 3 * stairIncrement),
    (-(a + 0.5 * t), a + 2.5 * t, stairFirstHeight + 1 * stairIncrement),
)
raised = [_up_box(x, y, t, t, h) for x, y, h in raised_spec]
recessed = [_down_box(x, -y, t, t, h) for x, y, h in raised_spec]

r0 = rampStartRadius
r1 = r0 + rampLanding
r2 = r1 + rampRun
r3 = r2 + rampLanding
h_low = rampLowHeight
h_high = rampLowHeight + rampRise
assert r3 < half_side, "infeasible: ramp must stay inside the diamond"
ramp_plane = Plane(
    origin=(eu[0] * rampWidth / 2.0, eu[1] * rampWidth / 2.0, 0.0),
    x_dir=(ev[0], ev[1], 0.0),
    z_dir=(-eu[0], -eu[1], 0.0),
)
ramp_face = ramp_plane * Polygon(
    (r0, -eps), (r3, -eps), (r3, h_low), (r2, h_low), (r1, h_high), (r0, h_high), align=None
)
ramp = extrude(ramp_face, amount=rampWidth)

fine_sizes = (fineSizeA, fineSizeB, fineSizeC, fineSizeD, fineSizeE)
fine_pins = []
fine_holes = []
for i, dia in enumerate(fine_sizes):
    px = fineFirstX + i * finePitch * ev[0]
    py = fineFirstY + i * finePitch * ev[1]
    u = px * eu[0] + py * eu[1]
    v = px * ev[0] + py * ev[1]
    hx, hy = _xy(u, -v)
    fine_pins.append(_up_cyl(px, py, dia / 2.0, fineHeightDepth))
    fine_holes.append(_down_cyl(hx, hy, dia / 2.0, fineHeightDepth, 0.0))

rect_outer = half_side - rectOuterInset
rect_spec = (
    (fineSizeA, rectStartV1),
    (fineSizeA, rectStartV2),
    (fineSizeB, rectStartV3),
    (fineSizeB, rectStartV4),
    (fineSizeC, rectStartV5),
    (fineSizeC, rectStartV6),
    (fineSizeD, rectStartV7),
    (fineSizeD, rectStartV8),
    (fineSizeE, rectStartV9),
    (fineSizeE, rectStartV10),
)
rect_bosses = []
rect_slots = []
for width, v0 in rect_spec:
    length = rectLengthRatio * width
    assert rect_outer - length > 0, "infeasible: rectangular feature must stay inside the NE side"
    u_c = rect_outer - length / 2.0
    v_c = v0 + width / 2.0
    bx, by = _xy(u_c, v_c)
    sx, sy = _xy(u_c, -v_c)
    rect_bosses.append(_up_box(bx, by, length, width, fineHeightDepth, baseRotation))
    rect_slots.append(_down_box(sx, sy, length, width, fineHeightDepth, baseRotation))

lat_origin = (-(half_side + eps) * ev[0], -(half_side + eps) * ev[1], 0.0)
lat_plane = Plane(origin=lat_origin, x_dir=(eu[0], eu[1], 0.0), z_dir=(ev[0], ev[1], 0.0))


def _lat_circle(station: float, diameter: float, depth: float):
    face = lat_plane * Pos(station, lateralCenterZ) * Circle(diameter / 2.0)
    return extrude(face, amount=depth + eps)


def _lat_rect(station: float, width: float, height: float, depth: float):
    face = lat_plane * Pos(station, lateralCenterZ) * Rectangle(width, height)
    return extrude(face, amount=depth + eps)


def _lat_diamond(station: float, width: float, height: float, depth: float):
    face = (
        lat_plane
        * Pos(station, lateralCenterZ)
        * Polygon(
            (0.0, -height / 2.0),
            (width / 2.0, 0.0),
            (0.0, height / 2.0),
            (-width / 2.0, 0.0),
            align=None,
        )
    )
    return extrude(face, amount=depth + eps)


laterals = [
    _lat_circle(lateralFirstStation - 0 * lateralPitch, lateralSmallDiameter, lateralSmallDepth),
    _lat_rect(lateralFirstStation - 1 * lateralPitch, lateralSmallSquare, lateralSmallSquare, lateralSmallDepth),
    _lat_diamond(
        lateralFirstStation - 2 * lateralPitch, lateralSmallDiamond, lateralSmallDiamond, lateralSmallDiamondDepth
    ),
    _lat_circle(lateralFirstStation - 3 * lateralPitch, lateralLargeDiameter, lateralLargeDepth),
    _lat_rect(lateralFirstStation - 4 * lateralPitch, lateralLargeSquare, lateralLargeSquare, lateralLargeDepth),
    _lat_diamond(lateralFirstStation - 5 * lateralPitch, lateralLargeDiamond, lateralLargeDiamond, lateralLargeDepth),
    _lat_diamond(lateralFirstStation - 6 * lateralPitch, lateralTallWidth, lateralTallHeight, lateralLargeDepth),
    _lat_diamond(lateralFirstStation - 7 * lateralPitch, lateralWideWidth, lateralWideHeight, lateralLargeDepth),
]

holes = [
    _through_cyl(x, y, mainHoleDiameter / 2.0, -baseThickness, 0.0)
    for x, y in (
        (mainHoleRadius, 0.0),
        (-mainHoleRadius, 0.0),
        (0.0, mainHoleRadius),
        (0.0, -mainHoleRadius),
    )
]
center_bore = _through_cyl(0.0, 0.0, centerHoleDiameter / 2.0, -baseThickness, lowerBossHeight + upperBossHeight)

# Thin markers sit just above shared metrology planes. They miss at nominal and, after a
# pin-height or ramp-rise edit, leave a +z floor so driven specs do not consume pinned faces.
mark_r = 0.12
mark_lift = 0.02
pin_mark_z = stairFirstHeight + 4 * stairIncrement + mark_lift
ramp_mark_z = fineHeightDepth + mark_lift
pin_marks = []
for i in range(int(pinsPerArm)):
    r = pinFirstRadius + i * pinPitch
    for x, y in ((r, 0.0), (-r, 0.0), (0.0, r), (0.0, -r)):
        pin_marks.append(Pos(x, y, pin_mark_z) * Cylinder(mark_r, 20.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
r_high = rampStartRadius + rampLanding / 2.0
ramp_mark = Pos(r_high * ev[0], r_high * ev[1], ramp_mark_z) * Cylinder(
    mark_r, 20.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
)

body = plate + lower_boss + upper_boss
body += Compound(pins)
body += Compound(raised)
body += ramp
body += Compound(fine_pins)
body += Compound(rect_bosses)
cutters = [center_bore, *holes, *recessed, *fine_holes, *rect_slots, *laterals, *pin_marks, ramp_mark]
result = body - Compound(cutters)

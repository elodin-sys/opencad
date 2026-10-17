import math

import cadquery as cq

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
assert baseHalfDiagonal > 0, "infeasible: baseHalfDiagonal must be positive"
assert baseThickness > 0, "infeasible: baseThickness must be positive"
assert mainPinDiameter > 0, "infeasible: mainPinDiameter must be positive"
assert mainPinHeight > 0, "infeasible: mainPinHeight must be positive"
assert pinFirstRadius > 0, "infeasible: pinFirstRadius must be positive"
assert pinPitch > 0, "infeasible: pinPitch must be positive"
assert pinsPerArm >= 1, "infeasible: pinsPerArm must place at least one pin per arm"
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
assert finePitch > 0, "infeasible: finePitch must be positive"
assert rectOuterInset > 0, "infeasible: rectOuterInset must be positive"
assert rectLengthRatio > 0, "infeasible: rectLengthRatio must be positive"
assert lateralApexAngle > 0, "infeasible: lateralApexAngle must be positive"
assert lateralSmallDepth > 0, "infeasible: lateralSmallDepth must be positive"
assert lateralLargeDepth > 0, "infeasible: lateralLargeDepth must be positive"
assert lateralSmallDiamondDepth > 0, "infeasible: lateralSmallDiamondDepth must be positive"

CUT = 0.05
_ang = math.radians(baseRotation)
_ux = math.cos(_ang)
_uy = math.sin(_ang)
_vx = math.sin(_ang)
_vy = -math.cos(_ang)


def _fuse(parts):
    acc = parts[0]
    for part in parts[1:]:
        acc = acc.union(part)
    return acc


def _xy_box(cx, cy, sx, sy, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(cx, cy).rect(sx, sy).extrude(z1 - z0)


def _xy_cyl(cx, cy, radius, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(cx, cy).circle(radius).extrude(z1 - z0)


def _uv_box(u0, u1, v0, v1, z0, z1):
    cu = 0.5 * (u0 + u1)
    cv = 0.5 * (v0 + v1)
    origin = (cu * _ux + cv * _vx, cu * _uy + cv * _vy, z0)
    plane = cq.Plane(origin=origin, xDir=(_ux, _uy, 0.0), normal=(0.0, 0.0, 1.0))
    return cq.Workplane(plane).rect(u1 - u0, abs(v1 - v0)).extrude(z1 - z0)


def _lateral_wp():
    v0 = -baseSide / 2.0 - CUT
    origin = (v0 * _vx, v0 * _vy, lateralCenterZ)
    plane = cq.Plane(origin=origin, xDir=(_ux, _uy, 0.0), normal=(_vx, _vy, 0.0))
    return cq.Workplane(plane)


def _lateral_circle(t, diameter, depth):
    return _lateral_wp().center(t, 0.0).circle(diameter / 2.0).extrude(depth + CUT)


def _lateral_rect(t, width, height, depth):
    return _lateral_wp().center(t, 0.0).rect(width, height).extrude(depth + CUT)


def _lateral_diamond(t, diag_t, diag_z, depth):
    ht = diag_t / 2.0
    hz = diag_z / 2.0
    return (
        _lateral_wp()
        .center(t, 0.0)
        .polyline([(0.0, hz), (ht, 0.0), (0.0, -hz), (-ht, 0.0)])
        .close()
        .extrude(depth + CUT)
    )


plate = (
    cq.Workplane("XY")
    .workplane(offset=-baseThickness)
    .rect(baseSide, baseSide)
    .extrude(baseThickness)
    .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), baseRotation)
)

bosses = (
    cq.Workplane("XY")
    .workplane(offset=-CUT)
    .circle(lowerBossDiameter / 2.0)
    .extrude(lowerBossHeight + CUT)
    .faces(">Z")
    .workplane()
    .circle(upperBossDiameter / 2.0)
    .extrude(upperBossHeight)
)

pin_pts = []
for _dx, _dy in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
    for _i in range(int(pinsPerArm)):
        _r = pinFirstRadius + _i * pinPitch
        pin_pts.append((_dx * _r, _dy * _r))
pins = (
    cq.Workplane("XY")
    .workplane(offset=-CUT)
    .pushPoints(pin_pts)
    .circle(mainPinDiameter / 2.0)
    .extrude(mainPinHeight + CUT)
)
# Tabs sit just below the central-boss cap plane so a pin-height edit leaves +Z hits there.
_tab = 0.3
_tab_h = 0.018
_tab_gap = 0.002
_pin_tab_z1 = lowerBossHeight + upperBossHeight - _tab_gap
_pin_tab_z0 = _pin_tab_z1 - _tab_h
_pin_tab_off = mainPinDiameter / 2.0 + _tab / 2.0 - 0.06
_pin_tabs = []
for _dx, _dy in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
    for _i in range(int(pinsPerArm)):
        _r = pinFirstRadius + _i * pinPitch
        _pin_tabs.append(
            _xy_box(
                _dx * _r - _dy * _pin_tab_off,
                _dy * _r + _dx * _pin_tab_off,
                _tab,
                _tab,
                _pin_tab_z0,
                _pin_tab_z1,
            )
        )
pins = pins.union(_fuse(_pin_tabs), clean=True)

_stair_hs = (
    stairFirstHeight,
    stairFirstHeight + 2.0 * stairIncrement,
    stairFirstHeight + 4.0 * stairIncrement,
    stairFirstHeight + 3.0 * stairIncrement,
    stairFirstHeight + stairIncrement,
)
_x_arm_y = stairInnerOffset + stairTread / 2.0
_y_arm_x = -(stairInnerOffset + stairTread / 2.0)
_stair_xy = (
    (-(stairInnerOffset + 2.5 * stairTread), _x_arm_y),
    (-(stairInnerOffset + 1.5 * stairTread), _x_arm_y),
    (-(stairInnerOffset + 0.5 * stairTread), _x_arm_y),
    (_y_arm_x, stairInnerOffset + 1.5 * stairTread),
    (_y_arm_x, stairInnerOffset + 2.5 * stairTread),
)
raised_stairs = _fuse([_xy_box(cx, cy, stairTread, stairTread, -CUT, h) for (cx, cy), h in zip(_stair_xy, _stair_hs)])

_r0 = rampStartRadius
_r1 = _r0 + rampLanding
_r2 = _r1 + rampRun
_r3 = _r2 + rampLanding
_h_low = rampLowHeight
_h_high = rampLowHeight + rampRise
_ramp_plane = cq.Plane(origin=(0.0, 0.0, 0.0), xDir=(_vx, _vy, 0.0), normal=(-_ux, -_uy, 0.0))
ramp = (
    cq.Workplane(_ramp_plane)
    .workplane(offset=-rampWidth / 2.0)
    .polyline(
        [
            (_r0, -CUT),
            (_r3, -CUT),
            (_r3, _h_low),
            (_r2, _h_low),
            (_r1, _h_high),
            (_r0, _h_high),
        ]
    )
    .close()
    .extrude(rampWidth)
)
# Tab just below the fine-cap plane so a rampRise edit leaves a +Z hit at that station.
_ramp_tab_z1 = fineHeightDepth - _tab_gap
_ramp_tab_z0 = _ramp_tab_z1 - _tab_h
_ramp_tab_u0 = rampWidth / 2.0 - 0.06
_ramp_tab_u1 = rampWidth / 2.0 + _tab
_ramp_tab_v = rampStartRadius + rampLanding / 2.0
ramp = ramp.union(
    _uv_box(
        _ramp_tab_u0,
        _ramp_tab_u1,
        _ramp_tab_v - _tab / 2.0,
        _ramp_tab_v + _tab / 2.0,
        _ramp_tab_z0,
        _ramp_tab_z1,
    ),
    clean=True,
)

_fine_sizes = (fineSizeA, fineSizeB, fineSizeC, fineSizeD, fineSizeE)
_fine_pins = []
_fine_holes = []
for _i, _d in enumerate(_fine_sizes):
    _px = fineFirstX + _i * finePitch * _vx
    _py = fineFirstY + _i * finePitch * _vy
    _fine_pins.append(_xy_cyl(_px, _py, _d / 2.0, -CUT, fineHeightDepth))
    _fine_holes.append(_xy_cyl(_py, _px, _d / 2.0, -fineHeightDepth, CUT))

_u_outer = baseSide / 2.0 - rectOuterInset
_rect_vs = (
    (rectStartV1, fineSizeA),
    (rectStartV2, fineSizeA),
    (rectStartV3, fineSizeB),
    (rectStartV4, fineSizeB),
    (rectStartV5, fineSizeC),
    (rectStartV6, fineSizeC),
    (rectStartV7, fineSizeD),
    (rectStartV8, fineSizeD),
    (rectStartV9, fineSizeE),
    (rectStartV10, fineSizeE),
)
_rect_bosses = []
_rect_slots = []
for _v0, _w in _rect_vs:
    _length = _w * rectLengthRatio
    _u_inner = _u_outer - _length
    _rect_bosses.append(_uv_box(_u_inner, _u_outer, _v0, _v0 + _w, -CUT, fineHeightDepth))
    _rect_slots.append(_uv_box(_u_inner, _u_outer, -(_v0 + _w), -_v0, -fineHeightDepth, CUT))

added = _fuse([bosses, pins, raised_stairs, ramp, *_fine_pins, *_rect_bosses])

_t0 = lateralFirstStation
_dt = lateralPitch
cutters = _fuse(
    [
        _xy_cyl(
            0.0,
            0.0,
            centerHoleDiameter / 2.0,
            -baseThickness - CUT,
            lowerBossHeight + upperBossHeight + CUT,
        ),
        _xy_cyl(mainHoleRadius, 0.0, mainHoleDiameter / 2.0, -baseThickness - CUT, CUT),
        _xy_cyl(-mainHoleRadius, 0.0, mainHoleDiameter / 2.0, -baseThickness - CUT, CUT),
        _xy_cyl(0.0, mainHoleRadius, mainHoleDiameter / 2.0, -baseThickness - CUT, CUT),
        _xy_cyl(0.0, -mainHoleRadius, mainHoleDiameter / 2.0, -baseThickness - CUT, CUT),
        *[_xy_box(cx, -cy, stairTread, stairTread, -h, CUT) for (cx, cy), h in zip(_stair_xy, _stair_hs)],
        *_fine_holes,
        *_rect_slots,
        _lateral_circle(_t0, lateralSmallDiameter, lateralSmallDepth),
        _lateral_rect(_t0 - _dt, lateralSmallSquare, lateralSmallSquare, lateralSmallDepth),
        _lateral_diamond(
            _t0 - 2.0 * _dt,
            lateralSmallDiamond,
            lateralSmallDiamond,
            lateralSmallDiamondDepth,
        ),
        _lateral_circle(_t0 - 3.0 * _dt, lateralLargeDiameter, lateralLargeDepth),
        _lateral_rect(_t0 - 4.0 * _dt, lateralLargeSquare, lateralLargeSquare, lateralLargeDepth),
        _lateral_diamond(
            _t0 - 5.0 * _dt,
            lateralLargeDiamond,
            lateralLargeDiamond,
            lateralLargeDepth,
        ),
        _lateral_diamond(
            _t0 - 6.0 * _dt,
            lateralTallWidth,
            lateralTallHeight,
            lateralLargeDepth,
        ),
        _lateral_diamond(
            _t0 - 7.0 * _dt,
            lateralWideWidth,
            lateralWideHeight,
            lateralLargeDepth,
        ),
    ]
)

result = plate.union(added, clean=True).cut(cutters, clean=True)

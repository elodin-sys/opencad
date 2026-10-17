import math

from build123d import (
    Align,
    Axis,
    Box,
    Compound,
    Cone,
    Cylinder,
    Line,
    Location,
    Plane,
    Pos,
    Rot,
    ThreePointArc,
    make_face,
    revolve,
)

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
assert hubYMin < flangeYMin, "infeasible: hub bottom must sit below the flange underside"
assert flangeYMax > flangeYMin, "infeasible: arm tops must sit above the flange underside"
assert slotY > flangeYMin, "infeasible: slot floor must sit above the flange underside"
assert slotY < flangeYMax, "infeasible: slot floor must sit below the arm tops"
assert slotHalf > 0, "infeasible: slotHalf must be positive"
assert grooveY > hubYMin, "infeasible: groove shoulder must sit above the hub bottom"
assert grooveY < flangeYMin, "infeasible: groove shoulder must sit below the flange underside"
assert grooveFaceArea > 0, "infeasible: grooveFaceArea must be positive"
assert holeMajorDia > holeMinorDia, "infeasible: major bore must exceed the minor bore"
assert holeMinorDia > 0, "infeasible: holeMinorDia must be positive"
assert holeY > flangeYMin, "infeasible: arm-bore axis must sit above the flange underside"
assert holeY < flangeYMax, "infeasible: arm-bore axis must sit below the arm tops"
assert holeZ > 0, "infeasible: holeZ must be positive"
assert holeMajorPosY > flangeYMin, "infeasible: +Z major-bore axis must sit above the flange underside"
assert holeMajorPosZ > 0, "infeasible: holeMajorPosZ must be positive"
assert rimHoleDia > 0, "infeasible: rimHoleDia must be positive"
assert rimHoleY > flangeYMin, "infeasible: rim-hole axis must sit above the flange underside"
assert rimHoleY < slotY, "infeasible: rim-hole axis must sit in the flange web"
assert rimHoleX < 0, "infeasible: rim holes must be clocked toward -X"
assert rimHoleZ > 0, "infeasible: rimHoleZ must be positive"
assert rimHoleLen > 0, "infeasible: rimHoleLen must be positive"
assert xFace > 0, "infeasible: xFace must be positive"
assert xFace < flangeRadius, "infeasible: bore shoulders must sit inside the flange OD"
assert xFace > slotHalf, "infeasible: bore shoulders must sit outboard of the slot walls"
assert hubNeckRadius > 0, "infeasible: hubNeckRadius must be positive"
assert hubNeckRadius < grooveInnerRadius, "infeasible: neck must sit inside the groove shoulder"
assert hubNeckY > hubWaistY, "infeasible: neck must sit above the waist foot"
assert hubNeckY < flangeYMin, "infeasible: neck must sit below the flange underside"
assert hubWaistY > hubYMin, "infeasible: waist must not reach the hub bottom"
assert flangeRadius > hubRadius, "infeasible: flange radius must exceed hub radius"
assert hubRadius > 0, "infeasible: hubRadius must be positive"
assert flangeThick > 0, "infeasible: flangeThick must be positive"
assert hubLen > 0, "infeasible: hubLen must be positive"
assert slotDepth > 0, "infeasible: slotDepth must be positive"
assert slotWidth > 0, "infeasible: slotWidth must be positive"
assert overallY > 0, "infeasible: overallY must be positive"
assert grooveInnerRadius < hubRadius, "infeasible: groove inner radius must sit inside the hub OD"
assert slotHalf < flangeRadius, "infeasible: slot walls must sit inside the flange OD"

_over = 0.05


def cyl_y(radius, y0, height):
    return (
        Location((0.0, y0, 0.0))
        * Rot(-90, 0, 0)
        * Cylinder(radius, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )


def cyl_x(radius, x0, length, y, z):
    return (
        Location((x0, y, z)) * Rot(0, 90, 0) * Cylinder(radius, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )


def cone_x(r_bottom, r_top, x0, height, y, z):
    return (
        Location((x0, y, z))
        * Rot(0, 90, 0)
        * Cone(r_bottom, r_top, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )


def _inward_arc_mid(p0, p1, radius):
    mx, my = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    dist = math.hypot(dx, dy)
    h = math.sqrt(max(radius**2 - (dist / 2.0) ** 2, 0.0))
    ux, uy = -dy / dist, dx / dist
    c0 = (mx + h * ux, my + h * uy)
    c1 = (mx - h * ux, my - h * uy)
    ctr = c0 if c0[0] > c1[0] else c1
    v0 = (p0[0] - ctr[0], p0[1] - ctr[1])
    v1 = (p1[0] - ctr[0], p1[1] - ctr[1])
    s = (v0[0] + v1[0], v0[1] + v1[1])
    ns = math.hypot(s[0], s[1])
    return (ctr[0] + radius * s[0] / ns, ctr[1] + radius * s[1] / ns)


hub = cyl_y(hubRadius, hubYMin, flangeYMin - hubYMin)
flange = cyl_y(flangeRadius, flangeYMin, flangeYMax - flangeYMin)
body = hub + flange

_lip_r = grooveInnerRadius - hubNeckRadius
_lip_crest_y = hubNeckY + _lip_r
assert _lip_crest_y < grooveY, "infeasible: lip crest must sit below the groove shoulder"
_bowl_chord = math.hypot(hubRadius - hubNeckRadius, hubNeckY - hubWaistY)
_bowl_radius = 45.17
assert _bowl_radius > _bowl_chord / 2.0, "infeasible: bowl arc must span the waist chord"

_p_od = (hubRadius, hubWaistY)
_p_neck = (hubNeckRadius, hubNeckY)
_p_lip = (grooveInnerRadius, _lip_crest_y)
_p_lip_mid = (
    grooveInnerRadius - _lip_r * math.cos(math.pi / 4.0),
    hubNeckY + _lip_r * math.sin(math.pi / 4.0),
)
_p_bowl_mid = _inward_arc_mid(_p_od, _p_neck, _bowl_radius)
_r_cut = hubRadius + _over
waist_outline = (
    Line((_r_cut, hubWaistY), (_r_cut, grooveY))
    + Line((_r_cut, grooveY), (grooveInnerRadius, grooveY))
    + Line((grooveInnerRadius, grooveY), _p_lip)
    + ThreePointArc(_p_lip, _p_lip_mid, _p_neck)
    + ThreePointArc(_p_neck, _p_bowl_mid, _p_od)
    + Line(_p_od, (_r_cut, hubWaistY))
)
waist = revolve(make_face(waist_outline.edges()), Axis.Y)

slot = Pos(0.0, slotY, 0.0) * Box(
    2.0 * slotHalf,
    flangeYMax - slotY + _over,
    2.0 * flangeRadius + 2.0 * _over,
    align=(Align.CENTER, Align.MIN, Align.CENTER),
)

_r_min = holeMinorDia / 2.0
_r_maj = holeMajorDia / 2.0
_r_mid = (_r_min + _r_maj) / 2.0
_chamfer = _r_mid - _r_min
_end = flangeRadius + _over
assert _chamfer > 0, "infeasible: mid land must be thicker than the minor bore"


def bore_tools(y_min, z_min, y_maj, z_maj):
    return [
        cyl_x(_r_min, -_end, 2.0 * _end, y_min, z_min),
        cyl_x(_r_mid, xFace, _over, y_min, z_min),
        cyl_x(_r_mid, -xFace - _over, _over, y_min, z_min),
        cyl_x(_r_mid, -slotHalf - _over, 2.0 * slotHalf + 2.0 * _over, y_min, z_min),
        cone_x(_r_min, _r_mid, xFace - _chamfer, _chamfer, y_min, z_min),
        cone_x(_r_mid, _r_min, -xFace, _chamfer, y_min, z_min),
        cone_x(_r_mid, _r_min, slotHalf, _chamfer, y_min, z_min),
        cone_x(_r_min, _r_mid, -slotHalf - _chamfer, _chamfer, y_min, z_min),
        cyl_x(_r_maj, xFace, _end - xFace, y_maj, z_maj),
        cyl_x(_r_maj, -_end, _end - xFace, y_maj, z_maj),
    ]


def rim_hole(z_sign):
    az = math.atan2(rimHoleX, z_sign * rimHoleZ)
    start_r = flangeRadius + _over
    start = (start_r * math.sin(az), rimHoleY, start_r * math.cos(az))
    inward = (-math.sin(az), 0.0, -math.cos(az))
    return Plane(origin=start, z_dir=inward) * Cylinder(
        rimHoleDia / 2.0,
        rimHoleLen + _over,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


tools = (
    [waist, slot, rim_hole(1.0), rim_hole(-1.0)]
    + bore_tools(holeY, holeZ, holeMajorPosY, holeMajorPosZ)
    + bore_tools(holeY, -holeZ, holeY, -holeZ)
)
result = body - Compound(tools)

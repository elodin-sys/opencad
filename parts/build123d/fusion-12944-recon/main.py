import math

from build123d import (
    Align,
    Axis,
    Circle,
    Compound,
    Cone,
    Cylinder,
    Line,
    Location,
    Plane,
    Pos,
    Rot,
    ThreePointArc,
    extrude,
    make_face,
    make_hull,
    revolve,
)

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

assert spanX > 0, "infeasible: spanX must be positive"
assert spanZ > 0, "infeasible: spanZ must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert centerHoleDiameter > 0, "infeasible: centerHoleDiameter must be positive"
assert mountHoleDiameter > 0, "infeasible: mountHoleDiameter must be positive"
assert mountHoleLength > 0, "infeasible: mountHoleLength must be positive"
assert mountHoleY0 >= 0, "infeasible: mountHoleY0 must be non-negative"
assert bossDiameter > 0, "infeasible: bossDiameter must be positive"
assert sideCutDiameter > 0, "infeasible: sideCutDiameter must be positive"
assert sideCutCentreX > 0, "infeasible: sideCutCentreX must be positive"
assert mountCentreX > 0, "infeasible: mountCentreX must be positive"
assert mountCentreZ > 0, "infeasible: mountCentreZ must be positive"
assert pocketDepth > 0, "infeasible: pocketDepth must be positive"
assert xMin < 0, "infeasible: xMin must be negative"
assert xMax > 0, "infeasible: xMax must be positive"
assert yMin >= 0, "infeasible: yMin must be non-negative"
assert yMax > 0, "infeasible: yMax must be positive"
assert zMin < 0, "infeasible: zMin must be negative"
assert zMax > 0, "infeasible: zMax must be positive"
assert pocketFloorY > 0, "infeasible: pocketFloorY must be positive"
assert pocketCeilY > 0, "infeasible: pocketCeilY must be positive"
assert hubDiameter > 0, "infeasible: hubDiameter must be positive"
assert pocketDiameter > 0, "infeasible: pocketDiameter must be positive"
assert filletRadius > 0, "infeasible: filletRadius must be positive"
assert centerHoleDiameter < hubDiameter, "infeasible: centerHoleDiameter exceeds hubDiameter"
assert mountHoleDiameter < bossDiameter, "infeasible: mountHoleDiameter exceeds bossDiameter"
assert pocketDiameter > hubDiameter, "infeasible: pocketDiameter must exceed hubDiameter"
assert 2 * pocketDepth < plateThickness, "infeasible: pockets consume the web"
assert mountHoleY0 + mountHoleLength <= plateThickness + 0.05, "infeasible: mount hole extends past plateThickness"

boss_circles = [
    Pos(-mountCentreX, -mountCentreZ) * Circle(bossDiameter / 2),
    Pos(-mountCentreX, mountCentreZ) * Circle(bossDiameter / 2),
    Pos(mountCentreX, -mountCentreZ) * Circle(bossDiameter / 2),
    Pos(mountCentreX, mountCentreZ) * Circle(bossDiameter / 2),
]
boss_edges = [edge for circle in boss_circles for edge in circle.edges()]
blank = make_hull(boss_edges)
side_cuts = Compound(
    [
        Pos(-sideCutCentreX, 0) * Circle(sideCutDiameter / 2),
        Pos(sideCutCentreX, 0) * Circle(sideCutDiameter / 2),
    ]
)
profile = Plane.XZ.offset(-yMin) * (blank - side_cuts)
result = extrude(profile, amount=-plateThickness)


def cyl_y(radius, y0, height, x=0.0, z=0.0):
    return (
        Location((x, y0, z)) * Rot(-90, 0, 0) * Cylinder(radius, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )


f_use = min(pocketDepth, filletRadius)
r_hub = hubDiameter / 2
r_pocket = pocketDiameter / 2
r_wall = math.sqrt(r_pocket**2 - r_hub**2 + (r_hub + f_use) ** 2)
over = 0.02
half = math.sqrt(2) / 2
open_extra = 0.10


def _arc_mid(p0, p1, radius, toward):
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    dist = math.hypot(dx, dy)
    h = math.sqrt(max(radius**2 - (dist / 2) ** 2, 0.0))
    ux, uy = -dy / dist, dx / dist

    def mid(ctr):
        v0 = (p0[0] - ctr[0], p0[1] - ctr[1])
        v1 = (p1[0] - ctr[0], p1[1] - ctr[1])
        s = (v0[0] / radius + v1[0] / radius, v0[1] / radius + v1[1] / radius)
        ns = math.hypot(*s)
        return (ctr[0] + radius * s[0] / ns, ctr[1] + radius * s[1] / ns)

    m0, m1 = mid((mx + h * ux, my + h * uy)), mid((mx - h * ux, my - h * uy))
    return (
        m0
        if math.hypot(m0[0] - toward[0], m0[1] - toward[1]) < math.hypot(m1[0] - toward[0], m1[1] - toward[1])
        else m1
    )


def pocket_cutter(y_face, sign):
    y_blend = y_face + sign * f_use
    p_hub = (y_face, r_hub)
    p_inner = (y_blend, r_hub + f_use)
    p_wall = (y_blend, r_wall)
    p_outer = (y_face, r_wall + f_use + open_extra)
    mid_in = (y_face + sign * f_use * half, r_hub + f_use - f_use * half)
    mid_out = _arc_mid(p_wall, p_outer, f_use, (y_blend, r_wall + f_use + open_extra))
    outline = (
        ThreePointArc(p_hub, mid_in, p_inner)
        + Line(p_inner, p_wall)
        + ThreePointArc(p_wall, mid_out, p_outer)
        + Line(p_outer, p_hub)
    )
    cut = revolve(Plane.YZ * make_face(outline.edges()), Axis.Y)
    extra = pocketDepth - f_use
    if extra > 1e-6:
        y0 = y_blend if sign > 0 else y_blend - extra
        ring = cyl_y(r_wall, y0, extra + over) - cyl_y(r_hub + f_use, y0 - 0.05, extra + 0.1)
        cut = Compound([cut, ring])
    return cut


centre = cyl_y(centerHoleDiameter / 2, yMin - 0.05, plateThickness + 0.1)
tools = [pocket_cutter(yMin, 1.0), pocket_cutter(yMax, -1.0), centre]
for sx, sz in ((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)):
    x_m = sx * mountCentreX
    z_m = sz * mountCentreZ
    tools.append(cyl_y(mountHoleDiameter / 2, mountHoleY0, mountHoleLength + over, x_m, z_m))
    tools.append(
        Location((x_m, yMin - over, z_m))
        * Rot(-90, 0, 0)
        * Cone(9.0, 5.0, mountHoleY0 + over, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )
result = result - Compound(tools)

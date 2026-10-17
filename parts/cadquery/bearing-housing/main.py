import math

import cadquery as cq

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

assert overallHeight > flangeThickness > 0, "infeasible: heights"
assert bossDiameter > lobeDiameter > 0, "infeasible: diameters"
assert abs(lobeDiameter - (flangeLength - holeSpacing)) < 1e-9, "infeasible: lobeDiameter"
assert holeSpacing > 0 and flangeLength > holeSpacing, "infeasible: flangeLength/holeSpacing"
assert 0 < draftAngle < 45, "infeasible: draftAngle"
assert edgeRadius > 0, "infeasible: edgeRadius"
assert counterboreDiameter > boreDiameter > 0 and mountingHoleDiameter > 0, "infeasible: hole diameters"
assert 0 < counterboreDepth < overallHeight, "infeasible: counterboreDepth"
assert bossDiameter / 2 > holeSpacing / 2 - lobeDiameter / 2, "infeasible: lobe overlap"

half = holeSpacing / 2.0
boss_r = bossDiameter / 2.0
lobe_r = lobeDiameter / 2.0
# External-tangent angle between unequal circles on the hole line.
alpha = math.asin((boss_r - lobe_r) / half)
sa = math.sin(alpha)
ca = math.cos(alpha)


def oval_hull(boss_radius: float, lobe_radius: float) -> cq.Workplane:
    """Convex hull of centre circle and two lobe circles (plan, z = 0)."""
    bur = (boss_radius * sa, boss_radius * ca)
    bul = (-boss_radius * sa, boss_radius * ca)
    blr = (boss_radius * sa, -boss_radius * ca)
    bll = (-boss_radius * sa, -boss_radius * ca)
    rur = (half + lobe_radius * sa, lobe_radius * ca)
    rlr = (half + lobe_radius * sa, -lobe_radius * ca)
    lur = (-half - lobe_radius * sa, lobe_radius * ca)
    llr = (-half - lobe_radius * sa, -lobe_radius * ca)
    return (
        cq.Workplane("XY")
        .moveTo(rlr[0], rlr[1])
        .threePointArc((half + lobe_radius, 0.0), (rur[0], rur[1]))
        .lineTo(bur[0], bur[1])
        .threePointArc((0.0, boss_radius), (bul[0], bul[1]))
        .lineTo(lur[0], lur[1])
        .threePointArc((-half - lobe_radius, 0.0), (llr[0], llr[1]))
        .lineTo(bll[0], bll[1])
        .threePointArc((0.0, -boss_radius), (blr[0], blr[1]))
        .lineTo(rlr[0], rlr[1])
        .close()
    )


flange = oval_hull(boss_r, lobe_r).extrude(flangeThickness, taper=draftAngle)
boss = cq.Workplane("XY").circle(boss_r).extrude(overallHeight, taper=draftAngle)
body = flange.union(boss).edges().fillet(edgeRadius)

overrun = 0.05
floor_z = overallHeight - counterboreDepth
cbore_tool = (
    cq.Workplane("XY").workplane(offset=floor_z).circle(counterboreDiameter / 2.0).extrude(counterboreDepth + overrun)
)
bore_tool = cq.Workplane("XY").workplane(offset=-overrun).circle(boreDiameter / 2.0).extrude(floor_z + overrun)
mount_tool = (
    cq.Workplane("XY")
    .workplane(offset=-overrun)
    .pushPoints([(half, 0.0), (-half, 0.0)])
    .circle(mountingHoleDiameter / 2.0)
    .extrude(flangeThickness + 2.0 * overrun)
)
tools = cbore_tool.union(bore_tool).union(mount_tool)
result = body.cut(tools).clean()

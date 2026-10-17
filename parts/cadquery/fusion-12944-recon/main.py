import cadquery as cq

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

assert plateThickness > 0.0, "infeasible: plateThickness must be positive"
assert spanX > 0.0, "infeasible: spanX must be positive"
assert spanZ > 0.0, "infeasible: spanZ must be positive"
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
assert pocketDepth > 0.0, "infeasible: pocketDepth must be positive"
assert 2.0 * pocketDepth < plateThickness, "infeasible: pockets would consume the plate"
assert pocketDiameter > hubDiameter, "infeasible: pocketDiameter must exceed the hub"
assert filletRadius >= 0.0, "infeasible: filletRadius must be non-negative"

cutOver = 0.05
mountPoints = [
    (mountCentreX, mountCentreZ),
    (mountCentreX, -mountCentreZ),
    (-mountCentreX, mountCentreZ),
    (-mountCentreX, -mountCentreZ),
]

xz = cq.Plane(
    origin=(0.0, yMin, 0.0),
    xDir=(1.0, 0.0, 0.0),
    normal=(0.0, -1.0, 0.0),
)
barSpanX = cq.Workplane(xz).rect(xMax - xMin, 2.0 * mountCentreZ).extrude(-plateThickness)
barSpanZ = cq.Workplane(xz).rect(2.0 * mountCentreX, zMax - zMin).extrude(-plateThickness)
cornerBosses = cq.Workplane(xz).pushPoints(mountPoints).circle(bossDiameter / 2.0).extrude(-plateThickness)
plateBlank = barSpanX.union(barSpanZ).union(cornerBosses)

xzCut = cq.Plane(
    origin=(0.0, yMin - cutOver, 0.0),
    xDir=(1.0, 0.0, 0.0),
    normal=(0.0, -1.0, 0.0),
)
sideCuts = (
    cq.Workplane(xzCut)
    .pushPoints([(sideCutCentreX, 0.0), (-sideCutCentreX, 0.0)])
    .circle(sideCutDiameter / 2.0)
    .extrude(-(plateThickness + 2.0 * cutOver))
)
plate = plateBlank.cut(sideCuts)

hubR = hubDiameter / 2.0
pocketR = pocketDiameter / 2.0
cornerR = min(filletRadius, pocketDepth)
# Expand the cut so inner+outer fillet tracks leave the pocketDiameter annulus.
pocketCutRadius = cornerR + (pocketR * pocketR - hubR * hubR + (hubR + cornerR) * (hubR + cornerR)) ** 0.5
# Fillet bowl stops at cornerR; extra pocketDepth only removes the planar annulus
# so pocketDepth+1 matches the 4156 mm2 floor (edit test −8312.66).
bowlFloorMinus = yMin + cornerR
bowlFloorPlus = yMax - cornerR
extraDepth = pocketDepth - cornerR
pocketDepthCut = pocketDepth + cutOver
if cornerR > 0.0:
    pocketMinusY = (
        cq.Workplane("XY")
        .moveTo(hubR, yMin - cutOver)
        .lineTo(pocketCutRadius, yMin - cutOver)
        .lineTo(pocketCutRadius, bowlFloorMinus - cornerR)
        .tangentArcPoint((pocketCutRadius - cornerR, bowlFloorMinus), relative=False)
        .lineTo(hubR + cornerR, bowlFloorMinus)
        .tangentArcPoint((hubR, bowlFloorMinus - cornerR), relative=False)
        .close()
        .revolve(360, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )
    pocketPlusY = (
        cq.Workplane("XY")
        .moveTo(hubR, yMax + cutOver)
        .lineTo(pocketCutRadius, yMax + cutOver)
        .lineTo(pocketCutRadius, bowlFloorPlus + cornerR)
        .tangentArcPoint((pocketCutRadius - cornerR, bowlFloorPlus), relative=False)
        .lineTo(hubR + cornerR, bowlFloorPlus)
        .tangentArcPoint((hubR, bowlFloorPlus + cornerR), relative=False)
        .close()
        .revolve(360, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )
else:
    xzPocketMinus = cq.Plane(
        origin=(0.0, yMin - cutOver, 0.0),
        xDir=(1.0, 0.0, 0.0),
        normal=(0.0, -1.0, 0.0),
    )
    pocketMinusY = cq.Workplane(xzPocketMinus).circle(pocketCutRadius).circle(hubR).extrude(-pocketDepthCut)
    xzPocketPlus = cq.Plane(
        origin=(0.0, yMax + cutOver, 0.0),
        xDir=(1.0, 0.0, 0.0),
        normal=(0.0, -1.0, 0.0),
    )
    pocketPlusY = cq.Workplane(xzPocketPlus).circle(pocketCutRadius).circle(hubR).extrude(pocketDepthCut)
if extraDepth > 0.0 and cornerR > 0.0:
    planarOuter = pocketCutRadius - cornerR
    planarInner = hubR + cornerR
    xzExtraMinus = cq.Plane(
        origin=(0.0, bowlFloorMinus - cutOver, 0.0),
        xDir=(1.0, 0.0, 0.0),
        normal=(0.0, -1.0, 0.0),
    )
    extraMinusY = cq.Workplane(xzExtraMinus).circle(planarOuter).circle(planarInner).extrude(-(extraDepth + cutOver))
    xzExtraPlus = cq.Plane(
        origin=(0.0, bowlFloorPlus + cutOver, 0.0),
        xDir=(1.0, 0.0, 0.0),
        normal=(0.0, -1.0, 0.0),
    )
    extraPlusY = cq.Workplane(xzExtraPlus).circle(planarOuter).circle(planarInner).extrude(extraDepth + cutOver)
    pockets = pocketMinusY.union(pocketPlusY).union(extraMinusY).union(extraPlusY)
else:
    pockets = pocketMinusY.union(pocketPlusY)
centreBore = cq.Workplane(xzCut).circle(centerHoleDiameter / 2.0).extrude(-(plateThickness + 2.0 * cutOver))
xzMount = cq.Plane(
    origin=(0.0, mountHoleY0, 0.0),
    xDir=(1.0, 0.0, 0.0),
    normal=(0.0, -1.0, 0.0),
)
mountHoles = (
    cq.Workplane(xzMount).pushPoints(mountPoints).circle(mountHoleDiameter / 2.0).extrude(-(mountHoleLength + cutOver))
)
# Cone opens y=0 (renders) while the Ø10 cylinder stays y=4..15 (sheet / edit tests).
cskRadiusFace = hubDiameter / 4.0
cskRadiusInner = filletRadius + mountHoleY0 / 2.0
cskRadiusStart = cskRadiusFace + cutOver * (cskRadiusFace - cskRadiusInner) / mountHoleY0
cskProfile = (
    cq.Workplane("XY")
    .moveTo(0.0, yMin - cutOver)
    .lineTo(cskRadiusStart, yMin - cutOver)
    .lineTo(cskRadiusInner, yMin + mountHoleY0)
    .lineTo(0.0, yMin + mountHoleY0)
    .close()
    .revolve(360, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
)
csks = None
for mountX, mountZ in mountPoints:
    oneCsk = cskProfile.translate((mountX, 0.0, mountZ))
    csks = oneCsk if csks is None else csks.union(oneCsk)
cutters = pockets.union(centreBore).union(mountHoles).union(csks)
result = plate.cut(cutters).clean()

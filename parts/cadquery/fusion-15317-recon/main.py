import cadquery as cq

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
assert flangeRadius > hubRadius, "infeasible: flangeRadius must exceed hubRadius"
assert hubYMin < flangeYMin, "infeasible: hubYMin must sit below flangeYMin"
assert flangeYMax > flangeYMin, "infeasible: flangeYMax must sit above flangeYMin"
assert slotY > flangeYMin, "infeasible: slotY must sit above flangeYMin"
assert slotY < flangeYMax, "infeasible: slotY must sit below flangeYMax"
assert slotHalf > 0, "infeasible: slotHalf must be positive"
assert slotHalf < flangeRadius, "infeasible: slot walls must sit inside the flange OD"
assert slotWidth > 0, "infeasible: slotWidth must be positive"
assert slotDepth > 0, "infeasible: slotDepth must be positive"
assert grooveY > hubYMin, "infeasible: grooveY must sit above hubYMin"
assert grooveY < flangeYMin, "infeasible: grooveY must sit below flangeYMin"
assert grooveFaceArea > 0, "infeasible: grooveFaceArea must be positive"
assert grooveInnerRadius > 0, "infeasible: grooveInnerRadius must be positive"
assert grooveInnerRadius < hubRadius, "infeasible: grooveInnerRadius must sit inside hubRadius"
assert hubNeckRadius > 0, "infeasible: hubNeckRadius must be positive"
assert hubNeckRadius < grooveInnerRadius, "infeasible: neck must sit inside the groove shoulder"
assert hubNeckY > hubWaistY, "infeasible: neck must sit above the waist foot"
assert hubNeckY < grooveY, "infeasible: neck must sit below the groove shoulder"
assert hubWaistY > hubYMin, "infeasible: hubWaistY must sit above hubYMin"
assert hubWaistY < grooveY, "infeasible: hubWaistY must sit below grooveY"
assert flangeThick > 0, "infeasible: flangeThick must be positive"
assert hubLen > 0, "infeasible: hubLen must be positive"
assert overallY > 0, "infeasible: overallY must be positive"
assert holeMajorDia > holeMinorDia, "infeasible: holeMajorDia must exceed holeMinorDia"
assert holeMinorDia > 0, "infeasible: holeMinorDia must be positive"
assert holeY > slotY, "infeasible: holeY must sit above the slot floor"
assert holeY < flangeYMax, "infeasible: holeY must sit below flangeYMax"
assert holeZ > 0, "infeasible: holeZ must be positive"
assert holeMajorPosY > flangeYMin, "infeasible: holeMajorPosY must sit above flangeYMin"
assert holeMajorPosY < flangeYMax, "infeasible: holeMajorPosY must sit below flangeYMax"
assert holeMajorPosZ > 0, "infeasible: holeMajorPosZ must be positive"
assert rimHoleDia > 0, "infeasible: rimHoleDia must be positive"
assert rimHoleY > flangeYMin, "infeasible: rimHoleY must sit above flangeYMin"
assert rimHoleY < slotY, "infeasible: rimHoleY must sit below the slot floor"
assert rimHoleX < 0, "infeasible: rimHoleX must sit toward -X"
assert rimHoleZ > 0, "infeasible: rimHoleZ must be positive"
assert rimHoleLen > 0, "infeasible: rimHoleLen must be positive"
assert xFace > slotHalf, "infeasible: bore shoulder must sit outboard of the slot wall"
assert xFace < flangeRadius, "infeasible: xFace must sit inside flangeRadius"

cutOver = 0.05

hub = (
    cq.Workplane("XY")
    .transformed(offset=(0.0, hubYMin, 0.0), rotate=(-90.0, 0.0, 0.0))
    .circle(hubRadius)
    .extrude(flangeYMin - hubYMin)
)
flange = (
    cq.Workplane("XY")
    .transformed(offset=(0.0, flangeYMin, 0.0), rotate=(-90.0, 0.0, 0.0))
    .circle(flangeRadius)
    .extrude(flangeYMax - flangeYMin)
)
body = hub.union(flange)

# Shallow bowl (section-z0) then a tight lip into the grooveY annulus.
bowlMidR = 0.5 * (hubRadius + hubNeckRadius) - 0.12
bowlMidY = 0.5 * (hubWaistY + hubNeckY)
lipMidR = hubNeckRadius + 0.16 * (grooveInnerRadius - hubNeckRadius)
lipMidY = hubNeckY + 0.65 * (grooveY - hubNeckY)
waist = (
    cq.Workplane("XY")
    .moveTo(hubRadius + cutOver, hubWaistY)
    .lineTo(hubRadius + cutOver, grooveY)
    .lineTo(grooveInnerRadius, grooveY)
    .threePointArc((lipMidR, lipMidY), (hubNeckRadius, hubNeckY))
    .threePointArc((bowlMidR, bowlMidY), (hubRadius, hubWaistY))
    .close()
    .revolve(360, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
)
body = body.cut(waist).clean()

slot = (
    cq.Workplane("XY")
    .transformed(offset=(0.0, slotY, 0.0), rotate=(-90.0, 0.0, 0.0))
    .rect(2.0 * slotHalf, 2.0 * (flangeRadius + cutOver), centered=True)
    .extrude(flangeYMax - slotY + cutOver)
)

rMaj = holeMajorDia / 2.0
rMin = holeMinorDia / 2.0
rMid = (rMaj + rMin) / 2.0
chamfer = rMid - rMin
endX = flangeRadius + 3.0
outerConeX = xFace - chamfer
innerConeX = slotHalf + chamfer
majorLen = flangeRadius - xFace + 3.0


def _coaxial(y0, z0):
    return (
        cq.Workplane("XY")
        .moveTo(-endX, 0.0)
        .lineTo(endX, 0.0)
        .lineTo(endX, rMid)
        .lineTo(xFace, rMid)
        .lineTo(outerConeX, rMin)
        .lineTo(innerConeX, rMin)
        .lineTo(slotHalf, rMid)
        .lineTo(-slotHalf, rMid)
        .lineTo(-innerConeX, rMin)
        .lineTo(-outerConeX, rMin)
        .lineTo(-xFace, rMid)
        .lineTo(-endX, rMid)
        .close()
        .revolve(360, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
        .translate((0.0, y0, z0))
    )


def _major(x0, y0, z0, sense):
    pl = cq.Plane(origin=(x0, y0, z0), xDir=(0.0, 1.0, 0.0), normal=(sense, 0.0, 0.0))
    return cq.Workplane(pl).circle(rMaj).extrude(majorLen)


bores = (
    _coaxial(holeY, holeZ)
    .union(_coaxial(holeY, -holeZ))
    .union(_major(xFace, holeMajorPosY, holeMajorPosZ, 1.0))
    .union(_major(-xFace, holeMajorPosY, holeMajorPosZ, -1.0))
    .union(_major(xFace, holeY, -holeZ, 1.0))
    .union(_major(-xFace, holeY, -holeZ, -1.0))
)

rimR = (rimHoleX * rimHoleX + rimHoleZ * rimHoleZ) ** 0.5
ux, uz = rimHoleX / rimR, rimHoleZ / rimR
startR = flangeRadius + 0.6


def _rim(sign):
    origin = (ux * startR, rimHoleY, sign * uz * startR)
    pl = cq.Plane(origin=origin, xDir=(0.0, 1.0, 0.0), normal=(-ux, 0.0, -sign * uz))
    return cq.Workplane(pl).circle(rimHoleDia / 2.0).extrude(rimHoleLen + 0.6)


rims = _rim(1.0).union(_rim(-1.0))
cutters = slot.union(bores).union(rims)
result = body.cut(cutters).clean()

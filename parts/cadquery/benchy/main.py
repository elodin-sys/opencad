# isort: off
import cadquery as cq
import math
# isort: on

# Contract dimensions, millimetres and degrees.
overallLength = 60.0
overallWidth = 31.0
overallHeight = 48.0
bridgeRoofLength = 23.0
chimneyInnerDiameter = 3.0
chimneyOuterDiameter = 7.0
chimneyHoleDepth = 11.0
cargoBoxTopHeight = 15.5
cargoBoxOuterA = 12.0
cargoBoxOuterB = 10.81
cargoBoxInnerA = 8.0
cargoBoxInnerB = 7.0
cargoBoxDepth = 9.0
hawsepipeInnerDiameter = 4.0
hawsepipeFlangeDepth = 0.3
frontWindowWidth = 10.5
frontWindowHeight = 9.5
rearWindowInnerDiameter = 9.0
rearWindowOuterDiameter = 12.0
rearWindowFlangeDepth = 0.3
bowOverhangAngle = 40.0
bridgeRoofAngle = 5.5
nameplateThickness = 0.1
hullKeelLength = 40.0
hullKeelWidth = 20.0
hullKeelCenterX = 25.0
hullSternWidth = 22.0
deckHeight = 10.0
sternGunwaleHeight = 11.5
bowGunwaleHeight = 24.0
hullWallThickness = 1.6
cabinCenterX = 31.0
cabinLength = 20.0
cabinWidth = 18.0
cabinWallThickness = 2.0
bridgeRoofWidth = 20.0
bridgeRoofThickness = 2.5
chimneyCenterX = 25.0
chimneyHeightAboveRoof = 10.0
chimneyStemDiameter = 5.5
chimneyCollarHeight = 2.0
cargoBoxCenterX = 15.0
hawsepipeCenterX = 52.0
hawsepipeCenterZ = 18.0
hawsepipeOuterDiameter = 6.0
windowCenterHeight = 27.0
sideOpeningWidth = 9.0
sideOpeningHeight = 22.0

# Small construction allowances do not change the caliper dimensions.
cutOverrun = 0.03
# Fixed parent mould; overallLength edits insert/remove a stern section.
mouldLength = 60.0
lengthInsertX = 3.0
lengthExtension = overallLength - mouldLength
assert overallLength > mouldLength - lengthInsertX, "infeasible stern shortening"
roofSlope = math.tan(math.radians(bridgeRoofAngle))
bowSlope = math.tan(math.radians(bowOverhangAngle))
keelAft = hullKeelCenterX - hullKeelLength / 2.0
keelBow = hullKeelCenterX + hullKeelLength / 2.0
# Quadratic bow meets the straight upper loft tangentially at deckHeight.
bowQuadratic = (mouldLength - keelBow - bowGunwaleHeight / bowSlope) / (
    2 * deckHeight * bowGunwaleHeight - deckHeight**2
)
bowAtDeck = keelBow + deckHeight / bowSlope + bowQuadratic * deckHeight**2
bowAtMid = keelBow + deckHeight / (2 * bowSlope) + bowQuadratic * (deckHeight / 2) ** 2
roofAtChimney = overallHeight - chimneyHeightAboveRoof
cabinAft = cabinCenterX - cabinLength / 2.0
cabinBow = cabinCenterX + cabinLength / 2.0
cargoFloor = cargoBoxTopHeight - cargoBoxDepth
chimneyFloor = overallHeight - chimneyHoleDepth

assert 0 < hullWallThickness < hullKeelWidth / 2, "infeasible hull thickness"
assert 0 <= keelAft < keelBow < bowAtDeck < overallLength, "infeasible bow envelope"
assert 0 < deckHeight < sternGunwaleHeight < bowGunwaleHeight, "infeasible sheer"
assert 0 < cabinWallThickness < min(cabinWidth, cabinLength) / 2, "infeasible cabin"
assert 0 < cargoFloor < deckHeight < cargoBoxTopHeight, "cargo pocket must be blind"
assert 0 < cargoBoxInnerA < cargoBoxOuterA, "infeasible cargo beam"
assert 0 < cargoBoxInnerB < cargoBoxOuterB, "infeasible cargo length"
assert 0 < chimneyInnerDiameter < chimneyStemDiameter < chimneyOuterDiameter, "infeasible chimney diameters"
assert chimneyFloor > roofAtChimney - bridgeRoofThickness + chimneyInnerDiameter * roofSlope, (
    "chimney floor must remain above cabin"
)
assert 0 < rearWindowInnerDiameter < rearWindowOuterDiameter < cabinWidth, "infeasible rear window"
assert frontWindowWidth < cabinWidth - 2 * cabinWallThickness, "front opening too wide"
assert sideOpeningWidth < cabinLength - 2 * cabinWallThickness, "side opening too wide"
assert deckHeight + sideOpeningHeight < roofAtChimney - bridgeRoofThickness, "side arch reaches roof"
assert bridgeRoofLength > cabinLength and bridgeRoofWidth > cabinWidth, "roof must overhang"


def half_waterline(z, aft, bow, beam, stern):
    """Two bounded cubic curves; beam maximum is an explicit tangent point."""
    span = bow - aft
    return (
        cq.Workplane("XY", origin=(0, 0, z))
        .moveTo(aft, 0)
        .lineTo(aft, stern)
        .bezier([(aft + 0.12 * span, beam), (aft + 0.27 * span, beam), (aft + 0.42 * span, beam)], includeCurrent=True)
        .bezier([(aft + 0.75 * span, beam), (bow, 0.55 * beam), (bow, 0)], includeCurrent=True)
        .close()
        .val()
    )


def waterline_loft(rows):
    wires = [half_waterline(*row) for row in rows]
    return cq.Workplane("XY").newObject(wires).toPending().loft(ruled=False)


# The lower bow has the specified tangent at the keel and joins the upper hull smoothly.
lowerHalf = waterline_loft(
    [
        (0.0, keelAft, keelBow, hullKeelWidth / 2, hullSternWidth * hullKeelWidth / overallWidth / 2),
        (
            deckHeight / 2,
            keelAft / 4,
            bowAtMid,
            (hullKeelWidth + 3 * overallWidth) / 8,
            hullSternWidth * (3 + hullKeelWidth / overallWidth) / 8,
        ),
        (deckHeight, 0.0, bowAtDeck, overallWidth / 2, hullSternWidth / 2),
    ]
)
upperHalf = waterline_loft(
    [
        (deckHeight, 0.0, bowAtDeck, overallWidth / 2, hullSternWidth / 2),
        (
            (deckHeight + bowGunwaleHeight) / 2,
            0.0,
            (bowAtDeck + mouldLength) / 2,
            overallWidth / 2,
            hullSternWidth / 2,
        ),
        (bowGunwaleHeight, 0.0, mouldLength, overallWidth / 2, hullSternWidth / 2),
    ]
)
# Sheer is a smooth curve, rising toward the bow. XZ positive normal is -Y.
sheer = (
    cq.Workplane("XZ")
    .moveTo(0, -cutOverrun)
    .lineTo(mouldLength, -cutOverrun)
    .lineTo(mouldLength, bowGunwaleHeight)
    .spline(
        [
            (0.87 * mouldLength, sternGunwaleHeight + 0.82 * (bowGunwaleHeight - sternGunwaleHeight)),
            (0.70 * mouldLength, sternGunwaleHeight + 0.45 * (bowGunwaleHeight - sternGunwaleHeight)),
            (0.50 * mouldLength, sternGunwaleHeight + 0.16 * (bowGunwaleHeight - sternGunwaleHeight)),
            (0.0, sternGunwaleHeight),
        ],
        includeCurrent=True,
    )
    .close()
    .extrude(overallWidth, both=True)
)
hullHalf = lowerHalf.union(upperHalf).intersect(sheer)
hullOuter = hullHalf.mirror("XZ", union=True)
innerHalf = waterline_loft(
    [
        (
            deckHeight,
            hullWallThickness,
            bowAtDeck - hullWallThickness,
            overallWidth / 2 - hullWallThickness,
            hullSternWidth / 2 - hullWallThickness,
        ),
        (
            (deckHeight + bowGunwaleHeight) / 2,
            hullWallThickness,
            (bowAtDeck + mouldLength) / 2 - hullWallThickness,
            overallWidth / 2 - hullWallThickness,
            hullSternWidth / 2 - hullWallThickness,
        ),
        (
            bowGunwaleHeight + cutOverrun,
            hullWallThickness,
            mouldLength - hullWallThickness,
            overallWidth / 2 - hullWallThickness,
            hullSternWidth / 2 - hullWallThickness,
        ),
    ]
)
wellTool = innerHalf.mirror("XZ", union=True)


def extend_stern(body):
    """Insert a constant section; leave the bow curvature and tangent intact."""
    if abs(lengthExtension) < 1e-9:
        return body
    aftEnd = lengthInsertX + min(lengthExtension, 0.0)
    aftClip = (
        cq.Workplane("XY")
        .box(aftEnd + cutOverrun, 2 * overallWidth, overallHeight, centered=(False, True, False))
        .translate((-cutOverrun, 0, 0))
    )
    foreClip = (
        cq.Workplane("XY")
        .box(mouldLength, 2 * overallWidth, overallHeight, centered=(False, True, False))
        .translate((lengthInsertX, 0, 0))
    )
    aft = body.intersect(aftClip)
    fore = body.intersect(foreClip).translate((lengthExtension, 0, 0))
    if lengthExtension > 0:
        bridge = (
            cq.Workplane("YZ", origin=(lengthInsertX, 0, 0))
            .add(body)
            .section()
            .wires()
            .toPending()
            .extrude(lengthExtension, combine=False)
        )
        return aft.union(bridge).union(fore).clean()
    return aft.union(fore).clean()


hullOuter = extend_stern(hullOuter)
wellTool = extend_stern(wellTool)
hull = hullOuter.cut(wellTool).clean()


def roof_z(x):
    return roofAtChimney + (x - chimneyCenterX) * roofSlope


def xz_prism(points, width):
    return cq.Workplane("XZ").polyline(points).close().extrude(width / 2, both=True)


cabin = xz_prism(
    [
        (cabinAft, deckHeight - cutOverrun),
        (cabinBow, deckHeight - cutOverrun),
        (cabinBow, roof_z(cabinBow) - bridgeRoofThickness + cutOverrun),
        (cabinAft, roof_z(cabinAft) - bridgeRoofThickness + cutOverrun),
    ],
    cabinWidth,
)
roofAft = cabinCenterX - bridgeRoofLength / 2
roofBow = cabinCenterX + bridgeRoofLength / 2
roof = xz_prism(
    [
        (roofAft, roof_z(roofAft) - bridgeRoofThickness),
        (roofBow, roof_z(roofBow) - bridgeRoofThickness),
        (roofBow, roof_z(roofBow)),
        (roofAft, roof_z(roofAft)),
    ],
    bridgeRoofWidth,
)
chimneyBase = roofAtChimney - chimneyStemDiameter * roofSlope / 2 - cutOverrun
stem = (
    cq.Workplane("XY", origin=(chimneyCenterX, 0, chimneyBase))
    .circle(chimneyStemDiameter / 2)
    .extrude(overallHeight - chimneyCollarHeight - chimneyBase + cutOverrun)
)
collar = (
    cq.Workplane("XY", origin=(chimneyCenterX, 0, overallHeight - chimneyCollarHeight))
    .circle(chimneyOuterDiameter / 2)
    .extrude(chimneyCollarHeight)
)
cargo = (
    cq.Workplane("XY", origin=(cargoBoxCenterX, 0, deckHeight - cutOverrun))
    .rect(cargoBoxOuterB, cargoBoxOuterA)
    .extrude(cargoBoxTopHeight - deckHeight + cutOverrun)
)
result = hull.union(cabin).union(roof).union(stem).union(collar).union(cargo).clean()

# Blind pockets and cabin interior: floors remain exact contract datums.
insideAft = cabinAft + cabinWallThickness
insideBow = cabinBow - cabinWallThickness
cabinVoid = xz_prism(
    [
        (insideAft, deckHeight),
        (insideBow, deckHeight),
        (insideBow, roof_z(insideBow) - bridgeRoofThickness),
        (insideAft, roof_z(insideAft) - bridgeRoofThickness),
    ],
    cabinWidth - 2 * cabinWallThickness,
)
cargoVoid = (
    cq.Workplane("XY", origin=(cargoBoxCenterX, 0, cargoFloor))
    .rect(cargoBoxInnerB, cargoBoxInnerA)
    .extrude(cargoBoxDepth + cutOverrun)
)
chimneyVoid = (
    cq.Workplane("XY", origin=(chimneyCenterX, 0, chimneyFloor))
    .circle(chimneyInnerDiameter / 2)
    .extrude(chimneyHoleDepth + cutOverrun)
)
voids = cabinVoid.union(cargoVoid).union(chimneyVoid)
result = result.cut(voids).clean()

# The rear flange is normal to X; its rear plane is 0.30 mm behind the wall.
rearFlange = (
    cq.Workplane("YZ", origin=(cabinAft - rearWindowFlangeDepth, 0, windowCenterHeight))
    .circle(rearWindowOuterDiameter / 2)
    .extrude(rearWindowFlangeDepth + cutOverrun)
)
# A translated copy of the outer mould gives an exact axial projection on
# the curved hull, rather than a floating planar washer.
hawseEnvelope = (
    cq.Workplane("XZ", origin=(hawsepipeCenterX, 0, hawsepipeCenterZ))
    .circle(hawsepipeOuterDiameter / 2)
    .extrude(overallWidth, both=True)
)
portRegion = (
    cq.Workplane("XY")
    .box(overallLength + 2 * cutOverrun, overallWidth, overallHeight, centered=(False, False, False))
    .translate((-cutOverrun, 0, 0))
)
portFlange = (
    hullOuter.translate((0, hawsepipeFlangeDepth, 0))
    .cut(hullOuter.translate((0, -cutOverrun, 0)))
    .intersect(hawseEnvelope)
    .intersect(portRegion)
)
hawseFlanges = portFlange.mirror("XZ", union=True)
frontVoid = (
    cq.Workplane("YZ", origin=(cabinBow - cabinWallThickness - cutOverrun, 0, windowCenterHeight))
    .rect(frontWindowWidth, frontWindowHeight)
    .extrude(cabinWallThickness + 2 * cutOverrun)
)
rearVoid = (
    cq.Workplane("YZ", origin=(cabinAft - rearWindowFlangeDepth - cutOverrun, 0, windowCenterHeight))
    .circle(rearWindowInnerDiameter / 2)
    .extrude(cabinWallThickness + rearWindowFlangeDepth + 2 * cutOverrun)
)
archRadius = sideOpeningWidth / 2
archSpring = deckHeight + sideOpeningHeight - archRadius
sideVoid = (
    cq.Workplane("XZ")
    .moveTo(cabinCenterX - archRadius, deckHeight - cutOverrun)
    .lineTo(cabinCenterX + archRadius, deckHeight - cutOverrun)
    .lineTo(cabinCenterX + archRadius, archSpring)
    .threePointArc((cabinCenterX, deckHeight + sideOpeningHeight), (cabinCenterX - archRadius, archSpring))
    .close()
    .extrude(cabinWidth / 2 + cutOverrun, both=True)
)
hawseVoid = (
    cq.Workplane("XZ", origin=(hawsepipeCenterX, 0, hawsepipeCenterZ))
    .circle(hawsepipeInnerDiameter / 2)
    .extrude(overallWidth, both=True)
)
openingTools = frontVoid.union(rearVoid).union(sideVoid).union(hawseVoid)
result = result.union(rearFlange).union(hawseFlanges).cut(openingTools).clean()

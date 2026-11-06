"""Parametric Benchy reconstruction; pipeline dimensions are millimetres."""

from math import radians, tan

from build123d import (
    Align,
    Bezier,
    Box,
    Compound,
    Cylinder,
    Face,
    Line,
    Plane,
    Polyline,
    Pos,
    ThreePointArc,
    Wire,
    extrude,
    make_face,
    mirror,
)
from navier_cad.blends import fuse_all
from navier_cad.sweeps import loft_sections

# Independent contract dimensions. The pipeline edits these literals individually.
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

assert overallLength > hullKeelCenterX + hullKeelLength / 2, "Bow beyond keel"
assert overallWidth > hullKeelWidth > 2 * hullWallThickness, "Positive hull flare"
assert 0 < deckHeight < sternGunwaleHeight < bowGunwaleHeight, "Open sheer"
assert 0 < cargoBoxDepth < cargoBoxTopHeight, "Cargo floor stays above keel"
assert cargoBoxInnerA < cargoBoxOuterA, "Cargo beam wall must be positive"
assert cargoBoxInnerB < cargoBoxOuterB, "Cargo length wall must be positive"
assert chimneyInnerDiameter < chimneyStemDiameter < chimneyOuterDiameter, "Chimney wall"
assert hawsepipeInnerDiameter < hawsepipeOuterDiameter, "Hawsepipe ring"
assert rearWindowInnerDiameter < rearWindowOuterDiameter < cabinWidth, "Rear flange"
assert cabinLength > 2 * cabinWallThickness + sideOpeningWidth, "Side jambs"
assert cabinWidth > frontWindowWidth + 2 * cabinWallThickness, "Front jambs"

# Nominal mould length: length edits stretch the inferred keel/midbody,
# not the independent stated roof, aperture, pocket or chimney dimensions.
hullReferenceLength = 60.0
hullLengthGrowth = overallLength - hullReferenceLength
hullKeelGrowthFraction = 0.85
cutOverrun = 0.02
roofSlope = tan(radians(bridgeRoofAngle))
roofAtStack = overallHeight - chimneyHeightAboveRoof
cabinRear = cabinCenterX - cabinLength / 2
cabinFront = cabinCenterX + cabinLength / 2
roofRear = cabinCenterX - bridgeRoofLength / 2
roofFront = cabinCenterX + bridgeRoofLength / 2


def roof_z(x):
    return roofAtStack + (x - chimneyCenterX) * roofSlope


assert deckHeight + sideOpeningHeight < roof_z(cabinRear) - bridgeRoofThickness, "Arch clearance"
assert overallHeight - chimneyHoleDepth > roof_z(chimneyCenterX) - bridgeRoofThickness, "Blind chimney floor"


def half_waterline(t, inset=0.0):
    """Four corresponding edges; cubic bow law has a 40-degree keel tangent."""
    keel_a = hullKeelCenterX - hullKeelLength / 2
    keel_b = hullKeelCenterX + hullKeelLength / 2 + hullKeelGrowthFraction * hullLengthGrowth
    bow_control = keel_b + bowGunwaleHeight / (3 * tan(radians(bowOverhangAngle)))
    a = keel_a * (1 - t) ** 2 + inset
    b = (
        keel_b * (1 - t) ** 3
        + 3 * bow_control * t * (1 - t) ** 2
        + 3 * overallLength * t**2 * (1 - t)
        + overallLength * t**3
        - inset
    )
    beam = (hullKeelWidth + t * (overallWidth - hullKeelWidth)) / 2 - inset
    stern = (0.70 * hullKeelWidth + t * (hullSternWidth - 0.70 * hullKeelWidth)) / 2 - inset
    widest = a + 0.40 * (b - a)
    stern_z = t * sternGunwaleHeight
    bow_z = t * bowGunwaleHeight

    def p(x, y):
        return (x, y, stern_z + (x - a) * (bow_z - stern_z) / (b - a))

    edges = [
        Line(p(a, 0), p(a, stern)),
        Bezier(p(a, stern), p(a + 0.12 * (b - a), beam), p(widest - 0.12 * (b - a), beam), p(widest, beam)),
        Bezier(p(widest, beam), p(widest + 0.25 * (b - a), beam), p(b, 0.36 * beam), p(b, 0)),
        Line(p(b, 0), p(a, 0)),
    ]
    return Face(Wire(edges))


stations = (0.0, 1 / 3, 2 / 3, 1.0)
outerHalf = loft_sections([half_waterline(t) for t in stations])
hull = fuse_all(outerHalf, [mirror(outerHalf, about=Plane.XZ)])


def sloped_prism(x0, x1, width, bottom_offset, top_offset):
    outline = Polyline(
        (x0, -width / 2, roof_z(x0) + bottom_offset),
        (x1, -width / 2, roof_z(x1) + bottom_offset),
        (x1, -width / 2, roof_z(x1) + top_offset),
        (x0, -width / 2, roof_z(x0) + top_offset),
        close=True,
    )
    return extrude(make_face(outline.edges()), amount=width, dir=(0, 1, 0))


def cabin_prism(x0, x1, width):
    outline = Polyline(
        (x0, -width / 2, deckHeight - cutOverrun),
        (x1, -width / 2, deckHeight - cutOverrun),
        (x1, -width / 2, roof_z(x1) - bridgeRoofThickness + cutOverrun),
        (x0, -width / 2, roof_z(x0) - bridgeRoofThickness + cutOverrun),
        close=True,
    )
    return extrude(make_face(outline.edges()), amount=width, dir=(0, 1, 0))


cabin = cabin_prism(cabinRear, cabinFront, cabinWidth)
roof = sloped_prism(roofRear, roofFront, bridgeRoofWidth, -bridgeRoofThickness, 0.0)
cargo = Pos(cargoBoxCenterX, 0, deckHeight - cutOverrun) * Box(
    cargoBoxOuterB,
    cargoBoxOuterA,
    cargoBoxTopHeight - deckHeight + cutOverrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
stackBase = roofAtStack - bridgeRoofThickness + cutOverrun
stem = Pos(chimneyCenterX, 0, stackBase) * Cylinder(
    chimneyStemDiameter / 2,
    overallHeight - stackBase - chimneyCollarHeight + cutOverrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
collar = Pos(chimneyCenterX, 0, overallHeight - chimneyCollarHeight) * Cylinder(
    chimneyOuterDiameter / 2,
    chimneyCollarHeight,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)

# Group 2: nested loft, clipped at deck, leaves the filled lower hull.
innerHalf = loft_sections([half_waterline(t, hullWallThickness) for t in stations])
innerRiserHalf = extrude(half_waterline(1.0, hullWallThickness), amount=overallHeight, dir=(0, 0, 1))
wellHalf = fuse_all(innerHalf, [innerRiserHalf])
well = fuse_all(wellHalf, [mirror(wellHalf, about=Plane.XZ)])
aboveDeck = Pos(overallLength / 2, 0, deckHeight) * Box(
    overallLength + 2,
    overallWidth + 2,
    overallHeight,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
well = well & aboveDeck
openHull = hull - well

interior = cabin_prism(
    cabinRear + cabinWallThickness,
    cabinFront - cabinWallThickness,
    cabinWidth - 2 * cabinWallThickness,
)
rearRing = Pos(cabinRear - rearWindowFlangeDepth / 2 + cutOverrun / 2, 0, windowCenterHeight) * Cylinder(
    rearWindowOuterDiameter / 2,
    rearWindowFlangeDepth + cutOverrun,
    rotation=(0, 90, 0),
)
frontAperture = Pos(cabinFront - cabinWallThickness / 2, 0, windowCenterHeight) * Box(
    cabinWallThickness + 2 * cutOverrun,
    frontWindowWidth,
    frontWindowHeight,
)
rearAperture = Pos(
    cabinRear + (cabinWallThickness - rearWindowFlangeDepth) / 2,
    0,
    windowCenterHeight,
) * Cylinder(
    rearWindowInnerDiameter / 2,
    cabinWallThickness + rearWindowFlangeDepth + 2 * cutOverrun,
    rotation=(0, 90, 0),
)
archRadius = sideOpeningWidth / 2
archSpring = deckHeight + sideOpeningHeight - archRadius
archLeft = cabinCenterX - archRadius
archRight = cabinCenterX + archRadius
archY = -cabinWidth / 2 - cutOverrun
archWire = Wire(
    [
        Line((archLeft, archY, deckHeight - cutOverrun), (archRight, archY, deckHeight - cutOverrun)),
        Line((archRight, archY, deckHeight - cutOverrun), (archRight, archY, archSpring)),
        ThreePointArc(
            (archRight, archY, archSpring),
            (cabinCenterX, archY, deckHeight + sideOpeningHeight),
            (archLeft, archY, archSpring),
        ),
        Line((archLeft, archY, archSpring), (archLeft, archY, deckHeight - cutOverrun)),
    ]
)
sideApertures = extrude(Face(archWire), amount=cabinWidth + 2 * cutOverrun, dir=(0, 1, 0))
cabinShell = fuse_all(cabin, [rearRing]) - Compound([interior, frontAperture, rearAperture, sideApertures])

result = fuse_all(openHull, [cabinShell, roof, cargo, stem, collar])
assert result.is_valid, "The hollow body must remain valid"
assert len(result.solids()) == 1, "The hollow body must remain connected"

# Group 3: a conformal 0.30-mm flange is a translated surface patch,
# not an arbitrary cylindrical boss on the curved bow. Its bore axis is Y.
flangeMask = Pos(hawsepipeCenterX, overallWidth / 4, hawsepipeCenterZ) * Cylinder(
    hawsepipeOuterDiameter / 2,
    overallWidth / 2,
    rotation=(90, 0, 0),
)
flangeOuter = (Pos(0, hawsepipeFlangeDepth, 0) * hull) & flangeMask
flangeInner = (Pos(0, -cutOverrun, 0) * hull) & flangeMask
assert flangeOuter is not None and flangeInner is not None, "Hawsepipe must reach bow wall"
portFlange = flangeOuter - flangeInner
starboardFlange = mirror(portFlange, about=Plane.XZ)

chimneyBore = Pos(chimneyCenterX, 0, overallHeight - chimneyHoleDepth) * Cylinder(
    chimneyInnerDiameter / 2,
    chimneyHoleDepth + cutOverrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
cargoPocket = Pos(cargoBoxCenterX, 0, cargoBoxTopHeight - cargoBoxDepth) * Box(
    cargoBoxInnerB,
    cargoBoxInnerA,
    cargoBoxDepth + cutOverrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
hawsepipeBore = Pos(hawsepipeCenterX, 0, hawsepipeCenterZ) * Cylinder(
    hawsepipeInnerDiameter / 2,
    overallWidth + 2 * cutOverrun,
    rotation=(90, 0, 0),
)
result = fuse_all(result, [portFlange, starboardFlange]) - Compound([chimneyBore, cargoPocket, hawsepipeBore])
assert result.is_valid, "The final Benchy must remain a valid solid"
assert len(result.solids()) == 1, "The print must remain one connected solid"

from math import radians, tan

from build123d import (
    Align,
    Bezier,
    Box,
    Compound,
    Cylinder,
    Line,
    Plane,
    Polyline,
    Pos,
    ThreePointArc,
    extrude,
    loft,
    make_face,
    mirror,
)

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
# Unstated intermediate waterline reconstruction controls. Longer boats gain
# submerged shoulder fullness as well as bow reach; keel and maximum beam stay fixed.
hullReferenceLength = 60.0
hullLengthFullnessRate = 0.31

assert overallLength > 0, "infeasible: overallLength must be positive"
assert overallWidth > 0, "infeasible: overallWidth must be positive"
assert overallHeight > 0, "infeasible: overallHeight must be positive"
assert cargoBoxDepth > 0, "infeasible: cargoBoxDepth must be positive"
assert hullSternWidth > 0, "infeasible: hullSternWidth must be positive"
assert sternGunwaleHeight > 0, "infeasible: sternGunwaleHeight must be positive"
assert bowGunwaleHeight > 0, "infeasible: bowGunwaleHeight must be positive"
assert chimneyOuterDiameter > 0, "infeasible: chimneyOuterDiameter must be positive"
assert hullWallThickness > 0, "infeasible: hullWallThickness must be positive"

assert 0 < hullKeelWidth < overallWidth, "infeasible: keel must fit inside beam"
assert 0 < hullSternWidth <= overallWidth, "infeasible: transom exceeds beam"
assert 0 < hullKeelLength < overallLength, "infeasible: keel exceeds hull length"
assert hullKeelCenterX - hullKeelLength / 2 > 0, "infeasible: keel crosses stern"
assert hullKeelCenterX + hullKeelLength / 2 < overallLength, "infeasible: keel crosses bow"
assert 0 < cabinWidth < bridgeRoofWidth < overallWidth, "infeasible: cabin/roof beam"
assert 0 < cabinLength < bridgeRoofLength, "infeasible: roof must overhang cabin"
assert bridgeRoofThickness > 0, "infeasible: roof thickness must be positive"
assert 0 < chimneyCollarHeight < chimneyHeightAboveRoof, "infeasible: chimney collar height"
assert 0 < chimneyStemDiameter <= chimneyOuterDiameter, "infeasible: chimney diameters"
assert 0 < cargoBoxDepth < cargoBoxTopHeight, "infeasible: cargo floor must remain above keel"


def half_outline(aft, fore, station, half_beam, half_transom, height):
    """Four-edge port outline; its control polygon stays within the envelope."""

    def point(x, y):
        return (x, y, height(x))

    return make_face(
        [
            Line(point(aft, 0.0), point(aft, half_transom)),
            Bezier(
                point(aft, half_transom),
                point(aft + (station - aft) * 0.3, half_beam),
                point(aft + (station - aft) * 0.7, half_beam),
                point(station, half_beam),
            ),
            Bezier(
                point(station, half_beam),
                point(station + (fore - station) * 0.55, half_beam),
                point(fore, half_beam * 0.3),
                point(fore, 0.0),
            ),
            Line(point(fore, 0.0), point(aft, 0.0)),
        ]
    )


# Fair, mirrored hull with a flat keel and a planar rising sheer.
keel = half_outline(
    hullKeelCenterX - hullKeelLength / 2,
    hullKeelCenterX + hullKeelLength / 2,
    hullKeelCenterX,
    hullKeelWidth / 2,
    hullKeelWidth * 0.4,
    lambda x: 0.0,
)
sheer = half_outline(
    0.0,
    overallLength,
    hullKeelCenterX,
    overallWidth / 2,
    hullSternWidth / 2,
    lambda x: sternGunwaleHeight + (bowGunwaleHeight - sternGunwaleHeight) * x / overallLength,
)
# Three sections preserve flare while allowing an independent bow tangent.
# The bounded solve uses the actual native edge, not an assumed loft
# parameterization: OpenCascade chooses its own interpolation parameters.
keel_fore = hullKeelCenterX + hullKeelLength / 2
middle_aft = (hullKeelCenterX - hullKeelLength / 2) / 2


def middle_outline(fore, inset=0.0):
    return half_outline(
        middle_aft + inset,
        fore - inset,
        hullKeelCenterX,
        (hullKeelWidth + overallWidth) / 4 + (overallLength - hullReferenceLength) * hullLengthFullnessRate - inset,
        (hullKeelWidth * 0.4 + hullSternWidth / 2) / 2 - inset,
        lambda x: (
            sternGunwaleHeight / 2
            + (bowGunwaleHeight - sternGunwaleHeight) / 2 * (x - middle_aft) / (fore - middle_aft)
            + (0.02 if inset else 0.0)
        ),
    )


def lower_bow_slope(body):
    edge = next(
        edge
        for edge in body.edges()
        if abs(edge.bounding_box().min.Y) < 0.00001
        and abs(edge.bounding_box().max.Y) < 0.00001
        and edge.bounding_box().min.Z < 0.00001
        and edge.bounding_box().max.X > overallLength - 0.00001
    )
    tangent = edge.tangent_at(0.0 if edge.position_at(0.0).Z < 0.00001 else 1.0)
    return abs(tangent.Z / tangent.X)


assert 0 < bowOverhangAngle < 90, "infeasible: bow angle"
assert (
    hullKeelWidth / 2
    < (hullKeelWidth + overallWidth) / 4 + (overallLength - hullReferenceLength) * hullLengthFullnessRate
    < overallWidth / 2
), "infeasible: intermediate waterline exceeds beam"
low_fore = (keel_fore + overallLength) / 2
high_fore = overallLength - 0.01
for _ in range(22):
    middle_fore = (low_fore + high_fore) / 2
    port_hull = loft([keel, middle_outline(middle_fore), sheer], ruled=False)
    if lower_bow_slope(port_hull) > tan(radians(bowOverhangAngle)):
        low_fore = middle_fore
    else:
        high_fore = middle_fore
assert abs(lower_bow_slope(port_hull) - tan(radians(bowOverhangAngle))) < 0.0001, "infeasible: bow tangent not resolved"
hull = port_hull + mirror(port_hull, about=Plane.XZ)


def roof_height(x):
    return overallHeight - chimneyHeightAboveRoof + (x - chimneyCenterX) * tan(radians(bridgeRoofAngle))


def slab(x0, x1, width, bottom, top):
    profile = make_face(
        Polyline(
            (x0, -width / 2, bottom(x0)),
            (x1, -width / 2, bottom(x1)),
            (x1, -width / 2, top(x1)),
            (x0, -width / 2, top(x0)),
            close=True,
        )
    )
    return extrude(profile, amount=width, dir=(0.0, 1.0, 0.0))


roof_aft = cabinCenterX - bridgeRoofLength / 2
roof_fore = cabinCenterX + bridgeRoofLength / 2
assert 0 < roof_aft < roof_fore < overallLength, "infeasible: roof exceeds hull length"
assert roof_height(roof_fore) < overallHeight, "infeasible: roof exceeds chimney top"
assert roof_height(roof_aft) - bridgeRoofThickness > bowGunwaleHeight, "infeasible: cabin height"

# Bridge outside and overhanging roof; interiors are subtracted below.
cabin = slab(
    cabinCenterX - cabinLength / 2,
    cabinCenterX + cabinLength / 2,
    cabinWidth,
    lambda x: deckHeight,
    lambda x: roof_height(x) - bridgeRoofThickness,
)
roof = slab(
    roof_aft,
    roof_fore,
    bridgeRoofWidth,
    lambda x: roof_height(x) - bridgeRoofThickness,
    roof_height,
)
stack_base = roof_height(chimneyCenterX) - bridgeRoofThickness
stem = Pos(chimneyCenterX, 0.0, stack_base) * Cylinder(
    chimneyStemDiameter / 2,
    overallHeight - chimneyCollarHeight - stack_base,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
collar = Pos(chimneyCenterX, 0.0, overallHeight - chimneyCollarHeight) * Cylinder(
    chimneyOuterDiameter / 2,
    chimneyCollarHeight,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
cargo = Pos(cargoBoxCenterX, 0.0, deckHeight) * Box(
    cargoBoxOuterB,
    cargoBoxOuterA,
    cargoBoxTopHeight - deckHeight,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)

# A smaller homologous loft opens the well while retaining the flat deck.
inner_keel = half_outline(
    hullKeelCenterX - hullKeelLength / 2 + hullWallThickness,
    hullKeelCenterX + hullKeelLength / 2 - hullWallThickness,
    hullKeelCenterX,
    hullKeelWidth / 2 - hullWallThickness,
    hullKeelWidth * 0.4 - hullWallThickness,
    lambda x: 0.0,
)
inner_sheer = half_outline(
    hullWallThickness,
    overallLength - hullWallThickness,
    hullKeelCenterX,
    overallWidth / 2 - hullWallThickness,
    hullSternWidth / 2 - hullWallThickness,
    lambda x: sternGunwaleHeight + (bowGunwaleHeight - sternGunwaleHeight) * x / overallLength + 0.04,
)
inner_port = loft([inner_keel, middle_outline(middle_fore, hullWallThickness), inner_sheer], ruled=False)
inner_hull = inner_port + mirror(inner_port, about=Plane.XZ)
above_deck = Pos(overallLength / 2, 0.0, deckHeight) * Box(
    overallLength + 0.04,
    overallWidth + 0.04,
    overallHeight,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
well = inner_hull & above_deck
outer_hull = hull
# Cylindrically clipped translated hulls give exactly the stated axial
# projection on each curved side without inventing a planar mounting pad.
hawse_stock = Pos(hawsepipeCenterX, 0.0, hawsepipeCenterZ) * Cylinder(
    hawsepipeOuterDiameter / 2,
    overallWidth + 2 * hawsepipeFlangeDepth,
    rotation=(90.0, 0.0, 0.0),
)
port_flange = (Pos(0.0, hawsepipeFlangeDepth, 0.0) * outer_hull) & hawse_stock
starboard_flange = mirror(port_flange, about=Plane.XZ)
hull = (outer_hull + port_flange + starboard_flange) - well
cabin_void = slab(
    cabinCenterX - cabinLength / 2 + cabinWallThickness,
    cabinCenterX + cabinLength / 2 - cabinWallThickness,
    cabinWidth - 2 * cabinWallThickness,
    lambda x: deckHeight,
    lambda x: roof_height(x) - bridgeRoofThickness,
)
chimney_void = Pos(chimneyCenterX, 0.0, overallHeight - chimneyHoleDepth) * Cylinder(
    chimneyInnerDiameter / 2,
    chimneyHoleDepth + 0.02,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
cargo_void = Pos(cargoBoxCenterX, 0.0, cargoBoxTopHeight - cargoBoxDepth) * Box(
    cargoBoxInnerB,
    cargoBoxInnerA,
    cargoBoxDepth + 0.02,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
assert 0 < chimneyInnerDiameter < chimneyStemDiameter, "infeasible: chimney bore exceeds stem"
assert overallHeight - chimneyHoleDepth > stack_base, "infeasible: chimney bore pierces roof"
assert 0 < cargoBoxInnerA < cargoBoxOuterA, "infeasible: cargo beam walls"
assert 0 < cargoBoxInnerB < cargoBoxOuterB, "infeasible: cargo length walls"
assert 0 < cabinWallThickness < min(cabinLength, cabinWidth) / 2, "infeasible: cabin walls"
result = hull + cabin + roof + stem + collar + cargo
result = result - Compound([cabin_void, chimney_void, cargo_void])


# End windows use world-space X axes, independent of the sloped roof.
rear_x = cabinCenterX - cabinLength / 2
front_x = cabinCenterX + cabinLength / 2
rear_flange = Pos(rear_x - rearWindowFlangeDepth, 0.0, windowCenterHeight) * Cylinder(
    rearWindowOuterDiameter / 2,
    rearWindowFlangeDepth + 0.02,
    rotation=(0.0, 90.0, 0.0),
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
rear_window = Pos(rear_x - rearWindowFlangeDepth - 0.02, 0.0, windowCenterHeight) * Cylinder(
    rearWindowInnerDiameter / 2,
    cabinWallThickness + rearWindowFlangeDepth + 0.04,
    rotation=(0.0, 90.0, 0.0),
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
front_window = Pos(front_x - cabinWallThickness / 2, 0.0, windowCenterHeight) * Box(
    cabinWallThickness + 0.04, frontWindowWidth, frontWindowHeight
)
arch_radius = sideOpeningWidth / 2
arch_spring = deckHeight + sideOpeningHeight - arch_radius
arch_y = -cabinWidth / 2 - 0.02
arch_left = cabinCenterX - arch_radius
arch_right = cabinCenterX + arch_radius
arch_profile = make_face(
    [
        Line((arch_left, arch_y, deckHeight), (arch_right, arch_y, deckHeight)),
        Line((arch_right, arch_y, deckHeight), (arch_right, arch_y, arch_spring)),
        ThreePointArc(
            (arch_right, arch_y, arch_spring),
            (cabinCenterX, arch_y, deckHeight + sideOpeningHeight),
            (arch_left, arch_y, arch_spring),
        ),
        Line((arch_left, arch_y, arch_spring), (arch_left, arch_y, deckHeight)),
    ]
)
side_openings = extrude(arch_profile, amount=cabinWidth + 0.04, dir=(0.0, 1.0, 0.0))
hawse_bore = Pos(hawsepipeCenterX, 0.0, hawsepipeCenterZ) * Cylinder(
    hawsepipeInnerDiameter / 2,
    overallWidth + 2 * hawsepipeFlangeDepth + 0.04,
    rotation=(90.0, 0.0, 0.0),
)
assert 0 < frontWindowWidth < cabinWidth - 2 * cabinWallThickness, "infeasible: front window beam"
assert 0 < frontWindowHeight < roof_height(front_x) - bridgeRoofThickness - deckHeight, (
    "infeasible: front window height"
)
assert 0 < rearWindowInnerDiameter < rearWindowOuterDiameter < cabinWidth, "infeasible: rear flange"
assert 0 < sideOpeningWidth < cabinLength - 2 * cabinWallThickness, "infeasible: side jambs"
assert sideOpeningWidth / 2 < sideOpeningHeight, "infeasible: side arch"
assert deckHeight + sideOpeningHeight < roof_height(arch_left) - bridgeRoofThickness, "infeasible: arch pierces roof"
assert 0 < hawsepipeInnerDiameter < hawsepipeOuterDiameter, "infeasible: hawse flange"
result = (result + rear_flange) - Compound([rear_window, front_window, side_openings, hawse_bore])
assert len(result.solids()) == 1, "infeasible: boat must be one connected solid"
assert result.is_valid, "infeasible: invalid boat solid"

# Finished-envelope guards follow edited dimensions rather than fixing them.
bounds = result.bounding_box()
assert abs(bounds.min.X) < 0.0001, "infeasible: stern datum moved"
assert abs(bounds.max.X - overallLength) < 0.0001, "infeasible: bow extent"
assert abs(bounds.min.Y + overallWidth / 2) < 0.0001, "infeasible: starboard extent"
assert abs(bounds.max.Y - overallWidth / 2) < 0.0001, "infeasible: port extent"
assert abs(bounds.min.Z) < 0.0001, "infeasible: keel datum moved"
assert abs(bounds.max.Z - overallHeight) < 0.0001, "infeasible: chimney extent"

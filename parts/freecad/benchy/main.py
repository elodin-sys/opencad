"""Parametric reconstruction of the dimensioned 3DBenchy calibration boat."""

import math

import FreeCAD
import Part
import PartDesign
import Sketcher

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

hullMouldReferenceLength = 60.0
forebodyStretchFraction = 0.8
forebodyExtension = forebodyStretchFraction * (overallLength - hullMouldReferenceLength)

roofSlope = math.tan(math.radians(bridgeRoofAngle))
roofAtChimney = overallHeight - chimneyHeightAboveRoof
keelAft = hullKeelCenterX - hullKeelLength / 2.0
keelBow = hullKeelCenterX + hullKeelLength / 2.0
bowDerivative = 1.0 / math.tan(math.radians(bowOverhangAngle))
bowQuadratic = (overallLength - forebodyExtension - keelBow - bowDerivative * bowGunwaleHeight) / bowGunwaleHeight**2
cabinAft = cabinCenterX - cabinLength / 2.0
cabinBow = cabinCenterX + cabinLength / 2.0
roofAft = cabinCenterX - bridgeRoofLength / 2.0
roofBow = cabinCenterX + bridgeRoofLength / 2.0
overrun = 0.03

assert 0.0 < keelAft < keelBow < overallLength, "infeasible: keel must fit the hull length"
assert 0.0 < hullKeelWidth < overallWidth, "infeasible: hull must flare above the keel"
assert 0.0 < hullWallThickness < hullSternWidth / 2.0, "infeasible: hull wall consumes the stern"
assert 0.0 < deckHeight < sternGunwaleHeight < bowGunwaleHeight, "infeasible: sheer must clear deck"
assert 0.0 < cabinWallThickness < min(cabinLength, cabinWidth) / 2.0, "infeasible: cabin cavity"
assert bridgeRoofLength > cabinLength and bridgeRoofWidth > cabinWidth, "infeasible: roof overhang"
assert 0.0 < cargoBoxDepth < cargoBoxTopHeight, "infeasible: cargo floor must remain above keel"
assert cargoBoxOuterA > cargoBoxInnerA > 0.0, "infeasible: cargo beam walls"
assert cargoBoxOuterB > cargoBoxInnerB > 0.0, "infeasible: cargo length walls"
assert chimneyOuterDiameter > chimneyStemDiameter > chimneyInnerDiameter > 0.0, "infeasible: chimney walls"
assert 0.0 < chimneyCollarHeight < chimneyHeightAboveRoof, "infeasible: chimney collar height"
assert (
    chimneyHeightAboveRoof
    < chimneyHoleDepth
    < chimneyHeightAboveRoof + bridgeRoofThickness - chimneyInnerDiameter * abs(roofSlope) / 2.0
), "infeasible: chimney bore must end inside roof"
assert frontWindowWidth < cabinWidth - 2.0 * cabinWallThickness, "infeasible: front window side clearance"
assert rearWindowOuterDiameter < cabinWidth, "infeasible: rear flange must fit cabin"
assert sideOpeningWidth < cabinLength - 2.0 * cabinWallThickness, "infeasible: side jambs"
assert deckHeight + sideOpeningHeight < roofAtChimney - bridgeRoofThickness, "infeasible: arch must clear roof"
assert windowCenterHeight + frontWindowHeight / 2.0 < roofAtChimney - bridgeRoofThickness, (
    "infeasible: front window roof clearance"
)
assert hawsepipeOuterDiameter > hawsepipeInnerDiameter > 0.0, "infeasible: hawse flange wall"

_ = PartDesign
doc = FreeCAD.newDocument("Benchy")
body = doc.addObject("PartDesign::Body", "Benchy")
body.AllowCompound = False
doc.recompute()
planes = {name: doc.getObject(name + "_Plane") for name in ("XY", "XZ", "YZ")}
axis = FreeCAD.Vector(0.0, 0.0, 1.0)


def sketch(name, plane="XY", offset=0.0):
    obj = body.newObject("Sketcher::SketchObject", name)
    obj.AttachmentSupport = [(planes[plane], "")]
    obj.MapMode = "FlatFace"
    obj.AttachmentOffset = FreeCAD.Placement(
        FreeCAD.Vector(0.0, 0.0, -offset if plane == "XZ" else offset), FreeCAD.Rotation()
    )
    doc.recompute()
    return obj


def vector(point):
    return FreeCAD.Vector(point[0], point[1], 0.0)


def blocked(obj, geometry):
    index = obj.addGeometry(geometry, False)
    obj.addConstraint(Sketcher.Constraint("Block", index))
    return index


def line(obj, a, b):
    index = obj.addGeometry(Part.LineSegment(vector(a), vector(b)), False)
    for endpoint, point in ((1, a), (2, b)):
        obj.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, index, endpoint, point[0]))
        obj.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, index, endpoint, point[1]))


def polygon(obj, points):
    for a, b in zip(points, points[1:] + points[:1]):
        line(obj, a, b)


def rectangle(obj, a, b, c, d):
    polygon(obj, [(a, b), (c, b), (c, d), (a, d)])


def circle(obj, x, y, diameter):
    index = obj.addGeometry(Part.Circle(vector((x, y)), axis, diameter / 2.0), False)
    obj.addConstraint(Sketcher.Constraint("Diameter", index, diameter))
    obj.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, index, 3, x))
    obj.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, index, 3, y))


def bezier(obj, points):
    curve = Part.BSplineCurve()
    curve.buildFromPolesMultsKnots([vector(p) for p in points], [4, 4], [0.0, 1.0], False, 3)
    blocked(obj, curve)


def validate(obj):
    doc.recompute()
    assert obj.isValid(), "infeasible: invalid feature " + obj.Name
    if obj.TypeId == "Sketcher::SketchObject":
        assert obj.FullyConstrained, "infeasible: unconstrained sketch " + obj.Name
    else:
        assert not obj.Shape.isNull(), "infeasible: empty feature " + obj.Name
        assert obj.Shape.isValid(), "infeasible: invalid shape " + obj.Name
        assert len(obj.Shape.Solids) == 1, "infeasible: disconnected feature " + obj.Name
    return obj


def prism(name, profile, length, kind="Pad", reverse=False):
    validate(profile)
    obj = body.newObject("PartDesign::" + kind, name)
    obj.Profile = profile
    obj.Length = length
    obj.Reversed = reverse
    obj.Refine = True
    return validate(obj)


def waterline(name, z, aft, bow, beam, stern, middle, half=False, existing=None):
    obj = existing if existing is not None else sketch(name, offset=z)
    # Two cubic arcs per side, with a common horizontal tangent at maximum beam.
    back = [(aft, stern), (aft + (middle - aft) * 0.35, beam), (middle - (middle - aft) * 0.35, beam), (middle, beam)]
    front = [(middle, beam), (middle + (bow - middle) * 0.50, beam), (bow, beam * 0.50), (bow, 0.0)]
    line(obj, (aft, 0.0), (aft, stern))
    bezier(obj, back)
    bezier(obj, front)
    if half:
        line(obj, (bow, 0.0), (aft, 0.0))
    else:
        bezier(obj, [(x, -y) for x, y in reversed(front)])
        bezier(obj, [(x, -y) for x, y in reversed(back)])
        line(obj, (aft, -stern), (aft, 0.0))
    return validate(obj)


def loft(name, profiles, subtract=False):
    obj = body.newObject("PartDesign::SubtractiveLoft" if subtract else "PartDesign::AdditiveLoft", name)
    obj.Profile = profiles[0]
    obj.Sections = profiles[1:]
    obj.Ruled = False
    obj.Refine = True
    return validate(obj)


def roof_z(x):
    return roofAtChimney + (x - chimneyCenterX) * roofSlope


# Extend the lower forebody and upper rocker independently of the stated openings.
# Datum body: filled hull, cabin, roof, chimney and aft cargo block.
profiles = []
for index, z in enumerate((0.0, sternGunwaleHeight, bowGunwaleHeight)):
    fraction = z / sternGunwaleHeight
    aft = keelAft * max(0.0, 1.0 - fraction)
    bow = keelBow + forebodyExtension + bowDerivative * z + bowQuadratic * z * z
    beam = hullKeelWidth / 2.0 + (overallWidth - hullKeelWidth) / 2.0 * min(1.0, fraction)
    stern = hullSternWidth / 2.0 * (0.70 + 0.30 * min(1.0, fraction))
    profiles.append(waterline("HullStation" + str(index), z, aft, bow, beam, stern, hullKeelCenterX, half=True))
hull = loft("SpoonHullHalf", profiles)


# FreeCAD chooses chord parameters for loft sections. Solve the middle station
# against the actual native lower-bow tangent, rather than assuming uniform z.
def lower_bow_angle():
    for edge in hull.Shape.Edges:
        first = edge.valueAt(edge.FirstParameter)
        last_point = edge.valueAt(edge.LastParameter)
        if (
            abs(first.y) < 0.00001
            and abs(last_point.y) < 0.00001
            and abs(first.z - last_point.z) > bowGunwaleHeight / 2.0
        ):
            parameter = edge.FirstParameter if first.z < last_point.z else edge.LastParameter
            point = edge.valueAt(parameter)
            if abs(point.x - keelBow - forebodyExtension) < 0.00001:
                tangent = edge.tangentAt(parameter)
                return math.degrees(math.atan2(abs(tangent.z), abs(tangent.x)))
    raise AssertionError("lower bow edge was not found by its datum coordinates")


middle_bow = keelBow + forebodyExtension + bowDerivative * sternGunwaleHeight + bowQuadratic * sternGunwaleHeight**2
previous_position = middle_bow
previous_angle = lower_bow_angle()
trial_position = middle_bow - 0.5
for iteration in range(7):
    if abs(lower_bow_angle() - bowOverhangAngle) < 0.00001:
        break
    station = profiles[1]
    while station.GeometryCount:
        station.delGeometry(station.GeometryCount - 1)
    waterline(
        "HullStation1",
        sternGunwaleHeight,
        0.0,
        trial_position,
        overallWidth / 2.0,
        hullSternWidth / 2.0,
        hullKeelCenterX,
        half=True,
        existing=station,
    )
    validate(hull)
    angle = lower_bow_angle()
    if abs(angle - bowOverhangAngle) < 0.00001:
        break
    next_position = trial_position + (bowOverhangAngle - angle) * (trial_position - previous_position) / (
        angle - previous_angle
    )
    previous_position, previous_angle = trial_position, angle
    trial_position = next_position
assert abs(lower_bow_angle() - bowOverhangAngle) < 0.005, "lower-bow tangent must meet the stated angle"
mirror = body.newObject("PartDesign::Mirrored", "HullMirror")
mirror.Originals = [hull]
mirror.MirrorPlane = (planes["XZ"], [""])
mirror.Refine = True
validate(mirror)
body.Tip = mirror
assert mirror.Shape.BoundBox.YMin < -hullKeelWidth / 2.0, "mirror did not produce the other half: " + str(
    mirror.PropertiesList
)

# Trim spline-interpolation overshoot to the exact finished beam and stern datum.
limit = sketch("EnvelopeTrim", offset=bowGunwaleHeight + overrun)
polygon(
    limit,
    [
        (-overallLength, -overallWidth),
        (overallLength + overrun, -overallWidth),
        (overallLength + overrun, -overallWidth / 2.0),
        (0.0, -overallWidth / 2.0),
        (0.0, overallWidth / 2.0),
        (overallLength + overrun, overallWidth / 2.0),
        (overallLength + overrun, overallWidth),
        (-overallLength, overallWidth),
    ],
)
prism("FinishedEnvelope", limit, bowGunwaleHeight + 2.0 * overrun, "Pocket")

sheer = sketch("SheerProfile", "XZ", -overallWidth)
bezier(
    sheer,
    [
        (0.0, sternGunwaleHeight),
        (overallLength / 3.0, sternGunwaleHeight),
        (2.0 * overallLength / 3.0, bowGunwaleHeight),
        (overallLength, bowGunwaleHeight),
    ],
)
line(sheer, (overallLength, bowGunwaleHeight), (overallLength + overrun, bowGunwaleHeight + overrun))
line(sheer, (overallLength + overrun, bowGunwaleHeight + overrun), (overallLength + overrun, overallHeight))
line(sheer, (overallLength + overrun, overallHeight), (-overrun, overallHeight))
line(sheer, (-overrun, overallHeight), (-overrun, sternGunwaleHeight))
line(sheer, (-overrun, sternGunwaleHeight), (0.0, sternGunwaleHeight))
prism("RaisedBowSheer", sheer, 2.0 * overallWidth, "Pocket")

well_bottom = waterline(
    "WellFloor",
    deckHeight,
    keelAft * max(0.0, 1.0 - deckHeight / sternGunwaleHeight) + hullWallThickness,
    keelBow + forebodyExtension + bowDerivative * deckHeight + bowQuadratic * deckHeight**2 - hullWallThickness,
    hullKeelWidth / 2.0 + (overallWidth - hullKeelWidth) / 2.0 * deckHeight / sternGunwaleHeight - hullWallThickness,
    hullSternWidth / 2.0 - hullWallThickness,
    hullKeelCenterX,
)
well_top = waterline(
    "WellMouth",
    bowGunwaleHeight + 2.0,
    hullWallThickness,
    overallLength - hullWallThickness,
    overallWidth / 2.0 - hullWallThickness,
    hullSternWidth / 2.0 - hullWallThickness,
    hullKeelCenterX,
)
loft("OpenDeckWell", [well_bottom, well_top], subtract=True)

cabin = sketch("CabinFootprint", offset=deckHeight - overrun)
rectangle(cabin, cabinAft, -cabinWidth / 2.0, cabinBow, cabinWidth / 2.0)
prism("CabinStock", cabin, roof_z(cabinBow) - bridgeRoofThickness - deckHeight + overrun)
trim = sketch("CabinRoofTrim", "XZ", -overallWidth)
polygon(
    trim,
    [
        (cabinAft - overrun, roof_z(cabinAft - overrun) - bridgeRoofThickness),
        (cabinBow + overrun, roof_z(cabinBow + overrun) - bridgeRoofThickness),
        (cabinBow + overrun, overallHeight),
        (cabinAft - overrun, overallHeight),
    ],
)
prism("SlopingCabinTop", trim, 2.0 * overallWidth, "Pocket")

inside = sketch("CabinInteriorProfile", "XZ", -cabinWidth / 2.0 + cabinWallThickness)
inner_aft = cabinAft + cabinWallThickness
inner_bow = cabinBow - cabinWallThickness
polygon(
    inside,
    [
        (inner_aft, deckHeight),
        (inner_bow, deckHeight),
        (inner_bow, roof_z(inner_bow) - bridgeRoofThickness + overrun),
        (inner_aft, roof_z(inner_aft) - bridgeRoofThickness + overrun),
    ],
)
prism("HollowCabin", inside, cabinWidth - 2.0 * cabinWallThickness, "Pocket")

roof = sketch("RoofSection", "XZ", bridgeRoofWidth / 2.0)
polygon(
    roof,
    [
        (roofAft, roof_z(roofAft) - bridgeRoofThickness),
        (roofBow, roof_z(roofBow) - bridgeRoofThickness),
        (roofBow, roof_z(roofBow)),
        (roofAft, roof_z(roofAft)),
    ],
)
prism("BridgeRoof", roof, bridgeRoofWidth)

stem = sketch("ChimneyStemProfile", offset=roofAtChimney - bridgeRoofThickness / 2.0)
circle(stem, chimneyCenterX, 0.0, chimneyStemDiameter)
prism("ChimneyStem", stem, overallHeight - chimneyCollarHeight - roofAtChimney + bridgeRoofThickness / 2.0)
collar = sketch("ChimneyCollarProfile", offset=overallHeight - chimneyCollarHeight)
circle(collar, chimneyCenterX, 0.0, chimneyOuterDiameter)
prism("ChimneyCollar", collar, chimneyCollarHeight)

cargo = sketch("CargoBoxOutside", offset=deckHeight - overrun)
rectangle(
    cargo,
    cargoBoxCenterX - cargoBoxOuterB / 2.0,
    -cargoBoxOuterA / 2.0,
    cargoBoxCenterX + cargoBoxOuterB / 2.0,
    cargoBoxOuterA / 2.0,
)
prism("CargoBoxStock", cargo, cargoBoxTopHeight - deckHeight + overrun)

box_hole = sketch("CargoCavityProfile", offset=cargoBoxTopHeight)
rectangle(
    box_hole,
    cargoBoxCenterX - cargoBoxInnerB / 2.0,
    -cargoBoxInnerA / 2.0,
    cargoBoxCenterX + cargoBoxInnerB / 2.0,
    cargoBoxInnerA / 2.0,
)
prism("CargoCavity", box_hole, cargoBoxDepth, "Pocket")
chimney_hole = sketch("ChimneyBoreProfile", offset=overallHeight)
circle(chimney_hole, chimneyCenterX, 0.0, chimneyInnerDiameter)
prism("BlindChimneyBore", chimney_hole, chimneyHoleDepth, "Pocket")

# The two end windows and one through-pocket for the opposed arched side openings.
front = sketch("FrontWindowProfile", "YZ", cabinBow + overrun)
rectangle(
    front,
    -frontWindowWidth / 2.0,
    windowCenterHeight - frontWindowHeight / 2.0,
    frontWindowWidth / 2.0,
    windowCenterHeight + frontWindowHeight / 2.0,
)
prism("FrontWindow", front, cabinWallThickness + 2.0 * overrun, "Pocket")
rear_flange = sketch("RearWindowFlangeProfile", "YZ", cabinAft - rearWindowFlangeDepth)
circle(rear_flange, 0.0, windowCenterHeight, rearWindowOuterDiameter)
prism("RearWindowFlange", rear_flange, rearWindowFlangeDepth + cabinWallThickness / 2.0)
rear = sketch("RearWindowProfile", "YZ", cabinAft - rearWindowFlangeDepth - overrun)
circle(rear, 0.0, windowCenterHeight, rearWindowInnerDiameter)
prism("RearWindow", rear, rearWindowFlangeDepth + cabinWallThickness + 2.0 * overrun, "Pocket", True)

arch_radius = sideOpeningWidth / 2.0
arch_center = deckHeight + sideOpeningHeight - arch_radius
arch_left = cabinCenterX - arch_radius
arch_right = cabinCenterX + arch_radius
side = sketch("SideOpeningProfile", "XZ", -cabinWidth / 2.0 - overrun)
line(side, (arch_left, deckHeight), (arch_right, deckHeight))
line(side, (arch_right, deckHeight), (arch_right, arch_center))
blocked(side, Part.ArcOfCircle(Part.Circle(vector((cabinCenterX, arch_center)), axis, arch_radius), 0.0, math.pi))
line(side, (arch_left, arch_center), (arch_left, deckHeight))
prism("SideOpenings", side, cabinWidth + 2.0 * overrun, "Pocket")

# Locate the two mouths from the actual wall intersections along the bore axis.
axis_material = body.Shape.common(
    Part.makeLine(
        FreeCAD.Vector(hawsepipeCenterX, -overallWidth, hawsepipeCenterZ),
        FreeCAD.Vector(hawsepipeCenterX, overallWidth, hawsepipeCenterZ),
    )
)
hawse_halfbeam = max(abs(vertex.Point.y) for vertex in axis_material.Vertexes)
for label, sign in (("Port", 1.0), ("Starboard", -1.0)):
    ring = sketch("HawseFlange" + label + "Profile", "XZ", sign * (hawse_halfbeam + hawsepipeFlangeDepth))
    circle(ring, hawsepipeCenterX, hawsepipeCenterZ, hawsepipeOuterDiameter)
    prism("HawseFlange" + label, ring, 2.0 * hullWallThickness + hawsepipeFlangeDepth, reverse=sign < 0.0)
hawse = sketch("HawsepipeProfile", "XZ", -overallWidth)
circle(hawse, hawsepipeCenterX, hawsepipeCenterZ, hawsepipeInnerDiameter)
last = prism("Hawsepipe", hawse, 2.0 * overallWidth, "Pocket")
last.Refine = True
body.Tip = last
doc.recompute()
for feature in body.Group:
    assert feature.isValid(), "invalid final feature: " + feature.Name
assert body.Shape.isValid() and len(body.Shape.Solids) == 1, "final solid must be valid and connected"
result = body

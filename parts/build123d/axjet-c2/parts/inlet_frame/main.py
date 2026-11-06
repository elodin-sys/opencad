import math

from build123d import (
    Align,
    Axis,
    Compound,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    Rot,
    SkipClean,
    extrude,
    make_face,
    revolve,
)

frontFlangeFrontZ = -72.0
frontFlangeRearZ = -67.0
frontFlangeDia = 224.0
frontBoltPcd = 216.0
frontBoltCount = 8
frontBoltDia = 5.5
ellipseCentreZ = -45.0
ellipseCentreR = 125.0
ellipseAxial = 50.0
ellipseRadial = 34.75
frontContourRadius = 95.752
ductRadius = 90.25
ductOuterRadius = 100.0
rearFlangeFrontZ = -24.0
rearFlangeRearZ = -18.0
rearFlangeDia = 224.0
rearBoltPcd = 212.0
rearBoltCount = 8
rearBoltDia = 5.5
hubRadius = 32.0
hubFrontZ = -80.0
fairingStartZ = -40.0
bearingBoreDia = 52.0
bearingBoreFrontZ = -75.0
bearingBoreRearZ = -35.0
frontWallBoreDia = 40.0
noseScrewPcd = 56.0
noseScrewCount = 4
noseScrewTapDia = 2.5
noseScrewDepth = 6.0
noseScrewClock = 45.0
fairingThickness = 3.0
fairingRadius = 57.6
fairingShoulderZ = -15.0
fairingRearZ = -11.0
sealBoreDia = 97.0
sealFrontZ = -21.0
sealSleeveWall = 3.0
strutCount = 5
strutLeadZ = -70.0
strutChord = 30.0
strutThickness = 6.0


def ellipse_radius(z):
    u = (z - ellipseCentreZ) / ellipseAxial
    assert abs(u) <= 1.0, "infeasible: station is outside the bellmouth ellipse"
    return ellipseCentreR - ellipseRadial * math.sqrt(1.0 - u * u)


strutPitch = 360.0 / strutCount
strutTrailZ = strutLeadZ + strutChord

assert strutThickness > 0.0, "infeasible: strutThickness must be positive"
assert ductOuterRadius > ellipse_radius(frontFlangeRearZ), "infeasible: duct outer wall crosses the bellmouth contour"

coneDr = fairingRadius - hubRadius
coneDz = fairingShoulderZ - fairingStartZ
coneLen = math.hypot(coneDr, coneDz)
# Inward normal of the rising cone points to smaller r and larger z.
innerR0 = hubRadius - fairingThickness * coneDz / coneLen
innerZ0 = fairingStartZ + fairingThickness * coneDr / coneLen
coneSlope = coneDr / coneDz


def inner_radius(z):
    return innerR0 + coneSlope * (z - innerZ0)


def outer_radius(z):
    if z >= fairingShoulderZ:
        return fairingRadius
    return hubRadius + coneSlope * (z - fairingStartZ)


def z_on_inner(r):
    return innerZ0 + (r - innerR0) / coneSlope


sealRadius = sealBoreDia / 2.0
sleeveOuterRadius = sealRadius + sealSleeveWall
fairingInnerRadius = fairingRadius - fairingThickness
zSleeveOuter = z_on_inner(sleeveOuterRadius)
zFairingInner = z_on_inner(fairingInnerRadius)
strutRootRadius = (bearingBoreDia / 2.0 + hubRadius) / 2.0
strutTipRadius = ductOuterRadius - 1.5

assert sealFrontZ < zSleeveOuter < zFairingInner < fairingRearZ, (
    "infeasible: seal sleeve does not meet the fairing shell"
)
assert inner_radius(sealFrontZ) < sealRadius, "infeasible: seal bore misses the fairing cone"
assert inner_radius(bearingBoreRearZ) > bearingBoreDia / 2.0, "infeasible: hub rear face has no area"
assert bearingBoreDia / 2.0 < strutRootRadius < hubRadius
assert strutTipRadius > ellipse_radius(strutLeadZ), "infeasible: strut tip does not reach the duct wall"
assert frontBoltPcd / 2.0 + frontBoltDia / 2.0 < frontFlangeDia / 2.0
assert frontBoltPcd / 2.0 - frontBoltDia / 2.0 > frontContourRadius
assert rearBoltPcd / 2.0 + rearBoltDia / 2.0 < rearFlangeDia / 2.0
assert rearBoltPcd / 2.0 - rearBoltDia / 2.0 > ductOuterRadius, "infeasible: rear bolt breaks into the duct wall"
assert noseScrewPcd / 2.0 - noseScrewTapDia / 2.0 > bearingBoreDia / 2.0
assert noseScrewPcd / 2.0 + noseScrewTapDia / 2.0 < hubRadius
assert hubFrontZ < bearingBoreFrontZ < fairingStartZ < bearingBoreRearZ
assert bearingBoreRearZ < fairingShoulderZ < fairingRearZ
assert frontFlangeFrontZ < frontFlangeRearZ < rearFlangeFrontZ < rearFlangeRearZ < fairingRearZ


def revolved_profile(points):
    wire = Polyline(*[(r, z) for r, z in points], close=True)
    # clean=False: UnifySameDomain on a 360 revolve makes a solid booleans cannot cut.
    return revolve(Plane.XZ * make_face(wire), axis=Axis.Z, clean=False)


def duct_points():
    z0 = frontFlangeFrontZ
    z1 = ellipseCentreZ
    count = 64
    stations = [z0 + (z1 - z0) * i / count for i in range(count + 1)]
    for z in (z0 + 1.0, frontFlangeRearZ, strutLeadZ + strutChord / 2.0):
        if z0 < z < z1:
            stations.append(z)
    stations = sorted(stations)
    unique = [stations[0]]
    for z in stations[1:]:
        if z - unique[-1] > 1e-9:
            unique.append(z)
    points = [(ellipse_radius(z), z) for z in unique]
    points[-1] = (ductRadius, ellipseCentreZ)
    points.extend(
        [
            (ductRadius, rearFlangeRearZ),
            (rearFlangeDia / 2.0, rearFlangeRearZ),
            (rearFlangeDia / 2.0, rearFlangeFrontZ),
            (ductOuterRadius, rearFlangeFrontZ),
            (ductOuterRadius, frontFlangeRearZ),
            (frontFlangeDia / 2.0, frontFlangeRearZ),
            (frontFlangeDia / 2.0, frontFlangeFrontZ),
        ]
    )
    return points


jointOverlap = 0.05


def hub_core_points():
    return [
        (hubRadius, hubFrontZ),
        (hubRadius, fairingStartZ),
        (outer_radius(bearingBoreRearZ), bearingBoreRearZ),
        (bearingBoreDia / 2.0, bearingBoreRearZ),
        (bearingBoreDia / 2.0, bearingBoreFrontZ),
        (frontWallBoreDia / 2.0, bearingBoreFrontZ),
        (frontWallBoreDia / 2.0, hubFrontZ),
    ]


def shell_points():
    # Buried 2 mm into the solid hub so the fuse has a real volume overlap.
    z_buried = bearingBoreRearZ - 2.0
    return [
        (outer_radius(z_buried) - 0.4, z_buried),
        (outer_radius(bearingBoreRearZ), bearingBoreRearZ),
        (fairingRadius, fairingShoulderZ),
        (fairingRadius, fairingRearZ),
        (fairingInnerRadius, fairingRearZ),
        (fairingInnerRadius, zFairingInner),
        (inner_radius(bearingBoreRearZ), bearingBoreRearZ),
        (inner_radius(z_buried), z_buried),
    ]


def sleeve_points():
    # Starts aft of the seal face; the shell carries the bore ledge at sealFrontZ.
    z0 = sealFrontZ + 0.2
    return [
        (sleeveOuterRadius, z0),
        (sleeveOuterRadius, fairingRearZ),
        (sealRadius - jointOverlap, fairingRearZ),
        (sealRadius - jointOverlap, z0),
    ]


def naca_half(xc):
    # a4 = -0.1036 closes the trailing edge (thickness is 0 at xc = 1).
    poly = 0.2969 * math.sqrt(xc) - 0.1260 * xc - 0.3516 * xc * xc + 0.2843 * xc**3 - 0.1036 * xc**4
    return 5.0 * strutThickness * poly


def airfoil_points():
    count = 24
    fractions = [0.5 * (1.0 - math.cos(math.pi * i / count)) for i in range(count + 1)]
    if all(abs(xc - 0.3) > 1e-9 for xc in fractions):
        fractions.append(0.3)
    fractions.sort()
    upper = [(naca_half(xc), strutLeadZ + xc * strutChord) for xc in fractions]
    return upper + [(-y, z) for y, z in reversed(upper[1:-1])]


def strut_prism():
    wire = Polyline(*airfoil_points(), close=True)
    face = Pos(strutRootRadius, 0, 0) * (Plane.YZ * make_face(wire))
    return extrude(face, strutTipRadius - strutRootRadius, dir=(1, 0, 0))


def hole_pattern(count, pcd, z0, diameter, depth, clock):
    radius = pcd / 2.0
    holes = []
    for i in range(int(count)):
        ang = math.radians(clock + i * (360.0 / count))
        holes.append(
            Pos(radius * math.cos(ang), radius * math.sin(ang), z0)
            * Cylinder(
                diameter / 2.0,
                depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        )
    return holes


duct = revolved_profile(duct_points())
_core = revolved_profile(hub_core_points())
_shell = revolved_profile(shell_points())
_sleeve = revolved_profile(sleeve_points())
with SkipClean():
    hub = _core + _shell
    _mid = [round(solid.volume) for solid in hub.solids()]
    hub = hub + _sleeve
    hub = hub - (
        Pos(0, 0, sealFrontZ)
        * Cylinder(
            sealRadius,
            (fairingRearZ - sealFrontZ) + jointOverlap,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
_hub_box = hub.bounding_box()
_vols = [solid.volume for solid in hub.solids()]
assert sum(_vols) > 80000.0 and len(_vols) == 1, (
    f"mid {_mid} n {len(_vols)} vols {[round(v) for v in _vols]} z {_hub_box.min.Z:.2f} {_hub_box.max.Z:.2f}"
)
_duct_box = duct.bounding_box()
assert abs(_duct_box.min.Z - frontFlangeFrontZ) < 0.05, (
    f"duct bbox {_duct_box.min.Z:.3f} {_duct_box.max.Z:.3f} vol {duct.volume:.1f}"
)
master = strut_prism()
strutBox = master.bounding_box()
assert abs(strutBox.min.X - strutRootRadius) < 0.05, "strut root radius"
assert abs(strutBox.max.X - strutTipRadius) < 0.05, "strut tip radius"
assert abs(strutBox.min.Z - strutLeadZ) < 0.05, "strut leading edge"
assert abs(strutBox.max.Z - strutTrailZ) < 0.05, "strut trailing edge"
assert abs(strutBox.max.Y - strutThickness / 2.0) < 0.05, "strut thickness"

struts = [Rot(0, 0, i * strutPitch) * master for i in range(int(strutCount))]
with SkipClean():
    # Move the revolve seams off the strut center-planes. Both bodies are axisymmetric.
    body = Rot(0, 0, 17) * hub
    for strut in struts:
        body += strut
    body += Rot(0, 0, 23) * duct
_fused = body.bounding_box()
assert len(body.solids()) == 1 and abs(_fused.min.Z - hubFrontZ) < 0.05, (
    f"fused solids {len(body.solids())} vol {body.volume:.0f} z {_fused.min.Z:.2f} {_fused.max.Z:.2f}"
)

cutterOverrun = 0.02
cutters = hole_pattern(
    frontBoltCount,
    frontBoltPcd,
    frontFlangeFrontZ - cutterOverrun,
    frontBoltDia,
    (frontFlangeRearZ - frontFlangeFrontZ) + 2.0 * cutterOverrun,
    0.0,
)
cutters += hole_pattern(
    rearBoltCount,
    rearBoltPcd,
    rearFlangeFrontZ - cutterOverrun,
    rearBoltDia,
    (rearFlangeRearZ - rearFlangeFrontZ) + 2.0 * cutterOverrun,
    0.0,
)
cutters += hole_pattern(
    noseScrewCount,
    noseScrewPcd,
    hubFrontZ - cutterOverrun,
    noseScrewTapDia,
    noseScrewDepth + cutterOverrun,
    noseScrewClock,
)
with SkipClean():
    result = body - Compound(cutters)

assert len(result.solids()) == 1, "inlet frame must be a single solid"
bounds = result.bounding_box()
_bbox = (
    bounds.min.X,
    bounds.min.Y,
    bounds.min.Z,
    bounds.max.X,
    bounds.max.Y,
    bounds.max.Z,
)
assert abs(bounds.min.Z - hubFrontZ) < 0.05, f"bbox min z {_bbox}"
assert abs(bounds.max.Z - fairingRearZ) < 0.05, f"bbox max z {_bbox}"
assert abs(bounds.max.X - frontFlangeDia / 2.0) < 0.05, f"bbox max x {_bbox}"
assert abs(bounds.min.X + frontFlangeDia / 2.0) < 0.05, f"bbox min x {_bbox}"
assert abs(bounds.max.Y - frontFlangeDia / 2.0) < 0.05, f"bbox max y {_bbox}"
assert abs(bounds.min.Y + frontFlangeDia / 2.0) < 0.05, f"bbox min y {_bbox}"

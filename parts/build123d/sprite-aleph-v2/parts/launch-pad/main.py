import math

from build123d import (
    Align,
    Box,
    CenterArc,
    Compound,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    extrude,
    make_face,
    mirror,
)

armSpanX = 170.0
armSpanY = 150.0
padHeight = 100.0
armWidth = 30.0
armEndRadius = 10.0
junctionRadius = 5.0
flangeThickness = 5.0
floorThickness = 1.2
cupOuterRadius = 28.89
cupFlatHalfLength = 13.69
wallThickness = 1.2
cupInnerRadius = cupOuterRadius - wallThickness
sideWallHeight = 58.54
shelfHeight = 73.53
cradleHalfWidth = 31.37
cradleArcRadius = 36.48
cradleArcDepth = 7.66
ribThickness = 5.0
ribTopRadius = ribThickness / 2.0
ribRise = 38.21
ribRunX = 32.91
ribRunY = 32.42
plugNotchHalfWidth = 24.5
plugNotchFloorZ = -27.0

assert ribThickness > 0.0, "infeasible: ribThickness must be positive"
assert armSpanX / 2.0 >= cupOuterRadius + ribRunX, "infeasible: x arm does not cover the gusset toe"
assert armSpanY / 2.0 >= cupFlatHalfLength + cupOuterRadius + ribRunY, "infeasible: y arm does not cover the gusset toe"
assert 0.0 < floorThickness < flangeThickness, "infeasible: floor must sit inside the flange"
assert sideWallHeight < shelfHeight < padHeight, "infeasible: wall, shelf and tip heights cross"
assert 2.0 * armEndRadius < armWidth, "infeasible: arm end radius consumes the arm"
assert cupOuterRadius > wallThickness, "infeasible: wall thicker than the cup radius"
assert ribThickness < armWidth, "infeasible: gusset thicker than the arm"
assert cradleArcRadius > cradleHalfWidth, "infeasible: cradle arc does not cross the cup axis"

assert 0.0 < plugNotchHalfWidth < cupInnerRadius, "infeasible: notch consumes the cap-wall seats"
assert -padHeight + sideWallHeight < plugNotchFloorZ < -padHeight + shelfHeight, (
    "infeasible: notch floor crosses retained wall or shelf"
)
assert 0.0 < wallThickness, "infeasible: wallThickness must be positive"
assert 0.0 < junctionRadius, "infeasible: junctionRadius must be positive"

_z_shelf = -padHeight + shelfHeight
_dz_arc = _z_shelf + cradleArcDepth
assert cradleArcRadius * cradleArcRadius > _dz_arc * _dz_arc, "infeasible: cradle arc does not reach the shelf"


def _ang(dx, dy):
    return math.degrees(math.atan2(dy, dx))


def _sweep_ccw(start, end):
    return (end - start) % 360.0


def _sweep_cw(start, end):
    sweep = -((start - end) % 360.0)
    if abs(sweep) < 1e-9:
        return -360.0
    return sweep


def _on_circle(center, radius, angle_deg):
    angle = math.radians(angle_deg)
    return (
        center[0] + radius * math.cos(angle),
        center[1] + radius * math.sin(angle),
    )


def stadium_face(radius, half_length):
    edges = [
        Polyline((radius, -half_length), (radius, half_length)),
        CenterArc((0.0, half_length), radius, 0.0, 180.0),
        Polyline((-radius, half_length), (-radius, -half_length)),
        CenterArc((0.0, -half_length), radius, 180.0, 180.0),
    ]
    return make_face(edges)


def footprint_face():
    """Cross flange outline in one quadrant, then mirrored. R10 ends, R5 junctions."""
    x_tip = armSpanX / 2.0
    y_tip = armSpanY / 2.0
    aw = armWidth / 2.0
    er = armEndRadius
    jr = junctionRadius
    cap = (0.0, cupFlatHalfLength)

    fillet_y = aw + jr
    fillet_dx = math.sqrt((cupOuterRadius + jr) ** 2 - (fillet_y - cupFlatHalfLength) ** 2)
    fillet_x = (fillet_dx, fillet_y)
    fillet_xcoord = aw + jr
    fillet_dy = math.sqrt((cupOuterRadius + jr) ** 2 - fillet_xcoord**2)
    fillet_arm = (fillet_xcoord, cupFlatHalfLength + fillet_dy)

    def _toward_cap(fillet):
        ux = fillet[0] - cap[0]
        uy = fillet[1] - cap[1]
        length = math.hypot(ux, uy)
        return (cap[0] + cupOuterRadius * ux / length, cap[1] + cupOuterRadius * uy / length)

    tan_x = _toward_cap(fillet_x)
    tan_y = _toward_cap(fillet_arm)
    line_x = (fillet_x[0], aw)
    line_y = (aw, fillet_arm[1])

    edges = [
        Polyline((x_tip, 0.0), (x_tip, aw - er)),
        CenterArc((x_tip - er, aw - er), er, 0.0, 90.0),
        Polyline((x_tip - er, aw), line_x),
        CenterArc(
            fillet_x,
            jr,
            -90.0,
            _sweep_cw(-90.0, _ang(tan_x[0] - fillet_x[0], tan_x[1] - fillet_x[1])),
        ),
        CenterArc(
            cap,
            cupOuterRadius,
            _ang(tan_x[0] - cap[0], tan_x[1] - cap[1]),
            _sweep_ccw(
                _ang(tan_x[0] - cap[0], tan_x[1] - cap[1]),
                _ang(tan_y[0] - cap[0], tan_y[1] - cap[1]),
            ),
        ),
        CenterArc(
            fillet_arm,
            jr,
            _ang(tan_y[0] - fillet_arm[0], tan_y[1] - fillet_arm[1]),
            _sweep_cw(
                _ang(tan_y[0] - fillet_arm[0], tan_y[1] - fillet_arm[1]),
                _ang(line_y[0] - fillet_arm[0], line_y[1] - fillet_arm[1]),
            ),
        ),
        Polyline(line_y, (aw, y_tip - er)),
        CenterArc((aw - er, y_tip - er), er, 0.0, 90.0),
        Polyline((aw - er, y_tip), (0.0, y_tip)),
        Polyline((0.0, y_tip), (0.0, 0.0)),
        Polyline((0.0, 0.0), (x_tip, 0.0)),
    ]
    quadrant = make_face(edges)
    half = quadrant + mirror(quadrant, Plane.XZ)
    return half + mirror(half, Plane.YZ)


def _quad(points):
    edges = [Polyline(points[i], points[(i + 1) % len(points)]) for i in range(len(points))]
    return make_face(edges)


def _rounded_prism(plane, profile, crest_a, crest_b):
    """Extrude a vertical gusset profile and replace the ridge with a full round."""
    sharp = extrude(plane.location * profile, ribThickness / 2.0, both=True)
    dx = crest_b[0] - crest_a[0]
    dy = crest_b[1] - crest_a[1]
    dz = crest_b[2] - crest_a[2]
    length = math.hypot(dx, dy, dz)
    # Thickness direction is D × Z; the outward normal is that crossed back into D.
    tx, ty = dy, -dx
    ox = ty * dz
    oy = -tx * dz
    oz = tx * dy - ty * dx
    normal = math.hypot(ox, oy, oz)
    outward = (ox / normal, oy / normal, oz / normal)
    mid = (
        (crest_a[0] + crest_b[0]) / 2.0,
        (crest_a[1] + crest_b[1]) / 2.0,
        (crest_a[2] + crest_b[2]) / 2.0,
    )
    axis = tuple(mid[i] - ribTopRadius * outward[i] for i in range(3))
    slope = (dx / length, dy / length, dz / length)
    frame = Plane(origin=axis, x_dir=outward, z_dir=slope)
    reach = ribTopRadius + 6.0
    cutter_box = (
        frame.location
        * Pos(reach / 2.0 - 0.02, 0.0, 0.0)
        * Box(
            reach,
            ribThickness + 2.0,
            length + 4.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
    )
    cutter_cyl = frame.location * Cylinder(
        ribTopRadius,
        length + 4.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    return sharp - (cutter_box - cutter_cyl)


def _x_gusset(sign):
    z_base = -padHeight + flangeThickness
    sink = 0.03
    embed = min(0.4, wallThickness * 0.45)
    toe_x = sign * (cupOuterRadius + ribRunX)
    root_x = sign * cupOuterRadius
    root_ext = sign * (cupOuterRadius - embed)
    run = abs(toe_x - root_x)
    t_ext = abs(toe_x - root_ext) / run
    z_ext = z_base + t_ext * ribRise
    profile = _quad(
        [
            (toe_x, z_base - sink),
            (root_ext, z_base - sink),
            (root_ext, z_ext),
            (toe_x, z_base),
        ]
    )
    crest_toe = (toe_x, 0.0, z_base)
    crest_root = (root_ext, 0.0, z_ext)
    # Plane.XZ maps sketch (x, y) onto global (x, z).
    return _rounded_prism(Plane.XZ, profile, crest_toe, crest_root)


def _y_gusset():
    z_base = -padHeight + flangeThickness
    sink = 0.03
    apex = cupFlatHalfLength + cupOuterRadius
    half_t = ribThickness / 2.0
    # Root face sits mid-wall across the gusset thickness. The crest is the
    # apex slope extended back into that face, so nothing sticks outside the cap.
    y_outer = cupFlatHalfLength + math.sqrt(cupOuterRadius**2 - half_t**2)
    y_inner = cupFlatHalfLength + math.sqrt(cupInnerRadius**2 - half_t**2)
    root_y = (y_outer + y_inner) / 2.0
    toe_y = apex + ribRunY
    run = toe_y - apex
    t_ext = (toe_y - root_y) / run
    z_ext = z_base + t_ext * ribRise
    profile = _quad(
        [
            (toe_y, z_base - sink),
            (root_y, z_base - sink),
            (root_y, z_ext),
            (toe_y, z_base),
        ]
    )
    # Plane.YZ maps sketch (x, y) onto global (y, z).
    return _rounded_prism(
        Plane.YZ,
        profile,
        (0.0, toe_y, z_base),
        (0.0, root_y, z_ext),
    )


def cradle_cutter():
    z_shelf = -padHeight + shelfHeight
    z_tan = -cradleArcDepth
    z_over = 0.05
    radius = cradleArcRadius
    center_y = cradleHalfWidth - radius
    center = (center_y, z_tan)
    center_neg = (-center_y, z_tan)
    dz = z_shelf - z_tan
    dy = math.sqrt(radius * radius - dz * dz)
    a_shelf = _ang(dy, dz)
    a_shelf_neg = _ang(-dy, dz)
    p_top = _on_circle(center, radius, 0.0)
    p_shelf = _on_circle(center, radius, a_shelf)
    p_top_neg = _on_circle(center_neg, radius, 180.0)
    p_shelf_neg = _on_circle(center_neg, radius, a_shelf_neg)
    edges = [
        Polyline((-p_top[0], z_over), (p_top[0], z_over)),
        Polyline((p_top[0], z_over), p_top),
        CenterArc(center, radius, 0.0, _sweep_cw(0.0, a_shelf)),
        Polyline(p_shelf, p_shelf_neg),
        CenterArc(center_neg, radius, a_shelf_neg, _sweep_cw(a_shelf_neg, 180.0)),
        Polyline(p_top_neg, (-p_top[0], z_over)),
    ]
    profile = Plane.YZ.location * make_face(edges)
    return extrude(profile, cupOuterRadius + 4.0, both=True)


z_flange_top = -padHeight + flangeThickness
flange = Pos(0.0, 0.0, -padHeight) * extrude(footprint_face(), flangeThickness)
cavity_height = flangeThickness - floorThickness + 0.05
cavity = Pos(0.0, 0.0, -padHeight + floorThickness) * extrude(
    stadium_face(cupInnerRadius, cupFlatHalfLength),
    cavity_height,
)
body = flange - cavity

wall_overlap = 0.05
ring = stadium_face(cupOuterRadius, cupFlatHalfLength) - stadium_face(cupInnerRadius, cupFlatHalfLength)
wall = Pos(0.0, 0.0, z_flange_top - wall_overlap) * extrude(ring, padHeight - flangeThickness + wall_overlap)
body = body + wall

z_window = -padHeight + sideWallHeight
window_dx = wallThickness + 0.1
window_dz = 0.05 - z_window
window_z = (z_window + 0.05) / 2.0
window_x = (cupInnerRadius + cupOuterRadius) / 2.0
windows = Compound(
    [
        Pos(window_x, 0.0, window_z) * Box(window_dx, 2.0 * cupFlatHalfLength, window_dz),
        Pos(-window_x, 0.0, window_z) * Box(window_dx, 2.0 * cupFlatHalfLength, window_dz),
    ]
)
body = body - windows
body = body - cradle_cutter()


def _apex_slots():
    # Apex-plane samples and the opposite root face are 2 mm apart. The slot
    # face sits on the mid plane, 1 mm from each.
    apex = cupFlatHalfLength + cupOuterRadius
    y_inner = cupFlatHalfLength + cupInnerRadius
    # Mesh apex sits 0.0035228 mm outside the rounded parameter sum.
    y_face = apex - 1.0 + 0.0035228
    y0 = y_inner - 0.3
    z0 = -padHeight + flangeThickness - 0.8
    z1 = z0 + ribRise + 2.0
    slots = []
    for sign in (1.0, -1.0):
        slots.append(Pos(0.0, sign * (y0 + y_face) / 2.0, (z0 + z1) / 2.0) * Box(4.0, y_face - y0, z1 - z0))
    return Compound(slots)


def _plug_notches():
    """Open-top plug/lead/PCB clearance; the historical z=0 datum stays fixed."""
    y_start = 20.0
    y_end = cupFlatHalfLength + cupOuterRadius + 0.05
    z_over = 0.05
    return Compound(
        [
            Pos(0.0, sign * (y_start + y_end) / 2.0, (plugNotchFloorZ + z_over) / 2.0)
            * Box(2.0 * plugNotchHalfWidth, y_end - y_start, z_over - plugNotchFloorZ)
            for sign in (1.0, -1.0)
        ]
    )


# Retain the seed gussets, rounded ridges and symmetric apex reliefs verbatim.
gusset_y = _y_gusset()
gussets = _x_gusset(1.0) + _x_gusset(-1.0) + gusset_y + mirror(gusset_y, Plane.XZ)
seed = body + gussets - _apex_slots()
result = seed - _plug_notches()

assert result.is_valid, "launch pad must be a valid solid"
assert len(result.solids()) == 1, "launch pad must remain one connected solid"
for seat_x in (-25.0, 25.0):
    for seat_y in (-27.0, 27.0):
        assert any(solid.is_inside((seat_x, seat_y, -25.0)) for solid in result.solids()), (
            "cradle seat contact was removed"
        )

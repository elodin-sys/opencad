"""Partial hotend channel and retention grooves, retaining original stock lips."""

from math import atan2, cos, degrees, hypot, pi, sin, sqrt

from build123d import (
    Align,
    Axis,
    Box,
    Circle,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    Rot,
    SkipClean,
    ThreePointArc,
    Vector,
    extrude,
    loft,
    make_face,
    revolve,
)
from params import (
    bodyTopZ,
    bottomZ,
    clampAxialLipDiameter,
    clampAxisX,
    clampCenterY,
    clampCornerAxisX,
    clampCornerAxisZ,
    clampCornerEnd,
    clampCornerFarY,
    clampCornerLipDiameter,
    clampCornerNearY,
    clampCornerOffsetDiameter,
    clampCornerOffsetLipDiameter,
    clampCornerOffsetX,
    clampCornerOffsetZ,
    clampCornerOuterDiameter,
    clampCornerStart,
    clampEndZ,
    clampFarLipDiameter,
    clampFarLipStart,
    clampFarY,
    clampInnerDiameter,
    clampNearY,
    clampOffsetDiameter,
    clampOffsetX,
    clampOuterDiameter,
    clampReliefDiameter,
    clampStartZ,
    clampTiltAxisX,
    clampTiltAxisZ,
    clampTiltDirX,
    clampTiltDirZ,
    clampTiltEnd,
    clampTiltInnerX,
    clampTiltInnerZ,
    clampTiltNearEnd,
    clampTiltStart,
    clampUpperInnerX,
    clampUpperNearEnd,
    clampUpperReliefEnd,
    clampUpperReliefX,
    counterboreDiameter,
    halfWidth,
    plateThickness,
    rightPivotX,
    sideScallopDiameter,
    sideScallopEnd,
    sideScallopX,
    sideScallopZ,
)

overrun = 0.03


def _box(x0, x1, y0, y1, z0, z1):
    assert x1 > x0 and y1 > y0 and z1 > z0, "infeasible: clamp box stations must be ordered"
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN))


def _channel_section(cx, radius, sx, near_y, far_y, small_radius, end_x):
    """Three exact circular arcs, joined across the table's submicron rounding."""
    assert 0.0 < small_radius < radius, "infeasible: channel arc radii"
    assert near_y < clampCenterY < far_y, "infeasible: channel offset axes"
    assert sx < cx < end_x, "infeasible: open channel section must face right"
    # Resolve the stated axes' 0.001 mm rounding into a shared tangent when
    # the correction is submicron; retain exact inputs for larger edits.
    tangent_square = (radius - small_radius) ** 2 - (clampCenterY - near_y) ** 2
    if tangent_square > 0.0:
        tangent_x = cx - sqrt(tangent_square)
        if abs(tangent_x - sx) < 0.002:
            sx = tangent_x
    points, angles = [], []
    for y in (near_y, far_y):
        dx, dy = sx - cx, y - clampCenterY
        distance = hypot(dx, dy)
        ux, uy = dx / distance, dy / distance
        points.append(((cx + radius * ux, clampCenterY + radius * uy), (sx + small_radius * ux, y + small_radius * uy)))
        angles.append(atan2(dy, dx))
    (bn, sn), (bf, sf) = points
    bottom, top = (sx, near_y - small_radius), (sx, far_y + small_radius)
    an, af = (angles[0] - pi / 2.0) / 2.0, (angles[1] + pi / 2.0) / 2.0
    mn = (sx + small_radius * cos(an), near_y + small_radius * sin(an))
    mf = (sx + small_radius * cos(af), far_y + small_radius * sin(af))
    edges = list(ThreePointArc(bottom, mn, sn).edges())
    if hypot(sn[0] - bn[0], sn[1] - bn[1]) > 1e-7:
        edges.extend(Polyline(sn, bn).edges())
    left = (cx - radius, clampCenterY)
    mid_n_angle, mid_f_angle = (angles[0] - pi) / 2.0, (angles[1] + pi) / 2.0
    edges.extend(
        ThreePointArc(bn, (cx + radius * cos(mid_n_angle), clampCenterY + radius * sin(mid_n_angle)), left).edges()
    )
    edges.extend(
        ThreePointArc(left, (cx + radius * cos(mid_f_angle), clampCenterY + radius * sin(mid_f_angle)), bf).edges()
    )
    if hypot(sf[0] - bf[0], sf[1] - bf[1]) > 1e-7:
        edges.extend(Polyline(bf, sf).edges())
    edges.extend(ThreePointArc(sf, mf, top).edges())
    edges.extend(Polyline(top, (end_x, top[1]), (end_x, bottom[1]), bottom).edges())
    return make_face(edges)


def _extrude_section(section, origin, direction, start, end):
    axis = Vector(*direction).normalized()
    radial = Vector(axis.Z, 0.0, -axis.X)
    frame = Plane(origin=Vector(*origin) + axis * start, x_dir=radial, z_dir=axis)
    return extrude(frame * section, amount=end - start, dir=axis)


def _uv_box(u0, u1, v0, v1, y0, y1):
    root = sqrt(2.0)
    frame = Plane(origin=((u0 + v0) / root, y0, (u0 - v0) / root), x_dir=(1.0, 0.0, -1.0), z_dir=(1.0, 0.0, 1.0))
    return frame * Box(v1 - v0, y1 - y0, u1 - u0, align=(Align.MIN, Align.MIN, Align.MIN))


def _apply(body):
    """Union bounded cutters and subtract once from the upstream stock."""
    assert 0.0 < clampAxialLipDiameter < clampOuterDiameter, "infeasible: axial groove radii"
    assert 0.0 < clampCornerLipDiameter < clampCornerOuterDiameter, "infeasible: diagonal groove radii"
    assert 0.0 < clampFarLipDiameter < clampOffsetDiameter, "infeasible: offset groove radii"
    assert 0.0 < clampCornerOffsetLipDiameter < clampCornerOffsetDiameter, "infeasible: diagonal offset radii"
    assert bottomZ < clampStartZ < clampEndZ < bodyTopZ, "infeasible: axial slot stations"
    assert clampCornerStart < clampCornerEnd, "infeasible: diagonal slot stations"
    assert clampTiltStart < clampTiltEnd < 0.0, "infeasible: tilted channel stations"
    assert 0.0 < sideScallopEnd < plateThickness, "infeasible: scallop depth"
    assert clampStartZ < clampFarLipStart < clampStartZ + 3.0, "infeasible: lower far lip lead"
    air_x = halfWidth + overrun
    axial_outer = _channel_section(
        clampAxisX, clampOuterDiameter / 2.0, clampOffsetX, clampNearY, clampFarY, clampOffsetDiameter / 2.0, 40.0
    )
    axial_inner = _channel_section(
        clampAxisX, clampAxialLipDiameter / 2.0, clampOffsetX, clampNearY, clampFarY, clampFarLipDiameter / 2.0, 40.0
    )
    groove = axial_outer - axial_inner
    tools = [
        Pos(0.0, 0.0, a) * extrude(groove, amount=b - a)
        for a, b in ((clampStartZ, clampStartZ + 3.0), (clampEndZ - 3.0, clampEndZ))
    ]
    upper_profile = _channel_section(
        clampUpperReliefX,
        clampReliefDiameter / 2.0,
        clampUpperInnerX,
        clampNearY,
        clampFarY,
        clampInnerDiameter / 2.0,
        40.0,
    )
    upper_cylinder = (
        Pos(clampUpperReliefX, clampCenterY, 0.0)
        * Rot(0.0, 0.0, 180.0)
        * Cylinder(clampReliefDiameter / 2.0, clampUpperReliefEnd, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )
    tools.append(upper_cylinder & extrude(upper_profile, amount=clampUpperReliefEnd))
    tilt_axis = Vector(clampTiltDirX, 0.0, clampTiltDirZ).normalized()
    tilt_radial = Vector(tilt_axis.Z, 0.0, -tilt_axis.X)
    inner_offset = Vector(clampTiltInnerX - clampTiltAxisX, 0.0, clampTiltInnerZ - clampTiltAxisZ).dot(tilt_radial)
    tilted_profile = _channel_section(
        0.0, clampReliefDiameter / 2.0, inner_offset, clampNearY, clampFarY, clampInnerDiameter / 2.0, 15.0
    )
    tilt_anchor = (clampTiltAxisX, 0.0, clampTiltAxisZ)
    tools.append(_extrude_section(tilted_profile, tilt_anchor, tilt_axis, clampTiltStart - overrun, clampTiltEnd))
    # Circular tangent transition read from section-y7. Its centre follows
    # from the stated tilted and vertical tangent lines, not a fitted spline.
    slope = tilt_axis.X / tilt_axis.Z
    radius = (clampTiltAxisX - slope * clampTiltAxisZ - clampUpperReliefX) / (1.0 / tilt_axis.Z - 1.0)
    assert radius > clampReliefDiameter, "infeasible: channel bend radius"
    bend_axis = Axis((clampUpperReliefX - radius, 0.0, 0.0), (0.0, 1.0, 0.0))
    tools.append(revolve(upper_profile, axis=bend_axis, revolution_arc=degrees(atan2(tilt_axis.X, tilt_axis.Z))))
    root = sqrt(2.0)
    corner_offset = ((clampCornerOffsetX - clampCornerAxisX) - (clampCornerOffsetZ - clampCornerAxisZ)) / root
    corner_outer = _channel_section(
        0.0,
        clampCornerOuterDiameter / 2.0,
        corner_offset,
        clampCornerNearY,
        clampCornerFarY,
        clampCornerOffsetDiameter / 2.0,
        15.0,
    )
    corner_inner = _channel_section(
        0.0,
        clampCornerLipDiameter / 2.0,
        corner_offset,
        clampCornerNearY,
        clampCornerFarY,
        clampCornerOffsetLipDiameter / 2.0,
        15.0,
    )
    tools.append(
        _extrude_section(
            corner_outer - corner_inner,
            (clampCornerAxisX, 0.0, clampCornerAxisZ),
            (1.0, 0.0, 1.0),
            clampCornerStart,
            clampCornerEnd,
        )
    )
    # The section drawing supplies x=24 walls and 1.375 mm slot shoulders.
    # Q4 leaves the scallop joins undimensioned. A 0.55 mm lower tangent blend
    # and a 0.2 mm upper edge round follow the supplied section-y1.5 contour.
    back_floor = 2.731
    upper_blend = 0.2
    lower_blend = 0.55
    scallop_r = sideScallopDiameter / 2.0
    nx, nz = sin(pi / 12.0), -cos(pi / 12.0)
    line_offset = nx * halfWidth + nz * -10.971
    upper_center_x = 24.0 - upper_blend
    upper_center_z = (line_offset - upper_blend - nx * upper_center_x) / nz
    upper_vertical = (24.0, upper_center_z)
    upper_tangent = (upper_center_x + upper_blend * nx, upper_center_z + upper_blend * nz)
    scallop_upper = (sideScallopX - scallop_r * nx, sideScallopZ - scallop_r * nz)
    lower_center_x = 23.14 - lower_blend
    lower_center_z = sideScallopZ - sqrt((scallop_r + lower_blend) ** 2 - (lower_center_x - sideScallopX) ** 2)
    lower_vertical = (23.14, lower_center_z)
    scallop_lower = (
        sideScallopX + scallop_r * (lower_center_x - sideScallopX) / (scallop_r + lower_blend),
        sideScallopZ + scallop_r * (lower_center_z - sideScallopZ) / (scallop_r + lower_blend),
    )
    upper_mid_angle = atan2(nz, nx) / 2.0
    upper_mid = (
        upper_center_x + upper_blend * cos(upper_mid_angle),
        upper_center_z + upper_blend * sin(upper_mid_angle),
    )
    lower_mid_angle = atan2(scallop_lower[1] - lower_center_z, scallop_lower[0] - lower_center_x) / 2.0
    lower_mid = (
        lower_center_x + lower_blend * cos(lower_mid_angle),
        lower_center_z + lower_blend * sin(lower_mid_angle),
    )
    side_profile = make_face(
        [
            *ThreePointArc(upper_vertical, upper_mid, upper_tangent).edges(),
            *Polyline(upper_tangent, scallop_upper).edges(),
            *ThreePointArc(scallop_upper, (sideScallopX - scallop_r, sideScallopZ), scallop_lower).edges(),
            *ThreePointArc(scallop_lower, lower_mid, lower_vertical).edges(),
            *Polyline(
                lower_vertical, (23.14, -22.65), (air_x, -22.65), (air_x, upper_center_z), upper_vertical
            ).edges(),
        ]
    )
    tools.extend(
        [
            _box(24.0, air_x, -overrun, back_floor, upper_center_z, -4.625),
            _box(24.0, air_x, -overrun, back_floor, clampUpperNearEnd, 25.375),
            _uv_box(-5.35, 4.0, 45.715 / root, 40.0, -overrun, 2.5),
            Pos(0.0, -overrun, 0.0)
            * extrude(Plane.XZ * side_profile, amount=sideScallopEnd + overrun, dir=(0.0, 1.0, 0.0)),
        ]
    )
    # Inclined row 4: far-side tangent wall continuing to the open flank.
    wall_normal = Vector(0.3368, -0.9397, -0.0594).normalized()
    tangent_y = clampFarY - clampInnerDiameter / 2.0 * wall_normal.Y
    wall = Plane(origin=(25.721, 12.259, -8.679), z_dir=wall_normal) * Box(
        100.0, 100.0, 30.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    tools.append(wall & _box(15.5, air_x, tangent_y, plateThickness + overrun, bottomZ - overrun, clampStartZ))

    # Retain the pivot shoulder's 0.1 mm guard. The upper-right counterbore
    # intentionally opens into the channel (sections y=7 and z=17); guarding
    # it would close that opening and leave its right support ledge too wide.
    guards = []
    for x, z in ((rightPivotX, 0.0),):
        guards.append(
            Pos(0.0, -overrun, 0.0)
            * extrude(
                Plane.XZ * Pos(x, z) * Circle(counterboreDiameter / 2.0 + 0.1),
                amount=plateThickness + 2.0 * overrun,
                dir=(0.0, 1.0, 0.0),
            )
        )
    # Tangent transition to the side wall. Cross-sections of its rolling
    # round follow the near cylinder and meet its documented terminal station.
    norm = hypot(inner_offset, clampNearY - clampCenterY)
    radial_x = inner_offset / norm * tilt_axis.Z
    contact_x = clampTiltInnerX + tilt_axis.X * clampTiltNearEnd + clampInnerDiameter / 2.0 * radial_x
    join_radius = (23.14 - contact_x) / (1.0 + radial_x)
    assert 0.0 < join_radius < 1.0, "infeasible: scallop-to-channel tangent round"
    join_sections = []
    for t in (
        clampTiltNearEnd + offset
        for offset in (-2.75, -2.25, -1.75, -1.25, -0.75, -0.25, 0.0, 0.25, 0.75, 1.25, 2.25, 3.25)
    ):
        centre = Vector(clampTiltInnerX, 0.0, clampTiltInnerZ) + tilt_axis * t
        wall_x = (23.14 - centre.X) / tilt_axis.Z
        blend_x = wall_x - join_radius
        blend_y = clampNearY - sqrt((clampInnerDiameter / 2.0 + join_radius) ** 2 - blend_x**2)
        ratio = (clampInnerDiameter / 2.0) / (clampInnerDiameter / 2.0 + join_radius)
        tangent = (blend_x * ratio, clampNearY + (blend_y - clampNearY) * ratio)
        angle = atan2(tangent[1] - blend_y, tangent[0] - blend_x)
        mid = (blend_x + join_radius * cos(angle / 2.0), blend_y + join_radius * sin(angle / 2.0))
        wall = (wall_x, blend_y)
        section = make_face(
            [
                *ThreePointArc(wall, mid, tangent).edges(),
                *Polyline(tangent, (3.0, clampNearY), (3.0, blend_y), wall).edges(),
            ]
        )
        join_sections.append(Plane(origin=centre, x_dir=tilt_radial, z_dir=tilt_axis) * section)
    tools.append(loft(join_sections, ruled=False) & _box(15.5, air_x, 0.0, clampNearY, -22.575, -16.0))
    cutter = tools[0].fuse(*tools[1:])
    cutter = cutter - guards[0].fuse(*guards[1:])
    footprint = _box(15.5, air_x, -overrun, plateThickness + overrun, bottomZ - overrun, bodyTopZ)
    cutter = cutter & footprint
    shaped = body - cutter
    assert shaped.is_valid, "infeasible: clamp boolean must be valid"
    assert len(shaped.solids()) == 1, "infeasible: clamp must retain one connected housing"
    return shaped


def apply(body):
    # Preserve the primitive cylinder's seam at its axial extremum. Removing
    # that seam inflates OpenCascade's UV bound on the roof's elliptic trim.
    with SkipClean():
        return _apply(body)

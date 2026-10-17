import cadquery as cq  # isort: skip
import math

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
    clampTiltFarEnd,
    clampTiltFarStart,
    clampTiltInnerX,
    clampTiltInnerZ,
    clampTiltNearEnd,
    clampTiltNearStart,
    clampTiltStart,
    clampUpperFarEnd,
    clampUpperInnerX,
    clampUpperNearEnd,
    clampUpperReliefEnd,
    clampUpperReliefX,
    counterboreDiameter,
    halfWidth,
    plateThickness,
    rightBottomChamferZ,
    rightPivotX,
    sideScallopDiameter,
    sideScallopEnd,
    sideScallopX,
    sideScallopZ,
    upperRightScrewX,
    upperRightScrewZ,
)

assert clampOuterDiameter > 0, "infeasible: clampOuterDiameter must be positive"
assert clampAxialLipDiameter > 0, "infeasible: clampAxialLipDiameter must be positive"
assert clampOuterDiameter > clampAxialLipDiameter, "infeasible: axial lip must fit inside outer cut"
assert clampCornerOuterDiameter > clampCornerLipDiameter, "infeasible: corner lip must fit inside outer cut"
assert clampOffsetDiameter > clampFarLipDiameter, "infeasible: far lip must fit inside offset cut"
assert clampCornerOffsetDiameter > clampCornerOffsetLipDiameter, "infeasible: corner offset lip must fit inside cut"
assert clampInnerDiameter > 0, "infeasible: clampInnerDiameter must be positive"
assert clampReliefDiameter > 0, "infeasible: clampReliefDiameter must be positive"
assert sideScallopDiameter > 0, "infeasible: sideScallopDiameter must be positive"
assert clampEndZ > clampStartZ, "infeasible: clamp axial span must be ordered"
assert clampCornerEnd > clampCornerStart, "infeasible: clamp corner span must be ordered"


def _cyl(ox, oy, oz, dx, dy, dz, radius, t0, t1, extra=0.02, extra0=None):
    length = (dx * dx + dy * dy + dz * dz) ** 0.5
    ux, uy, uz = dx / length, dy / length, dz / length
    lead = extra if extra0 is None else extra0
    start = t0 - lead
    height = (t1 - t0) + lead + extra
    origin = cq.Vector(ox + ux * start, oy + uy * start, oz + uz * start)
    return cq.Solid.makeCylinder(radius, height, origin, cq.Vector(ux, uy, uz))


def _box(xmin, xmax, ymin, ymax, zmin, zmax):
    return cq.Solid.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, cq.Vector(xmin, ymin, zmin))


def _plane_tool(point, normal, depth=50.0, span=80.0):
    nvec = cq.Vector(*normal).normalized()
    arb = cq.Vector(0, 1, 0) if abs(nvec.y) < 0.85 else cq.Vector(1, 0, 0)
    xdir = nvec.cross(arb)
    if xdir.Length < 1e-9:
        xdir = nvec.cross(cq.Vector(0, 0, 1))
    xdir = xdir.normalized()
    return (
        cq.Workplane(cq.Plane(origin=cq.Vector(*point), xDir=xdir, normal=nvec)).rect(span, span).extrude(depth).val()
    )


def _keep(shape, xmin, xmax, ymin, ymax, zmin, zmax):
    return shape.intersect(_box(xmin, xmax, ymin, ymax, zmin, zmax))


_SQ2 = 2.0**0.5


def _uvy(u, v, y):
    # Corner frame: u along the 45-degree ring axis (0.707, 0, 0.707), v across it (0.707, 0, -0.707), y through.
    return cq.Vector((u + v) / _SQ2, y, (u - v) / _SQ2)


def _uv_box(u0, u1, v0, v1, y0, y1):
    plane = cq.Plane(origin=_uvy(u0, v0, y0), xDir=(1.0 / _SQ2, 0.0, -1.0 / _SQ2), normal=(1.0 / _SQ2, 0.0, 1.0 / _SQ2))
    return cq.Workplane(plane).rect(v1 - v0, y1 - y0, centered=False).extrude(u1 - u0).val()


def _fuse(shapes):
    acc = shapes[0]
    for shape in shapes[1:]:
        acc = acc.fuse(shape)
    return acc


def apply(body):
    assert 0.0 < plateThickness and 0.0 < halfWidth, "infeasible: stock dimensions must be positive"
    assert bottomZ < clampStartZ < clampEndZ < clampUpperReliefEnd < bodyTopZ - 0.1, (
        "infeasible: channel crosses the top partition"
    )
    assert clampTiltStart < clampTiltEnd, "infeasible: tilted outer span must be ordered"
    assert clampTiltNearStart < clampTiltNearEnd, "infeasible: tilted near span must be ordered"
    assert clampTiltFarStart < clampTiltFarEnd, "infeasible: tilted far span must be ordered"
    assert clampTiltDirZ > 0.0, "infeasible: tilted channel must point upward"
    assert 0.0 < clampNearY < clampCenterY < clampFarY < plateThickness, (
        "infeasible: axial centers must fit within thickness"
    )
    assert 0.0 < clampCornerNearY < clampCenterY < clampCornerFarY < plateThickness, (
        "infeasible: corner centers must fit within thickness"
    )
    assert 0.0 < clampCornerLipDiameter and 0.0 < clampCornerOffsetLipDiameter and 0.0 < clampFarLipDiameter, (
        "infeasible: lip diameters must be positive"
    )
    assert 0.0 < sideScallopEnd < plateThickness, "infeasible: scallop depth must fit within thickness"
    extra = 0.02
    air = 0.03
    corner_dx = 0.7071
    corner_dz = 0.7071
    tilt_dx = clampTiltDirX
    tilt_dz = clampTiltDirZ

    # Partial tools retain the clamp cores; the slot cutters protect fastener stock.
    ax0, ax1 = 20.4, 32.0
    # Keep 0.1 mm clearance from the x=15.5 partition boundary.
    cx0 = 15.6
    y0, y1 = -air, plateThickness + air
    z0, z1 = bottomZ - air, bodyTopZ - 0.1

    r_axial = clampOuterDiameter / 2.0
    r_axial_lip = clampAxialLipDiameter / 2.0
    r_corner = clampCornerOuterDiameter / 2.0
    r_corner_lip = clampCornerLipDiameter / 2.0
    r_offset = clampOffsetDiameter / 2.0
    r_far_lip = clampFarLipDiameter / 2.0
    r_corner_off = clampCornerOffsetDiameter / 2.0
    r_corner_off_lip = clampCornerOffsetLipDiameter / 2.0
    r_inner = clampInnerDiameter / 2.0
    r_relief = clampReliefDiameter / 2.0
    r_scallop = sideScallopDiameter / 2.0

    # The straight slots follow the supplied tangent-circle outlines. Their
    # outer wall uses D12.63 and the two D9.5 arcs; the retained core uses D9.13
    # and the far D6 arc. A single closed wire avoids slivers at rounded tangencies.
    def join(cx, cy, radius, sx, sy, small_radius):
        dx, dy = sx - cx, sy - cy
        distance = math.hypot(dx, dy)
        along = (radius * radius - small_radius * small_radius + distance * distance) / (2.0 * distance)
        altitude = math.sqrt(max(0.0, radius * radius - along * along))
        candidates = [
            (
                cx + along * dx / distance + sign * altitude * dy / distance,
                cy + along * dy / distance - sign * altitude * dx / distance,
            )
            for sign in (-1.0, 1.0)
        ]
        return min(candidates, key=lambda point: point[0])

    def arc_mid(cx, cy, radius, start, end):
        first = math.atan2(start[1] - cy, start[0] - cx)
        last = math.atan2(end[1] - cy, end[0] - cx)
        while last > first:
            last -= 2.0 * math.pi
        angle = (first + last) / 2.0
        return (cx + radius * math.cos(angle), cy + radius * math.sin(angle))

    def groove(zlo, zhi):
        near_bottom = (clampOffsetX, clampNearY - r_offset)
        far_top = (clampOffsetX, clampFarY + r_offset)
        near_join = join(clampAxisX, clampCenterY, r_axial, clampOffsetX, clampNearY, r_offset)
        far_join = join(clampAxisX, clampCenterY, r_axial, clampOffsetX, clampFarY, r_offset)
        outer = (
            cq.Workplane("XY", origin=(0.0, 0.0, zlo))
            .moveTo(*near_bottom)
            .threePointArc(arc_mid(clampOffsetX, clampNearY, r_offset, near_bottom, near_join), near_join)
            .threePointArc((clampAxisX - r_axial, clampCenterY), far_join)
            .threePointArc(arc_mid(clampOffsetX, clampFarY, r_offset, far_join, far_top), far_top)
            .lineTo(ax1, far_top[1])
            .lineTo(ax1, near_bottom[1])
            .close()
            .extrude(zhi - zlo)
            .val()
        )
        core_bottom = (clampAxisX, clampCenterY - r_axial_lip)
        core_join = join(clampAxisX, clampCenterY, r_axial_lip, clampOffsetX, clampFarY, r_far_lip)
        core_top = (clampOffsetX, clampFarY + r_far_lip)
        core = (
            cq.Workplane("XY", origin=(0.0, 0.0, zlo - air))
            .moveTo(*core_bottom)
            .threePointArc((clampAxisX - r_axial_lip, clampCenterY), core_join)
            .threePointArc(arc_mid(clampOffsetX, clampFarY, r_far_lip, core_join, core_top), core_top)
            .lineTo(ax1 + air, core_top[1])
            .lineTo(ax1 + air, core_bottom[1])
            .close()
            .extrude(zhi - zlo + 2.0 * air)
            .val()
        )
        if zlo < clampFarLipStart < zhi:
            core = core.cut(_box(cx0, ax1 + 2.0 * air, core_join[1], y1, zlo - air, clampFarLipStart))
        return outer.cut(core)

    slot_lo = groove(clampStartZ, -6.0)
    slot_hi = groove(21.0, clampEndZ)
    # Open the lip on +x after the lower slot so z=-6 / z=21 floors can exist.
    axial_open = _keep(
        _cyl(
            clampAxisX,
            clampCenterY,
            0.0,
            0.0,
            0.0,
            1.0,
            r_axial_lip,
            -6.0,
            clampEndZ,
            extra=extra,
        ),
        clampAxisX - 0.02,
        ax1,
        4.5,
        9.5,
        -6.05,
        24.05,
    )
    # 45-degree corner as one construction. Slab u in [clampCornerStart, clampCornerEnd] between the two
    # walls; its air profile is the stated ring cuts (Ø12.684 between its tangent points with the Ø8.787
    # near/far discs, the discs themselves) plus the 3 mm channel band v >= v_o from the y 0.75 ledge to the
    # y 13.25 front floor, minus the boss (Ø9.184 core between its pin tangents, Ø5.287 pins, and everything
    # at v >= v_o between the y 2.5 pocket floor and the y 11.5 front ledge).
    u0, u1 = clampCornerStart, clampCornerEnd
    v_a = clampCornerAxisX * _SQ2
    v_o = clampCornerOffsetX * _SQ2
    v_b = v_o + 0.5
    v_c = (halfWidth - rightBottomChamferZ) / _SQ2
    u_bw = -5.35
    dy = clampCenterY - clampCornerNearY
    dist = ((v_a - v_o) ** 2 + dy * dy) ** 0.5
    y_ledge = clampCornerNearY - r_corner_off
    y_front = clampCornerFarY + r_corner_off
    y_floor = clampCornerNearY - r_corner_off_lip
    y_fledge = clampCornerFarY + r_corner_off_lip
    y_t = r_corner * dy / dist
    y_ct = r_corner_lip * dy / dist
    assert y_floor > y_ledge and y_front > y_fledge, "infeasible: corner ledges must be ordered"

    def c_cyl(y, radius, lead=0.0):
        ax = clampCornerAxisX if radius in (r_corner, r_corner_lip) else clampCornerOffsetX
        az = clampCornerAxisZ if radius in (r_corner, r_corner_lip) else clampCornerOffsetZ
        return _cyl(ax, y, az, corner_dx, 0.0, corner_dz, radius, u0, u1, extra=lead, extra0=lead)

    disc_corner = c_cyl(clampCenterY, r_corner).intersect(
        _uv_box(u0 - 0.1, u1 + 0.1, 20.0, 45.0, clampCenterY - y_t, clampCenterY + y_t)
    )
    outer = _fuse(
        [
            disc_corner,
            c_cyl(clampCornerNearY, r_corner_off),
            c_cyl(clampCornerFarY, r_corner_off),
            _uv_box(u0, u1, v_o, v_c + 0.6, y_ledge, y_front),
        ]
    )
    boss = _fuse(
        [
            c_cyl(clampCenterY, r_corner_lip, 0.1).intersect(
                _uv_box(u0 - 0.2, u1 + 0.2, 20.0, 45.0, clampCenterY - y_ct, clampCenterY + y_ct)
            ),
            c_cyl(clampCornerNearY, r_corner_off_lip, 0.1),
            c_cyl(clampCornerFarY, r_corner_off_lip, 0.1),
            _uv_box(u0 - 0.1, u1 + 0.1, v_o, v_c + 1.0, y_floor, y_fledge),
        ]
    )
    slab_air = outer.cut(boss)
    # Back pocket under the y 2.5 floor: bottom wall u=-5.35, back bevel v=v_b, out through the chamfer.
    back_pocket = _uv_box(u_bw, u1, v_b, v_c + 0.6, -0.05, y_floor)
    # Beyond the lower wall the back opening continues (section y=1.5) to the x 23.14 scallop end.
    lip_pocket = _uv_box(u1, 30.0, v_b, v_c + 0.6, -0.03, 1.85).intersect(_box(cx0, ax1, y0, y1, z0, -22.5))
    corner_tool = _fuse([slab_air, back_pocket, lip_pocket])
    tilt_cyl = _cyl(
        clampTiltAxisX,
        clampCenterY,
        clampTiltAxisZ,
        tilt_dx,
        0.0,
        tilt_dz,
        r_relief,
        clampTiltStart,
        clampTiltEnd,
        extra=0.0,
        extra0=extra,
    )
    # Find the joins in the plane normal to the tilted axes. The rounded
    # centers leave a 0.000108 mm circle overlap; trimming at the actual
    # intersections avoids thin cap slivers that cannot mesh consistently.
    tilt_dir = cq.Vector(tilt_dx, 0.0, tilt_dz).normalized()
    tilt_outer_radial = clampTiltAxisX * tilt_dir.z - clampTiltAxisZ * tilt_dir.x
    tilt_inner_radial = clampTiltInnerX * tilt_dir.z - clampTiltInnerZ * tilt_dir.x
    tilt_near_y = join(tilt_outer_radial, clampCenterY, r_relief, tilt_inner_radial, clampNearY, r_inner)[1]
    tilt_far_y = join(tilt_outer_radial, clampCenterY, r_relief, tilt_inner_radial, clampFarY, r_inner)[1]
    tilt_outer = _keep(tilt_cyl, cx0, ax1, tilt_near_y, tilt_far_y, z0, z1)
    # Q4 leaves the connecting blend unspecified. This three-station loft
    # joins the exact bore ends and meets the documented lower pocket floor.
    # The 0.165 mm middle-station setback controls that untabulated transition.
    blend_start = cq.Vector(clampTiltAxisX, clampCenterY, clampTiltAxisZ) + tilt_dir * clampTiltEnd
    blend_lower = (
        cq.Workplane(cq.Plane(origin=blend_start, xDir=(0.0, 1.0, 0.0), normal=tilt_dir)).circle(r_relief).val()
    )
    # Place the shared construction seam 0.02 mm into the connecting blend.
    # All three straight cutters start there, keeping their caps off z=0.
    blend_join_z = -extra
    blend_upper = cq.Workplane("XY", origin=(clampUpperReliefX, clampCenterY, blend_join_z)).circle(r_relief).val()
    blend_mid_z = -4.625
    blend_mid_x = clampTiltAxisX + (blend_mid_z - clampTiltAxisZ) * tilt_dx / tilt_dz - 0.165
    blend_mid = (
        cq.Workplane("XY", origin=(blend_mid_x, clampCenterY, blend_mid_z))
        .ellipse(r_relief / tilt_dir.z, r_relief)
        .val()
    )
    # Taper the final transition into the upper central arc. This removes
    # nearly tangent crescents while retaining the measured lower floors.
    blend_end_mask = (
        cq.Workplane("YZ", origin=(cx0, 0.0, 0.0))
        .polyline(
            [
                (y0, z0),
                (y1, z0),
                (y1, -0.1),
                (11.929, blend_join_z),
                (11.929, 0.1),
                (2.071, 0.1),
                (2.071, blend_join_z),
                (y0, -0.1),
            ]
        )
        .close()
        .extrude(ax1 - cx0)
        .val()
    )
    tilt_ext = cq.Solid.makeLoft([blend_lower, blend_mid, blend_upper]).intersect(blend_end_mask)
    relief_cyl = _cyl(
        clampUpperReliefX,
        clampCenterY,
        0.0,
        0.0,
        0.0,
        1.0,
        r_relief,
        0.0,
        clampUpperReliefEnd,
        extra=0.0,
        extra0=extra,
    )
    # Put the cylindrical seam on the inner generatrix. Its intersection with
    # the inclined rim then has tight STEP bounds without changing the bore.
    relief_cyl = relief_cyl.rotate(
        (clampUpperReliefX, clampCenterY, 0.0), (clampUpperReliefX, clampCenterY, 1.0), 180.0
    )
    # Let the stated relief cylinder meet the upper-right bevel continuously;
    # a narrower terminal band leaves an artificial step in that plane.
    upper_relief = _keep(relief_cyl, cx0, ax1, 2.071, 11.929, -0.05, z1)
    tilt_near = _keep(
        _cyl(
            clampTiltInnerX,
            clampNearY,
            clampTiltInnerZ,
            tilt_dx,
            0.0,
            tilt_dz,
            r_inner,
            clampTiltNearStart,
            clampTiltNearEnd,
            extra=extra,
        ),
        ax0,
        ax1,
        y0,
        y1,
        z0,
        z1,
    )
    tilt_far = _keep(
        _cyl(
            clampTiltInnerX,
            clampFarY,
            clampTiltInnerZ,
            tilt_dx,
            0.0,
            tilt_dz,
            r_inner,
            clampTiltFarStart,
            clampTiltFarEnd + 1.0,
            extra=extra,
        ),
        cx0,
        ax1,
        y0,
        12.26,
        z0,
        z1,
    ).intersect(_box(cx0, ax1, y0, y1, z0, -9.0))
    # Match the central cutter's lead into the blend so that all three bore
    # segments form the same continuous profile through the pivot section.
    upper_near = _keep(
        _cyl(
            clampUpperInnerX,
            clampNearY,
            0.0,
            0.0,
            0.0,
            1.0,
            r_inner,
            0.0,
            clampUpperNearEnd,
            extra=extra,
            extra0=extra,
        ),
        ax0,
        ax1,
        y0,
        y1,
        z0,
        z1,
    )
    upper_far = _keep(
        _cyl(
            clampUpperInnerX,
            clampFarY,
            0.0,
            0.0,
            0.0,
            1.0,
            r_inner,
            0.0,
            clampUpperFarEnd,
            extra=extra,
            extra0=extra,
        ),
        ax0,
        ax1,
        y0,
        y1,
        z0,
        z1,
    )

    scallop = _keep(
        _cyl(
            sideScallopX,
            0.0,
            sideScallopZ,
            0.0,
            1.0,
            0.0,
            r_scallop,
            0.0,
            sideScallopEnd,
            extra=air,
        ),
        20.4,
        32.0,
        -0.05,
        sideScallopEnd + air,
        sideScallopZ - r_scallop - 0.2,
        sideScallopZ + r_scallop + 0.2,
    )
    scallop_open = _box(23.14, 27.2, -0.05, sideScallopEnd + air, sideScallopZ - r_scallop, sideScallopZ + r_scallop)
    scallop_end = _box(23.14, 26.6, -0.05, 1.78, -22.65, -18.49)

    lower_back_pocket = _box(24.0, ax1, -air, 2.731, -11.59, -4.625)
    upper_back_pocket = _box(24.0, ax1, -air, 2.731, 19.625, 25.375)
    # Tilt wall: the flat tangent to the far Ø8 (y 12.259 line) out to the flank, from the lower wall plane
    # through the chamfer, below the z=-9 slot floor.
    wall_n = (0.3368, -0.9397, -0.0594)
    y_tan = clampFarY - r_inner * wall_n[1]
    tilt_wall = (
        _plane_tool((25.721, 12.259, -8.679), wall_n, depth=2.5)
        .intersect(_uv_box(u1, 30.0, 20.0, v_c + 0.6, y_tan, y1))
        .intersect(_box(15.0, 27.1, -0.1, 14.1, -30.0, -9.0))
    )

    tilt_open = (
        _plane_tool((clampTiltInnerX, clampFarY, clampTiltInnerZ), (tilt_dz, 0.0, -tilt_dx))
        .intersect(_uv_box(u1, 30.0, 20.0, v_c + 0.6, 2.071, y_tan))
        .intersect(_box(cx0, ax1, y0, y1, z0, -9.0))
    )

    keepout = _fuse(
        [
            _cyl(
                rightPivotX,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                counterboreDiameter / 2.0 + 0.15,
                -air,
                plateThickness + air,
                extra=0.0,
            ),
            _cyl(
                upperRightScrewX,
                0.0,
                upperRightScrewZ,
                0.0,
                1.0,
                0.0,
                counterboreDiameter / 2.0 + 0.15,
                -air,
                plateThickness + air,
                extra=0.0,
            ),
        ]
    )
    tool = _fuse(
        [
            slot_lo,
            slot_hi,
            axial_open,
            tilt_near,
            upper_near,
            upper_far,
            scallop,
            scallop_open,
            scallop_end,
            lower_back_pocket,
            upper_back_pocket,
        ]
    ).cut(keepout)
    # Reliefs meet the documented counterbore openings; they do not fill or
    # extend the neighboring screw stacks. Fuse every cutter before cutting stock.
    tool = _fuse([tool, corner_tool, tilt_wall, tilt_open, tilt_outer, tilt_ext, tilt_far, upper_relief])
    tool = tool.intersect(_box(cx0, halfWidth + air, -air, plateThickness + air, z0, z1))
    return body.cut(tool, clean=True)

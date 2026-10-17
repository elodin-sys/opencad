"""Exterior stock and retained bosses, before the keyhole and clamp modules.

The plane table determines the perimeter.  Areas trimmed by another module are
intentionally left for the composed critic.  The unspecified cosmetic blends,
lettering and arrow are omitted.
"""

from math import hypot, sqrt

from build123d import Align, Box, Circle, Plane, Polygon, Polyline, Pos, ThreePointArc, Vector, extrude, loft, make_face
from params import (
    bodyTopZ,
    bottomZ,
    filamentDiameter,
    filamentDirX,
    filamentDirY,
    filamentEntryAxisX,
    filamentEntryAxisY,
    filamentEntryEnd,
    filamentTransverseX,
    filamentZ,
    halfWidth,
    keyMiddleEnd,
    leftDiagonalAnchorX,
    leftDiagonalAnchorZ,
    leftFootX,
    leftShoulderZ,
    leftTopChamferZ,
    lugBossDiameter,
    lugMaxZ,
    lugNutX,
    lugNutZ,
    plateThickness,
    rightBottomChamferZ,
    rightTopChamferX,
    upperLeftBossDiameter,
    upperLeftScrewX,
    upperLeftScrewZ,
)

overrun = 0.03
# Dimension-sheet.md, +z planar faces at z=28: the right ledge's area.
top_right_ledge_area = 79.87


def _unit_xz(x, z):
    length = hypot(x, z)
    assert length > 0.0, "infeasible: a perimeter normal must be nonzero"
    return x / length, z / length


def _xz_prism(profile, start, end):
    assert end > start, "infeasible: exterior extrusion stations must be ordered"
    return Pos(0.0, start, 0.0) * extrude(Plane.XZ * profile, amount=end - start, dir=(0.0, 1.0, 0.0))


def _polygon_prism(points, start, end):
    return _xz_prism(Polygon(*points, align=None), start, end)


def apply(body):
    """Add connecting web stock, then remove one union of exterior cutters."""
    assert 0.0 < keyMiddleEnd < plateThickness, "infeasible: the boss depth must lie inside the plate"
    assert bottomZ < leftShoulderZ < leftTopChamferZ < bodyTopZ < lugMaxZ, "infeasible: exterior heights"
    assert -halfWidth < leftFootX < 0.0, "infeasible: the foot must lie inside the envelope"
    assert 0.0 < rightTopChamferX < halfWidth, "infeasible: upper-right bevel must meet the top ledge"
    assert bottomZ < rightBottomChamferZ < bodyTopZ, "infeasible: lower-right bevel height"
    assert upperLeftBossDiameter > 0.0 and lugBossDiameter > 0.0, "infeasible: positive boss diameters required"

    x_min, x_max = -halfWidth - overrun, halfWidth + overrun
    z_min, z_max = bottomZ - overrun, lugMaxZ + overrun
    y_min, y_max = -overrun, plateThickness + overrun

    # Intersect the two stated lower-left planes, rather than locking the
    # raster knee or the provisional datum's foot height to the result.
    nx, nz = _unit_xz(-0.7373, -0.6756)
    sx, sz = _unit_xz(-0.0872, -0.9962)
    lower_offset = nx * leftDiagonalAnchorX + nz * leftDiagonalAnchorZ
    shallow_offset = sx * -halfWidth + sz * leftShoulderZ
    determinant = nx * sz - nz * sx
    assert abs(determinant) > 0.01, "infeasible: the lower-left planes must intersect"
    knee_x = (lower_offset * sz - shallow_offset * nz) / determinant
    knee_z = (nx * shallow_offset - sx * lower_offset) / determinant
    foot_top = (lower_offset - nx * leftFootX) / nz
    shallow_air_z = (shallow_offset - sx * x_min) / sz
    assert -halfWidth < knee_x < leftFootX, "infeasible: the knee must lie between the left side and foot"
    assert bottomZ < foot_top < knee_z < leftShoulderZ, "infeasible: lower-left transitions must rise"
    tools = [
        _polygon_prism(
            [(x_min, z_min), (leftFootX, z_min), (leftFootX, foot_top), (knee_x, knee_z), (x_min, shallow_air_z)],
            y_min,
            y_max,
        )
    ]

    # Outward [1,0,-1]: x-z=halfWidth-rightBottomChamferZ.
    # Its full stock face is retained until the clamp removes its own slots.
    rx, rz = _unit_xz(0.7071, -0.7071)
    lower_right_offset = rx * halfWidth + rz * rightBottomChamferZ
    lower_right_x = (lower_right_offset - rz * z_min) / rx
    lower_right_z = (lower_right_offset - rx * x_max) / rz
    tools.append(_polygon_prism([(lower_right_x, z_min), (x_max, z_min), (x_max, lower_right_z)], y_min, y_max))

    # At y=0..8, the upper-left edge is the documented 45-degree plane.
    ux, uz = _unit_xz(-0.7071, 0.7071)
    upper_left_offset = ux * -halfWidth + uz * leftTopChamferZ
    upper_left_air_z = (upper_left_offset - ux * x_min) / uz
    upper_left_air_x = (upper_left_offset - uz * z_max) / ux
    tools.append(
        _polygon_prism(
            [(x_min, upper_left_air_z), (upper_left_air_x, z_max), (x_min, z_max)],
            y_min,
            keyMiddleEnd,
        )
    )

    # At y=8..14, replace that edge with the z=24 ledge, the exact
    # diameter-11 arc, and the table's inclined boss plane.  The plane crosses
    # the circle: use its upper intersection, not an invented tangent.
    boss_r = upperLeftBossDiameter / 2.0
    boss_rise = leftTopChamferZ - upperLeftScrewZ
    assert 0.0 < boss_rise < boss_r, "infeasible: the boss must rise above its ledge"
    boss_left_x = upperLeftScrewX - sqrt(boss_r * boss_r - boss_rise * boss_rise)
    bx, bz = _unit_xz(0.7660, 0.6428)
    boss_plane_x = upperLeftScrewX + 2.0  # Table anchor (-16.5, 14, 28).
    boss_offset = bx * boss_plane_x + bz * bodyTopZ
    distance = boss_offset - bx * upperLeftScrewX - bz * upperLeftScrewZ
    assert 0.0 < distance < boss_r, "infeasible: the boss bevel must intersect its cylinder"
    transverse = sqrt(boss_r * boss_r - distance * distance)
    boss_end = (
        upperLeftScrewX + bx * distance - bz * transverse,
        upperLeftScrewZ + bz * distance + bx * transverse,
    )
    # This cap ends at the screw-axis height, above the functional central
    # bore walls.  Its remaining horizontal shelf is inside the future upper
    # counterbore.  That module trims the boss bevel to its final area.
    cap_floor = upperLeftScrewZ
    bevel_floor_x = (boss_offset - bz * cap_floor) / bx
    lug_left = lugNutX - lugBossDiameter / 2.0
    assert x_min < boss_left_x < upperLeftScrewX < boss_end[0] < bevel_floor_x < lug_left, (
        "infeasible: upper relief order"
    )
    relief_profile = make_face(
        [
            *Polyline((x_min, leftTopChamferZ), (boss_left_x, leftTopChamferZ)).edges(),
            *ThreePointArc(
                (boss_left_x, leftTopChamferZ),
                (upperLeftScrewX, upperLeftScrewZ + boss_r),
                boss_end,
            ).edges(),
            *Polyline(
                boss_end,
                (bevel_floor_x, cap_floor),
                (lug_left, cap_floor),
                (lug_left, z_max),
                (x_min, z_max),
                (x_min, leftTopChamferZ),
            ).edges(),
        ]
    )
    tools.append(_xz_prism(relief_profile, keyMiddleEnd, y_max))

    # A ruled connecting web replaces the provisional rectangular blockout.
    # The low section is a tangent support to the lug beside the transverse
    # passage.  The rear section reaches the exact upper
    # right plane and z=lugMaxZ, including stock beyond y=7 for both passages.
    # The source does not dimension the cosmetic joining fillet.
    lug_r = lugBossDiameter / 2.0
    lug_top = lugNutZ + lug_r
    tx, tz = _unit_xz(0.7071, 0.7071)
    upper_right_offset = tx * rightTopChamferX + tz * bodyTopZ
    peak_x = (upper_right_offset - tz * lugMaxZ) / tx
    assert lugNutX < peak_x < rightTopChamferX and lug_top <= lugMaxZ, "infeasible: rear web exceeds the envelope"
    # The far end of the angled passage is the cylinder's extremum against
    # the 45-degree right plane.  Reach that side of the wing before its
    # contact y coordinate, not merely at the provisional stock's y=7 edge.
    # These shared passage parameters govern support only; there are no
    # passage cuts in this module.
    passage_norm = hypot(filamentDirX, filamentDirY)
    assert passage_norm > 0.0 and filamentDiameter > 0.0, "infeasible: positive passage size and axis required"
    passage_dx, passage_dy = filamentDirX / passage_norm, filamentDirY / passage_norm
    projected_normal = sqrt(tx * tx * passage_dy * passage_dy + tz * tz)
    contact_y = (
        filamentEntryAxisY
        + passage_dy * filamentEntryEnd
        + filamentDiameter / 2.0 * tx * passage_dx * passage_dy / projected_normal
    )
    rear_join_y = contact_y - overrun
    assert keyMiddleEnd < rear_join_y < plateThickness, "infeasible: angled passage support stations"
    # At z=28 the ruled web leaves a rectangular ledge through y=8 and
    # a triangle between y=8 and the rear join.  Its documented area fixes
    # the remaining width without inventing a blend radius.  The centroid
    # is an independent check, not another geometry target or an equality.
    ledge_width = 2.0 * top_right_ledge_area / (keyMiddleEnd + rear_join_y)
    web_tip_x = rightTopChamferX - ledge_width
    assert abs(web_tip_x - filamentTransverseX) < filamentDiameter / 2.0, "infeasible: transverse passage misses web"
    dx, dz = web_tip_x - lugNutX, bodyTopZ - lugNutZ
    d2 = dx * dx + dz * dz
    assert d2 > lug_r * lug_r, "infeasible: the web tip must be outside the lug"
    root = sqrt(d2 - lug_r * lug_r)
    tangent_x = lugNutX + (lug_r * lug_r * dx - lug_r * root * dz) / d2
    tangent_z = lugNutZ + (lug_r * lug_r * dz + lug_r * root * dx) / d2
    assert lugNutX < tangent_x < web_tip_x < rightTopChamferX, "infeasible: low web stations"
    front_profile = Polygon(
        (lugNutX, bodyTopZ - overrun),
        (lugNutX, lug_top),
        (tangent_x, tangent_z),
        (web_tip_x, bodyTopZ),
        (web_tip_x, bodyTopZ - overrun),
        align=None,
    )
    rear_profile = Polygon(
        (lugNutX, bodyTopZ - overrun),
        (lugNutX, lug_top),
        (peak_x, lugMaxZ),
        (rightTopChamferX, bodyTopZ),
        (rightTopChamferX, bodyTopZ - overrun),
        align=None,
    )
    low_web = _xz_prism(front_profile, 0.0, keyMiddleEnd)
    rising_web = loft(
        [
            Pos(0.0, keyMiddleEnd, 0.0) * (Plane.XZ * front_profile),
            Pos(0.0, rear_join_y, 0.0) * (Plane.XZ * rear_profile),
        ],
        ruled=True,
    )
    rear_web = rising_web.fuse(_xz_prism(rear_profile, rear_join_y, plateThickness))
    # A keep mask removes the old web without recutting or later restoring
    # the lug.  Extend it into air at both end faces for the single cut.
    lug_mask = _xz_prism(Pos(lugNutX, lugNutZ) * Circle(lug_r), y_min, y_max)
    web_mask = _xz_prism(front_profile, y_min, keyMiddleEnd).fuse(
        rear_web, _xz_prism(rear_profile, plateThickness, y_max), lug_mask
    )
    web_clearance = _polygon_prism(
        [(lug_left, bodyTopZ), (x_max, bodyTopZ), (x_max, z_max), (lug_left, z_max)],
        y_min,
        y_max,
    )
    tools.append(web_clearance - web_mask)

    # Cut only outside x+z=50.5 at nominal parameters.  In particular this
    # leaves the x=24 clamp walls and z=25.375 rim stock intact.
    upper_right_air_z = (upper_right_offset - tx * x_max) / tz
    upper_right_air_x = (upper_right_offset - tz * z_max) / tx
    tools.append(
        _polygon_prism(
            [(x_max, upper_right_air_z), (x_max, z_max), (upper_right_air_x, z_max)],
            y_min,
            y_max,
        )
    )

    # The dimension sheet also gives the open web's tangent wall through
    # (19.23, 13, 31.27), with outward normal (0.2876, -0.9135, 0.2876).
    # It is parallel to the angled filament axis and tangent to its circle.
    # Above that tangency, clear the forward stock instead of leaving a
    # closed roof over the passage. Preserve the lug's unblended cylinder
    # and the lower circular wall for the downstream filament cutter.
    # Resolve the table's rounded normal/anchor into exact tangency to avoid
    # a microscopic wedge where this plane meets the cylindrical surface.
    web_normal = Vector(passage_dy, -passage_dx, passage_dy).normalized()
    tangent_point = Vector(filamentEntryAxisX, filamentEntryAxisY, filamentZ) - web_normal * (filamentDiameter / 2.0)
    tangent_height = filamentZ - filamentDiameter / 2.0 * web_normal.Z
    assert bodyTopZ < tangent_height < lugMaxZ, "infeasible: filament tangent must lie inside the upper web"
    web_wall = Plane(origin=tangent_point, z_dir=web_normal) * Box(
        100.0, 100.0, 100.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    web_region = Pos(lugNutX + lug_r, y_min, tangent_height) * Box(
        x_max - lugNutX - lug_r,
        y_max - y_min,
        z_max - tangent_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    tools.append(web_wall & web_region)

    cutter = tools[0].fuse(*tools[1:])
    shaped = body.fuse(low_web, rear_web) - cutter
    assert len(shaped.solids()) == 1, "infeasible: exterior construction must remain one connected solid"
    assert shaped.is_valid, "infeasible: exterior boolean produced an invalid solid"
    return shaped

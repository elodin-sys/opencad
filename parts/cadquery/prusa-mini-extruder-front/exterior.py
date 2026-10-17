# CadQuery must be the first executable line under the backend source contract.
import cadquery as cq  # isort: skip
import math

from params import (
    bodyTopZ,
    bottomZ,
    filamentDiameter,
    filamentDirX,
    filamentDirY,
    filamentEntryAxisX,
    filamentEntryAxisY,
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
    lugWebPeakX,
    plateThickness,
    rightBottomChamferZ,
    rightTopChamferX,
    upperLeftBossDiameter,
    upperLeftScrewX,
    upperLeftScrewZ,
)

_OVERRUN = 0.03


def _xz_prism(points, start_y, end_y):
    return cq.Workplane("XZ", origin=(0.0, start_y, 0.0)).polyline(points).close().extrude(start_y - end_y)


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY", origin=(x0, y0, z0)).box(x1 - x0, y1 - y0, z1 - z0, centered=False)


def _union(shapes):
    joined = shapes[0]
    for shape in shapes[1:]:
        joined = joined.union(shape, clean=True)
    return joined


def _normal(x, z):
    length = math.hypot(x, z)
    return x / length, z / length


def apply(body):
    assert plateThickness > 0.0, "infeasible: plateThickness must be positive"
    assert 0.0 < keyMiddleEnd < plateThickness, "infeasible: front relief must lie within the plate"
    assert bottomZ < leftShoulderZ < leftTopChamferZ < bodyTopZ < lugMaxZ, "infeasible: exterior levels must be ordered"
    assert -halfWidth < leftFootX < 0.0, "infeasible: foot must be inside the left envelope"
    assert 0.0 < upperLeftBossDiameter and 0.0 < lugBossDiameter, "infeasible: boss diameters must be positive"
    assert filamentDiameter > 0.0, "infeasible: filamentDiameter must be positive"
    assert lugNutX < lugWebPeakX < rightTopChamferX < halfWidth, "infeasible: lug and web must fit inside the top edge"

    over = _OVERRUN
    back, front = -over, plateThickness + over
    left, right = -halfWidth, halfWidth

    # Dimension-sheet inclined rows 1 and 6 take precedence over raster knees.
    shallow_x, shallow_z = _normal(-0.0872, -0.9962)
    lower_x, lower_z = _normal(-0.7373, -0.6756)
    shallow_c = shallow_x * left + shallow_z * leftShoulderZ
    lower_c = lower_x * leftDiagonalAnchorX + lower_z * leftDiagonalAnchorZ
    determinant = shallow_x * lower_z - lower_x * shallow_z
    knee_x = (shallow_c * lower_z - lower_c * shallow_z) / determinant
    knee_z = (shallow_x * lower_c - lower_x * shallow_c) / determinant
    foot_top = (lower_c - lower_x * leftFootX) / lower_z
    assert left < knee_x < leftFootX and bottomZ < foot_top < knee_z < leftShoulderZ, (
        "infeasible: foot planes do not intersect in order"
    )

    # The supplied datum has a square notch: the two bevels require this small
    # addition below its shoulder, not a cut into the already absent stock.
    foot_fill = _xz_prism(
        [
            (left, leftShoulderZ),
            (knee_x, knee_z),
            (leftFootX, foot_top),
            (leftFootX, leftShoulderZ + over),
            (left, leftShoulderZ + over),
        ],
        0.0,
        plateThickness,
    )

    left_upper = _xz_prism(
        [
            (left - over, leftTopChamferZ - over),
            (left - over, bodyTopZ + over),
            (left + bodyTopZ - leftTopChamferZ + over, bodyTopZ + over),
        ],
        back,
        front,
    )
    right_upper = _xz_prism(
        [
            (right + over, bodyTopZ + rightTopChamferX - right - over),
            (right + over, lugMaxZ + over),
            (rightTopChamferX + bodyTopZ - lugMaxZ - over, lugMaxZ + over),
        ],
        back,
        front,
    )
    right_lower = _xz_prism(
        [
            (right + over, rightBottomChamferZ + over),
            (right + over, bottomZ - over),
            (right - rightBottomChamferZ + bottomZ - over, bottomZ - over),
        ],
        back,
        front,
    )

    # Front upper-left outline: z=24 ledge, true D11 circular arc, then the
    # tabulated inclined row 10. The following keyhole cuts its lower end.
    boss_r = upperLeftBossDiameter / 2.0
    ledge_height = leftTopChamferZ - upperLeftScrewZ
    assert 0.0 < ledge_height < boss_r, "infeasible: upper-left boss must rise above its ledge"
    arc_left = upperLeftScrewX - math.sqrt(boss_r**2 - ledge_height**2)
    bevel_x, bevel_z = _normal(0.766, 0.6428)
    bevel_anchor_x = upperLeftScrewX + ledge_height
    bevel_c = bevel_x * bevel_anchor_x + bevel_z * bodyTopZ
    distance = bevel_c - bevel_x * upperLeftScrewX - bevel_z * upperLeftScrewZ
    assert 0.0 < distance < boss_r, "infeasible: boss bevel must intersect the D11 contour"
    tangent_offset = math.sqrt(boss_r**2 - distance**2)
    arc_end = (
        upperLeftScrewX + distance * bevel_x - tangent_offset * bevel_z,
        upperLeftScrewZ + distance * bevel_z + tangent_offset * bevel_x,
    )
    relief_floor = upperLeftScrewZ
    bevel_end_x = (bevel_c - bevel_z * relief_floor) / bevel_x
    lug_left = lugNutX - lugBossDiameter / 2.0
    assert left < arc_left < arc_end[0] < bevel_end_x < lug_left, (
        "infeasible: upper-left relief outline must be ordered"
    )
    front_relief = (
        cq.Workplane("XZ", origin=(0.0, keyMiddleEnd, 0.0))
        .moveTo(left - over, leftTopChamferZ)
        .lineTo(arc_left, leftTopChamferZ)
        .threePointArc((upperLeftScrewX, upperLeftScrewZ + boss_r), arc_end)
        .lineTo(bevel_end_x, relief_floor)
        .lineTo(lug_left, relief_floor)
        .lineTo(lug_left, lugMaxZ + over)
        .lineTo(left - over, lugMaxZ + over)
        .close()
        .extrude(keyMiddleEnd - front)
    )

    # Keep the D10 lug. The D4 transverse segment is tangent to this lug and
    # z=28: supply the chordal stock that filament will cut into a concave arc.
    # This is support material only; neither documented bore is cut here.
    lug_r = lugBossDiameter / 2.0
    filament_r = filamentDiameter / 2.0
    center_dx = filamentTransverseX - lugNutX
    center_dz = filamentZ - lugNutZ
    centers = math.hypot(center_dx, center_dz)
    assert centers > lug_r, "infeasible: transverse support axis must lie outside the lug"
    join_x = lugNutX + lug_r * center_dx / centers
    join_z = lugNutZ + lug_r * center_dz / centers
    assert bodyTopZ < join_z < lugMaxZ, "infeasible: transverse support must join above the ledge"
    lug = cq.Workplane("XZ", origin=(lugNutX, back, lugNutZ)).circle(lug_r).extrude(back - front)
    transverse_support = _xz_prism(
        [
            (lugNutX, bodyTopZ - over),
            (filamentTransverseX, bodyTopZ - over),
            (filamentTransverseX, bodyTopZ),
            (join_x, join_z),
            (lugNutX, join_z),
        ],
        back,
        front,
    )

    # Front web: the supplied inclined row 28 is tangent to the angled D4
    # segment. In its transverse section q points into the web and h is Z.
    # A chord leaves stock for filament's circular cut; the planar upper flank
    # uses the documented normal, without guessing a cosmetic fillet radius.
    direction_length = math.hypot(filamentDirX, filamentDirY)
    assert direction_length > 0.0 and filamentDirX > 0.0, "infeasible: angled support direction must point right"
    dx, dy = filamentDirX / direction_length, filamentDirY / direction_length
    flank_length = math.sqrt(0.2876**2 + 0.9135**2 + 0.2876**2)
    flank_sine = 0.2876 / flank_length
    flank_cosine = math.sqrt(1.0 - flank_sine**2)
    tangent_q, tangent_h = filament_r * flank_cosine, -filament_r * flank_sine
    top_h = lugMaxZ - filamentZ + over
    top_q = (filament_r + flank_sine * top_h) / flank_cosine
    q_far = 2.0 * plateThickness
    ramp_plane = cq.Plane(
        origin=(filamentEntryAxisX, filamentEntryAxisY, filamentZ), xDir=(-dy, dx, 0.0), normal=(dx, dy, 0.0)
    )
    ramp = (
        cq.Workplane(ramp_plane)
        .polyline(
            [
                (0.0, bodyTopZ - filamentZ),
                (q_far, bodyTopZ - filamentZ),
                (q_far, top_h),
                (top_q, top_h),
                (tangent_q, tangent_h),
            ]
        )
        .close()
        .extrude(2.0 * halfWidth)
    )
    # The untabulated crown transition is a simple planar connection between
    # the known lug crown and the measured web peak; no fillet is asserted.
    peak_on_bevel = rightTopChamferX + bodyTopZ - lugMaxZ
    assert lugWebPeakX <= peak_on_bevel < rightTopChamferX, "infeasible: web peak must fit under the upper-right plane"
    crown = _xz_prism(
        [
            (lugNutX, bodyTopZ - over),
            (rightTopChamferX, bodyTopZ - over),
            (rightTopChamferX, bodyTopZ),
            (peak_on_bevel, lugMaxZ),
            (lugWebPeakX, lugMaxZ),
            (lugNutX, lugNutZ + lug_r),
        ],
        back,
        front,
    )
    front_web = ramp.intersect(crown, clean=True)
    upper_keep = _union([lug, transverse_support, front_web])
    envelope = _box(left, right, 0.0, plateThickness, bottomZ, lugMaxZ)
    additions = _union([foot_fill, transverse_support.intersect(envelope), front_web.intersect(envelope)])

    # Replace only the coarse web above z=28. All cutters are combined before
    # the single subtraction from the stock. SideClamp owns the later trims
    # of both right bevels; no compensating surface shaves are made here.
    top_waste = _box(left - over, right + over, back, front, bodyTopZ, lugMaxZ + over).cut(upper_keep, clean=True)
    cutter = _union([left_upper, right_upper, right_lower, front_relief, top_waste])
    return body.union(additions, clean=True).cut(cutter, clean=True)

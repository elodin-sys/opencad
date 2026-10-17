import cadquery as cq
from params import (
    auxBoreDiameter,
    auxLowerStartY,
    auxLowerX,
    auxLowerZ,
    auxUpperStartY,
    auxUpperX,
    auxUpperZ,
    backY,
    frontY,
    lowerMountBoreLength,
    lowerMountDiameter,
    lowerMountHalfSpacing,
    lowerMountZ,
    nozzleEndZ,
    rearBoreEndY,
    rearCableNotchDiameter,
    topBoreCylinderEndZ,
    topCounterboreDepth,
    topCounterboreDiameter,
    topCounterboreFloorZ,
    topHoleAx,
    topHoleAy,
    topHoleBx,
    topHoleBy,
    topPilotDiameter,
    topPilotLength,
    topPilotStartZ,
    topZ,
    upperMountDiameter,
    upperMountHalfSpacing,
    upperMountLeftStartY,
    upperMountRightStartY,
    upperMountZ,
)

assert topPilotDiameter > 0, "infeasible: topPilotDiameter must be positive"
assert topCounterboreDiameter > topPilotDiameter, "infeasible: topCounterboreDiameter must exceed topPilotDiameter"
assert topCounterboreDepth > 0, "infeasible: topCounterboreDepth must be positive"
assert topCounterboreDepth < topBoreCylinderEndZ - topPilotStartZ, (
    "infeasible: topCounterboreDepth must leave a positive pilot under the floor"
)
assert topPilotStartZ < topBoreCylinderEndZ, "infeasible: topPilotStartZ must sit below topBoreCylinderEndZ"
assert topPilotLength > 0, "infeasible: topPilotLength must be positive"
assert topCounterboreFloorZ > topPilotStartZ, "infeasible: topCounterboreFloorZ must sit above topPilotStartZ"
assert topCounterboreFloorZ < topBoreCylinderEndZ, "infeasible: topCounterboreFloorZ must sit below topBoreCylinderEndZ"
assert topBoreCylinderEndZ < topZ, "infeasible: straight counterbore must end below the top rim"
assert rearCableNotchDiameter > 0, "infeasible: rearCableNotchDiameter must be positive"
assert upperMountDiameter > 0, "infeasible: upperMountDiameter must be positive"
assert upperMountLeftStartY < rearBoreEndY, "infeasible: left upper bore must start before its rear end"
assert upperMountRightStartY < rearBoreEndY, "infeasible: right upper bore must start before its rear end"
assert rearBoreEndY < backY, "infeasible: rear bore end must sit in front of the back datum"
assert auxBoreDiameter > 0, "infeasible: auxBoreDiameter must be positive"
assert auxLowerStartY < rearBoreEndY, "infeasible: lower aux bore must start before its rear end"
assert auxUpperStartY < rearBoreEndY, "infeasible: upper aux bore must start before its rear end"
assert lowerMountDiameter > 0, "infeasible: lowerMountDiameter must be positive"
assert lowerMountBoreLength > 0, "infeasible: lowerMountBoreLength must be positive"
assert frontY < backY, "infeasible: front face must stay forward of the back datum"

_OVERRUN = 0.04
_LEFT_RAIL_X = -14.465
_LEFT_SEAT_Y = -4.665
_LEFT_SEAT_X_OUT = -20.0
_LEFT_SEAT_Z_LO = 24.9
_LEFT_SEAT_Z_HI = 49.4
_RIGHT_SEAT_Y = -3.8
_RIGHT_SEAT_X_IN = 18.2
_RIGHT_SEAT_X_OUT = 23.96
_RIGHT_SEAT_Z_LO = 6.6
_RIGHT_SEAT_Z_HI = 45.2
_BLEND_DIA = 3.984
_RIGHT_BOSS_Z_TOP = 24.0
_UNDERSIDE_Z = 16.001
_UNDERSIDE_FLOOR_Z = nozzleEndZ + 4.16  # exterior skims to nozzleEndZ + 4.2; start 0.04 inside that air
_UNDERSIDE_X_IN = 13.85
_PAD_Y_FRONT = -15.87
_PAD_Y_BACK = -5.07
_AUX_SEAT_Y = -4.2
_AUX_WELL_HALF = 2.58
_AUX_RING_DEPTH = 0.12
_ACCESS_HALF = 2.0
_UPPER_LEFT_BOSS_DIA = 11.4
_LOWER_LEFT_BOSS_DIA = 9.4
_LOWER_RIGHT_BOSS_DIA = 6.437
_BLEND_A_DIA = 8.0
_BLEND_B_DIA = 8.0
_RELIEF_DIA = 4.0
# Contract rightObliqueReliefA/B: axis point, direction, source axis extent.
_OBLIQUE_RELIEFS = (
    ((10.323, -14.55, 6.37), (0.564, 0.6326, 0.5308), (15.231, 19.443)),
    ((8.688, -12.962, 12.986), (0.791, 0.607, 0.0766), (14.467, 17.714)),
)


def _solid(body):
    if hasattr(body, "val"):
        return body.val()
    return body


def _box(xmin, ymin, zmin, xmax, ymax, zmax):
    return cq.Solid.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, cq.Vector(xmin, ymin, zmin))


def _y_cyl(cx, cz, diameter, y0, y1):
    height = y1 - y0
    assert height > 0, "infeasible: cylinder height must be positive"
    return cq.Solid.makeCylinder(diameter / 2.0, height, cq.Vector(cx, y0, cz), cq.Vector(0, 1, 0))


def _z_cyl(cx, cy, diameter, z0, z1):
    height = z1 - z0
    assert height > 0, "infeasible: cylinder height must be positive"
    return cq.Solid.makeCylinder(diameter / 2.0, height, cq.Vector(cx, cy, z0), cq.Vector(0, 0, 1))


def _well_minus(well, *keepers):
    leftover = well
    for pin in keepers:
        leftover = leftover.cut(pin)
    return leftover


def _fuse(shapes):
    acc = shapes[0]
    for shape in shapes[1:]:
        acc = acc.fuse(shape)
    return acc


def _largest(shape):
    solids = [s for s in shape.Solids() if s.Volume() > 1e-8]
    if not solids:
        return shape
    return max(solids, key=lambda s: s.Volume())


def _restore():
    # Exterior opens y>-5.4 for |x|<13.5 and a y>-1.2 rear well. Put fastener stock back.
    # Join left pad, hole-A roof and right back pad so z=55 is one loop.
    y0 = -5.7
    roof = _box(-12.2, y0, topPilotStartZ, 8.2, backY, topZ)
    right_join = _box(7.0, y0, 52.2, 16.4, backY, 59.2)
    aux = _box(-31.0, -4.4, 16.5, -22.0, backY, 37.5)
    left = _box(-22.0, -6.05, 16.5, -12.0, backY, topZ)
    # Outer seat only. Do not refill the cavity right-wall box (x<=17.6, z=17.5-23).
    right = _box(_RIGHT_SEAT_X_IN, -7.55, _RIGHT_SEAT_Z_LO, _RIGHT_SEAT_X_OUT, backY, 46.0)
    right_boss = _box(13.25, -7.55, 16.0, 18.4, backY, _RIGHT_BOSS_Z_TOP)
    return _fuse([roof, right_join, aux, left, right, right_boss])


def _top_screws():
    floor_z = topBoreCylinderEndZ - topCounterboreDepth
    entry_dia = topCounterboreDiameter + 2.0 * (topZ - topBoreCylinderEndZ + _OVERRUN)
    tools = []
    for cx, cy in ((topHoleAx, topHoleAy), (topHoleBx, topHoleBy)):
        tools.append(_z_cyl(cx, cy, topPilotDiameter, topPilotStartZ, floor_z + _OVERRUN))
        tools.append(_z_cyl(cx, cy, topCounterboreDiameter, floor_z, topBoreCylinderEndZ + _OVERRUN))
        tools.append(_z_cyl(cx, cy, entry_dia, topBoreCylinderEndZ - _OVERRUN, topZ + _OVERRUN))
    tools.append(_z_cyl(0.0, backY, rearCableNotchDiameter, topPilotStartZ, topZ + _OVERRUN))
    return tools


def _rear_bores():
    back = backY + _OVERRUN
    return [
        _y_cyl(-upperMountHalfSpacing, upperMountZ, upperMountDiameter, upperMountLeftStartY, back),
        _y_cyl(upperMountHalfSpacing, upperMountZ, upperMountDiameter, upperMountRightStartY, back),
        _y_cyl(-lowerMountHalfSpacing, lowerMountZ, lowerMountDiameter, -lowerMountBoreLength, back),
        _y_cyl(lowerMountHalfSpacing, lowerMountZ, lowerMountDiameter, -lowerMountBoreLength, back),
    ]


def _aux_seats():
    back = backY + _OVERRUN
    tools = []
    for cx, cz, start_y in (
        (auxLowerX, auxLowerZ, auxLowerStartY),
        (auxUpperX, auxUpperZ, auxUpperStartY),
    ):
        seat_y = min(start_y, _AUX_SEAT_Y)
        tools.append(_y_cyl(cx, cz, auxBoreDiameter, seat_y, back))
        square = _box(
            cx - _AUX_WELL_HALF,
            seat_y,
            cz - _AUX_WELL_HALF,
            cx + _AUX_WELL_HALF,
            seat_y + _AUX_RING_DEPTH,
            cz + _AUX_WELL_HALF,
        )
        inner = _y_cyl(cx, cz, auxBoreDiameter + 0.04, seat_y - _OVERRUN, seat_y + _AUX_RING_DEPTH + _OVERRUN)
        tools.append(square.cut(inner))
    return tools


def _lower_access():
    y1 = -lowerMountBoreLength - _OVERRUN
    tools = []
    for cx in (-lowerMountHalfSpacing, lowerMountHalfSpacing):
        tools.append(
            _box(
                cx - _ACCESS_HALF,
                frontY - _OVERRUN,
                lowerMountZ - _ACCESS_HALF,
                cx + _ACCESS_HALF,
                y1,
                lowerMountZ + _ACCESS_HALF,
            )
        )
    return tools


def _lower_undersides():
    # Exterior skims the bottom to z=6.567 and keeps the nozzle pads (|x| 14.99..19.29, y -15.87..-5.07).
    # Start the pockets inside that skim air so the pads keep their height instead of a 0.1 mm floor,
    # stay 0.85 mm off the |x|<13 U-gap, and end the pockets on the pad faces (no sub-mm strips).
    z0 = _UNDERSIDE_FLOOR_Z
    assert z0 < _UNDERSIDE_Z, "infeasible: underside pocket floor must sit below the z=16 underside"
    left = _box(-20.0, -14.0, z0, -_UNDERSIDE_X_IN, _PAD_Y_BACK, _UNDERSIDE_Z)
    right = _box(_UNDERSIDE_X_IN, _PAD_Y_FRONT, z0, 19.51, -8.41, _UNDERSIDE_Z)
    return [left, right]


def _left_rail():
    back = backY + _OVERRUN
    y0 = _LEFT_SEAT_Y
    concave_z = 33.855
    pocket = _box(_LEFT_SEAT_X_OUT, y0, _LEFT_SEAT_Z_LO, _LEFT_RAIL_X, back, _LEFT_SEAT_Z_HI)
    # Rib overshoots the concave blend's crown lines by 0.5 mm: tangent faces there pinched the STL to zero thickness.
    rib = _box(-19.4, y0, concave_z - _BLEND_DIA / 2.0 - 0.5, -17.3, back, concave_z + _BLEND_DIA / 2.0 + 0.5)
    upper = _y_cyl(-20.147, 41.463, _BLEND_DIA, y0, back)
    lower = _y_cyl(-21.775, 27.388, _BLEND_DIA, y0, back)
    concave = _y_cyl(-18.349, concave_z, _BLEND_DIA, y0, back)
    mid_well = _box(_LEFT_SEAT_X_OUT, y0, 51.55, _LEFT_RAIL_X - 0.2, back, 58.60)
    upper_boss = _y_cyl(-upperMountHalfSpacing, upperMountZ, _UPPER_LEFT_BOSS_DIA, y0, back)
    low_well = _box(_LEFT_SEAT_X_OUT, y0, 16.50, _LEFT_RAIL_X, back, 22.90)
    lower_boss = _y_cyl(-lowerMountHalfSpacing, lowerMountZ, _LOWER_LEFT_BOSS_DIA, y0, back)
    return [
        _well_minus(pocket, rib, upper, lower),
        concave,
        _well_minus(mid_well, upper_boss),
        _well_minus(low_well, lower_boss),
    ]


def _right_seats():
    back = backY + _OVERRUN
    y0 = _RIGHT_SEAT_Y
    # Outer strip only (centroid ~[21.1, 25.9]). No inner pocket through the cavity fill.
    pocket = _box(_RIGHT_SEAT_X_IN, y0, _RIGHT_SEAT_Z_LO, _RIGHT_SEAT_X_OUT, back, _RIGHT_SEAT_Z_HI)
    mount = _y_cyl(lowerMountHalfSpacing, lowerMountZ, _LOWER_RIGHT_BOSS_DIA, y0, back)
    blend_b = _y_cyl(17.15, 19.068, _BLEND_B_DIA, y0, back)
    blend_a = _y_cyl(15.902, 20.001, _BLEND_A_DIA, -6.184, back)
    # Clip the annuli exactly at the pocket's inner face (a gap there leaves a film wall) and
    # 0.85 mm under the boss block top so the ring wells keep a real roof.
    x_clip = _RIGHT_SEAT_X_IN
    z_clip = _RIGHT_BOSS_Z_TOP - 0.85
    blend_annulus = _well_minus(
        _y_cyl(15.902, 20.001, _BLEND_A_DIA + 0.6, -6.184, back),
        blend_a,
    ).intersect(_box(13.0, -6.184, 16.0, x_clip, back, z_clip))
    blend_b_annulus = _well_minus(
        _y_cyl(17.15, 19.068, _BLEND_B_DIA + 0.6, y0, back),
        blend_b,
    ).intersect(_box(13.0, y0, 14.0, x_clip, back, z_clip))
    annulus = _well_minus(
        _y_cyl(lowerMountHalfSpacing, lowerMountZ, _LOWER_RIGHT_BOSS_DIA + 2.4, y0, back),
        mount,
    ).intersect(_box(13.0, y0, 16.0, x_clip, back, z_clip))
    tail_a = _well_minus(
        _y_cyl(15.902, 20.001, _BLEND_A_DIA + 0.6, -1.28, -0.2),
        _y_cyl(15.902, 20.001, _BLEND_A_DIA, -1.28, -0.2),
    )
    tail_b = _well_minus(
        _y_cyl(17.15, 19.068, _BLEND_B_DIA + 0.6, -1.28, -0.2),
        _y_cyl(17.15, 19.068, _BLEND_B_DIA, -1.28, -0.2),
    )
    return [
        pocket,
        blend_annulus,
        blend_b_annulus,
        annulus,
        tail_a,
        tail_b,
    ]


def _oblique_reliefs():
    # _restore() refills the right seat block over exterior's oblique reliefs; recut the same cylinders.
    tools = []
    for point, direction, (t0, t1) in _OBLIQUE_RELIEFS:
        axis = cq.Vector(*direction)
        start = cq.Vector(*point) + axis * (t0 - _OVERRUN)
        tools.append(cq.Solid.makeCylinder(_RELIEF_DIA / 2.0, t1 - t0 + 2.0 * _OVERRUN, start, axis))
    return tools


def _cut_tools():
    tools = []
    tools.extend(_top_screws())
    tools.extend(_rear_bores())
    tools.extend(_aux_seats())
    tools.extend(_lower_access())
    tools.extend(_lower_undersides())
    tools.extend(_left_rail())
    tools.extend(_right_seats())
    tools.extend(_oblique_reliefs())
    return tools


def apply(body):
    solid = _solid(body)
    solid = solid.fuse(_restore())
    solid = _largest(solid.cut(_fuse(_cut_tools())))
    return cq.Workplane("XY").newObject([solid])

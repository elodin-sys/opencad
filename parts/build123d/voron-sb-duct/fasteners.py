from build123d import Align, Box, Compound, Cylinder, Location, Plane
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
_RIGHT_SEAT_X_IN = 13.25
_RIGHT_SEAT_X_MID = 17.3
_RIGHT_SEAT_X_OUT = 28.2
_RIGHT_SEAT_Z_LO = 15.0
_RIGHT_SEAT_Z_HI = 29.15
_RIGHT_SEAT_Z_BELLY = 29.15
_RIGHT_SEAT_Z_UPPER_LO = 31.0
_RIGHT_SEAT_Z_UPPER_HI = 35.2
_RIGHT_SEAT_CONNECTOR_X = 25.0
_BLEND_DIA = 3.984
_UNDERSIDE_Z = 16.001
_AUX_SEAT_Y = -4.2
_AUX_WELL_HALF = 2.58
_UPPER_LEFT_BOSS_DIA = 11.4
_LOWER_LEFT_BOSS_DIA = 9.4
_LOWER_RIGHT_BOSS_DIA = 6.437
_BLEND_A_DIA = 8.0
_BLEND_B_DIA = 8.0
_CAVITY_BLEND_DIA = 16.0


def _box(xmin, ymin, zmin, xmax, ymax, zmax):
    return Location((xmin, ymin, zmin)) * Box(
        xmax - xmin,
        ymax - ymin,
        zmax - zmin,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def _y_cyl(cx, cz, diameter, y0, y1):
    height = y1 - y0
    assert height > 0, "infeasible: cylinder height must be positive"
    return Plane(origin=(cx, y0, cz), z_dir=(0, 1, 0)) * Cylinder(
        diameter / 2.0,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def _z_cyl(cx, cy, diameter, z0, z1):
    height = z1 - z0
    assert height > 0, "infeasible: cylinder height must be positive"
    return Location((cx, cy, z0)) * Cylinder(
        diameter / 2.0,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def _axis_cyl(point, direction, diameter, half_length):
    axis = Plane(origin=point, z_dir=direction).z_dir
    origin = (
        point[0] - axis.X * half_length,
        point[1] - axis.Y * half_length,
        point[2] - axis.Z * half_length,
    )
    return Plane(origin=origin, z_dir=direction) * Cylinder(
        diameter / 2.0,
        2.0 * half_length,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def _well_minus(well, *keepers):
    leftover = well
    for pin in keepers:
        leftover = leftover - pin
    return leftover


def _restore_pads():
    # Exterior opens y>-5.55, |x|<19.5. Restore fastener stock only. Roof block
    # between the upper bores (drawing z=55: solid from y=0 to the cavity roof);
    # it starts above the hotend roof-erase slot (z<=54.05) and stays behind the
    # exterior's y=0 pads (y<-2) outside x=-11..7.5; it meets the right pad at
    # x=7.5 (a 0.1 gap there sealed a slot that read as a hole at z=55).
    # Left stock stays below the z=54 hotend plane and clear of the hotend
    # wall zone |x|<13.15 at z<25.7; its x0 is off the x=-22 section plane.
    y0 = -5.7
    y1 = backY
    roof_z0 = topPilotStartZ + 0.1
    roof_back = _box(-13.5, y0, roof_z0, 13.5, -2.0, topZ)
    # Wings sit outside the hotend roof pad; start at 53.9 so they fuse to the side stock.
    roof_left = _box(-16.4, y0, 53.9, -13.5, -2.0, topZ)
    roof_right = _box(13.5, y0, 53.9, 16.4, -2.0, topZ)
    roof_center = _box(-11.0, y0, roof_z0, 7.5, y1, topZ)
    left_stock = _box(-22.1, y0, 16.3, -13.25, y1, 53.9)
    left_stock_upper = _box(-22.1, y0, 25.8, -12.0, y1, 53.9)
    aux_back = _box(-31.0, y0, 16.5, -22.0, y1, 37.5)
    right_inner = _box(_RIGHT_SEAT_X_IN, y0, 13.8, 19.6, y1, _RIGHT_SEAT_Z_BELLY)
    right_upper = _box(_RIGHT_SEAT_X_IN, y0, _RIGHT_SEAT_Z_UPPER_LO, 19.6, y1, _RIGHT_SEAT_Z_UPPER_HI)
    right_blend = _box(_RIGHT_SEAT_X_IN, y0, 36.0, 19.5, y1, 46.0)
    return [
        roof_back,
        roof_left,
        roof_right,
        roof_center,
        left_stock,
        left_stock_upper,
        aux_back,
        right_inner,
        right_upper,
        right_blend,
    ]


def _keep_housing(shape):
    lumps = sorted(shape.solids(), key=lambda s: s.volume, reverse=True)
    assert lumps, "infeasible: fastener boolean left no solid"
    acc = lumps[0]
    for extra in lumps[1:]:
        fused = acc + extra
        if len(fused.solids()) == 1:
            acc = fused
    return acc


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
        y0 = min(start_y, _AUX_SEAT_Y)
        tools.append(_y_cyl(cx, cz, auxBoreDiameter, y0, back))
        tools.append(
            _box(
                cx - _AUX_WELL_HALF,
                y0 - 0.12,
                cz - 0.55,
                cx + _AUX_WELL_HALF,
                y0,
                cz + 0.55,
            )
        )
    return tools


def _lower_access():
    y1 = -lowerMountBoreLength - _OVERRUN
    tools = []
    for cx in (-lowerMountHalfSpacing, lowerMountHalfSpacing):
        tools.append(
            _box(
                cx - 2.0,
                frontY,
                lowerMountZ - 2.0,
                cx + 2.0,
                y1,
                lowerMountZ + 2.0,
            )
        )
    return tools


def _lower_undersides():
    z0 = nozzleEndZ + 0.1
    # x0 stops inside the exterior's left nozzle land (x -19.64..-14.64) so the
    # land stays joined to the body at y=-12 instead of being cut free.
    left = _box(-19.0, -14.0, z0, -13.5, -5.5, _UNDERSIDE_Z)
    right = _box(12.0, -15.61, z0, 19.51, -8.41, _UNDERSIDE_Z)
    return [left, right]


def _left_rail():
    back = backY + _OVERRUN
    y0 = _LEFT_SEAT_Y - _OVERRUN
    concave_z = 33.855
    pocket = _box(_LEFT_SEAT_X_OUT, y0, _LEFT_SEAT_Z_LO, _LEFT_RAIL_X, back, _LEFT_SEAT_Z_HI)
    rib = _box(-19.4, y0, concave_z - _BLEND_DIA / 2.0, -17.3, back, concave_z + _BLEND_DIA / 2.0)
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
    y0 = _RIGHT_SEAT_Y - _OVERRUN
    inner = _box(_RIGHT_SEAT_X_IN, y0, _RIGHT_SEAT_Z_LO, _RIGHT_SEAT_X_MID, back, _RIGHT_SEAT_Z_HI)
    outer = _box(_RIGHT_SEAT_X_MID, y0, _RIGHT_SEAT_Z_LO, _RIGHT_SEAT_X_OUT, back, _RIGHT_SEAT_Z_BELLY)
    upper = _box(_RIGHT_SEAT_X_IN, y0, _RIGHT_SEAT_Z_UPPER_LO, _RIGHT_SEAT_X_OUT, back, _RIGHT_SEAT_Z_UPPER_HI)
    connector = _box(_RIGHT_SEAT_CONNECTOR_X, y0, _RIGHT_SEAT_Z_HI, _RIGHT_SEAT_X_OUT, back, _RIGHT_SEAT_Z_UPPER_LO)
    pocket = inner + outer
    mount = _y_cyl(lowerMountHalfSpacing, lowerMountZ, _LOWER_RIGHT_BOSS_DIA, y0, back)
    blend_b = _y_cyl(17.15, 19.068, _BLEND_B_DIA, y0, back)
    blend_a = _y_cyl(15.902, 20.001, _BLEND_A_DIA, -6.184 - _OVERRUN, back)
    keepers = mount + blend_b + blend_a
    blend_a_well = _box(_RIGHT_SEAT_X_IN, -6.184 - _OVERRUN, 16.0, 20.2, back, 24.0)
    relief = _y_cyl(18.491, 17.626, 20.0, _RIGHT_SEAT_Y + 0.02, _RIGHT_SEAT_Y + 0.02 + 1.191)
    # Clip floor 0.1 below the z=10 section plane so no tool face lies in it.
    relief_keep = _box(18.50, _RIGHT_SEAT_Y + 0.02, 9.9, 30.0, _RIGHT_SEAT_Y + 0.02 + 1.191, 18.0)
    relief_tool = relief & relief_keep
    # Reference: the relief is a step between the y=-3.8 seat and a y=-2.609
    # level open to the back; the strip behind it closed a hole at z=10.
    relief_step = _box(18.50, _RIGHT_SEAT_Y + 0.02 + 1.191, 9.9, 30.0, back, 18.0)
    annulus = _well_minus(
        _y_cyl(lowerMountHalfSpacing, lowerMountZ, _LOWER_RIGHT_BOSS_DIA + 3.2, y0, back),
        _y_cyl(lowerMountHalfSpacing, lowerMountZ, _LOWER_RIGHT_BOSS_DIA, y0, back),
    )
    tail_a = _well_minus(
        _y_cyl(15.902, 20.001, _BLEND_A_DIA + 0.6, -1.28, -0.25),
        _y_cyl(15.902, 20.001, _BLEND_A_DIA, -1.28, -0.25),
    )
    tail_b = _well_minus(
        _y_cyl(17.15, 19.068, _BLEND_B_DIA + 0.6, -1.28, -0.25),
        _y_cyl(17.15, 19.068, _BLEND_B_DIA, -1.28, -0.25),
    )
    cavity_pocket = _box(_RIGHT_SEAT_X_IN, y0, 36.0, 19.50, back, 46.00)
    cavity_blend = _y_cyl(10.658, 40.871, _CAVITY_BLEND_DIA, y0, back)
    return [
        _well_minus(pocket, keepers),
        upper,
        connector,
        _well_minus(blend_a_well, blend_a),
        relief_tool,
        relief_step,
        annulus,
        tail_a,
        tail_b,
        _well_minus(cavity_pocket, cavity_blend),
    ]


def _oblique_reliefs():
    clip = _box(16.0, -8.0, 10.0, 26.0, 0.5, 22.0)
    a = _axis_cyl((20.102, -3.583, 15.573), (0.564, 0.6326, 0.5308), 4.0, 2.106 + _OVERRUN)
    b = _axis_cyl((21.417, -3.196, 14.219), (0.791, 0.607, 0.0766), 4.0, 1.624 + _OVERRUN)
    return [a & clip, b & clip]


def _blend_a_tail():
    # Keep the tail inside the exterior's y=0 mount pad footprint; the arc
    # outside it stood in air as two islands at z=20.
    ring = _well_minus(
        _y_cyl(15.902, 20.001, _BLEND_A_DIA + 0.5, -1.22, -0.2),
        _y_cyl(15.902, 20.001, _BLEND_A_DIA, -1.22, -0.2),
    )
    return ring & _box(13.9, -1.3, 17.0, 19.1, backY, 22.5)


def apply(body):
    stock = body
    for pad in _restore_pads():
        stock = stock + pad
    tools = []
    tools.extend(_top_screws())
    tools.extend(_rear_bores())
    tools.extend(_aux_seats())
    tools.extend(_lower_access())
    tools.extend(_lower_undersides())
    tools.extend(_left_rail())
    tools.extend(_right_seats())
    tools.extend(_oblique_reliefs())
    cut = stock - Compound(tools)
    cut = cut + _blend_a_tail()
    return _keep_housing(cut)

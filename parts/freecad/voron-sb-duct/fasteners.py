import FreeCAD
import Part
import PartDesign  # noqa: F401
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
_RIGHT_SEAT_X_MID = 17.4
_RIGHT_SEAT_X_OUT = 29.8
_RIGHT_SEAT_Z_LO = 14.0
_RIGHT_SEAT_Z_HI = 38.0
_RIGHT_SEAT_Z_BELLY = 31.85
_BLEND_DIA = 3.984
_UNDERSIDE_Z = 16.001
_AUX_SEAT_Y = -4.2
_AUX_WELL_HALF = 2.58
_ACCESS_HALF = 2.0
_UPPER_LEFT_BOSS_DIA = 11.4
_LOWER_LEFT_BOSS_DIA = 9.4
_LOWER_RIGHT_BOSS_DIA = 6.437
_BLEND_A_DIA = 8.0
_BLEND_B_DIA = 8.0


def _largest(shape):
    solids = [s for s in getattr(shape, "Solids", []) if s.Volume > 1e-8]
    if not solids:
        return shape
    out = solids[0]
    for extra in solids[1:]:
        out = out.fuse(extra)
    if hasattr(out, "removeSplitter"):
        out = out.removeSplitter()
    return out


def _box(xmin, ymin, zmin, xmax, ymax, zmax):
    return Part.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, FreeCAD.Vector(xmin, ymin, zmin))


def _y_cyl(cx, cz, diameter, y0, y1):
    height = y1 - y0
    assert height > 0, "infeasible: cylinder height must be positive"
    return Part.makeCylinder(diameter / 2.0, height, FreeCAD.Vector(cx, y0, cz), FreeCAD.Vector(0, 1, 0))


def _z_cyl(cx, cy, diameter, z0, z1):
    height = z1 - z0
    assert height > 0, "infeasible: cylinder height must be positive"
    return Part.makeCylinder(diameter / 2.0, height, FreeCAD.Vector(cx, cy, z0), FreeCAD.Vector(0, 0, 1))


def _axis_cyl(point, direction, diameter, half_length):
    axis = FreeCAD.Vector(*direction)
    axis.normalize()
    origin = FreeCAD.Vector(*point) - axis * half_length
    return Part.makeCylinder(diameter / 2.0, 2.0 * half_length, origin, axis)


def _well_minus(*keepers):
    well = keepers[0]
    leftover = well
    for pin in keepers[1:]:
        leftover = leftover.cut(pin)
    return _largest(leftover)


def _join(parts):
    tool = parts[0]
    for extra in parts[1:]:
        tool = tool.fuse(extra)
    return _largest(tool)


def _roof_restore():
    # Stay off y=-5. Do not span the rear slot (sec_z55) or bury y=0 / z=61.5 faces.
    y0 = -4.89
    y1 = backY - 0.1
    z1 = topZ
    left_wall = _box(-16.4, y0, topPilotStartZ, -13.15, y1, z1)
    neck = _box(-13.15, -4.35, topPilotStartZ, -8.4, -3.55, z1)
    hole_a = _box(-8.4, y0, topPilotStartZ, -4.6, -1.05, z1)
    pilot_pad = _z_cyl(topHoleAx, topHoleAy, topPilotDiameter + 1.2, topPilotStartZ, 57.5)
    collar_r = topCounterboreDiameter / 2.0 + 1.0
    collar_a = _z_cyl(topHoleAx, topHoleAy, 2.0 * collar_r, 57.5, z1)
    collar_b = _z_cyl(topHoleBx, topHoleBy, 2.0 * collar_r, 57.5, z1)
    # 1.25 mm notch wall, overlapped into hole_a so the through-cut cannot leave a stub.
    cable_wall = _box(-5.3, -1.25, topPilotStartZ + 0.1, 0.2, backY, z1)
    right = _box(13.15, y0, topPilotStartZ, 16.4, y1, z1)
    aux_back = _box(-31.0, -4.4, 16.5, -22.0, y1, 37.5)
    return _join([left_wall, neck, hole_a, pilot_pad, collar_a, collar_b, cable_wall, right, aux_back])


def _right_stock():
    # rightDuct patches stop at y=-4.7; overlap the exterior mount pad and roof.
    y0 = -4.75
    y1 = backY - 0.1
    inner = _box(_RIGHT_SEAT_X_IN, y0, _RIGHT_SEAT_Z_LO, _RIGHT_SEAT_X_MID + 0.25, y1, _RIGHT_SEAT_Z_HI)
    outer = _box(_RIGHT_SEAT_X_MID - 0.25, y0, _RIGHT_SEAT_Z_LO, _RIGHT_SEAT_X_OUT, y1, _RIGHT_SEAT_Z_BELLY)
    relief_y1 = _RIGHT_SEAT_Y + 0.02 + 1.191
    relief_slab = _box(18.30, y0, 9.9, _RIGHT_SEAT_X_OUT, relief_y1, 18.2)
    mount_join = _box(13.95, -2.15, 16.9, 19.05, y1, 22.6)
    roof_web = _box(13.20, y0, 36.4, 16.35, y1, 54.2)
    return _join([inner, outer, relief_slab, mount_join, roof_web])


def _top_screws():
    floor_z = topBoreCylinderEndZ - topCounterboreDepth
    entry_dia = topCounterboreDiameter + 2.0 * (topZ - topBoreCylinderEndZ + _OVERRUN)
    tools = []
    for cx, cy in ((topHoleAx, topHoleAy), (topHoleBx, topHoleBy)):
        tools.append(_z_cyl(cx, cy, topPilotDiameter, topPilotStartZ, floor_z))
        tools.append(_z_cyl(cx, cy, topCounterboreDiameter, floor_z, topBoreCylinderEndZ))
        tools.append(_z_cyl(cx, cy, entry_dia, topBoreCylinderEndZ, topZ + _OVERRUN))
    tools.append(_z_cyl(0.0, backY, rearCableNotchDiameter, topPilotStartZ, topZ + _OVERRUN))
    return _join(tools)


def _rear_bores():
    back = backY + _OVERRUN
    tools = [
        _y_cyl(-upperMountHalfSpacing, upperMountZ, upperMountDiameter, upperMountLeftStartY, back),
        _y_cyl(upperMountHalfSpacing, upperMountZ, upperMountDiameter, upperMountRightStartY, back),
        _y_cyl(-lowerMountHalfSpacing, lowerMountZ, lowerMountDiameter, -lowerMountBoreLength, back),
        _y_cyl(lowerMountHalfSpacing, lowerMountZ, lowerMountDiameter, -lowerMountBoreLength, back),
    ]
    return _join(tools)


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
    return _join(tools)


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
    return _join(tools)


def _lower_undersides():
    z0 = nozzleEndZ + 0.1
    left = _box(-20.0, -14.0, z0, -13.5, -5.5, _UNDERSIDE_Z)
    right = _box(13.81, -15.61, z0, 19.51, -8.41, _UNDERSIDE_Z)
    return _join([left, right])


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
    return _join(
        [
            _well_minus(pocket, rib, upper, lower),
            concave,
            _well_minus(mid_well, upper_boss),
            _well_minus(low_well, lower_boss),
        ]
    )


def _right_seats():
    back = backY + _OVERRUN
    y0 = _RIGHT_SEAT_Y - _OVERRUN
    # Stay below the rightDuct belly (z=32, x>17.4) and 0.1 mm outside x=13.15.
    inner = _box(_RIGHT_SEAT_X_IN, y0, _RIGHT_SEAT_Z_LO, _RIGHT_SEAT_X_MID, back, _RIGHT_SEAT_Z_HI)
    outer = _box(_RIGHT_SEAT_X_MID, y0, _RIGHT_SEAT_Z_LO, _RIGHT_SEAT_X_OUT, back, _RIGHT_SEAT_Z_BELLY)
    relief_y0 = _RIGHT_SEAT_Y + 0.02
    relief_y1 = relief_y0 + 1.191
    relief_keep = _box(18.50, y0, 9.9, _RIGHT_SEAT_X_OUT, relief_y1, 18.0)
    pocket = _largest(inner.fuse(outer).cut(relief_keep))
    mount = _y_cyl(lowerMountHalfSpacing, lowerMountZ, _LOWER_RIGHT_BOSS_DIA, y0, back)
    blend_b = _y_cyl(17.15, 19.068, _BLEND_B_DIA, y0, back)
    blend_a = _y_cyl(15.902, 20.001, _BLEND_A_DIA, -6.184 - _OVERRUN, back)
    keepers = _join([mount, blend_b, blend_a])
    blend_a_well = _box(12.95, -6.184 - _OVERRUN, 16.0, 20.2, _RIGHT_SEAT_Y, 24.0)
    relief = _y_cyl(18.491, 17.626, 20.0, relief_y0, relief_y1)
    relief_tool = _largest(relief.common(relief_keep))
    relief_step = _box(18.50, relief_y1, 9.9, 30.0, back, 18.0)
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
    return [
        _well_minus(pocket, keepers),
        _well_minus(blend_a_well, blend_a),
        relief_tool,
        relief_step,
        annulus,
        tail_a,
        tail_b,
    ]


def _oblique_reliefs():
    a = _axis_cyl((20.102, -3.583, 15.573), (0.564, 0.6326, 0.5308), 4.0, 2.106 + _OVERRUN)
    b = _axis_cyl((21.417, -3.196, 14.219), (0.791, 0.607, 0.0766), 4.0, 1.624 + _OVERRUN)
    clip = _box(16.0, -8.0, 10.0, 26.0, 0.5, 22.0)
    return _join([_largest(a.common(clip)), _largest(b.common(clip))])


def _families():
    rows = [
        ("TopScrews", _top_screws()),
        ("RearBores", _rear_bores()),
        ("AuxSeats", _aux_seats()),
        ("LowerAccess", _lower_access()),
        ("LowerUndersides", _lower_undersides()),
        ("LeftRail", _left_rail()),
        ("ObliqueReliefs", _oblique_reliefs()),
    ]
    for i, tool in enumerate(_right_seats()):
        rows.append((f"RightSeats{i}", tool))
    return rows


def _boolean(body, tool, name, typ):
    doc = body.Document
    before = body.Shape.Volume
    host = doc.addObject("Part::Feature", name + "Cutter")
    host.Shape = tool
    tool_body = doc.addObject("PartDesign::Body", name + "ToolBody")
    tool_body.AllowCompound = True
    tool_body.BaseFeature = host
    doc.recompute()
    boolean = body.newObject("PartDesign::Boolean", name)
    boolean.addObjects([tool_body])
    boolean.Type = typ
    boolean.Refine = False
    doc.recompute()
    assert boolean.isValid(), f"kernel: {name} is invalid after recompute"
    assert body.Shape.isValid(), f"kernel: body is invalid after {name}"
    if typ == "Cut" and body.Shape.Volume >= before - 0.01:
        return None
    if typ == "Fuse" and body.Shape.Volume <= before + 0.01:
        return None
    return boolean


def apply(body):
    target = body[0] if isinstance(body, tuple) else body
    target.AllowCompound = True
    _boolean(target, _roof_restore(), "RoofRestore", "Fuse")
    _boolean(target, _right_stock(), "RightStock", "Fuse")
    for name, tool in _families():
        _boolean(target, tool, name, "Cut")
    pin_a = _y_cyl(15.902, 20.001, _BLEND_A_DIA, _RIGHT_SEAT_Y, backY - 0.1)
    pin_a = pin_a.cut(_y_cyl(lowerMountHalfSpacing, lowerMountZ, lowerMountDiameter + 0.2, _RIGHT_SEAT_Y - 0.1, backY))
    _boolean(target, _largest(pin_a), "BlendAPin", "Fuse")
    pin_b = _y_cyl(17.15, 19.068, _BLEND_B_DIA, _RIGHT_SEAT_Y, backY - 0.1)
    pin_b = pin_b.cut(_y_cyl(lowerMountHalfSpacing, lowerMountZ, lowerMountDiameter + 0.2, _RIGHT_SEAT_Y - 0.1, backY))
    _boolean(target, _largest(pin_b), "BlendBPin", "Fuse")
    tail = _well_minus(
        _y_cyl(15.902, 20.001, _BLEND_A_DIA + 0.5, -1.22, -0.2),
        _y_cyl(15.902, 20.001, _BLEND_A_DIA, -1.22, -0.2),
    )
    tail = _largest(tail.common(_box(13.9, -1.3, 17.0, 19.1, backY - 0.1, 22.5)))
    if tail.Volume > 1.0:
        _boolean(target, tail, "BlendATail", "Fuse")

    for feat in target.Group:
        if str(getattr(feat, "TypeId", "")).startswith("PartDesign::") and hasattr(feat, "isValid"):
            assert feat.isValid(), f"kernel: feature {feat.Name} is invalid"
    target.Document.recompute()
    return body

import cadquery as cq
from params import (
    backY,
    fanCenterZ,
    fanOpeningDiameter,
    frontY,
    halfWidth,
    inletCenterY,
    inletDepth,
    leftInletCenterX,
    leftInletWidth,
    nozzleEndZ,
    overallDepth,
    overallHeight,
    overallWidth,
    rightInletCenterX,
    rightInletWidth,
    topZ,
)

assert overallWidth > 0, "infeasible: overallWidth must be positive"
assert overallDepth > 0, "infeasible: overallDepth must be positive"
assert overallHeight > 0, "infeasible: overallHeight must be positive"
assert halfWidth > 0, "infeasible: halfWidth must be positive"
assert topZ > nozzleEndZ, "infeasible: topZ must sit above nozzleEndZ"
assert frontY < backY, "infeasible: frontY must sit forward of backY"
assert fanOpeningDiameter > 0, "infeasible: fanOpeningDiameter must be positive"
assert leftInletWidth > 0, "infeasible: leftInletWidth must be positive"
assert rightInletWidth > 0, "infeasible: rightInletWidth must be positive"
assert inletDepth > 0, "infeasible: inletDepth must be positive"

_OV = 0.04
_RELIEF_CLIP_X = 18.25
assert _RELIEF_CLIP_X < 18.491, "infeasible: relief clip must keep the named Ø20 axis"
_U_HALF = 13.0
_U_TOP = 16.2
_SLOT_IN = 13.0
# Side slots stop under the solid shoulders (|x| 10..14, z 24..34); screw access is fasteners' cut.
_SLOT_TOP = 24.5
_REAR_OPEN_Y = -5.4
_REAR_RECESS = 1.2
_PAD_THICK = 2.0
_FAN_DEPTH = 8.2
_INLET_CUT = 2.2
_SKIM_Z = 4.2
_HOTEND_CLEAR = 13.5
_SIDE_SHAVE = 4.0
_FAN_CLIP_Z = 56.2
_PAD_X = 2.15
_PAD_Y = 5.4

_LEFT_MAIN = (-21.5, -12.0, 19.34, 61.5)
_RIGHT_MAIN = (7.5, 16.0, 36.5, 61.5)
_RIGHT_MOUNT = (13.9, 19.1, 17.0, 22.5)
_SLOT_OUT = 17.4
_LEFT_LIP = (-19.72, -16.72, 2.367, 6.59)
_RIGHT_LIP = (16.72, 19.72, 2.367, 6.59)
_TAPER_IN = 27.0
_TAPER_Z0 = 16.0
_RIGHT_TOP_Z = 45.0
_RIGHT_TOP_X = 22.0
# Fan grille (feature cosmeticFanGrille): hub boss Ø16 centred 0.2 mm above the bore axis, held by four
# 45 deg vanes that reach past the bore rim; protected from every cut, so the grille is datum material.
_HUB_R = 8.0
_HUB_DZ = 0.2
_VANE_T = 1.2
_VANE_R0 = 4.0
_VANE_R1 = 20.0
assert _HUB_R < fanOpeningDiameter / 2.0 - 4.0, "infeasible: hub must leave a 4 mm air ring inside the bore"
assert _VANE_R1 > fanOpeningDiameter / 2.0, "infeasible: vanes must reach past the bore rim"


def _box(xmin, ymin, zmin, xmax, ymax, zmax):
    assert xmax > xmin, "infeasible: box x1 must exceed x0"
    assert ymax > ymin, "infeasible: box y1 must exceed y0"
    assert zmax > zmin, "infeasible: box z1 must exceed z0"
    return (
        cq.Workplane("XY")
        .transformed(offset=(xmin, ymin, zmin))
        .box(xmax - xmin, ymax - ymin, zmax - zmin, centered=False)
    )


def _xz_prism(pts, y0, y1):
    return cq.Workplane("XZ").workplane(offset=-y1).polyline(pts).close().extrude(y1 - y0)


def _left_taper_x(z):
    return (-38.449 + 0.2605 * z) / 0.9655


def _right_taper_x(z):
    return (38.435 - 0.2588 * z) / 0.9659


def _union(tools):
    tool = tools[0]
    for extra in tools[1:]:
        tool = tool.union(extra)
    return tool


def _pad_box(x0, x1, z0, z1, y0, y1):
    return _box(x0, y0, z0, x1, y1, z1)


def _pads():
    y0 = -_PAD_THICK
    y1 = backY + _OV
    return [
        _pad_box(*_LEFT_MAIN, y0, y1),
        _pad_box(*_RIGHT_MAIN, y0, y1),
        _pad_box(*_RIGHT_MOUNT, y0, y1),
        _pad_box(*_LEFT_LIP, y0, y1),
        _pad_box(*_RIGHT_LIP, y0, y1),
    ]


def _without_pads(stock):
    out = stock
    for pad in _pads():
        out = out.cut(pad)
    return out


def _cyl(origin, direction, radius, length):
    d = cq.Vector(*direction)
    n = d / d.Length
    solid = cq.Solid.makeCylinder(radius, length, cq.Vector(*origin), n)
    return cq.Workplane("XY").newObject([solid])


def _two_leg_tools():
    y0 = frontY - _OV
    y1 = backY + _OV
    z0 = nozzleEndZ - _OV
    left_slot = _without_pads(_box(-_SLOT_OUT, y0, _U_TOP - 0.15, -_SLOT_IN, y1, _SLOT_TOP))
    right_slot = _without_pads(_box(_SLOT_IN, y0, _U_TOP - 0.15, _SLOT_OUT, y1, _SLOT_TOP))
    return [
        _box(-_U_HALF, y0, z0, _U_HALF, y1, _U_TOP + 0.15),
        left_slot,
        right_slot,
    ]


def _rear_tools():
    y1 = backY + _OV
    slot = _without_pads(_box(-_HOTEND_CLEAR, _REAR_OPEN_Y, _U_TOP - 0.15, _HOTEND_CLEAR, y1, topZ + _OV))
    well = _without_pads(_box(-halfWidth - _OV, -_REAR_RECESS, nozzleEndZ - _OV, halfWidth + _OV, y1, topZ + _OV))
    return [slot, well]


def _nozzle_tools():
    y0 = frontY - _OV
    y1 = backY + _OV
    z0 = nozzleEndZ - _OV
    left_z = (-2.043 - 0.2416 * (-halfWidth - _OV)) / 0.9704
    right_z = (0.2416 * (halfWidth + _OV) - 2.043) / 0.9704
    left_inner = -17.96
    right_inner = 17.96
    left_pts = (
        (-halfWidth - _OV, z0),
        (left_inner, z0),
        (-halfWidth - _OV, left_z),
    )
    right_pts = (
        (halfWidth + _OV, z0),
        (right_inner, z0),
        (halfWidth + _OV, right_z),
    )
    lx, ly = -17.14, -10.47
    rx, ry = 17.14, -10.47
    skim = _box(-halfWidth - _OV, y0, z0, halfWidth + _OV, y1, nozzleEndZ + _SKIM_Z)
    keep = _union(
        [
            _box(lx - _PAD_X, ly - _PAD_Y, z0, lx + _PAD_X, ly + _PAD_Y, nozzleEndZ + _SKIM_Z + _OV),
            _box(rx - _PAD_X, ry - _PAD_Y, z0, rx + _PAD_X, ry + _PAD_Y, nozzleEndZ + _SKIM_Z + _OV),
            _pad_box(*_LEFT_LIP, -_PAD_THICK, y1),
            _pad_box(*_RIGHT_LIP, -_PAD_THICK, y1),
        ]
    )
    skim = skim.cut(keep)
    return [
        _xz_prism(left_pts, y0, y1),
        _xz_prism(right_pts, y0, y1),
        skim,
    ]


def _outer_tools():
    y0 = frontY - _OV
    y1 = backY + _OV
    z0 = nozzleEndZ - _OV
    return [
        _box(-halfWidth - _OV, y0, 54.0, -31.2, y1, topZ + _OV),
        _box(31.2, y0, 54.0, halfWidth + _OV, y1, topZ + _OV),
        _box(-halfWidth - _OV, y0, 8.0, -halfWidth + _SIDE_SHAVE, y1, 53.0),
        _box(halfWidth - _SIDE_SHAVE, y0, 8.0, halfWidth + _OV, y1, 53.0),
        _box(-halfWidth - _OV, y0, z0, -28.5, -12.0, 14.0),
        _box(28.5, y0, z0, halfWidth + _OV, -12.0, 14.0),
        _box(_RIGHT_TOP_X, -7.0, _RIGHT_TOP_Z, halfWidth + _OV, y1, topZ + _OV),
        _box(-halfWidth - _OV, y0, 48.0, -31.0, -8.0, 61.6),
        _box(31.0, y0, 48.0, halfWidth + _OV, -8.0, 61.6),
    ]


def _inlet_tools():
    z0 = topZ - _INLET_CUT
    z1 = topZ + _OV
    ly0 = inletCenterY - inletDepth / 2.0
    ly1 = inletCenterY + inletDepth / 2.0
    return [
        _box(
            leftInletCenterX - leftInletWidth / 2.0,
            ly0,
            z0,
            leftInletCenterX + leftInletWidth / 2.0,
            ly1,
            z1,
        ),
        _box(
            rightInletCenterX - rightInletWidth / 2.0,
            ly0,
            z0,
            rightInletCenterX + rightInletWidth / 2.0,
            ly1,
            z1,
        ),
    ]


def _front_tools():
    y0 = frontY - _OV
    y1 = frontY + _FAN_DEPTH
    fan = _cyl((0.0, y0, fanCenterZ), (0.0, 1.0, 0.0), fanOpeningDiameter / 2.0, _FAN_DEPTH + 2.0 * _OV)
    clip = _box(-18.9, y0, 24.0, 18.9, y1 + _OV, _FAN_CLIP_Z)
    connector = _box(-_U_HALF, y0, _U_TOP, _U_HALF, y1, 32.0)
    return [fan.intersect(clip), connector]


def _grille():
    y0 = frontY - 0.5
    depth = _FAN_DEPTH + 1.0
    zc = fanCenterZ + _HUB_DZ
    hub = _cyl((0.0, y0, zc), (0.0, 1.0, 0.0), _HUB_R, depth)
    span = _VANE_R1 - _VANE_R0
    vanes = []
    for angle in (45.0, 135.0, 225.0, 315.0):
        vane = (
            cq.Workplane("XZ")
            .workplane(offset=-(y0 + depth))
            .center(0.0, zc)
            .transformed(rotate=(0.0, 0.0, angle))
            .center(_VANE_R0 + span / 2.0, 0.0)
            .rect(span, _VANE_T)
            .extrude(depth)
        )
        vanes.append(vane)
    return _union([hub] + vanes)


def _relief_tools():
    rear = _cyl((18.491, -3.82, 17.626), (0.0, 1.0, 0.0), 10.0, 1.24)
    rear = rear.intersect(_box(_RELIEF_CLIP_X, -3.86, 7.55, 28.55, -2.54, 27.70))
    a0 = cq.Vector(10.323, -14.55, 6.37) + cq.Vector(0.564, 0.6326, 0.5308) * (15.231 - 0.04)
    b0 = cq.Vector(8.688, -12.962, 12.986) + cq.Vector(0.791, 0.607, 0.0766) * (14.467 - 0.04)
    obl_a = _cyl((a0.x, a0.y, a0.z), (0.564, 0.6326, 0.5308), 2.0, 4.292)
    obl_b = _cyl((b0.x, b0.y, b0.z), (0.791, 0.607, 0.0766), 2.0, 3.327)
    return [rear, obl_a, obl_b]


def _taper_tools():
    y0 = frontY - _OV
    y1 = backY + _OV
    z1 = topZ + _OV
    x_out = halfWidth + _OV
    z_meet = (38.449 - _TAPER_IN * 0.9655) / 0.2605
    z_meet_r = (38.435 - _TAPER_IN * 0.9659) / 0.2588
    assert z_meet > _TAPER_Z0, "infeasible: left side taper must start above the hip"
    assert z_meet < topZ, "infeasible: left side taper must meet the clamp below the top"
    assert z_meet_r > _TAPER_Z0, "infeasible: right side taper must start above the hip"
    assert z_meet_r < topZ, "infeasible: right side taper must meet the clamp below the top"
    left_pts = (
        (-x_out, _TAPER_Z0),
        (-x_out, z1),
        (-_TAPER_IN, z1),
        (-_TAPER_IN, z_meet),
        (_left_taper_x(_TAPER_Z0), _TAPER_Z0),
    )
    right_pts = (
        (x_out, _TAPER_Z0),
        (x_out, z1),
        (_TAPER_IN, z1),
        (_TAPER_IN, z_meet_r),
        (_right_taper_x(_TAPER_Z0), _TAPER_Z0),
    )
    return [_xz_prism(left_pts, y0, y1), _xz_prism(right_pts, y0, y1)]


def apply(body):
    tool = _union(
        _two_leg_tools()
        + _rear_tools()
        + _nozzle_tools()
        + _outer_tools()
        + _inlet_tools()
        + _front_tools()
        + _relief_tools()
        + _taper_tools()
    )
    tool = tool.cut(_grille())
    return body.cut(tool, clean=True)

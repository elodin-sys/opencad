import cadquery as cq
from params import (
    backY,
    fanCenterZ,
    fanOpeningDiameter,
    frontY,
    hotendCavityBottomZ,
    hotendCavityHeight,
    hotendCavityTopZ,
    hotendCavityWidth,
    lowerMountBoreLength,
    lowerMountDiameter,
    lowerMountHalfSpacing,
    lowerMountZ,
    nozzleEndZ,
    topHoleAx,
    topHoleAy,
    topHoleBx,
    topHoleBy,
    topPilotDiameter,
    topZ,
    upperMountDiameter,
    upperMountHalfSpacing,
    upperMountZ,
)

assert hotendCavityWidth > 0, "infeasible: hotendCavityWidth must be positive"
assert hotendCavityHeight > 0, "infeasible: hotendCavityHeight must be positive"
assert hotendCavityBottomZ > nozzleEndZ, "infeasible: cavity bottom must sit above the nozzle end"
assert hotendCavityTopZ > hotendCavityBottomZ, "infeasible: cavity top must sit above its bottom"
assert fanOpeningDiameter > 0, "infeasible: fanOpeningDiameter must be positive"
assert fanCenterZ > nozzleEndZ, "infeasible: fan center must sit above the nozzle end"
assert fanCenterZ < topZ, "infeasible: fan center must sit below the housing top"
assert backY > frontY, "infeasible: back datum must sit behind the front face"

_OVERRUN = 0.04
# Source walls at ±13.15 (hotendWallSpacing 26.3); driven by the 26 mm cavity width.
_POCKET_HALF = hotendCavityWidth / 2 + 0.15
_REAR_ROOF_Z = 54.0
_BRIDGE_BOTTOM_Z = 27.8
_BRIDGE_TOP_Z = 29.0
_LOWER_RELIEF_R = 11.25
_UPPER_RELIEF_R = 10.2
_DIAG_R = 8.0
_DIAG_U = 0.7071
_DIAG_ORIGIN_Y = -14.542
_DIAG_ORIGIN_Z = 14.544
_DIAG_START_T = 0.989
_LEFT_DIAG_LEN = 17.759
_RIGHT_DIAG_LEN = 15.981
_FAN_MEET_Y = -16.0
_BLEND_R = 8.0
_BLEND_X = 10.658
_BLEND_Z = 40.871
# Front mouth loft (x=0 / y=-20 sections): the solid chin fills the round bore's bottom; its top rises
# from z=24.75 at the front face on an R15.82 arc to the flat z=29.4, tangent at y=-16. The sides close
# from x=+-18.75 to the +-15.5 rounded rectangle (z 29.4..57, r12 corners so the transition floor is
# >= 1 mm over the contract's solid point (10,-18,30)). Behind y=-16 the pocket is +-12.7. No air
# behind the fan bore floor (y=-19.2).
_CHIN_R = 15.82
_CHIN_AXIS_Z = 13.58
_CHIN_TOP_Z = 29.4
_CHIN_END_Y = -12.6
# Bridge-ramp underside z = y + _RAMP_C: the contract plane (z = y + 40.4) lowered 0.35 mm along its normal.
_RAMP_C = 39.9
_SIDE_R = 21.62
_RR_HALF = 15.5
_RR_TOP_Z = 57.0
_RR_CORNER = 12.0
_CAVITY_HALF = 12.7
_CAVITY_TOP_Z = 54.4
_CAVITY_CORNER = 5.5
_ROOF_START_Y = -8.6
_FRONT_STOP_Y = frontY + 0.2
# The optional fan grille (y=-20 drawing) is omitted: the y=-20 section band is binding without it.
_ROOF_FILL_TOP_Z = 54.85

assert _POCKET_HALF > 0, "infeasible: pocket half-width must be positive"
assert _BRIDGE_BOTTOM_Z > hotendCavityBottomZ, "infeasible: bridge must sit above the cavity bottom"
assert _BRIDGE_TOP_Z > _BRIDGE_BOTTOM_Z, "infeasible: bridge must have positive thickness"
assert _REAR_ROOF_Z > hotendCavityTopZ, "infeasible: rear roof must sit above the front cavity top"
assert _LOWER_RELIEF_R < _POCKET_HALF, "infeasible: lower relief must stay inside the pocket walls"
assert _UPPER_RELIEF_R < _POCKET_HALF, "infeasible: upper relief must stay inside the pocket walls"
assert _FAN_MEET_Y > frontY, "infeasible: fan mouth must start forward of the bridge"
assert _CHIN_TOP_Z > _BRIDGE_TOP_Z, "infeasible: chin top must clear the bridge top"
assert _CHIN_TOP_Z < fanCenterZ - fanOpeningDiameter / 4.0, "infeasible: chin must stay below the fan mouth"
assert _RR_HALF > _CAVITY_HALF, "infeasible: rear mouth must be wider than the pocket"
assert _CAVITY_TOP_Z < _REAR_ROOF_Z + 0.5, "infeasible: pocket top must stay at or below the rear roof"
assert abs(_CHIN_AXIS_Z + _CHIN_R - _CHIN_TOP_Z) < 1e-6, "infeasible: chin arc must be tangent to the chin flat"
assert _CHIN_R > _FAN_MEET_Y - _FRONT_STOP_Y, "infeasible: chin arc must reach the front face"
assert 2.0 * _RR_CORNER < _RR_TOP_Z - _CHIN_TOP_Z, "infeasible: mouth corner radius must fit its height"
assert 2.0 * _RR_CORNER < 2.0 * _RR_HALF, "infeasible: mouth corner radius must fit its width"


def _box(xmin, xmax, ymin, ymax, zmin, zmax):
    assert xmax > xmin, "infeasible: box x1 must exceed x0"
    assert ymax > ymin, "infeasible: box y1 must exceed y0"
    assert zmax > zmin, "infeasible: box z1 must exceed z0"
    return cq.Solid.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, cq.Vector(xmin, ymin, zmin))


def _cyl(radius, origin, direction, t0, t1, extra=_OVERRUN):
    dx, dy, dz = direction
    length = (dx * dx + dy * dy + dz * dz) ** 0.5
    assert length > 1e-9, "infeasible: zero cylinder direction"
    ux, uy, uz = dx / length, dy / length, dz / length
    start = t0 - extra
    height = (t1 - t0) + 2.0 * extra
    assert height > 0, "infeasible: cylinder length must be positive"
    p0 = cq.Vector(origin[0] + ux * start, origin[1] + uy * start, origin[2] + uz * start)
    return cq.Solid.makeCylinder(radius, height, p0, cq.Vector(ux, uy, uz))


def _yz_prism(points_yz, xmin, xmax):
    return cq.Workplane("YZ").workplane(offset=xmin).polyline(points_yz).close().extrude(xmax - xmin).val()


def _fuse(shapes):
    acc = shapes[0]
    for shape in shapes[1:]:
        acc = acc.fuse(shape)
    return acc


def _clip(shape, xmin, xmax, ymin, ymax, zmin, zmax):
    return shape.intersect(_box(xmin, xmax, ymin, ymax, zmin, zmax))


def _rounded_y_prism(xmin, xmax, ymin, ymax, zmin, zmax, radius):
    solid = _box(xmin, xmax, ymin, ymax, zmin, zmax)
    return cq.Workplane("XY").newObject([solid]).edges("|Y").fillet(radius).val()


def _cut_tools():
    half = _POCKET_HALF
    inner = half - 1.15
    # Exterior already opened z<16.2 and the rear y>-5.4 slot; only the remaining mid-pocket.
    # y=-12 drawing: the access reaches +-12.65 at z=21 and is full width only up to z~24.6 (keeps
    # (+-12, -12, 24) void, 0.8 mm wall to the exterior's x=+-13 slot face); above it the Ø16 diagonal
    # reliefs bound the access and the corners are material.
    mid_low = _box(-inner - 0.2, inner + 0.2, -19.0, -5.55, 16.25, 24.65)
    mid_upper = _box(-7.2, 7.2, -19.0, -5.55, 24.65 - _OVERRUN, _BRIDGE_BOTTOM_Z - _OVERRUN)
    # Pocket ahead of the z=54 roof: +-12.7 wide up to z=54.4 with rounded corners (y=-12 section).
    # Starts where the mouth's rear rounded rectangle ends (y=-16): ahead of it only mouth_rear's r8
    # corners open the transition, so the contract's solid point (10,-18,30) stays material.
    pocket_front = _rounded_y_prism(
        -_CAVITY_HALF,
        _CAVITY_HALF,
        _FAN_MEET_Y - 0.05,
        _ROOF_START_Y,
        _BRIDGE_TOP_Z + _OVERRUN,
        _CAVITY_TOP_Z,
        _CAVITY_CORNER,
    )
    pocket_rear = _box(-inner, inner, _ROOF_START_Y - _OVERRUN, -5.55, _BRIDGE_TOP_Z + _OVERRUN, 50.55)
    roof_pocket = _box(-half, half, -6.95, -1.50, 50.55, _REAR_ROOF_Z + _OVERRUN)
    # Rear end of the mouth loft: +-15.5 rounded rectangle from the exterior's Ø37.5 bore
    # (ends y=-19.16) back to y=-16, clipped to this module's z<=54.5 region.
    mouth_rear = _clip(
        _rounded_y_prism(-_RR_HALF, _RR_HALF, -19.3, _FAN_MEET_Y + 0.1, _CHIN_TOP_Z, _RR_TOP_Z, _RR_CORNER),
        -_RR_HALF - 1.0,
        _RR_HALF + 1.0,
        -19.4,
        _FAN_MEET_Y + 0.2,
        _CHIN_TOP_Z - 0.1,
        _CAVITY_TOP_Z + 0.06,
    )
    lower_relief = _cyl(
        _LOWER_RELIEF_R,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        _BRIDGE_BOTTOM_Z - 0.6,
        29.362,
        extra=_OVERRUN,
    )
    upper_relief = _clip(
        _cyl(_UPPER_RELIEF_R, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 50.55, _REAR_ROOF_Z),
        -_UPPER_RELIEF_R - 1.0,
        _UPPER_RELIEF_R + 1.0,
        -3.2,
        backY - 0.1,
        50.5,
        _REAR_ROOF_Z + 0.2,
    )
    left_diag = _cyl(
        _DIAG_R,
        (-5.15, _DIAG_ORIGIN_Y, _DIAG_ORIGIN_Z),
        (0.0, _DIAG_U, _DIAG_U),
        _DIAG_START_T,
        _LEFT_DIAG_LEN,
        extra=0.05,
    )
    right_diag = _clip(
        _cyl(
            _DIAG_R,
            (5.15, _DIAG_ORIGIN_Y, _DIAG_ORIGIN_Z),
            (0.0, _DIAG_U, _DIAG_U),
            _DIAG_START_T,
            _RIGHT_DIAG_LEN,
        ),
        -3.0,
        15.8,
        -18.8,
        -5.58,
        15.45,
        29.2,
    )
    # Fastener restore skins |x|=12..13.15 at the rear; strip that film so ±13.15 stays a face.
    clear_walls = _box(-half + 0.01, half - 0.01, -8.70, backY + _OVERRUN, 17.60, 25.70)
    # 0.85 mm film between the exterior U-gap (|x|<13) and the fasteners' left underside pocket
    # (x<-13.85, y -14..-5.07, z<16.001): the reference opens that pocket into the nozzle access.
    left_film = _box(-13.90, -12.95, -14.04, -5.03, 6.55, 16.04)
    return [
        mid_low,
        mid_upper,
        pocket_front,
        pocket_rear,
        roof_pocket,
        mouth_rear,
        lower_relief,
        upper_relief,
        left_diag,
        right_diag,
        clear_walls,
        left_film,
    ]


def _fill_tools():
    half = _POCKET_HALF
    # 0.89 mm roof plate: the fasteners' roof only spans x -12.2..8.2, so a thinner shim overhangs as a film.
    roof = _box(-half, half, -6.95, -1.50, _REAR_ROOF_Z - 0.04, _ROOF_FILL_TOP_Z)
    bridge = _box(-13.15, 10.93, -10.3, -6.74, _BRIDGE_BOTTOM_Z, _BRIDGE_TOP_Z)
    right_top = _box(-0.75, 6.75, -12.04, -8.78, 28.96, _BRIDGE_TOP_Z)
    # Restore ±13.15 pocket walls in the exterior side slots. Stop 0.1 mm short of
    # exterior y=0 and fasteners y=-3.8 so those owned faces stay intact.
    left_wall = _box(-17.6, -half, -7.47, -0.12, 17.65, 25.65)
    right_wall = _box(half, 17.6, -8.41, -3.95, 17.52, 22.94)
    # Exterior side slots (13<|x|<17.4, z 16..28.4) are solid flanks in the y=-20/-12 sections;
    # span them from the front (0.2 short of the y=-27.4 face). y-gap keeps the rear wall pads
    # as their own faces; the lower-mount bores/access channels are cut back out in _fill().
    left_span = _box(-17.55, -half, _FRONT_STOP_Y, -8.55, 16.30, 28.35)
    right_span = _box(half, 17.55, _FRONT_STOP_Y, -9.50, 16.30, 28.35)
    # Solid chin between the mouth and the nozzle access: from the 45 deg bridge ramp (z=y+_RAMP_C) up to
    # the loft's bottom arc, flat z=29.4 behind the arc's tangent point y=-16. Stops 0.1 short of the
    # exterior's x=+-13 step faces (z 28.4..29.8) beside the bore.
    chin_profile = [
        (_FRONT_STOP_Y, 23.5),
        (_FRONT_STOP_Y, _CHIN_TOP_Z),
        (_CHIN_END_Y, _CHIN_TOP_Z),
        (_CHIN_END_Y, _CHIN_END_Y + _RAMP_C),
        (23.5 - _RAMP_C, 23.5),
    ]
    # Below the step faces the chin joins the side spans (x=+-13.15) so the body is one region at z=20.
    chin_prism = _yz_prism(chin_profile, -12.9, 12.9).fuse(
        _clip(_yz_prism(chin_profile, -13.2, 13.2), -13.3, 13.3, frontY - 1.0, backY, 0.0, 28.3)
    )
    chin_arc = _cyl(_CHIN_R, (0.0, _FAN_MEET_Y, _CHIN_AXIS_Z), (1.0, 0.0, 0.0), -12.9, 12.9, extra=0.5)
    chin_front = chin_prism.intersect(chin_arc)
    chin_back = chin_prism.intersect(
        _box(-12.95, 12.95, _FAN_MEET_Y - 0.05, _CHIN_END_Y + 0.1, 23.0, _CHIN_TOP_Z + 0.1)
    )
    chin = chin_front.fuse(chin_back)
    # Mouth sides: material outside the loft's side arcs, inside the exterior's Ø37.5 bore.
    side_box_z = (24.0, _CAVITY_TOP_Z + 0.06)
    left_side = _box(-19.0, -_CAVITY_HALF, _FRONT_STOP_Y, -19.0, *side_box_z).intersect(
        _cyl(_SIDE_R, (-_RR_HALF - _SIDE_R, _FAN_MEET_Y, 20.0), (0.0, 0.0, 1.0), 0.0, 36.0)
    )
    right_side = _box(_CAVITY_HALF, 19.0, _FRONT_STOP_Y, -19.0, *side_box_z).intersect(
        _cyl(_SIDE_R, (_RR_HALF + _SIDE_R, _FAN_MEET_Y, 20.0), (0.0, 0.0, 1.0), 0.0, 36.0)
    )
    # Underside (x=0 drawing): the front-underside plane from the front face back to y=-23.9, the 20 deg lower
    # ramp from there to y=-19.3, the 45 deg bridge ramp behind. Planes sit 0.15 mm below their contract
    # points (tolerance 0.75); nothing hangs below them (drawn chin bottom z~20.5 at y=-20).
    lower_ramp = _yz_prism(
        [(-24.4, 18.97), (-24.4, 25.2), (-19.3, 25.2), (-19.3, 20.82)],
        -half - 0.05,
        half + 0.05,
    )
    bridge_ramp = _yz_prism(
        [(-19.4, -19.4 + _RAMP_C), (-19.4, 26.5), (-15.5, 26.5), (-15.5, -15.5 + _RAMP_C)],
        -half + 0.5,
        half - 0.5,
    )
    front_lip = _yz_prism(
        [(-27.2, 19.70), (-27.2, 24.2), (-23.9, 24.2), (-23.9, 19.156)],
        -half - 0.05,
        half + 0.05,
    )
    # Composed y=-12: 0.1 mm nozzle films reconnected to the z=5.05 floor pads.
    # Stop 0.1 mm short of the coolingDucts walls at x=±19.2 / ±19.5.
    left_lip = _box(-18.60, -14.94, -16.20, -5.15, 2.36, 5.10)
    right_lip = _box(14.94, 18.60, -16.20, -5.15, 2.36, 5.10)
    return [
        roof,
        bridge,
        right_top,
        left_wall,
        right_wall,
        left_span,
        right_span,
        lower_ramp,
        bridge_ramp,
        front_lip,
        left_lip,
        right_lip,
        chin,
        left_side,
        right_side,
    ]


def _fill_keepouts():
    # Fasteners' lower-mount air (Ø3.4 bores y -7.5..0, 4x4 access channels from the front):
    # keep every fill out of it so screwBoreAir / lowerMountAccessAir stay void. The bore keep-out
    # is the bore's own radius so the pad hole continues the Ø3.4 cylinder instead of stepping it.
    tools = []
    for cx in (-lowerMountHalfSpacing, lowerMountHalfSpacing):
        tools.append(_cyl(lowerMountDiameter / 2.0, (cx, 0.0, lowerMountZ), (0.0, 1.0, 0.0), frontY - 0.1, backY + 0.1))
        tools.append(
            _box(cx - 2.1, cx + 2.1, frontY - 0.1, -lowerMountBoreLength + 0.06, lowerMountZ - 2.1, lowerMountZ + 2.1)
        )
    # Fasteners' top pilots (from z=54) and rear upper bores pass through the thickened roof plate.
    for px, py in ((topHoleAx, topHoleAy), (topHoleBx, topHoleBy)):
        tools.append(
            _cyl(topPilotDiameter / 2.0, (px, py, 0.0), (0.0, 0.0, 1.0), _REAR_ROOF_Z - 0.2, _ROOF_FILL_TOP_Z + 0.2)
        )
    # The upper bores bottom out at z=53.12, under the plate: notch the plate over their full width
    # instead of a chord that would leave a knife edge.
    r = upperMountDiameter / 2.0
    for cx in (-upperMountHalfSpacing, upperMountHalfSpacing):
        tools.append(_box(cx - r, cx + r, -7.1, backY + 0.1, _REAR_ROOF_Z - 0.2, upperMountZ))
    return tools


def _split_tools():
    return [
        _box(-13.2, -10.3, -10.35, -6.7, 28.95, 29.08),
        _box(-5.8, -0.75, -10.35, -6.7, 28.95, 29.08),
        _box(6.75, 11.0, -10.35, -6.7, 28.95, 29.08),
        _box(-10.3, -5.8, -10.35, -9.72, 28.95, 29.08),
        _box(-10.3, -5.8, -7.28, -6.7, 28.95, 29.08),
        _box(-0.75, 6.75, -8.76, -6.7, 28.95, 29.08),
        _box(-13.05, -11.15, -10.7, -5.35, 16.25, 21.6),
    ]


def _right_blend():
    # Stop 0.1 mm short of the exterior's y=0 back face so the pin does not merge into backRightMain.
    pin = _cyl(_BLEND_R, (_BLEND_X, 0.0, _BLEND_Z), (0.0, 1.0, 0.0), -3.8, 0.0, extra=0.02)
    return pin.intersect(_box(-16.0, _POCKET_HALF + 0.02, -3.85, backY - 0.1, 32.8, 48.9))


def _keep_largest(wp):
    sols = wp.solids().vals()
    if len(sols) <= 1:
        return wp
    sols.sort(key=lambda s: s.Volume(), reverse=True)
    return cq.Workplane("XY").newObject([sols[0]])


def apply(body):
    stock = body if isinstance(body, cq.Workplane) else cq.Workplane("XY").newObject([body])
    cut = stock.cut(_fuse(_cut_tools()), clean=True)
    if not cut.solids().vals():
        cut = stock
    fill = _fuse(_fill_tools()).cut(_fuse(_fill_keepouts()))
    assert fill.Volume() > 1.0, "infeasible: lower-mount keep-outs emptied the cavity fills"
    filled = cut.union(fill, clean=True)
    split = filled.cut(_fuse(_split_tools()), clean=True)
    if not split.solids().vals():
        split = filled
    return _keep_largest(split.union(_right_blend(), clean=True))

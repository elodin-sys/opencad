import cadquery as cq
from params import (
    backY,
    ductCount,
    ductDepth,
    ductMidCenterX,
    ductMidCenterY,
    ductWall,
    ductWidth,
    fanCenterZ,
    fanOpeningDiameter,
    frontY,
    inletCenterY,
    inletDepth,
    leftInletCenterX,
    leftInletWidth,
    nozzleEndZ,
    outletsPerDuct,
    rightInletCenterX,
    rightInletWidth,
    topZ,
    wallMinimum,
)

assert ductCount >= 1, "infeasible: ductCount must be at least one"
assert outletsPerDuct >= 2, "infeasible: each duct must fork into two outlets"
assert ductWidth > 0, "infeasible: ductWidth must be positive"
assert ductDepth > 0, "infeasible: ductDepth must be positive"
assert ductWall > 0, "infeasible: ductWall must be positive"
assert wallMinimum > 0, "infeasible: wallMinimum must be positive"
assert leftInletWidth > 0, "infeasible: leftInletWidth must be positive"
assert rightInletWidth > 0, "infeasible: rightInletWidth must be positive"
assert inletDepth > 0, "infeasible: inletDepth must be positive"
assert leftInletCenterX < 0, "infeasible: left inlet must sit on the negative-x side"
assert rightInletCenterX > 0, "infeasible: right inlet must sit on the positive-x side"
assert ductMidCenterX > 0, "infeasible: mirrored mid-duct center magnitude must be positive"

_OVER = 0.04
_INLET_Z0 = 54.2


def _box(xmin, xmax, ymin, ymax, zmin, zmax):
    assert xmax > xmin, "infeasible: box x1 must exceed x0"
    assert ymax > ymin, "infeasible: box y1 must exceed y0"
    assert zmax > zmin, "infeasible: box z1 must exceed z0"
    return cq.Solid.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, cq.Vector(xmin, ymin, zmin))


def _cyl(origin, direction, radius, height):
    return cq.Solid.makeCylinder(radius, height, cq.Vector(*origin), cq.Vector(*direction))


def _largest(shape):
    sols = cq.Workplane("XY").newObject([shape]).solids().vals()
    assert sols, "infeasible: boolean produced no solids"
    sols.sort(key=lambda item: item.Volume(), reverse=True)
    return sols[0]


def _fuse(shapes):
    acc = shapes[0]
    for shape in shapes[1:]:
        acc = acc.fuse(shape)
    return acc


def _half_cyl_x(x0, x1, yc, zc, radius, keep_back=True):
    solid = _cyl((x0, yc, zc), (1.0, 0.0, 0.0), radius, x1 - x0)
    if keep_back:
        clip = _box(x0 - _OVER, x1 + _OVER, yc, yc + radius + 1.0, zc - radius - 1.0, zc + radius + 1.0)
    else:
        clip = _box(x0 - _OVER, x1 + _OVER, yc - radius - 1.0, yc, zc - radius - 1.0, zc + radius + 1.0)
    return _largest(solid.intersect(clip))


def _plane_slab(origin, normal, u0, u1, v0, v1, depth):
    nvec = cq.Vector(*normal)
    nvec = nvec.normalized()
    helper = cq.Vector(0.0, 1.0, 0.0) if abs(nvec.y) < 0.9 else cq.Vector(1.0, 0.0, 0.0)
    xdir = nvec.cross(helper)
    if xdir.Length < 1e-9:
        xdir = nvec.cross(cq.Vector(0.0, 0.0, 1.0))
    xdir = xdir.normalized()
    plane = cq.Plane(origin=cq.Vector(*origin), xDir=xdir, normal=nvec)
    return cq.Workplane(plane).center((u0 + u1) / 2.0, (v0 + v1) / 2.0).rect(u1 - u0, v1 - v0).extrude(depth).val()


def _left_tools():
    inlet_x0 = leftInletCenterX - leftInletWidth / 2.0 - _OVER
    inlet_x1 = leftInletCenterX + leftInletWidth / 2.0
    inlet_y0 = inletCenterY - inletDepth / 2.0
    inlet_y1 = inletCenterY + inletDepth / 2.0
    hd = ductDepth / 2.0
    turn = _half_cyl_x(-24.736 - _OVER, -11.333 + _OVER, -21.953, 54.064, 10.0, keep_back=True)
    turn = _largest(
        turn.intersect(_box(-24.736 - _OVER, -11.333 + _OVER, -21.953 - _OVER, -13.15, _INLET_Z0, topZ - 0.08))
    )
    # The 3.2 mm closing needs a >= 7.6 mm clear column (0.4 mm voxels) the whole way
    # down. Exterior clamps the wall at x=-27 above z=47.5 and the fan loft holds
    # y<-15.2 for x>-18.7 below z=51, so the column runs behind the loft at
    # x=-26..-18.1, y=-14.5..-6.5; the fan-side pocket stays 1 mm off the fan.
    rear_y = ductMidCenterY + hd + 0.5
    return [
        _box(inlet_x0, inlet_x1, inlet_y0, inlet_y1, _INLET_Z0, topZ + _OVER),
        turn,
        _box(-26.05, -10.0, -23.0, inlet_y1, 54.6, 59.5),
        _box(-26.05, -18.1, -23.0, rear_y, 51.0, 57.0),
        _box(-26.05, -18.1, -14.5, rear_y, 46.0, 51.0),
        _box(-26.05, -19.7, -23.0, -14.5, 46.0, 51.0),
        _box(-26.6, -18.1, -14.5, rear_y, 42.0, 46.0),
        _box(-26.6, -19.7, -23.0, -14.5, 42.0, 46.0),
        _box(-27.2, -19.7, -24.0, -14.5, 26.0, 44.9),
        _box(-27.2, -18.1, -14.5, rear_y, 26.0, 44.9),
        # Trunk floor sits at z=21.3 so the x=-22 plane keeps a 1.1 mm web (z 20.2..21.3)
        # between the rear-branch air (bore + junction, top 20.2) and the trunk: two
        # separate holes at that station. The trunk feeds the outlet through the
        # outboard riser (x -30.5..-22.5) that crosses the web band beside the plane.
        _box(-28.5, -19.4, -18.0, rear_y, 21.3, 28.0),
        _box(-30.5, -22.5, -13.4, -6.0, 15.0, 25.5),
        _box(-23.0, -21.0, -13.3, -6.1, 16.2, 20.2),
        _box(-26.15, -24.0, -25.6, -6.5, 11.8, 18.5),
        # Round rear outlet: a Ø8 bore holds the 3.2 mm closing ball around (-26,-10,10);
        # the 5 mm exit below z=8.4 is shut by the seal so the passage stays interior.
        _cyl((-24.6, -9.6, 8.4), (0.0, 0.0, 1.0), 4.0, 10.1),
        _box(-26.0, -21.0, -12.0, -5.5, 6.4, 8.5),
        _box(-26.0, -21.0, -25.6, -17.5, 6.4, 12.7),
    ]


def _right_tools():
    inlet_x0 = rightInletCenterX - rightInletWidth / 2.0
    inlet_x1 = rightInletCenterX + rightInletWidth / 2.0
    inlet_y0 = inletCenterY - inletDepth / 2.0
    inlet_y1 = inletCenterY + inletDepth / 2.0
    front_wall = frontY + ductWall
    # Fastener right-seat pocket starts at y=-3.8; underside ends at x=19.51.
    # Exterior opening starts at x=22, y=-7, z=45; stay off that corner.
    rear_stop = -3.95
    open_y = -7.25
    open_z = 44.75
    notch_y = -7.9
    branch_x0 = 19.65
    # Mirror of the left column; the exterior right-top notch (x>22, y>-7, z>45)
    # caps y at -7.9 above z=44.1, which leaves only 6.6 mm there (still sealed).
    tools = [
        _box(inlet_x0, inlet_x1, inlet_y0, inlet_y1, 55.1, topZ + _OVER),
        _box(18.05, 21.5, inlet_y0, inlet_y1, 55.0, 60.75),
        _box(12.0, 26.05, inlet_y0, inlet_y1, 54.6, 57.5),
        _box(10.564, 19.621, -15.0, -12.9, 56.5, 60.75),
        _box(18.1, 26.05, -23.0, notch_y, 51.0, 55.5),
        _box(18.1, 26.05, -14.5, notch_y, 46.0, 51.0),
        _box(19.7, 26.05, -23.0, -14.5, 46.0, 51.0),
        _box(18.1, 26.6, -14.5, notch_y, open_z, 46.0),
        _box(19.7, 26.6, -23.0, -14.5, open_z, 46.0),
        _box(19.7, 26.9, -23.0, -14.5, 26.0, open_z),
        _box(18.1, 26.5, -14.5, notch_y, 26.0, open_z),
        _box(18.1, 26.5, notch_y, -6.0, 26.0, 44.1),
        _box(19.5, 28.0, -12.0, rear_stop, 31.5, 41.5),
        _box(19.5, 26.2, -12.0, rear_stop, 41.5, open_z),
        # Mirror of the left trunk floor / riser / junction (web z 20.2..21.3 at x=22);
        # the front-branch feed climbs to the raised trunk inside its y range.
        _box(19.4, 29.5, -18.0, -6.0, 21.3, 28.0),
        _box(22.5, 30.5, -13.4, -6.05, 15.0, 25.5),
        _box(21.0, 23.0, -13.3, -6.15, 16.2, 20.2),
        _box(23.2, 25.4, -17.9, -13.3, 15.8, 21.6),
        _box(23.2, 25.4, -22.0, -16.0, 15.8, 19.0),
        _box(23.2, 25.4, -14.0, -7.2, 15.8, 19.0),
        _box(branch_x0, 24.5, -14.0, -7.0, 6.4, 16.8),
        _cyl((24.6, -9.6, 8.4), (0.0, 0.0, 1.0), 4.0, 10.1),
        _box(branch_x0, 24.5, front_wall, -16.0, 6.4, 16.8),
    ]
    belly = _box(17.422, 28.126, -12.0, rear_stop, 32.0, 41.5)
    belly_cyl = _cyl((17.422 - _OVER, -33.8, 36.775), (1.0, 0.0, 0.0), 30.0, 10.704 + 2.0 * _OVER)
    tools.append(_largest(belly.cut(belly_cyl)))
    belly_hi = _box(17.422, 26.2, -12.0, rear_stop, 41.5, open_z)
    tools.append(_largest(belly_hi.cut(belly_cyl)))
    turn = _box(10.564, 19.621, -13.05, open_y, 56.5, 60.75)
    turn_cyl = _cyl((10.564 - _OVER, -8.519, 59.745), (1.0, 0.0, 0.0), 5.0, 9.057 + 2.0 * _OVER)
    tools.append(_largest(turn.cut(turn_cyl)))
    return tools


def _keepout():
    fan = _cyl(
        (0.0, frontY - 0.1, fanCenterZ),
        (0.0, 1.0, 0.0),
        fanOpeningDiameter / 2.0 + 0.5,
        8.6,
    )
    u_cut = _box(-13.2, 13.2, frontY - 0.1, backY + 0.1, nozzleEndZ - 0.1, 16.3)
    right_seat = _box(18.4, 24.06, -3.9, 0.15, 6.5, 45.3)
    right_under = _box(13.71, 19.61, -15.71, -8.31, 2.36, 16.11)
    right_top_open = _box(21.88, 36.0, -7.08, 0.2, 44.88, 62.0)
    rear_slot = _box(-13.6, 13.6, -5.5, 0.2, 16.0, 62.0)
    return _fuse([fan, u_cut, right_seat, right_under, right_top_open, rear_slot, _left_neck()])


def _left_neck():
    # The 3.2 mm closing seals the left duct only if its inlet channel necks below 6.4 mm
    # between the z=55 station and the mouth (exterior's mouth floor is z=59.3): keep the
    # stock across the inlet at z 56..59.5 except a 4.4 mm slot in y over the mouth width.
    inlet_x0 = leftInletCenterX - leftInletWidth / 2.0
    inlet_x1 = leftInletCenterX + leftInletWidth / 2.0
    slot = _box(inlet_x0, inlet_x1 + 0.2, inletCenterY - 2.2, inletCenterY + 2.2, 55.9, 59.6)
    return _largest(_box(-26.1, -9.9, -23.2, -6.4, 56.0, 59.5).cut(slot))


def _plane_tools():
    return [
        _plane_slab((-15.756, -0.8, 4.61), (0.971, 0.0, -0.2391), -2.4, 2.4, -2.2, 3.2, 2.0),
        _plane_slab((-14.635, -27.433, 9.123), (0.7527, 0.0698, 0.6547), 0.2, 7.0, -1.5, 3.5, 1.8),
        _plane_slab((15.756, -0.8, 4.61), (-0.971, 0.0, -0.2391), -2.4, 2.4, -2.2, 3.2, 2.0),
        _plane_slab((14.635, -27.433, 9.123), (-0.7527, 0.0698, 0.6547), -0.5, 8.5, -3.0, 6.0, 3.2),
    ]


def _scrap_tools():
    z0 = 2.32
    z1 = 16.05
    y0 = frontY - _OVER
    y1 = -0.02
    # Keep a leg boss (|x| to 29.7, y -14.2..-4.8) around the Ø8 rear outlets, widened to
    # |x| 31.7 above z=10.7 so the riser bottom (z=15) sits in solid leg material.
    left_boss = _box(-29.7, -26.1, -14.2, -4.8, z0 - 0.1, z1 + 0.1)
    left_boss_hi = _box(-31.7, -29.6, -14.2, -4.8, 10.7, z1 + 0.1)
    right_boss = _box(26.1, 29.7, -14.2, -4.8, z0 - 0.1, z1 + 0.1)
    right_boss_hi = _box(29.6, 31.7, -14.2, -4.8, 10.7, z1 + 0.1)
    return [
        _largest(_box(-35.58, -26.2, y0, y1, z0, z1).cut(left_boss).cut(left_boss_hi)),
        _largest(_box(26.2, 35.58, y0, y1, z0, z1).cut(right_boss).cut(right_boss_hi)),
        _box(-17.4, -13.05, -3.2, y1, z0, z1),
        _box(13.05, 17.4, -3.2, y1, z0, z1),
        # Nozzle access under the chin: below z=20.9 the scrap still reaches y=-19.4 (under the
        # 45 deg ramp z=y+40.4, so the slit behind the front lip drains at z=20); above it the
        # scrap starts behind the chin end (y=-12.6) so hotendCavity's chamber back wall and
        # its |x| 12..13.15 side walls stay.
        _box(-13.0, 13.0, -19.4, -11.05, 16.0, 20.9),
        _box(-13.0, 13.0, -12.6, -11.0, 16.0, 28.0),
        # Slot behind the bridge (bridge back face y=-6.74, bottom z=27.8): stop 0.14 below the
        # bridge bottom so its face keeps the y -7.2..-6.74 strip (centre tolerance is 1 mm).
        _box(-13.0, 13.0, -7.2, -5.2, 16.0, 27.66),
        _box(21.85, 35.6, -7.08, y1, 44.85, topZ + _OVER),
    ]


def _floor_pads():
    return [
        _box(-31.2, -13.3, -27.35, -1.25, 5.05, 6.75),
        _box(13.3, 31.2, -27.35, -1.25, 5.05, 6.75),
        _box(-35.534, -31.4, -11.9, -1.25, 6.6, 7.95),
        _box(31.4, 35.534, -11.9, -1.25, 6.6, 7.95),
        _box(8.0, 19.50, -14.5, -5.55, 54.6, 60.70),
        _box(8.0, 21.50, -13.0, -7.25, 60.75, topZ),
        _box(21.2, 22.8, -8.5, -7.25, 12.0, 18.0),
    ]


def apply(body):
    solid = body.val() if hasattr(body, "val") else body
    stock = _largest(solid.fuse(_fuse(_floor_pads())).clean())
    duct = _fuse(_left_tools() + _right_tools()).cut(_keepout())
    tool = duct.fuse(_fuse(_scrap_tools())).fuse(_fuse(_plane_tools()))
    assert tool.Volume() > 1.0, "infeasible: keepout emptied the cooling-duct air tool"
    out = _largest(stock.cut(tool).clean())
    envelope = _box(-35.534, 35.534, -27.4, 0.0, 2.367, 61.5)
    out = _largest(out.intersect(envelope).clean())
    return cq.Workplane("XY").newObject([out])

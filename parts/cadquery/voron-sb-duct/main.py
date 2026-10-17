import cadquery as cq
from coolingDucts import apply as apply_coolingDucts
from datum import datum
from exterior import apply as apply_exterior
from fasteners import apply as apply_fasteners
from hotendCavity import apply as apply_hotendCavity
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
    halfWidth,
    lowerMountBoreLength,
    lowerMountDiameter,
    lowerMountHalfSpacing,
    lowerMountZ,
    nozzleEndZ,
    topZ,
    upperMountDiameter,
    upperMountHalfSpacing,
    upperMountRightStartY,
    upperMountZ,
)

_OV = 0.04
_ACCESS = 2.0


def _solid(body):
    if hasattr(body, "val"):
        return body.val()
    return body


def _box(xmin, xmax, ymin, ymax, zmin, zmax):
    return cq.Solid.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, cq.Vector(xmin, ymin, zmin))


def _cyl(origin, direction, radius, height):
    return cq.Solid.makeCylinder(radius, height, cq.Vector(*origin), cq.Vector(*direction))


def _y_cyl(cx, cz, diameter, y0, y1):
    return cq.Solid.makeCylinder(diameter / 2.0, y1 - y0, cq.Vector(cx, y0, cz), cq.Vector(0, 1, 0))


def _yz_prism(points_yz, xmin, xmax):
    return cq.Workplane("YZ").workplane(offset=xmin).polyline(points_yz).close().extrude(xmax - xmin).val()


def _fuse(shapes):
    acc = shapes[0]
    for shape in shapes[1:]:
        acc = acc.fuse(shape)
    return acc


def _xz_prism(points_xz, y0, y1):
    return cq.Workplane("XZ").workplane(offset=-y1).polyline(points_xz).close().extrude(y1 - y0).val()


def _hips():
    # Outer walls from the y=-12 / y=-20 drawings: the exterior's 15 deg taper (x 33.9 at z=22 ->
    # 27 at z=47.5) sits 0.3..1.8 mm inside the drawn profile between z=28 and z=47, and the side shave
    # at |x|>31.534 removes the leg's outer face, which the drawings slope from x 32.5 (z=8) to 34.85 (z=16).
    # The z 9.4..10.55 gap keeps sec_z10 out of it, like the leg slabs.
    # The z 30..47 band is left on the taper: the y=-20 drawing puts the outer face 0.3..1.2 mm inside it there
    # (sec_y-20 budget) and sec_z45 already sits at the top of its band.
    # Hips: the exterior's side shave holds |x|<=31.534 from z=8 up to where the taper takes over (z~30.5);
    # the drawings keep the hip at 35.4 (z=16) sloping to 32 (z=30).
    hips = [(31.4, 16.05), (35.4, 16.05), (34.6, 20.0), (32.5, 28.0), (32.0, 30.5), (31.4, 30.5)]
    upper = [(27.0, 48.0), (28.7, 48.0), (28.2, 52.0), (27.0, 56.0)]
    tools = []
    for flank in (hips, upper):
        tools.append(_xz_prism(flank, -24.0, -5.5))
        tools.append(_xz_prism([(-x, z) for x, z in flank], -24.0, -5.5))
    for x0, x1, z0, z1 in ((31.50, 33.00, 8.05, 9.40), (31.50, 33.50, 10.55, 13.00), (31.50, 35.00, 13.00, 16.05)):
        tools.append(_box(x0, x1, -24.0, -1.25, z0, z1))
        tools.append(_box(-x1, -x0, -24.0, -1.25, z0, z1))
    return tools


def _largest(shape):
    sols = [s for s in shape.Solids() if s.Volume() > 1e-8]
    if not sols:
        return shape
    return max(sols, key=lambda item: item.Volume())


def _aux_seat_grooves():
    # Faces auxLowerSeat / auxUpperSeat: annular +y floors at the bore start planes. Fasteners' 0.12 mm square
    # seat rings (5.16 sq minus O4.74) are sealed voids: re-cut them 0.02 larger as open grooves and vent each
    # into its bore through a 1 mm notch in the 0.02 mm sleeve, so the O4.7 bore face stays one continuous
    # segment (rearAuxPair 2, rearAux*Bore length 4.2) and the seat is the 5.2 sq minus O4.76 annulus (9.2 mm2).
    tools = []
    for cx, cz, seat_y in ((auxLowerX, auxLowerZ, auxLowerStartY), (auxUpperX, auxUpperZ, auxUpperStartY)):
        groove = _box(cx - 2.60, cx + 2.60, seat_y - 0.02, seat_y + 0.14, cz - 2.60, cz + 2.60)
        tools.append(groove.cut(_y_cyl(cx, cz, auxBoreDiameter + 0.06, seat_y - 0.10, seat_y + 0.20)))
        tools.append(_box(cx - 0.50, cx + 0.50, seat_y - 0.02, seat_y + 0.14, cz + 2.30, cz + 2.45))
        tools.append(_box(cx - 0.50, cx + 0.50, seat_y - 0.02, seat_y + 0.14, cz - 2.45, cz - 2.30))
    return tools


def _aux_seat_plug():
    # The lower seat groove crosses the z=20 section plane, where its two side slivers would read as holes:
    # an annular plug (r 2.36..3.0, overlapping the 0.02 sleeve, never the O4.7 bore) closes the groove over
    # z 19.85..20.15; both halves stay vented to the bore through the top and bottom notches.
    cx, cz, seat_y = auxLowerX, auxLowerZ, auxLowerStartY
    ring = _y_cyl(cx, cz, 6.0, seat_y - 0.05, seat_y + 0.17).cut(
        _y_cyl(cx, cz, auxBoreDiameter + 0.02, seat_y - 0.10, seat_y + 0.22)
    )
    return ring.intersect(_box(cx - 3.1, cx + 3.1, seat_y - 0.06, seat_y + 0.18, 19.85, 20.15))


def _seals():
    return [
        _box(21.70, 22.14, -8.00, -5.50, 45.20, 59.60),
        _box(21.90, 26.60, -7.50, -6.20, 44.70, 44.98),
        _aux_seat_plug(),
    ]


def _restock():
    return [
        _box(-27.30, -26.18, -25.70, -6.40, 11.55, 16.20),
        _box(-13.20, -13.14, -7.50, -0.10, 17.60, 25.70),
        _box(-31.534, -26.20, -27.35, -11.40, 5.05, 9.40),
        _box(26.20, 31.534, -27.35, -11.40, 5.05, 9.40),
        _box(-31.534, -26.20, -27.35, -11.40, 10.55, 16.15),
        _box(26.20, 31.534, -27.35, -11.40, 10.55, 16.15),
        _box(-35.534, -26.12, -12.60, -1.20, 6.55, 8.10),
        _box(26.12, 35.534, -12.60, -1.20, 6.55, 8.10),
        # Right underside pocket refill reaches the fasteners' pocket front face (y=-15.87)
        # and the exterior skim (z=6.567) so no 0.1 mm sliver survives at z=10.
        _box(13.70, 19.70, -15.92, -8.25, 6.55, 16.05),
        # Right duct roof (z=44.75) sat 0.25 mm under the exterior right-top notch floor (z=45).
        _box(21.90, 26.30, -7.60, -3.70, 44.00, 45.10),
        *_hips(),
        # Leg-boss column |x| 28.5..29.7 ends on the exterior corner-cut face y=-12.0 inside the slab
        # slot z 9.4..10.55; the y=-12 section read it as its own loop. Fill the slot across the slabs there.
        _box(-31.60, -26.10, -12.60, -11.30, 9.30, 10.65),
        _box(26.10, 31.60, -12.60, -11.30, 9.30, 10.65),
        # hotendCavity's access T (+-7.2 above z=24.65) inside coolingDucts' chin scrap (|x|<13, y -12.6..-11).
        _box(-12.70, -7.20, -12.65, -10.90, 24.70, 28.00),
        _box(7.20, 12.70, -12.65, -10.90, 24.70, 28.00),
        _box(-12.70, -12.20, -12.65, -10.90, 20.90, 24.75),
        _box(12.20, 12.70, -12.65, -10.90, 20.90, 24.75),
        # Plate spans the T arms (x=+-7.20) and covers the O16 diagonal reliefs' y=-12 apex (z=28.40).
        _box(-12.70, 12.70, -12.65, -10.90, 27.76, 28.45),
        # Right-top notch: the exterior cuts x>22 and coolingDucts x>21.85, so the x=22 section plane
        # falls in air over y -7..0, z 45..61.5; hold the notch face at x=22.15 (the recut below).
        _box(21.80, 22.30, -7.10, -0.30, 44.00, topZ),
        _box(18.05, 18.95, -3.75, -0.08, 16.15, 24.10),
        _box(-14.80, -12.70, -21.00, -18.70, 19.80, 21.20),
        _box(12.70, 14.80, -21.00, -18.70, 19.80, 21.20),
        _box(-14.80, -13.10, -8.70, -7.35, 19.55, 20.45),
        _box(13.10, 14.80, -9.60, -8.25, 19.55, 20.45),
        _box(8.00, 19.50, -15.60, -14.30, 54.55, 56.00),
        # Exterior right slot air (z 16.05..16.30) over the shallow underside pocket cut in _recuts: solid ceiling.
        _box(13.70, 19.70, -15.92, -8.25, 16.00, 16.35),
        _box(
            upperMountHalfSpacing - 3.25,
            upperMountHalfSpacing + 3.25,
            upperMountRightStartY,
            -5.45,
            upperMountZ - 2.55,
            upperMountZ + 2.55,
        ),
    ]


def _leg_passages():
    # y=-20 drawing: the legs are hollow ducts, air from the outer wall's inner face (x 33.4 at z=16 -> 27.9 at
    # z=30) to the inner wall (25.9 -> 21.2). Open that passage inside the hips wall (|x|<31.45, wall >= 1.2 mm)
    # from the kept upper leg slab (top z=16.15; the z 9.4..10.55 slit below it stays sealed off) up to the trunk.
    # y reaches -13.0 so the pocket merges with coolingDucts' riser (y -13.4..-6) and sec_z20 keeps two holes;
    # the inner edge stays 0.6 mm clear of the x=+-22 section planes.
    pocket = [(31.45, 16.3), (25.2, 16.3), (23.6, 22.0), (22.6, 24.5), (22.6, 27.5), (31.45, 27.5)]
    tools = [
        _xz_prism(pocket, -22.9, -13.0),
        _xz_prism([(-x, z) for x, z in pocket], -22.9, -13.0),
        # Outlet throats (drawn air x 16.5..28.9 at z=8): widen coolingDucts' front outlet boxes inboard to |x| 16.6,
        # under sec_z10 and above the floor pads.
        _box(-21.05, -16.6, -23.0, -18.0, 6.9, 9.8),
        _box(16.6, 19.7, -23.0, -18.0, 6.9, 9.8),
    ]
    return tools


def _recuts():
    a0 = cq.Vector(10.323, -14.55, 6.37) + cq.Vector(0.564, 0.6326, 0.5308) * (15.231 - _OV)
    b0 = cq.Vector(8.688, -12.962, 12.986) + cq.Vector(0.791, 0.607, 0.0766) * (14.467 - _OV)
    y_back = backY + _OV
    y_front = frontY - _OV
    tools = [
        _cyl((a0.x, a0.y, a0.z), (0.564, 0.6326, 0.5308), 2.0, 4.292),
        _cyl((b0.x, b0.y, b0.z), (0.791, 0.607, 0.0766), 2.0, 3.327),
        _box(22.15, halfWidth + _OV, -7.0, y_back, 45.0, topZ + _OV),
        _box(-22.25, -21.75, -1.28, y_back, 37.35, topZ + _OV),
        _box(-22.06, -21.94, -0.10, y_back, 16.40, 37.60),
        _box(-22.10, -12.00, -0.10, y_back, 16.40, 19.32),
        _box(-22.10, -21.52, -0.10, y_back, 19.32, topZ + _OV),
        _box(-12.04, -11.88, -0.10, y_back, 53.90, topZ + _OV),
        _box(7.00, 16.50, -0.10, y_back, 16.00, 36.48),
        _box(7.00, 7.48, -0.10, y_back, 36.48, topZ + _OV),
        _box(16.02, 24.20, -0.10, y_back, 36.40, topZ + _OV),
        _box(-13.155, -13.135, -8.70, y_back, 17.55, 25.80),
        _box(13.135, 13.155, -8.70, y_back, 17.55, 25.80),
        # 0.05 mm film between the exterior U-gap (|x|<13) and coolingDucts' rear scrap
        # (13.05<|x|<17.4, y -3.2..-0.02, z<16.05): open it over its whole extent.
        _box(-13.10, -12.90, -3.25, -1.10, 2.30, 16.10),
        _box(12.90, 13.10, -3.25, -1.10, 2.30, 16.10),
        # 0.15 mm film between hotendCavity's pocket back faces (y=-5.55) and the exterior rear slot (y>-5.4).
        _box(-12.30, 12.30, -5.60, -5.30, 16.20, 50.60),
        _box(17.35, 18.25, -2.65, -1.15, 8.50, 16.30),
        # coolingDucts' O8 rear-outlet bores, recut through the |x| 26.2..31.5 leg slabs restocked above.
        _cyl((-24.6, -9.6, 8.4), (0.0, 0.0, 1.0), 4.0, 10.1),
        _cyl((24.6, -9.6, 8.4), (0.0, 0.0, 1.0), 4.0, 10.1),
        *_leg_passages(),
        *_aux_seat_grooves(),
        # lowerMountUndersideRight: shallow open pocket under the z=16.001 ceiling, joined to the nozzle U-gap
        # like hotendCavity's left_film does on the left (real air, not a sealed void).
        _box(13.85, 19.51, -15.87, -8.41, 14.50, 16.001),
        _box(12.95, 13.90, -14.00, -8.45, 14.50, 16.001),
        # coolingDucts' left outlet exit box ends exactly on y=-12.0; the y=-12 section read its face as a loop.
        _box(-26.00, -21.00, -12.30, -11.90, 6.40, 8.50),
        _box(26.50, 28.00, -13.05, -11.95, 31.50, 41.50),
        _y_cyl(
            upperMountHalfSpacing,
            upperMountZ,
            upperMountDiameter,
            upperMountRightStartY,
            backY + _OV,
        ),
    ]
    for cx in (-lowerMountHalfSpacing, lowerMountHalfSpacing):
        tools.append(_y_cyl(cx, lowerMountZ, lowerMountDiameter, -19.0, y_back))
        tools.append(
            _box(
                cx - _ACCESS,
                cx + _ACCESS,
                y_front,
                -lowerMountBoreLength + _OV,
                lowerMountZ - _ACCESS,
                lowerMountZ + _ACCESS,
            )
        )
    return tools


def integrate(body):
    solid = _solid(body)
    solid = _largest(solid.fuse(_fuse(_restock())).clean())
    solid = _largest(solid.cut(_fuse(_recuts())).clean())
    solid = _largest(solid.fuse(_fuse(_seals())).clean())
    envelope = _box(-halfWidth, halfWidth, frontY, backY, nozzleEndZ, topZ)
    solid = _largest(solid.intersect(envelope).clean())
    return cq.Workplane("XY").newObject([solid])


composed = apply_coolingDucts(apply_hotendCavity(apply_fasteners(apply_exterior(datum))))
result = integrate(composed)

import math

import cadquery as cq

envelopeMinX = -10.242
envelopeMinY = 0.0
envelopeMinZ = -10.242
envelopeSizeX = 20.483
envelopeSizeY = 4.0
envelopeSizeZ = 20.483
discThickness = 3.0
hexFloorY = 1.0
hexPocketFlat = 3.463
hexBossFlat = 4.332
hexPocketVertex = 4.0
hexBossVertex = 5.0
boreDiameter = 3.1
boreLength = 1.0
rootDiameter = 19.0
tipFilletDiameter = 0.2
tipCircleRadius = 10.142
toothCount = 36.0
toothPhase = 0.0
hubHeight = 1.0
hexPocketDepth = 3.0
hexPocketAcross = 6.926
hexBossAcross = 8.664
boreRadius = 1.55
rootRadius = 9.5
tipFilletRadius = 0.1
tipOuterRadius = 10.242
toothPitchDeg = 10.0
gearModule = 0.569

assert envelopeSizeY > discThickness, "infeasible: envelopeSizeY must exceed discThickness"
assert discThickness > 0, "infeasible: discThickness must be positive"
assert hexFloorY > envelopeMinY, "infeasible: hexFloorY must sit above the circular face"
assert hexFloorY < envelopeSizeY, "infeasible: hexFloorY must sit below the boss cap"
assert tipOuterRadius > 0, "infeasible: tipOuterRadius must be positive"
assert hexBossVertex > 0, "infeasible: hexBossVertex must be positive"
assert envelopeSizeX > 0, "infeasible: envelopeSizeX must be positive"
assert envelopeSizeZ > 0, "infeasible: envelopeSizeZ must be positive"
assert envelopeMinX < 0, "infeasible: envelopeMinX must be on the -x side of the axis"
assert envelopeMinZ < 0, "infeasible: envelopeMinZ must be on the -z side of the axis"
assert hexPocketFlat > 0, "infeasible: hexPocketFlat must be positive"
assert hexBossFlat > 0, "infeasible: hexBossFlat must be positive"
assert hexPocketVertex > 0, "infeasible: hexPocketVertex must be positive"
assert hexPocketFlat < hexBossFlat, "infeasible: hex pocket must sit inside the boss flats"
assert hexPocketVertex < hexBossVertex, "infeasible: hex pocket must sit inside the boss vertices"
assert boreDiameter > 0, "infeasible: boreDiameter must be positive"
assert boreLength > 0, "infeasible: boreLength must be positive"
assert rootDiameter > 0, "infeasible: rootDiameter must be positive"
assert tipFilletDiameter > 0, "infeasible: tipFilletDiameter must be positive"
assert tipCircleRadius > rootRadius, "infeasible: tipCircleRadius must sit outside the root"
assert toothCount > 0, "infeasible: toothCount must be positive"
assert toothPhase >= 0, "infeasible: toothPhase must be non-negative"
assert hubHeight > 0, "infeasible: hubHeight must be positive"
assert hexPocketDepth > 0, "infeasible: hexPocketDepth must be positive"
assert hexPocketAcross > 0, "infeasible: hexPocketAcross must be positive"
assert hexBossAcross > 0, "infeasible: hexBossAcross must be positive"
assert boreRadius > 0, "infeasible: boreRadius must be positive"
assert rootRadius > 0, "infeasible: rootRadius must be positive"
assert tipFilletRadius > 0, "infeasible: tipFilletRadius must be positive"
assert toothPitchDeg > 0, "infeasible: toothPitchDeg must be positive"
assert gearModule > 0, "infeasible: gearModule must be positive"

_n_teeth = round(toothCount)
assert abs(_n_teeth - toothCount) < 1e-6, "infeasible: toothCount must be a whole number"
_cut_overshoot = 0.05
_flank_spread_deg = 59.59


def _plane_xy(world_x, world_z):
    return (world_x, -world_z)


def _root_hit(nx, nz, tx, tz):
    d = nx * tx + nz * tz
    px, pz = -nz, nx
    disc = rootRadius * rootRadius - d * d
    assert disc > 0.0, "infeasible: tooth flank misses the root cylinder"
    s = math.sqrt(disc)
    cands = (
        (d * nx + s * px, d * nz + s * pz),
        (d * nx - s * px, d * nz - s * pz),
    )
    return min(cands, key=lambda p: (p[0] - tx) ** 2 + (p[1] - tz) ** 2)


def _tooth_pts(k):
    theta = math.radians(toothPhase + k * toothPitchDeg)
    phi = math.radians(_flank_spread_deg)
    cx = tipCircleRadius * math.cos(theta)
    cz = tipCircleRadius * math.sin(theta)
    n_tr = (math.cos(theta - phi), math.sin(theta - phi))
    n_ld = (math.cos(theta + phi), math.sin(theta + phi))
    t_tr = (cx + tipFilletRadius * n_tr[0], cz + tipFilletRadius * n_tr[1])
    t_ld = (cx + tipFilletRadius * n_ld[0], cz + tipFilletRadius * n_ld[1])
    tip = (tipOuterRadius * math.cos(theta), tipOuterRadius * math.sin(theta))
    r_tr = _root_hit(n_tr[0], n_tr[1], t_tr[0], t_tr[1])
    r_ld = _root_hit(n_ld[0], n_ld[1], t_ld[0], t_ld[1])
    return t_tr, tip, t_ld, r_tr, r_ld


def _root_mid(r_from, r_to):
    a1 = math.atan2(r_from[1], r_from[0])
    a2 = math.atan2(r_to[1], r_to[0])
    if a2 < a1:
        a2 += 2.0 * math.pi
    amid = 0.5 * (a1 + a2)
    return (rootRadius * math.cos(amid), rootRadius * math.sin(amid))


def _hex_pts(flat, vertex):
    return [
        _plane_xy(0.0, vertex),
        _plane_xy(flat, 0.5 * vertex),
        _plane_xy(flat, -0.5 * vertex),
        _plane_xy(0.0, -vertex),
        _plane_xy(-flat, -0.5 * vertex),
        _plane_xy(-flat, 0.5 * vertex),
    ]


_along_y = cq.Plane(
    origin=(0.0, envelopeMinY, 0.0),
    xDir=(1.0, 0.0, 0.0),
    normal=(0.0, 1.0, 0.0),
)
_disc = cq.Workplane(_along_y)
for _k in range(_n_teeth):
    _t_tr, _tip, _t_ld, _r_tr, _r_ld = _tooth_pts(_k)
    _t_tr_n, _, _, _r_tr_n, _ = _tooth_pts(_k + 1)
    if _k == 0:
        _disc = _disc.moveTo(*_plane_xy(*_t_tr))
    _disc = _disc.threePointArc(_plane_xy(*_tip), _plane_xy(*_t_ld)).lineTo(*_plane_xy(*_r_ld))
    _disc = _disc.threePointArc(_plane_xy(*_root_mid(_r_ld, _r_tr_n)), _plane_xy(*_r_tr_n))
    if _k < _n_teeth - 1:
        _disc = _disc.lineTo(*_plane_xy(*_t_tr_n))
_disc = _disc.close().extrude(discThickness)

_boss_plane = cq.Plane(
    origin=(0.0, discThickness, 0.0),
    xDir=(1.0, 0.0, 0.0),
    normal=(0.0, 1.0, 0.0),
)
_boss = (
    cq.Workplane(_boss_plane)
    .polyline(_hex_pts(hexBossFlat, hexBossVertex))
    .close()
    .extrude(envelopeSizeY - discThickness)
)

_pocket_plane = cq.Plane(
    origin=(0.0, hexFloorY, 0.0),
    xDir=(1.0, 0.0, 0.0),
    normal=(0.0, 1.0, 0.0),
)
_pocket = (
    cq.Workplane(_pocket_plane)
    .polyline(_hex_pts(hexPocketFlat, hexPocketVertex))
    .close()
    .extrude(envelopeSizeY - hexFloorY + _cut_overshoot)
)
_bore_plane = cq.Plane(
    origin=(0.0, envelopeMinY - _cut_overshoot, 0.0),
    xDir=(1.0, 0.0, 0.0),
    normal=(0.0, 1.0, 0.0),
)
_bore = cq.Workplane(_bore_plane).circle(boreRadius).extrude(boreLength + 2.0 * _cut_overshoot)
_cutters = _pocket.union(_bore)

result = _disc.union(_boss).cut(_cutters, clean=True)

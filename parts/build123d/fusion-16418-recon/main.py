from math import atan2, cos, pi, radians, sin, sqrt

from build123d import (
    Align,
    Compound,
    Cylinder,
    Edge,
    Face,
    Plane,
    Pos,
    RegularPolygon,
    Rot,
    Wire,
    extrude,
)

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
toothCount = 36
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

assert tipOuterRadius > 0, "infeasible: tipOuterRadius must be positive"
assert discThickness > 0, "infeasible: discThickness must be positive"
assert hexBossVertex > 0, "infeasible: hexBossVertex must be positive"
assert hexPocketVertex > 0, "infeasible: hexPocketVertex must be positive"
assert rootRadius > 0, "infeasible: rootRadius must be positive"
assert boreRadius > 0, "infeasible: boreRadius must be positive"
assert tipFilletRadius > 0, "infeasible: tipFilletRadius must be positive"
assert toothCount >= 3, "infeasible: toothCount must be at least 3"
assert envelopeSizeY > discThickness, "infeasible: envelopeSizeY must exceed discThickness"
assert hexFloorY > envelopeMinY, "infeasible: hexFloorY must sit above the circular face"
assert hexFloorY < envelopeSizeY, "infeasible: hexFloorY must stay below the boss cap"
assert hexPocketVertex < hexBossVertex, "infeasible: hex pocket must fit inside the boss"


def _pt(x: float, z: float) -> tuple[float, float, float]:
    return (x, z, 0.0)


def _root_hit(px: float, pz: float, dx: float, dz: float) -> tuple[float, float]:
    mag = sqrt(dx * dx + dz * dz)
    dx, dz = dx / mag, dz / mag
    b = 2.0 * (px * dx + pz * dz)
    c = px * px + pz * pz - rootRadius * rootRadius
    disc = b * b - 4.0 * c
    assert disc >= 0.0, "infeasible: tooth flank misses the root cylinder"
    t1 = (-b - sqrt(disc)) / 2.0
    t2 = (-b + sqrt(disc)) / 2.0
    hits = [t for t in (t1, t2) if t > 1e-8]
    assert hits, "infeasible: tooth flank misses the root cylinder"
    t = min(hits)
    return (px + t * dx, pz + t * dz)


_n_teeth = int(toothCount)
_teeth: list[tuple] = []
for _k in range(_n_teeth):
    _th = radians(toothPhase + _k * toothPitchDeg)
    _ct, _st = cos(_th), sin(_th)
    _cx, _cz = tipCircleRadius * _ct, tipCircleRadius * _st
    _ncw = (cos(_th - radians(59.0)), sin(_th - radians(59.0)))
    _nccw = (cos(_th + radians(59.0)), sin(_th + radians(59.0)))
    _tcw = (_cx + tipFilletRadius * _ncw[0], _cz + tipFilletRadius * _ncw[1])
    _tccw = (_cx + tipFilletRadius * _nccw[0], _cz + tipFilletRadius * _nccw[1])
    _tip = (_cx + tipFilletRadius * _ct, _cz + tipFilletRadius * _st)
    _rcw = _root_hit(_tcw[0], _tcw[1], _ncw[1], -_ncw[0])
    _rccw = _root_hit(_tccw[0], _tccw[1], -_nccw[1], _nccw[0])
    _teeth.append((_rcw, _tcw, _tip, _tccw, _rccw))

_edges: list[Edge] = []
for _k, (_rcw, _tcw, _tip, _tccw, _rccw) in enumerate(_teeth):
    _nrcw = _teeth[(_k + 1) % _n_teeth][0]
    _a0 = atan2(_rccw[1], _rccw[0])
    _a1 = atan2(_nrcw[1], _nrcw[0])
    _amid = _a0 + 0.5 * ((_a1 - _a0) % (2.0 * pi))
    _rmid = (rootRadius * cos(_amid), rootRadius * sin(_amid))
    _edges.append(Edge.make_line(_pt(*_rcw), _pt(*_tcw)))
    _edges.append(Edge.make_three_point_arc(_pt(*_tcw), _pt(*_tip), _pt(*_tccw)))
    _edges.append(Edge.make_line(_pt(*_tccw), _pt(*_rccw)))
    _edges.append(Edge.make_three_point_arc(_pt(*_rccw), _pt(*_rmid), _pt(*_nrcw)))

_toothed = Face(Wire(_edges))
disc = Pos(0, envelopeMinY + discThickness, 0) * extrude(Plane.XZ * _toothed, amount=discThickness)
_boss_over = 0.05
boss = Pos(0, envelopeMinY + envelopeSizeY, 0) * extrude(
    Plane.XZ * RegularPolygon(hexBossVertex, 6, rotation=30),
    amount=envelopeSizeY - discThickness + _boss_over,
)
_cut_over = 0.05
pocket = Pos(0, envelopeMinY + envelopeSizeY + _cut_over, 0) * extrude(
    Plane.XZ * RegularPolygon(hexPocketVertex, 6, rotation=30),
    amount=envelopeSizeY - hexFloorY + _cut_over,
)
bore = (
    Pos(0, envelopeMinY - _cut_over, 0)
    * Rot(-90, 0, 0)
    * Cylinder(
        boreRadius,
        hexFloorY - envelopeMinY + 2.0 * _cut_over,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
)
result = disc + boss - Compound(children=[pocket, bore])

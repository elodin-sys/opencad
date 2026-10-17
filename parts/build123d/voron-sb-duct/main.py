from build123d import Align, Box, Compound, Cylinder, Location, Plane
from datum import datum
from exterior import apply as apply_exterior
from fasteners import _rear_bores, _top_screws
from fasteners import apply as apply_fasteners
from hotendCavity import apply as apply_hotendCavity
from leftDuct import apply as apply_leftDuct
from params import backY, nozzleEndZ, topZ
from rightDuct import apply as apply_rightDuct


def _box(x0, y0, z0, x1, y1, z1):
    return Location((x0, y0, z0)) * Box(
        x1 - x0,
        y1 - y0,
        z1 - z0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def _y_cyl(cx, cz, radius, y0, y1):
    return Plane(origin=(cx, y0, cz), z_dir=(0, 1, 0)) * Cylinder(
        radius, y1 - y0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )


def _x_cyl(cy, cz, radius, x0, x1):
    return Plane(origin=(x0, cy, cz), z_dir=(1, 0, 0)) * Cylinder(
        radius, x1 - x0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )


def _vol(shape):
    if shape is None or not shape.solids():
        return 0.0
    return float(shape.volume)


def _and(a, b):
    out = a & b
    return out if _vol(out) > 0.02 else None


def _largest(shape):
    lumps = sorted(shape.solids(), key=lambda s: s.volume, reverse=True)
    assert lumps, "infeasible: integrate boolean left no solid"
    acc = lumps[0]
    for extra in lumps[1:]:
        fused = acc + extra
        if len(fused.solids()) == 1:
            acc = fused
    return acc


def _stolen_keepout():
    # Leave fastener-owned lower access / seats and every fastener bore alone.
    return Compound(
        [
            _box(12.9, -27.4, 6.5, 18.2, -2.5, 29.0),
            _box(13.15, -3.84, 13.8, 28.3, backY, 46.1),
            *_top_screws(),
            *_rear_bores(),
        ]
    )


after_ext = apply_exterior(datum)
after_hot = apply_hotendCavity(after_ext)
after_left = apply_leftDuct(after_hot)
after_right = apply_rightDuct(after_left)
after_fast = apply_fasteners(after_right)

right_added = after_right - after_left
fast_removed = after_right - after_fast
fast_added = after_fast - after_right
hot_cut = after_ext - after_hot

body = after_fast

# Reveal rightDuctConvexTurn: the right-blend pad covers the pin to x=19.5. Run the cut
# through the seat-pocket floors (y=-3.84) into their air; stopping at -3.86 left a 0.02 mm
# skin (wall p05 0.25, extra hole at z=45). Keep the r=8 cavity blend pin.
blend_pin = _y_cyl(10.658, 40.871, 8.0, -4.5, 0.5)
cover = _and(fast_added, _box(17.40, -8.10, 32.0, 19.55, -3.80, 46.1) - blend_pin)
if cover is not None:
    body = body - cover

fill_hot = _and(fast_added, hot_cut)
if fill_hot is not None:
    body = body - fill_hot

stolen = _and(right_added, fast_removed)
if stolen is not None:
    keep = stolen - _stolen_keepout()
    if _vol(keep) > 0.02:
        body = body + keep

# rightDuctConvexTurn (r 30 about y -33.8, z 36.775) vs the fasteners' seat pockets behind it.
# Lower crescent (z 32..35.05) lies behind the upper seat (z 31..35.2, floor y=-3.84) with a
# 0.01 mm skin between: fill it up to the floor plane so the rightRearSeat floor keeps its
# full area (cutting the floor away instead left it at 187 mm2). Upper crescent (z 38.5..46)
# outboard of the cavity pocket: open the rear plate into the y>-1.2 well so it is not an
# enclosed hole at z=45. Keep the turn surface there and the 0.9 mm web at x 21.55..22.45.
turn = _x_cyl(-33.8, 36.775, 30.0, 17.0, 29.0)
body = body + (_box(17.40, -4.30, 32.0, 28.2, -3.84, 35.2) - turn)
body = body - (_box(22.40, -3.95, 36.0, 28.15, -1.15, 46.05) - turn)

# Fastener undersides (z 2.467..16) hollow the exterior's nozzle lands to 0.1 mm floors and
# 0.11-0.28 mm skins; put the land blocks back as the duct stages left them (z<=6.6 only, so
# the z=16 underside faces stay).
for x0, x1 in ((14.64, 19.64), (-19.64, -14.64)):
    land = _and(after_right, _box(x0, -15.72, nozzleEndZ - 0.04, x1, -5.22, 6.6))
    if land is not None:
        body = body + land

# Pinch: the fasteners' rail rib (z 31.863..35.847) spans exactly the concave blend's
# diameter, so its corner slivers meet the cylinder tangentially along x=-18.349; trim the
# tangent lines away (0.24-0.3 mm off the rib top and bottom, 0.015 into the seat floor).
body = body - Compound(
    [
        _box(-19.45, -4.72, 35.60, -17.25, backY + 0.05, 35.90),
        _box(-19.45, -4.72, 31.82, -17.25, backY + 0.05, 32.10),
    ]
)

# Isolate named y=0 pads from fused sibling plates (the left groove sits inside the fastener
# left-stock face, clear of the x=-22 section plane and of the aux_back pad edge at x=-22).
body = body - _box(16.05, -0.15, 22.6, 16.25, backY, topZ)
body = body - _box(-21.95, -0.15, 16.2, -21.30, backY, 54.0)
body = body - _box(-11.22, -0.15, 53.9, -11.0, backY, topZ)

result = _largest(body)

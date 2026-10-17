"""Neck flares and blind insert seat, preserving the shared shoulder boundary."""

from build123d import Align, Box, Compound, Cylinder, Pos
from exterior import clearance_loft
from params import (
    boreDiameter,
    boreFloorY,
    bossAxisZ,
    bossBackY,
    bossFilletRadius,
    bossRadius,
    envelopeMaxY,
    mountMinZ,
    neckClearance,
    neckFlareRadius,
    neckFlareTangentY,
    neckHalfWidth,
    plateThickness,
    plateTopZ,
    shoulderY,
)


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def apply(body):
    assert 0 < boreDiameter / 2 < bossRadius, "bore must retain a boss wall"
    assert bossBackY < boreFloorY < envelopeMaxY, "blind floor must lie inside boss"
    assert neckFlareTangentY > shoulderY, "flare must end above shoulder"
    assert neckClearance > 0, "neck clearance must be positive"
    under = plateTopZ - plateThickness
    r = bossFilletRadius
    assert 0 < r < plateThickness, "underside fillet must fit plate transition"
    assert bossAxisZ - bossRadius < under - r, "fillet must retain boss back face"
    overrun = 0.03
    # Fill only the concave junction behind the existing boss. The extended R4
    # profile limits this transition at its sides without duplicating the boss.
    support = Pos(0, bossBackY - r, bossAxisZ) * Cylinder(
        bossRadius,
        r + overrun,
        rotation=(-90, 0, 0),
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    support = support & _box(
        -bossRadius - overrun,
        bossRadius + overrun,
        bossBackY - r,
        bossBackY + overrun,
        under - r,
        under + overrun,
    )
    rounding = Pos(-bossRadius - overrun, bossBackY - r, under - r) * Cylinder(
        r,
        2 * (bossRadius + overrun),
        rotation=(0, 90, 0),
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    support = support - rounding
    stock = body + support
    tools = []
    # Stop the concave arcs at their tangencies: a full circle would also
    # remove the straight neck forward of the tangent station.
    half_span = neckHalfWidth + neckFlareRadius
    region = _box(
        -half_span - 0.02,
        half_span + 0.02,
        shoulderY,
        envelopeMaxY + overrun,
        mountMinZ - overrun,
        plateTopZ + overrun,
    )
    arc_region = _box(
        -half_span - 0.02,
        half_span + 0.02,
        shoulderY,
        neckFlareTangentY,
        under - overrun,
        plateTopZ + overrun,
    )
    for sign in (-1, 1):
        flare = Pos(sign * half_span, neckFlareTangentY, under - overrun) * Cylinder(
            neckFlareRadius,
            plateThickness + 2 * overrun,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        tools.append(flare & arc_region)
    # The shared analytic normal offset follows the crown in both x and z.
    mating = clearance_loft(mountMinZ - overrun, plateTopZ + overrun, neckClearance)
    tools.append(region - mating)
    tools.append(
        Pos(0, boreFloorY, bossAxisZ)
        * Cylinder(
            boreDiameter / 2,
            envelopeMaxY + overrun - boreFloorY,
            rotation=(-90, 0, 0),
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
    combined = tools[0].fuse(*tools[1:])
    if isinstance(combined, list):
        combined = Compound(combined)
    seat = stock - combined
    assert seat.is_valid, "insert seat must remain valid"
    assert len(seat.solids()) == 1, "insert seat must stay connected"
    return seat

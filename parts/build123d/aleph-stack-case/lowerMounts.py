"""Add the four lower compression pads and closure bores to the cover only."""

from build123d import Align, Compound, Cylinder, Pos
from params import (
    basePadDiameter,
    floorThickness,
    floorTop,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    mountHoleDiameter,
    mountXHigh,
    mountXLow,
    mountYHigh,
    mountYLow,
)


def apply(body):
    """Return the original cap and a single cover solid with four annular seats."""
    assert isinstance(body, (list, tuple)) and len(body) == 2, (
        "infeasible: lowerMounts requires the ordered cap and cover bodies"
    )
    upper_cap, bottom_cover = body
    overrun = 0.03
    seat_z = 0.0
    pad_radius = basePadDiameter / 2.0
    bore_radius = mountHoleDiameter / 2.0
    # Follow the foundation's working slab plane when floorThickness is edited.
    cover_base_z = floorTop - floorThickness

    assert floorThickness > overrun, "infeasible: the cover must contain the pad overlap"
    assert floorTop < seat_z, "infeasible: the cover floor must remain below the PCB seats"
    assert 0.0 < bore_radius < pad_radius, "infeasible: bores must leave positive pad material"
    assert pad_radius - bore_radius >= 2.0, "infeasible: lower pad ligament must be at least 2 mm"
    assert mountXHigh - mountXLow > basePadDiameter, "infeasible: pads must remain separate in x"
    assert mountYHigh - mountYLow > basePadDiameter, "infeasible: pads must remain separate in y"

    mount_axes = (
        (mountXLow, mountYLow),
        (mountXHigh, mountYLow),
        (mountXHigh, mountYHigh),
        (mountXLow, mountYHigh),
    )
    for x, y in mount_axes:
        assert innerXMin + 0.1 <= x - pad_radius and x + pad_radius <= innerXMax - 0.1, (
            "infeasible: lower pads must clear the cap's inner x faces"
        )
        assert innerYMin + 0.1 <= y - pad_radius and y + pad_radius <= innerYMax - 0.1, (
            "infeasible: lower pads must clear the cap's inner y faces"
        )

    # The overlap is inside the existing slab; the exposed seats stay at z=0.
    pads = Compound(
        [
            Pos(x, y, floorTop - overrun)
            * Cylinder(
                pad_radius,
                seat_z - floorTop + overrun,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            for x, y in mount_axes
        ]
    )
    bores = Compound(
        [
            Pos(x, y, cover_base_z - overrun)
            * Cylinder(
                bore_radius,
                seat_z - cover_base_z + 2.0 * overrun,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            for x, y in mount_axes
        ]
    )
    padded_cover = bottom_cover + pads
    drilled_cover = padded_cover - bores
    return [upper_cap, drilled_cover]

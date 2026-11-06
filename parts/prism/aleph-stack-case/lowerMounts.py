"""Four lower support pads and coaxial cover bores, in millimetres.

The ordered body pair is [upper_cap, bottom_cover]. Only bottom_cover is
modified; the upper-cap object is passed through unchanged. All pad seats
end on the base-PCB datum z=0, independently of the wall and roof parameters.
"""

from build123d import Align, Compound, Cylinder, Pos
from navier_cad.blends import fuse_all
from params import (
    basePadDiameter,
    floorThickness,
    floorTop,
    mountHoleDiameter,
    mountXHigh,
    mountXLow,
    mountYHigh,
    mountYLow,
)


def apply(body):
    """Add four integral pads, then cut the four closure bores in one batch."""
    assert len(body) == 2, "lowerMounts requires [upper_cap, bottom_cover]"
    assert floorThickness > 0.0, "infeasible: floorThickness must be positive"
    assert floorTop < 0.0, "infeasible: pad deck must lie below the z=0 seat"
    assert 0.0 < mountHoleDiameter < basePadDiameter, "infeasible: lower pads need a positive bore and annular material"
    assert mountXHigh - mountXLow > basePadDiameter, "infeasible: x mount spacing must keep the lower pads distinct"
    assert mountYHigh - mountYLow > basePadDiameter, "infeasible: y mount spacing must keep the lower pads distinct"

    upper_cap, bottom_cover = body
    seat_z = 0.0
    overrun = 0.03
    cover_bottom = floorTop - floorThickness
    mount_axes = (
        (mountXLow, mountYLow),
        (mountXHigh, mountYLow),
        (mountXHigh, mountYHigh),
        (mountXLow, mountYHigh),
    )

    # Embed each pad 0.03 mm into the cover to avoid a coincident fuse face;
    # the only newly exposed material is the D8 cylinder floorTop .. z=0.
    pads = [
        Pos(x, y, floorTop - overrun)
        * Cylinder(
            basePadDiameter / 2.0,
            seat_z - floorTop + overrun,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        for x, y in mount_axes
    ]
    padded_cover = fuse_all(bottom_cover, pads, what="lowerMounts.support_pads")

    # One disconnected tool family and one subtraction, only from the cover.
    # Both ends overrun 0.03 mm into air; no cutter touches cap material.
    bore_tool = Compound(
        [
            Pos(x, y, cover_bottom - overrun)
            * Cylinder(
                mountHoleDiameter / 2.0,
                seat_z - cover_bottom + 2.0 * overrun,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            for x, y in mount_axes
        ]
    )
    finished_cover = padded_cover - bore_tool
    assert finished_cover.is_valid, "lowerMounts produced an invalid cover"
    assert len(finished_cover.solids()) == 1, "lowerMounts pads must remain integral with one bottom-cover solid"
    return [upper_cap, finished_cover]

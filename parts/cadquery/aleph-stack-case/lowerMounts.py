# Four compression pads and coaxial through-bores on the existing lower cover.
import cadquery as cq
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


def _cylinder_tool(axes, radius, bottom, top):
    tool = None
    for x, y in axes:
        cylinder = cq.Workplane("XY", origin=(x, y, bottom)).circle(radius).extrude(top - bottom)
        tool = cylinder if tool is None else tool.union(cylinder, clean=True)
    return tool


def apply(body):
    upper, lower = body
    overrun = 0.02
    padRadius = basePadDiameter / 2.0

    assert mountHoleDiameter > 0.0, "infeasible: mountHoleDiameter must be positive"
    assert basePadDiameter > 0.0, "infeasible: basePadDiameter must be positive"
    assert basePadDiameter > mountHoleDiameter, "infeasible: pads must retain material around the closure bores"
    assert floorThickness > overrun, "infeasible: floorThickness must exceed the buried pad overlap"
    assert floorTop < 0.0, "infeasible: floorTop must lie below the base PCB seat at z=0"
    assert mountXHigh - mountXLow > basePadDiameter, "infeasible: x mounting pitch must keep the pads separate"
    assert mountYHigh - mountYLow > basePadDiameter, "infeasible: y mounting pitch must keep the pads separate"
    assert innerXMin + 0.1 < mountXLow - padRadius and mountXHigh + padRadius < innerXMax - 0.1, (
        "infeasible: lower pads must clear the upper-cap x walls by more than 0.1 mm"
    )
    assert innerYMin + 0.1 < mountYLow - padRadius and mountYHigh + padRadius < innerYMax - 0.1, (
        "infeasible: lower pads must clear the upper-cap y walls by more than 0.1 mm"
    )

    axes = (
        (mountXLow, mountYLow),
        (mountXHigh, mountYLow),
        (mountXHigh, mountYHigh),
        (mountXLow, mountYHigh),
    )
    # Bury the pad roots in the slab; only their annular seats end at z=0.
    padTool = _cylinder_tool(axes, padRadius, floorTop - overrun, 0.0)
    boreTool = _cylinder_tool(axes, mountHoleDiameter / 2.0, floorTop - floorThickness - overrun, overrun)
    paddedLower = lower.union(padTool, clean=True)
    newLower = paddedLower.cut(boreTool, clean=True)
    return [upper, newLower]

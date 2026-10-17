# Coplanar roof openings; preserve the upper walls and the separate lower cover.
import cadquery as cq
from params import (
    heatsinkCenterX,
    heatsinkCenterY,
    heatsinkLength,
    heatsinkMargin,
    heatsinkWidth,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    mountHoleDiameter,
    mountXHigh,
    mountXLow,
    mountYHigh,
    mountYLow,
    roofBottom,
    roofThickness,
)


def apply(body):
    upper, lower = body
    assert heatsinkMargin > 0.0, "infeasible: heatsinkMargin must be positive"
    assert mountHoleDiameter > 0.0, "infeasible: mountHoleDiameter must be positive"
    assert heatsinkLength > 0.0, "infeasible: heatsinkLength must be positive"
    assert heatsinkWidth > 0.0, "infeasible: heatsinkWidth must be positive"
    assert roofThickness > 0.0, "infeasible: roofThickness must be positive"

    openingLength = heatsinkLength + 2.0 * heatsinkMargin
    openingWidth = heatsinkWidth + 2.0 * heatsinkMargin
    openingXMin = heatsinkCenterX - openingLength / 2.0
    openingXMax = heatsinkCenterX + openingLength / 2.0
    openingYMin = heatsinkCenterY - openingWidth / 2.0
    openingYMax = heatsinkCenterY + openingWidth / 2.0
    faceClearance = 0.1
    assert innerXMin + faceClearance < openingXMin < openingXMax < innerXMax - faceClearance, (
        "infeasible: heatsink aperture must stay clear of the x walls"
    )
    assert innerYMin + faceClearance < openingYMin < openingYMax < innerYMax - faceClearance, (
        "infeasible: heatsink aperture must stay clear of the y walls"
    )

    # Both ends overrun into air. The aperture is recomputed from the editable
    # heatsink inputs instead of using the nominal heatOpening literals.
    overrun = 0.02
    toolBottom = roofBottom - overrun
    toolHeight = roofThickness + 2.0 * overrun
    apertureTool = (
        cq.Workplane("XY", origin=(heatsinkCenterX, heatsinkCenterY, toolBottom))
        .rect(openingLength, openingWidth)
        .extrude(toolHeight)
    )
    boreRadius = mountHoleDiameter / 2.0
    mountAxes = (
        (mountXLow, mountYLow),
        (mountXHigh, mountYLow),
        (mountXHigh, mountYHigh),
        (mountXLow, mountYHigh),
    )
    boreTools = []
    for x, y in mountAxes:
        assert innerXMin + faceClearance < x - boreRadius < x + boreRadius < innerXMax - faceClearance, (
            "infeasible: top screw bores must stay clear of the x walls"
        )
        assert innerYMin + faceClearance < y - boreRadius < y + boreRadius < innerYMax - faceClearance, (
            "infeasible: top screw bores must stay clear of the y walls"
        )
        distanceX = max(openingXMin - x, 0.0, x - openingXMax)
        distanceY = max(openingYMin - y, 0.0, y - openingYMax)
        assert distanceX**2 + distanceY**2 > (boreRadius + faceClearance) ** 2, (
            "infeasible: heatsink aperture must leave separate top screw lands"
        )
        boreTool = cq.Workplane("XY", origin=(x, y, toolBottom)).circle(boreRadius).extrude(toolHeight)
        boreTools.append(boreTool)

    # Deterministic union order: aperture, front left, front right, rear right,
    # rear left. One subtraction retains a single clean upper-shell solid.
    roofTool = apertureTool
    for boreTool in boreTools:
        roofTool = roofTool.union(boreTool, clean=True)
    newUpper = upper.cut(roofTool, clean=True)
    return [newUpper, lower]

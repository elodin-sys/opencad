# Connector projections and lower heatsink exhausts; all dimensions are millimetres.
import cadquery as cq
from params import (
    baseBoardThickness,
    carrierBottom,
    floorTop,
    heatsinkBottom,
    heatsinkCenterY,
    heatsinkWidth,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    portMargin,
    roofBottom,
    seamGap,
    wallThickness,
)


def _box(xMin, xMax, yMin, yMax, zMin, zMax):
    assert xMax > xMin and yMax > yMin and zMax > zMin, "infeasible: window tool spans must be positive"
    return cq.Workplane("XY", origin=(xMin, yMin, zMin)).box(
        xMax - xMin,
        yMax - yMin,
        zMax - zMin,
        centered=(False, False, False),
    )


def apply(body):
    upper, lower = body
    overrun = 0.02
    assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
    assert portMargin > 0.0, "infeasible: portMargin must be positive"
    assert heatsinkWidth > 0.0, "infeasible: heatsinkWidth must be positive"
    assert heatsinkBottom < roofBottom, "infeasible: exhaust floor must lie below the roof underside"

    # Only wall-normal depth includes overrun. Recompute exterior planes so a
    # wallThickness edit cannot leave a membrane at the old exterior boundary.
    frontYMin = innerYMin - wallThickness - overrun
    frontYMax = innerYMin + overrun
    rearYMin = innerYMax - overrun
    rearYMax = innerYMax + wallThickness + overrun
    leftXMin = innerXMin - wallThickness - overrun
    leftXMax = innerXMin + overrun
    rightXMin = innerXMax - overrun
    rightXMax = innerXMax + wallThickness + overrun

    # Supplied connector body projections, expanded by the editable port margin.
    # The base header and USB heights above their PCB are 4.42 and 3.38 mm.
    serviceFloor = baseBoardThickness - portMargin
    headerCeiling = baseBoardThickness + 4.42 + portMargin
    sideUsbCeiling = baseBoardThickness + 3.38 + portMargin
    carrierCeiling = carrierBottom + portMargin
    j9Floor = carrierBottom - 3.11 - portMargin
    j8Floor = carrierBottom - 3.37 - portMargin
    powerCeiling = carrierBottom + 4.68 + portMargin
    rearLeft = 8.08 - portMargin
    rearRight = 73.33 + portMargin
    frontLeft = 31.73 - portMargin
    frontRight = 75.18 + portMargin
    j9Left = 42.16 - portMargin
    j9Right = 50.90 + portMargin
    j8Left = 62.31 - portMargin
    j8Right = 71.25 + portMargin
    powerLowY = 6.65 - portMargin
    powerHighY = 16.71 + portMargin
    sideUsbLowY = 36.43 - portMargin
    sideUsbHighY = 45.37 + portMargin

    # Exhaust uncertainty is a fixed 3.0 mm addition, independent of both the
    # service port margin and the roof's heatsinkMargin parameter.
    exhaustWidth = heatsinkWidth + 3.0
    exhaustLowY = heatsinkCenterY - exhaustWidth / 2.0
    exhaustHighY = heatsinkCenterY + exhaustWidth / 2.0

    assert serviceFloor > floorTop + seamGap + 0.1, "infeasible: service openings must preserve the cap sill"
    assert max(j9Floor, j8Floor) < headerCeiling < carrierCeiling, (
        "infeasible: raised front windows must overlap the lower opening"
    )
    assert frontLeft < j9Left < j9Right < j8Left < j8Right < frontRight, (
        "infeasible: front windows must retain a web between the raised portions"
    )
    assert j8Left - j9Right > 2.1, "infeasible: raised USB windows must retain a structural web"
    assert powerCeiling < heatsinkBottom - 0.1, "infeasible: power and exhaust windows must remain separate"
    assert powerHighY < sideUsbLowY - 0.1, "infeasible: right-side service windows must remain separate"
    for xMin, xMax in ((rearLeft, rearRight), (frontLeft, frontRight)):
        assert innerXMin + 0.1 < xMin < xMax < innerXMax - 0.1, (
            "infeasible: front and rear windows must preserve the side-wall corners"
        )
    for yMin, yMax in (
        (powerLowY, powerHighY),
        (sideUsbLowY, sideUsbHighY),
        (exhaustLowY, exhaustHighY),
    ):
        assert innerYMin + 0.1 < yMin < yMax < innerYMax - 0.1, (
            "infeasible: side windows must preserve the front and rear wall corners"
        )

    rearTool = _box(rearLeft, rearRight, rearYMin, rearYMax, serviceFloor, headerCeiling)
    frontLowerTool = _box(frontLeft, frontRight, frontYMin, frontYMax, serviceFloor, headerCeiling)
    j9Tool = _box(j9Left, j9Right, frontYMin, frontYMax, j9Floor, carrierCeiling)
    j8Tool = _box(j8Left, j8Right, frontYMin, frontYMax, j8Floor, carrierCeiling)
    powerTool = _box(rightXMin, rightXMax, powerLowY, powerHighY, serviceFloor, powerCeiling)
    sideUsbTool = _box(rightXMin, rightXMax, sideUsbLowY, sideUsbHighY, serviceFloor, sideUsbCeiling)
    # Stop exactly at the shared roof underside: a vertical overrun here would
    # remove roof material outside this group's wall projection masks.
    leftExhaustTool = _box(leftXMin, leftXMax, exhaustLowY, exhaustHighY, heatsinkBottom, roofBottom)
    rightExhaustTool = _box(rightXMin, rightXMax, exhaustLowY, exhaustHighY, heatsinkBottom, roofBottom)

    frontTool = frontLowerTool.union(j9Tool, clean=True).union(j8Tool, clean=True)
    windowTool = rearTool
    for tool in (frontTool, powerTool, sideUsbTool, leftExhaustTool, rightExhaustTool):
        windowTool = windowTool.union(tool, clean=True)
    newUpper = upper.cut(windowTool, clean=True)
    return [newUpper, lower]

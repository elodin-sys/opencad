# Eight subtractive screw stacks; printable support openings precede the pilots.
import cadquery as cq
from params import (
    bridgeLayerHeight,
    counterboreDiameter,
    halfWidth,
    leftNutX,
    leftNutZ,
    leftPivotX,
    longCounterboreEnd,
    longCounterboreFullDepth,
    longPilotLength,
    longPilotStart,
    lowerLeftPilotDiameter,
    lowerLeftScrewX,
    lowerLeftScrewZ,
    lowerNutX,
    lowerNutZ,
    lugNutX,
    lugNutZ,
    nutAcrossFlats,
    nutCornerRadius,
    nutFullDepth,
    nutLeftFlatX,
    nutPilotStart,
    nutRectEnd,
    nutRightFlatX,
    pivotCounterboreStart,
    pivotMouthDiameter,
    pivotPilotEnd,
    plateThickness,
    rightCounterboreEnd,
    rightCounterboreFullDepth,
    rightPilotStart,
    rightPivotX,
    screwDiameter,
    upperLeftPilotDiameter,
    upperLeftScrewX,
    upperLeftScrewZ,
    upperRightScrewX,
    upperRightScrewZ,
)

_OVERRUN = 0.03
# The two D3.5 pilots are editable independently of these square bridges.
_LEFT_BRIDGE_WIDTH = 3.5


def _circle(x, z, radius, start_y, end_y):
    return cq.Workplane("XZ", origin=(x, start_y, z)).circle(radius).extrude(start_y - end_y)


def _prism(points, start_y, end_y):
    return cq.Workplane("XZ", origin=(0.0, start_y, 0.0)).polyline(points).close().extrude(start_y - end_y)


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY", origin=(x0, y0, z0)).box(x1 - x0, y1 - y0, z1 - z0, centered=False)


def _square(x, z, width, start_y, end_y):
    half = width / 2.0
    return _box(x - half, x + half, start_y, end_y, z - half, z + half)


def _counterbore_tools(x, z, full_depth, band_end, pilot_start, pilot_diameter, bridge_width, front):
    radius = counterboreDiameter / 2.0
    half = bridge_width / 2.0
    # The circular wall continues only beside the first support layer. A full
    # circular cut to band_end would remove the two horizontal ledges.
    band = _circle(x, z, radius, full_depth - _OVERRUN, band_end).intersect(
        _box(
            x - radius - _OVERRUN,
            x + radius + _OVERRUN,
            full_depth - 2.0 * _OVERRUN,
            band_end + _OVERRUN,
            z - half,
            z + half,
        ),
        clean=True,
    )
    return [
        _circle(x, z, radius, -_OVERRUN, full_depth),
        band,
        _square(x, z, bridge_width, full_depth - _OVERRUN, pilot_start),
        # No backward pilot overrun: a larger edited pilot must not remove any
        # material from the square support immediately before pilot_start.
        _circle(x, z, pilot_diameter / 2.0, pilot_start, front),
    ]


def _nut_tools(x, z, left, right, front):
    radius = nutCornerRadius
    points = [
        (x, z - radius),
        (right, z - radius / 2.0),
        (right, z + radius / 2.0),
        (x, z + radius),
        (left, z + radius / 2.0),
        (left, z - radius / 2.0),
    ]
    half = screwDiameter / 2.0
    # Preserve the sloped hex walls beside the first support opening: it is
    # the hex intersected by a horizontal band, not an oversized rectangle.
    band = _prism(points, nutFullDepth - _OVERRUN, nutRectEnd).intersect(
        _box(
            left - _OVERRUN,
            right + _OVERRUN,
            nutFullDepth - 2.0 * _OVERRUN,
            nutRectEnd + _OVERRUN,
            z - half,
            z + half,
        ),
        clean=True,
    )
    return [
        _prism(points, -_OVERRUN, nutFullDepth),
        band,
        _square(x, z, screwDiameter, nutFullDepth - _OVERRUN, nutPilotStart),
        _circle(x, z, half, nutPilotStart, front),
    ]


def _pivot_tools(x, front):
    pilot_radius = screwDiameter / 2.0
    mouth_radius = pivotMouthDiameter / 2.0
    slope = (mouth_radius - pilot_radius) / (pivotCounterboreStart - pivotPilotEnd)
    # Both loft ends overlap adjacent voids, with the design radii retained
    # exactly at y=pivotPilotEnd and y=pivotCounterboreStart.
    start = pivotPilotEnd - _OVERRUN
    end = pivotCounterboreStart + _OVERRUN
    mouth = (
        cq.Workplane("XZ", origin=(x, start, 0.0))
        .circle(pilot_radius - slope * _OVERRUN)
        .workplane(offset=start - end)
        .circle(mouth_radius + slope * _OVERRUN)
        .loft(ruled=True)
    )
    return [
        _circle(x, 0.0, pilot_radius, -_OVERRUN, pivotPilotEnd + _OVERRUN),
        mouth,
        _circle(x, 0.0, counterboreDiameter / 2.0, pivotCounterboreStart, front),
    ]


def apply(body):
    assert plateThickness > 0.0 and halfWidth > 0.0, "infeasible: plate dimensions must be positive"
    assert 0.0 < screwDiameter < pivotMouthDiameter < counterboreDiameter, (
        "infeasible: pivot pilot, mouth and counterbore diameters must increase"
    )
    assert 0.0 < upperLeftPilotDiameter < counterboreDiameter, "infeasible: upperLeftPilotDiameter out of range"
    assert 0.0 < lowerLeftPilotDiameter < counterboreDiameter, "infeasible: lowerLeftPilotDiameter out of range"
    assert _LEFT_BRIDGE_WIDTH < counterboreDiameter, "infeasible: counterbore must contain its support square"
    assert 0.0 < pivotPilotEnd < pivotCounterboreStart < plateThickness, "infeasible: pivot depths must be ordered"
    assert 0.0 < nutFullDepth < nutRectEnd < nutPilotStart < plateThickness, "infeasible: nut depths must be ordered"
    assert 0.0 < longCounterboreFullDepth < longCounterboreEnd < longPilotStart < plateThickness, (
        "infeasible: left screw depths must be ordered"
    )
    assert 0.0 < rightCounterboreFullDepth < rightCounterboreEnd < rightPilotStart < plateThickness, (
        "infeasible: right screw depths must be ordered"
    )
    assert 0.0 < bridgeLayerHeight < min(nutFullDepth, longCounterboreFullDepth, rightCounterboreFullDepth), (
        "infeasible: bridge layer must fit inside each recess"
    )
    assert 0.0 < longPilotLength < plateThickness, "infeasible: longPilotLength must fit inside the plate"
    assert 0.0 < screwDiameter < nutAcrossFlats and screwDiameter < 2.0 * nutCornerRadius, (
        "infeasible: nut trap must contain the screw opening"
    )
    assert nutLeftFlatX < leftNutX - screwDiameter / 2.0, "infeasible: left nut flat crosses its pilot"
    assert leftNutX + screwDiameter / 2.0 < nutRightFlatX, "infeasible: right nut flat crosses its pilot"
    assert -halfWidth < leftPivotX < rightPivotX < halfWidth, "infeasible: pivot axes must be inside the plate"

    front = plateThickness + _OVERRUN
    tools = []
    for x, z, diameter in (
        (upperLeftScrewX, upperLeftScrewZ, upperLeftPilotDiameter),
        (lowerLeftScrewX, lowerLeftScrewZ, lowerLeftPilotDiameter),
    ):
        tools.extend(
            _counterbore_tools(
                x,
                z,
                longCounterboreFullDepth,
                longCounterboreEnd,
                longPilotStart,
                diameter,
                _LEFT_BRIDGE_WIDTH,
                max(front, longPilotStart + longPilotLength + _OVERRUN),
            )
        )
    tools.extend(
        _counterbore_tools(
            upperRightScrewX,
            upperRightScrewZ,
            rightCounterboreFullDepth,
            rightCounterboreEnd,
            rightPilotStart,
            screwDiameter,
            screwDiameter,
            front,
        )
    )
    tools.extend(_nut_tools(leftNutX, leftNutZ, nutLeftFlatX, nutRightFlatX, front))
    for x, z in ((lugNutX, lugNutZ), (lowerNutX, lowerNutZ)):
        tools.extend(_nut_tools(x, z, x - nutAcrossFlats / 2.0, x + nutAcrossFlats / 2.0, front))
    for x in (leftPivotX, rightPivotX):
        tools.extend(_pivot_tools(x, front))

    # The left counterbore opens fully to the shared x=-halfWidth boundary.
    # All other tools keep their natural section, including the upper-right
    # D6.5 recess reaching x=23.25; sideClamp owns any subsequent trim.
    radius = counterboreDiameter / 2.0
    tools.append(_box(-halfWidth - _OVERRUN, leftPivotX, pivotCounterboreStart, front, -radius, radius))
    cutter = tools[0]
    for tool in tools[1:]:
        cutter = cutter.union(tool, clean=True)
    return body.cut(cutter, clean=True)

"""Eight screw stacks, including the two-layer printable support transitions."""

from build123d import Circle, Cone, Plane, Polygon, Pos, Rectangle, extrude
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

overrun = 0.03
# The drawing's preceding square is independent of either editable pilot.
long_bridge_width = 3.5


def _prism(profile, x, z, start, end):
    """Extrude an x/z profile in +y, retaining its specified internal stops."""
    assert end > start, "infeasible: fastener extrusion stations must be ordered"
    return Pos(x, start, z) * extrude(Plane.XZ * profile, amount=end - start, dir=(0.0, 1.0, 0.0))


def _supported_stack(profile, x, z, full_end, strip_end, pilot_start, bridge_width, pilot_diameter):
    """Full pocket, clipped strip, square, then the terminal round pilot."""
    assert 0.0 < full_end < strip_end < pilot_start < plateThickness, "infeasible: support depth order"
    assert 0.0 < pilot_diameter < counterboreDiameter, "infeasible: pilot diameter must fit the recess"
    assert 0.0 < bridge_width < counterboreDiameter, "infeasible: bridge width must fit the recess"
    # Intersections retain the circular arcs or short hex slopes through the
    # first bridge layer. A rectangular bore would erase those surfaces.
    strip = profile & Rectangle(2.0 * counterboreDiameter, bridge_width)
    square = Rectangle(bridge_width, bridge_width)
    return [
        _prism(profile, x, z, -overrun, full_end),
        _prism(strip, x, z, full_end - overrun, strip_end),
        _prism(square, x, z, strip_end - overrun, pilot_start),
        # Do not overrun backwards into the square: diameter edits are
        # confined to y=longPilotStart..plateThickness.
        _prism(Circle(pilot_diameter / 2.0), x, z, pilot_start, plateThickness + overrun),
    ]


def _hex(left, right):
    return Polygon(
        (0.0, nutCornerRadius),
        (right, nutCornerRadius / 2.0),
        (right, -nutCornerRadius / 2.0),
        (0.0, -nutCornerRadius),
        (left, -nutCornerRadius / 2.0),
        (left, nutCornerRadius / 2.0),
        align=None,
    )


def apply(body):
    """Union all eight cutter stacks before making a single stock subtraction."""
    assert upperLeftPilotDiameter > 0.0, "infeasible: upperLeftPilotDiameter must be positive"
    assert lowerLeftPilotDiameter > 0.0, "infeasible: lowerLeftPilotDiameter must be positive"
    assert 0.0 < screwDiameter < pivotMouthDiameter < counterboreDiameter, "infeasible: pivot diameters"
    assert 0.0 < pivotPilotEnd < pivotCounterboreStart < plateThickness, "infeasible: pivot stations"
    assert 0.0 < nutAcrossFlats < counterboreDiameter, "infeasible: nut flats must fit the stack envelope"
    assert nutCornerRadius > screwDiameter / 2.0, "infeasible: nut corners must clear the pilot"
    assert nutLeftFlatX < leftNutX < nutRightFlatX, "infeasible: nut flats must straddle their screw axis"
    assert nutRightFlatX - nutLeftFlatX > screwDiameter, "infeasible: the nut trap must clear the screw"
    assert overrun < bridgeLayerHeight < plateThickness, "infeasible: printable layer thickness"
    assert overrun < longPilotLength < plateThickness, "infeasible: straight pilot length"
    assert -halfWidth < leftPivotX < rightPivotX < halfWidth, "infeasible: pivot axes must lie in the plate"

    tools = []
    for x, z, diameter in (
        (upperLeftScrewX, upperLeftScrewZ, upperLeftPilotDiameter),
        (lowerLeftScrewX, lowerLeftScrewZ, lowerLeftPilotDiameter),
    ):
        tools.extend(
            _supported_stack(
                Circle(counterboreDiameter / 2.0),
                x,
                z,
                longCounterboreFullDepth,
                longCounterboreEnd,
                longPilotStart,
                long_bridge_width,
                diameter,
            )
        )

    tools.extend(
        _supported_stack(
            Circle(counterboreDiameter / 2.0),
            upperRightScrewX,
            upperRightScrewZ,
            rightCounterboreFullDepth,
            rightCounterboreEnd,
            rightPilotStart,
            screwDiameter,
            screwDiameter,
        )
    )

    for x, z, left, right in (
        (leftNutX, leftNutZ, nutLeftFlatX - leftNutX, nutRightFlatX - leftNutX),
        (lugNutX, lugNutZ, -nutAcrossFlats / 2.0, nutAcrossFlats / 2.0),
        (lowerNutX, lowerNutZ, -nutAcrossFlats / 2.0, nutAcrossFlats / 2.0),
    ):
        tools.extend(
            _supported_stack(
                _hex(left, right), x, z, nutFullDepth, nutRectEnd, nutPilotStart, screwDiameter, screwDiameter
            )
        )

    for x in (leftPivotX, rightPivotX):
        tools.append(_prism(Circle(screwDiameter / 2.0), x, 0.0, -overrun, pivotPilotEnd + overrun))
        transition_length = pivotCounterboreStart - pivotPilotEnd
        slope = (pivotMouthDiameter - screwDiameter) / (2.0 * transition_length)
        # The cone overruns only into the larger counterbore. Its radius at
        # the actual shoulder remains the raster-measured mouth radius.
        cone_length = transition_length + overrun
        tools.append(
            Pos(x, pivotPilotEnd + cone_length / 2.0, 0.0)
            * Cone(
                screwDiameter / 2.0,
                pivotMouthDiameter / 2.0 + slope * overrun,
                cone_length,
                rotation=(-90.0, 0.0, 0.0),
            )
        )
        tools.append(_prism(Circle(counterboreDiameter / 2.0), x, 0.0, pivotCounterboreStart, plateThickness + overrun))

    # Only the left pivot is open to the locating face. The slot meets the
    # counterbore at its axis, retaining the exact z=+/-3.25 tangencies.
    slot_left = -halfWidth - overrun
    tools.append(
        _prism(
            Rectangle(leftPivotX - slot_left, counterboreDiameter),
            (leftPivotX + slot_left) / 2.0,
            0.0,
            pivotCounterboreStart,
            plateThickness + overrun,
        )
    )

    cutter = tools[0].fuse(*tools[1:])
    shaped = body - cutter
    assert len(shaped.solids()) == 1, "infeasible: fastener cuts must leave one connected solid"
    assert shaped.is_valid, "infeasible: fastener boolean produced an invalid solid"
    return shaped

"""Parametric mounting plate in millimetres, with its blank minimum at the origin."""

from build123d import Align, Axis, Compound, Cylinder, Pos, Rectangle, extrude, fillet

plateWidth = 80.0
plateHeight = 50.0
plateThickness = 6.0
holeDiameter = 4.5
holeInset = 10.0
cornerRadius = 5.0

assert plateWidth > 0, "plateWidth must be positive"
assert plateHeight > 0, "plateHeight must be positive"
assert plateThickness > 0, "plateThickness must be positive"
assert 0 < cornerRadius < min(plateWidth, plateHeight) / 2, "cornerRadius must fit"
assert holeDiameter > 0, "holeDiameter must be positive"
assert holeInset > cornerRadius + holeDiameter / 2, "holes must clear rounded corners"
assert 2 * holeInset + holeDiameter < min(plateWidth, plateHeight), "holes must be separated"

outline = Rectangle(plateWidth, plateHeight, align=(Align.MIN, Align.MIN))
plate = extrude(outline, amount=plateThickness)
vertical_edges = plate.edges().filter_by(Axis.Z)
assert len(vertical_edges) == 4, "blank must have four vertical corner edges"
rounded_plate = fillet(vertical_edges, radius=cornerRadius)

hole_centres = (
    (holeInset, holeInset),
    (plateWidth - holeInset, holeInset),
    (plateWidth - holeInset, plateHeight - holeInset),
    (holeInset, plateHeight - holeInset),
)
cutter_overrun = 0.02
hole_tools = Compound(
    [
        Pos(x, y, -cutter_overrun)
        * Cylinder(
            holeDiameter / 2,
            plateThickness + 2 * cutter_overrun,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        for x, y in hole_centres
    ]
)
result = rounded_plate - hole_tools
assert result.is_valid, "finished plate must be a valid shape"
assert len(result.solids()) == 1, "finished plate must remain one solid"

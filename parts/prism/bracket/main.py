"""Parametric mounting plate, in millimetres, in the contract's datum frame."""

from build123d import Align, Axis, Compound, Cylinder, Pos, Rectangle, extrude, fillet

plateWidth = 80.0
plateHeight = 50.0
plateThickness = 6.0
holeDiameter = 4.5
holeInset = 10.0
cornerRadius = 5.0

assert plateWidth > 0.0, "infeasible: plateWidth must be positive"
assert plateHeight > 0.0, "infeasible: plateHeight must be positive"
assert plateThickness > 0.0, "infeasible: plateThickness must be positive"
assert 0.0 < cornerRadius < min(plateWidth, plateHeight) / 2.0, (
    "infeasible: cornerRadius must be positive and less than half the smaller side"
)
assert holeDiameter > 0.0, "infeasible: holeDiameter must be positive"
hole_radius = holeDiameter / 2.0
assert holeInset > hole_radius, "infeasible: holes must clear all straight plate edges"
assert 2.0 * holeInset + holeDiameter < min(plateWidth, plateHeight), (
    "infeasible: the four mounting holes must not touch or overlap"
)
if holeInset < cornerRadius:
    assert 2.0**0.5 * (cornerRadius - holeInset) + hole_radius < cornerRadius, (
        "infeasible: mounting holes must clear the rounded corners"
    )

# Datum A is the XY sketch plane; B and C are its minimum x/y boundaries.
plate_profile = Rectangle(plateWidth, plateHeight, align=(Align.MIN, Align.MIN))
plate = extrude(plate_profile, amount=plateThickness)

# Only the four vertical corner edges are rounded; top and bottom stay planar.
vertical_edges = plate.edges().filter_by(Axis.Z)
assert len(vertical_edges) == 4, "expected four vertical blank corner edges"
rounded_plate = fillet(vertical_edges, radius=cornerRadius)

# Use global XY coordinates, keeping the 60 x 30 mm interface centred.
hole_centres = [
    (holeInset, holeInset),
    (plateWidth - holeInset, holeInset),
    (plateWidth - holeInset, plateHeight - holeInset),
    (holeInset, plateHeight - holeInset),
]
cut_overrun = 0.02
hole_tools = Compound(
    [
        Pos(x, y, -cut_overrun)
        * Cylinder(
            hole_radius,
            plateThickness + 2.0 * cut_overrun,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        for x, y in hole_centres
    ]
)
result = rounded_plate - hole_tools
assert result.is_valid, "invalid finished mounting plate"
assert len(result.solids()) == 1, "finished mounting plate must be one solid"

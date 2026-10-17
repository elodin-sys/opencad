from build123d import Circle, Compound, Cylinder, Pos, extrude, make_hull

linkLength = 100.0
endRadius = 8.0
plateThickness = 5.0
holeDiameter = 6.0

assert linkLength > 0, "infeasible: linkLength must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"
assert endRadius > holeDiameter / 2, "infeasible: endRadius must exceed the hole radius"

stadium = make_hull(
    [
        (Pos(0, 0) * Circle(endRadius)).edges(),
        (Pos(linkLength, 0) * Circle(endRadius)).edges(),
    ]
)
plate = extrude(stadium, amount=plateThickness)
cutter_overrun = 0.02
hole_tool = Compound(
    [
        Pos(0, 0, plateThickness / 2) * Cylinder(holeDiameter / 2, plateThickness + 2 * cutter_overrun),
        Pos(linkLength, 0, plateThickness / 2) * Cylinder(holeDiameter / 2, plateThickness + 2 * cutter_overrun),
    ]
)
result = plate - hole_tool

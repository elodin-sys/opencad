from build123d import Circle, Compound, Cylinder, Pos, extrude, make_hull

linkLength = 40.0
linkWidth = 16.0
endRadius = linkWidth / 2
plateThickness = 5.0
holeDiameter = 6.0

assert linkLength > 0, "infeasible: linkLength must be positive"
assert linkWidth > 0, "infeasible: linkWidth must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"
assert holeDiameter < linkWidth, "infeasible: bore does not fit inside the rounded end"

stadium = make_hull(
    [
        (Pos(0, 0) * Circle(endRadius)).edges(),
        (Pos(linkLength, 0) * Circle(endRadius)).edges(),
    ]
)
plate = extrude(stadium, plateThickness)
bore_height = plateThickness + 0.1
bores = Compound(
    [
        Pos(0, 0, plateThickness / 2) * Cylinder(holeDiameter / 2, bore_height),
        Pos(linkLength, 0, plateThickness / 2) * Cylinder(holeDiameter / 2, bore_height),
    ]
)
result = plate - bores

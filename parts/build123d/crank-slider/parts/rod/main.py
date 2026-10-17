from build123d import Align, Circle, Compound, Cylinder, Pos, extrude, make_hull

centreDistance = 100.0
plateWidth = 16.0
plateThickness = 5.0
holeDiameter = 6.0
endRadius = plateWidth / 2

assert centreDistance > 0, "infeasible: centreDistance must be positive"
assert plateWidth > holeDiameter, "infeasible: plateWidth must exceed the pin bore"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"

stadium = make_hull(
    [
        (Pos(0, 0) * Circle(endRadius)).edges(),
        (Pos(centreDistance, 0) * Circle(endRadius)).edges(),
    ]
)
plate = extrude(stadium, amount=plateThickness)

bore_overrun = 0.02
bore_height = plateThickness + 2 * bore_overrun
bores = Compound(
    [
        Pos(0, 0, -bore_overrun)
        * Cylinder(
            holeDiameter / 2,
            bore_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ),
        Pos(centreDistance, 0, -bore_overrun)
        * Cylinder(
            holeDiameter / 2,
            bore_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ),
    ]
)
result = plate - bores

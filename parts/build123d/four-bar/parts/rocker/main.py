from build123d import Align, Circle, Compound, Cylinder, Pos, extrude, make_hull

linkLength = 80.0
endRadius = 8.0
linkWidth = 2 * endRadius
linkThickness = 5.0
holeDiameter = 6.0

assert linkLength > 0, "infeasible: linkLength must be positive"
assert endRadius > 0, "infeasible: endRadius must be positive"
assert linkWidth > holeDiameter, "infeasible: link width must clear the pin bore"
assert linkThickness > 0, "infeasible: linkThickness must be positive"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"
assert endRadius > holeDiameter / 2, "infeasible: end radius must clear the pin bore"

stadium = extrude(
    make_hull(
        [
            (Pos(0, 0, 0) * Circle(endRadius)).edges(),
            (Pos(linkLength, 0, 0) * Circle(endRadius)).edges(),
        ]
    ),
    amount=linkThickness,
)
bore_overrun = 0.05
bore_tool = Cylinder(
    holeDiameter / 2,
    linkThickness + 2 * bore_overrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
bores = Compound(
    children=[
        Pos(0, 0, -bore_overrun) * bore_tool,
        Pos(linkLength, 0, -bore_overrun) * bore_tool,
    ]
)
result = stadium - bores

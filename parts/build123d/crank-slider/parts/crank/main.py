from build123d import Align, CenterArc, Compound, Cylinder, Polyline, Pos, extrude, make_face

crankLength = 30.0
plateThickness = 5.0
endRadius = 8.0
plateWidth = 2 * endRadius
holeDiameter = 6.0

assert crankLength > 0, "infeasible: crankLength must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert endRadius > 0, "infeasible: endRadius must be positive"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"
assert endRadius > holeDiameter / 2, "infeasible: endRadius must exceed holeDiameter / 2"

half_width = plateWidth / 2
left_cap = CenterArc((0, 0), endRadius, 90, 180)
bottom_flank = Polyline((0, -half_width), (crankLength, -half_width))
right_cap = CenterArc((crankLength, 0), endRadius, 270, 180)
top_flank = Polyline((crankLength, half_width), (0, half_width))
plate = extrude(make_face([left_cap, bottom_flank, right_cap, top_flank]), plateThickness)
cutter_overrun = 0.05
bore = Cylinder(
    holeDiameter / 2,
    plateThickness + 2 * cutter_overrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
bores = Compound(
    [
        Pos(0, 0, -cutter_overrun) * bore,
        Pos(crankLength, 0, -cutter_overrun) * bore,
    ]
)
result = plate - bores

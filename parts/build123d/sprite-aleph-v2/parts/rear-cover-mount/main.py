from build123d import Axis, CenterArc, Circle, Line, Plane, extrude, fillet, make_face

tabWidth = 7.0
tabLength = 19.5
tabThickness = 4.0
seatY = 35.5
boreDiameter = 3.2
boreZ = 36.5
edgeFillet = 1.0

assert tabWidth > 0.0, "infeasible: tabWidth must be positive"
assert tabLength >= tabWidth, "infeasible: tabLength shorter than the two full-round ends"
assert tabThickness > edgeFillet, "infeasible: tabThickness leaves no room for the under-face fillet"
assert 0.0 < boreDiameter < tabWidth, "infeasible: bore does not fit inside the tab"
assert edgeFillet > 0.0, "infeasible: edgeFillet must be positive"

straight = tabLength - tabWidth
center_z = boreZ - straight / 2.0
end_radius = tabWidth / 2.0
top_y = straight / 2.0
bot_y = -straight / 2.0

sketch_plane = Plane(
    origin=(0.0, seatY, center_z),
    x_dir=(1.0, 0.0, 0.0),
    z_dir=(0.0, -1.0, 0.0),
)
if straight > 0.0:
    arc_top = CenterArc((0.0, top_y), end_radius, 0.0, 180.0)
    arc_bot = CenterArc((0.0, bot_y), end_radius, 180.0, 180.0)
    profile = sketch_plane * make_face(
        [
            arc_top,
            Line(arc_top @ 1, arc_bot @ 0),
            arc_bot,
            Line(arc_bot @ 1, arc_top @ 0),
        ]
    )
else:
    profile = sketch_plane * Circle(end_radius)

body = extrude(profile, amount=tabThickness)
body = fillet(body.edges().group_by(Axis.Y)[0], edgeFillet)

overrun = 0.02
bore_plane = Plane(
    origin=(0.0, seatY + overrun, boreZ),
    x_dir=(1.0, 0.0, 0.0),
    z_dir=(0.0, -1.0, 0.0),
)
bore = extrude(bore_plane * Circle(boreDiameter / 2.0), amount=tabThickness + 2.0 * overrun)
result = body - bore

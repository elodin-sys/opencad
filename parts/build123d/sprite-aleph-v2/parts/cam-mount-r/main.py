from build123d import Axis, Cylinder, GeomType, Pos, fillet

glueFaceX = -10.0
discDiameter = 12.0
discThickness = 2.0
pinDiameter = 4.0
pinLength = 4.0
pinAxisY = 15.0039
pinAxisZ = 224.2474
discBackFillet = 1.0
pinTipFillet = 0.5

assert discThickness > discBackFillet, "infeasible: discThickness must exceed discBackFillet"
assert pinLength > pinTipFillet, "infeasible: pinLength must exceed pinTipFillet"
assert discDiameter > pinDiameter, "infeasible: discDiameter must exceed pinDiameter"

pin_overlap = 0.05
disc = Pos(
    glueFaceX - discThickness / 2.0,
    pinAxisY,
    pinAxisZ,
) * Cylinder(discDiameter / 2.0, discThickness, rotation=(0, 90, 0))
pin = Pos(
    glueFaceX - discThickness - pinLength / 2.0 + pin_overlap / 2.0,
    pinAxisY,
    pinAxisZ,
) * Cylinder(pinDiameter / 2.0, pinLength + pin_overlap, rotation=(0, 90, 0))
body = disc + pin
back_x = glueFaceX - discThickness
stations = body.edges().filter_by(GeomType.CIRCLE).group_by(Axis.X)
assert len(stations) == 3, "expected tip, disc-back, and glue-face circles"
back = stations[1]
assert abs(back[0].center().X - back_x) < 1e-3, "disc-back circles are not the middle station"
longest = max(edge.length for edge in back)
outer = [edge for edge in back if edge.length > longest * 0.75]
assert outer, "disc back rim edge missing"
body = fillet(outer, discBackFillet)
tip = body.edges().filter_by(GeomType.CIRCLE).group_by(Axis.X)[0]
body = fillet(tip, pinTipFillet)
result = body

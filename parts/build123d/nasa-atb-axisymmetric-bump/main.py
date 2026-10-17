import math

from build123d import Align, Axis, Cylinder, Line, Pos, ThreePointArc, make_face, revolve

cylinderDiameter = 152.4
bumpChord = 203.2
bumpHeight = 19.05
filletRadius = 183.0
upstreamX = -650.0073203536
downstreamX = 900.0029136304

assert cylinderDiameter > 0, "infeasible: cylinderDiameter must be positive"
assert bumpChord > 0, "infeasible: bumpChord must be positive"
assert bumpHeight > 0, "infeasible: bumpHeight must be positive"
assert filletRadius > 0, "infeasible: filletRadius must be positive"
assert bumpHeight * 2.0 < bumpChord, "infeasible: use the shallow upper circular-arc branch"
assert upstreamX < 0.0, "infeasible: keep a positive upstream cylinder span before the origin"
assert downstreamX > bumpChord, "infeasible: keep a positive downstream cylinder span"

r = cylinderDiameter / 2.0
c = bumpChord
t = bumpHeight
f = filletRadius
h = c / 2.0
R = (t**2 + h**2) / (2.0 * t)
assert R > t, "infeasible: main-circle center must lie below the cylinder"
b = r + t - R
blend_radicand = 2.0 * (R + f) * t - t**2
assert blend_radicand > 0.0, "infeasible: blend tangency must have a real solution"
d = math.sqrt(blend_radicand)
a = h - d
j = a + f * d / (R + f)
q = r + f * t / (R + f)
assert upstreamX < a, "infeasible: keep a positive upstream cylinder span"
assert a < 0.0, "infeasible: leading blend must begin upstream of the origin"
assert j > 0.0, "infeasible: tangency must lie downstream of the nominal leading edge"
assert j < h, "infeasible: tangency must precede the bump crown"
assert j - a > 0.0, "infeasible: leading arc must have positive axial span"
assert j - a < f, "infeasible: leading arc must stay on its short lower branch"

x_blend_mid = (a + j) / 2.0
rho_blend_mid = r + f - math.sqrt(f**2 - (x_blend_mid - a) ** 2)
x_arc_mid = (j + c) / 2.0
rho_arc_mid = b + math.sqrt(R**2 - (x_arc_mid - h) ** 2)

core = Pos(upstreamX, 0.0, 0.0) * Cylinder(
    r,
    downstreamX - upstreamX,
    rotation=(0.0, 90.0, 0.0),
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
inset = 0.05
collar = (
    Line((a, r - inset), (a, r))
    + ThreePointArc((a, r), (x_blend_mid, rho_blend_mid), (j, q))
    + ThreePointArc((j, q), (x_arc_mid, rho_arc_mid), (c, r))
    + Line((c, r), (c, r - inset))
    + Line((c, r - inset), (a, r - inset))
)
result = core + revolve(make_face(collar.edges()), Axis.X)

named = 0
for face in result.faces().filter_by(Axis.X):
    centre = face.center()
    if abs(centre.X - upstreamX) < 0.05:
        face.label = "upstreamCap"
        named += 1
    elif abs(centre.X - downstreamX) < 0.05:
        face.label = "downstreamCap"
        named += 1
assert named >= 2, "expected named upstreamCap and downstreamCap"

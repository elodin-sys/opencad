"""Uncompressed silicone tube in the pump's fixed datum frame (millimetres)."""

from build123d import Axis, Circle, Plane, Pos, extrude, mirror, revolve

tubeOuterDiameter = 3.0
tubeInnerDiameter = 1.0
trackRadius = 12.17
centrelineRadius = trackRadius - tubeOuterDiameter / 2
bendAngle = 180.0
legLength = 30.0

assert 0 < tubeInnerDiameter < tubeOuterDiameter, "infeasible: require 0 < ID < OD"
assert legLength > 0, "infeasible: legLength must be positive"
assert centrelineRadius > tubeOuterDiameter / 2, "infeasible: bend must not self-intersect"
assert abs(bendAngle - 180.0) < 1e-9, "infeasible: parallel legs require a semicircular bend"


# One shared annulus supplies the constant wall and the open continuous bore.
annulus = Circle(tubeOuterDiameter / 2) - Circle(tubeInnerDiameter / 2)

# The bend starts at -Y and revolves through +X to +Y about datum B.
bendProfile = Pos(0, -centrelineRadius, 0) * (Plane.YZ * annulus)
bend = revolve(bendProfile, axis=Axis.Z, revolution_arc=bendAngle)
inletProfile = Pos(0, centrelineRadius, 0) * (Plane.YZ * annulus)
inletLeg = extrude(inletProfile, amount=legLength, dir=(-1, 0, 0))
outletLeg = mirror(inletLeg, about=Plane.XZ)

# Fuse matching annular tangent faces at x = 0. The full revolution avoids
# an artificial seam at the apex; circle profiles preserve the mid-plane datum.
result = bend + inletLeg + outletLeg
result.label = "tube"
assert len(result.solids()) == 1, "infeasible: the tube must be one continuous solid"
assert result.is_valid, "infeasible: the tube must have valid boundary geometry"

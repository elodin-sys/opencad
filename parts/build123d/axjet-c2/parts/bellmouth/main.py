import math

from build123d import (
    Align,
    Axis,
    CenterArc,
    Compound,
    Cylinder,
    EllipticalCenterArc,
    Plane,
    Polyline,
    Pos,
    make_face,
    mirror,
    revolve,
)

ellipseCenterZ = -45.0
ellipseCenterR = 125.0
ellipseAxialSemiAxis = 50.0
ellipseRadialSemiAxis = 34.75
lipRadius = 6.0
rearFaceZ = -72.0
flangeThickness = 5.0
flangeOuterDiameter = 224.0
boltCircleDiameter = 216.0
boltHoleDiameter = 4.2
boltHoleDepth = 10.0
boltCount = 8.0
boltStartAngle = 0.0

lipVertexZ = ellipseCenterZ - ellipseAxialSemiAxis
lipFrontZ = ellipseCenterZ - ellipseAxialSemiAxis
skinStartZ = lipVertexZ + lipRadius
skinStartRadius = ellipseCenterR + lipRadius
flangeFrontZ = rearFaceZ - flangeThickness

assert ellipseAxialSemiAxis > 0.0, "infeasible: ellipseAxialSemiAxis must be positive"
assert ellipseRadialSemiAxis > 0.0, "infeasible: ellipseRadialSemiAxis must be positive"
assert lipRadius > 0.0, "infeasible: lipRadius must be positive"
assert flangeThickness > 0.0, "infeasible: flangeThickness must be positive"
assert flangeOuterDiameter > 0.0, "infeasible: flangeOuterDiameter must be positive"
assert boltHoleDiameter > 0.0, "infeasible: boltHoleDiameter must be positive"
assert boltHoleDepth > 0.0, "infeasible: boltHoleDepth must be positive"
assert boltCircleDiameter > 0.0, "infeasible: boltCircleDiameter must be positive"
assert boltCount >= 1.0, "infeasible: boltCount must be at least 1"
assert abs(boltCount - round(boltCount)) < 1e-6, "infeasible: boltCount must be a whole number"

rear_axial_ratio = (rearFaceZ - ellipseCenterZ) / ellipseAxialSemiAxis
assert abs(rear_axial_ratio) < 1.0, "infeasible: rear face is outside the inner-contour ellipse"
rearInnerRadius = ellipseCenterR - ellipseRadialSemiAxis * math.sqrt(1.0 - rear_axial_ratio * rear_axial_ratio)
assert rearInnerRadius > 0.0, "infeasible: inner contour crosses the axis"
assert skinStartZ < flangeFrontZ, "infeasible: lip runs into the flange"
assert skinStartRadius > flangeOuterDiameter / 2.0, "infeasible: outer skin is inside the flange"

floor_axial_ratio = (rearFaceZ - boltHoleDepth - ellipseCenterZ) / ellipseAxialSemiAxis
assert abs(floor_axial_ratio) < 1.0, "infeasible: bolt-hole floor leaves the ellipse span"
floor_inner_radius = ellipseCenterR - ellipseRadialSemiAxis * math.sqrt(1.0 - floor_axial_ratio * floor_axial_ratio)
assert floor_inner_radius + boltHoleDiameter / 2.0 < boltCircleDiameter / 2.0, (
    "infeasible: bolt hole breaks into the flow contour"
)

# x = r = centerR + b*cos(θ), y = z = centerZ + a*sin(θ). θ = -90° is the lip vertex.
inner_cos = -math.sqrt(1.0 - rear_axial_ratio * rear_axial_ratio)
rear_angle = math.degrees(math.atan2(rear_axial_ratio, inner_cos))
vertex_angle = -90.0
inner = EllipticalCenterArc(
    (ellipseCenterR, ellipseCenterZ),
    ellipseRadialSemiAxis,
    ellipseAxialSemiAxis,
    rear_angle,
    arc_size=vertex_angle - rear_angle,
)
lip = CenterArc((ellipseCenterR, skinStartZ), lipRadius, vertex_angle, 90.0)
flange_outer_radius = flangeOuterDiameter / 2.0
outer = Polyline(
    lip @ 1,
    (flange_outer_radius, flangeFrontZ),
    (flange_outer_radius, rearFaceZ),
    inner @ 0,
)
profile = Plane.XZ * make_face((inner + lip + outer).edges())
# Quadrants, mirrored. A 360 revolve makes the gate's mass integral drift off-axis.
quarter = revolve(profile, axis=Axis.Z, revolution_arc=90)
half = quarter + mirror(quarter, about=Plane.YZ)
body = half + mirror(half, about=Plane.XZ)

hole_mouth_overrun = 0.05
hole_count = round(boltCount)
hole_tools = []
for i in range(hole_count):
    angle = math.radians(boltStartAngle + i * 360.0 / boltCount)
    hole_tools.append(
        Pos(
            boltCircleDiameter / 2.0 * math.cos(angle),
            boltCircleDiameter / 2.0 * math.sin(angle),
            rearFaceZ - boltHoleDepth,
        )
        * Cylinder(
            boltHoleDiameter / 2.0,
            boltHoleDepth + hole_mouth_overrun,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
result = body - Compound(hole_tools)

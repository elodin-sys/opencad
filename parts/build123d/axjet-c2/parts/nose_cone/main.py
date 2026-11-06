import math

from build123d import (
    Axis,
    BuildLine,
    CenterArc,
    Compound,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    make_face,
    revolve,
)

outerDiameter = 64.0
cylinderLength = 50.0
ogiveLength = 35.0
ogiveRadius = ((outerDiameter / 2) ** 2 + ogiveLength**2) / outerDiameter
wallThickness = 2.0
bulkheadFrontZ = -28.0
bulkheadThickness = 3.0
shaftHoleDiameter = 12.0
starterBoltCount = 4.0
starterBoltDiameter = 3.4
starterBoltPcd = 30.0
rimBoltCount = 4.0
rimBoltDiameter = 3.4
rimBoltPcd = 56.0
lipThickness = 3.0
lipInnerDiameter = 52.0
starterDiameter = 50.0
starterLength = 35.0
starterClearance = 2.0

assert cylinderLength >= -bulkheadFrontZ, "infeasible: cylinder must reach the bulkhead"
assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
assert starterLength > 0.0, "infeasible: starterLength must be positive"
assert starterDiameter > 0.0, "infeasible: starterDiameter must be positive"
assert starterClearance > 0.0, "infeasible: starterClearance must be positive"
assert outerDiameter / 2 - wallThickness - starterDiameter / 2 >= starterClearance, (
    "infeasible: bore is inside the starter clearance"
)

# A sharp apex on the axis is dropped by STEP; the flat is inside the 0.05 envelope.
tip_flat = 0.05
cutter_overrun = 0.02

r_out = outerDiameter / 2
r_bore = r_out - wallThickness
r_lip = lipInnerDiameter / 2
z_join = -cylinderLength
r_center = r_out - ogiveRadius
z_bulk_rear = bulkheadFrontZ + bulkheadThickness
z_lip = -lipThickness
inner_radius = ogiveRadius - wallThickness

outer_cos = (tip_flat - r_center) / ogiveRadius
inner_cos = (tip_flat - r_center) / inner_radius
assert -1.0 <= outer_cos <= 1.0, "infeasible: ogive does not reach the tip"
assert -1.0 <= inner_cos <= 1.0, "infeasible: inner ogive does not reach the tip"
phi = -math.acos(outer_cos)
psi = -math.acos(inner_cos)
z_tip = z_join + ogiveRadius * math.sin(phi)
z_cavity = z_join + inner_radius * math.sin(psi)
assert z_cavity > z_tip, "infeasible: cavity reaches past the tip"


def _pattern(count, diameter, pcd, z_center, height):
    holes = []
    n = int(count)
    radius = pcd / 2
    for i in range(n):
        angle = 2 * math.pi * i / n
        holes.append(Pos(radius * math.cos(angle), radius * math.sin(angle), z_center) * Cylinder(diameter / 2, height))
    return holes


def _revolve_xz(builder):
    # BuildLine draws on XY; map so local (r, z) lies on the XZ plane.
    return revolve(Plane.XZ * make_face(builder.wire()), axis=Axis.Z)


with BuildLine() as outer_line:
    Polyline((0.0, 0.0), (r_out, 0.0), (r_out, z_join))
    CenterArc((r_center, z_join), ogiveRadius, 0.0, math.degrees(phi))
    Polyline((tip_flat, z_tip), (0.0, z_tip), (0.0, 0.0))
outer = _revolve_xz(outer_line)

with BuildLine() as nose_line:
    Polyline((0.0, bulkheadFrontZ), (r_bore, bulkheadFrontZ), (r_bore, z_join))
    CenterArc((r_center, z_join), inner_radius, 0.0, math.degrees(psi))
    Polyline((tip_flat, z_cavity), (0.0, z_cavity), (0.0, bulkheadFrontZ))
nose_cavity = _revolve_xz(nose_line)

with BuildLine() as aft_line:
    Polyline(
        (0.0, z_bulk_rear),
        (r_bore, z_bulk_rear),
        (r_bore, z_lip),
        (r_lip, z_lip),
        (r_lip, cutter_overrun),
        (0.0, cutter_overrun),
        (0.0, z_bulk_rear),
    )
aft_cavity = _revolve_xz(aft_line)

bulk_height = bulkheadThickness + 2 * cutter_overrun
z_bulk_hole = bulkheadFrontZ + bulkheadThickness / 2
lip_height = lipThickness + 2 * cutter_overrun
z_lip_hole = -lipThickness / 2

holes = [Pos(0.0, 0.0, z_bulk_hole) * Cylinder(shaftHoleDiameter / 2, bulk_height)]
holes += _pattern(starterBoltCount, starterBoltDiameter, starterBoltPcd, z_bulk_hole, bulk_height)
holes += _pattern(rimBoltCount, rimBoltDiameter, rimBoltPcd, z_lip_hole, lip_height)

result = outer - nose_cavity - aft_cavity - Compound(children=holes)

import math

from build123d import Align, Axis, Compound, Cylinder, Polyline, Pos, make_face, revolve

frontFaceZ = -18.0
rearFaceZ = 18.0
boreDiameter = 180.5
ringOuterDiameter = 200.0
flangeOuterDiameter = 224.0
flangeThickness = 6.0
boltCircleDiameter = 212.0
boltHoleDiameter = 5.5
boltHoleCount = 8.0
boltStartAngle = 0.0
boltPitchAngle = 360.0 / boltHoleCount

assert rearFaceZ > frontFaceZ, "infeasible: rear face must be aft of the front face"
assert boreDiameter > 0.0, "infeasible: boreDiameter must be positive"
assert ringOuterDiameter > boreDiameter, "infeasible: ring OD must clear the bore"
assert flangeOuterDiameter > ringOuterDiameter, "infeasible: flange OD must exceed the ring OD"
assert flangeThickness > 0.0, "infeasible: flangeThickness must be positive"
assert 2 * flangeThickness < rearFaceZ - frontFaceZ, "infeasible: flanges must not meet"
assert boltCircleDiameter > 0.0, "infeasible: boltCircleDiameter must be positive"
assert boltHoleDiameter > 0.0, "infeasible: boltHoleDiameter must be positive"
assert boltHoleCount >= 1, "infeasible: boltHoleCount must be at least 1"
assert abs(boltHoleCount - round(boltHoleCount)) < 1e-9, "infeasible: boltHoleCount must be a whole number"
assert boltPitchAngle > 0.0, "infeasible: boltPitchAngle must be positive"
assert abs(boltStartAngle) < 360.0, "infeasible: boltStartAngle must be a single-turn clock"

bore_r = boreDiameter / 2.0
ring_r = ringOuterDiameter / 2.0
flange_r = flangeOuterDiameter / 2.0
hole_r = boltHoleDiameter / 2.0
pitch_r = boltCircleDiameter / 2.0
assert pitch_r - hole_r > ring_r, "infeasible: bolt holes break into the ring wall"
assert pitch_r + hole_r < flange_r, "infeasible: bolt holes break out of the flange rim"

front_back_z = frontFaceZ + flangeThickness
rear_back_z = rearFaceZ - flangeThickness

profile = Polyline(
    (bore_r, 0.0, frontFaceZ),
    (flange_r, 0.0, frontFaceZ),
    (flange_r, 0.0, front_back_z),
    (ring_r, 0.0, front_back_z),
    (ring_r, 0.0, rear_back_z),
    (flange_r, 0.0, rear_back_z),
    (flange_r, 0.0, rearFaceZ),
    (bore_r, 0.0, rearFaceZ),
    close=True,
)
body = revolve(make_face(profile), Axis.Z)

# Cutters overrun the flange faces into air so the tool caps are not coincident with the part.
cutter_overrun = 0.05
hole_depth = flangeThickness + 2.0 * cutter_overrun
hole_count = round(boltHoleCount)
holes = []
for i in range(hole_count):
    angle = math.radians(boltStartAngle + i * boltPitchAngle)
    x = pitch_r * math.cos(angle)
    y = pitch_r * math.sin(angle)
    holes.append(
        Pos(x, y, frontFaceZ + flangeThickness / 2.0)
        * Cylinder(hole_r, hole_depth, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    )
    holes.append(
        Pos(x, y, rearFaceZ - flangeThickness / 2.0)
        * Cylinder(hole_r, hole_depth, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    )
result = body - Compound(children=holes)

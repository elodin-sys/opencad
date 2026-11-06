import math

from build123d import (
    Align,
    Axis,
    Compound,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    make_face,
    revolve,
)

shaftFrontZ = -90.0
journalFrontZ = -75.0
journalRearZ = -40.0
shoulderFrontZ = 62.0
shoulderRearZ = 68.0
nutThreadFrontZ = -18.0
nutThreadRearZ = -8.0
flangeFrontZ = 254.0
shaftRearZ = 262.0
boreStartZ = -30.0
noseThreadDia = 20.0
journalDia = 25.0
drumDia = 40.0
neckDia = 36.0
shoulderDia = 46.0
nutThreadDia = 39.0
flangeDia = 60.0
boreDia = 28.0
recessDia = 44.0
recessDepth = 2.0
boltCircleDia = 50.0
boltCount = 6
boltHoleDia = 4.2
boltStartAngle = 0.0

assert (
    shaftFrontZ
    < journalFrontZ
    < journalRearZ
    < nutThreadFrontZ
    < nutThreadRearZ
    < shoulderFrontZ
    < shoulderRearZ
    < flangeFrontZ
    < shaftRearZ
), "infeasible: shaft stations out of order"
assert journalRearZ < boreStartZ < nutThreadFrontZ, "infeasible: boreStartZ cuts the journal or leaves the neck"
assert 0.0 < boreDia < neckDia, "infeasible: boreDia removes the neck wall and splits the shaft"
assert 0.0 < recessDepth < shaftRearZ - flangeFrontZ, "infeasible: recessDepth leaves the flange"
assert boreDia < recessDia, "infeasible: boreDia consumes the coupling recess"
assert noseThreadDia > 0.0 and journalDia > 0.0 and neckDia > 0.0, (
    "infeasible: nose, journal or neck diameter is not positive"
)
assert nutThreadDia > 0.0 and drumDia > 0.0 and shoulderDia > 0.0 and flangeDia > 0.0, (
    "infeasible: nut, drum, shoulder or flange diameter is not positive"
)
assert boltCount >= 1 and boltHoleDia > 0.0 and boltCircleDia > 0.0, "infeasible: bolt pattern is empty"

profile = Plane.XZ * Polyline(
    (0.0, shaftFrontZ),
    (noseThreadDia / 2, shaftFrontZ),
    (noseThreadDia / 2, journalFrontZ),
    (journalDia / 2, journalFrontZ),
    (journalDia / 2, journalRearZ),
    (neckDia / 2, journalRearZ),
    (neckDia / 2, nutThreadFrontZ),
    (nutThreadDia / 2, nutThreadFrontZ),
    (nutThreadDia / 2, nutThreadRearZ),
    (drumDia / 2, nutThreadRearZ),
    (drumDia / 2, shoulderFrontZ),
    (shoulderDia / 2, shoulderFrontZ),
    (shoulderDia / 2, shoulderRearZ),
    (drumDia / 2, shoulderRearZ),
    (drumDia / 2, flangeFrontZ),
    (flangeDia / 2, flangeFrontZ),
    (flangeDia / 2, shaftRearZ),
    (0.0, shaftRearZ),
    close=True,
)
outer = revolve(make_face(profile), axis=Axis.Z)

recess_floor_z = shaftRearZ - recessDepth
# Cutters overrun open faces and overlap each other so no tool face lies on stock.
cutter_overrun = 0.05
bore_tool = Pos(0, 0, boreStartZ) * Cylinder(
    boreDia / 2,
    recess_floor_z + cutter_overrun - boreStartZ,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
recess_tool = Pos(0, 0, recess_floor_z) * Cylinder(
    recessDia / 2,
    recessDepth + cutter_overrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
bolt_z0 = flangeFrontZ - cutter_overrun
bolt_height = shaftRearZ - flangeFrontZ + 2 * cutter_overrun
pitch = boltCircleDia / 2
bolt_tools = []
for i in range(int(boltCount)):
    angle = math.radians(boltStartAngle + 360.0 * i / boltCount)
    bolt_tools.append(
        Pos(pitch * math.cos(angle), pitch * math.sin(angle), bolt_z0)
        * Cylinder(
            boltHoleDia / 2,
            bolt_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )

result = outer - Compound([bore_tool + recess_tool, *bolt_tools])

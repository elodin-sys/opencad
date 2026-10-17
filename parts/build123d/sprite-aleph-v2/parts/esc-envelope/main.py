"""ARK4IN1 ESC provisional analytic clearance envelope, in the assembly frame.

Dimensions follow the frozen proposal and explicit provisional contract recipe.
Source PCB thickness 1.61 differs from the placed 1.60; the 12 mm spacers from
z=-7.2 imply -19.2, versus the pinned PCB seat at -19.0. Source +/- component
allowances and the quoted 9.43 socket thickness have unresolved datums and are
not added to the placed stack. The 24 g source mass is not a model density.

Component footprints, individual socket widths, plug profiles and stud height
are provisional. Slot proxies cannot certify the full PCB corners against the
curved cone. Wiring, real ring/boss distances and terminal access need assembly
verification; no bracket, spacers, wiring or future flight controller is added.
"""

from math import sqrt

from build123d import Align, Box, Compound, Cylinder, Pos

pcbLength = 63.15
pcbWidth = 42.25
sourcePcbThickness = 1.61
pcbXMin = -22.75
pcbXMax = 19.5
pcbZMin = -20.6
pcbZMax = -19.0
boardHolePitch = 30.5
originalHoleDiameter = 3.5
reamedHoleDiameter = 3.8
clampPitch = 30.0
clampDiameter = 3.0
spacerLength = 12.0
mountUndersideZ = -7.2
componentTopZ = -14.4
componentBottomZ = -25.5
socketStartY = 31.6
socketEndY = 38.3
socketTopZ = -18.6
plugReach = 46.5
slotHalfWidth = 22.5
slotBottomZ = -27.0
slotTopZ = -17.0
studX = -20.0
studOffsetY = 6.0
studDiameter = 2.5
sourcePlusAllowance = 4.85
sourceMinusAllowance = 4.58
sourceSocketSpan = 76.6
sourceSocketWidth = 42.3
sourceSocketThickness = 9.43
pcbHalfLength = pcbLength / 2.0
pcbPlacedThickness = pcbZMax - pcbZMin
holeAxisOffset = (boardHolePitch - clampPitch) / 2.0
studHeight = componentTopZ - pcbZMax
coreHalfWidth = 18.0
coreHalfLength = 23.0
socketLeftX = -21.0
socketInnerX = 4.0
connectorRootY = 31.5
plugTopZ = -18.6

# Ordering and containment guards allow the contract's independent edit tests.
assert min(pcbLength, pcbWidth, pcbPlacedThickness) > 0.0, "infeasible: PCB dimensions must be positive"
assert componentBottomZ < pcbZMin < pcbZMax < componentTopZ, "infeasible: PCB must lie inside the component Z limits"
assert 0.0 < coreHalfWidth < min(-pcbXMin, pcbXMax), "infeasible: component core must fit across the PCB"
assert 0.0 < coreHalfLength < connectorRootY < pcbHalfLength, "infeasible: roots must overlap PCB ends beyond the core"
assert connectorRootY < socketStartY < socketEndY < plugReach, "infeasible: plugReach must extend beyond the sockets"
assert pcbXMin < socketLeftX < -socketInnerX < 0.0 < socketInnerX < pcbXMax, (
    "infeasible: two nonzero socket lobes must retain a central split"
)
assert pcbZMax < socketTopZ < componentTopZ, "infeasible: sockets must connect to PCB without extending the core top"
assert componentBottomZ < plugTopZ < componentTopZ, "infeasible: plugs must overlap the sockets in Z"
assert slotBottomZ < componentBottomZ < max(socketTopZ, plugTopZ) < slotTopZ, (
    "infeasible: connectors must lie inside the slot Z limits"
)
assert -slotHalfWidth < socketLeftX and pcbXMax < slotHalfWidth, (
    "infeasible: connectors must lie inside the slot X limits"
)
assert 0.0 < originalHoleDiameter <= reamedHoleDiameter < boardHolePitch, "infeasible: invalid bore diameters or pitch"
assert boardHolePitch / 2.0 + reamedHoleDiameter / 2.0 < min(coreHalfWidth, coreHalfLength), (
    "infeasible: complete bores must lie inside the core"
)
assert reamedHoleDiameter / 2.0 - clampDiameter / 2.0 - sqrt(2.0) * abs(holeAxisOffset) >= 0.03, (
    "infeasible: unchanged M3 clamp axes do not fit reamed bores"
)
assert studDiameter > 0.0 and studHeight > 0.0, "infeasible: stud dimensions must be positive"
assert pcbXMin < studX - studDiameter / 2.0 < studX + studDiameter / 2.0 < -coreHalfWidth, (
    "infeasible: studs must lie on the PCB outside the core"
)
assert studDiameter / 2.0 < studOffsetY < pcbHalfLength - studDiameter / 2.0, (
    "infeasible: studs must be separate and inside the PCB ends"
)

# PCB: global XY rectangle extruded along +Z; retain the asymmetric X station.
pcb = Pos(pcbXMin, -pcbHalfLength, pcbZMin) * Box(
    pcbWidth,
    pcbLength,
    pcbPlacedThickness,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
# Provisional central components stop before the connector bands at both ends.
components = Pos(-coreHalfWidth, -coreHalfLength, componentBottomZ) * Box(
    2.0 * coreHalfWidth,
    2.0 * coreHalfLength,
    componentTopZ - componentBottomZ,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
body = pcb + components

# Four provisional MR30 socket lobes. Each analytic root overlaps the exact
# PCB end by 0.075 mm; socketStartY remains the source's rounded provenance.
socket_intervals = ((socketLeftX, -socketInnerX), (socketInnerX, pcbXMax))
for end_sign in (-1.0, 1.0):
    for x_min, x_max in socket_intervals:
        socket = Pos(
            x_min,
            min(end_sign * connectorRootY, end_sign * socketEndY),
            componentBottomZ,
        ) * Box(
            x_max - x_min,
            socketEndY - connectorRootY,
            socketTopZ - componentBottomZ,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )
        body = body + socket

# Mated plugs share complete end faces with the socket lobes. At nominal
# plugTopZ == socketTopZ the socket/plug seam disappears on union.
for end_sign in (-1.0, 1.0):
    for x_min, x_max in socket_intervals:
        plug = Pos(
            x_min,
            min(end_sign * socketEndY, end_sign * plugReach),
            componentBottomZ,
        ) * Box(
            x_max - x_min,
            plugReach - socketEndY,
            plugTopZ - componentBottomZ,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )
        body = body + plug

# Nominal M2.5 thread-major-diameter pins; height is an explicit allowance.
# The two distinct pins meet the PCB at pcbZMax and remain outside the core.
for stud_y in (-studOffsetY, studOffsetY):
    stud = Pos(studX, stud_y, pcbZMax) * Cylinder(
        studDiameter / 2.0,
        studHeight,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = body + stud

# Ream the true 30.5 pattern through all clearance material in one cut.
# The M3 hardware remains on the independent 30.0 pattern, checked by the critic.
cut_overrun = 0.02
bore_tools = [
    Pos(hole_x, hole_y, componentBottomZ - cut_overrun)
    * Cylinder(
        reamedHoleDiameter / 2.0,
        componentTopZ - componentBottomZ + 2.0 * cut_overrun,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for hole_x in (-boardHolePitch / 2.0, boardHolePitch / 2.0)
    for hole_y in (-boardHolePitch / 2.0, boardHolePitch / 2.0)
]
result = body - Compound(bore_tools)
result.label = "escEnvelope"

# Assembly interface metadata; external spacers are not clearance material.
joints = {"escOnSpacers": {"origin": [0.0, 0.0, pcbZMax], "axis": [0.0, 0.0, 1.0]}}
assert result.is_valid, "kernel: clearance envelope must be valid"
assert len(result.solids()) == 1, "kernel: clearance envelope must remain one connected solid"

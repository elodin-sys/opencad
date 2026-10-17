import math

from build123d import (
    CenterArc,
    Circle,
    Compound,
    Cylinder,
    Line,
    Polyline,
    Pos,
    Rectangle,
    extrude,
    fillet,
    make_face,
    make_hull,
)

plateThickness = 6.0
bodyHalfWidth = 25.0
bodyHalfLength = 37.5
bodyEndRadius = 25.0
bodyEndCentreY = bodyHalfLength - bodyEndRadius
centreHoleDiameter = 27.0
centreBoltSpacing = 30.0
centreBoltDiameter = 3.1
crescentFlatY = 25.5
crescentRim = 3.0
crescentOuterRadius = bodyEndRadius - crescentRim
crescentCornerRadius = 3.0
armWidth = 12.0
motorAxisOffset = 80.0
motorHoleDiameter = 6.0
motorSlotWidth = 3.1
motorSlotInnerRadius = 8.0
motorSlotOuterRadius = 9.5
padRadius = 11.5
lobeRadius = 4.0
outlineHalfSpan = motorAxisOffset + motorSlotOuterRadius + lobeRadius
bodyArmFilletRadius = 6.0
endArmFilletRadius = 5.0
armPadFilletRadius = 20.0
lobeFilletRadius = 3.0
motorBoltPattern = 12.0

assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert centreHoleDiameter > 0, "infeasible: centreHoleDiameter must be positive"
assert motorSlotInnerRadius < motorSlotOuterRadius, "infeasible: motor slot length"
assert crescentFlatY > bodyEndCentreY, "infeasible: D-slot flat crosses the end-arc centre"
assert crescentFlatY < bodyEndCentreY + crescentOuterRadius, "infeasible: D-slot misses the end arc"
assert padRadius > armWidth / 2.0, "infeasible: pad narrower than the arm"
assert bodyArmFilletRadius > 0 and endArmFilletRadius > 0, "infeasible: body fillet"
assert armPadFilletRadius > 0 and lobeFilletRadius > 0 and lobeRadius > 0, "infeasible: pad fillet"
assert outlineHalfSpan > motorAxisOffset, "infeasible: outline collapses inside the motor axes"

# Preserve the inherited 16-19 mm radial slots at the nominal 12 mm square setting.
motor_slot_shift = (motorBoltPattern - 12.0) / math.sqrt(2.0)
assert motorBoltPattern > 0, "infeasible: motorBoltPattern must be positive"
assert motorSlotInnerRadius + motor_slot_shift - motorSlotWidth / 2.0 > motorHoleDiameter / 2.0, (
    "infeasible: shifted motor slots meet the motor centre hole"
)
assert abs(motor_slot_shift) + motorSlotWidth / 2.0 < lobeRadius, (
    "infeasible: shifted motor slots leave their fixed outline lobes"
)

bolt_clearance = (centreBoltSpacing / 2.0) * math.sqrt(2.0)
assert centreHoleDiameter / 2.0 + centreBoltDiameter / 2.0 < bolt_clearance, (
    "infeasible: centre hole meets the M3 pattern"
)

edge_offset = (armWidth / 2.0) * math.sqrt(2.0)
flat_corner_y = bodyHalfWidth - edge_offset
assert flat_corner_y > bodyEndCentreY, "infeasible: arm covers the centre-body flat"

lobe_offset = outlineHalfSpan - motorAxisOffset - lobeRadius


def vertical_kinks(part, predicate, span):
    found = []
    for edge in part.edges():
        box = edge.bounding_box()
        tall = box.max.Z - box.min.Z > span * 0.8
        straight = box.max.X - box.min.X < 0.15 and box.max.Y - box.min.Y < 0.15
        if tall and straight:
            center = edge.center()
            if predicate(float(center.X), float(center.Y)):
                found.append(edge)
    return found


def on_arm_edge(x, y, tol=0.15):
    return abs(abs(x - y) - edge_offset) < tol or abs(abs(x + y) - edge_offset) < tol


def arm_face(sign_x, sign_y, station_0, station_1):
    def point(station, side):
        perp = (-sign_y, sign_x)
        scale = (armWidth / 2.0) / math.sqrt(2.0) * side
        return (
            sign_x * (station / 2.0) + perp[0] * scale,
            sign_y * (station / 2.0) + perp[1] * scale,
        )

    corners = [
        point(station_0, 1),
        point(station_1, 1),
        point(station_1, -1),
        point(station_0, -1),
    ]
    return make_face([Polyline(*corners, close=True)])


stadium = make_face(
    [
        Line((bodyHalfWidth, -bodyEndCentreY), (bodyHalfWidth, bodyEndCentreY)),
        CenterArc((0, bodyEndCentreY), bodyEndRadius, 0, 180),
        Line((-bodyHalfWidth, bodyEndCentreY), (-bodyHalfWidth, -bodyEndCentreY)),
        CenterArc((0, -bodyEndCentreY), bodyEndRadius, 180, 180),
    ]
)
# Flats run out to the arm-edge corners so the R6 fillet is tangent to x = ±bodyHalfWidth.
centre = stadium + Pos(0, 0) * Rectangle(2 * bodyHalfWidth, 2 * flat_corner_y)

arm_start = bodyHalfWidth
arm_end = 2 * motorAxisOffset - padRadius * math.sqrt(2.0) / 2.0
arms = None
motors = []
for sign_x in (1, -1):
    for sign_y in (1, -1):
        motors.append((sign_x * motorAxisOffset, sign_y * motorAxisOffset))
        arm = arm_face(sign_x, sign_y, arm_start, arm_end)
        arms = arm if arms is None else arms + arm

pads = None
for motor_x, motor_y in motors:
    pad = Pos(motor_x, motor_y) * Circle(padRadius)
    pads = pad if pads is None else pads + pad

plate = extrude(centre + arms + pads, amount=-plateThickness)


def arm_meets_pad(x, y):
    if not on_arm_edge(x, y):
        return False
    return any(abs(math.hypot(x - cx, y - cy) - padRadius) < 0.15 for cx, cy in motors)


plate = fillet(vertical_kinks(plate, arm_meets_pad, plateThickness), armPadFilletRadius)


def flat_corner(x, y):
    return abs(abs(x) - bodyHalfWidth) < 0.12 and abs(abs(y) - flat_corner_y) < 0.25


def end_arc_corner(x, y):
    on_arc = (
        abs(math.hypot(x, y - bodyEndCentreY) - bodyEndRadius) < 0.25
        or abs(math.hypot(x, y + bodyEndCentreY) - bodyEndRadius) < 0.25
    )
    return on_arc and on_arm_edge(x, y, 0.25)


plate = fillet(vertical_kinks(plate, flat_corner, plateThickness), bodyArmFilletRadius)
plate = fillet(vertical_kinks(plate, end_arc_corner, plateThickness), endArmFilletRadius)

lobe_steps = (
    (lobe_offset, 0.0),
    (-lobe_offset, 0.0),
    (0.0, lobe_offset),
    (0.0, -lobe_offset),
)
for motor_x, motor_y in motors:
    for step_x, step_y in lobe_steps:
        lobe = Pos(motor_x + step_x, motor_y + step_y, -plateThickness / 2.0) * Cylinder(lobeRadius, plateThickness)
        plate = plate + lobe


def lobe_junction(x, y):
    for motor_x, motor_y in motors:
        for step_x, step_y in lobe_steps:
            if abs(math.hypot(x - (motor_x + step_x), y - (motor_y + step_y)) - lobeRadius) < 0.2:
                return True
    return False


plate = fillet(vertical_kinks(plate, lobe_junction, plateThickness), lobeFilletRadius)


def through_hole(x, y, diameter):
    return Pos(x, y, -plateThickness / 2.0) * Cylinder(diameter / 2.0, plateThickness + 0.1)


def d_slot_tool(sign):
    arc_y = sign * bodyEndCentreY
    flat_y = sign * crescentFlatY
    rise = flat_y - arc_y
    half_x = math.sqrt(crescentOuterRadius**2 - rise**2)
    start = math.degrees(math.atan2(rise, half_x))
    sweep = 180.0 - 2.0 * abs(start)
    if sign > 0:
        arc = CenterArc((0, arc_y), crescentOuterRadius, start, sweep)
        chord = Line((-half_x, flat_y), (half_x, flat_y))
    else:
        arc = CenterArc((0, arc_y), crescentOuterRadius, start, -sweep)
        chord = Line((half_x, flat_y), (-half_x, flat_y))
    depth = plateThickness + 0.1
    solid = extrude(make_face([arc, chord]), amount=-depth)
    corners = vertical_kinks(solid, lambda x, y: abs(abs(x) - half_x) < 0.05, depth)
    assert len(corners) == 2, "D-slot corners missing"
    return Pos(0, 0, 0.05) * fillet(corners, crescentCornerRadius)


def motor_slot_tool(motor_x, motor_y, step_x, step_y):
    radius = motorSlotWidth / 2.0
    inner = (
        motor_x + step_x * (motorSlotInnerRadius + motor_slot_shift),
        motor_y + step_y * (motorSlotInnerRadius + motor_slot_shift),
    )
    outer = (
        motor_x + step_x * (motorSlotOuterRadius + motor_slot_shift),
        motor_y + step_y * (motorSlotOuterRadius + motor_slot_shift),
    )
    sketch = make_hull(
        [
            (Pos(inner[0], inner[1]) * Circle(radius)).edges(),
            (Pos(outer[0], outer[1]) * Circle(radius)).edges(),
        ]
    )
    return extrude(Pos(0, 0, 0.05) * sketch, amount=-(plateThickness + 0.1))


tools = [through_hole(0, 0, centreHoleDiameter)]
bolt = centreBoltSpacing / 2.0
for sign_x in (1, -1):
    for sign_y in (1, -1):
        tools.append(through_hole(sign_x * bolt, sign_y * bolt, centreBoltDiameter))
        tools.append(through_hole(sign_x * motorAxisOffset, sign_y * motorAxisOffset, motorHoleDiameter))
tools.append(d_slot_tool(1))
tools.append(d_slot_tool(-1))
for motor_x, motor_y in motors:
    for step_x, step_y in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        tools.append(motor_slot_tool(motor_x, motor_y, step_x, step_y))

result = plate - Compound(children=tools)

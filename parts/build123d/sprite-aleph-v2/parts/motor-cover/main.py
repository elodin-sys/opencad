import math

from build123d import CenterArc, Circle, Line, Pos, extrude, make_face

motorAxisOffset = 80.0
coverHeight = 10.0
plateThickness = 6.0
outerRadius = 14.0
plateTipRadius = 11.5
lugOffset = 9.5
lugRadius = 4.0
plateCornerRadius = 3.0
motorClearanceRadius = 13.0
openingHalfAngle = 29.0

assert coverHeight > plateThickness, "infeasible: cover taller than the plate slot"
assert motorClearanceRadius < outerRadius, "infeasible: motor clearance inside the outer wall"
assert motorClearanceRadius > 0.0, "infeasible: motor clearance radius must be positive"
assert outerRadius > plateTipRadius > 0.0, "infeasible: plate tip inside the outer wall"
assert lugRadius > 0.0 and plateCornerRadius > 0.0 and lugOffset > 0.0, "infeasible: lug geometry"
assert 0.0 < openingHalfAngle < 90.0, "infeasible: opening half-angle"

_axis = (motorAxisOffset, motorAxisOffset)
_blend_reach = plateTipRadius + plateCornerRadius
_fillet_span = lugRadius + plateCornerRadius
_cos_alpha = (lugOffset**2 + _blend_reach**2 - _fillet_span**2) / (2.0 * lugOffset * _blend_reach)
assert -1.0 < _cos_alpha < 1.0, "infeasible: lug blend does not meet the plate tip"
_alpha = math.degrees(math.acos(_cos_alpha))
_opening_center = math.degrees(math.atan2(-motorAxisOffset, -motorAxisOffset)) % 360.0
_end_angles = (
    (_opening_center - openingHalfAngle) % 360.0,
    (_opening_center + openingHalfAngle) % 360.0,
)


def _polar(angle, radius):
    theta = math.radians(angle)
    return (
        motorAxisOffset + radius * math.cos(theta),
        motorAxisOffset + radius * math.sin(theta),
    )


def _disk(center, radius):
    return Pos(center[0], center[1]) * Circle(radius)


def _circle_intersections(center_a, radius_a, center_b, radius_b):
    ax, ay = center_a
    bx, by = center_b
    distance = math.hypot(bx - ax, by - ay)
    assert abs(radius_a - radius_b) < distance < radius_a + radius_b, "infeasible: flank arc does not meet the lug"
    along = (radius_a**2 - radius_b**2 + distance**2) / (2.0 * distance)
    height = math.sqrt(radius_a**2 - along**2)
    mid = (ax + along * (bx - ax) / distance, ay + along * (by - ay) / distance)
    ox = -(by - ay) * height / distance
    oy = (bx - ax) * height / distance
    return ((mid[0] + ox, mid[1] + oy), (mid[0] - ox, mid[1] - oy))


def _nearest_lug(angle):
    lugs = (0.0, 90.0, 180.0, 270.0)

    def separation(lug):
        delta = abs(angle - lug) % 360.0
        return min(delta, 360.0 - delta)

    return min(lugs, key=separation)


def _opening_sector():
    radius = outerRadius + lugRadius
    arc = CenterArc(_axis, radius, _end_angles[0], 2.0 * openingHalfAngle)
    return make_face([arc, Line(arc @ 1, _axis), Line(_axis, arc @ 0)])


def _flank_cap(end_angle):
    lug_angle = _nearest_lug(end_angle)
    outer_point = _polar(end_angle, outerRadius)
    lug_center = _polar(lug_angle, lugOffset)
    flank_center = max(
        _circle_intersections(outer_point, plateCornerRadius, lug_center, _fillet_span),
        key=lambda point: math.hypot(point[0] - motorAxisOffset, point[1] - motorAxisOffset),
    )
    vx, vy = flank_center[0] - lug_center[0], flank_center[1] - lug_center[1]
    span = math.hypot(vx, vy)
    tangent = (lug_center[0] + lugRadius * vx / span, lug_center[1] + lugRadius * vy / span)
    theta = math.radians(end_angle)
    direction = (math.cos(theta), math.sin(theta))
    # Outer hit of the end ray on the lug circle: the flat the arc replaces.
    bx, by = motorAxisOffset - lug_center[0], motorAxisOffset - lug_center[1]
    linear = 2.0 * (bx * direction[0] + by * direction[1])
    constant = bx**2 + by**2 - lugRadius**2
    root = math.sqrt(linear**2 - 4.0 * constant)
    ray_t = max((-linear + root) / 2.0, (-linear - root) / 2.0)
    hit = (
        motorAxisOffset + ray_t * direction[0],
        motorAxisOffset + ray_t * direction[1],
    )
    start = math.degrees(math.atan2(tangent[1] - flank_center[1], tangent[0] - flank_center[0]))
    stop = math.degrees(math.atan2(outer_point[1] - flank_center[1], outer_point[0] - flank_center[0]))
    sweep = (stop - start) % 360.0
    if sweep > 180.0:
        sweep -= 360.0
    flank_arc = CenterArc(flank_center, plateCornerRadius, start % 360.0, sweep)
    lug_start = math.degrees(math.atan2(hit[1] - lug_center[1], hit[0] - lug_center[0]))
    lug_stop = math.degrees(math.atan2(tangent[1] - lug_center[1], tangent[0] - lug_center[0]))
    lug_sweep = (lug_stop - lug_start) % 360.0
    if lug_sweep > 180.0:
        lug_sweep -= 360.0
    lug_arc = CenterArc(lug_center, lugRadius, lug_start % 360.0, lug_sweep)
    return make_face([flank_arc, Line(flank_arc @ 1, lug_arc @ 0), lug_arc])


def _blend_sliver(lug_angle, side):
    blend_angle = (lug_angle + side * _alpha) % 360.0
    if _end_angles[0] <= blend_angle <= _end_angles[1]:
        return None
    blend_center = _polar(blend_angle, _blend_reach)
    lug_center = _polar(lug_angle, lugOffset)
    tip_point = _polar(blend_angle, plateTipRadius)
    vx, vy = blend_center[0] - lug_center[0], blend_center[1] - lug_center[1]
    span = math.hypot(vx, vy)
    lug_point = (lug_center[0] + lugRadius * vx / span, lug_center[1] + lugRadius * vy / span)
    tip_angle = math.degrees(math.atan2(tip_point[1] - blend_center[1], tip_point[0] - blend_center[0]))
    lug_ang = math.degrees(math.atan2(lug_point[1] - blend_center[1], lug_point[0] - blend_center[0]))
    sweep = (lug_ang - tip_angle) % 360.0
    if sweep > 180.0:
        sweep -= 360.0
    arc = CenterArc(blend_center, plateCornerRadius + 2.0, tip_angle % 360.0, sweep)
    wedge = make_face([arc, Line(arc @ 1, blend_center), Line(blend_center, arc @ 0)])
    return wedge - _disk(blend_center, plateCornerRadius) - _disk(_axis, plateTipRadius) - _disk(lug_center, lugRadius)


def _profile(inner_radius, with_blends):
    face = _disk(_axis, outerRadius) - _disk(_axis, inner_radius)
    for lug_angle in (0.0, 90.0, 180.0, 270.0):
        face -= _disk(_polar(lug_angle, lugOffset), lugRadius)
    face -= _opening_sector()
    for end_angle in _end_angles:
        face -= _flank_cap(end_angle)
    if with_blends:
        for lug_angle in (0.0, 90.0, 180.0, 270.0):
            for side in (-1.0, 1.0):
                sliver = _blend_sliver(lug_angle, side)
                if sliver is not None:
                    face -= sliver
    return face


_band = _profile(plateTipRadius, True)
_skirt = _profile(motorClearanceRadius, False)
assert len(_band.faces()) == 1, "infeasible: band profile is not a single loop"
assert len(_skirt.faces()) == 1, "infeasible: skirt profile is not a single loop"

# Skirt footprint is inside the band, so a short overlap fuses without a coplanar ledge.
_overlap = 0.02
_skirt_height = coverHeight - plateThickness
_band_solid = extrude(_band, amount=-plateThickness)
_skirt_solid = Pos(0, 0, -plateThickness + _overlap) * extrude(_skirt, amount=-(_skirt_height + _overlap))
result = _band_solid + _skirt_solid

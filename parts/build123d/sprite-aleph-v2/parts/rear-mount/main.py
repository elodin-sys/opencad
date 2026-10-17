"""Sprite Aleph rear mount in the original frame-top datum.

The supplied source OUTLINE, WINDOW, SLOT and loft station tables are preserved.
The ring is trimmed locally at ringBottomZ, the obsolete U-channel is omitted,
and only the ring-associated bore-support tails are trimmed at blockBottomZ.
Rear-shell and ESC hardware placement belongs to the assembly.
"""

from math import atan2, cos, pi, sin, sqrt

from build123d import (
    Box,
    Compound,
    Cylinder,
    Face,
    Plane,
    Polyline,
    Pos,
    Spline,
    ThreePointArc,
    Wire,
    extrude,
    loft,
    make_face,
    mirror,
    offset,
)

mountTopZ = -6.0
plateThickness = 1.2
bodyWidth = 50.0
bodyYMin = -36.53
plateFlatHalfLength = 9.35
plateEndSemiAxis = 27.3
bodyYMax = 36.7
wallThickness = 1.2
ringBottomZ = -13.0
sideLandBottomZ = -9.0
holeSpacing = 30.0
holeDiameter = 3.1
crossBoreDiameter = 3.2
crossBoreZ = -10.0
tabWidth = 18.0
tabYMin = 25.5
tabYMax = 30.0
blockBottomZ = -13.33
windowHalfWidth = 21.5
windowWideYMin = -7.5
windowWideYMax = 9.5
windowNeckHalfWidth = 10.0
windowNeckYMax = 22.5
slotHalfWidth = 10.25
slotYMax = -19.5
slotBossYMax = -29.5

assert plateThickness > 0.2, "infeasible: plateThickness must be positive"
assert plateThickness < mountTopZ - sideLandBottomZ, "infeasible: plate consumes the side lands"
assert wallThickness > 0.2, "infeasible: wallThickness must be positive"
assert holeDiameter > 0.2, "infeasible: holeDiameter must be positive"
assert holeSpacing > holeDiameter + 1.0, "infeasible: clamp holes overlap"
assert crossBoreDiameter > 0.2, "infeasible: crossBoreDiameter must be positive"
assert bodyYMax > plateFlatHalfLength, "infeasible: bodyYMax inside the flat land"
assert -bodyYMin > plateFlatHalfLength, "infeasible: bodyYMin inside the flat land"
assert plateEndSemiAxis > 1.0, "infeasible: plateEndSemiAxis must be positive"
assert sideLandBottomZ < mountTopZ, "infeasible: side lands above the top face"
assert sideLandBottomZ > ringBottomZ, "infeasible: side lands below the ring rim"

assert blockBottomZ < ringBottomZ, "infeasible: cap must remain below the ring cutoff"
assert blockBottomZ - (-14.4) >= 1.0, "infeasible: retained bosses violate ESC clearance"
assert ringBottomZ < -12.0067, "infeasible: ring cutoff consumes the source window bottoms"
assert ringBottomZ > -21.0, "infeasible: ring cutoff is below the source rim"
assert blockBottomZ < crossBoreZ - crossBoreDiameter / 2, "infeasible: cap does not enclose the bore"
assert crossBoreZ + crossBoreDiameter / 2 < mountTopZ - plateThickness, "infeasible: bore intersects plate"
assert tabWidth > crossBoreDiameter + 2 * wallThickness, "infeasible: cross bore consumes the cap"
assert tabYMax > tabYMin, "infeasible: cap has no length"
assert 0 < windowNeckHalfWidth < windowHalfWidth < bodyWidth / 2, "infeasible: window consumes side lands"
assert holeSpacing / 2 + holeDiameter / 2 < bodyWidth / 2, "infeasible: clamp hole outside plate"

# Inherited source outline, preserved without refitting or loading reference geometry.
MESH_X = 25.0
MESH_Y_POS = 36.6946
MESH_Y_NEG = -36.5286
# Inward drift of the ring's outer skin from the plate underside to the rim.
rimInset = 0.45
# Bore tongues. Wide enough for the (3, ±32) probes and narrow enough for the z=-12 caps.
endTongueHalfWidth = 4.0
sideOpenY0 = -14.6
sideOpenY1 = 15.6
ringWindowNeg = (-26.5, -17.5)
ringWindowPos = (17.5, 25.7)
ringWindowZ = (-12.1, -7.1)


def dedupe(pts, tol=0.04):
    kept = [pts[0]]
    for point in pts[1:]:
        dx = point[0] - kept[-1][0]
        dy = point[1] - kept[-1][1]
        if dx * dx + dy * dy > tol * tol:
            kept.append(point)
    dx = kept[0][0] - kept[-1][0]
    dy = kept[0][1] - kept[-1][1]
    if dx * dx + dy * dy < tol * tol:
        kept.pop()
    return kept


def scale_outline(pts):
    # plateFlatHalfLength / plateEndSemiAxis describe the same outline the mesh sample fits.
    _ = (plateFlatHalfLength, plateEndSemiAxis)
    scaled = []
    for x, y in pts:
        xs = x / MESH_X * (bodyWidth / 2.0)
        if y >= 0.0:
            ys = y / MESH_Y_POS * bodyYMax
        else:
            ys = y / MESH_Y_NEG * bodyYMin
        scaled.append((xs, ys))
    return dedupe(scaled)


def scale_window(pts):
    sx = windowHalfWidth / 21.5
    sy = (windowNeckYMax - windowWideYMin) / 30.0
    return dedupe([(x * sx, y * sy) for x, y in pts])


def scale_slot(pts):
    sx = slotHalfWidth / 10.25
    dy = slotYMax - (-19.5)
    return dedupe([(x * sx, y + dy) for x, y in pts])


OUTLINE = [
    (0.0000, 36.6946),
    (1.3985, 36.6585),
    (4.1618, 36.3372),
    (5.9877, 35.9439),
    (8.6382, 35.0989),
    (10.3480, 34.3661),
    (11.9963, 33.5037),
    (14.3318, 31.9785),
    (16.3511, 30.3833),
    (17.2756, 29.8782),
    (18.2877, 29.5458),
    (19.5411, 28.0931),
    (20.6879, 26.5356),
    (22.1560, 24.0807),
    (22.9784, 22.3485),
    (23.9615, 19.6306),
    (24.6213, 16.8351),
    (24.3222, 15.9712),
    (24.1045, 14.7632),
    (24.1303, 12.1588),
    (24.4662, 10.5802),
    (25.0000, 9.4874),
    (25.0000, -9.3219),
    (24.4673, -10.4118),
    (24.2428, -11.1934),
    (24.0769, -13.9472),
    (24.2190, -15.3742),
    (24.6418, -16.7171),
    (24.2520, -18.5696),
    (23.7221, -20.3905),
    (22.6662, -23.0471),
    (21.8015, -24.7350),
    (20.8113, -26.3524),
    (19.7017, -27.8897),
    (18.4781, -29.3393),
    (17.3954, -29.6619),
    (16.7066, -29.9970),
    (13.5731, -32.3507),
    (11.1805, -33.7847),
    (8.6452, -34.9301),
    (6.8770, -35.5317),
    (4.1618, -36.1712),
    (0.0000, -36.5286),
    (-1.3910, -36.4929),
    (-4.1618, -36.1712),
    (-6.8770, -35.5317),
    (-8.6452, -34.9301),
    (-11.1805, -33.7847),
    (-13.5731, -32.3507),
    (-16.7066, -29.9970),
    (-17.3954, -29.6619),
    (-18.4781, -29.3393),
    (-19.7017, -27.8897),
    (-20.8113, -26.3524),
    (-21.8015, -24.7350),
    (-22.6662, -23.0471),
    (-23.7221, -20.3905),
    (-24.2520, -18.5696),
    (-24.6418, -16.7171),
    (-24.2190, -15.3742),
    (-24.0769, -13.9472),
    (-24.2428, -11.1934),
    (-24.4673, -10.4118),
    (-25.0000, -9.3219),
    (-25.0000, 9.4874),
    (-24.4662, 10.5802),
    (-24.1303, 12.1588),
    (-24.1045, 14.7632),
    (-24.3222, 15.9712),
    (-24.6213, 16.8351),
    (-23.9615, 19.6306),
    (-22.9784, 22.3485),
    (-22.1560, 24.0807),
    (-20.6879, 26.5356),
    (-19.5411, 28.0931),
    (-18.2877, 29.5458),
    (-17.2756, 29.8782),
    (-16.3511, 30.3833),
    (-14.3318, 31.9785),
    (-11.9963, 33.5037),
    (-10.3480, 34.3661),
    (-8.6382, 35.0989),
    (-5.9877, 35.9439),
    (-4.1618, 36.3372),
    (-1.3985, 36.6585),
]

WINDOW = [
    (8.0000, 22.5000),
    (8.5176, 22.4319),
    (9.0000, 22.2320),
    (9.5867, 21.7175),
    (9.8478, 21.2654),
    (9.9829, 20.7611),
    (10.0187, 16.9541),
    (10.2967, 15.3416),
    (10.8969, 13.8195),
    (11.4642, 12.8866),
    (12.1533, 12.0396),
    (13.3866, 10.9642),
    (14.3195, 10.3969),
    (15.3210, 9.9619),
    (16.9107, 9.5745),
    (20.0176, 9.4319),
    (20.7175, 9.0867),
    (21.0867, 8.7175),
    (21.4319, 8.0176),
    (21.5000, 7.5000),
    (21.5000, -5.5000),
    (21.3735, -6.1360),
    (21.0867, -6.7175),
    (20.4170, -7.2602),
    (19.5842, -7.4832),
    (11.2250, -7.5000),
    (10.3914, -8.6180),
    (9.4469, -9.6439),
    (8.4016, -10.5670),
    (6.6694, -11.7375),
    (5.4230, -12.3629),
    (3.4492, -13.0519),
    (2.0843, -13.3381),
    (0.0000, -13.5000),
    (-2.0843, -13.3381),
    (-3.4492, -13.0519),
    (-5.4230, -12.3629),
    (-6.6694, -11.7375),
    (-8.4016, -10.5670),
    (-9.4469, -9.6439),
    (-10.3914, -8.6180),
    (-11.2250, -7.5000),
    (-19.5842, -7.4832),
    (-20.4170, -7.2602),
    (-21.0867, -6.7175),
    (-21.3735, -6.1360),
    (-21.5000, -5.5000),
    (-21.5000, 7.5000),
    (-21.4319, 8.0176),
    (-21.0867, 8.7175),
    (-20.7175, 9.0867),
    (-20.0176, 9.4319),
    (-16.9107, 9.5745),
    (-15.3210, 9.9619),
    (-14.3195, 10.3969),
    (-13.3866, 10.9642),
    (-12.1533, 12.0396),
    (-11.4642, 12.8866),
    (-10.8969, 13.8195),
    (-10.2967, 15.3416),
    (-10.0187, 16.9541),
    (-9.9829, 20.7611),
    (-9.8478, 21.2654),
    (-9.5867, 21.7175),
    (-9.0000, 22.2320),
    (-8.5176, 22.4319),
    (-8.0000, 22.5000),
]

SLOT = [
    (2.5385, -29.5092),
    (-2.5385, -29.5092),
    (-3.2260, -29.6452),
    (-3.8644, -29.9378),
    (-4.7244, -30.7276),
    (-5.4220, -32.1490),
    (-5.8119, -32.6675),
    (-6.3049, -33.0906),
    (-6.8770, -33.3975),
    (-9.8013, -32.1960),
    (-11.1912, -31.4409),
    (-12.3652, -30.6244),
    (-12.9279, -29.8462),
    (-13.1529, -29.2452),
    (-13.2395, -28.2887),
    (-13.1261, -27.6571),
    (-12.7122, -26.7905),
    (-12.0457, -26.0991),
    (-11.1949, -25.6537),
    (-10.2470, -25.5000),
    (-10.2298, -21.2389),
    (-9.9790, -20.5000),
    (-9.6612, -20.0858),
    (-9.0123, -19.6522),
    (-8.2470, -19.5000),
    (8.2470, -19.5000),
    (9.0123, -19.6522),
    (9.6612, -20.0858),
    (9.9790, -20.5000),
    (10.2298, -21.2389),
    (10.2470, -25.5000),
    (11.1949, -25.6537),
    (12.0457, -26.0991),
    (12.7122, -26.7905),
    (13.1261, -27.6571),
    (13.2395, -28.2887),
    (13.1529, -29.2452),
    (12.9279, -29.8462),
    (12.3652, -30.6244),
    (11.1912, -31.4409),
    (9.8013, -32.1960),
    (6.8770, -33.3975),
    (6.3049, -33.0906),
    (5.8119, -32.6675),
    (5.4220, -32.1490),
    (4.7244, -30.7276),
    (3.8644, -29.9378),
    (3.2260, -29.6452),
]


def face_of(pts):
    return make_face(Polyline(*pts, close=True))


outline_pts = scale_outline(OUTLINE)
window_pts = scale_window(WINDOW)
slot_pts = scale_slot(SLOT)
outline = face_of(outline_pts)
underside = mountTopZ - plateThickness

plate = extrude(Pos(0, 0, underside) * outline, amount=plateThickness)
cut_top = mountTopZ + 0.08
cut_depth = -(plateThickness + 0.2)
window_tool = extrude(Pos(0, 0, cut_top) * face_of(window_pts), amount=cut_depth)
slot_tool = extrude(Pos(0, 0, cut_top) * face_of(slot_pts), amount=cut_depth)
# Parameter-driven cores of the window, strictly inside the blended opening.
wide_tool = Pos(
    0,
    (windowWideYMin + windowWideYMax) / 2.0,
    mountTopZ - plateThickness / 2.0,
) * Box(
    2 * windowHalfWidth - 6.0,
    windowWideYMax - windowWideYMin - 4.0,
    plateThickness + 0.2,
)
neck_tool = Pos(
    0,
    (windowWideYMax + windowNeckYMax) / 2.0,
    mountTopZ - plateThickness / 2.0,
) * Box(
    2 * windowNeckHalfWidth - 4.0,
    windowNeckYMax - windowWideYMax - 2.0,
    plateThickness + 0.2,
)
half_pitch = holeSpacing / 2.0
hole_r = holeDiameter / 2.0
hole_tools = [
    Pos(sx, sy, mountTopZ - plateThickness / 2.0) * Cylinder(hole_r, plateThickness + 0.2)
    for sx in (half_pitch, -half_pitch)
    for sy in (half_pitch, -half_pitch)
]
plate = plate - Compound(children=[window_tool, slot_tool, wide_tool, neck_tool, *hole_tools])

# Original source ring stations, kept in their original datum. Each row is
# z, tip radius, shoulder blend centre/radius, side scallop centre/radius,
# and the end of the side opening. Lofting homologous arcs preserves draft.
ringStations = [
    (-21.0, 23.174, 21.355, 32.919, 6.299, 30.399, 15.767, 7.381, 16.0),
    (-19.566, 23.307, 20.963, 33.324, 6.165, 30.370, 15.281, 7.170, 15.605),
    (-16.434, 23.569, 20.291, 34.116, 6.007, 30.439, 14.464, 6.921, 14.906),
    (-13.408, 23.780, 19.841, 34.657, 5.894, 30.562, 14.010, 6.811, 14.498),
    (-12.010, 23.859, 19.700, 34.837, 5.852, 30.616, 13.909, 6.778, 14.254),
    (-10.695, 23.931, 19.630, 35.027, 5.882, 30.679, 13.871, 6.769, 13.546),
    (-9.600, 23.980, 19.571, 35.097, 5.843, 30.737, 13.877, 6.776, 12.3023),
    (-9.010, 24.007, 19.537, 35.094, 5.791, 30.767, 13.897, 6.781, 10.6448),
    (-8.480, 24.030, 19.538, 35.140, 5.806, 30.809, 13.922, 6.803, 9.4),
    (-7.180, 24.074, 19.581, 35.273, 5.893, 30.859, 14.022, 6.811, 9.4),
]
endCentreY = 12.583
sideCentreY = 12.5


def circle_intersections(c1, r1, c2, r2):
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = sqrt(dx * dx + dy * dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = sqrt(max(0.0, r1 * r1 - a * a))
    x, y = c1[0] + a * dx / d, c1[1] + a * dy / d
    return [(x - h * dy / d, y + h * dx / d), (x + h * dy / d, y - h * dx / d)]


def arc_between(c, a, b):
    aa, ab = atan2(a[1] - c[1], a[0] - c[0]), atan2(b[1] - c[1], b[0] - c[0])
    delta = (ab - aa + pi) % (2 * pi) - pi
    r = sqrt((a[0] - c[0]) ** 2 + (a[1] - c[1]) ** 2)
    mid = (c[0] + r * cos(aa + delta / 2), c[1] + r * sin(aa + delta / 2))
    return ThreePointArc(a, mid, b)


def ring_section(row, negative=False):
    z, tip, bx, by, br, sx, sy, sr, cut = row
    scale = bodyWidth / 50.0
    # Enforce tangency to the tip circle after fitting the shoulder arc.
    d = sqrt(bx * bx + (by - endCentreY) ** 2)
    bc = (bx * (tip + br) / d, endCentreY + (by - endCentreY) * (tip + br) / d)
    ec, sc, side = (0, endCentreY), (sx, sy), (0, sideCentreY)
    cut += 0.166 if negative else 0.0
    edges = []
    paths = []
    for t in (0.0, wallThickness):
        rr, er, blendr, scallopr = 25.0 - t, tip - t, br + t, sr + t

        def scallop_x(y, scallopr=scallopr, t=t):
            if y >= 13.5:
                return sx - sqrt(scallopr**2 - (y - sy) ** 2)
            d = 13.5 - y
            slope = 0.028 * d + 0.0225 * d * d
            return sx - sr + 0.014 * d * d + 0.0075 * d * d * d - t * sqrt(1 + slope * slope)

        start = (scallop_x(cut), cut)
        join = max(circle_intersections(side, rr, sc, scallopr), key=lambda q: q[1])
        shoulder = max(circle_intersections(side, rr, bc, blendr), key=lambda q: q[0])
        tangent = (bc[0] * er / (tip + br), endCentreY + (bc[1] - endCentreY) * er / (tip + br))
        end = (0.0, endCentreY + er)
        paths.append(
            (
                start,
                end,
                [
                    Spline(
                        *[(scallop_x(cut + (join[1] - cut) * i / 8), cut + (join[1] - cut) * i / 8) for i in range(9)]
                    ),
                    arc_between(side, join, shoulder),
                    arc_between(bc, shoulder, tangent),
                    arc_between(ec, tangent, end),
                ],
            )
        )
    edges.extend(paths[0][2])
    edges.append(Polyline(paths[0][1], paths[1][1]))
    edges.extend([e.reversed() for e in reversed(paths[1][2])])
    edges.append(Polyline(paths[1][0], paths[0][0]))
    f = Face(Wire([e for curve in edges for e in curve.edges()]))
    if negative:
        f = Pos(0, 0.166, 0) * mirror(f, Plane.XZ)
    # Contract width remains the driver for every ring station.
    f = f.scale(scale)
    # ringBottomZ is a selective trim parameter, not a station translation.
    return Pos(0, 0, z) * f


def station_loft(sections):
    # Consecutive station pairs avoid a global interpolation folding back
    # across the short opening caps when the section perimeter changes.
    spans = [loft(sections[i : i + 2], ruled=False) for i in range(len(sections) - 1)]
    shape = spans[0]
    for span in spans[1:]:
        shape = shape + span
    return shape


quarters = []
for negative in (False, True):
    quarter = station_loft([ring_section(row, negative) for row in ringStations])
    quarters.extend([quarter, mirror(quarter, Plane.YZ)])
wall = quarters[0] + quarters[1] + quarters[2] + quarters[3]
# The thin side bridge is present only above the side opening.
bridge = extrude(
    Pos(0, 0, sideLandBottomZ) * (outline - offset(outline, amount=-wallThickness)),
    amount=underside - sideLandBottomZ + 0.02,
)
bridge &= Pos(0, 0, -8.0) * Box(bodyWidth + 2, 28.0, 4.0)
wall += bridge
# Side apertures run along 45-degree lines through the ring, with a
# rounded lower corner. Their planes are measured from the source mesh.
windowZTop = -7.2067
windowZBottom = -12.0067
# Local coordinates are tangent to the circular band and vertical.
hw = 5.0
cr = 1.5
windowProfile = make_face(
    [
        Polyline((-hw, windowZTop), (-hw, windowZBottom + cr)),
        ThreePointArc(
            (-hw, windowZBottom + cr),
            (-hw + cr - cr / sqrt(2), windowZBottom + cr - cr / sqrt(2)),
            (-hw + cr, windowZBottom),
        ),
        Polyline((-hw + cr, windowZBottom), (hw - cr, windowZBottom)),
        ThreePointArc(
            (hw - cr, windowZBottom),
            (hw - cr + cr / sqrt(2), windowZBottom + cr - cr / sqrt(2)),
            (hw, windowZBottom + cr),
        ),
        Polyline((hw, windowZBottom + cr), (hw, windowZTop), (-hw, windowZTop)),
    ]
)
wp = Plane(origin=(0, 0.083, 0), x_dir=(-1 / sqrt(2), 1 / sqrt(2), 0), z_dir=(1 / sqrt(2), 1 / sqrt(2), 0))
w = extrude(wp * windowProfile, amount=42)
windows = [w, mirror(w, Plane.YZ)]
windows.extend([Pos(0, 0.166, 0) * mirror(v, Plane.XZ) for v in windows[:]])
wall -= Compound(children=windows)
# ringBottomZ only controls this local trim; source loft stations never move.
ring_trim_bottom = ringStations[0][0] - 0.05
ring_trim = Pos(0, 0, (ring_trim_bottom + ringBottomZ) / 2) * Box(
    bodyWidth + 0.1, bodyYMax - bodyYMin + 0.1, ringBottomZ - ring_trim_bottom
)
wall -= ring_trim


# End supports are lofted through the changing sections below the bore.
# The five ordinates describe the smooth inner crescent at x=0,2,4,6,8;
# the outer edge lies inside the wall so it fuses without changing its skin.
negativeSupportStations = [
    (-16.434, 23.569, (34.786, 34.695, 34.423, 33.960, 33.303)),
    (-15.0, 23.675, (34.638, 34.632, 34.507, 34.075, 33.418)),
    (-14.0, 23.744, (34.046, 34.179, 34.326, 34.138, 33.488)),
    (-13.4, 23.780, (33.309, 33.657, 34.087, 34.109, 33.530)),
    (-13.0, 23.807, (32.034, 33.109, 33.865, 34.055, 33.558)),
    (-12.5, 23.836, (30.788, 31.591, 33.511, 33.953, 33.592)),
    (-12.0, 23.865, (30.232, 30.698, 33.048, 33.819, 33.620)),
    (-11.5, 23.894, (29.93, 30.219, 32.419, 33.662, 33.631)),
    (-10.7, 23.931, (29.715, 29.775, 31.029, 33.379, 33.616)),
    (-9.5, 23.985, (29.5, 29.518, 30.256, 32.987, 33.574)),
    (-8.2, 24.043, (29.5, 29.5, 30.021, 32.811, 33.575)),
    (-7.18, 24.074, (29.5, 29.5, 30.028, 32.847, 33.614)),
]


def ordered_face(curves):
    return Face(Wire([e for curve in curves for e in curve.edges()]))


def support_section(z, tip, ordinates, negative):
    cy = endCentreY - (0.166 if negative else 0.0)
    inner_r, outer_r = tip - wallThickness, tip - 0.35
    # Extra width ensures that the support closes into the undisturbed ring.
    inner_end = (10.0, cy + sqrt(inner_r**2 - 100) + 0.08)
    pts = [
        (i * 2.0, y if z > -16 else cy + sqrt(inner_r**2 - (i * 2.0) ** 2) + 0.10) for i, y in enumerate(ordinates)
    ] + [inner_end]
    # Mirror the interpolation controls about the datum for a horizontal
    # tangent at the bore centreline, then keep the positive half.
    inn = Spline(*pts, tangents=[(1, 0), (1, -10 / sqrt(inner_r**2 - 100))])
    out_end = (10.0, cy + sqrt(outer_r**2 - 100))
    out_axis = (0, cy + outer_r)
    f = ordered_face(
        [inn, Polyline(inner_end, out_end), arc_between((0, cy), out_end, out_axis), Polyline(out_axis, pts[0])]
    )
    if negative:
        f = mirror(f, Plane.XZ)
    return Pos(0, 0, z) * f


boss_half = station_loft([support_section(z, r, ys, True) for z, r, ys in negativeSupportStations])
# These crescent tails follow the old deep ring below the retained boss.
# Trim the support alone at the specified boss limit, never the assembled part.
support_trim_bottom = negativeSupportStations[0][0] - 0.05
support_trim = Pos(0, 0, (support_trim_bottom + blockBottomZ) / 2) * Box(
    bodyWidth + 0.1, bodyYMax - bodyYMin + 0.1, blockBottomZ - support_trim_bottom
)
boss_half -= support_trim
boss = boss_half + mirror(boss_half, Plane.YZ)
# The channel cap's one-millimetre transition follows the measured top
# station; its lower rectangle retains the contract's interface dimensions.
block_rect = extrude(
    Pos(0, 0, blockBottomZ)
    * face_of([(-tabWidth / 2, tabYMin), (tabWidth / 2, tabYMin), (tabWidth / 2, tabYMax), (-tabWidth / 2, tabYMax)]),
    amount=-8.2 - blockBottomZ,
)
cap = loft(
    [
        Pos(0, 0, z) * face_of([(-w, y0), (w, y0), (w, tabYMax), (-w, tabYMax)])
        for z, w, y0 in [(-8.2, tabWidth / 2, tabYMin), (-7.18, tabWidth / 2 + 1, tabYMin - 1)]
    ]
)
block = block_rect + cap
positiveSupportStations = [
    (-16.434, 23.569, (34.95, 34.857, 34.585, 34.126, 33.469)),
    (-15.0, 23.675, (35.049, 34.969, 34.696, 34.237, 33.584)),
    (-14.0, 23.744, (34.785, 34.847, 34.762, 34.307, 33.654)),
    (-13.4, 23.780, (34.254, 34.515, 34.715, 34.348, 33.696)),
    (-13.0, 23.807, (33.08, 34.10, 34.62, 34.38, 33.72)),
]
# Below the channel cap the support rounds back into the rim.
pos_lower_half = station_loft([support_section(z, r, ys, False) for z, r, ys in positiveSupportStations])
pos_lower_half -= support_trim


# Above z=-13 the narrow throat grows along a curved XZ profile.
def positive_section(z, tip, width):
    cy = endCentreY
    ri, ro = tip - wallThickness, tip - 0.35
    fillet_r = 2.0
    cc = (width + fillet_r, cy + sqrt((ri - fillet_r) ** 2 - (width + fillet_r) ** 2))
    a = (width, cc[1])
    b = (cc[0] * ri / (ri - fillet_r), cy + (cc[1] - cy) * ri / (ri - fillet_r))
    end = (10, cy + sqrt(ri * ri - 100))
    oe = (10, cy + sqrt(ro * ro - 100))
    oa = (0, cy + ro)
    f = ordered_face(
        [
            Polyline((0, tabYMax - 0.02), (width, tabYMax - 0.02), a),
            arc_between(cc, a, b),
            arc_between((0, cy), b, end),
            Polyline(end, oe),
            arc_between((0, cy), oe, oa),
            Polyline(oa, (0, tabYMax - 0.02)),
        ]
    )
    return Pos(0, 0, z) * f


pos_upper_half = station_loft(
    [
        positive_section(z, r, w)
        for z, r, w in [
            (-13.0, 23.807, 0.85),
            (-12.8, 23.819, 1.46),
            (-12.0, 23.865, 2.97),
            (-10.695, 23.931, 4.21),
            (-9.5, 23.985, 4.81),
            (-8.2, 24.043, 5.05),
            (-7.6, 24.062, 5.43),
            (-7.18, 24.074, 6.77),
        ]
    ],
)
supportClip = Pos(0, 0, -16) * Box(16, 100, 30)
block = block_rect + cap
result = plate + wall + boss + block
for part in [pos_lower_half & supportClip, pos_upper_half & supportClip]:
    result = result + part + mirror(part, Plane.YZ)

bore = Pos(0, 0, crossBoreZ) * Cylinder(
    crossBoreDiameter / 2.0,
    bodyYMax - bodyYMin + 8.0,
    rotation=(90, 0, 0),
)
result = result - bore

assert len(result.solids()) == 1, "infeasible: feature groups must form one connected mount"

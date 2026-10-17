from build123d import (
    Align,
    Box,
    BuildLine,
    CenterArc,
    Circle,
    Line,
    Pos,
    RectangleRounded,
    extrude,
    make_face,
)

pcbLength = 69.6
pcbWidth = 45.0
pcbThickness = 1.2
cornerRadius = 0.6
keyNotchX = 38.3
keyNotchWidth = 1.0
keyNotchDepth = 3.5
keyNotchEndRadius = keyNotchWidth / 2
keyNotchEntryRadius = 0.25
sideNotchDepth = 1.75
sideNotchYMin = 18.0
sideNotchYMax = 22.0
sideNotchCornerRadius = 0.65
heatsinkHoleDiameter = 3.2
heatsinkPatternX = 43.2
heatsinkPatternY = 28.8
heatsinkPatternCx = 34.8
heatsinkPatternCy = 24.81
mountHoleDiameter = 2.75
mountHoleX = 3.0
mountHoleY = 42.0
smallHoleDiameter = 1.8
smallHoleX = 2.0
smallHoleY = 6.0
socXMin = 23.7
socXMax = 45.9
socYMin = 14.7
socYMax = 34.9
socTop = 3.83

assert pcbThickness > 0.0, "infeasible: pcbThickness must be positive"
assert socTop > pcbThickness, "infeasible: socTop must exceed pcbThickness"
assert sideNotchCornerRadius < sideNotchDepth <= 10.0, (
    "infeasible: sideNotchDepth must exceed sideNotchCornerRadius and be at most 10"
)
assert sideNotchYMax - sideNotchYMin > 2.0 * sideNotchCornerRadius, (
    "infeasible: side notch span must clear both inner corner radii"
)
assert keyNotchDepth > keyNotchEntryRadius, "infeasible: key notch shorter than its entry radius"
assert keyNotchDepth + keyNotchEndRadius < pcbWidth, "infeasible: key notch leaves the board"
assert cornerRadius > 0.0, "infeasible: cornerRadius must be positive"
assert 2.0 * cornerRadius < pcbLength and 2.0 * cornerRadius < pcbWidth, (
    "infeasible: cornerRadius does not fit the outline"
)
assert keyNotchWidth > 0.0 and keyNotchEndRadius > 0.0, "infeasible: key notch width"
assert heatsinkHoleDiameter > 0.0, "infeasible: heatsink hole diameter"
assert mountHoleDiameter > 0.0, "infeasible: mount hole diameter"
assert smallHoleDiameter > 0.0, "infeasible: small hole diameter"
assert socXMax > socXMin and socYMax > socYMin, "infeasible: SoC lid extent"

# Cut profiles overrun the outline so the boolean crosses the edge instead of kissing it.
_EDGE = 0.05


def _key_notch():
    half = keyNotchWidth / 2
    entry = keyNotchEntryRadius
    mouth_left = keyNotchX - half - entry
    mouth_right = keyNotchX + half + entry
    with BuildLine() as profile:
        left_arc = CenterArc((mouth_left, entry), entry, -90, 90)
        Line(left_arc @ 1, (keyNotchX - half, keyNotchDepth))
        cap = CenterArc((keyNotchX, keyNotchDepth), keyNotchEndRadius, 180, -180)
        Line(cap @ 1, (keyNotchX + half, entry))
        right_arc = CenterArc((mouth_right, entry), entry, 180, 90)
        Line(right_arc @ 1, (mouth_right, -_EDGE))
        Line((mouth_right, -_EDGE), (mouth_left, -_EDGE))
        Line((mouth_left, -_EDGE), left_arc @ 0)
    return make_face(profile.wire())


def _side_notch(on_left):
    radius = sideNotchCornerRadius
    y0 = sideNotchYMin
    y1 = sideNotchYMax
    if on_left:
        outer = -_EDGE
        floor = sideNotchDepth
        lower = (floor - radius, y0 + radius)
        upper = (floor - radius, y1 - radius)
        with BuildLine() as profile:
            start = Line((outer, y0), (floor - radius, y0))
            lower_arc = CenterArc(lower, radius, -90, 90)
            Line(lower_arc @ 1, (floor, y1 - radius))
            upper_arc = CenterArc(upper, radius, 0, 90)
            end = Line(upper_arc @ 1, (outer, y1))
            Line(end @ 1, start @ 0)
    else:
        outer = pcbLength + _EDGE
        floor = pcbLength - sideNotchDepth
        lower = (floor + radius, y0 + radius)
        upper = (floor + radius, y1 - radius)
        with BuildLine() as profile:
            start = Line((outer, y0), (floor + radius, y0))
            lower_arc = CenterArc(lower, radius, -90, -90)
            Line(lower_arc @ 1, (floor, y1 - radius))
            upper_arc = CenterArc(upper, radius, 180, -90)
            end = Line(upper_arc @ 1, (outer, y1))
            Line(end @ 1, start @ 0)
    return make_face(profile.wire())


def _holes():
    half_x = heatsinkPatternX / 2
    half_y = heatsinkPatternY / 2
    centers = [
        (
            heatsinkPatternCx + sx * half_x,
            heatsinkPatternCy + sy * half_y,
            heatsinkHoleDiameter,
        )
        for sx in (-1.0, 1.0)
        for sy in (-1.0, 1.0)
    ]
    centers += [
        (mountHoleX, mountHoleY, mountHoleDiameter),
        (pcbLength - mountHoleX, mountHoleY, mountHoleDiameter),
        (smallHoleX, smallHoleY, smallHoleDiameter),
        (pcbLength - smallHoleX, smallHoleY, smallHoleDiameter),
    ]
    sketch = None
    for x, y, diameter in centers:
        circle = Pos(x, y) * Circle(diameter / 2)
        sketch = circle if sketch is None else sketch + circle
    return sketch


outline = RectangleRounded(pcbLength, pcbWidth, cornerRadius, align=(Align.MIN, Align.MIN))
board = outline - _key_notch() - _side_notch(True) - _side_notch(False) - _holes()
pcb = extrude(board, pcbThickness)
lid = Pos(socXMin, socYMin, pcbThickness) * Box(
    socXMax - socXMin,
    socYMax - socYMin,
    socTop - pcbThickness,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
result = pcb + lid

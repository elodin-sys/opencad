import math

from build123d import Bezier, Pos, extrude, make_face

padBaseZ = 13.0
padThickness = 6.5
outerApexY = 135.0
outerCtrlAx = 20.0
outerCtrlAy = 135.0
outerCtrlBx = 50.0
outerCtrlBy = 130.0
outerCtrlBWeight = 2.5
cornerX = 40.0
cornerY = 105.0
innerCtrlAx = 30.0
innerCtrlAy = 80.0
innerCtrlBx = 35.0
innerCtrlBy = 90.0
innerApexY = 90.0

assert padThickness > 0, "infeasible: padThickness must be positive"
assert outerCtrlBWeight > 0, "infeasible: outerCtrlBWeight must be positive"

# One rational cubic under-integrates at 1e-7; equal-parameter splits are the same curve.
_OUTER_SPANS = 8


def _split_rational(poles, weights, t):
    degree = len(poles) - 1
    hom = [[weights[i] * poles[i][0], weights[i] * poles[i][1], weights[i]] for i in range(degree + 1)]
    pyramid = [hom]
    for _ in range(degree):
        prev = pyramid[-1]
        pyramid.append([[(1 - t) * prev[i][k] + t * prev[i + 1][k] for k in range(3)] for i in range(len(prev) - 1)])
    left = [pyramid[r][0] for r in range(degree + 1)]
    right = [pyramid[r][-1] for r in range(degree, -1, -1)]

    def dehom(rows):
        points, span_weights = [], []
        for x, y, weight in rows:
            points.append((x / weight, y / weight))
            span_weights.append(weight)
        return points, span_weights

    return dehom(left), dehom(right)


def _rational_spans(poles, weights, spans):
    pieces = [(list(poles), list(weights))]
    for _ in range(int(math.log2(spans))):
        nxt = []
        for points, span_weights in pieces:
            left, right = _split_rational(points, span_weights, 0.5)
            nxt.extend((left, right))
        pieces = nxt
    return [Bezier(*points, weights=tuple(span_weights)) for points, span_weights in pieces]


outer_right = _rational_spans(
    ((0, outerApexY), (outerCtrlAx, outerCtrlAy), (outerCtrlBx, outerCtrlBy), (cornerX, cornerY)),
    (1, 1, outerCtrlBWeight, 1),
    _OUTER_SPANS,
)
inner_right = Bezier(
    (cornerX, cornerY),
    (innerCtrlAx, innerCtrlAy),
    (innerCtrlBx, innerCtrlBy),
    (0, innerApexY),
)
inner_left = Bezier(
    (0, innerApexY),
    (-innerCtrlBx, innerCtrlBy),
    (-innerCtrlAx, innerCtrlAy),
    (-cornerX, cornerY),
)
outer_left = _rational_spans(
    ((-cornerX, cornerY), (-outerCtrlBx, outerCtrlBy), (-outerCtrlAx, outerCtrlAy), (0, outerApexY)),
    (1, outerCtrlBWeight, 1, 1),
    _OUTER_SPANS,
)

profile = make_face([*outer_right, inner_right, inner_left, *outer_left])
result = Pos(0, 0, padBaseZ) * extrude(profile, amount=padThickness)

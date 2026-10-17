import math

from build123d import Align, BuildLine, CenterArc, Cylinder, Polyline, Pos, extrude, make_face

toothCount = 40
gearModule = 2.0
pressureAngle = 20.0
profileShift = 0.0
addendumCoef = 1.0
dedendumCoef = 1.25
faceWidth = 8.0
boreDiameter = 8.0
toothThinning = 0.05
flankPoints = 14
pitchRadius = gearModule * toothCount / 2
baseRadius = pitchRadius * math.cos(math.radians(pressureAngle))
tipRadius = pitchRadius + (addendumCoef + profileShift) * gearModule
rootRadius = pitchRadius - (dedendumCoef - profileShift) * gearModule
toothThickness = gearModule * (math.pi / 2 + 2 * profileShift * math.tan(math.radians(pressureAngle))) - toothThinning

assert toothCount > 0, "infeasible: toothCount must be positive"
assert faceWidth > 0, "infeasible: faceWidth must be positive"
assert flankPoints >= 2, "infeasible: flankPoints needs a base point and a tip point"
assert tipRadius > baseRadius > rootRadius > boreDiameter / 2 > 0, "infeasible: radii out of order"

pressure = math.radians(pressureAngle)


def inv(alpha):
    return math.tan(alpha) - alpha


psi_pitch = toothThickness / (2.0 * pitchRadius)
psi_base = psi_pitch + inv(pressure)
alpha_tip = math.acos(baseRadius / tipRadius)
psi_tip = psi_base - inv(alpha_tip)
t_tip = math.tan(alpha_tip)
root_gap = 2.0 * math.pi / toothCount - 2.0 * psi_base

assert psi_tip > 0, "infeasible: tip land would be negative"
assert root_gap > 0, "infeasible: adjacent teeth overlap at the root"

n_teeth = int(toothCount)
n_flank = int(flankPoints)


def rotate(x, y, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (x * c - y * s, x * s + y * c)


def involute_xy(roll):
    return (
        baseRadius * (math.cos(roll) + roll * math.sin(roll)),
        baseRadius * (math.sin(roll) - roll * math.cos(roll)),
    )


def flank_point(roll, side):
    # Positive side is the involute mirrored across the tooth centreline.
    x0, y0 = involute_xy(roll)
    if side < 0:
        return rotate(x0, y0, -psi_base)
    return rotate(x0, -y0, psi_base)


cw0 = [flank_point(t_tip * i / (n_flank - 1), -1) for i in range(n_flank)]
ccw0 = [flank_point(t_tip * i / (n_flank - 1), 1) for i in range(n_flank)]

with BuildLine() as outline:
    for i in range(n_teeth):
        theta = i * 2.0 * math.pi / n_teeth
        cw = [rotate(p[0], p[1], theta) for p in cw0]
        ccw = [rotate(p[0], p[1], theta) for p in ccw0]
        root_cw = (cw[0][0] * rootRadius / baseRadius, cw[0][1] * rootRadius / baseRadius)
        root_ccw = (ccw[0][0] * rootRadius / baseRadius, ccw[0][1] * rootRadius / baseRadius)
        Polyline(root_cw, *cw)
        a0 = math.atan2(cw[-1][1], cw[-1][0])
        a1 = math.atan2(ccw[-1][1], ccw[-1][0])
        CenterArc((0, 0), tipRadius, math.degrees(a0), math.degrees((a1 - a0) % (2.0 * math.pi)))
        Polyline(ccw[-1], *list(reversed(ccw[:-1])), root_ccw)
        theta_n = ((i + 1) % n_teeth) * 2.0 * math.pi / n_teeth
        cw_n = rotate(cw0[0][0], cw0[0][1], theta_n)
        root_next = (cw_n[0] * rootRadius / baseRadius, cw_n[1] * rootRadius / baseRadius)
        b0 = math.atan2(root_ccw[1], root_ccw[0])
        b1 = math.atan2(root_next[1], root_next[0])
        CenterArc((0, 0), rootRadius, math.degrees(b0), math.degrees((b1 - b0) % (2.0 * math.pi)))

gear = extrude(make_face(outline.edges()), amount=faceWidth)
bore = Pos(0, 0, -0.02) * Cylinder(boreDiameter / 2, faceWidth + 0.04, align=(Align.CENTER, Align.CENTER, Align.MIN))
result = gear - bore

import math

import FreeCAD
import Part
import Sketcher

gearModule = 2.0
pressureAngle = 20.0
profileShift = 0.0
pinionTeeth = 20.0
wheelTeeth = 40.0
pinionBoreDiameter = 6.0
wheelBoreDiameter = 8.0
centerDistance = 60.0
gearFaceWidth = 8.0
addendumFactor = 1.0
dedendumFactor = 1.25
totalBacklash = 0.1
pinionPhase = 0.0
pinionAxisX = 0.0
pinionAxisY = 0.0
wheelAxisY = 0.0
gearBaseZ = 0.0
carrierLength = 110.0
carrierWidth = 50.0
carrierThickness = 5.0
carrierMinX = -25.0
carrierMinY = -25.0
wheelPhase = 4.5

assert gearModule > 0, "infeasible: gearModule must be positive"
assert 0 < pressureAngle < 90, "infeasible: pressureAngle must stay in (0, 90)"
assert pinionTeeth >= 3, "infeasible: pinionTeeth must be at least 3"
assert wheelTeeth >= 3, "infeasible: wheelTeeth must be at least 3"
assert abs(pinionTeeth - round(pinionTeeth)) < 1e-6, "infeasible: pinionTeeth must be an integer"
assert abs(wheelTeeth - round(wheelTeeth)) < 1e-6, "infeasible: wheelTeeth must be an integer"
assert pinionBoreDiameter > 0, "infeasible: pinionBoreDiameter must be positive"
assert wheelBoreDiameter > 0, "infeasible: wheelBoreDiameter must be positive"
assert centerDistance > 0, "infeasible: centerDistance must be positive"
assert gearFaceWidth > 0, "infeasible: gearFaceWidth must be positive"
assert addendumFactor + profileShift > 0, "infeasible: effective addendum must be positive"
assert dedendumFactor - profileShift > 0, "infeasible: effective dedendum must be positive"
assert carrierLength > 0, "infeasible: carrierLength must be positive"
assert carrierWidth > 0, "infeasible: carrierWidth must be positive"
assert carrierThickness > 0, "infeasible: carrierThickness must be positive"
assert totalBacklash >= 0, "infeasible: totalBacklash must be nonnegative"
assert -360 < pinionPhase < 360, "infeasible: pinionPhase is out of range"
assert -360 < wheelPhase < 360, "infeasible: wheelPhase is out of range"

alpha = math.radians(pressureAngle)
tooth_thickness = math.pi * gearModule / 2.0 + 2.0 * gearModule * profileShift * math.tan(alpha) - totalBacklash / 2.0
assert tooth_thickness > 0, "infeasible: totalBacklash leaves no tooth thickness"
wheel_axis_x = pinionAxisX + centerDistance


def gear_data(n_teeth, bore):
    n = round(n_teeth)
    pitch = gearModule * n_teeth / 2.0
    base = pitch * math.cos(alpha)
    tip = pitch + gearModule * (addendumFactor + profileShift)
    root = pitch - gearModule * (dedendumFactor - profileShift)
    assert base > 0, "infeasible: base radius must be positive"
    assert root > bore / 2.0, "infeasible: bore must leave a positive root web"
    assert root < pitch < tip, "infeasible: root, pitch and tip are not ordered"
    assert tip > base, "infeasible: tip does not clear the base circle"
    h0 = tooth_thickness / (2.0 * pitch) + math.tan(alpha) - alpha
    t_root = math.sqrt(max(0.0, (root / base) ** 2 - 1.0))
    t_pitch = math.tan(alpha)
    t_tip = math.sqrt((tip / base) ** 2 - 1.0)
    h_root = h0 - t_root + math.atan(t_root)
    h_tip = h0 - t_tip + math.atan(t_tip)
    assert h_tip > 0, "infeasible: backlash or shift erased the tooth tip"
    assert h_root < math.pi / n, "infeasible: tooth root closes the adjacent tooth space"
    assert t_pitch - t_root > 1e-8, "infeasible: root-to-pitch fitting interval is degenerate"
    assert t_tip - t_pitch > 1e-8, "infeasible: pitch-to-tip fitting interval is degenerate"
    return {
        "n": n,
        "pitch": pitch,
        "base": base,
        "tip": tip,
        "root": root,
        "h0": h0,
        "t_root": t_root,
        "t_pitch": t_pitch,
        "t_tip": t_tip,
        "h_root": h_root,
    }


pinion_g = gear_data(pinionTeeth, pinionBoreDiameter)
wheel_g = gear_data(wheelTeeth, wheelBoreDiameter)

fit_tol = 0.001
for ax, ay, rad in (
    (pinionAxisX, pinionAxisY, pinionBoreDiameter / 2.0),
    (wheel_axis_x, wheelAxisY, wheelBoreDiameter / 2.0),
):
    assert ax - rad > carrierMinX, "infeasible: hole breaks carrier left wall"
    assert ax + rad < carrierMinX + carrierLength, "infeasible: hole breaks carrier right wall"
    assert ay - rad > carrierMinY, "infeasible: hole breaks carrier front wall"
    assert ay + rad < carrierMinY + carrierWidth, "infeasible: hole breaks carrier back wall"
shaft = math.hypot(centerDistance, wheelAxisY - pinionAxisY)
assert shaft > (pinionBoreDiameter + wheelBoreDiameter) / 2.0, "infeasible: carrier holes overlap"
assert gearBaseZ - carrierThickness < gearBaseZ, "infeasible: carrier axial interval is empty"
assert gearBaseZ + gearFaceWidth > gearBaseZ, "infeasible: gear axial interval is empty"
assert shaft - pinion_g["tip"] - wheel_g["root"] > 2.0 * fit_tol, "infeasible: pinion tip collides with wheel root"
assert shaft - wheel_g["tip"] - pinion_g["root"] > 2.0 * fit_tol, "infeasible: wheel tip collides with pinion root"
assert shaft > pinion_g["base"] + wheel_g["base"], "infeasible: no real working pressure angle"
working = math.acos((pinion_g["base"] + wheel_g["base"]) / shaft)
path = (
    math.sqrt(pinion_g["tip"] ** 2 - pinion_g["base"] ** 2)
    + math.sqrt(wheel_g["tip"] ** 2 - wheel_g["base"] ** 2)
    - shaft * math.sin(working)
)
assert path / (math.pi * gearModule * math.cos(alpha)) > 1.0, "infeasible: contact ratio must exceed one"
working_inv = math.tan(working) - working
wp = shaft * pinionTeeth / (pinionTeeth + wheelTeeth)
ww = shaft * wheelTeeth / (pinionTeeth + wheelTeeth)
working_backlash = (
    2.0 * math.pi * wp / pinionTeeth
    - 2.0 * wp * (pinion_g["h0"] - working_inv)
    - 2.0 * ww * (wheel_g["h0"] - working_inv)
)
loc = math.atan2(wheelAxisY - pinionAxisY, centerDistance)
raw = (
    pinionTeeth * (math.radians(pinionPhase) - loc) + wheelTeeth * (math.radians(wheelPhase) - loc - math.pi) - math.pi
)
wrapped = raw - 2.0 * math.pi * round(raw / (2.0 * math.pi))
mesh_dist = abs(wrapped) * shaft / (pinionTeeth + wheelTeeth)
assert mesh_dist + 2.0 * fit_tol < working_backlash / 2.0, "infeasible: gear phases exceed available working backlash"


def origin_xy(body):
    return next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)


def new_body(name):
    body = doc.addObject("PartDesign::Body", name)
    body.AllowCompound = False
    doc.recompute()
    return body


def sketch_on(body, name, z):
    sk = body.newObject("Sketcher::SketchObject", name)
    sk.AttachmentSupport = [(origin_xy(body), "")]
    sk.MapMode = "FlatFace"
    sk.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, z), FreeCAD.Rotation())
    return sk


def add_xy_rect(sk, xmin, ymin, width, height):
    xmax = xmin + width
    ymax = ymin + height
    g0 = sk.addGeometry(Part.LineSegment(FreeCAD.Vector(xmin, ymin, 0), FreeCAD.Vector(xmax, ymin, 0)), False)
    g1 = sk.addGeometry(Part.LineSegment(FreeCAD.Vector(xmax, ymin, 0), FreeCAD.Vector(xmax, ymax, 0)), False)
    g2 = sk.addGeometry(Part.LineSegment(FreeCAD.Vector(xmax, ymax, 0), FreeCAD.Vector(xmin, ymax, 0)), False)
    g3 = sk.addGeometry(Part.LineSegment(FreeCAD.Vector(xmin, ymax, 0), FreeCAD.Vector(xmin, ymin, 0)), False)
    sk.addConstraint(Sketcher.Constraint("Coincident", g0, 2, g1, 1))
    sk.addConstraint(Sketcher.Constraint("Coincident", g1, 2, g2, 1))
    sk.addConstraint(Sketcher.Constraint("Coincident", g2, 2, g3, 1))
    sk.addConstraint(Sketcher.Constraint("Coincident", g3, 2, g0, 1))
    sk.addConstraint(Sketcher.Constraint("Horizontal", g0))
    sk.addConstraint(Sketcher.Constraint("Horizontal", g2))
    sk.addConstraint(Sketcher.Constraint("Vertical", g1))
    sk.addConstraint(Sketcher.Constraint("Vertical", g3))
    sk.addConstraint(Sketcher.Constraint("DistanceX", g0, 1, g0, 2, width))
    sk.addConstraint(Sketcher.Constraint("DistanceY", g0, 1, g3, 1, height))
    sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, g0, 1, xmin))
    sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, g0, 1, ymin))


def add_circle(sk, cx, cy, radius):
    gid = sk.addGeometry(Part.Circle(FreeCAD.Vector(cx, cy, 0), FreeCAD.Vector(0, 0, 1), radius), False)
    sk.addConstraint(Sketcher.Constraint("Radius", gid, radius))
    sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gid, 3, cx))
    sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gid, 3, cy))


def pad(body, name, sketch, length, refine=False):
    feat = body.newObject("PartDesign::Pad", name)
    feat.Profile = sketch
    feat.Length = length
    feat.Refine = refine
    doc.recompute()
    assert feat.Shape.isValid(), f"kernel: {name} is invalid after recompute"
    return feat


def vec(p):
    return FreeCAD.Vector(p[0], p[1], 0.0)


def polar(axis, radius, theta):
    return (axis[0] + radius * math.cos(theta), axis[1] + radius * math.sin(theta))


def edge_line(a, b):
    return Part.makeLine(vec(a), vec(b))


def edge_arc(a, mid, b):
    cr = (mid[0] - a[0]) * (b[1] - a[1]) - (mid[1] - a[1]) * (b[0] - a[0])
    if abs(cr) < 1e-12:
        return edge_line(a, b)
    return Part.Arc(vec(a), vec(mid), vec(b)).toShape()


def edge_center_arc(axis, radius, th0, th1):
    dt = th1 - th0
    while dt <= 0.0:
        dt += 2.0 * math.pi
    while dt >= 2.0 * math.pi:
        dt -= 2.0 * math.pi
    mid = th0 + 0.5 * dt
    return edge_arc(polar(axis, radius, th0), polar(axis, radius, mid), polar(axis, radius, th1))


def roll_samples(t_root, t_pitch, t_tip, n=12):
    ts = [t_root + (t_pitch - t_root) * i / n for i in range(n)]
    ts += [t_pitch + (t_tip - t_pitch) * i / n for i in range(n + 1)]
    return ts


def involute_xy(g, axis, t, tooth_angle, side):
    h = g["h0"] - t + math.atan(t)
    theta = tooth_angle + (h if side > 0 else -h)
    r = g["base"] * math.sqrt(1.0 + t * t)
    return polar(axis, r, theta)


def flank_arcs(g, axis, tooth_angle, side, ts, reverse=False):
    pairs = [(ts[i], ts[i + 1]) for i in range(len(ts) - 1)]
    if reverse:
        pairs = [(b, a) for a, b in reversed(pairs)]
    edges = []
    for t0, t1 in pairs:
        a = involute_xy(g, axis, t0, tooth_angle, side)
        b = involute_xy(g, axis, t1, tooth_angle, side)
        mid = involute_xy(g, axis, 0.5 * (t0 + t1), tooth_angle, side)
        edges.append(edge_arc(a, mid, b))
    return edges


def gear_outline_wire(g, axis, phase_deg):
    phase = math.radians(phase_deg)
    n = g["n"]
    pitch = 2.0 * math.pi / n
    ts = roll_samples(g["t_root"], g["t_pitch"], g["t_tip"])
    h_root = g["h_root"]
    radial = g["root"] < g["base"] - 1e-12
    edges = []
    for i in range(n):
        ang = phase + i * pitch
        lower0 = involute_xy(g, axis, ts[0], ang, -1)
        lower1 = involute_xy(g, axis, ts[-1], ang, -1)
        upper0 = involute_xy(g, axis, ts[0], ang, 1)
        upper1 = involute_xy(g, axis, ts[-1], ang, 1)
        if radial:
            lower_root = polar(axis, g["root"], ang - h_root)
            upper_root = polar(axis, g["root"], ang + h_root)
            edges.append(edge_line(lower_root, lower0))
        else:
            lower_root = lower0
            upper_root = upper0
        edges.extend(flank_arcs(g, axis, ang, -1, ts))
        th_lo = math.atan2(lower1[1] - axis[1], lower1[0] - axis[0])
        th_up = math.atan2(upper1[1] - axis[1], upper1[0] - axis[0])
        edges.append(edge_center_arc(axis, g["tip"], th_lo, th_up))
        edges.extend(flank_arcs(g, axis, ang, 1, ts, reverse=True))
        if radial:
            edges.append(edge_line(upper0, upper_root))
        nxt = polar(axis, g["root"], ang + pitch - h_root) if radial else involute_xy(g, axis, ts[0], ang + pitch, -1)
        th_ur = math.atan2(upper_root[1] - axis[1], upper_root[0] - axis[0])
        th_nl = math.atan2(nxt[1] - axis[1], nxt[0] - axis[0])
        edges.append(edge_center_arc(axis, g["root"], th_ur, th_nl))
    chained = []
    prev = None
    for e in edges:
        start = e.Vertexes[0].Point
        if prev is not None and (start - prev).Length > 1e-7:
            chained.append(Part.makeLine(prev, start))
        chained.append(e)
        prev = e.Vertexes[-1].Point
    outer = Part.Wire(chained)
    assert outer.isClosed(), "kernel: gear outline is not closed"
    return outer


def finalize_solid(solid):
    if solid.Solids:
        solid = solid.Solids[0]
    solid.sewShape()
    solid.fix(1e-6, 1e-6, 1e-5)
    solid = solid.removeSplitter()
    if solid.Solids:
        solid = solid.Solids[0]
    if solid.Shells:
        solid = Part.Solid(solid.Shells[0])
    return solid


def gear_solid(g, axis, phase_deg, bore):
    face = Part.Face(gear_outline_wire(g, axis, phase_deg))
    assert face.isValid() and face.Area > 0, "kernel: gear face is invalid"
    if abs(gearBaseZ) > 0:
        face.translate(FreeCAD.Vector(0, 0, gearBaseZ))
    solid = face.extrude(FreeCAD.Vector(0, 0, gearFaceWidth))
    bore_cyl = Part.makeCylinder(
        bore / 2.0,
        gearFaceWidth,
        FreeCAD.Vector(axis[0], axis[1], gearBaseZ),
        FreeCAD.Vector(0, 0, 1),
    )
    solid = solid.cut(bore_cyl)
    solid = finalize_solid(solid)
    assert solid.isValid() and solid.Volume > 0, "kernel: gear solid is invalid"
    return solid


def body_from_solid(name, solid):
    feat = doc.addObject("Part::Feature", name + "Solid")
    feat.Shape = solid
    body = new_body(name)
    body.BaseFeature = feat
    doc.recompute()
    assert body.Shape.isValid(), f"kernel: {name} shape is invalid after recompute"
    return body


doc = FreeCAD.newDocument("gear-pair")

carrier = new_body("Carrier")
carrier_sk = sketch_on(carrier, "CarrierSketch", gearBaseZ - carrierThickness)
add_xy_rect(carrier_sk, carrierMinX, carrierMinY, carrierLength, carrierWidth)
add_circle(carrier_sk, pinionAxisX, pinionAxisY, pinionBoreDiameter / 2.0)
add_circle(carrier_sk, wheel_axis_x, wheelAxisY, wheelBoreDiameter / 2.0)
pad(carrier, "CarrierPad", carrier_sk, carrierThickness, refine=True)

pinion_solid = gear_solid(pinion_g, (pinionAxisX, pinionAxisY), pinionPhase, pinionBoreDiameter)
wheel_solid = gear_solid(wheel_g, (wheel_axis_x, wheelAxisY), wheelPhase, wheelBoreDiameter)
pinion = body_from_solid("Pinion", pinion_solid)
wheel = body_from_solid("Wheel", wheel_solid)

doc.recompute()
assert pinion.Shape.isValid(), "kernel: pinion shape is invalid after recompute"
assert wheel.Shape.isValid(), "kernel: wheel shape is invalid after recompute"
assert carrier.Shape.isValid(), "kernel: carrier shape is invalid after recompute"
for obj in (pinion, wheel, carrier):
    for feat in obj.Group:
        if hasattr(feat, "Shape") and feat.Shape.Faces:
            assert feat.Shape.isValid(), f"kernel: {feat.Name} is invalid after recompute"
result = (pinion, wheel, carrier)

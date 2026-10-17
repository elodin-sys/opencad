import FreeCAD
import Part
import Sketcher

boardLength = 85.0
boardWidth = 56.0
pcbThickness = 1.6
mountX = 3.5
mountY = 3.5
mountPitchX = 58.0
mountPitchY = 49.0
boardMountDiameter = 2.7
underBoardDepth = 3.0
componentFreeRadius = 3.1
edgeClearance = 0.5
headroom = 20.0
wallThickness = 2.4
standoffHeight = 5.0
standoffDiameter = 6.2
pilotDiameter = 2.5
pilotDepth = 5.0
lidHoleDiameter = 3.0
lidThickness = 4.0
cornerPostWidth = 8.0
closureGap = 0.05
usbCx = 11.2
hdmi0X = 25.8
hdmi1X = 39.2
usbAUpperY = 47.0
usbALowerY = 29.1
rj45Y = 10.2
sdYMin = 22.0
sdYMax = 34.0

assert headroom > 0, "infeasible: headroom must be positive"
assert boardLength > 0, "infeasible: boardLength must be positive"
assert boardWidth > 0, "infeasible: boardWidth must be positive"
assert pcbThickness > 0, "infeasible: pcbThickness must be positive"
assert mountX > 0, "infeasible: mountX must be positive"
assert mountY > 0, "infeasible: mountY must be positive"
assert mountPitchX > 0, "infeasible: mountPitchX must be positive"
assert mountPitchY > 0, "infeasible: mountPitchY must be positive"
assert boardMountDiameter > 0, "infeasible: boardMountDiameter must be positive"
assert underBoardDepth > 0, "infeasible: underBoardDepth must be positive"
assert componentFreeRadius > 0, "infeasible: componentFreeRadius must be positive"
assert edgeClearance > 0, "infeasible: edgeClearance must be positive"
assert wallThickness >= 2.0, "infeasible: wallThickness must be at least 2 mm"
assert standoffHeight > 0, "infeasible: standoffHeight must be positive"
assert standoffDiameter > 0, "infeasible: standoffDiameter must be positive"
assert pilotDiameter > 0, "infeasible: pilotDiameter must be positive"
assert pilotDepth > 0, "infeasible: pilotDepth must be positive"
assert lidHoleDiameter > 0, "infeasible: lidHoleDiameter must be positive"
assert lidThickness >= 2.0, "infeasible: lidThickness must be at least 2 mm"
assert cornerPostWidth > 0, "infeasible: cornerPostWidth must be positive"
assert 0.0 <= closureGap <= 0.1, "infeasible: closureGap must stay in [0, 0.1]"
assert usbCx > 0, "infeasible: usbCx must be positive"
assert hdmi0X > 0, "infeasible: hdmi0X must be positive"
assert hdmi1X > 0, "infeasible: hdmi1X must be positive"
assert usbAUpperY > 0, "infeasible: usbAUpperY must be positive"
assert usbALowerY > 0, "infeasible: usbALowerY must be positive"
assert rj45Y > 0, "infeasible: rj45Y must be positive"
assert sdYMax > sdYMin, "infeasible: sd card slot y-range is inverted"
assert standoffHeight >= pilotDepth, "infeasible: standoffHeight must cover the standoff pilots"
assert standoffHeight > underBoardDepth, "infeasible: floor would intersect the bottom-component keep-out"
assert pilotDiameter < boardMountDiameter, "infeasible: pilot larger than the board mounting hole"
assert standoffDiameter / 2.0 <= componentFreeRadius, "infeasible: standoff boss leaves the component-free ring"
assert cornerPostWidth > wallThickness, "infeasible: corner posts must project past the walls"
assert cornerPostWidth / 2.0 > lidHoleDiameter / 2.0, "infeasible: lid hole does not fit in the corner post"
assert cornerPostWidth / 2.0 > pilotDiameter / 2.0, "infeasible: corner pilot does not fit in the corner post"

cavity_xmin = -edgeClearance
cavity_xmax = boardLength + edgeClearance
cavity_ymin = -edgeClearance
cavity_ymax = boardWidth + edgeClearance
ring_xmin = cavity_xmin - wallThickness
ring_xmax = cavity_xmax + wallThickness
ring_ymin = cavity_ymin - wallThickness
ring_ymax = cavity_ymax + wallThickness
outer_xmin = cavity_xmin - cornerPostWidth
outer_xmax = cavity_xmax + cornerPostWidth
outer_ymin = cavity_ymin - cornerPostWidth
outer_ymax = cavity_ymax + cornerPostWidth
floor_top = -standoffHeight
floor_z = floor_top - wallThickness
lid_z = pcbThickness + headroom
rim_z = lid_z - closureGap
base_height = rim_z - floor_z
usb_c_half = 6.5
hdmi_half = 6.0
usb_a_half = 7.5
rj45_half = 8.5
plug_overhang = 25.0
usb_c_height = 7.0
hdmi_height = 6.5
usb_a_height = 17.0
rj45_height = 15.0
mounts = (
    (mountX, mountY),
    (mountX + mountPitchX, mountY),
    (mountX, mountY + mountPitchY),
    (mountX + mountPitchX, mountY + mountPitchY),
)
corners = (
    (cavity_xmin - cornerPostWidth / 2.0, cavity_ymin - cornerPostWidth / 2.0),
    (cavity_xmax + cornerPostWidth / 2.0, cavity_ymin - cornerPostWidth / 2.0),
    (cavity_xmin - cornerPostWidth / 2.0, cavity_ymax + cornerPostWidth / 2.0),
    (cavity_xmax + cornerPostWidth / 2.0, cavity_ymax + cornerPostWidth / 2.0),
)


def add_xy_rect(sk, xmin, xmax, ymin, ymax):
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
    sk.addConstraint(Sketcher.Constraint("DistanceX", g0, 1, g0, 2, xmax - xmin))
    sk.addConstraint(Sketcher.Constraint("DistanceY", g0, 1, g3, 1, ymax - ymin))
    sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, g0, 1, xmin))
    sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, g0, 1, ymin))


def add_circle(sk, cx, cy, diameter):
    gid = sk.addGeometry(Part.Circle(FreeCAD.Vector(cx, cy, 0), FreeCAD.Vector(0, 0, 1), diameter / 2.0), False)
    sk.addConstraint(Sketcher.Constraint("Diameter", gid, diameter))
    sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gid, 3, cx))
    sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gid, 3, cy))


def origin_xy(body):
    return next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)


def sketch_on(body, name, z=0.0):
    sk = body.newObject("Sketcher::SketchObject", name)
    sk.AttachmentSupport = [(origin_xy(body), "")]
    sk.MapMode = "FlatFace"
    sk.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, z), FreeCAD.Rotation())
    return sk


def pad(body, name, sketch, length, reversed=False, refine=False):
    feat = body.newObject("PartDesign::Pad", name)
    feat.Profile = sketch
    feat.Length = length
    feat.Reversed = reversed
    feat.Refine = refine
    doc.recompute()
    assert feat.Shape.isValid(), f"kernel: {name} is invalid after recompute"
    return feat


def pocket(body, name, sketch, length=None, through=False, reversed=False, refine=False):
    feat = body.newObject("PartDesign::Pocket", name)
    feat.Profile = sketch
    if through:
        feat.Type = "ThroughAll"
    else:
        feat.Type = "Length"
        feat.Length = length
    feat.Reversed = reversed
    feat.Refine = refine
    doc.recompute()
    assert feat.Shape.isValid(), f"kernel: {name} is invalid after recompute"
    return feat


def add_bays(sk):
    add_xy_rect(sk, cavity_xmin, cavity_xmax, outer_ymin, ring_ymin)
    add_xy_rect(sk, cavity_xmin, cavity_xmax, ring_ymax, outer_ymax)
    add_xy_rect(sk, outer_xmin, ring_xmin, cavity_ymin, cavity_ymax)
    add_xy_rect(sk, ring_xmax, outer_xmax, cavity_ymin, cavity_ymax)


doc = FreeCAD.newDocument("rpi5-enclosure")
base = doc.addObject("PartDesign::Body", "Base")
base.AllowCompound = False
lid_tree = doc.addObject("PartDesign::Body", "LidTree")
lid_tree.AllowCompound = False
doc.recompute()

base_aabb = sketch_on(base, "BaseEnvelope", floor_z)
add_xy_rect(base_aabb, outer_xmin, outer_xmax, outer_ymin, outer_ymax)
pad(base, "BasePad", base_aabb, base_height)

base_bays = sketch_on(base, "BaseBays", floor_z)
add_bays(base_bays)
pocket(base, "BaseBayPockets", base_bays, length=base_height, reversed=True)

cavity = sketch_on(base, "Cavity", floor_top)
add_xy_rect(cavity, cavity_xmin, cavity_xmax, cavity_ymin, cavity_ymax)
pocket(base, "CavityPocket", cavity, length=rim_z - floor_top, reversed=True)

bosses = sketch_on(base, "StandoffBosses", floor_top)
for mx, my in mounts:
    add_circle(bosses, mx, my, standoffDiameter)
pad(base, "StandoffPads", bosses, standoffHeight)

standoff_pilots = sketch_on(base, "StandoffPilots", 0.0)
for mx, my in mounts:
    add_circle(standoff_pilots, mx, my, pilotDiameter)
pocket(base, "StandoffPilotPockets", standoff_pilots, length=pilotDepth)

corner_pilots = sketch_on(base, "CornerPilots", rim_z)
for cx, cy in corners:
    add_circle(corner_pilots, cx, cy, pilotDiameter)
pocket(base, "CornerPilotPockets", corner_pilots, length=pilotDepth)

port_notches = sketch_on(base, "PortNotches", pcbThickness)
add_xy_rect(port_notches, usbCx - usb_c_half, usbCx + usb_c_half, ring_ymin, 0.0)
add_xy_rect(port_notches, hdmi0X - hdmi_half, hdmi0X + hdmi_half, ring_ymin, 0.0)
add_xy_rect(port_notches, hdmi1X - hdmi_half, hdmi1X + hdmi_half, ring_ymin, 0.0)
add_xy_rect(port_notches, boardLength, ring_xmax, usbAUpperY - usb_a_half, usbAUpperY + usb_a_half)
add_xy_rect(port_notches, boardLength, ring_xmax, usbALowerY - usb_a_half, usbALowerY + usb_a_half)
add_xy_rect(port_notches, boardLength, ring_xmax, rj45Y - rj45_half, rj45Y + rj45_half)
pocket(base, "PortNotchPockets", port_notches, length=rim_z - pcbThickness, reversed=True)

sd_notch = sketch_on(base, "SdNotch", -underBoardDepth)
add_xy_rect(sd_notch, ring_xmin, 0.0, sdYMin, sdYMax)
pocket(base, "SdNotchPocket", sd_notch, length=rim_z + underBoardDepth, reversed=True, refine=True)

lid_aabb = sketch_on(lid_tree, "LidEnvelope", lid_z)
add_xy_rect(lid_aabb, outer_xmin, outer_xmax, outer_ymin, outer_ymax)
pad(lid_tree, "LidPad", lid_aabb, lidThickness)

lid_bays = sketch_on(lid_tree, "LidBays", lid_z)
add_bays(lid_bays)
pocket(lid_tree, "LidBayPockets", lid_bays, length=lidThickness, reversed=True)

lid_holes = sketch_on(lid_tree, "LidHoles", lid_z)
for cx, cy in corners:
    add_circle(lid_holes, cx, cy, lidHoleDiameter)
pocket(lid_tree, "LidHolePockets", lid_holes, length=lidThickness, reversed=True, refine=True)

plug_boxes = (
    (usbCx - usb_c_half, -plug_overhang, pcbThickness, usbCx + usb_c_half, 0.0, pcbThickness + usb_c_height),
    (hdmi0X - hdmi_half, -plug_overhang, pcbThickness, hdmi0X + hdmi_half, 0.0, pcbThickness + hdmi_height),
    (hdmi1X - hdmi_half, -plug_overhang, pcbThickness, hdmi1X + hdmi_half, 0.0, pcbThickness + hdmi_height),
    (
        boardLength,
        usbAUpperY - usb_a_half,
        pcbThickness,
        boardLength + plug_overhang,
        usbAUpperY + usb_a_half,
        pcbThickness + usb_a_height,
    ),
    (
        boardLength,
        usbALowerY - usb_a_half,
        pcbThickness,
        boardLength + plug_overhang,
        usbALowerY + usb_a_half,
        pcbThickness + usb_a_height,
    ),
    (
        boardLength,
        rj45Y - rj45_half,
        pcbThickness,
        boardLength + plug_overhang,
        rj45Y + rj45_half,
        pcbThickness + rj45_height,
    ),
    (-plug_overhang, sdYMin, -underBoardDepth, 0.0, sdYMax, 0.0),
)
lid_shape = lid_tree.Shape
if lid_shape.Solids:
    lid_shape = lid_shape.Solids[0]
for xmin, ymin, zmin, xmax, ymax, zmax in plug_boxes:
    tool = Part.makeBox(xmax - xmin, ymax - ymin, zmax - zmin)
    tool.translate(FreeCAD.Vector(xmin, ymin, zmin))
    lid_shape = lid_shape.cut(tool)
    if lid_shape.Solids:
        lid_shape = lid_shape.Solids[0]
assert lid_shape.isValid(), "kernel: lid shape is invalid after plug-box cuts"
lid_solid = doc.addObject("Part::Feature", "LidPlugTrim")
lid_solid.Shape = lid_shape
lid = doc.addObject("PartDesign::Body", "Lid")
lid.AllowCompound = False
lid.BaseFeature = lid_solid
doc.recompute()

assert base.Shape.isValid(), "kernel: base shape is invalid after recompute"
assert lid.Shape.isValid(), "kernel: lid shape is invalid after recompute"
for obj in (base, lid):
    for feat in obj.Group:
        if hasattr(feat, "Shape") and feat.Shape.Faces:
            assert feat.Shape.isValid(), f"kernel: {feat.Name} is invalid after recompute"
result = (base, lid)

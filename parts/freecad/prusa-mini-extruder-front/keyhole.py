"""Central stepped opening, constructed as one PartDesign cutting family.

The table/section interpretation of Q1 governs: upper 12/16/26 mm,
lower 22.5 mm, a conical transition, then 14 mm. No filament geometry
or unsupported lower 16 mm cylinder belongs to this module.

The front counterbore trims the adjacent boss bevel when composed with
the exterior. Its analytic diameter and depth govern that intersection.
"""

import math

import FreeCAD
import Part
import Sketcher
from params import (
    keyAxisX,
    keyBackDepth,
    keyLowerExitDiameter,
    keyLowerExitStart,
    keyLowerRecessDiameter,
    keyMiddleEnd,
    keyUpperBoreDiameter,
    keyUpperCounterboreDiameter,
    keyUpperRecessDiameter,
    keyUpperZ,
    lowerTransitionLength,
    plateThickness,
)

_OVERRUN = 0.02
# Stated dimension-sheet neck planes, expressed relative to the hole axes.
_NECK_NX = 0.9659
_NECK_NZ = -0.2588
_LEFT_DX = -6.566
_LEFT_Z = 5.18
_RIGHT_DX = 4.594
_RIGHT_DZ = -3.86


def _check(body, *features):
    body.Document.recompute()
    for feature in features:
        assert feature.isValid(), "kernel: invalid keyhole feature " + feature.Name
        if feature.TypeId == "Sketcher::SketchObject":
            assert feature.FullyConstrained, "sketch: unconstrained keyhole profile " + feature.Name
        else:
            assert feature.Shape.isValid(), "kernel: invalid keyhole shape " + feature.Name
            assert len(feature.Shape.Solids) == 1, "kernel: keyhole construction must be one solid"


def _sketch(body, name, y):
    plane = next(obj for obj in body.Origin.OriginFeatures if "XZ" in obj.Name and "Plane" in obj.Name)
    sketch = body.newObject("Sketcher::SketchObject", name)
    sketch.AttachmentSupport = [(plane, "")]
    sketch.MapMode = "FlatFace"
    sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, -y), FreeCAD.Rotation())
    return sketch


def _circle(body, name, y, z, diameter):
    sketch = _sketch(body, name, y)
    index = sketch.addGeometry(
        Part.Circle(FreeCAD.Vector(keyAxisX, z, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), diameter / 2.0),
        False,
    )
    sketch.addConstraint(Sketcher.Constraint("Diameter", index, diameter))
    if keyAxisX:
        sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, index, 3, keyAxisX))
    else:
        sketch.addConstraint(Sketcher.Constraint("DistanceX", index, 3, 0.0))
    if z:
        sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, index, 3, z))
    else:
        sketch.addConstraint(Sketcher.Constraint("PointOnObject", index, 3, -1))
    _check(body, sketch)
    return sketch


def _polygon(body, name, y, points):
    sketch = _sketch(body, name, y)
    for index, start in enumerate(points):
        end = points[(index + 1) % len(points)]
        sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(*start, 0.0), FreeCAD.Vector(*end, 0.0)), False)
    for index, point in enumerate(points):
        sketch.addConstraint(Sketcher.Constraint("Coincident", index, 2, (index + 1) % len(points), 1))
        sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, index, 1, point[0]))
        if point[1]:
            sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, index, 1, point[1]))
        else:
            sketch.addConstraint(Sketcher.Constraint("PointOnObject", index, 1, -1))
    _check(body, sketch)
    return sketch


def _pad(body, name, profile, length):
    pad = body.newObject("PartDesign::Pad", name)
    pad.Profile = profile
    pad.Length = length
    pad.Reversed = True  # Named XZ plane has normal -y.
    pad.Refine = True
    _check(body, pad)
    return pad


def _cylinder(body, name, y0, y1, z, diameter):
    profile = _circle(body, name + "Sketch", y0, z, diameter)
    return _pad(body, name, profile, y1 - y0)


def _tool(document):
    tool = document.addObject("PartDesign::Body", "KeyholeTool")
    tool.AllowCompound = False
    document.recompute()

    # The finite trapezoid spans the two axes. Its hidden bottom/top ends
    # lie inside the circular tools. Exposed walls are the stated planes;
    # their extents come from the circles and taper, without fitted slabs.
    normal_length = math.hypot(_NECK_NX, _NECK_NZ)
    nx, nz = _NECK_NX / normal_length, _NECK_NZ / normal_length
    slope = -nz / nx
    left_anchor = keyAxisX + _LEFT_DX
    right_anchor = keyAxisX + _RIGHT_DX
    right_z = keyUpperZ + _RIGHT_DZ

    def left(z):
        return left_anchor + slope * (z - _LEFT_Z)

    def right(z):
        return right_anchor - slope * (z - right_z)

    assert left(keyUpperZ) < right(keyUpperZ), "infeasible: neck planes cross below the upper axis"
    points = [(left(0.0), 0.0), (right(0.0), 0.0), (right(keyUpperZ), keyUpperZ), (left(keyUpperZ), keyUpperZ)]
    assert all(-15.0 <= x <= 11.0 and -11.25 <= z <= 29.4 for x, z in points), (
        "partition: neck profile exceeds the authorized region"
    )
    neck = _polygon(tool, "KeyholeNeckSketch", -_OVERRUN, points)
    _pad(tool, "KeyholeNeckTool", neck, keyMiddleEnd + _OVERRUN)

    _cylinder(tool, "KeyLowerBackRecessTool", -_OVERRUN, keyBackDepth, 0.0, keyLowerRecessDiameter)
    lower = _circle(tool, "KeyLowerTaperStart", keyBackDepth, 0.0, keyLowerRecessDiameter)
    upper = _circle(tool, "KeyLowerTaperEnd", keyLowerExitStart, 0.0, keyLowerExitDiameter)
    taper = tool.newObject("PartDesign::AdditiveLoft", "KeyLowerTaperTool")
    taper.Profile = lower
    taper.Sections = [upper]
    taper.Ruled = True
    taper.Refine = True
    _check(tool, taper)
    _cylinder(
        tool,
        "KeyLowerFrontCounterboreTool",
        keyLowerExitStart - _OVERRUN,
        plateThickness + _OVERRUN,
        0.0,
        keyLowerExitDiameter,
    )
    _cylinder(tool, "KeyUpperBackRecessTool", -_OVERRUN, keyBackDepth + _OVERRUN, keyUpperZ, keyUpperRecessDiameter)
    _cylinder(tool, "KeyUpperMiddleBoreTool", keyBackDepth, keyMiddleEnd + _OVERRUN, keyUpperZ, keyUpperBoreDiameter)
    _cylinder(
        tool,
        "KeyUpperFrontCounterboreTool",
        keyMiddleEnd,
        plateThickness + _OVERRUN,
        keyUpperZ,
        keyUpperCounterboreDiameter,
    )
    _check(tool, tool, *tool.Group)
    return tool


def apply(body):
    """Cut the union of the keyhole tools once; preserve the input identity."""
    target = body[0] if isinstance(body, tuple) else body
    assert 0.0 < keyBackDepth < keyMiddleEnd < plateThickness, "infeasible: upper stack depths cross"
    assert keyBackDepth < keyLowerExitStart < plateThickness, "infeasible: lower stack depths cross"
    assert lowerTransitionLength > 0.0, "infeasible: lower transition length must be positive"
    assert 0.0 < keyLowerExitDiameter < keyLowerRecessDiameter, "infeasible: lower taper must narrow"
    assert 0.0 < keyUpperRecessDiameter < keyUpperBoreDiameter < keyUpperCounterboreDiameter, (
        "infeasible: upper stack diameters must increase"
    )
    assert keyUpperZ > 0.0, "infeasible: upper axis must be above the lower axis"
    radii = (keyLowerRecessDiameter / 2.0, keyUpperCounterboreDiameter / 2.0)
    assert keyAxisX - max(radii) >= -15.0 and keyAxisX + max(radii) <= 11.0, (
        "partition: keyhole tools exceed the authorized x region"
    )
    assert -radii[0] >= -11.25 and keyUpperZ + radii[1] <= 29.4, (
        "partition: keyhole tools exceed the authorized z region"
    )
    tool = _tool(target.Document)
    cut = target.newObject("PartDesign::Boolean", "KeyholeCut")
    cut.addObjects([tool])
    cut.Type = "Cut"
    cut.Refine = True
    _check(target, cut, target, *target.Group)
    for feature in target.Document.Objects:
        if feature.TypeId.startswith("PartDesign::"):
            assert feature.isValid(), "kernel: invalid PartDesign feature after keyhole " + feature.Name
            if hasattr(feature, "Shape"):
                assert feature.Shape.isValid(), "kernel: invalid final feature shape " + feature.Name
    return body

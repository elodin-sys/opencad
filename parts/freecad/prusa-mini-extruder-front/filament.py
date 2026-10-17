"""Finite diameter-four filament surfaces in the exterior's upper web.

Two constrained circular profiles produce one united construction tool. The
axes differ, so one PartDesign Boolean consumes that tool in a single cut.
Only the documented finite spans are removed; connecting web trims remain
with the exterior and must not be inferred from the remote angled-axis origin.
"""

import math

import FreeCAD
import Part
import Sketcher
from params import (
    bodyTopZ,
    filamentDiameter,
    filamentDirX,
    filamentDirY,
    filamentEntryAxisX,
    filamentEntryAxisY,
    filamentEntryEnd,
    filamentEntryStart,
    filamentTransverseEnd,
    filamentTransverseX,
    filamentZ,
    lugMaxZ,
    lugWebPeakX,
    plateThickness,
)

_OVERRUN = 0.02
_FACE_CLEARANCE = 0.101
_REGION_MIN = (12.65, 0.0, 28.0)
_REGION_MAX = (23.25, 14.0, 32.0)


def _check(body, *features):
    body.Document.recompute()
    for feature in features:
        assert feature.isValid(), "kernel: invalid filament feature " + feature.Name
        if feature.TypeId == "Sketcher::SketchObject":
            assert feature.FullyConstrained, "sketch: unconstrained filament profile " + feature.Name
        else:
            assert not feature.Shape.isNull(), "kernel: null filament shape " + feature.Name
            assert feature.Shape.isValid(), "kernel: invalid filament shape " + feature.Name


def _cylinder(tool, name, origin, direction, first, last):
    """Pad a circle on the named XY plane with a parameter-driven attachment."""
    plane = next(obj for obj in tool.Origin.OriginFeatures if "XY" in obj.Name and "Plane" in obj.Name)
    sketch = tool.newObject("Sketcher::SketchObject", name + "Sketch")
    sketch.AttachmentSupport = [(plane, "")]
    sketch.MapMode = "FlatFace"
    axis = FreeCAD.Vector(*direction)
    start = FreeCAD.Vector(*origin) + axis * (first - _OVERRUN)
    sketch.AttachmentOffset = FreeCAD.Placement(start, FreeCAD.Rotation(FreeCAD.Vector(0.0, 0.0, 1.0), axis))
    circle = sketch.addGeometry(
        Part.Circle(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), filamentDiameter / 2.0), False
    )
    sketch.addConstraint(Sketcher.Constraint("Coincident", circle, 3, -1, 1))
    sketch.addConstraint(Sketcher.Constraint("Diameter", circle, filamentDiameter))
    _check(tool, sketch)
    pad = tool.newObject("PartDesign::Pad", name + "Tool")
    pad.Profile = sketch
    pad.Length = last - first + 2.0 * _OVERRUN
    pad.Refine = True
    _check(tool, pad, tool)
    return pad


def _preserve_lug(tool, stock):
    """Reserve the required 0.1 mm around the exterior-owned convex lug face."""
    faces = []
    for face in stock.Faces:
        surface = face.Surface
        if not isinstance(surface, Part.Cylinder):
            continue
        if not (0.0 < surface.Center.x < lugWebPeakX and abs(surface.Axis.y) > 0.999999):
            continue
        u0, u1, v0, v1 = face.ParameterRange
        u, v = (u0 + u1) / 2.0, (v0 + v1) / 2.0
        radial = face.valueAt(u, v) - surface.Center
        radial -= surface.Axis * radial.dot(surface.Axis)
        if face.normalAt(u, v).dot(radial) > 0.0:
            faces.append(face)
    assert faces, "partition: the exterior-owned lug face is missing"

    buffers = []
    for face in faces:
        surface = face.Surface
        radius = surface.Radius
        assert radius > 2.0 * _FACE_CLEARANCE, "infeasible: lug radius is smaller than its ownership clearance"
        u0, u1, v0, v1 = face.ParameterRange
        angle = math.asin(_FACE_CLEARANCE / (radius - _FACE_CLEARANCE))
        u0, u1 = u0 - angle, u1 + angle
        v0, v1 = v0 - _FACE_CLEARANCE, v1 + _FACE_CLEARANCE
        origin = surface.Center + surface.Axis * v0

        outer = [
            origin + (surface.value(u, v0) - origin) * ((radius + _FACE_CLEARANCE) / radius)
            for u in (u0, (u0 + u1) / 2.0, u1)
        ]
        inner = [
            origin + (surface.value(u, v0) - origin) * ((radius - _FACE_CLEARANCE) / radius)
            for u in (u1, (u0 + u1) / 2.0, u0)
        ]
        wire = Part.Wire(
            [
                Part.Arc(*outer).toShape(),
                Part.makeLine(outer[-1], inner[0]),
                Part.Arc(*inner).toShape(),
                Part.makeLine(inner[-1], outer[0]),
            ]
        )
        buffers.append(Part.Face(wire).extrude(surface.Axis * (v1 - v0)))
    united = buffers[0].multiFuse(buffers[1:]).removeSplitter() if len(buffers) > 1 else buffers[0]
    assert united.isValid(), "kernel: invalid lug-face clearance tool"
    doc = tool.Document
    seed = doc.addObject("Part::Feature", "FilamentLugClearanceGeometry")
    seed.Shape = united
    clearance = doc.addObject("PartDesign::Body", "FilamentLugClearanceTool")
    clearance.AllowCompound = True
    clearance.BaseFeature = seed
    _check(clearance, seed, clearance)
    trim = tool.newObject("PartDesign::Boolean", "FilamentLugClearance")
    trim.Type = "Cut"
    trim.Group = [clearance]
    trim.Refine = True
    _check(tool, trim, tool)
    for face in faces:
        assert tool.Shape.distToShape(face)[0] >= 0.1 - 1e-6, "partition: filament approaches the protected lug face"


def apply(body):
    """Cut the united passage family once and return the same Body or tuple."""
    assert filamentDiameter > 0.0, "infeasible: filament diameter must be positive"
    assert plateThickness > 0.0, "infeasible: plate thickness must be positive"
    assert 0.0 < filamentTransverseEnd < plateThickness - 0.1, "infeasible: transverse bore exceeds the web"
    assert 0.0 < filamentEntryStart < filamentEntryEnd, "infeasible: angled filament span is reversed"
    assert filamentTransverseX < lugWebPeakX, "infeasible: transverse filament axis lies beyond the lug web"
    radius = filamentDiameter / 2.0
    assert bodyTopZ <= filamentZ - radius, "partition: filament would cut below the shared clamp plane"
    assert filamentZ + radius <= lugMaxZ - 0.1, "partition: filament would cut the upper exterior crown"
    norm = math.hypot(filamentDirX, filamentDirY)
    assert norm > 0.0, "infeasible: angled filament direction is zero"
    dx, dy = filamentDirX / norm, filamentDirY / norm
    assert dx > 0.0 and dy > 0.0, "infeasible: angled filament direction must enter the upper web"

    target = body[0] if isinstance(body, tuple) else body
    doc = target.Document
    stock = target.Shape.copy()
    tool = doc.addObject("PartDesign::Body", "FilamentTool")
    # The tabulated finite surface spans are disjoint. Their union is a compound
    # construction tool, never an additional deliverable Body or invented link.
    tool.AllowCompound = True
    doc.recompute()
    _cylinder(
        tool,
        "FilamentTransverse",
        (filamentTransverseX, 0.0, filamentZ),
        (0.0, 1.0, 0.0),
        0.0,
        filamentTransverseEnd,
    )
    _cylinder(
        tool,
        "FilamentAngled",
        (filamentEntryAxisX, filamentEntryAxisY, filamentZ),
        (dx, dy, 0.0),
        filamentEntryStart,
        filamentEntryEnd,
    )
    _preserve_lug(tool, stock)
    _check(tool, tool, *tool.Group)

    # Check changed material rather than the tool's air overrun. Shared y=0 and
    # z=28 contacts are intentional; no clamp or surrounding-web trim is added.
    removed = stock.common(tool.Shape)
    assert removed.isValid() and removed.Volume > 0.0, "kernel: filament tools miss the exterior stock"
    # Ordinary bounds include the parent loft surface outside its trimmed face.
    bounds = removed.optimalBoundingBox(False, False)
    for actual, limit in zip((bounds.XMin, bounds.YMin, bounds.ZMin), _REGION_MIN):
        assert actual >= limit - 1e-6, f"partition: filament removal falls below its assigned region: {bounds}"
    for actual, limit in zip((bounds.XMax, bounds.YMax, bounds.ZMax), _REGION_MAX):
        assert actual <= limit + 1e-6, f"partition: filament removal exceeds its assigned region: {bounds}"
    assert bounds.YMax <= plateThickness - 0.1, "partition: filament reaches the opposite exterior face"

    cut = target.newObject("PartDesign::Boolean", "FilamentPassages")
    cut.Type = "Cut"
    cut.Group = [tool]
    cut.Refine = True
    _check(target, cut, target)
    assert len(target.Shape.Solids) == 1, "kernel: filament must leave one connected housing solid"
    assert target.Shape.Volume < stock.Volume, "kernel: filament did not remove material"
    assert target.Shape.cut(stock).Volume < 1e-7, "kernel: filament added material outside the exterior stock"
    for feature in (*target.Group, *tool.Group):
        assert feature.isValid(), "kernel: invalid feature after filament subtraction " + feature.Name
    doc.recompute()
    return body

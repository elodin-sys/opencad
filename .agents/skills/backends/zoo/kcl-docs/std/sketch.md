# std::sketch
Sketching is the foundational activity for most KCL programs.

Common args:
- instances: [n3] [n4] [n5]
- tolerance: [n2]
- useOriginal: [n8]
### ellipticPoint
`ellipticPoint(majorRadius: number, minorRadius: number, x?: number(Length), y?: number(Length)): Point2d`
- majorRadius: The major radius, a, of the elliptic equation x^2 / a ^ 2 + y^2 / b^2 = 1.
- minorRadius: The minor radius, b, of the hyperbolic equation x^2 / a ^ 2 + y^2 / b^2 = 1.
```kcl
point001 = ellipticPoint(x = 2, majorRadius = 2, minorRadius = 1)
point002 = ellipticPoint(y = 0, majorRadius = 2, minorRadius = 1)
assert(point001[0], isEqualTo = point002[0])
assert(point001[1], isEqualTo = point002[1])
```
### extrude
`extrude(@sketches: [Sketch|Face|TaggedFace|TaggedEdge|Edge|Segment|any; 1+], length?: number(Length), to?: Point3d|Axis3d|Plane|Edge|Face|Sketch|Solid|TaggedEdge|TaggedFace|any, symmetric?: bool, direction?: Point3d|Edge|TaggedEdge|Segment|any, bidirectionalLength?: number(Length), tagStart?: TagDecl, tagEnd?: TagDecl, draftAngle?: number(Angle), twistAngle?: number(Angle), twistAngleStep?: number(Angle), twistCenter?: Point2d, method?: string, hideSeams?: bool, bodyType?: string): [Solid; 1+]`
When you sketch on a face of a solid, extruding extends or cuts into the existing solid, meaning you don't need to union or subtract the volumes. You can change this behavior by using the `method` parameter.
- sketches: [face-api]
- to: Incompatible with `length` and `twistAngle`. [face-api]
- symmetric: If true, the extrusion will happen symmetrically around the sketch. Otherwise, the extrusion will happen on only one side of the sketch.
- direction: If specified, will extrude in this direction instead of the sketch plane normal. If an edge is being extruded, this defaults to halfway between the faces on either side of the edge.
- bidirectionalLength: Only used with `length`; incompatible with `symmetric`.
- tagStart: A named tag for the face at the start of the extrusion, i.e. the original sketch.
- tagEnd: A named tag for the face at the end of the extrusion, i.e. the new face created by extruding the original sketch.
- draftAngle: **Experimental.** Positive draft angle means the sketch gets smaller while extruding, i.e. inwards draft. Negative draft angle means the sketch gets bigger while extruding, i.e. outwards draft. Defaults to zero, i.e. no draft.
- twistAngle: If given, the sketch will be twisted around this angle while being extruded. Incompatible with `to`.
- twistAngleStep: Must be between 4 and 90 degrees. Only used if `twistAngle` is given, defaults to 15 degrees.
- twistCenter: Relative to the plane's origin. Only used if `twistAngle` is given, defaults to [0, 0] i.e. plane origin.
- method: The method used during extrusion, either `NEW` or `MERGE`. `NEW` creates a new object. `MERGE` merges the extruded objects together. The default is `MERGE`.
- hideSeams: Whether or not to hide the seams between the original and resulting object. Only used if a face is extruded and method = MERGE
### faceOf
`faceOf(@solid: Solid, face: TaggedFace|Segment): Face`
### getBoundedEdge
`getBoundedEdge(@solid: Solid, edge: Edge|any, lowerBound?: number(_), upperBound?: number(_)): BoundedEdge`
- edge: This can be a tagged edge or an edge ID from `edgeId(...)`. [face-api]
- lowerBound: A lower percentage bound of the edge, must be between 0 and 1 inclusive. Defaults to 0.
### getCommonEdge
`getCommonEdge(faces: [TaggedFace; 2]): Edge`
- faces: The tags of the faces you want to find the common edge between.
### getNextAdjacentEdge
`getNextAdjacentEdge(@edge: TaggedEdge): Edge`
### getOppositeEdge
`getOppositeEdge(@edge: TaggedEdge): Edge`
### getPreviousAdjacentEdge
`getPreviousAdjacentEdge(@edge: TaggedEdge): Edge`
### hyperbolicPoint
`hyperbolicPoint(semiMajor: number, semiMinor: number, x?: number(Length), y?: number(Length)): Point2d`
```kcl
point = hyperbolicPoint(x = 5, semiMajor = 2, semiMinor = 1)
```
### lastSegX
`lastSegX(@sketch: Sketch): number(Length)`
### lastSegY
`lastSegY(@sketch: Sketch): number(Length)`
### loft
`loft(@sketches: [Sketch|[Segment; 1+]; 2+], vDegree?: number(_), bezApproximateRational?: bool, baseCurveIndex?: number(_), tolerance?: number(Length), tagStart?: TagDecl, tagEnd?: TagDecl, bodyType?: string): Solid`
- sketches: Must include at least 2 sketches.
- vDegree: Must be greater than zero. For example, use 2 for quadratic, or 3 for cubic interpolation in the V direction.
- bezApproximateRational: This will remove banding around interpolations between arcs and non-arcs.
### parabolicPoint
`parabolicPoint(coefficients: [number; 3], x?: number(Length), y?: number(Length)): Point2d`
- coefficients: The coefficients [a, b, c] of the parabolic equation y = ax^2 + bx + c.
### patternCircular2d
`patternCircular2d(@sketches: [Sketch; 1+], instances: number(_), center?: Point2d, arcDegrees?: number(Angle), rotateDuplicates?: bool, useOriginal?: bool): [Sketch; 1+]`
- center: This is a 2D vector. If not given, defaults to `[0, 0]`.
- arcDegrees: The arc angle (in degrees) to place the repetitions. Must be greater than 0.
- rotateDuplicates: [n7]
### patternLinear2d
`patternLinear2d(@sketches: [Sketch; 1+], instances: number(_), distance: number(Length), axis: Axis2d|Point2d, useOriginal?: bool): [Sketch; 1+]`
Currently, KCL's type system limitations make the type signature here misleading. This function works with Regions from the new sketch blocks (that use constraint solvers), or the old, deprecated, imperative sketch/profile syntax from older versions of KCL. It does _not_ work as expected with sketch blocks, only with the regions that can be created from sketch blocks.
- distance: Distance between each repetition.
### patternTransform2d
`patternTransform2d(@sketches: [Sketch; 1+], instances: number(_), transform: fn(number(_)): { }, useOriginal?: bool): [Sketch; 1+]`
- transform: [n10] [n11]
### planeOf
`planeOf(@solid: Solid, face: TaggedFace|Segment): Plane`
### profileStart
`profileStart(@profile: Sketch): Point2d`
### profileStartX
`profileStartX(@profile: Sketch): number(Length)`
### profileStartY
`profileStartY(@profile: Sketch): number(Length)`
### region
`region(point?: Point2d|Segment, segments?: [Segment; 1+], intersectionIndex?: number(_), direction?: string, sketch?: any): Sketch`
Prefer the `segments` parameter. It forms a region by tracing the first segment from its start point to the intersection with the second segment, then turning at each intersection using `direction` until returning to the first segment.
For a single closed segment such as a circle, pass only that segment. `intersectionIndex` and `direction` are unnecessary for one loop; use them to disambiguate a boundary traced from multiple segments.
- intersectionIndex: The default is `-1`, which uses the last intersection. This is usually only needed when two or more `segments` are provided.
- direction: `CCW` for counterclockwise, `CW` for clockwise. Default is `CCW`. This is usually only needed when two or more `segments` are provided.
- sketch: This is required when point is a `Point2d`.
```kcl
s = sketch(on = XY) {
  line1 = line(start = [var -5mm, var 0mm], end = [var 5mm, var 0mm])
  arc1 = arc(start = [var 5mm, var 0mm], end = [var -5mm, var 0mm], center = [var 0mm, var 6mm])
  coincident([line1.end, arc1.start])
  coincident([line1.start, arc1.end])
}

r = region(segments = [s.line1, s.arc1])
extrude(r, length = 2)
```
### revolve
`revolve(@sketches: [Sketch|Segment; 1+], axis: Axis2d|Edge|Segment|any, angle?: number(Angle), tolerance?: number(Length), symmetric?: bool, bidirectionalAngle?: number(Angle), tagStart?: TagDecl, tagEnd?: TagDecl, bodyType?: string): [Solid; 1+]`
This, like extrude, is able to create a 3-dimensional solid from a 2-dimensional sketch.
**NOTE:** Currently,, revolved bodies don't support being scaled in a non-uniform way (i.e. scaled differently along each axis).
- axis: Can be an Axis2d, an Edge, or a solved Segment. [face-api]
- angle: Angle to revolve (in degrees). Default is 360.
- symmetric: If true, the extrusion will happen symmetrically around the sketch.
- bidirectionalAngle: If specified, will also revolve in the opposite direction to 'angle' to the specified angle. If 'symmetric' is true, this value is ignored.
### segAng
`segAng(@tag: TaggedEdge): number(Angle)`
### segEnd
`segEnd(@tag: TaggedEdge): Point2d`
### segEndX
`segEndX(@tag: TaggedEdge): number(Length)`
### segEndY
`segEndY(@tag: TaggedEdge): number(Length)`
### segLen
`segLen(@tag: TaggedEdge): number(Length)`
### segStart
`segStart(@tag: TaggedEdge): Point2d`
### segStartX
`segStartX(@tag: TaggedEdge): number(Length)`
### segStartY
`segStartY(@tag: TaggedEdge): number(Length)`
### sweep
`sweep(@sketches: [Sketch|Face|TaggedFace|Segment; 1+], path: Sketch|Helix|[Segment; 1+], sectional?: bool, tolerance?: number(Length), relativeTo?: string, translateProfileToPath?: bool, orientProfilePerpendicular?: bool, tagStart?: TagDecl, tagEnd?: TagDecl, bodyType?: string, version?: number(_)): [Solid; 1+]`
This, like extrude, is able to create a 3-dimensional surface or solid from a 2-dimensional sketch. This is useful for creating more complex shapes that can't be created with a simple extrusion.
- sectional: If true, the sweep will be broken up into sub-sweeps (extrusions, revolves, sweeps) based on the trajectory path components.
- relativeTo: !dep, removed in KCL 3; do not set
- translateProfileToPath: If true, the profile being swept will be moved to the path being swept along, before the sweep starts. If false, the profile stays where it is, and the sweep starts from there. Defaults to false.
- orientProfilePerpendicular: If true, before the sweep starts, the profile will be re-oriented so that it is perpendicular to the path being swept along. If false, the profile is left in its current orientation. On KCL 2.0 and earlier, defaults to false. On KCL 3.0 and later, defaults to the value of `translateProfileToPath`, so a profile that is moved to the path is also oriented perpendicular to it unless you say otherwise.
- version: !dep, removed in KCL 3; do not set
### tangentToEnd
`tangentToEnd(@tag: TaggedEdge): number(Angle)`

## Sketch v1 only, solver version pending (!v1soft): `conic`, `ellipse`, `elliptic`, `hyperbolic`, `parabolic`

## Deprecated sketch v1 (!dep; recognise in old code, never write): `angledLine`, `angledLineThatIntersects`, `arc`, `bezierCurve`, `circle`, `circleThreePoint`, `close`, `involuteCircular`, `line`, `polygon`, `rectangle`, `startProfile`, `startSketchOn`, `subtract2d`, `tangentialArc`, `xLine`, `yLine`

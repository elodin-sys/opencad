# std::solver
Functions for sketch-solve using constraints.
- `solver::ORIGIN: Point2d`: The origin point in a sketch.

Common args:
- labelPosition: Optional position for the displayed constraint label in the sketch's local 2D coordinate system.
### angleDimension
`solver::angleDimension(lines: [Segment; 2], sector: number(_), inverse?: bool, labelPosition?: Point2d)`
- lines: The ordered pair of line segments whose selected angle sector should match the value set with `==`. A line's positive direction runs from its start point to its end point; its negative direction is the reverse.
- sector: Which counterclockwise sweep about the line intersection to constrain: `1`, first line's positive direction to the second line's positive direction; `2`, second positive to first negative; `3`, first negative to second negative; or `4`, second negative to first positive.
- inverse: Use the counterclockwise sweep from the selected sector's end direction to its start direction. For example, a `20deg` sweep with `inverse = false` becomes `340deg` with `inverse = true`.
### arc
`solver::arc(start: Point2d, end: Point2d, center: Point2d, direction?: string, construction?: bool): Segment`
Use `direction = CW` to sweep the other way around the circle without swapping the start and end points.
- direction: The direction that the arc sweeps from start to end: `CCW` for counterclockwise or `CW` for clockwise. Defaults to `CCW`.
```kcl
height = 2
profile = sketch(on = XY) {
  arc1 = arc(start = [0, 0], end = [0, height], center = [0, height / 2])
}
```
### circle
`solver::circle(start: Point2d, center: Point2d, construction?: bool): Segment`
The starting point is currently free to float around the circumference of the circle. We suggest adding `vertical([myCircle.start, myCircle.center])` or `horizontal([myCircle.start, myCircle.center])`.
### coincident
`solver::coincident(@points: [Segment|Point2d; 2+])`
A single `Point2d` (e.g. `[1mm, 2.5mm]`) can be used to pin a point to a fixed position.
- points: When more than two inputs are provided, each item must be a point or `ORIGIN`.
```kcl
profile = sketch(on = XY) {
  edge1 = line(start = [var 0mm, var 0mm], end = [var 4mm, var 0mm])
  edge2 = line(start = [var 4mm, var 0mm], end = [var 4mm, var 3mm])
  edge3 = line(start = [var 4mm, var 3mm], end = [var 0mm, var 3mm])
  edge4 = line(start = [var 0mm, var 3mm], end = [var 0mm, var 0mm])
  coincident([edge1.end, edge2.start])
  coincident([edge2.end, edge3.start])
  coincident([edge3.end, edge4.start])
  coincident([edge4.end, edge1.start])
}

solid = extrude(region(segments = [profile.edge1, profile.edge2]), length = 2)
```
### controlPointSpline !exp
`solver::controlPointSpline(points: [Point2d; 3+], construction?: bool): Segment`
The current degree policy is: - 3 control points -> degree 2 - 4 or more control points -> degree 3
```kcl
@settings(experimentalFeatures = allow)

profile = sketch(on = XY) {
  spline1 = controlPointSpline(points = [
    [var 0mm, var 0mm],
    [var 20mm, var 30mm],
    [var 40mm, var 0mm],
    [var 60mm, var 20mm]
  ])
}
```
### diameter
`solver::diameter(@points: Segment, labelPosition?: Point2d)`
- points: The arc or circle segment whose diameter should match the value set with `==`.
### distance
`solver::distance(@points: [Segment|Point2d; 2], labelPosition?: Point2d)`
The distance is always non-negative, and the order of the two entities does not matter: `distance([a, b]) == 5mm` and `distance([b, a]) == 5mm` are the same constraint. This differs from `horizontalDistance` and `verticalDistance`, which are signed and order-sensitive.
A point may be `ORIGIN`, and arcs are treated as the full circle through them.
- points: Two sketch entities, or one sketch entity and `ORIGIN`, whose separation should match the value set with `==`. The order of the entities does not matter.
### equalLength
`solver::equalLength(@lines: [Segment; 2+])`
```kcl
profile = sketch(on = XY) {
  base = line(start = [var -3mm, var 0mm], end = [var 3mm, var 0mm])
  side1 = line(start = [var 3mm, var 0mm], end = [var 0mm, var 4mm])
  side2 = line(start = [var 0mm, var 4mm], end = [var -3mm, var 0mm])
  coincident([base.end, side1.start])
  coincident([side1.end, side2.start])
  coincident([side2.end, base.start])
  horizontal(base)
  equalLength([side1, side2])
}

solid = extrude(region(segments = [profile.base, profile.side1]), length = 2)
```
### equalRadius
`solver::equalRadius(@input: [Segment; 2+])`
```kcl
@settings(kclVersion = 2.0)

sketch1 = sketch(on = XY) {
  circle1 = circle(start = [var -2mm, var 0mm], center = [var -6mm, var 0mm])
  circle2 = circle(start = [var 10mm, var 0mm], center = [var 6mm, var 0mm])
  equalRadius([circle1, circle2])
}

solid1 = extrude(region(segments = [sketch1.circle1]), length = 2)
solid2 = extrude(region(segments = [sketch1.circle2]), length = 2)
```
### fixed
`solver::fixed(@points: [Segment|Point2d; 2+])`
`fixed()` is an alias for `coincident()`. By convention, `fixed()` is used when one of the points is a known location, not solved with constraints and not another point in the sketch.
Calling `fixed()` with one segment, such as `fixed(edge)`, is invalid and produces an argument error. `fixed()` requires an array of at least two points or segments.
```kcl
profile = sketch(on = XY) {
  edge = line(start = [var 0mm, var 0mm], end = [var 10mm, var 0mm])
  fixed([edge.start, ORIGIN])
  horizontal(edge)
  horizontalDistance([edge.start, edge.end]) == 10mm
}
```
### horizontal
`solver::horizontal(@input: Segment|[Segment|Point2d; 2+])`
```kcl
sketch001 = sketch(on = XY) {
  p0 = point(at = [var -0.04mm, var 2.3mm])
  horizontal([p0, ORIGIN])
}
```
### horizontalDistance
`solver::horizontalDistance(@points: [Segment|Point2d; 2], labelPosition?: Point2d)`
The distance is signed, so the order of the points matters: the value set with `==` equals the second point's X coordinate minus the first point's X coordinate.
- points: Two sketch points, or one sketch point and `ORIGIN`.
### line
`solver::line(start: Point2d, end: Point2d, construction?: bool): Segment`
### midpoint
`solver::midpoint(@input: Segment, point: Segment|Point2d)`
- point: May be a sketch point or `ORIGIN`.
### parallel
`solver::parallel(@input: [Segment; 2+])`
### perpendicular
`solver::perpendicular(@input: [Segment; 2+])`
Currently limited to two lines.
### point
`solver::point(at: Point2d): Segment`
- at: The point's position in the sketch's local 2D coordinate system.
### radius
`solver::radius(@points: Segment, labelPosition?: Point2d)`
- points: The arc or circle segment whose radius should match the value set with `==`.
```kcl
profile = sketch(on = XY) {
  base = line(start = [var -4mm, var 0mm], end = [var 4mm, var 0mm])
  arch = arc(start = [var 4mm, var 0mm], end = [var -4mm, var 0mm], center = [var 0mm, var 0mm])
  coincident([base.end, arch.start])
  coincident([base.start, arch.end])
  radius(arch) == 4mm
}

solid = extrude(region(segments = [profile.base, profile.arch]), length = 2)
```
### symmetric
`solver::symmetric(@input: [Segment; 2], axis: Segment)`
Supported homogeneous input pairs: - `Point` / `Point` - `Line` / `Line` - `CircularArc` / `CircularArc` - `Circle` / `Circle`
Symmetric `Line`s are at opposite angles (reflected across the axis). Symmetric `CircularArc`s have equal diameters and centers. Note that the `Symmetric` constraint does _not_ affect the position (i.e. the start and end points) of Lines or Arcs.
### tangent
`solver::tangent(@input: [Segment; 2])`
Supported input type pairs (unordered): - `Line` / `Circle` - `Line` / `CircularArc` - `Circle` / `Circle` - `Circle` / `CircularArc` - `CircularArc` / `CircularArc`
```kcl
profile = sketch(on = XY) {
  guideArc = arc(start = [var 0mm, var 2mm], end = [var 2mm, var 0mm], center = [var 2mm, var 2mm])
  tangentLine = line(start = [var 0mm, var 2mm], end = [var 0mm, var 4mm])
  tangent([tangentLine, guideArc])
  coincident([tangentLine.start, guideArc.start])
  line1 = line(start = [var 0mm, var 4mm], end = [var 2mm, var 0mm])
  coincident([guideArc.end, line1.end])
  coincident([tangentLine.end, line1.start])
}

solid = extrude(region(segments = [profile.guideArc, profile.tangentLine]), length = 2)
```
### vertical
`solver::vertical(@input: Segment|[Segment|Point2d; 2+])`
```kcl
sketch001 = sketch(on = XY) {
  p0 = point(at = [var 2.1mm, var -0.03mm])
  vertical([p0, ORIGIN])
}
```
### verticalDistance
`solver::verticalDistance(@points: [Segment|Point2d; 2], labelPosition?: Point2d)`
- points: Two sketch points, or one sketch point and `ORIGIN`. The value set with `==` equals the second point's Y coordinate minus the first point's Y coordinate, so the order of the points determines the sign.

## Deprecated sketch v1 (!dep; recognise in old code, never write): `solver::angle`

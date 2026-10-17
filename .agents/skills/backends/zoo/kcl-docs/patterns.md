# KCL 2 patterns

Verbatim excerpts from tested sources. `aq/<slug>/<file>` = `zoo.dev/aquarium/<slug>`; `book/<chapter>` = `zoo.dev/docs/kcl-book/<chapter>.html`. Excerpts assume `@settings(defaultLengthUnit = mm, kclVersion = 2.0)` plus the variables they reference.

## Parametric part function, mapped over inputs (book/map_reduce)
```kcl
fn cube(@offset) {
  sideLen = 10
  sketch001 = sketch(on = XY) {
    line1 = line(start = [var 0mm, var 0mm], end = [var 3.08mm, var 0mm])
    line2 = line(start = [var 3.08mm, var 0mm], end = [var 3.08mm, var -3.01mm])
    line3 = line(start = [var 3.08mm, var -3.01mm], end = [var 0mm, var -3.01mm])
    line4 = line(start = [var 0mm, var -3.01mm], end = [var 0mm, var 0mm])
    coincident([line1.end, line2.start])
    coincident([line2.end, line3.start])
    coincident([line3.end, line4.start])
    coincident([line4.end, line1.start])
    parallel([line2, line4])
    parallel([line3, line1])
    perpendicular([line1, line2])
    horizontal(line3)
    coincident([line1.start, ORIGIN])
    equalLength([line1, line2, line3, line4])
    fixed([line1.start, ORIGIN])
    distance([line1.start, line1.end]) == sideLen
  }
  hide(sketch001)
  return region(segments = [sketch001.line1, sketch001.line2])
    |> extrude(length = sideLen)
    |> translate(x = offset)
}

offsets = [0, 25, 50]
cubes = map(offsets, f = cube)
```
Rough `var` guesses, exact `==` constraints. Objects as inputs work the same: `fn cube(@params)` reading `params.x`.

## Dimensioned circle, extrude, tag the cap (aq/walkie-talkie/knob.kcl)
```kcl
knobSketch = sketch(on = XY) {
  knobCircle = circle(start = [var 0.25in, var 0in], center = [var 0in, var 0in])
  coincident([knobCircle.center, ORIGIN])
  diameter(knobCircle) == knobDiameter
}
knobRegion = region(segments = [knobSketch.knobCircle])
knobBlank = extrude(knobRegion, length = knobHeight, tagEnd = $knobEnd)
```

## Fillet cap edges via tags (aq/axial-fan/motor.kcl)
```kcl
motorBody = extrude(
  region001,
  length = 17,
  tagStart = $capStart001,
  tagEnd = $capEnd001,
)
  |> appearance(color = "#021b55")
  |> fillet(
       tags = [
         getCommonEdge(faces = [region001.tags.circle1, capStart001]),
         getCommonEdge(faces = [region001.tags.circle1, capEnd001])
       ],
       radius = 2,
     )
```

## Chamfer via opposite edge (book/fillets)
```kcl
chamferedCube = chamfer(extrudeCube, tags = [getOppositeEdge(regionCube.tags.line1)], length = 0.2)
```
`regionCube.tags.line1` is the wall grown from segment `line1`; `getOppositeEdge` gives its top edge.

## Countersunk hole on a tagged face (aq/countersunk-plate/main.kcl)
```kcl
plateBody = extrude(plateRegion, length = plateThickness, tagEnd = $topFace)

plateWithTopCountersink = hole::hole(
  plateBody,
  face = topFace,
  cutAt = [0, boltSpacing / 2],
  holeBottom = hole::flat(),
  holeBody = hole::blind(depth = plateThickness, diameter = boltDiameter),
  holeType = hole::countersink(angle = 90deg, diameter = boltDiameter * 2),
)
```
Feed the result into the next `hole::hole`; several at once: `hole::holes(cutsAt = […])`, `hole::holesLinear`.
`cutAt`/`cutsAt` are read in the target face's local frame, not global XY: on the `END` face of an XY extrusion `[a, b]` lands at global `(b, a)` (verified 2026-09-13, zoo 0.2.196; `smoke/parts/bracket` is the regression check). Probe one hole and read the centre of mass before placing a pattern.
`hole::flat()` is only safe when the blind depth consumes the whole wall (the floor is discarded). A planar blind floor must not use `hole::flat()` — see Engine limits.

## Revolve, radius set by construction line (book/sketch3d)
```kcl
circleSketch = sketch(on = XZ) {
  // Sketch a circle whose center is [20, 0].
  circle1 = circle(start = [var 0mm, var 1mm], center = [var 0mm, var 0mm])
  fixed([circle1.center, [20, 0]])

  // Use construction geometry to set the circle's radius to 1mm.
  vertical([circle1.start, circle1.center])
  line1 = line(start = [var 0mm, var 0mm], end = [var 0mm, var 1mm], construction = true)
  coincident([line1.start, circle1.center])
  coincident([line1.end, circle1.start])
  distance([line1.start, line1.end]) == 1mm
}

// Pick the region inside the circle
region001 = region(segments = [circleSketch.circle1])

// Revolve it around the center of the scene
revolve001 = revolve(region001, axis = Y)
```
Partial turn: `revolve(region001, axis = Y, angle = 360.0)` with a smaller angle (aq/torus/main.kcl).

## Sweep along a helix (aq/coilover-assembly/spring.kcl)
```kcl
springPath = helix(
  axis = Z,
  radius = springRadius,
  length = springLength,
  revolutions = springRevolutions,
  angleStart = 360,
  ccw = false,
)
```
```kcl
coiloverSpring = sweep(region001, path = springPath)
```
The profile is a circle sketched on `XZ`, its centre `springRadius` from the axis.

## Sweep along a sketched path (book/sketch3d)
```kcl
pathSketch = sketch(on = XZ) {
  line1 = line(start = [var 0mm, var 5.06mm], end = [var -5.02mm, var 4.93mm])
  vertical([line1.start, ORIGIN])
  arc1 = arc(start = [var -4.54mm, var 12.82mm], end = [var -5.02mm, var 4.93mm], center = [var -5.12mm, var 8.9mm])
  coincident([line1.end, arc1.end])
  tangent([line1, arc1])
}
```
```kcl
sweep(pillRegion, path = [pathSketch.line1, pathSketch.arc1])
```
Path plane (`XZ`) is perpendicular to the profile plane (`YZ`), and the path starts at the profile.

## Loft between a base sketch and an offset plane (book/sketch3d)
```kcl
// Sketch a circle, 10mm above the square.
circle = sketch(on = offsetPlane(XY, offset = 10mm)) {
  circle1 = circle(start = [var 0mm, var 1.5mm], center = [var 0mm, var 0mm])
  coincident([circle1.center, ORIGIN])
  vertical([circle1.start, circle1.center])
  distance([circle1.start, circle1.center]) == 1.5mm
}

// Pick out the right regions from each sketch.
squareRegion = region(segments = [square.line1, square.line2])
circleRegion = region(segments = [circle.circle1])

// Loft the square into the circle.
loft([squareRegion, circleRegion])
```
`loft` also accepts whole sketches: `twistedBlade = loft([rootProfile, tipProfile])` (aq/single-impeller-blade/main.kcl).

## Shell (aq/gingerbread-man-cookie-cutter/main.kcl)
```kcl
cutter = extrude(bodyRegion, length = thickness)
  |> shell(thickness = wallThickness, faces = [START, END])
```

## Mirror a half profile, then region by interior point (aq/gingerbread-man-cookie-cutter/main.kcl)
```kcl
bodyProfile = bodyHalf
  |> mirror2d(axis = Y)
  |> scale(x = scaleFactor, y = scaleFactor, z = 1)

bodyRegion = region(point = [0mm, 260mm], sketch = bodyProfile)
```

## Boolean subtract, gear bore (aq/herringbone-gear/main.kcl)
```kcl
gearHeight = 8
gearBody = gear::herringbone(
  nTeeth = 25,
  module = 1,
  pressureAngle = 14deg,
  helixAngle = 40deg,
  gearHeight,
)

boreSketch = sketch(on = XY) {
  bore = circle(start = [var 4mm, var 0mm], center = [var 0mm, var 0mm])
  coincident([bore.center, ORIGIN])
  radius(bore) == 4mm
}
boreBody = extrude(region(segments = [boreSketch.bore]), length = gearHeight)
herringboneGear = subtract(gearBody, tools = [boreBody])
hide(boreSketch)
```
`gear::*` needs `experimentalFeatures = allow`. `gearHeight,` passes a variable whose name matches the parameter.

Measured 2026-09-17 (`results/_spikes/gear-spur`, `gear::spur(nTeeth = 20, module = 2, pressureAngle = 20deg, gearHeight = 8)` under `kclVersion = 2.0`): it runs and exports; the STEP tip radius is exactly m(N+2)/2 = 22.0 and the tooth count is 20, but the root radius is 18.72 (dedendum ~0.64 m, not the standard 1.25 m, so the section area is 1300 mm² against 1217 for a standard tooth), there is no backlash or profile-shift parameter, and the tooth phase is not centred on +x. When a spec states addendum/dedendum, backlash, or tooth phase, build the involute from the equations (sample the flank from the base circle to the tip, mirror, pattern about the axis, then `rotate` for phase) instead of `gear::spur`. `zoo kcl analyze` reports the bounding box of a `gear::spur` body as 52.7 mm across for the 44 mm gear (control-point box); measure the exported STEP instead.

## Sketch on a face, extrude merges, then pattern (book/patterns)
```kcl
face001 = faceOf(base, face = END)
smallCircleSketch = sketch(on = face001) {
  circle1 = circle(start = [var -0.83mm, var 8.27mm], center = [var 0mm, var 7.79mm])
  vertical([circle1.center, ORIGIN])
  vertical([circle1.center, circle1.start])
}

// Extrude that circle into a small cylinder,
// then pattern it around.
region(segments = [smallCircleSketch.circle1])
  |> extrude(length = 2)
  |> patternCircular3d(
       instances = 6,
       axis = Y,
       useOriginal = true,
     )
```
Free-standing pattern: `translate(cube, z = 30)` then `|> patternCircular3d(instances = 12, axis = Y, center = [0, 0, 0], arcDegrees = 360deg, rotateDuplicates = false)`; linear: `|> patternLinear3d(instances = 2, distance = heatSinkDepth + fanHeight, axis = [-1, 0, 0])` (aq/cpu-cooler/main.kcl).

## Clone, transform, colour (book/transform_3d)
```kcl
extrude002 = clone(silverCube)
  |> translate(z = 10)
  |> rotate(roll = 45deg)
  |> appearance(color = "#00ff00", metalness = 80, roughness = 30)
```

## Custom plane (book/planes)
```kcl
customPlane = {
  origin = { x = 0, y = 1, z = 0},
  xAxis = { x = 1, y = 0, z = 0 },
  yAxis = { x = 0, y = 0, z = 1 },
}
```
Then `sketch(on = customPlane) { … }`. Both-ways extrude from a mid-plane: `pipeBody = extrude(ringRegion, length = -pipeLength, symmetric = true)` (aq/pipe/main.kcl).

## Multi-file assembly (aq/axial-fan/main.kcl)
```kcl
import "fan-housing.kcl" as fanHousing
import "motor.kcl" as motor
import "fan.kcl" as fan

// Produce the model for each imported part
fanHousing
motor
fan
```
Every part starts with `import * from "parameters.kcl"`; reusable parts expose `export fn pipe() { … }` factories (aq/pipe-flange-assembly).

## Design check (book/checking)
```kcl
wallMountingHoleDiameter = .625
wallMountLength = 2.25
assert(wallMountLength, isGreaterThanOrEqual = wallMountingHoleDiameter * 3, error = "This doesn't leave enough room for a hole. Either decrease hole diameter or increase wallMountLength")
```

## Dense coordinate profile: fitted arcs or adaptive polyline (opencad spike, docs/notes/profile-curves-spike.md)
Measured on the SPLEEN C1 airfoil (2 x 1001 table points): a 74-piece circular-arc fit (tolerance 0.001 mm, centres precomputed in Python) reproduces the table to p95 0.0007 mm / max 0.001 mm with 74 sketch segments; an RDP-adaptive polyline at 0.01 mm needs 105 `line` segments for p95 0.008 / max 0.010 mm. Feeding raw table points to `solver::controlPointSpline` does not interpolate them (control-polygon B-spline, max error 0.25 mm at 60 controls) and sketches above ~240 points per side stall the full program. Emit literal endpoints, keep each `end` byte-identical to the next `start`, no constraints needed:
```text
profile = sketch(on = XY) {
  e0000 = arc(start = [0mm, 0mm], end = [0.427175152413mm, -0.282804317698mm], center = [0.697786629931mm, 0.589979194365mm], direction = CCW)
  e0001 = line(start = [0.427175152413mm, -0.282804317698mm], end = [0.9mm, -0.6mm])
  // ... one piece per fitted arc/segment, closing back at e0000.start
}
airfoilRegion = region(segments = [profile.e0000, profile.e0001])
blade = extrude(airfoilRegion, length = span)
```
`direction = CW` for clockwise pieces (compute from the ordered sample triplet). Full example: docs/notes/profile-arcs-adaptive-0p001.kcl; fitting script: docs/notes/profile-fit-candidates.py.

## Engine limits (zoo 0.2.196)

Planar blind holes: `hole::holeAt` / `hole::hole` with `holeBottom = hole::flat()` builds a near-flat cone (sag ~1e-4 mm) whose degenerate apex the tessellator drops. The STEP keeps the face; the STL opens a ring of unpaired edges and `zoo kcl analyze` volume is short by z·A/3 (the missing disk in a divergence-theorem volume). Cut-extrude a circle, or `subtract` a cylinder, then `hide` the tool sketch:

```kcl
boreSketch = sketch(on = offsetPlane(XY, offset = floorZ)) {
  bore = circle(start = [var 1.5mm, var 0mm], center = [var 0mm, var 0mm])
  coincident([bore.center, ORIGIN])
  diameter(bore) == holeDiameter
}
boreCut = extrude(region(segments = [boreSketch.bore]), length = holeDepth)
body = subtract(body, tools = [boreCut])
hide(boreSketch)
```

Loft-versus-loft subtract: a boolean between a loft and a near-parallel offset of the same loft fails with `Batch edit result is not valid` (degenerate surface-surface intersection). Prefer `shell()` on the lofted body, a prismatic/extruded tool, or split the boolean. Prove the risky boolean in isolation before building on it.

Construction geometry: do not sketch datum axes (planes need no visible geometry). `hide(region)` every construction region so `zoo kcl analyze` bbox matches the finished STEP. `hide` does not take sketch blocks; leftover sketches fold their plane extents into the engine box (a vertical XZ sketch reads as a +Y "flagpole").

## Kernel-safe construction for large parts (opencad decomposition, 2026-09-19)

Learned on the Voron Stealthburner duct (five modules, two of which failed `BooleanUnion`/`BooleanSubtract` on every edit) and the Prusa extruder front:

- **One union of tools, one subtract.** Build every tool of a feature family as its own solid, `union` the tools into one, then `subtract` once from the stock. A chain of ten small subtracts each re-triangulates the whole body and the eighth fails where the first eight succeeded.
- **Never let a tool face coincide with a stock face.** Overrun every cut 0.01-0.05 mm past the face it exits through, into air or outside the envelope; start blind cuts 0.01 mm above the entry face. Coincident faces are the most common `Batch edit result is not valid`.
- **Keep 0.1 mm from other modules' faces.** In a decomposed part every module owns a region (`partition.yaml`); a tool that touches another module's geometry creates a sliver the later module's boolean cannot resolve. If a feature needs material outside the region, it is a partition problem, not something to cut through.
- **Ducts and cavities: air volume, then shell.** Model the air path as a solid (sweep or loft of the channel section), `union` the wall stock around it, then `subtract` the air solid once; or build the wall as `shell()` of the air body. Sculpting a channel by subtracting many overlapping boxes leaves internal faces that break the next boolean and leak the passage check.
- **Ports open inside their plug boxes.** A contract passage is judged with `plugs` sealing the mouths: every port the module cuts must open within the plug box and the air path must reach both probe points. A port 0.5 mm outside its plug box reads as `reaches_exterior`.
- **Prove the risky boolean in isolation.** In the module's scratch main, apply the module to the bare datum first; when the composed part fails, `python -m opencad kcl-bisect <main.kcl>` names the first `|>` step whose removal makes the file execute.
- **Fillets and chamfers last, and only on tagged edges.** A fillet before a subtract that intersects it fails; move all edge treatments to the end of the module (or to the integrate turn) and tag the edges explicitly.

Engine refusals seen on the Prusa extruder front (2026-10-15, zoo 0.2.204): `The Zoo engine cannot handle this 3D subtraction yet` / `union yet`, `Batch edit result is not valid`, `Internal engine error on request`. Try these in order before restructuring a module; each one cleared a real failure there and none changes a contract value:

- **Pass a boolean tolerance.** `subtract(stock, tools = [cutter], tolerance = 0.001mm)` (also `union`, `intersect`) let a stepped keyhole cutter build where several surface intersections met near one shoulder. On its own it did not fix a coplanar shoulder; combine it with the next two.
- **Build the cutter in a temporary frame, then rotate it into place.** Sketch a horizontal or tilted bore cutter on `XY`, extrude it along +Z, then `rotate` it into place with an exact angle (`90deg`, not a computed `atan2`) and `translate` it. A cut that failed when sketched on a face-local or offset plane composed once rebuilt this way. The XY sketch also keeps stray `XZ`/`YZ` sketch extents out of the engine bounding box.
- **Overlap a tool past a tangent or coplanar face, or change the tool order.** Move the tool face 0.002-0.02 mm into the solid it meets (for example a gusset end 0.02 mm inside a lug cylinder). If the union still fails, fold the tangent pieces into one cutter first: subtract the protected lug from the web cutter, then the gusset, then cut the stock once.

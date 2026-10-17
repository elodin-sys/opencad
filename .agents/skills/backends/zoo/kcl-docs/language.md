# KCL 2 language guide

Syntax and semantics only; API signatures live in `std/`. Deep dives: `zoo.dev/docs/kcl-lang/<page>` (page named per section) and `zoo.dev/docs/kcl-book/<chapter>.html`.

## File skeleton
- First statement (comments may precede): `@settings(defaultLengthUnit = mm, kclVersion = 2.0)`. Add `experimentalFeatures = allow` to use `!exp` items. `defaultAngleUnit` is deprecated: suffix angles (`90deg`).
- Then imports, named parameters, sketches, features. The last expression is the module's value when another file imports it.
- `name = value` declares a constant; redeclaration is an error. Comments: `//`.

## Values (`types`, `numeric`, `arrays`, `enums`)
- Numbers carry units. Suffixes: `mm cm m in ft yd`, `deg rad`, `_` unitless. A bare literal takes the file default and its kind (length/angle/count) stays ambiguous.
- Types: `number(mm)` or shorthand `mm`; `number(Length)`, `number(Angle)`, `number(Count)` (= `number(_)`); bare `number` accepts anything.
- Calls convert compatible units (`2in` into a `number(mm)` parameter is fine; `90deg` there is an error). Arithmetic converts when it can; when it cannot, ascribe: `(x * y): mm`. Ascription never rescales (`2mm: in` is `2in`).
- No area/volume units: convert every operand to one unit before multiplying. `10in * 25.4` is `254in`, not mm; use `std::units` conversions. `PI` forces ascription: `radius = (circumference / (2 * PI)): mm`.
- `bool`; `string` (`'a'` or `"a"`, `+` concatenates, `==` exact and case-sensitive).
- Arrays `[a, b]`, index `arr[0]`; types `[T]`, `[T; n]`, `[T; 1+]`. Ranges `[0..3]` inclusive, `[3..<10]` excludes end; bounds share units.
- Objects `{ a = 0, b = "thing" }`, access `myObj.a`.
- Enums `!exp`, top level only: `type Fit { | Loose | Normal | Press }`; value `Fit::Press`; only `==`/`!=` act on them (cross-enum or cross-type comparison is an error); `Fit::Press: string` gives `"Press"`; usable as a parameter type.
- `ImportedGeometry` is not `Solid`: no booleans or sketch-on-face on imports. Rebuild natively or keep the import as a reference.

## Operators (`arithmetic`)
`+ - * / % ^`; logic `& | !`; comparison `== != < > <= >=`. Unary `-` on a plane or axis flips it (`-XY` has normal −Z). On solids: `a + b` or `a | b` union, `a - b` subtract, `a & b` intersect.

## Functions and pipelines (`functions`, `pipelines`)
- `fn name(@first, kw1, kw2): Type { return … }`. Only the first parameter may be unlabeled (`@`); every other argument is passed by keyword. Types are optional (`theta: number(Angle)`); functions are values, anonymous ones too: `map(xs, f = fn(@x) { return x * x })`, `reduce(xs, initial = 0, f = fn(@i, accum) { return i + accum })`.
- `x |> f(%)` is `f(x)`; `%` fills the `@` slot and may be omitted: `|> f(kw = 1)`.
- `if c { a } else if d { b } else { e }` is an expression; `fail("msg")` aborts and returns `never`.
- Point-and-click cannot edit sketches inside function bodies: keep GUI-edited sketches top level. Identical copies: `clone` or a pattern, not a function. Function = parametric but re-executes per call; `clone` = O(1) exact duplicate.

## Sketch blocks (`sketches`)
```kcl
width = 40mm
height = 24mm

profile = sketch(on = XY) {
  bottom = line(start = [var 0mm, var 0mm], end = [var 40mm, var 0mm])
  right = line(start = [var 40mm, var 0mm], end = [var 40mm, var 24mm])
  top = line(start = [var 40mm, var 24mm], end = [var 0mm, var 24mm])
  left = line(start = [var 0mm, var 24mm], end = [var 0mm, var 0mm])

  coincident([bottom.end, right.start])
  coincident([right.end, top.start])
  coincident([top.end, left.start])
  coincident([left.end, bottom.start])
  horizontal(bottom)
  horizontal(top)
  vertical(right)
  vertical(left)
  horizontalDistance([bottom.start, bottom.end]) == width
  verticalDistance([bottom.start, left.start]) == height
  coincident([bottom.start, ORIGIN])
}
```
- Inside `sketch(on = plane | face) { }` the solver module is unprefixed. Segments are bindings; outside, address them as `profile.bottom`, `profile.bottom.start`, `.end`, `.center`.
- `var 40mm` is a solver starting guess and must be a literal. Never `var width` or `var (w / 2)`; dimensions come from constraints (`horizontalDistance`, `verticalDistance`, `distance`, `radius`, `diameter`, `angle`, `angleDimension`) with `== expr`.
- Geometric constraints: `coincident`, `horizontal`, `vertical`, `parallel`, `perpendicular`, `equalLength`, `equalRadius`, `tangent`, `symmetric`, `midpoint`, `fixed`. Anchor once (`coincident([p, ORIGIN])`) and relate the rest; repeated `fixed` points over-constrain and resist editing.
- A circle's start point floats: pin it (`vertical([c.start, c.center])`) before dimensioning `radius(c) == r`.
- `construction = true` segments guide without joining the profile.
- Arcs sweep counterclockwise from start to end; take the other way with `direction = CW`, not by swapping endpoints.
- Features consume a `region(segments = [first, second])` traced from a closed boundary; a lone closed segment (circle) is passed by itself. `direction = CW` or `intersectionIndex` disambiguate multi-segment boundaries; fix the boundary rather than falling back to `region(point = …)`. A region used by one feature is spent; call `region(...)` again for the next.
- `hide(sketch)` or `hide([a, b])` removes finished sketches from the scene.

## Solids (`sketch-on-face`, book `sketch3d`, `fillets`, `csg`, `patterns`)
- Create from regions: `extrude` (`length`, `symmetric`, `bidirectionalLength`, `to`, `twistAngle`), `revolve(axis = Y, angle = 360)`, `sweep(path = helix or [segments])`, `loft([regionA, regionB])`.
- Edge and face handles: tag caps at creation (`tagStart = $capStart`, `tagEnd = $capEnd`); walls are `region.tags.line1`; edges via `getCommonEdge(faces = [a, b])`, `getOppositeEdge(tag)`, `getNextAdjacentEdge`, `getPreviousAdjacentEdge`. Prefer `body.faces.capEnd` and `region.tags.line1` over bare tag identifiers and over `START`/`END`, which are ambiguous and leak across scopes.
- Sketching on `faceOf(solid, face = END)` and extruding extends or cuts that solid: one body, no boolean needed. For a separate body sketch on `planeOf(solid, face = END)` or pass `method = NEW`. Prefer the merge when one solid is intended.
- Booleans (`union`, `subtract`, `intersect`) consume their inputs: chain each result into the next call, never reuse a consumed variable. Coplanar booleans are unsupported by the engine.
- Planes: `XY`, `XZ`, `YZ`, negated `-XZ`, `offsetPlane(XY, offset = 10mm)`, or `{ origin = {x, y, z}, xAxis = {…}, yAxis = {…} }`.
- Transforms `translate(x =, y =, z =)`, `rotate(roll =, pitch =, yaw =)`, `scale`; `clone(solid)` then transform for copies; `patternLinear3d`, `patternCircular3d`, `patternTransform(transform = fn(@i) { … })`; `useOriginal = true` when the target was sketched on an extrusion.
- `appearance(color = "#rrggbb", metalness, roughness, opacity)`; `assert(x, isEqualTo | isGreaterThan | isGreaterThanOrEqual | isLessThan = …, tolerance, error = "…")`; `assertIs(bool)`.

## Modules and imports (`modules`, `foreign-imports`)
- `export fn f(@x) { … }` and `export size = 5mm`; `import f, g as h from "util.kcl"`; `import * from "parameters.kcl"` pulls every export (the shared-parameters idiom); whole module `import "part.kcl"` binds `part` (`as name` to rename; required when the filename has `-` or leading `_`). From a subdirectory only `dir/main.kcl` is importable; `export import x from "inner.kcl"` re-exports.
- Imports are top level only and must be acyclic: parameters import nothing; utilities import parameters; parts import both; `main.kcl` imports parts. A module's value is its last expression and must be one object (`union` several).
- A file imported twice renders once; use `clone` for a second instance.
- Foreign files: `import "x.step" as x` (`fbx`, `gltf`/`glb`, `obj`, `ply`, `sldprt`, `step`/`stp`, `stl`); `@(lengthUnit = ft, coords = opengl)` on the import sets unit and frame for `obj`/`ply`/`stl` (default `mm`, `zoo` frame: forward −Y, up +Z). Native Design Studio only. Reading starts a background render; the first transform on the value blocks, so defer transforms and put heavy imports in their own module. Modules execute in parallel; a function only costs when called, so call early or from another module.

## Settings (`settings`, `settings/project`)
- `@settings`: `defaultLengthUnit`, `kclVersion` (`1.0`, `2.0`, `"3.0-preview"`), `experimentalFeatures` (`allow` | `warn` | `deny`). Overrides `project.toml` (`[settings.modeling] base_unit = "in"`, written by the app; do not hand-edit).
- `"3.0-preview"` governs the whole execution: `return` exits immediately; `if` branches scope their variables; `a[b]` evaluates `a` first; `fillet`/`chamfer` run in order, so look up an edge before the fillet that consumes it and store it in a variable.

## Known issues (`known-issues`)
- Imported files are read-only `ImportedGeometry`.
- Coplanar CSG booleans fail.
- KCL 1.0 shuffled region tags; `kclVersion = 2.0` fixes it.

## Legacy sketch v1 (recognise in old code, never write)
```kcl
startSketchOn(XZ)
  |> startProfile(at = [0, 0])
  |> line(end = [3, 4])
  |> line(end = [10, 10])
  |> line(end = [-13, -14])
  |> close()
```
Also `xLine`, `yLine`, `angledLine`, `tangentialArc`, `arc(angleStart, angleEnd, radius)`, `circle(center, radius)`, `rectangle`, `polygon`, `subtract2d`, segment tags `$seg` read back with `segLen`, `segAng`, `lastSegX`, `profileStart`. KCL 2 replaces the pipeline with a sketch block plus `region(segments = […])`.

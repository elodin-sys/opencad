---
name: kcl-docs
disable-model-invocation: true
description: KCL 2 language and standard-library reference for Zoo/KittyCAD parametric CAD code. Use when writing, editing, or reviewing .kcl files, sketch blocks and constraints, extrude/revolve/sweep/loft, fillets and chamfers, holes, patterns, booleans, modules and imports, or when a KCL function signature, unit rule, or KCL error needs checking.
---
# kcl-docs

## Must-knows
1. First statement: `@settings(defaultLengthUnit = mm, kclVersion = 2.0)`; add `experimentalFeatures = allow` only for items flagged `!exp`.
2. Geometry lives in `sketch(on = XY) { … }` blocks. `var 10mm` is a literal solver guess; real dimensions are `== expr` constraints. `var width` is an error.
3. Features take `region(segments = [first, second])`; a circle alone for one closed loop. A region is spent by the feature that uses it.
4. `union`/`subtract`/`intersect` consume their inputs: pass each result forward. Coplanar booleans fail.
5. Sketch on `faceOf(solid, face = END)` and extrude to merge into that solid; `planeOf(...)` or `method = NEW` for a separate body.
6. Handles: `tagEnd = $cap` at extrude time, walls as `region.tags.line1`, edges via `getCommonEdge`/`getOppositeEdge`; avoid bare `START`/`END`.
7. Units ride on literals (`5mm`, `90deg`); there are no area/volume units, so ascribe `(x * y): mm` when arithmetic loses them.
8. Never write legacy sketch v1 (`startSketchOn`, `startProfile`, `|> line(end = …)`, `close()`); only recognise it in old files.
9. Identical copies: `clone` or `pattern*3d`; parametric variation: a `fn`.
10. Guard intent with `assert(x, isGreaterThan = …, error = "…")`, then verify through zoo-tooling.

## Files
- `language.md` (2.4k tok): syntax, values and units, sketch blocks, solids, modules, settings, known issues, legacy recognition. Read once per task.
- `std/index.md` (3.6k): one line per std item, grouped by module. Start here to find a function.
- `std/<module>.md`: typed signatures, arg semantics, one KCL 2 example. `sketch` (extrude, revolve, sweep, loft, region), `solver` (constraints), `solid` (fillet, chamfer, shell, booleans, patterns), `hole`, `transform`, `std` (assert, clone, helix, offsetPlane), `math`, `units`, `array`, `string`, `gdt`, `gear`, `view`, `types`.
- `patterns.md` (2.2k): 19 verbatim idioms from tested sources, hole pattern to multi-file assembly.

Full pages: `zoo.dev/docs/kcl-lang/<page>`, `zoo.dev/docs/kcl-std/functions/std-<module>-<name>`. Worked models: the kcl-examples skill.

## Workflow
Find the function in `std/index.md`, open its module page, copy the nearest idiom from `patterns.md` or a sample, write the file, then format, lint, execute, snapshot, and measure with zoo-tooling before claiming the geometry is right.

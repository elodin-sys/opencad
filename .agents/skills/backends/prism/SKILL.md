---
name: prism
disable-model-invocation: true
description: Worker pack for the prism backend (Prism's managed python-env: build123d 0.11, navier_cad, bd_warehouse; algebra mode, millimetres) covering the part and assembly-source contract, style, call signatures, the navier_cad vocabulary and the verify critics. Read before writing or correcting parts/prism/<name>/main.py.
---

# prism (opencad backend)

Read this before writing `parts/prism/<part>/main.py`. The part runs in Prism's managed python-env (build123d **0.11.x**,
`navier_cad` 0.1, `bd_warehouse` 0.2, OCP 7.9), a separate interpreter from the repository `.venv` (build123d 0.12). Algebra mode
first. **Millimetres.**

## Units: millimetres, not metres

Prism's standalone code-cad skill authors in metres for its FEM pipeline. This pipeline does not: the contract is in mm, the
evaluator measures the exported STEP in mm, edit tests rewrite the contract parameters as literal mm constants, and the
`envelope`, `mass_properties` and `features` gates are judged in mm. Write `plateWidth = 80.0`, never `0.08`. A part authored
in metres fails `envelope` by a factor of 1000. The `navier_cad` helpers are unit-agnostic geometry: pass them millimetres.

## Deliverable

```python
from build123d import Align, Box, Cylinder, Location, Compound

plateWidth = 80.0
assert plateWidth > 0, "infeasible: plateWidth must be positive"
plate = Box(plateWidth, plateHeight, plateThickness, align=(Align.MIN, Align.MIN, Align.MIN))
result = plate - tool
```

`result` is a `Part`, `Solid` or `Compound`. No file IO. No `materials`, `views` or `export_*` calls: the runner reads `result`
only, and the pipeline tessellates, renders and exports the STEP itself.

Multi-solid contracts (`acceptance.solid_count` > 1) keep each body separate and hand them over together:

```python
result = [base, lid]            # or: result = Compound([base, lid])
```

`base + lid` fuses touching bodies into one solid and fails `solid_count`; every solid in the list/Compound is exported.

## Imports

`build123d` (`from build123d import *`, explicit names, or `import build123d as bd`), `math`, `navier_cad.<module>` and
`bd_warehouse` (its parts are millimetres, which matches this pipeline). Nothing else: `OCP`, `collections`, `numpy` and any
other module fail `source_hygiene`. Never `navier_cad.cache` (`cached_part` writes under the working directory),
`navier_cad.checks`, `navier_cad.shapes.load_step` or `import_step` outside assembly orders.

## navier_cad vocabulary (prefer it over raw sweeps, lofts and fillets)

Each returns a valid positive-volume solid or raises a `ValueError` naming what to change. Signatures are exact; do not probe
them with `dir()` or `help()`.

- `blends.fuse_all(base, tools, what="fuse_all") -> Solid` — one fuse for a whole array instead of `body += tool` in a loop.
- `blends.fillet_safe(shape, edges, radius, *, min_radius=None) -> (Solid, BlendReport)` and
  `blends.chamfer_safe(shape, edges, length, *, min_length=None)` — back off per edge group and report it; never wrap a
  `fillet` in a bare `try/except`. `blends.blend_union(a, b, radius)` fillets only the joint; `blends.weld_bead(a, b, size)`.
- `sweeps.sweep_profile(profile, path, *, frame=Frame.AUTO, twist_deg=0.0)` (draw the profile in local XY at the origin; it is
  placed at the path start), `sweeps.pipe(path, outer_radius, wall=None)`, `sweeps.bent_tube(points, bend_radius, outer_radius,
  wall=None)` (real arc bends; bend radius >= 1 x OD), `sweeps.loft_sections(sections, *, ruled=False)`.
- `shapes.tube(ro, ri, h, at=None)`, `shapes.cylinder_along(start, end, radius)`, `shapes.pipe_between(start, end, ro, wall)`,
  `shapes.beam_between(start, end, w, d)`, `shapes.rounded_path(points, r) -> Wire`, `shapes.ring_positions(count, radius, phase_deg=0)`.
- `curves.spline_through(points, start_tangent=None, end_tangent=None) -> Wire`, `curves.helix(pitch, height, radius, plane=Plane.XY, *, lefthand=False)`,
  `curves.spiral(r_start, r_end, turns, plane=Plane.XY, *, kind=SpiralKind.ARCHIMEDEAN, rise=0.0)`, `curves.offset_curve(wire, distance)`.
- `profiles.rounded_rect(width, height, radius, plane=Plane.XY) -> Wire`, `profiles.slot(length, width, plane=Plane.XY)`,
  `profiles.closed_spline(points)`, `profiles.naca4(code, chord, plane=Plane.XY, *, twist_deg=0.0, pivot=0.25, n=40)`.
- `patterns.linear(count, step, start=(0, 0, 0))`, `patterns.polar(count, radius, phase_deg=0.0)`, `patterns.grid(nx, ny, dx, dy, *, centred=True)`,
  `patterns.along_path(path, count, *, include_ends=True)` — all `-> list[Location]`, so `[loc * tool for loc in polar(6, 20.0)]`.

## Assemblies

An assemble work order imports the two provided STEP bodies (only `inputs/<body>.step`), places them, and hands both over:

```python
from pathlib import Path
from build123d import import_step, Location

here = Path(__file__).resolve().parent
one = import_step(here / "inputs" / "body_one.step")
two = import_step(here / "inputs" / "body_two.step")
placed = one.move(Location((tx, ty, tz)))
result = [placed, two]
placements = {
    "body_one": [[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]],
    "body_two": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
}
```

`placements` is a 4×4 row-major millimetre matrix per body; the runner writes `placements.json` beside the STEP. Use
build123d's `import_step` (millimetres), not `navier_cad.shapes.load_step` (it switches the reader to metres). Do not import
anything under `truth/`.

## Style

- Algebra (`a - b`, `a + b`) by default. Builders only when clearer.
- `align=(Align.MIN, Align.MIN, Align.MIN)` when the contract origin is a min corner.
- Select with `faces().sort_by(Axis.Z)[-1]` or `filter_by`. Never a bare creation-order index.
- Batch tools into one `Compound`, then one subtraction (or `fuse_all` the tools first). Overrun a cutter 0.01–0.05 mm past the
  face into air; never leave a tool face coincident with a stock face (`BRep_API: command not done` is almost always that).
- Use the **exact** contract parameter names (`cornerRadius`, not `filletRadius`). Do not import STL or reference meshes.
- Blockout: if the volume band is much smaller than the AABB (e.g. benchy), do not `Box` the envelope; a hull-like solid must
  still touch all six faces.
- Fair hulls: `loft([...], ruled=False)` (or `sweeps.loft_sections`) with `Spline`/`ThreePointArc` section wires of equal edge
  count. Ruled polygon lofts print as flat facets. Symmetric parts are one half mirrored (`mirror(..., Plane.XZ)`) or verified
  with the `quick` symmetry line; a non-ruled spline loft can fold on one side, so read the stern and bow quarters in
  `quick-views.png`.
- Memory: an engine call may hold at most the engine memory budget (8 GB unless `OPENCAD_ENGINE_MEM_GB` says otherwise); a
  build past it is killed and fails as `memory`, the model's failure. Keep sources parametric (at most 4000 lines and 6000
  numeric literals across the part's files): a surface is a few sections or splines driven by named parameters, never point
  lists traced from a reference mesh.

## build123d 0.11 traps

- `shape.is_valid` is a property, not a method.
- `a & b` returns `None` for disjoint shapes and raises on an empty compound.
- `shape.moved(...)` takes a `Location`: `shape.moved(Location((x, y, z)))` or `Pos(x, y, z) * shape`.
- `Compound([...])` takes a list; `Compound(solid)` crashes with `'Solid' has no attribute 'IsNull'`. `shape.solids()` is a
  `ShapeList`: wrap it in `Compound(...)` before `.bounding_box()`.
- Thin walls on a loft or sweep: loft the outer and the inner profiles and subtract; `offset`/`offset_3d` on a lofted solid
  usually fails.
- `solid - face` raises "Dimensions ... inconsistent": extrude the face first.
- `align=` takes `Align.MIN/CENTER/MAX` (or a tuple of them), never 0 or None.
- `Cone(bottom_radius, top_radius, height)` puts the first radius at −Z; swapped arguments build a plausible inverted part.
- Do not call `.mesh()` on `result`. The critic tessellates the STEP itself.

## Decomposed parts

When the pipeline decomposes a part, `parts/prism/<part>/` holds `params.py` (every contract parameter as a top-level float),
`datum.py` (`datum` = the envelope `Part`) and one `<group>.py` per feature group with `def apply(body)`; `main.py` composes
them (`result = apply_b(apply_a(datum))`). Import parameters by name (`from params import plateWidth`; `ruff check` rejects
`import *`) and never redeclare them. The work-order brief carries the exact recipe and the pre-written scratch main for the critic.

## Call signatures (build123d 0.11)

`inspect.signature` of the installed 0.11 callables (`cls.__init__` for classes). Do not read the library source or call
`inspect.signature`.

- `extrude(to_extrude=None, amount=None, dir=None, until=None, target=None, both=False, taper=0.0, clean=True, mode=Mode.ADD)`
- `revolve(profiles=None, axis=Axis.Z, revolution_arc=360.0, clean=True, mode=Mode.ADD)`
- `loft(sections=None, ruled=False, clean=True, mode=Mode.ADD)`
- `sweep(sections=None, path=None, multisection=False, is_frenet=False, transition=Transition.TRANSFORMED, normal=None, binormal=None, clean=True, mode=Mode.ADD)`
- `fillet(objects, radius)`
- `chamfer(objects, length, length2=None, angle=None, reference=None)`
- `mirror(objects=None, about=Plane.XZ, mode=Mode.ADD)`
- `split(objects=None, bisect_by=Plane.XZ, keep=Keep.TOP, mode=Mode.REPLACE)`
- `offset(objects=None, amount=0, openings=None, kind=Kind.ARC, side=Side.BOTH, closed=True, min_edge_length=None, mode=Mode.REPLACE)`
- `make_hull(edges=None, mode=Mode.ADD)`
- `make_face(edges=None, mode=Mode.ADD)`
- `Circle(radius, arc_size=360.0, align=(Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Rectangle(width, height, rotation=0, align=(Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `RectangleRounded(width, height, radius, rotation=0, align=(Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Polyline(*pts, close=False, mode=Mode.ADD)`
- `Spline(*pts, tangents=None, tangent_scalars=None, periodic=False, mode=Mode.ADD)`
- `CenterArc(center, radius, start_angle, arc_size, mode=Mode.ADD)`
- `RadiusArc(start_point, end_point, radius, short_sagitta=True, mode=Mode.ADD)`
- `ThreePointArc(*pts, mode=Mode.ADD)`
- `Cylinder(radius, height, arc_size=360, rotation=(0, 0, 0), align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Cone(bottom_radius, top_radius, height, arc_size=360, rotation=(0, 0, 0), align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Box(length, width, height, rotation=(0, 0, 0), align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Sphere(radius, arc_size1=-90, arc_size2=90, arc_size3=360, rotation=(0, 0, 0), align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Pos(*args, **kwargs)` — call as `Pos(x, y, z)`
- `Location(*args, **kwargs)` — call as `Location((x, y, z))`
- `Compound(obj=None, label="", color=None, material="", joints=None, parent=None, children=None)`

A positive `extrude` taper shrinks the top of a sketch extruded along +Z. `fillet` edges come from
`part.edges().filter_by(GeomType.LINE)` or `part.edges().group_by(Axis.Z)[0]`, never a bare index. `mirror(..., Plane.YZ)`
reflects across x = 0; `Plane.XZ` reflects across y = 0.

When the contract has `acceptance.symmetry`, build one quadrant (or half), fillets included, and mirror it across each plane.
Do not import `OCP` to split or merge faces.

Tangent hull of circles: `make_hull([(Pos(x, y) * Circle(r)).edges() for x, y, r in circles])`. `make_hull` takes edges, not faces.

## Verify

`.venv/bin/ruff format --check`, `.venv/bin/ruff check` (the repository's pinned ruff; PATH may hold another version that
formats differently), then `python -m opencad quick main.py --contract designs/<part>/contract.yaml --backend prism`, which
builds the part in Prism's interpreter and measures the STEP with OpenCascade. Engine calls go through the ledger wrapper the
brief prints (`python -m opencad engine --backend prism --ledger <order>/engine-ledger.jsonl -- analyze <entry>`).

The `prism_cad_run` tool is not a critic here: it reads a script as metres, writes `<script>.step` beside it, and checks
nothing the gates check. If you use it at all, pass an inline `script` (`checks: "fast"`, `skip_mesh: true`) to probe one
feature; never point it at `main.py`.

Introductory examples: `sources/build123d/examples/` after `scripts/fetch_sources.py --backend build123d` (0.12 examples;
the 0.11 differences above still apply).

---
name: build123d
disable-model-invocation: true
description: Worker pack for the build123d backend (pinned 0.12, algebra mode) covering the part and assembly-source contract, style, call signatures and the verify critics. Read before writing or correcting parts/build123d/<name>/main.py.
---

# build123d (opencad backend)

Read this before writing `parts/build123d/<part>/main.py`. Pinned build123d 0.12.x. Algebra mode first. Millimetres.

## Deliverable

```python
from build123d import Align, Box, Cylinder, Location, Compound

plateWidth = 80.0
assert plateWidth > 0, "infeasible: plateWidth must be positive"
plate = Box(plateWidth, plateHeight, plateThickness, align=(Align.MIN, Align.MIN, Align.MIN))
result = plate - tool
```

`result` is a `Part`, `Solid` or `Compound`. No file IO.

Multi-solid contracts (`acceptance.solid_count` > 1) keep each body separate and hand them over together:

```python
result = [base, lid]            # or: result = Compound([base, lid])
```

`base + lid` fuses touching bodies into one solid and fails `solid_count`; every solid in the list/Compound is exported.

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

`placements` is a 4×4 row-major millimetre matrix per body; the runner writes `placements.json` beside the STEP. `RevoluteJoint` / `RigidJoint.connect_to` is optional — if you use it, still assign `result` and `placements`. Do not import anything under `truth/`.

## Style

- Algebra (`a - b`, `a + b`) by default. Builders only when clearer.
- `align=(Align.MIN, Align.MIN, Align.MIN)` when the contract origin is a min corner.
- Select with `faces().sort_by(Axis.Z)[-1]` or `filter_by`. Never a bare creation-order index.
- Batch tools into one `Compound`, then one subtraction. Overrun a cutter 0.01–0.05 mm past the face into air; never leave a tool face coincident with a stock face (`BRep_API: command not done` is almost always that).
- Use the **exact** contract parameter names (`cornerRadius`, not `filletRadius`). Algebra examples: `sources/build123d/examples/*_algebra.py`. Do not import STL or reference meshes.
- Blockout: if the volume band is much smaller than the AABB (e.g. benchy), do not `Box` the envelope; a hull-like solid must still touch all six faces.
- Fair hulls: `loft([...], ruled=False)` with `Spline`/`ThreePointArc` section wires of equal edge count. Ruled polygon lofts print as flat facets. Symmetric parts are one half mirrored (`mirror(..., Plane.XZ)`) or verified with the `quick` symmetry line; a non-ruled spline loft can fold on one side, so read the stern and bow quarters in `quick-views.png`.
- Memory: an engine call may hold at most the engine memory budget (8 GB unless `OPENCAD_ENGINE_MEM_GB` says otherwise); a build past it is killed and fails as `memory`, the model's failure. Keep sources parametric (at most 4000 lines and 6000 numeric literals across the part's files): a surface is a few sections or splines driven by named parameters, never point lists traced from a reference mesh.

## Decomposed parts

When the pipeline decomposes a part, `parts/build123d/<part>/` holds `params.py` (every contract parameter as a top-level float), `datum.py` (`datum` = the envelope `Part`) and one `<group>.py` per feature group with `def apply(body)`; `main.py` composes them (`result = apply_b(apply_a(datum))`). Import parameters by name (`from params import plateWidth`; `ruff check` rejects `import *`) and never redeclare them. The work-order brief carries the exact recipe and the pre-written scratch main for the critic.

## Call signatures (build123d 0.12)

Parameters below are `inspect.signature` of the pinned 0.12 callables (`cls.__init__` for classes). Do not read the library source or call `inspect.signature`.

- `extrude(to_extrude, amount, dir=None, until=None, target=None, both=False, taper=0.0, clean=True, mode=Mode.ADD)`
- `fillet(objects, radius)`
- `chamfer(objects, length, length2=None, angle=None, reference=None)`
- `mirror(objects=None, about=Plane.YZ, mode=Mode.ADD)`
- `make_hull(edges=None, mode=Mode.ADD)`
- `make_face(edges=None, mode=Mode.ADD)`
- `loft(sections=None, ruled=False, clean=True, mode=Mode.ADD)`
- `Circle(radius, arc_size=360, align=(Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Rectangle(width, height, rotation=0, align=(Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `RectangleRounded(width, height, radius, rotation=0, align=(Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Polyline(*pts, close=False, mode=Mode.ADD)`
- `CenterArc(center, radius, start_angle, arc_size, mode=Mode.ADD)`
- `RadiusArc(start_point, end_point, radius, short_sagitta=True, mode=Mode.ADD)`
- `ThreePointArc(*pts, mode=Mode.ADD)`
- `Cylinder(radius, height, arc_size=360, rotation=(0, 0, 0), align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Cone(bottom_radius, top_radius, height, arc_size=360, rotation=(0, 0, 0), align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Box(length, width, height, rotation=(0, 0, 0), align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)`
- `Pos(*args, **kwargs)` — call as `Pos(x, y, z)`
- `Location(*args, **kwargs)` — call as `Location((x, y, z))`
- `Compound(obj=None, label="", color=None, material=None, joints=None, parent=None, children=None)`

A positive `extrude` taper shrinks the top of a sketch extruded along +Z. Draft that leans inward toward +Z is `taper=draftAngle` on a sketch at z = 0. There is no `twist` parameter.

`fillet` edges come from `part.edges().filter_by(GeomType.LINE)` or `part.edges().group_by(Axis.Z)[0]`, never a bare index. `mirror(..., Plane.YZ)` reflects across x = 0; `Plane.XZ` reflects across y = 0.

When the contract has `acceptance.symmetry`, build one quadrant (or half), fillets included, and mirror it across each plane. A drafted or filleted face that crosses a mirror plane meshes unevenly, and the symmetry check can fail even when the solid is exact. Do not import `OCP` to split or merge faces; source hygiene rejects every import except `build123d` and `math`.

Tangent hull of circles: `make_hull([(Pos(x, y) * Circle(r)).edges() for x, y, r in circles])`. `make_hull` takes edges, not faces.

Do not call `.mesh()` on `result`. The critic tessellates the STEP itself.

## Verify

`.venv/bin/ruff format --check`, `.venv/bin/ruff check` (the pinned ruff; PATH may hold another version that formats differently), then `python -m opencad quick main.py --contract designs/<part>/contract.yaml`.

Introductory examples: `sources/build123d/examples/` after `scripts/fetch_sources.py --backend build123d`.

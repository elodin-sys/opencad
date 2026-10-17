---
name: cadquery
disable-model-invocation: true
description: Worker pack for the CadQuery backend (pinned 2.8) covering the part and assembly-source contract, style and the verify critics. Read before writing or correcting parts/cadquery/<name>/main.py.
---

# CadQuery (opencad backend)

Read this before writing `parts/cadquery/<part>/main.py`. Pinned CadQuery 2.8.x in the repo `.venv`. Units are millimetres.

## Deliverable

```python
import cadquery as cq
plateWidth = 80.0
# ... every contract parameter as a top-level float ...
assert plateWidth > 0, "infeasible: plateWidth must be positive"
result = cq.Workplane("XY").box(...)
```

`result` is a `Workplane` or Shape. No `show_object`, no file IO, no importers.

Every solid on the `result` stack is exported (like `cq.exporters.export`), so a multi-solid contract (`acceptance.solid_count` > 1) keeps its bodies separate and puts them all on the stack:

```python
result = base.add(lid)          # or: result = [base, lid]
```

`union` fuses touching bodies into one solid and fails `solid_count`; use `add` (or a list) for separate parts.

## Assemblies

An assemble work order imports the two provided STEP bodies (only `inputs/<body>.step`), places them, and hands both over:

```python
import cadquery as cq
from pathlib import Path

here = Path(__file__).resolve().parent
one = cq.importers.importStep(str(here / "inputs" / "body_one.step"))
two = cq.importers.importStep(str(here / "inputs" / "body_two.step"))
placed = one.val().located(cq.Location(tx, ty, tz))  # Location does not accept cq.Matrix on 2.8
result = [placed, two]
placements = {
    "body_one": [[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]],
    "body_two": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
}
```

`placements` is a 4×4 row-major millimetre matrix per body; the runner writes `placements.json` beside the STEP. Native `cq.Assembly` + `constrain`/`solve` is optional — if you use it, still assign `result` and `placements` (read the solved `loc` back into the dict). Do not import anything under `truth/`.

## Style

- Fluent `Workplane` from a named plane. `centered=(False, False, False)` when the contract origin is a min corner.
- Select with `faces(">Z")`, `edges("|Z")`, tags. Never `.edges()[i]`.
- Batch tools (`union` them), one `cut`. Overrun a cutter 0.01–0.05 mm past the face into air; never leave a tool face coincident with a stock face (`BRep_API: command not done` is almost always that). `clean=True` if a boolean goes sour.
- Holes: `hole` / `cboreHole` or a cut cylinder, not a coincident-face boolean.
- Use the **exact** contract parameter names (`cornerRadius`, not `filletRadius`). `centered=(False, False, False)` when the origin is a min corner.
- Blockout: if the volume band is much smaller than the AABB (e.g. benchy 20–31k vs 60×31×48 box), do not `box` the envelope. A hull-like solid must still touch all six envelope faces.
- If a loft face leaves an open STL ring, replace that section with an extrude and cut pockets from the prism before unioning. Do not scale a mid-station loft when `overallLength` changes — add length at a bow/stern block so the volume delta stays linear.
- Fair hulls: three or more spline stations with `loft(ruled=False)`. Keep `ruled=True` only where a flare must stay planar. Symmetric parts are one half mirrored (`mirror("XZ", union=True)`) or verified with the `quick` symmetry line; a non-ruled spline loft can fold on one side, so read the stern and bow quarters in `quick-views.png`.
- When the contract has `acceptance.symmetry`, build one quadrant (or half), fillets included, and `mirror` it across each plane. A drafted or filleted face that crosses a mirror plane meshes unevenly, and the symmetry check can fail even when the solid is exact. Do not import `OCP` to split or merge faces; source hygiene rejects every import except `cadquery` and `math`.

## Decomposed parts

When the pipeline decomposes a part, `parts/cadquery/<part>/` holds `params.py` (every contract parameter as a top-level float), `datum.py` (`datum` = the envelope body) and one `<group>.py` per feature group with `def apply(body)`; `main.py` composes them (`result = apply_b(apply_a(datum))`). Import parameters by name (`from params import plateWidth`; `ruff check` rejects `import *`) and never redeclare them. The work-order brief carries the exact recipe and the pre-written scratch main for the critic.

## Verify

`.venv/bin/ruff format --check`, `.venv/bin/ruff check` (the pinned ruff; PATH may hold another version that formats differently), then `python -m opencad quick main.py --contract designs/<part>/contract.yaml`.

Worked examples live under `sources/cadquery/examples/` when fetched (`scripts/fetch_sources.py --backend cadquery`).

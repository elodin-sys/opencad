---
name: freecad
disable-model-invocation: true
description: Worker pack for the FreeCAD PartDesign backend (freecadcmd 1.1, never FreeCADGui) covering the part and assembly-source contract, style and the verify critics. Read before writing or correcting parts/freecad/<name>/main.py.
---

# FreeCAD PartDesign (opencad backend)

Read this before writing `parts/freecad/<part>/main.py`. Driven by `freecadcmd` (FreeCAD 1.1.x, Python 3.11). Never import `FreeCADGui`. Millimetres.

## Deliverable

```python
import FreeCAD, Part, Sketcher, PartDesign
plateWidth = 80.0
assert plateWidth > 0, "infeasible: plateWidth must be positive"
doc = FreeCAD.newDocument("part")
body = doc.addObject("PartDesign::Body", "Body")
# Sketch on body.Origin XY, Pad, Pocket/Hole, Fillet...
doc.recompute()
result = body
```

`result` must be a `PartDesign::Body`. Every feature `isValid()` after `recompute()`.

Multi-solid contracts (`acceptance.solid_count` > 1, e.g. an enclosure base + lid or a gear pair): one Body per solid, all kept in the document, and `result` is a tuple of them in `acceptance.solids` order:

```python
base = doc.addObject("PartDesign::Body", "Base")
lid = doc.addObject("PartDesign::Body", "Lid")
# ... features on each body ...
doc.recompute()
result = (base, lid)
```

The runner exports every Body in `result` into one STEP/STL and measures the compound (combined bbox, summed volume, volume-weighted centroid). Never fuse separate solids into one Body.

## Assemblies

An assemble work order imports the two provided STEP bodies (only `inputs/<body>.step`), places them, and hands both over. `result` may be a tuple of `PartDesign::Body` or `Part::Feature`:

```python
import FreeCAD
import Part
from pathlib import Path

here = Path(__file__).resolve().parent
doc = FreeCAD.newDocument("asm")

def load(name, origin):
    shp = Part.Shape()
    shp.read(str(here / "inputs" / f"{name}.step"))
    feat = doc.addObject("Part::Feature", name)
    feat.Shape = shp
    feat.Placement = FreeCAD.Placement(FreeCAD.Vector(*origin), FreeCAD.Rotation())
    return feat

one = load("body_one", (tx, ty, tz))
two = load("body_two", (0.0, 0.0, 0.0))
doc.recompute()
result = (one, two)
placements = {
    "body_one": [[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]],
    "body_two": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
}
```

`placements` is a 4×4 row-major millimetre matrix per body; the runner writes `placements.json` beside the STEP. Wrapping the imported shape in a `PartDesign::Body` with a BaseFeature is fine. The Assembly workbench is optional and often unavailable under `freecadcmd`. Do not import anything under `truth/`.

## Style

- One body per deliverable solid. Features in order: Sketch → Pad → Pocket/Hole → Fillet/Chamfer/Loft/Thickness.
- Fully constrain sketches with `Sketcher.Constraint` distances from the parameters.
- Find faces by normal and centre, never `Face7`.
- One Pocket/Hole per family (multi-circle sketch). `Refine = True` on the last feature.
- Booleans: batch the profiles of one family into one sketch and one Pocket; a blind cut overruns 0.01–0.05 mm past the face it opens into (or `Type = ThroughAll`); never leave a tool face coincident with a stock face (`Recompute failed` / `BRep_API: command not done` is almost always that).
- Lofts: sketches on offset datum planes, `PartDesign::AdditiveLoft`. Smooth hulls are `Ruled = False` through `Part.BSplineCurve` / `Part.ArcOfCircle` sections with the same edge count; `Ruled = True` over polylines prints as flat facets. Keep one planar keel trim (Pocket at z=0). Symmetric parts are one half mirrored (`PartDesign::Mirrored`) or verified with the `quick` symmetry line; a non-ruled spline loft can fold on one side, so read the stern and bow quarters in `quick-views.png`.
- When the contract has `acceptance.symmetry`, build one quadrant (or half), fillets included, and mirror it across each plane with `PartDesign::Mirrored`. A drafted or filleted face that crosses a mirror plane meshes unevenly, and the symmetry check can fail even when the solid is exact. Do not import `OCP` to split or merge faces; source hygiene rejects every import except `FreeCAD`, `Part`, `Sketcher`, `PartDesign` and `math`.
- Pin every sketch to the origin: `DistanceX/Y` from `-1` (sketch origin) so the solid sits on the contract envelope, not a solver drift.
- Use the **exact** contract parameter names. Do not import meshes or `FreeCADGui`.
- Blockout: if the volume band is much smaller than the AABB (e.g. benchy), do not Pad the full envelope rectangle; a hull-like solid must still touch all six faces.

## Decomposed parts

When the pipeline decomposes a part, `parts/freecad/<part>/` holds `params.py` (every contract parameter as a top-level float), `datum.py` (opens the document, `datum` = the envelope `PartDesign::Body`) and one `<group>.py` per feature group with `def apply(body)` that adds its features to the Body, recomputes and returns it; `main.py` composes them (`result = apply_b(apply_a(datum))`). Import parameters by name (`from params import plateWidth`; `ruff check` rejects `import *`) and never redeclare them. The work-order brief carries the exact recipe and the pre-written scratch main for the critic.

## Verify

`.venv/bin/ruff format --check`, `.venv/bin/ruff check` (the pinned ruff; PATH may hold another version that formats differently), `python -m opencad quick main.py --contract designs/<part>/contract.yaml`. The runner also writes `<part>.FCStd`.

Sources: `sources/freecad/` after `scripts/fetch_sources.py --backend freecad`.

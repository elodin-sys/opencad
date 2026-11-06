"""Prism worker rules: build123d 0.11 algebra mode plus the `navier_cad` vocabulary, in millimetres."""

from __future__ import annotations

from pathlib import Path

from opencad.backends.local import SHARED_RULES
from opencad.paths import SKILLS

RULES = (
    SHARED_RULES
    + """
Prism rules (Prism's managed python-env: build123d 0.11.x, navier_cad, bd_warehouse; algebra mode):
- MILLIMETRES, not metres. Prism's standalone code-cad skill authors in metres; this pipeline measures the exported STEP in the contract's units (mm), rewrites contract parameters as literal mm constants for edit tests, and judges every gate in mm. A part authored in metres fails `envelope` by a factor of 1000.
- Import only `build123d` (`from build123d import *`, explicit names, or `import build123d as bd`), `math`, `navier_cad` (`from navier_cad.blends import fuse_all, fillet_safe`, `navier_cad.shapes`, `.sweeps`, `.curves`, `.profiles`, `.patterns`, `.materials`) and `bd_warehouse` (millimetres, matching this pipeline). `OCP`, `collections` and every other module fail source hygiene. No CadQuery, no FreeCAD.
- No `navier_cad.cache` (`cached_part` writes under the working directory), no `navier_cad.checks`, no `navier_cad.shapes.load_step` or `import_step` outside assembly orders, no `materials`/`views` module globals: the pipeline reads `result` only.
- Parameters are floats in millimetres (`plateWidth = 80.0`), top-level, before geometry.
- Deliverable: `main.py` assigns `result` to a `Part`, `Solid` or `Compound`, or to a list/tuple of them for a multi-solid contract (`result = [base, lid]` or `Compound([base, lid])`); every solid is exported. Never `+` (fuse) separate bodies. No file IO, no show/export helpers, except assembly tasks.
- Assembly tasks: import only the two provided `inputs/<body>.step` files (`import_step`); assign `result` to the two placed bodies and `placements` to a dict of 4x4 row-major millimetre matrices keyed by body name.
- Assembly sources (`parts/<backend>/<asm>/main.py`): `import_step` only the listed `inputs/<name>.step` files, move each with `.moved(Location(...))` or `Pos(...) * Rot(...) * body`, assign `result` to a list with one solid per body in the brief's order (never `+`), `placements` to a dict body -> 4x4 row-major mm matrix (identity for a derived body), and optionally `joints` to joint name -> {"origin", "axis"}. A derived fluid body is booleans of the placed solids (`Box(...) - housing - impeller`, then the solid that contains the seed). A construction input (role construction) is imported only to build derived bodies and is neither in `result` nor in `placements`.
- Algebra mode by default (`Box(...) - Cylinder(...)`, `Mode.SUBTRACT` only where the algebra is unclear). Builders only when they are clearer.
- Prefer the vetted `navier_cad` vocabulary over raw sweeps, lofts and fillets: `blends.fuse_all(base, tools)` (one fuse instead of a loop), `blends.fillet_safe(shape, edges, radius)` / `chamfer_safe` (return `(solid, report)`; never a bare `try/except` around a fillet), `sweeps.sweep_profile`, `sweeps.bent_tube`, `sweeps.pipe`, `sweeps.loft_sections`, `curves.spline_through`, `profiles.rounded_rect`, `profiles.slot`, `patterns.linear|polar|grid` (-> `list[Location]`). They are unit-agnostic geometry: pass millimetres.
- build123d 0.11 traps: `shape.is_valid` is a property; `a & b` returns `None` for disjoint shapes; `Compound([...])` takes a list (`Compound(solid)` crashes); `shape.moved(Location((x, y, z)))`, not a tuple; `align=` takes `Align.MIN/CENTER/MAX`, never 0 or None; `solid - face` raises, extrude the face first; thin walls on a loft or sweep are an outer loft minus an inner loft, `offset`/`offset_3d` on a lofted solid usually fails.
- Select with `faces().sort_by(Axis.Z)[-1]`, `faces().filter_by(Axis.Z)`, or Locations. Never a bare list index that depends on creation order except after an explicit `sort_by`.
- Batch tools into one `Compound` then one subtraction. Offset a cutting tool 0.01-0.05 mm past the face.
- Verify with the pipeline's critics only: `.venv/bin/ruff format --check`, `.venv/bin/ruff check` (the repo's pinned ruff), then `python -m opencad quick main.py --contract <contract> --backend prism`, which builds the part in Prism's interpreter. The `prism_cad_run` tool reads a script as metres and writes `<script>.step` beside it: use it, if at all, only with an inline `script` (`checks: "fast"`, `skip_mesh: true`) to probe one feature, never on `main.py` and never as verification.
"""
)

ALLOWED_IMPORTS = frozenset({"build123d", "math", "bd", "navier_cad", "bd_warehouse"})
CONSTRUCTION = frozenset(
    {
        "Box",
        "Cylinder",
        "Sphere",
        "Cone",
        "Torus",
        "Wedge",
        "extrude",
        "Extrude",
        "revolve",
        "Revolve",
        "loft",
        "Loft",
        "sweep",
        "Sweep",
        "Hole",
        "CounterBoreHole",
        "CounterSinkHole",
        "fillet",
        "Fillet",
        "chamfer",
        "Chamfer",
        "offset",
        "shell",
        "split",
        "mirror",
        "PolarLocations",
        "GridLocations",
        "HexLocations",
        "Locations",
        "Plane",
        "Axis",
        "Pos",
        "Rot",
        "Location",
        "Compound",
        "Part",
        "Solid",
        "Sketch",
        "Circle",
        "Rectangle",
        "Polygon",
        "make_face",
        "make_hull",
        # navier_cad vocabulary
        "tube",
        "cylinder_along",
        "pipe_between",
        "beam_between",
        "rounded_path",
        "fuse_all",
        "fillet_safe",
        "chamfer_safe",
        "blend_union",
        "weld_bead",
        "sweep_profile",
        "pipe",
        "bent_tube",
        "loft_sections",
        "spline_through",
        "helix",
        "spiral",
        "offset_curve",
        "rounded_rect",
        "slot",
        "closed_spline",
        "naca4",
        "linear",
        "polar",
        "grid",
        "along_path",
        "isogrid_panel",
        "rao_bell",
    }
)


def skills() -> list[Path]:
    root = SKILLS / "backends" / "prism"
    return [p for p in (root / "SKILL.md",) if p.exists()]


def skills_note() -> str:
    paths = skills()
    return (
        "Skills: read " + " and ".join(str(p) for p in paths) + " first."
        if paths
        else "Skills: build123d 0.11 algebra mode in millimetres with navier_cad helpers; result = Part, or a list of Parts for a multi-solid contract."
    )

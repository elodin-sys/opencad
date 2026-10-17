"""CadQuery worker rules and skills pointer."""

from __future__ import annotations

from pathlib import Path

from opencad.backends.local import SHARED_RULES
from opencad.paths import SKILLS

RULES = (
    SHARED_RULES
    + """
CadQuery rules (pinned 2.8.x):
- First line after comments: `import cadquery as cq`. Import only `cadquery` and `math`; `OCP`, `collections` and every other module fail source hygiene.
- Parameters are floats in millimetres (`plateWidth = 80.0`), top-level, before geometry.
- Deliverable: `main.py` assigns `result` to a `cq.Workplane` or a Shape; every solid on its stack is exported (`acceptance.solid_count` solids). Separate bodies: `result = base.add(lid)` or `result = [base, lid]`, never a `union` that fuses them. No `show_object`, no file IO, no `cq.importers` except assembly tasks.
- Assembly tasks: import only the two provided `inputs/<body>.step` files (`cq.importers.importStep`); assign `result` to the two placed bodies and `placements` to a dict of 4x4 row-major millimetre matrices keyed by body name.
- Assembly sources (`parts/<backend>/<asm>/main.py`): `cq.importers.importStep` only the listed `inputs/<name>.step` files, move each with `.val().moved(cq.Location(...))` or `transformShape`, assign `result` to a list with one solid per body in the brief's order (never `union`), `placements` to a dict body -> 4x4 row-major mm matrix (identity for a derived body), and optionally `joints` to joint name -> {"origin", "axis"}. A derived fluid body is booleans of the placed solids (a box `.cut()` by housing and impeller, then the solid that contains the seed). A construction input (role construction) is imported only to build derived bodies and is neither in `result` nor in `placements`.
- Select by direction or tag (`.faces(">Z")`, `.edges("|Z")`, `.faces(tag)`). Never `.edges()[i]` or any bare index into a topology list.
- Batch cuts: build tools, `union` them, then one `cut` (or `cutEach`). `clean=True` on the result. Offset a cutting tool 0.01-0.05 mm past the face.
- One fluent style per file; name intermediates. Holes with `hole` / `cboreHole` / `cskHole` or a cut cylinder, not a boolean of a coincident face.
- Verify: `.venv/bin/ruff format --check`, `.venv/bin/ruff check` (the pinned ruff; PATH may hold another version that formats differently), then `python -m opencad quick main.py --contract <contract>`.
"""
)

ALLOWED_IMPORTS = frozenset({"cadquery", "cq", "math"})
CONSTRUCTION = frozenset(
    {
        "Workplane",
        "box",
        "circle",
        "rect",
        "polygon",
        "extrude",
        "revolve",
        "loft",
        "sweep",
        "cut",
        "union",
        "intersect",
        "hole",
        "cboreHole",
        "cskHole",
        "fillet",
        "chamfer",
        "shell",
        "offset2D",
        "pushPoints",
        "eachpoint",
        "cutThruAll",
        "cutBlind",
        "workplane",
        "transformed",
        "tag",
        "faces",
        "edges",
        "wires",
        "solids",
        "vertices",
    }
)


def skills() -> list[Path]:
    root = SKILLS / "backends" / "cadquery"
    return [p for p in (root / "SKILL.md",) if p.exists()]


def skills_note() -> str:
    paths = skills()
    return (
        "Skills: read " + " and ".join(str(p) for p in paths) + " first."
        if paths
        else "Skills: CadQuery 2.8 fluent Workplane; result = Workplane (every stack solid is exported)."
    )

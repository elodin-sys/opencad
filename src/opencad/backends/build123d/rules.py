"""build123d worker rules (algebra mode first)."""

from __future__ import annotations

from pathlib import Path

from opencad.backends.local import SHARED_RULES
from opencad.paths import SKILLS

RULES = (
    SHARED_RULES
    + """
build123d rules (pinned 0.12.x, algebra mode):
- Import only `build123d` (`from build123d import *`, explicit names, or `import build123d as bd`) and `math`. `OCP`, `collections` and every other module fail source hygiene. No CadQuery, no FreeCAD.
- Parameters are floats in millimetres (`plateWidth = 80.0`), top-level, before geometry.
- Deliverable: `main.py` assigns `result` to a `Part`, `Solid` or `Compound`, or to a list/tuple of them for a multi-solid contract (`result = [base, lid]` or `Compound([base, lid])`); every solid is exported. Never `+` (fuse) separate bodies. No file IO, no show/export helpers, except assembly tasks.
- Assembly tasks: import only the two provided `inputs/<body>.step` files (`import_step`); assign `result` to the two placed bodies and `placements` to a dict of 4x4 row-major millimetre matrices keyed by body name.
- Assembly sources (`parts/<backend>/<asm>/main.py`): `import_step` only the listed `inputs/<name>.step` files, move each with `.moved(Location(...))` or `Pos(...) * Rot(...) * body`, assign `result` to a list with one solid per body in the brief's order (never `+`), `placements` to a dict body -> 4x4 row-major mm matrix (identity for a derived body), and optionally `joints` to joint name -> {"origin", "axis"}. A derived fluid body is booleans of the placed solids (`Box(...) - housing - impeller`, then the solid that contains the seed). A construction input (role construction) is imported only to build derived bodies and is neither in `result` nor in `placements`.
- Algebra mode by default (`Box(...) - Cylinder(...)`, `Mode.SUBTRACT` only where the algebra is unclear). Builders only when they are clearer.
- Select with `faces().sort_by(Axis.Z)[-1]`, `faces().filter_by(Axis.Z)`, or Locations. Never a bare list index that depends on creation order except after an explicit `sort_by`.
- Batch tools into one `Compound` then one subtraction. Offset a cutting tool 0.01-0.05 mm past the face.
- Verify: `.venv/bin/ruff format --check`, `.venv/bin/ruff check` (the pinned ruff; PATH may hold another version that formats differently), then `python -m opencad quick main.py --contract <contract>`.
"""
)

ALLOWED_IMPORTS = frozenset({"build123d", "math", "bd"})
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
    }
)


def skills() -> list[Path]:
    root = SKILLS / "backends" / "build123d"
    return [p for p in (root / "SKILL.md",) if p.exists()]


def skills_note() -> str:
    paths = skills()
    return (
        "Skills: read " + " and ".join(str(p) for p in paths) + " first."
        if paths
        else "Skills: build123d 0.12 algebra mode; result = Part, or a list of Parts for a multi-solid contract."
    )

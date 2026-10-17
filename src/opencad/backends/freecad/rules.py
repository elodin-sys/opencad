"""FreeCAD PartDesign worker rules."""

from __future__ import annotations

from pathlib import Path

from opencad.backends.local import SHARED_RULES
from opencad.paths import SKILLS

RULES = (
    SHARED_RULES
    + """
FreeCAD rules (1.1.x, PartDesign, headless freecadcmd):
- Imports allowed: `FreeCAD`, `Part`, `Sketcher`, `PartDesign` and `math` only; every other module (`FreeCADGui`, `OCP`, `collections`) fails source hygiene.
- Parameters are floats in millimetres (`plateWidth = 80.0`), top-level, before geometry.
- Open a new document, build one `PartDesign::Body` per deliverable solid (`acceptance.solid_count`, usually one), add named features in construction order (Sketch -> Pad/Pocket/Hole/Fillet/Chamfer/AdditiveLoft/Thickness/patterns). `doc.recompute()` before assigning `result`.
- Deliverable: `result` is that `PartDesign::Body`, or a tuple of Bodies in `acceptance.solids` order when the contract declares several (`result = (base, lid)`); the runner exports and measures every Body in it. Never fuse separate solids into one Body. `Part` is only for construction geometry or a `BaseFeature`. Assembly tasks may also return `Part::Feature` objects whose Shape is the imported-and-placed solid.
- Assembly tasks: import only the two provided `inputs/<body>.step` files (`Part.Shape.read` or a BaseFeature); assign `result` to the two placed bodies and `placements` to a dict of 4x4 row-major millimetre matrices keyed by body name.
- Assembly sources (`parts/<backend>/<asm>/main.py`): read only the listed `inputs/<name>.step` files, place each shape with `Placement`/`transformShape`, return `Part::Feature` objects (one per body, in the brief's order, never fused) as `result`, `placements` as a dict body -> 4x4 row-major mm matrix (identity for a derived body). A derived fluid body is booleans of the placed shapes (`Part.makeBox(...).cut(housing).cut(impeller)`, then the solid that contains the seed). A construction input (role construction) is imported only to build derived bodies and is neither in `result` nor in `placements`.
- Sketches attach to named planes or to a face found by normal and centre. Never `Face7` or any topological-name literal.
- One Pocket/Hole feature per family with a multi-profile sketch when possible. `Refine = True` on the last feature.
- Fully constrain sketches (`Sketcher.Constraint` distances from the parameters).
- Verify: `.venv/bin/ruff format --check`, `.venv/bin/ruff check` (the pinned ruff; PATH may hold another version that formats differently), `python -m opencad quick main.py --contract <contract>`. After recompute every feature must be `isValid()`.
"""
)

ALLOWED_IMPORTS = frozenset({"FreeCAD", "Part", "Sketcher", "PartDesign", "math"})
CONSTRUCTION = frozenset(
    {
        "newDocument",
        "addObject",
        "recompute",
        "addConstraint",
        "Constraint",
        "Pad",
        "Pocket",
        "Hole",
        "Fillet",
        "Chamfer",
        "AdditiveLoft",
        "SubtractiveLoft",
        "Thickness",
        "Revolution",
        "PolarPattern",
        "LinearPattern",
        "Mirrored",
        "Sketch",
        "Body",
    }
)


def skills() -> list[Path]:
    root = SKILLS / "backends" / "freecad"
    return [p for p in (root / "SKILL.md",) if p.exists()]


def skills_note() -> str:
    paths = skills()
    return (
        "Skills: read " + " and ".join(str(p) for p in paths) + " first."
        if paths
        else "Skills: FreeCAD 1.1 PartDesign Body; result = Body, or a tuple of Bodies for a multi-solid contract."
    )

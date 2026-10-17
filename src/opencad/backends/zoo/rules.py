"""Worker rules, skills pointer and critic note for the Zoo/KCL backend."""

from __future__ import annotations

from pathlib import Path

from opencad.paths import ZOO_SKILLS

KCL_RULES = """\
KCL rules for this repository (non-negotiable):
- First line: `@settings(defaultLengthUnit = mm, kclVersion = 2.0)`. Work in millimetres and degrees.
- KCL 2 sketch blocks only (`sketch(on = XY) { ... }`, constraints, `region(...)`). Never legacy v1 (`startSketchOn`, `startProfile`, `|> line(...)`, `close()`).
- Every contract parameter must appear as a top-level constant with EXACTLY the contract name and value, e.g. `plateWidth = 80mm`, one per line, before any geometry, so the pipeline can rewrite it for edit tests. Derive everything else from those constants.
- Add `assert(...)` sanity guards (`isGreaterThan`, `isLessThan`) for the invariants you rely on. Never assert equality between contract parameters (no `assert(a, isEqualTo = 12 * b)`): the pipeline rewrites one parameter at a time to prove editability, and such a lock turns every edit test into a failure. A derived value's formula belongs in the contract and in a comment, not in a hard equality check.
- Do not import or reference any reference mesh/CAD file from KCL; the deliverable must be editable construction, not an import.
- Never use `--allow-errors`. Never edit contract.yaml or brief.md; if the contract is wrong, report it under Open questions.
- Verify before reporting: `zoo kcl format --write`, `zoo kcl lint`, `zoo kcl analyze --format json --volume-output-unit mm3 --center-of-mass-output-unit mm --surface-area-output-unit mm2`. Render views locally from the exported STL. Compare measured to expected numbers and state both.
- Export requirements: `zoo kcl export -t stl` must be watertight (check with the repo `.venv`: `python -c "import trimesh; m=trimesh.load('out.stl'); print(m.is_watertight)"`). Engine volume from `zoo kcl analyze` must agree with the exported STEP within 0.2%. Engine bounding box must match the finished solid — hide every construction region; do not sketch datum axes (`hide` does not take sketch blocks).
- Blind holes that need a planar floor: cut-extrude a circle or subtract a cylinder. Never `hole::holeAt` / `hole::hole` with `holeBottom = hole::flat()` — that floor is a degenerate cone the tessellator drops, leaving an open STL ring and an engine volume short by z·A/3.
- Guard every parameter with geometric `assert` bounds (a counterbore shallower than the plate, a hole inside its boss, a wall thicker than zero). An impossible parameter value must fail loudly at the assert, never build distorted geometry: the pipeline sets deliberately infeasible values and expects an explicit failure. Bounds must admit every value in the contract's `edit_test.sweep` range and every `edit_test.delta`; a guard that rejects a declared sweep value is a modelling defect, not a refusal.
"""


def skills() -> list[Path]:
    return [ZOO_SKILLS / "kcl-docs" / "SKILL.md", ZOO_SKILLS / "zoo-tooling" / "SKILL.md"]


def skills_note() -> str:
    return f"Skills: read {ZOO_SKILLS}/kcl-docs/SKILL.md and {ZOO_SKILLS}/zoo-tooling/SKILL.md first; worked samples are under {ZOO_SKILLS}/kcl-examples."

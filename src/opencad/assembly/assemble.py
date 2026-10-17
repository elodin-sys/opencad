"""Assemble stage: stage the part handoff STEPs and purchased catalog solids into parts/<backend>/<asm>/inputs/, then one worker
turn writes parts/<backend>/<asm>/main.py placing every body on its joints (critic: `python -m opencad assembly check-source`)."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from opencad import worker
from opencad.assembly import AsmCtx, AssemblyError
from opencad.io import sha256_file
from opencad.paths import REPO_ROOT, design_dir


def stage_inputs(actx: AsmCtx) -> dict[str, Any]:
    from opencad.backends.local import write_step
    from opencad.geomcheck.multibody import build_hardware
    from opencad.geomcheck.qualify import qualify

    actx.inputs_dir.mkdir(parents=True, exist_ok=True)
    staged, missing, qualified = {}, [], {}
    for p in actx.contract.parts:
        dest = actx.input_step(p.name)
        if p.kind == "modelled":
            src = actx.handoff_step(p.design)
            if not src.exists():
                missing.append(f"{p.name}: no handoff STEP {src}")
                continue
            if actx.kcl:  # the zoo importer rejects zoo's own STEP export ("engine: import failed"); an OpenCascade rewrite imports
                from opencad.geomcheck import brep

                write_step(brep.read_step(src), dest, p.design)
            elif not dest.exists() or sha256_file(dest) != sha256_file(src):
                shutil.copy2(src, dest)
        elif p.kind == "purchased":
            hw = build_hardware([p.catalog], base_dir=actx.design_dir)
            if p.catalog.kind == "step":  # supplied CAD: qualified before any boolean reads it
                q = qualify(hw[p.catalog.name])
                qualified[p.name] = {k: q[k] for k in ("ok", "solids", "free_edges", "volumes", "problems")}
                if not q["ok"]:
                    missing.append(f"{p.name}: input CAD invalid ({p.catalog.path}): {'; '.join(q['problems'])}")
                    continue
            write_step(hw[p.catalog.name], dest, p.name)
        else:
            continue
        staged[p.name] = {"path": str(dest), "sha256": sha256_file(dest)}
    return {"ok": not missing, "inputs": staged, "missing": missing, "qualified": qualified}


def _frame(f: Any) -> str:
    return f"origin {list(f.origin)} axis {list(f.axis)}" + (f" ref {list(f.ref)}" if f.ref is not None else "")


def brief(actx: AsmCtx) -> str:
    a = actx.contract
    rows = []
    for p in a.parts:
        if p.kind == "derived":
            rows.append(f"| {p.name} | derived ({p.role}) | built in {actx.entry.name} from other bodies | {p.description or ''} |")
        elif not p.placed:
            rows.append(f"| {p.name} | construction input | `inputs/{actx.input_step(p.name).name}` | read it only to build derived bodies; never place or export it. {p.description or ''} |")
        else:
            rows.append(f"| {p.name} | {p.kind} | `inputs/{actx.input_step(p.name).name}` | {p.description or (p.intent[:120] + '...' if len(p.intent) > 120 else p.intent)} |")
    joints = "\n".join(f"| {j.name} | {j.kind}{' (closure)' if j.closure else ''} | {j.parent}: {_frame(j.parent_frame)} | {j.child}: {_frame(j.child_frame)} | offset {j.offset} mm, angle {j.angle} deg{', flipped' if j.flip else ''} |"
                       for j in a.joints)
    loops = [j.name for j in a.joints if j.closure]
    fluids = "\n".join(f"- `{f.body or f.name}`: the region inside {f.walls} minus {f.minus or 'nothing'}, closed at the caps "
                       + ", ".join(f"{c.name} (point {list(c.point)}, outward normal {list(c.normal)})" for c in f.caps)
                       + f"; the seed {list(f.seed)} lies inside it" + (f"; volume {f.volume.expected:g}" if f.volume else "") for f in a.fluid_volumes)
    return f"""Assemble the machine `{a.name}` on backend `{actx.backend_id}`. Read `{actx.contract_path}` (the AssemblyContract) first.

Bodies (every placed body is exactly its input STEP moved by a rigid transform; never edit, rebuild or re-model a part):

| body | kind | geometry | note |
|---|---|---|---|
{chr(10).join(rows)}

Joints (each frame is in that body's OWN frame, i.e. the frame of its input STEP; the datum part `{a.datum_part}` stays at the identity):

| joint | kind | parent frame | child frame | rest |
|---|---|---|---|---|
{joints}

Placement rule: for each joint, choose the child's transform so that its child frame lands on the parent's placed frame: the origins
coincide up to `offset` along the parent axis, the axes are parallel (anti-parallel when flipped), and, where both frames give `ref`,
the child's ref sits `angle` degrees from the parent's ref about the parent axis. Compose transforms from the datum part outward.
A gear on a joint a checked mesh couples must sit on its axis within a fifth of that mesh's backlash_max; never offset it to clear a tooth.
{('Closure joints ' + ', '.join(loops) + ' close kinematic loops: both of their bodies are already placed through the other joints, so they add '
  'no transform. Choose the rest angles of the loop so each closure joint is satisfied too (its frames coincide as above); the '
  'verify critic checks it like any joint.') if loops else ''}
{('Fluid bodies to build from the placed solids (booleans only, no new dimensions):' + chr(10) + fluids) if fluids else ''}

{_kcl_deliverable(actx) if actx.kcl else _py_deliverable(actx)}

Verify with the critic (it exports through the engine and prints every check the gates will apply: solid count, per-body agreement with
input x placement, joint fidelity, clearances, envelope), iterate until every line reads ok, then open `assembly-views.png`:
`cd {REPO_ROOT} && .venv/bin/python -m opencad assembly check-source {a.name} --backend {actx.backend_id}`
Report the transforms under `## Result` and the critic's numbers under `## Verification`.
"""


def _py_deliverable(actx: AsmCtx) -> str:
    return f"""Deliverable: `{actx.entry}` that
- imports only the files under `inputs/` listed above (relative paths `inputs/<name>.step`; nothing else, nothing under `truth/`);
- assigns `result` to a list with one solid per body, in the order of the table above (never fuse bodies);
- assigns `placements` to a dict body name -> 4x4 row-major millimetre matrix (the identity for derived bodies built in place);
- may assign `joints` to a dict joint name -> {{"origin": [x, y, z], "axis": [x, y, z]}} in the assembly frame (a cross-check)."""


def _kcl_deliverable(actx: AsmCtx) -> str:
    derived = [p.name for p in actx.contract.parts if p.kind == "derived"]
    return f"""Deliverables: `{actx.entry}` and `{actx.part_dir / 'placements.json'}`.
- `main.kcl` starts with `@settings(defaultLengthUnit = mm, kclVersion = 2.0)`, then one `import "inputs/<name>.step" as <body>` per placed body
  (only the files listed above; nothing else, nothing under `truth/`). Each body is placed by global elementary rotations in the order its
  rotation matrix composes them (rightmost factor first), then one global translate:
  `body |> rotate(axis = [1, 0, 0], angle = -90deg, global = true) |> rotate(axis = [0, 1, 0], angle = 30deg, global = true) |> translate(xyz = [x, y, z], global = true)`.
  Use elementary rotations rather than one axis-angle: a 180 deg turn has no stable axis-angle.
- Every placed body stays a separate imported solid: imported geometry cannot enter `union`/`subtract`/`intersect`.{(' Derived bodies (' + ', '.join(derived) + ') need booleans, which the zoo backend cannot apply to imported geometry: report them under `## Open questions`.') if derived else ''}
- `placements.json`: body name -> 4x4 row-major millimetre matrix equal to that body's rotations and translate in `main.kcl`.
  The critic compares every exported solid with its input STEP x this matrix, so a matrix that differs from the KCL fails agreement.
- Run `zoo kcl format --write {actx.entry}` and `zoo kcl lint {actx.entry}` before the critic."""


def readable(actx: AsmCtx) -> list[str]:
    return [str(actx.design_dir), *[str(design_dir(d)) for d in actx.contract.designs()]]


def images(actx: AsmCtx) -> list[Path]:
    out = []
    for d in actx.contract.designs():
        p = actx.part_results(d) / "snapshots" / "view-all.png"
        if p.exists():
            out.append(p)
    return out


def run(turn: Any, actx: AsmCtx, *, key: str = "assemble", message: str | None = None, resume: str | None = None, role: str = "assemble",
        timeout: float | None = None) -> dict[str, Any]:
    staged = stage_inputs(actx)
    if not staged["ok"]:
        raise AssemblyError("cannot assemble: " + "; ".join(staged["missing"]))
    n = len(actx.contract.parts)
    r = turn(lambda: worker.dispatch(message or brief(actx), role=role, key=key, results_dir=actx.results_dir, part=actx.name, cd=actx.part_dir,
                                     run_dir=actx.results_dir / "assemble-work", images=images(actx) if message is None else None, resume=resume,
                                     timeout=timeout, deliverables=[actx.entry, *([actx.part_dir / "placements.json"] if actx.kcl else [])], add_dirs=[actx.part_dir],
                                     context={"assembly": actx.name, "readable": readable(actx), "entry": str(actx.entry)},
                                     budget=worker.scaled_budget(role if role == "assemble" else "correction", n)))
    return {"ok": actx.entry.exists(), "inputs": staged["inputs"], "worker": r.summary(), "thread_id": r.thread_id, "report": r.sections,
            "critic": f"cd {REPO_ROOT} && .venv/bin/python -m opencad assembly check-source {actx.name} --backend {actx.backend_id}"}

"""Assembly drafting: one asm-draft turn writes assembly.yaml + brief.md from the sources (critic: `assembly check`), then one
part draft per design runs in parallel from each part's intent (critic: `check-bundle`), then joint frames are cross-checked
against the drafted part envelopes (a fix round on the asm-draft thread when they disagree), then everything is published.
`revise` applies a reviewer's notes before anything is built; `amend` applies evaluator evidence to a built machine."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from itertools import count
from pathlib import Path
from typing import Any, get_args, get_origin

from pydantic import BaseModel

from opencad import worker
from opencad.contract import (
    ContractError,
    check_assembly_bundle,
    check_bundle,
    lint_assembly,
    load_assembly,
    publish_assembly,
    publish_bundle,
    stage_bundle,
)
from opencad.initialize import _inlined_sources, _type_name, copy_sources, draft_brief
from opencad.io import dump_json, load_json, sha256_file
from opencad.paths import (
    AMENDED,
    ASSEMBLY_FILE,
    BRIEF_FILE,
    CONTRACT_FILE,
    DESIGNS,
    DOCS,
    NESTED,
    REPO_ROOT,
    RESULTS,
    design_dir,
    membership,
)
from opencad.paths import results_dir as results_of
from opencad.sim.reduced import docs
from opencad.worker.profiles import lean_turns

EXEMPLAR = DOCS / "exemplar-assembly.yaml"
MAX_ROUNDS = 3
FIX_ROUNDS = 2
SHARED_MODELS = {"Parameter", "Frame", "Datum", "Envelope", "Quantity", "PointQuantity", "ClearanceSpec", "HardwareEnvelope", "ExcludeCylinder",
                 "Reference", "Units", "EditTest", "EditExpectation", "EditSweep"}


def staging(name: str) -> Path:
    return DESIGNS / f".staging-{name}"


def request_path(name: str) -> Path:
    return DESIGNS / f".codex-draft-{name}" / "request.json"


def save_request(name: str, intent: str, *, images: list[Path], notes: str = "", checks: list[tuple[str, str]] | None = None) -> Path:
    return dump_json(request_path(name), {"intent": intent, "images": [str(p) for p in images], "notes": notes, "checks": [list(c) for c in checks or []]})


def assembly_schema_digest() -> str:
    """AssemblyContract fields; models shared with PartContract are listed by field name only."""
    from opencad.schemas import AssemblyContract

    lines: list[str] = []
    seen: set[type] = set()

    def emit(model: type[BaseModel]) -> None:
        if model in seen:
            return
        seen.add(model)
        if model.__name__ in SHARED_MODELS:
            lines.append(f"{model.__name__}: as in PartContract ({', '.join(model.model_fields)})")
            return
        lines.append(f"{model.__name__}:")
        nested: list[type[BaseModel]] = []
        for fname, field in model.model_fields.items():
            lines.append(f"  {fname}: {_type_name(field.annotation)} ({'required' if field.is_required() else 'optional'})" + (f" — {field.description}" if field.description else ""))
            for arg in (field.annotation, *get_args(field.annotation or ())):
                for sub in (arg, *get_args(arg)):
                    origin = get_origin(sub) or sub
                    if isinstance(origin, type) and issubclass(origin, BaseModel):
                        nested.append(origin)
        for sub in nested:
            emit(sub)

    emit(AssemblyContract)
    return "\n".join(lines)


def asm_brief(stage: Path, name: str, intent: str, *, sources: list[dict[str, Any]], images: list[Path], notes: str = "",
              checks: list[tuple[str, str]] | None = None) -> str:
    listed, inlined = _inlined_sources(stage, sources) if lean_turns() else ("\n".join(f"- {stage / s['path']}" for s in sources), "")
    img_lines = "\n".join(f"- {Path(i).name} (attached as an image)" for i in images) or "- (none)"
    scored = ""
    if checks:
        scored = ("\nThe finished machine is scored on these predictions. Declare an `observables[]` entry for each (the id, quantity, unit, case, "
                  "location, averaging) and, unless the line says the evaluator measures it, the `simulations[]` entry that predicts it; take every "
                  "condition from the sources, this list carries no values:\n"
                  + "\n".join(f"- {kind} `{obs}`" for kind, obs in checks) + "\n")
    return f"""Draft the AssemblyContract and assembly brief for a new machine. Write BOTH files in place:
- `{stage / ASSEMBLY_FILE}` (currently the seeded template; replace its contents)
- `{stage / BRIEF_FILE}` (currently the template with placeholders; replace every placeholder)

Assembly name: `{name}`
Intent (verbatim from the user): {intent}

Sources (absolute paths):
{listed}
{inlined}
Images attached to this task:
{img_lines}
{("Notes from the orchestrator: " + notes) if notes else ""}

Schema digest (do not open `src/opencad`):

{assembly_schema_digest()}

Filled exemplar `{EXEMPLAR}` (a fictitious machine; copy the shape, not the machine):

```yaml
{EXEMPLAR.read_text(encoding='utf-8').rstrip()}
```
{scored}
Rules:
- Millimetres and degrees. The assembly `frame` is the frame of `datum_part`; `envelope` is the assembled bounding box at rest.
- `parts[]`: one entry per body instance (three rollers are three entries sharing one `design`). `modelled` parts name a design
  `{name}-<part>` and carry an `intent` a separate drafter will turn into that part's own contract: the part's own frame (origin, axes),
  every dimension the sources give, and the interfaces it provides (bores, seats, faces other parts touch). Choose each part's frame so
  its joint frames are simple (a gear or rotor axis along +z through its own origin). `purchased` parts (bearings, motors, fasteners,
  tubing) get `catalog` geometry (box or cylinder) in their own frame. A fluid region the analyses need is a `derived` part with
  `role: fluid` (the assembly source builds it) plus a `fluid_volumes[]` entry (walls, bodies inside, port caps with outward normals,
  a seed point at least 1 mm from every wall, a volume band). A supplied model that is not a physical body (a flow-region or cavity
  model) is a `purchased` part with a `catalog` STEP and `role: construction`: staged for the assembly source to build derived bodies
  from (a housing wall around it, the fluid inside it), never placed, and not referenced by joints, boundaries or fluid walls.
- `joints[]` form a tree rooted at `datum_part`: every other body is the child of exactly one joint. Frames are in each body's OWN
  frame (the part contract frame), not the assembly frame; `offset` is along the parent axis. Rigid joints need `ref` on both frames.
  State `ref` on a revolute joint when its rest phase matters (meshing gears) and set `angle`. A driven joint has a `drive`
  (motor speed, a per-case value key, or a speed history); a joint moved by another through gears or rollers is `free` and a
  `transmissions[]` entry couples them (ratio = driven / driver displacement, negative for an opposite sense; `mesh` for spur gears).
  A closed linkage (four-bar, crank-slider) is a tree plus one `closure: true` joint per loop at its last pin or guide: its two bodies
  are already placed through the tree, the evaluator solves the loop at every pose, and the tree joints' rest angles (`angle` with
  `ref`, or parameters) must be those that close it. Give a revolute closure joint no `ref` (its rest angle follows from the loop;
  with refs its `angle` must be the links' relative angle there); a slider closure needs refs. An epicyclic set names the carrier's joint as `carrier` on every planet mesh
  (sun to planet, and ring to planet with the ring on a rigid joint as the driver); a rack is a `gear` transmission from the pinion's
  revolute joint to the rack's slider joint (ratio in mm/deg).
- Kinematic observables are measured by the evaluator (no `simulation`): `transmission_ratio` (the whole train, or `body` for one
  output), `joint_value` (a `joint` at drive value `at`, or a series over an acceptance `motion`), `joint_range` (a `joint` over a
  `motion`), `point_x|y|z` (a point `location` on `body`, given in the assembly frame at rest, at `at` or over `motion`). Values are
  displacements from rest in deg or mm, positive about or along the joint's parent axis. Band each `expected` at 1e-5 of the value
  or wider: the evaluator measures rack pitch and positions on tessellated sections.
- `acceptance.motions[]`: drive each motor joint through the range that exercises every contact (one or two tooth pitches, one roller
  pass, a full stroke); `acceptance.clearances[]` for every pair that must not touch (min_gap) or must seat (max_gap).
- `boundaries[]`: named patches the analyses load (inlets, outlets, rotating walls, contact faces, fixed supports, heat-flux faces),
  selected by plane, cylinder, region, touching or rest, in the assembly frame at rest.
- `operating_cases[]`, `observables[]`, `simulations[]`: transcribe every operating condition, material property and boundary value from
  the sources as `inputs` with provenance (`stated` + `source`; `inferred`/`defaulted` + `rationale` + `uncertainty` only where the
  sources are silent, each also an open question). Never put a measured result in the contract: observables state what to predict,
  where and how averaged; `min`/`max`/`expected` only for a requirement the sources state or an analytic identity. The analysis
  adapters and the input names, settings and quantities each one reads (name inputs exactly so):

{docs()}

- `references[]`: one entry per file under `sources/` with sha256. `open_questions`: everything unresolved.

Brief (`brief.md`): keep the template's section headings and fill them (sources table with sha256, bill of materials, frames/joints/motion,
fluid regions and boundaries, the input record with provenance, defaults and open questions). No `REPLACE ME` or `<intent>` may remain.

Verification before you finish: `cd {REPO_ROOT} && .venv/bin/python -m opencad assembly check {stage} --name {name}` must print `ok:`;
fix every problem and every `warning:` line once. Do not write part contracts or any CAD; do not create other files in {stage}.
Under `## Result` list the bodies, joints, transmissions, cases and simulations; under `## Open questions` repeat the contract's.
Do not open `src/opencad`, `truth/` or `results/`.
"""


def part_notes(a: Any, design: str) -> str:
    bodies = [p for p in a.parts if p.design == design]
    frames = []
    for j in a.joints:
        for b in bodies:
            if j.child == b.name:
                frames.append(f"joint {j.name} ({j.kind}) attaches it at its own-frame point {list(j.child_frame.origin)} axis {list(j.child_frame.axis)}")
            if j.parent == b.name:
                frames.append(f"joint {j.name} ({j.kind}) mounts {j.child} on its own-frame point {list(j.parent_frame.origin)} axis {list(j.parent_frame.axis)}")
    return (f"This part is body {', '.join(b.name for b in bodies)} of the assembly `{a.name}` ({a.intent.strip()[:400]}). "
            f"Its contract frame must be the part's own frame stated in the intent, because the assembly places it by these joint frames: "
            + ("; ".join(frames) or "(no joints reference it)") + ". Draft only this part; other bodies are separate designs.")


def _pending_dirs(wp: worker.WorkerPending) -> list[Path]:
    return sorted({o.dir.parent.parent for o in wp.orders})


def _stage_part(design: str, sources: list[Path]) -> Path:
    st = staging(design)
    if not st.exists():
        stage_bundle(design)
    copy_sources(st, sources)
    return st


def _view(designs: list[str]) -> Path:
    """A designs root where each part design resolves to its staged bundle when one exists (a draft or a revision), else the published one
    (for the frame cross-check)."""
    root = Path(tempfile.mkdtemp(prefix="opencad-asm-view-"))
    for d in designs:
        src = staging(d) if (staging(d) / CONTRACT_FILE).exists() else design_dir(d)
        if (src / CONTRACT_FILE).exists():
            os.symlink(src, root / d)
    return root


def _cross_check(turn: Any, name: str, stage: Path, todo: list[str], thread: str | None, *, timeout: float | None,
                 key: str) -> tuple[list[str], list[dict[str, Any]], str | None]:
    """The staged assembly's joint frames against its part contracts, with up to FIX_ROUNDS fix turns on the drafter's thread; `todo`
    are the staged part designs the turns may edit. Returns the problems left, the fix rounds and the thread."""
    results_dir = RESULTS / name
    a = load_assembly(stage)
    fixes: list[dict[str, Any]] = []
    for k in range(1, FIX_ROUNDS + 2):
        view = _view(a.designs())
        try:
            cross, _ = lint_assembly(a, designs_root=view)
        finally:
            shutil.rmtree(view, ignore_errors=True)
        cross += [f"{d}: {p}" for d in todo for p in check_bundle(staging(d), d)]
        if not cross or k > FIX_ROUNDS:
            break
        msg = ("The part contracts were drafted from your part intents, and the assembly no longer agrees with them:\n- " + "\n- ".join(cross)
               + f"\nFix `{stage / ASSEMBLY_FILE}` (joint frames, offsets, envelope) or the part contract that misread its intent "
               + ", ".join(f"`{staging(d) / CONTRACT_FILE}`" for d in todo)
               + f". Re-run `.venv/bin/python -m opencad assembly check {stage} --name {name}` and `check-bundle` on every part you touched until both print ok.")
        r = turn(lambda msg=msg, k=k, thread=thread: worker.dispatch(msg, role="asm-draft", key=f"{key}-{k}", results_dir=results_dir, part=name, cd=stage,
                                                                     run_dir=stage.parent / f".codex-draft-{name}" / f"{key}-{k}", resume=thread, timeout=timeout,
                                                                     add_dirs=[staging(d) for d in todo],
                                                                     deliverables=[stage / ASSEMBLY_FILE, *[staging(d) / CONTRACT_FILE for d in todo]]))
        thread = r.thread_id or thread
        fixes.append({"round": k, "worker": r.summary(), "problems": cross})
        a = load_assembly(stage)
    return cross, fixes, thread


def _backup(name: str) -> Path:
    """Where a republished bundle's previous version is kept, the next free N: designs/<asm>/.amended/<leaf>-N for a part of an
    assembly, designs/<name>/.amended/assembly-N for the assembly itself, else designs/.amended-<name>-N."""
    m = membership().get(name)
    if m:
        base, stem = DESIGNS / m[0] / AMENDED, m[1]
    elif (DESIGNS / name / ASSEMBLY_FILE).exists():
        base, stem = DESIGNS / name / AMENDED, "assembly"
    else:
        base, stem = DESIGNS, f".amended-{name}"
    return next(base / f"{stem}-{i}" for i in count(1) if not (base / f"{stem}-{i}").exists())


def _own(root: Path):
    """copytree ignore: an assembly folder's own entries, not its nested parts and backups."""
    return lambda d, names: [n for n in names if n in NESTED] if Path(d) == root else []


def _retire(name: str, previous: Path) -> None:
    """Move a published bundle to its backup; an assembly leaves its nested parts and backups in place."""
    src = design_dir(name)
    previous.parent.mkdir(parents=True, exist_ok=True)
    if not (src / ASSEMBLY_FILE).exists():
        shutil.move(str(src), str(previous))
        return
    previous.mkdir()
    for p in src.iterdir():
        if p.name not in NESTED:
            shutil.move(str(p), str(previous / p.name))


def drafter_thread(results_dir: Path) -> str | None:
    """The agent of the latest dispatched asm-draft order, so an amendment continues the drafter's thread."""
    from opencad.worker import orders

    for o in sorted(orders.list_orders(results_dir), key=lambda o: o.id, reverse=True):
        rec = (load_json(o.dispatch_path) or {}) if o.role == "asm-draft" and o.dispatch_path.exists() else {}
        if rec.get("agent_id"):
            return str(rec["agent_id"])
    return None


def amend(turn: Any, name: str, note: str, *, timeout: float | None = None) -> dict[str, Any]:
    """An engineering change on the published assembly contract, from evaluator evidence that the placements cannot fix."""
    from opencad.worker import orders

    stage = staging(name)
    results_dir = RESULTS / name
    ecr = sorted((o for o in orders.list_orders(results_dir) if o.key.startswith("asm-ecr-") and o.status != "superseded"), key=lambda o: o.id)
    published = DESIGNS / name / ASSEMBLY_FILE
    finished = (bool(ecr) and (ecr[-1].dir / "done").exists() and (stage / ASSEMBLY_FILE).exists() and published.exists()
                and (stage / ASSEMBLY_FILE).read_bytes() != published.read_bytes())
    summary: dict[str, Any] = {"resumed": ecr[-1].id} if finished else {}
    if not finished:  # a finished amendment interrupted before publishing keeps its staged edits
        if stage.exists():
            shutil.rmtree(stage)
        shutil.copytree(DESIGNS / name, stage, ignore=_own(DESIGNS / name))
        n = 1 + len(ecr)
        msg = (f"Engineering change on the published assembly `{name}`. With the parts placed exactly on your joint frames, the evaluator reports:\n\n{note}\n\n"
               f"Revise `{stage / ASSEMBLY_FILE}` where this evidence shows the contract itself is wrong (joint frames and offsets, clearances, tolerances, "
               "envelope, observables and their bodies). Keep every stated source value and do not change part designs or their intents. Record each "
               f"change and the evidence for it under `open_questions`. Re-run `.venv/bin/python -m opencad assembly check {stage} --name {name}` until it "
               "prints ok.")
        r = turn(lambda: worker.dispatch(msg, role="asm-draft", key=f"asm-ecr-{n}", results_dir=results_dir, part=name, cd=stage,
                                         run_dir=stage.parent / f".codex-draft-{name}" / f"ecr-{n}", resume=drafter_thread(results_dir), timeout=timeout,
                                         deliverables=[stage / ASSEMBLY_FILE]))
        summary = r.summary()
    problems = check_assembly_bundle(stage, name)
    if problems:
        return {"ok": False, "problems": problems, "worker": summary}
    previous = _backup(name)
    _retire(name, previous)
    publish_assembly(stage, name)
    return {"ok": True, "worker": summary, "previous": str(previous)}


REVISED = (ASSEMBLY_FILE, CONTRACT_FILE, BRIEF_FILE)
PART_STALE = ("blockout.json", "blockout", "handoff", "pipeline-state.json")


def _changed(staged: Path, published: Path) -> bool:
    return any((staged / f).exists() and (not (published / f).exists() or (staged / f).read_bytes() != (published / f).read_bytes()) for f in REVISED)


def revise(turn: Any, name: str, note: str, *, timeout: float | None = None) -> dict[str, Any]:
    """A revision before anything is built, from the reviewer's notes: one asm-draft turn on the drafter's thread may edit the assembly and
    any part contract (all staged), the frames are cross-checked again, and each changed bundle is republished (its previous version kept
    as designs/.amended-<name>-N) with that part's blockout and build results removed, so the checkpoint redoes them."""
    from opencad.worker import orders

    if not (DESIGNS / name / ASSEMBLY_FILE).exists():
        return {"ok": False, "problems": [f"{DESIGNS / name} is not published; draft it first (`assembly drive {name} --stop-after draft`)"]}
    stage, results_dir = staging(name), RESULTS / name
    designs = load_assembly(DESIGNS / name).designs()
    everything = [name, *designs]
    marker = results_dir / "revise-pending.json"
    done = [int(o.key.rsplit("-", 1)[1]) for o in orders.list_orders(results_dir) if re.fullmatch(r"asm-revise-\d+", o.key) and o.status != "superseded"]
    pending = load_json(marker).get("revision") if marker.exists() and stage.exists() else None
    n = pending or max(done, default=0) + 1  # an interrupted revision keeps its staged edits and its order key
    if pending is None:
        for d in everything:
            shutil.rmtree(staging(d), ignore_errors=True)
            shutil.copytree(design_dir(d), staging(d), ignore=_own(design_dir(d)))
        dump_json(marker, {"revision": n})
    msg = (f"Revision before anything is built. The reviewer read the drafted assembly `{name}`, its part contracts and their blockouts, and asks "
           f"for these changes:\n\n{note}\n\n"
           f"Edit only the staged copies: the assembly `{stage / ASSEMBLY_FILE}` and `{stage / BRIEF_FILE}`, and for a change that concerns a part, "
           f"that part's `{CONTRACT_FILE}` and `{BRIEF_FILE}` in its staged directory ({', '.join(f'`{staging(d)}`' for d in designs)}), keeping the "
           "part's `intent` in the assembly and its contract in agreement. Keep every stated source value the notes do not correct. Record each change "
           f"and its reason under that file's `open_questions` (\"Changed (revision {n}, reviewer notes): ...\"). Re-run `.venv/bin/python -m opencad "
           f"assembly check {stage} --name {name}`, and `.venv/bin/python -m opencad check-bundle <staged dir> --name <part>` for every part you "
           "touched, until each prints ok.")
    thread = drafter_thread(results_dir)
    r = turn(lambda: worker.dispatch(msg, role="asm-draft", key=f"asm-revise-{n}", results_dir=results_dir, part=name, cd=stage,
                                     run_dir=stage.parent / f".codex-draft-{name}" / f"revise-{n}", resume=thread, timeout=timeout,
                                     add_dirs=[staging(d) for d in designs], deliverables=[stage / ASSEMBLY_FILE]))
    cross, fixes, _ = _cross_check(turn, name, stage, designs, r.thread_id or thread, timeout=timeout, key=f"asm-revise-{n}-fix")
    problems = cross or check_assembly_bundle(stage, name)
    out: dict[str, Any] = {"revision": n, "worker": r.summary(), "fixes": fixes}
    if problems:
        for d in everything:
            shutil.rmtree(staging(d), ignore_errors=True)
        marker.unlink(missing_ok=True)
        return {**out, "ok": False, "problems": problems}
    changed, previous = [], {}
    for d in designs:
        if not _changed(staging(d), design_dir(d)):
            shutil.rmtree(staging(d))
            continue
        previous[d] = str(_backup(d))
        _retire(d, Path(previous[d]))
        publish_bundle(staging(d), d)
        for art in PART_STALE:
            p = results_of(d) / art
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink(missing_ok=True)
        orders.supersede(results_of(d), "blockout-")  # a live finished order would be taken as the redone blockout
        changed.append(d)
    if _changed(stage, DESIGNS / name):
        previous[name] = str(_backup(name))
        _retire(name, Path(previous[name]))
        publish_assembly(stage, name)
        changed.insert(0, name)
    else:
        shutil.rmtree(stage)
    marker.unlink(missing_ok=True)
    shutil.rmtree(DESIGNS / f".codex-draft-{name}", ignore_errors=True)
    return {**out, "ok": True, "changed": changed, "previous": previous}


def run(turn: Any, name: str, *, timeout: float | None = None) -> dict[str, Any]:
    """`turn(fn)` runs fn until its worker orders are done (the driver waits on done files and emits EVENT lines)."""
    if (DESIGNS / name / ASSEMBLY_FILE).exists():
        return {"ok": True, "skipped": "published"}
    stage = staging(name)
    if not (stage / ASSEMBLY_FILE).exists():
        raise ContractError(f"{stage} is not staged; run `python -m opencad assembly stage {name} --intent ... --source ...` first")
    req = load_json(request_path(name)) if request_path(name).exists() else {}
    intent = req.get("intent") or load_assembly(stage).intent
    images = [Path(p) for p in req.get("images") or []]
    checks = [tuple(c) for c in req.get("checks") or []]
    sources = [{"path": f"sources/{p.name}", "sha256": sha256_file(p), "suffix": p.suffix.lower()} for p in sorted((stage / "sources").iterdir()) if p.is_file()]
    results_dir = RESULTS / name
    rounds: list[dict[str, Any]] = []
    problems = ["not yet drafted"]
    thread: str | None = None
    for i in range(1, MAX_ROUNDS + 1):
        msg = (asm_brief(stage, name, intent, sources=sources, images=images, notes=req.get("notes", ""), checks=checks) if thread is None else
               "The assembly bundle is not yet publishable. `python -m opencad assembly check` reports:\n- " + "\n- ".join(problems)
               + "\nFix assembly.yaml and/or brief.md in place and re-run the check until it prints ok.")
        r = turn(lambda msg=msg, i=i, thread=thread: worker.dispatch(msg, role="asm-draft", key=f"asm-draft-{i}", results_dir=results_dir, part=name, cd=stage,
                                                                     run_dir=stage.parent / f".codex-draft-{name}" / f"round-{i}", images=images if thread is None else None,
                                                                     resume=thread, timeout=timeout, deliverables=[stage / ASSEMBLY_FILE, stage / BRIEF_FILE]))
        thread = r.thread_id or thread
        problems = check_assembly_bundle(stage, name)
        rounds.append({"round": i, "worker": r.summary(), "problems": problems})
        if not problems:
            break
    if problems:
        return {"ok": False, "stage": "asm-draft", "rounds": rounds, "problems": problems}
    a = load_assembly(stage)
    src_files = [stage / s["path"] for s in sources]
    todo = [d for d in a.designs() if not (design_dir(d) / CONTRACT_FILE).exists()]
    part_rounds: dict[str, list[dict[str, Any]]] = {d: [] for d in todo}
    part_problems: dict[str, list[str]] = {d: ["not yet drafted"] for d in todo}
    threads: dict[str, str | None] = {d: None for d in todo}
    for i in range(1, MAX_ROUNDS + 1):
        batch = [d for d in todo if part_problems[d]]
        if not batch:
            break
        specs = []
        for d in batch:
            st = _stage_part(d, src_files)
            part = next(p for p in a.parts if p.design == d)
            copied = [{"path": f"sources/{p.name}", "sha256": sha256_file(st / "sources" / p.name), "suffix": p.suffix.lower()} for p in src_files]
            msg = (draft_brief(st, d, part.intent, sources=copied, images=images, notes=part_notes(a, d)) if threads[d] is None else
                   "The bundle is not yet publishable. `python -m opencad check-bundle` reports:\n- " + "\n- ".join(part_problems[d])
                   + "\nFix contract.yaml and/or brief.md in place and re-run the check until it prints ok.")
            specs.append({"brief": msg, "role": "draft", "key": f"draft-{i}", "results_dir": results_of(d), "part": d, "cd": st,
                          "run_dir": DESIGNS / f".codex-draft-{d}" / f"round-{i}", "images": images if threads[d] is None else None, "resume": threads[d],
                          "timeout": timeout, "deliverables": [st / CONTRACT_FILE, st / BRIEF_FILE], "budget": worker.scaled_budget("draft", len(src_files))})
        results = turn(lambda specs=specs: worker.dispatch_many(specs))
        for d, r in zip(batch, results):
            threads[d] = r.thread_id or threads[d]
            part_problems[d] = check_bundle(staging(d), d)
            part_rounds[d].append({"round": i, "worker": r.summary(), "problems": part_problems[d]})
    failed = {d: p for d, p in part_problems.items() if p}
    if failed:
        return {"ok": False, "stage": "part-draft", "rounds": rounds, "parts": part_rounds, "problems": [f"{d}: {p}" for d, ps in failed.items() for p in ps]}
    cross, fixes, thread = _cross_check(turn, name, stage, todo, thread, timeout=timeout, key="asm-fix")
    if cross:
        return {"ok": False, "stage": "cross-check", "rounds": rounds, "parts": part_rounds, "fixes": fixes, "problems": cross}
    for d in todo:
        publish_bundle(staging(d), d)
    problems = check_assembly_bundle(stage, name)
    if problems:
        return {"ok": False, "stage": "publish", "problems": problems}
    publish_assembly(stage, name)
    shutil.rmtree(DESIGNS / f".codex-draft-{name}", ignore_errors=True)
    for d in todo:
        shutil.rmtree(DESIGNS / f".codex-draft-{d}", ignore_errors=True)
    return {"ok": True, "rounds": rounds, "parts": part_rounds, "fixes": fixes, "published": [name, *todo], "thread_id": thread}


def stage_request(name: str, intent: str, sources: list[Path], images: list[Path], notes: str = "", checks: list[tuple[str, str]] | None = None) -> Path:
    """`python -m opencad assembly stage`: designs/.staging-<name>/ with the sources copied in and the request recorded."""
    from opencad.contract import stage_assembly

    st = staging(name)
    if not st.exists():
        st = stage_assembly(name)
    copy_sources(st, [*sources, *images])
    save_request(name, intent, images=[st / "sources" / Path(i).name for i in images], notes=notes, checks=checks)
    return st

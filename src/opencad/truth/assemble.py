"""`python -m opencad.truth assemble <case>`: a held-out assembly task (Fusion 360 Gallery joint set) run live.

The agent gets both STEP bodies in their local frames, the task text and the evaluator renders in
results/<case>/work/ and must write `assembly.yaml` there (a placement per body). The dataset joint
(truth/joint_set.json) is sequestered while Codex works; afterwards the manifest is scored with
`opencad.truth.assembly_task.score`, a scorecard is written and an attempt is logged. No KCL, no
hosted engine: the evaluator applies the transforms in OpenCascade.
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any

import yaml

from opencad import worker
from opencad.io import dump_json, load_json, utc_now
from opencad.orchestrator import PipelineError
from opencad.paths import REPO_ROOT, RESULTS, part_dir
from opencad.truth import assembly_agree, assembly_task
from opencad.truth.manifest import case_dir
from opencad.truth.runner import Sequester, case_file, case_lock, log_attempt
from opencad.worker import WorkerPending
from opencad.worker.result import WorkerResult


def _joint_set(case: Path, seq: Sequester) -> Path:
    """Score from the vault while another concurrent holder still has truth sequestered."""
    live = case / "truth" / "joint_set.json"
    if live.exists():
        return live
    return Path(seq.dst) / "truth" / "joint_set.json"


def _worker_from_card(card: dict[str, Any], fallback_dir: Path) -> WorkerResult:
    w = card.get("worker") or {}
    return WorkerResult(
        thread_id=str(w.get("thread_id") or ""),
        exit_code=int(w.get("exit_code") or 0),
        seconds=float(w.get("seconds") or 0),
        commands=int(w.get("commands") or 0),
        usage=dict(w.get("usage") or {}),
        run_dir=Path(w.get("run_dir") or fallback_dir),
        result_md="",
        failure=str(w.get("failure") or ""),
        backend=str(w.get("backend") or "cursor"),
        role=str(w.get("role") or "assemble"),
        model=str(w.get("model") or ""),
        order_id=w.get("order_id"),
        metrics=dict(w.get("metrics") or {}),
    )


def load_task(case_id: str) -> dict[str, Any]:
    p = case_dir(case_id) / "task.yaml"
    if not p.exists():
        raise PipelineError(f"{case_id} has no task.yaml (assembly cases are task-driven, not manifest-driven)")
    task = yaml.safe_load(p.read_text(encoding="utf-8"))
    if task.get("kind") != "assembly":
        raise PipelineError(f"{case_id}: task kind {task.get('kind')!r} is not 'assembly'")
    return task


def brief(work: Path, task: dict[str, Any], renders: list[Path]) -> str:
    bodies = task["bodies"]
    steps = ", ".join(f"`{work / f'{b}.step'}`" for b in bodies)
    return f"""Assembly placement task. Read `{work / 'assembly-task.md'}` first: it names the two bodies, the joint type, the joint
faces and, for each face, the joint **key point** in the body's local frame and the axis direction; `{work / 'joint-task.json'}`
holds the same numbers. The bodies are {steps}, each in its own local frame (millimetres). Deliverable: `{work / 'assembly.yaml'}`
with a rigid placement for each body in one shared frame, exactly in the format the task describes (`origin` + `x_axis`,
`y_axis`, `z_axis`, or `matrix: 4x4`; body two may stay at the identity).

Method (a computation, then a check):
- The placement is defined by the key points: choose a rigid transform for body one so that its joint axis (through K1 along
  d1) becomes colinear with body two's (through K2 along d2), with d1' anti-parallel to d2' when `is_flipped` is true and
  parallel otherwise, and with (K1' - K2') . d2' equal to the stated `offset`. Any rotation about a revolute axis is
  acceptable (a slider's axial position is the offset).
- Verify with the local critic, which computes exactly the evaluator's numbers without the truth:
  `cd {REPO_ROOT} && .venv/bin/python -m opencad.truth assembly-check {work}` (axis angle, line distance, axial offset vs
  offset, interference, gap, and whether the flip matches). Iterate until every line reads ok.
- Interference: the dataset's own assembled pose may interpenetrate slightly (a pin tip past a bore bottom); the evaluator
  allows the dataset's interference plus 1 mm3, so do not move the bodies off their key points to remove a small overlap; report it.
- Measuring, if you need to: OpenCascade from the repository's virtualenv, e.g.
  `.venv/bin/python -c "from pathlib import Path; from opencad.geomcheck import brep; s = brep.read_step(Path('...')); print(brep.bbox(s)); print(brep.cylinders(s))"`
  (`brep.cylinders` lists every cylindrical face with axis point, direction, radius, extent and hole/pin kind). The renders in
  `{work / 'renders'}` show each body from the front, top and an isometric view.
- Do not modify the STEP files. Do not write anywhere except `{work}`.

Report under `## Result` the transforms you chose and the critic's numbers (axis angle, line distance, axial offset, interference,
gap); under `## Open questions` any ambiguity you resolved by assumption.
"""


def default_mode() -> str:
    from opencad.backends.registry import current_id

    return "placement" if current_id() == "zoo" else "modelled"


def modelled_brief(work: Path, parts: Path, task: dict[str, Any], backend: str) -> str:
    bodies = task["bodies"]
    steps = ", ".join(f"`inputs/{b}.step`" for b in bodies)
    entry = parts / "main.py"
    keys = ", ".join(f'"{b}"' for b in bodies)
    return f"""Assembly modelling task (backend `{backend}`). Read `{work / 'assembly-task.md'}` first: it names the two bodies, the joint
type, the joint faces and, for each face, the joint **key point** in the body's local frame and the axis direction;
`{work / 'joint-task.json'}` holds the same numbers. The same two STEP bodies are at `{parts / 'inputs'}` ({steps}), each in
its own local frame (millimetres).

Deliverable: `{entry}` that:
- imports only those two `inputs/<body>.step` files (no other CAD files, nothing under `truth/`);
- places them with this backend's API so the joint axes and offset match the task;
- assigns `result` to the two placed bodies (list/tuple, not a fused union);
- assigns `placements` to a dict `{keys}: <4x4 row-major millimetre matrix>` for each body.

Method (a computation, then a check):
- Choose a rigid transform for body one so that its joint axis (through K1 along d1) becomes colinear with body two's
  (through K2 along d2), with d1' anti-parallel to d2' when `is_flipped` is true and parallel otherwise, and with
  (K1' - K2') . d2' equal to the stated `offset`. Body two may stay at the identity. Any rotation about a revolute axis
  is acceptable.
- Format with `ruff format --check` and `ruff check`. Then verify with the local critic (the Worker protocol prints the
  exact command with `--entry` / `--ledger`): it exports through the engine, derives `assembly.yaml` from `placements`,
  and prints the evaluator's joint numbers plus export-agreement lines. Open `assembly-views.png` and write one `Visual:`
  line. Iterate until every line reads ok.
- Interference: the dataset's own assembled pose may interpenetrate slightly; do not move the bodies off their key points
  to remove a small overlap; report it.
- Measuring, if you need to: OpenCascade from the repository virtualenv, e.g.
  `.venv/bin/python -c "from pathlib import Path; from opencad.geomcheck import brep; s = brep.read_step(Path('...')); print(brep.bbox(s)); print(brep.cylinders(s))"`.
  The renders in `{work / 'renders'}` show each body from the front, top and an isometric view.
- Do not modify the STEP files. Write only under `{parts}` (and protocol files).

Report under `## Result` the transforms you chose, the critic's joint numbers, and the agreement numbers; under
`## Open questions` any ambiguity you resolved by assumption.
"""


def _stage_parts(case_id: str, task: dict[str, Any], work: Path) -> Path:
    dest = part_dir(case_id)
    inp = dest / "inputs"
    inp.mkdir(parents=True, exist_ok=True)
    for b in task["bodies"]:
        src = work / f"{b}.step"
        if src.exists():
            shutil.copy2(src, inp / f"{b}.step")
    return dest


def verify_modelled(case_id: str, task: dict[str, Any], parts: Path, work: Path, out: Path) -> dict[str, Any]:
    """Ruff, hygiene, analyze, export, placements → yaml, agreement, integrity, local joint critic."""
    from opencad.backends.placements import read_placements
    from opencad.backends.pythonlang import ruff_check, ruff_format_check
    from opencad.backends.registry import get
    from opencad.truth import assembly_check

    entry = parts / "main.py"
    fmt = ruff_format_check(parts)
    lint = ruff_check(parts)
    hyg = assembly_agree.hygiene(parts, list(task["bodies"]))
    program_executes = False
    analyze: dict[str, Any] = {}
    placements = None
    agreement: dict[str, Any] = {}
    integ: dict[str, Any] = {}
    critic: dict[str, Any] = {}
    solid_count = None
    error = None
    if entry.exists():
        try:
            eng = get().engine
            analyze = eng.analyze(entry)
            program_executes = True
            exp = out / "export"
            step = eng.export(entry, exp, "step")[0]
            stl = eng.export(entry, exp, "stl")[0]
            try:
                eng.export(entry, exp, "glb")
            except Exception:
                pass
            placements = read_placements(exp / "placements.json")
            if placements:
                assembly_agree.write_yaml(work / "assembly.yaml", placements)
            from opencad.geomcheck import brep

            step_info = brep.analyze_step(step)
            solid_count = step_info["solids"]
            integ = assembly_agree.integrity(step, stl, expected_solids=2)
            if placements:
                agreement = assembly_agree.agree(
                    step,
                    {b: work / f"{b}.step" for b in task["bodies"]},
                    placements,
                    bodies_dir=exp / "bodies",
                )
            if (work / "assembly.yaml").exists():
                critic = assembly_check.check(work)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
    ok = bool(
        program_executes
        and fmt.get("ok")
        and lint.get("ok")
        and hyg.get("ok")
        and solid_count == 2
        and integ.get("ok")
        and agreement.get("ok")
        and critic.get("ok")
        and not error
    )
    return {
        "ok": ok,
        "program_executes": program_executes,
        "solid_count": {"measured": solid_count, "expected": 2, "ok": solid_count == 2},
        "export_agreement": agreement,
        "export_integrity": integ,
        "hygiene": hyg,
        "ruff_format": fmt,
        "ruff_check": lint,
        "critic": critic,
        "analyze": analyze,
        "error": error,
        "placements": placements,
    }


def _correction_brief(work: Path, parts: Path, prog: dict[str, Any], backend: str) -> str:
    fails = []
    if not prog.get("program_executes"):
        fails.append(f"program did not execute: {prog.get('error')}")
    if not (prog.get("ruff_format") or {}).get("ok"):
        fails.append(f"ruff format: {(prog.get('ruff_format') or {}).get('findings')}")
    if not (prog.get("ruff_check") or {}).get("ok"):
        fails.append(f"ruff check: {(prog.get('ruff_check') or {}).get('output')}")
    if not (prog.get("hygiene") or {}).get("ok"):
        fails.append(f"hygiene: {prog.get('hygiene')}")
    if not (prog.get("solid_count") or {}).get("ok"):
        fails.append(f"solid_count: {prog.get('solid_count')}")
    if not (prog.get("export_agreement") or {}).get("ok"):
        fails.append(f"export_agreement: {prog.get('export_agreement')}")
    if not (prog.get("export_integrity") or {}).get("ok"):
        fails.append(f"export_integrity: {prog.get('export_integrity')}")
    if not (prog.get("critic") or {}).get("ok"):
        fails.append(f"joint critic: {prog.get('critic')}")
    bullets = "\n".join(f"- {x}" for x in fails) or "- unknown failure"
    return f"""Correction-1 for the modelled assembly (`{backend}`). `{parts / 'main.py'}` executed or was attempted; these checks failed:

{bullets}

Keep the two `inputs/<body>.step` imports. Fix the placement and/or `placements` dict so `assembly-check --entry` prints
every line ok. Write only under `{parts}`. Open `assembly-views.png` and write one `Visual:` line.
"""


def run_assembly(
    case_id: str,
    *,
    force: bool = False,
    timeout: float | None = None,
    cont: bool = False,
    mode: str | None = None,
) -> dict[str, Any]:
    """`cont=True` continues an attempt interrupted by a worker handback (the joint truth stays vaulted until scoring)."""
    mode = mode or default_mode()
    if mode not in ("placement", "modelled"):
        raise PipelineError(f"assemble mode must be placement or modelled, got {mode!r}")
    task = load_task(case_id)
    if mode == "placement":
        return _run_placement(case_id, task, force=force, timeout=timeout, cont=cont)
    return _run_modelled(case_id, task, force=force, timeout=timeout, cont=cont)


def _run_placement(case_id: str, task: dict[str, Any], *, force: bool, timeout: float | None, cont: bool) -> dict[str, Any]:
    task = load_task(case_id)
    case = case_dir(case_id)
    out = RESULTS / case_id
    work = out / "work"
    state_path = out / "attempt-state.json"
    if cont:
        if not state_path.exists():
            raise PipelineError(f"{state_path} missing: nothing to continue for {case_id}")
        st = load_json(state_path)
        entry: dict[str, Any] = st["entry"]
        t0 = float(st["t0"])
        renders = [Path(p) for p in st["renders"]]
        seq = Sequester.attach(case_id, Path(st["vault"]))
    else:
        if out.exists():
            if not force:
                raise PipelineError(f"{out} exists; pass --force to redo the attempt")
            shutil.rmtree(out)
        (work / "renders").mkdir(parents=True)
        for rel in task["inputs"]:
            shutil.copy2(case / rel, work / Path(rel).name)
        renders = []
        for p in sorted((case / "inputs" / "renders").glob("*")):
            shutil.copy2(p, work / "renders" / p.name)
            if p.suffix.lower() == ".png":
                renders.append(work / "renders" / p.name)
        entry = {"started": utc_now(), "arm": "assembly", "design": case_id, "stage_reached": "init", "force": force}
        t0 = time.time()
        seq = Sequester(case_id)
    with seq:
        entry["truth_sequestered_to"] = str(seq.dst)
        try:
            r = worker.dispatch(brief(work, task, renders), role="assemble", key="assemble", results_dir=out, part=case_id, cd=work, run_dir=out / "codex",
                                images=renders, timeout=timeout, deliverables=[work / "assembly.yaml"])
        except WorkerPending as wp:
            seq.keep()  # truth stays vaulted while the worker places the bodies
            dump_json(state_path, {"entry": entry, "t0": t0, "renders": [str(p) for p in renders], "vault": str(seq.dst), "order": str(wp.order.dir)})
            raise
    state_path.unlink(missing_ok=True)
    entry["worker"] = entry["codex"] = r.summary()
    entry["codex_report"] = r.sections
    entry["stage_reached"] = "assembled" if (work / "assembly.yaml").exists() else "no-manifest"
    card: dict[str, Any] = {"case": case_id, "scored_at": utc_now(), "worker": r.summary(), "codex": r.summary()}
    manifest = work / "assembly.yaml"
    if manifest.exists():
        try:
            card.update(assembly_task.score(_joint_set(case, seq), {b: work / f"{b}.step" for b in task["bodies"]}, manifest))
            card["manifest"] = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        except Exception as e:  # a scorer failure is a failed attempt, recorded, never hidden
            card.update(ok=False, error=f"{type(e).__name__}: {e}")
    else:
        card.update(ok=False, error="the worker wrote no assembly.yaml", codex_failure=r.failure)
    card["verdict"] = "PASS" if card.get("ok") else "FAIL"
    card["mode"] = "placement"
    if manifest.exists() and (work / "joint-task.json").exists():
        # visual verification for every scored attempt: GLB with the joint animated, HTML viewer; the dataset pose as a ghost node
        from opencad.truth import assembly_viz

        try:
            card["viz"] = assembly_viz.generate(work, out / "handoff", card=card, truth_joint_set=_joint_set(case, seq))
        except Exception as e:  # visuals never change the verdict
            card["viz"] = {"error": f"{type(e).__name__}: {e}"}
    stamp = card["scored_at"].replace(":", "").replace("-", "")
    from opencad.backends.registry import current_id

    be = current_id()
    with case_lock(case_id):
        cards = case_file(case_id, "scorecards", tree=case)
        cards.mkdir(parents=True, exist_ok=True)
        dump_json(cards / f"assembly@{be}-{stamp}.json", card)
        dump_json(cards / f"assembly@{be}-latest.json", card)
        dump_json(cards / "assembly-latest.json", card)  # historical alias
    dump_json(out / "scorecard.json", card)
    entry["scorecard"] = {"verdict": card["verdict"], "checks": {k: v.get("ok") for k, v in (card.get("checks") or {}).items()}, "error": card.get("error")}
    entry["stage_reached"] = "scored"
    entry["seconds"] = round(time.time() - t0)
    entry["finished"] = utc_now()
    log_attempt(case_id, entry)
    print(f"assembly {case_id}: {card['verdict']} " + (", ".join(f"{k}={('ok' if v['ok'] else 'FAIL') if 'ok' in v else 'info'}" for k, v in (card.get("checks") or {}).items()) or card.get("error", "")))
    if isinstance(card.get("viz"), dict) and card["viz"].get("html"):
        print(f"  visual check: {card['viz']['html']} (glb alongside)")
    return card


def _run_modelled(case_id: str, task: dict[str, Any], *, force: bool, timeout: float | None, cont: bool) -> dict[str, Any]:
    from opencad.backends.registry import current_id

    be = current_id()
    case = case_dir(case_id)
    out = RESULTS / case_id
    work = out / "work"
    state_path = out / "attempt-state.json"
    skip_worker = False
    r: WorkerResult | None = None
    if cont:
        if state_path.exists():
            st = load_json(state_path)
            entry: dict[str, Any] = st["entry"]
            t0 = float(st["t0"])
            renders = [Path(p) for p in st["renders"]]
            seq = Sequester.attach(case_id, Path(st["vault"]))
            parts = Path(st["parts"]) if st.get("parts") else _stage_parts(case_id, task, work)
        elif (part_dir(case_id) / "main.py").exists():
            parts = part_dir(case_id)
            renders = [p for p in sorted((work / "renders").glob("*.png"))]
            prev = load_json(out / "scorecard.json") if (out / "scorecard.json").exists() else {}
            entry = {
                "started": utc_now(),
                "arm": "assembly",
                "design": case_id,
                "stage_reached": "rescore",
                "mode": "modelled",
                "backend": be,
                "rescore": True,
            }
            t0 = time.time()
            seq = Sequester(case_id)
            skip_worker = True
            r = _worker_from_card(prev, out / "worker")
        else:
            raise PipelineError(f"{state_path} missing: nothing to continue for {case_id}")
    else:
        if out.exists():
            if not force:
                raise PipelineError(f"{out} exists; pass --force to redo the attempt")
            shutil.rmtree(out)
        (work / "renders").mkdir(parents=True)
        for rel in task["inputs"]:
            shutil.copy2(case / rel, work / Path(rel).name)
        renders = []
        for p in sorted((case / "inputs" / "renders").glob("*")):
            shutil.copy2(p, work / "renders" / p.name)
            if p.suffix.lower() == ".png":
                renders.append(work / "renders" / p.name)
        parts = _stage_parts(case_id, task, work)
        entry = {
            "started": utc_now(),
            "arm": "assembly",
            "design": case_id,
            "stage_reached": "init",
            "force": force,
            "mode": "modelled",
            "backend": be,
        }
        t0 = time.time()
        seq = Sequester(case_id)
    entry_py = parts / "main.py"
    ctx = {"work": str(work), "entry": str(entry_py), "views": "assembly-views.png"}

    def _pending(wp: WorkerPending) -> None:
        seq.keep()
        dump_json(
            state_path,
            {
                "entry": entry,
                "t0": t0,
                "renders": [str(p) for p in renders],
                "vault": str(seq.dst),
                "order": str(wp.order.dir),
                "mode": "modelled",
                "parts": str(parts),
            },
        )

    with seq:
        entry["truth_sequestered_to"] = str(seq.dst)
        try:
            if skip_worker:
                prog = verify_modelled(case_id, task, parts, work, out)
            else:
                r = worker.dispatch(
                    modelled_brief(work, parts, task, be),
                    role="assemble",
                    key="assemble",
                    results_dir=out,
                    part=case_id,
                    cd=parts,
                    run_dir=out / "codex",
                    images=renders,
                    timeout=timeout,
                    deliverables=[entry_py],
                    add_dirs=[parts, work],
                    context=ctx,
                )
                prog = verify_modelled(case_id, task, parts, work, out)
                if not prog.get("ok"):
                    r = worker.dispatch(
                        _correction_brief(work, parts, prog, be),
                        role="correction",
                        key="correction-1",
                        results_dir=out,
                        part=case_id,
                        cd=parts,
                        run_dir=out / "codex-correction",
                        images=renders,
                        timeout=timeout,
                        deliverables=[entry_py],
                        add_dirs=[parts, work],
                        context=ctx,
                    )
                    prog = verify_modelled(case_id, task, parts, work, out)
        except WorkerPending as wp:
            _pending(wp)
            raise
    state_path.unlink(missing_ok=True)
    entry["worker"] = entry["codex"] = r.summary()
    entry["codex_report"] = r.sections
    entry["stage_reached"] = "assembled" if (work / "assembly.yaml").exists() else "no-manifest"
    card: dict[str, Any] = {
        "case": case_id,
        "scored_at": utc_now(),
        "worker": r.summary(),
        "codex": r.summary(),
        "mode": "modelled",
        "program_executes": prog.get("program_executes"),
        "solid_count": prog.get("solid_count"),
        "export_agreement": prog.get("export_agreement"),
        "export_integrity": prog.get("export_integrity"),
        "hygiene": prog.get("hygiene"),
    }
    if prog.get("error"):
        card["program_error"] = prog["error"]
    manifest = work / "assembly.yaml"
    joint_ok = False
    if manifest.exists():
        try:
            card.update(
                assembly_task.score(
                    _joint_set(case, seq),
                    {b: work / f"{b}.step" for b in task["bodies"]},
                    manifest,
                )
            )
            card["manifest"] = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            joint_ok = bool(card.get("ok"))
        except Exception as e:
            card.update(ok=False, error=f"{type(e).__name__}: {e}")
    else:
        card.update(ok=False, error="no assembly.yaml (placements missing or program failed)", codex_failure=r.failure)
    all_ok = bool(
        joint_ok
        and prog.get("ok")
        and prog.get("program_executes")
        and (prog.get("solid_count") or {}).get("ok")
        and (prog.get("export_agreement") or {}).get("ok")
        and (prog.get("export_integrity") or {}).get("ok")
        and (prog.get("hygiene") or {}).get("ok")
    )
    card["ok"] = all_ok
    card["verdict"] = "PASS" if all_ok else "FAIL"
    if manifest.exists() and (work / "joint-task.json").exists():
        from opencad.truth import assembly_viz

        placed = {}
        bodies_dir = out / "export" / "bodies"
        if bodies_dir.exists():
            placed = {p.stem: p for p in bodies_dir.glob("*.step")}
        native = out / "export" / "main.glb"
        try:
            card["viz"] = assembly_viz.generate(
                work,
                out / "handoff",
                card=card,
                truth_joint_set=_joint_set(case, seq),
                placed_steps=placed or None,
                native_glb=native if native.exists() else None,
            )
        except Exception as e:
            card["viz"] = {"error": f"{type(e).__name__}: {e}"}
    stamp = card["scored_at"].replace(":", "").replace("-", "")
    with case_lock(case_id):
        cards = case_file(case_id, "scorecards", tree=case)
        cards.mkdir(parents=True, exist_ok=True)
        dump_json(cards / f"assembly@{be}-{stamp}.json", card)
        dump_json(cards / f"assembly@{be}-latest.json", card)
        dump_json(cards / "assembly-latest.json", card)
    dump_json(out / "scorecard.json", card)
    entry["scorecard"] = {
        "verdict": card["verdict"],
        "checks": {k: v.get("ok") for k, v in (card.get("checks") or {}).items()},
        "error": card.get("error"),
    }
    entry["stage_reached"] = "scored"
    entry["seconds"] = round(time.time() - t0)
    entry["finished"] = utc_now()
    log_attempt(case_id, entry)
    print(
        f"assembly {case_id}: {card['verdict']} mode=modelled "
        + (
            ", ".join(f"{k}={('ok' if v['ok'] else 'FAIL') if 'ok' in v else 'info'}" for k, v in (card.get("checks") or {}).items())
            or card.get("error", "")
        )
    )
    if isinstance(card.get("viz"), dict) and card["viz"].get("html"):
        print(f"  visual check: {card['viz']['html']} (glb alongside)")
    return card

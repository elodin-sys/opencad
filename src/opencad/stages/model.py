"""model: the worker authors parts/<part>/main.kcl following the plan (bounded self-corrections)."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from opencad import codex, worker
from opencad.orchestrator import Ctx

MAX_SELF_CORRECTIONS = 3
INCOMPLETE_MARKERS = ("incomplete", "fails execution", "does not execute", "not produced", "budget is exhausted")
TIMEOUT_EXIT = 124


def brief(ctx: Ctx, plan_md: str, work: Path, *, folded_plan: bool = False) -> str:
    target = ctx.entry
    lang = ctx.backend.language
    critics = lang.critics()
    if folded_plan:
        plan_block = f"""Plan first, inside this turn (no separate planning pass): before any geometry, write `{ctx.results_dir / 'plan.md'}` with at most 15 lines:
the construction sequence (plane/sketch/operation per step and the contract parameters each consumes), the invariants you will `assert`,
the part-specific risks (coplanar booleans, region consumption, face-local frames), and the engine-analyze numbers you expect. Then build it."""
    else:
        plan_block = f"Approved construction plan (follow it; deviate only with a stated reason under Open questions):\n{plan_md}"
    memory = ""
    if lang.suffixes[0] == ".py":
        from opencad import resources
        from opencad.backends.pythonlang import source_limits

        max_lines, max_literals = source_limits()
        memory = (f"- Memory and size: each engine call may hold at most {resources.gb(resources.runner_budget())}; a build past that is killed and fails as "
                  f"`memory`, the model's failure. Keep the part's sources under {max_lines} lines and {max_literals} numeric literals: a fair shell is a few "
                  "spline sections driven by named parameters, never point lists read from the reference mesh (a traced surface builds a model of tens of GB "
                  "and fails the `independence` gate).\n")
    envelope = ""
    if not (ctx.load_stage("blockout") or {}).get("ok"):
        e = ctx.contract.envelope
        envelope = (f"- No blockout checkpoint ran for this part, so the envelope is your first checkpoint: the first executing version is the primary "
                    f"solids that reach the envelope extremes, and the critic must show bbox {list(e.min)}..{list(e.max)} (±{e.tolerance}) before any "
                    "feature is added. The frame and datums do not move after that.\n")
    return f"""Author the {lang.id} model of the part below. Deliverable: `{target}` (create `{target.parent}` if needed). You may add extra `{', '.join(lang.suffixes)}` modules next to it only if the entry imports them. Write scratch snapshots/exports under `{work}`, never under `{target.parent}`.

{critics.get('note') or ''}

{codex.contract_digest(ctx.contract, ctx.design_dir)}

{plan_block}

Working method:
{envelope}{memory}- Build incrementally: datum body first, analyze `{target}` and confirm the envelope, then add features one group at a time and re-measure with the local critic `{critics.get('quick', 'python -m opencad quick {entry} --contract {contract}').format(entry=target, contract=ctx.contract_path, ledger='(work-order ledger)')}`. Do not write your own STEP checker.
- At most {MAX_SELF_CORRECTIONS} self-corrections after the first complete attempt. Before each retry write down the error class (language/API mismatch, solver constraint, kernel failure, misread requirement, tooling) and the intended fix in `{work}/construction-log.md`. Stop and report if the budget is exhausted.
- `{target}` must ALWAYS execute when you finish: keep a copy of the last executing version (`{work}/checkpoint{lang.suffixes[0]}`) before each risky change, and if the budget runs out or an engine error will not clear, restore that checkpoint as the deliverable and list the missing features under Open questions. A non-executing file is worth nothing to the pipeline; an incomplete executing file gets a measured correction turn.
- {ctx.backend.engine.hints()}
- Every contract feature must exist in the geometry. Optional/cosmetic features (fillets marked optional) may be omitted only if the engine refuses them; say so.
- The final `{lang.entry}` must be formatted, lint-clean, and reproduce the acceptance numbers within tolerance. Render front/top/right/iso from the exported STL and look at them: check feature positions and orientation, not just the numbers. When the design has input renders, the critic writes `quick-compare.png` (input render beside your part, same view) next to the ledger: open it and name what differs before the next edit.

{lang.rules()}
Under `## Verification` list every measured value beside its contract expectation (bbox min/max, volume, surface area, centre of mass) and the per-feature evidence you inspected. Under `## Open questions` list anything unverified or any contract conflict.
"""


def _incomplete(r: worker.WorkerResult) -> bool:
    text = (r.sections.get("Result") or "").lower()
    return bool(r.metrics.get("incomplete")) or any(k in text for k in INCOMPLETE_MARKERS)


def timed_out(r: worker.WorkerResult) -> bool:
    return r.exit_code == TIMEOUT_EXIT


def _builds(ctx: Ctx, entry: Path) -> bool:
    from opencad.backends.base import EngineError

    try:
        ctx.backend.engine.analyze(entry)
        return True
    except EngineError:
        return False


def restore_checkpoint(ctx: Ctx, checkpoint: Path, work: Path) -> bool:
    """A turn killed at its budget can leave the sources mid-edit. When the entry no longer builds, keep the killed sources under
    `work/timed-out/` and put back the worker's last executing checkpoint: one entry file, or a directory holding every part source."""
    if not checkpoint.exists() or (ctx.entry.exists() and _builds(ctx, ctx.entry)):
        return False
    files = sorted(checkpoint.glob("*")) if checkpoint.is_dir() else [checkpoint]
    sources = [f for f in files if f.is_file() and f.suffix in ctx.backend.language.suffixes]
    if not sources:
        return False
    killed = work / "timed-out"
    killed.mkdir(parents=True, exist_ok=True)
    for f in ctx.part_dir.iterdir():
        if f.is_file() and f.suffix in ctx.backend.language.suffixes:
            shutil.copy2(f, killed / f.name)
    for f in sources:
        shutil.copy2(f, ctx.entry if not checkpoint.is_dir() else ctx.part_dir / f.name)
    if _builds(ctx, ctx.entry):
        return True
    for f in killed.iterdir():
        shutil.copy2(f, ctx.part_dir / f.name)
    return False


def turn_ok(r: worker.WorkerResult, produced: bool) -> bool:
    """A deliverable left by a turn killed at its budget is still measured: the pipeline's correction turns finish it."""
    return produced and (r.ok or timed_out(r))


def run(ctx: Ctx) -> dict[str, Any]:
    plan = ctx.require_stage("plan")
    folded = bool(plan.get("folded"))
    plan_path = Path(plan.get("plan_md") or (ctx.results_dir / "plan.md"))
    plan_md = plan_path.read_text(encoding="utf-8") if plan_path.exists() and not folded else ""
    work = ctx.results_dir / "model-work"
    if worker.fresh(ctx.results_dir, "model"):  # a continued run keeps the worker's scratch and checkpoints
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
    ctx.part_dir.mkdir(parents=True, exist_ok=True)
    before = {p.name: p.stat().st_mtime for p in ctx.part_dir.iterdir()} if ctx.part_dir.exists() else {}
    from opencad.stages.decompose import acceptance_count

    r = worker.dispatch(brief(ctx, plan_md, work, folded_plan=folded), role="model", key="model", results_dir=ctx.results_dir, part=ctx.name, cd=work,
                        run_dir=work / "codex", add_dirs=[ctx.part_dir, ctx.results_dir] if folded else [ctx.part_dir], timeout=ctx.timeout, deliverables=[ctx.entry],
                        budget=worker.scaled_budget("model", acceptance_count(ctx.contract), ctx.backend.engine))
    restored = timed_out(r) and restore_checkpoint(ctx, work / f"checkpoint{ctx.backend.language.suffixes[0]}", work)
    produced = ctx.entry.exists()
    if produced:
        ctx.backend.language.format_write(ctx.entry)
    if folded:
        ctx.write_stage("plan", {**{k: v for k, v in plan.items() if k not in ("provenance", "stage", "engine_calls")}, "ok": True, "folded": True,
                                 "plan_md": str(plan_path), "written_by_model_turn": plan_path.exists(), "lines": len(plan_path.read_text(encoding="utf-8").splitlines()) if plan_path.exists() else 0})
    files = sorted(p.name for p in ctx.part_dir.iterdir() if p.is_file()) if ctx.part_dir.exists() else []
    reported = [Path(p).name for p in (r.metrics.get("files_changed") or []) if isinstance(p, str)]
    changed = [n for n in files if n in reported or n not in before or (ctx.part_dir / n).stat().st_mtime > before.get(n, 0)]
    incomplete = _incomplete(r)
    summary = r.summary()
    data = {
        "ok": turn_ok(r, produced),
        "timed_out": timed_out(r),
        "restored_checkpoint": restored,
        "self_reported_incomplete": incomplete,
        "worker": summary,
        "codex": summary,
        "thread_id": r.thread_id,
        "codex_report": r.sections,
        "kcl": str(ctx.entry),
        "source": str(ctx.entry),
        "files": files,
        "changed": changed,
        "visual_check": r.metrics.get("visual_check"),
    }
    ctx.write_stage("model", data)
    print(f"model {'ok' if data['ok'] else 'FAILED'}: {ctx.entry if produced else 'no ' + ctx.backend.language.entry}; {r.backend} {r.seconds:.0f}s, {r.commands} commands"
          + ("; the turn hit its budget, the deliverable is measured as left" if timed_out(r) else "")
          + ("; restored the last executing checkpoint" if restored else "")
          + ("; the worker reports the deliverable as INCOMPLETE" if incomplete else ""))
    return data


def retry(ctx: Ctx, thread_id: str, correction: str, *, key: str = "retry", role: str = "retry", budget: float | None = None,
          images: list[Path] | None = None) -> dict[str, Any]:
    """Bounded correction on the model thread; called by the pipeline after failed gates."""
    work = ctx.results_dir / "model-work"
    work.mkdir(parents=True, exist_ok=True)
    r = worker.dispatch(correction, role=role, key=key, results_dir=ctx.results_dir, part=ctx.name, cd=work, run_dir=work / f"codex-{key}",
                        resume=thread_id or None, add_dirs=[ctx.part_dir], timeout=ctx.timeout, deliverables=[ctx.entry], budget=budget,
                        images=[p for p in (images or []) if p.exists()] or None)
    if ctx.entry.exists():
        ctx.backend.language.format_write(ctx.entry)
    prev = ctx.load_stage("model") or {}
    summary = r.summary()
    entry = {"worker": summary, "codex": summary, "codex_report": r.sections, "correction": correction, "key": key, "incomplete": _incomplete(r), "visual_check": r.metrics.get("visual_check")}
    history = list(prev.get("corrections") or [])
    history.append(entry)
    data = {**prev, "ok": turn_ok(r, ctx.entry.exists()), "retry": entry, "corrections": history, "thread_id": r.thread_id or prev.get("thread_id") or thread_id,
            "visual_check": r.metrics.get("visual_check") or prev.get("visual_check")}
    ctx.write_stage("model", data)
    print(f"model {key} {'ok' if data['ok'] else 'FAILED'}; {r.backend} {r.seconds:.0f}s")
    return data

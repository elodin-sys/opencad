"""plan: the worker proposes a construction sequence and invariants before any geometry (read-only)."""

from __future__ import annotations

from typing import Any

from opencad import codex, worker
from opencad.orchestrator import Ctx


def brief(ctx: Ctx) -> str:
    lang = ctx.backend.language
    return f"""Plan the {lang.id} construction of the part below. Do NOT write any files; this is a read-only planning pass.

{lang.critics().get('note') or ''}

{codex.contract_digest(ctx.contract, ctx.design_dir)}

Deliver, in at most 80 lines, under `## Result`:
1. Construction sequence: numbered steps, each naming the plane/face, the sketch content in one line, the operation, and which contract parameters drive it. Build datum geometry first, then features, cosmetic features last.
2. Parameter map: every contract parameter -> the step(s) that consume it (none may be unused).
3. Invariants to assert (walls positive, holes inside the plate, spans positive, etc.).
4. Risks specific to this part and how to avoid them. {ctx.backend.engine.hints()}
5. Verification: the engine-analyze numbers you expect (bbox, volume, centre of mass) and which snapshot angles show the critical features.
6. Dense coordinate profiles: follow the backend skills pack; feeding a full table as sketch points is an allowed deviation only with a stated reason.

{lang.rules()}
"""


def fold(ctx: Ctx) -> dict[str, Any]:
    """No separate planning turn: the model turn writes results/<part>/plan.md itself (default; `--plan-separately` restores the read-only pass)."""
    data = {"ok": True, "folded": True, "plan_md": str(ctx.results_dir / "plan.md"), "note": "plan written by the model turn (folded)"}
    ctx.write_stage("plan", data)
    print("plan folded into the model turn (no separate planning pass)")
    return data


def run(ctx: Ctx) -> dict[str, Any]:
    work = ctx.results_dir / "plan-work"
    work.mkdir(parents=True, exist_ok=True)
    r = worker.dispatch(brief(ctx), role="plan", key="plan", results_dir=ctx.results_dir, part=ctx.name, cd=work, run_dir=work / "codex",
                        read_only=True, timeout=ctx.timeout)
    plan_md = r.sections.get("Result", "") or r.result_md
    (ctx.results_dir / "plan.md").write_text(plan_md + "\n", encoding="utf-8")
    summary = r.summary()
    data = {"ok": r.ok and bool(plan_md.strip()), "worker": summary, "codex": summary, "thread_id": r.thread_id,
            "plan_md": str(ctx.results_dir / "plan.md"), "open_questions": r.sections.get("Open questions", "")}
    ctx.write_stage("plan", data)
    print(f"plan {'ok' if data['ok'] else 'FAILED'}: {len(plan_md.splitlines())} lines, {r.backend} {r.seconds:.0f}s")
    return data

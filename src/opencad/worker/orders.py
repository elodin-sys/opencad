"""Work orders: the handback protocol between the pipeline and the Cursor `cad-worker` sub-agent.

A stage that needs a worker turn issues an order under results/<part>/worker/NNN-<role>/ (order.json,
brief.md) and the pipeline exits 75. The orchestrating Cursor agent runs the cad-worker on brief.md;
the worker writes result.md, metrics.json and an empty `done` file; the pipeline is re-run and
`complete()` turns the order into a WorkerResult. Orders are keyed so a re-run finds its own turn.
"""

from __future__ import annotations

import json
import os
import shutil
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from opencad.io import dump_json, load_json, utc_now
from opencad.paths import ASSEMBLY_PARTS, NESTED, REPO_ROOT, RESULTS, design_dir
from opencad.worker.profiles import lean_turns
from opencad.worker.result import WorkerResult

ORDERS_DIRNAME = "worker"
ORDER_FILE = "order.json"
BRIEF_FILE = "brief.md"
RESULT_FILE = "result.md"
METRICS_FILE = "metrics.json"
DISPATCH_FILE = "dispatch.json"
DONE_FILE = "done"
LEDGER_FILE = "engine-ledger.jsonl"
REPORT_SECTIONS = ("Result", "Files changed", "Verification", "Open questions")
LOCAL_CAD_BACKENDS = ("cadquery", "build123d", "freecad")


def _memory_line() -> str:
    from opencad import resources
    from opencad.backends.pythonlang import source_limits

    lines, literals = source_limits()
    return (f"- Memory: an engine call (analyze, export, `quick`) may hold at most {resources.gb(resources.runner_budget())}; past that it is killed "
            f"and the build fails as `memory`, the model's failure. Keep the part's sources parametric, at most {lines} lines and {literals} numeric "
            "literals: never paste point lists traced from a reference mesh.")


@dataclass
class WorkOrder:
    id: str
    seq: int
    key: str
    role: str
    part: str
    dir: Path
    cwd: Path
    writable_dirs: list[Path]
    images: list[Path]
    read_only: bool
    deliverables: list[Path]
    resume_of: str | None
    model: str
    budget_s: float
    created_at: str
    created_ts: float
    status: str = "pending"  # pending | done | failed | superseded
    context: dict[str, Any] = field(default_factory=dict)
    continue_cmd: str = ""
    finished_at: str | None = None
    backend: str = "zoo"

    @property
    def brief_path(self) -> Path:
        return self.dir / BRIEF_FILE

    @property
    def result_path(self) -> Path:
        return self.dir / RESULT_FILE

    @property
    def metrics_path(self) -> Path:
        return self.dir / METRICS_FILE

    @property
    def dispatch_path(self) -> Path:
        return self.dir / DISPATCH_FILE

    @property
    def done_path(self) -> Path:
        return self.dir / DONE_FILE

    @property
    def ledger_path(self) -> Path:
        return self.dir / LEDGER_FILE

    def to_json(self) -> dict[str, Any]:
        d = asdict(self)
        for k in ("dir", "cwd"):
            d[k] = str(d[k])
        for k in ("writable_dirs", "images", "deliverables"):
            d[k] = [str(p) for p in d[k]]
        d["paths"] = {
            "brief": str(self.brief_path),
            "result": str(self.result_path),
            "metrics": str(self.metrics_path),
            "dispatch": str(self.dispatch_path),
            "done": str(self.done_path),
            "ledger": str(self.ledger_path),
        }
        return d

    @classmethod
    def from_json(cls, d: dict[str, Any]) -> WorkOrder:
        d = {k: v for k, v in d.items() if k != "paths"}
        d["dir"] = Path(d["dir"])
        d["cwd"] = Path(d["cwd"])
        for k in ("writable_dirs", "images", "deliverables"):
            d[k] = [Path(p) for p in d.get(k, [])]
        d.setdefault("backend", "zoo")
        return cls(**d)


def orders_root(results_dir: Path) -> Path:
    return Path(results_dir) / ORDERS_DIRNAME


def save(order: WorkOrder) -> None:
    dump_json(order.dir / ORDER_FILE, order.to_json())


def load(order_dir: Path) -> WorkOrder:
    return WorkOrder.from_json(load_json(Path(order_dir) / ORDER_FILE))


def list_orders(results_dir: Path) -> list[WorkOrder]:
    root = orders_root(results_dir)
    if not root.exists():
        return []
    out = []
    for p in sorted(root.iterdir()):
        if (p / ORDER_FILE).exists():
            try:
                out.append(load(p))
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
    return out


def find(results_dir: Path, key: str) -> WorkOrder | None:
    """The latest live (not superseded) order with this key."""
    live = [o for o in list_orders(results_dir) if o.key == key and o.status != "superseded"]
    return live[-1] if live else None


def is_done(order: WorkOrder) -> bool:
    return order.done_path.exists()


def pending(results_dir: Path) -> list[WorkOrder]:
    return [o for o in list_orders(results_dir) if o.status == "pending" and not is_done(o)]


def all_pending(results_root: Path = RESULTS) -> list[WorkOrder]:
    out: list[WorkOrder] = []
    if not Path(results_root).exists():
        return out
    for d in sorted(Path(results_root).iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            out += pending(d)
            nested = d / ASSEMBLY_PARTS
            out += [o for p in sorted(nested.iterdir()) if p.is_dir() for o in pending(p)] if nested.is_dir() else []
    return out


def supersede(results_dir: Path, key_prefix: str) -> int:
    """Mark every live order whose key starts with `key_prefix` superseded (a stage is restarting fresh)."""
    n = 0
    for o in list_orders(results_dir):
        if o.key.startswith(key_prefix) and o.status != "superseded":
            o.status = "superseded"
            save(o)
            n += 1
    return n


def last_activity(order: WorkOrder) -> float:
    """Newest mtime across the order directory (ledger, result, views), its deliverables and the writable dirs: what a worker touches while it works."""
    latest = order.created_ts
    roots: list[Path] = [order.dir, *order.deliverables, *order.writable_dirs]
    for root in roots:
        if not root.exists():
            continue
        paths = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and not p.name.startswith(".")
                                               and p.relative_to(root).parts[0] not in NESTED]
        for p in paths[:5000]:
            try:
                latest = max(latest, p.stat().st_mtime)
            except OSError:
                continue
    return latest


def idle_seconds(order: WorkOrder, now: float | None = None) -> float:
    return max(0.0, (now if now is not None else time.time()) - last_activity(order))


def record_dispatch(order: WorkOrder, agent_id: str, model: str = "inherit", finished: bool = False) -> Path:
    """The orchestrator's record of which agent ran the turn (resume identity and the model on the telemetry row). Every call
    without `finished` is a dispatch; a second one is a re-dispatch after an interrupted worker."""
    prev = (load_json(order.dispatch_path) if order.dispatch_path.exists() else {}) or {}
    now = utc_now()
    data = {
        **prev,
        "agent_id": agent_id,
        "model": model or prev.get("model") or "inherit",
        "finished": now if finished else prev.get("finished"),
    }
    if not finished:
        data.setdefault("dispatched_at", now)
        data["dispatches"] = [
            *(prev.get("dispatches") or []),
            {"agent_id": agent_id, "at": now, "ts": round(time.time(), 3)},
        ]
    dump_json(order.dispatch_path, data)
    return order.dispatch_path


def lifecycle(order: WorkOrder, dispatch: dict[str, Any], done_ts: float, now: float) -> dict[str, Any]:
    """issued -> dispatched (-> re-dispatched) -> done -> consumed, and the latencies between them, for the turn row."""
    ds = [float(d["ts"]) for d in dispatch.get("dispatches") or [] if isinstance(d, dict) and d.get("ts")]
    first, last = (ds[0], ds[-1]) if ds else (None, None)
    return {
        "issued_at": order.created_at,
        "dispatched_at": _iso(first),
        "redispatched_at": _iso(last) if len(ds) > 1 else None,
        "done_at": _iso(done_ts),
        "consumed_at": _iso(now),
        "dispatches": len(ds),
        "dispatch_latency_s": round(max(0.0, first - order.created_ts), 1) if first else None,
        "worker_s": round(max(0.0, done_ts - (last or order.created_ts)), 1),
        "interruption_s": round(last - first, 1) if len(ds) > 1 else 0.0,
        "pickup_latency_s": round(max(0.0, now - done_ts), 1),
    }


def _iso(ts: float | None) -> str | None:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)) if ts else None


def known_agent(results_dir: Path, agent_id: str | None) -> bool:
    """Was this id recorded by the orchestrator for a cad-worker turn of this part? (A Codex thread id from an older run is not resumable here.)"""
    if not agent_id:
        return False
    for o in list_orders(results_dir):
        if o.dispatch_path.exists():
            try:
                if str((load_json(o.dispatch_path) or {}).get("agent_id") or "") == str(agent_id):
                    return True
            except json.JSONDecodeError:
                continue
    return False


def previous_results(results_dir: Path, before: WorkOrder | None = None, limit: int = 5) -> list[Path]:
    """result.md of earlier finished orders for the same part (context for a fresh worker that cannot resume a thread)."""
    out = []
    for o in list_orders(results_dir):
        if before is not None and o.seq >= before.seq:
            continue
        if (
            o.status != "pending" and o.result_path.exists()
        ):  # superseded turns still tell the next worker what was tried
            out.append(o.result_path)
    return out[-limit:]


def issue(
    results_dir: Path,
    *,
    key: str,
    role: str,
    part: str,
    brief: str,
    cwd: Path,
    writable_dirs: list[Path] | None = None,
    images: list[Path] | None = None,
    read_only: bool = False,
    deliverables: list[Path] | None = None,
    resume_of: str | None = None,
    model: str,
    budget_s: float,
    context: dict[str, Any] | None = None,
    continue_cmd: str = "",
) -> WorkOrder:
    root = orders_root(results_dir)
    root.mkdir(parents=True, exist_ok=True)
    seq = max((o.seq for o in list_orders(results_dir)), default=0) + 1
    oid = f"{seq:03d}-{role}"
    from opencad.backends.registry import current_id

    order = WorkOrder(
        id=oid,
        seq=seq,
        key=key,
        role=role,
        part=part,
        dir=root / oid,
        cwd=Path(cwd),
        writable_dirs=[Path(p) for p in (writable_dirs or [])],
        images=[Path(p) for p in (images or [])],
        read_only=read_only,
        deliverables=[Path(p) for p in (deliverables or [])],
        resume_of=resume_of,
        model=model,
        budget_s=float(budget_s),
        created_at=utc_now(),
        created_ts=time.time(),
        context=dict(context or {}),
        continue_cmd=continue_cmd,
        backend=current_id(),
    )
    order.dir.mkdir(parents=True, exist_ok=True)
    order.brief_path.write_text(
        prompt(order, brief, previous=previous_results(results_dir, before=order)), encoding="utf-8"
    )
    save(order)
    return order


_CRITIC_METHOD = {
    "sections": "a B-rep plane cut; area, loops and holes",
    "faces": "a plane and outward normal within tolerance, then the area band",
    "cylinders": "axis offset and radius against the named axis",
    "planes": "faces whose normal matches, summed area against the band",
    "dimensions": "a bbox extent, or the distance between two named faces",
    "symmetry": "surface samples reflected across the plane and measured against a fine tessellation of the STEP, not the export STL; quick samples 8,000 points, the gate 60,000",
    "thickness": "inward ray casts; the check is the p05",
    "probes": "each point classified solid or void",
    "volume": "solid volume against the band",
    "center_of_mass": "centre of mass per axis",
}


def _skill_inline(paths: list[Path], limit: int = 8192) -> str | None:
    import re

    # front-matter feeds Cursor's skill index, not the worker
    texts = [(p, re.sub(r"\A---\n.*?\n---\n+", "", p.read_text(encoding="utf-8"), count=1, flags=re.DOTALL)) for p in paths if p.is_file()]
    if not texts or sum(len(t) for _, t in texts) > limit:
        return None
    return "\n\n".join(f"### {p.name}\n\n{t.rstrip()}" for p, t in texts)


def _result_sections(path: Path) -> str:
    """`## Result` and `## Open questions` from an earlier turn, so this turn does not re-read the file."""
    import re

    text = path.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"^## ", text, flags=re.MULTILINE)
    keep = []
    for part in parts[1:]:
        heading, _, body = part.partition("\n")
        if heading.strip() in ("Result", "Open questions"):
            keep.append(f"## {heading.strip()}\n{body.strip()}")
    return "\n\n".join(keep)


def _critic_method(contract: str | None) -> str:
    if not contract or not Path(contract).is_file():
        return ""
    from opencad.contract import ContractError, load_contract

    try:
        acceptance = load_contract(Path(contract)).acceptance
    except (OSError, ValueError, ContractError):
        return ""
    present = [name for name in _CRITIC_METHOD if getattr(acceptance, name, None)]
    if not present:
        return ""
    lines = "\n".join(f"- {name}: {_CRITIC_METHOD[name]}" for name in present)
    return (
        "How the critic measures (do not reimplement these, and do not read `src/opencad` to find out):\n"
        + lines
        + "\n`python -m opencad quick <entry> --contract <contract> --stl --all` prints every check, passing and failing. "
        "It is the only measurement. Do not write your own probe script.\n"
    )


def prompt(order: WorkOrder, brief: str, previous: list[Path] | None = None) -> str:
    """The self-contained prompt for the cad-worker sub-agent: contract, protocol, then the stage brief."""
    writable = ", ".join(f"`{p}`" + (f" (not its `{ASSEMBLY_PARTS}/`: the part sources)" if (Path(p) / ASSEMBLY_PARTS).is_dir() else "")
                         for p in [order.cwd, *order.writable_dirs]) or f"`{order.cwd}`"
    deliverables = (
        ", ".join(f"`{p}`" for p in order.deliverables)
        or "(none: this is a read-only reasoning turn; the report is the deliverable)"
    )
    images = "\n".join(f"- `{p}`" for p in order.images)
    resume_note = (
        "You are continuing a thread you already worked in: the skills and files you read earlier are still valid, "
        "do not re-read them or restate what you did before.\n"
        if order.resume_of
        else ""
    )
    prior = ""
    if previous and not order.resume_of:
        if lean_turns():
            blocks = [
                f"### {p.parent.name}\n\n{_result_sections(p)}" for p in previous if p.is_file() and _result_sections(p)
            ]
            prior = "Earlier turns on this part:\n\n" + "\n\n".join(blocks) + "\n" if blocks else ""
        else:
            prior = (
                "Earlier turns on this part (read their `## Result` / `## Open questions` before starting):\n"
                + "\n".join(f"- `{p}`" for p in previous)
                + "\n"
            )
    from opencad.backends.registry import get

    be = get(order.backend)
    lang = be.language
    critics = lang.critics()
    skill_paths = " and ".join(f"`{p}`" for p in lang.skills())
    skill_body = _skill_inline(list(lang.skills())) if lean_turns() else None
    contract = order.context.get("contract")
    if not contract and order.role not in ("draft", "assemble", "plan"):
        default = design_dir(order.part) / "contract.yaml"
        contract = str(default) if default.exists() else None
    partial = ""
    if order.context.get("codex_partial"):
        partial = (
            f"A Codex worker started this turn and ran out of budget; its run dir is `{order.context['codex_partial']}` "
            f"(read result.md/events there if present, then finish the task).\n"
        )
    quick = critics.get("quick", "python -m opencad quick {entry} --contract {contract} --ledger {ledger}")
    assembly = order.context.get("assembly")
    assemble_like = order.role == "assemble" or (order.role == "correction" and bool(order.context.get("work") or assembly))
    views = "assembly-views.png" if assemble_like else "quick-views.png"
    if assemble_like:
        work = order.context.get("work") or str(order.cwd)
        entry = order.context.get("entry")
        if assembly:
            critic_line = (
                f"- Local critic: `cd {REPO_ROOT} && .venv/bin/python -m opencad assembly check-source {assembly} --backend {order.backend} "
                f"--ledger {order.ledger_path}` builds the assembly source through the engine and prints every check the assembly gates apply "
                "(solid count, per-body agreement, joint fidelity, clearances, envelope) and writes `assembly-views.png` next to the ledger. "
                "You MAY run this command (it is the critic, not a pipeline drive)."
            )
        elif entry:
            critic_line = (
                f"- Local critic: `cd {REPO_ROOT} && .venv/bin/python -m opencad.truth assembly-check {work} "
                f"--entry {entry} --backend {order.backend} --ledger {order.ledger_path}` exports through the engine, "
                "derives assembly.yaml from placements, and prints the joint numbers plus agreement lines. "
                "You MAY run this `assembly-check` command (it is the critic, not a pipeline drive)."
            )
        else:
            critic_line = (
                f"- Local critic: `cd {REPO_ROOT} && .venv/bin/python -m opencad.truth assembly-check {work}` "
                "prints the evaluator's joint numbers from assembly.yaml. You MAY run this `assembly-check` command."
            )
        never_truth = (
            "Never run the pipeline yourself (`python -m opencad drive|run|<stage>`, `python -m opencad.truth run|ecr|assemble`): "
            "the orchestrator continues it when your `done` file exists."
        )
        visual = (
            f"- Before creating `done`, open `{views}` (written next to the ledger by assembly-check) and write one "
            "`Visual: ...` line under `## Verification` naming contact, gap, axis alignment and any interpenetration."
            if entry
            else "- Before creating `done`, write one `Visual: ...` line under `## Verification` naming contact, gap, axis alignment and any interpenetration from the body renders and the critic numbers."
        )
    else:
        critic_line = (
            f"- Local critic (use it after every feature group instead of writing your own checker): `cd {REPO_ROOT} && {quick.format(entry='<entry>', contract=contract, ledger=order.ledger_path)}` "
            "exports once (cached by source hash), measures the STEP with OpenCascade against the contract and prints exactly the checks the gates would fail; add `--stl` before you finish."
            if contract
            else ""
        )
        never_truth = "Never run the pipeline yourself (`python -m opencad drive|run|<stage>`, `python -m opencad.truth ...`): the orchestrator continues it when your `done` file exists."
        visual = (
            "- Before creating `done`, open `quick-views.png` (written next to the ledger by `quick --stl`) and, when the design has input renders, "
            "`quick-compare.png` (input render beside your part, same view). Write one `Visual: ...` line under `## Verification` naming any step, fold, "
            "gap or asymmetry per quarter and the underside, and what still differs from the input renders."
        )
    lines = [
        f"You are a opencad CAD worker (work order `{order.id}`, role `{order.role}`, part `{order.part}`, backend `{order.backend}`). Finish the task below on your own; nobody will answer questions mid-turn.",
        "",
        "## Worker protocol",
        f"- Working directory (scratch): `{order.cwd}`. Writable locations: {writable}. Deliverables: {deliverables}. Write nowhere else."
        + (
            " This is a READ-ONLY reasoning turn: change no file anywhere; the only files you create are the three protocol files listed below."
            if order.read_only
            else ""
        ),
        *(
            [
                f"- Read only this brief, the attached images, this order's directory, `parts/{order.backend}/{order.part}`, `designs/{order.part}`"
                + "".join(f", `{p}`" for p in order.context.get("readable") or [])
                + " and the inlined skill. "
                "Do not open `src/opencad`, `tests/`, `truth/`, other orders under `results/`, or any other part under `parts/` or `designs/`."
                + (
                    " Do not read the library source or call `inspect.signature`; the signatures are in the skill."
                    if order.role == "model"
                    else ""
                )
            ]
            if lean_turns()
            else []
        ),
        (
            f"- Skills are inlined at the end of this brief; do not re-read them. {resume_note.strip()}"
            if skill_body
            else f"- Skills: read {skill_paths} before any CAD work. {resume_note.strip()}"
        ),
        f"- Every engine call (analyze, export) MUST run through the ledger wrapper so it is recorded: "
        f"`cd {REPO_ROOT} && .venv/bin/python -m opencad engine --backend {order.backend} --ledger {order.ledger_path} -- ...`. Format and lint may run without the ledger.",
        *([critic_line] if critic_line else []),
        visual,
        f"- Budget: {order.budget_s:.0f} s of wall time for this turn. When you are close to it, stop at an executing checkpoint and report; an on-time executing file beats a late perfect one.",
        *([_memory_line()] if order.backend in LOCAL_CAD_BACKENDS and order.role not in ("draft", "asm-draft") else []),
        "- Never run `codex`, never commit or push, never launch sub-agents or nested workers, never edit `contract.yaml`, `brief.md`, or anything under `truth/`. "
        + never_truth,
        "- Finish by writing, in this order:",
        f"  1. `{order.result_path}` with exactly these sections: `## Result`, `## Files changed`, `## Verification` (commands run, measured vs expected values, one `Visual:` line), `## Open questions` (anything unverified).",
        f'  2. `{order.metrics_path}`: JSON `{{"commands": <shell commands you ran>, "self_corrections": <n>, "engine_calls": <hosted engine calls>, "files_changed": [paths], "incomplete": true|false, "notes": ""}}`.',
        f"  3. an empty file `{order.done_path}` (create it LAST; the pipeline resumes when it exists).",
    ]
    if images:
        lines += [
            "",
            "Images to inspect (open each one; read dimension lines, count features, note pixel evidence):",
            images,
        ]
    if prior or partial:
        lines += ["", (prior + partial).rstrip()]
    lines += ["", "# Task", "", brief.strip(), ""]
    if lean_turns() and contract:
        method = _critic_method(str(contract))
        if method:
            lines += ["", method.rstrip(), ""]
    if skill_body:
        lines += ["", "# Skills", "", skill_body, ""]
    return "\n".join(lines)


def _ledger_rows(order: WorkOrder) -> list[dict[str, Any]]:
    if not order.ledger_path.exists():
        return []
    rows = []
    for line in order.ledger_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def complete(order: WorkOrder) -> WorkerResult:
    """Turn a finished order (done marker present) into a WorkerResult and record its status."""
    from opencad.codex import parse_sections

    result_md = order.result_path.read_text(encoding="utf-8") if order.result_path.exists() else ""
    sections = parse_sections(result_md)
    metrics: dict[str, Any] = {}
    if order.metrics_path.exists():
        try:
            metrics = load_json(order.metrics_path) or {}
        except json.JSONDecodeError:
            metrics = {"error": "metrics.json is not valid JSON"}
    dispatch: dict[str, Any] = {}
    if order.dispatch_path.exists():
        try:
            dispatch = load_json(order.dispatch_path) or {}
        except json.JSONDecodeError:
            dispatch = {}
    done_ts = order.done_path.stat().st_mtime if order.done_path.exists() else time.time()
    seconds = max(0.0, done_ts - order.created_ts)
    ledger = _ledger_rows(order)
    missing = [str(p) for p in order.deliverables if not p.exists()]
    failure = ""
    if not result_md.strip():
        failure = "worker finished without a result.md"
    elif missing:
        failure = f"deliverables missing after the turn: {missing}"
    # workers sometimes report lists where the protocol asks for counts; keep the list and count it
    for k in ("commands", "engine_calls", "self_corrections"):
        v = metrics.get(k)
        if isinstance(v, list):
            metrics[f"{k}_list"] = v
            metrics[k] = len(v)
        elif v is not None and not isinstance(v, (int, float)):
            try:
                metrics[k] = int(str(v).strip())
            except ValueError:
                metrics[k] = 0
    metrics = {
        **metrics,
        "engine_ledger_calls": len(ledger),
        "engine_ledger_seconds": round(sum(float(r.get("seconds", 0) or 0) for r in ledger), 2),
    }
    metrics["visual_check"] = _visual_line(sections.get("Verification") or "") or _visual_line(result_md)
    thread_id = str(dispatch.get("agent_id") or metrics.get("agent_id") or "")
    r = WorkerResult(
        thread_id=thread_id,
        exit_code=0 if not failure else 1,
        seconds=seconds,
        commands=int(metrics.get("commands") or 0),
        usage={},
        run_dir=order.dir,
        result_md=result_md,
        failure=failure,
        sections=sections,
        backend="cursor",
        role=order.role,
        model=str(dispatch.get("model") or order.model),
        order_id=order.id,
        metrics=metrics,
        fallback_from=order.context.get("fallback_from"),
    )
    order.status = "done" if not failure else "failed"
    order.finished_at = utc_now()
    if not order.context.get(
        "telemetry_recorded"
    ):  # exactly one turn row per order, however many times a continued run passes here
        from opencad import telemetry

        life = lifecycle(order, dispatch, done_ts, time.time())
        first = next(
            (float(d["ts"]) for d in dispatch.get("dispatches") or [] if isinstance(d, dict) and d.get("ts")), None
        )
        row = {
            **telemetry.turn_data(r, budget_s=order.budget_s),
            "key": order.key,
            **life,
            "expired": order.context.get("expired"),
            **telemetry.ledger_stats(ledger, start_ts=first or order.created_ts, worker_s=life["worker_s"]),
        }
        telemetry.record("turn", order.part, row, results_dir=order.dir.parent.parent)
        order.context["telemetry_recorded"] = True
        print(
            f"[worker] {order.id} ({order.role}, {r.model}) finished in {r.seconds:.0f} s, {r.commands} commands, {metrics.get('engine_ledger_calls', 0)} engine calls"
            f"{'; visual ' + ('ok' if metrics.get('visual_check') else 'missing')}"
            f"{'; INCOMPLETE' if metrics.get('incomplete') else ''}{'; FAILED: ' + failure if failure else ''}",
            flush=True,
        )
    save(order)
    return r


def _visual_line(text: str) -> str | None:
    for line in text.splitlines():
        s = line.strip()
        if s[:2] in ("- ", "* "):
            s = s[2:].strip()
        if s.lower().startswith("visual:"):
            return s
    return None


STALE_FACTOR = 1.25
EXPIRE_FACTOR = 1.5
EXPIRE_RETRY_S = 120.0


def wait(
    results_dir: Path,
    *,
    poll_s: float = 5.0,
    stale_factor: float = STALE_FACTOR,
    enforce: Callable[[Path], bool] | None = None,
) -> None:
    """Block until every pending order of this part has its `done` file (the caller then continues the run itself). A dispatched order
    idle for more than `stale_factor` x its budget prints one `STALE {...}` line naming the agent to resume or replace. With `enforce`
    (an "does this source execute" probe), a turn past EXPIRE_FACTOR x its budget is taken at its executing state (`expire`)."""
    warned: set[str] = set()
    tried: dict[str, float] = {}
    while True:
        pend = pending(results_dir)
        if not pend:
            return
        now = time.time()
        for o in pend:
            if o.id not in warned and o.dispatch_path.exists() and idle_seconds(o) > stale_factor * o.budget_s:
                warned.add(o.id)
                print(stale_line(o), flush=True)
            if (
                enforce is not None
                and elapsed_seconds(o, now) > EXPIRE_FACTOR * o.budget_s
                and now - tried.get(o.id, 0.0) > EXPIRE_RETRY_S
            ):
                tried[o.id] = now
                expire(o, enforce)
        time.sleep(poll_s)


def executes(source: Path) -> bool:
    """The current engine analyzes this source without an error (the `enforce` probe of `wait`)."""
    from opencad.backends.base import EngineError
    from opencad.backends.registry import get

    try:
        get().engine.analyze(source)
        return True
    except EngineError:
        return False


def elapsed_seconds(order: WorkOrder, now: float | None = None) -> float:
    """Since the first dispatch (or the issue, before one)."""
    dispatch = (load_json(order.dispatch_path) if order.dispatch_path.exists() else {}) or {}
    first = next(
        (float(d["ts"]) for d in dispatch.get("dispatches") or [] if isinstance(d, dict) and d.get("ts")),
        order.created_ts,
    )
    return (now if now is not None else time.time()) - first


def expire(order: WorkOrder, executes: Callable[[Path], bool]) -> bool:
    """Take an over-budget turn at its executing state: the source deliverable if it executes, else the worker's checkpoint (copied over
    it). Writes the protocol files and `done` and prints `EXPIRED {...}` (the orchestrator stops that worker); False when nothing executes."""
    code = [p for p in order.deliverables if p.suffix in (".py", ".kcl")]
    if not code:
        return False
    target = code[0]
    took = "the deliverable as it stood" if target.exists() and executes(target) else None
    if took is None:
        for cp in (order.cwd / f"checkpoint{target.suffix}", target.parent / f"checkpoint{target.suffix}"):
            if cp.exists() and executes(cp):
                shutil.copy2(cp, target)
                took = f"the worker's checkpoint {cp}"
                break
    if took is None:
        return False
    note = f"Expired at {EXPIRE_FACTOR} x the {order.budget_s:.0f} s budget; the pipeline took {took}."
    if not order.result_path.exists():
        order.result_path.write_text(
            f"## Result\n{note}\n## Files changed\n- {target}\n## Verification\n-\n## Open questions\n- the turn did not finish\n",
            encoding="utf-8",
        )
    prev = (load_json(order.metrics_path) if order.metrics_path.exists() else {}) or {}
    dump_json(order.metrics_path, {**prev, "incomplete": True, "expired": True, "notes": note})
    order.context["expired"] = took
    save(order)
    order.done_path.touch()
    dispatch = (load_json(order.dispatch_path) if order.dispatch_path.exists() else {}) or {}
    print(
        "EXPIRED "
        + json.dumps(
            {
                "part": order.part,
                "order": str(order.dir),
                "id": order.id,
                "role": order.role,
                "took": took,
                "resume": dispatch.get("agent_id"),
            }
        ),
        flush=True,
    )
    return True


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def watch(pending_fn: Callable[[], list[WorkOrder]], *, stale_s: float | None = None, pid: int | None = None, timeout: float = 3600.0,
          poll_s: float = 5.0) -> int:
    """Block until the orchestrator has something to do, reading the order files rather than a pipeline's output: an order nobody
    dispatched (its NEXT line), a dispatched one idle past `stale_s` (default STALE_FACTOR x its budget; its STALE line), or the
    pipeline process `pid` gone (EXITED). 0 when lines were printed, 3 when the pipeline exited, 4 on `timeout`."""
    t0 = time.time()
    while True:
        lines = []
        for o in pending_fn():
            if not o.dispatch_path.exists():
                lines.append(next_line(o, idle=True))
            elif idle_seconds(o) > (stale_s if stale_s is not None else STALE_FACTOR * o.budget_s):
                lines.append(stale_line(o))
        if lines:
            print("\n".join(lines), flush=True)
            return 0
        if pid is not None and not _alive(pid):
            print("EXITED " + json.dumps({"pid": pid}), flush=True)
            return 3
        if time.time() - t0 > timeout:
            print("TIMEOUT " + json.dumps({"waited_s": round(time.time() - t0)}), flush=True)
            return 4
        time.sleep(poll_s)


def stale_line(order: WorkOrder) -> str:
    dispatch = (load_json(order.dispatch_path) if order.dispatch_path.exists() else {}) or {}
    return "STALE " + json.dumps(
        {
            "part": order.part,
            "backend": order.backend,
            "order": str(order.dir),
            "id": order.id,
            "role": order.role,
            "idle_s": round(idle_seconds(order)),
            "budget_s": order.budget_s,
            "resume": dispatch.get("agent_id"),
            "done": str(order.done_path),
        }
    )


def next_line(order: WorkOrder, *, idle: bool = False) -> str:
    """One machine-readable line the drive loop prints when a turn is pending."""
    d = {
        "action": "worker",
        "part": order.part,
        "backend": order.backend,
        "order": str(order.dir),
        "id": order.id,
        "role": order.role,
        "model": order.model,
        "budget_s": order.budget_s,
        "prompt": str(order.brief_path),
        "images": [str(p) for p in order.images],
        "resume": order.resume_of,
        "dispatch_record": str(order.dispatch_path),
        "done": str(order.done_path),
        "continue": order.continue_cmd,
    }
    if idle:
        dispatched = order.dispatch_path.exists()
        d["idle_s"] = round(idle_seconds(order))
        d["dispatched"] = dispatched
        d["dispatch"] = f"python -m opencad dispatch {order.dir} --agent-id <id>"
    return "NEXT " + json.dumps(d)

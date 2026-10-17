"""Telemetry: one JSONL row per worker turn, evaluator stage, gate evaluation and case attempt.

Rows go to results/<part>/telemetry.jsonl and results/_campaign/telemetry.jsonl. They are what
`python -m opencad telemetry summary|compare|bench|promote` and the truth report read, and the only
numbers the speed work is judged by: wall time per role and stage, engine calls, budgets, pass rates.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import shutil
import statistics
import time
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

from opencad.io import load_json, utc_now
from opencad.paths import REGRESS, RESULTS_BASE, results_root
from opencad.paths import results_dir as results_of

PART_FILE = "telemetry.jsonl"


def campaign_file() -> Path:
    if CAMPAIGN_FILE is not None:
        return Path(CAMPAIGN_FILE)
    return results_root() / "_campaign" / "telemetry.jsonl"


def baseline_pointer(suite: str = "parts") -> Path:
    """results/_regress/baseline.json for the part suite; baseline-<suite>.json for another regression suite (assembly)."""
    if BASELINE_POINTER is not None:
        p = Path(BASELINE_POINTER)
        return p if suite == "parts" else p.with_name(f"{p.stem}-{suite}{p.suffix}")
    return REGRESS / ("baseline.json" if suite == "parts" else f"baseline-{suite}.json")


def baseline_tag(suite: str = "parts") -> str | None:
    """The promoted bench tag named by the suite's baseline pointer."""
    p = baseline_pointer(suite)
    if not p.exists():
        return None
    tag = load_json(p).get("tag")
    return str(tag) if tag else None


CAMPAIGN_FILE = None  # resolved at record time via campaign_file()
BASELINE_POINTER = None  # results/_regress/baseline.json; tests point this at a temp file
KINDS = ("turn", "stage", "gates", "attempt")
_ORDER_RE = re.compile(r"/worker/([^/\s\"'`]+)/brief\.md")
_BRIEF_LOC_RE = re.compile(r"results/([^/\s\"'`]+)/([^/\s\"'`]+)/worker/([^/\s\"'`]+)/brief\.md")

# alert thresholds (printed, never fatal)
STAGE_SLOW_S = 600.0
ENGINE_CALL_SLOW_S = 60.0
MEMORY_ALERT_SHARE = 0.75  # of the engine memory budget
CODEX_STEP_SLOW_S = 15.0
CODEX_CONTEXT_LARGE = 200_000
ATTEMPT_BUDGET_S = 3600.0
PICKUP_SLOW_S = 120.0


def _append(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        # rows longer than PIPE_BUF interleave between concurrent writers without the lock
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.write(json.dumps(row, default=str) + "\n")


def record(
    kind: str, part: str, data: dict[str, Any], *, results_dir: Path | None = None, campaign: Path | None = None
) -> dict[str, Any]:
    if kind not in KINDS:
        raise ValueError(f"telemetry kind {kind!r}")
    row = {"kind": kind, "part": part, "ts": utc_now(), **data}
    if "cad_backend" not in row:
        try:
            from opencad.backends.registry import current_id

            row["cad_backend"] = current_id()
        except Exception:
            pass
    if os.environ.get("OPENCAD_TAG"):
        row["tag"] = os.environ["OPENCAD_TAG"]  # A/B label: `telemetry summary --tag`, `telemetry compare tag:A tag:B`
    _append(Path(results_dir or results_of(part)) / PART_FILE, row)
    _append(campaign or campaign_file(), row)
    for a in alerts(row):
        print(f"[telemetry] ALERT {a}", flush=True)
    return row


def turn_data(result: Any, *, budget_s: float | None) -> dict[str, Any]:
    """Flatten a WorkerResult into a turn row (backend-independent fields first, Codex extras when present)."""
    s = result.summary()
    m = s.get("metrics") or {}
    tl = s.get("timeline") or {}
    usage = s.get("usage") or {}
    out_tok = usage.get("output") or 0
    reasoning = usage.get("reasoning") or 0
    d: dict[str, Any] = {
        "backend": s.get("backend"),
        "role": s.get("role"),
        "model": s.get("model"),
        "order_id": s.get("order_id"),
        "thread_id": s.get("thread_id"),
        "seconds": s.get("seconds"),
        "budget_s": budget_s,
        "over_budget": bool(budget_s and s.get("seconds", 0) > budget_s),
        "commands": s.get("commands"),
        "engine_calls": m.get("engine_ledger_calls", m.get("engine_calls")),
        "engine_seconds": m.get("engine_ledger_seconds"),
        "self_corrections": m.get("self_corrections"),
        "files_changed": len(m.get("files_changed") or []) if isinstance(m.get("files_changed"), list) else None,
        "incomplete": m.get("incomplete"),
        "ok": bool(result.ok),
        "failure": (s.get("failure") or "")[:200] or None,
        "fallback_from": s.get("fallback_from"),
        "network_stalls": s.get("network_stalls"),
        "network_wait_seconds": s.get("network_wait_seconds"),
    }
    if s.get("usage_mode"):
        d["usage_mode"] = s.get("usage_mode")
    if s.get("backend") == "codex":
        from opencad.worker.pricing import cost_usd

        priced = cost_usd(usage, model=s.get("model") or "gpt-6-astra")
        d.update(
            {
                "tokens_input": usage.get("input"),
                "tokens_cached": usage.get("cached"),
                "tokens_output": out_tok,
                "tokens_reasoning": reasoning,
                "usd": priced["usd"],
                "price_card": priced["card"],
                "price_reason": priced["reason"],
                "reasoning_share": round(reasoning / out_tok, 3) if out_tok else None,
                "tool_seconds": tl.get("tool_seconds"),
                "model_seconds": tl.get("model_seconds"),
                "step_latency_s": tl.get("step_latency_s"),
            }
        )
    if s.get("thread_id"):
        est = transcript_usage(s.get("thread_id"), s.get("order_id"))
        if est is not None:
            d["off_brief_reads"] = est.get("off_brief_reads", 0)
    return d


def alerts(row: dict[str, Any]) -> list[str]:
    out: list[str] = []
    k = row.get("kind")
    if k == "turn":
        if row.get("over_budget"):
            out.append(
                f"{row.get('role')} turn {row.get('order_id') or row.get('thread_id')} took {row.get('seconds')} s, budget {row.get('budget_s')} s"
            )
        if (row.get("interruption_s") or 0) > 0:
            out.append(
                f"{row.get('role')} turn {row.get('order_id')} was re-dispatched: {row['interruption_s']} s lost to an interrupted worker"
            )
        for f in ("dispatch_latency_s", "pickup_latency_s"):
            if (row.get(f) or 0) > PICKUP_SLOW_S:
                out.append(
                    f"{row.get('role')} turn {row.get('order_id')}: {f.replace('_s', '').replace('_', ' ')} {row[f]} s (> {PICKUP_SLOW_S:.0f} s)"
                )
        sl = row.get("step_latency_s") or {}
        if sl.get("median") and sl["median"] > CODEX_STEP_SLOW_S:
            out.append(
                f"codex median step latency {sl['median']} s (> {CODEX_STEP_SLOW_S:.0f} s): lower the effort or the context"
            )
        if (
            (row.get("tokens_input") or 0)
            and (row.get("commands") or 0)
            and row["tokens_input"] / max(1, row["commands"]) > CODEX_CONTEXT_LARGE
        ):
            out.append(
                f"codex context ≈ {row['tokens_input'] // max(1, row['commands']):,} tokens per step (> {CODEX_CONTEXT_LARGE:,})"
            )
    elif k == "stage":
        if (row.get("seconds") or 0) > STAGE_SLOW_S:
            out.append(f"stage {row.get('stage')} took {row.get('seconds')} s (> {STAGE_SLOW_S:.0f} s)")
        if (row.get("engine_call_max_s") or 0) > ENGINE_CALL_SLOW_S:
            out.append(
                f"stage {row.get('stage')}: an engine call took {row.get('engine_call_max_s')} s (> {ENGINE_CALL_SLOW_S:.0f} s)"
            )
    elif k == "attempt":
        if row.get("over_budget_reason"):
            out.append(f"attempt {row.get('case')}/{row.get('arm')} over budget: {row.get('over_budget_reason')}")
    if k in ("turn", "stage"):
        out += memory_alerts(row)
    return out


def memory_alerts(row: dict[str, Any]) -> list[str]:
    """An engine call near the memory budget, or killed past it."""
    from opencad import resources

    what = f"{row.get('role')} turn {row.get('order_id')}" if row.get("kind") == "turn" else f"stage {row.get('stage')}"
    budget_gb = resources.runner_budget() / resources.GB
    out = []
    if row.get("oom_killed"):
        out.append(f"{what}: {row['oom_killed']} engine call(s) killed past the {budget_gb:.1f} GB engine memory budget")
    elif (row.get("peak_rss_gb") or 0) > MEMORY_ALERT_SHARE * budget_gb:
        out.append(f"{what}: an engine call peaked at {row['peak_rss_gb']} GB (> {MEMORY_ALERT_SHARE:.0%} of the {budget_gb:.1f} GB budget)")
    return out


def _memory_stats(calls: list[dict[str, Any]]) -> dict[str, Any]:
    peak = max((int(e.get("peak_rss") or 0) for e in calls), default=0)
    return {"peak_rss_gb": round(peak / 1024**3, 2) if peak else None, "oom_killed": sum(1 for e in calls if e.get("oom_killed"))}


def stage_data(
    stage: str, seconds: float, ok: bool | None, engine_calls: list[dict[str, Any]] | None, *, cached: bool = False
) -> dict[str, Any]:
    calls = [e for e in engine_calls or [] if isinstance(e, dict)]
    secs = [float(e.get("seconds", 0) or 0) for e in calls]
    return {
        "stage": stage,
        "seconds": round(seconds, 2),
        "ok": ok,
        "engine_calls": len(calls),
        "engine_seconds": round(sum(secs), 2),
        "engine_call_max_s": round(max(secs), 2) if secs else 0.0,
        "cached": cached,
        "engine_startup_s": round(sum(float(e.get("startup_s") or 0) for e in calls), 2),
        "engine_failures": sum(1 for e in calls if e.get("class") in ("transient", "timeout")),
        **_memory_stats(calls),
    }


@contextmanager
def timed(stage: str, part: str, results_dir: Path, **fields: Any) -> Iterator[dict[str, Any]]:
    """Stage row for an evaluator step without a stage JSON of its own. Recorded in `finally`, so a block that ends by issuing a
    worker order (WorkerPending) is still timed. The block may set `ok`, `engine_calls` (ledger rows) or extra fields."""
    info: dict[str, Any] = dict(fields)
    t0 = time.time()
    try:
        yield info
    finally:
        calls, ok = info.pop("engine_calls", None), info.pop("ok", None)
        record("stage", part, {**stage_data(stage, time.time() - t0, ok, calls), **info}, results_dir=results_dir)


def ledger_stats(ledger: list[dict[str, Any]], *, start_ts: float | None, worker_s: float | None) -> dict[str, Any]:
    """Per-call engine numbers of one worker turn from its engine-ledger.jsonl."""
    secs = sorted(float(r.get("seconds") or 0) for r in ledger)
    starts = [float(r["started"]) for r in ledger if isinstance(r.get("started"), (int, float))]
    return {
        "engine_call_p50_s": round(statistics.median(secs), 2) if secs else None,
        "engine_call_max_s": round(secs[-1], 2) if secs else None,
        "first_engine_call_s": round(min(starts) - start_ts, 1) if starts and start_ts else None,
        "engine_share": round(sum(secs) / worker_s, 3) if worker_s else None,
        "engine_startup_s": round(sum(float(r.get("startup_s") or 0) for r in ledger), 2),
        **_memory_stats(ledger),
    }


def gates_data(fb: dict[str, Any], *, retry: bool = False) -> dict[str, Any]:
    return {
        "ok": fb.get("ok"),
        "summary": fb.get("summary"),
        "failed": fb.get("failed"),
        "retryable": fb.get("retryable_failed"),
        "after_retry": retry,
    }


# --- reading ---------------------------------------------------------------------------


def read(path: Path) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def rows_for(part: str | None = None, *, path: Path | None = None, tag: str | None = None) -> list[dict[str, Any]]:
    if path is not None:
        rows = read(path)
    elif part:
        rows = read(results_of(part) / PART_FILE)
    else:
        rows = read(campaign_file())
    return [r for r in rows if r.get("tag") == tag] if tag else rows


def _mean(xs: Iterable[float], ndigits: int = 1) -> float | None:
    xs = [float(x) for x in xs if x is not None]
    return round(statistics.fmean(xs), ndigits) if xs else None


def _pct(xs: Iterable[float], q: float) -> float | None:
    """Nearest-rank percentile (q in 0..100) of the given values."""
    xs = sorted(float(x) for x in xs if x is not None)
    if not xs:
        return None
    k = max(0, min(len(xs) - 1, round(q / 100.0 * (len(xs) - 1))))
    return round(xs[k])


def _sum_usd(rows: list[dict[str, Any]]) -> float | None:
    vals = [float(r["usd"]) for r in rows if r.get("usd") is not None]
    return round(sum(vals), 4) if vals else None


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregates the speed work is judged by: per role and per stage wall time, engine calls, budgets, pass rates."""
    turns = [r for r in rows if r.get("kind") == "turn"]
    stages = [r for r in rows if r.get("kind") == "stage"]
    gates = [r for r in rows if r.get("kind") == "gates"]
    attempts = [r for r in rows if r.get("kind") == "attempt"]
    by_role: dict[str, dict[str, Any]] = {}
    for role, grp in _group(turns, "role").items():
        secs = [r.get("seconds") or 0 for r in grp]
        by_role[role] = {
            "turns": len(grp),
            "total_s": round(sum(secs)),
            "mean_s": _mean(secs),
            "p50_s": _pct(secs, 50),
            "p95_s": _pct(secs, 95),
            "max_s": round(max(secs)) if secs else None,
            "budget_s": _pct([r.get("budget_s") for r in grp if r.get("budget_s") is not None], 50),
            "over_budget": sum(1 for r in grp if r.get("over_budget")),
            "ok": sum(1 for r in grp if r.get("ok")),
            "engine_calls": sum(int(r.get("engine_calls") or 0) for r in grp),
            "backends": sorted({str(r.get("backend")) for r in grp}),
            "models": sorted({str(r.get("model")) for r in grp if r.get("model")}),
            "fallbacks": sum(1 for r in grp if r.get("fallback_from")),
            "tokens_input": sum(int(r.get("tokens_input") or 0) for r in grp),
            "tokens_cached": sum(int(r.get("tokens_cached") or 0) for r in grp),
            "tokens_output": sum(int(r.get("tokens_output") or 0) for r in grp),
            "tokens_reasoning": sum(int(r.get("tokens_reasoning") or 0) for r in grp),
            "usd": _sum_usd(grp),
            "reasoning_share": _mean(
                [r.get("reasoning_share") for r in grp if r.get("reasoning_share") is not None], 3
            ),
            "median_step_s": _mean(
                [
                    (r.get("step_latency_s") or {}).get("median")
                    for r in grp
                    if (r.get("step_latency_s") or {}).get("median") is not None
                ]
            ),
        }
    by_stage: dict[str, dict[str, Any]] = {}
    for st, grp in _group(stages, "stage").items():
        secs = [r.get("seconds") or 0 for r in grp]
        by_stage[st] = {
            "runs": len(grp),
            "total_s": round(sum(secs)),
            "mean_s": _mean(secs),
            "max_s": round(max(secs)) if secs else None,
            "engine_calls": sum(int(r.get("engine_calls") or 0) for r in grp),
            "engine_s": round(sum(float(r.get("engine_seconds") or 0) for r in grp)),
            "cached": sum(1 for r in grp if r.get("cached")),
            "ok": sum(1 for r in grp if r.get("ok")),
        }
    att = {
        "attempts": len(attempts),
        "mean_s": _mean([a.get("seconds") for a in attempts]),
        "pass": sum(1 for a in attempts if a.get("verdict") == "PASS"),
        "over_budget": sum(1 for a in attempts if a.get("over_budget_reason")),
    }
    g = {
        "evaluations": len(gates),
        "pass": sum(1 for r in gates if r.get("ok")),
        "retries": sum(1 for r in gates if r.get("after_retry")),
    }
    worker_s = sum(r.get("seconds") or 0 for r in turns)
    eval_s = sum(r.get("seconds") or 0 for r in stages)
    cad = sorted({str(r.get("cad_backend")) for r in rows if r.get("cad_backend")})
    return {
        "turns": len(turns),
        "worker_s": round(worker_s),
        "evaluator_s": round(eval_s),
        "tokens_input": sum(v["tokens_input"] for v in by_role.values()),
        "tokens_cached": sum(v["tokens_cached"] for v in by_role.values()),
        "tokens_output": sum(v["tokens_output"] for v in by_role.values()),
        "tokens_reasoning": sum(v["tokens_reasoning"] for v in by_role.values()),
        "usd": _sum_usd(turns),
        "by_role": by_role,
        "by_stage": by_stage,
        "gates": g,
        "attempts": att,
        "parts": sorted({str(r.get("part")) for r in rows}),
        "cad_backends": cad,
    }


def _group(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        out[str(r.get(key))].append(r)
    return dict(sorted(out.items()))


def format_summary(s: dict[str, Any], title: str = "telemetry") -> str:
    lines = [
        f"# {title}",
        f"parts: {', '.join(s['parts']) or '-'}",
        f"cad backends: {', '.join(s.get('cad_backends') or []) or '-'}",
        f"worker turns: {s['turns']}  worker wall: {s['worker_s']} s  evaluator wall: {s['evaluator_s']} s",
        (
            f"tokens in {s.get('tokens_input') or 0} cached {s.get('tokens_cached') or 0} "
            f"out {s.get('tokens_output') or 0} reasoning {s.get('tokens_reasoning') or 0}  "
            f"usd {s['usd'] if s.get('usd') is not None else '-'}"
        ),
        "",
        "role         turns  total_s  mean_s   p50_s   p95_s   max_s  budget  over  ok  engine  fallback  backends / models",
    ]
    for role, v in s["by_role"].items():
        lines.append(
            f"{role:12s} {v['turns']:5d} {v['total_s']:8d} {v['mean_s'] or 0:7.0f} {v.get('p50_s') or 0:7d} {v.get('p95_s') or 0:7d} {v['max_s'] or 0:7d} {v.get('budget_s') or 0:7d} "
            f"{v['over_budget']:5d} {v['ok']:3d} {v['engine_calls']:7d} {v['fallbacks']:9d}  {'/'.join(v['backends'])} {', '.join(v['models'])}"
            + (f"  reasoning {v['reasoning_share']:.2f}" if v.get("reasoning_share") is not None else "")
            + (f"  usd {v['usd']}" if v.get("usd") is not None else "")
            + (f"  step {v['median_step_s']} s" if v.get("median_step_s") is not None else "")
        )
    lines += ["", "stage        runs  total_s  mean_s   max_s  engine  engine_s  cached  ok"]
    for st, v in s["by_stage"].items():
        lines.append(
            f"{st:12s} {v['runs']:4d} {v['total_s']:8d} {v['mean_s'] or 0:7.0f} {v['max_s'] or 0:7d} {v['engine_calls']:7d} {v['engine_s']:9d} {v['cached']:7d} {v['ok']:3d}"
        )
    g, a = s["gates"], s["attempts"]
    lines += [
        "",
        f"gates: {g['pass']}/{g['evaluations']} PASS ({g['retries']} after a retry)   attempts: {a['pass']}/{a['attempts']} PASS, mean {a['mean_s'] or '-'} s, {a['over_budget']} over budget",
    ]
    return "\n".join(lines)


def compare(base: dict[str, Any], cur: dict[str, Any]) -> str:
    lines = [
        "# telemetry compare (baseline -> current)",
        f"worker wall: {base['worker_s']} -> {cur['worker_s']} s ({_ratio(base['worker_s'], cur['worker_s'])})",
        f"evaluator wall: {base['evaluator_s']} -> {cur['evaluator_s']} s ({_ratio(base['evaluator_s'], cur['evaluator_s'])})",
        "",
        "role         base_mean_s  cur_mean_s  ratio   base_n  cur_n",
    ]
    for role in sorted(set(base["by_role"]) | set(cur["by_role"])):
        b, c = base["by_role"].get(role, {}), cur["by_role"].get(role, {})
        lines.append(
            f"{role:12s} {b.get('mean_s') or 0:11.0f} {c.get('mean_s') or 0:11.0f}  {_ratio(b.get('mean_s'), c.get('mean_s')):>6}  {b.get('turns', 0):6d} {c.get('turns', 0):6d}"
        )
    lines += ["", "stage        base_mean_s  cur_mean_s  ratio   base_engine  cur_engine"]
    for st in sorted(set(base["by_stage"]) | set(cur["by_stage"])):
        b, c = base["by_stage"].get(st, {}), cur["by_stage"].get(st, {})
        lines.append(
            f"{st:12s} {b.get('mean_s') or 0:11.0f} {c.get('mean_s') or 0:11.0f}  {_ratio(b.get('mean_s'), c.get('mean_s')):>6}  {b.get('engine_calls', 0):11d} {c.get('engine_calls', 0):11d}"
        )
    bg, cg = base["gates"], cur["gates"]
    lines += [
        "",
        f"gates PASS: {bg['pass']}/{bg['evaluations']} -> {cg['pass']}/{cg['evaluations']}   attempts PASS: {base['attempts']['pass']}/{base['attempts']['attempts']} -> {cur['attempts']['pass']}/{cur['attempts']['attempts']}",
    ]
    return "\n".join(lines)


def _ratio(a: float | None, b: float | None) -> str:
    if not a or b is None:
        return "-"
    return f"x{b / a:.2f}"


def design_summary(design: str) -> dict[str, Any]:
    """What the truth report shows per arm: worker wall by role, backends, over-budget turns, evaluator wall."""
    s = summarize(rows_for(design))
    return {
        "worker_s_by_role": {k: v["total_s"] for k, v in s["by_role"].items()},
        "backends": sorted({b for v in s["by_role"].values() for b in v["backends"]}),
        "cad_backends": s.get("cad_backends") or [],
        "over_budget_turns": sum(v["over_budget"] for v in s["by_role"].values()),
        "evaluator_s": s["evaluator_s"],
        "worker_s": s["worker_s"],
    }


# --- critical path -------------------------------------------------------------------------

BUCKETS = (
    "worker_union_s",
    "evaluator_s",
    "interruption_s",
    "latency_s",
)  # priority when intervals overlap; uncovered time is other_s
ROUND_RE = re.compile(r"^correction-(\d+)")


def intervals(rows: list[dict[str, Any]]) -> list[tuple[float, float, str, dict[str, Any]]]:
    """(start, end, bucket, row) per timed row. A turn is worker time from its (last) dispatch to done, an interruption between a first
    dispatch and a re-dispatch, and latency from issue to dispatch and from done to the pipeline consuming it; a stage is evaluator time."""
    out: list[tuple[float, float, str, dict[str, Any]]] = []
    for r in rows:
        end = _ts(r.get("ts"))
        if end is None:
            continue
        if r.get("kind") == "stage":
            out.append((end - float(r.get("seconds") or 0), end, "evaluator_s", r))
        elif r.get("kind") == "turn":
            issued, first, again, done, consumed = (
                _ts(r.get(k)) for k in ("issued_at", "dispatched_at", "redispatched_at", "done_at", "consumed_at")
            )
            if done is None:  # a row from before the lifecycle fields: issue -> done, recorded at pickup
                out.append((end - float(r.get("seconds") or 0), end, "worker_union_s", r))
                continue
            out.append((again or first or issued or done, done, "worker_union_s", r))
            if first and again:
                out.append((first, again, "interruption_s", r))
            if issued and first:
                out.append((issued, first, "latency_s", r))
            if consumed:
                out.append((done, consumed, "latency_s", r))
    return [iv for iv in out if iv[1] > iv[0]]


def timeline(rows: list[dict[str, Any]], start: float | None = None, end: float | None = None) -> dict[str, int]:
    """Exclusive critical-path buckets over [start, end]: each second goes to the highest-priority interval covering it."""
    iv = intervals(rows)
    start = min((a for a, _, _, _ in iv), default=0.0) if start is None else start
    end = max((b for _, b, _, _ in iv), default=start) if end is None else end
    cuts = sorted({start, end, *(min(max(x, start), end) for a, b, _, _ in iv for x in (a, b))})
    out = dict.fromkeys((*BUCKETS, "other_s"), 0.0)
    for lo, hi in zip(cuts, cuts[1:]):
        mid = (lo + hi) / 2
        cover = {k for a, b, k, _ in iv if a <= mid < b}
        out[next((k for k in BUCKETS if k in cover), "other_s")] += hi - lo
    return {**{k: round(v) for k, v in out.items()}, "wall_s": round(max(0.0, end - start))}


def round_of(row: dict[str, Any]) -> int | None:
    m = ROUND_RE.match(str(row.get("key") or ""))
    return int(m.group(1)) if m else None


def attempt_window(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], float | None, float | None]:
    """The rows of the latest attempt: a finished one ends at its attempt row; rows after the last attempt row are one in progress."""
    idx = [i for i, r in enumerate(rows) if r.get("kind") == "attempt"]
    if idx and idx[-1] == len(rows) - 1:
        a = rows[-1]
        start, end = _ts(a.get("started")), _ts(a.get("ts"))
        prev = idx[-2] if len(idx) > 1 else -1
        return [r for r in rows[prev + 1 : -1] if start is None or (_ts(r.get("ts")) or 0) >= start], start, end
    tail = rows[idx[-1] + 1 :] if idx else rows
    return tail, None, None


def waterfall(rows: list[dict[str, Any]], title: str = "timeline") -> str:
    """Per-round waterfall of one attempt: offset, duration, what ran, and the critical-path buckets."""
    win, start, end = attempt_window(rows)
    iv = sorted(intervals(win), key=lambda x: x[0])
    if not iv:
        return f"# {title}\n(no timed rows)"
    t0 = start if start is not None else iv[0][0]
    cp = timeline(win, t0, end)
    lines = [
        f"# {title}",
        f"wall {_mmss(cp['wall_s'])}: "
        + ", ".join(f"{k[:-2].replace('_union', '')} {_mmss(cp[k])}" for k in (*BUCKETS, "other_s")),
        "",
    ]
    rnd = 0
    for a, b, bucket, r in iv:
        if r.get("kind") == "turn" and bucket == "worker_union_s":
            n = round_of(r)
            if n is not None and n != rnd:
                rnd = n
                lines.append(f"round {n}")
        what = f"{r.get('role')} {r.get('order_id') or ''}".strip() if r.get("kind") == "turn" else str(r.get("stage"))
        detail = ""
        if r.get("kind") == "turn" and bucket == "worker_union_s":
            detail = (
                f"  engine {r.get('engine_calls') or 0} calls {r.get('engine_seconds') or 0} s"
                + (f" share {r['engine_share']}" if r.get("engine_share") is not None else "")
                + (f" first call +{r['first_engine_call_s']} s" if r.get("first_engine_call_s") is not None else "")
            )
        elif r.get("kind") == "stage" and (r.get("engine_calls") or r.get("steps") or r.get("timings")):
            detail = f"  engine {r.get('engine_calls') or 0} calls {r.get('engine_seconds') or 0} s" + (
                f" (startup {r['engine_startup_s']} s)" if r.get("engine_startup_s") else ""
            )
        lines.append(f"  +{_mmss(a - t0):>6} {_mmss(b - a):>6}  {bucket[:-2].replace('_union', ''):12s} {what}{detail}")
    return "\n".join(lines)


def _mmss(s: float) -> str:
    s = int(round(max(0.0, s)))
    return f"{s // 60}:{s % 60:02d}"


# --- transcript estimates ------------------------------------------------------------------


def _transcripts_root() -> Path:
    override = os.environ.get("OPENCAD_TRANSCRIPTS")
    return Path(override) if override else Path.home() / ".cursor" / "projects"


def _transcript_path(agent_id: str) -> Path | None:
    root = _transcripts_root()
    direct = root / "subagents" / f"{agent_id}.jsonl"
    if direct.is_file():
        return direct
    hits = sorted(root.glob(f"**/subagents/{agent_id}.jsonl"))
    return hits[0] if hits else None


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(p.get("text") or "") for p in content if isinstance(p, dict))
    return ""


_SEGMENT_CACHE: dict[tuple[str, int], dict[str, dict[str, int]]] = {}

_OFF_BRIEF_META = {"_campaign", "_logs", "_bakeoff", "_regress", "_spikes"}


def _off_brief_path(path: str, *, backend: str | None, part: str | None, order_id: str | None) -> bool:
    """A Read/Grep path outside this order: library, tests, truth, another part, or another order."""
    parts = [p for p in path.replace("\\", "/").split("/") if p not in ("", ".")]
    for i, seg in enumerate(parts):
        nxt = parts[i + 1] if i + 1 < len(parts) else None
        nxt2 = parts[i + 2] if i + 2 < len(parts) else None
        if seg == "src" and nxt == "opencad":
            return True
        if seg in ("tests", "truth"):
            return True
        if seg == "parts" and nxt and nxt2 and (backend is None or nxt != backend or nxt2 != part):
            return True
        if seg == "results" and nxt:
            if backend is None or nxt != backend:
                return True
            if nxt2 and nxt2 != part and nxt2 not in _OFF_BRIEF_META:
                return True
            if order_id and "worker" in parts[i + 1 :]:
                wi = parts.index("worker", i + 1)
                oid = parts[wi + 1] if wi + 1 < len(parts) else None
                if oid and oid != order_id:
                    return True
        if seg == "designs" and nxt and nxt != f".staging-{part}" and (part is None or nxt != part):
            return True
    return False


def _off_brief_hits(part: dict[str, Any], *, backend: str | None, part_name: str | None, order_id: str | None) -> int:
    if str(part.get("name") or "").lower() not in ("read", "grep"):
        return 0
    raw = part.get("input") or {}
    paths = [raw[k] for k in ("path", "target_directory") if isinstance(raw.get(k), str) and raw[k].strip()]
    if not paths:
        return 1 if str(part.get("name") or "").lower() == "grep" else 0
    return sum(1 for p in paths if _off_brief_path(p, backend=backend, part=part_name, order_id=order_id))


def _segments(agent_id: str) -> dict[str, dict[str, int]] | None:
    """Generated output of one worker transcript, split at each order's brief.md so a resumed correction is its own segment."""
    path = _transcript_path(agent_id)
    if path is None:
        return None
    key = (str(path), path.stat().st_mtime_ns)
    cached = _SEGMENT_CACHE.get(key)
    if cached is not None:
        return cached
    buckets: dict[str, dict[str, int]] = {}
    ctx: dict[str, tuple[str | None, str | None]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (ev.get("message") or {}).get("content")
        if ev.get("role") == "user":
            text = _message_text(content)
            loc = _BRIEF_LOC_RE.search(text)
            if loc:
                current = loc.group(3)
                ctx[current] = (loc.group(1), loc.group(2))
            else:
                m = _ORDER_RE.search(text)
                if m:
                    current = m.group(1)
            continue
        if ev.get("role") != "assistant" or current is None:
            continue
        b = buckets.setdefault(current, {"chars": 0, "tool_calls": 0, "model_steps": 0, "off_brief_reads": 0})
        b["model_steps"] += 1
        parts = content if isinstance(content, list) else [{"type": "text", "text": content}]
        be, pt = ctx.get(current, (None, None))
        for part in parts:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text":
                b["chars"] += len(part.get("text") or "")
            elif part.get("type") == "tool_use":
                b["tool_calls"] += 1
                b["chars"] += len(json.dumps(part.get("input") or {}))
                b["off_brief_reads"] += _off_brief_hits(part, backend=be, part_name=pt, order_id=current)
    out = {oid: {**b, "est_output_tokens": round(b["chars"] / 4)} for oid, b in buckets.items()}
    _SEGMENT_CACHE[key] = out
    return out


def transcript_usage(agent_id: str, order_id: str | None = None) -> dict[str, int] | None:
    """Estimated output of one order: assistant text plus tool-call arguments, chars / 4. A lower bound (no input or unrecorded reasoning)."""
    segs = _segments(agent_id)
    if segs is None:
        return None
    if order_id is None:
        if not segs:
            return {"chars": 0, "est_output_tokens": 0, "tool_calls": 0, "model_steps": 0, "off_brief_reads": 0}
        return {
            "chars": sum(s["chars"] for s in segs.values()),
            "est_output_tokens": sum(s["est_output_tokens"] for s in segs.values()),
            "tool_calls": sum(s["tool_calls"] for s in segs.values()),
            "model_steps": sum(s["model_steps"] for s in segs.values()),
            "off_brief_reads": sum(s.get("off_brief_reads", 0) for s in segs.values()),
        }
    seg = segs.get(order_id)
    if seg is None:
        return {"chars": 0, "est_output_tokens": 0, "tool_calls": 0, "model_steps": 0, "off_brief_reads": 0}
    return seg


def _usage_for_turns(turns: list[dict[str, Any]]) -> dict[str, int] | None:
    total = {"est_output_tokens": 0, "tool_calls": 0, "model_steps": 0, "off_brief_reads": 0}
    found = False
    seen: set[tuple[str, str]] = set()
    for r in turns:
        tid = r.get("thread_id")
        if not tid:
            continue
        oid = str(r.get("order_id") or "")
        key = (str(tid), oid)
        if key in seen:
            continue
        seen.add(key)
        u = transcript_usage(str(tid), oid or None)
        if u is None:
            continue
        found = True
        for k in total:
            total[k] += int(u.get(k) or 0)
    return total if found else None


# --- attempt aggregation -----------------------------------------------------------------


def attempt_data(
    case: str, arm: str, entry: dict[str, Any], design: str, *, budget_s: float = ATTEMPT_BUDGET_S
) -> dict[str, Any]:
    """Aggregate this attempt's turn/stage rows (those after `entry.started`) into one attempt row."""
    started = entry.get("started")
    rows = [r for r in rows_for(design) if not started or str(r.get("ts", "")) >= str(started)]
    turns = [r for r in rows if r.get("kind") == "turn"]
    stages = [r for r in rows if r.get("kind") == "stage"]
    worker_s = sum(r.get("seconds") or 0 for r in turns)
    engine_s = sum(float(r.get("engine_seconds") or 0) for r in turns)
    t_start = _ts(started)
    critical = timeline(rows, t_start, t_start + float(entry.get("seconds") or 0) if t_start is not None else None)
    by_backend: dict[str, float] = defaultdict(float)
    by_role: dict[str, float] = defaultdict(float)
    for r in turns:
        by_backend[str(r.get("backend"))] += r.get("seconds") or 0
        by_role[str(r.get("role"))] += r.get("seconds") or 0
    eval_s = sum(r.get("seconds") or 0 for r in stages)
    hang_s = sum(float(r.get("network_wait_seconds") or 0) for r in turns)
    seconds = entry.get("seconds") or 0
    reason = None
    if seconds > budget_s:
        top = max(by_role.items(), key=lambda kv: kv[1])[0] if by_role else None
        reason = f"{seconds} s > {budget_s:.0f} s; worker {round(worker_s)} s (largest role {top}: {round(by_role.get(top, 0)) if top else 0} s), evaluator {round(eval_s)} s, network wait {round(hang_s)} s"
    sc = entry.get("scorecard") or {}
    models = [str(r.get("model")) for r in turns if r.get("model") and r.get("model") != "inherit"]
    data = {
        "case": case,
        "arm": arm,
        "design": design,
        "seconds": seconds,
        "budget_s": budget_s,
        "over_budget_reason": reason,
        "stage_reached": entry.get("stage_reached"),
        "worker_s": round(worker_s),
        "worker_s_by_backend": {k: round(v) for k, v in by_backend.items()},
        "worker_s_by_role": {k: round(v) for k, v in by_role.items()},
        "evaluator_s": round(eval_s),
        "network_wait_s": round(hang_s),
        "turns": len(turns),
        "over_budget_turns": sum(1 for r in turns if r.get("over_budget")),
        "engine_calls": sum(int(r.get("engine_calls") or 0) for r in rows if r.get("kind") in ("turn", "stage")),
        "engine_s": round(engine_s),
        "engine_share": round(engine_s / worker_s, 3) if worker_s else None,
        "rounds": max((round_of(r) or 0 for r in turns), default=0),
        "critical_path": critical,
        "gates": (entry.get("pipeline") or {}).get("gates"),
        "verdict": sc.get("verdict"),
        "error": (entry.get("error") or "")[:200] or None,
        "resume_from": entry.get("resume_from"),
        "started": started,
    }
    if models:
        data["model"] = max(set(models), key=models.count)
    if sc.get("accuracy_score") is not None:
        data["accuracy_score"] = sc["accuracy_score"]
    usage = _usage_for_turns(turns)
    if usage:
        data.update(usage)
    return data


# --- benchmark report ----------------------------------------------------------------------


def snapshot_path(tag: str) -> Path:
    """A promoted tag's rows, tracked in git: they outlive the ignored campaign files."""
    return baseline_pointer().parent / "baselines" / f"{tag}.jsonl"


def bench_rows(tag: str, files: list[Path] | None = None) -> list[dict[str, Any]]:
    """Every row labelled `tag` across the backends' campaign files (a bench spans backends), else its promoted snapshot."""
    if files is None:
        rows = [r for f in sorted(RESULTS_BASE.glob("*/_campaign/telemetry.jsonl")) for r in read(f) if r.get("tag") == tag]
        return rows or read(snapshot_path(tag))
    return [r for f in files for r in read(f) if r.get("tag") == tag]


def _snapshot(tag: str, rows: list[dict[str, Any]], report: Path | None) -> None:
    snap = snapshot_path(tag)
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_text("".join(json.dumps(r, default=str) + "\n" for r in rows), encoding="utf-8")
    if report is not None and report.exists() and report.resolve() != snap.with_suffix(".md").resolve():
        shutil.copyfile(report, snap.with_suffix(".md"))


def promote(tag: str, *, report: Path | None = None, suite: str = "parts") -> dict[str, Any]:
    """Point the suite's baseline at `tag` and snapshot its rows and report (and the outgoing baseline's, once)."""
    from opencad.paths import REPO_ROOT

    rows = bench_rows(tag)
    attempts = [r for r in rows if r.get("kind") == "attempt"]
    if not attempts:
        raise ValueError(f"no attempt rows tagged {tag}")
    pointer = baseline_pointer(suite)
    old = load_json(pointer) if pointer.exists() else {}
    previous = old.get("tag")
    if previous and previous != tag and not snapshot_path(previous).exists():
        prev_rows = bench_rows(previous)
        if prev_rows:
            _snapshot(previous, prev_rows, REPO_ROOT / old["report"] if old.get("report") else None)
    if report is None:
        report = next((p for p in (REGRESS / f"{tag}.md", REGRESS / f"bench-{tag}.md") if p.exists()), None)
    _snapshot(tag, rows, report)
    turns = [r for r in rows if r.get("kind") == "turn" and r.get("model") and r.get("model") != "inherit"]
    models = {}
    for role in sorted({str(r.get("role")) for r in turns}):
        picked = [str(r["model"]) for r in turns if str(r.get("role")) == role]
        models[role] = max(set(picked), key=picked.count)
    session = _session_s(attempts)
    summary = RESULTS_BASE / "_logs" / tag / "summary.json"
    if session is None and summary.exists():  # rows without start stamps: the regress session measured its own wall
        session = load_json(summary).get("session_wall_s")
    md = snapshot_path(tag).with_suffix(".md")
    info = {
        "tag": tag,
        "model": ", ".join(f"{role} {m}" for role, m in models.items()) or old.get("model"),
        "models": models,
        "report": str(md.relative_to(REPO_ROOT)) if md.exists() and md.is_relative_to(REPO_ROOT) else (str(md) if md.exists() else None),
        "previous": previous if previous != tag else old.get("previous"),
        "promoted_at": utc_now(),
        "session_wall_s": round(session) if session is not None else None,
    }
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    return info


def rows_for_spec(spec: str) -> list[dict[str, Any]]:
    """`baseline` is the promoted tag; `tag:<t>` is every backend's rows for that tag."""
    if spec == "baseline":
        tag = baseline_tag()
        if not tag:
            raise ValueError("no baseline pointer (results/_regress/baseline.json)")
        return bench_rows(tag)
    if spec.startswith("tag:"):
        return bench_rows(spec[4:])
    raise ValueError(spec)


def _signed_mmss(delta_s: float) -> str:
    sign = "+" if delta_s >= 0 else "-"
    return f"{sign}{_mmss(abs(delta_s))}"


def _draft_only(a: dict[str, Any]) -> bool:
    return a.get("stage_reached") == "published"


def _run_passed(a: dict[str, Any]) -> bool:
    """The regression bar: the scorecard passes and no gate fails."""
    g = a.get("gates") or {}
    return a.get("verdict") == "PASS" and isinstance(g, dict) and bool(g.get("pass")) and not g.get("fail")


def _session_s(attempts: list[dict[str, Any]]) -> float | None:
    """First start to last finish."""
    spans = [(t, t + float(a.get("seconds") or 0)) for a in attempts if (t := _ts(a.get("started"))) is not None]
    return max(e for _, e in spans) - min(s for s, _ in spans) if spans else None


def _regression_lines(runs: list[dict[str, Any]], drafts: list[dict[str, Any]]) -> list[str]:
    lines = []
    session = _session_s([*drafts, *runs])
    if session is not None:
        lines.append(f"Session wall {_mmss(session)}, first start to last finish across {len(drafts) + len(runs)} attempts.")
    parts = []
    for be in sorted({str(a.get("cad_backend")) for a in runs}):
        grp = [a for a in runs if str(a.get("cad_backend")) == be]
        misses = [f"{a.get('case')} {a.get('verdict') or a.get('stage_reached') or '-'} gates {_gates_label([a])}" for a in grp if not _run_passed(a)]
        parts.append(f"{be} {'FAIL' if misses else 'PASS'} ({len(grp) - len(misses)}/{len(grp)}{': ' + ', '.join(misses) if misses else ''})")
    if parts:
        lines.append("Regression (scorecard PASS and no failed gate): " + "; ".join(parts) + ".")
    return lines


def _attempt_turns(a: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    t0 = _ts(a.get("started"))
    if t0 is None:
        return []
    t1 = t0 + float(a.get("seconds") or 0) + 300
    case, be = str(a.get("case")), str(a.get("cad_backend"))
    out = []
    for r in rows:
        if r.get("kind") != "turn" or str(r.get("cad_backend")) != be:
            continue
        if str(r.get("part")) not in (case, str(a.get("design") or case)):
            continue
        # a draft-only attempt owns only its draft turns; a run on a reused design owns none of them
        is_draft = str(r.get("role")) == "draft"
        if (_draft_only(a) and not is_draft) or (a.get("resume_from") == "blockout" and is_draft):
            continue
        ts = _ts(r.get("ts"))
        if ts is not None and t0 <= ts <= t1:
            out.append(r)
    return out


def _scorecard_for(a: dict[str, Any]) -> dict[str, Any] | None:
    """The scorecard written during this attempt: same case, arm and backend, scored_at inside the attempt window."""
    t0 = _ts(a.get("started"))
    if t0 is None:
        return None
    t1 = t0 + float(a.get("seconds") or 0) + 300
    from opencad.paths import TRUTH

    arm = str(a.get("arm") or "spec-and-views")
    be = str(a.get("cad_backend") or "")
    case = str(a.get("case") or "")
    hits = []
    for f in sorted((TRUTH / "cases" / case / "scorecards").glob(f"{arm}@{be}-20*.json")):
        try:
            card = load_json(f)
        except (OSError, json.JSONDecodeError):
            continue
        ts = _ts(card.get("scored_at"))
        if ts is not None and t0 <= ts <= t1:
            hits.append(card)
    return hits[-1] if hits else None


def _attempt_metrics(a: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Model, accuracy and estimated tokens, from the attempt row when it carries them and from transcripts and scorecards otherwise."""
    turns = _attempt_turns(a, rows)
    model = a.get("model")
    if not model or model == "inherit":
        models = [str(r.get("model")) for r in turns if r.get("model") and r.get("model") != "inherit"]
        model = max(set(models), key=models.count) if models else (model or "-")
    acc = a.get("accuracy_score")
    if acc is None:
        card = _scorecard_for(a)
        if card is not None:
            try:
                from opencad.truth.manifest import load_manifest
                from opencad.truth.scorer import accuracy_score

                acc = accuracy_score(card, load_manifest(str(a.get("case"))))
            except (OSError, ValueError, KeyError, TypeError, RuntimeError):
                acc = None
    usage = {
        "est_output_tokens": a.get("est_output_tokens"),
        "tool_calls": a.get("tool_calls"),
        "model_steps": a.get("model_steps"),
    }
    if usage["est_output_tokens"] is None:
        usage = _usage_for_turns(turns) or usage
    extra = _usage_for_turns(turns)
    off = None if extra is None else extra.get("off_brief_reads")
    if off is None:
        off = a.get("off_brief_reads")
    return {
        "model": model,
        "accuracy": acc,
        "est_output_tokens": usage.get("est_output_tokens"),
        "off_brief_reads": off,
    }


def _fmt_acc(v: float | None) -> str:
    return f"{v:.1f}" if isinstance(v, (int, float)) else "-"


def _fmt_tok(v: float | None) -> str:
    return f"{round(v)}" if isinstance(v, (int, float)) else "-"


def _mean_present(xs: list[float | None]) -> float | None:
    got = [float(x) for x in xs if isinstance(x, (int, float))]
    return statistics.fmean(got) if got else None


def _median_present(xs: list[float | None]) -> float | None:
    got = [float(x) for x in xs if isinstance(x, (int, float))]
    return statistics.median(got) if got else None


def _gates_label(grp: list[dict[str, Any]]) -> str:
    labels = []
    for a in grp:
        g = a.get("gates") or {}
        if isinstance(g, dict) and g:
            labels.append(f"{g.get('pass', 0)}/{g.get('pass', 0) + g.get('fail', 0)}")
    if not labels:
        return "-"
    if all(x == "11/11" for x in labels):
        return "11/11"
    return ", ".join(labels)


def _baseline_section(
    cells: dict[tuple[str, str], list[dict[str, Any]]],
    metrics: dict[int, dict[str, Any]],
    btag: str,
    *,
    draft_s: dict[str, float] | None = None,
    session_s: float | None = None,
) -> list[str]:
    """`draft_s`: each case's shared draft wall, added to its cells; a baseline that shared its drafts gets the same treatment,
    so cells always compare draft plus run on both sides."""
    draft_s = draft_s or {}
    base_rows = bench_rows(btag)
    base_all = [r for r in base_rows if r.get("kind") == "attempt"]
    base_drafts = sorted((a for a in base_all if _draft_only(a)), key=lambda r: str(r.get("started")))
    base_attempts = [a for a in base_all if not _draft_only(a)]
    base_draft_s = {str(a.get("case")): float(a.get("seconds") or 0) for a in base_drafts}
    base_metrics = {id(a): _attempt_metrics(a, base_rows) for a in base_attempts}
    base_cells: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for a in base_attempts:
        base_cells[(str(a.get("case")), str(a.get("cad_backend")))].append(a)
    lines = [
        "",
        f"## Against the baseline `{btag}`",
        "",
        "Per cell: median wall and its delta (this bench minus the baseline), completion, gates, mean accuracy and median estimated tokens."
        + (" A cell's wall here includes its case's draft wall: the draft ran once and every backend reused it." if draft_s or base_draft_s else ""),
        "",
        "| cell | median wall | delta | completion | gates | accuracy | est tokens | baseline wall | baseline accuracy | baseline tokens |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    keys = sorted(set(cells) | set(base_cells))
    for key in keys:
        grp, bgrp = cells.get(key, []), base_cells.get(key, [])
        wall = statistics.median([a.get("seconds") or 0 for a in grp]) + draft_s.get(key[0], 0.0) if grp else None
        bwall = statistics.median([a.get("seconds") or 0 for a in bgrp]) + base_draft_s.get(key[0], 0.0) if bgrp else None
        n_pass = sum(1 for a in grp if a.get("verdict") == "PASS")
        acc = _mean_present([metrics[id(a)]["accuracy"] for a in grp]) if grp else None
        tok = _median_present([metrics[id(a)]["est_output_tokens"] for a in grp]) if grp else None
        bacc = _mean_present([base_metrics[id(a)]["accuracy"] for a in bgrp]) if bgrp else None
        btok = _median_present([base_metrics[id(a)]["est_output_tokens"] for a in bgrp]) if bgrp else None
        delta = _signed_mmss(wall - bwall) if wall is not None and bwall is not None else "-"
        completion = f"{n_pass}/{len(grp)}" if grp else "-"
        lines.append(
            f"| {key[0]} / {key[1]} | {_mmss(wall) if wall is not None else '-'} | {delta} | {completion} | {_gates_label(grp) if grp else '-'} | "
            f"{_fmt_acc(acc)} | {_fmt_tok(tok)} | {_mmss(bwall) if bwall is not None else '-'} | {_fmt_acc(bacc)} | {_fmt_tok(btok)} |"
        )
    cur_walls = [(a.get("seconds") or 0) + draft_s.get(case, 0.0) for (case, _), grp in cells.items() for a in grp]
    base_walls = [(a.get("seconds") or 0) + base_draft_s.get(str(a.get("case")), 0.0) for a in base_attempts]
    if cur_walls and base_walls:
        lines.append("")
        lines.append(
            f"Median wall {_mmss(statistics.median(cur_walls))} (baseline {_mmss(statistics.median(base_walls))}, "
            f"delta {_signed_mmss(statistics.median(cur_walls) - statistics.median(base_walls))})."
        )
    shared = [c for c in sorted(draft_s) if c in base_draft_s]
    if shared:
        lines.append(
            "Drafts: "
            + "; ".join(f"{c} {_mmss(draft_s[c])} (baseline {_mmss(base_draft_s[c])}, {_signed_mmss(draft_s[c] - base_draft_s[c])})" for c in shared)
            + "."
        )
    base_session = _session_s(base_all) if base_drafts else None
    sequential = sum(statistics.median([a.get("seconds") or 0 for a in bgrp]) for bgrp in base_cells.values())
    if session_s is not None and base_session:
        lines.append(
            f"Session wall {_mmss(session_s)} against the baseline session {_mmss(base_session)}: delta {_signed_mmss(session_s - base_session)}."
        )
    elif session_s is not None and sequential:
        lines.append(
            f"Session wall {_mmss(session_s)} against {_mmss(sequential)} for one sequential pass at the baseline medians "
            f"(sum of its {len(base_cells)} cell medians): {session_s / sequential:.0%} of that time, delta {_signed_mmss(session_s - sequential)}."
        )
    return lines


def bench(tag: str, rows: list[dict[str, Any]], *, against: str | None = None, suite: str = "parts") -> str:
    """case x backend: wall, verdict, rounds, turns, critical-path buckets, model, accuracy and estimated tokens."""
    attempts = [r for r in rows if r.get("kind") == "attempt"]
    metrics = {id(a): _attempt_metrics(a, rows) for a in attempts}
    drafts = sorted((a for a in attempts if _draft_only(a)), key=lambda r: (str(r.get("case")), str(r.get("started"))))
    attempts = [a for a in attempts if not _draft_only(a)]
    draft_s = {str(a.get("case")): float(a.get("seconds") or 0) for a in drafts}
    lines = [
        f"# Bench `{tag}`",
        "",
        (
            f"Generated {utc_now()} by `python -m opencad telemetry bench --tag {tag}`. Times in m:ss; buckets are exclusive "
            "(worker > evaluator > interruption > latency > other) and sum to the wall. Accuracy is the tolerance-normalized score (0-100). "
            "Estimated tokens are generated characters / 4, a lower bound. Off-brief reads are Read/Grep calls under `src/opencad`, `tests/`, `truth/`, another part, or another order."
        ),
        "",
    ]
    btag = against or baseline_tag(suite)
    baseline_model = None
    if tag == btag:
        info = load_json(baseline_pointer(suite))
        baseline_model = info.get("model")
        lines += [f"Baseline model: {baseline_model}.", ""]
    regression = _regression_lines(attempts, drafts)
    if regression:
        lines += [*regression, ""]
    lines += [
        "| case | backend | wall | verdict | gates | rounds | turns | worker | evaluator | latency | interruption | other | engine share | model | accuracy | est tokens | off-brief reads |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for a in sorted(attempts, key=lambda r: (str(r.get("case")), str(r.get("cad_backend")), str(r.get("started")))):
        cp = a.get("critical_path") or {}
        g = a.get("gates") or {}
        gates = f"{g.get('pass', 0)}/{g.get('pass', 0) + g.get('fail', 0)}" if isinstance(g, dict) and g else "-"
        m = metrics[id(a)]
        model = m["model"] if m["model"] not in (None, "-", "inherit") else (baseline_model or m["model"])
        lines.append(
            f"| {a.get('case')} | {a.get('cad_backend')} | {_mmss(a.get('seconds') or 0)} | {a.get('verdict') or a.get('stage_reached') or '-'} | {gates} | "
            f"{a.get('rounds', '-')} | {a.get('turns', '-')} | "
            + " | ".join(
                _mmss(cp.get(k) or 0) if cp else "-"
                for k in ("worker_union_s", "evaluator_s", "latency_s", "interruption_s", "other_s")
            )
            + f" | {a.get('engine_share') if a.get('engine_share') is not None else '-'} | {model} | {_fmt_acc(m['accuracy'])} | {_fmt_tok(m['est_output_tokens'])} | "
            + (str(int(m["off_brief_reads"])) if isinstance(m.get("off_brief_reads"), (int, float)) else "-")
            + " |"
        )
    if drafts:
        lines += [
            "",
            "Drafts (one per case, reused by every backend; not counted in the cells):",
            "",
            "| case | backend | wall | stage reached | turns | model | est tokens | off-brief reads |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for a in drafts:
            m = metrics[id(a)]
            off = str(int(m["off_brief_reads"])) if isinstance(m.get("off_brief_reads"), (int, float)) else "-"
            lines.append(
                f"| {a.get('case')} | {a.get('cad_backend')} | {_mmss(a.get('seconds') or 0)} | {a.get('stage_reached')} | {a.get('turns', '-')} | "
                f"{m['model']} | {_fmt_tok(m['est_output_tokens'])} | {off} |"
            )
    lines += [
        "",
        "| cell | attempts | PASS | completion | median wall | p95 wall | median worker | median evaluator | median latency | accuracy | est tokens |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    cells: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for a in attempts:
        cells[(str(a.get("case")), str(a.get("cad_backend")))].append(a)
    for (case, be), grp in sorted(cells.items()):
        walls = [a.get("seconds") or 0 for a in grp]

        def med(k: str, grp: list[dict[str, Any]] = grp) -> str:
            return _mmss(statistics.median([(a.get("critical_path") or {}).get(k) or 0 for a in grp]))

        n_pass = sum(1 for a in grp if a.get("verdict") == "PASS")
        acc = _mean_present([metrics[id(a)]["accuracy"] for a in grp])
        tok = _median_present([metrics[id(a)]["est_output_tokens"] for a in grp])
        lines.append(
            f"| {case} / {be} | {len(grp)} | {n_pass} | {n_pass / len(grp):.0%} | {_mmss(statistics.median(walls))} | {_mmss(_pct(walls, 95) or 0)} | "
            f"{med('worker_union_s')} | {med('evaluator_s')} | {med('latency_s')} | {_fmt_acc(acc)} | {_fmt_tok(tok)} |"
        )
    walls = [a.get("seconds") or 0 for a in attempts]
    if walls:
        n_pass = sum(1 for a in attempts if a.get("verdict") == "PASS")
        sentence = f"All cells: {n_pass}/{len(attempts)} PASS ({n_pass / len(attempts):.0%}), median wall {_mmss(statistics.median(walls))}, p95 {_mmss(_pct(walls, 95) or 0)}"
        acc = _mean_present([metrics[id(a)]["accuracy"] for a in attempts])
        tok = _median_present([metrics[id(a)]["est_output_tokens"] for a in attempts])
        if acc is not None:
            sentence += f", mean accuracy {acc:.1f}"
        if tok is not None:
            sentence += f", median est tokens {round(tok)}"
        lines += ["", sentence + "."]
    if btag and tag != btag:
        session = _session_s([*drafts, *attempts]) if drafts else None
        lines += _baseline_section(cells, metrics, btag, draft_s=draft_s, session_s=session)
    lines += [
        "",
        "Evaluator stages (mean s per run, by backend):",
        "",
        "| stage | " + " | ".join(sorted({str(r.get("cad_backend")) for r in rows})) + " |",
        "|---|" + "---|" * len({str(r.get("cad_backend")) for r in rows}),
    ]
    bes = sorted({str(r.get("cad_backend")) for r in rows})
    stages = [r for r in rows if r.get("kind") == "stage"]
    for st in sorted({str(r.get("stage")) for r in stages}):
        cells_s = []
        for be in bes:
            secs = [
                r.get("seconds") or 0 for r in stages if str(r.get("stage")) == st and str(r.get("cad_backend")) == be
            ]
            cells_s.append(f"{_mean(secs):.0f} (n={len(secs)})" if secs else "-")
        lines.append(f"| {st} | " + " | ".join(cells_s) + " |")
    turns = [r for r in rows if r.get("kind") == "turn"]
    if turns:
        lines += [
            "",
            "Worker turns (median worker s / engine share, by role and backend):",
            "",
            "| role | " + " | ".join(bes) + " |",
            "|---|" + "---|" * len(bes),
        ]
        for role in sorted({str(r.get("role")) for r in turns}):
            cells_t = []
            for be in bes:
                grp = [r for r in turns if str(r.get("role")) == role and str(r.get("cad_backend")) == be]
                ws = [r.get("worker_s") if r.get("worker_s") is not None else r.get("seconds") or 0 for r in grp]
                shares = [r.get("engine_share") for r in grp if r.get("engine_share") is not None]
                cells_t.append(
                    f"{statistics.median(ws):.0f} / {statistics.median(shares):.2f} (n={len(grp)})"
                    if grp and shares
                    else f"{statistics.median(ws):.0f} (n={len(grp)})"
                    if grp
                    else "-"
                )
            lines.append(f"| {role} | " + " | ".join(cells_t) + " |")
    return "\n".join(lines) + "\n"


def _ts(s: str | None) -> float | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        return None

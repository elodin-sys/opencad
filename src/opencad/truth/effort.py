"""Reliability and effort per design and per case arm, from stage JSONs and attempts.yaml.

A model that succeeds once after manual rescue is a different result from a pipeline that
succeeds unattended; these numbers keep the two apart. Human interventions are always 0 for a
headless `truth run`; a manual re-run is a new attempt, never a correction of an old one.
"""

from __future__ import annotations

from typing import Any

from opencad.io import load_json
from opencad.paths import results_dir

STAGES = ("blockout", "plan", "model", "verify", "export", "inspect", "edit")


def _codex(block: dict[str, Any] | None) -> dict[str, Any]:
    c = (block or {}).get("codex") or {}
    u = c.get("usage") or {}
    return {"seconds": c.get("seconds") or 0, "commands": c.get("commands") or 0, "input": u.get("input") or 0, "output": u.get("output") or 0}


def effort_for_design(design: str) -> dict[str, Any]:
    """Codex time/tokens, engine calls, tool failures and repair iterations for one results/<design>."""
    root = results_dir(design)
    stages = {s: load_json(root / f"{s}.json") for s in STAGES if (root / f"{s}.json").exists()}
    fb = load_json(root / "gate_feedback.json") if (root / "gate_feedback.json").exists() else {}
    codex_sessions: list[dict[str, Any]] = []
    mdl = stages.get("model") or {}
    codex_sessions.append(_codex(mdl))
    if mdl.get("retry"):
        codex_sessions.append(_codex(mdl["retry"]))
    codex_sessions.append(_codex(stages.get("plan")))
    for it in (stages.get("blockout") or {}).get("iterations", []):
        codex_sessions.append(_codex(it))
    calls = [e for st in stages.values() for e in st.get("engine_calls", [])]
    tool_failures = [e for e in calls if e.get("class") in ("transient", "timeout")]
    return {
        "design": design,
        "codex_seconds": sum(s["seconds"] for s in codex_sessions),
        "codex_commands": sum(s["commands"] for s in codex_sessions),
        "tokens_input": sum(s["input"] for s in codex_sessions),
        "tokens_output": sum(s["output"] for s in codex_sessions),
        "engine_calls": len(calls),
        "tool_failures": len(tool_failures),
        "pipeline_retry": bool((fb.get("retry") or {}).get("attempted")),
        "blockout_iterations": (stages.get("blockout") or {}).get("iterations_used"),
        "gates": fb.get("summary"),
        "gates_ok": fb.get("ok"),
    }


def reliability_for_arm(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    """Hosted attempts only (score-only rows are re-judgements of an existing STEP, not runs)."""
    hosted = [a for a in attempts if a.get("resume_from") != "score"]
    scored = [a for a in hosted if a.get("scorecard")]
    passes = [a for a in scored if a["scorecard"].get("verdict") == "PASS"]
    first = hosted[0] if hosted else None
    first_pass = bool(first and (first.get("scorecard") or {}).get("verdict") == "PASS")
    return {
        "hosted_runs": len(hosted),
        "scored": len(scored),
        "passes": len(passes),
        "first_run_pass": first_pass,
        "final_pass": bool(scored and scored[-1]["scorecard"].get("verdict") == "PASS"),
        "pipeline_retries": sum(1 for a in hosted if (a.get("pipeline") or {}).get("retry")),
        "mean_seconds": round(sum(a.get("seconds", 0) for a in hosted) / len(hosted)) if hosted else None,
        "errors": sum(1 for a in hosted if a.get("error") or a.get("score_error")),
        "human_interventions": 0,
    }

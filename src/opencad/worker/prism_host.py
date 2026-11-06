"""Prism-hosted worker turns: token usage rebuilt from Prism's thread record.

When Prism orchestrates, a work order runs as a Prism sub-agent. Prism keeps the sub-agent's tool transcript and the measured
usage of its *last* request (final context, input and output tokens) in its thread store
(`~/Library/Application Support/prism/threads/chat.sqlite`, `thread_records.source`), but no per-request ledger the way a
Codex exec writes `turn.completed` events. This module reconstructs what the provider bills for a tool loop from that record:

- one request per tool call plus the final answer; request k re-reads the whole context `I_k`, so billed input is the sum of
  every `I_k`, and every request after the first is a prefix-cache hit on the previous request's prompt;
- the context grows by each tool call's arguments (a written file's size, a command line), its result (`Output size: ~N
  tokens` when the host printed one, else chars / 4, a flat allowance for an image) and each progress report;
- the last request's input is the measured value, which pins the base context (system prompt, tool schemas, brief);
- output counts the visible generation (tool arguments, reports, the final answer, the last one measured). Hidden reasoning
  tokens are not in the record, so `output` and the USD priced from it are lower bounds.

The result carries `mode = "prism-estimate"`; the bake-off reports and the site mark such cells as estimated rather than metered.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

MODE = "prism-estimate"
DEFAULT_THREAD_DB = Path.home() / "Library" / "Application Support" / "prism" / "threads" / "chat.sqlite"
CHARS_PER_TOKEN = 4
IMAGE_RESULT_TOKENS = 1600  # one rendered PNG as the model sees it
MIN_BASE_CONTEXT = 2000  # system prompt + tool schemas + brief can never be smaller
ARG_TOKENS = {"exec_command": 80, "edit_file": 250, "view_image": 30, "notify_parent": 0, "write_file": 800}
_OUTPUT_SIZE_RE = re.compile(r"Output size: ~(\d+) tokens")
_WRITTEN_RE = re.compile(r"^(?:write_file|edit_file): updated (.+)$", re.M)


def thread_db() -> Path:
    return Path(os.environ.get("OPENCAD_PRISM_THREADS") or DEFAULT_THREAD_DB)


def _tokens(text: str | None) -> int:
    return len(text or "") // CHARS_PER_TOKEN


def _walk(obj: Any, out: list[dict[str, Any]]) -> None:
    if isinstance(obj, dict):
        block = obj.get("SubAgent")
        if isinstance(block, dict) and block.get("agent_id"):
            out.append(block)
        for v in obj.values():
            _walk(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, out)


def sub_agent_blocks(db: Path | None = None) -> list[dict[str, Any]]:
    """Every SubAgent block in every thread of Prism's store, read-only (the app keeps the database open)."""
    path = Path(db or thread_db())
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        for (source,) in con.execute("select source from thread_records where source is not null"):
            try:
                _walk(json.loads(source), out)
            except (json.JSONDecodeError, TypeError):
                continue
    finally:
        con.close()
    return out


def sub_agent_block(agent_id: str, db: Path | None = None) -> dict[str, Any] | None:
    return next((b for b in sub_agent_blocks(db) if str(b.get("agent_id")) == str(agent_id)), None)


def _result_tokens(tool: str, result: str) -> int:
    if tool == "view_image":
        return IMAGE_RESULT_TOKENS
    m = _OUTPUT_SIZE_RE.search(result or "")
    return int(m.group(1)) + 40 if m else _tokens(result)


def _args_tokens(tool: str, result: str) -> int:
    if tool == "write_file":
        m = _WRITTEN_RE.search(result or "")
        if m:
            try:
                return max(1, Path(m.group(1).strip()).stat().st_size // CHARS_PER_TOKEN)
            except OSError:
                pass
    return ARG_TOKENS.get(tool, 100)


def estimate_usage(block: dict[str, Any]) -> dict[str, Any]:
    """Billed usage of one sub-agent from its SubAgent block (`turns`, `tools`, `usage`, `text`)."""
    tools = {t[1]: (t[0], t[2] if len(t) > 2 else "") for t in block.get("tools") or [] if isinstance(t, (list, tuple)) and len(t) >= 2}
    measured = block.get("usage") or {}
    final_input = int(measured.get("input_tokens") or 0)
    final_output = int(measured.get("output_tokens") or _tokens(block.get("text")))
    # context deltas in transcript order; `request` marks the steps that cost a model request
    deltas: list[tuple[int, int, bool]] = []  # (added to context, of which visible output, is a request)
    for turn in block.get("turns") or []:
        kind, text = turn.get("kind"), turn.get("text") or ""
        if kind == "tool":
            tool, result = tools.get(text, ("unknown", ""))
            args = _args_tokens(tool, result)
            deltas.append((args + _result_tokens(tool, result), args, True))
        elif kind == "report":
            deltas.append((_tokens(text), _tokens(text), False))
        elif kind == "prompt":
            deltas.append((_tokens(text), 0, False))
    requests = sum(1 for _, _, req in deltas if req) + 1
    grown = sum(d for d, _, _ in deltas)
    scaled = False
    if final_input and final_input - grown < MIN_BASE_CONTEXT:
        # the transcript over-counts what the context holds (truncated tool output, compaction): shrink it to the measured size
        factor = max(0.0, final_input - MIN_BASE_CONTEXT) / grown if grown else 0.0
        deltas = [(int(d * factor), int(o * factor), req) for d, o, req in deltas]
        grown = sum(d for d, _, _ in deltas)
        scaled = True
    base = (final_input - grown) if final_input else MIN_BASE_CONTEXT
    inputs: list[int] = []
    context = base
    for added, _, req in deltas:
        if req:
            inputs.append(context)
        context += added
    inputs.append(context if not final_input else final_input)  # the final answer's request, measured when Prism recorded it
    cached = sum(inputs[:-1])  # request k+1 replays request k's prompt
    output = sum(o for _, o, _ in deltas) + final_output
    return {
        "input": int(sum(inputs)),
        "cached": int(cached),
        "output": int(output),
        "reasoning": 0,
        "requests": requests,
        "final_input": final_input,
        "final_context": int(measured.get("context_tokens") or 0),
        "base_context": int(base),
        "scaled": scaled,
        "model": block.get("model"),
        "agent_id": block.get("agent_id"),
    }


def usage_for_agents(agent_ids: list[str], db: Path | None = None) -> dict[str, Any] | None:
    """Summed usage of the sub-agents that ran one order (a re-dispatched order has two), None when Prism's record has none."""
    blocks = {str(b.get("agent_id")): b for b in sub_agent_blocks(db)}
    found = [estimate_usage(blocks[a]) for a in dict.fromkeys(str(a) for a in agent_ids) if a in blocks]
    if not found:
        return None
    total = {k: sum(int(f[k]) for f in found) for k in ("input", "cached", "output", "reasoning", "requests")}
    return {
        **total,
        "mode": MODE,
        "agents": found,
        "basis": "rebuilt from Prism's thread record: one request per tool call, context pinned to the measured final input, prefix "
                 "cache assumed; output excludes hidden reasoning, so output and USD are lower bounds",
    }


def dispatched_agents(order_dir: Path) -> list[str]:
    """Every agent id an order's dispatch.json names (each dispatch, and the current one)."""
    path = Path(order_dir) / "dispatch.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8")) or {}
    ids = [d.get("agent_id") for d in data.get("dispatches") or [] if isinstance(d, dict) and d.get("agent_id")]
    if data.get("agent_id"):
        ids.append(data["agent_id"])
    return [str(i) for i in dict.fromkeys(ids)]


def usage_for_order(order_dir: Path, db: Path | None = None) -> dict[str, Any] | None:
    """Usage for the agents named in an order's dispatch.json."""
    ids = dispatched_agents(order_dir)
    return usage_for_agents(ids, db) if ids else None

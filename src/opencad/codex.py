"""Worker-brief building blocks and report parsing shared by every backend.

Dispatch lives in `opencad.worker` (Cursor cad-worker orders by default, Codex through
`opencad.worker.codex_backend` when opted in). This module keeps the parts both need: the KCL
rules, the contract digest, the report-section parser and the Codex event/timeline helpers.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from opencad.schemas import PartContract

REPORT_SECTIONS = ("Result", "Files changed", "Verification", "Open questions", "Not this module")
HEADER_RE = re.compile(r"thread_id=(\S+) exit=(\d+) seconds=(\d+) commands=(\d+) usage=in:(\d+) cached:(\d+) out:(\d+) reasoning:(\d+)")

_USAGE_FIELDS = (
    ("input", "input_tokens"),
    ("cached", "cached_input_tokens"),
    ("output", "output_tokens"),
    ("reasoning", "reasoning_output_tokens"),
)


def _usage_counts(usage: dict) -> dict[str, int]:
    return {short: int(usage.get(short) or usage.get(long) or 0) for short, long in _USAGE_FIELDS}


def _running_total(turns: list[dict[str, int]]) -> bool:
    """True when each later `turn.completed` already contains the earlier ones (a thread total, not a fresh bill)."""
    for prev, nxt in zip(turns, turns[1:]):
        if nxt["input"] < prev["input"] or nxt["output"] < prev["output"]:
            return False
    last = turns[-1]
    return last["input"] >= sum(u["input"] for u in turns[:-1]) and last["output"] >= sum(u["output"] for u in turns[:-1])


def sum_turn_usage(events: list[dict]) -> dict[str, Any]:
    """Sum every `turn.completed` in one Codex exec.

    Cached tokens are a subset of input. Reasoning tokens are a subset of output and stay
    in their own field so a price card does not bill them twice. A resumed exec that reports
    a running thread total (each event dominates the previous, and the last covers the sum
    of the earlier ones) is billed from the last event only.
    """
    raw: list[dict] = []
    turns: list[dict[str, int]] = []
    for event in events:
        if not isinstance(event, dict) or event.get("type") != "turn.completed":
            continue
        raw.append(event)
        turns.append(_usage_counts(event.get("usage") or {}))
    empty = {"input": 0, "cached": 0, "output": 0, "reasoning": 0, "turns": 0, "mode": "empty", "note": None, "events": []}
    if not turns:
        return empty
    chosen = turns
    mode = "sum"
    note = None
    if len(turns) >= 2 and _running_total(turns):
        chosen = turns[-1:]
        mode = "last"
        note = "turn.completed usage is a running thread total; billed the last event so it is not added twice"
    total = {key: sum(turn[key] for turn in chosen) for key in ("input", "cached", "output", "reasoning")}
    total.update({"turns": len(turns), "mode": mode, "note": note, "events": raw})
    return total


def rollout_usage(rollout: Path, since: datetime | None = None) -> dict[str, int] | None:
    """Usage of one exec from its thread's Codex rollout file, for an exec killed before any `turn.completed` or a resumed one.

    `token_count` totals are cumulative over the thread, so a resumed exec is billed the last total minus the last one
    logged before `since` (the exec's start)."""
    before: dict[str, int] | None = None
    last: dict[str, int] | None = None
    for line in rollout.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        payload = event.get("payload") if isinstance(event, dict) else None
        info = payload.get("info") if isinstance(payload, dict) and payload.get("type") == "token_count" else None
        if not isinstance(info, dict) or not isinstance(info.get("total_token_usage"), dict):
            continue
        total = _usage_counts(info["total_token_usage"])
        ts = event.get("timestamp")
        if since is not None and ts and datetime.fromisoformat(ts) < since:
            before = total
        else:
            last = total
    if last is None:
        return None
    return {key: max(0, last[key] - (before or {}).get(key, 0)) for key in last}


def parse_sections(md: str) -> dict[str, str]:
    out: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and m.group(1).strip() in REPORT_SECTIONS:
            if current:
                out[current] = "\n".join(buf).strip()
            current, buf = m.group(1).strip(), []
        elif current:
            buf.append(line)
    if current:
        out[current] = "\n".join(buf).strip()
    return out


def extract_block(text: str, lang: str) -> str | None:
    """Last fenced code block tagged `lang` (a worker may show drafts before the final one)."""
    blocks = re.findall(rf"```{lang}[^\n]*\n(.*?)```", text, flags=re.S)
    return blocks[-1].strip() if blocks else None


def _short_cmd(cmd: str, limit: int = 140) -> str:
    cmd = " ".join(cmd.split())
    return cmd if len(cmd) <= limit else cmd[: limit - 1] + "…"


def format_event(e: dict) -> str | None:
    """Readable one-liner for a Codex `events.jsonl` item, or None to skip."""
    kind = e.get("type")
    item = e.get("item") or {}
    itype = item.get("type")
    if kind == "thread.started":
        return f"thread {e.get('thread_id', '?')}"
    if kind == "turn.started":
        return "turn started"
    if kind == "turn.completed":
        u = e.get("usage") or {}
        return (
            f"turn completed  in={u.get('input_tokens', 0)} "
            f"out={u.get('output_tokens', 0)} reason={u.get('reasoning_output_tokens', 0)}"
        )
    if kind in ("turn.failed", "error"):
        return f"FAILED {e.get('error', e)}"
    if kind == "item.completed" and itype == "agent_message":
        text = (item.get("text") or "").strip().replace("\n", " ")
        return f"codex: {text}" if text else None
    if kind == "item.started" and itype == "command_execution":
        return f"$ {_short_cmd(item.get('command') or '')}"
    if kind == "item.completed" and itype == "command_execution":
        code = item.get("exit_code")
        status = item.get("status") or ""
        out = (item.get("aggregated_output") or "").strip().splitlines()
        tail = out[-1][:160] if out else ""
        mark = "ok" if code == 0 else f"exit {code}"
        extra = f"  | {tail}" if tail else ""
        return f"  {mark} {status}{extra}"
    if kind == "item.completed" and itype == "file_change":
        changes = item.get("changes") or item.get("files") or []
        names = []
        if isinstance(changes, list):
            for c in changes[:8]:
                if isinstance(c, dict):
                    names.append(str(c.get("path") or c.get("file") or c))
                else:
                    names.append(str(c))
        return f"files: {', '.join(names)}" if names else "files changed"
    return None


def timeline_summary(run_dir: Path) -> dict[str, Any]:
    """Split a Codex turn's wall time into tool time (command started -> completed) and model time (everything else)."""
    p = Path(run_dir) / "timeline.jsonl"
    if not p.exists():
        return {}
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(rows) < 2:
        return {}
    tool = 0.0
    started: dict[str, float] = {}
    longest: list[tuple[float, str]] = []
    gaps: list[float] = []
    last_done = rows[0]["t"]
    for r in rows:
        if r.get("item_type") != "command_execution":
            continue
        if r["type"] == "item.started":
            started[r.get("id") or ""] = r["t"]
            gaps.append(r["t"] - last_done)
        elif r["type"] == "item.completed" and (r.get("id") or "") in started:
            d = r["t"] - started.pop(r.get("id") or "")
            tool += d
            longest.append((round(d, 1), r.get("id") or ""))
            last_done = r["t"]
    total = rows[-1]["t"] - rows[0]["t"]
    longest.sort(reverse=True)
    gaps_sorted = sorted(gaps)
    pct = (lambda q: round(gaps_sorted[min(len(gaps_sorted) - 1, int(q * len(gaps_sorted)))], 1)) if gaps_sorted else (lambda q: None)
    return {"wall_seconds": round(total), "tool_seconds": round(tool), "model_seconds": round(max(0.0, total - tool)),
            "commands": sum(1 for r in rows if r["type"] == "item.completed" and r.get("item_type") == "command_execution"),
            "longest_commands_s": [d for d, _ in longest[:5]],
            "step_latency_s": {"median": pct(0.5), "p90": pct(0.9), "max": pct(1.0), "steps": len(gaps_sorted)}}


# --- brief building blocks ---------------------------------------------------------------


def _profile_chord_lines(design_dir: Path | None) -> list[str]:
    if design_dir is None:
        return []
    path = Path(design_dir) / "reference" / "profile.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    m = data.get("measurements") or data
    lines = ["Profile chords (reference/profile.json):"]
    fp, fp_st = m.get("chord"), m.get("stagger_deg")
    if fp is not None:
        lines.append(f"  farthest-pair: {float(fp):g} mm at {float(fp_st or 0):g} deg")
    lm, lm_st = m.get("landmark_chord"), m.get("landmark_stagger_deg")
    if lm is not None:
        lines.append(f"  landmarks (LE–TE): {float(lm):g} mm at {float(lm_st or 0):g} deg")
    else:
        lines.append("  landmarks (LE–TE): not present in this profile.json")
    lines.append("  farthest-pair is not the documented stagger")
    return lines


def contract_digest(c: PartContract, design_dir: Path | None = None) -> str:
    lines = [f"Part `{c.name}`: {c.intent}", "", f"Units: {c.units.length}/{c.units.angle}. Frame origin: {c.frame.origin}."]
    for ax, meaning in c.frame.axes.items():
        lines.append(f"  +{ax}: {meaning}")
    for d in c.frame.datums:
        lines.append(f"  datum {d.name}: {d.description}")
    lines.append(f"Envelope: min {list(c.envelope.min)} max {list(c.envelope.max)} (tol {c.envelope.tolerance}).")
    lines.append("Parameters (name = value unit | provenance | tolerance | note):")
    for p in c.parameters:
        note = p.description or p.formula or p.rationale or p.source or ""
        lines.append(f"  {p.name} = {p.value:g}{p.unit} | {p.provenance} | ±{p.tolerance:g} | {note}")
    edits = [p for p in c.parameters if p.edit_test]
    if edits:
        lines.append("Edit tests (parameter, delta, expected volume_delta / direction / bbox_delta):")
        for p in edits:
            e = p.edit_test.expect
            bbox = list(e.bbox_delta) if e.bbox_delta is not None else None
            lines.append(
                f"  {p.name}: delta {p.edit_test.delta:g}{p.unit}; volume_delta {e.volume_delta}; "
                f"direction {e.direction}; bbox_delta {bbox}"
            )
    lines.append("Features:")
    for f in c.features:
        cnt = f" x{f.count}" if f.count else ""
        lines.append(f"  [{f.id}] {f.kind}{cnt}: {f.description} (params: {', '.join(f.parameters) or '-'}){' [optional/cosmetic]' if f.optional else ''}")
    if c.interfaces:
        lines.append("Interfaces that must not change (pinned acceptance items are re-measured after every edit):")
        for i in c.interfaces:
            pins = f" [pinned: {', '.join(i.checks)}]" if i.checks else ""
            lines.append(f"  {i.name}: {i.description}{pins}")
    a = c.acceptance
    lines.append("Acceptance:")
    if a.volume:
        lines.append(f"  volume {a.volume.expected} mm3 (tol {a.volume.tolerance or ''}{' rel ' + str(a.volume.tolerance_rel) if a.volume.tolerance_rel else ''}) — {a.volume.note}")
    if a.surface_area:
        lines.append(f"  surface area {a.surface_area.expected} mm2")
    if a.center_of_mass:
        com_note = f" — {a.center_of_mass.note}" if a.center_of_mass.note else ""
        lines.append(f"  centre of mass {list(a.center_of_mass.expected)} (±{a.center_of_mass.tolerance} per axis){com_note}")
    lines.append(f"  solid count {a.solid_count}; bbox tolerance {c.bbox_tolerance}")
    for s in a.sections:
        e = s.expect
        lines.append(f"  section {s.id}: plane {s.plane} = {s.at}; area {e.area} loops {e.loops} holes {e.holes} {s.description}")
    for f in a.faces:
        extra = f", area {f.area}" if f.area else ""
        center = f", center {list(f.center)}" if f.center is not None else ""
        lines.append(f"  named face {f.name}: plane {f.plane} = {f.at}, normal {f.normal}, mode {f.mode}{center}{extra}")
    for cy in a.cylinders:
        ext = f", length {cy.length}" if cy.length is not None else ""
        lines.append(f"  cylinder {cy.name}: {cy.kind}, radius {cy.r:g}, axis through {list(cy.point)} along {list(cy.direction)} "
                     f"(axis offset tol {cy.axis_tolerance or c.envelope.tolerance}, radius tol {cy.radius_tolerance}){ext} {cy.description}")
    for pl in a.planes:
        extra = f", area {pl.area}" if pl.area else ""
        lines.append(f"  plane {pl.name}: outward normal {list(pl.normal)} through {list(pl.point)}{extra} {pl.description}")
    for dm in a.dimensions:
        where = f"between faces {list(dm.between)}" if dm.between else "bbox extent"
        lines.append(f"  dimension {dm.name}: {where} along {dm.axis} = {dm.expected} (tol {dm.tolerance or ''}{' rel ' + str(dm.tolerance_rel) if dm.tolerance_rel else ''}) {dm.description}")
    for s in a.solids:
        vol = f", volume {s.volume.expected} (tol {s.volume.tolerance or ''}{' rel ' + str(s.volume.tolerance_rel) if s.volume.tolerance_rel else ''})" if s.volume else ""
        lines.append(f"  solid {s.name}: the body containing point {list(s.contains_point)}{vol} {s.description}")
    for h in a.hardware:
        geo = f"box {list(h.min)}..{list(h.max)}" if h.kind == "box" else (f"cylinder r={h.radius} along {list(h.direction)} from {list(h.point)} length {h.length}" if h.kind == "cylinder" else f"STEP {h.path}")
        excl = f" minus {len(h.exclude_cylinders)} cylinder(s)" if h.exclude_cylinders else ""
        lines.append(f"  hardware envelope {h.name}: {geo}{excl} (evaluator-side; the part must respect it) {h.description}")
    for cl in a.clearances:
        band = f"gap >= {cl.min_gap}" + (f" and <= {cl.max_gap}" if cl.max_gap is not None else "")
        lines.append(f"  clearance {cl.name}: {cl.a} vs {cl.b}: no interference, {band} {cl.description}")
    for p in a.passages:
        lines.append(f"  passage {p.name}: air from {list(p.point_a)} to {list(p.point_b)} must {'connect' if p.expect_connected else 'NOT connect'} inside the part (ports sealed by "
                     f"{'closing radius ' + str(p.seal_radius) if p.seal_radius else str(len(p.plugs)) + ' plug(s)'}); "
                     + (f"air volume {p.volume_min}..{p.volume_max} mm3 " if p.volume_min or p.volume_max else "") + p.description)
    for t in a.thickness:
        lines.append(f"  wall thickness {t.name}: {t.stat} of inward ray casts >= {t.min} mm" + (f" within {list(t.region[0])}..{list(t.region[1])}" if t.region else "") + f" {t.description}")
    for pr in a.probes:
        lines.append(f"  probe {pr.name}: points {[list(x) for x in pr.points]} must be {pr.state} {pr.description}")
    for cc in a.cylinder_counts:
        lines.append(f"  cylinder count {cc.name}: {cc.kind} cylinders of radius {cc.r:g} (±{cc.radius_tolerance})" + (f" along {list(cc.direction)}" if cc.direction else "")
                     + (f": exactly {cc.expected}" if cc.expected is not None else f": at least {cc.expected_min}") + f" {cc.description}")
    for g in a.gears:
        lines.append(f"  gear {g.name}: {g.teeth} teeth, module {g.module}, axis {list(g.point)} along {list(g.direction)}, counted at station {g.at}" + (f" on solid {g.solid}" if g.solid else "") + f" {g.description}")
    for ms in a.meshes:
        lines.append(f"  gear mesh {ms.name}: {ms.a} (axis {list(ms.axis_a[0])}) drives {ms.b} (axis {list(ms.axis_b[0])}) at ratio {ms.ratio:g}; rotated through {ms.pitch_deg:g} deg in {ms.steps} steps: zero interference, flank gap <= {ms.backlash_max} {ms.description}")
    lines.extend(_profile_chord_lines(design_dir))
    if c.open_questions:
        lines.append("Open questions recorded in the contract:")
        for q in c.open_questions:
            lines.append(f"  - {q}")
    return "\n".join(lines)


def yaml_from_report(text: str) -> dict[str, Any] | None:
    block = extract_block(text, "yaml") or extract_block(text, "yml")
    if not block:
        return None
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None



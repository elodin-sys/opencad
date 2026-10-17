"""Bake-off campaign: status, next rung, run wrapper, and report across backends."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from opencad.paths import DESIGNS, RESULTS_BASE, design_dir, membership, results_dir
from opencad.truth.manifest import case_dir

CANDIDATES = ("cadquery", "build123d", "freecad")
REFERENCE = ("zoo",)
BAKEOFF_TAG = "bakeoff-astra"
PUBLISHED = "published.yaml"
# `thread-delta` marks a resumed turn re-metered after it was billed twice; `last` a running thread total
PUBLISHABLE_USAGE = ("sum", "rollout")

# Design-ladder order (docs/design-ladder.md). Prove pair, the fast pair, then the remaining corpus.
LADDER = (
    "bracket",
    "benchy",
    "bearing-housing",
    "enclosure-base",
    "coupon",
    "nasa-backstep-driver-seegmiller",
    "chiral-keyplate",
    "nasa-atb-axisymmetric-bump",
    "spleen-c1-blade",
    "nist-amb2022-01-bridge",
    "nist-amb2022-01-bridge-mesh",
    "nist-am-test-artifact",
    "rpi5-enclosure",
    "gear-pair",
    "fusion-01184-recon",
    "fusion-13786-recon",
    "fusion-12944-recon",
    "fusion-15317-recon",
    "fusion-16418-recon",
    "fusion-01184-assembly",
    "fusion-13786-assembly",
    "fusion-12944-assembly",
    "fusion-15317-assembly",
    "fusion-16418-assembly",
    "prusa-mini-extruder-front",
    "voron-sb-duct",
)

ASSEMBLY_CASES = (
    "fusion-01184-assembly",
    "fusion-13786-assembly",
    "fusion-12944-assembly",
    "fusion-15317-assembly",
    "fusion-16418-assembly",
)

# part → (truth case id, arm id). coupon/bracket/benchy have no reconstruction case.
TRUTH_CASE: dict[str, tuple[str, str]] = {
    "bearing-housing": ("bearing-housing", "spec-and-views"),
    "enclosure-base": ("enclosure-base", "spec-and-views"),
    "nasa-backstep-driver-seegmiller": ("nasa-backstep-driver-seegmiller", "text-only"),
    "chiral-keyplate": ("chiral-keyplate", "text-only"),
    "nasa-atb-axisymmetric-bump": ("nasa-atb-axisymmetric-bump", "text-and-points"),
    "spleen-c1-blade": ("spleen-c1-blade", "table-and-notes"),
    "nist-amb2022-01-bridge": ("nist-amb2022-01-bridge", "drawing-only"),
    "nist-amb2022-01-bridge-mesh": ("nist-amb2022-01-bridge", "mesh-input"),
    "nist-am-test-artifact": ("nist-am-test-artifact", "drawing-renders-sheet"),
    "rpi5-enclosure": ("rpi5-enclosure", "requirements"),
    "gear-pair": ("gear-pair", "spec-only"),
    "fusion-01184-recon": ("fusion-01184-recon", "renders-and-sheet"),
    "fusion-13786-recon": ("fusion-13786-recon", "renders-and-sheet"),
    "fusion-12944-recon": ("fusion-12944-recon", "renders-and-sheet"),
    "fusion-15317-recon": ("fusion-15317-recon", "renders-and-sheet"),
    "fusion-16418-recon": ("fusion-16418-recon", "renders-and-sheet"),
    "prusa-mini-extruder-front": ("prusa-mini-extruder-front", "renders-and-sheet"),
    "voron-sb-duct": ("voron-sb-duct", "renders-sections-sheet"),
}

ECR_LABELS: dict[str, list[str]] = {
    "rpi5-enclosure": ["ecr1", "ecr2", "ecr3", "ecr4"],
    "prusa-mini-extruder-front": ["ecr1"],
    "voron-sb-duct": ["ecr1"],
}


def design_names() -> list[str]:
    names = []
    for p in sorted(DESIGNS.iterdir()):
        if not p.is_dir() or p.name.startswith("_") or p.name.startswith("."):
            continue
        if (p / "contract.yaml").exists():
            names.append(p.name)
    return sorted([*names, *(d for d in membership() if (design_dir(d) / "contract.yaml").exists())])


def ladder_parts(parts: list[str] | None = None) -> list[str]:
    known = set(parts if parts is not None else [*design_names(), *ASSEMBLY_CASES])
    ordered = [p for p in LADDER if p in known]
    extra = [p for p in sorted(known) if p not in LADDER]
    return ordered + extra


def gate_path(backend: str, part: str) -> Path:
    return results_dir(part, backend=backend) / "gate_feedback.json"


def blockout_ok(backend: str, part: str) -> bool:
    p = results_dir(part, backend=backend) / "blockout.json"
    if not p.exists():
        return False
    try:
        return bool(json.loads(p.read_text()).get("ok"))
    except json.JSONDecodeError:
        return False


def assembly_scorecard(backend: str, part: str) -> Path:
    return results_dir(part, backend=backend) / "scorecard.json"


def cell(backend: str, part: str) -> dict[str, Any]:
    if part in ASSEMBLY_CASES:
        p = assembly_scorecard(backend, part)
        if not p.exists():
            return {"backend": backend, "part": part, "status": "pending", "ok": False}
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"backend": backend, "part": part, "status": "error", "ok": False}
        ok = data.get("verdict") == "PASS" and bool(data.get("ok", True))
        return {
            "backend": backend,
            "part": part,
            "status": "pass" if ok else "fail",
            "ok": ok,
            "mode": data.get("mode"),
            "verdict": data.get("verdict"),
        }
    gf = gate_path(backend, part)
    if not gf.exists():
        return {
            "backend": backend,
            "part": part,
            "status": "blockout-ok" if blockout_ok(backend, part) else "pending",
            "ok": False,
        }
    try:
        data = json.loads(gf.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"backend": backend, "part": part, "status": "error", "ok": False}
    ok = bool(data.get("ok"))
    return {
        "backend": backend,
        "part": part,
        "status": "pass" if ok else "fail",
        "ok": ok,
        "gates": data.get("summary") or data.get("passed"),
    }


def status(backends: tuple[str, ...] | None = None, parts: list[str] | None = None) -> list[dict[str, Any]]:
    backends = backends or CANDIDATES + REFERENCE
    parts = ladder_parts(parts)
    return [cell(b, p) for p in parts for b in backends]


def next_cell(backends: tuple[str, ...] | None = None, parts: list[str] | None = None) -> dict[str, Any] | None:
    """First unfinished cell, design-major then backend-major over LADDER."""
    backends = backends or CANDIDATES
    for p in ladder_parts(parts):
        for b in backends:
            c = cell(b, p)
            if not c["ok"]:
                return c
    return None


def next_rung(backends: tuple[str, ...] | None = None, parts: list[str] | None = None) -> dict[str, Any] | None:
    """First design that is not pass on every candidate backend, with all three commands."""
    backends = backends or CANDIDATES
    for p in ladder_parts(parts):
        cells = [cell(b, p) for b in backends]
        if any(not c["ok"] for c in cells):
            return {
                "part": p,
                "cells": cells,
                "commands": [run_argv(c["backend"], p) for c in cells if not c["ok"]],
            }
    return None


def _astra(argv: list[str]) -> list[str]:
    return [*argv, "--worker", "codex", "--tag", BAKEOFF_TAG]


def run_argv(backend: str, part: str) -> list[str]:
    """Command the orchestrator should run for this cell (truth run, or blockout then drive).

    Every cell is authored by the Codex Astra worker. The child must also see
    OPENCAD_CODEX_NO_FALLBACK=1 so an exhausted budget does not fall through to Cursor.
    """
    if part in ASSEMBLY_CASES:
        return _astra([
            "python", "-m", "opencad.truth", "assemble", part,
            "--backend", backend, "--parallel",
        ])
    if part in TRUTH_CASE:
        case, arm = TRUTH_CASE[part]
        return _astra([
            "python", "-m", "opencad.truth", "run", case, "--arm", arm,
            "--backend", backend, "--resume-from", "blockout", "--no-decompose",
            "--parallel",
        ])
    if not blockout_ok(backend, part) and not gate_path(backend, part).exists():
        return _astra(["python", "-m", "opencad", "blockout", part, "--backend", backend])
    return _astra(["python", "-m", "opencad", "drive", part, "--backend", backend, "--parallel"])


def scorecard_status(part: str, backend: str) -> str:
    spec = TRUTH_CASE.get(part)
    if spec is None:
        return "—"
    case, arm = spec
    p = case_dir(case) / "scorecards" / f"{arm}@{backend}-latest.json"
    if not p.exists():
        return "pending"
    try:
        card = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "error"
    verdict = card.get("verdict") or "unknown"
    s = card.get("summary") or {}
    if s.get("required_total"):
        return f"{verdict} {s.get('required_pass', 0)}/{s['required_total']}"
    return str(verdict)


def ecr_status(part: str, backend: str) -> str:
    labels = ECR_LABELS.get(part)
    if not labels:
        return "—"
    bits = []
    for label in labels:
        p = results_dir(part, backend=backend) / "ecr" / label / "ecr.json"
        if not p.exists():
            bits.append(f"{label}:pending")
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            bits.append(f"{label}:error")
            continue
        bits.append(f"{label}:{'pass' if data.get('ok') else 'fail'}")
    return " ".join(bits)


def _blank(value: Any) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def cell_tag(backend: str, part: str) -> str:
    """A re-run cell's own tag from `_bakeoff/cell-tags.json` (`{"<backend>/<part>": "<tag>"}`), else the campaign tag."""
    path = RESULTS_BASE / "_bakeoff" / "cell-tags.json"
    tags = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return tags.get(f"{backend}/{part}", BAKEOFF_TAG)


def cell_meter(backend: str, part: str, tag: str = BAKEOFF_TAG) -> dict[str, Any]:
    """Token, dollar, and time totals for one backend cell, filtered to the bake-off tag."""
    from opencad.telemetry import read

    path = results_dir(part, backend=backend) / "telemetry.jsonl"
    rows = [r for r in read(path) if r.get("tag") == tag] if path.exists() else []
    turns = [r for r in rows if r.get("kind") == "turn"]
    stages = [r for r in rows if r.get("kind") == "stage"]
    cost: dict[str, Any] = {}
    cost_path = results_dir(part, backend=backend) / "cost.json"
    if cost_path.exists():
        try:
            loaded = json.loads(cost_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            loaded = {}
        if isinstance(loaded, dict) and loaded.get("tag") in (tag, None, ""):
            cost = loaded
    usds = [float(r["usd"]) for r in turns if r.get("usd") is not None]
    worker_s = round(sum(float(r.get("seconds") or 0) for r in turns))
    eval_s = round(sum(float(r.get("seconds") or 0) for r in stages))
    present = bool(turns or stages)
    return {
        "turns": len(turns),
        "model": ",".join(sorted({str(r.get("model")) for r in turns if r.get("model")})) or "—",
        "fallbacks": sum(1 for r in turns if r.get("fallback_from")),
        "tokens_input": sum(int(r.get("tokens_input") or 0) for r in turns),
        "tokens_cached": sum(int(r.get("tokens_cached") or 0) for r in turns),
        "tokens_output": sum(int(r.get("tokens_output") or 0) for r in turns),
        "tokens_reasoning": sum(int(r.get("tokens_reasoning") or 0) for r in turns),
        "codex_usd": round(sum(usds), 4) if usds else None,
        "price_reason": next((r.get("price_reason") for r in turns if r.get("price_reason")), None),
        "zoo_credits": cost.get("zoo_credits_delta"),
        "zoo_usd": cost.get("zoo_monetary_delta"),
        "engine_usd": cost.get("engine_usd"),
        "worker_s": worker_s if present else None,
        "evaluator_s": eval_s if present else None,
        "wall_s": (worker_s + eval_s) if present else None,
        "usage_modes": sorted({str(r.get("usage_mode")) for r in turns if r.get("usage_mode")}),
    }


def _orchestrator_line() -> str:
    path = RESULTS_BASE / "_bakeoff" / "orchestrator.json"
    if not path.exists():
        return "Orchestrator (Grok) wall time is not recorded for this report and is excluded from CAD cost."
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "Orchestrator (Grok) record is unreadable and is excluded from CAD cost."
    return f"Orchestrator (Grok): {_blank(data.get('seconds'))} s, excluded from CAD cost."


def write_report(path: Path | None = None) -> Path:
    path = path or (RESULTS_BASE / "_bakeoff" / "report.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    parts = ladder_parts()
    backends = list(CANDIDATES + REFERENCE)
    rows = status(tuple(backends), parts)
    by = {(r["backend"], r["part"]): r for r in rows}
    lines = [
        "# CAD bake-off",
        "",
        "Per-backend gate verdicts. `pass` means `gate_feedback.json` has `ok: true`.",
        "Rows follow the design ladder. Scorecards are `truth/cases/<case>/scorecards/<arm>@<backend>-latest.json`.",
        "",
        "| part | " + " | ".join(backends) + " |",
        "|" + "---|" * (len(backends) + 1),
    ]
    for part in parts:
        cells = [by.get((b, part), {"status": "pending"})["status"] for b in backends]
        lines.append("| " + part + " | " + " | ".join(cells) + " |")
    lines += ["", "## Scorecards", "", "| part | arm | " + " | ".join(backends) + " |", "|" + "---|" * (len(backends) + 2)]
    for part in parts:
        spec = TRUTH_CASE.get(part)
        arm = spec[1] if spec else "—"
        cells = [scorecard_status(part, b) for b in backends]
        lines.append("| " + part + " | " + arm + " | " + " | ".join(cells) + " |")
    lines += ["", "## ECR", "", "| part | " + " | ".join(backends) + " |", "|" + "---|" * (len(backends) + 1)]
    for part in parts:
        if part not in ECR_LABELS:
            continue
        cells = [ecr_status(part, b) for b in backends]
        lines.append("| " + part + " | " + " | ".join(cells) + " |")
    if not any(p in ECR_LABELS for p in parts):
        lines.append("| — | " + " | ".join("—" for _ in backends) + " |")
    lines += [
        "",
        "## Assemblies",
        "",
        "Modelled cells (local backends import the two dataset STEPs and export a 2-solid STEP). Zoo is the frozen placement-only reference.",
        "",
        "| case | " + " | ".join(backends) + " |",
        "|" + "---|" * (len(backends) + 1),
    ]
    for part in ASSEMBLY_CASES:
        cells = []
        for b in backends:
            c = cell(b, part)
            mode = "placement" if b == "zoo" else (c.get("mode") or "modelled")
            if c["status"] == "pending":
                cells.append("pending")
            else:
                n = ""
                if isinstance(c.get("verdict"), str):
                    n = " PASS" if c["ok"] else " FAIL"
                cells.append(f"{c['status']}{n} ({mode})" if n else f"{c['status']} ({mode})")
        lines.append("| " + part + " | " + " | ".join(cells) + " |")
    lines += [
        "",
        "## Cost and time",
        "",
        f"Token totals, USD, and seconds are filtered to tag `{BAKEOFF_TAG}`; a re-run cell uses its own tag from `_bakeoff/cell-tags.json`, listed below the table.",
        "Codex USD uses the pinned fast-tier card. Zoo USD is the monetary balance delta; zoo credits is the prepaid balance drop.",
        "A non-zero fallback means a CAD turn left Astra for the Cursor worker.",
        _orchestrator_line(),
        "",
        "| part | backend | model | fallbacks | tokens in | cached | out | reasoning | codex USD | zoo credits | zoo USD | worker seconds | evaluator seconds | wall seconds |",
        "|" + "---|" * 14,
    ]
    fallback_notes = []
    retagged = []
    last_mode = False
    for part in parts:
        for backend in backends:
            tag = cell_tag(backend, part)
            if tag != BAKEOFF_TAG:
                retagged.append(f"{backend}/{part} `{tag}`")
            meter = cell_meter(backend, part, tag=tag)
            if meter["fallbacks"]:
                fallback_notes.append(f"{backend}/{part} fallbacks={meter['fallbacks']}")
            if "last" in meter["usage_modes"]:
                last_mode = True
            lines.append("| " + " | ".join([
                part, backend, meter["model"], _blank(meter["fallbacks"] if meter["turns"] else None),
                _blank(meter["tokens_input"] if meter["turns"] else None),
                _blank(meter["tokens_cached"] if meter["turns"] else None),
                _blank(meter["tokens_output"] if meter["turns"] else None),
                _blank(meter["tokens_reasoning"] if meter["turns"] else None),
                _blank(meter["codex_usd"] if meter["codex_usd"] is not None else meter["price_reason"]),
                _blank(meter["zoo_credits"]), _blank(meter["zoo_usd"]),
                _blank(meter["worker_s"]), _blank(meter["evaluator_s"]), _blank(meter["wall_s"]),
            ]) + " |")
    if retagged:
        lines += ["", "Re-run cells: " + "; ".join(retagged) + "."]
    if last_mode:
        lines.append("")
        lines.append("Usage mode `last`: a Codex exec reported a running thread total, so that exec was billed from its last turn.completed only.")
    if fallback_notes:
        lines += ["", "Readiness: FAIL — " + "; ".join(fallback_notes)]
    else:
        lines += ["", "Readiness: no tagged fallbacks. A cell is confirmed when its row shows gpt-6-astra, tokens, seconds, and a USD figure or an explicit null."]
    rung = next_rung()
    if rung:
        cmds = "; ".join(" ".join(c) for c in rung["commands"])
        lines += ["", f"Next rung: `{rung['part']}` — {cmds}"]
    else:
        lines += ["", "Next: campaign complete."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    publish_entries(path.parent / PUBLISHED, parts)
    return path


def _tagged_turns(backend: str, part: str, tag: str) -> list[dict[str, Any]]:
    from opencad.telemetry import read

    path = results_dir(part, backend=backend) / "telemetry.jsonl"
    return [r for r in read(path) if r.get("kind") == "turn" and r.get("tag") == tag] if path.exists() else []


def publishable_cell(backend: str, part: str) -> dict[str, Any] | None:
    """One backend's snapshot for the published log, or None when it is not a clean comparison: no gate verdict, no Astra turns
    on its tag, a fallback, or any turn billed outside PUBLISHABLE_USAGE."""
    gf = gate_path(backend, part)
    tag = cell_tag(backend, part)
    turns = _tagged_turns(backend, part, tag)
    if not gf.exists() or not turns:
        return None
    if any(r.get("model") != "gpt-6-astra" or r.get("fallback_from") or r.get("usage_mode") not in PUBLISHABLE_USAGE for r in turns):
        return None
    fb = json.loads(gf.read_text(encoding="utf-8"))
    gates = fb.get("gates") or []
    meter = cell_meter(backend, part, tag=tag)
    return {
        "tag": tag,
        "date": max(str(r.get("ts") or "") for r in turns)[:10],
        "verdict": "PASS" if fb.get("ok") else "FAIL",
        "passed": len(fb.get("passed") or []),
        "failed": len(fb.get("failed") or []),
        "not_applicable": len(fb.get("not_applicable") or []),
        "failed_gates": [g["id"] for g in gates if g.get("ok") is False],
        **{k: meter[k] for k in ("turns", "tokens_input", "tokens_cached", "tokens_output", "codex_usd", "zoo_credits", "zoo_usd",
                                 "worker_s", "evaluator_s", "wall_s")},
    }


def _note(cells: dict[str, dict[str, Any]]) -> str:
    fails = {b: c["failed_gates"] for b, c in cells.items()}
    if not any(fails.values()):
        return f"All {len(cells)} backends pass every applicable gate."
    sets = {tuple(v) for v in fails.values()}
    if len(sets) == 1:
        return "Every backend fails " + ", ".join(f"`{g}`" for g in next(iter(sets))) + "."
    return "; ".join(f"{b} fails " + ", ".join(f"`{g}`" for g in v) if v else f"{b} passes" for b, v in fails.items()) + "."


def publish_entries(path: Path, parts: list[str] | None = None) -> list[dict[str, Any]]:
    """Append each part whose four backends are clean comparisons (`publishable_cell`) to the published log, once per set of
    cell tags. Earlier entries are never rewritten, so a later re-meter does not change what was published."""
    data = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.exists() else {}
    entries: list[dict[str, Any]] = list(data.get("entries") or [])
    seen = {(e["part"], tuple(sorted((e.get("tags") or {}).items()))) for e in entries}
    backends = (*CANDIDATES, *REFERENCE)
    added = []
    for part in ladder_parts(parts):
        cells = {b: publishable_cell(b, part) for b in backends}
        if any(c is None for c in cells.values()):
            continue
        tags = {b: c.pop("tag") for b, c in cells.items()}
        if (part, tuple(sorted(tags.items()))) in seen:
            continue
        added.append({"part": part, "date": max(c.pop("date") for c in cells.values()), "tags": tags, "note": _note(cells), "backends": cells})
    if added:
        entries += sorted(added, key=lambda e: e["date"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump({"entries": entries}, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return added

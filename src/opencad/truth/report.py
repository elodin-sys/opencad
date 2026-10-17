"""docs/validation-envelope.md from registry, manifests, attempts and scorecards."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from opencad.io import utc_now
from opencad.paths import DOCS, TRUTH
from opencad.truth.manifest import CLASS_MEANING, case_dir, load_manifest, load_registry


def _latest(case_id: str, arm: str) -> dict[str, Any] | None:
    from opencad.backends.registry import current_id

    p = case_dir(case_id) / "scorecards" / f"{arm}@{current_id()}-latest.json"
    return json.loads(p.read_text()) if p.exists() else None


def build() -> Path:
    reg = load_registry()
    from opencad.backends.registry import current_id

    lines = ["# Validation envelope", "", f"Generated {utc_now()} by `python -m opencad.truth report`. Modelling backend: `{current_id()}`. Every verdict below is a CAD-reconstruction "
             "verdict: agreement between the exported geometry and the pinned truth, by truth class. Nothing here is physical or engineering validation, "
             "and downstream targets (flow, distortion) are recorded, not scored.", "", "## Truth classes", ""]
    for k, v in CLASS_MEANING.items():
        lines.append(f"- **{k}** — {v}")
    lines += ["", "## Cases", "", "| case | class | role | arm | backend | attempts | scored | passes | latest verdict | required checks | failed checks |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    detail: list[str] = []
    for entry in reg.get("cases", []):
        cid = entry["id"]
        if not (case_dir(cid) / "manifest.yaml").exists():  # sequestered by a live run
            lines.append(f"| {cid} | sequestered (live run) |" + " - |" * 9)
            continue
        m = load_manifest(cid)
        ap = case_dir(cid) / "attempts.yaml"
        attempts = yaml.safe_load(ap.read_text()).get("attempts", []) if ap.exists() else []
        for arm in m.arms:
            arm_attempts = [a for a in attempts if a.get("arm") == arm.id]
            scored = [a for a in arm_attempts if a.get("scorecard")]
            passes = [a for a in scored if a["scorecard"]["verdict"] == "PASS"]
            card = _latest(cid, arm.id)
            verdict = card["verdict"] if card else "not scored"
            req = f"{card['summary']['required_pass']}/{card['summary']['required_total']}" if card else "-"
            failed = ", ".join(c["id"] for c in card["checks"] if not c.get("ok")) if card else "-"
            be = (arm_attempts[-1].get("backend") if arm_attempts else None) or current_id()
            lines.append(f"| {cid} | {m.truth_class} | {m.role} | {arm.id} | {be} | {len(arm_attempts)} | {len(scored)} | {len(passes)} | {verdict} | {req} | {failed or '-'} |")
            detail.append(f"### {cid} — {arm.id}\n")
            detail.append(f"{m.title}. Source: {m.source.citation} (accessed {m.source.accessed}{', ' + m.source.revision if m.source.revision else ''}).\n")
            if card:
                detail.append("| check | kind | required | verdict | measured | expected / band |\n|---|---|---|---|---|---|")
                for c in card["checks"]:
                    meas = c.get("measured", c.get("checks", c.get("found", "")))
                    exp = c.get("expected", c.get("expected_area", c.get("band", "")))
                    detail.append(f"| {c['id']} | {c['kind']} | {'yes' if c['required'] else 'no'} | {'PASS' if c.get('ok') else 'FAIL'} | {_short(meas)} | {_short(exp)} |")
                detail.append("")
                detail.append(f"Pipeline gates: {card['pipeline_gates']}. STEP sha256 `{card['hash_binding']['step_sha256'][:16]}`; manifest `{card['hash_binding']['manifest_sha256'][:16]}`.\n")
            if m.downstream_targets:
                detail.append("Downstream targets (not scored by CAD): " + "; ".join(f"{t.name} = {t.value}{' ± ' + str(t.uncertainty) if t.uncertainty else ''} {t.units} ({t.note})" for t in m.downstream_targets) + "\n")
            if arm_attempts:
                detail.append("Attempts: " + "; ".join(f"{a.get('started', '?')[:16]} reached {a.get('stage_reached')}" + (f", scorecard {a['scorecard']['verdict']}" if a.get('scorecard') else "") + (f", error: {a['error'][:80]}" if a.get('error') else "") for a in arm_attempts) + "\n")
    lines += ["", *detail]
    lines += _machine_section(reg)
    lines += _assembly_section()
    lines += _reliability_section(reg)
    cl = TRUTH / "calibration-log.yaml"
    if cl.exists():
        log = yaml.safe_load(cl.read_text()) or {}
        lines += ["## Calibration log", ""]
        for e in log.get("entries", []):
            lines.append(f"- {e.get('date')} [{e.get('case', 'pipeline')}] {e.get('change')} — {e.get('reason')}")
    DOCS.mkdir(exist_ok=True)
    out = DOCS / "validation-envelope.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


ENVELOPE_JSON = "validation-envelope.json"


def _solver_of(design: str, obs_id: str) -> str | None:
    """The solver a machine contract names for an observable (older scorecards do not carry it); `evaluator` when no simulation predicts it."""
    from opencad.contract import ContractError, load_assembly
    from opencad.paths import design_dir

    try:
        a = load_assembly(design_dir(design))
    except ContractError:
        return None
    o = next((o for o in a.observables if o.id == obs_id), None)
    if o is None:
        return None
    return next((s.solver for s in a.simulations if s.id == o.simulation), None) if o.simulation else "evaluator"


def machine_rows(reg: dict[str, Any]) -> list[dict[str, Any]]:
    """Every performance row of every machine case's latest scorecard, with its solver and relative error."""
    out = []
    for entry in reg.get("cases", []):
        cid = entry["id"]
        if not (case_dir(cid) / "manifest.yaml").exists():
            continue
        m = load_manifest(cid)
        if m.kind != "machine":
            continue
        for arm in m.arms:
            card = _latest(cid, arm.id)
            for c in (card or {}).get("performance") or []:
                pred, ref = c.get("prediction"), c.get("reference")
                out.append({**c, "machine": cid, "arm": arm.id, "machine_verdict": card["verdict"], "scored_at": card.get("scored_at"),
                            "solver": c.get("solver") or _solver_of(arm.design, c["id"]) or "unknown",
                            "relative_error": (pred - ref) / ref if pred is not None and ref else None})
    return out


def envelope(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per solver and quantity over the scored predictions (development and held-out): points, machines, signed mean and spread of the
    relative error, the worst z, how many passed, and how many were resolved by a mesh ladder. A new machine's report quotes these."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in rows:
        if r.get("status") in ("scored", "unresolved"):
            groups.setdefault((r["solver"], r["quantity"]), []).append(r)
    out = []
    for (solver, quantity), rs in sorted(groups.items()):
        rel = [r["relative_error"] for r in rs if r.get("relative_error") is not None]
        zs = [r.get("z", r.get("z_rms")) for r in rs if r.get("z", r.get("z_rms")) is not None]
        out.append({"solver": solver, "quantity": quantity, "points": len(rs), "development": sum(1 for r in rs if r.get("split") == "development"),
                    "held_out": sum(1 for r in rs if r.get("split") == "held_out"), "machines": sorted({r["machine"] for r in rs}),
                    "evidence": sorted({r["evidence"] for r in rs}), "bias": float(np.mean(rel)) if rel else None,
                    "spread": float(np.std(rel)) if len(rel) > 1 else None, "max_abs_error": float(np.max(np.abs(rel))) if rel else None,
                    "max_z": float(max(zs)) if zs else None, "passed": sum(1 for r in rs if r.get("ok") is True),
                    "failed": sum(1 for r in rs if r.get("ok") is False), "unresolved": sum(1 for r in rs if r.get("status") == "unresolved"),
                    "resolved": sum(1 for r in rs if r.get("resolved") is True), "no_mesh_estimate": sum(1 for r in rs if r.get("resolved") is None)})
    return out


def _pct(x: float | None, sign: str = "+") -> str:
    return f"{100 * x:{sign}.1f} %" if x is not None else "-"


def _num(x: float | None) -> str:
    return f"{x:.4g}" if isinstance(x, (int, float)) else "-"


def _machine_section(reg: dict[str, Any]) -> list[str]:
    """Machine cases row by row, then the validation envelope per solver and quantity (also written to docs/validation-envelope.json)."""
    rows = machine_rows(reg)
    if not rows:
        return []
    env = envelope(rows)
    DOCS.mkdir(exist_ok=True)
    (DOCS / ENVELOPE_JSON).write_text(json.dumps({"generated": utc_now(), "envelope": env, "rows": rows}, indent=2, default=str) + "\n", encoding="utf-8")
    lines = ["", "## Machines: predictions against measurements", "",
             "Latest scorecard per machine case. `unresolved` predictions are not supported by their mesh ladder: they are reported, never passed.", "",
             "| machine | observable | quantity | op. case | split | solver | prediction | reference | rel. error | z | mesh-resolved | verdict |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        verdict = "unresolved" if r.get("status") == "unresolved" else {True: "PASS", False: "FAIL"}.get(r.get("ok"), r.get("status"))
        resolved = {True: "yes", False: "no"}.get(r.get("resolved"), "-")
        lines.append(f"| {r['machine']} | {r['id']} | {r['quantity']} | {r.get('case') or '-'} | {r.get('split')} | {r['solver']} | {_num(r.get('prediction'))} | "
                     f"{_num(r.get('reference'))} | {_pct(r.get('relative_error'))} | {_num(r.get('z', r.get('z_rms')))} | {resolved} | {verdict} |")
    lines += ["", "## Validation envelope per solver and quantity", "",
              (f"What a machine without truth data can quote for a prediction (`docs/{ENVELOPE_JSON}`): the relative error pred/ref - 1 over every scored "
               "point, its mean (bias) and spread, and how many points a mesh ladder resolved. A quantity or solver absent here is unvalidated."), "",
              "| solver | quantity | points (dev / held-out) | machines | bias | spread | max abs error | max z | pass / fail / unresolved | mesh-resolved |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for e in env:
        ladder = f"{e['resolved']} of {e['points']}" + (f" ({e['no_mesh_estimate']} without a ladder)" if e["no_mesh_estimate"] else "")
        lines.append(f"| {e['solver']} | {e['quantity']} | {e['points']} ({e['development']} / {e['held_out']}) | {', '.join(e['machines'])} | {_pct(e['bias'])} | "
                     f"{_pct(e['spread'], '')} | {_pct(e['max_abs_error'], '')} | {_num(e['max_z'])} | {e['passed']} / {e['failed']} / {e['unresolved']} | {ladder} |")
    return lines


def _assembly_section() -> list[str]:
    """Held-out assembly tasks (task.yaml cases): latest scorecard per backend, reported as-is (pipeline frozen, no tuning)."""
    backends = ("cadquery", "build123d", "freecad", "zoo")
    cases = [tp.parent.name for tp in sorted((TRUTH / "cases").glob("*/task.yaml"))]
    if not cases:
        return []
    header = "| case | " + " | ".join(backends) + " | visual |"
    sep = "|" + "---|" * (len(backends) + 2)
    rows = []
    for cid in cases:
        cells = []
        links = []
        for be in backends:
            card_p = TRUTH / "cases" / cid / "scorecards" / f"assembly@{be}-latest.json"
            if not card_p.exists() and be == "zoo":
                card_p = TRUTH / "cases" / cid / "scorecards" / "assembly-latest.json"
            if not card_p.exists():
                cells.append("not run")
                continue
            card = json.loads(card_p.read_text())
            mode = card.get("mode") or ("placement" if be == "zoo" else "modelled")
            failed = ", ".join(k for k, v in (card.get("checks") or {}).items() if "ok" in v and not v["ok"])
            cells.append(f"{card.get('verdict')} ({mode})" + (f" {failed}" if failed else ""))
            viz = card.get("viz") or {}
            if viz.get("html"):
                links.append(f"[{be}](../results/{be}/{cid}/handoff/assembly.html)")
        rows.append("| " + cid + " | " + " | ".join(cells) + " | " + (" ".join(links) or "-") + " |")
    return [
        "",
        "## Held-out assembly tasks",
        "",
        "Fusion 360 Gallery joint sets. Local backends run **modelled** mode (import the two dataset STEPs, place them, export a 2-solid STEP); "
        "Zoo is the frozen **placement** reference. Scored on axis alignment, axial offset, interference and contact (`truth/assembly_task.py`); "
        "reported as-is, never tuned. `truth assembly-check` is the worker's local critic. Every scored attempt writes a GLB with the joint "
        "animated and a model-viewer page (`results/<backend>/<case>/handoff/assembly.html`).",
        "",
        header,
        sep,
        *rows,
    ]


def _reliability_section(reg: dict[str, Any]) -> list[str]:
    """Reliability (hosted runs, first/final success) and effort (Codex time, engine calls, tool failures) per arm."""
    from opencad.truth.effort import effort_for_design, reliability_for_arm

    from opencad import telemetry

    lines = ["", "## Reliability and effort", "",
             "Hosted runs only; score-only re-judgements are excluded. `first` is the first hosted attempt's scorecard, `final` the latest scored one. "
             "Effort comes from the latest `results/<design>` stage JSONs (worker seconds/commands across plan, model, retry and blockout; engine-call ledger rows; "
             "transient/timeout rows as tool failures) and from `results/<design>/telemetry.jsonl` (worker wall by role, backends, over-budget turns, evaluator wall). "
             "Human interventions are 0 by construction for `truth run`.", "",
             "| case | arm | hosted runs | first PASS | final PASS | pipeline retries | mean s/run | worker s | worker cmds | engine calls | tool failures | blockout iters | worker s by role | backends | over-budget turns | evaluator s |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for entry in reg.get("cases", []):
        cid = entry["id"]
        if not (case_dir(cid) / "manifest.yaml").exists():  # sequestered by a live run
            lines.append(f"| {cid} | sequestered (live run) |" + " - |" * 14)
            continue
        m = load_manifest(cid)
        ap = case_dir(cid) / "attempts.yaml"
        attempts = yaml.safe_load(ap.read_text()).get("attempts", []) if ap.exists() else []
        for arm in m.arms:
            r = reliability_for_arm([a for a in attempts if a.get("arm") == arm.id])
            e = effort_for_design(arm.design)
            t = telemetry.design_summary(arm.design)
            by_role = ", ".join(f"{k} {v}" for k, v in t["worker_s_by_role"].items()) or "-"
            lines.append(f"| {cid} | {arm.id} | {r['hosted_runs']} | {'yes' if r['first_run_pass'] else 'no'} | {'yes' if r['final_pass'] else 'no'} | {r['pipeline_retries']} | "
                         f"{r['mean_seconds'] if r['mean_seconds'] is not None else '-'} | {e['codex_seconds']} | {e['codex_commands']} | {e['engine_calls']} | {e['tool_failures']} | {e['blockout_iterations'] if e['blockout_iterations'] is not None else '-'} | "
                         f"{by_role} | {', '.join(t['backends']) or '-'} | {t['over_budget_turns']} | {t['evaluator_s']} |")
    lines.append("")
    return lines


def _short(v: Any) -> str:
    s = json.dumps(v, default=str) if not isinstance(v, str) else v
    s = s.replace("|", "\\|")
    return s if len(s) <= 120 else s[:117] + "..."

"""Machine cases (manifest `kind: machine`): sequester truth, stage the arm's inputs as an assembly draft request, drive the
assembly pipeline (drafts, part lanes, assemble, evaluator stages, simulations), then score the assembled STEP against the
manifest's geometry observables and the simulations against its performance references. Truth stays vaulted for the whole
foreground run; worker turns are awaited on their done files (EVENT#k lines)."""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any

from opencad.io import dump_json, load_json, provenance, sha256_file, sha256_tree, utc_now
from opencad.paths import ASSEMBLY_FILE, DESIGNS, NESTED, design_dir, part_dir, results_dir
from opencad.truth import performance
from opencad.truth.manifest import CaseManifest, case_dir
from opencad.truth.runner import Sequester, case_file, case_lock, log_attempt, vault_path

MEASURED = ("transmission_ratio", "fluid_volume", "joint_value", "joint_range", "point_x", "point_y", "point_z")  # evaluator-measured from the placed geometry; no simulation predicts them


def checks_for_draft(m: CaseManifest) -> list[tuple[str, str]]:
    """What the drafter must declare (ids, quantities, cases), never the reference values."""
    return [("prediction", f"observable id `{p.id}`: {p.quantity}" + (f" [{p.unit}]" if p.unit else "") + (f" at operating case `{p.case}`" if p.case else "")
             + (f", {p.where}" if p.where else "")
             + (" (measured by the evaluator from the placed geometry: declare it with no `simulation`)" if p.quantity in MEASURED else ""))
            for p in m.performance if p.status == "available" and p.evidence != "X"]


def _reset(asm: str, be: str) -> None:
    from opencad.contract import load_assembly

    designs = []
    if (DESIGNS / asm / ASSEMBLY_FILE).exists():
        designs = load_assembly(DESIGNS / asm).designs()
    for d in [*designs, asm]:  # parts first: they resolve under the assembly only while its assembly.yaml exists
        for p in (design_dir(d), DESIGNS / f".staging-{d}", DESIGNS / f".codex-draft-{d}", results_dir(d, backend=be), part_dir(d, backend=be)):
            if p.exists():
                shutil.rmtree(p)


def _attribute(perf: list[dict[str, Any]], design: str, sim: dict[str, Any]) -> None:
    """Name each scored row's solver and model (the validation envelope aggregates by solver and quantity); an observable no simulation
    predicts is an evaluator measurement."""
    from opencad.contract import ContractError, load_assembly

    try:
        declared = {s.id: s for s in load_assembly(DESIGNS / design).simulations}
    except ContractError:
        declared = {}
    for c in perf:
        sid = c.get("simulation") or ((sim.get("observables") or {}).get(c["id"]) or {}).get("simulation")
        s, ran = declared.get(sid), (sim.get("simulations") or {}).get(sid) or {}
        c["simulation"] = sid
        c["solver"] = s.solver if s else ("evaluator" if not sid else None)
        c["model"] = ran.get("model") or (s.solver if s else "measured from the placed geometry")


def score_machine(case_id: str, m: CaseManifest, arm_id: str, *, case_root: Path | None = None) -> dict[str, Any]:
    from opencad.backends.registry import current_id
    from opencad.truth import scorer

    arm = next(a for a in m.arms if a.id == arm_id)
    root = Path(case_root) if case_root else case_dir(case_id)
    be = current_id()
    rd = results_dir(arm.design, backend=be)
    step, stl = rd / "handoff" / f"{arm.design}.step", rd / "handoff" / f"{arm.design}.stl"
    geometry = scorer.score_checks(root, m, step, stl if stl.exists() else None) if step.exists() and m.observables else []
    sim = load_json(rd / "simulate.json") if (rd / "simulate.json").exists() else {}
    perf = performance.score(m.performance, sim.get("observables") or {}, root)
    _attribute(perf, arm.design, sim)
    fb = load_json(rd / "gate_feedback.json") if (rd / "gate_feedback.json").exists() else {}
    verdict = performance.verdict(geometry, perf) if step.exists() else "FAIL"
    card = {
        "case": case_id, "arm": arm_id, "design": arm.design, "kind": "machine", "mode": arm.mode, "backend": be, "truth_class": m.truth_class,
        "scored_at": utc_now(), "verdict": verdict, "error": None if step.exists() else f"no assembled handoff STEP at {step}",
        "accuracy_score": scorer.accuracy_score({"checks": geometry}, m) if geometry else None,
        "summary": {**scorer.summarize_checks(geometry), "performance_pass": sum(1 for c in perf if c.get("ok")),
                    "performance_scored": sum(1 for c in perf if c.get("status") in ("scored", "unresolved")),
                    "performance_unresolved": sum(1 for c in perf if c.get("status") == "unresolved"), "performance_total": len(perf),
                    "performance_by_split": performance.by_split(perf)},
        "checks": geometry, "performance": perf, "pipeline_gates": {"ok": fb.get("ok"), "summary": fb.get("summary"), "failed": fb.get("failed")},
        "simulations": {k: {"status": v.get("status"), "solver": v.get("solver"), "reason": v.get("reason") or v.get("error")}
                        for k, v in (sim.get("simulations") or {}).items()},
        "hash_binding": {"manifest_sha256": sha256_file(root / "manifest.yaml"), "truth_files": {t.path: t.sha256 for t in m.truth},
                         "input_files": {i.path: i.sha256 for i in m.inputs}, "step_sha256": sha256_file(step) if step.exists() else None,
                         "assembly_source": sha256_tree(part_dir(arm.design, backend=be), (".py",), exclude=NESTED) if part_dir(arm.design, backend=be).exists() else {},
                         "design_bundle": sha256_tree(design_dir(arm.design), exclude=NESTED) if design_dir(arm.design).exists() else {}},
        "provenance": provenance(),
    }
    stamp = card["scored_at"].replace(":", "").replace("-", "")
    with case_lock(case_id):
        out = case_file(case_id, "scorecards", tree=case_dir(case_id))
        out.mkdir(parents=True, exist_ok=True)
        dump_json(out / f"{arm_id}@{be}-{stamp}.json", card)
        dump_json(out / f"{arm_id}@{be}-latest.json", card)
    dump_json(rd / "scorecard.json", card)
    return card


def run_machine(case_id: str, m: CaseManifest, arm_id: str, *, force: bool = False, cont: bool = False, jobs: int = 4,
                allow_retry: bool = True, amend: str | None = None) -> dict[str, Any]:
    from opencad.assembly.draft import stage_request
    from opencad.assembly.pipeline import drive
    from opencad.backends.registry import current_id

    arm = next((a for a in m.arms if a.id == arm_id), None)
    if arm is None:
        raise KeyError(f"arm {arm_id} is not in the {case_id} manifest")
    be, asm = current_id(), arm.design
    if force and not cont:
        _reset(asm, be)
    t0 = time.time()
    entry: dict[str, Any] = {"started": utc_now(), "arm": arm_id, "design": asm, "backend": be, "kind": "machine", "mode": arm.mode}
    held = vault_path(case_id)
    seq = Sequester.attach(case_id, held) if cont and held.exists() else Sequester(case_id)
    with seq:
        entry["truth_sequestered_to"] = str(seq.dst)
        case = case_dir(case_id)
        if not (DESIGNS / asm / ASSEMBLY_FILE).exists() and not (DESIGNS / f".staging-{asm}" / ASSEMBLY_FILE).exists():
            images = [case / p for p in arm.images]
            stage_request(asm, m.intent, [case / p for p in arm.inputs if p not in arm.images], images, notes=arm.notes, checks=checks_for_draft(m))
        code = drive(asm, backend=be, jobs=jobs, allow_retry=allow_retry, amend=amend)
        entry["amended"] = bool(amend)
        rd = results_dir(asm, backend=be)
        fb = load_json(rd / "gate_feedback.json") if (rd / "gate_feedback.json").exists() else {}
        entry["stage_reached"] = "scored"
        entry["pipeline"] = {"code": code, "gates": {"pass": len(fb.get("passed") or []), "fail": len(fb.get("failed") or [])}, "failed": fb.get("failed")}
        card = score_machine(case_id, m, arm_id, case_root=Path(seq.dst))
    entry["scorecard"] = {"verdict": card["verdict"], "summary": card["summary"], "accuracy_score": card.get("accuracy_score"),
                          "failed": [c["id"] for c in card["checks"] + card["performance"] if c.get("ok") is False],
                          "unresolved": [c["id"] for c in card["performance"] if c.get("status") == "unresolved"]}
    entry["seconds"] = round(time.time() - t0)
    entry["finished"] = utc_now()
    log_attempt(case_id, entry)
    print(json.dumps(entry, indent=2, default=str), flush=True)
    return entry

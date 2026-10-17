"""ecr: an engineering change request against an existing part, with interface preservation.

`python -m opencad ecr <part> <request.md> [--contract-delta delta.yaml] [--label ecr1] [--expect-infeasible]`

1. Baseline: measure every pinned interface item (must_not_change interface checks) on the current STEP.
2. Revise the contract: apply the delta (entries replaced by name/id) into designs/<part>/ecr/<label>/contract.yaml;
   the original contract stays immutable.
3. Brief Codex on the model thread with the request, the revised acceptance items and the preserved set.
   An infeasible request must be refused under `## Result` with the KCL untouched.
4. Re-run verify -> export -> inspect -> edit -> gates against the revised contract into results/<part>/ecr/<label>/,
   then compare the preserved interface items with the baseline. One bounded retry on a tier-A or preservation failure.
"""

from __future__ import annotations

import copy
import shutil
from pathlib import Path
from typing import Any

import yaml

from opencad import gates as gates_mod, interfaces, worker
from opencad.backends.base import EngineError
from opencad.contract import ContractError, load_contract
from opencad.geomcheck import brep
from opencad.io import dump_json, load_json, sha256_tree, utc_now
from opencad.orchestrator import Ctx, PipelineError
from opencad.paths import part_dir
from opencad.schemas import PartContract
from opencad.worker import orders

KEYED = {"parameters": "name", "features": "id", "interfaces": "name"}
ACCEPT_KEYED = {"sections": "id", "faces": "name", "cylinders": "name", "planes": "name", "dimensions": "name",
                "solids": "name", "hardware": "name", "clearances": "name", "passages": "name", "thickness": "name", "probes": "name", "cylinder_counts": "name",
                "gears": "name", "meshes": "name"}


def load_request_and_delta(request_path: Path, delta_path: Path | None) -> tuple[str, dict[str, Any]]:
    """Read the request (and optional delta) before `ecr/<label>/` is wiped; those files often live inside it."""
    request = Path(request_path).read_text(encoding="utf-8")
    if not delta_path:
        return request, {}
    raw = yaml.safe_load(Path(delta_path).read_text(encoding="utf-8"))
    return request, raw or {}


def apply_delta(contract: dict[str, Any], delta: dict[str, Any]) -> tuple[dict[str, Any], set[str]]:
    """Replace-or-append list entries by their key; scalar/dict fields replace. Returns the revised dict and the changed acceptance item names."""
    out = copy.deepcopy(contract)
    changed: set[str] = set()
    for k, v in delta.items():
        if k in KEYED and isinstance(v, list):
            key = KEYED[k]
            existing = {e[key]: i for i, e in enumerate(out.get(k, []))}
            for e in v:
                if e.get("_remove"):
                    out[k] = [x for x in out.get(k, []) if x[key] != e[key]]
                    existing = {x[key]: i for i, x in enumerate(out[k])}
                elif e[key] in existing:
                    out[k][existing[e[key]]] = {**out[k][existing[e[key]]], **e}
                else:
                    out.setdefault(k, []).append(e)
        elif k == "acceptance" and isinstance(v, dict):
            acc = out.setdefault("acceptance", {})
            for ak, av in v.items():
                if ak in ACCEPT_KEYED and isinstance(av, list):
                    key = ACCEPT_KEYED[ak]
                    existing = {e[key]: i for i, e in enumerate(acc.get(ak, []))}
                    for e in av:
                        changed.add(e[key])
                        if e.get("_remove"):
                            acc[ak] = [x for x in acc.get(ak, []) if x[key] != e[key]]
                            existing = {x[key]: i for i, x in enumerate(acc[ak])}
                        elif e[key] in existing:
                            acc[ak][existing[e[key]]] = {**acc[ak][existing[e[key]]], **e}
                        else:
                            acc.setdefault(ak, []).append(e)
                else:
                    acc[ak] = av
        elif k == "open_questions" and isinstance(v, list):
            out["open_questions"] = list(out.get("open_questions", [])) + v
        else:
            out[k] = v
    return out, changed


measure_interfaces = interfaces.measure
compare_interfaces = interfaces.compare


def _item_lines(revised: PartContract, name: str) -> list[str]:
    """Every acceptance item of the revised contract called `name` (a face and a probe may share one), one line each; empty when the request removed it."""
    a = revised.acceptance
    out: list[str] = []
    for cy in a.cylinders:
        if cy.name == name:
            out.append(f"- cylinder {name}: {cy.kind}, radius {cy.r:g}, axis through {list(cy.point)} along {list(cy.direction)}" + (f", length {cy.length}" if cy.length else "") + f" {cy.description}")
    for f in a.faces:
        if f.name == name:
            out.append(f"- face {name}: plane {f.plane} = {f.at}, normal {f.normal}" + (f", area {f.area} (rel tol {f.area_tolerance_rel})" if f.area else "")
                       + (f", centre {list(f.center)} (tol {f.tolerance or 0.2})" if f.center else "") + (", mode sum" if f.mode == "sum" else ""))
    for pl in a.planes:
        if pl.name == name:
            out.append(f"- plane {name}: normal {list(pl.normal)} through {list(pl.point)}")
    for d in a.dimensions:
        if d.name == name:
            out.append(f"- dimension {name}: {d.expected} along {d.axis}" + (f" between {list(d.between)}" if d.between else ""))
    for s in a.sections:
        if s.id == name:
            out.append(f"- section {name}: plane {s.plane} = {s.at}, expect {s.expect.model_dump(exclude_none=True)} {s.description}")
    for p in a.probes:
        if p.name == name:
            out.append(f"- probe {name}: {p.state} at {[list(pt) for pt in p.points]} {p.description}")
    for cc in a.cylinder_counts:
        if cc.name == name:
            out.append(f"- cylinder count {name}: {cc.kind}, radius {cc.r:g} (tol {cc.radius_tolerance})" + (f" along {list(cc.direction)}" if cc.direction else "")
                       + (f", axis centre inside {[list(cc.region[0]), list(cc.region[1])]}" if cc.region else "")
                       + (f", exactly {cc.expected}" if cc.expected is not None else f", at least {cc.expected_min}") + f" {cc.description}")
    for so in a.solids:
        if so.name == name:
            out.append(f"- solid {name}: contains {list(so.contains_point)}" + (f", volume {so.volume.model_dump(exclude_none=True)}" if so.volume else "") + f" {so.description}")
    for kind in ("hardware", "clearances", "passages", "thickness", "gears", "meshes"):
        for x in getattr(a, kind):
            if x.name == name:
                out.append(f"- {kind} {name}: {x.model_dump(exclude_none=True, exclude={'name', 'description'})} {getattr(x, 'description', '')}")
    return out


def _edit_expect(p: Any) -> dict[str, Any] | None:
    return p.edit_test.expect.model_dump(exclude_none=True) if p.edit_test and p.edit_test.expect else None


def _param_line(p: Any, old: Any | None) -> str:
    line = f"- parameter {p.name}: {p.value} {p.unit} ({p.provenance}, tol {p.tolerance})"
    if p.edit_test:
        line += f"; edit_test delta {p.edit_test.delta} expects {_edit_expect(p) or {}}"
    if old is None:
        line += " [new]"
    else:
        was = ([f"{old.value} {old.unit}"] if (old.value, old.unit) != (p.value, p.unit) else []) + ([f"edit_test expected {_edit_expect(old)}"] if _edit_expect(old) != _edit_expect(p) else [])
        line += f" [was {'; '.join(was)}]" if was else " [revised]"
    return line + (f" {p.description}" if p.description else "")


def _feature_line(f: Any, tag: str) -> str:
    return f"- feature {f.id} [{tag}]: {f.kind}{f', count {f.count}' if f.count else ''}; {f.description} (params: {', '.join(f.parameters) or '-'})"


def _revision_lines(base: PartContract, revised: PartContract, changed: set[str]) -> tuple[list[str], list[str]]:
    """(changed lines, removed lines): parameters, features and interfaces by diff against the base contract; acceptance items by the delta's names.

    Removed items are described from the base contract so the worker knows which geometry to delete.
    """
    lines: list[str] = []
    removed: list[str] = []
    old = {p.name: p for p in base.parameters}
    for p in revised.parameters:
        if p.name not in old or p.model_dump() != old[p.name].model_dump():
            lines.append(_param_line(p, old.get(p.name)))
    removed += [f"- parameter {n}: {old[n].value} {old[n].unit} {old[n].description}" for n in old if n not in {p.name for p in revised.parameters}]
    old_f = {f.id: f for f in base.features}
    for f in revised.features:
        if f.id not in old_f or f.model_dump() != old_f[f.id].model_dump():
            lines.append(_feature_line(f, "new" if f.id not in old_f else "revised"))
    removed += [_feature_line(old_f[i], "removed") for i in old_f if i not in {f.id for f in revised.features}]
    old_i = {i.name: i for i in base.interfaces}
    for i in revised.interfaces:
        if i.name not in old_i or i.model_dump() != old_i[i.name].model_dump():
            lines.append(f"- interface {i.name} [{'new' if i.name not in old_i else 'revised'}]: checks {i.checks}{'' if i.must_not_change else ' (not pinned)'}; {i.description}")
    removed += [f"- interface {n}: checks {old_i[n].checks}; {old_i[n].description}" for n in old_i if n not in {i.name for i in revised.interfaces}]
    for name in sorted(changed):
        item = _item_lines(revised, name)
        if item:
            lines += item
        else:
            removed += _item_lines(base, name) or [f"- {name}"]
    return lines, removed


def brief(ctx: Ctx, request: str, revised: PartContract, changed: set[str], baseline: dict[str, dict[str, Any]], label: str) -> str:
    preserved = [n for n in baseline if n not in changed]
    lines = [
        f"Engineering change request `{label}` for part `{ctx.name}`. The current `{ctx.entry}` passed its gates; modify it in place.",
        "", "## Request", request.strip(), "",
        "## Revised contract (only the items below changed; everything else is as before)",
    ]
    revision, removed = _revision_lines(ctx.contract, revised, changed)
    lines += revision
    if revised.acceptance.volume:
        lines.append(f"- acceptance volume: {revised.acceptance.volume.expected} (tol {revised.acceptance.volume.tolerance or ''}{' rel ' + str(revised.acceptance.volume.tolerance_rel) if revised.acceptance.volume.tolerance_rel else ''})")
    lines.append(f"- envelope: min {list(revised.envelope.min)} max {list(revised.envelope.max)}")
    if removed:
        lines += ["", "## Removed by this request (no longer in the revised contract: delete the geometry they described; nothing about them is preserved)"] + removed
    lines += ["", "## Interfaces that must be preserved exactly (re-measured on the exported STEP against this baseline)"]
    for name in preserved:
        b = baseline[name]
        sig = {k: v for k, v in b.items() if k not in ("kind", "ok")}
        lines.append(f"- {b['kind']} {name}: {sig}")
    lines += [
        "", "## Rules",
        "- Change only what the request needs. Do not scale, shift or enlarge the whole part; the preserved items above are checked to their contract tolerances after the edit.",
        "- Keep every contract parameter as a top-level literal constant; add new parameters for new values (they are listed in the revised contract).",
        f"- If the request conflicts with a preserved interface or with the part's own geometry, DO NOT edit `{ctx.backend.language.entry}`. Write `INFEASIBLE` as the first word under `## Result` and state the specific conflict with numbers. A silently distorted model fails; an explicit refusal of an impossible request passes.",
        "- Otherwise verify as before (format, lint, analyze, snapshots, STEP/STL export, watertight STL) and report measured vs expected under `## Verification`, including the analytic volume delta.",
        ctx.backend.language.rules(),
    ]
    return "\n".join(lines)


def _run_stages(ctx: Ctx) -> dict[str, Any]:
    import time

    from opencad import telemetry
    from opencad.stages import edit, export, inspect_stage, verify

    ctx.results_dir.mkdir(parents=True, exist_ok=True)
    out: dict[str, Any] = {}
    for name, fn in (("verify", verify.run), ("export", export.run), ("inspect", inspect_stage.run), ("edit", edit.run)):
        t0 = time.time()
        try:
            out[name] = fn(ctx)
        except (PipelineError, EngineError) as e:
            out[name] = {"ok": False, "error": str(e)[:2000], "class": getattr(e, "kind", None)}
            ctx.write_stage(name, out[name])
        telemetry.record("stage", ctx.name, telemetry.stage_data(name, time.time() - t0, out[name].get("ok"), (ctx.load_stage(name) or {}).get("engine_calls")),
                         results_dir=ctx.results_dir.parent.parent)
        if not out[name].get("ok") and "error" in out[name]:
            break
    fb = gates_mod.evaluate(ctx)
    dump_json(ctx.results_dir / "gate_feedback.json", fb)
    telemetry.record("gates", ctx.name, {**telemetry.gates_data(fb), "ecr": ctx.results_dir.name}, results_dir=ctx.results_dir.parent.parent)
    out["gates"] = fb
    return out


def run(part: str, request_path: Path, *, delta_path: Path | None = None, label: str = "ecr1", expect_infeasible: bool = False,
        timeout: float | None = None, allow_retry: bool = True, cont: bool = False) -> dict[str, Any]:
    """`cont=True` continues a request interrupted by a worker handback: the baseline, revised contract and finished stages are reused."""
    base_ctx = Ctx.load(part, timeout=timeout)
    mdl = base_ctx.load_stage("model") or {}
    thread = mdl.get("thread_id") or None
    if not thread:
        print(f"ecr {label}: {part} has no recorded worker thread; the worker starts fresh from the earlier turn reports", flush=True)
    if not base_ctx.entry.exists():
        raise PipelineError(f"{base_ctx.entry} missing")
    step = base_ctx.results_dir / "handoff" / f"{part}.step"
    if not step.exists():
        step = Path((base_ctx.load_stage("export") or {}).get("files", {}).get("step", {}).get("path", ""))
    if not step.exists():
        raise PipelineError("no exported STEP to baseline against")
    pf = base_ctx.backend.engine.preflight()
    if not pf.get("ok") and pf.get("class") == "billing":
        from opencad.backends.base import BillingError

        raise BillingError(pf.get("error") or "backend preflight failed")

    key = f"ecr-{label}"
    ecr_design = base_ctx.design_dir / "ecr" / label
    ecr_results = base_ctx.results_dir / "ecr" / label
    partial_path = ecr_results / "ecr.json"
    resumed = cont and partial_path.exists() and (load_json(partial_path) or {}).get("phase") in ("worker", "stages-done")
    if resumed:
        data: dict[str, Any] = load_json(partial_path)
        request = (ecr_design / "request.md").read_text(encoding="utf-8")
        delta = data.get("delta") or {}
        changed = set(data.get("changed_items") or [])
        baseline = data["baseline"]["interfaces"]
        kcl_before = data["baseline"]["kcl"]
        try:
            revised = load_contract(ecr_design / "contract.yaml")
        except ContractError as e:
            raise PipelineError(f"revised contract invalid: {e}") from e
    else:
        request, delta = load_request_and_delta(request_path, delta_path)
        orders.supersede(base_ctx.results_dir, key)
        for d in (ecr_design, ecr_results):
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True)
        (ecr_design / "request.md").write_text(request, encoding="utf-8")
        raw = yaml.safe_load(base_ctx.contract_path.read_text(encoding="utf-8"))
        revised_raw, changed = apply_delta(raw, delta or {})
        (ecr_design / "contract.yaml").write_text(yaml.safe_dump(revised_raw, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
        (ecr_design / "delta.yaml").write_text(yaml.safe_dump(delta or {}, sort_keys=False, allow_unicode=True), encoding="utf-8")
        try:
            revised = load_contract(ecr_design / "contract.yaml")
        except ContractError as e:
            raise PipelineError(f"revised contract invalid: {e}") from e
        for sub in ("reference", "sources"):  # provenance sources and reference ingests resolve relative to the revised contract's directory
            if (base_ctx.design_dir / sub).exists():
                shutil.copytree(base_ctx.design_dir / sub, ecr_design / sub)
        shutil.copy2(base_ctx.design_dir / "brief.md", ecr_design / "brief.md")

        # baseline against the *original* contract's pinned items (the preserved set is defined pre-change)
        shape = brep.read_step(step)
        a = brep.analyze_step(step)
        baseline = measure_interfaces(shape, base_ctx.contract, a["bbox_size"], step_path=step)
        kcl_before = sha256_tree(part_dir(part), tuple(base_ctx.backend.language.suffixes))
        data = {"label": label, "request": str(request_path), "delta": delta, "changed_items": sorted(changed), "expect_infeasible": expect_infeasible,
                "baseline": {"step": str(step), "interfaces": baseline, "kcl": kcl_before, "volume": a["volume"], "bbox_size": a["bbox_size"]},
                "started": utc_now(), "thread_id": thread, "phase": "worker"}
        dump_json(partial_path, data)

    ctx = Ctx(part, ecr_design, ecr_design / "contract.yaml", revised, ecr_results, part_dir(part), timeout or 3600, base_ctx.backend_id)
    msg = brief(base_ctx, request, revised, changed, baseline, label)
    (ecr_results / "brief.md").write_text(msg, encoding="utf-8")
    r = worker.dispatch(msg, role="ecr", key=key, results_dir=base_ctx.results_dir, part=part, cd=part_dir(part), run_dir=ecr_results / "codex",
                        resume=thread, timeout=timeout, deliverables=[ctx.entry], context={"contract": str(ctx.contract_path)})
    data["worker"] = data["codex"] = r.summary()
    data["codex_report"] = r.sections
    kcl_after = sha256_tree(part_dir(part), tuple(ctx.backend.language.suffixes))
    # stage records for the gates: the plan is the base design's, the model session is this request's turn on the same thread
    base_plan = base_ctx.load_stage("plan") or {}
    ctx.write_stage("plan", {"ok": True, "ecr": label, "inherited_from": str(base_ctx.results_dir / "plan.json"), "base_plan_ok": base_plan.get("ok"), "request": request[:2000]})
    ctx.write_stage("model", {"ok": r.ok, "ecr": label, "thread_id": r.thread_id or thread, "worker": r.summary(), "codex": r.summary(), "codex_report": r.sections, "kcl": str(ctx.entry),
                              "kcl_before": kcl_before, "kcl_after": kcl_after})
    result_text = (r.sections.get("Result") or r.result_md or "").strip()
    refused = result_text.upper().startswith("INFEASIBLE") or "INFEASIBLE" in result_text.upper()[:200]
    modified = kcl_after != kcl_before
    data.update({"refused": refused, "kcl_modified": modified})

    if refused and not modified:
        data["outcome"] = "refused"
        data["ok"] = expect_infeasible
        data["verdict_note"] = "explicit refusal of an infeasible request" if expect_infeasible else "refused a request the contract considered feasible"
        return _finish(ctx, data)
    if refused and modified:
        data.update({"outcome": "inconsistent", "ok": False, "verdict_note": "reported INFEASIBLE but changed the KCL"})
        return _finish(ctx, data)
    if expect_infeasible:
        data.update({"outcome": "silent-distortion" if modified else "no-op", "ok": False,
                     "verdict_note": "an infeasible request must be refused explicitly; the model was " + ("changed" if modified else "left unchanged without a refusal")})
        return _finish(ctx, data)

    fb_path = ctx.results_dir / "gate_feedback.json"
    if data.get("phase") == "stages-done" and data.get("preservation") and fb_path.exists():
        stages = {"gates": load_json(fb_path)}  # continued after the correction handback: the pre-correction measurements are already on disk
    else:
        stages = _run_stages(ctx)
        data["stages"] = {k: (v.get("ok") if isinstance(v, dict) else None) for k, v in stages.items() if k != "gates"}
        data["gates"] = {k: stages["gates"][k] for k in ("ok", "summary", "failed", "retryable_failed")}
        after = _after_interfaces(ctx, revised)
        data["preservation"] = compare_interfaces(baseline, after, revised, changed) if after is not None else {"ok": False, "error": "no STEP after the change"}
        data["phase"] = "stages-done"
        dump_json(partial_path, data)
    if allow_retry and (stages["gates"]["retryable_failed"] or not data["preservation"]["ok"]) and (ctx.results_dir / "inspect.json").exists():
        corr = gates_mod.correction_message(ctx, stages["gates"])
        bad = [f"- preserved {n} ({row['kind']}) moved: {({k: v for k, v in row.items() if k not in ('kind', 'changed_by_request', 'ok')})}" for n, row in data["preservation"].get("items", {}).items() if not row["ok"]]
        if bad:
            corr += "\nInterface preservation failures (these must return to their baseline values):\n" + "\n".join(bad)
        r2 = worker.dispatch(corr, role="correction", key=f"{key}-retry", results_dir=base_ctx.results_dir, part=part, cd=part_dir(part), run_dir=ecr_results / "codex-retry",
                             resume=r.thread_id or thread, timeout=timeout, deliverables=[ctx.entry], context={"contract": str(ctx.contract_path)})
        data["retry"] = {"worker": r2.summary(), "codex": r2.summary(), "codex_report": r2.sections, "correction": corr}
        for n in ("verify.json", "export.json", "inspect.json", "edit.json", "gate_feedback.json"):
            (ctx.results_dir / n).unlink(missing_ok=True)
        ctx.clean_stage_outputs("snapshots", "export")
        stages = _run_stages(ctx)
        data["stages"] = {k: (v.get("ok") if isinstance(v, dict) else None) for k, v in stages.items() if k != "gates"}
        data["gates"] = {k: stages["gates"][k] for k in ("ok", "summary", "failed", "retryable_failed")}
        after = _after_interfaces(ctx, revised)
        data["preservation"] = compare_interfaces(baseline, after, revised, changed) if after is not None else {"ok": False, "error": "no STEP after the change"}
    if (ctx.load_stage("export") or {}).get("ok"):  # determinism re-export, GLB and snapshots after the correction decision
        from opencad.stages import export as export_mod
        from opencad.stages import verify as verify_mod

        export_mod.finalize(ctx)
        verify_mod.render_snapshots(ctx)
        stages["gates"] = gates_mod.evaluate(ctx)
        dump_json(ctx.results_dir / "gate_feedback.json", stages["gates"])
        data["gates"] = {k: stages["gates"][k] for k in ("ok", "summary", "failed", "retryable_failed")}
    data["outcome"] = "applied"
    data["ok"] = bool(stages["gates"]["ok"] and data["preservation"]["ok"])
    # the handoff is what the scorer measures; it is written whatever the gates say (ok is a claim, the scorecard the verdict)
    handoff = ctx.results_dir / "handoff"
    handoff.mkdir(exist_ok=True)
    for fmt in ("step", "stl", "glb"):
        src = ctx.results_dir / "export" / f"{part}.{fmt}"
        if src.exists():
            shutil.copy2(src, handoff / f"{part}.{fmt}")
    if ctx.entry.exists():
        shutil.copy2(ctx.entry, ctx.results_dir / ctx.backend.language.entry)
    return _finish(ctx, data)


def _after_interfaces(ctx: Ctx, revised: PartContract) -> dict[str, dict[str, Any]] | None:
    exp = ctx.load_stage("export") or {}
    p = Path(exp.get("files", {}).get("step", {}).get("path", ""))
    if not p.exists():
        return None
    shape = brep.read_step(p)
    a = brep.analyze_step(p)
    return measure_interfaces(shape, revised, a["bbox_size"], step_path=p)


def _finish(ctx: Ctx, data: dict[str, Any]) -> dict[str, Any]:
    data.pop("phase", None)
    data["finished"] = utc_now()
    data["kcl_after"] = sha256_tree(part_dir(ctx.name), tuple(ctx.backend.language.suffixes))
    dump_json(ctx.results_dir / "ecr.json", data)
    print(f"ecr {data['label']} {'ok' if data.get('ok') else 'FAILED'}: outcome={data.get('outcome')} refused={data.get('refused')} modified={data.get('kcl_modified')}"
          + (f" gates={data['gates']['summary']} preservation={data['preservation'].get('ok')}" if data.get("gates") else "") + f" ({data.get('verdict_note', '')})")
    return data

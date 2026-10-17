"""The 12 tiered gates. Tier A: design/interpretation. Tier B: model consistency. Tier C: artifact truth.

Every gate reads stage JSONs only; `ok: true` in a stage is a claim that the gate re-checks.
"""

from __future__ import annotations

import json
import re
from typing import Any

from opencad.backends.base import MEMORY_PHRASE, is_program
from opencad.orchestrator import Ctx
from opencad.paths import DESIGNS, REPO_ROOT, design_dir, results_dir, results_root
from opencad.schemas import PartContract

TIERS = {"A": "design feasibility / interpretation: fix the contract or the model", "B": "model consistency: reconcile before trusting the part", "C": "artifact truth: fix inputs or generation; never auto-fixed"}


def _g(id_: str, tier: str, title: str, ok: bool | None, evidence: list[str], failure_means: str, knob: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"id": id_, "tier": tier, "title": title, "ok": ok, "evidence": evidence, "failure_means": failure_means, "knob": knob, "details": details or {}}


def traced_geometry_note(size: dict[str, Any]) -> str:
    return (f"the source embeds traced geometry ({size.get('lines')} lines, {size.get('numeric_literals')} numeric literals; limits "
            f"{size.get('max_lines')}/{size.get('max_literals')}): state dimensions as parameters, never point lists")


def mesh_watertight(mesh_: dict[str, Any], solid_count: int) -> bool:
    """One body: the STL must be watertight. Several bodies: each shell must be closed; touching bodies may share edges in the combined mesh."""
    if mesh_.get("watertight"):
        return True
    return solid_count > 1 and bool(mesh_.get("solids_watertight"))


def evaluate(ctx: Ctx) -> dict[str, Any]:
    c = ctx.contract
    ver = ctx.load_stage("verify") or {}
    exp = ctx.load_stage("export") or {}
    ins = ctx.load_stage("inspect") or {}
    edt = ctx.load_stage("edit") or {}
    mdl = ctx.load_stage("model") or {}
    pln = ctx.load_stage("plan") or {}
    gates: list[dict[str, Any]] = []
    be = getattr(ctx, "backend_id", "zoo")
    R = f"results/{be}/{results_dir(ctx.name, backend=be).relative_to(results_root(be)).as_posix()}"
    D = f"designs/{design_dir(ctx.name).relative_to(DESIGNS).as_posix()}"

    # 1 contract provenance (A): sources resolve to bundle files, no blocking questions, interfaces enforceable
    prov = c.provenance_summary()
    soft = prov.get("inferred", 0) + prov.get("defaulted", 0)
    pv = provenance_checks(ctx)
    ok1 = not pv["unresolved_sources"] and not pv["blocking_questions"] and not (c.release_status == "prototype" and pv["unenforced_interfaces"])
    gates.append(_g("contract_provenance", "A", "Contract validates; stated/measured sources resolve to bundle files; no blocking open questions; interfaces pinned by checks", ok1,
                    [f"{D}/contract.yaml: {len(c.parameters)} parameters {prov}; sources unresolved {pv['unresolved_sources']}; unanchored {len(pv['unanchored_sources'])}",
                     f"open questions: {len(c.open_questions)} (blocking {pv['blocking_questions']}); interfaces {len(c.interfaces)}, unenforced {pv['unenforced_interfaces']} (fails only for release_status prototype)"],
                    "the contract is not a usable specification", "re-run /initialize-cad with better sources, or resolve the blocking question",
                    {"provenance": prov, "soft_values": soft, "open_questions": c.open_questions, **pv}))

    # 2 envelope (A): the STEP measured by OpenCascade is authoritative; the engine bbox is disclosed
    ib, vb = ins.get("bbox", {}), ver.get("bbox", {})
    engine_note = "" if vb.get("ok") is not False else " (engine bbox differs: engine analyze can include cut-tool extents; disclosed, not gating)"
    if (ver.get("engine") or {}).get("status") == "missing":
        engine_note = f" (engine volume missing ({(ver.get('engine') or {}).get('class')}); disclosed, not gating)"
    gates.append(_g("envelope", "A", "Bounding box of the exported STEP equals the contract envelope", bool(ib.get("ok")) if ins else None,
                    [f"{R}/inspect.json bbox.max_error = {ib.get('max_error')} (tol {ib.get('tolerance')})", f"{R}/verify.json engine bbox.max_error = {vb.get('max_error')}{engine_note}"],
                     "the part is the wrong size, position, or orientation", "fix the frame/parameters in the model (worker correction) or a mis-read dimension in the contract",
                    {"inspect": ib, "engine": vb}))

    # 3 mass properties (A)
    mp = [ins.get(k, {}) for k in ("volume", "surface_area", "center_of_mass")]
    gates.append(_g("mass_properties", "A", "Volume, surface area and centre of mass within contract tolerance (independent STEP measurement)",
                    all(x.get("ok", False) for x in mp) if ins else None,
                    [f"{R}/inspect.json volume = {ins.get('volume', {}).get('measured')} vs {ins.get('volume', {}).get('expected')}",
                     f"{R}/inspect.json surface_area = {ins.get('surface_area', {}).get('measured')} vs {ins.get('surface_area', {}).get('expected')}",
                     f"{R}/inspect.json center_of_mass = {ins.get('center_of_mass', {}).get('measured')} vs {ins.get('center_of_mass', {}).get('expected')}"],
                    "material is missing or extra somewhere, or a feature is mis-placed", "worker correction with the measured deltas; or a wrong analytic expectation in the contract",
                    {k: ins.get(k) for k in ("volume", "surface_area", "center_of_mass")}))

    # 4 features (A)
    feats = ins.get("features", {})
    req_fail = [k for k, v in feats.items() if not v["optional"] and v["ok"] is False]
    opt_fail = [k for k, v in feats.items() if v["optional"] and v["ok"] is False]
    unverified = [k for k, v in feats.items() if not v["verified"]]
    secs, faces = ins.get("sections", {}), ins.get("faces", {})
    sec_fail = [k for k, v in secs.items() if not v["ok"]]
    face_fail = [k for k, v in faces.items() if not v["ok"]]
    cyl_fail = [k for k, v in (ins.get("cylinders") or {}).items() if not v["ok"]]
    plane_fail = [k for k, v in (ins.get("planes") or {}).items() if not v["ok"]]
    dim_fail = [k for k, v in (ins.get("dimensions") or {}).items() if not v["ok"]]
    multi_fail = {k: [n for n, v in (ins.get(k) or {}).items() if not v.get("ok")] for k in ("solids", "clearances", "passages", "thickness", "probes", "cylinder_counts", "gears", "meshes")}
    geo_fail = sec_fail + face_fail + cyl_fail + plane_fail + dim_fail + [n for v in multi_fail.values() for n in v]
    # older inspect.json without the key is not a failure (fixtures); a present table is gated
    sym_tbl = ins.get("symmetry")
    sym_fail = [k for k, v in (sym_tbl or {}).items() if not v.get("ok")] if sym_tbl is not None else []
    ev4 = [f"{R}/inspect.json features: {len(feats) - len(req_fail) - len(opt_fail)}/{len(feats)} ok; failed required {req_fail}; failed optional {opt_fail}; unverified {unverified}",
           f"sections failed {sec_fail}; faces failed {face_fail}; cylinders failed {cyl_fail}; planes failed {plane_fail}; dimensions failed {dim_fail}",
           "multi-body/interior failed: " + ", ".join(f"{k} {v}" for k, v in multi_fail.items() if v) if any(multi_fail.values()) else "multi-body/interior checks: all ok or none declared"]
    if sym_tbl is not None:
        ev4 += [symmetry_line(n, sym_tbl[n]) for n in (sym_fail or sym_tbl)]
    ref_sil = ((ver.get("snapshots") or {}).get("reference_silhouette")) if isinstance(ver.get("snapshots"), dict) else None
    if ref_sil:  # evidence only: input render vs part silhouette per view, framing-normalized
        ev4.append(f"{R}/verify.json snapshots.reference_silhouette (IoU vs input renders, evidence) = {ref_sil}; sheet snapshots/view-compare.png")
    gates.append(_g("features", "A", "Every required feature, section, named face, cylinder axis, plane, dimension, body, clearance, passage, wall, gear and symmetry check verified on the STEP", (not req_fail and not geo_fail and not sym_fail) if ins else None,
                    ev4,
                    "a hole, wall, cavity, channel, face or declared mirror is missing or in the wrong place", "worker correction naming the failed feature and its probe evidence",
                    {"failed_required": req_fail, "failed_optional": opt_fail, "unverified": unverified, "sections_failed": sec_fail, "faces_failed": face_fail,
                     "cylinders_failed": cyl_fail, "planes_failed": plane_fail, "dimensions_failed": dim_fail, "multibody_failed": multi_fail,
                     "symmetry_failed": sym_fail,
                     "cylinders": {k: {kk: v.get(kk) for kk in ("found", "axis_offset", "axis_tolerance", "radius_error", "ok")} for k, v in (ins.get("cylinders") or {}).items()},
                     "interfaces": ins.get("interfaces")}))

    # 5 reference fidelity (A)
    dev = ins.get("deviation", {})
    if not ins:
        ok5 = None
    elif dev.get("reference") is None:
        ok5 = None if not dev.get("declared") else False
    else:
        ok5 = dev.get("ok") if dev.get("declared") else None
    ev5 = [f"{R}/inspect.json deviation.p95 = {dev.get('p95')} hausdorff = {dev.get('hausdorff_estimate')} silhouette_iou_min = {dev.get('silhouette_iou_min')}",
           f"declared band: {c.acceptance.deviation.model_dump() if c.acceptance.deviation else 'none'}"]
    if dev.get("bands"):
        worst_band = max(dev["bands"], key=lambda b: b["p95"])
        ev5.append(f"worst band {band_name(dev.get('axis') or 'z', worst_band)}: p95 {worst_band['p95']} ({_sides(worst_band)})" + (f"; signed map {dev['map']}" if dev.get("map") else ""))
    gates.append(_g("reference_fidelity", "A", "Deviation from the reference model within the contract band (when a reference exists)", ok5,
                    ev5,
                    "the reconstruction departs from the measured reference beyond the declared band", "compare silhouettes; fix the contract measurement or the model",
                    {"deviation": {k: v for k, v in dev.items() if k != 'reference'}, "not_applicable": ok5 is None}))

    # 6 export agreement (B)
    agr = ins.get("agreement", {})
    engine_class = agr.get("engine_class") or (ver.get("engine") or {}).get("class")
    if not ins:
        ok6 = None
        ev6 = [f"{R}/inspect.json missing"]
    elif is_program(engine_class):
        ok6 = False
        ev6 = [f"{R}/inspect.json agreement: program-class verify failure; engine volume missing ({engine_class}); step={agr.get('step')} stl={agr.get('stl')}"]
    elif agr.get("engine_missing"):
        ok6 = agr.get("ok")
        ev6 = [f"engine volume missing ({engine_class or 'unknown'}); STL vs STEP rel={agr.get('stl_vs_step_rel')} (engine_vs_step_rel=None)"]
    else:
        ok6 = agr.get("ok")
        vol = agr.get("engine", agr.get("kcl"))
        ev6 = [f"{R}/inspect.json agreement engine={vol} step={agr.get('step')} stl={agr.get('stl')} (rel tol {agr.get('tolerance_rel')}; independent={agr.get('engine_independent')})"]
    if agr.get("manifold") is not None:
        ev6.append(f"{R}/inspect.json agreement.manifold = {agr.get('manifold')} (Manifold kernel witness, rel vs STEP {agr.get('manifold_vs_step_rel')}; disclosed, not gated)")
    elif ins:
        ev6.append("no kernel-independent witness (manifold3d not installed); STL volume is OCCT tessellation measured by trimesh")
    gates.append(_g("export_agreement", "B", "Engine, STEP (OpenCascade) and STL (trimesh) volumes agree", ok6,
                    ev6,
                    "the exported files do not represent the modelled solid", "re-export; report an exchange failure if persistent", agr))

    # 7 edit robustness (B)
    gates.append(_g("edit_robustness", "B", "Declared parameter edits rebuild with the expected effect, undriven interfaces stay put, sweeps regenerate, infeasible values are refused; baseline re-export hash unchanged",
                    (bool(edt.get("ok")) and edt.get("declared", 0) > 0) if edt else None,
                    [f"{R}/edit.json {sum(1 for t in edt.get('tests', []) if t.get('ok'))}/{len(edt.get('tests', []))} edit tests ok; restore.ok = {edt.get('restore', {}).get('ok')}",
                     f"sweep {edt.get('sweep_passed', 0)}/{edt.get('sweep_values', 0)} values; infeasible refused {edt.get('infeasible_refused', 0)}/{edt.get('infeasible_declared', 0)}; interfaces pinned {edt.get('interfaces_pinned', 0)}"],
                    "the model is not parametric in the contract's terms, an edit moved an interface it does not own, an impossible value built silently, or the deliverable changed",
                    "make features derive from the named constants; guard impossible values with asserts",
                    {"tests": [{k: t.get(k) for k in ('parameter', 'delta', 'ok', 'checks', 'error', 'sweep', 'infeasible')} for t in edt.get("tests", [])], "restore": edt.get("restore"),
                     "sweep": {"values": edt.get("sweep_values", 0), "passed": edt.get("sweep_passed", 0)}, "infeasible": {"declared": edt.get("infeasible_declared", 0), "refused": edt.get("infeasible_refused", 0)}}))

    # 8 source hygiene (B)
    hyg = ver.get("hygiene", {})
    unused = hyg.get("unused_parameters") or {}
    unused_ev = f" unused={unused}" if unused else ""
    dialect = hyg.get("dialect_ok", hyg.get("kcl_version_2"))
    unit = hyg.get("unit_ok", hyg.get("default_unit_mm"))
    legacy = hyg.get("legacy", hyg.get("legacy_v1"))
    gates.append(_g("source_hygiene", "B", "Dialect, units, formatted, lint-clean, named parameters match the contract, asserts present",
                    bool(hyg.get("ok")) and bool(ver.get("format", {}).get("ok")) and bool(ver.get("lint", {}).get("ok")) and hyg.get("asserts", 0) >= 1 if ver else None,
                    [f"{R}/verify.json hygiene: dialect={dialect} unit={unit} legacy={legacy} params_ok={hyg.get('parameters_ok')} asserts={hyg.get('asserts')}{unused_ev}",
                     f"format ok={ver.get('format', {}).get('ok')} lint ok={ver.get('lint', {}).get('ok')}"],
                    "the source is not maintainable as the contract's parametric program", "worker correction: rename constants, add asserts, format",
                    {"hygiene": hyg, "format": ver.get("format"), "lint": ver.get("lint")}))

    # 9 export integrity (C)
    step = exp.get("files", {}).get("step", {})
    mesh_ = ins.get("mesh") or {}
    voids = mesh_.get("void_shells") or 0
    mesh_ok = not mesh_ or (mesh_watertight(mesh_, c.acceptance.solid_count) and (mesh_.get("components", 0) - voids) == c.acceptance.solid_count)
    stl = exp.get("files", {}).get("stl")
    # determinism is checked by export.finalize after the retry decision: None = pending (not a failure), False = fails
    ok9 = None if not exp else bool(step.get("deterministic") is not False and step and stl and ins.get("valid") and ins.get("solid_count", {}).get("ok") and mesh_ok)
    gates.append(_g("export_integrity", "C", "Deterministic STEP (two exports identical), valid B-rep, expected solid count, watertight STL (solid shells == solids)", ok9,
                    [f"{R}/export.json step.deterministic = {step.get('deterministic') if step.get('deterministic') is not None else 'pending (finalize)'} sha256 {str(step.get('sha256', ''))[:12]}; stl={'present' if stl else 'missing'}; glb={'present' if exp.get('files', {}).get('glb') else 'optional/missing'}", f"{R}/inspect.json valid = {ins.get('valid')} solids = {ins.get('solid_count', {}).get('measured')} (expected {c.acceptance.solid_count})",
                     f"{R}/inspect.json mesh watertight = {mesh_.get('watertight')} components = {mesh_.get('components')} void_shells = {voids}",
                     f"kernel: evaluator OpenCascade, engine_independent = {agr.get('engine_independent')}; manifold witness = {mesh_.get('manifold_volume')}"],
                    "the exchange files are not trustworthy deliverables", "fix the model topology; never ship a non-deterministic or invalid export",
                    {"export": exp.get("files"), "valid": ins.get("valid"), "solid_count": ins.get("solid_count"), "mesh": mesh_}))

    # 10 traceability (C)
    stages_present = {s: (ctx.load_stage(s) is not None) for s in ("plan", "model", "verify", "export", "inspect", "edit")}
    allow_errors = any("--allow-errors" in e.get("cmd", "") for st in (ver, exp, ins, edt) for e in st.get("engine_calls", []))
    provs = [st.get("provenance", {}) for st in (mdl, ver, exp, ins, edt) if st]
    versions = {p.get("engine_version") or p.get("zoo_version") for p in provs}
    ok10 = bool(all(stages_present.values()) and mdl.get("thread_id") and not allow_errors and len(versions) == 1 and all(p.get("git", {}).get("head") for p in provs))
    engine_total = sum(len(st.get("engine_calls", [])) for st in (ver, exp, ins, edt, mdl, pln))
    gates.append(_g("traceability", "C", "Every stage JSON present with tool versions, git head, worker thread ids, engine-call ledger; no --allow-errors", ok10,
                    [f"stages present: {stages_present}", f"model thread {mdl.get('thread_id')}; engine versions {sorted(v for v in versions if v)}; engine calls {engine_total}; allow-errors used: {allow_errors}"],
                    "a headline number cannot be traced to evidence", "re-run the missing stage; never hand-edit stage JSONs",
                    {"stages_present": stages_present, "engine_calls_total": engine_total, "allow_errors": allow_errors, "engine_versions": sorted(v for v in versions if v), "zoo_versions": sorted(v for v in versions if v)}))

    # 11 evidence separation (C)
    ok11 = bool(ins) and ("volume" in ins) and ("deviation" in ins) and c.release_status in ("training-only", "reconstruction", "prototype")
    gates.append(_g("evidence_separation", "C", "Contract agreement, reference agreement and physical validation are reported as separate verdicts", ok11 if ins else None,
                    [f"{R}/inspect.json carries contract checks (volume/bbox/features) and a separate deviation block (reference = {dev.get('reference')})", f"release_status = {c.release_status}; physical validation: not performed"],
                    "a CAD match is being presented as engineering or experimental validation", "keep verdict categories separate in the report",
                    {"release_status": c.release_status, "physical_validation": "not performed"}))

    # 12 independence (C)
    ops = hyg.get("construction_ops") or {}
    if isinstance(ops, dict):
        sketches = ops.get("sketch_blocks", hyg.get("sketch_blocks", 0))
        features = ops.get("feature_ops", hyg.get("feature_ops", 0))
    else:
        sketches = hyg.get("sketch_blocks", 0)
        features = hyg.get("feature_ops", 0)
    size = hyg.get("source_size") or {}
    size_ok = size.get("ok", True)
    ok12 = bool(ver) and not hyg.get("forbidden_imports") and sketches >= 1 and features >= 1 and size_ok
    ev12 = [f"{R}/verify.json hygiene.forbidden_imports = {hyg.get('forbidden_imports')} construction_ops = {ops or {'sketch_blocks': sketches, 'feature_ops': features}} lines = {hyg.get('lines')}"]
    if not size_ok:
        ev12.append(f"{R}/verify.json hygiene.source_size: {traced_geometry_note(size)}")
    gates.append(_g("independence", "C", "The source is editable construction: no import of reference geometry, construction ops present, no traced geometry", ok12 if ver else None,
                    ev12,
                    "the deliverable is a re-export or a trace of the reference, not a design", "rebuild from construction with dimensions as parameters; the reference is for scoring only",
                    {"imports": hyg.get("imports"), "construction_ops": ops or {"sketch_blocks": sketches, "feature_ops": features}, "sketch_blocks": sketches, "feature_ops": features,
                     "source_size": size or None}))

    failed = [g["id"] for g in gates if g["ok"] is False]
    na = [g["id"] for g in gates if g["ok"] is None]
    passed = [g["id"] for g in gates if g["ok"] is True]
    tierA_failed = [g["id"] for g in gates if g["ok"] is False and g["tier"] == "A"]
    retryable = list(tierA_failed)
    by_id = {g["id"]: g for g in gates}
    agr = ins.get("agreement") or {}
    engine_class = agr.get("engine_class") or (ver.get("engine") or {}).get("class")
    if by_id.get("export_agreement", {}).get("ok") is False and engine_class == "ok":  # noqa: keep retryable only when the engine executed
        retryable.append("export_agreement")
    mesh_ = ins.get("mesh") or {}
    if (
        by_id.get("export_integrity", {}).get("ok") is False
        and ins.get("valid")
        and (ins.get("solid_count") or {}).get("ok")
        and mesh_
        and not mesh_.get("watertight")
    ):
        retryable.append("export_integrity")
    # an edit failure is model-attributable when the tooling worked (restore hash matched) and a declared test failed
    if by_id.get("edit_robustness", {}).get("ok") is False and edt.get("declared", 0) > 0 and (edt.get("restore") or {}).get("ok") \
            and not any((t.get("error_class") in ("transient", "timeout", "credits", "billing")) for t in edt.get("tests", [])):
        retryable.append("edit_robustness")
    if by_id.get("source_hygiene", {}).get("ok") is False:  # a static property of the worker's own source: always model-attributable
        retryable.append("source_hygiene")
    return {
        "ok": not failed and all(g["ok"] is not None for g in gates if g["id"] != "reference_fidelity"),
        "summary": {"pass": len(passed), "fail": len(failed), "not_applicable": len(na)},
        "passed": passed, "failed": failed, "not_applicable": na, "tier_a_failed": tierA_failed,
        "retryable_failed": retryable,
        "tiers": TIERS, "gates": gates,
    }


_PATH_TOKEN = re.compile(r"(?<![\w/])((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]{1,5})")


def provenance_checks(ctx: Ctx) -> dict[str, Any]:
    """Do stated/measured `source` fields point at files that exist? Any `blocking:` open question? Interfaces without checks?"""
    c = ctx.contract
    roots = (ctx.design_dir, ctx.design_dir / "sources", REPO_ROOT)
    unresolved: dict[str, list[str]] = {}
    unanchored: list[str] = []
    for p in c.parameters:
        if p.provenance not in ("stated", "measured", "measured (reference model)") or not p.source:
            continue
        tokens = [t.rstrip(".,;:") for t in _PATH_TOKEN.findall(p.source)]
        if not tokens:
            unanchored.append(p.name)
            continue
        missing = [t for t in tokens if not any((r / t).exists() for r in roots)]
        if missing and len(missing) == len(tokens):
            unresolved[p.name] = missing
    blocking = [q for q in c.open_questions if q.strip().lower().startswith("blocking:")]
    unenforced = [i.name for i in c.interfaces if i.must_not_change and not i.checks]
    return {"unresolved_sources": unresolved, "unanchored_sources": unanchored, "blocking_questions": blocking, "unenforced_interfaces": unenforced,
            "interface_checks": c.interface_checks()}


def symmetry_line(name: str, row: dict[str, Any]) -> str:
    wp = row.get("worst_point") or [0, 0, 0]
    if isinstance(wp, (list, tuple)) and len(wp) >= 3:
        loc = f"({float(wp[0]):.1f}, {float(wp[1]):.1f}, {float(wp[2]):.1f})"
    else:
        loc = str(wp)
    mx, p95 = row.get("max"), row.get("p95")
    mx_s = f"{mx:.3f}" if isinstance(mx, (int, float)) else str(mx)
    p95_s = f"{p95:.3f}" if isinstance(p95, (int, float)) else str(p95)
    src = f" [{row['source']}]" if row.get("source") else ""
    return f"symmetry {name}: max {mx_s} mm at {loc}, p95 {p95_s} (tol {row.get('max_deviation', 0.1)} / {row.get('p95_deviation', 0.05)}){src}"


ITEM_TABLES = ("sections", "faces", "cylinders", "planes", "dimensions", "solids", "clearances", "passages", "thickness", "probes", "cylinder_counts", "gears", "meshes", "symmetry")
SCALAR_ITEMS = ("bbox", "volume", "surface_area", "center_of_mass", "solid_count")
# correction priority: what a worker should land first when many items fail
FOCUS_ORDER = ("features", "sections", "cylinders", "faces", "planes", "dimensions", "solids", "thickness", "passages", "probes", "cylinder_counts", "clearances", "gears", "meshes", "symmetry")
FOCUS_LIMIT = 6
FOCUS_CLUSTER_MM = 15.0


def failing_item_names(ins: dict[str, Any]) -> list[str]:
    """`kind/name` of every failed inspect item (required features, acceptance tables, scalars): the progress signal of the correction loop."""
    names: list[str] = []
    for k in ITEM_TABLES:
        for n, x in (ins.get(k) or {}).items():
            if isinstance(x, dict) and x.get("ok") is False:
                names.append(f"{k}/{n}")
    for fid, f in (ins.get("features") or {}).items():
        if isinstance(f, dict) and f.get("ok") is False and not f.get("optional"):
            names.append(f"features/{fid}")
    for k in SCALAR_ITEMS:
        q = ins.get(k) or {}
        if isinstance(q, dict) and q.get("ok") is False:
            names.append(k)
    dev = ins.get("deviation") or {}
    if dev.get("ok") is False:
        names.append("deviation")
        names += [f"deviation/{band_name(dev.get('axis') or 'z', b)}" for b in dev.get("bands") or [] if b.get("ok") is False]
    return sorted(set(names))


def band_name(axis: str, band: dict[str, Any]) -> str:
    return f"{axis}={band['lo']:.1f}..{band['hi']:.1f}"


def _sides(r: dict[str, Any]) -> str:
    return f"model up to {r['inside_p95']:.2f} mm inside and {r['outside_p95']:.2f} mm outside the reference"


def deviation_items(dev: dict[str, Any], *, only_failed: bool = True) -> list[tuple[str, str]]:
    """The reference deviation: its checks and signed map, each band along the longest axis over the p95 limit, and the worst regions."""
    if not dev.get("declared") or not dev.get("reference") or (only_failed and dev.get("ok") is not False):
        return []
    checks = "; ".join(f"{k} {v['measured']:.3f} (limit {v.get('max', v.get('min'))}) {'OK' if v['ok'] else 'FAIL'}" for k, v in (dev.get("checks") or {}).items())
    where = f"; signed map {dev['map']} (red: model outside the reference, blue: inside)" if dev.get("map") else ""
    items = [("deviation", f"- reference deviation {'OK' if dev.get('ok') else 'FAIL'}: {checks}{where}")]
    axis = dev.get("axis") or "z"
    items += [(f"deviation/{band_name(axis, b)}", f"- deviation band {band_name(axis, b)} mm: p95 {b['p95']:.2f} max {b['max']:.2f}; {_sides(b)}")
              for b in dev.get("bands") or [] if b.get("ok") is False]
    share = f"{100 * (dev.get('worst_share') or 0.02):g}"
    items += [("deviation/worst", f"- worst {share} % of deviation samples: box {r['box'][0]}..{r['box'][1]} ({r['n']} samples) max {r['max']:.2f}; {_sides(r)}")
              for r in (dev.get("worst") or [])[:3] if dev.get("ok") is False]
    return items


def inspection_items(ins: dict[str, Any], contract: PartContract, *, only_failed: bool = True) -> list[tuple[str, str]]:
    """(`kind/name`, measured-vs-expected line) for every failed inspect check (shared by the correction brief and the worker's local critic).
    `only_failed=False` also lists the checks that passed, for `quick --all`."""
    items: list[tuple[str, str]] = []
    # Never fall back to the engine bbox: engine analyze can include sketch-plane padding.
    bb = ins.get("bbox") or {}
    if bb:
        items.append(("bbox", f"- bbox min {bb.get('measured_min')} max {bb.get('measured_max')}; expected min {bb.get('expected_min')} max {bb.get('expected_max')} (tol ±{bb.get('tolerance')})"))
    for k in ("volume", "surface_area"):
        q = ins.get(k) or {}
        if q.get("declared"):
            items.append((k, f"- {k}: measured {q.get('measured')} expected {q.get('expected')} (band ±{q.get('band')}) {'OK' if q.get('ok') else 'FAIL'}"))
    com = ins.get("center_of_mass") or {}
    if com.get("declared"):
        items.append(("center_of_mass", f"- centre of mass: measured {com.get('measured')} expected {com.get('expected')} (±{com.get('tolerance')} per axis) {'OK' if com.get('ok') else 'FAIL'}"))
    for sid, s in (ins.get("sections") or {}).items():
        if not s.get("ok"):
            items.append((f"sections/{sid}", f"- section {sid} ({s['plane']}={s['at']}): measured {s.get('measured')}; checks {s.get('checks')}"))
        elif not only_failed:
            items.append((f"sections/{sid}", f"- section {sid} ({s['plane']}={s['at']}): OK"))
    for fid, f in (ins.get("faces") or {}).items():
        if not f.get("ok"):
            items.append((f"faces/{fid}", f"- named face {fid}: plane {f['plane']}={f['at']} normal {f['normal']}: found {f.get('found')} area {f.get('area')} expected {f.get('area_expected')}"))
        elif not only_failed:
            items.append((f"faces/{fid}", f"- named face {fid}: OK area {f.get('area')}"))
    for cid, cy in (ins.get("cylinders") or {}).items():
        if not cy.get("ok"):
            if cy.get("found"):
                m = cy.get("measured") or {}
                items.append((f"cylinders/{cid}", (f"- cylinder {cid} ({cy['kind']}, r={cy['radius_expected']}): axis is {cy.get('axis_offset'):.3f} mm off its specified axis (tol {cy.get('axis_tolerance')}); "
                                                   f"measured centre {m.get('center')} radius {m.get('radius')} length {m.get('length')}; spec point {cy['point']} direction {cy['direction']}; checks {cy.get('checks')}")))
            else:
                items.append((f"cylinders/{cid}", f"- cylinder {cid} ({cy['kind']}, r={cy['radius_expected']}) not found near point {cy['point']} direction {cy['direction']} (radius band ±{contract.acceptance.cylinders[[x.name for x in contract.acceptance.cylinders].index(cid)].radius_tolerance})"))
    for pid, pl in (ins.get("planes") or {}).items():
        if not pl.get("ok"):
            items.append((f"planes/{pid}", f"- plane {pid}: normal {pl['normal']} through {pl['point']}: found {pl.get('found')} faces, area {pl.get('area')} expected {pl.get('area_expected')}"))
    for did, dm in (ins.get("dimensions") or {}).items():
        if not dm.get("ok"):
            items.append((f"dimensions/{did}", f"- dimension {did} along {dm['axis']}{' between ' + str(dm['between']) if dm.get('between') else ' (bbox extent)'}: measured {dm.get('measured')} expected {dm['expected']} (band ±{dm.get('band')})"))
    for sid, s in (ins.get("solids") or {}).items():
        if not s.get("ok"):
            items.append((f"solids/{sid}", f"- solid {sid}: {'not found at point ' + str(s.get('contains_point')) if not s.get('found') else 'volume check ' + str(s.get('volume_check'))}"))
    for cid, cl in (ins.get("clearances") or {}).items():
        if not cl.get("ok"):
            items.append((f"clearances/{cid}", f"- clearance {cid} between {cl.get('a')} and {cl.get('b')}: interference {cl.get('interference_volume')} mm3, gap {cl.get('gap')} (min_gap {cl.get('min_gap')}, max_gap {cl.get('max_gap')}) {cl.get('error') or ''}: material must not enter this envelope / the bodies must meet the gap band"))
    for pid, ps in (ins.get("passages") or {}).items():
        if not ps.get("ok"):
            items.append((f"passages/{pid}", f"- passage {pid}: connected={ps.get('connected')} reaches_exterior={ps.get('reaches_exterior')} a={(ps.get('a') or {}).get('state')} b={(ps.get('b') or {}).get('state')} volume={ps.get('passage_volume')} {ps.get('volume_check') or ''} {ps.get('error') or ''}"))
    for tid, th in (ins.get("thickness") or {}).items():
        if not th.get("ok"):
            clusters = th.get("thin_clusters") or []
            where = ("; thin skin, largest first (n samples, share of all, median mm, box min..max): "
                     + " | ".join(f"n={c['n']} {c['share']:.1%} t={c['median']} {c['min']}..{c['max']}" for c in clusters)) if clusters else f"; thinnest points {th.get('thinnest_points')}"
            items.append((f"thickness/{tid}", f"- wall thickness {tid}: {th.get('stat')} = {th.get('measured')} mm, required >= {th.get('min_required')}{where} {th.get('error') or ''}"))
    for pid, pr in (ins.get("probes") or {}).items():
        if not pr.get("ok"):
            items.append((f"probes/{pid}", f"- probe {pid} expects {pr.get('state')} at {pr.get('points')}: measured {pr.get('states')}"))
    for cid, cc in (ins.get("cylinder_counts") or {}).items():
        if not cc.get("ok"):
            items.append((f"cylinder_counts/{cid}", f"- cylinder count {cid} ({cc.get('kind')} r={cc.get('radius')}): found {cc.get('measured')} expected {cc.get('expected')} min {cc.get('expected_min')}; centres {cc.get('centers')}"))
    for gid, g in (ins.get("gears") or {}).items():
        if not g.get("ok"):
            items.append((f"gears/{gid}", f"- gear {gid}: counted {g.get('teeth')} teeth, expected {g.get('expected')} (tip radius {g.get('tip_radius')}) {g.get('error') or ''}"))
    for mid, ms in (ins.get("meshes") or {}).items():
        if not ms.get("ok"):
            bad = [p for p in ms.get("poses", []) if not p.get("ok")]
            items.append((f"meshes/{mid}", f"- gear mesh {mid}: max interference {ms.get('max_interference')} mm3, flank gap {ms.get('gap_min')}..{ms.get('gap_max')} (backlash max {ms.get('backlash_max')}); failing poses {[(p['theta_deg'], round(p['interference_volume'], 4), round(p['gap'], 4)) for p in bad][:6]} {ms.get('error') or ''}"))
    for fid, f in (ins.get("features") or {}).items():
        if f.get("ok") is False:
            for chk in f["checks"]:
                if not chk["ok"]:
                    items.append((f"features/{fid}", f"- feature {fid} {chk['method']}: {({k: v for k, v in chk.items() if k not in ('ok', 'method')})}"))
    for name, row in (ins.get("symmetry") or {}).items():
        items.append((f"symmetry/{name}", f"- {symmetry_line(name, row)}" + ("" if row.get("ok") else " FAIL")))
    items += deviation_items(ins.get("deviation") or {}, only_failed=only_failed)
    return items


def inspection_lines(ins: dict[str, Any], contract: PartContract) -> list[str]:
    """Measured-vs-expected lines for every failed inspect check."""
    return [line for _, line in inspection_items(ins, contract)]


def _item_point(contract: PartContract, key: str) -> list[float] | None:
    from opencad.stages.decompose import item_location

    kind, _, name = key.partition("/")
    if kind == "features":
        feat = next((f for f in contract.features if f.id == name), None)
        pts: list[list[float]] = []
        for v in (feat.verify if feat else []):
            for attr, k2 in (("cylinder", "cylinders"), ("face", "faces"), ("plane", "planes")):
                ref = getattr(v, attr, None)
                if ref:
                    p = item_location(contract, k2, ref)
                    if p:
                        pts.append(p)
            for p in (getattr(v, "points", None) or []):
                pts.append(list(p))
        return [sum(p[i] for p in pts) / len(pts) for i in range(3)] if pts else None
    if kind in ("sections",):
        sec = next((s for s in contract.acceptance.sections if s.id == name), None)
        if sec is None:
            return None
        p = [0.0, 0.0, 0.0]
        p["xyz".index(sec.plane)] = float(sec.at)
        return p
    return item_location(contract, kind, name) if kind in ("cylinders", "faces", "planes", "probes", "passages", "solids", "thickness") else None


def focus_block(ins: dict[str, Any], contract: PartContract, limit: int = FOCUS_LIMIT) -> list[str]:
    """`Fix first`: the highest-priority failing item and the failing items clustered around it (<= limit), each with its measured line.

    A worker with 40 failing lines fixes the plate; with six near one another it fixes the clamp.
    """
    failing = set(failing_item_names(ins))
    items = [(k, line) for k, line in inspection_items(ins, contract) if k in failing]
    if len(items) <= limit:
        return []
    rank = {k: i for i, k in enumerate(FOCUS_ORDER)}
    items.sort(key=lambda kl: (rank.get(kl[0].split("/", 1)[0], len(rank)), kl[0]))
    anchor_key = items[0][0]
    anchor = _item_point(contract, anchor_key)
    chosen: list[tuple[str, str]] = [items[0]]
    seen = {anchor_key}
    if anchor is not None:
        near = []
        for k, line in items[1:]:
            p = _item_point(contract, k)
            if p is None or k in seen:
                continue
            d = sum((a - b) ** 2 for a, b in zip(p, anchor)) ** 0.5
            if d <= FOCUS_CLUSTER_MM:
                near.append((d, k, line))
        for _, k, line in sorted(near):
            if len(chosen) >= limit:
                break
            chosen.append((k, line))
            seen.add(k)
    for k, line in items[1:]:
        if len(chosen) >= limit:
            break
        if k not in seen:
            chosen.append((k, line))
            seen.add(k)
    where = f" (cluster near ({anchor[0]:.1f}, {anchor[1]:.1f}, {anchor[2]:.1f}) mm)" if anchor is not None else ""
    out = [f"Fix first{where}: land these {len(chosen)} items before anything else, re-run the local critic and confirm each line reads OK, then continue down the full list:"]
    out += [line for _, line in chosen]
    out.append(f"Full list ({len(items)} failing items):")
    return out


def derived_only_misses(ins: dict[str, Any], contract: PartContract, failed: list[str]) -> list[str]:
    """Mass properties that miss a hand-derived band while every other gate passes."""
    if list(failed) != ["mass_properties"]:
        return []
    a = contract.acceptance
    declared = {"volume": a.volume, "surface_area": a.surface_area, "center_of_mass": a.center_of_mass}
    missed = [k for k in declared if not (ins.get(k) or {}).get("ok", True)]
    if missed and all(declared[k] is not None and declared[k].provenance in ("derived", "inferred", "defaulted") for k in missed):
        return missed
    return []


def correction_message(ctx: Ctx, feedback: dict[str, Any]) -> str:
    """Precise measured-vs-expected deltas for one bounded Codex retry on the model thread."""
    ins = ctx.load_stage("inspect") or {}
    ver = ctx.load_stage("verify") or {}
    lines = [f"Independent inspection of `{ctx.entry}` (OpenCascade on the exported STEP, plus engine analyze) failed these gates: {feedback['failed']}.", "Measured vs expected:"]
    derived = derived_only_misses(ins, ctx.contract, feedback.get("failed") or [])
    if derived:
        lines.insert(1, f"Every other check passes; only the derived value(s) {derived} miss the contract's own band. Do not change stated geometry to meet a derived number: "
                        "no offsets on parameters (`radius + 0.025`), no resized features. Recompute the derivation in the contract note from the stated parameters; "
                        "if the part matches them, leave the source unchanged and write the discrepancy under `## Open questions`.")
    exp = ctx.load_stage("export") or {}
    eng = ver.get("engine") or {}
    if not exp.get("ok") and (is_program(eng.get("class")) or any("execution failed" in str(e).lower() for e in (exp.get("errors") or {}).values())):
        err = eng.get("error") or next(iter((exp.get("errors") or {}).values()), "")
        lines.insert(1, f"THE PROGRAM DOES NOT EXECUTE. engine export failed with: {str(err)[:600]}\n"
                        f"Restore the last executing checkpoint of {ctx.backend.language.entry} first (every deliverable must execute), then re-apply the missing features one at a time, "
                        "running engine analyze after each. Nothing below could be measured until the file executes.")
    mem = next((str(e) for e in (eng.get("error"), *(exp.get("errors") or {}).values()) if e and MEMORY_PHRASE in str(e)), None)
    if not exp.get("ok") and (eng.get("class") == "memory" or mem):
        from opencad import resources

        lines.insert(1, f"THE BUILD WAS KILLED FOR MEMORY: {str(mem or eng.get('error') or '')[:600]}\n"
                        f"An engine call may hold at most {resources.gb(resources.runner_budget())}. Restore the last checkpoint of {ctx.backend.language.entry} that built "
                        "within it, then rebuild with far fewer operations: dimensions as named parameters and a few sections per surface, never point lists traced from the "
                        "reference mesh. Nothing below could be measured until the build fits.")
    lines += focus_block(ins, ctx.contract)
    lines += inspection_lines(ins, ctx.contract)
    ref_json = ctx.design_dir / "reference" / "reference.json"
    if "reference_fidelity" in (feedback.get("failed") or []) and ref_json.exists() and "stations" in (json.loads(ref_json.read_text()).get("measurements") or {}):
        where = ref_json.relative_to(REPO_ROOT) if ref_json.is_relative_to(REPO_ROOT) else ref_json
        lines.append(f"- the reference is measured at stations in `{where}` measurements.stations (per region: the best analytic fit and `outline_16`; sheet "
                     "`reference-sections-stations.png`): rebuild each band over the limit as a smooth loft through the stations it spans, not as boxes and fillets.")
    edt = ctx.load_stage("edit") or {}
    for t in edt.get("tests", []):
        if t.get("ok"):
            continue
        pname = t.get("parameter")
        if t.get("error"):
            lines.append(f"- edit test {pname} (delta {t.get('delta')}): {t['error']}")
        for k, chk in (t.get("checks") or {}).items():
            if not chk.get("ok"):
                lines.append(f"- edit test {pname} (delta {t.get('delta')}) check {k}: {({kk: vv for kk, vv in chk.items() if kk != 'ok'})}")
        for row in (t.get("sweep") or {}).get("values", []):
            if not row.get("ok"):
                lines.append(f"- sweep {pname} = {row.get('value')}: {row.get('error') or {k: v for k, v in (row.get('checks') or {}).items() if not v.get('ok')}}")
        for row in (t.get("infeasible") or {}).get("deltas", []):
            if not row.get("ok"):
                lines.append(f"- infeasible value {pname} = {row.get('value')} (delta {row.get('delta')}) {row.get('outcome')}: {row.get('note') or row.get('error')}. "
                             "Add an `assert` that rejects this value with a clear message; the value must fail loudly, not build.")
    hyg = ver.get("hygiene") or {}
    size = hyg.get("source_size") or {}
    if not size.get("ok", True):
        lines.append(f"- {traced_geometry_note(size)}. A surface is a few sections or splines driven by named parameters; rebuild the part "
                     "that way instead of pasting points read from the reference mesh.")
    bad_params = {k: v for k, v in (hyg.get("parameters") or {}).items() if not v.get("ok")}
    if bad_params:
        lines.append(f"- parameters missing or wrong as top-level constants: {bad_params}")
    if hyg.get("legacy_v1"):
        lines.append(f"- legacy KCL v1 constructs present: {hyg['legacy_v1']}")
    if not (ver.get("lint") or {}).get("ok", True):
        lines.append(f"- lint: {(ver.get('lint') or {}).get('output', '')[:500]}")
    agr = ins.get("agreement") or {}
    if agr:
        rel = agr.get("kcl_vs_step_rel")
        stl_rel = agr.get("stl_vs_step_rel")
        lines.append(
            f"- agreement: engine={agr.get('engine', agr.get('kcl'))} kcl={agr.get('kcl')} step={agr.get('step')} stl={agr.get('stl')} "
            f"kcl_vs_step_rel={rel} engine_vs_step_rel={agr.get('engine_vs_step_rel', rel)} stl_vs_step_rel={stl_rel} (tol {agr.get('tolerance_rel')}) "
            f"{'OK' if agr.get('ok') else 'FAIL'}"
        )
    mesh_ = ins.get("mesh") or {}
    oe = mesh_.get("open_edges") or {}
    if oe.get("count"):
        cxyz = oe.get("centroid") or []
        z = cxyz[2] if len(cxyz) == 3 else None
        z_note = f" at z = {z}" if z is not None else ""
        lines.append(
            f"- open mesh edges: {oe['count']} forming an open ring{z_note}; "
            f"bbox {oe.get('bbox_min')} .. {oe.get('bbox_max')}; centroid {cxyz}"
        )
    vb, ib = ver.get("bbox") or {}, ins.get("bbox") or {}
    if vb.get("measured_min") and ib.get("measured_min"):
        engine_box = (vb.get("measured_min"), vb.get("measured_max"))
        step_box = (ib.get("measured_min"), ib.get("measured_max"))
        if engine_box != step_box:
            lines.append(
                f"- engine bbox min {engine_box[0]} max {engine_box[1]} vs STEP min {step_box[0]} max {step_box[1]} "
                f"(engine max_error {vb.get('max_error')}); hide construction regions so the engine box matches the "
                f"finished solid — do not sketch datum axes (`hide` does not take sketch blocks)"
            )
    oq = ((ctx.load_stage("model") or {}).get("codex_report") or {}).get("Open questions")
    if oq:
        lines.append("Codex Open questions:")
        lines.append(oq)
    lines.append(f"Fix `{ctx.backend.language.entry}` in place (same frame, same parameter names; do not touch the contract), re-verify with analyze, and report the new measured values under ## Verification.")
    return "\n".join(lines)

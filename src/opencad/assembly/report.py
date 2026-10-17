"""Report stage: report.md / report.html (animation, gates, observables), handoff/ (assembled STEP/STL, animated GLBs, viewer)
and the engineering package/: source, assembly, geometry, boundaries, case, results, evaluation, provenance."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any

from opencad.assembly import AsmCtx
from opencad.io import dump_json, provenance, sha256_file, sha256_tree
from opencad.paths import DOCS, NESTED, design_dir, part_dir

PACKAGE_DIRS = ("source", "assembly", "geometry", "boundaries", "case", "results", "evaluation", "provenance")
CASE_SUFFIXES = {".inp", ".json", ".yaml", ".geo"}
RESULT_SUFFIXES = {".dat", ".sta", ".cvg", ".log", ".csv", ".txt"}
PACKAGE_FILE_MAX = 5_000_000


def _copy(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dest)


def package(actx: AsmCtx, fb: dict[str, Any]) -> dict[str, Any]:
    root = actx.results_dir / "package"
    for d in PACKAGE_DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    a = actx.contract
    _copy(actx.entry, root / "source" / actx.entry.name)
    _copy(actx.part_dir / "placements.json", root / "source" / "placements.json")
    suffixes = actx.backend.language.suffixes
    for d in a.designs():
        src_dir = part_dir(d, backend=actx.backend_id)
        for f in sorted(p for p in src_dir.iterdir() if p.suffix in suffixes) if src_dir.exists() else []:
            _copy(f, root / "source" / d / f.name)
        _copy(design_dir(d) / "contract.yaml", root / "source" / d / "contract.yaml")
    _copy(actx.contract_path, root / "assembly" / "assembly.yaml")
    exp = actx.results_dir / "export"
    _copy(exp / "placements.json", root / "assembly" / "placements.json")
    ver = actx.load_stage("verify") or {}
    dump_json(root / "assembly" / "bom.json", [{"body": p.name, "kind": p.kind, "role": p.role, "design": p.design, "material": p.material,
                                              "density_kg_m3": p.density_kg_m3, "input_step": str(actx.input_step(p.name)) if p.kind != "derived" else None} for p in a.parts])
    dump_json(root / "assembly" / "joints.json", {"contract": [j.model_dump() for j in a.joints], "fidelity": (ver.get("joints") or {}).get("joints"),
                                                  "transmissions": [t.model_dump() for t in a.transmissions]})
    _copy(exp / f"{actx.name}.step", root / "geometry" / f"{actx.name}.step")
    _copy(exp / "bodies", root / "geometry" / "bodies")
    dump_json(root / "geometry" / "units.json", {"length": "mm", "angle": "deg", "frame": a.frame.model_dump(), "envelope": a.envelope.model_dump(),
                                                 "note": "the fluid regions are analysis domains, not manufactured parts"})
    dom = actx.load_stage("domains") or {}
    _copy(actx.results_dir / "boundaries", root / "boundaries")
    dump_json(root / "boundaries" / "boundaries.json", {k: {"labels": v.get("labels"), "unassigned": v.get("unassigned"), "conflicts": v.get("conflicts")}
                                                         for k, v in (dom.get("boundaries") or {}).items()})
    sim_root = actx.results_dir / "sim"
    for d in sorted(sim_root.iterdir()) if sim_root.exists() else []:
        if not d.is_dir() or d.name == "geometry":
            continue
        for f in d.rglob("*"):
            if not f.is_file() or f.stat().st_size > PACKAGE_FILE_MAX or "polyMesh" in f.parts or any(p.startswith("processor") for p in f.parts):
                continue
            rel = f.relative_to(d)
            if f.suffix.lower() in RESULT_SUFFIXES or rel.parts[0] == "postProcessing":
                _copy(f, root / "results" / d.name / rel)
            elif f.suffix.lower() in CASE_SUFFIXES or rel.parts[0] in ("system", "constant", "0"):
                _copy(f, root / "case" / d.name / rel)
    sim = actx.load_stage("simulate") or {}
    dump_json(root / "results" / "observables.json", sim.get("observables") or {})
    dump_json(root / "evaluation" / "validation.json", bases(a, sim))
    _copy(DOCS / "validation-envelope.json", root / "evaluation" / "validation-envelope.json")
    dump_json(root / "case" / "inputs.json", [s.model_dump() for s in a.simulations])
    for st in ("parts", "verify", "kinematics", "domains", "simulate"):
        _copy(actx.stage_file(st), root / "evaluation" / f"{st}.json")
    dump_json(root / "evaluation" / "gate_feedback.json", fb)
    dump_json(root / "provenance" / "provenance.json", provenance({
        "assembly": actx.name, "backend": actx.backend_id, "contract_sha256": sha256_file(actx.contract_path),
        "design_bundles": {d: sha256_tree(design_dir(d), exclude=NESTED) for d in [actx.name, *a.designs()]},
        "part_handoffs": {d: (actx.load_stage("parts") or {}).get("designs", {}).get(d, {}).get("step_sha256") for d in a.designs()},
        "source": sha256_tree(actx.part_dir, (".py",), exclude=NESTED) if actx.part_dir.exists() else {},
        "references": [r.model_dump() for r in a.references],
    }))
    return {"root": str(root), "dirs": list(PACKAGE_DIRS)}


def handoff(actx: AsmCtx, fb: dict[str, Any], sim: dict[str, Any]) -> dict[str, Any]:
    from opencad.assembly import viz

    out = actx.results_dir / "handoff"
    out.mkdir(parents=True, exist_ok=True)
    exp = actx.results_dir / "export"
    for suffix in ("step", "stl"):
        _copy(exp / f"{actx.name}.{suffix}", out / f"{actx.name}.{suffix}")
    try:
        v = viz.generate(actx, out, fb=fb, sim=sim)
    except Exception as e:  # visuals never change the verdict
        v = {"error": f"{type(e).__name__}: {e}"}
    return {"dir": str(out), "viz": v}


def _row(*cells: Any) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def _g(x: Any) -> str:
    return f"{x:.4g}" if isinstance(x, (int, float)) and not isinstance(x, bool) else ("-" if x is None else str(x))


def validation_basis(solver: str, quantity: str, envelope: list[dict[str, Any]] | None = None) -> str:
    """What the validation envelope (docs/validation-envelope.json, from the machine truth cases) says about this solver and quantity."""
    if envelope is None:
        p = DOCS / "validation-envelope.json"
        envelope = json.loads(p.read_text()).get("envelope", []) if p.exists() else []
    e = next((e for e in envelope if e["solver"] == solver and e["quantity"] == quantity), None)
    if e is None:
        return f"unvalidated: no scored machine case uses {solver} for {quantity}"
    err = f"bias {100 * e['bias']:+.1f} %" + (f", spread {100 * e['spread']:.1f} %" if e.get("spread") is not None else "") if e.get("bias") is not None else "no scalar error"
    return (f"{e['points']} point{'s' if e['points'] != 1 else ''} ({e['development']} dev / {e['held_out']} held-out) on {', '.join(e['machines'])}: {err}; "
            f"{e['passed']} pass, {e['failed']} fail, {e['unresolved']} unresolved; {e['resolved']} mesh-resolved")


def _simulations(a: Any, sim: dict[str, Any]) -> list[str]:
    """Each analysis with its model and assumptions, each mesh ladder level by level, and every prediction with its numerical uncertainty,
    whether its ladder resolves it, and its validation basis."""
    declared = {s.id: s for s in a.simulations}
    lines = ["", "## Simulations", "", _row("simulation", "status", "solver", "model", "levels", "wall s", "note"), _row(*["---"] * 7)]
    for n, s in (sim.get("simulations") or {}).items():
        d = declared.get(n)
        meshed = d is not None and d.solver in ("calculix", "openfoam")
        lines.append(_row(n, s.get("status"), d.solver if d else "-", s.get("model") or "-", ", ".join(lv.label for lv in d.levels()) if meshed else "-",
                          s.get("wall_s"), (s.get("error") or s.get("reason") or "")[:200].replace("|", "/")))
    for n, s in (sim.get("simulations") or {}).items():
        if s.get("assumptions"):
            lines += ["", f"Assumptions of `{n}`:", *[f"- {x}" for x in s["assumptions"]]]
        for oid, st in ((s.get("refinement") or {}).get("observables") or {}).items():
            lines += ["", f"Mesh ladder of `{oid}` (`{n}`): " + ("resolved" if st.get("resolved") else "unresolved: " + "; ".join(st.get("unresolved_because") or [])),
                      "", _row("level", "cells", "value", "u_iteration", "drift"), _row(*["---"] * 5)]
            for i, lab in enumerate(st.get("mesh_levels") or []):
                lines.append(_row(lab, _g(st["cells"][i]), _g(st["values"][i]), _g((st.get("u_iterations") or [None] * (i + 1))[i]), _g(st["drift"][i])))
            if st.get("gci") is not None:
                lines += ["", (f"GCI {st['gci']:.4f} ({st.get('convergence')}, observed order {_g(st.get('order'))}, Fs {_g(st.get('fs'))}); "
                               f"Richardson value {_g(st.get('extrapolated'))}; u_discretisation {_g(st.get('u_discretisation'))}")]
    obs = sim.get("observables") or {}
    basis = bases(a, sim)
    counts = {k: sum(1 for o in obs.values() if o.get("status") == "ok" and o.get("resolved") is v) for k, v in (("resolved", True), ("unresolved", False), ("no ladder", None))}
    computed = sum(1 for o in obs.values() if o.get("status") == "ok")
    lines += ["", (f"Predictions: {computed} of {len(obs)} computed; mesh ladders resolve {counts['resolved']}, leave {counts['unresolved']} unresolved "
                   f"(reported, never evidence), {counts['no ladder']} have none (reduced models, measurements, one mesh level)."), "",
              _row("observable", "value", "unit", "u_num", "u_disc", "u_iter", "resolved", "case", "status", "requirement", "validation basis"), _row(*["---"] * 11)]
    for n, o in obs.items():
        req = o.get("requirement") or {}
        band = req.get("value_band")
        met = ({True: "met", False: "missed"}.get(req.get("ok"), "undetermined") + (f" over {_g(band[0])}..{_g(band[1])}" if band and band[0] != band[1] else "")) if req else "-"
        lines.append(_row(n, _g(o.get("value")), o.get("unit"), _g(o.get("u_numerical")), _g(o.get("u_discretisation")), _g(o.get("u_iteration")),
                          {True: "yes", False: "no"}.get(o.get("resolved"), "-"), o.get("case") or "-", o.get("status"), met, basis[n]["basis"]))
    return lines


def bases(a: Any, sim: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Per observable: its solver, quantity, whether its mesh ladder resolves it, and its validation basis from the envelope."""
    p = DOCS / "validation-envelope.json"
    envelope = json.loads(p.read_text()).get("envelope", []) if p.exists() else []
    declared = {s.id: s for s in a.simulations}
    out = {}
    for n, o in (sim.get("observables") or {}).items():
        spec = next((x for x in a.observables if x.id == n), None)
        solver = declared[spec.simulation].solver if spec is not None and spec.simulation in declared else "evaluator"
        out[n] = {"solver": solver, "quantity": o.get("quantity"), "resolved": o.get("resolved"), "basis": validation_basis(solver, o.get("quantity") or "", envelope)}
    return out


def markdown(actx: AsmCtx, fb: dict[str, Any], ho: dict[str, Any]) -> str:
    a = actx.contract
    ver = actx.load_stage("verify") or {}
    kin = actx.load_stage("kinematics") or {}
    dom = actx.load_stage("domains") or {}
    sim = actx.load_stage("simulate") or {}
    parts = actx.load_stage("parts") or {}
    lines = [f"# {actx.name} ({actx.backend_id}): {'PASS' if fb.get('ok') else 'FAIL'}", "", a.intent.strip(), "", f"Gates: {fb.get('summary')}", ""]
    viz = ho.get("viz") or {}
    if viz.get("html"):
        lines += [f"Animated viewer: `{viz['html']}` (GLB `{viz.get('glb')}`, clips {', '.join(viz.get('clips') or [])})", ""]
    lines += ["## Bill of materials", "", _row("body", "kind", "design", "part gates", "agreement"), _row("---", "---", "---", "---", "---")]
    for p in a.parts:
        pd = (parts.get("designs") or {}).get(p.design or "", {})
        ag = ((ver.get("agreement") or {}).get("bodies") or {}).get(p.name, {})
        agree = "see fluid regions" if p.role == "fluid" and not ag else ("ok" if ag.get("ok") else (ag.get("error") or f"vol {ag.get('volume_rel')}, haus {ag.get('hausdorff_mm')}"))
        lines.append(_row(p.name, f"{p.kind}/{p.role}", p.design or "-", pd.get("summary") or "-", agree))
    lines += ["", "## Joints", "", _row("joint", "kind", "parent -> child", "checks", "ok"), _row("---", "---", "---", "---", "---")]
    for n, j in ((ver.get("joints") or {}).get("joints") or {}).items():
        checks = ", ".join(f"{k} {c['measured']:.4g}" for k, c in (j.get("checks") or {}).items())
        lines.append(_row(n, j.get("kind"), f"{j.get('parent')} -> {j.get('child')}", checks or j.get("error", ""), j.get("ok")))
    if kin.get("motions") or kin.get("transmissions"):
        lines += ["", "## Motion", "", _row("item", "result", "ok"), _row("---", "---", "---")]
        for n, m in (kin.get("motions") or {}).items():
            lines.append(_row(f"motion {n}", f"{m.get('steps')} steps over {m.get('range')}, {len(m.get('pairs') or [])} pairs, max interference {m.get('max_interference'):.4g} mm3", m.get("ok")))
        for n, t in (kin.get("transmissions") or {}).items():
            mesh = t.get("mesh") or {}
            lines.append(_row(f"transmission {n}", f"ratio {t.get('ratio')} (teeth {t.get('ratio_measured')}); mesh gap {mesh.get('gap_min')}..{mesh.get('gap_max')}, interference {mesh.get('max_interference')}", t.get("ok")))
    if dom.get("fluids") or dom.get("boundaries"):
        lines += ["", "## Fluid regions and boundaries", ""]
        for n, f in (dom.get("fluids") or {}).items():
            lines.append(f"- fluid `{n}`: sealed {f.get('sealed')}, volume {f.get('volume')}, agreement {(f.get('agreement') or {}).get('hausdorff_mm')} mm; ok {f.get('ok')}")
        for n, b in (dom.get("boundaries") or {}).items():
            lines.append(f"- boundaries on `{n}`: " + ", ".join(f"{k} ({v['role']}, {len(v['faces'])} faces, {v['area']:.1f} mm2)" for k, v in (b.get("labels") or {}).items())
                         + f"; unassigned {b.get('unassigned')}")
    if sim.get("simulations") or sim.get("observables"):
        lines += _simulations(a, sim)
    lines += ["", "## Gates", "", _row("tier", "gate", "result", "evidence"), _row("---", "---", "---", "---")]
    for g in fb.get("gates") or []:
        lines.append(_row(g["tier"], g["id"], "PASS" if g["ok"] else ("FAIL" if g["ok"] is False else "n/a"), (g["evidence"] or [""])[0][:220].replace("|", "/")))
    retry = fb.get("retry") or {}
    if retry.get("attempted"):
        lines += ["", f"Corrections: {retry.get('corrections')} ({retry.get('stopped')})"]
    lines += ["", ("A PASS means the placed parts, joints, motion, fluid regions and declared analyses agree with the contract within its tolerances; it is not"
                   " experimental validation. Each prediction's validation basis quotes docs/validation-envelope.json: how the same solver did on the same"
                   " quantity against measurements in the machine truth cases. An unresolved or unvalidated prediction is not evidence of performance."), ""]
    return "\n".join(lines)


def build(actx: AsmCtx, fb: dict[str, Any]) -> dict[str, Any]:
    sim = actx.load_stage("simulate") or {}
    ho = handoff(actx, fb, sim)
    pkg = package(actx, fb)
    md = markdown(actx, fb, ho)
    (actx.results_dir / "report.md").write_text(md, encoding="utf-8")
    viewer = (ho.get("viz") or {}).get("html")
    body = html.escape(md).replace("\n", "<br>\n")
    frame = '<iframe src="handoff/assembly.html" style="width:100%;height:70vh;border:1px solid #ddd"></iframe>' if viewer else ""
    (actx.results_dir / "report.html").write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>{actx.name}</title></head>"
                                                  f"<body style='font:14px system-ui;margin:20px'>{frame}<div style='font-family:ui-monospace,monospace'>{body}</div></body></html>", encoding="utf-8")
    return {"ok": True, "verdict": "PASS" if fb.get("ok") else "FAIL", "report_md": str(actx.results_dir / "report.md"), "report_html": str(actx.results_dir / "report.html"),
            "handoff": ho, "package": pkg}

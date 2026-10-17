"""Assembly gates, tiered like the part gates. A (design): parts_pass, bom_complete, joint_fidelity, clearances, motion_clear,
fluid_domain. B (consistency): export_agreement, performance, conservation, refinement. C (artifact truth): source_hygiene,
boundaries_complete, provenance, evidence_separation. `None` is not applicable, never a pass."""

from __future__ import annotations

from typing import Any

from opencad.assembly import AsmCtx
from opencad.assembly import joints as jm
from opencad.assembly.verify import lines as verify_lines

RETRYABLE = ("bom_complete", "joint_fidelity", "clearances", "motion_clear", "fluid_domain", "export_agreement", "source_hygiene")


def _g(id_: str, tier: str, title: str, ok: bool | None, evidence: list[str], failure_means: str, knob: str, details: Any = None) -> dict[str, Any]:
    return {"id": id_, "tier": tier, "title": title, "ok": ok, "evidence": evidence, "failure_means": failure_means, "knob": knob, "details": details}


def _resolution(name: str, st: dict[str, Any]) -> str:
    gci = f"GCI {st['gci']:.3g}" if st.get("gci") is not None else "no GCI"
    return f"{name} {gci} " + ("resolved" if st.get("resolved") else f"unresolved ({'; '.join(st.get('unresolved_because') or [])})")


def evaluate(actx: AsmCtx) -> dict[str, Any]:
    R = f"results/{actx.backend_id}/{actx.name}"
    a = actx.contract
    parts = actx.load_stage("parts") or {}
    ver = actx.load_stage("verify") or {}
    kin = actx.load_stage("kinematics") or {}
    dom = actx.load_stage("domains") or {}
    sim = actx.load_stage("simulate") or {}
    designs = parts.get("designs") or {}
    gates = []
    bad_parts = [d for d, v in designs.items() if not (v.get("gates_ok") and v.get("handoff"))]
    part_gates = ", ".join(f"{d}={v.get('gates_ok')}" for d, v in designs.items())
    gates.append(_g("parts_pass", "A", "Every part design passed its own 12 gates and has a handoff STEP", (not bad_parts) if designs else None,
                    [f"{R}/parts.json designs.<design>.gates_ok: {part_gates}"],
                    "a part is wrong on its own, before any placement", "the part's own pipeline (correct that design)", {"failing": bad_parts}))
    sc, pl, ag = ver.get("solid_count") or {}, ver.get("placements") or {}, ver.get("agreement") or {}
    missing = [n for n, b in (ag.get("bodies") or {}).items() if "error" in b]
    bom_ok = bool(sc.get("ok") and pl.get("ok") and not missing) if ver else None
    gates.append(_g("bom_complete", "A", "Every body of the bill of materials is in the export, once, with a placement", bom_ok,
                    [f"{R}/verify.json solid_count = {sc.get('measured')} (expected {sc.get('expected')}); placements.missing = {pl.get('missing')}; unmatched = {missing}"],
                    "a body is missing, duplicated or fused", "the assembly source's `result` / `placements`", {"solid_count": sc, "missing": missing}))
    jn = ver.get("joints") or {}
    bad_j = [n for n, j in (jn.get("joints") or {}).items() if not j.get("ok")]
    gates.append(_g("joint_fidelity", "A", "Every joint's child frame lies on its parent frame (axis, offset, rest angle)", jn.get("ok") if a.joints and ver else None,
                    [f"{R}/verify.json joints.joints.<joint>.checks; failing: {bad_j or 'none'}"], "a body sits off its joint axis or at the wrong offset or phase",
                    "the placement transforms in the assembly source", {"failing": bad_j}))
    cl = ver.get("clearances") or {}
    bad_c = [n for n, c in cl.items() if not c.get("ok")]
    gates.append(_g("clearances", "A", "Static clearances and seats at rest", (not bad_c) if cl else None,
                    [f"{R}/verify.json clearances.<name>; failing: {bad_c or 'none'}"], "bodies interpenetrate or do not seat at rest",
                    "the placement (or the part if its interface is wrong)", {"failing": bad_c}))
    motions, trans = kin.get("motions") or {}, kin.get("transmissions") or {}
    bad_m = [n for n, m in motions.items() if not m.get("ok")] + [n for n, t in trans.items() if not t.get("ok")]
    gates.append(_g("motion_clear", "A", "Every drive moves through its range without interference; gears mesh; ratios match tooth counts",
                    (not bad_m and not kin.get("missing_bodies")) if (motions or trans) else None,
                    [f"{R}/kinematics.json motions.<name>.max_interference: " + ", ".join(f"{n}={m.get('max_interference', 0):.4g}" for n, m in motions.items()),
                     *([f"{R}/kinematics.json motions.<name>.loop.closure_mm_max: " + ", ".join(f"{n}={m['loop']['closure_mm_max']:.3g}" for n, m in motions.items() if m.get("loop"))]
                       if any(m.get("loop") for m in motions.values()) else []),
                     f"{R}/kinematics.json transmissions.<name>: " + ", ".join(f"{n} ratio {t.get('ratio_measured')} vs {t.get('ratio')}, mesh ok {(t.get('mesh') or {}).get('ok')}" for n, t in trans.items())],
                    "the machine jams, collides or is geared wrong", "phasing and placement in the assembly source, or the part geometry", {"failing": bad_m}))
    fl = dom.get("fluids") or {}
    bad_f = [n for n, f in fl.items() if not f.get("ok")]
    gates.append(_g("fluid_domain", "A", "Each fluid region is one sealed piece within its volume band and agrees with the source's fluid body",
                    (not bad_f) if fl else None, [f"{R}/domains.json fluids.<name>: " + ", ".join(f"{n} sealed={f.get('sealed')} volume={f.get('volume')}" for n, f in fl.items())],
                    "the analyses would run on a leaking or wrong fluid region", "walls and caps in the parts, the fluid booleans in the source", {"failing": bad_f}))
    env = ver.get("envelope") or {}
    agree_ok = bool(ag.get("ok") and env.get("ok")) if ver else None
    gates.append(_g("export_agreement", "B", "Each exported body equals its part handoff x placement; the assembled envelope matches",
                    agree_ok, [f"{R}/verify.json agreement.bodies.<body>.volume_rel/hausdorff_mm; envelope.max_error = {env.get('max_error')} (tol {env.get('tolerance')})"],
                    "a body was rebuilt, scaled or clipped instead of placed", "the assembly source (import, never rebuild)", None))
    obs = sim.get("observables") or {}
    reqs = {k: v["requirement"] for k, v in obs.items() if v.get("requirement")}
    judged = {k: r for k, r in reqs.items() if r.get("ok") is not None}
    undetermined = [k for k, r in reqs.items() if r.get("ok") is None and obs[k].get("status") == "ok"]

    def _band(k: str) -> str:
        lo, hi = reqs[k].get("value_band") or (None, None)
        return f"{k}={obs[k].get('value'):.4g}" + (f" (band {lo:.4g}..{hi:.4g})" if lo is not None and lo != hi else "") if obs[k].get("value") is not None else f"{k}=-"

    gates.append(_g("performance", "B", "Every predicted observable meets the requirement the sources state over its numerical band (value +- 2 u_numerical)",
                    (all(r["ok"] for r in judged.values())) if judged else None,
                    [f"{R}/simulate.json observables.<id>.requirement: " + ", ".join(_band(k) for k in reqs) or "none declared",
                     "undetermined (the band straddles the requirement): " + (", ".join(undetermined) or "none"),
                     "unavailable predictions: " + (", ".join(k for k, v in obs.items() if v.get("status") != "ok") or "none")],
                    "the machine does not do what the sources require at an operating case", "the design (a new change request), never the inputs",
                    {"unmet": [k for k, r in judged.items() if not r["ok"]], "undetermined": undetermined,
                     "unavailable": [k for k, v in obs.items() if v.get("status") != "ok"]}))
    sims = sim.get("simulations") or {}
    cons = {f"{s}.{c}": v for s, r in sims.items() for c, v in (r.get("conservation") or {}).items()}
    gates.append(_g("conservation", "B", "Energy, mass and force balances of every analysis close within their tolerance", (all(v.get("ok") for v in cons.values())) if cons else None,
                    [f"{R}/simulate.json simulations.<id>.conservation: " + ", ".join(f"{k}={v.get('value')}" for k, v in cons.items()) or "none"],
                    "an analysis created or lost energy/mass: its predictions are not evidence", "the analysis setup (boundaries, time step), never a fitted input", None))
    refs = {s: r["refinement"] for s, r in sims.items() if r.get("refinement")}
    single = [s.id for s in a.simulations if s.solver in ("calculix", "openfoam") and len(s.refinement) < 2 and (sims.get(s.id) or {}).get("status") == "ok"]
    gates.append(_g("refinement", "B", "Every prediction of a mesh ladder is resolved: all its levels finished and the grid-convergence index is within tolerance",
                    (all(v.get("ok") for v in refs.values())) if refs else None,
                    [f"{R}/simulate.json simulations.<id>.refinement.observables: " + "; ".join(f"{k}: " + ", ".join(_resolution(o, st) for o, st in (v.get("observables") or {}).items())
                                                                                              + (f" ({len(v['skipped'])} levels lost: {v['skipped'][0][:120]})" if v.get("skipped") else "")
                                                                                              for k, v in refs.items()) or "no mesh ladder",
                     "no discretisation estimate (one mesh level): " + (", ".join(single) or "none")],
                    "the prediction depends on the mesh: its discretisation error is unknown or above tolerance, so it supports no value",
                    "the refinement ladder (levels, regions, iterations) and mesh settings", {"unresolved": {k: v.get("unresolved") for k, v in refs.items() if v.get("unresolved")},
                                                                                              "no_estimate": single}))
    hy, rf, rc = ver.get("hygiene") or {}, ver.get("format") or {}, ver.get("lint") or {}
    gates.append(_g("source_hygiene", "C", "The assembly source imports only its declared inputs, formats and lints clean", bool(hy.get("ok") and rf.get("ok") and rc.get("ok")) if ver else None,
                    [f"{R}/verify.json hygiene: cad_refs={hy.get('cad_refs')} truth_refs={hy.get('truth_refs')}; {rf.get('tool', 'format')} {rf.get('ok')}, {rc.get('tool', 'lint')} {rc.get('ok')}"],
                    "the source reads files it must not, or is unformatted", "the assembly source", None))
    bd = dom.get("boundaries") or {}
    bad_b = {n: {"unassigned": b.get("unassigned"), "conflicts": b.get("conflicts")} for n, b in bd.items() if not b.get("ok")}
    gates.append(_g("boundaries_complete", "C", "Every face of a bounded body carries exactly one named boundary", (not bad_b) if bd else None,
                    [f"{R}/domains.json boundaries.<body>.unassigned/conflicts: {bad_b or 'none'}"], "an analysis would load a surface nobody named",
                    "boundary selectors in the contract (a drafting fix) or a missing face in the part", None))
    stamps = [s for s in ("verify", "kinematics", "domains", "simulate") if (actx.load_stage(s) or {}).get("provenance")]
    hashes = all(v.get("step_sha256") for v in designs.values()) if designs else not any(p.kind == "modelled" for p in actx.contract.parts)
    gates.append(_g("provenance", "C", "Stage JSONs carry provenance stamps; part handoffs are hash-bound; inputs carry provenance",
                    bool(hashes and len(stamps) == 4) if ver else None, [f"{R}/<stage>.json provenance present for {stamps}; parts.json designs.<d>.step_sha256 present: {hashes}"],
                    "an artefact cannot be traced to its inputs", "re-run the stage", None))
    truth_refs = hy.get("truth_refs") or []
    gates.append(_g("evidence_separation", "C", "No worker-visible artefact reads truth; the assembly source only places declared inputs",
                    (not truth_refs and bool(hy.get("ok"))) if ver else None, [f"{R}/verify.json hygiene.truth_refs = {truth_refs}"],
                    "evaluator truth leaked into the design", "remove the reference", None))
    failed = [g["id"] for g in gates if g["ok"] is False]
    passed = [g["id"] for g in gates if g["ok"] is True]
    na = [g["id"] for g in gates if g["ok"] is None]
    return {"ok": not failed and "parts_pass" in passed and "bom_complete" in passed, "summary": f"{len(passed)} pass, {len(failed)} fail, {len(na)} n/a",
            "passed": passed, "failed": failed, "not_applicable": na, "retryable_failed": [g for g in failed if g in RETRYABLE],
            "tier_a_failed": [g["id"] for g in gates if g["ok"] is False and g["tier"] == "A"], "gates": gates}


def correction_message(actx: AsmCtx, fb: dict[str, Any]) -> str:
    ver = actx.load_stage("verify") or {}
    kin = actx.load_stage("kinematics") or {}
    dom = actx.load_stage("domains") or {}
    fails = [ln for ln in verify_lines(ver) if ln.startswith("FAIL")]
    for n, m in (kin.get("motions") or {}).items():
        if not m.get("ok"):
            worst = max(m.get("poses") or [{}], key=lambda r: r.get("max_interference", 0))
            pair = max((worst.get("interference") or {"-": 0}).items(), key=lambda kv: kv[1])
            fails.append(f"FAIL motion {n}: max interference {m.get('max_interference'):.4g} mm3 at q = {worst.get('q')} ({pair[0]}); limit violations {m.get('limit_violations')}")
            loop = m.get("loop") or {}
            if loop.get("open_at") or loop.get("free"):
                fails.append(f"FAIL motion {n}: the loop does not close at q = {loop.get('open_at', [])[:6]} (worst {loop.get('closure_mm_max', 0):.4g} mm, "
                             f"{loop.get('closure_deg_max', 0):.3g} deg); joints the drive leaves free: {loop.get('free') or 'none'}")
    for n, t in (kin.get("transmissions") or {}).items():
        if not t.get("ok"):
            mesh = t.get("mesh") or {}
            fails.append(f"FAIL transmission {n}: ratio measured {t.get('ratio_measured')} vs {t.get('ratio')}; mesh max interference {mesh.get('max_interference')}, "
                         f"gap {mesh.get('gap_min')}..{mesh.get('gap_max')} (backlash max {mesh.get('backlash_max')}) {t.get('error') or ''}")
    for n, f in (dom.get("fluids") or {}).items():
        if not f.get("ok"):
            fails.append(f"FAIL fluid {n}: sealed={f.get('sealed')} leaks_to={f.get('leaks_to')} volume={f.get('volume')} check={f.get('volume_check')} "
                         f"agreement={f.get('agreement')} {f.get('error') or ''}")
    body = "\n".join(f"- {x}" for x in fails) or "- (see gate_feedback.json)"
    return f"""Correction for the assembly source `{actx.entry}`. The assembly gates failed: {', '.join(fb.get('failed') or [])}. Measured by the evaluator:

{body}

Fix the placements (and, for a fluid body, its booleans) in `{actx.entry}`; never rebuild a part.{f' Keep `{actx.part_dir / "placements.json"}` equal to the transforms in `{actx.entry.name}`.' if actx.kcl else ''} A gear on a meshed joint stays on its axis
(its radial bound is {jm.MESH_RADIAL_FRACTION:g} x the mesh's backlash_max): moving it off-axis to clear a tooth only makes it spin eccentrically, so a
mesh that interferes with the gears on their axes is a contract or part error (report it with the numbers), not a placement to change.
Re-run the critic until every line reads ok, open `assembly-views.png`, and report the new numbers."""

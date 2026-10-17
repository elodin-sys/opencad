"""Assembly verify: source hygiene, one engine build (STEP + STL + placements), every exported solid matched to a body and
agreed with its input STEP x placement, joint fidelity, static clearances, envelope and mass. Also the worker's critic
(`python -m opencad assembly check-source`), which runs the same checks into the order directory."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from opencad.assembly import AsmCtx
from opencad.assembly import joints as jm
from opencad.geomcheck import assembly as geo
from opencad.geomcheck import brep

VOLUME_MATCH_MAX_REL = 0.05  # a solid more than 5 % off a body's volume is not that body


def expected_bodies(actx: AsmCtx, placements: dict[str, np.ndarray]) -> dict[str, Any]:
    from opencad.truth.assembly_task import apply

    out = {}
    for p in actx.contract.parts:
        if not p.placed or p.role == "fluid" or p.name not in placements:
            continue
        src = actx.input_step(p.name)
        if src.exists():
            out[p.name] = apply(brep.read_step(src), placements[p.name])
    return out


def match(solids: list[Any], expected: dict[str, Any]) -> dict[str, int]:
    """Greedy lowest-cost assignment: volume mismatch plus COM distance over the assembly diagonal."""
    if not solids or not expected:
        return {}
    props = [brep.volume_props(s) for s in solids]
    lo = np.min([brep.bbox(s)[0] for s in solids], axis=0)
    hi = np.max([brep.bbox(s)[1] for s in solids], axis=0)
    diag = float(np.linalg.norm(hi - lo)) or 1.0
    cands = []
    for name, shape in expected.items():
        ep = brep.volume_props(shape)
        for i, p in enumerate(props):
            vol_rel = abs(p["volume"] - ep["volume"]) / abs(ep["volume"]) if ep["volume"] else 1.0
            if vol_rel > VOLUME_MATCH_MAX_REL:
                continue
            d = float(np.linalg.norm(np.subtract(p["center_of_mass"], ep["center_of_mass"])))
            cands.append((vol_rel + d / diag, name, i))
    out: dict[str, int] = {}
    used: set[int] = set()
    for _, name, i in sorted(cands):
        if name in out or i in used:
            continue
        out[name] = i
        used.add(i)
    return out


def _fluid_matches(actx: AsmCtx, solids: list[Any], used: set[int]) -> dict[str, int]:
    out = {}
    for fv in actx.contract.fluid_volumes:
        if fv.body is None:
            continue
        for i, s in enumerate(solids):
            if i not in used and brep.classify_points(s, [tuple(fv.seed)])[0] == "in":
                out[fv.body] = i
                used.add(i)
                break
    return out


def _derived_matches(actx: AsmCtx, solids: list[Any], used: set[int]) -> dict[str, int]:
    """Derived solid bodies (built in the source, no input STEP) take the remaining solids in the export's body order."""
    rest = [i for i in range(len(solids)) if i not in used]
    names = [p.name for p in actx.contract.parts if p.kind == "derived" and p.placed and p.role != "fluid"]
    return dict(zip(names, rest, strict=False))


def _compound(shapes: list[Any]):
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound

    comp = TopoDS_Compound()
    b = BRep_Builder()
    b.MakeCompound(comp)
    for s in shapes:
        b.Add(comp, s)
    return comp


def clearances(actx: AsmCtx, bodies: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for cl in actx.contract.acceptance.clearances:
        sides = []
        for side, other in ((cl.a, cl.b), (cl.b, cl.a)):
            if side == "all":
                sides.append(_compound([s for n, s in bodies.items() if n != other and actx.contract.part(n).role != "fluid"]))
            else:
                sides.append(bodies.get(side))
        if any(s is None for s in sides):
            out[cl.name] = {"ok": False, "error": f"body missing from the export ({cl.a}, {cl.b})"}
            continue
        out[cl.name] = {**geo.clearance(sides[0], sides[1], min_gap=cl.min_gap, max_gap=cl.max_gap, interference_tol=cl.interference_tolerance),
                        "a": cl.a, "b": cl.b}
    return out


def mass(actx: AsmCtx, bodies: dict[str, Any]) -> dict[str, Any]:
    from opencad.contract import load_contract
    from opencad.paths import design_dir

    total, moment, missing = 0.0, np.zeros(3), []
    for name, shape in bodies.items():
        p = actx.contract.part(name)
        if p.role == "fluid":
            continue
        rho = p.density_kg_m3
        if rho is None and p.kind == "modelled" and (design_dir(p.design) / "contract.yaml").exists():
            rho = load_contract(design_dir(p.design)).density_kg_m3
        if rho is None:
            missing.append(name)
            continue
        vp = brep.volume_props(shape)
        m = rho * vp["volume"] * 1e-9
        total += m
        moment += m * np.asarray(vp["center_of_mass"])
    out: dict[str, Any] = {"mass_kg": total, "center_of_mass": (moment / total).tolist() if total else None, "no_density": missing}
    acc = actx.contract.acceptance
    if acc.mass_kg is not None:
        ok, band = acc.mass_kg.within(total)
        out["mass_check"] = {"measured": total, "expected": acc.mass_kg.expected, "band": band, "ok": ok and not missing}
    if acc.center_of_mass is not None and out["center_of_mass"] is not None:
        ok, errs = acc.center_of_mass.within(tuple(out["center_of_mass"]))
        out["com_check"] = {"measured": out["center_of_mass"], "expected": list(acc.center_of_mass.expected), "errors": list(errs), "ok": ok}
    return out


def envelope(actx: AsmCtx, shape: Any) -> dict[str, Any]:
    lo, hi = brep.bbox(shape)
    env = actx.contract.envelope
    err = max(max(abs(a - b) for a, b in zip(lo, env.min)), max(abs(a - b) for a, b in zip(hi, env.max)))
    tol = actx.contract.bbox_tolerance
    return {"bbox_min": lo, "bbox_max": hi, "expected_min": list(env.min), "expected_max": list(env.max), "max_error": err, "tolerance": tol, "ok": err <= tol}


def allowed_stems(actx: AsmCtx) -> list[str]:
    return [p.design if p.kind == "modelled" else p.name for p in actx.contract.parts if p.kind != "derived"]


def source_checks(actx: AsmCtx) -> tuple[dict[str, Any], dict[str, Any]]:
    """(format, lint) of the assembly source: ruff for Python, `zoo kcl format` / `lint` on the KCL entry (not the nested part sources)."""
    if actx.kcl:
        from opencad.backends.zoo.engine import format_check, lint

        return {**format_check(actx.entry), "tool": "zoo kcl format"}, {**lint(actx.entry), "tool": "zoo kcl lint"}
    from opencad.backends.pythonlang import ruff_check, ruff_format_check

    return {**ruff_format_check(actx.part_dir), "tool": "ruff format"}, {**ruff_check(actx.part_dir), "tool": "ruff check"}


RIGID_TOL = 1e-5  # a placement rounded to six decimals is rigid; a 1e-4 scale moves a 100 mm body 0.01 mm


def rigidity_error(m: np.ndarray) -> float:
    """Largest deviation of a 4x4 placement from a rigid motion: R^T R = I, det R = +1, last row (0, 0, 0, 1)."""
    if m.shape != (4, 4):
        return float("inf")
    r = m[:3, :3]
    return float(max(np.abs(r.T @ r - np.eye(3)).max(), abs(np.linalg.det(r) - 1.0), np.abs(m[3] - [0.0, 0.0, 0.0, 1.0]).max()))


def evaluate(actx: AsmCtx, out_dir: Path) -> dict[str, Any]:
    """Every verify check; exports into out_dir (the stage's export/ or a critic scratch dir)."""
    from opencad.backends.local import write_step
    from opencad.backends.placements import read_joints, read_placements
    from opencad.truth import assembly_agree

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    res: dict[str, Any] = {"entry": str(actx.entry)}
    if not actx.entry.exists():
        return {**res, "ok": False, "program_executes": False, "error": f"{actx.entry} does not exist"}
    res["format"], res["lint"] = source_checks(actx)
    res["hygiene"] = (assembly_agree.kcl_hygiene if actx.kcl else assembly_agree.hygiene)(actx.part_dir, allowed_stems(actx))
    staged = {actx.input_step(p.name).name for p in actx.contract.parts if p.kind != "derived"}
    extra = sorted(f.name for f in actx.inputs_dir.glob("*") if f.is_file() and f.name not in staged) if actx.inputs_dir.exists() else []
    if extra:
        res["hygiene"] = {**res["hygiene"], "ok": False, "unstaged_inputs": extra}
    step, stl = out_dir / f"{actx.name}.step", out_dir / f"{actx.name}.stl"
    t0 = time.time()
    try:
        engine = actx.backend.engine
        built = (getattr(engine, "build_assembly", None) or engine.build)(actx.entry, analyze=False, step=step, stl=stl)
        res["program_executes"] = built.get("step") is not None
        res["build_s"] = round(time.time() - t0, 2)
    except Exception as e:  # a program that does not execute is the model's failure, recorded with its error
        return {**res, "ok": False, "program_executes": False, "error": f"{type(e).__name__}: {e}"[:4000]}
    if not step.exists():
        return {**res, "ok": False, "program_executes": False, "error": "the build wrote no STEP"}
    raw = read_placements(out_dir / "placements.json") or {}
    placements = {k: np.asarray(v, float) for k, v in raw.items()}
    for p in actx.contract.parts:
        if p.role == "fluid":
            placements.setdefault(p.name, np.eye(4))
    missing = [p.name for p in actx.contract.parts if p.placed and p.name not in placements]
    # agreement and joint fidelity apply the placement itself, so a scaled or sheared matrix would pass both: a body is moved, never resized
    non_rigid = {n: round(rigidity_error(m), 9) for n, m in placements.items() if rigidity_error(m) > RIGID_TOL}
    res["placements"] = {"bodies": sorted(raw), "missing": missing, "non_rigid": non_rigid, "ok": not missing and not non_rigid}
    shape = brep.read_step(step)
    solids = brep.solids(shape)
    expected_n = actx.contract.expected_solids()
    res["solid_count"] = {"measured": len(solids), "expected": expected_n, "ok": len(solids) == expected_n}
    expected = expected_bodies(actx, placements)
    matched = match(solids, expected)
    matched.update(_fluid_matches(actx, solids, set(matched.values())))
    matched.update(_derived_matches(actx, solids, set(matched.values())))
    bodies = {name: solids[i] for name, i in matched.items()}
    bodies_dir = out_dir / "bodies"
    bodies_dir.mkdir(parents=True, exist_ok=True)
    for name, s in bodies.items():
        write_step(s, bodies_dir / f"{name}.step", name)
    agree: dict[str, Any] = {}
    acc = actx.contract.acceptance
    for name, exp in expected.items():
        if name not in bodies:
            agree[name] = {"ok": False, "error": "no exported solid matches this body (volume within 5 %)"}
            continue
        ev, mv = brep.volume_props(exp)["volume"], brep.volume_props(bodies[name])["volume"]
        vol_rel = abs(mv - ev) / ev if ev else float("inf")
        haus = assembly_agree._hausdorff(bodies[name], exp)
        agree[name] = {"ok": vol_rel <= acc.agreement_volume_rel and haus <= acc.agreement_hausdorff, "volume_expected": ev, "volume_measured": mv,
                       "volume_rel": vol_rel, "volume_rel_max": acc.agreement_volume_rel, "hausdorff_mm": haus, "hausdorff_max_mm": acc.agreement_hausdorff}
    for p in actx.contract.parts:
        if p.kind == "derived" and p.placed and p.role != "fluid" and p.name not in bodies:
            agree[p.name] = {"ok": False, "error": "no exported solid is left for this derived body (one solid per body, in the brief's order)"}
        elif p.kind != "derived" and p.placed and p.name not in expected:
            agree[p.name] = {"ok": False, "error": f"no input STEP for {p.name} ({actx.input_step(p.name)}) or no placement"}
        if p.role == "fluid" and p.name not in bodies:
            agree[p.name] = {"ok": False, "error": "no exported solid contains the fluid volume's seed point"}
    res["agreement"] = {"ok": all(v["ok"] for v in agree.values()), "bodies": agree}
    fid = {}
    meshed = jm.mesh_bounds(actx.contract)
    for j in actx.contract.joints:
        if j.parent in placements and j.child in placements:
            fid[j.name] = jm.fidelity(j, placements[j.parent], placements[j.child], meshed.get(j.name))
        else:
            fid[j.name] = {"ok": False, "error": "parent or child has no placement"}
    res["joints"] = {"ok": all(v["ok"] for v in fid.values()), "joints": fid}
    declared = read_joints(out_dir / "joints.json")
    if declared:
        axes = jm.world_axes(actx.contract, placements) if not missing else {}
        res["declared_joints"] = {n: {"declared": d, "contract_axis": [axes[n][0].tolist(), axes[n][1].tolist()] if n in axes else None} for n, d in declared.items()}
    res["clearances"] = clearances(actx, bodies)
    res["envelope"] = envelope(actx, shape)
    res["mass"] = mass(actx, bodies)
    parts_ok = [res["format"].get("ok"), res["lint"].get("ok"), res["hygiene"].get("ok"), res["program_executes"], res["placements"]["ok"],
                res["solid_count"]["ok"], res["agreement"]["ok"], res["joints"]["ok"], all(c.get("ok") for c in res["clearances"].values()),
                res["envelope"]["ok"], (res["mass"].get("mass_check") or {}).get("ok", True), (res["mass"].get("com_check") or {}).get("ok", True)]
    res["ok"] = all(bool(x) for x in parts_ok)
    res["step"], res["stl"] = str(step), str(stl) if stl.exists() else None
    return res


def run(actx: AsmCtx) -> dict[str, Any]:
    import shutil

    exp = actx.results_dir / "export"
    if exp.exists():
        shutil.rmtree(exp)
    return evaluate(actx, exp)


def lines(res: dict[str, Any]) -> list[str]:
    """The critic's report: one line per check, FAIL first."""
    out: list[str] = []

    def add(ok: Any, text: str) -> None:
        out.append(f"{'ok  ' if ok else 'FAIL'} {text}")

    if res.get("error"):
        add(False, f"program: {res['error'][:600]}")
    for k in ("format", "lint"):
        if k in res:
            add(res[k].get("ok"), f"{res[k].get('tool', k)}: {(res[k].get('findings') or res[k].get('output') or '')!s:.300}")
    if "hygiene" in res:
        h = res["hygiene"]
        add(h.get("ok"), "hygiene: " + (f"result={h['has_result']} " if "has_result" in h else "")
            + f"placements={h.get('has_placements')} cad_refs={h.get('cad_refs')} truth_refs={h.get('truth_refs')}"
            + (f" files in inputs/ the evaluator did not stage (remove them): {h['unstaged_inputs']}" if h.get("unstaged_inputs") else ""))
    if "placements" in res:
        add(res["placements"]["ok"], f"placements for every body (missing {res['placements']['missing']})"
            + (f"; not rigid transforms (scale or shear, max deviation): {res['placements']['non_rigid']}" if res["placements"].get("non_rigid") else ""))
    if "solid_count" in res:
        add(res["solid_count"]["ok"], f"solid_count {res['solid_count']['measured']} expected {res['solid_count']['expected']}")
    for name, b in ((res.get("agreement") or {}).get("bodies") or {}).items():
        if "error" in b:
            add(False, f"agreement {name}: {b['error']}")
        else:
            add(b["ok"], f"agreement {name}: volume_rel {b['volume_rel']:.2e} (max {b['volume_rel_max']:.0e}) hausdorff {b['hausdorff_mm']:.4f} mm (max {b['hausdorff_max_mm']})")
    for name, j in ((res.get("joints") or {}).get("joints") or {}).items():
        if "error" in j:
            add(False, f"joint {name}: {j['error']}")
            continue
        parts = ", ".join(f"{k} {c['measured']:.4g}" + (f" (expected {c['expected']:.4g} +/- {c['max_error']})" if "expected" in c else f" (max {c['max']:.4g}"
                                                                                                                         + (f", {c['note']}" if c.get("note") else "") + ")")
                          for k, c in j["checks"].items())
        add(j["ok"], f"joint {name} ({j['kind']} {j['parent']} -> {j['child']}): {parts}")
    for name, c in (res.get("clearances") or {}).items():
        add(c.get("ok"), f"clearance {name} ({c.get('a')} / {c.get('b')}): interference {c.get('interference_volume', float('nan')):.4g} mm3, gap {c.get('gap', float('nan')):.4g} mm "
            f"(band {c.get('min_gap')}..{c.get('max_gap')})" if "error" not in c else f"clearance {name}: {c['error']}")
    if "envelope" in res:
        e = res["envelope"]
        add(e["ok"], f"envelope max error {e['max_error']:.4f} mm (tol {e['tolerance']}); measured {np.round(e['bbox_min'], 3).tolist()}..{np.round(e['bbox_max'], 3).tolist()}")
    for k in ("mass_check", "com_check"):
        c = (res.get("mass") or {}).get(k)
        if c:
            add(c["ok"], f"{k}: measured {c['measured']} expected {c['expected']}")
    out.sort(key=lambda s: not s.startswith("FAIL"))
    return out


def critic(name: str, *, ledger: Path | None = None, as_json: bool = False) -> int:
    """`python -m opencad assembly check-source <asm> --ledger <order>/engine-ledger.jsonl`: the assembly worker's critic."""
    from opencad.io import utc_now
    from opencad.truth.assembly_check import _render_views

    actx = AsmCtx.load(name)
    out_dir = (Path(ledger).parent if ledger else actx.results_dir) / "_check-export"
    t0 = time.time()
    res = evaluate(actx, out_dir)
    if ledger is not None:
        Path(ledger).parent.mkdir(parents=True, exist_ok=True)
        with Path(ledger).open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": utc_now(), "cmd": f"engine build step+stl {actx.entry}", "seconds": round(time.time() - t0, 2),
                                "ok": bool(res.get("program_executes")), "via": "assembly check-source"}) + "\n")
    if res.get("stl") or res.get("step"):
        views = _render_views(Path(res.get("stl") or res["step"]), (Path(ledger).parent if ledger else out_dir) / "assembly-views.png")
        if views:
            res["views"] = str(views)
    print(json.dumps(res, indent=2, default=str) if as_json else "\n".join([f"assembly check-source {'PASS' if res.get('ok') else 'FAIL'} ({name}, {actx.backend_id})", *lines(res)]
                                                                              + ([f"assembly-views: {res['views']}"] if res.get("views") else [])))
    return 0 if res.get("ok") else 1

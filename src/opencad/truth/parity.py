"""`python -m opencad.truth parity <case>`: evaluator-side audit of the worker-visible contract against the truth manifest.

The worker's critic (`quick` / `inspect`) and the truth scorer call the same geometry functions with the specs each side
declares. When the contract's spec differs from the observable's (a looser band, another endpoint, no volume band, no
`max_thickness`), the worker converges on numbers the scorer never checks. For every truth observable this module finds
the nearest contract acceptance item of the same kind and reports missing counterparts, looser tolerances, parameter
differences and endpoint drift. It also lists every scorecard that PASSED while the pipeline's own gates FAILED: the
pattern behind the seven contract-drafting defects of the bake-off. Truth stays scorer-side: the report goes to the
orchestrator (results/_bakeoff/parity/<case>.md), never into a worker brief.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import yaml

from opencad.contract import load_contract
from opencad.io import utc_now
from opencad.paths import BAKEOFF, TRUTH, design_dir
from opencad.schemas import PartContract
from opencad.truth.manifest import CaseManifest, Observable, case_dir

POINT_MATCH_MM = 0.5
SECTION_AT_MM = 0.05
PASSAGE_DRIFT_MM = 2.0
BACKENDS = ("cadquery", "build123d", "freecad", "zoo")


def manifest_root(case_id: str) -> Path:
    """The case directory in the tree, or its vault copy while a run holds it sequestered."""
    root = case_dir(case_id)
    if not (root / "manifest.yaml").exists():
        from opencad.truth.runner import vault_dirs

        for v in reversed(vault_dirs(case_id)):
            if (v / "manifest.yaml").exists():
                return v
    return root


def load_manifest_anywhere(case_id: str) -> CaseManifest:
    p = manifest_root(case_id) / "manifest.yaml"
    return CaseManifest.model_validate(yaml.safe_load(p.read_text(encoding="utf-8")))


def reference_integrity(m: CaseManifest, root: Path, contract: PartContract | None = None, design_dir: Path | None = None) -> dict[str, Any]:
    """Can the reference support the manifest's voxel observables, and does every passage endpoint and probe point
    lie where the observable says on the reference B-rep?

    The voron reference STL is a 31-shell, 802-open-edge export whose voxel flood fill leaks into the material;
    `passage_hotend_cavity` measured an 8439 mm3 "air path" through what the STEP classifies as solid. The B-rep
    is the arbiter: every truth passage endpoint must be `out` (air), void probes `out`, solid probes `in`.
    """
    from opencad.geomcheck import assembly, brep
    from opencad.geomcheck import mesh as meshcheck

    out: dict[str, Any] = {"mesh": None, "invalid": [], "contract_disagreements": [], "warnings": []}
    step = next((root / t.path for t in m.truth if t.path.lower().endswith((".step", ".stp"))), None)
    stl = next((root / t.path for t in m.truth if t.path.lower().endswith(".stl")), None)
    if stl is not None and stl.exists():
        a = meshcheck.analyze_mesh(stl)
        pitch = next((float(o.pitch) for o in m.observables if o.kind == "passage" and o.pitch), 0.5)
        fill = assembly._closed_grid(assembly._mesh_key(stl), pitch, None, 3)[4]
        out["mesh"] = {
            "path": stl.name,
            "watertight": a["watertight"],
            "components": a["components"],
            "open_edges": (a.get("open_edges") or {}).get("count"),
            "fill_ratio": fill["fill_ratio"],
            "leak": fill["leak"],
        }
        if fill["leak"]:
            out["warnings"].append(
                f"the reference mesh's voxel fill leaks ({fill['fill_ratio']:.2f} of the mesh volume filled, {out['mesh']['open_edges']} open edges): "
                "never author or recalibrate a passage / thickness band from it; measure on a watertight tessellation of the STEP"
            )
    if step is None or not step.exists():
        return out
    shape = brep.read_step(step)

    def classify(pts: list[list[float]]) -> list[str]:
        return brep.classify_points(shape, [list(map(float, p)) for p in pts])

    for o in m.observables:
        if o.kind == "passage" and o.point is not None and o.point_b is not None:
            states = classify([list(o.point), list(o.point_b)])
            if any(s != "out" for s in states):
                out["invalid"].append(
                    {
                        "observable": o.id,
                        "detail": f"passage endpoints classify {states} on the reference B-rep; an air path needs both `out`",
                    }
                )
        elif o.kind == "probe" and o.points:
            want = "out" if o.state == "void" else "in"
            bad = [(p, s) for p, s in zip(o.points, classify([list(p) for p in o.points])) if s != want]
            if bad:
                out["invalid"].append(
                    {
                        "observable": o.id,
                        "detail": f"{len(bad)}/{len(o.points)} {o.state} probe points are not `{want}` on the reference B-rep: {bad[:4]}",
                    }
                )
    if contract is not None:
        for p in contract.acceptance.passages:
            states = classify([list(p.point_a), list(p.point_b)])
            if any(s != "out" for s in states):
                out["contract_disagreements"].append(
                    {"item": f"passages/{p.name}", "detail": f"endpoints classify {states} on the reference B-rep"}
                )
        for pr in contract.acceptance.probes:
            want = "out" if pr.state == "void" else "in"
            bad = [(list(p), s) for p, s in zip(pr.points, classify([list(p) for p in pr.points])) if s != want]
            if bad:
                out["contract_disagreements"].append(
                    {
                        "item": f"probes/{pr.name}",
                        "detail": f"{len(bad)}/{len(pr.points)} {pr.state} points are not `{want}` on the reference: {bad[:4]}",
                    }
                )
        leak = bool((out.get("mesh") or {}).get("leak"))
        fails = contract_items_the_reference_fails(step, stl, contract, design_dir)
        if leak:  # passage / thickness values on a leaking mesh are not measurements; the mesh warning already says so
            fails = [f for f in fails if not f.startswith(("passages/", "thickness/"))]
        out["reference_fails"] = fails
        for item in fails:
            out["contract_disagreements"].append({"item": item, "detail": "the reference itself fails this contract item: a drafting defect"})
    return out


def contract_items_the_reference_fails(step: Path, stl: Path | None, contract: PartContract, design_dir: Path | None) -> list[str]:
    """Run the worker's own critic (inspect.measure) on the reference: every failing `kind/name` is a contract item the design
    it was drafted from does not satisfy. Voron's chamber items and Prusa's summed flank face were both of this kind."""
    from opencad.stages import inspect_stage

    try:
        m = inspect_stage.measure(step, stl if stl is not None and stl.exists() else None, contract, design_dir or step.parent)
    except Exception as e:  # noqa: BLE001 - the audit reports, it never raises for one bad reference
        return [f"<measure error: {str(e)[:120]}>"]
    kinds = ("sections", "faces", "cylinders", "planes", "dimensions", "passages", "thickness", "probes", "cylinder_counts", "solids", "clearances")
    return [f"{k}/{n}" for k in kinds for n, x in (m.get(k) or {}).items() if isinstance(x, dict) and not x.get("ok")]


def _dist(a: list[float] | tuple, b: list[float] | tuple) -> float:
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def _unit(v: list[float] | tuple) -> list[float]:
    n = math.sqrt(sum(float(x) ** 2 for x in v)) or 1.0
    return [float(x) / n for x in v]


def _axis_offset(point: list[float], direction: list[float], other_point: list[float]) -> float:
    d = _unit(direction)
    w = [float(o) - float(p) for o, p in zip(other_point, point)]
    t = sum(wi * di for wi, di in zip(w, d))
    return _dist(w, [t * di for di in d])


def _parallel(a: list[float], b: list[float]) -> bool:
    ua, ub = _unit(a), _unit(b)
    return abs(sum(x * y for x, y in zip(ua, ub))) > 0.9998


def _finding(o: Observable, status: str, counterpart: str | None, detail: str) -> dict[str, Any]:
    return {
        "observable": o.id,
        "kind": o.kind,
        "required": o.required,
        "status": status,
        "counterpart": counterpart,
        "detail": detail,
    }


def _passage_endpoint_drift(o: Observable, p) -> float:
    a, b = list(o.point or []), list(o.point_b or [])
    straight = _dist(a, p.point_a) + _dist(b, p.point_b)
    crossed = _dist(a, p.point_b) + _dist(b, p.point_a)
    return min(straight, crossed) / 2


def _audit_passage(o: Observable, c: PartContract) -> dict[str, Any]:
    if not c.acceptance.passages:
        return _finding(o, "missing", None, "the contract declares no passages")
    best = min(c.acceptance.passages, key=lambda p: _passage_endpoint_drift(o, p))
    drift = _passage_endpoint_drift(o, best)
    if drift > 15.0:
        return _finding(
            o,
            "missing",
            None,
            f"no contract passage within 15 mm of the truth endpoints (nearest `{best.name}`, mean endpoint drift {drift:.1f} mm)",
        )
    diffs: list[str] = []
    if drift > PASSAGE_DRIFT_MM:
        diffs.append(
            f"endpoints drift {drift:.1f} mm ({list(best.point_a)}->{list(best.point_b)} vs truth {list(o.point)}->{list(o.point_b)})"
        )
    if bool(best.expect_connected) != bool(o.expect_connected):
        diffs.append(f"expect_connected {best.expect_connected} vs truth {o.expect_connected}")
    t_pitch = o.pitch or 0.5
    if best.pitch > t_pitch + 1e-9:
        diffs.append(f"pitch {best.pitch} coarser than truth {t_pitch}")
    looser: list[str] = []
    if best.plugs and not o.plugs:
        # plugs the scorer does not paint hide every leak they cover (the voron left inlet passed the critic, failed the scorer)
        looser.append(f"sealing: the contract plugs {len(best.plugs)} ports the truth leaves to the closing radius alone (seal_radius {o.seal_radius})")
    elif (o.seal_radius is not None) != (best.seal_radius is not None) or bool(o.plugs) != bool(best.plugs):
        diffs.append(
            f"sealing: contract seal_radius={best.seal_radius} plugs={len(best.plugs)} vs truth seal_radius={o.seal_radius} plugs={len(o.plugs or [])}"
        )
    if (o.volume_min is not None or o.volume_max is not None) and best.volume_min is None and best.volume_max is None:
        looser.append(f"truth bands the air volume [{o.volume_min}, {o.volume_max}]; the contract reports it unbanded")
    elif (o.volume_min is not None and best.volume_min is not None and best.volume_min < o.volume_min - 1e-6) or (
        o.volume_max is not None and best.volume_max is not None and best.volume_max > o.volume_max + 1e-6
    ):
        looser.append(f"volume band [{best.volume_min}, {best.volume_max}] wider than truth [{o.volume_min}, {o.volume_max}]")
    status = "looser" if looser else ("params" if diffs else "ok")
    return _finding(o, status, best.name, "; ".join(looser + diffs) or "same endpoints, sealing, pitch and band class")


def _audit_section(o: Observable, c: PartContract) -> dict[str, Any]:
    match = next(
        (s for s in c.acceptance.sections if s.plane == o.plane and abs(float(s.at) - float(o.at)) <= SECTION_AT_MM),
        None,
    )
    if match is None:
        return _finding(o, "missing", None, f"no contract section at {o.plane}={o.at}")
    diffs: list[str] = []
    exp = o.expected if isinstance(o.expected, dict) else {}
    t_tol = o.area_tolerance_rel if o.area_tolerance_rel is not None else 0.01
    if (
        (exp.get("area") is not None or o.from_ is not None)
        and match.expect.area is not None
        and match.expect.area_tolerance_rel > t_tol + 1e-9
    ):
        diffs.append(f"area band {match.expect.area_tolerance_rel:.0%} looser than truth {t_tol:.0%}")
    if (exp.get("area") is not None or o.from_ is not None) and match.expect.area is None:
        diffs.append("truth checks the area; the contract declares none")
    for k in ("loops", "holes"):
        if exp.get(k) is not None and getattr(match.expect, k) is None:
            diffs.append(f"truth checks {k}={exp[k]}; the contract does not")
        elif exp.get(k) is not None and getattr(match.expect, k) != exp[k]:
            diffs.append(f"{k}: contract {getattr(match.expect, k)} vs truth {exp[k]}")
    return _finding(o, "looser" if diffs else "ok", match.id, "; ".join(diffs) or "same station, band and topology")


def _audit_thickness(o: Observable, c: PartContract) -> dict[str, Any]:
    if not c.acceptance.thickness:
        return _finding(o, "missing", None, "the contract declares no wall-thickness check")
    stat = o.stat or "p05"
    cands = [t for t in c.acceptance.thickness if t.stat == stat] or list(c.acceptance.thickness)
    if o.region:
        cands.sort(key=lambda t: 0 if t.region else 1)
    match = cands[0]
    diffs: list[str] = []
    if match.min < float(o.min) - 1e-9:
        diffs.append(f"min {match.min} below truth {o.min}")
    if o.max_thickness is not None and match.max_thickness is None:
        diffs.append(
            f"truth drops rays longer than {o.max_thickness} mm (max_thickness); the contract keeps them, so its p05 reads higher"
        )
    if match.stat != stat:
        diffs.append(f"stat {match.stat} vs truth {stat}")
    if bool(o.region) != bool(match.region):
        diffs.append(f"region: contract {match.region} vs truth {o.region}")
    return _finding(o, "params" if diffs else "ok", match.name, "; ".join(diffs) or "same stat, min and ray filter")


def _audit_cylinder(o: Observable, c: PartContract) -> dict[str, Any]:
    r = float(o.radius)
    cands = []
    for cy in c.acceptance.cylinders:
        cr = cy.radius if cy.radius is not None else (cy.diameter / 2 if cy.diameter else None)
        if cr is None or abs(cr - r) > 0.15 or not _parallel(list(cy.direction), list(o.direction)):
            continue
        cands.append((_axis_offset(list(cy.point), list(cy.direction), list(o.point)), cy))
    if not cands:
        return _finding(
            o, "missing", None, f"no contract cylinder r={r} on an axis through {o.point} along {o.direction}"
        )
    off, match = min(cands, key=lambda x: x[0])
    if off > POINT_MATCH_MM:
        return _finding(
            o, "missing", match.name, f"nearest r={r} cylinder `{match.name}` is {off:.2f} mm off the truth axis"
        )
    diffs: list[str] = []
    if o.length is not None and match.length is None and match.t_range is None:
        diffs.append(f"truth checks length {o.length}±{o.length_tolerance or 0.05}; the contract has no length/t_range")
    t_axis = o.tolerance if o.tolerance is not None else 0.05
    if match.axis_tolerance is not None and match.axis_tolerance > t_axis + 1e-9:
        diffs.append(f"axis tolerance {match.axis_tolerance} looser than truth {t_axis}")
    t_rad = o.radius_tolerance if o.radius_tolerance is not None else 0.05
    if match.radius_tolerance > t_rad + 1e-9:
        diffs.append(f"radius tolerance {match.radius_tolerance} looser than truth {t_rad}")
    return _finding(o, "looser" if diffs else "ok", match.name, "; ".join(diffs) or "same axis, radius and bands")


def _audit_face(o: Observable, c: PartContract) -> dict[str, Any]:
    cands = [
        f
        for f in c.acceptance.faces
        if f.plane == o.plane and abs(float(f.at) - float(o.at)) <= SECTION_AT_MM and f.normal == o.normal
    ]
    if not cands:
        return _finding(o, "missing", None, f"no contract face on {o.plane}={o.at} normal {o.normal}")
    if o.center is not None:
        cands.sort(key=lambda f: _dist(f.center, o.center) if f.center is not None else 1e9)
    if o.mode == "sum":  # a summed observable is answered by the contract's summed face on that plane when there is one
        cands.sort(key=lambda f: 0 if f.mode == "sum" else 1)
    match = cands[0]
    diffs: list[str] = []
    t_tol = o.area_tolerance_rel if o.area_tolerance_rel is not None else 0.01
    if o.expected is not None and match.area is None:
        diffs.append("truth checks the area; the contract does not")
    elif o.expected is not None and match.area_tolerance_rel > t_tol + 1e-9:
        diffs.append(f"area band {match.area_tolerance_rel:.0%} looser than truth {t_tol:.0%}")
    if o.mode == "sum" and match.mode != "sum":
        diffs.append("truth sums every coplanar hit (mode sum); the contract matches one face")
    elif o.mode == "sum" and o.tolerance is not None and match.tolerance is not None and match.tolerance < o.tolerance - 1e-9:
        # a summed face with a NARROWER plane window is the looser check: slivers the scorer adds to the sum are invisible to the gate
        diffs.append(f"plane window {match.tolerance:g} mm narrower than truth {o.tolerance:g} mm on a summed face (the scorer sums slivers the gate ignores)")
    return _finding(o, "looser" if diffs else "ok", match.name, "; ".join(diffs) or "same plane, normal and band")


def _audit_probe(o: Observable, c: PartContract) -> dict[str, Any]:
    pts = [list(p) for p in (o.points or [])]
    best, best_d = None, 1e9
    for pr in c.acceptance.probes:
        if pr.state != o.state:
            continue
        d = max(min(_dist(tp, cp) for cp in pr.points) for tp in pts)
        if d < best_d:
            best, best_d = pr, d
    if best is None or best_d > 3.0:
        return _finding(o, "missing", best.name if best else None, f"no contract {o.state} probe within 3 mm of {pts}")
    return _finding(
        o, "ok" if best_d <= POINT_MATCH_MM else "params", best.name, f"nearest contract probe {best_d:.2f} mm away"
    )


def _audit_scalar(o: Observable, c: PartContract) -> dict[str, Any]:
    a = c.acceptance
    if o.kind == "bbox_size":
        return _finding(
            o, "ok", "envelope", f"contract envelope tolerance {c.envelope.tolerance}; truth ±{o.tolerance}"
        )
    q = {"volume": a.volume, "surface_area": a.surface_area, "center_of_mass": a.center_of_mass}.get(o.kind)
    if q is None:
        return _finding(o, "missing" if o.required else "info", None, f"the contract declares no {o.kind} band")
    if o.kind == "center_of_mass":
        return _finding(o, "ok", o.kind, f"contract tolerance {getattr(q, 'tolerance', None)}; truth ±{o.tolerance}")
    t_rel = o.tolerance_rel
    c_rel = q.tolerance_rel if q.tolerance_rel is not None else (q.tolerance / q.expected if q.expected else None)
    if t_rel is not None and c_rel is not None and c_rel > t_rel + 1e-9:
        return _finding(o, "looser", o.kind, f"band {c_rel:.2%} looser than truth {t_rel:.2%}")
    return _finding(o, "ok", o.kind, f"contract band {c_rel}; truth {t_rel or o.tolerance}")


def _audit_solid_count(o: Observable, c: PartContract) -> dict[str, Any]:
    exp = int(o.expected) if o.expected is not None else 1
    ok = c.acceptance.solid_count == exp
    return _finding(o, "ok" if ok else "params", "solid_count", f"contract {c.acceptance.solid_count} vs truth {exp}")


def _audit_deviation(o: Observable, c: PartContract) -> dict[str, Any]:
    if c.acceptance.deviation is None:
        return _finding(
            o,
            "info",
            None,
            f"scorer-only mesh comparison against `{o.reference}` (p95<={o.p95_max}, hausdorff<={o.hausdorff_max}, IoU>={o.silhouette_iou_min}); "
            "the design bundle has no reference mesh, so the worker never sees this number. Input renders are the worker-visible proxy (view-compare.png).",
        )
    return _finding(o, "ok", "acceptance.deviation", "the contract declares a deviation band")


AUDITORS = {
    "passage": _audit_passage,
    "section": _audit_section,
    "thickness": _audit_thickness,
    "cylinder": _audit_cylinder,
    "face": _audit_face,
    "probe": _audit_probe,
    "volume": _audit_scalar,
    "surface_area": _audit_scalar,
    "center_of_mass": _audit_scalar,
    "bbox_size": _audit_scalar,
    "solid_count": _audit_solid_count,
    "deviation": _audit_deviation,
    "not_matching": _audit_deviation,
}


def audit(m: CaseManifest, c: PartContract) -> list[dict[str, Any]]:
    out = []
    for o in m.observables:
        fn = AUDITORS.get(o.kind)
        out.append(
            fn(o, c) if fn else _finding(o, "info", None, f"kind {o.kind} is not audited (checked by the scorer only)")
        )
    return out


def gate_scorecard_mismatches(case_id: str | None = None) -> list[dict[str, Any]]:
    """Every (case, arm, backend) whose latest scorecard PASSED while the pipeline gates it embeds FAILED."""
    rows = []
    cases = [case_dir(case_id)] if case_id else sorted(p for p in (TRUTH / "cases").iterdir() if p.is_dir())
    for cd in cases:
        for card_p in sorted((cd / "scorecards").glob("*@*-latest.json")) if (cd / "scorecards").exists() else []:
            try:
                card = json.loads(card_p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            pg = card.get("pipeline_gates") or {}
            if card.get("verdict") == "PASS" and pg and pg.get("ok") is False:
                arm, _, rest = card_p.stem.partition("@")
                backend = rest.removesuffix("-latest")
                rows.append(
                    {
                        "case": cd.name,
                        "arm": arm,
                        "backend": backend,
                        "failed_gates": pg.get("failed") or [],
                        "scorecard": str(card_p),
                    }
                )
    return rows


def write_report(
    case_id: str,
    findings_by_design: dict[str, list[dict[str, Any]]],
    mismatches: list[dict[str, Any]],
    out: Path | None = None,
    integrity: dict[str, dict[str, Any]] | None = None,
) -> Path:
    out = out or (BAKEOFF / "parity" / f"{case_id}.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    intro = (
        f"Generated {utc_now()} by `python -m opencad.truth parity {case_id}`. Evaluator-side: compares the truth manifest's "
        "observables with the worker-visible contract. Never hand this file to a worker; fix the contract (tighten, never relax) with a calibration-log entry."
    )
    lines = [f"# Parity — {case_id}", "", intro, ""]
    for design, integ in (integrity or {}).items():
        lines += [f"## Reference integrity ({design})", ""]
        mesh = integ.get("mesh")
        if mesh:
            lines.append(
                f"Reference mesh `{mesh['path']}`: watertight {mesh['watertight']}, {mesh['components']} shells, {mesh['open_edges']} open edges, "
                f"voxel fill ratio {mesh['fill_ratio']:.2f}{' — LEAK' if mesh['leak'] else ''}."
            )
        if integ["invalid"]:
            lines += [
                "",
                "Truth observables the reference B-rep contradicts (a truth defect: log it in truth/calibration-log.yaml and fix the manifest):",
                "",
            ]
            lines += [f"- **{r['observable']}**: {r['detail']}" for r in integ["invalid"]]
        if integ["contract_disagreements"]:
            lines += ["", "Contract items the reference B-rep contradicts (fix the contract):", ""]
            lines += [f"- **{r['item']}**: {r['detail']}" for r in integ["contract_disagreements"]]
        if not integ["invalid"] and not integ["contract_disagreements"]:
            lines.append("Every passage endpoint and probe point agrees with the reference B-rep.")
        lines += [f"- Warning: {w}" for w in integ.get("warnings") or []]
        lines.append("")
    for design, findings in findings_by_design.items():
        counts = {}
        for f in findings:
            counts[f["status"]] = counts.get(f["status"], 0) + 1
        lines += [
            f"## designs/{design}/contract.yaml",
            "",
            "Status counts: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())),
            "",
            "| observable | kind | req | status | contract item | detail |",
            "|---|---|---|---|---|---|",
        ]
        for f in findings:
            if f["status"] in ("ok", "invalid", "contract-vs-reference"):  # the last two are in the integrity section
                continue
            lines.append(
                f"| {f['observable']} | {f['kind']} | {'yes' if f['required'] else 'no'} | **{f['status']}** | {f['counterpart'] or '-'} | {f['detail']} |"
            )
        oks = [f["observable"] for f in findings if f["status"] == "ok"]
        if oks:
            lines += ["", f"Matched with equal or tighter bands: {', '.join(oks)}"]
        lines.append("")
    lines += ["## Scorecard PASS while pipeline gates FAIL", ""]
    if mismatches:
        lines += ["| case | arm | backend | failed gates |", "|---|---|---|---|"]
        lines += [f"| {r['case']} | {r['arm']} | {r['backend']} | {', '.join(r['failed_gates'])} |" for r in mismatches]
    else:
        lines.append("none")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def run(
    case_id: str, *, out: Path | None = None, corpus_mismatches: bool = False, integrity: bool = True
) -> tuple[Path, dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    root = manifest_root(case_id)
    m = load_manifest_anywhere(case_id)
    findings_by_design: dict[str, list[dict[str, Any]]] = {}
    integ: dict[str, dict[str, Any]] = {}
    for arm in m.arms:
        cp = design_dir(arm.design) / "contract.yaml"
        if arm.design in findings_by_design or not cp.exists():
            continue
        c = load_contract(cp)
        findings_by_design[arm.design] = audit(m, c)
        if integrity:
            integ[arm.design] = reference_integrity(m, root, c, design_dir(arm.design))
            for r in integ[arm.design]["invalid"]:
                findings_by_design[arm.design].append(
                    {
                        "observable": r["observable"],
                        "kind": "reference",
                        "required": True,
                        "status": "invalid",
                        "counterpart": None,
                        "detail": r["detail"],
                    }
                )
            for r in integ[arm.design]["contract_disagreements"]:
                findings_by_design[arm.design].append(
                    {
                        "observable": r["item"],
                        "kind": "reference",
                        "required": True,
                        "status": "contract-vs-reference",
                        "counterpart": r["item"],
                        "detail": r["detail"],
                    }
                )
    mismatches = gate_scorecard_mismatches(None if corpus_mismatches else case_id)
    return write_report(case_id, findings_by_design, mismatches, out, integrity=integ), findings_by_design, mismatches


def format_summary(findings_by_design: dict[str, list[dict[str, Any]]], mismatches: list[dict[str, Any]]) -> str:
    lines = []
    for design, findings in findings_by_design.items():
        bad = [f for f in findings if f["status"] not in ("ok", "info")]
        lines.append(f"{design}: {len(findings)} observables, {len(bad)} need a contract fix")
        for f in bad:
            lines.append(
                f"  {f['status']:8} {f['kind']:10} {f['observable']} -> {f['counterpart'] or '-'}: {f['detail']}"
            )
        for f in findings:
            if f["status"] == "invalid":
                lines.append(f"  TRUTH DEFECT {f['observable']}: fix the manifest with a calibration-log entry")
    lines.append(
        f"scorecard PASS / gates FAIL: {len(mismatches)}"
        + ("" if not mismatches else " (" + ", ".join(f"{r['case']}@{r['backend']}" for r in mismatches[:8]) + ")")
    )
    return "\n".join(lines)

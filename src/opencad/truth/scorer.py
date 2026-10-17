"""Score a produced design against sequestered truth. Only this module reads truth files."""

from __future__ import annotations

import math
import statistics
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from opencad.geomcheck import brep, gears, mesh as meshcheck, multibody
from opencad.geomcheck.features import assign_coplanar
from opencad.truth.extra_kinds import ExtraScorer
from opencad.io import dump_json, load_json, provenance, sha256_file, sha256_tree, utc_now
from opencad.backends.registry import current_id, get
from opencad.paths import design_dir, part_dir, results_dir
from opencad.schemas import FaceSpec
from opencad.truth.manifest import CaseManifest, Observable, case_dir
from opencad import __version__

SCORER_VERSION = "4"  # 3: cylinder / cylinder_count / plane; 4: solid, clearance, passage, thickness, probe, teeth, gear_mesh, solid-scoped sections
DEVIATION_SAMPLES = 20000
DEVIATION_SEED = 0


class ScoreError(RuntimeError):
    pass


def step_to_mesh(step_path: Path, out_path: Path, deflection: float = 0.02) -> Path:
    """Tessellate a STEP with OpenCascade into an STL (for deviation metrics against STEP truth)."""
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    shape = brep.read_step(step_path)
    BRepMesh_IncrementalMesh(shape, deflection, False, 0.2, True)
    w = StlAPI_Writer()
    w.ASCIIMode = False
    w.Write(shape, str(out_path))
    return out_path


def _truth_measure(case: Path, o: Observable) -> Any:
    f = case / o.from_.file
    if f.suffix.lower() in (".step", ".stp"):
        a = brep.analyze_step(f)
        shape = brep.read_step(f)
    else:
        a = meshcheck.analyze_mesh(f)
        shape = None
    m = o.from_.measure
    if m == "bbox_size":
        return [h - l for l, h in zip(a["bbox_min"], a["bbox_max"])]
    if m == "bbox":
        return {"min": a["bbox_min"], "max": a["bbox_max"]}
    if m == "section":
        if shape is not None:
            r = brep.section(shape, o.plane, o.at)
        else:
            from opencad.reference.mesh import load_mesh, section as mesh_section

            r = mesh_section(load_mesh(f), o.plane, o.at)
        return {"area": r["area"], "loops": r["loops"], "holes": r["holes"]}
    return a[m]


def _rel_ok(measured: float, expected: float, o: Observable) -> tuple[bool, float]:
    err = abs(measured - expected)
    band = o.tolerance if o.tolerance is not None else abs(expected) * (o.tolerance_rel or 0.0)
    return err <= band, band


def score_case(case_id: str, m: CaseManifest, arm_id: str, *, case_root: Path | None = None) -> dict[str, Any]:
    """`case_root` points at the case files (manifest, truth/): the live tree, or the vault while another run still holds the case."""
    arm = next((a for a in m.arms if a.id == arm_id), None)
    if arm is None:
        raise ScoreError(f"arm {arm_id} not in manifest")
    case = Path(case_root) if case_root is not None else case_dir(case_id)
    design = arm.design
    results = results_dir(design) / "ecr" / arm.ecr if arm.ecr else results_dir(design)
    fb = load_json(results / "gate_feedback.json") if (results / "gate_feedback.json").exists() else {}
    step = results / "handoff" / f"{design}.step"
    stl = results / "handoff" / f"{design}.stl"
    if not step.exists():
        raise ScoreError(
            f"no handoff STEP at {step}; run the pipeline first"
            + (f" (`python -m opencad ecr {design} ... --label {arm.ecr}`)" if arm.ecr else "")
        )
    checks = score_checks(case, m, step, stl if stl.exists() else None)
    required = [c for c in checks if c["required"]]
    verdict = "PASS" if all(c.get("ok") for c in required) else "FAIL"
    card = {
        "case": case_id,
        "arm": arm_id,
        "design": design,
        "ecr": arm.ecr,
        "results_dir": str(results),
        "truth_class": m.truth_class,
        "role": m.role,
        "scored_at": utc_now(),
        "verdict": verdict,
        "accuracy_score": accuracy_score({"checks": checks}, m),
        "summary": summarize_checks(checks),
        "checks": checks,
        "pipeline_gates": {"ok": fb.get("ok"), "summary": fb.get("summary"), "failed": fb.get("failed")},
        "downstream_targets": [t.model_dump() for t in m.downstream_targets],
        "hash_binding": {
            "manifest_sha256": sha256_file(case / "manifest.yaml"),
            "truth_files": {t.path: t.sha256 for t in m.truth},
            "input_files": {i.path: i.sha256 for i in m.inputs},
            "source": sha256_tree(part_dir(design), get().language.suffixes) if part_dir(design).exists() else {},
            "kcl": sha256_tree(part_dir(design), (".kcl",)) if part_dir(design).exists() else {},
            "step_sha256": sha256_file(step),
            "design_bundle": sha256_tree(design_dir(design) / "ecr" / arm.ecr if arm.ecr else design_dir(design)),
            "metrics": {
                "silhouette_px_long": 2400,
                "deviation_samples": DEVIATION_SAMPLES,
                "seed": DEVIATION_SEED,
                "scorer_version": SCORER_VERSION,
                "opencad_version": __version__,
            },
        },
        "provenance": provenance(),
    }
    from opencad.truth.runner import case_file, case_lock

    stamp = card["scored_at"].replace(":", "").replace("-", "")
    be = current_id()
    card["backend"] = be
    with case_lock(case_id):
        out_dir = case_file(case_id, "scorecards", tree=case_dir(case_id))
        out_dir.mkdir(parents=True, exist_ok=True)
        dump_json(out_dir / f"{arm_id}@{be}-{stamp}.json", card)
        dump_json(out_dir / f"{arm_id}@{be}-latest.json", card)
    return card


def _headroom(err: float, tol: float | None) -> float:
    if not tol:
        return 1.0 if not err else 0.0
    return max(0.0, 1.0 - abs(err) / tol)


def _check_headroom(c: dict[str, Any], o: Observable | None) -> float:
    """Tolerance-normalized closeness of one required check. A failed check scores 0; categorical checks score 1 or 0."""
    if not c.get("ok"):
        return 0.0
    k = c.get("kind")
    if o is None:
        return 1.0
    if k == "bbox_size":
        return _headroom(max(abs(a - b) for a, b in zip(c["measured"], c["expected"])), o.tolerance)
    if k in ("volume", "surface_area", "dimension"):
        return _headroom(c.get("error") or 0.0, c.get("band"))
    if k == "center_of_mass":
        return _headroom(max(abs(a - b) for a, b in zip(c["measured"], c["expected"])), o.tolerance)
    if k == "section":
        exp = o.expected or {}
        sub: list[float] = []
        if exp.get("area") is not None and o.area_tolerance_rel:
            sub.append(_headroom(c["measured"]["area"] - exp["area"], o.area_tolerance_rel * exp["area"]))
        sub += [
            1.0 if c["measured"].get(x) == exp.get(x) else 0.0 for x in ("loops", "holes") if exp.get(x) is not None
        ]
        return statistics.fmean(sub) if sub else 1.0
    if k == "face" and c.get("expected_area") is not None and o.area_tolerance_rel:
        return _headroom(c["area"] - c["expected_area"], o.area_tolerance_rel * c["expected_area"])
    if k == "plane" and c.get("expected") is not None and o.area_tolerance_rel:
        return _headroom(c["measured"] - c["expected"], o.area_tolerance_rel * c["expected"])
    if k == "cylinder":
        axis_max = (c.get("checks") or {}).get("axis", {}).get("max", o.tolerance)
        sub = [
            _headroom(c.get("axis_offset") or 0.0, axis_max),
            _headroom(c.get("radius_error") or 0.0, o.radius_tolerance),
        ]
        if o.length and isinstance(c.get("measured"), dict) and c["measured"].get("length") is not None:
            sub.append(_headroom(c["measured"]["length"] - o.length, o.length_tolerance))
        return statistics.fmean(sub)
    if k == "probe":
        want = "in" if c.get("expected") == "solid" else "out"
        measured = c.get("measured") or []
        return sum(1 for v in measured if v == want) / len(measured) if measured else 0.0
    return 1.0


def accuracy_score(card: dict[str, Any], manifest: CaseManifest) -> float:
    """Mean closeness of the required checks, 0-100. Optional checks (deviation) stay out of the score; verdicts are unchanged."""
    obs = {o.id: o for o in manifest.observables}
    scores = [_check_headroom(c, obs.get(c["id"])) for c in card.get("checks") or [] if c.get("required")]
    return round(100 * statistics.fmean(scores), 2) if scores else 0.0


def summarize_checks(checks: list[dict[str, Any]]) -> dict[str, int]:
    required = [c for c in checks if c["required"]]
    return {
        "required_pass": sum(1 for c in required if c.get("ok")),
        "required_total": len(required),
        "optional_pass": sum(1 for c in checks if not c["required"] and c.get("ok")),
        "optional_total": sum(1 for c in checks if not c["required"]),
    }


def score_checks(case: Path, m: CaseManifest, step: Path, stl: Path | None) -> list[dict[str, Any]]:
    """Evaluate every manifest observable against a STEP (and optional STL) in absolute mm; no rescaling, no alignment."""
    shape = brep.read_step(step)
    cand = brep.analyze_step(step)
    checks: list[dict[str, Any]] = []
    tmp = Path(tempfile.mkdtemp(prefix="opencad-score-"))
    face_results = _score_faces(shape, [o for o in m.observables if o.kind == "face"])
    cyls: list[dict[str, Any]] | None = None
    extra = ExtraScorer(case, m, shape, stl if stl is not None and stl.exists() else None)
    solid_points = {o.id: list(o.point) for o in m.observables if o.kind == "solid" and o.point is not None}

    def scoped(o: Observable):
        """The named solid's body when the observable is scoped to one, else the whole shape."""
        if o.solid:
            body = multibody.select_solid(shape, solid_points[o.solid])
            if body is None:
                raise ScoreError(f"solid {o.solid} not found")
            return body
        return shape

    for o in m.observables:
        c: dict[str, Any] = {"id": o.id, "kind": o.kind, "required": o.required, "note": o.note}
        try:
            expected = _truth_measure(case, o) if o.from_ else o.expected
            if o.kind in ("solid", "clearance", "passage", "thickness", "probe"):
                c.update(extra.score(o, expected))
            elif o.kind == "teeth":
                r = gears.tooth_count(
                    scoped(o), list(o.point), list(o.direction), float(o.at), float(o.module), int(expected)
                )
                c.update(
                    expected=int(expected),
                    measured=r.get("teeth"),
                    tip_radius=r.get("tip_radius"),
                    error=r.get("error"),
                    ok=bool(r.get("ok")),
                )
            elif o.kind == "gear_mesh":
                ba, bb = (
                    multibody.select_solid(shape, solid_points[o.a]),
                    multibody.select_solid(shape, solid_points[o.b]),
                )
                if ba is None or bb is None:
                    c.update(ok=False, error="a gear solid was not found")
                else:
                    r = gears.mesh_motion(
                        ba,
                        bb,
                        (list(o.axis_a[0]), list(o.axis_a[1])),
                        (list(o.axis_b[0]), list(o.axis_b[1])),
                        ratio=float(o.ratio),
                        pitch_deg=float(o.pitch_deg),
                        steps=int(o.steps or 6),
                        backlash_max=float(o.backlash_max if o.backlash_max is not None else 0.3),
                    )
                    c.update(
                        measured={k: r[k] for k in ("max_interference", "gap_min", "gap_max")},
                        poses=[
                            (p["theta_deg"], round(p["interference_volume"], 5), round(p["gap"], 4), p["ok"])
                            for p in r["poses"]
                        ],
                        expected={"interference": 0.0, "backlash_max": r["backlash_max"]},
                        ok=r["ok"],
                    )
            elif o.kind == "bbox_size":
                meas = cand["bbox_size"]
                errs = [abs(a - b) for a, b in zip(meas, expected)]
                c.update(expected=expected, measured=meas, error=max(errs), ok=max(errs) <= (o.tolerance or 0.0))
            elif o.kind in ("volume", "surface_area"):
                meas = cand[o.kind]
                ok, band = _rel_ok(meas, float(expected), o)
                c.update(expected=expected, measured=meas, error=abs(meas - expected), band=band, ok=ok)
            elif o.kind == "center_of_mass":
                meas = cand["center_of_mass"]
                errs = [abs(a - b) for a, b in zip(meas, expected)]
                c.update(expected=expected, measured=meas, error=max(errs), ok=max(errs) <= (o.tolerance or 0.0))
            elif o.kind == "solid_count":
                c.update(expected=expected, measured=cand["solids"], ok=cand["solids"] == int(expected))
            elif o.kind == "dimension":
                i = "xyz".index(o.axis)
                meas = cand["bbox_size"][i]
                ok, band = _rel_ok(meas, float(expected), o)
                c.update(expected=expected, measured=meas, error=abs(meas - expected), band=band, ok=ok)
            elif o.kind == "section":
                r = brep.section(scoped(o), o.plane, o.at)
                exp = expected or {}
                sub = {}
                if exp.get("area") is not None:
                    tol = o.area_tolerance_rel if o.area_tolerance_rel is not None else (o.tolerance_rel or 0.01)
                    sub["area"] = {
                        "expected": exp["area"],
                        "measured": r["area"],
                        "ok": abs(r["area"] - exp["area"]) <= abs(exp["area"]) * tol,
                    }
                for k in ("loops", "holes"):
                    if exp.get(k) is not None:
                        sub[k] = {"expected": exp[k], "measured": r[k], "ok": r[k] == exp[k]}
                if exp.get("regions") is not None:
                    # expected list of {center: [u, v], size: [du, dv]} in the section plane's in-plane axes; matched greedily
                    matched = _match_regions(r["regions"], exp["regions"], o.plane, o.tolerance or 0.1)
                    sub["regions"] = matched
                c.update(
                    plane=o.plane,
                    at=o.at,
                    measured={k: r[k] for k in ("area", "loops", "holes")},
                    checks=sub,
                    ok=all(v["ok"] for v in sub.values()),
                )
            elif o.kind == "face":
                c.update(**face_results[o.id])
            elif o.kind == "cylinder":
                if cyls is None:
                    cyls = brep.cylinders(shape)
                r = brep.match_cylinder(
                    cyls,
                    list(o.point),
                    list(o.direction),
                    float(o.radius),
                    kind=o.cyl_kind,
                    axis_tol=o.tolerance if o.tolerance is not None else 0.05,
                    radius_tol=o.radius_tolerance if o.radius_tolerance is not None else 0.05,
                    t_range=tuple(o.t_range) if o.t_range else None,
                    length=o.length,
                )
                sub = {
                    "axis": {
                        "max": o.tolerance if o.tolerance is not None else 0.05,
                        "measured": r.get("axis_offset"),
                        "ok": bool(r.get("ok")),
                    }
                }
                if r.get("found") and o.length is not None:
                    err = abs(r["measured"]["length"] - o.length)
                    sub["length"] = {
                        "expected": o.length,
                        "measured": r["measured"]["length"],
                        "ok": err <= (o.length_tolerance if o.length_tolerance is not None else 0.05),
                    }
                c.update(
                    expected={
                        "point": list(o.point),
                        "direction": list(o.direction),
                        "radius": o.radius,
                        "kind": o.cyl_kind,
                    },
                    measured=(
                        {k: r["measured"][k] for k in ("center", "direction", "radius", "length", "kind")}
                        if r.get("found")
                        else None
                    ),
                    axis_offset=r.get("axis_offset"),
                    radius_error=r.get("radius_error"),
                    checks=sub,
                    ok=all(v["ok"] for v in sub.values()),
                )
            elif o.kind == "cylinder_count":
                if cyls is None:
                    cyls = brep.cylinders(shape)
                rtol = o.radius_tolerance if o.radius_tolerance is not None else 0.05
                hits = [
                    x
                    for x in cyls
                    if abs(x["radius"] - float(o.radius)) <= rtol
                    and (o.cyl_kind == "any" or x["kind"] == o.cyl_kind)
                    and (
                        o.direction is None
                        or brep.axis_distance([0, 0, 0], list(o.direction), [0, 0, 0], x["direction"])[1] <= 0.5
                    )
                    and multibody.in_region(x["center"], o.region)
                ]
                n = len(hits)
                ok = (expected is None or n == int(expected)) and (o.expected_min is None or n >= int(o.expected_min))
                c.update(
                    expected=expected,
                    expected_min=o.expected_min,
                    measured=n,
                    centers=[h["center"] for h in hits],
                    region=o.region,
                    ok=ok,
                )
            elif o.kind == "plane":
                faces = brep.planar_faces(shape)
                hits = brep.find_face_normal(
                    faces, list(o.direction), list(o.point), o.tolerance if o.tolerance is not None else 0.05
                )
                area = sum(h["area"] for h in hits)
                ok = len(hits) > 0
                if o.expected is not None and hits:
                    rel = o.area_tolerance_rel if o.area_tolerance_rel is not None else 0.01
                    ok = ok and abs(area - float(o.expected)) <= abs(float(o.expected)) * rel
                c.update(expected=o.expected, found=len(hits), measured=area, ok=ok)
            elif o.kind in ("deviation", "not_matching"):
                ref = case / o.reference
                if ref.suffix.lower() in (".step", ".stp"):
                    ref = step_to_mesh(ref, tmp / (ref.stem + ".stl"))
                cand_mesh = stl if stl is not None and stl.exists() else step_to_mesh(step, tmp / "candidate.stl")
                dev = meshcheck.deviation(cand_mesh, ref, samples=DEVIATION_SAMPLES, seed=DEVIATION_SEED)
                sub = {}
                if o.kind == "deviation":
                    if o.p95_max is not None:
                        sub["p95"] = {"max": o.p95_max, "measured": dev["p95"], "ok": dev["p95"] <= o.p95_max}
                    if o.hausdorff_max is not None:
                        sub["hausdorff"] = {
                            "max": o.hausdorff_max,
                            "measured": dev["hausdorff_estimate"],
                            "ok": dev["hausdorff_estimate"] <= o.hausdorff_max,
                        }
                    if o.silhouette_iou_min is not None:
                        sub["silhouette_iou"] = {
                            "min": o.silhouette_iou_min,
                            "measured": dev["silhouette_iou_min"],
                            "ok": dev["silhouette_iou_min"] >= o.silhouette_iou_min,
                        }
                else:
                    sub["p95_exceeds"] = {
                        "min": o.min_distance,
                        "measured": dev["p95"],
                        "ok": dev["p95"] > (o.min_distance or 0.0),
                    }
                c.update(
                    measured={k: dev[k] for k in ("p95", "hausdorff_estimate", "silhouette_iou_min", "volume_ratio")},
                    checks=sub,
                    ok=all(v["ok"] for v in sub.values()),
                )
            elif o.kind == "profile2d":
                c.update(**_profile2d(scoped(o), case / o.reference, o))
            else:
                c.update(ok=False, error=f"unknown observable kind {o.kind}")
        except Exception as e:  # scorer failures are recorded as failed checks, never hidden
            c.update(ok=False, error=f"{type(e).__name__}: {e}")
        checks.append(c)
    return checks


def _obs_face_spec(o: Observable) -> FaceSpec:
    area = float(o.expected) if o.expected is not None else None
    return FaceSpec(
        name=o.id,
        plane=o.plane,
        at=o.at,
        normal=o.normal,
        area=area,
        area_tolerance_rel=o.area_tolerance_rel if o.area_tolerance_rel is not None else 0.01,
        tolerance=o.tolerance,
        center=o.center,
        mode=o.mode,
    )


def _score_faces(shape, obs: list[Observable]) -> dict[str, dict[str, Any]]:
    faces = brep.planar_faces(shape)
    groups: dict[tuple, list[Observable]] = defaultdict(list)
    for o in obs:
        groups[(o.plane, o.at, o.normal)].append(o)
    out: dict[str, dict[str, Any]] = {}
    for (plane, at, normal), group in groups.items():
        tol = next((o.tolerance for o in group if o.tolerance is not None), 0.05)
        hits = brep.find_face(faces, plane, at, normal, tol)
        if len(group) == 1 and group[0].mode == "sum":
            o = group[0]
            area = sum(h["area"] for h in hits)
            ok = len(hits) > 0
            if o.expected is not None and hits:
                rel = o.area_tolerance_rel if o.area_tolerance_rel is not None else 0.01
                ok = ok and abs(area - float(o.expected)) <= abs(float(o.expected)) * rel
            out[o.id] = {
                "plane": plane,
                "at": at,
                "normal": normal,
                "found": len(hits),
                "area": area,
                "expected_area": o.expected,
                "mode": "sum",
                "ok": ok,
            }
            continue
        assigned = assign_coplanar([_obs_face_spec(o) for o in group], hits, plane)
        for o in group:
            r = assigned[o.id]
            out[o.id] = {
                "plane": plane,
                "at": at,
                "normal": normal,
                "found": r.get("found", 0),
                "area": r.get("area"),
                "expected_area": o.expected,
                "mode": o.mode,
                "center": r.get("center_expected"),
                "centroid_uv": r.get("centroid_uv"),
                "ok": r.get("ok", False),
            }
    return out


def _inplane_axes(plane: str) -> tuple[int, int]:
    return {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[plane]


def _match_regions(
    regions: list[dict[str, Any]], expected: list[dict[str, Any]], plane: str, tol: float
) -> dict[str, Any]:
    u, v = _inplane_axes(plane)
    meas = [
        {
            "center": [r["centroid"][u], r["centroid"][v]],
            "size": [r["bbox_max"][u] - r["bbox_min"][u], r["bbox_max"][v] - r["bbox_min"][v]],
            "area": r["area"],
        }
        for r in regions
    ]
    used = set()
    rows = []
    for e in expected:
        best, best_d = None, math.inf
        for i, mr in enumerate(meas):
            if i in used:
                continue
            d = math.dist(mr["center"], e["center"])
            if d < best_d:
                best, best_d = i, d
        if best is None:
            rows.append({"expected": e, "measured": None, "ok": False})
            continue
        used.add(best)
        mr = meas[best]
        size_ok = all(abs(a - b) <= tol for a, b in zip(mr["size"], e["size"])) if e.get("size") else True
        rows.append({"expected": e, "measured": mr, "center_error": best_d, "ok": best_d <= tol and size_ok})
    return {
        "expected_count": len(expected),
        "measured_count": len(meas),
        "rows": rows,
        "ok": all(r["ok"] for r in rows) and len(meas) == len(expected),
    }


def _profile2d(shape, ref_table: Path, o: Observable) -> dict[str, Any]:
    """Compare the candidate's section at (plane, at) with a reference closed 2D profile (units -> mm)."""
    from opencad.reference.mesh import UNIT_TO_MM
    from opencad.reference.profile import analyse, read_loop

    scale = UNIT_TO_MM[o.reference_units or "mm"] if o.reference_scale is None else float(o.reference_scale)
    sides = [tuple(s) for s in o.reference_sides] if o.reference_sides else None
    pts = read_loop(ref_table, sheet=o.reference_sheet, sides=sides, skip=o.reference_skip) * scale
    side1 = None
    if o.reference_sides:
        from opencad.reference.profile import read_table

        side1 = (
            read_table(ref_table, sheet=o.reference_sheet, columns=tuple(o.reference_sides[0]), skip=o.reference_skip)
            * scale
        )
    ref = analyse(pts, side1=side1)
    r = brep.section(shape, o.plane, o.at)
    if not r.get("ok") or not r["regions"]:
        return {"ok": False, "error": "no section region at the profile plane"}
    # sample the candidate section boundary: tessellate the section faces' edges
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
    from OCP.GCPnts import GCPnts_UniformAbscissa
    from OCP.gp import gp_Dir, gp_Pln, gp_Pnt
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    i = "xyz".index(o.plane)
    origin, normal = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
    origin[i], normal[i] = o.at, 1.0
    sec = BRepAlgoAPI_Section(shape, gp_Pln(gp_Pnt(*origin), gp_Dir(*normal)))
    sec.Build()
    u, v = _inplane_axes(o.plane)
    samples = []
    section_shape = sec.Shape()
    outer_area = None
    if getattr(o, "outer_only", False):
        # keep only the outline of the largest section face; inner loops such as a bore are not part of the reference outline
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
        from OCP.BRepGProp import BRepGProp
        from OCP.BRepTools import BRepTools
        from OCP.GProp import GProp_GProps
        from OCP.TopAbs import TopAbs_FACE

        plane_face = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(*origin), gp_Dir(*normal)), -1e4, 1e4, -1e4, 1e4).Face()
        common = BRepAlgoAPI_Common(shape, plane_face)
        common.Build()
        faces = brep._explore(common.Shape(), TopAbs_FACE) if common.IsDone() else []
        if faces:

            def _face_area(f) -> float:
                props = GProp_GProps()
                BRepGProp.SurfaceProperties_s(TopoDS.Face(f), props)
                return float(props.Mass())

            biggest = TopoDS.Face(max(faces, key=_face_area))
            section_shape = BRepTools.OuterWire_s(biggest)
    exp = TopExp_Explorer(section_shape, TopAbs_EDGE)
    while exp.More():
        curve = BRepAdaptor_Curve(TopoDS.Edge(exp.Current()))
        ua = GCPnts_UniformAbscissa(curve, 0.05)
        if ua.IsDone():
            for k in range(1, ua.NbPoints() + 1):
                p = curve.Value(ua.Parameter(k))
                xyz = [p.X(), p.Y(), p.Z()]
                samples.append([xyz[u], xyz[v]])
        exp.Next()
    if not samples:
        return {"ok": False, "error": "no section edges"}
    samples = np.asarray(samples)
    if getattr(o, "outer_only", False):
        # area of the outer loop polygon (shoelace on angularly ordered samples about the loop centroid)
        c0 = samples.mean(axis=0)
        ang = np.arctan2(samples[:, 1] - c0[1], samples[:, 0] - c0[0])
        loop = samples[np.argsort(ang)]
        x, y = loop[:, 0], loop[:, 1]
        outer_area = float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))
    # point-to-polyline distance; wrap only for a closed loop
    closed = bool(getattr(o, "reference_closed", True))

    def dist_to_poly(P: np.ndarray, poly: np.ndarray, wrap: bool) -> np.ndarray:
        A = poly if wrap else poly[:-1]
        B = np.roll(poly, -1, axis=0) if wrap else poly[1:]
        AB = B - A
        d2 = np.einsum("ij,ij->i", AB, AB) + 1e-18
        best = np.full(len(P), np.inf)
        for a, ab, dd in zip(A, AB, d2):
            t = np.clip(((P - a) @ ab) / dd, 0, 1)
            proj = a + t[:, None] * ab
            best = np.minimum(best, np.linalg.norm(P - proj, axis=1))
        return best

    ref_loop = pts[:-1] if np.allclose(pts[0], pts[-1]) else pts
    d_c2r = dist_to_poly(samples, ref_loop, closed)
    d_r2c = np.array([np.min(np.linalg.norm(samples - q, axis=1)) for q in ref_loop])
    cand_area = outer_area if outer_area is not None else r["area"]
    defn = o.chord_definition or "farthest_pair"
    cand_chord = cand_stagger = exp_chord = exp_stagger = None
    section_iou = None
    if closed:
        if defn == "landmarks" and ref.get("landmark_endpoints"):
            le, te = (
                np.asarray(ref["landmark_endpoints"][0], dtype=float),
                np.asarray(ref["landmark_endpoints"][1], dtype=float),
            )
            cand_le = samples[int(np.argmin(np.linalg.norm(samples - le, axis=1)))]
            cand_te = samples[int(np.argmin(np.linalg.norm(samples - te, axis=1)))]
            if cand_le[0] > cand_te[0]:
                cand_le, cand_te = cand_te, cand_le
            cand_chord = float(np.linalg.norm(cand_te - cand_le))
            cand_stagger = float(np.degrees(np.arctan2(cand_te[1] - cand_le[1], cand_te[0] - cand_le[0])))
            exp_chord, exp_stagger = ref["landmark_chord"], ref["landmark_stagger_deg"]
        else:
            d = np.linalg.norm(samples[:, None, :] - samples[None, :, :], axis=2) if len(samples) <= 4000 else None
            if d is None:
                idx = np.random.default_rng(0).choice(len(samples), 4000, replace=False)
                sub = samples[idx]
                d = np.linalg.norm(sub[:, None, :] - sub[None, :, :], axis=2)
            else:
                sub = samples
            i, j = np.unravel_index(np.argmax(d), d.shape)
            a, b = sub[i], sub[j]
            if a[0] > b[0]:
                a, b = b, a
            cand_chord = float(d[i, j])
            cand_stagger = float(np.degrees(np.arctan2(b[1] - a[1], b[0] - a[0])))
            exp_chord, exp_stagger = ref["chord"], ref["stagger_deg"]
        try:
            if len(ref_loop) >= 3 and len(samples) >= 3:
                section_iou = meshcheck.polygon_iou(ref_loop, samples)
        except Exception:
            section_iou = None
    if closed:
        p95 = float(max(np.percentile(d_c2r, 95), np.percentile(d_r2c, 95)))
    else:
        p95 = float(np.percentile(d_r2c, 95))
    checks = {"p95": {"max": o.p95_max, "measured": p95, "ok": o.p95_max is None or p95 <= o.p95_max}}
    if closed:
        checks["area"] = {
            "expected": ref["area"],
            "measured": cand_area,
            "ok": abs(cand_area - ref["area"]) <= ref["area"] * (o.tolerance_rel or 0.005),
        }
        checks["chord"] = {
            "expected": exp_chord,
            "measured": cand_chord,
            "ok": abs(cand_chord - exp_chord) <= (o.chord_tolerance if o.chord_tolerance is not None else 0.1),
        }
        checks["stagger_deg"] = {
            "expected": exp_stagger,
            "measured": cand_stagger,
            "ok": abs(cand_stagger - exp_stagger)
            <= (o.stagger_tolerance_deg if o.stagger_tolerance_deg is not None else 0.2),
        }
    return {
        "plane": o.plane,
        "at": o.at,
        "reference_points": int(len(ref_loop)),
        "candidate_samples": int(len(samples)),
        "chord_definition": defn,
        "reference_closed": closed,
        "reference": {
            k: ref[k]
            for k in (
                "area",
                "chord",
                "stagger_deg",
                "landmark_chord",
                "landmark_stagger_deg",
                "max_thickness",
                "bbox_min",
                "bbox_max",
            )
            if k in ref
        },
        "measured": {
            "area": cand_area,
            "chord": cand_chord,
            "stagger_deg": cand_stagger,
            "bbox_min": [float(samples[:, 0].min()), float(samples[:, 1].min())],
            "bbox_max": [float(samples[:, 0].max()), float(samples[:, 1].max())],
            "d_c2r_max": float(d_c2r.max()),
            "d_r2c_max": float(d_r2c.max()),
            "section_iou": section_iou,
        },
        "checks": checks,
        "ok": all(c["ok"] for c in checks.values()),
    }

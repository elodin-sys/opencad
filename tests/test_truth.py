import json
from pathlib import Path

import numpy as np
import pytest
import yaml

from opencad.geomcheck import brep, mesh as meshcheck
from opencad.paths import REPO_ROOT
from opencad.schemas import PointQuantity
from opencad.truth.manifest import CaseManifest, Observable, case_dir, load_manifest, load_registry, verify_pins
from opencad.truth.scorer import _match_regions, _score_faces, accuracy_score, step_to_mesh

BRACKET_STEP = REPO_ROOT / "smoke" / "out" / "e2e" / "bracket.step"
_BUMP_STEP = REPO_ROOT / "truth" / "cases" / "nasa-atb-axisymmetric-bump" / "truth" / "bump.step"


def test_registry_cases_validate_and_pins_match():
    reg = load_registry()
    assert reg["cases"], "registry has cases"
    for entry in reg["cases"]:
        if not (case_dir(entry["id"]) / "manifest.yaml").exists():
            continue  # sequestered by a live run
        m = load_manifest(entry["id"])
        assert m.id == entry["id"]
        if not (case_dir(entry["id"]) / "truth").exists():
            continue
        assert verify_pins(entry["id"], m) == []


def test_manifest_rejects_unknown_arm_input():
    d = yaml.safe_load(
        (REPO_ROOT / "truth" / "cases" / "nasa-backstep-driver-seegmiller" / "manifest.yaml").read_text()
    )
    d["arms"][0]["inputs"].append("inputs/ghost.md")
    with pytest.raises(Exception, match="not a manifest input"):
        CaseManifest.model_validate(d)
    d = yaml.safe_load(
        (REPO_ROOT / "truth" / "cases" / "nasa-backstep-driver-seegmiller" / "manifest.yaml").read_text()
    )
    d["observables"].append({"id": "dev", "kind": "deviation", "reference": "truth/nope.stl", "p95_max": 0.1})
    with pytest.raises(Exception, match="not a truth file"):
        CaseManifest.model_validate(d)


def test_match_regions_greedy():
    regions = [
        {"centroid": [10, 10, 3], "bbox_min": [8, 8, 3], "bbox_max": [12, 12, 3], "area": 16},
        {"centroid": [70, 40, 3], "bbox_min": [68, 38, 3], "bbox_max": [72, 42, 3], "area": 16},
    ]
    expected = [{"center": [70, 40], "size": [4, 4]}, {"center": [10, 10], "size": [4, 4]}]
    r = _match_regions(regions, expected, "z", 0.5)
    assert r["ok"] and r["measured_count"] == 2
    bad = _match_regions(regions, [{"center": [70, 40], "size": [4, 4]}], "z", 0.5)
    assert not bad["ok"]  # count mismatch


@pytest.mark.skipif(not BRACKET_STEP.exists(), reason="smoke bracket STEP not present")
def test_step_to_mesh_roundtrip(tmp_path):
    stl = step_to_mesh(BRACKET_STEP, tmp_path / "b.stl")
    a = meshcheck.analyze_mesh(stl)
    assert a["watertight"] and a["components"] == 1
    assert a["volume"] == pytest.approx(23489.5, rel=0.002)
    dev = meshcheck.deviation(stl, REPO_ROOT / "smoke" / "out" / "e2e" / "bracket.stl", samples=3000)
    assert dev["p95"] < 0.05 and dev["silhouette_iou_min"] > 0.98
    assert dev.get("silhouette_px_long") == 2400
    assert a.get("void_shells") == 0


def _write_box_step(path: Path, dx=10.0, dy=10.0, dz=4.0):
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    w = STEPControl_Writer()
    w.Transfer(BRepPrimAPI_MakeBox(dx, dy, dz).Shape(), STEPControl_AsIs)
    assert w.Write(str(path)) == IFSelect_RetDone


def test_coplanar_tabs_assigned_by_center(tmp_path):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.gp import gp_Pnt

    plate = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 40, 20, 2).Shape()
    tab1 = BRepPrimAPI_MakeBox(gp_Pnt(4, 8, 2), 4, 4, 1).Shape()
    tab2 = BRepPrimAPI_MakeBox(gp_Pnt(32, 8, 2), 4, 4, 1).Shape()
    fused = BRepAlgoAPI_Fuse(plate, tab1)
    fused.Build()
    fused = BRepAlgoAPI_Fuse(fused.Shape(), tab2)
    fused.Build()
    step = tmp_path / "tabs.step"
    w = STEPControl_Writer()
    w.Transfer(fused.Shape(), STEPControl_AsIs)
    assert w.Write(str(step)) == IFSelect_RetDone
    shape = brep.read_step(step)
    obs = [
        Observable(
            id="left", kind="face", plane="z", at=3.0, normal="+", expected=16.0, center=(6.0, 10.0), tolerance=0.2
        ),
        Observable(
            id="right", kind="face", plane="z", at=3.0, normal="+", expected=16.0, center=(34.0, 10.0), tolerance=0.2
        ),
    ]
    scored = _score_faces(shape, obs)
    assert scored["left"]["ok"] and scored["right"]["ok"]
    assert scored["left"]["centroid_uv"][0] < scored["right"]["centroid_uv"][0]


def test_hollow_box_void_shell(tmp_path):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.gp import gp_Pnt

    outer = BRepPrimAPI_MakeBox(10, 10, 10).Shape()
    inner = BRepPrimAPI_MakeBox(gp_Pnt(2, 2, 2), 6, 6, 6).Shape()
    cut = BRepAlgoAPI_Cut(outer, inner)
    cut.Build()
    step = tmp_path / "hollow.step"
    w = STEPControl_Writer()
    w.Transfer(cut.Shape(), STEPControl_AsIs)
    assert w.Write(str(step)) == IFSelect_RetDone
    stl = step_to_mesh(step, tmp_path / "hollow.stl")
    a = meshcheck.analyze_mesh(stl)
    assert a["components"] >= 2
    assert a["void_shells"] >= 1
    assert a["solid_shells"] == a["components"] - a["void_shells"]


def test_section_fallback_when_common_not_done(tmp_path, monkeypatch):
    step = tmp_path / "box.step"
    _write_box_step(step)
    shape = brep.read_step(step)
    real = brep.BRepAlgoAPI_Common

    class _NotDone:
        def __init__(self, *a, **k):
            self._inner = real(*a, **k)

        def Build(self):
            self._inner.Build()

        def IsDone(self):
            return False

        def Shape(self):
            return self._inner.Shape()

    monkeypatch.setattr(brep, "BRepAlgoAPI_Common", _NotDone)
    r = brep.section(shape, "z", 2.0)
    assert r["ok"]
    assert r["method"] == "section-wires"
    assert r["area"] == pytest.approx(100.0, rel=0.02)


def test_polygon_iou_identical_square():
    sq = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], dtype=float)
    assert meshcheck.polygon_iou(sq, sq) == pytest.approx(1.0, abs=1e-3)


def test_point_quantity_note():
    pq = PointQuantity(expected=(1, 2, 3), tolerance=0.1, note="volume-weighted COM")
    assert pq.note.startswith("volume-weighted")


def test_log_score_appends_attempt(tmp_path, monkeypatch):
    from opencad.truth import runner

    attempts = tmp_path / "attempts.yaml"
    attempts.write_text("attempts: []\n")
    monkeypatch.setattr(runner, "attempts_path", lambda cid: attempts)
    card = {
        "scored_at": "2026-09-16T00:00:00Z",
        "verdict": "PASS",
        "design": "coupon",
        "summary": {"required_pass": 1, "required_total": 1},
        "checks": [{"id": "volume", "ok": True}],
        "hash_binding": {"step_sha256": "abc123"},
    }
    runner.log_score("demo", "arm-a", card, seconds=4.2)
    data = yaml.safe_load(attempts.read_text())
    e = data["attempts"][-1]
    assert e["resume_from"] == "score"
    assert e["stage_reached"] == "scored"
    assert e["scorecard"]["verdict"] == "PASS"
    assert e["step_sha256"] == "abc123"
    assert e["seconds"] == 4


def test_restore_merges_the_vault_back_and_refuses_existing(tmp_path, monkeypatch):
    from opencad.truth import runner
    from opencad.truth import __main__ as tm

    held = tmp_path / "vault" / "demo"
    (held / "truth").mkdir(parents=True)
    (held / "truth" / "marker").write_text("vaulted")
    (held / "scorecards").mkdir()
    (held / "scorecards" / "arm@cadquery-latest.json").write_text("{}")
    (held / "holders.json").write_text('{"active": [], "pending": 1}')
    case = tmp_path / "cases" / "demo"
    (case / "scorecards").mkdir(parents=True)
    (case / "scorecards" / "arm@freecad-latest.json").write_text("{}")
    monkeypatch.setattr(runner, "VAULT", tmp_path / "vault")
    monkeypatch.setattr(tm, "case_dir", lambda cid: case)
    monkeypatch.setattr(tm, "load_manifest", lambda cid: object())
    monkeypatch.setattr(tm, "verify_pins", lambda cid, m: [])
    assert tm.cmd_restore("demo") == 0
    assert (case / "truth" / "marker").read_text() == "vaulted" and not held.exists()
    assert {p.name for p in (case / "scorecards").iterdir()} == {"arm@cadquery-latest.json", "arm@freecad-latest.json"}
    assert tm.cmd_restore("demo") == 1  # refuse overwrite


def test_status_exits_1_when_truth_missing(tmp_path, monkeypatch, capsys):
    from opencad.truth import runner
    from opencad.truth import __main__ as tm

    case = tmp_path / "cases" / "ghost"
    case.mkdir(parents=True)
    monkeypatch.setattr(tm, "load_registry", lambda: {"cases": [{"id": "ghost"}]})

    class Arm:
        id = "a"
        design = "ghost"

    class M:
        truth_class = "D"
        arms = [Arm()]

    monkeypatch.setattr(tm, "load_manifest", lambda cid: M())
    monkeypatch.setattr(tm, "case_dir", lambda cid: case)
    monkeypatch.setattr(runner, "VAULT", tmp_path / "empty-vault")
    monkeypatch.setattr(runner, "attempts_path", lambda cid: case / "attempts.yaml")
    assert tm.cmd_status() == 1
    out = capsys.readouterr().out
    assert "MISSING" in out


def test_resume_from_publish_requires_staging():
    from opencad.orchestrator import PipelineError
    from opencad.truth.manifest import load_manifest
    from opencad.truth.runner import run_case

    m = load_manifest("nasa-backstep-driver-seegmiller")
    with pytest.raises(PipelineError, match="staging"):
        run_case("nasa-backstep-driver-seegmiller", m, "text-only", resume_from="publish")


def test_resume_from_blockout_force_resets_only_this_backends_run(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from opencad import paths
    from opencad.truth import runner

    for name in ("DESIGNS", "PARTS_BASE", "RESULTS_BASE"):
        monkeypatch.setattr(paths, name, tmp_path / name.lower())
    monkeypatch.setattr(runner, "DESIGNS", paths.DESIGNS)
    (paths.DESIGNS / "demo").mkdir(parents=True)
    (paths.DESIGNS / "demo" / "contract.yaml").write_text("id: demo\n")
    for root in (runner.part_dir("demo"), runner.results_of("demo")):
        root.mkdir(parents=True)
        (root / "stale").write_text("x")

    def preflight():
        raise RuntimeError("preflight reached")

    monkeypatch.setattr(runner, "get", lambda: SimpleNamespace(engine=SimpleNamespace(preflight=preflight)))
    m = SimpleNamespace(arms=[SimpleNamespace(id="a", design="demo")])
    with pytest.raises(RuntimeError, match="preflight reached"):
        runner.run_case("demo", m, "a", resume_from="blockout", force=True)
    assert (paths.DESIGNS / "demo" / "contract.yaml").exists()
    assert not runner.part_dir("demo").exists() and not runner.results_of("demo").exists()


def test_cli_from_stage_help_mentions_kcl_delete():
    from opencad.cli import build_parser

    help_ = build_parser().format_help()
    # argparse stores the dest help on the run subparser
    run_help = None
    for a in build_parser()._subparsers._group_actions:
        for name, p in a.choices.items():
            if name == "run":
                run_help = p.format_help()
    assert run_help and "plan deletes the part source files" in run_help


def test_chiral_keyplate_floors_and_mirror():
    case = REPO_ROOT / "truth" / "cases" / "chiral-keyplate"
    shape = brep.read_step(case / "truth" / "chiral-keyplate.step")
    obs = [
        Observable(
            id="a", kind="face", plane="z", at=4.0, normal="+", expected=96.0, center=(20.0, 8.0), tolerance=0.2
        ),
        Observable(
            id="b", kind="face", plane="z", at=4.0, normal="+", expected=96.0, center=(-8.0, 20.0), tolerance=0.2
        ),
        Observable(
            id="c", kind="face", plane="z", at=4.0, normal="+", expected=96.0, center=(-20.0, -8.0), tolerance=0.2
        ),
        Observable(
            id="d", kind="face", plane="z", at=4.0, normal="+", expected=96.0, center=(8.0, -20.0), tolerance=0.2
        ),
    ]
    scored = _score_faces(shape, obs)
    assert all(scored[k]["ok"] for k in ("a", "b", "c", "d"))
    a = brep.analyze_step(case / "truth" / "chiral-keyplate.step")
    assert a["volume"] == pytest.approx(49664.0, rel=1e-9)
    d = meshcheck.deviation(
        case / "truth" / "chiral-keyplate.stl", case / "truth" / "chiral-keyplate-mirrored.stl", samples=4000, seed=0
    )
    assert d["p95"] > 1.0
    assert d["silhouette_iou_min"] == pytest.approx(1.0, abs=0.01)
    assert d["volume_ratio"] == pytest.approx(1.0, abs=1e-6)


@pytest.mark.skipif(not _BUMP_STEP.exists(), reason="bump truth sequestered during a live run")
def test_profile2d_open_polyline_one_way():
    from opencad.truth.scorer import _profile2d

    case = REPO_ROOT / "truth" / "cases" / "nasa-atb-axisymmetric-bump"
    shape = brep.read_step(case / "truth" / "bump.step")
    o = Observable(
        id="meridian",
        kind="profile2d",
        plane="z",
        at=0.0,
        reference="truth/bumpgrd.surfpts_orig.dat",
        reference_scale=203.2,
        reference_closed=False,
        p95_max=0.5,
    )
    r = _profile2d(shape, case / "truth" / "bumpgrd.surfpts_orig.dat", o)
    assert r["ok"] and r["reference_closed"] is False
    assert "area" not in r["checks"] and "chord" not in r["checks"]
    assert r["checks"]["p95"]["measured"] <= 0.5


def test_prior_stuck_class_filters_backend(tmp_path, monkeypatch):
    from opencad.truth import runner

    case = tmp_path / "cases" / "prusa"
    case.mkdir(parents=True)
    (case / "attempts.yaml").write_text(
        "attempts:\n"
        "- arm: renders-and-sheet\n  backend: zoo\n  stuck_class: kernel-incomplete\n"
        "- arm: renders-and-sheet\n  backend: cadquery\n  resume_from: score\n"
        "- arm: renders-and-sheet\n  backend: cadquery\n  stuck_class: null\n"
    )
    monkeypatch.setattr(runner, "case_dir", lambda cid: case)
    monkeypatch.setattr(runner, "current_id", lambda: "cadquery")
    assert runner.prior_stuck_class("prusa", "renders-and-sheet") is None
    monkeypatch.setattr(runner, "current_id", lambda: "zoo")
    assert runner.prior_stuck_class("prusa", "renders-and-sheet") == "kernel-incomplete"


def test_parity_gate_names_missing_checks_without_truth_values(tmp_path, monkeypatch):
    """B6: before publishing, the drafted contract is audited against the case's observables; missing/looser checks (never the
    evaluator's own probe points) go back to the draft thread as kind + id, with no evaluator value in the brief."""
    import shutil

    from opencad import initialize, telemetry, worker
    from opencad.paths import TEMPLATE
    from opencad.truth import runner

    monkeypatch.setattr(runner, "results_of", lambda name: tmp_path / "results" / name)
    monkeypatch.setattr(telemetry, "CAMPAIGN_FILE", tmp_path / "campaign.jsonl")
    staging = tmp_path / ".staging-bearing-housing"
    staging.mkdir()
    shutil.copy2(TEMPLATE / "contract.yaml", staging / "contract.yaml")
    m = load_manifest("bearing-housing")
    gap = runner.parity_gap(m, staging, "bearing-housing")
    kinds = {f["kind"] for f in gap}
    assert "cylinder" in kinds and "probe" not in kinds and all(f["status"] in ("missing", "looser") for f in gap)
    seen = {}
    monkeypatch.setattr(worker, "dispatch", lambda brief, **kw: seen.update(kw, brief=brief))
    problems = initialize.parity_round(staging, "bearing-housing", gap, thread="agent-7", timeout=None)
    assert seen["key"] == "draft-parity" and seen["resume"] == "agent-7" and isinstance(problems, list)
    assert "`counterbore`" in seen["brief"] and "38.25" not in seen["brief"] and "23.5" not in seen["brief"]


def test_accuracy_score_perfect_half_band_and_failed():
    manifest = CaseManifest.model_construct(
        observables=[
            Observable(id="bbox", kind="bbox_size", tolerance=0.2),
            Observable(id="vol", kind="volume", tolerance_rel=0.01),
            Observable(id="count", kind="solid_count"),
        ]
    )
    perfect = {
        "checks": [
            {
                "id": "bbox",
                "kind": "bbox_size",
                "required": True,
                "ok": True,
                "measured": [10.0, 20.0, 5.0],
                "expected": [10.0, 20.0, 5.0],
            },
            {"id": "dev", "kind": "deviation", "required": False, "ok": False},
        ]
    }
    half = {"checks": [{"id": "vol", "kind": "volume", "required": True, "ok": True, "error": 5.0, "band": 10.0}]}
    failed = {
        "checks": [{"id": "count", "kind": "solid_count", "required": True, "ok": False, "expected": 1, "measured": 2}]
    }
    assert accuracy_score(perfect, manifest) == 100
    assert accuracy_score(half, manifest) == 50
    assert accuracy_score(failed, manifest) == 0

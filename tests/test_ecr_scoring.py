"""Change-request scoring (Arm.ecr), region-filtered cylinder counts, and the held-out assembly runner."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import yaml
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

from opencad.geomcheck import brep, multibody
from opencad.truth import assembly_task, scorer
from opencad.truth.manifest import CaseManifest
from opencad.truth.mutants import write_step


def _plate_with_holes():
    plate = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), gp_Pnt(100, 60, 5)).Shape()
    for x, y in ((50, -0.0 + 3), (75, 3), (50, 57), (75, 57), (10, 30)):
        plate = BRepAlgoAPI_Cut(plate, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, -1), gp_Dir(0, 0, 1)), 1.6, 8).Shape()).Shape()
    return plate


def test_cylinder_count_region_filter():
    cyls = brep.cylinders(_plate_with_holes())
    out = multibody.check_cylinder_counts(cyls, [
        {"name": "all", "radius": 1.6, "kind": "hole", "expected": 5},
        {"name": "x50_low", "radius": 1.6, "kind": "hole", "expected_min": 1, "region": [[49.5, -20, -10], [50.5, 10, 60]]},
        {"name": "x50_high", "radius": 1.6, "kind": "hole", "expected": 1, "region": [[49.5, 50, -10], [50.5, 80, 60]]},
        {"name": "x20_none", "radius": 1.6, "kind": "hole", "expected_min": 1, "region": [[19.5, -20, -10], [20.5, 80, 60]]},
    ])
    assert out["all"]["ok"] and out["x50_low"]["ok"] and out["x50_high"]["ok"] and not out["x20_none"]["ok"]
    assert out["x50_low"]["measured"] == 1 and out["x20_none"]["measured"] == 0


def test_inspect_cylinder_counts_apply_the_region():
    """inspect (and therefore `quick`) dropped `region` when it flattened CylinderCountSpec rows, so a region-filtered
    count saw every hole of the right radius: the pre-ECR corner holes satisfied every ECR-3 side-station count."""
    from opencad.schemas import CylinderCountSpec
    from opencad.stages.inspect_stage import count_specs

    specs = [CylinderCountSpec.model_validate({"name": "x50_low", "diameter": 3.2, "kind": "hole", "direction": [0, 0, 1], "region": [[49.5, -20, -10], [50.5, 10, 60]], "expected_min": 1}),
             CylinderCountSpec.model_validate({"name": "all", "radius": 1.6, "kind": "hole", "expected": 5})]
    rows = count_specs(specs)
    assert rows[0]["region"] == [[49.5, -20, -10], [50.5, 10, 60]] and rows[0]["radius"] == 1.6 and rows[1]["region"] is None
    out = multibody.check_cylinder_counts(brep.cylinders(_plate_with_holes()), rows)
    assert out["x50_low"]["measured"] == 1 and out["x50_low"]["centers"][0][:2] == [50.0, 3.0] and out["all"]["measured"] == 5


def _manifest(tmp_path: Path, ecr: str | None) -> tuple[Path, CaseManifest]:
    case = tmp_path / "truth" / "cases" / "demo"
    (case / "inputs").mkdir(parents=True, exist_ok=True)
    (case / "truth").mkdir(exist_ok=True)
    (case / "inputs" / "req.md").write_text("request")
    (case / "truth" / "rev.yaml").write_text("x: 1\n")
    raw = {
        "id": "demo", "title": "demo", "truth_class": "C", "role": "validation",
        "source": {"citation": "test", "urls": [], "accessed": "2026-09-17", "revision": "1", "license": "test"},
        "intent": "demo", "inputs": [{"path": "inputs/req.md", "kind": "text", "sha256": "0" * 64}],
        "truth": [{"path": "truth/rev.yaml", "kind": "yaml", "sha256": "0" * 64}],
        "arms": [{"id": "a", "design": "plate", **({"ecr": ecr} if ecr else {}), "inputs": ["inputs/req.md"]}],
        "observables": [
            {"id": "count", "kind": "cylinder_count", "cyl_kind": "hole", "radius": 1.6, "expected": 5, "direction": [0, 0, 1]},
            {"id": "side", "kind": "cylinder_count", "cyl_kind": "hole", "radius": 1.6, "expected_min": 1, "region": [[74.5, 50, -10], [75.5, 80, 60]]},
        ],
    }
    (case / "manifest.yaml").write_text(yaml.safe_dump(raw))
    return case, CaseManifest.model_validate(raw)


def test_arm_ecr_scores_the_ecr_handoff(tmp_path: Path, monkeypatch):
    case, m = _manifest(tmp_path, "ecr1")
    results = tmp_path / "results"
    (tmp_path / "designs" / "plate" / "ecr" / "ecr1").mkdir(parents=True)
    (tmp_path / "designs" / "plate" / "ecr" / "ecr1" / "contract.yaml").write_text("revised: true\n")
    (tmp_path / "parts" / "plate").mkdir(parents=True)
    handoff = results / "plate" / "ecr" / "ecr1" / "handoff"
    handoff.mkdir(parents=True)
    write_step(_plate_with_holes(), handoff / "plate.step")
    monkeypatch.setattr(scorer, "results_dir", lambda name: results / name)
    monkeypatch.setattr(scorer, "part_dir", lambda name: tmp_path / "parts" / name)
    monkeypatch.setattr(scorer, "case_dir", lambda cid: case)
    card = scorer.score_case("demo", m, "a")
    assert card["ecr"] == "ecr1" and card["results_dir"].endswith("ecr/ecr1") and card["verdict"] == "PASS"
    assert {c["id"]: c["ok"] for c in card["checks"]} == {"count": True, "side": True}
    # scored while the case's truth files sit in a vault: the card still lands in the tree's scorecards dir, not the vault
    vault = tmp_path / "vault" / "demo"
    shutil.copytree(case, vault, ignore=shutil.ignore_patterns("scorecards"))
    card2 = scorer.score_case("demo", m, "a", case_root=vault)
    latest = json.loads(next((case / "scorecards").glob("a@*-latest.json")).read_text())
    assert card2["verdict"] == "PASS" and latest["scored_at"] == card2["scored_at"]
    assert not (vault / "scorecards").exists()
    # without the label the base handoff is required
    _, base = _manifest(tmp_path, None)
    try:
        scorer.score_case("demo", base, "a")
    except scorer.ScoreError as e:
        assert "results/plate/handoff" in str(e).replace(str(tmp_path) + "/", "")
    else:
        raise AssertionError("base handoff missing must raise")


def test_truth_ecr_runner_sequesters_scores_and_restores_kcl(tmp_path: Path, monkeypatch):
    from opencad.stages import ecr as ecr_mod
    from opencad.truth import runner

    monkeypatch.setenv("OPENCAD_BACKEND", "zoo")
    case, m = _manifest(tmp_path, "ecr1")
    (case / "inputs" / "contract-delta.yaml").write_text("parameters: []\n")
    results = tmp_path / "results"
    parts = tmp_path / "parts" / "plate"
    parts.mkdir(parents=True)
    (parts / "main.kcl").write_text("base = 1\n")
    (tmp_path / "designs" / "plate" / "ecr" / "ecr1").mkdir(parents=True)
    (tmp_path / "designs" / "plate" / "ecr" / "ecr1" / "contract.yaml").write_text("revised: true\n")
    monkeypatch.setattr(scorer, "results_dir", lambda name: results / name)
    monkeypatch.setattr(scorer, "part_dir", lambda name: tmp_path / "parts" / name)
    monkeypatch.setattr(scorer, "case_dir", lambda cid: case)
    monkeypatch.setattr(runner, "part_dir", lambda name: tmp_path / "parts" / name)
    monkeypatch.setattr(runner, "results_of", lambda name: results / name)
    monkeypatch.setattr(runner, "case_dir", lambda cid: case)
    monkeypatch.setattr(runner, "VAULT", tmp_path / "vault")
    seen: dict = {}

    def fake_ecr(part, request_path, *, delta_path=None, label="ecr1", expect_infeasible=False, timeout=None, allow_retry=True, cont=False):
        seen.update(part=part, request=request_path.name, delta=delta_path.name if delta_path else None, label=label, truth_hidden=not (case / "truth").exists())
        (parts / "main.kcl").write_text("changed = 2\n")
        handoff = results / part / "ecr" / label / "handoff"
        handoff.mkdir(parents=True, exist_ok=True)
        write_step(_plate_with_holes(), handoff / f"{part}.step")
        return {"ok": True, "outcome": "applied", "refused": False, "kcl_modified": True, "gates": {"summary": {"pass": 1}}, "preservation": {"ok": True}, "codex": {"seconds": 1}}

    monkeypatch.setattr(ecr_mod, "run", fake_ecr)
    entry = runner.run_ecr("demo", m, "a", timeout=10)
    assert seen == {"part": "plate", "request": "req.md", "delta": "contract-delta.yaml", "label": "ecr1", "truth_hidden": True}
    assert (case / "truth" / "rev.yaml").exists() and (parts / "main.kcl").read_text() == "base = 1\n", "truth restored, base KCL restored"
    assert entry["stage_reached"] == "scored" and entry["scorecard"]["verdict"] == "PASS" and entry["base_kcl_restored"]
    assert yaml.safe_load((case / "attempts.yaml").read_text())["attempts"][-1]["ecr"]["outcome"] == "applied"
    # a second backend still holds the case: the live tree stays empty and this run scores from the vault
    with runner.Sequester("demo"):
        assert not (case / "manifest.yaml").exists()
        entry2 = runner.run_ecr("demo", m, "a", timeout=10)
        assert entry2["stage_reached"] == "scored" and entry2["scorecard"]["verdict"] == "PASS", entry2.get("score_error")
        assert not (case / "truth").exists(), "the other holder keeps the case vaulted"
    assert (case / "truth" / "rev.yaml").exists()


def _joint_case(tmp_path: Path) -> Path:
    """Two boxes with a coaxial Ø10 pin/bore revolute joint, body one displaced in its local frame."""
    case = tmp_path / "truth" / "cases" / "j1-assembly"
    (case / "inputs" / "renders").mkdir(parents=True)
    (case / "truth").mkdir()
    bore_body = BRepAlgoAPI_Cut(BRepPrimAPI_MakeBox(gp_Pnt(-20, -20, 0), gp_Pnt(20, 20, 10)).Shape(),
                                BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, -1), gp_Dir(0, 0, 1)), 5, 12).Shape()).Shape()
    pin_body = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 4.9, 10).Shape()
    write_step(bore_body, case / "inputs" / "two.step")
    write_step(pin_body, case / "inputs" / "one.step")
    (case / "inputs" / "assembly-task.md").write_text("place one into two")
    # truth: body one sits 10 mm up the axis (offset), body two at identity; dataset units cm
    js = {"body_one": "one", "body_two": "two", "joints": [{
        "name": "Rev", "type": "Joint", "is_flipped": False, "offset": {"value": 0.0},
        "joint_motion": {"joint_type": "RevoluteJointType"},
        "geometry_or_origin_one": {"transform": {"origin": {"x": 0, "y": 0, "z": 1.0}, "x_axis": {"x": 1, "y": 0, "z": 0}, "y_axis": {"x": 0, "y": 1, "z": 0}, "z_axis": {"x": 0, "y": 0, "z": 1}},
                                   "axis_line": {"origin": {"x": 0, "y": 0, "z": 1.0}, "direction": {"x": 0, "y": 0, "z": 1}}},
        "geometry_or_origin_two": {"transform": None, "axis_line": {"origin": {"x": 0, "y": 0, "z": 0}, "direction": {"x": 0, "y": 0, "z": 1}}},
    }]}
    (case / "truth" / "joint_set.json").write_text(json.dumps(js))
    (case / "task.yaml").write_text(yaml.safe_dump({"id": "j1-assembly", "kind": "assembly", "bodies": ["one", "two"],
                                                    "inputs": ["inputs/assembly-task.md", "inputs/one.step", "inputs/two.step"], "truth": ["truth/joint_set.json"]}))
    return case


def test_assemble_runner_scores_codex_manifest(tmp_path: Path, monkeypatch):
    from opencad.truth import assemble, runner

    case = _joint_case(tmp_path)
    results = tmp_path / "results"
    monkeypatch.setattr(assemble, "RESULTS", results)
    monkeypatch.setattr(assemble, "case_dir", lambda cid: case)
    monkeypatch.setattr(runner, "case_dir", lambda cid: case)
    monkeypatch.setattr(runner, "VAULT", tmp_path / "vault")
    seen: dict = {}

    def fake_dispatch(brief, *, role, key, results_dir, part, cd, run_dir, images=None, timeout=None, deliverables=None, **kw):
        seen["truth_hidden"] = not (case / "truth").exists()
        seen["role"] = role
        assert "assembly-task.md" in brief and (cd / "one.step").exists()
        (cd / "assembly.yaml").write_text(yaml.safe_dump({"bodies": {"one": {"origin": [0, 0, 10]}, "two": {"origin": [0, 0, 0]}}}))
        return worker_stub(run_dir)

    from opencad import worker
    from opencad.worker.result import WorkerResult

    def worker_stub(run_dir: Path):
        return WorkerResult(thread_id="t1", exit_code=0, seconds=3, commands=2, usage={}, run_dir=run_dir, result_md="## Result\nplaced", failure="", sections={"Result": "placed"}, backend="cursor")

    monkeypatch.setattr(worker, "dispatch", fake_dispatch)
    card = assemble.run_assembly("j1-assembly", timeout=10, mode="placement")
    assert seen["truth_hidden"] and seen["role"] == "assemble", "joint_set.json must be sequestered while the worker places the bodies"
    assert (case / "truth" / "joint_set.json").exists(), "truth restored"
    assert card["verdict"] == "PASS", card
    assert (case / "scorecards" / "assembly-latest.json").exists()
    attempts = yaml.safe_load((case / "attempts.yaml").read_text())["attempts"]
    assert attempts[-1]["stage_reached"] == "scored" and attempts[-1]["scorecard"]["verdict"] == "PASS"
    # the dataset's own placement is accepted by the scorer too
    truth = assembly_task.truth_manifest(json.loads((case / "truth" / "joint_set.json").read_text()))
    (tmp_path / "t.yaml").write_text(yaml.safe_dump(truth))
    ok = assembly_task.score(case / "truth" / "joint_set.json", {"one": case / "inputs" / "one.step", "two": case / "inputs" / "two.step"}, tmp_path / "t.yaml")
    assert ok["ok"] and np.isclose(ok["checks"]["axial_offset"]["measured"], 10.0)


def test_assemble_scores_from_vault_while_another_holder_keeps_truth(tmp_path: Path, monkeypatch):
    from opencad.truth import assemble, runner
    from opencad.worker.result import WorkerResult
    from opencad import worker

    case = _joint_case(tmp_path)
    monkeypatch.setattr(assemble, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(assemble, "case_dir", lambda cid: case)
    monkeypatch.setattr(runner, "case_dir", lambda cid: case)
    monkeypatch.setattr(runner, "VAULT", tmp_path / "vault")

    def fake_dispatch(brief, *, role, key, results_dir, part, cd, run_dir, images=None, timeout=None, deliverables=None, **kw):
        (cd / "assembly.yaml").write_text(yaml.safe_dump({"bodies": {"one": {"origin": [0, 0, 10]}, "two": {"origin": [0, 0, 0]}}}))
        return WorkerResult(thread_id="t1", exit_code=0, seconds=1, commands=1, usage={}, run_dir=run_dir, result_md="## Result\nplaced", failure="", sections={"Result": "placed"}, backend="cursor")

    monkeypatch.setattr(worker, "dispatch", fake_dispatch)
    with runner.Sequester("j1-assembly"):
        assert not (case / "truth" / "joint_set.json").exists()
        card = assemble.run_assembly("j1-assembly", timeout=10, mode="placement")
        assert card["verdict"] == "PASS", card
        assert not (case / "truth" / "joint_set.json").exists()
    assert (case / "truth" / "joint_set.json").exists()

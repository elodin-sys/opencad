import json
import shutil
from pathlib import Path

import pytest

import trimesh

from opencad import gates
from opencad.contract import load_contract
from opencad.geomcheck.mesh import analyze_mesh
from opencad.orchestrator import Ctx
from opencad.paths import DESIGNS, PARTS, REPO_ROOT

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "coupon-results"
BENCHY_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "benchy-results"


def make_ctx(tmp_path: Path) -> Ctx:
    results = tmp_path / "results" / "coupon"
    shutil.copytree(FIXTURE, results)
    design = DESIGNS / "coupon"
    return Ctx("coupon", design, design / "contract.yaml", load_contract(design), results, PARTS / "coupon")


def make_benchy_ctx(tmp_path: Path) -> Ctx:
    results = tmp_path / "results" / "benchy"
    shutil.copytree(BENCHY_FIXTURE, results)
    design = DESIGNS / "benchy"
    return Ctx("benchy", design, design / "contract.yaml", load_contract(design), results, PARTS / "benchy")


def test_recorded_coupon_run_passes_all_applicable_gates(tmp_path):
    fb = gates.evaluate(make_ctx(tmp_path))
    assert fb["ok"], fb["failed"]
    assert fb["summary"] == {"pass": 11, "fail": 0, "not_applicable": 1}
    assert fb["not_applicable"] == ["reference_fidelity"]
    assert {g["tier"] for g in fb["gates"]} == {"A", "B", "C"}
    assert len(fb["gates"]) == 12
    assert fb["tier_a_failed"] == []
    assert fb["retryable_failed"] == []


def test_gates_reject_tampered_evidence(tmp_path):
    ctx = make_ctx(tmp_path)
    ins = json.loads(ctx.stage_file("inspect").read_text())
    ins["volume"]["ok"] = False
    ins["volume"]["measured"] = 9000.0
    ins["features"]["blank"]["ok"] = False
    ins["features"]["blank"]["checks"][1]["ok"] = False
    ctx.stage_file("inspect").write_text(json.dumps(ins))
    fb = gates.evaluate(ctx)
    assert not fb["ok"]
    assert set(fb["failed"]) == {"mass_properties", "features"}
    assert fb["tier_a_failed"] == ["mass_properties", "features"]
    msg = gates.correction_message(ctx, fb)
    assert "9000" in msg and "feature blank" in msg
    assert "Fix first" not in msg  # two failing items: the full list is short enough on its own


def test_derived_only_miss_forbids_changing_stated_geometry(tmp_path):
    ctx = make_ctx(tmp_path)
    ins = json.loads(ctx.stage_file("inspect").read_text())
    ins["surface_area"]["ok"] = False
    ins["surface_area"]["measured"] = 5607.4
    ctx.stage_file("inspect").write_text(json.dumps(ins))
    fb = gates.evaluate(ctx)
    assert fb["failed"] == ["mass_properties"]
    assert gates.derived_only_misses(ins, ctx.contract, fb["failed"]) == ["surface_area"]
    assert "Do not change stated geometry" in gates.correction_message(ctx, fb)
    ins["features"]["blank"]["ok"] = False
    ins["features"]["blank"]["checks"][1]["ok"] = False
    ctx.stage_file("inspect").write_text(json.dumps(ins))
    fb = gates.evaluate(ctx)
    assert "Do not change stated geometry" not in gates.correction_message(ctx, fb)


def test_failing_item_names_and_focus_block():
    """Many failing items: the brief leads with a ranked, clustered `Fix first` block; the failing-item names drive the loop's progress signal."""
    from opencad.contract import template_contract
    from opencad.schemas import CylinderSpec, Feature, Verify

    c = template_contract()
    c.acceptance.cylinders = [CylinderSpec(name=f"h{i}", point=[x, 0.0, 0.0], direction=[0, 0, 1], radius=2.0, kind="hole") for i, x in enumerate((0.0, 5.0, 40.0, 80.0))]
    c.features = [Feature(id="clamp", kind="hole", description="clamp bore", verify=[Verify(method="cylinder", cylinder="h0")]),
                  Feature(id="trim", kind="chamfer", description="cosmetic", optional=True, verify=[Verify(method="cylinder", cylinder="h3")])]
    cyl = {f"h{i}": {"ok": False, "found": True, "kind": "hole", "radius_expected": 2.0, "axis_offset": 0.3, "axis_tolerance": 0.05, "measured": {}, "point": [0, 0, 0], "direction": [0, 0, 1], "checks": {}} for i in range(4)}
    sec = {f"s{i}": {"ok": False, "plane": "z", "at": 3.0, "measured": {}, "checks": {}} for i in range(3)}
    ins = {"cylinders": cyl, "sections": sec, "volume": {"declared": True, "ok": True, "measured": 1, "expected": 1, "band": 0},
           "features": {"clamp": {"ok": False, "optional": False, "checks": [{"method": "cylinder", "ok": False, "name": "h0"}]},
                        "trim": {"ok": False, "optional": True, "checks": [{"method": "cylinder", "ok": False, "name": "h3"}]}}}
    names = gates.failing_item_names(ins)
    assert names == ["cylinders/h0", "cylinders/h1", "cylinders/h2", "cylinders/h3", "features/clamp", "sections/s0", "sections/s1", "sections/s2"]
    block = gates.focus_block(ins, c)
    assert block[0].startswith("Fix first (cluster near (0.0, 0.0, 0.0) mm)") and block[-1] == "Full list (8 failing items):"
    chosen = block[1:-1]
    assert len(chosen) == 6 and chosen[0].startswith("- feature clamp") and chosen[1].startswith("- cylinder h0") and chosen[2].startswith("- cylinder h1")
    assert not any("trim" in line for line in chosen)  # optional features never lead a correction


def test_export_agreement_discloses_missing_engine_transient(tmp_path):
    ctx = make_ctx(tmp_path)
    ver = json.loads(ctx.stage_file("verify").read_text())
    ver["engine"] = {"status": "missing", "class": "transient"}
    ver.pop("analyze", None)
    ctx.stage_file("verify").write_text(json.dumps(ver))
    ins = json.loads(ctx.stage_file("inspect").read_text())
    ins["agreement"] = {
        "kcl": None, "step": 9600.0, "stl": 9600.0, "tolerance_rel": 0.002,
        "kcl_vs_step_rel": None, "stl_vs_step_rel": 0.0,
        "engine_missing": True, "engine_class": "transient", "ok": True,
    }
    ctx.stage_file("inspect").write_text(json.dumps(ins))
    fb = gates.evaluate(ctx)
    by_id = {g["id"]: g for g in fb["gates"]}
    assert by_id["export_agreement"]["ok"] is True
    assert "engine volume missing (transient)" in by_id["export_agreement"]["evidence"][0]


def test_export_agreement_fails_on_kcl_engine_error(tmp_path):
    ctx = make_ctx(tmp_path)
    ver = json.loads(ctx.stage_file("verify").read_text())
    ver["engine"] = {"status": "missing", "class": "kcl"}
    ctx.stage_file("verify").write_text(json.dumps(ver))
    ins = json.loads(ctx.stage_file("inspect").read_text())
    ins["agreement"] = {
        "kcl": None, "step": 9600.0, "stl": 9600.0, "tolerance_rel": 0.002,
        "kcl_vs_step_rel": None, "stl_vs_step_rel": 0.0,
        "engine_missing": True, "engine_class": "kcl", "ok": False,
    }
    ctx.stage_file("inspect").write_text(json.dumps(ins))
    fb = gates.evaluate(ctx)
    by_id = {g["id"]: g for g in fb["gates"]}
    assert by_id["export_agreement"]["ok"] is False
    assert "kcl" in by_id["export_agreement"]["evidence"][0].lower()


def test_export_integrity_ignores_optional_glb_flake(tmp_path):
    ctx = make_ctx(tmp_path)
    exp = json.loads(ctx.stage_file("export").read_text())
    exp["ok"] = False
    exp["errors"] = {"glb": "modeling connection interrupted; please reconnect and retry"}
    exp["files"].pop("glb", None)
    ctx.stage_file("export").write_text(json.dumps(exp))
    fb = gates.evaluate(ctx)
    by_id = {g["id"]: g for g in fb["gates"]}
    assert by_id["export_integrity"]["ok"] is True, by_id["export_integrity"]
    assert fb["ok"], fb["failed"]


def test_missing_stage_makes_gates_not_applicable_and_traceability_fail(tmp_path):
    ctx = make_ctx(tmp_path)
    ctx.stage_file("edit").unlink()
    fb = gates.evaluate(ctx)
    by_id = {g["id"]: g for g in fb["gates"]}
    assert by_id["edit_robustness"]["ok"] is None
    assert by_id["traceability"]["ok"] is False
    assert not fb["ok"]


def test_benchy_export_failures_are_retryable_not_tier_a(tmp_path):
    ctx = make_benchy_ctx(tmp_path)
    fb = gates.evaluate(ctx)
    assert fb["tier_a_failed"] == []
    assert fb["retryable_failed"] == ["export_agreement", "export_integrity"]
    assert set(fb["failed"]) == {"export_agreement", "export_integrity"}
    msg = gates.correction_message(ctx, fb)
    assert "open ring at z = 37" in msg
    assert "32" in msg
    assert "kcl_vs_step_rel" in msg
    assert "Codex Open questions:" in msg
    assert "hide construction regions" in msg


def test_kcl_engine_export_agreement_is_not_retryable(tmp_path):
    ctx = make_ctx(tmp_path)
    ver = json.loads(ctx.stage_file("verify").read_text())
    ver["engine"] = {"status": "missing", "class": "kcl"}
    ctx.stage_file("verify").write_text(json.dumps(ver))
    ins = json.loads(ctx.stage_file("inspect").read_text())
    ins["agreement"] = {
        "kcl": None, "step": 9600.0, "stl": 9600.0, "tolerance_rel": 0.002,
        "kcl_vs_step_rel": None, "stl_vs_step_rel": 0.0,
        "engine_missing": True, "engine_class": "kcl", "ok": False,
    }
    ctx.stage_file("inspect").write_text(json.dumps(ins))
    fb = gates.evaluate(ctx)
    assert "export_agreement" in fb["failed"]
    assert "export_agreement" not in fb["retryable_failed"]
    assert fb["tier_a_failed"] == []


def test_manifold_witness_volume_matches_a_box(tmp_path):
    """The Manifold kernel volume rides along in analyze_mesh (disclosed in export_agreement); skipped when manifold3d is absent."""
    pytest.importorskip("manifold3d")
    box = trimesh.creation.box(extents=(10, 6, 2))
    path = tmp_path / "box.stl"
    box.export(path)
    a = analyze_mesh(path)
    assert abs(a["manifold_volume"] - 120.0) < 1e-3 and abs(a["volume"] - 120.0) < 1e-3
    open_tri = trimesh.Trimesh(vertices=[[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 2.0, 0.0]], faces=[[0, 1, 2]], process=False)
    open_tri.export(tmp_path / "open.stl")
    assert analyze_mesh(tmp_path / "open.stl")["manifold_volume"] in (None, 0.0)


def test_analyze_mesh_reports_open_edge_ring(tmp_path):
    m = trimesh.Trimesh(
        vertices=[[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 2.0, 0.0]],
        faces=[[0, 1, 2]],
        process=False,
    )
    path = tmp_path / "open.stl"
    m.export(path)
    a = analyze_mesh(path)
    assert a["watertight"] is False
    assert a["open_edges"]["count"] == 3
    assert a["open_edges"]["centroid"] == [0.6667, 0.6667, 0.0]


def test_hygiene_counts_numeric_literals_and_folds_the_limit_into_ok(tmp_path, monkeypatch):
    from opencad.backends.build123d.lang import Build123dLanguage
    from opencad.backends.pythonlang import _tree, source_size

    monkeypatch.delenv("OPENCAD_MAX_SOURCE_LINES", raising=False)
    monkeypatch.delenv("OPENCAD_MAX_SOURCE_LITERALS", raising=False)
    part = tmp_path / "bracket"
    shutil.copytree(PARTS.parent / "build123d" / "bracket", part)
    lang, c = Build123dLanguage(), load_contract(DESIGNS / "bracket")
    hyg = lang.check(part, c)["hygiene"]
    assert hyg["ok"] and hyg["source_size"]["ok"] and hyg["numeric_literals"] == hyg["source_size"]["numeric_literals"] > 0
    monkeypatch.setenv("OPENCAD_MAX_SOURCE_LITERALS", "5")
    hyg = lang.check(part, c)["hygiene"]
    assert not hyg["ok"] and not hyg["source_size"]["ok"] and hyg["source_size"]["max_literals"] == 5
    monkeypatch.delenv("OPENCAD_MAX_SOURCE_LITERALS")
    traced, table = tmp_path / "traced", tmp_path / "table"
    traced.mkdir()
    table.mkdir()
    (traced / "main.py").write_text("PTS = [\n" + "".join(f"    ({i * 0.1:.1f}, {i * 0.2:.1f}),\n" for i in range(3500)) + "]\n")
    (table / "main.py").write_text("ROWS = [\n" + "".join(f"    ({i}.0, {i}.5),\n" for i in range(2000)) + "]\n")  # a 2,000-row coordinate table stays legal
    big, ok = source_size(_tree(traced)), source_size(_tree(table))
    assert big["numeric_literals"] == 7000 and not big["ok"]
    assert ok["numeric_literals"] == 4000 and ok["ok"]


def test_traced_geometry_fails_hygiene_and_independence_and_briefs_the_worker(tmp_path):
    ctx = make_ctx(tmp_path)
    ver = json.loads(ctx.stage_file("verify").read_text())
    ver["hygiene"].update(ok=False, lines=34617, source_size={"lines": 34617, "numeric_literals": 34358, "max_lines": 4000, "max_literals": 6000, "ok": False})
    ctx.stage_file("verify").write_text(json.dumps(ver))
    fb = gates.evaluate(ctx)
    by_id = {g["id"]: g for g in fb["gates"]}
    assert by_id["independence"]["ok"] is False and by_id["source_hygiene"]["ok"] is False
    assert any("traced geometry (34617 lines, 34358 numeric literals; limits 4000/6000)" in e for e in by_id["independence"]["evidence"])
    assert "source_hygiene" in fb["retryable_failed"], "a traced source earns a correction turn"
    msg = gates.correction_message(ctx, fb)
    assert "the source embeds traced geometry" in msg and "never point lists" in msg


def test_a_build_killed_for_memory_is_the_models_failure(tmp_path):
    from opencad.stages import pipeline

    ctx = make_ctx(tmp_path)
    err = "build123d runner failed (-9):\nkilled: RSS 9.1 GB exceeded the engine memory budget 8.0 GB (OPENCAD_ENGINE_MEM_GB)"
    ver = json.loads(ctx.stage_file("verify").read_text())
    ver["engine"] = {"status": "missing", "class": "memory", "error": err}
    ctx.stage_file("verify").write_text(json.dumps(ver))
    exp = json.loads(ctx.stage_file("export").read_text())
    exp.update(ok=False, errors={"step": err})
    ctx.stage_file("export").write_text(json.dumps(exp))
    ctx.stage_file("inspect").write_text(json.dumps({"ok": False, "skipped": True, "class": "memory", "error": "export produced no STEP (memory)"}))
    assert pipeline.program_failed(ctx) and not pipeline.tooling_failed(ctx)
    msg = gates.correction_message(ctx, gates.evaluate(ctx))
    assert "THE BUILD WAS KILLED FOR MEMORY" in msg and "never point lists" in msg


def _column(length: float) -> trimesh.Trimesh:
    return trimesh.creation.box(extents=(20, 20, length), transform=trimesh.transformations.translation_matrix((0, 0, length / 2)))


def test_deviation_bands_locate_a_candidate_short_at_one_end(tmp_path):
    from opencad.geomcheck.mesh import deviation

    _column(80).export(tmp_path / "cand.stl")
    _column(100).export(tmp_path / "ref.stl")
    dev = deviation(tmp_path / "cand.stl", tmp_path / "ref.stl", samples=6000, map_path=tmp_path / "map.png")
    assert dev["axis"] == "z" and len(dev["bands"]) == 10
    by_lo = {round(b["lo"]): b for b in dev["bands"]}
    assert by_lo[90]["inside_p95"] > 15 and by_lo[90]["outside_p95"] < 0.5, "the missing end reads as the model lying inside the reference"
    assert by_lo[80]["p95"] > 5
    assert all(by_lo[z]["p95"] < 0.05 for z in range(0, 80, 10)), "the length that matches is clean"
    top = dev["worst"][0]
    assert top["box"][0][2] > 85 and top["max"] > 15 and top["inside_p95"] > 15
    assert Path(dev["map"]).stat().st_size > 10_000


def _failing_deviation(map_path: Path) -> dict:
    bands = [{"lo": 10.0 * i, "hi": 10.0 * (i + 1), "n": 100, "p95": 0.1, "max": 0.2, "outside_p95": 0.1, "inside_p95": 0.05, "ok": True} for i in range(10)]
    bands[9].update(p95=12.4, max=20.0, inside_p95=12.4, outside_p95=0.0, ok=False)
    return {"reference": "reference/reference.ply", "declared": True, "ok": False, "axis": "z", "p95": 3.2, "hausdorff_estimate": 20.0, "silhouette_iou_min": 0.9,
            "checks": {"p95": {"max": 0.5, "measured": 3.2, "ok": False}}, "bands": bands, "worst_share": 0.02, "map": str(map_path),
            "worst": [{"box": [[-10, -10, 99.5], [10, 10, 100]], "n": 240, "p95": 20.0, "max": 20.0, "outside_p95": 0.0, "inside_p95": 20.0}]}


def test_a_failing_deviation_briefs_its_bands_worst_region_map_and_the_reference_stations(tmp_path):
    ctx = make_ctx(tmp_path)
    design = tmp_path / "designs" / "coupon"
    shutil.copytree(ctx.design_dir, design)
    (design / "reference").mkdir(exist_ok=True)
    (design / "reference" / "reference.json").write_text(json.dumps({"measurements": {"stations": {"axis": "z", "sections": []}}}))
    ctx = Ctx("coupon", design, design / "contract.yaml", ctx.contract, ctx.results_dir, ctx.part_dir)
    ins = json.loads(ctx.stage_file("inspect").read_text())
    ins["deviation"] = _failing_deviation(tmp_path / "deviation-map.png")
    ctx.stage_file("inspect").write_text(json.dumps(ins))
    assert gates.failing_item_names(ins) == ["deviation", "deviation/z=90.0..100.0"], "a band over the limit is a failing item: the loop sees it move"
    fb = gates.evaluate(ctx)
    assert "reference_fidelity" in fb["failed"]
    msg = gates.correction_message(ctx, fb)
    assert "- reference deviation FAIL: p95 3.200 (limit 0.5) FAIL; signed map " in msg
    assert "- deviation band z=90.0..100.0 mm: p95 12.40 max 20.00; model up to 12.40 mm inside and 0.00 mm outside the reference" in msg
    assert "- worst 2 % of deviation samples: box [-10, -10, 99.5]..[10, 10, 100] (240 samples) max 20.00" in msg
    assert "deviation band z=0.0..10.0" not in msg, "bands within the limit stay out of the brief"
    assert "measurements.stations" in msg


def test_quick_prints_the_deviation_bands_and_draws_the_map(tmp_path, capsys):
    import yaml
    from build123d import Box, Pos

    from opencad import quick
    from opencad.backends.local import write_step, write_stl
    from opencad.paths import CONTRACT_FILE, TEMPLATE

    design = tmp_path / "designs" / "column"
    (design / "reference").mkdir(parents=True)
    _column(100).export(design / "reference" / "reference.ply")
    data = yaml.safe_load((TEMPLATE / CONTRACT_FILE).read_text())
    data["acceptance"]["deviation"] = {"p95_max": 0.5}
    (design / "contract.yaml").write_text(yaml.safe_dump(data))
    shape = (Pos(0, 0, 40) * Box(20, 20, 80)).wrapped
    step = write_step(shape, tmp_path / "work" / "column.step")
    write_stl(shape, step.with_suffix(".stl"))
    quick.run(step, design / "contract.yaml", ledger=tmp_path / "work" / "ledger.jsonl")
    out = capsys.readouterr().out
    assert "- reference deviation FAIL" in out and "- deviation band z=90.0..100.0 mm" in out and "inside" in out
    assert (tmp_path / "work" / "deviation-map.png").exists()


def test_a_cached_inspect_redraws_the_deviation_map_a_restart_cleaned(tmp_path, monkeypatch):
    import yaml
    from build123d import Box, Pos

    from opencad.backends.local import write_step, write_stl
    from opencad.paths import CONTRACT_FILE, TEMPLATE
    from opencad.stages import inspect_stage

    monkeypatch.setenv("OPENCAD_CACHE_DIR", str(tmp_path / "cache"))
    design = tmp_path / "designs" / "column"
    (design / "reference").mkdir(parents=True)
    _column(100).export(design / "reference" / "reference.ply")
    data = yaml.safe_load((TEMPLATE / CONTRACT_FILE).read_text())
    data["acceptance"]["deviation"] = {"p95_max": 0.5}
    (design / "contract.yaml").write_text(yaml.safe_dump(data))
    results = tmp_path / "results" / "column"
    shape = (Pos(0, 0, 40) * Box(20, 20, 80)).wrapped
    step = write_step(shape, results / "export" / "column.step")
    stl = write_stl(shape, results / "export" / "column.stl")
    ctx = Ctx("column", design, design / "contract.yaml", load_contract(design), results, tmp_path / "parts" / "column")
    ctx.write_stage("export", {"ok": True, "files": {"step": {"path": str(step)}, "stl": {"path": str(stl)}}})
    first = inspect_stage.run(ctx)
    (results / "deviation-map.png").unlink()
    again = inspect_stage.run(ctx)
    assert again["cached"] and again["deviation"]["map"] == first["deviation"]["map"] and (results / "deviation-map.png").exists()

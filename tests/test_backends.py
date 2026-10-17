"""Registry, backend-rooted paths, STL render, and the one-run `Engine.build` path (the build tests call the CadQuery engine)."""

from __future__ import annotations

import math
import os

import pytest
import trimesh

from opencad.backends.registry import available, current_id, get, set_backend
from opencad.paths import PARTS, RESULTS, PARTS_BASE, RESULTS_BASE, parts_root, results_root
from opencad import render


def test_registry_default_is_build123d(monkeypatch):
    monkeypatch.delenv("OPENCAD_BACKEND", raising=False)
    assert current_id() == "build123d" and parts_root() == PARTS_BASE / "build123d"
    be = get()
    assert be.id == "build123d"
    assert be.language.entry == "main.py"
    assert get("zoo").language.suffixes == (".kcl",)
    assert "zoo" in available()
    for bid in ("cadquery", "build123d", "freecad"):
        assert bid in available()
        assert get(bid).language.entry == "main.py"


def test_set_backend_rejects_unknown(monkeypatch):
    monkeypatch.delenv("OPENCAD_BACKEND", raising=False)
    with pytest.raises(KeyError, match="unknown backend"):
        get("nope")


def test_paths_follow_backend_env(monkeypatch):
    monkeypatch.setenv("OPENCAD_BACKEND", "zoo")
    assert parts_root() == PARTS_BASE / "zoo"
    assert results_root() == RESULTS_BASE / "zoo"
    assert (PARTS / "coupon") == PARTS_BASE / "zoo" / "coupon"
    assert (RESULTS / "coupon") == RESULTS_BASE / "zoo" / "coupon"
    monkeypatch.setenv("OPENCAD_BACKEND", "cadquery")
    assert parts_root() == PARTS_BASE / "cadquery"
    assert (PARTS / "bracket") == PARTS_BASE / "cadquery" / "bracket"


def test_render_snapshots_subdivide_the_mesh_once(monkeypatch, tmp_path):
    """Every view shades the same subdivided mesh: one `_fine` per snapshot set, not one per view."""
    trimesh.creation.box(extents=(10, 6, 2)).export(tmp_path / "box.stl")
    calls = []
    real = render._fine
    monkeypatch.setattr(render, "_fine", lambda m, *a, **k: calls.append(1) or real(m, *a, **k))
    snaps = render.render_snapshots(tmp_path / "box.stl", tmp_path / "snaps", ("front", "top", "iso"), px=80)
    assert len(calls) == 1 and all(os.path.isfile(snaps[k]) for k in ("front", "top", "iso"))


def test_render_snapshots_from_box_stl(tmp_path):
    mesh = trimesh.creation.box(extents=(10, 6, 2))
    stl = tmp_path / "box.stl"
    mesh.export(stl)
    out = tmp_path / "snaps"
    snaps = render.render_snapshots(stl, out, ("iso", "four-ways"), px=120)
    for key in ("front", "top", "right-side", "iso", "four-ways"):
        assert key in snaps and os.path.isfile(snaps[key])
        assert os.path.getsize(snaps[key]) > 100


def test_compare_sheet_pairs_input_renders_with_part_views(tmp_path):
    """Input renders (front.png, right.png, <body>-top.png) sit beside the part's views; a same-shape render scores IoU ~1, a different one lower."""
    box = trimesh.creation.box(extents=(10, 6, 2))
    box.export(tmp_path / "box.stl")
    tall = trimesh.creation.cylinder(radius=3, height=10, transform=trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))  # axis along x: a disc from the side
    tall.export(tmp_path / "tall.stl")
    snaps = render.render_snapshots(tmp_path / "box.stl", tmp_path / "snaps", ("front", "top", "right-side"), px=160)
    ref_dir = tmp_path / "sources"
    render.render_snapshots(tmp_path / "box.stl", tmp_path / "ref-box", ("front", "top"), px=200)
    render.render_snapshots(tmp_path / "tall.stl", tmp_path / "ref-tall", ("right-side",), px=200)
    ref_dir.mkdir()
    os.replace(tmp_path / "ref-box" / "view-front.png", ref_dir / "front.png")
    os.replace(tmp_path / "ref-box" / "view-top.png", ref_dir / "body-top.png")
    os.replace(tmp_path / "ref-tall" / "view-right-side.png", ref_dir / "right.png")
    (ref_dir / "section-z1.png").write_bytes((ref_dir / "front.png").read_bytes())  # never a view
    refs = render.reference_renders(ref_dir)
    assert sorted(refs) == ["front", "right-side", "top"]
    out = render.compare_sheet(tmp_path / "snaps", refs, tmp_path / "view-compare.png")
    assert out and os.path.getsize(out) > 1000
    ious = render.reference_silhouettes(tmp_path / "snaps", refs)
    assert ious["front"] > 0.95 and ious["top"] > 0.95, ious  # same box at another framing
    assert ious["right-side"] < 0.9, ious  # a disc against the box's rectangle: shape, not framing, drives the number
    assert "front" in snaps and render.compare_sheet(tmp_path / "snaps", {}, tmp_path / "none.png") is None


def test_render_nine_views_crease_and_symmetry_heatmap(tmp_path):
    from opencad.schemas import PartContract
    from opencad.paths import TEMPLATE
    import yaml

    mesh = trimesh.creation.box(extents=(10, 6, 2))
    stl = tmp_path / "box.stl"
    mesh.export(stl)
    segs = render._crease_segments(mesh, render.VIEWS["iso"])
    assert len(segs) == 12
    raw = yaml.safe_load((TEMPLATE / "contract.yaml").read_text())
    raw["acceptance"]["symmetry"] = [{"name": "mirrorY", "plane": "y", "at": 0}]
    contract = PartContract.model_validate(raw)
    snaps = render.render_snapshots(stl, tmp_path / "snaps", render.DEFAULT_VIEWS, px=80, contract=contract)
    for key in render.DEFAULT_VIEWS:
        assert key in snaps and os.path.getsize(snaps[key]) > 100
    assert "all" in snaps and os.path.getsize(snaps["all"]) > 100
    assert "symmetry" in snaps and os.path.getsize(snaps["symmetry"]) > 100


BOX = "import cadquery as cq\n\nresult = cq.Workplane('XY').box(10, 20, 30)\n"


def _cq_ctx(tmp_path, monkeypatch):
    from opencad.contract import template_contract
    from opencad.orchestrator import Ctx

    monkeypatch.setenv("OPENCAD_BACKEND", "cadquery")
    design = tmp_path / "designs" / "demo"
    design.mkdir(parents=True)
    ctx = Ctx("demo", design, design / "contract.yaml", template_contract(), tmp_path / "results" / "demo", tmp_path / "parts" / "demo", 600, "cadquery")
    ctx.part_dir.mkdir(parents=True)
    ctx.results_dir.mkdir(parents=True)
    ctx.entry.write_text(BOX)
    return ctx


def test_build_writes_every_output_from_one_engine_run(tmp_path):
    """analyze, a canonical STEP and the STL from one CadQuery runner process (engine call)."""
    from opencad.backends.local import reset_ledger

    entry = tmp_path / "main.py"
    entry.write_text(BOX)
    reset_ledger("cadquery")
    r = get("cadquery").engine.build(entry, step=tmp_path / "o" / "main.step", stl=tmp_path / "o" / "main.stl", density_kg_m3=1000)
    rows = reset_ledger("cadquery")
    assert len(rows) == 1 and rows[0]["timings"]["stl_s"] >= 0 and rows[0]["startup_s"] >= 0
    assert r["analyze"]["volume_mm3"] == pytest.approx(6000) and r["analyze"]["mass_g"] == pytest.approx(6.0)
    assert r["step"].is_file() and r["stl"].is_file() and r["fcstd"] is None and "1970-01-01T00:00:00" in r["step"].read_text()[:3000]


def test_verify_and_export_share_one_build_and_finalize_runs_no_engine(monkeypatch, tmp_path):
    """verify's analyze and export's STEP + STL come from one engine run; finalize takes determinism from the edit stage's restore
    re-export of the same STEP and converts the STL to GLB (engine call)."""
    from opencad.stages import export, verify

    ctx = _cq_ctx(tmp_path, monkeypatch)
    eng = ctx.backend.engine
    calls: list = []
    real = eng.build
    monkeypatch.setattr(eng, "build", lambda entry, **kw: calls.append(entry) or real(entry, **kw))
    eng.reset_ledger()
    v = verify.run(ctx)
    e = export.run(ctx)
    assert calls == [ctx.entry] and v["analyze"]["volume_mm3"] == pytest.approx(6000) and e["ok"]
    assert len(ctx.load_stage("verify")["engine_calls"]) == 1 and ctx.load_stage("export")["engine_calls"] == []
    sha = e["files"]["step"]["sha256"]
    ctx.write_stage("edit", {"ok": True, "restore": {"baseline_sha256": sha, "re_export_sha256": sha, "ok": True}})
    monkeypatch.setattr(eng, "export", lambda *a, **k: pytest.fail("finalize ran the engine"))
    f = export.finalize(ctx)
    step = f["files"]["step"]
    assert step["deterministic"] is True and step["determinism_source"] == "edit restore re-export" and f["files"]["glb"]["bytes"] > 0
    assert calls == [ctx.entry] and set(f["finalize_timings"]) == {"determinism_s", "glb_s"}


def test_quick_builds_step_and_stl_once_and_ledgers_the_engine_rows(monkeypatch, tmp_path):
    """A cache miss on both formats is one engine build; the order ledger gets the engine's own rows (start, startup) (engine call)."""
    from opencad import quick

    monkeypatch.setenv("OPENCAD_BACKEND", "cadquery")
    monkeypatch.setenv("OPENCAD_ENGINE_CACHE", str(tmp_path / "cache"))
    entry = tmp_path / "part" / "main.py"
    entry.parent.mkdir()
    entry.write_text(BOX)
    ledger = tmp_path / "engine-ledger.jsonl"
    got = quick.export_cached_many(entry, ("step", "stl"), ledger=ledger)
    assert all(p.is_file() and not hit for p, hit in got.values())
    rows = [__import__("json").loads(line) for line in ledger.read_text().splitlines()]
    assert len(rows) == 1 and rows[0]["via"] == "opencad quick" and rows[0]["started"] and "startup_s" in rows[0]
    again = quick.export_cached_many(entry, ("step", "stl"), ledger=ledger)
    assert all(hit for _, hit in again.values()) and len(ledger.read_text().splitlines()) == 1


def test_freecad_step_cache_keys_on_the_entry_name(monkeypatch, tmp_path):
    """Two entries in one directory are two parts: the deterministic-STEP cache must not hand one the other's export."""
    from pathlib import Path

    eng = get("freecad").engine
    monkeypatch.setenv("OPENCAD_ENGINE_CACHE", str(tmp_path / "cache"))

    def fake_run(entry, **paths):
        Path(paths["export_step"]).write_text(f"ISO-10303-21;\nFILE_NAME('x','t',(''),(''),'','','');\n/* {Path(entry).name} */\n")
        return {"ok": True, "seconds": 0.1, "payload": {}}

    monkeypatch.setattr(eng, "_run", fake_run)
    src = tmp_path / "src"
    src.mkdir()
    for name in ("a.py", "b.py"):
        (src / name).write_text("x = 1\n")
    assert "a.py" in eng.export(src / "a.py", tmp_path / "oa", "step")[0].read_text()
    assert "b.py" in eng.export(src / "b.py", tmp_path / "ob", "step")[0].read_text()


def test_result_bound_inside_a_module_level_block_counts():
    """`with SkipClean(): result = ...` and `with BuildPart() as result:` bind `result` at module scope; a function-local one does not."""
    import ast

    from opencad.backends.pythonlang import _has_result

    assert _has_result(ast.parse("with SkipClean():\n    result = a - b\n"))
    assert _has_result(ast.parse("with BuildPart() as result:\n    Box(1, 1, 1)\n"))
    assert _has_result(ast.parse("if True:\n    result = 1\nelse:\n    result = 2\n"))
    assert not _has_result(ast.parse("def f():\n    result = 1\n    return result\n"))


def test_freecad_build_and_export_share_the_deterministic_step(monkeypatch, tmp_path):
    """freecadcmd's STEP bytes differ run to run: build() and a later deterministic export (the edit stage's restore, finalize's
    re-export) must return the one cached STEP of the source tree."""
    from pathlib import Path

    eng = get("freecad").engine
    monkeypatch.setenv("OPENCAD_ENGINE_CACHE", str(tmp_path / "cache"))
    runs = {"n": 0}

    def fake_run(entry, **paths):
        runs["n"] += 1
        for key in ("export_step", "export_stl"):
            if paths.get(key):
                Path(paths[key]).write_text(f"ISO-10303-21;\nFILE_NAME('x','t',(''),(''),'','','');\n/* run {runs['n']} */\n")
        return {"ok": True, "seconds": 0.1, "payload": {"analyze": {"volume_mm3": 1.0}}}

    monkeypatch.setattr(eng, "_run", fake_run)
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("x = 1\n")
    built = eng.build(src / "main.py", step=tmp_path / "b" / "main.step", stl=tmp_path / "b" / "main.stl")["step"].read_text()
    again = eng.export(src / "main.py", tmp_path / "e", "step")[0].read_text()
    rebuilt = eng.build(src / "main.py", step=tmp_path / "b2" / "main.step")["step"].read_text()
    assert "run 1" in built and again == built == rebuilt

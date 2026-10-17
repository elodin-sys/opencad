"""Zoo assembly sources: a `main.kcl` entry that places staged STEPs, its brief, hygiene, stale-source cleanup and handoff parity checks."""

from __future__ import annotations

import json
from pathlib import Path

from opencad.assembly import AsmCtx
from opencad.schemas import AssemblyContract
from tests.test_assembly_pipeline import CONTRACT

PUMP_LIKE = {**CONTRACT, "parts": [p for p in CONTRACT["parts"] if p["kind"] != "derived"],
             "joints": [j for j in CONTRACT["joints"] if j["child"] != "fluid"], "fluid_volumes": [], "boundaries": [],
             "observables": [], "acceptance": {}}


def _ctx(tmp_path: Path, backend: str) -> AsmCtx:
    contract = AssemblyContract.model_validate(PUMP_LIKE)
    return AsmCtx("t-mixer", tmp_path / "designs" / "t-mixer", contract, tmp_path / "results" / "t-mixer", tmp_path / "parts" / "t-mixer", backend)


def test_entry_follows_the_backend_language(tmp_path):
    assert _ctx(tmp_path, "zoo").entry.name == "main.kcl" and _ctx(tmp_path, "zoo").kcl
    assert _ctx(tmp_path, "build123d").entry.name == "main.py" and not _ctx(tmp_path, "build123d").kcl


def test_zoo_brief_asks_for_kcl_imports_placements_and_the_critic(tmp_path):
    from opencad.assembly.assemble import brief

    text = brief(_ctx(tmp_path, "zoo"))
    assert "main.kcl" in text and 'import "inputs/<name>.step" as <body>' in text and "global = true" in text
    assert "placements.json" in text and "assembly check-source t-mixer --backend zoo" in text
    assert "assigns `result`" not in text
    py = brief(_ctx(tmp_path, "build123d"))
    assert "assigns `result`" in py and "assembly check-source t-mixer --backend build123d" in py


def test_kcl_hygiene(tmp_path):
    from opencad.truth.assembly_agree import kcl_hygiene

    (tmp_path / "main.kcl").write_text('import "inputs/housing.step" as housing\nimport "inputs/t-mixer-rotor.step" as rotor\n')
    allowed = ["housing", "t-mixer-rotor"]
    assert not kcl_hygiene(tmp_path, allowed)["ok"], "no placements.json sidecar"
    (tmp_path / "placements.json").write_text("{}")
    assert kcl_hygiene(tmp_path, allowed)["ok"]
    (tmp_path / "main.kcl").write_text('import "../elsewhere/housing.step" as housing\nx = "truth/cases/a.step"\n')
    h = kcl_hygiene(tmp_path, allowed)
    assert not h["ok"] and h["cad_refs"] and h["truth_refs"]


def test_fresh_assemble_clears_stale_sources(tmp_path):
    from opencad.assembly.pipeline import clear_sources

    (tmp_path / "inputs").mkdir()
    for name in ("main.py", "checkpoint.py", "placements.json", "inputs/base.step", "notes.md"):
        (tmp_path / name).write_text("x")
    clear_sources(tmp_path)
    assert sorted(p.name for p in tmp_path.rglob("*") if p.is_file()) == ["base.step", "notes.md"]


def _snap(volume: float = 100.0, com=(0.0, 0.0, 0.0), flow: float = 6.0, gates: str = "10 pass, 0 fail, 4 n/a", files: bool = True) -> dict:
    return {"files": {"assembly.glb": files, "assembly.html": True}, "placements": True, "bodies": {"a": {"volume": volume, "com": list(com)}},
            "gates": gates, "bbox": [[0, 0, 0], [1, 1, 1]], "observables": {"driveRatio": 0.25, "flowRate": flow}, "glb_nodes": ["a"]}


def test_compare_checks_pass_on_matching_handoffs_and_fail_on_drift():
    from opencad.bakeoff.compare import checks

    assert all(ok for ok, _ in checks("x", _snap(), _snap(), ["a"]))
    bad = {text.split(":")[0].split(" (")[0]: ok for ok, text in checks("x", _snap(volume=101.0, com=(0.5, 0, 0), flow=6.5, files=False), _snap(), ["a"])}
    assert not bad["handoff files present"] and not bad["body a"] and not bad["flowRate 6.5 vs reference 6.0"]


def test_report_package_copies_the_kcl_entry_and_sidecar(tmp_path, monkeypatch):
    from opencad.assembly import report

    actx = _ctx(tmp_path, "zoo")
    actx.part_dir.mkdir(parents=True)
    actx.entry.write_text("// asm\n")
    (actx.part_dir / "placements.json").write_text(json.dumps({}))
    (actx.design_dir).mkdir(parents=True)
    (actx.design_dir / "assembly.yaml").write_text("x: 1\n")
    actx.results_dir.mkdir(parents=True)
    monkeypatch.setattr(report, "part_dir", lambda d, backend=None: tmp_path / "none")
    monkeypatch.setattr(report, "design_dir", lambda d: tmp_path / "none")
    try:
        report.package(actx, {"ok": True})
    except Exception:  # later package sections need evaluator stages this fixture does not run
        pass
    src = actx.results_dir / "package" / "source"
    assert (src / "main.kcl").exists() and (src / "placements.json").exists()

import json
import os
import stat
from pathlib import Path

import pytest

from opencad import zoo
from opencad.backends.zoo import engine as zoo_engine
from opencad.contract import load_contract
from opencad.orchestrator import Ctx
from opencad.paths import DESIGNS, PARTS
from opencad.stages import pipeline, verify


FAKE_ZOO = r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path

state = Path(os.environ["FAKE_ZOO_STATE"])
n = int(state.read_text()) if state.exists() else 0
n += 1
state.write_text(str(n))
mode = os.environ.get("FAKE_ZOO_MODE", "ok")
fails = int(os.environ.get("FAKE_ZOO_FAILS", "0"))
if mode == "transient" and n <= fails:
    print("Error: modeling connection interrupted; please reconnect and retry", file=sys.stderr)
    sys.exit(1)
if mode == "credits":
    print("no API credits available", file=sys.stderr)
    sys.exit(1)
if mode == "kcl":
    print("KCL execution failed: type error on line 1", file=sys.stderr)
    sys.exit(1)
if mode == "blocked":
    print("Failed executing KCL on engine, errors: AuthTokenInvalid Your account is blocked because your payment method failed.")
    sys.exit(1)
if mode == "timeout":
    sys.exit(124)
if "analyze" in sys.argv:
    print(json.dumps({
        "bounding_box": {"center": {"x": 30, "y": 20, "z": 2}, "dimensions": {"x": 60, "y": 40, "z": 4}},
        "volume": {"volume": 9600},
        "surface_area": {"surface_area": 5600},
        "center_of_mass": {"center_of_mass": {"x": 30, "y": 20, "z": 2}},
    }))
    sys.exit(0)
print("ok")
sys.exit(0)
'''


@pytest.fixture
def fake_zoo(tmp_path, monkeypatch):
    script = tmp_path / "zoo"
    script.write_text(FAKE_ZOO)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    state = tmp_path / "state"
    lock = tmp_path / "zoo.lock"
    monkeypatch.setattr(zoo_engine, "zoo_bin", lambda: str(script))
    monkeypatch.setattr(zoo, "zoo_bin", lambda: str(script))
    monkeypatch.setenv("FAKE_ZOO_STATE", str(state))
    monkeypatch.setenv("OPENCAD_ZOO_LOCK", str(lock))
    monkeypatch.setenv("OPENCAD_ZOO_RETRY_BASE", "0")
    zoo.reset_ledger()
    return state


def test_classify_strings():
    assert zoo.classify(zoo.Result(["x"], 0, "ok", "", 0.1)) == "ok"
    assert zoo.classify("modeling connection interrupted; please reconnect and retry") == "transient"
    assert zoo.classify("no API credits available") == "billing"
    assert zoo.classify("this export is not included in your current plan") == "billing"
    assert zoo.classify("AuthTokenInvalid Your account is blocked because your payment method failed.") == "billing"
    assert zoo.classify("KCL execution failed: boom") == "program"
    assert zoo.classify("KCL execution had errors") == "program"
    assert zoo.classify("zoo kcl analyze timed out after 600s", code=124) == "timeout"
    assert zoo.classify(zoo.Result(["x"], 124, "", "timed out after 1s", 1.0)) == "timeout"
    assert zoo.classify("something else") == "unknown"


def test_run_retries_transient_then_succeeds(fake_zoo, monkeypatch):
    monkeypatch.setenv("FAKE_ZOO_MODE", "transient")
    monkeypatch.setenv("FAKE_ZOO_FAILS", "2")
    r = zoo.run(["kcl", "analyze", "x.kcl"], engine=True)
    assert r.ok
    rows = zoo.LEDGER
    assert [row["class"] for row in rows] == ["transient", "transient", "ok"]
    assert [row["attempt"] for row in rows] == [1, 2, 3]
    assert all("seconds" in row for row in rows)
    assert int(fake_zoo.read_text()) == 3


def test_credits_aborts_without_retry(fake_zoo, monkeypatch):
    monkeypatch.setenv("FAKE_ZOO_MODE", "credits")
    r = zoo.run(["kcl", "analyze", "x.kcl"], engine=True)
    assert not r.ok
    assert zoo.classify(r) == "billing"
    assert len(zoo.LEDGER) == 1
    assert zoo.LEDGER[0]["class"] == "billing"
    assert int(fake_zoo.read_text()) == 1
    with pytest.raises(zoo.ZooCreditsError):
        zoo.raise_for(r, "analyze failed")


def test_a_blocked_account_fails_preflight_despite_a_prepaid_balance(fake_zoo, monkeypatch, tmp_path):
    monkeypatch.setenv("FAKE_ZOO_MODE", "blocked")
    monkeypatch.setattr(zoo_engine, "PROBE_CACHE", tmp_path / "probe.json")
    monkeypatch.setattr(zoo_engine, "credits", lambda: {"known": True, "remaining_total": 297953, "can_execute": True})
    pf = zoo_engine.preflight()
    assert not pf["ok"] and pf["class"] == "billing"
    monkeypatch.setenv("FAKE_ZOO_MODE", "ok")
    assert zoo_engine.preflight()["ok"]  # the cached refusal is re-probed once billing is fixed


def test_kcl_error_never_retries(fake_zoo, monkeypatch):
    monkeypatch.setenv("FAKE_ZOO_MODE", "kcl")
    r = zoo.run(["kcl", "analyze", "x.kcl"], engine=True)
    assert not r.ok
    assert zoo.classify(r) == "program"
    assert len(zoo.LEDGER) == 1
    with pytest.raises(zoo.ZooKclError):
        zoo.raise_for(r, "analyze failed")


def test_timeout_never_retries(fake_zoo, monkeypatch):
    monkeypatch.setenv("FAKE_ZOO_MODE", "timeout")
    r = zoo.run(["kcl", "analyze", "x.kcl"], engine=True)
    assert r.code == 124
    assert zoo.classify(r) == "timeout"
    assert len(zoo.LEDGER) == 1


def test_analyze_raises_typed_kcl(fake_zoo, monkeypatch):
    monkeypatch.setenv("FAKE_ZOO_MODE", "kcl")
    with pytest.raises(zoo.ZooKclError) as ei:
        zoo.analyze(Path("x.kcl"))
    assert ei.value.kind == "program"


def test_build_exports_step_and_stl_and_copies_sidecars(tmp_path, monkeypatch):
    src = tmp_path / "asm"
    src.mkdir()
    entry = src / "main.kcl"
    entry.write_text("// assembly\n")
    (src / "placements.json").write_text(json.dumps({"a": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]}))
    (src / "joints.json").write_text(json.dumps({"j": {"origin": [0, 0, 0], "axis": [0, 0, 1]}}))
    calls = []

    def fake_export(target, out_dir, fmt, **kw):
        calls.append((Path(target), fmt))
        out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / f"output.{fmt}"
        p.write_text(fmt)
        return [p]

    monkeypatch.setattr(zoo_engine, "export", fake_export)
    out_dir = tmp_path / "export"
    assert not hasattr(zoo_engine.ZooEngine(), "build"), "part stages read an engine `build` as the local single-run path"
    built = zoo_engine.ZooEngine().build_assembly(entry, analyze=False, step=out_dir / "asm.step", stl=out_dir / "asm.stl")
    assert [fmt for _, fmt in calls] == ["step", "stl"] and all(t == entry for t, _ in calls)
    assert built["step"].read_text() == "step" and built["stl"].read_text() == "stl" and built["analyze"] is None
    assert (out_dir / "placements.json").exists() and (out_dir / "joints.json").exists()


def test_forecast_calls_coupon():
    c = load_contract(DESIGNS / "coupon")
    f = zoo.forecast_calls(c, "verify")
    assert f["breakdown"] == {"analyze": 1, "snapshots": 0, "step": 2, "stl": 1, "glb": 1, "edit_exports": 3}
    assert f["total"] == 8
    assert f["edit_tests"] == 2
    late = zoo.forecast_calls(c, "edit")
    assert late["breakdown"]["analyze"] == 0
    assert late["breakdown"]["edit_exports"] == 3


def test_verify_ok_when_analyze_missing(tmp_path, monkeypatch):
    design = DESIGNS / "coupon"
    ctx = Ctx("coupon", design, design / "contract.yaml", load_contract(design), tmp_path / "results", PARTS / "coupon", 3600, "zoo")
    monkeypatch.setattr(ctx.backend.language, "check", lambda *a, **k: {
        "format": {"ok": True, "findings": []},
        "lint": {"ok": True, "code": 0, "output": ""},
        "hygiene": {
            "ok": True, "kcl_version_2": True, "dialect_ok": True, "default_unit_mm": True, "unit_ok": True,
            "legacy_v1": [], "legacy": [], "parameters_ok": True, "asserts": 1, "forbidden_imports": [],
            "sketch_blocks": 1, "feature_ops": 1, "construction_ops": {"sketch_blocks": 1, "feature_ops": 1},
            "parameters": {},
        },
    })

    def boom(*a, **k):
        raise zoo.ZooError("modeling connection interrupted; please reconnect and retry", kind="transient")

    monkeypatch.setattr(ctx.backend.engine, "analyze", boom)
    out = verify.run(ctx)
    assert out["ok"] is True
    assert out["engine"]["status"] == "missing"
    assert out["engine"]["class"] == "transient"
    assert out["bbox"]["ok"] is None
    assert out["volume"]["ok"] is None
    assert out["analyze_ok"] is False


def test_pipeline_tooling_failed_on_transient_export(tmp_path):
    from tests.test_gates import make_ctx

    ctx = make_ctx(tmp_path)
    exp = json.loads(ctx.stage_file("export").read_text())
    exp["ok"] = False
    exp["errors"] = {"step": "modeling connection interrupted; please reconnect and retry"}
    ctx.stage_file("export").write_text(json.dumps(exp))
    assert pipeline.tooling_failed(ctx) is True


def test_pipeline_tooling_failed_on_kcl_is_false(tmp_path):
    from tests.test_gates import make_ctx

    ctx = make_ctx(tmp_path)
    ver = json.loads(ctx.stage_file("verify").read_text())
    ver["engine"] = {"status": "missing", "class": "kcl"}
    ctx.stage_file("verify").write_text(json.dumps(ver))
    assert pipeline.tooling_failed(ctx) is False

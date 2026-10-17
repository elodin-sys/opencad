import math

import numpy as np
import pytest

from opencad.truth import performance
from opencad.truth.manifest import CaseManifest, PerformanceObservable


def perf(**kw):
    return PerformanceObservable(**{"id": "rise", "quantity": "pressure_rise", "unit": "Pa", "evidence": "A", **kw})


def test_z_score_with_numerical_uncertainty(tmp_path):
    p = perf(value=1000.0, uncertainty=30.0, z_max=2.0)
    ok = performance.check(p, {"status": "ok", "value": 1050.0, "u_numerical": 40.0}, tmp_path)
    assert ok["ok"] and ok["z"] == pytest.approx(50 / math.hypot(30, 40))
    bad = performance.check(p, {"status": "ok", "value": 1200.0}, tmp_path)
    assert not bad["ok"] and bad["z"] == pytest.approx(200 / 30)


def test_exact_reference_uses_a_tolerance_and_series_use_rms_z(tmp_path):
    exact = perf(id="ratio", quantity="transmission_ratio", unit="", evidence="C", value=-0.5, tolerance=1e-6)
    assert performance.check(exact, {"status": "ok", "value": -0.5}, tmp_path)["ok"]
    (tmp_path / "truth").mkdir()
    (tmp_path / "truth" / "p.csv").write_text("x,p\n0,1\n1,2\n2,3\n", encoding="utf-8")
    s = perf(id="profile", quantity="pressure", unit="MPa", series="truth/p.csv", uncertainty=0.1)
    row = performance.check(s, {"status": "ok", "series": {"x": [0, 2], "y": [1.1, 3.1]}}, tmp_path)
    assert row["ok"] and row["points"] == 3 and row["z_rms"] == pytest.approx(1.0)


def test_unavailable_extension_and_missing_predictions():
    un = perf(id="c3diffuser", status="unavailable", note="C3 has no diffuser data")
    ext = perf(id="stress", evidence="X", quantity="max_von_mises")
    rows = performance.score([un, ext, perf(value=1.0, uncertainty=0.1)], {"rise": {"status": "unavailable", "reason": "no solver"}}, None)
    assert [r["status"] for r in rows] == ["unavailable", "extension", "no-prediction"]
    assert [r["required"] for r in rows] == [False, False, True]
    assert performance.verdict([], rows) == "INCOMPLETE"
    rows[2]["prediction_status"] = "missing"
    assert performance.verdict([], rows) == "FAIL"
    assert performance.verdict([{"required": True, "ok": False}], []) == "FAIL"


def test_an_unresolved_prediction_never_passes_however_wide_its_uncertainty(tmp_path):
    p = perf(value=126.46, uncertainty=2.98)  # FAN-01 attempt 3 at q1403: 89.8 Pa with the 57 % level change as u_numerical gave z 0.71
    pred = {"status": "ok", "value": 89.8, "u_numerical": 51.5, "resolved": False, "unresolved_because": ["GCI 1.63 > 0.05"], "simulation": "mrfDesign"}
    row = performance.check(p, pred, tmp_path)
    assert row["status"] == "unresolved" and row["ok"] is None and row["z"] < 2 and row["resolved"] is False and row["simulation"] == "mrfDesign"
    assert performance.verdict([], [row]) == "INCOMPLETE"
    held = performance.check(perf(id="q1804", value=63.95, uncertainty=7.52, split="held_out"), {"status": "ok", "value": 86.4}, tmp_path)
    assert held["ok"] is False and "resolved" not in held and performance.verdict([], [row, held]) == "FAIL"
    assert performance.by_split([row, held]) == {"development": {"required": 1, "pass": 0, "fail": 0, "unresolved": 1, "missing": 0},
                                                "held_out": {"required": 1, "pass": 0, "fail": 1, "unresolved": 0, "missing": 0}}
    resolved = performance.check(p, {**pred, "value": 125.0, "u_numerical": 3.0, "resolved": True}, tmp_path)
    assert resolved["ok"] and resolved["status"] == "scored" and performance.verdict([], [resolved]) == "PASS"


def test_the_envelope_aggregates_by_solver_and_quantity_and_a_report_quotes_it():
    from opencad.assembly.report import validation_basis
    from opencad.truth.report import envelope

    def row(machine, rel, split="development", ok=True, status="scored", resolved=None, solver="openfoam", quantity="pressure_rise"):
        return {"machine": machine, "solver": solver, "quantity": quantity, "split": split, "evidence": "A", "ok": ok, "status": status, "resolved": resolved,
                "relative_error": rel, "z": abs(rel) * 10}

    rows = [row("fda-pump", 0.10, resolved=True), row("fda-pump", 0.20, "held_out", ok=False), row("fan-01", -0.3, ok=None, status="unresolved", resolved=False),
            row("gear-train", 0.0, solver="evaluator", quantity="transmission_ratio"), {**row("x", 1.0), "status": "unavailable"}]
    env = envelope(rows)
    cfd = next(e for e in env if e["solver"] == "openfoam")
    assert cfd["points"] == 3 and (cfd["development"], cfd["held_out"]) == (2, 1) and cfd["machines"] == ["fan-01", "fda-pump"]
    assert cfd["bias"] == pytest.approx(0.0) and cfd["spread"] == pytest.approx(np.std([0.1, 0.2, -0.3])) and cfd["max_abs_error"] == pytest.approx(0.3)
    assert (cfd["passed"], cfd["failed"], cfd["unresolved"], cfd["resolved"], cfd["no_mesh_estimate"]) == (1, 1, 1, 1, 1)
    text = validation_basis("openfoam", "pressure_rise", env)
    assert text.startswith("3 points (2 dev / 1 held-out) on fan-01, fda-pump: bias +0.0 %") and "1 unresolved" in text
    assert validation_basis("openfoam", "torque", env) == "unvalidated: no scored machine case uses openfoam for torque"


def test_manifest_rules_for_machine_cases():
    base = {"id": "m", "title": "t", "truth_class": "A", "role": "validation", "source": {"citation": "c", "accessed": "2026-09-25"}, "intent": "i",
            "inputs": [], "truth": [], "arms": [{"id": "a", "design": "m", "inputs": []}], "observables": []}
    with pytest.raises(ValueError, match="belong to machine cases"):
        CaseManifest.model_validate({**base, "performance": [{"id": "x", "quantity": "q", "unit": "", "evidence": "C", "value": 1.0, "tolerance": 0.1}]})
    with pytest.raises(ValueError, match="uncertainty"):
        CaseManifest.model_validate({**base, "kind": "machine", "performance": [{"id": "x", "quantity": "q", "unit": "", "evidence": "A", "value": 1.0}]})
    m = CaseManifest.model_validate({**base, "kind": "machine", "arms": [{"id": "a", "design": "m", "inputs": [], "mode": "analysis"}],
                                     "performance": [{"id": "x", "quantity": "q", "unit": "", "evidence": "N", "value": 1.0, "uncertainty": 0.1}]})
    assert m.arms[0].mode == "analysis"

"""Numerical uncertainty of a prediction: iteration averaging, the grid-convergence index on analytic ladders, the rules that
decide whether a prediction is resolved, and OpenFOAM histories and refinement regions (no container)."""

import math
from types import SimpleNamespace

import numpy as np
import pytest
from test_sim_openfoam import _case, _duct

from opencad.schemas import RefinementLevel, Simulation
from opencad.sim import DRIFT_MAX, gci, openfoam, refinement, study, tail


def test_tail_mean_spread_and_drift_of_an_oscillating_history():
    it = np.arange(1, 1501)
    y = 100.0 + 4.0 * np.sin(it / 7.0)
    st = tail(y)
    assert st["samples"] == 300 and st["mean"] == pytest.approx(100.0, abs=0.1) and st["std"] == pytest.approx(4 / math.sqrt(2), rel=0.02)
    assert st["drift"] < DRIFT_MAX and st["last"] == y[-1]
    assert tail(y + 0.01 * it)["drift"] > DRIFT_MAX
    assert tail([5.0]) == {"mean": 5.0, "std": 0.0, "drift": None, "samples": 1, "last": 5.0}


@pytest.mark.parametrize("p, r", [(2.0, [1.5, 1.5]), (1.3, [1.4, 1.3])])
def test_gci_recovers_the_order_and_the_exact_value_of_a_power_law(p, r):
    h = [1.0, 1.0 / r[0], 1.0 / (r[0] * r[1])]
    f = [10.0 + 3.0 * x ** p for x in h]
    g = gci(f, r)
    assert g["convergence"] == "monotone" and g["order"] == pytest.approx(p, rel=1e-6)
    assert g["extrapolated"] == pytest.approx(10.0, rel=1e-6) and g["fs"] == 1.25
    assert g["gci"] == pytest.approx(1.25 * abs(f[1] - f[2]) / f[2] / (r[1] ** p - 1), rel=1e-6)


def test_gci_is_conservative_for_pairs_oscillation_and_a_faster_than_formal_order():
    pair = gci([12.0, 11.0], [1.4])
    assert pair["convergence"] == "pair" and pair["gci"] == pytest.approx(3.0 * 1.0 / 11.0 / (1.4 ** 2 - 1))
    osc = gci([10.0, 12.0, 11.0], [1.4, 1.4])
    assert osc["convergence"] == "oscillatory" and osc["gci"] == pytest.approx(3.0 * 2.0 / 11.0 / (1.4 ** 2 - 1))
    assert gci([10.0, 11.0, 13.0], [1.4, 1.4])["convergence"] == "divergent"
    fast = gci([10.0 + 3.0, 10.0 + 3.0 / 2 ** 4, 10.0 + 3.0 / 4 ** 4], [2.0, 2.0])  # p = 4 is used as 2
    assert fast["order"] == pytest.approx(4.0) and fast["gci"] == pytest.approx(1.25 * (3 / 16 - 3 / 256) / (10 + 3 / 256) / 3)
    assert gci([1.0, 1.0], [1.4])["gci"] == 0.0 and gci([1.0, 2.0], [1.0])["convergence"] == "degenerate"


def _rows(values, factors=(1.0, 0.7, 0.5), regions=None, **kw):
    return [{"label": f"{f:g}", "factor": f, "regions": (regions or [{}] * len(values))[i], "value": v, "cells": None, **kw}
            for i, (f, v) in enumerate(zip(factors, values))]


def test_a_prediction_is_resolved_only_on_a_finished_converging_ladder():
    good = study(_rows([110.0, 104.0, 102.0], u_iteration=0.5, drift=0.001), expected=3, tolerance=0.05)
    assert good["resolved"] and good["u_numerical"] == pytest.approx(math.hypot(good["u_discretisation"], 0.5))
    assert good["u_discretisation"] == pytest.approx(good["gci"] * 102.0) and good["extrapolated"] < 102.0
    killed = study(_rows([110.0, 104.0]), expected=3, tolerance=0.05)
    assert not killed["resolved"] and "1 of 3 mesh levels did not finish" in killed["unresolved_because"]
    assert study(_rows([110.0]), expected=3, tolerance=0.05)["resolved"] is False
    one = study(_rows([110.0], u_iteration=2.0), expected=1, tolerance=0.05)
    assert one["resolved"] is None and one["u_numerical"] == 2.0 and one["u_discretisation"] is None
    drifting = study(_rows([110.0, 104.0, 102.0], drift=0.02), expected=3, tolerance=0.05)
    assert not drifting["resolved"] and "trends" in drifting["unresolved_because"][0]
    # FDA C5 level 0.7 at 3000 iterations: the mean moved 2.4 % inside its own 2.9 % spread, an oscillation without a trend
    oscillating = study(_rows([110.0, 104.0, 102.0], drift=0.024, u_iteration=0.029 * 102), expected=3, tolerance=0.05)
    assert oscillating["resolved"] and oscillating["u_numerical"] == pytest.approx(math.hypot(oscillating["u_discretisation"], 0.029 * 102))
    noisy = study(_rows([110.0, 104.0, 102.0], drift=0.024, u_iteration=0.045 * 102), expected=3, tolerance=0.05)
    assert not noisy["resolved"] and noisy["unresolved_because"] == [f"u_numerical {noisy['u_numerical'] / 102:.3g} of the value > 0.05 (the iteration spread)"]
    wide = study(_rows([141.0, 90.0]), expected=2, tolerance=0.05)
    assert not wide["resolved"] and wide["gci"] > 1.0  # FAN-01 attempt 3: 57 % between the levels is no pass however wide u_numerical is
    tip = study(_rows([141.0, 120.0, 118.0], factors=(1.0, 1.0, 1.0), regions=[{}, {"tip": 1}, {"tip": 2}]), expected=3, tolerance=0.05)
    assert tip["steps"] == ["regional", "regional"] and tip["ratios"] == [2.0, 2.0] and not tip["resolved"]
    assert any("only inside regions" in w for w in tip["unresolved_because"])
    ref = refinement({"a": good, "b": killed}, 0.05, ["b level 0.5 was killed"])
    assert not ref["ok"] and ref["unresolved"] == ["b"] and ref["gci_max"] == killed["gci"]


def test_global_steps_use_the_cell_counts():
    rows = _rows([110.0, 104.0, 102.0])
    for row, n in zip(rows, (1e6, 2.7e6, 7.29e6)):
        row["cells"] = n
    st = study(rows, expected=3, tolerance=0.05)
    assert st["ratios"] == pytest.approx([1.3925, 1.3925], rel=1e-3) and st["steps"] == ["global", "global"]


def test_refinement_levels_parse_label_and_validate():
    s = Simulation.model_validate({"id": "cfd", "physics": "cfd_steady", "solver": "openfoam", "regions": [{"name": "tip", "shape": "rotor_tip"}],
                                   "refinement": [1.0, {"factor": 1.0, "regions": {"tip": 1}, "iterations": 3000}, {"factor": 1.0, "regions": {"tip": 2}}]})
    assert [lv.label for lv in s.levels()] == ["1", "1-tip1", "1-tip2"] and s.levels()[1].iterations == 3000
    assert RefinementLevel(factor=0.7).label == "0.7"
    with pytest.raises(ValueError, match="unknown regions"):
        Simulation.model_validate({"id": "c", "physics": "cfd_steady", "solver": "openfoam", "refinement": [{"factor": 1.0, "regions": {"gap": 1}}]})
    with pytest.raises(ValueError, match="needs"):
        Simulation.model_validate({"id": "c", "physics": "cfd_steady", "solver": "openfoam", "regions": [{"name": "b", "shape": "box"}]})


def test_a_study_runs_one_case_of_a_simulation_with_its_overrides():
    from opencad.contract import load_assembly
    from opencad.paths import DOCS
    from opencad.sim.cli import simulation

    a = load_assembly(DOCS / "exemplar-assembly.yaml")
    s = simulation(a, "cfd", "design", levels='[1.0, {"factor": 0.7, "iterations": 3000}]', sets=["iterations=900", "image=custom:1"])
    assert s.cases == ["design"] and [lv.label for lv in s.levels()] == ["1", "0.7"] and s.levels()[1].iterations == 3000
    assert s.settings["iterations"] == 900 and s.settings["image"] == "custom:1" and s.settings["cell_mm"] == 1.0
    with pytest.raises(KeyError, match="does not run case"):
        simulation(a, "cfd", "high")


def _dat(path, rows, header="# Time  value"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n" + "\n".join(" ".join(str(x) for x in r) for r in rows) + "\n")


def test_histories_are_averaged_over_the_last_fifth_of_the_iterations(tmp_path):
    it = np.arange(10, 1510, 10)
    _dat(tmp_path / "postProcessing" / "pIn_inlet" / "0" / "surfaceFieldValue.dat", [(t, -100.0 + 5 * np.sin(t / 30)) for t in it])
    _dat(tmp_path / "postProcessing" / "pOut_outlet" / "0" / "surfaceFieldValue.dat", [(t, 0.0) for t in it])
    _dat(tmp_path / "postProcessing" / "torque" / "0" / "moment.dat", [(t, "(0", 2.0 + 0.1 * np.cos(t / 30), "0)", 0, 0, 0, 0, 0, 0) for t in it])
    res = openfoam.parse_results(tmp_path, 1.2, 100.0)
    assert len(res["history"]["p_inlet"]) == 150 and res["patch_pressure_pa"]["inlet"] == pytest.approx(1.2 * tail(-100.0 + 5 * np.sin(it / 30))["mean"])
    info = {"patches": {"inlet": "inlet", "outlet": "outlet"}, "inlet_dynamic_pa": 1.0}
    geom = SimpleNamespace(joint_axis=lambda _: (np.zeros(3), np.array([0.0, 1.0, 0.0])), joint_of=lambda _: SimpleNamespace(name="spin"))
    rise = openfoam._history(SimpleNamespace(quantity="pressure_rise_total_to_static", location=None), res["history"], info, geom, "rotor", 100.0, [])
    assert tail(rise)["mean"] == pytest.approx(-res["patch_pressure_pa"]["inlet"] - 1.0)
    torque = openfoam._history(SimpleNamespace(quantity="torque", location=None), res["history"], info, geom, "rotor", 100.0, [])
    assert tail(torque)["mean"] == pytest.approx(-2.0, abs=0.02) and res["moment_nm"][1] == pytest.approx(-tail(torque)["mean"])
    _dat(tmp_path / "postProcessing" / "pIn_inlet" / "1500" / "surfaceFieldValue.dat", [(t, -90.0) for t in np.arange(1510, 3010, 10)])
    longer = openfoam.parse_results(tmp_path, 1.2, 100.0)["history"]["p_inlet"]  # a run continued from its latest time to a longer endTime
    assert len(longer) == 300 and longer[-1] == pytest.approx(-108.0) and longer[0] == pytest.approx(res["history"]["p_inlet"][0])


def test_regions_refine_inside_boxes_and_cylinders_and_leave_other_levels_unchanged(tmp_path):
    sim, geom = _duct(tmp_path, size=(100.0, 50.0, 50.0))
    plain = _case(tmp_path / "a", sim, geom)
    before = (tmp_path / "a" / "case" / "system" / "snappyHexMeshDict").read_text()
    assert "refinementRegions {  };" in before and "searchable" not in before
    sim.regions = [SimpleNamespace(name="core", shape="cylinder", point1=(10.0, 25.0, 25.0), point2=(90.0, 25.0, 25.0), radius=10.0),
                   SimpleNamespace(name="corner", shape="box", min=(0.0, 0.0, 0.0), max=(20.0, 10.0, 10.0))]
    _case(tmp_path / "c", sim, geom)
    assert (tmp_path / "c" / "case" / "system" / "snappyHexMeshDict").read_text() == before
    info = _case(tmp_path / "b", sim, geom, regions={"core": 1, "corner": 2})
    snappy = (tmp_path / "b" / "case" / "system" / "snappyHexMeshDict").read_text()
    assert "core { type searchableCylinder; point1 (0.01 0.025 0.025); point2 (0.09 0.025 0.025); radius 0.01; }" in snappy
    assert "corner { type searchableBox; min (0 0 0); max (0.02 0.01 0.01); }" in snappy
    assert "core { mode inside; levels ((1e15 2)); }" in snappy and "corner { mode inside; levels ((1e15 3)); }" in snappy  # walls are level 1 here
    assert info["refinement_regions"]["core"]["cell_mm"] == 0.25 and info["cells_estimate"] > plain["cells_estimate"] + math.pi * 100 * 80 / 0.25 ** 3 * 0.99

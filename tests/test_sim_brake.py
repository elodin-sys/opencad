"""CalculiX transient thermal (friction_brake source) and the brake_energy reduced model on a synthetic disc and pad."""

import math

import pytest
import yaml

from opencad.assembly import AsmCtx
from opencad.schemas import AssemblyContract
from opencad.sim import calculix

MAT = {"disc": (7870.0, 82.0, 449.0, 0.28), "pad": (2000.0, 8.7, 935.0, 0.8)}
INPUTS = {
    "vehicleMass": 1800.0, "initialSpeed": 25.0, "deceleration": 10.0, "brakeStart": 0.5, "brakeEnd": 1.5, "brakeCount": 8.0, "ambientTemperature": 300.0,
    "airConductivity": 0.026, "airDensity": 1.17, "airSpecificHeat": 1100.0, "airViscosity": 1.85e-5, "convectionLength": 0.14, "wheelRadius": 0.3,
    **{f"{b}.{k}": v for b, vals in MAT.items() for k, v in zip(("density", "conductivity", "specificHeat", "emissivity"), vals)},
}
CONTRACT = {
    "name": "t-brake", "intent": "synthetic disc brake", "datum_part": "pad",
    "frame": {"origin": "disc axis on the symmetry plane", "axes": {"x": "x", "y": "toward the pad", "z": "axis"}},
    "envelope": {"min": [-140.0, -140.0, 0.0], "max": [140.0, 140.0, 23.0], "tolerance": 0.05},
    "parts": [{"name": "pad", "kind": "modelled", "design": "t-brake-pad", "intent": "block pad on the disc face"},
              {"name": "disc", "kind": "modelled", "design": "t-brake-disc", "intent": "disc with a hub"}],
    "joints": [{"name": "spin", "kind": "revolute", "parent": "pad", "child": "disc", "parent_frame": {"origin": [0.0, 0.0, 0.0]}, "child_frame": {"origin": [0.0, 0.0, 0.0]},
                "drive": {"kind": "motor", "history": [[0.0, 796.0], [0.5, 796.0], [1.5, 477.0], [3.0, 477.0]]}}],
    "boundaries": [
        {"name": "discContact", "role": "contact", "body": "disc", "select": "plane", "point": [0.0, 0.0, 13.0], "normal": [0.0, 0.0, 1.0]},
        {"name": "discSymmetry", "role": "symmetry", "body": "disc", "select": "plane", "point": [0.0, 0.0, 0.0], "normal": [0.0, 0.0, -1.0]},
        {"name": "discFree", "role": "convection", "body": "disc", "select": "rest"},
        {"name": "padContact", "role": "contact", "body": "pad", "select": "plane", "point": [0.0, 0.0, 13.0], "normal": [0.0, 0.0, -1.0]},
        {"name": "padFree", "role": "convection", "body": "pad", "select": "rest"},
    ],
    "observables": [
        {"id": "peakFea", "quantity": "max_temperature", "unit": "K", "simulation": "fea", "body": "disc", "averaging": "maximum"},
        {"id": "storedFea", "quantity": "stored_heat", "unit": "J", "simulation": "fea", "averaging": "final"},
        {"id": "producedFea", "quantity": "produced_heat", "unit": "J", "simulation": "fea", "averaging": "integral"},
        {"id": "peakReduced", "quantity": "max_temperature", "unit": "K", "simulation": "budget", "averaging": "maximum"},
        {"id": "producedReduced", "quantity": "produced_heat", "unit": "J", "simulation": "budget", "averaging": "integral"},
    ],
    "simulations": [
        {"id": "fea", "physics": "thermal_transient", "solver": "calculix", "bodies": ["disc", "pad"], "outputs": ["peakFea", "storedFea", "producedFea"],
         "settings": {"source": "friction_brake", "end_time": 2.0, "time_step": 0.05, "mesh_size_mm": 14.0, "contact_mesh_size_mm": 6.0}, "refinement": [1.0]},
        {"id": "budget", "physics": "reduced", "solver": "reduced:brake_energy", "bodies": ["disc", "pad"], "outputs": ["peakReduced", "producedReduced"],
         "settings": {"end_time": 2.0}},
    ],
}
for s in CONTRACT["simulations"]:
    s["inputs"] = {k: {"value": v, "unit": "SI", "provenance": "defaulted", "rationale": "test value"} for k, v in INPUTS.items()}

SOURCE = '''from build123d import import_step

disc = import_step("inputs/t-brake-disc.step")
pad = import_step("inputs/t-brake-pad.step")
identity = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
result = [pad, disc]
placements = {"pad": identity, "disc": identity}
'''


@pytest.fixture(scope="module")
def brake(tmp_path_factory):
    from build123d import Align, Box, Cylinder, Pos, export_step

    from opencad.assembly import domains, verify
    from opencad.backends.registry import set_backend

    set_backend("build123d")
    root = tmp_path_factory.mktemp("brake")
    part_dir = root / "parts" / "t-brake"
    (part_dir / "inputs").mkdir(parents=True)
    zmin = (Align.CENTER, Align.CENTER, Align.MIN)
    export_step(Cylinder(140, 13, align=zmin) + Pos(0, 0, 13) * Cylinder(80, 10, align=zmin), str(part_dir / "inputs" / "t-brake-disc.step"))
    export_step(Pos(0, 107.5, 13) * Box(80, 45, 6.5, align=zmin), str(part_dir / "inputs" / "t-brake-pad.step"))
    (part_dir / "main.py").write_text(SOURCE, encoding="utf-8")
    design = root / "designs" / "t-brake"
    design.mkdir(parents=True)
    (design / "assembly.yaml").write_text(yaml.safe_dump(CONTRACT), encoding="utf-8")
    actx = AsmCtx("t-brake", design, AssemblyContract.model_validate(CONTRACT), root / "results" / "t-brake", part_dir, "build123d")
    actx.results_dir.mkdir(parents=True)
    actx.write_stage("verify", verify.run(actx))
    actx.write_stage("domains", domains.run(actx))
    return actx


@pytest.mark.skipif(not calculix.available(), reason="ccx not installed")
def test_friction_brake_fea_closes_the_energy_budget_and_agrees_with_the_budget_model(brake):
    from opencad.assembly import simulate

    dom = brake.load_stage("domains")
    assert dom["boundaries"]["disc"]["ok"] and dom["boundaries"]["pad"]["ok"], dom["boundaries"]
    sim = simulate.run(brake)
    fea, budget = sim["simulations"]["fea"], sim["simulations"]["budget"]
    assert fea["status"] == "ok", fea.get("error")
    assert budget["status"] == "ok", budget.get("error")
    produced = 1800 * (25 ** 2 - 15 ** 2) / 2 / 8
    assert sim["observables"]["producedFea"]["value"] == pytest.approx(produced, rel=0.02)
    assert sim["observables"]["producedReduced"]["value"] == pytest.approx(produced, rel=0.02)
    assert abs(fea["conservation"]["energy_balance"]["value"]) < 0.05, fea["conservation"]
    peak_fea, peak_red = sim["observables"]["peakFea"]["value"], sim["observables"]["peakReduced"]["value"]
    assert 305 < peak_fea < 600 and 305 < peak_red < 600 and abs(peak_fea - peak_red) < 0.25 * (peak_red - 300), (peak_fea, peak_red)
    assert fea["peak_flash_K"] > 0 and max(fea["series"]["max_T_disc_mean_field_K"]) < peak_fea
    xi = fea["heat_fraction_disc"]
    e = {b: math.sqrt(k * rho * cp) for b, (rho, k, cp, _) in MAT.items()}
    assert xi == pytest.approx(e["disc"] / (e["disc"] + e["pad"]))

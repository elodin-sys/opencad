"""Run A of the disc-brake case: the reference geometry (COMSOL's construction, scripts/derive_brake_truth.py) through this
pipeline's own analyses (CalculiX friction_brake, reduced brake_energy), evaluator side. It measures the model-form difference
between these analyses and the COMSOL result before any reconstructed geometry is scored against it.

    .venv/bin/python scripts/brake_run_a.py [--out results/_spikes/disc-brake-run-a] [--refinement 1.0,0.7]
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / "truth" / "cases" / "disc-brake" / "truth"
INPUTS = {  # the packet's stated values; T_air and r_wheel are this run's assumptions (not stated by COMSOL)
    "vehicleMass": 1800.0, "initialSpeed": 25.0, "deceleration": 10.0, "brakeStart": 2.0, "brakeEnd": 4.0, "endTime": 12.0, "brakeCount": 8.0,
    "ambientTemperature": 300.0, "airConductivity": 0.026, "airDensity": 1.17, "airSpecificHeat": 1100.0, "airViscosity": 1.85e-5, "convectionLength": 0.14,
    "wheelRadius": 0.3, "disc.density": 7870.0, "disc.specificHeat": 449.0, "disc.conductivity": 82.0, "disc.emissivity": 0.28,
    "pad.density": 2000.0, "pad.specificHeat": 935.0, "pad.conductivity": 8.7, "pad.emissivity": 0.8,
}
LINE = [[0.0, 0.0, 12.9], [-47.0, 131.6, 12.9]]
OBS = [
    ("peakDiscTemperature", "max_temperature", "K", {"body": "disc", "averaging": "maximum"}),
    ("lineMaxTemperature", "line_max_temperature", "K", {"body": "disc", "line": LINE, "averaging": "maximum"}),
    ("timeOfPeak", "time_of_max_temperature", "s", {"body": "disc"}),
    ("producedHeat", "produced_heat", "J", {}),
    ("dissipatedHeat", "dissipated_heat", "J", {}),
    ("hotspotRadius", "hotspot_radius", "mm", {"body": "disc"}),
]


def contract(refinement: list[float]) -> dict:
    inputs = {k: {"value": v, "unit": "SI", "provenance": "stated" if k not in ("ambientTemperature", "wheelRadius", "airViscosity") else "inferred",
                  "source": "COMSOL brake_disc packet", "rationale": "not stated by COMSOL; Run A assumption"} for k, v in INPUTS.items()}
    obs, sims = [], []
    for tag, solver, physics, settings in (("Fea", "calculix", "thermal_transient", {"source": "friction_brake", "end_time": 12.0, "time_step": 0.05,
                                                                                    "mesh_size_mm": 10.0, "contact_mesh_size_mm": 4.0}),
                                           ("Budget", "reduced:brake_energy", "reduced", {"end_time": 12.0})):
        ids = []
        for oid, q, unit, extra in OBS:
            obs.append({"id": oid + tag, "quantity": q, "unit": unit, "simulation": tag.lower(), "case": "panicBrake", **extra})
            ids.append(oid + tag)
        sims.append({"id": tag.lower(), "physics": physics, "solver": solver, "cases": ["panicBrake"], "bodies": ["disc", "pad"], "inputs": inputs, "settings": settings,
                     "outputs": ids, "refinement": refinement if solver == "calculix" else [1.0]})
    return {
        "name": "disc-brake-run-a", "intent": "COMSOL reference geometry through the pipeline analyses", "datum_part": "pad",
        "frame": {"origin": "COMSOL origin (disc axis on the symmetry plane), mm", "axes": {"x": "x", "y": "y", "z": "disc axis"}},
        "envelope": {"min": [-140.0, -140.0, 0.0], "max": [140.0, 140.0, 23.0], "tolerance": 0.1},
        "parts": [{"name": "pad", "kind": "purchased", "catalog": {"name": "pad", "kind": "step", "path": "pad.step"}},
                  {"name": "disc", "kind": "purchased", "catalog": {"name": "disc", "kind": "step", "path": "disc.step"}}],
        "joints": [{"name": "discSpin", "kind": "revolute", "parent": "pad", "child": "disc", "parent_frame": {"origin": [0.0, 0.0, 0.0]}, "child_frame": {"origin": [0.0, 0.0, 0.0]},
                    "drive": {"kind": "motor", "history": [[0.0, 795.8], [2.0, 795.8], [4.0, 159.2], [12.0, 159.2]]}}],
        "boundaries": [
            {"name": "discContact", "role": "contact", "body": "disc", "select": "plane", "point": [0.0, 0.0, 13.0], "normal": [0.0, 0.0, 1.0]},
            {"name": "discSymmetry", "role": "symmetry", "body": "disc", "select": "plane", "point": [0.0, 0.0, 0.0], "normal": [0.0, 0.0, -1.0]},
            {"name": "discFree", "role": "convection", "body": "disc", "select": "rest"},
            {"name": "padContact", "role": "contact", "body": "pad", "select": "plane", "point": [0.0, 0.0, 13.0], "normal": [0.0, 0.0, -1.0]},
            {"name": "padFree", "role": "convection", "body": "pad", "select": "rest"},
        ],
        "operating_cases": [{"id": "panicBrake", "values": {"initialSpeed": 25.0}}], "observables": obs, "simulations": sims,
    }


SOURCE = '''from build123d import import_step

identity = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
result = [import_step("inputs/pad.step"), import_step("inputs/disc.step")]
placements = {"pad": identity, "disc": identity}
'''


def main(argv: list[str] | None = None) -> int:
    from opencad.assembly import AsmCtx, domains, simulate, verify
    from opencad.assembly.assemble import stage_inputs
    from opencad.backends.registry import set_backend
    from opencad.schemas import AssemblyContract

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "results" / "_spikes" / "disc-brake-run-a"))
    ap.add_argument("--refinement", default="1.0,0.7")
    a = ap.parse_args(argv)
    set_backend("build123d")
    out = Path(a.out)
    shutil.rmtree(out, ignore_errors=True)
    design = out / "design"
    design.mkdir(parents=True)
    for f in ("disc.step", "pad.step"):
        shutil.copy2(TRUTH / f, design / f)
    c = contract([float(x) for x in a.refinement.split(",")])
    (design / "assembly.yaml").write_text(yaml.safe_dump(c, sort_keys=False), encoding="utf-8")
    actx = AsmCtx("disc-brake-run-a", design, AssemblyContract.model_validate(c), out / "results", out / "parts", "build123d")
    actx.results_dir.mkdir(parents=True)
    stage_inputs(actx)
    actx.entry.write_text(SOURCE, encoding="utf-8")
    for stage, fn in (("verify", verify.run), ("domains", domains.run), ("simulate", simulate.run)):
        data = fn(actx)
        actx.write_stage(stage, data)
        print(f"{stage}: {'ok' if data.get('ok') else 'FAILED'}", flush=True)
    sim = actx.load_stage("simulate")
    print(json.dumps({k: {"value": v.get("value"), "u_numerical": v.get("u_numerical"), "levels": v.get("levels")} for k, v in sim["observables"].items()}, indent=1))
    for k, s in sim["simulations"].items():
        print(k, s["status"], json.dumps(s.get("conservation"), default=str)[:300], s.get("error", "")[:300])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""OpenFOAM adapter: case writing on a box duct (no container), and on a synthetic mixer with an inlet and an outlet, snappyHexMesh
from the labelled fluid STL, MRF rotor zone, patch pressures, mass balance and rotor torque (needs a running container runtime with
the OpenFOAM image; about 3 minutes)."""

import copy
import math
from types import SimpleNamespace

import numpy as np
import pytest
import yaml

from opencad.assembly import AsmCtx
from opencad.schemas import AssemblyContract
from opencad.sim import openfoam, runtime

from test_assembly_pipeline import CONTRACT as MIXER

RT = runtime.detect()
CONTAINER = pytest.mark.skipif(RT is None or not runtime.has_image(openfoam.IMAGE, RT), reason="no container runtime or OpenFOAM image")


def _box_stl(path, size, inward: bool = False) -> None:
    """ASCII STL of the box [0, size] (mm) with regions inlet (x = 0), outlet (x = max) and walls, triangles facing outward."""
    lx, ly, lz = size
    quads = {"inlet": [((0, 0, 0), (0, 0, lz), (0, ly, lz), (0, ly, 0))], "outlet": [((lx, 0, 0), (lx, ly, 0), (lx, ly, lz), (lx, 0, lz))],
             "walls": [((0, 0, 0), (lx, 0, 0), (lx, 0, lz), (0, 0, lz)), ((0, ly, 0), (0, ly, lz), (lx, ly, lz), (lx, ly, 0)),
                       ((0, 0, 0), (0, ly, 0), (lx, ly, 0), (lx, 0, 0)), ((0, 0, lz), (lx, 0, lz), (lx, ly, lz), (0, ly, lz))]}
    lines = []
    for region, qs in quads.items():
        lines.append(f"solid {region}")
        for a, b, c, d in qs:
            for tri in ((a, b, c), (a, c, d)):
                tri = tri[::-1] if inward else tri
                lines += ["  facet normal 0 0 0", "    outer loop", *(f"      vertex {x} {y} {z}" for x, y, z in tri), "    endloop", "  endfacet"]
        lines.append(f"endsolid {region}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _duct(tmp_path, size=(1000.0, 100.0, 100.0), inward=False, **settings):
    _box_stl(tmp_path / "boundaries" / "air.stl", size, inward)
    contract = SimpleNamespace(boundaries=[SimpleNamespace(name=n, role=r, body="air") for n, r in (("inlet", "inlet"), ("outlet", "outlet"), ("walls", "wall"))],
                               fluid_volumes=[SimpleNamespace(name="air", body="air", seed=[s / 2 for s in size])])
    geom = SimpleNamespace(contract=contract, actx=SimpleNamespace(results_dir=tmp_path),
                           fluid=lambda _: {"bbox_min": [0.0, 0.0, 0.0], "bbox_max": list(size), "volume": float(np.prod(size))})
    sim = SimpleNamespace(id="cfd", inputs={"fluidDensity": SimpleNamespace(value=1.2), "fluidViscosity": SimpleNamespace(value=1.8e-5)},
                          settings={"inlet_diameter_mm": 100.0, **settings})
    return sim, geom


def _case(tmp_path, sim, geom, cell_mm=1.0, **kw):
    return openfoam.write_case(tmp_path / "case", sim=sim, geom=geom, fluid="air", rotor=None, cell_mm=cell_mm, flow_m3s=0.01, omega=0.0, probes=[],
                               iterations=10, procs=1, **kw)


def test_background_is_coarsened_under_its_cap_and_the_fluid_refined_back(tmp_path):
    sim, geom = _duct(tmp_path)
    info = _case(tmp_path, sim, geom)
    snappy = (tmp_path / "case" / "system" / "snappyHexMeshDict").read_text()
    assert info["inside_level"] == 1 and info["cell_background_mm"] == 2.0 and np.prod(info["cells_background"]) <= openfoam.BACKGROUND_CELLS_MAX
    assert "fluid { mode inside; levels ((1e15 1)); }" in snappy and "walls { level (2 2);" in snappy and "addLayers false" in snappy
    assert info["wall_cell_mm"] == 0.5 and info["cells_estimate"] > 1e7  # the fluid at 1 mm is 1e7 cells whatever the box
    sim, geom = _duct(tmp_path / "b", background_cells_max=1e9)
    info = _case(tmp_path / "b", sim, geom)
    assert info["inside_level"] == 0 and info["cell_background_mm"] == 1.0 and "mode inside" not in (tmp_path / "b" / "case" / "system" / "snappyHexMeshDict").read_text()


def test_prism_layers_and_the_inlet_turbulence_are_written(tmp_path):
    sim, geom = _duct(tmp_path, size=(100.0, 50.0, 50.0), layers=3, final_layer_thickness=0.4)
    info = _case(tmp_path, sim, geom, turbulence_pct=7.0)
    snappy = (tmp_path / "case" / "system" / "snappyHexMeshDict").read_text()
    assert "addLayers true" in snappy and "walls { nSurfaceLayers 3; }" in snappy and "inlet { nSurfaceLayers" not in snappy and "finalLayerThickness 0.4" in snappy
    k = float((tmp_path / "case" / "0" / "k").read_text().split("internalField uniform ")[1].split(";")[0])
    assert info["inlet_turbulence_pct"] == 7.0 and k == pytest.approx(1.5 * (0.07 * info["u_inlet"]) ** 2)
    case = SimpleNamespace(values={"inletTurbulencePct": 4.0})
    assert openfoam.inlet_turbulence(sim, case) == 4.0 and openfoam.inlet_turbulence(sim, SimpleNamespace(values={})) == 5.0
    sim.settings["turbulence_key"] = "tu"
    assert openfoam.inlet_turbulence(sim, case) == 5.0


def test_an_inside_out_fluid_surface_is_refused(tmp_path):
    sim, geom = _duct(tmp_path, size=(100.0, 50.0, 50.0), inward=True)
    with pytest.raises(ValueError, match="face inward"):
        _case(tmp_path, sim, geom)


def test_a_run_killed_for_memory_is_retried_once_at_twice_the_memory(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(openfoam.runtime, "run", lambda image, argv, **kw: calls.append(kw["memory"]) or {"code": 137 if len(calls) == 1 else 0})
    r = openfoam.container_run("img", tmp_path, rt="docker", procs=8, need_gb=8.5, mem_cap=40.0, settings={})
    assert calls == ["17G", "34G"] and r == {"code": 0, "memory": "34G"}
    calls.clear()
    assert openfoam.container_run("img", tmp_path, rt="docker", procs=8, need_gb=30.0, mem_cap=40.0, settings={})["code"] == 137
    assert calls == ["40G"]
    calls.clear()
    openfoam.container_run("img", tmp_path, rt="docker", procs=8, need_gb=8.5, mem_cap=40.0, settings={"memory": "16G"})
    assert calls == ["16G"]


def test_a_changed_case_starts_clean(tmp_path):
    """A later time directory would make snappyHexMesh (startFrom latestTime) write its mesh there, leaving constant/polyMesh the box."""
    for d in ("0", "1500/polyMesh", "processor0/1500", "postProcessing/pIn_inlet/0", "constant/polyMesh", "constant/triSurface", "system"):
        (tmp_path / d).mkdir(parents=True)
    (tmp_path / "result.json").write_text("{}")
    openfoam.fresh(tmp_path)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["0", "constant", "system"] and [p.name for p in (tmp_path / "constant").iterdir()] == ["triSurface"]


def test_a_run_whose_driver_died_is_recovered_only_with_its_own_inputs(tmp_path):
    (tmp_path / "started.json").write_text('{"hash": "k"}')
    (tmp_path / "log.simpleFoam").write_text("Time = 3000\n\nEnd\n\nFinalising parallel run\n")
    (tmp_path / "log.reconstructPar").write_text("Reconstructing\n\nEnd\n")
    assert not openfoam.recovered(tmp_path, "k", 3000, 8)  # no 3000 time directory: the solver stopped short
    (tmp_path / "3000").mkdir()
    assert openfoam.recovered(tmp_path, "k", 3000, 8) and not openfoam.recovered(tmp_path, "other", 3000, 8)
    (tmp_path / "log.reconstructPar").write_text("Reconstructing\n")
    assert not openfoam.recovered(tmp_path, "k", 3000, 8) and openfoam.recovered(tmp_path, "k", 3000, 1)


def test_a_finished_case_is_adopted_from_the_previous_attempt_only_when_its_inputs_match(tmp_path):
    case, old = tmp_path / "sim" / "cfd" / "run-level-1", tmp_path / "sim.prev" / "cfd" / "run-level-1"
    for d in (case, old):
        (d / "system").mkdir(parents=True)
    (old / "result.json").write_text('{"hash": "abc"}')
    (old / "log.simpleFoam").write_text("End")
    openfoam.adopt(case, old, "xyz")
    assert not (case / "log.simpleFoam").exists() and old.exists()
    openfoam.adopt(case, old, "abc")
    assert (case / "log.simpleFoam").read_text() == "End" and not old.exists()

@CONTAINER
def test_snappy_refines_only_inside_a_tip_annulus(tmp_path, monkeypatch):
    sim, geom = _duct(tmp_path, size=(100.0, 50.0, 50.0))
    sim.regions = [SimpleNamespace(name="tip", shape="rotor_tip", body=None, inside_mm=2.0, outside_mm=2.0, axial_margin_mm=0.0)]
    monkeypatch.setattr(openfoam, "tip_band", lambda *a: (np.array([0.0, 25.0, 25.0]), np.array([1.0, 0.0, 0.0]), 15.0, 20.0, 80.0))
    cells = {}
    for name, regions in (("plain", None), ("tip", {"tip": 1})):
        case = tmp_path / name
        openfoam.write_case(case / "case", sim=sim, geom=geom, fluid="air", rotor=None, cell_mm=5.0, flow_m3s=0.01, omega=0.0, probes=[], iterations=10,
                            procs=1, regions=regions)
        (case / "case" / "Allrun").write_text(f"source {openfoam.BASHRC}\nset -e\ncd /case\nblockMesh > log.blockMesh 2>&1\n"
                                              "snappyHexMesh -overwrite > log.snappyHexMesh 2>&1\ncheckMesh > log.checkMesh 2>&1 || true\n")
        r = runtime.run(openfoam.IMAGE, ["bash", "/case/Allrun"], mounts={case / "case": "/case"}, workdir="/case", rt=RT, cpus=2, memory="4G", timeout=600)
        assert r["code"] == 0, (case / "case" / "log.snappyHexMesh").read_text()[-2000:]
        cells[name] = openfoam.parse_results(case / "case", 1.2, 0.0)["cells"]
    annulus = math.pi * (17.0 ** 2 - 13.0 ** 2) * 60.0 / 1.25 ** 3  # cells of 1.25 mm filling the annulus
    assert cells["plain"] + 0.5 * annulus < cells["tip"] < cells["plain"] + 3 * annulus, cells


CONTRACT = copy.deepcopy(MIXER)
CONTRACT["fluid_volumes"][0]["caps"].append({"name": "outletCap", "point": [30.0, 0.0, 15.0], "normal": [1.0, 0.0, 0.0]})
CONTRACT["fluid_volumes"][0]["volume"] = None
CONTRACT["boundaries"].insert(1, {"name": "outlet", "role": "outlet", "body": "fluid", "select": "plane", "point": [30.0, 0.0, 15.0], "normal": [1.0, 0.0, 0.0]})
CONTRACT["observables"] = [{"id": "rise", "quantity": "pressure_rise", "unit": "Pa", "simulation": "cfd", "case": "run"},
                           {"id": "torque", "quantity": "torque", "unit": "N m", "simulation": "cfd", "case": "run"}]
CONTRACT["operating_cases"] = [{"id": "run", "values": {"flowLMin": 2.0, "speedRpm": 3000.0}}]
CONTRACT["simulations"] = [{"id": "cfd", "physics": "cfd_steady", "solver": "openfoam", "cases": ["run"], "bodies": ["fluid", "rotor"], "outputs": ["rise", "torque"],
                            "inputs": {"fluidDensity": {"value": 1000.0, "unit": "kg/m3", "provenance": "defaulted", "rationale": "test"},
                                       "fluidViscosity": {"value": 1e-3, "unit": "Pa s", "provenance": "defaulted", "rationale": "test"}},
                            "settings": {"flow_key": "flowLMin", "speed_key": "speedRpm", "cell_mm": 2.5, "iterations": 150, "processes": 4, "memory": "8G"},
                            "refinement": [1.0]}]
SOURCE = '''from build123d import Align, Axis, Box, Cylinder, Location, Pos, import_step

housing = import_step("inputs/t-mixer-housing.step")
rotor = import_step("inputs/t-mixer-rotor.step").moved(Location((0, 0, 15)))
region = Box(60, 40, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)) - housing - rotor
fluid = next(s for s in region.solids() if s.is_inside((0, 10, 15)))
result = [housing, rotor, fluid]
placements = {
    "housing": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
    "rotor": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 15], [0, 0, 0, 1]],
    "fluid": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
}
'''


@CONTAINER
def test_mrf_case_runs_and_balances_mass(tmp_path):
    from build123d import Align, Axis, Box, Cylinder, Pos, export_step

    from opencad.assembly import domains, simulate, verify
    from opencad.backends.registry import set_backend

    set_backend("build123d")
    part_dir = tmp_path / "parts" / "t-mixer"
    (part_dir / "inputs").mkdir(parents=True)
    housing = Box(60, 40, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Pos(0, 0, 4) * Box(52, 32, 22, align=(Align.CENTER, Align.CENTER, Align.MIN))
    housing -= Pos(0, 0, 26) * Cylinder(5, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    housing -= Pos(28, 0, 15) * Cylinder(4, 4, rotation=(0, 90, 0))
    export_step(housing, str(part_dir / "inputs" / "t-mixer-housing.step"))
    export_step(Box(20, 4, 10), str(part_dir / "inputs" / "t-mixer-rotor.step"))
    (part_dir / "main.py").write_text(SOURCE, encoding="utf-8")
    design = tmp_path / "designs" / "t-mixer"
    design.mkdir(parents=True)
    (design / "assembly.yaml").write_text(yaml.safe_dump(CONTRACT), encoding="utf-8")
    actx = AsmCtx("t-mixer", design, AssemblyContract.model_validate(CONTRACT), tmp_path / "results" / "t-mixer", part_dir, "build123d")
    actx.results_dir.mkdir(parents=True)
    actx.write_stage("verify", verify.run(actx))
    dom = domains.run(actx)
    actx.write_stage("domains", dom)
    assert dom["fluids"]["fluid"]["sealed"] and dom["boundaries"]["fluid"]["ok"], dom
    sim = simulate.run(actx)
    cfd = sim["simulations"]["cfd"]
    assert cfd["status"] == "ok", cfd.get("error")
    run = cfd["runs"][0]
    assert run["mesh_ok"] and run["cells"] > 1000, run
    assert cfd["conservation"]["mass_balance"]["value"] < 0.02, cfd["conservation"]
    rise, torque = sim["observables"]["rise"]["value"], sim["observables"]["torque"]["value"]
    assert math.isfinite(rise) and math.isfinite(torque) and torque > 0, (rise, torque)  # driving torque: the flow takes power from the rotor
    _ = Axis

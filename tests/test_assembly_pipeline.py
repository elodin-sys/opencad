"""Evaluator stages of the assembly pipeline on a synthetic machine: a hollow housing with an inlet, a rotor on a motor-driven
revolute joint, and the fluid between them built by the assembly source."""

import json
import math
from pathlib import Path

import numpy as np
import pytest
import yaml

from opencad.assembly import AsmCtx
from opencad.assembly import joints as jm
from opencad.schemas import AssemblyContract

CONTRACT = {
    "name": "t-mixer",
    "intent": "synthetic mixer: housing, rotor, fluid",
    "frame": {"origin": "housing base centre", "axes": {"x": "length", "y": "width", "z": "up"}},
    "envelope": {"min": [-30.0, -20.0, 0.0], "max": [30.0, 20.0, 30.0], "tolerance": 0.05},
    "datum_part": "housing",
    "parts": [
        {"name": "housing", "kind": "modelled", "design": "t-mixer-housing", "intent": "hollow box with an inlet"},
        {"name": "rotor", "kind": "modelled", "design": "t-mixer-rotor", "intent": "a bar centred on its own origin"},
        {"name": "fluid", "kind": "derived", "role": "fluid"},
    ],
    "joints": [
        {"name": "spin", "kind": "revolute", "parent": "housing", "child": "rotor", "parent_frame": {"origin": [0.0, 0.0, 15.0]},
         "child_frame": {"origin": [0.0, 0.0, 0.0]}, "drive": {"kind": "motor", "speed": 60.0}},
        {"name": "fluidFixed", "kind": "rigid", "parent": "housing", "child": "fluid", "parent_frame": {"origin": [0.0, 0.0, 0.0], "ref": [1.0, 0.0, 0.0]},
         "child_frame": {"origin": [0.0, 0.0, 0.0], "ref": [1.0, 0.0, 0.0]}},
    ],
    "fluid_volumes": [{"name": "fluid", "body": "fluid", "walls": ["housing"], "minus": ["rotor"], "caps": [{"name": "inlet", "point": [0.0, 0.0, 30.0], "normal": [0.0, 0.0, 1.0]}],
                       "seed": [0.0, 10.0, 15.0], "volume": {"expected": 52 * 32 * 22 + math.pi * 25 * 4 - 20 * 4 * 10, "tolerance_rel": 0.001}}],
    "boundaries": [
        {"name": "inlet", "role": "inlet", "body": "fluid", "select": "plane", "point": [0.0, 0.0, 30.0], "normal": [0.0, 0.0, 1.0]},
        {"name": "rotorWall", "role": "rotating_wall", "body": "fluid", "select": "touching", "touching": "rotor"},
        {"name": "walls", "role": "wall", "body": "fluid", "select": "rest"},
    ],
    "observables": [{"id": "fluidVolume", "quantity": "fluid_volume", "unit": "mm3", "min": 30000.0}],
    "acceptance": {"clearances": [{"name": "rotorFree", "a": "rotor", "b": "housing", "min_gap": 2.0}],
                   "motions": [{"name": "turn", "drive": "spin", "range": [0.0, 360.0], "steps": 8}]},
}

SOURCE = '''from build123d import Align, Box, Location, import_step

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
joints = {"spin": {"origin": [0, 0, 15], "axis": [0, 0, 1]}}
'''


def _parts(inputs: Path) -> None:
    from build123d import Align, Box, Cylinder, Pos, export_step

    housing = Box(60, 40, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Pos(0, 0, 4) * Box(52, 32, 22, align=(Align.CENTER, Align.CENTER, Align.MIN))
    housing -= Pos(0, 0, 26) * Cylinder(5, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    export_step(housing, str(inputs / "t-mixer-housing.step"))
    export_step(Box(20, 4, 10), str(inputs / "t-mixer-rotor.step"))


@pytest.fixture(scope="module")
def machine(tmp_path_factory):
    from opencad.backends.registry import set_backend

    set_backend("build123d")
    root = tmp_path_factory.mktemp("asm")
    design = root / "designs" / "t-mixer"
    design.mkdir(parents=True)
    (design / "assembly.yaml").write_text(yaml.safe_dump(CONTRACT), encoding="utf-8")
    part_dir = root / "parts" / "t-mixer"
    (part_dir / "inputs").mkdir(parents=True)
    _parts(part_dir / "inputs")
    (part_dir / "main.py").write_text(SOURCE, encoding="utf-8")
    actx = AsmCtx("t-mixer", design, AssemblyContract.model_validate(CONTRACT), root / "results" / "t-mixer", part_dir, "build123d")
    actx.results_dir.mkdir(parents=True)
    return actx


def test_verify_kinematics_domains_gates_viz(machine):
    from opencad.assembly import domains, gates, kinematics, simulate, verify, viz

    ver = verify.run(machine)
    machine.write_stage("verify", ver)
    assert ver["program_executes"] and ver["solid_count"]["ok"], verify.lines(ver)
    assert ver["agreement"]["ok"], ver["agreement"]
    assert ver["joints"]["joints"]["spin"]["ok"] and ver["joints"]["joints"]["fluidFixed"]["ok"]
    assert ver["clearances"]["rotorFree"]["ok"] and ver["envelope"]["ok"]
    assert ver["declared_joints"]["spin"]["declared"]["origin"] == [0.0, 0.0, 15.0]
    kin = kinematics.run(machine)
    machine.write_stage("kinematics", kin)
    turn = kin["motions"]["turn"]
    assert turn["ok"] and turn["pairs"] == [["housing", "rotor"]] and len(turn["poses"]) == 9
    dom = domains.run(machine)
    machine.write_stage("domains", dom)
    fl = dom["fluids"]["fluid"]
    assert fl["sealed"] and fl["volume_check"]["ok"] and fl["agreement"]["hausdorff_mm"] < 0.01, fl
    labels = dom["boundaries"]["fluid"]["labels"]
    assert len(labels["inlet"]["faces"]) == 1 and abs(labels["inlet"]["area"] - math.pi * 25) < 0.5
    assert len(labels["rotorWall"]["faces"]) == 6 and dom["boundaries"]["fluid"]["unassigned"] == []
    assert (machine.results_dir / "boundaries" / "fluid.stl").read_text().count("solid inlet") == 2
    sim = simulate.run(machine)
    machine.write_stage("simulate", sim)
    assert sim["observables"]["fluidVolume"]["requirement"]["ok"]
    fb = gates.evaluate(machine)
    by = {g["id"]: g["ok"] for g in fb["gates"]}
    assert by["joint_fidelity"] and by["motion_clear"] and by["fluid_domain"] and by["boundaries_complete"] and by["export_agreement"] and by["performance"]
    assert by["parts_pass"] is None and not fb["ok"]
    out = viz.generate(machine, machine.results_dir / "handoff", fb=fb, sim=sim)
    assert {"drive:turn", "operate", "explode"} <= set(out["clips"])
    from pygltflib import GLTF2

    assert [a.name for a in GLTF2().load(out["glb"]).animations] == ["operate"]
    assert {a.name for a in GLTF2().load(out["glb_clips"]).animations} == {"drive:turn", "operate", "explode"}
    html = Path(out["html"]).read_text()
    assert "animation-name=\"operate\"" in html and 'src="assembly-clips.glb"' in html


def test_verify_flags_a_body_off_its_joint(machine, tmp_path):
    from opencad.assembly import verify

    src = machine.entry.read_text()
    machine.entry.write_text(src.replace("Location((0, 0, 15))", "Location((0.4, 0, 15))").replace("[0, 1, 0, 0], [0, 0, 1, 15]", "[0, 1, 0, 0], [0, 0, 1, 15.0]"))
    try:
        res = verify.evaluate(machine, tmp_path / "exp")
    finally:
        machine.entry.write_text(src)
    assert not res["agreement"]["bodies"]["rotor"]["ok"]
    assert any(line.startswith("FAIL agreement rotor") for line in verify.lines(res))


def test_a_restart_keeps_the_previous_simulations_aside_for_reuse(tmp_path):
    from opencad.assembly.pipeline import _clean

    (tmp_path / "sim" / "cfd").mkdir(parents=True)
    (tmp_path / "sim.prev" / "stale").mkdir(parents=True)
    (tmp_path / "simulate.json").write_text("{}")
    _clean(tmp_path, ["simulate", "gates"])
    assert not (tmp_path / "simulate.json").exists() and not (tmp_path / "sim").exists()
    assert (tmp_path / "sim.prev" / "cfd").is_dir() and not (tmp_path / "sim.prev" / "stale").exists()


def test_verify_rejects_a_scaled_placement(machine, tmp_path):
    from opencad.assembly import verify

    src = machine.entry.read_text()
    machine.entry.write_text(
        src.replace(
            '"rotor": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 15], [0, 0, 0, 1]]',
            '"rotor": [[1.001, 0, 0, 0], [0, 1.001, 0, 0], [0, 0, 1.001, 15], [0, 0, 0, 1]]',
        )
    )
    try:
        res = verify.evaluate(machine, tmp_path / "exp")
    finally:
        machine.entry.write_text(src)
    assert not res["placements"]["ok"] and set(res["placements"]["non_rigid"]) == {"rotor"}
    assert verify.rigidity_error(np.eye(4)) == 0.0


def test_joint_math_offsets_flips_and_chains():
    a = AssemblyContract.model_validate(json.loads(json.dumps(CONTRACT)))
    j = a.joint("spin")
    mp, mc = np.eye(4), np.eye(4)
    mc[2, 3] = 15.0
    assert jm.fidelity(j, mp, mc)["ok"]
    mc[0, 3] = 0.2
    bad = jm.fidelity(j, mp, mc)
    assert not bad["ok"] and bad["checks"]["radial_mm"]["measured"] == pytest.approx(0.2)
    placements = {"housing": np.eye(4), "rotor": np.eye(4), "fluid": np.eye(4)}
    placements["rotor"][2, 3] = 15.0
    ps = jm.poses(a, placements, {"spin": 90.0})
    assert np.allclose(ps["rotor"][:3, :3] @ [1, 0, 0], [0, 1, 0]) and np.allclose(ps["rotor"][:3, 3], [0, 0, 15])
    assert jm.moving_pairs(a, placements, [{"spin": 0.0}, {"spin": 30.0}]) == [("housing", "rotor")]


def test_derived_fluid_caps_close_ports_locally():
    """A U-shaped duct: the inlet riser ends at z = 80, the outlet riser at z = 120, so a half-space at the inlet cap would cut the outlet riser."""
    from types import SimpleNamespace

    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse

    from opencad.assembly.domains import derive_fluid
    from opencad.geomcheck import brep
    from opencad.geomcheck.assembly import make_box

    def fuse(x, y):
        op = BRepAlgoAPI_Fuse(x, y)
        op.Build()
        return op.Shape()

    cavity = fuse(fuse(make_box([0, 0, 0], [100, 10, 10]), make_box([0, 0, 0], [10, 10, 80])), make_box([90, 0, 0], [100, 10, 120]))
    block = fuse(make_box([-3, -3, -3], [103, 13, 80]), make_box([87, -3, 80], [103, 13, 120]))
    wall = BRepAlgoAPI_Cut(block, cavity)
    wall.Build()
    caps = [SimpleNamespace(name="in", point=[5.0, 5.0, 80.0], normal=[0.0, 0.0, 1.0]), SimpleNamespace(name="out", point=[95.0, 5.0, 120.0], normal=[0.0, 0.0, 1.0])]
    r = derive_fluid([wall.Shape()], [], caps, [50.0, 5.0, 5.0], cavity)
    expected = brep.volume_props(cavity)["volume"]
    assert r["sealed"] and abs(r["volume"] - expected) < 1e-3 * expected, (r.get("volume"), expected)


def test_derived_fluid_box_reaches_caps_beyond_the_walls():
    """An open box around a plate with a hole: the caps lie 40 mm beyond the plate and the seed upstream of it."""
    from types import SimpleNamespace

    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut

    from opencad.assembly.domains import derive_fluid
    from opencad.geomcheck.assembly import make_box

    plate = BRepAlgoAPI_Cut(make_box([0, 40, 0], [100, 50, 100]), make_box([40, 39, 40], [60, 51, 60]))
    plate.Build()
    planes = (
        ("in", [50, 0, 50], [0, -1, 0]),
        ("out", [50, 100, 50], [0, 1, 0]),
        ("x0", [0, 50, 50], [-1, 0, 0]),
        ("x1", [100, 50, 50], [1, 0, 0]),
        ("z0", [50, 50, 0], [0, 0, -1]),
        ("z1", [50, 50, 100], [0, 0, 1]),
    )
    caps = [SimpleNamespace(name=n, point=[float(v) for v in p], normal=[float(v) for v in d]) for n, p, d in planes]
    r = derive_fluid([plate.Shape()], [], caps, [50.0, 10.0, 50.0])
    expected = 100.0**3 - (100 * 10 * 100 - 20 * 10 * 20)
    assert r.get("sealed") and abs(r["volume"] - expected) < 1e-3 * expected, (r.get("error"), r.get("volume"), expected)


def test_a_requirement_is_judged_over_the_numerical_band():
    from types import SimpleNamespace

    from opencad.assembly.simulate import requirement
    from opencad.schemas import Quantity

    need = SimpleNamespace(min=500.0, max=None, expected=None)
    assert requirement(need, 4079.0, 1177.0)["ok"] is True  # mixer-01: 1725..6433 Pa clears 500 even unresolved
    assert requirement(need, 900.0, 300.0)["ok"] is None and requirement(need, 900.0, 0.0)["ok"] is True  # uncertainty never buys a pass
    assert requirement(need, 300.0, 50.0)["ok"] is False
    exact = SimpleNamespace(min=None, max=None, expected=Quantity(expected=-0.5, tolerance=1e-5))
    assert requirement(exact, -0.5, None)["ok"] is True and requirement(exact, -0.49, None)["ok"] is False


def test_the_refinement_gate_passes_only_resolved_ladders(machine):
    from opencad.assembly import gates
    from opencad.sim import refinement, study

    def gate(*values):
        rows = [{"label": f"{f:g}", "factor": f, "value": v} for f, v in zip((1.0, 0.7, 0.5), values)]
        st = study(rows, expected=3, tolerance=0.05)
        machine.write_stage("simulate", {"simulations": {"cfd": {"status": "ok", "refinement": refinement({"rise": st}, 0.05)}}, "observables": {}})
        return next(g for g in gates.evaluate(machine)["gates"] if g["id"] == "refinement")

    good, wide, lost = gate(110.0, 104.0, 102.0), gate(141.0, 90.0, 60.0), gate(141.0, 90.0)
    assert good["ok"] and "rise GCI 0.0255 resolved" in good["evidence"][0]
    assert wide["ok"] is False and "GCI" in wide["evidence"][0] and wide["details"]["unresolved"] == {"cfd": ["rise"]}
    assert lost["ok"] is False and "did not finish" in lost["evidence"][0]

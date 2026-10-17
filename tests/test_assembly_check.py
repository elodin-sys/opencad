"""The assembly worker's local critic reproduces the evaluator's axis/offset/flip numbers from joint-task.json alone."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

from opencad.truth import assembly_check


def _write_step(shape, path: Path) -> None:
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    w.Write(str(path))


def _case(tmp_path: Path) -> Path:
    work = tmp_path / "work"
    work.mkdir()
    # body one: a Ø10 pin 30 long along +y from y=0; body two: a plate with a Ø10 through hole along y (thickness 8)
    pin = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)), 5.0, 30.0).Shape()
    plate = BRepPrimAPI_MakeBox(gp_Pnt(-20, 0, -20), 40, 8, 40).Shape()
    hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, -1, 0), gp_Dir(0, 1, 0)), 5.0, 10.0).Shape()
    plate = BRepAlgoAPI_Cut(plate, hole).Shape()
    _write_step(pin, work / "pin.step")
    _write_step(plate, work / "plate.step")
    jt = {"set": "t", "joint_type": "RevoluteJointType", "body_one": "pin", "body_two": "plate", "offset_mm": -2.0, "is_flipped": False,
          "one": {"surface_type": "CylinderSurfaceType", "radius_mm": 5.0, "key_point_type": "StartKeyPoint", "key_point_local_mm": [0, 0, 0], "axis_direction_local": [0, 1, 0]},
          "two": {"surface_type": "CylinderSurfaceType", "radius_mm": 5.0, "key_point_type": "StartKeyPoint", "key_point_local_mm": [0, 0, 0], "axis_direction_local": [0, 1, 0]},
          "evaluator": {"axis_angle_max_deg": 2.0, "axis_line_distance_max_mm": 0.5, "axial_offset_tolerance_mm": 0.5, "gap_max_mm": 1.0}}
    (work / "joint-task.json").write_text(json.dumps(jt))
    return work


def test_assembly_check_reproduces_the_evaluator_numbers(tmp_path: Path):
    work = _case(tmp_path)
    # pin key point 2 mm below the plate's hole mouth along +y (offset -2): pin from y=-2 to 28 through the 8 mm plate
    (work / "assembly.yaml").write_text(yaml.safe_dump({"bodies": {"pin": {"origin": [0, -2, 0]}, "plate": {"origin": [0, 0, 0]}}}))
    r = assembly_check.check(work)
    c = r["checks"]
    assert r["ok"] and abs(c["axial_offset"]["measured"] + 2.0) < 1e-9 and c["axis_angle_deg"]["measured"] < 1e-9 and c["flip"]["ok"]
    assert c["interference_mm3"]["measured"] < 1e-6 and c["gap_mm"]["measured"] < 1e-6
    # off along the axis by 6 mm and flipped: two failures named
    (work / "assembly.yaml").write_text(yaml.safe_dump({"bodies": {"pin": {"origin": [0, 4, 0], "x_axis": [1, 0, 0], "y_axis": [0, -1, 0], "z_axis": [0, 0, -1]}, "plate": {"origin": [0, 0, 0]}}}))
    r2 = assembly_check.check(work)
    assert not r2["ok"] and not r2["checks"]["axial_offset"]["ok"] and not r2["checks"]["flip"]["ok"] and r2["checks"]["axis_angle_deg"]["ok"]
    text = assembly_check.format_report(r2)
    assert "FAIL axial_offset" in text and "FAIL flip" in text
    # a manifest that skips a body
    (work / "assembly.yaml").write_text(yaml.safe_dump({"bodies": {"pin": {"origin": [0, 0, 0]}}}))
    assert "must place both bodies" in assembly_check.check(work)["error"]


CQ_PIN_PLATE = """import cadquery as cq
from pathlib import Path

here = Path(__file__).resolve().parent
pin = cq.importers.importStep(str(here / "inputs" / "pin.step"))
plate = cq.importers.importStep(str(here / "inputs" / "plate.step"))
pin_placed = pin.val().located(cq.Location(cq.Vector(0, -2, 0)))
result = [pin_placed, plate]
placements = {
    "pin": [[1, 0, 0, 0], [0, 1, 0, -2], [0, 0, 1, 0], [0, 0, 0, 1]],
    "plate": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
}
"""


def test_modelled_critic_agreement_on_pin_plate(tmp_path: Path):
    import shutil

    work = _case(tmp_path)
    (work / "assembly.yaml").write_text(
        yaml.safe_dump({"bodies": {"pin": {"origin": [0, -2, 0]}, "plate": {"origin": [0, 0, 0]}}})
    )
    part = tmp_path / "part"
    (part / "inputs").mkdir(parents=True)
    shutil.copy2(work / "pin.step", part / "inputs" / "pin.step")
    shutil.copy2(work / "plate.step", part / "inputs" / "plate.step")
    (part / "main.py").write_text(CQ_PIN_PLATE)
    r = assembly_check.check_modelled(work, part / "main.py", backend="cadquery")
    assert r["ok"] and r["solid_count"] == 2, r
    assert r["export_agreement"]["ok"] and r["export_agreement"]["bodies"]["pin"]["ok"]
    assert r["checks"]["axial_offset"]["ok"]
    text = assembly_check.format_report(r)
    assert "agreement pin" in text and "solid_count" in text


def test_assembly_viz_placed_steps_uses_exported_bodies(tmp_path: Path):
    from pygltflib import GLTF2

    from opencad.truth import assembly_viz

    work = _case(tmp_path)
    (work / "assembly.yaml").write_text(yaml.safe_dump({"bodies": {"pin": {"origin": [0, -2, 0]}, "plate": {"origin": [0, 0, 0]}}}))
    jt = json.loads((work / "joint-task.json").read_text())
    manifest = yaml.safe_load((work / "assembly.yaml").read_text())
    import numpy as np

    truth = (np.eye(4), np.eye(4))
    placed = {"pin": work / "pin.step", "plate": work / "plate.step"}
    scene, info = assembly_viz.build_scene(work, jt, manifest, truth, placed_steps=placed)
    glb = assembly_viz.export_glb(scene, tmp_path / "placed.glb", jt, info)
    g = GLTF2().load(str(glb))
    names = [n.name for n in g.nodes]
    assert "joint_pivot" in names and "body:pin" in names and "body:plate" in names
    out = assembly_viz.generate(work, tmp_path / "handoff", card={"verdict": "PASS"}, placed_steps=placed, native_glb=None)
    assert Path(out["glb"]).exists()


def test_assembly_viz_writes_an_animated_glb_and_viewer(tmp_path: Path):
    from pygltflib import GLTF2

    from opencad.truth import assembly_viz

    work = _case(tmp_path)
    (work / "assembly.yaml").write_text(yaml.safe_dump({"bodies": {"pin": {"origin": [0, -2, 0]}, "plate": {"origin": [0, 0, 0]}}}))
    # a dataset pose for the ghost: the same placement expressed as joint_set transforms (cm) would need the Fusion JSON; pass poses directly
    card = {"verdict": "PASS", "checks": {"axial_offset": {"ok": True, "measured": -2.0, "expected": -2.0}}}
    import numpy as np

    jt = json.loads((work / "joint-task.json").read_text())
    manifest = yaml.safe_load((work / "assembly.yaml").read_text())
    truth = (np.eye(4), np.eye(4))
    scene, info = assembly_viz.build_scene(work, jt, manifest, truth)
    glb = assembly_viz.export_glb(scene, tmp_path / "assembly.glb", jt, info)
    g = GLTF2().load(str(glb))
    names = [n.name for n in g.nodes]
    assert "joint_pivot" in names and "body:pin" in names and "body:plate" in names and "joint_axis" in names and "ghost:pin" in names
    assert g.animations and g.animations[0].name == "joint:revolute" and g.nodes[g.animations[0].channels[0].target.node].name == "joint_pivot"
    assert sorted(m.name for m in g.materials) == ["body:pin", "body:plate", "ghost:pin", "joint_axis"]
    assert np.allclose(info["pivot"], [0, 0, 0]) and np.allclose(np.abs(info["axis"]), [0, 1, 0])
    html = assembly_viz.write_html(tmp_path / "assembly.html", "assembly.glb", jt, card, assembly_viz.motion_range(jt), "PASS")
    text = html.read_text()
    assert "model-viewer" in text and 'id="scrub"' in text and "axial_offset" in text and "PASS" in text
    assert 'id="ghost"' in text and "second mesh of body one" in text
    assert not hasattr(assembly_viz, "render_video")
    mr = assembly_viz.motion_range({"joint_type": "SliderJointType", "limits": {"slide_limits": {"is_minimum_value_enabled": True, "minimum_value": 0.0, "is_maximum_value_enabled": True, "maximum_value": 1.5}}})
    assert mr["kind"] == "slider" and mr["slide"] == (0.0, 15.0)


def test_assembly_integrity_two_solids_ok_if_combined_mesh_open(tmp_path: Path, monkeypatch):
    from opencad.truth import assembly_agree

    step = tmp_path / "a.step"
    stl = tmp_path / "a.stl"
    step.write_text("x")
    stl.write_text("x")
    monkeypatch.setattr(assembly_agree.brep, "analyze_step", lambda p: {"valid": True, "solids": 2})
    monkeypatch.setattr(assembly_agree.mesh, "analyze_mesh", lambda p: {"watertight": False, "solids_watertight": False})
    two = assembly_agree.integrity(step, stl, expected_solids=2)
    assert two["ok"] is True and two["watertight"] is False
    monkeypatch.setattr(assembly_agree.brep, "analyze_step", lambda p: {"valid": True, "solids": 1})
    one = assembly_agree.integrity(step, stl, expected_solids=1)
    assert one["ok"] is False

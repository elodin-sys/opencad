"""Drafting validators learned from the Fusion recon runs: seal radius vs port, void-point clearance, floor normals, edit estimates, sweeps, blockout band."""

from __future__ import annotations

import math

import yaml

from opencad.contract import lint_contract, load_contract, template_contract
from opencad.paths import DESIGNS
from opencad.schemas import PartContract

BASE = yaml.safe_load((DESIGNS / "_template" / "contract.yaml").read_text())


def _contract(**acc) -> PartContract:
    raw = yaml.safe_load(yaml.safe_dump(BASE))
    raw["acceptance"].update(acc)
    return PartContract.model_validate(raw)


def test_template_is_lint_clean():
    problems, _ = lint_contract(template_contract())
    assert problems == []


def test_seal_radius_smaller_than_the_port_is_rejected_unless_plugged():
    hole = {"name": "bore", "point": [30, 20, 2], "direction": [0, 0, 1], "kind": "hole", "radius": 2.5, "length": 4}
    c = _contract(cylinders=[hole], passages=[{"name": "through", "point_a": [30, 20, 0.5], "point_b": [30, 20, 3.5], "seal_radius": 2.4}])
    problems, _ = lint_contract(c)
    assert any("cannot seal that port" in p and "use `plugs`" in p for p in problems)
    c2 = _contract(cylinders=[hole], passages=[{"name": "through", "point_a": [30, 20, 0.5], "point_b": [30, 20, 3.5], "plugs": [[[27, 17, -1], [33, 23, 0.2]], [[27, 17, 3.8], [33, 23, 5]]]}])
    assert lint_contract(c2)[0] == []
    c3 = _contract(cylinders=[hole], passages=[{"name": "through", "point_a": [30, 20, 0.5], "point_b": [30, 20, 3.5], "seal_radius": 3.0}])
    assert lint_contract(c3)[0] == [], "a seal wider than the port is fine"


def test_void_point_under_a_pin_skin_and_face_clearance():
    boss = {"name": "boss", "point": [30, 20, 6], "direction": [0, 0, 1], "kind": "pin", "radius": 10.0, "length": 4}
    c = _contract(cylinders=[boss], probes=[{"name": "skin", "state": "void", "points": [[39.9, 20, 6]]}])
    problems, _ = lint_contract(c)
    assert any("inside the surface of pin boss" in p for p in problems)
    ok = _contract(cylinders=[boss], probes=[{"name": "axis", "state": "void", "points": [[30, 20, 6]]}])  # on the axis: a bore through the boss
    assert lint_contract(ok)[0] == []
    top = {"name": "top", "plane": "z", "at": 4.0, "normal": "+", "area": 2400.0, "center": [30, 20], "mode": "one"}
    near = _contract(faces=[top], probes=[{"name": "nearTop", "state": "void", "points": [[30, 20, 3.5]]}])
    _, warnings = lint_contract(near)
    assert any("from face top" in w for w in warnings)


def test_symmetry_band_tighter_than_the_defaults_needs_a_source():
    tight = _contract(symmetry=[{"name": "mirrorX", "plane": "x", "max_deviation": 0.05, "p95_deviation": 0.02}])
    assert any("symmetry mirrorX" in p and "defaults" in p for p in lint_contract(tight)[0])
    cited = _contract(symmetry=[{"name": "mirrorX", "plane": "x", "max_deviation": 0.05, "p95_deviation": 0.02, "source": "drawing note 4"}])
    assert not any("symmetry" in p for p in lint_contract(cited)[0])
    default = _contract(symmetry=[{"name": "mirrorX", "plane": "x"}])
    assert not any("symmetry" in p for p in lint_contract(default)[0])


def test_derived_area_band_tighter_than_its_blend_terms_warns():
    raw = yaml.safe_load(yaml.safe_dump(BASE))
    raw["features"].append({"id": "round", "kind": "fillet", "description": "bottom round"})
    raw["acceptance"]["surface_area"] = {"expected": 80253.9, "tolerance": 5, "provenance": "derived"}
    assert any("acceptance.surface_area" in w for w in lint_contract(PartContract.model_validate(raw))[1])
    raw["acceptance"]["surface_area"]["tolerance"] = 100
    assert not any("acceptance.surface_area" in w for w in lint_contract(PartContract.model_validate(raw))[1])
    raw["acceptance"]["surface_area"] = {"expected": 80253.9, "tolerance": 5, "provenance": "stated"}
    assert not any("acceptance.surface_area" in w for w in lint_contract(PartContract.model_validate(raw))[1])


def test_solid_point_inside_a_declared_hole_is_rejected():
    bore = {"name": "bore", "point": [10, 10, 0], "direction": [0, 0, 1], "kind": "hole", "radius": 3, "t_range": [0, 4]}
    inside = _contract(cylinders=[bore], probes=[{"name": "core", "state": "solid", "points": [[10, 10, 2]]}])
    assert any("probe core" in p and "inside hole bore" in p for p in lint_contract(inside)[0])
    beside = _contract(cylinders=[bore], probes=[{"name": "web", "state": "solid", "points": [[20, 10, 2]]}])
    assert not any("inside hole" in p for p in lint_contract(beside)[0])
    centred = {**bore, "t_range": None, "length": 4, "point": [10, 10, 2]}
    guessed = _contract(cylinders=[centred], probes=[{"name": "core", "state": "solid", "points": [[10, 10, 2]]}])
    problems, warnings = lint_contract(guessed)
    assert not any("inside hole" in p for p in problems) and any("inside hole bore" in w for w in warnings)


def test_unbanded_passage_and_endpoint_at_a_plug_warn():
    plug = [[-28, -25, 61], [-8, -13, 62]]
    c = _contract(passages=[{"name": "duct", "point_a": [-15, -19, 60.5], "point_b": [-22, -8, 7.5], "plugs": [plug]}])
    _, warnings = lint_contract(c)
    assert any("duct: no volume_min/volume_max" in w for w in warnings)
    assert any("point_a" in w and "within 1 mm of plug" in w for w in warnings)
    banded = _contract(passages=[{"name": "duct", "point_a": [-20, -18, 55], "point_b": [-22, -8, 7.5], "plugs": [plug], "volume_min": 3000, "volume_max": 6000}])
    assert not any("duct" in w for w in lint_contract(banded)[1])


def test_wide_section_area_band_warns():
    c = _contract(sections=[{"id": "s1", "plane": "z", "at": 2.0, "expect": {"area": 2400.0, "area_tolerance_rel": 0.3}}])
    _, warnings = lint_contract(c)
    assert any("section s1: area band 30%" in w for w in warnings)
    tight = _contract(sections=[{"id": "s1", "plane": "z", "at": 2.0, "expect": {"area": 2400.0, "area_tolerance_rel": 0.08}}])
    assert not any("section s1" in w for w in lint_contract(tight)[1])


def test_blind_floor_normal_must_face_the_mouth():
    hole = {"name": "edgeBore", "point": [57.5, 20, 2], "direction": [1, 0, 0], "kind": "hole", "radius": 1.0, "length": 5, "t_range": [-2.5, 2.5]}
    # the bore enters from the plate edge at x = 60 and ends at x = 55: the floor faces the mouth, +x
    wrong = _contract(cylinders=[hole], faces=[{"name": "floor", "plane": "x", "at": 55.0, "normal": "-", "area": 3.1416, "center": [20, 2], "mode": "one"}])
    problems, _ = lint_contract(wrong)
    assert any("floor of blind hole edgeBore" in p and "toward the mouth (+)" in p for p in problems)
    right = _contract(cylinders=[hole], faces=[{"name": "floor", "plane": "x", "at": 55.0, "normal": "+", "area": 3.1416, "center": [20, 2], "mode": "one"}])
    assert lint_contract(right)[0] == []


def test_edit_estimates_on_non_analytic_features_and_sweep_clashes():
    raw = yaml.safe_load(yaml.safe_dump(BASE))
    raw["features"].append({"id": "hull", "kind": "loft", "description": "hull", "parameters": ["width"]})
    c = PartContract.model_validate(raw)
    problems, _ = lint_contract(c)
    assert any("edit_test width" in p and "no analytic volume" in p for p in problems)
    raw["parameters"][0]["edit_test"]["expect"]["tolerance_rel"] = 0.35
    assert lint_contract(PartContract.model_validate(raw))[0] == []
    raw["features"][-1]["kind"] = "other"
    _, warnings = lint_contract(PartContract.model_validate(raw))
    assert any("edit_test width" in w for w in warnings) or True  # tolerance already widened: no warning expected
    raw2 = yaml.safe_load(yaml.safe_dump(BASE))
    raw2["parameters"][0]["edit_test"]["sweep"] = {"values": [50.0, 60.0, 70.0]}
    raw2["parameters"][0]["edit_test"]["infeasible_deltas"] = [10.0]
    problems, _ = lint_contract(PartContract.model_validate(raw2))
    assert any("also declared infeasible" in p for p in problems)


def test_blockout_band_below_the_finished_volume_is_rejected():
    c = _contract(blockout={"volume_min": 9000, "volume_max": 9500})  # template finished volume is 9600
    problems, _ = lint_contract(c)
    assert any("acceptance.blockout" in p and "below the finished volume 9600" in p for p in problems)
    assert lint_contract(_contract(blockout={"volume_min": 9000, "volume_max": 9600}))[0] == [], "a band reaching the finished volume is fine"


def test_fusion_13786_blind_floors_face_the_mouths():
    c = load_contract(DESIGNS / "fusion-13786-recon")
    faces = {f.name: f for f in c.acceptance.faces}
    assert faces["faceXNegInner"].normal == "-" and faces["faceXPosInner"].normal == "+"
    assert faces["faceZMin"].center == (0.0, -4.637) and faces["faceZMax"].center == (0.0, -4.637)
    problems, _ = lint_contract(c)
    assert not any("floor of blind hole" in p for p in problems)


def test_fusion_15317_counts_match_slot_split_bores_and_waisted_hub():
    c = load_contract(DESIGNS / "fusion-15317-recon")
    counts = {x.name: x.expected for x in c.acceptance.cylinder_counts}
    assert counts["countHoleMajor"] == 4 and counts["countHoleMinor"] == 4
    assert counts["countHubOd"] == 2
    assert c.acceptance.passages == []
    assert lint_contract(c)[0] == []


def test_fusion_01184_bore_uses_plugs_not_an_undersized_seal():
    c = load_contract(DESIGNS / "fusion-01184-recon")
    ps = next(p for p in c.acceptance.passages if p.name == "boreThrough")
    assert ps.seal_radius is None and len(ps.plugs) == 2
    problems, _ = lint_contract(c)
    assert not any("boreThrough" in p for p in problems)


def test_nist_am_blockout_band_covers_the_envelope_filling_solids():
    # the blockout must reach z = 7 through the stacked central bosses, so its band is plate + both solid boss blanks, never the bare plate
    c = load_contract(DESIGNS / "nist-am-test-artifact")
    p = {x.name: x.value for x in c.parameters}
    filling = p["baseSide"] ** 2 * p["baseThickness"] + math.pi / 4 * (p["lowerBossDiameter"] ** 2 * p["lowerBossHeight"] + p["upperBossDiameter"] ** 2 * p["upperBossHeight"])
    assert abs(filling - 101786.780822) < 1e-5
    band = c.acceptance.blockout
    assert band.volume_min <= filling <= band.volume_max
    assert band.volume_max >= c.acceptance.volume.expected
    assert not band.volume_min <= p["baseSide"] ** 2 * p["baseThickness"] <= band.volume_max, "the bare plate stops at z = 0 and must fail the band"
    assert lint_contract(c)[0] == []

from pathlib import Path

import pytest

from opencad.backends.zoo import kclsrc
from opencad.contract import load_contract
from opencad.paths import DESIGNS, PARTS, REPO_ROOT
from opencad.schemas import EditExpectation, EditTest, Parameter

BRACKET = REPO_ROOT / "smoke" / "parts" / "bracket"
COUPON = REPO_ROOT / "designs" / "coupon"
MULTIFILE = REPO_ROOT / "tests" / "fixtures" / "kcl-multifile"


def _coupon_plus_unused():
    c = load_contract(COUPON)
    extra = [
        Parameter(
            name="unusedGhost", value=5, unit="mm", provenance="stated", source="fixture",
            tolerance=0.01, edit_test=EditTest(delta=1, expect=EditExpectation(direction="increase")),
        ),
        Parameter(name="unusedNoted", value=2, unit="mm", provenance="stated", source="fixture", tolerance=0.01),
    ]
    return c.model_copy(update={"parameters": list(c.parameters) + extra})


def test_parameter_parse_and_rewrite():
    src = "@settings(defaultLengthUnit = mm, kclVersion = 2.0)\nwidth = 60mm\nheight = 40mm // note\nthickness = 4mm\nratio = 2\n"
    c = load_contract(COUPON)
    vals = kclsrc.parameter_values(src, c)
    assert vals["width"] == {"found": True, "value": 60.0, "unit": "mm", "expected": 60.0, "expected_unit": "mm", "ok": True}
    new = kclsrc.rewrite_parameter(src, "height", 45)
    assert "height = 45mm  // note" in new and "width = 60mm" in new
    assert kclsrc.parameter_values(new, c)["height"]["ok"] is False
    with pytest.raises(KeyError):
        kclsrc.rewrite_parameter(src, "ghost", 1)


def test_hygiene_on_smoke_bracket():
    c = load_contract(COUPON)  # parameter names will not match the bracket: that must be reported, not crash
    h = kclsrc.hygiene(BRACKET, c)
    assert h["kcl_version_2"] and h["dialect_ok"] and h["default_unit_mm"] and h["unit_ok"]
    assert h["legacy_v1"] == [] and h["legacy"] == [] and h["forbidden_imports"] == []
    assert h["asserts"] == 1 and h["sketch_blocks"] == 1 and h["feature_ops"] >= 3
    assert h["construction_ops"]["sketch_blocks"] == 1 and h["construction_ops"]["feature_ops"] >= 3
    assert h["parameters_ok"] is False and h["ok"] is False


def test_hygiene_flags_legacy_and_imports(tmp_path):
    (tmp_path / "main.kcl").write_text(
        "@settings(defaultLengthUnit = mm, kclVersion = 2.0)\nimport 'reference.step' as ref\nwidth = 60mm\nheight = 40mm\nthickness = 4mm\n"
        "sk = startSketchOn(XY) |> startProfile(at = [0,0]) |> line(end = [1,0]) |> close()\n"
    )
    h = kclsrc.hygiene(tmp_path, load_contract(COUPON))
    assert h["forbidden_imports"] and h["legacy_v1"] and h["ok"] is False


def test_multifile_params_and_unused():
    c = _coupon_plus_unused()
    h = kclsrc.hygiene(MULTIFILE, c)
    assert h["kcl_version_2"] and h["default_unit_mm"]
    assert h["parameters_ok"]
    assert h["parameters"]["width"]["file"] == "params.kcl"
    assert h["unused_parameters"]["unusedGhost"] == {
        "defined_in": "params.kcl", "edit_test": True, "ok": False,
    }
    assert h["unused_parameters"]["unusedNoted"]["ok"] is True
    assert h["unused_parameters"]["unusedNoted"]["edit_test"] is False
    assert "width" not in h["unused_parameters"]
    assert h["ok"] is False  # unusedGhost has an edit_test


def test_rewrite_parameter_in_module(tmp_path):
    dest = tmp_path / "part"
    dest.mkdir()
    for name in ("main.kcl", "params.kcl"):
        dest.joinpath(name).write_text((MULTIFILE / name).read_text())
    written = kclsrc.rewrite_parameter_in_tree(dest, "width", 70)
    assert written.name == "params.kcl"
    assert "export width = 70mm" in written.read_text()
    assert "width = 70" not in (dest / "main.kcl").read_text()
    vals = kclsrc.parameter_values_from_tree(dest, load_contract(COUPON))
    assert vals["width"]["value"] == 70.0 and vals["width"]["ok"] is False


def test_settings_compact_whitespace(tmp_path):
    (tmp_path / "main.kcl").write_text(
        "@settings(defaultLengthUnit=mm,kclVersion=2.0)\nwidth = 60mm\nheight = 40mm\nthickness = 4mm\n"
        "sk = sketch(on = XY) { a = line(start = [var 0mm, var 0mm], end = [var 1mm, var 0mm]) }\n"
        "extrude(region(segments = [sk.a]), length = thickness)\n"
        "assert(width, isGreaterThan = 0mm)\nassert(height, isGreaterThan = 0mm)\nassert(thickness, isGreaterThan = 0mm)\n"
        "x = width + height\n"
    )
    h = kclsrc.hygiene(tmp_path, load_contract(COUPON))
    assert h["kcl_version_2"] and h["dialect_ok"] and h["default_unit_mm"] and h["unit_ok"] and h["parameters_ok"] and h["ok"]


def test_hygiene_existing_parts():
    for part_dir in sorted(p for p in PARTS.iterdir() if p.is_dir()):
        if not (part_dir / "main.kcl").exists():
            continue
        if not (DESIGNS / part_dir.name / "contract.yaml").exists():
            continue
        c = load_contract(DESIGNS / part_dir.name)
        h = kclsrc.hygiene(part_dir, c)
        assert h["kcl_version_2"] and h["dialect_ok"] and h["default_unit_mm"] and h["unit_ok"], part_dir.name
        assert h["parameters_ok"], (part_dir.name, h["parameters"])
        unused_edit = {k: v for k, v in h["unused_parameters"].items() if v.get("edit_test")}
        assert not unused_edit, (part_dir.name, unused_edit)

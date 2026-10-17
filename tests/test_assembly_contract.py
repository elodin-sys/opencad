import copy
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from opencad import contract as contract_mod
from opencad.contract import check_assembly_bundle, lint_assembly, load_assembly, publish_assembly, stage_assembly
from opencad.paths import DOCS, TEMPLATE
from opencad.schemas import AssemblyContract

EXEMPLAR = DOCS / "exemplar-assembly.yaml"


def exemplar() -> dict:
    return yaml.safe_load(EXEMPLAR.read_text(encoding="utf-8"))


def test_exemplar_and_template_validate():
    a = load_assembly(EXEMPLAR)
    assert a.expected_solids() == 5
    assert a.designs() == ["demo-blower-housing", "demo-blower-impeller", "demo-blower-pinion"]
    assert lint_assembly(a) == ([], [])
    assert load_assembly(TEMPLATE / "assembly.yaml").name == "new-assembly"


@pytest.mark.parametrize(
    "mutate, message",
    [
        (lambda d: d["joints"].pop(1), "is not attached"),
        (lambda d: d["joints"][0]["child_frame"].pop("ref"), "rigid joint needs `ref`"),
        (lambda d: d["joints"][2].update(parent="impeller", child="housing"), "datum part"),
        (lambda d: d["transmissions"][0].update(driven="nope"), "unknown joint"),
        (lambda d: d["parts"][4].update(kind="modelled", design="demo-blower-air"), "fluid body is derived"),
        (lambda d: d["observables"][0].update(simulation="missing"), "unknown simulation"),
        (lambda d: d["acceptance"]["clearances"][0].update(b="casing"), "unknown body"),
        (lambda d: d["boundaries"][0].pop("normal"), "needs ['normal']"),
        (lambda d: d["simulations"][0].update(solver="ansys"), "solver must be"),
        (lambda d: d["simulations"][0]["inputs"]["airDensity"].pop("source"), "requires `source`"),
    ],
)
def test_cross_reference_errors(mutate, message):
    d = exemplar()
    mutate(d)
    with pytest.raises(ValidationError, match=message.replace("[", r"\[").replace("]", r"\]").replace("`", "`")):
        AssemblyContract.model_validate(d)


def test_construction_input_is_staged_but_not_placed():
    d = exemplar()
    d["parts"].append({"name": "cavity", "kind": "purchased", "role": "construction",
                       "catalog": {"name": "cavity", "kind": "box", "min": [0.0, 0.0, 0.0], "max": [10.0, 10.0, 10.0]}})
    a = AssemblyContract.model_validate(d)
    assert a.expected_solids() == 5 and not a.part("cavity").placed
    d["joints"][1]["child"] = "cavity"
    with pytest.raises(ValidationError, match="unknown body 'cavity'"):
        AssemblyContract.model_validate(d)


def test_joint_cycle_is_rejected():
    d = exemplar()
    d["joints"].append(copy.deepcopy(d["joints"][1]) | {"name": "loop", "parent": "pinion", "child": "motor"})
    with pytest.raises(ValidationError, match="child of two joints"):
        AssemblyContract.model_validate(d)


def test_lint_flags_frame_outside_part_envelope_and_unknown_model(tmp_path):
    part = yaml.safe_load((TEMPLATE / "contract.yaml").read_text(encoding="utf-8"))
    part["name"] = "demo-blower-pinion"
    part["envelope"] = {"min": [-6.0, -6.0, 0.0], "max": [6.0, 6.0, 4.0], "tolerance": 0.1}
    (tmp_path / "demo-blower-pinion").mkdir()
    (tmp_path / "demo-blower-pinion" / "contract.yaml").write_text(yaml.safe_dump(part), encoding="utf-8")
    d = exemplar()
    d["joints"][1]["child_frame"]["origin"] = [15.0, 0.0, 0.0]
    d["simulations"][0]["solver"] = "reduced:nonsense"
    problems, _ = lint_assembly(AssemblyContract.model_validate(d), designs_root=tmp_path)
    assert any("outside pinion's contract envelope" in p for p in problems)
    assert any("unknown reduced model" in p for p in problems)


def test_lint_flags_observable_missing_from_outputs():
    d = exemplar()
    d["simulations"][0]["outputs"] = ["pressureRise"]
    problems, _ = lint_assembly(AssemblyContract.model_validate(d))
    assert any("pressureRiseHigh" in p and "outputs" in p for p in problems)


def test_lint_flags_an_observable_nothing_computes():
    d = exemplar()
    d["observables"].append({"id": "airVolume", "quantity": "volume", "unit": "mm3", "body": "air"})
    problems, _ = lint_assembly(AssemblyContract.model_validate(d))
    assert any("airVolume" in p and "fluid_volume" in p for p in problems)
    d["observables"][-1]["quantity"] = "fluid_volume"
    assert lint_assembly(AssemblyContract.model_validate(d))[0] == []


def test_lint_orders_refinement_ladders_and_keeps_regions_on_openfoam():
    d = exemplar()
    cfd = d["simulations"][1]
    cfd["refinement"] = [{"factor": 0.7, "regions": {"tipGap": 1}}, {"factor": 1.0, "regions": {"tipGap": 1}}]
    assert any("neither finer everywhere" in p for p in lint_assembly(AssemblyContract.model_validate(d))[0])
    cfd["refinement"] = [{"factor": 1.0, "regions": {"tipGap": 1}}, {"factor": 0.7}]
    assert any("neither finer everywhere" in p for p in lint_assembly(AssemblyContract.model_validate(d))[0])
    cfd["refinement"] = [1.0, {"factor": 1.0, "regions": {"tipGap": 1}}, {"factor": 1.0, "regions": {"tipGap": 2}}]
    problems, warnings = lint_assembly(AssemblyContract.model_validate(d))
    assert not problems and any("sensitivity study" in w for w in warnings)
    cfd["bodies"] = ["air"]
    assert any("needs a rotating body" in p for p in lint_assembly(AssemblyContract.model_validate(d))[0])
    d["simulations"][2]["regions"] = [{"name": "boss", "shape": "box", "min": [0.0, 0.0, 0.0], "max": [1.0, 1.0, 1.0]}]
    assert any("openfoam setting" in p for p in lint_assembly(AssemblyContract.model_validate(d))[0])


def test_stage_check_publish_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(contract_mod, "DESIGNS", tmp_path)
    monkeypatch.setattr("opencad.paths.DESIGNS", tmp_path)
    staging = stage_assembly("demo-blower")
    assert any("placeholder" in p for p in check_assembly_bundle(staging, "demo-blower"))
    d = exemplar()
    (staging / "sources" / "spec.md").write_text("spec\n", encoding="utf-8")
    (staging / "assembly.yaml").write_text(yaml.safe_dump(d, sort_keys=False), encoding="utf-8")
    (staging / "brief.md").write_text("# demo-blower\n\nfilled\n", encoding="utf-8")
    assert check_assembly_bundle(staging, "demo-blower") == []
    target = publish_assembly(staging, "demo-blower")
    assert target == tmp_path / "demo-blower" and (target / "assembly.yaml").exists()
    assert contract_mod.is_assembly(target) and not contract_mod.is_assembly(Path(tmp_path))

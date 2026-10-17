from pathlib import Path

import pytest
import yaml

from opencad.contract import ContractError, check_bundle, load_contract, publish_bundle, template_contract
from opencad.paths import DESIGNS, TEMPLATE, PartNameError, check_part_name, resolve_part
from opencad.schemas import PartContract


def template_dict() -> dict:
    return yaml.safe_load((TEMPLATE / "contract.yaml").read_text())


def test_template_validates():
    c = template_contract()
    assert c.envelope.volume == 60 * 40 * 4
    assert c.blockout_band() == (9000, 9600.1)
    assert c.provenance_summary() == {"stated": 3}


@pytest.mark.parametrize(
    "mutate, message",
    [
        (lambda d: d["parameters"][0].pop("source"), "requires `source`"),
        (lambda d: d["parameters"][0].update(provenance="derived"), "require `formula`"),
        (lambda d: d["parameters"][0].update(provenance="inferred"), "require `rationale`"),
        (lambda d: d["parameters"][0].update(tolerance=0), "greater than 0"),
        (lambda d: d["features"][0]["parameters"].append("ghost"), "unknown parameter"),
        (lambda d: d["acceptance"]["sections"][0].update(at=99), "outside the envelope"),
        (lambda d: d["envelope"].update(max=[-1, 40, 4]), "envelope.max"),
        (lambda d: d["acceptance"]["volume"].pop("tolerance_rel"), "needs `tolerance`"),
        (lambda d: d.update(bogus=1), "extra"),
        (lambda d: d["parameters"][0].update(name="not valid"), "not a KCL identifier"),
    ],
)
def test_rejections(mutate, message):
    d = template_dict()
    mutate(d)
    with pytest.raises(Exception) as ei:
        PartContract.model_validate(d)
    assert message.lower() in str(ei.value).lower()


def test_quantity_within():
    c = template_contract()
    ok, band = c.acceptance.volume.within(9600 * 1.001)
    assert ok and band == pytest.approx(9600 * 0.002)
    ok, _ = c.acceptance.volume.within(9700)
    assert not ok
    ok, errs = c.acceptance.center_of_mass.within((30.01, 20, 2))
    assert ok and errs[0] == pytest.approx(0.01)


def test_part_names():
    assert check_part_name("bracket-v2") == "bracket-v2"
    for bad in ["_template", "../x", "a/b", ".hidden", "", "x" * 65]:
        with pytest.raises(PartNameError):
            check_part_name(bad)


def test_resolve_part():
    name, contract, results = resolve_part("bracket")
    assert (name, contract.name, results.name) == ("bracket", "contract.yaml", "bracket")
    assert resolve_part("designs/bracket")[0] == "bracket"
    assert resolve_part("designs/bracket/contract.yaml")[0] == "bracket"
    assert resolve_part(str(DESIGNS / "bracket"))[0] == "bracket"
    with pytest.raises(PartNameError):
        resolve_part("results/bracket")
    with pytest.raises(PartNameError):
        resolve_part("designs/a/b")


def test_bundle_check_and_publish(tmp_path, monkeypatch):
    monkeypatch.setattr("opencad.contract.DESIGNS", tmp_path / "designs")
    monkeypatch.setattr("opencad.paths.DESIGNS", tmp_path / "designs")
    staging = tmp_path / "designs" / ".staging-plate"
    staging.mkdir(parents=True)
    d = template_dict()
    d["name"] = "plate"
    d["intent"] = "A 60 x 40 x 4 mm training coupon."
    d["frame"] = {"origin": "min corner", "axes": {"x": "length", "y": "width", "z": "thickness"}, "datums": []}
    for p in d["parameters"]:
        p["source"] = "intent"
    (staging / "contract.yaml").write_text(yaml.safe_dump(d))
    (staging / "brief.md").write_text("# plate\n\nno placeholders here\n")
    assert check_bundle(staging) == []
    ref = staging / "reference"
    ref.mkdir()
    (ref / "profile.json").write_text("{}")
    (ref / "profile.png").write_bytes(b"")
    (ref / "reference-sections-extra.png").write_bytes(b"")
    (ref / "silhouette-front.png").write_bytes(b"")
    assert check_bundle(staging) == []
    (ref / "notes.txt").write_text("x")
    assert any("unexpected reference entry" in p for p in check_bundle(staging))
    (ref / "notes.txt").unlink()
    (staging / "stray.txt").write_text("x")
    assert any("unexpected bundle entry" in p for p in check_bundle(staging))
    (staging / "stray.txt").unlink()
    target = publish_bundle(staging, "plate")
    assert target == tmp_path / "designs" / "plate" and not staging.exists()
    assert load_contract(target).name == "plate"
    staging.mkdir()
    (staging / "contract.yaml").write_text(yaml.safe_dump(d))
    (staging / "brief.md").write_text("# plate\n")
    with pytest.raises(ContractError, match="already exists"):
        publish_bundle(staging, "plate")


def test_placeholders_block_publish(tmp_path, monkeypatch):
    monkeypatch.setattr("opencad.contract.DESIGNS", tmp_path / "designs")
    monkeypatch.setattr("opencad.paths.DESIGNS", tmp_path / "designs")
    staging = tmp_path / "designs" / ".staging-new"
    staging.mkdir(parents=True)
    d = template_dict()
    d["name"] = "new"
    (staging / "contract.yaml").write_text(yaml.safe_dump(d))
    (staging / "brief.md").write_text((TEMPLATE / "brief.md").read_text())
    problems = check_bundle(staging)
    assert any("placeholder" in p for p in problems)
    with pytest.raises(ContractError, match="not publishable"):
        publish_bundle(staging, "new")
    assert staging.exists()

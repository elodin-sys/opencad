"""Layout resolution: an assembly's part designs nest under it in designs/, parts/<backend>/ and results/<backend>/."""

from pathlib import Path

import pytest
import yaml


def _asm(root: Path, name: str, designs: list[str], *, staged: bool = False) -> None:
    d = root / (f".staging-{name}" if staged else name)
    d.mkdir(parents=True)
    parts = [{"name": x, "kind": "modelled", "design": x} for x in designs] + [{"name": "air", "kind": "derived"}]
    (d / "assembly.yaml").write_text(yaml.safe_dump({"name": name, "parts": parts}))


@pytest.fixture
def roots(tmp_path, monkeypatch):
    from opencad import paths

    for attr, sub in (("DESIGNS", "designs"), ("PARTS_BASE", "parts"), ("RESULTS_BASE", "results")):
        monkeypatch.setattr(paths, attr, tmp_path / sub)
    monkeypatch.setenv("OPENCAD_BACKEND", "build123d")
    (tmp_path / "designs").mkdir()
    return tmp_path


def test_members_nest_in_all_three_trees_and_standalone_parts_stay_flat(roots):
    from opencad import paths

    _asm(roots / "designs", "drone", ["drone-main-shell", "prop"])
    assert paths.design_dir("drone-main-shell") == roots / "designs" / "drone" / "parts" / "main-shell"
    assert paths.part_dir("drone-main-shell") == roots / "parts" / "build123d" / "drone" / "parts" / "main-shell"
    assert paths.results_dir("drone-main-shell", backend="zoo") == roots / "results" / "zoo" / "drone" / "parts" / "main-shell"
    assert paths.design_dir("prop") == roots / "designs" / "drone" / "parts" / "prop", "an unprefixed design keeps its name as the leaf"
    assert paths.design_dir("drone") == roots / "designs" / "drone"
    assert paths.results_dir("bracket") == roots / "results" / "build123d" / "bracket"


def test_a_staged_assembly_already_nests_its_parts(roots):
    from opencad import paths

    _asm(roots / "designs", "mixer", ["mixer-rotor"], staged=True)
    assert paths.design_dir("mixer-rotor") == roots / "designs" / "mixer" / "parts" / "rotor"


def test_reverse_lookup_from_a_nested_design_directory(roots):
    from opencad import paths

    _asm(roots / "designs", "drone", ["drone-main-shell"])
    name, contract, results = paths.resolve_part(roots / "designs" / "drone" / "parts" / "main-shell" / "contract.yaml")
    assert name == "drone-main-shell" and contract == roots / "designs" / "drone" / "parts" / "main-shell" / "contract.yaml"
    assert results == roots / "results" / "build123d" / "drone" / "parts" / "main-shell"
    assert paths.design_name(("drone", "parts", "main-shell", "main.py")) == "drone-main-shell"
    assert paths.design_name(("drone", "inputs", "x.step")) == "drone"
    with pytest.raises(paths.PartNameError, match="names no design"):
        paths.resolve_part(roots / "designs" / "drone" / "parts" / "tail")


def test_a_design_claimed_by_two_assemblies_is_an_error(roots):
    from opencad import paths

    _asm(roots / "designs", "a", ["shared"])
    _asm(roots / "designs", "b", ["shared"])
    with pytest.raises(paths.PartNameError, match="one assembly"):
        paths.design_dir("shared")


def test_all_pending_finds_an_order_inside_a_nested_part(roots):
    from opencad import paths
    from opencad.worker import orders

    _asm(roots / "designs", "drone", ["drone-main-shell"])
    rd = paths.results_dir("drone-main-shell")
    orders.issue(rd, key="model-1", role="model", part="drone-main-shell", brief="B.", cwd=rd, model="m", budget_s=60)
    assert [o.part for o in orders.all_pending(paths.results_root())] == ["drone-main-shell"]


def test_publish_assembly_moves_in_beside_parts_already_published(roots, monkeypatch):
    from opencad import contract

    monkeypatch.setattr(contract, "DESIGNS", roots / "designs")
    monkeypatch.setattr(contract, "check_assembly_bundle", lambda d, n: [])
    staged = roots / "designs" / ".staging-drone"
    (staged / "sources").mkdir(parents=True)
    (staged / "assembly.yaml").write_text("name: drone\n")
    (roots / "designs" / "drone" / "parts" / "main-shell").mkdir(parents=True)
    target = contract.publish_assembly(staged, "drone")
    assert (target / "assembly.yaml").exists() and (target / "sources").is_dir() and (target / "parts" / "main-shell").is_dir()
    assert not staged.exists()
    staged.mkdir()
    with pytest.raises(contract.ContractError, match="already exists"):
        contract.publish_assembly(staged, "drone")


def test_sha256_tree_exclude_skips_the_nested_entries(tmp_path):
    from opencad.io import sha256_tree
    from opencad.paths import NESTED

    (tmp_path / "parts" / "leaf").mkdir(parents=True)
    (tmp_path / "parts" / "leaf" / "main.py").write_text("x")
    (tmp_path / ".amended" / "assembly-1").mkdir(parents=True)
    (tmp_path / ".amended" / "assembly-1" / "assembly.yaml").write_text("y")
    (tmp_path / "assembly.yaml").write_text("z")
    assert list(sha256_tree(tmp_path, exclude=NESTED)) == ["assembly.yaml"]
    assert len(sha256_tree(tmp_path)) == 3

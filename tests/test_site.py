"""Design-review site: discovery by section, viewer and download pages, link integrity, and a guarded output directory."""

import json
from pathlib import Path

import pytest
import trimesh
import yaml


def _result(root: Path, backend: str, name: str, *, ok: bool = True, glb: bool = True, assembly: bool = False) -> Path:
    d = root / "results" / backend / name
    hd = d / "handoff"
    hd.mkdir(parents=True)
    (d / "report.md").write_text(f"# {name}\n")
    gates = [{"id": "envelope", "tier": "A", "title": "bbox", "ok": ok, "evidence": ["inspect.json bbox"], "failure_means": "wrong size"}]
    (d / "gate_feedback.json").write_text(json.dumps({"ok": ok, "passed": ["envelope"] if ok else [], "failed": [] if ok else ["envelope"],
                                                      "not_applicable": [], "gates": gates}))
    box = trimesh.creation.box((10, 20, 5))
    box.export(hd / f"{name}.stl")
    (hd / f"{name}.step").write_text("ISO-10303-21;\n")
    if glb:
        box.export(hd / ("assembly-clips.glb" if assembly else f"{name}.glb"))
    if assembly:
        (hd / "assembly.html").write_text('<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js">'
                                          '</script><model-viewer src="assembly-clips.glb"></model-viewer>')
    (hd / "properties.json").write_text(json.dumps({"volume": 1000.0, "bbox_min": [0, 0, 0], "bbox_max": [10, 20, 5]}))
    return d


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    for name, spec in (("rig", {"name": "rig", "intent": "A test rig. Second sentence.", "parts": [{"name": "arm", "kind": "modelled", "design": "rig-arm"},
                                                                                                 {"name": "bolt", "kind": "purchased"}]}),
                       ("bracket", {"name": "bracket", "intent": "A printed bracket for a sensor."}),
                       ("plate", {"name": "plate", "intent": "Rebuilt test plate."})):
        d = root / "designs" / name
        d.mkdir(parents=True)
        (d / ("assembly.yaml" if "parts" in spec else "contract.yaml")).write_text(yaml.safe_dump(spec))
    (root / "truth" / "cases" / "plate").mkdir(parents=True)
    rig = _result(root, "build123d", "rig", assembly=True)
    leaf = rig / "parts" / "arm" / "handoff"
    leaf.mkdir(parents=True)
    trimesh.creation.box((2, 2, 2)).export(leaf / "rig-arm.stl")
    _result(root, "build123d", "bracket")
    _result(root, "zoo", "bracket", ok=False, glb=False)
    _result(root, "build123d", "plate")
    _result(root, "_spikes", "scratch")
    return root


def test_build_publishes_sections_viewers_downloads_and_backend_tabs(repo, tmp_path):
    from opencad.site.build import build_site, check_links

    out = tmp_path / "site"
    designs = build_site(repo, out, cache=tmp_path / "cache", jobs=1)
    assert [(d.name, d.section) for d in designs] == [("rig", "machine"), ("bracket", "part"), ("plate", "corpus")]
    index = (out / "index.html").read_text()
    assert 'href="d/rig/build123d/"' in index and "A test rig." in index and "Second sentence" not in index
    assert (out / "d" / "rig" / "card.png").stat().st_size > 0

    viewer = (out / "d" / "rig" / "build123d" / "handoff" / "viewer.html").read_text()
    assert "../../../../assets/model-viewer.min.js" in viewer and "googleapis" not in viewer
    rig_page = (out / "d" / "rig" / "build123d" / "index.html").read_text()
    assert 'href="parts/arm/rig-arm.stl"' in rig_page and (out / "d" / "rig" / "build123d" / "parts" / "arm" / "rig-arm.stl").is_file()

    part_viewer = (out / "d" / "bracket" / "build123d" / "handoff" / "viewer.html").read_text()
    assert 'src="bracket.glb"' in part_viewer
    bracket = (out / "d" / "bracket" / "build123d" / "index.html").read_text()
    assert 'href="../zoo/"' in bracket and 'href="handoff/bracket.stl" download' in bracket
    zoo = (out / "d" / "bracket" / "zoo" / "index.html").read_text()
    assert "FAIL" in zoo and "Failing gates" in zoo and "<iframe" not in zoo, "no GLB: the page shows the card image, not a viewer"
    assert 'href="handoff/bracket.stl" download' in zoo and (out / "d" / "bracket" / "zoo" / "handoff" / "bracket.stl").is_file(), \
        "each backend page offers its own print files"
    assert "Assembled machine" in rig_page and 'href="handoff/rig.step" download' in rig_page
    assert "report.md" not in rig_page
    assert not (out / "d" / "scratch").exists()
    assert check_links(out) == []


def test_bakeoff_page_links_published_designs_in_the_gallery(repo, tmp_path):
    from opencad.site.build import build_site

    cell = {"verdict": "FAIL", "passed": 10, "failed": 1, "not_applicable": 1, "failed_gates": ["features"], "turns": 3,
            "tokens_input": 2_000_000, "codex_usd": 7.5, "zoo_credits": None, "zoo_usd": None, "wall_s": 4000}
    entries = [{"part": "bracket", "date": "2026-10-16", "tags": {"zoo": "bakeoff-astra"}, "note": "Every backend fails `features`.",
                "backends": {"zoo": {**cell, "zoo_credits": 12, "zoo_usd": 0.1}, "cadquery": cell}},
               {"part": "ghost", "date": "2026-10-14", "tags": {"zoo": "bakeoff-astra"}, "note": "", "backends": {"zoo": cell}}]
    (repo / "results" / "_bakeoff").mkdir()
    (repo / "results" / "_bakeoff" / "published.yaml").write_text(yaml.safe_dump({"entries": entries}))
    out = tmp_path / "site"
    build_site(repo, out, cache=tmp_path / "cache", jobs=1)
    page = (out / "bakeoff" / "index.html").read_text()
    assert page.index("Bracket") < page.index("Ghost"), "newest first"
    assert 'href="../d/bracket/build123d/"' in page and 'href="../d/ghost' not in page
    assert "<code>features</code>" in page and "12 credits, $0.10" in page and "1h 06m" in page
    index = (out / "index.html").read_text()
    assert 'href="bakeoff/index.html"' in index and "2 published comparisons" in index


def test_overrides_hide_and_retitle_and_links_outside_the_output_are_caught(repo, tmp_path):
    from opencad.site.build import build_site, check_links

    manifest = tmp_path / "designs.yaml"
    manifest.write_text(yaml.safe_dump({"designs": {"plate": {"hidden": True}, "bracket": {"title": "Sensor bracket", "featured": True}}}))
    out = tmp_path / "site"
    designs = build_site(repo, out, manifest=manifest, cache=tmp_path / "cache", jobs=1)
    assert [d.name for d in designs] == ["rig", "bracket"] and next(d for d in designs if d.featured).title == "Sensor bracket"
    (out / "index.html").write_text('<a href="../outside.html">x</a><img src="missing.png">')
    assert check_links(out) == ["index.html -> ../outside.html", "index.html -> missing.png"]


def test_the_output_must_be_a_previous_build_or_empty(repo, tmp_path):
    from opencad.site.build import SiteBuildError, build_site

    out = tmp_path / "busy"
    out.mkdir()
    (out / "keep.txt").write_text("not a site")
    with pytest.raises(SiteBuildError, match="holds no previous site build"):
        build_site(repo, out, cache=tmp_path / "cache", jobs=1)
    with pytest.raises(SiteBuildError, match="contains the repository"):
        build_site(repo, repo.parent, cache=tmp_path / "cache", jobs=1)
    assert (out / "keep.txt").exists()

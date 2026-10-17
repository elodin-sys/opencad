"""Local engine helpers and smoke runners (CadQuery / build123d; FreeCAD if installed)."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from opencad.backends.local import (
    STEP_TOKEN_RE,
    STEP_ZERO_SNAP,
    canonicalize_step,
    classify_text,
    normalize_step_header,
)
from opencad.backends.registry import get
from opencad.geomcheck.brep import analyze_step
from opencad.io import sha256_file
from opencad.paths import REPO_ROOT

SMOKE = REPO_ROOT / "smoke"


def test_freecad_version_is_remembered_across_calls_and_processes(tmp_path, monkeypatch):
    from opencad.backends.freecad import FreeCADEngine

    exe = tmp_path / "freecadcmd"
    exe.write_text("#!/bin/sh\n")
    monkeypatch.setenv("OPENCAD_FREECADCMD", str(exe))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(FreeCADEngine, "_versions", {})
    calls: list[int] = []
    eng = FreeCADEngine()
    monkeypatch.setattr(eng, "preflight", lambda: calls.append(1) or {"version": "['1', '1', '0']"})
    assert eng.version() == eng.version() == "['1', '1', '0']" and calls == [1]
    monkeypatch.setattr(FreeCADEngine, "_versions", {})
    assert FreeCADEngine().version() == "['1', '1', '0']" and calls == [1], "a new process reads the disk cache"


def test_derived_parameters_may_be_formulas_but_stated_ones_stay_literal(tmp_path):
    from opencad.backends.pythonlang import parameter_values
    from opencad.contract import template_contract
    from opencad.schemas import Parameter

    c = template_contract()
    c.parameters.append(Parameter(name="innerWidth", value=52, unit="mm", provenance="derived", formula="width - 2 * thickness", tolerance=0.01))
    (tmp_path / "main.py").write_text("width = 60.0\nheight = 40\nthickness = 4.0\ninnerWidth = width - 2 * thickness\nresult = None\n")
    vals = parameter_values(tmp_path, c)
    assert vals["innerWidth"]["ok"] and vals["innerWidth"]["formula"] and vals["width"]["ok"]
    (tmp_path / "main.py").write_text("width = 50.0 + 10.0\nheight = 40\nthickness = 4.0\ninnerWidth = 52\nresult = None\n")
    vals = parameter_values(tmp_path, c)
    assert not vals["width"]["ok"] and vals["innerWidth"]["ok"]


def test_engine_version_reads_package_metadata_without_a_subprocess(monkeypatch):
    import importlib.metadata

    from opencad.backends import local

    eng = get("build123d").engine
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **k: pytest.fail("version() spawned a subprocess"))
    assert eng.version() == importlib.metadata.version("build123d")
    monkeypatch.setattr(eng, "id", "not-installed-engine")
    monkeypatch.setattr(eng, "preflight", lambda: {"version": "9.9"})
    assert eng.version() == "9.9"


def test_normalize_step_header_is_stable(tmp_path):
    a = tmp_path / "a.step"
    b = tmp_path / "b.step"
    body = "ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('x'),'2;1');\nFILE_NAME('p.step','2020-01-02T03:04:05',('me'),('me'),'cad','cad','');\nENDSEC;\nDATA;\nENDSEC;\nEND-ISO-10303-21;\n"
    a.write_text(body.replace("2020-01-02T03:04:05", "2021-02-03T04:05:06"))
    b.write_text(body)
    normalize_step_header(a, "p")
    normalize_step_header(b, "p")
    assert a.read_text() == b.read_text()
    assert sha256_file(a) == sha256_file(b)


# the two serialisations build123d fusion-12944-recon produced from one unchanged main.py (investigation 007): the
# boolean kept a different one of two coincident vertices, so a coordinate came out `0.` in one export and
# `1.183291357832E-30` in the other; every other byte was identical
STEP_HEAD = (
    "ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('Open CASCADE Model'),'2;1');\n"
    "FILE_NAME('main.step','{ts}',('Open CASCADE'),('Open CASCADE'),'Open CASCADE STEP processor 7.9','Open CASCADE 7.9','Unknown');\n"
    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN {{ 1 0 10303 214 1 1 1 1 }}'));\nENDSEC;\nDATA;\n"
)
STEP_BODY = (
    "#1 = APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#2);\n"
    "#7 = PRODUCT('Open CASCADE STEP translator 7.9 1','Open CASCADE STEP translator 7.9 1','',(#8));\n"
    "#30 = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#28,'distance_accuracy_value','confusion accuracy');\n"
    "#1901 = CARTESIAN_POINT('',(0.,{y},18.));\n#1903 = CIRCLE('',#1904,18.);\n"
    "#1905 = CARTESIAN_POINT('',(0.,{y},0.));\n#1906 = DIRECTION('',({nx},1.,{nz}));\n"
    "#1907 = DIRECTION('',(0.7071067811865,0.,-0.7071067811865));\n"
    "#1950 = CARTESIAN_POINT('',(-63.3505,126.701,-1.879707962792E-04));\n#1951 = B_SPLINE_CURVE_WITH_KNOTS('',3,(#1,#2),.UNSPECIFIED.,.F.,.F.,(4,4),(0.,1.),.PIECEWISE_BEZIER_KNOTS.);\n"
    "ENDSEC;\nEND-ISO-10303-21;\n"
)


def test_canonicalize_step_snaps_kernel_noise(tmp_path):
    a = tmp_path / "a.step"
    b = tmp_path / "b.step"
    a.write_text(
        STEP_HEAD.format(ts="2026-09-20T05:24:41")
        + STEP_BODY.format(y="1.183291357832E-30", nx="-0.", nz="2.22044604925E-16")
    )
    b.write_text(
        STEP_HEAD.format(ts="2026-09-20T05:26:03") + STEP_BODY.format(y="0.", nx="0.", nz="-7.084691224754E-19")
    )
    canonicalize_step(a, "main")
    canonicalize_step(b, "main")
    assert a.read_text() == b.read_text() and sha256_file(a) == sha256_file(b)
    text = a.read_text()
    assert "(0.,0.,18.)" in text and "(0.,0.,0.)" in text and "DIRECTION('',(0.,1.,0.))" in text
    # every real that carries geometry, tolerance or knots is kept verbatim; strings, integers and ids are never touched
    for kept in (
        "LENGTH_MEASURE(1.E-07)",
        "(-63.3505,126.701,-1.879707962792E-04)",
        "(0.7071067811865,0.,-0.7071067811865)",
        "(4,4),(0.,1.)",
        "2000,#2",
        "#1901 = ",
        "translator 7.9 1",
        "FILE_NAME('main.step','1970-01-01T00:00:00'",
    ):
        assert kept in text, kept
    assert not [t for t in STEP_TOKEN_RE.findall(text) if t and t != "0." and abs(float(t)) < STEP_ZERO_SNAP]
    canonicalize_step(a, "main")  # idempotent
    assert a.read_text() == text


def test_classify_kernel_and_guard():
    assert classify_text("StdFail_NotDone: BRep_API: command not done") == "kernel"
    assert classify_text("AssertionError: infeasible: thickness") == "program"
    assert classify_text("IndentationError: unexpected indent (main.py, line 252)") == "program"
    assert classify_text("timed out", code=124) == "timeout"


def _twice(backend: str, entry: Path, tmp_path: Path) -> None:
    eng = get(backend).engine
    first = tmp_path / "a"
    second = tmp_path / "b"
    pa = eng.export(entry, first, "step")[0]
    pb = eng.export(entry, second, "step")[0]
    assert sha256_file(pa) == sha256_file(pb)


def test_cadquery_smoke_coupon_and_guard(tmp_path):
    entry = SMOKE / "cadquery" / "coupon" / "main.py"
    _twice("cadquery", entry, tmp_path)
    lang = get("cadquery").language
    from opencad.contract import load_contract

    c = load_contract(REPO_ROOT / "designs" / "coupon")
    work = tmp_path / "part"
    work.mkdir()
    dest = work / "main.py"
    dest.write_text(entry.read_text())
    lang.rewrite_parameter(work, "thickness", 0)
    with pytest.raises(Exception) as ei:
        get("cadquery").engine.analyze(dest)
    assert getattr(ei.value, "kind", None) == "program"
    assert (
        getattr(ei.value, "guard", False) or "infeasible" in str(ei.value).lower() or "assert" in str(ei.value).lower()
    )


def test_cadquery_smoke_bracket(tmp_path):
    _twice("cadquery", SMOKE / "cadquery" / "bracket" / "main.py", tmp_path)


def test_cadquery_quick_coupon(tmp_path, monkeypatch):
    from opencad.backends.registry import set_backend
    from opencad.quick import run

    monkeypatch.setenv("OPENCAD_BACKEND", "cadquery")
    set_backend("cadquery")
    monkeypatch.setenv("OPENCAD_ENGINE_CACHE", str(tmp_path / "cache"))
    rc = run(SMOKE / "cadquery" / "coupon" / "main.py", REPO_ROOT / "designs" / "coupon" / "contract.yaml")
    assert rc == 0


def test_build123d_smoke_coupon_and_bracket(tmp_path):
    _twice("build123d", SMOKE / "build123d" / "coupon" / "main.py", tmp_path / "c")
    _twice("build123d", SMOKE / "build123d" / "bracket" / "main.py", tmp_path / "b")


# a plate with a bore rotated into it: Rot(-90°) leaves cos(90°) ULP noise (`2.2E-16`, `-0.`, `1.9E-31`) in the raw
# writer output, the class of value whose exact form depends on OpenCascade's per-process map order
B3D_BORED_PLATE = """from build123d import Align, Box, Cylinder, Location, Rot

plateSide = 20.0
holeDiameter = 6.0
plateThickness = 8.0
assert holeDiameter < plateThickness, "infeasible: bore breaks through the plate faces"

plate = Box(plateSide, plateSide, plateThickness, align=(Align.CENTER, Align.CENTER, Align.MIN))
bore = Location((0, -plateSide / 2 - 1.0, plateThickness / 2)) * Rot(-90, 0, 0) * Cylinder(holeDiameter / 2, plateSide + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
result = plate - bore
"""

CQ_BORED_PLATE = """import cadquery as cq

plateSide = 20.0
holeDiameter = 6.0
plateThickness = 8.0
assert holeDiameter < plateThickness, "infeasible: bore breaks through the plate faces"

plate = cq.Workplane("XY").box(plateSide, plateSide, plateThickness, centered=(True, True, False))
bore = cq.Workplane("XZ", origin=(0, plateSide / 2 + 1.0, plateThickness / 2)).circle(holeDiameter / 2).extrude(plateSide + 2.0)
result = plate.cut(bore)
"""


def _noise_tokens(step: Path) -> list[str]:
    return [t for t in STEP_TOKEN_RE.findall(step.read_text()) if t and t != "0." and abs(float(t)) < STEP_ZERO_SNAP]


@pytest.mark.parametrize("backend,src", [("build123d", B3D_BORED_PLATE), ("cadquery", CQ_BORED_PLATE)])
def test_deterministic_export_hashes_equal_despite_writer_noise(backend, src, tmp_path):
    entry = tmp_path / backend / "main.py"
    entry.parent.mkdir()
    entry.write_text(src)
    eng = get(backend).engine
    raw = eng.export(entry, tmp_path / "raw", "step", deterministic=False)[0]
    assert _noise_tokens(raw), "fixture no longer exercises sub-tolerance writer noise"
    a = eng.export(entry, tmp_path / "a", "step")[0]
    b = eng.export(entry, tmp_path / "b", "step")[0]
    assert sha256_file(a) == sha256_file(b) != sha256_file(raw)
    assert not _noise_tokens(a)
    canon = tmp_path / "canon.step"
    canon.write_bytes(raw.read_bytes())
    assert sha256_file(canonicalize_step(canon, "main")) == sha256_file(
        a
    )  # the deterministic path is exactly the canonical form
    _same_solid(raw, a)  # snapping sub-1e-9 reals moves nothing OpenCascade can measure
    assert analyze_step(a)["volume"] == pytest.approx(20.0**2 * 8.0 - math.pi * 3.0**2 * 20.0, rel=1e-9)


def _same_solid(a: Path, b: Path) -> None:
    from opencad.geomcheck.brep import analyze_step

    aa, bb = analyze_step(a), analyze_step(b)
    for key in ("volume", "surface_area"):
        assert abs(aa[key] - bb[key]) <= 1e-6 * max(1.0, abs(aa[key]))
    for key in ("bbox_min", "bbox_max", "center_of_mass"):
        assert all(abs(x - y) <= 1e-6 for x, y in zip(aa[key], bb[key]))


# a decomposed part as the decompose stage lays it out: params.py, datum.py, one `apply(body)` module, and the entry
PARAMS_PY = "plateWidth = 60.0\nplateDepth = 40.0\nplateThickness = 4.0\nholeDiameter = 6.0\n"
DECOMPOSED = {
    "cadquery": {
        "datum.py": "import cadquery as cq\nfrom params import plateDepth, plateThickness, plateWidth\n\n"
        'datum = cq.Workplane("XY").box(plateWidth, plateDepth, plateThickness, centered=(False, False, False))\n',
        "holes.py": "import cadquery as cq\nfrom params import holeDiameter, plateDepth, plateThickness, plateWidth\n\n\n"
        "def apply(body):\n"
        '    tool = cq.Workplane("XY", origin=(plateWidth / 2, plateDepth / 2, -0.02)).circle(holeDiameter / 2).extrude(plateThickness + 0.04)\n'
        "    return body.cut(tool, clean=True)\n",
    },
    "build123d": {
        "datum.py": "from build123d import Align, Box\nfrom params import plateDepth, plateThickness, plateWidth\n\n"
        "datum = Box(plateWidth, plateDepth, plateThickness, align=(Align.MIN, Align.MIN, Align.MIN))\n",
        "holes.py": "from build123d import Align, Cylinder, Pos\nfrom params import holeDiameter, plateDepth, plateThickness, plateWidth\n\n\n"
        "def apply(body):\n"
        "    tool = Pos(plateWidth / 2, plateDepth / 2, -0.02) * Cylinder(holeDiameter / 2, plateThickness + 0.04, align=(Align.CENTER, Align.CENTER, Align.MIN))\n"
        "    return body - tool\n",
    },
}
MAIN_PY = "from datum import datum\nfrom holes import apply as apply_holes\n\nresult = apply_holes(datum)\n"


@pytest.mark.parametrize("backend", ["cadquery", "build123d"])
def test_python_runner_imports_sibling_modules(backend, tmp_path):
    """`python -I` strips the script directory: the runner must put the entry's directory on sys.path so a decomposed
    part (`from params import ...`, `from datum import datum`) executes, from the part dir and from a scratch main elsewhere."""
    from opencad.contract import template_contract

    part = tmp_path / "parts" / backend / "demo"
    part.mkdir(parents=True)
    (part / "params.py").write_text(PARAMS_PY)
    for name, src in DECOMPOSED[backend].items():
        (part / name).write_text(src)
    (part / "main.py").write_text(MAIN_PY)
    expected = 60.0 * 40.0 * 4.0 - math.pi * 3.0**2 * 4.0
    be = get(backend)
    assert be.engine.analyze(part / "main.py")["volume_mm3"] == pytest.approx(expected, rel=1e-6)
    scratch = tmp_path / "results" / backend / "demo" / "decompose" / "holes"
    scratch.mkdir(parents=True)
    (scratch / "main.py").write_text(
        f"import sys\n\nsys.path.insert(0, {str(part)!r})\nfrom datum import datum  # noqa: E402\nfrom holes import apply as apply_holes  # noqa: E402\n\nresult = apply_holes(datum)\n"
    )
    assert be.engine.analyze(scratch / "main.py")["volume_mm3"] == pytest.approx(expected, rel=1e-6)
    checked = be.language.check(part, template_contract())
    assert (
        checked["hygiene"]["forbidden_imports"] == [] and checked["hygiene"]["dialect_ok"] and checked["lint"]["ok"]
    ), checked


def test_quick_tree_key_follows_referenced_sources(tmp_path, monkeypatch):
    """A decompose scratch main lives under results/ but imports parts/: the critic's cache key must change when a module changes."""
    from opencad import quick
    from opencad.backends.registry import set_backend

    monkeypatch.setenv("OPENCAD_BACKEND", "cadquery")
    set_backend("cadquery")
    root = tmp_path.resolve()
    monkeypatch.setattr(quick, "REPO_ROOT", root)
    part = root / "parts" / "cadquery" / "demo"
    part.mkdir(parents=True)
    (part / "params.py").write_text(PARAMS_PY)
    (part / "holes.py").write_text(DECOMPOSED["cadquery"]["holes.py"])
    scratch = root / "results" / "cadquery" / "demo" / "decompose" / "holes"
    scratch.mkdir(parents=True)
    entry = scratch / "main.py"
    entry.write_text(
        f"import sys\n\nsys.path.insert(0, {str(part)!r})\nfrom holes import apply  # noqa: E402\n\nresult = apply(None)\n"
    )
    assert sorted(p.name for p in quick.referenced_sources(entry, (".py",))) == ["holes.py", "params.py"]
    k1 = quick.tree_key(entry, "step")
    (part / "holes.py").write_text(DECOMPOSED["cadquery"]["holes.py"].replace("0.02", "0.03"))
    k2 = quick.tree_key(entry, "step")
    assert k1 != k2 and quick.tree_key(entry, "step") == k2
    # a second entry in the same directory (the composed critic beside the standalone scratch) is another part: its own key
    composed = scratch / "composed.py"
    composed.write_text(entry.read_text())
    assert quick.tree_key(composed, "step") != quick.tree_key(entry, "step")
    composed.unlink()
    # string literals that are not repository sources are ignored, the repository root itself included
    entry.write_text(f'x = "XY"\ny = "/"\nz = {str(root)!r}\nresult = None\n')
    assert quick.referenced_sources(entry, (".py",)) == []


def test_freecad_smoke_if_installed(tmp_path):
    from opencad.backends.freecad import freecadcmd
    from opencad.backends.local import run_script
    from opencad.io import sha256_file

    if not Path(freecadcmd()).exists():
        pytest.skip("freecadcmd not installed")
    entry = SMOKE / "freecad" / "coupon" / "main.py"
    eng = get("freecad").engine
    pa = eng.export(entry, tmp_path / "a", "step")[0]
    pb = eng.export(entry, tmp_path / "b", "step")[0]
    if sha256_file(pa) != sha256_file(pb):
        _same_solid(pa, pb)
    fcstd = next((tmp_path / "a").glob("*.FCStd"), None)
    assert fcstd is not None and fcstd.exists()
    br_a = eng.export(SMOKE / "freecad" / "bracket" / "main.py", tmp_path / "br-a", "step")[0]
    br_b = eng.export(SMOKE / "freecad" / "bracket" / "main.py", tmp_path / "br-b", "step")[0]
    if sha256_file(br_a) != sha256_file(br_b):
        _same_solid(br_a, br_b)
    check = (
        "import FreeCAD, sys; "
        f"d=FreeCAD.openDocument({str(fcstd)!r}); d.recompute(); "
        "bad=[o.Name for o in d.Objects if getattr(o,'TypeId','').startswith('PartDesign::') "
        "and hasattr(o,'isValid') and not o.isValid()]; "
        "print('ok' if not bad else bad); sys.exit(1 if bad else 0)"
    )
    row = run_script([freecadcmd(), "-c", check], backend_id="freecad", cwd=tmp_path)
    assert row["ok"], row.get("stderr") or row.get("stdout")


def test_stl_to_glb_is_metres_y_up(tmp_path):
    import numpy as np
    import trimesh

    from opencad.backends.local import stl_to_glb

    box = trimesh.creation.box(extents=[80.0, 50.0, 6.0])
    box.apply_translation([40.0, 25.0, 3.0])
    stl = tmp_path / "bracket.stl"
    box.export(str(stl))
    glb = tmp_path / "bracket.glb"
    stl_to_glb(stl, glb)
    mesh = trimesh.load(str(glb), force="mesh")
    assert np.allclose(mesh.bounds, [[0.0, 0.0, -0.05], [0.08, 0.006, 0.0]], atol=1e-9)
    assert mesh.volume > 0
    assert abs(mesh.volume - 80.0 * 50.0 * 6.0e-9) < 1e-12
    assert mesh.is_watertight
    scene = trimesh.load(str(glb), force="scene")
    assert "bracket" in scene.geometry or "bracket" in list(scene.graph.nodes)


def test_blockout_preflight_non_billing_is_pipeline_error(monkeypatch):
    from opencad.orchestrator import PipelineError
    from opencad.stages import blockout

    class _Eng:
        def preflight(self):
            return {"ok": False, "class": "unknown", "error": "freecadcmd not found"}

    class _Ctx:
        backend = type("B", (), {"engine": _Eng()})()

    with pytest.raises(PipelineError, match="preflight failed \\(unknown\\)"):
        blockout.run(_Ctx())

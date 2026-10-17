"""kcl-bisect: pipeline step discovery, single-step and prefix modes with a fake engine, caching, tooling stops."""

from __future__ import annotations

from pathlib import Path

import pytest

from opencad.backends.zoo import bisect
from opencad.backends.zoo import engine as zoo

KCL = """@settings(defaultLengthUnit = mm, kclVersion = 2.0)
w = 10
tool = extrude(sketch(on = XY) { region(circle(center = [0, 0], radius = 2)) }, length = 20)

part = extrude(sketch(on = XY) { region(rectangle(center = [0, 0], width = w, height = w)) }, length = 5)
  |> fillet(radius = 1, tags = [])
  |> subtract(tools = [tool])
  |> shell(thickness = 1, faces = [END])
"""


def test_pipeline_steps_are_found_with_chains():
    steps = bisect.pipeline_steps(KCL)
    assert [s["call"] for s in steps] == ["fillet", "subtract", "shell"] and [s["line"] for s in steps] == [6, 7, 8] and {s["chain"] for s in steps} == {0}


def _runner(bad_calls: set[str]):
    calls = []

    def run(kcl: Path):
        text = kcl.read_text()
        calls.append(kcl.name)
        active = [s["call"] for s in bisect.pipeline_steps(text)]
        failing = [c for c in active if c in bad_calls]
        return (not failing, "" if not failing else f"KCL execution failed: engine cannot {failing[0]}")

    run.calls = calls  # type: ignore[attr-defined]
    return run


def test_single_mode_names_the_step_whose_removal_fixes_the_file(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(bisect, "CACHE_DIR", tmp_path / "cache")
    src = tmp_path / "main.kcl"
    src.write_text(KCL)
    r = bisect.bisect(src, runner=_runner({"subtract"}))
    assert not r["ok"] and r["culprits"][0]["call"] == "subtract" and r["culprits"][0]["line"] == 7 and r["calls"] == 4
    assert "line 7" in bisect.format_report(r) and "subtract" in r["verdict"]
    assert not (tmp_path / ".bisect-main").exists(), "variants are cleaned up"
    again = bisect.bisect(src, runner=_runner({"subtract"}))
    assert again.get("cached") and again["culprits"][0]["line"] == 7


def test_prefix_mode_and_an_executing_file(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(bisect, "CACHE_DIR", tmp_path / "cache")
    src = tmp_path / "main.kcl"
    src.write_text(KCL)
    r = bisect.bisect(src, mode="prefix", runner=_runner({"shell"}))
    assert r["culprits"][0]["call"] == "shell" and r["calls"] == 2
    ok = bisect.bisect(src, runner=_runner(set()), use_cache=False)
    assert ok["ok"] and "executes" in ok["verdict"]


def test_tooling_failures_stop_the_bisect(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(bisect, "CACHE_DIR", tmp_path / "cache")
    src = tmp_path / "main.kcl"
    src.write_text(KCL)

    def credits(kcl: Path):
        raise zoo.ZooCreditsError("pay-as-you-go collection threshold")

    with pytest.raises(zoo.ZooError):
        bisect.bisect(src, runner=credits, use_cache=False)
    monkeypatch.setattr(bisect, "default_runner", lambda ledger: credits)
    assert bisect.main(src, no_cache=True) == 2

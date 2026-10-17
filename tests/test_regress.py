"""truth regress: drafts first, then every case x backend in parallel, numbered EVENT lines, per-backend verdicts."""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

from opencad.truth import regress

FAKE = r"""
import json, pathlib, sys
name, designs, design, fail = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3], sys.argv[4].split(",")
if name.startswith("draft-"):
    if name not in fail:
        (designs / design).mkdir(parents=True, exist_ok=True)
        (designs / design / "contract.yaml").write_text("id: x\n")
    print(json.dumps({"stage_reached": "published" if name not in fail else "draft-failed"}, indent=2))
    sys.exit(1 if name in fail else 0)
print("== worker turn pending ==")
print("NEXT " + json.dumps({"id": "001-model", "role": "model", "model": "grok-4.7-medium-fast"}))
verdict = "FAIL" if name in fail else "PASS"
gates = {"pass": 10, "fail": 1} if name + ":gates" in fail else {"pass": 11, "fail": 0}
entry = {"stage_reached": "scored", "pipeline": {"gates": gates}, "scorecard": {"verdict": verdict, "accuracy_score": 99.5}}
print(json.dumps(entry, indent=2))
sys.exit(0 if verdict == "PASS" else 1)
"""


def _session(
    tmp_path: Path,
    monkeypatch,
    *,
    fail: tuple[str, ...] = (),
    jobs: int = 10,
    reuse: bool = False,
    backends: tuple[str, ...] = ("cadquery", "freecad"),
    problems: tuple[str, ...] = (),
) -> tuple[int, str]:
    designs = tmp_path / "designs"
    monkeypatch.setattr(regress, "design_dir", lambda name: designs / name)
    monkeypatch.setattr(regress, "RESULTS_BASE", tmp_path / "results")
    monkeypatch.setattr(regress, "design_for", lambda case, arm: f"{case}-d")

    def command(lane: regress.Lane, arm: str, tag: str) -> list[str]:
        return [sys.executable, "-c", FAKE, lane.name, str(designs), lane.design, ",".join(fail)]

    out = io.StringIO()
    code = regress.run(
        ["a", "b"],
        "spec-and-views",
        list(backends),
        jobs=jobs,
        tag="t1",
        reuse_designs=reuse,
        command=command,
        poll_s=0.02,
        out=out,
        check=lambda cases, bes: (list(problems), ["on battery"]),
        report=lambda tag: tmp_path / f"{tag}.md",
    )
    return code, out.getvalue()


def _events(text: str) -> list[tuple[int, dict]]:
    return [(int(m.group(1)), json.loads(m.group(2))) for m in re.finditer(r"^EVENT#(\d+) (.*)$", text, re.MULTILINE)]


def test_drafts_then_every_run_with_numbered_events(tmp_path: Path, monkeypatch):
    code, text = _session(tmp_path, monkeypatch)
    assert code == 0, text
    events = _events(text)
    assert [k for k, _ in events] == list(range(1, len(events) + 1))
    nexts = [e for _, e in events if e["kind"] == "next"]
    assert sorted(e["lane"] for e in nexts) == ["a@cadquery", "a@freecad", "b@cadquery", "b@freecad"]
    assert all(e["order"]["model"] == "grok-4.7-medium-fast" for e in nexts)
    starts = re.findall(r"^== (\S+): started", text, re.MULTILINE)
    for case in ("a", "b"):
        draft_exit = next(k for k, e in events if e["lane"] == f"draft-{case}" and e["kind"] == "exit")
        first_next = min(k for k, e in events if e["lane"].startswith(f"{case}@"))
        assert draft_exit < first_next
        assert starts.index(f"{case}@freecad") < starts.index(f"{case}@cadquery"), "longest runs start first"
    assert "backend cadquery: PASS (2/2)" in text and "backend freecad: PASS (2/2)" in text
    assert "[freecad/a] == worker turn pending ==" in text and "| a@freecad | 0 | PASS | 11/11 | 99.5 |" in text
    assert "session wall" in text and (tmp_path / "results" / "_logs" / "t1" / "a@freecad.log").exists()
    assert "warning: on battery" in text and f"report {tmp_path / 't1.md'}" in text
    summary = json.loads((tmp_path / "results" / "_logs" / "t1" / "summary.json").read_text())
    assert {r["run"]: r["verdict"] for r in summary["runs"]}["draft-a"] == "published"


def test_a_failed_draft_or_gate_fails_the_backend(tmp_path: Path, monkeypatch):
    code, text = _session(tmp_path, monkeypatch, fail=("draft-b", "a@cadquery", "a@freecad:gates"), jobs=1)
    assert code == 1
    skipped = sorted(e["lane"] for _, e in _events(text) if e["kind"] == "skipped")
    assert skipped == ["b@cadquery", "b@freecad"]
    assert "backend cadquery: FAIL (0/2: a FAIL gates 11/11, b NOT RUN)" in text
    assert "backend freecad: FAIL (0/2: a PASS gates 10/11, b NOT RUN)" in text
    assert re.findall(r"^== (\S+): started", text, re.MULTILINE) == ["draft-a", "draft-b", "a@freecad", "a@cadquery"]


def test_a_failed_preflight_starts_nothing(tmp_path: Path, monkeypatch):
    code, text = _session(tmp_path, monkeypatch, problems=("cadquery: 1 pending worker orders",))
    assert code == 2 and "problem: cadquery: 1 pending worker orders" in text and "not started" in text
    assert "started pid" not in text and not (tmp_path / "results" / "_logs").exists()


def test_preflight_blocks_on_pending_orders_vaulted_truth_and_engines(tmp_path: Path, monkeypatch):
    from types import SimpleNamespace

    from opencad.backends import registry
    from opencad.truth import manifest, runner
    from opencad.worker import orders

    (tmp_path / "held" / "truth").mkdir(parents=True)
    monkeypatch.setattr(
        orders,
        "all_pending",
        lambda root: [SimpleNamespace(part="p", id="001-model")] if root.name == "cadquery" else [],
    )
    engines = {"cadquery": {"ok": True}, "freecad": {"ok": False, "error": "no freecadcmd"}}
    monkeypatch.setattr(
        registry, "get", lambda be: SimpleNamespace(engine=SimpleNamespace(preflight=lambda: engines[be]))
    )
    monkeypatch.setattr(runner, "live_holders", lambda case: ["123-1"] if case == "held" else [])
    monkeypatch.setattr(runner, "vault_dirs", lambda case: [tmp_path] if case == "stranded" else [])
    monkeypatch.setattr(manifest, "case_dir", lambda case: tmp_path / case)
    monkeypatch.setattr(regress, "_on_battery", lambda: True)
    monkeypatch.setenv("OPENCAD_MODEL", "inherit")
    problems, warnings = regress.preflight(["held", "stranded", "missing"], ["cadquery", "freecad"])
    assert problems == [
        "cadquery: 1 pending worker orders (p/001-model); finish them first (`opencad next --backend cadquery`)",
        "freecad: engine preflight failed: no freecadcmd",
        "held: a live run holds its truth",
        "stranded: truth is still vaulted by an interrupted run (`python -m opencad.truth restore stranded`)",
        "missing: truth/ is missing",
    ]
    assert any("OPENCAD_MODEL" in w for w in warnings) and any("battery" in w for w in warnings)


def test_a_draft_only_run_exits_0_once_published(tmp_path: Path, monkeypatch):
    import yaml

    from opencad.paths import TRUTH
    from opencad.truth import __main__ as tm
    from opencad.truth import runner
    from opencad.truth.manifest import CaseManifest

    raw = yaml.safe_load((TRUTH / "cases" / "bearing-housing" / "manifest.yaml").read_text())
    case = tmp_path / "cases" / "c4"
    case.mkdir(parents=True)
    (case / "manifest.yaml").write_text("x")
    monkeypatch.setattr(tm, "case_dir", lambda _cid: case)
    monkeypatch.setattr(tm, "load_manifest", lambda _cid: CaseManifest.model_validate(raw))
    argv = ["run", "c4", "--arm", "spec-and-views", "--stop-after", "draft"]
    monkeypatch.setattr(runner, "run_case", lambda *a, **k: {"stage_reached": "published"})
    assert tm.main(argv) == 0
    monkeypatch.setattr(runner, "run_case", lambda *a, **k: {"stage_reached": "draft-failed"})
    assert tm.main(argv) == 1


def test_reuse_designs_skips_published_drafts(tmp_path: Path, monkeypatch):
    for case in ("a", "b"):
        (tmp_path / "designs" / f"{case}-d").mkdir(parents=True)
        (tmp_path / "designs" / f"{case}-d" / "contract.yaml").write_text("id: x\n")
    code, text = _session(tmp_path, monkeypatch, reuse=True, backends=("cadquery",))
    assert code == 0 and "draft-" not in text


def test_a_machine_case_runs_without_a_draft_lane(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(regress, "machine_arm", lambda case, arm: (case == "a", "packet" if case == "a" else arm))
    code, text = _session(tmp_path, monkeypatch, backends=("build123d",))
    assert code == 0, text
    starts = re.findall(r"^== (\S+): started", text, re.MULTILINE)
    assert "draft-a" not in starts and "draft-b" in starts and "a@build123d" in starts
    machine = regress.Lane("a", "a-d", "build123d", machine=True, arm="packet")
    argv = regress.truth_command(machine, "spec-and-views", "t1")
    assert argv[argv.index("--arm") + 1] == "packet" and "--resume-from" not in argv and "--wait" not in argv


def test_a_machine_lanes_nested_next_lines_become_events(tmp_path: Path):
    log = tmp_path / "logs"
    log.mkdir()
    session = regress.Session(log, out=io.StringIO())
    lane = regress.Lane("m", "m", "build123d", machine=True)
    nested = "[build123d/m-part] NEXT " + json.dumps({"id": "002-model", "role": "model", "model": "grok-4.7-medium-fast"})
    lane.proc = SimpleNamespace(stdout=iter([nested + "\n", "plain line\n"]))
    session._pump(lane, log / "m.log")
    events = _events(session.out.getvalue())
    assert [e["order"]["id"] for _, e in events if e["kind"] == "next"] == ["002-model"]

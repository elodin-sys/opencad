"""Scorecards and attempts.yaml stay in the vault while any holder of the case is active."""

from __future__ import annotations

import json
import threading
from pathlib import Path

import yaml

from opencad.truth import runner


def _case(tmp_path: Path, monkeypatch, cid: str = "c3") -> Path:
    case = tmp_path / "cases" / cid
    (case / "truth").mkdir(parents=True)
    (case / "truth" / "ref.step").write_text("x")
    (case / "manifest.yaml").write_text(f"id: {cid}\n")
    (case / "scorecards").mkdir()
    (case / "scorecards" / "arm@cadquery-latest.json").write_text("{}")
    (case / "attempts.yaml").write_text("attempts: []\n")
    monkeypatch.setattr(runner, "case_dir", lambda _cid: case)
    monkeypatch.setattr(runner, "VAULT", tmp_path / "vault")
    return case


def test_held_case_hides_scorecards_and_attempts(tmp_path: Path, monkeypatch):
    case = _case(tmp_path, monkeypatch)
    with runner.Sequester("c3"):
        assert not (case / "scorecards").exists() and not (case / "attempts.yaml").exists()
        assert runner.case_file("c3", "scorecards") == tmp_path / "vault" / "c3" / "scorecards"
    assert (case / "scorecards" / "arm@cadquery-latest.json").exists() and (case / "attempts.yaml").exists()
    assert runner.case_file("c3", "scorecards") == case / "scorecards"


def test_card_scored_under_a_second_holder_waits_in_the_vault(tmp_path: Path, monkeypatch):
    case = _case(tmp_path, monkeypatch)
    a, b = runner.Sequester("c3"), runner.Sequester("c3")
    a.__enter__()
    b.__enter__()
    with runner.case_lock("c3"):
        (runner.case_file("c3", "scorecards") / "arm@freecad-latest.json").write_text("{}")
    a.__exit__(None, None, None)
    runner.log_attempt("c3", {"arm": "arm", "backend": "freecad"})
    assert not (case / "scorecards").exists() and not (case / "attempts.yaml").exists()
    b.__exit__(None, None, None)
    assert {p.name for p in (case / "scorecards").iterdir()} == {"arm@cadquery-latest.json", "arm@freecad-latest.json"}
    assert yaml.safe_load((case / "attempts.yaml").read_text())["attempts"] == [{"arm": "arm", "backend": "freecad"}]


def test_run_joins_a_case_only_a_live_holder_keeps_vaulted(tmp_path: Path, monkeypatch):
    from opencad.paths import TRUTH
    from opencad.truth import __main__ as tm
    from opencad.truth.manifest import CaseManifest

    case = _case(tmp_path, monkeypatch)
    (case / "manifest.yaml").write_text((TRUTH / "cases" / "bearing-housing" / "manifest.yaml").read_text())
    monkeypatch.setattr(tm, "case_dir", lambda _cid: case)
    monkeypatch.setattr(
        tm,
        "load_manifest",
        lambda _cid: CaseManifest.model_validate(yaml.safe_load((case / "manifest.yaml").read_text())),
    )
    monkeypatch.setattr(runner, "run_case", lambda *a, **k: {"scorecard": {"verdict": "PASS"}})
    with runner.Sequester("c3"):
        assert not (case / "manifest.yaml").exists() and len(runner.live_holders("c3")) == 1
        assert tm.main(["run", "c3", "--arm", "spec-and-views"]) == 0
        state = runner.vault_path("c3") / "holders.json"
        data = json.loads(state.read_text())
        data["active"].append("999999999-1")
        state.write_text(json.dumps(data))
    assert runner.live_holders("c3") == [] and not (case / "manifest.yaml").exists()
    assert tm.main(["run", "c3", "--arm", "spec-and-views"]) == 2


def test_concurrent_log_attempt_keeps_every_entry(tmp_path: Path, monkeypatch):
    case = _case(tmp_path, monkeypatch)

    def write(n: int) -> None:
        for i in range(10):
            runner.log_attempt("c3", {"writer": n, "i": i})

    threads = [threading.Thread(target=write, args=(n,)) for n in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(yaml.safe_load((case / "attempts.yaml").read_text())["attempts"]) == 60

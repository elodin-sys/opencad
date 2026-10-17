import json

from opencad.bakeoff import (
    ASSEMBLY_CASES,
    BAKEOFF_TAG,
    CANDIDATES,
    LADDER,
    TRUTH_CASE,
    cell,
    cell_meter,
    design_names,
    ladder_parts,
    next_cell,
    next_rung,
    run_argv,
    status,
    write_report,
)
from opencad.bakeoff.__main__ import child_env
import os
import time

from opencad.costing import begin_credits, credit_delta, ledger_totals, write_cell_cost


def test_design_names_include_prove_parts():
    names = design_names()
    assert "bracket" in names and "benchy" in names


def test_ladder_is_design_major():
    assert LADDER[:6] == ("bracket", "benchy", "bearing-housing", "enclosure-base", "coupon", "nasa-backstep-driver-seegmiller")
    ordered = ladder_parts(["chiral-keyplate", "coupon", "bracket"])
    assert ordered == ["bracket", "coupon", "chiral-keyplate"]
    nxt = next_cell(backends=("cadquery",), parts=["this-part-does-not-exist"])
    assert nxt is not None and nxt["part"] == "this-part-does-not-exist"
    rung = next_rung(backends=("cadquery", "build123d"), parts=["this-part-does-not-exist"])
    assert rung is not None and rung["part"] == "this-part-does-not-exist" and len(rung["commands"]) == 2


def test_status_and_next_have_expected_shape():
    rows = status(backends=CANDIDATES, parts=["bracket"])
    assert {r["backend"] for r in rows} == set(CANDIDATES)
    assert all("status" in r for r in rows)
    nxt = next_cell(backends=("cadquery",), parts=["bracket"])
    if nxt is not None:
        assert nxt["backend"] == "cadquery"
        assert nxt["part"] == "bracket"
        assert run_argv(nxt["backend"], nxt["part"])[1:4] == ["-m", "opencad", "blockout"] or "drive" in run_argv(
            nxt["backend"], nxt["part"]
        )


def test_truth_case_run_argv():
    cmd = run_argv("cadquery", "nasa-backstep-driver-seegmiller")
    assert cmd[2:4] == ["opencad.truth", "run"]
    assert "--no-decompose" in cmd and "--backend" in cmd
    assert TRUTH_CASE["nist-amb2022-01-bridge-mesh"] == ("nist-amb2022-01-bridge", "mesh-input")


def test_write_report(tmp_path):
    out = write_report(tmp_path / "report.md")
    text = out.read_text()
    assert "bracket" in text and "cadquery" in text
    assert "## Scorecards" in text and "## ECR" in text
    assert text.index("coupon") < text.index("chiral-keyplate")


def test_empty_cell_is_pending():
    c = cell("cadquery", "this-part-does-not-exist")
    assert c["status"] == "pending" and c["ok"] is False


def test_assembly_cases_on_ladder_and_run_argv():
    assert "fusion-01184-assembly" in LADDER
    assert LADDER[LADDER.index("fusion-16418-recon") + 1] == "fusion-01184-assembly"
    assert set(ASSEMBLY_CASES) <= set(LADDER)
    cmd = run_argv("cadquery", "fusion-01184-assembly")
    assert cmd[2:5] == ["opencad.truth", "assemble", "fusion-01184-assembly"]
    assert "--backend" in cmd and "cadquery" in cmd and "--parallel" in cmd
    c = cell("cadquery", "fusion-01184-assembly")
    assert c["status"] in ("pending", "pass", "fail") and c["ok"] == (c["status"] == "pass")  # reads the live results tree
    c2 = cell("no-such-backend", "fusion-01184-assembly")
    assert c2["status"] == "pending" and c2["ok"] is False


def test_zoo_brief_reads_the_doc_tree():
    import importlib.util

    from opencad.backends.zoo.rules import KCL_RULES, skills, skills_note

    paths = [p.name for p in skills()]
    assert paths == ["SKILL.md", "SKILL.md"]
    assert "kcl-docs" in skills_note() and "kcl-examples" in skills_note()
    assert "zoo kcl analyze" in KCL_RULES
    path = __import__("opencad").paths.CODEX_EXEC
    spec = importlib.util.spec_from_file_location("codex_exec_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert "read backends/zoo/kcl-docs" in mod.CONTRACT
    assert not hasattr(mod, "zoo_mcp_overrides")


def test_run_argv_pins_astra_and_the_bakeoff_tag():
    for backend in ("cadquery", "zoo"):
        cmd = run_argv(backend, "bracket")
        assert cmd[cmd.index("--worker") + 1] == "codex"
        assert cmd[cmd.index("--tag") + 1] == BAKEOFF_TAG
    env = child_env()
    assert env["OPENCAD_CODEX_NO_FALLBACK"] == "1"
    assert env["OPENCAD_CODEX_EFFORT"] == "max" and env["CODEX_SERVICE_TIER"] == "fast"


def test_cell_meter_and_report_include_tokens_usd_and_seconds(tmp_path, monkeypatch):
    from opencad import bakeoff

    results = tmp_path / "build123d" / "bracket"
    results.mkdir(parents=True)
    row = {
        "kind": "turn", "tag": BAKEOFF_TAG, "backend": "codex", "model": "gpt-6-astra", "role": "model",
        "seconds": 12, "tokens_input": 100, "tokens_cached": 40, "tokens_output": 10, "tokens_reasoning": 4,
        "usd": 1.5, "fallback_from": "codex",
    }
    (results / "telemetry.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    (results / "cost.json").write_text(json.dumps({"tag": BAKEOFF_TAG, "zoo_credits_delta": 3, "zoo_monetary_delta": 0.25}) + "\n", encoding="utf-8")
    monkeypatch.setattr(bakeoff, "results_dir", lambda part, backend=None: tmp_path / backend / part)
    meter = cell_meter("build123d", "bracket")
    assert meter["model"] == "gpt-6-astra" and meter["fallbacks"] == 1 and meter["codex_usd"] == 1.5
    assert meter["wall_s"] == 12 and meter["zoo_credits"] == 3
    out = write_report(tmp_path / "report.md")
    text = out.read_text()
    assert "tokens" in text and "USD" in text and "seconds" in text
    assert "Readiness: FAIL" in text and "build123d/bracket fallbacks=1" in text


def test_a_re_run_cell_is_metered_under_its_own_tag(tmp_path, monkeypatch):
    from opencad import bakeoff

    (tmp_path / "_bakeoff").mkdir()
    (tmp_path / "_bakeoff" / "cell-tags.json").write_text(json.dumps({"zoo/bracket": "rerun"}), encoding="utf-8")
    results = tmp_path / "zoo" / "bracket"
    results.mkdir(parents=True)
    row = {"kind": "turn", "tag": "rerun", "backend": "codex", "model": "gpt-6-astra", "seconds": 5, "tokens_input": 10, "usd": 2.25}
    (results / "telemetry.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    monkeypatch.setattr(bakeoff, "RESULTS_BASE", tmp_path)
    monkeypatch.setattr(bakeoff, "results_dir", lambda part, backend=None: tmp_path / backend / part)
    assert bakeoff.cell_tag("zoo", "bracket") == "rerun" and bakeoff.cell_tag("cadquery", "bracket") == BAKEOFF_TAG
    text = write_report(tmp_path / "report.md").read_text()
    assert "| bracket | zoo | gpt-6-astra |" in text and "2.25" in text and "Re-run cells: zoo/bracket `rerun`." in text


def test_published_log_admits_clean_four_backend_cells_once(tmp_path, monkeypatch):
    from opencad import bakeoff

    monkeypatch.setattr(bakeoff, "RESULTS_BASE", tmp_path)
    monkeypatch.setattr(bakeoff, "results_dir", lambda part, backend=None: tmp_path / backend / part)
    for part in ("bracket", "benchy"):
        for backend in (*CANDIDATES, "zoo"):
            d = tmp_path / backend / part
            d.mkdir(parents=True)
            gates = [{"id": "envelope", "ok": True}, {"id": "features", "ok": backend != "zoo"}]
            (d / "gate_feedback.json").write_text(json.dumps({"ok": backend != "zoo", "passed": ["envelope"], "failed": [] if backend != "zoo" else ["features"],
                                                              "not_applicable": [], "gates": gates}))
            mode = "thread-delta" if (part, backend) == ("benchy", "zoo") else "sum"
            row = {"kind": "turn", "tag": BAKEOFF_TAG, "model": "gpt-6-astra", "ts": "2026-10-16T01:00:00Z", "seconds": 10,
                   "tokens_input": 100, "usd": 1.0, "usage_mode": mode}
            (d / "telemetry.jsonl").write_text(json.dumps(row) + "\n")
    log = tmp_path / "_bakeoff" / "published.yaml"
    added = bakeoff.publish_entries(log, ["bracket", "benchy"])
    assert [e["part"] for e in added] == ["bracket"], "a re-billed (thread-delta) turn keeps benchy off the log"
    assert added[0]["note"] == "cadquery passes; build123d passes; freecad passes; zoo fails `features`."
    assert bakeoff.publish_entries(log, ["bracket", "benchy"]) == [], "the same tags are published once"
    import yaml

    assert len(yaml.safe_load(log.read_text())["entries"]) == 1


def test_credit_delta_and_cell_cost(tmp_path):
    assert credit_delta({"remaining_total": 100, "monetary_value": 5}, {"remaining_total": 40, "monetary_value": 4}) == {
        "zoo_credits_delta": 60, "zoo_monetary_delta": 1,
    }
    assert credit_delta(None, {"remaining_total": 1})["zoo_credits_delta"] is None
    begin_credits(tmp_path, {"known": True, "remaining_total": 10, "monetary_value": 2, "plan": "pro"}, reset=True)
    begin_credits(tmp_path, {"known": True, "remaining_total": 1, "monetary_value": 0, "plan": "pro"}, reset=False)
    assert json.loads((tmp_path / "credits-before.json").read_text())["remaining_total"] == 10
    (tmp_path / "worker").mkdir()
    (tmp_path / "worker" / "engine-ledger.jsonl").write_text(json.dumps({"seconds": 1.5}) + "\n", encoding="utf-8")
    (tmp_path / "verify.json").write_text(json.dumps({"engine_calls": [{"seconds": 2}]}), encoding="utf-8")
    assert ledger_totals(tmp_path) == (2, 3.5)
    cost = write_cell_cost(
        tmp_path, backend_id="zoo", fetch=False,
        billing_after={"known": True, "remaining_total": 7, "monetary_value": 1.5, "plan": "pro"},
    )
    assert cost["zoo_credits_delta"] == 3 and cost["zoo_monetary_delta"] == 0.5 and cost["engine_usd"] is None
    assert cost["calls"] == 2 and cost["seconds"] == 3.5
    local = write_cell_cost(tmp_path, backend_id="build123d", fetch=False)
    assert local["engine_usd"] == 0


def test_ledger_totals_ignore_files_from_before_the_cell(tmp_path):
    stale_dir = tmp_path / "worker" / "001-model"
    stale_dir.mkdir(parents=True)
    stale = stale_dir / "engine-ledger.jsonl"
    stale.write_text(json.dumps({"seconds": 9}) + "\n", encoding="utf-8")
    os.utime(stale, (time.time() - 500, time.time() - 500))
    (tmp_path / "cell-start.json").write_text(json.dumps({"tag": "", "ts": time.time() - 5}) + "\n", encoding="utf-8")
    fresh_dir = tmp_path / "blockout"
    fresh_dir.mkdir()
    (fresh_dir / "engine-ledger.jsonl").write_text(json.dumps({"seconds": 0.5}) + "\n", encoding="utf-8")
    assert ledger_totals(tmp_path) == (1, 0.5)


def test_default_report_rebuilds_the_site(monkeypatch, tmp_path):
    from opencad.bakeoff import __main__ as cli

    monkeypatch.setattr(cli, "write_report", lambda out=None: tmp_path / "report.md")
    seen = []

    def fake_build(repo, dest, **kwargs):
        seen.append(dest)
        return []

    monkeypatch.setattr("opencad.site.build.build_site", fake_build)
    assert cli.main(["report"]) == 0
    assert seen == [cli.REPO_ROOT / "_site"]
    assert cli.main(["report", "-o", str(tmp_path / "other.md")]) == 0
    assert seen == [cli.REPO_ROOT / "_site"]


def test_write_report_has_assemblies_section(tmp_path):
    out = write_report(tmp_path / "report.md")
    text = out.read_text()
    assert "## Assemblies" in text and "fusion-01184-assembly" in text
    assert "placement" in text or "pending" in text

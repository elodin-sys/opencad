import json
from types import SimpleNamespace

from opencad.codex import HEADER_RE, contract_digest, extract_block, format_event, parse_sections, sum_turn_usage, yaml_from_report
from opencad.worker.codex_backend import _load_usage
from opencad.worker.pricing import CARD_ID, cost_usd
from opencad.contract import template_contract
from opencad.initialize import draft_brief, schema_digest
from opencad.schemas import FaceSpec
from opencad.stages.plan import brief as plan_brief


def test_parse_sections_and_blocks():
    md = """intro text
## Result
Built the plate.

```yaml
name: plate
value: 3
```
## Files changed
- main.kcl
## Verification
volume 9600 vs 9600
## Open questions
none
"""
    s = parse_sections(md)
    assert set(s) == {"Result", "Files changed", "Verification", "Open questions"}
    assert "Built the plate." in s["Result"] and s["Open questions"] == "none"
    assert yaml_from_report(md) == {"name": "plate", "value": 3}
    assert extract_block("```kcl\na = 1\n```\n```kcl\nb = 2\n```", "kcl") == "b = 2"


def _turn(inp, cached, out, reasoning):
    return {"type": "turn.completed", "usage": {
        "input_tokens": inp, "cached_input_tokens": cached, "output_tokens": out, "reasoning_output_tokens": reasoning,
    }}


def test_sum_turn_usage_adds_separate_bills_and_keeps_a_running_total():
    summed = sum_turn_usage([_turn(100, 40, 10, 4), _turn(50, 0, 30, 1), {"type": "thread.started"}])
    assert summed["mode"] == "sum" and summed["turns"] == 2
    assert summed["input"] == 150 and summed["cached"] == 40 and summed["output"] == 40 and summed["reasoning"] == 5
    running = sum_turn_usage([_turn(100, 10, 10, 2), _turn(250, 80, 40, 9)])
    assert running["mode"] == "last" and running["input"] == 250 and running["output"] == 40 and running["reasoning"] == 9
    assert running["note"]
    assert sum_turn_usage([])["mode"] == "empty"


def test_price_card_bills_output_once_and_refuses_an_unknown_model():
    priced = cost_usd({"input": 1_000_000, "cached": 250_000, "output": 1_000, "reasoning": 400})
    assert priced["card"] == CARD_ID
    assert priced["usd"] == round(750_000 * 20 / 1_000_000 + 250_000 * 2 / 1_000_000 + 1_000 * 100 / 1_000_000, 6)
    assert cost_usd({"input": 0, "cached": 0, "output": 1000, "reasoning": 400})["usd"] == 0.1
    missing = cost_usd({"input": 10, "output": 10}, model="other")
    assert missing["usd"] is None and missing["reason"]


def test_load_usage_reads_events_when_the_wrapper_wrote_no_file(tmp_path):
    (tmp_path / "events.jsonl").write_text(
        "\n".join(json.dumps(e) for e in (_turn(100, 40, 10, 4), _turn(50, 0, 30, 1))),
        encoding="utf-8",
    )
    loaded = _load_usage(tmp_path)
    assert loaded["mode"] == "sum"
    assert loaded["usage"] == {"input": 150, "cached": 40, "output": 40, "reasoning": 5}
    assert json.loads((tmp_path / "usage.json").read_text())["usage"]["input"] == 150


def _token_count(ts, inp, cached, out, reasoning):
    return {"timestamp": ts, "type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {
        "input_tokens": inp, "cached_input_tokens": cached, "output_tokens": out, "reasoning_output_tokens": reasoning}}}}


def test_rollout_usage_bills_a_killed_exec_and_only_its_share_of_a_resumed_thread(tmp_path):
    from opencad.worker.codex_backend import _rollout_usage

    thread = "01a1-killed"
    rollout = tmp_path / "sessions" / "2026" / "10" / "15" / f"rollout-2026-10-15T01-00-00-{thread}.jsonl"
    rollout.parent.mkdir(parents=True)
    rollout.write_text("\n".join(json.dumps(e) for e in (
        {"timestamp": "2026-10-15T08:00:00.000Z", "type": "session_meta", "payload": {"id": thread}},
        _token_count("2026-10-15T08:00:10.000Z", 1000, 800, 50, 10),
        _token_count("2026-10-15T08:30:00.000Z", 5000, 4000, 300, 90),  # the earlier exec's last total
        _token_count("2026-10-15T09:00:30.000Z", 9000, 7500, 420, 120),
    )), encoding="utf-8")
    fresh = tmp_path / "fresh"
    fresh.mkdir()
    loaded = _rollout_usage(fresh, thread, sessions_root=tmp_path / "sessions")
    assert loaded == {"usage": {"input": 9000, "cached": 7500, "output": 420, "reasoning": 120}, "mode": "rollout"}
    assert json.loads((fresh / "usage.json").read_text())["mode"] == "rollout"
    resumed = tmp_path / "resumed"
    resumed.mkdir()
    (resumed / "settings.json").write_text(json.dumps({"started": "20261015T090000Z"}))
    assert _rollout_usage(resumed, thread, sessions_root=tmp_path / "sessions")["usage"] == {"input": 4000, "cached": 3500, "output": 120, "reasoning": 30}
    assert _rollout_usage(resumed, "no-such-thread", sessions_root=tmp_path / "sessions") is None


def test_a_resumed_exec_is_billed_its_share_not_the_thread_total(monkeypatch, tmp_path):
    from functools import partial

    from opencad.worker import codex_backend

    thread = "01a1-resumed"
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    (sessions / f"rollout-2026-10-15T01-00-00-{thread}.jsonl").write_text("\n".join(json.dumps(e) for e in (
        _token_count("2026-10-15T08:30:00.000Z", 5000, 4000, 300, 90),  # the earlier exec's last total
        _token_count("2026-10-15T09:00:30.000Z", 9000, 7500, 420, 120),
    )), encoding="utf-8")
    fake = tmp_path / "fake_codex_exec.py"
    fake.write_text(
        "import json, sys\n"
        "from pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "run = Path(args[args.index('--run-dir') + 1])\n"
        "run.mkdir(parents=True, exist_ok=True)\n"
        "sys.stdin.read()\n"
        "(run / 'settings.json').write_text(json.dumps({'started': '20261015T090000Z'}))\n"
        f"events = [{{'type': 'thread.started', 'thread_id': '{thread}'}}, {{'type': 'turn.completed', 'usage': {{'input_tokens': 9000, 'cached_input_tokens': 7500, 'output_tokens': 420}}}}]\n"
        "(run / 'events.jsonl').write_text('\\n'.join(json.dumps(e) for e in events) + '\\n')\n"
        "(run / 'result.md').write_text('## Result\\nfixed\\n')\n"
        f"print('thread_id={thread} exit=0 seconds=30 commands=1 usage=in:9000 cached:7500 out:420 reasoning:120')\n"
    )
    monkeypatch.setattr(codex_backend, "CODEX_EXEC", fake)
    monkeypatch.setattr(codex_backend, "_rollout_usage", partial(codex_backend._rollout_usage, sessions_root=sessions))
    r = codex_backend.dispatch("fix it", cd=tmp_path, run_dir=tmp_path / "round-2", resume=thread, timeout=60, echo=False)
    assert r.usage == {"input": 4000, "cached": 3500, "output": 120, "reasoning": 30}
    assert r.usage_mode == "rollout"


def test_codex_briefs_carry_an_absolute_deadline_before_the_kill():
    from opencad.worker.codex_backend import with_deadline

    text = with_deadline("Build it.", 1200, now=0.0)
    assert text.startswith("Build it.\n\nDeadline: finish by 00:18:00 UTC; the turn is killed 120 s later.")
    assert "00:00:00" not in with_deadline("x", 30, now=0.0) and "00:01:00 UTC" in with_deadline("x", 30, now=0.0)


def test_header_regex():
    line = "thread_id=01a0a38b exit=0 seconds=402 commands=29 usage=in:1180326 cached:1115264 out:11039 reasoning:5000"
    m = HEADER_RE.search(line)
    assert m and m.group(1) == "01a0a38b" and int(m.group(4)) == 29


def test_format_event_agent_and_command():
    assert format_event({"type": "thread.started", "thread_id": "abc"}) == "thread abc"
    assert (
        format_event({"type": "item.completed", "item": {"type": "agent_message", "text": "hello"}}) == "codex: hello"
    )
    assert (
        format_event({"type": "item.started", "item": {"type": "command_execution", "command": "zoo kcl lint x.kcl"}})
        == "$ zoo kcl lint x.kcl"
    )
    assert (
        format_event(
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "x",
                    "exit_code": 0,
                    "status": "completed",
                    "aggregated_output": "ok\n",
                },
            }
        )
        == "  ok completed  | ok"
    )


def test_contract_digest_lists_parameters():
    d = contract_digest(template_contract())
    assert "width = 60mm" in d and "section mid_z" in d and "Envelope" in d
    assert "edit_test" in d.lower() or "Edit tests" in d
    assert "width: delta 10mm" in d
    assert "volume_delta 1600" in d


def test_contract_digest_emits_face_mode_center_and_com_note():
    c = template_contract()
    c.acceptance.center_of_mass.note = "width/2, height/2, thickness/2"
    c.acceptance.faces.append(
        FaceSpec(name="tab_a", plane="z", at=4, normal="+", area=12.0, center=(10.0, 5.0), mode="one")
    )
    d = contract_digest(c)
    assert "mode one" in d and "center [10.0, 5.0]" in d
    assert "width/2, height/2, thickness/2" in d


def test_contract_digest_both_chords(tmp_path):
    ref = tmp_path / "reference"
    ref.mkdir()
    (ref / "profile.json").write_text(
        json.dumps(
            {
                "measurements": {
                    "chord": 52.9878,
                    "stagger_deg": -26.1865,
                    "landmark_chord": 52.2846,
                    "landmark_stagger_deg": -24.4009,
                }
            }
        )
    )
    d = contract_digest(template_contract(), tmp_path)
    assert "farthest-pair: 52.9878 mm at -26.1865 deg" in d
    assert "landmarks (LE–TE): 52.2846 mm at -24.4009 deg" in d
    assert "farthest-pair is not the documented stagger" in d


def test_draft_brief_table_center_and_probe_guidance(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENCAD_LEAN_TURNS", "0")
    (tmp_path / "reference").mkdir()
    text = draft_brief(tmp_path, "demo", "a table-driven airfoil blade for a cascade.", sources=[], images=[], notes="")
    assert "extrusion-length" in text
    assert "acceptance.faces[].center" in text
    assert "farther from any inferred wall" in text
    assert "Schema: read" in text and "PartContract:" not in text


def test_lean_draft_brief_inlines_schema_sources_and_check_ids(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENCAD_LEAN_TURNS", raising=False)
    sources = tmp_path / "sources"
    sources.mkdir()
    (sources / "spec.md").write_text("outer width 100 mm\n", encoding="utf-8")
    text = draft_brief(
        tmp_path,
        "demo",
        "an enclosure base for the regression pair.",
        sources=[{"path": "sources/spec.md", "sha256": "abc123456789def"}],
        images=[],
        checks=[("section", "section_posts_x38"), ("volume", "volume")],
    )
    assert "PartContract:" in text and "exemplar-contract.yaml" in text and "bracket/contract.yaml" not in text
    assert "Seeded template" not in text
    assert 'Literal["stated"' in text and 'Literal["hole", "pin"' in text
    assert "stat: p05" in text and "infeasible_deltas" in text and "between:" in text
    assert "outer width 100 mm" in text
    assert "- section `section_posts_x38`" in text and "- volume `volume`" in text
    assert "schemas.py" not in text
    assert "Do not open `src/opencad`" in text
    digest = schema_digest()
    assert 'Literal["stated"' in digest and 'Literal["hole", "pin"' in digest


def test_exemplar_contract_validates_and_lints():
    import yaml

    from opencad.contract import lint_contract
    from opencad.initialize import EXEMPLAR_CONTRACT
    from opencad.schemas import PartContract

    contract = PartContract.model_validate(yaml.safe_load(EXEMPLAR_CONTRACT.read_text(encoding="utf-8")))
    problems, warnings = lint_contract(contract)
    assert problems == [] and warnings == []
    kinds = {
        "volume",
        "surface_area",
        "center_of_mass",
        "sections",
        "faces",
        "cylinders",
        "planes",
        "dimensions",
        "solids",
        "thickness",
        "probes",
        "cylinder_counts",
        "symmetry",
        "blockout",
    }
    acceptance = contract.acceptance
    assert all(getattr(acceptance, kind) for kind in kinds)
    assert contract.parameters[0].edit_test.sweep is not None
    assert contract.parameters[0].edit_test.infeasible_deltas
    assert contract.interfaces[0].checks and contract.references and contract.open_questions


def test_plan_brief_names_dense_profile_idiom():
    from opencad.backends.registry import get

    ctx = SimpleNamespace(contract=template_contract(), design_dir=None, backend=get("zoo"))
    text = plan_brief(ctx)
    assert "Dense coordinate profiles" in text
    assert "KCL rules" in text

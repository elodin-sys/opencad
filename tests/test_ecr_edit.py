"""Change-request plumbing, sweep/infeasible edit schema, interface preservation, and network-stall detection."""

from __future__ import annotations

import json
import math
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from opencad import interfaces
from opencad.contract import lint_contract
from opencad.worker import codex_backend
from opencad.worker.result import WorkerResult
from opencad.paths import DESIGNS, TRUTH
from opencad.schemas import EditTest, PartContract
from opencad.stages import ecr as ecr_mod
from opencad.stages.ecr import apply_delta, load_request_and_delta

BASE = yaml.safe_load((DESIGNS / "_template" / "contract.yaml").read_text())


def test_apply_delta_replaces_by_key_and_tracks_changed_items():
    raw = yaml.safe_load(yaml.safe_dump(BASE))
    raw["acceptance"]["cylinders"] = [{"name": "h1", "point": [0, 0, 0], "direction": [0, 0, 1], "radius": 3.25, "kind": "hole"},
                                      {"name": "h2", "point": [10, 0, 0], "direction": [0, 0, 1], "radius": 1.7, "kind": "hole"}]
    delta = {"acceptance": {"cylinders": [{"name": "h1", "radius": 2.5, "length": 6.0}, {"name": "h3", "point": [5, 5, 0], "direction": [0, 0, 1], "radius": 1.0}]},
             "parameters": [{"name": "trapDiameter", "value": 5.0, "unit": "mm", "provenance": "stated", "tolerance": 0.01, "source": "ecr-1-request.md"}],
             "open_questions": ["ecr: confirm insert length"]}
    out, changed = apply_delta(raw, delta)
    cyl = {c["name"]: c for c in out["acceptance"]["cylinders"]}
    assert cyl["h1"]["radius"] == 2.5 and cyl["h1"]["length"] == 6.0 and cyl["h1"]["kind"] == "hole"
    assert cyl["h2"]["radius"] == 1.7 and "h3" in cyl
    assert changed == {"h1", "h3"}
    assert any(p["name"] == "trapDiameter" for p in out["parameters"]) and out["open_questions"][-1].startswith("ecr:")
    removed, _ = apply_delta(out, {"acceptance": {"cylinders": [{"name": "h2", "_remove": True}]}})
    assert [c["name"] for c in removed["acceptance"]["cylinders"]] == ["h1", "h3"]


def test_apply_delta_merges_multibody_sections_by_name():
    raw = yaml.safe_load(yaml.safe_dump(BASE))
    raw["acceptance"]["probes"] = [{"name": "a", "state": "void", "points": [[0, 0, 1]]}, {"name": "b", "state": "solid", "points": [[0, 0, -1]]}]
    raw["acceptance"]["hardware"] = [{"name": "board", "kind": "box", "min": [0, 0, 0], "max": [1, 1, 1]}, {"name": "plug", "kind": "box", "min": [2, 0, 0], "max": [3, 1, 1]}]
    raw["acceptance"]["cylinder_counts"] = [{"name": "pilots", "radius": 1.25, "expected": 8}]
    out, changed = apply_delta(raw, {"acceptance": {
        "probes": [{"name": "a", "points": [[0, 0, 11]]}],
        "hardware": [{"name": "board", "max": [1, 1, 11]}],
        "cylinder_counts": [{"name": "side", "radius": 1.6, "expected_min": 1, "region": [[0, 0, 0], [1, 1, 1]]}],
        "volume": None,
    }})
    probes = {p["name"]: p for p in out["acceptance"]["probes"]}
    assert probes["a"]["points"] == [[0, 0, 11]] and probes["a"]["state"] == "void" and "b" in probes  # partial entry merged, others kept
    assert {h["name"]: h["max"] for h in out["acceptance"]["hardware"]} == {"board": [1, 1, 11], "plug": [3, 1, 1]}
    assert [c["name"] for c in out["acceptance"]["cylinder_counts"]] == ["pilots", "side"]
    assert out["acceptance"]["volume"] is None and {"a", "board", "side"} <= changed


def test_edit_test_sweep_and_infeasible_schema():
    et = EditTest.model_validate({"delta": 2, "sweep": {"min": 10, "max": 20, "steps": 3}, "infeasible_deltas": [-50]})
    assert et.sweep.sequence() == [10, 15, 20] and et.infeasible_deltas == [-50]
    assert EditTest.model_validate({"delta": 1, "sweep": {"values": [1, 2, 3]}}).sweep.sequence() == [1, 2, 3]
    with pytest.raises(ValueError):
        EditTest.model_validate({"delta": 1, "sweep": {"min": 1}})


def test_driven_items_and_compare():
    raw = yaml.safe_load(yaml.safe_dump(BASE))
    raw["parameters"].append({"name": "trapDepth", "value": 9.8, "unit": "mm", "provenance": "stated", "tolerance": 0.01, "source": "sources/x.md"})
    raw["acceptance"]["cylinders"] = [{"name": "trap", "point": [0, 0, 0], "direction": [0, 1, 0], "radius": 3.25, "kind": "hole", "length": 9.8},
                                      {"name": "screw", "point": [10, 0, 0], "direction": [0, 1, 0], "radius": 1.7, "kind": "hole"}]
    raw["features"].append({"id": "trapFeat", "kind": "hole", "description": "trap", "parameters": ["trapDepth"], "verify": [{"method": "cylinder", "cylinder": "trap"}]})
    raw["interfaces"] = [{"name": "mating", "description": "d", "checks": ["trap", "screw"]}]
    c = PartContract.model_validate(raw)
    assert interfaces.driven_items(c, "trapDepth") == {"trap"}
    base = {"trap": {"kind": "cylinder", "ok": True, "center": [0, 4.9, 0], "radius": 3.25, "length": 9.8, "direction": [0, 1, 0]},
            "screw": {"kind": "cylinder", "ok": True, "center": [10, 7, 0], "radius": 1.7, "length": 14, "direction": [0, 1, 0]}}
    after = {"trap": {"kind": "cylinder", "ok": True, "center": [0, 3, 0], "radius": 3.25, "length": 6.0, "direction": [0, 1, 0]},
             "screw": {"kind": "cylinder", "ok": True, "center": [10.4, 7, 0], "radius": 1.7, "length": 14, "direction": [0, 1, 0]}}
    r = interfaces.compare(base, after, c, changed={"trap"})
    assert r["items"]["trap"]["ok"] and r["items"]["trap"]["changed_by_request"]
    assert not r["items"]["screw"]["ok"] and abs(r["items"]["screw"]["axis_shift"] - 0.4) < 1e-9 and not r["ok"]


def test_edit_mode_exempts_driven_items_from_their_original_values():
    """An edit test rewrites one parameter: the items that parameter drives must still exist but are not judged against the unedited contract."""
    raw = yaml.safe_load(yaml.safe_dump(BASE))
    raw["parameters"].append({"name": "boreDia", "value": 18.0, "unit": "mm", "provenance": "stated", "tolerance": 0.01, "source": "sources/x.md"})
    raw["acceptance"]["cylinders"] = [{"name": "bore", "point": [0, 0, 0], "direction": [0, 1, 0], "radius": 9.0, "kind": "hole"},
                                      {"name": "mount", "point": [50, 0, 0], "direction": [0, 1, 0], "radius": 5.0, "kind": "hole"}]
    raw["features"].append({"id": "boreFeat", "kind": "hole", "description": "bore", "parameters": ["boreDia"], "verify": [{"method": "cylinder", "cylinder": "bore"}]})
    raw["interfaces"] = [{"name": "mating", "description": "d", "checks": ["bore", "mount"]}]
    c = PartContract.model_validate(raw)
    base = {"bore": {"kind": "cylinder", "ok": True, "center": [0, 7.5, 0], "radius": 9.0, "length": 15, "direction": [0, 1, 0]},
            "mount": {"kind": "cylinder", "ok": True, "center": [50, 7.5, 0], "radius": 5.0, "length": 15, "direction": [0, 1, 0]}}
    # the bore grew to r=10 as the edit asked: it fails the unedited radius spec (ok False) but still exists
    after = {"bore": {"kind": "cylinder", "ok": False, "center": [0, 7.5, 0], "radius": 10.0, "length": 15, "direction": [0, 1, 0]},
             "mount": {"kind": "cylinder", "ok": True, "center": [50, 7.5, 0], "radius": 5.0, "length": 15, "direction": [0, 1, 0]}}
    ecr = interfaces.compare(base, after, c, changed={"bore"})
    assert not ecr["items"]["bore"]["ok"], "an ECR judges driven items by the revised contract"
    edit = interfaces.compare(base, after, c, changed={"bore"}, mode="edit")
    assert edit["ok"] and edit["items"]["bore"]["ok"] and edit["items"]["bore"]["after"]["radius"] == 10.0 and edit["items"]["mount"]["ok"]
    # an undriven bore whose length changed because the edited material around it grew keeps its axis and radius: preserved
    longer = {**after, "mount": {**after["mount"], "ok": False, "length": 17}}
    assert interfaces.compare(base, longer, c, changed={"bore"}, mode="edit")["items"]["mount"]["ok"]
    assert not interfaces.compare(base, longer, c, changed={"bore"})["items"]["mount"]["ok"], "the ECR mode still judges the contract length"
    shifted = {**after, "mount": {**after["mount"], "center": [50.4, 7.5, 0]}}
    assert not interfaces.compare(base, shifted, c, changed={"bore"}, mode="edit")["items"]["mount"]["ok"], "an undriven axis that moved is a failure in both modes"
    # an item that already failed at the baseline has nothing to preserve
    base_missing = {**base, "mount": {**base["mount"], "ok": False, "center": None}}
    assert interfaces.compare(base_missing, after, c, changed={"bore"}, mode="edit")["items"]["mount"]["note"].startswith("not present at the baseline")
    assert not interfaces.present("face", {"area": 0.0, "position": 3.0}) and interfaces.present("dimension", {"measured": 4.0}) and not interfaces.present("plane", {"found": 0})


def _pinned_pair() -> dict:
    """Template contract with two pinned cylinders, each behind its own must_not_change interface."""
    raw = yaml.safe_load(yaml.safe_dump(BASE))
    raw["acceptance"]["cylinders"] = [{"name": "trap", "point": [0, 0, 0], "direction": [0, 1, 0], "radius": 3.25, "kind": "hole"},
                                      {"name": "screw", "point": [10, 0, 0], "direction": [0, 1, 0], "radius": 1.7, "kind": "hole"}]
    raw["interfaces"] = [{"name": "mating", "description": "d", "checks": ["trap"]}, {"name": "lug", "description": "d", "checks": ["screw"]}]
    return raw


def test_compare_treats_removed_items_as_deleted_not_failed():
    """A change request that deletes a pinned item (`_remove`) puts it in `changed`; the revised contract no longer declares it,
    so nothing can be measured afterwards. That is the requested outcome, not a preservation failure (the ECR-3 retry brief
    asked Codex to restore the deleted corner fasteners because this read as 'moved')."""
    raw = _pinned_pair()
    base_c = PartContract.model_validate(raw)
    revised_raw, changed = apply_delta(raw, {"acceptance": {"cylinders": [{"name": "screw", "_remove": True}, {"name": "trap", "radius": 3.0}]},
                                             "interfaces": [{"name": "lug", "_remove": True}]})
    revised = PartContract.model_validate(revised_raw)
    assert changed == {"screw", "trap"} and interfaces.declared(revised) >= {"trap"} and "screw" not in interfaces.declared(revised)
    baseline = {"trap": {"kind": "cylinder", "ok": True, "center": [0, 4.9, 0], "radius": 3.25, "length": 9.8, "direction": [0, 1, 0]},
                "screw": {"kind": "cylinder", "ok": True, "center": [10, 7, 0], "radius": 1.7, "length": 14, "direction": [0, 1, 0]}}
    after = {"trap": {"kind": "cylinder", "ok": True, "center": [0, 4.9, 0], "radius": 3.0, "length": 9.8, "direction": [0, 1, 0]}}  # screw: no spec left to measure
    r = interfaces.compare(baseline, after, revised, changed)
    assert r["ok"] and r["preserved"] == []
    assert r["items"]["screw"]["ok"] and r["items"]["screw"]["note"].startswith("removed by the request")
    assert r["items"]["trap"]["ok"] and r["items"]["trap"]["note"].startswith("revised by the request")
    # a revised item that fails its new spec is still a failure
    assert not interfaces.compare(baseline, {"trap": {**after["trap"], "ok": False}}, revised, changed)["ok"]
    # un-pinning an interface without touching its item: nothing to preserve either
    revised2_raw, changed2 = apply_delta(raw, {"interfaces": [{"name": "lug", "_remove": True}]})
    r2 = interfaces.compare(baseline, {"trap": baseline["trap"]}, PartContract.model_validate(revised2_raw), changed2)
    assert changed2 == set() and r2["ok"] and r2["items"]["screw"]["note"].startswith("no longer pinned")
    # unchanged behaviour: a pinned item the request did not touch that disappears is a failure
    r3 = interfaces.compare(baseline, {"trap": baseline["trap"]}, base_c, set())
    assert not r3["ok"] and r3["items"]["screw"]["note"] == "not found or failing after the change"


def test_ecr_brief_lists_removals_probes_counts_and_parameters():
    """The work order must show what the request removed and every revised item kind (probes, counts, solids, parameters,
    features, interfaces), and must not list a removed item as an interface to preserve."""
    raw = yaml.safe_load(yaml.safe_dump(BASE))
    raw["parameters"].append({"name": "lugDia", "value": 3.0, "unit": "mm", "provenance": "stated", "tolerance": 0.01, "source": "sources/x.md"})
    raw["acceptance"]["cylinders"] = [{"name": "lug_hole", "point": [0, 0, 0], "direction": [0, 0, 1], "radius": 1.5, "kind": "hole"},
                                      {"name": "datum_bore", "point": [30, 20, 0], "direction": [0, 0, 1], "radius": 5.0, "kind": "hole"}]
    raw["acceptance"]["probes"] = [{"name": "lug_void", "state": "void", "points": [[0, 0, 2]]}, {"name": "keep_void", "state": "void", "points": [[30, 20, 2]]}]
    raw["features"].append({"id": "lugs", "kind": "hole", "description": "corner lug holes", "parameters": ["lugDia"], "verify": [{"method": "cylinder", "cylinder": "lug_hole"}]})
    raw["interfaces"] = [{"name": "lug_fit", "description": "lug", "checks": ["lug_hole"]}, {"name": "datum", "description": "bore", "checks": ["datum_bore"]}]
    base_c = PartContract.model_validate(raw)
    delta = {
        "parameters": [{"name": "lugDia", "_remove": True}, {"name": "sideX", "value": 50, "unit": "mm", "provenance": "stated", "tolerance": 0.01, "source": "request.md", "description": "side screw x"}],
        "acceptance": {"cylinders": [{"name": "lug_hole", "_remove": True}], "probes": [{"name": "lug_void", "_remove": True}, {"name": "keep_void", "points": [[30, 20, 3]]}],
                       "cylinder_counts": [{"name": "side_holes", "diameter": 3.2, "kind": "hole", "region": [[49.5, -20, -10], [50.5, -0.5, 60]], "expected_min": 1, "description": "side screw"}]},
        "features": [{"id": "lugs", "_remove": True}],
        "interfaces": [{"name": "lug_fit", "_remove": True}],
    }
    revised_raw, changed = apply_delta(raw, delta)
    revised = PartContract.model_validate(revised_raw)
    assert changed == {"lug_hole", "lug_void", "keep_void", "side_holes"}
    baseline = {"lug_hole": {"kind": "cylinder", "ok": True, "center": [0, 0, 2], "radius": 1.5, "length": 4, "direction": [0, 0, 1]},
                "datum_bore": {"kind": "cylinder", "ok": True, "center": [30, 20, 2], "radius": 5.0, "length": 4, "direction": [0, 0, 1]}}
    ctx = SimpleNamespace(name="plate", entry=Path("parts/plate/main.kcl"), contract=base_c,
                          backend=SimpleNamespace(language=SimpleNamespace(entry="main.kcl", rules=lambda: "RULES")))
    text = ecr_mod.brief(ctx, "move the lugs", revised, changed, baseline, "ecr9")
    revised_part, rest = text.split("## Removed by this request", 1)
    removed_part, preserved_part = rest.split("## Interfaces that must be preserved exactly", 1)
    assert "- parameter sideX: 50.0 mm (stated, tol 0.01) [new] side screw x" in revised_part
    assert "- probe keep_void: void at [[30.0, 20.0, 3.0]]" in revised_part
    assert "- cylinder count side_holes: hole, radius 1.6 (tol 0.05), axis centre inside [[49.5, -20.0, -10.0], [50.5, -0.5, 60.0]], at least 1 side screw" in revised_part
    assert "- parameter lugDia: 3.0 mm" in removed_part and "- feature lugs [removed]" in removed_part and "- interface lug_fit" in removed_part
    assert "- cylinder lug_hole: hole, radius 1.5" in removed_part and "- probe lug_void: void at [[0.0, 0.0, 2.0]]" in removed_part
    assert "lug_hole" not in preserved_part and "- cylinder datum_bore:" in preserved_part
    assert preserved_part.rstrip().endswith("RULES")


def test_rpi5_ecr3_delta_describes_the_side_fastener_layout():
    """The ECR-3 delta must leave no corner-fastener item behind and its areas, centres and edit deltas must follow from the
    parameters for the applied layout (corner posts removed above the floor plate, four 8 x 5.6 side bosses, lid over walls and
    flanges). The 2026-09-18 Zoo attempt (truth PASS 36/36) has to sit inside the revised tolerances."""
    base_raw = yaml.safe_load((DESIGNS / "rpi5-enclosure" / "contract.yaml").read_text())
    delta = yaml.safe_load((TRUTH / "cases" / "rpi5-enclosure-ecr3" / "inputs" / "contract-delta.yaml").read_text())
    revised_raw, changed = apply_delta(base_raw, delta)
    c = PartContract.model_validate(revised_raw)
    assert lint_contract(c)[0] == []
    ecr_dir = DESIGNS / "rpi5-enclosure" / "ecr" / "ecr3"
    assert yaml.safe_load((ecr_dir / "contract.yaml").read_text()) == revised_raw, "published ECR-3 contract is base + the truth delta"
    assert yaml.safe_load((ecr_dir / "delta.yaml").read_text()) == delta
    names = interfaces.declared(c) | {p.name for p in c.acceptance.probes} | {x.name for x in c.acceptance.cylinder_counts} | {i.name for i in c.interfaces} | {f.id for f in c.features}
    assert not any(n.startswith("corner_") or n.startswith("lid_fastener_") for n in names) and "rim_pilots_section" not in names
    assert "lidHoleDiameter" not in {p.name for p in c.parameters} and {"sideScrewXNear", "sideScrewXFar", "sideLidHoleDiameter"} <= {p.name for p in c.parameters}
    probes = {p.name: p for p in c.acceptance.probes}
    assert {"side_pilots_void", "lid_holes_void", "side_boss_material"} <= set(probes)
    assert all(pt[0] in (50.0, 75.0) and pt[1] in (-4.5, 60.5) for n in ("side_pilots_void", "lid_holes_void") for pt in probes[n].points)
    assert all(pt[0] not in (50.0, 75.0) for pt in probes["shell_material"].points), "the wall probe must not sit on a screw axis"
    p = {x.name: x.value for x in c.parameters}
    w, post, ec = p["wallThickness"], p["cornerPostWidth"], p["edgeClearance"]
    cav_x, cav_y = p["boardLength"] + 2 * ec, p["boardWidth"] + 2 * ec
    wall = (cav_x + 2 * w) * (cav_y + 2 * w)
    bosses = 4 * post * (post - w)
    ring = wall - cav_x * cav_y + bosses
    rb, rp, rl = p["standoffDiameter"] / 2, p["pilotDiameter"] / 2, p["sideLidHoleDiameter"] / 2
    sec = {s.id: s.expect.area for s in c.acceptance.sections}
    face = {f.name: f for f in c.acceptance.faces}
    assert sec["floor_section"] == pytest.approx(5844.4 + bosses) and face["floor_exterior"].area == pytest.approx(5844.4 + bosses)
    assert sec["pcb_level_section"] == pytest.approx(ring - 12 * w) and sec["all_ports_section"] == pytest.approx(ring - 96 * w)
    assert sec["standoff_section"] == pytest.approx(ring - 12 * w + 4 * math.pi * (rb**2 - rp**2))
    assert face["base_rim"].area == pytest.approx(ring - 96 * w - 4 * math.pi * rp**2)
    lid = wall + bosses - 4 * math.pi * rl**2
    assert sec["lid_section"] == pytest.approx(lid) and face["lid_underside"].area == pytest.approx(lid) and face["lid_exterior"].area == pytest.approx(lid)
    assert face["lid_underside"].center[0] == pytest.approx((wall * 42.5 + (bosses - 4 * math.pi * rl**2) * 62.5) / lid, abs=1e-5)
    assert face["floor_exterior"].center[0] == pytest.approx((5844.4 * 42.5 + bosses * 62.5) / (5844.4 + bosses), abs=1e-5)
    assert c.parameter("headroom").edit_test.expect.volume_delta == pytest.approx((ring - 96 * w) * 5)
    assert c.parameter("standoffHeight").edit_test.expect.volume_delta == pytest.approx(ring + 4 * math.pi * rb**2, abs=1e-5)
    # Zoo's applied STEP (results/zoo/rpi5-enclosure/ecr/ecr3, 0.15 mm corner reliefs: 3.51 mm2 less wall section)
    zoo = {"floor_section": 6023.6, "standoff_section": 957.4578675, "pcb_level_section": 856.33, "all_ports_section": 654.73, "lid_section": 5758.4700912}
    assert all(abs(v - sec[k]) <= sec[k] * 0.01 for k, v in zoo.items()) and abs(635.0950459 - face["base_rim"].area) <= face["base_rim"].area * 0.01
    assert abs(3273.65 - (ring - 96 * w) * 5) <= (ring - 96 * w) * 5 * 0.02 and abs(1005.8928 - (ring + 4 * math.pi * rb**2)) <= (ring + 4 * math.pi * rb**2) * 0.02


def test_sequester_hides_manifest_and_mutants(monkeypatch, tmp_path: Path):
    import shutil

    from opencad.paths import TRUTH
    from opencad.truth import runner

    case = TRUTH / "cases" / "_tmp-sequester-test"
    shutil.rmtree(case, ignore_errors=True)
    (case / "truth").mkdir(parents=True)
    (case / "truth" / "ref.step").write_text("x")
    (case / "manifest.yaml").write_text("id: _tmp-sequester-test\n")
    (case / "mutants.yaml").write_text("mutants: []\n")
    (case / "attempts.yaml").write_text("attempts: []\n")
    monkeypatch.setattr(runner, "VAULT", tmp_path / "vault")
    try:
        with runner.Sequester("_tmp-sequester-test") as s:
            assert not (case / "truth").exists() and not (case / "manifest.yaml").exists() and not (case / "mutants.yaml").exists()
            assert not (case / "attempts.yaml").exists() and (s.dst / "attempts.yaml").exists()
            assert (s.dst / "manifest.yaml").exists() and (s.dst / "truth" / "ref.step").exists()
        assert (case / "truth" / "ref.step").read_text() == "x" and (case / "manifest.yaml").exists() and (case / "mutants.yaml").exists()
        assert (case / "attempts.yaml").exists()
        assert not s.dst.exists()
    finally:
        shutil.rmtree(case, ignore_errors=True)


def test_network_stall_detection(tmp_path: Path):
    events = [{"type": "thread.started", "thread_id": "t1"}, {"type": "turn.started"}]
    events += [{"type": "error", "message": "Reconnecting... waiting for network (Connection failed: error sending request)"}] * 5
    (tmp_path / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events))
    st = codex_backend.network_stall(tmp_path)
    assert st["stalled"] and st["network_errors"] == 5 and not st["turn_completed"] and st["commands"] == 0
    events.append({"type": "turn.completed", "usage": {}})
    (tmp_path / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events))
    assert not codex_backend.network_stall(tmp_path)["stalled"]
    assert not codex_backend.network_stall(tmp_path / "nowhere")["stalled"]


def test_idle_watchdog_kills_a_silent_turn_and_continues_the_thread(monkeypatch, tmp_path: Path):
    """A wrapper that emits thread.started/turn.started and then sleeps forever is killed after idle_timeout; the thread is resumed once."""
    import sys

    fake = tmp_path / "fake_codex_exec.py"
    fake.write_text(
        "import json, sys, time\n"
        "from pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "run = Path(args[args.index('--run-dir') + 1])\n"
        "run.mkdir(parents=True, exist_ok=True)\n"
        "sys.stdin.read()\n"
        "if '--resume' in args:\n"
        "    (run / 'events.jsonl').write_text(json.dumps({'type': 'thread.started', 'thread_id': 't-hang'}) + '\\n' + json.dumps({'type': 'turn.completed', 'usage': {}}) + '\\n')\n"
        "    (run / 'result.md').write_text('## Result\\nrecovered\\n')\n"
        "    print('thread_id=t-hang exit=0 seconds=3 commands=1 usage=in:1 cached:0 out:1 reasoning:0')\n"
        "    sys.exit(0)\n"
        "(run / 'events.jsonl').write_text(json.dumps({'type': 'thread.started', 'thread_id': 't-hang'}) + '\\n' + json.dumps({'type': 'turn.started'}) + '\\n')\n"
        "time.sleep(600)\n"
    )
    monkeypatch.setattr(codex_backend, "CODEX_EXEC", fake)
    monkeypatch.setattr(codex_backend, "IDLE_TIMEOUT", 2.0)
    t0 = __import__("time").time()
    r = codex_backend.dispatch("do it", cd=tmp_path, run_dir=tmp_path / "round-1", timeout=60, echo=False, network_retries=1)
    assert __import__("time").time() - t0 < 60, "the hung turn must be killed by the idle watchdog, not the timeout"
    assert r.ok and r.sections["Result"] == "recovered" and r.thread_id == "t-hang"
    assert len(r.network_stalls) == 1 and r.network_stalls[0]["hung"] is True


def test_recovered_reconnect_does_not_fail_a_completed_turn(monkeypatch, tmp_path: Path):
    import subprocess

    run_dir = tmp_path / "round-1"
    run_dir.mkdir()
    evs = [{"type": "thread.started", "thread_id": "t9"}, {"type": "error", "message": "Reconnecting... 5/5 (stream disconnected before completion: failed to lookup address information)"},
           {"type": "item.completed", "item": {"type": "agent_message", "text": "## Result\nplanned"}}, {"type": "turn.completed", "usage": {}}]
    (run_dir / "events.jsonl").write_text("\n".join(json.dumps(e) for e in evs))
    (run_dir / "result.md").write_text("## Result\nplanned\n")

    class P:
        returncode = 0

        def communicate(self, input=None, timeout=None):
            return ("thread_id=t9 exit=0 seconds=10 commands=3 usage=in:1 cached:0 out:1 reasoning:0\nfailure={\"type\": \"error\", \"message\": \"Reconnecting... 5/5 (stream disconnected before completion: failed to lookup address information)\"}\n", "")

        def kill(self):
            pass

    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: P())
    r = codex_backend.dispatch("plan it", cd=tmp_path, run_dir=run_dir, timeout=10, echo=False)
    assert r.ok and r.failure == "" and r.summary()["network_recovered"] and r.sections["Result"] == "planned"


def test_dispatch_retries_a_network_stall(monkeypatch, tmp_path: Path):
    calls: list[dict] = []

    def fake_once(brief, *, cd, run_dir, images, read_only, resume, add_dirs, timeout, echo, idle_timeout=None, effort=None):
        calls.append({"brief": brief, "resume": resume, "run_dir": Path(run_dir).name})
        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        if len(calls) == 1:
            evs = [{"type": "thread.started", "thread_id": "t1"}] + [{"type": "error", "message": "Reconnecting... waiting for network"}] * 4
            (run_dir / "events.jsonl").write_text("\n".join(json.dumps(e) for e in evs))
            return WorkerResult("t1", 124, 7200.0, 0, {}, run_dir, "", failure="exit 124")
        (run_dir / "events.jsonl").write_text(json.dumps({"type": "turn.completed", "usage": {}}))
        return WorkerResult("t1", 0, 100.0, 3, {}, run_dir, "## Result\nok")

    monkeypatch.setattr(codex_backend, "_dispatch_once", fake_once)
    monkeypatch.setattr(codex_backend, "wait_for_network", lambda **kw: 12.0)
    r = codex_backend.dispatch("do the thing", cd=tmp_path, run_dir=tmp_path / "round-1", timeout=10, echo=False)
    assert r.ok and len(calls) == 2
    assert calls[1]["resume"] == "t1" and calls[1]["brief"] == codex_backend.NETWORK_CONTINUE and calls[1]["run_dir"] == "round-1-net1"
    assert len(r.network_stalls) == 1 and r.network_stalls[0]["waited_seconds"] == 12 and r.summary()["network_stalls"] == 1


def test_load_request_and_delta_before_label_dir_wipe(tmp_path: Path):
    import shutil

    label = tmp_path / "ecr" / "ecr4"
    label.mkdir(parents=True)
    (label / "request.md").write_text("# ECR-4\nlower the lid below headroom\n", encoding="utf-8")
    (label / "delta.yaml").write_text("parameters: []\n", encoding="utf-8")
    request, delta = load_request_and_delta(label / "request.md", label / "delta.yaml")
    shutil.rmtree(label)
    assert "lower the lid" in request and delta == {"parameters": []}
    (tmp_path / "outside.md").write_text("ok\n", encoding="utf-8")
    request2, delta2 = load_request_and_delta(tmp_path / "outside.md", None)
    assert request2 == "ok\n" and delta2 == {}

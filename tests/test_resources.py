"""Memory governance: the runner watchdog, memory-sized slots and pools, admission, lane caps and the lane watchdog."""

import io
import os
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from opencad import resources

GB = 1024**3
GROW = "import time\nb = []\nfor _ in range(40):\n    b.append(bytearray(20 * 1024 * 1024))\n    time.sleep(0.05)\ntime.sleep(1)\n"


@pytest.fixture
def isolated_slots(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENCAD_ENGINE_LOCK", str(tmp_path / "locks" / "engine.lock"))
    monkeypatch.setenv("OPENCAD_MEM_HEADROOM_GB", "0")


def test_watchdog_kills_a_runner_past_its_budget_and_records_the_peak(monkeypatch, tmp_path, isolated_slots):
    from opencad.backends.base import EngineError
    from opencad.backends.local import classify_text, raise_run, reset_ledger, run_script

    monkeypatch.setenv("OPENCAD_ENGINE_MEM_GB", "0.2")
    row = run_script([sys.executable, "-c", GROW], backend_id="build123d", cwd=tmp_path)
    reset_ledger("build123d")
    assert not row["ok"] and row["code"] == -9 and row["class"] == "memory" and row["oom_killed"]
    assert row["peak_rss"] > 0.2 * GB
    assert "exceeded the engine memory budget 0.2 GB" in row["stderr"]
    assert classify_text(row["stderr"], code=-9) == "memory", "the budget phrase outranks the bare SIGKILL code"
    with pytest.raises(EngineError) as e:
        raise_run(row, "build123d runner failed")
    assert e.value.kind == "memory"


def test_a_runner_under_its_budget_is_untouched(monkeypatch, tmp_path, isolated_slots):
    from opencad.backends.local import reset_ledger, run_script

    monkeypatch.setenv("OPENCAD_ENGINE_MEM_GB", "2")
    row = run_script([sys.executable, "-c", "import time; b = bytearray(60 * 1024 * 1024); time.sleep(0.6)"], backend_id="build123d", cwd=tmp_path)
    reset_ledger("build123d")
    assert row["ok"] and row["class"] == "ok" and not row["oom_killed"]
    assert row["peak_rss"] > 50 * 1024**2


def test_memory_wait_timeout_is_a_resource_refusal_not_a_model_failure(monkeypatch, tmp_path, isolated_slots):
    from opencad.backends.base import is_tooling
    from opencad.backends.local import reset_ledger, run_script

    monkeypatch.setattr(resources, "available", lambda: 0)
    monkeypatch.setenv("OPENCAD_MEM_WAIT_S", "0")
    row = run_script([sys.executable, "-c", "print('never runs')"], backend_id="build123d", cwd=tmp_path)
    reset_ledger("build123d")
    assert not row["ok"] and row["class"] == "resource" and "not started" in row["stderr"] and "never runs" not in row["stdout"]
    assert is_tooling("resource") and not is_tooling("memory")


def test_engine_slots_and_pools_follow_memory_and_an_explicit_count_wins(monkeypatch):
    from opencad.assembly.kinematics import kin_workers
    from opencad.backends.local import max_slots
    from opencad.geomcheck.gears import mesh_workers

    for name in ("OPENCAD_ENGINE_SLOTS", "OPENCAD_KIN_WORKERS", "OPENCAD_MESH_WORKERS", "OPENCAD_ENGINE_MEM_GB", "OPENCAD_MEM_HEADROOM_GB"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(os, "cpu_count", lambda: 12)
    monkeypatch.setattr(resources, "total", lambda: 64 * GB)
    assert resources.memory_slots() == 6 and max_slots() == 6 and kin_workers() == 6 and mesh_workers() == 6
    monkeypatch.setattr(resources, "total", lambda: 32 * GB)
    assert resources.memory_slots() == 2 and max_slots() == 2 and kin_workers() == 2 and resources.pool_workers(11) == 2
    monkeypatch.setattr(resources, "total", lambda: 8 * GB)
    assert resources.memory_slots() == 1, "a small machine still runs one engine process"
    monkeypatch.setenv("OPENCAD_ENGINE_SLOTS", "3")
    monkeypatch.setenv("OPENCAD_KIN_WORKERS", "5")
    assert max_slots() == 3 and kin_workers() == 5


class _Session:
    """Starts each lane as a short real process and records how many were alive when it started."""

    def __init__(self):
        self.lanes, self.alive_at_start, self.events, self.said = [], [], [], []

    def say(self, text):
        self.said.append(text)

    def event(self, lane, kind, **data):
        self.events.append((lane.design, kind, data))

    def start(self, lane, argv):
        import subprocess

        self.alive_at_start.append(sum(1 for x in self.lanes if x.proc.poll() is None))
        lane.proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.3)"])
        lane.pump = threading.Thread(target=lambda: None)
        lane.pump.start()
        lane.started = time.time()
        self.lanes.append(lane)


def _actx(root: Path, designs: list[str]):
    return SimpleNamespace(contract=SimpleNamespace(designs=lambda: designs), backend_id="build123d",
                           part_results=lambda d: root / d, handoff_step=lambda d: root / d / "handoff" / f"{d}.step")


def test_parts_run_caps_lanes_by_memory_and_waits_for_a_lane_reserve(monkeypatch, tmp_path):
    from opencad.assembly import parts

    monkeypatch.setattr(resources, "memory_slots", lambda: 1)
    s = _Session()
    parts.run(_actx(tmp_path, ["a", "b", "c"]), s, jobs=3)
    assert s.alive_at_start == [0, 0, 0] and any("1 lanes at once, not 3" in t for t in s.said)
    assert [e[1] for e in s.events] == ["exit", "exit", "exit"]

    monkeypatch.setattr(resources, "memory_slots", lambda: 3)
    monkeypatch.setattr(resources, "fits", lambda need: False)
    s = _Session()
    parts.run(_actx(tmp_path, ["a", "b", "c"]), s, jobs=3)
    assert s.alive_at_start == [0, 0, 0], "with no memory to spare a lane starts only when none is running"


def test_lane_watchdog_kills_a_lane_past_its_own_limit_and_names_the_reason(monkeypatch, tmp_path):
    from opencad.truth.regress import Lane, Session

    monkeypatch.setenv("OPENCAD_ENGINE_MEM_GB", "0.1")
    out = io.StringIO()
    session = Session(tmp_path / "logs", out)
    (tmp_path / "logs").mkdir()
    lane = Lane(case="p", design="p", backend="build123d")
    session.start(lane, [sys.executable, "-c", GROW])
    lane.proc.wait(timeout=30)
    lane.pump.join(timeout=5)
    assert lane.proc.returncode == -9 and lane.exit_reason() == {"reason": "memory"}
    assert "exceeded the lane limit 0.2 GB" in out.getvalue()
    calm = Lane(case="q", design="q", backend="build123d")
    session.start(calm, [sys.executable, "-c", "print('ok')"])
    calm.proc.wait(timeout=30)
    assert calm.proc.returncode == 0 and calm.exit_reason() == {}

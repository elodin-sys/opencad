"""Memory governance for the pipeline's CAD processes.

Engine runners (a model build, an export) start only while enough memory is free and are killed by a watchdog past their budget;
pool and lane counts follow the machine's memory, not its core count. macOS does not enforce RLIMIT_AS, so the watchdog is the
limit that holds there. Every CAD process is a descendant of the editor's agent shell, which is why an unbounded run shows up as
the editor holding the machine's memory."""

from __future__ import annotations

import os
import sys
import threading
import time
from collections.abc import Callable
from typing import Any, Self

import psutil

GB = 1024**3
POLL_S = 0.25
WAIT_NOTE_S = 60.0


class MemoryWait(RuntimeError):
    """Available memory stayed below a request for the whole wait."""


def _gb_env(name: str, default: float) -> int:
    try:
        value = float(os.environ.get(name) or default)
    except ValueError:
        value = default
    return int(value * GB)


def runner_budget() -> int:
    """Bytes one engine process may hold before the watchdog kills it (OPENCAD_ENGINE_MEM_GB, default 8)."""
    return _gb_env("OPENCAD_ENGINE_MEM_GB", 8)


def headroom() -> int:
    """Bytes kept free for the OS, the editor and the pipeline's own processes (OPENCAD_MEM_HEADROOM_GB, default 16)."""
    return _gb_env("OPENCAD_MEM_HEADROOM_GB", 16)


def lane_reserve() -> int:
    """Bytes that must be free before another part lane starts (OPENCAD_LANE_MEM_GB, default 4)."""
    return _gb_env("OPENCAD_LANE_MEM_GB", 4)


def lane_limit() -> int:
    """A lane's own RSS (its in-process OpenCascade work, not its engine runners) past which the lane is killed."""
    return 2 * runner_budget()


def total() -> int:
    return int(psutil.virtual_memory().total)


def available() -> int:
    return int(psutil.virtual_memory().available)


def memory_slots() -> int:
    """Engine processes that fit at their full budget beside the headroom; at least one."""
    return max(1, (total() - headroom()) // max(1, runner_budget()))


def pool_workers(default: int) -> int:
    return max(1, min(default, memory_slots()))


def fits(need: int) -> bool:
    """`need` bytes can start now and still leave half the headroom free."""
    return available() >= need + headroom() // 2


def gb(n: float) -> str:
    return f"{n / GB:.1f} GB"


def wait_for_memory(need: int, *, timeout: float | None = None, label: str = "engine") -> float:
    """Block until `need` bytes fit; returns the seconds waited. Raises MemoryWait after `timeout` (OPENCAD_MEM_WAIT_S, 1800)."""
    limit = float(os.environ.get("OPENCAD_MEM_WAIT_S") or 1800) if timeout is None else timeout
    t0 = time.time()
    noted = 0.0
    while not fits(need):
        now = time.time()
        if now - t0 >= limit:
            raise MemoryWait(f"{label} not started: available memory {gb(available())} stayed below {gb(need + headroom() // 2)} "
                             f"for {now - t0:.0f} s (OPENCAD_ENGINE_MEM_GB, OPENCAD_MEM_HEADROOM_GB)")
        if now - noted >= WAIT_NOTE_S:
            print(f"[resources] {label} waiting: available {gb(available())} < {gb(need + headroom() // 2)}", file=sys.stderr, flush=True)
            noted = now
        time.sleep(1.0)
    return time.time() - t0


class Watchdog:
    """Polls a process's RSS (with its descendants when `tree`) every POLL_S and SIGKILLs it past `limit` bytes. `peak` is the
    largest RSS seen and `killed` whether it fired; `on_kill(rss)` runs after the kill."""

    def __init__(self, pid: int, limit: int, *, tree: bool = True, on_kill: Callable[[int], Any] | None = None, interval: float = POLL_S):
        self.limit, self.tree, self.on_kill, self.interval = limit, tree, on_kill, interval
        self.peak = 0
        self.killed = False
        self.killed_rss = 0
        try:
            self._root: psutil.Process | None = psutil.Process(pid)  # held, so a reused pid is never measured or killed
        except psutil.Error:
            self._root = None
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, name=f"watchdog-{pid}", daemon=True)

    def start(self) -> Self:
        self._thread.start()
        return self

    def stop(self) -> None:
        self._stop.set()
        if self._thread.is_alive() and self._thread is not threading.current_thread():
            self._thread.join(timeout=self.interval + 2)

    def __enter__(self) -> Self:
        return self.start()

    def __exit__(self, *exc: object) -> None:
        self.stop()

    def _procs(self) -> list[psutil.Process]:
        root = self._root
        if root is None or not root.is_running():
            return []
        if not self.tree:
            return [root]
        try:
            return [root, *root.children(recursive=True)]
        except psutil.Error:
            return [root]

    def _loop(self) -> None:
        while not self._stop.is_set():
            procs = self._procs()
            if not procs:
                return
            rss = 0
            for p in procs:
                try:
                    rss += p.memory_info().rss
                except psutil.Error:
                    pass
            self.peak = max(self.peak, rss)
            if rss > self.limit:
                self.killed, self.killed_rss = True, rss
                for p in reversed(procs):
                    try:
                        p.kill()
                    except psutil.Error:
                        pass
                if self.on_kill is not None:
                    self.on_kill(rss)
                return
            self._stop.wait(self.interval)

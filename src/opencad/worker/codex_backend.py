"""Opt-in Codex backend: runs codex_exec.py (GPT-6 Astra) and detects an exhausted account budget.

Selected only with `--worker codex` / OPENCAD_WORKER=codex. Per-role effort and idle timeouts come
from worker.profiles; the wrapper's remaining settings (context window, compaction, service tier) are
passed as CODEX_* environment variables to codex_exec.py.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from opencad.paths import CODEX_EXEC, REPO_ROOT
from opencad.worker import state
from opencad.worker.result import WorkerResult

HEADER_RE = re.compile(r"thread_id=(\S+) exit=(\d+) seconds=(\d+) commands=(\d+) usage=in:(\d+) cached:(\d+) out:(\d+) reasoning:(\d+)")
NETWORK_RE = re.compile(r"waiting for network|stream disconnected|Connection failed|Connection reset|tls handshake", re.IGNORECASE)
NETWORK_HOST = ("api.openai.com", 443)
NETWORK_CONTINUE = ("The previous turn was cut short by a network outage on our side, not by anything you did. "
                    "Continue the same task from where you left off; every instruction and rule from the original brief still applies. "
                    "Finish with the usual ## Result / ## Files changed / ## Verification / ## Open questions report.")
EXHAUSTION_RE = re.compile(r"usage limit|rate[ _-]?limit|too many requests|\b429\b|insufficient[_ ](quota|credits|funds)|out of credits|"
                           r"quota exceeded|spend (cap|limit)|billing|plan limit|usage_limit_reached|hit your (weekly|usage)", re.IGNORECASE)

IDLE_TIMEOUT = 300.0  # seconds without a Codex event before a turn is declared hung (a 10-minute single generation is a max-effort artefact)
NETWORK_MAX_WAIT = 900.0  # seconds to wait for connectivity before the attempt is parked as network-stalled
DEADLINE_MARGIN_S = 120.0
CODEX_SESSIONS = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"
MODEL = "gpt-6-astra"


def network_stall(run_dir: Path) -> dict[str, Any]:
    """Did this turn die waiting for the network? Counts network error events and whether the turn ever completed."""
    p = Path(run_dir) / "events.jsonl"
    errors, completed, commands, last_error = 0, False, 0, ""
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = ev.get("type")
            if kind == "turn.completed":
                completed = True
            elif kind in ("error", "turn.failed"):
                msg = str(ev.get("error") or ev.get("message") or ev)
                if NETWORK_RE.search(msg):
                    errors += 1
                    last_error = msg[:200]
            elif kind == "item.completed" and (ev.get("item") or {}).get("type") == "command_execution":
                commands += 1
    return {"network_errors": errors, "turn_completed": completed, "commands": commands, "last_error": last_error,
            "stalled": errors >= 3 and not completed}


def wait_for_network(max_wait: float = NETWORK_MAX_WAIT, poll: float = 30.0, host: tuple[str, int] = NETWORK_HOST) -> float:
    """Block until a TCP connection to the API host succeeds (or max_wait elapses). Returns seconds waited."""
    import socket

    t0 = time.time()
    while True:
        try:
            with socket.create_connection(host, timeout=5):
                return time.time() - t0
        except OSError:
            waited = time.time() - t0
            if waited >= max_wait:
                return waited
            if int(waited) % 300 < poll:
                print(f"[codex] network down for {waited / 60:.0f} min; waiting", flush=True)
            time.sleep(poll)


# --- account budget -----------------------------------------------------------------------

def _tail_lines(path: Path, max_bytes: int = 4 << 20) -> list[str]:
    size = path.stat().st_size
    with path.open("rb") as f:
        if size > max_bytes:
            f.seek(size - max_bytes)
            f.readline()  # drop the partial first line
        return f.read().decode("utf-8", errors="replace").splitlines()


def rate_limits(sessions_root: Path = CODEX_SESSIONS) -> dict[str, Any] | None:
    """The last `token_count.rate_limits` block Codex recorded, from the newest session rollout."""
    if not sessions_root.exists():
        return None
    files = [p for p in sessions_root.rglob("rollout-*.jsonl") if p.is_file()]
    if not files:
        return None
    newest = max(files, key=lambda p: p.stat().st_mtime)
    for line in reversed(_tail_lines(newest)):
        if '"token_count"' not in line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        rl = ((e.get("payload") or {}).get("rate_limits"))
        if rl:
            return {**rl, "session": str(newest), "recorded_at": e.get("timestamp")}
    return None


def budget(sessions_root: Path = CODEX_SESSIONS) -> dict[str, Any]:
    """Is the Codex account able to run a turn? Exhausted = a hard limit reached, a spend cap, or no credits left at 100 % usage."""
    rl = rate_limits(sessions_root)
    if not rl:
        return {"known": False, "exhausted": False, "reason": "no Codex session with rate-limit data"}
    prim = (rl.get("primary") or {}).get("used_percent") or 0
    sec = (rl.get("secondary") or {}).get("used_percent") or 0
    credits = rl.get("credits") or {}
    has_credits = credits.get("has_credits")
    reached = rl.get("rate_limit_reached_type")
    spend = rl.get("spend_control_reached")
    exhausted = bool(reached) or bool(spend) or (has_credits is False and (prim >= 100 or sec >= 100))
    reason = (f"rate_limit_reached_type={reached}" if reached else "spend control reached" if spend
              else f"no credits and usage primary {prim:.0f} % / secondary {sec:.0f} %" if exhausted else "")
    resets = (rl.get("secondary") or {}).get("resets_at") if sec >= 100 else (rl.get("primary") or {}).get("resets_at")
    return {"known": True, "exhausted": exhausted, "reason": reason, "primary_used": prim, "secondary_used": sec, "has_credits": has_credits,
            "spend_control_reached": spend, "rate_limit_reached_type": reached, "resets_at": resets, "plan_type": rl.get("plan_type"),
            "session": rl.get("session"), "recorded_at": rl.get("recorded_at")}


def exhausted_state() -> tuple[bool, dict[str, Any]]:
    """Campaign state first (a marked exhaustion sticks until its reset time), then the live session data."""
    marked, info = state.codex_exhausted()
    if marked:
        return True, {"source": "campaign-state", **info}
    b = budget()
    return bool(b.get("exhausted")), {"source": "sessions", **b}


def mark_exhausted(reason: str, resets_at: float | None = None) -> None:
    state.mark_codex_exhausted(reason, until_ts=float(resets_at) if resets_at else None)


def result_exhausted(r: WorkerResult) -> bool:
    """Did the turn fail because the account budget is gone (not a network stall, not a model failure)?"""
    if r.ok:
        return False
    if EXHAUSTION_RE.search(r.failure or ""):
        return True
    p = Path(r.run_dir) / "events.jsonl"
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if '"error"' not in line and '"turn.failed"' not in line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") in ("error", "turn.failed") and EXHAUSTION_RE.search(str(ev.get("error") or ev.get("message") or "")):
                return True
    return False


# --- dispatch ---------------------------------------------------------------------------------

def _short_cmd(cmd: str, limit: int = 140) -> str:
    cmd = " ".join(cmd.split())
    return cmd if len(cmd) <= limit else cmd[: limit - 1] + "…"


def _follow_events(path: Path, stop: threading.Event, *, prefix: str = "[codex]") -> None:
    """Echo events as they arrive and stamp each one into timeline.jsonl (codex exec emits no timestamps)."""
    from opencad.codex import format_event

    offset = 0
    timeline = path.with_name("timeline.jsonl")
    while True:
        if path.exists():
            with path.open(encoding="utf-8", errors="replace") as f, timeline.open("a", encoding="utf-8") as tl:
                f.seek(offset)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    now = time.time()
                    item = ev.get("item") or {}
                    tl.write(json.dumps({"t": round(now, 3), "type": ev.get("type"), "item_type": item.get("type"), "id": item.get("id"), "exit_code": item.get("exit_code")}) + "\n")
                    msg = format_event(ev)
                    if msg:
                        print(f"{prefix} {time.strftime('%H:%M:%S', time.localtime(now))} {msg}", flush=True)
                offset = f.tell()
        if stop.is_set():
            break
        stop.wait(0.4)


def _wait_with_watchdog(p: subprocess.Popen[str], brief: str, events: Path, *, timeout: float, idle_timeout: float) -> tuple[str, str, float]:
    """Feed the brief, then wait; kill the process group when the events file goes silent for `idle_timeout` s."""
    import signal

    pending: str | None = brief
    t0 = time.time()
    last = t0
    idle_killed = 0.0
    while True:
        try:
            stdout, stderr = p.communicate(input=pending, timeout=5)
            return stdout, stderr, idle_killed
        except subprocess.TimeoutExpired:
            pending = None
        now = time.time()
        if events.exists():
            last = max(last, events.stat().st_mtime)
        idle = now - last
        if idle > idle_timeout or now - t0 > timeout:
            idle_killed = idle if idle > idle_timeout else 0.0
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                p.kill()
            stdout, stderr = p.communicate()
            return stdout, stderr, idle_killed


def _load_usage(run_dir: Path) -> dict[str, Any] | None:
    """Summed usage from usage.json, or from events.jsonl when the wrapper was killed before it wrote the header."""
    path = run_dir / "usage.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
        if isinstance(data, dict) and isinstance(data.get("usage"), dict):
            usage = {key: int(data["usage"].get(key) or 0) for key in ("input", "cached", "output", "reasoning")}
            if any(usage.values()) or data.get("turns"):
                return {"usage": usage, "mode": data.get("mode") or ""}
    events_path = run_dir / "events.jsonl"
    if not events_path.exists():
        return None
    from opencad.codex import sum_turn_usage

    events = []
    for line in events_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    summary = sum_turn_usage(events)
    if not summary["turns"]:
        return None
    usage = {key: int(summary[key]) for key in ("input", "cached", "output", "reasoning")}
    payload = {"seconds": None, "turns": summary["turns"], "mode": summary["mode"], "note": summary["note"], "usage": usage, "events": summary["events"]}
    try:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    return {"usage": usage, "mode": summary["mode"] or ""}


def _rollout_usage(run_dir: Path, thread_id: str, sessions_root: Path = CODEX_SESSIONS) -> dict[str, Any] | None:
    """Usage of one exec read from the thread's rollout file, for an exec killed before any `turn.completed` or a resumed exec
    (whose `turn.completed` reports the whole thread); recorded in usage.json as mode `rollout`."""
    from datetime import UTC, datetime

    from opencad.codex import rollout_usage

    hits = sorted(sessions_root.glob(f"**/rollout-*-{thread_id}.jsonl")) if thread_id else []
    if not hits:
        return None
    since = None
    try:
        started = json.loads((run_dir / "settings.json").read_text(encoding="utf-8")).get("started")
        since = datetime.strptime(started, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC) if started else None
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    usage = rollout_usage(hits[-1], since)
    if not usage or not any(usage.values()):
        return None
    note = "usage is the rollout's token_count delta over this exec (killed before turn.completed, or resumed: turn.completed reports the thread)"
    try:
        (run_dir / "usage.json").write_text(json.dumps({"seconds": None, "turns": 0, "mode": "rollout", "note": note, "usage": usage}, indent=2) + "\n",
                                            encoding="utf-8")
    except OSError:
        pass
    return {"usage": usage, "mode": "rollout"}


def _dispatch_once(brief: str, *, cd: Path, run_dir: Path, images: list[Path] | None, read_only: bool, resume: str | None, add_dirs: list[Path] | None,
                   timeout: float, echo: bool, idle_timeout: float | None = None, effort: str | None = None) -> WorkerResult:
    idle_timeout = IDLE_TIMEOUT if idle_timeout is None else idle_timeout
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(CODEX_EXEC), "--run-dir", str(run_dir), "--timeout", str(int(timeout))]
    if resume:
        cmd += ["--resume", resume]
    else:
        cmd += ["--cd", str(cd)]
        if read_only:
            cmd.append("--read-only")
    for img in images or []:
        cmd += ["--image", str(img)]
    cmd.append("-")
    extra = []
    for d in add_dirs or []:
        extra += ["--add-dir", str(d)]
    if extra and not resume:
        cmd += ["--", *extra]
    env = {**os.environ}
    if effort:
        env["CODEX_REASONING_EFFORT"] = effort
    if echo:
        print(f"[codex] dispatch -> {run_dir.name} (cd={cd}, resume={resume or '-'}, effort={env.get('CODEX_REASONING_EFFORT', 'default')})", flush=True)
    stop = threading.Event()
    tailer = None
    if echo:
        tailer = threading.Thread(target=_follow_events, args=(run_dir / "events.jsonl", stop), daemon=True)
        tailer.start()
    idle_killed = 0.0
    try:
        # own process group so an idle kill takes `codex exec` down with the wrapper
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=REPO_ROOT, start_new_session=True, env=env)
        stdout, stderr, idle_killed = _wait_with_watchdog(p, brief, run_dir / "events.jsonl", timeout=timeout + 120, idle_timeout=idle_timeout)
    finally:
        stop.set()
        if tailer is not None:
            tailer.join(timeout=2)
    stdout = stdout or ""
    stderr = stderr or ""
    if idle_killed:
        stderr += f"\nidle watchdog: no Codex event for {idle_killed:.0f} s; process group killed"
    m = HEADER_RE.search(stdout)
    thread_id, usage, commands, seconds = "", {}, 0, 0.0
    usage_mode = ""
    if m:
        thread_id = m.group(1)
        seconds = float(m.group(3))
        commands = int(m.group(4))
        usage = {"input": int(m.group(5)), "cached": int(m.group(6)), "output": int(m.group(7)), "reasoning": int(m.group(8))}
    loaded = _load_usage(run_dir)
    if loaded:
        usage = loaded["usage"]
        usage_mode = loaded.get("mode") or ""
    if not thread_id and (run_dir / "events.jsonl").exists():  # a killed wrapper prints no header; the stream still names the thread
        for line in (run_dir / "events.jsonl").read_text(encoding="utf-8", errors="replace").splitlines():
            if '"thread.started"' in line:
                try:
                    thread_id = json.loads(line).get("thread_id", "") or ""
                except json.JSONDecodeError:
                    pass
                break
    if thread_id not in ("", "?") and (resume or not any(usage.values())):
        rolled = _rollout_usage(run_dir, thread_id)
        if rolled:
            usage, usage_mode = rolled["usage"], rolled["mode"]
    fm = re.search(r"^failure=(.*)$", stdout, flags=re.MULTILINE)
    result_md_path = run_dir / "result.md"
    result_md = result_md_path.read_text(encoding="utf-8") if result_md_path.exists() else ""
    failure = (fm.group(1).strip() if fm else "") or ("" if p.returncode == 0 else (stderr.strip()[-500:] or f"exit {p.returncode}"))
    network_warning = ""
    if failure and p.returncode == 0 and NETWORK_RE.search(failure) and network_stall(run_dir)["turn_completed"]:
        # a reconnect the worker recovered from: the turn completed and the report exists; record it, do not fail the stage
        network_warning, failure = failure, ""
    from opencad.codex import parse_sections

    r = WorkerResult(
        thread_id=thread_id if thread_id != "?" else "", exit_code=p.returncode if p.returncode is not None else 1, seconds=seconds,
        commands=commands, usage=usage, usage_mode=usage_mode, run_dir=run_dir, result_md=result_md, failure=failure, sections=parse_sections(result_md),
        backend="codex", model=MODEL,
    )
    if network_warning:
        r.network_stalls = [{"run_dir": str(run_dir), "recovered": True, "message": network_warning[:200]}]
        if echo:
            print(f"[codex] recovered from a network reconnect during the turn: {network_warning[:120]}", flush=True)
    (run_dir / "dispatch.stdout.txt").write_text(stdout, encoding="utf-8")
    if echo:
        print(f"[codex] done exit={r.exit_code} seconds={r.seconds:.0f} commands={r.commands} thread={r.thread_id or '?'}", flush=True)
    return r


def with_deadline(brief: str, timeout: float, now: float | None = None) -> str:
    """The brief plus an absolute UTC finish time: Codex has no clock of its own and otherwise runs into the kill mid-edit."""
    from datetime import UTC, datetime

    end = datetime.fromtimestamp((time.time() if now is None else now) + max(60.0, timeout - DEADLINE_MARGIN_S), tz=UTC)
    return (f"{brief.rstrip()}\n\nDeadline: finish by {end:%H:%M:%S} UTC; the turn is killed {DEADLINE_MARGIN_S:.0f} s later. Check `date -u +%H:%M:%S` "
            "before each long step. By the deadline the deliverable must be an executing checkpoint and your report written.\n")


def dispatch(brief: str, *, cd: Path, run_dir: Path, images: list[Path] | None = None, read_only: bool = False, resume: str | None = None,
             add_dirs: list[Path] | None = None, timeout: float = 1800, echo: bool = True, network_retries: int = 2,
             effort: str | None = None, idle_timeout: float | None = None) -> WorkerResult:
    """Run codex_exec.py and collect the report. Never raises on a Codex failure; check `.ok`.

    A turn that dies waiting for the network (no completion, repeated reconnect errors) or hangs is not charged
    against the caller's round budget: wait for connectivity (bounded), then continue the same thread, up to
    `network_retries` times. The stalls are recorded on the result.
    """
    run_dir = Path(run_dir)
    brief = with_deadline(brief, timeout)
    stalls: list[dict[str, Any]] = []
    for attempt in range(network_retries + 1):
        r = _dispatch_once(brief, cd=cd, run_dir=run_dir, images=images, read_only=read_only, resume=resume, add_dirs=add_dirs, timeout=timeout, echo=echo,
                           idle_timeout=idle_timeout, effort=effort)
        st = network_stall(run_dir)
        hung = "idle watchdog" in (r.failure or "") and not r.ok
        if not ((st["stalled"] or hung) and attempt < network_retries):
            r.network_stalls = stalls + list(r.network_stalls)
            r.seconds += sum(s.get("seconds", 0) for s in stalls)
            return r
        stalls.append({"run_dir": str(run_dir), "seconds": r.seconds, "hung": hung, **st})
        if hung:
            if echo:
                print(f"[codex] turn hung (no event for {idle_timeout or IDLE_TIMEOUT:.0f} s, process killed); continuing thread {r.thread_id or resume or '?'}", flush=True)
            waited = 0.0
        else:
            if echo:
                print(f"[codex] turn stalled on the network ({st['network_errors']} errors, {st['commands']} commands); waiting for connectivity, then continuing thread {r.thread_id or resume or '?'}", flush=True)
            waited = wait_for_network()
        stalls[-1]["waited_seconds"] = round(waited)
        resume = r.thread_id or resume
        if not resume:
            r.network_stalls = stalls
            return r
        brief = NETWORK_CONTINUE
        images = None
        run_dir = run_dir.with_name(f"{run_dir.name}-net{attempt + 1}")
    r.network_stalls = stalls  # pragma: no cover - loop always returns
    return r

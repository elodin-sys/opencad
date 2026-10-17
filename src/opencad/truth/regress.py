"""Regression session: each case drafted once and shared by every backend, then one run per case x backend, in parallel.

`python -m opencad.truth regress --tag T` starts the drafts, starts a case's backend runs as soon as its design is published
(FreeCAD first: its turns run longest), and prints one numbered `EVENT#k {...}` line per worker hand-back (`NEXT`), `STALE` or
`EXPIRED` notice, skipped run and child exit, so the orchestrator can wait for the next number. Children are ordinary
subprocesses of this command and stop with it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any

from opencad.io import dump_json, utc_now
from opencad.paths import REGRESS, REPO_ROOT, RESULTS_BASE, design_dir

DEFAULT_CASES = ("bearing-housing", "enclosure-base")
DEFAULT_BACKENDS = ("cadquery", "build123d", "freecad")
ASSEMBLY_SUITE = ("gear-train", "compound-train", "planetary-set", "rack-pinion", "four-bar", "crank-slider")
ASSEMBLY_BACKENDS = ("build123d",)
LANE_ORDER = ("freecad", "build123d", "cadquery")
EVENT_KINDS = {"NEXT": "next", "STALE": "stale", "EXPIRED": "expired"}


@dataclass
class Lane:
    case: str
    design: str
    backend: str
    draft: bool = False
    machine: bool = False
    arm: str = ""
    proc: subprocess.Popen[str] | None = None
    pump: threading.Thread | None = None
    watchdog: Any = None
    started: float | None = None
    ended: float | None = None
    code: int | None = None
    skipped: str | None = None
    lines: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return f"draft-{self.case}" if self.draft else f"{self.case}@{self.backend}"

    def exit_reason(self) -> dict[str, str]:
        """`{"reason": "memory"}` when the lane watchdog killed it; its pipeline state lets a later drive continue it."""
        return {"reason": "memory"} if self.watchdog is not None and self.watchdog.killed else {}

    @property
    def wall_s(self) -> float | None:
        return self.ended - self.started if self.started is not None and self.ended is not None else None

    def entry(self) -> dict[str, Any]:
        """The attempt entry the child prints last, as an indented JSON object."""
        for i in range(len(self.lines) - 1, -1, -1):
            if self.lines[i] != "{":
                continue
            try:
                obj, _ = json.JSONDecoder().raw_decode("\n".join(self.lines[i:]))
            except json.JSONDecodeError:
                continue
            return obj if isinstance(obj, dict) else {}
        return {}

    def verdict(self) -> str:
        if self.skipped:
            return "NOT RUN"
        if self.draft:
            return (
                "published" if self.code == 0 and (design_dir(self.design) / "contract.yaml").exists() else "DRAFT FAILED"
            )
        e = self.entry()
        verdict = (e.get("scorecard") or {}).get("verdict")
        return str(verdict) if verdict else ("ERROR" if e.get("error") or self.code == 2 else "FAIL")

    def gates(self) -> dict[str, int]:
        return (self.entry().get("pipeline") or {}).get("gates") or {}

    def passed(self) -> bool:
        """The regression bar: the scorecard passes and no gate fails."""
        g = self.gates()
        return self.verdict() == "PASS" and bool(g.get("pass")) and not g.get("fail")


def truth_command(lane: Lane, arm: str, tag: str) -> list[str]:
    argv = [sys.executable, "-m", "opencad.truth", "run", lane.case, "--arm", lane.arm or arm, "--backend", lane.backend, "--force", "--tag", tag]
    if lane.machine:  # a machine run drafts, waits on its own orders and scores in one command
        return argv
    return argv + ["--wait"] + (["--stop-after", "draft"] if lane.draft else ["--resume-from", "blockout"])


def machine_arm(case: str, arm: str) -> tuple[bool, str]:
    """(machine case?, the arm to run): the requested arm, or a machine case's first arm (machine arms are named per source packet)."""
    from opencad.truth.manifest import case_dir, load_manifest

    if not (case_dir(case) / "manifest.yaml").exists():
        return False, arm
    m = load_manifest(case)
    ids = [x.id for x in m.arms]
    if m.kind != "machine" or arm in ids:
        return m.kind == "machine", arm
    if not ids:
        raise SystemExit(f"{case} has no arms")
    return True, ids[0]


def arm_for(case: str, arm: str) -> str:
    return machine_arm(case, arm)[1]


def is_machine(case: str) -> bool:
    return machine_arm(case, "")[0]


def design_for(case: str, arm: str) -> str:
    from opencad.truth.manifest import load_manifest

    a = next((x for x in load_manifest(case).arms if x.id == arm_for(case, arm)), None)
    if a is None:
        raise SystemExit(f"arm {arm} is not in the {case} manifest")
    return a.design


def _on_battery() -> bool:
    if sys.platform != "darwin":
        return False
    out = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, check=False).stdout
    return bool(out) and "AC Power" not in out


def preflight(cases: list[str], backends: list[str]) -> tuple[list[str], list[str]]:
    """(problems that block a session, warnings): pending orders, vaulted or missing truth, engine preflights, power, overrides."""
    from opencad.backends.registry import get
    from opencad.truth.manifest import case_dir
    from opencad.truth.runner import live_holders, vault_dirs
    from opencad.worker import orders

    problems, warnings = [], []
    designs = set()
    for case in cases:
        try:
            designs.add(design_for(case, "spec-and-views"))
        except (SystemExit, OSError, ValueError):
            continue

    def ours(part: str) -> bool:  # a machine's part designs are <asm>-<part>
        return not designs or any(part == d or part.startswith(f"{d}-") for d in designs)

    for be in backends:
        pending = orders.all_pending(RESULTS_BASE / be)
        waiting = [o for o in pending if ours(o.part)]
        if waiting:
            names = ", ".join(f"{o.part}/{o.id}" for o in waiting[:3])
            problems.append(
                f"{be}: {len(waiting)} pending worker orders ({names}); finish them first (`opencad next --backend {be}`)"
            )
        elif pending:
            warnings.append(f"{be}: {len(pending)} pending orders on other parts ({pending[0].part}/{pending[0].id}); they share the machine, not the designs")
        pf = get(be).engine.preflight()
        if not pf.get("ok"):
            problems.append(f"{be}: engine preflight failed: {pf.get('error')}")
    for case in cases:
        if live_holders(case):
            problems.append(f"{case}: a live run holds its truth")
        elif vault_dirs(case):
            problems.append(
                f"{case}: truth is still vaulted by an interrupted run (`python -m opencad.truth restore {case}`)"
            )
        elif not (case_dir(case) / "truth").exists():
            problems.append(f"{case}: truth/ is missing")
    overrides = sorted(k for k in os.environ if k == "OPENCAD_MODEL" or k.startswith("OPENCAD_MODEL_"))
    if overrides:
        warnings.append(f"model overrides set ({', '.join(overrides)}): runs will not use the role defaults")
    if os.environ.get("OPENCAD_LEAN_TURNS", "1").lower() in {"0", "false", "no"}:
        warnings.append("OPENCAD_LEAN_TURNS=0: full-read briefs are not comparable with the baseline")
    if _on_battery():
        warnings.append("on battery: caffeinate -s cannot keep the Mac awake; plug in")
    return problems, warnings


def preflight_ok(
    cases: list[str],
    backends: list[str],
    check: Callable[..., tuple[list[str], list[str]]] = preflight,
    out: IO[str] | None = None,
) -> bool:
    problems, warnings = check(cases, backends)
    stream = out or sys.stdout
    for w in warnings:
        print(f"warning: {w}", file=stream, flush=True)
    for p in problems:
        print(f"problem: {p}", file=stream, flush=True)
    return not problems


def write_report(tag: str) -> Path:
    """The bench report against the promoted baseline, beside the other bench reports."""
    from opencad import telemetry

    out = REGRESS / f"{tag}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    suite = "assembly" if any(r.get("kind") == "attempt" and r.get("arm") == "assembly" for r in telemetry.bench_rows(tag)) else "parts"
    out.write_text(telemetry.bench(tag, telemetry.bench_rows(tag), suite=suite), encoding="utf-8")
    return out


def _gates(lane: Lane) -> str:
    g = lane.gates()
    return f"{g.get('pass', 0)}/{g.get('pass', 0) + g.get('fail', 0)}" if g else "-"


def _accuracy(lane: Lane) -> str:
    acc = (lane.entry().get("scorecard") or {}).get("accuracy_score")
    return f"{acc:.1f}" if isinstance(acc, (int, float)) else "-"


def _hms(s: float | None) -> str:
    if s is None:
        return "-"
    s = round(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


class Session:
    def __init__(self, log_dir: Path, out: IO[str] | None = None):
        self.log_dir = log_dir
        self.out = out or sys.stdout
        self.k = 0
        self._lock = threading.Lock()

    def say(self, text: str) -> None:
        with self._lock:
            print(text, file=self.out, flush=True)

    def event(self, lane: Lane, kind: str, **data: Any) -> None:
        with self._lock:
            self.k += 1
            print(
                f"EVENT#{self.k} " + json.dumps({"lane": lane.name, "kind": kind, **data}, default=str),
                file=self.out,
                flush=True,
            )

    def start(self, lane: Lane, argv: list[str]) -> None:
        log = self.log_dir / f"{lane.name}.log"
        lane.started = time.time()
        lane.proc = subprocess.Popen(
            argv,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        from opencad import resources

        # the lane's own RSS only: its engine runners have their own budget and watchdog
        limit = resources.lane_limit()
        lane.watchdog = resources.Watchdog(
            lane.proc.pid, limit, tree=False,
            on_kill=lambda rss: self.say(f"== {lane.name}: killed, its own RSS {resources.gb(rss)} exceeded the lane limit {resources.gb(limit)} "
                                         "(2 x OPENCAD_ENGINE_MEM_GB); its pipeline state is kept for a later drive =="),
        ).start()
        lane.pump = threading.Thread(target=self._pump, args=(lane, log), daemon=True)
        lane.pump.start()
        self.say(
            f"== {lane.name}: started pid {lane.proc.pid}, log {log.relative_to(REPO_ROOT) if log.is_relative_to(REPO_ROOT) else log} =="
        )

    def _pump(self, lane: Lane, log: Path) -> None:
        assert lane.proc is not None and lane.proc.stdout is not None
        prefix = f"[{'draft' if lane.draft else lane.backend}/{lane.case}]"
        with log.open("a", encoding="utf-8") as fh:
            for raw in lane.proc.stdout:
                fh.write(raw)
                fh.flush()
                line = raw.rstrip("\n")
                lane.lines.append(line)
                self.say(f"{prefix} {line}")
                body = line
                while body.startswith("[") and "] " in body:  # a machine run relays its part lanes' lines behind "[backend/part] "
                    body = body.split("] ", 1)[1]
                head, _, rest = body.partition(" ")
                if head in EVENT_KINDS:
                    try:
                        payload: Any = json.loads(rest)
                    except json.JSONDecodeError:
                        payload = rest
                    self.event(lane, EVENT_KINDS[head], order=payload)


def run(
    cases: list[str],
    arm: str,
    backends: list[str],
    *,
    jobs: int,
    tag: str,
    reuse_designs: bool = False,
    command: Callable[[Lane, str, str], list[str]] = truth_command,
    poll_s: float = 0.5,
    out: IO[str] | None = None,
    check: Callable[..., tuple[list[str], list[str]]] = preflight,
    report: Callable[[str], Path] | None = write_report,
) -> int:
    """Exit 0 when every case x backend run passes the scorecard and every gate, 1 when one does not, 2 when the preflight
    refuses to start. Drafts run on the first backend."""
    if not preflight_ok(cases, backends, check, out):
        print(f"== regress {tag}: not started ==", file=out or sys.stdout, flush=True)
        return 2
    log_dir = RESULTS_BASE / "_logs" / tag
    log_dir.mkdir(parents=True, exist_ok=True)
    session = Session(log_dir, out)
    designs = {c: design_for(c, arm) for c in cases}
    machines = {c for c in cases if is_machine(c)}
    drafts = {
        c: Lane(c, designs[c], backends[0], draft=True)
        for c in cases
        if c not in machines and not (reuse_designs and (design_dir(designs[c]) / "contract.yaml").exists())
    }
    rank = {be: LANE_ORDER.index(be) if be in LANE_ORDER else len(LANE_ORDER) for be in backends}
    runs = [Lane(c, designs[c], be, machine=c in machines, arm=arm_for(c, arm)) for be in sorted(backends, key=rank.__getitem__) for c in cases]
    queue: list[Lane] = [*drafts.values(), *runs]
    running: list[Lane] = []
    t0, started_at = time.time(), utc_now()
    session.say(f"== regress {tag}: {len(drafts)} drafts, {len(runs)} runs, jobs {jobs}, logs {log_dir} ==")
    try:
        while queue or running:
            for lane in [x for x in running if x.proc is not None and x.proc.poll() is not None]:
                assert lane.proc is not None and lane.pump is not None
                lane.pump.join()
                lane.ended, lane.code = time.time(), lane.proc.returncode
                running.remove(lane)
                session.event(lane, "exit", code=lane.code, verdict=lane.verdict(), wall_s=round(lane.wall_s or 0), **lane.exit_reason())
            for lane in list(queue):
                if len(running) >= jobs:
                    break
                d = drafts.get(lane.case)
                if not lane.draft and not lane.machine:
                    if d is not None and d.code is None:
                        continue
                    if d is not None and d.verdict() != "published":
                        lane.skipped = f"the {lane.case} draft did not publish"
                    elif not (design_dir(lane.design) / "contract.yaml").exists():
                        lane.skipped = f"no published {design_dir(lane.design)}"
                queue.remove(lane)
                if lane.skipped:
                    session.event(lane, "skipped", reason=lane.skipped)
                    continue
                session.start(lane, command(lane, arm, tag))
                running.append(lane)
            time.sleep(poll_s)
    finally:
        for lane in running:
            if lane.proc is not None and lane.proc.poll() is None:
                lane.proc.terminate()
    wall = time.time() - t0
    draft_wall = max((x.ended or 0 for x in drafts.values()), default=t0) - t0 if drafts else 0.0
    lines = [
        f"== regress {tag}: session wall {_hms(wall)} (drafts {_hms(draft_wall)}) ==",
        "| run | exit | verdict | gates | accuracy | wall | stage reached |",
        "|---|---|---|---|---|---|---|",
    ]
    for lane in [*drafts.values(), *runs]:
        code = "-" if lane.code is None else str(lane.code)
        lines.append(
            f"| {lane.name} | {code} | {lane.verdict()} | {_gates(lane)} | {_accuracy(lane)} | {_hms(lane.wall_s)} | "
            f"{lane.entry().get('stage_reached', '-')} |"
        )
    ok = True
    for be in backends:
        mine = [x for x in runs if x.backend == be]
        misses = [
            f"{x.case} {x.verdict()}" + (f" gates {_gates(x)}" if x.gates() else "") for x in mine if not x.passed()
        ]
        ok = ok and not misses
        lines.append(
            f"backend {be}: {'FAIL' if misses else 'PASS'} ({len(mine) - len(misses)}/{len(mine)}{': ' + ', '.join(misses) if misses else ''})"
        )
    session.say("\n".join(lines))
    dump_json(
        log_dir / "summary.json",
        {
            "tag": tag,
            "started": started_at,
            "session_wall_s": round(wall),
            "draft_wall_s": round(draft_wall),
            "runs": [
                {
                    "run": x.name,
                    "case": x.case,
                    "backend": x.backend,
                    "draft": x.draft,
                    "code": x.code,
                    "verdict": x.verdict(),
                    "passed": x.passed(),
                    "gates": x.gates(),
                    "accuracy": (x.entry().get("scorecard") or {}).get("accuracy_score"),
                    "wall_s": round(x.wall_s) if x.wall_s is not None else None,
                    "skipped": x.skipped,
                }
                for x in [*drafts.values(), *runs]
            ],
        },
    )
    if report is not None:
        try:
            session.say(f"report {report(tag)}")
        except (OSError, ValueError, KeyError, TypeError) as e:  # the verdict above stands without its report
            session.say(f"report not written: {e!r}")
    return 0 if ok else 1

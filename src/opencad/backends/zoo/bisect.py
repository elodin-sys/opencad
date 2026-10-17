"""`python -m opencad kcl-bisect <main.kcl>`: which pipeline step makes a KCL file fail on the engine?

The file is executed once; when it fails, each `|>` pipeline step is disabled in turn (a variant per step, the
step commented out) and the variant is executed. Steps whose removal makes the file execute are the culprits
("the subtract at line 41 fails; without it the part builds"). `--mode prefix` instead truncates the last
pipeline chain step by step and reports the first step that fails. Each variant is one hosted analyze,
recorded in the ledger when `--ledger` is given; results are cached by the file's content hash.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import time
from pathlib import Path
from typing import Any, Callable

from opencad.backends.zoo import engine as zoo

CACHE_DIR = Path(os.environ.get("OPENCAD_BISECT_CACHE") or (Path.home() / ".cache" / "opencad" / "bisect"))
STEP_RE = re.compile(r"^(\s*)\|>\s*(?P<call>[A-Za-z_][A-Za-z0-9_]*)\s*\(")
MAX_STEPS = 60

Runner = Callable[[Path], tuple[bool, str]]


def pipeline_steps(text: str) -> list[dict[str, Any]]:
    """Every `|> call(...)` line with its 1-based line number, call name and chain index."""
    steps: list[dict[str, Any]] = []
    chain = -1
    prev_was_step = False
    for i, line in enumerate(text.splitlines(), start=1):
        m = STEP_RE.match(line)
        if m:
            if not prev_was_step:
                chain += 1
            steps.append({"line": i, "call": m.group("call"), "text": line.strip(), "chain": chain})
            prev_was_step = True
        elif line.strip() and not line.strip().startswith("//"):
            prev_was_step = False
    return steps


def _disable(text: str, lines: set[int]) -> str:
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        out.append(("// [bisect] " + line) if i in lines else line)
    return "\n".join(out) + "\n"


def default_runner(ledger: Path | None) -> Runner:
    def run(kcl: Path) -> tuple[bool, str]:
        r = zoo.run(["kcl", "analyze", "--format", "json", str(kcl)], engine=True, timeout=600)
        if ledger is not None:
            ledger.parent.mkdir(parents=True, exist_ok=True)
            with ledger.open("a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "t": time.time(),
                            "cmd": "kcl analyze (bisect)",
                            "ok": r.ok,
                            "seconds": r.seconds,
                            "class": None if r.ok else zoo.classify(r),
                        }
                    )
                    + "\n"
                )
        err = (r.stderr or r.stdout).strip()
        if not r.ok and zoo.classify(r) in ("transient", "timeout", "credits", "billing"):
            raise zoo.ZooError(f"bisect stopped: {zoo.classify(r)} engine failure: {err[:300]}", kind=zoo.classify(r))
        return r.ok, err[:600]

    return run


def _variant_dir(src: Path) -> Path:
    # variants live next to the source so relative imports (params.kcl, modules) resolve exactly as in the original
    d = src.parent / f".bisect-{src.stem}"
    d.mkdir(exist_ok=True)
    return d


def bisect(
    src: Path, *, mode: str = "single", runner: Runner | None = None, ledger: Path | None = None, use_cache: bool = True
) -> dict[str, Any]:
    src = Path(src)
    text = src.read_text(encoding="utf-8")
    key = hashlib.sha256(f"{mode}\n{text}".encode()).hexdigest()[:24]
    cache = CACHE_DIR / f"{key}.json"
    if use_cache and cache.exists():
        return {**json.loads(cache.read_text()), "cached": True}
    run = runner or default_runner(ledger)
    steps = pipeline_steps(text)
    out: dict[str, Any] = {"file": str(src), "mode": mode, "steps": len(steps), "calls": 0}
    ok, err = run(src)
    out["calls"] += 1
    if ok:
        out.update({"ok": True, "verdict": "the file executes; nothing to bisect"})
        _cache(cache, out)
        return out
    out["error"] = err
    if not steps:
        out.update(
            {"ok": False, "verdict": "no `|>` pipeline steps found; the failure is outside a pipeline (see error)"}
        )
        _cache(cache, out)
        return out
    if len(steps) > MAX_STEPS:
        out["note"] = f"only the last {MAX_STEPS} of {len(steps)} steps are tried"
        steps = steps[-MAX_STEPS:]
    vdir = _variant_dir(src)
    culprits: list[dict[str, Any]] = []
    try:
        if mode == "prefix":
            last_chain = steps[-1]["chain"]
            chain = [s for s in steps if s["chain"] == last_chain]
            for k in range(len(chain) - 1, -1, -1):  # drop the tail step by step until it executes
                disabled = {s["line"] for s in chain[k:]}
                v = vdir / f"prefix-{k}.kcl"
                v.write_text(_disable(text, disabled), encoding="utf-8")
                ok_k, err_k = run(v)
                out["calls"] += 1
                if ok_k:
                    culprit = chain[k]
                    culprits.append(
                        {**culprit, "why": "the first step of the last chain whose addition breaks the execution"}
                    )
                    break
            if not culprits:
                out["verdict"] = "the last chain fails at its first step or the failure is elsewhere; try --mode single"
        else:
            for s in steps:
                v = vdir / f"single-{s['line']}.kcl"
                v.write_text(_disable(text, {s["line"]}), encoding="utf-8")
                ok_s, err_s = run(v)
                out["calls"] += 1
                if ok_s:
                    culprits.append({**s, "why": "the file executes without this step"})
                elif err_s and err_s.split("\n")[0] != err.split("\n")[0]:
                    s["changes_error"] = err_s.split("\n")[0][:200]
    finally:
        shutil.rmtree(vdir, ignore_errors=True)
    out["culprits"] = culprits
    out["ok"] = False
    if culprits:
        first = culprits[0]
        out["verdict"] = (
            f"line {first['line']}: `{first['text']}` ({first['call']}) is the failing operation: {first['why']}"
        )
    else:
        changed = [s for s in steps if s.get("changes_error")]
        out["verdict"] = "no single step's removal makes the file execute; " + (
            f"removing line {changed[0]['line']} changes the error to: {changed[0]['changes_error']}"
            if changed
            else "the failure needs two or more steps removed (try --mode prefix)"
        )
    _cache(cache, out)
    return out


def _cache(cache: Path, out: dict[str, Any]) -> None:
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out, indent=1, default=str))


def format_report(r: dict[str, Any]) -> str:
    lines = [
        f"kcl-bisect {r['file']} ({r['mode']}, {r['steps']} pipeline steps, {r['calls']} engine call(s){', cached' if r.get('cached') else ''})"
    ]
    if r.get("error"):
        lines.append("  error: " + r["error"].split("\n")[0][:200])
    lines.append("  " + r.get("verdict", ""))
    for c in r.get("culprits", [])[1:]:
        lines.append(f"  also: line {c['line']} `{c['text']}`")
    if r.get("note"):
        lines.append("  note: " + r["note"])
    return "\n".join(lines)


def main(
    src: Path, *, mode: str = "single", ledger: Path | None = None, no_cache: bool = False, as_json: bool = False
) -> int:
    try:
        r = bisect(Path(src), mode=mode, ledger=ledger, use_cache=not no_cache)
    except zoo.ZooError as e:
        print(f"kcl-bisect: {e}")
        return 2
    print(json.dumps(r, indent=1, default=str) if as_json else format_report(r))
    return 0 if r.get("ok") else 1

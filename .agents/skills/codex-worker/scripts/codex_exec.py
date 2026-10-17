#!/usr/bin/env python3
"""Dispatch one task to the local Codex CLI (GPT-6 Astra, role-based effort; the opt-in worker path) and collect its output.

  codex_exec.py [--cd DIR] [--read-only] [--image PATH]... [--resume THREAD_ID]
                [--run-dir DIR] [--timeout SEC] PROMPT [-- extra codex exec args]

PROMPT may be "-" to read the brief from stdin. Artifacts land in the run dir:
prompt.md, events.jsonl, stderr.log, result.md. Stdout is a short summary header
(run_dir, thread_id, exit, seconds, usage) followed by Codex's final message.
Exit code is Codex's own.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
REPO_SRC = Path(__file__).resolve().parents[4] / "src"

# Worker settings: non-interactive, network on so the Zoo engine is reachable from inside the sandbox.
# The pipeline sets CODEX_REASONING_EFFORT per role, or OPENCAD_CODEX_EFFORT for every role (`max` is
# GPT-6 Astra Max). `high` is the default for direct use. The model is pinned so a local config change
# cannot switch it. The context window stays at the catalog default (272k for gpt-6-astra) so
# auto-compaction fires near CODEX_COMPACT_LIMIT. CODEX_SERVICE_TIER pins a tier when set; empty omits
# it (the default "fast" is the Fast tier). All are recorded in the run dir's settings.json.
MODEL = "gpt-6-astra"
EFFORT = os.environ.get("CODEX_REASONING_EFFORT", "high")
SERVICE_TIER = os.environ.get("CODEX_SERVICE_TIER", "fast")
COMPACT_LIMIT = os.environ.get("CODEX_COMPACT_LIMIT", "160000")
CONTEXT_WINDOW = os.environ.get("CODEX_CONTEXT_WINDOW", "")
OVERRIDES = [
    "-c", "approval_policy=never",
    "-c", f'model="{MODEL}"',
    "-c", f"model_reasoning_effort={EFFORT}",
    "-c", f"model_auto_compact_token_limit={COMPACT_LIMIT}",
    "-c", "sandbox_workspace_write.network_access=true",
]
if SERVICE_TIER:
    OVERRIDES += ["-c", f'service_tier="{SERVICE_TIER}"']
if CONTEXT_WINDOW:
    OVERRIDES += ["-c", f"model_context_window={CONTEXT_WINDOW}"]

RULES = """- Do not run `codex`, do not commit or push, and do not touch files outside the stated scope.
- End your final message with these sections: `## Result`, `## Files changed`, `## Verification` (commands run, measured vs expected values), `## Open questions` (anything unverified).

# Task
"""

CONTRACT = f"""You are a Codex worker dispatched by a Cursor orchestrator. Finish the task below on your own; nobody will answer questions mid-run.
- Skills live in {SKILLS} (one SKILL.md per folder). For Zoo/KCL work read backends/zoo/kcl-docs and backends/zoo/zoo-tooling first.
""" + RULES

# a resumed thread already holds the skills and the part in context: re-reading them costs minutes per turn
CONTRACT_RESUME = f"""You are a Codex worker continuing a thread you already worked in for a Cursor orchestrator. Finish the task below on your own; nobody will answer questions mid-run.
- The skills under {SKILLS} and the files you read earlier are still valid: do not re-read them unless you need one specific reference; do not restate what you did before.
""" + RULES


def parse(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    extra: list[str] = []
    if "--" in argv:
        i = argv.index("--")
        argv, extra = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt", help='task brief, or "-" for stdin')
    ap.add_argument("--cd", default=os.getcwd(), help="Codex working root (the writable tree); default cwd")
    ap.add_argument("--read-only", action="store_true", help="review mode: no writes, no network")
    ap.add_argument("--image", action="append", default=[], help="attach an image (repeatable)")
    ap.add_argument("--resume", metavar="THREAD_ID", help="continue an existing thread")
    ap.add_argument("--run-dir", help="where to write artifacts (default $TMPDIR/codex-worker/<utc>-<pid>)")
    ap.add_argument("--timeout", type=float, default=1800, help="seconds before Codex is killed (default 1800)")
    return ap.parse_args(argv), extra


def main() -> int:
    args, extra = parse(sys.argv[1:])
    prompt = sys.stdin.read() if args.prompt == "-" else args.prompt
    prompt = (CONTRACT_RESUME if args.resume else CONTRACT) + prompt.strip() + "\n"

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = Path(args.run_dir or Path(os.environ.get("TMPDIR", "/tmp")) / "codex-worker" / f"{stamp}-{os.getpid()}")
    run.mkdir(parents=True, exist_ok=True)
    (run / "prompt.md").write_text(prompt, encoding="utf-8")
    (run / "settings.json").write_text(json.dumps({"model": MODEL, "reasoning_effort": EFFORT, "service_tier": SERVICE_TIER or None, "compact_limit": COMPACT_LIMIT,
                                                   "context_window": CONTEXT_WINDOW or "catalog", "resume": args.resume or None, "started": stamp}), encoding="utf-8")
    result = run / "result.md"

    cmd = ["codex", "exec"]
    if args.resume:
        cmd += ["resume", args.resume]
    else:
        cmd += ["--cd", str(Path(args.cd).resolve()), "--sandbox", "read-only" if args.read_only else "workspace-write"]
    cmd += OVERRIDES
    for img in args.image:
        cmd += ["-i", img]
    cmd += extra + ["--json", "-o", str(result), prompt]

    t0 = time.time()
    with (run / "events.jsonl").open("w", encoding="utf-8") as events, (run / "stderr.log").open("w", encoding="utf-8") as err:
        try:
            code = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=events, stderr=err, timeout=args.timeout).returncode
        except subprocess.TimeoutExpired:
            err.write(f"\ncodex_exec.py: killed after {args.timeout:.0f}s\n")
            code = 124
    seconds = time.time() - t0

    thread_id, failure, commands = "", "", 0
    parsed: list[dict] = []
    for line in (run / "events.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        parsed.append(e)
        t = e.get("type")
        if t == "thread.started":
            thread_id = e.get("thread_id", "")
        elif t in ("turn.failed", "error"):
            failure = json.dumps(e.get("error", e))[:300]
        elif t == "item.completed" and e.get("item", {}).get("type") == "command_execution":
            commands += 1
    if str(REPO_SRC) not in sys.path:
        sys.path.insert(0, str(REPO_SRC))
    from opencad.codex import sum_turn_usage

    summary = sum_turn_usage(parsed)
    usage = {key: summary[key] for key in ("input", "cached", "output", "reasoning")}
    (run / "usage.json").write_text(json.dumps({
        "seconds": round(seconds, 3), "turns": summary["turns"], "mode": summary["mode"], "note": summary["note"],
        "usage": usage, "events": summary["events"],
    }, indent=2) + "\n", encoding="utf-8")
    if code == 0 and not result.exists():
        code = 1
        failure = failure or "codex exited 0 without a final message"

    print(f"codex-worker run_dir={run}")
    print(f"thread_id={thread_id or '?'} exit={code} seconds={seconds:.0f} commands={commands} "
          f"usage=in:{usage['input']} cached:{usage['cached']} "
          f"out:{usage['output']} reasoning:{usage['reasoning']}")
    if summary["mode"] not in ("", "empty"):
        print(f"usage_mode={summary['mode']}")
    if failure:
        print(f"failure={failure}")
    print("--- final message ---")
    print(result.read_text(encoding="utf-8") if result.exists() else "(none)")
    return code


if __name__ == "__main__":
    sys.exit(main())

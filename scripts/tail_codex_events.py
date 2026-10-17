#!/usr/bin/env python3
"""Follow a Codex events.jsonl file and print a readable live log.

Usage:
  python scripts/tail_codex_events.py results/<part>/model-work/codex/events.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from opencad.codex import format_event


def follow(path: Path, *, poll: float) -> None:
    offset = 0
    while True:
        if not path.exists():
            time.sleep(poll)
            continue
        with path.open(encoding="utf-8", errors="replace") as f:
            f.seek(offset)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = format_event(e)
                if msg:
                    print(msg, flush=True)
            offset = f.tell()
        time.sleep(poll)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("events", type=Path)
    ap.add_argument("--poll", type=float, default=1.0)
    args = ap.parse_args()
    print(f"# following {args.events.resolve()}", flush=True)
    try:
        follow(args.events, poll=args.poll)
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

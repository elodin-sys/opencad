#!/usr/bin/env python3
"""Mirror KittyCAD/mcp README and server.py into sources/github/kittycad-mcp/."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

REPO = "KittyCAD/mcp"
FILES = ["README.md", "src/zoo_mcp/server.py", "pyproject.toml"]
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sources" / "github" / "kittycad-mcp"
MANIFEST = ROOT / "sources" / "manifest.json"


def get(url: str, accept: str = "application/vnd.github+json") -> bytes:
    req = Request(url, headers={"User-Agent": "opencad-docs-mirror/0.1", "Accept": accept})
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def main() -> int:
    sha = json.loads(get(f"https://api.github.com/repos/{REPO}/commits/main"))["sha"]
    OUT.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = []
    for rel in FILES:
        body = get(f"https://raw.githubusercontent.com/{REPO}/{sha}/{rel}", accept="*/*")
        dest = OUT / Path(rel).name
        dest.write_bytes(body)
        entries.append({"path": rel, "local_path": str(dest.relative_to(ROOT / "sources")), "bytes": len(body)})
        print(f"  {rel} -> {dest.relative_to(ROOT)} ({len(body)} bytes)")

    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    manifest["github"] = {"repo": REPO, "sha": sha, "fetched_at": fetched_at, "files": entries}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{REPO}@{sha[:12]} recorded in sources/manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

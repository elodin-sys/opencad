"""Fetch a public reference file into a truth case with provenance.

    python scripts/fetch_reference.py <case> <url> [--to truth/raw] [--name FILE] [--license TEXT] [--note TEXT] [--unzip]

Downloads go to truth/cases/<case>/<to>/ (default truth/raw/, which is sequestered with the rest of truth/ while workers run;
copy the worker-visible pieces into inputs/ explicitly). Each download appends {url, path, bytes, sha256, accessed, license,
note} to truth/cases/<case>/provenance.yaml; --unzip also extracts an archive beside it and records every member's sha256.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(case: str, url: str, *, to: str = "truth/raw", name: str | None = None, license_: str = "", note: str = "", unzip: bool = False) -> dict:
    case_dir = ROOT / "truth" / "cases" / case
    dest_dir = case_dir / to
    dest_dir.mkdir(parents=True, exist_ok=True)
    fname = name or Path(urllib.parse.unquote(urllib.parse.urlparse(url).path)).name or "download"
    dest = dest_dir / fname
    req = urllib.request.Request(url, headers={"User-Agent": "opencad-fetch/1"})
    with urllib.request.urlopen(req, timeout=300) as r, dest.open("wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    row = {"url": url, "path": str(dest.relative_to(case_dir)), "bytes": dest.stat().st_size, "sha256": sha256(dest),
           "accessed": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "license": license_, "note": note}
    if unzip and zipfile.is_zipfile(dest):
        out = dest_dir / dest.stem
        with zipfile.ZipFile(dest) as z:
            z.extractall(out)
        row["members"] = [{"path": str(p.relative_to(case_dir)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(out.rglob("*")) if p.is_file()]
    prov = case_dir / "provenance.yaml"
    data = yaml.safe_load(prov.read_text(encoding="utf-8")) if prov.exists() else {}
    files = [f for f in (data or {}).get("files") or [] if f.get("path") != row["path"]]
    prov.write_text(yaml.safe_dump({"case": case, "files": [*files, row]}, sort_keys=False, width=120), encoding="utf-8")
    return row


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("case")
    ap.add_argument("url")
    ap.add_argument("--to", default="truth/raw")
    ap.add_argument("--name")
    ap.add_argument("--license", dest="license_", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--unzip", action="store_true")
    a = ap.parse_args(argv)
    row = fetch(a.case, a.url, to=a.to, name=a.name, license_=a.license_, note=a.note, unzip=a.unzip)
    print(yaml.safe_dump({k: v for k, v in row.items() if k != "members"}, sort_keys=False).strip())
    if row.get("members"):
        print(f"members: {len(row['members'])} extracted")
    return 0


if __name__ == "__main__":
    sys.exit(main())

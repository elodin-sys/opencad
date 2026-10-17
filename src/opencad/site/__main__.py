"""python -m opencad.site build --out _site"""

from __future__ import annotations

import argparse
from pathlib import Path

from opencad.paths import REPO_ROOT
from opencad.site.build import CARD_CACHE, SiteBuildError, build_site


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m opencad.site")
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="build the static design-review site")
    b.add_argument("--out", type=Path, required=True, help="destination directory (replaced if it holds a previous build)")
    b.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    b.add_argument("--manifest", type=Path, help="overrides (default site/designs.yaml)")
    b.add_argument("--cache", type=Path, default=CARD_CACHE, help="card render cache")
    b.add_argument("--jobs", type=int, default=4, help="parallel card renders")
    args = parser.parse_args()
    try:
        designs = build_site(args.repo_root, args.out, manifest=args.manifest, cache=args.cache, jobs=args.jobs)
    except SiteBuildError as e:
        parser.error(str(e))
    print(f"built {args.out} with {len(designs)} designs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

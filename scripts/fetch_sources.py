#!/usr/bin/env python3
"""Fetch documentation and examples for a modelling backend into sources/<id>/."""

from __future__ import annotations

import argparse
import json
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "opencad-sources/0.1"}
CTX = ssl.create_default_context()


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return r.read()


def write(path: Path, data: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_bytes(data)
    print(f"  wrote {path.relative_to(ROOT)} ({path.stat().st_size} B)")


def github_contents(repo: str, path: str, ref: str = "master") -> list[dict]:
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
    return json.loads(get(url).decode())


def fetch_cadquery() -> None:
    dest = ROOT / "sources" / "cadquery"
    dest.mkdir(parents=True, exist_ok=True)
    for entry in github_contents("CadQuery/cadquery", "doc"):
        if entry["name"].endswith(".rst") and entry["type"] == "file":
            write(dest / "doc" / entry["name"], get(entry["download_url"]))
    for entry in github_contents("CadQuery/cadquery", "examples"):
        if entry["name"].startswith("Ex") and entry["name"].endswith(".py"):
            write(dest / "examples" / entry["name"], get(entry["download_url"]))


def fetch_build123d() -> None:
    dest = ROOT / "sources" / "build123d"
    dest.mkdir(parents=True, exist_ok=True)
    pages = (
        "index.rst.txt",
        "introduction.rst.txt",
        "key_concepts.rst.txt",
        "key_concepts_algebra.rst.txt",
        "introductory_examples.rst.txt",
        "topology_selection.rst.txt",
        "objects.rst.txt",
        "operations.rst.txt",
        "import_export.rst.txt",
    )
    base = "https://build123d.readthedocs.io/en/stable/_sources/"
    for page in pages:
        try:
            write(dest / "docs" / page, get(base + page).decode())
        except Exception as e:
            print(f"  skip {page}: {e}")
    for path in ("docs/general_examples.py", "examples"):
        try:
            listing = github_contents("gumyr/build123d", path, ref="dev")
            if isinstance(listing, dict):
                listing = [listing]
            for entry in listing:
                if entry.get("type") == "file" and str(entry.get("name", "")).endswith(".py"):
                    write(dest / "examples" / entry["name"], get(entry["download_url"]))
        except Exception as e:
            print(f"  {path} via github failed: {e}")


def fetch_freecad() -> None:
    dest = ROOT / "sources" / "freecad"
    dest.mkdir(parents=True, exist_ok=True)
    pages = {
        "Python_scripting_tutorial": "https://wiki.freecad.org/Python_scripting_tutorial?action=raw",
        "FreeCAD_Scripting_Basics": "https://wiki.freecad.org/FreeCAD_Scripting_Basics?action=raw",
        "Part_scripting": "https://wiki.freecad.org/Part_scripting?action=raw",
        "Topological_data_scripting": "https://wiki.freecad.org/Topological_data_scripting?action=raw",
        "Sketcher_scripting": "https://wiki.freecad.org/Sketcher_scripting?action=raw",
        "PartDesign_Workbench": "https://wiki.freecad.org/PartDesign_Workbench?action=raw",
        "PartDesign_Body": "https://wiki.freecad.org/PartDesign_Body?action=raw",
        "PartDesign_Pad": "https://wiki.freecad.org/PartDesign_Pad?action=raw",
        "PartDesign_Pocket": "https://wiki.freecad.org/PartDesign_Pocket?action=raw",
        "PartDesign_Hole": "https://wiki.freecad.org/PartDesign_Hole?action=raw",
        "PartDesign_Fillet": "https://wiki.freecad.org/PartDesign_Fillet?action=raw",
        "PartDesign_AdditiveLoft": "https://wiki.freecad.org/PartDesign_AdditiveLoft?action=raw",
        "PartDesign_Thickness": "https://wiki.freecad.org/PartDesign_Thickness?action=raw",
        "PartDesign_Plane": "https://wiki.freecad.org/PartDesign_Plane?action=raw",
        "Topological_naming_problem": "https://wiki.freecad.org/Topological_naming_problem?action=raw",
        "Headless_FreeCAD": "https://wiki.freecad.org/Headless_FreeCAD?action=raw",
    }
    for name, url in pages.items():
        try:
            write(dest / "wiki" / f"{name}.mediawiki", get(url).decode())
        except Exception as e:
            print(f"  skip {name}: {e}")
    try:
        for entry in github_contents("FreeCAD/FreeCAD", "src/Mod/PartDesign/PartDesignTests", ref="main"):
            if entry.get("type") == "file" and str(entry.get("name", "")).endswith(".FCStd"):
                write(dest / "examples" / entry["name"], get(entry["download_url"]))
                if len(list((dest / "examples").glob("*.FCStd"))) >= 4:
                    break
    except Exception as e:
        print(f"  examples via github failed: {e}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, choices=["cadquery", "build123d", "freecad", "all"])
    args = ap.parse_args()
    backends = ["cadquery", "build123d", "freecad"] if args.backend == "all" else [args.backend]
    for b in backends:
        print(f"== {b} ==")
        {"cadquery": fetch_cadquery, "build123d": fetch_build123d, "freecad": fetch_freecad}[b]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

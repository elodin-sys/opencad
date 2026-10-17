"""Repository layout and part-path resolution.

Parts and results are backend-rooted: `parts/<backend>/<part>` and `results/<backend>/<part>`.
`PARTS` / `RESULTS` resolve against the current `--backend` / `OPENCAD_BACKEND` (default build123d).
A part design an assembly names nests under it in all three trees: `designs/<asm>/parts/<leaf>`,
`parts/<backend>/<asm>/parts/<leaf>`, `results/<backend>/<asm>/parts/<leaf>` (leaf: the design name without `<asm>-`).
Build a design's paths with `design_dir`, `part_dir` and `results_dir`, never `ROOT / name`.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGNS = REPO_ROOT / "designs"
PARTS_BASE = REPO_ROOT / "parts"
RESULTS_BASE = REPO_ROOT / "results"
TRUTH = REPO_ROOT / "truth"
DOCS = REPO_ROOT / "docs"
SKILLS = REPO_ROOT / ".agents" / "skills"
ZOO_SKILLS = SKILLS / "backends" / "zoo"
CODEX_EXEC = SKILLS / "codex-worker" / "scripts" / "codex_exec.py"
TEMPLATE = DESIGNS / "_template"
CONTRACT_FILE = "contract.yaml"
ASSEMBLY_FILE = "assembly.yaml"
BRIEF_FILE = "brief.md"
LOGS = RESULTS_BASE / "_logs"
BAKEOFF = RESULTS_BASE / "_bakeoff"
REGRESS = RESULTS_BASE / "_regress"
DEFAULT_BACKEND = "build123d"

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class PartNameError(ValueError):
    pass


def check_part_name(name: str) -> str:
    """Same rules as open-air's concept_name: flat, safe, never reserved."""
    if not NAME_RE.match(name) or ".." in name or name.startswith("_"):
        raise PartNameError(
            f"invalid part name {name!r}: letters, digits, '.', '_', '-' only; no leading '_' or '.'; max 64 chars"
        )
    return name


def backend_id(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    return os.environ.get("OPENCAD_BACKEND") or DEFAULT_BACKEND


def parts_root(backend: str | None = None) -> Path:
    return PARTS_BASE / backend_id(backend)


def results_root(backend: str | None = None) -> Path:
    return RESULTS_BASE / backend_id(backend)


class _BackendRoot:
    """Path-like that resolves against the current backend at access time."""

    def __init__(self, kind: str):
        self._kind = kind

    def _p(self) -> Path:
        return parts_root() if self._kind == "parts" else results_root()

    def __truediv__(self, other: Any) -> Path:
        return self._p() / other

    def __fspath__(self) -> str:
        return str(self._p())

    def __str__(self) -> str:
        return str(self._p())

    def __repr__(self) -> str:
        return repr(self._p())

    def __eq__(self, other: object) -> bool:
        return self._p() == Path(other) if other is not None else False

    def exists(self) -> bool:
        return self._p().exists()

    def is_dir(self) -> bool:
        return self._p().is_dir()

    def iterdir(self):
        p = self._p()
        if not p.exists():
            return iter(())
        return p.iterdir()

    def mkdir(self, *a: Any, **kw: Any) -> None:
        self._p().mkdir(*a, **kw)

    def resolve(self) -> Path:
        return self._p().resolve()

    def glob(self, pattern: str):
        return self._p().glob(pattern)

    def rglob(self, pattern: str):
        return self._p().rglob(pattern)

    @property
    def parent(self) -> Path:
        return self._p().parent

    @property
    def name(self) -> str:
        return self._p().name


PARTS = _BackendRoot("parts")
RESULTS = _BackendRoot("results")


ASSEMBLY_PARTS = "parts"
AMENDED = ".amended"
NESTED = (ASSEMBLY_PARTS, AMENDED)  # entries of an assembly folder that are not the assembly's own files

_members: tuple[tuple[tuple[str, int], ...], dict[str, tuple[str, str]]] | None = None


def leaf_name(design: str, asm: str) -> str:
    return design.removeprefix(f"{asm}-") if design.startswith(f"{asm}-") else design


def membership() -> dict[str, tuple[str, str]]:
    """design -> (assembly, leaf) for every design a published or staged assembly.yaml names (staged: its parts publish first)."""
    global _members
    files: list[tuple[str, Path]] = []
    if DESIGNS.is_dir():
        for d in sorted(DESIGNS.iterdir()):
            asm = d.name.removeprefix(".staging-")
            if asm.startswith((".", "_")) or not (d / ASSEMBLY_FILE).is_file():
                continue
            files.append((asm, d / ASSEMBLY_FILE))
    key = tuple((str(f), f.stat().st_mtime_ns) for _, f in files)
    if _members is not None and _members[0] == key:
        return _members[1]
    out: dict[str, tuple[str, str]] = {}
    leaves: dict[tuple[str, str], str] = {}
    for asm, f in files:
        try:
            parts = (yaml.safe_load(f.read_text()) or {}).get("parts") or []
        except yaml.YAMLError:
            continue
        for p in parts:
            d = p.get("design") if isinstance(p, dict) else None
            if not d or d == asm:
                continue
            owner = out.get(d)
            if owner and owner[0] != asm:
                raise PartNameError(f"design {d!r} is named by assemblies {owner[0]!r} and {asm!r}; a design belongs to one assembly")
            leaf = leaf_name(d, asm)
            if leaves.setdefault((asm, leaf), d) != d:
                raise PartNameError(f"designs {leaves[(asm, leaf)]!r} and {d!r} of assembly {asm!r} share the folder name {leaf!r}")
            out[d] = (asm, leaf)
    _members = (key, out)
    return out


def _nest(root: Path, name: str) -> Path:
    m = membership().get(check_part_name(name))
    return root / m[0] / ASSEMBLY_PARTS / m[1] if m else root / name


def design_dir(name: str) -> Path:
    return _nest(DESIGNS, name)


def part_dir(name: str, *, backend: str | None = None) -> Path:
    return _nest(parts_root(backend), name)


def results_dir(name: str, *, backend: str | None = None) -> Path:
    return _nest(results_root(backend), name)


def design_name(rel: Path | tuple[str, ...]) -> str:
    """The design a path relative to a tree root (designs/, parts/<backend>/, results/<backend>/) belongs to."""
    parts = rel.parts if isinstance(rel, Path) else tuple(rel)
    if len(parts) >= 3 and parts[1] == ASSEMBLY_PARTS:
        for d, (asm, leaf) in membership().items():
            if (asm, leaf) == (parts[0], parts[2]):
                return d
    return parts[0]


def resolve_part(arg: str | Path, *, backend: str | None = None) -> tuple[str, Path, Path]:
    """Accept `<name>`, `designs/<name>`, `designs/<asm>/parts/<leaf>`, or either with `/contract.yaml`.

    Returns (name, contract_path, results_dir). Does not require the files to exist.
    """
    p = Path(arg)
    if p.name == CONTRACT_FILE:
        p = p.parent
    if len(p.parts) == 1 and not p.is_absolute():
        name = p.parts[0]
    else:
        full = (p if p.is_absolute() else REPO_ROOT / p).resolve()
        try:
            rel = full.relative_to(DESIGNS.resolve())
        except ValueError as e:
            raise PartNameError(f"{arg} is not under {DESIGNS}") from e
        if len(rel.parts) not in (1, 3) or (len(rel.parts) == 3 and rel.parts[1] != ASSEMBLY_PARTS):
            raise PartNameError(f"{arg} must be designs/<name> or designs/<asm>/{ASSEMBLY_PARTS}/<part>")
        name = design_name(rel)
        if len(rel.parts) == 3 and name == rel.parts[0]:
            raise PartNameError(f"{arg}: assembly {rel.parts[0]!r} names no design with folder {rel.parts[2]!r}")
    check_part_name(name)
    return name, design_dir(name) / CONTRACT_FILE, results_dir(name, backend=backend)

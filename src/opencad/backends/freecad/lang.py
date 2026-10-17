"""FreeCAD language: AST hygiene requiring a PartDesign tree."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from opencad.backends.freecad.rules import ALLOWED_IMPORTS, CONSTRUCTION, RULES, skills, skills_note
from opencad.backends.pythonlang import (
    hygiene,
    parameter_values,
    rewrite_parameter,
    ruff_check,
    ruff_format_check,
    ruff_format_write,
    source_files,
)
from opencad.paths import REPO_ROOT
from opencad.schemas import PartContract


class FreeCADLanguage:
    id = "freecad"
    entry = "main.py"
    suffixes = (".py",)

    def source_files(self, part_dir: Path) -> list[Path]:
        return source_files(part_dir)

    def check(self, part_dir: Path, contract: PartContract) -> dict[str, Any]:
        hyg = hygiene(
            part_dir, contract, allowed_imports=ALLOWED_IMPORTS, construction=CONSTRUCTION, dialect_token="PartDesign"
        )
        src = "\n".join(p.read_text(encoding="utf-8") for p in source_files(part_dir))
        hyg["partdesign_tree"] = "PartDesign::Body" in src or "PartDesign" in src and "Body" in src
        if not hyg["partdesign_tree"]:
            hyg["ok"] = False
        return {"format": ruff_format_check(part_dir), "lint": ruff_check(part_dir), "hygiene": hyg}

    def rewrite_parameter(self, part_dir: Path, name: str, value: float) -> Path:
        return rewrite_parameter(part_dir, name, value)

    def parameter_values(self, part_dir: Path, contract: PartContract) -> dict[str, Any]:
        return parameter_values(part_dir, contract)

    def format_write(self, target: Path) -> Any:
        return ruff_format_write(target)

    def rules(self) -> str:
        return RULES

    def skills(self) -> list[Path]:
        return skills()

    def critics(self) -> dict[str, str]:
        py = f"{REPO_ROOT}/.venv/bin/python -m opencad"
        return {
            "quick": f"{py} quick {{entry}} --contract {{contract}} --ledger {{ledger}} --backend freecad",
            "bisect": f"{py} engine --backend freecad -- analyze {{entry}}",
            "note": skills_note(),
        }

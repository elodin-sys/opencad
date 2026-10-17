"""CadQuery language: AST hygiene + ruff."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from opencad.backends.cadquery.rules import ALLOWED_IMPORTS, CONSTRUCTION, RULES, skills, skills_note
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


class CadQueryLanguage:
    id = "cadquery"
    entry = "main.py"
    suffixes = (".py",)

    def source_files(self, part_dir: Path) -> list[Path]:
        return source_files(part_dir)

    def check(self, part_dir: Path, contract: PartContract) -> dict[str, Any]:
        hyg = hygiene(
            part_dir,
            contract,
            allowed_imports=ALLOWED_IMPORTS,
            construction=CONSTRUCTION,
            dialect_token="import cadquery",
        )
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
            "quick": f"{py} quick {{entry}} --contract {{contract}} --ledger {{ledger}} --backend cadquery",
            "bisect": f"{py} engine --backend cadquery -- analyze {{entry}}",
            "note": skills_note(),
        }

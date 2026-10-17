"""KCL language: tokenizer, hygiene, parameter rewrite, Language protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from opencad.backends.zoo.engine import format_check, format_write, lint
from opencad.backends.zoo.kclsrc import hygiene, kcl_files, parameter_values_from_tree, rewrite_parameter_in_tree
from opencad.backends.zoo.rules import KCL_RULES, skills, skills_note
from opencad.paths import REPO_ROOT
from opencad.schemas import PartContract


class ZooLanguage:
    id = "kcl"
    entry = "main.kcl"
    suffixes = (".kcl",)

    def source_files(self, part_dir: Path) -> list[Path]:
        return kcl_files(part_dir)

    def check(self, part_dir: Path, contract: PartContract) -> dict[str, Any]:
        hyg = hygiene(part_dir, contract)
        return {"format": format_check(part_dir), "lint": lint(Path(part_dir) / self.entry), "hygiene": hyg}

    def rewrite_parameter(self, part_dir: Path, name: str, value: float) -> Path:
        return rewrite_parameter_in_tree(part_dir, name, value)

    def parameter_values(self, part_dir: Path, contract: PartContract) -> dict[str, Any]:
        return parameter_values_from_tree(part_dir, contract)

    def format_write(self, target: Path) -> Any:
        return format_write(target)

    def rules(self) -> str:
        return KCL_RULES

    def skills(self) -> list[Path]:
        return skills()

    def critics(self) -> dict[str, str]:
        py = f"{REPO_ROOT}/.venv/bin/python -m opencad"
        return {
            "quick": f"{py} quick {{entry}} --contract {{contract}} --ledger {{ledger}}",
            "bisect": f"{py} kcl-bisect {{entry}}",
            "note": skills_note(),
        }

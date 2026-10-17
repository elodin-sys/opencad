"""Assembly pipeline: an AssemblyContract drafted from sources, its parts through the part pipeline in parallel lanes, a worker
assembly source that places them, then evaluator stages (verify, kinematics, domains, simulate, gates, report).

Layout: designs/<asm>/assembly.yaml (+ designs/<asm>/parts/<leaf>/ part bundles for designs <asm>-<leaf>), parts/<backend>/<asm>/main.py
(the assembly source, inputs/ holds the part handoff STEPs), results/<backend>/<asm>/ (stage JSONs, export/, package/, handoff/). Each
part's own source and results nest the same way: parts/<backend>/<asm>/parts/<leaf>/, results/<backend>/<asm>/parts/<leaf>/.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from opencad.backends.registry import current_id, get
from opencad.contract import ContractError, load_assembly
from opencad.io import dump_stage, load_json
from opencad.paths import ASSEMBLY_FILE, DESIGNS, check_part_name, parts_root, results_dir, results_root
from opencad.schemas import AssemblyContract


class AssemblyError(RuntimeError):
    pass


@dataclass
class AsmCtx:
    name: str
    design_dir: Path
    contract: AssemblyContract
    results_dir: Path
    part_dir: Path
    backend_id: str = field(default_factory=current_id)

    @classmethod
    def load(cls, name: str, *, backend: str | None = None) -> AsmCtx:
        bid = backend or current_id()
        get(bid)
        name = Path(name).name if "/" in str(name) else str(name)
        check_part_name(name)
        design_dir = DESIGNS / name
        try:
            contract = load_assembly(design_dir / ASSEMBLY_FILE)
        except ContractError as e:
            raise AssemblyError(str(e)) from e
        return cls(name, design_dir, contract, results_root(bid) / name, parts_root(bid) / name, bid)

    @property
    def contract_path(self) -> Path:
        return self.design_dir / ASSEMBLY_FILE

    @property
    def backend(self):
        return get(self.backend_id)

    @property
    def entry(self) -> Path:
        return self.part_dir / self.backend.language.entry

    @property
    def kcl(self) -> bool:
        return self.entry.suffix == ".kcl"

    @property
    def inputs_dir(self) -> Path:
        return self.part_dir / "inputs"

    def stage_file(self, stage: str) -> Path:
        return self.results_dir / f"{stage}.json"

    def load_stage(self, stage: str) -> dict[str, Any] | None:
        p = self.stage_file(stage)
        return load_json(p) if p.exists() else None

    def write_stage(self, stage: str, data: dict[str, Any]) -> Path:
        return dump_stage(self.results_dir, stage, dict(data), contract_path=self.contract_path)

    def part_results(self, design: str) -> Path:
        return results_dir(design, backend=self.backend_id)

    def handoff_step(self, design: str) -> Path:
        return self.part_results(design) / "handoff" / f"{design}.step"

    def input_step(self, body: str) -> Path:
        """The STEP a body's placement applies to: its part design's handoff copy, or its catalog solid."""
        p = self.contract.part(body)
        return self.inputs_dir / f"{p.design if p.kind == 'modelled' else p.name}.step"

    def placed_step(self, body: str) -> Path:
        return self.results_dir / "export" / "bodies" / f"{body}.step"

"""Language + Engine + Backend protocols and the shared failure taxonomy."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Protocol, runtime_checkable

# `memory`: the build outgrew the engine memory budget and was killed; the model's failure. `resource`: the machine refused (no
# memory to start, a kill from outside), tooling.
FailureClass = Literal["ok", "transient", "billing", "program", "kernel", "timeout", "resource", "memory", "unknown"]

PROGRAM_CLASSES = frozenset({"program", "kcl"})
BILLING_CLASSES = frozenset({"billing", "credits"})
TOOLING_CLASSES = frozenset({"transient", "timeout", "billing", "credits", "unknown", "resource"})
MEMORY_PHRASE = "exceeded the engine memory budget"


def is_program(cls: str | None) -> bool:
    return cls in PROGRAM_CLASSES


def is_billing(cls: str | None) -> bool:
    return cls in BILLING_CLASSES


def is_tooling(cls: str | None) -> bool:
    return cls in TOOLING_CLASSES and not is_program(cls)


class EngineError(RuntimeError):
    """Any modelling-backend failure. `kind` is a FailureClass; `guard` marks an assert refusal."""

    kind: str = "unknown"
    guard: bool = False

    def __init__(self, message: str, *, kind: str = "unknown", guard: bool = False):
        super().__init__(message)
        self.kind = kind
        self.guard = guard


class BillingError(EngineError):
    def __init__(self, message: str):
        super().__init__(message, kind="billing")


class ProgramError(EngineError):
    def __init__(self, message: str, *, guard: bool = False):
        super().__init__(message, kind="program", guard=guard)


@runtime_checkable
class Language(Protocol):
    id: str
    entry: str
    suffixes: tuple[str, ...]

    def source_files(self, part_dir: Path) -> list[Path]: ...
    def check(self, part_dir: Path, contract: Any) -> dict[str, Any]: ...
    def rewrite_parameter(self, part_dir: Path, name: str, value: float) -> Path: ...
    def parameter_values(self, part_dir: Path, contract: Any) -> dict[str, Any]: ...
    def format_write(self, target: Path) -> Any: ...
    def rules(self) -> str: ...
    def skills(self) -> list[Path]: ...
    def critics(self) -> dict[str, str]: ...


@runtime_checkable
class Engine(Protocol):
    id: str

    def preflight(self) -> dict[str, Any]: ...
    def analyze(self, entry: Path, *, density_kg_m3: float | None = None, timeout: float = 600) -> dict[str, Any]: ...
    def export(
        self,
        entry: Path,
        out_dir: Path,
        fmt: str,
        *,
        deterministic: bool = True,
        timeout: float = 600,
        lock: bool = True,
    ) -> list[Path]: ...
    def classify(self, text_or_exc: Any, *, code: int | None = None) -> FailureClass: ...
    def kernel_patterns(self) -> list[Any]: ...
    def max_concurrency(self) -> int: ...
    def ledger_wrapper(self, argv: list[str], ledger: Path | None) -> int: ...
    def cost(self, ledger_rows: list[dict[str, Any]]) -> dict[str, Any]: ...
    def hints(self) -> str: ...
    def version(self) -> str: ...
    def reset_ledger(self) -> list[dict[str, Any]]: ...
    def engine_calls(self) -> int: ...


@runtime_checkable
class Backend(Protocol):
    id: str
    language: Language
    engine: Engine
    independent_of_evaluator: bool

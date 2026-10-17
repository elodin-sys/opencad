"""WorkerResult: what one worker turn returned, whichever backend ran it (Cursor cad-worker order or Codex thread)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WorkerResult:
    thread_id: str
    exit_code: int
    seconds: float
    commands: int
    usage: dict[str, int]
    run_dir: Path
    result_md: str
    failure: str = ""
    sections: dict[str, str] = field(default_factory=dict)
    network_stalls: list[dict[str, Any]] = field(default_factory=list)
    backend: str = "codex"
    role: str = ""
    model: str = ""
    order_id: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    fallback_from: str | None = None
    usage_mode: str = ""

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.failure

    def summary(self) -> dict[str, Any]:
        from opencad.codex import timeline_summary

        return {
            "backend": self.backend, "role": self.role, "model": self.model, "order_id": self.order_id,
            "thread_id": self.thread_id, "exit_code": self.exit_code, "seconds": round(self.seconds),
            "commands": self.commands, "usage": self.usage, "usage_mode": self.usage_mode, "run_dir": str(self.run_dir), "failure": self.failure,
            "fallback_from": self.fallback_from, "metrics": self.metrics,
            "network_stalls": len(self.network_stalls), "network_wait_seconds": sum(s.get("waited_seconds", 0) for s in self.network_stalls),
            "network_recovered": any(s.get("recovered") for s in self.network_stalls),
            "timeline": timeline_summary(self.run_dir) if self.backend == "codex" else {},
        }

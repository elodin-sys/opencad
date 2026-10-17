"""Per-role worker profiles: Cursor model, wall budget and Codex knobs. Drafts run on DRAFT_MODEL, every other role on WORK_MODEL.

Overrides: OPENCAD_MODEL / OPENCAD_MODEL_<ROLE> (`inherit` gives the Task the parent agent's model), OPENCAD_BUDGET_<ROLE> (seconds),
OPENCAD_CODEX_EFFORT (every role) / OPENCAD_CODEX_EFFORT_<ROLE> (one role, and it wins), OPENCAD_LEAN_TURNS=0 (full-read briefs).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from typing import Any

INHERIT = "inherit"
DRAFT_MODEL = "claude-opus-5-5-max"
WORK_MODEL = "grok-4.7-xhigh-fast"


@dataclass(frozen=True)
class RoleProfile:
    role: str
    model: str
    budget_s: float
    codex_effort: str
    codex_idle_s: float = 300.0
    description: str = ""


_DEFAULTS: dict[str, RoleProfile] = {
    "draft": RoleProfile("draft", DRAFT_MODEL, 900, "medium", description="contract.yaml + brief.md from sources; check-bundle is the critic"),
    "asm-draft": RoleProfile("asm-draft", DRAFT_MODEL, 1500, "high", description="assembly.yaml + brief.md from sources; `assembly check` is the critic"),
    "blockout": RoleProfile("blockout", WORK_MODEL, 600, "low", description="envelope-only KCL; measured by OpenCascade"),
    "plan": RoleProfile("plan", WORK_MODEL, 480, "high", description="read-only construction plan"),
    "model": RoleProfile("model", WORK_MODEL, 2700, "high", description="author main.kcl; the engine is the critic"),
    "retry": RoleProfile("retry", WORK_MODEL, 1200, "high", description="bounded retry on the model thread with measured deltas"),
    "correction": RoleProfile("correction", WORK_MODEL, 900, "medium", description="short targeted correction with exact deltas"),
    "ecr": RoleProfile("ecr", WORK_MODEL, 1800, "high", description="engineering change request on the model thread"),
    "assemble": RoleProfile("assemble", WORK_MODEL, 600, "medium", description="held-out assembly placement (bake-off p95 284 s)"),
    "partition": RoleProfile("partition", WORK_MODEL, 480, "high", description="split a large contract into feature groups"),
    "module": RoleProfile("module", WORK_MODEL, 1200, "medium", description="one feature-group module"),
    "integrate": RoleProfile("integrate", WORK_MODEL, 1200, "high", description="merge modules and re-measure"),
}

ROLES = tuple(_DEFAULTS)


def lean_turns() -> bool:
    """Briefs inline the schema, skills and critic method; OPENCAD_LEAN_TURNS=0 restores the full-read briefs."""
    return os.environ.get("OPENCAD_LEAN_TURNS", "1").lower() not in {"0", "false", "no"}


def profile(role: str) -> RoleProfile:
    base = _DEFAULTS.get(role) or replace(_DEFAULTS["model"], role=role)
    key = role.upper().replace("-", "_")
    model = os.environ.get(f"OPENCAD_MODEL_{key}") or os.environ.get("OPENCAD_MODEL") or base.model
    budget = os.environ.get(f"OPENCAD_BUDGET_{key}")
    effort = os.environ.get(f"OPENCAD_CODEX_EFFORT_{key}") or os.environ.get("OPENCAD_CODEX_EFFORT") or base.codex_effort
    # a max-effort generation can sit silent for minutes; the 300 s watchdog would kill it
    idle = 900.0 if effort == "max" else base.codex_idle_s
    return replace(base, model=model, budget_s=float(budget) if budget else base.budget_s, codex_effort=effort, codex_idle_s=idle)


def budget_for(role: str, timeout: float | None, budget: float | None = None) -> float:
    """The profile budget (or an explicit size-scaled one), capped by an explicit --timeout when the caller gave a smaller one."""
    b = float(budget) if budget is not None else profile(role).budget_s
    return b if timeout is None else min(float(timeout), b)


# turns that scale with the work they are handed: (base, per item, cap); OPENCAD_BUDGET_<ROLE> still overrides the whole budget
SCALED = {"partition": (480.0, 4.0, None), "module": (1200.0, 30.0, None), "integrate": (1200.0, 300.0, None), "correction": (900.0, 60.0, 1800.0),
          "draft": (420.0, 60.0, 900.0), "blockout": (300.0, 10.0, 600.0), "model": (600.0, 20.0, 2700.0), "assemble": (600.0, 120.0, 2400.0)}
# at or below this many acceptance items the blockout turn is folded into the model turn: the corpus's simple parts draft at <= 45
# (fast pair 29-38), its complex ones at >= 52 (gear pair 52, Voron 109, Prusa 174)
SMALL_CONTRACT_ITEMS = 45


def scaled_budget(role: str, size: int, engine: Any = None) -> float:
    """partition: 480 s + 4 s per acceptance item; module: 1200 s + 30 s per owned item; integrate: 1200 s + 300 s per module;
    correction: 900 s + 60 s per failing item, capped at 1800 s; draft: 420 s + 60 s per source file, capped at 900 s (the contract
    does not exist yet); blockout: 300 s + 10 s and model: 600 s + 20 s per acceptance item, capped at 600 s and 2700 s. An engine's
    `turn_factor` (FreeCAD 1.5: every critic run is a freecadcmd export) scales the whole budget, cap included."""
    env = os.environ.get(f"OPENCAD_BUDGET_{role.upper().replace('-', '_')}")
    if env:
        return float(env)
    base, per, cap = SCALED.get(role, (profile(role).budget_s, 0.0, None))
    factor = float(getattr(engine, "turn_factor", 1.0) or 1.0)
    b = (base + per * max(0, int(size))) * factor
    return min(b, cap * factor) if cap else b

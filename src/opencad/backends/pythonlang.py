"""AST hygiene, parameter rewrite and ruff checks shared by the Python backends."""

from __future__ import annotations

import ast
import math
import operator
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

from opencad.paths import NESTED
from opencad.schemas import PartContract


def source_files(part_dir: Path) -> list[Path]:
    root = Path(part_dir)
    return sorted(p for p in root.rglob("*.py") if p.is_file() and ".venv" not in p.parts and p.relative_to(root).parts[0] not in NESTED)


def _parse(p: Path) -> tuple[Path, ast.AST, str]:
    text = p.read_text(encoding="utf-8")
    try:
        return p, ast.parse(text, filename=str(p)), text
    except SyntaxError:
        return p, ast.Module(body=[], type_ignores=[]), text


def _tree(part_dir: Path) -> list[tuple[Path, ast.AST, str]]:
    return [_parse(p) for p in source_files(part_dir)]


def source_limits() -> tuple[int, int]:
    """(lines, numeric literals) a part's sources may hold: OPENCAD_MAX_SOURCE_LINES / _LITERALS, default 4000 / 6000.
    Parametric sources in this repository stay under 2,700 lines and 4,100 literals; a mesh traced into point lists runs to tens
    of thousands and builds a model that needs tens of GB."""
    return int(os.environ.get("OPENCAD_MAX_SOURCE_LINES") or 4000), int(os.environ.get("OPENCAD_MAX_SOURCE_LITERALS") or 6000)


def source_size(trees: list[tuple[Path, ast.AST, str]]) -> dict[str, Any]:
    lines = sum(text.count("\n") + 1 for _, _, text in trees)
    literals = sum(1 for _, tree, _ in trees for n in ast.walk(tree)
                   if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool))
    max_lines, max_literals = source_limits()
    return {"lines": lines, "numeric_literals": literals, "max_lines": max_lines, "max_literals": max_literals,
            "ok": lines <= max_lines and literals <= max_literals}


def source_size_of(files: list[Path]) -> dict[str, Any]:
    return source_size([_parse(Path(p)) for p in files])


def _const_num(node: ast.AST) -> float | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return float(node.value)
    if (
        isinstance(node, ast.UnaryOp)
        and isinstance(node.op, (ast.USub, ast.UAdd))
        and isinstance(node.operand, ast.Constant)
    ):
        v = _const_num(node.operand)
        return None if v is None else (-v if isinstance(node.op, ast.USub) else v)
    return None


_BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow}
_MATH_CONSTS = {"pi": math.pi, "e": math.e, "tau": math.tau}
_MATH_FUNCS = {n: getattr(math, n) for n in ("cos", "sin", "tan", "acos", "asin", "atan", "atan2", "radians", "degrees", "sqrt", "hypot", "exp", "log",
                                              "floor", "ceil", "fabs")}
_BUILTIN_FUNCS = {"abs": abs, "min": min, "max": max}


def _eval_num(node: ast.AST, env: dict[str, float]) -> float | None:
    """Arithmetic over numbers, names bound earlier at module level and `math` constants and functions; anything else is not a parameter value."""
    v = _const_num(node)
    if v is not None:
        return v
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "math":
        return _MATH_CONSTS.get(node.attr)
    if isinstance(node, ast.Call) and not node.keywords:
        f = node.func
        fn = (_MATH_FUNCS.get(f.attr) if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "math"
              else _BUILTIN_FUNCS.get(f.id) if isinstance(f, ast.Name) else None)
        args = [_eval_num(a, env) for a in node.args]
        if fn is None or any(a is None for a in args):
            return None
        try:
            return float(fn(*args))
        except (ArithmeticError, TypeError, ValueError):
            return None
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        x = _eval_num(node.operand, env)
        return None if x is None else (-x if isinstance(node.op, ast.USub) else x)
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        a, b = _eval_num(node.left, env), _eval_num(node.right, env)
        if a is None or b is None:
            return None
        try:
            return float(_BINOPS[type(node.op)](a, b))
        except (ArithmeticError, TypeError, ValueError):
            return None
    return None


def _top_values(tree: ast.AST) -> dict[str, tuple[float, bool]]:
    """Module-level numeric bindings in source order: (value, written as a literal)."""
    out: dict[str, tuple[float, bool]] = {}
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name, value = node.targets[0].id, node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            name, value = node.target.id, node.value
        else:
            continue
        literal = _const_num(value)
        v = literal if literal is not None else _eval_num(value, {k: val for k, (val, _) in out.items()})
        if v is not None:
            out[name] = (v, literal is not None)
    return out


def _top_assigns(tree: ast.AST) -> dict[str, float]:
    return {name: v for name, (v, literal) in _top_values(tree).items() if literal}


def parameter_values(part_dir: Path, contract: PartContract) -> dict[str, Any]:
    """Each contract parameter as a top-level constant. A derived one may be its formula over the stated names (an edit to a
    stated parameter must carry through) and is compared within its tolerance; every other one must be the literal value,
    because edit tests rewrite literals."""
    found: dict[str, tuple[float, bool, str]] = {}
    for p, tree, _ in _tree(part_dir):
        for name, (val, literal) in _top_values(tree).items():
            found[name] = (val, literal, p.name)
    out: dict[str, Any] = {}
    for p in contract.parameters:
        hit = found.get(p.name)
        if hit is None:
            out[p.name] = {"found": False, "expected": p.value, "ok": False}
            continue
        val, literal, fn = hit
        band = max(1e-9, abs(p.value) * 1e-9) if literal else p.tolerance
        row = {"found": True, "value": val, "expected": p.value, "file": fn, "ok": abs(val - p.value) <= band and (literal or p.provenance == "derived")}
        if not literal:
            row["formula"] = True
        out[p.name] = row
    return out


def rewrite_parameter(part_dir: Path, name: str, value: float) -> Path:
    import re

    pat = re.compile(rf"^(\s*){re.escape(name)}\s*(?::[^=]+)?=\s*[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", re.M)
    for p in source_files(part_dir):
        text = p.read_text(encoding="utf-8")
        new, n = pat.subn(lambda m: f"{m.group(1)}{name} = {value}", text, count=1)
        if n:
            p.write_text(new, encoding="utf-8")
            return p
    raise KeyError(name)


def _imports(tree: ast.AST) -> list[str]:
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module.split(".")[0])
    return names


def _calls(tree: ast.AST) -> list[str]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                out.append(fn.id)
            elif isinstance(fn, ast.Attribute):
                out.append(fn.attr)
    return out


def _has_result(tree: ast.AST) -> bool:
    """A module-scope binding of `result`: an assignment or `with ... as result`, also inside module-level with/if/for/try blocks
    (they bind at module scope), never inside a function or class."""
    stack = list(getattr(tree, "body", []))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "result" for t in node.targets):
            return True
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "result":
            return True
        if isinstance(node, (ast.With, ast.AsyncWith)) and any(isinstance(i.optional_vars, ast.Name) and i.optional_vars.id == "result" for i in node.items):
            return True
        for field in ("body", "orelse", "finalbody", "handlers"):
            stack.extend(getattr(node, field, None) or [])
    return False


def _assert_count(tree: ast.AST) -> int:
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))


def hygiene(
    part_dir: Path,
    contract: PartContract,
    *,
    allowed_imports: Iterable[str],
    construction: Iterable[str],
    dialect_token: str,
    forbidden: Iterable[str] = ("show_object", "show"),
) -> dict[str, Any]:
    allowed = set(allowed_imports)
    construction_set = set(construction)
    forbidden_set = set(forbidden)
    trees = _tree(part_dir)
    src_all = "\n".join(t for _, _, t in trees)
    imports: list[str] = []
    calls: list[str] = []
    syntax_ok = True
    has_result = False
    asserts = 0
    for p, tree, text in trees:
        if not tree.body and text.strip():
            try:
                ast.parse(text)
            except SyntaxError:
                syntax_ok = False
        imports.extend(_imports(tree))
        calls.extend(_calls(tree))
        has_result = has_result or _has_result(tree)
        asserts += _assert_count(tree)
    siblings = {p.stem for p, _, _ in trees}  # a decomposed part imports its own params / datum / group modules
    bad_imports = sorted(
        {i for i in imports if i not in allowed and i not in {"__future__", "math", "typing"} and i not in siblings}
    )
    legacy = sorted({c for c in calls if c in forbidden_set})
    ops = sum(1 for c in calls if c in construction_set)
    params = parameter_values(part_dir, contract)
    unused = unused_parameters(part_dir, contract, trees)
    unused_fail = any(not u["ok"] for u in unused.values())
    dialect = bool(syntax_ok and dialect_token in src_all)
    size = source_size(trees)
    ok = bool(
        dialect
        and has_result
        and not bad_imports
        and not legacy
        and all(v["ok"] for v in params.values())
        and ops > 0
        and not unused_fail
        and size["ok"]
    )
    return {
        "settings": dialect_token if dialect else None,
        "kcl_version_2": dialect,
        "dialect_ok": dialect,
        "default_unit_mm": True,
        "unit_ok": True,
        "legacy_v1": legacy,
        "legacy": legacy,
        "imports": imports,
        "forbidden_imports": bad_imports,
        "asserts": asserts,
        "sketch_blocks": ops,
        "feature_ops": ops,
        "construction_ops": {"calls": ops, "has_result": has_result},
        "parameters": params,
        "parameters_ok": all(v["ok"] for v in params.values()),
        "unused_parameters": unused,
        "lines": src_all.count("\n") + 1,
        "numeric_literals": size["numeric_literals"],
        "source_size": size,
        "ok": ok,
    }


def unused_parameters(
    part_dir: Path, contract: PartContract, trees: list[tuple[Path, ast.AST, str]] | None = None
) -> dict[str, Any]:
    trees = trees or _tree(part_dir)
    names_used: set[str] = set()
    defined: dict[str, str] = {}
    for p, tree, _ in trees:
        for name in _top_assigns(tree):
            defined.setdefault(name, p.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                names_used.add(node.id)
    out = {}
    for p in contract.parameters:
        if p.name in names_used:
            continue
        if p.name not in defined:
            continue
        has_edit = p.edit_test is not None
        out[p.name] = {"defined_in": defined[p.name], "edit_test": has_edit, "ok": not has_edit}
    return out



def ruff_exe() -> str:
    """The ruff beside the running interpreter (the pinned one), not whatever `ruff` PATH resolves to: another version formats differently."""
    beside = Path(sys.executable).with_name("ruff")
    return str(beside) if beside.exists() else (shutil.which("ruff") or "ruff")

def ruff_format_check(part_dir: Path) -> dict[str, Any]:
    files = source_files(part_dir)
    if not files:
        return {"ok": False, "findings": [{"error": "no .py files"}]}
    r = subprocess.run(
        [ruff_exe(), "format", "--check", *[str(f) for f in files]], capture_output=True, text=True, timeout=60
    )
    findings = [] if r.returncode == 0 else [{"error": (r.stderr or r.stdout).strip()[:500]}]
    return {"ok": r.returncode == 0, "findings": findings}


def ruff_check(part_dir: Path) -> dict[str, Any]:
    files = source_files(part_dir)
    if not files:
        return {"ok": False, "code": 1, "output": "no .py files"}
    r = subprocess.run([ruff_exe(), "check", *[str(f) for f in files]], capture_output=True, text=True, timeout=60)
    return {"ok": r.returncode == 0, "code": r.returncode, "output": (r.stdout or r.stderr)[:2000]}


def ruff_format_write(target: Path) -> dict[str, Any]:
    r = subprocess.run([ruff_exe(), "format", str(target)], capture_output=True, text=True, timeout=60)
    return {"ok": r.returncode == 0, "output": (r.stdout or r.stderr)[:500]}

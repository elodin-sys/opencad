"""Static checks on KCL source: settings, parameters, legacy dialect, imports, asserts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from opencad.schemas import PartContract

SETTINGS_RE = re.compile(r"@settings\(([^)]*)\)")
LEGACY = ("startSketchOn", "startProfile", "|> line(", "close()", "startProfileAt", "|> extrude(")
IMPORT_RE = re.compile(r"^\s*import\b.*$", re.M)
IMPORT_FILE_RE = re.compile(r'import\b[^"\n]*"([^"]+\.kcl)"')
ASSERT_RE = re.compile(r"\bassert\s*\(")
SKETCH_RE = re.compile(r"\bsketch\s*\(")
IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
ASSIGN_RE = re.compile(r"(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)")
NUMERIC_LIT = re.compile(r"^\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*(mm|cm|m|in|ft|deg|rad|_)?\s*$")
FEATURE_OPS = (
    "extrude(",
    "revolve(",
    "sweep(",
    "loft(",
    "subtract(",
    "union(",
    "intersect(",
    "hole::",
    "fillet(",
    "chamfer(",
    "shell(",
    "pattern",
)
_KEYWORDS = frozenset(
    {
        "export",
        "import",
        "from",
        "as",
        "fn",
        "type",
        "if",
        "else",
        "for",
        "return",
        "true",
        "false",
        "and",
        "or",
        "not",
    }
)


def param_re(name: str) -> re.Pattern[str]:
    return re.compile(
        rf"^(?P<indent>\s*)(?P<export>export\s+)?{re.escape(name)}\s*=\s*"
        rf"(?P<value>-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*(?P<unit>mm|cm|m|in|ft|deg|rad|_)?\s*(?P<comment>//.*)?$",
        re.M,
    )


def mask_strings_and_comments(src: str) -> str:
    """Replace string and // comment contents with spaces, keeping newlines and length."""
    out: list[str] = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if c in ("'", '"'):
            quote = c
            out.append(" ")
            i += 1
            while i < n:
                if src[i] == "\\":
                    out.append(" ")
                    i += 1
                    if i < n:
                        out.append("\n" if src[i] == "\n" else " ")
                        i += 1
                    continue
                if src[i] == quote:
                    out.append(" ")
                    i += 1
                    break
                out.append("\n" if src[i] == "\n" else " ")
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def kcl_files(target: Path) -> list[Path]:
    """Every .kcl in the part, plus files imported (relative) from those modules."""
    target = Path(target)
    start = [target] if target.is_file() else sorted(target.rglob("*.kcl"))
    seen: set[Path] = set()
    out: list[Path] = []
    stack = list(start)
    while stack:
        p = stack.pop()
        try:
            p = p.resolve()
        except OSError:
            continue
        if p in seen or not p.is_file():
            continue
        seen.add(p)
        out.append(p)
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        masked = mask_strings_and_comments(text)
        for m in IMPORT_FILE_RE.finditer(masked):
            stack.append(p.parent / m.group(1))
    return sorted(out, key=lambda x: str(x))


def read_source(target: Path) -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in kcl_files(target))


def main_source(target: Path) -> str:
    target = Path(target)
    return (target if target.is_file() else target / "main.kcl").read_text(encoding="utf-8")


def top_level_assignments(src: str) -> list[dict[str, Any]]:
    """Depth-0 `ident = expr` (optional `export`) after stripping comments and strings."""
    masked = mask_strings_and_comments(src)
    assigns: list[dict[str, Any]] = []
    i, n, depth = 0, len(masked), 0
    while i < n:
        ch = masked[i]
        if ch in "({[":
            depth += 1
            i += 1
            continue
        if ch in ")}]":
            depth = max(0, depth - 1)
            i += 1
            continue
        if depth == 0:
            m = ASSIGN_RE.match(masked, i)
            if m and (i == 0 or not (masked[i - 1].isalnum() or masked[i - 1] == "_")):
                name = m.group(1)
                if name not in _KEYWORDS:
                    expr_start = m.end()
                    j, nest = expr_start, 0
                    while j < n:
                        cj = masked[j]
                        if cj in "({[":
                            nest += 1
                        elif cj in ")}]":
                            nest = max(0, nest - 1)
                        elif cj == "\n" and nest == 0:
                            break
                        j += 1
                    expr = src[expr_start:j].strip()
                    export = src[i : m.start(1)].lstrip().startswith("export")
                    rec: dict[str, Any] = {
                        "name": name,
                        "export": export,
                        "expr": expr,
                        "start": i,
                        "end": j,
                        "lhs_start": m.start(1),
                    }
                    lit = NUMERIC_LIT.match(expr.split("//")[0])
                    if lit:
                        rec["value"] = float(lit.group(1))
                        rec["unit"] = lit.group(2) or ""
                    assigns.append(rec)
                    i = j
                    continue
        i += 1
    return assigns


def _numeric_match(src: str, name: str) -> re.Match[str] | None:
    return param_re(name).search(src)


def parameter_values(src: str, contract: PartContract) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in contract.parameters:
        m = _numeric_match(src, p.name)
        if not m:
            out[p.name] = {"found": False, "ok": False}
            continue
        value = float(m.group("value"))
        unit = m.group("unit") or ""
        ok = abs(value - p.value) <= p.tolerance and (unit == p.unit or (unit in ("", "_") and p.unit in ("", "_")))
        out[p.name] = {
            "found": True,
            "value": value,
            "unit": unit,
            "expected": p.value,
            "expected_unit": p.unit,
            "ok": ok,
        }
    return out


def parameter_values_from_tree(target: Path, contract: PartContract) -> dict[str, dict[str, Any]]:
    files = [(p, p.read_text(encoding="utf-8")) for p in kcl_files(target)]
    out: dict[str, dict[str, Any]] = {}
    for p in contract.parameters:
        found: tuple[Path, re.Match[str]] | None = None
        for path, text in files:
            m = _numeric_match(text, p.name)
            if m:
                found = (path, m)
                break
        if not found:
            out[p.name] = {"found": False, "ok": False}
            continue
        path, m = found
        value = float(m.group("value"))
        unit = m.group("unit") or ""
        ok = abs(value - p.value) <= p.tolerance and (unit == p.unit or (unit in ("", "_") and p.unit in ("", "_")))
        out[p.name] = {
            "found": True,
            "value": value,
            "unit": unit,
            "expected": p.value,
            "expected_unit": p.unit,
            "ok": ok,
            "file": path.name,
        }
    return out


def rewrite_parameter(src: str, name: str, new_value: float) -> str:
    m = _numeric_match(src, name)
    if not m:
        raise KeyError(name)
    unit = m.group("unit") or ""
    comment = f"  {m.group('comment')}" if m.group("comment") else ""
    export = m.group("export") or ""
    line = f"{m.group('indent')}{export}{name} = {new_value:g}{unit}{comment}"
    return src[: m.start()] + line + src[m.end() :]


def rewrite_parameter_in_tree(target: Path, name: str, new_value: float) -> Path:
    """Rewrite a numeric depth-0 parameter in the module that defines it."""
    for path in kcl_files(target):
        text = path.read_text(encoding="utf-8")
        if _numeric_match(text, name):
            path.write_text(rewrite_parameter(text, name, new_value), encoding="utf-8")
            return path
    raise KeyError(name)


def unused_parameters(target: Path, contract: PartContract) -> dict[str, dict[str, Any]]:
    """Contract parameters whose identifier never appears beyond the definition."""
    files = [(p, p.read_text(encoding="utf-8")) for p in kcl_files(target)]
    defined: dict[str, str] = {}
    for path, text in files:
        for a in top_level_assignments(text):
            defined.setdefault(a["name"], path.name)
    blob = "\n".join(mask_strings_and_comments(text) for _, text in files)
    unused: dict[str, dict[str, Any]] = {}
    for p in contract.parameters:
        if p.name not in defined:
            continue
        count = sum(1 for m in IDENT_RE.finditer(blob) if m.group() == p.name)
        # definition is one occurrence; anything else is a reference
        if count <= 1:
            unused[p.name] = {
                "defined_in": defined[p.name],
                "edit_test": p.edit_test is not None,
                "ok": p.edit_test is None,
            }
    return unused


def hygiene(
    target: Path,
    contract: PartContract,
    forbidden_imports: tuple[str, ...] = (
        ".step",
        ".stp",
        ".stl",
        ".ply",
        ".obj",
        ".glb",
        ".gltf",
        ".iges",
        ".igs",
        "reference",
    ),
) -> dict[str, Any]:
    src_all = read_source(target)
    main = main_source(target)
    settings = SETTINGS_RE.search(main)
    settings_text = settings.group(1) if settings else ""
    compact = re.sub(r"\s+", "", settings_text)
    kcl2 = "kclVersion=2.0" in compact
    mm = "defaultLengthUnit=mm" in compact
    imports = IMPORT_RE.findall(src_all)
    bad_imports = [i for i in imports if any(tok in i.lower() for tok in forbidden_imports)]
    legacy_hits = [tok for tok in LEGACY if tok in src_all]
    params = parameter_values_from_tree(target, contract)
    unused = unused_parameters(target, contract)
    unused_fail = any(not u["ok"] for u in unused.values())
    features = sum(src_all.count(op) for op in FEATURE_OPS)
    sketches = len(SKETCH_RE.findall(src_all))
    ok = bool(
        settings
        and kcl2
        and mm
        and not legacy_hits
        and not bad_imports
        and all(v["ok"] for v in params.values())
        and features > 0
        and not unused_fail
    )
    return {
        "settings": settings_text,
        "kcl_version_2": kcl2,
        "default_unit_mm": mm,
        "legacy_v1": legacy_hits,
        "imports": imports,
        "forbidden_imports": bad_imports,
        "asserts": len(ASSERT_RE.findall(src_all)),
        "sketch_blocks": sketches,
        "feature_ops": features,
        "parameters": params,
        "parameters_ok": all(v["ok"] for v in params.values()),
        "unused_parameters": unused,
        "lines": src_all.count("\n") + 1,
        "ok": ok,
        "dialect_ok": kcl2,
        "unit_ok": mm,
        "legacy": legacy_hits,
        "construction_ops": {"sketch_blocks": sketches, "feature_ops": features},
    }

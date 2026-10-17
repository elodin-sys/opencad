#!/usr/bin/env python3
"""Gate checks for .agents/skills: coverage, token budgets, duplication, links,
KCL snippet provenance, dialect, and SKILL.md frontmatter.

Exit code 1 when any gate fails. Artifacts not built yet are reported as SKIP.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources"
SKILLS = ROOT / ".agents" / "skills"
ZOO = "backends/zoo"
SKILL_NAMES = [f"{ZOO}/kcl-docs", f"{ZOO}/kcl-examples", f"{ZOO}/kcl-research", f"{ZOO}/zoo-tooling", "codex-worker"]

# Token caps (chars/4). Directory keys are totals for every .md below them.
BUDGETS: dict[str, int] = {
    f"{ZOO}/kcl-docs/SKILL.md": 1000,
    f"{ZOO}/kcl-docs/language.md": 5000,
    f"{ZOO}/kcl-docs/patterns.md": 4000,
    f"{ZOO}/kcl-docs/std/": 18500,
    f"{ZOO}/kcl-examples/SKILL.md": 1000,
    f"{ZOO}/kcl-examples/index.md": 3500,
    f"{ZOO}/kcl-examples/by-feature.md": 1500,
    f"{ZOO}/kcl-research/SKILL.md": 1000,
    f"{ZOO}/kcl-research/digest.md": 2500,
    f"{ZOO}/zoo-tooling/SKILL.md": 1000,
    f"{ZOO}/zoo-tooling/cli.md": 2000,
    f"{ZOO}/zoo-tooling/mcp.md": 2500,
    f"{ZOO}/zoo-tooling/api.md": 3000,
    "backends/cadquery/SKILL.md": 1000,
    "backends/build123d/SKILL.md": 1000,
    "backends/freecad/SKILL.md": 1000,
    "backends/cadquery/sources.md": 4000,
    "backends/build123d/sources.md": 4000,
    "backends/freecad/sources.md": 4000,
}
NGRAM = 12
FENCE = re.compile(r"```kcl[^\n]*\n(.*?)```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")
REL_LINK = re.compile(r"\]\((?!https?://|mailto:|#)([^)\s]+)\)")
LEGACY = re.compile(r"startSketchOn|startProfile")


def tokens(text: str) -> int:
    return len(text) // 4


def skill_md_files() -> list[Path]:
    return sorted(p for p in SKILLS.rglob("*.md") if p.is_file())


def h1(path: Path) -> str:
    m = re.search(r"^# (.+)$", path.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip() if m else path.stem


class Gate:
    def __init__(self, name: str) -> None:
        self.name = name
        self.problems: list[str] = []
        self.skipped = False
        self.info: list[str] = []

    def fail(self, msg: str) -> None:
        self.problems.append(msg)

    def skip(self, why: str) -> None:
        self.skipped = True
        self.info.append(why)


# ------------------------------------------------------------------ budgets

def gate_budgets() -> Gate:
    g = Gate("budget")
    for key, cap in BUDGETS.items():
        target = SKILLS / key
        if key.endswith("/"):
            files = sorted(target.glob("*.md")) if target.is_dir() else []
            if not files:
                g.skip(f"{key} not built")
                continue
            total = sum(tokens(p.read_text(encoding="utf-8")) for p in files)
            g.info.append(f"{key} {total}/{cap}")
            if total > cap:
                g.fail(f"{key} total {total} tok > cap {cap}")
        else:
            if not target.is_file():
                g.skip(f"{key} not built")
                continue
            n = tokens(target.read_text(encoding="utf-8"))
            g.info.append(f"{key} {n}/{cap}")
            if n > cap:
                g.fail(f"{key} {n} tok > cap {cap}")
    return g


# ------------------------------------------------------------------ dedup

def dedup_units(text: str) -> list[list[str]]:
    """Split into units (fenced block or prose line) of normalised words.

    Inline code is exempt (signatures legitimately share structure); repeats inside one
    fenced block are verbatim source structure and are not counted.
    """
    units: list[list[str]] = []
    pos = 0

    def prose(chunk: str) -> None:
        for line in chunk.split("\n"):
            units.append(re.sub(r"[^a-z0-9]+", " ", INLINE_CODE.sub(" ", line).lower()).split())

    for m in re.finditer(r"```.*?```", text, re.S):
        prose(text[pos : m.start()])
        units.append(re.sub(r"[^a-z0-9]+", " ", m.group(0).lower()).split())
        pos = m.end()
    prose(text[pos:])
    return [u for u in units if u]


def gate_dedup() -> Gate:
    g = Gate("dedup")
    for skill in SKILL_NAMES:
        files = sorted((SKILLS / skill).rglob("*.md")) if (SKILLS / skill).is_dir() else []
        if not files:
            g.skip(f"{skill} not built")
            continue
        seen: dict[tuple[str, ...], tuple[str, int]] = {}
        pair_hits: dict[tuple[str, str], list[str]] = defaultdict(list)
        unit_id = 0
        for p in files:
            rel = str(p.relative_to(SKILLS))
            for w in dedup_units(p.read_text(encoding="utf-8")):
                unit_id += 1
                reported = False
                for i in range(len(w) - NGRAM + 1):
                    gram = tuple(w[i : i + NGRAM])
                    if gram in seen:
                        other, uid = seen[gram]
                        if uid == unit_id:
                            continue
                        if not reported:  # one report per duplicated unit
                            pair_hits[(other, rel)].append(" ".join(gram))
                            reported = True
                    else:
                        seen[gram] = (rel, unit_id)
        for (a, b), grams in pair_hits.items():
            g.fail(f"{skill}: {len(grams)} repeated passage(s) between {a} and {b}; e.g. \"{grams[0]}\"")
    return g


# ------------------------------------------------------------------ links

def gate_links() -> Gate:
    g = Gate("links")
    files = skill_md_files()
    if not files:
        g.skip("no skills built")
        return g
    for p in files:
        text = p.read_text(encoding="utf-8")
        for m in REL_LINK.finditer(text):
            dest = m.group(1).split("#")[0]
            if not dest:
                continue
            if not (p.parent / dest).exists():
                g.fail(f"{p.relative_to(SKILLS)}: broken link {m.group(1)}")
    return g


# ------------------------------------------------------------------ provenance

def source_kcl_blocks() -> list[str]:
    blocks: list[str] = []
    for sub in ("zoo-docs", "zoo-aquarium"):
        for p in (SRC / sub).rglob("*.md"):
            for b in FENCE.findall(p.read_text(encoding="utf-8", errors="replace")):
                blocks.append(re.sub(r"\s+", "", b))
    return blocks


def gate_provenance() -> Gate:
    g = Gate("provenance")
    files = skill_md_files()
    if not files:
        g.skip("no skills built")
        return g
    blocks = source_kcl_blocks()
    joined = "\n".join(blocks)
    checked = 0
    for p in files:
        for b in FENCE.findall(p.read_text(encoding="utf-8")):
            norm = re.sub(r"\s+", "", b)
            if not norm:
                continue
            checked += 1
            if norm not in joined:
                g.fail(f"{p.relative_to(SKILLS)}: kcl block not found verbatim in sources: {b.strip().splitlines()[0][:70]}")
    g.info.append(f"{checked} kcl blocks checked against {len(blocks)} source blocks")
    return g


# ------------------------------------------------------------------ dialect

def gate_dialect() -> Gate:
    g = Gate("dialect")
    files = skill_md_files()
    if not files:
        g.skip("no skills built")
        return g
    for p in files:
        heading = ""
        for n, line in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
            if line.startswith("#"):
                heading = line
            if LEGACY.search(line):
                allowed = re.search(r"legacy|deprecated|v1", heading, re.I) or "!dep" in line or "legacy" in line.lower()
                if not allowed:
                    g.fail(f"{p.relative_to(SKILLS)}:{n}: legacy sketch API outside a legacy section")
    return g


# ------------------------------------------------------------------ frontmatter

def gate_frontmatter() -> Gate:
    g = Gate("frontmatter")
    any_found = False
    for skill in SKILL_NAMES:
        p = SKILLS / skill / "SKILL.md"
        if not p.is_file():
            g.skip(f"{skill}/SKILL.md not built")
            continue
        any_found = True
        text = p.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
        if not m:
            g.fail(f"{skill}: missing frontmatter")
            continue
        fm, body = m.group(1), m.group(2)
        name = re.search(r"^name:\s*(.+)$", fm, re.M)
        desc = re.search(r"^description:\s*(.+?)(?=^\w+:|\Z)", fm, re.M | re.S)
        if not name or not re.fullmatch(r"[a-z0-9-]{1,64}", name.group(1).strip()):
            g.fail(f"{skill}: invalid name")
        elif name.group(1).strip() != Path(skill).name:
            g.fail(f"{skill}: name {name.group(1).strip()} != directory")
        if not desc:
            g.fail(f"{skill}: missing description")
        else:
            d = " ".join(desc.group(1).replace(">-", "").split())
            if not d or len(d) > 1024:
                g.fail(f"{skill}: description empty or > 1024 chars")
            if re.search(r"\bI\b|\byou can use\b|\bI can\b", d):
                g.fail(f"{skill}: description not third person")
            if not re.search(r"\buse when\b|\bwhen\b", d, re.I):
                g.fail(f"{skill}: description lacks a WHEN trigger clause")
        if body.count("\n") >= 500:
            g.fail(f"{skill}: body >= 500 lines")
    if not any_found:
        g.skipped = True
    return g


# ------------------------------------------------------------------ coverage

def gate_coverage_std() -> Gate:
    g = Gate("coverage:std")
    out = SKILLS / ZOO / "kcl-docs" / "std"
    if not (out / "index.md").is_file():
        g.skip("kcl-docs/std not built")
        return g
    index = (out / "index.md").read_text(encoding="utf-8")
    pages = {p.stem: p.read_text(encoding="utf-8") for p in out.glob("*.md") if p.stem != "index"}

    def entry_count(text: str, name: str) -> int:
        """Entries are `- `name`...` lines or names inside `- !dep:` / `- consts:` lists."""
        n = len(re.findall(rf"^- `{re.escape(name)}`", text, re.M))
        for line in re.findall(r"^- (?:!dep|consts): .*$", text, re.M):
            n += len(re.findall(rf"`{re.escape(name)}`", line))
        return n

    fn_pages = sorted((SRC / "zoo-docs/kcl-std/functions").glob("*.md"))
    for p in fn_pages:
        name = h1(p)
        parts = p.stem.split("-")
        mod = parts[1] if len(parts) > 2 else "std"
        short = name.split("::")[-1]
        n_idx = entry_count(index, name)
        if n_idx != 1:
            g.fail(f"index.md: `{name}` appears {n_idx}x (want 1)")
        page = pages.get(mod)
        if page is None:
            g.fail(f"module page {mod}.md missing for {name}")
            continue
        n_head = len(re.findall(rf"^### {re.escape(short)}(?: |$)", page, re.M))
        n_list = len(re.findall(rf"^## (?:Deprecated|Sketch v1).*`{re.escape(name)}`", page, re.M))
        if n_head + n_list != 1:
            g.fail(f"{mod}.md: `{name}` defined {n_head + n_list}x (want 1)")

    types_page = pages.get("types", "")
    for p in sorted((SRC / "zoo-docs/kcl-std/types").glob("*.md")):
        name = h1(p)
        n = len(re.findall(rf"^- `{re.escape(name)}`", types_page, re.M))
        if n != 1:
            g.fail(f"types.md: `{name}` appears {n}x (want 1)")
    for p in sorted((SRC / "zoo-docs/kcl-std/consts").glob("*.md")):
        name = h1(p)
        parts = p.stem.split("-")
        mod = parts[1] if len(parts) > 2 else "std"
        n_idx = entry_count(index, name)
        # Module pages list consts as `- `NAME: Type`: desc` or grouped `- `A: T`, `B: T`: desc`.
        n_mod = len(re.findall(rf"^- (?:`[^`\n]*`, )*`{re.escape(name)}(?::| |`)", pages.get(mod, ""), re.M))
        if n_idx != 1 or n_mod != 1:
            g.fail(f"const `{name}`: index {n_idx}x, {mod}.md {n_mod}x (want 1/1)")
    g.info.append(f"{len(fn_pages)} functions, {len(list((SRC / 'zoo-docs/kcl-std/types').glob('*.md')))} types, "
                  f"{len(list((SRC / 'zoo-docs/kcl-std/consts').glob('*.md')))} consts checked")
    return g


def gate_coverage_examples() -> Gate:
    g = Gate("coverage:examples")
    out = SKILLS / ZOO / "kcl-examples"
    if not (out / "index.md").is_file():
        g.skip("kcl-examples not built")
        return g
    index = (out / "index.md").read_text(encoding="utf-8")
    n_samples = n_files = 0
    for p in sorted((SRC / "zoo-aquarium").glob("*.md")):
        if p.name == "index.md":
            continue
        text = p.read_text(encoding="utf-8")
        files = re.findall(r"^### (\S+\.kcl)$", text, re.M)
        if not files:
            continue
        n_samples += 1
        slug = p.stem
        n = len(re.findall(rf"^- `{re.escape(slug)}`", index, re.M))
        if n != 1:
            g.fail(f"index.md: sample {slug} appears {n}x (want 1)")
        for f in files:
            n_files += 1
            if not (out / "samples" / slug / f).is_file():
                g.fail(f"samples/{slug}/{f} missing")
    for line in index.split("\n"):
        if line.startswith("- `") and tokens(line) > 30:
            g.fail(f"index.md line over 30 tokens: {line[:60]}")
    g.info.append(f"{n_samples} samples, {n_files} kcl files checked")
    return g


def rest_endpoints() -> list[tuple[str, str, str]]:
    """(method, path, page) for every REST endpoint page in sources."""
    found: list[tuple[str, str, str]] = []
    for p in sorted((SRC / "zoo-docs/developer-tools/api").rglob("*.md")):
        if p.name in ("index.md", "authentication.md", "errors.md"):
            continue
        text = p.read_text(encoding="utf-8")
        m = re.search(r"^`(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD) (/\S*)`", text, re.M)
        if not m:
            m2 = re.search(r"^(get|post|put|delete|patch|options|head)\n\n(/[^\s]*?)(?:curl|$)", text, re.M | re.I)
            if not m2:
                continue
            found.append((m2.group(1).upper(), m2.group(2).strip(), str(p.relative_to(SRC))))
            continue
        found.append((m.group(1), m.group(2), str(p.relative_to(SRC))))
    return found


def gate_coverage_tooling() -> Gate:
    g = Gate("coverage:tooling")
    out = SKILLS / ZOO / "zoo-tooling"
    cli, api, mcp = out / "cli.md", out / "api.md", out / "mcp.md"
    if not (cli.is_file() and api.is_file() and mcp.is_file()):
        g.skip("zoo-tooling not built")
        return g
    cli_text = cli.read_text(encoding="utf-8")
    for p in sorted((SRC / "zoo-docs/developer-tools/cli/manual").glob("*.md")):
        if p.name == "index.md":
            continue
        cmd = h1(p)
        if not re.search(r"`" + re.escape(cmd) + r"(?:[` ])", cli_text):
            g.fail(f"cli.md: `{cmd}` missing")
    api_text = api.read_text(encoding="utf-8")
    eps = rest_endpoints()
    seen: set[tuple[str, str]] = set()
    for method, path, page in eps:
        key = (method, path)
        if key in seen:
            continue
        seen.add(key)
        n = len(re.findall(r"^- `" + re.escape(f"{method} {path.replace(chr(92) + '_', '_')}") + r"`", api_text, re.M))
        if n != 1:
            g.fail(f"api.md: `{method} {path}` appears {n}x as an entry (want 1) [{page}]")
    server = SRC / "github/kittycad-mcp/server.py"
    tools = re.findall(r"@mcp\.tool\(\)\s*\nasync def ([a-z_0-9]+)\(", server.read_text(encoding="utf-8"))
    mcp_text = mcp.read_text(encoding="utf-8")
    for t in tools:
        n = len(re.findall(r"^- `" + re.escape(t) + r"\(", mcp_text, re.M))
        if n != 1:
            g.fail(f"mcp.md: `{t}` appears {n}x as an entry (want 1)")
    g.info.append(f"{len(seen)} endpoints, {len(tools)} MCP tools checked")
    return g


def _exec_python_example(path: Path, timeout: float = 30) -> str | None:
    """Run a fetched example with show_object stubbed. Return an error string or None."""
    import subprocess
    import sys

    stub = (
        "import sys, types\n"
        "def _show(*a, **k):\n    return None\n"
        "m = types.ModuleType('ocp_vscode')\n"
        "m.show = m.show_all = m.show_object = _show\n"
        "sys.modules['ocp_vscode'] = m\n"
        f"p = {str(path)!r}\n"
        "src = open(p, encoding='utf-8').read()\n"
        "ns = {'__name__': '__ex__', '__file__': p, 'show_object': _show, 'show': _show, 'show_all': _show}\n"
        "exec(compile(src, p, 'exec'), ns, ns)\n"
    )
    r = subprocess.run([sys.executable, "-c", stub], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        return (r.stderr or r.stdout or "exit 1")[:240]
    return None


def gate_backend_examples() -> Gate:
    """Fetched examples must compile; a sample must execute on the pinned interpreter."""
    g = Gate("backend-examples")
    for bid in ("cadquery", "build123d", "freecad"):
        skill = SKILLS / "backends" / bid / "SKILL.md"
        if not skill.is_file():
            g.fail(f"backends/{bid}/SKILL.md missing")
            continue
        src = SRC / bid
        examples = []
        if src.exists():
            examples = sorted(set(src.rglob("Ex*.py")) | set((src / "examples").glob("*.py")))
        wiki = list((src / "wiki").glob("*")) if (src / "wiki").exists() else []
        if bid == "freecad":
            if not wiki:
                g.skip(f"{bid} wiki not fetched")
            else:
                g.info.append(f"{bid}: {len(wiki)} wiki pages")
            continue
        if not examples:
            g.skip(f"{bid} examples not fetched")
            continue
        compiled = 0
        for p in examples:
            try:
                compile(p.read_text(encoding="utf-8", errors="replace"), str(p), "exec")
                compiled += 1
            except SyntaxError as e:
                g.fail(f"{bid} {p.name}: syntax {e}")
        preferred = [p for p in examples if "algebra" in p.name or p.name.startswith("Ex00")]
        preferred += [p for p in examples if p.stat().st_size < 2500]
        tried: list[Path] = []
        ran = 0
        for p in preferred + examples:
            if p in tried:
                continue
            tried.append(p)
            if ran >= 2 or len(tried) >= 16:
                break
            try:
                err = _exec_python_example(p)
            except Exception as e:
                err = str(e)[:240]
            if err:
                g.info.append(f"{bid} exec skip {p.name}: {err.splitlines()[0][:120]}")
            else:
                ran += 1
        g.info.append(f"{bid}: {compiled}/{len(examples)} compile, {ran} exec ok")
        if compiled == 0:
            g.fail(f"{bid}: no example compiled")
        if ran == 0 and examples:
            g.fail(f"{bid}: no fetched example executed on the pinned interpreter")
    return g


# ------------------------------------------------------------------ report

def token_report() -> None:
    print("\nToken report (chars/4):")
    for skill in SKILL_NAMES:
        d = SKILLS / skill
        if not d.is_dir():
            continue
        files = sorted(p for p in d.rglob("*.md"))
        total = 0
        rows = []
        for p in files:
            n = tokens(p.read_text(encoding="utf-8"))
            total += n
            rows.append((str(p.relative_to(d)), n))
        print(f"  {skill}: {total} tok in {len(files)} files")
        for rel, n in rows:
            if n >= 300 or rel == "SKILL.md":
                print(f"    {n:6d}  {rel}")
        std_dir = d / "std"
        if std_dir.is_dir():
            small = sum(n for rel, n in rows if rel.startswith("std/") and n < 300)
            print(f"    {small:6d}  std/ (pages under 300 tok, summed)")


def main() -> int:
    gates = [
        gate_frontmatter(),
        gate_budgets(),
        gate_dedup(),
        gate_links(),
        gate_provenance(),
        gate_dialect(),
        gate_coverage_std(),
        gate_coverage_examples(),
        gate_coverage_tooling(),
        gate_backend_examples(),
    ]
    failed = False
    for g in gates:
        status = "FAIL" if g.problems else ("SKIP" if g.skipped and not g.info else "PASS")
        if g.skipped and g.info and not g.problems:
            status = "PASS*"
        print(f"[{status}] {g.name}" + (f"  ({'; '.join(g.info[:3])})" if g.info else ""))
        for msg in g.problems[:12]:
            print(f"    - {msg}")
        if len(g.problems) > 12:
            print(f"    ... {len(g.problems) - 12} more")
        failed |= bool(g.problems)
    token_report()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

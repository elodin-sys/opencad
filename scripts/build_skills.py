#!/usr/bin/env python3
"""Generate the machine-built parts of the Cursor skills from sources/.

Usage: build_skills.py [std] [examples] [tooling]   (default: all)
"""

from __future__ import annotations

import html as html_lib
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources"
DOCS = SRC / "zoo-docs"
STD = DOCS / "kcl-std"
SKILLS = ROOT / ".agents" / "skills"
ZOO_SKILLS = SKILLS / "backends" / "zoo"

LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
FENCE = re.compile(r"```kcl[^\n]*\n(.*?)```", re.S)
WARN = re.compile(r"\*\*WARNING:\*\* This (?:function|type|constant) is (deprecated|experimental)[^\n]*")
SENTENCE_END = re.compile(r"(?<=[.!?])(?<!i\.e\.)(?<!e\.g\.)\s+(?=[A-Z`\[])")
EXAMPLE_REF = re.compile(r"\bexamples?\b|\bbelow\b|\babove\b|\bhere,|\bthis is the same shape", re.I)
FACE_API = re.compile(
    r"Experimental face API: .*?(?:ships|yet)\.|Edge specifier objects \(`\{[^`]*`\) are experimental; do not use them in generated or user-facing KCL yet\."
    r"|\*\*Experimental\.\*\* Experimental face API\. Do not use in generated or user-facing KCL yet; prefer `tags` until point-and-click and migration support ships\.",
    re.S,
)
REMOVED_ARG = re.compile(r"Removed in KCL 3\.0|Deprecated as of KCL 2\.0|\*\*Deprecated\.\*\*")
SOFT_DEP = re.compile(
    r"This\s+is\s+part\s+of\s+sketch\s+v1\s+and\s+is\s+soft\s+deprecated\s+in\s+favor\s+of\s+sketch-solve\.?\s*"
    r"(?:The\s+sketch-solve\s+version\s+of\s+\w+\s+is\s+still\s+under\s+development\.?)?"
)
# Arg descriptions are kept only when they add semantics beyond the parameter name.
ARG_SIGNAL = re.compile(
    r"incompatible|requires?|default|\bonly\b|must|\bif\b|unless|otherwise|when omitted|experimental|"
    r"deprecated|relative|absolute|degrees|radians|\bunits?\b|`|==|\d|\bnot\b|instead|e\.g\.|i\.e\.|"
    r"between|clockwise|positive|negative|percent|inclusive|exclusive|guess|\[",
    re.I,
)
# Note sentences survive only when they carry KCL-specific behaviour, not textbook definitions.
NOTE_SIGNAL = re.compile(
    r"`|\d|\bmust\b|\berror|cannot|n't\b|\bonly\b|incompatible|consum|default|\bnot\b|instead|"
    r"requir|deprecated|experimental|currently|\bfree\b|\bfixed\b|suggest|prefer|avoid|==|"
    r"\binto\b|without|merge|union|subtract|extend|\bcut",
    re.I,
)
STANDARDS_PROSE = re.compile(r"\bASME\b|\bISO\b|Y14\.5")
FACE_API_NOTE = (
    "[face-api] Edge-specifier objects `{ sideFaces, endFaces?, index? }` are experimental; "
    "use tags, edgeId(...), or the listed geometry types instead."
)


def tokens(text: str) -> int:
    return len(text) // 4


def strip_links(text: str) -> str:
    return LINK.sub(r"\1", text)


def first_sentence(text: str) -> str:
    text = " ".join(text.split())
    parts = SENTENCE_END.split(text, maxsplit=1)
    return parts[0].strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)} ({tokens(text)} tok)")


# --------------------------------------------------------------------------- std

@dataclass
class Arg:
    name: str
    type: str
    desc: str
    required: bool


@dataclass
class Fn:
    name: str
    module: str
    summary: str
    signature: str
    args: list[Arg] = field(default_factory=list)
    returns: str = ""
    notes: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    deprecated: bool = False
    experimental: bool = False
    soft_deprecated: bool = False


def module_of(stem: str) -> str:
    parts = stem.split("-")
    return parts[1] if len(parts) > 2 else "std"


def body_after_header(text: str) -> str:
    # Drop provenance header and H1.
    lines = text.split("\n")
    i = next(k for k, l in enumerate(lines) if l.startswith("# "))
    return "\n".join(lines[i + 1 :])


def one_line_signature(sig: str) -> str:
    s = " ".join(sig.split())
    s = s.replace("( ", "(").replace(", )", ")").replace(" )", ")")
    s = s.replace(" | ", "|")
    return s


def parse_table(section: str) -> list[Arg]:
    args: list[Arg] = []
    for line in section.split("\n"):
        if not line.startswith("|") or set(line.strip()) <= {"|", "-", " "}:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] == "Name":
            continue
        name = cells[0].strip("`")
        typ = strip_links(cells[1]).replace(" or ", "|")
        desc = strip_links(cells[2])
        args.append(Arg(name, typ, desc, cells[3].lower().startswith("yes")))
    return args


def parse_function(path: Path) -> Fn:
    text = path.read_text(encoding="utf-8")
    name = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    body = body_after_header(text)
    deprecated = "This function is deprecated" in body
    experimental = "This function is experimental" in body
    body = WARN.sub("", body)

    m = FENCE.search(body)
    signature = one_line_signature(m.group(1))
    pre, post = body[: m.start()], body[m.end() :]
    summary = first_sentence(strip_links(pre.strip().split("\n\n")[0])) if pre.strip() else ""

    def section(title: str) -> str:
        mm = re.search(rf"^### {title}\n(.*?)(?=^### |\Z)", post, re.S | re.M)
        return mm.group(1) if mm else ""

    notes_text = re.split(r"^### ", post, maxsplit=1, flags=re.M)[0]
    notes_text = FENCE.sub("", notes_text)
    notes_text = re.sub(r"<model-viewer.*?</model-viewer>", "", notes_text, flags=re.S)
    notes_text = strip_links(notes_text)
    notes = []
    soft = bool(SOFT_DEP.search(notes_text))
    notes_text = SOFT_DEP.sub("", notes_text)
    for p in notes_text.strip().split("\n\n"):
        p = " ".join(p.split())
        # Skip empties, flattened tables/lists, and paragraphs that introduce a dropped list.
        if not p or "| " in p or p.startswith("- ") or p.endswith(":"):
            continue
        kept = [
            s for s in SENTENCE_END.split(p)
            if not EXAMPLE_REF.search(s) and NOTE_SIGNAL.search(s) and not STANDARDS_PROSE.search(s)
        ]
        if kept:
            notes.append(" ".join(kept))
        if len(notes) == 2:
            break
    args = parse_table(section("Arguments"))
    for a in args:
        a.desc = FACE_API.sub("[face-api]", a.desc)
    ret = section("Returns").strip()
    returns = strip_links(ret.split("\n")[0]).strip() if ret else ""
    examples = [b.strip("\n") for b in FENCE.findall(section("Examples"))]
    return Fn(name, module_of(path.stem), summary, signature, args, returns, notes, examples, deprecated, experimental, soft)


def arg_note(a: Arg) -> str:
    desc = " ".join(a.desc.split())
    if not desc or desc.endswith("?") and len(desc.split()) <= 10:
        return ""
    if REMOVED_ARG.search(desc):
        return "!dep, removed in KCL 3; do not set"
    sentences = SENTENCE_END.split(desc)
    kept = [
        s for s in sentences
        if (ARG_SIGNAL.search(s) or s.startswith("[")) and " - `" not in s and not s.endswith(":")
    ]
    note = " ".join(kept).strip()
    return note if len(note.split()) > 3 or note.startswith("[") else ""


def parse_simple(path: Path, kind: str) -> dict:
    text = path.read_text(encoding="utf-8")
    name = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    body = WARN.sub("", body_after_header(text))
    experimental = f"This {kind} is experimental" in text
    sig = FENCE.search(body)
    signature = one_line_signature(sig.group(1)) if sig else ""
    prose = FENCE.sub("", body)
    paragraphs = [p for p in prose.strip().split("\n\n") if p.strip() and not p.strip().startswith("#")]
    summary = " ".join(strip_links(paragraphs[0]).split()) if paragraphs else ""
    return {"name": name, "summary": summary, "signature": signature, "experimental": experimental, "stem": path.stem}


def is_kcl2(code: str) -> bool:
    return "startSketchOn" not in code and "startProfile" not in code


def pick_example(fn: Fn, max_lines: int, guard: "NgramGuard | None" = None) -> str | None:
    candidates = [e for e in fn.examples if is_kcl2(e) and fn.name.split("::")[-1] in e]
    candidates = [e for e in candidates if len(e.split("\n")) <= max_lines]
    for e in sorted(candidates, key=len):
        if guard is None or guard.admit(e):
            return e
    return None


def clean_desc(desc: str, shared: dict[str, str]) -> str:
    desc = " ".join(desc.split())
    for sentence, tag in shared.items():
        desc = desc.replace(sentence, f"[{tag}]")
    desc = re.sub(r"\s+", " ", desc).strip()
    return desc


def build_std() -> None:
    fns = [parse_function(p) for p in sorted(STD.glob("functions/*.md"))]
    consts = [parse_simple(p, "constant") for p in sorted(STD.glob("consts/*.md"))]
    types = [parse_simple(p, "type") for p in sorted(STD.glob("types/*.md"))]
    modules: dict[str, str] = {}
    for p in sorted(STD.glob("modules/*.md")):
        mod = p.stem.replace("std-", "", 1) if p.stem != "std" else "std"
        body = body_after_header(p.read_text(encoding="utf-8"))
        modules[mod] = first_sentence(strip_links(body.strip().split("\n\n")[0]))

    by_mod: dict[str, list[Fn]] = defaultdict(list)
    for fn in fns:
        by_mod[fn.module].append(fn)
    const_mod: dict[str, list[dict]] = defaultdict(list)
    for c in consts:
        const_mod[module_of(c["stem"])].append(c)

    # Arg-description sentences repeated in 2+ modules get one global note in index.md.
    sentence_mods: dict[str, set[str]] = defaultdict(set)
    for fn in fns:
        if fn.deprecated or fn.soft_deprecated:
            continue
        for a in fn.args:
            for s in SENTENCE_END.split(" ".join(a.desc.split())):
                if len(s.split()) >= 8:
                    sentence_mods[s.strip()].add(fn.module)
    shared: dict[str, str] = {}
    for s, mods_using in sentence_mods.items():
        if len(mods_using) >= 2:
            shared[s] = f"n{len(shared) + 1}"

    # Within a module: identical (arg, description) in 3+ functions and identical note
    # paragraphs in 2+ functions are hoisted to the module header.
    common_args: dict[str, dict[tuple[str, str], int]] = defaultdict(dict)
    common_notes: dict[str, dict[str, list[str]]] = defaultdict(dict)
    for mod, mod_fns in by_mod.items():
        ac: dict[tuple[str, str], int] = defaultdict(int)
        nc: dict[str, list[str]] = defaultdict(list)
        for fn in mod_fns:
            if fn.deprecated or fn.soft_deprecated:
                continue
            for a in fn.args:
                ac[(a.name, clean_desc(arg_note(a), shared))] += 1
            for n in fn.notes:
                nc[n].append(fn.name.split("::")[-1])
        common_args[mod] = {k: v for k, v in ac.items() if v >= 3 and k[1]}
        common_notes[mod] = {k: v for k, v in nc.items() if len(v) >= 2}

    out = ZOO_SKILLS / "kcl-docs" / "std"
    order = ["std", "sketch", "solver", "solid", "sweep", "hole", "transform", "array", "math", "units",
             "vector", "string", "gdt", "gear", "appearance", "view", "operation", "runtime", "turns", "types"]
    mods = [m for m in order if m in by_mod or m in const_mod or m == "types"]

    # index.md
    idx = [
        "# KCL std index",
        "",
        "One line per item: `name: gist`. Typed signatures, arg notes, examples: `std/<module>.md`.",
        "Full page: `zoo.dev/docs/kcl-std/functions/std-<module>-<name>` (root module: `std-<name>`).",
        "`solver::*` is in scope unprefixed inside `sketch(on = …) { }`; other prefixed modules are called as written (`module::name`).",
        "Flags: `!dep` deprecated sketch-v1 API (recognise, never write); `!v1soft` sketch-v1 form, solver version pending; `!exp` experimental, needs `@settings(experimentalFeatures = allow)`.",
        FACE_API_NOTE,
    ]
    if shared:
        idx += ["", "Shared arg notes (referenced as [nN] in module pages):"] + [f"- [{tag}] {s}" for s, tag in shared.items()]
    for mod in mods:
        if mod == "types":
            continue
        idx += ["", f"## {mod}"]
        if const_mod.get(mod):
            idx.append("- consts: " + ", ".join(f"`{c['name']}`" for c in const_mod[mod]))
        dep = [fn for fn in by_mod.get(mod, []) if fn.deprecated]
        for fn in by_mod.get(mod, []):
            if fn.deprecated:
                continue
            flag = (" !exp" if fn.experimental else "") + (" !v1soft" if fn.soft_deprecated else "")
            idx.append(f"- `{fn.name}`{flag}: {short_gist(fn.summary)}")
        if dep:
            idx.append("- !dep: " + ", ".join(f"`{fn.name}`" for fn in dep))
    idx += ["", "## types: see `std/types.md`"]
    write(out / "index.md", "\n".join(idx))

    # module pages
    guard = NgramGuard()
    guard.record("\n".join(idx))
    for mod in mods:
        if mod == "types":
            continue
        lines = [f"# std::{mod}" if mod != "std" else "# std (root)"]
        if mod in modules and mod != "std":
            lines.append(modules[mod])
        for n, users in common_notes[mod].items():
            lines.append(f"{', '.join(users)}: {n}" if len(users) < len(by_mod[mod]) else n)
        lines += const_lines(const_mod.get(mod, []))
        common_tail, signatures = factor_common_params(by_mod.get(mod, []))
        if common_tail:
            lines += ["", "`…common` = " + ", ".join(common_tail)]
        if common_args[mod]:
            lines += ["", "Common args:"]
            for (name, desc), _ in sorted(common_args[mod].items()):
                lines.append(f"- {name}: {desc}")
        guard.record("\n".join(lines))
        for fn in by_mod.get(mod, []):
            if fn.deprecated or fn.soft_deprecated:
                continue
            flags = " !exp" if fn.experimental else ""
            lines.append(f"### {fn.name.split('::')[-1]}{flags}")
            lines.append(f"`{signatures[fn.name]}`")
            for n in fn.notes:
                if n not in common_notes[mod]:
                    kept = guard.admit_line("", n)
                    if kept:
                        lines.append(kept)
            for a in fn.args:
                d = clean_desc(arg_note(a), shared)
                if d and (a.name, d) not in common_args[mod]:
                    kept = guard.admit_line(a.name, d)
                    if kept:
                        lines.append(f"- {a.name}: {kept}")
            ex = pick_example(fn, max_lines=12, guard=guard)
            if ex:
                lines += ["```kcl", ex, "```"]
        soft = [fn for fn in by_mod.get(mod, []) if fn.soft_deprecated]
        if soft:
            lines += ["", "## Sketch v1 only, solver version pending (!v1soft): " + ", ".join(f"`{fn.name}`" for fn in soft)]
        dep = [fn for fn in by_mod.get(mod, []) if fn.deprecated]
        if dep:
            lines += ["", "## Deprecated sketch v1 (!dep; recognise in old code, never write): " + ", ".join(f"`{fn.name}`" for fn in dep)]
        write(out / f"{mod}.md", "\n".join(lines))

    # types.md
    lines = ["# std::types", "", "Type names usable in signatures and `fn` parameter annotations."]
    for t in types:
        flag = " !exp" if t["experimental"] else ""
        lines.append(f"- `{t['name']}`{flag}: {t['summary']}")
    write(out / "types.md", "\n".join(lines))


def split_params(signature: str) -> tuple[str, list[str], str]:
    """'f(a: T, b?: U): R' -> ('f', ['a: T', 'b?: U'], ': R')."""
    open_i = signature.index("(")
    depth = 0
    for i in range(open_i, len(signature)):
        ch = signature[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                close_i = i
                break
    head, inner, tail = signature[:open_i], signature[open_i + 1 : close_i], signature[close_i + 1 :]
    params, depth, cur = [], 0, ""
    for ch in inner:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            params.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        params.append(cur.strip())
    return head, params, tail


def factor_common_params(fns: list[Fn]) -> tuple[list[str], dict[str, str]]:
    """Optional params shared by 4+ functions in a module become one `…common` tail."""
    live = [fn for fn in fns if not fn.deprecated and not fn.soft_deprecated]
    if len(live) < 4:
        return [], {fn.name: fn.signature for fn in fns}
    counts: dict[str, int] = defaultdict(int)
    for fn in live:
        for p in split_params(fn.signature)[1]:
            if "?" in p.split(":")[0]:
                counts[p] += 1
    candidate = {p for p, n in counts.items() if n >= 4}
    param_sets = {fn.name: set(split_params(fn.signature)[1]) for fn in live}
    # Shrink by least-frequent param; keep the set that saves the most signature text.
    best: tuple[int, set[str]] = (0, set())
    while len(candidate) >= 3:
        carriers = [n for n, ps in param_sets.items() if candidate <= ps]
        saved = len(carriers) * sum(len(p) for p in candidate) if len(carriers) >= 4 else 0
        if saved > best[0]:
            best = (saved, set(candidate))
        candidate.remove(min(candidate, key=lambda p: counts[p]))
    common_set = best[1]
    if len(common_set) < 3 or best[0] < 600:
        return [], {fn.name: fn.signature for fn in fns}
    out: dict[str, str] = {}
    ordered: list[str] = []
    for fn in fns:
        head, params, tail = split_params(fn.signature)
        if common_set <= set(params):
            if not ordered:
                ordered = [p for p in params if p in common_set]
            params = [p for p in params if p not in common_set] + ["…common"]
        out[fn.name] = f"{head}({', '.join(params)}){tail}"
    return ordered, out


class NgramGuard:
    """Admits text only if it shares no 12-gram with text admitted before."""

    def __init__(self, n: int = 12) -> None:
        self.n = n
        self.seen: set[tuple[str, ...]] = set()

    @staticmethod
    def words(text: str) -> list[str]:
        text = re.sub(r"`[^`\n]*`", " ", text)  # inline code is exempt, as in check_skills
        return re.sub(r"[^a-z0-9]+", " ", text.lower()).split()

    def grams(self, text: str) -> set[tuple[str, ...]]:
        w = self.words(text)
        return {tuple(w[i : i + self.n]) for i in range(len(w) - self.n + 1)}

    def admit(self, text: str) -> bool:
        g = self.grams(text)
        if g & self.seen:
            return False
        self.seen |= g
        return True

    def admit_line(self, prefix: str, text: str) -> str:
        """Longest leading run of sentences that, with `prefix`, repeats no n-gram."""
        sentences = SENTENCE_END.split(text)
        kept: list[str] = []
        for s in sentences:
            candidate = f"{prefix} {' '.join(kept + [s])}"
            if self.grams(candidate) & self.seen:
                break
            kept.append(s)
        if kept:
            self.record(f"{prefix} {' '.join(kept)}")
        return " ".join(kept).strip()

    def record(self, text: str) -> None:
        self.seen |= self.grams(text)


def const_lines(consts: list[dict]) -> list[str]:
    """Consts whose descriptions differ only by their own name share one line."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for c in consts:
        desc = first_sentence(c["summary"])
        key = re.sub(rf"\b{re.escape(c['name'].split('::')[-1])}\b", "§", desc)
        groups[key].append(c)
    lines = []
    for key, members in groups.items():
        if len(members) == 1:
            c = members[0]
            lines.append(f"- `{c['signature'] or c['name']}`: {key.replace('§', c['name'].split('::')[-1])}")
        else:
            names = ", ".join(f"`{c['signature'] or c['name']}`" for c in members)
            lines.append(f"- {names}: {key.replace('§', '<name>')}")
    return lines


def short_gist(summary: str, max_words: int = 10) -> str:
    words = summary.rstrip(".").split()
    if len(words) <= max_words:
        return " ".join(words)
    cut = " ".join(words[:max_words])
    for sep in (";", ",", " or ", " and "):
        k = cut.rfind(sep)
        if k > len(cut) // 2:
            cut = cut[:k]
            break
    return cut.rstrip(",;") + "…"


# ---------------------------------------------------------------------- examples

SAMPLE_FILE = re.compile(r"^### (\S+\.kcl)\n\n```kcl\n(.*?)```", re.S | re.M)
CATEGORY_ABBR = {
    "Mechanical Components": "Mech",
    "Parametric": "Param",
    "Industrial & Manufacturing": "Indust",
    "Home & Lifestyle": "Home",
    "3D Printable": "Print",
    "Architecture & Construction": "Arch",
    "Science & Education": "Edu",
    "Automotive & Transportation": "Auto",
    "Art & Design": "Art",
    "Toys, Games, & Recreation": "Toys",
    "Electronics & Computing": "Elec",
    "Tools": "Tools",
    "Robotics & Automation": "Robot",
    "Aerospace": "Aero",
    "Medical & Assistive": "Med",
}
# Feature label -> regex over the sample's KCL. Order = display priority.
FEATURES: list[tuple[str, str]] = [
    ("sweep", r"\bsweep\("),
    ("helix", r"\bhelix\("),
    ("loft", r"\bloft\("),
    ("revolve", r"\brevolve\("),
    ("shell", r"\bshell\("),
    ("hollow", r"\bhollow\("),
    ("hole::", r"\bhole::\w+\("),
    ("gear::", r"\bgear::\w+\("),
    ("gdt::", r"\bgdt::\w+\("),
    ("view::", r"\bview::\w+\("),
    ("blend", r"\bblend\("),
    ("split", r"\bsplit\("),
    ("surfaces", r"\bjoinSurfaces\(|\bflipSurface\(|bodyType = SURFACE|deleteFace\("),
    ("intersect", r"\bintersect\("),
    ("union", r"\bunion\("),
    ("subtract", r"\bsubtract\("),
    ("fillet", r"\bfillet\("),
    ("chamfer", r"\bchamfer\("),
    ("twist", r"twistAngle"),
    ("draft", r"draftAngle"),
    ("patternTransform", r"\bpatternTransform\("),
    ("patternCircular3d", r"\bpatternCircular3d\("),
    ("patternLinear3d", r"\bpatternLinear3d\("),
    ("pattern2d", r"\bpattern(?:Linear|Circular|Transform)2d\("),
    ("mirror2d", r"\bmirror2d\("),
    ("sketchOnFace", r"\bfaceOf\(|\bplaneOf\("),
    ("offsetPlane", r"\boffsetPlane\("),
    ("customPlane", r"xAxis\s*=\s*\{"),
    ("clone", r"\bclone\("),
    ("rotate", r"\brotate\("),
    ("scale", r"\bscale\("),
    ("assert", r"\bassert(?:Is)?\("),
    ("map/reduce", r"\bmap\(|\breduce\("),
    ("fn", r"^\s*(?:export )?fn \w+\("),
    ("modules", r"^import .* from \"|^import \"[^\"]+\.kcl\""),
    ("foreignImport", r"^import \"[^\"]+\.(?:step|stp|stl|obj|gltf|glb|ply|sldprt|fbx)\""),
    ("enum", r"^type \w+ \{"),
    ("appearance", r"\bappearance\("),
    ("extrude", r"\bextrude\("),
]
COMMON_FEATURE_SHARE = 0.5  # features in more than half the samples are not listed per line
MAX_LINE_FEATURES = 5
BY_FEATURE_MAX = 25  # by-feature.md lists only features rare enough to be a useful filter


def parse_sample(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    files = SAMPLE_FILE.findall(text)
    if not files:
        return None
    title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    cats_m = re.search(r"^- Categories: (.+)$", text, re.M)
    cats = [c.strip() for c in cats_m.group(1).split(",")] if cats_m else []
    # "Toys, Games, & Recreation" contains commas; re-join known names.
    joined: list[str] = []
    for c in cats:
        if joined and (joined[-1] + ", " + c) in CATEGORY_ABBR or (joined and joined[-1].startswith("Toys")
                                                                     and c in ("Games", "& Recreation")):
            joined[-1] = joined[-1] + ", " + c
        else:
            joined.append(c)
    code = "\n".join(c for _, c in files)
    feats = [label for label, rx in FEATURES if re.search(rx, code, re.M)]
    main = next((c for f, c in files if f == "main.kcl"), code)
    m = re.search(r"kclVersion\s*=\s*([\d.]+)", main)
    version = m.group(1) if m else "unset"
    return {"slug": path.stem, "title": title, "cats": joined, "files": files, "features": feats, "version": version}


def build_examples() -> None:
    out = ZOO_SKILLS / "kcl-examples"
    samples = []
    no_source = []
    for p in sorted((SRC / "zoo-aquarium").glob("*.md")):
        if p.name == "index.md":
            continue
        s = parse_sample(p)
        if s is None:
            no_source.append(p.stem)
        else:
            samples.append(s)

    for s in samples:
        for fname, code in s["files"]:
            write(out / "samples" / s["slug"] / fname, code.rstrip("\n"))

    n = len(samples)
    feature_count: dict[str, int] = defaultdict(int)
    for s in samples:
        for f in s["features"]:
            feature_count[f] += 1
    common = {f for f, c in feature_count.items() if c > COMMON_FEATURE_SHARE * n}

    outliers = [s for s in samples if s["version"] != "2.0"]
    idx = [
        "# KCL sample index",
        "",
        f"{n} samples from zoo.dev/aquarium, one line each: `slug` Title · file count · notable features · categories.",
        "Read a sample: `samples/<slug>/main.kcl` (multi-file samples import their siblings). Page: `zoo.dev/aquarium/<slug>`.",
        "Features in most samples are omitted from lines: " + ", ".join(sorted(common)) + ". Feature lookup: `by-feature.md`.",
        "Categories: " + ", ".join(f"{v}={k}" for k, v in CATEGORY_ABBR.items()) + ".",
        f"`!kcl<v>` marks the {len(outliers)} samples whose `main.kcl` does not declare `kclVersion = 2.0` (sketch-block syntax under 1.0 or no version); set 2.0 when adapting them.",
        "",
    ]
    seen_titles: set[str] = set()
    for s in samples:
        feats = [f for f in s["features"] if f not in common][:MAX_LINE_FEATURES]
        cats = ", ".join(CATEGORY_ABBR.get(c, c) for c in s["cats"])
        nfiles = f"{len(s['files'])}f"
        # Title is dropped when it only restates the slug or repeats an earlier sample's title.
        redundant = re.sub(r"[^a-z0-9]", "", s["title"].lower()) == s["slug"].replace("-", "") or s["title"] in seen_titles
        seen_titles.add(s["title"])
        title = "" if redundant else f" {s['title']}"
        flag = "" if s["version"] == "2.0" else f" !kcl{s['version']}"
        while True:
            line = f"- `{s['slug']}`{title} · {nfiles} · {' '.join(feats) or '-'}{flag} · {cats}"
            if tokens(line) <= 30:
                break
            if feats:
                feats.pop()
            elif title:
                title = ""  # long title: the slug carries the name
            else:
                break
        idx.append(line)
    if no_source:
        idx += ["", "No KCL source on the page (community preview, not indexed): " + ", ".join(f"`{x}`" for x in no_source)]
    write(out / "index.md", "\n".join(idx))

    by = [
        "# Samples by feature",
        "",
        f"Feature -> sample slugs, for features used by at most {BY_FEATURE_MAX} of {n} samples. "
        "Broader features (extrude, subtract, fillet, patterns, offsetPlane, rotate, clone, fn, modules) are on each line of `index.md`.",
    ]
    for label, _ in FEATURES:
        slugs = [s["slug"] for s in samples if label in s["features"]]
        if not slugs or len(slugs) > BY_FEATURE_MAX:
            continue
        by += ["", f"## {label} ({len(slugs)})", " ".join(f"`{x}`" for x in slugs)]
    write(out / "by-feature.md", "\n".join(by))


# ----------------------------------------------------------------------- tooling

CLI_DIR = DOCS / "developer-tools" / "cli" / "manual"
API_DIR = DOCS / "developer-tools" / "api"
MCP_SERVER = SRC / "github" / "kittycad-mcp" / "server.py"
DL_FLAG = re.compile(r"<dt><code>([^<]+)</code></dt>\s*<dd>(.*?)</dd>", re.S)
# Flags every command repeats; documented once in the header instead.
GLOBAL_FLAGS = {"-d/--debug", "--host", "-h/--help", "-V/--version", "--show-trace", "--allow-errors", "-f/--format", "--format"}


def cli_page(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    cmd = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    body = body_after_header(text)
    summary = first_sentence(strip_links(body.strip().split("\n\n")[0]))
    flags = []
    for name, desc in DL_FLAG.findall(body):
        desc = html_lib.unescape(desc)
        values = re.search(r"Possible values: <code>([^<]+)</code>", desc)
        default = re.search(r"Default value: <code>([^<]+)</code>", desc)
        plain = re.sub(r"<br/>.*", "", desc, flags=re.S)
        plain = " ".join(re.sub(r"<[^>]+>", "", plain).split())
        flags.append({
            "name": name.strip(),
            "desc": first_sentence(plain),
            "values": values.group(1).replace(" ", "") if values else "",
            "default": default.group(1) if default else "",
        })
    subs = re.findall(r"^\* \[(zoo [^\]]+)\]", body, re.M)
    return {"cmd": cmd, "summary": summary, "flags": flags, "subs": subs}


def cli_flag_line(f: dict) -> str:
    positional = not f["name"].startswith("-")
    label = f"<{f['name']}>" if positional else f["name"]
    if f["values"]:
        label += f" {f['values']}"
    elif f["default"] and f["default"] != "false":
        label += f" (default {f['default']})"
    desc = f["desc"].rstrip(".")
    if desc and len(desc.split()) > 25:
        desc = short_gist(desc, 18)
    return f"`{label}`" + (f": {desc}" if desc else "")


def build_cli() -> str:
    pages = {p["cmd"]: p for p in (cli_page(p) for p in sorted(CLI_DIR.glob("*.md")) if p.name != "index.md")}
    lines = [
        "# zoo CLI",
        "",
        "Auth: `ZOO_API_TOKEN` env var (takes precedence) or `zoo auth login`; `ZOO_HOST`/`--host` for another API host.",
        "Every command accepts `-d/--debug`, `-h`; API commands add `-f/--format json|yaml|table`, `--show-trace`, and `--allow-errors` (continue past non-fatal KCL problems; never for acceptance builds).",
        "`<input>` is a `.kcl` file, a directory with `main.kcl`, or `-` for stdin; execution settings come from the nearest `project.toml`.",
        "Manual: `zoo.dev/docs/developer-tools/cli/manual/zoo_<sub>_<cmd>`.",
        "",
        "## zoo kcl",
    ]
    kcl_cmds = [c for c in pages if c.startswith("zoo kcl ")]
    for cmd in kcl_cmds:
        p = pages[cmd]
        lines.append(f"### `{cmd}`: {p['summary']}")
        for f in p["flags"]:
            if f["name"] in GLOBAL_FLAGS or f["name"] == "input":
                continue
            lines.append("- " + cli_flag_line(f))
    lines += ["", "## Other commands"]
    top = pages["zoo"]["subs"]
    for parent in top:
        if parent == "zoo kcl":
            continue
        p = pages.get(parent)
        if not p:
            continue
        subs = [s for s in pages if s.startswith(parent + " ")]
        gist = short_gist(p["summary"], 10)
        if subs:
            leaves = []
            for s in subs:
                summary = pages[s]["summary"].rstrip(".")
                leaf_gist = summary if len(summary.split()) <= 7 else ""
                leaves.append(f"`{s}`" + (f" {leaf_gist}" if leaf_gist and leaf_gist.lower() not in gist.lower() else ""))
            lines.append(f"- `{parent}` {gist}: " + "; ".join(leaves))
        else:
            lines.append(f"- `{parent}` {gist}")
    lines.append("- `zoo kcl` see above")
    return "\n".join(lines)


def rest_pages() -> list[dict]:
    out = []
    for p in sorted(API_DIR.rglob("*.md")):
        if p.name in ("index.md", "authentication.md", "errors.md") or p.parent == API_DIR:
            continue
        text = p.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", text, re.M).group(1).strip().rstrip(".")
        m = re.search(r"^`(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD) (/\S*)`", text, re.M)
        hidden = False
        if not m:
            m2 = re.search(r"^(get|post|put|delete|patch|options|head)\n\n(/[^\s]*?)(?:curl|$)", text, re.M | re.I)
            if not m2:
                continue
            method, path, hidden = m2.group(1).upper(), m2.group(2).strip(), True
        else:
            method, path = m.group(1), m.group(2)
        if not hidden and re.search(r"^hidden$", text, re.M):
            hidden = True
        path = path.replace("\\_", "_")
        section = p.relative_to(API_DIR).parts[0]  # titles containing '/' nest one level deeper
        out.append({"section": section, "method": method, "path": path, "title": title, "hidden": hidden})
    return out


STOPWORDS = {"get", "list", "the", "a", "an", "for", "your", "of", "to", "and", "from", "with", "in", "by", "on", "or",
             "is", "are", "that", "all", "one", "new", "own", "you", "given", "specific", "single", "currently"}


def gist_restates_path(gist: str, path: str) -> bool:
    """True when most content words of the gist already appear in the path."""
    def stem(w: str) -> str:
        return re.sub(r"(ies|s|es)$", "", w.lower())
    path_words = {stem(w) for w in re.split(r"[/{}\-_.]", path) if w}
    words = [stem(w) for w in re.findall(r"[A-Za-z]+", gist) if w.lower() not in STOPWORDS]
    if not words:
        return True
    hits = sum(1 for w in words if w in path_words or any(w in pw or pw in w for pw in path_words if len(w) > 3))
    return hits / len(words) >= 0.6


def build_api() -> str:
    eps = rest_pages()
    sections: dict[str, str] = {}
    for p in sorted(API_DIR.glob("*/index.md")):
        text = p.read_text(encoding="utf-8")
        body = body_after_header(text).strip()
        first = body.split("\n\n")[0] if body else ""
        sections[p.parent.name] = first_sentence(strip_links(first)) if first and not first.startswith(("|", "#", "-")) else ""
    lines = [
        "# Zoo REST API",
        "",
        "Base `https://api.zoo.dev`, header `Authorization: Bearer $ZOO_API_TOKEN`. OpenAPI: `GET /`.",
        "Large or slow jobs return an async operation `id`; poll `GET /async/operations/{id}`. Errors are JSON with `error_code` and `message` (see `/docs/developer-tools/api/errors`).",
        "`†` = hidden endpoint (absent from public nav; unstable; listed by path only). Page: `zoo.dev/docs/developer-tools/api/<section>/<slug-of-title>`.",
    ]
    seen: set[tuple[str, str]] = set()
    by_section: dict[str, list[dict]] = defaultdict(list)
    for e in eps:
        key = (e["method"], e["path"])
        if key in seen:
            continue
        seen.add(key)
        by_section[e["section"]].append(e)
    lines.append("Gists are omitted where the path already says it.")
    for section in sorted(by_section):
        gist = sections.get(section, "")
        lines += ["", f"## {section}" + (f": {short_gist(gist, 12)}" if gist else "")]
        for e in sorted(by_section[section], key=lambda e: (e["path"], e["method"])):
            mark = " †" if e["hidden"] else ""
            g = "" if e["hidden"] or gist_restates_path(e["title"], e["path"]) else " " + short_gist(e["title"], 8)
            lines.append(f"- `{e['method']} {e['path']}`{mark}{g}")
    return "\n".join(lines)


MCP_GROUPS: list[tuple[str, str]] = [
    ("Execute and check KCL", r"^(execute_kcl|exec_kcl_project|mock_execute_kcl|lint_and_fix_kcl|format_kcl|get_sketch_constraint_status|visualize_sketch)$"),
    ("Modeling sessions", r"modeling_session|^import_cad_file$"),
    ("Export and convert", r"^(export_kcl|convert_cad_file)$"),
    ("Physical properties", r"^calculate_"),
    ("Snapshots and images", r"^(snapshot|save_image)$"),
    ("Scene queries (need a session)", r"^(get_face_info|entity_|set_selection_filter|select_entities|center_camera_on_selection|highlight_set_entities|curve_|engine_util_|edge_get_length)"),
    ("Docs and samples lookup", r"kcl_docs|kcl_doc$|kcl_samples|kcl_sample$"),
    ("Org datasets and skills", r"^(list_org_|search_org_)"),
]
MCP_TOOL = re.compile(r"@mcp\.tool\(\)\s*\nasync def ([a-z_0-9]+)\((.*?)\)\s*->\s*([^:\n]+):\s*\n\s*\"\"\"(.*?)\"\"\"", re.S)


def mcp_params(params: str) -> str:
    out = []
    for p in split_params(f"f({params})")[1]:
        p = p.strip().rstrip(",")
        if not p:
            continue
        name = p.split(":")[0].strip()
        optional = "=" in p
        out.append(name + ("?" if optional else ""))
    return ", ".join(out)


def build_mcp() -> str:
    src = MCP_SERVER.read_text(encoding="utf-8")
    tools = []
    for name, params, ret, doc in MCP_TOOL.findall(src):
        first = first_sentence(" ".join(doc.split()))
        first = re.sub(r"\s*Either kcl_code or kcl_path must be provided\.?", "", first)
        first = re.sub(r" given a string of KCL code or a path to a KCL project", "", first)
        tools.append({"name": name, "params": mcp_params(" ".join(params.split())), "ret": " ".join(ret.split()), "doc": first})
    lines = [
        "# Zoo MCP",
        "",
        "Server `zoo-mcp` (KittyCAD/mcp, Python 3.11-3.13). Run `uvx zoo-mcp` with `ZOO_API_TOKEN` in the environment; client config = command `uvx`, args `[\"zoo-mcp\"]`, env `ZOO_API_TOKEN`, cwd = the design project. Prebuilt binaries on GitHub releases. No MCP fee, but hosted tools bill as API usage.",
        "Codex: `codex -c 'mcp_servers.zoo.command=\"uvx\"' -c 'mcp_servers.zoo.args=[\"zoo-mcp\"]' -c mcp_servers.zoo.env.ZOO_API_TOKEN=\"$ZOO_API_TOKEN\"`. Claude Code: `claude mcp add --scope project \"Zoo-MCP\" uv -- --directory \"$PWD\"/src/zoo_mcp run server.py`.",
        "",
        "## Sessions",
        "At most one persistent modeling session per server process. `get_modeling_sessions` recovers its id after a reconnect; otherwise `start_modeling_session`. Populate it with `execute_kcl`, `exec_kcl_project`, or `import_cad_file`; pass the same `session_id` to `snapshot` and scene-query tools; `stop_modeling_session` when done.",
        "Session executions save an artifact graph (JSON path returned); sessionless `execute_kcl` has no artifact graph and more network overhead. Snapshots are orthographic, so on-image measurements are undistorted.",
        "",
        "## Conventions",
        "Tools with `kcl_code?, kcl_path?` need exactly one; `kcl_path` is a `.kcl` file or a directory holding `main.kcl`. Unit strings: length `mm cm m in ft yd`, mass `g kg lb`, density `kg:m3 lb:ft3`, area/volume `mm2 cm3` style. Export/convert formats: `fbx glb gltf obj ply step stl` (import also `sldprt`, `stp`). Failures may come back as strings: check the returned type before trusting a result.",
        "`mock_execute_kcl` runs the interpreter without the engine: syntax, types, and `assert` fail fast, but face-dependent std code (`hole::*`, sketch-on-face queries) reports \"The engine isn't available\"; use `execute_kcl` for those. `lint_and_fix_kcl(kcl_path = dir)` rewrites files in place; pass `kcl_code` to keep sources untouched. `snapshot` with a `camera_view` list writes one composite `image.jpg` when `output_path` is a directory.",
        "",
        f"## Tools ({len(tools)}): `name(params)` -> return: purpose. `?` = optional.",
    ]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for t in tools:
        for label, rx in MCP_GROUPS:
            if re.search(rx, t["name"]):
                grouped[label].append(t)
                break
        else:
            grouped["Other"].append(t)
    guard = NgramGuard()
    guard.record("\n".join(lines))
    for label, _ in MCP_GROUPS + [("Other", "")]:
        if not grouped.get(label):
            continue
        lines += ["", f"### {label}"]
        for t in grouped[label]:
            doc = guard.admit_line(t["name"], t["doc"])
            lines.append(f"- `{t['name']}({t['params']})` -> `{t['ret']}`" + (f": {doc}" if doc else ""))
    return "\n".join(lines)


def build_tooling() -> None:
    out = ZOO_SKILLS / "zoo-tooling"
    write(out / "cli.md", build_cli())
    write(out / "api.md", build_api())
    write(out / "mcp.md", build_mcp())


def build_backends() -> None:
    """Index fetched backend examples next to the hand-written SKILL.md packs."""
    for bid in ("cadquery", "build123d", "freecad"):
        src = SRC / bid
        skill = SKILLS / "backends" / bid
        if not skill.exists():
            print(f"  skip {bid}: no skill pack")
            continue
        files = sorted(p.relative_to(src).as_posix() for p in src.rglob("*") if p.is_file()) if src.exists() else []
        body = f"# {bid} sources\n\nFetched into `sources/{bid}/` (`scripts/fetch_sources.py --backend {bid}`).\n\n"
        body += "\n".join(f"- `{f}`" for f in files[:80]) or "- (not fetched yet)\n"
        if len(files) > 80:
            body += f"\n- ... {len(files) - 80} more\n"
        write(skill / "sources.md", body)


def main(argv: list[str]) -> int:
    targets = argv or ["std", "examples", "tooling", "backends"]
    if "std" in targets:
        print("std:")
        build_std()
    if "examples" in targets:
        print("examples:")
        build_examples()
    if "tooling" in targets:
        print("tooling:")
        build_tooling()
    if "backends" in targets:
        print("backends:")
        build_backends()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

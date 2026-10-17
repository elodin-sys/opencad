"""Discover every design with a handoff, render its card, and write the static site: index, one page per design and backend,
model-viewer pages over the handoff GLBs, and the preferred backend's print files as downloads. Large files are hard-linked
into the output. The site reads only committed results: handoff/ and gate_feedback.json (see the root .gitignore)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml

from opencad.assembly.viz import MODEL_VIEWER_CDN
from opencad.paths import leaf_name
from opencad.site import templates as t

BACKENDS = ("build123d", "cadquery", "freecad", "zoo")
SECTIONS = ("machine", "part", "corpus")
MARKER = ".opencad-site"
STATIC = Path(__file__).parent / "static"
CARD_CACHE = Path.home() / ".cache" / "opencad" / "site-cards"
CARD_VERSION = "1"
PRINT_SUFFIXES = (".step", ".stp", ".stl")
OVERRIDE_KEYS = {"title", "summary", "intent", "featured", "section", "hidden"}
VIEWER_GLB_RE = re.compile(r'<model-viewer[^>]*\ssrc="([^"]+\.glb)"')


class SiteBuildError(ValueError):
    pass


@dataclass
class Result:
    backend: str
    dir: Path
    feedback: dict[str, Any]

    @property
    def ok(self) -> bool:
        return bool(self.feedback.get("ok"))

    @property
    def counts(self) -> tuple[int, int, int]:
        fb = self.feedback
        return len(fb.get("passed") or []), len(fb.get("failed") or []), len(fb.get("not_applicable") or [])

    def handoff(self) -> list[Path]:
        hd = self.dir / "handoff"
        return sorted(p for p in hd.iterdir() if p.is_file()) if hd.is_dir() else []


@dataclass
class Design:
    name: str
    section: str
    title: str
    summary: str
    intent: str
    spec_path: Path
    spec: dict[str, Any]
    truth: bool
    featured: bool = False
    results: dict[str, Result] = field(default_factory=dict)

    @property
    def preferred(self) -> Result:
        return self.results[next(b for b in (*BACKENDS, *sorted(self.results)) if b in self.results)]

    @property
    def machine(self) -> bool:
        return self.spec_path.name == "assembly.yaml"

    def leaf_dirs(self, r: Result) -> list[tuple[str, Path]]:
        return [(design, r.dir / "parts" / leaf_name(design, self.name)) for design in self.leaves()]

    def prints(self) -> list[Path]:
        """The preferred backend's print files: a part's handoff STEP and STLs, or each printable leaf's for a machine."""
        r = self.preferred
        if not self.machine:
            return [p for p in r.handoff() if p.suffix in PRINT_SUFFIXES]
        return [p for _, ldir in self.leaf_dirs(r) for p in Result(r.backend, ldir, {}).handoff() if p.suffix in PRINT_SUFFIXES]

    def leaves(self) -> list[str]:
        """Modelled part designs a machine names, in assembly order."""
        out = [p.get("design") for p in self.spec.get("parts") or [] if isinstance(p, dict) and p.get("kind") == "modelled"]
        return list(dict.fromkeys(d for d in out if d and d != self.name))


def _summary(intent: str, limit: int = 240) -> str:
    s = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", intent, maxsplit=1)[0]
    return s if len(s) <= limit else s[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def load_overrides(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    raw = yaml.safe_load(path.read_text()) or {}
    out = raw.get("designs") or {}
    if not isinstance(out, dict):
        raise SiteBuildError(f"{path}: designs must be a mapping of design name to overrides")
    for name, o in out.items():
        bad = set(o or {}) - OVERRIDE_KEYS
        if bad:
            raise SiteBuildError(f"{path}: {name} has unknown keys {sorted(bad)}")
        if (o or {}).get("section", "machine") not in SECTIONS:
            raise SiteBuildError(f"{path}: {name} section must be one of {SECTIONS}")
    return {k: v or {} for k, v in out.items()}


def discover(repo: Path, overrides: dict[str, dict[str, Any]]) -> list[Design]:
    designs: dict[str, Design] = {}
    results = repo / "results"
    for bdir in sorted(p for p in results.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))) if results.is_dir() else []:
        for rdir in sorted(p for p in bdir.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
            name = rdir.name
            o = overrides.get(name, {})
            ddir = repo / "designs" / name
            spec_path = next((p for p in (ddir / "assembly.yaml", ddir / "contract.yaml") if p.is_file()), None)
            fb_path = rdir / "gate_feedback.json"
            if o.get("hidden") or spec_path is None or not fb_path.is_file():
                continue
            res = Result(bdir.name, rdir, json.loads(fb_path.read_text()))
            if not any(p.suffix in (".glb", ".stl") for p in res.handoff()):
                continue
            if name not in designs:
                spec = yaml.safe_load(spec_path.read_text()) or {}
                intent = " ".join(str(spec.get("intent") or "").split())
                truth = (repo / "truth" / "cases" / name).is_dir()
                section = o.get("section") or ("machine" if spec_path.name == "assembly.yaml" else "corpus" if truth else "part")
                shown = " ".join(str(o["intent"]).split()) if o.get("intent") else intent
                designs[name] = Design(name, section, o.get("title") or name.replace("-", " ").capitalize(), o.get("summary") or _summary(shown),
                                       shown, spec_path, spec, truth, bool(o.get("featured")))
            designs[name].results[bdir.name] = res
    out = sorted(designs.values(), key=lambda d: (SECTIONS.index(d.section), d.title.lower()))
    if out and not any(d.featured for d in out):
        (next((d for d in out if d.name == "aleph-stack"), None) or out[0]).featured = True
    return out


def _place(src: Path, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)
    return dst


def _reset(out: Path, repo: Path) -> None:
    out = out.resolve()
    if out == repo.resolve() or repo.resolve().is_relative_to(out):
        raise SiteBuildError(f"refusing to replace {out}: it contains the repository")
    if out.exists():
        if any(out.iterdir()) and not (out / MARKER).exists():
            raise SiteBuildError(f"{out} is not empty and holds no previous site build ({MARKER})")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / MARKER).write_text("generated by python -m opencad.site build\n")


def viewer_files(r: Result, name: str) -> list[Path]:
    """What a backend page's viewer loads: a machine's assembly.html and the GLB it names, else the part's GLB."""
    html = r.dir / "handoff" / "assembly.html"
    if html.is_file():
        m = VIEWER_GLB_RE.search(html.read_text())
        glb = r.dir / "handoff" / m.group(1) if m else None
        return [html, *([glb] if glb and glb.is_file() else [])]
    glbs = [p for p in r.handoff() if p.suffix == ".glb"]
    glb = next((p for p in glbs if p.stem == name), glbs[0] if glbs else None)
    return [glb] if glb else []


def _hidden_bodies(spec: dict[str, Any]) -> tuple[str, ...]:
    """Derived solids and fluid regions are analysis geometry; the viewer starts with them off, and so does the card."""
    return tuple(p["name"] for p in (spec.get("parts") or []) if isinstance(p, dict) and p.get("name") and (p.get("kind") == "derived" or p.get("role") == "fluid"))


def _card_input(d: Design) -> tuple[Path, tuple[str, ...]] | None:
    """A machine card renders its viewer GLB without analysis bodies; a part card its preferred print STL."""
    if d.machine:
        glb = next((p for p in viewer_files(d.preferred, d.name) if p.suffix == ".glb"), None)
        return (glb, _hidden_bodies(d.spec)) if glb else None
    stls = [p for p in d.prints() if p.suffix == ".stl"]
    stl = next((p for p in stls if p.stem == d.name), max(stls, key=lambda p: p.stat().st_size) if stls else None)
    return (stl, ()) if stl else None


def render_card(src: str, out: str, exclude: tuple[str, ...] = ()) -> str:
    """Iso view of a handoff mesh without crease lines, cropped to the axes (module-level so a process pool can run it).

    A GLB with `exclude` drops those named bodies (`body:<name>`), which is how a machine card leaves out the fluid box."""
    import trimesh
    from PIL import Image

    from opencad.render import _fine, render_view

    if src.endswith(".glb"):
        scene = trimesh.load(src, force="scene")
        drop = {f"body:{n}" for n in exclude}
        kept = [g for n, g in scene.geometry.items() if n not in drop]
        m = trimesh.util.concatenate(kept) if kept else trimesh.load(src, force="mesh")
    else:
        m = trimesh.load(src, force="mesh")
    # subdivision keeps the painter's sort right on long wall triangles; past ~750k faces it costs more than it fixes
    fine = _fine(m, rel_edge=0.01, max_faces=1_500_000) if len(m.faces) < 750_000 else m
    render_view(m, "iso", Path(out), px=900, fine=fine, creases=False)
    im = Image.open(out)
    w, h = im.size
    im.crop((int(w * 0.02) + 3, int(h * 0.02) + 3, int(w * 0.98) - 3, int(h * 0.98) - 3)).save(out)
    return out


def _cards(designs: list[Design], out: Path, cache: Path, jobs: int) -> dict[str, str]:
    """Card image per design: a cached render of committed geometry, so a clean clone builds the same cards."""
    cache.mkdir(parents=True, exist_ok=True)
    todo: dict[str, tuple[Path, Path, tuple[str, ...]]] = {}
    for d in designs:
        chosen = _card_input(d)
        if chosen is None:
            continue
        src, exclude = chosen
        blob = src.read_bytes()
        # an empty exclusion list keeps the original cache key, so only cards that drop bodies are redrawn
        prefix = f"{CARD_VERSION}\0{chr(0).join(exclude)}\0".encode() if exclude else CARD_VERSION.encode()
        key = hashlib.sha256(prefix + blob).hexdigest()
        todo[d.name] = (src, cache / f"{key}.png", exclude)
    missing = {n: v for n, v in todo.items() if not v[1].exists()}
    with ProcessPoolExecutor(max_workers=max(1, jobs)) as pool:
        futures = {n: pool.submit(render_card, str(src), str(png), exclude) for n, (src, png, exclude) in missing.items()}
        failed = {n for n, f in futures.items() if f.exception() is not None}
    cards: dict[str, str] = {}
    for d in designs:
        src = todo[d.name][1] if d.name in todo and d.name not in failed else None
        if src is not None:
            dest = out / "d" / d.name
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest / "card.png")
            cards[d.name] = "card.png"
    return cards


def _files(paths: list[Path], dest: Path, rel: str) -> list[dict[str, Any]]:
    for p in paths:
        _place(p, dest / p.name)
    return [{"name": p.name, "href": f"{rel}/{p.name}", "kind": p.suffix.lstrip(".").upper(), "bytes": p.stat().st_size} for p in paths]


def _viewer(src: list[Path], hd: Path, title: str) -> str | None:
    """handoff/viewer.html: the machine's own assembly.html on the vendored model-viewer, or a model-viewer page over the part GLB."""
    for p in src:
        if p.suffix == ".glb":
            _place(p, hd / p.name)
    html = next((p for p in src if p.suffix == ".html"), None)
    if html is not None:
        page = html.read_text().replace(MODEL_VIEWER_CDN, "../../../../assets/model-viewer.min.js")
        (hd / "viewer.html").write_text(page.replace("</head>", t.ASSEMBLY_VIEWER_PATCH + "</head>", 1))
        return "handoff/viewer.html"
    glb = next((p for p in src if p.suffix == ".glb"), None)
    if glb is None:
        return None
    (hd / "viewer.html").write_text(t.part_viewer(title, glb.name))
    return "handoff/viewer.html"


def _write_design(d: Design, r: Result, out: Path, cards: dict[str, str], built: str) -> None:
    """One backend's page, with that backend's own handoff STEP/STL (and, for a machine, its printable parts' files)."""
    page = out / "d" / d.name / r.backend
    hd = page / "handoff"
    hd.mkdir(parents=True, exist_ok=True)
    viewer = _viewer(viewer_files(r, d.name), hd, d.title)
    downloads = _files([p for p in r.handoff() if p.suffix in PRINT_SUFFIXES], hd, "handoff")
    leaves = []
    if d.machine:
        for design, ldir in d.leaf_dirs(r):
            leaf = ldir.name
            fb_path = ldir / "gate_feedback.json"
            lr = Result(r.backend, ldir, json.loads(fb_path.read_text()) if fb_path.is_file() else {})
            prints = [p for p in lr.handoff() if p.suffix in PRINT_SUFFIXES]
            leaves.append({"design": design, "leaf": leaf, "result": lr, "files": _files(prints, page / "parts" / leaf, f"parts/{leaf}")})
    _place(d.spec_path, page / d.spec_path.name)
    props_path = r.dir / "handoff" / "properties.json"
    props = json.loads(props_path.read_text()) if props_path.is_file() and not d.machine else {}
    tabs = [(b, d.results[b]) for b in dict.fromkeys((*BACKENDS, *sorted(d.results))) if b in d.results]
    card = "../card.png" if d.name in cards else None
    (page / "index.html").write_text(t.design_page(d, r, tabs, viewer, downloads, leaves, props, card, built))


def _git_label(repo: Path) -> str:
    try:
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo, capture_output=True, text=True, check=False).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "an unversioned tree"
    return f"{head}{' with local changes' if dirty else ''}"


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.links += [v for k, v in attrs if k in ("href", "src") and v]


def check_links(out: Path) -> list[str]:
    """Every relative href/src in the built pages resolves to a file inside the output."""
    out = out.resolve()
    bad = []
    for page in out.rglob("*.html"):
        parser = _Links()
        parser.feed(page.read_text())
        for link in parser.links:
            u = urlsplit(link)
            if u.scheme or link.startswith(("#", "//")):
                continue
            path = unquote(u.path)
            target = (out / path.lstrip("/")) if path.startswith("/") else (page.parent / path)
            target = target.resolve()
            if path.endswith("/") or target.is_dir():
                target = target / "index.html"
            if not target.is_relative_to(out) or not target.is_file():
                bad.append(f"{page.relative_to(out)} -> {link}")
    return bad


def build_site(repo: Path, out: Path, *, manifest: Path | None = None, cache: Path = CARD_CACHE, jobs: int = 4) -> list[Design]:
    repo = repo.resolve()
    designs = discover(repo, load_overrides(manifest or repo / "site" / "designs.yaml"))
    if not designs:
        raise SiteBuildError(f"no design under {repo / 'results'} has gate feedback and a handoff mesh")
    _reset(out, repo)
    assets = out / "assets"
    assets.mkdir()
    (assets / "site.css").write_text(t.CSS)
    _place(STATIC / "model-viewer.min.js", assets / "model-viewer.min.js")
    built = f"Built from {_git_label(repo)} on {datetime.now(UTC):%d %b %Y %H:%M} UTC"
    cards = _cards(designs, out, cache, jobs)
    for d in designs:
        for r in d.results.values():
            _write_design(d, r, out, cards, built)
        (out / "d" / d.name / "index.html").write_text(t.redirect(f"{d.preferred.backend}/"))
    log = repo / "results" / "_bakeoff" / "published.yaml"
    bakeoffs = list((yaml.safe_load(log.read_text()) or {}).get("entries") or []) if log.is_file() else []
    (out / "bakeoff").mkdir()
    (out / "bakeoff" / "index.html").write_text(t.bakeoff_page(bakeoffs, designs, built))
    (out / "index.html").write_text(t.index_page(designs, cards, built, bakeoffs))
    (out / "404.html").write_text(t.not_found())
    bad = check_links(out)
    if bad:
        raise SiteBuildError("broken links in the built site:\n  " + "\n  ".join(bad[:20]))
    return designs

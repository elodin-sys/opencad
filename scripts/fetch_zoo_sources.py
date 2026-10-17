#!/usr/bin/env python3
"""Mirror zoo.dev /docs, /aquarium, and /research into sources/."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html as html_lib
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen

BASE = "https://zoo.dev"
SITEMAP_INDEX = f"{BASE}/sitemap.xml"
USER_AGENT = "opencad-docs-mirror/0.1"
PREFIXES = ("/docs", "/aquarium", "/research")
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
KCL_BOOK_TOC = f"{BASE}/docs/kcl-book/toc.js"
KCL_BOOK_PRINT = f"{BASE}/docs/kcl-book/print.html"

HEADING_ANCHOR = re.compile(r"^(#{1,6})\s+<a\b[^>]*>(.*?)</a>\s*$", re.M)
HTML_HREF = re.compile(
    r"""href=["']((?:https://zoo\.dev)?/(?:docs|aquarium|research)[^"']*)["']"""
)
NEXT_DATA = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S
)
KATEX_OPEN = re.compile(r'<span class="[^"]*\bkatex(?:-display)?\b[^"]*"')
TEX_ANNOTATION = re.compile(
    r'<annotation encoding="application/x-tex">(.*?)</annotation>', re.S
)
RESEARCH_ASSET = re.compile(
    r"(?:https://zoo\.dev)?(/documentation-assets/research/[^)\s\"'<>]+)"
)
DATA_IMG = re.compile(
    r"<img\b[^>]*src=(?:\"data:[^\"]*\"|'data:[^']*')[^>]*/?>",
    re.I,
)
DATA_IMG_MD = re.compile(r'<img\b[^>]*src="data:[^"]*"[^>]*>\s*', re.I)
ASSET_IMG_MD = re.compile(
    r'<img\b[^>]*src="(assets/[^"]+)"[^>]*(?:alt="([^"]*)")?[^>]*/?>',
    re.I,
)
BACK_LINK = re.compile(
    r'<a\b[^>]*href="/research"[^>]*>.*?</a>', re.S | re.I
)
FENCE_KCL = re.compile(r"^```\s+kcl\b", re.M)
BOOK_HTML_LINK = re.compile(r"\]\(([^)]+?)\.html(#[^)]*)?\)")
TITLE_MD = re.compile(r"^#\s+(.+)$", re.M)
HTML_TITLE = re.compile(r"<title[^>]*>([^<]+)</title>", re.I)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonicalize(url_or_path: str) -> str | None:
    raw = html_lib.unescape(url_or_path.strip())
    if not raw or raw.startswith("mailto:"):
        return None
    if raw.startswith("/"):
        raw = BASE + raw
    parsed = urlparse(raw)
    if parsed.netloc and parsed.netloc != "zoo.dev":
        return None
    path = unquote(parsed.path or "/")
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    if not any(path == p or path.startswith(p + "/") for p in PREFIXES):
        if path not in PREFIXES:
            return None
    safe_path = quote(path, safe="/.-_~")
    return f"{BASE}{safe_path}"


def page_kind(url: str) -> str:
    path = urlparse(url).path
    if path == "/research" or path.startswith("/research/"):
        return "research"
    if path.startswith("/docs/kcl-book"):
        return "kcl-book"
    return "markdown"


def http_get(url: str, headers: dict[str, str], timeout: float = 60.0) -> dict:
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return {
                "status": resp.status,
                "url": resp.geturl(),
                "content_type": resp.headers.get("content-type", ""),
                "body": resp.read(),
            }
    except HTTPError as e:
        body = e.read() if e.fp else b""
        return {
            "status": e.code,
            "url": url,
            "content_type": e.headers.get("content-type", "") if e.headers else "",
            "body": body,
        }


def fetch_with_retries(url: str, accept_markdown: bool, retries: int = 3) -> dict:
    headers = {"User-Agent": USER_AGENT}
    if accept_markdown:
        headers["Accept"] = "text/markdown"
    delay = 0.5
    last: dict | None = None
    for attempt in range(retries):
        try:
            last = http_get(url, headers)
            status = last["status"]
            if status == 429 or status >= 500:
                time.sleep(delay)
                delay *= 2
                continue
            return last
        except (URLError, TimeoutError, OSError, UnicodeEncodeError) as e:
            last = {"status": 0, "url": url, "content_type": "", "body": b"", "error": str(e)}
            time.sleep(delay)
            delay *= 2
    return last or {"status": 0, "url": url, "content_type": "", "body": b"", "error": "unknown"}


def is_html_body(body: bytes) -> bool:
    head = body.lstrip()[:32].lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_sitemap_urls() -> list[str]:
    index = fetch_with_retries(SITEMAP_INDEX, accept_markdown=False)
    if index["status"] != 200:
        raise RuntimeError(f"sitemap index failed: {index['status']}")
    root = ET.fromstring(index["body"])
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [el.text.strip() for el in root.findall(".//sm:loc", ns) if el.text]
    child_xmls = [loc for loc in locs if loc.endswith(".xml") or "sitemap" in loc]
    page_locs = [loc for loc in locs if loc not in child_xmls]
    if not child_xmls and page_locs:
        child_xmls = []
    if not child_xmls:
        # Single sitemap of URLs, or the index loc is the only sitemap.
        if locs == page_locs:
            child_xmls = locs if any(x.endswith(".xml") for x in locs) else []
            if not child_xmls:
                return [u for u in (canonicalize(x) for x in locs) if u]
    found: list[str] = []
    targets = child_xmls or [SITEMAP_INDEX]
    for sm_url in targets:
        res = fetch_with_retries(sm_url, accept_markdown=False)
        if res["status"] != 200:
            raise RuntimeError(f"sitemap {sm_url} failed: {res['status']}")
        sm_root = ET.fromstring(res["body"])
        for el in sm_root.findall(".//sm:loc", ns):
            if not el.text:
                continue
            url = canonicalize(el.text.strip())
            if url:
                found.append(url)
    return list(dict.fromkeys(found))


def parse_kcl_book_toc(js: str) -> list[tuple[str, str, str | None]]:
    """Return (filename, title, part_title) in sidebar order."""
    entries: list[tuple[str, str, str | None]] = []
    part: str | None = None
    for m in re.finditer(
        r'<li class="part-title">([^<]+)</li>|<a href="([^"]+\.html)">(.*?)</a>',
        js,
    ):
        if m.group(1):
            part = html_lib.unescape(m.group(1)).strip()
            continue
        filename = m.group(2)
        inner = re.sub(r"<[^>]+>", "", m.group(3))
        title = html_lib.unescape(inner).strip()
        title = re.sub(r"^\d+\.\s*", "", title)
        entries.append((filename, title, part))
    return entries


def discover_kcl_book() -> tuple[list[str], list[tuple[str, str, str | None]]]:
    res = fetch_with_retries(KCL_BOOK_TOC, accept_markdown=False)
    if res["status"] != 200:
        raise RuntimeError(f"kcl-book toc.js failed: {res['status']}")
    toc = parse_kcl_book_toc(res["body"].decode("utf-8", errors="replace"))
    urls = [f"{BASE}/docs/kcl-book/{name}" for name, _, _ in toc]
    urls.append(KCL_BOOK_PRINT)
    return urls, toc


def iter_markdown_dests(text: str):
    i = 0
    while True:
        start = text.find("](", i)
        if start < 0:
            break
        j = start + 2
        depth = 1
        while j < len(text) and depth:
            ch = text[j]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "\n":
                break
            j += 1
        if depth == 0:
            dest = text[start + 2 : j - 1].strip()
            if dest.startswith("<") and ">" in dest:
                dest = dest[1 : dest.index(">")]
            elif dest:
                dest = dest.split()[0]
            if dest:
                yield dest
        i = start + 2


def extract_links(text: str) -> set[str]:
    urls: set[str] = set()
    for dest in iter_markdown_dests(text):
        url = canonicalize(dest)
        if url:
            urls.add(url)
    for path in HTML_HREF.findall(text):
        url = canonicalize(path)
        if url:
            urls.add(url)
    return urls


def is_soft_404(body: bytes) -> bool:
    title = title_from_html(body.decode("utf-8", errors="replace")) or ""
    return bool(re.search(r"\b404\b|not found", title, re.I))


def parse_next_data(html: str) -> dict | None:
    m = NEXT_DATA.search(html)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def aquarium_from_next_data(html: str) -> str | None:
    data = parse_next_data(html)
    if not data:
        return None
    sample = data.get("props", {}).get("pageProps", {}).get("initialSample")
    if not isinstance(sample, dict) or not sample.get("title"):
        return None
    title = sample.get("title") or ""
    desc = (sample.get("description") or "").strip()
    page = sample.get("page") or ""
    cats = sample.get("categories") or []
    screenshot = sample.get("screenshot") or ""
    parts = sample.get("parts") or []
    lines = [f"# {title}", ""]
    if desc:
        lines.extend([desc, ""])
    lines.append(f"- Page: /aquarium/{page}")
    if screenshot:
        lines.append(f"- Preview image: {screenshot}")
    if cats:
        lines.append(f"- Categories: {', '.join(str(c) for c in cats)}")
    if parts:
        lines.extend(["", "## Files", ""])
        for part in parts:
            if not isinstance(part, dict):
                continue
            name = part.get("filename") or part.get("name") or part.get("path") or "main.kcl"
            code = part.get("code") or part.get("contents") or part.get("kcl") or ""
            lines.extend([f"### {name}", "", "```kcl", str(code).rstrip(), "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def find_matching_span_end(html: str, start: int) -> int:
    gt = html.find(">", start)
    if gt < 0:
        return len(html)
    pos = gt + 1
    depth = 1
    for m in re.finditer(r"</?span\b[^>]*>", html[pos:]):
        tag = m.group(0)
        if tag.startswith("</"):
            depth -= 1
            if depth == 0:
                return pos + m.end()
        else:
            depth += 1
    return len(html)


def replace_katex_with_tex(html: str) -> str:
    out: list[str] = []
    i = 0
    while True:
        m = KATEX_OPEN.search(html, i)
        if not m:
            out.append(html[i:])
            break
        out.append(html[i : m.start()])
        end = find_matching_span_end(html, m.start())
        block = html[m.start() : end]
        tex_m = TEX_ANNOTATION.search(block)
        if tex_m:
            tex = html_lib.unescape(tex_m.group(1)).strip()
            display = "katex-display" in m.group(0)
            out.append(f"$${tex}$$" if display else f"${tex}$")
        else:
            out.append(block)
        i = end
    return "".join(out)


def extract_tag_blocks(html: str, tag: str) -> list[str]:
    return re.findall(rf"<{tag}\b[^>]*>.*?</{tag}>", html, re.S | re.I)


def extract_research_fragment(html: str, is_index: bool) -> str:
    articles = extract_tag_blocks(html, "article")
    mains = extract_tag_blocks(html, "main")
    if is_index:
        if mains:
            return max(mains, key=len)
        return "\n".join(articles) or html
    if articles:
        return max(articles, key=len)
    if mains:
        return max(mains, key=len)
    return html


def extract_book_fragment(html: str) -> str:
    mains = extract_tag_blocks(html, "main")
    return max(mains, key=len) if mains else html


def clean_research_html(fragment: str) -> str:
    html = replace_katex_with_tex(fragment)
    html = DATA_IMG.sub("", html)
    html = BACK_LINK.sub("", html)
    return html


def unwrap_heading_anchors(md: str) -> str:
    def repl(m: re.Match) -> str:
        inner = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        return f"{m.group(1)} {inner}"

    return HEADING_ANCHOR.sub(repl, md)


def pandoc_gfm(html: str, from_fmt: str) -> str:
    proc = subprocess.run(
        ["pandoc", "-f", from_fmt, "-t", "gfm", "--wrap=none"],
        input=html,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or "").strip() or "pandoc failed"
        raise RuntimeError(err)
    return proc.stdout


def convert_research(html: str, is_index: bool) -> str:
    fragment = clean_research_html(extract_research_fragment(html, is_index))
    md = pandoc_gfm(fragment, "html-native_divs-native_spans")
    md = unwrap_heading_anchors(md)
    md = RESEARCH_ASSET.sub(lambda m: "assets/" + m.group(1).split("/documentation-assets/research/", 1)[1], md)
    md = DATA_IMG_MD.sub("", md)
    md = ASSET_IMG_MD.sub(lambda m: f"![{m.group(2) or ''}]({m.group(1)})", md)
    md = md.replace("\\$", "$")
    return md.strip() + "\n"


def convert_book(html: str) -> str:
    fragment = extract_book_fragment(html)
    md = pandoc_gfm(fragment, "html")
    md = unwrap_heading_anchors(md)
    md = FENCE_KCL.sub("```kcl", md)
    md = BOOK_HTML_LINK.sub(r"](\1.md\2)", md)
    return md.strip() + "\n"


def convert_site_html(html: str) -> str:
    articles = extract_tag_blocks(html, "article")
    fragment = max(articles, key=len) if articles else extract_book_fragment(html)
    fragment = DATA_IMG.sub("", fragment)
    fragment = replace_katex_with_tex(fragment)
    md = pandoc_gfm(fragment, "html-native_divs-native_spans")
    md = unwrap_heading_anchors(md)
    md = re.sub(r'<img\b[^>]*src="data:[^"]*"[^>]*>', "", md)
    return md.strip() + "\n"


def first_heading(md: str) -> str | None:
    m = TITLE_MD.search(md)
    if not m:
        return None
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return html_lib.unescape(title) or None


def title_from_html(html: str) -> str | None:
    m = HTML_TITLE.search(html)
    if not m:
        return None
    title = html_lib.unescape(m.group(1)).strip()
    title = re.sub(r"\s+\|\s+Zoo\s*$", "", title)
    title = re.sub(r"\s+-\s+Modeling with KCL\s*$", "", title)
    return title or None


def provenance(url: str, title: str, body: str) -> str:
    return f"Source URL: {url}\nTitle: {title}\n\n{body.lstrip()}"


def paths_with_children(urls: list[str]) -> set[str]:
    paths = [unquote(urlparse(u).path).rstrip("/") or "/" for u in urls]
    path_set = set(paths)
    children: set[str] = set()
    for p in path_set:
        prefix = p + "/"
        if any(q.startswith(prefix) for q in path_set if q != p):
            children.add(p)
    return children


def local_paths(url: str, child_paths: set[str]) -> dict[str, str]:
    path = unquote(urlparse(url).path)
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    if path == "/docs":
        return {"md": "zoo-docs/index.md"}
    if path.startswith("/docs/kcl-book"):
        name = Path(path).name or "index.html"
        if not name.endswith(".html"):
            name = f"{name}.html"
        stem = Path(name).stem
        return {
            "md": f"zoo-docs/kcl-book/{stem}.md",
            "html": f"zoo-docs/kcl-book/html/{name}",
        }
    if path.startswith("/docs/"):
        rel = path[len("/docs/") :]
        if path in child_paths:
            return {"md": f"zoo-docs/{rel}/index.md"}
        return {"md": f"zoo-docs/{rel}.md"}
    if path == "/aquarium":
        return {"md": "zoo-aquarium/index.md"}
    if path.startswith("/aquarium/"):
        return {"md": f"zoo-aquarium/{path[len('/aquarium/'):]}.md"}
    if path == "/research":
        return {"md": "zoo-research/index.md", "html": "zoo-research/html/index.html"}
    if path.startswith("/research/"):
        slug = path[len("/research/") :]
        return {"md": f"zoo-research/{slug}.md", "html": f"zoo-research/html/{slug}.html"}
    raise ValueError(f"unmapped url: {url}")


def write_bytes(root: Path, rel: str, data: bytes) -> None:
    dest = root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


def write_text(root: Path, rel: str, text: str) -> bytes:
    data = text.encode("utf-8")
    write_bytes(root, rel, data)
    return data


def aquarium_slugs(urls: list[str]) -> list[str]:
    slugs = []
    for url in urls:
        path = urlparse(url).path
        if path.startswith("/aquarium/") and path != "/aquarium":
            slugs.append(path[len("/aquarium/") :])
    return slugs


def collect_research_assets(htmls: list[str]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for html in htmls:
        for path in RESEARCH_ASSET.findall(html):
            path = html_lib.unescape(path.split("?")[0])
            ext = Path(path).suffix.lower()
            if ext not in IMG_EXT:
                continue
            if path in seen:
                continue
            seen.add(path)
            found.append(path)
    return found


def build_book_index(toc: list[tuple[str, str, str | None]]) -> str:
    lines = [
        "Source URL: https://zoo.dev/docs/kcl-book/intro.html",
        "Title: Modeling with KCL",
        "",
        "# Modeling with KCL",
        "",
        "KCL Book chapters in site TOC order.",
        "",
    ]
    current_part: str | None = object()  # type: ignore
    for filename, title, part in toc:
        if part != current_part:
            current_part = part
            if part:
                lines.append("")
                lines.append(f"## {part}")
                lines.append("")
        stem = Path(filename).stem
        lines.append(f"- [{title}]({stem}.md)")
    lines.extend(["", "## Printable book", "", "- [Full book (print)](print.md)", ""])
    return "\n".join(lines)


def map_site_path_to_local(path: str, child_paths: set[str]) -> str | None:
    url = canonicalize(path)
    if not url:
        return None
    try:
        return local_paths(url, child_paths)["md"]
    except ValueError:
        return None


def write_readme(
    root: Path,
    fetched_at: str,
    counts: dict,
    gaps: list[str],
    manifest_rel: str,
) -> None:
    lines = [
        "# zoo.dev source mirror",
        "",
        f"Fetched at `{fetched_at}` by `scripts/fetch_zoo_sources.py`.",
        "",
        "Native Markdown via `Accept: text/markdown` for `/docs` (except the KCL Book) and `/aquarium`.",
        "Raw HTML plus pandoc GFM for `/research` and `/docs/kcl-book`.",
        "",
        "## Counts",
        "",
        f"- Docs Markdown pages: {counts['docs_md']}",
        f"- KCL Book chapters (converted): {counts['book_md']}",
        f"- KCL Book raw HTML: {counts['book_html']}",
        f"- Aquarium pages: {counts['aquarium_md']}",
        f"- Aquarium screenshots: {counts['aquarium_png']}",
        f"- Research pages: {counts['research_md']}",
        f"- Research raw HTML: {counts['research_html']}",
        f"- Research figures: {counts['research_assets']}",
        f"- Failed page fetches: {counts['failed_pages']}",
        f"- Failed asset fetches: {counts['failed_assets']}",
        "",
        f"Full per-URL inventory: [{manifest_rel}]({manifest_rel}).",
        "",
        "## Known gaps",
        "",
        "These are stale or unpublished zoo.dev URLs (sitemap or in-page links that 404).",
        "Hidden API pages that omit Markdown are stored via HTML fallback.",
        "",
    ]
    if gaps:
        lines.extend(f"- {g}" for g in gaps)
    else:
        lines.append("- None.")
    lines.append("")
    write_text(root, "README.md", "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "sources",
        help="Output directory (default: <repo>/sources)",
    )
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    fetched_at = now_iso()

    print("Discovering sitemap URLs...", flush=True)
    urls = fetch_sitemap_urls()
    print(f"  sitemap in-scope: {len(urls)}", flush=True)
    book_urls, book_toc = discover_kcl_book()
    print(f"  kcl-book chapters: {len(book_toc)} + print.html", flush=True)
    pending = list(dict.fromkeys(urls + book_urls))
    fetched: dict[str, dict] = {}

    while pending:
        batch = [u for u in pending if u not in fetched]
        pending = []
        if not batch:
            break
        print(f"Fetching {len(batch)} pages...", flush=True)

        def work(url: str) -> tuple[str, dict]:
            kind = page_kind(url)
            if kind != "markdown":
                res = fetch_with_retries(url, accept_markdown=False)
                res["kind"] = kind
                return url, res
            res = fetch_with_retries(url, accept_markdown=True)
            body = res.get("body") or b""
            if res["status"] == 200 and body and not is_html_body(body):
                res["kind"] = "markdown"
                return url, res
            html_res = fetch_with_retries(url, accept_markdown=False)
            html_body = html_res.get("body") or b""
            if html_res["status"] == 200 and html_body and not is_soft_404(html_body):
                html_res["kind"] = "html-fallback"
                return url, html_res
            res["kind"] = "markdown"
            return url, res

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            for url, res in pool.map(work, batch):
                fetched[url] = res

        new_links: set[str] = set()
        for url, res in fetched.items():
            if res.get("_scanned"):
                continue
            body = res.get("body") or b""
            if res["status"] != 200 or not body:
                res["_scanned"] = True
                continue
            text = body.decode("utf-8", errors="replace")
            new_links |= extract_links(text)
            res["_scanned"] = True
        for url in sorted(new_links):
            if url not in fetched:
                pending.append(url)
        if pending:
            print(f"  discovered {len(pending)} new in-scope links", flush=True)

    page_urls = list(fetched)
    child_paths = paths_with_children(page_urls)
    manifest: list[dict] = []
    gaps: list[str] = []
    ok_md_urls: set[str] = set()
    research_fragments: list[str] = []
    screenshot_overrides: dict[str, str] = {}
    docs_md = book_md = book_html = aquarium_md = research_md = research_html = 0
    failed_pages = 0

    print("Writing pages...", flush=True)
    for url in sorted(page_urls):
        res = fetched[url]
        kind = res["kind"]
        status = res["status"]
        body: bytes = res.get("body") or b""
        entry: dict = {
            "url": url,
            "kind": kind,
            "status": status,
            "bytes": len(body),
            "sha256": sha256_bytes(body) if body else None,
            "local_path": None,
            "html_path": None,
            "ok": False,
            "error": res.get("error"),
            "fetched_at": fetched_at,
        }

        if status != 200 or not body:
            entry["error"] = entry["error"] or f"http {status}"
            gaps.append(f"{url} failed ({entry['error']})")
            failed_pages += 1
            manifest.append(entry)
            continue

        if kind == "markdown" and is_html_body(body):
            entry["error"] = "markdown request returned HTML"
            gaps.append(f"{url} returned HTML instead of Markdown")
            failed_pages += 1
            manifest.append(entry)
            continue

        rels = local_paths(url, child_paths)
        path = unquote(urlparse(url).path)

        try:
            if kind == "markdown":
                md = body.decode("utf-8")
                title = first_heading(md) or url
                data = write_text(out, rels["md"], provenance(url, title, md))
                entry["local_path"] = rels["md"]
                entry["bytes"] = len(data)
                entry["sha256"] = sha256_bytes(data)
                entry["ok"] = True
                ok_md_urls.add(url)
                if path.startswith("/aquarium"):
                    aquarium_md += 1
                else:
                    docs_md += 1
            elif kind == "html-fallback":
                html = body.decode("utf-8", errors="replace")
                if path.startswith("/aquarium"):
                    md = aquarium_from_next_data(html) or convert_site_html(html)
                    sample = (parse_next_data(html) or {}).get("props", {}).get("pageProps", {}).get("initialSample") or {}
                    shot = sample.get("screenshot") if isinstance(sample, dict) else None
                    slug = path[len("/aquarium/") :]
                    if shot and slug:
                        screenshot_overrides[slug] = shot
                    aquarium_md += 1
                else:
                    md = convert_site_html(html)
                    docs_md += 1
                title = first_heading(md) or title_from_html(html) or url
                data = write_text(out, rels["md"], provenance(url, title, md))
                entry["local_path"] = rels["md"]
                entry["bytes"] = len(data)
                entry["sha256"] = sha256_bytes(data)
                entry["ok"] = True
                ok_md_urls.add(url)
            elif kind == "research":
                html = body.decode("utf-8", errors="replace")
                research_fragments.append(extract_research_fragment(html, path == "/research"))
                write_bytes(out, rels["html"], body)
                entry["html_path"] = rels["html"]
                research_html += 1
                md = convert_research(html, is_index=(path == "/research"))
                title = first_heading(md) or title_from_html(html) or url
                data = write_text(out, rels["md"], provenance(url, title, md))
                entry["local_path"] = rels["md"]
                entry["bytes"] = len(data)
                entry["sha256"] = sha256_bytes(data)
                entry["ok"] = True
                ok_md_urls.add(url)
                research_md += 1
            elif kind == "kcl-book":
                html = body.decode("utf-8", errors="replace")
                write_bytes(out, rels["html"], body)
                entry["html_path"] = rels["html"]
                book_html += 1
                md = convert_book(html)
                title = first_heading(md) or title_from_html(html) or url
                data = write_text(out, rels["md"], provenance(url, title, md))
                entry["local_path"] = rels["md"]
                entry["bytes"] = len(data)
                entry["sha256"] = sha256_bytes(data)
                entry["ok"] = True
                ok_md_urls.add(url)
                book_md += 1
        except Exception as e:
            entry["error"] = str(e)
            entry["ok"] = False
            gaps.append(f"{url} conversion/write failed: {e}")
            failed_pages += 1

        manifest.append(entry)

    book_index_rel = "zoo-docs/kcl-book/index.md"
    write_text(out, book_index_rel, build_book_index(book_toc))

    print("Downloading assets...", flush=True)
    asset_jobs: list[tuple[str, str]] = []
    ok_kinds = {"markdown", "html-fallback"}
    for slug in aquarium_slugs([u for u, r in fetched.items() if r["kind"] in ok_kinds and r["status"] == 200]):
        shot = screenshot_overrides.get(slug) or f"{BASE}/kcl-samples/screenshots/{slug}.png"
        asset_jobs.append((shot, f"zoo-aquarium/screenshots/{slug}.png"))
    research_asset_paths = collect_research_assets(research_fragments)
    for path in research_asset_paths:
        rel = "zoo-research/assets/" + path.split("/documentation-assets/research/", 1)[1]
        asset_jobs.append((urljoin(BASE, path), rel))

    aquarium_png = 0
    research_assets = 0
    failed_assets = 0

    def fetch_asset(job: tuple[str, str]) -> tuple[str, str, dict]:
        url, rel = job
        res = fetch_with_retries(url, accept_markdown=False)
        return url, rel, res

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for url, rel, res in pool.map(fetch_asset, asset_jobs):
            body = res.get("body") or b""
            ok = res["status"] == 200 and body and not is_html_body(body)
            if ok:
                write_bytes(out, rel, body)
                if rel.startswith("zoo-aquarium/screenshots/"):
                    aquarium_png += 1
                else:
                    research_assets += 1
            else:
                failed_assets += 1
                gaps.append(f"{url} asset failed (http {res['status']})")
            manifest.append(
                {
                    "url": url,
                    "kind": "asset",
                    "status": res["status"],
                    "bytes": len(body) if ok else 0,
                    "sha256": sha256_bytes(body) if ok else None,
                    "local_path": rel if ok else None,
                    "html_path": None,
                    "ok": bool(ok),
                    "error": None if ok else f"http {res['status']}",
                    "fetched_at": fetched_at,
                }
            )

    # Link coverage: every in-scope markdown/html link should resolve locally.
    missing_targets: list[str] = []
    for url in sorted(ok_md_urls):
        rel = local_paths(url, child_paths)["md"]
        text = (out / rel).read_text(encoding="utf-8")
        for dest in set(iter_markdown_dests(text)):
            target_url = canonicalize(dest)
            if not target_url:
                continue
            target = map_site_path_to_local(unquote(urlparse(target_url).path), child_paths)
            if target is None:
                continue
            if not (out / target).is_file():
                missing_targets.append(f"{url} -> {dest} (expected {target})")
        if page_kind(url) == "kcl-book":
            for m in re.finditer(r"\]\(([^)]+?\.md)(?:#[^)]*)?\)", text):
                dest = (out / Path(rel).parent / m.group(1)).resolve()
                try:
                    dest.relative_to(out.resolve())
                except ValueError:
                    continue
                if not dest.is_file():
                    missing_targets.append(f"{url} -> {m.group(1)}")

    for item in missing_targets:
        if item not in gaps:
            gaps.append(item)

    doctype_hits = sorted(
        str(p.relative_to(out))
        for p in out.rglob("*.md")
        if "<!DOCTYPE html>" in p.read_text(encoding="utf-8", errors="replace")
    )
    for rel in doctype_hits:
        gaps.append(f"{rel} contains <!DOCTYPE html>")

    counts = {
        "docs_md": docs_md,
        "book_md": book_md,
        "book_html": book_html,
        "aquarium_md": aquarium_md,
        "aquarium_png": aquarium_png,
        "research_md": research_md,
        "research_html": research_html,
        "research_assets": research_assets,
        "failed_pages": failed_pages,
        "failed_assets": failed_assets,
    }
    manifest_doc = {
        "fetched_at": fetched_at,
        "base": BASE,
        "counts": counts,
        "pages": manifest,
    }
    # Keep the GitHub section written by fetch_github_sources.py across refreshes.
    manifest_path = out / "manifest.json"
    if manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8"))
            if "github" in previous:
                manifest_doc["github"] = previous["github"]
        except json.JSONDecodeError:
            pass
    write_text(out, "manifest.json", json.dumps(manifest_doc, indent=2) + "\n")
    write_readme(out, fetched_at, counts, gaps, "manifest.json")

    print("Done.", flush=True)
    for key, value in counts.items():
        print(f"  {key}: {value}")
    print(f"  known_gaps: {len(gaps)}")
    if doctype_hits:
        print("ERROR: HTML leaked into Markdown files", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

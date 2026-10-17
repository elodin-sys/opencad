"""HTML and CSS for the design-review site. Pages link with relative paths so the output serves from any directory."""

from __future__ import annotations

import html
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from opencad.site.build import Design, Result

SECTION_TITLES = {
    "machine": ("Machines", "Assemblies of placed parts on measured joints, with motion sweeps, clearances and, where declared, fluid regions and simulations."),
    "part": ("Parts", "Standalone printed parts designed from datasheets, drawings and photos."),
    "corpus": ("Reconstruction corpus", "Parts rebuilt from public references and scored against held-back truth geometry."),
}
SECTION_LABEL = {"machine": "Machine", "part": "Part", "corpus": "Reconstruction"}
BACKEND_LABEL = {"build123d": "build123d", "cadquery": "CadQuery", "freecad": "FreeCAD", "zoo": "Zoo KCL"}

CSS = """
:root { --ink:#14212b; --muted:#5b6b75; --line:#dde3e6; --bg:#f5f6f4; --panel:#ffffff; --accent:#0f6e74; --accent-soft:#e3f0f0;
  --pass:#1f7a3a; --pass-soft:#e4f2e8; --fail:#b3261e; --fail-soft:#f8e5e3; --dark:#0f1d24; }
* { box-sizing:border-box; }
html { -webkit-text-size-adjust:100%; }
body { margin:0; font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; color:var(--ink); background:var(--bg); }
a { color:var(--accent); }
code { font:13px ui-monospace,SFMono-Regular,Menlo,monospace; background:#eef1f2; padding:1px 5px; border-radius:4px; }
.wrap { max-width:1180px; margin:0 auto; padding:0 24px; }
.top { background:var(--dark); color:#dbe7ea; }
.top .wrap { display:flex; align-items:center; justify-content:space-between; gap:20px; height:56px; }
.brand { color:white; font-weight:800; letter-spacing:-.02em; text-decoration:none; font-size:17px; }
.top nav { display:flex; gap:18px; font-size:13px; }
.top nav a { color:#b9cdd2; text-decoration:none; }
.top nav a:hover { color:white; }
.hero { background:var(--dark); color:#e8f0f2; padding:48px 0 56px; }
.hero .wrap { display:grid; grid-template-columns:1.05fr 1fr; gap:44px; align-items:center; }
.eyebrow { text-transform:uppercase; letter-spacing:.12em; font-size:11px; font-weight:700; color:#7fb7bb; margin:0 0 10px; }
.hero h1 { font-size:40px; line-height:1.08; letter-spacing:-.03em; margin:0 0 16px; color:white; }
.hero p.lede { font-size:16px; color:#c3d4d8; margin:0 0 26px; max-width:560px; }
.stats { display:flex; gap:30px; flex-wrap:wrap; }
.stats div { font-size:12px; color:#9db5bb; }
.stats b { display:block; font-size:26px; color:white; letter-spacing:-.02em; }
.showcase { display:block; border:1px solid #2a3c44; border-radius:14px; overflow:hidden; background:white; text-decoration:none; }
.showcase img { display:block; width:100%; aspect-ratio:4/3; object-fit:contain; background:white; }
.showcase span { display:flex; justify-content:space-between; gap:12px; padding:9px 14px; background:#12262e; color:#cfe0e4; font-size:12px; }
section.block { padding:52px 0 8px; }
section.block h2 { font-size:26px; letter-spacing:-.02em; margin:0 0 6px; }
section.block > .wrap > p.sub { color:var(--muted); margin:0 0 22px; max-width:760px; }
.cards { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; }
.card { display:flex; flex-direction:column; background:var(--panel); border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.card:hover { border-color:#b8c6cb; }
.card .media { display:block; background:white; border-bottom:1px solid var(--line); }
.card .media img { display:block; width:100%; aspect-ratio:4/3; object-fit:contain; }
.card .body { display:flex; flex-direction:column; flex:1; padding:16px 18px 18px; }
.card h3 { font-size:18px; margin:8px 0 6px; letter-spacing:-.015em; line-height:1.2; }
.card h3 a { color:var(--ink); text-decoration:none; }
.card p { margin:0 0 12px; color:var(--muted); font-size:14px; }
.facts { display:flex; flex-wrap:wrap; gap:4px 12px; margin-top:auto; font-size:12px; color:var(--muted); }
.row { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.tag { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); }
.pill { display:inline-block; font-size:11px; font-weight:700; padding:2px 8px; border-radius:999px; }
.pill.pass { color:var(--pass); background:var(--pass-soft); }
.pill.fail { color:var(--fail); background:var(--fail-soft); }
.pill.na { color:var(--muted); background:#eceff0; }
.actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:14px; }
.btn { display:inline-flex; align-items:center; min-height:34px; padding:6px 12px; border-radius:8px; font-size:13px; font-weight:700; text-decoration:none; background:var(--accent); color:white; }
.btn.secondary { background:#e6ecee; color:var(--ink); }
.steps { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.step { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:18px; }
.step b { display:block; font-size:12px; color:var(--accent); letter-spacing:.08em; text-transform:uppercase; margin-bottom:6px; }
.step h3 { margin:0 0 6px; font-size:17px; }
.step p { margin:0; color:var(--muted); font-size:14px; }
.callout { background:var(--panel); border:1px solid var(--line); border-left:5px solid var(--accent); border-radius:10px; padding:18px 22px; max-width:860px; }
.callout p { margin:0 0 8px; }
.callout p:last-child { margin:0; }
footer { margin-top:64px; background:var(--dark); color:#9db5bb; font-size:13px; padding:26px 0; }
footer .wrap { display:flex; justify-content:space-between; gap:20px; flex-wrap:wrap; }
.crumbs { font-size:13px; padding:18px 0 0; }
.crumbs a { text-decoration:none; }
.head { padding:10px 0 18px; }
.head h1 { font-size:32px; letter-spacing:-.025em; margin:6px 0 8px; line-height:1.12; }
.head p { color:var(--muted); margin:0; max-width:820px; }
.tabs { display:flex; gap:6px; flex-wrap:wrap; margin:16px 0 0; }
.tabs a { display:inline-flex; align-items:center; gap:7px; padding:6px 12px; border:1px solid var(--line); border-radius:8px; background:var(--panel); color:var(--ink); text-decoration:none; font-size:13px; font-weight:600; }
.tabs a.on { border-color:var(--accent); background:var(--accent-soft); }
.tabs .dot { width:8px; height:8px; border-radius:50%; background:var(--pass); }
.tabs .dot.fail { background:var(--fail); }
.viewer { display:block; width:100%; height:72vh; min-height:440px; border:1px solid var(--line); border-radius:12px; background:white; }
.still { display:block; width:100%; max-height:72vh; object-fit:contain; border:1px solid var(--line); border-radius:12px; background:white; }
.cols { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.45fr); gap:22px; margin-top:22px; align-items:start; }
.panel { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:18px 20px; margin-bottom:22px; }
.panel h2 { font-size:16px; margin:0 0 12px; letter-spacing:-.01em; }
dl.kv { display:grid; grid-template-columns:auto 1fr; gap:6px 16px; margin:0; font-size:14px; }
dl.kv dt { color:var(--muted); }
dl.kv dd { margin:0; font-variant-numeric:tabular-nums; }
table { width:100%; border-collapse:collapse; font-size:13px; }
th { text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); font-weight:700; padding:6px 8px; border-bottom:1px solid var(--line); }
td { padding:7px 8px; border-bottom:1px solid #edf0f1; vertical-align:top; }
th.num { text-align:right; }
.scroll { overflow-x:auto; }
.scroll td, .scroll th { white-space:nowrap; }
td.num { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
tr.fail td { background:#fdf4f3; }
.ev { color:var(--muted); font-size:12px; word-break:break-word; }
details { margin-top:4px; }
summary { cursor:pointer; font-weight:600; }
.intent { white-space:pre-wrap; color:var(--muted); font-size:14px; margin:10px 0 0; }
.files a { font-weight:600; }
@media (max-width:980px) { .hero .wrap, .cols { grid-template-columns:1fr; } .showcase { max-width:560px; } .cards { grid-template-columns:repeat(2,1fr); } .steps { grid-template-columns:repeat(2,1fr); } }
@media (max-width:620px) { .cards, .steps { grid-template-columns:1fr; } .hero h1 { font-size:30px; } .top nav { display:none; } .viewer { height:60vh; } }
"""


# assembly.html puts a fixed 380 px panel beside the model (stacked below 700 px here), and draws derived bodies such as
# chamber walls and fluid regions, which can enclose the machine; the site starts with those switched off
ASSEMBLY_VIEWER_PATCH = """<style>@media (max-width:700px){body{grid-template-columns:1fr;grid-template-rows:62vh auto;height:auto}
aside{border-left:0;border-top:1px solid #ddd}}</style>
<script type="module">
const mv = document.getElementById('mv');
const hideDerived = () => { for (const cb of document.querySelectorAll('input[data-body]'))
  if (cb.checked && cb.parentElement.textContent.includes('(derived')) cb.click(); };
if (mv.loaded) hideDerived(); else mv.addEventListener('load', hideDerived, { once: true });
</script>"""


def e(v: Any) -> str:
    return html.escape(str(v), quote=True)


def _page(title: str, root: str, body: str, built: str = "") -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><link rel="stylesheet" href="{root}assets/site.css"></head>
<body>
<header class="top"><div class="wrap"><a class="brand" href="{root}index.html">opencad</a>
<nav><a href="{root}index.html#machine">Machines</a><a href="{root}index.html#part">Parts</a><a href="{root}index.html#corpus">Corpus</a>
<a href="{root}bakeoff/index.html">Bake-off</a><a href="{root}index.html#how">How it works</a><a href="{root}index.html#evidence">Evidence</a></nav></div></header>
{body}
<footer><div class="wrap"><span>opencad: agent-authored CAD with the evidence left visible.</span><span>{e(built)}</span></div></footer>
</body></html>
"""


def _verdict(r: Result) -> str:
    p, f, _ = r.counts
    if not r.feedback:
        return '<span class="pill na">no gates</span>'
    cls, word = ("pass", "PASS") if r.ok else ("fail", "FAIL")
    return f'<span class="pill {cls}">{word} {p}/{p + f}</span>'


def _mb(n: int) -> str:
    return f"{n / 1048576:.1f} MB" if n >= 104858 else f"{n / 1024:.0f} KB"


def _dims(lo: Any, hi: Any) -> str | None:
    try:
        return " × ".join(f"{b - a:.1f}" for a, b in zip(lo, hi)) + " mm"
    except TypeError:
        return None


def _envelope(spec: dict[str, Any]) -> str | None:
    env = spec.get("envelope") or {}
    return _dims(env.get("min"), env.get("max")) if isinstance(env, dict) else None


def _card_facts(d: Design) -> list[str]:
    r = d.preferred
    facts = []
    if d.section == "machine":
        facts.append(f"{len(d.spec.get('parts') or [])} bodies")
        if d.leaves():
            facts.append(f"{len(d.leaves())} part designs")
    else:
        props_path = r.dir / "handoff" / "properties.json"
        if props_path.is_file():
            p = json.loads(props_path.read_text())
            dims = _dims(p.get("bbox_min"), p.get("bbox_max"))
            if dims:
                facts.append(dims)
    facts.append(", ".join(BACKEND_LABEL.get(b, b) for b in d.results))
    if d.truth:
        facts.append("scored truth case")
    return facts


def _card(d: Design, cards: dict[str, str]) -> str:
    r = d.preferred
    href = f"d/{e(d.name)}/{e(r.backend)}/"
    img = f'<a class="media" href="{href}"><img src="d/{e(d.name)}/{e(cards[d.name])}" alt="{e(d.title)} iso view" loading="lazy"></a>' if d.name in cards else ""
    stl = None if d.machine else next((p for p in d.prints() if p.suffix == ".stl" and p.stem == d.name), None)
    dl = f'<a class="btn secondary" href="{href}handoff/{e(stl.name)}" download>STL</a>' if stl else ""
    facts = "".join(f"<span>{e(f)}</span>" for f in _card_facts(d))
    return f"""<article class="card">{img}<div class="body">
<div class="row"><span class="tag">{SECTION_LABEL[d.section]}</span>{_verdict(r)}</div>
<h3><a href="{href}">{e(d.title)}</a></h3><p>{e(d.summary)}</p>
<div class="facts">{facts}</div>
<div class="actions"><a class="btn" href="{href}">Open design review</a>{dl}</div></div></article>"""


def index_page(designs: list[Design], cards: dict[str, str], built: str, bakeoffs: list[dict[str, Any]] | None = None) -> str:
    feat = next(d for d in designs if d.featured)
    machines = sum(d.section == "machine" for d in designs)
    printable = sum(1 for d in designs for p in d.prints() if p.suffix == ".stl")
    backends = sorted({b for d in designs for b in d.results})
    passing = sum(d.preferred.ok for d in designs)
    feat_img = f'<img src="d/{e(feat.name)}/{e(cards[feat.name])}" alt="{e(feat.title)}">' if feat.name in cards else ""
    sections = []
    for key, (title, sub) in SECTION_TITLES.items():
        group = [d for d in designs if d.section == key]
        if group:
            sections.append(f"""<section class="block" id="{key}"><div class="wrap"><p class="eyebrow">{len(group)} designs</p><h2>{title}</h2>
<p class="sub">{e(sub)}</p><div class="cards">{''.join(_card(d, cards) for d in group)}</div></div></section>""")
    if bakeoffs:
        latest = max(bakeoffs, key=lambda x: x["date"])
        sections.append(f"""<section class="block" id="bakeoff"><div class="wrap"><p class="eyebrow">{len(bakeoffs)} published comparisons</p><h2>Bake-off</h2>
<p class="sub">The same contract authored by the same agent on all four CAD backends, with every turn's tokens, dollars and time metered.
Latest: {e(_part_title(latest, {d.name: d.title for d in designs}))}, {e(latest['date'])}.</p>
<div class="actions"><a class="btn" href="bakeoff/index.html">Open the bake-off log</a></div></div></section>""")
    body = f"""<section class="hero"><div class="wrap"><div>
<p class="eyebrow">Agentic CAD pipeline</p>
<h1>Parts and machines, modelled by agents and checked by OpenCascade.</h1>
<p class="lede">Each design starts as a contract with a source for every number. A worker writes editable CAD on build123d, CadQuery,
FreeCAD or Zoo; the exported STEP is measured independently against the contract; and every handoff ships a STEP and an STL you can print.</p>
<div class="stats"><div><b>{len(designs)}</b>designs</div><div><b>{machines}</b>machines</div><div><b>{passing}</b>passing all gates</div>
<div><b>{printable}</b>printable STLs</div><div><b>{len(backends)}</b>CAD backends</div></div></div>
<a class="showcase" href="d/{e(feat.name)}/{e(feat.preferred.backend)}/">{feat_img}<span><b>Featured: {e(feat.title)}</b><span>Open the interactive review →</span></span></a>
</div></section>
{''.join(sections)}
<section class="block" id="how"><div class="wrap"><p class="eyebrow">How it works</p><h2>From intent to a printable handoff</h2>
<p class="sub">Python is the control plane. Agents do the modelling and spatial reasoning; every claim they make is re-measured on the exported geometry.</p>
<div class="steps">
<div class="step"><b>01 · Contract</b><h3>Design</h3><p>Sources (datasheets, drawings, photos, reference meshes) become one <code>contract.yaml</code> or <code>assembly.yaml</code> with provenance on every parameter.</p></div>
<div class="step"><b>02 · Model</b><h3>Build</h3><p>A worker plans the construction and writes parametric source on the chosen backend; a blockout checks scale and frame first.</p></div>
<div class="step"><b>03 · Gates</b><h3>Verify</h3><p>OpenCascade reads the STEP for envelope, mass properties, features, edits and export agreement: 12 gates per part, 14 per machine.</p></div>
<div class="step"><b>04 · Handoff</b><h3>Print</h3><p>The handoff is the gated STEP, an STL in millimetres, a GLB for the viewer, and the provenance that binds them to the source.</p></div>
</div></div></section>
<section class="block" id="evidence"><div class="wrap"><p class="eyebrow">Evidence</p><h2>Claims, verdicts and geometry</h2>
<div class="callout"><p><code>ok: true</code> in a stage file is the worker's claim. <code>gate_feedback.json</code> is the verdict, and the exported STEP is authoritative.</p>
<p>A failing design stays listed with its failing gates. A PASS means the geometry agrees with its contract within tolerance; it is not a physical test of the printed part.</p></div>
</div></section>"""
    return _page("opencad · design reviews", "", body, built)


def _kv(rows: list[tuple[str, Any]]) -> str:
    return '<dl class="kv">' + "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in rows if v not in (None, "", [])) + "</dl>"


def _file_rows(files: list[dict[str, Any]]) -> str:
    return "".join(f'<tr><td><a href="{e(f["href"])}" download>{e(f["name"])}</a></td><td>{e(f["kind"])}</td><td class="num">{_mb(f["bytes"])}</td></tr>' for f in files)


def _gates(r: Result) -> str:
    rows = []
    for g in r.feedback.get("gates") or []:
        ok = g.get("ok")
        res = '<span class="pill pass">PASS</span>' if ok else ('<span class="pill fail">FAIL</span>' if ok is False else '<span class="pill na">n/a</span>')
        ev = g.get("evidence") or ""
        ev = str(ev[0] if isinstance(ev, list) else ev)
        ev = ev if len(ev) <= 260 else ev[:260] + "…"
        means = f"<br><b>Means:</b> {e(g.get('failure_means'))}" if ok is False and g.get("failure_means") else ""
        rows.append(f'<tr class="{"fail" if ok is False else ""}"><td>{e(g.get("tier"))}</td><td><b>{e(g.get("id"))}</b><div class="ev">{e(g.get("title"))}</div></td>'
                    f'<td>{res}</td><td class="ev">{e(ev)}{means}</td></tr>')
    return "<table><tr><th>Tier</th><th>Gate</th><th>Result</th><th>Evidence</th></tr>" + "".join(rows) + "</table>"


def _facts(d: Design, r: Result, props: dict[str, Any]) -> str:
    p, f, n = r.counts
    rows: list[tuple[str, Any]] = [("Backend", BACKEND_LABEL.get(r.backend, r.backend)), ("Gates", f"{p} pass, {f} fail, {n} n/a")]
    if d.section == "machine":
        parts = d.spec.get("parts") or []
        kinds = {k: sum(1 for x in parts if x.get("kind") == k) for k in ("modelled", "purchased", "derived")}
        rows += [("Envelope", _envelope(d.spec)), ("Bodies", f"{len(parts)} ({', '.join(f'{v} {k}' for k, v in kinds.items() if v)})"),
                 ("Joints", len(d.spec.get("joints") or []) or None), ("Simulations", len(d.spec.get("simulations") or []) or None)]
    else:
        vol = props.get("volume")
        rows += [("Bounding box", _dims(props.get("bbox_min"), props.get("bbox_max"))), ("Volume", f"{vol / 1000:.2f} cm³" if vol else None),
                 ("Material", d.spec.get("material") or props.get("material")), ("Process", d.spec.get("process")),
                 ("Mass", f"{props['mass_g']:.1f} g" if props.get("mass_g") else None), ("Release", d.spec.get("release_status"))]
    rows.append(("Truth case", "yes, scored against held-back geometry" if d.truth else None))
    return _kv(rows)


def _leaves(leaves: list[dict[str, Any]]) -> str:
    if not leaves:
        return ""
    rows = []
    for lf in leaves:
        stl = [f for f in lf["files"] if f["kind"] == "STL"]
        step = [f for f in lf["files"] if f["kind"] in ("STEP", "STP")]
        links = " · ".join(f'<a href="{e(f["href"])}" download>{f["kind"]}</a>' for f in (*step, *stl)) or "no handoff"
        rows.append(f"<tr><td><b>{e(lf['leaf'])}</b><div class='ev'>{e(lf['design'])}</div></td><td>{_verdict(lf['result'])}</td><td class='files'>{links}</td></tr>")
    return f"""<div class="panel"><h2>Printable part designs</h2><table><tr><th>Part</th><th>Gates</th><th>Files</th></tr>{''.join(rows)}</table></div>"""


def _bom(d: Design) -> str:
    parts = d.spec.get("parts") or []
    if d.section != "machine" or not parts:
        return ""
    rows = "".join(f"<tr><td>{e(p.get('name'))}</td><td>{e(p.get('kind'))}</td><td class='ev'>{e(p.get('design') or '')}</td><td class='ev'>{e(p.get('material') or '')}</td></tr>"
                   for p in parts if isinstance(p, dict))
    return f'<div class="panel"><h2>Bill of materials</h2><table><tr><th>Body</th><th>Kind</th><th>Design</th><th>Material</th></tr>{rows}</table></div>'


def _print_panel(d: Design, downloads: list[dict[str, Any]]) -> str:
    if not downloads:
        return ""
    title = "Assembled machine" if d.machine else "Print files"
    return (f'<div class="panel"><h2>{title}</h2><table class="files"><tr><th>File</th><th>Kind</th><th class="num">Size</th></tr>'
            f'{_file_rows(downloads)}</table></div>')


def design_page(d: Design, r: Result, tabs: list[tuple[str, Result]], viewer: str | None, downloads: list[dict[str, Any]],
                leaves: list[dict[str, Any]], props: dict[str, Any], card: str | None, built: str) -> str:
    root = "../../../"
    tab_html = "".join(f'<a class="{"on" if b == r.backend else ""}" href="../{e(b)}/"><span class="dot{"" if tr.ok else " fail"}"></span>{e(BACKEND_LABEL.get(b, b))}</a>'
                       for b, tr in tabs)
    if viewer:
        media = f'<iframe class="viewer" src="{e(viewer)}" title="{e(d.title)} 3D viewer" loading="lazy"></iframe>'
    elif card:
        media = f'<img class="still" src="{e(card)}" alt="{e(d.title)} iso view">'
    else:
        media = ""
    failed = [g for g in r.feedback.get("gates") or [] if g.get("ok") is False]
    fail_note = (f'<div class="panel" style="border-left:5px solid var(--fail)"><h2>Failing gates</h2><p class="ev">'
                 f'{e(", ".join(g["id"] for g in failed))}. The geometry and handoff are published as built; read each gate below before printing.</p></div>') if failed else ""
    body = f"""<div class="wrap">
<div class="crumbs"><a href="{root}index.html#{d.section}">← {SECTION_TITLES[d.section][0]}</a></div>
<div class="head"><div class="row"><span class="tag">{SECTION_LABEL[d.section]}</span>{_verdict(r)}</div>
<h1>{e(d.title)}</h1><p>{e(d.summary)}</p><div class="tabs">{tab_html}</div></div>
{media}
<div class="cols"><div>
<div class="panel"><h2>Facts</h2>{_facts(d, r, props)}</div>
{_leaves(leaves)}
{_print_panel(d, downloads)}
<div class="panel"><h2>Source</h2><p class="ev"><a href="{e(d.spec_path.name)}">{e(d.spec_path.name)}</a> (design contract)</p>
<details><summary>Design intent</summary><p class="intent">{e(d.intent)}</p></details></div>
</div><div>
{fail_note}
<div class="panel"><h2>Gates</h2>{_gates(r)}</div>
{_bom(d)}
</div></div></div>"""
    return _page(f"{d.title} ({BACKEND_LABEL.get(r.backend, r.backend)}) · opencad", root, body, built)


def _part_title(entry: dict[str, Any], titles: dict[str, str]) -> str:
    return titles.get(entry["part"]) or entry["part"].replace("-", " ").capitalize()


def _duration(s: Any) -> str:
    if not isinstance(s, (int, float)):
        return "—"
    s = int(s)
    return f"{s // 3600}h {s % 3600 // 60:02d}m" if s >= 3600 else f"{s // 60}m {s % 60:02d}s"


def _note_html(note: str) -> str:
    parts = e(note).split("`")
    return "".join(f"<code>{p}</code>" if i % 2 else p for i, p in enumerate(parts))


def _bakeoff_entry(entry: dict[str, Any], titles: dict[str, str], prefs: dict[str, str]) -> str:
    title = e(_part_title(entry, titles))
    head = f'<a href="../d/{e(entry["part"])}/{e(prefs[entry["part"]])}/">{title}</a>' if entry["part"] in prefs else title
    rows = []
    usd = {b: c.get("codex_usd") for b, c in entry["backends"].items() if isinstance(c.get("codex_usd"), (int, float))}
    cheapest = min(usd, key=usd.get) if usd else None
    for b, c in entry["backends"].items():
        cls, word = ("pass", "PASS") if c["verdict"] == "PASS" else ("fail", "FAIL")
        gates = f'<span class="pill {cls}">{word} {c["passed"]}/{c["passed"] + c["failed"]}</span>'
        zoo = f"{c['zoo_credits']} credits, ${c['zoo_usd']:.2f}" if c.get("zoo_credits") is not None and c.get("zoo_usd") is not None else "—"
        dollars = f"${c['codex_usd']:,.2f}" if b in usd else "—"
        rows.append(f"<tr><td><b>{e(BACKEND_LABEL.get(b, b))}</b>{' <span class=\"tag\">lowest Codex</span>' if b == cheapest else ''}</td><td>{gates}</td>"
                    f"<td class='num'>{dollars}</td><td class='num'>{e(zoo)}</td><td class='num'>{c['tokens_input'] / 1e6:.1f}M</td>"
                    f"<td class='num'>{c['turns']}</td><td class='num'>{_duration(c.get('wall_s'))}</td></tr>")
    tags = sorted(set((entry.get("tags") or {}).values()))
    return f"""<article class="panel"><div class="row"><span class="tag">{e(entry['date'])}</span><span class="tag">tag {e(', '.join(tags))}</span></div>
<h2 style="font-size:20px;margin:6px 0 8px">{head}</h2><p class="ev" style="font-size:13px;margin:0 0 12px">{_note_html(entry.get('note') or '')}</p>
<div class="scroll"><table><tr><th>Backend</th><th>Gates</th><th class="num">Codex USD</th><th class="num">Zoo API</th><th class="num">Input tokens</th><th class="num">Turns</th><th class="num">Wall</th></tr>
{''.join(rows)}</table></div></article>"""


def bakeoff_page(entries: list[dict[str, Any]], designs: list[Design], built: str) -> str:
    titles = {d.name: d.title for d in designs}
    prefs = {d.name: d.preferred.backend for d in designs}
    body_entries = "".join(_bakeoff_entry(x, titles, prefs) for x in sorted(entries, key=lambda x: x["date"], reverse=True))
    if not body_entries:
        body_entries = '<p class="sub">No comparison has been published yet. <code>python -m opencad.bakeoff report</code> adds one when a part has a clean cell on every backend.</p>'
    body = f"""<div class="wrap"><div class="head" style="padding-top:28px"><p class="eyebrow" style="color:var(--accent)">Bake-off</p>
<h1>One contract, four CAD backends</h1>
<p>Each entry is the same design contract authored by Astra (<code>gpt-6-astra</code>, fast tier) on CadQuery, build123d, FreeCAD and Zoo KCL,
then gated by the same OpenCascade evaluator. Codex USD comes from the pinned price card; local kernels cost nothing to run, and the Zoo API
column is the prepaid balance drop for that cell. Newest first.</p></div>
<div class="callout" style="margin-bottom:22px"><p><code>python -m opencad.bakeoff report</code> appends an entry once every backend has a gate verdict,
Astra turns on its tag, no fallback to another worker, and every turn metered from a single exec (<code>sum</code> or <code>rollout</code>).
Runs with a re-billed resumed thread or a voided Zoo cell stay in <code>docs/bake-off-experiments.md</code> and off this page. A published entry is not rewritten.</p></div>
{body_entries}</div>"""
    return _page("Bake-off · opencad", "../", body, built)


def part_viewer(title: str, glb: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{e(title)}</title>
<script type="module" src="../../../../assets/model-viewer.min.js"></script>
<style>html,body{{margin:0;height:100%;background:#eef1f3}}model-viewer{{width:100%;height:100%;--poster-color:#eef1f3}}</style></head>
<body><model-viewer id="mv" src="{e(glb)}" alt="{e(title)}" camera-controls auto-rotate auto-rotate-delay="1500" rotation-per-second="18deg"
shadow-intensity="0.7" exposure="1.0" environment-image="neutral" interaction-prompt="none"></model-viewer>
<script>
// part GLBs carry no colour; tint them so the solid reads against the background
document.getElementById('mv').addEventListener('load', e => {{
  for (const m of e.target.model.materials) {{ m.pbrMetallicRoughness.setBaseColorFactor([0.55, 0.63, 0.72, 1]); m.pbrMetallicRoughness.setRoughnessFactor(0.6); }}
}});
</script></body></html>
"""


def redirect(url: str) -> str:
    return f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={e(url)}"><a href="{e(url)}">Continue</a>\n'


def not_found() -> str:
    body = """<div class="wrap" style="padding:80px 24px"><p class="eyebrow" style="color:var(--accent)">404</p><h1>Not published</h1>
<p>No design review lives at this address.</p><div class="actions"><a class="btn" href="/index.html">Return to the design index</a></div></div>"""
    return _page("Not found · opencad", "/", body)

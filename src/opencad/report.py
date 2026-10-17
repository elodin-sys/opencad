"""report.md, self-contained report.html, contact-sheet.png, and the handoff/ package."""

from __future__ import annotations

import base64
import html
import json
import shutil
from pathlib import Path
from typing import Any

from opencad.io import dump_json, provenance, sha256_file, sha256_tree
from opencad.orchestrator import Ctx


def _img_b64(path: Path) -> str:
    if not path or not Path(path).exists():
        return ""
    data = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def contact_sheet(ctx: Ctx, snaps: dict[str, str], out: Path, cell_w: int = 640) -> Path | None:
    from opencad.render import ALL_ORDER, sheet as compose

    def _path(v: Any) -> Path | None:
        return Path(v) if isinstance(v, (str, Path)) else None

    all_p, sym_p = _path(snaps.get("all")), _path(snaps.get("symmetry"))
    if all_p and all_p.exists() and sym_p and sym_p.exists():
        return compose({"all": all_p, "symmetry": sym_p}, out, (("all", "all nine"), ("symmetry", "symmetry")), cols=1, cell_w=cell_w * 2)
    if all_p and all_p.exists():
        shutil.copy2(all_p, out)
        return out
    paths = {k: p for k, v in snaps.items() if (p := _path(v)) and p.exists()}
    if not paths:
        return None
    try:
        return compose(paths, out, ALL_ORDER, cols=3, cell_w=cell_w)
    except FileNotFoundError:
        return None


def _fmt(v: Any, escape: bool = True) -> str:
    if isinstance(v, float):
        return f"{v:.4g}" if abs(v) < 1e-3 or abs(v) >= 1e6 else f"{v:.4f}".rstrip("0").rstrip(".")
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_fmt(x, escape) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k}: {_fmt(x, escape)}" for k, x in v.items()) + "}"
    return html.escape(str(v)) if escape else str(v)


def _table(rows: list[list[Any]], header: list[str]) -> str:
    h = "".join(f"<th>{html.escape(x)}</th>" for x in header)
    body = "".join("<tr>" + "".join(f"<td>{_fmt(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>"


def _md_table(rows: list[list[Any]], header: list[str]) -> str:
    def cell(v: Any) -> str:
        return _fmt(v, escape=False).replace("|", "\\|")

    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def build(ctx: Ctx, feedback: dict[str, Any]) -> dict[str, Any]:
    c = ctx.contract
    ver, exp, ins, edt, mdl, pln, blk = (ctx.load_stage(s) or {} for s in ("verify", "export", "inspect", "edit", "model", "plan", "blockout"))
    snaps = ver.get("snapshots", {})
    sheet = contact_sheet(ctx, snaps, ctx.results_dir / "contact-sheet.png")

    # measured vs expected rows
    rows: list[list[Any]] = []
    bb = ins.get("bbox", {})
    if bb:
        rows.append(["bbox min (STEP)", bb.get("expected_min"), bb.get("measured_min"), f"±{bb.get('tolerance')}", "ok" if bb.get("ok") else "FAIL"])
        rows.append(["bbox max (STEP)", bb.get("expected_max"), bb.get("measured_max"), f"±{bb.get('tolerance')}", "ok" if bb.get("ok") else "FAIL"])
    for name, row in (ins.get("symmetry") or {}).items():
        band = f"max ≤{row.get('max_deviation')} p95 ≤{row.get('p95_deviation')}"
        rows.append([f"symmetry {name} ({row.get('plane')}={row.get('at')})", band, f"max {row.get('max')} p95 {row.get('p95')} at {row.get('worst_point')}", band, "ok" if row.get("ok") else "FAIL"])
    visual = mdl.get("visual_check")
    rows.append(["worker visual review", "Visual: line under ## Verification", visual or "missing", "", "ok" if visual else "n/a"])
    corr_path = ctx.results_dir / "correct.json"
    if corr_path.exists():
        corr = json.loads(corr_path.read_text(encoding="utf-8"))
        delta = corr.get("delta_vs_previous")
        if delta:
            rows.append(["correct delta vs previous", "", delta, "", ""])
    for k, label in (("volume", "volume mm3 (STEP)"), ("surface_area", "surface area mm2 (STEP)")):
        q = ins.get(k, {})
        if q.get("declared"):
            rows.append([label, q.get("expected"), q.get("measured"), f"±{q.get('band')}", "ok" if q.get("ok") else "FAIL"])
    com = ins.get("center_of_mass", {})
    if com.get("declared"):
        rows.append(["centre of mass mm (STEP)", com.get("expected"), com.get("measured"), f"±{com.get('tolerance')}", "ok" if com.get("ok") else "FAIL"])
    a = ver.get("analyze", {})
    if a:
        rows.append(["volume mm3 (engine analyze)", (c.acceptance.volume.expected if c.acceptance.volume else "-"), a.get("volume_mm3"), "", "ok" if ver.get("volume", {}).get("ok") else "FAIL"])
    for sid, s in ins.get("sections", {}).items():
        m = s.get("measured", {})
        exp_ = next((x for x in c.acceptance.sections if x.id == sid), None)
        rows.append([f"section {sid} ({s['plane']}={s['at']}) area/loops/holes", [exp_.expect.area, exp_.expect.loops, exp_.expect.holes] if exp_ else "", [m.get("area"), m.get("loops"), m.get("holes")], "", "ok" if s.get("ok") else "FAIL"])
    for fid, f in ins.get("faces", {}).items():
        rows.append([f"face {fid} ({f['plane']}={f['at']} {f['normal']})", f.get("area_expected", "present"), f.get("area"), "", "ok" if f.get("ok") else "FAIL"])
    for fid, f in ins.get("features", {}).items():
        rows.append([f"feature {fid} ({f['kind']}{', optional' if f['optional'] else ''})", f"{len(f['checks'])} checks", "; ".join(ch["method"] + (":" + str(ch.get("states")) if ch.get("states") else "") for ch in f["checks"]), "", "ok" if f.get("ok") else ("n/a" if f.get("ok") is None else "FAIL")])
    for t in edt.get("tests", []):
        rows.append([f"edit {t['parameter']} {t['delta']:+g}", {k: v.get("expected") for k, v in t.get("checks", {}).items()}, {k: v.get("measured") for k, v in t.get("checks", {}).items()}, "", "ok" if t.get("ok") else "FAIL"])
    dev = ins.get("deviation", {})
    if dev.get("reference"):
        rows.append(["deviation p95 / hausdorff / silhouette IoU vs reference", c.acceptance.deviation.model_dump() if c.acceptance.deviation else "not declared", [dev.get("p95"), dev.get("hausdorff_estimate"), dev.get("silhouette_iou_min")], "", "ok" if dev.get("ok") else ("n/a" if dev.get("ok") is None else "FAIL")])

    gate_rows = [[g["tier"], g["id"], g["title"], "PASS" if g["ok"] else ("n/a" if g["ok"] is None else "FAIL"), "; ".join(g["evidence"])] for g in feedback["gates"]]
    prov_rows = [[p.name, f"{p.value} {p.unit}", p.provenance, p.tolerance, p.source or p.formula or p.rationale or ""] for p in c.parameters]

    engine_total = feedback["gates"][9]["details"].get("engine_calls_total") if len(feedback["gates"]) > 9 else None
    threads = {"plan": pln.get("codex", {}).get("thread_id"), "model": mdl.get("thread_id"), "model_retry": (mdl.get("retry") or {}).get("codex", {}).get("thread_id"), "blockout": blk.get("thread_id")}
    src_path = ctx.entry
    src_text = src_path.read_text(encoding="utf-8") if src_path.exists() else "(missing)"
    lang_id = ctx.backend.language.id
    prov = provenance()
    verdict = "PASS" if feedback["ok"] else "FAIL"

    view_lines = [f"![contact sheet](contact-sheet.png)" if sheet else "(no snapshots)"]
    view_lines += [f"- `{k}`: `{snaps[k]}`" for k in ("front", "back", "left", "right-side", "top", "bottom", "iso", "iso2", "iso-below", "all", "symmetry") if k in snaps]
    if snaps.get("symmetry"):
        view_lines += ["", f"![symmetry heatmap]({snaps['symmetry']})"]
    view_lines.append(f"- worker visual review: {visual or 'missing'}")
    md = [f"# {c.name} — opencad report", "", f"**Verdict: {verdict}** — {feedback['summary']['pass']} gates pass, {feedback['summary']['fail']} fail, {feedback['summary']['not_applicable']} not applicable. "
          f"Release status: `{c.release_status}`. This report establishes agreement between the {lang_id} model, its exports and the contract"
          + (" and the reference model" if dev.get("reference") else "") + ". It is not physical or engineering validation.", "",
          f"Intent: {c.intent}", "", "## Views", "", *view_lines, "",
          "## Measured vs expected", "", _md_table(rows, ["check", "expected", "measured", "tolerance", "verdict"]), "",
          "## Gates", "", _md_table(gate_rows, ["tier", "gate", "title", "verdict", "evidence"]), "",
          "## Contract parameters and provenance", "", _md_table(prov_rows, ["parameter", "value", "provenance", "tolerance", "source / formula / rationale"]), "",
          "## Provenance", "", f"- backend: {ctx.backend_id}", f"- engine: {prov.get('engine_version')}", f"- git: {prov['git']}", f"- worker threads: {threads}", f"- engine calls (all stages): {engine_total}",
          f"- source sha256: {sha256_file(src_path) if src_path.exists() else None}", f"- STEP sha256: {exp.get('files', {}).get('step', {}).get('sha256')} deterministic={exp.get('files', {}).get('step', {}).get('deterministic')}",
          f"- design bundle: {json.dumps(sha256_tree(ctx.design_dir))}", "",
          "## Open questions", "", *(f"- {q}" for q in c.open_questions), *(["- (contract lists none)"] if not c.open_questions else []),
          *(["", "Worker (model) open questions:", mdl.get("codex_report", {}).get("Open questions", "")] if mdl.get("codex_report", {}).get("Open questions") else []), "",
          f"## Source ({lang_id})", "", f"```{lang_id}", src_text.rstrip(), "```", ""]
    (ctx.results_dir / "report.md").write_text("\n".join(md), encoding="utf-8")

    css = "body{font:14px/1.45 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:2rem auto;max-width:1100px;color:#222}table{border-collapse:collapse;width:100%;margin:.5rem 0 1.5rem}th,td{border:1px solid #ddd;padding:4px 8px;text-align:left;vertical-align:top;font-size:13px}th{background:#f4f4f4}img{max-width:100%;border:1px solid #ddd}pre{background:#f7f7f7;padding:1rem;overflow:auto;font-size:12px}.pass{color:#1b7f3b;font-weight:600}.fail{color:#b00020;font-weight:600}.na{color:#777}h2{margin-top:2rem}"
    def v(x: str) -> str:
        return f'<span class="{ "pass" if x in ("PASS", "ok") else "fail" if x == "FAIL" else "na"}">{x}</span>'
    gate_html = "".join(f"<tr><td>{g['tier']}</td><td><code>{g['id']}</code></td><td>{html.escape(g['title'])}</td><td>{v('PASS' if g['ok'] else 'n/a' if g['ok'] is None else 'FAIL')}</td><td>{'<br>'.join(html.escape(e) for e in g['evidence'])}</td><td>{html.escape(g['failure_means'])}<br><i>{html.escape(g['knob'])}</i></td></tr>" for g in feedback["gates"])
    rows_html = "".join("<tr>" + "".join(f"<td>{v(_fmt(cell)) if i == 4 else _fmt(cell)}</td>" for i, cell in enumerate(r)) + "</tr>" for r in rows)
    sections_imgs = ""
    for k in ("all", "symmetry", "four-ways"):
        if k in snaps and Path(snaps[k]).exists():
            sections_imgs += f'<h3>{k}</h3><img src="{_img_b64(Path(snaps[k]))}" alt="{k}">'
    blk_img = blk.get("snapshots", {}).get("four-ways")
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(c.name)} — opencad report</title><style>{css}</style></head><body>
<h1>{html.escape(c.name)} — opencad report</h1>
<p><b>Verdict: {v(verdict)}</b> — {feedback['summary']['pass']} gates pass, {feedback['summary']['fail']} fail, {feedback['summary']['not_applicable']} not applicable. Release status <code>{c.release_status}</code>.
This report establishes agreement between the {html.escape(lang_id)} model, its exports and the contract{' and the reference model' if dev.get('reference') else ''}. It is <b>not</b> physical or engineering validation.</p>
<p>{html.escape(c.intent)}</p>
<h2>Views</h2>{f'<img src="{_img_b64(sheet)}" alt="contact sheet">' if sheet else '<p>no snapshots</p>'}{sections_imgs}
{f'<h3>blockout checkpoint</h3><img src="{_img_b64(Path(blk_img))}" alt="blockout">' if blk_img else ''}
<h2>Measured vs expected</h2><table><thead><tr><th>check</th><th>expected</th><th>measured</th><th>tolerance</th><th>verdict</th></tr></thead><tbody>{rows_html}</tbody></table>
<h2>Gates</h2><table><thead><tr><th>tier</th><th>gate</th><th>title</th><th>verdict</th><th>evidence</th><th>failure means / knob</th></tr></thead><tbody>{gate_html}</tbody></table>
<h2>Contract parameters and provenance</h2>{_table(prov_rows, ["parameter", "value", "provenance", "tolerance", "source / formula / rationale"])}
<h2>Provenance</h2><ul><li>backend: {html.escape(ctx.backend_id)}</li><li>engine: {html.escape(str(prov.get('engine_version')))}</li><li>git: {html.escape(json.dumps(prov['git']))}</li><li>worker threads: {html.escape(json.dumps(threads))}</li><li>engine calls (all stages): {engine_total}</li>
<li>source sha256: {sha256_file(src_path) if src_path.exists() else None}</li><li>STEP sha256: {exp.get('files', {}).get('step', {}).get('sha256')} (deterministic={exp.get('files', {}).get('step', {}).get('deterministic')})</li></ul>
<h2>Open questions</h2><ul>{''.join(f'<li>{html.escape(q)}</li>' for q in c.open_questions) or '<li>(contract lists none)</li>'}</ul>
{('<h3>Codex open questions (model stage)</h3><pre>' + html.escape(mdl.get('codex_report', {}).get('Open questions', '')) + '</pre>') if mdl.get('codex_report', {}).get('Open questions') else ''}
<h2>Source ({html.escape(lang_id)})</h2><pre>{html.escape(src_text)}</pre>
</body></html>"""
    (ctx.results_dir / "report.html").write_text(page, encoding="utf-8")

    handoff = write_handoff(ctx, exp, ins, feedback, threads, engine_total)
    return {"ok": True, "report_html": str(ctx.results_dir / "report.html"), "report_md": str(ctx.results_dir / "report.md"), "contact_sheet": str(sheet) if sheet else None, "handoff": handoff, "verdict": verdict}


def write_handoff(ctx: Ctx, exp: dict[str, Any], ins: dict[str, Any], feedback: dict[str, Any], threads: dict[str, Any], engine_total: int | None) -> dict[str, Any]:
    c = ctx.contract
    hd = ctx.results_dir / "handoff"
    if hd.exists():
        shutil.rmtree(hd)
    hd.mkdir(parents=True)
    files: dict[str, Any] = {}
    for fmt, meta in exp.get("files", {}).items():
        src = Path(meta["path"])
        if src.exists():
            dst = hd / src.name
            shutil.copy2(src, dst)
            files[fmt] = {"file": dst.name, "sha256": meta["sha256"], "bytes": meta["bytes"]}
    export_dir = ctx.results_dir / "export"
    for extra in export_dir.glob("*.FCStd"):
        dst = hd / extra.name
        shutil.copy2(extra, dst)
        files.setdefault("fcstd", {"file": dst.name, "sha256": sha256_file(dst), "bytes": dst.stat().st_size})
    brep = ins.get("brep", {})
    density = c.density_kg_m3
    vol = brep.get("volume")
    props = {
        "units": {"length": "mm", "volume": "mm3", "area": "mm2", "mass": "g", "density": "kg/m3"},
        "volume": vol, "surface_area": brep.get("surface_area"), "center_of_mass": brep.get("center_of_mass"),
        "bbox_min": brep.get("bbox_min"), "bbox_max": brep.get("bbox_max"),
        "inertia_about_com_unit_density": brep.get("inertia_about_com"),
        "density_kg_m3": density, "material": c.material,
        "mass_g": (vol * 1e-9 * density * 1e3) if (vol and density) else None,
        "mass_note": "mass = volume x declared density; density is a contract assumption, not a measurement" if density else "no density declared; no mass claim",
        "source": "OpenCascade GProp on the exported STEP",
    }
    dump_json(hd / "properties.json", props)
    faces = {"named_faces": ins.get("faces", {}), "contract_faces": [f.model_dump() for f in c.acceptance.faces], "planar_faces_total": brep.get("planar_faces")}
    dump_json(hd / "faces.json", faces)
    prov = provenance({
        "part": c.name, "release_status": c.release_status, "verdict": "PASS" if feedback["ok"] else "FAIL",
        "gates": {"passed": feedback["passed"], "failed": feedback["failed"], "not_applicable": feedback["not_applicable"]},
        "design_bundle_sha256": sha256_tree(ctx.design_dir), "kcl_sha256": sha256_tree(ctx.part_dir, ctx.backend.language.suffixes),
        "source_sha256": sha256_tree(ctx.part_dir, ctx.backend.language.suffixes), "backend": ctx.backend_id, "engine_version": provenance().get("engine_version"),
        "exports": files, "codex_threads": threads, "engine_calls_total": engine_total,
        "physical_validation": "not performed", "engineering_review": "not performed",
    })
    dump_json(hd / "provenance.json", prov)
    return {"dir": str(hd), "files": files, "properties": str(hd / "properties.json"), "faces": str(hd / "faces.json"), "provenance": str(hd / "provenance.json")}

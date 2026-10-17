"""`python -m opencad quick <main.kcl|part.step> --contract <contract.yaml>`: the worker's local critic.

Exports the KCL once (hosted, cached by the sha256 of the KCL tree under ~/.cache/opencad/engine/), measures
the STEP with OpenCascade exactly as the inspect stage does, and prints the same measured-vs-expected lines the
correction brief carries. Nothing under results/ is touched, so a worker can call it after every feature group
instead of rebuilding its own verify script.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

from opencad import gates
from opencad.backends.base import EngineError
from opencad.backends.registry import get
from opencad.contract import load_contract
from opencad.io import sha256_file, utc_now
from opencad.paths import NESTED, PARTS_BASE, REPO_ROOT, design_dir, design_name, results_root

QUOTED_RE = re.compile(r"""["']([^"'\n]+)["']""")
SYMMETRY_SAMPLES = 8000  # the inspect gate samples 60,000; the inner loop needs the band, not the rarest outlier


def engine_cache_dir() -> Path:
    return Path(os.environ.get("OPENCAD_ENGINE_CACHE") or (Path.home() / ".cache" / "opencad" / "engine"))


def referenced_sources(entry: Path, suffixes: tuple[str, ...]) -> list[Path]:
    """Source files a scratch main pulls in from outside its own directory: a KCL `import x from "<path>"` or a Python
    `sys.path.insert(0, "<part dir>")` (decompose scratch mains reference `parts/<backend>/<part>/`). Repository paths only."""
    home = entry.parent.resolve()
    out: list[Path] = []
    for lit in QUOTED_RE.findall(entry.read_text(encoding="utf-8", errors="replace")):
        p = (Path(lit) if lit.startswith("/") else home / lit).resolve()
        if p == REPO_ROOT or not p.is_relative_to(REPO_ROOT) or p.is_relative_to(home) or not p.exists():
            continue
        out += [p] if p.is_file() and p.suffix in suffixes else sorted(q for q in p.rglob("*") if q.suffix in suffixes) if p.is_dir() else []
    return out


def tree_key(entry: Path, fmt: str) -> str:
    """Cache key of an export: format, engine, the entry file's name, every source in its directory tree and every repository
    source it references. The entry name matters: two entries in one directory (a module's standalone scratch and a composed
    entry) are different parts of the same tree."""
    be = get()
    h = hashlib.sha256()
    h.update(f"{fmt}:{be.id}:{be.engine.version()}:{entry.name}".encode())
    suffixes = be.language.suffixes
    for f in sorted(p for p in entry.parent.rglob("*") if p.suffix in suffixes and p.relative_to(entry.parent).parts[0] not in NESTED):
        h.update(b"|" + f.relative_to(entry.parent).as_posix().encode() + b":" + sha256_file(f).encode())
    for f in referenced_sources(entry, suffixes):
        h.update(b"|" + f.as_posix().encode() + b":" + sha256_file(f).encode())
    return h.hexdigest()


def export_cached_many(entry: Path, fmts: tuple[str, ...], *, ledger: Path | None = None,
                       rows_out: list[dict[str, Any]] | None = None) -> dict[str, tuple[Path, bool]]:
    """Each format once per source-tree hash; a missing STEP and STL come from one engine build where the engine has one.
    Returns {fmt: (path, cache_hit)}; the engine's own ledger rows (start, seconds, startup, peak RSS) go to `ledger` and
    `rows_out`, also when the build fails."""
    be = get()
    dests = {f: engine_cache_dir() / tree_key(entry, f) / f"output.{f}" for f in fmts}
    no_cache = os.environ.get("OPENCAD_NO_CACHE", "") in ("1", "true", "yes")
    out = {f: (d, True) for f, d in dests.items() if d.exists() and not no_cache}
    missing = [f for f in fmts if f not in out]
    if not missing:
        return out
    tmp = dests[missing[0]].parent / "tmp"
    build = getattr(be.engine, "build", None)
    try:
        if build is not None and set(missing) <= {"step", "stl"}:
            r = build(entry, analyze=False, step=tmp / f"{entry.stem}.step" if "step" in missing else None,
                      stl=tmp / f"{entry.stem}.stl" if "stl" in missing else None, lock=False)
            written = {f: r[f] for f in missing}
        else:
            written = {f: be.engine.export(entry, tmp / f, f, deterministic=True, lock=False)[0] for f in missing}
    finally:
        rows = be.engine.reset_ledger()
        if rows_out is not None:
            rows_out.extend(rows)
        if ledger is not None:
            ledger.parent.mkdir(parents=True, exist_ok=True)
            with ledger.open("a", encoding="utf-8") as fh:
                for row in rows:
                    fh.write(json.dumps({"ts": utc_now(), **row, "via": "opencad quick"}, default=str) + "\n")
    for f in missing:
        dests[f].parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(written[f]), str(dests[f]))
        out[f] = (dests[f], False)
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def source_size(target: Path) -> dict[str, Any] | None:
    """The traced-geometry check on a Python source: the part directory's sources, or a scratch entry and what it references."""
    if target.suffix != ".py":
        return None
    from opencad.backends.pythonlang import source_files, source_size_of

    home = target.parent.resolve()
    files = source_files(home) if home.is_relative_to(PARTS_BASE.resolve()) else [target, *referenced_sources(target, (".py",))]
    return source_size_of(files)


def budget_lines(size: dict[str, Any] | None, rows: list[dict[str, Any]], *, cached: bool) -> list[str]:
    from opencad import resources

    lines = []
    if size is not None:
        lines.append(f"source: {size['lines']} lines, {size['numeric_literals']} numeric literals (limits {size['max_lines']}/{size['max_literals']})"
                     + ("" if size["ok"] else f"; FAIL: {gates.traced_geometry_note(size)}"))
    if rows:
        peak = max(int(r.get("peak_rss") or 0) for r in rows)
        killed = any(r.get("oom_killed") for r in rows)
        lines.append(f"engine: peak RSS {resources.gb(peak)} of the {resources.gb(resources.runner_budget())} budget (OPENCAD_ENGINE_MEM_GB)"
                     + ("; FAIL: killed for memory, the build must use far fewer operations" if killed else ""))
    elif cached:
        lines.append("engine: cached export, no engine call")
    return lines


def infer_contract(target: Path) -> Path | None:
    try:
        rel = target.resolve().relative_to(PARTS_BASE.resolve())
    except ValueError:
        return None
    # parts/<backend>/<part>/... or parts/<backend>/<asm>/parts/<leaf>/...
    part = design_name(rel.parts[1:]) if len(rel.parts) > 1 else rel.parts[0]
    p = design_dir(part) / "contract.yaml"
    return p if p.exists() else None


def run(target: Path, contract_path: Path | None, *, with_stl: bool = False, design_dir: Path | None = None, ledger: Path | None = None, as_json: bool = False, show_all: bool = False) -> int:
    from opencad.stages import inspect_stage

    target = Path(target)
    contract_path = Path(contract_path) if contract_path else infer_contract(target)
    if contract_path is None or not contract_path.exists():
        print("quick: no contract; pass --contract designs/<part>/contract.yaml", flush=True)
        return 2
    try:
        rel = target.resolve().relative_to(PARTS_BASE.resolve())
        if rel.parts:
            from opencad.backends.registry import set_backend

            set_backend(rel.parts[0])
    except ValueError:
        pass
    c = load_contract(contract_path)
    design_dir = Path(design_dir) if design_dir else contract_path.parent
    hits: dict[str, bool] = {}
    views = with_stl
    has_reference = c.acceptance.deviation is not None and any((design_dir / "reference").glob("reference.*"))
    needs_stl = bool(c.acceptance.passages or c.acceptance.thickness or c.acceptance.symmetry or has_reference)  # these checks voxelize or sample the mesh
    if needs_stl and not with_stl:
        print("quick: the contract declares passages/thickness/symmetry/deviation; exporting the STL for those checks (add --stl for the nine views)", flush=True)
        with_stl = True
    dest_dir = Path(ledger).parent if ledger else results_root() / "_quick" / contract_path.parent.name
    rows: list[dict[str, Any]] = []
    size = source_size(target)
    if target.suffix in get().language.suffixes:
        try:
            got = export_cached_many(target, ("step", "stl") if with_stl else ("step",), ledger=ledger, rows_out=rows)
        except EngineError:
            for line in budget_lines(size, rows, cached=False):
                print(line, flush=True)
            raise
        step, hits["step"] = got["step"]
        stl = None
        if with_stl:
            stl, hits["stl"] = got["stl"]
    else:
        step = target
        stl = target.with_suffix(".stl") if target.with_suffix(".stl").exists() else None
    out: dict[str, Any] = inspect_stage.measure(step, stl, c, design_dir, symmetry_samples=SYMMETRY_SAMPLES, deviation_map=dest_dir / "deviation-map.png")
    ok = bool(out["ok"]) and (size is None or size["ok"])
    if as_json:
        print(json.dumps({**{k: v for k, v in out.items() if k != "mesh" or v is None or "components_watertight" in v}, "ok": ok, "source_size": size}, default=str)[:200000])
        return 0 if ok else 1
    b = out["brep"]
    tables = ("sections", "faces", "cylinders", "planes", "dimensions", "solids", "clearances", "passages", "thickness", "probes", "cylinder_counts", "gears", "meshes")
    counts = " ".join(f"{k}={sum(1 for x in out[k].values() if x.get('ok'))}/{len(out[k])}" for k in tables if out.get(k))
    how = ("cached export" if hits.get("step") else "exported") if target.suffix in get().language.suffixes else "given STEP"
    print(f"quick {'PASS' if ok else 'FAIL'} ({how}): valid={b['valid']} solids={b['solids']} (expected {c.acceptance.solid_count}) "
          f"volume={b['volume']:.3f} bbox={[round(v, 3) for v in b['bbox_min']]}..{[round(v, 3) for v in b['bbox_max']]} {counts}", flush=True)
    for line in budget_lines(size, rows, cached=bool(hits.get("step"))):
        print(line, flush=True)
    lines = [line for _, line in gates.inspection_items(out, c, only_failed=not show_all)] if show_all else gates.inspection_lines(out, c)
    if out["ok"]:
        print("every contract check passes on this STEP" + ("" if not out.get("mesh") else f"; STL watertight={out['mesh'].get('watertight')}"))
    for l in lines:
        print(l)
    if out.get("mesh") and not gates.mesh_watertight(out["mesh"], c.acceptance.solid_count):
        print(f"- STL not watertight: components {out['mesh'].get('components')} watertight {out['mesh'].get('components_watertight')} open edges {out['mesh'].get('open_edges')}")
    from opencad import render

    refs = render.reference_renders(design_dir / "sources")
    if views or refs:
        dest_dir.mkdir(parents=True, exist_ok=True)
        mesh_src = Path(stl) if stl and Path(stl).exists() else step
        angles = render.DEFAULT_VIEWS if views else tuple(a for a in render.DEFAULT_VIEWS if a in refs)
        snaps = render.render_snapshots(mesh_src, dest_dir, angles, px=480, contract=c if views else None)
        if views:
            qv = dest_dir / "quick-views.png"
            if snaps.get("all") and snaps.get("symmetry"):
                render.sheet({"all": Path(snaps["all"]), "symmetry": Path(snaps["symmetry"])}, qv, (("all", "all nine"), ("symmetry", "symmetry")), cols=1, cell_w=960)
            elif snaps.get("all"):
                shutil.copy2(snaps["all"], qv)
            print(f"quick-views: {qv}", flush=True)
        if refs:  # the arm's input renders beside this part, same views: the visual check a worker can act on
            qc = render.compare_sheet(dest_dir, refs, dest_dir / "quick-compare.png")
            if qc:
                ious = render.reference_silhouettes(dest_dir, refs)
                print(f"quick-compare: {qc} (input render | your part per view; silhouette IoU {ious})", flush=True)
        for name, row in (out.get("symmetry") or {}).items():
            print(gates.symmetry_line(name, row), flush=True)
    return 0 if ok else 1

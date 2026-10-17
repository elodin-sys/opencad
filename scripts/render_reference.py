#!/usr/bin/env python
"""Evaluator-side renders of a reference STEP/STL for the design agent: orthographic views and section drawings.

The agent may see pictures of the reference (with a mm grid) but never the CAD file itself. Pure
matplotlib software rendering: no OpenGL, no Zoo calls.

  python scripts/render_reference.py truth/cases/x/truth/part.step out/ --views top,front,right,iso --sections z=3,x=10.5
"""

from __future__ import annotations

import argparse
import math
import tempfile
from pathlib import Path

import matplotlib
import numpy as np
import trimesh

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

VIEWS = {
    # rotation applied to (x, y, z); screen u = row 0, v = row 1, depth toward viewer = row 2
    "top": np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float),
    "bottom": np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], float),
    "front": np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float),
    "back": np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], float),
    "right": np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], float),
    "left": np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], float),
}


def _iso(viewer: tuple[float, float, float] = (1.0, -1.0, 1.0)) -> np.ndarray:
    """Orthographic basis looking from `viewer` toward the origin, screen-up as close to +z as possible; row 2 is depth toward the viewer."""
    w = np.asarray(viewer, float)
    w /= np.linalg.norm(w)
    u = np.cross([0.0, 0.0, 1.0], w)
    u /= np.linalg.norm(u)
    v = np.cross(w, u)
    return np.array([u, v, w])


VIEWS["iso"] = _iso((1.0, -1.0, 1.0))  # from +x, -y, +z (front-right-top)
VIEWS["iso2"] = _iso((-1.0, 1.0, 1.0))  # from -x, +y, +z (back-left-top)
VIEWS["iso-below"] = _iso((1.0, -1.0, -1.0))


def load_mesh(path: Path, deflection: float = 0.05) -> trimesh.Trimesh:
    if path.suffix.lower() in (".step", ".stp"):
        from opencad.truth.scorer import step_to_mesh

        tmp = Path(tempfile.mkdtemp(prefix="render-")) / "ref.stl"
        step_to_mesh(path, tmp, deflection=deflection)
        path = tmp
    m = trimesh.load(path, force="mesh")
    if isinstance(m, trimesh.Scene):
        m = trimesh.util.concatenate([g for g in m.geometry.values()])
    return m


def _grid_step(extent: float) -> float:
    for s in (0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500):
        if extent / s <= 24:
            return s
    return 1000


def _fine(mesh: trimesh.Trimesh, rel_edge: float = 0.015, max_faces: int = 400_000) -> trimesh.Trimesh:
    """Painter's-algorithm ordering needs small triangles: split long edges so no edge exceeds rel_edge * extent."""
    max_edge = float(mesh.extents.max()) * rel_edge
    v, f = trimesh.remesh.subdivide_to_size(mesh.vertices, mesh.faces, max_edge=max_edge, max_iter=8)
    if len(f) > max_faces:
        return mesh
    return trimesh.Trimesh(v, f, process=False)


def render_view(mesh: trimesh.Trimesh, view: str, out: Path, px: int = 1600, title: str | None = None, grid: bool = True) -> Path:
    R = VIEWS[view]
    mesh = _fine(mesh)
    v = mesh.vertices @ R.T
    tri = v[mesh.faces]  # (n, 3, 3)
    depth = tri[:, :, 2].mean(axis=1)
    order = np.argsort(depth)  # far first
    n = mesh.face_normals @ R.T
    light = np.array([0.3, 0.4, 0.866])
    shade = 0.30 + 0.70 * np.clip(n @ light, 0, 1)
    # back faces (normal pointing away from viewer) are darker
    shade = np.where(n[:, 2] < 0, shade * 0.6, shade)
    # depth cue so coplanar features (pins, steps) read in axis-aligned views: nearer is lighter
    drange = depth.max() - depth.min()
    if drange > 1e-9:
        shade = shade * (0.7 + 0.3 * (depth - depth.min()) / drange)
    base = np.array([0.72, 0.78, 0.86])
    colors = np.clip(shade[:, None] * base[None, :], 0, 1)[order]
    polys = tri[order][:, :, :2]
    lo, hi = v[:, :2].min(axis=0), v[:, :2].max(axis=0)
    span = np.maximum(hi - lo, 1e-6)
    pad = 0.06 * span.max()
    w, h = span + 2 * pad
    fig_w = px / 100
    fig = plt.figure(figsize=(fig_w, fig_w * h / w), dpi=100)
    ax = fig.add_axes([0.08, 0.08, 0.9, 0.86])
    ax.add_collection(PolyCollection(polys, facecolors=colors, edgecolors="none", antialiaseds=False))
    ax.set_xlim(lo[0] - pad, hi[0] + pad)
    ax.set_ylim(lo[1] - pad, hi[1] + pad)
    ax.set_aspect("equal")
    labels = {"top": ("x", "y"), "bottom": ("x", "-y"), "front": ("x", "z"), "back": ("-x", "z"), "right": ("y", "z"), "left": ("-y", "z")}
    if view in labels and grid:
        step = _grid_step(span.max())
        ax.set_xticks(np.arange(math.floor(lo[0] / step) * step, hi[0] + step, step))
        ax.set_yticks(np.arange(math.floor(lo[1] / step) * step, hi[1] + step, step))
        ax.grid(True, linewidth=0.4, alpha=0.5)
        ax.set_xlabel(f"{labels[view][0]} [mm]")
        ax.set_ylabel(f"{labels[view][1]} [mm]")
        ax.tick_params(labelsize=7)
    else:
        ax.set_xticks([])
        ax.set_yticks([])
        ext = mesh.extents
        ax.text(0.01, 0.01, f"bbox {ext[0]:.2f} x {ext[1]:.2f} x {ext[2]:.2f} mm", transform=ax.transAxes, fontsize=8)
    ax.set_title(title or f"{view} view (orthographic)", fontsize=10)
    fig.savefig(out)
    plt.close(fig)
    return out


def render_section(mesh: trimesh.Trimesh, axis: str, at: float, out: Path, px: int = 1400, title: str | None = None) -> Path | None:
    i = "xyz".index(axis)
    normal = np.zeros(3)
    normal[i] = 1.0
    origin = np.zeros(3)
    origin[i] = at
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        return None
    u, w = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[axis]
    segs = sec.vertices[sec.entities[0].points] if False else None  # noqa: F841 - explicit path below
    lines = [sec.vertices[e.points][:, [u, w]] for e in sec.entities]
    allpts = np.vstack(lines)
    lo, hi = allpts.min(axis=0), allpts.max(axis=0)
    span = np.maximum(hi - lo, 1e-6)
    pad = 0.08 * span.max()
    fig_w = px / 100
    fig = plt.figure(figsize=(fig_w, fig_w * (span[1] + 2 * pad) / (span[0] + 2 * pad)), dpi=100)
    ax = fig.add_axes([0.1, 0.1, 0.86, 0.82])
    # fill closed polygons when the planar path is well formed
    area_note = ""
    try:
        planar, _ = sec.to_planar()
        area_note = f"; solid area {planar.area:.2f} mm2 ({len(planar.polygons_full)} region(s))"
    except Exception:
        pass
    for ln in lines:
        ax.plot(ln[:, 0], ln[:, 1], color="k", linewidth=1.0)
    step = _grid_step(span.max())
    ax.set_xticks(np.arange(math.floor(lo[0] / step) * step, hi[0] + step, step))
    ax.set_yticks(np.arange(math.floor(lo[1] / step) * step, hi[1] + step, step))
    ax.grid(True, linewidth=0.4, alpha=0.5)
    ax.set_aspect("equal")
    ax.set_xlim(lo[0] - pad, hi[0] + pad)
    ax.set_ylim(lo[1] - pad, hi[1] + pad)
    ax.tick_params(labelsize=7)
    ax.set_xlabel(f"{'xyz'[u]} [mm]")
    ax.set_ylabel(f"{'xyz'[w]} [mm]")
    ax.set_title(title or f"section {axis} = {at:g} mm (material outline){area_note}", fontsize=9)
    fig.savefig(out)
    plt.close(fig)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("reference", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--views", default="top,front,right,iso")
    ap.add_argument("--sections", default="", help="comma list like z=3,x=10.5")
    ap.add_argument("--px", type=int, default=1600)
    ap.add_argument("--deflection", type=float, default=0.05, help="STEP tessellation deflection (mm)")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--no-grid", action="store_true", help="omit the mm grid (pure picture)")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    mesh = load_mesh(a.reference, a.deflection)
    written = []
    for v in [x for x in a.views.split(",") if x]:
        written.append(render_view(mesh, v, a.out / f"{a.prefix}{v}.png", px=a.px, grid=not a.no_grid))
    for s in [x for x in a.sections.split(",") if x]:
        axis, at = s.split("=")
        p = render_section(mesh, axis.strip(), float(at), a.out / f"{a.prefix}section-{axis.strip()}{float(at):g}.png", px=a.px)
        if p:
            written.append(p)
    ext = mesh.extents
    (a.out / f"{a.prefix}render-notes.md").write_text(
        f"Renders of the reference ({a.reference.name}): {len(mesh.faces)} triangles, extents {ext[0]:.3f} x {ext[1]:.3f} x {ext[2]:.3f} mm, "
        f"bbox min {mesh.bounds[0].round(3).tolist()} max {mesh.bounds[1].round(3).tolist()}. Orthographic views with a mm grid; sections show the material outline.\n"
        + "".join(f"- {p.name}\n" for p in written), encoding="utf-8")
    for p in written:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Universal snapshots from an exported STL (or STEP): nine views, crease overlay, sheets.

No engine calls. Software matplotlib rendering, adapted from scripts/render_reference.py.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Iterable

import matplotlib
import numpy as np
import trimesh
from PIL import Image, ImageDraw

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection, PolyCollection  # noqa: E402

VIEWS = {
    "top": np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float),
    "bottom": np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], float),
    "front": np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float),
    "back": np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], float),
    "right": np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], float),
    "left": np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], float),
}

ANGLE_MAP = {"right-side": "right", "iso": "iso", "four-ways": "four-ways", "all": "all", "symmetry": "symmetry"}
DEFAULT_VIEWS = ("front", "back", "left", "right-side", "top", "bottom", "iso", "iso2", "iso-below")
ALL_ORDER = (
    ("front", "front"), ("back", "back"), ("left", "left"),
    ("right-side", "right"), ("top", "top"), ("bottom", "bottom"),
    ("iso", "iso"), ("iso2", "iso2"), ("iso-below", "iso-below"),
)
CREASE_DEG = 25.0


def _iso(viewer: tuple[float, float, float] = (1.0, -1.0, 1.0)) -> np.ndarray:
    w = np.asarray(viewer, float)
    w /= np.linalg.norm(w)
    u = np.cross([0.0, 0.0, 1.0], w)
    u /= np.linalg.norm(u)
    v = np.cross(w, u)
    return np.array([u, v, w])


VIEWS["iso"] = _iso((1.0, -1.0, 1.0))
VIEWS["iso2"] = _iso((-1.0, 1.0, 1.0))
VIEWS["iso-below"] = _iso((1.0, -1.0, -1.0))


def load_mesh(path: Path, deflection: float = 0.05) -> trimesh.Trimesh:
    path = Path(path)
    if path.suffix.lower() in (".step", ".stp"):
        from opencad.truth.scorer import step_to_mesh

        tmp = Path(tempfile.mkdtemp(prefix="render-")) / "mesh.stl"
        step_to_mesh(path, tmp, deflection=deflection)
        path = tmp
    m = trimesh.load(path, force="mesh")
    if isinstance(m, trimesh.Scene):
        m = trimesh.util.concatenate([g for g in m.geometry.values()])
    return m


def _fine(mesh: trimesh.Trimesh, rel_edge: float = 0.015, max_faces: int = 400_000) -> trimesh.Trimesh:
    # long wall triangles break the painter's sort; relax the edge size rather than fall back to the unrefined mesh
    for rel in (rel_edge, 2 * rel_edge, 4 * rel_edge, 8 * rel_edge):
        v, f = trimesh.remesh.subdivide_to_size(mesh.vertices, mesh.faces, max_edge=float(mesh.extents.max()) * rel, max_iter=8)
        if len(f) <= max_faces:
            return trimesh.Trimesh(v, f, process=False)
    return mesh


def _crease_segments(mesh: trimesh.Trimesh, R: np.ndarray, deg: float = CREASE_DEG) -> np.ndarray:
    """2-D segments of edges whose dihedral angle exceeds `deg`, in view coordinates."""
    if len(mesh.faces) < 2:
        return np.zeros((0, 2, 2))
    try:
        edges = mesh.face_adjacency_edges
        angles = np.degrees(mesh.face_adjacency_angles)
    except Exception:
        return np.zeros((0, 2, 2))
    mask = angles > deg
    if not mask.any():
        return np.zeros((0, 2, 2))
    return (mesh.vertices[edges[mask]] @ R.T)[:, :, :2]


def _mirror_vertex_dev(mesh: trimesh.Trimesh, plane: str, at: float) -> np.ndarray:
    axis = "xyz".index(plane)
    v = np.asarray(mesh.vertices, float)
    mir = v.copy()
    mir[:, axis] = 2.0 * at - mir[:, axis]
    from opencad.geomcheck.mesh import closest_point

    _, dist, _ = closest_point(mesh, mir)
    return np.asarray(dist, float)


def render_view(
    mesh: trimesh.Trimesh,
    view: str,
    out: Path,
    px: int = 1200,
    title: str | None = None,
    grid: bool = False,
    creases: bool = True,
    vertex_dev: np.ndarray | None = None,
    fine: trimesh.Trimesh | None = None,
) -> Path:
    """`fine` is `_fine(mesh)` precomputed by a caller rendering several views of one mesh."""
    view = ANGLE_MAP.get(view, view)
    R = VIEWS[view]
    coarse = mesh
    shaded = mesh if vertex_dev is not None else (fine if fine is not None else _fine(mesh))
    v = shaded.vertices @ R.T
    tri = v[shaded.faces]
    depth = tri[:, :, 2].mean(axis=1)
    order = np.argsort(depth)
    if vertex_dev is not None:
        fd = np.asarray(vertex_dev, float)[shaded.faces].mean(axis=1)
        vmax = max(float(np.percentile(fd, 99)) if fd.size else 0.1, 0.05)
        t = np.clip(fd / vmax, 0, 1)
        colors = np.clip(np.stack([0.15 + 0.85 * t, 0.85 * (1 - t) + 0.15, 0.25 * (1 - t)], axis=1)[order], 0, 1)
    else:
        n = shaded.face_normals @ R.T
        light = np.array([0.3, 0.4, 0.866])
        shade = 0.30 + 0.70 * np.clip(n @ light, 0, 1)
        shade = np.where(n[:, 2] < 0, shade * 0.6, shade)
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
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.add_collection(PolyCollection(polys, facecolors=colors, edgecolors="none", antialiaseds=False))
    if creases:
        segs = _crease_segments(coarse, R)
        if len(segs):
            ax.add_collection(LineCollection(segs, colors=(0.08, 0.08, 0.1, 0.85), linewidths=0.45, zorder=3))
    ax.set_xlim(lo[0] - pad, hi[0] + pad)
    ax.set_ylim(lo[1] - pad, hi[1] + pad)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=10)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def render_section(mesh: trimesh.Trimesh, plane: str, at: float, out: Path, px: int = 1200, title: str | None = None) -> Path:
    """Filled planar cross-section with mm axes (the drawing a designer reads a profile from). Holes are the loops nested an
    odd number of times; they are drawn unfilled."""
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MplPath

    i = "xyz".index(plane)
    u, v = [k for k in range(3) if k != i]
    normal = np.zeros(3)
    normal[i] = 1.0
    origin = np.zeros(3)
    origin[i] = at
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        raise ValueError(f"no section at {plane}={at}")
    loops = [np.asarray(d)[:, [u, v]] for d in sec.discrete if len(d) >= 3]
    paths = [MplPath(lp) for lp in loops]
    depth = [sum(1 for j, q in enumerate(paths) if j != k and q.contains_point(lp[0])) for k, lp in enumerate(loops)]
    verts, codes = [], []
    for lp, d in zip(loops, depth):
        area = 0.5 * float(np.sum(lp[:, 0] * np.roll(lp[:, 1], -1) - np.roll(lp[:, 0], -1) * lp[:, 1]))
        lp = lp if (area > 0) == (d % 2 == 0) else lp[::-1]  # outer loops CCW, holes CW: nonzero winding leaves holes open
        verts += [*lp, lp[0]]
        codes += [MplPath.MOVETO] + [MplPath.LINETO] * (len(lp) - 1) + [MplPath.CLOSEPOLY]
    allv = np.vstack(loops)
    lo, hi = allv.min(axis=0), allv.max(axis=0)
    span = np.maximum(hi - lo, 1e-6)
    pad = 0.08 * span.max()
    fig_w = px / 100
    fig = plt.figure(figsize=(fig_w, fig_w * (span[1] + 2 * pad) / (span[0] + 2 * pad) + 0.6), dpi=100)
    ax = fig.add_axes([0.08, 0.08, 0.9, 0.84])
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=(0.72, 0.78, 0.86), edgecolor=(0.08, 0.08, 0.1), linewidth=0.8))
    ax.set_xlim(lo[0] - pad, hi[0] + pad)
    ax.set_ylim(lo[1] - pad, hi[1] + pad)
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_xlabel(f"{'xyz'[u]} (mm)")
    ax.set_ylabel(f"{'xyz'[v]} (mm)")
    ax.set_title(title or f"section {plane} = {at:g} mm", fontsize=10)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def sheet(paths: dict[str, Path], out: Path, order: Iterable[tuple[str, str]], cols: int, cell_w: int = 640) -> Path:
    imgs = []
    for key, label in order:
        src = paths.get(key) or paths.get(label)
        if src and Path(src).exists():
            imgs.append((label, Image.open(src).convert("RGB")))
    if not imgs:
        raise FileNotFoundError("no views to compose into a sheet")
    for _, im in imgs:
        im.thumbnail((cell_w - 8, cell_w - 8))
    cell_h = max(im.height for _, im in imgs) + 8
    rows = (len(imgs) + cols - 1) // cols
    im = Image.new("RGB", (cell_w * cols, cell_h * rows + 24), "white")
    d = ImageDraw.Draw(im)
    for i, (label, pic) in enumerate(imgs):
        x, y = (i % cols) * cell_w + 4, (i // cols) * cell_h + 4
        im.paste(pic, (x, y))
        d.text((x + 6, y + 6), label, fill=(40, 40, 40))
    d.text((8, cell_h * rows + 4), " / ".join(label for label, _ in imgs)[:160], fill=(60, 60, 60))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    return out


FOUR_WAYS = (("front", "front"), ("top", "top"), ("right-side", "right"), ("iso", "iso"))


def four_ways(paths: dict[str, Path], out: Path, cell_w: int = 640) -> Path:
    return sheet(paths, out, FOUR_WAYS, cols=2, cell_w=cell_w)


# --- reference renders (the arm's worker-visible input images) beside the part's own views ---------------------

_REF_ALIASES = {"right": "right-side"}
_REF_SKIP = ("section", "view-", "silhouette", "reference", "quick-", "contact")


def reference_renders(source_dir: Path | None) -> dict[str, Path]:
    """Input renders keyed by snapshot angle: `front.png`, `iso-below.png`, `<body>-top.png`, `right.png` (-> right-side)."""
    out: dict[str, Path] = {}
    if not source_dir or not Path(source_dir).exists():
        return out
    for p in sorted(Path(source_dir).glob("*.png")):
        stem = p.stem.lower()
        if stem.startswith(_REF_SKIP):
            continue
        for angle in (*DEFAULT_VIEWS, *_REF_ALIASES):
            if stem == angle or stem.endswith("-" + angle):
                key = _REF_ALIASES.get(angle, angle)
                out.setdefault(key, p)
                break
    return out


def compare_sheet(snap_dir: Path, refs: dict[str, Path], out: Path, cell_w: int = 560) -> Path | None:
    """Reference render | part view, one row per matched angle, so a worker (and the QA reviewer) compares like with like."""
    snap_dir = Path(snap_dir)
    pairs = [(a, refs[a], snap_dir / f"view-{a}.png") for a in DEFAULT_VIEWS if a in refs and (snap_dir / f"view-{a}.png").exists()]
    if not pairs:
        return None
    cells = []
    for angle, ref, part in pairs:
        ims = [Image.open(ref).convert("RGB"), Image.open(part).convert("RGB")]
        for im in ims:
            im.thumbnail((cell_w - 8, cell_w - 8))
        cells.append((angle, ims))
    per_row = 2  # two reference|part pairs per row keeps the sheet readable at nine views
    cell_h = max(im.height for _, ims in cells for im in ims) + 24
    n_rows = (len(cells) + per_row - 1) // per_row
    canvas = Image.new("RGB", (cell_w * 2 * per_row, cell_h * n_rows + 24), "white")
    d = ImageDraw.Draw(canvas)
    for i, (angle, ims) in enumerate(cells):
        r, p = divmod(i, per_row)
        for c, (label, im) in enumerate(zip(("reference", "part"), ims)):
            x, y = (p * 2 + c) * cell_w + 4, r * cell_h + 20
            canvas.paste(im, (x, y))
            d.text((x + 6, y - 14), f"{label} {angle}", fill=(40, 40, 40))
    d.text((8, cell_h * n_rows + 4), "reference = input render the contract was drafted from; part = this export, same view", fill=(60, 60, 60))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    return out


def silhouette_mask(png: Path) -> np.ndarray:
    """The shaded part pixels of a render: the part colour is bluish; grid, axes and text are neutral or white."""
    im = np.asarray(Image.open(png).convert("RGB")).astype(int)
    r, b = im[..., 0], im[..., 2]
    return (b - r > 10) & (b < 250)


def mask_iou_normalized(a: np.ndarray, b: np.ndarray, size: int = 256) -> float | None:
    """IoU of two silhouettes after each is cropped to its own bounding box and resampled: framing-independent shape agreement."""

    def crop(m: np.ndarray) -> np.ndarray | None:
        ys, xs = np.nonzero(m)
        if len(ys) == 0:
            return None
        sub = m[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]
        return np.asarray(Image.fromarray((sub * 255).astype(np.uint8)).resize((size, size), Image.NEAREST)) > 127

    A, B = crop(a), crop(b)
    if A is None or B is None:
        return None
    union = int((A | B).sum())
    return float((A & B).sum() / union) if union else None


def reference_silhouettes(snap_dir: Path, refs: dict[str, Path]) -> dict[str, float]:
    """Per matched angle: normalized silhouette IoU between the input render and the part view (evidence, not a gate)."""
    out: dict[str, float] = {}
    for angle, ref in refs.items():
        part = Path(snap_dir) / f"view-{angle}.png"
        if not part.exists():
            continue
        iou = mask_iou_normalized(silhouette_mask(ref), silhouette_mask(part))
        if iou is not None:
            out[angle] = round(iou, 3)
    return out


def render_symmetry(mesh: trimesh.Trimesh, out: Path, plane: str, at: float = 0.0, px: int = 1200) -> Path:
    dist = _mirror_vertex_dev(mesh, plane, at)
    tmp = Path(tempfile.mkdtemp(prefix="sym-"))
    written: dict[str, Path] = {}
    for view in ("iso", "iso2"):
        dest = tmp / f"{view}.png"
        render_view(mesh, view, dest, px=px, creases=True, vertex_dev=dist, title=f"{view} mirror {plane}={at:g}")
        written[view] = dest
    return sheet(written, out, (("iso", "iso"), ("iso2", "iso2")), cols=2, cell_w=px)


def render_snapshots(
    mesh_path: Path,
    out_dir: Path,
    angles: Iterable[str] | None = None,
    *,
    px: int = 1200,
    contract=None,
) -> dict[str, str]:
    """Write view-<angle>.png files from an STL/STEP. Returns {angle: path}."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    angles = tuple(angles) if angles is not None else DEFAULT_VIEWS
    mesh = load_mesh(Path(mesh_path))
    extras = {"four-ways", "all", "symmetry"}
    singles = [a for a in angles if a not in extras]
    if not singles:
        singles = list(DEFAULT_VIEWS)
    if "four-ways" in angles:
        singles += [a for a, _ in FOUR_WAYS if a not in singles]
    written: dict[str, Path] = {}
    fine = _fine(mesh)  # the subdivision is ~half of a view's render time; every view shades the same one
    for angle in singles:
        view = ANGLE_MAP.get(angle, angle)
        dest = out_dir / f"view-{angle}.png"
        render_view(mesh, view, dest, px=px, creases=True, fine=fine)
        written[angle] = dest
    dest_all = out_dir / "view-all.png"
    try:
        written["all"] = sheet(written, dest_all, ALL_ORDER, cols=3, cell_w=min(640, px))
    except FileNotFoundError:
        pass
    if "four-ways" in angles:
        dest = out_dir / "view-four-ways.png"
        four_ways(written, dest)
        written["four-ways"] = dest
    specs = list(getattr(getattr(contract, "acceptance", None), "symmetry", None) or [])
    if specs:
        spec = specs[0]
        dest = out_dir / "view-symmetry.png"
        render_symmetry(mesh, dest, spec.plane, spec.at, px=px)
        written["symmetry"] = dest
    return {k: str(v) for k, v in written.items()}

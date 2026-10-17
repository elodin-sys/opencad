"""STL/GLB inspection with trimesh, plus deviation metrics against a reference mesh."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import trimesh

from opencad.reference.mesh import load_mesh


def _void_shells(comps: list) -> int:
    """Inner shells: negative signed volume, or a body whose centroid is inside a larger outer shell."""
    if len(comps) <= 1:
        return 0
    outer_i = max(range(len(comps)), key=lambda i: abs(float(comps[i].volume)))
    outer = comps[outer_i]
    n = 0
    for i, c in enumerate(comps):
        if i == outer_i:
            continue
        if float(c.volume) < 0:
            n += 1
            continue
        probe = c.center_mass if getattr(c, "is_watertight", False) else c.centroid
        try:
            if bool(outer.contains(np.asarray([probe], dtype=float))[0]):
                n += 1
        except Exception:
            continue
    return n


def _open_edges(m: trimesh.Trimesh) -> dict[str, Any]:
    """Boundary edges (appear once in `edges_sorted`) with their vertex bbox and centroid."""
    unique, counts = np.unique(m.edges_sorted, axis=0, return_counts=True)
    open_e = unique[counts == 1]
    n = int(len(open_e))
    if n == 0:
        return {"count": 0, "bbox_min": None, "bbox_max": None, "centroid": None}
    pts = m.vertices[open_e].reshape(-1, 3)
    return {
        "count": n,
        "bbox_min": [round(float(v), 4) for v in pts.min(axis=0)],
        "bbox_max": [round(float(v), 4) for v in pts.max(axis=0)],
        "centroid": [round(float(v), 4) for v in pts.mean(axis=0)],
    }


def manifold_volume(m) -> float | None:
    """Signed volume of the mesh through the Manifold kernel (not OCCT, not trimesh): the export witness that shares no code with the
    modelling kernel. None when `manifold3d` is not installed or the mesh is not a valid manifold."""
    try:
        import manifold3d
    except ImportError:
        return None
    try:
        mm = manifold3d.Manifold(
            manifold3d.Mesh(np.asarray(m.vertices, dtype=np.float32), np.asarray(m.faces, dtype=np.uint32))
        )
        if mm.is_empty():
            return None
        return float(mm.volume())
    except (RuntimeError, ValueError, TypeError):
        return None


def analyze_mesh(path: Path) -> dict[str, Any]:
    m = load_mesh(Path(path))
    lo, hi = m.bounds
    comps = m.split(only_watertight=False)
    degenerate = int((m.area_faces <= 1e-12).sum())
    voids = _void_shells(list(comps))
    comp_wt = [bool(c.is_watertight) for c in comps]
    return {
        "manifold_volume": manifold_volume(m),
        "faces": int(len(m.faces)),
        "vertices": int(len(m.vertices)),
        "watertight": bool(m.is_watertight),
        # touching bodies share edges in one STL and make the combined mesh non-manifold; each body can still be closed
        "components_watertight": comp_wt,
        "solids_watertight": bool(comp_wt) and all(comp_wt),
        "winding_consistent": bool(m.is_winding_consistent),
        "components": len(comps),
        "void_shells": voids,
        "solid_shells": len(comps) - voids,
        "degenerate_faces": degenerate,
        "volume": float(m.volume),
        "surface_area": float(m.area),
        "bbox_min": lo.tolist(),
        "bbox_max": hi.tolist(),
        "center_of_mass": (m.center_mass if m.is_watertight else m.centroid).tolist(),
        "open_edges": _open_edges(m),
    }


def polygon_iou(a: np.ndarray, b: np.ndarray, px_long: int = 2400) -> float:
    """IoU of two 2-D polygons rasterised on a shared grid (same long-axis policy as silhouette IoU)."""
    from PIL import Image, ImageDraw

    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    lo = np.minimum(a.min(axis=0), b.min(axis=0)) - 1.0
    hi = np.maximum(a.max(axis=0), b.max(axis=0)) + 1.0
    size = hi - lo
    mm_per_px = float(max(float(size.max()), 1e-9) / px_long)
    shape = (int(size[1] / mm_per_px) + 2, int(size[0] / mm_per_px) + 2)

    def rast(p: np.ndarray) -> np.ndarray:
        img = Image.new("1", (shape[1], shape[0]), 0)
        d = ImageDraw.Draw(img)
        xy = [((float(x) - lo[0]) / mm_per_px, (float(y) - lo[1]) / mm_per_px) for x, y in p]
        if len(xy) >= 3:
            d.polygon(xy, fill=1)
        return np.asarray(img, dtype=bool)

    ra, rb = rast(a), rast(b)
    union = np.logical_or(ra, rb).sum()
    return float(np.logical_and(ra, rb).sum() / union) if union else 1.0


def contains(path: Path, points: list[tuple[float, float, float]]) -> list[bool]:
    m = load_mesh(Path(path))
    return [bool(v) for v in m.contains(np.asarray(points, dtype=float))]


DEVIATION_BANDS = 10
WORST_SHARE = 0.02  # the worst 2 % of samples, clustered into regions


def deviation(candidate: Path, reference: Path, samples: int = 20000, seed: int = 0, *, map_path: Path | None = None) -> dict[str, Any]:
    """Symmetric point-to-surface deviation (mm): p95/p99/max each way, silhouette IoU, and where it is: DEVIATION_BANDS bands along
    the reference's longest axis and the clustered worst WORST_SHARE of samples, each signed (model outside the reference > 0, inside
    < 0). `map_path` also draws the signed samples in three projections."""
    cand = load_mesh(Path(candidate))
    ref = load_mesh(Path(reference))
    rng = np.random.default_rng(seed)

    def one_way(a: trimesh.Trimesh, b: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, float]]:
        pts, _ = trimesh.sample.sample_surface(a, samples, seed=int(rng.integers(0, 2**31)))
        closest, dist, tri = closest_point(b, pts)
        outside = np.einsum("ij,ij->i", pts - closest, b.face_normals[tri]) > 0  # the sample lies outside b
        stats = {
            "p50": float(np.percentile(dist, 50)),
            "p95": float(np.percentile(dist, 95)),
            "p99": float(np.percentile(dist, 99)),
            "max": float(dist.max()),
            "mean": float(dist.mean()),
        }
        return pts, np.asarray(dist, float), outside, stats

    cp, cd, c_out, c2r = one_way(cand, ref)
    rp, rd, r_out, r2c = one_way(ref, cand)
    # model outside the reference: a model sample outside it, or a reference sample inside the model
    pts, dist = np.vstack([cp, rp]), np.concatenate([cd, rd])
    signed = np.concatenate([np.where(c_out, cd, -cd), np.where(r_out, -rd, rd)])
    ious = {view: silhouette_iou(cand, ref, view) for view in ("top", "front", "right")}
    axis = int(np.argmax(ref.bounds[1] - ref.bounds[0]))
    out = {
        "samples": samples,
        "candidate_to_reference": c2r,
        "reference_to_candidate": r2c,
        "p95": max(c2r["p95"], r2c["p95"]),
        "hausdorff_estimate": max(c2r["max"], r2c["max"]),
        "silhouette_iou": ious,
        "silhouette_iou_min": min(ious.values()),
        "silhouette_px_long": 2400,
        "volume_ratio": float(cand.volume / ref.volume) if ref.volume else None,
        "bbox_delta": (np.abs(cand.bounds - ref.bounds)).max(axis=0).tolist(),
        "axis": "xyz"[axis],
        "bands": deviation_bands(pts, dist, signed, axis, float(ref.bounds[0][axis]), float(ref.bounds[1][axis])),
        "worst": worst_regions(pts, dist, signed, float(np.linalg.norm(ref.bounds[1] - ref.bounds[0]))),
        "worst_share": WORST_SHARE,
    }
    if map_path is not None:
        out["map"] = str(deviation_map(pts, signed, Path(map_path), title=f"p95 {out['p95']:.2f} mm, max {out['hausdorff_estimate']:.2f} mm"))
    return out


def _signed_summary(d: np.ndarray, s: np.ndarray) -> dict[str, Any]:
    pos, neg = s[s > 0], -s[s < 0]
    return {"n": len(d), "p95": round(float(np.percentile(d, 95)), 4) if len(d) else 0.0, "max": round(float(d.max()), 4) if len(d) else 0.0,
            "outside_p95": round(float(np.percentile(pos, 95)), 4) if len(pos) else 0.0, "inside_p95": round(float(np.percentile(neg, 95)), 4) if len(neg) else 0.0}


def deviation_bands(pts: np.ndarray, dist: np.ndarray, signed: np.ndarray, axis: int, lo: float, hi: float, n: int = DEVIATION_BANDS) -> list[dict[str, Any]]:
    """Equal bands of the reference extent along `axis`: p95 and max of the samples in each, and how far the model lies outside and
    inside the reference there (95th percentile of each sign)."""
    edges = np.linspace(lo, hi, n + 1)
    k = np.clip(np.searchsorted(edges, pts[:, axis], side="right") - 1, 0, n - 1)
    return [{"lo": round(float(edges[i]), 3), "hi": round(float(edges[i + 1]), 3), **_signed_summary(dist[k == i], signed[k == i])} for i in range(n)]


def worst_regions(pts: np.ndarray, dist: np.ndarray, signed: np.ndarray, diagonal: float, limit: int = 5) -> list[dict[str, Any]]:
    """The worst WORST_SHARE of samples joined into regions by adjacency on a grid of 2 % of the diagonal (at least 2 mm), largest
    deviation first: each region's box ([min, max] corners), sample count, max and signed 95th percentiles."""
    from scipy import ndimage

    if not len(dist):
        return []
    worst = dist >= np.percentile(dist, 100 * (1 - WORST_SHARE))
    p, d, s = pts[worst], dist[worst], signed[worst]
    cell = max(0.02 * diagonal, 2.0)
    idx = np.floor((p - p.min(axis=0)) / cell).astype(int)
    grid = np.zeros(idx.max(axis=0) + 1, dtype=bool)
    grid[tuple(idx.T)] = True
    labels, _ = ndimage.label(grid, structure=np.ones((3, 3, 3)))
    lab = labels[tuple(idx.T)]
    regions = []
    for g in np.unique(lab):
        m = lab == g
        regions.append({"box": [np.round(p[m].min(axis=0), 2).tolist(), np.round(p[m].max(axis=0), 2).tolist()], **_signed_summary(d[m], s[m])})
    return sorted(regions, key=lambda r: -r["max"])[:limit]


def deviation_map(pts: np.ndarray, signed: np.ndarray, out: Path, *, title: str = "") -> Path:
    """The signed samples in top (xy), front (xz) and right (yz) projections: red where the model lies outside the reference,
    blue where it lies inside, clipped at the 99th percentile."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    vmax = max(float(np.percentile(np.abs(signed), 99)), 0.05)
    order = np.argsort(np.abs(signed))  # the largest deviations drawn last, on top
    p, s = pts[order], signed[order]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4), constrained_layout=True)
    sc = None
    for ax, (i, j), name in zip(axes, ((0, 1), (0, 2), (1, 2)), ("top (x, y)", "front (x, z)", "right (y, z)")):
        sc = ax.scatter(p[:, i], p[:, j], c=s, cmap="coolwarm", vmin=-vmax, vmax=vmax, s=1.5, linewidths=0)
        ax.set_aspect("equal")
        ax.set_title(name)
        ax.grid(True, linewidth=0.3)
    fig.colorbar(sc, ax=axes, shrink=0.8, label="mm: model outside (+) / inside (-) the reference")
    fig.suptitle(f"deviation from the reference: {title}")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=90)
    plt.close(fig)
    return out


def _raster(
    m: trimesh.Trimesh, cols: tuple[int, int], lo: np.ndarray, mm_per_px: float, shape: tuple[int, int]
) -> np.ndarray:
    from PIL import Image, ImageDraw

    img = Image.new("1", (shape[1], shape[0]), 0)
    d = ImageDraw.Draw(img)
    v = m.vertices
    pts = np.stack([(v[:, cols[0]] - lo[0]) / mm_per_px, (v[:, cols[1]] - lo[1]) / mm_per_px], axis=1)
    for tri in m.faces:
        d.polygon([tuple(pts[i]) for i in tri], fill=1)
    return np.asarray(img, dtype=bool)


def silhouette_iou(a: trimesh.Trimesh, b: trimesh.Trimesh, view: str, px_long: int = 2400) -> float:
    cols = {"top": (0, 1), "front": (0, 2), "right": (1, 2)}[view]
    lo = np.minimum(a.bounds[0][list(cols)], b.bounds[0][list(cols)]) - 1.0
    hi = np.maximum(a.bounds[1][list(cols)], b.bounds[1][list(cols)]) + 1.0
    size = hi - lo
    mm_per_px = float(max(size.max(), 1e-9) / px_long)
    shape = (int(size[1] / mm_per_px) + 2, int(size[0] / mm_per_px) + 2)
    ra = _raster(a, cols, lo, mm_per_px, shape)
    rb = _raster(b, cols, lo, mm_per_px, shape)
    union = np.logical_or(ra, rb).sum()
    return float(np.logical_and(ra, rb).sum() / union) if union else 1.0


def closest_point(m: trimesh.Trimesh, pts: np.ndarray, chunk: int = 2000) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """`trimesh.proximity.closest_point` in chunks: its candidate set per point grows with triangle size, so a planar face's
    part-length slivers took ~0.25 MB per query point (60k samples, 16 GB) in one call."""
    parts = [trimesh.proximity.closest_point(m, pts[i : i + chunk]) for i in range(0, len(pts), chunk)]
    if not parts:
        return np.zeros((0, 3)), np.zeros(0), np.zeros(0, dtype=int)
    return tuple(np.concatenate(c) for c in zip(*parts, strict=True))  # type: ignore[return-value]


def _as_mesh(mesh_or_path: Path | trimesh.Trimesh) -> trimesh.Trimesh:
    if isinstance(mesh_or_path, trimesh.Trimesh):
        return mesh_or_path
    return load_mesh(Path(mesh_or_path))


def step_tessellation(step: Path, *, deflection: float = 0.005, angular: float = 0.1) -> trimesh.Trimesh:
    """A mesh of the STEP for the symmetry check: finer than the export STL and independent of it.

    The fine STL is cached by the STEP's sha256 under ~/.cache/opencad/tess so a repeated quick on the same export does not re-mesh.
    """
    import hashlib
    import shutil
    import tempfile

    from opencad.backends.local import write_stl
    from opencad.geomcheck.brep import read_step

    digest = hashlib.sha256(Path(step).read_bytes()).hexdigest()
    cache = Path.home() / ".cache" / "opencad" / "tess" / f"{digest}-{deflection:g}-{angular:g}.stl"
    if cache.is_file() and cache.stat().st_size > 0:
        return load_mesh(cache)
    cache.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="opencad-tess-"))
    try:
        stl = write_stl(read_step(step), tmp / "part.stl", deflection=deflection, angular=angular)
        shutil.copy2(stl, cache)
        return load_mesh(cache)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def mirror_deviation(
    mesh_or_path: Path | trimesh.Trimesh,
    plane: str,
    at: float = 0.0,
    samples: int = 60000,
    seed: int = 0,
    exceed_mm: float = 0.1,
) -> dict[str, Any]:
    """Reflect surface samples across `plane=at` and measure point-to-surface distance on the original."""
    m = _as_mesh(mesh_or_path)
    axis = "xyz".index(plane)
    rng = np.random.default_rng(seed)
    n = min(int(samples), max(int(len(m.faces) * 4), 1))
    pts, _ = trimesh.sample.sample_surface(m, n, seed=int(rng.integers(0, 2**31)))
    mirrored = pts.copy()
    mirrored[:, axis] = 2.0 * at - mirrored[:, axis]
    _, dist, _ = closest_point(m, mirrored)
    dist = np.asarray(dist, float)
    worst_i = int(dist.argmax()) if len(dist) else 0
    worst_point = [round(float(v), 4) for v in (pts[worst_i] if len(pts) else (0.0, 0.0, 0.0))]
    cell = np.floor(pts / 2.0).astype(int) if len(pts) else np.zeros((0, 3), dtype=int)
    if len(cell):
        uniq, inv = np.unique(cell, axis=0, return_inverse=True)
        cell_max = np.zeros(len(uniq))
        np.maximum.at(cell_max, inv, dist)
        wc = uniq[int(cell_max.argmax())]
        lo = wc.astype(float) * 2.0
        worst_cell = {"min": [round(float(v), 4) for v in lo], "max": [round(float(v), 4) for v in lo + 2.0]}
    else:
        worst_cell = {"min": None, "max": None}
    centroids = m.triangles_center
    areas = m.area_faces
    pos = centroids[:, axis] >= at
    area_pos = float(areas[pos].sum()) if len(areas) else 0.0
    area_neg = float(areas[~pos].sum()) if len(areas) else 0.0
    n_ex = int((dist > exceed_mm).sum()) if len(dist) else 0
    return {
        "samples": int(len(dist)),
        "plane": plane,
        "at": at,
        "mean": float(dist.mean()) if len(dist) else 0.0,
        "p95": float(np.percentile(dist, 95)) if len(dist) else 0.0,
        "max": float(dist.max()) if len(dist) else 0.0,
        "exceed_fraction": float(n_ex / len(dist)) if len(dist) else 0.0,
        "n_exceed": n_ex,
        "exceed_mm": exceed_mm,
        "worst_point": worst_point,
        "worst_cell_bbox": worst_cell,
        "side_area_ratio": (area_pos / area_neg) if area_neg > 1e-12 else None,
        "area_positive": area_pos,
        "area_negative": area_neg,
    }

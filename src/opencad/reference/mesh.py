"""Triangle-mesh ingest: units, axes, datum, measurements, sections, silhouettes.

With stations, every section also carries its regions' outlines in the plane's two world axes (`UV_AXES`) and the closest
circle, ellipse and axis-aligned rounded rectangle to each, so a drafter can state a free-form skin station by station."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngInfo

from opencad.io import sha256_file, utc_now

UNIT_TO_MM = {"mm": 1.0, "cm": 10.0, "m": 1000.0, "in": 25.4, "ft": 304.8}
MESH_SUFFIXES = {".stl", ".ply", ".obj", ".off", ".glb", ".gltf", ".3mf"}
AXES_RE = re.compile(r"^([xyz])=([+-]?)([xyz])$")
UV_AXES = {"x": ("y", "z"), "y": ("x", "z"), "z": ("x", "y")}
OUTLINE_POINTS = 32
FIT_TOL_MM = 0.3  # an analytic fit whose largest residual is under this stands in for the station outline


class IngestError(ValueError):
    pass


def parse_axes(spec: str | None) -> np.ndarray:
    """`x=+y,y=-x,z=+z` -> 3x3 matrix R such that part = R @ source."""
    R = np.zeros((3, 3))
    if not spec:
        return np.eye(3)
    seen_src, seen_dst = set(), set()
    for item in spec.split(","):
        m = AXES_RE.match(item.strip())
        if not m:
            raise IngestError(f"bad axes item {item!r}; expected like x=+y")
        dst, sign, src = m.groups()
        i, j = "xyz".index(dst), "xyz".index(src)
        R[i, j] = -1.0 if sign == "-" else 1.0
        seen_src.add(src)
        seen_dst.add(dst)
    if seen_src != {"x", "y", "z"} or seen_dst != {"x", "y", "z"}:
        raise IngestError("axes mapping must assign each of x, y, z exactly once")
    if abs(np.linalg.det(R) - 1.0) > 1e-9:
        raise IngestError("axes mapping is not a proper rotation (determinant must be +1); flip one sign")
    return R


def load_mesh(path: Path) -> trimesh.Trimesh:
    path = Path(path)
    if path.suffix.lower() not in MESH_SUFFIXES:
        raise IngestError(f"{path.name}: not a triangle mesh (accepted {sorted(MESH_SUFFIXES)}); export a mesh with a known unit")
    loaded = trimesh.load(path, force="mesh", process=True)
    if isinstance(loaded, trimesh.Scene):
        loaded = trimesh.util.concatenate(tuple(g for g in loaded.geometry.values()))
    if not isinstance(loaded, trimesh.Trimesh) or len(loaded.faces) == 0:
        raise IngestError(f"{path.name}: no triangles found")
    return loaded


@dataclass
class Measured:
    bbox_min: list[float]
    bbox_max: list[float]
    size: list[float]
    volume: float
    surface_area: float
    center_of_mass: list[float]
    watertight: bool
    components: int
    faces: int
    principal_axes: list[list[float]]
    principal_extents: list[float]
    sections: list[dict[str, Any]] = field(default_factory=list)


def measure(mesh: trimesh.Trimesh) -> Measured:
    lo, hi = mesh.bounds
    comps = mesh.split(only_watertight=False)
    vol = float(mesh.volume) if mesh.is_watertight else float(abs(mesh.volume))
    pa = mesh.principal_inertia_vectors if mesh.is_watertight else np.eye(3)
    proj = (mesh.vertices - mesh.vertices.mean(axis=0)) @ pa.T
    ext = (proj.max(axis=0) - proj.min(axis=0)).tolist()
    return Measured(
        bbox_min=lo.tolist(),
        bbox_max=hi.tolist(),
        size=(hi - lo).tolist(),
        volume=vol,
        surface_area=float(mesh.area),
        center_of_mass=(mesh.center_mass if mesh.is_watertight else mesh.centroid).tolist(),
        watertight=bool(mesh.is_watertight),
        components=len(comps),
        faces=int(len(mesh.faces)),
        principal_axes=np.asarray(pa).tolist(),
        principal_extents=ext,
    )


def _uv(points_2d: np.ndarray, to_3d: np.ndarray, axis: str) -> np.ndarray:
    """Section-plane coordinates to the plane's two world axes (UV_AXES), mm."""
    p = np.asarray(points_2d, float)
    h = np.column_stack([p, np.zeros(len(p)), np.ones(len(p))]) @ np.asarray(to_3d, float).T
    return h[:, ["xyz".index(a) for a in UV_AXES[axis]]]


def _rounded(a: Any, nd: int) -> Any:
    return np.round(np.asarray(a, float), nd).tolist()


def resample_ring(ring: np.ndarray, n: int) -> np.ndarray:
    """A closed ring resampled to n points evenly by arc length, counter-clockwise, starting at its largest-u point, so the
    outlines of successive stations line up for a loft."""
    pts = np.asarray(ring, float)
    if len(pts) > 1 and np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    if np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1]) < 0:
        pts = pts[::-1]
    pts = np.roll(pts, -int(np.argmax(pts[:, 0])), axis=0)
    closed = np.vstack([pts, pts[:1]])
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(closed, axis=0), axis=1))])
    t = np.linspace(0.0, s[-1], n, endpoint=False)
    return np.column_stack([np.interp(t, s, closed[:, 0]), np.interp(t, s, closed[:, 1])])


def _residual(res: np.ndarray) -> dict[str, float]:
    return {"rms": round(float(np.sqrt(np.mean(res**2))), 4), "p95": round(float(np.percentile(res, 95)), 4), "max": round(float(res.max()), 4)}


def polyline_distance(p: np.ndarray, curve: np.ndarray) -> np.ndarray:
    """Distance from each point to a closed polyline: the nearest vertex's two segments, so the sample spacing adds no error."""
    from scipy.spatial import cKDTree

    c = np.asarray(curve, float)
    idx = cKDTree(c).query(p)[1]
    best = np.full(len(p), np.inf)
    for j in (idx - 1, idx):
        a, b = c[j % len(c)], c[(j + 1) % len(c)]
        ab = b - a
        t = np.clip(np.einsum("ij,ij->i", p - a, ab) / np.maximum(np.einsum("ij,ij->i", ab, ab), 1e-18), 0.0, 1.0)
        best = np.minimum(best, np.linalg.norm(p - (a + ab * t[:, None]), axis=1))
    return best


def _argmin_1d(f: Any, lo: float, hi: float, n: int = 21, passes: int = 3) -> float:
    """Grid search refined around the best cell `passes` times: robust for the one-parameter fits."""
    for _ in range(passes):
        grid = np.linspace(lo, hi, n)
        k = int(np.argmin([f(x) for x in grid]))
        lo, hi = grid[max(k - 1, 0)], grid[min(k + 1, n - 1)]
    return float((lo + hi) / 2)


def _inliers(res: np.ndarray) -> np.ndarray:
    """The best 90 % of an outline's points: the refit that keeps a notch or a cut from dragging the fitted skin."""
    return res <= np.percentile(res, 90)


def _circle(q: np.ndarray) -> tuple[np.ndarray, float] | None:
    (d, e, f), *_ = np.linalg.lstsq(np.column_stack([q, np.ones(len(q))]), -(q**2).sum(axis=1), rcond=None)
    c = np.array([-d / 2, -e / 2])
    r2 = float(c @ c - f)
    return (c, math.sqrt(r2)) if r2 > 0 else None


def fit_circle(p: np.ndarray) -> dict[str, Any] | None:
    got = _circle(p)
    if got is None:
        return None

    def res(g: tuple[np.ndarray, float]) -> np.ndarray:
        return np.abs(np.linalg.norm(p - g[0], axis=1) - g[1])

    keep = _inliers(res(got))
    refit = _circle(p[keep]) if keep.sum() >= 8 else None
    c, r = min((g for g in (got, refit) if g is not None), key=lambda g: float(np.percentile(res(g), 95)))
    return {"center": _rounded(c, 4), "radius": round(r, 4), **_residual(res((c, r)))}


def ellipse_points(center: Any, a: float, b: float, angle_deg: float, n: int = 720) -> np.ndarray:
    t = np.linspace(0.0, 2 * math.pi, n, endpoint=False)
    th = math.radians(angle_deg)
    u, v = np.array([math.cos(th), math.sin(th)]), np.array([-math.sin(th), math.cos(th)])
    return np.asarray(center, float) + np.outer(a * np.cos(t), u) + np.outer(b * np.sin(t), v)


def fit_ellipse(p: np.ndarray) -> dict[str, Any] | None:
    """Direct least-squares ellipse, refitted once on its inliers, with the geometric residual against the fitted curve."""
    got = _ellipse(p)
    if got is None:
        return None

    def res(g: dict[str, Any]) -> np.ndarray:
        return polyline_distance(p, ellipse_points(g["center"], *g["semi_axes"], g["angle_deg"]))

    keep = _inliers(res(got))
    refit = _ellipse(p[keep]) if keep.sum() >= 12 else None
    g = min((g for g in (got, refit) if g is not None), key=lambda g: float(np.percentile(res(g), 95)))
    return {**g, **_residual(res(g))}


def _ellipse(p: np.ndarray) -> dict[str, Any] | None:
    """Halir and Flusser's direct least-squares ellipse: centre, semi-axes (major first) and the major axis angle."""
    mu = p.mean(axis=0)
    s = float(np.abs(p - mu).max()) or 1.0
    x, y = ((p - mu) / s).T
    d1 = np.column_stack([x * x, x * y, y * y])
    d2 = np.column_stack([x, y, np.ones_like(x)])
    s1, s2, s3 = d1.T @ d1, d1.T @ d2, d2.T @ d2
    try:
        t = -np.linalg.solve(s3, s2.T)
        m = s1 + s2 @ t
        _, vec = np.linalg.eig(np.array([m[2] / 2, -m[1], m[0] / 2]))
    except np.linalg.LinAlgError:
        return None
    vec = np.real(vec)
    ok = np.where(4 * vec[0] * vec[2] - vec[1] ** 2 > 0)[0]
    if not len(ok):
        return None
    A, B, C, D, E, F = np.concatenate([vec[:, ok[0]], t @ vec[:, ok[0]]])
    den = B * B - 4 * A * C
    if den >= 0:
        return None
    x0, y0 = (2 * C * D - B * E) / den, (2 * A * E - B * D) / den
    num = 2 * (A * E * E + C * D * D - B * D * E + den * F)
    root = math.sqrt((A - C) ** 2 + B * B)
    ax1, ax2 = math.sqrt(abs(num * (A + C + root))) / abs(den), math.sqrt(abs(num * (A + C - root))) / abs(den)
    center = mu + s * np.array([x0, y0])
    theta = math.degrees(0.5 * math.atan2(-B, C - A))
    best = None
    for a, b, th in ((ax1 * s, ax2 * s, theta), (ax2 * s, ax1 * s, theta)):  # the conic formulas leave which semi-axis lies along theta open
        res = polyline_distance(p, ellipse_points(center, a, b, th))
        if best is None or res.max() < best[3].max():
            best = (a, b, th, res)
    a, b, th, res = best
    if a < b:
        a, b, th = b, a, th + 90.0
    th = (th + 90.0) % 180.0 - 90.0
    return {"center": _rounded(center, 4), "semi_axes": [round(float(a), 4), round(float(b), 4)], "angle_deg": round(float(th), 3)}


def rounded_rect_points(center: Any, size: Any, radius: float) -> np.ndarray:
    from shapely.geometry import box

    c, h = np.asarray(center, float), np.asarray(size, float) / 2
    inner = np.maximum(h - radius, 1e-9)
    shape = box(*(c - inner), *(c + inner)).buffer(radius, quad_segs=16) if radius > 1e-9 else box(*(c - h), *(c + h))
    return np.asarray(shape.exterior.coords)


def fit_rounded_rect(p: np.ndarray) -> dict[str, Any]:
    """Axis-aligned rounded rectangle on the outline's bounding box; the corner radius minimises the rms distance."""
    lo, hi = p.min(axis=0), p.max(axis=0)
    c, h = (lo + hi) / 2, (hi - lo) / 2

    def dist(r: float) -> np.ndarray:
        q = np.abs(p - c) - (h - r)
        return np.abs(np.linalg.norm(np.maximum(q, 0.0), axis=1) + np.minimum(q.max(axis=1), 0.0) - r)

    r = _argmin_1d(lambda r: float(np.sqrt(np.mean(dist(r) ** 2))), 0.0, float(h.min()))
    return {"center": _rounded(c, 4), "size": _rounded(2 * h, 4), "corner_radius": round(r, 4), **_residual(dist(r))}


# (u, v) -> canonical (U, V) with the U shape's round end toward -V, and back; each map is an isometry, so residuals carry over
_U_ENDS = {
    "-v": (lambda p: p, lambda p: p),
    "+v": (lambda p: p * [1, -1], lambda p: p * [1, -1]),
    "-u": (lambda p: p[:, ::-1], lambda p: p[:, ::-1]),
    "+u": (lambda p: np.column_stack([p[:, 1], -p[:, 0]]), lambda p: np.column_stack([-p[:, 1], p[:, 0]])),
}


def _u_canonical(cu: float, vc: float, a: float, b: float, top: float, step: float = 0.25) -> np.ndarray:
    """Closed U outline with its round end toward -V: a semi-ellipse (semi-axes a across, b along) centred at (cu, vc), straight
    sides at cu +- a up to `top`, and the flat end at `top`."""
    t = np.linspace(math.pi, 2 * math.pi, 181)
    arc = np.column_stack([cu + a * np.cos(t), vc + b * np.sin(t)])
    n = max(2, int((top - vc) / step) + 1)
    right = np.column_stack([np.full(n, cu + a), np.linspace(vc, top, n)])
    m = max(2, int(2 * a / step) + 1)
    chord = np.column_stack([np.linspace(cu + a, cu - a, m), np.full(m, top)])
    return np.vstack([arc, right, chord, right[::-1] * [-1, 1] + [2 * cu, 0]])


def fit_u_shape(p: np.ndarray) -> dict[str, Any] | None:
    """Two parallel straight sides closed by a semi-elliptic end and a flat end (a channel or canopy skin with its opening
    chorded), axis-aligned with the round end toward any of the four axis directions. Fitted on the outline's bounding box: the one
    unknown is where the round end meets the sides."""

    def err(q: np.ndarray, vc: float) -> np.ndarray:
        lo, hi = q.min(axis=0), q.max(axis=0)
        cu, a = (lo[0] + hi[0]) / 2, (hi[0] - lo[0]) / 2
        return polyline_distance(q, _u_canonical(cu, vc, a, vc - lo[1], hi[1]))

    def rms(q: np.ndarray, vc: float) -> float:
        return float(np.sqrt(np.mean(err(q, vc) ** 2)))

    best = None
    for end, (fwd, _) in _U_ENDS.items():
        q = fwd(p)
        lo, hi = q.min(axis=0), q.max(axis=0)
        vc = _argmin_1d(lambda v, q=q: rms(q, v), lo[1], hi[1], n=11, passes=1)
        if best is None or rms(q, vc) < best[0]:
            best = (rms(q, vc), end, q)
    _, end, q = best
    lo, hi = q.min(axis=0), q.max(axis=0)
    vc = _argmin_1d(lambda v: rms(q, v), lo[1], hi[1])
    cu, a = (lo[0] + hi[0]) / 2, (hi[0] - lo[0]) / 2
    center = _U_ENDS[end][1](np.array([[cu, vc]]))[0]
    return {"end": end, "center": _rounded(center, 4), "half_width": round(a, 4), "depth": round(vc - lo[1], 4), "length": round(hi[1] - vc, 4),
            **_residual(err(q, vc))}


def u_shape_points(g: dict[str, Any]) -> np.ndarray:
    fwd, back = _U_ENDS[g["end"]]
    cu, vc = fwd(np.array([g["center"]], float))[0]
    return back(_u_canonical(cu, vc, g["half_width"], g["depth"], vc + g["length"], step=1.0))


def ring_fits(ring: np.ndarray) -> dict[str, Any]:
    """Circle, ellipse, U shape and rounded rectangle against one closed outline. `best` is the simplest whose 95th-percentile
    residual is within FIT_TOL_MM (and within 0.02 mm of the closest), else None: keep the outline. The 95th percentile, not the
    largest residual, decides, so a notch or a cut (its own feature) does not hide the skin's shape; `max` is reported too."""
    dense = resample_ring(ring, 256)
    out: dict[str, Any] = {"circle": fit_circle(dense), "ellipse": fit_ellipse(dense), "u_shape": fit_u_shape(dense), "rounded_rect": fit_rounded_rect(dense)}
    ok = [(k, v) for k, v in out.items() if v is not None and v["p95"] <= FIT_TOL_MM]
    least = min((v["p95"] for _, v in ok), default=None)
    out["best"] = next((k for k, v in ok if v["p95"] <= least + 0.02), None) if ok else None
    out["tolerance"] = FIT_TOL_MM
    return out


def fit_curve(fit: dict[str, Any]) -> np.ndarray | None:
    """The best fit of `ring_fits` as a closed polyline in the same axes, for overlays."""
    name = fit.get("best")
    g = fit.get(name) if name else None
    if not g:
        return None
    if name == "circle":
        return ellipse_points(g["center"], g["radius"], g["radius"], 0.0, 180)
    if name == "ellipse":
        return ellipse_points(g["center"], *g["semi_axes"], g["angle_deg"], 180)
    if name == "u_shape":
        return u_shape_points(g)
    return rounded_rect_points(g["center"], g["size"], g["corner_radius"])


def _ring_detail(ring_uv: np.ndarray) -> dict[str, Any]:
    pts = resample_ring(ring_uv, OUTLINE_POINTS)
    return {"outline": _rounded(pts, 2), "outline_16": _rounded(pts[::2], 2), "fit": ring_fits(ring_uv)}


def _uv_polygons(polys: list[Any], to_3d: np.ndarray, axis: str) -> list[Any]:
    from shapely.geometry import Polygon

    return [Polygon(_uv(np.asarray(p.exterior.coords), to_3d, axis), [_uv(np.asarray(i.coords), to_3d, axis) for i in p.interiors]) for p in polys]


def section(mesh: trimesh.Trimesh, axis: str, at: float, *, detail: bool = False) -> dict[str, Any]:
    """Planar cross-section: solid area, loop counts, per-loop bounds (contract length unit). `detail` adds, in the plane's world
    axes, each region's outline, hole outlines and fits, and the section's convex hull (the outer skin of a convex section)."""
    i = "xyz".index(axis)
    normal = np.zeros(3)
    normal[i] = 1.0
    origin = np.zeros(3)
    origin[i] = at
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    out: dict[str, Any] = {"plane": axis, "at": at, "area": 0.0, "loops": 0, "holes": 0, "regions": []}
    if sec is None:
        return out
    planar, T = sec.to_2D()
    area = 0.0
    regions = []
    uv_polys = _uv_polygons(planar.polygons_full, T, axis) if detail else []
    for k, poly in enumerate(planar.polygons_full):
        area += poly.area
        b = poly.bounds
        region = {
            "area": float(poly.area),
            "holes": len(poly.interiors),
            "bounds_2d": [float(v) for v in b],
            "size_2d": [float(b[2] - b[0]), float(b[3] - b[1])],
            "centroid_2d": [float(poly.centroid.x), float(poly.centroid.y)],
        }
        if detail:
            q = uv_polys[k]
            ub = q.bounds
            region.update({"bounds_uv": _rounded(ub, 3), "centroid_uv": _rounded([q.centroid.x, q.centroid.y], 3),
                           **_ring_detail(np.asarray(q.exterior.coords)),
                           "hole_outlines": [_rounded(resample_ring(np.asarray(h.coords), 16), 2) for h in q.interiors]})
        regions.append(region)
        out["holes"] += len(poly.interiors)
    out["area"] = float(area)
    out["loops"] = len(planar.polygons_full)
    out["regions"] = sorted(regions, key=lambda r: r["centroid_2d"])
    out["to_3d"] = np.asarray(T).tolist()
    if detail and uv_polys:
        from shapely.geometry import MultiPolygon

        hull = MultiPolygon(uv_polys).convex_hull
        out["uv_axes"] = list(UV_AXES[axis])
        if hull.geom_type == "Polygon":
            out["hull"] = {"area": round(float(hull.area), 3), **_ring_detail(np.asarray(hull.exterior.coords))}
    return out


def station_positions(m: Measured, axis: str, n: int) -> list[float]:
    """n planes across the bbox along `axis`, closer together at both ends (Chebyshev spacing), where noses and tails curve fastest."""
    i = "xyz".index(axis)
    mid, half = (m.bbox_min[i] + m.bbox_max[i]) / 2, (m.bbox_max[i] - m.bbox_min[i]) / 2
    return [round(mid - half * math.cos(math.pi * (k + 0.5) / n), 3) for k in range(n)]


def station_profile(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The envelope along the station axis: every station's bounds, centre and half size in its world axes."""
    rows = []
    for s in sections:
        bs = [r["bounds_uv"] for r in s["regions"] if r.get("bounds_uv")]
        if not bs:
            rows.append({"at": s["at"], "area": 0.0, "loops": 0})
            continue
        b = np.array(bs)
        lo, hi = b[:, :2].min(axis=0), b[:, 2:].max(axis=0)
        rows.append({"at": s["at"], "area": round(s["area"], 3), "loops": s["loops"], "holes": s["holes"], "bounds_uv": _rounded([*lo, *hi], 3),
                     "center_uv": _rounded((lo + hi) / 2, 3), "half_size_uv": _rounded((hi - lo) / 2, 3)})
    return rows


def default_section_planes(m: Measured, per_axis: int = 3) -> list[tuple[str, float]]:
    planes = []
    for i, axis in enumerate("xyz"):
        lo, hi = m.bbox_min[i], m.bbox_max[i]
        for k in range(1, per_axis + 1):
            planes.append((axis, lo + (hi - lo) * k / (per_axis + 1)))
    return planes


def silhouette(mesh: trimesh.Trimesh, view: str, px_long: int = 800, grid_mm: float = 10.0) -> tuple[Image.Image, float]:
    """Orthographic filled silhouette. view: top (xy), front (xz), right (yz). Returns (image, mm_per_px)."""
    cols = {"top": (0, 1), "front": (0, 2), "right": (1, 2)}[view]
    lo, hi = mesh.bounds
    size2 = np.array([hi[cols[0]] - lo[cols[0]], hi[cols[1]] - lo[cols[1]]])
    mm_per_px = float(max(size2.max(), 1e-9) / px_long)
    pad = 20
    w, h = int(size2[0] / mm_per_px) + 2 * pad, int(size2[1] / mm_per_px) + 2 * pad
    img = Image.new("L", (w, h), 255)
    draw = ImageDraw.Draw(img)
    # grid
    for gx in np.arange(0, size2[0] + grid_mm, grid_mm):
        x = pad + gx / mm_per_px
        draw.line([(x, 0), (x, h)], fill=225)
    for gy in np.arange(0, size2[1] + grid_mm, grid_mm):
        y = h - pad - gy / mm_per_px
        draw.line([(0, y), (w, y)], fill=225)
    v = mesh.vertices
    pts = np.stack([(v[:, cols[0]] - lo[cols[0]]) / mm_per_px + pad, h - pad - (v[:, cols[1]] - lo[cols[1]]) / mm_per_px], axis=1)
    for tri in mesh.faces:
        draw.polygon([tuple(pts[i]) for i in tri], fill=40)
    return img, mm_per_px


def sections_sheet(mesh: trimesh.Trimesh, sections: list[dict[str, Any]], out: Path, cell: int = 300) -> None:
    """One cell per section in the plane's world axes (UV_AXES, second axis up); a section with detail overlays the best fit of
    each region and of its hull in grey."""
    n = len(sections)
    if n == 0:
        return
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    sheet = Image.new("L", (cols * cell, rows * cell), 255)
    draw = ImageDraw.Draw(sheet)
    for k, s in enumerate(sections):
        ox, oy = (k % cols) * cell, (k // cols) * cell
        draw.rectangle([ox, oy, ox + cell - 1, oy + cell - 1], outline=200)
        draw.text((ox + 6, oy + 6), f"{s['plane']}={s['at']:.2f}  A={s['area']:.1f}  loops={s['loops']} holes={s['holes']}", fill=0)
        i = "xyz".index(s["plane"])
        normal = np.zeros(3)
        normal[i] = 1
        origin = np.zeros(3)
        origin[i] = s["at"]
        sec = mesh.section(plane_origin=origin, plane_normal=normal)
        if sec is None:
            continue
        planar, T = sec.to_2D()
        polys = _uv_polygons(planar.polygons_full, T, s["plane"])
        if not polys:
            continue
        u, v = UV_AXES[s["plane"]]
        fits = [(r.get("fit") or {}) for r in s["regions"]] + [((s.get("hull") or {}).get("fit") or {})]
        named = [f.get("best") for f in fits[:-1] if f.get("best")]
        draw.text((ox + 6, oy + 18), f"{u} right, {v} up; fits {len(named)}/{len(s['regions'])}" + (f"; hull {fits[-1]['best']}" if fits[-1].get("best") else ""), fill=90)
        allpts = np.vstack([np.asarray(p.exterior.coords) for p in polys])
        lo2, hi2 = allpts.min(axis=0), allpts.max(axis=0)
        scale = (cell - 50) / max((hi2 - lo2).max(), 1e-9)

        def px(c: np.ndarray, ox: int = ox, oy: int = oy, lo2: np.ndarray = lo2, scale: float = scale) -> list[tuple[float, float]]:
            return [(ox + 20 + (x - lo2[0]) * scale, oy + cell - 16 - (y - lo2[1]) * scale) for x, y in c]

        for poly in polys:
            for r in [poly.exterior, *poly.interiors]:
                draw.line(px(np.asarray(r.coords)), fill=0, width=2)
        for f in fits:
            curve = fit_curve(f)
            if curve is not None:
                draw.line(px(np.vstack([curve, curve[:1]])), fill=150, width=1)
    sheet.save(out)


def ingest(
    path: Path,
    out_dir: Path,
    *,
    units: str,
    axes: str | None = None,
    datum: str = "min",
    expect_size_mm: list[float] | None = None,
    anchor_tolerance_rel: float = 0.02,
    section_planes: list[tuple[str, float]] | None = None,
    dry_run: bool = False,
    decimate_faces: int = 200_000,
    treatment: str = "reproduction",
    stations: int = 0,
    station_axis: str | None = None,
) -> dict[str, Any]:
    """Measure a reference mesh into `out_dir/reference.json` (+ ply, sections, silhouettes). `stations` > 0 adds that many
    cross-sections along `station_axis` (default the longest) with outlines and fits, the profile along that axis, and the same
    detail on every other section."""
    path = Path(path)
    if units not in UNIT_TO_MM:
        raise IngestError(f"units must be one of {sorted(UNIT_TO_MM)}")
    if station_axis is not None and station_axis not in UV_AXES:
        raise IngestError("station axis must be x, y or z")
    mesh = load_mesh(path)
    scale = UNIT_TO_MM[units]
    R = parse_axes(axes)
    T = np.eye(4)
    T[:3, :3] = R * scale
    mesh.apply_transform(T)
    lo, hi = mesh.bounds
    if datum == "min":
        shift = -lo
    elif datum == "center":
        shift = -(lo + hi) / 2
    elif datum == "centroid":
        shift = -(mesh.center_mass if mesh.is_watertight else mesh.centroid)
    elif datum == "keep":
        shift = np.zeros(3)
    else:
        raise IngestError("datum must be min|center|centroid|keep")
    mesh.apply_translation(shift)

    m = measure(mesh)
    anchor: dict[str, Any] = {"checked": False}
    if expect_size_mm:
        got = sorted(m.size, reverse=True)
        exp = sorted(expect_size_mm, reverse=True)
        rel = [abs(g - e) / e if e else 0.0 for g, e in zip(got, exp)]
        anchor = {"checked": True, "expected_sorted_mm": exp, "measured_sorted_mm": got, "rel_error": rel, "ok": all(r <= anchor_tolerance_rel for r in rel)}
        if not anchor["ok"]:
            raise IngestError(
                f"unit anchor failed: expected sorted size {exp} mm, measured {got} mm (declared unit {units}); wrong --units or --axes?"
            )
    planes = section_planes or default_section_planes(m)
    m.sections = [section(mesh, a, v, detail=stations > 0) for a, v in planes]
    station_block: dict[str, Any] | None = None
    if stations > 0:
        ax = station_axis or "xyz"[int(np.argmax(m.size))]
        st = [section(mesh, ax, v, detail=True) for v in station_positions(m, ax, stations)]
        station_block = {"axis": ax, "uv_axes": list(UV_AXES[ax]), "positions": [s["at"] for s in st], "fit_tolerance_mm": FIT_TOL_MM,
                         "outline_points": OUTLINE_POINTS, "sections": st}

    record: dict[str, Any] = {
        "kind": "reference-model",
        "generated_at": utc_now(),
        "source": {"file": path.name, "sha256": sha256_file(path), "declared_units": units, "faces_original": int(len(mesh.faces))},
        "transform": {"axes": axes or "identity", "rotation": R.tolist(), "scale_to_mm": scale, "datum": datum, "translation_mm": shift.tolist()},
        "anchor": anchor,
        "treatment": treatment,
        "measurements": {
            "bbox_min": m.bbox_min, "bbox_max": m.bbox_max, "size": m.size,
            "volume": m.volume, "surface_area": m.surface_area, "center_of_mass": m.center_of_mass,
            "watertight": m.watertight, "components": m.components, "faces": m.faces,
            "principal_axes": m.principal_axes, "principal_extents": m.principal_extents,
            "sections": m.sections,
            **({"stations": station_block, "profile": station_profile(station_block["sections"])} if station_block else {}),
        },
        "suggested": {
            "envelope": {"min": [round(v, 4) for v in m.bbox_min], "max": [round(v, 4) for v in m.bbox_max], "tolerance": 0.1},
            "acceptance": {
                "volume": {"expected": round(m.volume, 3), "tolerance_rel": 0.01, "provenance": "measured (reference model)"},
                "center_of_mass": {"expected": [round(v, 3) for v in m.center_of_mass], "tolerance": 0.25, "provenance": "measured (reference model)"},
                "deviation": {"p95_max": 0.2, "hausdorff_max": 0.5, "silhouette_iou_min": 0.98},
            },
        },
        "notes": [],
    }
    if not m.watertight:
        record["notes"].append("mesh is not watertight: volume and centre of mass are approximate")
    if m.components > 1:
        record["notes"].append(f"mesh has {m.components} connected components")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "-dryrun" if dry_run else ""
    sections_sheet(mesh, m.sections, out_dir / f"reference-sections{suffix}.png")
    files = {"sections": f"reference-sections{suffix}.png"}
    if station_block:
        sections_sheet(mesh, station_block["sections"], out_dir / f"reference-sections-stations{suffix}.png")
        files["stations"] = f"reference-sections-stations{suffix}.png"
    if not dry_run:
        export = mesh
        if len(mesh.faces) > decimate_faces:
            export = mesh.simplify_quadric_decimation(face_count=decimate_faces)
            record["notes"].append(f"reference.ply decimated to {len(export.faces)} faces")
        export.export(out_dir / "reference.ply")
        files["ply"] = "reference.ply"
        for view in ("top", "front", "right"):
            img, mpp = silhouette(mesh, view)
            meta = PngInfo()
            meta.add_text("mm_per_px", f"{mpp:.6f}")
            meta.add_text("view", view)
            meta.add_text("grid_mm", "10")
            img.save(out_dir / f"silhouette-{view}.png", pnginfo=meta)
            files[f"silhouette_{view}"] = f"silhouette-{view}.png"
        record["files"] = files
        (out_dir / "reference.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    else:
        record["files"] = files
        (out_dir / "reference-dryrun.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record

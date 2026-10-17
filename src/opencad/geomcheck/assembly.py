"""Multi-body and interior checks: solid identity, interference and gaps against other solids or hardware envelopes,
wall thickness by inward ray casting, and passage connectivity by voxel flood fill (OpenCascade + trimesh, no Zoo)."""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from OCP.TopoDS import TopoDS_Shape

from opencad.geomcheck import brep


# --- solids -----------------------------------------------------------------------------------

def select_solid(shape: TopoDS_Shape, contains: list[float]):
    """The solid of `shape` that contains the point, or None."""
    for s in brep.solids(shape):
        if brep.classify_points(s, [tuple(contains)])[0] == "in":
            return s
    return None


def solid_props(solid) -> dict[str, Any]:
    lo, hi = brep.bbox(solid)
    props = brep.volume_props(solid)
    return {"volume": props["volume"], "surface_area": props["surface_area"], "center_of_mass": props["center_of_mass"],
            "bbox_min": lo, "bbox_max": hi, "bbox_size": [h - l for l, h in zip(lo, hi)]}


# --- hardware envelopes -----------------------------------------------------------------------

def make_box(lo: list[float], hi: list[float]) -> TopoDS_Shape:
    return BRepPrimAPI_MakeBox(gp_Pnt(*lo), gp_Pnt(*hi)).Shape()


def make_cylinder(point: list[float], direction: list[float], radius: float, length: float) -> TopoDS_Shape:
    d = brep._unit(direction)
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*point), gp_Dir(*d)), radius, length).Shape()


def load_placed(path: Path, translate: list[float] | None = None, scale: float | None = None) -> TopoDS_Shape:
    """A hardware STEP (board, connector, cooler) moved into the part frame."""
    shape = brep.read_step(path)
    if scale and abs(scale - 1.0) > 1e-12:
        t = gp_Trsf()
        t.SetScale(gp_Pnt(0, 0, 0), scale)
        shape = BRepBuilderAPI_Transform(shape, t, True).Shape()
    if translate and any(abs(x) > 1e-12 for x in translate):
        t = gp_Trsf()
        t.SetTranslation(gp_Vec(*translate))
        shape = BRepBuilderAPI_Transform(shape, t, True).Shape()
    return shape


# --- interference and gaps ---------------------------------------------------------------------

def common_volume(a: TopoDS_Shape, b: TopoDS_Shape) -> float:
    op = BRepAlgoAPI_Common(a, b)
    op.Build()
    if not op.IsDone():
        return float("nan")
    return brep.volume_props(op.Shape())["volume"]


EXACT_DISTANCE_FACES = 300  # past this many faces between them, B-rep extrema on free-form surfaces can run for hours


def _mesh(shape: TopoDS_Shape, deflection: float) -> trimesh.Trimesh:
    import tempfile

    from opencad.backends.local import write_stl

    with tempfile.TemporaryDirectory(prefix="opencad-dist-") as td:
        path = write_stl(shape, Path(td) / "s.stl", deflection=deflection, angular=0.2)
        return trimesh.load(path, force="mesh")


def mesh_distance(a: TopoDS_Shape, b: TopoDS_Shape, deflection: float) -> float:
    """Closest approach of two tessellations: vertex KD-tree candidates, then exact point-to-mesh distances (error ~ deflection)."""
    from scipy.spatial import cKDTree

    ma, mb = _mesh(a, deflection), _mesh(b, deflection)
    best = float("inf")
    for src, dst in ((ma, mb), (mb, ma)):
        d0, _ = cKDTree(dst.vertices).query(src.vertices)
        near = src.vertices[np.argsort(d0)[:2000]]
        _, d, _ = trimesh.proximity.closest_point(dst, near)
        best = min(best, float(d.min()))
    return best


def min_distance(a: TopoDS_Shape, b: TopoDS_Shape) -> float:
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer

    def faces(s: TopoDS_Shape) -> int:
        ex, n = TopExp_Explorer(s, TopAbs_FACE), 0
        while ex.More():
            n += 1
            ex.Next()
        return n

    if faces(a) + faces(b) > EXACT_DISTANCE_FACES:
        lo, hi = np.min([brep.bbox(a)[0], brep.bbox(b)[0]], axis=0), np.max([brep.bbox(a)[1], brep.bbox(b)[1]], axis=0)
        return mesh_distance(a, b, max(0.01, 5e-5 * float(np.linalg.norm(hi - lo))))
    d = BRepExtrema_DistShapeShape(a, b)
    d.Perform()
    return float(d.Value()) if d.IsDone() else float("nan")


def clearance(a: TopoDS_Shape, b: TopoDS_Shape, *, min_gap: float = 0.0, max_gap: float | None = None, interference_tol: float = 1e-3) -> dict[str, Any]:
    """No interference (common volume below tol) and, when asked, a gap band between two bodies."""
    inter = common_volume(a, b)
    gap = min_distance(a, b) if inter <= interference_tol else 0.0
    ok = inter <= interference_tol and gap >= min_gap - 1e-6 and (max_gap is None or gap <= max_gap + 1e-6)
    return {"interference_volume": inter, "gap": gap, "min_gap": min_gap, "max_gap": max_gap, "ok": bool(ok)}


# --- wall thickness ---------------------------------------------------------------------------

THIN_CELL_MM = 4.0
THIN_CLUSTERS_MAX = 12


def thin_clusters(pts: np.ndarray, thick: np.ndarray, below: float, cell: float = THIN_CELL_MM, limit: int = THIN_CLUSTERS_MAX) -> list[dict[str, Any]]:
    """Where the sub-minimum wall is: surface samples thinner than `below`, binned on a `cell` mm grid, largest bins first.
    Each cluster is a box with its sample count, share of all samples and median thickness: a worker can act on a box."""
    mask = thick < below
    if not mask.any():
        return []
    p, t = pts[mask], thick[mask]
    keys = [tuple(k) for k in np.floor(p / cell).astype(int)]
    # occupied cells that share a face are one wall: union-find over the cells
    parent: dict[tuple[int, ...], tuple[int, ...]] = {k: k for k in set(keys)}

    def root(k: tuple[int, ...]) -> tuple[int, ...]:
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    for k in list(parent):
        for d in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):  # face-adjacent cells only: corner contact would chain unrelated skins into one box
            nb = (k[0] + d[0], k[1] + d[1], k[2] + d[2])
            if nb in parent:
                ra, rb = root(k), root(nb)
                if ra != rb:
                    parent[ra] = rb
    labels = np.asarray([hash(root(k)) for k in keys])
    out: list[dict[str, Any]] = []
    for lab in np.unique(labels):
        sel = labels == lab
        q = p[sel]
        out.append({"n": int(sel.sum()), "share": round(float(sel.sum()) / len(pts), 4), "median": round(float(np.median(t[sel])), 3),
                    "min": q.min(axis=0).round(2).tolist(), "max": q.max(axis=0).round(2).tolist()})
    out.sort(key=lambda c: -c["n"])
    return out[:limit]


def thickness(mesh_path: Path, *, samples: int = 4000, seed: int = 0, region: tuple[list[float], list[float]] | None = None,
              floor: float = 0.05, max_thickness: float | None = None, thin_below: float | None = None) -> dict[str, Any]:
    """Local wall thickness at sampled surface points: distance along the inward normal to the next surface hit.

    `region` restricts the sample to surface points inside a box (a wall of interest); hits closer than
    `floor` are the same face (skipped); `max_thickness` caps rays that cross the whole part (open interiors);
    `thin_below` adds `thin_clusters`, the boxes where samples measure under that thickness.
    """
    mesh = trimesh.load(mesh_path, force="mesh")
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(list(mesh.geometry.values()))
    rng = np.random.default_rng(seed)
    pts, fidx = trimesh.sample.sample_surface(mesh, samples * (4 if region else 1), seed=int(rng.integers(0, 2**31)))
    normals = mesh.face_normals[fidx]
    if region is not None:
        lo, hi = np.asarray(region[0], float), np.asarray(region[1], float)
        keep = np.all((pts >= lo) & (pts <= hi), axis=1)
        pts, normals = pts[keep], normals[keep]
    if len(pts) == 0:
        return {"ok": False, "error": "no surface samples in region", "samples": 0}
    origins = pts - normals * (floor * 0.5)
    locations, index_ray, _ = mesh.ray.intersects_location(origins, -normals, multiple_hits=True)
    best = np.full(len(pts), np.inf)
    if len(locations):
        # distances are measured from the true surface point (the origin sits floor/2 inside it)
        d = np.linalg.norm(locations - origins[index_ray], axis=1) + floor * 0.5
        for i, dist in zip(index_ray, d):
            if dist > floor and dist < best[i]:
                best[i] = dist
    finite = best[np.isfinite(best)]
    if max_thickness is not None:
        finite = finite[finite <= max_thickness]
    if len(finite) == 0:
        return {"ok": False, "error": "no inward hits", "samples": int(len(pts))}
    order = np.argsort(best)
    thin_idx = order[:5]
    out = {
        "samples": int(len(pts)), "hits": int(len(finite)),
        "min": float(finite.min()), "p01": float(np.percentile(finite, 1)), "p05": float(np.percentile(finite, 5)), "p50": float(np.percentile(finite, 50)), "max": float(finite.max()),
        "thinnest_points": [pts[i].round(3).tolist() for i in thin_idx if np.isfinite(best[i])],
    }
    if thin_below is not None:
        ok = np.isfinite(best) if max_thickness is None else (np.isfinite(best) & (best <= max_thickness))
        out["thin_clusters"] = thin_clusters(pts[ok], best[ok], float(thin_below))
    return out


# --- passages ---------------------------------------------------------------------------------

def _mesh_key(p: Path) -> tuple[str, int, int]:
    st = p.stat()
    return (str(p.resolve()), st.st_size, st.st_mtime_ns)


def ball_closing(solid: np.ndarray, r_vox: int) -> np.ndarray:
    """Morphological closing by a Euclidean ball of `r_vox` voxels through two distance transforms: dilation is
    `dist(x, solid) <= r`, erosion of that is `dist(x, ~dilated) > r`. Exact for the ball and O(N), where
    scipy's structuring-element closing is O(N * r^3) (minutes per passage on a 0.25 mm duct grid)."""
    from scipy import ndimage

    dilated = ndimage.distance_transform_edt(~solid) <= r_vox
    return ndimage.distance_transform_edt(dilated) > r_vox


FILL_LEAK_RATIO = 0.8


@functools.lru_cache(maxsize=4)
def _closed_grid(mesh_key: tuple[str, int, int], pitch: float, seal_radius: float | None, pad_voxels: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, float | None, dict[str, Any]]:
    """(voxel solid before closing, after closing, world origin of voxel (0,0,0), effective seal mm, fill integrity), shared by every passage of one part.

    The flood fill leaks through cracks in a non-watertight shell, leaving thick material as void; a fake cavity
    then reads as a passage (voron reference STL: 802 open edges, fill 11.5 of 40.1 cm3). `fill` records the ratio.
    """
    mesh = trimesh.load(mesh_key[0], force="mesh")
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(list(mesh.geometry.values()))
    vg = mesh.voxelized(pitch).fill()
    solid = vg.matrix.copy()
    mesh_volume = float(abs(mesh.volume))
    fill_volume = float(solid.sum()) * pitch ** 3
    ratio = fill_volume / mesh_volume if mesh_volume > 0 else None
    open_edges = int((np.bincount(mesh.edges_unique_inverse) == 1).sum())
    fill = {"watertight": bool(mesh.is_watertight), "open_edges": open_edges, "mesh_volume": mesh_volume, "fill_volume": fill_volume, "fill_ratio": ratio,
            "leak": bool(ratio is not None and ratio < FILL_LEAK_RATIO)}
    origin = np.asarray(vg.transform[:3, 3], float)  # world position of voxel (0,0,0) centre
    # pad so the exterior is connected around the part (and the closing has room to work)
    pad = max(pad_voxels, int(np.ceil((seal_radius or 0) / pitch)) + 2)
    solid = np.pad(solid, pad, constant_values=False)
    origin = origin - pad * pitch
    before = solid
    seal_effective = None
    if seal_radius:
        # whole voxels rounded DOWN: a 2.4 mm seal at 0.5 mm pitch must not become a 2.5 mm ball that fills a 2.5 mm bore
        r = max(1, int(seal_radius // pitch))
        seal_effective = r * pitch
        solid = ball_closing(before, r)
    before.setflags(write=False)
    solid.setflags(write=False)
    return before, solid, origin, seal_effective, fill


def passage(mesh_path: Path, a: list[float], b: list[float], *, pitch: float = 0.5, plugs: list[tuple[list[float], list[float]]] | None = None,
            seal_radius: float | None = None, pad_voxels: int = 3, expect_connected: bool = True) -> dict[str, Any]:
    """Is there an interior void path from `a` to `b` that does not go around the outside?

    The STL is voxelized and filled. Ports are sealed either by `plugs` (boxes in mm) or by a
    morphological closing of radius `seal_radius` (mm), which shuts every opening narrower than
    about twice that radius while leaving the passage itself open. Void voxels touching the padded
    bounding box are `exterior`. Both probes must lie in interior void voxels and (when
    `expect_connected`) share a connected component; `reaches_exterior` reports an unsealed opening.
    """
    from scipy import ndimage

    before, solid, origin, seal_effective, fill = _closed_grid(_mesh_key(Path(mesh_path)), float(pitch), seal_radius, pad_voxels)
    solid = solid.copy()  # plugs are painted per passage; the closed grid is shared across passages
    out_err = None
    if fill["leak"]:
        out_err = (f"voxel fill leaked: filled {fill['fill_volume']:.0f} mm3 of a {fill['mesh_volume']:.0f} mm3 mesh ({fill['open_edges']} open edges); "
                   "void components inside the material are artefacts, not passages; tessellate a watertight mesh from the STEP first")
    elif seal_radius:
        sealed_probe = [tuple(int(x) for x in np.round((np.asarray(p, float) - origin) / pitch).astype(int)) for p in (a, b)]
        if all(all(0 <= k < n for k, n in zip(i, solid.shape)) and solid[i] and not before[i] for i in sealed_probe):
            out_err = f"the closing radius {seal_effective:g} mm fills the passage at both probe points; seal a uniform bore with `plugs` over its mouths instead"

    def idx(p: list[float]) -> tuple[int, int, int]:
        i = np.round((np.asarray(p, float) - origin) / pitch).astype(int)
        return tuple(int(x) for x in i)

    def inside(i: tuple[int, int, int]) -> bool:
        return all(0 <= k < n for k, n in zip(i, solid.shape))

    for lo, hi in plugs or []:
        i0, i1 = idx(lo), idx(hi)
        sl = tuple(slice(max(0, min(p, q)), min(n, max(p, q) + 1)) for p, q, n in zip(i0, i1, solid.shape))
        solid[sl] = True
    void = ~solid
    labels, n = ndimage.label(void)
    border = np.zeros_like(void)
    border[0, :, :] = border[-1, :, :] = border[:, 0, :] = border[:, -1, :] = border[:, :, 0] = border[:, :, -1] = True
    exterior_labels = set(np.unique(labels[border & void]).tolist()) - {0}
    ia, ib = idx(a), idx(b)
    out: dict[str, Any] = {"pitch": pitch, "grid": list(solid.shape), "components": int(n), "exterior_components": len(exterior_labels)}
    for name, i in (("a", ia), ("b", ib)):
        if not inside(i):
            out[name] = {"state": "outside-grid"}
            continue
        lab = int(labels[i])
        out[name] = {"index": list(i), "state": "solid" if solid[i] else ("exterior" if lab in exterior_labels else "interior"), "label": lab}
    la, lb = out["a"].get("label"), out["b"].get("label")
    interior_ok = out["a"].get("state") == "interior" and out["b"].get("state") == "interior"
    out["connected"] = bool(interior_ok and la == lb)
    out["reaches_exterior"] = bool((la in exterior_labels) or (lb in exterior_labels))
    if out["a"].get("state") == "interior":
        comp = labels == la
        # the void voxels are wholly void, the solid layer touching them partly: the true volume lies between the two counts
        out["passage_volume"] = float(comp.sum() * pitch ** 3)
        out["passage_volume_max"] = float((comp.sum() + (ndimage.binary_dilation(comp) & solid).sum()) * pitch ** 3)
    out["seal_radius"] = seal_radius
    out["seal_effective_mm"] = seal_effective
    out["fill"] = fill
    if out_err:
        out["error"] = out_err
    out["expect_connected"] = expect_connected
    out["ok"] = bool(interior_ok and not out["reaches_exterior"] and (out["connected"] if expect_connected else not out["connected"]) and not fill["leak"])
    return out

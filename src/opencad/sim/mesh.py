"""Tetrahedral meshes of placed bodies with gmsh (Python SDK). Each named boundary of the domains stage becomes a set of element
faces: gmsh surfaces are matched to the boundary's B-rep faces by centroid and area, and every surface triangle is mapped to the
(element, face) of the tetrahedron it bounds, in CalculiX face numbering."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

# CalculiX C3D4/C3D10 faces by corner index (0-based): F1 1-2-3, F2 1-4-2, F3 2-4-3, F4 3-4-1
TET_FACES = ((0, 1, 2), (0, 3, 1), (1, 3, 2), (2, 3, 0))
GMSH_TO_CCX_TET10 = (0, 1, 2, 3, 4, 5, 6, 7, 9, 8)  # gmsh edges 01 12 20 30 32 31 -> ccx 12 23 31 14 24 34


@dataclass
class Mesh:
    order: int
    nodes: np.ndarray  # (N, 3) mm, row k is node ids[k]
    ids: np.ndarray
    elements: dict[str, np.ndarray] = field(default_factory=dict)  # body -> (M, 4 | 10) node ids, CalculiX order
    elem_ids: dict[str, np.ndarray] = field(default_factory=dict)
    faces: dict[str, list[tuple[int, int]]] = field(default_factory=dict)  # "body:label" -> [(element id, face 1..4)]
    tris: dict[str, np.ndarray] = field(default_factory=dict)  # "body:label" -> (K, 3) corner node ids
    unmatched: dict[str, list[int]] = field(default_factory=dict)

    def index(self) -> dict[int, int]:
        return {int(t): k for k, t in enumerate(self.ids)}

    def coords(self, node_ids: Any) -> np.ndarray:
        idx = self.index()
        return self.nodes[[idx[int(n)] for n in np.asarray(node_ids).ravel()]].reshape(*np.asarray(node_ids).shape, 3)

    def surface_nodes(self, key: str) -> np.ndarray:
        return np.unique(self.tris[key]) if key in self.tris else np.array([], int)

    def tri_areas(self, key: str) -> np.ndarray:
        p = self.coords(self.tris[key])
        return 0.5 * np.linalg.norm(np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), axis=1)

    def tet_volumes(self, body: str) -> np.ndarray:
        p = self.coords(self.elements[body][:, :4])
        return np.abs(np.einsum("ij,ij->i", np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), p[:, 3] - p[:, 0])) / 6.0

    @property
    def size(self) -> dict[str, int]:
        return {"nodes": int(len(self.ids)), **{f"elements:{b}": int(len(e)) for b, e in self.elements.items()}}


def _match(gm: Any, surfaces: list[int], faces: list[dict[str, Any]], scale: float) -> dict[int, int]:
    """gmsh surface tag -> B-rep face id, by centroid within 1e-4 x scale and area within 0.1 %."""
    out = {}
    for s in surfaces:
        c = np.asarray(gm.occ.getCenterOfMass(2, s))
        a = gm.occ.getMass(2, s)
        for f in faces:
            if np.linalg.norm(c - np.asarray(f["centroid"])) <= 1e-4 * scale + 1e-6 and abs(a - f["area"]) <= 1e-3 * max(f["area"], 1e-9):
                out[s] = f["id"]
                break
    return out


def tet_mesh(bodies: dict[str, Path], labels: dict[str, dict[str, list[dict[str, Any]]]], *, size: float, size_min: float | None = None,
             refine: dict[str, float] | None = None, order: int = 2, threads: int = 8) -> Mesh:
    """bodies: name -> placed STEP (mm); labels: body -> label -> B-rep face rows (id, centroid, area) from the domains stage.
    refine: "body:label" -> element size at that surface (distance-threshold field growing to `size`)."""
    import gmsh

    gmsh.initialize(interruptible=False)
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.NumThreads", threads)
        gmsh.option.setNumber("Mesh.MeshSizeMax", size)
        gmsh.option.setNumber("Mesh.MeshSizeMin", size_min or size / 4)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)
        gmsh.option.setNumber("Mesh.Algorithm3D", 10)
        gmsh.model.add("opencad")
        vols: dict[str, list[int]] = {}
        for name, step in bodies.items():
            vols[name] = [t for d, t in gmsh.model.occ.importShapes(str(step)) if d == 3]
        gmsh.model.occ.synchronize()
        surf_label: dict[str, dict[int, str]] = {}
        unmatched: dict[str, list[int]] = {}
        for name, vtags in vols.items():
            surfs = sorted({abs(t) for _, t in gmsh.model.getBoundary([(3, v) for v in vtags], oriented=False)})
            lo = np.min([gmsh.model.getBoundingBox(3, v)[:3] for v in vtags], axis=0)
            hi = np.max([gmsh.model.getBoundingBox(3, v)[3:] for v in vtags], axis=0)
            scale = float(np.linalg.norm(hi - lo))
            by_face = {f["id"]: lab for lab, rows in (labels.get(name) or {}).items() for f in rows}
            rows = [f for rows in (labels.get(name) or {}).values() for f in rows]
            matched = _match(gmsh.model, surfs, rows, scale)
            surf_label[name] = {s: by_face[fid] for s, fid in matched.items()}
            unmatched[name] = sorted(set(by_face) - set(matched.values()))
        fields = []
        for key, h in (refine or {}).items():
            body, label = key.split(":", 1)
            tags = [s for s, lab in surf_label.get(body, {}).items() if lab == label]
            if not tags:
                continue
            fd = gmsh.model.mesh.field.add("Distance")
            gmsh.model.mesh.field.setNumbers(fd, "SurfacesList", tags)
            ft = gmsh.model.mesh.field.add("Threshold")
            gmsh.model.mesh.field.setNumber(ft, "InField", fd)
            gmsh.model.mesh.field.setNumber(ft, "SizeMin", h)
            gmsh.model.mesh.field.setNumber(ft, "SizeMax", size)
            gmsh.model.mesh.field.setNumber(ft, "DistMin", h)
            gmsh.model.mesh.field.setNumber(ft, "DistMax", 6 * size)
            fields.append(ft)
        if fields:
            fm = gmsh.model.mesh.field.add("Min")
            gmsh.model.mesh.field.setNumbers(fm, "FieldsList", fields)
            gmsh.model.mesh.field.setAsBackgroundMesh(fm)
        gmsh.model.mesh.generate(3)
        if order == 2:
            gmsh.model.mesh.setOrder(2)
        tags, coords, _ = gmsh.model.mesh.getNodes()
        mesh = Mesh(order=order, nodes=np.asarray(coords).reshape(-1, 3), ids=np.asarray(tags, int), unmatched=unmatched)
        next_id = 1
        for name, vtags in vols.items():
            conn = []
            for v in vtags:
                etypes, _, enodes = gmsh.model.mesh.getElements(3, v)
                for et, en in zip(etypes, enodes):
                    n = {4: 4, 11: 10}.get(int(et))
                    if n is None:
                        raise RuntimeError(f"unexpected gmsh volume element type {et} in {name}")
                    conn.append(np.asarray(en, int).reshape(-1, n))
            el = np.vstack(conn)
            if el.shape[1] == 10:
                el = el[:, GMSH_TO_CCX_TET10]
            mesh.elements[name] = el
            mesh.elem_ids[name] = np.arange(next_id, next_id + len(el))
            next_id += len(el)
            lookup = {}
            for eid, row in zip(mesh.elem_ids[name], el[:, :4]):
                for k, (i, j, m) in enumerate(TET_FACES, start=1):
                    lookup[frozenset((int(row[i]), int(row[j]), int(row[m])))] = (int(eid), k)
            for s, lab in surf_label[name].items():
                key = f"{name}:{lab}"
                etypes, _, enodes = gmsh.model.mesh.getElements(2, s)
                for et, en in zip(etypes, enodes):
                    npe = {2: 3, 9: 6}[int(et)]
                    tri = np.asarray(en, int).reshape(-1, npe)[:, :3]
                    mesh.tris[key] = np.vstack([mesh.tris[key], tri]) if key in mesh.tris else tri
                    mesh.faces.setdefault(key, []).extend(lookup[frozenset(map(int, t))] for t in tri)
        return mesh
    finally:
        gmsh.finalize()


def check_tet10(mesh: Mesh, body: str, sample: int = 50) -> float:
    """Largest distance of a mid-edge node from its edge midpoint (a node-ordering check; ~0 for straight-sided elements)."""
    el = mesh.elements[body]
    if el.shape[1] != 10:
        return 0.0
    edges = ((0, 1, 4), (1, 2, 5), (2, 0, 6), (0, 3, 7), (1, 3, 8), (2, 3, 9))
    worst = 0.0
    for row in el[: sample]:
        p = mesh.coords(row)
        for a, b, m in edges:
            worst = max(worst, float(np.linalg.norm(p[m] - (p[a] + p[b]) / 2)) / (float(np.linalg.norm(p[a] - p[b])) or 1.0))
    return worst

"""2D coordinate-table ingest (airfoil / closed profile) -> profile.json (+ png)."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from opencad.io import sha256_file, utc_now
from opencad.reference.mesh import UNIT_TO_MM, IngestError


def read_loop(path: Path, *, sheet: str | None = None, sides: list[tuple[int, int]] | None = None, skip: int = 0) -> np.ndarray:
    """Closed loop from one column pair, or from two sides (e.g. pressure and suction side listed
    LE->TE in separate column pairs): side 1 forward, side 2 reversed, shared endpoints dropped."""
    sides = sides or [(0, 1)]
    if len(sides) == 1:
        return read_table(path, sheet=sheet, columns=tuple(sides[0]), skip=skip)
    a = read_table(path, sheet=sheet, columns=tuple(sides[0]), skip=skip)
    b = read_table(path, sheet=sheet, columns=tuple(sides[1]), skip=skip)[::-1]
    if np.allclose(a[-1], b[0], atol=1e-12):
        b = b[1:]
    if np.allclose(a[0], b[-1], atol=1e-12):
        b = b[:-1]
    return np.vstack([a, b])


def read_table(path: Path, *, sheet: str | None = None, columns: tuple[int, int] = (0, 1), skip: int = 0) -> np.ndarray:
    path = Path(path)
    rows: list[list[Any]] = []
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        import openpyxl

        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
    elif path.suffix.lower() in (".csv", ".txt", ".dat"):
        import io

        text = path.read_text(encoding="utf-8", errors="replace")
        sample = text[:4096]
        # NASA/Tecplot .dat files are whitespace-delimited with leading spaces; a CSV
        # sniffer treats the indent as an empty first column. Prefer csv only when
        # commas or semicolons actually separate fields.
        use_csv = sample.count(",") >= 2 or sample.count(";") >= 2
        if use_csv:
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
            except csv.Error:
                dialect = csv.excel
            rows = [r for r in csv.reader(io.StringIO(text), dialect)]
        else:
            rows = [line.split() for line in text.splitlines()]
    else:
        raise IngestError(f"{path.name}: expected .xlsx or .csv/.txt")
    pts = []
    for r in rows[skip:]:
        try:
            x, y = float(r[columns[0]]), float(r[columns[1]])
        except (TypeError, ValueError, IndexError):
            continue
        if math.isfinite(x) and math.isfinite(y):
            pts.append((x, y))
    if len(pts) < 3:
        raise IngestError(f"{path.name}: fewer than 3 numeric (x, y) rows found in columns {columns}")
    return np.asarray(pts, dtype=float)


def shoelace(p: np.ndarray) -> float:
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def area_centroid(loop: np.ndarray) -> list[float]:
    """Polygon centroid from area moments, not the vertex mean."""
    x, y = loop[:, 0], loop[:, 1]
    x2, y2 = np.roll(x, -1), np.roll(y, -1)
    cross = x * y2 - x2 * y
    a = 0.5 * float(cross.sum())
    if abs(a) < 1e-18:
        return loop.mean(axis=0).tolist()
    cx = float((x + x2) @ cross / (6.0 * a))
    cy = float((y + y2) @ cross / (6.0 * a))
    return [cx, cy]


def _orient(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    return float((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))


def segment_intersections(loop: np.ndarray) -> int:
    """Count proper intersections between non-adjacent segments of a closed loop."""
    n = len(loop)
    if n < 4:
        return 0
    count = 0
    for i in range(n):
        a, b = loop[i], loop[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            c, d = loop[j], loop[(j + 1) % n]
            o1, o2 = _orient(a, b, c), _orient(a, b, d)
            o3, o4 = _orient(c, d, a), _orient(c, d, b)
            if o1 * o2 < 0 and o3 * o4 < 0:
                count += 1
    return count


def _landmark_chord(le: np.ndarray, te: np.ndarray) -> tuple[float, float, list, list]:
    a, b = np.asarray(le, dtype=float), np.asarray(te, dtype=float)
    chord = float(np.linalg.norm(b - a))
    stagger = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return chord, stagger, a.tolist(), b.tolist()


def analyse(pts: np.ndarray, *, scale_to_mm: float = 1.0, side1: np.ndarray | None = None) -> dict[str, Any]:
    p = pts * scale_to_mm
    closed = bool(np.allclose(p[0], p[-1], atol=1e-9))
    loop = p[:-1] if closed else p
    # chord: farthest pair (O(n^2) is fine for a few hundred points)
    d = np.linalg.norm(loop[:, None, :] - loop[None, :, :], axis=2)
    i, j = np.unravel_index(np.argmax(d), d.shape)
    a, b = loop[i], loop[j]
    if a[0] > b[0]:
        a, b = b, a
    chord = float(d[i, j])
    stagger = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    signed_area = shoelace(loop)
    seg = np.linalg.norm(np.diff(np.vstack([loop, loop[:1]]), axis=0), axis=1)
    lo, hi = loop.min(axis=0), loop.max(axis=0)
    # thickness distribution: perpendicular extent along the chord line, in 20 bins
    u = (b - a) / chord if chord else np.array([1.0, 0.0])
    n = np.array([-u[1], u[0]])
    s = (loop - a) @ u
    t = (loop - a) @ n
    bins = np.clip((s / max(chord, 1e-18) * 20).astype(int), 0, 19)
    thick = []
    for k in range(20):
        sel = t[bins == k]
        thick.append(float(sel.max() - sel.min()) if len(sel) >= 2 else 0.0)
    if side1 is not None and len(side1) >= 2:
        s1 = side1 * scale_to_mm
        lm_chord, lm_stagger, lm_a, lm_b = _landmark_chord(s1[0], s1[-1])
    else:
        lm_chord, lm_stagger, lm_a, lm_b = _landmark_chord(loop[0], loop[-1])
    centroid = area_centroid(loop)
    crosses = segment_intersections(loop)
    return {
        "points": int(len(loop)),
        "closed_input": closed,
        "bbox_min": lo.tolist(), "bbox_max": hi.tolist(), "size": (hi - lo).tolist(),
        "area": abs(signed_area), "orientation": "ccw" if signed_area > 0 else "cw",
        "perimeter": float(seg.sum()),
        "centroid": centroid,
        "area_centroid": centroid,
        "chord": chord, "chord_endpoints": [a.tolist(), b.tolist()], "stagger_deg": stagger,
        "landmark_chord": lm_chord, "landmark_stagger_deg": lm_stagger, "landmark_endpoints": [lm_a, lm_b],
        "max_thickness": max(thick) if thick else 0.0, "thickness_bins": thick,
        "segment_length": {"min": float(seg.min()), "max": float(seg.max()), "mean": float(seg.mean())},
        "self_intersections": crosses,
        "self_intersecting": crosses > 0,
        "self_intersections_checked": True,
    }


def plot(pts: np.ndarray, out: Path, size: int = 900) -> None:
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    scale = (size - 60) / max((hi - lo).max(), 1e-9)
    w, h = int((hi[0] - lo[0]) * scale) + 60, int((hi[1] - lo[1]) * scale) + 60
    img = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(img)
    xy = [(30 + (x - lo[0]) * scale, h - 30 - (y - lo[1]) * scale) for x, y in pts]
    d.line(xy + xy[:1], fill=0, width=2)
    for x, y in xy[:: max(1, len(xy) // 60)]:
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=120)
    img.save(out)


def ingest_profile(path: Path, out_dir: Path, *, units: str, sheet: str | None = None, columns: tuple[int, int] = (0, 1), skip: int = 0, sides: list[tuple[int, int]] | None = None, scale_to_mm: float | None = None) -> dict[str, Any]:
    if scale_to_mm is None and units not in UNIT_TO_MM:
        raise IngestError(f"units must be one of {sorted(UNIT_TO_MM)}")
    scale = float(scale_to_mm) if scale_to_mm is not None else UNIT_TO_MM[units]
    side_pairs = sides or [tuple(columns)]
    pts = read_loop(path, sheet=sheet, sides=side_pairs, skip=skip)
    side1 = read_table(path, sheet=sheet, columns=tuple(side_pairs[0]), skip=skip) if side_pairs else None
    a = analyse(pts, scale_to_mm=scale, side1=side1)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plot(pts * scale, out_dir / "profile.png")
    record = {
        "kind": "profile",
        "generated_at": utc_now(),
        "source": {"file": Path(path).name, "sha256": sha256_file(Path(path)), "declared_units": units, "sheet": sheet, "sides": [list(s) for s in (sides or [tuple(columns)])], "skip": skip, "scale_to_mm": scale},
        "measurements": a,
        "points_mm": (pts * scale).tolist(),
        "files": {"plot": "profile.png"},
    }
    (out_dir / "profile.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record

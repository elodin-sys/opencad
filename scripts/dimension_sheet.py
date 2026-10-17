#!/usr/bin/env python
"""Evaluator-prepared dimension sheet from a reference STEP (OpenCascade, no Zoo).

Produces the kind of sheet a drafter would hand a designer: envelope, mass properties, axis-aligned
planar faces by level, every cylindrical feature (holes and pins) with axis, diameter and depth, and
section summaries at requested stations. The CAD itself stays with the evaluator.

  python scripts/dimension_sheet.py truth/cases/x/truth/part.step out/dimension-sheet.md --sections z=3,x=10.5 --min-face-area 4
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from opencad.geomcheck import brep


def fmt(v: float, nd: int = 3) -> str:
    return f"{v:.{nd}f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def build(step: Path, sections: list[tuple[str, float]], min_face_area: float, max_faces: int, min_radius: float) -> str:
    shape = brep.read_step(step)
    a = brep.analyze_step(step)
    lines = [f"# Dimension sheet: {step.stem}", "",
             "All values in mm, measured on the reference geometry in its native frame (no re-alignment). Datum: the bounding-box minimum corner is the reference frame origin offset listed below.", "",
             "## Envelope and mass properties", "",
             f"- bbox min {[round(x, 3) for x in a['bbox_min']]}, max {[round(x, 3) for x in a['bbox_max']]}, size {[round(x, 3) for x in a['bbox_size']]}",
             f"- solids {a['solids']}, faces {a['faces']} ({a['planar_faces']} planar)",
             f"- volume {a['volume']:.2f} mm3, surface area {a['surface_area']:.2f} mm2, centre of mass {[round(x, 3) for x in a['center_of_mass']]}", ""]
    faces = brep.planar_faces(shape)
    lines += ["## Axis-aligned planar faces (by level; faces smaller than the threshold omitted)", "",
              "| normal | level | count | total area | per-face areas (largest first) | centroids (u,v in-plane) |", "|---|---|---|---|---|---|"]
    groups: dict[tuple, list] = defaultdict(list)
    for f in faces:
        n = f["normal"]
        ax = [i for i in range(3) if abs(abs(n[i]) - 1) < 1e-6]
        if not ax or f["area"] < min_face_area:
            continue
        i = ax[0]
        groups[("xyz"[i], "+" if n[i] > 0 else "-", round(f["point"][i], 3))].append(f)
    for (axis, sign, level), fs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][2], kv[0][1])):
        fs.sort(key=lambda f: -f["area"])
        u, v = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[axis]
        cents = "; ".join(f"({fmt(f['centroid'][u], 2)}, {fmt(f['centroid'][v], 2)})" for f in fs[:max_faces])
        areas = ", ".join(fmt(f["area"], 2) for f in fs[:max_faces]) + (" ..." if len(fs) > max_faces else "")
        lines.append(f"| {sign}{axis} | {axis} = {fmt(level)} | {len(fs)} | {fmt(sum(f['area'] for f in fs), 2)} | {areas} | {cents} |")
    incl = [f for f in faces if not any(abs(abs(f['normal'][i]) - 1) < 1e-6 for i in range(3)) and f["area"] >= min_face_area]
    if incl:
        lines += ["", "## Inclined planar faces", "", "| outward normal | point on plane | area | centroid |", "|---|---|---|---|"]
        for f in sorted(incl, key=lambda f: -f["area"])[:max_faces]:
            lines.append(f"| {[round(x, 4) for x in f['normal']]} | {[round(x, 3) for x in f['point']]} | {fmt(f['area'], 2)} | {[round(x, 3) for x in f['centroid']]} |")
    cyls = [c for c in brep.cylinders(shape) if c["radius"] >= min_radius]
    lines += ["", "## Cylindrical features (holes are concave, pins/bosses convex)", "",
              "| kind | diameter | axis direction | axis passes through (centre of extent) | extent along axis | length | full 360 |", "|---|---|---|---|---|---|---|"]
    for c in cyls:
        lines.append(f"| {c['kind']} | {fmt(c['diameter'])} | {[round(x, 4) for x in c['direction']]} | {[round(x, 3) for x in c['center']]} | {fmt(c['t_min'])} .. {fmt(c['t_max'])} (from axis point {[round(x, 3) for x in c['point']]}) | {fmt(c['length'])} | {'yes' if c['full'] else 'partial'} |")
    counts: dict[tuple, int] = defaultdict(int)
    for c in cyls:
        counts[(c["kind"], round(c["diameter"], 2))] += 1
    lines += ["", "Counts by kind and diameter: " + "; ".join(f"{k} Ø{d}: {n}" for (k, d), n in sorted(counts.items()))]
    if sections:
        lines += ["", "## Sections (solid material at the station)", "", "| plane | area | outer loops | holes | regions (centroid, bbox size) |", "|---|---|---|---|---|"]
        for axis, at in sections:
            s = brep.section(shape, axis, at)
            if not s.get("ok"):
                lines.append(f"| {axis} = {at} | section failed | | | |")
                continue
            u, v = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[axis]
            regs = "; ".join(f"({fmt(r['centroid'][u], 2)}, {fmt(r['centroid'][v], 2)}) {fmt(r['bbox_max'][u] - r['bbox_min'][u], 2)}x{fmt(r['bbox_max'][v] - r['bbox_min'][v], 2)}" for r in s["regions"][:max_faces])
            lines.append(f"| {axis} = {at} | {fmt(s['area'], 2)} | {s['loops']} | {s['holes']} | {regs} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("step", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--sections", default="", help="comma list like z=3,x=10.5")
    ap.add_argument("--min-face-area", type=float, default=1.0)
    ap.add_argument("--max-faces", type=int, default=12, help="per level / table row cap")
    ap.add_argument("--min-radius", type=float, default=0.0)
    a = ap.parse_args(argv)
    secs = [(s.split("=")[0].strip(), float(s.split("=")[1])) for s in a.sections.split(",") if s]
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(build(a.step, secs, a.min_face_area, a.max_faces, a.min_radius), encoding="utf-8")
    print(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

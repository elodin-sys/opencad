"""python -m opencad.reference ingest <mesh> --units mm [--axes x=+y,y=-x,z=+z] [--datum min] [--expect-size-mm 75 12 5] [--stations 12]
    [--station-axis z] --out DIR [--dry-run]
python -m opencad.reference profile <table> --units mm [--sheet NAME] [--columns 0 1] [--skip 1] --out DIR
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from opencad.reference.mesh import IngestError, ingest
from opencad.reference.profile import ingest_profile


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="opencad.reference", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ingest")
    p.add_argument("mesh")
    p.add_argument("--units", required=True, help="declared unit of the mesh coordinates: mm|cm|m|in|ft")
    p.add_argument("--axes", help="part axis <- signed source axis, e.g. x=+y,y=-x,z=+z (default identity)")
    p.add_argument("--datum", default="min", help="min|center|centroid|keep (default min: bbox min corner to origin)")
    p.add_argument("--expect-size-mm", nargs=3, type=float, metavar=("A", "B", "C"), help="anchor: expected bbox size in any order; aborts on a unit mistake")
    p.add_argument("--anchor-tolerance-rel", type=float, default=0.02)
    p.add_argument("--section", action="append", default=[], metavar="AXIS=AT", help="extra section plane, e.g. z=3.5 (repeatable)")
    p.add_argument("--treatment", default="reproduction", choices=["reproduction", "inspiration", "requirement"])
    p.add_argument("--stations", type=int, default=12, help="cross-sections with outlines and circle/ellipse/rounded-rectangle fits along one axis (0: none)")
    p.add_argument("--station-axis", choices=["x", "y", "z"], help="axis of the stations (default the longest)")
    p.add_argument("--out", required=True)
    p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("profile")
    p.add_argument("table")
    p.add_argument("--units", required=True)
    p.add_argument("--sheet")
    p.add_argument("--columns", nargs=2, type=int, default=[0, 1])
    p.add_argument("--side", action="append", nargs=2, type=int, metavar=("XCOL", "YCOL"), help="column pair for one side (repeat for PS then SS listed LE->TE); overrides --columns")
    p.add_argument("--skip", type=int, default=0)
    p.add_argument("--out", required=True)

    a = ap.parse_args(argv)
    try:
        if a.cmd == "ingest":
            planes = None
            if a.section:
                planes = []
                for s in a.section:
                    ax, at = s.split("=")
                    planes.append((ax.strip(), float(at)))
            rec = ingest(
                Path(a.mesh), Path(a.out), units=a.units, axes=a.axes, datum=a.datum, expect_size_mm=a.expect_size_mm,
                anchor_tolerance_rel=a.anchor_tolerance_rel, section_planes=planes, dry_run=a.dry_run, treatment=a.treatment,
                stations=a.stations, station_axis=a.station_axis,
            )
            m = rec["measurements"]
            st = m.get("stations") or {}
            print(json.dumps({"bbox_min": m["bbox_min"], "bbox_max": m["bbox_max"], "size": m["size"], "volume": m["volume"],
                              "center_of_mass": m["center_of_mass"], "watertight": m["watertight"], "components": m["components"],
                              "anchor": rec["anchor"], "files": rec["files"], "notes": rec["notes"],
                              **({"stations": [{"at": s["at"], "regions": s["loops"], "fits": [r["fit"]["best"] for r in s["regions"]],
                                                "hull": ((s.get("hull") or {}).get("fit") or {}).get("best")} for s in st.get("sections", [])],
                                  "station_axis": st.get("axis")} if st else {})}, indent=2))
        else:
            rec = ingest_profile(Path(a.table), Path(a.out), units=a.units, sheet=a.sheet, columns=tuple(a.columns), skip=a.skip, sides=[tuple(s) for s in a.side] if a.side else None)
            m = dict(rec["measurements"])
            m.pop("thickness_bins", None)
            print(json.dumps(m, indent=2))
    except IngestError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

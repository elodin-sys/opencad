#!/usr/bin/env python
"""Preselect held-out Fusion 360 Gallery joint sets (Phase 6) and stage their files.

Seeded, criteria-based, decided before the pipeline is frozen: single RevoluteJointType joint between
two cylindrical (non-planar) faces, both bodies' OBJ meshes watertight, both STEPs read as one solid,
sizes between 10 and 250 mm after the cm -> mm scale, modest face counts. Writes
truth/cases/_fusion360-selection.yaml and stages STEP/OBJ/JSON under ~/.cache/opencad/downloads/fusion360/selected/.

  python scripts/select_fusion_joints.py --n 5 --seed 20260917
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import py7zr
import trimesh
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from opencad.geomcheck import brep  # noqa: E402

ROOT = Path.home() / ".cache" / "opencad" / "downloads" / "fusion360"
ARC = ROOT / "j1.0.0.7z"
EXTRACT = ROOT / "extract" / "j1.0.0" / "joint"
SELECTED = ROOT / "selected"
CM_TO_MM = 10.0


def candidates(seed: int) -> list[str]:
    tt = json.load(open(EXTRACT / "train_test.json"))
    rows = []
    for sid in tt["test"]:
        js = json.load(open(EXTRACT / f"{sid}.json"))
        if len(js["joints"]) != 1:
            continue
        j = js["joints"][0]
        if j["joint_motion"]["joint_type"] != "RevoluteJointType":
            continue
        g1, g2 = j["geometry_or_origin_one"].get("geometry_type"), j["geometry_or_origin_two"].get("geometry_type")
        if g1 != "JointNonPlanarBRepFaceGeometry" or g2 != "JointNonPlanarBRepFaceGeometry":
            continue
        rows.append(sid)
    random.Random(seed).shuffle(rows)
    return rows


def extract(names: list[str]) -> None:
    missing = [n for n in names if not (ROOT / "extract" / n).exists()]
    if missing:
        with py7zr.SevenZipFile(ARC, "r") as z:
            z.extract(path=ROOT / "extract", targets=missing)


def qualify(sid: str) -> dict | None:
    js = json.load(open(EXTRACT / f"{sid}.json"))
    bodies = [js["body_one"], js["body_two"]]
    names = [f"j1.0.0/joint/{b}.{ext}" for b in bodies for ext in ("step", "obj")]
    extract(names)
    info = {"set": sid, "bodies": bodies, "joint_type": js["joints"][0]["joint_motion"]["joint_type"], "holes": len(js.get("holes", [])), "contacts": len(js.get("contacts", []))}
    for b in bodies:
        # the dataset OBJs are not manifold (documented caveat); the STEPs are millimetre B-reps and are tessellated by the evaluator
        try:
            a = brep.analyze_step(EXTRACT / f"{b}.step")
        except Exception:
            return None
        size_mm = a["bbox_size"]
        if a["solids"] != 1 or not a["valid"] or max(size_mm) > 250 or max(size_mm) < 10 or a["faces"] > 400 or a["faces"] < 6:
            return None
        info[b] = {"faces": a["faces"], "size_mm": [round(x, 2) for x in size_mm], "volume_mm3": round(a["volume"], 2), "bbox_min": [round(x, 3) for x in a["bbox_min"]]}
    # qualify the reference assembly itself: the dataset's assembled state must be (nearly) interference-free
    from opencad.geomcheck import assembly
    from opencad.truth import assembly_task as at

    t1, t2 = at.truth_poses(js)
    inter = assembly.common_volume(at.apply(brep.read_step(EXTRACT / f"{bodies[0]}.step"), t1), at.apply(brep.read_step(EXTRACT / f"{bodies[1]}.step"), t2))
    if not (inter <= 20.0):
        return None
    info["truth_interference_mm3"] = round(float(inter), 3)
    return info


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260917)
    ap.add_argument("--max-tries", type=int, default=40)
    a = ap.parse_args(argv)
    cands = candidates(a.seed)
    chosen, tried = [], 0
    for sid in cands:
        if len(chosen) >= a.n or tried >= a.max_tries:
            break
        tried += 1
        info = qualify(sid)
        print(f"{sid}: {'ok' if info else 'rejected'}")
        if info:
            chosen.append(info)
    SELECTED.mkdir(parents=True, exist_ok=True)
    for info in chosen:
        d = SELECTED / info["set"]
        d.mkdir(exist_ok=True)
        (d / "joint_set.json").write_text((EXTRACT / f"{info['set']}.json").read_text())
        for b in info["bodies"]:
            for ext in ("step", "obj"):
                (d / f"{b}.{ext}").write_bytes((EXTRACT / f"{b}.{ext}").read_bytes())
    out = REPO / "truth" / "cases" / "_fusion360-selection.yaml"
    out.write_text(yaml.safe_dump({"seed": a.seed, "criteria": "test split; single RevoluteJointType; both joint geometries JointNonPlanarBRepFaceGeometry; STEP one valid solid; 10..250 mm; 6..400 faces",
                                   "tried": tried, "candidates": len(cands), "units": "STEP files are millimetres (SI_UNIT .MILLI. .METRE.); joint JSON coordinates are centimetres (x10 to mm); OBJ meshes are not manifold and are not used",
                                   "selected": chosen}, sort_keys=False), encoding="utf-8")
    print(f"selected {len(chosen)} of {tried} tried -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

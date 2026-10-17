#!/usr/bin/env python
"""Contract deltas for the rpi5-enclosure change requests, derived from the passing design's own STEP.

An ECR revises the contract before Codex edits the KCL (`python -m opencad ecr ... --contract-delta`), so the
revised acceptance values must be known up front. For ECR-1 (+10 mm headroom) and ECR-2 (3 mm shells) the
requested change is fully determined by the current geometry, so the evaluator constructs the post-change
reference solid in OpenCascade (wall band raised / shell grown, pilots moved, lid translated) and reads the
new volume, centre of mass, section areas and face levels from it. ECR-3 (lid screws moved to the long sides)
fixes the boss layout the Zoo attempt applied (truth PASS 36/36): corner posts removed above the floor plate, four
side bosses cornerPostWidth wide on the long walls, lid over the walls and flanges; its section areas, face areas
and centres and edit deltas are derived from the contract parameters, the fastener axes are pinned by region-filtered
cylinder counts and void probes, and the mass targets are dropped.

  python scripts/rpi5_ecr_deltas.py            # writes truth/cases/rpi5-enclosure-ecr{1,2,3}/inputs/contract-delta.yaml
  python scripts/rpi5_ecr_deltas.py --check    # also re-scores the constructed references against the revised contracts
"""

from __future__ import annotations

import argparse
import copy
import math
import sys
from pathlib import Path

import yaml
from OCP.BRep import BRep_Builder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from OCP.TopoDS import TopoDS_Compound

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from opencad.geomcheck import brep, multibody  # noqa: E402
from opencad.truth.mutants import write_step  # noqa: E402

DESIGN = "rpi5-enclosure"
CONTRACT = REPO / "designs" / DESIGN / "contract.yaml"
STEP = REPO / "results" / "zoo" / DESIGN / "handoff" / f"{DESIGN}.step"
CASES = REPO / "truth" / "cases"
SIDE_X = (50.0, 75.0)


def box(lo, hi):
    return BRepPrimAPI_MakeBox(gp_Pnt(*lo), gp_Pnt(*hi)).Shape()


def cyl(x, y, z0, z1, r):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1)), r, z1 - z0).Shape()


def moved(shape, dz):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(0, 0, dz))
    return BRepBuilderAPI_Transform(shape, t, True).Shape()


def fuse(a, b):
    op = BRepAlgoAPI_Fuse(a, b)
    op.Build()
    return op.Shape()


def cut(a, b):
    op = BRepAlgoAPI_Cut(a, b)
    op.Build()
    return op.Shape()


def common(a, b):
    op = BRepAlgoAPI_Common(a, b)
    op.Build()
    return op.Shape()


def unify(shape):
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain

    u = ShapeUpgrade_UnifySameDomain(shape, True, True, True)
    u.Build()
    return u.Shape()


def compound(*shapes):
    c = TopoDS_Compound()
    bb = BRep_Builder()
    bb.MakeCompound(c)
    for s in shapes:
        bb.Add(c, s)
    return c


def by_name(items, name):
    return next(i for i in items if i["name"] == name)


def param(c, name):
    return float(by_name(c["parameters"], name)["value"])


class Design:
    """The passing design read back from its contract and STEP."""

    def __init__(self):
        self.c = yaml.safe_load(CONTRACT.read_text())
        a = self.c["acceptance"]
        shape = brep.read_step(STEP)
        sel = {s["name"]: multibody.select_solid(shape, s["contains_point"]) for s in a["solids"]}
        self.base, self.lid = sel["base"], sel["lid"]
        self.headroom = param(self.c, "headroom")
        self.wall = param(self.c, "wallThickness")
        self.rim = by_name(a["faces"], "base_rim")["at"]
        self.lid_under = by_name(a["faces"], "lid_underside")["at"]
        self.lid_top = by_name(a["faces"], "lid_exterior")["at"]
        self.floor_bottom = by_name(a["faces"], "floor_exterior")["at"]
        self.pilot_r = param(self.c, "pilotDiameter") / 2
        self.pilot_depth = param(self.c, "pilotDepth")
        self.corner_axes = [tuple(x["point"][:2]) for x in a["cylinders"] if x["name"].startswith("corner_") and x["name"].endswith("_pilot")]
        self.plugs = {h["name"]: (h["min"], h["max"]) for h in a["hardware"] if h["name"].endswith("_plug") or h["name"] == "sd_card_slot"}

    def measure(self, base, lid, tmp: Path):
        # boolean fuses split coplanar faces at the seams; a KCL-built part has whole faces, so unify before measuring
        comp = compound(unify(base), unify(lid))
        path = write_step(comp, tmp)
        return brep.analyze_step(path), comp


def shift_z_items(acc: dict, dz: float, *, faces_pred, probes_pred, sections_pred) -> dict:
    """Delta entries that move acceptance items up by dz (faces by name, probes by name, sections by id)."""
    d: dict = {"faces": [], "probes": [], "sections": []}
    for f in acc["faces"]:
        if faces_pred(f):
            d["faces"].append({"name": f["name"], "at": round(f["at"] + dz, 4)})
    for p in acc["probes"]:
        if probes_pred(p):
            d["probes"].append({"name": p["name"], "points": [[x, y, round(z + dz, 4)] for x, y, z in p["points"]]})
    for s in acc["sections"]:
        if sections_pred(s):
            d["sections"].append({"id": s["id"], "at": round(s["at"] + dz, 4)})
    return d


def remeasure_faces(comp, faces: list[dict], moved_at: dict[str, float]) -> list[dict]:
    """Delta entries for named faces whose level moved or whose area changed by more than 0.5 % on the reference solid."""
    planar = brep.planar_faces(comp)
    out = []
    for f in faces:
        at = moved_at.get(f["name"], f["at"])
        hits = brep.find_face(planar, f["plane"], at, f["normal"], f.get("tolerance") or 0.05)
        if f.get("center") and hits:
            u, v = [i for i in range(3) if i != "xyz".index(f["plane"])]
            hits = [min(hits, key=lambda h: (h["centroid"][u] - f["center"][0]) ** 2 + (h["centroid"][v] - f["center"][1]) ** 2)]
        area = sum(h["area"] for h in hits) if hits else None
        entry: dict = {"name": f["name"]}
        if f["name"] in moved_at:
            entry["at"] = at
        if area is not None and f.get("area") and abs(area - f["area"]) > 0.005 * f["area"]:
            entry["area"] = round(area, 3)
        if f.get("center") and len(hits) == 1:
            u, v = [i for i in range(3) if i != "xyz".index(f["plane"])]
            cu, cv = hits[0]["centroid"][u], hits[0]["centroid"][v]
            if abs(cu - f["center"][0]) > 0.02 or abs(cv - f["center"][1]) > 0.02:
                entry["center"] = [round(cu, 4), round(cv, 4)]
        if len(entry) > 1:
            out.append(entry)
    return out


def section_expect(comp, plane: str, at: float, tol_rel: float) -> dict:
    r = brep.section(comp, plane, at)
    return {"area": round(r["area"], 3), "area_tolerance_rel": tol_rel, "loops": r["loops"], "holes": r["holes"]}


def ecr1(design: Design, out_dir: Path) -> tuple[dict, object]:
    """+10 mm headroom: wall band raised, corner pilots follow the rim, lid translated."""
    c, a = design.c, design.c["acceptance"]
    dz = 10.0
    lo, hi = brep.bbox(design.base)
    # a 10 mm slab of the wall ring taken below the corner pilots and above every notch sill, placed on the old rim
    z0 = design.rim - design.pilot_depth - 1.0 - dz
    band = common(design.base, box([lo[0] - 1, lo[1] - 1, z0], [hi[0] + 1, hi[1] + 1, z0 + dz]))
    new_base = fuse(design.base, moved(band, design.rim - z0))
    for x, y in design.corner_axes:
        new_base = fuse(new_base, cyl(x, y, design.rim - design.pilot_depth - 0.01, design.rim + 0.01, design.pilot_r))  # fill the old pilot
        new_base = cut(new_base, cyl(x, y, design.rim + dz - design.pilot_depth, design.rim + dz + 1.0, design.pilot_r))  # cut the new one
    new_lid = moved(design.lid, dz)
    an, comp = design.measure(new_base, new_lid, out_dir / "ecr1-reference.step")
    rim = design.rim
    delta = {
        "parameters": [{"name": "headroom", "value": design.headroom + dz,
                        "edit_test": {**by_name(c["parameters"], "headroom")["edit_test"], "infeasible_deltas": [-(design.headroom + dz + 1.0)]}}],
        "envelope": {**c["envelope"], "max": [c["envelope"]["max"][0], c["envelope"]["max"][1], round(c["envelope"]["max"][2] + dz, 4)]},
        "acceptance": {
            "volume": {**a["volume"], "expected": round(an["volume"], 3), "provenance": "measured (reference model)",
                       "note": "ECR-1 reference: the passing STEP with its wall band raised 10 mm, corner pilots following the rim and the lid translated (scripts/rpi5_ecr_deltas.py)."},
            "center_of_mass": {**a["center_of_mass"], "expected": [round(v, 4) for v in an["center_of_mass"]], "provenance": "measured (reference model)",
                               "note": "ECR-1 reference geometry centroid (scripts/rpi5_ecr_deltas.py)."},
            "blockout": {"volume_min": a["blockout"]["volume_min"], "volume_max": a["blockout"]["volume_max"] + 20000},
            "solids": [{**s, "contains_point": [s["contains_point"][0], s["contains_point"][1], round(s["contains_point"][2] + dz, 4)]} if s["name"] == "lid"
                       else {**s, "volume": None} for s in a["solids"]],
            "hardware": [{**h, "max": [h["max"][0], h["max"][1], round(h["max"][2] + dz, 4)]} if h["name"] == "top_envelope" else h for h in a["hardware"]],
            "dimensions": [{"name": d["name"], "expected": round(d["expected"] + dz, 4)} for d in a["dimensions"] if d["name"] == "overall_z"],
        },
    }
    moves = shift_z_items(a, dz, faces_pred=lambda f: f["at"] >= rim - design.pilot_depth - 0.5 and f["plane"] == "z",
                          probes_pred=lambda p: p["name"] in ("corner_pilots_void", "lid_holes_void"),
                          sections_pred=lambda s: s["plane"] == "z" and s["at"] > rim - design.pilot_depth - 0.5)
    delta["acceptance"].update(moves)
    # faces whose area changes (the open-top notch jambs grow with the wall band) and the surface area, read from the reference
    moved_levels = {f["name"]: f["at"] for f in moves["faces"]}
    delta["acceptance"]["faces"] = remeasure_faces(comp, a["faces"], moved_levels)
    if a.get("surface_area"):
        delta["acceptance"]["surface_area"] = {**a["surface_area"], "expected": round(an["surface_area"], 3), "provenance": "measured (reference model)",
                                               "note": "ECR-1 reference geometry surface area (scripts/rpi5_ecr_deltas.py)."}
    # the lid selector probe moves with the lid
    for p in a["probes"]:
        if p["name"] == "required_body_points":
            delta["acceptance"]["probes"].append({"name": p["name"], "points": [[x, y, round(z + dz, 4)] if z > rim else [x, y, z] for x, y, z in p["points"]]})
    # section expectations re-measured on the reference (areas do not change for a pure translation, but re-measure anyway)
    for s in delta["acceptance"]["sections"]:
        src = next(x for x in a["sections"] if x["id"] == s["id"])
        s["expect"] = section_expect(comp, src["plane"], s["at"], src["expect"].get("area_tolerance_rel", 0.01))
    # solid volumes for base/lid
    for s in delta["acceptance"]["solids"]:
        sol = multibody.select_solid(comp, s["contains_point"])
        s["volume"] = {"expected": round(brep.volume_props(sol)["volume"], 3), "tolerance_rel": 0.005, "provenance": "measured (reference model)", "note": "ECR-1 reference geometry"}
    # feature verify probes above the old rim (the lid selector) move with the lid
    delta["features"] = shift_feature_probes(c["features"], lambda pt: pt[2] > rim - design.pilot_depth - 0.5, dz)
    return delta, comp


def shift_feature_probes(features_: list[dict], pred, dz: float) -> list[dict]:
    """Feature deltas re-stating `verify` with every void/solid probe point that satisfies `pred` moved by dz."""
    out = []
    for f in features_:
        if not any(v.get("points") and any(pred(pt) for pt in v["points"]) for v in f["verify"]):
            continue
        verify = copy.deepcopy(f["verify"])
        for v in verify:
            if v.get("points"):
                v["points"] = [[pt[0], pt[1], round(pt[2] + dz, 4)] if pred(pt) else pt for pt in v["points"]]
        out.append({"id": f["id"], "verify": verify})
    return out


def ecr2(design: Design, out_dir: Path) -> tuple[dict, object]:
    """3 mm shells: walls grow outward, floor grows downward, openings extended through the thicker wall, lid unchanged (already 4 mm)."""
    c, a = design.c, design.c["acceptance"]
    grow = 3.0 - design.wall
    if grow <= 0:
        raise SystemExit("walls are already >= 3 mm; ECR-2 needs a different design")
    lo, hi = brep.bbox(design.base)
    inner_lo, inner_hi = [-0.5, -0.5], [85.5, 56.5]
    w = design.wall
    # grow each wall outward by copying its own slab (notches, sills and posts included) `grow` further out; the floor likewise downward
    slabs = [
        (box([lo[0] - 1, inner_lo[1] - w, design.floor_bottom], [hi[0] + 1, inner_lo[1], design.rim + 1]), (0, -grow, 0)),   # south wall (y-)
        (box([lo[0] - 1, inner_hi[1], design.floor_bottom], [hi[0] + 1, inner_hi[1] + w, design.rim + 1]), (0, grow, 0)),    # north wall (y+)
        (box([inner_lo[0] - w, lo[1] - 1, design.floor_bottom], [inner_lo[0], hi[1] + 1, design.rim + 1]), (-grow, 0, 0)),   # west wall (x-)
        (box([inner_hi[0], lo[1] - 1, design.floor_bottom], [inner_hi[0] + w, hi[1] + 1, design.rim + 1]), (grow, 0, 0)),    # east wall (x+)
        (box([lo[0] - 1, lo[1] - 1, design.floor_bottom - 0.01], [hi[0] + 1, hi[1] + 1, design.floor_bottom + w]), (0, 0, -grow)),  # floor
    ]
    new_base = design.base
    for region, (dx, dy, dz) in slabs:
        t = gp_Trsf()
        t.SetTranslation(gp_Vec(dx, dy, dz))
        piece = BRepBuilderAPI_Transform(common(design.base, region), t, True).Shape()
        new_base = fuse(new_base, piece)
        if dz == 0:  # the moved wall's outer face runs down to the new floor bottom: extend its lowest layer by `grow`
            skirt = common(piece, box([lo[0] - 2, lo[1] - 2, design.floor_bottom - 0.01], [hi[0] + 2, hi[1] + 2, design.floor_bottom + grow]))
            t2 = gp_Trsf()
            t2.SetTranslation(gp_Vec(0, 0, -grow))
            new_base = fuse(new_base, BRepBuilderAPI_Transform(skirt, t2, True).Shape())
    for x, y in design.corner_axes:  # the copied wall slabs graze the corner-post pilots; the pilots themselves do not change
        new_base = cut(new_base, cyl(x, y, design.rim - design.pilot_depth, design.rim + 1.0, design.pilot_r))
    an, comp = design.measure(new_base, design.lid, out_dir / "ecr2-reference.step")
    new_floor = round(design.floor_bottom - grow, 4)
    blo, bhi = brep.bbox(comp)
    faces_delta = remeasure_faces(comp, a["faces"], {"floor_exterior": new_floor})
    # edit-test volume deltas scale with the wall ring: headroom adds the notched ring section (measured above every sill,
    # below the pilots); standoff height adds the full ring (floor footprint minus the interior) plus the four boss disks
    ring_notched = brep.section(comp, "z", 10.0)["area"]
    ring_full = brep.section(comp, "z", design.floor_bottom + 1.0)["area"] - (85.0 + 1.0) * (56.0 + 1.0)
    boss_r = param(c, "standoffDiameter") / 2
    params_delta = [{"name": "wallThickness", "value": 3.0}]
    for p in c["parameters"]:
        et = p.get("edit_test")
        if not et:
            continue
        if p["name"] == "headroom":
            params_delta.append({"name": "headroom", "edit_test": {**et, "expect": {**et["expect"], "volume_delta": round(ring_notched * et["delta"], 3)}}})
        elif p["name"] == "standoffHeight":
            params_delta.append({"name": "standoffHeight", "edit_test": {**et, "expect": {**et["expect"], "volume_delta": round((ring_full + 4 * math.pi * boss_r ** 2) * et["delta"], 3)}}})
    delta = {
        "parameters": params_delta,
        "envelope": {"min": [round(v, 4) for v in blo], "max": [round(v, 4) for v in bhi], "tolerance": c["envelope"]["tolerance"]},
        "acceptance": {
            "volume": {**a["volume"], "expected": round(an["volume"], 3), "provenance": "measured (reference model)",
                       "note": "ECR-2 reference: the passing STEP with its walls grown outward and floor grown downward to 3 mm, openings extended (scripts/rpi5_ecr_deltas.py)."},
            "center_of_mass": {**a["center_of_mass"], "expected": [round(v, 4) for v in an["center_of_mass"]], "provenance": "measured (reference model)",
                               "note": "ECR-2 reference geometry centroid (scripts/rpi5_ecr_deltas.py)."},
            "blockout": {"volume_min": a["blockout"]["volume_min"], "volume_max": a["blockout"]["volume_max"] + 20000},
            "thickness": [{**t, "min": 3.0} for t in a["thickness"]],
            "faces": faces_delta,
            **({"surface_area": {**a["surface_area"], "expected": round(an["surface_area"], 3), "provenance": "measured (reference model)",
                                 "note": "ECR-2 reference geometry surface area (scripts/rpi5_ecr_deltas.py)."}} if a.get("surface_area") else {}),
            "dimensions": [{"name": "overall_x", "expected": round(bhi[0] - blo[0], 4)},
                           {"name": "overall_y", "expected": round(bhi[1] - blo[1], 4)},
                           {"name": "overall_z", "expected": round(bhi[2] - blo[2], 4)},
                           {"name": "floor_thickness", "expected": 3.0}],
            "sections": [],
            "solids": [],
        },
    }
    for s in a["sections"]:
        at = s["at"]
        if s["plane"] == "z" and s["at"] < design.floor_bottom + 1e-6 + grow and s["id"] == "floor_section":
            at = round(new_floor + (s["at"] - design.floor_bottom), 4)
        delta["acceptance"]["sections"].append({"id": s["id"], "at": at, "expect": section_expect(comp, s["plane"], at, s["expect"].get("area_tolerance_rel", 0.01))})
    for s in a["solids"]:
        sol = multibody.select_solid(comp, s["contains_point"])
        delta["acceptance"]["solids"].append({**s, "volume": {"expected": round(brep.volume_props(sol)["volume"], 3), "tolerance_rel": 0.005, "provenance": "measured (reference model)", "note": "ECR-2 reference geometry"}})
    return delta, comp


def ecr3(design: Design) -> dict:
    """Lid screws to the long sides, as the Zoo attempt applied it (truth PASS 36/36, 2026-09-18).

    Geometry the revised contract describes: the square corner posts are removed above the floor top (their feet stay
    in the floor plate, so footprint O, the envelope and overall_x/y are unchanged); four side bosses cornerPostWidth
    wide in x, centred on x = 50 and x = 75, fill the band between the wall exterior and the old post line on both long
    sides over the full base height, each with a Ø2.5 x pilotDepth blind pilot from the rim on the axis mid-depth of the
    wall+boss band (y = -4.5 / 60.5); the lid covers the wall footprint plus the four flanges (no corner lugs) with four
    Ø3.2 through holes coaxial with the pilots. Every area, centre and edit delta below follows from the parameters.
    The pilot y is left free inside the wall band by the region counts; the void probes tolerate +-1.25 mm around it.
    """
    c, a = design.c, design.c["acceptance"]
    lo, hi = brep.bbox(design.base)
    w, post, ec = design.wall, param(c, "cornerPostWidth"), param(c, "edgeClearance")
    length, width = param(c, "boardLength"), param(c, "boardWidth")
    rb, rp, rl = param(c, "standoffDiameter") / 2, design.pilot_r, 3.2 / 2
    cav_x, cav_y = length + 2 * ec, width + 2 * ec
    wall_x, wall_y = cav_x + 2 * w, cav_y + 2 * w
    wall_ring = wall_x * wall_y - cav_x * cav_y                                  # straight walls only, 709.44
    ao = by_name(a["faces"], "floor_exterior")["area"]                          # footprint O with the four corner feet, 5844.4
    boss = post * (post - w)                                                    # one side boss outside the wall, 8 x 5.6
    ring = wall_ring + 4 * boss                                                 # wall section above the floor, bosses included, 888.64
    widths = {d["name"]: d["expected"] for d in a["dimensions"] if d["name"].endswith("_width")}
    notches, sd = sum(widths.values()), widths["sd_card_slot_width"]           # 96 and 12
    xc, yc, xs = length / 2, width / 2, sum(SIDE_X) / len(SIDE_X)               # footprint centre and the side-boss centre line
    r6 = lambda v: round(v, 6)  # noqa: E731
    floor_area = ao + 4 * boss
    lid_area = r6(wall_x * wall_y + 4 * boss - 4 * math.pi * rl**2)
    lid_cx = r6((wall_x * wall_y * xc + (4 * boss - 4 * math.pi * rl**2) * xs) / lid_area)
    y_front, y_back = -(ec + post / 2), width + ec + post / 2                   # pilot / lid-hole axes: mid-depth of the wall+boss band
    y_front_boss, y_back_boss = -(ec + post) + 1.5, width + ec + post - 1.5     # boss material between the pilot and the outer face
    z_pilot = design.rim - design.pilot_depth / 2
    z_lid = (design.lid_under + design.lid_top) / 2
    axes = [[x, y] for y in (y_front, y_back) for x in SIDE_X]
    mid = f"axes ({SIDE_X[0]:g}, {y_front:g}), ({SIDE_X[1]:g}, {y_front:g}), ({SIDE_X[0]:g}, {y_back:g}), ({SIDE_X[1]:g}, {y_back:g})"
    symbols = f"Ao = {ao:g} (footprint O with the corner feet), Ab = {post:g}*{post - w:g} = {boss:g} (one side boss outside the wall), Aw = {wall_x:g}*{wall_y:g}-{cav_x:g}*{cav_y:g} = {wall_ring:g} (straight-wall ring)"
    sections = {
        "floor_section": (r6(floor_area), f"ECR-3: through the full floor plate, below the pilot ends; footprint O with its corner feet plus the four {post:g} x {post - w:g} side bosses: Ao+4*Ab = {floor_area:.6g}. Symbols: {symbols}."),
        "standoff_section": (r6(ring - sd * w + 4 * math.pi * (rb**2 - rp**2)), f"ECR-3: one shell region (straight walls plus four side bosses; corner posts gone above the floor) opened by the SD notch, plus four annular standoffs: Aw+4*Ab-12*w+4*pi*(rb^2-rp^2) = {ring - sd * w + 4 * math.pi * (rb**2 - rp**2):.6f}."),
        "pcb_level_section": (r6(ring - sd * w), f"ECR-3: one shell region with the SD notch; the PCB rectangle is void: Aw+4*Ab-12*w = {ring - sd * w:.6g}."),
        "all_ports_section": (r6(ring - notches * w), f"ECR-3: seven open notches split the wall cross-section into seven regions: Aw+4*Ab-96*w = {ring - notches * w:.6g}; the side-boss pilots start higher."),
    }
    counts = [{"name": "lid_clearance_count", "diameter": 3.2, "radius_tolerance": 0.15, "expected": 4, "description": "ECR-3: four Ø3.2 lid holes on the long sides; the corner holes are gone"},
              {"name": "pilot_count", "description": "ECR-3: four board standoff pilots plus four side-boss pilots; the corner-post pilots are gone."}]
    stations = []
    for x in SIDE_X:
        for side, (y0, y1) in (("ym", (lo[1] - 10.0, -0.5)), ("yp", (56.5, hi[1] + 10.0))):
            region = [[x - 0.5, y0, lo[2]], [x + 0.5, y1, hi[2] + 20.0]]
            stations.append({"name": f"side_screw_{side}_x{int(x)}", "diameter": 3.2, "radius_tolerance": 0.15, "kind": "hole", "direction": [0, 0, 1], "region": region, "expected_min": 1,
                             "description": f"ECR-3: lid clearance hole at x = {x} in the {'y < 0' if side == 'ym' else 'y > 56'} wall"})
            stations.append({"name": f"side_pilot_{side}_x{int(x)}", "diameter": 2.5, "radius_tolerance": 0.1, "kind": "hole", "direction": [0, 0, 1], "region": region, "expected_min": 1,
                             "description": f"ECR-3: Ø2.5 boss pilot under the x = {x} screw"})
    params: list[dict] = [
        {"name": "sideScrewXNear", "value": SIDE_X[0], "unit": "mm", "provenance": "stated", "tolerance": 0.01,
         "source": f'designs/{DESIGN}/ecr/ecr3/request.md: "two per side at x = 50 and x = 75 (board frame)"',
         "description": f"ECR-3: x of the near lid screw on each long side; axis ({SIDE_X[0]:g}, {y_front:g}) and ({SIDE_X[0]:g}, {y_back:g}), mid-depth of the {post:g} mm wall+boss band."},
        {"name": "sideScrewXFar", "value": SIDE_X[1], "unit": "mm", "provenance": "stated", "tolerance": 0.01,
         "source": f'designs/{DESIGN}/ecr/ecr3/request.md: "two per side at x = 50 and x = 75 (board frame)"',
         "description": f"ECR-3: x of the far lid screw on each long side; axis ({SIDE_X[1]:g}, {y_front:g}) and ({SIDE_X[1]:g}, {y_back:g})."},
        {"name": "sideLidHoleDiameter", "value": 3.2, "unit": "mm", "provenance": "stated", "tolerance": 0.01,
         "source": f'designs/{DESIGN}/ecr/ecr3/request.md: "a Ø3.2 clearance hole through the lid flange"',
         "description": "ECR-3: the four lid clearance holes on the long sides, coaxial with the side-boss pilots (replaces the corner holes and lidHoleDiameter)."},
        {"name": "lidHoleDiameter", "_remove": True},
        {"name": "cornerPostWidth", "description": f"ECR-3: the {post:g} mm square corner feet remain in the floor plate only (the posts above the floor top are removed); the same value is the x-width of the four side bosses and lid flanges and their outer offset from the cavity (y = {-(ec + post):g} and {width + ec + post:g})."},
        {"name": "pilotDiameter", "description": "Diameter of all four standoff pilots and, after ECR-3, of the four side-boss pilots (blind, pilotDepth from the rim)."},
    ]
    for p in c["parameters"]:
        et = p.get("edit_test")
        if p["name"] == "headroom" and et:
            params.append({"name": "headroom", "edit_test": {**et, "expect": {**et["expect"], "volume_delta": round((ring - notches * w) * et["delta"], 6)}}})
        elif p["name"] == "standoffHeight" and et:
            params.append({"name": "standoffHeight", "edit_test": {**et, "expect": {**et["expect"], "volume_delta": round((ring + 4 * math.pi * rb**2) * et["delta"], 6)}}})
    corner_ref = lambda v: v.get("section") == "rim_pilots_section" or str(v.get("cylinder") or v.get("face") or v.get("dimension") or "").startswith("corner_")  # noqa: E731
    delta = {
        "parameters": params,
        "acceptance": {
            "volume": None, "center_of_mass": None, "surface_area": None,
            "cylinders": [{"name": x["name"], "_remove": True} for x in a["cylinders"] if x["name"].startswith("corner_")],
            "faces": [{"name": f["name"], "_remove": True} for f in a["faces"] if f["name"].startswith("corner_")]
                     + [{"name": "floor_exterior", "area": r6(floor_area), "center": [r6((ao * xc + 4 * boss * xs) / floor_area), yc]},
                        {"name": "base_rim", "area": r6(ring - notches * w - 4 * math.pi * rp**2)},
                        {"name": "lid_underside", "area": lid_area, "center": [lid_cx, yc]},
                        {"name": "lid_exterior", "area": lid_area, "center": [lid_cx, yc]}],
            "dimensions": [{"name": d["name"], "_remove": True} for d in a["dimensions"] if d["name"].startswith("corner_")],
            "sections": [{"id": "rim_pilots_section", "_remove": True}]
                        + [{"id": s["id"], "expect": {**s["expect"], "area": sections[s["id"]][0]}, "description": sections[s["id"]][1]} for s in a["sections"] if s["id"] in sections]
                        + [{"id": "lid_section", "expect": {"area": lid_area, "area_tolerance_rel": 0.01, "loops": 1, "holes": 4},
                            "description": f"ECR-3: one lid region (wall footprint plus four side flanges) with four Ø3.2 through holes: {wall_x:g}*{wall_y:g}+4*Ab-4*pi*rl^2 = {lid_area:.6f}."}],
            "probes": [{"name": "corner_pilots_void", "_remove": True},
                       {"name": "side_pilots_void", "state": "void", "points": [[x, y, z_pilot] for x, y in axes],
                        "description": f"ECR-3: mid-depth points of the four side-boss pilots, {mid}; a pilot anywhere within {rp:g} mm of the nominal axis covers them."},
                       {"name": "lid_holes_void", "points": [[x, y, z_lid] for x, y in axes],
                        "description": f"ECR-3: mid-thickness points of the four Ø3.2 lid clearance holes on the side flanges, {mid}."},
                       {"name": "side_boss_material", "state": "solid", "points": [[x, y, 10.0] for y in (y_front_boss, y_back_boss) for x in SIDE_X],
                        "description": f"ECR-3: material of the four side bosses at mid-height, 1.5 mm inside their outer faces (y = {y_front_boss:g} / {y_back_boss:g}), outside the pilots."},
                       {"name": "shell_material", "points": [[xs, -(ec + w / 2), 10], [xc, width + ec + w / 2, 10]],
                        "description": f"Uninterrupted front/back walls at mid-thickness; the front probe sits at x = {xs:g}, between the two side bosses and off both screw axes."}],
            "cylinder_counts": counts + stations,
            "solids": [{**s, "volume": None, "description": "Exact source-contained point; connected shell, floor plate with its corner feet, standoffs and four side bosses."} if s["name"] == "base"
                       else {**s, "volume": None, "description": "Exact source-contained point; separate flat cover over the walls and the four side flanges with four Ø3.2 through holes."} for s in a["solids"]],
        },
        "interfaces": [{"name": i["name"], "_remove": True} for i in c["interfaces"] if i["name"].startswith("lid_fastener_")]
                      + [{"name": "side_fasteners", "must_not_change": False, "checks": [s["name"] for s in stations],
                          "description": "ECR-3: four lid screws on the long sides at x = 50 and x = 75, Ø3.2 through the lid into Ø2.5 x >= 5 boss pilots"}],
        "features": [{"id": "corner_post_fasteners", "_remove": True}]
                    + [{"id": f["id"], "verify": [v for v in f["verify"] if not corner_ref(v)]} for f in c["features"] if f["id"] != "corner_post_fasteners" and any(corner_ref(v) for v in f["verify"])]
                    + [{"id": "base_shell", "description": f"Rectangular cavity [{-ec:g},{length + ec:g}] x [{-ec:g},{width + ec:g}], straight {w:g} mm walls and {w:g} mm floor. ECR-3: the square corner posts exist only as {post:g} x {post:g} feet in the floor plate (z <= -standoffHeight); four side bosses {post:g} wide in x, centred on x = {SIDE_X[0]:g} and x = {SIDE_X[1]:g}, fill y = {-(ec + post):g}..{-(ec + w):g} and y = {width + ec + w:g}..{width + ec + post:g} from the floor exterior to the rim. Floor top is -standoffHeight; footprint O is defined in brief section 5."},
                       {"id": "lid", "description": f"Separate flat {param(c, 'lidThickness'):g} mm plate over the wall footprint [{-(ec + w):g},{length + ec + w:g}] x [{-(ec + w):g},{width + ec + w:g}] plus the four side flanges over the bosses (no corner lugs), below face at pcbThickness+headroom, four Ø3.2 through holes on the {mid}. Apply source plug cutters to the lid at every headroom; they are inactive at nominal 20 and form USB-A edge reliefs at 15.",
                        "parameters": ["headroom", "pcbThickness", "lidThickness", "cornerPostWidth", "sideScrewXNear", "sideScrewXFar", "sideLidHoleDiameter"]},
                       {"id": "side_fasteners", "kind": "hole", "count": 4,
                        "description": f"Four lid screws on the long sides (y = 0 side and y = 56 side) at x = 50 and x = 75: Ø3.2 clearance through the lid flange, Ø2.5 x >= 5 blind pilot from the rim into the side boss, {mid} (mid-depth of the wall+boss band), outside the board and its edge band; verified by the region-filtered cylinder counts side_screw_*/side_pilot_* and the void/solid probes.",
                        "parameters": ["sideScrewXNear", "sideScrewXFar", "sideLidHoleDiameter", "pilotDiameter", "pilotDepth", "cornerPostWidth", "lidThickness", "headroom"],
                        "verify": [{"method": "void", "points": [[x, y, z_pilot] for x, y in axes], "note": "mid-depth of the four side-boss pilots"},
                                   {"method": "void", "points": [[x, y, z_lid] for x, y in axes], "note": "mid-thickness of the four lid clearance holes"},
                                   {"method": "solid", "points": [[x, y, 10.0] for y in (y_front_boss, y_back_boss) for x in SIDE_X], "note": "side-boss material at mid-height"},
                                   {"method": "section", "section": "lid_section"}],
                        "optional": False}],
    }
    return delta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="apply each delta and validate the revised contract; re-score the references")
    a = ap.parse_args(argv)
    if not STEP.exists():
        raise SystemExit(f"{STEP} missing: run the design first")
    design = Design()
    out = REPO / "results" / "_campaign" / "rpi5-ecr-references"
    out.mkdir(parents=True, exist_ok=True)
    deltas = {"ecr1": ecr1(design, out)[0], "ecr2": ecr2(design, out)[0], "ecr3": ecr3(design)}
    for label, delta in deltas.items():
        p = CASES / f"{DESIGN}-{label}" / "inputs" / "contract-delta.yaml"
        p.write_text(yaml.safe_dump(delta, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
        print(f"wrote {p}")
    if a.check:
        from opencad.contract import load_contract
        from opencad.geomcheck import features
        from opencad.stages.common import bbox_check
        from opencad.stages.ecr import apply_delta

        raw = yaml.safe_load(CONTRACT.read_text())
        for label, delta in deltas.items():
            revised, changed = apply_delta(copy.deepcopy(raw), delta)
            tmp = out / f"{label}-contract.yaml"
            tmp.write_text(yaml.safe_dump(revised, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
            try:
                c = load_contract(tmp)
            except Exception as e:  # noqa: BLE001
                print(f"{label}: revised contract INVALID: {e}")
                continue
            ref = out / f"{label}-reference.step"
            if not ref.exists():
                print(f"{label}: revised contract valid; {len(changed)} acceptance items changed (no reference solid: structural request)")
                continue
            shape = brep.read_step(ref)
            an = brep.analyze_step(ref)
            bad: list[str] = []
            face_res = features.check_faces(shape, c)
            for kind, res in (("face", face_res), ("cylinder", features.check_cylinders(shape, c)), ("section", features.check_sections(shape, c)),
                              ("dimension", features.check_dimensions(c, an["bbox_size"], face_res))):
                bad += [f"{kind}:{k}" for k, r in res.items() if not r.get("ok")]
            for f in c.features:
                for v in f.verify:
                    if v.points:
                        want = "out" if v.method == "void" else "in"
                        if any(s != want for s in brep.classify_points(shape, [list(p) for p in v.points])):
                            bad.append(f"feature-probe:{f.id}")
            for p in c.acceptance.probes:
                want = "out" if p.state == "void" else "in"
                if any(s != want for s in brep.classify_points(shape, [list(x) for x in p.points])):
                    bad.append(f"probe:{p.name}")
            if not bbox_check(c, an["bbox_min"], an["bbox_max"])["ok"]:
                bad.append("bbox")
            if c.acceptance.volume and abs(an["volume"] - c.acceptance.volume.expected) > c.acceptance.volume.expected * (c.acceptance.volume.tolerance_rel or 0):
                bad.append("volume")
            print(f"{label}: revised contract valid; {len(changed)} acceptance items changed; reference solid " + ("passes every check" if not bad else f"FAILS {bad}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

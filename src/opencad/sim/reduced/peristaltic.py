"""Peristaltic pump displacement from the placed geometry: rollers on a rotor squeeze a tube against a stator track.

Ideal positive displacement: each revolution moves the lumen volume along the roller track once, V_rev = A_lumen * 2 pi R_c,
with R_c the tube centreline radius where the rollers pass (from the placed rollers' axes and radii plus half the tube OD).
Occlusion is judged from the geometry: the radial space the rollers leave between themselves and the stator track against the
tube's double wall; an unoccluded tube pumps nothing ideal, a partly occluded one is reported as such."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from opencad.sim import observable, unavailable

DOC = """`reduced:peristaltic` — bodies [rotor, stator, <roller>, ...] (the rollers are the bodies whose joints sit on the rotor); inputs
tubeInnerDiameter, tubeOuterDiameter (mm); settings.speed_key names the operating-case rotor speed (rpm) unless the rotor's drive states
it; settings.track_radius_mm overrides the stator track radius found in the rollers' axial band. Quantities: flow_rate (mL/min),
volume_per_rev (uL), occlusion_gap (mm, radial roller-to-stator space), track_radius (mm)."""

ASSUMPTIONS = [
    "ideal positive displacement: the full lumen area moves once around the roller track per revolution",
    "no tube elastic recovery, backflow or slip; rollers roll without dragging the tube",
    "occlusion from the rest geometry: roller surface to stator track radial space against twice the tube wall",
]


def _v(sim: Any, key: str) -> float:
    return float(sim.inputs[key].value)


def run(sim: Any, obs: list[Any], geom: Any, cases: dict[str, Any]) -> dict[str, Any]:
    a = geom.contract
    rotor = str(sim.settings.get("rotor") or sim.bodies[0])
    stator = str(sim.settings.get("stator") or sim.bodies[1])
    from opencad.assembly.joints import chain

    rj = next((j for j in reversed(chain(a, rotor)) if j.rotates), None)  # a rotor fixed to a driven gear turns on the gear's joint
    if rj is None:
        return unavailable(f"neither {rotor} nor a body it is fixed to turns on a joint")
    o, ax = geom.joint_axis(rj.name)
    rollers = [j.child for j in a.joints if j.parent == rotor and j.child in sim.bodies and not j.closure]
    if not rollers:
        return unavailable(f"no roller bodies on joints of {rotor}")
    centres, radii = [], []
    for b in rollers:
        ro, rax = geom.joint_axis(geom.joint_of(b).name)
        w = ro - o
        centres.append(float(np.linalg.norm(w - (w @ ax) * ax)))
        radii.append(geom.radial_extent(b)[1])
    r_roll = float(np.mean(centres) + np.mean(radii))  # outermost roller surface radius
    spans = [geom.axial_extent(b, rj.name) for b in rollers]
    band = (min(s for s, _ in spans), max(e for _, e in spans))
    s_in = float(sim.settings["track_radius_mm"]) if "track_radius_mm" in sim.settings else geom.radial_extent(stator, rj.name, band=band, beyond=float(np.mean(centres)))[0]
    d_in, d_out = _v(sim, "tubeInnerDiameter"), _v(sim, "tubeOuterDiameter")
    gap = s_in - r_roll
    wall2 = d_out - d_in
    occlusion = float(np.clip((d_out - gap) / wall2, 0.0, None)) if wall2 > 0 else float("nan")
    r_c = r_roll + max(gap, 0.0) / 2 if gap > 0 else r_roll
    v_rev = math.pi * (d_in / 2) ** 2 * 2 * math.pi * r_c  # mm3 = uL
    speed_key = sim.settings.get("speed_key")
    out = {}
    for ob in obs:
        case = cases.get(ob.case) if ob.case else (cases.get(sim.cases[0]) if sim.cases else None)
        rpm = float(case.values[speed_key]) if case is not None and speed_key else (rj.drive.speed if rj.drive is not None and rj.drive.speed else None)
        val = {"volume_per_rev": v_rev, "occlusion_gap": gap, "track_radius": r_c,
               "flow_rate": v_rev * rpm / 1000.0 if rpm is not None else None}.get(ob.quantity)
        out[ob.id] = observable(val, ob.unit, case=ob.case, model="peristaltic")
    return {"status": "ok", "solver": {"name": "reduced:peristaltic"}, "observables": out, "assumptions": ASSUMPTIONS,
            "inputs_used": {"rollers": rollers, "roller_centre_radius_mm": float(np.mean(centres)), "roller_radius_mm": float(np.mean(radii)),
                            "stator_track_radius_mm": s_in, "radial_gap_mm": gap, "double_wall_mm": wall2, "occlusion_ratio": occlusion, "track_radius_mm": r_c}}

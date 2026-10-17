"""Centrifugal pump head from Euler's turbine equation on the placed impeller.

Theoretical head with zero inlet swirl: H_th = u2 c_u2 / g with c_u2 = sigma u2 - c_m2 / tan(beta2), u2 = omega r2, the impeller tip
radius r2 measured from the placed rotor about its joint axis, c_m2 = Q / (2 pi r2 b2), sigma the Wiesner slip factor
1 - sqrt(sin beta2) / Z^0.7. The static pressure rise is eta_h rho g H_th with the declared hydraulic efficiency; its stated
uncertainty is propagated to the prediction as u_input. No coefficient is fitted to a measurement."""

from __future__ import annotations

import math
from typing import Any

from opencad.sim import observable, unavailable

DOC = """`reduced:pump_euler` — bodies [rotor]; inputs fluidDensity (kg/m3), bladeCount, bladeOutletAngle (deg from the tangent, 90 for radial
blades), bladeOutletWidth (mm), hydraulicEfficiency (with its uncertainty); settings flow_key / speed_key (operating-case values in L/min
and rpm). The tip radius comes from the placed rotor. Quantities: pressure_rise (Pa), head (m), euler_head (m, ideal)."""

ASSUMPTIONS = [
    "zero inlet swirl; Wiesner slip on the blade outlet angle and count",
    "static pressure rise = hydraulic efficiency x ideal (slipped) Euler head; the efficiency is a declared input, not fitted",
    "the impeller tip radius is the placed rotor's largest radius about its joint axis",
]

G = 9.80665


def _v(sim: Any, key: str) -> float:
    return float(sim.inputs[key].value)


def run(sim: Any, obs: list[Any], geom: Any, cases: dict[str, Any]) -> dict[str, Any]:
    rotor = str(sim.settings.get("rotor") or sim.bodies[0])
    j = geom.joint_of(rotor)
    if j is None or not j.rotates:
        return unavailable(f"{rotor} has no rotating joint")
    r2 = geom.radial_extent(rotor)[1] * 1e-3
    rho, z = _v(sim, "fluidDensity"), _v(sim, "bladeCount")
    beta = math.radians(_v(sim, "bladeOutletAngle"))
    b2 = _v(sim, "bladeOutletWidth") * 1e-3
    eta = sim.inputs["hydraulicEfficiency"]
    sigma = 1 - math.sqrt(math.sin(beta)) / z ** 0.7
    fk, sk = sim.settings.get("flow_key"), sim.settings.get("speed_key")
    out = {}
    for ob in obs:
        case = cases.get(ob.case) if ob.case else None
        if case is None or fk not in case.values or sk not in case.values:
            out[ob.id] = observable(None, ob.unit, case=ob.case, note="the observable needs an operating case with the flow and speed keys")
            continue
        q, w = float(case.values[fk]) / 60000.0, float(case.values[sk]) * 2 * math.pi / 60
        u2 = w * r2
        cm2 = q / (2 * math.pi * r2 * b2)
        cu2 = sigma * u2 - cm2 / math.tan(beta)
        h_th = u2 * cu2 / G
        dp = float(eta.value) * rho * G * h_th
        u_in = (eta.uncertainty or 0.0) * rho * G * h_th
        val = {"pressure_rise": dp, "head": float(eta.value) * h_th, "euler_head": h_th}.get(ob.quantity)
        if ob.quantity == "pressure_rise" and ob.unit.lower() == "mmhg":
            val, u_in = dp / 133.322, u_in / 133.322
        out[ob.id] = observable(val, ob.unit, case=ob.case, u_input=u_in if ob.quantity in ("pressure_rise", "head") else None, model="pump_euler",
                                tip_speed_m_s=u2, slip=sigma)
    return {"status": "ok", "solver": {"name": "reduced:pump_euler"}, "observables": out, "assumptions": ASSUMPTIONS,
            "inputs_used": {"tip_radius_m": r2, "slip_factor": sigma, "blade_outlet_width_m": b2, "hydraulic_efficiency": float(eta.value)}}

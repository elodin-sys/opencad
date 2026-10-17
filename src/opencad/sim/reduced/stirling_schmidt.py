"""Isothermal (Schmidt) analysis of a rhombic-drive displacer-type Stirling engine.

Rhombic drive (two counter-rotating cranks of radius r at +-e from the cylinder axis, rods of length L): displacer yoke
y_d = r sin(t) + b, piston yoke y_p = r sin(t) - b, b = sqrt(L^2 - (e - r cos t)^2). Expansion space V_e = V_ce + A (max y_d - y_d);
compression space V_c = V_cc + (A - A_rod) (2b - min 2b), with the displacer rod through the piston. Uniform pressure over the
expansion (T_h), heater (T_h), regenerator (log-mean), cooler (T_k) and compression (T_k) spaces; the gas mass sets the cycle-mean
pressure to the case value. Indicated work is the cycle integral of p dV. It is the ideal isothermal upper bound: no heat-exchanger,
flow, leakage or mechanical losses."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from opencad.sim import observable

DOC = """`reduced:stirling_schmidt` — bodies [] or the mechanism bodies; inputs cylinderBore, displacerRodDiameter, crankRadius,
connectingRodLength, eccentricity (mm), expansionClearanceVolume, heaterVolume, regeneratorVolume, coolerVolume,
compressionClearanceVolume (cm3), gasConstant (J/kg K); settings pressure_key (MPa), speed_key (rpm), hot_key and cold_key (K) naming
operating-case values. Quantities: indicated_power (W), indicated_work (J per cycle), pressure_ratio (max/min), swept_volume_expansion and
swept_volume_compression (cm3)."""

ASSUMPTIONS = [
    "isothermal expansion and compression spaces at the heater and cooler temperatures; ideal regenerator at the log-mean temperature",
    "uniform instantaneous pressure (no flow friction); no leakage, shuttle, conduction or mechanical losses",
]


def volumes(bore: float, rod: float, r: float, rod_len: float, e: float, v_ce: float, v_cc: float, n: int = 720) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Crank angle (rad) and expansion / compression volumes (m3) from drive lengths (m) and clearances (m3)."""
    t = np.linspace(0.0, 2 * math.pi, n, endpoint=False)
    b = np.sqrt(rod_len ** 2 - (e - r * np.cos(t)) ** 2)
    yd = r * np.sin(t) + b
    a = math.pi * bore ** 2 / 4
    ve = v_ce + a * (yd.max() - yd)
    vc = v_cc + (a - math.pi * rod ** 2 / 4) * (2 * b - (2 * b).min())
    return t, ve, vc


def schmidt(t: np.ndarray, ve: np.ndarray, vc: np.ndarray, vh: float, vr: float, vk: float, th: float, tk: float, p_mean: float, gas_r: float) -> dict[str, float]:
    tr = (th - tk) / math.log(th / tk)
    s = vc / tk + vk / tk + vr / tr + vh / th + ve / th
    shape = 1.0 / s
    mass = p_mean / (gas_r * shape.mean())
    p = mass * gas_r * shape
    dve, dvc = np.roll(ve, -1) - ve, np.roll(vc, -1) - vc
    pm = 0.5 * (p + np.roll(p, -1))
    we, wc = float(np.sum(pm * dve)), float(np.sum(pm * dvc))
    return {"work_j": we + wc, "expansion_work_j": we, "compression_work_j": wc, "pressure_ratio": float(p.max() / p.min()), "gas_mass_kg": mass,
            "p_max_pa": float(p.max()), "p_min_pa": float(p.min())}


def run(sim: Any, obs: list[Any], geom: Any, cases: dict[str, Any]) -> dict[str, Any]:
    v = {k: float(x.value) for k, x in sim.inputs.items()}
    t, ve, vc = volumes(v["cylinderBore"] * 1e-3, v["displacerRodDiameter"] * 1e-3, v["crankRadius"] * 1e-3, v["connectingRodLength"] * 1e-3,
                        v["eccentricity"] * 1e-3, v["expansionClearanceVolume"] * 1e-6, v["compressionClearanceVolume"] * 1e-6)
    pk, sk, hk, ck = (sim.settings.get(k) for k in ("pressure_key", "speed_key", "hot_key", "cold_key"))
    out, per = {}, {}
    for ob in obs:
        case = cases.get(ob.case) if ob.case else None
        if case is None or any(k not in case.values for k in (pk, sk, hk, ck)):
            out[ob.id] = observable(None, ob.unit, case=ob.case, note="the observable needs an operating case with pressure, speed and both temperatures")
            continue
        res = per.get(ob.case) or schmidt(t, ve, vc, v["heaterVolume"] * 1e-6, v["regeneratorVolume"] * 1e-6, v["coolerVolume"] * 1e-6,
                                          float(case.values[hk]), float(case.values[ck]), float(case.values[pk]) * 1e6, v["gasConstant"])
        per[ob.case] = res
        freq = float(case.values[sk]) / 60
        val = {"indicated_power": res["work_j"] * freq, "indicated_work": res["work_j"], "pressure_ratio": res["pressure_ratio"],
               "swept_volume_expansion": float((ve.max() - ve.min()) * 1e6), "swept_volume_compression": float((vc.max() - vc.min()) * 1e6)}.get(ob.quantity)
        out[ob.id] = observable(val, ob.unit, case=ob.case, model="stirling_schmidt")
    return {"status": "ok", "solver": {"name": "reduced:stirling_schmidt"}, "observables": out, "assumptions": ASSUMPTIONS, "cases": per,
            "inputs_used": {"swept_expansion_cm3": float((ve.max() - ve.min()) * 1e6), "swept_compression_cm3": float((vc.max() - vc.min()) * 1e6)}}

"""Friction-brake energy budget and surface temperature, closed form on the placed geometry.

Uses the same inputs as the CalculiX friction_brake source. Produced heat is the per-brake share of the vehicle's kinetic-energy
loss. The disc surface temperature is the semi-infinite (Duhamel) response to the ring-averaged flux over the pad's swept band,
plus Jaeger's high-Peclet flash rise under the pad (a band source of the pad's arc length moving at the disc surface speed).
Bulk temperatures come from lumped balances with forced convection and radiation over each body's exposed area."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from opencad.sim import observable
from opencad.sim.calculix import MM, SIGMA, _v, brake_history, charron, film_coefficient

DOC = """`reduced:brake_energy` — bodies [disc, pad]; the same inputs as calculix friction_brake plus wheelRadius (m, disc speed = vehicle
speed / wheel radius). Quantities: max_temperature (disc surface: ring-averaged rise plus the flash rise under the pad; with body = pad the
pad's bulk maximum), time_of_max_temperature, produced_heat, stored_heat, dissipated_heat (J), bulk_temperature (K), hotspot_radius."""

ASSUMPTIONS = [
    "disc surface: semi-infinite body under the ring-averaged flux (valid while the heat penetration depth is below the disc thickness)",
    "flash rise: Jaeger's moving band source at high Peclet number from the excess flux q_pad - q_ring, the pad's mean arc length, "
    "disc surface speed = omega r at mid-band",
    "heat split between disc and pad by Charron's effusivity ratio; no conduction across the interface",
    "bulk temperatures: lumped bodies; losses by forced convection (flat plate, U = vehicle speed) and radiation on exposed faces",
]


def _exposed_area(geom: Any, body: str) -> float:
    rows = geom.boundaries(body).get("faces") or []
    roles = {b.name: b.role for b in geom.contract.boundaries if b.body == body}
    area = sum(r["area"] for r in rows if roles.get(r.get("label")) not in ("symmetry", "contact"))
    return area * MM * MM if rows else float("nan")


def run(sim: Any, obs: list[Any], geom: Any, cases: dict[str, Any]) -> dict[str, Any]:
    bodies = list(sim.bodies)
    disc = str(sim.settings.get("disc") or bodies[0])
    pad = str(sim.settings.get("pad") or next(b for b in bodies if b != disc))
    joint = geom.joint_of(disc)
    t_end = float(sim.settings.get("end_time") or _v(sim, "endTime", 12.0))
    dt = 1e-3
    t = np.arange(0.0, t_end + dt / 2, dt)
    hist = brake_history(sim, t)
    power, v = hist["power"], hist["v"]
    produced = np.concatenate([[0.0], np.cumsum((power[1:] + power[:-1]) / 2 * dt)])
    xi = charron(sim, disc, pad)
    r_in, r_out = geom.radial_extent(pad, joint.name)
    r_in, r_out = r_in * MM, r_out * MM
    contact_pad = [b.name for b in geom.contract.boundaries if b.body == pad and b.role == "contact"]
    a_pad = sum(r["area"] for r in geom.boundaries(pad).get("faces") or [] if r.get("label") in contact_pad) * MM * MM
    if not a_pad:
        a_pad = float("nan")
    a_ring = math.pi * (r_out ** 2 - r_in ** 2)
    e_d = math.sqrt(_v(sim, f"{disc}.conductivity") * _v(sim, f"{disc}.density") * _v(sim, f"{disc}.specificHeat"))
    q_ring = xi * power / a_ring
    kernel = 1.0 / np.sqrt(np.maximum(t, dt / 2))
    dT_ring = np.convolve(q_ring, kernel)[: len(t)] * dt / (e_d * math.sqrt(math.pi))
    r_mid = (r_in + r_out) / 2
    arc = a_pad / (r_out - r_in)
    omega = np.abs(v) / _v(sim, "wheelRadius")
    speed = np.maximum(omega * r_mid, 1e-6)
    dT_flash = np.where(power > 0, 2 * xi * power / a_pad * max(0.0, 1.0 - a_pad / a_ring) * np.sqrt(arc / (math.pi * speed)) / e_d, 0.0)
    t_amb = _v(sim, "ambientTemperature")
    t0 = _v(sim, "initialTemperature", t_amb)
    peak = t0 + dT_ring + dT_flash
    h = film_coefficient(sim, v)
    temps = {}
    stored = np.zeros_like(t)
    lost = np.zeros_like(t)
    for body, share in ((disc, xi), (pad, 1 - xi)):
        mc = _v(sim, f"{body}.density") * geom.volume(body) * MM ** 3 * _v(sim, f"{body}.specificHeat")
        area, eps = _exposed_area(geom, body), _v(sim, f"{body}.emissivity", 0.0)
        tb = np.empty_like(t)
        tb[0] = t0
        loss = np.zeros_like(t)
        for k in range(1, len(t)):
            q_out = h[k - 1] * area * (tb[k - 1] - t_amb) + eps * SIGMA * area * (tb[k - 1] ** 4 - t_amb ** 4)
            loss[k] = loss[k - 1] + q_out * dt
            tb[k] = tb[k - 1] + (share * power[k - 1] - q_out) * dt / mc
        temps[body] = tb
        stored += mc * (tb - t0)
        lost += loss
    residual = (produced[-1] - stored[-1] - lost[-1]) / produced[-1] if produced[-1] else 0.0
    values = {"max_temperature": float(peak.max()), "time_of_max_temperature": float(t[int(np.argmax(peak))]), "produced_heat": float(produced[-1]),
              "stored_heat": float(stored[-1]), "dissipated_heat": float(lost[-1]), "bulk_temperature": float(temps[disc][-1]),
              "hotspot_radius": r_out / MM}
    out = {}
    for ob in obs:
        val = values.get(ob.quantity)
        if ob.quantity == "max_temperature" and ob.body == pad:
            val = float(temps[pad].max())
        if ob.quantity == "hotspot_radius" and ob.unit == "m":
            val = r_out
        out[ob.id] = observable(val, ob.unit, case=ob.case, model="brake_energy")
    step = max(1, len(t) // 400)
    return {"status": "ok", "solver": {"name": "reduced:brake_energy"}, "observables": out, "assumptions": ASSUMPTIONS,
            "conservation": {"energy_balance": {"value": float(residual), "tolerance": 1e-3, "ok": abs(residual) <= 1e-3, "produced_j": float(produced[-1]),
                                                "stored_j": float(stored[-1]), "dissipated_j": float(lost[-1])}},
            "series": {"t_s": t[::step].tolist(), "peak_surface_K": peak[::step].tolist(), "ring_rise_K": dT_ring[::step].tolist(),
                       "flash_rise_K": dT_flash[::step].tolist(), f"bulk_{disc}_K": temps[disc][::step].tolist(), f"bulk_{pad}_K": temps[pad][::step].tolist()},
            "inputs_used": {"heat_fraction_disc": xi, "band_m": [r_in, r_out], "pad_contact_area_m2": a_pad, "ring_area_m2": a_ring, "pad_arc_m": arc}}

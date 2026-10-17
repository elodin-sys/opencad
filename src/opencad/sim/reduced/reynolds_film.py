"""Hydrodynamic partial-arc journal bearing: finite-length Reynolds equation with Swift-Stieber cavitation, load-balanced.

Geometry comes from the placed bodies: the shaft radius (its largest radius inside the bush's axial band), the bush bore radius
(its smallest radius), the radial clearance as their difference, the bush length along the shaft axis and the bush arc (the angular
span of the bore surface about the shaft axis; bottom dead centre, BDC, is the arc bisector). Angles are measured from BDC in the
direction the shaft surface moves. Film h = c (1 - e cos(theta - alpha)); p = 0 at the arc ends and the bush edges; p >= 0 by a
primal-dual active set. (e, alpha) are solved so the film force balances the case load acting toward BDC. Viscosity follows
Walther's equation through the two stated kinematic viscosities at the film temperature, which the thermal wedge marches along the
arc from the inlet (adiabatic mixed film: rho c_p q dT = dissipation dtheta, the liquid flow frozen past film rupture)."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from opencad.sim import observable, unavailable

DOC = """`reduced:reynolds_film` — bodies [shaft, bush] (the shaft on a revolute joint); inputs oilDensity (kg/m3), oilViscosity40 and
oilViscosity100 (kinematic, mm2/s), oilSpecificHeat (J/kg K), inletTemperature (degC); settings load_key (kN) and speed_key (rpm) naming
operating-case values, grid [n_theta, n_z] (default [181, 41]), thermal (default true: the thermal wedge). Radius,
clearance, length and arc are measured from the placed bodies. Quantities: pressure (at observable.location on the bore; Pa, kPa, MPa or
bar), max_pressure, min_film_thickness (um or mm), min_film_angle (deg from BDC in the rotation direction), eccentricity_ratio,
attitude_angle (deg), friction_power (W), temperature_rise (K), max_temperature_ratio (maximum film temperature over the film temperature
at settings.ratio_reference_deg, default -85, both in degC)."""

ASSUMPTIONS = [
    "rigid, aligned surfaces (no thermal or elastic distortion of the clearance)",
    "Swift-Stieber (Reynolds) cavitation: p >= 0 with zero gradient at film rupture; zero gauge pressure at the arc ends and bush edges",
    "thermal wedge: viscosity varies along the arc only (mixed across the gap and the length), adiabatic walls, fresh oil at the inlet edge",
]

PRESSURE_UNITS = {"pa": 1.0, "kpa": 1e3, "mpa": 1e6, "bar": 1e5}
LENGTH_UNITS = {"um": 1e-6, "µm": 1e-6, "micrometre": 1e-6, "mm": 1e-3, "m": 1.0}


def walther(nu40: float, nu100: float):
    """Kinematic viscosity (mm2/s) at T (degC) through log10 log10(nu + 0.7) = A - B log10(T_K)."""
    t1, t2 = math.log10(313.15), math.log10(373.15)
    y1, y2 = math.log10(math.log10(nu40 + 0.7)), math.log10(math.log10(nu100 + 0.7))
    b = (y1 - y2) / (t2 - t1)
    a = y1 + b * t1
    return lambda t: 10 ** (10 ** (a - b * math.log10(t + 273.15))) - 0.7


class Film:
    """Finite-difference Reynolds solver on the arc [th1, th2] x [0, L]."""

    def __init__(self, radius: float, clearance: float, length: float, th1: float, th2: float, n_theta: int, n_z: int):
        from scipy import sparse

        self.sparse = sparse
        self.R, self.c, self.L = radius, clearance, length
        self.th = np.linspace(th1, th2, n_theta)
        self.z = np.linspace(0.0, length, n_z)
        self.dth, self.dz = self.th[1] - self.th[0], self.z[1] - self.z[0]
        self.ni, self.nj = n_theta - 2, n_z - 2

    def h(self, th: np.ndarray, ecc: float, alpha: float) -> np.ndarray:
        return self.c * (1.0 - ecc * np.cos(th - alpha))

    def solve(self, ecc: float, alpha: float, mu: float | np.ndarray, omega: float) -> np.ndarray:
        """Pressure on the full grid (zero on the boundary) for eccentricity ratio ecc, attitude alpha (rad); mu scalar or per theta node."""
        sp = self.sparse
        from scipy.sparse.linalg import spsolve

        R, dth, dz, ni, nj = self.R, self.dth, self.dz, self.ni, self.nj
        thi = self.th[1:-1]
        m = np.broadcast_to(np.asarray(mu, float), self.th.shape)
        me, mw = 0.5 * (m[1:-1] + m[2:]), 0.5 * (m[1:-1] + m[:-2])
        he, hw, hp = self.h(thi + dth / 2, ecc, alpha), self.h(thi - dth / 2, ecc, alpha), self.h(thi, ecc, alpha)
        ae, aw = he ** 3 / me / (R * dth) ** 2, hw ** 3 / mw / (R * dth) ** 2
        an = hp ** 3 / m[1:-1] / dz ** 2
        n = ni * nj
        idx = np.arange(n).reshape(ni, nj)
        diag = np.repeat(ae + aw + 2 * an, nj)
        rows, cols, vals = [idx.ravel()], [idx.ravel()], [diag]
        for di, coef in ((1, ae), (-1, aw)):
            src = idx[max(0, -di):ni - max(0, di), :]
            rows.append(src.ravel())
            cols.append((src + di * nj).ravel())
            vals.append(-np.repeat(coef[max(0, -di):ni - max(0, di)], nj))
        for dj in (1, -1):
            src = idx[:, max(0, -dj):nj - max(0, dj)]
            rows.append(src.ravel())
            cols.append((src + dj).ravel())
            vals.append(-np.repeat(an, nj - 1))
        k = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
        g = np.repeat(-6.0 * omega * (he - hw) / dth, nj)
        scale = float(diag.mean())
        active = np.zeros(n, bool)
        p = np.zeros(n)
        for _ in range(60):
            free = ~active
            p = np.zeros(n)
            if free.any():
                p[free] = spsolve(k[free][:, free].tocsc(), g[free])
            lam = k @ p - g
            new = (lam - scale * p) > 1e-12 * max(1.0, float(np.abs(g).max()))
            if np.array_equal(new, active):
                break
            active = new
        full = np.zeros((ni + 2, nj + 2))
        full[1:-1, 1:-1] = np.maximum(p, 0.0).reshape(ni, nj)
        return full

    def forces(self, p: np.ndarray) -> tuple[float, float]:
        """(along BDC, along the rotation tangent) film-force components the bush exerts on the shaft (N), positive away from the bore."""
        w = np.trapezoid(p, self.z, axis=1) * self.R
        return float(np.trapezoid(w * np.cos(self.th), self.th)), float(np.trapezoid(w * np.sin(self.th), self.th))

    def balance(self, load: float, mu: float | np.ndarray, omega: float, guess: tuple[float, float] = (0.6, math.radians(30))) -> tuple[float, float, np.ndarray]:
        ecc, alpha = guess
        for _ in range(40):
            p = self.solve(ecc, alpha, mu, omega)
            fb, ft = self.forces(p)
            r = np.array([fb - load, ft])
            if abs(r[0]) <= 1e-4 * load and abs(r[1]) <= 1e-4 * load:
                return ecc, alpha, p
            de, da = 1e-4, 1e-4
            j = np.empty((2, 2))
            for k, (e2, a2) in enumerate(((ecc + de, alpha), (ecc, alpha + da))):
                f2 = self.forces(self.solve(e2, a2, mu, omega))
                j[:, k] = (np.array([f2[0] - load, f2[1]]) - r) / (de if k == 0 else da)
            step = np.linalg.solve(j, -r)
            t = 1.0
            while t > 1e-3:
                e_new, a_new = ecc + t * step[0], alpha + t * step[1]
                if 0.0 < e_new < 0.995:
                    fb2, ft2 = self.forces(self.solve(e_new, a_new, mu, omega))
                    if math.hypot(fb2 - load, ft2) < math.hypot(*r):
                        break
                t /= 2
            ecc, alpha = min(max(ecc + t * step[0], 1e-3), 0.995), alpha + t * step[1]
        raise RuntimeError(f"load balance did not converge (e={ecc:.4f}, alpha={math.degrees(alpha):.2f} deg)")

    def wedge(self, p: np.ndarray, ecc: float, alpha: float, mu: np.ndarray, omega: float) -> tuple[np.ndarray, np.ndarray]:
        """Per theta station: circumferential liquid flow (m3/s) and dissipation per radian (W/rad). Past film rupture the liquid flow
        stays at its rupture value and shears only that fraction of the gap."""
        h = self.h(self.th, ecc, alpha)
        dpdth = np.gradient(p, self.dth, axis=0)
        u = omega * self.R
        m = mu[:, None]
        q = np.trapezoid(u * h[:, None] / 2 - h[:, None] ** 3 / (12 * m * self.R) * dpdth, self.z, axis=1)
        diss = np.trapezoid((m * u / h[:, None] + h[:, None] / (2 * self.R) * dpdth) * u, self.z, axis=1) * self.R
        centre = p[:, p.shape[1] // 2]
        peak = int(np.argmax(centre))
        rupt = next((i for i in range(peak, len(centre)) if centre[i] <= 0.0), None)
        if rupt is not None:
            q_liq = q[rupt]
            frac = np.clip(q_liq / np.maximum(q[rupt:], 1e-12), 0.0, 1.0)
            q[rupt:] = np.minimum(q[rupt:], q_liq)
            diss[rupt:] *= frac
        return q, diss

    def march(self, q: np.ndarray, diss: np.ndarray, t_in: float, rho: float, cp: float) -> np.ndarray:
        """Mixed film temperature along the arc from the inlet edge (adiabatic walls)."""
        t = np.empty_like(self.th)
        t[0] = t_in
        for i in range(1, len(t)):
            dq = 0.5 * (diss[i - 1] + diss[i]) * self.dth
            t[i] = t[i - 1] + dq / (rho * cp * max(0.5 * (q[i - 1] + q[i]), 1e-12))
        return t


def _unit(unit: str, table: dict[str, float], default: float) -> float:
    return table.get((unit or "").strip().lower(), default)


def run(sim: Any, obs: list[Any], geom: Any, cases: dict[str, Any]) -> dict[str, Any]:
    shaft = str(sim.settings.get("shaft") or sim.bodies[0])
    bush = str(sim.settings.get("bush") or sim.bodies[1])
    j = geom.joint_of(shaft)
    if j is None or not j.rotates:
        return unavailable(f"{shaft} has no rotating joint")
    o, a = geom.joint_axis(j.name)
    t0, t1 = geom.axial_extent(bush, j.name)
    r_bore = geom.radial_extent(bush, j.name)[0]
    r_shaft = geom.radial_extent(shaft, j.name, band=(t0, t1))[1]
    c = (r_bore - r_shaft) * 1e-3
    if c <= 0:
        return unavailable(f"no clearance between {shaft} (r {r_shaft:.4f} mm) and the {bush} bore (r {r_bore:.4f} mm)")
    import trimesh

    v = np.asarray(trimesh.load(geom.stl(bush), force="mesh").vertices) - o
    radial = v - np.outer(v @ a, a)
    rr = np.linalg.norm(radial, axis=1)
    bore = radial[np.abs(rr - r_bore) < max(0.25 * (r_bore - r_shaft), 1e-4)]
    bdc = bore.mean(axis=0)
    bdc /= np.linalg.norm(bdc)
    fk, sk, lk = sim.settings.get("flow_key"), sim.settings.get("speed_key"), sim.settings.get("load_key")
    sense = 1.0
    if j.drive is not None and j.drive.speed is not None and j.drive.speed < 0:
        sense = -1.0
    tan = sense * np.cross(a, bdc)
    ang = np.degrees(np.arctan2(bore @ tan, bore @ bdc))
    arc = sim.settings.get("arc_deg") or [float(ang.min()), float(ang.max())]
    n_theta, n_z = (sim.settings.get("grid") or [181, 41])[:2]
    film = Film(r_shaft * 1e-3, c, (t1 - t0) * 1e-3, math.radians(arc[0]), math.radians(arc[1]), int(n_theta), int(n_z))
    nu_of = walther(float(sim.inputs["oilViscosity40"].value), float(sim.inputs["oilViscosity100"].value))
    rho = float(sim.inputs["oilDensity"].value)
    cp = float(sim.inputs["oilSpecificHeat"].value)
    t_in = float(sim.inputs["inletTemperature"].value)
    relax = float(sim.settings.get("thermal_relaxation", 0.5))
    thermal = bool(sim.settings.get("thermal", True))
    del fk
    out: dict[str, Any] = {}
    solved: dict[str, dict[str, Any]] = {}
    for cid in sorted({ob.case for ob in obs if ob.case}):
        case = cases.get(cid)
        if case is None or lk not in case.values or sk not in case.values:
            continue
        load, omega = float(case.values[lk]) * 1e3, float(case.values[sk]) * 2 * math.pi / 60
        temp, guess = np.full_like(film.th, t_in), (0.6, math.radians(30))
        for _ in range(40 if thermal else 1):
            mu = rho * np.array([nu_of(t) for t in temp]) * 1e-6
            ecc, alpha, p = film.balance(load, mu, omega, guess)
            guess = (ecc, alpha)
            q, diss = film.wedge(p, ecc, alpha, mu, omega)
            new = film.march(q, diss, t_in, rho, cp)
            change = float(np.abs(new - temp).max())
            temp = temp + relax * (new - temp)
            if not thermal or change < 0.05:
                break
        h = film.h(film.th, ecc, alpha)
        solved[cid] = {"eccentricity_ratio": ecc, "attitude_angle_deg": math.degrees(alpha), "viscosity_inlet_pa_s": float(mu[0]),
                       "viscosity_outlet_pa_s": float(mu[-1]), "temperature_rise_k": float(temp.max() - t_in), "friction_power_w": float(np.trapezoid(diss, film.th)),
                       "inflow_m3_s": float(q[0]), "max_pressure_pa": float(p.max()), "min_film_m": float(h.min()),
                       "min_film_angle_deg": math.degrees(float(film.th[int(np.argmin(h))])), "temperature_c": temp.round(2).tolist()[::10],
                       "ratio": float(temp.max() / np.interp(math.radians(float(sim.settings.get("ratio_reference_deg", -85.0))), film.th, temp)), "p": p}
    for ob in obs:
        s = solved.get(ob.case or "")
        if s is None:
            out[ob.id] = observable(None, ob.unit, case=ob.case, note="the observable needs an operating case with the load and speed keys")
            continue
        q, val = ob.quantity, None
        if q == "pressure" and ob.location is not None:
            w = np.asarray(ob.location, float) - o
            zz = (w @ a - t0) * 1e-3
            th = math.atan2(float(w @ tan), float(w @ bdc))
            from scipy.interpolate import RegularGridInterpolator

            f = RegularGridInterpolator((film.th, film.z), s["p"], bounds_error=False, fill_value=None)
            val = float(f([[th, zz]])[0]) / _unit(ob.unit, PRESSURE_UNITS, 1.0)
        elif q == "max_pressure":
            val = s["max_pressure_pa"] / _unit(ob.unit, PRESSURE_UNITS, 1.0)
        elif q == "min_film_thickness":
            val = s["min_film_m"] / _unit(ob.unit, LENGTH_UNITS, 1e-6)
        elif q == "min_film_angle":
            val = s["min_film_angle_deg"]
        elif q in ("eccentricity_ratio", "attitude_angle", "friction_power", "temperature_rise"):
            val = s[{"eccentricity_ratio": "eccentricity_ratio", "attitude_angle": "attitude_angle_deg", "friction_power": "friction_power_w",
                     "temperature_rise": "temperature_rise_k"}[q]]
        elif q == "max_temperature_ratio":
            val = s["ratio"]
        out[ob.id] = observable(val, ob.unit, case=ob.case, model="reynolds_film")
    return {"status": "ok", "solver": {"name": "reduced:reynolds_film", "grid": [int(n_theta), int(n_z)]}, "observables": out, "assumptions": ASSUMPTIONS,
            "inputs_used": {"shaft_radius_mm": r_shaft, "bore_radius_mm": r_bore, "clearance_um": c * 1e6, "length_mm": t1 - t0, "arc_deg": arc,
                            "bdc": bdc.tolist(), "rotation_tangent": tan.tolist()},
            "cases": {cid: {k: v for k, v in s.items() if k != "p"} for cid, s in solved.items()}}

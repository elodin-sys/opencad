"""CalculiX adapter (the ccx bundled with FreeCAD, `OPENCAD_CCX`): gmsh tetrahedra (C3D10), SI units, one analysis per
refinement level, results parsed from the .dat file.

thermal_transient, `settings.source: friction_brake`: a vehicle decelerating from `initialSpeed` at `deceleration` between
`brakeStart` and `brakeEnd` puts P(t) = vehicleMass v(t) a(t) / brakeCount into each brake. The disc share (Charron's
effusivity ratio unless `discHeatFraction` is given) is spread over the band of the disc's contact face that the pad sweeps
(ring-averaged: the pad's passes are faster than conduction across the band); the pad share goes into the pad's contact face.
Every other face except `symmetry` boundaries loses heat by forced convection (flat plate, U = v(t)) and radiation.
structural_static: fixed boundaries, centrifugal load from the body's drive speed, `pressure.<boundary>` loads.
modal: fixed boundaries, `settings.modes` natural frequencies."""

from __future__ import annotations

import math
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np

from opencad.sim import FORMAL_ORDER, failed, observable, predict, refinement, study, unavailable


def _studies(sim: Any, obs: list[Any], levels: dict[str, list[float]]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Observable rows and the refinement verdict of a global ladder (every level computed, in the declared order)."""
    factors = [lv.factor for lv in sim.levels()]
    tol = float(sim.settings.get("refinement_tolerance", 0.05))
    studies, out = {}, {}
    for ob in obs:
        rows = [{"label": f"{f:g}", "factor": f, "value": v} for f, v in zip(factors, levels.get(ob.id) or [])]
        studies[ob.id] = study(rows, expected=len(factors), tolerance=tol, formal_order=float(sim.settings.get("formal_order", FORMAL_ORDER)))
        out[ob.id] = predict(rows, studies[ob.id], ob.unit, ob.case)
    return out, (refinement(studies, tol) if len(factors) > 1 else None)

DOC = """`calculix` — physics thermal_transient | structural_static | modal (gmsh C3D10 on the placed bodies, SI units):
- thermal_transient needs settings.source: friction_brake; bodies [disc, pad] (settings.disc / settings.pad; the disc is on a rotating joint).
  Inputs: vehicleMass (kg), initialSpeed (m/s), deceleration (m/s2, positive), brakeStart, brakeEnd, endTime (s), brakeCount (brakes sharing
  the vehicle's heat), ambientTemperature and initialTemperature (K), <body>.density, <body>.conductivity, <body>.specificHeat,
  <body>.emissivity for both bodies, and filmCoefficient (W/m2K) or airConductivity, airDensity, airSpecificHeat, airViscosity (Pa s),
  convectionLength (m) for flat-plate forced convection at the vehicle speed; optional discHeatFraction (default: Charron's effusivity
  ratio); wheelRadius (m) adds the moving-source flash rise under the pad to the ring-averaged field (settings.flash: false omits it).
  Boundaries: one `contact` boundary on each body; `symmetry` boundaries are insulated; every other face convects and radiates.
  Settings: end_time, time_step (s), mesh_size_mm, contact_mesh_size_mm, line_radius_mm. Quantities: max_temperature (observable.body),
  time_of_max_temperature, line_max_temperature (observable.line), temperature (observable.location), produced_heat, stored_heat,
  dissipated_heat (J), hotspot_radius (unit m or mm).
- structural_static: one body; inputs <body>.youngsModulus (Pa), <body>.poissonRatio, <body>.density, pressure.<boundary> (Pa); `fixed`
  boundaries clamp; centrifugal load from the body's drive speed at the case. Quantities: max_displacement, displacement (location), mm.
- modal: as structural_static without loads; settings.modes; quantities natural_frequency_<k> (Hz)."""

CCX = os.environ.get("OPENCAD_CCX", "/Applications/FreeCAD.app/Contents/Resources/bin/ccx")
SIGMA = 5.670374419e-8
MM = 1e-3
SMOOTH_S = 0.1  # half-width of the speed-corner smoothing (COMSOL's 0.2 s transition zone)


def available() -> bool:
    return Path(CCX).exists()


def version() -> str:
    try:
        out = subprocess.run([CCX, "-v"], capture_output=True, text=True, timeout=30, check=False).stdout
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    m = re.search(r"Version\s+([\d.]+)", out)
    return m.group(1) if m else out.strip()[:40]


# ---------------------------------------------------------------------------------------------------------------- input deck

def _set(body: str) -> str:
    return f"E{re.sub(r'[^A-Za-z0-9]', '', body).upper()}"


def deck_mesh(mesh: Any) -> list[str]:
    lines = ["*HEADING", "opencad", "*NODE, NSET=NALL"]
    lines += [f"{int(n)},{x:.9e},{y:.9e},{z:.9e}" for n, (x, y, z) in zip(mesh.ids, mesh.nodes * MM)]
    for body, el in mesh.elements.items():
        lines.append(f"*ELEMENT, TYPE={'C3D10' if el.shape[1] == 10 else 'C3D4'}, ELSET={_set(body)}")
        lines += [f"{int(e)}," + ",".join(str(int(n)) for n in row) for e, row in zip(mesh.elem_ids[body], el)]
    return lines


def deck_material(body: str, props: dict[str, float]) -> list[str]:
    name = f"M{_set(body)[1:]}"
    out = [f"*MATERIAL, NAME={name}"]
    if "density" in props:
        out += ["*DENSITY", f"{props['density']:.9e}"]
    if "conductivity" in props:
        out += ["*CONDUCTIVITY", f"{props['conductivity']:.9e}"]
    if "specificHeat" in props:
        out += ["*SPECIFIC HEAT", f"{props['specificHeat']:.9e}"]
    if "youngsModulus" in props:
        out += ["*ELASTIC", f"{props['youngsModulus']:.9e},{props.get('poissonRatio', 0.3):.6f}"]
    return out + [f"*SOLID SECTION, ELSET={_set(body)}, MATERIAL={name}"]


def run_ccx(work: Path, deck: list[str], *, timeout: float = 7200) -> dict[str, Any]:
    work.mkdir(parents=True, exist_ok=True)
    (work / "job.inp").write_text("\n".join(deck) + "\n", encoding="utf-8")
    t0 = time.time()
    env = {**os.environ, "OMP_NUM_THREADS": str(min(8, os.cpu_count() or 2)), "CCX_NPROC_EQUATION_SOLVER": str(min(8, os.cpu_count() or 2))}
    with (work / "ccx.log").open("w", encoding="utf-8") as fh:
        try:
            code = subprocess.run([CCX, "-i", "job"], cwd=work, stdout=fh, stderr=subprocess.STDOUT, timeout=timeout, env=env, check=False).returncode
        except subprocess.TimeoutExpired:
            code = 124
    log = (work / "ccx.log").read_text(encoding="utf-8", errors="replace")
    ok = code == 0 and (work / "job.dat").exists() and "*ERROR" not in log
    return {"ok": ok, "code": code, "seconds": round(time.time() - t0, 1), "log_tail": log[-1500:] if not ok else ""}


def parse_dat(path: Path, what: str) -> dict[float, dict[int, np.ndarray]]:
    """Blocks of `<what> for set ... and time T` -> {time: {node or element: values}}."""
    out: dict[float, dict[int, np.ndarray]] = {}
    cur: dict[int, np.ndarray] | None = None
    head = re.compile(rf"^\s*{what}.*time\s+([-+0-9.Ee]+)")
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = head.match(line)
        if m:
            cur = out.setdefault(float(m.group(1)), {})
            continue
        if cur is None:
            continue
        parts = line.split()
        if not parts:
            continue
        try:
            cur[int(parts[0])] = np.asarray([float(x) for x in parts[1:]], float)
        except ValueError:
            cur = None
    return out


def parse_frequencies(path: Path) -> list[float]:
    text = path.read_text(encoding="utf-8", errors="replace")
    block = text.split("E I G E N V A L U E   O U T P U T", 1)
    if len(block) < 2:
        return []
    freqs = []
    for line in block[1].splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0].isdigit():
            try:
                freqs.append(float(parts[3]))
            except ValueError:
                continue
        elif freqs and not parts:
            break
    return freqs


# ------------------------------------------------------------------------------------------------------------- shared pieces

def _labels(geom: Any, bodies: list[str]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    out: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for b in bodies:
        for f in geom.boundaries(b).get("faces") or []:
            if f.get("label"):
                out.setdefault(b, {}).setdefault(f["label"], []).append(f)
    return out


def _roles(geom: Any, body: str) -> dict[str, str]:
    return {b.name: b.role for b in geom.contract.boundaries if b.body == body}


def _props(sim: Any, body: str, keys: tuple[str, ...]) -> dict[str, float]:
    out = {}
    for k in keys:
        iv = sim.inputs.get(f"{body}.{k}")
        if iv is not None:
            out[k] = float(iv.value)
    return out


def _v(sim: Any, key: str, default: float | None = None) -> float:
    if key in sim.inputs:
        return float(sim.inputs[key].value)
    if default is None:
        raise KeyError(f"simulation {sim.id}: input {key!r} is missing")
    return default


def _quadratic_weights(n: int) -> np.ndarray:
    """Integration weights of the element's nodal values over its volume (linear: 1/4 each; quadratic: -1/20 corners, 1/5 edges)."""
    return np.full(4, 0.25) if n == 4 else np.array([-0.05] * 4 + [0.2] * 6)


# --------------------------------------------------------------------------------------------------------- friction brake

def smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (6 * x - 15) + 10)


def brake_history(sim: Any, t: np.ndarray) -> dict[str, np.ndarray]:
    """Vehicle speed, deceleration and per-brake heat rate on the time grid (C2-smoothed corners)."""
    v0, dec = _v(sim, "initialSpeed"), _v(sim, "deceleration")
    ts, te = _v(sim, "brakeStart"), _v(sim, "brakeEnd")
    m, n = _v(sim, "vehicleMass"), _v(sim, "brakeCount", 1.0)
    on = smoothstep((t - (ts - SMOOTH_S)) / (2 * SMOOTH_S)) - smoothstep((t - (te - SMOOTH_S)) / (2 * SMOOTH_S))
    a = -abs(dec) * on
    v = v0 + np.concatenate([[0.0], np.cumsum((a[1:] + a[:-1]) / 2 * np.diff(t))])
    power = np.maximum(0.0, -m * v * a / n)
    return {"t": t, "v": v, "a": a, "power": power}


def film_coefficient(sim: Any, speed: np.ndarray) -> np.ndarray:
    """Averaged flat-plate forced convection (Churchill-Ozoe laminar, Re <= 5e5; turbulent above), or a constant filmCoefficient."""
    if "filmCoefficient" in sim.inputs:
        return np.full_like(speed, _v(sim, "filmCoefficient"))
    k, rho, cp, mu, length = (_v(sim, x) for x in ("airConductivity", "airDensity", "airSpecificHeat", "airViscosity", "convectionLength"))
    pr = cp * mu / k
    re_ = np.maximum(rho * np.abs(speed) * length / mu, 1e-9)
    lam = 2 * k / length * 0.3387 * pr ** (1 / 3) * np.sqrt(re_) / (1 + (0.0468 / pr) ** (2 / 3)) ** 0.25
    turb = 2 * k / length * pr ** (1 / 3) * (0.037 * re_ ** 0.8 - 871)
    return np.where(re_ <= 5e5, lam, turb)


def charron(sim: Any, disc: str, pad: str) -> float:
    if "discHeatFraction" in sim.inputs:
        return _v(sim, "discHeatFraction")
    e = {b: math.sqrt(_v(sim, f"{b}.conductivity") * _v(sim, f"{b}.density") * _v(sim, f"{b}.specificHeat")) for b in (disc, pad)}
    return e[disc] / (e[disc] + e[pad])


def pad_footprint(points: np.ndarray, o: np.ndarray, ax: np.ndarray, bins_mm: float = 1.0) -> dict[str, Any]:
    """The pad contact face in polar coordinates about the disc axis: per radius bin the angular span (relative to the pad's
    centre angle), from points sampled on its triangulation (mm)."""
    u = np.cross(ax, [1.0, 0.0, 0.0]) if abs(ax[0]) < 0.9 else np.cross(ax, [0.0, 1.0, 0.0])
    u /= np.linalg.norm(u)
    v = np.cross(ax, u)
    w = points - o
    r = np.linalg.norm(w - np.outer(w @ ax, ax), axis=1)
    th = np.arctan2(w @ v, w @ u)
    c = math.atan2(float(np.mean(np.sin(th))), float(np.mean(np.cos(th))))
    phi = (th - c + math.pi) % (2 * math.pi) - math.pi
    edges = np.arange(r.min(), r.max() + bins_mm, bins_mm)
    lo, hi, mid = [], [], []
    for a, b in zip(edges[:-1], edges[1:]):
        sel = (r >= a) & (r < b)
        if sel.sum() >= 2:
            lo.append(float(phi[sel].min()))
            hi.append(float(phi[sel].max()))
            mid.append((a + b) / 2)
    return {"u": u, "v": v, "centre": c, "r": np.asarray(mid), "phi_lo": np.asarray(lo), "phi_hi": np.asarray(hi), "r_in": float(r.min()), "r_out": float(r.max())}


def _sample_triangles(p: np.ndarray, n: int = 6) -> np.ndarray:
    """Points on each triangle (barycentric grid), for a dense footprint of a coarse contact mesh."""
    out = [p.reshape(-1, 3)]
    for i in range(1, n):
        for j in range(1, n - i):
            a, b = i / n, j / n
            out.append(p[:, 0] * (1 - a - b) + p[:, 1] * a + p[:, 2] * b)
    return np.vstack(out)


def flash_rise(fp: dict[str, Any], pts: np.ndarray, o: np.ndarray, ax: np.ndarray, *, power: np.ndarray, speed: np.ndarray, xi: float, a_pad: float,
               a_ring: float, e_disc: float, wheel: float, sense: float) -> np.ndarray:
    """Moving band-source rise [time, point] at disc surface points under the pad (Jaeger, high Peclet): the excess flux
    (q_pad - q_ring) acting for the time the point has spent under the pad at the local surface speed."""
    w = pts - o
    r = np.linalg.norm(w - np.outer(w @ ax, ax), axis=1)
    phi = (np.arctan2(w @ fp["v"], w @ fp["u"]) - fp["centre"] + math.pi) % (2 * math.pi) - math.pi
    lo, hi = np.interp(r, fp["r"], fp["phi_lo"]), np.interp(r, fp["r"], fp["phi_hi"])
    inside = (r >= fp["r_in"]) & (r <= fp["r_out"]) & (phi >= lo) & (phi <= hi)
    frac = np.clip(((phi - lo) if sense >= 0 else (hi - phi)) / np.maximum(hi - lo, 1e-9), 0.0, 1.0)
    dwell = np.where(inside, frac * np.maximum(hi - lo, 0.0) * r * MM, 0.0)  # arc length already travelled under the pad, m
    q = xi * power / a_pad * max(0.0, 1.0 - a_pad / a_ring)
    surf = np.maximum(np.abs(speed) / wheel, 1e-9)[:, None] * (r * MM)[None, :]
    return np.where((power > 0)[:, None] & inside[None, :], 2 * q[:, None] * np.sqrt(dwell[None, :] / (math.pi * surf)) / e_disc, 0.0)


def _output_times(t_end: float, ts: float, te: float) -> list[float]:
    pts = set(np.round(np.arange(0.0, t_end + 1e-9, 0.5), 4)) | set(np.round(np.arange(ts, min(te + 1.0, t_end) + 1e-9, 0.05), 4))
    return sorted(float(x) for x in pts if 0 < x <= t_end)


def thermal_transient(sim: Any, obs: list[Any], geom: Any, cases: dict[str, Any]) -> dict[str, Any]:
    from opencad.sim.mesh import check_tet10, tet_mesh

    if sim.settings.get("source") != "friction_brake":
        return unavailable("thermal_transient needs settings.source: friction_brake (the only heat source model implemented)")
    bodies = list(sim.bodies)
    disc = str(sim.settings.get("disc") or bodies[0])
    pad = str(sim.settings.get("pad") or next(b for b in bodies if b != disc))
    joint = geom.joint_of(disc)
    if joint is None or not joint.rotates:
        return unavailable(f"{disc} has no rotating joint: the pad's swept band is undefined")
    o, ax = geom.joint_axis(joint.name)
    labels = _labels(geom, [disc, pad])
    roles = {b: _roles(geom, b) for b in (disc, pad)}
    contact = {b: [lab for lab, r in roles[b].items() if r == "contact"] for b in (disc, pad)}
    if not contact[disc] or not contact[pad]:
        return unavailable("friction_brake needs a `contact` boundary on both the disc and the pad")
    t_end = float(sim.settings.get("end_time") or _v(sim, "endTime", 12.0))
    dt0 = float(sim.settings.get("time_step", 0.05))
    h0 = float(sim.settings.get("mesh_size_mm", 6.0))
    hc0 = float(sim.settings.get("contact_mesh_size_mm", 1.5))
    t_amb = _v(sim, "ambientTemperature")
    t0 = _v(sim, "initialTemperature", t_amb)
    xi = charron(sim, disc, pad)
    grid = np.arange(0.0, t_end + 1e-9, 0.005)
    hist = brake_history(sim, grid)
    hfilm = film_coefficient(sim, hist["v"])
    p_ref, h_ref = float(hist["power"].max()), float(hfilm.max())
    ts, te = _v(sim, "brakeStart"), _v(sim, "brakeEnd")
    times = _output_times(t_end, ts, te)
    levels: dict[str, list[float]] = {}
    runs = []
    rows_by_level = []
    work_root = geom.work_dir(sim.id)
    for f in (lv.factor for lv in sim.levels()):
        work = work_root / f"level-{f:g}"
        mesh = tet_mesh({disc: geom.step(disc), pad: geom.step(pad)}, labels, size=h0 * f, size_min=hc0 * f,
                        refine={f"{disc}:{contact[disc][0]}": hc0 * f, f"{pad}:{contact[pad][0]}": hc0 * f})
        if any(mesh.unmatched.values()):
            return failed(f"gmsh surfaces did not match boundary faces: {mesh.unmatched}")
        pad_nodes = mesh.coords(mesh.surface_nodes(f"{pad}:{contact[pad][0]}")) - o
        radial = np.linalg.norm(pad_nodes - np.outer(pad_nodes @ ax, ax), axis=1)
        r_in, r_out = float(radial.min()), float(radial.max())
        key_d = f"{disc}:{contact[disc][0]}"
        tri_c = mesh.coords(mesh.tris[key_d]).mean(axis=1) - o
        tri_r = np.linalg.norm(tri_c - np.outer(tri_c @ ax, ax), axis=1)
        band = (tri_r >= r_in) & (tri_r <= r_out)
        a_band = float(mesh.tri_areas(key_d)[band].sum()) * MM * MM
        key_p = f"{pad}:{contact[pad][0]}"
        a_pad = float(mesh.tri_areas(key_p).sum()) * MM * MM
        q_disc, q_pad = xi * p_ref / a_band, (1 - xi) * p_ref / a_pad
        eps = {b: _v(sim, f"{b}.emissivity", 0.0) for b in (disc, pad)}
        deck = deck_mesh(mesh)
        for b in (disc, pad):
            deck += deck_material(b, _props(sim, b, ("density", "conductivity", "specificHeat")))
        deck += ["*PHYSICAL CONSTANTS, ABSOLUTE ZERO=0., STEFAN BOLTZMANN=5.670374419E-8", "*INITIAL CONDITIONS, TYPE=TEMPERATURE", f"NALL,{t0:.6f}"]
        deck += ["*AMPLITUDE, NAME=APOWER"] + [f"{t:.5f},{p / p_ref:.9e}" for t, p in zip(grid[::4], hist["power"][::4])]
        deck += ["*AMPLITUDE, NAME=AFILM"] + [f"{t:.5f},{h / h_ref:.9e}" for t, h in zip(grid[::4], hfilm[::4])]
        deck += ["*TIME POINTS, NAME=TP"] + [f"{t:.5f}" for t in times]
        dt = dt0 * f
        deck += ["*STEP, INC=100000", f"*HEAT TRANSFER, SOLVER={sim.settings.get('solver', 'ITERATIVE CHOLESKY')}",
                 f"{dt:.6f},{t_end:.6f},{dt / 100:.8f},{dt:.6f}", "*DFLUX, AMPLITUDE=APOWER"]
        deck += [f"{e},S{k},{q_disc:.9e}" for (e, k), inb in zip(mesh.faces[key_d], band) if inb]
        deck += [f"{e},S{k},{q_pad:.9e}" for e, k in mesh.faces[key_p]]
        exposed = {b: [lab for lab, r in roles[b].items() if r != "symmetry" and not (b == pad and lab in contact[pad])] for b in (disc, pad)}
        deck += ["*FILM, FILM AMPLITUDE=AFILM"]
        for b in (disc, pad):
            for lab in exposed[b]:
                deck += [f"{e},F{k},{t_amb:.6f},{h_ref:.9e}" for e, k in mesh.faces.get(f"{b}:{lab}", [])]
        deck += ["*RADIATE"]
        for b in (disc, pad):
            if eps[b] > 0:
                for lab in exposed[b]:
                    deck += [f"{e},R{k},{t_amb:.6f},{eps[b]:.6f}" for e, k in mesh.faces.get(f"{b}:{lab}", [])]
        deck += ["*NODE PRINT, NSET=NALL, TIME POINTS=TP", "NT", "*END STEP"]
        r = run_ccx(work, deck)
        runs.append({"level": f, "mesh": mesh.size, "tet10_midnode_error": check_tet10(mesh, disc), "dt": dt, "band_mm": [r_in, r_out],
                     "band_area_m2": a_band, "pad_area_m2": a_pad, **r})
        if not r["ok"]:
            return failed(f"ccx failed at refinement {f}: {r['log_tail'][-600:]}", runs=runs)
        temps = parse_dat(work / "job.dat", "temperatures")
        flash = None
        if sim.settings.get("flash", True) and "wheelRadius" in sim.inputs:
            fp = pad_footprint(_sample_triangles(mesh.coords(mesh.tris[key_p])), o, ax)
            d = joint.drive
            speeds = [s for _, s in (d.history if d is not None else [])] or ([d.speed] if d is not None and d.speed is not None else [1.0])
            flash = {"fp": fp, "key": key_d, "xi": xi, "a_pad": a_pad, "a_ring": math.pi * (r_out ** 2 - r_in ** 2) * MM * MM, "wheel": _v(sim, "wheelRadius"),
                     "e": math.sqrt(_v(sim, f"{disc}.conductivity") * _v(sim, f"{disc}.density") * _v(sim, f"{disc}.specificHeat")),
                     "sense": 1.0 if float(np.mean(speeds)) >= 0 else -1.0}
        row = _brake_observables(sim, obs, mesh, temps, disc, pad, exposed, eps, hist, hfilm, grid, t0, t_amb, o, ax, flash)
        rows_by_level.append(row)
        for k, v in row["values"].items():
            levels.setdefault(k, []).append(v)
    last = rows_by_level[-1]
    out_obs, ref = _studies(sim, [ob for ob in obs if levels.get(ob.id)], levels)
    for ob in obs:
        if not levels.get(ob.id):
            out_obs[ob.id] = observable(None, ob.unit, case=ob.case, note=f"quantity {ob.quantity!r} is not computed by friction_brake")
    tol = float(sim.settings.get("energy_balance_tolerance", 0.03))
    residual = last["energy"]["residual_rel"]
    return {"status": "ok", "solver": {"name": "calculix", "version": version(), "binary": CCX}, "model": "transient heat conduction, friction_brake source",
            "observables": out_obs, "conservation": {"energy_balance": {"value": residual, "tolerance": tol, "ok": abs(residual) <= tol, **last["energy"]}},
            "refinement": ref,
            "series": last["series"], "runs": runs, "heat_fraction_disc": xi, "peak_power_w": p_ref, "peak_film_w_m2k": h_ref, "peak_flash_K": last["peak_flash_K"],
            "assumptions": ["heat source ring-averaged over the band the pad sweeps on the disc; under the pad the moving band-source flash rise "
                            "(Jaeger, high Peclet, excess flux q_pad - q_ring, wheelRadius sets the surface speed) is superposed on the mean field"
                            if last["peak_flash_K"] else "heat source ring-averaged over the band the pad sweeps on the disc (no flash term: settings.flash off or no wheelRadius)",
                            "no conduction across the pad/disc interface; the friction heat is split by Charron's effusivity ratio",
                            "forced convection on every non-symmetry face including the disc band; the pad's contact face is insulated",
                            f"speed corners smoothed over {2 * SMOOTH_S:g} s"]}


def _brake_observables(sim, obs, mesh, temps, disc, pad, exposed, eps, hist, hfilm, grid, t0, t_amb, o, ax, flash=None) -> dict[str, Any]:
    tt = np.array(sorted(temps))
    idx = mesh.index()
    temp = np.array([[temps[t].get(int(n), np.array([np.nan]))[0] for n in mesh.ids] for t in tt])
    surf = temp.copy()  # the disc surface under the pad also carries the flash rise; energy bookkeeping keeps the mean field
    peak_flash = 0.0
    if flash is not None:
        cnodes = mesh.surface_nodes(flash["key"])
        ccol = np.array([idx[int(n)] for n in cnodes])
        rise = flash_rise(flash["fp"], mesh.nodes[ccol], o, ax, power=np.interp(tt, grid, hist["power"]), speed=np.interp(tt, grid, hist["v"]), xi=flash["xi"],
                          a_pad=flash["a_pad"], a_ring=flash["a_ring"], e_disc=flash["e"], wheel=flash["wheel"], sense=flash["sense"])
        surf[:, ccol] += rise
        peak_flash = float(rise.max()) if rise.size else 0.0
    nodes_of = {b: np.unique(mesh.elements[b]) for b in (disc, pad)}
    col = {b: np.array([idx[int(n)] for n in nodes_of[b]]) for b in (disc, pad)}
    stored = np.zeros(len(tt))
    for b in (disc, pad):
        rho, cp = _v(sim, f"{b}.density"), _v(sim, f"{b}.specificHeat")
        vol = mesh.tet_volumes(b) * MM ** 3
        w = _quadratic_weights(mesh.elements[b].shape[1])
        el_idx = np.vectorize(lambda n: idx[int(n)])(mesh.elements[b])
        tbar = (temp[:, el_idx] - t0) @ w
        stored += rho * cp * (tbar * vol).sum(axis=1)
    produced = np.interp(tt, grid, np.concatenate([[0.0], np.cumsum((hist["power"][1:] + hist["power"][:-1]) / 2 * np.diff(grid))]))
    loss_rate = np.zeros(len(tt))
    h_t = np.interp(tt, grid, hfilm)
    for b in (disc, pad):
        for lab in exposed[b]:
            key = f"{b}:{lab}"
            if key not in mesh.tris:
                continue
            area = mesh.tri_areas(key) * MM * MM
            tri_idx = np.vectorize(lambda n: idx[int(n)])(mesh.tris[key])
            ts_ = temp[:, tri_idx].mean(axis=2)
            loss_rate += (h_t[:, None] * (ts_ - t_amb) * area).sum(axis=1) + (eps[b] * SIGMA * (ts_ ** 4 - t_amb ** 4) * area).sum(axis=1)
    tq = np.concatenate([[0.0], tt])
    lr = np.concatenate([[0.0], loss_rate])
    dissipated = np.concatenate([[0.0], np.cumsum((lr[1:] + lr[:-1]) / 2 * np.diff(tq))])[1:]
    residual = (produced[-1] - stored[-1] - dissipated[-1]) / produced[-1] if produced[-1] else 0.0
    tmax_d = np.nanmax(surf[:, col[disc]], axis=1)
    tmax_mean = np.nanmax(temp[:, col[disc]], axis=1)
    tmax_p = np.nanmax(temp[:, col[pad]], axis=1)
    k_star = int(np.nanargmax(tmax_d))
    # the weighted radius of the hottest 2 % of the rise converges under refinement where a single node's radius jumps by a spacing
    t_star = surf[k_star, col[disc]]
    floor = tmax_d[k_star] - 0.02 * (tmax_d[k_star] - float(np.nanmin(t_star)))
    w = np.clip(np.nan_to_num(t_star - floor, nan=0.0), 0.0, None)
    rel = mesh.nodes[col[disc]] - o
    radial = np.linalg.norm(rel - np.outer(rel @ ax, ax), axis=1)
    hot_radius = float((w * radial).sum() / w.sum()) if w.sum() > 0 else float(radial[int(np.nanargmax(t_star))])
    values: dict[str, float] = {}
    for ob in obs:
        q = ob.quantity
        body = ob.body or disc
        series = tmax_d if body == disc else tmax_p
        if q == "max_temperature":
            values[ob.id] = float(np.nanmax(series)) if ob.body else float(max(np.nanmax(tmax_d), np.nanmax(tmax_p)))
        elif q == "time_of_max_temperature":
            values[ob.id] = float(tt[int(np.nanargmax(series))])
        elif q in ("produced_heat", "stored_heat", "dissipated_heat"):
            values[ob.id] = float({"produced_heat": produced, "stored_heat": stored, "dissipated_heat": dissipated}[q][-1])
        elif q == "hotspot_radius":
            values[ob.id] = hot_radius * (MM if ob.unit == "m" else 1.0)
        elif q in ("temperature", "line_max_temperature") and (ob.location is not None or ob.line is not None):
            pts = mesh.nodes[col[body]]
            if ob.line is not None:
                a, b_ = np.asarray(ob.line[0], float), np.asarray(ob.line[1], float)
                d = b_ - a
                s = np.clip(((pts - a) @ d) / (d @ d), 0, 1)
                dist = np.linalg.norm(pts - (a + np.outer(s, d)), axis=1)
                near = col[body][dist <= float(sim.settings.get("line_radius_mm", 1.5))]
            else:
                near = col[body][[int(np.argmin(np.linalg.norm(pts - np.asarray(ob.location, float), axis=1)))]]
            if len(near) == 0:
                continue
            tl = np.nanmax((surf if body == disc else temp)[:, near], axis=1)
            values[ob.id] = float(tl[-1] if ob.averaging == "final" else np.nanmax(tl))
    return {"values": values, "energy": {"produced_j": float(produced[-1]), "stored_j": float(stored[-1]), "dissipated_j": float(dissipated[-1]),
                                         "residual_rel": float(residual)}, "peak_flash_K": peak_flash,
            "series": {"t_s": tt.tolist(), f"max_T_{disc}_K": tmax_d.tolist(), f"max_T_{disc}_mean_field_K": tmax_mean.tolist(), f"max_T_{pad}_K": tmax_p.tolist(),
                       "produced_J": produced.tolist(), "stored_J": stored.tolist(), "dissipated_J": dissipated.tolist()}}


# ------------------------------------------------------------------------------------------------------- structural and modal

def _fixed_nodes(mesh: Any, geom: Any, body: str) -> np.ndarray:
    labs = [lab for lab, r in _roles(geom, body).items() if r == "fixed"]
    return np.unique(np.concatenate([mesh.surface_nodes(f"{body}:{lab}") for lab in labs])) if labs else np.array([], int)


def _solid_deck(sim: Any, geom: Any, body: str, size: float) -> tuple[Any, list[str], np.ndarray]:
    from opencad.sim.mesh import tet_mesh

    mesh = tet_mesh({body: geom.step(body)}, _labels(geom, [body]), size=size)
    fixed = _fixed_nodes(mesh, geom, body)
    deck = deck_mesh(mesh) + deck_material(body, _props(sim, body, ("density", "youngsModulus", "poissonRatio")))
    deck += ["*NSET, NSET=NFIXED"] + [",".join(str(int(n)) for n in fixed[i:i + 12]) for i in range(0, len(fixed), 12)]
    deck += ["*BOUNDARY", "NFIXED,1,3"]
    return mesh, deck, fixed


def structural_static(sim: Any, obs: list[Any], geom: Any, cases: dict[str, Any]) -> dict[str, Any]:
    body = sim.bodies[0]
    case = cases.get(sim.cases[0]) if sim.cases else None
    h0 = float(sim.settings.get("mesh_size_mm", 3.0))
    levels: dict[str, list[float]] = {}
    runs = []
    for f in (lv.factor for lv in sim.levels()):
        mesh, deck, fixed = _solid_deck(sim, geom, body, h0 * f)
        if len(fixed) == 0:
            return unavailable(f"{body} has no `fixed` boundary: the static problem is singular")
        deck += ["*STEP", "*STATIC"]
        j = geom.joint_of(body)
        if j is not None and j.rotates and j.drive is not None:
            rpm = j.drive.speed if j.drive.speed is not None else (case.values.get(j.drive.case_value) if case and j.drive.case_value else None)
            if rpm:
                o, ax = geom.joint_axis(j.name)
                w = rpm * 2 * math.pi / 60
                deck += ["*DLOAD", f"{_set(body)},CENTRIF,{w * w:.9e},{o[0] * MM:.9e},{o[1] * MM:.9e},{o[2] * MM:.9e},{ax[0]:.9f},{ax[1]:.9f},{ax[2]:.9f}"]
        for key, iv in sim.inputs.items():
            if key.startswith("pressure."):
                lab = key.split(".", 1)[1]
                deck += ["*DLOAD"] + [f"{e},P{k},{float(iv.value):.9e}" for e, k in mesh.faces.get(f"{body}:{lab}", [])]
        deck += ["*NODE PRINT, NSET=NALL", "U", "*END STEP"]
        r = run_ccx(geom.work_dir(sim.id) / f"level-{f:g}", deck)
        runs.append({"level": f, "mesh": mesh.size, **r})
        if not r["ok"]:
            return failed(f"ccx failed: {r['log_tail'][-600:]}", runs=runs)
        disp = parse_dat(geom.work_dir(sim.id) / f"level-{f:g}" / "job.dat", "displacements")
        u = next(iter(disp.values())) if disp else {}
        mags = {n: float(np.linalg.norm(v[:3])) / MM for n, v in u.items()}
        for ob in obs:
            if ob.quantity == "max_displacement":
                levels.setdefault(ob.id, []).append(max(mags.values(), default=float("nan")))
            elif ob.quantity == "displacement" and ob.location is not None:
                k = int(np.argmin(np.linalg.norm(mesh.nodes - np.asarray(ob.location, float), axis=1)))
                levels.setdefault(ob.id, []).append(mags.get(int(mesh.ids[k]), float("nan")))
    return _pack(sim, obs, levels, runs, ["linear elastic, small displacement", "fixed boundaries clamp all three translations"])


def modal(sim: Any, obs: list[Any], geom: Any, cases: dict[str, Any]) -> dict[str, Any]:
    body = sim.bodies[0]
    h0 = float(sim.settings.get("mesh_size_mm", 5.0))
    n = int(sim.settings.get("modes", 10))
    levels: dict[str, list[float]] = {}
    runs = []
    for f in (lv.factor for lv in sim.levels()):
        mesh, deck, _ = _solid_deck(sim, geom, body, h0 * f)
        deck += ["*STEP", "*FREQUENCY", f"{n}", "*END STEP"]
        r = run_ccx(geom.work_dir(sim.id) / f"level-{f:g}", deck)
        runs.append({"level": f, "mesh": mesh.size, **r})
        if not r["ok"]:
            return failed(f"ccx failed: {r['log_tail'][-600:]}", runs=runs)
        freqs = parse_frequencies(geom.work_dir(sim.id) / f"level-{f:g}" / "job.dat")
        for ob in obs:
            m = re.match(r"natural_frequency_(\d+)$", ob.quantity)
            if m and int(m.group(1)) <= len(freqs):
                levels.setdefault(ob.id, []).append(freqs[int(m.group(1)) - 1])
    return _pack(sim, obs, levels, runs, ["linear modal analysis about the unloaded state", "fixed boundaries clamp all three translations"])


def _pack(sim: Any, obs: list[Any], levels: dict[str, list[float]], runs: list[dict[str, Any]], assumptions: list[str]) -> dict[str, Any]:
    out, ref = _studies(sim, obs, levels)
    return {"status": "ok", "solver": {"name": "calculix", "version": version(), "binary": CCX}, "model": sim.physics, "observables": out, "runs": runs,
            "refinement": ref, "assumptions": assumptions}


def run(sim: Any, obs: list[Any], geom: Any, cases: dict[str, Any]) -> dict[str, Any]:
    if not available():
        return unavailable(f"CalculiX not found at {CCX} (OPENCAD_CCX)")
    fn = {"thermal_transient": thermal_transient, "structural_static": structural_static, "modal": modal}.get(sim.physics)
    if fn is None:
        return unavailable(f"physics {sim.physics} is not implemented in the CalculiX adapter")
    return fn(sim, obs, geom, cases)

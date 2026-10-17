#!/usr/bin/env python
"""Analytic references for the kinematic machine cases (evaluator side; numpy only, no CAD):

- compound-train: 20T pinion -> 40T/15T compound idler -> 45T output, module 2; train ratio (-20/40)(-15/45) = +1/6.
- planetary-set: fixed internal 48T ring, 24T sun, three 12T planets on a carrier, module 2; carrier/sun = 24/(24+48) = 1/3.
- rack-pinion: 20T module-2 pinion on a straight-flank rack; pi m z / 360 mm per degree; rack volume from its trapezoid teeth.
- four-bar: ground 100, crank 40, coupler 100, rocker 80 (Grashof crank-rocker); rocker angle and a coupler point over one
  crank turn by circle intersection on the assembled (open) branch.
- crank-slider: crank 30, rod 100, pin line offset 10; slider travel x(theta) - x(0) and the stroke.

Every value is from rest (the configuration the specifications state), degrees positive about +z. Writes each case's
truth/*.csv series and truth/<case>-truth.yaml; run `python -m opencad.truth pin <case>` afterwards.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import yaml

CASES = Path(__file__).resolve().parents[1] / "truth" / "cases"
STEP_DEG = 10.0  # reference series spacing; the prediction is interpolated onto it


def stadium_volume(length: float, width: float = 16.0, thick: float = 5.0, hole_d: float = 6.0, holes: int = 2) -> float:
    return thick * (length * width + math.pi * (width / 2) ** 2 - holes * math.pi * (hole_d / 2) ** 2)


def mesh_phase(z_a: int, z_b: int, alpha: float, psi: float = 0.0) -> float:
    """Rest angle (deg, modulo B's pitch) of B's tooth pattern (a tooth on its own +x) so that B, centred in direction psi from
    A, meshes with A whose pattern is turned alpha: B's tooth centre at psi + 180 + 180/z_b - (alpha - psi) z_a / z_b."""
    beta = psi + 180.0 + 180.0 / z_b - (alpha - psi) * z_a / z_b
    return beta % (360.0 / z_b)


def write_series(path: Path, header: list[str], rows: list[list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows([[f"{v:.9f}" for v in r] for r in rows])


def dump(case: str, data: dict) -> None:
    p = CASES / case / "truth" / f"{case}-truth.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump(data, sort_keys=False, width=120), encoding="utf-8")
    print(f"{case}: {data}")


def compound_train() -> None:
    idler = mesh_phase(20, 40, 0.0)
    output = mesh_phase(15, 45, idler)
    dump("compound-train", {"ratio": (-20 / 40) * (-15 / 45), "output_at_pinion_360_deg": 360.0 * (-20 / 40) * (-15 / 45),
                            "idler_rest_deg": idler, "output_rest_deg": output, "centre_distances_mm": [60.0, 60.0],
                            "volumes_mm3": {"plate": 195 * 100 * 5 - math.pi * (3 ** 2 + 2 * 4 ** 2) * 5}})


def planetary_set() -> None:
    zs, zp, zr = 24, 12, 48
    planet = mesh_phase(zs, zp, 0.0, 0.0)
    for k in (1, 2):  # the same absolute phase meshes every planet with the sun and puts a ring tooth in each planet's space
        assert abs(mesh_phase(zs, zp, 0.0, 120.0 * k) - planet) < 1e-9
        assert abs(((120.0 * k - planet) / (360 / zp)) % 1 - 0.5) < 1e-9 and ((120.0 * k) / (360 / zr)) % 1 < 1e-9
    ratio = zs / (zs + zr)
    dump("planetary-set", {"carrier_ratio": ratio, "carrier_at_sun_360_deg": 360.0 * ratio, "planet_rest_deg": planet,
                           "orbit_radius_mm": (zs + zp) * 2 / 2, "planet_relative_per_sun_deg": -(zs / zp) * (1 - ratio),
                           "assembly_condition": (zs + zr) / 3,
                           "planet_axes_mm": [[36.0 * math.cos(math.radians(120 * k)), 36.0 * math.sin(math.radians(120 * k))] for k in range(3)],
                           "volumes_mm3": {"plate": 150 * 150 * 5 - math.pi * 5 ** 2 * 5, "carrier": math.pi * 5 * (44 ** 2 - 5 ** 2 - 3 * 4 ** 2)}})


def rack_pinion() -> None:
    m, z, alpha, backlash = 2.0, 20, math.radians(20.0), 0.05
    p = math.pi * m
    t_pitch = p / 2 - backlash
    tip = t_pitch - 2 * m * math.tan(alpha)
    root = t_pitch + 2 * 1.25 * m * math.tan(alpha)
    teeth, length, body = 32, 200.0, 9.5
    area = length * body + teeth * (tip + root) / 2 * (2.25 * m)
    dump("rack-pinion", {"mm_per_deg": p * z / 360.0, "travel_per_turn_mm": p * z, "rack_volume_mm3": area * 8.0,
                         "tooth_tip_width_mm": tip, "tooth_root_width_mm": root, "pitch_mm": p,
                         "volumes_mm3": {"plate": 240 * 80 * 5 - math.pi * 3 ** 2 * 5}})


def four_bar() -> None:
    a, b, c, d = 40.0, 100.0, 80.0, 100.0
    p_local = np.array([50.0, 30.0])

    def pose(t2: float) -> tuple[np.ndarray, np.ndarray, float, float]:
        pa = np.array([a * math.cos(math.radians(t2)), a * math.sin(math.radians(t2))])
        dv = np.array([d, 0.0]) - pa
        n = float(np.linalg.norm(dv))
        along = (b ** 2 - c ** 2 + n ** 2) / (2 * n)
        pb = pa + along * dv / n + math.sqrt(b ** 2 - along ** 2) * np.array([-dv[1], dv[0]]) / n
        return pa, pb, math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0])), math.degrees(math.atan2(pb[1], pb[0] - d))

    _, _, t3_0, t4_0 = pose(0.0)

    def point(t2: float) -> np.ndarray:
        pa, _, t3, _ = pose(t2)
        c3, s3 = math.cos(math.radians(t3)), math.sin(math.radians(t3))
        return pa + np.array([c3 * p_local[0] - s3 * p_local[1], s3 * p_local[0] + c3 * p_local[1]])

    qs = np.arange(0.0, 360.0 + 1e-9, STEP_DEG)
    rocker = [pose(q)[3] - t4_0 for q in qs]
    fine = [pose(q)[3] - t4_0 for q in np.linspace(0.0, 360.0, 360001)]
    write_series(CASES / "four-bar" / "truth" / "rocker-angle.csv", ["crank_deg", "rocker_deg"], [[q, r] for q, r in zip(qs, rocker)])
    write_series(CASES / "four-bar" / "truth" / "coupler-point.csv", ["crank_deg", "x_mm", "y_mm"], [[q, *point(q)] for q in qs])
    s = a + b
    dump("four-bar", {"coupler_rest_deg": t3_0, "rocker_rest_deg": t4_0, "rocker_swing_deg": max(fine) - min(fine),
                      "coupler_point_rest_mm": point(0.0).tolist(), "grashof": s <= b + c and a == min(a, b, c, d),
                      "volumes_mm3": {"crank": stadium_volume(a), "coupler": stadium_volume(b), "rocker": stadium_volume(c),
                                      "ground": 160 * 60 * 5 - 2 * math.pi * 9 * 5}})


def crank_slider() -> None:
    r, l, e = 30.0, 100.0, 10.0

    def x(t: float) -> float:
        t = math.radians(t)
        return r * math.cos(t) + math.sqrt(l ** 2 - (e - r * math.sin(t)) ** 2)

    x0 = x(0.0)
    qs = np.arange(0.0, 360.0 + 1e-9, STEP_DEG)
    write_series(CASES / "crank-slider" / "truth" / "slider-travel.csv", ["crank_deg", "travel_mm"], [[q, x(q) - x0] for q in qs])
    dump("crank-slider", {"pin_rest_mm": [x0, e], "rod_rest_deg": math.degrees(math.atan2(e, x0 - r)),
                          "stroke_mm": math.sqrt((l + r) ** 2 - e ** 2) - math.sqrt((l - r) ** 2 - e ** 2),
                          "travel_range_mm": [min(x(q) for q in np.linspace(0, 360, 360001)) - x0, max(x(q) for q in np.linspace(0, 360, 360001)) - x0],
                          "volumes_mm3": {"crank": stadium_volume(r), "rod": stadium_volume(l), "slider": 30 * 16 * 5 - math.pi * 9 * 5,
                                          "ground": 200 * 70 * 5 - math.pi * 9 * 5}})


if __name__ == "__main__":
    compound_train()
    planetary_set()
    rack_pinion()
    four_bar()
    crank_slider()

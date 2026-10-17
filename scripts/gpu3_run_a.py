"""Run A for GPU-3: the reduced Stirling model on the stated engine dimensions against the stated brake-power anchors.

    python scripts/gpu3_run_a.py
"""

from __future__ import annotations

from pathlib import Path

import yaml

from opencad.sim.reduced.stirling_schmidt import schmidt, volumes

HP_W = 745.7
PSI_PA = 6894.76
HELIUM_R = 2077.0


def kelvin(f: float) -> float:
    return (f - 32) * 5 / 9 + 273.15


def main() -> None:
    a = yaml.safe_load((Path(__file__).resolve().parents[1] / "truth/cases/gpu3-stirling/truth/anchors.yaml").read_text(encoding="utf-8"))
    e = a["engine"]
    t, ve, vc = volumes(e["cylinder_bore_cm"] * 1e-2, e["displacer_rod_diameter_cm"] * 1e-2, e["crank_radius_cm"] * 1e-2, e["connecting_rod_length_cm"] * 1e-2,
                        e["eccentricity_cm"] * 1e-2, e["expansion_clearance_cm3"] * 1e-6, e["compression_clearance_cm3"] * 1e-6)
    print(f"swept expansion {(ve.max() - ve.min()) * 1e6:.2f} cm3, swept compression {(vc.max() - vc.min()) * 1e6:.2f} cm3")
    for p in a["points"]:
        r = schmidt(t, ve, vc, e["heater_dead_cm3"] * 1e-6, e["regenerator_dead_cm3"] * 1e-6, e["cooler_dead_cm3"] * 1e-6, kelvin(p["heater_gas_F"]),
                    kelvin(p["water_inlet_F"]), p["mean_pressure_psi"] * PSI_PA, HELIUM_R)
        ind = r["work_j"] * p["speed_rpm"] / 60
        brake = p["brake_hp"] * HP_W
        print(f"{p['gas']} {p['mean_pressure_psi']} psi {p['speed_rpm']} rpm: Schmidt indicated {ind / 1e3:.2f} kW, measured brake {brake / 1e3:.2f} kW, "
              f"ratio {ind / brake:.2f}, pressure ratio {r['pressure_ratio']:.3f}")


if __name__ == "__main__":
    main()

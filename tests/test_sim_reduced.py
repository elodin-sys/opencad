"""Reduced models on synthetic inputs: the Reynolds film solver and the Euler pump head."""

import math
from types import SimpleNamespace

import numpy as np
import pytest

from opencad.sim.reduced import pump_euler
from opencad.sim.reduced.reynolds_film import Film, walther


def test_walther_reproduces_the_stated_viscosities():
    nu = walther(26.98, 5.28)
    assert nu(40.0) == pytest.approx(26.98, rel=1e-9) and nu(100.0) == pytest.approx(5.28, rel=1e-9)
    assert nu(30.0) > nu(40.0) > nu(60.0)


def test_film_balances_the_load_with_cavitation():
    f = Film(0.05, 1e-4, 0.075, math.radians(-90), math.radians(90), 61, 15)
    ecc, alpha, p = f.balance(10e3, 0.025, 3000 * 2 * math.pi / 60)
    fb, ft = f.forces(p)
    assert fb == pytest.approx(10e3, rel=1e-3) and abs(ft) < 10.0
    assert 0 < ecc < 1 and 0 < math.degrees(alpha) < 90
    assert p.min() >= 0 and not p[0].any() and not p[-1].any() and not p[:, 0].any() and not p[:, -1].any()
    assert (p[np.argmin(f.h(f.th, ecc, alpha)) + 5:] == 0).any(), "the diverging film ruptures"


def test_rhombic_drive_swept_volumes_match_gpu3():
    from opencad.sim.reduced.stirling_schmidt import schmidt, volumes

    t, ve, vc = volumes(69.9e-3, 9.52e-3, 13.8e-3, 46.0e-3, 20.8e-3, 12.5e-6, 21.18e-6)
    assert (ve.max() - ve.min()) * 1e6 == pytest.approx(120.82, abs=0.05)
    assert (vc.max() - vc.min()) * 1e6 == pytest.approx(114.14, abs=0.05)
    r = schmidt(t, ve, vc, 80.8e-6, 65.5e-6, 13.13e-6, 922.0, 286.0, 2.76e6, 2077.0)
    assert r["work_j"] > 0 and r["p_min_pa"] < 2.76e6 < r["p_max_pa"]


def test_pump_euler_radial_blades():
    inputs = {k: SimpleNamespace(value=v, uncertainty=u) for k, v, u in
              (("fluidDensity", 1000.0, None), ("bladeCount", 4.0, None), ("bladeOutletAngle", 90.0, None), ("bladeOutletWidth", 3.0, None),
               ("hydraulicEfficiency", 0.6, 0.1))}
    sim = SimpleNamespace(settings={"flow_key": "q", "speed_key": "n"}, bodies=["rotor"], inputs=inputs)
    geom = SimpleNamespace(joint_of=lambda b: SimpleNamespace(rotates=True), radial_extent=lambda b: (0.0, 26.0))
    ob = SimpleNamespace(id="dp", quantity="pressure_rise", unit="Pa", case="c")
    r = pump_euler.run(sim, [ob], geom, {"c": SimpleNamespace(values={"q": 6.0, "n": 3500.0})})
    u2 = 3500 * 2 * math.pi / 60 * 0.026
    sigma = 1 - 1 / 4 ** 0.7
    got = r["observables"]["dp"]
    assert got["value"] == pytest.approx(0.6 * 1000 * sigma * u2 ** 2, rel=1e-9)
    assert got["u_input"] == pytest.approx(got["value"] / 6, rel=1e-9)

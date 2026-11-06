"""CalculiX structural_static and modal decks on a 100 x 10 x 10 mm steel cantilever against beam theory: the fixed root face
holds every node of its quadratic tetrahedra."""

import math
from types import SimpleNamespace

import numpy as np
import pytest

from opencad.sim import calculix

E, NU, RHO, L, B = 200e9, 0.3, 7800.0, 0.1, 0.01


@pytest.mark.skipif(not calculix.available(), reason="ccx not installed")
def test_a_fixed_face_holds_its_mid_edge_nodes_and_the_cantilever_matches_beam_theory(tmp_path):
    from build123d import Align, Box, export_step

    step = tmp_path / "beam.step"
    export_step(Box(100, 10, 10, align=(Align.MIN, Align.CENTER, Align.CENTER)), str(step))
    root = {"label": "root", "id": 1, "centroid": [0.0, 0.0, 0.0], "area": 100.0}
    geom = SimpleNamespace(step=lambda b: step, boundaries=lambda b: {"faces": [root]},
                           contract=SimpleNamespace(boundaries=[SimpleNamespace(name="root", role="fixed", body="beam")]))
    sim = SimpleNamespace(inputs={f"beam.{k}": SimpleNamespace(value=v) for k, v in (("density", RHO), ("youngsModulus", E), ("poissonRatio", NU))})
    mesh, deck, fixed = calculix._solid_deck(sim, geom, "beam", 2.5)
    assert set(fixed) == set(mesh.ids[np.abs(mesh.nodes[:, 0]) < 1e-6])

    w = 44000 * 2 * math.pi / 60
    spin = ["*STEP", "*STATIC", "*DLOAD", f"{calculix._set('beam')},CENTRIF,{w * w:.9e},0,0,0,0,0,1", "*NODE PRINT, NSET=NALL", "U", "*END STEP"]
    assert calculix.run_ccx(tmp_path / "spin", deck + spin)["ok"]
    u = next(iter(calculix.parse_dat(tmp_path / "spin" / "job.dat", "displacements").values()))
    assert max(v[0] for v in u.values()) == pytest.approx(RHO * w * w * L ** 3 / (3 * E), rel=0.01)  # uniform bar spun about its root

    assert calculix.run_ccx(tmp_path / "modes", deck + ["*STEP", "*FREQUENCY", "2", "*END STEP"])["ok"]
    f1 = calculix.parse_frequencies(tmp_path / "modes" / "job.dat")[0]
    assert f1 == pytest.approx(1.875104 ** 2 / (2 * math.pi) * math.sqrt(E * B ** 2 / (12 * RHO * L ** 4)), rel=0.01)  # Euler-Bernoulli

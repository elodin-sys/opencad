import math

import numpy as np
import pytest

from opencad.assembly import joints as jm
from opencad.contract import load_assembly
from opencad.paths import DESIGNS
from opencad.schemas import AssemblyContract


def _rz(deg: float, t=(0.0, 0.0, 0.0)) -> np.ndarray:
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    m = np.eye(4)
    m[:2, :2] = [[c, -s], [s, c]]
    m[:3, 3] = t
    return m


def _mechanism(name: str, parts: list[str], joints: list[dict], **kw) -> AssemblyContract:
    return AssemblyContract.model_validate(
        {
            "name": name,
            "intent": "synthetic mechanism",
            "datum_part": parts[0],
            "frame": {"origin": "o", "axes": {"x": "x", "y": "y", "z": "z"}},
            "envelope": {"min": [-200, -200, -10], "max": [200, 200, 10], "tolerance": 0.1},
            "parts": [{"name": n, "kind": "modelled", "design": f"{name}-{n}", "intent": "link " * 10} for n in parts],
            "joints": joints,
            **kw,
        }
    )


def _rev(name: str, parent: str, child: str, po, co, **kw) -> dict:
    return {
        "name": name,
        "kind": "revolute",
        "parent": parent,
        "child": child,
        "parent_frame": {"origin": list(po)},
        "child_frame": {"origin": list(co)},
        **kw,
    }


def _four_bar(closure_at_pivot: bool = False) -> tuple[AssemblyContract, dict[str, np.ndarray]]:
    """Ground 100, crank 40, coupler 100, rocker 80 (Grashof crank-rocker); at rest the crank lies on +x, the rocker points +y."""
    joints = [
        _rev("crankPivot", "ground", "crank", (0, 0, 0), (0, 0, 0), drive={"kind": "motor", "speed": 10.0}),
        _rev("crankPin", "crank", "coupler", (40, 0, 0), (0, 0, 0)),
    ]
    if closure_at_pivot:
        joints += [
            _rev("couplerPin", "coupler", "rocker", (100, 0, 0), (80, 0, 0)),
            _rev("rockerPivot", "ground", "rocker", (100, 0, 0), (0, 0, 0), closure=True),
        ]
    else:
        joints += [
            _rev("rockerPivot", "ground", "rocker", (100, 0, 0), (0, 0, 0)),
            _rev("couplerPin", "coupler", "rocker", (100, 0, 0), (80, 0, 0), closure=True),
        ]
    a = _mechanism(
        "fb",
        ["ground", "crank", "coupler", "rocker"],
        joints,
        acceptance={"motions": [{"name": "turn", "drive": "crankPivot", "range": [0.0, 360.0], "steps": 36}]},
    )
    return a, {
        "ground": np.eye(4),
        "crank": np.eye(4),
        "coupler": _rz(math.degrees(math.atan2(80, 60)), (40, 0, 0)),
        "rocker": _rz(90.0, (100, 0, 0)),
    }


def _rocker_exact(crank_deg: float) -> float:
    """Rocker angle from rest by circle intersection on the assembled (open) branch."""
    a = np.array([40 * math.cos(math.radians(crank_deg)), 40 * math.sin(math.radians(crank_deg))])
    d = np.array([100.0, 0.0]) - a
    n = float(np.linalg.norm(d))
    along = (100**2 - 80**2 + n**2) / (2 * n)
    b = a + along * d / n + math.sqrt(100**2 - along**2) * np.array([-d[1], d[0]]) / n
    return math.degrees(math.atan2(b[1], b[0] - 100)) - 90.0


def _star_part(teeth: int, r: float):
    from build123d import Box, Cylinder, PolarLocations

    body = Cylinder(r, 6)
    for loc in PolarLocations(r + 0.8, teeth):
        body += loc * Box(2.0, 1.5, 6)
    return body


def _star(teeth: int, r: float):
    return _star_part(teeth, r).wrapped


def test_count_teeth_reads_star_profiles_and_ratio():
    from opencad.assembly.kinematics import count_teeth

    z = np.array([0.0, 0.0, 1.0])
    a = count_teeth(_star(12, 10.0), np.zeros(3), z)
    b = count_teeth(_star(24, 20.0), np.zeros(3), z)
    assert (a["teeth"], b["teeth"]) == (12, 24)
    assert -a["teeth"] / b["teeth"] == pytest.approx(-0.5)


def test_propagate_chains_transmissions_and_limits_are_contract_checked():
    base = {
        "name": "t-train", "intent": "two-stage gear train", "datum_part": "frame",
        "frame": {"origin": "o", "axes": {"x": "x", "y": "y", "z": "z"}}, "envelope": {"min": [0, 0, 0], "max": [1, 1, 1], "tolerance": 0.1},
        "parts": [{"name": n, "kind": "modelled", "design": f"t-train-{n}", "intent": "gear " * 10} for n in ("frame", "a", "b", "c")],
        "joints": [{"name": f"j{n}", "kind": "revolute", "parent": "frame", "child": n, "parent_frame": {"origin": [x, 0.0, 0.0]}, "child_frame": {"origin": [0.0, 0.0, 0.0]},
                    **({"limits": [-100.0, 100.0]} if n == "c" else {})} for n, x in (("a", 0.0), ("b", 30.0), ("c", 60.0))],
        "transmissions": [{"name": "ab", "kind": "gear", "driver": "ja", "driven": "jb", "ratio": -0.5},
                          {"name": "bc", "kind": "gear", "driver": "jb", "driven": "jc", "ratio": -2.0}],
    }
    a = AssemblyContract.model_validate(base)
    assert jm.propagate(a, "ja", 90.0) == {"ja": 90.0, "jb": -45.0, "jc": 90.0}
    from opencad.contract import lint_assembly

    bad = {**base, "acceptance": {"motions": [{"name": "far", "drive": "jc", "range": [0.0, 360.0]}]}}
    problems, _ = lint_assembly(AssemblyContract.model_validate(bad))
    assert any("exceeds joint jc limits" in p for p in problems)


@pytest.mark.parametrize("closure_at_pivot", [False, True])
def test_four_bar_loop_follows_the_closed_form_on_its_assembled_branch(closure_at_pivot):
    a, pl = _four_bar(closure_at_pivot)
    qs = list(range(0, 361, 10))
    path = jm.solve_path(a, pl, [{"crankPivot": float(q)} for q in qs])
    rocker = [jm.displacement(a, pl, v, "rockerPivot") for v, _ in path]
    assert max(abs(r - _rocker_exact(q)) for q, r in zip(qs, rocker)) < 1e-9
    assert all(info["ok"] and info["closure_mm"] < 1e-9 for _, info in path)
    assert jm.unknowns(a, {"crankPivot": 0.0}) == (["crankPin", "couplerPin"] if closure_at_pivot else ["crankPin", "rockerPivot"])


def test_closure_joints_are_linted_and_a_second_parent_needs_one():
    from pydantic import ValidationError

    from opencad.contract import lint_assembly

    a, _ = _four_bar()
    assert lint_assembly(a)[0] == []
    d = a.model_dump()
    d["joints"][3]["closure"] = False
    with pytest.raises(ValidationError, match="child of two joints"):
        AssemblyContract.model_validate(d)
    d["joints"][3].update(closure=True, drive={"kind": "motor", "speed": 1.0})
    assert any("cannot be rigid or driven" in p for p in lint_assembly(AssemblyContract.model_validate(d))[0])
    d["joints"][3].update(drive=None, kind="slider")
    assert any("slider closure needs `ref`" in p for p in lint_assembly(AssemblyContract.model_validate(d))[0])


def test_measured_kinematic_bands_are_not_finer_than_the_evaluator():
    from opencad.contract import lint_assembly

    a, _ = _four_bar()
    obs = {"id": "rockerSwing", "quantity": "joint_range", "unit": "deg", "joint": "rockerPivot", "motion": a.acceptance.motions[0].name}
    tight = a.model_dump() | {"observables": [obs | {"expected": {"expected": 64.667, "tolerance": 1e-6}}]}
    assert any("finer than the evaluator measures" in p for p in lint_assembly(AssemblyContract.model_validate(tight))[0])
    loose = a.model_dump() | {"observables": [obs | {"expected": {"expected": 64.667, "tolerance": 1e-3}}]}
    assert not any("finer than the evaluator" in p for p in lint_assembly(AssemblyContract.model_validate(loose))[0])


def test_crank_slider_stroke_matches_the_offset_formula():
    xr = 30 + math.sqrt(100**2 - 10**2)
    guide = {
        "name": "guide",
        "kind": "slider",
        "parent": "ground",
        "child": "slider",
        "parent_frame": {"origin": [xr, 10, 0], "axis": [1, 0, 0], "ref": [0, 1, 0]},
        "child_frame": {"origin": [0, 0, 0], "axis": [1, 0, 0], "ref": [0, 1, 0]},
    }
    a = _mechanism(
        "cs",
        ["ground", "crank", "rod", "slider"],
        [
            _rev("crankPivot", "ground", "crank", (0, 0, 0), (0, 0, 0), drive={"kind": "motor", "speed": 10.0}),
            _rev("crankPin", "crank", "rod", (30, 0, 0), (0, 0, 0)),
            guide,
            _rev("wristPin", "rod", "slider", (100, 0, 0), (0, 0, 0), closure=True),
        ],
    )
    pl = {"ground": np.eye(4), "crank": np.eye(4), "rod": _rz(math.degrees(math.atan2(10, xr - 30)), (30, 0, 0)), "slider": _rz(0.0, (xr, 10, 0))}
    xs = [v["guide"] for v, _ in jm.solve_path(a, pl, [{"crankPivot": float(q)} for q in np.linspace(0, 360, 721)])]
    exact = [30 * math.cos(math.radians(q)) + math.sqrt(100**2 - (10 - 30 * math.sin(math.radians(q))) ** 2) - xr for q in np.linspace(0, 360, 721)]
    assert max(abs(x - e) for x, e in zip(xs, exact)) < 1e-9
    assert max(xs) - min(xs) == pytest.approx(math.sqrt(130**2 - 10**2) - math.sqrt(70**2 - 10**2), abs=1e-3)


def _planetary(ring_mesh: bool = True) -> tuple[AssemblyContract, dict[str, np.ndarray]]:
    """Fixed ring z48 on the frame, sun z24 driven, three planets z12 on a free carrier (centre distance 18)."""
    joints = [
        {
            "name": "ringFixed",
            "kind": "rigid",
            "parent": "frame",
            "child": "ring",
            "parent_frame": {"origin": [0, 0, 0], "ref": [1, 0, 0]},
            "child_frame": {"origin": [0, 0, 0], "ref": [1, 0, 0]},
        },
        _rev("sunSpin", "frame", "sun", (0, 0, 0), (0, 0, 0), drive={"kind": "motor", "speed": 10.0}),
        _rev("carrierSpin", "frame", "carrier", (0, 0, 0), (0, 0, 0)),
    ]
    trans, pl = [], {n: np.eye(4) for n in ("frame", "ring", "sun", "carrier")}
    for k in range(3):
        c = (18 * math.cos(math.radians(120 * k)), 18 * math.sin(math.radians(120 * k)), 0.0)
        joints.append(_rev(f"planet{k}Spin", "carrier", f"planet{k}", c, (0, 0, 0)))
        pl[f"planet{k}"] = _rz(0.0, c)
        trans.append(
            {"name": f"sunPlanet{k}", "kind": "gear", "driver": "sunSpin", "driven": f"planet{k}Spin", "ratio": -2.0, "carrier": "carrierSpin"}
        )
        if ring_mesh:
            trans.append(
                {"name": f"ringPlanet{k}", "kind": "gear", "driver": "ringFixed", "driven": f"planet{k}Spin", "ratio": 4.0, "carrier": "carrierSpin"}
            )
    return _mechanism("pl", ["frame", "ring", "sun", "carrier", "planet0", "planet1", "planet2"], joints, transmissions=trans), pl


def test_planetary_carrier_turns_a_third_and_an_open_carrier_is_reported_free():
    a, pl = _planetary()
    v, info = jm.solve(a, pl, {"sunSpin": 360.0})
    assert info["ok"] and v["carrierSpin"] == pytest.approx(120.0, abs=1e-9) and v["planet1Spin"] == pytest.approx(-480.0, abs=1e-9)
    v, info = jm.solve(a, pl, {"carrierSpin": 30.0})  # driven from the carrier, the sun follows 3:1
    assert info["ok"] and v["sunSpin"] == pytest.approx(90.0, abs=1e-9)
    b, pl = _planetary(ring_mesh=False)
    _, info = jm.solve(b, pl, {"sunSpin": 10.0})
    assert not info["ok"] and "carrierSpin" in info["free"]
    from opencad.contract import lint_assembly

    motion = {"acceptance": {"motions": [{"name": "turn", "drive": "sunSpin", "range": [0.0, 360.0]}]}}
    problems, _ = lint_assembly(AssemblyContract.model_validate(b.model_dump() | motion))
    assert any("underdetermined" in p for p in problems)
    assert lint_assembly(AssemblyContract.model_validate(a.model_dump() | motion))[0] == []


def test_a_meshed_gear_cannot_buy_clearance_off_its_axis():
    a, pl = _planetary()
    d = a.model_dump()
    for t in d["transmissions"]:
        t["mesh"] = {"pitch_deg": 15.0, "backlash_max": 0.10}
    a = AssemblyContract.model_validate(d)
    bounds = jm.mesh_bounds(a)
    assert bounds["planet0Spin"] == pytest.approx(0.02) and bounds["sunSpin"] == pytest.approx(0.02) and set(bounds).isdisjoint({"ringFixed", "carrierSpin"})
    off = pl["planet0"].copy()
    off[0, 3] += 0.04  # the planetary correction moved each planet 0.04 mm off its spin axis to clear the ring
    j = a.joint("planet0Spin")
    loose, tight = jm.fidelity(j, pl["carrier"], off), jm.fidelity(j, pl["carrier"], off, bounds["planet0Spin"])
    assert loose["ok"] and not tight["ok"] and tight["checks"]["radial_mm"]["max"] == pytest.approx(0.02) and "gear mesh" in tight["checks"]["radial_mm"]["note"]


def test_ring_gear_is_read_internally_and_a_rack_pitch_gives_mm_per_degree():
    from build123d import Box, Cylinder, PolarLocations, Pos

    from opencad.assembly.kinematics import meshing_teeth, rack_ratio

    ring = Cylinder(30, 6) - Cylinder(25, 6)
    for loc in PolarLocations(24.4, 48):
        ring += loc * Box(1.4, 1.0, 6)
    planet = Pos(18, 0, 0) * _star_part(12, 5.2)
    z = np.array([0.0, 0.0, 1.0])
    tr, tp = meshing_teeth(ring.wrapped, planet.wrapped, np.zeros(3), z, np.array([18.0, 0.0, 0.0]), z)
    assert (tr["teeth"], tr.get("internal"), tp["teeth"]) == (48, True, 12) and tr["heights_meshing"] > 0
    from opencad.geomcheck.gears import tooth_count

    part_check = tooth_count(ring.wrapped, [0, 0, 0], [0, 0, 1], 0.0, 1.0, 48)  # the part pipeline's gear check reads the bore too
    assert part_check["ok"] and part_check["internal"] and tooth_count(_star(12, 5.2), [0, 0, 0], [0, 0, 1], 0.0, 1.0, 12)["ok"]
    pitch = 2 * math.pi  # module 2
    rack = Pos(0, -20, 0) * Box(130, 10, 6)
    for k in range(-9, 10):
        rack += Pos(k * pitch, -14, 0) * Box(2.4, 2.0, 6)
    rr = rack_ratio(_star(20, 10.0), rack.wrapped, np.zeros(3), z, np.array([1.0, 0.0, 0.0]))
    assert rr["pinion"]["teeth"] == 20 and rr["rack"]["pitch"] == pytest.approx(pitch, rel=2e-4)
    assert rr["mm_per_deg"] == pytest.approx(20 * pitch / 360, rel=2e-4)
    assert rack_ratio(_star(20, 10.0), rack.wrapped, np.zeros(3), -z, np.array([1.0, 0.0, 0.0]))["mm_per_deg"] < 0  # the other sense


def _observing(a: AssemblyContract, placements: dict[str, np.ndarray], tmp_path, kin: dict | None = None):
    from types import SimpleNamespace

    from opencad.backends.placements import write_placements

    (tmp_path / "export").mkdir(parents=True)
    write_placements(tmp_path / "export" / "placements.json", {k: v.tolist() for k, v in placements.items()})
    return SimpleNamespace(contract=a, results_dir=tmp_path, load_stage=lambda s: (kin or {}) if s == "kinematics" else {})


def test_kinematic_observables_track_the_loop_from_rest(tmp_path):
    from opencad.assembly.simulate import geometric

    a, pl = _four_bar()
    a = AssemblyContract.model_validate(
        a.model_dump()
        | {
            "observables": [
                {"id": "rocker", "quantity": "joint_value", "unit": "deg", "joint": "rockerPivot", "motion": "turn"},
                {"id": "swing", "quantity": "joint_range", "unit": "deg", "joint": "rockerPivot", "motion": "turn"},
                {"id": "rockerAt90", "quantity": "joint_value", "unit": "deg", "joint": "rockerPivot", "at": 90.0},
                {"id": "pinY", "quantity": "point_y", "unit": "mm", "body": "rocker", "location": [100.0, 80.0, 0.0], "at": 90.0},
            ]
        }
    )
    actx = _observing(a, pl, tmp_path)
    obs = {o.id: geometric(actx, o) for o in a.observables}
    s = obs["rocker"]["series"]
    assert s["x"][0] == 0.0 and s["x"][-1] == 360.0 and len(s["x"]) == 361
    assert max(abs(y - _rocker_exact(x)) for x, y in zip(s["x"], s["y"])) < 1e-9
    exact = [_rocker_exact(q) for q in np.linspace(0, 360, 36001)]
    assert obs["swing"]["value"] == pytest.approx(max(exact) - min(exact), abs=1e-3)
    assert obs["rockerAt90"]["value"] == pytest.approx(_rocker_exact(90.0), abs=1e-9)
    assert obs["pinY"]["value"] == pytest.approx(80 * math.sin(math.radians(90 + _rocker_exact(90.0))), abs=1e-9)


def test_transmission_ratio_of_a_carrier_uses_the_measured_meshes(tmp_path):
    from opencad.assembly.simulate import geometric

    a, pl = _planetary()
    a = AssemblyContract.model_validate(
        a.model_dump() | {"observables": [{"id": "carrierRatio", "quantity": "transmission_ratio", "unit": "", "body": "carrier"}]}
    )
    measured = {t.name: {"ratio_measured": t.ratio, "driver": t.driver, "driven": t.driven} for t in a.transmissions}
    assert geometric(_observing(a, pl, tmp_path, {"transmissions": measured}), a.observables[0])["value"] == pytest.approx(1 / 3, abs=1e-12)
    measured.pop("ringPlanet1")
    assert geometric(_observing(a, pl, tmp_path / "x", {"transmissions": measured}), a.observables[0])["status"] == "unavailable"


@pytest.mark.parametrize(
    "path", sorted(p for p in DESIGNS.glob("*/assembly.yaml") if not p.parent.name.startswith(("_", "."))), ids=lambda p: p.parent.name
)
def test_tree_contracts_keep_exact_propagation(path):
    a = load_assembly(path.parent)
    if not jm.is_tree(a):
        pytest.skip("closure joints or carrier meshes: solved, not propagated")
    placements = {p.name: np.eye(4) for p in a.parts}
    for m in a.acceptance.motions:
        qs = [m.range[0] + (m.range[1] - m.range[0]) * i / m.steps for i in range(m.steps + 1)]
        assert [v for v, _ in jm.solve_path(a, placements, [{m.drive: q} for q in qs])] == [jm.propagate(a, m.drive, q) for q in qs]

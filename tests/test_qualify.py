import pytest

from opencad.geomcheck.qualify import qualify, repair


def _box():
    from build123d import Box

    return Box(10, 20, 30).wrapped


def test_valid_box_qualifies():
    q = qualify(_box())
    assert q["ok"] and q["solids"] == 1 and q["free_edges"] == 0 and q["volumes"][0] == pytest.approx(6000.0)


def test_inside_out_box_is_rejected_and_reoriented_through_a_step_round_trip(tmp_path):
    from opencad.backends.local import write_step
    from opencad.geomcheck import brep

    q = qualify(_box().Reversed())
    assert not q["ok"] and q["inverted"] == [0] and q["volumes"][0] == pytest.approx(-6000.0)
    fixed, rec = repair(_box().Reversed())
    assert rec["ok"] and rec["steps"] and qualify(fixed)["volumes"][0] == pytest.approx(6000.0)
    write_step(fixed, tmp_path / "box.step", "box")
    back = qualify(brep.read_step(tmp_path / "box.step"))
    assert back["ok"] and back["volumes"][0] == pytest.approx(6000.0)


def test_loose_faces_with_a_gap_are_sewn_into_a_solid():
    from build123d import Compound, Pos

    faces = _box_faces()
    faces[0] = Pos(0.03, 0, 0) * faces[0]  # one face 0.03 mm off: open at the default tolerance, closed by the sweep
    loose = Compound(children=faces).wrapped
    q = qualify(loose)
    assert not q["ok"] and q["solids"] == 0
    _, rec = repair(loose)
    assert rec["ok"], rec
    assert rec["after"]["solids"] == 1 and rec["after"]["volumes"][0] == pytest.approx(6000.0, rel=0.01)
    assert any(s.startswith("sewn at 0.05 mm") for s in rec["steps"])


def _box_faces():
    from build123d import Box

    return list(Box(10, 20, 30).faces())

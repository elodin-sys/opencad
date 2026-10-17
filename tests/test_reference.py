import json
import math

import numpy as np
import pytest
import trimesh

from opencad.reference.mesh import IngestError, ingest, parse_axes, section
from opencad.reference.profile import analyse, ingest_profile


def box_with_hole_mesh() -> trimesh.Trimesh:
    """80 x 50 x 6 plate with a 10 mm square through-hole, built from two boxes without booleans."""
    outer = trimesh.creation.box(extents=[80, 50, 6]).apply_translation([40, 25, 3])
    return outer


def test_parse_axes():
    assert np.allclose(parse_axes(None), np.eye(3))
    R = parse_axes("x=+y,y=-x,z=+z")
    assert np.allclose(R @ np.array([1, 0, 0]), [0, -1, 0])
    with pytest.raises(IngestError):
        parse_axes("x=+x,y=+x,z=+z")
    with pytest.raises(IngestError, match="determinant"):
        parse_axes("x=+y,y=+x,z=+z")


def test_ingest_box_units_axes_datum(tmp_path):
    m = trimesh.creation.box(extents=[7.5, 1.2, 0.5])  # cm, centred at origin
    src = tmp_path / "ref.stl"
    m.export(src)
    rec = ingest(src, tmp_path / "out", units="cm", axes="x=+x,y=-z,z=+y", datum="min", expect_size_mm=[75, 5, 12])
    meas = rec["measurements"]
    assert meas["size"] == pytest.approx([75, 5, 12], abs=1e-6)
    assert meas["bbox_min"] == pytest.approx([0, 0, 0], abs=1e-6)
    assert meas["volume"] == pytest.approx(75 * 5 * 12, rel=1e-6)
    assert meas["center_of_mass"] == pytest.approx([37.5, 2.5, 6], abs=1e-6)
    assert meas["watertight"] and meas["components"] == 1
    assert rec["anchor"]["ok"]
    out = tmp_path / "out"
    assert (out / "reference.json").exists() and (out / "reference.ply").exists()
    for v in ("top", "front", "right"):
        assert (out / f"silhouette-{v}.png").exists()
    assert (out / "reference-sections.png").exists()
    assert len(meas["sections"]) == 9
    zsec = [s for s in meas["sections"] if s["plane"] == "z"][0]
    assert zsec["area"] == pytest.approx(75 * 5, rel=1e-6) and zsec["loops"] == 1 and zsec["holes"] == 0


def test_ingest_anchor_rejects_wrong_units(tmp_path):
    m = trimesh.creation.box(extents=[75, 12, 5])
    src = tmp_path / "ref.stl"
    m.export(src)
    with pytest.raises(IngestError, match="unit anchor failed"):
        ingest(src, tmp_path / "out", units="in", expect_size_mm=[75, 12, 5])


def test_ingest_dry_run_writes_only_previews(tmp_path):
    m = trimesh.creation.box(extents=[10, 20, 30])
    src = tmp_path / "ref.ply"
    m.export(src)
    ingest(src, tmp_path / "out", units="mm", dry_run=True)
    names = sorted(p.name for p in (tmp_path / "out").iterdir())
    assert names == ["reference-dryrun.json", "reference-sections-dryrun.png"]


def test_section_of_annulus_counts_hole():
    ring = trimesh.creation.annulus(r_min=5, r_max=10, height=4)
    s = section(ring, "z", 0.0)
    assert s["loops"] == 1 and s["holes"] == 1
    assert s["area"] == pytest.approx(math.pi * (100 - 25), rel=0.02)


def _prism(poly, h: float = 10.0) -> trimesh.Trimesh:
    return trimesh.creation.extrude_polygon(poly, h)


def _u_section(deg: float = 0.0):
    """A channel skin: straight sides x = +-25 up to y = 40 on a semi-ellipse (depth 15) centred at (0, 10), rotated by deg."""
    from shapely import affinity
    from shapely.geometry import Point, box
    from shapely.ops import unary_union

    u = unary_union([box(-25, 10, 25, 40), affinity.scale(Point(0, 10).buffer(1, quad_segs=64), 25, 15, origin=(0, 10))])
    return affinity.rotate(u, deg, origin=(0, 0))


@pytest.mark.parametrize("deg,end,center", [(0, "-v", [0, 10]), (180, "+v", [0, -10]), (-90, "-u", [10, 0]), (90, "+u", [-10, 0])])
def test_u_shape_fit_recovers_a_channel_skin_in_any_orientation(deg, end, center):
    f = section(_prism(_u_section(deg)), "z", 5.0, detail=True)["regions"][0]["fit"]
    g = f["u_shape"]
    assert f["best"] == "u_shape" and g["end"] == end and g["center"] == pytest.approx(center, abs=0.05)
    assert g["half_width"] == pytest.approx(25, abs=0.01) and g["depth"] == pytest.approx(15, abs=0.05) and g["length"] == pytest.approx(30, abs=0.05)


def test_fits_recover_ellipse_and_rounded_rectangle_and_a_notch_does_not_hide_a_circle():
    from shapely import affinity
    from shapely.geometry import Point, box

    ellipse = affinity.rotate(affinity.scale(Point(0, 0).buffer(1, quad_segs=64), 25, 18.5), 30, origin=(0, 0))
    f = section(_prism(ellipse), "z", 5.0, detail=True)["regions"][0]["fit"]
    assert f["best"] == "ellipse" and f["ellipse"]["semi_axes"] == pytest.approx([25, 18.5], abs=0.01)
    assert f["ellipse"]["angle_deg"] == pytest.approx(30, abs=0.1) and f["ellipse"]["p95"] < 0.01
    rounded = box(-20, -12, 20, 12).buffer(-4).buffer(4, quad_segs=32)
    f = section(_prism(rounded), "z", 5.0, detail=True)["regions"][0]["fit"]
    assert f["best"] == "rounded_rect" and f["rounded_rect"]["size"] == pytest.approx([40, 24], abs=0.01)
    assert f["rounded_rect"]["corner_radius"] == pytest.approx(4, abs=0.01)
    notched = Point(0, 0).buffer(10, quad_segs=64).difference(box(9.2, -0.3, 11, 0.3))
    f = section(_prism(notched), "z", 5.0, detail=True)["regions"][0]["fit"]
    assert f["best"] == "circle" and f["circle"]["radius"] == pytest.approx(10, abs=0.05) and f["circle"]["max"] > 0.5, "the notch shows in max, not in the choice"


def test_ingest_stations_add_outlines_fits_profile_and_a_sheet(tmp_path):
    from opencad.initialize import station_note
    from opencad.reference.__main__ import main

    src = tmp_path / "u.stl"
    _prism(_u_section(), h=60.0).export(src)
    out = tmp_path / "out"
    assert main(["ingest", str(src), "--units", "mm", "--datum", "keep", "--stations", "4", "--station-axis", "z", "--out", str(out)]) == 0
    rec = json.loads((out / "reference.json").read_text())
    st, prof = rec["measurements"]["stations"], rec["measurements"]["profile"]
    assert st["axis"] == "z" and st["uv_axes"] == ["x", "y"] and len(st["positions"]) == 4
    assert 0 < st["positions"][0] < 5 and 55 < st["positions"][-1] < 60, "Chebyshev spacing: stations crowd both ends"
    s = st["sections"][0]
    assert len(s["regions"][0]["outline"]) == 32 and len(s["regions"][0]["outline_16"]) == 16 and s["hull"]["fit"]["best"] == "u_shape"
    assert prof[0]["half_size_uv"] == pytest.approx([25, 22.5], abs=0.05) and prof[0]["center_uv"] == pytest.approx([0, 17.5], abs=0.05)
    assert (out / "reference-sections-stations.png").exists()
    assert all("outline" in r for sec in rec["measurements"]["sections"] for r in sec["regions"])
    assert "u_shape" in station_note(out) and "outline_16" in station_note(out)
    legacy = ingest(src, tmp_path / "legacy", units="mm", datum="keep")
    assert "stations" not in legacy["measurements"] and "outline" not in legacy["measurements"]["sections"][0]["regions"][0]
    assert station_note(tmp_path / "legacy") == ""


def test_profile_analysis_square():
    pts = np.array([[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], dtype=float)
    a = analyse(pts)
    assert a["area"] == pytest.approx(100) and a["perimeter"] == pytest.approx(40)
    assert a["closed_input"] and a["points"] == 4
    assert a["chord"] == pytest.approx(math.sqrt(200))
    assert a["stagger_deg"] == pytest.approx(45)
    assert a["area_centroid"] == pytest.approx([5.0, 5.0], abs=1e-9)
    assert a["self_intersections_checked"] and not a["self_intersecting"]


def test_profile_landmark_chord_ellipse():
    t = np.linspace(math.pi, 0, 80)
    side1 = np.stack([50 * np.cos(t), 20 * np.sin(t)], axis=1)
    t2 = np.linspace(math.pi, 0, 80)
    side2 = np.stack([50 * np.cos(t2), -20 * np.sin(t2)], axis=1)
    loop = np.vstack([side1, side2[1:-1][::-1]])
    a = analyse(loop, side1=side1)
    assert a["landmark_chord"] == pytest.approx(100.0, abs=1e-6)
    assert a["landmark_stagger_deg"] == pytest.approx(0.0, abs=1e-6)
    assert a["area_centroid"] == pytest.approx([0.0, 0.0], abs=0.2)


def test_profile_self_intersection_bowtie():
    bow = np.array([[0.0, 0.0], [1.0, 1.0], [1.0, 0.0], [0.0, 1.0]], dtype=float)
    a = analyse(bow)
    assert a["self_intersecting"] and a["self_intersections"] >= 1


def test_profile_ingest_csv_and_units(tmp_path):
    n = 200
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    pts = np.stack([5 * np.cos(t), 2 * np.sin(t)], axis=1)  # ellipse a=5 b=2 (cm)
    src = tmp_path / "ellipse.csv"
    src.write_text("x,y\n" + "\n".join(f"{x},{y}" for x, y in pts))
    rec = ingest_profile(src, tmp_path / "out", units="cm")
    m = rec["measurements"]
    assert m["area"] == pytest.approx(math.pi * 50 * 20, rel=0.002)
    assert m["chord"] == pytest.approx(100, rel=0.001)
    assert abs(m["stagger_deg"]) < 1.0
    assert m["max_thickness"] == pytest.approx(40, rel=0.02)
    assert (tmp_path / "out" / "profile.png").exists()
    saved = json.loads((tmp_path / "out" / "profile.json").read_text())
    assert len(saved["points_mm"]) == n


def test_profile_ingest_scale_to_mm_overrides_units(tmp_path):
    src = tmp_path / "nondim.dat"
    src.write_text("# comment\nVARIABLES = X Y\n0.0 0.375\n1.0 0.375\n1.0 0.46875\n0.0 0.46875\n0.0 0.375\n")
    rec = ingest_profile(src, tmp_path / "out", units="mm", scale_to_mm=203.2)
    m = rec["measurements"]
    assert m["bbox_max"][0] == pytest.approx(203.2, abs=0.01)
    assert m["bbox_max"][1] == pytest.approx(0.46875 * 203.2, abs=0.01)

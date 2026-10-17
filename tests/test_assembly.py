"""Multi-body and interior checks: clearance, solid selection, wall thickness, passage connectivity."""

from __future__ import annotations

from pathlib import Path

from OCP.BRep import BRep_Builder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.TopoDS import TopoDS_Compound

from opencad.geomcheck import assembly
from opencad.truth.mutants import write_stl


def _duct():
    outer = BRepPrimAPI_MakeBox(40, 40, 40).Shape()
    inner = BRepPrimAPI_MakeBox(gp_Pnt(2, 2, 2), gp_Pnt(38, 38, 38)).Shape()
    shell = BRepAlgoAPI_Cut(outer, inner).Shape()
    port = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(-1, 20, 20), gp_Dir(1, 0, 0)), 3, 42).Shape()
    return BRepAlgoAPI_Cut(shell, port).Shape()


PLUGS = [([-0.5, 16, 16], [2.5, 24, 24]), ([37.5, 16, 16], [40.5, 24, 24])]


def test_passage_refuses_a_leaked_voxel_fill(tmp_path: Path):
    """A cracked shell (one face missing) lets the flood fill into the material: the fake cavity must not read as a passage."""
    import trimesh

    solid = trimesh.creation.box(extents=(40, 40, 40))
    stl = tmp_path / "solid.stl"
    solid.export(stl)
    ok = assembly.passage(stl, [0, 0, 0], [10, 0, 0], pitch=1.0)
    assert ok["a"]["state"] == "solid" and not ok["fill"]["leak"] and ok["fill"]["fill_ratio"] > 0.9
    # drop one face of the box: the fill leaks, the interior becomes a fake air component
    cracked = trimesh.Trimesh(solid.vertices.copy(), solid.faces[:-1].copy(), process=False)
    cracked_stl = tmp_path / "cracked.stl"
    cracked.export(cracked_stl)
    r = assembly.passage(cracked_stl, [0, 0, 0], [10, 0, 0], pitch=1.0)
    assert r["fill"]["leak"] and r["fill"]["open_edges"] == 3 and r["fill"]["fill_ratio"] < assembly.FILL_LEAK_RATIO
    assert not r["ok"] and "voxel fill leaked" in r["error"]


def test_clearance_gap_and_interference():
    a = BRepPrimAPI_MakeBox(10, 10, 10).Shape()
    b = BRepPrimAPI_MakeBox(gp_Pnt(11.5, 0, 0), gp_Pnt(20, 10, 10)).Shape()
    r = assembly.clearance(a, b, min_gap=1.0)
    assert r["ok"] and abs(r["gap"] - 1.5) < 1e-9 and r["interference_volume"] < 1e-9
    assert not assembly.clearance(a, b, min_gap=2.0)["ok"]
    c = BRepPrimAPI_MakeBox(gp_Pnt(9.5, 0, 0), gp_Pnt(20, 10, 10)).Shape()
    r = assembly.clearance(a, c)
    assert not r["ok"] and abs(r["interference_volume"] - 50) < 1e-6


def test_select_solid_by_point():
    a = BRepPrimAPI_MakeBox(10, 10, 10).Shape()
    b = BRepPrimAPI_MakeBox(gp_Pnt(11.5, 0, 0), gp_Pnt(20, 10, 10)).Shape()
    comp = TopoDS_Compound()
    bb = BRep_Builder()
    bb.MakeCompound(comp)
    bb.Add(comp, a)
    bb.Add(comp, b)
    assert assembly.solid_props(assembly.select_solid(comp, [15, 5, 5]))["bbox_min"] == [11.5, 0.0, 0.0]
    assert assembly.select_solid(comp, [10.7, 5, 5]) is None


def test_thickness_and_passage(tmp_path: Path):
    duct = _duct()
    stl = write_stl(duct, tmp_path / "duct.stl", 0.05)
    th = assembly.thickness(stl, samples=3000, max_thickness=10)
    assert abs(th["min"] - 2.0) < 0.05 and abs(th["p50"] - 2.0) < 0.05
    # a 2 mm wall is never "thin" under a 0.75 minimum; under a 3 mm minimum every sample is, and the clusters box the whole duct
    assert assembly.thickness(stl, samples=3000, max_thickness=10, thin_below=0.75)["thin_clusters"] == []
    clusters = assembly.thickness(stl, samples=3000, max_thickness=10, thin_below=3.0)["thin_clusters"]
    assert clusters and clusters[0]["n"] >= clusters[-1]["n"] and abs(clusters[0]["median"] - 2.0) < 0.05 and 0 < clusters[0]["share"] <= 1
    assert all(len(c["min"]) == 3 and len(c["max"]) == 3 and all(a <= b for a, b in zip(c["min"], c["max"])) for c in clusters)
    r = assembly.passage(stl, [5, 20, 20], [35, 20, 20], pitch=0.5, plugs=PLUGS)
    assert r["ok"] and r["connected"] and not r["reaches_exterior"] and r["a"]["state"] == "interior"
    true_volume = 36.0 ** 3 - 2 * 0.5 * 8 * 8  # the cavity less the plugs' 0.5 mm reach into it
    assert r["passage_volume"] < true_volume < r["passage_volume_max"], (r["passage_volume"], r["passage_volume_max"])
    from opencad.geomcheck.multibody import check_passages

    spec = {"name": "p", "point_a": [5, 20, 20], "point_b": [35, 20, 20], "pitch": 1.0, "plugs": PLUGS, "volume_min": 0.98 * true_volume, "volume_max": 1.02 * true_volume}
    band = check_passages(stl, [spec])["p"]
    assert band["volume_check"]["measured"] < spec["volume_min"] and band["volume_check"]["ok"] and band["ok"]  # the raw count alone misses the band
    assert not check_passages(stl, [{**spec, "volume_min": 1.2 * true_volume, "volume_max": 1.3 * true_volume}])["p"]["ok"]
    unplugged = assembly.passage(stl, [5, 20, 20], [35, 20, 20], pitch=0.5, plugs=[])
    assert unplugged["reaches_exterior"] and not unplugged["ok"]
    blocked = BRepAlgoAPI_Fuse(duct, BRepPrimAPI_MakeBox(gp_Pnt(18, 0, 0), gp_Pnt(22, 40, 40)).Shape()).Shape()
    stl2 = write_stl(blocked, tmp_path / "blocked.stl", 0.05)
    r3 = assembly.passage(stl2, [5, 20, 20], [35, 20, 20], pitch=0.5, plugs=PLUGS)
    assert not r3["connected"] and not r3["ok"]
    assert assembly.passage(stl, [20, 20, 1], [35, 20, 20], pitch=0.5, plugs=PLUGS)["a"]["state"] == "solid"

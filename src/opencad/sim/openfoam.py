"""OpenFOAM adapter (ESI `opencfd/openfoam-default:2412`, arm64, in the container runtime): steady incompressible MRF with
simpleFoam and k-omega SST on the fluid body the assembly source builds.

Case from the domains stage: the fluid's labelled patch STL (metres) meshed by blockMesh + snappyHexMesh with `locationInMesh`
at the fluid seed; the rotor's MRF cell zone is a cylinder about its joint axis just past the blade tips. Patches by boundary
role: inlet (flowRateInletVelocity from the case flow), outlet (p = 0), rotating_wall (rotating with the zone), wall (noSlip).
Function objects give patch-averaged pressures, mass flows, rotor torque and point probes every 10 iterations; each observable is
the mean of its last TAIL of iterations (u_iteration its spread), and the refinement ladder's levels give the grid-convergence
index (opencad.sim.study). The background box is coarsened (a power of two above the interior size) until it holds at most
settings.background_cells_max hexes, and a refinement region inside the closed fluid surface brings the fluid back to the interior
size, so a level's memory follows the fluid, not the box; named regions (a rotor's tip annulus, a cylinder, a box) refine further. Inputs: fluidDensity, fluidViscosity (dynamic); the case values named by
settings.flow_key (L/min), settings.speed_key (rpm, else the rotor's drive) and settings.turbulence_key (inlet turbulence intensity,
%; default key inletTurbulencePct, else settings.inlet_turbulence_pct)."""

from __future__ import annotations

import math
import re
import shutil
from pathlib import Path
from typing import Any

import numpy as np

from opencad.io import dump_json, load_json
from opencad.sim import FORMAL_ORDER, TAIL, failed, predict, refinement, runtime, study, tail, unavailable

DOC = """`openfoam` — physics cfd_steady (steady MRF simpleFoam, k-omega SST): bodies [fluid, rotor] (the derived fluid body and the rotating
part); inputs fluidDensity (kg/m3), fluidViscosity (Pa s, dynamic); settings flow_key and speed_key (operating-case value names in L/min and
rpm), turbulence_key (the case value with the inlet turbulence intensity in %, default inletTurbulencePct; inlet_turbulence_pct when the
case has none, default 5), inlet_diameter_mm, cell_mm (interior cell size at level 1.0), surface_level (wall refinement levels below it,
default 1), layers (prism layers on walls, default 0), background_cells_max, iterations, processes, timeout_s (per run); boundaries on the
fluid body by role inlet, outlet, rotating_wall, wall.
Refinement: `refinement` is the mesh ladder coarse to fine and the last level is the prediction; state three levels (e.g. [1.0, 0.7, 0.5])
for a grid-convergence index, two give only a conservative (Fs 3) estimate and one none. A level is a size factor or {factor, regions:
{<region>: n}, iterations}: `regions` (on the simulation: {name, shape: rotor_tip | cylinder | box, ...}) refines a zone n levels past the
finest surface cells, e.g. a tip gap. Each step refines everywhere or only inside regions; a prediction is resolved only when its finest
steps refine everywhere with GCI <= settings.refinement_tolerance (0.05). Values are the mean of the last 20 % of the iterations.
Quantities: pressure_rise (Pa, outlet minus inlet patch average), pressure_rise_total_to_static (Pa, outlet static minus inlet static plus
the inlet's mean dynamic pressure, the ISO 5801 fan quantity), torque (N m, the driving torque the rotor absorbs: positive when the
flow takes power from it), velocity_magnitude, velocity_x|y|z and
pressure at observable.location."""

IMAGE = "opencfd/openfoam-default:2412"
BASHRC = "/usr/lib/openfoam/openfoam2412/etc/bashrc"
MM = 1e-3
MEMORY_CAP_GB = 40.0
BACKGROUND_CELLS_MAX = 3.0e6
TURBULENCE_PCT = 5.0
HEADER = "FoamFile {{ version 2.0; format ascii; class {cls}; object {obj}; }}\n"


def _v(sim: Any, key: str, default: float | None = None) -> float:
    if key in sim.inputs:
        return float(sim.inputs[key].value)
    if default is None:
        raise KeyError(f"simulation {sim.id}: input {key!r} is missing")
    return default


def _vec(v: Any) -> str:
    return "(" + " ".join(f"{float(x):.9g}" for x in v) + ")"


def _write(path: Path, cls: str, obj: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER.format(cls=cls, obj=obj) + body.strip() + "\n", encoding="utf-8")


def scaled_stl(src: Path, dest: Path, scale: float = MM, areas: dict[str, float] | None = None) -> dict[str, int]:
    """Copy a multi-solid ASCII STL in metres without its degenerate facets (two coincident vertices open an otherwise closed
    surface); returns triangles per region (and fills `areas`, m2 per region, the enclosed `_signed_volume` in m3, positive for
    outward triangles, and `_dropped` facets, when given)."""
    counts: dict[str, int] = {}
    out, facet, region, dropped = [], [], None, 0
    for line in src.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("solid "):
            region = s.split(None, 1)[1]
            counts[region] = 0
            out.append(line)
        elif s.startswith("facet ") and region is not None:
            facet = [line]
        elif facet:
            facet.append(f"      vertex {' '.join(f'{float(t) * scale:.9e}' for t in s.split()[1:4])}" if s.startswith("vertex ") else line)
            if s.startswith("endfacet"):
                verts = [ln.split()[1:4] for ln in facet if ln.strip().startswith("vertex ")]
                if len({tuple(v) for v in verts}) < 3:
                    dropped += 1
                else:
                    out += facet
                    counts[region] += 1
                    if areas is not None:
                        a, b, c = (np.asarray([float(t) for t in v]) for v in verts)
                        areas[region] = areas.get(region, 0.0) + 0.5 * float(np.linalg.norm(np.cross(b - a, c - a)))
                        areas["_signed_volume"] = areas.get("_signed_volume", 0.0) + float(np.dot(a, np.cross(b, c))) / 6.0
                facet = []
        else:
            out.append(line)
    if areas is not None:
        areas["_dropped"] = float(dropped)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    return counts


def _case_values(sim: Any, geom: Any, case: Any, rotor: str | None) -> tuple[float, float]:
    """(volumetric flow m3/s, rotor omega rad/s) for one operating case."""
    flow_key, speed_key = sim.settings.get("flow_key"), sim.settings.get("speed_key")
    q_lmin = float(case.values[flow_key]) if case is not None and flow_key else _v(sim, "flowRate", None) * 60000.0
    rpm = None
    if case is not None and speed_key:
        rpm = float(case.values[speed_key])
    elif rotor is not None:
        j = geom.joint_of(rotor)
        d = j.drive if j is not None else None
        if d is not None:
            rpm = d.speed if d.speed is not None else (float(case.values[d.case_value]) if case is not None and d.case_value else None)
    if rpm is None:
        raise KeyError("no rotor speed: set settings.speed_key or a drive speed")
    return q_lmin / 60000.0, rpm * 2 * math.pi / 60


def inlet_turbulence(sim: Any, case: Any) -> float:
    """Inlet turbulence intensity, %: the operating case's value under settings.turbulence_key, else the simulation's default."""
    key = str(sim.settings.get("turbulence_key", "inletTurbulencePct"))
    if case is not None and key in case.values:
        return float(case.values[key])
    return float(sim.settings.get("inlet_turbulence_pct", TURBULENCE_PCT))


def background(lo: np.ndarray, hi: np.ndarray, cell_mm: float, cap: float) -> tuple[int, float, np.ndarray, np.ndarray, np.ndarray]:
    """(k, background cell mm, cells, box lo, box hi): the smallest k >= 0 whose padded box at cell_mm 2^k holds at most `cap` hexes."""
    for k in range(7):
        h = cell_mm * 2 ** k
        # a port flush with the background box leaves its cells on the box boundary instead of forming the port patch
        pad = max(4 * h, 3.0) * MM
        n = np.maximum(1, np.ceil((hi - lo + 2 * pad) / (h * MM))).astype(int)
        if float(np.prod(n)) <= cap:
            break
    return k, h, n, lo - pad, hi + pad


def fresh(case_dir: Path) -> None:
    """Remove a previous run's outputs before a changed case runs: with a later time directory present, snappyHexMesh (startFrom
    latestTime) writes its mesh there and leaves constant/polyMesh the background box, which the patch check then rejects."""
    for p in case_dir.iterdir():
        try:
            later = float(p.name) > 0
        except ValueError:
            later = False
        if p.is_dir() and (later or p.name == "postProcessing" or p.name.startswith("processor")):
            shutil.rmtree(p)
    shutil.rmtree(case_dir / "constant" / "polyMesh", ignore_errors=True)
    for f in ("result.json", "started.json"):
        (case_dir / f).unlink(missing_ok=True)


def recovered(case_dir: Path, key: str, iterations: int, procs: int) -> bool:
    """A run whose driver died after starting it (the container went on alone) counts as finished when its start marker names these
    inputs, the solver reached endTime or converged, and the parallel run was reconstructed."""
    marker = case_dir / "started.json"
    if not marker.exists() or load_json(marker).get("hash") != key:
        return False
    log, rec = case_dir / "log.simpleFoam", case_dir / "log.reconstructPar"
    text = log.read_text(errors="replace") if log.exists() else ""
    times = [float(p.name) for p in case_dir.iterdir() if p.is_dir() and re.fullmatch(r"\d+(\.\d+)?", p.name)]
    done = max(times, default=0) >= iterations or "SIMPLE solution converged" in text
    return "\nEnd" in text[-3000:] and done and (procs <= 1 or rec.exists() and "\nEnd" in rec.read_text(errors="replace")[-500:])


def adopt(case_dir: Path, old: Path, key: str) -> None:
    """Move the last attempt's finished case into place when its inputs hash the same (a re-placement that left them alone)."""
    done = old / "result.json"
    if done.exists() and load_json(done).get("hash") == key:
        shutil.rmtree(case_dir)
        old.rename(case_dir)


def container_run(image: str, case_dir: Path, *, rt: str, procs: int, need_gb: float, mem_cap: float, settings: dict[str, Any]) -> dict[str, Any]:
    """Run the case's Allrun. snappyHexMesh's castellation holds cells on both sides of every wall, about twice the fluid mesh, so the
    request is twice the estimate; a run killed for memory (exit 137) is retried once at twice that, up to the cap."""
    gb = min(mem_cap, max(12.0, float(math.ceil(2 * need_gb))))
    while True:
        memory = str(settings.get("memory") or f"{gb:g}G")
        r = runtime.run(image, ["bash", "/case/Allrun"], mounts={case_dir: "/case"}, workdir="/case", rt=rt, cpus=procs, memory=memory,
                        timeout=float(settings.get("timeout_s", 7200)), log=case_dir / "log.container")
        r["memory"] = memory
        if r.get("code") != 137 or settings.get("memory") or gb >= mem_cap:
            return r
        gb = min(mem_cap, 2 * gb)


def layer_report(case_dir: Path) -> dict[str, dict[str, float]]:
    """Per-patch prism layer coverage from the snappyHexMesh log: faces, mean layers, overall thickness % of the target."""
    log = case_dir / "log.snappyHexMesh"
    if not log.exists():
        return {}
    text = log.read_text(errors="replace")
    table = text[text.rfind("overall thickness"):] if "overall thickness" in text else ""
    return {m.group(1): {"faces": int(m.group(2)), "layers": float(m.group(3)), "thickness_pct": float(m.group(5))}
            for m in re.finditer(r"^(\w+)\s+(\d+)\s+([0-9.]+)\s+([0-9.eE+-]+)\s+([0-9.]+)\s*$", table, flags=re.MULTILINE)}


def tip_band(geom: Any, body: str, depth: float) -> tuple[np.ndarray, np.ndarray, float, float, float]:
    """(axis origin, axis, tip radius, axial start, axial end) of the body's surface within `depth` of its largest radius."""
    import trimesh

    o, ax = geom.joint_axis(geom.joint_of(body).name)
    w = np.asarray(trimesh.load(geom.stl(body), force="mesh").vertices) - o
    t = w @ ax
    r = np.linalg.norm(w - np.outer(t, ax), axis=1)
    tip = r >= r.max() - max(depth, 1e-3)
    return o, ax, float(r.max()), float(t[tip].min()), float(t[tip].max())


def region_entries(sim: Any, geom: Any, rotor: str | None, levels: dict[str, int], finest: int, finest_mm: float) -> tuple[str, str, float, dict[str, Any]]:
    """snappyHexMesh geometry and refinementRegions entries for the regions a level refines, `n` levels past the finest surface cells
    (snappy level `finest`, `finest_mm` in size), with their volume in cells at that size (for the memory estimate) and a record of each."""
    geo, zones, cells, placed = "", "", 0.0, {}
    for name, n in sorted(levels.items()):
        reg = next(r for r in sim.regions if r.name == name)
        h = finest_mm / 2 ** n
        if reg.shape == "rotor_tip":
            o, ax, r_tip, t0, t1 = tip_band(geom, reg.body or rotor, reg.inside_mm)
            p1, p2 = o + (t0 - reg.axial_margin_mm) * ax, o + (t1 + reg.axial_margin_mm) * ax
            r_out, r_in = r_tip + reg.outside_mm, max(0.0, r_tip - reg.inside_mm)
            geo += (f" {name} {{ type searchableCone; point1 {_vec(p1 * MM)}; radius1 {r_out * MM:.9g}; innerRadius1 {r_in * MM:.9g}; "
                    f"point2 {_vec(p2 * MM)}; radius2 {r_out * MM:.9g}; innerRadius2 {r_in * MM:.9g}; }}")
            vol = math.pi * (r_out ** 2 - r_in ** 2) * float(np.linalg.norm(p2 - p1))
            placed[name] = {"shape": reg.shape, "tip_radius_mm": r_tip, "radii_mm": [r_in, r_out], "axial_mm": [t0 - reg.axial_margin_mm, t1 + reg.axial_margin_mm]}
        elif reg.shape == "cylinder":
            geo += f" {name} {{ type searchableCylinder; point1 {_vec(np.asarray(reg.point1) * MM)}; point2 {_vec(np.asarray(reg.point2) * MM)}; radius {reg.radius * MM:.9g}; }}"
            vol = math.pi * reg.radius ** 2 * float(np.linalg.norm(np.subtract(reg.point2, reg.point1)))
            placed[name] = {"shape": reg.shape}
        else:
            geo += f" {name} {{ type searchableBox; min {_vec(np.asarray(reg.min) * MM)}; max {_vec(np.asarray(reg.max) * MM)}; }}"
            vol = float(np.prod(np.subtract(reg.max, reg.min)))
            placed[name] = {"shape": reg.shape}
        zones += f" {name} {{ mode inside; levels ((1e15 {finest + n})); }}"
        cells += vol / h ** 3
        placed[name].update(level=finest + n, cell_mm=h, volume_mm3=vol)
    return geo, zones, cells, placed


def write_case(case_dir: Path, *, sim: Any, geom: Any, fluid: str, rotor: str | None, cell_mm: float, flow_m3s: float, omega: float,
               probes: list[list[float]], iterations: int, procs: int, turbulence_pct: float = TURBULENCE_PCT,
               regions: dict[str, int] | None = None) -> dict[str, Any]:
    roles = {b.name: b.role for b in geom.contract.boundaries if b.body == fluid}
    areas: dict[str, float] = {}
    counts = scaled_stl(geom.actx.results_dir / "boundaries" / f"{fluid}.stl", case_dir / "constant" / "triSurface" / "fluid.stl", areas=areas)
    missing = [lab for lab in roles if lab not in counts]
    if missing or "unassigned" in counts:
        raise ValueError(f"patch STL regions {sorted(counts)} do not match the fluid boundaries {sorted(roles)}")
    signed, dropped = areas.pop("_signed_volume", 0.0), int(areas.pop("_dropped", 0))
    if signed <= 0:  # snappyHexMesh's inside region and the surface level rely on outward triangles
        raise ValueError(f"the fluid surface {fluid}.stl encloses {signed:.3g} m3: its triangles face inward or it is open")
    fl = geom.fluid(fluid) or {}
    fv = next((f for f in geom.contract.fluid_volumes if f.body == fluid or f.name == fluid), None)
    lo, hi = np.asarray(fl.get("bbox_min") or geom.bbox(fluid)[0]) * MM, np.asarray(fl.get("bbox_max") or geom.bbox(fluid)[1]) * MM
    k, h_bg, n, lo, hi = background(lo, hi, cell_mm, float(sim.settings.get("background_cells_max", BACKGROUND_CELLS_MAX)))
    seed = np.asarray(fv.seed if fv else geom.contract.fluid_volumes[0].seed, float) * MM
    rho, mu = _v(sim, "fluidDensity"), _v(sim, "fluidViscosity")
    nu = mu / rho
    inlets = [lab for lab, r in roles.items() if r == "inlet"]
    outlets = [lab for lab, r in roles.items() if r == "outlet"]
    rotating = [lab for lab, r in roles.items() if r in ("rotating_wall", "moving_wall")]
    walls = [lab for lab, r in roles.items() if r not in ("inlet", "outlet", "rotating_wall", "moving_wall")]
    level = int(sim.settings.get("surface_level", 1)) + k
    patch_regions = "\n".join(f"            {lab} {{ name {lab}; }}" for lab in roles)
    patch_info = "\n".join(f"                {lab} {{ level ({level} {level + (1 if roles[lab] in ('rotating_wall', 'moving_wall') else 0)}); patchInfo {{ type {'patch' if roles[lab] in ('inlet', 'outlet') else 'wall'}; }} }}"
                           for lab in roles)
    inside = f"fluid {{ mode inside; levels ((1e15 {k})); }}" if k else ""
    n_layers = int(sim.settings.get("layers", 0))
    layer_patches = " ".join(f"{lab} {{ nSurfaceLayers {n_layers}; }}" for lab in walls + rotating) if n_layers else ""
    h_wall = cell_mm / 2 ** int(sim.settings.get("surface_level", 1))
    finest = level + (1 if rotating else 0)
    geo, zones, region_cells, placed = region_entries(sim, geom, rotor, regions or {}, finest, h_wall / (2 if rotating else 1))
    wall_area_mm2 = sum(areas.get(lab, 0.0) for lab in walls + rotating) / MM ** 2
    cells_estimate = (float(np.prod(n)) + float(fl.get("volume") or 0.0) / cell_mm ** 3 + 3.0 * wall_area_mm2 / h_wall ** 2 * (1 + n_layers / 3)
                      + region_cells)
    _write(case_dir / "system" / "blockMeshDict", "dictionary", "blockMeshDict", f"""
scale 1;
vertices ( ({lo[0]} {lo[1]} {lo[2]}) ({hi[0]} {lo[1]} {lo[2]}) ({hi[0]} {hi[1]} {lo[2]}) ({lo[0]} {hi[1]} {lo[2]})
           ({lo[0]} {lo[1]} {hi[2]}) ({hi[0]} {lo[1]} {hi[2]}) ({hi[0]} {hi[1]} {hi[2]}) ({lo[0]} {hi[1]} {hi[2]}) );
blocks ( hex (0 1 2 3 4 5 6 7) ({n[0]} {n[1]} {n[2]}) simpleGrading (1 1 1) );
boundary ( background {{ type patch; faces ( (0 3 2 1) (4 5 6 7) (0 1 5 4) (2 3 7 6) (0 4 7 3) (1 2 6 5) ); }} );
""")
    max_cells = int(max(8e6, 3 * cells_estimate))
    _write(case_dir / "system" / "snappyHexMeshDict", "dictionary", "snappyHexMeshDict", f"""
castellatedMesh true; snap true; addLayers {'true' if n_layers else 'false'};
geometry {{ fluid.stl {{ type triSurfaceMesh; name fluid; regions {{
{patch_regions}
        }} }}{geo} }}
castellatedMeshControls {{ maxLocalCells {max_cells}; maxGlobalCells {max_cells}; minRefinementCells 0; nCellsBetweenLevels 2; maxLoadUnbalance 0.1;
    features (); refinementSurfaces {{ fluid {{ level ({level} {level}); regions {{
{patch_info}
            }} }} }}
    resolveFeatureAngle 30; refinementRegions {{ {inside}{zones} }}; locationInMesh {_vec(seed)}; allowFreeStandingZoneFaces true; }}
snapControls {{ nSmoothPatch 3; tolerance 2.0; nSolveIter 50; nRelaxIter 5; nFeatureSnapIter 10; implicitFeatureSnap true; explicitFeatureSnap false; multiRegionFeatureSnap false; }}
addLayersControls {{ relativeSizes true; layers {{ {layer_patches} }}; expansionRatio {float(sim.settings.get('layer_expansion', 1.2)):g};
    finalLayerThickness {float(sim.settings.get('final_layer_thickness', 0.3)):g}; minThickness 0.1; nGrow 0; featureAngle 60; nRelaxIter 3;
    nSmoothSurfaceNormals 1; nSmoothNormals 3; nSmoothThickness 10; maxFaceThicknessRatio 0.5; maxThicknessToMedialRatio 0.3; minMedialAxisAngle 90; nBufferCellsNoExtrude 0; nLayerIter 50; }}
meshQualityControls {{ maxNonOrtho 65; maxBoundarySkewness 20; maxInternalSkewness 4; maxConcave 80; minVol 1e-18; minTetQuality 1e-15; minArea -1; minTwist 0.02;
    minDeterminant 0.001; minFaceWeight 0.05; minVolRatio 0.01; minTriangleTwist -1; nSmoothScale 4; errorReduction 0.75; }}
mergeTolerance 1e-6;
""")
    zone = ""
    mrf = ""
    if rotor is not None and omega:
        o, ax = geom.joint_axis(geom.joint_of(rotor).name)
        _, r_max = geom.radial_extent(rotor)
        lo_r, hi_r = np.asarray(geom.bbox(rotor)[0]), np.asarray(geom.bbox(rotor)[1])
        corners = np.array([[x, y, z] for x in (lo_r[0], hi_r[0]) for y in (lo_r[1], hi_r[1]) for z in (lo_r[2], hi_r[2])])
        t = (corners - o) @ ax
        margin = float(sim.settings.get("mrf_margin_mm", max(0.5, 0.05 * r_max)))
        p1, p2 = (o + (t.min() - margin) * ax) * MM, (o + (t.max() + margin) * ax) * MM
        zone = f"{{ name rotor; type cellZoneSet; action new; source cylinderToCell; p1 {_vec(p1)}; p2 {_vec(p2)}; radius {(r_max + margin) * MM:.9g}; }}"
        mrf = f"MRF1 {{ cellZone rotor; active yes; nonRotatingPatches ({' '.join(walls + inlets + outlets)}); origin {_vec(o * MM)}; axis {_vec(ax)}; omega {omega:.9g}; }}"
    _write(case_dir / "system" / "topoSetDict", "dictionary", "topoSetDict", f"actions ( {zone} );")
    _write(case_dir / "constant" / "MRFProperties", "dictionary", "MRFProperties", mrf)
    _write(case_dir / "constant" / "transportProperties", "dictionary", "transportProperties", f"transportModel Newtonian; nu {nu:.9g};")
    _write(case_dir / "constant" / "turbulenceProperties", "dictionary", "turbulenceProperties", "simulationType RAS; RAS { RASModel kOmegaSST; turbulence on; printCoeffs off; }")
    d_in = float(sim.settings.get("inlet_diameter_mm", 10.0)) * MM
    area_in = math.pi * d_in ** 2 / 4
    u_in = flow_m3s / area_in
    k_in = 1.5 * (turbulence_pct / 100.0 * u_in) ** 2
    om_in = math.sqrt(k_in) / (0.09 ** 0.25 * 0.07 * d_in)
    bc = {
        "U": ("volVectorField", "[0 1 -1 0 0 0 0]", "uniform (0 0 0)", {"inlet": f"type flowRateInletVelocity; volumetricFlowRate {flow_m3s:.9g}; value uniform (0 0 0);",
                                                                          "outlet": "type inletOutlet; inletValue uniform (0 0 0); value uniform (0 0 0);",
                                                                          "rotating_wall": "type fixedValue; value uniform (0 0 0);", "wall": "type noSlip;"}),
        "p": ("volScalarField", "[0 2 -2 0 0 0 0]", "uniform 0", {"inlet": "type zeroGradient;", "outlet": "type fixedValue; value uniform 0;",
                                                                  "rotating_wall": "type zeroGradient;", "wall": "type zeroGradient;"}),
        "k": ("volScalarField", "[0 2 -2 0 0 0 0]", f"uniform {k_in:.9g}", {"inlet": f"type fixedValue; value uniform {k_in:.9g};",
                                                                            "outlet": f"type inletOutlet; inletValue uniform {k_in:.9g}; value uniform {k_in:.9g};",
                                                                            "rotating_wall": f"type kqRWallFunction; value uniform {k_in:.9g};", "wall": f"type kqRWallFunction; value uniform {k_in:.9g};"}),
        "omega": ("volScalarField", "[0 0 -1 0 0 0 0]", f"uniform {om_in:.9g}", {"inlet": f"type fixedValue; value uniform {om_in:.9g};",
                                                                                 "outlet": f"type inletOutlet; inletValue uniform {om_in:.9g}; value uniform {om_in:.9g};",
                                                                                 "rotating_wall": f"type omegaWallFunction; value uniform {om_in:.9g};", "wall": f"type omegaWallFunction; value uniform {om_in:.9g};"}),
        "nut": ("volScalarField", "[0 2 -1 0 0 0 0]", "uniform 0", {"inlet": "type calculated; value uniform 0;", "outlet": "type calculated; value uniform 0;",
                                                                    "rotating_wall": "type nutkWallFunction; value uniform 0;", "wall": "type nutkWallFunction; value uniform 0;"}),
    }
    for field, (cls, dim, internal, by_role) in bc.items():
        patches = "\n".join(f"    {lab} {{ {by_role['rotating_wall' if r in ('rotating_wall', 'moving_wall') else (r if r in ('inlet', 'outlet') else 'wall')]} }}" for lab, r in roles.items())
        _write(case_dir / "0" / field, cls, field, f"dimensions {dim};\ninternalField {internal};\nboundaryField {{\n{patches}\n    \".*\" {{ type zeroGradient; }}\n}}")
    fo = []
    for tag, labs in (("pIn", inlets), ("pOut", outlets)):
        for lab in labs:
            fo.append(f"{tag}_{lab} {{ type surfaceFieldValue; libs (fieldFunctionObjects); writeControl timeStep; writeInterval 10; log false; writeFields false; "
                      f"regionType patch; name {lab}; operation areaAverage; fields (p); }}")
            fo.append(f"q{tag[1:]}_{lab} {{ type surfaceFieldValue; libs (fieldFunctionObjects); writeControl timeStep; writeInterval 10; log false; writeFields false; "
                      f"regionType patch; name {lab}; operation sum; fields (phi); }}")
    if rotating and rotor is not None and omega:
        o, _ = geom.joint_axis(geom.joint_of(rotor).name)
        fo.append(f"torque {{ type forces; libs (forces); writeControl timeStep; writeInterval 10; log false; patches ({' '.join(rotating)}); rho rhoInf; rhoInf {rho:.9g}; CofR {_vec(o * MM)}; }}")
    if probes:
        fo.append(f"probes {{ type probes; libs (sampling); writeControl timeStep; writeInterval 10; fields (U p); probeLocations ({' '.join(_vec(np.asarray(p) * MM) for p in probes)}); }}")
    functions = "\n    ".join(fo)
    _write(case_dir / "system" / "controlDict", "dictionary", "controlDict", f"""
application simpleFoam; startFrom latestTime; startTime 0; stopAt endTime; endTime {iterations}; deltaT 1;
writeControl timeStep; writeInterval {iterations}; purgeWrite 1; writeFormat ascii; writePrecision 8; writeCompression off; timeFormat general; timePrecision 6; runTimeModifiable false;
functions
{{
    {functions}
}}
""")
    _write(case_dir / "system" / "fvSchemes", "dictionary", "fvSchemes", """
ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; limited cellLimited Gauss linear 1; grad(U) $limited; grad(k) $limited; grad(omega) $limited; }
divSchemes { default none; div(phi,U) bounded Gauss linearUpwind limited; turbulence bounded Gauss upwind; div(phi,k) $turbulence; div(phi,omega) $turbulence;
    div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear limited corrected 0.33; }
interpolationSchemes { default linear; }
snGradSchemes { default limited corrected 0.33; }
wallDist { method meshWave; }
""")
    _write(case_dir / "system" / "fvSolution", "dictionary", "fvSolution", """
solvers { p { solver GAMG; smoother GaussSeidel; tolerance 1e-7; relTol 0.05; } "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-8; relTol 0.1; } }
SIMPLE { nNonOrthogonalCorrectors 1; consistent yes; residualControl { p 1e-4; U 1e-5; "(k|omega)" 1e-5; } }
relaxationFactors { equations { U 0.8; ".*" 0.8; } fields { p 1; } }
""")
    _write(case_dir / "system" / "decomposeParDict", "dictionary", "decomposeParDict", f"numberOfSubdomains {procs}; method scotch;")
    inlet_area = sum(areas.get(lab, 0.0) for lab in inlets)
    return {"cells_background": n.tolist(), "cell_mm": cell_mm, "cell_background_mm": h_bg, "surface_level": level, "inside_level": k, "wall_cell_mm": h_wall,
            "layers": n_layers, "cells_estimate": round(cells_estimate), "fluid_signed_volume_m3": signed, "degenerate_facets_dropped": dropped,
            "seed_m": seed.tolist(), "patches": roles, "refinement_regions": placed,
            "regions": counts, "nu": nu, "u_inlet": u_in, "flow_m3s": flow_m3s, "omega": omega, "inlet_turbulence_pct": turbulence_pct, "inlet_area_m2": inlet_area,
            "inlet_dynamic_pa": 0.5 * rho * (flow_m3s / inlet_area) ** 2 if inlet_area > 0 else None}


SCRIPT = """source {bashrc}
set -e
cd /case
export OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
blockMesh > log.blockMesh 2>&1
snappyHexMesh -overwrite > log.snappyHexMesh 2>&1
topoSet > log.topoSet 2>&1 || true
checkMesh > log.checkMesh 2>&1 || true
if [ {procs} -gt 1 ]; then decomposePar -force > log.decomposePar 2>&1 && mpirun -np {procs} simpleFoam -parallel > log.simpleFoam 2>&1 && reconstructPar -latestTime > log.reconstructPar 2>&1
else simpleFoam > log.simpleFoam 2>&1; fi
"""


def _table(case_dir: Path, name: str, fname: str) -> np.ndarray:
    """A function object's rows (time first, vector parentheses dropped) across every start-time directory (a run restarted from a
    later time writes a new one); later rows replace earlier ones from the same iteration on."""
    def start(p: Path) -> float:
        try:
            return float(p.parent.name)
        except ValueError:
            return -1.0

    out = np.empty((0, 0))
    for path in sorted((case_dir / "postProcessing" / name).glob(f"*/{fname}"), key=start):
        rows = [ln.replace("(", " ").replace(")", " ").split() for ln in path.read_text(errors="replace").splitlines() if ln.strip() and not ln.startswith("#")]
        tab = np.asarray(rows, float) if rows else np.empty((0, 0))
        if tab.size:
            out = np.vstack([out[out[:, 0] < tab[0, 0]], tab]) if out.size else tab
    return out


def _case_hash(case_dir: Path) -> str:
    """Digest of everything a run reads, so a finished case is reused only when nothing it depends on changed."""
    import hashlib

    h = hashlib.sha256()
    files = [case_dir / "Allrun", *sorted((case_dir / "system").glob("*")), *sorted((case_dir / "0").glob("*")),
             *sorted((case_dir / "constant").glob("*Properties")), case_dir / "constant" / "triSurface" / "fluid.stl"]
    for f in files:
        if f.is_file():
            h.update(f.relative_to(case_dir).as_posix().encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def patch_faces(case_dir: Path) -> dict[str, int]:
    """Face count per patch of the final mesh (constant/polyMesh/boundary)."""
    f = case_dir / "constant" / "polyMesh" / "boundary"
    if not f.exists():
        return {}
    return {m.group(1): int(m.group(2)) for m in re.finditer(r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);", f.read_text(errors="replace"))}


def parse_results(case_dir: Path, rho: float, omega: float) -> dict[str, Any]:
    """Iteration histories of the function objects (patch pressures in Pa, patch flows, rotor moment, probes) with the patch values as
    their means over the last TAIL of the iterations; residuals, iterations and convergence from the solver log; the mesh's cells."""
    out: dict[str, Any] = {"patch_pressure_pa": {}, "patch_flow_m3s": {}, "history": {}}
    h = out["history"]
    for d in sorted((case_dir / "postProcessing").glob("*")) if (case_dir / "postProcessing").exists() else []:
        tab = _table(case_dir, d.name, "surfaceFieldValue.dat")
        if not tab.size:
            continue
        kind, _, lab = d.name.partition("_")
        if kind in ("pIn", "pOut"):
            h[f"p_{lab}"] = rho * tab[:, -1]
            out["patch_pressure_pa"][lab] = tail(h[f"p_{lab}"])["mean"]
        elif kind in ("qIn", "qOut"):
            h[f"q_{lab}"] = tab[:, -1]
            out["patch_flow_m3s"][lab] = tail(h[f"q_{lab}"])["mean"]
    tab = _table(case_dir, "torque", "moment.dat")
    if tab.size:
        h["moment"] = tab[:, 1:4]
        out["moment_nm"] = h["moment"][-tail(tab[:, 1])["samples"]:].mean(axis=0).tolist()
    tab = _table(case_dir, "probes", "U")
    if tab.size:
        h["probe_u"] = tab[:, 1:].reshape(len(tab), -1, 3)
    tab = _table(case_dir, "probes", "p")
    if tab.size:
        h["probe_p"] = rho * tab[:, 1:]
    log = case_dir / "log.simpleFoam"
    if log.exists():
        text = log.read_text(errors="replace")
        res = {}
        for fld in ("Ux", "Uy", "Uz", "p", "k", "omega"):
            m = re.findall(rf"Solving for {fld}, Initial residual = ([0-9.eE+-]+)", text)
            if m:
                res[fld] = float(m[-1])
        out["final_residuals"] = res
        out["iterations"] = len(re.findall(r"^Time = ", text, flags=re.MULTILINE))
        out["converged"] = "SIMPLE solution converged" in text
    cm = case_dir / "log.checkMesh"
    if cm.exists():
        m = re.search(r"cells:\s+(\d+)", cm.read_text(errors="replace"))
        out["cells"] = int(m.group(1)) if m else None
        out["mesh_ok"] = "Mesh OK." in cm.read_text(errors="replace")
    return out


def _history(o: Any, h: dict[str, Any], info: dict[str, Any], geom: Any, rotor: str | None, omega: float, probe_obs: list[Any]) -> np.ndarray | None:
    """An observable's value at every written iteration of one run."""
    pin = [h[f"p_{lab}"] for lab, role in info["patches"].items() if role == "inlet" and f"p_{lab}" in h]
    pout = [h[f"p_{lab}"] for lab, role in info["patches"].items() if role == "outlet" and f"p_{lab}" in h]
    m = min((len(x) for x in pin + pout), default=0)
    rise = np.mean([x[-m:] for x in pout], axis=0) - np.mean([x[-m:] for x in pin], axis=0) if pin and pout and m else None
    if o.quantity == "pressure_rise" and o.location is None:
        return rise
    if o.quantity == "pressure_rise_total_to_static":
        return rise - info["inlet_dynamic_pa"] if rise is not None and info.get("inlet_dynamic_pa") is not None else None
    if o.quantity == "torque" and "moment" in h and rotor is not None:
        _, ax = geom.joint_axis(geom.joint_of(rotor).name)
        return -(h["moment"] @ ax) * math.copysign(1.0, omega)
    if o in probe_obs and o.quantity == "pressure":
        return h["probe_p"][:, probe_obs.index(o)] if "probe_p" in h else None
    if o in probe_obs and "probe_u" in h:
        u = h["probe_u"][:, probe_obs.index(o), :]
        return {"velocity_magnitude": np.linalg.norm(u, axis=1), "velocity_x": u[:, 0], "velocity_y": u[:, 1], "velocity_z": u[:, 2]}.get(o.quantity)
    return None


def finished(geom: Any, sim_id: str, name: str, key: str) -> str | None:
    """Where a finished run with these inputs lies (this attempt's work directory or the last one's), if anywhere."""
    for d in (geom.work_dir(sim_id) / name, geom.previous_dir(sim_id) / name):
        if (d / "result.json").exists() and load_json(d / "result.json").get("hash") == key:
            return str(d)
    return None


def run(sim: Any, obs: list[Any], geom: Any, cases: dict[str, Any], *, dry_root: Path | None = None) -> dict[str, Any]:
    """`dry_root`: write every level's case there instead, and report whether a finished run would be reused; nothing runs."""
    rt = None if dry_root else runtime.detect()
    if rt is None and not dry_root:
        return unavailable("no container runtime is running (Apple `container system start`, or OrbStack/Docker)")
    image = str(sim.settings.get("image", IMAGE))
    if rt and not runtime.has_image(image, rt):
        return unavailable(f"image {image} is not pulled (`container image pull --arch arm64 {image}`)")
    fluid = str(sim.settings.get("fluid") or next(b for b in sim.bodies if geom.contract.part(b).role == "fluid"))
    rotor = sim.settings.get("rotor") or next((b for b in sim.bodies if b != fluid and geom.joint_of(b) is not None and geom.joint_of(b).rotates), None)
    rho = _v(sim, "fluidDensity")
    cell0 = float(sim.settings.get("cell_mm", 2.0))
    iterations = int(sim.settings.get("iterations", 600))
    procs = int(sim.settings.get("processes", 8))
    probe_obs = [o for o in obs if o.location is not None]
    probes = [list(o.location) for o in probe_obs]
    levels = sim.levels()
    rows: dict[str, list[dict[str, Any]]] = {}
    runs: list[dict[str, Any]] = []
    errors: list[str] = []
    per_case: dict[str, dict[str, Any]] = {}
    mem_cap = float(sim.settings.get("memory_cap_gb", MEMORY_CAP_GB))
    skipped: list[str] = []
    for cid in sim.cases or [None]:
        case = cases.get(cid) if cid else None
        flow, omega = _case_values(sim, geom, case, rotor)
        ti = inlet_turbulence(sim, case)
        for lv in levels:  # coarse to fine: the last value an observable gets is the finest level's
            f = lv.factor
            case_dir = (dry_root / sim.id if dry_root else geom.work_dir(sim.id)) / f"{cid or 'case'}-level-{lv.label}"
            info = write_case(case_dir, sim=sim, geom=geom, fluid=fluid, rotor=rotor, cell_mm=cell0 * f, flow_m3s=flow, omega=omega, probes=probes,
                              iterations=lv.iterations or iterations, procs=procs, turbulence_pct=ti, regions=lv.regions)
            (case_dir / "Allrun").write_text(SCRIPT.format(bashrc=BASHRC, procs=procs), encoding="utf-8")
            # blockMesh holds the background box (about 0.8 GB per million hexes); snappyHexMesh and the solver about 1.5 GB per million fluid cells
            need_gb = max(float(np.prod(info["cells_background"])) * 0.8e-6, info["cells_estimate"] * 1.5e-6)
            info["memory_estimate_gb"] = round(need_gb, 1)
            where = {"case": cid, "level": f, "label": lv.label, "level_regions": lv.regions}
            if dry_root:
                runs.append({**where, **info, "reuse": finished(geom, sim.id, case_dir.name, _case_hash(case_dir)), "skipped": need_gb > mem_cap})
                continue
            if need_gb > mem_cap:
                errors.append(f"{cid} level {lv.label}: about {info['cells_estimate'] / 1e6:.1f} M cells need {need_gb:.0f} GB (> {mem_cap:g} GB); level skipped")
                skipped.append(errors[-1])
                runs.append({**where, **info, "skipped": errors[-1]})
                continue
            key = _case_hash(case_dir)
            adopt(case_dir, geom.previous_dir(sim.id) / case_dir.name, key)
            done = case_dir / "result.json"
            prev = load_json(done) if done.exists() else {}
            if prev.get("hash") == key:
                r = {**prev.get("run", {}), "reused": True}
            elif recovered(case_dir, key, lv.iterations or iterations, procs):
                r = {"code": 0, "runtime": rt, "recovered": True}
            else:
                fresh(case_dir)
                dump_json(case_dir / "started.json", {"hash": key})
                r = container_run(image, case_dir, rt=rt, procs=procs, need_gb=need_gb, mem_cap=mem_cap, settings=sim.settings)
            res = parse_results(case_dir, rho, omega)
            faces = patch_faces(case_dir)
            runs.append({**where, **info, **r, "patch_faces": faces, **({"layer_coverage": layer_report(case_dir)} if info["layers"] else {}),
                         **{k: res.get(k) for k in ("cells", "mesh_ok", "iterations", "converged", "final_residuals")}})
            if r.get("code") in (124, 137):
                why = f"timed out after {r.get('seconds')} s (timeout_s)" if r["code"] == 124 else f"was killed at {r.get('memory')} (out of memory)"
                errors.append(f"OpenFOAM run ({cid}, level {lv.label}) {why}")
                skipped.append(errors[-1])
                continue
            empty = [lab for lab, role in info["patches"].items() if role in ("inlet", "outlet") and not faces.get(lab)]
            if faces and (empty or faces.get("background")):
                errors.append(f"snappyHexMesh ({cid}, level {lv.label}): port patches without faces {empty}, {faces.get('background', 0)} faces left on the "
                              f"background box; the fluid surface is open or a port is not resolved at cell_mm {cell0 * f:g}")
                continue
            if r.get("code") != 0 or not res.get("patch_pressure_pa"):
                log_tail = next((p.read_text(errors="replace")[-800:] for p in sorted(case_dir.glob("log.*"), key=lambda p: p.stat().st_mtime, reverse=True)), "")
                errors.append(f"OpenFOAM run failed ({cid}, level {lv.label}, exit {r.get('code')}): {log_tail}")
                continue
            if not r.get("reused"):
                dump_json(done, {"hash": key, "run": {k: v for k, v in r.items() if k in ("code", "seconds", "digest", "runtime", "recovered")}})
                for p in case_dir.glob("processor[0-9]*"):  # reconstructPar merged them; they double a case's size
                    shutil.rmtree(p)
            per_case.setdefault(cid or "case", {})[lv.label] = res
            for o in obs:
                if o.case not in (cid, None):
                    continue
                y = _history(o, res["history"], info, geom, rotor, omega, probe_obs)
                if y is not None and len(y):
                    st = tail(y)
                    rows.setdefault(o.id, []).append({"label": lv.label, "factor": f, "regions": lv.regions, "value": st["mean"], "last": st["last"],
                                                      "u_iteration": st["std"], "drift": st["drift"], "samples": st["samples"], "cells": res.get("cells"),
                                                      "iterations": res.get("iterations")})
    if dry_root:
        return {"status": "dry-run", "runs": runs, "observables": {}}
    if not per_case:
        return failed("; ".join(errors) or "no OpenFOAM case ran", runs=runs)
    flows = []
    for byf in per_case.values():
        q = list(byf.values())[-1]["patch_flow_m3s"]
        if q:
            qin = sum(v for k, v in q.items() if v < 0)
            flows.append(abs(sum(q.values())) / (abs(qin) or 1.0))
    ref_tol = float(sim.settings.get("refinement_tolerance", 0.05))
    order = float(sim.settings.get("formal_order", FORMAL_ORDER))
    studies = {o.id: study(rows.get(o.id, []), expected=len(levels), tolerance=ref_tol, formal_order=order) for o in obs}
    out = {o.id: predict(rows.get(o.id, []), studies[o.id], o.unit, o.case) for o in obs}
    tol = float(sim.settings.get("mass_balance_tolerance", 0.01))
    worst = max(flows, default=None)
    ref = refinement(studies, ref_tol, skipped) if len(levels) > 1 else None
    n_layers = int(sim.settings.get("layers", 0))
    return {"status": "ok", "solver": {"name": "openfoam", "image": image, "runtime": rt, "digest": runs[-1].get("digest") if runs else None},
            "model": "steady MRF simpleFoam, k-omega SST", "observables": out, "runs": runs, "errors": errors,
            "conservation": {"mass_balance": {"value": worst, "tolerance": tol, "ok": worst is not None and worst <= tol}} if flows else {},
            "refinement": ref,
            "assumptions": ["steady frozen-rotor MRF (no blade-passage unsteadiness)",
                            f"k-omega SST with wall functions, {f'{n_layers} prism layers on the walls' if n_layers else 'no prism layers'}",
                            "incompressible Newtonian fluid with the stated density and viscosity",
                            f"each value is the mean over the last {TAIL:.0%} of a run's iterations; u_iteration is its spread there"]}

"""Load, validate, and atomically publish design bundles."""

from __future__ import annotations

import math
import os
import re
from itertools import pairwise
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from opencad.paths import (
    ASSEMBLY_FILE,
    BRIEF_FILE,
    CONTRACT_FILE,
    DESIGNS,
    NESTED,
    TEMPLATE,
    check_part_name,
    design_dir,
    design_name,
)
from opencad.schemas import AssemblyContract, PartContract, SymmetrySpec, Vec3

PLACEHOLDERS = ("new-part", "<intent>", "<part>", "REPLACE ME", "TODO:")
ALLOWED_TOP = {CONTRACT_FILE, BRIEF_FILE, "sources", "reference", "ecr"}  # ecr/<label>/ holds revised contracts written by `opencad ecr`
ALLOWED_REFERENCE_PREFIXES = ("profile.", "reference.", "reference-sections", "silhouette-")


def _allowed_reference(name: str) -> bool:
    return name.startswith(ALLOWED_REFERENCE_PREFIXES)


class ContractError(ValueError):
    pass


def load_contract(path: Path) -> PartContract:
    path = Path(path)
    if path.is_dir():
        path = path / CONTRACT_FILE
    if not path.exists():
        raise ContractError(f"missing {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        c = PartContract.model_validate(data)
    except ValidationError as e:
        raise ContractError(f"{path}: {e}") from e
    except yaml.YAMLError as e:
        raise ContractError(f"{path}: YAML error: {e}") from e
    return c


NON_ANALYTIC_KINDS = ("loft", "sweep")  # no closed-form volume: a first-order estimate needs a wide band
UNCERTAIN_KINDS = ("other", "shell", "fillet", "chamfer")  # analytic in principle, often estimated: warn
SURFACE_CLEARANCE_MM = 1.0
DERIVED_BAND_MIN_REL = 0.001  # a hand-derived blend term is rarely closer than 0.5 % of itself


def _axis_dist(point, cy) -> tuple[float, float]:
    """(distance from the point to the cylinder axis, axial parameter of the point relative to cy.point)."""
    p = [a - b for a, b in zip(point, cy.point)]
    d = list(cy.direction)
    n = math.sqrt(sum(x * x for x in d)) or 1.0
    d = [x / n for x in d]
    t = sum(a * b for a, b in zip(p, d))
    perp = [a - t * b for a, b in zip(p, d)]
    return math.sqrt(sum(x * x for x in perp)), t


def _in_axial_range(cy, t: float, slack: float) -> bool:
    if cy.t_range is not None:
        lo, hi = cy.t_range
    elif cy.length is not None:
        lo, hi = -cy.length / 2, cy.length / 2
    else:
        return True
    return lo - slack <= t <= hi + slack


def lint_contract(c: PartContract) -> tuple[list[str], list[str]]:
    """Drafting rules the geometry checks cannot recover from: (problems, warnings).

    Learned from the 2026-09-19 Fusion recon runs: passages sealed by a radius smaller than their port, probe
    points inside a skin, blind-floor normals pointing into the material, first-order edit estimates on
    non-analytic features, sweep ranges that overlap the declared infeasible values. From the NIST AM artifact
    (2026-09-20): a blockout band below the finished volume.
    """
    problems: list[str] = []
    warnings: list[str] = []
    a = c.acceptance
    # a "partial cylindrical surface" (a bend wall or blend, per the drafter's description) is not a bore that opens a port
    holes = [cy for cy in a.cylinders if cy.kind == "hole" and "partial" not in (cy.description or "").lower()]
    # 1. a closing radius can only seal ports narrower than itself: through bores need plugs
    for ps in a.passages:
        if ps.seal_radius is None or ps.plugs:
            continue
        for label, pt in (("point_a", ps.point_a), ("point_b", ps.point_b)):
            for cy in holes:
                dist, t = _axis_dist(pt, cy)
                if dist <= cy.r + 1e-6 and cy.r >= ps.seal_radius and _in_axial_range(cy, t, 1.0):
                    problems.append(f"passage {ps.name}: {label} {list(pt)} lies in hole {cy.name} (r {cy.r:g}) which is not narrower than seal_radius {ps.seal_radius:g}; "
                                    "a closing radius cannot seal that port: use `plugs` over the bore mouths")
                    break
    # 2. void probe points and passage ends must sit clear of every declared surface (a point 0.16 mm inside a skin lands in the breakout)
    void_points: list[tuple[str, Vec3]] = []
    for ps in a.passages:
        void_points += [(f"passage {ps.name} point_a", ps.point_a), (f"passage {ps.name} point_b", ps.point_b)]
    for pr in a.probes:
        if pr.state == "void":
            void_points += [(f"probe {pr.name}", p) for p in pr.points]
    for label, pt in void_points:
        in_hole = any(_axis_dist(pt, cy)[0] < cy.r and _in_axial_range(cy, _axis_dist(pt, cy)[1], 0.0) for cy in holes)
        for cy in a.cylinders:
            dist, t = _axis_dist(pt, cy)
            if not _in_axial_range(cy, t, 0.0):
                continue
            if cy.kind == "pin" and not in_hole and cy.r - SURFACE_CLEARANCE_MM < dist < cy.r:
                # just under a boss/shaft surface with no declared bore there: the 15317 probes sat 0.15 mm inside the flange OD, in the breakout
                problems.append(f"{label} {list(pt)} lies {cy.r - dist:.2f} mm inside the surface of pin {cy.name} (r {cy.r:g}); void points need >= {SURFACE_CLEARANCE_MM:g} mm clearance")
                break
            if cy.kind == "hole" and cy.r <= dist < cy.r + SURFACE_CLEARANCE_MM:
                warnings.append(f"{label} {list(pt)} is {dist - cy.r:.2f} mm outside hole {cy.name} (r {cy.r:g}), in its wall; void points need >= {SURFACE_CLEARANCE_MM:g} mm clearance")
                break
        if in_hole:
            continue  # inside a declared bore: the bore's own mouth faces are not walls to clear
        for f in a.faces:
            if f.center is None or f.area is None:
                continue
            ax = "xyz".index(f.plane)
            if abs(pt[ax] - f.at) < SURFACE_CLEARANCE_MM:
                u, v = [i for i in range(3) if i != ax]
                if math.dist([pt[u], pt[v]], list(f.center)) <= math.sqrt(f.area / math.pi):
                    warnings.append(f"{label} {list(pt)} is {abs(pt[ax] - f.at):.2f} mm from face {f.name} ({f.plane} = {f.at}); void points need >= {SURFACE_CLEARANCE_MM:g} mm clearance unless they sit in an opening of that face")
                    break
    # 3. a blind hole's floor face faces the mouth
    for cy in holes:
        if cy.length is None and cy.t_range is None:
            continue
        lo, hi = cy.t_range if cy.t_range is not None else (-cy.length / 2, cy.length / 2)
        d = list(cy.direction)
        n = math.sqrt(sum(x * x for x in d)) or 1.0
        d = [x / n for x in d]
        ax = max(range(3), key=lambda i: abs(d[i]))
        if abs(d[ax]) < 0.999:
            continue
        ends = [[p + lo * x for p, x in zip(cy.point, d)], [p + hi * x for p, x in zip(cy.point, d)]]
        for f in a.faces:
            if f.plane != "xyz"[ax] or f.area is None or abs(f.area - math.pi * cy.r ** 2) > 0.2 * math.pi * cy.r ** 2:
                continue
            for k, end in enumerate(ends):
                if abs(f.at - end[ax]) > 0.05:
                    continue
                if f.center is not None:
                    u, v = [i for i in range(3) if i != ax]
                    if math.dist(list(f.center), [cy.point[u], cy.point[v]]) > 0.5:
                        continue
                mouth = ends[1 - k]
                want = "+" if mouth[ax] > end[ax] else "-"
                if f.normal != want:
                    problems.append(f"face {f.name} is the floor of blind hole {cy.name} at {f.plane} = {f.at}: its outward normal must point toward the mouth ({want}), not {f.normal}")
    # 4. first-order volume estimates on non-analytic features
    kinds_by_param: dict[str, set[str]] = {}
    for feat in c.features:
        for pn in feat.parameters:
            kinds_by_param.setdefault(pn, set()).add(feat.kind)
    for p in c.parameters:
        et = p.edit_test
        if et is None:
            continue
        kinds = kinds_by_param.get(p.name, set())
        non_analytic = kinds & set(NON_ANALYTIC_KINDS)
        uncertain = kinds & set(UNCERTAIN_KINDS)
        if et.expect.volume_delta is not None and et.expect.tolerance_rel < 0.3:
            if non_analytic:
                problems.append(f"edit_test {p.name}: volume_delta {et.expect.volume_delta:g} drives {sorted(non_analytic)} features, which have no analytic volume; "
                                "set expect.tolerance_rel >= 0.3 or state `direction` only")
            elif uncertain:
                warnings.append(f"edit_test {p.name}: volume_delta {et.expect.volume_delta:g} drives {sorted(uncertain)} features; derive it from the geometry (formula in the brief) "
                                "or widen expect.tolerance_rel")
        # 5. a sweep value that is also declared infeasible contradicts itself; a wide sweep is a warning
        if et.sweep is not None:
            infeasible = {round(p.value + dlt, 9) for dlt in et.infeasible_deltas}
            clash = [v for v in et.sweep.sequence() if round(v, 9) in infeasible]
            if clash:
                problems.append(f"edit_test {p.name}: sweep values {clash} are also declared infeasible")
            span = max(et.sweep.sequence()) - min(et.sweep.sequence())
            if p.value and span > abs(p.value):
                warnings.append(f"edit_test {p.name}: the sweep spans {span:g} around a value of {p.value:g}; state the feasible interval in the brief and keep the sweep inside it")
    # 6. the blockout is the uncut primary solids filling the finished part's envelope: it cannot hold less material than the finished part
    if a.blockout is not None and a.volume is not None and a.blockout.volume_max < a.volume.expected:
        problems.append(f"acceptance.blockout: volume_max {a.blockout.volume_max:g} is below the finished volume {a.volume.expected:g}; a blockout smaller than the finished solid cannot fill the envelope: "
                        "band the primary solids that reach the envelope extremes (base plus the tallest boss, pin or lug)")
    # 7. a passage the worker can satisfy with a hollow of any size, or whose endpoint sits in the very port a plug closes, checks little:
    #    the voron ducts read 5/5 on inlet-mouth endpoints while the scorer's mid-duct points sat in material (2026-09-20)
    for ps in a.passages:
        if ps.expect_connected and ps.volume_min is None and ps.volume_max is None:
            warnings.append(f"passage {ps.name}: no volume_min/volume_max; a connected pinhole would pass. Band the air volume from the drawing (cross-section x path length)")
        for label, pt in (("point_a", ps.point_a), ("point_b", ps.point_b)):
            for lo, hi in ps.plugs:
                if all(l - 1.0 <= x <= h + 1.0 for x, l, h in zip(pt, lo, hi)):
                    warnings.append(f"passage {ps.name}: {label} {list(pt)} lies inside or within 1 mm of plug {[list(lo), list(hi)]}; an endpoint at a sealed port measures the plug, not the duct: move it to a mid-duct station")
                    break
    # 8. a sheet-stated section area with a wide band is a drafting hedge, not a check
    for s in a.sections:
        if s.expect.area is not None and s.expect.area_tolerance_rel > 0.10:
            warnings.append(f"section {s.id}: area band {s.expect.area_tolerance_rel:.0%} on a stated area {s.expect.area:g}; reference-derived areas hold within 10 %: tighten or drop the area")
    # 9. the symmetry check samples a tessellation whose blend edges carry up to ~0.1 mm of mesh error
    sym_max = SymmetrySpec.model_fields["max_deviation"].default
    sym_p95 = SymmetrySpec.model_fields["p95_deviation"].default
    for s in a.symmetry:
        if (s.max_deviation < sym_max or s.p95_deviation < sym_p95) and not s.source:
            problems.append(f"symmetry {s.name}: max {s.max_deviation:g} / p95 {s.p95_deviation:g} mm is tighter than the {sym_max:g} / {sym_p95:g} mm defaults; "
                            "the check measures a tessellation whose blends carry up to 0.1 mm of mesh error. Use the defaults, or set `source` to the document that states the tighter band")
    # 10. a derived volume or area on blended geometry banded tighter than its derivation turns an arithmetic slip into a correction turn
    blends = sorted({f.kind for f in c.features} & set(NON_ANALYTIC_KINDS + UNCERTAIN_KINDS))
    for label, q in (("volume", a.volume), ("surface_area", a.surface_area)):
        if q is None or not blends or not q.expected or q.provenance not in ("derived", "inferred", "defaulted"):
            continue
        _, band = q.within(q.expected)
        if band / abs(q.expected) < DERIVED_BAND_MIN_REL:
            warnings.append(f"acceptance.{label}: band ±{band:g} ({band / abs(q.expected):.3%}) on a derived value with {blends} features; "
                            f"hand-derived blend terms are rarely that close: use tolerance_rel >= {DERIVED_BAND_MIN_REL:g} unless a source states the value")
    # 11. a solid point inside a declared bore contradicts the bore; the extent is only certain when t_range states it
    solid_points = [(f"probe {pr.name}", p) for pr in a.probes if pr.state == "solid" for p in pr.points]
    solid_points += [(f"feature {f.id} verify", p) for f in c.features for v in f.verify if v.method == "solid" for p in v.points or []]
    for label, pt in solid_points:
        for cy in holes:
            dist, t = _axis_dist(pt, cy)
            if dist < cy.r and _in_axial_range(cy, t, 0.0):
                msg = f"{label} {list(pt)} lies inside hole {cy.name} (r {cy.r:g}); a solid point there contradicts the hole"
                (problems if cy.t_range is not None else warnings).append(msg)
                break
    prose = " ".join(
        [c.frame.origin, *c.frame.axes.values(), *(d.name + " " + d.description for d in c.frame.datums),
         *(i.name + " " + i.description for i in c.interfaces)]
    )
    if re.search(r"mirror|symmetr", prose, re.IGNORECASE) and not a.symmetry:
        warnings.append("frame/datums/interfaces mention a mirror or symmetry plane but acceptance.symmetry is empty; declare a SymmetrySpec")
    return problems, warnings


def check_bundle(design_dir: Path, name: str | None = None, *, lint: bool = True) -> list[str]:
    """Return human-readable problems with a design bundle (empty list = ok).

    `lint=False` skips the drafting rules (`lint_contract`): a published design is evaluated as written; the rules gate drafting and publishing.

    `name` is the intended design name; defaults to the one its directory holds (`designs/<name>`, `designs/<asm>/parts/<leaf>`)
    unless it is a dot-prefixed staging directory.
    """
    problems: list[str] = []
    design_dir = Path(design_dir)
    if name is None and not design_dir.name.startswith("."):
        try:
            name = design_name(design_dir.resolve().relative_to(DESIGNS.resolve()))
        except ValueError:
            name = design_dir.name
    if name is not None:
        try:
            check_part_name(name)
        except ValueError as e:
            problems.append(str(e))
    for child in design_dir.iterdir():
        if child.name not in ALLOWED_TOP:
            problems.append(f"unexpected bundle entry {child.name!r} (allowed: {sorted(ALLOWED_TOP)})")
    ref = design_dir / "reference"
    if ref.exists():
        for child in ref.iterdir():
            if not _allowed_reference(child.name):
                problems.append(f"unexpected reference entry {child.name!r}")
    brief = design_dir / BRIEF_FILE
    if not brief.exists():
        problems.append("missing brief.md")
    else:
        text = brief.read_text(encoding="utf-8")
        for ph in PLACEHOLDERS:
            if ph in text:
                problems.append(f"brief.md still contains placeholder {ph!r}")
    try:
        c = load_contract(design_dir / CONTRACT_FILE)
        if name is not None and c.name != name:
            problems.append(f"contract.name {c.name!r} != {name!r}")
        for ph in PLACEHOLDERS:
            if ph in c.intent or ph == c.name:
                problems.append(f"contract still contains placeholder {ph!r}")
        for r in c.references:
            if not (design_dir / r.path).exists():
                problems.append(f"reference {r.path!r} is missing from the bundle")
        if lint:
            lint_problems, _ = lint_contract(c)
            problems += lint_problems
    except ContractError as e:
        problems.append(str(e))
    return problems


def publish_bundle(staging_dir: Path, name: str) -> Path:
    """Move a complete staged bundle to its design directory with one same-filesystem rename."""
    target = design_dir(name)
    if target.exists():
        raise ContractError(f"{target} already exists; never merge into or replace an existing design")
    staging_dir = Path(staging_dir)
    problems = check_bundle(staging_dir, name)
    if problems:
        raise ContractError("bundle not publishable:\n  - " + "\n  - ".join(problems))
    target.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staging_dir, target)
    return target


def stage_bundle(name: str) -> Path:
    """Copy the template into designs/.staging-<name>/ with the name filled in."""
    if design_dir(name).exists():
        raise ContractError(f"{design_dir(name)} already exists")
    staging = DESIGNS / f".staging-{name}"
    if staging.exists():
        raise ContractError(f"{staging} already exists; finish or discard it first")
    # copy only the two bundle files: anything else in the template (an editor's stray main.kcl, .DS_Store) would fail check-bundle
    staging.mkdir(parents=True)
    for f in (CONTRACT_FILE, BRIEF_FILE):
        p = staging / f
        p.write_text((TEMPLATE / f).read_text(encoding="utf-8").replace("new-part", name), encoding="utf-8")
    (staging / "sources").mkdir()
    return staging


def template_contract() -> PartContract:
    return load_contract(TEMPLATE / CONTRACT_FILE)


# assembly bundles: designs/<asm>/{assembly.yaml, brief.md, sources/}; each modelled part is an ordinary part bundle designs/<design>/

ASSEMBLY_TEMPLATE_BRIEF = "assembly-brief.md"
ASSEMBLY_ALLOWED_TOP = {ASSEMBLY_FILE, BRIEF_FILE, "sources", "reference", *NESTED}
CALCULIX_PHYSICS = ("thermal_transient", "thermal_steady", "structural_static", "modal", "thermoelastic")
OPENFOAM_PHYSICS = ("cfd_steady", "cfd_transient")
FRAME_SLACK_MM = 1.0
CLOSURE_EQUATIONS = {"revolute": 5, "cylindrical": 4, "slider": 5, "ball": 3, "planar": 3}  # constraints a closure imposes in space
MEASURED_KINEMATIC = ("transmission_ratio", "joint_value", "joint_range", "point_x", "point_y", "point_z")
MEASURED = (*MEASURED_KINEMATIC, "fluid_volume")  # what the evaluator measures for an observable no simulation predicts
MEASURED_BAND_MIN_REL = 1e-5  # rack pitch and positions are measured on tessellated sections, to about 3e-7 of the value


def is_assembly(path: Path) -> bool:
    path = Path(path)
    return (path / ASSEMBLY_FILE).exists() if path.is_dir() else path.name == ASSEMBLY_FILE


def load_assembly(path: Path) -> AssemblyContract:
    path = Path(path)
    if path.is_dir():
        path = path / ASSEMBLY_FILE
    if not path.exists():
        raise ContractError(f"missing {path}")
    try:
        return AssemblyContract.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    except ValidationError as e:
        raise ContractError(f"{path}: {e}") from e
    except yaml.YAMLError as e:
        raise ContractError(f"{path}: YAML error: {e}") from e


def _inside(point: Vec3, lo: Vec3, hi: Vec3, slack: float) -> bool:
    return all(l - slack <= x <= h + slack for x, l, h in zip(point, lo, hi))


def _lint_ladder(s: Any, parts: dict[str, Any], joints: dict[str, Any]) -> list[str]:
    """A refinement ladder runs coarse to fine: each step refines everywhere (a smaller factor, the same regions) or only inside
    regions (the same factor, more region levels). Regions are an OpenFOAM mesh feature; a tip region needs a rotating body."""
    problems = []
    for a, b in pairwise(s.levels()):
        everywhere = b.factor < a.factor and b.regions == a.regions
        inside = b.factor == a.factor and b.regions != a.regions and all(b.regions.get(k, 0) >= n for k, n in a.regions.items())
        if not (everywhere or inside):
            problems.append(f"simulation {s.id}: refinement level {b.label} after {a.label} is neither finer everywhere (a smaller factor, the same "
                            "regions) nor finer only inside regions (the same factor, more region levels); order the ladder coarse to fine")
    if s.regions and s.solver != "openfoam":
        problems.append(f"simulation {s.id}: refinement regions are an openfoam setting, not {s.solver}")
    rotating = [b for b in s.bodies if any(j.child == b and j.rotates for j in joints.values())]
    for r in s.regions:
        if r.shape == "rotor_tip" and not (r.body in s.bodies if r.body else rotating):
            problems.append(f"simulation {s.id}: region {r.name} (rotor_tip) needs a rotating body among the simulation's bodies")
        if r.body is not None and r.body not in parts:
            problems.append(f"simulation {s.id}: region {r.name} names unknown body {r.body!r}")
    return problems


def lint_assembly(a: AssemblyContract, designs_root: Path | None = None) -> tuple[list[str], list[str]]:
    """Drafting rules for an assembly: (problems, warnings). Part contracts that are already drafted are cross-checked:
    a joint frame outside its body's envelope means the assembly and the part disagree about that part's frame."""
    from opencad.sim.reduced import MODELS

    problems: list[str] = []
    warnings: list[str] = []
    bundle = (lambda d: designs_root / d) if designs_root else design_dir
    parts = {p.name: p for p in a.parts}
    joints = {j.name: j for j in a.joints}
    for p in a.parts:
        if p.kind != "modelled":
            continue
        try:
            check_part_name(p.design or "")
        except ValueError as e:
            problems.append(f"part {p.name}: {e}")
            continue
        if not p.design.startswith(f"{a.name}-"):
            warnings.append(f"part {p.name}: design {p.design!r} does not start with '{a.name}-'; assembly parts are easier to find as <assembly>-<part>")
        if not (bundle(p.design) / CONTRACT_FILE).exists() and len(p.intent) < 40:
            problems.append(f"part {p.name}: design {p.design} is not drafted yet and its `intent` is too short to draft from; state every dimension, the part's own frame and its interfaces")
    envelopes: dict[str, tuple[Vec3, Vec3, float]] = {}
    for p in a.parts:
        if p.kind == "modelled" and (bundle(p.design) / CONTRACT_FILE).exists():
            try:
                c = load_contract(bundle(p.design))
            except ContractError as e:
                problems.append(f"part {p.name}: {e}")
                continue
            envelopes[p.name] = (c.envelope.min, c.envelope.max, c.envelope.tolerance)
    for j in a.joints:
        # A moving joint's axis may pass beside a stationary parent (a disc spinning past a fixed pad), so only the child side is binding.
        for side, frame, binding in ((j.parent, j.parent_frame, j.kind == "rigid"), (j.child, j.child_frame, True)):
            env = envelopes.get(side)
            if env and not _inside(frame.origin, env[0], env[1], env[2] + FRAME_SLACK_MM):
                (problems if binding else warnings).append(
                    f"joint {j.name}: {side} frame origin {list(frame.origin)} lies outside {side}'s contract envelope "
                    f"{list(env[0])}..{list(env[1])}; the assembly and the part contract disagree about that part's frame")
        if j.drive is not None and j.drive.kind == "motor" and j.drive.speed is None and not j.drive.history and not j.drive.case_value:
            warnings.append(f"joint {j.name}: motor drive without speed, case_value or history; the animation uses a unit speed")
        if j.drive is not None and j.kind == "rigid":
            problems.append(f"joint {j.name}: a rigid joint cannot be driven")
        if j.closure and (j.kind == "rigid" or j.drive is not None):
            problems.append(f"joint {j.name}: a closure joint is a free pin or guide of a loop; it cannot be rigid or driven")
        if j.closure and j.kind == "slider" and (j.parent_frame.ref is None or j.child_frame.ref is None):
            problems.append(f"joint {j.name}: a slider closure needs `ref` on both frames to lock its rotation")
    for t in a.transmissions:
        for side in (t.driver, t.driven):
            if joints[side].kind == "rigid" and not (side == t.driver and t.carrier):  # a fixed ring or sun of an epicyclic set
                problems.append(f"transmission {t.name}: joint {side} is rigid")
            if joints[side].closure:
                problems.append(f"transmission {t.name}: joint {side} closes a loop; couple tree joints")
        if t.carrier is not None and not joints[t.carrier].rotates:
            problems.append(f"transmission {t.name}: carrier joint {t.carrier} does not rotate")
        if t.mesh is not None and not (joints[t.driver].rotates and joints[t.driven].rotates):
            problems.append(f"transmission {t.name}: a gear mesh check needs two rotating joints")
    from opencad.assembly.joints import unknowns

    equations = len(a.transmissions) + sum(CLOSURE_EQUATIONS[j.kind] for j in a.joints if j.closure and j.kind in CLOSURE_EQUATIONS)
    for m in a.acceptance.motions:
        j = joints[m.drive]
        if j.kind == "rigid":
            problems.append(f"motion {m.name}: joint {m.drive} is rigid")
        if j.closure:
            problems.append(f"motion {m.name}: joint {m.drive} closes a loop; drive a tree joint")
        if j.limits is not None and (min(m.range) < j.limits[0] - 1e-9 or max(m.range) > j.limits[1] + 1e-9):
            problems.append(f"motion {m.name}: range {list(m.range)} exceeds joint {m.drive} limits {list(j.limits)}")
        free = unknowns(a, {m.drive: 0.0})
        if len(free) > equations:
            problems.append(f"motion {m.name}: {len(free)} joints follow the drive ({', '.join(free)}) but the loops and transmissions give only "
                            f"{equations} equations; the mechanism is underdetermined")
    for f in a.fluid_volumes:
        for cap in f.caps:
            if sum(x * x for x in cap.normal) < 1e-12:
                problems.append(f"fluid volume {f.name}: cap {cap.name} normal is zero")
        if f.volume is None:
            warnings.append(f"fluid volume {f.name}: no volume band; any sealed pocket would pass")
    outputs = {s.id: set(s.outputs) for s in a.simulations}
    for s in a.simulations:
        if s.solver.startswith("reduced:") and s.solver.split(":", 1)[1] not in MODELS:
            problems.append(f"simulation {s.id}: unknown reduced model {s.solver!r} (known: {', '.join(MODELS)})")
        if s.solver == "calculix" and s.physics not in CALCULIX_PHYSICS:
            problems.append(f"simulation {s.id}: calculix runs {CALCULIX_PHYSICS}, not {s.physics}")
        if s.solver == "openfoam" and s.physics not in OPENFOAM_PHYSICS:
            problems.append(f"simulation {s.id}: openfoam runs {OPENFOAM_PHYSICS}, not {s.physics}")
        if not s.outputs:
            warnings.append(f"simulation {s.id}: no outputs; nothing it computes is reported")
        problems += _lint_ladder(s, parts, joints)
        if s.solver in ("calculix", "openfoam"):
            if len(s.refinement) < 2:
                warnings.append(f"simulation {s.id}: one refinement level gives no numerical-uncertainty estimate")
            elif len(s.refinement) == 2:
                warnings.append(f"simulation {s.id}: two refinement levels give only a conservative (Fs 3) estimate; three give the grid-convergence index")
            steps = list(pairwise(s.levels()))[-2:]
            if any(a.factor == b.factor for a, b in steps):
                warnings.append(f"simulation {s.id}: a finest step refines only inside regions, so its predictions cannot be resolved (a region sensitivity "
                                "study; keep the regions on every level of a ladder of factors to resolve them)")
    for o in a.observables:
        if o.simulation is not None and o.id not in outputs.get(o.simulation, set()):
            problems.append(f"observable {o.id}: simulation {o.simulation} does not list it in `outputs`")
        if o.simulation is None and o.quantity not in MEASURED:
            problems.append(f"observable {o.id}: no simulation predicts it and the evaluator does not measure {o.quantity!r} (it measures "
                            f"{', '.join(MEASURED)}); name a simulation or use one of those")
        if o.simulation is None and o.quantity in MEASURED_KINEMATIC and o.expected is not None:
            band = o.expected.within(o.expected.expected)[1]
            if band < MEASURED_BAND_MIN_REL * abs(o.expected.expected):
                problems.append(f"observable {o.id}: band {band:g} {o.unit} is finer than the evaluator measures ({MEASURED_BAND_MIN_REL:g} of "
                                f"{o.expected.expected:g}); widen `expected.tolerance`")
    for b in a.boundaries:
        if b.body in parts and parts[b.body].role == "fluid" and b.select == "touching" and b.touching == b.body:
            problems.append(f"boundary {b.name}: a body cannot touch itself")
    return problems, warnings


def check_assembly_bundle(design_dir: Path, name: str | None = None, *, lint: bool = True) -> list[str]:
    problems: list[str] = []
    design_dir = Path(design_dir)
    if name is None and not design_dir.name.startswith("."):
        name = design_dir.name
    if name is not None:
        try:
            check_part_name(name)
        except ValueError as e:
            problems.append(str(e))
    for child in design_dir.iterdir():
        if child.name not in ASSEMBLY_ALLOWED_TOP:
            problems.append(f"unexpected bundle entry {child.name!r} (allowed: {sorted(ASSEMBLY_ALLOWED_TOP)})")
    brief = design_dir / BRIEF_FILE
    if not brief.exists():
        problems.append("missing brief.md")
    else:
        text = brief.read_text(encoding="utf-8")
        problems += [f"brief.md still contains placeholder {ph!r}" for ph in PLACEHOLDERS if ph in text]
    try:
        a = load_assembly(design_dir)
    except ContractError as e:
        return problems + [str(e)]
    if name is not None and a.name != name:
        problems.append(f"assembly.name {a.name!r} != {name!r}")
    problems += [f"assembly still contains placeholder {ph!r}" for ph in PLACEHOLDERS if ph in a.intent or ph == a.name]
    problems += [f"reference {r.path!r} is missing from the bundle" for r in a.references if not (design_dir / r.path).exists()]
    for p in a.parts:
        if p.catalog is not None and p.catalog.path and not (design_dir / p.catalog.path).exists():
            problems.append(f"part {p.name}: catalog path {p.catalog.path!r} is missing from the bundle")
    if lint:
        problems += lint_assembly(a)[0]
    return problems


def stage_assembly(name: str) -> Path:
    check_part_name(name)
    if (DESIGNS / name / ASSEMBLY_FILE).exists():
        raise ContractError(f"{DESIGNS / name} already exists")
    staging = DESIGNS / f".staging-{name}"
    if staging.exists():
        raise ContractError(f"{staging} already exists; finish or discard it first")
    staging.mkdir(parents=True)
    (staging / ASSEMBLY_FILE).write_text((TEMPLATE / ASSEMBLY_FILE).read_text(encoding="utf-8").replace("new-assembly", name), encoding="utf-8")
    (staging / BRIEF_FILE).write_text((TEMPLATE / ASSEMBLY_TEMPLATE_BRIEF).read_text(encoding="utf-8").replace("new-assembly", name), encoding="utf-8")
    (staging / "sources").mkdir()
    return staging


def publish_assembly(staging_dir: Path, name: str) -> Path:
    """Its parts may have published into designs/<name>/parts/ first: the staged entries then move in beside them."""
    check_part_name(name)
    target = DESIGNS / name
    if target.exists() and any(p.name not in NESTED for p in target.iterdir()):
        raise ContractError(f"{target} already exists; never merge into or replace an existing design")
    problems = check_assembly_bundle(Path(staging_dir), name)
    if problems:
        raise ContractError("assembly bundle not publishable:\n  - " + "\n  - ".join(problems))
    if not target.exists():
        os.replace(staging_dir, target)
        return target
    for p in Path(staging_dir).iterdir():
        os.replace(p, target / p.name)
    Path(staging_dir).rmdir()
    return target

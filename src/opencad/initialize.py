"""Headless /initialize-cad pieces: Codex drafts contract.yaml and brief.md into a staging bundle.

`python -m opencad draft designs/.staging-<part> --name <part> --intent "..." [--source F]... [--image F]... [--notes TEXT]`
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import UnionType
from typing import Any, Literal, Union, get_args, get_origin

from pydantic import BaseModel

from opencad import telemetry, worker
from opencad.contract import check_bundle
from opencad.io import sha256_file
from opencad.paths import REPO_ROOT, TEMPLATE
from opencad.paths import results_dir as results_of

EXEMPLAR_CONTRACT = REPO_ROOT / "docs" / "exemplar-contract.yaml"
from opencad.worker import orders
from opencad.worker.profiles import lean_turns

_TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml"}
_INLINE_SOURCE_MAX = 8192

MAX_ROUNDS = 3
SCHEMA_PATH = REPO_ROOT / "src" / "opencad" / "schemas.py"


def copy_sources(staging: Path, sources: list[Path]) -> list[dict[str, Any]]:
    out = []
    (staging / "sources").mkdir(exist_ok=True)
    for s in sources:
        s = Path(s)
        dst = staging / "sources" / s.name
        if s.resolve() != dst.resolve():
            shutil.copy2(s, dst)
        out.append({"path": f"sources/{s.name}", "sha256": sha256_file(dst), "suffix": s.suffix.lower()})
    return out


def _literal_arg(value: Any) -> str:
    return json.dumps(value) if isinstance(value, str) else str(value)


def _type_name(tp: Any) -> str:
    origin = get_origin(tp)
    if origin is None:
        return getattr(tp, "__name__", str(tp))
    args = get_args(tp)
    if origin is list:
        return f"list[{_type_name(args[0])}]" if args else "list"
    if origin is dict:
        return f"dict[{_type_name(args[0])}, {_type_name(args[1])}]" if len(args) == 2 else "dict"
    if origin is tuple:
        return "tuple[" + ", ".join(_type_name(a) for a in args) + "]" if args else "tuple"
    if origin is Literal:
        return "Literal[" + ", ".join(_literal_arg(a) for a in args) + "]"
    if origin in (Union, UnionType) or origin is type(None):
        return " | ".join(_type_name(a) for a in args if a is not type(None))
    return getattr(origin, "__name__", str(origin))


def schema_digest() -> str:
    """Field, type, required and description for PartContract and the models it nests. Replaces reading schemas.py."""
    from opencad.schemas import PartContract

    lines: list[str] = []
    seen: set[type] = set()

    def emit(model: type[BaseModel]) -> None:
        if model in seen:
            return
        seen.add(model)
        lines.append(f"{model.__name__}:")
        nested: list[type[BaseModel]] = []
        for name, field in model.model_fields.items():
            ann = field.annotation
            lines.append(
                f"  {name}: {_type_name(ann)} ({'required' if field.is_required() else 'optional'})"
                + (f" — {field.description}" if field.description else "")
            )
            for arg in (ann, *get_args(ann or ())):
                origin = get_origin(arg) or arg
                if isinstance(origin, type) and issubclass(origin, BaseModel):
                    nested.append(origin)
        for sub in nested:
            emit(sub)

    emit(PartContract)
    return "\n".join(lines)


def _inlined_sources(staging: Path, sources: list[dict[str, Any]]) -> tuple[str, str]:
    """Text sources under 8 KB go in the brief; everything else stays a path."""
    listed, bodies = [], []
    for s in sources:
        p = staging / s["path"]
        if p.suffix.lower() in _TEXT_SUFFIXES and p.is_file() and p.stat().st_size <= _INLINE_SOURCE_MAX:
            bodies.append(f"### {p.name}\n\n{p.read_text(encoding='utf-8', errors='replace').rstrip()}")
        else:
            listed.append(f"- {p} (sha256 {s['sha256'][:12]})")
    return ("\n".join(listed) or "- (all text sources are inlined below)"), "\n\n".join(bodies)


def station_note(ref: Path) -> str:
    """How to state a free-form skin from a reference ingest's stations, when it has them."""
    p = ref / "reference.json"
    try:
        st = (json.loads(p.read_text(encoding="utf-8")).get("measurements") or {}).get("stations") if p.exists() else None
    except json.JSONDecodeError:
        return ""
    if not st:
        return ""
    u, _ = st["uv_axes"]
    return (
        f"\nStations: `{p}` `.measurements.stations` cuts the mesh at {len(st['positions'])} planes {st['axis']} = {st['positions']} "
        "(drawn in `reference-sections-stations.png`, fits in grey). Every section there and in `.measurements.sections` lists its regions "
        f"with `outline` (32 points in the plane's world axes `uv_axes`, mm, counter-clockwise from the largest-{u} point), `outline_16`, "
        "`hole_outlines` and `fit`: circle, ellipse, u_shape (two parallel sides closed by a semi-elliptic end, round end toward `end`) and "
        f"rounded_rect, each with rms/p95/max residual in mm, and `best`, the simplest within {st['fit_tolerance_mm']} mm p95 (else null). "
        "The section's convex `hull` carries the same fields: the outer skin of a channel or canopy with its opening chorded. "
        "`.measurements.profile` gives each station's bounds, centre and half size along the axis. State a free-form skin station by station: "
        "where a fit is `best`, its dimensions become parameters (`measured (reference model)`, `source` `reference/reference.json`, "
        "tolerance at least that fit's p95); where none is, name that station's `outline_16` in the feature's description so the model "
        "embeds it (at most 16 points per station and 12 stations). Add an `acceptance.sections` entry at each station you use (area, loops, "
        "holes from that station) and describe the surface as a smooth loft (`ruled=False`) through arc or spline sections, never ruled "
        "polygons.\n"
    )


def draft_brief(
    staging: Path,
    name: str,
    intent: str,
    *,
    sources: list[dict[str, Any]],
    images: list[Path],
    notes: str = "",
    checks: list[tuple[str, str]] | None = None,
) -> str:
    ref = staging / "reference"
    ref_files = sorted(p.name for p in ref.iterdir()) if ref.exists() else []
    src_lines = "\n".join(f"- {staging / s['path']} (sha256 {s['sha256'][:12]})" for s in sources) or "- (none)"
    inlined = ""
    schema = f"Schema: read `{SCHEMA_PATH}` (PartContract). The seeded `{TEMPLATE / 'contract.yaml'}` shows the expected shape."
    scored = ""
    discipline = ""
    if lean_turns():
        listed, inlined = _inlined_sources(staging, sources)
        src_lines = listed
        schema = (
            "Schema digest (do not open `src/opencad`):\n\n"
            + schema_digest()
            + f"\n\nFilled exemplar `{EXEMPLAR_CONTRACT}` (a fictitious part; copy the shape, not the part):\n\n```yaml\n{EXEMPLAR_CONTRACT.read_text(encoding='utf-8').rstrip()}\n```"
        )
        if checks:
            scored = (
                "\nThe finished part is scored on these checks. State a matching acceptance item for each. "
                "Take every value from the sources; this list carries none:\n"
                + "\n".join(f"- {kind} `{obs}`" for kind, obs in checks)
                + "\n"
            )
        discipline = (
            "\nDo not open `src/opencad`, `truth/` or `results/`. Look at the attached images, write `contract.yaml`, "
            "write `brief.md`, run check-bundle, fix every problem and `warning:` line it prints once, then write the protocol files.\n"
        )
    img_lines = "\n".join(f"- {Path(i).name} (attached as an image)" for i in images) or "- (none)"
    ref_lines = "\n".join(f"- {ref / f}" for f in ref_files) or "- (none)"
    return f"""Draft the PartContract and design brief for a new CAD part. Write BOTH files in place:
- `{staging / "contract.yaml"}` (currently the seeded template; replace its contents)
- `{staging / "brief.md"}` (currently the template with placeholders; replace every placeholder)

Part name: `{name}`
Intent (verbatim from the user): {intent}

Text/table sources to read (absolute paths):
{src_lines}
{inlined}
Images attached to this task (read dimension lines, count features, record pixel evidence):
{img_lines}
Reference ingest outputs (deterministic measurements of a mesh or a coordinate table; treat as `measured (reference model)` with the suggested tolerances):
{ref_lines}
{station_note(ref)}{("Additional notes from the orchestrator: " + notes) if notes else ""}

{schema}
{scored}Rules:
- Units mm and deg. `frame` must state the origin, the meaning of +x/+y/+z and the datums in words a later reader can reproduce; choose the frame the sources use (or the reference ingest frame when one exists).
- Every `parameters[]` entry needs a nonzero digital `tolerance` and a `provenance`: `stated` (quoted from a document; give `source`), `measured` (read from an image/drawing; give `source` and a wide tolerance that reflects pixel/line-width uncertainty), `measured (reference model)` (from reference.json/profile.json; `source` = that file), `derived` (give `formula` in terms of other parameters), `inferred` or `defaulted` (give `rationale`). Never invent a dimension: if the sources do not fix it, add an `open_questions` entry and, only if the part cannot be built without it, an `inferred` value with a clear rationale and wide tolerance.
- Parameter names are identifiers the modelling backend will declare as top-level constants: start with a letter, no spaces. For Zoo/KCL they must also be lowerCamelCase (no underscores; never three capitals in a row or two at the end: `usbCx`, `sdYMin`, `hdmi0X` pass; `usbCX`, `holeID`, `mountXY` fail).
- `features[]`: every geometric feature the sources describe, with `verify` probes: `bbox`, `solid`/`void` points (inside material / inside a hole or cavity, in the contract frame), `section` (references an `acceptance.sections` id), `count` (loops in a section), `face` (references an `acceptance.faces` name), `cylinder` (references an `acceptance.cylinders` name), `plane`, `dimension`. Cosmetic-only features get `optional: true`.
- `acceptance`: analytic `volume`, `surface_area` (if computable), `center_of_mass` with formulas in `note`; `sections` at planes that expose the critical internal features (cavities, holes, channels) with expected area/loops/holes; `faces` for every axis-aligned face downstream users must name (inlets, outlets, mating faces); `cylinders` for EVERY hole, bore, pin, boss and shaft the sources locate (name, `point` on the axis, `direction`, `kind` hole|pin, `diameter` or `radius`, optional `length`; the inspector reports each axis offset in mm, so a pattern of 16 pins is 16 entries, not one); `planes` for inclined faces (ramps, drafts, chamfer-like walls) by a point and outward normal; `dimensions` for stated distances (bbox extent along an axis, or `between` two named faces); `blockout` band = volume of the envelope-only primary solids (min/max); `deviation` only when a reference mesh exists (use the suggested band from reference.json).
- Multi-body and interior requirements (enclosures, ducts, gear sets) use the acceptance sections `solids` (name each body by a `contains_point`; set `solid_count`), `hardware` (evaluator-side keep-out boxes/cylinders the part must respect, with optional `exclude_cylinders`), `clearances` (`a`/`b` are solid names, hardware names or `all`; `min_gap`, optional `max_gap` for a lid resting on a rim), `passages` (air connectivity `point_a` -> `point_b` with `seal_radius` or `plugs`), `thickness` (`min` wall by inward ray casting, optional `region`), `probes` (`void`/`solid` points), `cylinder_counts` (`radius` or `diameter`, `expected` or `expected_min`, optional `direction`), `gears`/`meshes` (tooth counts and a meshing sweep). Copy the intent's hardware boxes and requirement values into these sections verbatim; every requirement the intent states must map to at least one acceptance item.
- `interfaces[]`: mating or datum interfaces that must survive later edits, each with `checks` listing the acceptance items (face, cylinder, plane, dimension, section, symmetry names) that pin it; an interface without checks is unenforceable.
- Declare `acceptance.symmetry` when the sources state a mirror plane (`name`, `plane` x|y|z, `at`, `max_deviation`, `p95_deviation`); pin it from the matching interface's `checks`. Non-ruled spline lofts can fold on one side of a hull.
- `acceptance.blockout`: the blockout checkpoint is an envelope-only solid that must fill the SAME bounding box as the finished part (every axis, to the envelope tolerance), so its band must cover the primary solids that reach the envelope extremes (base plus the tallest boss, pin or lug), not the bare base alone. Give a band at least a few percent wide.
- Probe and passage rules (`check-bundle` rejects violations): a `seal_radius` can only close ports narrower than itself, so a uniform through bore is sealed with `plugs` (boxes over both mouths), never with a closing radius; every `void` probe point and passage end sits at least 1 mm away from every declared surface (never in a skin, never 0.5 mm from a face); a blind hole's floor face has its outward normal pointing toward the hole's mouth (the open side); an `edit_test.volume_delta` on a parameter that drives a `loft` or `sweep` feature needs `tolerance_rel >= 0.3` or `direction` only, and estimates on `other`/`shell` features must be derived from the geometry with the formula in the brief.
- `edit_test.sweep` (optional, on one or two independent parameters the design must survive varying): `{{min, max, steps}}` or `{{values: [...]}}` absolute values the harness sets with no agent; `edit_test.infeasible_deltas` (optional): one or two deltas that make the part impossible (a counterbore deeper than the plate, a hole outside its boss); the KCL must refuse them with an `assert`, never build distorted geometry. State the feasible interval of every swept parameter in the brief and keep the sweep inside it; a sweep value may never coincide with an infeasible value.
- `edit_test` on the two or three parameters that best prove editability, with the expected `volume_delta` (formula in the brief), `direction`, and `bbox_delta`. Prefer independent parameters (`stated`, `measured`, `inferred`); an edit test on a `derived` parameter means "override the formula for this one parameter", so its expected deltas must be computed with the other parameters held fixed. Table-driven parts (a coordinate table or `profile.json`) prefer an extrusion-length / span / thickness edit test, or an explicit scale factor stated in the plan; do not edit a table-derived chord.
- Repeated coplanar faces (tabs, legs, identical inlets on one plane) need `acceptance.faces[].center` (in-plane centroid) so later scoring can tell them apart. `mode: sum` only when the contract wants the combined area; never leave that implicit.
- Probe points (`void` / `solid`) must sit farther from any inferred wall than that wall's digital tolerance. If a probe cannot be placed with that clearance, record an open question instead of the probe.
- `references[]`: one entry per file under `sources/` and `reference/` with kind, role (`authoritative` or `illustrative`), sha256, units, revision.
- `open_questions`: everything unresolved. Prefer a question to a guess.

Brief (`brief.md`): keep the template's eight section headings. Fill sections 1-7 with real content: source table (file, kind, role, sha256, notes), requirement record, frame/scale/measurement method (for images: which pixel features were read and how scale was established), the measurement and inference record (one row per parameter and per acceptance value with formula/evidence), defaults retained, unrepresentable or low-confidence features. Leave section 8 as the empty log table. No `REPLACE ME`, `<intent>`, or `new-part` may remain.

Verification before you finish: `cd {REPO_ROOT} && .venv/bin/python -m opencad check-bundle {staging} --name {name}` must print `ok:`; fix every reported problem. Do not write any KCL. Do not create any other files in {staging}.
Under `## Result` summarise the frame, the parameter count by provenance, and the acceptance values; under `## Open questions` repeat the contract's open questions.
{discipline}"""


def parity_round(
    staging: Path, name: str, findings: list[dict[str, Any]], *, thread: str | None, timeout: float | None
) -> list[str]:
    """One bounded draft turn on the draft thread after the evaluator's parity audit found checks the part will be scored on that the
    contract lacks or states more loosely. The lines name the check kind and id only, never an evaluator value; returns check-bundle problems."""
    lines = "\n".join(
        f"- {f['status']}: {f['kind']} `{f['observable']}`"
        + (f" (closest contract item `{f['counterpart']}`)" if f.get("counterpart") else "")
        for f in findings
    )
    msg = (
        "The bundle passes check-bundle, but an audit against the checks the finished part will be scored on finds acceptance items the contract "
        "does not state (missing) or states more loosely than the sources support (looser):\n"
        + lines
        + "\nFor each line re-read the sources and "
        "add or tighten the matching acceptance item with values derived from the sources; never loosen anything and never guess a value the "
        "sources do not give (record an open question instead). Re-run check-bundle until it prints ok."
    )
    worker.dispatch(
        msg,
        role="draft",
        key="draft-parity",
        results_dir=results_of(name),
        part=name,
        cd=staging,
        run_dir=staging.parent / f".codex-draft-{name}" / "parity",
        resume=thread,
        timeout=timeout,
        deliverables=[staging / "contract.yaml", staging / "brief.md"],
        budget=worker.scaled_budget("draft", 0),
    )
    return check_bundle(staging, name)


def draft(
    staging: Path,
    name: str,
    intent: str,
    *,
    sources: list[Path],
    images: list[Path],
    notes: str = "",
    timeout: float | None = None,
    cont: bool = False,
    checks: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Up to MAX_ROUNDS worker turns until `check-bundle` passes. Re-entrant: with `cont=True` finished rounds are replayed from their orders."""
    staging = Path(staging)
    copied = copy_sources(staging, sources)
    run_root = staging.parent / f".codex-draft-{name}"
    run_root.mkdir(parents=True, exist_ok=True)
    results_dir = results_of(name)
    if not cont:
        orders.supersede(results_dir, "draft-")
    thread: str | None = None
    rounds: list[dict[str, Any]] = []
    problems: list[str] = ["not yet drafted"]
    deliverables = [staging / "contract.yaml", staging / "brief.md"]
    for i in range(1, MAX_ROUNDS + 1):
        if thread is None:
            msg = draft_brief(staging, name, intent, sources=copied, images=images, notes=notes, checks=checks)
        else:
            msg = (
                "The bundle is not yet publishable. `python -m opencad check-bundle` reports:\n- "
                + "\n- ".join(problems)
                + "\nFix contract.yaml and/or brief.md in place and re-run the check until it prints ok."
            )
        r = worker.dispatch(
            msg,
            role="draft",
            key=f"draft-{i}",
            results_dir=results_dir,
            part=name,
            cd=staging,
            run_dir=run_root / f"round-{i}",
            images=images if thread is None else None,
            resume=thread,
            timeout=timeout,
            deliverables=deliverables,
            budget=worker.scaled_budget("draft", len(sources)),
        )
        thread = r.thread_id or thread
        with telemetry.timed("draft-check", name, results_dir, key=f"draft-{i}") as t:
            problems = check_bundle(staging, name)
            t["ok"] = not problems
        summary = r.summary()
        rounds.append({"round": i, "worker": summary, "codex": summary, "problems": problems, "sections": r.sections})
        if not problems:
            break
    shutil.rmtree(run_root, ignore_errors=True) if not problems else None
    return {"ok": not problems, "rounds": rounds, "problems": problems, "thread_id": thread, "staging": str(staging)}

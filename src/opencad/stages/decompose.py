"""decompose: the model stage for parts one worker turn cannot finish (large contracts, kernel-hostile booleans).

Three kinds of worker turn, all through work orders (file suffix per backend: `.kcl` for Zoo, `.py` for CadQuery,
build123d and FreeCAD; the module protocol is `export fn <group>(@body)` in KCL and `def apply(body)` in Python):

1. `partition` (one turn): writes `results/<part>/decompose/partition.yaml` (feature groups with the parameters and
   acceptance items each owns), `parts/<part>/params.*` (every contract parameter) and
   `parts/<part>/datum.*` (the envelope body from the blockout, named `datum`).
2. `module` (one turn per group, issued together so the orchestrator runs them in parallel): each writes
   `parts/<part>/<group>.*` with the function that applies its features, verified standalone against a
   sub-contract (only the items the group owns) with the local critic.
3. `integrate` (one turn): writes the entry (`main.*`) composing datum + modules, verified against the full contract.

The result is written as the `model` stage so verify/export/inspect/edit/gates run unchanged; corrections resume the
integrate worker. A kernel boolean that fails inside a 30-line module is a short fix, not a 3-hour loop.
"""

from __future__ import annotations

import hashlib
import json
import keyword
import os
import re
import shutil
import time
from pathlib import Path
from typing import Any

import yaml

from opencad import telemetry, worker
from opencad.backends.base import EngineError, is_tooling
from opencad.codex import contract_digest
from opencad.contract import load_contract
from opencad.io import dump_json, sha256_file
from opencad.orchestrator import Ctx, PipelineError
from opencad.paths import REPO_ROOT

PARTITION_FILE = "partition.yaml"
GROUP_RE = re.compile(r"^[a-z][A-Za-z0-9]{1,30}$")
ACCEPTANCE_LISTS = ("sections", "faces", "cylinders", "planes", "dimensions", "solids", "clearances", "passages", "thickness", "probes", "cylinder_counts", "gears", "meshes")
ACCEPTANCE_KEY = {"sections": "id"}
SIZE_TRIGGER_PARAMS = 50
SIZE_TRIGGER_FEATURES = 25  # contract features (families), not patterned acceptance items: a 16-boss pattern is one feature
RESERVED_IDS = frozenset({"params", "main", "sys", "math", "cadquery", "cq", "build123d", "bd"})  # a module file with this name would shadow it


def acceptance_names(contract) -> dict[str, list[str]]:
    a = contract.acceptance
    out: dict[str, list[str]] = {}
    for k in ACCEPTANCE_LISTS:
        items = getattr(a, k, None) or []
        out[k] = [getattr(x, ACCEPTANCE_KEY.get(k, "name")) for x in items]
    return out


def acceptance_count(contract) -> int:
    return sum(len(v) for v in acceptance_names(contract).values())


def should_decompose(ctx: Ctx, explicit: bool | None) -> bool:
    if explicit is not None:
        return explicit
    c = ctx.contract
    return len(c.parameters) >= SIZE_TRIGGER_PARAMS or len(c.features) >= SIZE_TRIGGER_FEATURES


def work_dir(ctx: Ctx) -> Path:
    return ctx.results_dir / "decompose"


def is_kcl(ctx: Ctx) -> bool:
    return ctx.backend.language.id == "kcl"


def src_path(ctx: Ctx, stem: str) -> Path:
    """`parts/<backend>/<part>/<stem>.<kcl|py>`: params, datum and one file per module group."""
    return ctx.part_dir / f"{stem}{ctx.backend.language.suffixes[0]}"


def scratch_main(ctx: Ctx, applied: list[str], scratch: Path) -> str:
    """A scratch entry in `scratch` that composes `datum` + the listed modules in order: relative KCL imports for Zoo,
    a `sys.path` entry + the `apply` chain for the Python backends (the runners exec the entry with `python -I`)."""
    if is_kcl(ctx):
        rel = Path(os.path.relpath(ctx.part_dir, scratch)).as_posix()
        lines = ["@settings(defaultLengthUnit = mm, kclVersion = 2.0)", f'import datum from "{rel}/datum.kcl"']
        lines += [f'import {g} from "{rel}/{g}.kcl"' for g in applied]
        return "\n".join(lines + ["", "body = datum" + "".join(f"\n  |> {g}()" for g in applied), ""])
    lines = ["import sys", "", f"sys.path.insert(0, {str(ctx.part_dir)!r})", "from datum import datum  # noqa: E402"]
    lines += [f"from {g} import apply as apply_{g}  # noqa: E402" for g in applied]
    body = "datum"
    for g in applied:
        body = f"apply_{g}({body})"
    return "\n".join(lines + ["", f"result = {body}", ""])


def _critic(ctx: Ctx, entry: Path, contract: Path, extra: str = "") -> str:
    return f"cd {REPO_ROOT} && .venv/bin/python -m opencad quick {entry} --contract {contract} --backend {ctx.backend_id}{extra}"


def _bisect(ctx: Ctx, entry: Path) -> str:
    cmd = ctx.backend.language.critics().get("bisect", "").format(entry=entry)
    what = "names the first pipeline step that fails" if is_kcl(ctx) else "runs the file outside the critic's cache and prints the traceback of the failing operation"
    return f"`cd {REPO_ROOT} && {cmd}` {what}"


def recipe(ctx: Ctx, gid: str = "<id>") -> dict[str, str]:
    """How params, datum, a module and the integrated entry are written in the backend's language; the briefs quote these."""
    lang = ctx.backend.language
    if is_kcl(ctx):
        return {
            "params": "`@settings(defaultLengthUnit = mm, kclVersion = 2.0)` then EVERY contract parameter as `export <name> = <value><unit>` with the exact contract names and values, one per line (this is where the pipeline rewrites values)",
            "datum": "import the parameters (`import <names> from \"params.kcl\"`), rebuild the primary solid(s) and `export datum = <solid>` (for `solid_count > 1` export one named solid per body)",
            "module": f"`@settings(defaultLengthUnit = mm, kclVersion = 2.0)`, `import` the parameters it needs from `\"params.kcl\"`, and `export fn {gid}(@body) {{ ... return <solid> }}` that takes the stock solid and returns it with this group's features added or cut. No other top-level solids; helper functions are fine",
            "signature": f"export fn {gid}(@body)",
            "integrate": "`@settings(...)`, imports, then `datum` piped through the module functions in that order, ending with the finished solid(s)",
            "params_rule": "Every contract parameter must still resolve to the literal in `params.kcl` (do not redeclare them)",
            "format": "`zoo kcl format --write` on every file and `zoo kcl lint`",
        }
    imp = "`from params import <the names it needs>` (explicit names: `ruff check` rejects `import *`)"
    if lang.id == "freecad":
        datum = (f"{imp}, open the document, build one `PartDesign::Body` per contract solid padded to the envelope from the passed blockout, `doc.recompute()`, "
                 "then assign `datum` to that Body (for `solid_count > 1` a tuple of Bodies in `acceptance.solids` order)")
        module = ("`from params import <the names this group consumes>` (explicit names) and `def apply(body):` that adds this group's PartDesign features to `body` "
                  "(sketches on named planes or on faces found by normal and centre; one Pocket/Hole per family), calls `body.Document.recompute()` and returns the same "
                  "Body (or the tuple it was given); every feature must be `isValid()`. Build the cutting tools first, union them into ONE tool and cut once "
                  "(a SubtractiveBox/Pocket per family, not per hole); overrun every tool 0.01-0.05 mm past the face it cuts; never leave a tool face coincident with "
                  "a stock face. No top-level geometry and no `result`; helper functions are fine")
    else:
        kind = "a `cq.Workplane` (or Shape)" if lang.id == "cadquery" else "a `Part`/`Solid`"
        datum = (f"{imp}, rebuild the primary solid(s) from the passed blockout and assign `datum` to the envelope body, {kind} "
                 "(for `solid_count > 1` a list with one body per contract solid)")
        module = ("`from params import <the names this group consumes>` (explicit names) and `def apply(body):` that takes the stock body and returns it with this group's "
                  "features added or cut. Build the tools first, union them into ONE tool and cut once; overrun every tool 0.01-0.05 mm past the face it cuts; never leave "
                  "a tool face coincident with a stock face. No top-level geometry and no `result`; helper functions are fine")
    return {
        "params": "EVERY contract parameter as a top-level float in millimetres (`<name> = <value>`) with the exact contract names and values, one per line, and nothing else (this is where the pipeline rewrites values)",
        "datum": datum,
        "module": module,
        "signature": "def apply(body)",
        "integrate": "`from datum import datum`, one `from <id> import apply as apply_<id>` per module, then `result = apply_<last>(... apply_<first>(datum))` in that order, ending with the finished solid(s)",
        "params_rule": f"Parameters stay in `params{lang.suffixes[0]}`: import the names you need, never redeclare them",
        "format": f"`ruff format` on every file under `{ctx.part_dir}` and `ruff check` (must be clean)",
    }


# --- briefs ------------------------------------------------------------------------------------

def partition_brief(ctx: Ctx, plan_md: str) -> str:
    wd = work_dir(ctx)
    lang = ctx.backend.language
    blockout = ctx.results_dir / "blockout" / lang.entry
    r = recipe(ctx)
    names = acceptance_names(ctx.contract)
    listing = "\n".join(f"  {k}: {', '.join(v)}" for k, v in names.items() if v)
    return f"""Partition the part below into feature-group modules that separate workers will build in parallel, and lay the shared foundation.

Skills: read {' and '.join(str(p) for p in lang.skills())} first.

{contract_digest(ctx.contract, ctx.design_dir)}

{('Construction plan so far:' + chr(10) + plan_md) if plan_md.strip() else ''}

Deliverables (all three must exist and the {lang.id} sources must execute):
1. `{wd / PARTITION_FILE}`: YAML with
   ```yaml
   groups:
     - id: <lowerCamel identifier, also the module file name>
       title: <one line>
       features: [<contract feature ids this group builds>]
       parameters: [<contract parameter names this group consumes>]
       acceptance: {{cylinders: [...], faces: [...], sections: [...], planes: [...], dimensions: [...], probes: [...], solids: [...], passages: [...], thickness: [...], cylinder_counts: [...], gears: [...], meshes: [...]}}
       depends_on: [<group ids whose geometry must exist first>]
       region: {{min: [x, y, z], max: [x, y, z]}}   # the AABB (mm, contract frame) every feature and acceptance item of this group lives in
       shared_planes: [{{axis: x|y|z, at: <mm>, with: <group id>}}]   # boundary planes where this group's region touches another's
       notes: <what the module adds or cuts, which faces it must not touch>
   ```
   Rules: every contract feature id and every acceptance item name appears in exactly one group (the datum body's own
   faces/dimensions go to a group called `datum`, which has no module); 2 to 6 groups; a group is one boolean family
   (a fastener stack, a pocket family, a duct, a set of bosses), never "everything else". `region` is the spatial
   contract between modules: a module may only add or cut material inside its region (tools may overrun into air or
   outside the envelope, never into another group's region); items are assigned to the group whose region contains them.
   If the contract's section areas are much smaller than the blockout's at most stations (the envelope prism carries
   exterior material that must be sculpted away: chamfered corners, tapers, external reliefs), one group must be
   `exterior` (the sculpting of the envelope), applied first. Keep the acceptance list names exactly as printed here:
{listing}
2. `{src_path(ctx, 'params')}`: {r['params']}.
3. `{src_path(ctx, 'datum')}`: the envelope body. Start from the passed blockout `{blockout}` (it already fills the contract
   envelope): {r['datum']}. It must execute: `{wd / 'datum-check' / lang.entry}` is already written (it takes `datum` as the result);
   `{_critic(ctx, wd / 'datum-check' / lang.entry, ctx.contract_path)}` must show the contract envelope bbox
   (the feature checks fail until the modules exist).

Write nothing else under `{ctx.part_dir}`. Scratch files go under `{wd}`.
{lang.rules()}
Under `## Result` list the groups and their sizes; under `## Open questions` anything the contract leaves ambiguous per group.
"""


def void_keepouts(contract, partition: dict[str, Any], gid: str) -> list[str]:
    """Air volumes other groups own (passage routes, void probes): lines a module's cutting tools must stay clear of."""
    a = contract.acceptance
    own: dict[str, str] = {}
    for g in partition.get("groups", []):
        for k, lst in (g.get("acceptance") or {}).items():
            for n in lst or []:
                own[f"{k}/{n}"] = str(g.get("id"))
    out: list[str] = []
    for ps in a.passages:
        if own.get(f"passages/{ps.name}", gid) != gid and ps.expect_connected:
            out.append(f"passage `{ps.name}` (owner `{own[f'passages/{ps.name}']}`): air route {list(ps.point_a)} -> {list(ps.point_b)}"
                       + (f", sealed by a {ps.seal_radius:g} mm closing (a channel narrower than ~{2 * ps.seal_radius:g} mm counts as closed)" if ps.seal_radius else ""))
    for pr in a.probes:
        if pr.state == "void" and own.get(f"probes/{pr.name}", gid) != gid:
            out.append(f"void probe `{pr.name}` (owner `{own[f'probes/{pr.name}']}`): {[list(p) for p in pr.points]}")
    return out


def _region_text(group: dict[str, Any], partition: dict[str, Any], contract=None) -> str:
    reg = group.get("region")
    if not reg:
        return ""
    others = [f"`{g['id']}` {g.get('region', {}).get('min')} .. {g.get('region', {}).get('max')}" for g in partition.get("groups", []) if g.get("id") not in (group["id"], "datum") and g.get("region")]
    planes = "; ".join(f"{p.get('axis')} = {p.get('at')} (with {p.get('with')})" for p in (group.get("shared_planes") or [])) or "none declared"
    text = (f"\nSpatial contract: this module may add or cut material only inside its region {reg.get('min')} .. {reg.get('max')} mm. Tools may overrun into air or "
            f"outside the part envelope; they must stop at least 0.1 mm short of any face another module owns. Boundary planes: {planes}. Other modules' regions: "
            f"{', '.join(others) or 'none'}. A feature that needs material outside the region is a partition problem: report it under `## Open questions`, do not cut it.\n")
    keep = void_keepouts(contract, partition, group["id"]) if contract is not None else []
    if keep:
        wall = min((t.min for t in contract.acceptance.thickness), default=0.75)
        text += (f"Keep-outs (air other modules own; the composed part fails when your material enters it or your cuts open it): every tool of this module stays "
                 f">= {wall + 0.1:.2f} mm (wall_min + 0.1) away from these volumes and never breaks into them:\n" + "\n".join(f"- {k}" for k in keep) + "\n")
    return text


def module_brief(ctx: Ctx, group: dict[str, Any], sub_contract: Path, scratch: Path, partition: dict[str, Any]) -> str:
    gid = group["id"]
    lang = ctx.backend.language
    r = recipe(ctx, gid)
    entry = scratch / lang.entry
    deps = group.get("depends_on") or []
    dep_note = (f"This module is applied after {deps}: their modules are `{', '.join(str(src_path(ctx, d)) for d in deps)}`; the scratch main applies them "
                f"to the datum before this module so your features cut the right stock.") if deps else "This module is applied directly to the datum body."
    sub_raw = yaml.safe_load(Path(sub_contract).read_text(encoding="utf-8")) if Path(sub_contract).exists() else {}
    has_passages = bool(((sub_raw.get("acceptance") or {}).get("passages")))
    passage_rule = ("- Passages: a passage is judged with its ports sealed by the contract's `plugs` boxes (or a closing radius). Every port this group cuts must open "
                    "INSIDE a plug box and the air path must reach both probe points; a port outside its plug box leaks to the exterior and fails the passage. Check with "
                    "the critic's `passages` lines (`reaches_exterior`, `a`/`b` state).\n") if has_passages else ""
    return f"""Build ONE feature-group module of the part: group `{gid}` ({group.get('title', '')}).

Skills: read {' and '.join(str(p) for p in lang.skills())} first.

Shared foundation (already written, do not edit): `{src_path(ctx, 'params')}` defines every contract parameter; `{src_path(ctx, 'datum')}` defines
the envelope body `datum`. {dep_note}

Group definition (from `{work_dir(ctx) / PARTITION_FILE}`):
{yaml.safe_dump(group, sort_keys=False)}
Sub-contract with only the acceptance items this group owns: `{sub_contract}` (the local critic below measures exactly these).
{_region_text(group, partition, ctx.contract)}
Deliverable: `{src_path(ctx, gid)}`:
- {r['module']}.
- Verify standalone: `{entry}` is already written (it composes `datum`, the dependency modules and this module in that order; edit it only if
  that order is wrong) and run the local critic `{_critic(ctx, entry, sub_contract)}`.
  Every item in the sub-contract must pass; bbox/volume/COM are not judged at this level.
- Kernel booleans that fail ("cannot handle this 3D subtraction", `BRep_API: command not done`, coincident faces): build the tools first, union them into ONE tool, and subtract
  once; overrun the tool 0.01-0.05 mm past the face into air; never let a tool face coincide with a stock face; change the order if needed.
  {_bisect(ctx, entry)}.
  Keep an executing checkpoint of the module.
{passage_rule}
{lang.rules()}
Under `## Verification` list each sub-contract item measured vs expected. Under `## Open questions` anything the group definition leaves ambiguous.
"""


def integrate_brief(ctx: Ctx, partition: dict[str, Any], probe: dict[str, Any] | None = None) -> str:
    groups = [g for g in partition["groups"] if g["id"] != "datum"]
    order = _apply_order(groups)
    lang = ctx.backend.language
    r = recipe(ctx)
    probe_text = probe_findings_text(probe) if probe else ""
    return f"""Integrate the feature-group modules into the deliverable `{ctx.entry}` and make the whole part pass its contract.

Skills: read {' and '.join(str(p) for p in lang.skills())} first.

{contract_digest(ctx.contract, ctx.design_dir)}

Modules (already written and verified standalone against their sub-contracts, in `{ctx.part_dir}`): `{src_path(ctx, 'params').name}` (all parameters),
`{src_path(ctx, 'datum').name}` (defines `datum`), and one `{r['signature']}` per group: {', '.join(f'`{src_path(ctx, g).name}`' for g in order)}.
Application order that respects `depends_on`: {' -> '.join(order)}.
{probe_text}
{_bisect(ctx, ctx.entry)} when the composition does not execute.

Deliverable: `{ctx.entry}` = {r['integrate']} (solid count {ctx.contract.acceptance.solid_count}). {r['params_rule']}.
If a module's feature breaks once composed (a boolean that worked on the bare datum fails on the cut stock), fix that module in
place with the smallest change and re-run its sub-contract critic; report every module you touched.
Each time the composed `{ctx.entry.name}` executes, copy every `{', '.join(lang.suffixes)}` file of `{ctx.part_dir}` into `{integrate_checkpoint(ctx)}/`
(replace its contents). When the budget runs out or an engine error will not clear, leave those files in place: the pipeline restores
that checkpoint if the sources no longer execute and measures it, and correction turns finish the rest.

Verify the composed part with the local critic against the FULL contract: `{_critic(ctx, ctx.entry, ctx.contract_path, ' --stl')}`,
then {r['format']}. The STL must be watertight (per body when several).

{lang.rules()}
Under `## Verification` list bbox/volume/COM measured vs expected and the per-feature evidence; under `## Open questions` anything unverified.
"""


def integrate_checkpoint(ctx: Ctx) -> Path:
    return work_dir(ctx) / "integrate" / "checkpoint"


def _prereqs(groups: list[dict[str, Any]], gid: str) -> list[str]:
    """The modules `gid` transitively depends on, in application order."""
    by_id = {g["id"]: g for g in groups}
    need: set[str] = set()
    stack = [d for d in (by_id.get(gid, {}).get("depends_on") or []) if d in by_id]
    while stack:
        d = stack.pop()
        if d not in need and d != gid:
            need.add(d)
            stack += [x for x in (by_id[d].get("depends_on") or []) if x in by_id]
    return [g for g in _apply_order(groups) if g in need]


def _apply_order(groups: list[dict[str, Any]]) -> list[str]:
    done: list[str] = []
    remaining = {g["id"]: set(g.get("depends_on") or []) - {"datum"} for g in groups}
    while remaining:
        ready = sorted(g for g, deps in remaining.items() if deps <= set(done))
        if not ready:  # a cycle: keep going in name order rather than failing the integration turn
            ready = sorted(remaining)
        for g in ready:
            done.append(g)
            remaining.pop(g)
    return done


# --- partition handling ------------------------------------------------------------------------

def load_partition(ctx: Ctx) -> dict[str, Any]:
    p = work_dir(ctx) / PARTITION_FILE
    if not p.exists():
        raise PipelineError(f"{p} missing: the partition turn wrote no partition.yaml")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or not isinstance(data.get("groups"), list):
        raise PipelineError(f"{p}: expected a mapping with a `groups` list")
    return data


def validate_partition(ctx: Ctx, data: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    c = ctx.contract
    names = acceptance_names(c)
    feature_ids = {f.id for f in c.features}
    seen_features: dict[str, str] = {}
    seen_items: dict[str, str] = {}
    ids = [str(g.get("id")) for g in data["groups"]]
    for g in data["groups"]:
        gid = str(g.get("id"))
        if not GROUP_RE.match(gid):
            problems.append(f"group id {gid!r} is not a lowerCamel identifier")
        elif gid in RESERVED_IDS or keyword.iskeyword(gid):
            problems.append(f"group id {gid!r} is reserved (its module file would shadow a language or foundation module)")
        for f in g.get("features") or []:
            if f not in feature_ids:
                problems.append(f"group {gid}: unknown feature {f}")
            elif f in seen_features:
                problems.append(f"feature {f} owned by both {seen_features[f]} and {gid}")
            seen_features[f] = gid
        for k, lst in (g.get("acceptance") or {}).items():
            for n in lst or []:
                key = f"{k}:{n}"
                if n not in names.get(k, []):
                    problems.append(f"group {gid}: unknown acceptance item {k}/{n}")
                elif key in seen_items:
                    problems.append(f"acceptance item {k}/{n} owned by both {seen_items[key]} and {gid}")
                seen_items[key] = gid
        for d in g.get("depends_on") or []:
            if d not in ids:
                problems.append(f"group {gid} depends on unknown group {d}")
    for f in feature_ids - set(seen_features):
        problems.append(f"feature {f} is owned by no group")
    for k, lst in names.items():
        for n in lst:
            if f"{k}:{n}" not in seen_items:
                problems.append(f"acceptance item {k}/{n} is owned by no group")
    modules = [g for g in data["groups"] if g.get("id") != "datum"]
    if not 1 <= len(modules) <= 8:
        problems.append(f"{len(modules)} module groups; expected 1 to 8")
    for g in modules:
        reg = g.get("region")
        if not (isinstance(reg, dict) and _vec3(reg.get("min")) and _vec3(reg.get("max"))):
            problems.append(f"group {gid_of(g)}: `region` must be {{min: [x, y, z], max: [x, y, z]}} in mm")
    for stem in ("params", "datum"):
        if not src_path(ctx, stem).exists():
            problems.append(f"{src_path(ctx, stem)} missing")
    return problems


def gid_of(g: dict[str, Any]) -> str:
    return str(g.get("id"))


def _vec3(v: Any) -> bool:
    return isinstance(v, (list, tuple)) and len(v) == 3 and all(isinstance(x, (int, float)) for x in v)


def _in_region(p: list[float] | tuple[float, ...], reg: dict[str, Any], slack: float = 0.5) -> bool:
    lo, hi = reg["min"], reg["max"]
    return all(a - slack <= x <= b + slack for x, a, b in zip(p, lo, hi))


def item_location(contract, kind: str, name: str) -> list[float] | None:
    """A representative point (mm) of an acceptance item, for region assignment."""
    a = contract.acceptance
    key = ACCEPTANCE_KEY.get(kind, "name")
    item = next((x for x in (getattr(a, kind, None) or []) if getattr(x, key) == name), None)
    if item is None:
        return None
    if kind == "cylinders":
        return list(item.point)
    if kind == "faces":
        if item.center is None:
            return None
        ax = "xyz".index(item.plane)
        u, v = [i for i in range(3) if i != ax]
        p = [0.0, 0.0, 0.0]
        p[ax], p[u], p[v] = item.at, item.center[0], item.center[1]
        return p
    if kind == "planes":
        return list(item.point)
    if kind == "probes":
        pts = list(item.points)
        return [sum(p[i] for p in pts) / len(pts) for i in range(3)]
    if kind == "passages":
        return [(a_ + b_) / 2 for a_, b_ in zip(item.point_a, item.point_b)]
    if kind == "solids":
        return list(item.contains_point) if getattr(item, "contains_point", None) else None
    if kind == "thickness" and getattr(item, "region", None):
        lo, hi = item.region
        return [(x + y) / 2 for x, y in zip(lo, hi)]
    return None


def export_scratch(ctx: Ctx, entry: Path, out_dir: Path) -> Path:
    """One STEP export of a scratch main (kernel truth for the composition probe and the datum check)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written = ctx.backend.engine.export(entry, out_dir, "step", deterministic=False)
    return next((w for w in written if w.suffix.lower() in (".step", ".stp")), written[0])


STEP_TRANSLATOR_RE = re.compile(r"STEP translator [\d. ]+")  # OCCT's PRODUCT name carries a per-process write counter


def step_body_sha(step: Path) -> str:
    """Hash of a STEP file without its header (the timestamp): equal bodies mean the same B-rep in the same sub-shape order."""
    body = step.read_text(encoding="utf-8", errors="replace").split("ENDSEC;", 1)[-1]
    return hashlib.sha256(STEP_TRANSLATOR_RE.sub("STEP translator", body).encode()).hexdigest()


def restore_mismatch(ctx: Ctx) -> bool:
    """The edit stage re-exported the untouched source and got a different STEP: the model's booleans are not deterministic."""
    restore = (ctx.load_stage("edit") or {}).get("restore") or {}
    return restore.get("ok") is False and bool(restore.get("re_export_sha256"))


def export_scratch_stl(ctx: Ctx, entry: Path, out_dir: Path) -> Path | None:
    """The STL beside a scratch STEP so passages and wall thickness (voxel / ray checks) are probed per composition step."""
    try:
        written = ctx.backend.engine.export(entry, out_dir, "stl", deterministic=False)
    except EngineError:
        return None
    return next((w for w in written if w.suffix.lower() == ".stl"), None)


def build_scratch(ctx: Ctx, entry: Path, out_dir: Path, *, stl: bool) -> tuple[Path, Path | None]:
    """A scratch main's STEP, and its STL when passages or wall thickness are probed, from one engine run where the engine can."""
    build = getattr(ctx.backend.engine, "build", None)
    if not stl or build is None:
        return export_scratch(ctx, entry, out_dir), export_scratch_stl(ctx, entry, out_dir) if stl else None
    r = build(entry, analyze=False, step=out_dir / f"{entry.stem}.step", stl=out_dir / f"{entry.stem}.stl" if stl else None, deterministic=False)
    if r["step"] is None:
        raise EngineError(f"the engine wrote no STEP for {entry}", kind="unknown")
    return r["step"], r["stl"]


def measure_datum(ctx: Ctx, data: dict[str, Any]) -> dict[str, Any]:
    """Export the datum body once and measure the datum-owned acceptance items on it; failing items are reassigned to the
    module whose region contains them (or reported). Also decides whether an `exterior` group is required."""
    from opencad.stages import inspect_stage

    wd = work_dir(ctx)
    scratch = wd / "datum-check"
    scratch.mkdir(parents=True, exist_ok=True)
    main = scratch / ctx.backend.language.entry
    main.write_text(scratch_main(ctx, [], scratch), encoding="utf-8")
    out: dict[str, Any] = {"ok": True, "reassigned": [], "unplaceable": [], "exterior_required": False, "problems": []}
    try:
        step = export_scratch(ctx, main, scratch)
    except EngineError as e:
        out.update({"ok": False, "error": f"datum export failed ({e.kind}): {str(e)[:300]}", "tooling": is_tooling(e.kind)})
        return out
    m = inspect_stage.measure(step, None, ctx.contract, ctx.design_dir)
    datum_group = next((g for g in data["groups"] if g.get("id") == "datum"), None)
    modules = [g for g in data["groups"] if g.get("id") != "datum" and g.get("region")]
    if datum_group is not None:
        for kind, names in list((datum_group.get("acceptance") or {}).items()):
            for n in list(names or []):
                res = (m.get(kind) or {}).get(n)
                if res is None or res.get("ok"):
                    continue
                loc = item_location(ctx.contract, kind, n)
                home = next((g for g in modules if loc is not None and _in_region(loc, g["region"])), None)
                if home is None:
                    out["unplaceable"].append(f"{kind}/{n}")
                    out["problems"].append(f"datum-owned item {kind}/{n} fails on the datum body and no module region contains it {loc}: assign it to the module that builds it")
                    continue
                names.remove(n)
                home.setdefault("acceptance", {}).setdefault(kind, []).append(n)
                out["reassigned"].append({"item": f"{kind}/{n}", "to": home["id"]})
    # exterior material: datum section areas vs the contract's expected areas
    over = []
    for sid, sec in (m.get("sections") or {}).items():
        exp = (sec.get("checks") or {}).get("area", {}).get("expected")
        meas = (sec.get("checks") or {}).get("area", {}).get("measured")
        if exp and meas:
            over.append(meas > 1.2 * exp)
    if over and sum(over) * 2 > len(over):
        out["exterior_required"] = True
        if not any(g.get("id") == "exterior" or g.get("role") == "exterior" for g in modules):
            out["problems"].append(f"the datum's section area exceeds the contract's by >20 % at {sum(over)} of {len(over)} stations: add an `exterior` group (id `exterior`) that sculpts the envelope, applied first")
    out["datum_measure"] = {k: f"{sum(1 for x in m[k].values() if x.get('ok'))}/{len(m[k])}" for k in ACCEPTANCE_LISTS if m.get(k)}
    out["step"] = str(step)
    return out


# --- composition probe ------------------------------------------------------------------------------

PASSAGE_SHRINK_REL = 0.10  # a module that takes more than this share of another module's sealed air volume is its breaker


def compose_probe(ctx: Ctx, data: dict[str, Any]) -> dict[str, Any]:
    """Compose datum + modules incrementally (one export per step), measure each step against the full contract (STEP and STL,
    so passages and wall thickness are probed too), and intersect the modules' delta solids pairwise: the integrate turn starts
    from what breaks where, not from a guess. `breakers` names the module that first broke or shrank each item."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut

    from opencad.geomcheck import brep
    from opencad.stages import inspect_stage

    groups = [g for g in data["groups"] if g.get("id") != "datum"]
    order = _apply_order(groups)
    wd = work_dir(ctx) / "probe"
    wd.mkdir(parents=True, exist_ok=True)
    steps: list[dict[str, Any]] = []
    shapes: dict[str, Any] = {}
    breakers: dict[str, str] = {}
    prev_shape = None
    prev_passages: dict[str, float] = {}
    prev_passage_ok: dict[str, bool] = {}
    # the edit stage's restore re-export differed from the baseline: export each step twice (separate engine processes) until the
    # first step whose B-rep varies run to run, and name that module the determinism breaker
    check_determinism = restore_mismatch(ctx)
    t_probe = time.time()
    for i in range(0, len(order) + 1):
        applied = order[:i]
        name = "datum" if i == 0 else applied[-1]
        main = wd / f"step{i}{ctx.backend.language.suffixes[0]}"
        main.write_text(scratch_main(ctx, applied, wd), encoding="utf-8")
        row: dict[str, Any] = {"step": i, "applied": applied, "module": name}
        t_step = time.time()
        try:
            step_file, stl_file = build_scratch(ctx, main, wd / f"step{i}", stl=bool(ctx.contract.acceptance.passages or ctx.contract.acceptance.thickness))
            if check_determinism:
                again = export_scratch(ctx, main, wd / f"step{i}-again")
                row["deterministic"] = step_body_sha(step_file) == step_body_sha(again)
                if not row["deterministic"]:
                    breakers.setdefault("export/determinism", name)
                    check_determinism = False  # the onset is what matters; later steps inherit the varying sub-shape order
        except EngineError as e:
            row.update({"ok": False, "error": f"{e.kind}: {str(e)[:400]}"})
            steps.append(row)
            if is_tooling(e.kind):
                return {"steps": steps, "aborted": row["error"], "overlaps": [], "breakers": breakers}
            continue  # a kcl-class failure at this step: the next step tells whether it is this module alone
        row["export_s"] = round(time.time() - t_step, 2)
        m = inspect_stage.measure(step_file, stl_file, ctx.contract, ctx.design_dir)
        row.update({"ok": True, "valid": m["brep"]["valid"], "solids": m["brep"]["solids"], "volume": m["brep"]["volume"],
                    "counts": {k: f"{sum(1 for x in m[k].values() if x.get('ok'))}/{len(m[k])}" for k in ACCEPTANCE_LISTS if m.get(k)},
                    "failing": [f"{k}/{n}" for k in ACCEPTANCE_LISTS for n, x in (m.get(k) or {}).items() if not x.get("ok")]})
        passages = {n: float(x["passage_volume"]) for n, x in (m.get("passages") or {}).items() if isinstance(x.get("passage_volume"), (int, float))}
        passage_ok = {n: bool(x.get("ok")) for n, x in (m.get("passages") or {}).items()}
        shape = brep.read_step(step_file)
        if prev_shape is not None and i > 0:
            added = BRepAlgoAPI_Cut(shape, prev_shape).Shape()
            removed = BRepAlgoAPI_Cut(prev_shape, shape).Shape()
            shapes[name] = {"added": added, "removed": removed, "added_volume": _vol(added), "removed_volume": _vol(removed)}
            row.update({"added_volume": shapes[name]["added_volume"], "removed_volume": shapes[name]["removed_volume"]})
            # items that passed before this module and fail after it were broken by it
            prev_fail = set(steps[-1].get("failing") or [])
            row["newly_failing"] = sorted(set(row["failing"]) - prev_fail)
            row["newly_passing"] = sorted(prev_fail - set(row["failing"]))
            for item in row["newly_failing"]:
                breakers.setdefault(item, name)
            # a sealed, in-band air volume another module carved out and this module part-filled. Before the duct walls exist the
            # "passage" is the whole open air, so only a passage that PASSED before the step counts: enclosing air is not filling it
            shrink = []
            for pn, v0 in prev_passages.items():
                v1 = passages.get(pn)
                if v1 is not None and v0 > 0 and prev_passage_ok.get(pn) and (v0 - v1) / v0 > PASSAGE_SHRINK_REL:
                    shrink.append({"passage": pn, "before": round(v0, 1), "after": round(v1, 1), "module": name})
                    breakers.setdefault(f"passages/{pn}", name)
            if shrink:
                row["passage_shrink"] = shrink
        prev_shape = shape
        prev_passages, prev_passage_ok = passages, passage_ok
        row["seconds"] = round(time.time() - t_step, 2)
        steps.append(row)
    overlaps: list[dict[str, Any]] = []
    names = list(shapes)
    for a_i in range(len(names)):
        for b_i in range(a_i + 1, len(names)):
            a, b = names[a_i], names[b_i]
            for ka in ("added", "removed"):
                for kb in ("added", "removed"):
                    try:
                        common = BRepAlgoAPI_Common(shapes[a][ka], shapes[b][kb]).Shape()
                        v = _vol(common)
                    except Exception:  # an empty or invalid delta solid
                        v = 0.0
                    if v > 0.5:
                        overlaps.append({"a": f"{a}.{ka}", "b": f"{b}.{kb}", "volume": round(v, 3)})
    out = {"order": order, "steps": steps, "overlaps": overlaps, "breakers": breakers,
           "contract_sha": sha256_file(ctx.contract_path) if ctx.contract_path.exists() else None}
    dump_json(work_dir(ctx) / "probe.json", out)
    telemetry.record("stage", ctx.name, {**telemetry.stage_data("probe", time.time() - t_probe, True, [{"seconds": r.get("export_s") or 0} for r in steps]),
                                         "steps": [{k: r.get(k) for k in ("module", "seconds", "export_s")} for r in steps]}, results_dir=ctx.results_dir)
    return out


def _vol(shape) -> float:
    from opencad.geomcheck import brep

    try:
        return float(brep.volume_props(shape)["volume"])
    except Exception:
        return 0.0


def probe_findings_text(probe: dict[str, Any]) -> str:
    if not probe:
        return ""
    if probe.get("aborted"):
        return f"\nComposition probe: unavailable ({probe['aborted']}); compose step by step yourself and run the critic after each module.\n"
    lines = ["", "Composition probe (the pipeline composed datum + modules in order, exported each step and measured it against the full contract):"]
    for s in probe.get("steps", []):
        if not s.get("ok"):
            lines.append(f"- step {s['step']} (+{s['module']}): EXPORT FAILED: {s.get('error')}")
            continue
        extra = ""
        if s.get("newly_failing"):
            extra += f"; breaks {s['newly_failing']}"
        if s.get("newly_passing"):
            extra += f"; fixes {s['newly_passing']}"
        vols = f", adds {s.get('added_volume', 0):.1f} mm3 / removes {s.get('removed_volume', 0):.1f} mm3" if s["step"] else ""
        lines.append(f"- step {s['step']} (+{s['module']}): valid={s['valid']} solids={s['solids']} volume={s['volume']:.1f}{vols}; passing {s['counts']}{extra}")
        for sh in s.get("passage_shrink") or []:
            lines.append(f"  - this module fills {sh['before'] - sh['after']:.0f} mm3 of passage `{sh['passage']}` ({sh['before']:.0f} -> {sh['after']:.0f} mm3): its tools cut into air another module owns")
        if s.get("deterministic") is False:
            lines.append("  - NOT DETERMINISTIC: two exports of this step give different STEP bodies (sub-shape order or topology varies run to run), so the "
                         "export_integrity determinism check and the edit stage's restore re-export fail. This module's booleans must be made deterministic: "
                         "fuse tool solids one at a time in a fixed order instead of passing a Compound of overlapping solids to a boolean; give tools a clear "
                         "overlap (no coincident or tangent faces between tools or against the body); verify with two exports in separate processes")
    if probe.get("breakers"):
        lines.append("- breakers (the module whose step first broke or shrank an item; a correction of that item goes to that module, not to the owner):")
        lines += [f"  - {item}: `{mod}`" for item, mod in sorted(probe["breakers"].items())]
    if probe.get("overlaps"):
        lines.append("- delta-solid overlaps between modules (material two modules both add/remove in the same place; the usual source of failed booleans and leaked passages):")
        lines += [f"  - {o['a']} x {o['b']}: {o['volume']} mm3" for o in probe["overlaps"]]
    else:
        lines.append("- no delta-solid overlaps between modules")
    lines.append(f"Full data: `{'probe.json'}` in the decompose work dir. Start from the first step that breaks an item.")
    return "\n".join(lines) + "\n"


def composed_only_sections(raw: dict[str, Any], group: dict[str, Any], partition: dict[str, Any] | None) -> list[str]:
    """Section ids whose plane also cuts another group's region: their area / loops / holes exist only on the composed part. Held to the
    full-part band standalone, a module carves fake air or adds fake material to hit a number its own region cannot produce."""
    if not partition:
        return []
    others = [g for g in partition.get("groups", []) if g.get("id") not in (group.get("id"), "datum") and g.get("region")]
    out = []
    for s in (raw.get("acceptance") or {}).get("sections") or []:
        try:
            k, v = "xyz".index(str(s["plane"])), float(s["at"])
        except (KeyError, ValueError):
            continue
        if any(float(g["region"]["min"][k]) - 1e-6 <= v <= float(g["region"]["max"][k]) + 1e-6 for g in others):
            out.append(s["id"])
    return out


def write_subcontract(ctx: Ctx, group: dict[str, Any], dest: Path, extra_items: list[str] | None = None, partition: dict[str, Any] | None = None) -> Path:
    """The contract restricted to what the group owns: same frame, envelope and parameters; only its features and acceptance items; no mass
    properties. `extra_items` (`kind/name`) are items a correction round assigned to this module beyond its partition (breaker attribution).
    With `partition`, sections whose plane crosses another group's region are left to the composed critic (named in the intent)."""
    raw = yaml.safe_load(ctx.contract_path.read_text(encoding="utf-8"))
    owned = {k: set(v or []) for k, v in (group.get("acceptance") or {}).items()}
    for item in extra_items or []:
        kind, _, name = item.partition("/")
        if kind in ACCEPTANCE_LISTS and name:
            owned.setdefault(kind, set()).add(name)
    composed_only = [s for s in composed_only_sections(raw, group, partition) if s in owned.get("sections", set())]
    owned["sections"] = owned.get("sections", set()) - set(composed_only)
    feats = set(group.get("features") or [])
    # cross-referenced items come along as measurement context (a gear needs its solid, a mesh both gears' solids, a dimension its faces)
    acc0 = raw.get("acceptance") or {}
    by = {k: {x.get(ACCEPTANCE_KEY.get(k, "name")): x for x in (acc0.get(k) or [])} for k in ACCEPTANCE_LISTS}
    changed = True
    while changed:
        changed = False

        def pull(kind: str, name: str | None) -> None:
            nonlocal changed
            if name and name in by.get(kind, {}) and name not in owned.setdefault(kind, set()):
                owned[kind].add(name)
                changed = True

        for n in list(owned.get("gears", ())):
            pull("solids", by["gears"][n].get("solid")) if n in by["gears"] else None
        for n in list(owned.get("meshes", ())):
            if n in by["meshes"]:
                pull("solids", by["meshes"][n].get("a"))
                pull("solids", by["meshes"][n].get("b"))
        for n in list(owned.get("clearances", ())):
            if n in by["clearances"]:
                pull("solids", by["clearances"][n].get("a"))
                pull("solids", by["clearances"][n].get("b"))
        for n in list(owned.get("dimensions", ())):
            for fn in (by["dimensions"].get(n, {}).get("between") or ()):
                pull("faces", fn)
        for kind in ("sections", "cylinders", "faces", "planes", "probes", "thickness", "passages", "cylinder_counts"):
            for n in list(owned.get(kind, ())):
                pull("solids", by[kind].get(n, {}).get("solid"))
    raw["features"] = [f for f in raw.get("features", []) if f.get("id") in feats]
    if not raw["features"]:  # a group that owns only acceptance items still needs one feature entry for a valid contract
        raw["features"] = [{"id": f"{group['id']}Scope", "kind": "other", "description": f"module {group['id']}: {group.get('title', '')}".strip(), "parameters": [], "verify": []}]
    # features that verify against items another group owns lose those probes here (they are judged at integration)
    owned_names = {n for lst in owned.values() for n in (lst or [])}
    ref_fields = ("section", "face", "cylinder", "plane", "dimension")
    for f in raw["features"]:
        f["verify"] = [v for v in (f.get("verify") or []) if all(not v.get(k) or v.get(k) in owned_names for k in ref_fields)]
    acc = raw.setdefault("acceptance", {})
    for k in ACCEPTANCE_LISTS:
        key = ACCEPTANCE_KEY.get(k, "name")
        acc[k] = [x for x in (acc.get(k) or []) if x.get(key) in owned.get(k, set())]
    for k in ("volume", "surface_area", "center_of_mass", "deviation"):
        acc[k] = None
    if not owned.get("clearances"):
        acc.pop("hardware", None)
    # interfaces pin acceptance items; keep only the pins this group owns (an interface with none left is dropped here, judged at integration)
    kept_ifaces = []
    for i in raw.get("interfaces") or []:
        checks = [c for c in (i.get("checks") or []) if c in owned_names]
        if checks:
            kept_ifaces.append({**i, "checks": checks})
    raw["interfaces"] = kept_ifaces
    raw["name"] = f"{ctx.name}-{group['id']}"
    raw["intent"] = f"[module {group['id']}] " + str(raw.get("intent", ""))
    if composed_only:
        raw["intent"] += (f" Sections {', '.join(sorted(composed_only))} cut other modules' regions and are judged on the composed part only "
                          "(the composed critic in the brief); this module's standalone composition is not expected to match their bands.")
    raw["open_questions"] = [q for q in raw.get("open_questions", []) if not str(q).lower().startswith("blocking:")]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(yaml.safe_dump(raw, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
    load_contract(dest)  # raises if the subset is not a valid PartContract
    return dest


# --- module-level corrections --------------------------------------------------------------------------

def failing_items(ctx: Ctx) -> dict[str, list[str]]:
    """Acceptance items the last inspect stage failed, by table (the edit stage's failures are integrate-level)."""
    ins = ctx.load_stage("inspect") or {}
    return {k: sorted(n for n, x in (ins.get(k) or {}).items() if isinstance(x, dict) and not x.get("ok")) for k in ACCEPTANCE_LISTS if ins.get(k)}


def thin_spots(ctx: Ctx) -> dict[str, list[list[float]]]:
    """Centres of each failing thickness item's thin-skin clusters (from the last inspect stage), for module attribution."""
    ins = ctx.load_stage("inspect") or {}
    out: dict[str, list[list[float]]] = {}
    for name, th in (ins.get("thickness") or {}).items():
        if isinstance(th, dict) and not th.get("ok"):
            pts = [[(a + b) / 2 for a, b in zip(c["min"], c["max"])] for c in (th.get("thin_clusters") or [])]
            out[f"thickness/{name}"] = pts or [list(p) for p in (th.get("thinnest_points") or [])]
    return out


def _region_owner(data: dict[str, Any], point: list[float] | None) -> str | None:
    """The most specific (smallest) non-datum group region that holds the point (0.5 mm slack); regions often nest or overlap."""
    if point is None:
        return None
    hits: list[tuple[float, str]] = []
    for g in data.get("groups", []):
        reg = g.get("region")
        if g.get("id") == "datum" or not reg:
            continue
        lo, hi = reg["min"], reg["max"]
        if all(float(a) - 0.5 <= p <= float(b) + 0.5 for p, a, b in zip(point, lo, hi)):
            vol = 1.0
            for a, b in zip(lo, hi):
                vol *= max(float(b) - float(a), 1e-6)
            hits.append((vol, str(g["id"])))
    return min(hits)[1] if hits else None


def owners(data: dict[str, Any], items: dict[str, list[str]], breakers: dict[str, str] | None = None, contract=None,
           thin_spots: dict[str, list[list[float]]] | None = None) -> dict[str, list[str]]:
    """Failing items grouped by the module that must fix them: the module the composition probe caught breaking or shrinking the
    item (`breakers`), else the module that owns it (partition.json), else (an item added to the contract after the partition) the
    module whose region holds it. `datum`-owned and still-unowned items are integrate-level. A thickness item with `thin_spots`
    (centres of its thin-skin clusters) goes to EVERY module whose region holds one: thin skins sit on module boundaries."""
    own: dict[str, str] = {}
    for g in data.get("groups", []):
        for k, lst in (g.get("acceptance") or {}).items():
            for n in lst or []:
                own[f"{k}/{n}"] = str(g.get("id"))
    order = _apply_order([g for g in data.get("groups", []) if g.get("id") != "datum"])
    pos = {gid: i for i, gid in enumerate(order)}
    # an item renamed or added after the partition has no owner; when one module owns every item of its kind (all passages are the
    # duct module's), it takes the newcomer too, before the smallest-region fallback (which handed the duct passages to `fasteners`)
    by_kind: dict[str, set[str]] = {}
    for key, gid in own.items():
        if gid != "datum":
            by_kind.setdefault(key.split("/", 1)[0], set()).add(gid)
    affinity = {k: next(iter(g)) for k, g in by_kind.items() if len(g) == 1}
    out: dict[str, list[str]] = {}
    for k, names in items.items():
        for n in names:
            key = f"{k}/{n}"
            if k == "thickness" and (thin_spots or {}).get(key):
                holders = {g for p in thin_spots[key] for g in [_region_owner(data, p)] if g and g != "datum"}
                if (breakers or {}).get(key) in pos:  # the module whose step first broke the wall shares every thin boundary it made
                    holders.add(breakers[key])
                if holders:
                    for g in sorted(holders):
                        out.setdefault(g, []).append(key)
                    continue
            breaker, owner = (breakers or {}).get(key), own.get(key)
            if breaker and owner and breaker != owner and pos.get(breaker, -1) < pos.get(owner, -1):
                breaker = None  # the item did not exist before its owner was applied: an earlier step cannot have broken it
            gid = breaker or owner or affinity.get(k)
            if gid is None and contract is not None and k == "faces":
                gid = _plane_owner(contract, own, n)
            if gid is None and contract is not None and k != "sections":
                # a section plane crosses every region: with no breaker and no owner it is the integrate turn's, not a region guess
                gid = _region_owner(data, item_location(contract, k, n))
            if gid and gid != "datum":
                out.setdefault(gid, []).append(key)
    return out


def _plane_owner(contract, own: dict[str, str], name: str) -> str | None:
    """An unowned face (added after the partition, typically a summed whole-plane face) goes to the module that owns the other
    faces on the same plane, when there is exactly one such module."""
    specs = {f.name: f for f in (contract.acceptance.faces or [])}
    f = specs.get(name)
    if f is None:
        return None
    mods = {own.get(f"faces/{o.name}") for o in specs.values() if o.name != name and o.plane == f.plane and abs(float(o.at) - float(f.at)) < 1e-6}
    mods -= {None, "datum"}
    return next(iter(mods)) if len(mods) == 1 else None


def probe_is_stale(ctx: Ctx, data: dict[str, Any]) -> bool:
    """True when a module source changed after probe.json was written (a correction round edited it), so breaker attribution must be re-measured."""
    pj = work_dir(ctx) / "probe.json"
    if not pj.exists():
        return False  # never probed (older run): attribution falls back to ownership rather than spending exports here
    t = pj.stat().st_mtime
    return any(src_path(ctx, g["id"]).exists() and src_path(ctx, g["id"]).stat().st_mtime > t for g in data.get("groups", []) if g.get("id") != "datum")


def module_correction_brief(ctx: Ctx, group: dict[str, Any], items: list[str], correction: str, sub_contract: Path, scratch: Path, probe_text: str,
                            partition: dict[str, Any] | None = None, composed: Path | None = None) -> str:
    gid = group["id"]
    module = src_path(ctx, gid)
    entry = scratch / ctx.backend.language.entry
    composed = composed or scratch / f"composed{ctx.backend.language.suffixes[0]}"
    relevant = [l for l in correction.splitlines() if any(n.split("/", 1)[1] in l for n in items)]
    if "export/determinism" in items:
        relevant.append("- export/determinism: this module is the first composition step whose STEP differs between two exports of the same source "
                        "(see the NOT DETERMINISTIC step in the composition probe below); make its booleans deterministic")
    what = ("is the integrated entry the gates inspect (every module plus the integrate-level operations)" if composed == ctx.kcl_target
            else "composes datum + every module (current files, apply order)")
    composed_text = (f"\nThe gates measure the COMPOSED part. `{_critic(ctx, composed, ctx.contract_path)}` {what} and checks the full contract: "
                     "run it after each change and report your items' composed values under `## Verification`; the standalone critic below only proves "
                     "your module executes and holds its own items. Sections and faces that fail standalone but pass composed are not your defect; "
                     "sections that fail composed by material inside your region are.\n"
                     if composed.exists() else "")
    return f"""Correct ONE feature-group module of the part: `{module}` (group `{gid}`, {group.get('title', '')}).

Skills: read {' and '.join(str(p) for p in ctx.backend.language.skills())} first.

The composed part failed its gates; these failing acceptance items belong to this module: {items}.
Measured vs expected for them (from the pipeline's inspection of the composed STEP):
{chr(10).join(relevant) if relevant else correction}
{probe_text}{composed_text}
Rules: edit only `{module}` (its `{recipe(ctx, gid)['signature']}`); keep every other module untouched. Re-verify standalone with
`{_critic(ctx, entry, sub_contract)}` (the scratch main from the module turn
composes datum + dependencies + this module). If a boolean fails, {_bisect(ctx, entry)}. Keep the module executing.
{_region_text(group, partition or {"groups": [group]}, ctx.contract)}
{ctx.backend.language.rules()}
Under `## Verification` list each item measured vs expected after the fix; under `## Open questions` anything that needs the integrate turn.
If the composed critic shows an assigned item is not produced by this module, do not change geometry for it: add a `## Not this module`
section with one bullet per item, `- kind/name: which file or module owns it and why`; the pipeline stops re-issuing it to you and
hands it to the integrate turn.
"""


def module_corrections(ctx: Ctx, correction: str, key: str) -> dict[str, Any] | None:
    """For a decomposed part: one parallel correction order per module that owns a failing item, before the integrate-level correction.
    Returns None when the part is not decomposed or no module owns a failing item. May raise WorkerPending."""
    mdl = ctx.load_stage("model") or {}
    pj = work_dir(ctx) / "partition.json"
    if not mdl.get("decomposed") or not pj.exists():
        return None
    data = json.loads(pj.read_text(encoding="utf-8"))
    if not (work_dir(ctx) / f"module-targets-{key}.json").exists() and probe_is_stale(ctx, data):
        try:  # re-measure the composition so the breaker of each failing item is the current one
            compose_probe(ctx, data)
        except EngineError as e:
            print(f"composition probe skipped before {key}: {e.kind}: {str(e)[:200]}", flush=True)
    with telemetry.timed("briefs", ctx.name, ctx.results_dir, key=key):
        return _module_orders(ctx, correction, key, mdl, data)


def _module_orders(ctx: Ctx, correction: str, key: str, mdl: dict[str, Any], data: dict[str, Any]) -> dict[str, Any] | None:
    groups = {g["id"]: g for g in data.get("groups", []) if g.get("id") != "datum"}
    probe_path = work_dir(ctx) / "probe.json"
    targets_path = work_dir(ctx) / f"module-targets-{key}.json"
    if targets_path.exists():
        # a continued round: the orders were issued from this attribution; re-deriving it now (modules changed, the probe re-ran)
        # would hand the finished orders' items to other modules and leave the finished orders unconsumed
        targets = [(gid, items) for gid, items in json.loads(targets_path.read_text(encoding="utf-8"))]
        probe = json.loads(probe_path.read_text(encoding="utf-8")) if probe_path.exists() else {}
    else:
        probe = json.loads(probe_path.read_text(encoding="utf-8")) if probe_path.exists() else {}
        failing = failing_items(ctx)
        last = (probe.get("steps") or [{}])[-1]
        same_contract = probe.get("contract_sha") and ctx.contract_path.exists() and probe["contract_sha"] == sha256_file(ctx.contract_path)
        if same_contract and last.get("ok") and isinstance(last.get("failing"), list) and not probe_is_stale(ctx, data):
            # an item that passes with every module composed and fails only on the integrated entry was broken by integrate-level
            # code (main.py); no module can fix it, so it is not issued to one
            still = set(last["failing"])
            integrate_level = [f"{k}/{n}" for k, names in failing.items() for n in names if f"{k}/{n}" not in still]
            if integrate_level:
                print(f"{key}: left to the integrate turn (pass with all modules composed): {', '.join(integrate_level)}", flush=True)
            failing = {k: [n for n in names if f"{k}/{n}" in still] for k, names in failing.items()}
        spots = thin_spots(ctx)
        by_group = owners(data, failing, probe.get("breakers"), ctx.contract, spots)
        det = (probe.get("breakers") or {}).get("export/determinism")
        if det in groups and restore_mismatch(ctx):
            by_group.setdefault(det, []).append("export/determinism")  # a synthetic item: no sub-contract entry, the probe text says what to fix
        # an item a module's worker declined (`## Not this module`) in an earlier round is not re-issued to it; when the decline names
        # another module as the owner, the item is handed to that module (even if it passes there by the partition's reckoning).
        # A thickness item placed by its thin-skin clusters is evidence, not a guess: it overrides an earlier decline
        declined = load_declined(ctx)
        by_group = {gid: [i for i in items if i not in declined.get(gid, {}) or i in spots] for gid, items in by_group.items()}
        still_failing = {f"{k}/{n}" for k, names in failing.items() for n in names}
        for item, target in handoffs(declined, set(groups)).items():
            if item in still_failing and item not in declined.get(target, {}) and item not in by_group.get(target, []):
                by_group.setdefault(target, []).append(item)
                for gid, items in by_group.items():
                    if gid != target and item in items:
                        items.remove(item)
        targets = [(gid, items) for gid, items in by_group.items() if items and gid in groups and src_path(ctx, gid).exists()]
        if not targets:
            return None
        targets_path.write_text(json.dumps(targets), encoding="utf-8")
    probe_text = probe_findings_text(probe) if probe else ""
    order = _apply_order(list(groups.values()))
    snap = ctx.results_dir / "snapshots"
    images = [p for p in (snap / "view-compare.png", snap / "view-all.png") if p.exists()]  # rendered by the retry loop before this call
    specs = []
    for gid, items in targets:
        scratch = work_dir(ctx) / gid
        sub = scratch / "contract.yaml"
        # regenerated every round: the design contract may have changed since the module turn, and the items this round assigns to the
        # module (breaker attribution) must be in the critic the worker runs
        write_subcontract(ctx, groups[gid], sub, extra_items=items, partition=data)
        # the worker measures its items where the gates measure them: the integrated entry itself once the integrate turn wrote it
        # (module code + integrate-level operations), else a scratch entry composing every module, never the datum + dependencies +
        # module scratch alone, whose sections and faces cannot match the full part
        if ctx.kcl_target.exists():
            composed = ctx.kcl_target
        else:
            composed = scratch / f"composed{ctx.backend.language.suffixes[0]}"
            composed.write_text(scratch_main(ctx, [g for g in order if src_path(ctx, g).exists()], scratch), encoding="utf-8")
        thread = ((mdl.get("modules") or {}).get(gid) or {}).get("thread_id")
        specs.append(dict(brief=module_correction_brief(ctx, groups[gid], items, correction, sub, scratch, probe_text, data, composed=composed), role="correction", key=f"{key}-{gid}",
                          results_dir=ctx.results_dir, part=ctx.name, cd=scratch, run_dir=scratch / "codex-correction", add_dirs=[ctx.part_dir], timeout=ctx.timeout,
                          deliverables=[src_path(ctx, gid)], context={"contract": str(sub)}, resume=thread or None, images=images,
                          budget=worker.scaled_budget("module", len(items), ctx.backend.engine) / 2))
    results = worker.dispatch_many(specs)
    record_declined(ctx, {gid: r for (gid, _), r in zip(targets, results)})
    return {"modules": {gid: r.summary() for (gid, _), r in zip(targets, results)}, "items": dict(targets)}


def clear_module_targets(ctx: Ctx) -> None:
    """Forget the per-round module attributions (a fresh correction loop reuses the round keys)."""
    for p in work_dir(ctx).glob("module-targets-*.json"):
        p.unlink()


DECLINED_FILE = "declined.json"
DECLINE_RE = re.compile(r"^\s*[-*]\s*`?([a-z_]+/[A-Za-z0-9_.+-]+)`?\s*[:\u2014-]\s*(.*)$")


def load_declined(ctx: Ctx) -> dict[str, dict[str, str]]:
    p = work_dir(ctx) / DECLINED_FILE
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")) or {}
    except json.JSONDecodeError:
        return {}


HANDOFF_RE = re.compile(r"owne[rd]\b[^`\w]*(?:by\s+)?`?(\w+)`?", re.IGNORECASE)
OWNS_RE = re.compile(r"`?(\w+)`?\s+owns?\b", re.IGNORECASE)  # "clamp owns the second loop ..."
LEAD_RE = re.compile(r"^\s*`?(\w+)`?\s*(?:[—–\-:/,(]|$)")  # "clamp — the 67.94 mm2 patch ...", "keyhole / fasteners — ..."


def handoffs(declined: dict[str, dict[str, str]], modules: set[str]) -> dict[str, str]:
    """item -> module named as its owner in a decline reason ("owner sideClamp", "owned by exterior", "clamp owns ...", or a reason
    that opens with the module's name); later declines win."""
    out: dict[str, str] = {}
    for _gid, items in declined.items():
        for item, reason in items.items():
            text = reason or ""
            for rx in (HANDOFF_RE, LEAD_RE, OWNS_RE):  # a leading "clamp/exterior own ..." names clamp, not exterior
                hit = next((m.group(1) for m in rx.finditer(text) if m.group(1) in modules), None)
                if hit:
                    out[item] = hit
                    break
    return out


def record_declined(ctx: Ctx, results: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Merge each module worker's `## Not this module` bullets (`- kind/name: reason`) into the decompose work dir."""
    declined = load_declined(ctx)
    for gid, r in results.items():
        for line in (getattr(r, "sections", {}) or {}).get("Not this module", "").splitlines():
            m = DECLINE_RE.match(line)
            if m:
                declined.setdefault(gid, {})[m.group(1)] = m.group(2).strip()
    if declined:
        (work_dir(ctx) / DECLINED_FILE).write_text(json.dumps(declined, indent=2), encoding="utf-8")
    return declined


# --- the stage -----------------------------------------------------------------------------------

def run(ctx: Ctx) -> dict[str, Any]:
    plan = ctx.load_stage("plan") or {}
    plan_path = Path(plan.get("plan_md") or (ctx.results_dir / "plan.md"))
    plan_md = plan_path.read_text(encoding="utf-8") if plan_path.exists() and not plan.get("folded") else ""
    wd = work_dir(ctx)
    if worker.fresh(ctx.results_dir, "partition"):
        if wd.exists():
            shutil.rmtree(wd)
        wd.mkdir(parents=True)
        ctx.part_dir.mkdir(parents=True, exist_ok=True)
    ctx.part_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {"decomposed": True}

    # 1. partition (+ one validation round)
    n_items = sum(len(v) for v in acceptance_names(ctx.contract).values())
    params, datum = src_path(ctx, "params"), src_path(ctx, "datum")
    check = wd / "datum-check"  # the partition worker's critic target; measure_datum exports the same file afterwards
    check.mkdir(parents=True, exist_ok=True)
    (check / ctx.backend.language.entry).write_text(scratch_main(ctx, [], check), encoding="utf-8")
    r = worker.dispatch(partition_brief(ctx, plan_md), role="partition", key="partition", results_dir=ctx.results_dir, part=ctx.name, cd=wd, run_dir=wd / "codex-partition",
                        add_dirs=[ctx.part_dir], timeout=ctx.timeout, deliverables=[wd / PARTITION_FILE, params, datum],
                        budget=worker.scaled_budget("partition", n_items))
    summary["partition"] = r.summary()
    data = load_partition(ctx) if (wd / PARTITION_FILE).exists() else {"groups": []}
    problems = validate_partition(ctx, data) if data["groups"] else ["no groups"]
    if problems:
        fix = ("The partition is not usable yet. Problems:\n- " + "\n- ".join(problems[:40]) + f"\nFix partition.yaml / {params.name} / {datum.name} in place and re-verify.")
        r2 = worker.dispatch(fix, role="partition", key="partition-2", results_dir=ctx.results_dir, part=ctx.name, cd=wd, run_dir=wd / "codex-partition-2",
                             resume=r.thread_id or None, add_dirs=[ctx.part_dir], timeout=ctx.timeout, deliverables=[wd / PARTITION_FILE])
        summary["partition_fix"] = r2.summary()
        data = load_partition(ctx)
        problems = validate_partition(ctx, data)
        if problems:
            summary.update({"ok": False, "partition_problems": problems, "thread_id": r2.thread_id or r.thread_id})
            ctx.write_stage("model", {**summary, "worker": summary["partition"], "codex": summary["partition"], "kcl": str(ctx.kcl_target), "files": _files(ctx)})
            print(f"decompose FAILED: partition still invalid after one correction: {problems[:5]}")
            return ctx.load_stage("model") or summary
    # 1b. the datum measured: failing datum-owned items move to the module whose region holds them; an exterior group when the envelope is oversized
    dm = measure_datum(ctx, data)
    summary["datum_check"] = {k: v for k, v in dm.items() if k != "step"}
    if dm.get("problems"):
        fix = ("The datum body was exported and measured against the contract. Problems:\n- " + "\n- ".join(dm["problems"][:40])
               + f"\nFix partition.yaml (group assignment, regions, an `exterior` group) and/or {datum.name} in place and re-verify.")
        r2b = worker.dispatch(fix, role="partition", key="partition-3", results_dir=ctx.results_dir, part=ctx.name, cd=wd, run_dir=wd / "codex-partition-3",
                              resume=r.thread_id or None, add_dirs=[ctx.part_dir], timeout=ctx.timeout, deliverables=[wd / PARTITION_FILE])
        summary["partition_fix_measured"] = r2b.summary()
        data = load_partition(ctx)
        problems = validate_partition(ctx, data)
        if problems:
            summary.update({"ok": False, "partition_problems": problems, "thread_id": r2b.thread_id or r.thread_id})
            ctx.write_stage("model", {**summary, "worker": summary["partition"], "codex": summary["partition"], "kcl": str(ctx.kcl_target), "files": _files(ctx)})
            print(f"decompose FAILED: partition invalid after the measured check: {problems[:5]}")
            return ctx.load_stage("model") or summary
        dm = measure_datum(ctx, data)
        summary["datum_check"] = {k: v for k, v in dm.items() if k != "step"}
    dump_json(wd / "partition.json", data)
    groups = [g for g in data["groups"] if g.get("id") != "datum"]

    # 2. modules, in parallel
    specs = []
    for g in groups:
        gid = g["id"]
        scratch = wd / gid
        scratch.mkdir(parents=True, exist_ok=True)
        sub = write_subcontract(ctx, g, scratch / "contract.yaml", partition=data)
        main = scratch / ctx.backend.language.entry
        if not main.exists():  # the module's critic target: datum + its (transitive) dependencies + itself
            main.write_text(scratch_main(ctx, _prereqs(groups, gid) + [gid], scratch), encoding="utf-8")
        owned = sum(len(v or []) for v in (g.get("acceptance") or {}).values())
        specs.append(dict(brief=module_brief(ctx, g, sub, scratch, data), role="module", key=f"module-{gid}", results_dir=ctx.results_dir, part=ctx.name, cd=scratch,
                          run_dir=scratch / "codex", add_dirs=[ctx.part_dir], timeout=ctx.timeout, deliverables=[src_path(ctx, gid)], context={"contract": str(sub)},
                          budget=worker.scaled_budget("module", owned, ctx.backend.engine)))
    results = worker.dispatch_many(specs)
    summary["modules"] = {g["id"]: res.summary() for g, res in zip(groups, results)}
    summary["modules_ok"] = {g["id"]: res.ok for g, res in zip(groups, results)}

    # 2b. composition probe: compose incrementally, measure, intersect the deltas; the integrate brief starts from the findings
    probe = compose_probe(ctx, data)
    summary["probe"] = {"steps": [{k: v for k, v in s.items() if k in ("step", "module", "ok", "valid", "solids", "newly_failing", "error")} for s in probe.get("steps", [])],
                        "overlaps": probe.get("overlaps", []), "aborted": probe.get("aborted")}
    if str(probe.get("aborted") or "").startswith("billing:"):
        result = {**summary, "ok": False, "class": "billing", "error": f"integrate not dispatched; the engine refuses hosted calls: {probe['aborted']}",
                  "kcl": str(ctx.entry), "files": _files(ctx)}
        ctx.write_stage("model", result)
        print(f"decompose FAILED (billing): {result['error'][:300]}")
        return result

    # 3. integrate
    r3 = worker.dispatch(integrate_brief(ctx, data, probe), role="integrate", key="integrate", results_dir=ctx.results_dir, part=ctx.name, cd=wd / "integrate", run_dir=wd / "integrate" / "codex",
                         add_dirs=[ctx.part_dir], timeout=ctx.timeout, deliverables=[ctx.entry], context={"contract": str(ctx.contract_path)},
                         budget=worker.scaled_budget("integrate", len(groups), ctx.backend.engine))
    from opencad.stages.model import _incomplete, restore_checkpoint, timed_out, turn_ok

    restored = timed_out(r3) and restore_checkpoint(ctx, integrate_checkpoint(ctx), wd / "integrate")
    produced = ctx.entry.exists()
    if produced:
        for f in sorted(p for p in ctx.part_dir.iterdir() if p.suffix in ctx.backend.language.suffixes):
            ctx.backend.language.format_write(f)

    s3 = r3.summary()
    result = {
        **summary, "ok": turn_ok(r3, produced), "timed_out": timed_out(r3), "restored_checkpoint": restored, "self_reported_incomplete": _incomplete(r3),
        "worker": s3, "codex": s3, "thread_id": r3.thread_id, "codex_report": r3.sections,
        "kcl": str(ctx.entry), "source": str(ctx.entry), "files": _files(ctx), "changed": _files(ctx), "groups": [g["id"] for g in groups],
    }
    ctx.write_stage("model", result)
    print(f"decompose {'ok' if result['ok'] else 'FAILED'}: {len(groups)} modules ({sum(1 for v in summary['modules_ok'].values() if v)} ok), integrate {r3.backend} {r3.seconds:.0f}s"
          + ("; the integrate turn hit its budget, the deliverable is measured as left" if timed_out(r3) else "")
          + ("; restored the last executing checkpoint" if restored else "")
          + ("; the worker reports the deliverable as INCOMPLETE" if result["self_reported_incomplete"] else ""))
    return result


def _files(ctx: Ctx) -> list[str]:
    return sorted(p.name for p in ctx.part_dir.iterdir() if p.is_file()) if ctx.part_dir.exists() else []

"""`python -m opencad sim study <asm> <sim> --case <id>`: one simulation's mesh ladder on one operating case, run into the same work
directories as the simulate stage, so the pipeline adopts every finished run whose inputs still hash the same. Prints each level's
value (the mean of its last iterations), iteration spread and drift, then the grid-convergence index and whether the prediction is
resolved. `--levels`, `--regions` and `--set` try a ladder or setting before a contract states it (an amendment that states the same
values reuses these runs); `--dry-run` writes each level's case aside and says whether a finished run would be reused, running nothing."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from typing import Any


def _value(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def simulation(contract: Any, sim_id: str, case: str, *, levels: str | None = None, regions: str | None = None, sets: list[str] = ()) -> Any:
    """The contract's simulation restricted to one case, with the overrides applied."""
    from opencad.schemas import Simulation

    s = next((s for s in contract.simulations if s.id == sim_id), None)
    if s is None:
        raise KeyError(f"no simulation {sim_id!r} (have {[x.id for x in contract.simulations]})")
    if case not in s.cases:
        raise KeyError(f"simulation {sim_id} does not run case {case!r} (cases {s.cases})")
    d = s.model_dump()
    d["cases"] = [case]
    if levels:
        d["refinement"] = json.loads(levels)
    if regions:
        d["regions"] = json.loads(regions)
    for kv in sets:
        k, _, v = kv.partition("=")
        d["settings"][k] = _value(v)
    return Simulation.model_validate(d)


def table(r: dict[str, Any]) -> list[str]:
    """Per observable: each mesh level's value, iteration spread, drift and last sample, then the ladder's GCI and verdict."""
    lines = []
    for oid, st in (r.get("observables") or {}).items():
        lines.append(f"{oid}:")
        lines.append(f"  {'level':<14}{'cells':>10}{'value':>14}{'u_iter':>11}{'drift':>9}{'last':>14}")
        for i, lab in enumerate(st.get("mesh_levels") or []):
            cells, drift, u_it, last = st["cells"][i], st["drift"][i], st["u_iterations"][i], st["last"][i]
            lines.append(f"  {lab:<14}{cells or '-':>10}{st['levels'][i]:>14.6g}{(f'{u_it:.3g}' if u_it is not None else '-'):>11}"
                         f"{(f'{drift:.4f}' if drift is not None else '-'):>9}{(f'{last:.6g}' if last is not None else '-'):>14}")
        if st.get("gci") is not None:
            order = f"p {st['order']:.2f}" if st.get("order") is not None else "p assumed"
            ext = f"{st['extrapolated']:.6g}" if st.get("extrapolated") is not None else "-"
            lines.append(f"  GCI {st['gci']:.4f} ({st.get('convergence')}, {order}, Fs {st.get('fs')}); extrapolated {ext}; "
                         f"u_discretisation {st['u_discretisation']:.4g}, u_numerical {st['u_numerical']:.4g}")
        lines.append(f"  resolved: {st.get('resolved')}" + (f" ({'; '.join(st.get('unresolved_because') or [])})" if not st.get("resolved") else ""))
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="opencad sim", description=__doc__)
    sub = ap.add_subparsers(dest="verb", required=True)
    p = sub.add_parser("study", help="one simulation's mesh ladder on one operating case (runs adopted by the simulate stage)")
    p.add_argument("asm")
    p.add_argument("sim")
    p.add_argument("--case", required=True)
    p.add_argument("--levels", help='JSON ladder replacing the contract\'s, e.g. \'[1.0, {"factor": 1.0, "regions": {"tip": 1}, "iterations": 3000}]\'')
    p.add_argument("--regions", help="JSON list replacing the simulation's refinement regions")
    p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="override one numerical setting (JSON value)")
    p.add_argument("--dry-run", action="store_true", help="write the cases aside and report reuse or compute per level; run nothing")
    p.add_argument("--backend", default=None)
    args = ap.parse_args(argv)
    from opencad.assembly import AsmCtx
    from opencad.assembly.simulate import Geometry, adapter
    from opencad.backends.registry import set_backend
    from opencad.io import dump_json

    if args.backend:
        set_backend(args.backend)
    actx = AsmCtx.load(args.asm, backend=args.backend)
    try:
        s = simulation(actx.contract, args.sim, args.case, levels=args.levels, regions=args.regions, sets=args.set)
    except (KeyError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    obs = [o for o in actx.contract.observables if o.id in s.outputs and o.case in (args.case, None)]
    cases = {c.id: c for c in actx.contract.operating_cases}
    geom = Geometry(actx)
    if args.dry_run:
        if s.solver != "openfoam":
            print("error: --dry-run applies to openfoam simulations", file=sys.stderr)
            return 2
        from opencad.sim import openfoam

        scratch = actx.results_dir / "sim.dry-run"
        try:
            r = openfoam.run(s, obs, geom, cases, dry_root=scratch)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        for run in r["runs"]:
            print(f"{run['case']} level {run['label']}: {'reuse ' + run['reuse'] if run['reuse'] else 'compute'}; estimate {run['cells_estimate'] / 1e6:.2f} M cells, "
                  f"{run['memory_estimate_gb']} GB" + (" (over memory_cap_gb: skipped)" if run["skipped"] else "")
                  + "".join(f"; region {k}: {v}" for k, v in (run.get("refinement_regions") or {}).items()))
        return 0
    print(f"== sim study {args.asm}/{s.id} case {args.case}: {[lv.label for lv in s.levels()]} ==", flush=True)
    r = adapter(s.solver).run(s, obs, geom, cases)
    out = actx.results_dir / "sim" / s.id / f"study-{args.case}.json"
    dump_json(out, {"simulation": s.model_dump(), "result": r})
    for e in r.get("errors") or []:
        print(f"error: {e[:400]}")
    print("\n".join(table(r)))
    print(f"study: {out}")
    return 0 if r.get("status") == "ok" else 1

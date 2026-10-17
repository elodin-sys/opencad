"""python -m opencad.truth validate | run | score | status | restore | report | pin"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml

from opencad.io import sha256_file
from opencad.orchestrator import PipelineError
from opencad.paths import RESULTS, TRUTH, design_dir, part_dir, results_dir
from opencad.backends.base import EngineError
from opencad.backends.registry import current_id, get
from opencad.truth.manifest import CaseManifest, case_dir, load_manifest, load_registry, verify_pins


def cmd_validate() -> int:
    reg = load_registry()
    problems: list[str] = []
    for entry in reg.get("cases", []):
        cid = entry["id"]
        try:
            m = load_manifest(cid)
        except Exception as e:
            problems.append(f"{cid}: manifest invalid: {e}")
            continue
        if m.id != cid:
            problems.append(f"{cid}: manifest id {m.id!r} differs")
        mp = case_dir(cid) / "manifest.yaml"
        if entry.get("sha256") and sha256_file(mp) != entry["sha256"]:
            problems.append(f"{cid}: manifest sha256 differs from registry pin")
        problems += verify_pins(cid, m)
        # leakage: no truth file byte-identical inside any produced design/part
        for arm in m.arms:
            # a reference mesh that is deliberately both an arm input and a truth file is not a leak
            arm_inputs = {i.sha256 for i in m.inputs if i.path in arm.inputs}
            truth_hashes = {t.sha256 for t in m.truth} - arm_inputs
            input_names = {Path(p).name for p in arm.inputs}
            truth_names = {Path(t.path).name for t in m.truth} - input_names
            suffixes = get().language.suffixes
            for root in (design_dir(arm.design), part_dir(arm.design)):
                if root.exists():
                    for p in root.rglob("*"):
                        if p.is_file() and sha256_file(p) in truth_hashes:
                            problems.append(f"{cid}/{arm.id}: truth file leaked into {p}")
                    for src in root.rglob("*"):
                        if src.is_file() and src.suffix in suffixes:
                            text = src.read_text(encoding="utf-8", errors="replace")
                            # a truth name inside a longer input name (inputs/gear-train-pinion.step vs pinion.step) is not a reference
                            if "truth/" in text or any(re.search(rf"(?<![\w.-]){re.escape(n)}", text) for n in truth_names):
                                problems.append(f"{cid}/{arm.id}: {src} references a truth file")
        print(f"{cid}: class {m.truth_class} {m.role}; {len(m.inputs)} inputs, {len(m.truth)} truth files, {len(m.arms)} arm(s), {len(m.observables)} observables")
    if problems:
        print("problems:\n  - " + "\n  - ".join(problems))
        return 1
    print("truth corpus ok")
    return 0


def cmd_restore(case_id: str) -> int:
    """Move the vaulted case files back to the tree; refuse if truth/ is already present."""
    from opencad.truth.runner import SEQUESTERED, VAULT, _merge_back, vault_dirs

    case = case_dir(case_id)
    target = case / "truth"
    if target.exists():
        print(f"{target} already present; refuse to overwrite", file=sys.stderr)
        return 1
    held = vault_dirs(case_id)
    if not held:
        print(f"nothing in {VAULT} for {case_id}", file=sys.stderr)
        return 1
    vault = held[0]
    for name in SEQUESTERED:
        if (vault / name).exists():
            _merge_back(vault / name, case / name)
    for leftover in ("holders.json", "holders.lock"):
        (vault / leftover).unlink(missing_ok=True)
    if not any(vault.iterdir()):
        vault.rmdir()
    m = load_manifest(case_id)
    problems = verify_pins(case_id, m)
    if problems:
        print("restored but pins failed:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 1
    print(f"restored {target} from {vault}")
    return 0


def cmd_status() -> int:
    """Print live cases, latest scorecards, last attempt stage, and vault orphans."""
    from datetime import datetime, timezone

    from opencad.truth.runner import attempts_path, case_file

    missing = False
    for entry in load_registry().get("cases", []):
        cid = entry["id"]
        try:
            m = load_manifest(cid)
        except Exception as e:
            print(f"{cid}: MANIFEST INVALID {e}")
            missing = True
            continue
        truth_ok = (case_dir(cid) / "truth").exists()
        if not truth_ok:
            missing = True
        orphans = []
        from opencad.truth.runner import vault_dirs

        for p in vault_dirs(cid):
            mtime = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
            orphans.append(f"{p.name} ({mtime})")
        ap = attempts_path(cid)
        attempts = yaml.safe_load(ap.read_text()).get("attempts", []) if ap.exists() else []
        print(f"{cid}: truth={'ok' if truth_ok else 'MISSING'} class={m.truth_class} orphans={len(orphans)}")
        if orphans:
            for o in orphans:
                print(f"  vault {o}")
        from opencad.truth.runner import pending_attempts

        for pa in pending_attempts(m):
            flag = "--continue" if pa["kind"] == "run" else "--continue (ecr)"
            print(f"  PENDING worker turn for arm {pa['arm']} at {pa['point']} (order {pa['order']}); finish it, then `python -m opencad.truth {'run' if pa['kind'] == 'run' else 'ecr'} {cid} --arm {pa['arm']} {flag.split()[0]}`")
        for arm in m.arms:
            published = (design_dir(arm.design) / ("assembly.yaml" if getattr(m, "kind", "part") == "machine" else "contract.yaml")).exists()
            kcl = (part_dir(arm.design) / get().language.entry).exists()
            latest_p = case_file(cid, "scorecards") / f"{arm.id}@{current_id()}-latest.json"
            if latest_p.exists():
                card = json.loads(latest_p.read_text())
                verdict = f"{card.get('verdict')} {card.get('scored_at', '')}"
            else:
                verdict = "not scored"
            arm_attempts = [a for a in attempts if a.get("arm") == arm.id]
            last_stage = arm_attempts[-1].get("stage_reached") if arm_attempts else "-"
            print(f"  arm {arm.id}: design={'published' if published else 'absent'} kcl={'yes' if kcl else 'no'} latest={verdict} last_stage={last_stage}")
    be = current_id()
    tasks = sorted((TRUTH / "cases").glob("*/task.yaml"))
    if tasks:
        print("assembly tasks:")
        for tp in tasks:
            cid = tp.parent.name
            card_p = tp.parent / "scorecards" / f"assembly@{be}-latest.json"
            if not card_p.exists():
                card_p = tp.parent / "scorecards" / "assembly-latest.json"
            if card_p.exists():
                card = json.loads(card_p.read_text())
                print(f"  {cid}: {card.get('verdict')} mode={card.get('mode', 'placement')} {card.get('scored_at', '')}")
            else:
                print(f"  {cid}: not scored")
    return 1 if missing else 0


def cmd_pin(case_id: str, allow_invalid: bool = False) -> int:
    """Fill sha256 pins for inputs/truth in a manifest and the registry entry (run once when adding files). Every pinned STEP must
    qualify as valid, closed, positively oriented solids (scripts/qualify_inputs.py repairs what it can)."""
    from opencad.geomcheck import brep
    from opencad.geomcheck.qualify import qualify

    mp = case_dir(case_id) / "manifest.yaml"
    data = yaml.safe_load(mp.read_text())
    bad = []
    for rel in dict.fromkeys(f["path"] for g in ("inputs", "truth") for f in data.get(g, []) if f["path"].lower().endswith((".step", ".stp"))):
        q = qualify(brep.read_step(case_dir(case_id) / rel))
        if not q["ok"]:
            bad.append(f"{rel}: {'; '.join(q['problems'])}")
    if bad:
        print("unqualified CAD:\n  " + "\n  ".join(bad) + f"\nrepair: .venv/bin/python scripts/qualify_inputs.py {case_id} --repair --write", file=sys.stderr)
        if not allow_invalid:
            return 2
    for group in ("inputs", "truth"):
        for f in data.get(group, []):
            f["sha256"] = sha256_file(case_dir(case_id) / f["path"])
    mp.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
    CaseManifest.model_validate(data)
    reg_path = TRUTH / "registry.yaml"
    reg = load_registry()
    cases = [c for c in reg.get("cases", []) if c["id"] != case_id]
    cases.append({"id": case_id, "manifest": f"cases/{case_id}/manifest.yaml", "sha256": sha256_file(mp)})
    reg["cases"] = sorted(cases, key=lambda c: c["id"])
    reg_path.write_text(yaml.safe_dump(reg, sort_keys=False), encoding="utf-8")
    print(f"pinned {case_id}: {len(data.get('inputs', []))} inputs, {len(data.get('truth', []))} truth files")
    return 0


def _carry(a: argparse.Namespace) -> str:
    """The flags a continued attempt keeps: its telemetry tag and the wait mode."""
    return ((f" --tag {a.tag}" if getattr(a, "tag", None) else "") + (" --wait" if getattr(a, "wait", False) else "")
            + (" --enforce-budgets" if getattr(a, "enforce_budgets", False) else ""))


def _add_backend(p: argparse.ArgumentParser) -> None:
    p.add_argument("--backend", default=None, help="modelling backend (default OPENCAD_BACKEND or build123d)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="opencad.truth", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    _add_backend(sub.add_parser("validate"))
    p = sub.add_parser("run", help="live case attempt (exit 75 = a worker turn is pending; finish it and re-run with --continue)")
    p.add_argument("case")
    p.add_argument("--arm", help="arm id (default: every arm in order)")
    p.add_argument("--force", action="store_true", help="delete designs/parts/results of the arm and redo")
    p.add_argument("--amend", help="machine cases: a markdown file (or text) of evaluator evidence for an engineering change on the published assembly "
                                   "contract; the drafter revises it under sequestration, then the machine is re-placed and re-evaluated")
    p.add_argument("--timeout", type=float, default=None, help="cap on each worker turn budget (default: the role profile)")
    p.add_argument("--stop-after", choices=["draft", "blockout"], help="stop early (debugging the initializer)")
    p.add_argument("--no-retry", action="store_true", help="score the modelled part without the bounded worker retry")
    p.add_argument("--resume-from", choices=["publish", "blockout", "pipeline", "retry"], help="restart an attempt from a checkpoint: publish a staging bundle, or keep a published design (blockout) / passed blockout (pipeline) / modelled part (retry: re-verify, gates, bounded retry)")
    p.add_argument("--continue", dest="cont", action="store_true", help="continue the attempt a worker handback interrupted (truth stays vaulted until it is scored)")
    p.add_argument("--worker", choices=["cursor", "codex"], help="worker backend (default OPENCAD_WORKER or cursor)")
    p.add_argument("--decompose", dest="decompose", action="store_const", const=True, default=None, help="model through partition -> parallel modules -> integrate (automatic after a kernel/incomplete stuck attempt or for large contracts)")
    p.add_argument("--no-decompose", dest="decompose", action="store_const", const=False)
    p.add_argument("--parallel", action="store_true", help="this case runs beside others: per-design engine lock")
    p.add_argument("--tag", help="label every telemetry row of this run (A/B)")
    p.add_argument("--wait", action="store_true", help="after a NEXT line keep running: poll the orders' done files every 5 s and continue by itself")
    p.add_argument("--enforce-budgets", action="store_true", help="with --wait: a turn past 1.5x its budget is taken at its executing deliverable or checkpoint")
    _add_backend(p)
    from opencad.truth.regress import ASSEMBLY_BACKENDS, ASSEMBLY_SUITE, DEFAULT_BACKENDS, DEFAULT_CASES

    p = sub.add_parser("regress", help="regression session: draft each case once, then run every case x backend in parallel; EVENT#k lines for the orchestrator")
    p.add_argument("--suite", choices=["parts", "assembly"], default="parts", help="assembly: the passing machine cases on the assembly backends")
    p.add_argument("--cases", help=f"comma-separated cases (parts default {','.join(DEFAULT_CASES)}; assembly default {','.join(ASSEMBLY_SUITE)})")
    p.add_argument("--arm", default="spec-and-views", help="part cases' arm; a machine case not naming it runs its first arm")
    p.add_argument("--backends", help=f"the first one also runs the drafts (parts default {','.join(DEFAULT_BACKENDS)}; assembly default {','.join(ASSEMBLY_BACKENDS)})")
    p.add_argument("--jobs", type=int, default=None, help="concurrent children (default: cores - 2, capped by how many engine budgets fit in memory)")
    p.add_argument("--tag", help="label every telemetry row; logs go to results/_logs/<tag>/ (required unless --check)")
    p.add_argument("--reuse-designs", action="store_true", help="skip the draft of a case whose design is already published")
    p.add_argument("--check", action="store_true", help="run the preflight only (pending orders, vaulted truth, engines, power, overrides)")
    p = sub.add_parser("score")
    p.add_argument("case")
    p.add_argument("--arm")
    _add_backend(p)
    _add_backend(sub.add_parser("report"))
    _add_backend(sub.add_parser("status", help="live cases, latest verdicts, pending worker turns, and vault orphans"))
    p = sub.add_parser("pin")
    p.add_argument("case")
    p.add_argument("--allow-invalid", action="store_true", help="pin even if a STEP fails qualification (recorded on stderr)")
    _add_backend(p)
    p = sub.add_parser("restore", help="bring sequestered truth back from the vault after an interrupted run")
    p.add_argument("case")
    _add_backend(p)
    p = sub.add_parser("ecr", help="change-request case (arm with `ecr:`): sequester, `opencad ecr` on the base design with inputs/contract-delta.yaml, restore the base KCL, score")
    p.add_argument("case")
    p.add_argument("--arm")
    p.add_argument("--timeout", type=float, default=None, help="cap on each worker turn budget (default: the role profile)")
    p.add_argument("--expect-infeasible", action="store_true", help="the request must be refused; no scorecard")
    p.add_argument("--keep-kcl", action="store_true", help="leave the changed part in place instead of restoring the base design")
    p.add_argument("--continue", dest="cont", action="store_true", help="continue the request a worker handback interrupted")
    p.add_argument("--worker", choices=["cursor", "codex"])
    p.add_argument("--tag", help="label every telemetry row of this run (A/B)")
    p.add_argument("--wait", action="store_true", help="after a NEXT line keep running: poll the orders' done files every 5 s and continue by itself")
    p.add_argument("--enforce-budgets", action="store_true", help="with --wait: a turn past 1.5x its budget is taken at its executing deliverable or checkpoint")
    _add_backend(p)
    p = sub.add_parser("assembly-check", help="local critic for an assembly work dir: the evaluator's axis/offset/flip/interference numbers from assembly.yaml + joint-task.json, no truth")
    p.add_argument("work", help="results/<case>/work (holds joint-task.json, the STEP bodies and assembly.yaml)")
    p.add_argument("--manifest", help="an assembly.yaml elsewhere (default <work>/assembly.yaml)")
    p.add_argument("--entry", help="modelled mode: parts/<backend>/<case>/main.py; export through the engine and derive yaml from placements")
    p.add_argument("--ledger", help="engine ledger JSONL (the work order's engine-ledger.jsonl)")
    p.add_argument("--json", action="store_true")
    _add_backend(p)
    p = sub.add_parser("assemble", help="held-out assembly task (truth/cases/<case>/task.yaml): the worker places two STEP bodies, the joint is scored")
    p.add_argument("case")
    p.add_argument("--force", action="store_true", help="delete results/<case> and redo the attempt")
    p.add_argument("--timeout", type=float, default=None, help="cap on the worker turn budget (default: the role profile)")
    p.add_argument("--continue", dest="cont", action="store_true", help="continue the attempt a worker handback interrupted")
    p.add_argument("--worker", choices=["cursor", "codex"])
    p.add_argument("--mode", choices=["placement", "modelled"], default=None, help="placement: yaml only (zoo default). modelled: backend imports STEPs (local default)")
    p.add_argument("--parallel", action="store_true", help="this case runs beside others: per-design engine lock")
    p.add_argument("--tag", help="label every telemetry row of this run")
    _add_backend(p)
    p = sub.add_parser("parity", help="evaluator-side audit: truth observables vs the worker-visible contract (missing / looser / different params), plus scorecard-PASS-gates-FAIL cells; writes results/_bakeoff/parity/<case>.md")
    p.add_argument("case")
    p.add_argument("--out", help="report path (default results/_bakeoff/parity/<case>.md)")
    p.add_argument("--corpus", action="store_true", help="list scorecard/gate mismatches for every case, not only this one")
    _add_backend(p)
    p = sub.add_parser("mutate", help="score deliberately bad parts (truth/cases/<case>/mutants.yaml); every mutant must FAIL")
    p.add_argument("case")
    p.add_argument("--arm")
    p.add_argument("--mutant", help="mutant id (default: all)")
    p.add_argument("--source", default="candidate", help="candidate (handoff STEP), truth (truth STEP), or a path")
    p.add_argument("--op", help="ad-hoc mutant op instead of mutants.yaml")
    p.add_argument("--params", default="{}", help="JSON kwargs for --op")
    _add_backend(p)
    a = ap.parse_args(argv)
    if getattr(a, "backend", None):
        from opencad.backends.registry import set_backend

        set_backend(a.backend)

    if a.cmd == "validate":
        return cmd_validate()
    if a.cmd == "restore":
        return cmd_restore(a.case)
    if a.cmd == "status":
        return cmd_status()
    if a.cmd == "pin":
        return cmd_pin(a.case, a.allow_invalid)
    if a.cmd == "report":
        from opencad.truth.report import build

        print(build())
        return 0
    if a.cmd == "parity":
        from opencad.truth import parity

        out, findings, mismatches = parity.run(a.case, out=Path(a.out) if a.out else None, corpus_mismatches=a.corpus)
        print(parity.format_summary(findings, mismatches))
        print(out)
        return 0
    if a.cmd == "regress":
        from opencad.truth import regress

        asm = a.suite == "assembly"
        cases = (a.cases or ",".join(ASSEMBLY_SUITE if asm else DEFAULT_CASES)).split(",")
        backends = (a.backends or ",".join(ASSEMBLY_BACKENDS if asm else DEFAULT_BACKENDS)).split(",")
        if a.check:
            return 0 if regress.preflight_ok(cases, backends) else 2
        if not a.tag:
            print("error: --tag is required", file=sys.stderr)
            return 2
        from opencad import resources

        jobs = a.jobs or resources.pool_workers(max(1, (os.cpu_count() or 4) - 2))
        return regress.run(cases, a.arm, backends, jobs=jobs, tag=a.tag, reuse_designs=a.reuse_designs)
    from opencad import worker
    from opencad.worker import EXIT_WORKER_PENDING, WorkerPending, orders

    if getattr(a, "worker", None):
        worker.set_backend(a.worker)
    if getattr(a, "tag", None):
        os.environ["OPENCAD_TAG"] = a.tag
    if getattr(a, "parallel", False):
        os.environ.setdefault("OPENCAD_ZOO_LOCK", str(Path.home() / ".cache" / "opencad" / f"zoo-{a.case}.lock"))
    if a.cmd == "assembly-check":
        from opencad.truth.assembly_check import main as check_main

        return check_main(
            Path(a.work),
            Path(a.manifest) if a.manifest else None,
            as_json=a.json,
            entry=Path(a.entry) if getattr(a, "entry", None) else None,
            backend=getattr(a, "backend", None),
            ledger=Path(a.ledger) if getattr(a, "ledger", None) else None,
        )
    if a.cmd == "assemble":
        from opencad.truth.assemble import default_mode, run_assembly

        mode = a.mode or default_mode()
        be = current_id()
        cont = f"python -m opencad.truth assemble {a.case} --continue --backend {be} --mode {mode}"
        if getattr(a, "tag", None):
            cont += f" --tag {a.tag}"
        if getattr(a, "parallel", False):
            cont += " --parallel"
        worker.set_continue_cmd(cont)
        try:
            card = run_assembly(a.case, force=a.force, timeout=a.timeout, cont=a.cont, mode=mode)
        except WorkerPending as wp:
            for o in wp.orders:
                print(orders.next_line(o), flush=True)
            return EXIT_WORKER_PENDING
        except PipelineError as e:
            print(f"error: {e}")
            return 2
        return 0 if card.get("ok") else 1
    from opencad.truth.runner import case_lock, live_holders, vault_dirs

    with case_lock(a.case):
        m = load_manifest(a.case) if (case_dir(a.case) / "manifest.yaml").exists() else None
        # a vaulted manifest serves --continue, or a run beside a live holder of the case (another backend's run)
        vaults = [p for p in vault_dirs(a.case) if (p / "manifest.yaml").exists()]
        joins = a.cmd in ("run", "ecr") and (getattr(a, "cont", False) or bool(live_holders(a.case)))
        if m is None and vaults and joins:
            m = CaseManifest.model_validate(yaml.safe_load((vaults[-1] / "manifest.yaml").read_text(encoding="utf-8")))
    if m is None:
        print(f"error: {a.case} has no manifest.yaml in the tree (sequestered by an interrupted run?); use --continue or `truth restore {a.case}`", file=sys.stderr)
        return 2
    arms = [x.id for x in m.arms] if not a.arm else [a.arm]
    if m.kind == "machine" and a.cmd in ("run", "score"):
        from opencad.truth.machine import run_machine, score_machine

        code = 0
        for arm in arms:
            worker.set_continue_cmd(f"python -m opencad.truth run {a.case} --arm {arm} --backend {current_id()} --continue" + _carry(a))
            if a.cmd == "score":
                card = score_machine(a.case, m, arm)
                verdict = card["verdict"]
                print(f"{a.case}/{arm}: {verdict} geometry {card['summary']['required_pass']}/{card['summary']['required_total']}, performance "
                      f"{card['summary']['performance_pass']}/{card['summary']['performance_scored']} scored of {card['summary']['performance_total']} "
                      f"({card['summary']['performance_unresolved']} unresolved); by split {card['summary']['performance_by_split']}")
                for c in card["checks"] + card["performance"]:
                    print(f"  {'PASS' if c.get('ok') else ('n/a ' if c.get('ok') is None else 'FAIL')} {c['id']} ({c['kind']}) "
                          + json.dumps({k: c.get(k) for k in ('measured', 'expected', 'prediction', 'reference', 'z', 'status') if c.get(k) is not None}, default=str)[:220])
            else:
                note = getattr(a, "amend", None)
                if note and Path(note).is_file():
                    note = Path(note).read_text(encoding="utf-8")
                verdict = run_machine(a.case, m, arm, force=a.force, cont=a.cont, allow_retry=not a.no_retry, amend=note)["scorecard"]["verdict"]
            code = code or (0 if verdict == "PASS" else 1)
        return code
    if a.cmd == "run":
        from opencad.truth.runner import run_case

        code = 0
        for arm in arms:
            worker.set_continue_cmd(f"python -m opencad.truth run {a.case} --arm {arm} --backend {current_id()} --continue" + _carry(a))
            cont = a.cont
            while True:
                try:
                    entry = run_case(a.case, m, arm, force=a.force, timeout=a.timeout, stop_after=a.stop_after, resume_from=a.resume_from, allow_retry=not a.no_retry,
                                     cont=cont, decompose=a.decompose)
                except (PipelineError, EngineError) as e:
                    print(f"error: {e}", file=sys.stderr)
                    return 2
                if not (entry.get("pending") and a.wait):
                    break
                orders.wait(results_dir(next(x.design for x in m.arms if x.id == arm)), enforce=orders.executes if a.enforce_budgets else None)
                cont = True
            if entry.get("pending"):
                return EXIT_WORKER_PENDING
            print(json.dumps(entry, indent=2, default=str))
            stop = {"draft": "published", "blockout": "blockout"}.get(a.stop_after or "")
            if not (entry.get("stage_reached") == stop if stop else entry.get("scorecard", {}).get("verdict") == "PASS"):
                code = 1
        return code
    if a.cmd == "ecr":
        from opencad.truth.runner import run_ecr

        code = 0
        for arm in arms:
            worker.set_continue_cmd(f"python -m opencad.truth ecr {a.case} --arm {arm} --backend {current_id()}" + (" --expect-infeasible" if a.expect_infeasible else "") + " --continue"
                                    + _carry(a))
            cont = a.cont
            while True:
                try:
                    entry = run_ecr(a.case, m, arm, timeout=a.timeout, expect_infeasible=a.expect_infeasible, keep_kcl=a.keep_kcl, cont=cont)
                except (PipelineError, EngineError) as e:
                    print(f"error: {e}", file=sys.stderr)
                    return 2
                if not (entry.get("pending") and a.wait):
                    break
                orders.wait(results_dir(next(x.design for x in m.arms if x.id == arm)), enforce=orders.executes if a.enforce_budgets else None)
                cont = True
            if entry.get("pending"):
                return EXIT_WORKER_PENDING
            print(json.dumps(entry, indent=2, default=str))
            ok = (entry.get("ecr") or {}).get("refused") if a.expect_infeasible else entry.get("scorecard", {}).get("verdict") == "PASS"
            if not ok:
                code = 1
        return code
    if a.cmd == "mutate":
        from opencad.io import dump_json
        from opencad.truth.mutants import load_mutants, run_mutant

        specs = [{"id": a.op, "op": a.op, **json.loads(a.params)}] if a.op else load_mutants(a.case)
        if a.mutant:
            specs = [s for s in specs if s.get("id") == a.mutant]
        if not specs:
            print(f"no mutants for {a.case}", file=sys.stderr)
            return 2
        code = 0
        for arm in arms:
            rows = []
            for spec in specs:
                r = run_mutant(a.case, m, arm, spec, source=a.source)
                rows.append(r)
                base = r.get("baseline", {}).get("verdict", "-")
                mark = "caught" if r.get("ok") else "MISSED"
                print(f"{a.case}/{arm} mutant {r['id']}: {mark} (verdict {r['verdict']}, baseline {base}) by {r.get('caught_by') or r.get('error')}")
                if not r.get("ok"):
                    code = 1
            dump_json(RESULTS / "_mutants" / a.case / arm / "summary.json", {"case": a.case, "arm": arm, "mutants": [{k: v for k, v in r.items() if k != "checks"} for r in rows]})
        return code
    if a.cmd == "score":
        import time

        from opencad.truth.runner import log_score
        from opencad.truth.scorer import score_case

        code = 0
        for arm in arms:
            t0 = time.time()
            card = score_case(a.case, m, arm)
            log_score(a.case, arm, card, seconds=time.time() - t0)
            print(f"{a.case}/{arm}: {card['verdict']} required {card['summary']['required_pass']}/{card['summary']['required_total']}")
            for c in card["checks"]:
                print(f"  {'PASS' if c.get('ok') else 'FAIL'} {c['id']} ({c['kind']}): measured={json.dumps(c.get('measured', c.get('found')), default=str)[:160]} expected={json.dumps(c.get('expected', c.get('checks')), default=str)[:160]}" + (f" error={c['error']}" if c.get('error') else ""))
            if card["verdict"] != "PASS":
                code = 1
        return code
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

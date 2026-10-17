#!/usr/bin/env python
"""Clone a truth case into a change-request (ECR) case: same observables with the request's revisions applied.

  python scripts/derive_ecr_case.py voron-sb-duct ecr1 truth/cases/voron-sb-duct/inputs/ecr/ecr-1-screw-holes.md \
      --title "Ø3.4 screw holes lowered 3 mm" \
      --set 'hole_d3p4_m16p2_m3p7_19p3.point[2]=16.301' --set 'hole_d3p4_16p3_m3p7_19p3.point[2]=16.301' \
      --drop volume --drop center_of_mass --drop deviation
  python -m opencad.truth pin voron-sb-duct-ecr1

The new case `<base>-<label>` is class C (the reference CAD is the pre-change part, so mesh-derived
observables are dropped unless `--copy-truth`), and its single arm points at the base design with
`ecr: <label>`, so `python -m opencad.truth score <base>-<label>` reads
results/<design>/ecr/<label>/handoff/. `--set` takes `<observable id>.<field>[<index>]=<yaml value>`.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
CASES = REPO / "truth" / "cases"

SET_RE = re.compile(r"^(?P<id>[A-Za-z0-9_\-]+)\.(?P<field>[A-Za-z_]+)(?:\[(?P<idx>\d+)\])?=(?P<value>.*)$")


def apply_set(obs: list[dict], spec: str) -> None:
    m = SET_RE.match(spec)
    if not m:
        raise SystemExit(f"bad --set {spec!r}; want '<id>.<field>[<index>]=<value>'")
    o = next((x for x in obs if x["id"] == m["id"]), None)
    if o is None:
        raise SystemExit(f"--set {spec!r}: no observable {m['id']!r}")
    value = yaml.safe_load(m["value"])
    if m["idx"] is not None:
        o[m["field"]][int(m["idx"])] = value
    else:
        o[m["field"]] = value


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base")
    ap.add_argument("label")
    ap.add_argument("request", type=Path, help="markdown change request; copied into the case's inputs/")
    ap.add_argument("--title", required=True)
    ap.add_argument("--set", action="append", default=[], help="observable field override")
    ap.add_argument("--drop", action="append", default=[], help="observable id to leave out")
    ap.add_argument("--copy-truth", action="store_true", help="copy the base truth files (keeps mesh-derived observables)")
    a = ap.parse_args(argv)

    base_dir = CASES / a.base
    base = yaml.safe_load((base_dir / "manifest.yaml").read_text())
    case_id = f"{a.base}-{a.label}"
    case = CASES / case_id
    (case / "inputs").mkdir(parents=True, exist_ok=True)
    (case / "truth").mkdir(exist_ok=True)
    shutil.copy2(a.request, case / "inputs" / a.request.name)

    obs = [dict(o) for o in base["observables"] if o["id"] not in a.drop]
    if not a.copy_truth:
        obs = [o for o in obs if not o.get("from") and not str(o.get("reference", "")).startswith("truth/")]
    for spec in a.set:
        apply_set(obs, spec)

    truth: list[dict] = []
    if a.copy_truth:
        for t in base["truth"]:
            shutil.copy2(base_dir / t["path"], case / t["path"])
            truth.append({**t, "sha256": "PIN"})
    (case / "truth" / "revisions.yaml").write_text(yaml.safe_dump({"base": a.base, "label": a.label, "title": a.title, "set": a.set, "drop": a.drop}, sort_keys=False), encoding="utf-8")
    truth.append({"path": "truth/revisions.yaml", "kind": "yaml", "sha256": "PIN", "note": "the observable revisions the request implies (evaluator-side)"})

    arm = base["arms"][0]
    m = {
        "id": case_id,
        "title": f"{base['title'].split(':')[0]} after {a.label.upper()}: {a.title}",
        "truth_class": "C", "role": base.get("role", "validation"), "source": base["source"],
        "intent": f"Score the design after change request {a.label.upper()} ({a.title}): the revised observables apply and every other observable is unchanged.",
        "inputs": [{"path": f"inputs/{a.request.name}", "kind": "text", "sha256": "PIN", "note": "the change request"}],
        "truth": truth,
        **({"hardware": base["hardware"]} if base.get("hardware") else {}),
        "arms": [{"id": a.label, "design": arm["design"], "ecr": a.label, "inputs": [f"inputs/{a.request.name}"], "images": [],
                  "notes": f"Scored with `python -m opencad.truth score {case_id}` after `python -m opencad ecr {arm['design']} <request> --contract-delta <yaml> --label {a.label}`; not a drafting run."}],
        "observables": obs,
        "notes": [f"Class C change-request case cloned from {a.base}: its checks with the request's revisions applied."],
    }
    (case / "manifest.yaml").write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
    print(f"wrote {case / 'manifest.yaml'} with {len(obs)} observables ({len(a.set)} revised, {len(a.drop)} dropped)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

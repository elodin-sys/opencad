"""Qualify a truth case's pinned CAD (evaluator side): every STEP under the manifest's `inputs:` and `truth:` must be valid,
closed, positively oriented solids. `--repair` tries ShapeFix, a sewing sweep and orientation; `--write` replaces the file with the
repaired solid and records before/after in the case's `qualification.yaml` (then re-run `truth pin <case>`).

    .venv/bin/python scripts/qualify_inputs.py <case> [--repair [--write]]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

CAD_SUFFIXES = (".step", ".stp")


def cad_files(case: Path) -> list[str]:
    data = yaml.safe_load((case / "manifest.yaml").read_text(encoding="utf-8"))
    paths = [f["path"] for g in ("inputs", "truth") for f in data.get(g) or [] if f.get("kind") == "cad" or f["path"].lower().endswith(CAD_SUFFIXES)]
    return list(dict.fromkeys(p for p in paths if p.lower().endswith(CAD_SUFFIXES)))


def main(argv: list[str] | None = None) -> int:
    from opencad.backends.local import write_step
    from opencad.geomcheck import brep
    from opencad.geomcheck.qualify import qualify, repair
    from opencad.io import sha256_file, utc_now
    from opencad.truth.manifest import case_dir

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("case")
    p.add_argument("--repair", action="store_true")
    p.add_argument("--write", action="store_true", help="with --repair: overwrite each repaired file and record it")
    a = p.parse_args(argv)
    case = case_dir(a.case)
    record_path = case / "qualification.yaml"
    record = yaml.safe_load(record_path.read_text(encoding="utf-8")) if record_path.exists() else {}
    bad = 0
    for rel in cad_files(case):
        path = case / rel
        shape = brep.read_step(path)
        q = qualify(shape)
        line = f"{'ok  ' if q['ok'] else 'FAIL'} {rel}: {q['solids']} solids, {q['faces']} faces, free edges {q['free_edges']}, volumes {[round(v, 3) for v in q['volumes']]}"
        print(line + ("" if q["ok"] else f" ({'; '.join(q['problems'])})"), flush=True)
        if q["ok"] or not a.repair:
            bad += not q["ok"]
            continue
        fixed, rec = repair(shape)
        after = rec["after"]
        print(f"     repair {'ok' if rec['ok'] else 'FAILED'}: {', '.join(rec['steps']) or 'nothing applied'}; now {after['solids']} solids, "
              f"free edges {after['free_edges']}, volumes {[round(v, 3) for v in after['volumes']]}" + ("" if rec["ok"] else f" ({'; '.join(after['problems'])})"), flush=True)
        bad += not rec["ok"]
        if rec["ok"] and a.write:
            before_sha = sha256_file(path)
            write_step(fixed, path, path.stem)
            back = qualify(brep.read_step(path))
            if not back["ok"]:
                print(f"     the written STEP does not qualify: {'; '.join(back['problems'])}", flush=True)
                bad += 1
            record[rel] = {"repaired": utc_now(), "steps": rec["steps"], "sha256_before": before_sha, "sha256_after": sha256_file(path),
                           "before": {k: rec["before"][k] for k in ("solids", "faces", "free_edges", "volumes", "problems")},
                           "after": {k: after[k] for k in ("solids", "faces", "free_edges", "volumes")}}
    if a.write and record:
        record_path.write_text(yaml.safe_dump(record, sort_keys=False, width=120), encoding="utf-8")
        print(f"recorded {record_path}; re-pin with: python -m opencad.truth pin {a.case}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

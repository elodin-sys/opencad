---
name: cad-qa
description: Gate-by-gate review checklist for a opencad part after /create-cad. Re-reads every gate from its evidence path, recomputes a headline value independently, inspects the renders, and produces a verdict with evidence. Use after a pipeline run or when asked to review results/<part>.
---

# CAD QA review

`ok: true` in any stage JSON is a claim. The verdict comes from evidence paths.

## 1. Load the evidence

Paths below are for a standalone part; a part of an assembly is at `results/<backend>/<asm>/parts/<leaf>/` and
`designs/<asm>/parts/<leaf>/` (design `<asm>-<leaf>`).

```bash
python - <<'EOF'
import json, sys
fb = json.load(open("results/<backend>/<part>/gate_feedback.json"))
for g in fb["gates"]:
    print(g["tier"], "PASS" if g["ok"] else "n/a" if g["ok"] is None else "FAIL", g["id"], "|", "; ".join(g["evidence"]))
print(fb["summary"], "retry:", fb.get("retry"))
EOF
```

Open `results/<part>/inspect.json`, `verify.json`, `export.json`, `edit.json` and check
that each value quoted in a gate's evidence actually appears there.

## 2. Gate walk (tiers)

Tier A — design/interpretation (fix the contract or the model):

1. `contract_provenance`: how many values are `inferred`/`defaulted`? Are the open
   questions geometric? If so the part is not yet specified.
2. `envelope`: `inspect.bbox` (STEP, OpenCascade) is the verdict. `verify.bbox` (KCL
   engine) is supporting evidence and is not required when the engine is missing. A
   pass on one and not the other (when both exist) is an exchange problem, not a
   design pass.
3. `mass_properties`: volume/area/COM errors versus band; note the analytic formula the
   contract used and confirm it is right for the geometry.
4. `features`: every required feature has at least one probe; look at what each probe
   actually tested (void/solid points, section loops and holes, named faces, cylinder
   axes with their offsets in mm, inclined planes, dimensions). Multi-body and interior
   checks live under the same gate (`inspect.json` solids, clearances, passages,
   thickness, probes, cylinder_counts, gears, meshes): a thickness `p05` at exactly the
   minimum and a passage that "reaches the exterior" are the two results worth reading
   twice.
5. `reference_fidelity`: when a reference exists, read p95, Hausdorff, silhouette IoU,
   `inspect.json deviation.bands` (ten signed bands along the longest axis) and `.worst`;
   view `deviation-map.png` and compare `designs/<part>/reference/silhouette-*.png` with the snapshots.

Tier B — model consistency (reconcile before trusting):

6. `export_agreement`: KCL vs STEP vs STL volumes; tessellation explains only the STL.
   A fail while the engine responded (`engine_class == "ok"`) is model-attributable
   and gets one bounded KCL retry (then re-export / re-measure).
7. `edit_robustness`: each edit test's expected vs measured delta; the sweep count
   (every declared value must rebuild with interfaces preserved); infeasible deltas
   refused by an assert (a silent build is a fail); the restore hash. For a change
   request (`results/<part>/ecr/<label>/`), also read `ecr.json .preservation`: every
   `must_not_change` interface item not named by the request must sit at its baseline.
8. `source_hygiene`: KCL 2, mm, formatted, lint-clean, named constants, asserts.

Tier C — artifact truth (never repaired in place):

9. `export_integrity`: deterministic STEP, valid B-rep, solid count, watertight STL.
   An open mesh with a valid STEP of the right solid count is model-attributable and
   gets the same one KCL retry; the STL/STEP files themselves are not patched.
10. `traceability`: every stage JSON present, one zoo version, git head, worker thread/agent ids,
    engine calls, no `--allow-errors`.
11. `evidence_separation`: contract agreement, reference agreement, physical validation
    reported separately; the report must not call a CAD match "validated".
12. `independence`: no import of reference geometry; sketch blocks and features present.

## 3. Recompute one headline value

Pick the volume or a section area and recompute it by hand from the contract parameters
(e.g. `w*h*t - n*pi*(d/2)^2*t`). It must match `inspect.json .volume.measured` within
the contract band. If the analytic value and the STEP disagree while the gate passed, the
contract expectation is wrong: report it.

## 4. Look

Open `results/<backend>/<part>/snapshots/view-all.png` and `view-symmetry.png` (and the
contact sheet). Check each quarter and the underside for steps, folds, slivers; compare
left/right. Numbers cannot catch a folded hull or a mirrored hole pattern that preserves
volume; the picture can. When the design has input renders, open `snapshots/view-compare.png`
(input render beside the part, same view) and name every difference: missing bells, tapers,
bosses, openings; `verify.json snapshots.reference_silhouette` gives a framing-normalized IoU
per view (evidence, not a gate; below ~0.9 on an orthographic view means a visible shape miss). For a `correct` turn compare with the previous sheet and
`correct.json` `delta_vs_previous` (p95, max, changed-region bbox, area per side).
`model.json` `visual_check` should quote the worker's `Visual:` line; "missing" is a
disclosure, not a gate.

For an assembly attempt (`results/<case>/scorecard.json` with `viz`), open
`results/<case>/handoff/assembly.html` (serve the directory with `python3 -m http.server` so
the GLB loads): body one (red) must move about the green joint axis the way the joint type
says (a revolute turns, a slider slides) and stay in contact with body two (blue). The grey
`ghost:` node is a second copy of body one in the dataset pose — not a rendering artifact.
In the HTML viewer it is off by default; check "show dataset pose" to compare. A raw GLB
preview always shows it.

## 5. Verdict

Write: PASS or FAIL; each failed gate with evidence path + key + value; the recomputed
headline value; visual findings; worker open questions from `model.json`; the engine call
total and thread ids. A PASS means the KCL, its exports, and the contract agree (and the
reference band is met when a reference exists). It is not engineering validation, not
manufacturability, not physical inspection.

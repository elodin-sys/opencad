---
name: initialize-cad
description: Bootstraps a reviewable opencad part or machine from an intent, requirement documents, drawings or images, coordinate tables, and optionally a reference triangle mesh. It states whether the goal is one part or an assembly, drafts the contract (for a machine, the assembly contract and one part contract per design), and runs the bounded envelope-only blockout checkpoint for every part. Use only when explicitly invoked as /initialize-cad.
disable-model-invocation: true
---

# Initialize a CAD part or machine

Interpret the invocation as:

```text
/initialize-cad <name> "<intent>" @requirement-docs @drawings-or-images @coordinate-tables @reference-mesh [--kind part|assembly]
```

Sections 1 to 7 initialize a part; section 8 initializes a machine. Decide which first (section 0).

## 0. Part or assembly

Decide the goal from the intent and the sources before staging anything:

- **assembly** when they describe two or more bodies that move relative to each other (joints, gears, a linkage, a rotor in a
  housing), a fluid region, operating conditions (a speed, a flow), or a performance prediction (pressure rise, torque, a
  temperature);
- **part** otherwise, including one design exported as several fixed solids (a two-piece enclosure) and a single part that only
  mates with purchased hardware.

`--kind part|assembly` overrides the decision. State it before anything else, with the phrase that decided it, for example
`Goal: assembly ("a 4-blade impeller on the motor shaft inside the housing ... pressure rise at 1500 rpm")`, so the user can
correct it before any worker turn runs. A part continues with section 1, an assembly with section 8.

For a part, produce `designs/<part>/` (contract.yaml, brief.md, sources/, optional reference/) and the
blockout checkpoint in `results/<backend>/<part>/blockout/`. An assembly's parts publish under it instead:
`designs/<asm>/parts/<leaf>/` and `results/<backend>/<asm>/parts/<leaf>/` for design `<asm>-<leaf>`. Honour `--backend` /
`OPENCAD_BACKEND`. Never run `python -m opencad run` here; the only worker turns
authorised are source interpretation, the contract draft, and the blockout. Cursor never
models or measures geometry itself (AGENTS.md): images, drawings and dimension placement
are worker turns; meshes and tables go through the deterministic ingest commands.

Environment: `source .venv/bin/activate` from the repository root (create it with
`scripts/setup_env.sh`). `python -m opencad preflight --backend <id>` must pass; a
preflight failure stops the run. Zoo login is only required for `--backend zoo` (account
exhausted — prefer a local backend). `codex --version` only when `--worker codex` is used.

## 1. Resolve and guard

1. Require a part name and a non-empty intent. Accept `<part>` or `designs/<part>`.
2. Names follow `opencad.paths.check_part_name`: letters, digits, `.`, `_`, `-`; no
   leading `_` or `.`; max 64 characters.
3. Refuse if `designs/<part>` exists (offer a new name; never merge or replace) or if
   `results/<part>` exists (stale artifacts would masquerade as this checkpoint; ask the
   user to remove or rename them; this skill never deletes results).
4. Create the staging bundle: `python -m opencad stage-bundle <part>` ->
   `designs/.staging-<part>/` seeded from `designs/_template/`. Do not edit the template.

## 2. Ingest and classify sources

Copy every attachment into `designs/.staging-<part>/sources/` (original filename, EXIF
orientation applied for photos, sha256 recorded). Classify by content, not filename:

- **text/markdown/pdf-text**: read it yourself. Extract requirements, stated dimensions,
  units, coordinate conventions, revision identifiers, and explicit uncertainties.
  Distinguish quoted facts from engineering assumptions.
- **drawings, figures, photos**: do not measure them yourself. They are attached to the
  contract draft with `--image` (step 3) so the worker reads dimension lines,
  counts features, and records pixel evidence with tolerances.
- **triangle mesh** (STL/PLY/OBJ/GLB/3MF/OFF): the declared unit is mandatory; never
  guess. Dry-run first, check the sections sheet, then ingest:

  ```bash
  python -m opencad.reference ingest sources/<mesh> --units mm --axes "x=+x,y=+y,z=+z" \
      --datum min --expect-size-mm <A> <B> <C> --out designs/.staging-<part>/reference --dry-run
  python -m opencad.reference ingest ... --out designs/.staging-<part>/reference
  ```

  `--expect-size-mm` is the unit anchor (bbox size in any order, from a stated dimension);
  a wrong `--units`/`--axes` aborts. View `reference-sections.png` and the three
  `silhouette-*.png`; fix `--axes`/`--datum` until the frame matches the contract frame.
  Everything in `reference.json .measurements` becomes `measured (reference model)`
  input with the `suggested` tolerances. A free-form skin also gets `--stations 12
  --station-axis <long axis>`: per-station region outlines, analytic fits and
  `reference-sections-stations.png` for the contract's sections and the model's lofts. Native CAD (STEP/IGES) or scan-project files are
  refused: ask the user for a triangle mesh with a known unit.
- **coordinate table** (xlsx/csv of a 2D profile): `python -m opencad.reference profile
  sources/<table> --units mm [--sheet NAME --columns 0 1 --skip N] --out
  designs/.staging-<part>/reference`. Read `profile.json .measurements` (chord, area,
  stagger, thickness) and `profile.png`.

Sources with a revision history: record which revision is used and why; when two sources
disagree (e.g. a coordinate table and a CAD export), the contract must name the one taken
as authoritative and list the other under open questions.

## 3. Draft the contract (worker turn)

Run the headless drafter and drive its worker turns with `.cursor/skills/cad-drive`:

```bash
python -m opencad draft designs/.staging-<part> --name <part> --intent "<intent>" \
  --source <text or table> --image <each drawing>
# exit 75 -> Task(cad-worker, model = NEXT.model, prompt = brief.md), then re-run with --continue
```

The stage's brief (`src/opencad/initialize.py::draft_brief`) is self-contained:

- the intent verbatim, the text sources (absolute paths), `reference.json`/`profile.json`
  when present, and the attached images;
- the PartContract schema digest and an exemplar contract, inlined (the worker never opens
  `src/opencad`), and the seeded `designs/.staging-<part>/contract.yaml` to fill in;
- the rules: mm/deg; every parameter carries `provenance` (`stated`, `measured`,
  `measured (reference model)`, `derived` with `formula`, `inferred` or `defaulted` with
  `rationale`), a nonzero digital `tolerance`, and a `source` for stated/measured values;
  measured image values are approximate and get wide tolerances; nothing is invented —
  unknown details become `open_questions`, not numbers;
- the deliverables: the complete `contract.yaml` as a ```yaml block, a measurement record
  table (parameter, value, tolerance, provenance, evidence) for the brief, the feature
  list with a verification method each (`bbox`, `section`, `void`, `solid`, `count`,
  `face`), analytic `acceptance` values with formulas where they exist, the blockout
  volume band, and `edit_test` deltas for the two or three parameters that best prove
  editability;
- the frame: origin, axes, datums must be stated in words that a later reader can
  reproduce; name faces (`acceptance.faces`) when downstream meshing or mating needs them.

The worker writes `contract.yaml` and `brief.md` in place and must make
`python -m opencad check-bundle designs/.staging-<part> --name <part>` print `ok`; up to
three rounds, each a worker turn re-briefed with the exact validator message. Do not
silently edit numbers yourself.

## 4. Review the brief

The draft worker writes `designs/.staging-<part>/brief.md` (sections 1–8 of the template)
with the contract. Read it: no placeholders may remain, and it must agree with the contract
(the brief is prose for humans; the contract is the machine truth). A gap goes back to the
worker as another draft round; do not rewrite the brief yourself.

## 5. Publish

```bash
python -m opencad check-bundle designs/.staging-<part> --name <part>
python -m opencad publish designs/.staging-<part> --name <part>
```

Publication is a single same-filesystem rename and refuses an existing target. On any
failure discard the staging directory rather than leaving a partial bundle.

## 6. Blockout checkpoint (bounded)

```bash
python -m opencad blockout designs/<part>          # at most 2 worker iterations; exit 75 = worker turn, then --continue
```

The stage sends the worker an envelope-only brief, then measures the exported STEP with
OpenCascade (bbox vs `envelope`, volume vs `acceptance.blockout`). `zoo kcl analyze`
is supporting evidence and may be missing after a transient engine failure. Snapshots
four views plus an isometric, writes `results/<backend>/<part>/blockout.json`, and appends a row
to the brief's log. Then:

1. Open `results/<backend>/<part>/blockout/blockout-four-ways.png` and `blockout-iso.png` beside the
   source drawings or silhouettes. Confirm orientation, proportions, and the frame.
2. If it failed because the **contract** is wrong (a mis-read dimension, a wrong axis),
   fix `contract.yaml` (and the brief record), and rerun the blockout once. If the
   **model** is wrong, report it; do not loosen the envelope or the band to pass.
3. A blockout is a scale/frame sanity check, not geometry validation.

## 7. Report and hand off

Report: files created; a table separating stated, measured, measured (reference model),
derived, inferred, and defaulted values; open questions; blockout evidence (bbox error,
volume, iterations, engine calls) with the four-view PNG inline; the anchor check and
scan weaknesses when a reference was ingested. State that initialization is a checkpoint,
not part validation. End with:

```bash
/create-cad designs/<part>
```

## 8. Machines (`Goal: assembly`)

The machine pipeline drafts everything itself: one `asm-draft` turn writes the AssemblyContract and its brief, one `draft` turn
per modelled part writes that part's contract in parallel, the joint frames are cross-checked against the part envelopes,
everything is published, and every part's blockout runs. Nothing is modelled until `/create-cad`. Do not run sections 1 to 7
per part. `.cursor/skills/create-assembly/SKILL.md` is the full machine reference.

1. **Guard.** Names as in section 1. Refuse if `designs/<asm>` or `results/<backend>/<asm>` exists, and
   `python -m opencad next --backend <be>` must list nothing for this machine. `python -m opencad preflight --backend <be>`
   must pass. A missing solver (the container runtime and its OpenFOAM image, CalculiX) is not fatal here: its simulations will
   come back `unavailable`, and the review says so.
2. **Stage** the sources (text, tables and supplied CAD as `--source`, drawings and photos as `--image`):

   ```bash
   python -m opencad assembly stage <asm> --intent "<intent>" --source <file> ... --image <drawing> ... [--notes "..."]
   ```

3. **Draft, then blockout every part**, in the foreground with output to a log file (never `tee`):

   ```bash
   mkdir -p results/_logs && caffeinate -i -s python -m opencad assembly drive <asm> --backend <be> --stop-after blockout > results/_logs/<asm>-initialize.log 2>&1
   ```

   Give the Shell call `block_until_ms: 20000`, note its PID, and run the event loop of `.cursor/skills/regress/SKILL.md`
   section 3: `python -m opencad next --watch --pid <pid> --backend <be>`, one worker Task per `NEXT` line on its `model`
   (all of a pass in one message), each recorded with `python -m opencad dispatch` before watching again. Roles: `asm-draft`
   and `draft` on Opus, `blockout` on Grok. The command exits 0 when every part's blockout passed and 1 when one failed; the log
   ends with the checkpoint list (each part design, its blockout verdict and `blockout-four-ways.png`) and the build command.
   `--stop-after draft` stops after the drafts alone.
4. **Review and report:**
   - `Goal: assembly` and the phrase that decided it;
   - `designs/<asm>/brief.md`, and from `designs/<asm>/assembly.yaml`: the bodies (modelled, purchased, derived fluid or wall),
     the joints and their drives, transmissions, operating cases, observables, each simulation with its solver and mesh ladder,
     and the acceptance clearances and motions;
   - the lint warnings from `python -m opencad assembly check designs/<asm> --name <asm>` (for example: one mesh level gives no
     uncertainty estimate; a finest step refined only inside a region is a sensitivity study, so that prediction cannot resolve);
   - each part's `designs/<design>/brief.md` and its `results/<backend>/<design>/blockout/blockout-four-ways.png` inline, beside
     the source drawings: orientation, proportions, frame;
   - the open questions of the assembly and of every part, flagging inferred inputs (a guessed efficiency, a defaulted speed)
     and any question that changes geometry;
   - per simulation, a rough cost: how many mesh levels, the finest cell size against the fluid volume, and whether it needs
     the container; CFD ladders on large domains run for hours.
5. **Revise** when the review asks for changes: write the notes to a markdown file and run

   ```bash
   python -m opencad assembly drive <asm> --backend <be> --amend <notes.md> --stop-after draft > results/_logs/<asm>-revise.log 2>&1
   ```

   One `asm-draft` turn on the drafter's thread edits staged copies of the assembly and its part contracts, the frames are
   cross-checked again, and each changed bundle is republished (its previous version kept as `designs/<asm>/.amended/<leaf>-N`,
   the assembly's as `.amended/assembly-N`) with its blockout removed. Then run step 3 again; it redoes only those blockouts. Never edit `designs/` yourself. A failed blockout
   whose contract is wrong goes back the same way; one whose model is wrong is reported, and the build lane models the part from
   its contract regardless.
6. **Hand off.** Initialization is a checkpoint, not validation. End with:

   ```bash
   /create-cad designs/<asm>
   ```

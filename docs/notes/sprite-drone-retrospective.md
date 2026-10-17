# Sprite drone retrospective: three iterations to a PASS

The Sprite FPV drone (14 printed parts, 17 bodies, 16 joints) was recreated from its source STLs and
assembly guide. The machine passed on 2026-09-29 at 18:47 UTC: every part 12/12, the assembly 9 pass,
0 fail, 5 not applicable. It took three iterations and about 36 hours of wall clock. This note records
what the telemetry says about where the time went, why the first two iterations missed, and what would
let the next machine pass on its first pass.

A PASS is agreement between the source meshes, the contracts and the exported STEP. It is not a cooling,
printing or flight result.

## 1. Outcome and cost

| Measure | Value |
| --- | --- |
| Wall clock, first draft order to PASS | 2026-09-28 07:04Z to 2026-09-29 18:47Z (35 h 42 min) |
| Recorded worker turns | 132 (34.3 h of turn time) |
| Cursor `cad-worker` turns | 112 turns, 28.0 h (Grok 4.7 xhigh fast 94, Claude Opus 5.5 max 18 drafts) |
| Codex turns (GPT-6 Astra, effort max) | 20 turns, 6.3 h |
| Assembly attempts | 9 (8 FAIL, 1 PASS), 7.6 h |
| Part gate runs | 104; `reference_fidelity` failed 58, `features` 36, `mass_properties` 25, `edit_robustness` 19 |
| Contract revisions republished | 25 amended bundles across three `--amend` rounds |
| OOM crashes | 3 (before the memory governor; not in telemetry) |

Telemetry undercounts: the three crashed runs left no rows, `--from-stage plan` rebuilds cleaned some
results directories, and the orchestrator's own verification time is not a turn.

Where the turn time went:

| Part | Turns | Hours | First-pass result |
| --- | --- | --- | --- |
| main shell | 41 | 10.3 | FAIL: blocky skin, p95 5 to 8 mm against a 0.25 mm band |
| rear shell | 15 | 6.2 | FAIL: fidelity |
| top cover | 14 | 4.3 | FAIL: fidelity |
| assembly | 16 | 3.0 | FAIL: parts, seat clearance, camera sweep |
| rear mount | 8 | 1.9 | FAIL: fidelity (0.2 mm band) |
| cam mount L, VTX mount | 7 each | 1.6, 1.4 | FAIL: provenance strings parsed as paths |
| eight other parts | 3 to 4 | 0.4 to 1.1 | 12/12 on the first gate run |

Three free-form skins took 60 percent of all turn time. The eight prismatic parts passed on their first
gate run, seven of them from a single model turn (the launch pad's first model order was superseded and
reissued once).

Final fidelity of the skins, against their source meshes:

| Part | p95 | Hausdorff | Silhouette IoU | Band |
| --- | --- | --- | --- | --- |
| main shell | 0.165 mm | 1.45 mm | 0.994 | 0.5 / 2.0 / 0.97 |
| rear shell | 0.335 mm | 1.72 mm | 0.992 | 0.5 / 2.0 / 0.98 |
| top cover | 0.135 mm | 1.62 mm | 0.987 | 0.5 / 2.0 / 0.98 |
| rear mount | 0.062 mm | 0.48 mm | 0.997 | 0.2 / 0.5 / 0.98 |

## 2. The three iterations

**Iteration 1: match the manual.** `/initialize-cad` drafted 14 part contracts and the assembly from the
STLs and the guide; `/create-cad` built them in parallel lanes. Eight parts passed. Two failed only on
provenance strings that parsed as file paths. The three skins and the rear mount failed
`reference_fidelity`; the main shell was extruded between stations and looked blocky.
The assembly failed `parts_pass`, `clearances` and the camera sweep. Three machine crashes (Cursor at
134 GB) stopped the run before the memory governor was added. The first contracts asked for p95 0.25 mm
(main shell) and 0.2 mm (rear shell) while giving the worker only area, loop count and bounding box per
section: a band with no information to reach it.

**Iteration 2: fidelity.** Station ingest (12 Chebyshev stations per part, circle, ellipse, U-shape and
rounded-rectangle fits, 16-point outlines where nothing fits) and localized deviation (ten signed bands
along the long axis, worst regions, a deviation map) were added, and the contracts were revised to
smooth lofts with the band the reviewer chose (p95 0.5 mm, Hausdorff 2 mm). The main shell was decomposed
into five modules carved from a box envelope. The modules never replaced the box with the U skin: 22
corrections, p95 stuck between 5 and 8 mm, volume 126,000 to 169,000 mm3 against 96,390. The main shell
was then rebuilt as one file on Codex GPT-6 Astra at max effort, from the U-channel and nose lofts: 12/12
at p95 0.169 mm in two turns. The rear shell stayed at p95 2.40 mm and the loop stopped on "the worker
changed nothing". The assembly failed `parts_pass` and `topCoverSeat` (127.5 mm3 against 1.0).

**Iteration 3: inlets and the seat.** Measurement showed the rear shell's four worst regions were lobes
the model had invented, and that the source's air inlets are not holes but a 3.2 mm setback of the inner
wall beside the rear mount at ±x, open at the rim. The contract's `rearMountFit` said "line-to-line"
everywhere, so the model had closed them. The seat overlap came from the main shell's groove at the
rounded stated values 4.30 to 8.20 mm (the mesh says 4.25 to 8.25) and its side walls ending at 160.5 mm
(the mesh drops at 160.164). A contract revision added `airInlets`, probes on the lobe sites and the
slots, a section at z = -12, measured groove faces and `noseSplitZ` 160.16; a second revision corrected
two numbers the drafter had taken from the reviewer's notes instead of the mesh (the groove normals, and
the tongue flats, which are 4.30 and 8.20). One Codex correction took the rear shell to 12/12 at p95
0.335 mm. The seat then needed three more turns: the groove faces (one correction), a 2 mm ramp where the
wall should step (57 mm3, one `correct`), and the cover's outer face flaring 0.1 mm early (2.9 mm3, one
`correct`). Final seat overlap: 0.05 mm3.

## 3. Why it took three iterations

Grouped by where the defect entered.

### A. Information the worker never had

1. **Sections without outlines.** The first contracts recorded area, loops and bounding box per section.
   Workers ruled between stations and got blocky skins. Station outlines fixed this, but only in
   iteration 2.
2. **A fidelity gate with one number.** p95 alone told the worker nothing about where the model was
   wrong; corrections wandered and the loop stopped on "changed nothing". Signed bands, worst regions and
   the deviation map fixed this, also in iteration 2.
3. **Bands set without regard to the information.** p95 0.25 mm was asked of a part whose stations had
   no outlines. The band should follow from what the ingest measured.

### B. Intent the drafter got wrong

4. **A functional feature with no representation.** The inlets were visible in the render (the user
   saw "bumps where the air should come in") and in the mesh (a 3.2 mm gap between two source parts),
   but no contract named them. The drafter wrote "line-to-line" and verified it with one axial probe.
5. **Rounded "stated" values at a mating interface.** Groove 4.3 to 8.2 with tolerance 0.1, and
   `noseSplitZ` 160.5 ± 0.5, when the mesh gives 4.25, 8.25 and 160.164. A 0.05 mm rounding over a 140 mm
   tongue is 65 mm3 of interference; the 0.34 mm nose-split error is another 62 mm3.
6. **The drafter trusts notes over the mesh.** Revision 3 wrote face normals opposite to the mesh and
   moved the tongue to values the mesh does not have, because the reviewer's notes said so. It recorded
   the conflict under `open_questions` and published. `check-bundle` never compares a contract with the
   reference mesh.
7. **Provenance strings parsed as paths.** "1.989/1.898" and "192.4/195.6" in `source:` fields were read
   as missing files: five gate runs, and a correction turn that edited the contract to get past it.

### C. Interfaces are checked at the assembly and tolerated at the part

8. **Part tolerances are 10 to 100 times looser than the assembly clearance implies.** Faces at 0.1 mm
   and skins at p95 0.5 mm both pass while a 1 mm3 clearance over a 140 mm tongue fails. The seat took
   four separate fixes because each part passed on its own. The source meshes, placed on the joints,
   overlap by 0.00 mm3: that number was computable on day one and no stage computed it.
9. **Stale assembly inputs.** After a part `correct`, `assembly drive --from-stage verify` re-gated the
   old STEP; `parts.json` was stale after `--from-stage assemble`. Both were refreshed by hand.

### D. Worker execution

10. **Decomposing a skin.** Partitioning is triggered by item count (50 parameters or 25 features), not
    by feature kind. Five modules carved from a box could not become a loft; 22 corrections were spent
    before the single-file rebuild.
11. **Turn completion.** Cursor turns on Grok finished `incomplete` in 34 of 40 corrections and 9 of 21
    model turns, and ran over budget in 33 of 112. Codex Astra max turns hit the wall in 7 of 20, but the
    parts that moved to Codex each passed within one to three turns, and a killed turn still left a
    better `main.py` that the remeasure accepted.
12. **Budgets sized for prismatic parts.** 900 s corrections; the skins needed 1800 to 2700 s.
13. **Tooling defects found in flight.** `IndentationError` classified as unknown (correction skipped as
    tooling); the contact sheet crashing on a boolean snapshot value; the contract not reloaded after its
    hash changed mid-round; the deviation map lost when a results directory was cleaned; a Cursor agent id
    handed to `codex exec resume`. All fixed, all with tests where the harness allowed.

### E. Infrastructure

14. **Memory.** Three crashes before the governor (12 GB engine budget, 16 GB headroom, lane reserve,
    RSS watchdog). After it, across four monitored runs: free memory never below 28.4 GB, swap 0, peak
    engine call 9.6 GB.

## 4. What worked

- Station outlines with hybrid fits, and signed deviation bands with worst regions and a map. Every
  correction that landed after iteration 2 quoted these.
- Independent verification by the orchestrator (trimesh sections and rays, OpenCascade on the STEP)
  found every remaining defect: lobes versus inlets, the slot geometry, the wrong normals, the tongue
  flats, the 2 mm ramp, the 0.1 mm early flare. None was found by a gate first.
- `correct` with a note that states the measured and the expected value: three for three, one turn each.
- Codex GPT-6 Astra at max effort for free-form lofts, one file, no modules.
- The revision flow (`--amend --stop-after draft` on staged copies, republished as amended bundles) and
  the bundle and assembly checks.
- The memory governor and the sampler.
- The reviewer's eye. The inlet observation was a functional one that no gate expressed.

## 5. Recommendations for a first-iteration PASS

Ordered by how much of the above each removes.

**R1. Source-assembly baseline before any part is built.** At initialize, place the source meshes on
the drafted joints and compute every declared clearance, passage and motion, plus the gap map between
each mated pair. Record it in the assembly bundle. Derive part interface tolerances from it: a mating
pair with 0.05 mm designed clearance gets 0.02 mm face tolerances and `measured` provenance, written
into both part contracts by the drafter. Removes 5 and 8. The seat would have passed on the first
assembly.

**R2. A contract-versus-reference critic in `check-bundle`.** Every `measured (reference model)`
parameter, named face (position and outward normal), section (area, loops, holes) and solid or void
probe is evaluated against `reference.ply` before publication; a mismatch blocks publication and prints
the measured value. Removes 6, most of 5, and the unverified half of 4. Both revision-3 defects would
have been caught before a build.

**R3. Openings, passages and setbacks as first-class acceptance.** From the gap map in R1, the ingest
lists where a part's wall stands off its mate and where an external volume connects to an internal
cavity; the drafter must name each one (`airInlets`) with void probes in the gap and solid probes on
the wall. At the assembly level, a `passages` check flood-fills the source assembly from outside to
each internal cavity and repeats it on the built assembly. Removes 4. This is the defect a human found.

**R4. Station outlines and localized deviation by default.** For any part with a mesh reference,
`initialize` runs `--stations 12` and the contract carries the outlines; the fidelity gate always
reports bands and worst regions. The band follows the ingest: stations that fit analytic shapes to
0.014 mm can carry a tight band, a free-form bulge cannot. Removes 1 to 3.

**R5. Route the model and the budget by part class.** Classify parts at draft time (prismatic,
analytic, free-form loft). Free-form parts go to the high-effort model as one file with decomposition
off and 2700 s correction budgets; prismatic parts keep the fast model. Removes 10 to 12. The data: the
eight prismatic parts passed in one Grok turn each; every skin that moved to Codex passed in one to
three turns after 22 Grok corrections had not.

**R6. Never partition a loft.** Decomposition considers feature kind, not only item count; a contract
that is mostly stations and lofts is built as one file.

**R7. Keep the best solid inside a turn.** When the local critic passes during a turn, snapshot
`main.py`; a wall kill returns the best passing snapshot rather than the last edit. The exit-124 turns
that still passed did so by luck.

**R8. Assembly staleness follows part changes.** `correct` or `drive` on a part that belongs to an
assembly marks the assembly's parts stage stale, and assembly verify restages any input whose handoff
hash changed. Removes 9.

**R9. Provenance path tokens need a separator and a known extension, or a `sources/` or `reference/`
prefix.** Numbers with slashes are not paths. Removes 7.

**R10. Reference-derived probes in fidelity corrections.** When `reference_fidelity` fails with worst
regions, the brief carries mid-wall solid probes and void probes computed from the reference at those
regions as evidence (not contract edits), and "changed nothing" ends the loop only after such a brief
was issued. Removes the rear shell's iteration-2 stall.

**R11. Functional intent from the guide.** The assembly draft gets a `functions` section (cooling air
path, camera tilt range, battery access) with the check that expresses each one. The guide describes
the machine's purpose; the contracts described only its shape.

**R12. Three truth cases with calibration-log entries.** A free-form skin from stations; a mating pair
with sub-0.1 mm designed clearance; a setback opening between mated parts. These failure modes are then
scored, not rediscovered.

**R13. Keep the in-flight fixes under test.** The program-error classifier, the contact sheet, the
contract reload, the deviation-map redraw and the resume guard each have a test; add one for the
assembly restaging in R8 when it lands.

## 6. What a first pass would look like

With R1 to R5 in place: initialize produces contracts whose interface tolerances come from the source
assembly and whose stations, probes and openings were checked against the meshes; the eleven prismatic
and analytic parts build in one or two fast turns each, as eight of them did; the three skins build once on the high-effort
model from station outlines with the localized gate; the assembly is placed once and passes clearances
because both sides of every seat were pinned to the same measured planes. The parts that passed first time
here cost 0.4 to 1.1 hours each; the skins, once the contract carried outlines and probes, cost one to
three turns of 15 to 45 minutes. That points to a single pass of roughly a third of the recorded turn
time, with the drafter's share growing and the correction share shrinking. It is a projection from this
one machine, not a measurement.

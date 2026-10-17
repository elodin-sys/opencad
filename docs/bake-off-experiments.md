# Bake-off experiments

Running log for the Zoo bake-off. Each entry is one controlled run of the same part, so later notes can be compared with these numbers. Append new entries at the bottom. Do not rewrite an earlier entry when a later run changes the conclusion.

The audience is Zoo. The question under test is what it costs Astra (`gpt-6-astra`) to author the part, and what it costs the Zoo API to execute it.

## Shared setup

- Part: `designs/bracket`. An 80 × 50 × 6 mm plate, four Ø4.5 holes, R5 vertical fillets. Contract volume **23489.535 mm³**.
- Author: Codex CLI, model `gpt-6-astra`, service tier **fast**. Cursor only starts the pipeline and writes this log. No Cursor CAD worker. `OPENCAD_CODEX_NO_FALLBACK=1`.
- Price card `gpt-6-astra-fast-short-2026-10-14` (OpenAI fast-tier short-context list prices, 2026-10-14): **$20** uncached input, **$2** cached input, **$100** output, per million tokens. Reasoning tokens are already inside output and are not billed again.
- A cell is blockout, then `drive --fresh`. Wall time is worker seconds plus evaluator seconds. Zoo credits are the prepaid balance drop for that cell; Zoo USD is the monetary-value drop. Local kernels are $0.
- Every finished cell below passed 11 gates, with 1 not applicable, and the exported STEP measured **23489.535 mm³** in OpenCascade. Fallback count was 0.

## 2026-10-14 — Four backends, role-default effort

Tag `bakeoff-astra`. Reasoning effort came from the role profile: blockout **low**, model **high**. Fast tier. Zoo geometry went through the `zoo` CLI. The worker was told to read `kcl-docs` and `zoo-tooling` before writing KCL, and it did.

| Backend | Input tokens | Cached | Output | Codex USD | Zoo | Worker | Wall |
|---|---:|---:|---:|---:|---|---:|---:|
| CadQuery | 1,134,076 | 1,058,944 | 9,086 | $4.53 | — | 228 s | 247 s |
| build123d | 1,096,382 | 984,320 | 8,895 | $5.10 | — | 216 s | 235 s |
| FreeCAD | 791,206 | 728,576 | 8,708 | $3.58 | — | 187 s | 206 s |
| Zoo | 2,631,735 | 2,514,048 | 16,829 | $9.06 | 97 credits, $0.80 | 401 s | 423 s |

Zoo turns: blockout 90 s, 383,411 input tokens, $1.46; model 311 s, 2,248,324 input tokens (2,154,880 cached), $7.60.

Zoo cost about twice the local backends on this plate. The prompt itself is about 70 lines. The extra tokens are the doc pages the worker opened, then re-sent on every later step. Cached input is $2 per million, and it is most of the Zoo Codex bill.

## 2026-10-14 — Zoo MCP, max reasoning

Tag `bakeoff-astra-mcp`. Effort **max**, tier **fast**. Zoo docs lookup and the modeling session went through `zoo-mcp` (`search_kcl_docs`, `get_kcl_doc`, `execute_kcl`, `stop_modeling_session`, and the format, lint, snapshot, measure, and export tools). The worker was told not to open `kcl-docs/`, `zoo-tooling/*.md`, or `kcl-examples/`. The pipeline's own verify and export stayed on the `zoo` CLI.

The first attempt was stopped. Codex started `zoo-mcp`, then refused every tool call with "MCP tool call requires approval, but approval policy is never." The worker began searching the repo. That process was killed before a part existed. The completed cell below used `mcp_servers.zoo.default_tools_approval_mode="approve"`.

| | Input tokens | Cached | Output | Codex USD | Zoo | Worker | Wall |
|---|---:|---:|---:|---:|---|---:|---:|
| Zoo cell | 3,574,191 | 3,396,864 | 38,249 | $14.17 | 486 credits, $4.04 | 697 s | 719 s |

Turns: blockout 161 s, 1,087,909 input tokens, $4.10; model 536 s, 2,486,282 input tokens (2,370,560 cached), $10.07. No commands opened the doc tree. The model turn still issued 8 doc searches, 7 full doc fetches, 9 executes, and 9 exports.

Codex dollars and Zoo credits both rose relative to the high-effort CLI cell. The credit jump is the hosted MCP calls. The Codex jump is a longer thread: max reasoning, plus each tool result billed again on the next step.

## 2026-10-14 — MCP off, max reasoning, CLI docs

Tag `bakeoff-astra-max`. Same max effort and fast tier. Zoo MCP removed. The worker again reads `kcl-docs` and `zoo-tooling` and checks geometry with `zoo kcl format`, `lint`, `analyze`, and `export`. This is the control for the MCP cell: effort matches, tooling matches the first Zoo cell.

| | Input tokens | Cached | Output | Codex USD | Zoo | Worker | Wall |
|---|---:|---:|---:|---|---:|---:|---:|
| Zoo cell | 4,287,214 | 4,094,464 | 37,520 | $15.80 | 88 credits, $0.73 | 656 s | 679 s |

Turns: blockout 143 s, 845,807 input tokens, $3.63; model 513 s, 3,441,407 input tokens (3,311,744 cached), $12.17. Zero Zoo MCP events. `settings.json` records `reasoning_effort: max` and `service_tier: fast`.

Zoo credits returned to the first cell's range (88 versus 97). Codex dollars did not. This cell is the most expensive Codex bill of the three. Max reasoning, with the doc text carried in the thread, accounts for the step from $9.06 to about $15. The MCP session accounts for the step from about $0.80 of Zoo API to $4.04.

## What to tell Zoo so far

On this plate, Astra's Codex bill is dominated by thread length, and most of that length is cached input resent after each tool call. Pointing the worker at the KCL markdown tree makes a long thread. Giving it `zoo-mcp` avoided those file reads and did not shorten the thread, because the worker fetched several docs and ran many hosted executes. Those executes are Zoo API credits on top of the Codex bill.

A useful Zoo-side change is a lookup that returns one short page, and a modeling session the worker can keep open without a fresh doc search and a fresh export on every check.

## 2026-10-14 — Peristaltic pump, max reasoning, CLI

Tag `bakeoff-astra-pump`. Effort **max**, tier **fast**. Zoo MCP off. Machine `designs/peristaltic-pump`: purchased printed parts placed from STEP, plus one modelled silicone tube (`peristaltic-pump-tube`). `assembly drive --fresh` on CadQuery, build123d, FreeCAD, and Zoo together. The older build123d tube handoff was set aside so that lane was authored again.

The tube passed on every backend. OpenCascade volume **587.608 mm³** against 587.608. Tube gates 11 pass, 1 not applicable.

| Backend | Input tokens | Cached | Output | Codex USD | Zoo | Worker | Wall | Assembly gates |
|---|---:|---:|---:|---:|---|---:|---:|---|
| CadQuery | 3,611,707 | 3,403,520 | 44,722 | $15.44 | — | 877 s | 1,074 s | PASS 10 / 0 / 4 n/a |
| build123d | 3,238,111 | 3,039,616 | 38,019 | $13.85 | — | 779 s | 977 s | PASS 10 / 0 / 4 n/a |
| FreeCAD | 6,785,682 | 6,525,568 | 55,768 | $23.83 | — | 1,169 s | 1,366 s | PASS 10 / 0 / 4 n/a |
| Zoo | 10,947,889 | 10,481,536 | 89,410 | $39.23 | 105 credits, $0.87 | 1,609 s | 1,700 s | FAIL 4 / 3 / 7 n/a |

Turns, input tokens: CadQuery tube 2,206,192 and assemble 1,405,515. build123d tube 1,768,804 and assemble 1,469,307. FreeCAD tube 4,701,788 and assemble 2,083,894. Zoo tube 5,026,176, assemble 2,182,029, and a correction 3,739,684.

The three local assemblies agree. Drive ratio **0.25** (the 4:1 train). Reduced-model flow **6.109** (same number on each, from the shared solver, not from the kernel). Envelope error 0.0004 mm.

Zoo authored a passing tube, then wrote `parts/zoo/peristaltic-pump/main.py` because the assemble deliverable is Python. `ZooEngine` has no `build()`, so verify raised `AttributeError` and the export, joint, and motion gates failed. A bounded correction repeated the same miss. The worker's own local STEP check saw 14 solids and the joints seated; the pipeline never got a Zoo export. Zoo credits here are the tube's hosted calls only.

## 2026-10-14 — Peristaltic pump on Zoo, native KCL assembly

Tags `bakeoff-astra-pump-zoo` (blocked attempt) and `bakeoff-astra-pump-zoo2` (pass). Effort **max**, tier **fast**. Zoo MCP off. The zoo assembly source is now `parts/zoo/peristaltic-pump/main.kcl`: `import "inputs/<body>.step"` for each of the 14 staged STEPs, global elementary rotations then a global translate, plus a `placements.json` sidecar. `ZooEngine.build_assembly` runs `zoo kcl export` for STEP and STL; the existing evaluator does the rest. The zoo tube from the first pump run was reused, not re-authored.

A two-body live check first confirmed the CLI resolves foreign STEP imports and `global = true` turns about the world axes: two separate solids, volume error 5e-14, Hausdorff 3e-8 mm.

**Zoo cannot import its own STEP export.** The first KCL attempt failed at verify with `KCL execution failed: engine: import failed` on `peristaltic-pump-tube.step`, the tube STEP the zoo backend had exported (AP242, metre units). The other 13 STEPs, written by OpenCascade, imported and placed within tolerance. The same tube solid re-written by OpenCascade imported on the first try. The pipeline now rewrites modelled handoffs through OpenCascade when it stages zoo assembly inputs.

| Zoo turn | Input tokens | Cached | Output | Codex USD | Zoo | Worker |
|---|---:|---:|---:|---:|---|---:|
| Tube model (first pump run) | 5,026,176 | — | — | $16.71 | 105 credits, $0.87 | 808 s |
| Python placement + correction (first pump run, no `build()`) | 5,921,713 | — | — | $22.52 | — | 801 s |
| KCL assemble + correction, tube import blocked | 7,699,631 | — | — | $28.44 | 286 credits, $2.37 | 1,158 s |
| KCL assemble, OpenCascade-staged tube | 5,390,991 | 5,246,080 | 31,712 | $16.56 | 89 credits, $0.74 | 1,164 s |

The passing path (tube plus the KCL assemble) cost **$33.27** of Codex and **194 Zoo credits ($1.61)**, with 1,972 s of worker time and 154 s of evaluator time. The three local machines were $13.85 to $23.83. The two blocked attempts added $50.96 and 286 credits.

Result: PASS 10 / 0 / 4 n/a, same as CadQuery, build123d, and FreeCAD. 14 solids. Largest agreement deviation is the tube: volume error 4.8e-10, Hausdorff 0.031 mm against a 0.05 mm limit. `python -m opencad.bakeoff compare-assembly peristaltic-pump` against build123d passes for zoo, CadQuery, and FreeCAD. Same five handoff files, every body's volume within 4e-10 and centre of mass within 0.0001 mm, same bounding box, drive ratio 0.25, flow 6.109, 14 GLB bodies.

## 2026-10-15 — Prusa MINI extruder front, max reasoning, CLI

Tag `bakeoff-astra`. Effort **max**, tier **fast**. Zoo MCP off. Part `designs/prusa-mini-extruder-front`: one solid, 124 parameters, 52 features. Published contract, fresh authoring. CadQuery, build123d, and FreeCAD ran together; Zoo ran after them. All four decomposed into feature-group modules.

| | Input tokens | Cached | Output | Codex USD | Zoo | Worker | Wall |
|---|---:|---:|---:|---:|---|---:|---:|
| cadquery | 23,768,543 | 22,490,240 | 254,047 | $95.95 | — | 7,282 s | 7,356 s |
| build123d | 22,620,515 | 21,443,968 | 279,426 | $94.36 | — | 8,096 s | 8,172 s |
| freecad | 34,753,628 | 33,203,968 | 316,353 | $129.04 | — | 10,061 s | 10,178 s |
| zoo | 15,767,502 | 15,258,624 | 139,787 | $54.67 | 1,434 credits, $11.90 | 14,177 s | 14,183 s |

What changed: this is the first metered Astra run of the extruder housing. CadQuery, build123d, and FreeCAD each pass 11 gates (1 n/a) with 52/52 features. OpenCascade STEP volumes are 29,957.813 mm³, 29,946.203 mm³, and 30,069.481 mm³. The contract declares no volume band; the dimension sheet's diagnostic quote is 29,833.56 mm³. Fallbacks are 0. Zoo's integrate turn hit the 2,700 s budget while the kernel returned `The Zoo engine cannot handle this 3D subtraction yet`. The cell is FAIL on traceability: plan and model exist, verify/export/inspect/edit do not, and there is no gated STEP volume. The handoff has provenance sidecars and no STEP, STL, or GLB.

## 2026-10-15 — Correction: why the Zoo Prusa cell failed, and what it cost

The Zoo row above is under-metered, and most of the failure came from the pipeline, not the kernel.

**Cost.** Five of the eight Zoo turns hit their wall budget (exit 124): partition, the exterior, keyhole, and halfClamp modules, and integrate. A killed `codex exec` never emits `turn.completed`, so those turns were recorded as zero tokens. The thread rollout files (`~/.codex/sessions/**/rollout-*-<thread>.jsonl`, last `token_count.total_token_usage`) hold the real usage:

| Killed turn | Input tokens | Cached | Output | Codex USD |
|---|---:|---:|---:|---:|
| partition | 3,562,693 | 3,420,800 | 35,222 | $13.20 |
| exterior module | 5,703,127 | 5,494,016 | 51,293 | $20.30 |
| keyhole module | 6,578,910 | 6,382,848 | 43,312 | $21.02 |
| halfClamp module | 13,683,753 | 13,470,592 | 61,092 | $37.31 |
| integrate | 12,454,976 | 12,125,952 | 88,973 | $39.73 |
| **unmetered total** | 41,983,459 | 40,894,208 | 279,892 | **$131.56** |

Zoo's real Codex cost for that cell is **$186.23**, not $54.67: about 57.8M input tokens, more than any local backend. Credits (1,434, $11.90) were metered correctly. No local turn was killed, so the CadQuery, build123d, and FreeCAD rows stand. Killed turns are now billed from the rollout: usage mode `rollout`, the exec's delta for a resumed thread.

**Pipeline causes, Zoo only.**

1. Decomposed parts compose `datum` and the modules in scratch mains under `results/zoo/<part>/decompose/<group>/main.kcl`, which imported `"../../../../../parts/zoo/<part>/datum.kcl"`. Zoo 0.2.204 rejects any import path that starts with `..`. The datum check and the composition probe failed in 0.01 s, and every module worker's critic target failed the same way. The workers lost much of their budgets on workarounds (`*-standalone.kcl` copies, symlinks). The Python backends import with `sys.path` and never saw this. The Zoo engine now runs such an entry from a flat temporary copy of the part's sources.
2. At 04:29 the integrate worker had all five modules composed into one valid solid: 30,212 mm³, 32/40 cylinders, 76/89 faces. It was killed at 2,700 s, and the stage then required a clean exit (`ok = exit 0 and entry exists`). Verify, export, inspect, and every correction round were skipped. A killed turn's deliverable is now measured; the last executing checkpoint is restored first when the sources no longer run. Briefs also carry an absolute UTC deadline 120 s before the kill.

**Kernel causes.** These were real: `The Zoo engine cannot handle this 3D subtraction yet` (and `union yet`), `Batch edit result is not valid`, `Internal engine error on request`. The workers cleared several of them without changing a dimension:

- a boolean `tolerance = 0.001mm` for a stepped keyhole cutter;
- building a cutter on `XY` and rotating it into place by an exact `90deg`;
- overlapping a tool 0.002-0.02 mm past a tangent face, or folding the tangent tools into one cutter.

These are now in the Zoo skill (`kcl-docs/patterns.md`, "Kernel-safe construction"). The earlier ladder notes that "Zoo never landed the booleans" on this part and stalled on the Voron duct may include the same import failure. Treat them as unconfirmed kernel failures until re-run. Run-1 diagnostics (about 150 isolated engine runs with their messages) are preserved under `results/_spikes/zoo-prusa-run1/integrate/`.

## 2026-10-15 — Zoo Prusa re-run with the fixes, voided by an account block

Tag `bakeoff-astra-prusa-zoo2`. Effort max. Tier fast. Zoo path: CLI. Fresh run from blockout on the same contract, with the import staging, timeout measurement, rollout billing, and brief deadline above.

| | Input tokens | Cached | Output | Codex USD | Zoo | Worker | Wall |
|---|---:|---:|---:|---:|---|---:|---:|
| zoo | 46,149,250 | 44,587,648 | 391,202 | $159.53 | 642 credits, $5.33 | 11,658 s | 11,667 s |

What changed: the fixes held. The datum check passed, every module's critic target executed, no turn hit its budget, and all nine turns were metered from `turn.completed`. With the engine available, the fasteners module passed 84 of its 85 items, keyhole 12 of 12, and exterior stopped partway (3/8 faces, 1/6 planes) because Zoo would not join the lower-left bevel wedge. At 16:31 UTC, during the halfClamp module, Zoo began refusing every engine call with `AuthTokenInvalid Your account is blocked because your payment method failed`, while the balance API still reported `can_execute: true` with 297,953 prepaid credits. halfClamp stopped at its last exported checkpoint (14/46 items). The filament module and integrate ($18.49) were written but never executed. Verify and export hit the same refusal, so there is no STEP; gates were 5 pass, 5 fail, 2 n/a. The cell is void, not a Zoo modelling verdict; the block was still in place at 17:03 UTC. Since then the refusal classifies as billing, preflight runs its 1 mm engine probe on every call (and re-probes a cached refusal), and decompose stops before the integrate turn when the composition probe is refused on billing. A block that starts during a module still lets the remaining module turns run.

## 2026-10-15 — Zoo Prusa run 3: PASS, and resumed turns were billed twice

Tag `bakeoff-astra-prusa-zoo3`. Effort max. Tier fast. Zoo path: CLI. Same contract and fixes as run 2, after Zoo lifted the block; the account plan now reads `free`, with the same prepaid credits and PAYG price. Preflight's engine probe was invalid KCL for zoo 0.2.204 (it had only run at a zero balance) and is now a cube that executes. The local rows are the `bakeoff-astra` cells above, re-metered as described below.

| | Input tokens | Cached | Output | Codex USD | Zoo | Worker | Wall |
|---|---:|---:|---:|---:|---|---:|---:|
| cadquery | 21,585,983 | 20,440,192 | 228,780 | $86.67 | — | 7,282 s | 7,356 s |
| build123d | 20,889,623 | 19,834,112 | 251,379 | $85.92 | — | 8,096 s | 8,172 s |
| freecad | 31,621,818 | 30,219,904 | 292,610 | $117.74 | — | 10,061 s | 10,178 s |
| zoo | 74,685,265 | 72,643,328 | 550,988 | $241.22 | 3,626 credits, $30.09 | 12,916 s | 14,041 s |

What changed: Zoo passes 11 gates (1 n/a) with 52/52 features, like the other three. The handoff STEP is one valid solid of 29,911.334 mm³ in OpenCascade, against 29,957.813, 29,946.203, and 30,069.481 mm³ for CadQuery, build123d, and FreeCAD; the contract declares no volume band. Every module and the integrate turn finished inside its budget (integrate 2,522 s of 2,700). One correction round (784 s) made the native STL watertight without changing a contract check. The read-only Astra render review found the same features as the CadQuery review and no detached geometry. Zoo cost 2.8 times the cheapest local cell in Codex, most of it in the integrate turn (17.6M input tokens) and the five modules, plus $30.09 of Zoo credits, and took 1.9 times the wall time.

**Metering correction.** In a resumed `codex exec`, `turn.completed` reports the thread's running total, not the exec's own usage, so every resumed turn (partition fix, correction, ECR) was billed again for the earlier turns of its thread. The thread's rollout `token_count` delta over the exec gives the real share: run 3's correction used 6,600,824 input tokens and was recorded as 24,239,600. Resumed execs are now billed from that delta (usage mode `rollout`), and the recorded telemetry rows were corrected in place (mode `thread-delta`, original figures kept as `tokens_reported` and `usd_reported`). Superseded figures above:

- 2026-10-15 Prusa: CadQuery $95.95 is $86.67, build123d $94.36 is $85.92, FreeCAD $129.04 is $117.74.
- 2026-10-15 Zoo run 2: $159.53 is $148.09 (43,228,549 input tokens).
- 2026-10-14 first pump run: Zoo $39.23 is $30.94; its correction turn used 1,557,655 input tokens, not 3,739,684.
- 2026-10-14 pump on Zoo: Python placement plus correction $22.52 is $14.24; KCL assemble plus correction $28.44 is $17.68; the two blocked attempts cost $31.92, not $50.96. The passing path ($33.27) had no resumed turn.

## 2026-10-15 — Three minimal Zoo kernel repros

One Astra turn (effort high, outside any bake-off cell: $9.40, 52 engine calls) reduced logged Prusa failures to self-contained KCL 2 programs under `results/_spikes/zoo-repros/`. Each `main.kcl` fails on zoo 0.2.204 on two separate runs, and its `workaround.kcl`, one line different, passes; both were re-run independently afterwards. `README.md` there has the commands, volumes, sources, and every intermediate engine input.

| Case | Lines | Engine refusal | One-line workaround |
|---|---:|---|---|
| `01-subtraction` | 21 | `The Zoo engine cannot handle this 3D subtraction yet.` | A box cutter that ends exactly on a stepped cylinder's shoulder, tangent to the smaller cylinder; end it 0.01 mm past the shoulder. |
| `02-union` | 17 | `The Zoo engine cannot handle this 3D union yet.` | A box whose corner lies exactly on a quarter-annulus's inner arc; extend the box 0.01 mm. |
| `03-batch-edit` | 29 | `Batch edit result is not valid` | Two orthogonal notches into the same stepped cylinder; extend the second notch 0.01 mm. |

All three are ordinary positive-volume solids. The refusal follows an exact tangency or a point contact on a curved face, which the 0.01 mm overruns already in `kcl-docs/patterns.md` avoid.

## Adding an entry

Copy the block below, fill it from `results/<backend>/<part>/telemetry.jsonl` filtered by `--tag`, and from `cost.json` for Zoo credits. Record the tag, effort, tier, whether Zoo MCP was attached, gate verdict, OpenCascade volume, and one sentence on what changed.

```markdown
## YYYY-MM-DD — Title

Tag `...`. Effort .... Tier fast. Zoo path: CLI or MCP.

| | Input tokens | Cached | Output | Codex USD | Zoo | Worker | Wall |
|---|---:|---:|---:|---:|---|---:|---:|
| | | | | | | | |

What changed:
```

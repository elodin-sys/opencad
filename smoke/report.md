# Smoke test report

Run: 2026-09-15 05:29:26 UTC on Daniels-MacBook-Pro.local, 558s, 44/44 checks passed, 35 hosted engine executions (billed as API usage).

## Environment

| id | check | status | time | evidence |
|---|---|---|---|---|
| E1 | zoo CLI present | PASS | 0.0s | zoo 0.2.196 (c8d8092200c3) |
| E2 | zoo auth logged in | PASS | 0.4s | x46085@gmail.com @ https://api.zoo.dev/ |
| E3 | API token available for MCP | PASS | 0.4s | 40 chars via zoo auth status -t (used for the MCP server) |
| E4 | uv/uvx present | PASS | 0.0s | uv 0.5.13 (Homebrew 2024-12-27) |
| E5 | Zoo Design Studio installed | PASS | 0.0s | installed, v1.4.8 |

## Skills (static)

| id | check | status | time | evidence |
|---|---|---|---|---|
| S1 | check_skills.py gates | PASS | 0.3s | 9 gates pass: frontmatter, budget, dedup, links, provenance, dialect, coverage:std, coverage:examples, coverage:tooling |
| S2 | skill discovery (5 SKILL.md in .agents/skills) | PASS | 0.0s | codex-worker, kcl-docs, kcl-examples, kcl-research, zoo-tooling |
| S3 | cold-read task budgets <= 8k tokens | PASS | 0.0s | plate with M4 holes 6003; extrude(method = NEW) 6975; helix sweep sample 1479; B-rep vs mesh 1649; export STEP via CLI 2139 tok |
| S4 | sample corpus extracted intact | PASS | 0.0s | 126 samples, 176 files; 5 without kclVersion = 2.0 are flagged in index.md: bracket, bracket-with-slot, field-monitor-stand, multi-axis-robot, sheet-metal-bracket |

## CLI: zoo kcl

| id | check | status | time | evidence |
|---|---|---|---|---|
| C1 | format is idempotent on the coupon | PASS | 0.0s | formatted output identical to committed source |
| C2 | lint passes on the coupon | PASS | 0.0s | no lint findings |
| C3 | lint rejects `var width` with a readable error | PASS | 0.0s | exit 1: Use of sketch var without initial value is experimental and may change or be removed. |
| C4 | analyze coupon matches analytic volume/area/com/bbox | PASS | 2.4s | volume 9600.00 mm3, area 5600.0 mm2, com (30.00, 20.00, 2.00), bbox 60x40x4 |
| C5 | export STEP is deterministic with exact B-rep topology | PASS | 3.0s | 7060 bytes, identical sha256 across two exports (9bb7eb93d128); B-rep topology 1 solid / 6 faces / 12 edges / 8 vertices |
| C6 | export STL passes independent mesh check | PASS | 2.0s | 12 triangles, closed manifold, mesh volume 9600.00 mm3 (independent stdlib check) |
| C7 | snapshot four-ways PNG | PASS | 2.4s | smoke/out/cli/coupon-four-ways.png 2560x1440 |
| C8 | bracket (skill patterns) matches analytic volume | PASS | 2.2s | volume 23491.23 mm3 vs analytic 23489.54 (+0.007%), com centred: tags, fillet, hole::holes, assert all exercised |
| C9 | multi-file skill sample executes as a project | PASS | 5.3s | coilover-assembly (5 files, imports parameters.kcl) volume 334960 mm3 |

## REST API via CLI

| id | check | status | time | evidence |
|---|---|---|---|---|
| A1 | authenticated GET /user | PASS | 0.4s | GET /user -> x46085@gmail.com |
| A2 | GET /ping | PASS | 0.4s | GET /ping -> pong |
| A3 | file API volume of exported STEP | PASS | 2.2s | POST /file/volume on exported STEP -> 9600.00 mm3 (round-trip agrees with KCL) |

## MCP server (uvx zoo-mcp)

| id | check | status | time | evidence |
|---|---|---|---|---|
| M1 | initialize handshake | PASS | 7.5s | Zoo MCP Server v1.30.0, protocol 2024-11-05 |
| M2 | tools/list matches skill inventory | PASS | 0.0s | 46 tools, identical to zoo-tooling/mcp.md |
| M3 | format_kcl | PASS | 0.0s | format_kcl returns the source unchanged |
| M4 | lint_and_fix_kcl (code string, no writes) | PASS | 0.0s | lint_and_fix_kcl: source unchanged, All lints fixed |
| M5 | mock_execute_kcl coupon | PASS | 0.0s | coupon mock-executes: KCL code mock executed successfully |
| M6 | mock_execute_kcl surfaces `var` error | PASS | 0.0s | broken.kcl rejected: syntax: Use of sketch var without initial value is experimental and may change or be removed. |
| M7 | assert() fails fast under mock execution | PASS | 0.0s | assert fires without the engine: type: assert failed: Expected 2 to be greater than 2.25 but it wasn't: plate too thin for M4 clearance holes |
| M8 | skill samples mock-execute (local interpreter) | PASS | 6.7s | 122/126 mock-execute locally; 4 need the engine (hole::): bracket, countersunk-plate, gridfinity-bins, gridfinity-bins-stacking-lip |
| M9 | calculate_kcl_physical_properties coupon | PASS | 2.2s | volume 9600.00 mm3, com (30.0, 20.0, 2.0) |
| M10 | docs and sample lookup | PASS | 0.0s | search_kcl_docs('fillet') -> std-solid-fillet; search_kcl_samples('gear rack') -> gear-rack |

## Agent loop via MCP (bracket)

| id | check | status | time | evidence |
|---|---|---|---|---|
| L1 | source checks: format, lint, mock | PASS | 0.0s | format + lint clean; mock defers hole:: to the engine as documented |
| L2 | execute in a modeling session | PASS | 1.6s | session 5564c4ef, artifact graph 63 KB |
| L3 | inspect: 4-view snapshot | PASS | 1.3s | 4-view composite smoke/out/e2e/image.jpg |
| L4 | measure against the analytic contract | PASS | 3.3s | volume 23491.23 mm3 (+0.007% vs analytic), com centred |
| L5 | export STEP (exact B-rep) | PASS | 3.0s | smoke/out/e2e/bracket.step 29 KB, 18 B-rep faces (6 plate + 4 fillets + 4 holes x 2 half-cylinders) |
| L6 | convert STEP -> STL and check the mesh independently | PASS | 1.6s | STEP -> STL: 796 triangles, closed, mesh volume 23491.2 mm3 (+0.01%, tessellation) |
| L7 | re-measure the exported file with a real density | PASS | 8.9s | exported STEP re-measured: volume 23491.23 mm3, mass 63.43 g at 2700 kg/m3 (aluminium) |
| L8 | clean up the session | PASS | 0.0s | session closed, none left open |

## Codex worker (GPT-6 Astra)

| id | check | status | time | evidence |
|---|---|---|---|---|
| X1 | codex CLI present | PASS | 0.0s | codex-cli 0.154.0 |
| X2 | codex doctor: gpt-6-astra via openai, ChatGPT auth | PASS | 0.8s | gpt-6-astra via openai, auth chatgpt, doctor ok |
| X3 | read-only round trip at max effort | PASS | 6.0s | thread 01a0a38b answered OPENCAD-OK, effort max; 0 commands, 6s, tokens in 15363 (cached 12032) out 55 |
| X4 | CAD task: plate with hole, verified independently | PASS | 402.8s | main.kcl written and self-verified; independent analyze: volume 5607.93 mm3 (+0.011% vs analytic), bbox 40x30x5, com centred; 29 commands, 399s, tokens in 1180326 (cached 1115264) out 11039 |
| X5 | resume the thread: change the hole, re-verify | PASS | 90.3s | thread 01a0a38b resumed; volume 5435.42 mm3 (+0.017% vs analytic); 5 commands, 88s, tokens in 1475271 (cached 1322752) out 13328 |

## Notes

- 5 aquarium samples use sketch blocks but declare kclVersion 1.0 or none (bracket, bracket-with-slot, field-monitor-stand, multi-axis-robot, sheet-metal-bracket); kcl-examples/index.md flags them `!kcl…`.
- hole::hole/holes `cutAt` is read in the target face's local frame: on the END face of an XY extrusion `[a, b]` lands at global `(b, a)`. smoke/parts/bracket encodes this; a future engine change would show up here as a volume/centre-of-mass mismatch.
- mock_execute_kcl cannot evaluate face-dependent std code: 4 samples using hole:: (bracket, countersunk-plate, gridfinity-bins, gridfinity-bins-stacking-lip) report "engine isn't available" and need execute_kcl.

# Validation envelope

Generated 2026-09-28T01:09:49Z by `python -m opencad.truth report`. Modelling backend: `build123d`. Every verdict below is a CAD-reconstruction verdict: agreement between the exported geometry and the pinned truth, by truth class. Nothing here is physical or engineering validation, and downstream targets (flow, distortion) are recorded, not scored.

## Truth classes

- **A** — physical measurement of the real object
- **B** — reference geometry published by the benchmark authors
- **C** — derived arithmetically from published dimensions
- **D** — self-consistency only
- **E** — illustrative

## Cases

| case | class | role | arm | backend | attempts | scored | passes | latest verdict | required checks | failed checks |
|---|---|---|---|---|---|---|---|---|---|---|
| bearing-housing | B | validation | spec-and-views | freecad | 41 | 38 | 38 | PASS | 22/22 | - |
| chiral-keyplate | D | calibration | text-only | freecad | 6 | 4 | 4 | PASS | 14/14 | - |
| compound-train | C | validation | spec-only | build123d | 6 | 6 | 6 | PASS | 14/14 | - |
| crank-slider | C | validation | spec-only | build123d | 6 | 6 | 6 | PASS | 9/9 | - |
| disc-brake | B | validation | construction-steps | build123d | 2 | 2 | 0 | FAIL | 11/11 | - |
| enclosure-base | B | validation | spec-and-views | freecad | 39 | 36 | 36 | PASS | 24/24 | - |
| fan-01 | A | validation | supplied-cad | build123d | 3 | 3 | 0 | FAIL | 2/2 | - |
| fda-pump | A | validation | supplied-cad | build123d | 4 | 4 | 0 | FAIL | 2/2 | - |
| four-bar | C | validation | spec-only | build123d | 6 | 6 | 6 | PASS | 10/10 | - |
| fusion-01184-recon | B | validation | renders-and-sheet | freecad | 6 | 4 | 4 | PASS | 18/18 | - |
| fusion-12944-recon | B | validation | renders-and-sheet | freecad | 9 | 7 | 4 | PASS | 22/22 | - |
| fusion-13786-recon | B | validation | renders-and-sheet | freecad | 6 | 4 | 4 | PASS | 15/15 | - |
| fusion-15317-recon | B | validation | renders-and-sheet | build123d | 7 | 5 | 4 | PASS | 20/20 | - |
| fusion-16418-recon | B | validation | renders-and-sheet | build123d | 6 | 4 | 4 | PASS | 11/11 | - |
| gear-pair | C | validation | spec-only | freecad | 7 | 5 | 5 | PASS | 16/16 | - |
| gear-train | C | validation | spec-only | build123d | 7 | 7 | 7 | PASS | 16/16 | - |
| nasa-atb-axisymmetric-bump | C | validation | text-and-points | freecad | 6 | 4 | 4 | PASS | 11/11 | - |
| nasa-backstep-driver-seegmiller | C | validation | text-only | freecad | 15 | 13 | 13 | PASS | 15/15 | - |
| nist-am-test-artifact | B | validation | drawing-renders-sheet | build123d | 6 | 4 | 4 | PASS | 69/69 | - |
| nist-amb2022-01-bridge | B | validation | drawing-only | build123d | 14 | 11 | 11 | PASS | 14/14 | - |
| nist-amb2022-01-bridge | B | validation | mesh-input | freecad | 13 | 11 | 11 | PASS | 14/14 | - |
| nottingham-bearing | A | validation | paper-text | build123d | 1 | 1 | 0 | FAIL | 2/2 | - |
| peristaltic-pump | A | validation | published-parts | build123d | 2 | 2 | 0 | FAIL | 0/0 | - |
| planetary-set | C | validation | spec-only | build123d | 6 | 6 | 6 | PASS | 16/16 | - |
| prusa-mini-extruder-front | B | validation | renders-and-sheet | freecad | 27 | 18 | 6 | PASS | 33/33 | deviation_vs_prusa |
| prusa-mini-extruder-front-ecr1 | C | validation | ecr1 | build123d | 0 | 0 | 0 | not scored | - | - |
| rack-pinion | C | validation | spec-only | build123d | 6 | 6 | 6 | PASS | 8/8 | - |
| rpi5-enclosure | C | validation | requirements | build123d | 8 | 5 | 4 | PASS | 28/28 | - |
| rpi5-enclosure-ecr1 | C | validation | ecr1 | build123d | 5 | 4 | 4 | PASS | 28/28 | - |
| rpi5-enclosure-ecr2 | C | validation | ecr2 | build123d | 5 | 5 | 4 | PASS | 28/28 | - |
| rpi5-enclosure-ecr3 | C | validation | ecr3 | build123d | 5 | 4 | 4 | PASS | 36/36 | - |
| spleen-c1-blade | B | validation | table-and-notes | freecad | 15 | 12 | 11 | PASS | 12/12 | - |
| voron-sb-duct | B | validation | renders-sections-sheet | freecad | 17 | 14 | 5 | PASS | 21/21 | deviation_vs_voron |
| voron-sb-duct-ecr1 | C | validation | ecr1 | build123d | 0 | 0 | 0 | not scored | - | - |

### bearing-housing — spec-and-views

Cast bearing housing (oval flanged unit): 4 deg drafted flange and boss, r = 1 rounds, Ø47 x 14 counterbore over a Ø14 bore, two Ø10 mounting holes; one solid (fast regression). Source: build123d example "Cast Bearing Unit" (examples/cast_bearing_unit.py), housing body only; reference generated and frozen by scripts/derive_bearing_housing_truth.py with build123d 0.12.0 (accessed 2026-09-22, gumyr/build123d@cdaf1caa4c72436ebfe0907e1fb05e246d568cbc (2025-05-25)).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [98.35526277995001, 56.85526277995, 26.0] | [98.35526277995001, 56.85526277995001, 26.0] |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| volume | volume | yes | PASS | 46881.32942684002 | 46881.33406120509 |
| section_flange_z5p5 | section | yes | PASS | {"area": 3321.789209436761, "loops": 1, "holes": 3} |  |
| section_boss_z15 | section | yes | PASS | {"area": 632.4427242372717, "loops": 1, "holes": 1} |  |
| section_boss_z24 | section | yes | PASS | {"area": 525.1380171247033, "loops": 1, "holes": 1} |  |
| section_y0 | section | yes | PASS | {"area": 844.3613001874643, "loops": 4, "holes": 0} |  |
| bottom_face | face | yes | PASS | 1 | 3160.954 |
| counterbore_floor | face | yes | PASS | 1 | 1581.007 |
| flange_top_left | face | yes | PASS | 1 | 369.232 |
| flange_top_right | face | yes | PASS | 1 | 369.232 |
| boss_top | face | yes | PASS | 1 | 348.029 |
| draft_flat_pp | plane | yes | PASS | 311.5970393336434 | 311.44 |
| draft_flat_mp | plane | yes | PASS | 311.5970393336117 | 311.44 |
| draft_flat_mm | plane | yes | PASS | 311.5970393336008 | 311.437 |
| draft_flat_pm | plane | yes | PASS | 311.59703933363835 | 311.437 |
| counterbore | cylinder | yes | PASS | {"center": [0.0, 0.0, 19.0], "direction": [0.0, 0.0, 1.0], "radius": 23.5, "length": 14.0, "kind": "hole"} | {"point": [0.0, 0.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 23.5, "kind": "hole"} |
| through_bore | cylinder | yes | PASS | {"center": [0.0, 0.0, 6.0], "direction": [0.0, 0.0, 1.0], "radius": 7.0, "length": 12.0, "kind": "hole"} | {"point": [0.0, 0.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 7.0, "kind": "hole"} |
| mounting_hole_left | cylinder | yes | PASS | {"center": [-38.25, 0.0, 5.5], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "length": 11.0, "kind": "hole"} | {"point": [-38.25, 0.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "kind": "hole"} |
| mounting_hole_right | cylinder | yes | PASS | {"center": [38.25, 0.0, 5.5], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "length": 11.0, "kind": "hole"} | {"point": [38.25, 0.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "kind": "hole"} |
| material_solid | probe | yes | PASS | ["in", "in", "in", "in", "in", "in", "in"] | solid |
| openings_void | probe | yes | PASS | ["out", "out", "out", "out", "out", "out", "out"] | void |
| deviation | deviation | no | PASS | {"p95": 0.04953088894372226, "hausdorff_estimate": 0.14982982388064317, "silhouette_iou_min": 0.9988746095765745, "vo... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `06343576c3f45aad`; manifest `2493ff3e0aae1bf1`.

Attempts: 2026-09-23T01:58 reached scored, scorecard PASS; 2026-09-23T02:40 reached scored, scorecard PASS; 2026-09-23T03:12 reached scored, scorecard PASS; 2026-09-23T05:52 reached scored, scorecard PASS; 2026-09-23T06:22 reached scored, scorecard PASS; 2026-09-23T07:05 reached scored, scorecard PASS; 2026-09-23T07:31 reached scored, scorecard PASS; 2026-09-23T08:53 reached scored, scorecard PASS; 2026-09-23T09:41 reached scored, scorecard PASS; 2026-09-23T10:03 reached scored, scorecard PASS; 2026-09-23T14:49 reached scored, scorecard PASS; 2026-09-23T15:32 reached scored, scorecard PASS; 2026-09-23T16:06 reached scored, scorecard PASS; 2026-09-23T17:51 reached scored, scorecard PASS; 2026-09-23T18:16 reached scored, scorecard PASS; 2026-09-23T18:50 reached scored, scorecard PASS; 2026-09-23T23:13 reached scored, scorecard PASS; 2026-09-23T23:55 reached scored, scorecard PASS; 2026-09-24T01:14 reached scored, scorecard PASS; 2026-09-24T02:13 reached scored, scorecard PASS; 2026-09-24T05:24 reached scored, scorecard PASS; 2026-09-24T06:15 reached scored, scorecard PASS; 2026-09-24T07:17 reached scored, scorecard PASS; 2026-09-24T14:10 reached scored, scorecard PASS; 2026-09-24T15:28 reached scored, scorecard PASS; 2026-09-24T15:59 reached scored, scorecard PASS; 2026-09-24T16:35 reached scored, scorecard PASS; 2026-09-24T17:14 reached scored, scorecard PASS; 2026-09-24T18:06 reached scored, scorecard PASS; 2026-09-24T20:26 reached published; 2026-09-24T20:33 reached scored, scorecard PASS; 2026-09-24T20:33 reached scored, scorecard PASS; 2026-09-24T20:33 reached scored, scorecard PASS; 2026-09-24T23:13 reached published; 2026-09-24T23:20 reached scored, scorecard PASS; 2026-09-24T23:20 reached scored, scorecard PASS; 2026-09-24T23:20 reached scored, scorecard PASS; 2026-09-25T18:38 reached published; 2026-09-25T18:46 reached scored, scorecard PASS; 2026-09-25T18:46 reached scored, scorecard PASS; 2026-09-25T18:46 reached scored, scorecard PASS

### chiral-keyplate — text-only

Square key plate with four identical rectangular slots in a C4 pinwheel: volume, bbox and COM are mirror-invariant; the pattern is not. Source: opencad calibration fixture (no external publisher); geometry defined by inputs/chiral-keyplate-spec.md (accessed 2026-09-16, class D self-consistency; truth built by scripts/derive_chiral_truth.py).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [80.0, 80.0, 8.0] | [80, 80, 8] |
| volume | volume | yes | PASS | 49664.0 | 49664.0 |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| center_of_mass | center_of_mass | yes | PASS | [-6.409534987526676e-17, -6.867358915207154e-17, 3.9381443298969083] | [6.867358915207154e-18, -5.493887132165723e-17, 3.9381443298969083] |
| below_slots | section | yes | PASS | {"area": 6399.999999999999, "loops": 1, "holes": 0} |  |
| through_slots | section | yes | PASS | {"area": 6015.999999999999, "loops": 1, "holes": 4} |  |
| slot_a_floor | face | yes | PASS | 1 | 96.0 |
| slot_b_floor | face | yes | PASS | 1 | 96.0 |
| slot_c_floor | face | yes | PASS | 1 | 96.0 |
| slot_d_floor | face | yes | PASS | 1 | 96.0 |
| plate_bottom | face | yes | PASS | 1 | 6400.0 |
| plate_top | face | yes | PASS | 1 | 6016.0 |
| deviation_vs_truth | deviation | yes | PASS | {"p95": 2.5618982671915014e-14, "hausdorff_estimate": 2.480000278066503e-12, "silhouette_iou_min": 1.0, "volume_ratio... |  |
| not_matching_mirror | not_matching | yes | PASS | {"p95": 2.0820021003749134, "hausdorff_estimate": 4.0, "silhouette_iou_min": 1.0, "volume_ratio": 1.0} |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `7e8c29620ec51794`; manifest `882831f9f4026f7f`.

Attempts: 2026-09-16T08:46 reached scored, scorecard PASS; 2026-09-20T05:44 reached pipeline; 2026-09-20T05:44 reached pipeline; 2026-09-20T05:44 reached scored, scorecard PASS; 2026-09-20T05:52 reached scored, scorecard PASS; 2026-09-20T05:52 reached scored, scorecard PASS

### compound-train — spec-only

Compound spur-gear train as an assembly: pinion, compound idler and output gear on a base plate, two meshes, ratio +1/6. Source: Analytic mechanism reference (scripts/derive_mechanism_truth.py); tooth counts, module and phases from the specification (accessed 2026-09-25, spec v1).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [195.0, 100.0, 21.5] | [195.0, 100.0, 21.5] |
| solid_count | solid_count | yes | PASS | 4 | 4 |
| plate | solid | yes | PASS | {"volume": 96855.97350601408, "bbox_min": [-25.0, -50.0, -5.0], "bbox_max": [170.0, 50.0, 0.0], "center_of_mass": [72... |  |
| pinion | solid | yes | PASS | {"volume": 9545.55466679259, "bbox_min": [-22.0, -22.0, 0.0], "bbox_max": [22.0, 22.0, 8.0], "center_of_mass": [9.552... |  |
| idler | solid | yes | PASS | {"volume": 44413.27742474177, "bbox_min": [18.078254474050013, -41.921745525949994, 0.0], "bbox_max": [101.9217455259... |  |
| output | solid | yes | PASS | {"volume": 50031.01595609869, "bbox_min": [73.01820193733883, -46.99882371801393, 8.5], "bbox_max": [166.997468832482... |  |
| pinion_teeth | teeth | yes | PASS | 20 | 20 |
| idler_large_teeth | teeth | yes | PASS | 40 | 40 |
| idler_small_teeth | teeth | yes | PASS | 15 | 15 |
| output_teeth | teeth | yes | PASS | 45 | 45 |
| idler_bore | cylinder | yes | PASS | {"center": [60.0, 0.0, 8.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 16.0, "kind": "hole"} | {"point": [60.0, 0.0, 8.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "kind": "hole"} |
| output_bore | cylinder | yes | PASS | {"center": [120.0, 0.0, 12.5], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 8.0, "kind": "hole"} | {"point": [120.0, 0.0, 12.5], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "kind": "hole"} |
| first_mesh | gear_mesh | yes | PASS | {"max_interference": 0.0, "gap_min": 0.04774079317521846, "gap_max": 0.050552932272562356} | {"interference": 0.0, "backlash_max": 0.15} |
| second_mesh | gear_mesh | yes | PASS | {"max_interference": 0.0, "gap_min": 0.04711843137823647, "gap_max": 0.048254074732540314} | {"interference": 0.0, "backlash_max": 0.15} |

Pipeline gates: {'ok': True, 'summary': '10 pass, 0 fail, 4 n/a', 'failed': []}. STEP sha256 `6ce066893abb44cc`; manifest `d8d2498c461c5a25`.

Attempts: 2026-09-26T00:28 reached scored, scorecard PASS; 2026-09-26T01:59 reached scored, scorecard PASS; 2026-09-26T05:43 reached scored, scorecard PASS; 2026-09-26T07:38 reached scored, scorecard PASS; 2026-09-27T08:12 reached scored, scorecard PASS; 2026-09-27T16:22 reached scored, scorecard PASS

### crank-slider — spec-only

Offset crank-slider as an assembly: ground, crank, connecting rod and slider closed into one loop. Source: Analytic mechanism reference (scripts/derive_mechanism_truth.py); x = r cos t + sqrt(l^2 - (e - r sin t)^2) (accessed 2026-09-25, spec v1).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [200.0, 70.0, 15.0] | [200.0, 70.0, 15.0] |
| solid_count | solid_count | yes | PASS | 4 | 4 |
| ground | solid | yes | PASS | {"volume": 69858.62833058844, "bbox_min": [-40.0, -30.0, -5.0], "bbox_max": [160.0, 40.0, 0.0], "center_of_mass": [60... |  |
| crank | solid | yes | PASS | {"volume": 3122.5663106202464, "bbox_min": [-8.0, -8.0, 0.0], "bbox_max": [38.0, 8.0, 5.0], "center_of_mass": [14.999... |  |
| rod | solid | yes | PASS | {"volume": 8722.563840805076, "bbox_min": [22.0, -8.0, 5.0], "bbox_max": [137.49874371070845, 17.99999999953785, 10.0... |  |
| slider | solid | yes | PASS | {"volume": 2258.628330588459, "bbox_min": [114.498743711, 2.0, 0.0], "bbox_max": [144.498743711, 18.0, 5.0], "center_... |  |
| crank_pin_hole | cylinder | yes | PASS | {"center": [30.0, 0.0, 2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 5.0, "kind": "hole"} | {"point": [30.0, 0.0, 2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |
| rod_wrist_hole | cylinder | yes | PASS | {"center": [129.49874371070845, 9.999999999537849, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 5.0, ... | {"point": [129.498744, 10.0, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |
| slider_hole | cylinder | yes | PASS | {"center": [129.498743711, 10.0, 2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 5.0, "kind": "hole"} | {"point": [129.498744, 10.0, 2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |

Pipeline gates: {'ok': True, 'summary': '10 pass, 0 fail, 4 n/a', 'failed': []}. STEP sha256 `7695c9dac2558610`; manifest `5b7308052bde98d5`.

Attempts: 2026-09-26T00:28 reached scored, scorecard PASS; 2026-09-26T01:59 reached scored, scorecard PASS; 2026-09-26T05:43 reached scored, scorecard PASS; 2026-09-26T07:38 reached scored, scorecard PASS; 2026-09-27T08:12 reached scored, scorecard PASS; 2026-09-27T16:22 reached scored, scorecard PASS

### disc-brake — construction-steps

COMSOL 6.3 heat generation in a disc brake: disc and pad as an assembly, transient braking heat. Source: COMSOL Multiphysics 6.3 Application Library, Heat Transfer Module: Heat Generation in a Disc Brake (brake_disc) (accessed 2026-09-25, 6.3).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [280.0, 280.0, 23.0] | [280.0, 280.0, 23.0] |
| solid_count | solid_count | yes | PASS | 2 | 2 |
| disc | solid | yes | PASS | {"volume": 1001539.7379644258, "bbox_min": [-140.0, -140.0, 0.0], "bbox_max": [140.0, 140.0, 23.0], "center_of_mass":... |  |
| pad | solid | yes | PASS | {"volume": 23038.509745229527, "bbox_min": [-44.69422649660599, 88.0246912580247, 12.999999899999999], "bbox_max": [4... |  |
| disc_rim | cylinder | yes | PASS | {"center": [0.0, 0.0, 6.5], "direction": [0.0, 0.0, 1.0], "radius": 140.0, "length": 13.0, "kind": "pin"} | {"point": [0.0, 0.0, 6.5], "direction": [0.0, 0.0, 1.0], "radius": 140.0, "kind": "pin"} |
| hub | cylinder | yes | PASS | {"center": [0.0, 0.0, 18.0], "direction": [0.0, 0.0, 1.0], "radius": 80.0, "length": 10.0, "kind": "pin"} | {"point": [0.0, 0.0, 18.0], "direction": [0.0, 0.0, 1.0], "radius": 80.0, "kind": "pin"} |
| pad_contact | face | yes | PASS | 1 | 3544.37 |
| pad_top | face | yes | PASS | 1 | 3544.37 |
| hub_top | face | yes | PASS | 1 | 20106.19 |
| section_z16 | section | yes | PASS | {"area": 23650.583368033127, "loops": 2, "holes": 0} |  |
| pad_on_disc | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": 0.05} |

Pipeline gates: {'ok': True, 'summary': '13 pass, 0 fail, 1 n/a', 'failed': []}. STEP sha256 `907ccfa08112ca98`; manifest `c5146b5d8e50adc9`.

Downstream targets (not scored by CAD): fade_margin_K = 600.0 K (braking power starts to fade above 600 K (text))

Attempts: 2026-09-25T08:18 reached scored, scorecard FAIL; 2026-09-25T11:13 reached scored, scorecard FAIL

### enclosure-base — spec-and-views

Enclosure base (CadQuery parametric enclosure, lower body): open 100 x 150 x 47 box, 3 mm walls and floor, four hollow Ø10/Ø4 screw posts with blind bores; one solid (fast regression). Source: CadQuery documentation example "A Parametric Enclosure", base body only (published default parameters, split 4 mm below the top, lower body selected by position); reference generated and frozen by scripts/derive_enclosure_base_truth.py with CadQuery 2.8.0 (accessed 2026-09-22, CadQuery/cadquery@17846d631e26e8deee0fee43bd6daa1c5c5dbee2 (2023-10-22)).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [100.0, 150.0, 47.0] | [100.0, 150.0, 47.0] |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| volume | volume | yes | PASS | 118431.48123442396 | 118431.4812348242 |
| section_mid_z25 | section | yes | PASS | {"area": 1684.1150082347629, "loops": 5, "holes": 5} |  |
| section_floor_z1p5 | section | yes | PASS | {"area": 14883.508093207733, "loops": 1, "holes": 0} |  |
| section_posts_x38 | section | yes | PASS | {"area": 1240.2831853071796, "loops": 1, "holes": 0} |  |
| bottom_face | face | yes | PASS | 1 | 13961.062 |
| cavity_floor | face | yes | PASS | 1 | 13179.779 |
| bore_floor_pp | face | yes | PASS | 1 | 12.566 |
| bore_floor_mp | face | yes | PASS | 1 | 12.566 |
| bore_floor_mm | face | yes | PASS | 1 | 12.566 |
| bore_floor_pm | face | yes | PASS | 1 | 12.566 |
| rim | face | yes | PASS | 1 | 1420.221 |
| bore_pp | cylinder | yes | PASS | {"center": [38.0, 63.0, 25.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 44.0, "kind": "hole"} | {"point": [38.0, 63.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "hole"} |
| bore_mp | cylinder | yes | PASS | {"center": [-38.0, 63.0, 25.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 44.0, "kind": "hole"} | {"point": [-38.0, 63.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "hole"} |
| bore_mm | cylinder | yes | PASS | {"center": [-38.0, -63.0, 25.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 44.0, "kind": "hole"} | {"point": [-38.0, -63.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "hole"} |
| bore_pm | cylinder | yes | PASS | {"center": [38.0, -63.0, 25.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 44.0, "kind": "hole"} | {"point": [38.0, -63.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "hole"} |
| post_pp | cylinder | yes | PASS | {"center": [38.0, 63.0, 25.0], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "length": 44.0, "kind": "pin"} | {"point": [38.0, 63.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "kind": "pin"} |
| post_mp | cylinder | yes | PASS | {"center": [-38.0, 63.0, 25.0], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "length": 44.0, "kind": "pin"} | {"point": [-38.0, 63.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "kind": "pin"} |
| post_mm | cylinder | yes | PASS | {"center": [-38.0, -63.0, 25.0], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "length": 44.0, "kind": "pin"} | {"point": [-38.0, -63.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "kind": "pin"} |
| post_pm | cylinder | yes | PASS | {"center": [38.0, -63.0, 25.0], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "length": 44.0, "kind": "pin"} | {"point": [38.0, -63.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "kind": "pin"} |
| material_solid | probe | yes | PASS | ["in", "in", "in", "in", "in", "in", "in"] | solid |
| openings_void | probe | yes | PASS | ["out", "out", "out", "out", "out", "out", "out"] | void |
| min_wall | thickness | yes | PASS | {"min": 2.9903187988371607, "p01": 2.994513517496119, "p05": 2.9994458084863065, "p50": 3.0000000000000004} | {"min": 2.9} |
| deviation | deviation | no | PASS | {"p95": 0.004695427616466572, "hausdorff_estimate": 0.02036252442888369, "silhouette_iou_min": 0.9999744810863214, "v... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `904a0a9ac7207959`; manifest `9504b81de4992440`.

Attempts: 2026-09-23T03:42 reached scored, scorecard PASS; 2026-09-23T04:04 reached scored, scorecard PASS; 2026-09-23T04:34 reached scored, scorecard PASS; 2026-09-23T07:54 reached scored, scorecard PASS; 2026-09-23T08:13 reached scored, scorecard PASS; 2026-09-23T08:30 reached scored, scorecard PASS; 2026-09-23T10:23 reached scored, scorecard PASS; 2026-09-23T10:45 reached scored, scorecard PASS; 2026-09-23T11:03 reached scored, scorecard PASS; 2026-09-23T16:30 reached scored, scorecard PASS; 2026-09-23T16:45 reached scored, scorecard PASS; 2026-09-23T17:03 reached scored, scorecard PASS; 2026-09-23T19:08 reached scored, scorecard PASS; 2026-09-23T19:24 reached scored, scorecard PASS; 2026-09-23T19:40 reached scored, scorecard PASS; 2026-09-23T23:34 reached scored, scorecard PASS; 2026-09-24T00:05 reached scored, scorecard PASS; 2026-09-24T01:55 reached scored, scorecard PASS; 2026-09-24T02:33 reached scored, scorecard PASS; 2026-09-24T05:42 reached scored, scorecard PASS; 2026-09-24T06:34 reached scored, scorecard PASS; 2026-09-24T15:09 reached scored, scorecard PASS; 2026-09-24T15:47 reached scored, scorecard PASS; 2026-09-24T16:20 reached scored, scorecard PASS; 2026-09-24T16:51 reached scored, scorecard PASS; 2026-09-24T17:39 reached scored, scorecard PASS; 2026-09-24T18:36 reached scored, scorecard PASS; 2026-09-24T20:26 reached published; 2026-09-24T20:34 reached scored, scorecard PASS; 2026-09-24T20:34 reached scored, scorecard PASS; 2026-09-24T20:34 reached scored, scorecard PASS; 2026-09-24T23:13 reached published; 2026-09-24T23:20 reached scored, scorecard PASS; 2026-09-24T23:20 reached scored, scorecard PASS; 2026-09-24T23:20 reached scored, scorecard PASS; 2026-09-25T18:38 reached published; 2026-09-25T18:45 reached scored, scorecard PASS; 2026-09-25T18:45 reached scored, scorecard PASS; 2026-09-25T18:45 reached scored, scorecard PASS

### fan-01 — supplied-cad

FAN-01 low-pressure axial fan in its short duct: rotor, duct and flow domain; total-to-static pressure rise on the characteristic. Source: FAN-01 benchmark (Zenger, Junger, Kaltenbacher, Becker; Zenodo record 10787093 v4), Schoder and Czwielong 2022 arXiv:2211.12014 (accessed 2026-09-25, v4 (2024-03-06)).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| rotor | solid | yes | PASS | {"volume": 1176101.6951063105, "bbox_min": [-643.6053682208604, -421.00000009995756, 1269.864418592224], "bbox_max": ... |  |
| duct | solid | yes | PASS | {"volume": 3481742.027737341, "bbox_min": [-725.0, -510.0000036, 1190.0], "bbox_max": [-74.99999999999994, -135.99992... |  |

Pipeline gates: {'ok': False, 'summary': '11 pass, 1 fail, 2 n/a', 'failed': ['refinement']}. STEP sha256 `35a341b57ee42f8a`; manifest `df5a0aa8022dd49e`.

Attempts: 2026-09-26T07:37 reached scored, scorecard FAIL; 2026-09-26T12:25 reached scored, scorecard FAIL; 2026-09-27T20:52 reached scored, scorecard FAIL

### fda-pump — supplied-cad

FDA benchmark centrifugal blood pump (Interlaboratory Study 2): assembly, sealed flow domain and pressure rise per operating condition. Source: FDA/OSEL-DAM CFD and Blood Damage Benchmarks, Blood Pump (Malinauskas et al. 2017 ASAIO J 63:150; Hariharan et al. 2018 CVET 9:623; Ponnaluri et al. 2022 ASAIO J 69:e1) (accessed 2026-09-25, ca35ecc44137fa6bd0d735190eb836ea0dc0d547).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| rotor | solid | yes | PASS | {"volume": 9768.403890346883, "bbox_min": [-26.00000009999522, -26.00000009999277, 0.0], "bbox_max": [26.000000099997... |  |
| flowDomain | solid | yes | PASS | {"volume": 78329.70784420539, "bbox_min": [-30.0000001, -33.8, -1e-07], "bbox_max": [245.0, 30.0000001, 300.0], "cent... |  |

Pipeline gates: {'ok': False, 'summary': '11 pass, 1 fail, 2 n/a', 'failed': ['refinement']}. STEP sha256 `f6997f5cdf57bdae`; manifest `7dd995e916d5d5dc`.

Attempts: 2026-09-25T08:56 reached scored, scorecard FAIL; 2026-09-25T11:11 reached scored, scorecard FAIL; 2026-09-26T07:24 reached scored, scorecard FAIL; 2026-09-27T16:10 reached scored, scorecard FAIL

### four-bar — spec-only

Planar four-bar crank-rocker as an assembly: ground, crank, coupler and rocker closed into one loop. Source: Analytic mechanism reference (scripts/derive_mechanism_truth.py); circle intersection on the assembled branch (accessed 2026-09-25, spec v1).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [160.0, 118.0, 20.0] | [160.0, 118.0, 20.0] |
| solid_count | solid_count | yes | PASS | 4 | 4 |
| ground | solid | yes | PASS | {"volume": 47717.256661176914, "bbox_min": [-30.0, -30.0, -5.0], "bbox_max": [130.0, 30.0, 0.0], "center_of_mass": [5... |  |
| crank | solid | yes | PASS | {"volume": 3922.565322047687, "bbox_min": [-8.0, -8.0, 0.0], "bbox_max": [48.0, 8.0, 5.0], "center_of_mass": [19.9999... |  |
| coupler | solid | yes | PASS | {"volume": 8722.563840805078, "bbox_min": [32.0, -8.0, 5.0], "bbox_max": [108.0, 88.0, 10.0], "center_of_mass": [69.9... |  |
| rocker | solid | yes | PASS | {"volume": 7122.564334552614, "bbox_min": [92.0, -8.0, 10.0], "bbox_max": [108.0, 88.0, 15.0], "center_of_mass": [99.... |  |
| crank_pin_hole | cylinder | yes | PASS | {"center": [40.0, 0.0, 2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 5.0, "kind": "hole"} | {"point": [40.0, 0.0, 2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |
| coupler_far_hole | cylinder | yes | PASS | {"center": [100.0, 80.0, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 5.0, "kind": "hole"} | {"point": [100.0, 80.0, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |
| rocker_pivot_hole | cylinder | yes | PASS | {"center": [100.0, 0.0, 12.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 5.0, "kind": "hole"} | {"point": [100.0, 0.0, 12.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |
| ground_rocker_hole | cylinder | yes | PASS | {"center": [100.0, 0.0, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 5.0, "kind": "hole"} | {"point": [100.0, 0.0, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |

Pipeline gates: {'ok': True, 'summary': '9 pass, 0 fail, 5 n/a', 'failed': []}. STEP sha256 `754afbab5ee1c7c4`; manifest `eda2343bfb8bdece`.

Attempts: 2026-09-26T00:28 reached scored, scorecard PASS; 2026-09-26T01:59 reached scored, scorecard PASS; 2026-09-26T05:43 reached scored, scorecard PASS; 2026-09-26T07:38 reached scored, scorecard PASS; 2026-09-27T08:12 reached scored, scorecard PASS; 2026-09-27T16:22 reached scored, scorecard PASS

### fusion-01184-recon — renders-and-sheet

Held-out Fusion 360 Gallery body 36938_ae684b66_0002_2 (joint set joint_set_01184): reconstruction. Source: Autodesk AI Lab, Fusion 360 Gallery Dataset, Assembly-Joint subset j1.0.0 (Willis et al., JoinABLe, CVPR 2022) (accessed 2026-09-17, j1.0.0).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [10.000000199999988, 88.0000001, 50.00000019999999] | [10.0, 88.0, 50.0] |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| volume | volume | yes | PASS | 4863.73264713257 | 4863.73329938278 |
| center_of_mass | center_of_mass | yes | PASS | [105.0000000003052, 18.855719031939387, 95.00000000002015] | [105.00000045477397, 18.855721361457622, 95.00000045947311] |
| hole_d5_105_5_95 | cylinder | yes | PASS | {"center": [105.0, 5.0, 95.0], "direction": [0.0, 0.0, 1.0], "radius": 2.5, "length": 50.0, "kind": "hole"} | {"point": [105.0, 5.0, 95.0], "direction": [0.0, 0.0, 1.0], "radius": 2.5, "kind": "hole"} |
| pin_d8_104_4_95 | cylinder | yes | PASS | {"center": [104.0, 4.0, 95.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 50.0, "kind": "pin"} | {"point": [104.0, 4.0, 95.0], "direction": [-0.0, -0.0, 1.0], "radius": 4.0, "kind": "pin"} |
| pin_d8_104_6_95 | cylinder | yes | PASS | {"center": [104.0, 6.0, 95.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 50.0, "kind": "pin"} | {"point": [104.0, 6.0, 95.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "kind": "pin"} |
| pin_d8_106_4_95 | cylinder | yes | PASS | {"center": [106.0, 4.0, 95.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 50.0, "kind": "pin"} | {"point": [106.0, 4.0, 95.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "kind": "pin"} |
| pin_d8_106_6_95 | cylinder | yes | PASS | {"center": [106.0, 6.0, 95.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 50.0, "kind": "pin"} | {"point": [106.0, 6.0, 95.0], "direction": [-0.0, -0.0, 1.0], "radius": 4.0, "kind": "pin"} |
| pin_d5_105_48p9_95 | cylinder | yes | PASS | {"center": [105.0, 48.854049621774, 95.0], "direction": [-0.0, 1.0, -2.22044604925e-16], "radius": 2.5, "length": 78.... | {"point": [105.0, 48.8538, 95.0], "direction": [-0.0, 1.0, 0.0], "radius": 2.5, "kind": "pin"} |
| face_zp_120 | face | yes | PASS | 1 | 66.631 |
| face_yn_0 | face | yes | PASS | 1 | 100.0 |
| face_yp_10 | face | yes | PASS | 2 | 90.273 |
| face_yp_88 | face | yes | PASS | 1 | 19.635 |
| face_xp_110 | face | yes | PASS | 1 | 100.0 |
| face_xn_100 | face | yes | PASS | 1 | 100.0 |
| face_zn_70 | face | yes | PASS | 1 | 66.631 |
| deviation | deviation | yes | PASS | {"p95": 0.007391089262899599, "hausdorff_estimate": 0.009317237074144426, "silhouette_iou_min": 0.9967427730276551, "... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `1e151dd4f56145a7`; manifest `8841416b37b7522d`.

Attempts: 2026-09-19T05:50 reached scored, scorecard PASS; 2026-09-20T10:20 reached pipeline; 2026-09-20T10:20 reached pipeline; 2026-09-20T10:20 reached scored, scorecard PASS; 2026-09-20T10:31 reached scored, scorecard PASS; 2026-09-20T10:31 reached scored, scorecard PASS

### fusion-12944-recon — renders-and-sheet

Held-out Fusion 360 Gallery body 22303_e9723631_0014_1 (joint set joint_set_12944): reconstruction. Source: Autodesk AI Lab, Fusion 360 Gallery Dataset, Assembly-Joint subset j1.0.0 (Willis et al., JoinABLe, CVPR 2022) (accessed 2026-09-17, j1.0.0).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [126.70198518078092, 15.000000206000703, 108.0] | [126.7014, 15.0, 108.0] |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| volume | volume | yes | PASS | 148055.58174867477 | 148190.97607994877 |
| center_of_mass | center_of_mass | yes | PASS | [5.343706022383419e-07, 7.553316516397358, 1.5533584661085496e-09] | [1.4053035411080966e-06, 7.55359264327638, 1.3152875586324587e-07] |
| hole_d174_m141_7p5_m3p53em14 | cylinder | yes | PASS | {"center": [-141.0, 7.5, 0.0], "direction": [-0.0, 1.0, -0.0], "radius": 87.0, "length": 15.0, "kind": "hole"} | {"point": [-141.0, 7.5, -0.0], "direction": [0.0, 1.0, 0.0], "radius": 87.0, "kind": "hole"} |
| hole_d174_141_7p5_m1p84em13 | cylinder | yes | PASS | {"center": [141.0, 7.5, 0.0], "direction": [-0.0, 1.0, -0.0], "radius": 87.0, "length": 15.0, "kind": "hole"} | {"point": [141.0, 7.5, -0.0], "direction": [0.0, 1.0, 0.0], "radius": 87.0, "kind": "hole"} |
| hole_d18_0_7p5_0 | cylinder | yes | PASS | {"center": [0.0, 7.5, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 9.0, "length": 15.0, "kind": "hole"} | {"point": [0.0, 7.5, 0.0], "direction": [-0.0, 1.0, -0.0], "radius": 9.0, "kind": "hole"} |
| hole_d10_m51p4_9p5_m42 | cylinder | yes | PASS | {"center": [-51.351, 9.5, -42.0], "direction": [0.0, 1.0, 0.0], "radius": 5.0, "length": 11.0, "kind": "hole"} | {"point": [-51.3507, 9.5, -42.0], "direction": [-0.0, 1.0, -0.0], "radius": 5.0, "kind": "hole"} |
| hole_d10_m51p4_9p5_42 | cylinder | yes | PASS | {"center": [-51.351, 9.5, 42.0], "direction": [0.0, 1.0, 0.0], "radius": 5.0, "length": 11.0, "kind": "hole"} | {"point": [-51.3507, 9.5, 42.0], "direction": [-0.0, 1.0, -0.0], "radius": 5.0, "kind": "hole"} |
| hole_d10_51p4_9p5_m42 | cylinder | yes | PASS | {"center": [51.351, 9.5, -42.0], "direction": [0.0, 1.0, 0.0], "radius": 5.0, "length": 11.0, "kind": "hole"} | {"point": [51.3507, 9.5, -42.0], "direction": [-0.0, 1.0, -0.0], "radius": 5.0, "kind": "hole"} |
| hole_d10_51p4_9p5_42 | cylinder | yes | PASS | {"center": [51.351, 9.5, 42.0], "direction": [0.0, 1.0, 0.0], "radius": 5.0, "length": 11.0, "kind": "hole"} | {"point": [51.3507, 9.5, 42.0], "direction": [-0.0, 1.0, -0.0], "radius": 5.0, "kind": "hole"} |
| pin_d24_51p4_7p5_m42 | cylinder | yes | PASS | {"center": [51.351, 7.5, -42.0], "direction": [-0.0, 1.0, -0.0], "radius": 12.0, "length": 15.0, "kind": "pin"} | {"point": [51.3507, 7.5, -42.0], "direction": [0.0, 1.0, 0.0], "radius": 12.0, "kind": "pin"} |
| pin_d24_m51p4_7p5_m42 | cylinder | yes | PASS | {"center": [-51.351, 7.5, -42.0], "direction": [-0.0, 1.0, -0.0], "radius": 12.0, "length": 15.0, "kind": "pin"} | {"point": [-51.3507, 7.5, -42.0], "direction": [0.0, 1.0, 0.0], "radius": 12.0, "kind": "pin"} |
| pin_d24_m51p4_7p5_42 | cylinder | yes | PASS | {"center": [-51.351, 7.5, 42.0], "direction": [-0.0, 1.0, -0.0], "radius": 12.0, "length": 15.0, "kind": "pin"} | {"point": [-51.3507, 7.5, 42.0], "direction": [0.0, 1.0, 0.0], "radius": 12.0, "kind": "pin"} |
| pin_d24_51p4_7p5_42 | cylinder | yes | PASS | {"center": [51.351, 7.5, 42.0], "direction": [-0.0, 1.0, -0.0], "radius": 12.0, "length": 15.0, "kind": "pin"} | {"point": [51.3507, 7.5, 42.0], "direction": [0.0, 1.0, 0.0], "radius": 12.0, "kind": "pin"} |
| face_yn_0 | face | yes | PASS | 2 | 5952.327 |
| face_yn_3 | face | yes | PASS | 1 | 4156.327 |
| face_yp_12 | face | yes | PASS | 1 | 4156.327 |
| face_yp_15 | face | yes | PASS | 2 | 6656.044 |
| face_zp_54 | face | yes | PASS | 1 | 1540.52 |
| face_zn_m54 | face | yes | PASS | 1 | 1540.52 |
| deviation | deviation | yes | PASS | {"p95": 0.06313792212765211, "hausdorff_estimate": 0.32198293557187707, "silhouette_iou_min": 0.9994993304471675, "vo... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `499fbe7cc2d5faa1`; manifest `e67395e2f821ff88`.

Attempts: 2026-09-19T05:50 reached scored, scorecard PASS; 2026-09-20T11:40 reached pipeline; 2026-09-20T11:40 reached pipeline; 2026-09-20T11:40 reached scored, scorecard FAIL; 2026-09-20T11:57 reached scored, scorecard PASS; 2026-09-20T11:57 reached scored, scorecard FAIL; 2026-09-20T12:07 reached scored, scorecard FAIL; 2026-09-20T13:03 reached scored, scorecard PASS; 2026-09-20T13:09 reached scored, scorecard PASS

### fusion-13786-recon — renders-and-sheet

Held-out Fusion 360 Gallery body 84608_204c01e6_0008_1 (joint set joint_set_13786): reconstruction. Source: Autodesk AI Lab, Fusion 360 Gallery Dataset, Assembly-Joint subset j1.0.0 (Willis et al., JoinABLe, CVPR 2022) (accessed 2026-09-17, j1.0.0).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [100.0000002, 100.0000002, 3.0000001999999997] | [100.0, 100.0, 3.0] |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| volume | volume | yes | PASS | 25204.941045706237 | 25187.468083716412 |
| center_of_mass | center_of_mass | yes | PASS | [0.0024845520846599, -4.682432883970004, 1.5] | [-3.265091164744456e-05, -4.716323627791606, 1.5000000245412441] |
| hole_d5_0_0_1p5 | cylinder | yes | PASS | {"center": [0.0, 0.0, 1.5], "direction": [0.0, 0.0, 1.0], "radius": 2.5, "length": 3.0, "kind": "hole"} | {"point": [0.0, 0.0, 1.5], "direction": [-0.0, -0.0, 1.0], "radius": 2.5, "kind": "hole"} |
| hole_d2_0_42_1p5 | cylinder | yes | PASS | {"center": [0.0, 42.0, 1.500000000000011], "direction": [1.0, 0.0, 2.22044604925e-16], "radius": 1.0, "length": 100.0... | {"point": [0.0, 42.0, 1.5], "direction": [1.0, -0.0, -0.0], "radius": 1.0, "kind": "hole"} |
| pin_d6_m47_47_1p5 | cylinder | yes | PASS | {"center": [-47.0, 47.0, 1.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 3.0, "kind": "pin"} | {"point": [-47.0, 47.0, 1.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "pin"} |
| pin_d6_47_47_1p5 | cylinder | yes | PASS | {"center": [47.0, 47.0, 1.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 3.0, "kind": "pin"} | {"point": [47.0, 47.0, 1.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "pin"} |
| face_zn_0 | face | yes | PASS | 1 | 8331.096 |
| face_zp_3 | face | yes | PASS | 1 | 8331.096 |
| face_yn_m50 | face | yes | PASS | 1 | 270.0 |
| face_xp_50 | face | yes | PASS | 1 | 272.858 |
| face_xn_m50 | face | yes | PASS | 1 | 272.858 |
| face_yp_50 | face | yes | PASS | 1 | 282.0 |
| deviation | deviation | yes | PASS | {"p95": 2.7231366557152733e-12, "hausdorff_estimate": 0.2143902632609908, "silhouette_iou_min": 0.9996666663093958, "... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `a8c4f298b13e049f`; manifest `7784c30b4ed0b1d2`.

Attempts: 2026-09-19T05:50 reached scored, scorecard PASS; 2026-09-20T10:47 reached pipeline; 2026-09-20T10:47 reached pipeline; 2026-09-20T10:47 reached scored, scorecard PASS; 2026-09-20T10:50 reached scored, scorecard PASS; 2026-09-20T10:50 reached scored, scorecard PASS

### fusion-15317-recon — renders-and-sheet

Held-out Fusion 360 Gallery body 22337_e2f65ed2_0003_1 (joint set joint_set_15317): reconstruction. Source: Autodesk AI Lab, Fusion 360 Gallery Dataset, Assembly-Joint subset j1.0.0 (Willis et al., JoinABLe, CVPR 2022) (accessed 2026-09-17, j1.0.0).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [88.90000020000001, 32.54400009999999, 88.90000020000001] | [88.9, 32.544, 88.9] |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| volume | volume | yes | PASS | 93854.05844246075 | 93854.24814066986 |
| center_of_mass | center_of_mass | yes | PASS | [0.0038047406184234, 110.10063542723742, -0.0015032182389887305] | [0.003883648397225696, 110.09813198657827, -0.0014959663789264426] |
| hole_d11p1_0_118_18p9 | cylinder | yes | PASS | {"center": [4.000355602329364e-12, 118.139, 18.923], "direction": [1.0, 0.0, 0.0], "radius": 5.5565, "length": 84.785... | {"point": [0.0, 118.1392, 18.9234], "direction": [1.0, 0.0, 0.0], "radius": 5.5565, "kind": "hole"} |
| hole_d11p1_0_118_m19p1 | cylinder | yes | PASS | {"center": [0.0, 118.204, -19.05], "direction": [1.0, 0.0, 0.0], "radius": 5.5565, "length": 84.704851283736, "kind":... | {"point": [0.0, 118.2045, -19.05], "direction": [1.0, 0.0, 0.0], "radius": 5.5565, "kind": "hole"} |
| hole_d7p94_0_118_m19p1 | cylinder | yes | PASS | {"center": [0.0, 118.204, -19.05], "direction": [1.0, 0.0, 0.0], "radius": 3.969, "length": 71.4365, "kind": "hole"} | {"point": [0.0, 118.2045, -19.05], "direction": [1.0, -0.0, -0.0], "radius": 3.969, "kind": "hole"} |
| hole_d7p94_0_118_19p1 | cylinder | yes | PASS | {"center": [0.0, 118.204, 19.05], "direction": [1.0, 0.0, 0.0], "radius": 3.969, "length": 71.4365, "kind": "hole"} | {"point": [0.0, 118.2045, 19.05], "direction": [1.0, -0.0, -0.0], "radius": 3.969, "kind": "hole"} |
| pin_d88p9_0_116_0 | cylinder | yes | PASS | {"center": [0.0, 115.82300000000001, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 44.45, "length": 19.04999999999999... | {"point": [0.0, 115.8235, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 44.45, "kind": "pin"} |
| pin_d50p8_0_99p6_0 | cylinder | yes | PASS | {"center": [0.0, 99.551, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 25.4, "length": 13.494, "kind": "pin"} | {"point": [0.0, 99.5515, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 25.4, "kind": "pin"} |
| face_xp_m19p8 | face | yes | PASS | 3 | 867.763 |
| face_xp_36p5 | face | yes | PASS | 2 | 51.45 |
| face_xn_m36p5 | face | yes | PASS | 2 | 51.45 |
| face_xn_19p8 | face | yes | PASS | 3 | 867.763 |
| face_yn_92p8 | face | yes | PASS | 1 | 2026.83 |
| face_yn_104 | face | yes | PASS | 1 | 414.946 |
| face_yn_106 | face | yes | PASS | 1 | 4180.337 |
| face_yp_113 | face | yes | PASS | 1 | 3407.284 |
| face_yp_125 | face | yes | PASS | 2 | 2799.883 |
| deviation | deviation | yes | PASS | {"p95": 0.04304873314194202, "hausdorff_estimate": 0.5106082794635823, "silhouette_iou_min": 0.9988432757024275, "vol... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `009199c7d79dfb9c`; manifest `eeb1be53cccc1fea`.

Attempts: 2026-09-19T05:50 reached scored, scorecard PASS; 2026-09-20T13:13 reached pipeline; 2026-09-20T13:13 reached pipeline; 2026-09-20T13:13 reached scored, scorecard PASS; 2026-09-20T13:34 reached scored, scorecard PASS; 2026-09-20T13:34 reached scored, scorecard FAIL; 2026-09-20T13:39 reached scored, scorecard PASS

### fusion-16418-recon — renders-and-sheet

Held-out Fusion 360 Gallery body 23309_76dcf100_0002_1 (joint set joint_set_16418): reconstruction. Source: Autodesk AI Lab, Fusion 360 Gallery Dataset, Assembly-Joint subset j1.0.0 (Willis et al., JoinABLe, CVPR 2022) (accessed 2026-09-17, j1.0.0).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [20.483999999999998, 4.0, 20.483999999999998] | [20.4834, 4.0, 20.4834] |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| volume | volume | yes | PASS | 828.4609444397535 | 827.6532984081297 |
| center_of_mass | center_of_mass | yes | PASS | [7.357701694102293e-13, 1.5153825341551073, 1.822754541791158e-13] | [3.4823523950388154e-10, 1.515397544839943, 1.1887981364141823e-10] |
| hole_d3p1_0_0p5_0 | cylinder | yes | PASS | {"center": [0.0, 0.5, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 1.55, "length": 1.0, "kind": "hole"} | {"point": [0.0, 0.5, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 1.55, "kind": "hole"} |
| pin_d19_0_1p5_0 | cylinder | yes | PASS | {"center": [0.0, 1.5, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 9.499999999998, "length": 3.0, "kind": "pin"} | {"point": [0.0, 1.5, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 9.5, "kind": "pin"} |
| face_yp_1 | face | yes | PASS | 1 | 34.022 |
| face_yp_3 | face | yes | PASS | 1 | 233.367 |
| face_yp_4 | face | yes | PASS | 1 | 23.383 |
| face_yn_0 | face | yes | PASS | 1 | 290.771 |
| deviation | deviation | yes | PASS | {"p95": 0.006787646852399146, "hausdorff_estimate": 0.009588972315282475, "silhouette_iou_min": 0.9986838182820079, "... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `24c898ad726959d2`; manifest `f03ca1875cf4559b`.

Attempts: 2026-09-19T05:50 reached scored, scorecard PASS; 2026-09-20T13:40 reached pipeline; 2026-09-20T13:40 reached pipeline; 2026-09-20T13:40 reached scored, scorecard PASS; 2026-09-20T14:04 reached scored, scorecard PASS; 2026-09-20T14:04 reached scored, scorecard PASS

### gear-pair — spec-only

Spur-gear pair (20T/40T, m = 2, 20 deg) on a carrier plate: separate solids, tooth counts, involute profile, meshing motion. Source: Design specification authored for this benchmark; reference geometry generated independently by scripts/derive_gear_truth.py (numpy involute + OpenCascade) (accessed 2026-09-17, spec v1).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [126.92174552595046, 83.8434910519028, 13.0] | [126.92, 83.84, 13.0] |
| solid_count | solid_count | yes | PASS | 3 | 3 |
| pinion | solid | yes | PASS | {"volume": 9547.102403720215, "bbox_min": [-22.00000000000007, -22.00000000000007, 0.0], "bbox_max": [22.000000000000... |  |
| wheel | solid | yes | PASS | {"volume": 39388.64196866667, "bbox_min": [18.07825447404975, -41.92174552595, 0.0], "bbox_max": [101.92174552595046,... |  |
| carrier | solid | yes | PASS | {"volume": 27107.300918301276, "bbox_min": [-25.0, -25.0, -5.0], "bbox_max": [85.0, 25.0, 0.0], "center_of_mass": [29... |  |
| pinion_bore | cylinder | yes | PASS | {"center": [0.0, 0.0, 4.0], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 8.0, "kind": "hole"} | {"point": [0.0, 0.0, 4.0], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |
| wheel_bore | cylinder | yes | PASS | {"center": [60.0, 0.0, 4.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 8.0, "kind": "hole"} | {"point": [60.0, 0.0, 4.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "kind": "hole"} |
| carrier_pinion_hole | cylinder | yes | PASS | {"center": [0.0, 0.0, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 5.0, "kind": "hole"} | {"point": [0.0, 0.0, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |
| carrier_wheel_hole | cylinder | yes | PASS | {"center": [60.0, 0.0, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 5.0, "kind": "hole"} | {"point": [60.0, 0.0, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "kind": "hole"} |
| pinion_teeth | teeth | yes | PASS | 20 | 20 |
| wheel_teeth | teeth | yes | PASS | 40 | 40 |
| pinion_profile | profile2d | yes | PASS | {"area": 1222.168429855085, "chord": 44.00000000000736, "stagger_deg": 55.73809347487863, "bbox_min": [-21.9999931349... |  |
| gear_mesh | gear_mesh | yes | PASS | {"max_interference": 0.0, "gap_min": 0.046909546158536077, "gap_max": 0.04700777292882576} | {"interference": 0.0, "backlash_max": 0.15} |
| gears_separate | clearance | yes | PASS | {"gap": 0.04700777292690892, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": 0.15} |
| pinion_on_carrier | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": 0.05} |
| gear_tops | face | yes | PASS | 2 | null |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `815d18ddbcf34ec9`; manifest `999d906e78342ebb`.

Attempts: 2026-09-19T05:24 reached scored, scorecard PASS; 2026-09-20T08:53 reached pipeline; 2026-09-20T08:53 reached pipeline; 2026-09-20T10:03 reached scored, scorecard PASS; 2026-09-20T10:04 reached scored, scorecard PASS; 2026-09-20T10:04 reached scored, scorecard PASS; 2026-09-20T10:11 reached scored, scorecard PASS

### gear-train — spec-only

Spur-gear train as an assembly: pinion, wheel and carrier drafted and modelled as separate parts, placed on revolute joints, driven through the 2:1 mesh. Source: Machine version of the gear-pair case: same specification and the same independently generated reference geometry (scripts/derive_gear_truth.py) (accessed 2026-09-17, spec v1).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [126.92174552595043, 83.84349105190043, 13.0] | [126.92, 83.84, 13.0] |
| solid_count | solid_count | yes | PASS | 3 | 3 |
| pinion | solid | yes | PASS | {"volume": 9545.554666792588, "bbox_min": [-22.0, -22.0, 0.0], "bbox_max": [22.0, 22.0, 8.0], "center_of_mass": [9.54... |  |
| wheel | solid | yes | PASS | {"volume": 39384.06520919478, "bbox_min": [18.078254474050013, -41.921745525949994, 0.0], "bbox_max": [101.9217455259... |  |
| carrier | solid | yes | PASS | {"volume": 27107.300918301276, "bbox_min": [-25.0, -25.0, -5.0], "bbox_max": [85.0, 25.0, 0.0], "center_of_mass": [29... |  |
| pinion_bore | cylinder | yes | PASS | {"center": [0.0, 0.0, 4.0], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 8.0, "kind": "hole"} | {"point": [0.0, 0.0, 4.0], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |
| wheel_bore | cylinder | yes | PASS | {"center": [60.0, 0.0, 4.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 8.0, "kind": "hole"} | {"point": [60.0, 0.0, 4.0], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "kind": "hole"} |
| carrier_pinion_hole | cylinder | yes | PASS | {"center": [0.0, 0.0, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 5.0, "kind": "hole"} | {"point": [0.0, 0.0, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |
| carrier_wheel_hole | cylinder | yes | PASS | {"center": [60.0, 0.0, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 5.0, "kind": "hole"} | {"point": [60.0, 0.0, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "kind": "hole"} |
| pinion_teeth | teeth | yes | PASS | 20 | 20 |
| wheel_teeth | teeth | yes | PASS | 40 | 40 |
| pinion_profile | profile2d | yes | PASS | {"area": 1221.742975443881, "chord": 44.0000000000004, "stagger_deg": -55.73809347489584, "bbox_min": [-21.9999931349... |  |
| gear_mesh | gear_mesh | yes | PASS | {"max_interference": 0.0, "gap_min": 0.04774079317521846, "gap_max": 0.050552932272562356} | {"interference": 0.0, "backlash_max": 0.15} |
| gears_separate | clearance | yes | PASS | {"gap": 0.050552932272562356, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": 0.15} |
| pinion_on_carrier | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": 0.05} |
| gear_tops | face | yes | PASS | 2 | null |

Pipeline gates: {'ok': True, 'summary': '10 pass, 0 fail, 4 n/a', 'failed': []}. STEP sha256 `52379d8c2f4c4fd0`; manifest `5cf6b457f85f3084`.

Attempts: 2026-09-25T06:59 reached scored, scorecard PASS; 2026-09-25T09:49 reached scored, scorecard PASS; 2026-09-26T01:59 reached scored, scorecard PASS; 2026-09-26T05:43 reached scored, scorecard PASS; 2026-09-26T07:38 reached scored, scorecard PASS; 2026-09-27T08:12 reached scored, scorecard PASS; 2026-09-27T16:22 reached scored, scorecard PASS

### nasa-atb-axisymmetric-bump — text-and-points

NASA TMR axisymmetric transonic bump (Bachalo–Johnson): cylinder with a circular-arc bump and leading-edge fillet, revolved as one solid. Source: NASA Turbulence Modeling Resource, ATB: Axisymmetric Transonic Bump; Bachalo & Johnson, AIAA Journal 24(3), 1986, 437-443; surface points bumpgrd.surfpts_orig.dat (accessed 2026-09-16, TMR wording of 2024-09-03; surfpts from Axi_Bump_grids/bumpgrd.surfpts_orig.dat).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [1550.010233984, 190.50000010006008, 190.50000020006013] | [1550.010234, 190.5, 190.5] |
| volume | volume | yes | PASS | 29664295.533711348 | 29664339.610171862 |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| center_of_mass | center_of_mass | yes | PASS | [123.82903199366561, -0.02365412118874145, -0.027054032844969995] | [123.82900362633464, -0.050850250495143745, -7.327277394486154e-15] |
| upstream_disk | section | yes | PASS | {"area": 18241.469247509922, "loops": 1, "holes": 0} |  |
| crest_disk | section | yes | PASS | {"area": 28502.229947925833, "loops": 1, "holes": 0} |  |
| downstream_disk | section | yes | PASS | {"area": 18241.469247509922, "loops": 1, "holes": 0} |  |
| inlet_cap | face | yes | PASS | 1 | 18241.47 |
| outlet_cap | face | yes | PASS | 1 | 18241.47 |
| meridian | profile2d | yes | PASS | {"area": 241504.06423730202, "chord": null, "stagger_deg": null, "bbox_min": [-650.0073203536, -95.2499980977099], "b... |  |
| deviation_vs_truth | deviation | yes | PASS | {"p95": 0.021514387166126997, "hausdorff_estimate": 0.049996833463416934, "silhouette_iou_min": 0.9994893738333861, "... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `155d6a4edb15bf5c`; manifest `287052dbb9eb5fb6`.

Attempts: 2026-09-16T09:36 reached scored, scorecard PASS; 2026-09-20T05:52 reached pipeline; 2026-09-20T05:52 reached pipeline; 2026-09-20T05:52 reached scored, scorecard PASS; 2026-09-20T06:07 reached scored, scorecard PASS; 2026-09-20T06:07 reached scored, scorecard PASS

### nasa-backstep-driver-seegmiller — text-only

Driver-Seegmiller backward-facing step: flow-passage (air volume) solid, parallel-roof case, NASA WIND computational domain. Source: NASA Glenn Research Center, WIND-US validation archive, Backstep Study #1 (D. A. Yoder); Driver & Seegmiller, AIAA Journal 23(2), 1985, 163-171 (accessed 2026-09-15, page last updated 2021-02-10).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [1968.5, 152.4, 114.3] | [1968.5, 152.4, 114.3] |
| volume | volume | yes | PASS | 31708968.839999992 | 31708968.84 |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| center_of_mass | center_of_mass | yes | PASS | [-323.4069767441861, 76.20000000000002, 61.284883720930246] | [-323.407, 76.2, 61.2849] |
| upstream_section | section | yes | PASS | {"area": 15483.839999999998, "loops": 1, "holes": 0} |  |
| downstream_section | section | yes | PASS | {"area": 17419.32, "loops": 1, "holes": 0} |  |
| below_step_top_section | section | yes | PASS | {"area": 96773.99999999999, "loops": 1, "holes": 0} |  |
| inlet | face | yes | PASS | 1 | 15483.84 |
| outlet | face | yes | PASS | 1 | 17419.32 |
| step_face | face | yes | PASS | 1 | 1935.48 |
| roof | face | yes | PASS | 1 | 299999.4 |
| upstream_floor | face | yes | PASS | 1 | 203225.4 |
| downstream_floor | face | yes | PASS | 1 | 96774.0 |
| side_wall_y0 | face | yes | PASS | 1 | 208064.1 |
| side_wall_y_max | face | yes | PASS | 1 | 208064.1 |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `69aa64ac5f1854d6`; manifest `dcad84629ebff690`.

Downstream targets (not scored by CAD): reattachment_x_r_over_H = 6.26 ± 0.1 H (Driver-Seegmiller experiment, 0 deg roof; x_r = 79.5 +/- 1.3 mm at H = 12.7 mm; requires CFD with the documented inlet conditions)

Attempts: 2026-09-15T07:31 reached scored, scorecard PASS; 2026-09-15T08:17 reached scored, scorecard PASS; 2026-09-16T07:49 reached scored, scorecard PASS; 2026-09-16T07:53 reached scored, scorecard PASS; 2026-09-16T08:35 reached scored, scorecard PASS; 2026-09-16T08:42 reached scored, scorecard PASS; 2026-09-16T09:29 reached scored, scorecard PASS; 2026-09-16T09:36 reached scored, scorecard PASS; 2026-09-16T09:45 reached scored, scorecard PASS; 2026-09-16T10:30 reached scored, scorecard PASS; 2026-09-20T05:35 reached pipeline; 2026-09-20T05:35 reached pipeline; 2026-09-20T05:35 reached scored, scorecard PASS; 2026-09-20T05:43 reached scored, scorecard PASS; 2026-09-20T05:43 reached scored, scorecard PASS

### nist-am-test-artifact — drawing-renders-sheet

NIST Additive Manufacturing Test Artifact (Moylan et al. 2014): diamond base with centre hole, concentric bosses, 16 pins, 4 holes, two staircases, ramp, lateral and fine features. Source: S. P. Moylan, J. A. Slotwinski, A. L. Cooke, K. K. Jurrens, M. A. Donmez, An Additive Manufacturing Test Artifact, J. Res. NIST 119 (2014) 429-459, doi:10.6028/jres.119.017; NIST artifact download page (accessed 2026-09-17, NIST Test Artifact_ver3b.step (2017-10-05) and NIST Test Artifact online.STL (2013-04-10); STL translated by (-70.7107, -70.7107, -10) into the STEP frame).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [141.421356237305, 141.42135623730502, 17.0] | [141.4214, 141.4214, 17.0] |
| volume | volume | yes | PASS | 100987.06165182835 | 100987.06165341612 |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| center_of_mass | center_of_mass | yes | PASS | [0.2612567392300908, 0.8671615503671708, -4.636979473470054] | [0.26125675155433825, 0.8671615291514636, -4.636979473010583] |
| hole_d10_0_0 | cylinder | yes | PASS | {"center": [0.0, 0.0, -1.5], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "length": 17.0, "kind": "hole"} | {"point": [0.0, 0.0, -1.5], "direction": [0.0, 0.0, 1.0], "radius": 5.0, "kind": "hole"} |
| hole_d6_m26p52_40p66 | cylinder | yes | PASS | {"center": [-26.51650429449234, 40.65863991822434, -5.0], "direction": [0.7071067811865476, -0.7071067811865476, 0.0]... | {"point": [-26.5165, 40.6586, -5.0], "direction": [0.7071, -0.7071, -0.0], "radius": 3.0, "kind": "hole"} |
| hole_d4_m60_m0 | cylinder | yes | PASS | {"center": [-60.0, 0.0, -5.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 10.0, "kind": "hole"} | {"point": [-60.0, -0.0, -5.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "hole"} |
| hole_d4_60_0 | cylinder | yes | PASS | {"center": [60.0, 0.0, -5.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 10.0, "kind": "hole"} | {"point": [60.0, 0.0, -5.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "hole"} |
| hole_d4_0_m60 | cylinder | yes | PASS | {"center": [0.0, -60.0, -5.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 10.0, "kind": "hole"} | {"point": [0.0, -60.0, -5.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "hole"} |
| hole_d4_0_60 | cylinder | yes | PASS | {"center": [0.0, 60.0, -5.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 10.0, "kind": "hole"} | {"point": [0.0, 60.0, -5.0], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "hole"} |
| hole_d3_m6p01_62p58 | cylinder | yes | PASS | {"center": [-6.0104076400860045, 62.578950135010004, -5.0], "direction": [0.7071067811865476, -0.7071067811865476, 0.... | {"point": [-6.0104, 62.579, -5.0], "direction": [0.7071, -0.7071, -0.0], "radius": 1.5, "kind": "hole"} |
| hole_d2_21p21_28p28 | cylinder | yes | PASS | {"center": [21.213, 28.284, -1.0], "direction": [0.0, 0.0, 1.0], "radius": 1.0, "length": 2.0, "kind": "hole"} | {"point": [21.2132, 28.2843, -1.0], "direction": [0.0, 0.0, 1.0], "radius": 1.0, "kind": "hole"} |
| hole_d1p5_17p68_31p82 | cylinder | yes | PASS | {"center": [17.677466094067, 31.819533905933, -1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.75, "length": 2.0, "ki... | {"point": [17.6777, 31.8198, -1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.75, "kind": "hole"} |
| hole_d1_14p14_35p36 | cylinder | yes | PASS | {"center": [14.141932188135, 35.355067811865, -1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.5, "length": 2.0, "kin... | {"point": [14.1421, 35.3553, -1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.5, "kind": "hole"} |
| hole_d0p5_10p61_38p89 | cylinder | yes | PASS | {"center": [10.606398282202, 38.890601717798, -1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.25, "length": 2.0, "ki... | {"point": [10.6066, 38.8909, -1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.25, "kind": "hole"} |
| hole_d0p25_7p07_42p43 | cylinder | yes | PASS | {"center": [7.070864376269, 42.426135623731, -1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.125, "length": 2.0, "ki... | {"point": [7.0711, 42.4264, -1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.125, "kind": "hole"} |
| pin_d20_0_0 | cylinder | yes | PASS | {"center": [0.0, 0.0, 2.0], "direction": [0.0, 0.0, 1.0], "radius": 10.0, "length": 4.0, "kind": "pin"} | {"point": [0.0, 0.0, 2.0], "direction": [0.0, 0.0, 1.0], "radius": 10.0, "kind": "pin"} |
| pin_d15_0_0 | cylinder | yes | PASS | {"center": [0.0, 0.0, 5.5], "direction": [0.0, 0.0, 1.0], "radius": 7.5, "length": 3.0, "kind": "pin"} | {"point": [0.0, 0.0, 5.5], "direction": [0.0, 0.0, 1.0], "radius": 7.5, "kind": "pin"} |
| pin_d4_m50_m0 | cylinder | yes | PASS | {"center": [-50.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [-50.0, -0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_m40_m0 | cylinder | yes | PASS | {"center": [-40.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [-40.0, -0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_m30_m0 | cylinder | yes | PASS | {"center": [-30.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [-30.0, -0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_m20_m0 | cylinder | yes | PASS | {"center": [-20.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [-20.0, -0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_20_0 | cylinder | yes | PASS | {"center": [20.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [20.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_30_0 | cylinder | yes | PASS | {"center": [30.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [30.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_40_0 | cylinder | yes | PASS | {"center": [40.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [40.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_50_0 | cylinder | yes | PASS | {"center": [50.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [50.0, 0.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_0_m50 | cylinder | yes | PASS | {"center": [0.0, -50.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [0.0, -50.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_0_m40 | cylinder | yes | PASS | {"center": [0.0, -40.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [0.0, -40.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_0_m30 | cylinder | yes | PASS | {"center": [0.0, -30.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [0.0, -30.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_0_m20 | cylinder | yes | PASS | {"center": [0.0, -20.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [0.0, -20.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_0_20 | cylinder | yes | PASS | {"center": [0.0, 20.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [0.0, 20.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_0_30 | cylinder | yes | PASS | {"center": [0.0, 30.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [0.0, 30.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_0_40 | cylinder | yes | PASS | {"center": [0.0, 40.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [0.0, 40.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d4_0_50 | cylinder | yes | PASS | {"center": [0.0, 50.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "length": 7.0, "kind": "pin"} | {"point": [0.0, 50.0, 3.5], "direction": [0.0, 0.0, 1.0], "radius": 2.0, "kind": "pin"} |
| pin_d2_28p28_21p21 | cylinder | yes | PASS | {"center": [28.284, 21.213, 0.9999999999999999], "direction": [0.0, 0.0, 1.0], "radius": 1.0, "length": 1.99999999999... | {"point": [28.2843, 21.2132, 1.0], "direction": [0.0, 0.0, 1.0], "radius": 1.0, "kind": "pin"} |
| pin_d1p5_31p82_17p68 | cylinder | yes | PASS | {"center": [31.819533905933, 17.677466094067, 0.9999999999999999], "direction": [0.0, 0.0, 1.0], "radius": 0.75, "len... | {"point": [31.8198, 17.6777, 1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.75, "kind": "pin"} |
| pin_d1_35p36_14p14 | cylinder | yes | PASS | {"center": [35.355067811865, 14.141932188135, 0.9999999999999999], "direction": [0.0, 0.0, 1.0], "radius": 0.5, "leng... | {"point": [35.3553, 14.1421, 1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.5, "kind": "pin"} |
| pin_d0p5_38p89_10p61 | cylinder | yes | PASS | {"center": [38.890601717798, 10.606398282202, 0.9999999999999999], "direction": [0.0, 0.0, 1.0], "radius": 0.25, "len... | {"point": [38.8909, 10.6066, 1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.25, "kind": "pin"} |
| pin_d0p25_42p43_7p07 | cylinder | yes | PASS | {"center": [42.426135623731, 7.070864376269, 0.9999999999999999], "direction": [0.0, 0.0, 1.0], "radius": 0.125, "len... | {"point": [42.4264, 7.0711, 1.0], "direction": [0.0, 0.0, 1.0], "radius": 0.125, "kind": "pin"} |
| count_pins_d4 | cylinder_count | yes | PASS | 16 | 16 |
| count_holes_d4 | cylinder_count | yes | PASS | 4 | 4 |
| count_fine_pins | cylinder_count | yes | PASS | 1 | 1 |
| count_fine_holes | cylinder_count | yes | PASS | 1 | 1 |
| ramp_plane | plane | yes | PASS | 125.09996003212463 | 125.1 |
| side_mxmy | plane | yes | PASS | 999.9999999999325 | 1000.0 |
| side_mxpy | plane | yes | PASS | 872.9083713411255 | 872.91 |
| side_pxmy | plane | yes | PASS | 999.9999999999679 | 1000.0 |
| side_pxpy | plane | yes | PASS | 1000.0000000000034 | 1000.0 |
| top_surface | face | yes | PASS | 1 | null |
| bottom_face | face | yes | PASS | 1 | 9871.19 |
| step_up_z3 | face | yes | PASS | 1 | 100.0 |
| step_down_zm7 | face | yes | PASS | 1 | 100.0 |
| step_down_zm3 | face | yes | PASS | 1 | 100.0 |
| step_down_zm5 | face | yes | PASS | 1 | 100.0 |
| step_down_zm6 | face | yes | PASS | 1 | 100.0 |
| step_down_zm4 | face | yes | PASS | 1 | 100.0 |
| step_up_z7 | face | yes | PASS | 1 | 100.0 |
| step_up_z5 | face | yes | PASS | 1 | 100.0 |
| step_up_z6 | face | yes | PASS | 1 | 100.0 |
| step_up_z4 | face | yes | PASS | 1 | 100.0 |
| ramp_landing_z2 | face | yes | PASS | 1 | 12.5 |
| ramp_landing_z1 | face | yes | PASS | 1 | 12.5 |
| section_z1 | section | yes | PASS | {"area": 1137.9959524597182, "loops": 35, "holes": 1} |  |
| section_zm1 | section | yes | PASS | {"area": 9319.880127591747, "loops": 1, "holes": 21} |  |
| section_z5 | section | yes | PASS | {"area": 599.2367002544277, "loops": 19, "holes": 1} |  |
| section_zm5 | section | yes | PASS | {"area": 9502.233176975498, "loops": 2, "holes": 6} |  |
| section_x0 | section | yes | PASS | {"area": 1513.21356237305, "loops": 4, "holes": 0} |  |
| section_y0 | section | yes | PASS | {"area": 1513.21356237305, "loops": 4, "holes": 0} |  |
| deviation_vs_nist | deviation | yes | PASS | {"p95": 0.003848423726579589, "hausdorff_estimate": 0.03706538474409521, "silhouette_iou_min": 0.999200114929335, "vo... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `4c1b667d5b3a5583`; manifest `57e1dc3b1f732dc7`.

Attempts: 2026-09-17T07:12 reached scored, scorecard PASS; 2026-09-20T07:03 reached pipeline; 2026-09-20T07:03 reached pipeline; 2026-09-20T07:03 reached scored, scorecard PASS; 2026-09-20T07:26 reached scored, scorecard PASS; 2026-09-20T07:26 reached scored, scorecard PASS

### nist-amb2022-01-bridge — drawing-only

NIST AM Bench AMB2022-01 individual bridge artifact (IN718 LPBF benchmark part): 12 legs, 45 deg overhangs, pointed taper, 11 top tabs, hollow leg L10 with four thin walls. Source: NIST AM Bench 2022, AMB2022-01 Benchmark Measurements and Challenge Problems; dataset 'AM Bench 2022 3D Build Modeling Challenge Description Data (AMB2022-01)', doi:10.18434/mds2-2607, /CAD_Geometry/ (accessed 2026-09-15, Figure 3 drawing updated by NIST 2023-09-20; PartCAD.STEP exported from SolidWorks 2021 on 2022-03-14; STL/STEP sha256 verified against NIST's published .sha256 files).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [75.0, 5.0, 12.5] | [75, 5, 12.5] |
| volume | volume | yes | PASS | 3678.099999999998 | 3679.060003280461 |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| center_of_mass | center_of_mass | yes | PASS | [36.91975476468829, 2.5002610043228883, 6.672922160898293] | [36.91807961243961, 2.5006336665814612, 6.671963759208492] |
| legs_section_z3 | section | yes | PASS | {"area": 235.14999999999998, "loops": 13, "holes": 5} |  |
| overhang_section_z6 | section | yes | PASS | {"area": 308.7500000000003, "loops": 13, "holes": 0} |  |
| bridge_section_z9 | section | yes | PASS | {"area": 368.75, "loops": 1, "holes": 0} |  |
| tabs_section | section | yes | PASS | {"area": 55.0, "loops": 11, "holes": 0} |  |
| l10_cavity_section | section | yes | PASS | {"area": 46.400000000000006, "loops": 1, "holes": 5} |  |
| block_section_x10 | section | yes | PASS | {"area": 60.0, "loops": 1, "holes": 0} |  |
| bottom_face | face | yes | PASS | 13 | 248.75 |
| bridge_top_face | face | yes | PASS | 11 | 313.75 |
| tab_tops | face | yes | PASS | 11 | 55.0 |
| deviation_vs_nist_mesh | deviation | yes | PASS | {"p95": 4.869289383706755e-13, "hausdorff_estimate": 0.12910008430480957, "silhouette_iou_min": 1.0, "volume_ratio": ... |  |
| deviation_vs_nist_step_variant | deviation | no | PASS | {"p95": 0.5964919952171187, "hausdorff_estimate": 0.6000000238418579, "silhouette_iou_min": 0.9717812766917535, "volu... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `69be05f4ea367ae0`; manifest `bde90eb854d783c5`.

Downstream targets (not scored by CAD): part_deflection_after_partial_cut = 0.0 mm (CMM ridge heights, see NIST 3.4) (NIST measured ridge-height deflection after EDM partial separation; requires a build-process model, never a CAD comparison)

Attempts: 2026-09-15T08:17 reached published, error: interrupted: Zoo API credits exhausted (free plan, 1205 monthly credits) during ; 2026-09-15T15:36 reached scored, scorecard PASS; 2026-09-16T07:49 reached scored, scorecard PASS; 2026-09-16T08:35 reached scored, scorecard PASS; 2026-09-16T08:42 reached scored, scorecard PASS; 2026-09-16T09:29 reached scored, scorecard PASS; 2026-09-16T09:36 reached scored, scorecard PASS; 2026-09-16T09:45 reached scored, scorecard PASS; 2026-09-16T10:30 reached scored, scorecard PASS; 2026-09-20T06:28 reached pipeline; 2026-09-20T06:28 reached pipeline; 2026-09-20T06:28 reached scored, scorecard PASS; 2026-09-20T06:39 reached scored, scorecard PASS; 2026-09-20T06:40 reached scored, scorecard PASS

### nist-amb2022-01-bridge — mesh-input

NIST AM Bench AMB2022-01 individual bridge artifact (IN718 LPBF benchmark part): 12 legs, 45 deg overhangs, pointed taper, 11 top tabs, hollow leg L10 with four thin walls. Source: NIST AM Bench 2022, AMB2022-01 Benchmark Measurements and Challenge Problems; dataset 'AM Bench 2022 3D Build Modeling Challenge Description Data (AMB2022-01)', doi:10.18434/mds2-2607, /CAD_Geometry/ (accessed 2026-09-15, Figure 3 drawing updated by NIST 2023-09-20; PartCAD.STEP exported from SolidWorks 2021 on 2022-03-14; STL/STEP sha256 verified against NIST's published .sha256 files).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [75.0, 5.0, 12.5] | [75, 5, 12.5] |
| volume | volume | yes | PASS | 3678.099999999999 | 3679.060003280461 |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| center_of_mass | center_of_mass | yes | PASS | [36.91975476468829, 2.5001305021614386, 6.672922160898289] | [36.91807961243961, 2.5006336665814612, 6.671963759208492] |
| legs_section_z3 | section | yes | PASS | {"area": 235.14999999999998, "loops": 13, "holes": 5} |  |
| overhang_section_z6 | section | yes | PASS | {"area": 308.7500000000003, "loops": 13, "holes": 0} |  |
| bridge_section_z9 | section | yes | PASS | {"area": 368.75, "loops": 1, "holes": 0} |  |
| tabs_section | section | yes | PASS | {"area": 55.0, "loops": 11, "holes": 0} |  |
| l10_cavity_section | section | yes | PASS | {"area": 46.400000000000006, "loops": 1, "holes": 5} |  |
| block_section_x10 | section | yes | PASS | {"area": 60.0, "loops": 1, "holes": 0} |  |
| bottom_face | face | yes | PASS | 13 | 248.75 |
| bridge_top_face | face | yes | PASS | 11 | 313.75 |
| tab_tops | face | yes | PASS | 11 | 55.0 |
| deviation_vs_nist_mesh | deviation | yes | PASS | {"p95": 4.876531610436205e-13, "hausdorff_estimate": 0.17910003662109375, "silhouette_iou_min": 1.0, "volume_ratio": ... |  |
| deviation_vs_nist_step_variant | deviation | no | PASS | {"p95": 0.5964919952171187, "hausdorff_estimate": 0.6000000238418579, "silhouette_iou_min": 0.9717812766917535, "volu... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 12, 'fail': 0, 'not_applicable': 0}, 'failed': []}. STEP sha256 `d6106e89e49098c3`; manifest `bde90eb854d783c5`.

Downstream targets (not scored by CAD): part_deflection_after_partial_cut = 0.0 mm (CMM ridge heights, see NIST 3.4) (NIST measured ridge-height deflection after EDM partial separation; requires a build-process model, never a CAD comparison)

Attempts: 2026-09-15T16:44 reached scored, scorecard PASS; 2026-09-16T07:49 reached scored, scorecard PASS; 2026-09-16T08:35 reached scored, scorecard PASS; 2026-09-16T08:42 reached scored, scorecard PASS; 2026-09-16T09:29 reached scored, scorecard PASS; 2026-09-16T09:36 reached scored, scorecard PASS; 2026-09-16T09:46 reached scored, scorecard PASS; 2026-09-16T10:30 reached scored, scorecard PASS; 2026-09-20T06:40 reached pipeline; 2026-09-20T06:40 reached pipeline; 2026-09-20T06:40 reached scored, scorecard PASS; 2026-09-20T06:49 reached scored, scorecard PASS; 2026-09-20T06:49 reached scored, scorecard PASS

### nottingham-bearing — paper-text

University of Nottingham highly loaded half-journal bearing: shaft, 180-degree bush and oil film; film pressure, heating and operating film. Source: Layton J. et al. (2026) Experimental Investigation of a Highly Loaded Half-Journal Bearing, Lubricants 14(2):76; dataset Zenodo 10.5281/zenodo.18375341 (accessed 2026-09-25, dataset v1 (2026-01-26)).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bore | cylinder | yes | PASS | {"center": [0.0, 0.0, 37.5], "direction": [-0.0, -0.0, 1.0], "radius": 50.1, "length": 75.0, "kind": "hole"} | {"point": [0.0, 0.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 50.1, "kind": "hole"} |
| journal | cylinder | yes | PASS | {"center": [0.0, 0.0, 37.5], "direction": [0.0, 0.0, 1.0], "radius": 50.0, "length": 230.0, "kind": "pin"} | {"point": [0.0, 0.0, 0.0], "direction": [0.0, 0.0, 1.0], "radius": 50.0, "kind": "pin"} |

Pipeline gates: {'ok': True, 'summary': '11 pass, 0 fail, 3 n/a', 'failed': []}. STEP sha256 `81c4acba77149fd0`; manifest `9c1b0c339c4f4dcf`.

Attempts: 2026-09-25T09:01 reached scored, scorecard FAIL

### peristaltic-pump — published-parts

Behrens et al. 2020 open-source peristaltic pump: printed pump head and 4:1 gearbox assembled, rollers on the tube, delivered flow. Source: Behrens, Fuller, Swist et al., Open-source, 3D-printed Peristaltic Pumps for Small Volume Point-of-Care Liquid Handling, Sci Rep 10, 1543 (2020) (accessed 2026-09-25, Dataset 1).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|

Pipeline gates: {'ok': True, 'summary': '10 pass, 0 fail, 4 n/a', 'failed': []}. STEP sha256 `2a870ecc0afad306`; manifest `45bc6edc1f4850fc`.

Attempts: 2026-09-25T08:30 reached scored, scorecard FAIL; 2026-09-25T09:35 reached scored, scorecard FAIL

### planetary-set — spec-only

Planetary gear set as an assembly: fixed internal ring, sun, carrier and three planets, carrier ratio 1/3. Source: Analytic mechanism reference (scripts/derive_mechanism_truth.py); tooth counts, module and phases from the specification (accessed 2026-09-25, spec v1).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [150.0, 150.0, 20.0] | [150.0, 150.0, 20.0] |
| solid_count | solid_count | yes | PASS | 7 | 7 |
| plate | solid | yes | PASS | {"volume": 112107.30091830126, "bbox_min": [-75.0, -75.0, -5.0], "bbox_max": [75.0, 75.0, 0.0], "center_of_mass": [5.... |  |
| ring | solid | yes | PASS | {"volume": 32944.28418430639, "bbox_min": [-58.0, -58.0, 0.0], "bbox_max": [58.0, 58.0, 10.0], "center_of_mass": [7.0... |  |
| sun | solid | yes | PASS | {"volume": 16860.05692217019, "bbox_min": [-26.0, -26.0, 0.0], "bbox_max": [26.0, 26.0, 10.0], "center_of_mass": [9.0... |  |
| carrier | solid | yes | PASS | {"volume": 29263.93556818893, "bbox_min": [-44.0, -44.0, 10.0], "bbox_max": [44.0, 44.0, 15.0], "center_of_mass": [5.... |  |
| planet0 | solid | yes | PASS | {"volume": 3769.361293615628, "bbox_min": [22.34239130942548, -13.657608690574522, 0.0], "bbox_max": [49.657608690575... |  |
| planet1 | solid | yes | PASS | {"volume": 3769.3612936156287, "bbox_min": [-31.65760869057452, 17.51930630942548, 0.0], "bbox_max": [-4.342391309424... |  |
| planet2 | solid | yes | PASS | {"volume": 3769.361293615627, "bbox_min": [-31.65760869057452, -44.83452369057452, 0.0], "bbox_max": [-4.342391309424... |  |
| sun_teeth | teeth | yes | PASS | 24 | 24 |
| planet0_teeth | teeth | yes | PASS | 12 | 12 |
| planet1_teeth | teeth | yes | PASS | 12 | 12 |
| planet2_teeth | teeth | yes | PASS | 12 | 12 |
| ring_outside | cylinder | yes | PASS | {"center": [0.0, 0.0, 5.0], "direction": [0.0, 0.0, 1.0], "radius": 58.0, "length": 10.0, "kind": "pin"} | {"point": [0.0, 0.0, 5.0], "direction": [0.0, 0.0, 1.0], "radius": 58.0, "kind": "pin"} |
| carrier_hole_0 | cylinder | yes | PASS | {"center": [36.0, 0.0, 12.5], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 5.0, "kind": "hole"} | {"point": [36.0, 0.0, 12.5], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "kind": "hole"} |
| sun_mesh | gear_mesh | yes | PASS | {"max_interference": 0.0, "gap_min": 0.08910204899774841, "gap_max": 0.0966154911780339} | {"interference": 0.0, "backlash_max": 0.2} |

Pipeline gates: {'ok': True, 'summary': '10 pass, 0 fail, 4 n/a', 'failed': []}. STEP sha256 `eb39aa94af7aa9a7`; manifest `a8689838f17f4df5`.

Attempts: 2026-09-26T01:13 reached scored, scorecard PASS; 2026-09-26T01:59 reached scored, scorecard PASS; 2026-09-26T05:43 reached scored, scorecard PASS; 2026-09-26T07:38 reached scored, scorecard PASS; 2026-09-27T08:12 reached scored, scorecard PASS; 2026-09-27T16:22 reached scored, scorecard PASS

### prusa-mini-extruder-front — renders-and-sheet

Original Prusa MINI extruder front housing: functional mating part with keyhole bore stack, screw holes, heat-set traps, filament path and hotend clamp channel. Source: Prusa Research, Original Prusa MINI / MINI+ printed parts, STEP/PRINTED PARTS/MINI-extruder-front.stp (GitHub prusa3d/Original-Prusa-MINI, master) (accessed 2026-09-17, master as of 2026-09-17).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [53.000000100000086, 14.000000199999999, 63.72000010000001] | [53.0, 14.001, 63.72] |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| volume | volume | no | PASS | 30217.665329984153 | 29833.563535171925 |
| center_of_mass | center_of_mass | no | PASS | [-0.4690178635811615, 6.987973573323372, -2.61085866777646] | [-0.7028272592884086, 6.9885205318155394, -2.702754838554198] |
| hole_d26_m2_16p4_y11 | cylinder | yes | PASS | {"center": [-2.0, 11.0, 16.4], "direction": [0.0, 1.0, 0.0], "radius": 13.0, "length": 6.0, "kind": "hole"} | {"point": [-2.0, 11.0, 16.4], "direction": [-0.0, 1.0, -0.0], "radius": 13.0, "kind": "hole"} |
| hole_d22p5_m2_0_y1p5 | cylinder | yes | PASS | {"center": [-2.0, 1.5150000000000001, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 11.25, "length": 3.03000000000000... | {"point": [-2.0, 1.5, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 11.25, "kind": "hole"} |
| hole_d16_m2_16p4_y5p5 | cylinder | yes | PASS | {"center": [-2.0, 5.5, 16.4], "direction": [0.0, 1.0, 0.0], "radius": 8.0, "length": 5.0, "kind": "hole"} | {"point": [-2.0, 5.5, 16.4], "direction": [-0.0, 1.0, -0.0], "radius": 8.0, "kind": "hole"} |
| hole_d14_m2_0_y12p18 | cylinder | yes | PASS | {"center": [-2.0, 12.1805, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 7.0, "length": 3.6389999999999993, "kind": "... | {"point": [-2.0, 12.1806, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 7.0, "kind": "hole"} |
| hole_d12p68_21p17_m24p67_y7 | cylinder | no | PASS | {"center": [21.171910716563, 7.0, -24.67208928343], "direction": [0.7071067811865476, 0.0, 0.7071067811865476], "radi... | {"point": [21.1721, 7.0, -24.6727], "direction": [0.7071, -0.0, 0.7071], "radius": 6.3421, "kind": "hole"} |
| hole_d12p63_25p62_7p5_y7 | cylinder | yes | PASS | {"center": [25.618, 7.0, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 6.315, "length": 33.0, "kind": "hole"} | {"point": [25.6177, 7.0, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 6.3152, "kind": "hole"} |
| hole_d12_m2_16p4_y1p5 | cylinder | yes | PASS | {"center": [-2.0, 1.5, 16.4], "direction": [0.0, 1.0, 0.0], "radius": 6.0, "length": 3.0, "kind": "hole"} | {"point": [-2.0, 1.5, 16.4], "direction": [0.0, 1.0, 0.0], "radius": 6.0, "kind": "hole"} |
| hole_d11p5_26p02_m20p04_y7 | cylinder | no | PASS | {"center": [26.02013572150662, 7.0, -20.057815331008047], "direction": [0.1736027776670195, 0.0, 0.9848157571781108],... | {"point": [26.0232, 7.0, -20.036], "direction": [0.1736, -0.0, 0.9848], "radius": 5.75, "kind": "hole"} |
| hole_d11p5_28p75_13p75_y7 | cylinder | yes | PASS | {"center": [28.75, 7.0, 13.7310842899505], "direction": [0.0, 0.0, 1.0], "radius": 5.75, "length": 27.522168579901003... | {"point": [28.75, 7.0, 13.7532], "direction": [-0.0, -0.0, 1.0], "radius": 5.75, "kind": "hole"} |
| hole_d9p5_25p17_7p5_y5p5 | cylinder | yes | PASS | {"center": [25.171, 5.5, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 4.75, "length": 33.0, "kind": "hole"} | {"point": [25.1705, 5.5, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 4.75, "kind": "hole"} |
| hole_d9p5_25p17_7p5_y8p5 | cylinder | yes | PASS | {"center": [25.171, 8.5, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 4.75, "length": 33.0, "kind": "hole"} | {"point": [25.1705, 8.5, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 4.75, "kind": "hole"} |
| hole_d8p79_20p75_m24p25_y5p14 | cylinder | no | PASS | {"center": [20.753910716563002, 5.143, -24.254089283429998], "direction": [0.7071067811865476, 0.0, 0.707106781186547... | {"point": [20.7533, 5.1435, -24.254], "direction": [0.7071, -0.0, 0.7071], "radius": 4.3935, "kind": "hole"} |
| hole_d8p79_20p75_m24p25_y8p86 | cylinder | no | PASS | {"center": [20.753910716563, 8.857, -24.25408928343], "direction": [0.7071067811865476, 0.0, 0.7071067811865476], "ra... | {"point": [20.7533, 8.8565, -24.254], "direction": [0.7071, -0.0, 0.7071], "radius": 4.3935, "kind": "hole"} |
| hole_d8_24p72_m22p26_y5p5 | cylinder | no | PASS | {"center": [24.715775420015664, 5.5, -22.263748654191453], "direction": [0.1736027776670195, 0.0, 0.9848157571781108]... | {"point": [24.7151, 5.5, -22.2635], "direction": [0.1736, -0.0, 0.9848], "radius": 4.0, "kind": "hole"} |
| hole_d8_25p36_m18p58_y8p5 | cylinder | no | PASS | {"center": [25.360187799328795, 8.5, -18.608118981708515], "direction": [0.1736027776670195, 0.0, 0.9848157571781108]... | {"point": [25.3649, 8.5, -18.5782], "direction": [0.1736, -0.0, 0.9848], "radius": 4.0, "kind": "hole"} |
| hole_d8_27p85_9p81_y5p5 | cylinder | yes | PASS | {"center": [27.849, 5.5, 9.8125], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 19.665, "kind": "hole"} | {"point": [27.8486, 5.5, 9.8125], "direction": [-0.0, -0.0, 1.0], "radius": 4.0, "kind": "hole"} |
| hole_d8_27p85_12p36_y8p5 | cylinder | yes | PASS | {"center": [27.849, 8.5, 12.356], "direction": [0.0, 0.0, 1.0], "radius": 4.0, "length": 24.752, "kind": "hole"} | {"point": [27.8486, 8.5, 12.3559], "direction": [-0.0, -0.0, 1.0], "radius": 4.0, "kind": "hole"} |
| hole_d6p5_m23p92_0_y11p25 | cylinder | yes | PASS | {"center": [-23.92, 11.25, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 3.25, "length": 5.5, "kind": "hole"} | {"point": [-23.9203, 11.25, 0.0], "direction": [-0.0, 1.0, -0.0], "radius": 3.25, "kind": "hole"} |
| hole_d6p5_m18p5_22_y4p9 | cylinder | yes | PASS | {"center": [-18.5, 4.9, 22.0], "direction": [0.0, 1.0, 0.0], "radius": 3.25, "length": 9.8, "kind": "hole"} | {"point": [-18.5, 4.9, 22.0], "direction": [0.0, 1.0, 0.0], "radius": 3.25, "kind": "hole"} |
| hole_d6p5_m17_m20_y4p9 | cylinder | yes | PASS | {"center": [-17.0, 4.9, -20.0], "direction": [0.0, 1.0, 0.0], "radius": 3.25, "length": 9.8, "kind": "hole"} | {"point": [-17.0, 4.9, -20.0], "direction": [0.0, 1.0, 0.0], "radius": 3.25, "kind": "hole"} |
| hole_d6p5_19p92_0_y11p25 | cylinder | yes | PASS | {"center": [19.92, 11.25, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 3.25, "length": 5.5, "kind": "hole"} | {"point": [19.9203, 11.25, 0.0], "direction": [-0.0, 1.0, -0.0], "radius": 3.25, "kind": "hole"} |
| hole_d6p5_20_17_y3p9 | cylinder | yes | PASS | {"center": [20.0, 3.9, 17.0], "direction": [0.0, 1.0, 0.0], "radius": 3.25, "length": 7.8, "kind": "hole"} | {"point": [20.0, 3.9, 17.0], "direction": [0.0, 1.0, 0.0], "radius": 3.25, "kind": "hole"} |
| hole_d5p5_22p09_m15_y2p32 | cylinder | yes | PASS | {"center": [22.088, 2.339500000000167, -15.0], "direction": [0.0, 1.0, 0.0], "radius": 2.75, "length": 4.679000000000... | {"point": [22.0879, 2.3244, -15.0], "direction": [-0.0, 1.0, -0.0], "radius": 2.75, "kind": "hole"} |
| hole_d4_14p71_30_y4p62 | cylinder | yes | PASS | {"center": [14.708, 4.621, 30.0], "direction": [0.0, 1.0, 0.0], "radius": 2.0, "length": 9.242, "kind": "hole"} | {"point": [14.7082, 4.6209, 30.0], "direction": [0.0, 1.0, 0.0], "radius": 2.0, "kind": "hole"} |
| hole_d4_20p27_30_y10p74 | cylinder | no | PASS | {"center": [20.273986061727776, 10.74010863318965, 30.0], "direction": [0.9538407632561003, 0.30031283414303156, 0.0]... | {"point": [20.2742, 10.7397, 30.0], "direction": [0.9538, 0.3003, -0.0], "radius": 2.0, "kind": "hole"} |
| hole_d3p5_m18p5_22_y12p05 | cylinder | yes | PASS | {"center": [-18.5, 12.05, 22.0], "direction": [0.0, 1.0, 0.0], "radius": 1.75, "length": 3.9000000000000004, "kind": ... | {"point": [-18.5, 12.05, 22.0], "direction": [0.0, 1.0, 0.0], "radius": 1.75, "kind": "hole"} |
| hole_d3p5_m17_m20_y12p05 | cylinder | yes | PASS | {"center": [-17.0, 12.05, -20.0], "direction": [0.0, 1.0, 0.0], "radius": 1.75, "length": 3.9000000000000004, "kind":... | {"point": [-17.0, 12.05, -20.0], "direction": [0.0, 1.0, 0.0], "radius": 1.75, "kind": "hole"} |
| hole_d3p4_m23p92_0_y3p91 | cylinder | yes | PASS | {"center": [-23.92, 3.9065, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "length": 7.813, "kind": "hole"} | {"point": [-23.9203, 3.9066, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "kind": "hole"} |
| hole_d3p4_m22_15_y9p3 | cylinder | yes | PASS | {"center": [-22.0, 9.3, 15.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "length": 9.4, "kind": "hole"} | {"point": [-22.0, 9.3, 15.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "kind": "hole"} |
| hole_d3p4_8_28_y9p3 | cylinder | yes | PASS | {"center": [8.0, 9.3, 28.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "length": 9.4, "kind": "hole"} | {"point": [8.0, 9.3, 28.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "kind": "hole"} |
| hole_d3p4_12_m17_y9p3 | cylinder | yes | PASS | {"center": [12.0, 9.3, -17.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "length": 9.4, "kind": "hole"} | {"point": [12.0, 9.3, -17.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "kind": "hole"} |
| hole_d3p4_19p92_0_y3p91 | cylinder | yes | PASS | {"center": [19.92, 3.9065, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "length": 7.813, "kind": "hole"} | {"point": [19.9203, 3.9066, 0.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "kind": "hole"} |
| hole_d3p4_20_17_y11p05 | cylinder | yes | PASS | {"center": [20.0, 11.05, 17.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "length": 5.9, "kind": "hole"} | {"point": [20.0, 11.05, 17.0], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "kind": "hole"} |
| pin_d11_m18p5_22_y11 | cylinder | no | PASS | {"center": [-18.5, 11.0, 22.0], "direction": [0.0, 1.0, 0.0], "radius": 5.5, "length": 6.0, "kind": "pin"} | {"point": [-18.5, 11.0, 22.0], "direction": [0.0, 1.0, 0.0], "radius": 5.5, "kind": "pin"} |
| pin_d10_8_28_y7 | cylinder | no | PASS | {"center": [8.0, 7.0, 28.0], "direction": [0.0, 1.0, 0.0], "radius": 5.0, "length": 14.0, "kind": "pin"} | {"point": [8.0, 7.0, 28.0], "direction": [0.0, 1.0, 0.0], "radius": 5.0, "kind": "pin"} |
| pin_d9p18_21p17_m24p67_y7 | cylinder | no | PASS | {"center": [21.17191071656115, 7.0, -24.67208928343385], "direction": [0.7071067811865476, 0.0, 0.7071067811865476], ... | {"point": [21.1721, 7.0, -24.6727], "direction": [0.7071, -0.0, 0.7071], "radius": 4.5921, "kind": "pin"} |
| pin_d9p13_25p62_7p5_y7 | cylinder | no | PASS | {"center": [25.618, 7.0, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 4.565, "length": 33.0, "kind": "pin"} | {"point": [25.6177, 7.0, 7.5], "direction": [0.0, 0.0, 1.0], "radius": 4.5652, "kind": "pin"} |
| pin_d6_25p17_7p88_y8p5 | cylinder | no | PASS | {"center": [25.171, 8.5, 7.878999999999962], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 32.24200000000007... | {"point": [25.1705, 8.5, 7.8789], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "pin"} |
| pin_d5p29_20p75_m24p25_y5p14 | cylinder | no | PASS | {"center": [20.753910716563826, 5.143, -24.254089283431174], "direction": [0.7071067811865476, 0.0, 0.707106781186547... | {"point": [20.7533, 5.1435, -24.254], "direction": [0.7071, -0.0, 0.7071], "radius": 2.6435, "kind": "pin"} |
| pin_d5p29_20p75_m24p25_y8p86 | cylinder | no | PASS | {"center": [20.7539107165615, 8.857, -24.2540892834335], "direction": [0.7071067811865476, 0.0, 0.7071067811865476], ... | {"point": [20.7533, 8.8565, -24.254], "direction": [0.7071, -0.0, 0.7071], "radius": 2.6435, "kind": "pin"} |
| back_mating_face | face | yes | PASS | 1 | 2166.04 |
| front_face | face | yes | PASS | 1 | 2279.29 |
| bottom_face | face | yes | PASS | 1 | 573.52 |
| left_side_face | face | yes | PASS | 1 | 607.2 |
| right_side_faces | face | no | PASS | 6 | 106.85 |
| section_y7 | section | yes | PASS | {"area": 2204.7994157476405, "loops": 1, "holes": 11} |  |
| section_y1p5 | section | no | PASS | {"area": 2219.251898993416, "loops": 1, "holes": 9} |  |
| section_y12 | section | no | PASS | {"area": 2151.779355939236, "loops": 1, "holes": 7} |  |
| deviation_vs_prusa | deviation | no | FAIL | {"p95": 0.9013622976319787, "hausdorff_estimate": 6.798918680599096, "silhouette_iou_min": 0.9691608036206084, "volum... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `aa6f286b4ab0d560`; manifest `6b5dd42e11826db4`.

Attempts: 2026-09-17T13:33 reached draft-failed; 2026-09-17T14:03 reached scored, scorecard FAIL; 2026-09-17T18:26 reached pipeline; 2026-09-17T20:41 reached pipeline; 2026-09-18T04:16 reached scored, scorecard FAIL; 2026-09-20T14:04 reached pipeline; 2026-09-20T14:04 reached pipeline; 2026-09-20T14:04 reached scored, scorecard FAIL; 2026-09-20T15:11 reached scored, scorecard FAIL; 2026-09-20T15:11 reached scored, scorecard FAIL; 2026-09-20T15:12 reached pipeline; 2026-09-20T15:12 reached pipeline; 2026-09-20T15:12 reached scored, scorecard FAIL; 2026-09-20T16:13 reached scored, scorecard FAIL; 2026-09-20T16:13 reached scored, scorecard FAIL; 2026-09-20T16:40 reached pipeline; 2026-09-20T16:40 reached pipeline; 2026-09-20T16:40 reached scored, scorecard FAIL; 2026-09-20T20:09 reached scored, scorecard FAIL; 2026-09-20T20:09 reached scored, scorecard FAIL; 2026-09-21T14:35 reached scored, scorecard PASS; 2026-09-21T19:10 reached scored, scorecard PASS; 2026-09-21T20:12 reached scored, scorecard PASS; 2026-09-21T20:57 reached scored, scorecard PASS; 2026-09-21T23:45 reached scored, scorecard FAIL; 2026-09-22T05:11 reached scored, scorecard PASS; 2026-09-22T05:24 reached scored, scorecard PASS

### prusa-mini-extruder-front-ecr1 — ecr1

Prusa MINI extruder front after ECR-1 (heat-set traps Ø6.5 x 9.8 -> Ø5.0 x 6.0) with every other interface preserved. Source: Prusa Research, Original Prusa MINI / MINI+ printed parts, STEP/PRINTED PARTS/MINI-extruder-front.stp (GitHub prusa3d/Original-Prusa-MINI, master); ECR-1 nominal derived from the request (class C) (accessed 2026-09-17, master as of 2026-09-17).

### rack-pinion — spec-only

Rack and pinion as an assembly: a 20-tooth module-2 pinion driving a straight-flank rack on a slide. Source: Analytic mechanism reference (scripts/derive_mechanism_truth.py); module, tooth count and rack teeth from the specification (accessed 2026-09-25, spec v1).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [240.0, 80.0, 13.0] | [240.0, 80.0, 13.0] |
| solid_count | solid_count | yes | PASS | 3 | 3 |
| plate | solid | yes | PASS | {"volume": 95858.62833058844, "bbox_min": [-120.0, -50.0, -5.0], "bbox_max": [120.0, 30.0, 0.0], "center_of_mass": [-... |  |
| pinion | solid | yes | PASS | {"volume": 9545.55466679258, "bbox_min": [-22.0, -22.0, 0.0], "bbox_max": [22.0, 22.0, 8.0], "center_of_mass": [9.561... |  |
| rack | solid | yes | PASS | {"volume": 18971.16159187418, "bbox_min": [-100.0, -32.0, 0.0], "bbox_max": [100.0, -17.999999999999787, 8.0], "cente... |  |
| pinion_teeth | teeth | yes | PASS | 20 | 20 |
| pinion_bore | cylinder | yes | PASS | {"center": [0.0, 0.0, 4.0], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "length": 8.0, "kind": "hole"} | {"point": [0.0, 0.0, 4.0], "direction": [0.0, 0.0, 1.0], "radius": 3.0, "kind": "hole"} |
| pinion_on_rack | clearance | yes | PASS | {"gap": 0.047211751225539146, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": 0.15} |

Pipeline gates: {'ok': True, 'summary': '10 pass, 0 fail, 4 n/a', 'failed': []}. STEP sha256 `99c23fe941148fdb`; manifest `642a7910d2846819`.

Attempts: 2026-09-26T00:28 reached scored, scorecard PASS; 2026-09-26T01:59 reached scored, scorecard PASS; 2026-09-26T05:43 reached scored, scorecard PASS; 2026-09-26T07:38 reached scored, scorecard PASS; 2026-09-27T08:12 reached scored, scorecard PASS; 2026-09-27T16:22 reached scored, scorecard PASS

### rpi5-enclosure — requirements

Raspberry Pi 5 two-piece enclosure designed to functional requirements (board fit, standoff datums, plug access, lid closure, wall minimum). Source: Raspberry Pi Ltd, Raspberry Pi 5 mechanical drawing RP-008347-DS-1 (pip.raspberrypi.com); requirements authored for this benchmark (accessed 2026-09-17, drawing updated 6 Oct 2025 per the product information portal).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| two_solids | solid_count | yes | PASS | 2 | 2 |
| base_solid | solid | yes | PASS | {"volume": 34725.78456717068, "bbox_min": [-8.5, -8.5, -7.4], "bbox_max": [93.5, 64.5, 21.550000000000004], "center_o... |  |
| lid_solid | solid | yes | PASS | {"volume": 23264.50266447077, "bbox_min": [-8.5, -8.5, 21.6], "bbox_max": [93.5, 64.5, 25.6], "center_of_mass": [42.4... |  |
| clear_pcb_slab | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_pcb_edge_band | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_top_envelope | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_bottom_keepout | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_c_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_hdmi0_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_hdmi1_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_a_upper_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_a_lower_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_rj45_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_sd_card_slot | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| lid_on_base | clearance | yes | PASS | {"gap": 0.05000000000000071, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": 0.1} |
| standoff_1_top | face | yes | PASS | 1 | null |
| standoff_1_pilot | cylinder | yes | PASS | {"center": [3.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [3.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_2_top | face | yes | PASS | 1 | null |
| standoff_2_pilot | cylinder | yes | PASS | {"center": [61.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [61.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_3_top | face | yes | PASS | 1 | null |
| standoff_3_pilot | cylinder | yes | PASS | {"center": [3.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [3.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_4_top | face | yes | PASS | 1 | null |
| standoff_4_pilot | cylinder | yes | PASS | {"center": [61.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [61.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| lid_screw_clearance_holes | cylinder_count | yes | PASS | 4 | null |
| pilot_holes_total | cylinder_count | yes | PASS | 8 | null |
| wall_min | thickness | yes | PASS | {"min": 1.4000015258789076, "p01": 1.8511694747455432, "p05": 2.400000095367431, "p50": 2.4000015258789076} | {"min": 2.0} |
| headroom_probe | probe | yes | PASS | ["out", "out", "out"] | void |
| floor_probe | probe | yes | PASS | ["in"] | solid |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `b674a3df644adc48`; manifest `818368a320e78afb`.

Attempts: 2026-09-18T06:11 reached scored, scorecard FAIL; 2026-09-18T06:49 reached scored, scorecard PASS; 2026-09-18T09:17 reached judged; 2026-09-20T07:47 reached pipeline; 2026-09-20T07:47 reached pipeline; 2026-09-20T07:47 reached scored, scorecard PASS; 2026-09-20T07:59 reached scored, scorecard PASS; 2026-09-20T08:00 reached scored, scorecard PASS

### rpi5-enclosure-ecr1 — ecr1

Raspberry Pi 5 enclosure after ECR1: +10 mm internal headroom, datums and openings fixed. Source: Raspberry Pi Ltd, Raspberry Pi 5 mechanical drawing RP-008347-DS-1 (pip.raspberrypi.com); requirements authored for this benchmark (accessed 2026-09-17, drawing updated 6 Oct 2025 per the product information portal).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| two_solids | solid_count | yes | PASS | 2 | 2 |
| base_solid | solid | yes | PASS | {"volume": 41845.784567170675, "bbox_min": [-8.5, -8.5, -7.4], "bbox_max": [93.5, 64.5, 31.550000000000004], "center_... |  |
| lid_solid | solid | yes | PASS | {"volume": 23264.50266447077, "bbox_min": [-8.5, -8.5, 31.6], "bbox_max": [93.5, 64.5, 35.6], "center_of_mass": [42.5... |  |
| clear_pcb_slab | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_pcb_edge_band | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_top_envelope | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_bottom_keepout | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_c_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_hdmi0_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_hdmi1_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_a_upper_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_a_lower_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_rj45_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_sd_card_slot | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| lid_on_base | clearance | yes | PASS | {"gap": 0.05000000000000071, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": 0.1} |
| standoff_1_top | face | yes | PASS | 1 | null |
| standoff_1_pilot | cylinder | yes | PASS | {"center": [3.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [3.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_2_top | face | yes | PASS | 1 | null |
| standoff_2_pilot | cylinder | yes | PASS | {"center": [61.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [61.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_3_top | face | yes | PASS | 1 | null |
| standoff_3_pilot | cylinder | yes | PASS | {"center": [3.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [3.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_4_top | face | yes | PASS | 1 | null |
| standoff_4_pilot | cylinder | yes | PASS | {"center": [61.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [61.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| lid_screw_clearance_holes | cylinder_count | yes | PASS | 4 | null |
| pilot_holes_total | cylinder_count | yes | PASS | 8 | null |
| wall_min | thickness | yes | PASS | {"min": 1.4000015258789076, "p01": 1.8518058854704944, "p05": 2.400000095367431, "p50": 2.4000015258789076} | {"min": 2.0} |
| headroom_probe | probe | yes | PASS | ["out", "out", "out"] | void |
| floor_probe | probe | yes | PASS | ["in"] | solid |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `d6c629ee3eedf4b4`; manifest `df7bd97cc5ea2bf4`.

Attempts: 2026-09-18T07:08 reached init, error: design bundle problems:
  - unexpected bundle entry 'ecr' (allowed: ['brief.md',; 2026-09-18T07:17 reached scored, scorecard PASS; 2026-09-20T08:00 reached scored, scorecard PASS; 2026-09-20T08:42 reached scored, scorecard PASS; 2026-09-20T08:46 reached scored, scorecard PASS

### rpi5-enclosure-ecr2 — ecr2

Raspberry Pi 5 enclosure after ECR2: 3 mm walls growing outward, interior preserved. Source: Raspberry Pi Ltd, Raspberry Pi 5 mechanical drawing RP-008347-DS-1 (pip.raspberrypi.com); requirements authored for this benchmark (accessed 2026-09-17, drawing updated 6 Oct 2025 per the product information portal).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| two_solids | solid_count | yes | PASS | 2 | 2 |
| base_solid | solid | yes | PASS | {"volume": 42120.964567170595, "bbox_min": [-8.5, -8.5, -8.0], "bbox_max": [93.5, 64.5, 21.55], "center_of_mass": [41... |  |
| lid_solid | solid | yes | PASS | {"volume": 23264.50266447077, "bbox_min": [-8.5, -8.5, 21.6], "bbox_max": [93.5, 64.5, 25.6], "center_of_mass": [42.4... |  |
| clear_pcb_slab | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_pcb_edge_band | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_top_envelope | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_bottom_keepout | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_c_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_hdmi0_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_hdmi1_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_a_upper_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_a_lower_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_rj45_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_sd_card_slot | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| lid_on_base | clearance | yes | PASS | {"gap": 0.05000000000000071, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": 0.1} |
| standoff_1_top | face | yes | PASS | 1 | null |
| standoff_1_pilot | cylinder | yes | PASS | {"center": [3.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [3.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_2_top | face | yes | PASS | 1 | null |
| standoff_2_pilot | cylinder | yes | PASS | {"center": [61.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [61.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_3_top | face | yes | PASS | 1 | null |
| standoff_3_pilot | cylinder | yes | PASS | {"center": [3.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [3.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_4_top | face | yes | PASS | 1 | null |
| standoff_4_pilot | cylinder | yes | PASS | {"center": [61.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [61.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| lid_screw_clearance_holes | cylinder_count | yes | PASS | 4 | null |
| pilot_holes_total | cylinder_count | yes | PASS | 8 | null |
| wall_min | thickness | yes | PASS | {"min": 1.4000015258789076, "p01": 1.853052197815869, "p05": 2.9999999999999942, "p50": 3.0000000000000013} | {"min": 3.0} |
| headroom_probe | probe | yes | PASS | ["out", "out", "out"] | void |
| floor_probe | probe | yes | PASS | ["in"] | solid |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `931ab98f9da9dc6b`; manifest `99a11f1462a95051`.

Attempts: 2026-09-18T07:34 reached scored, scorecard FAIL; 2026-09-18T08:06 reached scored, scorecard PASS; 2026-09-20T08:00 reached scored, scorecard PASS; 2026-09-20T08:42 reached scored, scorecard PASS; 2026-09-20T08:46 reached scored, scorecard PASS

### rpi5-enclosure-ecr3 — ecr3

Raspberry Pi 5 enclosure after ECR3: lid screws moved to the long sides at x = (50.0, 75.0). Source: Raspberry Pi Ltd, Raspberry Pi 5 mechanical drawing RP-008347-DS-1 (pip.raspberrypi.com); requirements authored for this benchmark (accessed 2026-09-17, drawing updated 6 Oct 2025 per the product information portal).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| two_solids | solid_count | yes | PASS | 2 | 2 |
| base_solid | solid | yes | PASS | {"volume": 33728.53656717064, "bbox_min": [-8.5, -8.5, -7.4], "bbox_max": [93.5, 64.5, 21.550000000000004], "center_o... |  |
| lid_solid | solid | yes | PASS | {"volume": 23033.880364908968, "bbox_min": [-2.9, -8.5, 21.6], "bbox_max": [87.9, 64.5, 25.6], "center_of_mass": [43.... |  |
| clear_pcb_slab | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_pcb_edge_band | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_top_envelope | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_bottom_keepout | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_c_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_hdmi0_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_hdmi1_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_a_upper_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_usb_a_lower_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_rj45_plug | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| clear_sd_card_slot | clearance | yes | PASS | {"gap": 0.0, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": null} |
| lid_on_base | clearance | yes | PASS | {"gap": 0.05000000000000071, "interference_volume": 0.0} | {"min_gap": 0.0, "max_gap": 0.1} |
| standoff_1_top | face | yes | PASS | 1 | null |
| standoff_1_pilot | cylinder | yes | PASS | {"center": [3.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [3.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_2_top | face | yes | PASS | 1 | null |
| standoff_2_pilot | cylinder | yes | PASS | {"center": [61.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [61.5, 3.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_3_top | face | yes | PASS | 1 | null |
| standoff_3_pilot | cylinder | yes | PASS | {"center": [3.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [3.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| standoff_4_top | face | yes | PASS | 1 | null |
| standoff_4_pilot | cylinder | yes | PASS | {"center": [61.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "length": 5.0, "kind": "hole"} | {"point": [61.5, 52.5, -2.5], "direction": [0.0, 0.0, 1.0], "radius": 1.25, "kind": "hole"} |
| lid_screw_clearance_holes | cylinder_count | yes | PASS | 4 | 4 |
| pilot_holes_total | cylinder_count | yes | PASS | 8 | 8 |
| side_screw_ym_x50 | cylinder_count | yes | PASS | 1 | null |
| side_pilot_ym_x50 | cylinder_count | yes | PASS | 1 | null |
| side_screw_yp_x50 | cylinder_count | yes | PASS | 1 | null |
| side_pilot_yp_x50 | cylinder_count | yes | PASS | 1 | null |
| side_screw_ym_x75 | cylinder_count | yes | PASS | 1 | null |
| side_pilot_ym_x75 | cylinder_count | yes | PASS | 1 | null |
| side_screw_yp_x75 | cylinder_count | yes | PASS | 1 | null |
| side_pilot_yp_x75 | cylinder_count | yes | PASS | 1 | null |
| wall_min | thickness | yes | PASS | {"min": 1.4000015258789076, "p01": 1.8515692414086458, "p05": 2.400000095367431, "p50": 2.4000015258789076} | {"min": 2.0} |
| headroom_probe | probe | yes | PASS | ["out", "out", "out"] | void |
| floor_probe | probe | yes | PASS | ["in"] | solid |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `c7718b3737a1b641`; manifest `b48a7f971faf0228`.

Attempts: 2026-09-18T08:07 reached scored, scorecard PASS; 2026-09-20T08:00 reached ecr; 2026-09-20T08:37 reached scored, scorecard PASS; 2026-09-20T08:42 reached scored, scorecard PASS; 2026-09-20T08:46 reached scored, scorecard PASS

### spleen-c1-blade — table-and-notes

SPLEEN C1 high-speed low-pressure turbine cascade blade: published airfoil coordinates extruded over the 165 mm cascade span. Source: Lavagnoli, Lopes, Simonassi, Torre (VKI), SPLEEN - High Speed Turbine Cascade - Test Case Database v5, Zenodo 13712768, doi:10.5281/zenodo.13712768 (CC-BY-4.0); Test_Case_Setup/SPLEENC1_Geometry_Airfoil_2D_v1.xlsx, SPLEENC1_Geometry_Airfoil_2D_CAD_v2.stp, SPLEEN-HSTC-DB-Geometry_TestSection_Info_v2.pdf (accessed 2026-09-15, database v5 (2024-09-09); archive md5 e85ff6468e90477d2895817e349d30fc; v1 CAD with the wrong stagger is Zenodo 7264762 (2022-10-30, zip md5 73af4bf92c5ac51d86e4e06ed6dbdef4) and is no longer shipped; the coordinate table is the authoritative geometry per the v2 update note).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [47.97268569995657, 31.21231434354737, 165.0] | [47.9727, 31.2123, 165.0] |
| volume | volume | yes | PASS | 38055.12443402208 | 38055.54277899529 |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| center_of_mass | center_of_mass | yes | PASS | [20.619657984838334, 1.0449253890211685, 82.5000000000001] | [20.619763426241885, 1.0447954300575213, 82.50000000000004] |
| midspan_profile | profile2d | yes | PASS | {"area": 230.6371177819423, "chord": 52.987829613121185, "stagger_deg": -26.186513023340094, "bbox_min": [-0.19685863... |  |
| midspan_landmarks | profile2d | yes | PASS | {"area": 230.6371177819423, "chord": 52.284640202739865, "stagger_deg": -24.40085023652175, "bbox_min": [-0.196858635... |  |
| root_profile | profile2d | yes | PASS | {"area": 230.6371177819423, "chord": 52.987829613121185, "stagger_deg": -26.186513023340094, "bbox_min": [-0.19685863... |  |
| midspan_section | section | yes | PASS | {"area": 230.6371177819423, "loops": 1, "holes": 0} |  |
| root_face | face | yes | PASS | 1 | 230.64 |
| tip_face | face | yes | PASS | 1 | 230.64 |
| deviation_vs_v2_blade | deviation | yes | PASS | {"p95": 0.0060180127440484605, "hausdorff_estimate": 0.030933261518474732, "silhouette_iou_min": 0.9940283472293985, ... |  |
| not_matching_v1_wrong_stagger | not_matching | yes | PASS | {"p95": 0.5782052795830523, "hausdorff_estimate": 0.992694783458808, "silhouette_iou_min": 0.86421018511218, "volume_... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `26c1b3a9520510ea`; manifest `200fb44a3b41e190`.

Downstream targets (not scored by CAD): blade_pressure_distribution_steady_inlet = 0.0 Mach / Cp along the blade at midspan (measured in the cascade (periodic passage, documented inlet conditions); a later CFD comparison, never a CAD input)

Attempts: 2026-09-15T17:56 reached draft-failed; 2026-09-15T18:15 reached scored, scorecard FAIL; 2026-09-15T19:43 reached scored, scorecard PASS; 2026-09-16T07:50 reached scored, scorecard PASS; 2026-09-16T08:36 reached scored, scorecard PASS; 2026-09-16T08:42 reached scored, scorecard PASS; 2026-09-16T09:31 reached scored, scorecard PASS; 2026-09-16T09:39 reached scored, scorecard PASS; 2026-09-16T09:48 reached scored, scorecard PASS; 2026-09-16T10:32 reached scored, scorecard PASS; 2026-09-20T06:07 reached pipeline; 2026-09-20T06:07 reached pipeline; 2026-09-20T06:07 reached scored, scorecard PASS; 2026-09-20T06:25 reached scored, scorecard PASS; 2026-09-20T06:27 reached scored, scorecard PASS

### voron-sb-duct — renders-sections-sheet

Voron Stealthburner printhead front (Rapido V2): two part-cooling ducts, hotend cavity, fan opening; interior connectivity, passage volumes, sections and wall minimum. Source: VoronDesign, Voron-Stealthburner, CAD/Printheads/Stealthburner_Printhead_Rapido_V2.step (front body, solid 0) (accessed 2026-09-17, main as of 2026-09-17 (release 1.0, 2024-07-04)).

| check | kind | required | verdict | measured | expected / band |
|---|---|---|---|---|---|
| bbox_size | bbox_size | yes | PASS | [71.06800000000356, 27.4000002, 59.133000000001914] | [71.068, 27.4, 59.133] |
| solid_count | solid_count | yes | PASS | 1 | 1 |
| volume | volume | no | PASS | 40218.14776506256 | 40073.2601304934 |
| passage_left_duct | passage | yes | PASS | {"connected": true, "reaches_exterior": false, "passage_volume": 4672.3200000000015} | {"connected": true, "volume_min": 3474.3, "volume_max": 5211.4} |
| passage_right_duct | passage | yes | PASS | {"connected": true, "reaches_exterior": false, "passage_volume": 3754.752000000001} | {"connected": true, "volume_min": 3440.4, "volume_max": 5160.7} |
| ducts_separate | passage | yes | PASS | {"connected": false, "reaches_exterior": false, "passage_volume": 4672.3200000000015} | {"connected": false, "volume_min": null, "volume_max": null} |
| section_ym12 | section | yes | PASS | {"area": 1364.2220834519965, "loops": 1, "holes": 5} |  |
| section_ym20 | section | yes | PASS | {"area": 1481.816942271945, "loops": 2, "holes": 8} |  |
| section_z10 | section | yes | PASS | {"area": 459.7996489051243, "loops": 2, "holes": 4} |  |
| section_z30 | section | yes | PASS | {"area": 717.2342841124283, "loops": 2, "holes": 2} |  |
| section_z45 | section | yes | PASS | {"area": 522.4127700588193, "loops": 3, "holes": 2} |  |
| wall_min | thickness | yes | PASS | {"min": 0.055975308098987854, "p01": 0.5505500778831898, "p05": 0.9000015258789077, "p50": 3.100000381469728} | {"min": 0.75} |
| hole_d5_m7p0_m3p9_59p4 | cylinder | yes | PASS | {"center": [-6.963, -3.939, 59.43], "direction": [0.0, 0.0, 1.0], "radius": 2.5, "length": 2.8599999999999994, "kind"... | {"point": [-6.963, -3.939, 59.45], "direction": [-0.0, 0.0, 1.0], "radius": 2.5, "kind": "hole"} |
| hole_d5_3p9_m7p0_59p4 | cylinder | yes | PASS | {"center": [3.939, -6.963, 59.43], "direction": [0.0, 0.0, 1.0], "radius": 2.5, "length": 2.8599999999999994, "kind":... | {"point": [3.939, -6.963, 59.45], "direction": [-0.0, 0.0, 1.0], "radius": 2.5, "kind": "hole"} |
| hole_d4p7_m28p0_m2p3_19p0 | cylinder | yes | PASS | {"center": [-28.0, -2.1, 19.0], "direction": [0.0, 1.0, 0.0], "radius": 2.35, "length": 4.2, "kind": "hole"} | {"point": [-28.0, -2.3, 19.0], "direction": [0.0, 1.0, -0.0], "radius": 2.35, "kind": "hole"} |
| hole_d4p7_m25p0_m2p3_35p0 | cylinder | yes | PASS | {"center": [-25.0, -2.1285, 35.0], "direction": [0.0, 1.0, 0.0], "radius": 2.35, "length": 4.257, "kind": "hole"} | {"point": [-25.0, -2.329, 35.0], "direction": [0.0, 1.0, -0.0], "radius": 2.35, "kind": "hole"} |
| hole_d4p6_m12p7_m3p2_55p4 | cylinder | yes | PASS | {"center": [-12.7, -3.0, 55.424], "direction": [0.0, 1.0, 0.0], "radius": 2.3, "length": 6.0, "kind": "hole"} | {"point": [-12.7, -3.2, 55.424], "direction": [-0.0, 1.0, -0.0], "radius": 2.3, "kind": "hole"} |
| hole_d4p6_12p7_m3p1_55p4 | cylinder | yes | PASS | {"center": [12.7, -2.9305, 55.424], "direction": [0.0, 1.0, 0.0], "radius": 2.3, "length": 5.861, "kind": "hole"} | {"point": [12.7, -3.131, 55.424], "direction": [-0.0, 1.0, -0.0], "radius": 2.3, "kind": "hole"} |
| hole_d3p4_m16p2_m3p7_19p3 | cylinder | yes | PASS | {"center": [-16.25, -3.75, 19.301], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "length": 7.5, "kind": "hole"} | {"point": [-16.25, -3.75, 19.301], "direction": [0.0, 1.0, -0.0], "radius": 1.7, "kind": "hole"} |
| hole_d3p4_16p3_m3p7_19p3 | cylinder | yes | PASS | {"center": [16.25, -3.75, 19.301], "direction": [0.0, 1.0, 0.0], "radius": 1.7, "length": 7.5, "kind": "hole"} | {"point": [16.25, -3.75, 19.301], "direction": [0.0, 1.0, -0.0], "radius": 1.7, "kind": "hole"} |
| hole_d2p7_m7p0_m3p9_56p0 | cylinder | yes | PASS | {"center": [-6.963, -3.939, 56.0], "direction": [0.0, 0.0, 1.0], "radius": 1.35, "length": 4.0, "kind": "hole"} | {"point": [-6.963, -3.939, 56.0], "direction": [-0.0, 0.0, 1.0], "radius": 1.35, "kind": "hole"} |
| hole_d2p7_3p9_m7p0_56p0 | cylinder | yes | PASS | {"center": [3.939, -6.963, 56.0], "direction": [0.0, 0.0, 1.0], "radius": 1.35, "length": 4.0, "kind": "hole"} | {"point": [3.939, -6.963, 56.0], "direction": [-0.0, 0.0, 1.0], "radius": 1.35, "kind": "hole"} |
| deviation_vs_voron | deviation | no | FAIL | {"p95": 2.5464024902113893, "hausdorff_estimate": 5.179480639655186, "silhouette_iou_min": 0.9001545501010052, "volum... |  |

Pipeline gates: {'ok': True, 'summary': {'pass': 11, 'fail': 0, 'not_applicable': 1}, 'failed': []}. STEP sha256 `ba13a7474c61e4df`; manifest `29813e0f5abc7877`.

Attempts: 2026-09-18T12:26 reached pipeline; 2026-09-18T15:01 reached scored, scorecard FAIL; 2026-09-18T17:34 reached scored, scorecard FAIL; 2026-09-19T07:44 reached scored, scorecard FAIL; 2026-09-20T20:10 reached scored, scorecard FAIL; 2026-09-20T20:10 reached scored, scorecard FAIL; 2026-09-20T20:10 reached scored, scorecard FAIL; 2026-09-20T21:03 reached pipeline; 2026-09-20T21:03 reached init, error: another pipeline process is driving voron-sb-duct (results/voron-sb-duct/.drive.; 2026-09-20T21:03 reached scored, scorecard FAIL; 2026-09-20T21:03 reached scored, scorecard FAIL; 2026-09-21T00:29 reached scored, scorecard FAIL; 2026-09-21T07:07 reached scored, scorecard PASS; 2026-09-21T14:12 reached scored, scorecard PASS; 2026-09-21T19:48 reached scored, scorecard PASS; 2026-09-22T00:02 reached scored, scorecard PASS; 2026-09-22T10:05 reached scored, scorecard PASS

### voron-sb-duct-ecr1 — ecr1

Voron Stealthburner printhead front (Rapido V2) after ECR1: two Ø3.4 side screw holes lowered 3 mm to z = 16.3. Source: VoronDesign, Voron-Stealthburner, CAD/Printheads/Stealthburner_Printhead_Rapido_V2.step (front body, solid 0) (accessed 2026-09-17, main as of 2026-09-17 (release 1.0, 2024-07-04)).


## Machines: predictions against measurements

Latest scorecard per machine case. `unresolved` predictions are not supported by their mesh ladder: they are reported, never passed.

| machine | observable | quantity | op. case | split | solver | prediction | reference | rel. error | z | mesh-resolved | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| compound-train | trainRatio | transmission_ratio | - | development | evaluator | 0.1667 | 0.1667 | +0.0 % | - | - | PASS |
| compound-train | outputAt360 | joint_value | - | development | evaluator | 60 | 60 | +0.0 % | - | - | PASS |
| crank-slider | sliderTravel | joint_value | - | development | evaluator | - | - | - | - | - | PASS |
| crank-slider | stroke | joint_range | - | development | evaluator | 60.33 | 60.33 | -0.0 % | - | - | PASS |
| disc-brake | peakDiscTemperature | max_temperature | panicBrake | development | calculix | 424.5 | 430 | -1.3 % | 0.8615 | - | PASS |
| disc-brake | lineMaxTemperature | line_max_temperature | panicBrake | development | calculix | 424.5 | 405 | +4.8 % | 3.036 | - | FAIL |
| disc-brake | timeOfPeak | time_of_max_temperature | panicBrake | development | calculix | 2.8 | 3 | -6.7 % | 0.8 | - | PASS |
| disc-brake | producedHeat | produced_heat | panicBrake | development | calculix | 6.75e+04 | 6.75e+04 | +0.0 % | - | - | PASS |
| disc-brake | dissipatedHeat | dissipated_heat | panicBrake | development | calculix | 981.9 | 590 | +66.4 % | 4.355 | - | FAIL |
| disc-brake | hotspotRadius | hotspot_radius | panicBrake | development | calculix | 113.5 | 132 | -14.0 % | 4.508 | - | FAIL |
| fan-01 | dpts_q1403 | pressure_rise_total_to_static | q1403 | development | openfoam | 94.67 | 126.5 | -25.1 % | 5.053 | no | unresolved |
| fan-01 | dpts_q1804 | pressure_rise_total_to_static | q1804 | held_out | openfoam | 84.11 | 63.95 | +31.5 % | 2.655 | - | FAIL |
| fan-01 | dpts_q0994 | pressure_rise_total_to_static | q0994 | held_out | openfoam | 116 | 134.7 | -13.9 % | 6.663 | - | FAIL |
| fan-01 | torque_q1403 | torque | q1403 | development | openfoam | 1.983 | 2.142 | -7.4 % | 2.714 | no | unresolved |
| fda-pump | pressureRiseC1 | pressure_rise | C1 | development | openfoam | 2.367e+04 | 2.24e+04 | +5.7 % | 0.6364 | - | PASS |
| fda-pump | pressureRiseC2 | pressure_rise | C2 | held_out | openfoam | 4.872e+04 | 4.653e+04 | +4.7 % | 0.9755 | - | PASS |
| fda-pump | pressureRiseC3 | pressure_rise | C3 | held_out | openfoam | 4.779e+04 | 4.173e+04 | +14.5 % | 2.373 | - | FAIL |
| fda-pump | pressureRiseC4 | pressure_rise | C4 | held_out | openfoam | 7470 | 8266 | -9.6 % | 0.2883 | - | PASS |
| fda-pump | pressureRiseC5 | pressure_rise | C5 | development | openfoam | 3.624e+04 | 3.533e+04 | +2.6 % | 0.1056 | no | unresolved |
| fda-pump | pressureRiseC6 | pressure_rise | C6 | held_out | openfoam | 3.569e+04 | 2.773e+04 | +28.7 % | 1.682 | - | PASS |
| four-bar | rockerAngle | joint_value | - | development | evaluator | - | - | - | - | - | PASS |
| four-bar | rockerSwing | joint_range | - | development | evaluator | 64.67 | 64.67 | -0.0 % | - | - | PASS |
| four-bar | couplerX | point_x | - | development | evaluator | - | - | - | - | - | PASS |
| four-bar | couplerY | point_y | - | development | evaluator | - | - | - | - | - | PASS |
| gear-train | gearRatio | transmission_ratio | - | development | evaluator | -0.5 | -0.5 | -0.0 % | - | - | PASS |
| nottingham-bearing | p20c_n1000w10 | pressure | n1000w10 | held_out | reduced:reynolds_film | 2.144 | 2.058 | +4.1 % | 1.755 | - | PASS |
| nottingham-bearing | p20c_n3000w10 | pressure | n3000w10 | development | reduced:reynolds_film | 2.245 | 2.141 | +4.9 % | 2.141 | - | FAIL |
| nottingham-bearing | p20s_n3000w10 | pressure | n3000w10 | development | reduced:reynolds_film | 1.697 | 1.6 | +6.1 % | 2.002 | - | FAIL |
| nottingham-bearing | p45c_n3000w10 | pressure | n3000w10 | development | reduced:reynolds_film | 1.392 | 1.128 | +23.4 % | 5.439 | - | FAIL |
| nottingham-bearing | p20c_n3000w15 | pressure | n3000w15 | held_out | reduced:reynolds_film | 3.316 | 3.156 | +5.1 % | 3.295 | - | FAIL |
| nottingham-bearing | p20c_n4000w10 | pressure | n4000w10 | held_out | reduced:reynolds_film | 2.263 | 2.217 | +2.1 % | 0.9406 | - | PASS |
| nottingham-bearing | hmin_n1000w10 | min_film_thickness | n1000w10 | held_out | reduced:reynolds_film | 29.87 | 20.57 | +45.2 % | 3.099 | - | FAIL |
| nottingham-bearing | hminAngle_n1000w10 | min_film_angle | n1000w10 | held_out | reduced:reynolds_film | 41 | 9.44 | +334.3 % | 6.312 | - | FAIL |
| nottingham-bearing | hmin_n3000w10 | min_film_thickness | n3000w10 | development | reduced:reynolds_film | 52.6 | 32.28 | +62.9 % | 6.772 | - | FAIL |
| nottingham-bearing | hminAngle_n3000w10 | min_film_angle | n3000w10 | development | reduced:reynolds_film | 56 | 39.53 | +41.7 % | 3.294 | - | FAIL |
| nottingham-bearing | hmin_n4000w10 | min_film_thickness | n4000w10 | held_out | reduced:reynolds_film | 58.85 | 33.04 | +78.1 % | 8.603 | - | FAIL |
| nottingham-bearing | hminAngle_n4000w10 | min_film_angle | n4000w10 | held_out | reduced:reynolds_film | 61 | 53.41 | +14.2 % | 1.518 | - | PASS |
| nottingham-bearing | hmin_n3000w15 | min_film_thickness | n3000w15 | held_out | reduced:reynolds_film | 41.83 | 25.38 | +64.8 % | 5.484 | - | FAIL |
| nottingham-bearing | hminAngle_n3000w15 | min_film_angle | n3000w15 | held_out | reduced:reynolds_film | 50 | 31.96 | +56.4 % | 3.608 | - | FAIL |
| nottingham-bearing | hmin_n2000w15 | min_film_thickness | n2000w15 | held_out | reduced:reynolds_film | 33.78 | 24.1 | +40.2 % | 3.227 | - | FAIL |
| nottingham-bearing | hminAngle_n2000w15 | min_film_angle | n2000w15 | held_out | reduced:reynolds_film | 44 | 18.94 | +132.3 % | 5.012 | - | FAIL |
| nottingham-bearing | hmin_n4000w20 | min_film_thickness | n4000w20 | held_out | reduced:reynolds_film | 40.13 | 25.81 | +55.5 % | 4.774 | - | FAIL |
| nottingham-bearing | hminAngle_n4000w20 | min_film_angle | n4000w20 | held_out | reduced:reynolds_film | 50 | 40.15 | +24.5 % | 1.97 | - | PASS |
| nottingham-bearing | tRatio_n1000w10 | max_temperature_ratio | n1000w10 | held_out | reduced:reynolds_film | 1.402 | 1.321 | +6.1 % | 0.9417 | - | PASS |
| nottingham-bearing | tRatio_n3000w10 | max_temperature_ratio | n3000w10 | development | reduced:reynolds_film | 1.47 | 1.736 | -15.3 % | 3.092 | - | FAIL |
| nottingham-bearing | tRatio_n4000w10 | max_temperature_ratio | n4000w10 | held_out | reduced:reynolds_film | 1.51 | 1.855 | -18.6 % | 4.01 | - | FAIL |
| peristaltic-pump | flowRate | flow_rate | rotor108 | development | reduced:peristaltic | 6.109 | 1.62 | +277.1 % | 56.11 | - | FAIL |
| peristaltic-pump | driveRatio | transmission_ratio | - | development | evaluator | 0.25 | 0.25 | +0.0 % | - | - | PASS |
| planetary-set | carrierRatio | transmission_ratio | - | development | evaluator | 0.3333 | 0.3333 | +0.0 % | - | - | PASS |
| planetary-set | carrierAt360 | joint_value | - | development | evaluator | 120 | 120 | +0.0 % | - | - | PASS |
| rack-pinion | rackRatio | transmission_ratio | - | development | evaluator | 0.3491 | 0.3491 | +0.0 % | - | - | PASS |
| rack-pinion | rackTravel | joint_range | - | development | evaluator | 125.7 | 125.7 | +0.0 % | - | - | PASS |

## Validation envelope per solver and quantity

What a machine without truth data can quote for a prediction (`docs/validation-envelope.json`): the relative error pred/ref - 1 over every scored point, its mean (bias) and spread, and how many points a mesh ladder resolved. A quantity or solver absent here is unvalidated.

| solver | quantity | points (dev / held-out) | machines | bias | spread | max abs error | max z | pass / fail / unresolved | mesh-resolved |
|---|---|---|---|---|---|---|---|---|---|
| calculix | dissipated_heat | 1 (1 / 0) | disc-brake | +66.4 % | - | 66.4 % | 4.355 | 0 / 1 / 0 | 0 of 1 (1 without a ladder) |
| calculix | hotspot_radius | 1 (1 / 0) | disc-brake | -14.0 % | - | 14.0 % | 4.508 | 0 / 1 / 0 | 0 of 1 (1 without a ladder) |
| calculix | line_max_temperature | 1 (1 / 0) | disc-brake | +4.8 % | - | 4.8 % | 3.036 | 0 / 1 / 0 | 0 of 1 (1 without a ladder) |
| calculix | max_temperature | 1 (1 / 0) | disc-brake | -1.3 % | - | 1.3 % | 0.8615 | 1 / 0 / 0 | 0 of 1 (1 without a ladder) |
| calculix | produced_heat | 1 (1 / 0) | disc-brake | +0.0 % | - | 0.0 % | - | 1 / 0 / 0 | 0 of 1 (1 without a ladder) |
| calculix | time_of_max_temperature | 1 (1 / 0) | disc-brake | -6.7 % | - | 6.7 % | 0.8 | 1 / 0 / 0 | 0 of 1 (1 without a ladder) |
| evaluator | joint_range | 3 (3 / 0) | crank-slider, four-bar, rack-pinion | -0.0 % | 0.0 % | 0.0 % | - | 3 / 0 / 0 | 0 of 3 (3 without a ladder) |
| evaluator | joint_value | 4 (4 / 0) | compound-train, crank-slider, four-bar, planetary-set | +0.0 % | 0.0 % | 0.0 % | - | 4 / 0 / 0 | 0 of 4 (4 without a ladder) |
| evaluator | point_x | 1 (1 / 0) | four-bar | - | - | - | - | 1 / 0 / 0 | 0 of 1 (1 without a ladder) |
| evaluator | point_y | 1 (1 / 0) | four-bar | - | - | - | - | 1 / 0 / 0 | 0 of 1 (1 without a ladder) |
| evaluator | transmission_ratio | 5 (5 / 0) | compound-train, gear-train, peristaltic-pump, planetary-set, rack-pinion | +0.0 % | 0.0 % | 0.0 % | - | 5 / 0 / 0 | 0 of 5 (5 without a ladder) |
| openfoam | pressure_rise | 6 (2 / 4) | fda-pump | +7.8 % | 11.7 % | 28.7 % | 2.373 | 4 / 1 / 1 | 0 of 6 (5 without a ladder) |
| openfoam | pressure_rise_total_to_static | 3 (1 / 2) | fan-01 | -2.5 % | 24.5 % | 31.5 % | 6.663 | 0 / 2 / 1 | 0 of 3 (2 without a ladder) |
| openfoam | torque | 1 (1 / 0) | fan-01 | -7.4 % | - | 7.4 % | 2.714 | 0 / 0 / 1 | 0 of 1 |
| reduced:peristaltic | flow_rate | 1 (1 / 0) | peristaltic-pump | +277.1 % | - | 277.1 % | 56.11 | 0 / 1 / 0 | 0 of 1 (1 without a ladder) |
| reduced:reynolds_film | max_temperature_ratio | 3 (1 / 2) | nottingham-bearing | -9.3 % | 11.0 % | 18.6 % | 4.01 | 1 / 2 / 0 | 0 of 3 (3 without a ladder) |
| reduced:reynolds_film | min_film_angle | 6 (1 / 5) | nottingham-bearing | +100.6 % | 111.3 % | 334.3 % | 6.312 | 2 / 4 / 0 | 0 of 6 (6 without a ladder) |
| reduced:reynolds_film | min_film_thickness | 6 (1 / 5) | nottingham-bearing | +57.8 % | 12.7 % | 78.1 % | 8.603 | 0 / 6 / 0 | 0 of 6 (6 without a ladder) |
| reduced:reynolds_film | pressure | 6 (3 / 3) | nottingham-bearing | +7.6 % | 7.2 % | 23.4 % | 5.439 | 2 / 4 / 0 | 0 of 6 (6 without a ladder) |

## Held-out assembly tasks

Fusion 360 Gallery joint sets. Local backends run **modelled** mode (import the two dataset STEPs, place them, export a 2-solid STEP); Zoo is the frozen **placement** reference. Scored on axis alignment, axial offset, interference and contact (`truth/assembly_task.py`); reported as-is, never tuned. `truth assembly-check` is the worker's local critic. Every scored attempt writes a GLB with the joint animated and a model-viewer page (`results/<backend>/<case>/handoff/assembly.html`).

| case | cadquery | build123d | freecad | zoo | visual |
|---|---|---|---|---|---|
| fusion-01184-assembly | PASS (modelled) | PASS (modelled) | PASS (modelled) | PASS (placement) | [cadquery](../results/cadquery/fusion-01184-assembly/handoff/assembly.html) [build123d](../results/build123d/fusion-01184-assembly/handoff/assembly.html) [freecad](../results/freecad/fusion-01184-assembly/handoff/assembly.html) [zoo](../results/zoo/fusion-01184-assembly/handoff/assembly.html) |
| fusion-12944-assembly | PASS (modelled) | PASS (modelled) | PASS (modelled) | PASS (placement) | [cadquery](../results/cadquery/fusion-12944-assembly/handoff/assembly.html) [build123d](../results/build123d/fusion-12944-assembly/handoff/assembly.html) [freecad](../results/freecad/fusion-12944-assembly/handoff/assembly.html) [zoo](../results/zoo/fusion-12944-assembly/handoff/assembly.html) |
| fusion-13786-assembly | PASS (modelled) | PASS (modelled) | PASS (modelled) | PASS (placement) | [cadquery](../results/cadquery/fusion-13786-assembly/handoff/assembly.html) [build123d](../results/build123d/fusion-13786-assembly/handoff/assembly.html) [freecad](../results/freecad/fusion-13786-assembly/handoff/assembly.html) [zoo](../results/zoo/fusion-13786-assembly/handoff/assembly.html) |
| fusion-15317-assembly | PASS (modelled) | PASS (modelled) | PASS (modelled) | PASS (placement) | [cadquery](../results/cadquery/fusion-15317-assembly/handoff/assembly.html) [build123d](../results/build123d/fusion-15317-assembly/handoff/assembly.html) [freecad](../results/freecad/fusion-15317-assembly/handoff/assembly.html) [zoo](../results/zoo/fusion-15317-assembly/handoff/assembly.html) |
| fusion-16418-assembly | PASS (modelled) | PASS (modelled) | PASS (modelled) | PASS (placement) | [cadquery](../results/cadquery/fusion-16418-assembly/handoff/assembly.html) [build123d](../results/build123d/fusion-16418-assembly/handoff/assembly.html) [freecad](../results/freecad/fusion-16418-assembly/handoff/assembly.html) [zoo](../results/zoo/fusion-16418-assembly/handoff/assembly.html) |

## Reliability and effort

Hosted runs only; score-only re-judgements are excluded. `first` is the first hosted attempt's scorecard, `final` the latest scored one. Effort comes from the latest `results/<design>` stage JSONs (worker seconds/commands across plan, model, retry and blockout; engine-call ledger rows; transient/timeout rows as tool failures) and from `results/<design>/telemetry.jsonl` (worker wall by role, backends, over-budget turns, evaluator wall). Human interventions are 0 by construction for `truth run`.

| case | arm | hosted runs | first PASS | final PASS | pipeline retries | mean s/run | worker s | worker cmds | engine calls | tool failures | blockout iters | worker s by role | backends | over-budget turns | evaluator s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bearing-housing | spec-and-views | 41 | yes | yes | 8 | 1361 | 604 | 12 | 4 | 0 | - | model 604 | cursor | 0 | 45 |
| chiral-keyplate | text-only | 4 | yes | yes | 0 | 986 | 322 | 20 | 10 | 0 | 1 | blockout 185, model 137 | cursor | 0 | 29 |
| compound-train | spec-only | 6 | yes | yes | 0 | 2252 | 0 | 0 | 0 | 0 | - | asm-draft 504, assemble 361 | cursor | 0 | 132 |
| crank-slider | spec-only | 6 | yes | yes | 0 | 1697 | 0 | 0 | 0 | 0 | - | asm-draft 584, assemble 218 | cursor | 0 | 53 |
| disc-brake | construction-steps | 2 | no | no | 0 | 1846 | 0 | 0 | 0 | 0 | - | asm-draft 1470, assemble 127 | cursor | 0 | 2952 |
| enclosure-base | spec-and-views | 39 | yes | yes | 4 | 1060 | 348 | 8 | 4 | 0 | - | model 348 | cursor | 0 | 62 |
| fan-01 | supplied-cad | 3 | no | no | 0 | 20169 | 0 | 0 | 0 | 0 | - | asm-draft 3385, assemble 3436 | cursor | 1 | 61086 |
| fda-pump | supplied-cad | 4 | no | no | 0 | 169 | 0 | 0 | 0 | 0 | - | asm-draft 1279, assemble 1962 | cursor | 1 | 22635 |
| four-bar | spec-only | 6 | yes | yes | 0 | 1756 | 0 | 0 | 0 | 0 | - | asm-draft 678, assemble 309 | cursor | 0 | 66 |
| fusion-01184-recon | renders-and-sheet | 4 | yes | yes | 1 | 1212 | 408 | 24 | 18 | 0 | 1 | blockout 194, model 214 | cursor | 0 | 41 |
| fusion-12944-recon | renders-and-sheet | 5 | yes | no | 2 | 1991 | 2298 | 59 | 20 | 0 | 1 | blockout 272, correction 1483, model 998 | cursor | 1 | 416 |
| fusion-13786-recon | renders-and-sheet | 4 | yes | yes | 2 | 975 | 544 | 16 | 16 | 0 | 1 | blockout 133, model 411 | cursor | 0 | 57 |
| fusion-15317-recon | renders-and-sheet | 4 | yes | yes | 1 | 2876 | 876 | 26 | 15 | 0 | 1 | blockout 195, correction 134, model 547 | cursor | 0 | 110 |
| fusion-16418-recon | renders-and-sheet | 4 | yes | yes | 3 | 2650 | 845 | 25 | 17 | 0 | 1 | blockout 236, correction 161, model 448 | cursor | 0 | 64 |
| gear-pair | spec-only | 5 | yes | yes | 0 | 1170 | 863 | 16 | 16 | 0 | 1 | blockout 231, model 632 | cursor | 0 | 239 |
| gear-train | spec-only | 7 | yes | yes | 0 | 2824 | 0 | 0 | 0 | 0 | - | asm-draft 600, assemble 219 | cursor | 0 | 71 |
| nasa-atb-axisymmetric-bump | text-and-points | 4 | yes | yes | 0 | 1324 | 526 | 18 | 10 | 0 | 1 | blockout 234, model 292 | cursor | 0 | 34 |
| nasa-backstep-driver-seegmiller | text-only | 6 | yes | yes | 0 | 1049 | 312 | 10 | 11 | 0 | 1 | blockout 226, model 86 | cursor | 0 | 25 |
| nist-am-test-artifact | drawing-renders-sheet | 4 | yes | yes | 3 | 6484 | 868 | 15 | 11 | 0 | 1 | blockout 182, correction 382, model 304 | cursor | 0 | 58 |
| nist-amb2022-01-bridge | drawing-only | 5 | no | yes | 1 | 637 | 446 | 15 | 11 | 0 | 1 | blockout 185, model 261 | cursor | 0 | 26 |
| nist-amb2022-01-bridge | mesh-input | 4 | yes | yes | 0 | 1425 | 394 | 13 | 11 | 0 | 1 | blockout 172, model 222 | cursor | 0 | 27 |
| nottingham-bearing | paper-text | 1 | no | no | 0 | 45 | 0 | 0 | 0 | 0 | - | asm-draft 605, assemble 891 | cursor | 0 | 100 |
| peristaltic-pump | published-parts | 2 | no | no | 0 | 1574 | 0 | 0 | 0 | 0 | - | asm-draft 1484, assemble 880, correction 1491 | cursor | 0 | 708 |
| planetary-set | spec-only | 6 | yes | yes | 0 | 2657 | 0 | 0 | 0 | 0 | - | asm-draft 892, assemble 229 | cursor | 0 | 183 |
| prusa-mini-extruder-front | renders-and-sheet | 21 | no | yes | 18 | 6094 | 1103 | 31 | 16 | 0 | 1 | blockout 277, correction 42324, integrate 705, model 1952, module 3181, partition 304, retry 627 | cursor | 8 | 950 |
| prusa-mini-extruder-front-ecr1 | ecr1 | 0 | no | no | 0 | - | 1103 | 31 | 16 | 0 | 1 | blockout 277, correction 42324, integrate 705, model 1952, module 3181, partition 304, retry 627 | cursor | 8 | 950 |
| rack-pinion | spec-only | 6 | yes | yes | 0 | 1931 | 0 | 0 | 0 | 0 | - | asm-draft 646, assemble 161 | cursor | 0 | 60 |
| rpi5-enclosure | requirements | 5 | no | yes | 0 | 858 | 505 | 13 | 21 | 0 | 1 | blockout 195, ecr 428, model 310 | cursor | 0 | 125 |
| rpi5-enclosure-ecr1 | ecr1 | 5 | no | yes | 0 | 274 | 505 | 13 | 21 | 0 | 1 | blockout 195, ecr 428, model 310 | cursor | 0 | 125 |
| rpi5-enclosure-ecr2 | ecr2 | 4 | no | yes | 0 | 623 | 505 | 13 | 21 | 0 | 1 | blockout 195, ecr 428, model 310 | cursor | 0 | 125 |
| rpi5-enclosure-ecr3 | ecr3 | 5 | yes | yes | 0 | 1068 | 505 | 13 | 21 | 0 | 1 | blockout 195, ecr 428, model 310 | cursor | 0 | 125 |
| spleen-c1-blade | table-and-notes | 5 | no | yes | 0 | 1741 | 546 | 11 | 10 | 0 | 1 | blockout 312, model 234 | cursor | 0 | 101 |
| voron-sb-duct | renders-sections-sheet | 16 | no | yes | 15 | 10776 | 939 | 16 | 14 | 0 | 1 | blockout 213, correction 34995, integrate 419, model 1351, module 6151, partition 350 | cursor | 16 | 1498 |
| voron-sb-duct-ecr1 | ecr1 | 0 | no | no | 0 | - | 939 | 16 | 14 | 0 | 1 | blockout 213, correction 34995, integrate 419, model 1351, module 6151, partition 350 | cursor | 16 | 1498 |

## Calibration log

- 2026-09-15 [nasa-backstep-driver-seegmiller] codex.KCL_RULES now forbids equality asserts between contract parameters (sanity guards only); initialize.draft_brief now steers edit tests toward independent parameters and defines an edit test on a derived parameter as a formula override. The failing model was corrected on its own thread and re-verified from the verify stage (see attempts.yaml). — editability is a scorecard item; a hard equality lock makes the KCL non-parametric in the contract's terms
- 2026-09-15 [nist-amb2022-01-bridge] `opencad.zoo.require_credits()` preflight in `run`, `blockout` and `truth run` (fails fast with the billing URL); `python -m opencad credits`; `truth restore <case>` for interrupted runs; `truth run --resume-from blockout|pipeline` to continue from a published design without paying for a second contract draft. — hosted-engine budget is a run precondition, not a mid-run surprise; a refused engine must not consume Codex time
- 2026-09-15 [spleen-c1-blade] kcl-docs/patterns.md gained the dense-profile idiom (fitted arcs / adaptive polyline) with the runnable example under docs/notes — the model stage must not discover curve-construction limits by trial against a billed engine
- 2026-09-15 [pipeline] Engine (tessellated) measurements are now evidence only; the envelope and mass-properties gates read the STEP via OpenCascade; edit tests export STEP and measure with OpenCascade. — gates must fail on geometry, not on engine bookkeeping
- 2026-09-15 [nist-amb2022-01-bridge] `require_credits` treats paid/PAYG plans as executable at zero prepaid credits. Blockout measures the exported STEP with OpenCascade (engine box is evidence only) and can remeasure an existing main.kcl without another Codex session. `correction_message` no longer falls back to the engine bbox. Pipeline skips the bounded Codex retry when inspect recorded a tooling exception rather than a geometry miss. — a refused or padded engine number must not consume Codex time or rewrite correct geometry
- 2026-09-15 [nist-amb2022-01-bridge] Coplanar FaceSpecs are assigned one measured face each (optional in-plane `center`, else greedy area match). Inspect and export_integrity accept `components >= solid_count` when the mesh is watertight. — repeated coplanar faces and internal voids are real geometry, not inspect failures
- 2026-09-15 [nist-amb2022-01-bridge] `zoo.run` retries hosted calls on modeling-connection interrupts (4 attempts, 5/10/20 s backoff). Export stage ok and the export_integrity gate require deterministic STEP plus STL only; GLB is a viewer extra recorded in errors when it flakes. — a transient Zoo disconnect on a viewer format must not fail a geometrically correct part
- 2026-09-15 [spleen-c1-blade] `check_bundle` now accepts `profile.png` (and still accepts `profile.json`) as a deterministic profile-ingest artifact. The published bundle was kept and the case resumed from blockout. — an ingest preview must not fail a contract that already checks out
- 2026-09-15 [spleen-c1-blade] Mesh silhouette IoU now rasters the long axis at 2400 px so a thin trailing edge is not decided by aliasing. Deviation records `silhouette_px_long` as evidence. — a 0.03 mm surface match must not fail a 1-pixel silhouette fringe
- 2026-09-15 [spleen-c1-blade] Filename leakage now ignores truth basenames that are also arm inputs. A `truth/` path in KCL is still a fail. — citing the authoritative source table is not importing sequestered truth
- 2026-09-16 [pipeline] `zoo.classify` labels transient / credits / kcl / timeout / unknown. `run` retries only transient (4 attempts). `ZooCreditsError` stops the pipeline without a Codex brief; `ZooKclError` is a geometry class. Ledger is one row per attempt (`attempt`, `class`, `seconds`). Hosted calls take `~/.cache/opencad/zoo.lock`. Verify ok is format+lint+hygiene; analyze failure records `engine: {status: missing, class}` and bbox/volume `ok: null`. Blockout continues to the STEP measure when analyze flakes. `export_agreement` discloses a missing engine volume and fails only on a kcl-class miss. Pipeline skips the Codex retry on transient/timeout/credits. Credit banner prints plan, prepaid, PAYG, and a call forecast. Coupon and bracket `--from-stage verify --no-retry` both PASS. — a dead Zoo connection must not consume a Codex retry or fail a geometrically correct part
- 2026-09-16 [spleen-c1-blade] FaceSpec/Observable `mode` (default `one`) and `center`; scorer groups faces and uses the shared `assign_coplanar` helper; `sum` is explicit (NIST bottom/tabs/bridge-top). Profile analyse now reports landmark chord/stagger, area centroid, and a segment self-intersection count. `profile2d.chord_definition` is `farthest_pair` (default) or `landmarks`; SPLEEN gained `midspan_landmarks` (measured 52.2846 mm, -24.4008 deg) and was re-pinned. Scorecards record `hash_binding.metrics` (silhouette_px_long, samples, seed, scorer_version 2). `brep.section` falls back to Section wires (`method`). Mesh `void_shells` / inspect requires `components - void_shells == solid_count`. `PointQuantity.note` added. Four existing arms still PASS (SPLEEN 11/11). — the next coplanar or thin-feature check must use a named definition, not an implicit sum or farthest-pair
- 2026-09-16 [pipeline] `truth score` logs an attempt (`resume_from: score`, stage scored, scorecard, step_sha256). `truth status` lists truth presence, vault orphans, published design, KCL, latest verdict, last attempt stage (exit 1 if any truth is missing). `restore` takes newest mtime, refuses when truth/ exists, and re-runs verify_pins. `truth run --resume-from publish` accepts `designs/.staging-<design>` after check_bundle. CLI `--from-stage` help states that plan deletes `parts/<part>/*.kcl`. — scorecards, sequesters, and staging resumes must be operable without hand-edited YAML
- 2026-09-16 [nasa-backstep-driver-seegmiller] Reference allowlist is prefixes (`profile.*`, `reference.*`, `reference-sections*`, `silhouette-*`). Digest emits face mode/center, each edit_test delta, COM note, and both chords with "farthest-pair is not the documented stagger". `draft_brief` steers table-part edits, coplanar `center`, and probe clearance. `plan.brief` names the 74-arc dense-profile idiom. initialize-cad/cad-qa/create-cad and AGENTS.md record STEP-authoritative blockout and the hot-reload warning. — Codex must see scoring policy in the brief rather than rediscover it after a failed publish
- 2026-09-16 [spleen-c1-blade] `scripts/derive_spleen_truth.py --source v1` cuts the central v1 blade (plate at y < 0; box y from 0.05) and maps it into the table frame. Measured v1-vs-v2 p95 is 0.568 mm. Manifest gained the derived v1 STEP/STL and `not_matching_v1_wrong_stagger` with min_distance 0.28 mm (half of that). Re-pinned. Existing handoff still PASS 12/12; the other three arms still PASS. — a negative reference must be a real published file, not a synthetic transform of the truth
- 2026-09-16 [chiral-keyplate] New class-D calibration case. `scripts/derive_chiral_truth.py` builds an 80×80×8 mm plate with four 16×6×4 mm C4 pinwheel pockets and a YZ-mirrored STL. Manifest requires bbox/volume/COM/solid_count, a z=2 section, four centred pocket floors, deviation vs truth, and not_matching vs the mirror. Registered, pinned, hosted `truth run`. Four existing arms still PASS on rescore. — a mirror that preserves volume and silhouette must fail a required observable, not slip through as a PASS
- 2026-09-16 [pipeline] Tolerant tokenizer (comments/strings masked, depth-0 assignments, import following) finds numeric parameters in every `.kcl`. `rewrite_parameter_in_tree` edits the defining module. `hygiene.unused_parameters` lists identifiers with no reference beyond the definition; `source_hygiene` FAILS when one of those has an `edit_test`, discloses otherwise. Settings match on whitespace-stripped `kclVersion=2.0` / `defaultLengthUnit=mm`. Multi-file fixture and a static pass over existing `parts/*/main.kcl`. Four existing arms still PASS on rescore. — edit tests and hygiene must see the same constants the model actually binds
- 2026-09-16 [nasa-atb-axisymmetric-bump] First revolve case. `scripts/derive_bump_truth.py` builds both R2 values; truth STEP/STL at 183.0 mm. `profile2d` gained `reference_closed: false` (one-way p95) and `reference_scale` / `ProfileIngest.scale_to_mm` for the chord-normalized NASA table. `read_table` treats whitespace `.dat` files as split fields, not CSV with a leading empty column. Manifest arm `text-and-points`. Four existing arms still PASS on rescore. — a revolve through Codex must be scored on the meridian and the unit trap, not only bbox/volume
- 2026-09-16 [pipeline] Folded the landed items into Known engine behaviours, Lifecycle, Validate, and repository layout. Future improvements now holds residuals only (non-planar faces, Class A, sweep/loft, assemblies, `--keep-kcl`, CI). README corpus is five cases and six arms. Regenerated `docs/validation-envelope.md`. — the map must describe the corpus that exists, not the campaign that produced it
- 2026-09-17 [pipeline] Mutant harness: `truth/mutants.py` (scale, translate, mirror, rotate, fill_box, cut_box, shift_hole, fuse_solids, remove_solid) + `python -m opencad.truth mutate` scoring `truth/cases/<case>/mutants.yaml` against the passing candidate; 24 mutants across the six arms all FAIL with baselines PASS. Scorer v3: `score_checks` shared with the harness; new observable kinds `cylinder` (axis point/direction/radius/kind via merged GeomAbs_Cylinder faces, reports the axis offset), `cylinder_count`, `plane` (arbitrary normal). Contract: `acceptance.cylinders/planes/dimensions`, `Verify` methods cylinder/plane/dimension, `Interface.checks` (pinned acceptance items), `PartContract.interface_checks()`. Gates: `contract_provenance` now fails on unresolved stated/measured source paths, `blocking:` open questions, and unenforced interfaces on prototype parts; `features` covers cylinders/planes/dimensions; the correction message says "cylinder X is 0.7 mm off its axis". `truth report` gains a reliability/effort table (`truth/effort.py`). Evaluator-side input generators: scripts/render_reference.py, dimension_sheet.py, pdf_pages.py. Stale NIST bridge inspect.json (pre void-shell accounting) re-inspected; both arms still PASS. — a PASS is only evidence once the checker is shown to reject the failures we care about
- 2026-09-17 [nist-am-test-artifact] `codex.dispatch` detects a network-stalled turn (>= 3 reconnect errors, no turn.completed, exit != 0), waits for connectivity (`wait_for_network`, TCP to api.openai.com, up to 6 h) and continues the same thread with a short nudge, up to 2 times, without charging the caller's round budget; stalls are recorded in the Codex summary. `Sequester` now also moves manifest.yaml and mutants.yaml (`truth restore` handles both vault layouts). Draft brief: the blockout band must cover the solids that reach the envelope extremes; `edit_test.sweep` and `infeasible_deltas` explained. KCL_RULES: assert-guard every parameter so an impossible value fails loudly. — a dead network is not a failed round, and the observable list is truth
- 2026-09-17 [pipeline] `EditTest.sweep` (values or min/max/steps) and `EditTest.infeasible_deltas`; the edit stage rebuilds every sweep value (valid, solid count, bbox linear in the declared bbox_delta, volume monotonic, undriven interfaces preserved) and requires a kcl-class refusal for each infeasible value (a silent build fails). Interface preservation on the primary delta: pinned items not driven by the edited parameter (via Feature.parameters) must match the baseline STEP. `edit_robustness` failures are retryable when tooling worked. New `python -m opencad ecr <part> <request.md> --contract-delta delta.yaml [--label] [--expect-infeasible]`: baseline the pinned interfaces, revise the contract into designs/<part>/ecr/<label>/, brief Codex on the model thread, re-run verify->gates into results/<part>/ecr/<label>/, compare preserved items with the baseline, one bounded retry; an infeasible request must be refused with INFEASIBLE and an untouched KCL. Shared `opencad/interfaces.py`. — a single successful nominal model should not score like one that regenerates across its declared range
- 2026-09-17 [prusa-mini-extruder-front] `stage_bundle` writes only contract.yaml and brief.md (plus sources/) instead of copying the template tree; the stray template main.kcl is deleted. Attempt 1 is resumed from publish with the drafted bundle (`--resume-from publish`). The input description text is left as pinned (the sheet is declared authoritative in it). — an orchestrator artifact must never cost the worker a round
- 2026-09-17 [prusa-mini-extruder-front] `program_failed`: a kcl-class analyze/export failure is model-attributable and never suppresses the retry; inspect/edit are skipped with the export cause recorded instead of raising; the correction message leads with THE PROGRAM DOES NOT EXECUTE and the engine error. Model brief: the deliverable must always execute (keep and restore a checkpoint), plus the coincident-face recipe for "cannot handle this 3D subtraction". model.json records `self_reported_incomplete`. — a file that does not run is the clearest possible retry signal, not a tooling fault
- 2026-09-17 [pipeline] Contract: `acceptance.solids/hardware/clearances/passages/thickness/probes/ cylinder_counts/gears/meshes` (schemas), evaluated by `geomcheck/multibody.py`, `geomcheck/assembly.py` (select_solid, clearance, thickness by inward rays, voxel passage with plug or closing-radius sealing) and `geomcheck/gears.py` (tooth count from a polar section profile, mesh_motion rotation sweep); inspect/gates/correction message wired; Codex digest lists them. Truth: observable kinds solid, clearance, passage, thickness, probe, teeth, gear_mesh, manifest `hardware`, `expected_min`, solid-scoped section/profile2d, `outer_only` profiles (outer wire of the largest section face); scorer v4. Cylinders are merged per solid; `match_cylinder` prefers the coaxial candidate whose extent contains the spec point. Mutants: translate_solid, case-relative `source`, baseline scoring tessellates its own STL. Cases staged and pinned: rpi5-enclosure (class C requirements, 28 observables, 11 envelopes), voron-sb-duct (24 observables, passages sealed at 3.2 mm), gear-pair (16 observables incl. mesh motion). Fusion 360 joint sets preselected by seed (truth/cases/_fusion360-selection.yaml; two rejected for reference self-interference). — functional parts are judged on fit, motion and interior, none of which a bbox or a volume can see
- 2026-09-17 [prusa-mini-extruder-front] `_dispatch_once` treats a network-class failure string as a recovered warning when the process exited 0 and events show `turn.completed`; recorded as `network_recovered` in the Codex summary. Mutant harness: a mutant with its own `source:` is still baselined against the case's passing source; the Voron wall-opening mutant cuts to the duct wall (x >= -27.5). — a completed turn is a completed turn; the network's hiccups are evidence, not verdicts
- 2026-09-17 [prusa-mini-extruder-front] `truth run --resume-from retry` keeps parts/<design>/main.kcl and the model.json thread and runs the pipeline from `verify` (re-measure, gates, the bounded retry). Resumed Codex threads get a preamble that does not ask them to re-read the skills (codex_exec.py CONTRACT_RESUME); CODEX_REASONING_EFFORT env hook, default max. — an interrupted correction pass is continued, not repeated from scratch
- 2026-09-17 [prusa-mini-extruder-front] No pipeline change against the case. Stuck rule applied: recorded in results/_campaign/ledger.md, Phase 2 ECR arm deferred with the base, campaign continues to Phase 3. — the plan's three-attempt rule; a fourth identical attempt has no new information to act on
- 2026-09-17 [rpi5-enclosure] Run stopped before geometry existed (1492 s draft + 2 min blockout spent). Case text corrected, not tuned: requirement 7 names the p05 statistic the scorer uses and the boss annulus as the accepted exception; requirement 9 states that sweep values only have to regenerate a valid enclosure and that no assert may reject 15..35. The manifest observables are unchanged (wall_min was already p05). Re-run with --force. — a requirement the author contradicted is a case bug found by the agent, not a scorer to relax
- 2026-09-17 [rpi5-enclosure] Parameter.name validation mirrors the lint rule (measured on the CLI: usbCX, holeID, mountXY, abcXYZw, snake_case, Upper fail; usbCx, sdYMin, hdmi0X, abcXYz pass), so check-bundle sends the draft back; the draft brief states the rule; the blockout correction names lint/format failures and says when the geometry already passes. The published contract's `usbCX` was renamed `usbCx` (contract, brief, blockout KCL), the blockout re-measured without a Codex session (PASS), run resumed from the pipeline. — a check that fails must say why; an identifier rule the model must obey belongs in the contract validator
- 2026-09-17 [rpi5-enclosure] `floor_probe` now probes the stated point (42.5, 28, -6) instead of an author's assumption. Case re-pinned and re-scored without another run. The requirement text and every other observable are unchanged. — a class-C observable must follow from the requirements document the agent was given
- 2026-09-18 [rpi5-enclosure-ecr1] scripts/rpi5_ecr_deltas.py constructs the post-change reference solid in OpenCascade (wall band raised / shells grown with the wall slabs copied outward, pilots re-cut, coplanar faces unified) and re-measures every named face (level, area, in-plane centroid), section, dimension, volume, centroid and surface area from it; `--check` applies the delta and proves the reference passes the revised contract's face, cylinder, section, dimension, bbox and volume checks before Codex is briefed. `ALLOWED_TOP` gains `ecr`. `truth ecr <case>` sequesters the request case, runs the ECR on the base design with inputs/contract-delta.yaml, restores the base KCL and scores results/<design>/ecr/<label>/handoff (Arm.ecr); the ECR stage always writes its handoff and keeps the changed main.kcl next to it. — a revised contract must be self-consistent before the modeller sees it; the evaluator can build the expected geometry when the request determines it
- 2026-09-18 [rpi5-enclosure-ecr2] check_thickness compares with 1 µm of slack (far below any tolerance in play); rpi5_ecr_deltas.py derives the edit-test volume deltas from the reference solid (the notched ring section x delta for headroom; the full ring plus four boss disks for the standoff height), which reproduce the measured 4130.0 and 1234.763 exactly. ECR-2 re-scored without another run: PASS 28/28. — a check that fails on 6e-15 mm is a rounding artefact, not a wall; edit expectations must follow the revised geometry
- 2026-09-18 [voron-sb-duct] No pipeline change against the case. Stuck rule applied: recorded in results/_campaign/ledger.md; Phase 4 ECR arm deferred with the base; campaign continues to Phase 5. — the plan's three-attempt rule; another identical kernel-boolean loop has no new information
- 2026-09-19 [gear-pair] export_integrity and inspect judge watertightness per shell when solid_count > 1 (mesh.analyze_mesh reports components_watertight / solids_watertight); gears.mesh_motion samples coarse-to-fine (12 coarse poses in parallel worker processes, then the requested fine resolution across the coarse interval on each side of the worst pose): 23 poses in 72 s on the same STEP with the same verdict (zero interference, gap 0.0469-0.0470 mm). Inspect and edit results are cached by the hashes of the STEP/STL/KCL/contract they measure. — touching bodies are not a topology defect; a sweep that costs 20 minutes per pass and repeats three times is an evaluator cost, not evidence
- 2026-09-19 [fusion-01184-recon] Pipeline only: sub-contracts drop interface pins the group does not own and pull in cross-referenced solids/faces as measurement context; a tooling exception in a worker stage keeps the run state and the vault (exit 3) instead of a crash; a vault restored by a crash is re-sequestered on --continue; the kernel-stuck regex matches kernel failure phrases only. No case, manifest, contract or truth file was edited. — held-out cases judge the pipeline; the pipeline's own contract checks are a drafting-quality signal, logged here and left for /initialize-cad
- 2026-09-19 [gear-pair] Hosted calls made without the global lock take one of two cross-process slot locks (OPENCAD_ZOO_SLOTS, also used by the worker's `opencad zoo` wrapper); the connection error is classed transient and retried; edit results with tooling-class failures are never cached. — a platform limit is not evidence about the part
- 2026-09-19 [fusion-12944-recon] interfaces.compare gains mode="edit" (used by the edit stage): a driven item must still exist after the rebuild but is not re-judged against the unedited contract's values, and only the undriven pinned items decide the preservation verdict. ECR keeps judging driven items by the revised contract. Evaluator cache version bumped so the old verdicts are not replayed; KCL assert lines are quoted when a sweep value fails to execute. — an edit test rewrites one parameter on purpose; judging the features it drives by the unedited values fails every correct parametric part whose contract pins interfaces
- 2026-09-19 [fusion-01184-recon] geomcheck.assembly.passage takes the closing radius in whole voxels rounded down, reports `seal_effective_mm`, and returns an explicit error when the closing fills both probe points ("seal a uniform bore with plugs over its mouths"). — a seal that removes the passage it is meant to test is a measurement error, not a missing feature
- 2026-09-19 [fusion-16418-recon] gears.tooth_count profiles the outer loop only (samples above tip radius minus three modules) and takes the root radius from that loop. Mutant pinion_19_teeth is still caught. — a tooth count is a property of the toothed boundary, not of a bore drawn inside it
- 2026-09-19 [fusion-13786-recon] brep.cylinders merges coaxial equal-radius faces only when their axial extents touch or overlap (gap <= 1e-3 mm); gapped segments stay separate records. brep.match_cylinder then matches a spec against single segments and against unions of consecutive coaxial segments, preferring the candidate whose length matches the spec's `length`: two Ø2 x 5 specs get two bores, a Ø7.94 x 71.4 spec spanning a slot or a Ø50.8 x 13.5 hub OD interrupted by a groove get the union (fusion-15317's truth observables keep passing). Mutants rpi5 4/4 and gear-pair 4/4 still caught. — two bores separated by 90 mm of plate are two features in every downstream check (length, count, edit tests)
- 2026-09-19 [fusion-12944-recon] features.assign_coplanar breaks centre ties with the relative area error and, when no single hit matches a spec's area, accepts two or three coplanar hits whose areas sum to it with the area-weighted centroid at the spec centre (`merged_faces` recorded). — a seam split and a shared centre are export artefacts; the contract names one face and the geometry has one
- 2026-09-19 [fusion-12944-assembly] scripts/derive_fusion_heldout.py --assembly-only rewrites inputs/assembly-task.md (task_text_version 2) and adds inputs/joint-task.json: per side the surface type, radius, body-local bbox, key_point_type and the key point in the body's local frame with its axis direction; the evaluator's definitions (axial offset between key points along body two's placed axis, tolerances, interference rule, flip rule) and the motion limits. `truth assembly-check <work>` computes the same numbers from assembly.yaml without the truth; the assemble brief tells the worker to compute the placement from the key points. Truth (joint_set.json), scorer and tolerances unchanged; the v1 results stay in the ledger. — a joint is defined by two geometries with key points plus offset/flip/angle; a task that omits the key points cannot be solved, only guessed
- 2026-09-19 [pipeline] Added backends/{cadquery,build123d,freecad} with local sandbox runner, per-backend skills under .agents/skills/backends/, sources fetched by scripts/fetch_sources.py, and bakeoff CLI. Worker briefs and critics now come from language.rules/skills/critics. FreeCAD runner is freecadcmd via OPENCAD_FC_* env (argv is reserved for documents). — hosted Zoo is out of budget; the bake-off needs local engines and equal skill packs
- 2026-09-19 [pipeline] freecad/runner.analyze_body falls back to shape.Solids[0]; language.critics() quick includes --backend <id>; opencad quick infers the backend from parts/<backend>/<part>. — local critic and analyze must work for a normal PartDesign feature tree without a worker workaround
- 2026-09-19 [pipeline] FreeCADEngine.export caches STEP by source-tree sha256 so the same program yields the same bytes (header still normalised). CadQuery skill: extrude+cut-before-union for loft faces that fail triangulation; add length at a bow/stern block instead of stretching a mid-station loft. — header normalisation is the determinism contract; a non-deterministic kernel must not fail a geometrically identical restore
- 2026-09-20 [pipeline] stl_to_glb maps (x, y, z) mm → (x, z, -y) m (Zoo's glTF convention). `opencad correct` issues a deliberate improve-N turn on the model thread and re-verifies from verify. Backend skills: fair hulls are non-ruled lofts through spline/arc sections of equal edge count; FreeCAD keeps a planar keel Pocket at z=0. — the viewer file must match Zoo so a visual compare is scale- and axis-honest; ruled polylines are a documented hull defect, not a gate miss
- 2026-09-20 [pipeline] Local and FreeCAD STL deflection is 0.02 mm. A new retry sequence supersedes leftover `correction-` orders so a later campaign cannot complete against an old turn. FreeCAD skill already requires a planar keel Pocket; the restored part stays the passing faceted loft until a later turn can keep the band. — a smooth hull must still tessellate within the agreement gate; a done work-order key is not a new turn
- 2026-09-20 [pipeline] acceptance.symmetry SymmetrySpec (benchy: mirrorY, plane y, at 0, max 0.1 / p95 0.05); inspect.mirror_deviation; features gate + inspection_lines; interface preservation; lint when frame/datums/interfaces mention mirror|symmetr without a spec. Nine crease-aware views (view-all.png 3×3), view-symmetry heatmap, SNAPSHOT_ANGLES complete. quick --stl writes quick-views.png; worker protocol requires a Visual: line; correct records delta_vs_previous. Tightening only; other designs get the lint warning, not an edit. — a folded hull that preserves volume, bbox, sections and named faces is not a passing reconstruction; symmetry and complete views are the machine checks that class needs
- 2026-09-20 [nist-am-test-artifact] acceptance.blockout re-derived as 101786.780822 mm3 +-1 % (100768.9-102804.6; the bare plate is outside by construction) with the formula noted in the contract and in the brief's two blockout rows; finished volume, surface area, COM, envelope and every other acceptance item untouched. lint_contract rule 6: problem when acceptance.blockout.volume_max is below acceptance.volume.expected; only this contract was flagged across designs/. Zoo artefacts replayed without a hosted call (inspect/gates/report, engine_calls 0): gates still 11/0/1, report PASS; blockout.json left as recorded. Investigation: results/_bakeoff/investigations/001-nist-am-blockout-band.md. — a blockout that must fill the finished envelope cannot be banded below the finished solid; the band was wrong, not the geometry
- 2026-09-20 [rpi5-enclosure] backends/local.py `collect_shapes` / `result_shape`: a lone shape is returned as is (single-solid STEP bytes unchanged: nine fresh exports sha256-equal to the frozen results/<backend>/<part> files), several become one TopoDS_Compound; an empty result is a program-class ValueError. CadQuery and build123d `_shape` delegate to it (Workplane stack, list/tuple, builder `.part`). FreeCAD runner: `result` is one Body or a tuple of Bodies (N, checked by TypeId), `Part.export` of all of them, `analyze_bodies` with combined bbox, summed volume/area and volume-weighted centroid (Part.Compound has no CenterOfMass). Rules and skills for the three backends: one body per contract solid, `base.add(lid)` / `[base, lid]` / `Compound([...])` / `result = (base, lid)`, never fuse separate bodies. tests/test_multi_solid_export.py: unit tests without freecadcmd, two- and three-solid CadQuery, two-solid build123d and (when installed) two-Body FreeCAD end to end: 2/3 solids, summed volume, named-solid selection, watertight per-shell STL. solid_count checks untouched. Investigation: results/_bakeoff/investigations/002-multi-solid-export.md. — a runner that keeps the first body turns a correct two-part model into a solid_count miss the worker cannot fix
- 2026-09-20 [rpi5-enclosure-ecr3] scripts/rpi5_ecr_deltas.py ecr3() derives the whole delta from the parameters for the applied layout (corner posts removed above the floor plate, feet kept, four 8 x 5.6 side bosses at x = 50/75, pilots on (x, -4.5)/(x, 60.5), lid over walls + flanges with Ø3.2 holes): floor 6023.6 (centre x 43.094993), standoff 960.967868, pcb 859.84, ports 658.24, rim 638.605046, lid 5758.470091 (centre x 43.010657), headroom +5 -> 3291.2, standoffHeight +1 -> 1009.402822; corner probes removed/relocated, side_pilots_void and side_boss_material added, shell_material moved to x = 62.5, parameters sideScrewXNear/sideScrewXFar/sideLidHoleDiameter added and lidHoleDiameter removed, descriptions restated, side_fasteners verified; truth inputs/contract-delta.yaml rewritten from it and designs/.../ecr3/{delta,contract}.yaml regenerated as ecr.run does (valid, lint problems none). interfaces.compare: a changed item no longer declared is "removed by the request" (ok), a revised one is judged by the revised contract, an un-pinned one is ok; untouched items that vanish still fail. ecr.brief diffs parameters/features/interfaces against the base contract, prints every changed acceptance kind (probes, counts with region, solids, hardware, ...) and a "Removed by this request" section described from the base contract. inspect_stage.count_specs carries `region` (quick inherits). Scratch replay of the frozen Zoo ECR-3 STEP (OpenCascade only, edit deltas re-judged from the recorded engine measurements): inspect ok, features 15/15, probes 9/9, counts 11/11 (side stations 1 each), preservation ok with 22 preserved and 8 removed, gates 11/0/1; every Zoo measurement inside the revised bands (max 0.55 % section deficit from its 0.15 mm corner relief). Tests: tests/test_ecr_edit.py (compare removals, brief removals/probes/counts/parameters, the real ECR-3 delta consistency and Zoo numbers) and tests/test_ecr_scoring.py (region in inspect counts); pytest -q 191 passed, 1 pre-existing cache failure (test_freecad_smoke_if_installed). Recorded Zoo ecr3 artefacts left as the record; truth observables untouched. The fresh freecad re-run (order 004-ecr, brief from the new code) applied the request in one worker turn: quick 5/5 sections, 34/34 faces, 9/9 probes, 11/11 counts, STEP volume 56762.417 = the analytic total; stages/score pending on --continue. Investigation: results/_bakeoff/investigations/003-rpi5-ecr3-contract.md. — a revised contract that still describes the pre-change geometry, plus a comparator that reads a requested deletion as a moved interface, turns a feasible request into a refusal; the request was feasible (Zoo truth PASS)
- 2026-09-20 [rpi5-enclosure] load_request_and_delta reads the request and optional delta before the wipe; run() then rewrites ecr/<label>/. Published ecr4/ restored from git. Test test_load_request_and_delta_before_label_dir_wipe. Investigation: results/_bakeoff/investigations/004-ecr-request-wipe.md. — the published request path is inside the label directory the stage rebuilds; wiping first is a self-delete
- 2026-09-20 [fusion-01184-recon] Contract passage boreThrough: replace seal_radius with plugs over both mouths ([102, 2, 68.5]–[108, 8, 70.5] and [102, 2, 119.5]–[108, 8, 121.5]). Probe points and truth observables unchanged. test_fusion_01184_bore_uses_plugs_not_an_undersized_seal. Investigation 006. Zoo inspect/gates/report replayed on the recorded STEP/STL (no hosted call). — a closing radius narrower than the port cannot seal it; that is a contract drafting error, not a missing bore
- 2026-09-20 [fusion-13786-recon] Flip faceXNegInner normal to - and faceXPosInner to + so each floor faces its mouth. test_fusion_13786_blind_floors_face_the_mouths. faceZMin/Max in-plane centers set to the STEP centroid [0, -4.637] shared by cadquery, build123d and freecad (sheet had -4.93/-4.94, 0.29 mm off the same ellipse that matches volume, COM, plateThickness ΔV 8412.12 and sections). Area 8331.1 ±2% already covers the measured 8412. Correction orders for the centroid miss are superseded; they must not change the ellipse. — a blind floor's outward normal is toward the mouth; sheet face centroids that disagree with the solid they describe are a drafting error, not a missing slot
- 2026-09-20 [fusion-12944-recon] Replace each seal_radius with plugs over both y-mouths. Probe points unchanged. Truth observables unchanged. — a closing radius narrower than the port cannot seal it
- 2026-09-20 [fusion-15317-recon] Replace each seal_radius with plugs over both arm-shoulder mouths (x=±36.4..±37.6, 6.6 mm around the bore axis). Passage ends moved from x=±40 (exterior, past the shoulder) to x=±30 (same as voidArmBores). Truth observables unchanged. test_fusion_15317_arm_bores_use_plugs_not_an_undersized_seal. Zoo inspect/gates replayed on the recorded STEP (no hosted call). — a closing radius narrower than the port cannot seal it; that is a contract drafting error, not a missing bore
- 2026-09-20 [fusion-15317-recon] Dropped the two arm-bore passages. Cylinder counts set to the extracted segments (major 4, minor 4, hub OD 2). Named cylinders and voidArmBores still pin the bores. test_fusion_15317_counts_match_slot_split_bores_and_waisted_hub. Zoo inspect/gates replayed on the recorded STEP (no hosted call). — a slot-vented through-bore cannot be sealed as one interior passage; extracted cylinder segments are not a missing feature
- 2026-09-20 [gear-pair] FreeCAD STL walks each Body, meshes it, then Mesh.Mesh.addMesh into one document (investigation 005). export_integrity still requires a valid STEP; a non-watertight combined mesh of touching bodies is judged per shell when solid_count > 1. — a multi-body STEP is not a single-shell mesh; the evaluator must not fail a correct compound
- 2026-09-20 [fusion-12944-recon] Local STEP writes go through canonicalize_step (header-normalised text form, STEP_ZERO_SNAP 1e-9) so two exports of one part hash-equal (investigation 007). — restore hash is a determinism check, not a licence to rewrite correct geometry
- 2026-09-20 [prusa-mini-extruder-front] Port decompose to Python backends: params.py, datum.py, def apply(body) per group, main.py compose chain; runners put entry.parent on sys.path (python -I); hygiene allows sibling .py imports; briefs use explicit from params import names (ruff F403/F405). should_decompose True on cq/b123d/fc. tests/test_decompose.py. Investigation 009. — the stuck-class recommendation to decompose must be executable on every modelling backend
- 2026-09-20 [pipeline] assemble._joint_set reads the vaulted joint_set.json when the live file is absent (placement and modelled). --continue without attempt-state re-scores an existing main.py. Visual: lines as markdown bullets count. Investigation 010. — concurrent holders on one case must not fail a correct assembly on a vault path
- 2026-09-20 [pipeline] assembly_agree.integrity records combined-mesh watertightness but does not fail a valid 2-solid STEP on it (investigation 011). Single-solid exports still require a watertight STL. — a multi-body assembly STEP is not a single-shell mesh; the evaluator must not fail a correct compound
- 2026-09-20 [pipeline] Modelled assemble mode: worker writes parts/<backend>/<case>/main.py that imports the two dataset STEPs, places them, assigns result + placements; engine exports a 2-solid STEP; agreement vs input x placement; scorer unchanged; evaluator builds the animated GLB from exported bodies. Default modelled for non-zoo, placement for zoo. Cases and joint_set.json were not edited. — a bake-off cell must run the named CAD backend; placement yaml is not a backend result
- 2026-09-21 [pipeline] Signature = gate ids + engine class + digest of the failing item names; history records failing_count/failing_items. Three turns are granted; turns 4..6 are earned by a falling count; two turns without a fall stop as no-progress. A non-executing correction is reverted to the worker's own checkpoint and re-measured (two in a row stop). correction_message leads with a ranked, spatially clustered "Fix first" block of <= 6 items. Correction budget 900 + 60 s per failing item (cap 1800). Report views (and view-compare.png) are attached to every correction. — a loop that cannot see progress stops the worker while it is converging; a non-executing deliverable is a wasted turn
- 2026-09-21 [pipeline] `python -m opencad.truth parity <case>` (evaluator-side): nearest contract item per truth observable with missing / looser / params findings and the scorecard-PASS-gates-FAIL list, written to results/_bakeoff/parity/<case>.md, never handed to a worker. lint_contract rule 7 (unbanded passage; endpoint within 1 mm of a plug) and rule 8 (stated section area with a band > 10 %). `quick` exports the STL whenever the contract declares passages, thickness or symmetry. Passage closing is two Euclidean distance transforms (exact ball closing, O(N)) and the closed grid is cached per part: 11 passages at 0.25 mm went from minutes each to 35 s total. — the worker's critic must measure what the scorer measures; a closing that takes minutes per passage is not a critic a worker will run
- 2026-09-21 [voron-sb-duct] Tightened only. Passages: inlet chamber [-20,-18,55] to the drawn duct stations at z=45, 30, 20 and the round rear outlet (-26,-10,10), mirrored; pitch 0.4; seal_radius 3.2 (the drawn ~8 x 19 channel with ~1 mm walls stays open, narrower leaks shut); the six drawing plugs plus bottom slabs under the outlet lips; air volume band 3400-6200 mm3 (~100 mm2 x ~48 mm, +-30 %); isolation at the z=45 centres; hotendFanChamber (-8,-19,24)..(8,-19,24), band 5000-12000 mm3 (section y=-20 chamber plus the fan annulus). Sections y=-12/-20, z=10/30/45 bands to 6/8 %. minimumHousingWall max_thickness 8.0. The ten scored fastener bores: radius_tolerance 0.15 -> 0.1. Verified evaluator-side on the reference STEP/STL: every contract item passes; duct air 4343/4301 mm3, chamber 8439 mm3, wall p05 0.874. Truth files untouched. — the contract must describe the ducts the scorer measures; a passage that a pinhole at the wrong station satisfies is not a duct
- 2026-09-21 [prusa-mini-extruder-front] backDatum area_tolerance_rel 0.04 -> 0.03 (tighten only). — worker-visible bands must not be looser than the scorer's
- 2026-09-21 [voron-sb-duct] hotendFanChamber description states the chamber is air and how to read both sections; new void probe hotendFanChamberAir at (+-8,-19,24), (0,-19,24), (0,-24,24), (0,-19,27) pins it on the B-rep (verified air on the reference). Round 2: the module built a 7 mm tall, 8 mm deep chamber and reported the closing "erases it"; four more probe points ((+-12,-19,29), (+-12,-12,24), verified chamber air at both pitches) and the measured extents (side bays z~21..30, y~-26.5..-11; x=0 band z 22..28 to y~-18) went into the description. Round 3: the module built a sealed 1117 mm3 chamber and called the 5000 mm3 floor unreachable; the reference component (8439 mm3 at 0.4 mm) is the whole air wrapping the fan bore: under it z 20..28 back to y~-17, beside it (|x| 10..14) z 20..36 back to y~-6 - the description's z 9..44 hotend cavity minus bore and open pocket. Description rewritten from that reading; probes (+-13,-10,28), (+-13,-8,32) added (chamber air at both pitches). Tightening only. — a contract the drawings let two readers disagree on is a drafting defect; the reference decides and the contract says so
- 2026-09-21 [voron-sb-duct] passage_hotend_cavity removed from voron-sb-duct and voron-sb-duct-ecr1 manifests. Duct passages re-measured on a repaired tessellation (null faces patched from their pcurves, fill ratio 1.14): left 4343, right 4288 mm3, ducts_separate holds, wall p05 0.864 / p50 2.98; those bands stand. Contract: hotendFanChamber passage and hotendFanChamberAir probes removed; solid probe hotendFanFloorSolid at (0,-17,26), (0,-16,28), (10,-18,30), (-13.6,-18.8,26.4), (13,-10,28), (-13,-8,32) - every point >=1.5 mm inside material on the reference B-rep, all behind the y=-19.2 bore floor so a plain Ø37.5 bore stays legal. Critic: assembly.passage now records the fill ratio and open-edge count and returns ok=false with a "voxel fill leaked" error below FILL_LEAK_RATIO 0.8. truth parity gained a reference-integrity section: mesh fill health plus B-rep classification of every truth and contract passage endpoint and probe point (results/_bakeoff/parity/voron-sb-duct-2026-09-21-pre-fix.md shows the defect as caught). — an observable the reference B-rep contradicts is not truth; voxel measurements on a cracked shell are not evidence, and the scorer must say so instead of banding them
- 2026-09-21 [voron-sb-duct] Contract only (truth unchanged): feature cosmeticFanGrille is now required for the hub (vanes stay optional) with the drawn extents and solid verify points; new solid probe fanHubSolid at (0,-23,41), (0,-23,45), (0,-21,43), (0,-25,43), (+-4,-23,43) - every point >=1.5 mm inside the reference hub; sec_z45 verify moved onto the feature; sec_y-20 description rewritten (islands_min stays 1: the extra loops are cosmetic ribs). Tightening only. — an optional feature that a scored 8 % section band cannot do without is not optional; the contract must say what the bands need
- 2026-09-21 [voron-sb-duct] Contract only: plugs removed from all nine passages (closing-only sealing, as scored); descriptions state the neck requirement; left stations banded 3474-5211, right 3440-5161. lint_contract rule 1 no longer treats a cylinder described as a "partial cylindrical surface" (the Ø20 inlet bend wall leftInletTurn) as a bore that needs a plug. — a parity 'params' finding on sealing is a contract defect, not a note: the worker must be scored by the critic the scorer runs
- 2026-09-21 [prusa-mini-extruder-front] Contract only: leftDatum, frontDatum and bottomDatum switched to mode sum (same areas, bands already at or below the truth's); new face rightSideFacesTotal (x = 26.5, +, mode sum, 106.85 +-15 %). The parity face auditor now pairs a summed observable with the contract's summed face on that plane. — a candidate must be able to fail the contract wherever it can fail the scorer; extra coplanar patches the drawing does not show are such a failure
- 2026-09-21 [prusa-mini-extruder-front] Contract only: leftDatum, backDatum, frontDatum and bottomDatum plane tolerance 0.03 -> 0.05 (the truth's). Parity face auditor flags a summed face whose plane window is narrower than the truth's as "looser". — the gate must sum every sliver the scorer sums; a summed face's plane window is part of its band
- 2026-09-25 [gear-train] Added truth/cases/gear-train (kind machine): the gear-pair observables score the assembled handoff STEP unchanged; one performance reference, the transmission ratio -0.5 (evidence C, exact, tolerance 1e-9), measured by the kinematics stage from the tooth counts of the placed gears. No threshold was tuned. — first assembly-level case: every new stage exercised with zero external-data risk
- 2026-09-25 [disc-brake] None to the case. Recorded as the model-form evidence the thresholds were set against: ring averaging removes the flash temperature under the moving pad (-60 K); the reference uncertainties (5 K reading, 4 K input for the unstated T_air) are the reference's own, so a ring-averaged prediction is expected to fail peakDiscTemperature and lineMaxTemperature. — separate the analysis setup's error from the reconstruction's error before any agent geometry is scored
- 2026-09-25 [gear-train] pythonlang._eval_num evaluates `math` constants and functions and abs/min/max; part gates treat a failed source_hygiene as retryable (a static property of the worker's own source); `opencad correct --note` accepts inline text longer than a file name; the asm-draft brief marks evaluator-measured predictions (transmission_ratio) as simulation-free; adapter input and quantity conventions are inlined into the asm-draft brief; `assembly stage-run <asm> parts` refreshes parts.json. — a correct part must not fail on the evaluator's inability to read its own formulas; tier-B source failures are cheap corrections
- 2026-09-25 [disc-brake] calculix.friction_brake superposes the flash on a surface copy of the field when `wheelRadius` is given (energies still from the conduction field); brake_energy uses the excess flux only. No reference or threshold changed. — the ring-averaged field cannot carry the moving-pad flash; superposing the classical moving-source solution closes most of the peak gap
- 2026-09-25 [nottingham-bearing] Case added with Stage A (tap pressures) gating and Stages B (heating) and C (operating film) scored but not required: a rigid thermal-wedge Reynolds model runs at lower eccentricity than the rig at every condition (the 1000 rpm film is too thick even where the heating matches), a model-form gap for a thermo-elasto-hydrodynamic analysis, not a threshold to tune. — qualify the analysis on the stated geometry before any reconstruction is scored; record which stages the current model can own
- 2026-09-25 [fda-pump] Case added in analysis mode (the FDA CAD among the inputs) with the published development / held-out split (C5, C1 / C2, C3, C4, C6), z_max 2 against the inter-laboratory SD (the Ponnaluri 2022 criterion), 4 mmHg digitisation added in quadrature. Assembly parts gained role construction (a supplied flow-region model staged for the source, never placed). — first open experimental pump benchmark: score placement, sealed domain and pressure rise on the published CAD
- 2026-09-25 [gpu3-stirling] No machine case: the isothermal lossless model is an upper bound and cannot own brake power (heat-exchanger, pressure-drop, leakage and mechanical losses are 70-80 % of the ideal work here). The mechanism and geometry stage waits for an adiabatic model with losses that qualifies on these anchors, as the challenge document orders it. — qualify the thermodynamic model on documented points before any CAD is scored
- 2026-09-25 [fan-02] No case: a housing modal analysis would have no reference to score against, so it would be a verification exercise, not a validation case. Kept conditional until the response data are published. — a scored case needs a measured or numerical reference
- 2026-09-25 [disc-brake] lint_assembly checks the child frame of every joint and the parent frame of rigid joints only (a moving joint's axis may pass beside a stationary parent; the parent side is a warning). No reference or threshold changed. — a faithful machine (pad as the fixed datum, disc spinning past it) must pass drafting
- 2026-09-25 [nottingham-bearing] domains.derive_fluid closes a port by the half-space beyond its cap unless the fluid body crosses that plane elsewhere, when a local plug just outside the plane (sized from the fluid body's face there, cut on its own) is used; the fluid agreement is the p99 surface deviation each way (a boolean-derived region keeps zero-volume fins where a shaft end touches a wall coplanar). — a fluid domain's derivation must neither cut away a branch (FDA outlet tube) nor leak at plug corners (bearing film)
- 2026-09-25 [fda-pump] verify matches derived solids to the remaining exported solids in body order and flags files in inputs/ the evaluator did not stage; the provenance gate passes vacuously with no modelled parts; openfoam pads the background by max(4 cells, 3 mm), fails fast when a port patch is empty or cells sit on the background box, and sizes the container memory from the background cell count. No reference or threshold changed. — evaluator defects exposed by the first CFD machine; none of them was the worker's geometry
- 2026-09-25 [peristaltic-pump] `truth run --amend <evidence.md>` / `assembly drive --amend`: one asm-draft turn on the drafter's thread revises the published contract under sequestration, the old bundle is kept as designs/.amended-<asm>-<n>, the machine is re-placed from assemble. transmission_ratio without a body measures the whole train (it read the first stage, -0.5). The peristaltic model takes the nearest rotating joint up the rotor's chain (a rotor fixed to the output gear) and any body jointed to the rotor as a roller. No reference or threshold changed. — placement corrections cannot fix contract errors; the drafter owns them and fixes them from the evaluator's evidence
- 2026-09-25 [fda-pump] openfoam runs levels coarse to fine, skips a level whose background box exceeds the memory cap (recorded), keeps the other cases when one fails, and reuses a finished case whose inputs hash unchanged (result.json). No reference or threshold changed. — Run A of the adapter on the published CAD: the model-form error of this RANS setup, before any reconstruction arm
- 2026-09-25 [disc-brake] calculix friction_brake reports the weighted hot-band radius. No reference or threshold changed. — a location metric must converge under refinement before it can be scored; the converged value exposes a real offset
- 2026-09-25 [fan-01] local.run_script scales the CPU limit by the core count; geomcheck.min_distance uses a tessellated estimate (KD-tree candidates, exact point-to-mesh; error ~ deflection) when two bodies have more than 300 faces. The case is not scored: its inputs need a repaired duct (ShapeFix, valid closed solid) and a re-oriented shaft, then a fresh draft and the MRF runs. — the reference inputs must be valid solids before any placement, domain or CFD result on them means anything
- 2026-09-25 [fan-01] scripts/iges_to_solids.py rebuilds both bodies as the revolution of their meridional section at 15 deg (section cells polygonized, united, clipped to r >= 0, simplified to 0.005 mm): duct 193 analytic faces, 3,481,742 mm3; shaft 32 faces, 282,082 mm3. Flow surfaces match the IGES to 0.001 mm (planar sections of bore, rotor band and diffuser; shaft both ways within 0.007 mm); the flange rings between r 274 and 295 lose their notches and bolt bosses. Replaced in inputs/ and truth/ (qualification.yaml records before/after hashes, steps and fidelity); the duct observable's point moved to the nozzle lip at the same azimuth (-311.0, -507.5, 1216.5) and its expected volume re-derived from the repaired solid; the packet now describes the repaired solids and states the 250 mm bore across the rotor band (2.5 mm tip gap; it had said 252, the outer radius). No performance reference or threshold changed. designs/fan-01 archived to designs/.amended-fan-01-1 for a fresh draft. — input repair before any run, not tuning: a boolean, a domain or a CFD result on an invalid solid means nothing
- 2026-09-25 [fda-pump] openfoam coarsens the background by powers of two until the padded box holds at most background_cells_max (3e6) hexes and adds a refinement region inside the closed fluid surface back to the interior size, raising the surface levels by the same count, so each level keeps its interior, wall and rotor sizes while the memory follows the fluid (maxGlobalCells from the estimate); degenerate facets are dropped and an inward-facing surface is refused; the inlet turbulence intensity is read per operating case (settings.turbulence_key, default inletTurbulencePct; FDA C1-C6 carry 4/4/5/7/7/7 %, the adapter had used 5 % for all); optional prism layers (settings.layers) with the coverage parsed from the snappy log; skipped levels are carried in the refinement evidence. Mesh-only check at C5: 0.6 mm level 1,250,239 cells (Mesh OK, 9 min), 0.42 mm level 2,855,435 cells (2 skew faces, 18 min), estimates 3.1 and 7.2 GB. No reference or threshold changed; the FDA results so far are on the unrefined mesh and are re-run in the next attempt. — a refinement gate and any statement about discretisation error need the meshes the settings describe
- 2026-09-25 [four-bar] geomcheck.pool_context starts the kinematics and gear-mesh pools from a fork server (a fresh interpreter preloading only the geometry modules; OPENCAD_MESH_START overrides), and opencad.assembly's __main__ is guarded like the other entry points. The compound-train specification lifts the output gear to z 8.5 (0.5 mm clear of the idler's large gear) and the manifest's bbox, output point, tooth height and bore point follow. The drafter brief tells a revolute closure joint to carry no ref. No reference value or threshold changed. — the evaluator measures every kinematic prediction exactly on reference geometry before agent geometry is scored
- 2026-09-26 [planetary-set] geomcheck.gears.tooth_count reads the inner boundary when the outer boundary is plain (radial relief under a quarter module): teeth where it comes inside its tip radius + 0.6 module, reported as internal. External gears are unchanged (their outer relief is 2.25 modules). The same function serves the scorer's `teeth` observables. No reference or threshold changed; the run continues from the ring's correction. — a part check must measure the feature the contract declares; a ring gear carries its teeth inside
- 2026-09-26 [planetary-set] cache.key mixes in a digest of the measuring code (geomcheck, the inspect and edit stages, gates), so a change to a check re-measures unchanged parts instead of relying on a manual VERSION bump. The ring re-run from inspect passes 11/11 gates; the machine continues from assemble. — an evaluator fix must reach every result it measures
- 2026-09-26 [planetary-set] verify rejects any placement that is not a rigid motion (R^T R = I, det R = +1, last row 0 0 0 1, within 1e-5), reported under placements.non_rigid and failing bom_complete; every other machine's placements are rigid to 1e-16. Re-evaluated, this run's gates read bom_complete FAIL: its PASS is not counted, and the regression run is the case's evidence. The specification now states that external flanks run radially from the base circle to the root (the reference's construction). No reference value or threshold changed. — a body is placed, never resized; the specification must fix every surface a mesh can touch
- 2026-09-26 [planetary-set] The specification's backlash row states the reference's values: every external tooth thinned 0.10 mm at its pitch circle and every ring space widened 0.05 mm (0.20 mm circular backlash at the sun meshes, 0.15 mm at the ring meshes); re-pinned. Run A now builds every gear exactly as its specification states (0.05 mm thinning for compound-train and rack-pinion, 0.10 mm for the planetary sun and planets). No reference value, tolerance or gate changed; the sun-mesh flank gap limit (0.2 mm) is unchanged. regress-asm-20260926 is not promoted; the suite re-runs as regress-asm-20260926-2. — a specification must be satisfiable by its own reference geometry, and Run A must build exactly what the text says
- 2026-09-26 [fan-01] derive_fluid pads a box over the walls and every cap point, so caps can bound a fluid beyond its walls (an open box around a duct); caps at ports inside the walls' extent leave the box as it was (the U-duct test is unchanged). New test: a plate with a hole between caps 40 mm beyond it. No tolerance or reference value changed. — the caps, not the walls, bound an open-air domain
- 2026-09-26 [rack-pinion] The assembly lint rejects a band on an evaluator-measured kinematic observable (transmission_ratio, joint_value, joint_range, point_x|y|z) finer than 1e-5 of its value, so the drafter widens it before publishing; the drafter rules say so, and the exemplar's gear ratio and joint value bands are 1e-5 and 1e-3 deg. No truth value or scorer tolerance changed. — a contract band finer than the measurement turns measurement noise into a failed gate
- 2026-09-26 [fda-pump] None to the evaluator or the case; this entry records the refined results against iteration 1. Mesh convergence at C5 (a third level, prism layers, iteration-averaged observables) and the C3/C6 over-prediction go to the physics roadmap. — refined walls change the predictions by 8-20 %: the unrefined iteration-1 numbers are not evidence
- 2026-09-26 [fan-01] The OpenFOAM adapter requests twice its memory estimate (snappyHexMesh's castellation holds cells on both sides of every wall), retries a run killed for memory (exit 137) once at twice that up to the 40 GB cap, and reports a kill or a timeout as such before the port-face check. A second amendment gives the drafter the gate, the kill and the measured run times (level 1.0: 3.78 M cells where the adapter estimated 2.82 M) and asks only for mrfDesign timeout_s. No truth value or scorer tolerance changed. — a mesh killed for memory is an evaluator failure, not refinement evidence, and its error named the wrong cause
- 2026-09-26 [fan-01] A restart moves `sim/` to `sim.prev/` instead of deleting it; the OpenFOAM adapter adopts a finished case from there when its inputs hash the same, and simulate deletes `sim.prev/` when it ends, so `sim/` holds only the current attempt's cases and the report packages nothing stale. The adapter also deletes a finished case's decomposed `processor*` copies (reconstructPar has merged them; they doubled every case and twice filled the disk this iteration). No truth value, scorer tolerance or contract changed. — an engineering change that leaves a case's inputs alone must not rerun it; here that was 4.4 h of identical CFD
- 2026-09-27 [pipeline] Numerical uncertainty is computed, not assumed (src/opencad/sim/__init__.py). Each OpenFOAM observable is the mean of its last 20 % of iterations; u_iteration is the spread there and drift that mean against the 20 % before it. Simulation.refinement is a ladder of levels coarse to fine (a size factor, or {factor, regions, iterations}); Simulation.regions names zones a level refines past the finest surface cells (rotor_tip: the annulus spanning a rotor's tip radius over its tips' axial reach, a hollow searchableCone; cylinder; box). The finest three levels give the grid-convergence index (Celik 2008: observed order capped at 2, Fs 1.25; a pair, or oscillating or diverging levels, Fs 3 at order 2; refinement ratio from the cell counts, 2 per level inside a region); u_discretisation = GCI x value, u_numerical their quadrature sum. A prediction is resolved when every level finished, the finest three converge monotonically (or a pair differs little), GCI <= refinement_tolerance (0.05), no level's mean drifts 1 % or more, and its finest steps refine everywhere (a regional step is a sensitivity study). `python -m opencad sim study` runs one case's ladder into the cached case directories (`--dry-run` says which runs a contract would reuse). Re-parse of the cached runs, nothing recomputed (every case hashed as before), last sample -> tail mean: FDA C5 314.6 -> 314.9 (spread 4.2, drift 0.9 %) and 290.1 -> 289.7 mmHg (5.9, 1.3 %) at levels 1.0 and 0.7, pair GCI 0.356, unresolved (GCI and the 0.7 drift); C1 179.0 -> 177.5, C2 371.4 -> 365.4, C3 360.0 -> 358.4, C4 56.1 -> 56.0, C6 262.1 -> 267.7 mmHg (one level, no discretisation estimate). FAN-01 q1403 141.3 -> 142.2 Pa (spread 4.1; attempt 2's last sample 147.7 lies 1.4 spreads from it) and 89.8 -> 92.6 Pa (1.6, 0.35 %), pair GCI 3.0, unresolved; torque 2.468 -> 2.472 and 1.944 -> 1.983 N m, GCI 1.38; q1804 86.4 -> 84.1 and q0994 115.4 -> 116.0 Pa (one level). The C5 levels' 150-iteration window means wander about 1 % with no trend, so the fine levels run 3000 iterations (a longer endTime continues a cached run from its latest time; the histories are stitched across start-time directories). — a prediction's uncertainty must come from its own convergence evidence before any agent geometry is scored with it
- 2026-09-27 [fan-01] The scorer marks a prediction its mesh ladder does not resolve `unresolved`: its z is reported but it neither passes nor fails, and a required one makes the verdict INCOMPLETE (a failure elsewhere still makes it FAIL). Scorecards count required predictions by split (development, held-out) and name each row's simulation, solver and model. The refinement gate passes only when every prediction of every ladder is resolved; a level lost to memory or a timeout fails it; one-level simulations stay n/a and are listed as having no discretisation estimate. Under these rules attempt 3's design point is unresolved (pair GCI 3.0 on the re-parsed means) and its two passes are void; the verdict stays FAIL on the held-out points. No truth value, z_max or tolerance changed. — a wider numerical uncertainty must never make a prediction acceptable
- 2026-09-27 [planetary-set] A revolute or cylindrical joint that a checked gear mesh couples is bounded radially by 0.2 x the mesh's backlash_max (or its own position_tolerance, if tighter): 0.04 mm on the planetary contract (backlash_max 0.2), 0.02 mm at the specification's 0.10 mm backlash. The critic prints the bound; the placement and correction briefs say a meshed gear stays on its axis and a mesh that interferes there is a contract or part error. No truth value changed. — a placement must not buy clearance with eccentric spin
- 2026-09-27 [fda-pump] A case whose inputs changed now starts from a clean directory (no later time directory, postProcessing, processor copies or mesh), so a longer run re-meshes and re-solves from its initial fields. A level's tail mean counts as still trending only when it moves more than its own spread (and 1 %) between the last two fifths: a steady solution that oscillates without a trend is converged to within that spread, which u_iteration carries; a resolved prediction now also needs u_numerical (GCI and iteration spread together) within refinement_tolerance of its value. The level-0.7 case was restored to its finished 1500-iteration state (the continuation's outputs set aside, the snappy mesh moved back to constant/polyMesh: 2,855,435 cells and patch faces identical to the original record, checkMesh log regenerated), and reuses its original hash. No truth value or tolerance changed. — a rerun must not inherit a previous run's time directories; iteration noise is not a trend
- 2026-09-27 [pipeline] The OpenFOAM adapter writes a start marker (the inputs' hash) before a run, and a case whose driver died is recovered, not rerun, when its marker names the same inputs, the solver reached endTime (or converged) and the parallel run was reconstructed. The level-0.5 run began before markers existed: its marker was written from the hash of the dictionaries the container was running, then its adapter process was stopped so the timeout could not kill a run 90 % done. No truth value changed. — a finished solver run must survive the death of the process that started it
- 2026-09-27 [pipeline] (1) The passage check brackets the volume between the void voxels and the void plus the partly-void wall layer, and a contract band must meet the bracket (the truth scorer still reads the plain count its references were derived with). (2) The assembly lint rejects an observable no simulation predicts unless the evaluator measures its quantity. (3) A requirement is judged over value +- 2 u_numerical: met when the whole band meets it, failed when the whole band misses it, undetermined otherwise, so a wider uncertainty never makes a requirement easier to meet. (4) Reduced models show no mesh levels; the viewer shows value +- u_numerical and whether the ladder resolves it. The mixer then went back through `--amend` (quantity fluid_volume, a fourth, finer mesh level): 13 of 14 gates; the one failure is the honest one, the pressure rise oscillating across the finest three levels (3878, 4079, 3915 Pa; GCI 0.283 at Fs 3), so it is reported as 3915 +- 1109 Pa, unresolved, with the requirement met over the whole band (1697..6132 Pa). — the pipeline's first machine without truth data should say exactly how far to trust each number
- 2026-09-27 [fda-pump] None to the evaluator, the scorer or the case; the contract change went through --amend. The `sim study` command module is now src/opencad/sim/cli.py: named study.py, importing it replaced the package's study() function with the module, so the command crashed at its first run that reached the grid-convergence step (no result changed). — the third C5 level measures the base mesh's discretisation error instead of assuming it
- 2026-09-27 [fan-01] None to the evaluator, the scorer or the case; the contract change went through --amend and the global pair's values are recorded in the contract's open questions. With the tip gap resolved the design point stays 25-28 % low in pressure rise and 7-9 % low in torque: the remaining gap is model form or observable definition, not the mesh (physics roadmap section 3.6). — a tip-gap ladder separates the mesh dependence from the model-form gap at the design point
- 2026-09-27 [pipeline] None to the evaluator or any case: the envelope is report-only (the scorer never reads it). A new machine's report can now quote these rows; no scored CFD prediction is mesh-resolved yet. — what a machine without truth data may quote must come from the final scorecards

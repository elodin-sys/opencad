# fusion-12944-recon — design brief

## 1. Intent and configuration

Reconstruct Fusion Gallery body `22303_e9723631_0014_1` (joint set `joint_set_12944`) as one
editable KCL solid in the part's own frame. The body is a 15 mm mounting flange: square-ish
XZ outline with four Ø24 corner bosses, two concave Ø174 side cuts, a through Ø18 centre
bore, a through Ø36 hub, matching circular pockets 3 mm deep from each Y face, and four
Ø10 holes coaxial with the bosses. Authoritative numbers are `sources/dimension-sheet.md`
and the frame/export rules in `sources/part-brief.md`. Renders and section drawings confirm
topology. Held-out: the pipeline is frozen and the reference CAD is evaluator-only. Export
STEP and STL. Units mm and deg; `release_status` reconstruction; material and density unset.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/part-brief.md | text | authoritative | def482e91661e934c0c45f0f2bc0e109c5b2b61cae7d5556e27385205cdec0bf | Frame, one-solid, STEP+STL, held-out |
| sources/dimension-sheet.md | table | authoritative | d2fa6c8c40ab0e2b8a2ea1d7aac083922b8315c3072c1cf5c04ef7022809c708 | Envelope, mass, 8 planar levels, 11 cylinders, 3 sections |
| sources/render-notes.md | text | illustrative | 099190bcedfa422c7d7d81397eada2c9e5d54e61f2dd2be8203fde4c7ddddde3 | Mesh bbox 126.682 × 15 × 108 |
| sources/front.png | image | illustrative | cf01480c1ad346e0e3732cad97c7ea957759eac23febacc27c2a3193e6b0fdad | Ortho XZ, concentric hub/pocket, 4 corner holes |
| sources/iso-below.png | image | illustrative | dbe4e357a283f8c277b8bd95c6e546cd9226e8e6d96efbb9ba8d6815aff5f777 | Iso from −y; caption bbox 126.68 × 15 × 108 |
| sources/iso.png | image | illustrative | 4e81696ca175f97af16fc382bbf322e9ed71f5bfcb054beb6ef2bd8eb055f5d4 | Iso from +y; recessed circle, raised hub |
| sources/iso2.png | image | illustrative | c20a5240025eef2e304ffe428dea619a25366480e2759169c23a17c47d03c3c7 | Second +y iso, same topology |
| sources/right.png | image | illustrative | e3e091f2a7e45f4ab9114548cc1d8250151fdcc39aa69fa818b860d60ca597b9 | Ortho YZ; 15 mm slab |
| sources/section-x0.png | drawing | illustrative | 3cb9e0711767d1111766e1e932e04b49fe19f3a1bdccbe4bce49e0c34776b141 | x = 0 outline; two I-beams, 0 holes |
| sources/section-y7.5.png | drawing | illustrative | 6646a693b71db350844cf159d6c4fb43d6cedd8d903b861b8c6a8be3e295460e | y = 7.5 outline; pixel scale 8.9 px/mm |
| sources/section-z-0.png | drawing | illustrative | 0071550d873ea971ea404e6fbf6d44b4ac2655422502f8a8c4af7f0715312ecc | z = 0 outline; two I-beams; anisotropic scale |
| sources/top.png | image | illustrative | c5b417abe796ee2a4bc8ab1fa48b3175c5730908cf2544e1c20a461dc4b22623 | Ortho XY; thickness 15, x ≈ ±63 |

Truth-case renders under `truth/cases/fusion-12944-recon/inputs/renders/` are byte-identical
to the staging copies above (same sha256); they were opened as the work-order image list.

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| one solid | 1 | — | part-brief.md, sheet solids 1 | — | stated |
| export STEP and STL | yes | — | part-brief.md | — | stated |
| envelope min | [-63.351, 0, -54] | mm | dimension-sheet.md / intent | 0.05 | stated |
| envelope size | [126.701, 15, 108] | mm | dimension-sheet.md / intent | 0.05 | stated |
| volume | 148190.98 | mm3 | dimension-sheet.md | 0.2 % | stated |
| surface area | 34691.95 | mm2 | dimension-sheet.md | 0.5 % | stated |
| centre of mass | [0, 7.554, 0] | mm | dimension-sheet.md | 0.05 | stated |
| planar face levels | 8 (y=0,3,12,15; z=±54) | — | dimension-sheet.md | — | stated |
| cylinders | 2×Ø174 hole, 1×Ø18 hole, 4×Ø10 hole, 4×Ø24 pin | mm | dimension-sheet.md | 0.05 | stated |
| section x=0 | area 1041.45, 2 loops, 0 holes | mm2 | dimension-sheet.md | 1 % | stated |
| section y=7.5 | area 11999.89, 1 loop, 5 holes | mm2 | dimension-sheet.md | 1 % | stated |
| section z=0 | area 1041.45, 2 loops, 0 holes | mm2 | dimension-sheet.md | 1 % | stated |
| hub OD | 36 | mm | derived from 763.41 mm2 end faces | 0.05 | derived |
| pocket OD | 81.174 | mm | derived from 4156.33 mm2 floors | 0.5 | derived |
| pocket depth each side | 3 | mm | y=3 and y=12 face levels | 0.05 | stated |
| fillet at pocket corners | 3 | mm | section I-beam corners | 1.5 | inferred / open |
| material / density / process | unset | — | none | — | open |
| Ø10 breakthrough at y=0 | sheet says y=4..15; both-face renders show openings | — | sheet vs iso/front | — | open |
| surface deviation vs reference | unset (held-out, no mesh in bundle) | — | — | — | open |

## 4. Coordinate frame, scale, and measurement method

**Frame.** Origin at the XZ centre of the y = 0 face, matching the dimension sheet: bbox min
is the offset [-63.351, 0, -54], max [63.351, 15, 54]. +x to the right in front.png /
section-y7.5.png; +y from the bottom face toward the top; +z up in those same views.
Right-handed. Datum A = y = 0 faces; B = z = -54 edge; C = x = 0 and z = 0 midplanes.

**Image scale (section-y7.5.png, 1600×1396).** Light-gray grid vlines at px 312, 402, … 1473
and hlines at px 237, 327, … 1219; median pitch **89 px = 10 mm** (8.9 px/mm). Origin of
the plot is px (848, 684): x_mm = (x_px − 848) / 8.9, z_mm = (684 − y_px) / 8.9. This
matches the labelled −70…70 / −60…60 axes. Ink threshold < 40 on the material outline.

**Pixel reads on that scale (confirming the sheet, not replacing it):**

- Centre hole outline: 376 ink px, mean radius **9.02 mm** (sheet Ø18).
- Four corner holes: mean radii **5.014–5.024 mm** at (±51.351, ±42) (sheet Ø10).
- Corner-boss outline band r 10–14 mm: mean **12.25–12.50 mm** (sheet Ø24; mixed with
  adjacent profile, so wide).
- +x / −x outer ink distance to the Ø174 axes at x = ±141: medians **86.90 / 86.77 mm**
  (sheet radius 87).
- Topology: one outer loop, five holes; concave ±x sides; straight ±z sides; rounded
  corners — matches front.png and the iso views.

**section-z-0.png (1600×412).** 5 mm v-grid, median pitch 52 px (10.4 px/mm) on x; y is
stretched (plot frame rows 33 = y=15 and 371 = y=0). Two I-beam islands separated by the
Ø18 gap. Used for topology (full-height hub and flange, recessed web, corner fillets),
not for a locked y-scale radius.

**section-x0.png (1600×6209).** Thin outline of two stacked I-beams; confirms 2 loops,
0 holes, filleted web. Grid ~203 px / 10 mm on the long axis.

**front.png / iso views.** Shaded confirmation of concentric circular pocket and hub on
both Y faces, four corner holes, and the scalloped square outline. Not used as a second
numeric source where the sheet already states the value.

**No reference ingest.** Orchestrator listed none; values quoted from the dimension sheet
are `stated`, not `measured (reference model)`.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| xMin | -63.351 | 0.02 | stated | dimension-sheet.md bbox min x |
| yMin | 0 | 0.01 | stated | dimension-sheet.md bbox min y |
| zMin | -54 | 0.02 | stated | dimension-sheet.md bbox min z |
| spanX | 126.701 | 0.05 | stated | dimension-sheet.md size x / intent |
| plateThickness | 15 | 0.01 | stated | dimension-sheet.md size y |
| spanZ | 108 | 0.02 | stated | dimension-sheet.md size z |
| centerHoleDiameter | 18 | 0.05 | stated | sheet cylinder Ø18; pixel r 9.02 mm |
| mountHoleDiameter | 10 | 0.05 | stated | sheet four Ø10; pixel r 5.02 mm |
| mountHoleLength | 11 | 0.05 | stated | sheet extent 4 .. 15 |
| mountHoleY0 | 4 | 0.05 | stated | sheet extent start |
| bossDiameter | 24 | 0.05 | stated | sheet four pin Ø24 |
| sideCutDiameter | 174 | 0.05 | stated | sheet two hole Ø174 |
| sideCutCentreX | 141 | 0.05 | stated | sheet axis x = ±141 |
| mountCentreX | 51.351 | 0.02 | stated | sheet axis x; also -xMin − 12 |
| mountCentreZ | 42 | 0.02 | stated | sheet axis z; also -zMin − 12 |
| pocketDepth | 3 | 0.05 | stated | sheet planar y = 3 and y = 12 = 15 − 3 |
| xMax | 63.351 | 0.02 | derived | −xMin |
| yMax | 15 | 0.01 | derived | yMin + plateThickness |
| zMax | 54 | 0.02 | derived | −zMin |
| pocketFloorY | 3 | 0.05 | derived | yMin + pocketDepth |
| pocketCeilY | 12 | 0.05 | derived | yMax − pocketDepth |
| hubDiameter | 36 | 0.05 | derived | 2*sqrt(763.41/π + 9²); 763.41 = π(18²−9²) |
| pocketDiameter | 81.174 | 0.5 | derived | 2*sqrt(4156.33/π + (hubDiameter/2)²) |
| filletRadius | 3 | 1.5 | inferred | I-beam corner read on section-x0 / section-z-0; anisotropic z=0 plot |
| acceptance.volume | 148190.98 | 0.2 % | stated | dimension-sheet.md mass properties |
| acceptance.surface_area | 34691.95 | 0.5 % | stated | dimension-sheet.md |
| acceptance.center_of_mass | [0, 7.554, 0] | 0.05 | stated | dimension-sheet.md |
| sectionX0 area / loops / holes | 1041.45 / 2 / 0 | 1 % | stated | dimension-sheet.md; two islands in section-x0.png |
| sectionYMid area / loops / holes | 11999.89 / 1 / 5 | 1 % | stated | dimension-sheet.md; caption 12002.30 |
| sectionZ0 area / loops / holes | 1041.45 / 2 / 0 | 1 % | stated | dimension-sheet.md; caption 1042.53 |
| faceY0Flange area | 5188.92 | 1 % | stated | sheet −y at y=0, larger face |
| faceY0Hub area | 763.41 | 1 % | stated | sheet −y at y=0, smaller face |
| faceY3Pocket area | 4156.33 | 1 % | stated | sheet −y at y=3 |
| faceY12Pocket area | 4156.33 | 1 % | stated | sheet +y at y=12 |
| faceY15Flange area | 5892.64 | 1 % | stated | sheet +y at y=15, larger face |
| faceY15Hub area | 763.41 | 1 % | stated | sheet +y at y=15, smaller face |
| faceZMin / faceZMax area | 1540.52 | 1 % | stated | sheet z = ±54, count 1 each |
| blockout volume band | 182000–205300 | — | derived | outline extrusion ≈ 12568×15 ≈ 188528; bbox prism 126.701×15×108 ≈ 205256 |

**Edit-test volume formulas (other parameters held fixed):**

- `centerHoleDiameter` +2 → 20 mm: ΔV = −π(10² − 9²)×15 = −895.35 mm3; bbox unchanged.
  Infeasible +20 → Ø38 exceeds hub Ø36; KCL must `assert`.
- `mountHoleDiameter` +2 → 12 mm: ΔV = −4π(6² − 5²)×11 = −1519.82 mm3; bbox unchanged.
  Infeasible +15 → Ø25 exceeds boss Ø24; KCL must `assert`.
- `pocketDepth` +1 (both faces): ΔV ≈ −2×4156.33 = −8312.66 mm3 (planar floors; 8 % rel
  because of fillets). Infeasible +6 → web 15 − 18 < 0; KCL must `assert`.

**Geometric identities used in construction (not extra parameters):**
mount centres sit `bossDiameter/2` inside the envelope; each Ø24 boss is externally
tangent to the nearer Ø174 (centre distance 99 = 87+12). Outer XZ profile = convex hull
of the four boss disks, minus the two side-cut disks.

## 6. Defaults retained

- `material`, `density_kg_m3`, `process` remain null: no alloy or process is named.
- `acceptance.deviation` remains null: no reference mesh in the bundle (held-out CAD).
- `acceptance.planes` is empty: no inclined planar faces are stated; pocket walls are
  cylindrical and the I-beam corners are fillets.
- `units` mm/deg and `release_status` reconstruction are the template defaults and match
  the sheet / intent.
- `export_volume_tolerance_rel` 0.002 is the schema default; it matches the stated volume
  band.
- `filletRadius` is an inferred construction default, not a template leftover; see §7.

## 7. Unrepresentable or low-confidence features

- Unstated fillet radii (inner vs outer, and whether all eight pocket corners match).
  Encoded as one optional `filletRadius` with a wide band.
- Hub OD and pocket OD are not in the sheet cylinder table, so they are construction
  parameters and faces, not acceptance cylinders. A later inspector will not score a
  hub-pin axis from this contract.
- Ø10 y = 4 .. 15 vs both-face openings in the renders. Cylinders follow the sheet;
  the y = 0 .. 4 boss cores were not given a solid probe.
- 0.001 mm x-span conflict (126.701 vs 2×63.351) and 0.02 mm mesh-vs-B-rep width
  (126.682). Covered by envelope.tolerance 0.05.
- Section-caption vs sheet area offsets (~2 mm2). Sheet wins.
- Unexplained 703.72 mm2 difference between the y = 0 and y = 15 flange faces.
- 19 of 27 reference faces are unlisted (below the planar threshold, or curved).
- Material / density / process unknown.
- Held-out reference CAD: no deviation band.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-63.351, 0.0, -54.0] → [63.351, 15.0, 54.0] | 188561.0649523068 | pass | 2026-09-19T06:14:02Z: within envelope and band |

# enclosure-base — design brief

## 1. Intent and configuration

Lower body of a two-part box enclosure (the lid keeps the top 4 mm of a 50 mm box). One connected solid in mm:
100 x 150 x 47 outer body with r = 10 vertical corners, an r = 2 bottom edge round and a flat, sharp-edged rim at
z = 47 (the parting plane); a 94 x 144 cavity with r = 7 corners from the 3 mm floor (z = 3) through the open top; four
free-standing Ø10 screw posts at (±38, ±63) from z = 3 to z = 47, each with a Ø4 blind bore that stops at the floor
top. Base only: no lid, gasket or hardware. `sources/enclosure-base-spec.md` is authoritative; the three renders are
illustrative and were used only to confirm topology and proportions. Backend: cadquery, release status
reconstruction.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/enclosure-base-spec.md | text | authoritative | 5fea818692cbc29954c48cebb5413d22ad2b7f42ae80416c72d6d387ef1b2002 | parameters, construction, reference measurements, edit-test deltas |
| sources/enclosure-base-iso.png | image | illustrative | 2a8fd145c1e633fdafe492ced42153af2857af9dcff05c33c6323383ed0f1382 | isometric: 4 posts, open top, bottom round, bore floors shown through the floor |
| sources/enclosure-base-top.png | image | illustrative | d2082d6515363d4843797322498e9f62ae0f9a60f9b725bbc8b916171e7deb7b | top view (+x right, +y up): wall ring, 4 post annuli |
| sources/enclosure-base-section.png | drawing | illustrative | d15e879f8de5dee0e38f58a63a70206e7099478c43379d0b2ed5f1ba6728a3d8 | section x = 38 with mm axes: walls, post walls, blind bores, rounded bottom corners |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| single connected solid | 1 | | spec, header | exact | stated |
| bounding box | 100 x 150 x 47 | mm | spec, reference measurements | 0.05 | stated |
| volume | 118431.5 | mm³ | spec, reference measurements | 0.2 % | stated |
| section z = 25 | 1684.1, 5 loops, 5 holes | mm² | spec | 0.5 % | stated |
| section z = 1.5 | 14883.5, 1 loop, 0 holes | mm² | spec | 0.5 % | stated |
| section x = 38 | 1240.28, 1 loop, 0 holes | mm² | derived (formula in section 5) | 0.5 % | derived |
| bottom face z = 0, -z | 13961.1 | mm² | spec | 0.5 % | stated |
| cavity floor z = 3, +z | 13179.8, centroid origin | mm² | spec | 0.5 % | stated |
| bore floors z = 3, +z | 4 x 12.57 at (±38, ±63) | mm² | spec | 1 % | stated |
| rim z = 47, +z | 1420.2, centroid origin | mm² | spec | 0.5 % | stated |
| post tops z = 47, +z | 4 x 65.97 at (±38, ±63) | mm² | spec | 1 % | stated |
| posts | Ø10, z 3 .. 47, axes (±38, ±63) | mm | spec, construction 3 | r ± 0.02 | stated |
| bores | Ø4, z 3 .. 47, blind | mm | spec, construction 4 | r ± 0.02 | stated |
| minimum material thickness | p05 >= 2.9 | mm | spec, scoring | | stated |
| symmetry | planes x = 0 and y = 0 | | spec, frame | 0.1 max / 0.05 p95 | stated |
| edit: outerWidth 100 -> 110 | ΔV +7122.83, bbox +10 x | mm³ | spec, editability (a) | 2 % | stated |
| edit: postBoreDiameter 4 -> 5 | ΔV -1244.07, bbox unchanged | mm³ | spec, editability (b) | 2 % | stated |
| material, density, process | not given | | | | open |

## 4. Coordinate frame, scale, and measurement method

Origin at the centre of the footprint on the bottom face; +x along the 100 mm width, +y along the 150 mm length, +z up;
datum A is the bottom face z = 0, B and C the mirror planes x = 0 and y = 0, D the rim z = 47. This is the frame the
spec states. Every value comes from the spec text; no dimension was scaled from pixels. The renders were cross-checked
only: in the top view the outer boundary spans about 67..652 px by 73..950 px (ratio 1.50 = 150/100, about
5.85 px/mm); post centres at about x 137 / 581 px and y 142 / 880 px give spans of about 76 and 126 mm (2 x 38,
2 x 63); the post ring is about 58 px (≈ 9.9 mm) and the bore about 23 px (≈ 3.9 mm); the wall band is about 18 px
(≈ 3.1 mm). The section image reads directly in mm: walls at |y| 72..75, post walls at |y| 58..61 and 65..68, bores at
|y| 61..65 ending on the floor at z = 3, floor z 0..3, top z = 47, rounded outer bottom corners.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| outerWidth | 100 | 0.01 | stated | spec Parameters; edit test +10 |
| outerLength | 150 | 0.01 | stated | spec Parameters |
| baseHeight | 47 | 0.01 | stated | spec Parameters (not 50) |
| wallThickness | 3 | 0.01 | stated | spec Parameters (walls and floor) |
| outerCornerRadius | 10 | 0.01 | stated | spec Parameters |
| bottomEdgeRadius | 2 | 0.01 | stated | spec Parameters |
| innerCornerRadius | 7 | 0.01 | derived | outerCornerRadius - wallThickness |
| cavityWidth | 94 | 0.01 | derived | outerWidth - 2 wallThickness |
| cavityLength | 144 | 0.01 | derived | outerLength - 2 wallThickness |
| postInset | 12 | 0.01 | stated | spec Parameters |
| postX | 38 | 0.01 | derived | outerWidth / 2 - postInset |
| postY | 63 | 0.01 | derived | outerLength / 2 - postInset |
| postOuterDiameter | 10 | 0.01 | stated | spec Parameters |
| postBoreDiameter | 4 | 0.01 | stated | spec Parameters; edit test +1 |
| volume | 118431.5 | 0.2 % | measured (reference model) | spec; analytic 14914.16·47 − 412.06 − 13493.94·44 + 4·65.97·44 = 118431.48 (bottom-round spandrel ring by Pappus: (1 − π/4)·4 · (420 + 2π·(10 − 0.447))) |
| surface area | 80261.3 | 0.5 % | derived | bottom 13961.06 + round 1319.47 + 183.07 + outer walls 482.83·45 + rim 1420.22 + cavity walls 463.98·44 + cavity floor 13179.78 + posts 4π·10·44 + post tops 263.89 + bores 4π·4·44 + bore floors 50.27 |
| centre of mass | (0, 0, 16.21) | 0.1 | derived | symmetry; z = Σ V_i z_i / V (prism 23.5, spandrel 0.447, cavity and posts 25) = 16.207 |
| section z = 25 | 1684.1 | 0.5 % | stated | rounded ring 14914.16 − 13493.94 = 1420.22 plus 4 annuli 65.97 |
| section z = 1.5 | 14883.5 | 0.5 % | stated | footprint inset 2 − √(4 − 0.25) = 0.0635 at z = 1.5 |
| section x = 38 | 1240.28 | 0.5 % | derived | 150·3 − 2(1 − π/4)·4 = 448.28, + 2·3·44 = 264, + 4·3·44 = 528 |
| bottom face | 13961.1 | 0.5 % | stated | 96 x 146 with r = 8 |
| cavity floor | 13179.8 | 0.5 % | stated | 13493.94 − 4π·5² |
| edit ΔV outerWidth +10 | +7122.83 | 2 % | stated | 10 · (448.28 + 264); posts move to x = ±43 |
| edit ΔV postBoreDiameter +1 | −1244.07 | 2 % | stated | −π(2.5² − 2²)·44·4 |
| blockout band | 690000 .. 706000 | | derived | solid outer body: rounded prism 700553 to sharp box 705000 |

Sweeps and feasibility: outerWidth feasible for outerWidth > 2·(postInset + postOuterDiameter/2) = 34 (posts stay
separate; the 4 mm post-to-wall gap and the 4.83 mm post-to-corner gap do not depend on the width); sweep
[90, 100, 110]; delta −70 (width 30) must fail an assert. postBoreDiameter feasible for 0 < d < postOuterDiameter;
sweep [3, 4, 5]; delta +6 (d = 10, no post wall) must fail an assert.

## 6. Defaults retained

Material, density and process stay null: the spec does not state them and no mass claim is made. Symmetry bands use
the default 0.1 max / 0.05 p95. Envelope tolerance 0.05 and parameter tolerances 0.01 are the pipeline defaults for
stated dimensions.

## 7. Unrepresentable or low-confidence features

None: every feature is fully dimensioned in the spec. The section x = 38 area, surface area and centre of mass are
derived analytically rather than quoted. The blockout band assumes a solid envelope blockout (open question).

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|

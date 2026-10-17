# fusion-01184-recon — design brief

## 1. Intent and configuration

Reconstruct Fusion 360 Gallery body `36938_ae684b66_0002_2` (joint set `joint_set_01184`) as editable KCL in the part's native frame. The solid is a T: a 10 × 10 × 50 mm head with R4 vertical corner fillets and a Ø5 bore along z, unioned with a Ø5 shaft along +y to y = 88. Envelope min [100, 0, 70] mm, size [10, 88, 50] mm. One solid; export STEP and STL. Authoritative numbers come from `sources/dimension-sheet.md`; renders confirm topology. Held-out: the pipeline is frozen and the reference CAD is evaluator-only. Units mm/deg. Material, density and process unknown.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/part-brief.md | text | authoritative | 1fd7a3e2fd439c3d2dcc9a64f656afc91fd568b74e39c10f1f9d2060cf3bd6ae | native-frame bbox and reconstruction rules |
| sources/dimension-sheet.md | text | authoritative | 52b2551ba8b14028f430b8ffe7ec4f1af0abcb8101332afe6afbf55aed91fa3b | envelope, mass, 8 planar levels, 6 cylinders, 3 sections |
| sources/render-notes.md | text | illustrative | f76626d9b84b32b68e7aeafe877b7bbd8a0e62a7418e931f01adc9de11783b9f | render list; mesh extents 10 × 88 × 50 mm |
| sources/front.png | drawing | illustrative | 5272bbaf14764c846990e1a9ad7dfc24e290864d97385d9eb15fc16b90e4c37c | front; 10 × 50 mm head rectangle |
| sources/right.png | drawing | illustrative | 372740fcee48db7a8975f1baaef255264dd323c5d222f6bf2f523d3c5cb7fbea | right with mm grid; T profile |
| sources/top.png | drawing | illustrative | cb17ead244a8b2a12a76b5bc7c23339aa3c7e9ac3a8e9552586b3123ce060e75 | top; annular head plus shaft |
| sources/iso.png | image | illustrative | f669f71ff9706661274180a5cd82491dcaa42257da9b8a4f9759348b4bac11ce | iso; through-bore and side shaft |
| sources/iso2.png | image | illustrative | 0c7fb2de4b77e9215e890ebca772c020e1dd3a208e0133e584c6d1ae0d22c467 | iso, opposite quarter |
| sources/iso-below.png | image | illustrative | 17b886df612534828ea253bfa72f51be8d7a40c36aa021149819bb0b89ac60ac | iso from below; bore visible |
| sources/section-x105.png | drawing | illustrative | bec3c9216cd6bbec90223c7116b14a514bd9775e9e34d1a743bedc31b9e08404 | x = 105; caption 639.93 mm², 2 regions |
| sources/section-y44.png | drawing | illustrative | 8123d17a41ee6d08e2227537410a25742d86f773697b53621380ea14dbdfa2e7 | y = 44; caption 19.61 mm², Ø5 disk |
| sources/section-z95.png | drawing | illustrative | 9791c0fa2267526758b2b7f3d0ebb84e91c9e5e21a8f3a2cdef9fc74fdecf3ca | z = 95; lollipop outline |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| envelope min | [100, 0, 70] | mm | dimension-sheet / part-brief | 0.05 | stated |
| envelope size | [10, 88, 50] | mm | dimension-sheet / part-brief | 0.05 | stated |
| solid count | 1 | | dimension-sheet; intent | 0 | stated |
| planar face levels | 8 (14 faces total, 8 planar) | | dimension-sheet | | stated |
| hole Ø5 along z | 1, axis [105, 5, *], z = 70..120 | mm | dimension-sheet | 0.05 | stated |
| pin Ø5 along y | 1, axis [105, *, 95], y = 9.708..88 | mm | dimension-sheet | 0.05 | stated |
| pin Ø8 along z | 4 partial, centres (104,4), (104,6), (106,4), (106,6) | mm | dimension-sheet | 0.05 | stated |
| volume | 4863.73 | mm3 | dimension-sheet | 0.002 rel | stated |
| surface area | 3802.07 | mm2 | dimension-sheet | 0.02 rel | stated |
| centre of mass | [105.0, 18.856, 95.0] | mm | dimension-sheet | 0.1 | stated |
| section x = 105 | area 640, 2 loops, 0 holes | mm2 | dimension-sheet; PNG caption 639.93 | 0.01 rel | stated |
| section y = 44 | area 19.63, 1 loop, 0 holes | mm2 | dimension-sheet; PNG caption 19.61 | 0.01 rel | stated |
| section z = 95 | area 456.92, 1 loop, 1 hole | mm2 | dimension-sheet | 0.01 rel | stated |
| export | STEP and STL | | part-brief | | stated |
| material / density / process | unset | | none | | open |

## 4. Coordinate frame, scale, and measurement method

Frame is the dimension-sheet native frame (no re-alignment). [0, 0, 0] is the Fusion origin; the part bbox minimum is [100, 0, 70]. +x is the 10 mm head width, +y is along the shaft toward y = 88, +z is along the bore toward z = 120. Datum A is the remaining y = 0 flat, B is z = 70, C is the remaining x = 100 flat.

Image scale is taken from the labelled millimetre grid on `right.png` (y from 0 to 90, z from 70 to 120) and from the sheet extents, not from a pixel-to-mm fit on unlabelled views. Pixel evidence, all consistent with the sheet:

- `right.png`: head occupies y = 0..10 and z = 70..120; shaft leaves the head at y = 10, runs to y = 88, and spans z ≈ 92.5..97.5 (Ø5) about z = 95. No fillet or chamfer is visible at the junction at this resolution.
- `front.png`: a single 10 × 50 mm rectangle (looking along +y; the shaft recedes along the view).
- `top.png` / `section-z95.png`: annular head plus a constant-width shaft (thermometer / lollipop). The head reads circular because R4 on a 10 mm square leaves 2 mm flats.
- `iso.png`, `iso2.png`, `iso-below.png`: one T-shaped solid; through-hole visible on the head end; shaft is a full cylinder; bbox caption 10.00 × 88.00 × 50.00 mm.
- `section-x105.png`: two regions — a 2.5 × 50 mm bar at y = 0..2.5, and a connected T (y ≈ 7.5..88). Caption 639.93 mm² vs sheet 640.
- `section-y44.png`: circle centred at (105, 95), x = 102.5..107.5, z = 92.5..97.5. Caption 19.61 mm² vs sheet 19.63.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| xMin | 100 | 0.01 | stated | dimension-sheet bbox min x |
| yMin | 0 | 0.01 | stated | dimension-sheet bbox min y |
| zMin | 70 | 0.01 | stated | dimension-sheet bbox min z |
| bodyWidth | 10 | 0.01 | stated | dimension-sheet size x |
| bodyDepth | 10 | 0.01 | stated | y = 0 to the +y face level y = 10 |
| bodyHeight | 50 | 0.01 | stated | dimension-sheet size z |
| overallLength | 88 | 0.01 | stated | dimension-sheet size y |
| holeDiameter | 5 | 0.05 | stated | dimension-sheet hole Ø5 |
| shaftDiameter | 5 | 0.05 | stated | dimension-sheet pin Ø5 |
| filletRadius | 4 | 0.05 | stated | four partial Ø8 pins; remaining flats 2 mm ⇒ r = (10 − 2) / 2 |
| xMax | 110 | 0.01 | derived | xMin + bodyWidth |
| yHead | 10 | 0.01 | derived | yMin + bodyDepth |
| zMax | 120 | 0.01 | derived | zMin + bodyHeight |
| holeCenterX | 105 | 0.01 | derived | xMin + bodyWidth / 2 (sheet hole axis x = 105) |
| holeCenterY | 5 | 0.01 | derived | yMin + bodyDepth / 2 (sheet hole axis y = 5) |
| shaftCenterZ | 95 | 0.01 | derived | zMin + bodyHeight / 2 (sheet shaft/hole z = 95) |
| volume | 4863.73 | 0.002 rel | stated | sheet. Analytic without cheeks: 10·10·50 − 4·16·(1−π/4)·50 − π·2.5²·50 + π·2.5²·78 = 4863.05. Cheeks ≈ 0.68 mm³. |
| surface area | 3802.07 | 0.02 rel | stated | sheet (blend not closed-form) |
| centre of mass | [105, 18.856, 95] | 0.1 | stated | sheet. Check: (3331.5·5 + 1531.5·49) / 4863.05 ≈ 18.857 |
| faceXMin / faceXMax area | 100 | 0.02 rel | stated | 2 mm remnant flat × 50 mm height |
| faceYMin area | 100 | 0.02 rel | stated | 2 mm remnant flat × 50 mm height |
| faceYHeadLow / High area | 45.14 | 0.02 rel | stated | y = 10 flat (100 mm²) split by the Ø5 shaft bite of 9.73 mm² |
| faceYShaftEnd area | 19.63 | 0.02 rel | stated | π·2.5² |
| faceZMin / faceZMax area | 66.63 | 0.02 rel | stated | 100 − 4·16·(1−π/4) − π·2.5² |
| shaft exposed start | 9.708 | 0.02 | stated | sheet pin extent; equals 6 + √(16 − 1.5²) |
| shaft exposed length | 78.292 | 0.02 | stated | sheet; 88 − 9.708 |
| shaft mid-y | 48.854 | 0.02 | stated | sheet axis point; (9.708 + 88) / 2 |
| edit overallLength +10 | ΔV = 196.350 | 0.01 rel | derived | π·(shaftDiameter/2)²·10; bbox [0, 10, 0] |
| edit holeDiameter +1 | ΔV = −431.969 | 0.01 rel | derived | −π·(3² − 2.5²)·bodyHeight; bbox [0, 0, 0] |

Construction that matches the sheet: extrude the 10 × 10 mm square on z from 70 to 120, fillet the four vertical corners R4, subtract the Ø5 bore at (105, 5), union a Ø5 cylinder on +y through (105, 95) from inside the head out to y = yMin + overallLength. The four Ø8 "pins" are those fillet arcs. Do not build a Ø10 circular tube — that would have three planar faces, not eight, and one Ø10 cylinder, not four Ø8 pins.

## 6. Defaults retained

Envelope comparison tolerance 0.05 mm (sheet values are 0.1 mm or integer). Cylinder radius tolerance 0.05 mm. Face and section relative area bands 0.01–0.02 because the shaft/fillet cheeks move area at the third decimal. Export volume agreement 0.002. Blockout band 5200–7200 mm³ covers an envelope-only T (filleted or box head plus shaft, no bore): about 5460 mm³ for a Ø10 head cylinder plus shaft, 5850 mm³ for the filleted head plus shaft, 6950 mm³ for a box head plus a 5 × 5 × 78 mm shaft prism. Material, density and process stay unset.

## 7. Unrepresentable or low-confidence features

No threads, drafts, chamfers or edge blends appear in the sources beyond the four R4 corners. The iso/top views look like a circular tube; that is a rendering artefact of large fillets, not a second interpretation. Surface area is sheet-stated only. The 0.68 mm³ cheek volume is implied by sheet volume minus the simple-union formula; it is not dimensioned as its own feature. Reference CAD and mesh are evaluator-only, so `deviation` is unset.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [100.0, 0.0, 70.0] → [110.0, 88.0, 120.0] | 6531.526418625023 | pass | 2026-09-19T06:10:09Z: within envelope and band |

# axjet-c2-seal_spacer — design brief

## 1. Intent and configuration

The S1 seal spacer of the AXJET-220 two-stage compressor module (assembly `axjet-c2`, body `seal_spacer`): a plain 2618-T61 ring, OD 115 × ID 40 × 14 long, clamped in the rotor stack on the Ø40 drum between the rotor-1 rear spigot boss (Ø100, assembly z 24) and the rotor-2 front face (assembly z 38). Its OD is the rotating half of the stator-1 inner-band two-tooth labyrinth, running 0.5 mm radially inside the band's inner surface (r 58.0). The bore is modelled at Ø40.0, line-to-line on the drum. The authoritative source is `sources/axjet_design_and_implementation_guide.md`: the section 14.1 body table (row `seal-spacer`), section 4.4 (rotor-1 rear spigot, stator inner bands) and section 8.1 (rotor stack). The assembly attaches the part by the rigid joint `spacerOnDrum` at its own-frame point [0, 0, 0], axis [0, 0, 1].

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | Section 14.1 table row `seal-spacer`: ring OD 115, ID 40, length 14, own origin at its front face (assembly z 24), 2618-T61, 2760 kg/m³. Section 4.4: rotor-1 rear spigot Ø100 pilots the spacer (OD Ø115, z 24 … 38, 0.5 mm inside the S1 inner band); stator inner band inner surface r 58.0 with a two-tooth labyrinth at 0.5 mm radial gap. Section 8.1: stack order blisk 1 → spacer (OD Ø115 × ID Ø40, z 24 … 38) → blisk 2; drum Ø40 h6. |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| outer diameter (labyrinth land) | 115 | mm | guide 14.1 table; 4.4; 8.1 | 0.01 (cylinder check ±0.02 on radius) | stated |
| inner diameter (drum bore) | 40.0 | mm | guide 14.1 table; 8.1; intent (line-to-line) | 0.01 (cylinder check ±0.02 on radius) | stated |
| length | 14 | mm | guide 14.1 table; 4.4 and 8.1 (assembly z 24 … 38) | 0.01 (dimension ±0.02) | stated |
| own origin at the front face, axis +z | assembly z 24 | mm | guide 14.1 table; intent; joint `spacerOnDrum` | envelope 0.05 | stated |
| front face bears on the rotor-1 rear spigot boss | Ø100 boss at assembly z 24 | mm | guide 4.4; intent | face z 0 ±0.05 | stated |
| rear face carries rotor-2 | assembly z 38 | mm | guide 8.1, 14.1 (rotor-2 disc z 38 … 62); intent | face z 14 ±0.05 | stated |
| radial gap to the stator-1 band (r 58.0) | 0.5 | mm | guide 4.4, 14.1; intent | assembly-level (`spacerSeal` min_gap 0.4) | stated; 0.4 in 8.1 is open |
| material / density | 2618-T61 / 2760 | kg/m³ | guide 14.1 table | – | stated (Appendix C: assumed) |
| pilot recess for the Ø100 spigot | none (plain ring) | – | intent, 14.1 "modelled (ring)" | – | open |
| edge breaks, finish, anti-rotation | none | – | not stated | – | open |

## 4. Coordinate frame, scale, and measurement method

Own frame per the intent and the section 14.1 table: origin on the ring axis at the front face (assembly z 24); +z along the spool axis from the front face (z 0) aft to the rear face (z 14, assembly z 38); x and y parallel to the assembly x and y (right-handed). Datum A is the front face z = 0 (rotor-1 seat), datum B the bore axis (the z axis), datum C the rear face z = 14 (rotor-2 seat). Assembly placement is a pure translation of +24 along z. No images, drawings or meshes were supplied; every dimension is a number quoted from the guide's text and tables, so no scaling or rectification was needed. The envelope is [−57.5, −57.5, 0] … [57.5, 57.5, 14] with 0.05 tolerance.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| outerDiameter | 115 mm | 0.01 | stated | guide 14.1 table (OD 115), 4.4 (OD Ø115), 8.1 (OD Ø115) |
| innerDiameter | 40 mm | 0.01 | stated | guide 14.1 table (ID 40), 8.1 (ID Ø40); modelled 40.0 line-to-line per the intent |
| spacerLength | 14 mm | 0.01 | stated | guide 14.1 table (length 14), 4.4 and 8.1 (z 24 … 38) |
| volume | 127,823.6 mm³ | rel 0.002 | derived | π/4 · (115² − 40²) · 14 = 2906.25π · 14 |
| surface area | 25,077.8 mm² | rel 0.005 | derived | 2 · π/4 · (115² − 40²) + π · 115 · 14 + π · 40 · 14 = 7982.5π |
| centre of mass | (0, 0, 7) | 0.05 | derived | solid of revolution about z; at spacerLength / 2 |
| mass (information) | 0.353 kg | – | derived | 127,823.6 mm³ × 2760 kg/m³ |
| section `mid_z` (z 7) | 9130.25 mm², 1 loop, 1 hole | rel 0.005 | derived | π/4 · (115² − 40²) |
| section `meridian_x` (x 0) | 1050 mm², 2 loops, 0 holes | rel 0.005 | derived | 2 · (57.5 − 20) · 14 |
| faces `frontFace` (z 0, −) and `rearFace` (z 14, +) | 9130.25 mm² each | rel 0.005 | derived | annulus area as above |
| cylinders `bore` Ø40 hole and `odSeal` Ø115 pin | axis z through the origin | radius 0.02, axis 0.02 | stated | lengths are left to `stackLength` so the length edit does not resize the pinned cylinders |
| dimension `stackLength` | 14 | 0.02 | stated | between `frontFace` and `rearFace` |
| probes | solid at r 38.75, z 7 in each quadrant; void at (0, 0, 7) and (59.5, 0, 7) | – | derived | mid-wall points sit 18.75 mm from the bore and OD and 7 mm from both faces; void points are 20 mm and 2 mm from the nearest surface |
| blockout band | 125,000 … 147,000 mm³ | – | derived | covers the finished ring (127,824) and a bore-less Ø115 × 14 disc (π · 57.5² · 14 = 145,416), both of which fill the envelope |
| edit test spacerLength +1 | ΔV = +9130.25 mm³, Δbbox (0, 0, 1) | rel 0.02 | derived | π/4 · (115² − 40²) · 1; feasible interval spacerLength > 0 (the model must assert it); sweep 10, 14, 18; infeasible delta −20 (length −6) |

## 6. Defaults retained

- Envelope tolerance 0.05 mm and parameter digital tolerances 0.01 mm: template defaults, appropriate for exact turned geometry from prismatic CAD.
- Volume tolerance 0.2 % and area tolerances 0.5 %: export and tessellation agreement for an all-analytic solid, much tighter than any feature that could be missing (the bore alone is 14 % of the disc).
- Process "CNC turning (nominal)": not stated by the guide; it affects no geometry.
- Only one edit test (spacerLength). The other two dimensions are the drum fit and the labyrinth land, both pinned interfaces; an edit test on them would resize a pinned check. The rear face (rotor-2 seat, datum C) moves with spacerLength, so it is checked by `rearFace` and `stackLength` but not pinned in an interface.

## 7. Unrepresentable or low-confidence features

- The two labyrinth teeth belong to the stator-1 inner band; the spacer OD is a plain land. The radial gap (0.5 mm here versus 0.4 mm in section 8.1 and the assembly's `spacerSeal` min_gap 0.4) is an assembly-level check, not part of this contract.
- Section 4.4 says the rotor-1 spigot "pilots" the spacer; a Ø100 pilot recess in the front face is not modelled because the intent and the 14.1 table call the part a plain ring.
- The drum fit (interference or clearance) is not stated; the bore is nominal 40.0.
- No chamfers, edge breaks, balance cuts or dowel holes are stated, so none are modelled.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|

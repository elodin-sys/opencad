# axjet-c2-rotor_1 — design brief

## 1. Intent and configuration

Rotor-1 blisk of the AXJET-220/2 two-stage transonic axial compressor module (assembly `axjet-c2`, body `rotor_1`, joint `rotor1OnDrum` rigid at own-frame point [0, 0, 0], axis +z). One solid: a revolved disc with a forward seal arm (three labyrinth teeth) and a rear D100 spigot boss, carrying 29 lofted blades between the conical hub flow surface and a flat tip at r 90.0. Material 2618-T61 forged bar, density 2760 kg/m³, 5-axis milled. The authoritative source is the AXJET-220 design and implementation guide (sections 3.2, 4.1–4.4, 8.1, 14.1); blade sections are the section 4.3 baseline (circular-arc camber, NACA-65 thickness) until step-2 section files exist.

Construction recipe for the modeller:
- Disc: revolve the (r, z) profile (20, −8) → (20, 24) → (50, 24) → (50, 16) → (61.0, 16) → (57.6, 0) → (57.6, −8) → (46.1, −8) → seal arm land r 46.1 forward to z −18 with three rectangular teeth to r 48.1 (0.8 wide, centres z −16, −13, −10) → (44, −18) → (44, −8) → close. Solid disc: no web cavities (section 7).
- Blades: build each section in the blade-to-blade plane (z, r·θ): a circular-arc camber line with tangent angles κ1 (LE) and κ2 = κ1 − camber (TE) from +z, chord c, stagger (κ1 + κ2)/2; NACA-65 thickness distribution scaled to t_max (hub 1.92, mean 1.10, tip 0.80), LE radius 0.3, TE thickness 0.5. The LE leads in the direction of rotation: going downstream along the camber line the blade moves toward −θ, so for blade 0 the LE sits on the +y side and the concave pressure surface faces +y. Stack the three sections radially on their centroids along the radial line through +x, with the axial position chosen so the hub section's LE lies at z 0 (the stacking z is about 7.5, about 0.45 of the hub axial chord 16.78). Loft (ruled=False) with the sections extended slightly below the hub and beyond r 90, then intersect with the flow-annulus body (revolved: hub flow surface out to r 90.0, z ≤ 16) so the tip is a cylinder r 90.0 and nothing passes z 16; fuse into the disc; fillet the blade–hub junction r 1.5; pattern 29× about +z (pitch 12.4138°).
- Assert `17 <= bladeCount <= 47` (guide 2.3) and `hubThicknessRatio > 0`.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | mm, deg; 3.2 flow-path radii, 4.1–4.3 stage data and metal angles, 4.4 blisk geometry, 8.1 rotor stack (drum D46 shoulder z −14 … −8, seal spacer z 24 … 38), 14.1 rotor-1 body and assembly clearances |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| blade count | 29 | – | guide 4.1, 4.4 | exact | stated |
| radial stacking on section centroids, no lean/sweep | – | – | guide 4.4 | – | stated |
| hub flow surface r 57.6 over z −8 … 0, straight to r 61.0 at z 16 | 57.6 / 61.0 | mm | guide 3.2, 4.4 | 0.01 | stated |
| hub blade extent | z 0 … 16 | mm | guide 4.4 | 0.01 | stated (conflict with the hub chord, section 7) |
| flat tip radius | 90.0 | mm | guide 4, 4.4 | 0.01 | stated |
| minimum tip thickness | 0.8 | mm | guide 2.3, 4.4 | 0.01 | stated (governs over 3.5 %) |
| root fillet on the hub | 1.5 | mm | guide 2.3, 4.4 | 0.01 | stated |
| section radii hub / mean / tip | 57.6 / 73.8 / 90.0 | mm | guide 4.2 | 0.01 | stated |
| inlet metal angle | 62.0 / 67.3 / 71.4 | deg | guide 4.3 | 0.1 | stated |
| camber | 32.7 / 14.0 / 7.6 | deg | guide 4.3 | 0.1 | stated |
| exit metal angle | 29.3 / 53.3 / 63.8 | deg | guide 4.3 | 0.1 | stated (= inlet − camber) |
| stagger | 45.65 / 60.3 / 67.6 | deg | guide 4.3 ("approx.") | 0.1 | derived |
| max thickness / chord | 8 / 5 / 3.5 | % | guide 4.3 | 0.1 % | stated |
| chord | 24 / 22 / 20 | mm | guide 4.1, 4.2 item 4 | 0.01 | stated |
| LE radius / TE thickness | 0.3 / 0.5 | mm | guide 4.3 | 0.01 | stated |
| bore | D40 (modelled 40.0) through z −8 … 24 | mm | guide 4.4, 8.1 | 0.01 | stated |
| front face z −8 clamped by the stack nut (revision 1; the drum shoulder moved to z 62) | −8 | mm | guide 4.4, 8.1; revision 1 change 1 | 0.01 | stated |
| rim | r 50 … 57.6, z −8 … 16 | mm | guide 4.4 | 0.01 | stated |
| web 10 thick at the bore, 6 at r 50 | 10 / 6 | mm | guide 4.4 | – | open (not representable with the stated faces) |
| seal arm r 44 … 48.1, z −18 … −8, three teeth to D96.2 | 44 / 48.1 / −18 / 3 | mm | guide 4.4, 8.1 | 0.01 | stated |
| rear face z 24, D100 spigot boss r 20 … 50 | 24 / 50 | mm | guide 4.4, intent | 0.01 | stated |
| nothing outside r 50 behind z 16 | – | mm | intent (4 mm to the stator_1 inner band) | – | stated (section discRear, probes behindRim) |
| mass | about 0.9 | kg | guide 4.4, 12 | volume band ±7 % | stated estimate |
| 10 µm interference, two D4 dowels | – | – | guide 4.4 | – | not modelled (intent) |

## 4. Coordinate frame, scale, and measurement method

Own frame of the part, which the assembly uses for joint `rotor1OnDrum`: origin on the rotor axis at the blade leading-edge plane (the hub section's LE, assembly z 0); +z along the axis, downstream with the flow; the spool turns positively about +z (from +x toward +y); +x parallel to the assembly x (engine up), with blade 0's stacking line on +x; +y completes the right-handed frame. Datums: A, the bore axis; B, the front face z −8 (drum shoulder seat); C, the LE plane z 0. Angles are measured from the axial direction; as in the guide's Appendix A, a positive relative metal angle means the camber line leans against rotation going downstream (the LE leads in +θ).

No images or meshes: every value is read from the guide's text and tables. All lengths in mm. Derived acceptance values come from Pappus integrals over the revolved (r, z) profile, plus a blade estimate: section area = 0.68 × c × t_max at the hub and mean and 0.72 × c × t_max at the tip (NACA-65 area factor, with a margin for the 0.5 mm TE), interpolated quadratically in r and integrated over the exposed span r 59.3 … 90.0.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| bladeCount | 29 | 0.01 | stated | guide 4.1, 4.4; feasible 17 … 47 (guide 2.3) |
| bladePitch | 12.4138 deg | 0.001 | derived | 360 / bladeCount |
| bladeClockingAngle | 0 deg | 0.01 | defaulted | blade 0 on +x; unclocked in the sources |
| hubRadius | 57.6 | 0.01 | stated | guide 3.2, 4.4 |
| hubRadiusTe | 61.0 | 0.01 | stated | guide 3.2, 4.4 |
| frontFaceZ | −8 | 0.01 | stated | guide 4.4, 8.1 |
| hubLeZ | 0 | 0.01 | stated | guide 3.2, 4.4 |
| hubTeZ | 16 | 0.01 | stated | guide 3.2, 4.4 |
| tipRadius | 90.0 | 0.01 | stated | guide 4, 4.4 |
| meanRadius | 73.8 | 0.01 | stated | guide 4.2 |
| rootFilletRadius | 1.5 | 0.01 | stated | guide 2.3, 4.4 |
| minTipThickness | 0.8 | 0.01 | stated | guide 2.3, 4.4 |
| hub/mean/tipInletMetalAngle | 62.0 / 67.3 / 71.4 deg | 0.1 | stated | guide 4.3 |
| hub/mean/tipCamber | 32.7 / 14.0 / 7.6 deg | 0.1 | stated | guide 4.3 |
| hub/mean/tipExitMetalAngle | 29.3 / 53.3 / 63.8 deg | 0.1 | derived | inlet − camber; equals the tabulated values |
| hub/mean/tipStagger | 45.65 / 60.3 / 67.6 deg | 0.1 | derived | (inlet + exit) / 2 for a circular arc |
| hub/mean/tipChord | 24 / 22 / 20 | 0.01 | stated | guide 4.1, 4.2 item 4 |
| hub/mean/tipThicknessRatio | 0.08 / 0.05 / 0.035 | 0.001 | stated | guide 4.3 |
| tipMaxThickness | 0.8 | 0.01 | derived | max(0.035 × 20, 0.8) |
| leRadius / teThickness | 0.3 / 0.5 | 0.01 | stated | guide 4.3 |
| boreRadius | 20.0 | 0.01 | stated | D40 H6 modelled 40.0 |
| rearFaceZ | 24 | 0.01 | stated | guide 4.4, 8.1 |
| spigotRadius | 50.0 | 0.01 | stated | D100 spigot = rim inner radius |
| sealArmInnerRadius | 44.0 | 0.01 | stated | guide 4.4 |
| sealToothTipRadius | 48.1 | 0.01 | stated | D96.2 |
| sealArmFrontZ | −18 | 0.01 | stated | guide 4.4, 8.1 |
| sealToothCount | 3 | 0.01 | stated | guide 4.4, 8.1 |
| sealArmLandRadius | 46.1 | 0.2 | inferred | 2.0 mm teeth below the D96.2 tips (2.1 mm arm wall); keeps the groove void probes 1 mm from every surface |
| sealToothWidth | 0.8 | 0.2 | inferred | rectangular machinable teeth |
| sealToothPitch | 3.0 | 0.2 | inferred | three teeth over the 10 mm arm |
| firstToothZ | −16.0 | 0.2 | inferred | teeth at z −16, −13, −10 |
| volume | 306386 mm³ ±7 % | – | derived | disc 290175 (block r 20 … 50 × 32 = 211115, rim 71694, arm 5944, teeth 1421) + 29 × (535 + 24) = 16211; 0.9 kg → 326087 (+6.4 %) inside the band |
| surface area | 83170 mm² ±8 % | – | derived | profile surfaces 44367 − footprints 905 + 29 × 1369 |
| centre of mass | (0, 0, 6.75) ±0.3 | – | derived | (290175 × 6.710 + 16211 × 7.5) / 306386 |
| section discFront z −4 | 9166.4 mm², 1 loop, 1 hole | 1 % | derived | π(57.6² − 20²) |
| section bladeRow z 8 | 1 loop, 1 hole | – | derived | blades fused to the rim |
| section discRear z 20 | 6597.3 mm², 1 loop, 1 hole | 1 % | derived | π(50² − 20²) |
| section sealArm z −17 | 594.4 mm², 1 loop, 1 hole | 5 % | derived | π(46.1² − 44²) |
| face frontFace z −8 (sum) | 8572.0 mm² | 2 % | derived | π(44² − 20²) + π(57.6² − 46.1²) |
| face rearFace z 24 | 6597.3 mm² | 1 % | derived | π(50² − 20²) |
| face rimRearFace z 16 | 3835.9 mm² | 3 % | derived | π(61² − 50²); TE trims and fillets touch it |
| face sealArmFront z −18 | 594.4 mm² | 5 % | derived | π(46.1² − 44²) |
| cylinders | bore r 20 (z −8 … 24), hub extension r 57.6 (z −8 … 0), spigot r 50 (z 16 … 24), arm bore r 44 (z −18 … −8), tooth tips r 48.1, blade tips r 90.0 | 0.01–0.02 | stated | guide 4.4 |
| dimensions | spanZ 42, hubAxialLength 32, tipDiameterX/Y 180 | 0.05 | derived | bbox; the nearest tips come within 0.01 of −x (no blade at 180°) |
| thickness tipThickness | p05 ≥ 0.35 in blade 0's outer 6 mm | – | derived | proxy only; LE r 0.3 and TE 0.5 are thinner than the 0.8 max |
| seal groove void probes | r 47.1 at z −14.5 and −11.5 | – | derived | 1.0 from the tooth-tip cylinder and the land, 1.1 from the flanks |
| bladePassage void probes | r 75 and r 85 at half pitch (6.207°), z 8 | – | derived | ≥ 2 mm from either blade with camber and the stacking uncertainty |
| edit bladeCount +2 | +1118 mm³, bbox 0 | rel 0.4 | derived | 2 × (535 + 24); sweep 27 / 29 / 31; infeasible −13 (16 blades) and +19 (48) |
| edit hubThicknessRatio +0.02 | +870 mm³, bbox 0 | rel 0.4 | derived | hub section area × 1.25 over the exposed span, 29 blades; infeasible −0.08 (zero thickness) |
| blockout band | 295000 … 335000 mm³ | – | derived | disc 290175 + blades between thin flat plates (~5000) and chunky plates (~45000) |

## 6. Defaults retained

- Blade clocking: blade 0 on +x (affects only the angular phase; the assembly spin covers a full pitch).
- Edges not called out (bore, spigot, faces, seal arm) stay sharp; the guide gives no chamfers.
- Release status `reconstruction` kept from the template.
- The bore is modelled at 40.0 line-to-line on the drum; the 10 µm interference and the two D4 dowels are left out, as the intent says.

## 7. Unrepresentable or low-confidence features

- Web: the guide's "web 10 mm thick at the bore, 6 mm at r 50" cannot coexist with the stated faces: a 6 mm web joining a rim that ends at z 16 cannot also reach a rear face at z 24 spanning r 20 … 50. The stated mass (0.9 kg) matches the solid disc (0.85 kg), not a webbed one (about 0.55–0.65 kg). The contract models the solid disc; the web is an open question for the stress and modal cases.
- Hub chord versus axial extent: chord 24 at stagger 45.65° is 16.78 mm axially; the blade is clipped at z 16, which trims about 0.1–0.2 mm of the exposed root trailing edge (the r 57.6 section itself is buried in the rim).
- Tip section: 3.5 % × 20 = 0.70 mm is below the 0.8 mm minimum, so the tip is built at 0.8 mm (4.0 %). The transonic tip (M_rel 1.30) would use a multiple-circular-arc profile per the guide; the intent fixes circular-arc camber and NACA-65 thickness.
- Seal teeth shape (rectangular, 2.0 high, 0.8 wide, pitch 3.0) is inferred; only the tip diameter and count are stated.
- Blade count is not counted directly by any acceptance item (the coaxial tip faces share one axis); it is enforced by the parameter and the bladeCount edit test.
- The balance correction (material removal on the rear face at r 45) and the drive dowels are not modelled.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|

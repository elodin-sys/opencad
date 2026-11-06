# axjet-c2-ogv_ring — design brief

## 1. Intent and configuration

The AXJET-220 outlet guide vane (OGV) ring, body `ogv_ring` of the assembly `axjet-c2`. It is the third stacked casing ring (z 58 ... 80) and carries the 47-vane OGV row between an outer band (integral with the casing, flow surface r 90.0) and an inner band (flow surface r 66.5 -> 67.5, bore r 63.5 with a two-tooth labyrinth around the rotor_2 rear seal sleeve). The whole ring is one solid of 6061-T6 (2700 kg/m3), 5-axis milled with the vanes integral with both bands.

Configuration: the baseline single row of section 4.3 (0 deg exit flow); the tandem pair and the solidity-1.8 options of section 4.2 are not modelled. The part is drafted in the assembly frame because the assembly places it with joint `ogvOnCase` (rigid) at its own-frame point [0, 0, 58], axis +z: the front face z 58 seats on the stator_1 rear flange. The rear flange takes the diffuser of the full engine.

Authoritative source: `sources/axjet_design_and_implementation_guide.md` (sections 3, 3.2, 4.1-4.4, 11, 14.1, Appendix B).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | Section 3: frame. 3.2: flow-path radii (OGV hub 66.5 -> 67.5, tip 90.0, station 3 at z 80). 4.1: 47 vanes, chord 14. 4.3: metal angles, LE radius 0.25 and TE thickness 0.5. 4.4: casing rings, PCD 206, OD 200/212, inner band r 63.5, labyrinth at 0.5 mm. 11: material and process. 14.1: body row and joint `ogvOnCase`. Appendix B: angle sign convention. No images, drawings or reference meshes. |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| ring axial extent | z 58 ... 80 | mm | intent; 4.4; 14.1 | 0.05 | stated |
| casing OD between flanges | 200 (z 64 ... 74) | mm | intent; 3.2; 4.4 | 0.05 | stated |
| front flange | z 58 ... 64, OD 224, 8 x D5.5 (M5 clearance) on PCD 212, one on +x | mm | revision 1 change 2 (was OD 212, 8 x D6.4 on PCD 206) | 0.05 | stated |
| rear flange | z 74 ... 80, OD 224, 8 x D5.5 on PCD 212 | mm | revision 1 change 2 | 0.05 | stated (clocking inferred) |
| outer flow surface | r 90.0 over z 59 ... 78 (band r 90.0 ... 93.5 integral) | mm | intent; 3.2 | 0.05 | stated |
| station bore | r 90.25 over z 58 ... 59 and z 78 ... 80 | mm | intent; 3.2 station 3 | 0.05 | stated |
| inner band flow surface | r 66.5 z 59 ... 61, straight to r 67.5 at z 76, r 67.5 to z 80 | mm | intent; 3.2 | 0.05 | stated |
| inner band front face | z 59 (4 mm behind the rotor_2 hub TE at z 55) | mm | intent | 0.05 | stated |
| inner band bore and tooth tips | r 63.5; nothing inside r 63.5 | mm | intent; 4.4 | 0.05 | stated |
| labyrinth | two teeth facing the rotor_2 sleeve OD 126, z 62 ... 70, 0.5 mm radial gap | mm | intent; 4.4; 14.1 | 0.1 (gap) | stated; tooth shape inferred |
| vane count | 47, single row | – | intent; 4.1 | exact | stated |
| vane chord | 14 | mm | intent; 4.1 | 0.01 | stated |
| vane LE / axial extent | LE z 61; TE inside z 76 | mm | intent; 3.2 | 0.1 | stated |
| inlet metal angles hub/mean/tip | 53.8 / 48.9 / 44.5 | deg | 4.3 | 0.1 | stated |
| camber hub/mean/tip | 65.3 / 60.4 / 56.0 | deg | 4.3 | 0.1 | stated (= inlet - exit) |
| exit metal angle | -11.5 (all sections) | deg | 4.3 | 0.1 | stated |
| stagger hub/mean/tip | about 21.1 / 18.7 / 16.5 | deg | 4.3 | 0.1 | stated (approx.), derived |
| max thickness / chord | 8 / 7 / 6 % | – | 4.3 | 0.1 % | stated |
| LE radius / TE thickness | 0.25 / 0.5 | mm | 4.3 | 0.01 | stated |
| stacking | radial | – | intent | – | stated (reading in section 4) |
| material / density | 6061-T6, 2700 kg/m3 | – | 11; 14.1 | – | stated |
| sleeve seal clearance | min_gap 0.4 to rotor_2 | mm | 14.1 acceptance `sleeveSeal` | – | stated (assembly) |
| single body | 1 solid | – | intent | exact | stated |

## 4. Coordinate frame, scale, and measurement method

Frame: the AXJET assembly frame of guide section 3, so the part needs no placement transform. The origin is on the engine axis at the stage-1 rotor leading-edge plane, z runs along the axis in the flow direction, x points up (dorsal) and y completes the right-handed frame. The ring spans z 58 ... 80. Datum A is the front mating face z 58 (normal -z). Datum B is the engine axis. Datum C is the plane y = 0 through the +x hole of the front flange.

Angles: metal angles and stagger are measured from the +z axis, positive in the direction of rotation (Appendix B). The rotation sense is not stated, so it is inferred right-handed about +z: +theta runs from +x toward +y. The vane leading edges therefore point toward +theta (53.8 deg at the hub) and the trailing edges 11.5 deg toward -theta.

Vane construction (for the modeller): each vane is lofted through planar sections normal to its radial stacking line at r 66.5 (hub), 78.25 (mean) and 90.0 (tip). Each section has a circular-arc camber line from the inlet metal angle to -11.5 deg (chord 14) and a NACA-65 thickness distribution scaled to tmax/c, with a 0.25 mm leading-edge radius and a 0.5 mm trailing edge (guide section 14: "circular-arc camber lines and NACA-65 thickness"). Each section's leading edge is at z 61. Tangentially, the section centroids lie on one radial line. The axial chord is 14 cos(stagger) = 13.06 / 13.26 / 13.42, so the trailing edges land at z 74.06 / 74.26 / 74.42. Extend the loft about 0.5 mm into both bands and fuse it.

Measurement method: every dimension comes from the text. There are no images, drawings or meshes, so no pixel scale is involved. Areas and volumes were computed analytically. Revolved regions use pi * sum((ro^2 - ri^2) dz). Each D5.5 bolt hole (r 103.25 ... 108.75) lies wholly inside the r 100 ... 112 flange land, so it removes a full circle of pi x 2.75^2 = 23.758 mm2 (revision 1). Vanes use section area 0.65 tmax c (NACA-65 area factor from the 65-010 ordinates) plus 0.25 teThickness c (half of a linear TE ramp).

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| ringFrontZ | 58 | 0.01 | stated | intent; 4.4; 14.1 |
| ringRearZ | 80 | 0.01 | stated | intent; 3.1 station 3 |
| casingOd | 200 | 0.01 | stated | intent "OD 200 between the flanges". Edit +2: pi(101^2-100^2) x 10 = 6315 mm3. Feasible 184 < casingOd < 224 (wall >= 2 mm over r 90, below the flange OD). Sweep 196/200/204. Infeasible +26 (226 > 224) and -20 (180, zero wall); both must assert |
| flangeOd | 224 | 0.01 | stated | revision 1 change 2 (was 212, intent; 4.4) |
| flangeThickness | 6 | 0.01 | stated | intent z 58 ... 64 and 74 ... 80 |
| boltCount | 8 | 0.01 | stated | intent; 4.4 |
| boltHoleDiameter | 5.5 | 0.01 | stated | revision 1 change 2: M5 clearance (was 6.4) |
| boltPcd | 212 | 0.01 | stated | revision 1 change 2 (was 206) |
| boltClockAngle | 0 | 0.1 deg | stated | intent "one on +x"; rear flange inferred to match |
| outerFlowRadius | 90.0 | 0.01 | stated | intent; 3.2 |
| stationBoreRadius | 90.25 | 0.01 | stated | intent; 3.2 station 3 |
| outerFlowFrontZ | 59 | 0.01 | stated | intent |
| outerFlowRearZ | 78 | 0.01 | stated | intent |
| innerBandFrontZ | 59 | 0.01 | stated | intent |
| hubFrontRadius | 66.5 | 0.01 | stated | intent; 3.2 |
| hubRearRadius | 67.5 | 0.01 | stated | intent; 3.2. Edit +0.5: band pi x [int_ramp(4.4333u + 0.0055556u^2) du + (68^2-67.5^2) x 4] = pi x (505.0 + 271.0) = 2438, minus the vane roots buried by the higher band, about 0.22 mm x 11.9 mm2 x 47 = 123, giving 2315 mm3 |
| hubRampStartZ | 61 | 0.01 | stated | intent |
| hubRampEndZ | 76 | 0.01 | stated | intent |
| innerBoreRadius | 63.5 | 0.01 | stated | intent; 4.4 |
| labyrinthToothCount | 2 | 0.01 | stated | intent; 4.4 |
| labyrinthGrooveRadius | 64.5 | 0.5 | inferred | tooth height not stated; 1.0 mm grooves leave a band wall of at least 2.07 mm (r 64.5 to 66.57 at z 62) |
| labyrinthToothWidth | 1.0 | 0.5 | inferred | tooth width not stated; rectangular 1 mm lands |
| labyrinthToothPitch | 4.0 | 1.0 | inferred | teeth at the quarter points of the 8 mm sleeve span (z 64, 68) |
| labyrinthFrontZ | 62 | 0.5 | inferred | groove region equals the stated sleeve span z 62 ... 70 |
| labyrinthRearZ | 70 | 0.5 | inferred | as above |
| vaneCount | 47 | 0.01 | stated | intent; 4.1 |
| vaneChord | 14 | 0.01 | stated | intent; 4.1. Edit +1: thickness area scales as c^2 (9668 x ((15/14)^2 - 1) = 1431) and the TE share as c (1897/14 = 136), giving 1570 mm3 with tolerance_rel 0.35 (loft). Infeasible +2.5: chord 16.5 puts the tip TE at 61 + 16.5 cos 16.5 = 76.8 > 76; must assert |
| vaneLeZ | 61 | 0.01 | stated | intent; 3.2 |
| inletMetalHub / Mean / Tip | 53.8 / 48.9 / 44.5 | 0.1 deg | stated | 4.3 table |
| exitMetalAngle | -11.5 | 0.1 deg | stated | 4.3 table |
| camberHub / Mean / Tip | 65.3 / 60.4 / 56.0 | 0.1 deg | derived | inletMetal - exitMetalAngle (equals the table) |
| staggerHub / Mean / Tip | 21.15 / 18.7 / 16.5 | 0.1 deg | derived | (inletMetal + exitMetalAngle) / 2 (table "approx." 21.1 / 18.7 / 16.5) |
| tmaxHub / Mean / Tip | 0.08 / 0.07 / 0.06 | 0.001 | stated | 4.3 table |
| leRadius | 0.25 | 0.01 | stated | 4.3 (stators) |
| teThickness | 0.5 | 0.01 | stated | 4.3 |
| vaneMeanRadius | 78.25 | 0.01 | derived | (hubFrontRadius + outerFlowRadius) / 2 |
| vaneClockAngle | 0 | 3.8 deg | inferred | not stated; first vane on +x (half-pitch tolerance) |

| acceptance value | expected | tolerance | evidence / formula |
|---|---|---|---|
| volume | 264230 mm3 | 3000 | casing revolve with OD 224 flanges pi x 56496.81 + 2 pi (112^2-106^2) x 6 = 226800, minus 16 holes x 6 x 23.758 = 2281, gives 224519 (revision 1: +25044 per flange). Inner band pi x 9728.5 = 30563, minus grooves pi(64.5^2-63.5^2) x 6 = 2413, gives 28150. Vanes 47 x 23.06 mean span x 10.67 mean section = 11564 |
| surface area | 125880 mm2 | 5 % | casing 71985 (revision 1: +8653 per flange) + inner band 22561 + vanes 31333 (2 x 14.67 mean camber-arc length x 23.06 + TE face, less the band footprints) |
| centre of mass | (0, 0, 69.03) | 0.3 | z = (174429 x 68.992 + 28150 x 70.477 + 11564 x 66.3 + 2 x 25044 x 69) / 264233. The vane centroid z 66.3 is at 45 % of the camber arc |
| envelope | [-112, -112, 58] ... [112, 112, 80] | 0.05 | flange OD 224 |
| section z 58.5 | 13629.6 mm2, 1 loop, 9 holes | 1 % | pi(112^2-90.25^2) - 8 x 23.758 |
| section z 60 | 14996.4 mm2, 2 loops, 10 holes | 1 % | 13771.2 flange + 1225.2 band (no vanes ahead of z 61) |
| section z 66 | 8202.7 mm2, 1 loop, 48 holes | 3 % | 5969.0 casing + 962.7 band (groove r 64.5) + 47 x 27.0 vane cuts (width about t/cos(phi): 1.22 / 1.06 / 0.90 at phi 24.9 / 23.2 / 21.4 deg, plus the half-ramp TE share). The holes are the bore and 47 passages |
| section z 75.5 | 15403.2 mm2, 2 loops, 10 holes | 1 % | 13771.2 + pi(67.467^2-63.5^2) = 1632.0 (vanes end by z 74.42) |
| section z 79 | 15275.8 mm2, 2 loops, 10 holes | 1 % | 13629.6 + 1646.2 |
| faces z 58 / z 80 casing | 13629.6 mm2 (z 58 pinned; z 80 by the z 79 section) | 1 % | annulus r 90.25 ... 112 less 8 x 23.758; the z 80 face carries no area pin because the bundle check would read an area above the r 63.5 bore's cross-section as a blind-hole floor |
| faces z 64 / z 74 | 7802.2 mm2 each | 1 % | pi(112^2-100^2) = 7992.2 less 8 x 23.758 |
| face z 80 band | 1646.2 mm2 | 1 % | pi(67.5^2-63.5^2) |
| face z 59 band | 1225.2 mm2 | 1 % | pi(66.5^2-63.5^2) |
| bore steps z 59 / z 78 | 141.6 mm2 each | 5 % | pi(90.25^2-90^2) |
| sleeve clearance | 0.4 ... 0.6 mm | – | tooth tip r 63.5 vs sleeve r 63.0 (stated 0.5) |
| bolt-hole count | 16 | exact | 8 per flange |
| blockout band | 221300 ... 271300 mm3 | – | casing revolve without holes is 226800 (it already spans the full bbox; the earlier band shifted by the revision 1 flange growth 49310); the band reaches up to a blockout with the inner band and simplified vanes |

## 6. Defaults retained

- Envelope tolerance 0.05 mm and stated-parameter tolerance 0.01 mm. These are the template's digital thresholds; they suit turned features defined by stated numbers.
- Bolt holes are cut through each flange only (z 58 ... 64, z 74 ... 80) and not into the OD 200 body. A drilled clearance hole on a flange stops at its back face.
- No edge breaks, chamfers or vane fillets. None are stated, and a fillet would shift volume and areas without evidence.
- No abradable recess. The guide applies abradable only over the rotors.
- Thickness check at p05 >= 0.4 mm. It keeps the 0.5 mm trailing edge from being modelled thinner.

## 7. Unrepresentable or low-confidence features

- Vane thickness details. The NACA-65 form, the LE radius blend and the TE treatment are only partly fixed by the sources. The vane volume carries about +-20 % (+-2000 mm3), which is why the total-volume tolerance is 3000 mm3 and the z 66 section has a 3 % band. The contract checks the vanes through counts (48 holes at z 66), the section areas, the vane-free sections at z 60 and z 75.5, and the edit test on chord.
- Labyrinth tooth shape. Only the count, the tip radius and the 0.5 mm gap are stated; the width, pitch, depth and groove extent are inferred and carry wide tolerances.
- Changed (revision 1, reviewer notes): flanges OD 224 with 8 x D5.5 on PCD 212. The guide's D6.4 on PCD 206 with OD 212 left the holes 0.2 mm through the flange rim with no seat for a head or nut.
- Rotation sense and vane clocking are inferred; see the open questions.
- Assembly concern: the casing front-face corner sits about 3 mm from the rotor_2 tip trailing edge, below the assembly's rotor2ToOgv 4.0 mm if that is measured body to body.
- Not modelled: the tandem OGV pair and the solidity-1.8 option (section 4.2), instrumentation taps (ps3 wall taps and the pt3 Kiel probe in section 10 have no stated positions on this ring), and the bolts themselves.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|

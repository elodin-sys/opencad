# gear-pair — design brief

## 1. Intent and configuration

Design the spur-gear pair and carrier plate exactly as specified in the attached specification: module 2, pressure angle 20 deg, zero profile shift, 20-tooth pinion (bore Ø6) at the origin and 40-tooth wheel (bore Ø8) at (60, 0), face width 8 (z 0..8), 0.10 mm total circular backlash, pinion tooth centred on +x and the wheel phased half a pitch so the pair meshes; carrier 110 x 50 x 5 under the gears with clearance holes on the axes. Three separate solids in one KCL file; the pair must turn through a full pitch without interference. Declare the three solids by contained points, the bores as cylinders, and the gears' tooth counts and mesh as acceptance items.

The authoritative configuration is the supplied text specification, pinned by its full SHA-256 below. Deliverable modeling will use one native editable KCL 2 file containing the pinion, wheel, and carrier as three separate solids. Their common seating plane is z=0. The carrier does not enclose the wheel footprint; the specified wheel overhang remains. This bundle stage creates the contract and brief only. It contains no CAD model or claim of measured geometry.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/gear-pair-spec.md | text | authoritative | 0acea6d35513df93499f95e7242721b64488c45819f6e58ebd09ed627fb09d87 | mm and deg; unversioned supplied specification, revision identified by this hash. Prefix matches 0acea6d35513. Contains dimensions, phase, motion and STEP scoring requirements. |

This is the only file under `sources/`; no `reference/` directory, images, drawing sheets, mesh, coordinate table, or reference ingest output was supplied. The evaluator-only involutes are unavailable and must not be imported or used to construct the model.

## 3. Requirement record

All source references in this table mean `sources/gear-pair-spec.md`. Digital tolerances below are comparison thresholds, not production fit specifications. They do not change the nominal source requirements.

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| Assembly | 3 separate solids; one KCL file | count / file | opening paragraph; user intent | exact topology | stated; solid_count, solids, sections, bodyMaterial; file count is a later deliverable audit |
| Module / pressure angle / shift | 2 / 20 / 0 | mm / deg / dimensionless | table Module, Pressure angle, Profile shift | 0.01 mm / 0.01 deg / 0.000001 | stated; gears, involuteFlank probes, radial witnesses, envelope and area |
| Pinion | 20 teeth; axis (0,0), +z; bore Ø6 | count / mm | table Pinion | exact count; axis 0.01; diameter 0.01 | stated; pinionTeeth, pinionBore, sixMillimeterHoles, pinion solid |
| Wheel | 40 teeth; axis (60,0), +z; bore Ø8 | count / mm | table Wheel | exact count; axis 0.01; diameter 0.01 | stated; wheelTeeth, wheelBore, eightMillimeterHoles, wheel solid |
| Center distance | 60 | mm | table Centre distance | each axis 0.01 | stated; cylinder axes and fullPitchMesh axis origins; no cylinder-to-cylinder DimensionSpec exists |
| Gear thickness / station | 8; z=0..8 for both | mm | table Face width | face planes / length 0.02 | stated; named cap faces, face-width dimensions, bore lengths, gearMidsection |
| Addendum / dedendum | 1.0 m / 1.25 m | module multiples | table Addendum / dedendum | factors 0.000001 | stated; rootMaterial/rootSpaces and tipMaterial/beyondTips, analytic sections |
| Tip / root radii | pinion 22 / 17.5; wheel 42 / 37.5 | mm | table Addendum / dedendum | source-derived construction; radial probes +/-0.25 | stated and derivable; radial witnesses, envelope, gear descriptions |
| Tip clearance | 0.5 | mm | table Addendum / dedendum | derived from module/factors | stated; 60-22-37.5 = 60-42-17.5 = 0.5; radial witnesses and mesh |
| Circular backlash / per-tooth thinning | 0.10 total / 0.05 per gear | mm | table Circular backlash | parameter 0.001; pitch-flank probe guard 0.015 | stated; pitchThickness probes and fullPitchMesh description; exact circular-backlash metrology is not a schema field |
| Initial phase | pinion tooth +x; wheel space -x, tooth pattern +4.5 | deg | table Tooth phase | 0.01 | stated geometry; wheelPhase derived; four phase probes and fullPitchMesh |
| Carrier | 110 x 50 x 5; (-25,-25,-5) to (85,25,0) | mm | table Carrier plate | face / dimension 0.02 | stated; six carrier faces, dimensions, carrierMidsection, carrier solid |
| Carrier holes | Ø6 at (0,0); Ø8 at (60,0); z=-5..0 | mm | table Carrier plate | diameter / axis 0.01; length 0.02 | stated; two carrier cylinders, void probes, cylinder counts |
| Seating | carrier top and gear bottoms touch at z=0; separate | mm / topology | Frame paragraph | zero nominal gap; Boolean tolerance 0.001 mm3 | stated; pinionSeat, wheelSeat, two contact clearances, solid_count |
| Motion | pinion 0..18; wheel 0..-9; ratio -1/2 | deg / ratio | table Motion; one full pitch derived from 20 teeth | 73 poses plus local refinement | stated behavior; fullPitchMesh, 72 intervals of 0.25 deg |
| Interference / flank gap | 0 interference; gap <=0.15 | mm3 / mm | table Motion | inspector Boolean tolerance 0.001 mm3 | stated; static clearance and fullPitchMesh; continuous proof remains open |
| Whole-profile involute fidelity | p95 <=0.10 | mm | final scored-on-STEP paragraph | 0.10 threshold | stated; recorded in gears and analytic probes, evaluator-only percentile not locally representable |
| Editable native construction | native editable KCL; suggested 12–16 flank samples | implementation | opening and Frame paragraphs | source recommendation, not a manufacturing tolerance | stated; two edit tests; no reference-geometry imports |

The four cylinders locate both axes independently, so their 0.01 mm perpendicular axis bands imply at most 0.02 mm worst-case center-distance error; 60 mm remains the exact nominal design value. Carrier clearance holes are exactly the stated diameters. No shaft, bearing, fastener, hub, keyway, chamfer, relief, or added gap is authorized by this source.

## 4. Coordinate frame, scale, and measurement method

Origin is the intersection of the pinion axis with the carrier top and gear bottom plane, (0,0,0). +x points from the pinion axis toward the wheel axis at (60,0); +z points upward along both shafts; +y completes the right-handed frame, with x cross y = z. Viewed from +z with +x to the right, +y is up. Positive tooth-pattern angles are counterclockwise in that view. Datum A is the carrier top at z=0. Datum B is the pinion / Ø6 carrier-hole axis. Datum C is the y=0 plane through the two axes, oriented by +x toward the wheel. The plate occupies [-25,85] x [-25,25] x [-5,0]; both gears occupy z=0..8.

There are no pixels to measure, feature counts to infer from an image, scale bars to calibrate, camera perspectives to rectify, or reference-model measurements. All stated values are transcribed from the text; all remaining numbers are reproducible analytic calculations or explicitly disclosed digital verification choices. The source tooth counts are 20 and 40. Coordinates and lengths use mm; contract angles use deg. Involute formulas in section 5 use radians internally and must be converted explicitly in later KCL.

The initial pinion pattern has tooth centers at 0 + k*18 deg. Wheel tooth centers are 4.5 + k*9 deg; its spaces include -x (180 deg) and +x (0 deg). The largest wheel coordinate about its axis is H=41.921745526 mm, not its 42 mm circumradius, because no tip arc crosses a cardinal axis in this phase. The finished assembly bbox is [-25, -41.921745526, -5] to [101.921745526, 41.921745526, 8] mm, size [126.921745526, 83.843491052, 13] mm. The later blockout must match these same six coordinates.

The source permits sampled involute flanks (12–16 points recommended) or a library implementation honoring all requirements. Use sufficient resolution to preserve the pitch-thickness witnesses and the evaluator's p95 limit. The installed gear skill documents no backlash argument for `gear::spur`; do not assume its unmodified profile meets the required thinning. This brief prescribes equations and checks, not KCL implementation text.

## 5. Measurement and inference record

Every contract parameter is listed below. There are 23 parameters: 22 stated and 1 derived; 0 measured, 0 measured (reference model), 0 inferred dimensional parameters, and 0 defaulted dimensional parameters. Each later parameter declaration must be a literal top-level constant using the exact lowerCamelCase identifier. Nominal derived constants carry their formula for traceability. The two edit tests target independent stated parameters; no equality lock should freeze them.

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| gearModule | 2 mm | 0.01 | stated | sources/gear-pair-spec.md — table Module: "2 mm" |
| pressureAngle | 20 deg | 0.01 | stated | sources/gear-pair-spec.md — table Pressure angle: "20 deg" |
| profileShift | 0 | 0.000001 | stated | sources/gear-pair-spec.md — table Profile shift: "0 (both gears)" |
| pinionTeeth | 20 | 0.000001 | stated | sources/gear-pair-spec.md — table Pinion: "20 teeth, bore Ø6, axis at (0, 0) parallel to z" |
| wheelTeeth | 40 | 0.000001 | stated | sources/gear-pair-spec.md — table Wheel: "40 teeth, bore Ø8, axis at (60, 0) parallel to z" |
| pinionBoreDiameter | 6 mm | 0.01 | stated | sources/gear-pair-spec.md — table Pinion: "bore Ø6"; Carrier plate: "with Ø6 and Ø8 clearance holes on the two gear axes" |
| wheelBoreDiameter | 8 mm | 0.01 | stated | sources/gear-pair-spec.md — table Wheel: "bore Ø8"; Carrier plate: "with Ø6 and Ø8 clearance holes on the two gear axes" |
| centerDistance | 60 mm | 0.01 | stated | sources/gear-pair-spec.md — table Centre distance: "60 mm (= (20 + 40) x 2 / 2)" |
| gearFaceWidth | 8 mm | 0.01 | stated | sources/gear-pair-spec.md — table Face width: "8 mm, both gears from z = 0 to z = 8" |
| addendumFactor | 1 | 0.000001 | stated | sources/gear-pair-spec.md — table Addendum / dedendum: "1.0 m / 1.25 m" |
| dedendumFactor | 1.25 | 0.000001 | stated | sources/gear-pair-spec.md — table Addendum / dedendum: "1.0 m / 1.25 m" |
| totalBacklash | 0.1 mm | 0.001 | stated | sources/gear-pair-spec.md — table Circular backlash: "0.10 mm total: thin each tooth by 0.05 mm at its pitch circle" |
| pinionPhase | 0 deg | 0.01 | stated | sources/gear-pair-spec.md — table Tooth phase: "pinion has a tooth centred on +x" |
| pinionAxisX | 0 mm | 0.01 | stated | sources/gear-pair-spec.md — table Pinion: "axis at (0, 0) parallel to z" |
| pinionAxisY | 0 mm | 0.01 | stated | sources/gear-pair-spec.md — table Pinion: "axis at (0, 0) parallel to z" |
| wheelAxisY | 0 mm | 0.01 | stated | sources/gear-pair-spec.md — table Wheel: "axis at (60, 0) parallel to z" |
| gearBaseZ | 0 mm | 0.01 | stated | sources/gear-pair-spec.md — table Face width: "from z = 0 to z = 8"; Frame: "gear bottoms at z = 0, carrier top at z = 0" |
| carrierLength | 110 mm | 0.01 | stated | sources/gear-pair-spec.md — table Carrier plate: "110 x 50 x 5 mm" |
| carrierWidth | 50 mm | 0.01 | stated | sources/gear-pair-spec.md — table Carrier plate: "110 x 50 x 5 mm" |
| carrierThickness | 5 mm | 0.01 | stated | sources/gear-pair-spec.md — table Carrier plate: "110 x 50 x 5 mm" |
| carrierMinX | -25 mm | 0.01 | stated | sources/gear-pair-spec.md — table Carrier plate: "corner at (-25, -25, -5) to (85, 25, 0)" |
| carrierMinY | -25 mm | 0.01 | stated | sources/gear-pair-spec.md — table Carrier plate: "corner at (-25, -25, -5) to (85, 25, 0)" |
| wheelPhase | 4.5 deg | 0.01 | derived | 180 / wheelTeeth |

The unspecific root-transition shape is a construction uncertainty, not a measured dimension. For transparent analytic estimates only, use a sharp radial extension from each base-circle involute endpoint to its stated root circle, with circular root-space and tip arcs. This is a provisional convention; no fillet radius or manufacturing cutter was invented. The source fixes the involute flanks and all radii, but does not uniquely fix this below-base transition. Gear-derived area and volume bands are 2%, aggregate volume 1%, surface area 3%, and centroid 0.15 mm per axis to avoid presenting the provisional model as exact source data. The carrier area and volume band is 0.2%. These bands cannot waive the independent tooth counts, source dimensions, mesh requirements or evaluator-only profile threshold.

For each gear let m=gearModule, N be its tooth count, D its bore diameter, alpha=pressureAngle converted to radians, and J=totalBacklash. At the required zero profile shift:

- Rp=m*N/2; Rb=Rp*cos(alpha); Ra=Rp+m*addendumFactor; Rf=Rp-m*dedendumFactor.
- Circular tooth thickness s=pi*m/2-J/2. Half-thickness angle at the pitch circle is s/(2*Rp); do not subtract J/2 from each flank separately.
- h0=s/(2*Rp)+tan(alpha)-alpha. For Rb <= r <= Ra, t=sqrt((r/Rb)^2-1) and the half tooth angle h(r)=h0-(t-atan(t)). Below Rb, the provisional radial extension uses h(r)=h0.
- T=sqrt((Ra/Rb)^2-1), ha=h0-T+atan(T), and F(T)=T^3/3-((1+T^2)*atan(T)-T)/2.
- Net gear section A=pi*Rf^2+N*[h0*(Ra^2-Rf^2)-2*Rb^2*F(T)]-pi*D^2/4. Gear volume is gearFaceWidth*A.
- Outer gear perimeter P=N*[2*(Rb-Rf)+Rb*T^2+2*Ra*ha+Rf*(2*pi/N-2*h0)]. Gear surface area is 2*A+gearFaceWidth*(P+pi*D).
- Carrier Ac=carrierLength*carrierWidth-pi*(pinionBoreDiameter^2+wheelBoreDiameter^2)/4. Vc=carrierThickness*Ac; Sc=2*Ac+carrierThickness*[2*(carrierLength+carrierWidth)+pi*(pinionBoreDiameter+wheelBoreDiameter)].
- Carrier centroid xc=[5500*30-pi*3^2*0-pi*4^2*60]/Ac. Total centroid is [(Vp*0+Vw*60+Vc*xc)/V, 0, ((Vp+Vw)*4-2.5*Vc)/V], where V=Vp+Vw+Vc. All three volumes carry the same arbitrary unit density for this geometric centroid; no mass is specified.
- Sum the surface areas of all three separate solids. The two sides of contacting interfaces remain separate faces and are included in that sum.

| analytic quantity | value | unit | evidence |
|---|---|---|---|
| Pinion rp | 20 | mm | derived; radial-root convention where applicable |
| Pinion rb | 18.793852416 | mm | derived; radial-root convention where applicable |
| Pinion ra | 22 | mm | derived; radial-root convention where applicable |
| Pinion rf | 17.5 | mm | derived; radial-root convention where applicable |
| Pinion h0 | 0.0921942 | rad | derived; radial-root convention where applicable |
| Pinion ha | 0.030335454 | rad | derived; radial-root convention where applicable |
| Pinion ta | 0.608517823 | dimensionless | derived; radial-root convention where applicable |
| Pinion area | 1193.387615727 | mm2 | derived; radial-root convention where applicable |
| Pinion perimeter | 263.054092306 | mm | derived; radial-root convention where applicable |
| Wheel rp | 40 | mm | derived; radial-root convention where applicable |
| Wheel rb | 37.587704831 | mm | derived; radial-root convention where applicable |
| Wheel ra | 42 | mm | derived; radial-root convention where applicable |
| Wheel rf | 37.5 | mm | derived; radial-root convention where applicable |
| Wheel h0 | 0.053549292 | rad | derived; radial-root convention where applicable |
| Wheel ha | 0.017486059 | rad | derived; radial-root convention where applicable |
| Wheel ta | 0.49855085 | dimensionless | derived; radial-root convention where applicable |
| Wheel area | 4923.578944181 | mm2 | derived; radial-root convention where applicable |
| Wheel perimeter | 514.442515334 | mm | derived; radial-root convention where applicable |
| Common circular tooth thickness | 3.091592654 | mm | pi*gearModule/2-totalBacklash/2 |
| Per-gear tooth thinning | 0.05 | mm | totalBacklash/2 |
| Tip clearance | 0.5 | mm | gearModule*(dedendumFactor-addendumFactor) |
| Wheel cardinal extent H | 41.921745526 | mm | 42*cos(pi/40-ha40) |
| Carrier net area Ac | 5421.46018366 | mm2 | 110*50-pi*(3^2+4^2) |
| Carrier horizontal centroid x | 29.878310559 | mm | (5500*30-pi*4^2*60)/Ac |
| Circle-overlap lens L | 56.530327606 | mm2 | circle-lens formula below |
| Single clipped cap C | 0.267436531 | mm2 | 42^2*acos(H/42)-H*sqrt(42^2-H^2) |
| Envelope-only blockout Vblock | 83539.741184558 | mm3 | 27500+8*(pi*(22^2+42^2)-L-3*C) |

Envelope formula: H=Ra40*cos(pi/wheelTeeth-ha40). With the initial phase and counts, xmin=carrierMinX, xmax=pinionAxisX+centerDistance+H, ymin=-H, ymax=H, zmin=gearBaseZ-carrierThickness, zmax=gearBaseZ+gearFaceWidth. The pinion reaches radius 22 on each cardinal axis; the wheel and plate determine the assembly extremes.

Blockout construction is the solid union of the unperforated carrier and two addendum-circle gear envelopes of height 8, with the wheel disk clipped to local x/y in [-H,H]. This preserves the actual phased bbox while omitting bores and teeth. Clipping removes four circular caps from the wheel disk; its left cap lies entirely inside the pinion envelope, so the union loses only three caps. For radii r=22, R=42, separation d=60, overlap lens L=r^2*acos((d^2+r^2-R^2)/(2*d*r))+R^2*acos((d^2+R^2-r^2)/(2*d*R))-sqrt((-d+r+R)*(d+r-R)*(d-r+R)*(d+r+R))/2. A clipped cap has area C=R^2*acos(H/R)-H*sqrt(R^2-H^2). Vblock=110*50*5+8*[pi*(22^2+42^2)-L-3*C]=83539.741184558 mm3. The declared band is +/-5%: 79362.75412533..87716.728243786 mm3. It includes the whole assembly envelope, rather than only the carrier. Unclipped 42 mm wheel cylinders would miss the final bbox tolerance by about 0.0783 mm.

Probe construction: body points are strictly interior; bore probes sit on hole axes away from end planes; phase and tip probes are at least 0.25 mm from their intended tip/root boundaries. For flank witnesses use pinion tooth center theta=180 deg and wheel tooth center theta=94.5 deg to avoid the other body. At a radius r, each nominal flank angle is theta +/- h(r). Solid and void points shift inward/outward by epsilon/r radians, with epsilon=0.015 mm at Rp and epsilon=0.12 mm at Rb+0.5 and Ra-0.3. These are tangential construction offsets, not measured profile errors. Root probes lie on space centerlines at Rf +/-0.25, away from the unspecified transition corners. No probe relies on a wall whose location is inferred. A wheel-space void point facing the pinion would be inside pinion material, so the enforceable whole-assembly space probe uses the diametrically opposite +x space instead.

Every acceptance value and its evidence is recorded below. Coordinates for faces use in-plane centroids, and `mode: one` is explicit throughout. Cylinder axis points are at mid-depth, with separate ranges for the gear and carrier, so stacked holes are not mistaken for one long cylinder. Empty acceptance groups mean the source supplies no such requirement.

| acceptance value | value | tolerance / interpretation | provenance | formula / evidence |
|---|---|---|---|---|
| envelope.min | [-25, -41.921745526, -5] | 0.05 mm per axis | derived | Plate fixes xmin=-25 and zmin=-5; phased wheel fixes ymin=-H. |
| envelope.max | [101.921745526, 41.921745526, 8] | 0.05 mm per axis | derived | Wheel fixes xmax=60+H and ymax=H; gearFaceWidth fixes zmax=8. |
| acceptance.bbox_tolerance | 0.05 | mm | defaulted | Digital shape-comparison band; permits small sampling differences, not full 42 mm-radius disks at the final phase. |
| volume.expected | 76043.033397564 | 1% | derived | V=8*(A20+A40)+5*Ac; conditional radial-root estimate, formulas below. |
| surface_area.expected | 31468.596211209 | 3% | derived | Sum 2*A+height*(outer perimeter+bore circumference) for all three separate bodies; touching faces counted per body. |
| center_of_mass.expected | [41.729506395, 0, 1.682924417] | 0.15 mm per axis | derived | Volume-weighted body centroids; uniform unit density only; carrier centroid corrected for unequal bores. |
| solid_count | 3 | exact | stated | Opening source paragraph: three separate solids; no fused bodies. |
| sections.gearMidsection.plane / at | z = 4 | mm; interior station | derived | Mid-thickness station: gearBaseZ+gearFaceWidth/2 or gearBaseZ-carrierThickness/2. |
| sections.gearMidsection.area | 6116.966559908 | 2% | derived | Two disjoint annular toothed regions; each has one central bore. Area uses the analytic radial-root estimate. Tooth counts are checked separately in acceptance.gears; loops do not count teeth. |
| sections.gearMidsection.loops | 2 | exact | stated topology | Two disjoint annular toothed regions; each has one central bore. Area uses the analytic radial-root estimate. Tooth counts are checked separately in acceptance.gears; loops do not count teeth. |
| sections.gearMidsection.holes | 2 | exact | stated topology | Two disjoint annular toothed regions; each has one central bore. Area uses the analytic radial-root estimate. Tooth counts are checked separately in acceptance.gears; loops do not count teeth. |
| sections.carrierMidsection.plane / at | z = -2.5 | mm; interior station | derived | Mid-thickness station: gearBaseZ+gearFaceWidth/2 or gearBaseZ-carrierThickness/2. |
| sections.carrierMidsection.area | 5421.46018366 | 0.2% | derived | One rectangular plate region with two through-hole loops; area=110*50-pi*(3^2+4^2). |
| sections.carrierMidsection.loops | 1 | exact | stated topology | One rectangular plate region with two through-hole loops; area=110*50-pi*(3^2+4^2). |
| sections.carrierMidsection.holes | 2 | exact | stated topology | One rectangular plate region with two through-hole loops; area=110*50-pi*(3^2+4^2). |
| faces.carrierTop.plane / at / normal | z = 0, outward +z | 0.02 mm | stated | Source carrier corners or gear z=0..8 interval. |
| faces.carrierTop.center | [29.878310559, 0] | 0.02 mm in-plane | derived | Single face centroid: (x,y) for z faces, (y,z) for x faces, (x,z) for y faces. Carrier horizontal centroid includes unequal bore removals. |
| faces.carrierTop.area | 5421.46018366 | 0.2% | derived | Ac or A20/A40 for horizontal faces; 50*5 or 110*5 for plate sides. mode=one for every face; no implicit summing. |
| faces.carrierBottom.plane / at / normal | z = -5, outward -z | 0.02 mm | stated | Source carrier corners or gear z=0..8 interval. |
| faces.carrierBottom.center | [29.878310559, 0] | 0.02 mm in-plane | derived | Single face centroid: (x,y) for z faces, (y,z) for x faces, (x,z) for y faces. Carrier horizontal centroid includes unequal bore removals. |
| faces.carrierBottom.area | 5421.46018366 | 0.2% | derived | Ac or A20/A40 for horizontal faces; 50*5 or 110*5 for plate sides. mode=one for every face; no implicit summing. |
| faces.carrierLeft.plane / at / normal | x = -25, outward -x | 0.02 mm | stated | Source carrier corners or gear z=0..8 interval. |
| faces.carrierLeft.center | [0, -2.5] | 0.02 mm in-plane | derived | Single face centroid: (x,y) for z faces, (y,z) for x faces, (x,z) for y faces. Carrier horizontal centroid includes unequal bore removals. |
| faces.carrierLeft.area | 250 | 0.2% | derived | Ac or A20/A40 for horizontal faces; 50*5 or 110*5 for plate sides. mode=one for every face; no implicit summing. |
| faces.carrierRight.plane / at / normal | x = 85, outward +x | 0.02 mm | stated | Source carrier corners or gear z=0..8 interval. |
| faces.carrierRight.center | [0, -2.5] | 0.02 mm in-plane | derived | Single face centroid: (x,y) for z faces, (y,z) for x faces, (x,z) for y faces. Carrier horizontal centroid includes unequal bore removals. |
| faces.carrierRight.area | 250 | 0.2% | derived | Ac or A20/A40 for horizontal faces; 50*5 or 110*5 for plate sides. mode=one for every face; no implicit summing. |
| faces.carrierFront.plane / at / normal | y = -25, outward -y | 0.02 mm | stated | Source carrier corners or gear z=0..8 interval. |
| faces.carrierFront.center | [30, -2.5] | 0.02 mm in-plane | derived | Single face centroid: (x,y) for z faces, (y,z) for x faces, (x,z) for y faces. Carrier horizontal centroid includes unequal bore removals. |
| faces.carrierFront.area | 550 | 0.2% | derived | Ac or A20/A40 for horizontal faces; 50*5 or 110*5 for plate sides. mode=one for every face; no implicit summing. |
| faces.carrierBack.plane / at / normal | y = 25, outward +y | 0.02 mm | stated | Source carrier corners or gear z=0..8 interval. |
| faces.carrierBack.center | [30, -2.5] | 0.02 mm in-plane | derived | Single face centroid: (x,y) for z faces, (y,z) for x faces, (x,z) for y faces. Carrier horizontal centroid includes unequal bore removals. |
| faces.carrierBack.area | 550 | 0.2% | derived | Ac or A20/A40 for horizontal faces; 50*5 or 110*5 for plate sides. mode=one for every face; no implicit summing. |
| faces.pinionBottom.plane / at / normal | z = 0, outward -z | 0.02 mm | stated | Source carrier corners or gear z=0..8 interval. |
| faces.pinionBottom.center | [0, 0] | 0.02 mm in-plane | derived | Single face centroid: (x,y) for z faces, (y,z) for x faces, (x,z) for y faces. Carrier horizontal centroid includes unequal bore removals. |
| faces.pinionBottom.area | 1193.387615727 | 2% | derived | Ac or A20/A40 for horizontal faces; 50*5 or 110*5 for plate sides. mode=one for every face; no implicit summing. |
| faces.pinionTop.plane / at / normal | z = 8, outward +z | 0.02 mm | stated | Source carrier corners or gear z=0..8 interval. |
| faces.pinionTop.center | [0, 0] | 0.02 mm in-plane | derived | Single face centroid: (x,y) for z faces, (y,z) for x faces, (x,z) for y faces. Carrier horizontal centroid includes unequal bore removals. |
| faces.pinionTop.area | 1193.387615727 | 2% | derived | Ac or A20/A40 for horizontal faces; 50*5 or 110*5 for plate sides. mode=one for every face; no implicit summing. |
| faces.wheelBottom.plane / at / normal | z = 0, outward -z | 0.02 mm | stated | Source carrier corners or gear z=0..8 interval. |
| faces.wheelBottom.center | [60, 0] | 0.02 mm in-plane | derived | Single face centroid: (x,y) for z faces, (y,z) for x faces, (x,z) for y faces. Carrier horizontal centroid includes unequal bore removals. |
| faces.wheelBottom.area | 4923.578944181 | 2% | derived | Ac or A20/A40 for horizontal faces; 50*5 or 110*5 for plate sides. mode=one for every face; no implicit summing. |
| faces.wheelTop.plane / at / normal | z = 8, outward +z | 0.02 mm | stated | Source carrier corners or gear z=0..8 interval. |
| faces.wheelTop.center | [60, 0] | 0.02 mm in-plane | derived | Single face centroid: (x,y) for z faces, (y,z) for x faces, (x,z) for y faces. Carrier horizontal centroid includes unequal bore removals. |
| faces.wheelTop.area | 4923.578944181 | 2% | derived | Ac or A20/A40 for horizontal faces; 50*5 or 110*5 for plate sides. mode=one for every face; no implicit summing. |
| cylinders.pinionBore.point | [0, 0, 4] | axis offset <=0.01 mm | stated x/y; derived z | Axis from source; choose midpoint z to distinguish coaxial holes in touching bodies. |
| cylinders.pinionBore.direction / kind | [0,0,1]; hole | parallel to z; inspector 0.5 deg matching threshold | stated | Source z-parallel bore / clearance-hole axes; sign of cylinder axis is irrelevant. |
| cylinders.pinionBore.diameter | 6 | radius +/-0.005 mm = diameter +/-0.01 mm | stated | Ø6 pinion stack or Ø8 wheel stack; no additional clearance allowance. |
| cylinders.pinionBore.length | 8 | 0.02 mm | derived | Through length equals body face width or carrier thickness. |
| cylinders.pinionBore.t_range | [-4, 4] | mm from point along direction | derived | [-length/2,+length/2] about the chosen midpoint; nominal absolute z extents are [0,8] or [-5,0]. |
| cylinders.wheelBore.point | [60, 0, 4] | axis offset <=0.01 mm | stated x/y; derived z | Axis from source; choose midpoint z to distinguish coaxial holes in touching bodies. |
| cylinders.wheelBore.direction / kind | [0,0,1]; hole | parallel to z; inspector 0.5 deg matching threshold | stated | Source z-parallel bore / clearance-hole axes; sign of cylinder axis is irrelevant. |
| cylinders.wheelBore.diameter | 8 | radius +/-0.005 mm = diameter +/-0.01 mm | stated | Ø6 pinion stack or Ø8 wheel stack; no additional clearance allowance. |
| cylinders.wheelBore.length | 8 | 0.02 mm | derived | Through length equals body face width or carrier thickness. |
| cylinders.wheelBore.t_range | [-4, 4] | mm from point along direction | derived | [-length/2,+length/2] about the chosen midpoint; nominal absolute z extents are [0,8] or [-5,0]. |
| cylinders.carrierPinionHole.point | [0, 0, -2.5] | axis offset <=0.01 mm | stated x/y; derived z | Axis from source; choose midpoint z to distinguish coaxial holes in touching bodies. |
| cylinders.carrierPinionHole.direction / kind | [0,0,1]; hole | parallel to z; inspector 0.5 deg matching threshold | stated | Source z-parallel bore / clearance-hole axes; sign of cylinder axis is irrelevant. |
| cylinders.carrierPinionHole.diameter | 6 | radius +/-0.005 mm = diameter +/-0.01 mm | stated | Ø6 pinion stack or Ø8 wheel stack; no additional clearance allowance. |
| cylinders.carrierPinionHole.length | 5 | 0.02 mm | derived | Through length equals body face width or carrier thickness. |
| cylinders.carrierPinionHole.t_range | [-2.5, 2.5] | mm from point along direction | derived | [-length/2,+length/2] about the chosen midpoint; nominal absolute z extents are [0,8] or [-5,0]. |
| cylinders.carrierWheelHole.point | [60, 0, -2.5] | axis offset <=0.01 mm | stated x/y; derived z | Axis from source; choose midpoint z to distinguish coaxial holes in touching bodies. |
| cylinders.carrierWheelHole.direction / kind | [0,0,1]; hole | parallel to z; inspector 0.5 deg matching threshold | stated | Source z-parallel bore / clearance-hole axes; sign of cylinder axis is irrelevant. |
| cylinders.carrierWheelHole.diameter | 8 | radius +/-0.005 mm = diameter +/-0.01 mm | stated | Ø6 pinion stack or Ø8 wheel stack; no additional clearance allowance. |
| cylinders.carrierWheelHole.length | 5 | 0.02 mm | derived | Through length equals body face width or carrier thickness. |
| cylinders.carrierWheelHole.t_range | [-2.5, 2.5] | mm from point along direction | derived | [-length/2,+length/2] about the chosen midpoint; nominal absolute z extents are [0,8] or [-5,0]. |
| dimensions.carrierLength | 110 mm along x | 0.02 mm | stated | Separation of carrierLeft, carrierRight |
| dimensions.carrierWidth | 50 mm along y | 0.02 mm | stated | Separation of carrierFront, carrierBack |
| dimensions.carrierThickness | 5 mm along z | 0.02 mm | stated | Separation of carrierBottom, carrierTop |
| dimensions.pinionFaceWidth | 8 mm along z | 0.02 mm | stated | Separation of pinionBottom, pinionTop |
| dimensions.wheelFaceWidth | 8 mm along z | 0.02 mm | stated | Separation of wheelBottom, wheelTop |
| dimensions.pinionSeat | 0 mm along z | 0.01 mm | stated | Separation of carrierTop, pinionBottom |
| dimensions.wheelSeat | 0 mm along z | 0.01 mm | stated | Separation of carrierTop, wheelBottom |
| dimensions.assemblySpanX | 126.921745526 mm along x | 0.05 mm | derived | Overall envelope extent; formula for H below. |
| dimensions.assemblySpanY | 83.843491052 mm along y | 0.05 mm | derived | Overall envelope extent; formula for H below. |
| dimensions.assemblySpanZ | 13 mm along z | 0.05 mm | derived | Overall envelope extent; formula for H below. |
| solids.pinion.contains_point | [0, 10, 4] | strictly inside | derived witness | Point has generous material clearance; names the body without relying on transient face or solid indices. |
| solids.pinion.volume | 9547.100925818 | 2% | derived | gearFaceWidth*A_pinion; analytic radial-root estimate defined in acceptance.volume.note. |
| solids.wheel.contains_point | [60, 10, 4] | strictly inside | derived witness | Point has generous material clearance; names the body without relying on transient face or solid indices. |
| solids.wheel.volume | 39388.631553445 | 2% | derived | gearFaceWidth*A_wheel; analytic radial-root estimate defined in acceptance.volume.note. |
| solids.carrier.contains_point | [30, 0, -2.5] | strictly inside | derived witness | Point has generous material clearance; names the body without relying on transient face or solid indices. |
| solids.carrier.volume | 27107.300918301 | 0.2% | derived | carrierThickness*(carrierLength*carrierWidth-pi*(pinionBoreDiameter^2+wheelBoreDiameter^2)/4). |
| clearances.pinionCarrierContact.a / b | pinion / carrier | named solids | stated | Touching at z=0, separate material bodies; zero nominal overlap volume. The 0.001 mm3 threshold is only numerical Boolean tolerance. |
| clearances.pinionCarrierContact.min_gap | 0 | mm | stated | No penetration; gear/carrier contact and gear-pair clearance. |
| clearances.pinionCarrierContact.max_gap | 0 | mm | stated | Exact contact for carrier interfaces; 0.15 mm maximum closest-flank gap for gear pair. |
| clearances.pinionCarrierContact.interference_tolerance | 0.001 | mm3 | defaulted | Numerical Boolean threshold; nominal requirement remains zero overlap. |
| clearances.wheelCarrierContact.a / b | wheel / carrier | named solids | stated | Touching at z=0, separate material bodies; zero nominal overlap volume. The wheel overhang is intentional. |
| clearances.wheelCarrierContact.min_gap | 0 | mm | stated | No penetration; gear/carrier contact and gear-pair clearance. |
| clearances.wheelCarrierContact.max_gap | 0 | mm | stated | Exact contact for carrier interfaces; 0.15 mm maximum closest-flank gap for gear pair. |
| clearances.wheelCarrierContact.interference_tolerance | 0.001 | mm3 | defaulted | Numerical Boolean threshold; nominal requirement remains zero overlap. |
| clearances.initialGearClearance.a / b | pinion / wheel | named solids | stated | Initial-pose no-interference and maximum flank-gap check; full-pitch motion is separately required below. |
| clearances.initialGearClearance.min_gap | 0 | mm | stated | No penetration; gear/carrier contact and gear-pair clearance. |
| clearances.initialGearClearance.max_gap | 0.15 | mm | stated | Exact contact for carrier interfaces; 0.15 mm maximum closest-flank gap for gear pair. |
| clearances.initialGearClearance.interference_tolerance | 0.001 | mm3 | defaulted | Numerical Boolean threshold; nominal requirement remains zero overlap. |
| probes.bodyMaterial.1 | [0, 10, 4] | solid; strict interior/exterior | derived witness | Interior witnesses for the three material bodies, away from holes, teeth, and contact faces. |
| probes.bodyMaterial.2 | [60, 10, 4] | solid; strict interior/exterior | derived witness | Interior witnesses for the three material bodies, away from holes, teeth, and contact faces. |
| probes.bodyMaterial.3 | [30, 0, -2.5] | solid; strict interior/exterior | derived witness | Interior witnesses for the three material bodies, away from holes, teeth, and contact faces. |
| probes.boresThroughGears.1 | [0, 0, 0.5] | void; strict interior/exterior | derived witness | The two axes must remain void through the gear thickness. |
| probes.boresThroughGears.2 | [0, 0, 4] | void; strict interior/exterior | derived witness | The two axes must remain void through the gear thickness. |
| probes.boresThroughGears.3 | [0, 0, 7.5] | void; strict interior/exterior | derived witness | The two axes must remain void through the gear thickness. |
| probes.boresThroughGears.4 | [60, 0, 0.5] | void; strict interior/exterior | derived witness | The two axes must remain void through the gear thickness. |
| probes.boresThroughGears.5 | [60, 0, 4] | void; strict interior/exterior | derived witness | The two axes must remain void through the gear thickness. |
| probes.boresThroughGears.6 | [60, 0, 7.5] | void; strict interior/exterior | derived witness | The two axes must remain void through the gear thickness. |
| probes.boresThroughCarrier.1 | [0, 0, -4.5] | void; strict interior/exterior | derived witness | The two coaxial carrier holes must remain void through the plate. |
| probes.boresThroughCarrier.2 | [0, 0, -2.5] | void; strict interior/exterior | derived witness | The two coaxial carrier holes must remain void through the plate. |
| probes.boresThroughCarrier.3 | [0, 0, -0.5] | void; strict interior/exterior | derived witness | The two coaxial carrier holes must remain void through the plate. |
| probes.boresThroughCarrier.4 | [60, 0, -4.5] | void; strict interior/exterior | derived witness | The two coaxial carrier holes must remain void through the plate. |
| probes.boresThroughCarrier.5 | [60, 0, -2.5] | void; strict interior/exterior | derived witness | The two coaxial carrier holes must remain void through the plate. |
| probes.boresThroughCarrier.6 | [60, 0, -0.5] | void; strict interior/exterior | derived witness | The two coaxial carrier holes must remain void through the plate. |
| probes.pinionToothPhase.1 | [21.5, 0, 4] | solid; strict interior/exterior | derived witness | A pinion tooth is centered on +x; radius 21.5 is inside its addendum. |
| probes.pinionSpacePhase.1 | [-21.235299323, -3.363340998, 4] | void; strict interior/exterior | derived witness | A pinion tooth space is centered at 189 deg, safely away from the other gear. |
| probes.wheelToothPhase.1 | [101.37206935, 3.256052473, 4] | solid; strict interior/exterior | derived witness | A wheel tooth is centered at +4.5 deg. |
| probes.wheelSpacePhase.1 | [101.5, 0, 4] | void; strict interior/exterior | derived witness | A wheel tooth space is centered on +x; the even 40-tooth pattern also places a space on -x toward the pinion. A void probe on -x would be occupied by the pinion and is intentionally avoided. |
| probes.rootMaterial.1 | [-17.037623875, -2.698494522, 4] | solid; strict interior/exterior | derived witness | Material 0.25 mm inside the stated root circles, along tooth-space centerlines. |
| probes.rootMaterial.2 | [97.25, 0, 4] | solid; strict interior/exterior | derived witness | Material 0.25 mm inside the stated root circles, along tooth-space centerlines. |
| probes.rootSpaces.1 | [-17.531468046, -2.776711754, 4] | void; strict interior/exterior | derived witness | Void 0.25 mm outside the stated root circles, along tooth-space centerlines; probes avoid the unspecified root-transition corners. |
| probes.rootSpaces.2 | [97.75, 0, 4] | void; strict interior/exterior | derived witness | Void 0.25 mm outside the stated root circles, along tooth-space centerlines; probes avoid the unspecified root-transition corners. |
| probes.tipMaterial.1 | [21.75, 0, 4] | solid; strict interior/exterior | derived witness | Material 0.25 mm inside each stated tip radius on a tooth centerline. |
| probes.tipMaterial.2 | [101.621298683, 3.275667247, 4] | solid; strict interior/exterior | derived witness | Material 0.25 mm inside each stated tip radius on a tooth centerline. |
| probes.beyondTips.1 | [-22.25, 0, 4] | void; strict interior/exterior | derived witness | Void 0.25 mm beyond each stated tip circle, away from the other body. |
| probes.beyondTips.2 | [102.11975735, 3.314896795, 4] | void; strict interior/exterior | derived witness | Void 0.25 mm beyond each stated tip circle, away from the other body. |
| probes.pitchThicknessSolid.1 | [-19.94144516, 1.529302109, 4] | solid; strict interior/exterior | derived witness | Both flanks of a remote tooth on each gear, at the pitch radius, bracketed by +/-0.015 mm tangential offsets from the analytic flank. Tooth thickness is pi*gearModule/2 - totalBacklash/2 = 3.091592654 mm. Pinion tooth center 180 deg; wheel tooth center 94.5 deg. These reject an unthinned standard tooth; they do not directly measure circular backlash to 0.001 mm. |
| probes.pitchThicknessSolid.2 | [-19.94144516, -1.529302109, 4] | solid; strict interior/exterior | derived witness | Both flanks of a remote tooth on each gear, at the pitch radius, bracketed by +/-0.015 mm tangential offsets from the analytic flank. Tooth thickness is pi*gearModule/2 - totalBacklash/2 = 3.091592654 mm. Pinion tooth center 180 deg; wheel tooth center 94.5 deg. These reject an unthinned standard tooth; they do not directly measure circular backlash to 0.001 mm. |
| probes.pitchThicknessSolid.3 | [58.389639, 39.967571073, 4] | solid; strict interior/exterior | derived witness | Both flanks of a remote tooth on each gear, at the pitch radius, bracketed by +/-0.015 mm tangential offsets from the analytic flank. Tooth thickness is pi*gearModule/2 - totalBacklash/2 = 3.091592654 mm. Pinion tooth center 180 deg; wheel tooth center 94.5 deg. These reject an unthinned standard tooth; they do not directly measure circular backlash to 0.001 mm. |
| probes.pitchThicknessSolid.4 | [55.338229184, 39.727419912, 4] | solid; strict interior/exterior | derived witness | Both flanks of a remote tooth on each gear, at the pitch radius, bracketed by +/-0.015 mm tangential offsets from the analytic flank. Tooth thickness is pi*gearModule/2 - totalBacklash/2 = 3.091592654 mm. Pinion tooth center 180 deg; wheel tooth center 94.5 deg. These reject an unthinned standard tooth; they do not directly measure circular backlash to 0.001 mm. |
| probes.involuteFlankSolid.1 | [-19.22913108, 1.579005686, 4] | solid; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankSolid.2 | [-19.22913108, -1.579005686, 4] | solid; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankSolid.3 | [-21.68822364, 0.714811393, 4] | solid; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankSolid.4 | [-21.68822364, -0.714811393, 4] | solid; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankSolid.5 | [58.873566574, 38.071044208, 4] | solid; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankSolid.6 | [55.156941727, 37.778539489, 4] | solid; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankSolid.7 | [57.481917782, 41.623902531, 4] | solid; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankSolid.8 | [55.975667522, 41.505358065, 4] | solid; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.pitchThicknessVoid.1 | [-19.939128773, 1.559212545, 4] | void; strict interior/exterior | derived witness | Both flanks of a remote tooth on each gear, at the pitch radius, bracketed by +/-0.015 mm tangential offsets from the analytic flank. Tooth thickness is pi*gearModule/2 - totalBacklash/2 = 3.091592654 mm. Pinion tooth center 180 deg; wheel tooth center 94.5 deg. These reject an unthinned standard tooth; they do not directly measure circular backlash to 0.001 mm. |
| probes.pitchThicknessVoid.2 | [-19.939128773, -1.559212545, 4] | void; strict interior/exterior | derived witness | Both flanks of a remote tooth on each gear, at the pitch radius, bracketed by +/-0.015 mm tangential offsets from the analytic flank. Tooth thickness is pi*gearModule/2 - totalBacklash/2 = 3.091592654 mm. Pinion tooth center 180 deg; wheel tooth center 94.5 deg. These reject an unthinned standard tooth; they do not directly measure circular backlash to 0.001 mm. |
| probes.pitchThicknessVoid.3 | [58.419615128, 39.968767602, 4] | void; strict interior/exterior | derived witness | Both flanks of a remote tooth on each gear, at the pitch radius, bracketed by +/-0.015 mm tangential offsets from the analytic flank. Tooth thickness is pi*gearModule/2 - totalBacklash/2 = 3.091592654 mm. Pinion tooth center 180 deg; wheel tooth center 94.5 deg. These reject an unthinned standard tooth; they do not directly measure circular backlash to 0.001 mm. |
| probes.pitchThicknessVoid.4 | [55.308434933, 39.723912411, 4] | void; strict interior/exterior | derived witness | Both flanks of a remote tooth on each gear, at the pitch radius, bracketed by +/-0.015 mm tangential offsets from the analytic flank. Tooth thickness is pi*gearModule/2 - totalBacklash/2 = 3.091592654 mm. Pinion tooth center 180 deg; wheel tooth center 94.5 deg. These reject an unthinned standard tooth; they do not directly measure circular backlash to 0.001 mm. |
| probes.involuteFlankVoid.1 | [-19.208002349, 1.818072275, 4] | void; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankVoid.2 | [-19.208002349, -1.818072275, 4] | void; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankVoid.3 | [-21.678991598, 0.95463254, 4] | void; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankVoid.4 | [-21.678991598, -0.95463254, 4] | void; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankVoid.5 | [59.113482367, 38.077386279, 4] | void; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankVoid.6 | [54.918987578, 37.747272379, 4] | void; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankVoid.7 | [57.721520193, 41.637705626, 4] | void; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| probes.involuteFlankVoid.8 | [55.736855734, 41.481509145, 4] | void; strict interior/exterior | derived witness | Both flanks at r=baseRadius+0.5 and r=tipRadius-0.3, bracketed by +/-0.12 mm tangential offsets. Derived from the 20 deg involute with zero profile shift. These sparse witnesses supplement, but cannot replace, the evaluator-only whole-profile p95 <= 0.10 mm comparison. |
| cylinder_counts.sixMillimeterHoles.diameter | 6 | radius +/-0.005 mm | stated | Hole kind; direction [0,0,1]; count by physical body even when coaxial. |
| cylinder_counts.sixMillimeterHoles.expected | 2 | exact | derived | One gear bore and one carrier hole of this diameter. |
| cylinder_counts.eightMillimeterHoles.diameter | 8 | radius +/-0.005 mm | stated | Hole kind; direction [0,0,1]; count by physical body even when coaxial. |
| cylinder_counts.eightMillimeterHoles.expected | 2 | exact | derived | One gear bore and one carrier hole of this diameter. |
| gears.pinionTeeth.solid / point / direction | pinion; [0, 0, 0]; [0, 0, 1] | axis in source frame | stated | Isolate the named gear body before taking the tooth-count section. |
| gears.pinionTeeth.at | 4 | mm along axis | derived | gearBaseZ+gearFaceWidth/2=4; same station as gearMidsection. |
| gears.pinionTeeth.module | 2 | mm; parameter tolerance 0.01 | stated | Common module; this field alone is not a full tooth-profile test. |
| gears.pinionTeeth.teeth | 20 | exact integer | stated | Source Pinion / Wheel rows; radial section runs count teeth, not outer loops. |
| gears.wheelTeeth.solid / point / direction | wheel; [60, 0, 0]; [0, 0, 1] | axis in source frame | stated | Isolate the named gear body before taking the tooth-count section. |
| gears.wheelTeeth.at | 4 | mm along axis | derived | gearBaseZ+gearFaceWidth/2=4; same station as gearMidsection. |
| gears.wheelTeeth.module | 2 | mm; parameter tolerance 0.01 | stated | Common module; this field alone is not a full tooth-profile test. |
| gears.wheelTeeth.teeth | 40 | exact integer | stated | Source Pinion / Wheel rows; radial section runs count teeth, not outer loops. |
| meshes.fullPitchMesh.a / b | pinion / wheel | named bodies | stated | Pinion drives wheel. |
| meshes.fullPitchMesh.axis_a | [[0, 0, 0], [0, 0, 1]] | mm origin; unit direction | stated | Axes at (0,0) and (60,0), parallel to +z; fixes center distance 60. |
| meshes.fullPitchMesh.axis_b | [[60, 0, 0], [0, 0, 1]] | mm origin; unit direction | stated | Axes at (0,0) and (60,0), parallel to +z; fixes center distance 60. |
| meshes.fullPitchMesh.ratio | 0.5 | dimensionless | derived | pinionTeeth/wheelTeeth=20/40; inspector applies the minus sign to the driven wheel rotation. |
| meshes.fullPitchMesh.pitch_deg | 18 | deg | derived | 360/pinionTeeth; wheel ends at -18*(20/40)=-9 deg. |
| meshes.fullPitchMesh.steps | 72 | intervals; 73 initial poses | defaulted | 0.25 deg pinion increments plus inspector refinement near its worst sampled pose; higher resolution than schema default 6. |
| meshes.fullPitchMesh.backlash_max | 0.15 | mm | stated | Motion row maximum closest-flank gap; distinct from 0.10 mm total circular backlash. |
| gears / probes descriptions: profile p95 limit | 0.1 | mm; evaluator-only | stated | Final source paragraph. Schema cannot perform this percentile without supplied reference geometry; recorded, not represented as a passing local check. |
| blockout.volume_min | 79362.75412533 | mm3 | derived / defaulted band | 0.95*Vblock; Vblock includes carrier and both full-height clipped gear envelopes, before bores/teeth. |
| blockout.volume_max | 87716.728243786 | mm3 | derived / defaulted band | 1.05*Vblock; envelope must also match each min/max coordinate to 0.05 mm. |
| export_volume_tolerance_rel | 0.002 | 0.2% | defaulted | Retain schema engine/STEP/STL volume-agreement threshold; separate from analytic root-model uncertainty. |
| deviation | null | not applicable locally | source availability | No mesh or ingested reference exists; never invent a reference or use evaluator-only geometry. |
| hardware | [] | no invented requirement | source availability | No purchased hardware, air passage, minimum-wall requirement, or specified inclined planar face appears in the source. Involute flanks are curved. |
| passages | [] | no invented requirement | source availability | No purchased hardware, air passage, minimum-wall requirement, or specified inclined planar face appears in the source. Involute flanks are curved. |
| thickness | [] | no invented requirement | source availability | No purchased hardware, air passage, minimum-wall requirement, or specified inclined planar face appears in the source. Involute flanks are curved. |
| planes | [] | no invented requirement | source availability | No purchased hardware, air passage, minimum-wall requirement, or specified inclined planar face appears in the source. Involute flanks are curved. |

The edit tests are analytic predictions, not executed CAD measurements:

| parameter change | expected volume_delta (mm3) | direction | expected bbox_delta (mm) | formula / safeguards |
|---|---|---|---|---|
| gearFaceWidth: 8 -> 10 | 12233.933119816 | increase | [0, 0, 2] | Delta V=2*(A20+A40). Sweep [6,8,10]; grow upward from z=0. Delta -8 produces zero face width and must fail a sanity assert. |
| totalBacklash: 0.10 -> 0.15 | -53.55 | decrease | [-0.00080288, -0.00160576, 0] | Delta V=-gearFaceWidth*Delta J*sum[N*(Ra^2-Rf^2)/(4*Rp)] = -53.55. Sweep [0.08,0.10,0.15]. Delta +6.5 gives J=6.6 and negative pitch tooth thickness; assert before constructing geometry. |

For the backlash edit, h0 and ha fall by Delta J/(4*Rp), so Hnew=42*cos(pi/40-ha40+Delta J/(4*40)). The bbox delta is [Hnew-H, 2*(Hnew-H), 0]. The volume formula is exact for the provisional radial-root construction; the 2% edit-delta band accommodates flank discretization, not an arbitrary topology change. A different root-transition construction must be reconciled with this expectation before claiming edit compliance. Face-width changes use the same existing profile, so their volume response is linear. The nominal parameters must remain editable: require positive widths, positive pitch and tip tooth thickness, valid bore/root containment, and integer tooth counts, without equality assertions locking dimensions to their seed values.

Pinned interfaces use the fixed carrier seating plane, carrier plan dimensions, carrier cylinder axes, gear bottom-face centroids and midsection topology. These remain invariant under both selected edits, within their explicit area bands. Top faces and gear-bore axial lengths are checked at the baseline and may follow gearFaceWidth; they are not pinned as constant axial extents in the edit tests. In the later model, all holes must remain through their respective bodies after regeneration.

## 6. Defaults retained

Length unit mm, angle unit deg, schema_version 1 and release_status reconstruction are retained. Material, density_kg_m3 and process remain null because the source gives none. No seed geometry or seed volume survives. Every digital threshold is explicit: stated length parameters generally 0.01 mm, pressure/phase 0.01 deg, integer/count and dimensionless factors 0.000001, backlash 0.001 mm, bbox 0.05 mm, planar location/centroid 0.02 mm, cylinder radius 0.005 mm, axis offset 0.01 mm, cylinder length 0.02 mm, seating-plane separation 0.01 mm. These are computational comparisons, not inferred manufacturing allowances.

The 0.2% engine/STEP/STL volume-agreement setting is retained from the schema. Numerical Boolean interference tolerance is 0.001 mm3; the nominal allowed overlap is zero. Mesh gap is the source's 0.15 mm limit, overriding the schema's looser default. Motion sampling is explicitly increased to 72 intervals plus available refinement. Blockout band width (+/-5%), analytic root-model quantity bands, probe guards, section stations, and edit-test sweeps are disclosed verification choices. No inferred physical dimension is added.

The carrier and both gears must remain separate at their z=0 contact, with no invented axial lift. Hole diameters remain Ø6 and Ø8 despite the source using the word clearance. No material assignment, mass, production process or fit class is implied.

## 7. Unrepresentable or low-confidence features

- Which below-base-circle root transition is intended: radial extension, generated trochoid, or a specified fillet? The root radii are stated, but the transition is not; gear volume, area, and surface estimates provisionally use sharp radial extensions, with no invented fillet radius.
- What material, density, manufacturing process, and production fit tolerances are intended? These are unspecified; material, density_kg_m3, and process remain null, and the stated Ø6/Ø8 carrier holes receive no added clearance allowance.
- How will the evaluator-only involute p95 <= 0.10 mm requirement be reported? No reference geometry is supplied and PartContract has no reference-free per-gear profile-deviation field; analytic probes cannot establish that percentile, so acceptance.deviation remains null.
- What evidence will certify zero interference between the sampled sweep poses? The required continuous full-pitch motion is retained, but the available inspector uses discrete poses with local refinement and a fixed 0.001 mm3 Boolean tolerance.

The schema's gear check counts teeth and its mesh check measures sampled minimum separation and interference. It has no direct pressure-angle fit, profile-shift fit, pitch-circle tooth-thickness measurement, or total circular-backlash scalar check; the stated parameter values, analytic boundary witnesses, envelope/area checks and motion checks collectively constrain those requirements. The 0.015 mm pitch witness brackets reject omitted thinning but do not certify circular backlash to its 0.001 mm parameter tolerance. The exact independent whole-profile p95 check belongs to the evaluator and remains outstanding. No deviation object is fabricated without reference geometry.

Likewise, the dimension schema measures bbox extents or named face separations, not distances between axes. The source center distance is therefore pinned by the four independently located cylinders and both mesh axes. The source describes curved involutes; faceted approximations do not create additional source-defined inclined mating planes. KCL single-file packaging, literal parameters, physical sanity asserts, exported solid validity and all CAD measurements remain for the modeling stage. No image evidence is missing: this is expressly a text-only source bundle.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-25.0, -41.9218, -5.0] → [101.9218, 41.9218, 8.0] | 83989.84504694387 | pass | 2026-09-18T23:53:41Z: within envelope and band |

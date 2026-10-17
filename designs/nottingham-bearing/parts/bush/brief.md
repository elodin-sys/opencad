# nottingham-bearing-bush — design brief

## 1. Intent and configuration

Stationary 180-degree half-journal bush of the University of Nottingham highly loaded half-journal bearing rig
(Layton et al. 2026, Lubricants 14(2) 76, section 2). EN24T steel, Ra 0.1 um bore. It is the body `bush` of the
assembly `nottingham-bearing`; its own frame is the assembly frame. The body is the half annulus
50.1 <= r <= 75, y <= 0, 0 <= z <= 75: a D100.2 bore about +z spanning 180 deg below the axis (inlet edge
t = -90 deg at x = -50.1, BDC at -y, outlet edge t = +90 deg at x = +50.1), split faces in y = 0, end faces z = 0
and z = 75, and an inferred D150 concentric outside. The bore is the outer wall of the oil film facing the D100.0
shaft journal across a 0.1 mm radial clearance. Pressure tappings and thermocouples are measurement locations only:
no holes, grooves, chamfers or feed ports; the inlet film generator is not modelled. `sources/bearing-packet.md` is
the only and authoritative source (text, no CAD, no drawing).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/bearing-packet.md | text | authoritative | 59abf634a3867c0c21ea6118b6bf08e72e4cfdfc5d0eb56ceacbfd8c8d944c4b | transcription of Layton et al. 2026 section 2; mm; no measured results |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| bore diameter | 100.2 | mm | packet, Unit under test | 0.01 (diameter) | stated |
| radial clearance to D100.0 shaft | 0.1 | mm | packet, Unit under test | - | stated (interface, shaft is a separate part) |
| bush length | 75 | mm | packet, Unit under test | 0.01 | stated |
| axial centreline | 37.5 | mm | packet, Unit under test | - | stated (datum D, journal joint point) |
| arc span, -90 to +90 deg through BDC | 180 | deg | packet, Unit under test and angle convention | 0.01 | stated |
| material EN24T, Ra 0.1 bore | - | - | packet, Unit under test | - | stated (non-geometric) |
| outside diameter | 150 | mm | user intent | 1.0 | inferred (open question) |
| pressure tappings t = -20, -45 deg at z = 18.5, 37.5, 56 | 6 stations | - | packet, Instrumentation | - | stated; solid probes, no holes |
| thermocouple row t = -85..+90 deg, 1 mm below the bore | row | - | packet, Instrumentation | - | stated; solid probes, no holes |
| no holes, grooves, chamfers or feed ports | 1 bore | - | user intent | - | stated; `boreCount`, solid probes |
| frame = assembly frame, journal joint [0, 0, 37.5] +z, oilFixed [0, 0, 0] +z | - | - | orchestrator notes | - | stated; interfaces `journalBore`, `filmEdges` |

## 4. Coordinate frame, scale, and measurement method

Origin on the bearing axis in the plane of the end face z = 0. +z along the bearing axis to the far end face
z = 75; +x horizontal toward the outlet edge; +y vertical from BDC toward the axis, so the material lies in y <= 0.
Angle t is measured from BDC (-y) positive toward +x; a bore point is (50.1 sin t, -50.1 cos t, z), and a positive
rotation of the shaft about +z moves its surface from the inlet edge through BDC to the outlet edge, matching the
packet's convention. Datums: A end face z = 0 (outward -z), B split plane y = 0 (outward +y), C bore axis, D axial
centreline z = 37.5. There are no images or reference models: every value is read from the packet text or derived
analytically, so no pixel scale or rectification applies. Probe coordinates are (r sin t, -r cos t, z).

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| boreDiameter | 100.2 mm | 0.01 | stated | packet: bush bore 100.2 mm, manufactured within 0.01 mm |
| outerDiameter | 150 mm | 1.0 | inferred | no outside dimension in the packet; intent's concentric D150, 24.9 mm wall |
| bushLength | 75 mm | 0.01 | stated | packet: bearing 75 mm long, centreline 37.5 mm |
| arcSpan | 180 deg | 0.01 | stated | packet: bush spans 180 deg, arc -90 to +90 deg from BDC |
| envelope | [-75, -75, 0] .. [75, 0, 75] | 0.05 | derived | x = +-outerDiameter/2, y = -outerDiameter/2..0, z = 0..bushLength |
| volume | 366976.1 mm3 | rel 0.002 | derived | (pi/2)(75^2 - 50.1^2)(75) = 4893.015 * 75 |
| surface area | 42997.0 mm2 | rel 0.005 | derived | pi*50.1*75 + pi*75*75 + 2*4893.015 + 2*24.9*75 = 11804.5 + 17671.5 + 9786.0 + 3735 |
| centre of mass | [0, -40.346, 37.5] | 0.05 | derived | y = -(4/(3 pi))(75^3 - 50.1^3)/(75^2 - 50.1^2); x, z by symmetry |
| section midZ (z = 37.5) | 4893.0 mm2, 1 loop, 0 holes | rel 0.005 | derived | (pi/2)(75^2 - 50.1^2) |
| section bdcX (x = 0) | 1867.5 mm2, 1 loop | rel 0.005 | derived | 24.9 * 75 |
| section tapY (y = -20) | 3952.4 mm2, 2 loops | rel 0.005 | derived | 2 (sqrt(75^2 - 400) - sqrt(50.1^2 - 400)) 75 = 2 * 26.349 * 75 |
| faces endBack | 4893.0 mm2 at (0, -40.346) | rel 0.005 | derived | half-annulus area and centroid; endFront (datum A) is checked by position only |
| faces splitInlet / splitOutlet | 1867.5 mm2 at (-+62.55, 37.5) | rel 0.005 | derived | (75 - 50.1) * 75; centre x = (50.1 + 75)/2 |
| dimensions length / spanX / spanY | 75 / 150 / 75 | 0.02 / 0.1 / 0.1 | derived | bushLength; outerDiameter; outerDiameter/2 |
| probes | see contract | >= 1 mm | derived | wall r = 62.55; tappings r = 55 (4.9 mm inside the bore); thermocouples r = 51.1; voids r <= 49 or y >= 5 |
| edit outerDiameter +10 | dV = +91302.5 mm3, bbox [10, 5, 0] | rel 0.02 | derived | (pi/2)(80^2 - 75^2)(75) |
| edit bushLength +5 | dV = +24465.1 mm3, bbox [0, 0, 5] | rel 0.02 | derived | 4893.015 * 5 |
| blockout band | 355000 .. 380000 mm3 | - | derived | the half annulus itself (366976) reaches every envelope extreme; band -3.3 % / +3.5 % |

Feasible intervals: outerDiameter > boreDiameter (sweep 120, 150, 180; infeasible delta -50 gives D100 < D100.2,
the model must assert); bushLength > 0 (sweep 50, 75, 100; infeasible delta -75 gives zero length, the model must
assert). The bore, split plane and end face z = 0 are pinned by the interfaces; neither edit moves them.

## 6. Defaults retained

- Density 7850 kg/m3: handbook value for EN24T (817M40); the packet states the material but not its density. It only
  affects mass reports, not any interface.
- Envelope tolerance 0.05 mm and symmetry bands 0.1 / 0.05 mm are the pipeline defaults; the bore keeps the stated
  0.01 mm diameter tolerance (radius 0.005).
- Blockout: the half annulus is the primary solid (the bore does not change the bounding box, but a solid half
  cylinder would be 662680 mm3, 1.8x the part), so the blockout band is centred on the finished volume.

## 7. Unrepresentable or low-confidence features

- Outside diameter (D150) is inferred; the packet gives no outside dimension, housing, anti-rotation or mounting
  features, so none are modelled.
- Pressure tappings, thermocouples and the inlet film generator are not geometry here; the tappings and the
  thermocouple row are probed as solid material. The +90 deg thermocouple lies in the split plane y = 0 and is not
  probed.
- Surface finish (Ra 0.1 um) and the 0.01 mm manufacturing tolerance are not representable in the B-rep beyond the
  bore radius tolerance.
- The tapping stations (z = 18.5, 37.5, 56) are not symmetric about z = 37.5; they do not affect the modelled geometry.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|

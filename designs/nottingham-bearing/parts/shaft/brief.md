# nottingham-bearing-shaft — design brief

## 1. Intent and configuration

Instrumented EN24T steel shaft (Ra 0.1 um) of the University of Nottingham highly loaded half-journal bearing rig, body `shaft` of the assembly `nottingham-bearing`. It is drafted in its own frame: rotation axis +z through the origin, origin at mid-length, mid-way between the two supporting cylindrical roller bearings (230 mm apart) and on the bush axial centreline at rest. The geometry is a plain D100.0 solid cylinder (radius 50.0, diameter tolerance 0.01) from z = -115 to z = +115; bearing seats, shoulders, the drive end, keyways, pockets, holes and the ultrasonic film sensors are not modelled. The journal band z = -37.5..+37.5 runs concentrically in the D100.2 bush bore with a 0.1 mm radial clearance and is the inner, moving wall of the oil film; the end faces are the support-bearing stations. The assembly attaches the shaft with the revolute joint `journal` at [0, 0, 0] about +z. The only and authoritative source is the text packet `sources/bearing-packet.md` (Layton et al. 2026, Lubricants 14(2) 76, section 2); there is no CAD, drawing or image, so the reference geometry is the stated dimensions.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/bearing-packet.md | text | authoritative | 59abf634a3867c0c21ea6118b6bf08e72e4cfdfc5d0eb56ceacbfd8c8d944c4b | Section 2 (experimental method) transcription: shaft D100.0, bush bore D100.2 (100 um radial clearance), both within 0.01 mm, EN24T Ra 0.1, bearings 230 mm apart, bush 75 mm long with its axial centreline at 37.5 mm, sensors listed without positions on the shaft |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| shaft (journal) diameter | 100.0 | mm | packet, Unit under test; intent | +-0.01 on diameter (radius +-0.005) | stated |
| shaft radius | 50.0 | mm | intent (shaftDiameter / 2) | +-0.005 | stated |
| modelled length = support span | 230 (z = -115..+115) | mm | packet "two cylindrical roller bearings 230 mm apart"; intent | 0.01 digital | stated |
| rotation axis | +z through the origin, positive rotation about +z | - | intent; assembly joint `journal` at [0, 0, 0] axis [0, 0, 1] | axis offset 0.01 | stated |
| origin | mid-length, mid-way between the bearings, on the bush axial centreline at rest | - | intent | COM 0.01; symmetry 0.1 / 0.05 | stated |
| journal band (interface only) | z = -37.5..+37.5 (bush 75 long) | mm | packet "bush is 75 mm long, axial centreline at 37.5"; intent | - | stated, not a separate face |
| radial clearance to the D100.2 bush bore | 0.1 | mm | packet; intent | assembly level | stated, not checked by this part |
| support-bearing stations | end faces z = -115 and z = +115 | mm | intent | 0.05 | stated |
| no keyways, pockets or holes | - | - | intent | sections, probes | stated |
| material | EN24T steel, Ra 0.1 um | - | packet | - | stated (finish is non-geometric) |
| density | 7850 | kg/m3 | EN24T handbook value | - | defaulted |
| bearing seats, shoulders, drive end | not stated | - | - | - | open |
| sensor / thermocouple / magnetic ring positions on the shaft | not stated | - | - | - | open |

## 4. Coordinate frame, scale, and measurement method

The frame is the one the intent and the assembly joint define: the origin is on the shaft axis at mid-length, mid-way between the support stations and on the bush axial centreline at rest; +z runs along the rotation axis from the -z station (z = -115) to the +z station (z = +115) and the shaft turns positively about +z. +x is a radial direction fixed in the shaft and +y = z cross x; the part is axisymmetric, so the angular zero of x has no geometric effect (the joint's zero angle defines it). Datums: A the z axis (journal cylinder axis), B the mid-span plane z = 0, C the end face z = -115, D the end face z = +115.

There are no images, drawings or meshes. Every dimension is quoted from the text packet or the intent; nothing was scaled or measured from pixels. The envelope follows directly: x and y in +-shaftDiameter/2 = +-50, z in +-shaftLength/2 = +-115.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| shaftDiameter | 100.0 mm | 0.01 | stated | packet: shaft diameter 100.0 mm, manufactured within 0.01 mm; intent D100.0 |
| shaftLength | 230 mm | 0.01 | stated | packet: bearings 230 mm apart; intent: z = -115..+115, length = support span |
| envelope | [-50, -50, -115]..[50, 50, 115] | 0.05 | derived | +-shaftDiameter/2 in x and y, +-shaftLength/2 in z |
| volume | 1806415.78 mm3 | rel 0.001 | derived | pi * 50^2 * 230 = 575000 pi |
| surface_area | 87964.59 mm2 | rel 0.002 | derived | lateral pi * 100 * 230 = 72256.63 plus two ends 2 * pi * 50^2 = 15707.96; total 28000 pi |
| center_of_mass | [0, 0, 0] | 0.01 | derived | axisymmetric about z, mirror-symmetric about z = 0 |
| sections mid, stationMinus, stationPlus (z = 0, -110, +110) | 7853.98 mm2, 1 loop, 0 holes | default rel | derived | pi * 50^2; solid disc, no bore, no seat or shoulder near the stations |
| sections axialX, axialY (x = 0, y = 0) | 23000 mm2, 1 loop, 0 holes | default rel | derived | shaftDiameter * shaftLength = 100 * 230; no cross holes |
| faces endMinus / endPlus | z = -115 (normal -) / z = +115 (normal +), 7853.98 mm2, centre [0, 0] | plane 0.05 | derived | pi * 50^2 at -+shaftLength/2 |
| cylinder journal | pin, D100.0, point [0, 0, 0], direction [0, 0, 1] | radius 0.005, axis 0.01 | stated | radius tolerance = half the 0.01 diameter tolerance; axis tolerance kept well below the 0.1 mm film clearance |
| dimension supportSpan | 230 between endMinus and endPlus | 0.05 | stated | support span |
| symmetry midSpan | plane z = 0 | max 0.1, p95 0.05 | derived | origin at mid-length between the stations |
| probes inShaft (solid) | axis at z = 0, +-114; 1 mm under the surface at z = 0, +-37 | - | derived | 1 mm inside every face; material under the journal band and no centre holes |
| probes outsideShaft (void) | r = 52 at z = 0, +-100; z = +-117 on the axis | - | derived | 2 mm outside every face (rule minimum 1 mm) |
| blockout band | 1750000..1860000 mm3 | - | derived | the blockout is the cylinder itself (1806416); band -3.1 % / +3.0 % |
| edit test shaftLength +10 | volume +78539.82, bbox [0, 0, +10], increase | rel 0.01 | derived | pi * 50^2 * 10 = 25000 pi; extension symmetric about z = 0 (ends at +-120) |
| sweep shaftLength | 200, 230, 260 | - | derived | feasible interval shaftLength >= 75 (the journal band z = -37.5..+37.5 must stay on the shaft); all values rebuild the journal axis, D100.0 and the mid-span plane |
| infeasible delta shaftLength -240 | length -10 | - | derived | a non-positive length is impossible; the model must refuse it with `assert shaftLength > 0` |
| density_kg_m3 | 7850 | - | defaulted | handbook density of EN24T (817M40T); not in the packet |

The diameter carries no edit test: it is the stated, toleranced journal interface (0.1 mm film clearance to the D100.2 bore), so the interface `journalSurface` pins the `journal` cylinder and the `midSpan` plane, neither of which the length edit moves. The interface `supportStations` pins only `midSpan`, because the length edit moves both end faces symmetrically.

## 6. Defaults retained

- Envelope tolerance 0.05 mm (template default): the STEP bounding box of a cylinder is exact, the value stays well below the 0.1 mm film clearance, and the D100.0 is held tighter by the `journal` cylinder check (radius +-0.005, axis 0.01).
- Symmetry bands max 0.1 / p95 0.05 mm (exemplar defaults); no source states a tighter band.
- Density 7850 kg/m3, the handbook value for EN24T; only needed for mass or inertia claims downstream.
- Sharp end-face edges: no chamfer or edge break is stated.
- `release_status: reconstruction`: rebuilt from a published text description, not from CAD.

## 7. Unrepresentable or low-confidence features

- Bearing seats, shoulders, the drive end or coupling, and the shaft length beyond the support bearings are not stated; the real shaft certainly extends past the stations, but the intent models only the support span.
- The two ultrasonic film sensors, the thermocouples 1 mm below the shaft surface and the RLS MR050E magnetic ring are listed without positions; no pockets or holes are modelled.
- The Ra 0.1 um surface finish is non-geometric and is recorded only as material data.
- The packet does not state that the bush sits mid-way between the support bearings; the intent places the bush axial centreline at the mid-span origin, so the journal band z = -37.5..+37.5 is an intent value.
- The 230 mm support span is read as bearing centre to bearing centre and the stations are modelled as the end faces; bearing widths are not stated.
- "Within a tolerance of 0.01 mm" is read as +-0.01 on the diameter; a total band would halve the radius tolerance.
- The journal band is not a separate face on a plain cylinder; it is pinned only through the whole D100.0 cylinder.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|

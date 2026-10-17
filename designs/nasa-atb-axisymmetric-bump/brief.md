# nasa-atb-axisymmetric-bump — design brief

## 1. Intent and configuration

User intent, verbatim:

> Reconstruct the Bachalo-Johnson axisymmetric transonic bump as ONE solid of revolution for a CFD outer-mould line. The attached spec is inch-native (cylinder diameter 6 in, bump chord 8 in, bump height 3/4 in); convert to millimetres. Frame: +x along the cylinder axis with the bump chord occupying x = 0 to x = c, origin on the axis. Revolve the meridian a full 360 degrees. The bump is a circular arc of radius R1 = 0.5 (t^2 + 0.25 c^2) / t; blend it to the upstream cylinder with a leading-edge fillet R2. The references list R2 as 18.30 cm (use 183.0 mm) with 20.32 cm as a documented alternate (open question, inferred). No trailing-edge fillet. Axial extent is the x-range of the attached surface-point file (nondimensional by the 8 in chord; multiply by 8 inches to get millimetres). Name the two planar end caps. Expose cylinderDiameter, bumpChord, bumpHeight and filletRadius. One solid; export STEP and STL.

The construction is analytic: a cylinder, a tangent leading circular blend, and a circular-arc bump, closed to the axis and revolved once through 360 deg. The source table establishes the axial extent. Its intermediate samples are approximate checks and do not override the specified sharp trailing join. The later deliverable is one filled solid with named `upstreamCap` and `downstreamCap` planar faces, exported as STEP and STL. This bundle defines intent and checks; no CAD model or export has been made at this stage.

Expose six independent literal constants: `cylinderDiameter`, `bumpChord`, `bumpHeight`, `filletRadius`, `upstreamX`, and `downstreamX`. Compute the main circle radius, maximum radius, arc centers and tangencies from these constants so edits propagate. The table is not imported or interpolated as the construction, and the 1550.010233984 mm ingest endpoint span must never replace the 203.2 mm bump chord.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| `sources/nasa-atb-bump-spec.md` | text | authoritative | `f773288693cfbcd96bc113422d051fd3f47b86791ad0c254f7c704e99ce86165` | Unversioned supplied snapshot. Inch-native diameter/chord/height; cm-native R2 alternatives. Governs analytic geometry, frame and sharp trailing join. |
| `sources/bumpgrd.surfpts_orig.dat` | table | authoritative | `46f028810ad0e6e68e20520452edb44c2dfe77b42ceefa59229733d92bb15b1f` | Supplied `surfpts_orig` snapshot; header explicitly says approximate. 181 open `(x/c,r/c)` samples with c = 203.2 mm. Authority covers scale and axial limits; interior samples are subordinate to the written geometry. |
| `reference/profile.json` | reference-model | authoritative | `32b04d48e80559b1e61f02b364213768d9fdee0f03423e0b29ee5bb8ca900b1c` | Generated 2026-09-16T09:36:55Z. Authority covers measured axial limits. `points_mm` and measurements already include the 203.2 conversion. No mesh or suggested tolerance band is present. |
| `reference/profile.png` | image | illustrative | `4a9d293999dd4fa5f207270b279a6237aa144e62610cd43bee6d6b48e9a67f91` | Companion 900 by 70 pixel plot from the same ingest. Shows one bump between straight cylinder runs; no annotated dimensions. |

All four files were read and their complete SHA-256 values computed. The supplied specification cites NASA's ATB resource and Bachalo and Johnson, AIAA Journal 24(3), 1986, pp. 437–443. Those citations are background to the supplied specification, not additional files or independently verified revisions.

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| Cylinder diameter | 6 in = 152.4 | mm | Specification, Geometry | ±0.01 | stated |
| Bump chord | 8 in = 203.2, from x = 0 to x = 203.2 | mm | Specification, Geometry and Frame | ±0.01 | stated |
| Bump radial rise | 3/4 in = 19.05 | mm | Specification, Geometry | ±0.01 | stated |
| Main arc radius | 280.458333333333 | mm | R1 = `(t²+c²/4)/(2t)` | Computed from parameters; sections checked at 0.1% area | derived |
| Leading-edge blend | Circular, tangent at both ends; R2 = 183.0 | mm | Specification selects 18.30 cm | ±1.0 digital radius tolerance on selected nominal | inferred; 203.2 mm alternate open |
| Trailing edge | Sharp arc-to-cylinder join at x = 203.2, no fillet | mm | Specification and user intent | Sections at x = 202 and 204, ±0.1% area | stated; conflicting table smoothing documented |
| Upstream limit | -650.0073203536 | mm | `profile.json`, `measurements.bbox_min[0]` | ±0.01 | measured (reference model) |
| Downstream limit | 900.0029136304 | mm | `profile.json`, `measurements.bbox_max[0]` | ±0.01 | measured (reference model) |
| Revolution | Full 360 about +x, closed to the axis | deg | Specification, Frame | Exact full revolution/topology | stated |
| Body count and cavities | 1 connected filled solid; no holes or cavities | count | User intent/specification | Exact topology; sections have 1 outer loop, 0 holes | stated |
| Cap names | `upstreamCap` and `downstreamCap` | names | User request to name both ends; names assigned in this contract | One face per end, ±0.01 mm plane position, ±0.1% area | required; naming convention selected |
| Exposed controls | Four requested dimensions plus both axial limits | identifiers | Specification, Parameters to expose | Exact identifiers and nominal literals | stated |
| Edit checks | Height +1 mm and diameter +2 mm, independently | mm | Orchestrator requirement; magnitudes selected for a measurable signal | ±0.2% volume delta; ±0.05 mm bbox size delta | required; analytic effects below |
| Export formats | STEP and STL of the same solid, in mm | formats | User intent | Cross-format volume agreement 0.2%; STL local tessellation unresolved | required |

## 4. Coordinate frame, scale, and measurement method

The origin is on the cylinder axis at the nominal, unfilleted leading-edge plane x = 0. The x-axis points downstream along the table's X direction. In the meridian plane z = 0, positive y is the outward radius represented by the table's Y column. Set +z = +x cross +y for a right-handed frame; azimuth is arbitrary because the body is rotationally symmetric. The axis datum is y = z = 0. The chord datums are x = 0 and x = 203.2 mm. The end-cap datums are x = -650.0073203536 mm (normal -x) and x = 900.0029136304 mm (normal +x). No recentering is permitted.

Use the exact unit conversion 1 in = 25.4 mm. For the raw table, multiply **both** columns by the fixed original 8 in chord, 203.2 mm: `x = 203.2*(x/c)` and `r = 203.2*(r/c)`. Thus the cylinder row value 0.375 is radius 76.2 mm, not diameter. All 181 numeric rows were parsed after the two comment lines and the `VARIABLES` header; every scaled coordinate equals the corresponding `profile.json.points_mm` entry within floating-point roundoff (observed maximum difference 0.0 mm). The raw minimum and maximum x/c are -3.198854923 and 4.429148197. Hold their converted mm coordinates fixed when editing height or diameter.

The ingest's `source.declared_units: mm` does not describe the raw nondimensional columns; `source.scale_to_mm: 203.2` was already applied. Never scale `points_mm` twice. The ingest labels the full endpoint span 1550.010233984 mm as `chord` and `landmark_chord`; neither is the physical bump chord. The input is open. Its generic polygon summary closes the meridian along the cylinder-radius baseline, so `area = 2643.901328066364 mm²` is an approximate excess-profile area, not a full axial material section. Its polygon centroid, perimeter and binned `max_thickness = 17.26960360144 mm` are likewise not the three-dimensional centroid, surface area or authoritative 19.05 mm bump height.

There are no attached dimensioned drawings. The illustrative plot was viewed and inspected without deriving dimensions from it. Using zero-based image coordinates, dark or grey pixels (minimum RGB channel < 240) occupy x = 28–872 and y = 27–42; the cylinder baseline is near y = 40, and the topmost marked crown pixels span x = 431–446 at y = 27. Marker size and line width consume several pixels of the roughly ten-pixel rise. The plot contains one raised meridian and long straight runs on both sides, with no dimension lines. Scale comes exclusively from the table's numeric normalization; no parameter has image-measured provenance or an invented pixel precision.

## 5. Measurement and inference record

Digital tolerances compare the selected nominal reconstruction; they are not manufacturing tolerances or confidence intervals for historical dimensions. `profile.json` supplies no recommended comparison tolerances, so its endpoint tolerances are explicitly chosen as ±0.01 mm, much wider than the input decimal rounding. The inferred radius gets ±1 mm, 100 times the stated-dimension digital tolerances. The discrete 203.2 mm alternative is not absorbed into acceptance of a different shape: nominal analytical checks remain tied to the instructed 183.0 mm choice.

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| `cylinderDiameter` | 152.4 mm | ±0.01 mm | stated | Specification: “Cylinder diameter d = 6 inches.” Multiply by 25.4. |
| `bumpChord` | 203.2 mm | ±0.01 mm | stated | Specification: “Bump chord c = 8 inches”. Multiply by 25.4; independent of total table span. |
| `bumpHeight` | 19.05 mm | ±0.01 mm | stated | Specification: “Bump height t = 3/4 inch above the cylinder radius.” Multiply by 25.4. |
| `filletRadius` | 183.0 mm | ±1.0 mm | inferred | Directed selection of 18.30 cm over the documented 20.32 cm alternate; wider digital tolerance records lower confidence. |
| `upstreamX` | -650.0073203536 mm | ±0.01 mm | measured (reference model) | `profile.json.measurements.bbox_min[0]`; raw minimum -3.198854923 times 203.2. |
| `downstreamX` | 900.0029136304 mm | ±0.01 mm | measured (reference model) | `profile.json.measurements.bbox_max[0]`; raw maximum 4.429148197 times 203.2. |

Parameter count: **6 total — 3 stated, 2 measured (reference model), 1 inferred**. There are no independently editable derived constants. Auxiliary geometry below must be recomputed from the six controls, including during the two edit tests.

For the formulas, let `r = cylinderDiameter/2`, `c = bumpChord`, `t = bumpHeight`, `f = filletRadius`, `u = upstreamX`, and `v = downstreamX`. Define:

```text
R = (t² + c²/4)/(2t)                 = 280.458333333333 mm
h = c/2                              = 101.6 mm
b = r+t-R                            = -185.208333333333 mm
d = sqrt(2(R+f)t-t²)
a = h-d                              = -29.909923579934 mm
j = a+f*d/(R+f)                       = 22.017756395169 mm
rho(j) = r+f*t/(R+f)                  = 83.722035422098 mm

rho(x) = r                            for u <= x <= a
         r+f-sqrt(f²-(x-a)²)          for a <= x <= j
         b+sqrt(R²-(x-h)²)            for j <= x <= c
         r                            for c <= x <= v
```

The leading blend circle has center `(a,r+f)` and radius f. It is externally tangent to the main circle with center `(h,b)` and radius R; the center distance is R+f. Its lower branch connects the cylinder tangentially at `(a,r)` to the main circle's upper branch at `(j,rho(j))`. Close the positive-radius meridian to `(v,0)` and `(u,0)` and revolve around x. The maximum radius r+t occurs at x = h. At x = c the left-hand slope is `-h/(R-t) = -0.388663967611`; the downstream cylinder slope is zero. Preserve that slope discontinuity.

The acceptance formulas are `V = pi*integral(rho² dx)`, `S = 2*pi*integral(rho*sqrt(1+rho'²) dx)+2*pi*r²`, `xbar = pi*integral(x*rho² dx)/V`, and `A_meridian = 2*integral(rho dx)`, each integrated from u to v across the four separate intervals. The cap term in S includes both ends. A uniform density cancels in the centroid; no mass is asserted.

For reproducible closed-form evaluation on either curved interval, write `rho = k+s*sqrt(q²-w²)` with `w=x-p`. The leading blend has `(p,k,q,s)=(a,r+f,f,-1)`; the bump arc has `(h,b,R,+1)`. With `H(w)=(w*sqrt(q²-w²)+q²*asin(w/q))/2`, antiderivatives are:

```text
I1 = integral(rho dx)    = k*w+s*H(w)
I2 = integral(rho² dx)   = (k²+q²)*w-w³/3+2*s*k*H(w)
Ix = integral(x*rho² dx)
   = (k²+q²)*w²/2-w⁴/4-(2*s*k/3)*(q²-w²)^(3/2)+p*I2
Is = integral(rho*sqrt(1+rho'²) dx)
   = q*(k*asin(w/q)+s*w)
```

Use radians for these analytic inverse-trigonometric evaluations; later CAD angular literals remain in degrees. Add the constant-radius cylinder integrals on `[u,a]` and `[c,v]`. Independent SciPy quadrature agrees with the antiderivatives to less than 0.000001 mm³ in volume, 0.000001 mm² in area and 0.000000001 mm in centroid for the nominal and both edited configurations.

| acceptance value | nominal expectation | tolerance / comparison | provenance and formula / evidence |
|---|---|---|---|
| `envelope.min` | [-650.0073203536, -95.25, -95.25] mm | ±0.05 mm per axis | Derived: `[u,-(r+t),-(r+t)]`; x endpoint measured from ingest. |
| `envelope.max` | [900.0029136304, 95.25, 95.25] mm | ±0.05 mm per axis | Derived: `[v,r+t,r+t]`. |
| Bounding-box size | [1550.010233984, 190.5, 190.5] mm | `acceptance.bbox_tolerance = 0.05 mm` | Derived: `[v-u,2(r+t),2(r+t)]`. |
| `volume` | 29664257.630154 mm³ | Relative 0.001 (0.1%) | Derived: V above, including filled cylinder and blend. |
| `surface_area` | 797417.539677 mm² | Relative 0.001 (0.1%) | Derived: S above, including both caps. |
| `center_of_mass` | [123.829056217831, 0, 0] mm | ±0.05 mm per axis | Derived: xbar above; y and z vanish by revolution symmetry. |
| `solid_count` | 1 | Exact integer | Stated one-solid requirement. |
| Section `upstreamCylinder`, x = -400 mm | 18241.469247510 mm²; 1 loop, 0 holes | Area relative 0.001; topology exact | Derived: `pi*r²`. |
| Section `leadingBlendUpstream`, x = -10 mm | 18765.272872550 mm²; 1 loop, 0 holes | Area relative 0.001; topology exact | Derived: `pi*rho(-10)²`, rho = 77.286298088788 mm. |
| Section `leadingChord`, x = 0 mm | 19438.680527848 mm²; 1 loop, 0 holes | Area relative 0.001; topology exact | Derived: `pi*rho(0)²`, rho = 78.660817351350 mm. |
| Section `forwardArc`, x = 50 mm | 25709.015640963 mm²; 1 loop, 0 holes | Area relative 0.001; topology exact | Derived: `pi*rho(50)²`, rho = 90.462333833326 mm. |
| Section `bumpCrown`, x = 101.6 mm | 28502.295699234 mm²; 1 loop, 0 holes | Area relative 0.001; topology exact | Derived: `pi*(r+t)²`. |
| Section `beforeTrailingJoin`, x = 202 mm | 18463.929012381 mm²; 1 loop, 0 holes | Area relative 0.001; topology exact | Derived: `pi*rho(202)²`, rho = 76.663232011419 mm. |
| Section `afterTrailingJoin`, x = 204 mm | 18241.469247510 mm²; 1 loop, 0 holes | Area relative 0.001; topology exact | Derived: `pi*r²`; local check against unintended trailing smoothing. |
| Section `downstreamCylinder`, x = 400 mm | 18241.469247510 mm²; 1 loop, 0 holes | Area relative 0.001; topology exact | Derived: `pi*r²`. |
| Section `axialMeridian`, z = 0 mm | 241504.064289478 mm²; 1 loop, 0 holes | Area relative 0.001; topology exact | Derived: `2*integral(rho dx)` across the complete filled section. |
| Face `upstreamCap` | x = -650.0073203536 mm; normal -x; area 18241.469247510 mm²; in-plane center (y,z) = (0,0) | Plane ±0.01 mm; area relative 0.001; `mode: one` | Derived planar disk at u with area `pi*r²`; name selected to satisfy the cap requirement. |
| Face `downstreamCap` | x = 900.0029136304 mm; normal +x; area 18241.469247510 mm²; in-plane center (y,z) = (0,0) | Plane ±0.01 mm; area relative 0.001; `mode: one` | Derived planar disk at v with area `pi*r²`. |
| `blockout.volume_min` | 30605031.757600 mm³ | Inclusive lower bound | Derived: `0.998*V_blockout`; envelope-only primary solids described below. |
| `blockout.volume_max` | 30727697.215547 mm³ | Inclusive upper bound | Derived: `1.002*V_blockout`, rounded outward. |
| `deviation` | null | Not applicable | There is a coordinate table, but no reference surface mesh or suggested mesh-distance band. |
| `export_volume_tolerance_rel` | 0.002 | 0.2% cross-format volume difference | Retained schema default for later KCL/STEP/STL agreement; not a substitute for STL surface accuracy. |
| Height edit: `bumpHeight += 1.0 mm` | V = 29747061.670930 mm³; delta = +82804.040776 mm³; bbox-size delta [0,2,2] mm | Delta relative 0.002; increase; bbox ±0.05 mm | Derived: `V(r,c,t+1,f,u,v)-V(r,c,t,f,u,v)` with R, a and j recomputed. |
| Diameter edit: `cylinderDiameter += 2.0 mm` | V = 30427834.525102 mm³; delta = +763576.894948 mm³; bbox-size delta [0,2,2] mm | Delta relative 0.002; increase; bbox ±0.05 mm | Derived: radial offset dr = 1 mm gives `pi*(2*dr*integral(rho dx)+dr²*(v-u))`. |

The envelope-only blockout is the union of a radius-r cylinder from u to v and a radius-(r+t) coaxial collar spanning **a to c**, including the negative-x leading-blend envelope. Subtract the overlapped cylinder volume once: `V_blockout = pi*r²*(v-u)+pi*((r+t)²-r²)*(c-a) = 30666364.486573 mm³`. Its acceptance band is ±0.2%. This is a construction checkpoint, distinct from the final curved-solid volume. The stepped blockout can be one revolved profile; no imported shape is needed.

The edit tests are independent, always starting from the nominal configuration. Increasing t leaves c, r, f, u and v fixed and changes both circle geometry and tangent locations. Increasing diameter by 2 mm raises rho everywhere by 1 mm while t, c, f, u and v stay fixed; `integral(rho dx)=120752.032144739 mm²` and `v-u=1550.010233984 mm` give its delta directly. Neither test edits an ingest-derived chord or rescales the table. All edited configurations must still be a single solid.

Solid probes lie safely inside the body. At the inferred blend, `(10,78,0)` has radius below `rho(10)=80.604932879310 mm`; its shortest distance to the blend circle is 2.543100114653 mm, exceeding the 1 mm inferred-radius digital tolerance. Crown probes in four radial directions are 5.25 mm below the outer surface; the other probes are at least 6.2 mm inside the nearest exposed surface. There are no hole/cavity probes because no void features are required. The nine sections check filled disks, the blend, the bump, the sharp join and the connected axial material section.

## 6. Defaults retained

Length and angle units are mm and deg. `release_status: reconstruction` is appropriate for a source-based geometry reconstruction. `material` and `density_kg_m3` remain null because this is a CFD outer-mould line; no mass or material-dependent performance is claimed. The process field records the reconstruction purpose without inventing a manufacturing process.

The template's 0.05 mm envelope/centroid comparison tolerance is retained as a digital validation threshold. The schema's 0.002 export-volume comparison tolerance is retained, and independently selected as the edit-delta and blockout relative bands. Section and final volume/surface-area tolerances are explicitly set to 0.001, so local feature checks are tighter than the generic template. Parameter and cap-plane tolerances are specified separately above. These are validation settings, not additional geometric dimensions.

The solid count remains one because the user requires it. `interfaces` stays empty because no assembly mating interface is specified; downstream cap identities are fully represented by named face requirements. `deviation` remains null because there is no reference mesh. The inherited plate envelope, plate dimensions, blank feature, volume, section and blockout numbers have all been replaced. No invented material, wall thickness, bore, machining allowance or cosmetic feature is introduced.

## 7. Unrepresentable or low-confidence features

The supplied table differs from the requested analytic construction. At x = 202.25304955456 mm it reports r = 76.92656053824 mm versus analytic r = 76.5660740320132 mm, a 0.360486506227 mm radial difference. At x = 205.1139334848 mm, already downstream of c, it remains 0.238720884 mm above the cylinder. These samples indicate trailing smoothing and are deliberately not fitted because the written requirement specifies no trailing fillet. In the leading-blend region, the largest sampled difference from the selected analytic profile is approximately 0.027850 mm. The sampled maximum radius, 95.24992128032 mm, is only 0.00007871968 mm below the exact 95.25 mm crown because the table does not sample x = c/2 exactly.

The table's baseline-closed excess area is 2643.901328066364 mm², while the selected analytic excess area `integral(rho-r dx)` is 2641.252315157959 mm². This is another check that blindly revolving the ingested polygon would describe a different object. The contract instead closes the specified analytic exterior to the axis.

The schema represents sections, filled points and named planar faces, but has no direct G1-tangency, curve-radius or sharp-edge-angle acceptance probe. Those properties are explicit feature requirements with analytic construction formulas; the local sections support them but do not by themselves prove exact continuity. Later CAD inspection must review the circular tangencies and the sharp trailing edge. No geometric feature is marked cosmetic or optional.

The following unresolved questions are also recorded in `contract.yaml`:

1. Which historical leading-edge radius is correct: 18.30 cm (183.0 mm) or the documented alternate 20.32 cm (203.2 mm)? This contract fixes the instructed inferred nominal at 183.0 mm; 203.2 mm is an unbuilt alternate.
2. What accounts for the approximate coordinate table's trailing-edge smoothing and small leading-blend differences from the specified analytic profile? The active contract uses its axial limits but retains the explicitly required sharp trailing join; it does not interpolate the rounded samples.
3. What chordal and angular tessellation tolerances does the downstream CFD workflow require for STL? No values were supplied; the retained 0.2 percent cross-format volume check alone does not establish local surface accuracy.

This stage verifies the bundle and analytic expectations only. CAD execution, engine measurements, actual face naming, blockout geometry, STEP topology and STL accuracy remain for the modeling and export stages. No blockout checkpoint has been performed, so the log below is intentionally empty.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-650.0073, -95.25, -95.25] → [900.0029, 95.25, 95.25] | 30666364.377166126 | pass | 2026-09-16T10:03:51Z: within envelope and band |

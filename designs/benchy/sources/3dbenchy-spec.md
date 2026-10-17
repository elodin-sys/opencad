# #3DBenchy — quoted official specification

Transcription of the cited Creative Tools sources. millimetres and degrees throughout.
Revision: public pages and brochure as retrieved 2026-09-16 from 3dbenchy.com.
License note from the brochure: CC BY-ND 4.0; this file quotes published dimensions, it is not the official STL.

## A. User intent (also in sources/prompt.md)

Create a CAD model of the standard 1:1 #3DBenchy tugboat used to calibrate 3D printers.
The user will print the result and physically measure features against an existing control print.

The user quoted these 1:1 overall sizes as matching a Bambu Lab print:
Length 60.00 mm, width 31.00 mm, height 48.00 mm.

## B. Stated dimensions — 3dbenchy.com/dimensions/ and brochure page “Measure and calibrate”

Quoted verbatim from the official measure-and-calibrate text:

1. Bridge roof length. The front and rear surfaces of the roof are parallel at a distance of 23.00 mm.
2. Chimney roundness. The cylindrical hole and outer top part of the chimney measure 3.00 and 7.00 mm in diameter. The depth of the blind hole measures 11.00 mm.
3. Horizontal overall-length. #3DBenchy’s horizontal overall-length from bow to stern measures 60.00 mm.
4. Horizontal overall-width. #3DBenchy’s horizontal overall-width from port to starboard measures 31.00 mm.
5. Vertical overall-height. #3DBenchy’s vertical overall-height from top to bottom measures 48.00 mm. The top of the box measures 15.50 mm above the bottom surface.
6. Cargo-box size. The box on #3DBenchy’s deck measures 12.00 x 10.81 mm on the outside and 8.00 x 7.00 mm on the inside. The depth measures 9.00 mm.
7. Hawsepipe diameter. The inner diameter of #3DBenchy’s hawsepipe measures 4.00 mm. The depth of the flange against the hull is 0.30 mm.
8. Bridge front window size. The rectangular front window measures 10.50 x 9.50 mm. Its parallel inner surfaces are horizontally cut into the bridge.
9. Bridge rear window size. The inner diameter of the cylindrical stern window meastures 9.00 mm. Its outer diameter measures 12.00 mm. The flange’s depth is 0.30 mm.
10. Bow overhang inclination. #3DBenchy’s high-cain spoon bow has a 40° overhang angle to the horizontal plane.
11. Bridge roof inclination. The roof of the bridge slopes at a 5.5° angle to the horizontal plane.
12. Small-detail stern nameplate. The sign and small letters at the stern are extruded at 0.10 mm.

Official dimension figures ( rasters under sources/ ) illustrate those twelve items. They are the authoritative drawings for the labelled numbers. Do not re-measure a labelled number from pixels when the caption already states it.

## C. Stated volume and process notes — 3dbenchy.com/about/ and /features/, brochure “Features”

- Designed to print at 1:1 scale without support materials.
- “the small volume (15.55 cm3)” — finished printed solid volume = 15550 mm³.
- Perfectly symmetrical (port–starboard), so any skewness and warping is easy to detect.
- Top surfaces of the deck, box and chimney are planar, horizontal and parallel to the bottom plane.
- Letters on the stern are less than 2 mm tall; nameplate thickness is 0.1 mm (same 0.10 mm extrusion as B.12).
- Chimney: concentric cylindrical inner and outer diameters (see B.2).
- Rear window: large circular horizontal hole; the boat’s wheel is a round secluded feature.
- Hawsepipe: small short horizontal hole with a very thin flange against the hull (see B.7).
- Fishing-rod-holder: a very small slightly-slanted blind hole.
- Shallow letters on the bottom (first-layer details).
- Hull: large smooth overhanging curved surface.
- Gunwale and bridge roof are low-slope surfaces.
- STL triangulation maximum deviation from the original CAD is stated as 0.001 mm (quality of the official mesh, not a CAD parameter we can reconstruct without that mesh).

## D. Features visible in sources/image.png (physical 1:1 print, illustrative)

A white fused-filament print of a tugboat, approximately three-quarter starboard-bow view, sitting on its keel:

- Spoon bow with a circular hawsepipe through the hull.
- Sheerline / gunwale, flared hull sides, transom stern.
- Cabin/bridge with a rectangular front window, rectangular side door/window openings (port and starboard), slatted bridge roof, cylindrical chimney/funnel on the roof.
- Aft cargo box on deck, open on top, with a small cylindrical fitting on the starboard aft deck.
- Small cylindrical fitting on the bow deck (fishing-rod holder region).

Layer lines and print artefacts are not CAD features. The photograph is not a dimensioned drawing; any size taken from it is `measured` with a wide tolerance, and a labelled official number always wins.

## E. Explicitly not stated (must not be invented as `stated`)

The official sources do not give numbers for, among other things:

- Hull waterline / keel / transom / sheer curves (only overall L×W×H, 40° bow overhang, and qualitative “smooth overhanging curved surface”).
- Cabin/bridge outer length, width, height, wall thickness, or side-opening sizes (front window and rear-window diameters are given; side openings are not).
- Chimney height, axial position, or height of the chimney top other than overall height 48.00 mm.
- Deck height except the cargo-box top at 15.50 mm above the bottom.
- Which cargo-box outer number is beam vs length (12.00 vs 10.81) and which inner number is beam vs length (8.00 vs 7.00) — read the official box figure.
- Hawsepipe / window / door through-depth except the 0.30 mm flanges where given.
- Wheel geometry, fishing-rod-holder diameter/depth/angle, bottom letterforms, nameplate letterforms, gunwale thickness, interior of the cabin.

Unknown details are `open_questions`. Only if the later solid cannot be built without a number may it be `inferred`, with rationale and a wide digital tolerance.

## F. Frame convention for this reconstruction (no official CAD origin is published)

Adopt a right-handed millimetre frame that a later reader can reproduce from the hull:

- Bottom (keel contact plane) at z = 0, +z toward the chimney top (overall height 48 mm).
- Length along +x from stern toward bow (or the reverse — pick one and state it), overall 60 mm.
- Beam along +y, port–starboard, centred, overall 31 mm, symmetry plane y = 0.
- Origin: the intersection of the midship/centreline plane y = 0, the bottom plane z = 0, and a longitudinal station that is defined in words (for example the bounding-box mid-length, or the transom, or the bow). State which.

Name planar faces that later meshing or printing needs: bottom/keel plane, cargo-box top, chimney top, and other identifiable planes if they are fixed by stated numbers.

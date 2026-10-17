# Original Prusa MINI extruder front housing: reconstruction brief

Source: prusa3d/Original-Prusa-MINI, `STEP/PRINTED PARTS/MINI-extruder-front.stp` (GNU GPL v3.0). The
reference CAD is evaluator-only; the agent works from the renders, section drawings and the dimension
sheet in this bundle.

## What the part is

The front half of the MINI extruder body: a printed plate, 53 x 14 x 63.72 mm, that mates face-to-face
with the extruder rear housing and carries the idler pivot. Functional geometry that governs assembly:

- Frame (native to the reference): x across the plate (-26.5 .. +26.5), y through the plate thickness
  with the flat back (mating) face at y = 0 and the front face at y = 14, z vertical (-30 .. +33.72) with
  the flat bottom face at z = -30.
- A keyhole-shaped central opening: a Ø22.5 recess 3 mm deep from the back face (y 0..3), a Ø16 bore
  (y 3..8) and a Ø26 counterbore from the front (y 8..14), all on the axis x = -2, z = 0 (parallel to y);
  above it a Ø12 recess (y 0..3) and Ø16 bore (y 3..8) with a Ø14 counterbore (y 10.36..14) on the axis
  x = -2, z = 16.4. The two circles merge into one keyhole in the mid-plate section.
- Screw holes parallel to y: Ø3.4 through holes and their Ø6.5 / Ø3.5 counterbores and heat-set traps
  at the positions listed in the dimension sheet; hexagonal nut traps on the front face around several
  of them.
- The filament path: Ø4 holes near the top lug (x ~ 14.7 and an angled entry) and the hotend clamp
  channel along z at x ~ 25.6 (stepped Ø12.63 / Ø9.5 / Ø8 bores, partial, forming the groove-mount
  half-clamp) on the +x side.
- Mating planes: back face y = 0, front face y = 14, bottom z = -30, left side x = -26.5, plus the
  smaller +x side faces.

The organic fan-duct lobe on the +x side, the top lug fillet, the embossed "R1" text and arrow are
cosmetic for this benchmark: reproduce their envelope, but they are not scored individually.

## What is scored (evaluator)

Required: bounding box, one solid, every axis-aligned cylindrical feature (hole or bore) with its axis
position and depth, the mating planes' positions and areas, and the mid-plate section area at y = 7.
Diagnostic only: volume, centre of mass, exterior deviation against the reference mesh.

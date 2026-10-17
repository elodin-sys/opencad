# Raspberry Pi 5 two-piece enclosure: requirements (the contract to design to)

This is a design task, not a reconstruction: there is no reference enclosure. Every requirement below
is checked on the exported geometry. Interface authority: Raspberry Pi 5 mechanical drawing
RP-008347-DS-1 (attached as `rpi5-drawing-01.png`; all dimensions mm, approximate per the drawing note).

## Board frame (use this frame for the enclosure too)

- x along the 85 mm board edge, y along the 56 mm edge, origin at the board corner nearest the USB-C
  connector (bottom-left in the drawing's plan view); z up with the PCB bottom surface at z = 0 and the
  PCB top at z = 1.6.
- Mounting holes Ø2.7 (M2.5) at (x, y) = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]; 58 x 49 centres.
- Bottom-side components reach z = -3.0 everywhere except within 3.1 mm of each
  hole centre (component-free rings where standoffs may touch the board).
- Top-side envelope: the component field needs 20.0 mm of clear height above the PCB top over the
  whole board footprint (this fits the official Active Cooler).
- Connectors on the y = 0 edge (plan view bottom): USB-C centred x = 11.2, micro-HDMI centred x = 25.8 and
  x = 39.2. Connectors on the x = 85 edge: two stacked USB-A pairs centred y = 47.0 and y = 29.1, RJ45
  centred y = 10.2. The micro-SD slot is under the board at the x = 0 edge, y 22..34. Each connector needs
  a wall opening that a cable plug body passes through: the plug envelopes are listed below as boxes in
  the board frame that must contain no enclosure material.

## Enclosure requirements

1. Two separate printed parts (two solids in one STEP, not touching each other's material): `base`
   below/around the board and `lid` above. The base contains the point (42.5, 28, -6); the lid contains
   (42.5, 28, 24.6).
2. Standoffs: four bosses on the base whose top faces lie exactly at z = 0 (the PCB bottom) centred on the
   four hole positions, each with a Ø2.5 x >= 5 mm deep pilot hole on the hole axis for M2.5 self-tapping
   screws from above the board (the boss outer diameter is your choice, <= 6.2 mm).
3. Board fit: no enclosure material inside the PCB slab [0,85] x [0,56] x [0,1.6], inside the
   bottom-component keep-out (the slab footprint from z = -3.0 to 0, minus the four standoff
   rings), or inside the top envelope [0,85] x [0,56] x [1.6, 21.6]. Leave >= 0.5 mm
   between the board edges and the inner walls.
4. Connector access: none of these plug envelopes may intersect enclosure material:
   - usb_c_plug: min [4.699999999999999, -25.0, 1.6] max [17.7, 0.0, 8.6]
   - hdmi0_plug: min [19.8, -25.0, 1.6] max [31.8, 0.0, 8.1]
   - hdmi1_plug: min [33.2, -25.0, 1.6] max [45.2, 0.0, 8.1]
   - usb_a_upper_plug: min [85.0, 39.5, 1.6] max [110.0, 54.5, 18.6]
   - usb_a_lower_plug: min [85.0, 21.6, 1.6] max [110.0, 36.6, 18.6]
   - rj45_plug: min [85.0, 1.6999999999999993, 1.6] max [110.0, 18.7, 16.6]
   - sd_card_slot: min [-25.0, 22.0, -3.0] max [0.0, 34.0, 0.0]
5. Lid closes on the base: the lid rests on the base rim (max gap 0.1 mm at the closest approach) with
   zero interference; the lid is removable, so no fused geometry.
6. Lid fastening: at least four Ø3.0..3.4 clearance holes through the lid along z that continue as
   Ø2.5 pilot holes >= 5 mm deep into base corner posts, positioned outside the board footprint.
7. Walls: minimum wall and floor thickness 2.0 mm for the enclosure shells, measured by the evaluator as the
   5th percentile of inward ray casts on the exported STL (walls, floor, lid, the material around every
   opening). The four standoff bosses are the one accepted exception: a boss capped at Ø6.2 around
   a Ø2.5 pilot leaves a 1.85 mm annulus, which is intended; declare the wall check
   with the percentile statistic (or exclude the boss annuli by region), not as a global minimum.
8. Declared manufacturing process: FFF printing, no supports; overhangs <= 45 deg; the base prints on its
   floor and the lid on its ceiling.
9. Parametric: enclosure wall thickness, internal headroom, and standoff height are top-level parameters;
   the headroom parameter carries a regeneration sweep over 10 values from 15 to 35 mm and one infeasible
   value (negative headroom) that an assert must reject. Sweep values only have to regenerate a valid
   two-solid enclosure with the standoff datums and openings preserved; the fit requirements above are
   checked at the nominal 20.0 mm only, so no assert may reject a headroom in 15..35.

## Not required

Ventilation slots, text, fillets and cable strain reliefs are welcome but not scored. Do not model the
board itself in the deliverable; it is an evaluator-side keep-out envelope.

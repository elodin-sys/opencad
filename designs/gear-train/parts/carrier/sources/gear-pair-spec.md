# Spur-gear pair on a carrier plate: design specification

Design the assembly below as editable KCL: three separate solids in one file (no fused bodies).

| Parameter | Value |
| --- | ---: |
| Module | 2 mm |
| Pressure angle | 20 deg |
| Profile shift | 0 (both gears) |
| Pinion | 20 teeth, bore Ø6, axis at (0, 0) parallel to z |
| Wheel | 40 teeth, bore Ø8, axis at (60, 0) parallel to z |
| Centre distance | 60 mm (= (20 + 40) x 2 / 2) |
| Face width | 8 mm, both gears from z = 0 to z = 8 |
| Addendum / dedendum | 1.0 m / 1.25 m (tip radii 22 and 42; root radii 17.5 and 37.5; tip clearance 0.5) |
| Circular backlash | 0.10 mm total: thin each tooth by 0.05 mm at its pitch circle |
| Tooth phase | pinion has a tooth centred on +x; the wheel has a tooth SPACE centred toward the pinion (rotate its pattern half a pitch, pi/40) |
| Carrier plate | 110 x 50 x 5 mm, corner at (-25, -25, -5) to (85, 25, 0), with Ø6 and Ø8 clearance holes on the two gear axes |
| Motion | the wheel turns at half the pinion's speed in the opposite sense; the pair must rotate through a full pitch with zero interference and a flank gap of at most 0.15 mm |

Frame: z up (gear axes), the pinion axis is the origin, +x from the pinion axis toward the wheel axis. The gears sit on
the carrier (gear bottoms at z = 0, carrier top at z = 0), touching but separate. The involute flanks may be built from
the involute equations (recommended, sample the flank at 12-16 points from the base circle to the tip) or with the
standard library's gear functions if they honour the module, tooth counts, pressure angle and backlash above.

Scored on the exported STEP: three solids, tooth counts (20 and 40) from a mid-thickness section, bore axes and
diameters, the centre distance, the tooth profile against an independently generated involute (p95 <= 0.1 mm), and a
rotation sweep of the meshed pair (interference and backlash band). The reference geometry is evaluator-only.

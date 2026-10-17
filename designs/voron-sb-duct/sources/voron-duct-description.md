# Voron Stealthburner printhead front (Rapido V2 variant): ducted housing reconstruction brief

Source: VoronDesign/Voron-Stealthburner, `CAD/Printheads/Stealthburner_Printhead_Rapido_V2.step`, the
front (part-cooling duct) body (GPL-3.0). The reference CAD is evaluator-only; work from the renders,
the section drawings and the dimension sheet.

## What the part is

The front shell of the Stealthburner toolhead: a printed housing 71.07 x 27.40 x 59.13 mm that carries
two part-cooling air ducts, the hotend cavity and the hotend-fan opening. Frame (native to the
reference): x across the toolhead (-35.53 .. +35.53, symmetric), y from the flat back mating face at
y = 0 toward the front (negative y, to -27.40), z up from the nozzle end (z = 2.37) to the top (z = 61.5).

## Interior geometry that is scored (the section drawings show it; this text names it)

- Two part-cooling ducts, mirror images about x = 0. Each is a closed curved channel that starts at a
  rectangular fan inlet on the top face (about x -24..-17 / 17..24, y -23..-12, z ~ 56) and runs down the
  outside of the housing to the nozzle end, where it forks into two outlets that open downward and inward
  around z ~ 8..10 (see sections z = 10 and z = 20). At z = 45 each duct is a single channel about 8 x 19 mm
  (sections z = 45, z = 30); the duct wall is about 1 mm thick. The two ducts do not connect to each other.
- The hotend cavity: a rounded-rectangle pocket about 26 mm wide (x) and 35 mm tall (z 9..44), open to the
  back face (y = 0) and to the nozzle end, with the round hotend-fan opening on the front (see y = -12 and
  y = -20 sections and the front render).
- The screw holes and their bosses at the positions in the dimension sheet.

The evaluator checks connectivity inside the ducts (a probe near each fan inlet must reach a probe near
its outlets through air, with the ports sealed; a path around the outside does not count), that the two
ducts are separate, the hotend cavity, the air volume of each passage, the material area at the section
stations, and the minimum wall thickness (5th percentile of inward ray casts >= 0.75 mm). Exterior
volume and deviation are diagnostic only: styling surfaces, the embossed text and the fan grille are
cosmetic.

# ECR-1: +10 mm internal headroom

Increase the internal clear height above the PCB top from 20 mm to 30 mm without moving the board's mounting
datums: the four standoff top faces stay at z = 0 at (3.5,3.5) (61.5,3.5) (3.5,52.5) (61.5,52.5), the pilot holes
keep their axes and depth, the floor and the bottom keep-out clearance are unchanged, every connector plug envelope
still passes through its opening (the openings may grow upward but must not move), and the lid still closes on the
base rim with zero interference. The lid may grow taller or the base walls may grow; do not change wall thickness.
Update the acceptance envelope (z max grows by 10) and the headroom probes (air at z = 1.6 + 30 - 0.5) accordingly.

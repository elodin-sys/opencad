from pathlib import Path

from build123d import Align, Box, Location, import_step

here = Path(__file__).resolve().parent
bush = import_step(here / "inputs" / "nottingham-bearing-bush.step")
shaft = import_step(here / "inputs" / "nottingham-bearing-shaft.step").move(Location((0.0, 0.0, 37.5)))

# Box stays inside the D150 wall and crosses the bore, the split plane and both end faces.
stock = Box(102.0, 52.0, 77.0, align=(Align.CENTER, Align.MIN, Align.MIN)).move(Location((0.0, -51.0, -1.0)))
# Caps: y <= 0, z = 0..75. Outward normals are +y, -z and +z.
closure = Box(120.0, 80.0, 75.0, align=(Align.CENTER, Align.MAX, Align.MIN))
bore = (stock - bush) & closure
oil = bore - shaft

seed = (0.0, -50.05, 37.5)
film = [solid for solid in oil.solids() if solid.is_inside(seed)]
oil = film[0]

result = [bush, shaft, oil]
placements = {
    "bush": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "shaft": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 37.5], [0.0, 0.0, 0.0, 1.0]],
    "oil": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
}
joints = {
    "journal": {"origin": [0.0, 0.0, 37.5], "axis": [0.0, 0.0, 1.0]},
    "oilFixed": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
}

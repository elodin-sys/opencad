from build123d import Cylinder, Pos

discRadius = 140.0
discThickness = 13.0
hubRadius = 80.0
hubHeight = 10.0

assert discRadius > hubRadius > 0, "infeasible: hub must sit inside a positive disc radius"
assert discThickness > 0, "infeasible: discThickness must be positive"
assert hubHeight > 0, "infeasible: hubHeight must be positive"

disc = Pos(0, 0, discThickness / 2) * Cylinder(discRadius, discThickness)
hub = Pos(0, 0, discThickness + hubHeight / 2) * Cylinder(hubRadius, hubHeight)
result = disc + hub

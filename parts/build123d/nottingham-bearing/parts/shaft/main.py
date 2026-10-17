from build123d import Cylinder

shaftDiameter = 100.0
shaftLength = 230.0

assert shaftDiameter > 0, "infeasible: shaftDiameter must be positive"
assert shaftLength > 0, "infeasible: shaftLength must be positive"

result = Cylinder(shaftDiameter / 2, shaftLength)

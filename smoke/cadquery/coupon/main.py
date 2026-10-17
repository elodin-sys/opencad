import cadquery as cq

width = 60.0
height = 40.0
thickness = 4.0
assert thickness > 0, "infeasible: thickness must be positive"
assert width > 0, "infeasible: width must be positive"
assert height > 0, "infeasible: height must be positive"

result = cq.Workplane("XY").box(width, height, thickness, centered=(False, False, False))

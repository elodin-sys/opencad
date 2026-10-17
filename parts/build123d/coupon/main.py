from build123d import Align, Rectangle, extrude

width = 60.0
height = 40.0
thickness = 4.0
assert width > 0, "infeasible: width must be positive"
assert height > 0, "infeasible: height must be positive"
assert thickness > 0, "infeasible: thickness must be positive"

sketch = Rectangle(width, height, align=(Align.MIN, Align.MIN))
result = extrude(sketch, amount=thickness)

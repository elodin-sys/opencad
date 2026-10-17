Source URL: https://zoo.dev/aquarium/pillow-block-bearing
Title: Pillow Block Bearing

# Pillow Block Bearing

A bearing pillow block, also known as a plummer block or pillow block bearing, is a pedestal used to provide support for a rotating shaft with the help of compatible bearings and various accessories. Housing a bearing, the pillow block provides a secure and stable foundation that allows the shaft to rotate smoothly within its machinery setup. These components are essential in a wide range of mechanical systems and machinery, playing a key role in reducing friction and supporting radial and axial loads.

- Page: /aquarium/pillow-block-bearing
- Legacy docs page: /docs/kcl-samples/pillow-block-bearing
- Preview image: /kcl-samples/screenshots/pillow-block-bearing.png
- Categories: Mechanical Components, Industrial & Manufacturing

## Files

### main.kcl

```kcl
// Pillow Block Bearing
// A bearing pillow block, also known as a plummer block or pillow block bearing, is a pedestal used to provide support for a rotating shaft with the help of compatible bearings and various accessories. Housing a bearing, the pillow block provides a secure and stable foundation that allows the shaft to rotate smoothly within its machinery setup. These components are essential in a wide range of mechanical systems and machinery, playing a key role in reducing friction and supporting radial and axial loads.
// Categories: Mechanical Components; Industrial & Manufacturing

// Set units
@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

// Import parts and parameters
import * from "parameters.kcl"
import "ball-bearing.kcl" as ballBearing
import "block.kcl" as block

// Render each part
ballBearing
block
```

### ball-bearing.kcl

```kcl
// Pillow Block Bearing
// The ball bearing for the pillow block bearing assembly

// Set units
@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

// Import Parameters
import * from "parameters.kcl"

// Create the sketch of one of the balls. The ball diameter is sized as a fraction of the difference between inner and outer radius of the bearing
ballsSketch = sketch(on = offsetPlane(XY, offset = stockThickness / 2)) {
  arc1 = arc(start = [var 1.19375in, var 0.001in], end = [var 0.975in, var 0.001in], center = [var 1.084375in, var 0.001in])
  line2 = line(start = [var 1.19375in, var 0.001in], end = [var 0.975in, var 0.001in])
  coincident([arc1.start, line2.start])
}

region001 = region(segments = [ballsSketch.arc1, ballsSketch.line2])
// Revolve the ball to make a sphere and pattern around the inside wall
balls = revolve(region001, axis = X)
  |> patternCircular3d(
       arcDegrees = 360,
       axis = [0, 0, 1],
       center = [0, 0, 0],
       instances = 16,
       rotateDuplicates = true,
     )

// Create the sketch for the chain around the balls
chainSketch = sketch(on = offsetPlane(XY, offset = stockThickness / 2)) {
  arc1 = arc(start = [var 1.1390625in, var 0.108253175in], end = [var 1.0296875in, var 0.108253175in], center = [var 1.084375in, var 0.013531647in])
  line2 = line(start = [var 1.1390625in, var 0.108253175in], end = [var 1.1390625in, var 0.135596925in])
  coincident([arc1.start, line2.start])
  line3 = line(start = [var 1.1390625in, var 0.135596925in], end = [var 1.0296875in, var 0.135596925in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var 1.0296875in, var 0.135596925in], end = [var 1.0296875in, var 0.108253175in])
  coincident([line3.end, line4.start])
}

region002 = region(segments = [chainSketch.arc1, chainSketch.line2])
// Revolve the chain sketch
chainHead = revolve(region002, axis = X)
  |> patternCircular3d(
       arcDegrees = 360,
       axis = [0, 0, 1],
       center = [0, 0, 0],
       instances = 16,
       rotateDuplicates = true,
     )

// Create the sketch for the links in between the chains
linkSketch = sketch(on = XZ) {
  circle1 = circle(start = [var 1.11171875in, var 0.25in], center = [var 1.084375in, var 0.25in])
}

// Create the walls of the bearing
sketch001 = sketch(on = XZ) {
  line1 = line(start = [var 1.2425in, var 0.5in], end = [var 1.24162738in, var 0.450007615in])
  line2 = line(start = [var 1.24162738in, var 0.450007615in], end = [var 0.94912738in, var 0.450007615in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 0.94912738in, var 0.450007615in], end = [var 0.94912738in, var 0.105in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var 0.94912738in, var 0.105in], end = [var 0.92412738in, var 0.105in])
  coincident([line3.end, line4.start])
  line5 = line(start = [var 0.92412738in, var 0.105in], end = [var 0.917232629in, var 0.5in])
  coincident([line4.end, line5.start])
  line6 = line(start = [var 0.917232629in, var 0.5in], end = [var 1.2425in, var 0.5in])
  coincident([line5.end, line6.start])
}
region003 = region(segments = [sketch001.line1, sketch001.line2])
bearingUpper = revolve(region003, angle = 360, axis = Y)
  |> appearance(color = "#121212")

sketch002 = sketch(on = XZ) {
  line1 = line(start = [var 0.875in, var 0.025in], end = [var 0.925in, var 0.025in])
  line2 = line(start = [var 0.925in, var 0.025in], end = [var 0.935352762in, var 0.063637033in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 0.935352762in, var 0.063637033in], end = [var 0.985352762in, var 0.063637033in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var 0.985352762in, var 0.063637033in], end = [var 0.995705524in, var 0.025in])
  coincident([line3.end, line4.start])
  line5 = line(start = [var 0.995705524in, var 0.025in], end = [var 1.3125in, var 0.025in])
  coincident([line4.end, line5.start])
  line6 = line(start = [var 1.3125in, var 0.025in], end = [var 1.3125in, var 0.525in])
  coincident([line5.end, line6.start])
  line7 = line(start = [var 1.3125in, var 0.525in], end = [var 1.2425in, var 0.525in])
  coincident([line6.end, line7.start])
  line8 = line(start = [var 1.2425in, var 0.525in], end = [var 1.235081597in, var 0.1in])
  coincident([line7.end, line8.start])
  line9 = line(start = [var 1.235081597in, var 0.1in], end = [var 0.925in, var 0.1in])
  coincident([line8.end, line9.start])
  line10 = line(start = [var 0.925in, var 0.1in], end = [var 0.915836091in, var 0.625in])
  coincident([line9.end, line10.start])
  line11 = line(start = [var 0.915836091in, var 0.625in], end = [var 0.875in, var 0.625in])
  coincident([line10.end, line11.start])
  line12 = line(start = [var 0.875in, var 0.625in], end = [var 0.875in, var 0.025in])
  coincident([line11.end, line12.start])
}
region004 = region(segments = [sketch002.line1, sketch002.line2])
bearingLower = revolve(region004, angle = 360, axis = Y)
  |> appearance(color = "#f0f0f0")

region005 = region(segments = [linkSketch.circle1])
// Revolve the link sketch
revolve(region005, axis = Y, angle = 360 / 16)
  |> patternCircular3d(
       arcDegrees = 360,
       axis = [0, 0, 1],
       center = [0, 0, 0],
       instances = 16,
       rotateDuplicates = true,
     )
```

### block.kcl

```kcl
// Pillow Block Bearing
// The machined block for the pillow block bearing assembly. The block is dimensioned using the bolt pattern spacing, and each bolt hole includes a counterbore

// Set units
@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

// Import Parameters
import * from "parameters.kcl"

// Calculate the dimensions of the block using the specified bolt spacing. The size of the block can be defined by adding a multiple of the counterbore diameter to the bolt spacing
blockLength = boltSpacingX + counterboreDiameter + boltDiameter
blockWidth = boltSpacingY + counterboreDiameter + boltDiameter

// Draw the base plate
plateSketch = sketch(on = XY) {
  line1 = line(start = [var -3.0625in, var -2.0625in], end = [var 3.0625in, var -2.0625in])
  line2 = line(start = [var 3.0625in, var -2.0625in], end = [var 3.0625in, var 2.0625in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 3.0625in, var 2.0625in], end = [var -3.0625in, var 2.0625in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -3.0625in, var 2.0625in], end = [var -3.0625in, var -2.0625in])
  coincident([line3.end, line4.start])
  bearingBore = circle(start = [var 1.3125in, var 0in], center = [var 0in, var 0in])
}
region001 = region(segments = [plateSketch.line1, plateSketch.line2])
plateBody = extrude(region001, length = stockThickness)
  |> appearance(color = "#1e62eb")
  |> fillet(
       radius = boltDiameter * 1 / 3,
       tags = [
         getNextAdjacentEdge(region001.tags.line2),
         getNextAdjacentEdge(region001.tags.line1),
         getNextAdjacentEdge(region001.tags.line3),
         getNextAdjacentEdge(region001.tags.line4)
       ],
     )

// Define hole positions
holePositions = [
  [-boltSpacingX / 2, -boltSpacingY / 2],
  [-boltSpacingX / 2, boltSpacingY / 2],
  [boltSpacingX / 2, -boltSpacingY / 2],
  [boltSpacingX / 2, boltSpacingY / 2]
]

// Create the counterbore and through-hole cutters explicitly so the physical
// result does not depend on the implicit face-extrusion behavior of sketch-v1.
counterboreSketch = sketch(on = offsetPlane(XY, offset = stockThickness)) {
  bore = circle(start = [var -2.125in, var -1.5in], center = [var -2.5in, var -1.5in])
}
counterboreSeed = extrude(region(segments = [counterboreSketch.bore]), length = -counterboreDepth)
counterboreCutters = patternLinear3d(
  counterboreSeed,
  instances = 2,
  distance = boltSpacingY,
  axis = Y,
)
  |> patternLinear3d(instances = 2, distance = boltSpacingX, axis = X)
plateCounterbored = subtract(plateBody, tools = counterboreCutters)

boltSketch = sketch(on = offsetPlane(XY, offset = stockThickness - counterboreDepth)) {
  bore = circle(start = [var -2.3125in, var -1.5in], center = [var -2.5in, var -1.5in])
}
boltSeed = extrude(region(segments = [boltSketch.bore]), length = -(stockThickness - counterboreDepth))
boltCutters = patternLinear3d(
  boltSeed,
  instances = 2,
  distance = boltSpacingY,
  axis = Y,
)
  |> patternLinear3d(instances = 2, distance = boltSpacingX, axis = X)
block = subtract(plateCounterbored, tools = boltCutters)
  |> appearance(color = "#1e62eb")
```

### parameters.kcl

```kcl
// Global parameters for the pillow block bearing

// Set units
@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

// Export parameters
export boltSpacingX = 5
export boltSpacingY = 3
export boltDiameter = 3 / 8
export counterboreDiameter = 3 / 4
export counterboreDepth = 3 / 16
export stockThickness = .5
export bearingBoreDiameter = 1 + 3 / 4
export bearingOuterDiameter = bearingBoreDiameter * 1.5
export sphereDia = (bearingOuterDiameter - bearingBoreDiameter) / 4
export chainWidth = sphereDia / 2
export chainThickness = sphereDia / 8
export linkDiameter = sphereDia / 4
```

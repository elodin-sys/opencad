Source URL: https://zoo.dev/aquarium/artificial-heart
Title: Artificial Heart

# Artificial Heart

A model of a permanent electromagnetic blood pump

- Page: /aquarium/artificial-heart
- Legacy docs page: /docs/kcl-samples/artificial-heart
- Preview image: /kcl-samples/screenshots/artificial-heart.png
- Categories: Medical & Assistive

## Files

### main.kcl

```kcl
// Artificial Heart
// A model of a permanent electromagnetic blood pump
// Categories: Medical & Assistive

// Define units
@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Import all components
import "housing.kcl" as housing
import "stator.kcl" as stator
import "impeller.kcl" as impeller
import "plumbing.kcl" as plumbing
```

### housing.kcl

```kcl
// Housing

// Set units
@settings(defaultLengthUnit = in, kclVersion = 2.0)

// Sketch the primary housing for the pump, to be revolved
sketch001 = sketch(on = XY) {
  line1 = line(start = [var 0.47in, var -0.19in], end = [var 0.47in, var -0.23in])
  line2 = line(start = [var 0.47in, var -0.23in], end = [var 1.5in, var -0.23in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 1.5in, var -0.23in], end = [var 1.5in, var -0.63in])
  coincident([line2.end, line3.start])
  arc1 = arc(start = [var 1.43in, var -0.7in], end = [var 1.5in, var -0.63in], center = [var 1.43in, var -0.63in])
  coincident([line3.end, arc1.end])
  tangent([line3, arc1])
  line4 = line(start = [var 1.43in, var -0.7in], end = [var 0.2in, var -0.7in])
  coincident([line4.start, arc1.start])
  line5 = line(start = [var 0.2in, var -0.7in], end = [var 0.2in, var -0.73in])
  coincident([line4.end, line5.start])
  line6 = line(start = [var 0.2in, var -0.73in], end = [var 1.43in, var -0.73in])
  coincident([line5.end, line6.start])
  arc2 = arc(start = [var 1.43in, var -0.73in], end = [var 1.53in, var -0.63in], center = [var 1.43in, var -0.63in])
  coincident([line6.end, arc2.start])
  tangent([line6, arc2])
  line7 = line(start = [var 1.53in, var -0.63in], end = [var 1.53in, var 0.67in])
  coincident([line7.start, arc2.end])
  arc3 = arc(start = [var 1.53in, var 0.67in], end = [var 1.43in, var 0.77in], center = [var 1.43in, var 0.67in])
  coincident([line7.end, arc3.start])
  tangent([line7, arc3])
  line8 = line(start = [var 1.43in, var 0.77in], end = [var 0.2in, var 0.77in])
  coincident([line8.start, arc3.end])
  line9 = line(start = [var 0.2in, var 0.77in], end = [var 0.2in, var 0.74in])
  coincident([line8.end, line9.start])
  line10 = line(start = [var 0.2in, var 0.74in], end = [var 1.43in, var 0.74in])
  coincident([line9.end, line10.start])
  arc4 = arc(start = [var 1.5in, var 0.67in], end = [var 1.43in, var 0.74in], center = [var 1.43in, var 0.67in])
  coincident([line10.end, arc4.end])
  tangent([line10, arc4])
  line11 = line(start = [var 1.5in, var 0.67in], end = [var 1.5in, var -0.19in])
  coincident([line11.start, arc4.start])
  line12 = line(start = [var 1.5in, var -0.19in], end = [var 0.47in, var -0.19in])
  coincident([line11.end, line12.start])
  coincident([line12.end, line1.start])
  horizontal(line6)
  horizontal(line4)
  horizontal(line2)
  horizontal(line12)
  horizontal(line10)
  horizontal(line8)
  vertical(line9)
  vertical(line1)
  vertical(line5)
  vertical(line3)
  vertical(line11)
  vertical(line7)
  tangent([line4, arc1])
  tangent([line7, arc2])
  coincident([arc2.center, arc1.center])
  coincident([arc4.center, arc3.center])
  tangent([line11, arc4])
  tangent([line8, arc3])
  radius(arc2) == .1
  radius(arc1) == .07
  equalRadius([arc2, arc3])
  equalRadius([arc1, arc4])
  horizontalDistance([ORIGIN, line3.start]) == 1.5
  verticalDistance([line5.start, ORIGIN]) == .7

  verticalDistance([arc2.start, ORIGIN]) == 0.73in
  horizontalDistance([ORIGIN, line5.start]) == .2
  coincident([line5, line9])
  verticalDistance([line12.end, ORIGIN]) == 0.19
  distance([line1.start, line1.end]) == 0.04
}
region001 = region(segments = [sketch001.line1, sketch001.line2])
hide(sketch001)
revolve001 = revolve(region001, angle = 360deg, axis = Y)
  |> appearance(color = "#ededed", opacity = 30)

// Model a bore with the same outer diameter as the housing, which will be used for cutting the exterior ports to shape
sketch002 = sketch(on = XZ) {
  circle1 = circle(start = [var -1.18in, var 0.92in], center = [var 0in, var 0in])
  coincident([circle1.center, ORIGIN])
  radius(circle1) == 3 / 2
}
hide(sketch002)
region002 = region(segments = [sketch002.circle1])

extrude002 = extrude(region002, length = 2, symmetric = true)

// Model the two exterior bungs
sketch003 = sketch(on = -YZ) {
  line1 = line(start = [var 0in, var 0in], end = [var -0.3in, var -0.1in], construction = true)
  coincident([line1.start, ORIGIN])
  line2 = line(start = [var 0in, var 0in], end = [var 0.3in, var 0.1in], construction = true)
  coincident([line2.start, line1.start])
  coincident([line2, line1])
  equalLength([line2, line1])
  circle1 = circle(start = [var 0.44in, var 0.03in], center = [var 0.3in, var 0.1in])
  coincident([circle1.center, line2.end])
  circle2 = circle(start = [var -0.15in, var -0.15in], center = [var -0.3in, var -0.1in])
  coincident([circle2.center, line1.end])
  circle3 = circle(start = [var -0.17in, var -0.14in], center = [var -0.3in, var -0.1in])
  coincident([circle3.center, line1.end])
  circle4 = circle(start = [var 0.3in, var -0.04in], center = [var 0.3in, var 0.1in])
  coincident([circle4.center, line2.end])
  equalRadius([circle2, circle1])
  equalRadius([circle4, circle3])
  radius(circle1) == .2
  radius(circle4) == .17
  horizontalDistance([circle3.center, circle4.center]) == .75
  verticalDistance([circle3.center, circle4.center]) == .2
}
hide(sketch003)

region003 = region(segments = [sketch003.circle2])
region004 = region(segments = [sketch003.circle1])

extrude001 = extrude([region003, region004], length = 1.8)
  |> appearance(color = "#ededed", opacity = 30)

  // Rotate the outlet bungs into position, then cut so they fit the housing
  |> rotate(pitch = 45, global = true)
  |> subtract(tools = extrude002)

// Model a pocket on the front face of the housing
sketch004 = sketch(on = offsetPlane(XZ, offset = 0.73)) {
  arc1 = arc(start = [var -0.13in, var 1.27in], end = [var -1.27in, var -0.18in], center = [var 0in, var 0in])
  coincident([arc1.center, ORIGIN])
  arc2 = arc(start = [var 0.91in, var -1.04in], end = [var 1.28in, var -0.5in], center = [var 0in, var 0in])
  coincident([arc2.center, arc1.center])
  coincident([arc2.start, arc2.start])
  arc3 = arc(start = [var 0.05in, var 1.2in], end = [var -0.13in, var 1.27in], center = [var -0.11in, var 1.07in])
  coincident([arc1.start, arc3.end])
  tangent([arc1, arc3])
  arc4 = arc(start = [var 1.28in, var -0.5in], end = [var 1.25in, var -0.31in], center = [var 1.1in, var -0.43in])
  coincident([arc2.end, arc4.start])
  tangent([arc2, arc4])
  arc5 = arc(start = [var 0.7in, var -1.07in], end = [var 0.91in, var -1.04in], center = [var 0.78in, var -0.89in])
  coincident([arc2.start, arc5.end])
  tangent([arc2, arc5])
  arc6 = arc(start = [var -1.27in, var -0.18in], end = [var -1.14in, var -0.34in], center = [var -1.07in, var -0.15in])
  coincident([arc1.end, arc6.start])
  tangent([arc1, arc6])
  line1 = line(start = [var -1.14in, var -0.34in], end = [var 0.7in, var -1.07in])
  coincident([line1.start, arc6.end])
  coincident([line1.end, arc5.start])
  line2 = line(start = [var 1.25in, var -0.31in], end = [var 0.05in, var 1.2in])
  coincident([line2.start, arc4.end])
  coincident([line2.end, arc3.start])
  tangent([line1, arc6])
  tangent([line1, arc5])
  tangent([line2, arc4])
  tangent([line2, arc3])
  equalRadius([arc5, arc4, arc3, arc6])
  radius(arc6) == .2
  radius(arc1) == 1.28in
  radius(arc2) == 1.38in
  circle1 = circle(start = [var 0.59in, var -0.15in], center = [var 0in, var 0in])
  coincident([circle1.center, arc1.center])
  diameter(circle1) == 1.22in
}
hide(sketch004)
region006 = region(segments = [sketch004.arc1])

extrude004 = extrude(region006, length = .02)
  |> appearance(color = "#ededed", opacity = 30)

// Sketch the path for the front face inlet bung
sketch005 = sketch(on = XY) {
  line1 = line(start = [var 0in, var -0.7in], end = [var 0in, var -0.75in])
  vertical([line1.start, ORIGIN])
  vertical([line1.end, ORIGIN])
  verticalDistance([line1.start, ORIGIN]) == 0.7
  verticalDistance([line1.end, line1.start]) == .05
  arc1 = arc(start = [var 0in, var -0.75in], end = [var 0.6in, var -1.16in], center = [var 0.47in, var -0.75in])
  coincident([line1.end, arc1.start])
  tangent([line1, arc1])
  arc2 = arc(start = [var 0.91in, var -1.09in], end = [var 0.6in, var -1.16in], center = [var 0.98in, var -2.13in])
  coincident([arc1.end, arc2.end])
  tangent([arc1, arc2])
}

// Model the profile of the front inlet bung, then sweep
sketch006 = sketch(on = offsetPlane(XZ, offset = 0.7)) {
  circle1 = circle(start = [var 0.17in, var 0.15in], center = [var 0in, var 0in])
  coincident([circle1.center, ORIGIN])
  circle2 = circle(start = [var 0.12in, var 0.09in], center = [var 0in, var 0in])
  coincident([circle2.center, circle1.center])
  radius(circle1) == 0.2
  radius(circle2) == 0.17
}
hide(sketch006)
region005 = region(segments = [sketch006.circle1])

sweep001 = sweep(region005, path = sketch005)
  |> appearance(color = "#ededed", opacity = 30)
  |> rotate(pitch = 80)

// Sketch the path for the rear face inlet bung
sketch007 = sketch(on = XY) {
  line1 = line(start = [var 0in, var 0.7in], end = [var 0in, var 0.75in])
  vertical([line1.start, ORIGIN])
  vertical([line1.end, ORIGIN])
  arc1 = arc(start = [var 0.53in, var 1.23in], end = [var 0in, var 0.75in], center = [var 0.48in, var 0.75in])
  coincident([line1.end, arc1.end])
  tangent([line1, arc1])
  arc2 = arc(start = [var 0.53in, var 1.23in], end = [var 0.81in, var 1.2in], center = [var 1.32in, var 8.66in])
  coincident([arc1.start, arc2.start])
  tangent([arc1, arc2])
  verticalDistance([ORIGIN, line1.start]) == .7
  verticalDistance([line1.start, line1.end]) == .05
  line2 = line(start = [var 0.48in, var 0.75in], end = [var 0.53in, var 1.23in], construction = true)
  coincident([line2.start, arc1.center])
  coincident([line2.end, arc2.start])
  angleDimension(lines = [line2, line1], sector = 1, labelPosition = [0.28in, 1.38in]) == 6
}

// Model the profile of the rear inlet bung, then sweep
sketch008 = sketch(on = offsetPlane(XZ, offset = -0.7)) {
  circle1 = circle(start = [var 0.17in, var 0.15in], center = [var 0in, var 0in])
  coincident([circle1.center, ORIGIN])
  circle2 = circle(start = [var 0.12in, var 0.09in], center = [var 0in, var 0in])
  coincident([circle2.center, circle1.center])
  radius(circle1) == 0.2
  radius(circle2) == 0.17
}
hide(sketch008)
region008 = region(segments = [sketch008.circle1])

sweep002 = sweep(region008, path = sketch007)
  |> appearance(color = "#ededed", opacity = 30)
  |> rotate(pitch = 75)
```

### impeller.kcl

```kcl
// Impeller

// Set units
@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

// Define parameters
impellerDiameter = 3
plateHeight = 0.1
vaneCount = 7
vaneHeight = 0.1
vaneThickness = 0.14
mountDiameter = 0.25

// Revolve the base plate of the impeller
sketch002 = sketch(on = XY) {
  line2 = line(start = [var 1.5in, var 0.25in], end = [var 1.5in, var 0.35in])
  line3 = line(start = [var 1.5in, var 0.35in], end = [var 0.49in, var 0.35in])
  coincident([line2.end, line3.start])
  arc4 = arc(start = [var 0.33in, var 0.46in], end = [var 0.49in, var 0.35in], center = [var 0.49in, var 0.52in])
  coincident([line3.end, arc4.end])
  line5 = line(start = [var 0.33in, var 0.46in], end = [var 0.24in, var 0.69in])
  coincident([arc4.start, line5.start])
  line6 = line(start = [var 0.24in, var 0.69in], end = [var 0in, var 0.69in])
  coincident([line5.end, line6.start])
  distance([line2.start, line2.end]) == plateHeight
  horizontal(line3)
  horizontal(line6)
  line8 = line(start = [var 0in, var 0in], end = [var 2.31in, var 0in], construction = true)
  horizontal([line8.end, ORIGIN])
  line10 = line(start = [var 1.5in, var -0.25in], end = [var 1.5in, var -0.35in])
  line11 = line(start = [var 1.5in, var -0.35in], end = [var 0.49in, var -0.35in])
  coincident([line10.end, line11.start])
  arc1 = arc(start = [var 0.49in, var -0.35in], end = [var 0.33in, var -0.46in], center = [var 0.49in, var -0.52in])
  coincident([line11.end, arc1.start])
  tangent([line11, arc1])
  line12 = line(start = [var 0.33in, var -0.46in], end = [var 0.24in, var -0.69in])
  coincident([line12.start, arc1.end])
  line13 = line(start = [var 0.24in, var -0.69in], end = [var 0in, var -0.69in])
  coincident([line12.end, line13.start])
  symmetric([line2, line10], axis = line8)
  vertical(line2)
  symmetric([line11, line3], axis = line8)
  symmetric([arc1, arc4], axis = line8)
  symmetric([line12, line5], axis = line8)
  symmetric([line13, line6], axis = line8)
  coincident([line8.start, ORIGIN])
  tangent([line5, arc4])
  line1 = line(start = [var 0.4in, var 0in], end = [var 0.4in, var 0.25in])
  horizontal([line1.start, ORIGIN])
  line4 = line(start = [var 0.4in, var 0.25in], end = [var 1.5in, var 0.25in])
  coincident([line1.end, line4.start])
  coincident([line4.end, line2.start])
  line7 = line(start = [var 0in, var 0.69in], end = [var 0in, var -0.69in])
  coincident([line7.start, line6.end])
  coincident([line7.end, line13.end])
  line9 = line(start = [var 0.4in, var 0in], end = [var 0.4in, var -0.25in])
  coincident([line9.start, line1.start])
  line14 = line(start = [var 0.4in, var -0.25in], end = [var 1.5in, var -0.25in])
  coincident([line9.end, line14.start])
  coincident([line14.end, line10.start])
  vertical(line1)
  distance([line1.start, line1.end]) == 0.25
  horizontal(line4)
  horizontalDistance([line8.start, line4.end]) == impellerDiameter / 2
  horizontalDistance([line8.start, line9.start]) == .4
  symmetric([line1, line9], axis = line8)
  symmetric([line14, line4], axis = line8)
  vertical(line7)
  coincident([line7, line8.start])
}
hide(sketch002)
region002 = region(segments = [sketch002.line1, sketch002.line2])
basePlate = revolve(region002, axis = Y)

// Model a vane of the impeller
sketch003 = sketch(on = offsetPlane(XZ, offset = 0.4)) {
  arc1 = arc(start = [var -0.04in, var -0.71in], end = [var 1.46in, var 0.12in], center = [var 0.47in, var 0.14in])
  arc2 = arc(start = [var 0.04in, var -0.59in], end = [var -0.04in, var -0.71in], center = [var 0in, var -0.65in])
  coincident([arc1.start, arc2.end])
  arc3 = arc(start = [var 0.04in, var -0.59in], end = [var 1.32in, var 0.12in], center = [var 0.47in, var 0.14in])
  coincident([arc2.start, arc3.start])
  arc4 = arc(start = [var 1.46in, var 0.12in], end = [var 1.32in, var 0.12in], center = [var 1.39in, var 0.12in])
  coincident([arc3.end, arc4.end])
  coincident([arc1.end, arc4.start])
  radius(arc2) == 0.07in
  diameter(arc3) == 1.7
  radius(arc4) == 0.07in
  line2 = line(start = [var 1.39in, var 0.12in], end = [var 0in, var 0in], construction = true)
  coincident([line2.end, ORIGIN])
  line3 = line(start = [var 0in, var 0in], end = [var 0in, var -0.65in], construction = true)
  coincident([line2.end, line3.start])
  coincident([line3.end, arc2.center])
  line4 = line(start = [var -0.04in, var -0.71in], end = [var 0.04in, var -0.59in], construction = true)
  coincident([line4.start, arc1.start])
  coincident([line4.end, arc2.start])
  coincident([line3.end, line4])
  line5 = line(start = [var 1.32in, var 0.12in], end = [var 1.46in, var 0.12in], construction = true)
  coincident([line5.start, arc4.end])
  coincident([line5.end, arc1.end])
  coincident([line2.start, line5])
  equalLength([line4, line5])
  distance([line5.start, line5.end]) == vaneThickness
  vertical(line3)
  distance([line3.start, line3.end]) == 0.65
  coincident([arc3.center, arc1.center])
  tangent([arc1, arc2])
  tangent([arc3, arc4])
  angleDimension(lines = [line2, line3], labelPosition = [0.12in, 0.16in], sector = 3) == 85
  distance([line2.start, line2.end]) == 1.4
  coincident([line2.start, arc4.center])
}
hide(sketch003)
region003 = region(segments = [sketch003.arc1, sketch003.arc2])

vane = extrude(region003, length = vaneHeight)
  // Pattern the vane around the Z axis
  |> patternCircular3d(
       useOriginal = true,
       instances = vaneCount,
       axis = Y,
       center = [0, 0, 0],
     )
  |> patternLinear3d(instances = 2, distance = 1, axis = Y)
```

### plumbing.kcl

```kcl
// Plumbing

// Set units
@settings(defaultLengthUnit = in, kclVersion = 2.0)

// Draw the sweep path for the aorta and pulmonary artery
sketch002 = sketch(on = XZ) {
  line1 = line(start = [var 0in, var 0in], end = [var -1.17in, var 1.17in], construction = true)
  coincident([line1.start, ORIGIN])
  arc1 = arc(start = [var -1.17in, var 1.17in], end = [var -3.68in, var -0.77in], center = [var -2.3in, var 0.04in])
  coincident([line1.end, arc1.start])
  tangent([line1, arc1])
  line2 = line(start = [var -3.68in, var -0.77in], end = [var -2.09in, var -3.51in])
  coincident([line2.start, arc1.end])
  tangent([line2, arc1])
  line3 = line(start = [var 0in, var 0in], end = [var -1.72in, var 0in], construction = true)
  coincident([line3.start, line1.start])
  horizontal([line3.end, ORIGIN])
  horizontal(line3)
  angleDimension(lines = [line1, line3], sector = 1) == 45
  distance([line1.start, line1.end]) == 1.65in
  radius(arc1) == 3.2 / 2
  circle1 = circle(start = [var 1.18in, var 0.93in], center = [var 0in, var 0in], construction = true)
  coincident([circle1.center, line3.start])
  radius(circle1) == 3 / 2
}

// Draw the tube profiles for the aorta and pulmonary artery
sketch003 = sketch(on = offsetPlane(-YZ, offset = 1.65)) {
  line1 = line(start = [var 0in, var 0in], end = [var -0.3in, var -0.1in], construction = true)
  coincident([line1.start, ORIGIN])
  line2 = line(start = [var 0in, var 0in], end = [var 0.3in, var 0.1in], construction = true)
  coincident([line2.start, line1.start])
  coincident([line2, line1])
  equalLength([line2, line1])
  circle1 = circle(start = [var 0.44in, var 0.03in], center = [var 0.3in, var 0.1in])
  coincident([circle1.center, line2.end])
  circle2 = circle(start = [var -0.15in, var -0.15in], center = [var -0.3in, var -0.1in])
  coincident([circle2.center, line1.end])
  circle3 = circle(start = [var -0.17in, var -0.14in], center = [var -0.3in, var -0.1in])
  coincident([circle3.center, line1.end])
  circle4 = circle(start = [var 0.3in, var -0.04in], center = [var 0.3in, var 0.1in])
  coincident([circle4.center, line2.end])
  equalRadius([circle2, circle1])
  equalRadius([circle4, circle3])
  radius(circle1) == .25
  radius(circle4) == .17
  horizontalDistance([circle3.center, circle4.center]) == .75
  verticalDistance([circle3.center, circle4.center]) == .2
}
hide(sketch003)

// Sweep the pulmonary artery
region003 = region(segments = [sketch003.circle2])
  |> rotate(pitch = 45, global = true)
  |> sweep(path = clone(sketch002))
  |> appearance(color = "#0e23be")

// Sweep the aorta
region004 = region(segments = [sketch003.circle1])
  |> rotate(pitch = 45, global = true)
  |> sweep(path = sketch002)
  |> appearance(color = "#a60c0c")

// Model the sweep path for the pulmonary vein and the superior vena cava
sketch009 = sketch(on = XZ) {
  line1 = line(start = [var 0.8in, var 0in], end = [var 0.85in, var 0in])
  horizontal([line1.start, ORIGIN])
  horizontal([line1.end, ORIGIN])
  arc1 = arc(start = [var 1.77in, var -0.57in], end = [var 0.85in, var 0in], center = [var 0.85in, var -1.02in])
  coincident([line1.end, arc1.end])
  tangent([line1, arc1])
  arc2 = arc(start = [var 1.77in, var -0.57in], end = [var 2.72in, var -2.27in], center = [var 18.45in, var 7.67in])
  coincident([arc1.start, arc2.start])
  tangent([arc1, arc2])
  distance([line1.start, line1.end]) == .05
  horizontalDistance([ORIGIN, line1.start]) == .8
}

// Sketch the tube profile for the pulmonary vein, then sweep
sketch010 = sketch(on = offsetPlane(YZ, offset = 0.8)) {
  circle1 = circle(start = [var -0.92in, var -0.08in], center = [var -1.1in, var 0in])
  horizontal([circle1.center, ORIGIN])
  circle2 = circle(start = [var -0.9in, var -0.15in], center = [var -1.1in, var 0in])
  coincident([circle2.center, circle1.center])
  radius(circle2) == .25
  radius(circle1) == 0.2in
}
hide(sketch010)
region007 = region(segments = [sketch010.circle2])
sweep003 = sweep(region007, path = clone(sketch009))
  // Move the vein into position at the inlet bung
  |> rotate(pitch = 80)
  |> rotate(roll = 4, yaw = 2)
  |> translate(y = -.027, z = .08)
  |> appearance(color = "#a60c0c")

// Sketch the tube profile of the superior vena cava, then sweep
sketch011 = sketch(on = offsetPlane(YZ, offset = 0.8)) {
  circle1 = circle(start = [var 0.92in, var -0.08in], center = [var 1.1in, var 0in])
  horizontal([circle1.center, ORIGIN])
  circle2 = circle(start = [var 0.9in, var -0.15in], center = [var 1.1in, var 0in])
  coincident([circle2.center, circle1.center])
  radius(circle2) == .25
  radius(circle1) == 0.2in
}
hide(sketch011)
region0011 = region(segments = [sketch011.circle2])
sweep004 = sweep(region0011, path = sketch009)
  // Move it into position at the inlet bung
  |> rotate(pitch = 75)
  |> rotate(roll = -4, yaw = -4)
  |> translate(x = -.11, y = 0.17, z = .1)
  |> appearance(color = "#0e23be")
```

### stator.kcl

```kcl
// Stator

// Set units
@settings(defaultLengthUnit = in, kclVersion = 2.0)

// Sketch the PCB profile
sketch001 = sketch(on = offsetPlane(XZ, offset = -.26)) {
  circle1 = circle(start = [var 1.17in, var 0.8in], center = [var 0mm, var 0mm])
  coincident([circle1.center, ORIGIN])
  circle2 = circle(start = [var 0.36in, var 0.44in], center = [var 0in, var 0in])
  coincident([circle2.center, circle1.center])
}

// Sketch the profile of the stator windings
sketch002 = sketch(on = XZ) {
  line1 = line(start = [var -0.21in, var 1.22in], end = [var -0.15in, var 0.97in])
  line2 = line(start = [var 0.15in, var 0.97in], end = [var 0.21in, var 1.22in])
  line3 = line(start = [var 0in, var 0in], end = [var 0in, var 0.51in], construction = true)
  coincident([line3.start, ORIGIN])
  vertical([line3.end, ORIGIN])
  arc1 = arc(start = [var -0.15in, var 0.97in], end = [var -0.05in, var 0.9in], center = [var -0.05in, var 1in])
  coincident([line1.end, arc1.start])
  tangent([line1, arc1])
  arc2 = arc(start = [var 0.05in, var 0.9in], end = [var 0.15in, var 0.97in], center = [var 0.05in, var 1in])
  coincident([line2.start, arc2.end])
  tangent([line2, arc2])
  arc3 = arc(start = [var -0.05in, var 0.9in], end = [var 0.05in, var 0.9in], center = [var 0in, var 2.85in])
  coincident([arc3.start, arc1.end])
  coincident([arc2.start, arc3.end])
  tangent([arc2, arc3])
  arc4 = arc(start = [var -0.12in, var 1.35in], end = [var -0.21in, var 1.22in], center = [var -0.12in, var 1.25in])
  coincident([line1.start, arc4.end])
  tangent([line1, arc4])
  arc5 = arc(start = [var 0.21in, var 1.22in], end = [var 0.12in, var 1.35in], center = [var 0.12in, var 1.25in])
  coincident([line2.end, arc5.start])
  tangent([line2, arc5])
  arc6 = arc(start = [var 0.12in, var 1.35in], end = [var -0.12in, var 1.35in], center = [var 0in, var -1.7in])
  coincident([arc6.start, arc5.end])
  coincident([arc4.start, arc6.end])
  tangent([arc4, arc6])
  symmetric([arc5, arc4], axis = line3)
  symmetric([line2, line1], axis = line3)
  symmetric([arc2, arc1], axis = line3)
  tangent([arc3, arc1])
  angleDimension(lines = [line1, line2], sector = 2, labelPosition = [0in, 1.16in]) == 30
  tangent([arc5, arc6])
  verticalDistance([line3.start, arc2.center]) == 1
  horizontalDistance([arc1.center, arc2.center]) == .1
  verticalDistance([line3.start, arc5.center]) == 1.25
  radius(arc1) == .1
  equalRadius([arc4, arc1])
  arc7 = arc(start = [var -0.12in, var 1.45in], end = [var -0.31in, var 1.2in], center = [var -0.12in, var 1.25in])
  coincident([arc7.center, arc4.center])
  arc8 = arc(start = [var -0.24in, var 0.95in], end = [var -0.05in, var 0.8in], center = [var -0.05in, var 1in])
  coincident([arc8.center, arc1.center])
  arc9 = arc(start = [var 0.05in, var 0.8in], end = [var 0.24in, var 0.95in], center = [var 0.05in, var 1in])
  coincident([arc9.center, arc2.center])
  arc10 = arc(start = [var 0.31in, var 1.2in], end = [var 0.12in, var 1.45in], center = [var 0.12in, var 1.25in])
  coincident([arc10.center, arc5.center])
  line4 = line(start = [var -0.31in, var 1.2in], end = [var -0.24in, var 0.95in])
  coincident([line4.start, arc7.end])
  coincident([line4.end, arc8.start])
  line5 = line(start = [var 0.24in, var 0.95in], end = [var 0.31in, var 1.2in])
  coincident([line5.start, arc9.end])
  coincident([line5.end, arc10.start])
  line6 = line(start = [var -0.05in, var 0.8in], end = [var 0.05in, var 0.8in])
  coincident([line6.start, arc8.end])
  coincident([line6.end, arc9.start])
  line7 = line(start = [var -0.12in, var 1.45in], end = [var 0.12in, var 1.45in])
  coincident([line7.start, arc7.start])
  coincident([line7.end, arc10.end])
  symmetric([arc7, arc10], axis = line3)
  symmetric([line4, line5], axis = line3)
  symmetric([arc8, arc9], axis = line3)
  parallel([line4, line1])
  tangent([line4, arc7])
  tangent([line7, arc7])
  tangent([line7, arc10])
  tangent([line5, arc10])
  tangent([line5, arc9])
  tangent([line6, arc9])
  tangent([line6, arc8])
  equalRadius([arc8, arc7])
  radius(arc8) == 0.2
}
hide(sketch002)

// Select and extrude the stator cores
region001 = region(segments = [sketch002.line1, sketch002.arc1])
extrude001 = extrude(region001, length = .35, symmetric = true)

hide(sketch002)

// Select and extrude the stator windings
region002 = region(segments = [sketch002.line4, sketch002.arc8])
extrude002 = extrude(region002, length = .3, symmetric = true)
  |> appearance(color = "#d54b10")

// Pattern both elements
pattern001 = patternCircular3d(
  [extrude001, extrude002],
  instances = 12,
  axis = Y,
  center = [0, 0, 0],
)
hidden001 = hide(sketch001)

// Extrude the motor board
region003 = region(segments = [sketch001.circle1])
extrude003 = extrude(region003, length = .1)
  |> appearance(color = "#115D33")
```

Source URL: https://zoo.dev/aquarium/multi-axis-robot
Title: Robot Arm

# Robot Arm

A 4 axis robotic arm for industrial use. These machines can be used for assembly, packaging, organization of goods, and quality inspection processes

- Page: /aquarium/multi-axis-robot
- Legacy docs page: /docs/kcl-samples/multi-axis-robot
- Preview image: /kcl-samples/screenshots/multi-axis-robot.png
- Categories: Robotics & Automation, Industrial & Manufacturing

## Files

### main.kcl

```kcl
// Robot Arm
// A 4 axis robotic arm for industrial use. These machines can be used for assembly, packaging, organization of goods, and quality inspection processes
// Categories: Robotics & Automation; Industrial & Manufacturing

// Set Units
@settings(defaultLengthUnit = in, kclVersion = 1.0)

// Import parts
import "robot-arm-base.kcl" as robotArmBase
import "robot-rotating-base.kcl" as rotatingBase
import "robot-arm-j2.kcl" as j2RobotArm
import "robot-arm-j3.kcl" as j3RobotArm
```

### globals.kcl

```kcl
// Global constants for the multi-axis robot

// Define Units
@settings(defaultLengthUnit = in, kclVersion = 1.0)

// Export constants
export axisJ4 = 25deg
export axisJ3 = 60deg
export axisJ2 = 110deg
export axisJ1 = 80deg

export basePlateRadius = 5.5
export basePlateThickness = 0.5
export baseChamfer = 2
export baseHeight = 5

export axisJ2ArmLength = 31
export axisJ2ArmWidth = 4
export axisJ2ArmThickness = 2.5
export axisJ2BasePivotX = axisJ2ArmWidth / 2 - 0.25
export axisJ2BasePivotY = baseHeight + 3
export axisJ2EndPivotX = axisJ2BasePivotX + axisJ2ArmLength * cos(axisJ2)
export axisJ2EndPivotY = axisJ2BasePivotY + axisJ2ArmLength * sin(axisJ2)
export axisJ2HubRadius = axisJ2ArmWidth / 2 - 0.1

export axisJ3C = axisJ3 - 180deg + axisJ2
export axisJ3CArmLength = 20
export axisJ3CArmWidth = 3.75
export axisJ3CArmThickness = 2.5
export axisJ3BasePivotX = axisJ2EndPivotX
export axisJ3BasePivotY = axisJ2EndPivotY
export axisJ3EndPivotX = axisJ3BasePivotX + axisJ3CArmLength * cos(axisJ3C)
export axisJ3EndPivotY = axisJ3BasePivotY + axisJ3CArmLength * sin(axisJ3C)
export axisJ3HubRadius = axisJ3CArmWidth / 2

export clawFingerLength = 6.8
export clawFingerWidth = 1.0
export clawFingerThickness = 1.5
export clawOpening = 1.8
export clawRootOffset = 0.35
export clawTipBackset = 1.0
export clawTipInset = 0.35
export clawOuterTipDrop = 0.25

export plane001 = {
  origin = [0.0, 0.0, baseHeight - 1.5 + 0.1],
  xAxis = [1.0, 0.0, 0.0],
  yAxis = [0.0, 1.0, 0.0]
}

export plane002 = {
  origin = [0.0, 0.0, 0.0],
  xAxis = [sin(axisJ1): in, cos(axisJ1): in, 0.0],
  yAxis = [0.0, 0.0, 1.0]
}

export plane003 = {
  origin = [-0.1, 0.0, 0.0],
  xAxis = [sin(axisJ1): in, cos(axisJ1): in, 0.0],
  yAxis = [0.0, 0.0, 1.0]
}
```

### robot-arm-base.kcl

```kcl
// Robot Arm Base

// Set Units
@settings(defaultLengthUnit = in, kclVersion = 2.0)

// Import Constants
import * from "globals.kcl"

// Base Plate
sketch004 = sketch(on = XY) {
  line1 = line(start = [var -5.5in, var -5.5in], end = [var 5.5in, var -5.5in])
  line2 = line(start = [var 5.5in, var -5.5in], end = [var 5.5in, var 5.5in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 5.5in, var 5.5in], end = [var -5.5in, var 5.5in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -5.5in, var 5.5in], end = [var -5.5in, var -5.5in])
  coincident([line3.end, line4.start])
  line5 = line(start = [var 0in, var 0in], end = [var 4.43in, var 2.99in], construction = true)
  coincident([line5.start, ORIGIN])
  line6 = line(start = [var 0in, var 0in], end = [var 2.99in, var 4.43in], construction = true)
  coincident([line6.start, line5.start])
  line7 = line(start = [var 0in, var 0in], end = [var -2.99in, var 4.43in], construction = true)
  coincident([line7.start, line6.start])
  line8 = line(start = [var 0in, var 0in], end = [var -4.43in, var 2.99in], construction = true)
  coincident([line8.start, line7.start])
  line9 = line(start = [var 0in, var 0in], end = [var -4.43in, var -2.99in], construction = true)
  coincident([line9.start, line8.start])
  line10 = line(start = [var 0in, var 0in], end = [var -2.99in, var -4.43in], construction = true)
  coincident([line10.start, line9.start])
  line11 = line(start = [var 0in, var 0in], end = [var 2.99in, var -4.43in], construction = true)
  coincident([line11.start, line10.start])
  line12 = line(start = [var 0in, var 0in], end = [var 4.43in, var -2.99in], construction = true)
  coincident([line12.start, line11.start])
  equalLength([
    line11,
    line12,
    line5,
    line6,
    line7,
    line8,
    line9,
    line10
  ])
  line13 = line(start = [var 0in, var 0in], end = [var 4.86in, var 0in], construction = true)
  coincident([line13.start, line8.start])
  horizontal([line13.end, ORIGIN])
  line14 = line(start = [var 0in, var 0in], end = [var -4.41in, var 0in], construction = true)
  coincident([line14.start, line10.start])
  horizontal([line14.end, ORIGIN])
  horizontal(line14)
  horizontal(line13)
  angleDimension(lines = [line13, line5], sector = 1) == 34
  line15 = line(start = [var 0in, var 0in], end = [var 0in, var 4.46in], construction = true)
  coincident([line15.start, line5.start])
  vertical([line15.end, ORIGIN])
  line16 = line(start = [var 0in, var 0in], end = [var 0in, var -3.56in], construction = true)
  coincident([line16.start, line15.start])
  vertical([line16.end, ORIGIN])
  vertical(line16)
  vertical(line15)
  angleDimension(lines = [line6, line15], sector = 1) == 34
  angleDimension(lines = [line15, line7], sector = 1) == 34
  angleDimension(lines = [line8, line14], sector = 1) == 34
  angleDimension(lines = [line14, line9], sector = 1) == 34
  angleDimension(lines = [line10, line16], sector = 1) == 34
  angleDimension(lines = [line16, line11], sector = 1) == 34
  angleDimension(lines = [line12, line13], sector = 1) == 34
  distance([line12.start, line12.end]) == 5.35
  circle1 = circle(start = [var 4.54in, var 2.61in], center = [var 4.43in, var 2.99in])
  coincident([circle1.center, line5.end])
  circle2 = circle(start = [var 3in, var 4.04in], center = [var 2.99in, var 4.43in])
  coincident([circle2.center, line6.end])
  circle3 = circle(start = [var -2.6in, var 4.34in], center = [var -2.99in, var 4.43in])
  coincident([circle3.center, line7.end])
  circle4 = circle(start = [var -4.32in, var 2.61in], center = [var -4.43in, var 2.99in])
  coincident([circle4.center, line8.end])
  circle5 = circle(start = [var -4.3in, var -3.37in], center = [var -4.43in, var -2.99in])
  coincident([circle5.center, line9.end])
  circle6 = circle(start = [var -2.63in, var -4.6in], center = [var -2.99in, var -4.43in])
  coincident([circle6.center, line10.end])
  circle7 = circle(start = [var 3.35in, var -4.62in], center = [var 2.99in, var -4.43in])
  coincident([circle7.center, line11.end])
  circle8 = circle(start = [var 4.59in, var -3.36in], center = [var 4.43in, var -2.99in])
  coincident([circle8.center, line12.end])
  equalRadius([
    circle8,
    circle7,
    circle6,
    circle5,
    circle4,
    circle3,
    circle2,
    circle1
  ])
  radius(circle2) == .4
}
region001 = region(segments = [sketch004.line1, sketch004.line2])
hidden001 = hide(sketch004)
sketch001 = extrude(region001, length = basePlateThickness)

// Base Motor for actuating first joint
sketch002 = sketch(on = faceOf(sketch001, face = END)) {
  circle1 = circle(start = [var 4in, var 0in], center = [var 0in, var 0in])
}
region002 = region(segments = [sketch002.circle1])
extrude002 = extrude(region002, length = baseHeight - basePlateThickness - 1.5)

sketch003 = sketch(on = faceOf(extrude002, face = END)) {
  circle1 = circle(start = [var 0.5in, var 0in], center = [var 0in, var 0in])
}
region003 = region(segments = [sketch003.circle1])
extrude003 = extrude(region003, length = 1)
  |> appearance(color = "#754110", roughness = 90, metalness = 90)
chamfer001 = chamfer(
  sketch001,
  tags = [
    getCommonEdge(faces = [
      region001.tags.line1,
      region001.tags.line2
    ]),
    getCommonEdge(faces = [
      region001.tags.line2,
      region001.tags.line3
    ]),
    getCommonEdge(faces = [
      region001.tags.line3,
      region001.tags.line4
    ]),
    getCommonEdge(faces = [
      region001.tags.line4,
      region001.tags.line1
    ])
  ],
  length = 1,
)
```

### robot-arm-j2.kcl

```kcl
// J2 Axis for Robot Arm

// Set Units
@settings(defaultLengthUnit = in, kclVersion = 1.0)

// Import Constants
import * from "globals.kcl"

// Create Body of J2 Robot Arm
sketch011 = sketch(on = plane003) {
  arc1 = arc(start = [var -0.13in, var 7.32in], end = [var 3.63in, var 8.68in], center = [var 1.75in, var 8in])
  line2 = line(start = [var 3.63in, var 8.68in], end = [var -6.97in, var 37.81in])
  coincident([arc1.end, line2.start])
  arc3 = arc(start = [var -6.97in, var 37.81in], end = [var -10.73in, var 36.45in], center = [var -8.85in, var 37.13in])
  coincident([line2.end, arc3.start])
  line4 = line(start = [var -10.73in, var 36.45in], end = [var -0.13in, var 7.32in])
  coincident([arc3.end, line4.start])
}
region001 = region(segments = [sketch011.arc1, sketch011.line2])
extrude011 = extrude(region001, length = -axisJ2ArmThickness)

sketch012 = sketch(on = faceOf(extrude011, face = START)) {
  circle1 = circle(start = [var 0.15in, var 8in], center = [var -1.75in, var 8in])
}

region002 = region(segments = [sketch012.circle1])
extrude012 = extrude(region002, length = 0.15)

sketch013 = sketch(on = faceOf(extrude011, face = START)) {
  circle1 = circle(start = [var 10.75in, var 37.13in], center = [var 8.85in, var 37.13in])
}

region003 = region(segments = [sketch013.circle1])
extrude013 = extrude(region003, length = 1)

sketch016 = sketch(on = faceOf(extrude011, face = END)) {
  circle1 = circle(start = [var -8.55in, var 37.13in], center = [var -8.85in, var 37.13in])
}

region005 = region(segments = [sketch016.circle1])
extrude(region005, length = 1)
  |> appearance(color = "#454545", metalness = 90, roughness = 90)
```

### robot-arm-j3.kcl

```kcl
// J3 Robot Arm

// Set Units
@settings(defaultLengthUnit = in, kclVersion = 1.0)

// Import Constants
import * from "globals.kcl"

// Create Body of J3 Robot Arm
sketch017 = sketch(on = plane002) {
  arc1 = arc(start = [var -8.53in, var 38.98in], end = [var -9.18in, var 35.28in], center = [var -8.85in, var 37.13in])
  line2 = line(start = [var -9.18in, var 35.28in], end = [var 10.52in, var 31.81in])
  coincident([arc1.end, line2.start])
  arc3 = arc(start = [var 11.17in, var 35.5in], end = [var 10.52in, var 31.81in], center = [var 10.84in, var 33.66in])
  coincident([line2.end, arc3.end])
  line4 = line(start = [var 11.17in, var 35.5in], end = [var -8.53in, var 38.98in])
  coincident([arc3.start, line4.start])
  coincident([arc1.start, line4.end])
}
region001 = region(point = [-10.7000292in, 37.454302in], sketch = sketch017)
extrude017 = extrude(region001, length = axisJ3CArmThickness)

sketch018 = sketch(on = faceOf(extrude017, face = END)) {
  circle1 = circle(start = [var -7in, var 37.13in], center = [var -8.85in, var 37.13in])
}

region002 = region(segments = [sketch018.circle1])
extrude018 = extrude(region002, length = 0.15)

// On the J3 Robot Arm Body, Create Mounting Clevis for Grabber Claw
sketch020 = sketch(on = faceOf(extrude017, face = START)) {
  circle1 = circle(start = [var -8.97in, var 33.66in], center = [var -10.84in, var 33.66in])
}
region003 = region(segments = [sketch020.circle1])
extrude020 = extrude(region003, length = -0.5, method = NEW)

sketch021 = sketch(on = faceOf(extrude017, face = END)) {
  circle1 = circle(start = [var 12.71in, var 33.66in], center = [var 10.84in, var 33.66in])
}

region004 = region(segments = [sketch021.circle1])
extrude021 = extrude(region004, length = -0.5, method = NEW)

// Define Grabber Claw Constants
grabberLength = 7

sketch022 = sketch(on = faceOf(extrude021, face = START)) {
  circle1 = circle(start = [var 0.1in, var 0in], center = [var 0in, var 0in])
}

region005 = region(segments = [sketch022.circle1])
extrude022 = extrude(region005, length = -0.01)

// Build Upper Claw Finger
sketch023 = sketch(on = faceOf(extrude022, face = START)) {
  line1 = line(start = [var 10.84in, var 33.66in], end = [var 12.57in, var 33.35in])
  arc2 = arc(start = [var 16.55in, var 32.65in], end = [var 12.57in, var 33.35in], center = [var 14.35in, var 31.85in])
  coincident([line1.end, arc2.end])
  line3 = line(start = [var 16.55in, var 32.65in], end = [var 17.7in, var 32.45in])
  coincident([arc2.start, line3.start])
  line4 = line(start = [var 17.7in, var 32.45in], end = [var 16.64in, var 34.15in])
  coincident([line3.end, line4.start])
  line5 = line(start = [var 16.64in, var 34.15in], end = [var 14.9in, var 35.15in])
  coincident([line4.end, line5.start])
  line6 = line(start = [var 14.9in, var 35.15in], end = [var 12.61in, var 34.74in])
  coincident([line5.end, line6.start])
  line7 = line(start = [var 12.61in, var 34.74in], end = [var 10.84in, var 33.66in])
  coincident([line6.end, line7.start])
}

region006 = region(segments = [sketch023.line1, sketch023.arc2])
extrude023 = extrude(region006, length = -1.5, method = NEW)

// Build Lower Claw Finger
sketch024 = sketch(on = faceOf(extrude022, face = START)) {
  line1 = line(start = [var 10.84in, var 33.66in], end = [var 12.57in, var 33.35in])
  arc2 = arc(start = [var 12.57in, var 33.35in], end = [var 16.55in, var 32.65in], center = [var 14.76in, var 34.15in])
  coincident([line1.end, arc2.start])
  line3 = line(start = [var 16.55in, var 32.65in], end = [var 17.7in, var 32.45in])
  coincident([arc2.end, line3.start])
  line4 = line(start = [var 17.7in, var 32.45in], end = [var 16.12in, var 31.22in])
  coincident([line3.end, line4.start])
  line5 = line(start = [var 16.12in, var 31.22in], end = [var 14.15in, var 30.87in])
  coincident([line4.end, line5.start])
  line6 = line(start = [var 14.15in, var 30.87in], end = [var 12.13in, var 32.04in])
  coincident([line5.end, line6.start])
  line7 = line(start = [var 12.13in, var 32.04in], end = [var 10.84in, var 33.66in])
  coincident([line6.end, line7.start])
}

region007 = region(segments = [sketch024.line1, sketch024.arc2])
extrude024 = extrude(region007, length = -1.5, method = NEW)
appearance(
  [
    extrude020,
    extrude021,
    extrude023,
    extrude024
  ],
  color = "#6572b3",
  metalness = 90,
  roughness = 90,
)
```

### robot-rotating-base.kcl

```kcl
// Robot Rotating Base

// Set Units
@settings(defaultLengthUnit = in, kclVersion = 1.0)

// Import Constants
import * from "globals.kcl"

sketch005 = sketch(on = plane001) {
  circle1 = circle(start = [var 3.9, var 0], center = [var 0, var 0])
  coincident([circle1.center, [0, 0]])
  diameter(circle1) == 7.8
}
region001 = region(segments = [sketch005.circle1])
extrude005 = extrude(region001, length = 1.5 - 0.1)
  |> appearance(color = "#4f7d54", metalness = 90, roughness = 90)

sketch006 = sketch(on = plane002) {
  line1 = line(start = [var 3.5, var 5], end = [var 4.38, var 6.52])
  arc2 = arc(start = [var 4.38, var 6.52], end = [var -0.82, var 9.52], center = [var 1.78, var 8.02])
  line3 = line(start = [var -0.82, var 9.52], end = [var -3.43, var 5])
  line4 = line(start = [var -3.43, var 5], end = [var 3.5, var 5])
  coincident([line1.end, arc2.start])
  coincident([arc2.end, line3.start])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
}
region002 = region(segments = [sketch006.line1, sketch006.arc2])
extrude006 = extrude(region002, length = 1)

sketch007 = sketch(on = faceOf(extrude006, face = END)) {
  circle1 = circle(start = [var 4.5, var 8], center = [var 1.75, var 8])
  coincident([
    circle1.center,
    [axisJ2BasePivotX, axisJ2BasePivotY]
  ])
  diameter(circle1) == 5.5
}
region003 = region(segments = [sketch007.circle1])
extrude007 = extrude(region003, length = 1.5)

sketch009 = sketch(on = faceOf(extrude007, face = END)) {
  circle1 = circle(start = [var 2.25, var 8], center = [var 1.75, var 8])
  coincident([
    circle1.center,
    [axisJ2BasePivotX, axisJ2BasePivotY]
  ])
  diameter(circle1) == 1
}
region004 = region(segments = [sketch009.circle1])
extrude009 = extrude(region004, length = 0.15)
  |> appearance(color = "#4f7d54", metalness = 90, roughness = 90)

sketch010 = sketch(on = plane002) {
  circle1 = circle(start = [var 2.05, var 8], center = [var 1.75, var 8])
  coincident([
    circle1.center,
    [axisJ2BasePivotX, axisJ2BasePivotY]
  ])
  diameter(circle1) == 0.6
}
region005 = region(segments = [sketch010.circle1])
extrude(region005, length = -1)
```

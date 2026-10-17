Source URL: https://zoo.dev/aquarium/car-wheel-assembly
Title: Car Wheel Assembly

# Car Wheel Assembly

A car wheel assembly with a rotor, tire, and lug nuts.

- Page: /aquarium/car-wheel-assembly
- Legacy docs page: /docs/kcl-samples/car-wheel-assembly
- Preview image: /kcl-samples/screenshots/car-wheel-assembly.png
- Categories: Automotive & Transportation, Mechanical Components

## Files

### main.kcl

```kcl
// Car Wheel Assembly
// A car wheel assembly with a rotor, tire, and lug nuts.
// Categories: Automotive & Transportation; Mechanical Components

// Set units and version
@settings(defaultLengthUnit = in, kclVersion = 2.0)

// Import parameters
import * from "parameters.kcl"

// Import all parts into the assembly file
import "brake-rotor.kcl" as brakeRotor
import "car-tire.kcl" as carTire
import "car-wheel.kcl" as carWheel
import "lug-nut.kcl" as lugNut

lugNut
  |> patternCircular3d(instances = lugCount, axis = Y, center = [0, 0, 0])
```

### brake-rotor.kcl

```kcl
// Brake Rotor
// Vented rotor with a bell and rear friction disc.

// Set units and version
@settings(defaultLengthUnit = in, kclVersion = 2.0)

// Import parameters
import * from "parameters.kcl"

bellOuterFaceOffset = 1.66281in
frontDiscInnerFaceOffset = bellOuterFaceOffset - tDiscHalf
rearDiscOuterFaceOffset = frontDiscInnerFaceOffset - tVent
rotorColor = "#f0d77a"

bellProfileSketch = sketch(on = -XY) {
  line1 = line(start = [var 1.5in, var 0in], end = [var 1.5in, var -0.2in])
  line2 = line(start = [var 1.5in, var -0.2in], end = [var 3.75in, var -0.2in])
  line3 = line(start = [var 3.75in, var -0.2in], end = [var 3.93418in, var 1.3in])
  arc1 = arc(start = [var 4.13343in, var 1.28781in], end = [var 3.93418in, var 1.3in], center = [var 4.03343in, var 1.28781in])
  line4 = line(start = [var 4.13in, var 1.29in], end = [var 6.73in, var 1.3in])
  line5 = line(start = [var 6.73in, var 1.67in], end = [var 3.73in, var 1.66in])
  line6 = line(start = [var 3.73343in, var 1.66281in], end = [var 3.52925in, var 0in])
  line7 = line(start = [var 3.52in, var 0.01in], end = [var 1.49in, var 0.01in])
  line8 = line(start = [var 6.73in, var 1.3in], end = [var 6.73in, var 1.67in])
  line9 = line(start = [var 0in, var 0in], end = [var 0in, var 2.32in], construction = true)
  coincident([line1.end, line2.start])
  coincident([line2.end, line3.start])
  coincident([line3.end, arc1.end])
  coincident([arc1.start, line4.start])
  coincident([line4.end, line8.start])
  coincident([line8.end, line5.start])
  coincident([line5.end, line6.start])
  coincident([line6.end, line7.start])
  coincident([line7.end, line1.start])
  coincident([line9.start, ORIGIN])
  vertical(line8)
  horizontal(line4)
  horizontal(line5)
  vertical([line9.end, ORIGIN])
  horizontalDistance([line9.start, line8.end]) == rotorDiameter / 2
  distance([line8.start, line8.end]) == tDiscHalf
}

bellRegion = region(segments = [
  bellProfileSketch.line1,
  bellProfileSketch.line2
])
hide([bellProfileSketch])

lugHoleSketch = sketch(on = XZ) {
  circle1 = circle(start = [var -1.98004in, var 0in], center = [var -2.25in, var 0in])
  horizontalDistance([ORIGIN, circle1.center]) == -(lugSpacing / 2)
  verticalDistance([ORIGIN, circle1.center]) == 0in
  diameter(circle1) == lugThreadDiameter
}

lugHoleRegion = region(segments = [lugHoleSketch.circle1])
hide([lugHoleSketch])

bell = revolve(bellRegion, axis = Y)
  |> subtract(tools = patternCircular3d(
       extrude(
         lugHoleRegion,
         length = tBell * 4,
         symmetric = true,
         method = NEW,
       ),
       instances = lugCount,
       axis = Y,
       center = [0, 0, 0],
     ))
  |> appearance(color = rotorColor, metalness = 70, roughness = 30)

ventPlane = offsetPlane(XZ, offset = -frontDiscInnerFaceOffset - tDiscHalf)
ventSketch = sketch(on = ventPlane) {
  line1 = line(start = [var -0.125in, var 3.64in], end = [var 0.125in, var 3.64in])
  line2 = line(start = [var 0.125in, var 3.64in], end = [var 0.125in, var 6in])
  line3 = line(start = [var 0.125in, var 6in], end = [var -0.125in, var 6in])
  line4 = line(start = [var -0.125in, var 6in], end = [var -0.125in, var 3.64in])
  coincident([line1.end, line2.start])
  coincident([line2.end, line3.start])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
  horizontal(line1)
  vertical(line2)
  horizontal(line3)
  vertical(line4)
  horizontalDistance([ORIGIN, line1.start]) == -(wVent / 2)
  verticalDistance([ORIGIN, line1.start]) == rotorDiameter / 2 - hFrictionSurface
  horizontalDistance([line1.start, line1.end]) == wVent
  verticalDistance([line2.start, line2.end]) == hFrictionSurface
}

ventRegion = region(segments = [ventSketch.line1, ventSketch.line2])
hide([ventSketch])

ventSet = patternCircular3d(
  extrude(ventRegion, length = -tVent, method = NEW),
  instances = nVentBosses,
  axis = Y,
  center = [0, 0, 0],
)
  |> appearance(color = rotorColor, metalness = 70, roughness = 30)

rearDiscPlane = offsetPlane(XZ, offset = -frontDiscInnerFaceOffset - tDiscHalf - tVent)
rearDiscSketch = sketch(on = rearDiscPlane) {
  circle1 = circle(start = [var 6in, var 0in], center = [var 0in, var 0in])
  circle2 = circle(start = [var 3.64in, var 0in], center = [var 0in, var 0in])
  coincident([circle1.center, ORIGIN])
  coincident([circle2.center, circle1.center])
  diameter(circle1) == rotorDiameter
  diameter(circle2) == rotorDiameter - (2 * hFrictionSurface)
}

rearDiscRegion = region(segments = [rearDiscSketch.circle1])
rearDisc = extrude(rearDiscRegion, length = -tDiscHalf, method = NEW)
  |> appearance(color = rotorColor, metalness = 70, roughness = 30)
hide([rearDiscSketch])

rotor = [bell, ventSet, rearDisc]
```

### car-tire.kcl

```kcl
// Tire
// Solver sketch version of the full tire profile.

// Set units and version
@settings(defaultLengthUnit = in, kclVersion = 2.0)

// Import parameters
import * from "parameters.kcl"

tireSketch = sketch(on = XY) {
  line1 = line(start = [var 12.01in, var 0in], end = [var 12.01in, var 2.51in])
  arc1 = arc(start = [var 12.01in, var 2.75in], end = [var 12.01in, var 2.51in], center = [var 12.01in, var 2.63in])
  line2 = line(start = [var 12.01in, var 2.75in], end = [var 12.01in, var 4.02in])
  arc2 = arc(start = [var 12.01in, var 4.02in], end = [var 11.1in, var 5.02in], center = [var 11.01in, var 4.02in])
  arc3 = arc(start = [var 11.1in, var 5.02in], end = [var 9in, var 4.75in], center = [var 10.66in, var 0.05in])
  line3 = line(start = [var 9in, var 4.75in], end = [var 9in, var 4.51in])
  line4 = line(start = [var 9in, var 4.51in], end = [var 9.09in, var 4.55in])
  arc4 = arc(start = [var 11.01in, var 4.18in], end = [var 9.09in, var 4.55in], center = [var 9.74in, var 2.72in])
  line5 = line(start = [var 11.01in, var 4.18in], end = [var 11.01in, var 0in])
  line6 = line(start = [var 11.01in, var 0in], end = [var 11.01in, var -4.18in])
  arc5 = arc(start = [var 9.09in, var -4.55in], end = [var 11.01in, var -4.18in], center = [var 9.74in, var -2.72in])
  line7 = line(start = [var 9.09in, var -4.55in], end = [var 9in, var -4.51in])
  line8 = line(start = [var 9in, var -4.51in], end = [var 9in, var -4.75in])
  arc6 = arc(start = [var 9in, var -4.75in], end = [var 11.1in, var -5.02in], center = [var 10.66in, var -0.05in])
  arc7 = arc(start = [var 11.1in, var -5.02in], end = [var 12.01in, var -4.02in], center = [var 11.01in, var -4.02in])
  line9 = line(start = [var 12.01in, var -4.02in], end = [var 12.01in, var -2.75in])
  arc8 = arc(start = [var 12.01in, var -2.51in], end = [var 12.01in, var -2.75in], center = [var 12.01in, var -2.63in])
  line10 = line(start = [var 12.01in, var -2.51in], end = [var 12.01in, var 0in])
  coincident([line1.end, arc1.end])
  coincident([arc1.start, line2.start])
  coincident([line2.end, arc2.start])
  coincident([arc2.end, arc3.start])
  coincident([arc3.end, line3.start])
  coincident([line3.end, line4.start])
  coincident([line4.end, arc4.end])
  coincident([arc4.start, line5.start])
  coincident([line5.end, line6.start])
  coincident([line6.end, arc5.end])
  coincident([arc5.start, line7.start])
  coincident([line7.end, line8.start])
  coincident([line8.end, arc6.start])
  coincident([arc6.end, arc7.start])
  coincident([arc7.end, line9.start])
  coincident([line9.end, arc8.end])
  coincident([arc8.start, line10.start])
  coincident([line10.end, line1.start])
}

tireRegion = region(segments = [tireSketch.line1, tireSketch.arc1])
tireBody = revolve(tireRegion, axis = Y)
hide([tireSketch])

carTire = tireBody
  |> appearance(color = "#0a0a0a", roughness = 20)
  |> translate(y = -tBell + offset, global = true)
```

### car-wheel.kcl

```kcl
// Car Wheel
// A sports car wheel with a circular lug pattern and spokes.

// Set units and version
@settings(defaultLengthUnit = in, kclVersion = 2.0)

// Import parameters
import * from "parameters.kcl"

lugMountsSketch = sketch(on = XY) {
  line1 = line(start = [var 2.25in, var 0in], end = [var 2.51997in, var 0in])
  line2 = line(start = [var 2.51997in, var 0in], end = [var 2.51997in, var -1.05in])
  line3 = line(start = [var 2.51997in, var -1.05in], end = [var 2.72244in, var -1.05in])
  line4 = line(start = [var 2.72244in, var -1.05in], end = [var 2.72244in, var -2.3in])
  line5 = line(start = [var 2.72244in, var -2.3in], end = [var 2.25in, var -2.3in])
  line6 = line(start = [var 2.25in, var -2.3in], end = [var 2.25in, var 0in])
  coincident([line1.end, line2.start])
  coincident([line2.end, line3.start])
  coincident([line3.end, line4.start])
  coincident([line4.end, line5.start])
  coincident([line5.end, line6.start])
  coincident([line6.end, line1.start])
}
lugMountsRegion = region(segments = [
  lugMountsSketch.line1,
  lugMountsSketch.line2
])
lugMounts = revolve(lugMountsRegion, axis = lugMountsSketch.line6)
hide([lugMountsSketch])

lugMountPattern = patternCircular3d(
  lugMounts,
  instances = lugCount,
  axis = [0, -1, 0],
  center = [0, 0, 0],
)

wheelCenterSketch = sketch(on = XY) {
  line1 = line(start = [var 1.5in, var -0.2in], end = [var 1.5in, var -0.95in])
  line2 = line(start = [var 1.5in, var -0.95in], end = [var 0in, var -0.95in])
  line3 = line(start = [var 0in, var -0.95in], end = [var 0in, var -1.45in])
  arc1 = arc(start = [var 0in, var -1.45in], end = [var 1.33877in, var -1.21445in], center = [var 0in, var 2.46304in])
  line4 = line(start = [var 1.33877in, var -1.21445in], end = [var 2.09302in, var -1.21445in])
  arc2 = arc(start = [var 2.58548in, var -1.44409in], end = [var 2.09302in, var -1.21445in], center = [var 2.09302in, var -1.85731in])
  arc3 = arc(start = [var 2.58548in, var -1.44409in], end = [var 2.85806in, var -1.63495in], center = [var 3.07794in, var -1.03087in])
  line5 = line(start = [var 2.85806in, var -1.63495in], end = [var 3.32428in, var -0.2in])
  line6 = line(start = [var 3.32428in, var -0.2in], end = [var 1.5in, var -0.2in])
  coincident([line1.end, line2.start])
  coincident([line2.end, line3.start])
  coincident([line3.end, arc1.start])
  coincident([arc1.end, line4.start])
  coincident([line4.end, arc2.end])
  coincident([arc2.start, arc3.start])
  coincident([arc3.end, line5.start])
  coincident([line5.end, line6.start])
  coincident([line6.end, line1.start])
}
wheelCenterRegion = region(segments = [
  wheelCenterSketch.line1,
  wheelCenterSketch.line2
])
wheelCenter = revolve(wheelCenterRegion, axis = Y)
  |> subtract(tools = lugMountPattern)
hide([wheelCenterSketch])

rimSketch = sketch(on = XY) {
  line1 = line(start = [var 9in, var -5.3437in], end = [var 9in, var -3.9187in])
  line2 = line(start = [var 9in, var -3.9187in], end = [var 8.7625in, var -3.6812in])
  line3 = line(start = [var 8.7625in, var -3.6812in], end = [var 8.7625in, var -1.3062in])
  line4 = line(start = [var 8.7625in, var -1.3062in], end = [var 9in, var -1.0687in])
  line5 = line(start = [var 9in, var -1.0687in], end = [var 9in, var 4.1563in])
  line6 = line(start = [var 9in, var 4.1563in], end = [var 9.475in, var 4.2513in])
  line7 = line(start = [var 9.475in, var 4.2513in], end = [var 9.475in, var 4.4888in])
  line8 = line(start = [var 9.475in, var 4.4888in], end = [var 9.285in, var 4.4888in])
  line9 = line(start = [var 9.285in, var 4.4888in], end = [var 9.285in, var 4.3938in])
  line10 = line(start = [var 9.285in, var 4.3938in], end = [var 8.81in, var 4.2988in])
  line11 = line(start = [var 8.81in, var 4.2988in], end = [var 8.81in, var -0.9262in])
  line12 = line(start = [var 8.81in, var -0.9262in], end = [var 8.5725in, var -1.1637in])
  line13 = line(start = [var 8.5725in, var -1.1637in], end = [var 8.5725in, var -2.1137in])
  line14 = line(start = [var 8.5725in, var -2.1137in], end = [var 7.9075in, var -2.35577in])
  line15 = line(start = [var 7.9075in, var -2.35577in], end = [var 7.9075in, var -2.55577in])
  line16 = line(start = [var 7.9075in, var -2.55577in], end = [var 8.5725in, var -3.22077in])
  line17 = line(start = [var 8.5725in, var -3.22077in], end = [var 8.5725in, var -3.83827in])
  line18 = line(start = [var 8.5725in, var -3.83827in], end = [var 8.81in, var -4.07577in])
  line19 = line(start = [var 8.81in, var -4.07577in], end = [var 8.81in, var -5.50077in])
  line20 = line(start = [var 8.81in, var -5.50077in], end = [var 9.285in, var -5.59577in])
  line21 = line(start = [var 9.285in, var -5.59577in], end = [var 9.285in, var -5.69077in])
  line22 = line(start = [var 9.285in, var -5.69077in], end = [var 9.475in, var -5.69077in])
  line23 = line(start = [var 9.475in, var -5.69077in], end = [var 9.475in, var -5.45327in])
  line24 = line(start = [var 9.475in, var -5.45327in], end = [var 9in, var -5.3437in])
  coincident([line1.end, line2.start])
  coincident([line2.end, line3.start])
  coincident([line3.end, line4.start])
  coincident([line4.end, line5.start])
  coincident([line5.end, line6.start])
  coincident([line6.end, line7.start])
  coincident([line7.end, line8.start])
  coincident([line8.end, line9.start])
  coincident([line9.end, line10.start])
  coincident([line10.end, line11.start])
  coincident([line11.end, line12.start])
  coincident([line12.end, line13.start])
  coincident([line13.end, line14.start])
  coincident([line14.end, line15.start])
  coincident([line15.end, line16.start])
  coincident([line16.end, line17.start])
  coincident([line17.end, line18.start])
  coincident([line18.end, line19.start])
  coincident([line19.end, line20.start])
  coincident([line20.end, line21.start])
  coincident([line21.end, line22.start])
  coincident([line22.end, line23.start])
  coincident([line23.end, line24.start])
  coincident([line24.end, line1.start])
}
rimRegion = region(segments = [rimSketch.line1, rimSketch.line2])
rim = revolve(rimRegion, axis = Y)
hide([rimSketch])

spokeSideSketch = sketch(on = XY) {
  line1 = line(start = [var 2.85806in, var -1.63495in], end = [var 3.32428in, var -0.2in])
  line2 = line(start = [var 3.32428in, var -0.2in], end = [var 3.40908in, var -0.25299in])
  arc1 = arc(start = [var 3.40908in, var -0.25299in], end = [var 7.9075in, var -2.35577in], center = [var 14.2831in, var 17.153in])
  line3 = line(start = [var 7.9075in, var -2.35577in], end = [var 7.9075in, var -2.55577in])
  line4 = line(start = [var 7.9075in, var -2.55577in], end = [var 8.5725in, var -3.22077in])
  line5 = line(start = [var 8.5725in, var -3.22077in], end = [var 8.56276in, var -3.2185in])
  arc2 = arc(start = [var 2.85806in, var -1.63495in], end = [var 8.56276in, var -3.2185in], center = [var 24.672in, var 65.901in])
  coincident([line1.end, line2.start])
  coincident([line2.end, arc1.start])
  coincident([arc1.end, line3.start])
  coincident([line3.end, line4.start])
  coincident([line4.end, line5.start])
  coincident([line5.end, arc2.end])
  coincident([arc2.start, line1.start])
}
spokeSideRegion = region(segments = [
  spokeSideSketch.line1,
  spokeSideSketch.line2
])
spokeSide = rotate(spokeSideRegion, pitch = 90deg, global = false)
  |> revolve(axis = Y)
hide([spokeSideSketch])

spokeFaceSketch = sketch(on = XZ) {
  line1 = line(start = [var -4in, var 0.75in], end = [var -11.46in, var 5.78in])
  line2 = line(start = [var -11.32in, var 5.99in], end = [var -2.94in, var 1.56in])
  arc3 = arc(start = [var -2.94in, var 1.56in], end = [var -2.32in, var 1.69in], center = [var -2.71in, var 2.01in])
  arc6 = arc(start = [var -2.31in, var -1.7in], end = [var -2.94in, var -1.57in], center = [var -2.7in, var -2in])
  line3 = line(start = [var -2.94in, var -1.57in], end = [var -11.32in, var -5.99in])
  line4 = line(start = [var -11.46in, var -5.78in], end = [var -4in, var -0.75in])
  coincident([line2.end, arc3.start])
  coincident([arc6.end, line3.start])
  point2 = point(at = [var -2.87in, var 0in])
  arc4 = arc(start = [var -2.32in, var 1.69in], end = [var -2.31in, var -1.7in], center = [var 0in, var 0in])
  coincident([arc4.start, arc3.end])
  coincident([point2, arc4])
  coincident([arc4.center, ORIGIN])
  radius(arc4) == 2.87
  line5 = line(start = [var -11.46in, var -5.78in], end = [var -11.32in, var -5.99in])
  coincident([line5.start, line4.start])
  coincident([line5.end, line3.end])
  line6 = line(start = [var -11.32in, var 5.99in], end = [var -11.46in, var 5.78in])
  coincident([line6.start, line2.start])
  coincident([line6.end, line1.end])
  point3 = point(at = [var -3.62in, var 0in])
  arc1 = arc(start = [var -4in, var -0.75in], end = [var -4in, var 0.75in], center = [var -4.54in, var 0in])
  coincident([arc1.start, line4.end])
  coincident([point3, arc1])
  coincident([arc4.end, arc6.start])
  coincident([arc1.end, line1.start])
}
spokeFaceRegion = region(segments = [
  spokeFaceSketch.arc1,
  spokeFaceSketch.line1
])
spokeFace = extrude(spokeFaceRegion, length = wheelWidth * 2)
hide([spokeFaceSketch])

spokes = intersect([spokeFace, spokeSide])
  |> patternCircular3d(instances = spokeCount, axis = Y, center = [0, 0, 0])

wheel = appearance(
  [wheelCenter, spokes, rim],
  color = "#ededed",
  metalness = 70,
  roughness = 30,
)
```

### lug-nut.kcl

```kcl
// Lug Nut
// Solver sketch version of the lug nut profile.

// Set units and version
@settings(defaultLengthUnit = in, kclVersion = 2.0)

// Import parameters
import * from "parameters.kcl"

customPlane = {
  origin = {
    x = lugSpacing / 2,
    y = (-tBell - 0.85) * 25.4,
    z = 0
  },
  xAxis = { x = 1, y = 0, z = 0 },
  yAxis = { x = 0, y = -1, z = 0 }
}

lugNutSketch = sketch(on = customPlane) {
  line1 = line(start = [var 0.47in, var 0in], end = [var 0.47in, var 0.63in])
  arc1 = arc(start = [var 0.47in, var 0.63in], end = [var 0.35in, var 0.74in], center = [var 0.35in, var 0.63in])
  line2 = line(start = [var 0.35in, var 0.74in], end = [var 0in, var 0.74in])
  line3 = line(start = [var 0in, var 0.74in], end = [var 0in, var 0.38in])
  line4 = line(start = [var 0in, var 0.38in], end = [var 0.35in, var 0.38in])
  line5 = line(start = [var 0.35in, var 0.38in], end = [var 0.47in, var 0in])
  coincident([line1.end, arc1.start])
  coincident([arc1.end, line2.start])
  coincident([line2.end, line3.start])
  coincident([line3.end, line4.start])
  coincident([line4.end, line5.start])
  coincident([line5.end, line1.start])
}

lugNutRegion = region(segments = [lugNutSketch.line1, lugNutSketch.arc1])
lugNutBody = revolve(lugNutRegion, axis = Y)
hide([lugNutSketch])

lugNut = lugNutBody
  |> appearance(color = "#ededed", metalness = 70, roughness = 30)
```

### parameters.kcl

```kcl
// Car wheel assembly parameters

// Set units
@settings(defaultLengthUnit = in, kclVersion = 2.0)

// Lugs
export lugCount = 5
export lugSpacing = 114.3mm
export lugDiameter = 24mm
export lugThreadDiameter = lugDiameter / 1.75
export lugLength = 5 / 8

// Car wheel
export spokeCount = 5
export offset = -10mm
export wheelWidth = 9.5
export rimDiameter = 18

// Brake caliper
export caliperThickness = 2.5

// Brake rotor
export rotorDiameter = 12
export rotorBore = 3
export hFrictionSurface = 2.36
export tDiscHalf = 3 / 8
export tVent = 3 / 8
export wVent = 1 / 4
export rVentFillet = 1 / 10
export nVentBosses = 36
export dDrillDia = 1 / 4
export aBase = 90deg
export aSweep = 30deg
export nArcs = 12
export tBell = 0.2
export hBellAboveDiscFace = 1.5
export wUndercut = 0.2
export rDraftAngle = 83deg

// Car tire
export tireWidth = 255mm
export aspectRatio = 30
export overallDiameter = rimDiameter + tireWidth * aspectRatio * 0.02
export sidewallThickness = 6mm
export treadDepth = 3mm
```

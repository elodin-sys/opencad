Source URL: https://zoo.dev/aquarium/pipe-flange-assembly
Title: Pipe and Flange Assembly

# Pipe and Flange Assembly

A crucial component in various piping systems, designed to facilitate the connection, disconnection, and access to piping for inspection, cleaning, and modifications. This assembly combines pipes (long cylindrical conduits) with flanges (plate-like fittings) to create a secure yet detachable joint.

- Page: /aquarium/pipe-flange-assembly
- Legacy docs page: /docs/kcl-samples/pipe-flange-assembly
- Preview image: /kcl-samples/screenshots/pipe-flange-assembly.png
- Categories: Architecture & Construction, Mechanical Components

## Files

### main.kcl

```kcl
// Pipe and Flange Assembly
// A crucial component in various piping systems, designed to facilitate the connection, disconnection, and access to piping for inspection, cleaning, and modifications. This assembly combines pipes (long cylindrical conduits) with flanges (plate-like fittings) to create a secure yet detachable joint.
// Categories: Architecture & Construction; Mechanical Components

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import * from "parameters.kcl"

import "9472k188-gasket.kcl" as gasket
import flange from "68095k348-flange.kcl"
import washer from "98017a257-washer.kcl"
import bolt from "91251a404-bolt.kcl"
import hexNut from "95479a127-hex-nut.kcl"
import pipe from "1120t74-pipe.kcl"

flange()
flange()
  |> rotate(axis = [0, 1, 0], angle = 180deg)
  |> translate(x = 0, y = 0, z = flangeBackHeight * 2 + gasketThickness)

gasket
  |> translate(x = 0, y = 0, z = -flangeBackHeight - gasketThickness)

washer()
  |> translate(x = mountingHolePlacementDiameter / 2, y = 0, z = flangeBaseThickness)
  |> patternCircular3d(
       instances = 4,
       axis = Z,
       center = [0, 0, 0],
       arcDegrees = 360deg,
       rotateDuplicates = false,
     )
  |> patternLinear3d(instances = 2, distance = -(flangeBaseThickness * 2 + flangeBackHeight * 2 + gasketThickness + washerThickness), axis = Z)

bolt()
  |> translate(x = mountingHolePlacementDiameter / 2, y = 0, z = flangeBaseThickness + washerThickness)
  |> rotate(roll = 90deg, pitch = 0deg, yaw = 0deg)
  |> patternCircular3d(
       instances = 4,
       axis = Z,
       center = [0, 0, 0],
       arcDegrees = 360deg,
       rotateDuplicates = false,
     )

hexNut()
  |> translate(x = mountingHolePlacementDiameter / 2, y = 0, z = -(flangeBackHeight * 2 + gasketThickness + flangeBaseThickness + washerThickness + hexNutThickness))
  |> patternCircular3d(
       instances = 4,
       axis = Z,
       center = [0, 0, 0],
       arcDegrees = 360deg,
       rotateDuplicates = false,
     )

pipe()
  |> rotate(roll = -90deg, pitch = 0deg, yaw = 0deg)
  |> translate(
       x = 0,
       y = 0,
       z = flangeBaseThickness + flangeFrontHeight - 0.5,
       global = true,
     )

pipe()
  |> rotate(roll = 90deg, pitch = 0deg, yaw = 0deg)
  |> translate(
       x = 0,
       y = 0,
       z = -(flangeBackHeight * 2 + gasketThickness + flangeBaseThickness + flangeFrontHeight - 0.5),
       global = true,
     )
```

### 1120t74-pipe.kcl

```kcl
// Pipe
// Piping for the pipe flange assembly

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import pipeInnerDiameter, pipeOuterDiameter, pipeLength from "parameters.kcl"

export fn pipe() {
  pipeSketch = sketch(on = XZ) {
    outerCircle = circle(start = [var 1.1875in, var 0in], center = [var 0in, var 0in])
    innerCircle = circle(start = [var 1in, var 0in], center = [var 0in, var 0in])
  }

  pipeRegion = region(segments = [pipeSketch.outerCircle])
  pipeBody = extrude(pipeRegion, length = pipeLength)
    |> appearance(color = "#a24ed0")

  return pipeBody
}
```

### 68095k348-flange.kcl

```kcl
// Flange
// Flange used for mating two pipes together in the pipe flange assembly.

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import pipeDiameter, mountingHoleDiameter, mountingHolePlacementDiameter, flangeDiameter, flangeTotalThickness, flangeBackHeight, flangeFrontHeight, flangeBaseThickness, flangeBackDiameter, flangeFrontDiameter from "parameters.kcl"

export fn flange() {
  baseSketch = sketch(on = XY) {
    outerCircle = circle(start = [var 3in, var 0in], center = [var 0in, var 0in])
  }
  baseRegion = region(segments = [baseSketch.outerCircle])
  flangeBase = extrude(baseRegion, length = flangeBaseThickness)

  mountingHoleSketch = sketch(on = offsetPlane(XY, offset = -flangeBackHeight)) {
    mountingHole = circle(start = [var 0.375in, var 2.375in], center = [var 0in, var 2.375in])
  }
  mountingHoleRegion = region(segments = [mountingHoleSketch.mountingHole])
  mountingHoleTool = extrude(mountingHoleRegion, length = flangeTotalThickness)
    |> patternCircular3d(
         instances = 4,
         axis = Z,
         center = [0, 0, 0],
         arcDegrees = 360deg,
         rotateDuplicates = false,
       )
  flangeBaseWithHoles = subtract(flangeBase, tools = mountingHoleTool)

  backSketch = sketch(on = XY) {
    outerCircle = circle(start = [var 1.81in, var 0in], center = [var 0in, var 0in])
  }
  flangeBack = extrude(region(segments = [backSketch.outerCircle]), length = -flangeBackHeight)

  frontSketch = sketch(on = offsetPlane(XY, offset = flangeBaseThickness)) {
    outerCircle = circle(start = [var 1.53in, var 0in], center = [var 0in, var 0in])
  }
  flangeFront = extrude(region(segments = [frontSketch.outerCircle]), length = flangeFrontHeight)

  flangeBody = union([
    flangeBaseWithHoles,
    flangeBack,
    flangeFront
  ])

  pipeCutSketch = sketch(on = offsetPlane(XY, offset = -flangeBackHeight)) {
    pipeCutCircle = circle(start = [var 1.22in, var 0in], center = [var 0in, var 0in])
  }
  pipeCutTool = extrude(region(segments = [pipeCutSketch.pipeCutCircle]), length = flangeTotalThickness)

  flangeResult = subtract(flangeBody, tools = [pipeCutTool])
    |> appearance(color = "#bab0b0")

  return flangeResult
}
```

### 91251a404-bolt.kcl

```kcl
// Socket Head Cap Screw
// Screw for mating the flanges together in the pipe flange assembly

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import boltLength, boltHeadLength from "parameters.kcl"

export fn bolt() {
  headSketch = sketch(on = XZ) {
    headCircle = circle(start = [var 0.469in, var 0in], center = [var 0in, var 0in])
  }
  headRegion = region(segments = [headSketch.headCircle])
  boltHead = extrude(
    headRegion,
    length = -boltHeadLength,
    tagStart = $headStart,
    tagEnd = $headEnd,
  )
    |> fillet(
         edges = [
           {
             sideFaces = [headRegion.tags.headCircle, headStart]
           },
           {
             sideFaces = [headRegion.tags.headCircle, headEnd]
           }
         ],
         radius = 0.020,
       )

  // Cut the drive with an independent sketch on the head's original plane.
  // This avoids a face-derived cutter whose direction is ambiguous after the
  // head fillets while preserving the legacy 75% recess depth.
  hexSketch = sketch(on = offsetPlane(XZ, offset = -boltHeadLength)) {
    hex1 = line(start = [var 0.25in, var 0.1443375673in], end = [var 0.25in, var -0.1443375673in])
    hex2 = line(start = [var 0.25in, var -0.1443375673in], end = [var 0in, var -0.2886751346in])
    coincident([hex1.end, hex2.start])
    hex3 = line(start = [var 0in, var -0.2886751346in], end = [var -0.25in, var -0.1443375673in])
    coincident([hex2.end, hex3.start])
    hex4 = line(start = [var -0.25in, var -0.1443375673in], end = [var -0.25in, var 0.1443375673in])
    coincident([hex3.end, hex4.start])
    hex5 = line(start = [var -0.25in, var 0.1443375673in], end = [var 0in, var 0.2886751346in])
    coincident([hex4.end, hex5.start])
    hex6 = line(start = [var 0in, var 0.2886751346in], end = [var 0.25in, var 0.1443375673in])
    coincident([hex5.end, hex6.start])
    coincident([hex6.end, hex1.start])
  }
  hexRegion = region(segments = [hexSketch.hex1, hexSketch.hex2], direction = CW)
  hexCut = extrude(hexRegion, length = boltHeadLength * 0.75)
  recessedHead = subtract(boltHead, tools = [hexCut])

  shaftSketch = sketch(on = XZ) {
    shaftCircle = circle(start = [var 0.3125in, var 0in], center = [var 0in, var 0in])
  }
  shaft = extrude(region(segments = [shaftSketch.shaftCircle]), length = boltLength)

  boltResult = union([recessedHead, shaft])
    |> appearance(color = "#4dd043", metalness = 90, roughness = 90)

  return boltResult
}
```

### 9472k188-gasket.kcl

```kcl
// Gasket
// A seal between the two mating flange surfaces

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import gasketOutsideDiameter, gasketInnerDiameter, gasketThickness from "parameters.kcl"

gasketSketch = sketch(on = XY) {
  outerCircle = circle(start = [var 2.0625in, var 0in], center = [var 0in, var 0in])
  innerCircle = circle(start = [var 1.1875in, var 0in], center = [var 0in, var 0in])
}
gasketRegion = region(segments = [gasketSketch.outerCircle])
extrude(gasketRegion, length = gasketThickness)
  |> appearance(color = "#d0cb3e")
```

### 95479a127-hex-nut.kcl

```kcl
// Hex Nut
// Hex nut for the screws in the pipe flange assembly

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import hexNutDiameter, hexNutFlatToFlat, hexNutThickness, hexNutFlatLength from "parameters.kcl"

export fn hexNut() {
  nutSketch = sketch(on = XY) {
    hex1 = line(start = [var 0.46875in, var 0.2706329387in], end = [var 0.46875in, var -0.2706329387in])
    hex2 = line(start = [var 0.46875in, var -0.2706329387in], end = [var 0in, var -0.5412658774in])
    coincident([hex1.end, hex2.start])
    hex3 = line(start = [var 0in, var -0.5412658774in], end = [var -0.46875in, var -0.2706329387in])
    coincident([hex2.end, hex3.start])
    hex4 = line(start = [var -0.46875in, var -0.2706329387in], end = [var -0.46875in, var 0.2706329387in])
    coincident([hex3.end, hex4.start])
    hex5 = line(start = [var -0.46875in, var 0.2706329387in], end = [var 0in, var 0.5412658774in])
    coincident([hex4.end, hex5.start])
    hex6 = line(start = [var 0in, var 0.5412658774in], end = [var 0.46875in, var 0.2706329387in])
    coincident([hex5.end, hex6.start])
    coincident([hex6.end, hex1.start])
    bore = circle(start = [var 0.3125in, var 0in], center = [var 0in, var 0in])
  }

  nutRegion = region(segments = [nutSketch.hex1, nutSketch.hex2], direction = CW)
  nutBody = extrude(nutRegion, length = hexNutThickness)
    |> appearance(color = "#4edfd5")

  return nutBody
}
```

### 98017a257-washer.kcl

```kcl
// Washer
// Washer for the screws in the pipe flange assembly

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import washerInnerDia, washerOuterDia, washerThickness from "parameters.kcl"

export fn washer() {
  washerSketch = sketch(on = XY) {
    outerCircle = circle(start = [var 0.594in, var 0in], center = [var 0in, var 0in])
    innerCircle = circle(start = [var 0.32in, var 0in], center = [var 0in, var 0in])
  }

  washerRegion = region(segments = [washerSketch.outerCircle])
  washerBody = extrude(washerRegion, length = washerThickness)
    |> appearance(color = "#ee4f4f")

  return washerBody
}
```

### parameters.kcl

```kcl
// Parameters

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

// Flange (68095K348)
export pipeDiameter = 2.440
export mountingHoleDiameter = 0.750
export mountingHolePlacementDiameter = 4.750

export flangeDiameter = 6.0
export flangeTotalThickness = 1.0
export flangeBackHeight = 0.060
export flangeFrontHeight = 0.250
export flangeBaseThickness = flangeTotalThickness - flangeBackHeight - flangeFrontHeight

export flangeBackDiameter = 3.620
export flangeFrontDiameter = 3.060

// Washer (98017A257)
export washerInnerDia = 0.640
export washerOuterDia = 1.188
export washerThickness = 0.032

// Bolt (91251A404)
export boltDiameter = 0.625
export boltLength = 2.500
export boltHeadLength = boltDiameter
export boltHeadDiameter = 0.938
export boltHexDrive = 1 / 2
export boltHexFlatLength = boltHexDrive / (2 * cos(30deg))
export boltThreadLength = 1.750

// Hex nut (95479A127)
export hexNutDiameter = 5 / 8
export hexNutFlatToFlat = 15 / 16
export hexNutThickness = 35 / 64
export hexNutFlatLength = hexNutFlatToFlat / (2 * cos(30deg))

// Gasket (9472K188)
export gasketOutsideDiameter = 4.125
export gasketInnerDiameter = 2.375
export gasketThickness = 0.031

// Pipe (1120T74)
export pipeInnerDiameter = 2.0
export pipeOuterDiameter = 2.375
export pipeLength = 6
```

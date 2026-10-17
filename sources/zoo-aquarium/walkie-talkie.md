Source URL: https://zoo.dev/aquarium/walkie-talkie
Title: Walkie Talkie

# Walkie Talkie

A portable, handheld two-way radio device that allows users to communicate wirelessly over short to medium distances. It operates on specific radio frequencies and features a push-to-talk button for transmitting messages, making it ideal for quick and reliable communication in outdoor, work, or emergency settings.

- Page: /aquarium/walkie-talkie
- Legacy docs page: /docs/kcl-samples/walkie-talkie
- Preview image: /kcl-samples/screenshots/walkie-talkie.png
- Categories: Electronics & Computing

## Files

### main.kcl

```kcl
// Walkie Talkie
// A portable, handheld two-way radio device that allows users to communicate wirelessly over short to medium distances. It operates on specific radio frequencies and features a push-to-talk button for transmitting messages, making it ideal for quick and reliable communication in outdoor, work, or emergency settings.
// Categories: Electronics & Computing

// set units
@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

// import constants
import * from "parameters.kcl"

// import parts and parameters
import "body.kcl" as body
import "case.kcl" as case
import "antenna.kcl" as antenna
import "talk-button.kcl" as talkButton
import "knob.kcl" as knob
import button from "button.kcl"

// Import the body
body

// Import the antenna
antenna
  |> translate(x = -width / 2 + .60, y = -0.20, z = height / 2)

// Import the case
case
  |> translate(x = 0, y = -1, z = 0)

// Import the talk button
talkButton
  |> translate(x = width / 2, y = -thickness / 2, z = .5)

// Import the frequency knob
knob
  |> translate(x = width / 2 - 0.70, y = -thickness / 2, z = height / 2)

// Import the buttons
button()
  |> translate(x = -(screenWidth / 2 + tolerance), y = -1, z = screenYPosition)
button()
  |> translate(x = -(screenWidth / 2 + tolerance), y = -1, z = screenYPosition - buttonHeight - (tolerance * 2))
button()
  |> rotate(roll = 0, pitch = 180, yaw = 0)
  |> translate(
       x = screenWidth / 2 + tolerance,
       y = -1,
       z = screenYPosition - buttonHeight,
       global = true,
     )
button()
  |> rotate(roll = 0, pitch = 180, yaw = 0)
  |> translate(
       x = screenWidth / 2 + tolerance,
       y = -1,
       z = screenYPosition - (buttonHeight * 2) - (tolerance * 2),
       global = true,
     )
```

### antenna.kcl

```kcl
// Walkie Talkie Antenna
// Antenna for the walkie talkie assembly

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import antennaLength from "parameters.kcl"

antennaBaseSketch = sketch(on = XY) {
  line1 = line(start = [var -0.25in, var 0.125in], end = [var 0.25in, var 0.125in])
  line2 = line(start = [var 0.25in, var 0.125in], end = [var 0.25in, var -0.125in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 0.25in, var -0.125in], end = [var -0.25in, var -0.125in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -0.25in, var -0.125in], end = [var -0.25in, var 0.125in])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
  horizontal(line1)
  vertical(line2)
  horizontal(line3)
  vertical(line4)
}

loftPlane = offsetPlane(XY, offset = antennaLength)
antennaTopSketch = sketch(on = loftPlane) {
  line1 = line(start = [var -0.125in, var 0.0625in], end = [var 0.125in, var 0.0625in])
  line2 = line(start = [var 0.125in, var 0.0625in], end = [var 0.125in, var -0.0625in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 0.125in, var -0.0625in], end = [var -0.125in, var -0.0625in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -0.125in, var -0.0625in], end = [var -0.125in, var 0.0625in])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
  horizontal(line1)
  vertical(line2)
  horizontal(line3)
  vertical(line4)
}

antennaBaseRegion = region(segments = [
  antennaBaseSketch.line1,
  antennaBaseSketch.line2
])
antennaTopRegion = region(segments = [
  antennaTopSketch.line1,
  antennaTopSketch.line2
])
antenna = loft([antennaBaseRegion, antennaTopRegion])
  |> appearance(color = "#000000")
hide([antennaBaseSketch, antennaTopSketch])

antenna
```

### body.kcl

```kcl
// Walkie Talkie Body
// The main body of the walkie talkie assembly

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import thickness, chamferLength, screenDepth from "parameters.kcl"

bodySketch = sketch(on = XZ) {
  line1 = line(start = [var -1.25in, var 2in], end = [var 1.25in, var 2in])
  line2 = line(start = [var 1.25in, var 2in], end = [var 1.25in, var -2in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 1.25in, var -2in], end = [var -1.25in, var -2in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -1.25in, var -2in], end = [var -1.25in, var 2in])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
  horizontal(line1)
  vertical(line2)
  horizontal(line3)
  vertical(line4)
}
bodyRegion = region(segments = [bodySketch.line1, bodySketch.line2])
bodyBlank = extrude(bodyRegion, length = thickness)
body = chamfer(
  bodyBlank,
  length = chamferLength,
  edges = [
    {
      sideFaces = [
        bodyRegion.tags.line1,
        bodyRegion.tags.line2
      ]
    },
    {
      sideFaces = [
        bodyRegion.tags.line2,
        bodyRegion.tags.line3
      ]
    },
    {
      sideFaces = [
        bodyRegion.tags.line3,
        bodyRegion.tags.line4
      ]
    },
    {
      sideFaces = [
        bodyRegion.tags.line4,
        bodyRegion.tags.line1
      ]
    }
  ],
)

caseIndentSketch = sketch(on = faceOf(body, face = END)) {
  line1 = line(start = [var -1.125in, var 1.630806in], end = [var -0.880806in, var 1.875in])
  line2 = line(start = [var -0.880806in, var 1.875in], end = [var 0.880806in, var 1.875in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 0.880806in, var 1.875in], end = [var 1.125in, var 1.630806in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var 1.125in, var 1.630806in], end = [var 1.125in, var -1.630806in])
  coincident([line3.end, line4.start])
  line5 = line(start = [var 1.125in, var -1.630806in], end = [var 0.880806in, var -1.875in])
  coincident([line4.end, line5.start])
  line6 = line(start = [var 0.880806in, var -1.875in], end = [var -0.880806in, var -1.875in])
  coincident([line5.end, line6.start])
  line7 = line(start = [var -0.880806in, var -1.875in], end = [var -1.125in, var -1.630806in])
  coincident([line6.end, line7.start])
  line8 = line(start = [var -1.125in, var -1.630806in], end = [var -1.125in, var 1.630806in])
  coincident([line7.end, line8.start])
  coincident([line8.end, line1.start])
}
caseIndentRegion = region(segments = [
  caseIndentSketch.line1,
  caseIndentSketch.line2
])
caseIndent = extrude(caseIndentRegion, length = -0.0625)

screenCutoutSketch = sketch(on = faceOf(caseIndent, face = START)) {
  line1 = line(start = [var -0.875in, var 1.25in], end = [var 0.875in, var 1.25in])
  line2 = line(start = [var 0.875in, var 1.25in], end = [var 0.875in, var 0.25in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 0.875in, var 0.25in], end = [var -0.875in, var 0.25in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -0.875in, var 0.25in], end = [var -0.875in, var 1.25in])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
  horizontal(line1)
  vertical(line2)
  horizontal(line3)
  vertical(line4)
}
screenCutoutRegion = region(segments = [
  screenCutoutSketch.line1,
  screenCutoutSketch.line2
])
screenCutout = extrude(screenCutoutRegion, length = screenDepth)

speakerBoxSketch = sketch(on = faceOf(caseIndent, face = START)) {
  line1 = line(start = [var -0.625in, var -0.125in], end = [var 0.625in, var -0.125in])
  line2 = line(start = [var 0.625in, var -0.125in], end = [var 0.625in, var -1.375in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 0.625in, var -1.375in], end = [var -0.625in, var -1.375in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -0.625in, var -1.375in], end = [var -0.625in, var -0.125in])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
  horizontal(line1)
  vertical(line2)
  horizontal(line3)
  vertical(line4)
}
speakerBoxRegion = region(segments = [
  speakerBoxSketch.line1,
  speakerBoxSketch.line2
])
speakerBox = extrude(speakerBoxRegion, length = -.5)
  |> appearance(color = "#277bb0")

hide([
  bodySketch,
  caseIndentSketch,
  screenCutoutSketch,
  speakerBoxSketch
])

[
  body,
  caseIndent,
  screenCutout,
  speakerBox
]
```

### button.kcl

```kcl
// Walkie Talkie Button
// Button for the walkie talkie

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import buttonWidth, buttonHeight, buttonThickness from "parameters.kcl"

export fn button() {
  buttonSketch = sketch(on = XZ) {
    line1 = line(start = [var 0in, var 0in], end = [var -0.15in, var 0in])
    line2 = line(start = [var -0.15in, var 0in], end = [var -0.15in, var -0.48in])
    coincident([line1.end, line2.start])
    line3 = line(start = [var -0.15in, var -0.48in], end = [var 0in, var -0.48in])
    coincident([line2.end, line3.start])
    line4 = line(start = [var 0in, var -0.48in], end = [var 0in, var 0in])
    coincident([line3.end, line4.start])
    coincident([line4.end, line1.start])
    coincident([line1.start, ORIGIN])
    horizontal(line1)
    vertical(line2)
    horizontal(line3)
    vertical(line4)
    horizontalDistance([line1.end, line1.start]) == buttonWidth
    verticalDistance([line2.end, line2.start]) == buttonHeight
  }
  buttonRegion = region(segments = [buttonSketch.line1, buttonSketch.line2])
  buttonBlank = extrude(buttonRegion, length = buttonThickness)
  result = chamfer(
    buttonBlank,
    length = .050,
    edges = [
      {
        sideFaces = [
          buttonRegion.tags.line1,
          buttonRegion.tags.line2
        ]
      },
      {
        sideFaces = [
          buttonRegion.tags.line2,
          buttonRegion.tags.line3
        ]
      }
    ],
  )
    |> appearance(color = "#ff0000")
  hide(buttonSketch)
  return result
}
```

### case.kcl

```kcl
// Walkie Talkie Case
// The plastic case for the front of the walkie talkie

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

caseProfile = sketch(on = XZ) {
  line1 = line(start = [var -1.115in, var 1.62727in], end = [var -0.87727in, var 1.865in])
  line2 = line(start = [var -0.87727in, var 1.865in], end = [var 0.87727in, var 1.865in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 0.87727in, var 1.865in], end = [var 1.115in, var 1.62727in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var 1.115in, var 1.62727in], end = [var 1.115in, var -1.62727in])
  coincident([line3.end, line4.start])
  line5 = line(start = [var 1.115in, var -1.62727in], end = [var 0.87727in, var -1.865in])
  coincident([line4.end, line5.start])
  line6 = line(start = [var 0.87727in, var -1.865in], end = [var -0.87727in, var -1.865in])
  coincident([line5.end, line6.start])
  line7 = line(start = [var -0.87727in, var -1.865in], end = [var -1.115in, var -1.62727in])
  coincident([line6.end, line7.start])
  line8 = line(start = [var -1.115in, var -1.62727in], end = [var -1.115in, var 1.62727in])
  coincident([line7.end, line8.start])
  coincident([line8.end, line1.start])
}
caseRegion = region(segments = [caseProfile.line1, caseProfile.line2])
caseBlank = extrude(caseRegion, length = -0.0625)

screenSketch = sketch(on = XZ) {
  line1 = line(start = [var -0.875in, var 1.25in], end = [var 0.875in, var 1.25in])
  line2 = line(start = [var 0.875in, var 1.25in], end = [var 0.875in, var 0.25in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 0.875in, var 0.25in], end = [var -0.875in, var 0.25in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -0.875in, var 0.25in], end = [var -0.875in, var 1.25in])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
  horizontal(line1)
  vertical(line2)
  horizontal(line3)
  vertical(line4)
}
screenRegion = region(segments = [screenSketch.line1, screenSketch.line2])
screenTool = extrude(screenRegion, length = -0.0625)
caseWithScreen = subtract(caseBlank, tools = [screenTool])

// Exact 13 x 11 speaker grille. The cutter extends beyond both panel faces so
// this multi-tool Boolean does not depend on coplanar faces.
speakerDotSketch = sketch(on = offsetPlane(XZ, offset = 0.0001)) {
  line1 = line(start = [var -0.775in, var 0in], end = [var -0.74375in, var 0in])
  line2 = line(start = [var -0.74375in, var 0in], end = [var -0.74375in, var -0.03125in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var -0.74375in, var -0.03125in], end = [var -0.775in, var -0.03125in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -0.775in, var -0.03125in], end = [var -0.775in, var 0in])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
  horizontal(line1)
  vertical(line2)
  horizontal(line3)
  vertical(line4)
}
speakerDotRegion = region(segments = [
  speakerDotSketch.line1,
  speakerDotSketch.line2
])
speakerDotSeed = extrude(speakerDotRegion, length = -0.0627, method = NEW)
speakerDots = patternLinear3d(
  speakerDotSeed,
  instances = 13,
  distance = 0.125,
  axis = X,
)
  |> patternLinear3d(instances = 11, distance = 0.125, axis = -Z)
caseWithGrille = subtract(caseWithScreen, tools = speakerDots)

zSketch = sketch(on = XZ) {
  line1 = line(start = [var -0.3in, var -1.795in], end = [var -0.3in, var -1.825in])
  line2 = line(start = [var -0.3in, var -1.825in], end = [var -0.27in, var -1.825in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var -0.27in, var -1.825in], end = [var -0.24in, var -1.79266in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -0.24in, var -1.79266in], end = [var -0.24in, var -1.825in])
  coincident([line3.end, line4.start])
  line5 = line(start = [var -0.24in, var -1.825in], end = [var -0.114in, var -1.825in])
  coincident([line4.end, line5.start])
  line6 = line(start = [var -0.114in, var -1.825in], end = [var -0.114in, var -1.78in])
  coincident([line5.end, line6.start])
  line7 = line(start = [var -0.114in, var -1.78in], end = [var -0.228in, var -1.78in])
  coincident([line6.end, line7.start])
  line8 = line(start = [var -0.228in, var -1.78in], end = [var -0.114in, var -1.657106in])
  coincident([line7.end, line8.start])
  line9 = line(start = [var -0.114in, var -1.657106in], end = [var -0.114in, var -1.627106in])
  coincident([line8.end, line9.start])
  line10 = line(start = [var -0.114in, var -1.627106in], end = [var -0.144in, var -1.627106in])
  coincident([line9.end, line10.start])
  line11 = line(start = [var -0.144in, var -1.627106in], end = [var -0.174in, var -1.659447in])
  coincident([line10.end, line11.start])
  line12 = line(start = [var -0.174in, var -1.659447in], end = [var -0.174in, var -1.627106in])
  coincident([line11.end, line12.start])
  line13 = line(start = [var -0.174in, var -1.627106in], end = [var -0.3in, var -1.627106in])
  coincident([line12.end, line13.start])
  line14 = line(start = [var -0.3in, var -1.627106in], end = [var -0.3in, var -1.672106in])
  coincident([line13.end, line14.start])
  line15 = line(start = [var -0.3in, var -1.672106in], end = [var -0.185743in, var -1.672106in])
  coincident([line14.end, line15.start])
  line16 = line(start = [var -0.185743in, var -1.672106in], end = [var -0.3in, var -1.795in])
  coincident([line15.end, line16.start])
  coincident([line16.end, line1.start])
}
zRegion = region(segments = [zSketch.line1, zSketch.line2])
zTool = extrude(zRegion, length = -0.0625)

o1OuterSketch = sketch(on = XZ) {
  arc1 = arc(start = [var 0.0826in, var -1.6408in], end = [var -0.059435in, var -1.793915in], center = [var 0.019629in, var -1.724822in])
  line2 = line(start = [var -0.059435in, var -1.793915in], end = [var -0.026791in, var -1.758725in])
  coincident([arc1.end, line2.start])
  arc3 = arc(start = [var 0.050115in, var -1.675819in], end = [var -0.026791in, var -1.758725in], center = [var 0.01972in, var -1.724746in])
  coincident([line2.end, arc3.end])
  line4 = line(start = [var 0.050115in, var -1.675819in], end = [var 0.0826in, var -1.6408in])
  coincident([arc3.start, line4.start])
  coincident([line4.end, arc1.start])
}
o1OuterRegion = region(segments = [
  o1OuterSketch.arc1,
  o1OuterSketch.line2
])
o1OuterTool = extrude(o1OuterRegion, length = -0.0625)

o1InnerSketch = sketch(on = XZ) {
  arc1 = arc(start = [var -0.043in, var -1.8092in], end = [var 0.099035in, var -1.656085in], center = [var 0.019971in, var -1.725178in])
  line2 = line(start = [var 0.099035in, var -1.656085in], end = [var 0.066391in, var -1.691275in])
  coincident([arc1.end, line2.start])
  arc3 = arc(start = [var -0.010515in, var -1.774181in], end = [var 0.066391in, var -1.691275in], center = [var 0.01988in, var -1.725254in])
  coincident([line2.end, arc3.end])
  line4 = line(start = [var -0.010515in, var -1.774181in], end = [var -0.043in, var -1.8092in])
  coincident([arc3.start, line4.start])
  coincident([line4.end, arc1.start])
}
o1InnerRegion = region(segments = [
  o1InnerSketch.arc1,
  o1InnerSketch.line2
])
o1InnerTool = extrude(o1InnerRegion, length = -0.0625)

o2OuterSketch = sketch(on = XZ) {
  arc1 = arc(start = [var 0.3326in, var -1.6408in], end = [var 0.190565in, var -1.793915in], center = [var 0.269629in, var -1.724822in])
  line2 = line(start = [var 0.190565in, var -1.793915in], end = [var 0.223209in, var -1.758725in])
  coincident([arc1.end, line2.start])
  arc3 = arc(start = [var 0.300115in, var -1.675819in], end = [var 0.223209in, var -1.758725in], center = [var 0.26972in, var -1.724746in])
  coincident([line2.end, arc3.end])
  line4 = line(start = [var 0.300115in, var -1.675819in], end = [var 0.3326in, var -1.6408in])
  coincident([arc3.start, line4.start])
  coincident([line4.end, arc1.start])
}
o2OuterRegion = region(segments = [
  o2OuterSketch.arc1,
  o2OuterSketch.line2
])
o2OuterTool = extrude(o2OuterRegion, length = -0.0625)

o2InnerSketch = sketch(on = XZ) {
  arc1 = arc(start = [var 0.207in, var -1.8092in], end = [var 0.349035in, var -1.656085in], center = [var 0.269971in, var -1.725178in])
  line2 = line(start = [var 0.349035in, var -1.656085in], end = [var 0.316391in, var -1.691275in])
  coincident([arc1.end, line2.start])
  arc3 = arc(start = [var 0.239485in, var -1.774181in], end = [var 0.316391in, var -1.691275in], center = [var 0.26988in, var -1.725254in])
  coincident([line2.end, arc3.end])
  line4 = line(start = [var 0.239485in, var -1.774181in], end = [var 0.207in, var -1.8092in])
  coincident([arc3.start, line4.start])
  coincident([line4.end, arc1.start])
}
o2InnerRegion = region(segments = [
  o2InnerSketch.arc1,
  o2InnerSketch.line2
])
o2InnerTool = extrude(o2InnerRegion, length = -0.0625)

caseWithZ = subtract(caseWithGrille, tools = [zTool])
caseWithO1Outer = subtract(caseWithZ, tools = [o1OuterTool])
caseWithO1Inner = subtract(caseWithO1Outer, tools = [o1InnerTool])
caseWithO2Outer = subtract(caseWithO1Inner, tools = [o2OuterTool])
case = subtract(caseWithO2Outer, tools = [o2InnerTool])
  |> appearance(color = "#D0FF01", metalness = 0, roughness = 50)

hide([
  caseProfile,
  screenSketch,
  speakerDotSketch,
  zSketch,
  o1OuterSketch,
  o1InnerSketch,
  o2OuterSketch,
  o2InnerSketch
])

case
```

### knob.kcl

```kcl
// Walkie Talkie Frequency Knob

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import knobDiameter, knobHeight, knobFilletRadius from "parameters.kcl"

knobSketch = sketch(on = XY) {
  knobCircle = circle(start = [var 0.25in, var 0in], center = [var 0in, var 0in])
  coincident([knobCircle.center, ORIGIN])
  diameter(knobCircle) == knobDiameter
}
knobRegion = region(segments = [knobSketch.knobCircle])
knobBlank = extrude(knobRegion, length = knobHeight, tagEnd = $knobEnd)
knob = fillet(
  knobBlank,
  radius = knobFilletRadius,
  edges = [
    {
      sideFaces = [knobRegion.tags.knobCircle, knobEnd]
    }
  ],
)
  |> appearance(color = "#afbf36")
hide(knobSketch)

knob
```

### parameters.kcl

```kcl
// Global parameters for the walkie talkie

// Set units
@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

// body
export height = 4
export width = 2.5
export thickness = 1
export chamferLength = .325
export offset = .125
export screenWidth = 1.75
export screenHeight = 1
export screenYPosition = height / 2 - 0.75
export screenDepth = -.0625
export speakerBoxWidth = 1.25
export speakerBoxHeight = 1.25

// antenna
export antennaBaseWidth = .5
export antennaBaseHeight = .25
export antennaTopWidth = antennaBaseWidth * .5
export antennaTopHeight = antennaBaseHeight * .5
export antennaLength = 2

// button
export buttonWidth = .15
export tolerance = 0.020
export buttonHeight = screenHeight / 2 - tolerance
export buttonThickness = .040

// case
export squareHoleSideLength = 0.0625
export caseTolerance = 0.010

// knob
export knobDiameter = .5
export knobHeight = .25
export knobFilletRadius = 0.050

// talk-button
export talkButtonSideLength = 0.5
export talkButtonHeight = 0.050
```

### talk-button.kcl

```kcl
// Walkie talkie talk button

@settings(defaultLengthUnit = in, kclVersion = 2.0, experimentalFeatures = allow)

import talkButtonHeight from "parameters.kcl"

talkButtonSketch = sketch(on = YZ) {
  line1 = line(start = [var -0.25in, var 0.25in], end = [var 0.25in, var 0.25in])
  line2 = line(start = [var 0.25in, var 0.25in], end = [var 0.25in, var -0.25in])
  coincident([line1.end, line2.start])
  line3 = line(start = [var 0.25in, var -0.25in], end = [var -0.25in, var -0.25in])
  coincident([line2.end, line3.start])
  line4 = line(start = [var -0.25in, var -0.25in], end = [var -0.25in, var 0.25in])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
  horizontal(line1)
  vertical(line2)
  horizontal(line3)
  vertical(line4)
}

talkButtonRegion = region(segments = [
  talkButtonSketch.line1,
  talkButtonSketch.line2
])
talkButtonBlank = extrude(talkButtonRegion, length = talkButtonHeight)
talkButton = fillet(
  talkButtonBlank,
  radius = 0.050,
  edges = [
    {
      sideFaces = [
        talkButtonRegion.tags.line1,
        talkButtonRegion.tags.line2
      ]
    },
    {
      sideFaces = [
        talkButtonRegion.tags.line2,
        talkButtonRegion.tags.line3
      ]
    },
    {
      sideFaces = [
        talkButtonRegion.tags.line3,
        talkButtonRegion.tags.line4
      ]
    },
    {
      sideFaces = [
        talkButtonRegion.tags.line4,
        talkButtonRegion.tags.line1
      ]
    }
  ],
)
  |> appearance(color = "#D0FF01", metalness = 90, roughness = 90)
hide(talkButtonSketch)

talkButton
```

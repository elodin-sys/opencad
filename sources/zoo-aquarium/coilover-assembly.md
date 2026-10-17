Source URL: https://zoo.dev/aquarium/coilover-assembly
Title: Coilover Assembly

# Coilover Assembly

Consist of a lower and upper body combination with eye-end mounts at the top and bottom. 200 mm-long helical spring (44 mm OD, and wire diameter of 6 mm) captured between upper and lower seats; Internal piston rod running through the spring. Integrated bump-stop beneath the upper seat to limit compression stroke. The assembly provides adjustable ride height and damping when installed between chassis and wheel hub.

- Page: /aquarium/coilover-assembly
- Legacy docs page: /docs/kcl-samples/coilover-assembly
- Preview image: /kcl-samples/screenshots/coilover-assembly.png
- Categories: Automotive & Transportation, Mechanical Components

## Files

### main.kcl

```kcl
// Coilover Assembly
// Consist of a lower and upper body combination with eye-end mounts at the top and bottom. 200 mm-long helical spring (44 mm OD, and wire diameter of 6 mm) captured between upper and lower seats; Internal piston rod running through the spring. Integrated bump-stop beneath the upper seat to limit compression stroke. The assembly provides adjustable ride height and damping when installed between chassis and wheel hub.
// Categories: Automotive & Transportation; Mechanical Components

// Set units
@settings(defaultLengthUnit = mm, kclVersion = 2.0)

import "coilover-bottom.kcl" as coiloverBottom
import "spring.kcl" as coiloverSpring
import "coilover-top.kcl" as coiloverTop
```

### coilover-bottom.kcl

```kcl
// Coilover Bottom
// Part consists of a 70 mm diameter retainer plate with a cylindrical lower mount body below it, and a eye-end mount (or hole) at the bottom. Above the retainer plate, there is a cylindrical damper body with a hole through its length that allows a piston shaft to pass through it when included in the coilover assembly.

// Set units
@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Import parameters
import * from "parameters.kcl"

// Retainer Plate
retainerPlateProfile = sketch(on = XY) {
  anchor = line(start = [var 0mm, var 0mm], end = [var 35mm, var 0mm], construction = true)
  circle1 = circle(start = [var 35mm, var 0mm], center = [var 0mm, var 0mm])

  coincident([anchor.start, ORIGIN])
  coincident([anchor.end, [retainerPlateRadius, 0mm]])
  horizontal(anchor)

  coincident([circle1.center, anchor.start])
  coincident([circle1.start, anchor.end])
}
region001 = region(segments = [retainerPlateProfile.circle1])
retainerPlateExtrude = extrude(region001, length = retainerPlateLength, tagStart = $capStart001)
  |> chamfer(
       length = retainerPlateChamfer,
       tags = [
         getCommonEdge(faces = [region001.tags.circle1, capStart001])
       ],
     )

hide(retainerPlateProfile)

baseSeatingPlane = planeOf(retainerPlateExtrude, face = START)
baseSeatingProfile = sketch(on = baseSeatingPlane) {
  anchor = line(start = [var 0mm, var 0mm], end = [var 27.5mm, var 0mm], construction = true)
  circle1 = circle(start = [var 27.5mm, var 0mm], center = [var 0mm, var 0mm])

  coincident([anchor.start, ORIGIN])
  coincident([anchor.end, [baseSeatingRadius, 0mm]])
  horizontal(anchor)

  coincident([circle1.center, anchor.start])
  coincident([circle1.start, anchor.end])
}
region002 = region(segments = [baseSeatingProfile.circle1])
baseSeatingExtrude = extrude(region002, length = baseSeatingLength)

hide(baseSeatingProfile)

// Lower Mount
lowerMountPlane = planeOf(baseSeatingExtrude, face = END)
lowerMountProfile = sketch(on = lowerMountPlane) {
  anchor = line(start = [var 0mm, var 0mm], end = [var 19mm, var 0mm], construction = true)
  circle1 = circle(start = [var 19mm, var 0mm], center = [var 0mm, var 0mm])

  coincident([anchor.start, ORIGIN])
  coincident([anchor.end, [lowerMountRadius, 0mm]])
  horizontal(anchor)

  coincident([circle1.center, anchor.start])
  coincident([circle1.start, anchor.end])
}
region003 = region(segments = [lowerMountProfile.circle1])
lowerMountExtrude = extrude(region003, length = lowerMountLength, tagEnd = $capEnd001)
  |> chamfer(
       length = lowerMountChamfer,
       tags = [
         getCommonEdge(faces = [region003.tags.circle1, capEnd001])
       ],
     )

hide(lowerMountProfile)

// Eye End for Lower Mount
eyeEndPlane = planeOf(lowerMountExtrude, face = END)
eyeEndProfile = sketch(on = eyeEndPlane) {
  anchor = line(start = [var 0mm, var 0mm], end = [var 12.5mm, var 0mm], construction = true)
  circle1 = circle(start = [var 12.5mm, var 0mm], center = [var 0mm, var 0mm])

  coincident([anchor.start, ORIGIN])
  coincident([anchor.end, [eyeEndMountRadius, 0mm]])
  horizontal(anchor)

  coincident([circle1.center, anchor.start])
  coincident([circle1.start, anchor.end])
}
region004 = region(segments = [eyeEndProfile.circle1])
eyeEndExtrude = extrude(
  region004,
  length = eyeEndMountLength,
  tagStart = $capStart002,
  tagEnd = $capEnd002,
)
  |> fillet(
       radius = eyeEndTipFillet,
       tags = [
         getCommonEdge(faces = [region004.tags.circle1, capEnd002])
       ],
     )
  |> fillet(
       radius = eyeEndRootFillet,
       tags = [
         getCommonEdge(faces = [region004.tags.circle1, capStart002])
       ],
     )

hide(eyeEndProfile)

// Eye End Outer Profile for Lower Mount
eyeEndOuterProfile = sketch(on = YZ) {
  line1 = line(start = [var 31.35mm, var -114.5mm], end = [var 11.35mm, var -114.5mm])
  arc2 = arc(start = [var 11.35mm, var -114.5mm], end = [var 6.35mm, var -119.5mm], center = [var 11.35mm, var -119.5mm])
  line3 = line(start = [var 6.35mm, var -119.5mm], end = [var 6.35mm, var -141.5mm])
  line4 = line(start = [var 6.35mm, var -141.5mm], end = [var -6.35mm, var -141.5mm])
  line5 = line(start = [var -6.35mm, var -141.5mm], end = [var -6.35mm, var -119.5mm])
  arc6 = arc(start = [var -6.35mm, var -119.5mm], end = [var -11.35mm, var -114.5mm], center = [var -11.35mm, var -119.5mm])
  line7 = line(start = [var -11.35mm, var -114.5mm], end = [var -31.35mm, var -114.5mm])
  line8 = line(start = [var -31.35mm, var -114.5mm], end = [var -31.35mm, var -144.5mm])
  line9 = line(start = [var -31.35mm, var -144.5mm], end = [var 31.35mm, var -144.5mm])
  line10 = line(start = [var 31.35mm, var -144.5mm], end = [var 31.35mm, var -114.5mm])

  coincident([line1.end, arc2.start])
  coincident([arc2.end, line3.start])
  coincident([line3.end, line4.start])
  coincident([line4.end, line5.start])
  coincident([line5.end, arc6.start])
  coincident([arc6.end, line7.start])
  coincident([line7.end, line8.start])
  coincident([line8.end, line9.start])
  coincident([line9.end, line10.start])
  coincident([line10.end, line1.start])

  horizontal(line1)
  vertical(line3)
  horizontal(line4)
  vertical(line5)
  horizontal(line7)
  vertical(line8)
  horizontal(line9)
  vertical(line10)

  tangent([line1, arc2])
  tangent([arc2, line3])
  tangent([line5, arc6])
  tangent([arc6, line7])

  radius(arc2) == eyeEndShoulderRadius
  radius(arc6) == eyeEndShoulderRadius

  horizontalDistance([arc2.center, line1.end]) == 0mm
  verticalDistance([arc2.center, line3.start]) == 0mm
  horizontalDistance([arc6.center, line7.start]) == 0mm
  verticalDistance([arc6.center, line5.end]) == 0mm

  horizontalDistance([ORIGIN, line1.start]) == eyeEndOuterHalfWidth
  verticalDistance([ORIGIN, line1.start]) == eyeEndCutTop

  distance([line1.start, line1.end]) == eyeEndOuterHalfWidth - eyeEndShoulderHalfWidth
  equalLength([line1, line7])
  distance([line3.start, line3.end]) == eyeEndSlotTop - eyeEndSlotBottom
  equalLength([line3, line5])
  distance([line4.start, line4.end]) == eyeEndSlotHalfWidth * 2
  distance([line8.start, line8.end]) == eyeEndCutTop - eyeEndCutBottom
  equalLength([line8, line10])
  distance([line9.start, line9.end]) == eyeEndOuterHalfWidth * 2
}

region005 = region(segments = [eyeEndOuterProfile.line1])
eyeEndOuterExtrude = extrude(region005, length = eyeEndCutThickness, symmetric = true)
lowerMount = subtract([eyeEndExtrude], tools = [eyeEndOuterExtrude])

hide(eyeEndOuterProfile)

// Eye End Hole for Lower Mount
eyeEndHoleCenterZ = -(baseSeatingLength + lowerMountLength + eyeEndMountLength) + eyeEndMountRadius
eyeEndHolePlane = offsetPlane(XZ, offset = eyeEndCutThickness / 2)
eyeEndHoleProfile = sketch(on = eyeEndHolePlane) {
  circle1 = circle(start = [var 6mm, var -127mm], center = [var 0mm, var -126mm])
  radiusGuide = line(start = [var 1mm, var -128mm], end = [var 7mm, var -128mm], construction = true)

  coincident([radiusGuide.start, circle1.center])
  coincident([radiusGuide.end, circle1.start])
  horizontal(radiusGuide)

  horizontalDistance([ORIGIN, circle1.center]) == 0mm
  verticalDistance([ORIGIN, circle1.center]) == eyeEndHoleCenterZ
  horizontalDistance([radiusGuide.start, radiusGuide.end]) == eyeEndMountRadius / 2
}

region006 = region(segments = [eyeEndHoleProfile.circle1])
eyeEndHoleExtrude = extrude(region006, length = -40mm, method = NEW)
lowerMountSolid = subtract([lowerMount], tools = [eyeEndHoleExtrude])

hide(eyeEndHoleProfile)

damperBodyProfile = sketch(on = XY) {
  anchor = line(start = [var 0mm, var 0mm], end = [var 19mm, var 0mm], construction = true)
  circle1 = circle(start = [var 19mm, var 0mm], center = [var 0mm, var 0mm])

  coincident([anchor.start, ORIGIN])
  coincident([anchor.end, [lowerMountRadius, 0mm]])
  horizontal(anchor)

  coincident([circle1.center, anchor.start])
  coincident([circle1.start, anchor.end])
}
region007 = region(segments = [damperBodyProfile.circle1])
damperBodyExtrude = extrude(region007, length = damperBodyLength)

hide(damperBodyProfile)

// Hole for the piston shaft in the damper body
pistonShaftPlane = planeOf(damperBodyExtrude, face = END)
pistonShaftProfile = sketch(on = pistonShaftPlane) {
  anchor = line(start = [var 0mm, var 0mm], end = [var 5mm, var 0mm], construction = true)
  circle1 = circle(start = [var 5mm, var 0mm], center = [var 0mm, var 0mm])

  coincident([anchor.start, ORIGIN])
  coincident([
    anchor.end,
    [pistonShaftHoleRadius, 0mm]
  ])
  horizontal(anchor)

  coincident([circle1.center, anchor.start])
  coincident([circle1.start, anchor.end])
}
region008 = region(segments = [pistonShaftProfile.circle1])
pistonShaftHoleCutter = extrude(region008, length = -damperBodyLength, method = NEW)
damperBodySolid = subtract([damperBodyExtrude], tools = [pistonShaftHoleCutter])

hide(pistonShaftProfile)

buildCoiloverBottom = union([lowerMountSolid, damperBodySolid])
```

### coilover-top.kcl

```kcl
// Coilover Top
// Part consists of a 70 mm diameter plate with a tapered mount body , and a eye-end mount (with a hole) on top of it. Below this plate/body, there is a stopper that limits the travel of the coilover, and a piston shaft below it to guide the coilover.

// Set units
@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Import parameters
import * from "parameters.kcl"

// Stopper for the Piston Rod located just below Upper Mount Plate
upperStopperProfile = sketch(on = XY) {
  anchor = line(start = [var 0mm, var 0mm], end = [var 12.5mm, var 0mm], construction = true)
  circle1 = circle(start = [var 12.5mm, var 0mm], center = [var 0mm, var 0mm])

  coincident([anchor.start, ORIGIN])
  coincident([anchor.end, [eyeEndMountRadius, 0mm]])
  horizontal(anchor)

  coincident([circle1.center, anchor.start])
  coincident([circle1.start, anchor.end])
}
region010 = region(segments = [upperStopperProfile.circle1])
upperStopperExtrude = extrude(region010, length = -upperPistonRodStopLength, tagStart = $upperCapStart001)
  |> chamfer(
       length = 6mm,
       tags = [
         getCommonEdge(faces = [
           region010.tags.circle1,
           upperCapStart001
         ])
       ],
     )

hide(upperStopperProfile)

// Piston Rod located below the Stopper
upperPistonRodPlane = planeOf(upperStopperExtrude, face = START)
upperPistonRodProfile = sketch(on = upperPistonRodPlane) {
  anchor = line(start = [var 0mm, var 0mm], end = [var 4.95mm, var 0mm], construction = true)
  circle1 = circle(start = [var 4.95mm, var 0mm], center = [var 0mm, var 0mm])

  coincident([anchor.start, ORIGIN])
  coincident([
    anchor.end,
    [upperPistonRodRadius, 0mm]
  ])
  horizontal(anchor)

  coincident([circle1.center, anchor.start])
  coincident([circle1.start, anchor.end])
}
region011 = region(segments = [upperPistonRodProfile.circle1])
upperPistonRodExtrude = extrude(region011, length = 200mm)

hide(upperPistonRodProfile)

// Upper Mount Plate
upperMountPlatePlane = planeOf(upperStopperExtrude, face = END)
upperMountPlateProfile = sketch(on = upperMountPlatePlane) {
  anchor = line(start = [var 0mm, var 0mm], end = [var 35mm, var 0mm], construction = true)
  circle1 = circle(start = [var 35mm, var 0mm], center = [var 0mm, var 0mm])

  coincident([anchor.start, ORIGIN])
  coincident([anchor.end, [retainerPlateRadius, 0mm]])
  horizontal(anchor)

  coincident([circle1.center, anchor.start])
  coincident([circle1.start, anchor.end])
}
region012 = region(segments = [upperMountPlateProfile.circle1])
upperMountPlateExtrude = extrude(region012, length = upperMountPlateThickness, tagEnd = $upperCapEnd002)
  |> chamfer(
       length = 19mm,
       tags = [
         getCommonEdge(faces = [region012.tags.circle1, upperCapEnd002])
       ],
     )

hide(upperMountPlateProfile)

// Eye End for Upper Mount
upperEyeEndPlane = planeOf(upperMountPlateExtrude, face = END)
upperEyeEndProfile = sketch(on = upperEyeEndPlane) {
  anchor = line(start = [var 0mm, var 0mm], end = [var 12.5mm, var 0mm], construction = true)
  circle1 = circle(start = [var 12.5mm, var 0mm], center = [var 0mm, var 0mm])

  coincident([anchor.start, ORIGIN])
  coincident([anchor.end, [eyeEndMountRadius, 0mm]])
  horizontal(anchor)

  coincident([circle1.center, anchor.start])
  coincident([circle1.start, anchor.end])
}
region013 = region(segments = [upperEyeEndProfile.circle1])
upperEyeEndExtrude = extrude(region013, length = eyeEndMountLength, tagEnd = $upperCapEnd003)
  |> fillet(
       radius = eyeEndTipFillet,
       tags = [
         getCommonEdge(faces = [region013.tags.circle1, upperCapEnd003])
       ],
     )

hide(upperEyeEndProfile)

// Eye End Outer Profile for Upper Mount
upperEyeEndOuterProfile = sketch(on = YZ) {
  line1 = line(start = [var 31.35mm, var 40mm], end = [var 11.35mm, var 40mm])
  line3 = line(start = [var 6.35mm, var 45mm], end = [var 6.35mm, var 67mm])
  line4 = line(start = [var 6.35mm, var 67mm], end = [var -6.35mm, var 67mm])
  line5 = line(start = [var -6.35mm, var 67mm], end = [var -6.35mm, var 45mm])
  line7 = line(start = [var -11.35mm, var 40mm], end = [var -31.35mm, var 40mm])
  line8 = line(start = [var -31.35mm, var 40mm], end = [var -31.35mm, var 70mm])
  line9 = line(start = [var -31.35mm, var 70mm], end = [var 31.35mm, var 70mm])
  line10 = line(start = [var 31.35mm, var 70mm], end = [var 31.35mm, var 40mm])
  coincident([line3.end, line4.start])
  coincident([line4.end, line5.start])

  coincident([line7.end, line8.start])
  coincident([line8.end, line9.start])
  coincident([line9.end, line10.start])
  coincident([line10.end, line1.start])
  horizontal(line1)
  vertical(line3)
  horizontal(line4)
  vertical(line5)
  horizontal(line7)
  vertical(line8)

  horizontal(line9)
  vertical(line10)
  horizontalDistance([ORIGIN, line1.start]) == eyeEndOuterHalfWidth
  verticalDistance([ORIGIN, line1.start]) == upperEyeEndCutTop
  distance([line1.start, line1.end]) == eyeEndOuterHalfWidth - eyeEndShoulderHalfWidth
  equalLength([line1, line7])
  distance([line3.start, line3.end]) == upperEyeEndSlotBottom - upperEyeEndSlotTop
  equalLength([line3, line5])

  distance([line4.start, line4.end]) == eyeEndSlotHalfWidth * 2
  distance([line8.start, line8.end]) == upperEyeEndCutBottom - upperEyeEndCutTop
  equalLength([line8, line10])
  distance([line9.start, line9.end]) == eyeEndOuterHalfWidth * 2
  arc1 = arc(start = [var -11.35mm, var 40.03mm], end = [var -6.35mm, var 45.03mm], center = [var -11.35mm, var 45.03mm])
  coincident([arc1.end, line5.end])
  coincident([line7.start, arc1.start])
  tangent([line7, arc1])
  arc2 = arc(start = [var 6.35mm, var 45mm], end = [var 11.35mm, var 40mm], center = [var 11.35mm, var 45mm])
  coincident([arc2.start, line3.start])
  coincident([line1.end, arc2.end])
  tangent([line1, arc2])
  radius(arc1) == 5mm
  radius(arc2) == 5mm
}
region014 = region(segments = [
  upperEyeEndOuterProfile.line1,
  upperEyeEndOuterProfile.arc2
])
upperEyeEndOuterExtrude = extrude(region014, length = eyeEndCutThickness, symmetric = true)
upperMount = subtract([upperEyeEndExtrude], tools = [upperEyeEndOuterExtrude])

hide(upperEyeEndOuterProfile)

// Eye End Hole for Upper Mount
upperEyeEndHolePlane = offsetPlane(XZ, offset = eyeEndCutThickness / 2)
upperEyeEndHoleProfile = sketch(on = upperEyeEndHolePlane) {
  circle1 = circle(start = [var 6mm, var 53mm], center = [var 0mm, var 52mm])
  radiusGuide = line(start = [var 1mm, var 52mm], end = [var 7mm, var 52mm], construction = true)

  coincident([radiusGuide.start, circle1.center])
  coincident([radiusGuide.end, circle1.start])
  horizontal(radiusGuide)

  horizontalDistance([ORIGIN, circle1.center]) == 0mm
  verticalDistance([ORIGIN, circle1.center]) == upperEyeEndHoleCenterZ
  horizontalDistance([radiusGuide.start, radiusGuide.end]) == eyeEndMountRadius / 2
}
region015 = region(segments = [upperEyeEndHoleProfile.circle1])
upperEyeEndHoleExtrude = extrude(region015, length = -40mm, method = NEW)
upperMountSolid = subtract([upperMount], tools = [upperEyeEndHoleExtrude])
  |> appearance(color = "#252318", roughness = 90, metalness = 90)

hide(upperEyeEndHoleProfile)

translatedUpperPistonRod = translate(upperPistonRodExtrude, z = 200mm)
translatedUpperMountPlate = translate(upperMountPlateExtrude, z = 200mm)
translatedUpperStopper = translate(upperStopperExtrude, z = 200mm)
translatedUpperMount = translate(upperMountSolid, z = 200mm)

coiloverTop = [
  translatedUpperPistonRod,
  translatedUpperMountPlate,
  translatedUpperStopper,
  translatedUpperMount
]
```

### parameters.kcl

```kcl
// Coilover assembly parameters
// Key dimensional parameters for all parts in the coilover assembly. These are imported into the kcl part files. Key parameters include retainer plate, eye mount, spring and piston rod dimensions.

// Set units
@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Coilover Bottom (coilover-bottom.kcl)
export retainerPlateLength = 6.3mm
export retainerPlateRadius = 35mm
export retainerPlateChamfer = 3.7mm
export baseSeatingLength = 5mm
export baseSeatingRadius = 27.5mm
export lowerMountLength = 92mm
export lowerMountRadius = 19mm
export lowerMountChamfer = 3mm
export eyeEndMountRadius = 12.5mm
export eyeEndMountLength = eyeEndMountRadius + 30mm
export eyeEndTipFillet = eyeEndMountRadius - 0.01mm
export eyeEndRootFillet = 3mm
export eyeEndOuterHalfWidth = 31.35mm
export eyeEndShoulderHalfWidth = 11.35mm
export eyeEndSlotHalfWidth = 6.35mm
export eyeEndCutTop = -114.5mm
export eyeEndCutBottom = -144.5mm
export eyeEndSlotTop = -119.5mm
export eyeEndSlotBottom = -141.5mm
export eyeEndShoulderRadius = 5mm
export eyeEndCutThickness = 30mm
export damperBodyLength = 51mm
export pistonShaftHoleRadius = 5mm

// Coilover Spring (spring.kcl)
export springRadius = 22mm
export springLength = 200mm
export springRevolutions = 8
export coilThickness = 6mm

// Coilover Top (coilover-top.kcl)
export upperPistonRodStopLength = 32.5mm
export upperPistonRodRadius = 4.95mm
export upperMountPlateThickness = 22.5mm
export upperEyeEndCutTop = 40mm
export upperEyeEndCutBottom = 70mm
export upperEyeEndSlotTop = 45mm
export upperEyeEndSlotBottom = 67mm
export upperEyeEndHoleCenterZ = 52.5mm
```

### spring.kcl

```kcl
// Spring for coilover assembly
// Spring that sits on top of the retainer plate in the coilover assembly, with a piston shaft running through it. 200 mm long, with a 22 mm radius, and coils at 6 mm thick.

@settings(defaultLengthUnit = mm, kclVersion = 2.0)

import * from "parameters.kcl"

springPath = helix(
  axis = Z,
  radius = springRadius,
  length = springLength,
  revolutions = springRevolutions,
  angleStart = 360,
  ccw = false,
)

springProfile = sketch(on = XZ) {
  radiusGuide = line(start = [var 22mm, var 0mm], end = [var 25mm, var 0mm], construction = true)
  circle1 = circle(start = [var 25mm, var 0mm], center = [var 22mm, var 0mm])

  coincident([radiusGuide.start, circle1.center])
  coincident([radiusGuide.end, circle1.start])
  horizontal(radiusGuide)

  horizontalDistance([ORIGIN, radiusGuide.start]) == springRadius
  verticalDistance([ORIGIN, radiusGuide.start]) == 0mm
  horizontalDistance([radiusGuide.start, radiusGuide.end]) == coilThickness / 2
}
region001 = region(segments = [springProfile.circle1])
coiloverSpring = sweep(region001, path = springPath)
  |> appearance(color = "#d78109", roughness = 90, metalness = 50)

hide(springProfile)
```

Source URL: https://zoo.dev/aquarium/axial-fan
Title: PC Fan

# PC Fan

A small axial fan, used to push or draw airflow over components to remove excess heat

- Page: /aquarium/axial-fan
- Legacy docs page: /docs/kcl-samples/axial-fan
- Preview image: /kcl-samples/screenshots/axial-fan.png
- Categories: Electronics & Computing, Mechanical Components

## Files

### main.kcl

```kcl
// PC Fan
// A small axial fan, used to push or draw airflow over components to remove excess heat
// Categories: Electronics & Computing; Mechanical Components

// Set units
@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Import all parts into assembly file
import "fan-housing.kcl" as fanHousing
import "motor.kcl" as motor
import "fan.kcl" as fan

// Produce the model for each imported part
fanHousing
motor
fan
```

### fan-housing.kcl

```kcl
// Fan Housing
// The plastic housing that contains the fan and the motor

// Set units
@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Import parameters
import * from "parameters.kcl"

// Create the housing body
sketch001 = sketch(on = XY) {
  line1 = line(start = [var -52.5mm, var -52.5mm], end = [var 52.5mm, var -52.5mm], construction = true)
  line2 = line(start = [var 52.5mm, var -52.5mm], end = [var 52.5mm, var 52.5mm], construction = true)
  line3 = line(start = [var 52.5mm, var 52.5mm], end = [var -52.5mm, var 52.5mm], construction = true)
  line4 = line(start = [var -52.5mm, var 52.5mm], end = [var -52.5mm, var -52.5mm], construction = true)
  coincident([line1.end, line2.start])
  coincident([line2.end, line3.start])
  coincident([line3.end, line4.start])
  coincident([line4.end, line1.start])
  parallel([line2, line4])
  parallel([line3, line1])
  perpendicular([line1, line2])
  horizontal(line3)
  line5 = line(start = [var -62.5mm, var -62.5mm], end = [var 62.5mm, var -62.5mm], construction = true)
  line6 = line(start = [var 62.5mm, var -62.5mm], end = [var 62.5mm, var 62.5mm], construction = true)
  line7 = line(start = [var 62.5mm, var 62.5mm], end = [var -62.5mm, var 62.5mm], construction = true)
  line8 = line(start = [var -62.5mm, var 62.5mm], end = [var -62.5mm, var -62.5mm], construction = true)
  coincident([line5.end, line6.start])
  coincident([line6.end, line7.start])
  coincident([line7.end, line8.start])
  coincident([line8.end, line5.start])
  parallel([line6, line8])
  parallel([line7, line5])
  perpendicular([line5, line6])
  horizontal(line7)
  line9 = line(start = [var -52.5mm, var -52.5mm], end = [var 0mm, var 0mm], construction = true)
  coincident([line9.start, line4.end])
  coincident([line9.end, ORIGIN])
  line10 = line(start = [var 0mm, var 0mm], end = [var 52.5mm, var 52.5mm], construction = true)
  coincident([line10.start, line9.end])
  coincident([line10.end, line3.start])
  line11 = line(start = [var 62.5mm, var -62.5mm], end = [var 0mm, var 0mm], construction = true)
  coincident([line11.start, line6.start])
  coincident([line11.end, line10.start])
  line12 = line(start = [var -62.5mm, var 62.5mm], end = [var 0mm, var 0mm], construction = true)
  coincident([line12.start, line8.start])
  coincident([line12.end, line11.end])
  equalLength([line12, line11])
  parallel([line11, line12])
  parallel([line9, line10])
  equalLength([line10, line9])
  equalLength([line5, line6, line7, line8])
  distance([line5.start, line5.end]) == 125
  equalLength([line1, line2, line3, line4])
  distance([line1.start, line1.end]) == mountingHoleSpacing
  circle1 = circle(start = [var -51.24mm, var 50.64mm], center = [var -52.5mm, var 52.5mm])
  coincident([circle1.center, line4.start])
  circle2 = circle(start = [var 50.89mm, var 50.93mm], center = [var 52.5mm, var 52.5mm])
  coincident([circle2.center, line3.start])
  circle3 = circle(start = [var 54.32mm, var -51.18mm], center = [var 52.5mm, var -52.5mm])
  coincident([circle3.center, line2.start])
  circle4 = circle(start = [var -50.33mm, var -53.1mm], center = [var -52.5mm, var -52.5mm])
  coincident([circle4.center, line1.start])
  equalRadius([circle4, circle3, circle2, circle1])
  diameter(circle2) == mountingHoleSize
  circle5 = circle(start = [var 16.55mm, var 57.67mm], center = [var 0mm, var 0mm])
  coincident([circle5.center, line10.start])
  diameter(circle5) == fanSize
  line13 = line(start = [var -62.5mm, var -56.5mm], end = [var -62.5mm, var 56.5mm])
  coincident([line13.start, line8])
  coincident([line13.end, line8])
  line14 = line(start = [var -56.5mm, var 62.5mm], end = [var 56.5mm, var 62.5mm])
  coincident([line14.start, line7])
  coincident([line14.end, line7])
  line15 = line(start = [var 62.5mm, var 56.5mm], end = [var 62.5mm, var -56.5mm])
  coincident([line15.start, line6])
  coincident([line15.end, line6])
  line16 = line(start = [var 56.5mm, var -62.5mm], end = [var -56.5mm, var -62.5mm])
  coincident([line16.start, line5])
  coincident([line16.end, line5])
  arc1 = arc(start = [var -62.5mm, var -56.5mm], end = [var -56.5mm, var -62.5mm], center = [var -56.5mm, var -56.5mm])
  coincident([arc1.start, line13.start])
  coincident([line16.end, arc1.end])
  tangent([line16, arc1])
  arc2 = arc(start = [var -56.5mm, var 62.5mm], end = [var -62.5mm, var 56.5mm], center = [var -56.5mm, var 56.5mm])
  coincident([arc2.start, line14.start])
  coincident([line13.end, arc2.end])
  tangent([line13, arc2])
  arc3 = arc(start = [var 62.5mm, var 56.5mm], end = [var 56.5mm, var 62.5mm], center = [var 56.5mm, var 56.5mm])
  coincident([arc3.start, line15.start])
  coincident([line14.end, arc3.end])
  tangent([line14, arc3])
  arc4 = arc(start = [var 56.5mm, var -62.5mm], end = [var 62.5mm, var -56.5mm], center = [var 56.5mm, var -56.5mm])
  coincident([arc4.start, line16.start])
  coincident([line15.end, arc4.end])
  tangent([line15, arc4])
  tangent([line13, arc1])
  tangent([line14, arc2])
  tangent([line15, arc3])
  tangent([line16, arc4])
  equalRadius([arc4, arc1, arc2, arc3])
  radius(arc3) == 6
}
region001 = region(segments = [sketch001.line13, sketch001.arc2], direction = CW)
hidden001 = hide(sketch001)
extrude001 = extrude(region001, length = 25)

// Draw the revolved cut to trim the corners
sketch002 = sketch(on = XZ) {
  line1 = line(start = [var 116.61mm, var 2.55mm], end = [var 65mm, var 2.55mm], construction = true)
  point2 = point(at = [var 64mm, var 7mm])
  point3 = point(at = [var 64mm, var 12.58mm])
  point4 = point(at = [var 64.02mm, var 18.26mm])
  line6 = line(start = [var 65mm, var 22.55mm], end = [var 117.16mm, var 22.55mm], construction = true)
  line7 = line(start = [var 117.16mm, var 22.55mm], end = [var 116.61mm, var 2.55mm])
  coincident([line6.end, line7.start])
  coincident([line7.end, line1.start])
  line9 = line(start = [var 0mm, var 0mm], end = [var 65mm, var 0mm], construction = true)
  coincident([line9.start, ORIGIN])
  line10 = line(start = [var 0mm, var 0mm], end = [var 0mm, var 25.09mm], construction = true)
  coincident([line10.start, line9.start])
  vertical([line10.end, ORIGIN])
  line11 = line(start = [var 0mm, var 25.09mm], end = [var 65mm, var 25.09mm], construction = true)
  coincident([line11.start, line10.end])
  distance([line10.start, line10.end]) == 25.09mm
  horizontal(line11)
  horizontal(line9)
  line12 = line(start = [var 65mm, var 2.55mm], end = [var 65mm, var 0mm], construction = true)
  line13 = line(start = [var 65mm, var 22.55mm], end = [var 65mm, var 25.09mm], construction = true)
  coincident([line11.end, line13.end])
  coincident([line9.end, line12.end])
  equalLength([line13, line12])
  vertical(line12)
  vertical(line13)
  coincident([line13, line12])
  horizontal(line1)
  horizontal(line6)
  distance([line9.start, line9.end]) == 65
  point5 = point(at = [var 65.24mm, var 22.19mm])
  arc4 = arc(start = [var 66mm, var 22.55mm], end = [var 65mm, var 21.55mm], center = [var 66mm, var 21.55mm])
  coincident([arc4.start, line6])
  coincident([point5, arc4])
  tangent([line6, arc4])
  point6 = point(at = [var 65.33mm, var 2.8mm])
  arc5 = arc(start = [var 65mm, var 3.55mm], end = [var 66mm, var 2.55mm], center = [var 66mm, var 3.55mm])
  coincident([point6, arc5])
  tangent([line1, arc5])
  line15 = line(start = [var 66mm, var 2.55mm], end = [var 116.61mm, var 2.55mm])
  coincident([line15.start, arc5.end])
  coincident([line15.end, line7.end])
  line18 = line(start = [var 66mm, var 22.55mm], end = [var 117.16mm, var 22.55mm])
  coincident([line18.end, line7.start])
  coincident([line18.start, arc4.start])
  equalRadius([arc4, arc5])
  coincident([line15.start, line1])
  line2 = line(start = [var 65mm, var 21.55mm], end = [var 65mm, var 3.55mm])
  coincident([line2.start, arc4.end])
  coincident([line2.end, arc5.start])
}
region002 = region(segments = [sketch002.line15, sketch002.line7])
hidden002 = hide(sketch002)
revolve001 = revolve(region002, angle = 360deg, axis = Y)

solid001 = subtract(extrude001, tools = revolve001)

// Draw the airflow pattern on the back face of the fan
sketch003 = sketch(on = XY) {
  arc1 = arc(start = [var -0.02mm, var 6mm], end = [var -3.44mm, var 4.92mm], center = [var 0mm, var 0mm])
  coincident([arc1.center, ORIGIN])
  line1 = line(start = [var -0.02mm, var 6mm], end = [var 59.7mm, var 6mm])
  coincident([line1.start, arc1.start])
  arc2 = arc(start = [var 59.7mm, var 6mm], end = [var 58.79mm, var 12mm], center = [var 0mm, var 0mm])
  coincident([arc2.center, arc1.center])
  coincident([arc2.start, line1.end])
  line2 = line(start = [var 58.79mm, var 12mm], end = [var 2.94mm, var 12mm])
  coincident([line2.start, arc2.end])
  arc3 = arc(start = [var -2.26mm, var 15mm], end = [var 2.94mm, var 12mm], center = [var 2.94mm, var 18mm])
  coincident([line2.end, arc3.end])
  tangent([line2, arc3])
  line3 = line(start = [var -2.26mm, var 15mm], end = [var -25.07mm, var 54.51mm])
  coincident([line3.start, arc3.start])
  tangent([line3, arc3])
  arc4 = arc(start = [var -25.07mm, var 54.51mm], end = [var -30.45mm, var 51.7mm], center = [var 0mm, var 0mm])
  coincident([arc4.center, arc1.center])
  coincident([arc4.start, line3.end])
  line4 = line(start = [var -30.45mm, var 51.7mm], end = [var -3.44mm, var 4.92mm])
  coincident([line4.start, arc4.end])
  coincident([line4.end, arc1.end])
  equalRadius([arc2, arc4])
  diameter(arc2) == fanSize
  radius(arc1) == 6
  horizontal(line1)
  parallel([line2, line1])
  parallel([line3, line4])
  radius(arc3) == 6
  line5 = line(start = [var 59.7mm, var 6mm], end = [var 58.79mm, var 12mm], construction = true)
  coincident([line5.start, arc2.start])
  coincident([line5.end, line2.start])
  line6 = line(start = [var -25.07mm, var 54.51mm], end = [var -30.45mm, var 51.7mm], construction = true)
  coincident([line6.start, arc4.start])
  coincident([line6.end, line4.start])
  equalLength([line5, line6])
  verticalDistance([line5.start, line5.end]) == 6
  angleDimension(lines = [line3, line2], sector = 4, labelPosition = [7.16mm, 24.34mm]) == 120deg
  horizontalDistance([line1.start, arc4.center]) == 0.02mm
  coincident([arc4.center, line4])
}
hidden003 = hide(sketch003)
region003 = region(segments = [sketch003.arc1, sketch003.line1])
extrude002 = extrude(region003, length = 2)
pattern001 = patternCircular3d(
  extrude002,
  instances = 3,
  axis = Z,
  center = [0, 0, 0],
)
face001 = faceOf(extrude002, face = END)

// Mount a housing for the motor
sketch004 = sketch(on = face001) {
  circle1 = circle(start = [var -2.28mm, var 9.74mm], center = [var 0mm, var 0mm])
  coincident([circle1.center, ORIGIN])
  circle2 = circle(start = [var 7.51mm, var 9.36mm], center = [var 0mm, var 0mm])
  coincident([circle2.center, circle1.center])
  diameter(circle2) == 24
  diameter(circle1) == 20
}
hidden004 = hide(sketch004)
region004 = region(segments = [sketch004.circle2])
extrude003 = extrude(region004, length = 12)

// Apply appearance to all
appearance([solid001, extrude003], color = "#a55e2c")
```

### fan.kcl

```kcl
// Fan
// Spinning axial fan that moves airflow

// Set units
@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Import parameters
import * from "parameters.kcl"

// Model the center hub of the fan
sketch001 = sketch(on = XZ) {
  line1 = line(start = [var 0mm, var 25mm], end = [var -13.5mm, var 25mm])
  arc2 = arc(start = [var -13.5mm, var 25mm], end = [var -15mm, var 23.5mm], center = [var -13.5mm, var 23.5mm])
  coincident([line1.end, arc2.start])
  line3 = line(start = [var -15mm, var 23.5mm], end = [var -15mm, var 4.5mm])
  coincident([arc2.end, line3.start])
  line4 = line(start = [var -15mm, var 4.5mm], end = [var -13mm, var 4.5mm])
  coincident([line3.end, line4.start])
  line5 = line(start = [var -13mm, var 4.5mm], end = [var -13mm, var 20mm])
  coincident([line4.end, line5.start])
  arc6 = arc(start = [var -12mm, var 21mm], end = [var -13mm, var 20mm], center = [var -12mm, var 20mm])
  coincident([line5.end, arc6.end])
  line7 = line(start = [var -12mm, var 21mm], end = [var -1mm, var 21mm])
  coincident([arc6.start, line7.start])
  line8 = line(start = [var -1mm, var 21mm], end = [var -1mm, var 23mm])
  coincident([line7.end, line8.start])
  line9 = line(start = [var -1mm, var 23mm], end = [var -1.15mm, var 23mm])
  coincident([line8.end, line9.start])
  line10 = line(start = [var -1.15mm, var 23mm], end = [var -1mm, var 23.6mm])
  coincident([line9.end, line10.start])
  line11 = line(start = [var -1mm, var 23.6mm], end = [var 0mm, var 23.6mm])
  coincident([line10.end, line11.start])
  line12 = line(start = [var 0mm, var 23.6mm], end = [var 0mm, var 25mm])
  coincident([line11.end, line12.start])
  coincident([line12.end, line1.start])
}
region001 = region(segments = [sketch001.line1, sketch001.arc2])
hidden001 = hide(sketch001)
fanCenter = revolve(
  region001,
  axis = {
    direction = [0.0, 1.0],
    origin = [0.0, 0.0]
  },
)
  |> appearance(color = "#f3e2d8")

// Define blade construction
bladeBaseZ = 4.5
bladeLengthZ = fanHeight - 2 - bladeBaseZ
bladeRootAngle = 50deg
bladeOuterR = fanSize * 22 / 50
bladeInnerR = 15
bladeTwist = -bladeRootAngle

// Base planform sketch for one blade (on XY at bladeBaseZ)
bladeBase = sketch(on = offsetPlane(XY, offset = bladeBaseZ)) {
  arc2 = arc(start = [var 52.13mm, var 27.64mm], end = [var 6.88mm, var 13.4mm], center = [var 40.63mm, var -14.83mm])
  arc3 = arc(start = [var 52.89mm, var 26.14mm], end = [var 52.13mm, var 27.64mm], center = [var 0mm, var 0mm])
  coincident([arc2.start, arc3.end])
  arc4 = arc(start = [var 52.89mm, var 26.14mm], end = [var 7.96mm, var 12.78mm], center = [var 40.63mm, var -14.83mm])
  coincident([arc3.start, arc4.start])
  radius(arc3) == fanSize / 2 - 1
  coincident([arc3.center, ORIGIN])
  arc1 = arc(start = [var 7.96mm, var 12.78mm], end = [var 6.88mm, var 13.4mm], center = [var 0mm, var 0mm])
  coincident([arc1.center, arc3.center])
  radius(arc1) == 15.06mm
  coincident([arc4.end, arc1.start])
  coincident([arc2.end, arc1.end])
  coincident([arc4.center, arc2.center])
  line1 = line(start = [var 7.96mm, var 12.78mm], end = [var 30.43mm, var 19.46mm], construction = true)
  coincident([line1.start, arc1.start])
  line2 = line(start = [var 30.43mm, var 19.46mm], end = [var 52.89mm, var 26.14mm], construction = true)
  coincident([line1.end, line2.start])
  coincident([line2.end, arc4.start])
  line3 = line(start = [var 30.43mm, var 19.46mm], end = [var 40.63mm, var -14.83mm], construction = true)
  coincident([line3.start, line2.start])
  coincident([line3.end, arc4.center])
  coincident([line1, line2])
  equalLength([line1, line2])
  perpendicular([line3, line1])
  radius(arc4) == 42.77mm
  radius(arc2) == 44
}

region002 = region(segments = [bladeBase.arc1, bladeBase.arc2])
hidden002 = hide(bladeBase)
// Create the twisted blade solid and pattern
twistedBlade = extrude(
  region002,
  length = bladeLengthZ,
  twistAngle = bladeTwist,
  twistAngleStep = 12deg,
  twistCenter = [0, 0],
)
  |> appearance(color = "#f3e2d8")
  |> patternCircular3d(
       instances = 9,
       axis = [0, 0, 1],
       center = [0, 0, 0],
       arcDegrees = 360,
       rotateDuplicates = true,
     )
```

### motor.kcl

```kcl
// Motor
// A small electric motor to power the fan

// Set Units
@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Import Parameters
import * from "parameters.kcl"

// Model the motor body and stem


topFacePlane = offsetPlane(XY, offset = 4)
sketch001 = sketch(on = topFacePlane) {
  circle1 = circle(start = [var 10mm, var 0mm], center = [var 0mm, var 0mm])
  diameter(circle1) == 20mm
}
region001 = region(segments = [sketch001.circle1])
motorBody = extrude(
  region001,
  length = 17,
  tagStart = $capStart001,
  tagEnd = $capEnd001,
)
  |> appearance(color = "#021b55")
  |> fillet(
       tags = [
         getCommonEdge(faces = [region001.tags.circle1, capStart001]),
         getCommonEdge(faces = [region001.tags.circle1, capEnd001])
       ],
       radius = 2,
     )
sketch002 = sketch(on = offsetPlane(XY, offset = 21)) {
  circle1 = circle(start = [var 1mm, var 0mm], center = [var 0mm, var 0mm])
}
region002 = region(segments = [sketch002.circle1])
extrude(region002, length = 3.8)
  |> appearance(color = "#dbc89e")

hidden001 = hide(sketch001)
```

### parameters.kcl

```kcl
// Global parameters for the axial fan

// Set units
@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Define Parameters
export fanSize = 120
export fanHeight = 25
export mountingHoleSpacing = 105
export mountingHoleSize = 4.5
```

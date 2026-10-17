Source URL: https://zoo.dev/aquarium/herringbone-gear
Title: Herringbone Gear

# Herringbone Gear

A double-helical involute gear with opposing tooth angles and an 8 mm center bore.

- Page: /aquarium/herringbone-gear
- Legacy docs page: /docs/kcl-samples/herringbone-gear
- Preview image: /kcl-samples/screenshots/herringbone-gear.png
- Categories: Mechanical Components

## Files

### main.kcl

```kcl
// Herringbone Gear
// A double-helical involute gear with opposing tooth angles and an 8 mm center bore.
// Categories: Mechanical Components

@settings(defaultLengthUnit = mm, kclVersion = 2.0, experimentalFeatures = allow)

gearHeight = 8
gearBody = gear::herringbone(
  nTeeth = 25,
  module = 1,
  pressureAngle = 14deg,
  helixAngle = 40deg,
  gearHeight,
)

boreSketch = sketch(on = XY) {
  bore = circle(start = [var 4mm, var 0mm], center = [var 0mm, var 0mm])
  coincident([bore.center, ORIGIN])
  radius(bore) == 4mm
}
boreBody = extrude(region(segments = [boreSketch.bore]), length = gearHeight)
herringboneGear = subtract(gearBody, tools = [boreBody])
hide(boreSketch)
```

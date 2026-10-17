Source URL: https://zoo.dev/aquarium/torus
Title: Torus

# Torus

A torus is defined by its diameter and height.

- Page: /aquarium/torus
- Legacy docs page: /docs/kcl-samples/torus
- Preview image: /kcl-samples/screenshots/torus.png
- Categories: Science & Education, Parametric

## Files

### main.kcl

```kcl
// Torus
// A torus is defined by its diameter and height.
// Categories: Science & Education; Parametric

@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Define parameters
torusInnerDiameter = 20
crossSectionDiameter = 10

// create the profile for the cross section of the torus
profile = sketch(on = XY) {
  circle1 = circle(start = [var 20mm, var 0mm], center = [var 15mm, var 0mm])
}

region001 = region(segments = [profile.circle1])
// revolve the profile to create the torus
torus = revolve(region001, axis = Y, angle = 360.0)
```

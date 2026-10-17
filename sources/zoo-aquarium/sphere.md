Source URL: https://zoo.dev/aquarium/sphere
Title: Sphere

# Sphere

A sphere is a primitive shape defined by its diameter.

- Page: /aquarium/sphere
- Legacy docs page: /docs/kcl-samples/sphere
- Preview image: /kcl-samples/screenshots/sphere.png
- Categories: Science & Education, Parametric

## Files

### main.kcl

```kcl
// Sphere
// A sphere is a primitive shape defined by its diameter.
// Categories: Science & Education; Parametric

@settings(defaultLengthUnit = mm, kclVersion = 2.0)

// Define parameters
diameter = 10

// create the profile centered at the origin
profile = sketch(on = XY) {
  line1 = line(start = [var -5mm, var 0mm], end = [var 5mm, var 0mm])
  arc2 = arc(start = [var 5mm, var 0mm], end = [var -5mm, var 0mm], center = [var 0mm, var 0mm])
  coincident([line1.end, arc2.start])
  horizontal(line1)
  radius(arc2) == 5mm
}

region001 = region(segments = [profile.line1, profile.arc2])
// revolve the profile to create the sphere
sphere = revolve(region001, axis = X, angle = 360.0)
```

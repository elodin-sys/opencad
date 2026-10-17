# std::gear
Define gears that users can include in their models.
The gear will be placed at (0, 0, 0) in the global scene, and extruded up the Z axis. Use `translate()` and `rotate()` to move it around once it's created.
### helical !exp
`gear::helical(nTeeth: number(_), module: number(Length), pressureAngle: number(Angle), helixAngle: number(Angle), gearHeight: number(Length)): Solid`
```kcl
// Basic helical gear example.

@settings(defaultLengthUnit = mm, kclVersion = 1.0, experimentalFeatures = allow)

gearBody = gear::helical(
  nTeeth = 10,
  module = 2,
  pressureAngle = 20deg,
  helixAngle = 35deg,
  gearHeight = 7,
)
```
### herringbone !exp
`gear::herringbone(nTeeth: number(_), module: number(Length), pressureAngle: number(Angle), gearHeight: number(Length), helixAngle: number(Angle)): Solid`
```kcl
// Basic herringbone gear example.

@settings(defaultLengthUnit = mm, kclVersion = 1.0, experimentalFeatures = allow)

myGear = gear::herringbone(
  nTeeth = 10,
  module = 2,
  pressureAngle = 20deg,
  gearHeight = 5,
  helixAngle = 40deg,
)
```
### ring !exp
`gear::ring(nTeeth: number(_), module: number(Length), pressureAngle: number(Angle), helixAngle: number(Angle), gearHeight: number(Length)): Solid`
```kcl
// Basic example of a ring gear.

@settings(defaultLengthUnit = mm, kclVersion = 1.0, experimentalFeatures = allow)

gear::ring(
  nTeeth = 40,
  module = 1.5,
  pressureAngle = 14deg,
  helixAngle = -25deg,
  gearHeight = 5,
)
```
### spur !exp
`gear::spur(nTeeth: number(_), module: number(Length), pressureAngle: number(Angle), gearHeight: number(Length)): Solid`
```kcl
// Basic example of a spur gear.

@settings(defaultLengthUnit = mm, kclVersion = 1.0, experimentalFeatures = allow)

gear::spur(
  nTeeth = 21,
  module = 1.5,
  pressureAngle = 14deg,
  gearHeight = 6,
)
```

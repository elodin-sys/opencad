# std (root)
- `CCW: string`: Counterclockwise circular direction, currently used by `region()`.
- `CW: string`: Clockwise circular direction, currently used by `region()`.
- `END: TaggedFace`: Identifies the ending face of an extrusion.
- `MERGE: string`: Specifies that the extrusion will be pulled into or pushed out of the existing object, modifying it without creating a new object.
- `NEW: string`: Specifies that a new object is created during extrusion.
- `SOLID: string`: When bodies are solid, they have a top and bottom, and enclose all space between them.
- `START: TaggedFace`: Identifies the starting face of an extrusion.
- `SURFACE: string`: When bodies are surfaces, they have zero thickness.
- `X: Axis3d`, `Y: Axis3d`: The <name>-axis (can be used in both 2d and 3d contexts).
- `XY: Plane`: An abstract 3d plane aligned with the X and Y axes.
- `XZ: Plane`: An abstract 3d plane aligned with the X and Z axes.
- `YZ: Plane`: An abstract 3d plane aligned with the Y and Z axes.
- `Z: Axis3d`: The 3D Z-axis.
### assert
`assert(@actual: number, isGreaterThan?: number, isLessThan?: number, isGreaterThanOrEqual?: number, isLessThanOrEqual?: number, isEqualTo?: number, isNotEqualTo?: number, tolerance?: number, error?: string)`
- actual: If this is the boolean value true, assert passes. Otherwise it fails..
- isGreaterThan: If given, checks the `actual` value is greater than this.
- isLessThan: If given, checks the `actual` value is less than this.
- isGreaterThanOrEqual: If given, checks the `actual` value is greater than or equal to this.
- isLessThanOrEqual: If given, checks the `actual` value is less than or equal to this.
- isEqualTo: If given, checks the `actual` value is equal to this.
- isNotEqualTo: If given, checks the `actual` value is not equal to this.
- tolerance: If `isEqualTo` or `isNotEqualTo` is used, this is the tolerance to allow for the comparison.
- error: If the value was false, the program will terminate with this error message
### assertIs
`assertIs(@actual: bool, error?: string)`
- actual: If this is the boolean value true, assert passes.
```kcl
kclIsFun = true
assertIs(kclIsFun)
```
### clone
`clone(@geometries: [Sketch|Solid|ImportedGeometry; 1+]): [Sketch|Solid|ImportedGeometry; 1+]`
This doesn't really have much utility unless you need the equivalent of a double instance pattern with zero transformations.
Really only use this function if YOU ARE SURE you need it. In most cases you do not need clone and using a pattern with `instance = 2` is more appropriate.
```kcl
// Clone an imported model.

import "tests/inputs/cube.sldprt" as cube

myCube = cube

clonedCube = clone(myCube)
  |> translate(x = 1020)
  |> appearance(color = "#ff0000", metalness = 50, roughness = 50)
```
### edgeId
`edgeId(@body: Solid, index?: number(_), closestTo?: Point3d): Edge`
- closestTo: Uses absolute global coordinates.
### faceId
`faceId(@body: Solid, index: number(_)): TaggedFace`
### fail !exp
`fail(@msg: string): never`
Use `fail` when evaluation cannot continue and the caller should receive a specific error message. `fail` never returns a value.
```kcl
fn positive(@value: number): number {
  return if value > 0 {
    value
  } else {
    fail("value must be positive")
  }
}
```
### helix
`helix(revolutions: number(_), angleStart: number(Angle), ccw?: bool, radius?: number(Length), axis?: Axis3d|Edge|Segment|any, length?: number(Length), cylinder?: Solid): Helix`
- ccw: Is the helix rotation counter clockwise? The default is `false`.
- axis: Can be an Axis3d, an Edge, or a Segment when not using a cylinder. [face-api]
- length: This is not necessary if the helix is created around an edge. If not given the length of the edge is used.
### offsetPlane
`offsetPlane(@plane: Plane, offset: number(Length)): Plane`
- plane: The plane (e.g. `XY`) which this new plane is created from.

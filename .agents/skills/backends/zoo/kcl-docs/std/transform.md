# std::transform
This module contains functions for transforming sketches and solids.

Common args:
- global: If true, the transform is applied in global space. By default, the transform is applied in local sketch axis, therefore the origin will not move.
### delete !exp
`delete(@objects: [Solid; 1+]|[Sketch; 1+]|[Helix; 1+]|ImportedGeometry|[GdtAnnotation; 1+])`
- objects: [Sketch; 1+]
```kcl
// Basic example, showing deleting something.
@settings(kclVersion = 2.0, experimentalFeatures = allow)

// Make a cylinder
sketch001 = sketch(on = XY) {
  circle1 = circle(start = [var -2mm, var 1mm], center = [var -1mm, var 0.5mm])
}
cylinder = extrude(region(sketch = sketch001, point = sketch001.circle1.center), length = 5)
// Delete it
delete(cylinder)
```
### hide
`hide(@objects: [Solid; 1+]|[Plane; 1+]|[Sketch; 1+]|[Helix; 1+]|ImportedGeometry|[GdtAnnotation; 1+]): [Solid; 1+]|[Plane; 1+]|[Sketch; 1+]|[Helix; 1+]|ImportedGeometry|[GdtAnnotation; 1+]`
- objects: [Plane; 1+]
### mirror2d
`mirror2d(@sketches: [Sketch; 1+], axis: Axis2d|Edge|Segment): Sketch`
### mirror3d
`mirror3d(@bodies: [Solid; 1+], across: Edge|Plane|Axis3d|Segment|any): [Solid; 1+]`
- across: An edge specifier object such as `{ sideFaces = [faceTag1, faceTag2] }` can identify a solid edge without using its UUID.
### rotate
`rotate(@objects: [Solid; 1+]|[Sketch; 1+]|[Helix; 1+]|ImportedGeometry, roll?: number(Angle), pitch?: number(Angle), yaw?: number(Angle), axis?: Axis3d|Point3d, angle?: number(Angle), global?: bool): [Solid; 1+]|[Sketch; 1+]|[Helix; 1+]|ImportedGeometry`
By default, this does a local rotation, around the sketch/body's center. To rotate around the global scene coordinates, use `global = true`.
- axis: Must be used with `angle`.
- angle: Must be used with `axis`.
```kcl
// Rotate an imported model.

import "tests/inputs/cube.sldprt" as cube

cube
  |> rotate(axis = [0, 0, 1.0], angle = 9deg)
```
### scale
`scale(@objects: [Solid; 1+]|[Sketch; 1+]|[Helix; 1+]|ImportedGeometry, x?: number(_), y?: number(_), z?: number(_), global?: bool, factor?: number(_)): [Solid; 1+]|[Sketch; 1+]|[Helix; 1+]|ImportedGeometry`
The `x`, `y`, `z`, and `factor` arguments are dimensionless multipliers, not physical distances. Unlike `translate`, `scale` does not accept a length such as `10mm`.
- factor: If given, scale the solid by this dimensionless factor. Equivalent to setting `x`, `y` and `z` all to this number. Incompatible with `x`, `y` or `z`.
```kcl
// Scale an imported model.

import "tests/inputs/cube.sldprt" as cube

cube
  |> scale(y = 2.5)
```
### translate
`translate(@objects: [Solid; 1+]|[Sketch; 1+]|[Helix; 1+]|ImportedGeometry, x?: number(Length), y?: number(Length), z?: number(Length), global?: bool, xyz?: [number(Length); 3]): [Solid; 1+]|[Sketch; 1+]|[Helix; 1+]|ImportedGeometry`
By default, this does a local translation, around the sketch/body's coordinate system. To translate around the global scene coordinate system, use `global = true`.
Translate is really useful for sketches if you want to move a sketch and then rotate it using the `rotate` function to create a loft.
- xyz: If given, interpret this point as 3 distances, along each of [X, Y, Z] and translate by each of them.

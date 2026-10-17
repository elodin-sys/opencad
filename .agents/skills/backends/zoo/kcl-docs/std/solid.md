# std::solid
This module contains functions for modifying solids, e.g., by adding a fillet or chamfer, or removing part of a solid.
intersect, union: This operation consumes every input solid. After it succeeds, the original solid variables cannot be used in another modeling operation.

Common args:
- instances: [n3] [n4] [n5]
- legacyMethod: !dep, removed in KCL 3; do not set
- tolerance: [n2]
- useOriginal: [n8]
### appearance
`appearance(@solids: [Solid; 1+]|ImportedGeometry|Plane, color: string, metalness?: number(_), roughness?: number(_), opacity?: number(_)): [Solid; 1+]|ImportedGeometry|Plane`
For planes, only `color` is used.
- color: Color of the new material, a hex string like '#ff0000'.
- metalness: Metalness of the new material, a percentage like 95.7.
- roughness: Roughness of the new material, a percentage like 95.7.
- opacity: Defaults to 100 (totally opaque). 0 would be totally transparent.
```kcl
offsetPlane(XZ, offset = 4mm)
  |> appearance(color = "#ff0000", opacity = 50)
```
### blend
`blend(@edges: [BoundedEdge|TaggedEdge|any; 2]): Solid`
- edges: [face-api]
### chamfer
`chamfer(@solid: Solid, length: number(Length), tags?: [Edge; 1+], edges?: [any], secondLength?: number(Length), angle?: number(Angle), tag?: TagDecl, legacyMethod?: bool, version?: number(_)): Solid`
Chamfer is similar in function and use to a fillet, except a fillet will blend the transition along an edge, rather than cut a sharp, straight transitional edge.
- secondLength: If this argument isn't given, the lengths chamfered away from both the first and second face are both given by `length`. If this argument _is_ given, it determines how much is cut away from the second face. Incompatible with `angle`.
- angle: This argument determines the angle between the two cut edges. Requires `length`, incompatible with `secondLength`. The valid range is 0deg < angle < 90deg.
- version: !dep, removed in KCL 3; do not set
### deleteFace
`deleteFace(@body: Solid, faces?: [TaggedFace; 1+], faceIndices?: [number(_); 1+]): Solid`
- faces: This is the usual face representation, e.g. a tagged face.
### fillet
`fillet(@solid: Solid, radius: number(Length), tags?: [Edge; 1+], edges?: [any], tolerance?: number(Length), tag?: TagDecl, legacyMethod?: bool, version?: number(_)): Solid`
Fillet is similar in function and use to a chamfer, except a chamfer will cut a sharp transition along an edge while fillet will smoothly blend the transition.
- version: !dep, removed in KCL 3; do not set
### flipSurface
`flipSurface(@surface: [Solid; 1+]): [Solid; 1+]`
### hollow
`hollow(@solid: Solid, thickness: number(Length)): Solid`
Remove volume from a 3-dimensional shape such that a wall of the provided thickness remains around the exterior of the shape. By default, it'll look visually the same, but you can see the difference if you use `appearance` to make it transparent, or cut it open with a `subtract`.
### intersect
`intersect(@solids: [Solid; 2+], tolerance?: number(Length), legacyMethod?: bool): [Solid; 1+]`
### isSolid
`isSolid(@val: Solid): bool`
- val: Value to check if it is a solid or not
### isSurface
`isSurface(@val: Solid): bool`
- val: Value to check if it is a surface or not
### joinSurfaces
`joinSurfaces(@selection: [Solid; 1+], tolerance?: number(Length)): Solid`
### patternCircular3d
`patternCircular3d(@solids: [Solid; 1+]|ImportedGeometry, instances: number(_), axis: Axis3d|Point3d, center?: Point3d, arcDegrees?: number(deg), rotateDuplicates?: bool, useOriginal?: bool): [Solid|ImportedGeometry; 1+]`
- center: This is a 3D vector. If not given, defaults to `[0, 0, 0]`.
- arcDegrees: Must be greater than 0.
- rotateDuplicates: [n7]
### patternLinear3d
`patternLinear3d(@solids: [Solid; 1+]|ImportedGeometry, instances: number(_), distance: number(Length), axis: Axis3d|Point3d, useOriginal?: bool): [Solid|ImportedGeometry; 1+]`
- distance: Distance between each repetition.
### patternTransform
`patternTransform(@solids: [Solid; 1+]|ImportedGeometry, instances: number(_), transform: fn(number(_)): { }, useOriginal?: bool): [Solid|ImportedGeometry; 1+]`
Replicates the 3D solid or imported geometry, applying a transformation function to each replica.
The `patternTransform` call itself takes a number for how many total instances of the shape should be.
- transform: [n10] [n11]
### shell
`shell(@solids: [Solid; 1+], thickness: number(Length), faces: [TaggedFace; 1+]): [Solid]`
### split
`split(@targets: [Solid; 1+], merge?: bool, keepTools?: bool, tools?: [Solid], legacyMethod?: bool): [Solid; 1+]`
- keepTools: If false, the tool bodies will be removed from the scene. If true, they'll be kept. Defaults to false.
### subtract
`subtract(@solids: [Solid; 1+], tools: [Solid], tolerance?: number(Length), legacyMethod?: bool): [Solid]`
Performs a bool subtraction operation, removing the volume of one or more tool solids from one or more base solids. The result is a new solid representing the material that remains after all tool solids have been cut away.
This operation consumes both the base solids and the tool solids. For multiple cuts, pass each `subtract` result into the next call instead of reusing the original base solid.
### union
`union(@solids: [Solid; 2+], tolerance?: number(Length), legacyMethod?: bool): [Solid; 1+]`

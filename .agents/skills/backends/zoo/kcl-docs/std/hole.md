# std::hole
Definitions of standard holes that could be drilled or cut into solids.

Common args:
- holeBody: E.g. a blind distance.
- holeBottom: E.g. drilled or flat.
- holeType: E.g. countersink, counterbore, simple.
### blind
`hole::blind(depth: number(Length), diameter: number(Length))`
### counterbore
`hole::counterbore(diameter: number(Length), depth: number(Length))`
### countersink
`hole::countersink(diameter: number(Length), angle: number(Angle), headClearance?: number(Length))`
### drill
`hole::drill(pointAngle: number(Angle))`
### flat
`hole::flat()`
### hole
`hole::hole(@solid: Solid, face: TaggedFace, holeBottom, holeBody, holeType, cutAt: [number(Length); 2])`
- cutAt: Given as absolute coordinates in the global scene.
### holeAt
`hole::holeAt(@solids: [Solid; 1+], plane: Plane, holeBottom, holeBody, holeType)`
- plane: The plane's X and Y axis determine which way the hole is pointing (it points down the normal i.e. Z axis, following the right-hand rule).
### holes
`hole::holes(@solid: Solid, face: TaggedFace, holeBottom, holeBody, holeType, cutsAt: [[number(Length); 2]])`
- cutsAt: Where to place the holes, given as absolute coordinates in the global scene.
### holesLinear
`hole::holesLinear(@solid: Solid, face: TaggedFace, holeBottom, holeBody, holeType, cutAt: [number(Length); 2], instances: number(_), distance, axis: Axis2d|Point2d)`
- cutAt: Where to place the first cut in the linear pattern, given as absolute coordinates in the global scene.
- distance: How far between each hole
### simple
`hole::simple()`

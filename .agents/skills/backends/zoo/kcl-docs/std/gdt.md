# std::gdt
Functions for working with geometric dimensioning and tolerancing (GD&T).

`…common` = precision?: number(_), framePosition?: Point2d, framePlane?: Plane, leaderScale?: number(_), fontSize?: number(Length), annotationName?: string

Common args:
- annotationName: This is not displayed visually.
- edges: [face-api]
- fontSize: The default is `10mm`. Explicit units are supported; bare numbers use the file's default length unit. This changes the scene size, not the internal raster texture quality.
- framePlane: The default is `XY`. Other standard planes like `XZ` and `YZ` can also be used.
- framePosition: The position of the feature control frame relative to the leader arrow. The default is `[100mm, 100mm]`.
- leaderScale: The default is `1.0`, which maps to the calibrated normal dot size. The value is normalized against `fontSize` so the dot stays consistent as text size changes. Must be greater than `0`.
- precision: The default is `3`. Must be greater than or equal to `0` and less than or equal to `9`.
### angularity
`gdt::angularity(tolerance: number(Length), faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], datums?: [string; 1+], …common): [GdtAnnotation; 1+]`
The `tolerance` is a length controlling the size of the zone, not an angular plus-or-minus value. Provide at least one of `faces` or `edges`. Supplying both is allowed, but omitting both is an error.
- faces: At least one of `faces` or `edges` must be supplied.
- edges: At least one of `faces` or `edges` must be supplied. [face-api]
### annotation
`gdt::annotation(annotation: string, faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], framePosition?: Point2d, framePlane?: Plane, leaderScale?: number(_), fontSize?: number(Length), annotationName?: string): [GdtAnnotation; 1+]`
- framePosition: The position of the annotation relative to the leader arrow. The default is `[100mm, 100mm]`.
### circularity
`gdt::circularity(tolerance: number(Length), faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], …common): [GdtAnnotation; 1+]`
When applied to a circular edge, every point of the edge must lie between two concentric circles whose radii differ by the given `tolerance`. When applied to a round face, such as the wall of a cylinder or cone, every cross-section perpendicular to the axis must meet that same requirement.
Circularity is a form tolerance, so it does not reference datums.
```kcl
@settings(kclVersion = 2.0)

cylinderSketch = sketch(on = XY) {
  perimeter = circle(start = [var 5mm, var 0mm], center = [var 0mm, var 0mm])
}

cylinderRegion = region(segments = [cylinderSketch.perimeter])
hide(cylinderSketch)
cylinder = extrude(cylinderRegion, length = 10mm)
gdt::circularity(edges = [cylinderRegion.tags.perimeter], tolerance = 0.05mm, framePosition = [-12mm, 8mm])
```
### concentricity
`gdt::concentricity(tolerance: number(Length), datums: [string; 1+], faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], …common): [GdtAnnotation; 1+]`
The tolerance zone is cylindrical, with a diameter equal to `tolerance`. Datum references are required.
### cylindricity
`gdt::cylindricity(tolerance: number(Length), faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], …common): [GdtAnnotation; 1+]`
It controls how much a cylindrical surface may deviate from a perfect cylinder, combining roundness, straightness, and taper into a single requirement. Every point on the surface must lie between two coaxial cylinders whose radii differ by the given `tolerance`.
Cylindricity is a form tolerance, so it does not reference datums.
### datum
`gdt::datum(face: TaggedFace, name: string, framePosition?: Point2d, framePlane?: Plane, leaderScale?: number(_), fontSize?: number(Length), annotationName?: string): GdtAnnotation`
### distance
`gdt::distance(tolerance?: number(Length), from?: Face|TaggedFace|Edge|any, to?: Face|TaggedFace|Edge|any, edges?: [Edge|any; 1+], …common): [GdtAnnotation; 1+]`
- tolerance: If not given, or 0, tolerance will not be shown.
- from: Must be used with `to`. The default position is the entity center. [face-api]
- to: Must be used with `from`. The default position is the entity center.
- edges: Cannot be combined with `from` or `to`. [face-api]
- framePosition: The position of the distance label relative to the measured geometry. The default is `[100mm, 100mm]`.
- leaderScale: The default is `1.0`. Must be greater than `0`.
### flatness
`gdt::flatness(faces: [TaggedFace; 1+], tolerance: number(Length), …common): [GdtAnnotation; 1+]`
### note
`gdt::note(note: string, framePlane?: Plane, framePosition?: Point2d, fontSize?: number(Length), annotationName?: string): GdtAnnotation`
Unlike `gdt::annotation`, a note has no leader and is placed directly on a plane. By default it lives on the world `XY` plane, but any plane (a standard plane like `XZ`/`YZ`, or a user-defined plane) can be supplied via `framePlane`.
- framePlane: The default is `XY`. Other standard planes like `XZ` and `YZ`, or a user-defined plane, can also be used.
- framePosition: The 2D position of the note within the plane, in the plane's local coordinates. The default is `[100mm, 100mm]`.
### parallelism
`gdt::parallelism(tolerance: number(Length), faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], datums?: [string; 1+], …common): [GdtAnnotation; 1+]`
### perpendicularity
`gdt::perpendicularity(tolerance: number(Length), faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], datums?: [string; 1+], …common): [GdtAnnotation; 1+]`
### position
`gdt::position(tolerance: number(Length), faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], datums?: [string; 1+], …common): [GdtAnnotation; 1+]`
### profile
`gdt::profile(tolerance: number(Length), edges?: [Edge|any; 1+], faces?: [TaggedFace; 1+], datums?: [string; 1+], …common): [GdtAnnotation; 1+]`
`gdt::profile` is kept for backwards compatibility with existing KCL programs. For new code, prefer `gdt::profileLine` when annotating edges and `gdt::profileSurface` when annotating faces.
Provide exactly one of `edges` or `faces`. Passing `edges` delegates to `profileLine`; passing `faces` delegates to `profileSurface`. Passing both, or neither, is a KCL error.
- edges: Provide either `edges` or `faces`, but not both. [face-api]
- faces: Provide either `edges` or `faces`, but not both.
### profileLine
`gdt::profileLine(edges: [Edge|any; 1+], tolerance: number(Length), datums?: [string; 1+], …common): [GdtAnnotation; 1+]`
### profileSurface
`gdt::profileSurface(faces: [TaggedFace; 1+], tolerance: number(Length), datums?: [string; 1+], …common): [GdtAnnotation; 1+]`
### runout
`gdt::runout(tolerance: number(Length), datums: [string; 1+], faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], …common): [GdtAnnotation; 1+]`
Datum references are required.
Runout is applied regardless of feature size and does not use MMC or LMC.
- tolerance: The circular runout relative to the datum axis that is acceptable.
### straightness
`gdt::straightness(tolerance: number(Length), faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], …common): [GdtAnnotation; 1+]`
When applied to a planar face, every line element of the face must lie between two parallel lines separated by the given `tolerance`. When applied to an edge, the edge itself must lie within that zone.
### symmetry
`gdt::symmetry(tolerance: number(Length), datums: [string; 1+], faces?: [TaggedFace; 1+], edges?: [Edge|any; 1+], …common): [GdtAnnotation; 1+]`
The tolerance zone is bounded by two parallel planes equally disposed about the datum plane, with a total width equal to `tolerance`. Datum references are required.
- tolerance: The total width of the tolerance zone between two parallel planes.

# KCL std index

One line per item: `name: gist`. Typed signatures, arg notes, examples: `std/<module>.md`.
Full page: `zoo.dev/docs/kcl-std/functions/std-<module>-<name>` (root module: `std-<name>`).
`solver::*` is in scope unprefixed inside `sketch(on = …) { }`; other prefixed modules are called as written (`module::name`).
Flags: `!dep` deprecated sketch-v1 API (recognise, never write); `!v1soft` sketch-v1 form, solver version pending; `!exp` experimental, needs `@settings(experimentalFeatures = allow)`.
[face-api] Edge-specifier objects `{ sideFaces, endFaces?, index? }` are experimental; use tags, edgeId(...), or the listed geometry types instead.

Shared arg notes (referenced as [nN] in module pages):
- [n1] Defines the smallest distance below which two entities are considered coincident, intersecting, coplanar, or similar.
- [n2] For most use cases, it should not be changed from its default value of 10^-7 millimeters.
- [n3] Must be greater than or equal to 1.
- [n4] For example, if instances is 2, there will be two copies -- the original, and one new copy.
- [n5] If instances is 1, this has no effect.
- [n6] The center about which to make the pattern.
- [n7] Whether or not to rotate the duplicates as they are copied.
- [n8] If the target was sketched on an extrusion, setting this will use the original sketch as the target, not the entire joined solid.
- [n9] The transform function takes a single parameter: an integer representing which number replication the transform is for.
- [n10] E.g. the first replica to be transformed will be passed the argument `1`.
- [n11] This simplifies your math: the transform function can rely on id `0` being the original instance passed into the `patternTransform`.
- [n12] KCL 3.0 and later always use the newest algorithm.

## std
- consts: `CCW`, `CW`, `END`, `MERGE`, `NEW`, `SOLID`, `START`, `SURFACE`, `X`, `XY`, `XZ`, `Y`, `YZ`, `Z`
- `assert`: Check a value meets some expected conditions at runtime
- `assertIs`: Asserts that a value is the boolean value true
- `clone`: Clone a sketch or solid
- `edgeId`: Given an edge index, find its ID
- `faceId`: Given a face index, find its ID
- `fail` !exp: Stop KCL evaluation with a user-defined error
- `helix`: Create a helix
- `offsetPlane`: Offset a plane by a distance along its normal

## sketch
- `conic` !exp !v1soft: Add a conic section to an existing sketch
- `ellipse` !exp !v1soft: Construct a 2-dimensional ellipse, of the specified major/minor radius…
- `elliptic` !exp !v1soft: Add an elliptic section to an existing sketch
- `ellipticPoint`: Calculate the point (x, y) on an ellipse given x…
- `extrude`: Extend a 2-dimensional sketch or individual segment of a sketch…
- `faceOf`: Get the face of a solid
- `getBoundedEdge`: Get a bounded edge of a surface used for the…
- `getCommonEdge`: Get the shared edge between two faces
- `getNextAdjacentEdge`: Get the next adjacent edge to the edge given
- `getOppositeEdge`: Get the opposite edge to the edge given
- `getPreviousAdjacentEdge`: Get the previous adjacent edge to the edge given
- `hyperbolic` !exp !v1soft: Add a hyperbolic section to an existing sketch
- `hyperbolicPoint`: Calculate the point (x, y) on a hyperbola given x…
- `lastSegX`: Extract the 'x' axis value of the last line segment…
- `lastSegY`: Extract the 'y' axis value of the last line segment…
- `loft`: Create a 3D surface or solid by interpolating between two…
- `parabolic` !exp !v1soft: Add a parabolic segment to an existing sketch
- `parabolicPoint`: Calculate the point (x, y) on a parabola given x…
- `patternCircular2d`: Repeat a 2-dimensional sketch some number of times along a…
- `patternLinear2d`: Repeat a 2-dimensional sketch along some dimension…
- `patternTransform2d`: Just like `patternTransform`, but works on 2D sketches not 3D…
- `planeOf`: Find the plane a face lies on
- `profileStart`: Extract the provided 2-dimensional sketch's profile origin as an array…
- `profileStartX`: Extract the provided 2-dimensional sketch's profile's origin's 'x' value
- `profileStartY`: Extract the provided 2-dimensional sketch's profile's origin's 'y' value
- `region`: Create a region from closed segments
- `revolve`: Rotate a sketch around some provided axis…
- `segAng`: Compute the angle (in degrees) of the provided line segment
- `segEnd`: Compute the ending point of the provided line segment
- `segEndX`: Compute the ending point of the provided line segment along…
- `segEndY`: Compute the ending point of the provided line segment along…
- `segLen`: Compute the length of the provided line segment
- `segStart`: Compute the starting point of the provided line segment
- `segStartX`: Compute the starting point of the provided line segment along…
- `segStartY`: Compute the starting point of the provided line segment along…
- `sweep`: Create a 3D surface or solid by sweeping a sketch…
- `tangentToEnd`: Returns the angle coming out of the end of the…
- !dep: `angledLine`, `angledLineThatIntersects`, `arc`, `bezierCurve`, `circle`, `circleThreePoint`, `close`, `involuteCircular`, `line`, `polygon`, `rectangle`, `startProfile`, `startSketchOn`, `subtract2d`, `tangentialArc`, `xLine`, `yLine`

## solver
- consts: `solver::ORIGIN`
- `solver::angleDimension`: Constrain the angle in the selected sector between two lines
- `solver::arc`: Create a circular arc
- `solver::circle`: Create a circle in a sketch
- `solver::coincident`: Constrain points, or a point…
- `solver::controlPointSpline` !exp: Create a control-point spline in a sketch
- `solver::diameter`: Constrain the diameter of an arc or circle segment
- `solver::distance`: Constrain the distance between two sketch entities
- `solver::equalLength`: Constrain lines to have equal length
- `solver::equalRadius`: Constrain circular segments to have equal radius
- `solver::fixed`: Constrain a point to be fixed to a position
- `solver::horizontal`: Constrain a line, or a list of points…
- `solver::horizontalDistance`: Constrain the horizontal distance between two points
- `solver::line`: Create a straight line segment in a sketch
- `solver::midpoint`: Constrain a point to lie at the midpoint of a…
- `solver::parallel`: Constrain lines to be parallel
- `solver::perpendicular`: Constrain lines to be perpendicular
- `solver::point`: Create a point in a sketch
- `solver::radius`: Constrain the radius of an arc or circle segment
- `solver::symmetric`: Constrain two points, lines, arcs…
- `solver::tangent`: Constrain two segments to be tangent
- `solver::vertical`: Constrain a line, or a list of points…
- `solver::verticalDistance`: Constrain the vertical distance between two points
- !dep: `solver::angle`

## solid
- `appearance`: Set the appearance of a solid, imported geometry, or plane
- `blend`: Blend two surfaces together
- `chamfer`: Cut a straight transitional edge along a tagged path
- `deleteFace`: Delete a face from a body (a solid…
- `fillet`: Blend a transitional edge along a tagged path…
- `flipSurface`: Flips the orientation of a surface…
- `hollow`: Make the inside of a 3D object hollow
- `intersect`: Intersect returns the shared volume between multiple solids…
- `isSolid`: Given a KCL value that is a \"body\" (currently typed…
- `isSurface`: Given a KCL value that is a 'body' (currently typed…
- `joinSurfaces`: Join multiple surfaces together into one body…
- `patternCircular3d`: Repeat a 3-dimensional body or imported geometry some number of…
- `patternLinear3d`: Repeat a 3-dimensional body or imported geometry along a linear…
- `patternTransform`: Repeat a 3-dimensional body or imported geometry…
- `shell`: Remove volume from a 3-dimensional shape such that a wall…
- `split`: Split all faces of the target body along all faces…
- `subtract`: Subtract removes tool solids from base solids…
- `union`: Union two or more solids into a single solid

## sweep
- consts: `sweep::SKETCH_PLANE`, `sweep::TRAJECTORY`

## hole
- `hole::blind`: The hole has the given blind depth
- `hole::counterbore`: Cut a straight vertical counterbore at the top of the…
- `hole::countersink`: Cut an angled countersink at the top of the hole
- `hole::drill`: End the hole in an angle…
- `hole::flat`: End the hole flat
- `hole::hole`: From the hole's parts (bottom, middle, top)…
- `hole::holeAt`: From the hole's parts (bottom, middle, top)…
- `hole::holes`: From the hole's parts (bottom, middle, top)…
- `hole::holesLinear`: Place the given holes in a line
- `hole::simple`: A hole top with no decoration

## transform
- `delete` !exp: Deletes something from the scene
- `hide`: Hide solids, planes, sketches, helices, or imported objects
- `mirror2d`: Mirror a sketch
- `mirror3d`: Create a mirror image of a 3D solid/surface/body…
- `rotate`: Rotate a solid, a sketch, or a helix
- `scale`: Scale a solid, a sketch, or a helix
- `translate`: Move a solid, a sketch, or a helix

## array
- `concat`: Combine two arrays into one by concatenating them
- `count`: Find the number of elements in an array
- `flatten`: Flatten an array by one level
- `map`: Apply a function to every element of a list
- `pop`: Remove the last element from an array
- `push`: Append an element to the end of an array
- `reduce`: Take a starting value
- `slice`: Get a subarray from `start` (inclusive) to `end` (exclusive)

## math
- consts: `E`, `PI`, `TAU`
- `abs`: Compute the absolute value of a number
- `acos`: Compute the arccosine of a number
- `asin`: Compute the arcsine of a number
- `atan`: Compute the arctangent of a number
- `atan2`: Compute the four quadrant arctangent of Y and X
- `ceil`: Compute the smallest integer greater than…
- `cos`: Compute the cosine of a number
- `floor`: Compute the largest integer less than…
- `legAngX`: Compute the angle of the given leg for x
- `legAngY`: Compute the angle of the given leg for y
- `legLen`: Compute the length of the given leg
- `ln`: Compute the natural logarithm of the number
- `log`: Compute the logarithm of the number with respect to an…
- `log10`: Compute the base 10 logarithm of the number
- `log2`: Compute the base 2 logarithm of the number
- `max`: Compute the maximum of the given arguments
- `min`: Compute the minimum of the given arguments
- `polar`: Convert polar (angle, distance) coordinates to cartesian (x/y grid) coordinates
- `pow`: Compute the number to a power
- `rem`: Compute the remainder after dividing `num` by `div`
- `round`: Round a number to the nearest integer
- `sin`: Compute the sine of a number
- `sqrt`: Compute the square root of a number
- `tan`: Compute the tangent of a number

## units
- `units::toCentimeters`: Convert a number to centimeters from its current units
- `units::toDegrees`: Converts a number to degrees from its current units
- `units::toFeet`: Convert a number to feet from its current units
- `units::toInches`: Convert a number to inches from its current units
- `units::toMeters`: Convert a number to meters from its current units
- `units::toMillimeters`: Convert a number to millimeters from its current units
- `units::toRadians`: Converts a number to radians from its current units
- `units::toYards`: Converts a number to yards from its current units

## vector
- `vector::add`: Adds every element of u to its corresponding element in…
- `vector::cross`: Find the cross product of two 3D points or vectors
- `vector::div`: Divides every element of u by its corresponding element in…
- `vector::dot`: Find the dot product of two points…
- `vector::magnitude`: Find the Euclidean distance of a vector
- `vector::mul`: Multiplies every element of u by its corresponding element in…
- `vector::normalize`: Normalize a vector (with any number of dimensions)
- `vector::sub`: Subtracts from every element of u its corresponding element in…

## string
- `string::isEqual`: Compare two strings for equality
- `string::lowercase`: Convert all cased characters in a string to lowercase
- `string::toString`: Convert a number to human-readable text
- `string::trim`: Remove whitespace from the start and end of a string
- `string::trimEnd`: Remove whitespace from the end of a string
- `string::trimStart`: Remove whitespace from the start of a string
- `string::uppercase`: Convert all cased characters in a string to uppercase

## gdt
- `gdt::angularity`: GD&T angularity annotation specifying how much faces…
- `gdt::annotation`: GD&T annotation for attaching manufacturing text to faces or edges
- `gdt::circularity`: GD&T annotation specifying how circular (round) a feature must be
- `gdt::concentricity`: GD&T concentricity annotation specifying how closely a feature's median axis…
- `gdt::cylindricity`: GD&T annotation specifying how closely a feature must conform to…
- `gdt::datum`: GD&T datum feature
- `gdt::distance`: GD&T distance annotation for displaying measured edge lengths…
- `gdt::flatness`: GD&T annotation specifying how flat faces should be
- `gdt::note`: GD&T note for adding free-floating manufacturing text that is not…
- `gdt::parallelism`: GD&T parallelism annotation specifying how much faces…
- `gdt::perpendicularity`: GD&T perpendicularity annotation specifying how much faces…
- `gdt::position`: GD&T position annotation specifying how much faces…
- `gdt::profile`: GD&T profile annotation specifying how much edges…
- `gdt::profileLine`: GD&T profile-of-a-line annotation specifying how much edges may deviate from…
- `gdt::profileSurface`: GD&T profile-of-a-surface annotation specifying how much faces may deviate from…
- `gdt::runout`: GD&T annotation specifying circular runout relative to a datum axis
- `gdt::straightness`: GD&T annotation specifying how straight a feature must be
- `gdt::symmetry`: GD&T symmetry annotation specifying how closely a feature's median plane…

## gear
- `gear::helical` !exp: A helical gear (like a spur gear…
- `gear::herringbone` !exp: A herringbone gear (like a helical gear that reverses direction…
- `gear::ring` !exp: A ring gear (i.e. a gear with internal teeth)
- `gear::spur` !exp: A spur gear (like a helical gear…

## appearance
- `appearance::hexString`: Build a color from its red, green and blue components

## view
- `view::directed` !exp: Create a camera view that looks along a custom direction
- `view::named` !exp: Create a named view: a camera paired with the objects…
- `view::oriented` !exp: Create a camera view that looks at the model from…

## operation
- `operation::facing` !exp: 

## runtime
- `exit` !exp: Exit the program early

## turns
- consts: `turns::HALF_TURN`, `turns::QUARTER_TURN`, `turns::THREE_QUARTER_TURN`, `turns::ZERO`

## types: see `std/types.md`

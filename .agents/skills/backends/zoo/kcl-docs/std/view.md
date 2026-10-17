# std::view
Named views: cameras and visibility sets defined in KCL.
directed, oriented: The returned value stores intent, not resolved numbers: an argument you omit stays absent, and the consumer that activates the view resolves it against the model it is showing, so one view value is valid for any model.
### directed !exp
`view::directed(@direction: Point3d, up?: Point3d, target?: Point3d, distance?: number(Length), projection?: Projection): CameraView`
`direction` and `up` set only directions: both are normalized when the view is constructed, so their magnitudes carry no information and zoom comes from `distance`. Each must be a non-zero vector, and they must not be parallel or nearly parallel to each other; such arguments are errors. When that happens, choose an `up` that does not lie along `direction`.
- up: When omitted, `[0, 0, 1]`: the positive Z axis, which is the modeling app's world up.
- target: When omitted, the view centers on the bounds of the model at activation.
- distance: Must be greater than zero. When omitted, the view fits the model at activation.
- projection: When omitted, the view is orthographic, so the same file renders identically in every consumer.
```kcl
@settings(experimentalFeatures = allow)

overheadView = view::directed([0, 1, -2])

closeUp = view::directed(
  [-1, -1, -0.3],
  up = [0, 0, 1],
  target = [0, 0, 10],
  distance = 200,
  projection = view::Projection::Perspective,
)
```
### named !exp
`view::named(@name: string, camera: CameraView, baseline: Visibility, except?: [Solid|Sketch|GdtAnnotation; 1+]): NamedView`
A view is data, not an action. Creating one moves no camera and changes nothing about what is visible; a consumer such as the modeling app or a STEP export activates it later, which is why the same file yields the same views on every machine.
Duplicates in `except` are dropped, so listing an object twice does the same as listing it once.
- name: Required, unique within the file, and compared exactly.
- camera: Call `view::oriented()` or `view::directed()` to build one.
- baseline: The default visibility of every object the program creates: visible under `Visibility::Show`, hidden under `Visibility::Hide`. Use `except` below to override that default for individual objects.
- except: The objects the baseline does not apply to: the hidden ones under a `Show` baseline, and the only visible ones under `Hide`.
### oriented !exp
`view::oriented(@orientation: Orientation, target?: Point3d, distance?: number(Length), projection?: Projection): CameraView`
Every argument you do pass must be a finite number; an infinite or undefined value, such as one produced by dividing by zero, is an error rather than a stored value no consumer could use.
- distance: Must be greater than zero.
```kcl
@settings(experimentalFeatures = allow)

isoView = view::oriented(view::Orientation::Isometric)

frontView = view::oriented(
  view::Orientation::Front,
  target = [0, 0, 0],
  distance = 500,
  projection = view::Projection::Perspective,
)
```

Source URL: https://zoo.dev/docs/kcl-std/functions/std-math-atan2
Title: atan2

# atan2

Compute the four quadrant arctangent of Y and X.

Compute the four quadrant arctangent of Y and X.

```kcl
atan2(
  y: number(Length),
  x: number(Length),
): number(rad)
```



### Arguments

| Name | Type | Description | Required |
|----------|------|-------------|----------|
| `y` | [`number(Length)`](/docs/kcl-std/types/std-types-number) | A number. | Yes |
| `x` | [`number(Length)`](/docs/kcl-std/types/std-types-number) | A number. | Yes |

### Returns

[`number(rad)`](/docs/kcl-std/types/std-types-number) - A number.


### Examples

```kcl
sketch001 = startSketchOn(XZ)
  |> startProfile(at = [0, 0])
  |> angledLine(angle = atan2(y = 1.25, x = 2), length = 20)
  |> yLine(endAbsolute = 0)
  |> close()

extrude001 = extrude(sketch001, length = 5)

```


<model-viewer
  class="kcl-example"
  alt="Example showing a rendered KCL program that uses the atan2 function"
  src="/kcl-test-outputs/models/serial_test_example_fn_std-math-atan20_output.gltf"
  ar
  environment-image="/moon_1k.hdr"
  poster="/kcl-test-outputs/serial_test_example_fn_std-math-atan20.png"
  shadow-intensity="1"
  camera-controls
  touch-action="pan-y"
>
</model-viewer>

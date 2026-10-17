Source URL: https://zoo.dev/docs/kcl-std/functions/std-math-log10
Title: log10

# log10

Compute the base 10 logarithm of the number.

Compute the base 10 logarithm of the number.

```kcl
log10(@input: number): number
```



### Arguments

| Name | Type | Description | Required |
|----------|------|-------------|----------|
| `input` | [`number`](/docs/kcl-std/types/std-types-number) | A number. | Yes |

### Returns

[`number`](/docs/kcl-std/types/std-types-number) - A number.


### Examples

```kcl
exampleSketch = startSketchOn(XZ)
  |> startProfile(at = [0, 0])
  |> line(end = [log10(100), 0])
  |> line(end = [5, 8])
  |> line(end = [-10, 0])
  |> close()

example = extrude(exampleSketch, length = 5)

```


<model-viewer
  class="kcl-example"
  alt="Example showing a rendered KCL program that uses the log10 function"
  src="/kcl-test-outputs/models/serial_test_example_fn_std-math-log100_output.gltf"
  ar
  environment-image="/moon_1k.hdr"
  poster="/kcl-test-outputs/serial_test_example_fn_std-math-log100.png"
  shadow-intensity="1"
  camera-controls
  touch-action="pan-y"
>
</model-viewer>

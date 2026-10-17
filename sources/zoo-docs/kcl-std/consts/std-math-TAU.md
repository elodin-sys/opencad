Source URL: https://zoo.dev/docs/kcl-std/consts/std-math-TAU
Title: TAU

# TAU

The value of `tau`, the full circle constant (τ). Equal to 2π.

The value of `tau`, the full circle constant (τ). Equal to 2π.

```kcl
TAU: number = 6.28318530717958647692528676655900577_
```



### Type

[`number`](/docs/kcl-std/types/std-types-number) - A number.

### Examples

```kcl
exampleSketch = startSketchOn(XZ)
  |> startProfile(at = [0, 0])
  |> angledLine(angle = 50deg, length = 10 * TAU)
  |> yLine(endAbsolute = 0)
  |> close()

example = extrude(exampleSketch, length = 5)

```

![Rendered example of TAU 0](/kcl-test-outputs/serial_test_example_const_std-math-TAU0.png)

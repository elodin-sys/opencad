Source URL: https://zoo.dev/docs/kcl-std/functions/std-math-atan
Title: atan

# atan

Compute the arctangent of a number.

Compute the arctangent of a number.

```kcl
atan(@num: number(_)): number(rad)
```

Consider using `atan2()` instead for the true inverse of tangent.

### Arguments

| Name | Type | Description | Required |
|----------|------|-------------|----------|
| `num` | [`number(_)`](/docs/kcl-std/types/std-types-number) | A number. | Yes |

### Returns

[`number(rad)`](/docs/kcl-std/types/std-types-number) - A number.


### Examples

```kcl
sketch001 = startSketchOn(XZ)
  |> startProfile(at = [0, 0])
  |> angledLine(angle = atan(1.25), length = 20)
  |> yLine(endAbsolute = 0)
  |> close()

extrude001 = extrude(sketch001, length = 5)

```

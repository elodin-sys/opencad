Source URL: https://zoo.dev/docs/kcl-std/functions/std-fail
Title: fail

# fail

Stop KCL evaluation with a user-defined error.

**WARNING:** This function is experimental and may change or be removed.

Stop KCL evaluation with a user-defined error.

```kcl
fail(@msg: string): never
```

Use `fail` when evaluation cannot continue and the caller should receive a
specific error message. `fail` never returns a value.

### Arguments

| Name | Type | Description | Required |
|----------|------|-------------|----------|
| `msg` | [`string`](/docs/kcl-std/types/std-types-string) | Message reported to the caller. | Yes |

### Returns

[`never`](/docs/kcl-std/types/std-types-never) - The uninhabited type of computations that never complete normally.


### Examples

```kcl
fn positive(@value: number): number {
  return if value > 0 {
    value
  } else {
    fail("value must be positive")
  }
}

```

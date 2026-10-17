Source URL: https://zoo.dev/docs/kcl-std/functions/std-string-uppercase
Title: string::uppercase

# string::uppercase

Convert all cased characters in a string to uppercase.

Convert all cased characters in a string to uppercase.

```kcl
string::uppercase(@text: string): string
```

This conversion is Unicode-aware and locale-independent. Some characters
expand into multiple characters; for example, `ß` becomes `SS`. The exact
mappings follow the Unicode data bundled with KCL.

Unicode normalization is not performed. Canonically equivalent strings
therefore retain their original representations. Empty strings and strings
without cased characters are returned unchanged.

### Arguments

| Name | Type | Description | Required |
|----------|------|-------------|----------|
| `text` | [`string`](/docs/kcl-std/types/std-types-string) | The string to convert. | Yes |

### Returns

[`string`](/docs/kcl-std/types/std-types-string) - A sequence of characters


### Examples

```kcl
result = "Straße"
  |> string::uppercase()

assertIs(result == "STRASSE")

```

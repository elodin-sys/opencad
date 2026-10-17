# std::string
Operations on KCL strings.
lowercase, uppercase: Unicode normalization is not performed. Empty strings and strings without cased characters are returned unchanged.
trim, trimEnd, trimStart: If the input is empty or contains only whitespace, this returns an empty string. Unicode normalization and case conversion are not performed.
### isEqual
`string::isEqual(@text: string, to: string, caseInsensitive?: bool): bool`
By default, this performs an exact, case-sensitive comparison equivalent to the `==` operator. Set `caseInsensitive` to `true` to compare using locale-independent full Unicode case folding.
Unicode normalization is not performed.
- to: The string to compare `text` with.
```kcl
matches = "Straße"
  |> string::isEqual(to = "STRASSE", caseInsensitive = true)

assertIs(matches)
```
### lowercase
`string::lowercase(@text: string): string`
```kcl
result = "KCL ΟΣ"
  |> string::lowercase()

assertIs(result == "kcl ος")
```
### toString
`string::toString(@num: number): string`
Defined for every `number` value, including the non-finite ones.
The output is meant to be read, not parsed. Some results are not valid KCL source and reading one back is not supported.
```kcl
lengthText = 12mm
  |> string::toString()

assertIs(lengthText == "12mm")

countText = string::toString(3_)

assertIs(countText == "3_")
```
### trim
`string::trim(@text: string): string`
Whitespace is defined by Unicode's `White_Space` property and includes spaces, tabs, newlines, and non-breaking spaces.
```kcl
result = "  KCL strings  "
  |> string::trim()

assertIs(result == "KCL strings")
```
### trimEnd
`string::trimEnd(@text: string): string`
```kcl
result = "  KCL strings  "
  |> string::trimEnd()

assertIs(result == "  KCL strings")
```
### trimStart
`string::trimStart(@text: string): string`
```kcl
result = "  KCL strings  "
  |> string::trimStart()

assertIs(result == "KCL strings  ")
```
### uppercase
`string::uppercase(@text: string): string`
```kcl
result = "Straße"
  |> string::uppercase()

assertIs(result == "STRASSE")
```

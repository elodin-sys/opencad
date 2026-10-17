Source URL: https://zoo.dev/docs/kcl-std/functions/std-vector-magnitude
Title: vector::magnitude

# vector::magnitude

Find the Euclidean distance of a vector.

Find the Euclidean distance of a vector.

```kcl
vector::magnitude(@v: [number]): number
```



### Arguments

| Name | Type | Description | Required |
|----------|------|-------------|----------|
| `v` | [[`number`](/docs/kcl-std/types/std-types-number)] |  | Yes |

### Returns

[`number`](/docs/kcl-std/types/std-types-number) - A number.


### Examples

```kcl
v = [3, 4]
m = vector::magnitude(v)
assert(m, isEqualTo = 5)

```

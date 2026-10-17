Source URL: https://zoo.dev/docs/kcl-std/functions/std-vector-normalize
Title: vector::normalize

# vector::normalize

Normalize a vector (with any number of dimensions)

Normalize a vector (with any number of dimensions)

```kcl
vector::normalize(@v: [number]): [number]
```



### Arguments

| Name | Type | Description | Required |
|----------|------|-------------|----------|
| `v` | [[`number`](/docs/kcl-std/types/std-types-number)] |  | Yes |

### Returns

[[`number`](/docs/kcl-std/types/std-types-number)]


### Examples

```kcl
v = [3, 4]
normed = vector::normalize(v)
assert(normed[0], isEqualTo = 0.6)
assert(normed[1], isEqualTo = 0.8)

```

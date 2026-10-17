Source URL: https://zoo.dev/docs/kcl-std/functions/std-vector-dot
Title: vector::dot

# vector::dot

Find the dot product of two points or vectors of any dimension.

Find the dot product of two points or vectors of any dimension.

```kcl
vector::dot(
  @u: [number],
  v: [number],
): number
```



### Arguments

| Name | Type | Description | Required |
|----------|------|-------------|----------|
| `u` | [[`number`](/docs/kcl-std/types/std-types-number)] |  | Yes |
| `v` | [[`number`](/docs/kcl-std/types/std-types-number)] |  | Yes |

### Returns

[`number`](/docs/kcl-std/types/std-types-number) - A number.


### Examples

```kcl
u = [1, 2, 3]
v = [4, -5, 6]
dotprod = vector::dot(u, v)
assert(dotprod, isEqualTo = 12)

```

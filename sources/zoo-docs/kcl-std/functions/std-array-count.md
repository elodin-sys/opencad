Source URL: https://zoo.dev/docs/kcl-std/functions/std-array-count
Title: count

# count

Find the number of elements in an array.

Find the number of elements in an array.

```kcl
count(@array: [any]): number
```



### Arguments

| Name | Type | Description | Required |
|----------|------|-------------|----------|
| `array` | [[`any`](/docs/kcl-std/types/std-types-any)] | The array whose length will be returned. | Yes |

### Returns

[`number`](/docs/kcl-std/types/std-types-number) - A number.


### Examples

```kcl
arr1 = [10, 20, 30]
assert(count(arr1), isEqualTo = 3)

```

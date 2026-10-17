# std::array
Functions for manipulating arrays of values.
### concat
`concat(@array: [any], items: [any]): [any]`
```kcl
// Concatenating an empty array has no effect.
newArr = concat([10, 20, 30], items = [])
assert(newArr[0], isEqualTo = 10, tolerance = 0.00001)
assert(newArr[1], isEqualTo = 20, tolerance = 0.00001)
assert(newArr[2], isEqualTo = 30, tolerance = 0.00001)
assert(count(newArr), isEqualTo = 3, tolerance = 0.00001)
```
### count
`count(@array: [any]): number`
```kcl
arr1 = [10, 20, 30]
assert(count(arr1), isEqualTo = 3)
```
### flatten
`flatten(@array: [any]): [any]`
Returns a new array where any nested arrays are expanded into the top-level array. This only flattens one level deep.
```kcl
arr = [1, [2, 3], 4]
flat = flatten(arr)
assert(flat[0], isEqualTo = 1)
assert(flat[1], isEqualTo = 2)
assert(flat[2], isEqualTo = 3)
assert(flat[3], isEqualTo = 4)
```
### map
`map(@array: [any], f: fn(any): any): [any]`
Given a list like `[a, b, c]`, and a function like `f`, returns `[f(a), f(b), f(c)]`
- array: The output array is this input array, but every element has had the function `f` run on it.
- f: The output array is just the input array, but `f` has been run on every item.
### pop
`pop(@array: [any; 1+]): [any]`
- array: Must not be empty.
### push
`push(@array: [any], item: any): [any; 1+]`
```kcl
arr = [1, 2, 3]
new_arr = push(arr, item = 4)
assert(
  new_arr[3],
  isEqualTo = 4,
  tolerance = 0.1,
  error = "4 was added to the end of the array",
)
```
### reduce
`reduce(@array: [any], initial: any, f: fn(any, accum: any): any): any`
- array: Each element of this array gets run through the function `f`, combined with the previous output from `f`, and then used for the next run.
- initial: The first time `f` is run, it will be called with the first item of `array` and this initial starting value.
- f: Run once per item in the input `array`. This function takes an item from the array, and the previous output from `f` (or `initial` on the very first run). The final time `f` is run, its output is returned as the final output from `reduce`.
### slice
`slice(@array: [any], start?: number(_), end?: number(_)): [any]`
Negative indexes count from the end of the array, so `-1` is the last element, `-2` is the second-to-last element, and so on.
If `start` is omitted, it defaults to `0`. If `end` is omitted, it defaults to the length of the array.
- start: The starting index (inclusive). Defaults to `0`.
- end: The ending index (exclusive). Defaults to the array length.
```kcl
s = slice([1, 2, 3, 4, 5], start = -2)
assert(s[0], isEqualTo = 4)
assert(s[1], isEqualTo = 5)
assert(count(s), isEqualTo = 2)
```

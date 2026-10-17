# std::vector
## Functions and constants
### add
`vector::add(@u: [number], v: [number]): [number]`
```kcl
u = [1, 2, 3]
v = [10, 10, 10]
v2 = vector::add(u, v)
assert(v2[0], isEqualTo = 11)
assert(v2[1], isEqualTo = 12)
assert(v2[2], isEqualTo = 13)
```
### cross
`vector::cross(@u: Point3d, v: Point3d)`
```kcl
vx = [1, 0, 0]
vy = [0, 1, 0]
vz = vector::cross(vx, v = vy)
assert(vz[0], isEqualTo = 0)
assert(vz[1], isEqualTo = 0)
assert(vz[2], isEqualTo = 1)
```
### div
`vector::div(@u: [number], v: [number]): [number]`
```kcl
u = [10, 10, 10]
v = [1, 2, 3]
v2 = vector::div(u, v)
assert(v2[0], isEqualTo = 10)
assert(v2[1], isEqualTo = 5)
assert(v2[2], isEqualTo = 3.333, tolerance = 0.01)
```
### dot
`vector::dot(@u: [number], v: [number]): number`
```kcl
u = [1, 2, 3]
v = [4, -5, 6]
dotprod = vector::dot(u, v)
assert(dotprod, isEqualTo = 12)
```
### magnitude
`vector::magnitude(@v: [number]): number`
```kcl
v = [3, 4]
m = vector::magnitude(v)
assert(m, isEqualTo = 5)
```
### mul
`vector::mul(@u: [number], v: [number]): [number]`
```kcl
u = [10, 10, 10]
v = [1, 2, 3]
v2 = vector::mul(u, v)
assert(v2[0], isEqualTo = 10)
assert(v2[1], isEqualTo = 20)
assert(v2[2], isEqualTo = 30)
```
### normalize
`vector::normalize(@v: [number]): [number]`
```kcl
v = [3, 4]
normed = vector::normalize(v)
assert(normed[0], isEqualTo = 0.6)
assert(normed[1], isEqualTo = 0.8)
```
### sub
`vector::sub(@u: [number], v: [number]): [number]`
```kcl
u = [10, 10, 10]
v = [1, 2, 3]
v2 = vector::sub(u, v)
assert(v2[0], isEqualTo = 9)
assert(v2[1], isEqualTo = 8)
assert(v2[2], isEqualTo = 7)
```

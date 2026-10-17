# std::math
Functions for mathematical operations and some useful constants.
- `E: number = 2.71828182845904523536028747135266250_`: The value of Euler’s number `e`.
- `PI: number(_?) = 3.14159265358979323846264338327950288_?`: The value of `pi`, Archimedes’ constant (π).
- `TAU: number = 6.28318530717958647692528676655900577_`: The value of `tau`, the full circle constant (τ).

Common args:
- leg: The length of one of the triangle's legs (i.e. non-hypotenuse side).
### abs
`abs(@input: number): number`
### acos
`acos(@num: number(_)): number(rad)`
### asin
`asin(@num: number(_)): number(rad)`
### atan
`atan(@num: number(_)): number(rad)`
Consider using `atan2()` instead for the true inverse of tangent.
### atan2
`atan2(y: number(Length), x: number(Length)): number(rad)`
### ceil
`ceil(@input: number): number`
### cos
`cos(@num: number(Angle)): number`
### floor
`floor(@input: number): number`
### legAngX
`legAngX(hypotenuse: number(Length), leg: number(Length)): number(deg)`
```kcl
legAngX(hypotenuse = 5, leg = 3)
```
### legAngY
`legAngY(hypotenuse: number(Length), leg: number(Length)): number(deg)`
```kcl
legAngY(hypotenuse = 5, leg = 3)
```
### legLen
`legLen(hypotenuse: number(Length), leg: number(Length)): number(Length)`
```kcl
legLen(hypotenuse = 5, leg = 3)
```
### ln
`ln(@input: number): number`
### log
`log(@input: number, base: number(_)): number`
The result might not be correctly rounded owing to implementation details; `log2` can produce more accurate results for base 2, and `log10` can produce more accurate results for base 10.
### log10
`log10(@input: number): number`
### log2
`log2(@input: number): number`
### max
`max(@input: [number; 1+]): number`
### min
`min(@input: [number; 1+]): number`
### polar
`polar(angle: number(rad), length: number(Length)): Point2d`
### pow
`pow(@input: number, exp: number(_)): number`
### rem
`rem(@num: number, divisor: number): number`
- num: The number which will be divided by `divisor`.
- divisor: The number which will divide `num`.
```kcl
assert(rem(7, divisor = 4), isEqualTo = 3, error = "remainder is 3")
assert(rem(-7, divisor = 4), isEqualTo = -3, error = "remainder is -3")
assert(rem(7, divisor = -4), isEqualTo = 3, error = "remainder is 3")
assert(rem(6, divisor = 2.5), isEqualTo = 1, error = "remainder is 1")
assert(rem(6.5, divisor = 2.5), isEqualTo = 1.5, error = "remainder is 1.5")
assert(rem(6.5, divisor = 2), isEqualTo = 0.5, error = "remainder is 0.5")
```
### round
`round(@input: number): number`
### sin
`sin(@num: number(Angle)): number`
### sqrt
`sqrt(@input: number): number`
### tan
`tan(@num: number(Angle)): number`

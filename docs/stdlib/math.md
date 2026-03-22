# luz-math

Mathematical library included with Luz. No installation needed.

```
import "math"
```

---

## Constants

| Name | Value |
|---|---|
| `PI` | `3.14159265358979` |
| `TAU` | `6.28318530717959` |
| `E` | `2.71828182845905` |

```
write(PI)    # 3.14159265358979
write(TAU)   # 6.28318530717959
write(E)     # 2.71828182845905
```

---

## Number theory

### `factorial(n)`
Returns `n!`. Raises an error if `n < 0`.

```
write(factorial(6))   # 720
```

### `fibonacci(n)`
Returns the nth Fibonacci number (0-indexed).

```
write(fibonacci(10))  # 55
```

### `gcd(a, b)`
Greatest common divisor.

```
write(gcd(12, 8))   # 4
```

### `lcm(a, b)`
Least common multiple.

```
write(lcm(4, 6))    # 12
```

### `is_prime(n)`
Returns `true` if `n` is prime.

```
write(is_prime(17))   # true
write(is_prime(18))   # false
```

---

## Trigonometry

All functions work in **radians**. Use `to_rad` / `to_deg` to convert.

### `sin(x)` / `cos(x)` / `tan(x)`

```
write(sin(to_rad(90)))    # 1.0
write(cos(to_rad(0)))     # 1.0
write(tan(to_rad(45)))    # ~1.0
```

### `to_rad(degrees)` / `to_deg(radians)`

```
write(to_rad(180))   # 3.14159...
write(to_deg(PI))    # 180.0
```

---

## Logarithms

### `log(x)` — natural logarithm (base e)
### `log2(x)` — base-2 logarithm
### `log10(x)` — base-10 logarithm

```
write(round(log(E), 4))     # 1.0
write(round(log2(8), 4))    # 3.0
write(round(log10(100), 4)) # 2.0
```

---

## Geometry

### `hypot(a, b)`
Returns the hypotenuse of a right triangle with legs `a` and `b`.

```
write(hypot(3, 4))   # 5.0
```

### `distance(x1, y1, x2, y2)`
Returns the Euclidean distance between two points.

```
write(distance(0, 0, 3, 4))   # 5.0
```

### `cbrt(x)`
Returns the cube root of `x`. Works with negative values.

```
write(cbrt(27))    # 3.0
write(cbrt(-8))    # -2.0
```

### `lerp(a, b, t)`
Linear interpolation between `a` and `b` by factor `t` (0.0–1.0).

```
write(lerp(0, 100, 0.25))   # 25.0
```

### `map_range(x, in_min, in_max, out_min, out_max)`
Maps a value from one range to another.

```
write(map_range(5, 0, 10, 0, 100))   # 50.0
```

---

## Statistics

### `sum(list)`

```
write(sum([1, 2, 3, 4, 5]))   # 15
```

### `mean(list)`

```
write(mean([1, 2, 3, 4, 5]))  # 3.0
```

### `median(list)`

```
write(median([3, 1, 4, 1, 5]))   # 3
```

### `variance(list)` / `std_dev(list)`

```
data = [2, 4, 4, 4, 5, 5, 7, 9]
write(mean(data))      # 5.0
write(std_dev(data))   # 2.0
```

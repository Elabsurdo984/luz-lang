# luz-random

Random number and data generation library included with Luz. No installation needed.

```
import "random"
```

---

## Core

### `random()`
Random float between `0.0` and `1.0`.

```
write(random())   # e.g. 0.7341
```

### `random_float(low, high)`
Random float in the range `[low, high)`.

```
write(random_float(1.0, 5.0))
```

### `random_int(low, high)`
Random integer in the range `[low, high]` inclusive.

```
write(random_int(1, 100))   # e.g. 42
```

### `random_bool(chance)`
Returns `true` with the given probability (`0.0` – `1.0`).

```
write(random_bool(0.7))   # true ~70% of the time
```

### `coin()`
Returns `true` or `false` with equal probability.

```
write(coin())
```

### `random_sign()`
Returns `1` or `-1` at random.

### `random_normal(mean, std)`
Gaussian-distributed random value.

```
write(random_normal(0, 1))   # value near 0
```

### `seed(value)`
Set the random seed for reproducible results.

```
seed(42)
write(random_int(1, 10))   # always the same
```

---

## Sequences

### `pick(list)`
Pick one random element from a list.

```
colors = ["red", "green", "blue"]
write(pick(colors))
```

### `sample(list, n)`
Pick `n` unique elements from a list (no repetition).

```
write(sample([1, 2, 3, 4, 5], 3))   # e.g. [4, 1, 3]
```

### `shuffle(list)`
Return a new shuffled copy of the list.

```
deck = [1, 2, 3, 4, 5]
write(shuffle(deck))
```

### `random_list(n, low, high)`
Generate a list of `n` random integers.

```
write(random_list(5, 1, 10))   # e.g. [3, 7, 1, 9, 4]
```

### `weighted_pick(list, weights)`
Pick a random element using a weight for each item.

```
items   = ["common", "rare", "epic"]
weights = [70, 25, 5]
write(weighted_pick(items, weights))
```

---

## Generators

### `random_color()`
Returns a random hex color string.

```
write(random_color())   # e.g. "#a3f2c1"
```

### `random_token(length)`
Alphanumeric random string.

```
write(random_token(16))   # e.g. "gT3kPxZ9mN2wLqYv"
```

### `random_pin(length)`
Numeric PIN string.

```
write(random_pin(4))   # e.g. "7391"
```

### `random_uuid()`
UUID v4-style identifier.

```
write(random_uuid())   # e.g. "a1b2c3d4-e5f6-4789-abcd-ef0123456789"
```

---

## Dice

### `roll(sides)`
Roll a die with `sides` faces.

```
write(roll(6))    # 1–6
write(roll(20))   # 1–20
```

### `roll_sum(n, sides)`
Roll `n` dice and return the sum.

```
write(roll_sum(3, 6))   # sum of 3d6
```

### `roll_all(n, sides)`
Roll `n` dice and return all results as a list.

```
write(roll_all(4, 6))   # e.g. [3, 6, 1, 4]
```

### `roll_advantage(sides)` / `roll_disadvantage(sides)`
Roll twice and return the higher / lower result.

```
write(roll_advantage(20))     # best of 2d20
write(roll_disadvantage(20))  # worst of 2d20
```

### `chance(probability)`
Returns `true` with the given probability.

```
if chance(0.1) {
    write("Critical hit!")
}
```

### `flip()`
Returns `"heads"` or `"tails"`.

```
write(flip())
```

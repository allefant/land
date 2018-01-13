import global stdint
import global stdbool
import global stdarg
typedef float float32_t
typedef double LandFloat
typedef char const *str

def land_constrain(LandFloat *v, v_min, v_max) -> LandFloat:
    if *v < v_min: *v = v_min
    if *v > v_max: *v = v_max
    return *v

def land_mod(int x, d) -> int:
    """
    Version of % that always is positive.
    """
    x %= d
    if x < 0: x += d
    return x

def land_div(int x, d) -> int:
    """
    Version of / that rounds to negative infinity for negative numbers.
    """
    if x < 0:
        x -= d - 1
    x /= d
    return x

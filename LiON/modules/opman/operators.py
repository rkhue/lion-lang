import math
from typing import Iterable
from LiON.lion_node import (construct_def_operator,
                            exec_variable_like)


def union(a: tuple | set | str | Iterable, b: tuple | set | str | Iterable):
    if isinstance(a, set) and isinstance(b, set):
        return a.union(b)

    if isinstance(a, dict) and isinstance(b, dict):
        return a | b

    out = set(a + b)
    if isinstance(a, list) and isinstance(b, list):
        return list(out) if isinstance(a, list) or isinstance(b, list) else ''.join(out)

    out = tuple(set(a + b))

    return out if isinstance(a, tuple) or isinstance(b, tuple) else ''.join(out)


def intersection(a: tuple | set | str, b: tuple | set | str):
    if isinstance(a, set) and isinstance(b, set):
        return a.intersection(b)
    elif isinstance(a, tuple) and isinstance(b, tuple):
        return tuple(set(a) & set(b))

    elif isinstance(a, list) and isinstance(b, list):
        return list(set(a) & set(b))

    return ''.join(set(a) & set(b))


def difference(a: tuple | set | str, b: tuple | set | str):
    b_set = set(b)

    if isinstance(a, set):
        return a - b_set

    if isinstance(a, str):
        return ''.join([item for item in a if item not in b_set])

    return type(a)(item for item in a if item not in b_set)


def is_inside(a: tuple | set | str, b: tuple | set | str) -> bool:
    if isinstance(a, set) and isinstance(b, set):
        return a.issubset(b)

    for elem in a:
        if elem not in b:
            return False
    return True


def find_where(a, b: tuple | set | str) -> int:
    return sum(int(a == m) for m in b)


STANDARD_OPERATORS = {
    # Arithmetic Operators
    "+": construct_def_operator("+", type=2, proc=8, lam=lambda x, y: x + y),
    "-": construct_def_operator("-", type=2, proc=8, lam=lambda x, y: x - y),

    "*": construct_def_operator("*", type=2, proc=9, lam=lambda x, y: x * y),
    "of": construct_def_operator("of", type=2, proc=9, lam=lambda x, y: x * y),
    "/": construct_def_operator("/", type=2, proc=9, lam=lambda x, y: x / y),
    ":": construct_def_operator(":", type=2, proc=9, lam=lambda x, y: x / y),
    "//": construct_def_operator("//", type=2, proc=9, lam=lambda x, y: x // y),
    "%": construct_def_operator("%", type=2, proc=9, lam=lambda x, y: x % y),

    "**": construct_def_operator("**", type=2, proc=10, lam=lambda x, y: x ** y),
    "@": construct_def_operator("@", type=1, proc=10, lam=lambda x: math.sqrt(x)),

    # Iterable operators | Set theory
    "U": construct_def_operator("U", type=2, proc=6, lam=lambda x, y: union(x, y)),
    "!U": construct_def_operator("!U", type=2, proc=6, lam=lambda x, y: intersection(x, y)),
    "left": construct_def_operator("left", type=2, proc=5, lam=lambda x, y: difference(x, y)),
    "right": construct_def_operator("right", type=2, proc=5, lam=lambda x, y: difference(y, x)),
    "in": construct_def_operator("in", type=2, proc=4, lam=lambda x, y: x in y),
    "C": construct_def_operator("C", type=2, proc=5, lam=lambda x, y: is_inside(x, y)),
    "oc": construct_def_operator("oc", type=2, proc=5, lam=lambda x, y: find_where(x, y)),

    # Node operations
    ">>": construct_def_operator(">>", type=2, proc=5, lam=lambda rel, y: exec_variable_like(rel, (y,))),

    # Relational operators
    ">": construct_def_operator(">", type=2, proc=4, lam=lambda x, y: x > y),
    "<": construct_def_operator("<", type=2, proc=4, lam=lambda x, y: x < y),
    "==": construct_def_operator("==", type=2, proc=4, lam=lambda x, y: x == y),
    "is": construct_def_operator("is", type=2, proc=4, lam=lambda x, y: x is y),
    "!=": construct_def_operator("!=", type=2, proc=4, lam=lambda x, y: x != y),
    "<=": construct_def_operator("<=", type=2, proc=4, lam=lambda x, y: x <= y),
    ">=": construct_def_operator(">=", type=2, proc=4, lam=lambda x, y: x >= y),

    # Logical operators
    "and": construct_def_operator("and", type=2, proc=2, lam=lambda x, y: x and y),
    "or": construct_def_operator("or", type=2, proc=1, lam=lambda x, y: x or y),
    "xor": construct_def_operator("xor", type=2, proc=1, lam=lambda x, y: (x or y) and not (x and y)),
    "not": construct_def_operator("not", type=1, proc=3, lam=lambda x: not x),

    # Interval operators
    "~": construct_def_operator("~", type=2, proc=7, lam=lambda x, y: tuple(range(min(x, y), max(x + 1, y + 1)))),
    "~~": construct_def_operator("~~", type=2, proc=7, lam=lambda x, y: tuple(range(min(x + 1, y + 1), max(x, y)))),

    # Scaling operators
    "scale": construct_def_operator("scale", type=2, proc=5, lam=lambda x, y: x * (y ** -1)),
    "downscale": construct_def_operator("downscale", type=2, proc=5, lam=lambda x, y: x * y),
}

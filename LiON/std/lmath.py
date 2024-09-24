import math
global parent_parser, construct_builtin, construct_node, construct_variable


def delta(a, b, c):
    return (b**2) - (4 * a * c)


def bhaskara(a, b, c) -> tuple:
    if a == 0:
        raise ArithmeticError('Invalid equation, a must be != than 0')

    if c == 0:
        return 0, -b/(2*a)

    if b == 0:
        root = c**(1/2)
        return root, -root

    root_delta = delta(a, b, c) ** (1/2)
    if root_delta < 0:
        raise ArithmeticError('Solution not in the Real Numbers')

    return (-b + root_delta) / 2 * a, (-b - root_delta) / 2 * a


def vertex(a, b, c):
    d = delta(a, b, c)
    return (-b / (2*a)), (-d / (4*a))


MATH = construct_node("math")

MATH.update({
    "pi": construct_variable("pi", math.pi, __rs__=('final',)),
    "tau": construct_variable("phi", math.tau, __rs__=('final',)),
    "e": construct_variable("e", math.e, __rs__=('final',)),
    "nan": construct_variable("nan", math.nan, __rs__=('final',)),
    "inf": construct_variable("inf", math.inf, __rs__=('final',)),
    "isnan": construct_builtin("isnan", math.isnan),
    "isinf": construct_builtin("isinf", math.isinf),
    "isfinite": construct_builtin("isfinite", math.isfinite),
    "sum": construct_builtin("sum", sum),
    "max": construct_builtin("max", max),
    "min": construct_builtin("min", min),
    "any": construct_builtin("any", any),
    "all": construct_builtin("all", all),
    "sin": construct_builtin("sin", math.sin),
    "cos": construct_builtin("cos", math.cos),
    "tan": construct_builtin("tan", math.tan),
    "sinh": construct_builtin("sinh", math.sinh),
    "cosh": construct_builtin("cosh", math.cosh),
    "tanh": construct_builtin("tanh", math.tanh),
    "dist": construct_builtin("dist", math.dist),
    "radians": construct_builtin("radians", math.radians),
    "degrees": construct_builtin("degrees", math.degrees),
    "floor": construct_builtin("floor", math.floor),
    "log": construct_builtin("log", math.log),
    "log10": construct_builtin("log10", math.log10),
    "log2": construct_builtin("log2", math.log2),
    "hypot": construct_builtin("hypot", math.hypot),
    "ceil": construct_builtin("ceil", math.ceil),
    "round": construct_builtin("round", round),
    "abs": construct_builtin("abs", abs),
    "exp": construct_builtin("exp", math.exp),
    "factorial": construct_builtin("factorial", math.factorial),
    "delta": construct_builtin("delta", delta),
    "bhask": construct_builtin("bhask", bhaskara),
    "vertex": construct_builtin("vertex", vertex),
    "circlea": construct_builtin("circlea", lambda r: math.pi * r ** 2)
})

parent_parser.assign_references({
    "math": MATH
})

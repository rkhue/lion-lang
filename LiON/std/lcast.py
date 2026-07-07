global parent_parser, construct_node, construct_builtin


cast = construct_node("cast")

cast.update({
    "str": construct_builtin("str", lambda t: str(t)),
    "list": construct_builtin("list", lambda t: list(t)),
    "tuple": construct_builtin("tuple", lambda t: tuple(t)),
    "int": construct_builtin("int", lambda t: int(t)),
    "float": construct_builtin("float", lambda t: float(t)),
    "perc": construct_builtin(
        "perc",
        lambda t: (float(str(t).replace("%", "")) / 100) if not isinstance(t, int | float) else float(t) / 100),
    "bool": construct_builtin("bool", lambda t: bool(t)),
    "bin": construct_builtin("bin", bin),
    "oct": construct_builtin("oct", oct),
})

parent_parser.assign_references({
    "cast": cast,
})

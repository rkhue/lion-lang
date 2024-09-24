import string
global parent_parser, construct_builtin, construct_node, construct_variable

module = construct_node("str")

module.update({
    "alpha": construct_variable("alpha", string.ascii_lowercase),
    "digits": construct_variable("digits", string.digits),
    "hex": construct_variable("hex", string.hexdigits),
    "whitespace": construct_variable("whitespace", string.whitespace),
    "cap": construct_builtin("cap", lambda s: s.capitalize()),
    "lower": construct_builtin("lower", lambda s: s.lower()),
    "upper": construct_builtin("upper", lambda s: s.upper()),
    "isdigit": construct_builtin("isdigit", lambda s: s.isdigit()),
    "isalpha": construct_builtin("isalpha", lambda s: s.isalpha()),
    "isalnum": construct_builtin("isalnum", lambda s: s.isalnum()),
    "isnumeric": construct_builtin("isnumeric", lambda s: s.isnumeric()),
    "starts": construct_builtin("starts", lambda s, other: s.startswith(other)),
    "ends": construct_builtin("ends", lambda s, other: s.ends(other)),
    "slice": construct_builtin("slice", lambda s, start, end=None: s[start: end if end else len(s)]),
    "split": construct_builtin("split", lambda s, delimiter=' ': s.split(delimiter)),
    "reverse": construct_builtin("reverse", lambda s: s[::-1]),
    "substring": construct_builtin("substring", lambda s, index, forward: s[index:index + forward]),
    "join": construct_builtin("join", lambda s, iterable: str(s).join(iterable)),
    "format": construct_builtin("format", lambda s, *args: s.format(*args)),
    "strip": construct_builtin("strip", lambda s, chars=string.whitespace: "".join([ch for ch in s if ch not in chars]))
})

parent_parser.assign_references({
    "str": module
})

from functools import reduce
from typing import Any

global parent_parser, construct_builtin


def reduce_statement(node: dict[str, Any], iterable):
    return reduce(lambda x, y: parent_parser.exec(node, (x, y)), iterable)


parent_parser.assign_references({
    "min": construct_builtin("min", min),
    "max": construct_builtin("max", max),
    "sum": construct_builtin("sum", sum),
    "avg": construct_builtin("avg", lambda x: sum(x) / len(x)),
    "all": construct_builtin("all", all),
    "any": construct_builtin("any", any),
    "enum": construct_builtin("enum", enumerate),
    "range": construct_builtin("range", range),
    "zip": construct_builtin("zip", zip),
    "reduce": construct_builtin("reduce", reduce_statement),
})

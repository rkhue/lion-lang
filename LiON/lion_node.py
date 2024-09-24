from LiON.lang.lexerconst import LEXER_TYPE_PATHNAME
from LiON.lang.semantic import KEYWORD_DICTIONARY
from LiON.exceptions import LiONException
from LiON.lang.restrictions import *
from LiON.lang.const import *
from typing import Any


ITERABLE = tuple | list


def split_pathname(pathname: str, delimiter=PATHNAME_DELIMITER):
    return pathname.split(delimiter)


def get_pathname_name(pathname: str, delimiter=PATHNAME_DELIMITER):
    """
    Gets the last element from a given pathname
    :param delimiter: delimiter
    :param pathname: Path to node
    :return:
    """
    return pathname.rsplit(delimiter, 1)[-1]


def is_node(candidate):
    return isinstance(candidate, dict) and CLASS_ATTRIBUTE in candidate


def is_code(candidate):
    return (
            isinstance(candidate, list) and
            all(isinstance(item, dict) and LEXER_TYPE_PATHNAME in item for item in candidate) and
            len(candidate) != 0
    )


def typeof(x):
    if x is None:
        return None
    if is_code(x):
        return 'code'
    if is_node(x):
        return f'node:{x[CLASS_ATTRIBUTE]}'
    return x.__class__.__name__


def request_attribute(node: dict[str, Any], *attributes):
    for attr in attributes:
        yield node.get(attr)


def request_restrictions(node: dict[str, Any]) -> tuple:
    rs = node.get(RESTRICTIONS_ATTRIBUTE)
    return rs if rs is not None else ()


def reparse_callpart(key: str, dictionary: dict[str, Any],
                     if_false: tuple | dict | str | list | None = tuple()) -> tuple | list | dict | str:
    value = dictionary.get(key)
    return value if value else if_false


def get_from_dict(key: str, dictionary: dict) -> Any:
    if key in dictionary:
        return dictionary.pop(key)
    return None


def unbound_in(key: str, v: dict | None):
    if v is None:
        return False
    if v.get(key) is None:
        return False
    return True


def unbound_get(key: str, v: dict | None, func):
    if v is None:
        return None
    if v.get(key) is None:
        return None
    return func(v[key])


def yield_items(relative, args: ITERABLE) -> Any | ITERABLE:
    for a in args:
        if isinstance(a, ITERABLE):
            yield from yield_items(relative, a)
        else:
            yield relative[a]


def collections_rel_op(func):
    def wrapper(relative, args: ITERABLE):
        if args:
            assert relative is not None, "Cannot use relative operations on null values"
        assert hasattr(args, '__getitem__'), \
            "Cannot use relative operations on non-iterable values"
        return func(relative, args)

    return wrapper


@collections_rel_op
def pop_items(relative, args: ITERABLE) -> Any | ITERABLE:
    for a in args:
        if isinstance(a, ITERABLE):
            yield from pop_items(relative, a)
        else:
            yield relative.pop(a)


@collections_rel_op
def exec_variable_like(relative, args: ITERABLE) -> Any | ITERABLE:
    if not args:
        return relative

    if len(args) == 1:
        arg = args[0]
        if isinstance(arg, ITERABLE):
            return tuple(yield_items(relative, arg))
        return relative[arg]
    else:
        return tuple(yield_items(relative, args))


# NODE RELATED CONSTRUCTIONS

def override_node(node: dict[str, Any], override: dict[str, Any], include=None):
    if not include:
        node.update(override)
    else:
        node.update({k: v for k, v in override if k in include})


def construct_node(name, class_: NODE_CLASSES = NEWABLE, relative=None, restrictions=None, tag=None,
                   icon=None, doc=None, **kwargs) -> dict[str, Any]:
    node = {
        NAME_ATTRIBUTE: name,
        CLASS_ATTRIBUTE: class_,
        RELATIVE_ATTRIBUTE: relative,
    }

    assert isinstance(name, str), "Cannot make nodes with non-string names."
    assert isinstance(class_, str), "Cannot make nodes with non-string classes."

    if restrictions is not None:
        node[RESTRICTIONS_ATTRIBUTE] = restrictions

    if tag is not None:
        node[TAG_ATTRIBUTE] = tag

    if doc:
        node[DOCUMENTATION_ATTRIBUTE] = doc

    if icon:
        node[ICON_ATTRIBUTE] = icon

    if kwargs:
        # I don't like {__rs__:None}
        node.update({k: v for k, v in kwargs.items() if v is not None})

    return node


def construct_registry(name: str, **kwargs):
    return construct_node(name, REGISTRY, dict(), **kwargs)


def construct_method(name: str, **kwargs):
    return construct_node(name, METHOD, **kwargs)


def construct_builtin(name: str, func, **kwargs):
    node = construct_node(name, BUILTIN, func, **kwargs)
    return node


def construct_statement(name: str, func, **kwargs):
    node = construct_builtin(name, func, __class__=STATEMENT, **kwargs)
    return node


def construct_def_constructor(name: str, for_class: str, func, **kwargs):
    node = construct_builtin(name, func, __class__=DEFAULT_CONSTRUCTOR, __for__=for_class, **kwargs)
    return node


def construct_scope(name: str, **kwargs):
    return construct_node(name, SCOPE, **kwargs)


def construct_variable(name: str, value: Any = None, **kwargs) -> dict[str, Any]:
    """
    Constructs a node that behaves as a variable, with __rel__ being the given value
    :param name: Name of the variable
    :param value: Value of the variable
    :param kwargs: Extra arguments
    :return:
    """
    return construct_node(name, VARIABLE, value, **kwargs)


def construct_tree_conf(name: str, value: Any = None):
    return construct_variable(name, value, __class__=TREE_CONFIG)


def construct_dms(symbol: str, points: str):
    return construct_variable(symbol, points, __class__=DMS)


def construct_parameter(name: str, for_function: str, value=None, **kwargs) -> dict[str, Any]:
    return construct_variable(name, value, __class__=PARAMETER, __for__=for_function, **kwargs)


def construct_function(name: str, args: list | tuple, code, **kwargs) -> dict[str, Any]:
    """
    Constructs and a function node with empty variables for the arguments
    :param name: Name of the function
    :param args: Arguments names as a list with strings
    :param code: LiON code
    :return: dict[str, Any]
    """
    f_new_keys = {'__args__': tuple(args)} | {k: construct_parameter(k, name) for k in args}
    node = construct_node(name, FUNCTION, code, **kwargs)
    node.update(f_new_keys)
    return node


def construct_saber(name: str, code, **kwargs):
    return construct_node(name, SABER, code, **kwargs)


def construct_constructor(name: str, args, code, **kwargs):
    node = construct_function(name, args, code, __class__=CONSTRUCTOR, **kwargs)
    return node


def construct_lambda(args: list | tuple, code, **kwargs) -> dict[str, Any]:
    built = construct_function("<lambda>", args, code, __class__=LAMBDA, **kwargs)
    return built


def construct_alias(pathname: str, pointer: str, **kwargs):
    """
    Constructs an alias node that points to a given pathname
    :param pathname: Name of the alias
    :param pointer: Pathname to be pointed
    :return:
    """
    return construct_node(pathname, "alias", pointer, doc=f"Alias {repr(pathname)} pointing to path {repr(pointer)}",
                          **kwargs)


def construct_def_operator(name: str, type: int, proc: int, lam, **kwargs):
    operator_part = {
        PRECEDENCE_ATTRIBUTE: proc,
        TYPE_ATTRIBUTE: type,
        LAMBDA_ATTRIBUTE: lam,
    }
    node = construct_node(name, DEFAULT_OPERATOR, **operator_part, **kwargs)
    return node


def construct_operator(name: str, type: int, proc: int, lam, **kwargs):
    node = construct_def_operator(name, type, proc, lam, __class__=OPERATOR, **kwargs)
    return node


def construct_task(name: str, lam, delay=1, **kwargs):
    task_part = {
        LAMBDA_ATTRIBUTE: lam,
        DELAY_ATTRIBUTE: delay,
    }
    node = construct_node(name, TASK, **task_part, **kwargs)
    return node


def construct_locale(name: str, semantic: dict[str, str] = None, node_names: dict[str, str] = None,
                     locale: dict[str, str] = None):
    node = construct_node(name, LOCALE, locale)
    node.update({
        ARGUMENTS_ATTRIBUTE: node_names,
        SEMANTIC_ATTRIBUTE: semantic,
    })
    return node


def construct_exception(name: str, message: str = "Error", at=None, who=None, **kwargs):
    node = construct_node(name, EXCEPTION, message, **kwargs)
    node.update({ARGUMENTS_ATTRIBUTE: (at, who), })
    return node


def construct_from_pyException(exception: Exception, at=None, who=None, **kwargs):
    if isinstance(exception, LiONException):
        if exception.get_node() is not None:
            node = exception.get_node()
            node.update({NAME_ATTRIBUTE: f"node:{node[NAME_ATTRIBUTE]}",
                         ARGUMENTS_ATTRIBUTE: (who, at)})
            return node

    node = construct_exception(exception.__class__.__name__, str(exception), at, who, **kwargs)
    return node


def generate_locale(root: dict[str, Any]):
    locale = construct_locale("base",
                              KEYWORD_DICTIONARY,
                              {k: k for k, v in root.items() if is_node(v) and k not in EXCLUDE_FROM_LOCALES})
    return locale


def apply_restrictions(node: dict[str, Any], restrictions: tuple[str] = None, children=True):
    if not restrictions:
        restrictions = (PROTECT,)

    node.update({RESTRICTIONS_ATTRIBUTE: restrictions})
    if children:
        for k, v in node.items():
            if is_node(v):
                apply_restrictions(v, children=children, restrictions=restrictions)


def construct_tree(name="LiON", debug: bool = False):
    root = construct_node(name, NEWABLE)

    reg = construct_node("reg", TREE_CONFIG)
    reg.update({
        REGISTRY_OPERATOR: construct_registry(REGISTRY_OPERATOR),
        REGISTRY_CLASSES: construct_registry(REGISTRY_CLASSES),
        REGISTRY_TASK: construct_registry(REGISTRY_TASK),
        REGISTRY_LOCALES: construct_registry(REGISTRY_LOCALES),
        REGISTRY_PERMISSIONS: construct_registry(REGISTRY_PERMISSIONS),
        REGISTRY_EXCEPTIONS: construct_registry(REGISTRY_EXCEPTIONS),
        REGISTRY_DMS: construct_registry(REGISTRY_DMS),
    })

    root.update({
        REGISTRY_ROOT: reg,
        OUT: construct_tree_conf(OUT),
        DEBUG: construct_tree_conf(DEBUG, debug),
        THROW_ERRORS: construct_tree_conf(THROW_ERRORS, False),
    })

    return root

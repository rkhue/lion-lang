from LiON.lion_node import *
from LiON.lang.lexerconst import GLOBAL, FLIPPING_MAP
from LiON.exceptions import *
from typing import Callable
from functools import wraps

"""
OBJECTIVES
Must do all before getting it public

- Harden up security (make the secure node only modifiable in the instantiation of a scope)
    - Make override not allowed only if explicit
       - Avoid strange nodes


- [NODE VALIDATE]
    v Make nodes with illegal __name__ / __class__ types impossible 
    - Add warnings in parser for illegal nodes like functions with int __rel__
    
"""


class Scope:
    def __init__(self, name: str = LANGUAGE, debug: bool = None, secure: bool = True):
        self.name = name
        self.self = self
        self.scope_stack: list[dict[str, Any]] = [construct_scope(self.name)]
        self.stdout = print
        self.debug = debug
        self.secure = secure

    def __getitem__(self, item):
        return self.scope_stack[0][item]

    def get_debug(self, debug=None):
        return debug or self.debug

    def get_root(self):
        return self.scope_stack[0]

    def get_head(self):
        return self.scope_stack[-1]

    def get_name(self):
        return self.scope_stack[0][NAME_ATTRIBUTE]

    def __str__(self):
        return (f'\033[1m{self.get_name()}\033[0m{" => " if len(self.scope_stack) > 1 else ""}' +
                " => ".join(s[NAME_ATTRIBUTE] for s in self.scope_stack[1:]))

    def add_scope(self, name: str, refs: dict[str, Any], debug=None):
        if self.get_debug(debug):
            self.stdout(f"[SCOPE] Adding scope {repr(name)} with {len(refs)} refs => {repr(refs)}")
        self.scope_stack.append(construct_scope(str(name), **refs))

    def assign_references(self, refs: dict[str, Any]):
        self.scope_stack[0].update(refs)

    def assign_references_head(self, refs: dict[str, Any]):
        self.get_head().update(refs)

    def add_refs_head(self, **refs):
        self.get_head().update(refs)

    def release(self) -> dict[str, Any]:
        if len(self.scope_stack) < 2:
            raise SystemError(f"Cannot release global scope {self.get_name()}")
        return self.scope_stack.pop()

    # NODE MODIFY OPERATIONS
    # Direct Operations
    def get_exact(self, path: tuple[str], root: dict[str, Any]) -> Any | dict[str, Any]:
        step = root
        for i, p in enumerate(path):
            if p not in step:
                parent = ".".join(path[:i]) if i != 0 else self.get_root()[NAME_ATTRIBUTE]
                raise NodeNotFound(f"Could not find node {repr(path[i])}"
                                   f" at parent {repr(parent)}")

            step = step[p]

        return step

    def pop_exact(self, path: tuple[str], root: dict[str, Any] = None) -> dict[str, Any]:
        branch = root
        for i, name in enumerate(path[:-1]):
            if name not in branch:
                raise NodeNotFound(f'Could not delete node on path {repr(".".join(path))} because'
                                   f' the parent "{".".join(path[:i + 1])}" does not exist')

            branch = branch[name]

        if is_node(branch[path[-1]]):
            if (
                    RESTRICTIONS_ATTRIBUTE in branch[path[-1]]
                    and branch[path[-1]][RESTRICTIONS_ATTRIBUTE]
                    is not None and PROTECT in branch[path[-1]][RESTRICTIONS_ATTRIBUTE]
            ) and self.secure:
                raise NodeIsProtected(f"Cannot pop {repr('.'.join(path))}, node is protected.")

        assert path[-1] not in ESSENTIAL_ATTRIBUTES, f"Cannot pop {repr('.'.join(path))}, attribute is essential"

        return branch.pop(path[-1])

    def pack_exact(self, path: tuple[str], node: dict[str, Any], root: dict[str, Any]):
        pathsize = len(path)
        branch = root
        for i, name in enumerate(path):
            if name in branch and i == pathsize - 1:
                if is_node(branch[name]):
                    if branch[name][CLASS_ATTRIBUTE] != node[CLASS_ATTRIBUTE]:
                        raise ClassMismatch(f"Override class mismatch for node {repr('.'.join(path[:i + 1]))}"
                                            f" and {repr(node[NAME_ATTRIBUTE])}"
                                            f" '{branch[name][CLASS_ATTRIBUTE]}' != '{node[CLASS_ATTRIBUTE]}'")
                else:
                    parent = ".".join(path[:i]) if i != 0 else self.get_root()[NAME_ATTRIBUTE]
                    raise IsNotANode(f"Cannot override any attribute, tried overriding {repr(name)} "
                                     f"from parent {repr(parent)}")

                branch[name].update(node)

            if name not in branch:
                # if 'protect' in get_pr(branch) and security:
                #     raise NodeIsProtected(f'Cannot overwrite to {repr(pathname)} because node is protected.')

                if i < pathsize - 1:
                    raise NodeNotFound(f'Could not create node on path {repr(".".join(path))} because'
                                       f' the parent {repr(".".join(path[:i + 1]))}" does not exist')

                branch[name] = node
                continue

            branch = branch[name]

    def conf_exact(self, path: tuple[str], value, root: dict[str, Any]):
        # TODO: Fix scope issues with conf
        if len(path) == 1:
            if path[0] in {NAME_ATTRIBUTE, CLASS_ATTRIBUTE}:
                assert isinstance(value, str), "Cannot change node's __name__ nor __class__ to non-string values."

            root.update({path[0]: value})
            return

        left, domain, key = path[:-2], path[-2], path[-1]
        domain: str
        leftpath = ".".join(left)

        # print(left, domain, key)

        if leftpath:
            node = self.get_exact(path[:-1], root)
        else:
            node = self.get_exact((domain,), root)

        if is_node(node):
            if (FINAL in request_restrictions(node) and key == RELATIVE_ATTRIBUTE
                    and self.secure):
                raise NodeIsFinal(f'Cannot modify relative from node {repr(node[NAME_ATTRIBUTE])}'
                                  f' because it is final.')

            if key in {NAME_ATTRIBUTE, CLASS_ATTRIBUTE}:
                assert isinstance(value, str), "Cannot change node's __name__ nor __class__ to non-string values."

        node.update({key: value})

    # Bridge operations

    def repass_scope_operation(self, path: list[str], method: Callable, *args, **kwargs):
        last_err = None
        for scope in reversed(self.scope_stack):
            try:
                return method(path, *args, root=scope, **kwargs)
            except NodeNotFound as error:
                last_err = error

        raise last_err

    def repass_operation(self, pathname: str, method: Callable,
                         *args, __scope__=None):
        path = split_pathname(pathname)

        if __scope__ is not None:
            try:
                return method(path, *args, root=self.get_root() if __scope__ == GLOBAL else self.get_head())
            except NodeNotFound as err:
                raise NodeNotFound(err.__str__() + f" in the {repr(__scope__)} scope")

        return self.repass_scope_operation(path, method, *args)

    def get(self, pathname: str, __scope__=None) -> Any | dict[str, Any]:
        return self.repass_operation(pathname, self.get_exact, __scope__=__scope__)

    def pack(self, pathname: str, node: dict[str, Any], __scope__=None):
        self.repass_operation(pathname, self.pack_exact, node, __scope__=__scope__)

    def pop(self, pathname: str, __scope__=None) -> Any | dict[str, Any]:
        return self.repass_operation(pathname, self.pop_exact, __scope__=__scope__)

    def drop(self, pathname: str | tuple[str], __scope__=None):
        if not isinstance(pathname, tuple):
            self.pop(pathname, __scope__=__scope__)
            return
        for name in pathname:
            self.pop(name, __scope__=__scope__)

    def move(self, pathname: str, parent_pathname: str, __scope__=None):
        node = dict(self.get(pathname, __scope__=__scope__))
        self.pack(parent_pathname + '.' + get_pathname_name(pathname), node, __scope__=__scope__)
        self.drop(pathname)

    def rename(self, pathname: str, new_pathname: str, __scope__=None):
        node = dict(self.get(pathname, __scope__=__scope__))
        node.update({NAME_ATTRIBUTE: get_pathname_name(new_pathname)})
        self.pack(new_pathname, node, __scope__=__scope__)
        self.drop(pathname)

    def conf(self, pathname: str, value=None, __scope__=None):
        return self.repass_operation(pathname, self.conf_exact, value, __scope__=__scope__)

    def set_rel(self, pathname: str, value, __scope__=None):
        self.conf(pathname + "." + RELATIVE_ATTRIBUTE, value, __scope__=__scope__)

    def flip(self, pathname: str, __scope__=None):
        node = self.get(pathname, __scope__)
        try:
            typ = type(node[RELATIVE_ATTRIBUTE])
            rel = typ(FLIPPING_MAP[node[RELATIVE_ATTRIBUTE]])
        except KeyError as e:
            raise FlippingError(f"Unable to find flip mappings for {repr(node[RELATIVE_ATTRIBUTE])}"
                                f" the relative of node {repr(node[NAME_ATTRIBUTE])} | {e}")

        node[RELATIVE_ATTRIBUTE] = rel

    def restrict(self, pathname: str, restrictions: tuple[str], __scope__=None):
        node = self.get(pathname, __scope__=__scope__)
        assert is_node(node), "Cannot restrict an attribute or a non-node"
        restrictions = tuple(restrictions)
        if RESTRICTIONS_ATTRIBUTE in node:
            node[RESTRICTIONS_ATTRIBUTE] = tuple(set(restrictions + tuple(node[RESTRICTIONS_ATTRIBUTE])))
        else:
            node.update({RESTRICTIONS_ATTRIBUTE: restrictions})

    @staticmethod
    def _get_cache_node():
        return {
            "cache": construct_builtin("cache", lambda: "Cache is to be implemented.", **{
                "clear": construct_builtin("clear", lambda: "Cache is to be implemented.")
            }),
        }


# DECORATORS


def scoped(scope_name: str = None, refs: dict[str, Any] = None):
    """
    Decorator used for executing functions in scope contexts.
    :param scope_name: Name of the scope
    :param refs: Additional references
    :return:
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                self = args[0]
                self.add_scope(scope_name, refs if refs is not None else {})
                result = func(*args, **kwargs)
                return result

            finally:
                self = args[0]
                if self.get_debug():
                    self.stdout(
                        f'[@scoped] Releasing scope {repr(scope_name)} at level {len(self.scope_stack)}')
                self.release()

        return wrapper

    return decorator


def rel_modify(func):
    def wrapper(*args, __scope__=None):
        assert len(args) > 1, ("[@rel_modify] All relative operation nodes must receive"
                               "at least 1 argument")
        self: Scope = args[0]
        node = self.get(args[1], __scope__=__scope__)

        if is_node(node):
            node[RELATIVE_ATTRIBUTE] = func(self, node[RELATIVE_ATTRIBUTE], *args[2:])
        else:
            self.conf(args[1], func(self, node, *args[2:]), __scope__=__scope__)

    return wrapper


def rel_retrieve(func):
    def wrapper(*args, __scope__=None):
        assert len(args) > 1, ("[@rel_modify] All relative operation nodes must receive"
                               "at least 1 argument")
        self: Scope = args[0]
        node = self.get(args[1], __scope__=__scope__)

        if is_node(node):
            return func(self, node[RELATIVE_ATTRIBUTE], *args[2:])
        return func(self, node, *args[2:])

    return wrapper

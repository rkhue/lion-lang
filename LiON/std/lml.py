from LiON.modules.lml.compile import LMLCompiler
from LiON.exceptions import LiONException
from typing import Any, Callable

global parent_parser, construct_builtin, construct_node, funclib

DEFAULT_STDOUT = parent_parser.stdout


class InvalidLMLMode(LiONException):
    pass


def node_func(node: dict[str, Any]):
    def wrapper(*args, **kwargs):
        return parent_parser.exec(node, args, kwargs)

    return wrapper


def lml_mode(modes: dict[str, Callable]):
    def decorator(func):
        def wrapper(mode: str, args: str, refs: dict[str, Any] = None):
            if refs is None:
                refs = {}

            if mode not in modes:
                raise InvalidLMLMode(f"Cannot invoke LML mode {mode:!r}, expected:"
                                     f" {', '.join((repr(s) for s in modes))}")

            return func(modes[mode], args, refs)

        return wrapper
    return decorator


def lml_compile_code(code: str, refs: dict[str, Any]) -> LMLCompiler:
    lmlc = LMLCompiler(code, parent_parser, DEFAULT_STDOUT, refs)
    lmlc.compile()
    return lmlc


def lml_compile_file(filepath: str, refs: dict[str, Any]):
    content = funclib.loadRaw(filepath)
    return lml_compile_code(content, refs)


def lml_run_code(code: str, refs: dict[str, Any]):
    lmlc = lml_compile_code(code, refs)
    lmlc.run()


def lml_run_file(filepath: str, refs: dict[str, Any]):
    lmlc = lml_compile_file(filepath, refs)
    lmlc.run()


@lml_mode({"file": lml_run_file, "code": lml_run_code})
def lml_run(func, args: str, refs: dict[str, Any]):
    return func(args, refs)


@lml_mode({"file": lml_compile_file, "code": lml_compile_code})
def lml_compile(func, args: str, refs: dict[str, Any]):
    return func(args, refs)


lml = construct_node("lml")
lml.update({
    "cpl": construct_builtin("cpl", lml_compile),
    "run": construct_builtin("run", lml_run)
})

parent_parser.assign_references({
    "lml": lml
})

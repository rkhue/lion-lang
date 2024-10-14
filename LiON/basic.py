from LiON.modules.opman.operators import STANDARD_OPERATORS
from LiON.modules.opman import OperatorManager
from LiON.modules.lman import LanguageManager
from LiON.lexer import transpose_call, lexer_cascade
from LiON.modules.dms import LionDMS
from LiON.lang.semantic import *
from functools import lru_cache, reduce
from LiON.parser import *
from LiON import funclib
import sys
import os

MODULE_DIR = os.path.dirname(__file__)
sys.path.append(MODULE_DIR + "./std/")

DOCUMENTATION = funclib.loadRaw(f"{MODULE_DIR}/assets/doc/liondoc.md")
NOTICE = funclib.loadRaw(f"{MODULE_DIR}/assets/conf/notice.txt")
HELP = funclib.loadRaw(f"{MODULE_DIR}/assets/doc/help.md")


def constructor_def_constructor(pathname: str,
                                args, code: list[dict] = None, __rs__=None):
    if not code:
        code = list(args)
        args = ()

    return construct_constructor(
        get_pathname_name(pathname), args, code, __rs__=__rs__
    )


class LiONBasic(TreeManager):
    def __init__(self, name: str = LANGUAGE, cargo: dict[str, Callable] = None):
        super().__init__(name)
        self.stdout = print
        self.token_extrafunc = self.extrafunc

        # Registry managers
        self.dms = LionDMS(self, os.getcwd(), MODULE_DIR)
        self.opman = OperatorManager(self)
        self.lman = LanguageManager(self)

        self.cargo: dict[str, Callable] = {
            "CACHE": self._get_cache_node,
            "BASIC": self.get_basic,
            "DMS": self.dms.get_basic,
            "LMAN": self.lman.get_basic,
        }
        if cargo:
            self.cargo.update(cargo)

        self.setup()

    def print_finished(self, prompt: str):
        self.stdout(f"[{self.get_name()}] Finished: {repr(prompt)}")

    def extrafunc(self, token: tuple[str, Any]):
        name = token[0]
        value = token[1]
        if name == DMS_DIRECTORY_TYPE:
            return self.dms.parse(value)
        return value

    def setup(self):

        # * Setup version
        self.assign_references({
            DOCUMENTATION_ATTRIBUTE: DOCUMENTATION,
            NOTICE_ATTRIBUTE: NOTICE,
            VERSION_ROOT: funclib.openJson(MODULE_DIR + "/assets/conf/verinfo.json")
        })
        # * Setup registry

        # - Setup operators
        self.update_registry_domain(REGISTRY_OPERATOR, STANDARD_OPERATORS)

        # - Build up cargo
        # self.stdout(f"[{self.name} at `setup`] Building up cargo for {repr(self.get_name())} ({len(self.cargo)})")
        for name, func in self.cargo.items():
            self.assign_references(func())
            # self.stdout(f"[OK] {name}")

        # - Setup locale / semantics
        self.promote(generate_locale(self.get_root()))

        # Apply restrictions `protect` to tree
        apply_restrictions(self.scope_stack[0])

    @lru_cache
    def get_docs(self, pathname: str):
        """
        Gets the documentation from the @assets/docs/nodes directory.
        :param pathname: Given pathname
        :return: Documentation text
        """
        content = funclib.loadRaw(self.dms.parse("@assets/doc/node/") + pathname + ".md")
        return content

    def get_basic(self):
        return {
            # RUN / HELP STATEMENTS / IMPLEMENTATION STATEMENTS
            "help": construct_statement("help", self.help_statement),
            "lion": construct_statement("lion", self.run_statement, __icon__="🦁"),
            "import": construct_statement("import", self.import_statement),

            # TREE MANAGEMENT STATEMENTS
            "*": construct_statement("*", self.star_statement),
            "get": construct_statement("get", self.get),
            "pop": construct_statement("pop", self.pop_statement),
            "drop": construct_statement("drop", self.drop),
            "pack": construct_statement("pack", self.pack_statement),
            "export": construct_statement("export", self.export_statement),
            "move": construct_statement("move", self.move),
            "rename": construct_statement("rename", self.rename),
            "new": construct_statement("new", self.new_statement),
            "call": construct_statement("call", self.call_statement),
            "exec": construct_statement("exec", self.exec),
            "conf": construct_statement("conf", self.conf),
            "set": construct_statement("set", self.set_statement),
            "flip": construct_statement("flip", self.flip),
            "restrict": construct_statement("restrict", self.restrict_statement),
            "promote": construct_statement("promote", self.promote_from_pathname),
            "demote": construct_statement("demote", self.demote),

            # CONTROL STATEMENTS
            "if": construct_statement("if", self.if_statement),
            "switch": construct_statement("switch", self.switch_statement),
            "do": construct_statement("do", self.do_statement),
            "repeat": construct_statement("repeat", self.repeat_statement),
            "each": construct_statement("each", self.each_statement),
            "while": construct_statement("while", self.while_statement),
            "for": construct_statement("for", self.for_statement),
            "iter": construct_statement("iter", self.iter_statement),
            "itert": construct_statement("itert", self.iter_tuple_statement),
            "iters": construct_statement("iters", self.iter_string_statement),
            "filter": construct_statement("filter", self.filter_statement),
            "assert": construct_statement("assert", self.assert_statement),
            "throw": construct_statement("throw", self.throw),
            "try": construct_statement("try", self.try_statement),
            "keysfrom": construct_statement("keysfrom", self.keysfrom_statement),
            "return": construct_statement("return", self.return_statement),

            # RELATIVE OPERATIONS
            "push": construct_statement("push", self.push_statement),
            "extend": construct_statement("extend", self.extend_statement),

            # CONSTRUCTORS
            "node": construct_def_constructor("node", NEWABLE, construct_node),
            "struct": construct_def_constructor("struct", NEWABLE, self.struct_def_constructor),
            "inherited": construct_def_constructor("inherited", INHERITED, self.inherited_def_constructor),
            "overload": construct_def_constructor("overload", NEWABLE, self.overload_def_constructor),
            "method": construct_def_constructor("method", METHOD, construct_method),
            "exception": construct_def_constructor("exception", EXCEPTION, construct_exception),
            "var": construct_def_constructor("var", VARIABLE, construct_variable),
            "alias": construct_def_constructor("alias", ALIAS, construct_alias),
            "function": construct_def_constructor("function", FUNCTION, self.function_def_constructor),
            "saber": construct_def_constructor("saber", SABER, construct_saber),
            "lam": construct_anon_constructor("lam", LAMBDA, self.lambda_anon_constructor),
            "operator": construct_def_constructor("operator", OPERATOR, self.operator_def_construtor),
            "constructor": construct_def_constructor("constructor", CONSTRUCTOR, constructor_def_constructor),
            "class": construct_def_constructor("class", CLASS, self.class_def_constructor),

            # CONVENIENCE CONSTRUCTORS
            "string": construct_def_constructor("string", VARIABLE, self.string_def_constructor),
            "tuple": construct_def_constructor("tuple", VARIABLE, self.tuple_def_constructor),
            "list": construct_def_constructor("list", VARIABLE, self.list_def_constructor),
            "keyvalue": construct_def_constructor("keyvalue", VARIABLE, self.keyvalue_def_constructor),

            # ARITHMETIC:
            "sum": construct_builtin("sum", sum),
            "avg": construct_builtin("avg", lambda x: sum(x) / len(x)),
            "all": construct_builtin("all", all),
            "any": construct_builtin("any", any),
            "enum": construct_builtin("enum", enumerate),
            "range": construct_builtin("range", range),
            "reduce": construct_builtin("reduce", self.reduce_statement),
            "$": construct_builtin("$", self.eval_builtin),
            "!": construct_builtin("!", lambda *args, **kwargs: not self.eval_builtin(*args, **kwargs)),
            "+": construct_builtin("+", self.ret_increment_builtin),
            "-": construct_builtin("-", self.ret_decrease_builtin),
            "++": construct_builtin('++', self.increment_builtin),
            "--": construct_builtin('--', self.decrease_builtin),

            # GENERAL USE BUILTINS
            "stdout": construct_builtin("stdout", self.stdout),
            "clear": construct_builtin("clear", funclib.clear),
            "info": construct_builtin("info", self.info),
            "scopes": construct_builtin("scopes", lambda: self.stdout(self.__str__())),
            "typeof": construct_builtin("typeof", typeof),
            "is": self._get_is(),
        }

    def execute_python(self, filename: str, parent_console=None):
        filename = self.dms.parse(filename)
        directory = funclib.getDirFromDir(filename)

        # Add the directory to sys.path
        sys.path.append(directory)

        with open(filename, 'r', encoding='utf-8') as file:
            code = compile(file.read(), filename, 'exec')

        exec(code, {
            'parent_parser': parent_console if parent_console else self,
            'dms': self.dms,
            "lman": self.lman,
            "opman": self.opman,
            'funclib': funclib,
            "construct_tree_config": construct_tree_conf,
            'construct_variable': construct_variable,
            'construct_builtin': construct_builtin,
            'construct_node': construct_node,
            "stdout": self.stdout,
            "stdin": self.stdin,
            "stderr": self.stderr,
            "root": self.get_root(),
            '__filename__': filename,
            '__home__': os.getcwd(),
        })

    # STATEMENTS

    def _get_is(self):
        return construct_builtin("is", lambda x, y: typeof(x) == y, **{
            "node": construct_builtin("node", is_node),
            "code": construct_builtin("code", is_code),
            "op": construct_builtin("op", self.opman.is_operator),
        })

    def star_statement(self, from_=None, pathname: str = None, __scope__=GLOBAL):
        if from_ is not None:
            assert pathname, "Star statement requires a pathname after the from keyword"
            from_kw = self.lman.query_semantics((FROM_KEYWORD,))
            assert from_ in from_kw, f"Expected semantic keywords {repr(from_kw)}, got {repr(from_)}"
            root = self.get(pathname, __scope__)
            return tuple(s for s in root.values() if is_node(s))

        if __scope__ == GLOBAL:
            return tuple(s for s in self.get_root().values() if is_node(s))
        elif __scope__ == LOCAL:
            return tuple(s for s in self.get_head().values() if is_node(s))

    def import_statement(self, *args):
        kw = self.lman.query_semantics((FROM_KEYWORD,))
        from_kw = kw[FROM_KEYWORD]
        assert len(args) >= 1, ("Incomplete call to import statement. Use a `from` or a"
                                " filepath")
        if args[0] in from_kw:
            if len(args[1:]) < 2:
                raise IncompleteCallError("Incomplete call to import-from statement. "
                                          f"Please provide a `base` and a tuple with"
                                          f" filenames. Got {args[1:]}")

            base = args[1]
            filenames = args[2]
            assert isinstance(filenames, tuple | list), f"Expected a filename list after specifying the base `{base}`"

            for filename in filenames:
                self.execute_python(base + "/" + filename.strip())

        else:
            for f in args:
                self.execute_python(f)

    def run_statement(self, filename: str, silent=False):
        file = funclib.loadRaw(self.dms.parse(filename))
        self.parsefunc(file, debug=self.get_debug())
        if not silent:
            self.print_finished(filename)

    def pop_statement(self, pathname: str, *indexes, __scope__=None):
        if not indexes:
            return self.pop(pathname, __scope__)
        rel = self.get(pathname, __scope__)

        if is_node(rel):
            rel = rel[RELATIVE_ATTRIBUTE]

        if len(indexes) == 1 and isinstance(indexes[0], int):
            return rel.pop(indexes[0])
        return tuple(pop_items(rel, indexes))

    def extend_statement(self, pathname: str, iterable, __scope__=None):
        rel = self.get(pathname, __scope__)
        if is_node(rel):
            rel = rel[RELATIVE_ATTRIBUTE]

        assert isinstance(rel, list)
        rel.extend(iterable)

    def push_statement(self, pathname: str, things: Any | tuple[Any]):
        rel = self.get(pathname)[RELATIVE_ATTRIBUTE]
        assert isinstance(rel, list), f"Cannot use push to {repr(pathname)} with a non-list relative"
        if isinstance(things, tuple):
            rel.extend(things)
        else:
            rel.append(things)

    def pack_statement(self, pathname: str, node: dict[str, Any] | str, filename=None, __scope__=None):
        if isinstance(node, str):
            sem = self.lman.query_semantics((FROM_KEYWORD,))
            from_kw = sem[FROM_KEYWORD]

            assert node in from_kw, "Must use either the keyword `from` or pass a node to `pack`"
            assert filename is not None, "Cannot provide an empty filename after using the `from` keyword"

            node = funclib.openJson(self.dms.parse(filename))
        else:
            assert filename is None, "Cannot pack a node both from a file and passed as an argument."

        self.pack(pathname, node, __scope__=__scope__)

    def export_statement(self, node: dict[str, Any] | str, filename=None, __scope__=None):
        if isinstance(node, str):
            node = self.get(node, __scope__=__scope__)

        if not filename:
            filename = f'{node[NAME_ATTRIBUTE]}.json'

        funclib.write_file(self.dms.parse(filename), json.dumps(node, indent=4, ensure_ascii=False))

    def new_statement(self, pathname, *args, **kwargs):
        restrictions = get_from_dict(RESTRICTIONS_ATTRIBUTE, kwargs)
        return self.new(self.get(pathname), args, kwargs, restrictions)[1]

    def call_statement(self, pathname: str, *args, **kwargs):
        restrictions = get_from_dict(RESTRICTIONS_ATTRIBUTE, kwargs)
        scope = get_from_dict(SCOPE_ATTRIBUTE, kwargs)
        return self.call(pathname, args, kwargs, restrictions, scope)

    def exec_statement(self, node: dict[str, Any], args, **kwargs):
        restrictions = get_from_dict(RESTRICTIONS_ATTRIBUTE, kwargs)
        scope = get_from_dict(SCOPE_ATTRIBUTE, kwargs)
        return self.exec(node, args, kwargs, restrictions, scope)

    def set_statement(self, pathname: str, value=None, __rs__=None, __scope__=None):
        self.set_rel(pathname, value, __scope__=__scope__)

    def restrict_statement(self, pathname: str, restrictions: tuple[str], __scope__=None):
        if isinstance(pathname, (tuple, list)):
            for p in pathname:
                self.restrict(p, restrictions, __scope__)
        else:
            self.restrict(pathname, restrictions, __scope__)

    # CONSTRUCTORS
    def inherited_def_constructor(self, pathname: str, inherit: str, *args, __rs__=None, **kwargs):
        node = self.get(inherit)
        node_constructor = self.get(node[INSTANCEOF_ATTRIBUTE])
        built = self.new(node_constructor, (pathname,) + args, kwargs, restrictions=__rs__)

        result = copy.deepcopy(node)
        result.update(built[1])
        result.update({NAME_ATTRIBUTE: get_pathname_name(pathname)})

        if self.get_debug():
            self.stdout(f'[{self.name} built {repr(pathname)} inherited from {node[CLASS_ATTRIBUTE]} {repr(inherit)}:] '
                        f'=> {built}')

        return result

    @scoped("struct")
    def struct_def_constructor(self, pathname: str, code, filename=None, __rs__=None):
        name = get_pathname_name(pathname)
        if isinstance(code, str):
            assert code in self.lman.query_semantics((FROM_KEYWORD,))[FROM_KEYWORD], ("Expected "
                                                                                      "third argument to "
                                                                                      "be the `from` keyword.")
            code = full_lexer(funclib.loadRaw(self.dms.parse(filename)))
        else:
            assert filename is None, "Cannot create struct both from local code and from a filename"

        struct = construct_node(name, __rs__=__rs__)

        self.parse_calls_direct(code)
        struct.update({k: v for k, v in self.get_head().items() if k not in {NAME_ATTRIBUTE, CLASS_ATTRIBUTE}})

        return struct

    def class_def_constructor(self, pathname: str, code, filename: str = None, __rs__=None):
        custom_struct = self.struct_def_constructor(pathname, code, filename=filename, __rs__=__rs__)
        custom_struct.update({CLASS_ATTRIBUTE: CLASS})
        return custom_struct

    def overload_def_constructor(self, pathname: str, code, filename: str = None, __rs__=None):
        custom_struct = self.struct_def_constructor(pathname, code, filename=filename, __rs__=__rs__)
        fns = {k: v for k, v in custom_struct.items() if is_node(v)}
        out_overload = construct_node(get_pathname_name(pathname), OVERLOAD, fns)
        if fns.get("_"):
            out_overload.update({"_": fns.pop("_")})
        return out_overload
    @staticmethod
    def function_def_constructor(pathname: str, args, code: list = None, **kwargs):
        if not code:
            code = list(args)
            args = ()

        return construct_function(pathname, args, code, **kwargs)

    @staticmethod
    def lambda_anon_constructor(args: tuple | list[dict[str, Any]], code: list = None, **kwargs):
        if code is None:
            code = list(args)
            args = tuple()

        return construct_lambda(args, code, **kwargs)

    def operator_def_construtor(self, symbol: str, data: dict[str, Any] | str, **kwargs) -> dict[str, Any]:
        if isinstance(data[PRECEDENCE_ATTRIBUTE], str):
            data[PRECEDENCE_ATTRIBUTE] = self.opman.get_operator_precedence(self.opman.get(data[PRECEDENCE_ATTRIBUTE]))

        return construct_operator(symbol, **kwargs, **data)

    # CONVENIENCE CONSTRUCTORS
    @staticmethod
    def tuple_def_constructor(pathname: str, *values, __rs__=None):
        return construct_variable(pathname, values, __rs__=__rs__)

    @staticmethod
    def list_def_constructor(pathname: str, *values, __rs__=None):
        return construct_variable(pathname, list(values), __rs__=__rs__)

    @staticmethod
    def keyvalue_def_constructor(pathname: str, dictionary: dict = None, __rs__=None):
        return construct_variable(pathname, dictionary if dictionary is not None else {}, __rs__=__rs__)

    @staticmethod
    def string_def_constructor(pathname: str, chars="", __rs__=None):
        return construct_variable(pathname, chars, __rs__=__rs__)

    # STATEMENTS

    @staticmethod
    def return_statement(thing):
        return thing

    def keysfrom_statement(self, pathname, __scope__=None):
        if isinstance(pathname, dict):
            assert __scope__ is None, "Cannot pass a scope to `keysfrom` with a key-value pair."
            return tuple(pathname.keys())

        return tuple(self.get(pathname, __scope__).keys())

    # Control statements

    def cascade_if_statement(self, lexed_cascade, if_kw, elif_kw, else_kw):
        did_the_if = False
        out = None
        success = False
        for pace in lexed_cascade:
            call = pace[0]
            condition = pace[1]
            if call in if_kw:
                if not did_the_if:
                    did_the_if = True
                    if condition:
                        out = self.parse_calls(pace[2])
                        success = True
                    continue
                else:
                    raise ParsingError("Cannot call 'if' 2 or more times within a cascade.")

            if call in elif_kw and condition:
                out = self.parse_calls(pace[2])
                success = True
                continue

            if not success and call in else_kw:
                out = self.parse_calls(pace[1])
                break

        return out

    def if_statement(self, *args, __rs__=None):
        semantics = self.lman.query_semantics((IF_KEYWORD, ELIF_KEYWORD, ELSE_KEYWORD))
        if_kw = semantics[IF_KEYWORD]
        elif_kw = semantics[ELIF_KEYWORD]
        else_kw = semantics[ELSE_KEYWORD]

        if not args:
            raise ParsingError(f'Incomplete call to {if_kw}'
                               f', please specify at least a condition and a codeblock.')
        cascading = True if __rs__ and 'cascade' in __rs__ else False

        lexed_cascade = lexer_cascade(("if",) + args, self.get_debug(), recognized_blocks=if_kw + elif_kw + else_kw)

        if cascading:
            return self.cascade_if_statement(lexed_cascade, if_kw, elif_kw, else_kw)

        did_the_if = False
        for pace in lexed_cascade:
            call = pace[0]
            if call in if_kw and not did_the_if:
                did_the_if = True
                if pace[1]:
                    return self.parse_calls(pace[2])

            elif call in if_kw and did_the_if:
                raise PairMismatch('Cannot call `if` 2 or more times within a cascade.')

            if not did_the_if:
                continue

            if call in elif_kw and not pace[1]:
                continue
            elif call in else_kw:
                return self.parse_calls(pace[1])

            elif call in elif_kw:
                return self.parse_calls(pace[2])

    def switch_statement(self, pathname: str, *args):
        semantics = self.lman.query_semantics((SWITCH_KEYWORD, CASE_KEYWORD, DEFAULT_KEYWORD))
        switch_kw, case_kw, default_kw = semantics[SWITCH_KEYWORD], semantics[CASE_KEYWORD], semantics[DEFAULT_KEYWORD]

        node = self.get(pathname)
        if is_node(node):
            value = node[RELATIVE_ATTRIBUTE]
        else:
            value = node

        lexed_cascade = lexer_cascade(args, self.get_debug(), recognized_blocks=switch_kw + case_kw + default_kw)

        for pace in lexed_cascade:
            call = pace[0]

            if call in case_kw and pace[1]:
                if value == pace[1]:
                    return self.parse_calls(pace[2])
                continue

            elif call in default_kw:
                return self.parse_calls(pace[1])

    @scoped("repeat")
    def repeat_statement(self, times: int | tuple[str, int], code):
        pathname = None
        callout = None
        iscounted = isinstance(times, tuple)

        if iscounted:
            pathname, times = times
            name = get_pathname_name(pathname)
            self.pack(name, construct_variable(name, 0))

        for i in range(times):
            if iscounted:
                self.set_rel(pathname, i)

            callout = self.parse_calls_direct(code)
            if isinstance(callout, AbstractInternal):
                if self.get_debug():
                    self.stdout(f'At `repeat` iteration {i} code {code}')

                if callout.type == 'BREAK':
                    break
                elif callout.type == 'CONTINUE':
                    continue

        return callout

    # BASIC
    def do_statement(self, code, *args):
        semantics = self.lman.query_semantics((WHILE_KEYWORD, REPEAT_KEYWORD))
        whilekw = semantics[WHILE_KEYWORD]
        repeatkw = semantics[REPEAT_KEYWORD]

        if args:
            assert len(args) == 2, "Expected while/repeat with one argument after the code."
            call = args[0]
            conditional_code = args[1]
            if call in whilekw:
                callout = self.parse_calls(code, scope_name="do-while")

                if isinstance(callout, AbstractInternal):
                    if callout.type == 'BREAK':
                        return

                return self.while_statement(conditional_code, code)

            elif call in repeatkw:
                callout = self.parse_calls(code, scope_name="do-repeat")

                if isinstance(callout, AbstractInternal):
                    if callout.type == 'BREAK':
                        return

                if conditional_code == 0:
                    return callout

                return self.repeat_statement(conditional_code, code)

            else:
                raise ParsingError(
                    f"Expected keyword {repr(whilekw)} or {repr(repeatkw)} in args '{', '.join(args)}'")

        return self.parse_calls(code, scope_name="do")

    @scoped("while")
    def while_statement(self, condition, code):
        call_buf = None

        while self.parse_calls_direct(condition):
            callout = self.parse_calls_direct(code)
            if isinstance(callout, AbstractInternal):
                if self.get_debug():
                    self.stdout(f'At `while` {code};{condition} => AB {callout.type}')

                if callout.type == 'BREAK':
                    break
                elif callout.type == 'CONTINUE':
                    continue

            call_buf = callout
        return call_buf

    def iter_build(self, pathname: str, iterable, code):
        if self.get_debug():
            self.stdout(f'[Parser] at iter {repr(pathname)} loop with iterable = {iterable} ==> {code} ')

        name = get_pathname_name(pathname)
        self.pack(name, construct_tree_conf(name, None))

        for it in iterable:
            self.set_rel(name, it)
            out = self.parse_calls_direct(code)
            yield out

    @scoped("iter")
    def iter_statement(self, pathname: str, iterable, code):
        return list(self.iter_build(pathname, iterable, code))

    @scoped("itert")
    def iter_tuple_statement(self, pathname: str, iterable, code):
        return tuple(self.iter_build(pathname, iterable, code))

    @scoped("iters")
    def iter_string_statement(self, pathname: str, iterable, code):
        return str().join(self.iter_build(pathname, iterable, code))

    def filter(self, pathname: str, iterable, condition_code: list[dict]):
        self.pack(get_pathname_name(pathname), construct_variable(pathname, None))
        for x in iterable:
            self.set_rel(pathname, x)
            if self.parse_calls_direct(condition_code):
                yield x

    def filter_string(self, pathname: str, string: str, condition_code: list[dict]):
        return ''.join(str(s) for s in self.filter(pathname, string, condition_code))

    @scoped('filter')
    def filter_statement(self, pathname: str, iterable, condition_code: list[dict]):
        type_ = type(iterable)
        if type_ is str:
            return self.filter_string(pathname, iterable, condition_code)
        return type_(self.filter(pathname, iterable, condition_code))

    def reduce_statement(self, node: dict[str, Any], iterable):
        return reduce(lambda x, y: self.exec(node, (x, y)), iterable)

    @scoped("multi_each")
    def multi_each(self, params: tuple[str], iterable, code):
        names = []
        for param in params:
            name = get_pathname_name(param)
            self.pack(name, construct_variable(name, None))
            names.append(name)

        call_buf = None

        for it in iterable:
            for i, ele in enumerate(it):
                self.set_rel(names[i], ele)

            callout = self.parse_calls_direct(code)
            if isinstance(callout, AbstractInternal):
                if callout.type == 'BREAK':
                    break
                elif callout.type == 'CONTINUE':
                    continue
                call_buf = callout

        return call_buf

    @scoped("each")
    def each_statement(self, pathname: tuple[str] | str, iterable, code):
        if self.get_debug():
            self.stdout(f'[Parser] at each `{pathname}` loop with iterable = {iterable} ==> {code} ')

        if isinstance(pathname, tuple):
            return self.multi_each(pathname, iterable, code)

        name = get_pathname_name(pathname)

        self.pack(name, construct_variable(name, None))

        call_buf = None
        for it in iterable:
            self.set_rel(name, it)

            callout = self.parse_calls_direct(code)
            if isinstance(callout, AbstractInternal):
                if self.get_debug():
                    self.stdout(f'At `each` {pathname} => AB {callout.type}')

                if callout.type == 'BREAK':
                    break
                elif callout.type == 'CONTINUE':
                    continue
            call_buf = callout

        return call_buf

    @scoped("for")
    def for_statement(self, start_code: list, condition, shorthand, code):
        debug_enabled = self.get_debug()
        start_code = transpose_call(start_code[0])
        # print(json.dumps(start_code, ensure_ascii=False, indent=4))
        if debug_enabled:
            self.stdout(
                f"[Parser] at for '{start_code}' loop with condition "
                f"'{condition}' shorthand '{shorthand}' ==> {code}")

        node = self.parse_call(start_code)  # get iterator node
        self.pack(node[NAME_ATTRIBUTE], node)

        call_buf = None

        while self.parse_calls_direct(condition):
            callout = self.parse_calls_direct(code)
            if isinstance(callout, AbstractInternal):
                if debug_enabled:
                    self.stdout(f'At `for` {condition};{shorthand} => AB {callout.type}')

                if callout.type == 'BREAK':
                    break
                elif callout.type == 'CONTINUE':
                    continue
            call_buf = callout
            self.parse_calls_direct(shorthand)

        return call_buf

    # ERROR HANDLING STATEMENTS
    @staticmethod
    def assert_statement(condition, error_message=""):
        assert condition, error_message

    def try_statement(self, *args):
        kw = self.lman.query_semantics((TRY_KEYWORD, CATCH_KEYWORD, FINALLY_KEYWORD))
        try_kw = kw[TRY_KEYWORD]
        catch_kw = kw[CATCH_KEYWORD]
        finally_kw = kw[FINALLY_KEYWORD]

        lexed_cascade = lexer_cascade(("try",) + args, self.get_debug(), try_kw + catch_kw + finally_kw)

        assert len(lexed_cascade) >= 2, "Try must come with a catch or finally"

        if self.get_debug():
            self.stdout(f'[TRY] Executing cascade {repr(lexed_cascade)}')

        try_block = lexed_cascade.pop(0)
        finally_block = None

        assert try_block[0] in try_kw, "First statement must be try"

        if len(lexed_cascade) >= 1:
            if lexed_cascade[-1][0] in FINALLY_KEYWORD:
                finally_block = lexed_cascade.pop()

        caught_something = False

        try:
            return self.parse_calls(try_block[1])
        except Exception as e:
            while len(lexed_cascade) > 0 and lexed_cascade[0][0] in catch_kw:
                catch_block = lexed_cascade.pop()
                exception_name = catch_block[1]
                exception_pathname = catch_block[2]
                code = catch_block[3]

                exception_node = construct_from_pyException(e)

                if exception_name == exception_node[NAME_ATTRIBUTE]:
                    caught_something = True
                    self.parse_calls(code, f'catch {exception_pathname}',
                                     refs={exception_pathname: construct_from_pyException(e)})

            if not caught_something:
                raise e
        finally:
            if finally_block is not None:
                self.parse_calls(finally_block[1])

    # TREE VISUALIZING / HELP

    def build_info(self, pathname: str = None, root: dict[str, Any] = None, mx=32, s="some"):

        listed = 0
        for k, v in root.items():
            if s == "some":
                if k.startswith('__') and not pathname:
                    continue

            icon = ''
            if is_node(v):
                if ICON_ATTRIBUTE in v:
                    icon = v[ICON_ATTRIBUTE]

            bullet = '*' if is_node(v) else '-'

            self.stdout(f"{bullet} {k} {icon}", end='')
            if is_node(v):
                class_ = v[CLASS_ATTRIBUTE]
                if class_ == ALIAS:
                    self.stdout(f" -> {repr(v[RELATIVE_ATTRIBUTE])}", end='')

            if not isinstance(v, dict) and pathname:
                self.stdout(f": {repr(v) if (len(str(v)) < mx or not mx) else f'{str(v)[:mx - 1]}...'}")
            elif pathname:
                self.stdout(':...')
            else:
                self.stdout()

            listed += 1
        return listed

    def info_list(self, view_list: list, pathname: str):
        self.stdout(f"On iterable at {pathname}: ")
        self.stdout('=' * 30)
        size_adjust = len(str(len(view_list))) + 1
        for index, ele in enumerate(view_list):
            self.stdout(f'{index}. '.ljust(size_adjust) + repr(ele))
        self.stdout('=' * 30)
        self.stdout(f'Listed {len(view_list)} elements.')

    def info(self, pathname: str = None, mx=32, s="some"):
        tree_path = self.get_root() if not pathname else self.get(pathname)

        if isinstance(tree_path, (tuple, list)):
            self.info_list(tree_path, pathname if pathname is not None else self[NAME_ATTRIBUTE])
            return

        self.stdout(f'On Tree at Parent: {tree_path["__name__"] if not pathname else pathname}')
        self.stdout('=' * 30)
        listed = self.build_info(pathname, root=tree_path, mx=mx, s=s)
        self.stdout('=' * 30)
        self.stdout(f"Listed {listed} elements.")

    def help_statement(self, pathname=None):
        if not pathname:
            return HELP

        self.stdout(self.get_docs(pathname))

    # ARITHMETIC

    @rel_modify
    def increment_builtin(self, rel, amount=1):
        return rel + amount

    @rel_modify
    def decrease_builtin(self, rel, amount=1):
        return rel - amount

    @rel_retrieve
    def ret_increment_builtin(self, rel, amount=1):
        return rel + amount

    @rel_retrieve
    def ret_decrease_builtin(self, rel, amount=1):
        return rel - amount

    def eval_builtin(self, *args, r=None):
        lexed_exp = self.opman.shunting_yard(args)
        result = self.opman.parse_sorted(lexed_exp)
        return result if not r else (round(result, r) if isinstance(r, int) else round(result, int(r)))

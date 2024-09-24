from LiON.lang.lexerconst import *
from LiON.lang.control import *
from LiON.lexer import full_lexer
from LiON.scope import *
from LiON.exceptions import *
import json
import copy
import uuid


# TODO: Add dman (debug manager)
#       - Logging
#       - Active debug
# TODO: Optimize the whole thing [~]

class TreeManager(Scope):
    def __init__(self, name=LANGUAGE):
        super().__init__(name)
        self.scope_stack = [construct_tree(name)]
        self.name = name
        self.stdout = print
        self.stderr = print
        self.stdin = input
        self.debug = None
        self.token_extrafunc = None

    def get_registry(self):
        return self.get_root()[REGISTRY_ROOT]

    def get_registry_domain(self, domain: str):
        try:
            return self.get_registry()[domain][RELATIVE_ATTRIBUTE]
        except KeyError:
            raise InvalidRegistryDomainError(f"Could not find registry domain {repr(domain)}")

    def query_registry(self, domain: str, key: str) -> dict[str, Any]:
        try:
            return self.get_registry_domain(domain)[key]
        except KeyError:
            raise InvalidRegistryError(f"Could not find key {repr(key)} in registry domain {repr(domain)}")

    def update_registry_domain(self, domain: str, dictionary: dict[str, Any]):
        self.get_registry_domain(domain).update(dictionary)

    def promote_to_registry(self, domain: str, key: str, node: dict[str, Any]):
        self.update_registry_domain(domain, {key: node})

    def promote(self, node: dict[str, Any], pathname=None):
        if not is_node(node):
            raise IsNotANode(f"Cannot promote a not node {repr(node)}")

        class_ = node[CLASS_ATTRIBUTE]
        success = False
        name = get_pathname_name(pathname) if pathname else node[NAME_ATTRIBUTE]

        for domain, binding in REGISTRY_CLASS_BINDING.items():
            if class_ in binding:
                self.promote_to_registry(domain, name, node)
                success = True

        if not success:
            raise UndefinedClassError(f"Node {repr(node[NAME_ATTRIBUTE])} have class {repr(class_)} "
                                      f"which is not promotable.")

    def promote_from_pathname(self, pathname: str):
        node = self.get(pathname)
        self.promote(node, pathname)

    def demote(self, domain: str, key: str):
        self.get_registry_domain(domain).pop(key)

    def get_class(self, node: dict[str, Any], operation: str = 'get') -> dict[str, Any]:
        assert is_node(node), IsNotANode('Cannot get class from a non-node')

        try:
            class_ = self.query_registry(REGISTRY_CLASSES, node.get(CLASS_ATTRIBUTE))

            return class_

        except InvalidRegistryError:
            raise UndefinedClassError(f"Cannot {operation} {repr(node.get(NAME_ATTRIBUTE))} with of undefined "
                                      f"class {repr(node.get(CLASS_ATTRIBUTE))}")

    def get_method(self, node: dict[str, Any], method_name: str, operation: str = 'get') -> dict[str, Any]:
        class_ = self.get_class(node)
        try:
            return class_[method_name]
        except KeyError:
            raise ClassWithoutMethod(f'Cannot {operation} {repr(node.get(NAME_ATTRIBUTE))} that is'
                                     f'without the {repr(method_name)} method.')

    def get_debug(self, debug=None) -> bool:
        return debug if debug is not None else self['debug'][RELATIVE_ATTRIBUTE]

    def set_out(self, value: Any):
        self.get_root()[OUT][RELATIVE_ATTRIBUTE] = value

    @staticmethod
    def new_from_def_constructor(relative, args, kwargs, restrictions=None) -> tuple[str, dict[str, Any]]:
        """
        :param relative:
        :param args:
        :param kwargs:
        :param restrictions:
        :return: The first argument always is the pathname, then, the node built
        """
        built = relative(*args, **kwargs, __rs__=restrictions)
        return args[0], built

    def new_from_constructor(self, constructor: dict[str, Any],
                             args, kwargs, restrictions=None) -> tuple[str, dict[str, Any]]:
        built: dict = self.exec_function(constructor, args, kwargs)
        if restrictions is not None:
            built.update({
                RESTRICTIONS_ATTRIBUTE: restrictions,
            })
        return args[0], built

    def new(self, constructor, args=None, kwargs: dict = None, restrictions=None) -> tuple[str, dict[str, Any]]:
        if not args:
            args = tuple()
        if not kwargs:
            kwargs = dict()

        class_ = constructor[CLASS_ATTRIBUTE]
        if class_ == DEFAULT_CONSTRUCTOR:
            pathname, built = self.new_from_def_constructor(constructor[RELATIVE_ATTRIBUTE], args, kwargs, restrictions)
        elif class_ == CONSTRUCTOR:
            pathname, built = self.new_from_constructor(constructor, args, kwargs, restrictions)
        elif class_ == CLASS:
            new_method = constructor.get(METHOD_MARKER + NEW_METHOD)
            if not new_method:
                raise ClassWithoutMethod(f"Tried using class {repr(constructor[NAME_ATTRIBUTE])} "
                                         f"as a constructor that's without a {repr(NEW_METHOD)} method")

            pathname, built = self.new_from_constructor(new_method, args, kwargs, restrictions)
        else:
            pathname, built = args[0] if len(args) != 0 else None, copy.deepcopy(constructor)

        if not constructor[NAME_ATTRIBUTE] == INHERITED:
            built.update({INSTANCEOF_ATTRIBUTE: constructor[NAME_ATTRIBUTE]})

        if self.get_debug():
            self.stdout(f'[PARSER at `new`] Built {repr(pathname)} with {repr(constructor[NAME_ATTRIBUTE])} => {built}')

        return pathname, built

    @staticmethod
    def throw_node(exception: dict[str, Any], message: str = None):
        if message is None:
            assert exception[RELATIVE_ATTRIBUTE] is not None, (f"You must provide a message "
                                                               f"to {repr(EXCEPTION[NAME_ATTRIBUTE])}")
            message = exception[RELATIVE_ATTRIBUTE]
        else:
            exception.update({RELATIVE_ATTRIBUTE: message})
        raise NodeThrownError(f'{repr(exception[NAME_ATTRIBUTE])} -> {message}', node=exception)

    def throw(self, exception_name, message: str = None):
        exception = copy.deepcopy(self.query_registry(REGISTRY_EXCEPTIONS, exception_name))
        return self.throw_node(exception, message)

    @staticmethod
    def get_bindings_for_function(node: dict[str, Any], args=None, kwargs: dict = None) -> dict:
        # TODO: Implement multi numbered bindings
        if not args:
            args = tuple()
        if not kwargs:
            kwargs = dict()

        args_given = (len(args) + len(kwargs))
        if args_given != len(node[ARGUMENTS_ATTRIBUTE]):
            raise ArgumentBindingMismatchError(f"Given {args_given}, missing"
                                               f" {len(node[ARGUMENTS_ATTRIBUTE]) - args_given} amount of "
                                               f"arguments to {repr(node[NAME_ATTRIBUTE])}")

        return dict(zip(node[ARGUMENTS_ATTRIBUTE], args)) | kwargs

    # PARSING FUNCTIONS

    @scoped("exec_function")
    def exec_function(self, node: dict[str, Any],
                      args=None, kwargs: dict = None):
        bindings = self.get_bindings_for_function(node, args, kwargs)

        # apply bindings to parameter relatives
        for k, v in bindings.items():
            node[k][RELATIVE_ATTRIBUTE] = bindings[k]

        if self.get_debug():
            self.stdout(f"[EXEC] Running function \033[38;2;255;0;0m{repr(node[NAME_ATTRIBUTE])}\033[0m"
                        f" at {self.__str__()}")

        self.add_refs_head(**{NAME_ATTRIBUTE: node[NAME_ATTRIBUTE], THIS: node},
                           **{k: node[k] for k in node[ARGUMENTS_ATTRIBUTE]})

        # execute code here
        return self.parse_calls_direct(node[RELATIVE_ATTRIBUTE])

    @scoped("exec_saber")
    def exec_saber(self, node: dict[str, Any],
                   args=(), kwargs: dict = None):
        if kwargs is None:
            kwargs = dict()
        self.add_refs_head(**{NAME_ATTRIBUTE: node[NAME_ATTRIBUTE], THIS: node,
                              ARGUMENTS_ATTRIBUTE: args, KWARGS_ATTRIBUTE: kwargs})
        return self.parse_calls_direct(node[RELATIVE_ATTRIBUTE])

    @scoped("exec_method")
    def exec_method(self, method_name: str,
                    node: dict[str, Any], args: tuple = (),
                    kwargs: dict = None, restrictions=None,
                    constructor=False, scope=None):
        try:
            class_ = self.query_registry(REGISTRY_CLASSES, node[CLASS_ATTRIBUTE])
            class_method = class_.get(METHOD_MARKER + method_name)
            if class_method is None:
                raise ClassWithoutMethod(
                    f"Method {repr(method_name)} was not found on class {repr(class_[NAME_ATTRIBUTE])} "
                    f"of node {repr(node[NAME_ATTRIBUTE])}")

            return self.scoped_exec(class_method, args, kwargs, restrictions, constructor, scope, refs={SELF: node})

        except InvalidRegistryError:
            raise UndefinedClassError(
                f"Cannot invoke method {repr(method_name)} on {repr(node.get(NAME_ATTRIBUTE))} node "
                f"of undefined "
                f"class {repr(node[CLASS_ATTRIBUTE])}.")

    def exec(self, node: dict[str, Any], args: tuple = (), kwargs: dict = None, restrictions=None,
             constructor=False, scope=None) -> Any:
        if not kwargs:
            kwargs = dict()

        if not is_node(node):
            return exec_variable_like(node, args)

        node_class, relative = node.get(CLASS_ATTRIBUTE), node.get(RELATIVE_ATTRIBUTE)
        assert isinstance(node_class, str), (f"Tried to exec node {repr(node[NAME_ATTRIBUTE])} "
                                             f"of invalid class {repr(node[CLASS_ATTRIBUTE])}")

        output = None
        if self.get_debug():
            self.stdout(f"[EXEC] Executing node with args {repr(args)} and kwargs {repr(kwargs)}")

        if node_class in {BUILTIN, STATEMENT}:
            additional_kwargs = {}
            if restrictions:
                additional_kwargs[RESTRICTIONS_ATTRIBUTE] = restrictions

            if scope:
                additional_kwargs[SCOPE_ATTRIBUTE] = scope

            output = relative(*args, **kwargs, **additional_kwargs)

        elif node_class in CONSTRUCTOR_LIKE:

            pathname, built = self.new(node, args, kwargs, restrictions)

            if constructor:
                output = built
            else:
                self.pack(pathname, built, __scope__=scope)
                output = None

        elif node_class == VERSION:
            output = f'{LANGUAGE} {node[FOR_ATTRIBUTE]} {node[TAG_ATTRIBUTE]} {relative}'

        elif node_class in VARIABLE_LIKE:
            output = exec_variable_like(relative, args)

        elif node_class == SABER:
            output = self.exec_saber(node, args, kwargs)
        elif node_class in FUNCTION_LIKE:
            output = self.exec_function(node, args, kwargs)
        elif node_class in METHOD:
            assert len(args) > 0, "Cannot execute method without passing at least a pathname"
            node_pathname = args[0]
            output = self.exec_method(node[NAME_ATTRIBUTE], self.get(node_pathname), args[1:], kwargs,
                                      restrictions, constructor, scope)

        elif node_class == ALIAS:
            output = self.call(relative, args, kwargs, restrictions, constructor)
        elif node_class == EXCEPTION:
            self.throw_node(node, *args)
        else:
            output = self.exec_method(EXEC_METHOD, node, args, kwargs, restrictions, constructor, scope)

        return output

    @scoped("scoped-exec")
    def scoped_exec(self, node: dict[str, Any], args: tuple = (), kwargs: dict = None, restrictions=None,
                    constructor=False, scope=None, refs: dict[str, Any] = None) -> Any:
        if refs is not None:
            self.get_head().update(refs)
        return self.exec(node, args, kwargs, restrictions, constructor=constructor, scope=scope)

    def call(self, pathname: str, args: tuple = (), kwargs=None, restrictions=None, constructor=False,
             debug: bool = None, scope=None):

        if self.get_debug(debug):
            self.stdout(f"[CALL] Calling node at pathname {repr(pathname)} with args {repr(args)}"
                        f" and kwargs {repr(kwargs)}")

        node = self.get(pathname)
        out = self.exec(node, args, kwargs, restrictions, constructor, scope=scope)

        if is_node(node):
            if ONLY in reparse_callpart(RESTRICTIONS_ATTRIBUTE, node, if_false=()):
                self.drop(pathname)

        return out

    # LEXER CONNECT FUNCTIONS
    def parse_token(self, token: tuple[str, Any], debug: bool = None):
        token_type = token[0]
        token_value = token[1]

        if debug:
            self.stdout(f"[PARSE_TOKEN] Parsing arg token {repr(token)}")

        if token_type == MASK_TYPE:
            return self.parse_call(token_value, debug)

        if token_type == LIST_MASK_TYPE:
            return list(self.parse_call(token_value, debug))

        if token_type in {TUPLE_TYPE, LIST_TYPE}:
            parsed = tuple(self.parse_token(k, debug) for k in token_value)
            if token_type == LIST_TYPE:
                return list(parsed)
            return parsed

        if token_type == KEY_VALUE_TYPE:
            return {k: self.parse_token(v, debug) for k, v in token_value.items()}

        if not self.token_extrafunc:
            return token_value
        return self.token_extrafunc(token)

    def parse_tokens(self, args, debug=None):
        for a in args:
            token_type, token_value = a
            if token_type == DISTRIBUTE_MASK:
                yield from self.parse_call(token_value, debug=debug)
            else:
                yield self.parse_token(a, debug=debug)

    def parse_call(self, call: dict[str, Any], debug: bool = None):
        if not call:
            return None

        pathname = call[LEXER_TYPE_PATHNAME]
        args = reparse_callpart(LEXER_TYPE_POSARGS, call)
        keywords = reparse_callpart(LEXER_TYPE_KEYWORDS, call, if_false=None)
        scope = reparse_callpart(LEXER_TYPE_SCOPE, call, if_false=None)
        implicit_args = reparse_callpart(LEXER_TYPE_IMPLICIT, call, dict())

        if debug:
            self.stdout(f"[PARSE_CALL] Parsing call to {repr(pathname)} with args"
                        f" {repr(args)} and kwargs {repr(implicit_args)}")

        def parse_token_dict(dictionary: dict[str, Any]) -> dict:
            return {ke: self.parse_token(va, debug) for ke, va in dictionary.items()}

        args = tuple(self.parse_tokens(args))
        if implicit_args:
            implicit_args = parse_token_dict(implicit_args)

        return self.call(pathname, args, implicit_args, restrictions=keywords, scope=scope)

    def parse_calls_direct(self, calls: list[dict[str, Any]], debug: bool = None):
        if not calls:
            return None

        debug = self.get_debug(debug)
        com_out = None
        # Parsing the code
        for index, call in enumerate(calls):
            call: dict[str, Any]  # call is a dict just so the ide gives delicious syntax highlighting
            if not call:
                continue

            pathname = call[LEXER_TYPE_PATHNAME]
            if pathname in AB_CALLS:
                return AB_CALLS[pathname]
            com_out = self.parse_call(call, debug)
            if isinstance(com_out, AbstractInternal):
                break

            elif com_out is not None:
                self.set_out(com_out)

            if debug:
                self.stdout(
                    f"[PARSECALLS] after calling '{pathname}' args {pathname} => "
                    f"{repr(com_out)} '{com_out.__class__.__name__}'")

        return com_out

    def parse_calls(self, calls: list[dict[str, Any]], scope_name: str = None,
                    refs: dict[str, Any] = None,
                    debug: bool = None):
        try:
            self.add_scope(scope_name if scope_name is not None else uuid.uuid4().hex,
                           refs if refs is not None else {}, debug)
            out = self.parse_calls_direct(calls, debug)
            return out
        finally:
            self.release()

    def parsefunc(self, code: str, debug: bool = None, cent_size=30):
        debug = self.get_debug(debug)

        # Lexing the code first
        if debug:
            self.stdout(f'{"-" * cent_size}[* \033[92mLEXER\033[0m *]{"-" * cent_size}')
        calls = full_lexer(code, debug)
        if debug:
            self.stdout('-=' * 30)
            self.stdout(json.dumps(calls, indent=4))
            self.stdout('-=' * 30)
            self.stdout(f'{"-" * cent_size}[* \033[92mPARSER\033[0m *]{"-" * cent_size}')
        return self.parse_calls_direct(calls, debug)

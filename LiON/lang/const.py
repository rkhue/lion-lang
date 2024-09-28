from typing import Literal

LANGUAGE = "LiON"
FILE_EXTENSIONS = ('.lion', '.leonid', ".lions")

# Node classes
NEWABLE = "newable"
BUILTIN = "builtin"
DEF_STATEMENT = "def_statement"
STATEMENT = "statement"
METHOD = "method"
INHERITED = "inherited"
TASK = "task"
CLASS = "class"

# Locale-like
LOCALE = "locale"

# System like
TREE_CONFIG = "tree_conf"
REGISTRY = "registry"
SYSTEM_LIKE = {TREE_CONFIG, REGISTRY}


# Variable like
VARIABLE = "variable"
PARAMETER = "parameter"
SCOPE = "scope"
DMS = "dms"

VARIABLE_LIKE = {VARIABLE, PARAMETER, SCOPE, TREE_CONFIG, DMS, REGISTRY}


# Function like
FUNCTION = "function"
LAMBDA = "lambda"
SABER = "saber"
OVERLOAD = "overload"
FUNCTION_LIKE = {FUNCTION, LAMBDA}


# Constructor like
DEFAULT_CONSTRUCTOR = "def_constructor"
ANONYMOUS_CONSTRUCTOR = "anon_constructor"
CONSTRUCTOR = "constructor"
CONSTRUCTOR_LIKE = {DEFAULT_CONSTRUCTOR, ANONYMOUS_CONSTRUCTOR, CONSTRUCTOR, CLASS}

# Operator like
DEFAULT_OPERATOR = "def_operator"
OPERATOR = "operator"
OPERATOR_LIKE = {DEFAULT_OPERATOR, OPERATOR}

# Alias like
ALIAS = "alias"

# Exception like
EXCEPTION = "exception"

# Status like
VERSION = "version"

BUILTIN_LIKE = {BUILTIN, DEFAULT_CONSTRUCTOR, DEFAULT_OPERATOR, STATEMENT}

NODE_CLASSES = Literal[
    "newable", "tree_conf", "stack", "registry", "exception",
    "def_constructor", "constructor", "alias", "version", "locale",
    "dms", "scope", "overload", "anon_constructor",
    "builtin", "variable", "parameter", "function", "method", "lambda", "saber"
]

PATHNAME_DELIMITER = '.'


NAME_ATTRIBUTE = "__name__"
CLASS_ATTRIBUTE = "__class__"
RELATIVE_ATTRIBUTE = "__rel__"
RESTRICTIONS_ATTRIBUTE = "__rs__"
TAG_ATTRIBUTE = "__tag__"
ICON_ATTRIBUTE = "__icon__"
DOCUMENTATION_ATTRIBUTE = "__doc__"
NOTICE_ATTRIBUTE = "__notice__"
INSTANCEOF_ATTRIBUTE = "__instanceof__"
SELF_ATTRIBUTE = "__self__"

ESSENTIAL_ATTRIBUTES = (NAME_ATTRIBUTE, CLASS_ATTRIBUTE, RELATIVE_ATTRIBUTE)

FOR_ATTRIBUTE = "__for__"
ARGUMENTS_ATTRIBUTE = "__args__"
KWARGS_ATTRIBUTE = "__kwargs__"
SEMANTIC_ATTRIBUTE = "__semantic__"
SCOPE_ATTRIBUTE = "__scope__"

TYPE_ATTRIBUTE = "type"
PRECEDENCE_ATTRIBUTE = "proc"
LAMBDA_ATTRIBUTE = "lam"
TOGGLE_ATTRIBUTE = "toggle"
DELAY_ATTRIBUTE = "delay"

CONTEXT_ROOT = "__ctx__"

METHOD_MARKER = "%"
NEW_METHOD = "new"
EXEC_METHOD = "exec"

REGISTRY_ROOT = "reg"
REGISTRY_OPERATOR = "op"
REGISTRY_CLASSES = "classes"
REGISTRY_TASK = "task"
REGISTRY_EXCEPTIONS = "except"
REGISTRY_LOCALES = "locale"
REGISTRY_SEMANTICS = "semantic"
REGISTRY_PERMISSIONS = "perm"
REGISTRY_DMS = "dms"

THIS = "this"
SELF = "self"

REGISTRY_CLASS_BINDING = {
    REGISTRY_OPERATOR: OPERATOR_LIKE,
    REGISTRY_LOCALES: {LOCALE},
    REGISTRY_TASK: {TASK},
    REGISTRY_EXCEPTIONS: {EXCEPTION},
    REGISTRY_DMS: {DMS},
    REGISTRY_CLASSES: {CLASS}
}

VERSION_ROOT = "version"

OUT = "out"
DEBUG = "debug"
THROW_ERRORS = "throw_err"
SECURE = "secure"

EXPRESSION_MARKER = "$"

EXCLUDE_FROM_LOCALES = {
    REGISTRY_ROOT, CONTEXT_ROOT, THROW_ERRORS,
    OUT, DEBUG, SECURE, EXPRESSION_MARKER
}


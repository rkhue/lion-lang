from LiON.lang.restrictions import *

REGEX_COMMENT_PATTERN = r'(#.*)|(\/\*)+?[\w\W]+?(\*\/)+'
REGEX_NUMERIC_PATTERN = r'(\d+(\.\d+)?|\.\d+)[f%]?'
REGEX_FUNCTION_MASK_PATTERN = r'^(?P<pathname>[\w\.]+)\[(?P<posargs>(.|\s)*)\]'
REGEX_LAMBDA_EXPRESSION = r'^\((?P<posargs>[^\)]*)\)=>\{(?P<code>(\s|.)*)\}$'

RECOGNIZED_BRACKET_PAIRS = {
    "{": "}",
    "[": "]",
    "(": ")",
}
BRACKETS = "{}[]()"
RECOGNIZED_OPEN_BRACKET_PAIRS = set(RECOGNIZED_BRACKET_PAIRS.keys())
RECOGNIZED_CLOSING_BRACKET_PAIRS = set(RECOGNIZED_BRACKET_PAIRS.values())

INLINE_COMMENT = "#"
MULTILINE_COMMENT = ("/*", "*/")


GLOBAL = 'global'
LOCAL = 'local'
NONLOCAL = 'nonlocal'
DEFAULT = 'default'

SCOPE_KEYWORDS = (GLOBAL, LOCAL, NONLOCAL, DEFAULT)
DEFAULT_PERMISSIONS = DEFAULT_RESTRICTIONS + SCOPE_KEYWORDS


IMPLICIT_MARKER = '->'
INSERT_MARKER = '<-'
LITERAL_MARKER = "?"
LOCAL_IMPLICIT_MARKER = '-'
TOKENIZER_DELIMITER = " "
CALLS_DELIMITERS = (';', '\n')
STRING_MARKER = '"'

COLLECTIONS_DELIMITER = ','
DICT_DELIMITER = ':'
GET_PATHNAME_MARKER = "::"
ELLIPSIS_MARKER = "..."

EXPRESSION_MARKER = "$"

STRING_TYPE = "str"
STRING_UNKNOWN = "unk"
DMS_DIRECTORY_TYPE = "dms"
FLOAT_TYPE = "float"
INT_TYPE = "int"
BOOLEAN_TYPE = "bool"
NONE_TYPE = "none"

CODEBLOCK_TYPE = "code"
MASK_TYPE = "mask"
ELLIPSIS_TYPE = "ellipsis"
TUPLE_TYPE = "tuple"
LIST_TYPE = "list"
LIST_MASK_TYPE = "list-mask"
KEY_VALUE_TYPE = "key-value"
DISTRIBUTE_MASK = "dist-mask"
LAMBDA_EXPRESSION = "lam-exp"

LEXER_TYPE_KEYWORDS = "kw"
LEXER_TYPE_PATHNAME = "pathname"
LEXER_TYPE_POSARGS = "posargs"
LEXER_TYPE_IMPLICIT = "implicit"
LEXER_TYPE_INSERTING = "inserting"
LEXER_TYPE_SCOPE = "scope"

PASSING_TOKENS = (STRING_TYPE, FLOAT_TYPE, INT_TYPE, BOOLEAN_TYPE,
                  TUPLE_TYPE, LIST_TYPE, KEY_VALUE_TYPE)

BOOL_KEYWORDS = {
    "on": True,
    "off": False,
    "true": True,
    "false": False,
}

NONE_KEYWORDS = {
    "none", "null", "nil"
}

FLIPPING_MAP = {
    True: False,
    False: True,
    0: 1,
    1: 0,
    "0": "1",
    "1": "0"
}


class LiONString(str):
    pass

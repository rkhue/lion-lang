from LiON.lang.const import *
from LiON.lang.lexerconst import *
from LiON.exceptions import *
from typing import Iterable, Any
import re


# FIX EMPTY KEYS ON KEY-VALUE TYPE

def match_delimiter(text: str, delimiter=':') -> bool:
    """
    Checks if a given string is delimited by a given delimiter
    :param text: Text to be checked
    :param delimiter: character
    :return: boolean
    """
    opened_brackets = []
    opened_strings = 0

    for char in text:
        if not opened_brackets and not opened_strings:
            if char == delimiter:
                return True

        if char in RECOGNIZED_BRACKET_PAIRS:
            opened_brackets.append(char)

        elif char in RECOGNIZED_CLOSING_BRACKET_PAIRS and opened_brackets:
            if char == RECOGNIZED_BRACKET_PAIRS[opened_brackets[-1]]:
                opened_brackets.pop()

        elif char == '"':
            opened_strings += 1 if not opened_strings else -1

    return False


def lex_indexed_collection(text: str, debug=False) -> Iterable[tuple[str, Any]]:
    return (lexer_condemner(t.strip(), debug) for t in lexer_tokenizer(text, debug, COLLECTIONS_DELIMITER))


def lex_list(text: str, debug=False) -> list:
    """
    Gets a text delimited by a comma and returns a list with its values condemned and tokenized.
    :param text: Input text
    :param debug: Debugging options
    :return: list
    """
    return list(lex_indexed_collection(text, debug))


def lex_tuple(text: str, debug=False) -> tuple:
    """
    Gets a text delimited by a comma and returns a tuple with its values condemned and tokenized.
    :param text: Input text
    :param debug: Debugging options
    :return: tuple
    """
    return tuple(lex_indexed_collection(text, debug))


def lexer_cascade(cascade_blocks, debug=False,
                  recognized_blocks: tuple[str] | list[str] = ('if', 'elif', 'else')
                  ) -> list[tuple[Any, ...] | list[Any]]:
    cascade = []
    current_block = []

    for item in cascade_blocks:
        if item in recognized_blocks:
            if current_block:
                cascade.append(tuple(current_block))
                current_block.clear()

        current_block.append(item)

    if current_block:
        cascade.append(current_block)

    if debug:
        print(f'[LEXER at `lexer_cascade`] : cascade = {cascade}')

    return cascade


def lexer_key_value(text: str, debug=False) -> dict:
    """
    Gets an input text and transforms into a dictionary/key-value pair
    :param text: Input text
    :param debug: debugging options
    :return: Lexed key-value
    """
    pairs = {}
    opened_brackets = []
    opened_string = False

    pair_name = ""
    current_token = ""
    for i, char in enumerate(text):

        if debug:
            print(f'[KEY-VALUE] at char {i}: {char} | {" ".join(opened_brackets)} | {opened_string} | {current_token}'
                  f' | {pair_name} | {pairs}')

        if char == DICT_DELIMITER and not opened_brackets and not opened_string:
            pair_name = current_token.strip()
            current_token = ""
            continue

        if not opened_string:
            if char in RECOGNIZED_BRACKET_PAIRS:
                opened_brackets.append(char)

            elif opened_brackets:
                if char == RECOGNIZED_BRACKET_PAIRS[opened_brackets[-1]]:
                    opened_brackets.pop()

        if char == COLLECTIONS_DELIMITER and not (opened_brackets or opened_string):
            pairs.update({str(pair_name): current_token.strip()})
            pair_name = ""
            current_token = ""
            continue

        if char == '"':
            opened_string = True if not opened_string else False

        current_token += char
    if current_token:
        pairs.update({pair_name: current_token.strip()})

    return {k: lexer_condemner(v, debug, at='KEY-VALUE') for k, v in pairs.items() if k.strip()}


def remove_comments(text: str) -> str:
    """
    Removes comments based on the const REGEX_COMMENT_PATTERN.
    * Inline -> #
    * Multiline -> /* */
    :param text: Given text
    :return: Clean text
    """
    return re.sub(REGEX_COMMENT_PATTERN, ' ', text)


def lexer_delimiter(code: str, debug=False, depth=0) -> list[str]:
    """
    Divides the string by ; or newlines, returns recursively tokenized calls
    :param code: Code string
    :param debug: Debugging option
    :param depth: Lexer depth
    :return:
    """
    if not code.strip():
        return []

    calls = []
    current_call = []
    opened_brackets = []

    linenum = 0

    last_line_open_bracket = None
    last_char_open_bracket = None

    semicolon_delimiter = False

    opened_string = False
    comment = {
        "multiline": None,
        "inline": False,
    }

    if debug:
        print(f'\033[1;32m[DELIMITER ({depth})] Delimiting chars ({len(code)}) ...\033[0m')

    skip = 0
    for i, char in enumerate(code):

        if debug:
            print(f'[DELIMITER] at char {i} '
                  f'{repr(char)}{f" line {linenum} "}'
                  f'{"| " + (" > ".join(opened_brackets)) if opened_brackets else ""} '
                  f'| str {opened_string}'
                  + (f' |\033[91m semicolon \033[0m' if semicolon_delimiter else '') +
                  f' | at callsize {len(current_call)}'.rjust(10))

        if skip:
            skip -= 1
            continue

        if char == '\n':
            linenum += 1
            if semicolon_delimiter:
                semicolon_delimiter = False
                continue

            if comment['inline']:
                comment['inline'] = False

        if not opened_string:
            if char == INLINE_COMMENT:
                comment['inline'] = True

            elif len(code[i:]) >= 1:
                if char == '/' and code[i + 1] == '*':
                    comment['multiline'] = True
                    continue
                elif char == '*' and code[i + 1] == '/':
                    comment['multiline'] = False
                    skip += 1
                    continue

        if comment['multiline'] or comment['inline']:
            continue

        if not opened_brackets and not opened_string and char in CALLS_DELIMITERS:
            # Tokenize them lines
            if current_call:
                string_call = ''.join(current_call)
                if string_call:
                    calls.append(string_call)
                current_call.clear()
                semicolon_delimiter = char == ';'
            continue

        # Ignore strings or brackets at splitting

        if char == '"':
            opened_string = True if not opened_string else False
            last_line_open_bracket = int(linenum)
            last_char_open_bracket = int(i)

        if not opened_string:
            if char in RECOGNIZED_BRACKET_PAIRS:
                opened_brackets.append(char)
                last_line_open_bracket = int(linenum)
                last_char_open_bracket = int(i)

            elif char in RECOGNIZED_BRACKET_PAIRS.values():
                match = RECOGNIZED_BRACKET_PAIRS[opened_brackets[-1]]
                if len(opened_brackets) == 0:
                    raise BracketMismatch(f'[DELIMITER ({depth}) at call {repr("".join(current_call))} char {i}]'
                                          f' Did not open any brackets before closing with "{char}"')
                if match == char:
                    opened_brackets.pop()
                else:
                    raise BracketMismatch(f"[DELIMITER ({depth}) at {repr(''.join(current_call))} char {i}]"
                                          f" Expected closing bracket {repr(match)} "
                                          f"for {repr(opened_brackets[-1])} instead got {repr(char)}")

        current_call.append(char)

    if current_call:
        string_call = ''.join(current_call)
        if string_call:
            calls.append(string_call)

    if opened_brackets:
        raise BracketNeverClosed(f'[DELIMITER] Opened a bracket at line {last_line_open_bracket}'
                                 f' char {last_char_open_bracket}, never closed it')
    if opened_string:
        raise StringNeverClosed(f'[DELIMITER] Opened a string at line {last_line_open_bracket}'
                                f' char {last_char_open_bracket}, never closed it')

    return [c for c in calls if c.strip() != '']


def lexer_tokenizer(call: str, lexer_debug=False, delimiter=" ") -> list[str]:
    """
    Divides a call by its tokens using spaces by default as an argument delimiter
    :param call: Given call as text
    :param lexer_debug: Debugging options
    :param delimiter: Character for delimiting
    :return: Tokenized call
    """
    call = call.lstrip().strip()
    tokens = []
    opened_brackets = []
    opened_string = False

    current_token = ""
    for char in call:
        if char == delimiter and not opened_brackets and not opened_string:
            if current_token:
                tokens.append(current_token)
            current_token = ""
            continue

        if not opened_string:
            if char in RECOGNIZED_BRACKET_PAIRS:
                opened_brackets.append(char)

            elif opened_brackets:
                if char == RECOGNIZED_BRACKET_PAIRS[opened_brackets[-1]]:
                    opened_brackets.pop()

        if char == '"':
            opened_string = True if not opened_string else False

        current_token += char

    if current_token:
        tokens.append(current_token)

    if lexer_debug:
        print(f"[LEXER] At `tokenize_command`: tokens = {tokens} | delimiter ({delimiter}) |")
    return tokens


def build_call(keywords: list[str], pathname: str, posargs: list = None,
               implicit: dict = None, inserting: dict = None, scope: str = None, kwargs: dict = None):
    base = {
        LEXER_TYPE_PATHNAME: pathname,
    }
    base.update({k: v for k, v in ((LEXER_TYPE_KEYWORDS, keywords),
                                   (LEXER_TYPE_POSARGS, posargs), (LEXER_TYPE_IMPLICIT, implicit),
                                   (LEXER_TYPE_INSERTING, inserting), (LEXER_TYPE_SCOPE, scope)) if v})

    if kwargs is not None:
        base.update(kwargs)
    return base


def lexer_parenthesis(token: str, debug=False, expects: Literal["tuple", "dict"] = None):
    if match_delimiter(token, DICT_DELIMITER):
        if expects == "tuple":
            raise LexingError(f'[LEX_PR Error with {repr(token)}] Expected {expects} and got "dict"')
        return KEY_VALUE_TYPE, lexer_key_value(token, debug)

    if expects == "dict":
        raise LexingError(f'[LEX_PR Error with {repr(token)}] Expected {expects} and got "tuple"')

    return TUPLE_TYPE, lex_tuple(token, debug)


def lexer_get_pathname(token: str, debug=False, get_name='get'):
    if debug:
        print(f'[CONDEMNER at get_pathname] Transforming {repr(token)}')

    stripped_token = token.replace(GET_PATHNAME_MARKER, PATHNAME_DELIMITER).lstrip('.')
    return MASK_TYPE, build_call(
        keywords=[], pathname=get_name,
        posargs=[(STRING_UNKNOWN, stripped_token)])


def lexer_string(token: str):
    return token.encode(
    ).decode('unicode-escape').encode('latin1').decode('utf-8')


def lexer_mask(token: str, returns=MASK_TYPE, debug: bool = False) -> tuple[str, Any]:
    if len(token.strip()) == 0:
        raise EmptyMask(f"[Lexer at CONDEMNER] Usage of empty masks is forbidden, given token {repr(token)}")
    return returns, full_lexer(token, debug, del_comments=False)[-1]  # parse masks


def lexer_condemner(token: str, debug=False, expects=None,
                    remove_string_marker=True, at=None) -> tuple[str, Any]:
    """
    Condemns a token to its type, in other words, does type-matching
    :param token: Given token
    :param debug: Debugging options
    :param expects: Expects a type, if not found raises an error [NOTICE: It only works for 'tuple' and 'dict' for now]
    :param remove_string_marker: Remove quotes from strings, default to true
    :param at: Where is the condemner running, defaults to None
    :return: Condemned token
    """
    cropped_token = token[1:-1]
    if debug:
        print(f'[CONDEMNER{f" at {repr(at)}" if at else ""}] at TOKEN '
              f'{repr(token)}{f" expecting {repr(expects)}" if expects else ""}')

    # arrays
    if token.startswith('&(') and token.endswith(')'):
        return LIST_TYPE, lex_list(cropped_token[1:], debug)

    # codeblocks and masks
    if token.startswith('{') and token.endswith('}'):
        return CODEBLOCK_TYPE, full_lexer(cropped_token, debug, del_comments=False)

    if token.startswith('[') and token.endswith(']'):
        return lexer_mask(cropped_token)

    elif token.startswith('&[') and token.endswith(']'):
        return lexer_mask(cropped_token[1:], returns=LIST_MASK_TYPE, debug=debug)

    elif token.startswith('|[') and token.endswith(']'):
        return lexer_mask(cropped_token[1:], returns=DISTRIBUTE_MASK, debug=debug)

    if token.startswith(LITERAL_MARKER) and len(token) > 1:
        # if len(token) <= 1:
        #     raise EmptyMask(f"[Lexer at CONDEMNER] Usage of empty literals is forbidden, given token {repr(token)} "
        #                     f"in case of only using `?`, please enclose it into a string.")

        return MASK_TYPE, full_lexer(token[1:], debug, del_comments=False)[-1]

    # tuples or dicts
    if token.startswith('(') and token.endswith(')'):
        return lexer_parenthesis(cropped_token, debug, expects=expects)

    # strings
    if token.endswith('"'):
        if token.startswith('d"'):
            return DMS_DIRECTORY_TYPE, cropped_token[1:] if remove_string_marker else token
        elif token.startswith('r"'):
            return STRING_TYPE, cropped_token[1:] if remove_string_marker else token
        elif token.startswith('"'):
            return STRING_TYPE, lexer_string(cropped_token) if remove_string_marker else token

    # numbers
    if token.replace('.', '').replace('f', '').replace('%', '').replace('-', '').isnumeric():
        if token.endswith('f'):
            return FLOAT_TYPE, float(token[:-1])
        elif token.endswith('%'):
            return FLOAT_TYPE, float(token[:-1]) / 100
        elif '.' in token:
            return FLOAT_TYPE, float(token)
        return INT_TYPE, int(token)

    # boolean or null
    if token in BOOL_KEYWORDS:
        return BOOLEAN_TYPE, BOOL_KEYWORDS[token.lower()]
    # doesn't know
    if GET_PATHNAME_MARKER in token:
        return lexer_get_pathname(token, debug)

    return STRING_UNKNOWN, token


def get_value(token: tuple[str, Any]) -> Any:
    return token[1]


def handle_marker(call, marker, marker_dict, marker_name, debug=False, at=None, expects=None):
    """
    Helper function to lexer_categorize. It handles marker logic of a given marker and call.
    :param call: Call to be handled
    :param marker: Marker symbol
    :param marker_dict: Dictionary to store condemned results
    :param marker_name: Name of the marker
    :param debug: Debugging options
    :param at: where
    :param expects: Same as lexer_condemner expects
    :return: call
    """
    if call and call[0] == marker:
        if len(call) < 2:
            raise LexingError(f'[LEXER] at [CATEGORIZE{f" at {repr(at)}" if at else ""}] '
                              f'Error categorizing call {repr(call)}'
                              f': Did not parse any key-value pairs after'
                              f' using the {repr(marker)} {repr(marker_name)}')

        marker_dict.update(get_value(lexer_condemner(call[1], debug=debug, expects=expects)))
        call = call[2:]
    return call


def lexer_categorize(call: list[str], debug=False, at=None, kwargs=None) -> dict[str, Any]:
    """
    Lexer categorize returns a list of nested calls based on a certain tokenized call.
    :param call: Call given
    :param debug: Debugging options
    :param at: Where "categorize" is running
    :param kwargs: Extra call arguments
    :return: categorized call
    """
    if not call:
        raise LexingError(f'[LEXER] at [CATEGORIZE NORMAL{f" at {repr(at)}" if at else ""}] '
                          f'cannot categorize empty call.')

    keywords = []
    posargs = []
    implicit = {}
    inserting = {}
    scope = None

    full_call = list(call)

    while True:
        if call:
            if call[0] not in DEFAULT_PERMISSIONS:
                break
            k = call.pop(0)

            if k in SCOPE_KEYWORDS:
                # check if scope is already defined
                if scope is not None:
                    raise LexingError(f'[LEXER at CATEGORIZE{f" at {repr(at)}" if at else ""}] Call scope {repr(scope)}'
                                      f' conflicted with {repr(k)}')
                scope = k
            else:
                keywords.append(k)
        else:
            raise LexingError(f'[LEXER at CATEGORIZE{f" at {repr(at)}" if at else ""}] Incomplete call'
                              f' {repr(full_call)}, please use a pathname after giving keywords')

    pathname = call.pop(0)
    condemned = lexer_condemner(pathname, debug=debug, at=at)

    if condemned[0] != STRING_UNKNOWN:
        pathname = EXPRESSION_MARKER
        posargs.append(condemned)

    i = 0
    while call and call[0] not in {INSERT_MARKER, IMPLICIT_MARKER}:
        token = call.pop(0)

        arg = lexer_condemner(token, debug)
        posargs.append(arg)
        i += 1

    if len(posargs) == 1 and pathname == EXPRESSION_MARKER:
        pathname = 'return'

    # Handle implicit and inserting markers
    call = handle_marker(call, INSERT_MARKER, inserting, "insert marker", debug, at, expects='dict')
    handle_marker(call, IMPLICIT_MARKER, implicit, "implicit marker", debug, at)

    return build_call(keywords, pathname, posargs, implicit, inserting, scope, kwargs=kwargs)


def lexer_pre_parser(calls: list[str], debug=False):
    """
    The pre-parser lexer gets a list of calls, tokenizes and returns a nested list of categorized calls.
    :param calls: Calls to be pre-parsed
    :param debug: Debugging options
    :return: pre-parsed calls
    """
    tokenized = [lexer_tokenizer(c, debug) for c in calls]
    return [lexer_categorize(c, debug) for c in tokenized]


def full_lexer(text: str, debug=False, del_comments=True) -> list[dict]:
    """
    The full lexer of LiON gets code represented as text and "compiles" it, so it is understandable by the parser.
    Also, it is of function of the lexer to type arguments and handle syntax errors.
    :param text: Code given
    :param debug: Lexer debugging options
    :param del_comments: Delete comments option, if on, it removes recognized comments
    :return: Lexed code
    """
    calls = lexer_delimiter(text, debug=debug)

    return lexer_pre_parser(calls, debug)


def transpose_call(call: dict[str, Any], head='new'):
    """
    Joker's method, used for transpose calls.
    Changes the pathname to a given 'head' and makes the old to be the first argument.
    :param call: Call to be transposed.
    :param head: New pathname, default is `new`
    :return: transposed call.
    """
    pn = call.pop('pathname')
    call['posargs'] = [lexer_condemner(pn)] + call['posargs']
    call['pathname'] = head
    return call

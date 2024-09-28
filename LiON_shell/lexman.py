from pygments.lexer import RegexLexer
from pygments.token import *
from LiON.lang.lexerconst import *


class LiONLexer(RegexLexer):
    name = 'LiON'
    aliases = ['lion', 'lions']
    filenames = ['*.lion', '*.lions']

    tokens = {
        'root': [
            (REGEX_COMMENT_PATTERN, Comment),
            (r"\/\*.*", Comment),
            (r'"', String.Double, 'string'),
            (r'\@\w+', String),
            (r'\?\w+', Token.Literal),
            (r'\!\w+', Generic.Strong),
            (r'\b(help|lion|import|get|pop|drop|pack|export|new|call|exec|conf|'
             r'flip|restrict|move|rename|promote'
             r'|demote|if|elif|else|switch|case|default|do|while|repeat|from|'
             r'each|iter|itert|iters|for|assert|throw|try'
             r'|catch|finally|push|extend|break|continue'
             r'|set|keysfrom|filter|return|cascade|protect|final|method'
             r'|only|global|local|nonlocal)\b', Keyword),
            (r'\b(node|struct|class|overload'
             r'|inherited|var|alias|function|saber'
             r'|lam|operator|constructor|string|tuple|list'
             r'|keyvalue|exception)\b',
             Keyword),
            (r'\b(true|false|on|off|null|nil|none)\b', Name.Builtin),
            (r'\(', Punctuation),
            (r'\)', Punctuation),
            (r'\{', Punctuation),
            (r'\}', Punctuation),
            (r'\[', Punctuation),
            (r'\]', Punctuation),
            (r'\|', Punctuation),
            (r'\:|\,', Keyword),
            (r'\;|\.', Punctuation),
            (REGEX_NUMERIC_PATTERN, Number),
            # Operators
            (r'\!', Operator),
            (r'(>|<|=|<=|>=|!=|==|is)', Operator),
            (r'[+\-*/%~^]{1,2}|->|\$|&', Operator),
            (r'\b(C|U|!U|in|left|right)\b', Operator),
            (r'\b(and|or|xor|not|oc|of)\b', Operator),
            (r'\b(scale|downscale)\b', Operator),
            (r'[a-zA-Z_]\w*', Name),
            (r'\s+', Text),
        ],
        'string': [
            (r'\\.', String.Escape),  # Escape sequences
            (r'"', String.Double, '#pop'),  # End of string
            (r'[^"\\]+', String.Double),  # Regular characters
        ]
    }

    def update_words(self, wordlist: list[str]):
        self.tokens['root'][2] = r'\b(' + "|".join(wordlist) + r')\b'

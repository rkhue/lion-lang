from LiON.lang.const import *

NODE_CLASSES_COLORS_LIST = {
    True: (0, 189, 0),
    False: (189, 0, 0),
    None: (128, 128, 128),
    NEWABLE: (84, 128, 255),
    FUNCTION: (255, 189, 0),
    SABER: (235, 103, 52),
    METHOD: (234, 71, 255),
    BUILTIN: (255, 255, 255),
    VARIABLE: (0, 255, 255),
    ALIAS: (255, 0, 189),
    REGISTRY: (189, 189, 189),
    DEFAULT_OPERATOR: (255, 255, 255),
    DEFAULT_CONSTRUCTOR: (255, 70, 137),
    ANONYMOUS_CONSTRUCTOR: (255, 70, 137),
    CLASS: (255, 64, 0),
    OPERATOR: (255, 189, 0),
    LOCALE: (189, 255, 81),
    CONSTRUCTOR: (255, 70, 137),
    STATEMENT: (255, 70, 137),
    VERSION: (12, 239, 89),
    EXCEPTION: (255, 70, 0),
}

NODE_CLASSES_EMOJI_LIST = {
    NEWABLE: "📦",
    VARIABLE: "🏷️",
    FUNCTION: "⚡",
    SABER: "🥷",
    LAMBDA: "🥸",
    METHOD: "🪄",
    BUILTIN: "🔧",
    ALIAS: "🔗",
    LOCALE: "🗺️",
    REGISTRY: "📚",
    STATEMENT: "🔖",
    ANONYMOUS_CONSTRUCTOR: "🥸",
    DEFAULT_CONSTRUCTOR: "🧩",
    OPERATOR: "🔢",
    DEFAULT_OPERATOR: "🔢",
    CONSTRUCTOR: "🔨",
    CLASS: "📜",
    VERSION: "📖",
    EXCEPTION: "🛑"
}

CLASS_ABBREVIATIONS = {
    NEWABLE: "new",
    VARIABLE: "var",
    METHOD: "mtd",
    FUNCTION: "fun",
    LAMBDA: "lam",
    SABER: "sbr",
    BUILTIN: "bui",
    ALIAS: "als",
    TREE_CONFIG: "cfg",
    LOCALE: "loc",
    REGISTRY: "reg",
    STATEMENT: "smt",
    DEFAULT_CONSTRUCTOR: "dcs",
    DEFAULT_OPERATOR: "dop",
    CLASS: "cls",
    OPERATOR: "ope",
    CONSTRUCTOR: "cst",
    VERSION: "ver",
    EXCEPTION: "exc",
}

BOOLEAN_MAPPINGS = {
    True: "✅",
    False: "❌",
    None: "⛔",
}

COLSIM_COLORS = ((191, 252, 249), (211, 0, 0), (255, 243, 250))
ALIAS_MARKER = "*"
BROKEN_ALIAS_MARKER = '!'

ATTRIBUTE_EMOJI = "📄"
TREE_CONFIG_EMOJI = "⚙️"

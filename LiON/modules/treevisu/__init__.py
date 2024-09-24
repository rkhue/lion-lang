from LiON.lion_node import *
from LiON.funclib import newColored
from LiON.modules.treevisu.theme import *
import inspect

GRAY = (81, 81, 81)
GREEN = (0, 189, 0)


def has_children(node: dict):
    for k, v in node.items():
        if is_node(v):
            return True
    return False


def get_emoji_icon(node: dict):
    if not node.get(ICON_ATTRIBUTE):
        em = NODE_CLASSES_EMOJI_LIST.get(node[CLASS_ATTRIBUTE])
        return em if em is not None else ATTRIBUTE_EMOJI

    return node[ICON_ATTRIBUTE]


def get_color_attr(value: Any):
    if isinstance(value, bool) or value is None:
        return NODE_CLASSES_COLORS_LIST[value]

    return GREEN


def get_emoji_color(node: dict | tuple[str, Any]):
    if is_node(node):
        class_ = node[CLASS_ATTRIBUTE]
        emoji_from_class = get_emoji_icon(node)

        if has_children(node) and class_ not in {NEWABLE, FUNCTION, METHOD, OPERATOR, LANGUAGE, CLASS}:
            return emoji_from_class, NODE_CLASSES_COLORS_LIST[NEWABLE]
        elif class_ in NODE_CLASSES_COLORS_LIST:
            return emoji_from_class, NODE_CLASSES_COLORS_LIST[class_]
        elif class_ == TREE_CONFIG:
            rel = node.get(RELATIVE_ATTRIBUTE)
            if isinstance(rel, bool) or rel is None:
                return BOOLEAN_MAPPINGS[rel], get_color_attr(rel)
            return TREE_CONFIG_EMOJI, GRAY
        else:
            return emoji_from_class, GRAY

    _, value = node
    return ATTRIBUTE_EMOJI, get_color_attr(value)


def print_node(node: dict, abbreviations=True):
    emoji, color = get_emoji_color(node)
    if is_node(node):
        class_ = node[CLASS_ATTRIBUTE]
        abb = CLASS_ABBREVIATIONS.get(class_) if class_ in CLASS_ABBREVIATIONS else class_[:3]
        return (f'{emoji}'
                f'{(newColored(color, abb) + ": ") if abbreviations else ""}{node[NAME_ATTRIBUTE]}'
                f'{newColored(GREEN, ALIAS_MARKER) if class_ == ALIAS else ""}')

    name, value = node
    return f'{emoji} {newColored(color, name)}'


def build_info_tree(tree: dict, max_depth: int = 1, start=True, indent=1):
    if max_depth == 0:
        return
    if start:
        print(f'{print_node(tree)}')
        if has_children(tree):
            print(f"{newColored(GRAY, '::')} ")

    spacing = (indent * f"{newColored(GRAY, '::')} ")
    for key, value in tree.items():
        if key.startswith("__") or not is_node(value):
            continue

        print(f'{spacing}{print_node(value)}')
        print(f'{spacing}{newColored(GRAY, "::")}')
        if is_node(value):
            build_info_tree(tree[key], max_depth - 1, False, indent=indent + 1)


def analyze_node(node: dict, abbreviations=True):
    imprint = print_node(node, abbreviations)

    class_ = node[CLASS_ATTRIBUTE]
    rel = node[RELATIVE_ATTRIBUTE]
    name = node[NAME_ATTRIBUTE]
    doc = node.get(DOCUMENTATION_ATTRIBUTE)
    rel_type = type(rel) if rel is not None else None
    protections = node.get(RESTRICTIONS_ATTRIBUTE)
    signature = None
    docstring = None

    if class_ in BUILTIN_LIKE:
        signature = inspect.signature(rel)
        docstring = rel.__doc__
        rel = None
        rel_type = None

    elif class_ in FUNCTION_LIKE:
        signature = node[ARGUMENTS_ATTRIBUTE]
        rel = None
        rel_type = None

    return {
        "name": name,
        "imprint": imprint,
        "class": class_,
        "rel_type": rel_type,
        "signature": signature,
        RELATIVE_ATTRIBUTE: rel,
        RESTRICTIONS_ATTRIBUTE: protections,
        "doc": doc,
        "docstring": docstring
    }

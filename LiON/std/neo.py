from LiON.modules.neo.style import NeoStyleSheet
from typing import Any

global parent_parser, construct_builtin, construct_node, funclib

stylesheet = NeoStyleSheet()


def load_stylesheet(filename: str):
    stylesheet.load_styles(funclib.loadRaw(filename))


def dump_stylesheet(filename: str):
    if '.' not in filename:
        filename += '.neo'

    funclib.write_file(filename, stylesheet.decompile())


def add_style(style: dict[str, Any]):
    stylesheet.add(style["__name__"], style["__rel__"])


def aquarela(style_selector, *args, end='\n', sep=' '):
    parent_parser.stdout(stylesheet.parse(style_selector, ' '.join([str(s) for s in args])), end=end, sep=sep)


neo = construct_builtin("neo", stylesheet.parse)
neo.update({
    "add": construct_builtin("add", add_style),
    "load": construct_builtin("load", load_stylesheet),
    "dump": construct_builtin("dump", dump_stylesheet),
    "styles": construct_builtin("styles", stylesheet.get_styles),
    "embedded": construct_builtin("embedded", stylesheet.get_embed),
    "cache": construct_builtin("cache", stylesheet.get_cache) | {
        "clear": construct_builtin("clear", stylesheet.cache.clear)
    },
})

parent_parser.assign_references({
    "neo": neo,
    "aquarela": construct_builtin("aquarela", aquarela),
})

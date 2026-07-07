import os
from LiON.modules.neo.const import *
from LiON.funclib import loadRaw
from typing import Any
import yaml

MODULE_DIR = os.path.dirname(__file__)

properties = yaml.load(loadRaw(MODULE_DIR + "/properties.yml"), yaml.FullLoader)


def compile_style_block(style: dict[str, Any]) -> str:
    blocks = []

    for k, v in style.items():
        mapping = ANSI_PARAMS.get(k)
        if isinstance(v, bool) and v:
            blocks.append(mapping)
        elif k in SPECIAL_COLOR_NAMES:
            blocks.append(mapping.format(*v))

    return ";".join(filter(None, blocks))


def compile_style(style: dict[str, Any]) -> str:
    return f"\033[{compile_style_block(style)}m{{}}\033[0m"


def hex_to_rgb(hex: str) -> tuple[int, ...]:
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))


class StyleException(Exception):
    pass


class NeoStyleSheet:
    def __init__(self, stream: str = None, embed: dict[str, Any] = properties) -> None:
        self.stylesheet: dict[str, Any] = dict()
        self.cache: dict[str, str] = dict()
        self.embed: dict[str, Any] = embed if embed is not None else dict()
        if stream:
            self.load_styles(stream)

    def get_styles(self):
        return self.stylesheet

    def decompile(self) -> str:
        return yaml.dump(self.stylesheet)

    def add(self, style_name: str, style: dict[str, Any]):
        if style_name in self.cache:  # Cache invalidation
            self.cache.pop(style_name)

        self.stylesheet.update({style_name: style})

    def load_styles(self, stream: str):
        self.stylesheet.update(yaml.load(stream, yaml.FullLoader))

    def use_style(self, style: str) -> str:
        ansi_style = self.cache.get(style)
        if not ansi_style:
            raw_style = self.stylesheet.get(style)
            if not raw_style:
                raise ValueError(f"Neo style {repr(style)} not defined")

            ansi_style = compile_style(raw_style)
            self.cache.update({style: ansi_style})
        return ansi_style

    def get_cache(self):
        return self.cache

    def get_embed(self):
        return self.embed

    def parse_text(self, styles: tuple[str], text) -> str:
        for style in styles:
            text = self.use_style(style).format(text)
        return text

    def parse(self, style_selector, text) -> str:
        styles: tuple[str] = style_selector.split('+')

        cache_buf = {}
        for style in styles:
            new_style = None

            if style.startswith('#'):
                new_style = {style: compile_style({"color": hex_to_rgb(style)})}
            elif style.startswith('&'):
                name = style[1:]

                if not self.embed.get(name):
                    raise StyleException(f"No embed defined for '{style}'")

                new_style = {style: compile_style({"color": self.embed.get(name)})}

            if new_style:
                if style not in self.cache:
                    cache_buf.update(new_style)

        self.cache.update(cache_buf)

        return self.parse_text(styles, text)

    def __str__(self):
        return self.decompile()

    def __repr__(self):
        return self.stylesheet.__repr__()

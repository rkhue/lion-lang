from LiON.parser import TreeManager
from LiON.lion_node import construct_alias, construct_node, construct_builtin
from LiON.funclib import openJson
from LiON.lang.const import *
from typing import Any


class LanguageManager:
    def __init__(self, tree: TreeManager):
        self.tree = tree

    def get_basic(self):
        lang = construct_builtin("lang", self.add_language)
        lang.update({
            "add": construct_builtin("add", self.add_language),
            "setup": construct_builtin("setup", self.setup_language),
            "remove": construct_builtin("remove", self.remove_language),
            "get": construct_builtin("get", self.get_language),
            "query_semantics": construct_builtin("query_semantics", self.query_semantics)
        })
        return {"lang": lang}

    def get_language_registry(self) -> dict[str, Any]:
        return self.tree.get_registry_domain(REGISTRY_LOCALES)

    def get_language(self, name: str):
        return self.tree.query_registry(REGISTRY_LOCALES, name)

    def match_semantic(self, semantic: str):
        for language in self.get_language_registry():
            language: dict[str, Any]
            if semantic in language[SEMANTIC_ATTRIBUTE]:
                return language[SEMANTIC_ATTRIBUTE][semantic]

    def query_semantics(self, semantics: tuple) -> dict[str, list[str]]:
        listing: dict[str, list[str]] = {s: [] for s in semantics}
        for lid, language in self.get_language_registry().items():
            language: dict[str, Any]
            for s in semantics:
                if s in language[SEMANTIC_ATTRIBUTE]:
                    listing[s].append(language[SEMANTIC_ATTRIBUTE][s])

        return listing

    def add_language(self, language_name: str):
        self.create_language_aliases(self.get_language(language_name))

    def setup_language(self, filename: str):
        assert hasattr(self.tree, "dms"), "[LANG] DMS not found in TreeManager"
        node = openJson(self.tree.dms.parse(filename))
        self.tree.pack(node[NAME_ATTRIBUTE], node)
        self.tree.promote_to_registry(REGISTRY_LOCALES, node[NAME_ATTRIBUTE], node)
        self.create_language_aliases(node)

    def remove_language(self, language_name: str):
        self.remove_language_aliases(self.get_language(language_name))
        self.tree.demote(LOCALE, language_name)

    def create_language_aliases(self, language: dict[str, Any]):
        for alias, points in language[ARGUMENTS_ATTRIBUTE].items():
            if alias == points:
                continue
            self.tree.pack(alias, construct_alias(alias, points, __tag__=language[NAME_ATTRIBUTE]))

    def remove_language_aliases(self, language: dict[str, Any]):
        for pathname in language[ARGUMENTS_ATTRIBUTE]:
            self.tree.drop(pathname)


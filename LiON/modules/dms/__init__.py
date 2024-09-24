"""
LiON Directory management system
LiON-DMS

Deal with files, directory names etc
"""
import os.path
from os import getcwd, chdir
from pathlib import Path
from LiON.exceptions import InformalDMSRegistryError
from LiON.parser import TreeManager
from LiON.funclib import getFilesFromDir
from LiON.lion_node import *

# TODO: Add loadRaw / openJSON / loadTXT here


def normalize_directory(directory: str):
    directory = directory.replace(r"\"", "/")
    return directory.replace('//', '/')


class LionDMS:
    def __init__(self, tree: TreeManager, home: str, module_home: str, dms_identifier='@'):
        self.name = 'DMS'
        self.identifier = dms_identifier
        self.tree = tree
        storage = {
            "%": construct_dms("%", module_home),  # LiON module home
            "~": construct_dms("~", home),  # Where LiON is running
            f"{dms_identifier}u": construct_dms(f"{dms_identifier}u", str(Path.home())),  # user home
            f"{dms_identifier}std": construct_dms(f"f{dms_identifier}std", module_home + "/std/"),
            f"{dms_identifier}scripts": construct_dms(f"f{dms_identifier}scripts", module_home + "/scripts/"),
            f"{dms_identifier}samples": construct_dms(f"{dms_identifier}samples", module_home + "/scripts/samples/"),
            f"{dms_identifier}assets": construct_dms(f"f{dms_identifier}assets", module_home + "/assets/"),
            f"{dms_identifier}conf": construct_dms(f"f{dms_identifier}conf", module_home + "/assets/conf/"),
            f"{dms_identifier}icon": construct_dms(f"f{dms_identifier}icon", module_home + "/assets/icon/"),
            f"{dms_identifier}doc": construct_dms(f"f{dms_identifier}doc", module_home + "/assets/doc/"),
            f"{dms_identifier}locale": construct_dms(f"f{dms_identifier}conf", module_home + "/assets/locale/"),
        }

        self.tree.update_registry_domain(REGISTRY_DMS, storage)

    def get_basic(self):
        dms = construct_builtin("dms", self.parse, __tag__=REGISTRY_DMS)
        dms.update({
            "assign": construct_builtin("assign", self.assign_symbol, __tag__=REGISTRY_DMS),
            "make": construct_builtin("make", self.make_dms),
            "symbol": construct_builtin("symbol", self.get_symbol),
            "set_home": construct_builtin("set_home", self.set_home),
            "listdir": construct_builtin("listdir", self.list_dir),
        })
        return {
            "dms": dms,
            "cwd": construct_builtin("cwd", os.getcwd, __tag__=REGISTRY_DMS),
            "cd": construct_builtin("cd", self.change_dir, __tag__=REGISTRY_DMS),
        }

    def get_storage(self):
        return self.tree.get_registry_domain(REGISTRY_DMS)

    def get_symbol(self, symbol: str):
        return self.tree.query_registry(REGISTRY_DMS, symbol)[RELATIVE_ATTRIBUTE]

    def get_cwd(self):
        return self.make_dms(getcwd())

    def is_valid_symbol(self, symbol: str):
        return symbol.startswith(self.identifier)

    def set_home(self, directory: str):
        if not os.path.isdir(directory):
            raise FileNotFoundError(f'[{self.name}] Cannot assign home {repr("~")} symbol to directory '
                                    f'{repr(directory)} '
                                    f'because it does not exist')
        self.assign_symbol('~', directory)

    def assign_symbol(self, symbol: str, value: str):
        if not self.is_valid_symbol(symbol):
            raise InformalDMSRegistryError(f'[{self.name}] Cannot assign invalid symbol {repr(symbol)}, '
                                           f'please use an identifier {repr(self.identifier)} before the symbol.')
        value = self.parse(normalize_directory(value))
        if not os.path.isdir(value):
            raise FileNotFoundError(f'[{self.name}] Cannot assign symbol {repr(symbol)} to directory {repr(value)}'
                                    f' because it does not exist.')

        self.tree.get_root()[REGISTRY_ROOT][REGISTRY_DMS][RELATIVE_ATTRIBUTE].update({symbol: construct_dms(symbol, value)})

    def change_dir(self, directory: str):
        directory = self.parse(directory)
        chdir(directory)

    def parse(self, directory: str):
        """
        Converts a DMS directory to a normal system directory
        :param directory:
        :return:
        """
        directory = normalize_directory(directory)
        for k in self.get_storage():
            ksize = len(k)
            if directory.startswith(k):
                return self.get_symbol(k) + directory[ksize:]

        return directory

    def make_dms(self, directory: str):
        directory = normalize_directory(directory)
        for k, v in self.get_storage().items():
            if v[RELATIVE_ATTRIBUTE] in directory:
                return directory.replace(v[RELATIVE_ATTRIBUTE], k)

        return directory

    def list_dir(self, directory: str = '.', extension=None):
        return getFilesFromDir(self.parse(directory), extension=extension)

from LiON.lexer import full_lexer_json
from LiON.modules.treevisu import *
from LiON.funclib import *
from copy import deepcopy
from timeit import timeit
from LiON.basic import *
import subprocess
import threading
import datetime
import tqdm


class LiONStandard(LiONBasic):
    def __init__(self, cargo: dict[str, Any] = None):
        if not cargo:
            cargo = {}

        super().__init__(cargo={
            "standard": self.get_standard
        } | cargo)
        self.backup_root = deepcopy(self.get_root())
        self.stdout = print

    # HELPER METHODS
    def print_finished(self, prompt: str):
        self.stdout(newColored((0, 255, 0), f"[{self.get_name()}] Finished: {repr(prompt)}"))

    def get_standard(self):
        return {
            # RESET REPAIR
            "reset": construct_builtin("reset", self.reset_builtin),
            "repair": construct_builtin("repair", self.repair_builtin),
            "lex": construct_builtin("lex", self.lexer_builtin, __icon__="✒️"),
            "lxj": construct_builtin("lxj", lambda code: full_lexer_json(code, debug=self.get_debug()), __icon__="✒️"),

            # TREE VISUALIZING
            "info": construct_builtin('info', self.info, __icon__="ℹ️"),
            "colsim": construct_builtin("colsim", self.colsim, __icon__='📋'),
            "tree": construct_builtin('tree', self.tree_builtin, __icon__="🌲"),
            "linos": construct_builtin('linos', self.list_nodes_builtin, __icon__="🌲"),
            "anl": construct_builtin("anl", self.analyze_node_builtin, __icon__="🩺"),

            # CONSOLE
            "clear": construct_builtin('clear', clear, __icon__="🧹"),

            # PRINTING
            "echo": construct_builtin("echo", self.stdout, __icon__="🖨️"),
            "recho": construct_builtin("recho", self.recho_builtin, __icon__="📐"),
            "quote": construct_builtin("quote", self.quote_builtin, __icon__="💬"),
            "printf": construct_builtin("printf", self.printf_builtin, __icon__="🖨️"),
            "see": construct_builtin("see", self.see, __icon__="🔎"),

            # MATH RELATED
            "equals": construct_builtin('equals', self.equals_builtin, __icon__="🟰"),
            "merge": construct_builtin('merge', self.merge_builtin, __icon__="➕"),
            'len': construct_builtin('len', len, __icon__="📏"),
            "maxi": construct_builtin('maxi', lambda x: len(x) - 1, __icon__="📏"),
            'range': construct_builtin('range', range, __icon__="🔢"),

            # TIME
            "current": construct_builtin('current', self.current_builtin, __icon__="📅"),
            'timeit': construct_builtin('timeit', self.timeit_builtin, __icon__="⌚"),
            "timeout": construct_builtin('timeout', self.timeout_builtin, __icon__="⌛"),

            # MODULES
            "input": self.get_input_module(),
            "sh": self.get_sh_module(),
            "cast": self.get_cast_module(),
        }

    # LiON Jump
    def lexer_builtin(self, code):
        return full_lexer(code, debug=self.get_debug())

    # RESET / REPAIR TREE
    def reset(self):
        before = int(len(self.get_root()))

        self.stdout(f'[Reset] Resetting... ({len(self.get_root())})')
        self.get_root().clear()
        self.scope_stack[0] = self.backup_root.copy()
        self.setup()

        diff = before - len(self.get_root())

        symbol = '--' if diff > 0 else "++"
        self.stdout(f'[Reset] Done. ({len(self.get_root())}){f" ({symbol}{abs(diff)})" if diff != 0 else ""}')

    def reset_builtin(self, f=False, w=True):
        if not f:
            if w:
                self.stdout(f'[WARN] Resetting the whole tree deletes and re-setups all nodes.'
                            f' [Changes are IRREVERSIBLE!]')
            if not funclib.askForYorN(f'[WARN] Do you want to reset '
                                      f'{repr(self.get_name())}? '):
                return

            self.reset()
            return

        self.reset()

    def repair_node(self, pathname: str, comparison: dict[str, Any] = None, silent=False):
        node = self.get(pathname)
        comparison_module = construct_node(get_pathname_name(pathname)) if not comparison else comparison

        if not silent:
            self.stdout(f'[Repair] Analyzing {repr(pathname)} {len(node)}x{len(comparison_module)}')
        to_repair = {}
        for k, v in comparison_module.items():
            if k not in node:
                to_repair.update({k: v})

        if not silent:
            self.stdout(f'[Repair] Found {len(to_repair)} missing attributes, re-adding '
                        f'into {repr(pathname)}')

        node.update(to_repair)
        return len(to_repair) > 0

    def repair_builtin(self, pathname=None):
        if pathname:
            self.repair_node(pathname)
        else:
            built = self.get_basic()
            to_repair = {}
            repaired_nodes = 0
            self.stdout(f'[Repair] Analyzing {repr(self.get_name())} {len(self.get_root())}x{len(built)}')
            for k, v in tqdm.tqdm(built.items()):
                if k not in self.get_root():
                    to_repair.update({k: v})
                    continue
                repaired_nodes += int(self.repair_node(k, built[k] if k in built else None, silent=True))

            if not to_repair and not repaired_nodes:
                self.stdout(f'[Repair] All fine in {repr(self.get_name())}.')
                return

            if to_repair:
                self.stdout(f'[Repair] Found {len(to_repair)} missing nodes, re-adding '
                            f'into {repr(self.get_name())}')

                self.get_name().update(to_repair)

            if repaired_nodes:
                self.stdout(f'[Repair] Found {repaired_nodes} 2 nodes with missing attributes, re-created them.')

        self.stdout(f'[{self.name}] Fixed.')

    # TREE VISUALIZING

    def tree_builtin(self, pathname: str = None, depth=1, **kwargs):
        tree_path = self.get_root() if not pathname else self.get(pathname,
                                                                  __scope__=get_from_dict(SCOPE_ATTRIBUTE, kwargs))
        build_info_tree(tree_path, depth, **kwargs)

    def list_nodes_builtin(self, pathname=None, node: dict[str, Any] = None, ln=6, sp=2,
                           s="some", r=False, __scope__=None):
        if node is not None:
            assert pathname is None, "[LINOS] Cannot provide a node and a pathname to linos in the same call."
            tree_path = node
        else:
            tree_path = self.get_root() if not pathname else self.get(pathname, __scope__=__scope__)

        if not r:
            self.stdout(f'On Tree at Parent: {repr(tree_path[NAME_ATTRIBUTE] if not pathname else pathname)}')

        tree_path = {name: n for (name, n) in tree_path.items() if
                     not (name.startswith('__') and ((not pathname) and not node) and (s == "some"))}
        if r:
            return len(tree_path)

        node_amount = len([a for a in tree_path.values() if is_node(a)])
        attribute_amount = len(tree_path) - node_amount
        self.stdout(f"""Nodes: {node_amount} | Attributes: {attribute_amount} | Total: {len(tree_path)}
    """)
        max_spacing = len(max(tree_path.keys(), key=len)) + sp

        for i, (name, n) in enumerate(tree_path.items()):
            emoji, color = get_emoji_color(n if is_node(n) else (name, n))
            self.stdout(newColored(color, f'{emoji} {name}'.ljust(max_spacing + (len(emoji) - 1))), end=' ')
            if (i + 1) % ln == 0:
                self.stdout()
        self.stdout()

    def analyze_node_builtin(self, pathname: str, s=False, __scope__=None):
        node = self.get(pathname, __scope__=__scope__)
        if not is_node(node):
            raise ParsingError(f'Cannot analyze {repr(pathname)}, expected it to be an node not an attribute')
        analysis = analyze_node(node)

        class_ = node.get(CLASS_ATTRIBUTE)

        emoji, color = get_emoji_color(node)
        rel_type = analysis.pop('rel_type')

        self.stdout(f"{analysis.pop('imprint')}"
                    f" -> {newColored(color, f'{class_} ')}{f': {rel_type}' if rel_type else ''}")
        if not s:
            self.stdout("=" * 30)
            for k, v in analysis.items():
                if v is not None:
                    self.stdout(f"* {k}: {v}")

            self.stdout("=" * 30)

    def colsim(self, pathname: str = None, mx=5, s="some"):
        root = self.get_root() if not pathname else self.get(pathname)

        sz_elements = len(root)

        for i, k in enumerate(root.keys()):
            end = " " if not (i + 1) % mx == 0 and i < sz_elements - 1 else '\n'
            _, color = get_emoji_color(root[k] if is_node(root[k]) else (k, root[k]))
            self.stdout(newColored(color, k), end=end)

        self.stdout()

    # MODULES

    def get_input_module(self):
        inp = construct_builtin('input', self.stdin, __icon__='🔤')

        inp.update({
            "yn": construct_builtin("yn", lambda prompt: funclib.askForYorN(prompt, self.stdin)),
            "int": construct_builtin("int", lambda a, b, prompt: funclib.askForIntBetween(a, b, prompt, self.stdin)),
            "float": construct_builtin("float",
                                       lambda a, b, prompt: funclib.askForFloatBetween(a, b, prompt, self.stdin))
        })
        return inp

    @staticmethod
    def get_cast_module():
        cast = construct_node("cast")
        cast.update({
            "str": construct_builtin("str", lambda t: str(t)),
            "arr": construct_builtin("arr", lambda t: list(t)),
            "tuple": construct_builtin("tuple", lambda t: tuple(t)),
            "int": construct_builtin("int", lambda t: int(t)),
            "float": construct_builtin("float", lambda t: float(t)),
            "perc": construct_builtin(
                "perc",
                lambda t: (float(str(t).replace("%", "")) / 100) if not isinstance(t, int | float) else float(t) / 100),
            "bool": construct_builtin("bool", lambda t: bool(t)),
            "bin": construct_builtin("bin", bin),
            "oct": construct_builtin("oct", oct),
            "octperm": construct_builtin("perm", lambda perm: LINUX_PERM_OCT[perm]),
            "permoct": construct_builtin("permoct", lambda octal: LINUX_OCT_PERMISSION[octal])
        })
        return cast

    def get_sh_module(self):
        sh = construct_builtin("sh", lambda *comargs: os.system(" ".join(str(x) for x in comargs)))
        sh.update({
            "linux_permoct": LINUX_PERM_OCT,
            "linux_octperm": LINUX_OCT_PERMISSION,
            "doit": construct_builtin("doit", self.sh_doit)
        })
        return sh

    def sh_doit(self, *args, pn=None, __scope__=None):
        com = [str(x) for x in args]
        process = subprocess.Popen(com)
        self.stdout(f'[{self.name}] Started subprocess at PID {repr(str(process.pid))}')

        if pn:
            process_module = construct_node(pn)
            process_module.update({
                "args": process.args,
                "pid": process.pid,
                "stdout": process.stdout,
                "stdin": process.stdin,
                "stderr": process.stderr,
                "wait": construct_builtin("wait", process.wait),
                "signal": construct_builtin("signal", process.send_signal),
                "kill": construct_builtin("kill", lambda: (
                    process.kill(),
                    self.drop(pn)
                )),
                "__doc__": f"Process module {repr(pn)} at pid {process.pid}"
            })
            self.pack(pn, process_module, __scope__=__scope__)
            self.stdout(f'[{self.name}] Added new module {repr(pn)} for process management.')

    # STDOUT RELATED
    def printf_builtin(self, string: str = "", *args, end='\n'):
        self.stdout(str(string).format(*args), end=end)

    def recho_builtin(self, *args, end='\n', sep=' '):
        self.stdout(*[repr(a) for a in args], end=end, sep=sep)

    def quote_builtin(self, *args, end='\n', sep=' ', author=None):
        self.stdout('"', end='')
        self.stdout(" ".join([str(a) for a in args]), end='', sep=sep)
        self.stdout('"', end=end if not author else '')
        if isinstance(author, bool) and author:
            self.stdout(f' — {self.get_name()}', end=end)
        elif author:
            self.stdout(f' — {author}', end=end)

    def see(self, filename: str):
        self.stdout(loadRaw(self.dms.parse(filename)))

    # EXTRA STUFF

    # MATH RELATED
    @staticmethod
    def equals_builtin(a, b):
        return str(a) == str(b)

    @staticmethod
    def merge_builtin(a, b):
        return a + b

    # TIME AND SECONDS
    @scoped("timeit")
    def timeit_builtin(self, seconds, code):
        def do_work():
            self.parse_calls_direct(code)

        return timeit(do_work, number=int(seconds)) / int(seconds)

    def timeout_builtin(self, *args):
        delay = 5
        if isinstance(args[0], int | float):
            delay = args[0]
            code = args[1]
        else:
            code = args[0]

        timer = threading.Timer(delay, function=lambda: self.parse_calls(code))
        timer.start()

    @staticmethod
    def current_builtin(unit: str):
        today = datetime.datetime.now()
        match unit:
            case 'time':
                return today
            case 'second':
                return today.second
            case 'minute':
                return today.minute
            case 'hour':
                return today.hour
            case 'date':
                return today.date()
            case 'day':
                return today.day
            case 'weekday':
                return today.weekday()
            case 'month':
                return today.month
            case 'year':
                return today.year
            case _:
                raise ParsingError(f'[DATE] cannot resolve date unit {repr(unit)}, '
                                   f'please consider using `time`, `hour`, `minute`, `second`'
                                   f'`date`, `day`, `weekday`,'
                                   f' `month` or `year`')

import subprocess
import os

global parent_parser, construct_builtin, funclib, construct_node


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
    self.stdout(funclib.loadRaw(self.dms.parse(filename)))


def get_input_module():
    inp = construct_builtin('input', parent_parser.stdin, __icon__='🔤')
    inp.update({
        "yn": construct_builtin("yn", lambda prompt: funclib.askForYorN(prompt, parent_parser.stdin)),
        "int": construct_builtin("int", lambda a, b, prompt: funclib.askForIntBetween(a, b, prompt, parent_parser.stdin)),
        "float": construct_builtin("float",
                                   lambda a, b, prompt: funclib.askForFloatBetween(a, b, prompt, parent_parser.stdin))
    })
    return inp


def get_sh_module():
    sh = construct_builtin("sh", lambda *comargs: os.system(" ".join(str(x) for x in comargs)))
    sh.update({
        "linux_permoct": funclib.LINUX_PERM_OCT,
        "linux_octperm": funclib.LINUX_OCT_PERMISSION,
        "doit": construct_builtin("doit", sh_doit)
    })
    return sh


def sh_doit(*args, pn=None, __scope__=None):
    com = [str(x) for x in args]
    process = subprocess.Popen(com)
    parent_parser.stdout(f'[{parent_parser.get_name()}] Started subprocess at PID {repr(str(process.pid))}')
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
                parent_parser.drop(pn)
            )),
            "__doc__": f"Process module {repr(pn)} at pid {process.pid}"
        })
        parent_parser.pack(pn, process_module, __scope__=__scope__)
        parent_parser.stdout(f'[{parent_parser.get_name()}] Added new module {repr(pn)} for process management.')


parent_parser.assign_references({
    "echo": construct_builtin("echo", parent_parser.stdout, __icon__="🖨️"),
    "recho": construct_builtin("recho", recho_builtin, __icon__="📐"),
    "quote": construct_builtin("quote", quote_builtin, __icon__="💬"),
    "printf": construct_builtin("printf", printf_builtin, __icon__="🖨️"),
    "clear": construct_builtin('clear', funclib.clear, __icon__="🧹"),
    "see": construct_builtin("see", see, __icon__="🔎"),
    "input": get_input_module(),
    "sh": get_sh_module(),
})

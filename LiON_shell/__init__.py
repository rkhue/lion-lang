from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style, merge_styles
from prompt_toolkit.patch_stdout import patch_stdout
from pygments.formatters import Terminal256Formatter
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.formatted_text import HTML
from pygments.styles import get_style_by_name
from pygments.lexers import get_lexer_by_name
from prompt_toolkit.output import ColorDepth
from prompt_toolkit import PromptSession
from LiON_shell.lexman import LiONLexer
from LiON.shell import format_out, is_brackets_balanced, count_brackets
from pygments import highlight
from os.path import dirname
import pygments.util
from LiON import *
import traceback

DMS_COLOR = (0, 255, 255)
DEBUG_COLOR = (0, 255, 0)
NOT_SECURE_COLOR = (255, 0, 0)
TYPE_COLOR = (189, 189, 255)
NODE_COLOR = (255, 189, 0)

LION_SHELL_MODULE_DIR = dirname(__file__)

mode = 'lion'

Message_Style = Style.from_dict({
    # User input (default text).
    'pound': '#00FF00 bold',
    'host': '#00ffff bg:#444400',
    'directory': 'ansicyan',
    'debug': "#00FF89 bold",
    'red': '#ff0000',
    'delimiters': '#FF4689',
    'pygments.punctuation': '#D866FF',
    'pygments.keyword': '#FF4689 bold',
    'pygments.name.builtin': "#78DCE8 bold",
    "pygments.generic.strong": "#ff4249"
})

pygments_monokai_style = get_style_by_name('monokai')
style = style_from_pygments_cls(pygments_monokai_style)
style = merge_styles([style, Message_Style])
basic_formatter_cls = Terminal256Formatter(style='monokai')

lion_lexer_cls = LiONLexer()


class ImpossibleError(ParsingError):
    pass


class LSI(LiONStandard):
    def __init__(self):
        self.stdout = print
        self.mode = 'lion'

        self.shell_config_module = construct_node("shell")
        self.shell_config_module.update({
            "__icon__": "🖥️",
            "__init__": LION_SHELL_MODULE_DIR + "/shellinit.lion",
            "__bar__": True,
            "__pound__": "L\u2009",
            "shdir": construct_variable("shdir", LION_SHELL_MODULE_DIR, __rs__=(FINAL,)),
        })

        self.PACKAGE = {
            "shell": self.shell_config_module,
            "highlight": construct_builtin("highlight", self.highlight_builtin,
                                           __icon__="✏️"),
            "seef": construct_builtin("seef", self.seef_builtin,
                                      __icon__="🔍"),
        }

        super().__init__(cargo={"LSI": lambda: self.PACKAGE})

    def color_dms_symbol(self, directory: str):
        for n in self.dms.storage:
            if n in directory:
                directory = directory.replace(n, newColored(DMS_COLOR, n))
        return directory

    @staticmethod
    def format_out(text):
        format_out(text)

    def print_exception(self, error):
        print(newColored(NOT_SECURE_COLOR, f'[{self.get_name()}] '
                                           f'{f"{error.__class__.__name__}: " if self.get_debug() else ""}'
                                           f'{error}'))

    def bottom_toolbar(self):
        return HTML(f'<b><style bg="ansired">{self["__name__"]}</style></b> '
                    + ((f'<b><style fg="ansigreen">Debugging</style></b>' + ' ') if self.get_debug() else '')
                    + (('<b><style bg="red">Not secure mode</style></b>' +
                        ' ') if not self.secure else '')
                    + (('<b><style fg="ansired">Errors can throw</style></b>'
                        + ' ') if self[THROW_ERRORS][RELATIVE_ATTRIBUTE] else '')
                    + f'ln::{len(self.get_root())} '
                    + f'at {self.dms.get_cwd()}')

    def get_message(self):
        message = [
            ('class:directory', self.dms.get_cwd() + ' '),
        ]

        if self[THROW_ERRORS][RELATIVE_ATTRIBUTE]:
            message.append(('class:red', '!'))

        if not self.secure:
            message.append(('class:red', '*'))

        return message + [
            ('class:pound', self.shell_config_module["__pound__"]) if not self.get_debug() else ('class:debug', '& ')]

    @staticmethod
    def highlight_builtin(code: str, extension='lion'):
        if '.' + extension in FILE_EXTENSIONS:
            return highlight(code, lion_lexer_cls, basic_formatter_cls)

        match extension.lower():
            case 'md':
                return highlight(code, get_lexer_by_name('markdown'), basic_formatter_cls)

            case 'json':
                return highlight(code, get_lexer_by_name('json'), basic_formatter_cls)

            case 'yaml' | 'yml' | 'neo':
                return highlight(code, get_lexer_by_name('yaml'), basic_formatter_cls)

            case _:
                try:
                    lexer = get_lexer_by_name(extension)
                    return highlight(code, lexer, basic_formatter_cls)
                except pygments.util.ClassNotFound:
                    return code

    def seef_builtin(self, filename: str):
        filename = self.dms.parse(filename)
        contents = loadRaw(filename)
        self.stdout(self.highlight_builtin(contents, funclib.getFileExtensionByDir(filename)))

    def prompt(self, session: PromptSession = None, msg=">>> "):
        if not session:
            session = PromptSession()

        with patch_stdout():
            user_input = ""

            while True:
                try:
                    new_input = session.prompt(msg if user_input == '' else '... ')
                    user_input += new_input + "\n"

                    if is_brackets_balanced(count_brackets(user_input)):
                        break

                except KeyboardInterrupt:
                    self.stdout(newColored((255, 0, 0), "KeyboardInterrupt"))
                    return

            return user_input

    def run(self, run_init=True):
        # Runs shell init
        if run_init:
            self.run_statement(self.shell_config_module["__init__"], silent=True)

        running = True
        history = InMemoryHistory()
        completer = WordCompleter([str(k) for k in self.get_root()])
        lion_lexer = PygmentsLexer(LiONLexer)
        session = PromptSession(
            history=history,
            lexer=lion_lexer,
            style=style,
            color_depth=ColorDepth.TRUE_COLOR,
            auto_suggest=AutoSuggestFromHistory(),
            completer=completer,
            bottom_toolbar=self.bottom_toolbar,
            multiline=False
        )

        while running:
            exptype = ImpossibleError if self[THROW_ERRORS][RELATIVE_ATTRIBUTE] else Exception
            completer.words = [str(k) for k in self.get_root()]
            session.bottom_toolbar = self.bottom_toolbar if self.shell_config_module["__bar__"] else None
            try:
                user_input = self.prompt(session, self.get_message())

                if not user_input.strip():
                    continue

                if user_input.startswith("!exit"):
                    running = False

                elif mode == 'lion':
                    out = self.parsefunc(user_input)
                    if out is not None and not self.get_debug():
                        self.format_out(out)
                elif mode == 'cmd':
                    os.system(user_input)

            except KeyboardInterrupt:
                self.stdout(newColored((255, 0, 0), "KeyboardInterrupt"))

            except EOFError:
                self.stdout(newColored((255, 0, 0), "EOFError"))

            except exptype as error:
                if self.get_debug():
                    tb = traceback.format_exc()
                    self.print_exception(tb)
                self.print_exception(error)

            except not self[THROW_ERRORS][RELATIVE_ATTRIBUTE] and exptype as error:
                self.print_exception(error)

        self.stdout(f"[{self.get_name()}] Exiting LiON shell...", flush=False)

from LiON.parser import *
from LiON.modules.lml.const import *


class LMLSyntaxError(ValueError):
    pass


def parseline(line: str):
    lst = line.strip()
    if lst == LML_NEWLINE:
        return '\n'
    elif lst.startswith('..'):
        return line.replace('..', '.', 1)

    return line


class LMLCompiler:
    def __init__(self, stdin: str, parser: TreeManager, stdout=None, refs: dict = None):

        self.stdout = parser.stdout if not stdout else stdout
        self.parser = parser
        self.compiled = None

        self._stdin = stdin

        if not refs:
            refs = {}

        refs.update({
            LML_STDOUT_NAME: construct_builtin(LML_STDOUT_NAME, self.stdout)
        })

        self.parser.assign_references(refs)


    def run(self):
        assert self.compiled is not None, "You first need to call the .compile() method before running."
        self.parser.parsefunc(self.compiled)

    def compile(self) -> str:
        output_lines = []
        text_start = 0
        cursor = 0

        def append_text(text: str):
            if text:
                output_lines.append(f'{LML_STDOUT_NAME} "{text.strip()}"')

        def append_code(code: str):
            code = code.strip()
            if code:
                output_lines.append(code)

        while cursor < len(self._stdin):
            block_start = self._stdin.find(LML_LION_BLOCK_START, cursor)
            directive_start = self._stdin.find(LML_LION_SCRIPTLET, cursor)
            if directive_start != -1 and directive_start != 0:
                if self._stdin[directive_start - 1] != '\n':
                    directive_start = -1

            candidates = [index for index in (block_start, directive_start)
                          if index != -1]
            if not candidates:
                break

            scriptlet_start = min(candidates)
            append_text(self._stdin[text_start:scriptlet_start])

            if scriptlet_start == block_start:
                block_end = self._stdin.find(LML_LION_BLOCK_END,
                                             scriptlet_start + len(LML_LION_BLOCK_START))
                if block_end == -1:
                    raise LMLSyntaxError(
                        f"Unterminated LML code block starting at character "
                        f"{scriptlet_start}"
                    )

                append_code(self._stdin[
                    scriptlet_start + len(LML_LION_BLOCK_START):block_end
                ])
                cursor = block_end + len(LML_LION_BLOCK_END)
                text_start = cursor
                continue

            line_end = self._stdin.find('\n', scriptlet_start)
            if line_end == -1:
                line_end = len(self._stdin)
            append_code(self._stdin[
                scriptlet_start + len(LML_LION_SCRIPTLET):line_end
            ])
            cursor = line_end + (1 if line_end < len(self._stdin) else 0)
            text_start = cursor

        append_text(self._stdin[text_start:])

        self.compiled = '\n'.join(output_lines)
        return self.compiled

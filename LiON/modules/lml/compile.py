from LiON.parser import *
from LiON.modules.lml.const import *
import re


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
        lines = self._stdin.splitlines(keepends=True)
        output_lines = []
        current_block = []

        for line in lines:
            if line.startswith('@@'):
                if current_block:
                    output_lines.append(f'{LML_STDOUT_NAME} "{"".join(current_block).strip()}"')
                    current_block = []
                output_lines.append(line[2:].strip())
            else:
                current_block.append(line)

        if current_block:
            output_lines.append(f'{LML_STDOUT_NAME} "{"".join(current_block).strip()}"')

        self.compiled = '\n'.join(output_lines)
        return self.compiled

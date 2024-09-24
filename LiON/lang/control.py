from typing import Literal

AB_INTERNALS = Literal['BREAK', 'CONTINUE']


class AbstractInternal:
    def __init__(self, type_: AB_INTERNALS):
        self.type = type_

    def get(self):
        return self.type

    def __eq__(self, other):
        if isinstance(other, AbstractInternal):
            return self.type.upper() == other.type.upper()
        elif isinstance(other, str):
            return other.upper() == self.type.upper()
        return False


AB_CALLS = {
    "break": AbstractInternal('BREAK'),
    "continue": AbstractInternal('CONTINUE')
}


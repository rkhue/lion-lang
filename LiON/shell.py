from LiON import *
import traceback
import os


# run initializer script
init = loadRaw('./LiON/scripts/init.lion')
LiON = LiONStandard()


DMS_COLOR = (0, 189, 255)
DEBUG_COLOR = (0, 255, 0)
NOT_SECURE_COLOR = (255, 0, 0)
TYPE_COLOR = (189, 189, 255)
NODE_COLOR = (255, 189, 0)

EXECUTING_MODE = "lion"
CMD_MODE = "cmd"


def print_exception(Error):
    print(newColored(NOT_SECURE_COLOR, f'[{LiON["__name__"]}] '
                                       f'{f"{Error.__class__.__name__}: " if LiON else ""}'
                                       f'{Error}'))


class ImpossibleError(ParsingError):
    pass


def color_dms_symbol(directory: str):
    for k in LiON.dms.get_storage():
        if k in directory:
            directory = directory.replace(k, newColored(DMS_COLOR, k))
    return directory


def format_out(text):
    type_text = typeof(text)

    print(
        f"[{newColored(TYPE_COLOR, type_text)}] {newColored((0, 255, 0), 'out:')} ",
        end="")
    if isinstance(text, dict):
        try:
            print(json.dumps(text, indent=4, ensure_ascii=False))
        except Exception:
            print(text)
        return

    print(text)


def get_input_text(mode: str):
    return (f'{newColored(NOT_SECURE_COLOR, "!") if LiON[THROW_ERRORS][RELATIVE_ATTRIBUTE] else ""}'
            f'{(mode + ":") if mode != EXECUTING_MODE else ""}{color_dms_symbol(LiON.dms.get_cwd())} '
            f'{newColored(NOT_SECURE_COLOR, "*") if not LiON.secure else ""}'
            f'{newColored(DEBUG_COLOR, "& ") if LiON.get_debug() else "$ "}')


def count_brackets(input_str: str) -> dict[str, int]:
    brackets = {"(": 0, ")": 0, "[": 0, "]": 0, "{": 0, "}": 0}

    opened_string = False
    for char in input_str:
        if char == '"':
            if opened_string:
                opened_string = False
            elif not opened_string:
                opened_string = True
            continue

        if not opened_string:
            if char in brackets:
                brackets[char] += 1

    return brackets


def is_brackets_balanced(brackets: dict[str, int]) -> bool:
    return (brackets['('] == brackets[')']
            and
            brackets['['] == brackets[']']
            and
            brackets['{'] == brackets['}'])


def start(mode: Literal['lion', 'cmd'] = EXECUTING_MODE):
    LiON.parsefunc(init)

    user_input = ""
    while True:
        exptype = ImpossibleError if LiON[THROW_ERRORS][RELATIVE_ATTRIBUTE] else Exception

        line_input = LiON.stdin(get_input_text(mode) if not user_input else '... ')

        if not line_input.strip():
            continue

        user_input += line_input + '\n'
        brackets = count_brackets(user_input)

        if is_brackets_balanced(brackets):
            if user_input.startswith('!') and len(user_input) != 1:
                command = user_input[1:].strip()
                split = command.split(' ')
                comname = split[0]
                args = split[1:]
                if comname == 'exit':
                    break
                elif comname == "mode":
                    if len(args) != 1:
                        raise ArgumentBindingMismatchError(
                            "Expected exactly 1 argument to be given to special command 'mode'"
                        )

                    newmode = args[0]
                    LiON.stdout(f'[shell.py] Changing mode {mode} -> {newmode}')
                    mode = str(newmode)

                user_input = ""
                continue

            try:
                if mode == EXECUTING_MODE:
                    out = LiON.parsefunc(user_input)
                    if out is not None and not LiON.get_debug():
                        format_out(out)
                elif mode == CMD_MODE:
                    os.system(user_input)

                else:
                    print_exception(Exception(f"[SHELL] {repr(mode)} mode not implemented"))
                    mode = EXECUTING_MODE
                continue
            except exptype as error:
                if LiON.get_debug():
                    tb = traceback.format_exc()
                    print_exception(tb)
                print_exception(error)

            finally:
                user_input = ""

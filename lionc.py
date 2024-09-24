from LiON.shell import start, format_out
from LiON_shell import LSI
from LiON import *
import json
import sys

LOADED_FROM_IMPORT = False

try:
    global parent_parser
    lion = parent_parser
    LOADED_FROM_IMPORT = True
except NameError as e:
    lion = LiONStandard()
    sys.path.append(__file__)

PATH_TO_DOCUMENTATION = os.path.dirname(__file__) + "/LiON_shell/docs/lionc_help.md"
DOCUMENTATION = funclib.loadRaw(PATH_TO_DOCUMENTATION)


def print_usage():
    lion.stdout(DOCUMENTATION, flush=False)


def parse_argv(*args):
    if not LOADED_FROM_IMPORT:
        args = args[1:]

    mode = args[0].lower()
    match mode:
        case "-r":
            lion.run_statement(lion.dms.parse(args[1]))

        case "-sh":
            start()
        case "-wi":
            LSI().run(False)
        case "-i":
            LSI().run()

        case "-c":
            optional = args[2:]
            filename = lion.dms.parse(args[1])
            lexed_code = full_lexer(funclib.loadRaw(filename),
                                    debug='--d' in optional,
                                    del_comments='--nocom' not in optional)
            funclib.write_file(args[2], json.dumps(
                construct_variable(getFileNameFromDir(filename), lexed_code),
                ensure_ascii=False, indent=4))

        case "-exec":
            filename = lion.dms.parse(args[1])
            node = funclib.openJson(filename)

            out = lion.exec(node)
            format_out(out)
            lion.print_finished(filename)

        case '-h':
            print_usage()

        case _:
            print('Invalid command! Try seeing `lionc.py -h` for help')


if __name__ == "__main__":
    parse_argv(*sys.argv)
else:
    cli_module = construct_builtin("lionc", parse_argv)
    cli_module.update({
        "help": construct_builtin("help", print_usage),
        "__doc__": f"""You can find the docs for lionc.py here {repr(PATH_TO_DOCUMENTATION)}"""
    })
    lion.assign_references({
        "lionc": cli_module
    })

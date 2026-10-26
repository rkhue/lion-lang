from LiON.shell import start, format_out
from LiON_shell import LSI
from LiON import *
import json
import os
from pathlib import Path
import sys

LOADED_FROM_IMPORT = False

try:
    global parent_parser
    lion = parent_parser
    LOADED_FROM_IMPORT = True
except NameError:
    lion = LiONStandard()

PATH_TO_DOCUMENTATION = Path(__file__).with_name("LiON_shell") / "docs" / "lionc_help.md"
DOCUMENTATION = funclib.loadRaw(PATH_TO_DOCUMENTATION)


def print_usage():
    try:
        lion.stdout(DOCUMENTATION, flush=False)
    except UnicodeEncodeError:
        output = DOCUMENTATION.encode(sys.stdout.encoding or "utf-8", errors="replace")
        sys.stdout.buffer.write(output)
        sys.stdout.flush()


def _error(message: str) -> int:
    print(f"lionc: {message}", file=sys.stderr)
    return 2


def _path_argument(value: str, *, must_exist: bool) -> Path:
    path = Path(value).expanduser()
    path = path.resolve(strict=True) if must_exist else path.absolute()
    if must_exist and not path.is_file():
        raise IsADirectoryError(f"not a regular file: {value}")
    if not must_exist and not path.parent.is_dir():
        raise FileNotFoundError(f"output directory does not exist: {path.parent}")
    return path


def _write_compiled(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    created = False
    try:
        file = temporary.open("x", encoding="utf-8", newline="")
        created = True
        with file:
            file.write(content)
        os.replace(temporary, path)
    finally:
        if created:
            temporary.unlink(missing_ok=True)


def parse_argv(*args):
    if not LOADED_FROM_IMPORT:
        args = args[1:]

    if not args:
        print_usage()
        return 2

    mode = args[0].lower()
    match mode:
        case "-r":
            if len(args) != 2:
                return _error("usage: -r <filepath>")
            try:
                lion.run_statement(str(_path_argument(args[1], must_exist=True)))
            except (OSError, UnicodeError) as error:
                return _error(str(error))

        case "-sh":
            if len(args) != 1:
                return _error("usage: -sh")
            start()
        case "-wi":
            if len(args) != 1:
                return _error("usage: -wi")
            LSI().run(False)
        case "-i":
            if len(args) != 1:
                return _error("usage: -i")
            LSI().run()

        case "-c":
            optional = args[3:]
            if len(args) < 3:
                return _error("usage: -c <input_filepath> <output_filepath> [--d|--debug]")
            if any(flag not in ("--d", "--debug") for flag in optional):
                return _error("unknown -c option")
            try:
                filename = _path_argument(args[1], must_exist=True)
                output = _path_argument(args[2], must_exist=False)
                if filename == output:
                    return _error("input and output paths must be different")
                lexed_code = full_lexer(
                    filename.read_text(encoding="utf-8"),
                    debug="--d" in optional or "--debug" in optional
                )
                compiled = json.dumps(
                    construct_variable(filename.name, lexed_code),
                    ensure_ascii=False,
                    indent=4
                )
                _write_compiled(output, compiled)
            except (OSError, UnicodeError, TypeError, ValueError) as error:
                return _error(str(error))

        case "-exec":
            if len(args) != 2:
                return _error("usage: -exec <input_filepath>")
            try:
                filename = _path_argument(args[1], must_exist=True)
                node = json.loads(filename.read_text(encoding="utf-8"))
                out = lion.exec(node)
                format_out(out)
                lion.print_finished(str(filename))
            except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
                return _error(str(error))

        case '-h':
            if len(args) != 1:
                return _error("usage: -h")
            print_usage()

        case _:
            return _error("invalid command; try `lionc.py -h`")

    return 0


if __name__ == "__main__":
    sys.exit(parse_argv(*sys.argv))
else:
    cli_module = construct_builtin("lionc", parse_argv)
    cli_module.update({
        "help": construct_builtin("help", print_usage),
        "__doc__": f"""You can find the docs for lionc.py here {repr(PATH_TO_DOCUMENTATION)}"""
    })
    lion.assign_references({
        "lionc": cli_module
    })

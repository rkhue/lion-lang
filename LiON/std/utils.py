import json
import os
global parent_parser, construct_builtin, construct_node, funclib, dms


def change_directory(d: str):
    dms.change_dir(d)


def dmsParse(f):
    def wrapper(*args, **kwargs):
        if args:
            assert isinstance(args[0], str), "Cannot parse a non-string directory."
            directory = dms.parse(args[0])
            args = (directory,) + args[1:]

        return f(*args, **kwargs)

    return wrapper


def make_file(filename: str):
    with open(dms.parse(filename), 'w+', encoding='utf-8') as f:
        f.write('')


def write_file(filename: str, *args, mode='w+'):
    with open(dms.parse(filename), mode, encoding='utf-8') as f:
        for arg in args:
            f.write(arg)


def json_builtin(content: dict, i=4, ea=False):
    return json.dumps(content, indent=i, ensure_ascii=ea)


def write_json(filename: str, content: dict, i=4, ea=False):
    with open(dms.parse(filename), 'w+', encoding='utf-8') as f:
        f.write(json_builtin(content, i, ea))


def loadRaw_builtin(filename: str, *args):
    filename = dms.parse(filename)
    return funclib.loadRaw(filename, *args)


def loadJson_builtin(filename: str, *args):
    filename = dms.parse(filename)
    return funclib.openJson(filename, *args)


def loadRaws_builtin(directory: str, e=None, *args):
    directory = dms.parse(directory)
    return tuple(funclib.loadRaws(directory, e, *args))


def loadJsons_builtin(directory: str, e=None, *args):
    directory = dms.parse(directory)
    return tuple(funclib.openJSONs(directory, e, *args))


def loadLines_builtin(directory: str, *args):
    directory = dms.parse(directory)
    return funclib.loadTxt(directory, *args)


def remove_dir_builtin(filename: str):
    os.rmdir(dms.parse(filename))


def remove_file_builtin(filename: str):
    os.remove(filename)


def make_dir_builtin(directory: str):
    os.mkdir(dms.parse(directory))


def sort_dir_key(item):
    is_dir = os.path.isdir(item)
    return not is_dir, item.lower()


def list_directory_builtin(directory: str = '.', s='some'):
    inside = sorted(os.listdir(dms.parse(directory)), key=sort_dir_key)
    for t in inside:
        if t.startswith('.') and s == 'some':
            continue
        if os.path.isdir(directory + "/" + t):
            parent_parser.stdout(funclib.newColored((0, 255, 255) if not t.startswith('.') else (189, 189, 189),
                                                    f"📁 {t}"))
        elif t.endswith('.py'):
            parent_parser.stdout(funclib.newColored((0, 255, 0), f"🅿️ {t}"))
        elif t.endswith('.json'):
            parent_parser.stdout(funclib.newColored((255, 189, 0), f'📦 {t}'))
        elif t.endswith('.lion'):
            parent_parser.stdout(funclib.newColored((255, 255, 0), f'🦁 {t}'))
        else:
            parent_parser.stdout(funclib.newColored((189, 189, 189), f'📄 {t}'))


def cat_builtin(filename: str):
    path = dms.parse(filename)
    parent_parser.stdout(f"* {funclib.getFileNameFromDir(filename)}\n")
    parent_parser.stdout(funclib.loadRaw(path))


# file loading
load = construct_builtin('load', loadRaw_builtin)
write = construct_builtin('write', write_file)

load.update({
    "lines": construct_builtin('lines', loadLines_builtin),
    "raw": construct_builtin('raw', loadRaw_builtin),
    "raws": construct_builtin('raws', loadRaws_builtin),
    "json": construct_builtin('json', loadJson_builtin),
    "jsons": construct_builtin('jsons', loadJsons_builtin)
})

write.update({
    "json": construct_builtin('json', write_json)
})

file = construct_node("file", **{
    "exists": construct_builtin("exists", dmsParse(os.path.exists)),
    "isfile": construct_builtin("isfile", dmsParse(os.path.isfile)),
    "isdir": construct_builtin("isdir", dmsParse(os.path.isdir)),
})

parent_parser.assign_references({
    "file": file,
    "dir": construct_builtin("dir", lambda d: sorted(os.listdir(dms.parse(d))), key=sort_dir_key),
    "ls": construct_builtin('ls', list_directory_builtin),
    "cat": construct_builtin("cat", cat_builtin),
    "cd": construct_builtin('cd', change_directory),
    "cwd": construct_builtin('cwd', os.getcwd),
    "touch": construct_builtin('touch', make_file),
    "load": load,
    "write": write,
    "json": construct_builtin('json', json_builtin),
    "mkdir": construct_builtin('mkdir', make_dir_builtin),
    "rm": construct_builtin('rm', remove_file_builtin),
    "del": construct_builtin('del', remove_dir_builtin),
})
# construct file load module

from os import listdir, path
import zipfile
import pathlib
import random
import math
import json
import re
import os

BOOL_TABLE = {
    1: True,
    0: False,
    -1: False,
    "1": True,
    "0": False,
    "-1": False,
    "true": True,
    "false": False,
    "yes": True,
    "no": False,
    "y": True,
    "n": False
}


LINUX_OCT_PERMISSION = {
    "---": "000",
    "--x": "001",
    "-w-": "010",
    "-wx": "011",
    "r--": "100",
    "r-x": "101",
    "rw-": "110",
    "rwx": "111"
}
LINUX_PERM_OCT = {v: k for k, v in LINUX_OCT_PERMISSION.items()}


def flatten_dict(dictionary: dict, parent_key: str = '', sep: str = '.',
                 stop_key: str = '__class__') -> dict:
    flattened_dict = {}
    for key, value in dictionary.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            if stop_key in value and value[stop_key]:
                flattened_dict[new_key] = value
            else:
                flattened_dict.update(flatten_dict(value, new_key, sep=sep, stop_key=stop_key))
        else:
            flattened_dict[new_key] = value
    return flattened_dict


def insert_strings(texts: list[str], noise: str) -> str:
    result = list(noise)
    indices = list(range(len(noise)))

    already_used_indices = []

    for text in texts:
        text_size = len(text)

        while True:
            start_index = random.choice(indices[:len(indices) - text_size + 1])
            end_index = start_index + text_size

            overlap = False
            for used_index in already_used_indices:
                if start_index < used_index[1] and end_index > used_index[0]:
                    overlap = True
                    break

            if not overlap:
                break

        result[start_index:end_index] = text
        already_used_indices.append((start_index, end_index))
        indices = [i for i in indices if i < start_index or i >= end_index]

    return ''.join(result)


def clear_cache(directory: str):
    [p.unlink() for p in pathlib.Path(directory).rglob('*.py[co]')]
    [p.rmdir() for p in pathlib.Path(directory).rglob('__pycache__')]


class ZipUtilities:
    def toZip(self, file, filename):
        zip_file = zipfile.ZipFile(filename, 'w')
        if path.isfile(file):
            zip_file.write(file)
        else:
            self.addFolderToZip(zip_file, file)
        zip_file.close()

    def addFolderToZip(self, zip_file, folder):
        with zipfile.ZipFile(zip_file, 'a') as zf:
            self.addFolderToOpenZip(zf, zip_file, folder)

    def addFolderToOpenZip(self, zf, zip_file, folder):
        for file in listdir(folder):
            full_path = path.join(folder, file)
            if path.isfile(full_path):
                zf.write(full_path)
            elif path.isdir(full_path):
                self.addFolderToOpenZip(zf, zip_file, full_path)


def prod(array):
    o = None
    for elem in array:
        if not o:
            o = elem
            continue
        o *= elem
    return o


def deep_sine(x, amplitude: float, frequency: float, depth: int, exp_factor: float) -> float:
    """
    Link of the detailed function in <https://www.desmos.com/calculator/xiqw5zttt0>
    :param x: Number
    :param amplitude: Amplitude of the sine waves
    :param frequency: Frequency of the sine waves
    :param depth: How many sine waves to be multiplied
    :param exp_factor: Exponential factor
    :return: float
    """

    sines = []
    for i in range(depth):
        den = exp_factor ** i
        sines.append((math.sin((x + i) * frequency) * amplitude) / den)

    return prod(sines)


def apply_sine(arr, angle: float, amplitude: float = 1, freq: float = 2, func=math.sin):
    return [func(((x + angle) * amplitude) * freq) for x in arr]


def apply_sine2(arr, func=math.sin):
    return [func(x) for x in arr]


def mda(numbers: list):
    lenNums = len(numbers)
    x = 0
    for i in numbers:
        x += i
    return x / lenNums


def tokenize(string: str) -> list[str]:
    return [i for i in re.split(r'(\d+|\W+)', string) if i]


def array_to_rotated_matrix2D(array, width, height):
    matrix = []
    for x in range(width):
        matrix.append([])
        for y in range(height):
            matrix[x].append(array[y * width + x])
    return matrix


def array_to_matrix2D(array, width, height):
    matrix = []

    for y in range(height):
        col = []
        for x in range(width):
            col.append(array[y * width + x])
        matrix.append(col)
    return matrix


def matrix2D_to_array(matrix):
    array = []
    for y in range(len(matrix[0])):
        for x in range(len(matrix)):
            array.append(matrix[x][y])
    return array


def revert_matrix(matrix):
    return matrix[::-1]


def fix_matrix(matrix):
    return list(zip(*matrix[::-1]))


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        print(chr(27) + "[2J")


def blockTop(length=30, char: str = "-"):
    print(char * length)


def Convert_to_arr(string):
    list1 = []
    list1[:0] = string
    return list1


def loadTxt(path, encoding='utf-8'):
    if not os.path.exists(path):
        raise FileNotFoundError(f'File in {path} does not exist')
    else:
        with open(path, 'r', encoding=encoding) as f:
            lines = f.readlines()
            for i, lin in enumerate(lines):
                lines[i] = lin.replace('\n', '')

        return lines


def loadRaw(path, encoding='utf-8') -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f'File in {path} does not exist')

    with open(path, 'r', encoding=encoding) as f:
        content = f.read()

    return content


def loadRaws(path, extension=None, encoding='utf-8') -> list[str]:
    filenames = getFilesFromDir(path, extension=extension)
    out = []
    for f in filenames:
        out.append(loadRaw(path + f, encoding=encoding))
    return out


def openJSONs(path, extension=None, encoding='utf-8') -> dict[str, dict]:
    filenames = getFilesFromDir(path, extension=extension)
    out = {}
    for f in filenames:
        out.update({f: openJson(path + f, encoding=encoding)})
    return out


def split_list(Input_list, n):
    for i in range(0, len(Input_list), n):
        yield Input_list[i:i + n]


def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def newColored(color: tuple, text):
    return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(color[0], color[1], color[2], text)


def is_float(element: str) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False


def openJson(dire, encoding='utf-8') -> dict:
    with open(dire, 'r', encoding=encoding) as f:
        js = json.loads(f.read())
        return js


def is_int(element: str) -> bool:
    try:
        int(element)
        return True
    except ValueError:
        return False


def askForYorN(question: str, stdin=input):
    while True:
        i = stdin(f"{question}{'[y/n]' if '[y/n]' not in question.lower() else ''}: ").lower()
        if i.startswith('y'):
            return True  # yes
        elif i.startswith('n'):
            return False  # no


def askForIntBetween(a: int, b: int, question: str = "A number between ", stdin=input):
    while True:
        i = stdin(question + f"[{a} ~ {b}]: ")
        if is_int(i):
            if a <= int(i) <= b:
                return int(i)


def askForFloatBetween(a: int, b: int, question: str = "A number between ", stdin=input):
    while True:
        i = stdin(question + f"[{a} ~ {b}]: ")
        if is_float(i):
            if a <= float(i) <= b:
                return float(i)


def getFileNameFromDir(directory: str):
    directory = directory.replace(r"\"", "/")
    return directory.replace('//', '/').split("/")[-1]


def getFileExtensionByDir(directory: str):
    return getFileNameFromDir(directory).split('.')[-1]


def getDirFromDir(directory: str):
    directory = directory.replace(r"\"", "/")
    return os.path.dirname(directory)


def line(size: int, char="-"):
    print(char * size)


def printBeauty(text, l_size=50):
    lin = False
    for n, la in enumerate(text):
        if n % l_size == 0 and n >= 1:
            lin = True
        if la == ' ' and lin:
            la += '\n'
            lin = False
        print(la, end='')
    print()


def getFilesFromDir(directory: str, extension=None):
    if extension is None:
        return [pos for pos in listdir(directory)]
    return [pos for pos in listdir(directory) if pos.endswith(extension)]


def endslist(filename: str, extensions) -> bool:
    for ext in extensions:
        if filename.endswith(ext):
            return True
    return False


def write_file(filename: str, content, encoding='utf-8'):
    with open(filename, 'w+', encoding=encoding) as file:
        file.write(content)


def getNamesFromList(lista: list):
    n_l = []
    for thing in lista:
        n_l.append(thing.name)

    return n_l


def get_multiples(n, count=1000):
    mul = []
    for num in range(count):
        if num % n == 0:
            mul.append(num)

    return mul


def get_closest_multiple_of(x, st=0, range_n=1000):
    num_m = 0

    for num in range(st, range_n):
        if num % x == 0:
            num_m = num
            break
    return num_m


def decompose(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors


def get_functional_range(num_range=5):
    return [-x for x in range(1, num_range + 1)] + list(range(num_range + 1))


def linear_function_points(angular_num, linear_num, num_range=5):
    def local_linear_function(x: float) -> float:
        return (float(angular_num) * x) + float(linear_num)

    return [(n, local_linear_function(n)) for n in get_functional_range(num_range)]


def pass_func():
    pass


def go_back(stdin: input):
    stdin('<-- Go back ')


def proceed(stdin: input):
    stdin('Proceed --> ')

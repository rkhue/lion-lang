import threading
import datetime
from timeit import timeit
from LiON.exceptions import ParsingError

global parent_parser, construct_builtin, scoped


@scoped("timeit")
def timeit_builtin(self, seconds, code):
    def do_work():
        self.parse_calls_direct(code)

    return timeit(do_work, number=int(seconds)) / int(seconds)


def timeout_builtin(self, *args):
    delay = 5
    if isinstance(args[0], int | float):
        delay = args[0]
        code = args[1]
    else:
        code = args[0]

    timer = threading.Timer(delay, function=lambda: self.parse_calls(code))
    timer.start()


def current_builtin(unit: str):
    today = datetime.datetime.now()
    match unit:
        case 'time':
            return today
        case 'second':
            return today.second
        case 'minute':
            return today.minute
        case 'hour':
            return today.hour
        case 'date':
            return today.date()
        case 'day':
            return today.day
        case 'weekday':
            return today.weekday()
        case 'month':
            return today.month
        case 'year':
            return today.year
        case _:
            raise ParsingError(f'[DATE] cannot resolve date unit {repr(unit)}, '
                               f'please consider using `time`, `hour`, `minute`, `second`'
                               f'`date`, `day`, `weekday`,'
                               f' `month` or `year`')


parent_parser.assign_references({
    "current": construct_builtin('current', current_builtin, __icon__="📅"),
    'timeit': construct_builtin('timeit', timeit_builtin, __icon__="⌚"),
    "timeout": construct_builtin('timeout', timeout_builtin, __icon__="⌛"),
})

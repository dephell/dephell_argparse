# built-in
import os


try:
    try:
        from colorama import Fore, init
    except ImportError:
        from pip._vendor.colorama import Fore, init
    init()
except ImportError:
    Fore = None


class _ForeAnsi:
    _f = '\x1b[{}m'.format

    BLACK = _f(30)
    RED = _f(31)
    GREEN = _f(32)
    YELLOW = _f(33)
    BLUE = _f(34)
    MAGENTA = _f(35)
    CYAN = _f(36)
    WHITE = _f(37)
    RESET = _f(39)


class _ForeWin:
    _f = '\x1b[{}m'.format

    BLACK = _f(30)
    RED = _f(31)
    GREEN = _f(32)
    YELLOW = _f(33)
    BLUE = _f(34)
    MAGENTA = _f(35)
    CYAN = _f(36)
    WHITE = _f(37)
    RESET = _f(39)


if Fore is None:
    if os.name == 'nt':
        Fore = _ForeAnsi
    else:
        Fore = _ForeWin

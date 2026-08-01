"""Non-GUI, non-file builtins (GRAMMAR.md §12): str/num/print/ascii/date/time, plus the
"system" builtins run_program/open_url/open_email.

Each function raises a plain ValueError/TypeError on bad input — the interpreter's
call wrapper catches those and re-raises as a LeopardRuntimeError with the call's
source line, so these functions don't need to know about line numbers at all.
"""

from __future__ import annotations

import datetime
import subprocess
import webbrowser

from .errors import describe_type


def leo_str(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, (int, float, str)):
        return str(value)
    raise TypeError(f"str() can't convert {describe_type(value)}")


def leo_num(text: str) -> float | int:
    if not isinstance(text, str):
        raise TypeError(f"num() needs a string, not {describe_type(text)}")
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        raise ValueError(f"'{text}' is not a number") from None


def leo_print(value: object) -> None:
    try:
        print(leo_str(value))
    except TypeError:
        raise TypeError(
            f"print() only supports numbers, strings, and true/false, not {describe_type(value)}"
        ) from None


def leo_ascii(char: str) -> int:
    if not isinstance(char, str) or len(char) != 1:
        raise ValueError("ascii() needs a single character")
    return ord(char)


def leo_date() -> str:
    return datetime.date.today().isoformat()


def leo_time() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def leo_run_program(command: str) -> int:
    if not isinstance(command, str):
        raise TypeError(f"run_program() needs a string, not {describe_type(command)}")
    result = subprocess.run(command, shell=True)
    return result.returncode


def leo_open_url(url: str) -> None:
    if not isinstance(url, str):
        raise TypeError(f"open_url() needs a string, not {describe_type(url)}")
    webbrowser.open(url)


def leo_open_email(address: str) -> None:
    if not isinstance(address, str):
        raise TypeError(f"open_email() needs a string, not {describe_type(address)}")
    webbrowser.open(f"mailto:{address}")


BUILTINS = {
    "str": leo_str,
    "num": leo_num,
    "print": leo_print,
    "ascii": leo_ascii,
    "date": leo_date,
    "time": leo_time,
    "run_program": leo_run_program,
    "open_url": leo_open_url,
    "open_email": leo_open_email,
}

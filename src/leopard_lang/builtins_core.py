"""Non-GUI, non-file builtins (GRAMMAR.md §12): str/num/split/join/print/ascii/date/time,
plus the "system" builtins run_program/open_url/open_email.

Each function raises a plain ValueError/TypeError on bad input — the interpreter's
call wrapper catches those and re-raises as a LeopardRuntimeError with the call's
source line, so these functions don't need to know about line numbers at all.
"""

from __future__ import annotations

import datetime
import math
import os
import random
import subprocess
import webbrowser

from .errors import describe_type


def _require_number(value: object, fname: str) -> float | int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{fname}() needs a number, not {describe_type(value)}")
    return value


def _require_whole_number(value: object, fname: str, what: str = "value") -> int:
    value = _require_number(value, fname)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{fname}()'s {what} must be a whole number")
    return value


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


def leo_is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def leo_is_string(value: object) -> bool:
    return isinstance(value, str)


def leo_is_list(value: object) -> bool:
    return isinstance(value, list)


def leo_type_of(value: object) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "list"
    return "nothing"  # a function call that fell off the end without a `return`


def leo_print(value: object) -> None:
    try:
        print(leo_str(value))
    except TypeError:
        raise TypeError(
            f"print() only supports numbers, strings, and true/false, not {describe_type(value)}"
        ) from None


def leo_input(prompt: str = "") -> str:
    if not isinstance(prompt, str):
        raise TypeError(f"input() needs a string prompt, not {describe_type(prompt)}")
    try:
        return input(prompt)
    except EOFError:
        raise ValueError("input() found no more input to read") from None


def leo_get_env(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError(f"get_env() needs a string, not {describe_type(name)}")
    return os.environ.get(name, "")


def leo_split(text: str, sep: str) -> list:
    if not isinstance(text, str):
        raise TypeError(f"split() needs a string, not {describe_type(text)}")
    if not isinstance(sep, str) or sep == "":
        raise ValueError("split() needs a non-empty separator string")
    return text.split(sep)


def leo_join(items: list, sep: str) -> str:
    if not isinstance(items, list):
        raise TypeError(f"join() needs a list, not {describe_type(items)}")
    if not isinstance(sep, str):
        raise TypeError(f"join()'s separator must be a string, not {describe_type(sep)}")
    for item in items:
        if not isinstance(item, str):
            raise TypeError("join() needs a list of strings — use str() to convert numbers first")
    return sep.join(items)


def leo_ascii(char: str) -> int:
    if not isinstance(char, str) or len(char) != 1:
        raise ValueError("ascii() needs a single character")
    return ord(char)


def leo_chr(code: float | int) -> str:
    code = _require_number(code, "chr")
    if isinstance(code, bool) or not isinstance(code, int):
        raise TypeError("chr() needs a whole number")
    try:
        return chr(code)
    except (ValueError, OverflowError):
        raise ValueError(f"{code} is not a valid character code") from None


def _values_equal(left: object, right: object) -> bool:
    """Leopard's `=` equality (interpreter.py's Interpreter._values_equal) — duplicated
    here rather than imported, since interpreter.py already imports this module."""
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    left_is_num = isinstance(left, (int, float)) and not isinstance(left, bool)
    right_is_num = isinstance(right, (int, float)) and not isinstance(right, bool)
    if left_is_num and right_is_num:
        return left == right
    return type(left) is type(right) and left == right


def leo_upper(s: str) -> str:
    if not isinstance(s, str):
        raise TypeError(f"upper() needs a string, not {describe_type(s)}")
    return s.upper()


def leo_lower(s: str) -> str:
    if not isinstance(s, str):
        raise TypeError(f"lower() needs a string, not {describe_type(s)}")
    return s.lower()


def leo_trim(s: str) -> str:
    if not isinstance(s, str):
        raise TypeError(f"trim() needs a string, not {describe_type(s)}")
    return s.strip()


def leo_contains(collection: object, value: object) -> bool:
    if isinstance(collection, str):
        if not isinstance(value, str):
            raise TypeError(f"contains() needs a string to search for, not {describe_type(value)}")
        return value in collection
    if isinstance(collection, list):
        return any(_values_equal(item, value) for item in collection)
    raise TypeError(f"contains() needs a string or list, not {describe_type(collection)}")


def leo_index_of(collection: object, value: object) -> int:
    """1-based position of `value`, or 0 if not found (0 is Leopard's existing
    "no match" sentinel — see `.selected`)."""
    if isinstance(collection, str):
        if not isinstance(value, str):
            raise TypeError(f"index_of() needs a string to search for, not {describe_type(value)}")
        return collection.find(value) + 1
    if isinstance(collection, list):
        for i, item in enumerate(collection, start=1):
            if _values_equal(item, value):
                return i
        return 0
    raise TypeError(f"index_of() needs a string or list, not {describe_type(collection)}")


def leo_reverse(collection: object) -> object:
    if isinstance(collection, str):
        return collection[::-1]
    if isinstance(collection, list):
        return list(reversed(collection))
    raise TypeError(f"reverse() needs a string or list, not {describe_type(collection)}")


def leo_sort(items: list) -> list:
    if not isinstance(items, list):
        raise TypeError(f"sort() needs a list, not {describe_type(items)}")
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in items):
        return sorted(items)
    if all(isinstance(v, str) for v in items):
        return sorted(items)
    raise TypeError("sort() needs a list of all numbers or all strings")


def leo_remove_at(items: list, index: float | int) -> list:
    if not isinstance(items, list):
        raise TypeError(f"remove_at() needs a list, not {describe_type(items)}")
    index = _require_whole_number(index, "remove_at", "index")
    if index < 1 or index > len(items):
        plural = "item" if len(items) == 1 else "items"
        raise ValueError(f"remove_at() index {index} is out of range (list has {len(items)} {plural})")
    return items[: index - 1] + items[index:]


def leo_sum(items: list) -> float | int:
    if not isinstance(items, list):
        raise TypeError(f"sum() needs a list, not {describe_type(items)}")
    return sum(_require_number(v, "sum") for v in items)


def leo_replace(s: str, old: str, new: str) -> str:
    if not isinstance(s, str):
        raise TypeError(f"replace() needs a string, not {describe_type(s)}")
    if not isinstance(old, str) or old == "":
        raise ValueError("replace() needs a non-empty search string")
    if not isinstance(new, str):
        raise TypeError(f"replace()'s replacement must be a string, not {describe_type(new)}")
    return s.replace(old, new)


def leo_starts_with(s: str, prefix: str) -> bool:
    if not isinstance(s, str):
        raise TypeError(f"starts_with() needs a string, not {describe_type(s)}")
    if not isinstance(prefix, str):
        raise TypeError(f"starts_with() needs a string to check for, not {describe_type(prefix)}")
    return s.startswith(prefix)


def leo_ends_with(s: str, suffix: str) -> bool:
    if not isinstance(s, str):
        raise TypeError(f"ends_with() needs a string, not {describe_type(s)}")
    if not isinstance(suffix, str):
        raise TypeError(f"ends_with() needs a string to check for, not {describe_type(suffix)}")
    return s.endswith(suffix)


def leo_substring(s: str, start: float | int, end: float | int) -> str:
    if not isinstance(s, str):
        raise TypeError(f"substring() needs a string, not {describe_type(s)}")
    start = _require_whole_number(start, "substring", "start")
    end = _require_whole_number(end, "substring", "end")
    if start < 1 or end > len(s) or start > end:
        raise ValueError(
            f"substring() range {start}..{end} is out of range (string has {len(s)} characters)"
        )
    return s[start - 1 : end]


def leo_left(s: str, n: float | int) -> str:
    if not isinstance(s, str):
        raise TypeError(f"left() needs a string, not {describe_type(s)}")
    n = _require_whole_number(n, "left", "count")
    if n < 0:
        raise ValueError("left() needs a count that isn't negative")
    return s[:n]


def leo_right(s: str, n: float | int) -> str:
    if not isinstance(s, str):
        raise TypeError(f"right() needs a string, not {describe_type(s)}")
    n = _require_whole_number(n, "right", "count")
    if n < 0:
        raise ValueError("right() needs a count that isn't negative")
    if n == 0:
        return ""
    return s[-n:]


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


# -- math (LANGUAGE_ROADMAP.md §1) -------------------------------------------


def leo_abs(n: float | int) -> float | int:
    return abs(_require_number(n, "abs"))


def leo_sqrt(n: float | int) -> float:
    n = _require_number(n, "sqrt")
    if n < 0:
        raise ValueError("sqrt() needs a number that isn't negative")
    return math.sqrt(n)


def leo_round(n: float | int, digits: float | int | None = None) -> float | int:
    n = _require_number(n, "round")
    if digits is None:
        return round(n)
    digits = _require_number(digits, "round")
    if isinstance(digits, bool) or not isinstance(digits, int):
        raise TypeError("round()'s digits value must be a whole number")
    return round(n, digits)


def leo_floor(n: float | int) -> int:
    return math.floor(_require_number(n, "floor"))


def leo_ceil(n: float | int) -> int:
    return math.ceil(_require_number(n, "ceil"))


def leo_min(*args: object) -> float | int:
    if len(args) == 1 and isinstance(args[0], list):
        items = args[0]
        if not items:
            raise ValueError("min() needs a non-empty list")
        return min(_require_number(v, "min") for v in items)
    if len(args) == 2:
        return min(_require_number(args[0], "min"), _require_number(args[1], "min"))
    raise TypeError("min() needs either two numbers or one list")


def leo_max(*args: object) -> float | int:
    if len(args) == 1 and isinstance(args[0], list):
        items = args[0]
        if not items:
            raise ValueError("max() needs a non-empty list")
        return max(_require_number(v, "max") for v in items)
    if len(args) == 2:
        return max(_require_number(args[0], "max"), _require_number(args[1], "max"))
    raise TypeError("max() needs either two numbers or one list")


def leo_sin(n: float | int) -> float:
    return math.sin(math.radians(_require_number(n, "sin")))


def leo_cos(n: float | int) -> float:
    return math.cos(math.radians(_require_number(n, "cos")))


def leo_tan(n: float | int) -> float:
    return math.tan(math.radians(_require_number(n, "tan")))


def leo_log(n: float | int) -> float:
    n = _require_number(n, "log")
    if n <= 0:
        raise ValueError("log() needs a number greater than 0")
    return math.log(n)


def leo_exp(n: float | int) -> float:
    return math.exp(_require_number(n, "exp"))


# -- randomness (LANGUAGE_ROADMAP.md §2) -------------------------------------


def leo_random() -> float:
    return random.random()


def leo_random_int(lo: float | int, hi: float | int) -> int:
    lo = _require_number(lo, "random_int")
    hi = _require_number(hi, "random_int")
    if isinstance(lo, bool) or not isinstance(lo, int):
        raise TypeError("random_int()'s min value must be a whole number")
    if isinstance(hi, bool) or not isinstance(hi, int):
        raise TypeError("random_int()'s max value must be a whole number")
    if lo > hi:
        raise ValueError("random_int()'s min value must not be greater than its max value")
    return random.randint(lo, hi)


def leo_shuffle(items: list) -> list:
    if not isinstance(items, list):
        raise TypeError(f"shuffle() needs a list, not {describe_type(items)}")
    shuffled = list(items)
    random.shuffle(shuffled)
    return shuffled


def leo_choice(items: list) -> object:
    if not isinstance(items, list):
        raise TypeError(f"choice() needs a list, not {describe_type(items)}")
    if not items:
        raise ValueError("choice() needs a non-empty list")
    return random.choice(items)


# Bare-identifier constants (not called with parens), seeded into the interpreter's
# global scope at startup — see Interpreter.__init__.
CONSTANTS = {
    "pi": math.pi,
}


BUILTINS = {
    "str": leo_str,
    "num": leo_num,
    "is_number": leo_is_number,
    "is_string": leo_is_string,
    "is_list": leo_is_list,
    "type_of": leo_type_of,
    "split": leo_split,
    "join": leo_join,
    "print": leo_print,
    "input": leo_input,
    "get_env": leo_get_env,
    "ascii": leo_ascii,
    "date": leo_date,
    "time": leo_time,
    "run_program": leo_run_program,
    "open_url": leo_open_url,
    "open_email": leo_open_email,
    "abs": leo_abs,
    "sqrt": leo_sqrt,
    "round": leo_round,
    "floor": leo_floor,
    "ceil": leo_ceil,
    "min": leo_min,
    "max": leo_max,
    "sin": leo_sin,
    "cos": leo_cos,
    "tan": leo_tan,
    "log": leo_log,
    "exp": leo_exp,
    "random": leo_random,
    "random_int": leo_random_int,
    "shuffle": leo_shuffle,
    "choice": leo_choice,
    "chr": leo_chr,
    "upper": leo_upper,
    "lower": leo_lower,
    "trim": leo_trim,
    "contains": leo_contains,
    "index_of": leo_index_of,
    "reverse": leo_reverse,
    "sort": leo_sort,
    "remove_at": leo_remove_at,
    "sum": leo_sum,
    "replace": leo_replace,
    "starts_with": leo_starts_with,
    "ends_with": leo_ends_with,
    "substring": leo_substring,
    "left": leo_left,
    "right": leo_right,
}

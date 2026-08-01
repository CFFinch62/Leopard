"""File builtins (GRAMMAR.md §12): write_file/read_file/append_file/delete_file/etc.

Same error convention as builtins_core.py: raise plain ValueError/OSError, let the
interpreter's call wrapper attach the source line.
"""

from __future__ import annotations

import os
import urllib.request

from .errors import describe_type


def write_file(path: str, text: str) -> None:
    _require_str(path, "path")
    _require_str(text, "text")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def append_file(path: str, text: str) -> None:
    _require_str(path, "path")
    _require_str(text, "text")
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)


def read_file(path: str) -> str:
    _require_str(path, "path")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"file '{path}' does not exist") from None


def delete_file(path: str) -> None:
    _require_str(path, "path")
    try:
        os.remove(path)
    except FileNotFoundError:
        raise ValueError(f"file '{path}' does not exist") from None


def make_dir(path: str) -> None:
    _require_str(path, "path")
    os.makedirs(path, exist_ok=True)


def remove_dir(path: str) -> None:
    _require_str(path, "path")
    try:
        os.rmdir(path)
    except FileNotFoundError:
        raise ValueError(f"directory '{path}' does not exist") from None
    except OSError:
        raise ValueError(f"directory '{path}' is not empty") from None


def file_exists(path: str) -> bool:
    _require_str(path, "path")
    return os.path.isfile(path)


def download_file(url: str, path: str) -> None:
    _require_str(url, "url")
    _require_str(path, "path")
    urllib.request.urlretrieve(url, path)


def _require_str(value: object, arg_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{arg_name} must be a string, not {describe_type(value)}")


BUILTINS = {
    "write_file": write_file,
    "append_file": append_file,
    "read_file": read_file,
    "delete_file": delete_file,
    "make_dir": make_dir,
    "remove_dir": remove_dir,
    "file_exists": file_exists,
    "download_file": download_file,
}

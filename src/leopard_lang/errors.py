"""Leopard error types: line number + plain-English message (GRAMMAR.md status #8)."""

from __future__ import annotations


class LeopardError(Exception):
    def __init__(self, line: int, message: str):
        self.line = line
        self.message = message
        super().__init__(f"Line {line}: {message}")


class LeopardSyntaxError(LeopardError):
    """Raised by the lexer or parser on malformed source."""


class LeopardRuntimeError(LeopardError):
    """Raised by the interpreter during execution (Phase 3)."""


def describe_type(value: object) -> str:
    """User-facing type name for runtime error messages — shared by interpreter.py
    and the builtins modules (kept here, not in interpreter.py, to avoid a cycle)."""
    if isinstance(value, bool):
        return "a boolean"
    if isinstance(value, (int, float)):
        return "a number"
    if isinstance(value, str):
        return "a string"
    if isinstance(value, list):
        return "a list"
    if value is None:
        return "nothing"
    return type(value).__name__

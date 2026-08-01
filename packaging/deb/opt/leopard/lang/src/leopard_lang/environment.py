"""Variable scoping (GRAMMAR.md §3): module scope + one scope per function call.

"Ordinary Python-like scoping" with no nested function declarations means only two
levels ever exist. Assignment always creates/updates a variable in the *current*
scope (GRAMMAR.md: "scoped to the function/handler it's assigned in") — there's no
`global` keyword, so a function can read a module-level variable but never write one
by plain assignment. Reads fall through to the parent scope when not found locally.
"""

from __future__ import annotations

from typing import Any, Optional

from .errors import LeopardRuntimeError


class Environment:
    def __init__(self, parent: Optional["Environment"] = None):
        self.parent = parent
        self.values: dict[str, Any] = {}

    def get(self, name: str, line: int) -> Any:
        env: Optional["Environment"] = self
        while env is not None:
            if name in env.values:
                return env.values[name]
            env = env.parent
        raise LeopardRuntimeError(line, f"'{name}' is not defined")

    def set(self, name: str, value: Any) -> None:
        self.values[name] = value

    def has(self, name: str) -> bool:
        env: Optional["Environment"] = self
        while env is not None:
            if name in env.values:
                return True
            env = env.parent
        return False

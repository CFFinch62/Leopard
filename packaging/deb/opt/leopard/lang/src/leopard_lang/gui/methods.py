"""Method-call dispatch for GUI controls (GRAMMAR.md §10, Phase 13).

Plugs into `Interpreter.gui_methods` — see interpreter.py's `_eval_Call`. Mirrors
`properties.py`'s `PropertyDispatcher` shape exactly, just for `receiver.method(args)`
calls instead of `.property` get/set. Today the only control with methods (rather than
properties) is a `graphics` control's turtle-canvas — `build_turtle_builtins(canvas)`
(turtle_canvas.py) already builds exactly the name->bound-method dict this dispatcher
needs, so it's reused unchanged as the method registry.
"""

from __future__ import annotations

from typing import Any

from ..errors import LeopardRuntimeError
from .turtle_canvas import TurtleCanvas, build_turtle_builtins


class MethodDispatcher:
    def is_gui_object(self, obj: Any) -> bool:
        return isinstance(obj, TurtleCanvas)

    def call(self, obj: TurtleCanvas, name: str, args: list, line: int) -> Any:
        methods = build_turtle_builtins(obj)
        fn = methods.get(name)
        if fn is None:
            raise LeopardRuntimeError(line, f"'.{name}()' is not a recognized method for this control")
        try:
            return fn(*args)
        except LeopardRuntimeError:
            raise
        except TypeError as exc:
            if "positional argument" in str(exc) or "argument" in str(exc):
                raise LeopardRuntimeError(line, f"'.{name}()' called with the wrong number of arguments") from exc
            raise LeopardRuntimeError(line, str(exc)) from exc
        except (ValueError, OSError) as exc:
            raise LeopardRuntimeError(line, str(exc)) from exc

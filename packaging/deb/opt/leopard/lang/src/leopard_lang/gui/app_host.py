"""QApplication lifecycle: own one when run standalone, reuse one when hosted.

This is the one mechanism `leopard run` (Phase 4, standalone) and the eventual IDE
integration (Phase 9) share, so GUI-runtime code never needs to know which is hosting
it — pass `existing_app=None` (or omit it) to own the loop; pass an app to reuse one.
"""

from __future__ import annotations

import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication

from .. import ast_nodes as ast
from ..errors import LeopardRuntimeError
from ..interpreter import Interpreter
from .dialogs import build_gui_builtins
from .properties import PropertyDispatcher
from .sound import build_sound_builtins
from .text_page import create_text_page
from .turtle_canvas import TurtleCanvas, build_turtle_builtins
from .window_builder import LeopardWindow, build_window_body


def run_window(program: ast.Program, *, existing_app: Optional[QApplication] = None) -> LeopardWindow:
    if program.window is None:
        raise LeopardRuntimeError(0, "run_window() needs a program with a window header")

    owns_app = existing_app is None
    app = existing_app if existing_app is not None else QApplication(sys.argv)

    window_decl = program.window
    window = LeopardWindow()
    window.setWindowTitle(window_decl.title)
    window.resize(int(window_decl.width), int(window_decl.height))

    interpreter = Interpreter(gui_properties=PropertyDispatcher())
    interpreter.gui_builtins = build_gui_builtins(window)
    interpreter.gui_builtins.update(build_sound_builtins(window))
    interpreter.globals.set("window", window)

    if window_decl.kind == "graphics_window":
        canvas = TurtleCanvas(int(window_decl.width), int(window_decl.height), parent=window)
        canvas.show()
        interpreter.gui_builtins.update(build_turtle_builtins(canvas))
    elif window_decl.kind == "text_window":
        page = create_text_page(int(window_decl.width), int(window_decl.height), parent=window)
        page.show()
        interpreter.globals.set("page", page)

    build_window_body(window_decl, interpreter, interpreter.globals, window)

    window.show()

    if owns_app:
        app.exec()

    return window

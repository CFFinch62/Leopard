"""Control-declaration AST -> QWidget tree, and the window body walk (GRAMMAR.md §7, §8).

Reaches into a few of `Interpreter`'s underscore-prefixed methods (`_eval`,
`_exec`, `_exec_block`) directly — `gui/` is part of the same package as
`interpreter.py`, not a separate consumer, so this is an internal implementation
detail rather than a public API concern.
"""

from __future__ import annotations

from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QWidget,
)

from .. import ast_nodes as ast
from ..environment import Environment
from ..errors import LeopardRuntimeError, describe_type
from ..interpreter import Interpreter
from . import events as gui_events
from . import menus as gui_menus
from .turtle_canvas import TurtleCanvas


class LeopardWindow(QWidget):
    """Absolute-positioned top-level container (controls use `at x, y, w, h`, not
    a layout manager — matches the original BASIC's positioning style)."""

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 (Qt's naming)
        on_close = getattr(self, "_leo_on_close", None)
        if on_close is not None:
            stmt, interpreter, env = on_close
            interpreter._exec_block(stmt.body, env)
        event.accept()


def _make_bmpbutton(caption: str | None, w: int, h: int) -> QPushButton:
    button = QPushButton()
    if caption:
        button.setIcon(QIcon(caption))
    return button


# Every factory takes (caption, w, h) uniformly, even though only "graphics" needs
# w/h — a TurtleCanvas sizes its drawing surface and turtle home position from its
# constructor args (turtle_canvas.py), so it must be built at its final size rather
# than resized afterward the way every other control's QWidget can be.
_CONTROL_FACTORIES = {
    "textbox": lambda caption, w, h: QLineEdit(),
    "textedit": lambda caption, w, h: QTextEdit(),
    "label": lambda caption, w, h: QLabel(caption or ""),
    "button": lambda caption, w, h: QPushButton(caption or ""),
    "bmpbutton": _make_bmpbutton,
    "listbox": lambda caption, w, h: QListWidget(),
    "combobox": lambda caption, w, h: QComboBox(),
    "radiobutton": lambda caption, w, h: QRadioButton(caption or ""),
    "checkbox": lambda caption, w, h: QCheckBox(caption or ""),
    "groupbox": lambda caption, w, h: QGroupBox(caption or ""),
    "graphics": lambda caption, w, h: TurtleCanvas(int(w), int(h)),
}


def _eval_geometry_number(interpreter: Interpreter, expr: ast.Expr, env: Environment, line: int, where: str):
    value = interpreter._eval(expr, env)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LeopardRuntimeError(line, f"{where} needs a number, not {describe_type(value)}")
    return value


def build_control(
    decl: ast.ControlDecl,
    interpreter: Interpreter,
    env: Environment,
    parent: QWidget,
    y_offset: int = 0,
) -> QWidget:
    factory = _CONTROL_FACTORIES.get(decl.kind)
    if factory is None:
        raise LeopardRuntimeError(decl.line, f"unknown control kind '{decl.kind}'")

    x = _eval_geometry_number(interpreter, decl.x, env, decl.line, "a control's x position")
    y = _eval_geometry_number(interpreter, decl.y, env, decl.line, "a control's y position")
    w = _eval_geometry_number(interpreter, decl.w, env, decl.line, "a control's width")
    h = _eval_geometry_number(interpreter, decl.h, env, decl.line, "a control's height")

    widget = factory(decl.caption, w, h)
    widget.setParent(parent)
    widget.setGeometry(int(x), int(y) + y_offset, int(w), int(h))
    widget.show()

    env.set(decl.name, widget)
    return widget


def build_window_body(
    window_decl: ast.WindowDecl, interpreter: Interpreter, env: Environment, container: QWidget
) -> None:
    """Walk a window's body once: hoist functions, build controls, wire events, and
    run any other plain statement immediately (ordinary window "setup" code).

    A menu bar (if any) is built first and claims its own horizontal strip at the
    top: every `at x, y, w, h` control below is shifted down by the menu bar's
    height, and the window grows by that same amount, so a script's declared
    `y` values always mean "position within the workspace under the menu" -
    the same regardless of whether a menu is present, and regardless of where
    in the window body the `menu` block happens to be written.
    """
    for stmt in window_decl.body:
        if isinstance(stmt, ast.FunctionDecl):
            interpreter.functions[stmt.name] = stmt

    menu_decls = [stmt for stmt in window_decl.body if isinstance(stmt, ast.MenuDecl)]
    y_offset = 0
    if menu_decls:
        menubar = gui_menus.build_menu_bar(menu_decls, env, container)
        y_offset = menubar.height()
        container.resize(container.width(), container.height() + y_offset)

    for stmt in window_decl.body:
        if isinstance(stmt, ast.FunctionDecl) or isinstance(stmt, ast.MenuDecl):
            continue  # hoisted / already built above
        if isinstance(stmt, ast.ControlDecl):
            build_control(stmt, interpreter, env, container, y_offset=y_offset)
        elif isinstance(stmt, ast.EventHandler):
            if stmt.event == "close":
                container._leo_on_close = (stmt, interpreter, env)
            else:
                gui_events.wire_event_handler(stmt, interpreter, env)
        else:
            interpreter._exec(stmt, env)

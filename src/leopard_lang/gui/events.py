"""`on click`/`change`/`select` -> Qt signal wiring (GRAMMAR.md §9).

Targets are either a control widget or, since Phase 5, a menu `item`/`checkitem`
`QAction` (GRAMMAR.md §8) — an item's `on click` and a checkitem's `on change` work
the same way a button's/checkbox's do, just on a different Qt class. Since Phase 7,
`on change page` (GRAMMAR.md §11) works the same way too — `page` is just a QTextEdit,
same as `textedit`, so `on change` fires on its `textChanged` signal.

`on close` has no target widget (it's window-level) and is handled separately by
`window_builder.LeopardWindow.closeEvent`, not here.
"""

from __future__ import annotations

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QCheckBox, QComboBox, QListWidget, QPushButton, QRadioButton, QTextEdit

from .. import ast_nodes as ast
from ..environment import Environment
from ..errors import LeopardRuntimeError
from ..interpreter import Interpreter


def wire_event_handler(handler: ast.EventHandler, interpreter: Interpreter, env: Environment) -> None:
    if handler.target is None:
        raise LeopardRuntimeError(handler.line, f"'on {handler.event}' needs a control name")
    if not env.has(handler.target):
        raise LeopardRuntimeError(handler.line, f"'{handler.target}' is not a declared control")
    target = env.get(handler.target, handler.line)

    def run_handler(*_qt_args: object) -> None:
        interpreter._exec_block(handler.body, env)

    if handler.event == "click":
        if isinstance(target, (QPushButton, QAction)):
            (target.clicked if isinstance(target, QPushButton) else target.triggered).connect(run_handler)
        else:
            raise LeopardRuntimeError(handler.line, "'on click' needs a button or menu item")
    elif handler.event == "change":
        if isinstance(target, (QCheckBox, QRadioButton)) or (
            isinstance(target, QAction) and target.isCheckable()
        ):
            target.toggled.connect(run_handler)
        elif isinstance(target, QComboBox):
            target.currentIndexChanged.connect(run_handler)
        elif isinstance(target, QTextEdit):
            target.textChanged.connect(run_handler)
        else:
            raise LeopardRuntimeError(
                handler.line,
                "'on change' needs a checkbox, radiobutton, combobox, checkitem, or page/textedit",
            )
    elif handler.event == "select":
        if isinstance(target, QListWidget):
            target.itemSelectionChanged.connect(run_handler)
        elif isinstance(target, QComboBox):
            target.currentIndexChanged.connect(run_handler)
        else:
            raise LeopardRuntimeError(handler.line, "'on select' needs a listbox or combobox")
    else:
        raise LeopardRuntimeError(handler.line, f"'on {handler.event}' is not supported here")

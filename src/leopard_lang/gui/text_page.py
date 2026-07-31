"""Binds the reserved `page` identifier to a full-window `QTextEdit` (GRAMMAR.md §11).

`page` is just an ordinarily-registered environment name pointing at a QTextEdit —
`.text` get/set (`properties.py`) and `on change`/`on close` wiring (`events.py`,
`window_builder.LeopardWindow.closeEvent`) already handle a QTextEdit/window-level
event generically, since GRAMMAR.md §11 deliberately reuses the ordinary control and
event vocabulary rather than inventing `page`-specific syntax. Nothing page-specific
is needed here beyond creating and sizing it to fill the window.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QTextEdit, QWidget


def create_text_page(width: int, height: int, parent: QWidget) -> QTextEdit:
    page = QTextEdit(parent)
    page.setGeometry(0, 0, width, height)
    return page

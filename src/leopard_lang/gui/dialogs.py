"""notice/confirm/ask, file/color/font dialogs, and close/maximize/minimize_window
(GRAMMAR.md §12) — bound to one specific window instance, since Leopard only ever
has the one window per program.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QColorDialog, QFileDialog, QFontDialog, QInputDialog, QMessageBox, QWidget


def build_gui_builtins(window: QWidget) -> dict:
    def notice(message: str) -> None:
        QMessageBox.information(window, "Notice", str(message))

    def confirm(message: str) -> bool:
        result = QMessageBox.question(window, "Confirm", str(message))
        return result == QMessageBox.StandardButton.Yes

    def ask(prompt: str) -> str:
        text, ok = QInputDialog.getText(window, "Input", str(prompt))
        return text if ok else ""

    def open_file_dialog() -> str:
        path, _selected_filter = QFileDialog.getOpenFileName(window)
        return path

    def save_file_dialog() -> str:
        path, _selected_filter = QFileDialog.getSaveFileName(window)
        return path

    def color_dialog() -> str:
        color = QColorDialog.getColor()
        return color.name() if color.isValid() else ""

    def font_dialog() -> str:
        font, ok = QFontDialog.getFont()
        return font.family() if ok else ""

    def close_window() -> None:
        window.close()

    def maximize_window() -> None:
        window.showMaximized()

    def minimize_window() -> None:
        window.showMinimized()

    return {
        "notice": notice,
        "confirm": confirm,
        "ask": ask,
        "open_file_dialog": open_file_dialog,
        "save_file_dialog": save_file_dialog,
        "color_dialog": color_dialog,
        "font_dialog": font_dialog,
        "close_window": close_window,
        "maximize_window": maximize_window,
        "minimize_window": minimize_window,
    }

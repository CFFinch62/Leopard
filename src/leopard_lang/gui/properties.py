"""Property get/set dispatch for GUI controls (GRAMMAR.md §7).

Plugs into `Interpreter.gui_properties` — see interpreter.py's `_eval_PropertyAccess`
and `_exec_PropertyAssignment`. `.color`/`.background` are implemented via a small
per-widget stylesheet cache (a plain ad-hoc attribute on the widget instance) so
setting one doesn't clobber the other — Qt stylesheets are just one string per widget.
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import QComboBox, QListWidget, QTextEdit, QWidget

from ..errors import LeopardRuntimeError, describe_type
from .turtle_canvas import TurtleCanvas


class ListboxItems(list):
    """Live view of a listbox/combobox's items.

    A `list` subclass so the interpreter's existing generic `.add()` handling
    (`isinstance(obj, list)` + `obj.append(...)`) and `.length`/indexing all just
    work — only `append()` is overridden, to also push the new item into the widget.
    """

    def __init__(self, widget: QWidget):
        super().__init__(_get_items(widget))
        self._widget = widget

    def append(self, value: object) -> None:
        text = str(value)
        super().append(text)
        self._widget.addItem(text)


def _get_items(widget: QWidget) -> list:
    if isinstance(widget, QListWidget):
        return [widget.item(i).text() for i in range(widget.count())]
    if isinstance(widget, QComboBox):
        return [widget.itemText(i) for i in range(widget.count())]
    raise ValueError("'.items' needs a listbox or combobox")


def _set_items(widget: QWidget, items: list) -> None:
    if not isinstance(widget, (QListWidget, QComboBox)):
        raise ValueError("'.items' needs a listbox or combobox")
    widget.clear()
    for item in items:
        widget.addItem(str(item))


def _selected_get(widget: QWidget) -> int:
    if isinstance(widget, QListWidget):
        row = widget.currentRow()
    elif isinstance(widget, QComboBox):
        row = widget.currentIndex()
    else:
        raise ValueError("'.selected' needs a listbox or combobox")
    return row + 1 if row >= 0 else 0


def _selected_set(widget: QWidget, value: int) -> None:
    row = value - 1 if value >= 1 else -1
    if isinstance(widget, QListWidget):
        widget.setCurrentRow(row)
    elif isinstance(widget, QComboBox):
        widget.setCurrentIndex(row)
    else:
        raise ValueError("'.selected' needs a listbox or combobox")


def _text_get(widget: QWidget) -> str:
    if isinstance(widget, QTextEdit):
        return widget.toPlainText()
    return widget.text()


def _text_set(widget: QWidget, value: str) -> None:
    if isinstance(widget, QTextEdit):
        widget.setPlainText(value)
    else:
        widget.setText(value)


def _mouse_pos_get(widget: QWidget, axis: str) -> int:
    if not isinstance(widget, TurtleCanvas):
        raise ValueError(f"'.{axis}' needs a graphics control")
    return getattr(widget, axis)


def _style_state(widget: QWidget) -> dict:
    style = getattr(widget, "_leo_style", None)
    if style is None:
        style = {}
        widget._leo_style = style
    return style


def _set_style_prop(widget: QWidget, css_key: str, value: str) -> None:
    style = _style_state(widget)
    style[css_key] = value
    widget.setStyleSheet("; ".join(f"{k}: {v}" for k, v in style.items()))


_GETTERS = {
    "text": _text_get,
    "color": lambda w: _style_state(w).get("color", ""),
    "background": lambda w: _style_state(w).get("background-color", ""),
    "font": lambda w: w.font().family(),
    "checked": lambda w: w.isChecked(),
    "items": ListboxItems,
    "selected": _selected_get,
    "visible": lambda w: w.isVisible(),
    "enabled": lambda w: w.isEnabled(),
    "title": lambda w: w.windowTitle(),
    "mouse_x": lambda w: _mouse_pos_get(w, "mouse_x"),
    "mouse_y": lambda w: _mouse_pos_get(w, "mouse_y"),
}

_READ_ONLY_PROPS = {"mouse_x", "mouse_y"}

_SETTERS = {
    "text": _text_set,
    "color": lambda w, v: _set_style_prop(w, "color", v),
    "background": lambda w, v: _set_style_prop(w, "background-color", v),
    "font": lambda w, v: w.setFont(QFont(v)),
    "checked": lambda w, v: w.setChecked(v),
    "items": _set_items,
    "selected": _selected_set,
    "visible": lambda w, v: w.setVisible(v),
    "enabled": lambda w, v: w.setEnabled(v),
    "title": lambda w, v: w.setWindowTitle(v),
}

_STRING_PROPS = {"text", "color", "background", "font", "title"}
_BOOL_PROPS = {"checked", "visible", "enabled"}


class PropertyDispatcher:
    def is_gui_object(self, obj: Any) -> bool:
        # QAction (menu items/checkitems, GRAMMAR.md §8) isn't a QWidget in Qt —
        # it's the one non-widget object this dispatcher needs to recognize.
        return isinstance(obj, (QWidget, QAction))

    def get(self, widget: QWidget, name: str, line: int) -> Any:
        getter = _GETTERS.get(name)
        if getter is None:
            raise LeopardRuntimeError(line, f"'.{name}' is not a recognized property")
        try:
            return getter(widget)
        except ValueError as exc:
            raise LeopardRuntimeError(line, str(exc)) from exc

    def set(self, widget: QWidget, name: str, value: Any, line: int) -> None:
        if name in _READ_ONLY_PROPS:
            raise LeopardRuntimeError(line, f"'.{name}' is read-only")
        setter = _SETTERS.get(name)
        if setter is None:
            raise LeopardRuntimeError(line, f"'.{name}' is not a recognized property")
        if name in _STRING_PROPS and not isinstance(value, str):
            raise LeopardRuntimeError(line, f"'.{name}' needs a string, not {describe_type(value)}")
        if name in _BOOL_PROPS and not isinstance(value, bool):
            raise LeopardRuntimeError(line, f"'.{name}' needs true/false, not {describe_type(value)}")
        if name == "selected" and (isinstance(value, bool) or not isinstance(value, int)):
            raise LeopardRuntimeError(line, "'.selected' needs a whole number")
        if name == "items" and not isinstance(value, list):
            raise LeopardRuntimeError(line, f"'.items' needs a list, not {describe_type(value)}")
        try:
            setter(widget, value)
        except ValueError as exc:
            raise LeopardRuntimeError(line, str(exc)) from exc

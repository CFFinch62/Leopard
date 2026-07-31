"""`menu`/`item`/`checkitem`/`submenu`/`separator` -> QMenuBar/QMenu/QAction tree
(GRAMMAR.md §8). Works the same regardless of window kind (`window`, `text window`,
or `graphics window`) — the caller just passes whatever top-level container it has.

Every `QMenu` is constructed with an explicit Qt parent (the menubar, or the parent
menu for a submenu) — without one, Qt's C++ side doesn't keep the Python wrapper
alive, and `addMenu()` alone isn't enough to stop it being garbage-collected out
from under the menu bar (a well-known PyQt/PySide gotcha, confirmed by hand here:
omitting `parent` silently leaves `menubar.actions()` empty).

Qt honors `&`-accelerators in QAction/QMenu text natively; nothing extra is needed
for that here (verified in `tests/test_menus.py`, not just assumed).
"""

from __future__ import annotations

from typing import Union

from PyQt6.QtWidgets import QMenu, QMenuBar, QWidget

from .. import ast_nodes as ast
from ..environment import Environment

_MenuOrSubmenu = Union[ast.MenuDecl, ast.SubmenuDecl]


def build_menu_bar(menu_decls: list[ast.MenuDecl], env: Environment, parent: QWidget) -> QMenuBar:
    menubar = QMenuBar(parent)
    for decl in menu_decls:
        menu = _build_menu(decl, env, parent=menubar)
        menubar.addMenu(menu)
        env.set(decl.name, menu)
    menubar.setGeometry(0, 0, parent.width(), menubar.sizeHint().height())
    menubar.show()
    return menubar


def _build_menu(decl: _MenuOrSubmenu, env: Environment, parent: QWidget) -> QMenu:
    menu = QMenu(decl.title, parent)
    for item in decl.body:
        _add_menu_item(menu, item, env)
    return menu


def _add_menu_item(menu: QMenu, item: ast.MenuItem, env: Environment) -> None:
    if isinstance(item, ast.Separator):
        menu.addSeparator()
    elif isinstance(item, ast.ItemDecl):
        action = menu.addAction(item.title)
        env.set(item.name, action)
    elif isinstance(item, ast.CheckItemDecl):
        action = menu.addAction(item.title)
        action.setCheckable(True)
        env.set(item.name, action)
    elif isinstance(item, ast.SubmenuDecl):
        submenu = _build_menu(item, env, parent=menu)
        menu.addMenu(submenu)
        env.set(item.name, submenu)

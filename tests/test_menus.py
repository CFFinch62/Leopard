import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
from PyQt6.QtGui import QAction  # noqa: E402
from PyQt6.QtWidgets import QApplication, QCheckBox, QLabel, QMenuBar, QTextEdit  # noqa: E402

from leopard_lang.gui.app_host import run_window  # noqa: E402
from leopard_lang.lexer import tokenize  # noqa: E402
from leopard_lang.parser import parse  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


def build(qapp, source: str):
    program = parse(tokenize(source))
    return run_window(program, existing_app=qapp)


def menu_bar_of(window) -> QMenuBar:
    return window.findChild(QMenuBar)


# ---------------------------------------------------------------------------
# Tree structure (GRAMMAR.md §8), including nested submenu + separator
# ---------------------------------------------------------------------------


FILE_VIEW_MENU_SRC = (
    'window "Editor", 500, 400:\n'
    '\n'
    '    menu "&File" as fileMenu:\n'
    '        item "&New..." as mnuNew\n'
    '        item "&Open..." as mnuOpen\n'
    '        separator\n'
    '        submenu "Open &Recent" as mnuRecent:\n'
    '            item "report.lep" as mnuRecent1\n'
    '        separator\n'
    '        item "E&xit" as mnuExit\n'
    '\n'
    '    menu "&View" as viewMenu:\n'
    '        checkitem "Show &Toolbar" as mnuToolbar\n'
)


def test_two_top_level_menus_built(qapp):
    window = build(qapp, FILE_VIEW_MENU_SRC)
    menubar = menu_bar_of(window)
    titles = [action.menu().title() for action in menubar.actions()]
    assert titles == ["&File", "&View"]


def test_menu_item_order_separators_and_submenu(qapp):
    window = build(qapp, FILE_VIEW_MENU_SRC)
    file_menu = menu_bar_of(window).actions()[0].menu()
    actions = file_menu.actions()

    assert actions[0].text() == "&New..."
    assert actions[1].text() == "&Open..."
    assert actions[2].isSeparator()
    assert actions[3].text() == "Open &Recent"
    assert actions[3].menu() is not None
    assert actions[4].isSeparator()
    assert actions[5].text() == "E&xit"

    submenu_items = actions[3].menu().actions()
    assert [a.text() for a in submenu_items] == ["report.lep"]


def test_accelerator_text_is_preserved_natively(qapp):
    # Qt's own mnemonic handling should keep the literal '&' in .text() — verify,
    # don't assume (GRAMMAR.md's Phase 5 checklist item).
    window = build(qapp, FILE_VIEW_MENU_SRC)
    file_menu_action = menu_bar_of(window).actions()[0]
    assert file_menu_action.menu().title() == "&File"
    new_item = file_menu_action.menu().actions()[0]
    assert new_item.text() == "&New..."


def test_checkitem_is_checkable(qapp):
    window = build(qapp, FILE_VIEW_MENU_SRC)
    view_menu = menu_bar_of(window).actions()[1].menu()
    (toolbar_item,) = view_menu.actions()
    assert isinstance(toolbar_item, QAction)
    assert toolbar_item.isCheckable()
    assert toolbar_item.isChecked() is False


# ---------------------------------------------------------------------------
# Properties + events on menu items/checkitems
# ---------------------------------------------------------------------------


def test_checkitem_checked_property_via_leopard(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    menu "&View" as viewMenu:\n'
        '        checkitem "Show" as mnuShow\n'
        "    mnuShow.checked = true\n",
    )
    (item,) = menu_bar_of(window).actions()[0].menu().actions()
    assert item.isChecked() is True


def test_item_on_click_runs_handler(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    label "" as resultLabel at 0, 0, 100, 20\n'
        '    menu "&File" as fileMenu:\n'
        '        item "&New..." as mnuNew\n'
        "\n"
        "    on click mnuNew:\n"
        '        resultLabel.text = "new clicked"\n',
    )
    (label,) = window.findChildren(QLabel)
    (item,) = menu_bar_of(window).actions()[0].menu().actions()
    item.trigger()
    assert label.text() == "new clicked"


def test_checkitem_on_change_runs_handler(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    checkbox "" as toolbar at 0, 0, 10, 10\n'
        '    menu "&View" as viewMenu:\n'
        '        checkitem "Show &Toolbar" as mnuToolbar\n'
        "\n"
        "    on change mnuToolbar:\n"
        "        toolbar.visible = mnuToolbar.checked\n",
    )
    (toolbar,) = window.findChildren(QCheckBox)
    (item,) = menu_bar_of(window).actions()[0].menu().actions()

    item.trigger()  # False -> True
    assert toolbar.isVisible() is True
    item.trigger()  # True -> False
    assert toolbar.isVisible() is False


def test_item_on_click_can_close_window(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    menu "&File" as fileMenu:\n'
        '        item "E&xit" as mnuExit\n'
        "\n"
        "    on click mnuExit:\n"
        "        close_window()\n",
    )
    (item,) = menu_bar_of(window).actions()[0].menu().actions()
    assert window.isVisible()
    item.trigger()
    assert not window.isVisible()


# ---------------------------------------------------------------------------
# Menus attach the same way in all three window kinds (GRAMMAR.md §8, Phase 5's
# Definition of Done)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "header",
    [
        'window "W", 300, 300:',
        'text window "W", 300, 300:',
        'graphics window "W", 300, 300:',
    ],
)
def test_menu_attaches_in_every_window_kind(qapp, header):
    source = f'{header}\n    menu "&File" as fileMenu:\n        item "&New..." as mnuNew\n'
    window = build(qapp, source)
    menubar = menu_bar_of(window)
    assert menubar is not None
    assert [a.menu().title() for a in menubar.actions()] == ["&File"]


# ---------------------------------------------------------------------------
# Full GRAMMAR.md §8 example, standalone (no IDE)
# ---------------------------------------------------------------------------


def test_grammar_section_8_example_end_to_end(qapp):
    source = (
        'window "Editor", 500, 400:\n'
        "\n"
        '    textedit as editorBox at 0, 20, 500, 380\n'
        '    checkbox "" as toolbar at 0, 0, 10, 10\n'
        "\n"
        '    menu "&File" as fileMenu:\n'
        '        item "&New..." as mnuNew\n'
        '        item "&Open..." as mnuOpen\n'
        "        separator\n"
        '        submenu "Open &Recent" as mnuRecent:\n'
        '            item "report.lep" as mnuRecent1\n'
        "        separator\n"
        '        item "E&xit" as mnuExit\n'
        "\n"
        '    menu "&View" as viewMenu:\n'
        '        checkitem "Show &Toolbar" as mnuToolbar\n'
        "\n"
        "    on click mnuNew:\n"
        '        editorBox.text = ""\n'
        "\n"
        "    on click mnuExit:\n"
        "        close_window()\n"
        "\n"
        "    on change mnuToolbar:\n"
        "        toolbar.visible = mnuToolbar.checked\n"
    )
    window = build(qapp, source)
    (editor_box,) = window.findChildren(QTextEdit)
    (toolbar,) = window.findChildren(QCheckBox)
    file_menu = menu_bar_of(window).actions()[0].menu()
    view_menu = menu_bar_of(window).actions()[1].menu()

    editor_box.setPlainText("some text")
    new_action = file_menu.actions()[0]
    new_action.trigger()
    assert editor_box.toPlainText() == ""

    toolbar_action = view_menu.actions()[0]
    toolbar_action.trigger()
    assert toolbar.isVisible() is True

    exit_action = file_menu.actions()[5]
    assert window.isVisible()
    exit_action.trigger()
    assert not window.isVisible()

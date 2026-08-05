import pathlib

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
from PyQt6.QtWidgets import (  # noqa: E402
    QApplication,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QRadioButton,
    QTextEdit,
)

from PyQt6.QtCore import QEvent, QPointF, Qt  # noqa: E402
from PyQt6.QtGui import QMouseEvent  # noqa: E402

from leopard_lang.errors import LeopardRuntimeError  # noqa: E402
from leopard_lang.gui.app_host import run_window  # noqa: E402
from leopard_lang.gui.turtle_canvas import TurtleCanvas  # noqa: E402
from leopard_lang.lexer import tokenize  # noqa: E402
from leopard_lang.parser import parse  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


def build(qapp, source: str):
    program = parse(tokenize(source))
    window = run_window(program, existing_app=qapp)
    return window


# ---------------------------------------------------------------------------
# Control declarations -> QWidget mapping
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "decl, widget_type",
    [
        ('textbox as c at 0, 0, 100, 20', QLineEdit),
        ('textedit as c at 0, 0, 100, 20', QTextEdit),
        ('label "hi" as c at 0, 0, 100, 20', QLabel),
        ('button "Go" as c at 0, 0, 100, 20', QPushButton),
        ('listbox as c at 0, 0, 100, 20', QListWidget),
        ('combobox as c at 0, 0, 100, 20', QComboBox),
        ('radiobutton "R" as c at 0, 0, 100, 20', QRadioButton),
        ('checkbox "C" as c at 0, 0, 100, 20', QCheckBox),
        ('groupbox "G" as c at 0, 0, 100, 20', QGroupBox),
    ],
)
def test_control_maps_to_correct_widget_type(qapp, decl, widget_type):
    window = build(qapp, f'window "W", 200, 200:\n    {decl}\n')
    assert len(window.findChildren(widget_type)) == 1


def test_control_geometry_and_caption(qapp):
    window = build(qapp, 'window "W", 200, 200:\n    button "Greet" as btn at 10, 20, 80, 24\n')
    (btn,) = window.findChildren(QPushButton)
    assert btn.text() == "Greet"
    assert (btn.x(), btn.y(), btn.width(), btn.height()) == (10, 20, 80, 24)


def test_control_registered_by_name_in_environment(qapp):
    program = parse(tokenize('window "W", 200, 200:\n    textbox as nameBox at 0, 0, 100, 20\n'))
    window = run_window(program, existing_app=qapp)
    assert isinstance(window.findChildren(QLineEdit)[0], QLineEdit)


# ---------------------------------------------------------------------------
# Properties (GRAMMAR.md §7)
# ---------------------------------------------------------------------------


def test_text_property_get_and_set(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    textbox as nameBox at 0, 0, 100, 20\n'
        '    nameBox.text = "hello"\n'
        "    result = nameBox.text\n",
    )
    (box,) = window.findChildren(QLineEdit)
    assert box.text() == "hello"


def test_color_and_background_do_not_clobber_each_other(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    label "x" as lbl at 0, 0, 100, 20\n'
        '    lbl.color = "red"\n'
        '    lbl.background = "blue"\n',
    )
    (lbl,) = window.findChildren(QLabel)
    style = lbl.styleSheet()
    assert "color: red" in style
    assert "background-color: blue" in style


def test_checked_property(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    checkbox "C" as chk at 0, 0, 100, 20\n'
        "    chk.checked = true\n",
    )
    (chk,) = window.findChildren(QCheckBox)
    assert chk.isChecked() is True


def test_items_property_set_and_add(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    listbox as fruitList at 0, 0, 100, 20\n'
        '    fruitList.items = ["Apple", "Banana"]\n'
        '    fruitList.items.add("Cherry")\n',
    )
    (listbox,) = window.findChildren(QListWidget)
    items = [listbox.item(i).text() for i in range(listbox.count())]
    assert items == ["Apple", "Banana", "Cherry"]


def test_items_length(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    listbox as fruitList at 0, 0, 100, 20\n'
        '    fruitList.items = ["Apple", "Banana"]\n'
        '    n = fruitList.items.length\n',
    )
    (listbox,) = window.findChildren(QListWidget)
    assert listbox.count() == 2


def test_selected_property_is_one_based(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    listbox as fruitList at 0, 0, 100, 20\n'
        '    fruitList.items = ["Apple", "Banana"]\n'
        "    fruitList.selected = 2\n",
    )
    (listbox,) = window.findChildren(QListWidget)
    assert listbox.currentRow() == 1  # 0-based internally


def test_visible_and_enabled_properties(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    button "B" as btn at 0, 0, 100, 20\n'
        "    btn.enabled = false\n",
    )
    (btn,) = window.findChildren(QPushButton)
    assert btn.isEnabled() is False


def test_window_title_property(qapp):
    window = build(qapp, 'window "Original", 200, 200:\n    window.title = "Changed"\n')
    assert window.windowTitle() == "Changed"


def test_property_wrong_type_is_runtime_error(qapp):
    with pytest.raises(LeopardRuntimeError, match="needs a string"):
        build(qapp, 'window "W", 200, 200:\n    button "B" as btn at 0, 0, 100, 20\n    btn.text = 5\n')


# ---------------------------------------------------------------------------
# Events (GRAMMAR.md §9)
# ---------------------------------------------------------------------------


def test_on_click_runs_handler_body(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    label "" as resultLabel at 0, 0, 100, 20\n'
        '    button "Go" as btnGo at 0, 30, 100, 20\n'
        "\n"
        "    on click btnGo:\n"
        '        resultLabel.text = "clicked"\n',
    )
    (label,) = window.findChildren(QLabel)
    (btn,) = window.findChildren(QPushButton)
    assert label.text() == ""
    btn.click()
    assert label.text() == "clicked"


def test_on_change_checkbox(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    label "" as resultLabel at 0, 0, 100, 20\n'
        '    checkbox "C" as chk at 0, 30, 100, 20\n'
        "\n"
        "    on change chk:\n"
        '        resultLabel.text = "changed"\n',
    )
    (label,) = window.findChildren(QLabel)
    (chk,) = window.findChildren(QCheckBox)
    chk.toggle()
    assert label.text() == "changed"


def test_on_close_runs_handler_before_closing(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    label "" as resultLabel at 0, 0, 100, 20\n'
        "\n"
        "    on close:\n"
        '        resultLabel.text = "closing"\n',
    )
    (label,) = window.findChildren(QLabel)
    window.close()
    assert label.text() == "closing"


def test_on_click_requires_a_button(qapp):
    with pytest.raises(LeopardRuntimeError, match="needs a button"):
        build(
            qapp,
            'window "W", 200, 200:\n'
            '    label "" as lbl at 0, 0, 100, 20\n'
            "\n"
            "    on click lbl:\n"
            "        x = 1\n",
        )


# ---------------------------------------------------------------------------
# on mousemove + .mouse_x/.mouse_y (Phase 16) — TurtleCanvas.mouseMoved is a
# custom pyqtSignal (turtle_canvas.py), not a native Qt widget signal like the
# events above, so it's driven here by feeding a synthetic QMouseEvent straight
# into mouseMoveEvent() rather than a QTest.mouseMove() (which needs a real,
# visible/mapped window to hit-test against — not guaranteed under
# QT_QPA_PLATFORM=offscreen).
# ---------------------------------------------------------------------------


def _synthetic_move(canvas: TurtleCanvas, x: float, y: float) -> None:
    event = QMouseEvent(
        QEvent.Type.MouseMove,
        QPointF(x, y),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    canvas.mouseMoveEvent(event)


def test_mouse_x_mouse_y_start_at_zero(qapp):
    window = build(qapp, 'window "W", 200, 200:\n    graphics as canvas1 at 0, 0, 100, 100\n')
    (canvas,) = window.findChildren(TurtleCanvas)
    assert (canvas.mouse_x, canvas.mouse_y) == (0, 0)


def test_on_mousemove_runs_handler_body_and_updates_mouse_position(qapp):
    window = build(
        qapp,
        'window "W", 200, 200:\n'
        '    graphics as canvas1 at 0, 0, 100, 100\n'
        '    label "" as posLabel at 0, 110, 100, 20\n'
        "\n"
        "    on mousemove canvas1:\n"
        '        posLabel.text = "X: " & str(canvas1.mouse_x) & " Y: " & str(canvas1.mouse_y)\n',
    )
    (canvas,) = window.findChildren(TurtleCanvas)
    (label,) = window.findChildren(QLabel)
    assert label.text() == ""
    _synthetic_move(canvas, 42, 77)
    assert (canvas.mouse_x, canvas.mouse_y) == (42, 77)
    assert label.text() == "X: 42 Y: 77"


def test_on_mousemove_requires_a_graphics_control(qapp):
    with pytest.raises(LeopardRuntimeError, match="needs a graphics control"):
        build(
            qapp,
            'window "W", 200, 200:\n'
            '    button "B" as btn at 0, 0, 100, 20\n'
            "\n"
            "    on mousemove btn:\n"
            "        x = 1\n",
        )


def test_mouse_x_property_needs_a_graphics_control(qapp):
    with pytest.raises(LeopardRuntimeError, match="needs a graphics control"):
        build(
            qapp,
            'window "W", 200, 200:\n'
            '    button "B" as btn at 0, 0, 100, 20\n'
            "    x = btn.mouse_x\n",
        )


def test_mouse_x_and_mouse_y_are_read_only(qapp):
    with pytest.raises(LeopardRuntimeError, match="'.mouse_x' is read-only"):
        build(
            qapp,
            'window "W", 200, 200:\n'
            '    graphics as canvas1 at 0, 0, 100, 100\n'
            "    canvas1.mouse_x = 5\n",
        )


# ---------------------------------------------------------------------------
# gui_builtins: close/maximize/minimize_window (notice/confirm/ask/dialogs are
# inherently modal/interactive — not exercised headlessly here)
# ---------------------------------------------------------------------------


def test_close_window_builtin(qapp):
    window = build(qapp, 'window "W", 200, 200:\n    button "B" as btn at 0, 0, 100, 20\n\n    on click btn:\n        close_window()\n')
    (btn,) = window.findChildren(QPushButton)
    assert window.isVisible()
    btn.click()
    assert not window.isVisible()


def test_gui_only_builtins_available_in_gui_builtins_dict(qapp):
    from leopard_lang.gui.dialogs import build_gui_builtins

    builtins = build_gui_builtins(window=object())
    for name in (
        "notice", "confirm", "ask", "open_file_dialog", "save_file_dialog",
        "color_dialog", "font_dialog", "close_window", "maximize_window", "minimize_window",
    ):
        assert name in builtins


# ---------------------------------------------------------------------------
# Full Greeter example (GRAMMAR.md §13) end-to-end, standalone (no IDE)
# ---------------------------------------------------------------------------


def test_greeter_example_end_to_end(qapp):
    source = (pathlib.Path(__file__).parent / "programs" / "greeter_worked_example.lep").read_text()
    window = build(qapp, source)

    assert window.windowTitle() == "Greeter"
    assert (window.width(), window.height()) == (360, 160)

    (name_box,) = window.findChildren(QLineEdit)
    (greet_button,) = window.findChildren(QPushButton)
    labels = window.findChildren(QLabel)
    result_label = next(lbl for lbl in labels if lbl.text() == "")

    greet_button.click()
    assert result_label.text() == "Please enter a name."

    name_box.setText("Chuck")
    greet_button.click()
    assert result_label.text() == "Hello, Chuck!"


# ---------------------------------------------------------------------------
# CLI dispatch: a window program routes to the GUI runtime, not the interpreter
# ---------------------------------------------------------------------------


def test_cli_dispatches_window_programs_to_gui_runtime(qapp, tmp_path, monkeypatch):
    from leopard_lang import cli

    calls = []
    monkeypatch.setattr(
        "leopard_lang.gui.app_host.run_window", lambda program, **kw: calls.append(program)
    )

    script = tmp_path / "w.lep"
    script.write_text('window "W", 100, 100:\n    button "B" as btn at 0, 0, 10, 10\n')

    exit_code = cli.main(["run", str(script)])
    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0].window is not None

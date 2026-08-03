import pathlib

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
from PyQt6.QtWidgets import QApplication, QLabel, QTextEdit  # noqa: E402

from leopard_lang.gui.app_host import run_window  # noqa: E402
from leopard_lang.lexer import tokenize  # noqa: E402
from leopard_lang.parser import parse  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


def build(qapp, body: str, width=600, height=400):
    source = (
        f'window "T", {width}, {height}:\n'
        f'    textedit as page at 0, 0, {width}, {height}\n{body}'
    )
    program = parse(tokenize(source))
    window = run_window(program, existing_app=qapp)
    return window, window.findChild(QTextEdit)


# ---------------------------------------------------------------------------
# `textedit` is an ordinary control; `.text` reuses the ordinary property dispatch
# ---------------------------------------------------------------------------


def test_textedit_is_a_placeable_control(qapp):
    window, page = build(qapp, "    x = 1\n", width=600, height=400)
    assert isinstance(page, QTextEdit)
    assert (page.width(), page.height()) == (600, 400)


def test_page_text_get_and_set(qapp):
    _window, page = build(qapp, '    page.text = "Start typing..."\n')
    assert page.toPlainText() == "Start typing..."


def test_page_text_read_reflects_user_edits(qapp):
    _window, page = build(qapp, '    result = page.text\n')
    page.setPlainText("typed by hand")
    assert page.toPlainText() == "typed by hand"


# ---------------------------------------------------------------------------
# Events (GRAMMAR.md §9): `on change`, `on close`
# ---------------------------------------------------------------------------


def test_on_change_page_runs_handler(qapp):
    window, page = build(
        qapp,
        '    label "" as wordCountLabel at 0, 0, 200, 20\n'
        "\n"
        "    on change page:\n"
        '        wordCountLabel.text = "Editing..."\n',
    )
    (label,) = window.findChildren(QLabel)
    assert label.text() == ""
    page.setPlainText("hello")
    assert label.text() == "Editing..."


def test_on_close_writes_page_text_to_file(qapp, tmp_path):
    path = str(tmp_path / "notes.txt")
    window, page = build(
        qapp,
        f'    on close:\n        write_file("{path}", page.text)\n',
    )
    page.setPlainText("saved on close")
    window.close()
    assert pathlib.Path(path).read_text() == "saved on close"


# ---------------------------------------------------------------------------
# A `textedit` control works the same in any window, and multiple named
# instances are independent (Phase 13: no more single implicit `page`)
# ---------------------------------------------------------------------------


def test_textedit_works_the_same_in_any_window(qapp):
    window, page = build(qapp, "    on change page:\n        x = 1\n")
    assert page is not None


def test_multiple_named_textedit_controls_are_independent(qapp):
    source = (
        'window "T", 600, 400:\n'
        "    textedit as notes at 0, 0, 300, 400\n"
        "    textedit as scratch at 300, 0, 300, 400\n"
        '    notes.text = "first"\n'
        '    scratch.text = "second"\n'
    )
    program = parse(tokenize(source))
    window = run_window(program, existing_app=qapp)
    pages = window.findChildren(QTextEdit)
    assert len(pages) == 2
    notes = next(p for p in pages if p.pos().x() == 0)
    scratch = next(p for p in pages if p.pos().x() == 300)
    assert notes.toPlainText() == "first"
    assert scratch.toPlainText() == "second"


# ---------------------------------------------------------------------------
# Full GRAMMAR.md §11 example, standalone (no IDE)
# ---------------------------------------------------------------------------


def test_grammar_section_11_example_end_to_end(qapp, tmp_path):
    # The raw §11 example references `wordCountLabel` without declaring it (same
    # kind of illustrative gap as §8's menu example) — declared here so the whole
    # thing is a complete, runnable program.
    path = str(tmp_path / "notes.txt")
    source = (
        'window "Notes", 600, 400:\n'
        "\n"
        '    textedit as page at 0, 0, 600, 400\n'
        '    label "" as wordCountLabel at 0, 0, 200, 20\n'
        "\n"
        '    page.text = "Start typing..."\n'
        "\n"
        "    on change page:\n"
        '        wordCountLabel.text = "Editing..."\n'
        "\n"
        "    on close:\n"
        f'        write_file("{path}", page.text)\n'
    )
    program = parse(tokenize(source))
    window = run_window(program, existing_app=qapp)
    page = window.findChild(QTextEdit)
    (label,) = window.findChildren(QLabel)

    assert page.toPlainText() == "Start typing..."
    assert label.text() == ""

    page.setPlainText("Start typing...and some more.")
    assert label.text() == "Editing..."

    window.close()
    assert pathlib.Path(path).read_text() == "Start typing...and some more."

"""LeopardLanguageProvider: wires the standalone `leopard-lang` package into the IDE.

This is integration only — everything it calls into (the lexer/parser/interpreter,
the GUI runtime) was already built and proven standalone via `leopard run` before
this file existed (see LANGUAGES/Leopard/IMPLEMENTATION_PLAN.md, Phases 0-8). The
one new thing Phase 9 adds: passing the IDE's own already-running QApplication into
`run_window()` so a GUI Leopard program reuses the IDE's event loop instead of
spawning a second one.
"""

from __future__ import annotations

import contextlib
import re
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtGui import QSyntaxHighlighter, QTextDocument
from PyQt6.QtWidgets import QApplication

from app.language import LanguageProvider
from app.syntax import HighlightRule, RuleBasedHighlighter, keyword_rule
from app.themes import SyntaxColors
from leopard_lang.errors import LeopardError
from leopard_lang.interpreter import interpret
from leopard_lang.lexer import tokenize
from leopard_lang.parser import parse
from leopard_lang.tokens import KEYWORDS

if TYPE_CHECKING:
    from app.terminal import TerminalPane


class _TerminalStdout:
    """Redirect target for `print`: buffers to newlines, forwards each line to the console pane."""

    def __init__(self, terminal: "TerminalPane") -> None:
        self._terminal = terminal
        self._buffer = ""

    def write(self, text: str) -> None:
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._terminal.write(line)

    def flush(self) -> None:
        if self._buffer:
            self._terminal.write(self._buffer)
            self._buffer = ""

# Turtle graphics commands (GRAMMAR.md §10) and builtins (§12) get their own
# color, layered on top of the general keyword rule below (rules are applied in
# order, later rules win on overlapping spans — see app/syntax.py). Hand-listed
# here rather than imported from `leopard_lang.parser`'s private categorization
# sets, matching every other fork's convention of its own KEYWORDS/BUILTINS
# constants (e.g. BLISS/euphoria_language.py) — those forks wrap an external
# interpreter with no importable token list at all, but the convention of
# keeping the highlighter's word lists self-contained here still applies.
_BUILTINS_AND_COMMANDS = [
    # turtle graphics (§10)
    "up", "down", "home", "go", "goto", "place", "turn", "north", "fill",
    "pen", "size", "font", "text", "backcolor", "box", "boxfilled",
    "circle", "circlefilled", "ellipse", "ellipsefilled", "drawbmp",
    # builtins (§12)
    "str", "num", "notice", "confirm", "ask", "beep", "date", "time",
    "write_file", "append_file", "read_file", "delete_file", "make_dir",
    "remove_dir", "file_exists", "open_file_dialog", "save_file_dialog",
    "color_dialog", "font_dialog", "open_url", "open_email", "run_program",
    "ascii", "set_cursor", "close_window", "maximize_window", "minimize_window",
    "play_sound", "stop_sound", "play_music", "stop_music", "pause_music",
    "download_file",
]


def _leopard_rules() -> List[HighlightRule]:
    return [
        keyword_rule(list(KEYWORDS.keys()), "keyword"),
        keyword_rule(_BUILTINS_AND_COMMANDS, "builtin"),
        HighlightRule(re.compile(r"\b\d+\.?\d*\b"), "number"),
        HighlightRule(re.compile(r"\.\w+"), "identifier"),  # .property access
        # GRAMMAR.md §4 operators/punctuation, minus '.' (handled above, as
        # part of property access rather than a bare operator)
        HighlightRule(re.compile(r"[+\-*/%^&=<>()\[\],:]"), "operator"),
        HighlightRule(re.compile(r'"(?:\\.|[^"\\])*"'), "string"),
        HighlightRule(re.compile(r"#.*"), "comment"),
    ]


class LeopardHighlighter(RuleBasedHighlighter):
    def __init__(self, document: QTextDocument, syntax_colors: SyntaxColors):
        super().__init__(document, syntax_colors, _leopard_rules())


class LeopardLanguageProvider(LanguageProvider):
    @property
    def name(self) -> str:
        return "Leopard"

    @property
    def file_extensions(self) -> List[str]:
        return [".lep"]

    def create_highlighter(
        self, document: QTextDocument, syntax_colors: SyntaxColors
    ) -> Optional[QSyntaxHighlighter]:
        return LeopardHighlighter(document, syntax_colors)

    def run(self, source: str, terminal: "TerminalPane") -> None:
        try:
            program = parse(tokenize(source))
        except LeopardError as exc:
            terminal.write(f"{exc}\n")
            return

        try:
            if program.window is not None:
                from leopard_lang.gui.app_host import run_window

                run_window(program, existing_app=QApplication.instance())
            else:
                stdout = _TerminalStdout(terminal)
                with contextlib.redirect_stdout(stdout):
                    interpret(program)
                stdout.flush()
                terminal.write("Program finished.\n")
        except LeopardError as exc:
            terminal.write(f"{exc}\n")

    def compile(self, source: str, name: str, output_dir: Path, terminal: "TerminalPane") -> None:
        terminal.write(f"Compiling {name}...\n")
        try:
            from leopard_lang.build import compile_program
        except ImportError:
            terminal.write("Compiling needs the 'build' extra: pip install -e '.[build]'\n")
            return

        try:
            exe_path = compile_program(source, name, output_dir)
        except LeopardError as exc:
            terminal.write(f"{exc}\n")
            return
        except Exception as exc:  # PyInstaller failures aren't LeopardErrors
            terminal.write(f"Build failed: {exc}\n")
            return

        terminal.write(f"Built {exe_path}\n")

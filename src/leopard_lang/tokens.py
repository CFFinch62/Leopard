"""TokenType enum and Token dataclass for the Leopard lexer.

Every reserved word gets its own TokenType member: the core keywords (GRAMMAR.md §14),
the control-declaration keywords (GRAMMAR.md §7 — see IMPLEMENTATION_PLAN.md's decisions
log for why these are included despite being absent from §14's consolidated list), every
turtle-graphics command (§10), and every builtin (§12).
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any


class TokenType(enum.Enum):
    # Structural / literals
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"

    # Operators & punctuation (GRAMMAR.md §4)
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    PERCENT = "%"
    CARET = "^"
    AMP = "&"
    EQ = "="
    NEQ = "<>"
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="
    LPAREN = "("
    RPAREN = ")"
    LBRACKET = "["
    RBRACKET = "]"
    COMMA = ","
    COLON = ":"
    DOT = "."

    # `eq` — a word alternative for equality-only comparison, so a program can use `=`
    # for assignment and `eq` for comparison unambiguously if that's clearer to read
    # (both spellings remain valid; see GRAMMAR.md §4 and IMPLEMENTATION_PLAN.md's
    # decisions log for why `=` itself was kept doing double duty rather than split).
    EQ_WORD = "eq"

    # Core keywords (GRAMMAR.md §14)
    WINDOW = "window"
    TEXT = "text"
    GRAPHICS = "graphics"
    AS = "as"
    AT = "at"
    TRUE = "true"
    FALSE = "false"
    AND = "and"
    OR = "or"
    NOT = "not"
    IF = "if"
    ELSEIF = "elseif"
    ELSE = "else"
    WHILE = "while"
    FOR = "for"
    TO = "to"
    STEP = "step"
    BREAK = "break"
    CONTINUE = "continue"
    FUNCTION = "function"
    RETURN = "return"
    MENU = "menu"
    ITEM = "item"
    CHECKITEM = "checkitem"
    SUBMENU = "submenu"
    SEPARATOR = "separator"
    ON = "on"
    CLICK = "click"
    CHANGE = "change"
    SELECT = "select"
    CLOSE = "close"
    PAGE = "page"

    # Control declaration keywords (GRAMMAR.md §7)
    TEXTBOX = "textbox"
    TEXTEDIT = "textedit"
    LABEL = "label"
    BUTTON = "button"
    BMPBUTTON = "bmpbutton"
    LISTBOX = "listbox"
    COMBOBOX = "combobox"
    RADIOBUTTON = "radiobutton"
    CHECKBOX = "checkbox"
    GROUPBOX = "groupbox"

    # Turtle graphics commands (GRAMMAR.md §10)
    UP = "up"
    DOWN = "down"
    HOME = "home"
    GO = "go"
    GOTO = "goto"
    PLACE = "place"
    TURN = "turn"
    NORTH = "north"
    FILL = "fill"
    PEN = "pen"
    SIZE = "size"
    FONT = "font"
    BACKCOLOR = "backcolor"
    BOX = "box"
    BOXFILLED = "boxfilled"
    CIRCLE = "circle"
    CIRCLEFILLED = "circlefilled"
    ELLIPSE = "ellipse"
    ELLIPSEFILLED = "ellipsefilled"
    DRAWBMP = "drawbmp"

    # Builtins (GRAMMAR.md §12)
    STR = "str"
    NUM = "num"
    NOTICE = "notice"
    CONFIRM = "confirm"
    ASK = "ask"
    BEEP = "beep"
    DATE = "date"
    TIME = "time"
    WRITE_FILE = "write_file"
    APPEND_FILE = "append_file"
    READ_FILE = "read_file"
    DELETE_FILE = "delete_file"
    MAKE_DIR = "make_dir"
    REMOVE_DIR = "remove_dir"
    FILE_EXISTS = "file_exists"
    OPEN_FILE_DIALOG = "open_file_dialog"
    SAVE_FILE_DIALOG = "save_file_dialog"
    COLOR_DIALOG = "color_dialog"
    FONT_DIALOG = "font_dialog"
    OPEN_URL = "open_url"
    OPEN_EMAIL = "open_email"
    RUN_PROGRAM = "run_program"
    ASCII = "ascii"
    SET_CURSOR = "set_cursor"
    CLOSE_WINDOW = "close_window"
    MAXIMIZE_WINDOW = "maximize_window"
    MINIMIZE_WINDOW = "minimize_window"
    PLAY_SOUND = "play_sound"
    STOP_SOUND = "stop_sound"
    PLAY_MUSIC = "play_music"
    STOP_MUSIC = "stop_music"
    PAUSE_MUSIC = "pause_music"
    DOWNLOAD_FILE = "download_file"


_NON_KEYWORD_TYPES = {
    TokenType.IDENTIFIER,
    TokenType.STRING,
    TokenType.NUMBER,
    TokenType.NEWLINE,
    TokenType.INDENT,
    TokenType.DEDENT,
    TokenType.EOF,
}

# word -> TokenType, for every reserved word (operators/punctuation excluded: their
# values aren't valid identifiers, so this comprehension naturally skips them).
KEYWORDS: dict[str, TokenType] = {
    tok.value: tok
    for tok in TokenType
    if tok not in _NON_KEYWORD_TYPES and tok.value.isidentifier()
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    value: Any
    line: int

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Token({self.type.name}, {self.lexeme!r}, line={self.line})"

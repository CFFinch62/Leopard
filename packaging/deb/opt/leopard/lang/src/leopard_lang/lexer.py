"""Source text -> token stream. Indentation-sensitive, Python `tokenize`-inspired.

GRAMMAR.md §1: `#` comments to end of line, double-quoted strings, one numeric type,
colon+indentation blocks, newline-terminated statements (no line continuation).
"""

from __future__ import annotations

from .errors import LeopardSyntaxError
from .tokens import KEYWORDS, Token, TokenType

_SINGLE_CHAR_OPERATORS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERCENT,
    "^": TokenType.CARET,
    "&": TokenType.AMP,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    ".": TokenType.DOT,
}

_ESCAPES = {"n": "\n", '"': '"', "\\": "\\"}


class _LineScanner:
    """Tokenizes the code portion of one physical line (indentation already stripped)."""

    def __init__(self, text: str, line: int):
        self.text = text
        self.line = line
        self.pos = 0
        self.length = len(text)

    def scan(self) -> list[Token]:
        tokens: list[Token] = []
        while self.pos < self.length:
            ch = self.text[self.pos]

            if ch in " \t":
                self.pos += 1
                continue
            if ch == "#":
                break  # comment: rest of line ignored
            if ch == '"':
                tokens.append(self._scan_string())
                continue
            if ch.isdigit():
                tokens.append(self._scan_number())
                continue
            if ch.isalpha() or ch == "_":
                tokens.append(self._scan_word())
                continue

            tokens.append(self._scan_operator())

        return tokens

    def _scan_string(self) -> Token:
        start = self.pos
        self.pos += 1  # opening quote
        chars: list[str] = []
        while True:
            if self.pos >= self.length:
                raise LeopardSyntaxError(self.line, "unterminated string literal")
            ch = self.text[self.pos]
            if ch == '"':
                self.pos += 1
                break
            if ch == "\\":
                self.pos += 1
                if self.pos >= self.length:
                    raise LeopardSyntaxError(self.line, "unterminated string literal")
                esc = self.text[self.pos]
                if esc not in _ESCAPES:
                    raise LeopardSyntaxError(self.line, f"unknown string escape '\\{esc}'")
                chars.append(_ESCAPES[esc])
                self.pos += 1
                continue
            chars.append(ch)
            self.pos += 1
        lexeme = self.text[start : self.pos]
        return Token(TokenType.STRING, lexeme, "".join(chars), self.line)

    def _scan_number(self) -> Token:
        start = self.pos
        while self.pos < self.length and self.text[self.pos].isdigit():
            self.pos += 1
        is_float = False
        if (
            self.pos < self.length
            and self.text[self.pos] == "."
            and self.pos + 1 < self.length
            and self.text[self.pos + 1].isdigit()
        ):
            is_float = True
            self.pos += 1
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        lexeme = self.text[start : self.pos]
        value: float | int = float(lexeme) if is_float else int(lexeme)
        return Token(TokenType.NUMBER, lexeme, value, self.line)

    def _scan_word(self) -> Token:
        start = self.pos
        while self.pos < self.length and (self.text[self.pos].isalnum() or self.text[self.pos] == "_"):
            self.pos += 1
        lexeme = self.text[start : self.pos]
        tok_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        return Token(tok_type, lexeme, lexeme, self.line)

    def _scan_operator(self) -> Token:
        two = self.text[self.pos : self.pos + 2]
        if two == "<>":
            self.pos += 2
            return Token(TokenType.NEQ, two, None, self.line)
        if two == "<=":
            self.pos += 2
            return Token(TokenType.LE, two, None, self.line)
        if two == ">=":
            self.pos += 2
            return Token(TokenType.GE, two, None, self.line)

        ch = self.text[self.pos]
        if ch == "<":
            self.pos += 1
            return Token(TokenType.LT, ch, None, self.line)
        if ch == ">":
            self.pos += 1
            return Token(TokenType.GT, ch, None, self.line)
        if ch == "=":
            self.pos += 1
            return Token(TokenType.EQ, ch, None, self.line)
        if ch in _SINGLE_CHAR_OPERATORS:
            self.pos += 1
            return Token(_SINGLE_CHAR_OPERATORS[ch], ch, None, self.line)

        raise LeopardSyntaxError(self.line, f"unexpected character {ch!r}")


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    indent_stack = [0]

    lines = source.splitlines()
    for lineno, raw_line in enumerate(lines, start=1):
        stripped = raw_line.lstrip(" \t")
        prefix = raw_line[: len(raw_line) - len(stripped)]
        rest = stripped

        if rest == "" or rest.startswith("#"):
            continue  # blank/comment-only lines don't affect indentation

        if " " in prefix and "\t" in prefix:
            raise LeopardSyntaxError(lineno, "cannot mix tabs and spaces in indentation")

        # A tab counts as one column, same as a space — this only needs to be
        # self-consistent within a line (mixing is already rejected above).
        indent_width = len(prefix)

        if indent_width > indent_stack[-1]:
            indent_stack.append(indent_width)
            tokens.append(Token(TokenType.INDENT, prefix, None, lineno))
        elif indent_width < indent_stack[-1]:
            while indent_stack[-1] > indent_width:
                indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, "", None, lineno))
            if indent_stack[-1] != indent_width:
                raise LeopardSyntaxError(lineno, "unindent does not match any outer indentation level")

        tokens.extend(_LineScanner(rest, lineno).scan())
        tokens.append(Token(TokenType.NEWLINE, "", None, lineno))

    final_line = len(lines) + 1
    while indent_stack[-1] > 0:
        indent_stack.pop()
        tokens.append(Token(TokenType.DEDENT, "", None, final_line))
    tokens.append(Token(TokenType.EOF, "", None, final_line))

    return tokens

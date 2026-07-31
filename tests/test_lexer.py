import pathlib

import pytest

from leopard_lang.errors import LeopardSyntaxError
from leopard_lang.lexer import tokenize
from leopard_lang.tokens import TokenType


def token_types(source: str) -> list[TokenType]:
    return [t.type for t in tokenize(source)]


# ---------------------------------------------------------------------------
# One test per token category
# ---------------------------------------------------------------------------


def test_identifier():
    assert token_types("score") == [TokenType.IDENTIFIER, TokenType.NEWLINE, TokenType.EOF]


def test_string_literal():
    tokens = tokenize('"hello"')
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "hello"


def test_integer_literal():
    tokens = tokenize("42")
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == 42
    assert isinstance(tokens[0].value, int)


def test_float_literal():
    tokens = tokenize("3.14")
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == 3.14
    assert isinstance(tokens[0].value, float)


def test_boolean_keywords():
    assert token_types("true") == [TokenType.TRUE, TokenType.NEWLINE, TokenType.EOF]
    assert token_types("false") == [TokenType.FALSE, TokenType.NEWLINE, TokenType.EOF]


@pytest.mark.parametrize(
    "op, expected",
    [
        ("+", TokenType.PLUS),
        ("-", TokenType.MINUS),
        ("*", TokenType.STAR),
        ("/", TokenType.SLASH),
        ("%", TokenType.PERCENT),
        ("^", TokenType.CARET),
        ("&", TokenType.AMP),
        ("=", TokenType.EQ),
        ("eq", TokenType.EQ_WORD),
        ("<>", TokenType.NEQ),
        ("<", TokenType.LT),
        (">", TokenType.GT),
        ("<=", TokenType.LE),
        (">=", TokenType.GE),
        ("(", TokenType.LPAREN),
        (")", TokenType.RPAREN),
        ("[", TokenType.LBRACKET),
        ("]", TokenType.RBRACKET),
        (",", TokenType.COMMA),
        (":", TokenType.COLON),
        (".", TokenType.DOT),
    ],
)
def test_operators_and_punctuation(op, expected):
    assert token_types(op) == [expected, TokenType.NEWLINE, TokenType.EOF]


def test_logical_word_operators():
    assert token_types("and or not") == [
        TokenType.AND,
        TokenType.OR,
        TokenType.NOT,
        TokenType.NEWLINE,
        TokenType.EOF,
    ]


@pytest.mark.parametrize(
    "word, expected",
    [
        ("if", TokenType.IF),
        ("elseif", TokenType.ELSEIF),
        ("else", TokenType.ELSE),
        ("while", TokenType.WHILE),
        ("for", TokenType.FOR),
        ("function", TokenType.FUNCTION),
        ("return", TokenType.RETURN),
        ("menu", TokenType.MENU),
        ("checkitem", TokenType.CHECKITEM),
        ("page", TokenType.PAGE),
        ("textbox", TokenType.TEXTBOX),
        ("button", TokenType.BUTTON),
        ("goto", TokenType.GOTO),
        ("circlefilled", TokenType.CIRCLEFILLED),
        ("notice", TokenType.NOTICE),
        ("write_file", TokenType.WRITE_FILE),
    ]
)
def test_reserved_words(word, expected):
    assert token_types(word) == [expected, TokenType.NEWLINE, TokenType.EOF]


def test_newline_and_eof():
    tokens = tokenize("x = 1")
    assert tokens[-2].type == TokenType.NEWLINE
    assert tokens[-1].type == TokenType.EOF


def test_indent_dedent():
    src = "if true:\n    x = 1\ny = 2\n"
    types = token_types(src)
    assert TokenType.INDENT in types
    assert TokenType.DEDENT in types
    # dedent must land before the top-level statement that follows the block
    dedent_index = types.index(TokenType.DEDENT)
    assert types[dedent_index + 1] == TokenType.IDENTIFIER


# ---------------------------------------------------------------------------
# Comments, string escapes
# ---------------------------------------------------------------------------


def test_comment_stripped_to_end_of_line():
    tokens = tokenize("x = 1 # this is a comment")
    assert token_types("x = 1 # this is a comment") == [
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.NUMBER,
        TokenType.NEWLINE,
        TokenType.EOF,
    ]
    assert tokens[2].value == 1


def test_comment_only_line_does_not_affect_indentation():
    src = "x = 1\n# a comment\ny = 2\n"
    types = token_types(src)
    assert TokenType.INDENT not in types
    assert TokenType.DEDENT not in types


@pytest.mark.parametrize(
    "escape, expected",
    [
        (r"\n", "\n"),
        (r"\"", '"'),
        (r"\\", "\\"),
    ],
)
def test_string_escapes(escape, expected):
    tokens = tokenize(f'"a{escape}b"')
    assert tokens[0].value == f"a{expected}b"


def test_unknown_escape_is_error():
    with pytest.raises(LeopardSyntaxError):
        tokenize(r'"bad \q escape"')


def test_unterminated_string_is_error():
    with pytest.raises(LeopardSyntaxError):
        tokenize('"never closed')


# ---------------------------------------------------------------------------
# Mixed tabs/spaces
# ---------------------------------------------------------------------------


def test_mixed_tabs_and_spaces_in_indentation_is_specific_error():
    src = "if true:\n \t x = 1\n"
    with pytest.raises(LeopardSyntaxError) as exc_info:
        tokenize(src)
    assert "mix tabs and spaces" in exc_info.value.message


def test_inconsistent_dedent_is_error():
    src = "if true:\n    x = 1\n  y = 2\n"
    with pytest.raises(LeopardSyntaxError) as exc_info:
        tokenize(src)
    assert "unindent" in exc_info.value.message


# ---------------------------------------------------------------------------
# Line numbers
# ---------------------------------------------------------------------------


def test_every_token_carries_a_line_number():
    src = "x = 1\ny = 2\n"
    for tok in tokenize(src):
        assert tok.line >= 1


def test_line_numbers_advance_correctly():
    src = "x = 1\n\ny = 2\n"
    tokens = tokenize(src)
    x_tok = tokens[0]
    y_tok = next(t for t in tokens if t.type == TokenType.IDENTIFIER and t.lexeme == "y")
    assert x_tok.line == 1
    assert y_tok.line == 3


# ---------------------------------------------------------------------------
# Every GRAMMAR.md example tokenizes without error
# ---------------------------------------------------------------------------

PROGRAMS_DIR = pathlib.Path(__file__).parent / "programs"


@pytest.mark.parametrize("path", sorted(PROGRAMS_DIR.glob("*.lep")), ids=lambda p: p.stem)
def test_grammar_examples_tokenize_without_error(path: pathlib.Path):
    source = path.read_text(encoding="utf-8")
    tokens = tokenize(source)
    assert tokens[-1].type == TokenType.EOF

import pathlib

import pytest

from leopard_lang import ast_nodes as ast
from leopard_lang.errors import LeopardSyntaxError
from leopard_lang.lexer import tokenize
from leopard_lang.parser import parse


def parse_src(source: str) -> ast.Program:
    return parse(tokenize(source))


# ---------------------------------------------------------------------------
# Assignment / property assignment / expressions
# ---------------------------------------------------------------------------


def test_plain_assignment():
    prog = parse_src("x = 1\n")
    assert prog.body == [ast.Assignment(target="x", value=ast.Literal(1, 1), line=1)]


def test_property_assignment():
    prog = parse_src('nameBox.text = "hi"\n')
    (stmt,) = prog.body
    assert isinstance(stmt, ast.PropertyAssignment)
    assert isinstance(stmt.target, ast.PropertyAccess)
    assert stmt.target.name == "text"
    assert isinstance(stmt.target.obj, ast.Identifier)
    assert stmt.target.obj.name == "nameBox"
    assert stmt.value == ast.Literal("hi", 1)


def test_list_literal_and_index():
    prog = parse_src('fruits = ["apple", "banana"]\nfirst = fruits[1]\n')
    assign1, assign2 = prog.body
    assert isinstance(assign1.value, ast.ListLiteral)
    assert assign1.value.elements == [ast.Literal("apple", 1), ast.Literal("banana", 1)]
    assert isinstance(assign2.value, ast.Index)
    assert assign2.value.obj == ast.Identifier("fruits", 2)
    assert assign2.value.index == ast.Literal(1, 2)


def test_bare_command_call_no_parens():
    prog = parse_src('notice "hi"\n')
    (stmt,) = prog.body
    assert isinstance(stmt, ast.ExprStatement)
    assert isinstance(stmt.expr, ast.Call)
    assert stmt.expr.callee == ast.Identifier("notice", 1)
    assert stmt.expr.args == [ast.Literal("hi", 1)]


def test_bare_command_multiple_args():
    prog = parse_src('write_file "a.txt", "hi"\n')
    (stmt,) = prog.body
    assert stmt.expr.callee.name == "write_file"
    assert stmt.expr.args == [ast.Literal("a.txt", 1), ast.Literal("hi", 1)]


def test_zero_arg_bare_command():
    # A bare name as an entire statement is a zero-arg call — fixed in Phase 6 after
    # this originally parsed as a bare Identifier, which the interpreter can't call.
    prog = parse_src("beep\n")
    (stmt,) = prog.body
    assert isinstance(stmt, ast.ExprStatement)
    assert stmt.expr == ast.Call(callee=ast.Identifier("beep", 1), args=[], line=1)


def test_parenthesized_call():
    prog = parse_src('confirm("Really quit?")\n')
    (stmt,) = prog.body
    assert isinstance(stmt.expr, ast.Call)
    assert stmt.expr.callee == ast.Identifier("confirm", 1)
    assert stmt.expr.args == [ast.Literal("Really quit?", 1)]


def test_chained_property_and_call():
    prog = parse_src('fruitList.items.add("Date")\n')
    (stmt,) = prog.body
    call = stmt.expr
    assert isinstance(call, ast.Call)
    assert isinstance(call.callee, ast.PropertyAccess)
    assert call.callee.name == "add"
    assert call.callee.obj.name == "items"


# ---------------------------------------------------------------------------
# Operator precedence (GRAMMAR.md §4)
# ---------------------------------------------------------------------------


def test_precedence_multiplicative_over_additive():
    prog = parse_src("x = 1 + 2 * 3\n")
    value = prog.body[0].value
    assert value.op == "+"
    assert value.left == ast.Literal(1, 1)
    assert isinstance(value.right, ast.BinaryOp)
    assert value.right.op == "*"


def test_precedence_concat_tighter_than_comparison():
    prog = parse_src('x = a & b = c\n')
    value = prog.body[0].value
    assert value.op == "="
    assert isinstance(value.left, ast.BinaryOp)
    assert value.left.op == "&"


def test_eq_word_is_same_operator_as_eq_symbol():
    prog = parse_src("x = a eq b\n")
    value = prog.body[0].value
    assert isinstance(value, ast.BinaryOp)
    assert value.op == "="


def test_precedence_not_looser_than_comparison():
    prog = parse_src("x = not a = b\n")
    value = prog.body[0].value
    assert isinstance(value, ast.UnaryOp)
    assert value.op == "not"
    assert isinstance(value.operand, ast.BinaryOp)
    assert value.operand.op == "="


def test_precedence_and_or():
    prog = parse_src("x = a and b or c\n")
    value = prog.body[0].value
    assert value.op == "or"
    assert isinstance(value.left, ast.BinaryOp)
    assert value.left.op == "and"


def test_power_is_right_associative():
    prog = parse_src("x = 2 ^ 3 ^ 2\n")
    value = prog.body[0].value
    assert value.op == "^"
    assert value.left == ast.Literal(2, 1)
    assert isinstance(value.right, ast.BinaryOp)
    assert value.right.op == "^"


def test_statement_starting_with_not():
    # `not x` can never be an assignment target, so a leading `not` must still parse
    # as a bare expression-statement rather than hitting the assignment-detection path.
    prog = parse_src("not found\n")
    (stmt,) = prog.body
    assert isinstance(stmt, ast.ExprStatement)
    assert isinstance(stmt.expr, ast.UnaryOp)
    assert stmt.expr.op == "not"
    assert stmt.expr.operand == ast.Identifier("found", 1)


def test_string_concat_operator():
    prog = parse_src('x = "Score: " & str(score)\n')
    value = prog.body[0].value
    assert value.op == "&"
    assert isinstance(value.right, ast.Call)
    assert value.right.callee.name == "str"


# ---------------------------------------------------------------------------
# Control flow (GRAMMAR.md §5)
# ---------------------------------------------------------------------------


def test_if_elseif_else():
    src = (
        "if score > 10:\n"
        '    notice "You win!"\n'
        "elseif score > 0:\n"
        '    notice "Keep going."\n'
        "else:\n"
        '    notice "Try again."\n'
    )
    prog = parse_src(src)
    (stmt,) = prog.body
    assert isinstance(stmt, ast.If)
    assert len(stmt.then_body) == 1
    assert len(stmt.elseif_clauses) == 1
    assert stmt.else_body is not None and len(stmt.else_body) == 1


def test_while_loop():
    prog = parse_src("while count < 5:\n    count = count + 1\n")
    (stmt,) = prog.body
    assert isinstance(stmt, ast.While)
    assert stmt.condition.op == "<"


def test_for_loop_with_step():
    prog = parse_src("for i = 1 to 10 step 2:\n    x = i\n")
    (stmt,) = prog.body
    assert isinstance(stmt, ast.For)
    assert stmt.var == "i"
    assert stmt.start == ast.Literal(1, 1)
    assert stmt.end == ast.Literal(10, 1)
    assert stmt.step == ast.Literal(2, 1)


def test_for_loop_without_step():
    prog = parse_src("for i = 1 to 10:\n    x = i\n")
    (stmt,) = prog.body
    assert stmt.step is None


def test_for_each_loop():
    prog = parse_src("for fruit in fruits:\n    print fruit\n")
    (stmt,) = prog.body
    assert isinstance(stmt, ast.ForEach)
    assert stmt.var == "fruit"
    assert stmt.iterable == ast.Identifier("fruits", 1)


def test_do_until_loop():
    prog = parse_src("do:\n    n = n + 1\nuntil n >= 3\n")
    (stmt,) = prog.body
    assert isinstance(stmt, ast.DoUntil)
    assert len(stmt.body) == 1
    assert stmt.condition.op == ">="


def test_switch_with_default():
    src = (
        "switch x:\n"
        "    case 1:\n"
        '        print "one"\n'
        "    case 2:\n"
        '        print "two"\n'
        "    default:\n"
        '        print "other"\n'
    )
    prog = parse_src(src)
    (stmt,) = prog.body
    assert isinstance(stmt, ast.Switch)
    assert len(stmt.cases) == 2
    assert stmt.cases[0][0] == ast.Literal(1, 2)
    assert stmt.default_body is not None and len(stmt.default_body) == 1


def test_switch_without_default():
    prog = parse_src('switch x:\n    case 1:\n        print "one"\n')
    (stmt,) = prog.body
    assert stmt.default_body is None


def test_switch_with_no_cases_is_error():
    with pytest.raises(LeopardSyntaxError):
        parse_src("switch x:\n    default:\n        y = 1\n")


def test_switch_with_two_defaults_is_error():
    src = "switch x:\n    case 1:\n        y = 1\n    default:\n        y = 2\n    default:\n        y = 3\n"
    with pytest.raises(LeopardSyntaxError):
        parse_src(src)


def test_break_and_continue():
    prog = parse_src("break\ncontinue\n")
    assert prog.body == [ast.Break(1), ast.Continue(2)]


def test_return_with_and_without_value():
    prog = parse_src("function f():\n    return\n\nfunction g():\n    return 1\n")
    f_decl, g_decl = prog.body
    assert f_decl.body[0].value is None
    assert g_decl.body[0].value == ast.Literal(1, 5)


# ---------------------------------------------------------------------------
# Functions (GRAMMAR.md §6)
# ---------------------------------------------------------------------------


def test_function_decl_with_params_and_body():
    prog = parse_src('function greet(who):\n    return "Hello, " & who\n')
    (fn,) = prog.body
    assert isinstance(fn, ast.FunctionDecl)
    assert fn.name == "greet"
    assert fn.params == ["who"]
    assert isinstance(fn.body[0], ast.Return)


def test_function_decl_no_params():
    prog = parse_src("function f():\n    return 1\n")
    (fn,) = prog.body
    assert fn.params == []


# ---------------------------------------------------------------------------
# Controls (GRAMMAR.md §7)
# ---------------------------------------------------------------------------


def test_control_decl_with_caption():
    prog = parse_src('button "Greet" as btnGreet at 220, 10, 80, 24\n')
    (ctrl,) = prog.body
    assert isinstance(ctrl, ast.ControlDecl)
    assert ctrl.kind == "button"
    assert ctrl.caption == "Greet"
    assert ctrl.name == "btnGreet"
    assert ctrl.x == ast.Literal(220, 1)
    assert ctrl.h == ast.Literal(24, 1)


def test_control_decl_without_caption():
    prog = parse_src("textbox as nameBox at 120, 10, 200, 24\n")
    (ctrl,) = prog.body
    assert ctrl.kind == "textbox"
    assert ctrl.caption is None
    assert ctrl.name == "nameBox"


# ---------------------------------------------------------------------------
# Menus (GRAMMAR.md §8)
# ---------------------------------------------------------------------------


def test_menu_with_items_separator_and_nested_submenu():
    src = (
        'menu "&File" as fileMenu:\n'
        '    item "&New..." as mnuNew\n'
        "    separator\n"
        '    submenu "Open &Recent" as mnuRecent:\n'
        '        item "report.lep" as mnuRecent1\n'
    )
    prog = parse_src(src)
    (menu,) = prog.body
    assert isinstance(menu, ast.MenuDecl)
    assert menu.title == "&File"
    assert menu.name == "fileMenu"
    item, sep, submenu = menu.body
    assert isinstance(item, ast.ItemDecl) and item.name == "mnuNew"
    assert isinstance(sep, ast.Separator)
    assert isinstance(submenu, ast.SubmenuDecl)
    assert submenu.name == "mnuRecent"
    assert isinstance(submenu.body[0], ast.ItemDecl)


def test_checkitem():
    prog = parse_src('menu "&View" as viewMenu:\n    checkitem "Show &Toolbar" as mnuToolbar\n')
    (menu,) = prog.body
    (checkitem,) = menu.body
    assert isinstance(checkitem, ast.CheckItemDecl)
    assert checkitem.name == "mnuToolbar"


# ---------------------------------------------------------------------------
# Events (GRAMMAR.md §9)
# ---------------------------------------------------------------------------


def test_event_handler_with_target():
    prog = parse_src('on click btnGreet:\n    notice "hi"\n')
    (handler,) = prog.body
    assert isinstance(handler, ast.EventHandler)
    assert handler.event == "click"
    assert handler.target == "btnGreet"


def test_event_handler_close_has_no_target():
    prog = parse_src('on close:\n    confirm("Really quit?")\n')
    (handler,) = prog.body
    assert handler.event == "close"
    assert handler.target is None


# ---------------------------------------------------------------------------
# GRAMMAR.md §11: `page` needs no special grammar (Phase 2 checklist item) —
# it parses via the same EXPRESSION_KEYWORDS path as any other reserved word
# used in expression position (see parser.py); these tests exercise that path
# through `page` specifically rather than a dedicated grammar rule.
# ---------------------------------------------------------------------------


def test_page_property_assignment():
    prog = parse_src('page.text = "Start typing..."\n')
    (stmt,) = prog.body
    assert isinstance(stmt, ast.PropertyAssignment)
    assert stmt.target.obj == ast.Identifier("page", 1)


def test_page_as_event_target():
    prog = parse_src('on change page:\n    x = 1\n')
    (handler,) = prog.body
    assert handler.target == "page"


# ---------------------------------------------------------------------------
# Program shape (GRAMMAR.md §2)
# ---------------------------------------------------------------------------


def test_bare_script_has_no_window():
    prog = parse_src("x = 1\n")
    assert prog.window is None


def test_window_header():
    prog = parse_src('window "My App", 500, 400:\n    notice "hi"\n')
    assert prog.window is not None
    assert prog.window.title == "My App"
    assert (prog.window.width, prog.window.height) == (500, 400)


@pytest.mark.parametrize(
    "header",
    [
        'text window "Log Viewer", 600, 400:',
        'graphics window "Turtle Demo", 640, 480:',
    ],
)
def test_text_and_graphics_window_headers_are_retired(header):
    # Phase 13: `text window`/`graphics window` are gone — a `textedit`/`graphics`
    # control declared inside an ordinary `window` replaces them (see below).
    with pytest.raises(LeopardSyntaxError):
        parse_src(f'{header}\n    notice "hi"\n')


def test_graphics_control_decl():
    prog = parse_src("graphics as canvas1 at 0, 0, 300, 300\n")
    (ctrl,) = prog.body
    assert isinstance(ctrl, ast.ControlDecl)
    assert ctrl.kind == "graphics"
    assert ctrl.caption is None
    assert ctrl.name == "canvas1"
    assert ctrl.w == ast.Literal(300, 1)
    assert ctrl.h == ast.Literal(300, 1)


def test_turtle_command_is_a_dotted_method_call():
    prog = parse_src("canvas1.go(100)\n")
    (stmt,) = prog.body
    call = stmt.expr
    assert isinstance(call, ast.Call)
    assert isinstance(call.callee, ast.PropertyAccess)
    assert call.callee.name == "go"
    assert call.callee.obj == ast.Identifier("canvas1", 1)
    assert call.args == [ast.Literal(100, 1)]


def test_bare_turtle_command_without_receiver_is_a_syntax_error():
    # Phase 13: turtle commands are no longer valid as bare, receiver-less statements.
    with pytest.raises(LeopardSyntaxError):
        parse_src("go 100\n")


# ---------------------------------------------------------------------------
# Every GRAMMAR.md example fixture parses without error
# ---------------------------------------------------------------------------

PROGRAMS_DIR = pathlib.Path(__file__).parent / "programs"


@pytest.mark.parametrize("path", sorted(PROGRAMS_DIR.glob("*.lep")), ids=lambda p: p.stem)
def test_grammar_examples_parse_without_error(path: pathlib.Path):
    source = path.read_text(encoding="utf-8")
    prog = parse_src(source)
    assert isinstance(prog, ast.Program)


# ---------------------------------------------------------------------------
# Deliberately broken programs: exact expected message + line number
# (GRAMMAR.md status #8; the checklist's own example is reproduced verbatim below)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "source, expected_message",
    [
        ("if x\n    y = 1\n", "Line 1: expected ':' after 'if' condition"),
        ("if x:\ny = 1\n", "Line 2: expected an indented block after 'if' condition"),
        ("1 = 2\n", "Line 1: left-hand side of '=' is not something that can be assigned to"),
        ("x = (1 + 2\n", "Line 1: expected ')' to close '('"),
        ("function :\n    return 1\n", "Line 1: expected a function name after 'function'"),
        ("for i = 1\n    x = 1\n", "Line 1: expected 'to' after the 'for' loop's starting value"),
        ('"never closed\n', "Line 1: unterminated string literal"),
        ("button as btn at 0, 0, 0\n", "Line 1: expected ',' after the control's width"),
        (
            'menu "&File" as fileMenu:\n    whoops\n',
            "Line 2: expected 'item', 'checkitem', 'submenu', or 'separator' inside a menu",
        ),
        (
            "on whoops:\n    x = 1\n",
            "Line 1: expected 'click', 'change', 'select', 'close', or 'mousemove' after 'on'",
        ),
    ],
)
def test_broken_programs_produce_exact_error(source, expected_message):
    with pytest.raises(LeopardSyntaxError) as exc_info:
        parse_src(source)
    assert str(exc_info.value) == expected_message

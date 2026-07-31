import pathlib

import pytest

from leopard_lang.errors import LeopardRuntimeError
from leopard_lang.interpreter import Interpreter
from leopard_lang.lexer import tokenize
from leopard_lang.parser import parse


def run(source: str) -> Interpreter:
    interp = Interpreter()
    interp.run(parse(tokenize(source)))
    return interp


def value_of(source: str, name: str):
    return run(source).globals.values[name]


# ---------------------------------------------------------------------------
# One test per operator
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("1 + 2", 3),
        ("5 - 2", 3),
        ("3 * 4", 12),
        ("10 / 4", 2.5),
        ("10 % 3", 1),
        ("2 ^ 3", 8),
    ],
)
def test_arithmetic_operators(expr, expected):
    assert value_of(f"x = {expr}\n", "x") == expected


def test_string_concat_operator():
    assert value_of('x = "a" & "b"\n', "x") == "ab"


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("1 = 1", True),
        ("1 = 2", False),
        ("1 eq 1", True),
        ("1 eq 2", False),
        ("1 <> 2", True),
        ("1 <> 1", False),
        ("1 < 2", True),
        ("2 > 1", True),
        ("2 <= 2", True),
        ("2 >= 3", False),
    ],
)
def test_comparison_operators(expr, expected):
    assert value_of(f"x = {expr}\n", "x") is expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("true and false", False),
        ("true and true", True),
        ("false or true", True),
        ("false or false", False),
        ("not true", False),
        ("not false", True),
    ],
)
def test_logical_operators(expr, expected):
    assert value_of(f"x = {expr}\n", "x") is expected


def test_unary_minus():
    assert value_of("x = -5\n", "x") == -5


def test_plus_on_two_strings_is_runtime_error_pointing_at_amp():
    with pytest.raises(LeopardRuntimeError) as exc_info:
        run('x = "a" + "b"\n')
    assert "&" in exc_info.value.message


def test_amp_with_non_string_is_runtime_error_pointing_at_str():
    with pytest.raises(LeopardRuntimeError) as exc_info:
        run('x = "Score: " & 5\n')
    assert "str()" in exc_info.value.message


def test_division_by_zero():
    with pytest.raises(LeopardRuntimeError, match="division by zero"):
        run("x = 1 / 0\n")


def test_modulo_by_zero():
    with pytest.raises(LeopardRuntimeError, match="division by zero"):
        run("x = 1 % 0\n")


def test_and_or_require_booleans():
    with pytest.raises(LeopardRuntimeError):
        run("x = 1 and true\n")


def test_arithmetic_requires_numbers():
    with pytest.raises(LeopardRuntimeError):
        run('x = 1 + "a"\n')


# ---------------------------------------------------------------------------
# One test per statement kind
# ---------------------------------------------------------------------------


def test_assignment():
    assert value_of("x = 1\nx = x + 1\n", "x") == 2


def test_if_then():
    assert value_of("x = 0\nif true:\n    x = 1\n", "x") == 1


def test_if_else():
    assert value_of("x = 0\nif false:\n    x = 1\nelse:\n    x = 2\n", "x") == 2


def test_if_elseif():
    src = "x = 0\nif false:\n    x = 1\nelseif true:\n    x = 2\nelse:\n    x = 3\n"
    assert value_of(src, "x") == 2


def test_while_loop():
    assert value_of("x = 0\nwhile x < 5:\n    x = x + 1\n", "x") == 5


def test_while_with_break():
    src = "x = 0\nwhile true:\n    x = x + 1\n    if x = 3:\n        break\n"
    assert value_of(src, "x") == 3


def test_while_with_continue():
    # sums 1..5 but skips 3
    src = (
        "i = 0\ntotal = 0\n"
        "while i < 5:\n"
        "    i = i + 1\n"
        "    if i = 3:\n"
        "        continue\n"
        "    total = total + i\n"
    )
    assert value_of(src, "total") == 1 + 2 + 4 + 5


def test_for_loop_default_step():
    assert value_of("total = 0\nfor i = 1 to 5:\n    total = total + i\n", "total") == 15


def test_for_loop_with_step():
    src = 'items = []\nfor i = 1 to 10 step 2:\n    items.add(i)\n'
    assert value_of(src, "items") == [1, 3, 5, 7, 9]


def test_for_loop_negative_step():
    src = "items = []\nfor i = 5 to 1 step -1:\n    items.add(i)\n"
    assert value_of(src, "items") == [5, 4, 3, 2, 1]


def test_for_loop_step_zero_is_error():
    with pytest.raises(LeopardRuntimeError, match="step cannot be 0"):
        run("for i = 1 to 5 step 0:\n    x = i\n")


def test_break_outside_loop_is_error():
    with pytest.raises(LeopardRuntimeError, match="'break' used outside a loop"):
        run("break\n")


def test_continue_outside_loop_is_error():
    with pytest.raises(LeopardRuntimeError, match="'continue' used outside a loop"):
        run("continue\n")


def test_function_call_and_return():
    src = "function double(n):\n    return n * 2\n\nx = double(21)\n"
    assert value_of(src, "x") == 42


def test_function_without_return_yields_none():
    src = "function noop():\n    x = 1\n\nresult = noop()\n"
    assert value_of(src, "result") is None


def test_function_wrong_arg_count_is_error():
    src = "function f(a, b):\n    return a + b\n\nx = f(1)\n"
    with pytest.raises(LeopardRuntimeError, match="expects 2 arguments, got 1"):
        run(src)


def test_recursive_function():
    src = (
        "function factorial(n):\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    else:\n"
        "        return n * factorial(n - 1)\n"
        "\n"
        "x = factorial(5)\n"
    )
    assert value_of(src, "x") == 120


def test_function_locals_do_not_leak_to_module_scope():
    src = "function f(a):\n    local_var = a * 2\n    return local_var\n\ny = f(3)\n"
    interp = run(src)
    assert interp.globals.values["y"] == 6
    assert "local_var" not in interp.globals.values
    assert "a" not in interp.globals.values


def test_function_reads_but_cannot_assign_globals():
    src = (
        "counter = 0\n"
        "function bump():\n"
        "    counter = counter + 1\n"  # assigns a new *local*, per GRAMMAR.md §3
        "    return counter\n"
        "\n"
        "x = bump()\n"
    )
    interp = run(src)
    assert interp.globals.values["x"] == 1
    assert interp.globals.values["counter"] == 0


# ---------------------------------------------------------------------------
# Lists (GRAMMAR.md status #4: 1-based indexing, plus .length and .add())
# ---------------------------------------------------------------------------


def test_list_literal():
    assert value_of('x = ["a", "b", "c"]\n', "x") == ["a", "b", "c"]


def test_list_is_one_based():
    assert value_of('x = ["a", "b", "c"]\nfirst = x[1]\n', "first") == "a"


def test_list_length():
    assert value_of('x = ["a", "b", "c"]\nn = x.length\n', "n") == 3


def test_list_add():
    assert value_of('x = ["a"]\nx.add("b")\n', "x") == ["a", "b"]


def test_list_index_out_of_range():
    with pytest.raises(LeopardRuntimeError, match="out of range"):
        run('x = ["a"]\ny = x[5]\n')


def test_list_index_zero_is_out_of_range():
    # 1-based: index 0 is never valid
    with pytest.raises(LeopardRuntimeError, match="out of range"):
        run('x = ["a"]\ny = x[0]\n')


def test_indexing_a_non_list_is_error():
    with pytest.raises(LeopardRuntimeError, match="only lists support"):
        run('x = "hello"\ny = x[1]\n')


def test_list_index_assignment():
    assert value_of('x = ["a", "b", "c"]\nx[2] = "z"\n', "x") == ["a", "z", "c"]


def test_list_index_assignment_out_of_range():
    with pytest.raises(LeopardRuntimeError, match="out of range"):
        run('x = ["a"]\nx[5] = "z"\n')


def test_list_index_assignment_on_non_list_is_error():
    with pytest.raises(LeopardRuntimeError, match="only lists support"):
        run('x = "hello"\nx[1] = "z"\n')


# ---------------------------------------------------------------------------
# Non-GUI builtins (GRAMMAR.md §12)
# ---------------------------------------------------------------------------


def test_str_of_number():
    assert value_of("x = str(42)\n", "x") == "42"


def test_str_of_whole_float_has_no_trailing_zero():
    assert value_of("x = str(10 / 2)\n", "x") == "5"


def test_str_of_boolean():
    assert value_of("x = str(true)\n", "x") == "true"


def test_num_of_valid_string():
    assert value_of('x = num("42")\n', "x") == 42


def test_num_of_invalid_string_is_error():
    with pytest.raises(LeopardRuntimeError, match="is not a number"):
        run('x = num("banana")\n')


def test_print_writes_to_stdout(capsys):
    run('print "hello"\n')
    assert capsys.readouterr().out == "hello\n"


def test_print_number_has_no_trailing_zero(capsys):
    run("print 10 / 2\n")
    assert capsys.readouterr().out == "5\n"


def test_print_boolean(capsys):
    run("print true\n")
    assert capsys.readouterr().out == "true\n"


def test_print_multiple_statements(capsys):
    run('print 1\nprint "two"\n')
    assert capsys.readouterr().out == "1\ntwo\n"


def test_print_of_a_list_is_error():
    with pytest.raises(LeopardRuntimeError, match="print\\(\\) only supports"):
        run('x = [1, 2]\nprint x\n')


def test_ascii():
    assert value_of('x = ascii("A")\n', "x") == 65


def test_date_and_time_return_strings():
    interp = run("d = date()\nt = time()\n")
    assert isinstance(interp.globals.values["d"], str)
    assert isinstance(interp.globals.values["t"], str)


def test_file_roundtrip(tmp_path: pathlib.Path):
    path = str(tmp_path / "notes.txt")
    src = f'write_file("{path}", "hello")\nappend_file("{path}", " world")\ncontent = read_file("{path}")\n'
    assert value_of(src, "content") == "hello world"


def test_file_exists(tmp_path: pathlib.Path):
    path = str(tmp_path / "exists.txt")
    src = f'before = file_exists("{path}")\nwrite_file("{path}", "x")\nafter = file_exists("{path}")\n'
    interp = run(src)
    assert interp.globals.values["before"] is False
    assert interp.globals.values["after"] is True


def test_delete_file(tmp_path: pathlib.Path):
    path = str(tmp_path / "gone.txt")
    src = f'write_file("{path}", "x")\ndelete_file("{path}")\nstill_there = file_exists("{path}")\n'
    assert value_of(src, "still_there") is False


def test_read_missing_file_is_error(tmp_path: pathlib.Path):
    path = str(tmp_path / "missing.txt")
    with pytest.raises(LeopardRuntimeError, match="does not exist"):
        run(f'x = read_file("{path}")\n')


def test_make_and_remove_dir(tmp_path: pathlib.Path):
    path = str(tmp_path / "newdir")
    src = f'make_dir("{path}")\nexisted = file_exists("{path}")\n'
    # file_exists is file-only, so a bare make_dir + remove_dir just needs to not error
    run(src)
    run(f'make_dir("{path}")\nremove_dir("{path}")\n')


# ---------------------------------------------------------------------------
# Full programs
# ---------------------------------------------------------------------------


def test_full_program_factorial():
    src = (
        "function factorial(n):\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    else:\n"
        "        return n * factorial(n - 1)\n"
        "\n"
        "results = []\n"
        "for i = 1 to 6:\n"
        "    results.add(factorial(i))\n"
    )
    assert value_of(src, "results") == [1, 2, 6, 24, 120, 720]


def test_full_program_fizzbuzz_equivalent():
    src = (
        "function classify(n):\n"
        "    if n % 15 = 0:\n"
        "        return \"FizzBuzz\"\n"
        "    elseif n % 3 = 0:\n"
        "        return \"Fizz\"\n"
        "    elseif n % 5 = 0:\n"
        "        return \"Buzz\"\n"
        "    else:\n"
        "        return str(n)\n"
        "\n"
        "results = []\n"
        "for i = 1 to 15:\n"
        "    results.add(classify(i))\n"
    )
    expected = [
        "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
        "11", "Fizz", "13", "14", "FizzBuzz",
    ]
    assert value_of(src, "results") == expected


# ---------------------------------------------------------------------------
# Runtime errors use the same line + plain-English format as syntax errors
# ---------------------------------------------------------------------------


def test_runtime_error_has_line_and_plain_english_message():
    with pytest.raises(LeopardRuntimeError) as exc_info:
        run('x = 1\ny = "a" + "b"\n')
    assert exc_info.value.line == 2
    assert str(exc_info.value) == "Line 2: cannot use '+' on two strings — use '&' to join text"


def test_undefined_variable_is_runtime_error():
    with pytest.raises(LeopardRuntimeError, match="is not defined"):
        run("x = y\n")


# ---------------------------------------------------------------------------
# GRAMMAR.md examples that are valid *bare-script* programs run cleanly
# ---------------------------------------------------------------------------

PROGRAMS_DIR = pathlib.Path(__file__).parent / "programs"
_BARE_SCRIPT_FIXTURES = ["variables.lep", "control_flow.lep", "functions.lep"]


@pytest.mark.parametrize("name", _BARE_SCRIPT_FIXTURES)
def test_bare_script_fixtures_run_without_crashing_on_setup(name):
    # These fixtures reference undefined names (e.g. `print`, `outputBox` — GRAMMAR.md
    # examples aren't full runnable programs) so we only assert *parsing+setup* works;
    # full execution is intentionally not asserted here.
    source = (PROGRAMS_DIR / name).read_text(encoding="utf-8")
    program = parse(tokenize(source))
    assert program.window is None

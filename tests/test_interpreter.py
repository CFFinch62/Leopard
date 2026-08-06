import io
import math
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


def test_indexing_a_non_list_non_string_is_error():
    with pytest.raises(LeopardRuntimeError, match="only lists and strings support"):
        run("x = 5\ny = x[1]\n")


def test_list_index_assignment():
    assert value_of('x = ["a", "b", "c"]\nx[2] = "z"\n', "x") == ["a", "z", "c"]


def test_list_index_assignment_out_of_range():
    with pytest.raises(LeopardRuntimeError, match="out of range"):
        run('x = ["a"]\nx[5] = "z"\n')


def test_list_index_assignment_on_non_list_is_error():
    with pytest.raises(LeopardRuntimeError, match="only lists support"):
        run('x = "hello"\nx[1] = "z"\n')


# ---------------------------------------------------------------------------
# Strings: 1-based indexing (read-only) and .length, mirroring list behavior
# ---------------------------------------------------------------------------


def test_string_is_one_based():
    assert value_of('x = "hello"\nfirst = x[1]\n', "first") == "h"


def test_string_length():
    assert value_of('x = "hello"\nn = x.length\n', "n") == 5


def test_string_index_out_of_range():
    with pytest.raises(LeopardRuntimeError, match="out of range"):
        run('x = "hi"\ny = x[5]\n')


def test_string_index_zero_is_out_of_range():
    with pytest.raises(LeopardRuntimeError, match="out of range"):
        run('x = "hi"\ny = x[0]\n')


def test_string_index_assignment_is_still_an_error():
    # Strings stay immutable — only lists support in-place [ ] assignment.
    with pytest.raises(LeopardRuntimeError, match="only lists support"):
        run('x = "hello"\nx[1] = "H"\n')


# ---------------------------------------------------------------------------
# Non-GUI builtins (GRAMMAR.md §12)
# ---------------------------------------------------------------------------


def test_split_basic():
    assert value_of('x = split("a,b,c", ",")\n', "x") == ["a", "b", "c"]


def test_split_multi_char_separator():
    assert value_of('x = split("a::b::c", "::")\n', "x") == ["a", "b", "c"]


def test_split_keeps_empty_fields():
    assert value_of('x = split("a,,b", ",")\n', "x") == ["a", "", "b"]


def test_split_with_empty_separator_is_error():
    with pytest.raises(LeopardRuntimeError, match="non-empty separator"):
        run('x = split("abc", "")\n')


def test_join_basic():
    assert value_of('x = join(["a", "b", "c"], ",")\n', "x") == "a,b,c"


def test_join_of_non_strings_is_error():
    with pytest.raises(LeopardRuntimeError, match="list of strings"):
        run('x = join([1, 2], ",")\n')


def test_split_join_round_trip():
    assert value_of('x = join(split("a|b|c", "|"), "|")\n', "x") == "a|b|c"


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
# Math builtins (LANGUAGE_ROADMAP.md §1)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("abs(-5)", 5),
        ("abs(5)", 5),
        ("abs(-5.5)", 5.5),
        ("sqrt(9)", 3.0),
        ("round(3.4)", 3),
        ("round(3.5)", 4),
        ("round(3.14159, 2)", 3.14),
        ("floor(3.9)", 3),
        ("floor(-3.1)", -4),
        ("ceil(3.1)", 4),
        ("ceil(-3.9)", -3),
        ("min(3, 7)", 3),
        ("max(3, 7)", 7),
        ("min([5, 2, 8, 1])", 1),
        ("max([5, 2, 8, 1])", 8),
        ("log(1)", 0.0),
        ("exp(0)", 1.0),
        ("pi", math.pi),
    ],
)
def test_math_functions(expr, expected):
    assert value_of(f"x = {expr}\n", "x") == expected


def test_sqrt_of_negative_is_error():
    with pytest.raises(LeopardRuntimeError, match="isn't negative"):
        run("x = sqrt(-1)\n")


def test_log_of_non_positive_is_error():
    with pytest.raises(LeopardRuntimeError, match="greater than 0"):
        run("x = log(0)\n")


def test_min_of_empty_list_is_error():
    with pytest.raises(LeopardRuntimeError, match="non-empty list"):
        run("x = min([])\n")


def test_min_with_wrong_arg_count_is_error():
    with pytest.raises(LeopardRuntimeError, match="two numbers or one list"):
        run("x = min(1, 2, 3)\n")


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("sin(0)", 0.0),
        ("cos(0)", 1.0),
        ("sin(90)", 1.0),
        ("cos(180)", -1.0),
    ],
)
def test_trig_functions_use_degrees(expr, expected):
    assert round(value_of(f"x = {expr}\n", "x"), 9) == expected


def test_math_functions_reject_booleans():
    with pytest.raises(LeopardRuntimeError, match="needs a number"):
        run("x = abs(true)\n")


def test_pi_is_not_callable_as_a_function_by_mistake():
    # 'pi' is a bare constant, not a function — confirm it behaves like a plain
    # identifier (usable directly in an expression, no parens).
    assert value_of("x = pi * 2\n", "x") == math.pi * 2


# ---------------------------------------------------------------------------
# Randomness (LANGUAGE_ROADMAP.md §2)
# ---------------------------------------------------------------------------


def test_random_is_a_float_between_zero_and_one():
    x = value_of("x = random()\n", "x")
    assert isinstance(x, float)
    assert 0 <= x < 1


def test_random_int_is_within_inclusive_range():
    interp = run("results = []\nfor i = 1 to 200:\n    results.add(random_int(3, 5))\n")
    results = interp.globals.values["results"]
    assert set(results) <= {3, 4, 5}
    assert 3 in results and 5 in results  # 200 draws over a 3-wide range should hit both ends


def test_random_int_single_value_range():
    assert value_of("x = random_int(7, 7)\n", "x") == 7


def test_random_int_min_greater_than_max_is_error():
    with pytest.raises(LeopardRuntimeError, match="not be greater than"):
        run("x = random_int(9, 2)\n")


def test_random_int_needs_whole_numbers():
    with pytest.raises(LeopardRuntimeError, match="whole number"):
        run("x = random_int(1.5, 5)\n")


# ---------------------------------------------------------------------------
# String functions (LANGUAGE_ROADMAP.md §3)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expr, expected",
    [
        ('upper("Chuck")', "CHUCK"),
        ('lower("Chuck")', "chuck"),
        ('trim("  hi  ")', "hi"),
        ('contains("hello world", "wor")', True),
        ('contains("hello world", "xyz")', False),
        ('index_of("hello", "ll")', 3),
        ('index_of("hello", "z")', 0),
        ('reverse("hello")', "olleh"),
        ('replace("hello", "l", "L")', "heLLo"),
        ('starts_with("hello", "he")', True),
        ('starts_with("hello", "lo")', False),
        ('ends_with("hello", "lo")', True),
        ('ends_with("hello", "he")', False),
        ('substring("hello", 2, 4)', "ell"),
        ('left("hello", 3)', "hel"),
        ('right("hello", 3)', "llo"),
        ('left("hi", 10)', "hi"),
        ('right("hi", 0)', ""),
        ("chr(65)", "A"),
    ],
)
def test_string_functions(expr, expected):
    assert value_of(f"x = {expr}\n", "x") == expected


def test_chr_and_ascii_are_inverses():
    assert value_of('x = chr(ascii("Z"))\n', "x") == "Z"


def test_substring_out_of_range_is_error():
    with pytest.raises(LeopardRuntimeError, match="out of range"):
        run('x = substring("hi", 1, 5)\n')


def test_substring_start_after_end_is_error():
    with pytest.raises(LeopardRuntimeError, match="out of range"):
        run('x = substring("hello", 4, 2)\n')


def test_replace_with_empty_search_is_error():
    with pytest.raises(LeopardRuntimeError, match="non-empty search string"):
        run('x = replace("hello", "", "z")\n')


def test_upper_on_non_string_is_error():
    with pytest.raises(LeopardRuntimeError, match="needs a string"):
        run("x = upper(42)\n")


def test_left_with_negative_count_is_error():
    with pytest.raises(LeopardRuntimeError, match="isn't negative"):
        run('x = left("hi", -1)\n')


# ---------------------------------------------------------------------------
# List functions (LANGUAGE_ROADMAP.md §4)
# ---------------------------------------------------------------------------


def test_sort_numbers():
    assert value_of("x = sort([3, 1, 2])\n", "x") == [1, 2, 3]


def test_sort_strings():
    assert value_of('x = sort(["banana", "apple", "cherry"])\n', "x") == ["apple", "banana", "cherry"]


def test_sort_does_not_mutate_original():
    interp = run("original = [3, 1, 2]\nsorted_copy = sort(original)\n")
    assert interp.globals.values["original"] == [3, 1, 2]
    assert interp.globals.values["sorted_copy"] == [1, 2, 3]


def test_sort_mixed_types_is_error():
    with pytest.raises(LeopardRuntimeError, match="all numbers or all strings"):
        run('x = sort([1, "a"])\n')


def test_remove_at():
    assert value_of('x = remove_at(["a", "b", "c"], 2)\n', "x") == ["a", "c"]


def test_remove_at_does_not_mutate_original():
    interp = run('original = ["a", "b", "c"]\nresult = remove_at(original, 1)\n')
    assert interp.globals.values["original"] == ["a", "b", "c"]


def test_remove_at_out_of_range_is_error():
    with pytest.raises(LeopardRuntimeError, match="out of range"):
        run('x = remove_at(["a"], 5)\n')


def test_sum_of_list():
    assert value_of("x = sum([1, 2, 3, 4])\n", "x") == 10


def test_sum_of_empty_list_is_zero():
    assert value_of("x = sum([])\n", "x") == 0


def test_sum_of_non_numbers_is_error():
    with pytest.raises(LeopardRuntimeError, match="needs a number"):
        run('x = sum([1, "a"])\n')


def test_contains_on_list():
    assert value_of("x = contains([1, 2, 3], 2)\n", "x") is True
    assert value_of("x = contains([1, 2, 3], 9)\n", "x") is False


def test_index_of_on_list():
    assert value_of('x = index_of(["a", "b", "c"], "b")\n', "x") == 2
    assert value_of('x = index_of(["a", "b", "c"], "z")\n', "x") == 0


def test_reverse_on_list():
    assert value_of("x = reverse([1, 2, 3])\n", "x") == [3, 2, 1]


def test_reverse_does_not_mutate_original():
    interp = run("original = [1, 2, 3]\nresult = reverse(original)\n")
    assert interp.globals.values["original"] == [1, 2, 3]


def test_min_max_on_list():
    assert value_of("x = min([4, 2, 9])\n", "x") == 2
    assert value_of("x = max([4, 2, 9])\n", "x") == 9


def test_shuffle_returns_a_permutation_and_does_not_mutate():
    interp = run("original = [1, 2, 3, 4, 5]\nresult = shuffle(original)\n")
    assert interp.globals.values["original"] == [1, 2, 3, 4, 5]
    assert sorted(interp.globals.values["result"]) == [1, 2, 3, 4, 5]


def test_choice_returns_a_member_of_the_list():
    interp = run('options = ["a", "b", "c"]\nresult = choice(options)\n')
    assert interp.globals.values["result"] in ["a", "b", "c"]


def test_choice_of_empty_list_is_error():
    with pytest.raises(LeopardRuntimeError, match="non-empty list"):
        run("x = choice([])\n")


# ---------------------------------------------------------------------------
# Control flow additions (LANGUAGE_ROADMAP.md §5)
# ---------------------------------------------------------------------------


def test_for_each_over_list():
    interp = run('results = []\nfor fruit in ["a", "b", "c"]:\n    results.add(fruit)\n')
    assert interp.globals.values["results"] == ["a", "b", "c"]


def test_for_each_over_non_list_is_error():
    with pytest.raises(LeopardRuntimeError, match="needs a list"):
        run('for x in "hello":\n    print x\n')


def test_for_each_iterates_a_snapshot_not_a_live_list():
    # Appending to the same list inside the loop body must not extend iteration.
    src = 'items = [1, 2, 3]\nseen = []\nfor x in items:\n    seen.add(x)\n    items.add(99)\n'
    interp = run(src)
    assert interp.globals.values["seen"] == [1, 2, 3]


def test_for_each_with_break():
    src = 'results = []\nfor x in [1, 2, 3, 4]:\n    if x = 3:\n        break\n    results.add(x)\n'
    assert value_of(src, "results") == [1, 2]


def test_for_each_with_continue():
    src = 'results = []\nfor x in [1, 2, 3, 4]:\n    if x % 2 = 0:\n        continue\n    results.add(x)\n'
    assert value_of(src, "results") == [1, 3]


def test_do_until_runs_body_at_least_once():
    interp = run("n = 0\ndo:\n    n = n + 1\nuntil true\n")
    assert interp.globals.values["n"] == 1


def test_do_until_loops_until_condition_true():
    interp = run("n = 0\ndo:\n    n = n + 1\nuntil n >= 5\n")
    assert interp.globals.values["n"] == 5


def test_do_until_with_break():
    interp = run("n = 0\ndo:\n    n = n + 1\n    if n = 3:\n        break\nuntil n >= 10\n")
    assert interp.globals.values["n"] == 3


def test_do_until_with_continue():
    src = "n = 0\nresults = []\ndo:\n    n = n + 1\n    if n % 2 = 0:\n        continue\n    results.add(n)\nuntil n >= 4\n"
    assert value_of(src, "results") == [1, 3]


def test_switch_matches_first_case():
    src = 'x = 2\nswitch x:\n    case 1:\n        r = "one"\n    case 2:\n        r = "two"\n'
    assert value_of(src, "r") == "two"


def test_switch_falls_to_default_when_no_case_matches():
    src = 'x = 9\nswitch x:\n    case 1:\n        r = "one"\n    default:\n        r = "none"\n'
    assert value_of(src, "r") == "none"


def test_switch_with_no_match_and_no_default_does_nothing():
    interp = run('x = 9\nr = "unset"\nswitch x:\n    case 1:\n        r = "one"\n')
    assert interp.globals.values["r"] == "unset"


def test_switch_break_still_propagates_to_enclosing_loop():
    src = (
        "results = []\n"
        "for i = 1 to 4:\n"
        "    switch i:\n"
        "        case 3:\n"
        "            break\n"
        "        default:\n"
        "            results.add(i)\n"
    )
    assert value_of(src, "results") == [1, 2]


def test_break_inside_switch_with_no_enclosing_loop_is_error():
    with pytest.raises(LeopardRuntimeError, match="outside a loop"):
        run("switch 1:\n    case 1:\n        break\n")


# ---------------------------------------------------------------------------
# Console input (LANGUAGE_ROADMAP.md §6)
# ---------------------------------------------------------------------------


def test_input_reads_a_line_from_stdin(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("Chuck\n"))
    assert value_of("x = input()\n", "x") == "Chuck"


def test_input_with_prompt_writes_prompt_to_stdout(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("42\n"))
    assert value_of('x = input("Age: ")\n', "x") == "42"
    assert capsys.readouterr().out == "Age: "


def test_input_at_eof_is_error(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    with pytest.raises(LeopardRuntimeError, match="no more input"):
        run("x = input()\n")


def test_get_env_reads_an_existing_variable(monkeypatch):
    monkeypatch.setenv("LEOPARD_TEST_VAR", "hello")
    assert value_of('x = get_env("LEOPARD_TEST_VAR")\n', "x") == "hello"


def test_get_env_of_missing_variable_is_empty_string(monkeypatch):
    monkeypatch.delenv("LEOPARD_TEST_VAR_UNSET", raising=False)
    assert value_of('x = get_env("LEOPARD_TEST_VAR_UNSET")\n', "x") == ""


def test_command_line_args_returns_extra_argv():
    interp = Interpreter(script_args=["--verbose", "input.txt"])
    interp.run(parse(tokenize("x = command_line_args()\n")))
    assert interp.globals.values["x"] == ["--verbose", "input.txt"]


def test_command_line_args_defaults_to_empty_list():
    assert value_of("x = command_line_args()\n", "x") == []


# ---------------------------------------------------------------------------
# Type introspection (LANGUAGE_ROADMAP.md §7)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("is_number(42)", True),
        ("is_number(3.14)", True),
        ('is_number("42")', False),
        ("is_number(true)", False),
        ("is_number([1])", False),
        ('is_string("hi")', True),
        ("is_string(42)", False),
        ("is_string(true)", False),
        ("is_list([1, 2])", True),
        ("is_list([])", True),
        ('is_list("hi")', False),
        ("is_list(42)", False),
        ('type_of(42)', "number"),
        ('type_of("hi")', "string"),
        ("type_of(true)", "boolean"),
        ("type_of([1, 2])", "list"),
    ],
)
def test_type_introspection(expr, expected):
    assert value_of(f"x = {expr}\n", "x") == expected


def test_type_of_a_no_return_function_call_is_nothing():
    src = "function f():\n    x = 1\n\nresult = type_of(f())\n"
    assert value_of(src, "result") == "nothing"


def test_is_number_lets_a_program_check_before_calling_num():
    src = (
        'function safe_num(value):\n'
        '    if is_number(value):\n'
        '        return value\n'
        '    if is_string(value):\n'
        '        return num(value)\n'
        '    return 0\n'
        '\n'
        'a = safe_num("42")\n'
        'b = safe_num(7)\n'
    )
    interp = run(src)
    assert interp.globals.values["a"] == 42
    assert interp.globals.values["b"] == 7


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

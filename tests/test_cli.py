import os
import pathlib

import pytest

from leopard_lang.cli import main


@pytest.fixture(autouse=True)
def _restore_cwd():
    # `leopard run` changes the process's cwd to the script's own directory
    # (so relative paths in the script resolve correctly) — restore it after
    # each test so this file doesn't leak a changed cwd into later tests.
    original = os.getcwd()
    yield
    os.chdir(original)


def test_run_passes_extra_argv_to_command_line_args(tmp_path: pathlib.Path, capsys):
    script = tmp_path / "argstest.lep"
    script.write_text('for a in command_line_args():\n    print a\n', encoding="utf-8")

    exit_code = main(["run", str(script), "hello", "world"])

    assert exit_code == 0
    assert capsys.readouterr().out == "hello\nworld\n"


def test_run_with_no_extra_argv_is_an_empty_list(tmp_path: pathlib.Path, capsys):
    script = tmp_path / "noargs.lep"
    script.write_text("print command_line_args().length\n", encoding="utf-8")

    exit_code = main(["run", str(script)])

    assert exit_code == 0
    assert capsys.readouterr().out == "0\n"

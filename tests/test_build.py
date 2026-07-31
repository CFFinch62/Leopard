import subprocess

import pytest

pytest.importorskip("PyInstaller")

from leopard_lang.build import compile_file, compile_program  # noqa: E402
from leopard_lang.errors import LeopardSyntaxError  # noqa: E402


# ---------------------------------------------------------------------------
# Fast tests: mock PyInstaller.__main__.run to inspect what compile_program()
# would hand it, without paying for a real multi-second build each time.
# ---------------------------------------------------------------------------


def _capture_launcher(monkeypatch):
    """Patch PyInstaller.__main__.run to record its args and the generated
    launcher's contents (read while the temp dir is still alive), instead of
    actually invoking PyInstaller."""
    calls = []

    def fake_run(args):
        launcher_path = args[-1]
        with open(launcher_path, encoding="utf-8") as f:
            launcher_source = f.read()
        calls.append({"args": args, "launcher_source": launcher_source})

    import PyInstaller.__main__

    monkeypatch.setattr(PyInstaller.__main__, "run", fake_run)
    return calls


def test_bare_script_compiles_without_pyqt6_and_uses_console(tmp_path, monkeypatch):
    calls = _capture_launcher(monkeypatch)
    compile_program("x = 1\n", "myprog", tmp_path)

    (call,) = calls
    assert "--console" in call["args"]
    assert "--windowed" not in call["args"]
    assert "--hidden-import" not in call["args"]  # no GUI hidden-imports for a bare script
    assert "leopard_lang.gui" not in call["launcher_source"]
    assert "SOURCE = 'x = 1\\n'" in call["launcher_source"]


def test_window_program_compiles_windowed_with_gui_hidden_imports(tmp_path, monkeypatch):
    calls = _capture_launcher(monkeypatch)
    compile_program('window "W", 100, 100:\n    x = 1\n', "myprog", tmp_path)

    (call,) = calls
    assert "--windowed" in call["args"]
    assert "--console" not in call["args"]
    assert "PyQt6" in call["args"]
    assert "leopard_lang.gui.app_host" in call["args"]
    assert "from leopard_lang.gui.app_host import run_window" in call["launcher_source"]


def test_compile_program_uses_correct_name_and_output_dir(tmp_path, monkeypatch):
    calls = _capture_launcher(monkeypatch)
    compile_program("x = 1\n", "custom_name", tmp_path)

    (call,) = calls
    args = call["args"]
    assert args[args.index("--name") + 1] == "custom_name"
    assert args[args.index("--distpath") + 1] == str(tmp_path / "dist")


def test_broken_script_fails_before_invoking_pyinstaller(tmp_path, monkeypatch):
    calls = _capture_launcher(monkeypatch)
    with pytest.raises(LeopardSyntaxError):
        compile_program("if x\n    y = 1\n", "myprog", tmp_path)
    assert calls == []  # PyInstaller should never have been invoked


def test_compile_file_reads_source_and_defaults_name_to_stem(tmp_path, monkeypatch):
    calls = _capture_launcher(monkeypatch)
    script = tmp_path / "greeter.lep"
    script.write_text("x = 1\n")
    compile_file(script, tmp_path)

    (call,) = calls
    assert call["args"][call["args"].index("--name") + 1] == "greeter"


# ---------------------------------------------------------------------------
# One real, slow, end-to-end build: proves the mechanism genuinely produces a
# working standalone executable, not just correctly-shaped PyInstaller args.
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_real_bare_script_compiles_and_runs_standalone(tmp_path):
    output_path = tmp_path / "output.txt"
    source = (
        "function factorial(n):\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    else:\n"
        "        return n * factorial(n - 1)\n"
        "\n"
        f'write_file("{output_path}", str(factorial(6)))\n'
    )
    exe_path = compile_program(source, "factorial_test", tmp_path)
    assert exe_path.exists()

    result = subprocess.run([str(exe_path)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    assert output_path.read_text() == "720"

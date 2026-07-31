"""`leopard` console-script entry point: `leopard run <script.lep>`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import LeopardError
from .interpreter import interpret
from .lexer import tokenize
from .parser import parse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="leopard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a .lep script")
    run_parser.add_argument("script", type=Path)

    build_parser = subparsers.add_parser(
        "build", help="Compile a .lep script into a standalone executable"
    )
    build_parser.add_argument("script", type=Path)
    build_parser.add_argument(
        "-o", "--output", type=Path, default=Path("."), help="Output directory (default: .)"
    )
    build_parser.add_argument("-n", "--name", help="Executable name (default: script's filename)")

    args = parser.parse_args(argv)

    if args.command == "run":
        source = args.script.read_text(encoding="utf-8")
        try:
            program = parse(tokenize(source))
            if program.window is not None:
                _run_gui(program)
            else:
                interpret(program)
        except LeopardError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        return 0

    if args.command == "build":
        return _build(args.script, args.output, args.name)

    return 1


def _build(script: Path, output: Path, name: str | None) -> int:
    try:
        from .build import compile_file
    except ImportError:
        print(
            "Compiling needs the 'build' extra: pip install -e '.[build]'",
            file=sys.stderr,
        )
        return 1

    try:
        exe_path = compile_file(script, output, name)
    except LeopardError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Built {exe_path}")
    return 0


def _run_gui(program) -> None:
    # Imported lazily so bare-script installs (no `[gui]` extra) never need PyQt6
    # just to import this module — only running a window program needs it.
    try:
        from .gui.app_host import run_window
    except ImportError:
        print(
            "This program declares a window, which needs the 'gui' extra: "
            "pip install -e '.[gui]'",
            file=sys.stderr,
        )
        raise SystemExit(1)
    run_window(program)


if __name__ == "__main__":
    sys.exit(main())

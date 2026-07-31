<img src="leopard-banner.svg" alt="Leopard" width="100%"/>

# Leopard

Leopard is a small, beginner-friendly programming language for writing desktop
GUI programs: windows, controls, menus, turtle graphics, editable text
windows, and sound. It's a from-scratch, modernized resurrection of
[leopard.bas](original%20-source/leopard.bas), a 2013 Liberty BASIC
application by **Brandon Watts** — this time a real language, with variables,
expressions, control flow, functions, and lists, rather than a
fixed-vocabulary state machine.

```
window "Hello", 300, 100:
    label "Hello, world!" as greeting at 10, 10, 200, 24
```

```bash
pip install -e ".[gui]"
leopard run hello.lep
```

## Installing

Leopard is a standard pip package (`leopard-lang`), split into optional
extras so you only install what you need:

```bash
pip install -e .              # the language core only — no GUI dependency at all
pip install -e ".[gui]"       # + PyQt6, needed for window/menu/turtle/sound programs
pip install -e ".[build]"     # + PyInstaller, needed for `leopard build`
pip install -e ".[dev]"       # + pytest, for running this project's own test suite
```

A bare (no-window) script never needs PyQt6 installed at all — the language
core has zero GUI dependency.

## Using the CLI

```bash
leopard run script.lep              # run a program
leopard build script.lep            # compile it into a standalone executable
leopard build script.lep -o dist -n myapp
```

`leopard build` bundles your script's source, the Leopard runtime, and a
small generated launcher into one `--onefile` PyInstaller executable — no
Python installation required on the machine that runs it.

## Learning Leopard

- **[LANGUAGE_GUIDE.md](LANGUAGE_GUIDE.md)** — start here. A tutorial that
  walks through every part of the language with runnable examples.
- **[GRAMMAR.md](GRAMMAR.md)** — the complete, precise language spec: every
  keyword, operator, and builtin, with exact rules. The source of truth the
  guide is derived from.
- `IDE_Suite 2/LEOPARD/examples/` — a sixteen-program curriculum, from
  bare-script fundamentals through every window kind to two capstone
  projects, ready to open and run in the Leopard IDE. See that folder's own
  `README.md` for the full, ordered list.

## The Leopard IDE

Leopard is fully usable from the command line with any text editor, but a
dedicated IDE also exists at `IDE_Suite 2/LEOPARD/` (a sibling project, not
part of this package) — syntax highlighting, a run/build toolbar, and a
file browser built on the same `leopard-lang` package described here.

## Project layout

```
LANGUAGES/Leopard/
  original -source/leopard.bas   <- original 2013 source, read-only reference
  GRAMMAR.md                <- canonical language spec
  LANGUAGE_GUIDE.md          <- beginner tutorial
  IMPLEMENTATION_PLAN.md     <- project tracker / build history
  pyproject.toml
  src/leopard_lang/
    tokens.py, lexer.py, ast_nodes.py, parser.py    <- lexer/parser
    errors.py, environment.py, interpreter.py        <- runtime core
    builtins_core.py, builtins_files.py              <- non-GUI builtins
    cli.py                                           <- `leopard` command
    build.py                                         <- `leopard build` / PyInstaller packaging
    gui/                                              <- windows, menus, turtle, text window, sound
  tests/
```

## Development

```bash
pip install -e ".[dev,gui,build]"
pytest
```

287 tests, headless (`QT_QPA_PLATFORM=offscreen` set automatically in
`tests/conftest.py`), a few seconds to run. See `IMPLEMENTATION_PLAN.md` for
the full build history and design decisions behind the language.

## Acknowledgments

Leopard's vocabulary and spirit — window/text-window/graphics-window programs,
named GUI controls, turtle graphics — come from **Brandon Watts**'s original
2013 Liberty BASIC application, `leopard.bas`
(`original -source/leopard.bas`, and originally distributed via
leopardprogramming.com). This project is a ground-up reimplementation as a
real programming language, but the idea and design it draws inspiration from
are his.

## License

MIT — see [LICENSE](LICENSE).

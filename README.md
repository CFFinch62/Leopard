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

- **[user-docs/LANGUAGE_GUIDE.md](user-docs/LANGUAGE_GUIDE.md)** — start here. A tutorial that
  walks through every part of the language with runnable examples.
- **[user-docs/LANGUAGE_SPEC.md](user-docs/LANGUAGE_SPEC.md)** — the complete, flat reference:
  every operator, statement form, and builtin function in one catalog, kept
  verified against source.
- **[dev-docs/GRAMMAR.md](dev-docs/GRAMMAR.md)** — the incremental design/decision log (why
  things are the way they are), rather than a flat reference.
- **[Example curriculum](https://github.com/CFFinch62/LEOPARD-IDE/tree/main/examples)**
  — sixteen sample programs in the companion [Leopard IDE](https://github.com/CFFinch62/LEOPARD-IDE)
  repository, from bare-script fundamentals through every window kind to two
  capstone projects. See that folder's own README for the full, ordered list.

## The Leopard IDE

Leopard is fully usable from the command line with any text editor, but a
dedicated IDE also exists, in its own separate repository:
**[github.com/CFFinch62/LEOPARD-IDE](https://github.com/CFFinch62/LEOPARD-IDE)**
— syntax highlighting, a run/build toolbar, a file browser, and the example
curriculum above, all built on this package (`leopard-lang`). Install this
package first (see Installing, above), then follow that repo's own README.

## Project layout

```
LANGUAGES/Leopard/
  original -source/leopard.bas   <- original 2013 source, read-only reference
  user-docs/
    LANGUAGE_SPEC.md           <- complete, flat language reference
    LANGUAGE_GUIDE.md          <- beginner tutorial
  dev-docs/
    GRAMMAR.md                 <- design/decision log
    IMPLEMENTATION_PLAN.md     <- project tracker / build history
    FEATURE_PARITY_REVIEW.md   <- gap review vs. the original leopard.bas
    LANGUAGE_ROADMAP.md        <- stdlib/control-flow gap review vs. mainstream languages
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

447 tests, headless (`QT_QPA_PLATFORM=offscreen` set automatically in
`tests/conftest.py`), a few seconds to run. See `dev-docs/IMPLEMENTATION_PLAN.md` for
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

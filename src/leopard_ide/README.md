# Leopard IDE

![Leopard banner](../../leopard-banner.svg)

A lightweight PyQt6 IDE for Leopard, built on the Base IDE skeleton. This
package (`leopard_ide`) lives inside the main [Leopard](../../README.md)
repository, alongside the language it hosts (`leopard_lang`, in
[`../leopard_lang/`](../leopard_lang/)) — one repo, one `pyproject.toml`, one
`.deb` package for both.

## Install and run

From the repository root:

```bash
pip install -e ".[gui]"
leopard-ide
```

That's the same `leopard-lang` install as the language CLI itself (see the
main [README](../../README.md)) — the `gui` extra (PyQt6) is all this IDE
needs beyond the language core. `leopard-lang[build]` additionally pulls in
PyInstaller, needed for the **Build** toolbar button (compiling a Leopard
program to a standalone executable) and for `build_ide.py` (below).

## Features
- Top menu bar (File, Edit, View, Theme, Help)
- Toolbar, including Run and **Build** (compile the current program to a
  standalone executable)
- Left file browser with navigation controls and bookmarks
- Tabbed editor area with line numbers, current-line highlight, and full
  Leopard syntax highlighting (keywords, builtins, strings, numbers,
  comments, operators, `.property` access)
- Find/Replace dialog (Ctrl+F)
- Console/terminal panel, with an input line wired to the active language provider
- An in-app documentation panel (View → Toggle Documentation, or Help menu)
  rendering the Language Guide, Language Spec, and this project's own IDE
  Guide from `../../user-docs/` without leaving the IDE
- Status bar with cursor position
- Generic open/save workflow with error dialogs on failure, including a
  `.lep`-aware file filter
- Window size, splitter layout, and theme persisted across restarts

See [`../../user-docs/IDE_GUIDE.md`](../../user-docs/IDE_GUIDE.md) for a full
tour of all of the above — it's also available from inside the IDE itself,
via **Help → IDE Guide**.

## Build a standalone binary

**The IDE itself:**
```bash
source .venv/bin/activate
python build_ide.py
```
(from the repository root — `build_ide.py` lives there, not in this
directory). Produces a self-contained app in `dist/LeopardIDE/` via
PyInstaller, bundling `leopard-icon.svg` and `user-docs/` alongside this
package and `leopard_lang`. This is a separate, optional distribution path
from the Debian package (`packaging/stage.sh` + `dpkg-deb`, see
[`../../packaging/README.md`](../../packaging/README.md)) — most users on
Linux Mint should just use the `.deb`; this is for a standalone executable
on another OS, or outside apt.

**A Leopard program you've written:** click the **Build** toolbar button (or
run `leopard build script.lep` from the command line, outside the IDE) to
compile the current program into its own standalone, double-clickable
executable — no Python installation required on the machine that runs it.
This is the feature the original 2013 app's "Compile" button always claimed
to do but never did.

## Leopard support
`app/leopard_language.py`'s `LeopardLanguageProvider`:
- `file_extensions` — `.lep`.
- `run(source, terminal)` — tokenizes and parses `source` via `leopard_lang`;
  a bare (no-window) script runs through the interpreter directly. A program
  with a `window`/`text window`/`graphics window` header runs via
  `leopard_lang.gui.app_host.run_window(program, existing_app=...)`, passing
  this IDE's own already-running `QApplication` — the same function
  `leopard run` itself calls standalone, just reusing the IDE's event loop
  instead of spawning a second one. Syntax/runtime errors are written to the
  terminal pane with their line number, the same format `leopard run` prints.
- `compile(source, name, output_dir, terminal)` — the Build button's entry
  point; calls `leopard_lang.build.compile_program` and reports progress and
  any errors to the terminal pane.
- `create_highlighter` — full Leopard syntax highlighting (`LeopardHighlighter`
  in the same file): reserved words, builtins/turtle commands, strings,
  numbers, comments, operators, and `.property` access, each its own color.

## Examples
[`../../examples/`](../../examples/) has sixteen complete, runnable programs
arranged as a full curriculum — from bare-script fundamentals (variables,
control flow, functions, lists, file I/O — no window at all) through every
window kind (controls, dialogs, menus, turtle graphics, text windows, sound)
to two capstone programs that combine it all. See
[`../../examples/README.md`](../../examples/README.md) for the complete,
ordered list and what each lesson covers.

Open any of them in the IDE and click Run.
[`LANGUAGE_GUIDE.md`](../../user-docs/LANGUAGE_GUIDE.md) walks through the
language feature-by-feature with the same examples;
[`LANGUAGE_SPEC.md`](../../user-docs/LANGUAGE_SPEC.md) has the complete,
precise reference.

## Acknowledgments
The Leopard language this IDE hosts is a modernized, ground-up
reimplementation of **Brandon Watts**'s original 2013 Liberty BASIC
application, `leopard.bas` (see
[`../../original -source/`](../../original%20-source/) — originally
distributed via leopardprogramming.com) — the vocabulary and spirit of the
language (windows, named controls, turtle graphics) trace back to his
design.

## License
MIT — see [LICENSE](../../LICENSE).

# Leopard IDE

![Leopard banner](leopard-banner.svg)

A lightweight PyQt6 IDE for Leopard, built on the Base IDE skeleton.

## Requirements
The Leopard language itself — lexer, parser, interpreter, and GUI runtime — lives
in this repo's sibling language directory, as the standalone `leopard-lang` pip
package:

```
LANGUAGES/Leopard/
```

This IDE doesn't embed a copy of it; `requirements.txt` installs it as an
editable, path-based dependency (`leopard-lang[gui]`), so the IDE always runs
whatever's currently in `LANGUAGES/Leopard/src/leopard_lang/`. `leopard-lang`
is a real, independent CLI tool in its own right (`leopard run script.lep`) —
this IDE is one consumer of it, not the only way to run a `.lep` file.

## Features
- Top menu bar (File, Edit, View, Theme)
- Toolbar, including Run and **Build** (compile the current program to a
  standalone executable)
- Left file browser with navigation controls and bookmarks
- Tabbed editor area with line numbers, current-line highlight, and full
  Leopard syntax highlighting (keywords, builtins, strings, numbers,
  comments, operators, `.property` access)
- Find/Replace dialog (Ctrl+F)
- Console/terminal panel, with an input line wired to the active language provider
- Status bar with cursor position
- Generic open/save workflow with error dialogs on failure, including a
  `.lep`-aware file filter
- Window size, splitter layout, and theme persisted across restarts

## Run
```bash
cd "/home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/IDES/IDE_Suite 2/LEOPARD"
./run.sh
```
`run.sh` creates `venv/` and installs requirements automatically (via
`setup.sh`) on first run, then launches the app. Run `./setup.sh` directly
if you just want to (re)provision the environment without launching.

## Build a standalone binary

**The IDE itself:**
```bash
source venv/bin/activate
python build.py
```
Produces a self-contained app in `dist/LeopardIDE/` via PyInstaller.

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
`examples/` has sixteen complete, runnable programs arranged as a full
curriculum — from bare-script fundamentals (variables, control flow,
functions, lists, file I/O — no window at all) through every window kind
(controls, dialogs, menus, turtle graphics, text windows, sound) to two
capstone programs that combine it all. See
**[`examples/README.md`](examples/README.md)** for the complete, ordered
list and what each lesson covers.

Open any of them in the IDE and click Run. `LANGUAGES/Leopard/LANGUAGE_GUIDE.md`
walks through the language feature-by-feature with the same examples;
`LANGUAGES/Leopard/GRAMMAR.md` has the complete, precise spec.

## Other extension points
- Expand the file browser with project management features such as new folders, rename, and delete.
- Add a preferences dialog for editor font size, tab width, etc.

## Acknowledgments
The Leopard language this IDE hosts is a modernized, ground-up
reimplementation of **Brandon Watts**'s original 2013 Liberty BASIC
application, `leopard.bas` (see `LANGUAGES/Leopard/original -source/`,
originally distributed via leopardprogramming.com) — the vocabulary and
spirit of the language (windows, named controls, turtle graphics) trace back
to his design.

## License
MIT — see [LICENSE](LICENSE).
